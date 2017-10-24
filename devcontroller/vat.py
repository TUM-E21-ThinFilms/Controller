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
from e21_util.error import ErrorResponse
from e21_util.retry import retry
from e21_util.interface import Loggable

class VATController(Loggable):

    DOC = """
        VATController - Controller for the VAT valve

        Usage:
            open(): Immediately opens the valve
            close(): Immediately closes the valve
            hold(): Holds the current open-status of the valve
            get_pressure() [mbar]: Returns the current pressure of the valve in mbar.
            set_pressure(pressure [mbar]): Sets the pressure for the valve in mbar.
            calibrate(): Calibrates the pressure with the Pfeiffer Gauge
    """

    def __init__(self, valve=None, logger=None, reference_gauge=None):
        if logger is None:
            logger = LoggerFactory().get_vat_valve_logger()

        super(VATController, self).__init__(logger)

        if not reference_gauge is None:
            self._gauge = reference_gauge
        else:
            self._gauge = PfeifferTPG26xFactory().create_gauge()

        if valve is None:
            factory = VAT590Factory()
            self.valve = factory.create_argon_valve()
        else:
            self.valve = valve

        self._pressure_range = 0
        self._sensor_offset = 0
        self.initialize()

        print(self.DOC)

    def get_driver(self):
        return self.valve

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

    def pressure_to_voltage(self, pressure):
        return self._pressure_to_voltage(pressure) * self._pressure_range / 10.0 - self._sensor_offset

    @retry()
    def get_pressure(self):
        return self._voltage_to_pressure(float(self.valve.get_pressure())/(self._pressure_range/10.0) + self._sensor_offset)

    @retry()
    def set_pressure(self, pressure):
        # pressure in mbar
        if pressure >= 1:
            raise ValueError("Will not set pressure higher than 1 mbar.")

        try:
            p_ref = self._gauge.get_pressure()
            p_vat = self.get_pressure()
        except Exception as e:
            self._logger.exception(e)
            raise ExecutionError("Could not check for correct pressure reading. See log files")

        relative_tolerance = 1.0

        if abs(p_vat / p_ref - 1.0) > relative_tolerance:
            raise ExecutionError("Reference pressure (%s) and VAT pressure (%s) differ more than 5%%!" % (str(p_ref), str(p_vat)))

        self.valve.clear()

        voltage = self._pressure_to_voltage(pressure)*self._pressure_range/10.0 - self._sensor_offset
        self.valve.set_pressure(int(voltage))

    @retry()
    def set_pressure_alignment(self, pressure):

        self.valve.clear()

        config = self.valve.get_sensor_configuration()
        config[1] = "1" # Enable zero - needed to set pressure alignment (otherwise not allowed)
        self.valve.set_sensor_configuration(config)

        voltage = self._pressure_to_voltage(pressure) * self._pressure_range / 10.0 - self._sensor_offset
        self.valve.set_pressure_alignment(int(voltage))
        self.initialize()

    @retry()
    def initialize(self):
        try:
            self.valve.clear()
            self._pressure_range = int(self.valve.get_pressure_range())
            self._sensor_offset  = int(self.valve.get_sensor_offset()/self._pressure_range/10.0)
        except ErrorResponse as e:
            raise e
        except Exception as e:
            self._logger.exception(e)
            raise ExecutionError("Could not initialize VAT. See log files")

    @retry()
    def open(self):
        self._logger.info('Opening valve...')
        self.valve.clear()
        self.valve.open()

    @retry()
    def close(self):
        self._logger.info('Closing valve...')
        self.valve.clear()
        self.valve.close()

    @retry()
    def hold(self):
        self.valve.clear()
        self.valve.hold()

    def calibrate(self):
        pressure = self._gauge.get_pressure()
        print("Pfeiffer pressure: %s" % str(pressure))
        self.set_pressure_alignment(pressure)

