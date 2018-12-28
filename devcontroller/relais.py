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

from relais_197720.factory import RelayFactory
from relais_197720.constants import Relay
from devcontroller.misc.logger import LoggerFactory
from e21_util.retry import retry
from e21_util.interface import Loggable


# TODO: Rename to RelayController
class RelaisController(Loggable):

    RELAY_ADDRESS = 1

    SCROLL_PORT = (1, Relay.PORT_1)
    LAMP_PORT = (1, Relay.PORT_3)
    BYPASS_PORT = (1, Relay.PORT_4)
    HELIUM_PORT = (1, Relay.PORT_6)
    HELIUM_LEAK_PORT = (1, Relay.PORT_5)

    DOC = """
        RelayController - Controls the Conrad 197720 Relais.

        Usage:
            scroll_on(), scroll_off(): Turns the scroll pump on/off
            lamp_on(), lamp_off()    : Turns the lamp on/off
            bypass_on(), bypass_off(): Opens/Closes the bypass
            helium_on(), helium_off(): Opens/Closes the helium valve for the cryo
            off()                    : Turns all off (scroll, lamp, bypass)
            is_scroll_on(), ....     : Returns True if the scroll(...) is On.

    """

    def __init__(self, relay=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_relais_logger()

        super(RelaisController, self).__init__(logger)

        if relay is None:
            self.relay = RelayFactory().create_relay()
        else:
            self.relay = relay

        response = self.relay.setup()

        if not response.get_number_of_devices() == 1:
            raise RuntimeError(
                "Expected to have exactly one relay module, but got {}".format(response.get_number_of_devices()))

        print(self.DOC)

    @retry()
    def helium_on(self):
        self.relay.set_single(*self.HELIUM_PORT)
        self.relay.del_single(*self.HELIUM_LEAK_PORT)

    @retry()
    def helium_off(self, leak=True):
        self.relay.del_single(*self.HELIUM_PORT)
        if leak:
            self.relay.set_single(*self.HELIUM_LEAK_PORT)

    @retry()
    def helium_leak_on(self):
        self.relay.set_single(*self.HELIUM_LEAK_PORT)

    @retry()
    def helium_leak_off(self):
        self.relay.del_single(*self.HELIUM_LEAK_PORT)

    @retry()
    def scroll_on(self):
        self.relay.set_single(*self.SCROLL_PORT)

    @retry()
    def scroll_off(self):
        self.relay.del_single(*self.SCROLL_PORT)

    @retry()
    def lamp_on(self):
        self.relay.set_single(*self.LAMP_PORT)

    @retry()
    def lamp_off(self):
        self.relay.del_single(*self.LAMP_PORT)

    @retry()
    def bypass_on(self):
        self.relay.set_single(*self.BYPASS_PORT)

    @retry()
    def bypass_off(self):
        self.relay.del_single(*self.BYPASS_PORT)

    @retry()
    def off(self):
        self.relay.set_port(self.RELAY_ADDRESS, 0)

    @retry()
    def is_port_on(self, port):
        return self.relay.get_port(self.RELAY_ADDRESS).get_response().get_port() & port[1] > 0

    def is_scroll_on(self):
        return self.is_port_on(self.SCROLL_PORT)

    def is_lamp_on(self):
        return self.is_port_on(self.LAMP_PORT)

    def is_bypass_on(self):
        return self.is_port_on(self.BYPASS_PORT)

    def is_helium_on(self):
        return self.is_port_on(self.HELIUM_PORT)

    def is_helium_leak_on(self):
        return self.is_port_on(self.HELIUM_LEAK_PORT)

    def get_driver(self):
        return self.relay
