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
from devcontroller.encoder.theta import ThetaEncoder
from phymotion import ThetaMotorController


class SampleThetaController(Loggable, Interruptable):
    MAX_ANGLE_MOVE = 10
    ANGLE_MIN = -10.0
    ANGLE_MAX = 10.0
    ANGLE_TOL = 0.004
    TOTAL_WAITING_TIME = 60
    WAITING_TIME = 0.1
    HYSTERESIS_OFFSET = 400

    def __init__(self, interruptor=None, timer=None, logger=None):

        if logger is None:
            logger = LoggerFactory().get_sample_theta_logger()

        if interruptor is None:
            interruptor = Interruptor()

        Loggable.__init__(self, logger)
        Interruptable.__init__(self, interruptor)

        self._motor = ThetaMotorController()
        self._encoder = ThetaEncoder()
        self._moving = False
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
        if not self._moving is False:
            return self._moving

        with self._encoder:
            return self._encoder.get_angle()

    @retry()
    def set_angle(self, angle):
        if not (self.ANGLE_MIN <= angle <= self.ANGLE_MAX):
            raise RuntimeError("New angle is not in the allowed angle range [%s, %s]", self.ANGLE_MIN, self.ANGLE_MAX)
        try:
            self._moving = 0
            with self._encoder:
                self._move_angle(angle)
        finally:
            self._moving = False

    @retry()
    def move_cw(self, angle):
        self.set_angle(abs(angle))

    @retry()
    def move_acw(self, angle):
        self.set_angle(-1.0 * abs(angle))

    def search_reference(self):
        try:
            self._encoder.connect()
            self._motor.get_driver().deactivate_endphase()

            self._encoder.start_reference()
            raw_encoder = self._encoder.get_encoder()
            raw_encoder.clearBuffer()
            while not raw_encoder.receivedReference():
                self._interrupt.stoppable()
                raw_encoder.read()
                self._logger.info("At position %s. Reference 1: %s, Reference 2: %s", raw_encoder.getPosition(), raw_encoder.getReference1(),
                                  raw_encoder.getReference2())

            self._encoder.stop_reference()

        finally:
            self._encoder.disconnect()
            self._motor.get_driver().activate_endphase()

    def _move_angle(self, angle):
        continue_movement = True
        while continue_movement:
            self._interrupt.stoppable()
            cur_angle = self._encoder.get_angle()
            self._moving = cur_angle
            diff = angle - cur_angle

            if 0.03 < abs(diff) < 0.1:
                self._logger.info("---> Angle difference %s very low. Read angle again just be sure ...")
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

    def _proposal_steps(self, angle_diff):

        new_proposal = -1 * int(angle_diff * 1100)

        hysteresis_correction = 0
        if not self._last_steps == 0:
            sig_new = self.signum(new_proposal)
            sig_old = self.signum(self._last_steps)
            if not sig_new == sig_old:
                hysteresis_correction = sig_new * self.HYSTERESIS_OFFSET

        self._logger.info("Last steps: %s, new proposal: %s + hysteresis offset: %s", self._last_steps, new_proposal, hysteresis_correction)
        self._last_steps = new_proposal + hysteresis_correction
        return new_proposal

    def signum(self, value):
        if value > 0:
            return +1
        if value < 0:
            return -1
        return 0
