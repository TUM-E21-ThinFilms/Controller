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

from math import log10
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.error import ExecutionError
from vat_590.factory import VAT590Factory
from tpg26x.factory import PfeifferTPG26xFactory

class VATController(object):

    DOC = """
        VATController - Controller for the VAT valve

        Usage:
            open(): Immediately opens the valve
            close(): Immediately closes the valve
            hold(): Holds the current open-status of the valve
            get_pressure() [mbar]: Returns the current pressure of the valve in mbar.
            set_pressure(pressure [mbar]): Sets the pressure for the valve in mbar.
            get_valve(): Returns the valve driver
            set_pressure_alignment(pressure [mbar]): Sets the alignment of the pressure (i.e. adjust pressure output)

    """

    def __init__(self, valve=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_vat_valve_logger()

        self.logger = logger

        if valve is None:
            factory = VAT590Factory()
            self.valve = factory.create_argon_valve()
        else:
            self.valve = valve

        self._pressure_range = 0
        self._sensor_offset = 0
        self.initialize()

        print(self.DOC)

    def get_valve(self):
        return self.valve

    def get_logger(self):
        return self.logger

    """
        Converts a voltage (FullRange Gauge PKR 261) to a pressure in mbar.
    """
    def _voltage_to_pressure(self, voltage):
        # We're using the formula provided by Pfeiffer for the Compact FullRange Gauge PKR 261:
        # pressure p [mbar] = 10^(1.667 * U - d) where
        #   U is the given signal from the gauge
        #   d is a constant, namely d = 11.33

        #volt = voltage / ( self._pressure_range / 10.0)  + self._sensor_offset
        return pow(10, 1.667 * voltage - 11.33)

    """
        Converts a pressure [mbar] into a voltage.
    """
    def _pressure_to_voltage(self, pressure):
        # We're using the formula provided by Pfeiffer for the Compact FullRange Gauge PKR 261:
        # voltage U [V] = c + 0.6* log_10(p)   where
        # c = 6.8 a constant
        # p the given pressure in [mbar]
        return 6.8 + 0.6 * log10(pressure)

    def get_pressure(self):
        return self._voltage_to_pressure(float(self.valve.get_pressure())/(self._pressure_range/10.0) + self._sensor_offset)

    """
        Sets the pressure in mbar
    """
    def set_pressure(self, pressure):
        if pressure >= 1:
            raise ValueError("Will not set pressure higher than 1 mbar.")

        self.valve.clear()

        voltage = self._pressure_to_voltage(pressure)*self._pressure_range/10.0 - self._sensor_offset
        self.valve.set_pressure(int(voltage))

    def set_pressure_alignment(self, pressure):
        self.valve.clear()
        voltage = self._pressure_to_voltage(pressure) * self._pressure_range / 10.0 - self._sensor_offset
        self.valve.set_pressure_alignment(int(voltage))

    def initialize(self):
        try:
            self.valve.clear()
            self._pressure_range = int(self.valve.get_pressure_range())
            self._sensor_offset  = int(self.valve.get_sensor_offset())
        except Exception as e:
            self.logger.exception("Could not initialize VAT Controller")
            raise ExecutionError("Could not initialize VAT. See log files")

    def open(self):
        self.logger.info('Opening valve...')
        self.valve.clear()
        self.valve.open()

    def close(self):
        self.logger.info('Closing valve...')
        self.valve.clear()
        self.valve.close()

    def hold(self):
        self.valve.clear()
        self.valve.hold()

    def calibrate(self):
        pfeiffer_gauge = PfeifferTPG26xFactory.create_gauge()
        self.set_pressure_alignment(pfeiffer_gauge.get_pressure_measurement()[1])
