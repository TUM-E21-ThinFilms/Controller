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

class CompressorController(object):

    DOC = """
        CompressorController - Controlls the compressor (Sumitomo F70H)

        Usage:
            turn_on(): Turns the compressor on
            turn_off(): Turns the compressor off
            reset(): Resets the compressor
            get_status(): returns the status
    """

    def __init__(self, compressor=None):
        if compressor is None:
            self.factory = SumitomoF70HFactory()
            self.julabo = self.factory.create()
        else:
            self.compressor = compressor

        self.compressor.clear()

        print(self.DOC)

    def turn_on(self):
        self.compressor.turn_on()

    def turn_off(self):
        self.compressor.turn_off()

    def get_all_temperatures(self):
        return self.get_all_temperatures()

    def reset(self):
        self.compressor.reset()

    def get_status(self):
        return self.compressor.status()

    def get_driver(self):
        return self.compressor


