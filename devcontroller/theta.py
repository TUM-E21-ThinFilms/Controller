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

import heidenhain

class HeidenhainThetaController(object):
    DOC = """ TODO """

    def __init__(self):
        self._encoder = None
        print(self.DOC)

    def __del__(self):
        if not self._encoder is None:
            self._encoder.disconnect()

    def connect(self):
        if not self._encoder is None:
            return True

        success = self._connect()

        if not success:
            self._encoder = None

        return True

    def _connect(self):
        self._encoder = heidenhain.GetEncoder()

        success = self._encoder.connect() and not self._encoder.hasError()

        if not success:
            return False

        if self._encoder.ReferenceMarkReceived():
            self._encoder.computeAbsoluteReferenceMark()

        return True

    def get_position(self):
        if self._encoder is None:
            return None

        self._encoder.clearFifo()

        if self._encoder.getNext():
            return self._encoder.getPosition()
        else:
            return None
