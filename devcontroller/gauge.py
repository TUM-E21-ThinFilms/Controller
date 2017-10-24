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

import os
import time

from e21_util.retry import retry
from e21_util.interface import Loggable
from devcontroller.misc.logger import LoggerFactory
from tpg26x.factory import PfeifferTPG26xFactory


class GaugeController(Loggable):
    TMP_FILE_GAUGE = '/media/ramdisk/gauge_continuous_measurement'

    DOC = """
        GaugeController - Controlls the gauges

        Usage:
            get_pressure(): Returns the pressure inside the chamber in mbar
    """

    def __init__(self, gauge=None, logger=None):

        if logger is None:
            logger = LoggerFactory().get_gauge_logger()

        super(GaugeController, self).__init__(logger)

        if gauge is None:
            self._gauge = PfeifferTPG26xFactory().create_gauge()
        else:
            self._gauge = gauge

        print(self.DOC)

    @retry()
    def get_pressure(self):
        # yay, someone already started the continuous measurement for this gauge!
        if os.path.isfile(self.TMP_FILE_GAUGE):
            return self._gauge.get_pressure()
        else:
            self._gauge.start_continuous_measurement()
            with open(self.TMP_FILE_GAUGE, "w") as f:
                f.write(str(int(time.time())))
            return self._gauge.get_pressure()

    def get_driver(self):
        return self._gauge
