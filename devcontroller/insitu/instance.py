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

from e21_util.insitu.connection import Connection
from e21_util.insitu.devices import Devices

from devcontroller.misc.logger import LoggerFactory

from encoder.factory import Factory

from relais_197720.factory import RelayFactory
from terranova_751a.factory import Terranova751AFactory
from phytron_phymotion.factory import PhytronFactory
from baur_pdcx85.factory import BaurFactory
from edwards_nxds.factory import EdwardsNXDSFactory
from tpg26x.factory import PfeifferTPG26xFactory
from julabo_fl.factory import JulaboFactory

from devcontroller.relay import RelayController
from devcontroller.terranova import TerranovaController
from devcontroller.phymotion import ThetaMotorController
from devcontroller.sampletheta import SampleThetaController
from devcontroller.gun import GunController
from devcontroller.samplex import SampleXController
from devcontroller.samplez import SampleZController
from devcontroller.nxds import nXDSController
from devcontroller.julabo import JulaboController

from e21_util.paths import Paths
from e21_util.gunparameter import GunConfigParser


class Instantiator(object):
    def __init__(self, connections):
        assert isinstance(connections, Connection)

        self._con = connections
        self._log = LoggerFactory()

    def _get(self, device_name):
        transport = self._con.get_transport(device_name)
        logger = self._log.get(device_name)

        return transport, logger

    def get_relay(self):
        transport, logger = self._get(Devices.DEVICE_RELAY)
        driver = RelayFactory.create(transport, logger)

        return RelayController(driver, self._log.get_relay_logger())

    def get_ion_getter(self):
        transport, logger = self._get(Devices.DEVICE_TERRANOVA)
        driver = Terranova751AFactory.create(transport, logger)

        return TerranovaController(driver, self._log.get_terranova_logger())

    def get_theta_motor(self):
        transport, logger = self._get(Devices.DEVICE_THETA)
        driver = PhytronFactory.create(transport, logger)

        return ThetaMotorController(driver, self._log.get_theta_logger())

    def get_position_encoder(self):
        return Factory().get_interface()

    def get_theta_sample(self):
        return SampleThetaController(self.get_theta_motor(), self.get_position_encoder(),
                                     self._log.get_sample_theta_logger())

    def get_gun_driver(self):
        transport, logger = self._get(Devices.DEVICE_GUN)
        return BaurFactory.create(transport, logger)

    def get_gun(self):
        config_parser = GunConfigParser(Paths.GUN_CONFIG_PATH)
        return GunController(self.get_gun_driver(), config_parser)

    def get_x_motor(self):
        transport, logger = self._get(Devices.DEVICE_X_MOTOR)
        return BaurFactory.create(transport, logger)

    def get_x(self):
        return SampleXController(self.get_x_motor(), self._log.get_x_logger())

    def get_z_motor(self):
        transport, logger = self._get(Devices.DEVICE_Z_MOTOR)
        return BaurFactory.create(transport, logger)

    def get_z(self):
        return SampleZController(self.get_z_motor(), self.get_position_encoder(), self._log.get_z_logger())

    def get_scroll(self):
        transport, logger = self._get(Devices.DEVICE_SCROLL)
        return nXDSController(EdwardsNXDSFactory.create(transport, logger), logger)

    def get_gauge_main(self):
        transport, logger = self._get(Devices.DEVICE_GAUGE_MAIN_CHAMBER)
        return PfeifferTPG26xFactory.create(transport, logger)

    def get_gauge_cryo(self):
        transport, logger = self._get(Devices.DEVICE_GAUGE_CRYO)
        return PfeifferTPG26xFactory.create(transport, logger)

    def get_julabo(self):
        transport, logger = self._get(Devices.DEVICE_JULABO)
        return JulaboController(JulaboFactory.create(transport, logger), logger)