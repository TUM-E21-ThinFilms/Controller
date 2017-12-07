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

from edwards_nxds.factory import EdwardsNXDSFactory

from e21_util.retry import retry
from e21_util.interface import Loggable
from devcontroller.misc.logger import LoggerFactory


class nXDSController(Loggable):
    DOC = """
        Edwards nXDS Scroll pump controller

        Usage:

    """

    def __init__(self, pump=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_lakeshore_logger()

        super(nXDSController, self).__init__(logger)

        if pump is None:
            self.pump = EdwardsNXDSFactory().create_pump()
        else:
            self.pump = pump

        self.pump.clear()

        print(self.DOC)

    def get_logger(self):
        return self._logger

    def get_driver(self):
        return self.pump

    @retry()
    def on(self):
        self.pump.start_pump()

    @retry()
    def off(self):
        self.pump.stop_pump()

    @retry()
    def is_on(self):
        return self.pump.get_status().get_register1().flag_running() > 0

    @retry()
    def get_rotation(self):
        # returns the rotation of the pump in rpm.
        return self.pump.get_status().get_rotation() * 60

    @retry()
    def has_warning(self):
        return self.pump.get_status().get_register2().flag_warning() > 0

    @retry()
    def has_fault(self):
        return self.pump.get_status().get_register2().flag_fault() > 0