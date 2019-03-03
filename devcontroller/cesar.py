# Copyright (C) 2019, see AUTHORS.md
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

from cesar136.driver import Driver
from cesar136.constants import Parameter

from devcontroller.misc.error import ExecutionError
from devcontroller.misc.thread import StoppableThread

from e21_util.retry import retry
from e21_util.interface import Loggable, Interruptable
from e21_util.interruptor import InterruptableTimer


class CesarController(Loggable, Interruptable):
    DOC = """
        CesarController - Controls the Cesar 136 sputter power supply

        Usage:
            get_driver(): Returns the Driver
            is_connected(): Tests whether there is a connection to the power supply
            sputter(value, mode): Sputters with mode and value, i.e. mode=Parameter.ControlMode.SERIAL_CONTROL, value=50 [Watt]
            power(power [W]): Sputters in power mode with power in Watt
            on()/turn_on(): Sputters with the pre-set values
            off()/turn_off(): Turns off sputtering immediately
            get_power(): Returns the delivered power to target
    """

    def __init__(self, driver, logger, interruptor):
        Loggable.__init__(self, logger)
        Interruptable.__init__(self, interruptor)

        assert isinstance(driver, Driver)

        self._driver = driver
        self._thread = None
        self._current_mode = None

        self.initialize()

        print(self.DOC)

    def get_driver(self):
        return self._driver

    def is_connected(self):
        try:
            return len(self._driver.get_model_number().get_parameter().get()) > 0
        except BaseException as e:
            return False

    @retry(retry_count=2)
    def initialize(self):
        self._driver.clear()
        self._driver.set_control_mode(Parameter.ControlMode.SERIAL_CONTROL)
        self._driver.set_remote_control(Parameter.ControlOverride.BIT_ENABLE_ON_OFF_BUTTON)
        self._driver.set_user_port_scaling(40)
        self._driver.set_time_limit(3)
        self._driver.set_reflected_power_limit(50)
        self._driver.set_reflected_power_parameters(3, 40)

    def _check_mode(self, new_mode):
        if self.current_mode is not None and not self.current_mode == new_mode:
            self._logger.error(
                "Already sputtering in mode %s. Cannot sputter in new mode %s".format(self.mode, new_mode))
            raise ExecutionError("Already sputtering in different mode.")

        self._current_mode = new_mode

    @retry()
    def sputter(self, value, mode=Parameter.Regulation.LOAD_POWER):
        self._check_mode(mode)
        self._driver.clear()

        self._driver.set_regulation_mode(mode)
        self._driver.set_setpoint(value)

        self.turn_on()

    @retry()
    def turn_on(self):
        if self._thread is None or not self._thread.is_running():
            self._thread = TurnOnThread(InterruptableTimer(self._interruptor, 0.1))
            self._thread.daemon = True
            self._thread.set_driver(self._driver, self._logger)
            self._thread.start()

    @retry()
    def turn_off(self):
        if not self.thread is None:
            self._thread.stop()

        self._thread = None
        self._current_mode = None
        self._driver.turn_off()

    def on(self):
        self.turn_on()

    def off(self):
        self.turn_off()

    def power(self, power):
        self.sputter(power)

    @retry()
    def get_power(self):
        return self._driver.get_delivered_power()


class TurnOnThread(StoppableThread):
    def __init__(self, timer):
        super(TurnOnThread, self).__init__()
        self._timer = timer
        self._logger = None
        self._driver = None

    def set_driver(self, driver, logger):
        self._logger = logger
        self._driver = driver

    def do_execute(self):
        try:
            self._driver.turn_on()
        except BaseException as e:
            self._logger.warning(
                "Exception in sputter keep-alive thread. May result in plasma defect if this happens three times in a row.")

        self._timer.sleep(0.5)
