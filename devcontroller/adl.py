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

from adl_x547.driver import ADLSputterDriver
from adl_x547.factory import ADLSputterFactory

from devcontroller.misc.error import ExecutionError
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.thread import StoppableThread
from devcontroller.misc.sputtercheck import SputterChecker

class ADLController(object):

    DOC = """
        ADLController - Controls the ADL Sputter power supply

        Usage:
            get_sputter(): Returns the ADLDriver
            sputter(value, mode): Sputters with mode and value, i.e. mode=ADLSputterDriver.MODE_POWER, value=50 [Watt]
            sputter_power(power [W]): Sputters in power mode with power in Watt - immediately starts sputtering
            sputter_voltage(voltage [V]): Sputters in voltage mode with voltage - immediately starts sputtering
            turn_off(): Turns off sputtering immediately
    """

    def __init__(self, sputter=None, logger=None, checker=None):
        if logger is None:
            logger = LoggerFactory().get_adl_sputter_logger()
        
        self.logger = logger

        if checker is None:
            self.checker = SputterChecker()
        else:
            self.checker = checker

        if sputter is None:
            factory = ADLSputterFactory()
            self.sputter  = factory.create_sputter()
        else:
            self.sputter = sputter
            
        self.thread = None
        self.current_mode = None
        print(self.DOC)
            
    def get_driver(self):
        return self.sputter
            
    def get_logger(self):
        return self.logger

    def __check_mode(self, new_mode):
        if self.current_mode is not None and not self.current_mode == new_mode:
            self.logger.error("Already sputtering in mode %s. Cannot sputter in new mode %s" % self.mode % new_mode)
            raise ExecutionError("Already sputting in different mode.")

        self.current_mode = new_mode

    def sputter(self, value, mode=ADLSputterDriver.MODE_POWER):
        self.checker.check()
        self.__check_mode(mode)
        self.sputter.clear()
        self.sputter.set_mode(mode, value)
        self.turn_on()

    def sputter_power(self, power):
        self.checker.check()
        self.__check_mode(ADLSputterDriver.MODE_POWER)
        power = self.sputter.convert_into_power(power)
        self.sputter.clear()
        self.sputter.set_mode_p(power)
        #self.sputter.set_ramp(2000) # 2 seconds
        #self.sputter.activate_ramp()
        #self.turn_on()

    def sputter_voltage(self, voltage):
        self.checker.check()
        self.__check_mode(ADLSputterDriver.MODE_VOLTAGE)
        voltage = self.sputter.convert_into_voltage(voltage)
        self.sputter.clear()
        self.sputter.set_mode_u(voltage)
        #self.sputter.set_ramp(2000)
        #self.sputter.activate_ramp()
        #self.turn_on()
        
    def turn_on(self):
        self.checker.check()
        if self.thread is None or not self.thread.is_running():
            self.thread = TurnOnThread()
            self.thread.daemon = True
            self.thread.set_driver(self.sputter)
            self.thread.start()
        else:
            self.logger.info('Sputter thread already running. Will continue...')

    def turn_off(self):
        if not self.thread is None:
            self.thread.stop()

        self.mode = None
        self.sputter.turn_off()

class TurnOnThread(StoppableThread):

    def set_driver(self, driver):
        self.driver = driver

    def do_execute(self):
        self.driver.turn_on()
        time.sleep(1)
