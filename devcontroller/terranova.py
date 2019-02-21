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

from terranova_751a.driver import Terranova751ADriver

from e21_util.interface import Loggable
from e21_util.retry import retry


class TerranovaController(Loggable):
    DOC = """
        TerranovaController - Controls the Terranova 751 A Ion-Getter Pump
            
        Usage:
            on()/turn_on(): Turns the pump on
            off()/turn_off(): Turns the pump off
            is_on(): Returns True if the pump is turned on
            is_connected(): Returns True if the pump is connected and can be controlled
            get_voltage(): Returns the current voltage in V
            get_current(): Returns the current current in A
            get_pressure(): Returns the current pressure in the desired units (mBar typically), only if the pump is on
    """

    def __init__(self, driver, logger):
        super(TerranovaController, self).__init__(logger)
        assert isinstance(driver, Terranova751ADriver)

        self.driver = driver

        print(self.DOC)

    def get_driver(self):
        return self.driver

    def is_connected(self):
        try:
            self.driver.get_status()
            return True
        except:
            return False

    @retry()
    def is_on(self):
        return self.driver.get_hv() == Terranova751ADriver.HV_ON

    @retry()
    def turn_on(self):
        self.driver.set_hv(Terranova751ADriver.HV_ON)

    def on(self):
        self.turn_on()

    @retry()
    def turn_off(self):
        self.driver.set_hv(Terranova751ADriver.HV_OFF)

    def off(self):
        self.turn_off()

    @retry()
    def get_voltage(self):
        return self.driver.get_voltage()

    @retry()
    def get_current(self):
        return self.driver.get_current()

    @retry()
    def get_pressure(self):
        return self.driver.get_pressure()
