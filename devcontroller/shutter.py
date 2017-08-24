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
            timer(self._timer [s]): opens the shutter, waits self._timer, closes shutter
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

    def __init__(self, shutter=None, logger=None, timer=None):
        self._status = self.STATUS_UNKNOWN
        if timer is None:
            timer = time
            
        self._timer = timer

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
        self._timer.sleep(0.3)
        self.initialize(10, 10)
        self._timer.sleep(0.3)
        self.shutter.move(47)
        self._status = self.STATUS_CLOSED
        self._timer.sleep(7)
        self.initialize()

    def init(self):
        print("moving shutter to the leftmost position ...")
        self.initialize(10, 10)
        self._timer.sleep(0.3)
        self.shutter.move(-75)
        self._timer.sleep(10)
        self.shutter.move(47)
        self._timer.sleep(7)
        self.initialize()
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
            self.move(27)

        if self._status == self.STATUS_CLOSED:
            self.move(-21)

        if self._status == self.STATUS_UNKNOWN:
            raise RuntimeError("Cannot open shutter. Shutter is in unknown position")

        self._status = self.STATUS_OPEN

    def close(self):
        if self._status == self.STATUS_OPEN:
            self.move(-25)
            self._status = self.STATUS_CLOSED_RESET_REQUIRED
            self._timer.sleep(0.3)

        if self._status == self.STATUS_CLOSED_RESET_REQUIRED:
            return

        if self._status == self.STATUS_CLOSED:
            return

        raise RuntimeError("Cannot close shutter. Shutter is in unknown position")

    def timer(self, time_sec):

        if not self._status == self.STATUS_CLOSED:
            raise RuntimeError("Shutter is currently not closed!")

        if time_sec < 0.5:
            raise RuntimeError("Cannot sputter for less than 0.5 seconds")

        # 0.4 seconds, since this is the self._timer the shutter needs to open and close.
        time_sec = time_sec - 0.4

        try:
            self.countdown(time_sec)

            try:
                self.shutter.move(-21)
                self._status = self.STATUS_OPEN
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.exception("Received exception while opening")
                raise ExecutionError("Could not open shutter")

            self._timer.sleep(time_sec)
        except KeyboardInterrupt:
            if not self.countdown_thread is None:
                self.countdown_thread.stop()

        try:
            self.shutter.move(-25)
            self._status = self.STATUS_CLOSED_RESET_REQUIRED
        except:
            self.logger.exception("Received exception while closing")
            raise ExecutionError("Could not close shutter")

        self.logger.info("Sputtered for %s seconds.", str(time_sec))
