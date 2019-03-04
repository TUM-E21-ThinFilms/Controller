#  Copyright (C) 2019, see AUTHORS.md
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from e21_util.pvd.connection import Connection
from e21_util.pvd.devices import Devices

from devcontroller.misc.logger import LoggerFactory

from e21_util.paths import Paths
from e21_util.interruptor import Interruptor

from cesar136.factory import CesarFactory

from devcontroller.cesar import CesarController


class Instantiator(object):
    def __init__(self, connections):
        assert isinstance(connections, Connection)

        self._con = connections
        self._log = LoggerFactory()
        self._interrupt = Interruptor()

    def _get(self, device_name, interrupt):
        if interrupt is None:
            interrupt = self._interrupt

        transport = self._con.get_transport(device_name)
        logger = self._log.get(device_name)

        return transport, logger, interrupt

    def get_cesar(self, interrupt=None):
        transport, logger, interrupt = self._get(Devices.DEVICE_CESAR, interrupt)

        return CesarController(transport, logger, interrupt)
