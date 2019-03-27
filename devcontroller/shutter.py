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

from devcontroller.misc.thread import CountdownThread
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.error import ExecutionError

from e21_util.interface import Loggable
from e21_util.serial_connection import SerialTimeoutException
from e21_util.retry import retry

from trinamic_pd110.driver import TrinamicPD110Driver, Parameter


class ShutterController(Loggable):
    DOC = """
        ShutterController - Controls the Trinamic PD 110 Shutter.

        Usage:
            timer(self._timer [s]): opens the shutter, waits self._timer, closes shutter
            move(deg [degree]): moves the shutter for deg degree
            stop(): stops current movement
            open(), close(): opens/closes the shutter
            init(): Initializes the shutter to find the correct starting position
            reset(): Resets the shutter to the starting position (open() is then possible)
    """

    STATUS_UNKNOWN = 0
    STATUS_OPEN = 1
    STATUS_CLOSED = 2
    STATUS_CLOSED_RESET_REQUIRED = 3

    STEP_ANGLE = 1.8  # 1.8 degree per full step

    def __init__(self, shutter, logger, timer=None):
        super(ShutterController, self).__init__(logger)
        assert isinstance(shutter, TrinamicPD110Driver)

        self._status = self.STATUS_UNKNOWN

        if timer is None:
            timer = time

        self._timer = timer

        self._driver = shutter

        self.countdown_thread = None

        self.initialize()

        print(self.DOC)

    @retry()
    def is_on(self):
        response = self._driver.stop()
        return response.is_successful()

    def initialize(self, accel=100, speed=100):
        self._driver.set_axis_parameter(Parameter.Axis.MAX_ACCELERATION, accel)
        self._driver.set_axis_parameter(Parameter.Axis.MAX_POSITIONING_SPEED, speed)

    def get_driver(self):
        return self._driver

    @retry()
    def stop(self):
        self._driver.stop()

    def set_closed(self):
        self._status = self.STATUS_CLOSED

    def reset(self):
        self.stop()
        self._timer.sleep(0.3)
        self.initialize(10, 10)
        self._timer.sleep(0.3)
        self._driver.move(49)
        self._status = self.STATUS_CLOSED
        self._timer.sleep(7)
        self.initialize()

    def init(self):
        print("moving shutter to the leftmost position ...")
        self.initialize(10, 10)
        self._timer.sleep(0.3)
        self._driver.move(-75)
        self._timer.sleep(10)
        self._driver.move(49)
        self._timer.sleep(7)
        self.initialize()
        print("done.")
        self._status = self.STATUS_CLOSED

    def move(self, degree):
        full_steps_for_full_rotation = 360.0 / self.STEP_ANGLE

        # assuming motor is set to 1/64 micro steps
        full_rotation = full_steps_for_full_rotation * 64.0

        try:
            self._driver.move(int(float(degree) / 360.0 * full_rotation))
        except SerialTimeoutException:
            # It happens kind of often that the device does not respond
            # but it still moves ...
            pass

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
            self.move(-25)

        if self._status == self.STATUS_UNKNOWN:
            raise RuntimeError("Cannot open shutter. Shutter is in unknown position")

        self._status = self.STATUS_OPEN

    def close(self):
        if self._status == self.STATUS_OPEN:
            self.move(-23)
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

        if time_sec < 0.3:
            raise RuntimeError("Cannot sputter for less than 0.3 seconds")

        # 0.4 seconds, since this is the self._timer the shutter needs to open and close.
        time_sec = time_sec - 0.2

        try:
            self.countdown(time_sec)

            try:
                self.move(-25)
                self._status = self.STATUS_OPEN
            except KeyboardInterrupt:
                raise
            except Exception:
                self._logger.exception("Received exception while opening")
                raise ExecutionError("Could not open shutter")

            self._timer.sleep(time_sec)
        except KeyboardInterrupt:
            if not self.countdown_thread is None:
                self.countdown_thread.stop()

        try:
            self.move(-23)
            self._status = self.STATUS_CLOSED_RESET_REQUIRED
            # wait one second until the shutter is closed
            self._timer.sleep(1)
        except Exception:
            self._logger.exception("Received exception while closing")
            raise ExecutionError("Could not close shutter")

        self._logger.info("Sputtered for %s seconds.", str(time_sec))
