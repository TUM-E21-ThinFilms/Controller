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

import logging
from e21_util.paths import Paths

class LoggerFactory(object):

    LOG_FILE_CONTROLLER = Paths.LOG_PATH + 'controller.log'

    def _get_logger(self, name, file):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def get_turbo_logger(self):
        return self._get_logger('Controller: Turbo', self.LOG_FILE_CONTROLLER)

    def get_adl_sputter_logger(self):
        return self._get_logger('Controller: ADL Sputter', self.LOG_FILE_CONTROLLER)
    
    def get_trumpf_sputter_logger(self):
        return self._get_logger('Controller: Trumpf DC', self.LOG_FILE_CONTROLLER)

    def get_trumpf_rf_sputter_logger(self):
        return self._get_logger('Controller: Trumpf RF Sputter', self.LOG_FILE_CONTROLLER)

    def get_vat_valve_logger(self):
        return self._get_logger('Controller: VAT Valve', self.LOG_FILE_CONTROLLER)

    def get_shutter_logger(self):
        return self._get_logger('Controller: Shutter', self.LOG_FILE_CONTROLLER)

    def get_sample_theta_logger(self):
        return self._get_logger('Controller: Sample: Theta', self.LOG_FILE_CONTROLLER)

    def get_sample_z_logger(self):
        return self._get_logger('Controller: Sample: Z', self.LOG_FILE_CONTROLLER)

    def get_sample_x_logger(self):
        return self._get_logger('Controller: Sample: X', self.LOG_FILE_CONTROLLER)

    def get_lakeshore_logger(self):
        return self._get_logger('Controller: Lakeshore', self.LOG_FILE_CONTROLLER)

    def get_gun_logger(self):
        return self._get_logger('Controller: Gun', self.LOG_FILE_CONTROLLER)

    def get_julabo_logger(self):
        return self._get_logger('Controller: Julabo', self.LOG_FILE_CONTROLLER)

    def get_theta_logger(self):
        return self._get_logger('Controller: Theta', self.LOG_FILE_CONTROLLER)

    def get_relais_logger(self):
        return self._get_logger('Controller: Relais', self.LOG_FILE_CONTROLLER)

    def get_compressor_logger(self):
        return self._get_logger('Controller: Compressor', self.LOG_FILE_CONTROLLER)

    def get_gauge_logger(self):
        return self._get_logger('Controller: Gauge', self.LOG_FILE_CONTROLLER)

    def get_edwards_nxds_logger(self):
        return self._get_logger('Controller: Edwards nXDS', self.LOG_FILE_CONTROLLER)