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
        self._reference_computed = False
        self._calibration = 0
        print(self.DOC)

    def __del__(self):
        self.disconnect()

    def is_connected(self):
        return not self._encoder is None

    def connect(self):
        if not self._encoder is None:
            return True

        success = self._connect()

        if not success:
            self._encoder = None

        return True

    def _assert_connected(self):
        if not self.is_connected():
            raise RuntimeError("Encoder is not connected")

    def _assert_reference(self):
        return self._reference_computed

    def disconnect(self):
        if not self._encoder is None:
            self._encoder.disconnect()

    def start_reference(self):
        self._assert_connected()

        self.clear_reference()
        success = self._encoder.startReference()

        if not success:
            raise RuntimeError("Could not start the reference search")

    def received_reference(self):
        self._assert_connected()
        return self._encoder.receivedReference()

    def clear_reference(self):
        self._assert_connected()
        return self._encoder.clearReference()

    def stop_reference(self):
        self._assert_connected()

        received = self.received_reference()

        success = self._encoder.stopReference()
        if not success:
            raise RuntimeError("Could not stop the reference search")

        if received is True:
            self.compute_reference()
            return True

        return False

    def compute_reference(self):
        self._assert_connected()

        if not self._encoder.hasReference():
            raise RuntimeError("No reference available")

        success = self._encoder.computeAbsoluteReference()
        if not success:
            raise RuntimeError("Could not calculate absolute reference position")

        self._reference_computed = True

    def has_reference(self):
        self._assert_connected()

        return self._encoder.hasReference()

    def get_encoder(self):
        return self._encoder

    def _connect(self):
        self._encoder = heidenhain.get_theta_encoder()

        success = self._encoder.connect() and not self._encoder.hasError()

        if not success:
            return False

        if self._encoder.hasReference():
            self.compute_reference()

        return True

    def get_angle(self):
        self._assert_connected()
        self._assert_reference()

        return self._encoder.getAbsoluteDegree(True) + self._calibration

    def calibrate(self, new_angle):
        self._calibration = 0
        current_angle = self.get_angle()
        diff = new_angle - current_angle
        self._calibration = diff
