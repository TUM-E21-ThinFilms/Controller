# Copyright (C) 2016, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERLTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
from lakeshore336.factory import LakeShore336Factory
from lakeshore336.driver import LakeShore336Driver

class LakeshoreController(object):

    DOC = """
        LakeshoreController - Controlls the Lakeshore 336

        Usage:
            heat(temperatue [K], input=1 [1-4], intensity=LakeShore336Driver.HEATER_RANGE_HIGH): turns on the heater.
            timer(time [minutes > 0], input=1 [1-4]): Turns the heater off after $time minutes on input.
            turn_off(input [1-4]): Turns the heater off on input.
    """

    def __init__(self, lakeshore=None):
        if lakeshore is None:
            self.factory = LakeShore336Factory()
            self.lakeshore = self.factory.create_lakeshore()
        else:
            self.lakeshore = lakeshore

        self.lakeshore.clear()

        print(self.DOC)

    def heat(self, heat, input=1, intensity=LakeShore336Driver.HEATER_RANGE_HIGH):
        self.lakeshore.set_control_setpoint(input, heat)
        self.lakeshore.set_heater_range(input, intensity)

    def timer(self, sleep_in_minutes, input=1):
        if not isinstance(sleep_in_minutes, (int, long)) or sleep_in_minutes <= 0:
            raise ValueError("A positive integer as `sleep_in_minutes` has to be given")

        print("Turn off heater in %s minutes:" % str(sleep_in_minutes))

        i = 1
        while i <= sleep_in_minutes:
            print("%s minute(s) remaining..." % str(sleep_in_minutes - i + 1))
            time.sleep(60)
            i = i+1

        self.turn_off(input)

    def turn_off(self, input):
        self.lakeshore.set_heater_range(input, LakeShore336Driver.HEATER_RANGE_OFF)

    def off(self):
        self.turn_off()

    def get_driver(self):
        return self.lakeshore