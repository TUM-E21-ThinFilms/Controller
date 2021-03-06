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

from truplasmadc_3000.factory import TruPlasmaDC3000Factory
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.thread import StoppableThread
from e21_util.retry import retry
from e21_util.cache import CACHE_TRUMPFDC, CACHE_TRUMPFDC_NAMESPACE, CACHE


class TruPlasmaDC3000Controller(object):
    cache = CACHE_TRUMPFDC

    INT_CHANNEL_CONTROL = 1
    CONTROL_RS232 = 1
    CONTROL_DISPLAY = 2

    FLOAT_CHANNEL_VOLTAGE_ON_THRESHOLD = 95
    FLOAT_CHANNEL_VOLTAGE_OFF_THRESHOLD = 76
    FLOAT_CHANNEL_VOLTAGE_ARC_THRESHOLD = 77

    BYTE_CHANNEL_LONG_RAMP = 0
    LONG_RAMP_POWER = 0
    LONG_RAMP_CURRENT = 1

    NORMAL_RUN_BIT_MAINS_RELAY = 1
    NORMAL_RUN_BIT_POWER_ON = 2
    NORMAL_RUN_BIT_RESET_ARC_COUNTER = 4
    NORMAL_RUN_BIT_ANALOG = 16
    NORMAL_RUN_BIT_PC_CONTROL = 32
    NORMAL_RUN_BIT_PROFIBUS_CONTROL = 64
    NORMAL_RUN_BIT_DISPLAY_CONTROL = 128

    DOC = """
        TruPlasmaDC3000Controller - Controller for the Trumpf Sputter power supply

        Usage:
            prepare_sputter(voltage [V], current [mA], power [W], bits = None): sets values for sputtering
            get_last_sputter_response(): returns the last response from the sputter device (contains power, current and voltage)
            turn_on(): sputters with previously set values
            turn_off(): turns sputtering off
    """

    def __init__(self, sputter=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_trumpf_sputter_logger()

        self.logger = logger

        if sputter is None:
            self.driver = TruPlasmaDC3000Factory().create_sputter()
        else:
            self.driver = sputter

        self.voltage, self.current, self.power, self.bits = None, None, None, None
        self.thread, self.set, self.last_sputter_response = None, False, None
        print(self.DOC)

    def get_driver(self):
        return self.driver

    @retry()
    def remote_control(self):
        self.driver.set_int(self.INT_CHANNEL_CONTROL, self.CONTROL_RS232)

    @retry()
    def local_control(self):
        self.driver.set_int(self.INT_CHANNEL_CONTROL, self.CONTROL_DISPLAY)

    def sputter_with_set_values(self):
        if self.set is True:
            self.last_sputter_response = self.sputter(self.voltage, self.current, self.power, self.bits)
            self.cache.put('last_sputter_response', self.last_sputter_response)
        else:
            raise RuntimeError("No predefined values set. Cannot sputter")

    def get_last_sputter_response(self):
        if 'last_sputter_response' in self.cache:
            return self.cache.get('last_sputter_response')
        else:
            return None

    @retry()
    def sputter(self, voltage, current, power, bits):
        if bits is None:
            bits = self.NORMAL_RUN_BIT_MAINS_RELAY | self.NORMAL_RUN_BIT_POWER_ON | self.NORMAL_RUN_BIT_PC_CONTROL | self.NORMAL_RUN_BIT_DISPLAY_CONTROL

        try:
            return self.driver.normal_run(voltage, current, power, bits)
        except Exception as e:
            self.logger.exception("Could not sputter")
            raise e

    def prepare_sputter(self, voltage, current, power, bits=None):
        self.voltage = voltage
        self.current = current
        self.power = power
        self.bits = bits
        self.set = True

    def on(self):
        self.turn_on()

    def off(self):
        self.turn_off()

    def turn_on(self):

        if self.set is False:
            raise RuntimeError("No sputter values set. Set them before turning sputter on!")

        time.sleep(0.3)

        self.remote_control()

        time.sleep(0.3)

        self.thread = SputterThread()
        self.thread.daemon = True
        self.thread.set_driver(self)
        self.thread.start()

    def turn_off(self):
        self.set = False

        if not self.thread is None:
            self.thread.stop()

        try:
            # turns off Mains relay and power.
            self.sputter(0, 0, 0, self.NORMAL_RUN_BIT_PC_CONTROL | self.NORMAL_RUN_BIT_DISPLAY_CONTROL)
            self.local_control()
            return True
        except Exception as e:
            self.logger.exception("Probably could not turn off sputter")
            return False

    def get_voltage_on_threshold(self):
        return self.driver.read_float(self.FLOAT_CHANNEL_VOLTAGE_ON_THRESHOLD)

    def set_voltage_on_threshold(self, threshold):
        return self.driver.set_float(self.FLOAT_CHANNEL_VOLTAGE_ON_THRESHOLD, threshold)

    def get_voltage_off_threshold(self):
        return self.driver.read_float(self.FLOAT_CHANNEL_VOLTAGE_OFF_THRESHOLD)

    def set_voltage_off_threshold(self, threshold):
        return self.driver.set_float(self.FLOAT_CHANNEL_VOLTAGE_OFF_THRESHOLD, threshold)

    def get_voltage_arc_threshold(self):
        return self.driver.read_float(self.FLOAT_CHANNEL_VOLTAGE_ARC_THRESHOLD)

    def set_voltage_arc_threshold(self, threshold):
        return self.driver.set_float(self.FLOAT_CHANNEL_VOLTAGE_ARC_THRESHOLD, threshold)

    def get_long_ramp(self):
        return self.driver.read_byte(self.BYTE_CHANNEL_LONG_RAMP)

    def set_long_ramp(self, ramp_type):
        if ramp_type not in [self.LONG_RAMP_POWER, self.LONG_RAMP_CURRENT]:
            raise ValueError("type of ramp must be either POWER or CURRENT")

        return self.driver.set_byte(self.BYTE_CHANNEL_LONG_RAMP, ramp_type)

    def get_current_voltage(self):
        return self.get_last_sputter_response().get_voltage()

    def get_current_power(self):
        return self.get_last_sputter_response().get_power()


class SputterThread(StoppableThread):
    def set_driver(self, driver):
        self.driver = driver

    def do_execute(self):
        self.driver.sputter_with_set_values()
        time.sleep(1)
