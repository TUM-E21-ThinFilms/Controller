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

from julabo_fl.factory import JulaboFactory

class JulaboController(object):

    DOC = """
        JulaboController - Controlls the Julabo Cooler

        Usage:
            turn_on(): Turns the cooler on
            turn_off(): Turns the cooler off
            get_on(): Returns True if the cooler is on
            set_temperature(tmp [C]): sets the desired cooling temperature
            get_temperature(): gets the actual temperature
            get_version(): returns the version of the cooler
            get_driver(): returns the julabo driver
    """

    def __init__(self, julabo=None):
        if julabo is None:
            self.factory = JulaboFactory()
            self.julabo = self.factory.create_julabo()
        else:
            self.julabo = julabo

        self.julabo.clear()

        print(self.DOC)

    def get_driver(self):
        return self.julabo

    def turn_on(self):
        self.julabo.turn_on()

    def turn_off(self):
        self.julabo.turn_off()

    def get_on(self):
        return self.julabo.get_on() == 1

    def set_temperature(self, temperature):
        self.julabo.set_setpoint(temperature)

    def get_target_temperature(self):
        return self.julabo.get_setpoint()

    def get_temperature(self):
        return self.julabo.get_temperature()

    def get_version(self):
        return self.julabo.get_version()

    def on(self):
        self.turn_on()

    def off(self):
        self.turn_off()
