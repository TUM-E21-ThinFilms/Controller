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

from math import log10
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.error import ExecutionError
from vat_641.factory import VAT641Factory

class TurboVATController(object):

    DOC = """
        TurboVATController - Controller for the Turbo VAT valve

        Usage:
            open(): Immediately opens the valve
            close(): Immediately closes the valve
            hold(): Holds the current open-status of the valve
            get_open(): Return the percentage of the valve position. 100^= open, 0^= close
            set_speed(speed [0-1000]): Sets the speed for opening and closing the valve
            set_position(pos [0-1000]): Sets the position: 1000 ^= open, 0^= close
            get_valve(): Returns the valve driver
    """

    def __init__(self, valve=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_vat_valve_logger()

        self.logger = logger

        if valve is None:
            factory = VAT641Factory()
            self.valve = factory.create_valve()
        else:
            self.valve = valve

        print(self.DOC)

    def _to_remote(self):
        self.valve.switch_to_remote_mode()

    def _to_local(self):
        self.valve.switch_to_local_mode()

    def get_valve(self):
        return self.valve

    def get_logger(self):
        return self.logger

    def open(self):
        self._to_remote()
        self.valve.open()
        self._to_local()

    def close(self):
        self._to_remote()
        self.valve.close()
        self._to_local()

    def holde(self):
        self._to_remote()
        self.valve.hold()
        self._to_local()

    def get_open(self):
        return self.valve.get_open()

    def set_speed(self, speed):
        self._to_remote()
        self.valve.set_speed(speed)
        self._to_local()

    def set_position(self, position):
        self._to_remote()
        self.valve.position(position)
        self._to_local()