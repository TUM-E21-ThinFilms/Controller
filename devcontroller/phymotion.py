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

from phytron_phymotion.factory import PhytronFactory
from phytron_phymotion.messages.parameter import PARAMETER_CURRENT, PARAMETER_FREQUENCY, PARAMETER_MICROSTEP, PARAMETER_START_STOP_FREQUENCY, \
    PARAMETER_BOOST_CURRENT, PARAMETER_ENABLE_BOOST, PARAMETER_STOP_CURRENT, PARAMETER_CURRENT_DELAY_TIME
from devcontroller.misc.logger import LoggerFactory
from e21_util.retry import retry
from e21_util.interface import Loggable


class ThetaMotorController(Loggable):
    AXIS_THETA = 1

    def __init__(self, module=1, logger=None):
        if logger is None:
            logger = LoggerFactory().get_theta_logger()

        super(ThetaMotorController, self).__init__(logger)

        self._speed = 0
        self._mod = module
        self._driver_theta = PhytronFactory().create_driver()
        self._init_driver_theta(0.8)

    @retry()
    def _init_driver_theta(self, rotations_per_minute):
        self._driver_theta.set_axis(self._mod, self.AXIS_THETA)
        self._driver_theta.set_parameter(PARAMETER_MICROSTEP, 11)  # 1/128 pulse per step
        self._driver_theta.set_parameter(PARAMETER_CURRENT, 150)  # 1.5 A
        self._driver_theta.set_parameter(PARAMETER_FREQUENCY, int(rotations_per_minute * 200 * 128 / 60.0))
        self._driver_theta.set_parameter(PARAMETER_START_STOP_FREQUENCY, 1)  # 1 Hz start-stop freq.
        self._driver_theta.set_parameter(PARAMETER_STOP_CURRENT, 10)  # 0.1 A stopping current
        self._driver_theta.set_parameter(PARAMETER_BOOST_CURRENT, 200)  # 2.0 A
        self._driver_theta.set_parameter(PARAMETER_ENABLE_BOOST, 2)  # enables boost if motor is in ramp
        self._driver_theta.set_parameter(PARAMETER_CURRENT_DELAY_TIME, 40)  # 40 ms of boost current after last movement
        self._driver_theta.set_parameter(32, 1)  # linear ramp form

    @retry()
    def set_speed(self, rotations_per_minute):
        if rotations_per_minute < 0 or rotations_per_minute > 10:
            raise RuntimeError("Given rpm is either too high or too low")

        # Nothing to do here
        if rotations_per_minute == self._speed:
            return

        self._driver_theta.set_parameter(PARAMETER_FREQUENCY, int(rotations_per_minute * 200 * 128 / 60.0))
        self._speed = rotations_per_minute

    @retry()
    def stop(self):
        self._driver_theta.stop()

    @retry()
    def is_moving(self):
        return not self._driver_theta.stopped()

    @retry()
    def move(self, steps):
        if steps > 15000:
            raise RuntimeError("Will not move more than 15000 steps!")

        self._driver_theta.move_relative(steps)

    def get_driver_theta(self):
        return self._driver_theta

    def get_driver(self):
        return self._driver_theta
