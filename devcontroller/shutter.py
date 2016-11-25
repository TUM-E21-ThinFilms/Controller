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

class ShutterController(object):

    DOC = """
        ShutterController - Controls the Trinamic PD 110 Shutter.

        Usage:
            sputter(time [s]): opens the shutter, waits time, closes shutter
            automatic_sputter(time [s]): same as sputter(time), except no user input required.
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

        print(self.DOC)

    def get_shutter(self):
        return self.shutter

    def get_logger(self):
        return self.logger

    def automatic_sputter(self, sputter_time):
        try:
            self.shutter.move(180)
        except Exception as e:
            self.logger.exception("Received exception while opening")
            print("Error on execution")

        time.sleep(sputter_time)

        try:
            self.shutter.move(180)
        except:
            self.logger.exception("Received exception while closing")
            print("Error on execution")

        self.logger.info("Sputtered for %s seconds.", str(sputter_time))

    def sputter(self, sputter_time):
        x = raw_input("Is the shutter closed? (yes/no) : ")
        if x != "yes":
            self.logger.warning("Aborted sputtering due to a open shutter.")
            print('Shutter: Command aborted!')
            return

        self.automatic_sputter(sputter_time)
