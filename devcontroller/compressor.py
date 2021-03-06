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

from sumitomo_f70h.factory import SumitomoF70HFactory
from e21_util.retry import retry
from e21_util.interface import Loggable

class CompressorController(Loggable):

    DOC = """
        CompressorController - Controls the compressor (Sumitomo F70H)

        Usage:
            turn_on(): Turns the compressor on
            turn_off(): Turns the compressor off
            reset(): Resets the compressor
            get_status(): returns the status
    """

    def __init__(self, compressor, logger):
        super(CompressorController, self).__init__(logger)

        self._driver = compressor

        self._driver.clear()

        print(self.DOC)

    @retry()
    def turn_on(self):
        self._driver.turn_on()

    @retry()
    def turn_off(self):
        self._driver.turn_off()

    @retry()
    def get_all_temperatures(self):
        return self._driver.get_all_temperatures()

    def reset(self):
        self._driver.reset()

    @retry()
    def get_status(self):
        return self._driver.get_status()

    @retry()
    def is_on(self):
        return self._driver.get_on()

    def get_driver(self):
        return self._driver

    def on(self):
        self.turn_on()

    def off(self):
        self.turn_off()

