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
    PARAMETER_BOOST_CURRENT, PARAMETER_ENABLE_BOOST


class SampleController(object):
    DOC = """ TODO """

    AXIS_THETA = 1

    def __init__(self, module=1):
        self._mod = module
        self._driver_theta = PhytronFactory().create_driver()
        self._driver_theta.set_axis(1, 1)

        print(self.DOC)

    def _init_driver_theta(self):
        self._driver_theta.set_axis(self._mod, self.AXIS_THETA)

    def _set_speed_theta(self, rotations_per_minute):
        self._driver_theta.set_parameter(PARAMETER_MICROSTEP, 11)  # 1/128 pulse per step
        self._driver_theta.set_parameter(PARAMETER_CURRENT, 100)  # 1.0 A
        self._driver_theta.set_parameter(PARAMETER_FREQUENCY, int(rotations_per_minute * 200 * 128 / 60.0))
        self._driver_theta.set_parameter(PARAMETER_START_STOP_FREQUENCY, 1)  # 1 Hz start-stop freq.
        self._driver_theta.set_parameter(PARAMETER_BOOST_CURRENT, 200)  # 2.0 A
        self._driver_theta.set_parameter(PARAMETER_ENABLE_BOOST, 2)  # enables boost if motor is in ramp

    def move_degree(self, degree):
        # TODO
        steps = 128 * degree * 200.0

        self._driver_theta.move_relative(steps)

    def get_degree(self):
        pass

    def set_degree(self, degree):
        pass

    def get_driver_theta(self):
        return self._driver_theta
