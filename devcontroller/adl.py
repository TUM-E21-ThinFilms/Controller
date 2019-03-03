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
from e21_util.retry import retry
from e21_util.interface import Loggable


class ADLController(Loggable):
    DOC = """
        ADLController - Controls the ADL Sputter power supply

        Usage:
            get_driver(): Returns the ADLDriver
            sputter(value, mode): Sputters with mode and value, i.e. mode=ADLSputterDriver.MODE_POWER, value=50 [Watt]
            sputter_power(power [W])/power(power [W]): Sputters in power mode with power in Watt
            sputter_voltage(voltage [V]): Sputters in voltage mode with voltage
            on()/turn_on(): Sputters with the pre-set values
            off()/turn_off(): Turns off sputtering immediately
    """

    def __init__(self, sputter=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_adl_sputter_logger()

        super(ADLController, self).__init__(logger)

        if sputter is None:
            factory = ADLSputterFactory()
            self.sputter = factory.create_sputter()
        else:
            self.sputter = sputter

        self.thread = None
        self.current_mode = None
        self.coeff_volt = None
        self.coeff_power = None
        self.coeff_current = None

        self.initialize()

        print(self.DOC)

    def get_driver(self):
        return self.sputter

    @retry(retry_count=2)
    def initialize(self):
        coeff = self.sputter.get_coefficients()

        self.coeff_volt = coeff.get_voltage()
        self.coeff_power = coeff.get_power()
        self.coeff_current = coeff.get_current()

    def __check_mode(self, new_mode):
        if self.current_mode is not None and not self.current_mode == new_mode:
            self._logger.error("Already sputtering in mode %s. Cannot sputter in new mode %s" % self.mode % new_mode)
            raise ExecutionError("Already sputtering in different mode.")

        self.current_mode = new_mode

    @retry()
    def sputter(self, value, mode=ADLSputterDriver.MODE_POWER):
        self.__check_mode(mode)
        self.sputter.clear()

        if mode == ADLSputterDriver.MODE_POWER:
            coeff = self.coeff_power
        if mode == ADLSputterDriver.MODE_VOLTAGE:
            coeff = self.coeff_volt
        if mode == ADLSputterDriver.MODE_CURRENT:
            coeff = self.coeff_current

        self.sputter.set_mode(mode, value, True, coeff=coeff)
        self.turn_on()

    @retry()
    def sputter_power(self, power):
        self.__check_mode(ADLSputterDriver.MODE_POWER)
        power = self.sputter.convert_into_power(power, coeff=self.coeff_power)
        self.sputter.clear()
        self.sputter.set_mode_p(power)

    @retry()
    def sputter_voltage(self, voltage):
        self.__check_mode(ADLSputterDriver.MODE_VOLTAGE)
        voltage = self.sputter.convert_into_voltage(voltage, coeff=self.coeff_volt)
        self.sputter.clear()
        self.sputter.set_mode_u(voltage)

    @retry()
    def turn_on(self):
        if self.thread is None or not self.thread.is_running():
            self.thread = TurnOnThread()
            self.thread.daemon = True
            self.thread.set_driver(self.sputter, self._logger)
            self.thread.start()
        else:
            self._logger.info('ADL-Sputter thread already running. Will continue...')

    @retry()
    def turn_off(self):
        if not self.thread is None:
            self.thread.stop()
            # self.thread = None

        self.current_mode = None
        self.sputter.turn_off()

    def on(self):
        self.turn_on()

    def off(self):
        self.turn_off()

    def power(self, sputter_power):
        self.sputter_power(sputter_power)

    @retry()
    def get_actual_values(self):
        return self.sputter.get_actual_value()

    def get_power(self):
        return self.sputter.convert_from_power(self.get_actual_values().get_power(), coeff=self.coeff_power)

    def get_voltage(self):
        return self.sputter.convert_from_voltage(self.get_actual_values().get_voltage(), coeff=self.coeff_volt)

    def get_current(self):
        return self.sputter.convert_from_current(self.get_actual_values().get_current(), coeff=self.coeff_current)


class TurnOnThread(StoppableThread):
    def __init__(self):
        super(TurnOnThread, self).__init__()
        self._logger = None
        self.driver = None

    def set_driver(self, driver, logger):
        self._logger = logger
        self.driver = driver

    def do_execute(self):
        try:
            self.driver.turn_on()
        except BaseException as e:
            self._logger.warning("Exception in sputter keep-alive thread. May result in plasma defect if this happens three times in a row.")

        time.sleep(1)
