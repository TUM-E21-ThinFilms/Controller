# Copyright (C) 2016, see AUTHORS.md
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
import time
from e21_util.gunparameter import *
from devcontroller.misc.logger import LoggerFactory
from e21_util.retry import retry
from e21_util.interface import Loggable
from e21_util.paths import Paths

from baur_pdcx85.driver import BaurDriver
from e21_util.gunparameter import GunConfig


class GunController(Loggable):
    DOC = """
        GunController - Controller for controller the gun position

            get_position():          Returns the position of the gun (in steps)
            set_position(position):  Sets the new position of the gun (in steps)
            move_left/right(steps):  Moves the gun left/right (in steps)
            get_gun():               Returns the current gun number which is above the target (1,2,3,4). If unknown, then 0
            set_gun(gun_number):     Moves gun such that gun_number is above the target
            calibrate(gun_number, tol=None, diff=None): Calibrates the controller. gun_number: current gun, tol: tolerance for
                                                        accepting a gun (in steps), diff: difference between two guns (in steps)

    """

    def __init__(self, driver, config_parser, logger=None):
        if logger is None:
            logger = LoggerFactory().get_gun_logger()

        super(GunController, self).__init__(logger)

        assert isinstance(driver, BaurDriver)
        assert isinstance(config_parser, GunConfigParser)

        self._driver = driver
        self._parser = config_parser
        self._config = self._parser.get_config()
        self._target_gun = None
        self._driver.initialize(4000, 1, 1, 10)

        self.current_pos_time = None
        self.current_pos_cached = None
        self.current_pos_time_limit = 0.5

        print(self.DOC)

    def update_config(self):
        self._config = self._parser.get_config()

    def get_driver(self):
        return self._driver

    @retry()
    def get_position(self):

        # A little implementation of a cache so that we do not kill the device by sending too much messages
        if self.current_pos_cached is None or abs(time.time() - self.current_pos_time) > self.current_pos_time_limit:
            self.current_pos_cached = self._driver.get_position()
            self.current_pos_time = time.time()

        return self.current_pos_cached

    @retry()
    def set_position(self, position):
        self._driver.position = position

    @retry()
    def move_left(self, steps):
        pos = self.get_position()
        self.set_position(pos - abs(int(steps)))

    @retry()
    def move_right(self, steps):
        self._driver.move_rel(abs(int(steps)))

    def move_angle(self, angle):
        # moving positive angles moves the gun to higher positions
        # since a higher position means lower steps, the sign must be negative
        total_steps = -1 * angle * self.steps_per_degree()
        self.set_position(self.get_position() + total_steps)

    def steps_per_degree(self):
        total_steps = sum([self._config.get_differences()])
        return total_steps / 270.0

    def compute_gun_position(self, gun_pos):
        self.is_valid_gun(gun_pos)

        step_gun_1 = self._config.get_absolute_gun_position()

        # Calculating the gun position works as follows:
        # 1. Calculate the steps to position 1 (starting from pos "current")
        # 2. Calculate the steps to position x (starting from pos 1)

        # Calculate the steps to position 1:
        current_steps = self.get_position()
        to_gun_1 = step_gun_1 - current_steps
        to_gun_x = self.step_difference(1, gun_pos)

        # Note that, it's on purpose a bit more complicated that just "step_difference(current, gun_pos),
        # because now one can move to any position even if the current gun position is not correctly defined.

        return current_steps + to_gun_1 - to_gun_x

    def is_valid_gun(self, gun):
        if not gun in [1, 2, 3, 4]:
            raise ValueError("Only guns 1, 2, 3, 4 are allowed")

        return True

    def step_difference(self, from_gun, to_gun):

        self.is_valid_gun(from_gun)
        self.is_valid_gun(to_gun)

        sgn = -1

        if from_gun > to_gun:
            from_gun, to_gun = to_gun, from_gun
            sgn = 1

        if from_gun == to_gun:
            return 0

        return sgn * sum(self._config.get_differences()[from_gun-1:to_gun-1])


    @retry()
    def get_gun(self):
        position = self.get_position()
        tol = self._config.get_tolerance()

        gun_1_pos = self.compute_gun_position(1)
        gun_2_pos = self.compute_gun_position(2)
        gun_3_pos = self.compute_gun_position(3)
        gun_4_pos = self.compute_gun_position(4)

        if abs(position - gun_1_pos) <= tol:
            return 1
        elif abs(position - gun_2_pos) <= tol:
            return 2
        elif abs(position - gun_3_pos) <= tol:
            return 3
        elif abs(position - gun_4_pos) <= tol:
            return 4
        else:
            return 0

    @retry()
    def stop(self):
        self.clear()
        self._driver.stop()

    def clear(self):
        self._driver.clear()

    def vend(self, value):
        self._driver.vend(value)

    def vstart(self, value):
        self._driver.vstart(value)

    def acc(self, value):
        self._driver.acc(value)

    @retry()
    def set_gun(self, pos):
        self._target_gun = pos
        steps = self.compute_gun_position(pos)
        self.set_position(steps)

    def wait(self, pos=None):
        if not pos is None:
            self.set_gun(pos)
        else:
            pos = self._target_gun

        if pos is None:
            return

        for i in range(0, 300):
            current = self.get_gun()
            if current == pos:
                return
            time.sleep(1)

        raise RuntimeError("Did not reach gun position %s in 300 seconds" % str(pos))

    def calibrate(self, actual_position, new_tol=None, new_diffs=None):
        self.is_valid_gun(actual_position)

        if new_tol is None or new_tol < 0:
            new_tol = self._config.get_tolerance()

        if new_diffs is None or not len(new_diffs) == 3:
            new_diffs = self._config.get_differences()

        # do this now, so that step_difference works with the updated values
        self._config.set_differences(new_diffs)

        gun_1_pos = self.get_position() + self.step_difference(actual_position, 1)


        self._config.set_tolerance(new_tol)
        self._config.set_absolute_gun_position(gun_1_pos)
        self._parser.write_config(self._config)
