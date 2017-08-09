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
        self.disconnect()

    def connect(self):
        if not self._encoder is None:
            return True

        success = self._connect()

        if not success:
            self._encoder = None

        return True

    def disconnect(self):
        if not self._encoder is None:
            self._encoder.disconnect()

    def get_encoder(self):
        return self._encoder

    def _connect(self):
        self._encoder = heidenhain.get_theta_encoder()

        success = self._encoder.connect() and not self._encoder.hasError()

        if not success:
            return False

        if self._encoder.hasReference():
            self._encoder.computeAbsoluteReference()

        return True

    def get_position(self):
        if self._encoder is None:
            return None

        self._encoder.clearBuffer()

        if self._encoder.read():
            return self._encoder.getPosition()
        else:
            return None
