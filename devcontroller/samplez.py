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
from encoder.factory import Factory
from devcontroller.misc.logger import LoggerFactory
from baur_pdcx85.factory import BaurFactory


class SampleZController(Loggable, Interruptable):
    Z_MIN = -15.0
    Z_MAX = 15.0
    Z_TOL = 4e-4
    TOTAL_WAITING_TIME = 100
    WAITING_TIME = 0.25
    STEP_TOL = 1

    def __init__(self, interruptor=None, encoder=None, timer=None, logger=None):

        if logger is None:
            logger = LoggerFactory().get_sample_theta_logger()

        if interruptor is None:
            interruptor = Interruptor()

        Loggable.__init__(self, logger)
        Interruptable.__init__(self, interruptor)

        self._motor = BaurFactory().create_z()
        self._motor.initialize(4000, 20, 500, 300)

        if encoder is None:
            encoder = Factory().get_interface()

        self._encoder = encoder

        if timer is None:
            timer = InterruptableTimer(self._interrupt)

        self._timer = timer

    def get_encoder(self):
        return self._encoder

    def get_motor(self):
        return self._motor

    @retry()
    def stop(self):
        self._motor.stop()

    @retry()
    def get_position(self):
        return self._encoder.get_z()

    @retry()
    def set_position(self, pos):
        if not (self.Z_MIN <= pos <= self.Z_MAX):
            raise RuntimeError("New position is not in the allowed angle range [%s, %s]", self.Z_MIN, self.Z_MAX)

        self._move_position(pos)

    def move_up(self, position):
        self.set_position(self.get_position() + abs(position))

    def move_down(self, position):
        self.set_position(self.get_position() - abs(position))

    def _move_position(self, position):
        current_position = self._encoder.get_z()
        diff = position - current_position
        steps = self._proposal_steps(diff)
        self._logger.info("Goal: %s mm, current: %s mm, estimated steps: %s", position, current_position, steps)

        if abs(steps) < self.STEP_TOL:
            self._logger.info("Estimated steps %s smaller than STEP_TOLERANCE %s", steps, self.STEP_TOL)
            return

        try:
            self._interrupt.stoppable()
            self._move_motor(steps)
            self._motor.stop()
            new_position = self._encoder.get_z()

            self._logger.info("Current position: %s", new_position)

            new_diff = abs(position - new_position)
        except BaseException as e:
            self._motor.stop()
            raise e

        if new_diff > self.Z_TOL:
            self._logger.info("Goal: %s mm, current: %s mm, difference: %s", position, new_position, new_diff)
            self._move_position(position)

    def _move_motor(self, diff_steps):
        cur_steps = self._motor.get_position()
        desired_position = cur_steps + diff_steps

        self._logger.info("Moving motor to position %s ...", desired_position)
        self._motor.move_abs(desired_position)
        i = 0
        while True:
            self._interrupt.stoppable()
            i += self.WAITING_TIME
            if self._motor.get_position() == desired_position or i >= self.TOTAL_WAITING_TIME:
                break

            current_position = self._encoder.get_z()
            if not (self.Z_MIN <= current_position <= self.Z_MAX):
                self._logger.error("Position not in allowed range. STOP")
                raise RuntimeError("z-position not in allowed range anymore. STOP.")

            self._logger.info("---> Current position %s", current_position)

            self._timer.sleep(self.WAITING_TIME)

    def _proposal_steps(self, distance_diff_mm):
        return int(distance_diff_mm * 5000)
