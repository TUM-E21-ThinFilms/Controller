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

from ps9000.factory import PS9000Factory

class HeaterController(object):

    DOC = """
        HeaterController - Controls the Heater EA PS 9000

        Usage:
            turn_on(current=16), turn_off() : Turns the heater on/off
            measure()                       : Measures Voltage[V] and Current [A]
    """

    def __init__(self, supply=None):
        if supply is None:
            supply = PS9000Factory().create_powersupply()

        self.supply = supply

        print(self.DOC)

    def get_driver(self):
        return self.supply

    def turn_on(self, current = 16):
        self.supply.set_voltage(12)
        self.supply.set_current(current)
        self.supply.set_output(True)

    def turn_off(self):
        self.supply.set_current(0)
        self.supply.set_output(False)
        self.supply.reset()

    def measure(self):
        volt = self.supply.measure_voltage()
        current = self.supply.measure_current()

        return (str(volt) + 'V', str(current) + 'A')
