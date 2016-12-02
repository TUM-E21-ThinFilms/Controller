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

from pfg_600.factory import PFG600Factory
from pfg_600.driver import PFG600Driver
from devcontroller.misc.error import ExecutionError
from devcontroller.misc.logger import LoggerFactory
from devcontroller.misc.sputtercheck import SputterChecker

class TrumpfPFG600Controller(object):

    DOC = """
        TrumpfPFG600Controller - Controller for the Trumpf RF PFG 600 Series

        Usage:
            turn_on(): Turns the sputtering process on
            turn_off(): Turns the sputtering process off
            sputter_power(power [W], voltage_limit [V]): Sets the power mode
            sputter_voltage(voltage [V], power_limit [W]): Sets the volage mode
            reset(): resets the sputter

    """

    def __init__(self, sputter=None, logger=None, checker=None):
        if logger is None:
            logger = LoggerFactory().get_trumpf_rf_sputter_logger()

        self.logger = logger

        if checker is None:
            checker = SputterChecker()

        self.checker = checker

        if sputter is None:
            factory = PFG600Factory()
            self.sputter = factory.create_pfg600()
        else:
            self.sputter = sputter

        print(self.DOC)

    def get_sputter(self):
        return self.sputter

    def turn_off(self):
        try:
            self.sputter.clear()
        except:
            self.logger.exception('Exception while clearing message pipe')

        try:
            self.sputter.set_operating_status(PFG600Driver.OFF)
        except BaseException:
            self.logger.exception('Exception while turning sputter off')
            raise ExecutionError('Error while turning sputter off')

    def turn_on(self):
        self.checker.check()

        try:
            self.sputter.set_operating_status(PFG600Driver.ON)
        except BaseException:
            self.logger.exception('Exception while turning sputter on')
            raise ExecutionError('Error while turning sputter on')

    def is_on(self):
        try:
            return self.sputter.get_operating_status() == PFG600Driver.ON
        except:
            self.logger.exception('Could not determine status of rf sputter')
            raise ExecutionError('Cannot determine status of rf sputter')

    def sputter_power(self, power, voltage_limit):
        self.sputter.clear()
        self.sputter.set_target_power(power)
        self.sputter.set_target_voltage(voltage_limit)
        self.sputter.set_regulate(PFG600Driver.REGULATE_POWER)

    def sputter_voltage(self, voltage, power_limit):
        self.sputter.clear()
        self.sputter.set_target_voltage(voltage)
        self.sputter.set_target_power(power_limit)
        self.sputter.set_regulate(PFG600Driver.REGULATE_VOLTAGE)

    def reset(self):
        self.sputter.clear()
        self.sputter.reset()