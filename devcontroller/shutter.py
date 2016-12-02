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

import time

from trinamic_pd110.factory import TrinamicPD110Factory
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.error import ExecutionError

class ShutterController(object):

    DOC = """
        ShutterController - Controls the Trinamic PD 110 Shutter.

        Usage:
            timer(time [s]): opens the shutter, waits time, closes shutter
	        move(deg=180 [degree]): moves the shutter with deg degree
            get_shutter(): returns the TrinamicPD110Driver (for configuration purposes)
            get_logger(): returns the logger for this controller
    """

    def __init__(self, shutter=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_shutter_logger()

        self.logger = logger

        if shutter is None:
            factory = TrinamicPD110Factory()
            self.shutter = factory.create_shutter()
        else:
            self.shutter = shutter
	
        self.initialize()

        print(self.DOC)

    def initialize(self):
        self.shutter.acceleration=400
        self.shutter.speed_max=300

    def get_shutter(self):
        return self.shutter

    def get_logger(self):
        return self.logger

    def move(self, degree=180):
        self.shutter.move(degree)

    def timer(self, sputter_time):
        try:
            self.shutter.move(180)
        except Exception as e:
            self.logger.exception("Received exception while opening")
            raise ExecutionError("Could not open shutter")

        time.sleep(sputter_time)

        try:
            self.shutter.move(180)
        except:
            self.logger.exception("Received exception while closing")
            raise ExecutionError("Could not close shutter")

        self.logger.info("Sputtered for %s seconds.", str(sputter_time))


