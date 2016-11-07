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

from stp_ix455.factory import STPPumpFactory
from stp_ix455.messages.SetOptionFunc import SetOptionFuncMessage
from controller.logger import LoggerFactory
from tpg26x.driver import PfeifferTPG26xDriver
from controller.relais.controller import RelaisController

class TurboController(object):
        
    def __init__(self, pump=None, logger=None):
        if logger is None:
            logger = LoggerFactory().get_turbo_logger()
        
        self.logger = logger
        
        if pump is None:
            factory = STPPumpFactory()
            self.pump  = factory.create_pump()
        else:
            self.pump = pump  
            
    def get_pump(self):
        return self.pump
            
    def get_logger(self):
        return self.logger

    def start(self):        
        # Always switch back to local operation mode (i.e. the power supply), in case of
        # an error, one can always shut down the pump via the pressing a button on the power supply...
        try:
            self._to_remote_operation()
            self.pump.start()
        except Exception as e:
            self.logger.error("Error while starting pump: %s", e)
            return False
        finally:
            self._to_local_operation()
            
    def stop(self):
        try:
            self._to_remote_operation()
            self.pump.stop()
        except Exception as e:
            self.logger.error("Error while stopping pump: %s", e)
            return False
        finally:
            self._to_local_operation()
            
    def get_rotation_speed(self):
        return self.pump.get_rotation().get_rotation_speed()
        
    def _to_remote_operation(self):
        self.logger.debug("Switching pump to remote operation mode...")
        opts = self.pump.prepare_options()
        opts.set_remote_operation_mode(SetOptionFuncMessage.REMOTE_OPERATION_MODE_X3)
        self.pump.set_options(opts)
        
    def _to_local_operation(self):
        self.logger.debug("Switching pump to local operation mode...")
        opts = self.pump.prepare_options()
        opts.set_remote_operation_mode(SetOptionFuncMessage.REMOTE_OPERATION_MODE_POWER_SUPPLY)
        self.pump.set_options(opts)

class SafeController(TurboController):

    def __init__(self, pump=None, gauge=None, relais=None, logger=None):
        super(SafeController, self).__init__(pump, logger)
        
        if gauge is not None:
            self.set_gauge(gauge)
            
        if relais is not None:
            self.set_relais(relais)
            
        self.force = False
    
    def set_gauge(self, gauge):
        if not isinstance(gauge, PfeifferTPG26xDriver):
            raise TypeError()
            
        self.gauge = gauge
    
    def get_gauge(self):
        return self.gauge
    
    def set_relais(self, relais):
        if not isinstance(relais, RelaisController):
            raise TypeError()
            
        self.relais = relais
        
    def get_relais(self).
        return self.relais
    
    def check_pressure(self):
        if self.gauge is None:
            self.logger.error("No gauge controller set. Cannot check whether pressure is low enough...")
            return False
        
        try:
            reading, pressure = self.gauge.get_pressure_measurement()
            
            if pressure > 0.001:
                self.logger.error("Pressure is too high: %s", str(pressure))
                return False
            
        except Exception as e:
            self.logger.error("Could not read pressure: %s", e)
            return False
        
        return True
    
    def check_scroll(self):
        
        if self.scroll is None:
            self.logger.error("Cannot check whether the scroll pump is running...")
            return False
        
        try:
            status = self.relais.is_scroll_on()
            
            if not status:
                self.logger.error("Scroll pump is not turned on. Then Turbo cannot be turned on")
                return False
        except Exception as e:
            self.logger.error("Could not read scroll status: %s", e)
            return False
            
        return True
            
    def start(self):
        if not self.force:
            if not self.check_pressure():
                self.logger.error("Will not start the pump, since the pressure is not in range")
                return False

            if not self.check_scroll():
                self.logger.error("Will not start the pump, if the scroll pump is not running")
                return False
        
        self.unforce()        
        return super(SafeController, self).start()
        
    def force(self):
        self.force = True
    
    def unforce(self):
        self.force = False
    