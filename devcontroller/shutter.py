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
from devcontroller.misc.thread import CountdownThread
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.error import ExecutionError

class ShutterController(object):

    DOC = """
        ShutterController - Controls the Trinamic PD 110 Shutter.

        Usage:
            timer(time [s]): opens the shutter, waits time, closes shutter
            move(deg=180 [degree]): moves the shutter with deg degree
            stop(): stoppes current movement
            open(), close(): opens/closes the shutter
            init(): Initializes the shutter to find the correct starting position
            reset(): Resets the shutter to the starting position (open() is then possible)
    """

    STATUS_UNKNOWN = 0
    STATUS_OPEN = 1
    STATUS_CLOSED = 2
    STATUS_CLOSED_RESET_REQUIRED = 3

    def __init__(self, shutter=None, logger=None):
        self._status = self.STATUS_UNKNOWN


        if logger is None:
            logger = LoggerFactory().get_shutter_logger()

        self.logger = logger

        if shutter is None:
            factory = TrinamicPD110Factory()
            self.shutter = factory.create_shutter()
        else:
            self.shutter = shutter

        self.countdown_thread = None

        self.initialize()

        print(self.DOC)

    def initialize(self, accel=100, speed=100):
        self.shutter.acceleration=accel
        self.shutter.speed_max=speed

    def get_driver(self):
        return self.shutter

    def get_logger(self):
        return self.logger

    def stop(self):
        self.shutter.stop()

    def reset(self):
        self.stop()
        self.initialize(5, 10)
        time.sleep(0.5)
        self.shutter.move(46)
        self._status = self.STATUS_CLOSED

    def init(self):
        print("moving shutter to the leftmost position ...")
        self.initialize(10, 10)
        time.sleep(1)
        self.shutter.move(-23)
        time.sleep(5)
        self.shutter.move(-23)
        time.sleep(5)
        self.shutter.move(46)
        print("done.")
        self._status = self.STATUS_CLOSED

    def move(self, degree=180):
        self.shutter.move(degree)

    def countdown(self, t):
        thread = CountdownThread()
        thread.set_time(t)
        thread.daemon = True
        thread.start()
        self.countdown_thread = thread

    def open(self):
        if self._status == self.STATUS_OPEN:
            return

        if self._status == self.STATUS_CLOSED_RESET_REQUIRED:
            self.move(23)

        if self._status == self.STATUS_CLOSED:
            self.move(-23)

        if self._status == self.STATUS_UNKNOWN:
            raise RuntimeError("Cannot opend shutter. Shutter is in unknown position. Do a init()")

        self._status = self.STATUS_OPEN

    def close(self):
        if self._status == self.STATUS_OPEN:
            self.move(23)
            self._status = self.STATUS_CLOSED

        if self._status == self.STATUS_CLOSED_RESET_REQUIRED:
            return

        if self._status == self.STATUS_CLOSED:
            return

        raise RuntimeError("Cannot close shutter. Shutter is in unknown position. Do a init()")

    def timer(self, sputter_time):

        if not self._status == self.STATUS_CLOSED:
            raise RuntimeError("Shutter is currently not closed!")

        if sputter_time < 0.5:
            raise RuntimeError("Cannot sputter for less than 0.5 seconds")

        self.initialize()
        time.sleep(0.5)
        self.logger.info("Timer set for %s seconds", str(sputter_time))
        # 0.4 seconds, since this is the time the shutter needs to open and close.
        sputter_time = sputter_time - 0.4

        try:
            self.countdown(sputter_time)

            try:
                self.shutter.move(-23)
                self._status = self.STATUS_OPEN
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.exception("Received exception while opening")
                raise ExecutionError("Could not open shutter")

            time.sleep(sputter_time)
        except KeyboardInterrupt:
            if not self.countdown_thread is None:
                self.countdown_thread.stop()

        try:
            self.shutter.move(-23)
            self._status = self.STATUS_CLOSED_RESET_REQUIRED
        except:
            self.logger.exception("Received exception while closing")
            raise ExecutionError("Could not close shutter")

        self.logger.info("Sputtered for %s seconds.", str(sputter_time))
