# Copyright (C) 2017, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from e21_util.interruptor import Interruptor, InterruptableTimer
from e21_util.retry import retry
from e21_util.interface import Loggable, Interruptable
from devcontroller.misc.logger import LoggerFactory
from devcontroller.phymotion import ThetaMotorController
from encoder.factory import Factory


class SampleThetaController(Loggable, Interruptable):
    MAX_ANGLE_MOVE = 10
    ANGLE_MIN = -10.0
    ANGLE_MAX = 10.0
    ANGLE_TOL = 0.001
    TOTAL_WAITING_TIME = 5
    WAITING_TIME = 0.1
    HYSTERESIS_OFFSET = 800
    STEP_TOL = 1
    MAX_ITERATIONS = 25

    def __init__(self, interruptor=None, encoder=None, timer=None, logger=None):

        if logger is None:
            logger = LoggerFactory().get_sample_theta_logger()

        if interruptor is None:
            interruptor = Interruptor()

        Loggable.__init__(self, logger)
        Interruptable.__init__(self, interruptor)

        self._motor = ThetaMotorController(logger=logger)

        if encoder is None:
            encoder = Factory().get_interface()

        self._encoder = encoder
        self._last_steps = 0

        if timer is None:
            timer = InterruptableTimer(self._interrupt)

        self._timer = timer

    def get_motor(self):
        return self._motor

    def get_encoder(self):
        return self._encoder

    @retry()
    def stop(self):
        self._motor.stop()

    @retry()
    def get_angle(self):
        return self._encoder.get_angle()

    @retry()
    def set_angle(self, angle):
        if not (self.ANGLE_MIN <= angle <= self.ANGLE_MAX):
            raise RuntimeError("New angle is not in the allowed angle range [%s, %s]", self.ANGLE_MIN, self.ANGLE_MAX)

        self._set_angle(angle)

    @retry()
    def move_cw(self, angle):
        self.set_angle(abs(angle))

    @retry()
    def move_ccw(self, angle):
        self.set_angle(-1.0 * abs(angle))

    def move_acw(self, angle):
        self.move_ccw(angle)

    def _set_angle(self, angle):
        self._interrupt.stoppable()
        steps_to_move = 0
        iterations = 0
        while True:
            iterations += 1

            if iterations > self.MAX_ITERATIONS:
                self._logger.info("Run out of iterations. Re-engaging completely new ...")
                self._move_motor(self.signum(self._last_steps) * self.HYSTERESIS_OFFSET * -1)
                iterations = 0


            current_angle, angle_difference = self._angle_difference(angle)
            steps_to_move = self._proposal_steps(angle_difference)
            self._logger.info("Target: %s, current: %s, difference: %s, steps: %s", angle, current_angle,
                              angle_difference, steps_to_move)
            if abs(steps_to_move) < self.STEP_TOL or abs(angle_difference) < self.ANGLE_TOL:
                self._logger.info("---> Difference %s very low, moving just %s steps. Aborting.",
                                  angle_difference, steps_to_move)
                break

            self._interrupt.stoppable()

            self._move_motor(steps_to_move, angle)

            current_angle, angle_difference = self._angle_difference(angle)

            if abs(angle_difference) < self.ANGLE_TOL:
                self._logger.info("---> Reached target %s with current %s, difference %s", angle,
                                  current_angle, angle_difference)

        # if finished, move the motor in the opposite direction for approx 50-100 steps.
        # if not, then the motor still "pushes" into the direction, which leads to a continuous increment
        # in the angle...
        #direction = -1 * self.signum(steps_to_move)
        #steps = direction * 40
        #self._logger.info("---> Moving %s steps in the opposite direction", str(steps))
        # self._move_motor(steps)

    def _angle_difference(self, target_angle):
        current_angle = self.get_angle()
        if target_angle is None:
            target_angle = current_angle

        angle_difference = target_angle - current_angle
        return current_angle, angle_difference

    def _move_motor(self, relative_steps, target_angle=None):
        try:

            if abs(relative_steps) > 500:
                self._motor.set_speed(0.8)
            elif abs(relative_steps) > 50:
                self._motor.set_speed(0.4)
            else:
                self._motor.set_speed(0.05)

            self._motor.move(relative_steps)
            self._last_steps = relative_steps

            i = 0.0
            while True:
                self._interrupt.stoppable()
                i += self.WAITING_TIME
                if i >= self.TOTAL_WAITING_TIME:
                    self._logger.info("---> Motor movement exceeded waiting time")
                    self._motor.stop()
                    break

                if not self._motor.is_moving():
                    break

                # Note: angle_diff is 0 if target_angle is None!
                cur_angle, angle_diff = self._angle_difference(target_angle)

                if not target_angle is None:
                    self._logger.info("--> Current angle %s", cur_angle)
                    if abs(angle_diff) < self.ANGLE_TOL:
                        self._logger.info("---> Reached target angle, difference: %s", angle_diff)
                        self._motor.stop()
                        break

                if not (self.ANGLE_MIN <= cur_angle <= self.ANGLE_MAX):
                    self._logger.error("---> Motor not in allowed range. STOP")
                    raise RuntimeError("Angle not in allowed position anymore. STOP.")

                self._timer.sleep(self.WAITING_TIME)
        except BaseException as e:
            self._motor.stop()
            raise e

    def _proposal_steps(self, angle_diff):

        if angle_diff > 0.2:
            new_proposal = -1 * int(angle_diff * 2000)  # 2000 for 1/128 microsteps, 100 for 1/64
        else:
            new_proposal = -1 * int(angle_diff * 1500)

        hysteresis_correction = 0
        if not self._last_steps == 0:
            sig_new = self.signum(new_proposal)
            sig_old = self.signum(self._last_steps)
            if not sig_new == sig_old:
                hysteresis_correction = sig_new * self.HYSTERESIS_OFFSET

        self._logger.info("Last steps: %s, new proposal: %s + hysteresis offset: %s", self._last_steps, new_proposal,
                          hysteresis_correction)
        return new_proposal + hysteresis_correction

    def signum(self, value):
        if value > 0:
            return +1
        if value < 0:
            return -1
        return 0
