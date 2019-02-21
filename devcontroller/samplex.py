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

from e21_util.interruptor import InterruptableTimer, Interruptor, StopException
from e21_util.retry import retry
from e21_util.interface import Loggable, Interruptable
from devcontroller.misc.logger import LoggerFactory
from baur_pdcx85.driver import BaurDriver


class SampleXController(Loggable, Interruptable):
    def __init__(self, driver, logger, timer=None, interruptor=None):
        if interruptor is None:
            interruptor = Interruptor()

        Loggable.__init__(self, logger)
        Interruptable.__init__(self, interruptor)

        assert isinstance(driver, BaurDriver)

        if timer is None:
            timer = InterruptableTimer(self._interrupt)

        self._timer = timer

        self._motor = driver
        self._motor.initialize(4000, 20, 400, 300)

    def get_motor(self):
        return self._motor

    @retry()
    def stop(self):
        self._motor.stop()

    @retry()
    def get_position(self):
        return self._motor.get_position()

    @retry()
    def set_position(self, pos):
        self._motor.move_abs(pos)
        self._timer.sleep(0.5)
        cur_pos = self._motor.get_position()
        try:
            while True:
                self._interrupt.stoppable()
                try:
                    cur_pos = self.get_position()
                except BaseException as e:
                    self._logger.warning("Could not read current position")
                    self._logger.exception(e)

                if pos == cur_pos:
                    break
                self._timer.sleep(1)
        except StopException as e:
            self._motor.stop()
            raise e

    def _move(self, steps):
        current_steps = self._motor.get_position()
        final_steps = current_steps + steps
        try:
            while True:
                self._interrupt.stoppable()
                if current_steps == final_steps:
                    return True
                self._timer.sleep(1)
                current_steps = self._motor.get_position()
        except StopException as e:
            self._motor.stop()
            raise e

    def move(self, diff):
        if diff > 0:
            self.move_right(diff)
        else:
            self.move_left(diff)

    @retry()
    def move_left(self, diff_in_mm):
        diff = abs(diff_in_mm)
        if abs(diff_in_mm) > 5:
            raise RuntimeError("Will not move more than 5 mm in total")
        steps = self._mm_to_steps(diff)
        self._logger.info("Moving %s mm to the left. This corresponds to %s steps", diff, steps)
        self._move(steps)

    @retry()
    def move_right(self, diff_in_mm):
        diff = abs(diff_in_mm)
        if abs(diff_in_mm) > 5:
            raise RuntimeError("Will not move more than 5 mm in total")
        steps = self._mm_to_steps(-1 * diff)
        self._logger.info("Moving %s mm to the right. This corresponds to %s steps", diff, steps)
        self._move(steps)

    @retry()
    def move_left_steps(self, steps):
        abs_stps = abs(steps)
        if abs_stps > 30000:
            raise RuntimeError("Will not move more than 30.000 steps in total")
        self._logger.info("Moving %s steps to the left. This corresponds to %s mm", steps, self._steps_to_mm(steps))
        self._move(steps)

    @retry()
    def move_right_steps(self, steps):
        abs_stps = abs(steps)
        if abs_stps > 30000:
            raise RuntimeError("Will not move more than 30.000 steps in total")
        self._logger.info("Moving %s steps to the right. This corresponds to %s mm", steps,
                          self._steps_to_mm(-1 * steps))
        self._move(-1 * steps)

    def _mm_to_steps(self, mm):
        return int(mm * 5977)

    def _steps_to_mm(self, steps):
        return steps * 0.000167308
