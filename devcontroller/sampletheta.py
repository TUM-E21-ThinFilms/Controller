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

    def __init__(self, interruptor=None, encoder=None, timer=None, logger=None):

        if logger is None:
            logger = LoggerFactory().get_sample_theta_logger()

        if interruptor is None:
            interruptor = Interruptor()

        Loggable.__init__(self, logger)
        Interruptable.__init__(self, interruptor)

        self._motor = ThetaMotorController()

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
        while True:
            current_angle = self.get_angle()
            angle_difference = angle - current_angle

            steps_to_move = self._proposal_steps(angle_difference)

            if abs(steps_to_move) < 5:
                self._logger.info("---> Angle difference %s very low, moving just %s steps. Aborting.",
                                  angle_difference, steps_to_move)
                break
            self._interrupt.stoppable()

            try:
                self._motor.move(steps_to_move)

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

                    cur_angle = self.get_angle()
                    self._moving = cur_angle
                    self._logger.info("--> Current angle %s", cur_angle)

                    if not (self.ANGLE_MIN <= cur_angle <= self.ANGLE_MAX):
                        self._logger.error("---> Motor not in allowed range. STOP")
                        raise RuntimeError("Angle not in allowed position anymore. STOP.")

                    self._timer.sleep(self.WAITING_TIME)
            except BaseException as e:
                self._motor.stop()
                raise e

            current_angle = self.get_angle()
            angle_difference = angle - current_angle

            if abs(angle_difference) < self.ANGLE_TOL:
                self._logger.info("---> Reached target angle %s with current angle %s, difference %s", angle,
                                  current_angle, angle_difference)

        # if finished, move the motor in the opposite direction for approx 50-100 steps.
        # if not, then the motor still "pushes" into the direction, which leads to a continuous increment
        # in the angle...
        direction = -1 * self.signum(steps_to_move)
        self._motor.move(direction * 100)
        self._last_steps = direction * 100

    """
    def _move_angle(self, angle):
        continue_movement = True
        while continue_movement:
            self._interrupt.stoppable()
            cur_angle = self._encoder.get_angle()
            self._moving = cur_angle
            diff = angle - cur_angle

            if 0.03 < abs(diff) < 0.1:
                self._logger.info("---> Angle difference %s very low. Read angle again just to be sure ...", abs(diff))
                self._timer.sleep(1)
                cur_angle = self._encoder.get_angle()
                diff = angle - cur_angle
                steps = self._proposal_steps(diff) / 2
            else:
                steps = self._proposal_steps(diff)

            self._logger.info("Moving to angle %s", angle)
            self._logger.info("--> Proposal steps: %s" % steps)
            if steps == 0:
                return

            try:
                self._motor.move(steps)
                i = 0
                while True:
                    self._interrupt.stoppable()
                    i += self.WAITING_TIME
                    if i >= self.TOTAL_WAITING_TIME:
                        self._logger.info("---> Motor movement exceeded waiting time")
                        self._motor.stop()

                    if not self._motor.is_moving():
                        break

                    cur_angle = self._encoder.get_angle()
                    self._moving = cur_angle
                    self._logger.info("--> Current angle %s", cur_angle)

                    if not (self.ANGLE_MIN <= cur_angle <= self.ANGLE_MAX):
                        self._logger.error("---> Motor not in allowed range. STOP")
                        raise RuntimeError("Angle not in allowed position anymore. STOP.")

                    self._timer.sleep(self.WAITING_TIME)

                new_angle = self._encoder.get_angle()
                self._moving = new_angle
                self._logger.info("---> Current angle %s", new_angle)

                new_diff = abs(angle - new_angle)
            except BaseException as e:
                self._motor.stop()
                raise e

            if new_diff > self.ANGLE_TOL:
                self._logger.info("Goal: %s, current: %s, difference: %s", angle, new_angle, new_diff)
                # self._move_angle(angle)
            else:
                continue_movement = False
    """

    def _proposal_steps(self, angle_diff):

        new_proposal = -1 * int(angle_diff * 2000)  # 2000 for 1/128 microsteps, 100 for 1/64

        hysteresis_correction = 0
        if not self._last_steps == 0:
            sig_new = self.signum(new_proposal)
            sig_old = self.signum(self._last_steps)
            if not sig_new == sig_old:
                hysteresis_correction = sig_new * self.HYSTERESIS_OFFSET

        self._logger.info("Last steps: %s, new proposal: %s + hysteresis offset: %s", self._last_steps, new_proposal,
                          hysteresis_correction)
        self._last_steps = new_proposal + hysteresis_correction
        return self._last_steps

    def signum(self, value):
        if value > 0:
            return +1
        if value < 0:
            return -1
        return 0
