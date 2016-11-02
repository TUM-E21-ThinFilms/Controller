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

class TurboController(object):
        
    def __init__(self, pump=None):
        if pump is None:
            factory = STPPumpFactory()
            self.pump  = factory.create_pump()
        else:
            self.pump = pump
            
    def get_pump(self):
        return self.pump
    
    def start(self):
        # TODO: check that the pressure is low enough.
        #       A too high pressure might damage the edwards turbo pump
        
        if not self.check_pressure():
            return False
        
        # Always switch back to local operation mode (i.e. the power supply), in case of
        # an error, one can always shut down the pump via the pressing a button on the power supply...
        try:
            self._to_remote_operation()
            self.pump.start()
        except:
            return False
        finally:
            self._to_local_operation()
            
    def stop(self):
        try:
            self._to_remote_operation()
            self.pump.stop()
        except:
            return False
        finally:
            self._to_local_operation()
            
    def get_rotation_speed(self):
        return self.pump.get_rotation().get_rotation_speed()
        
    def _to_remote_operation(self):
        opts = self.pump.prepare_options()
        opts.set_remote_operation_mode(SetOptionFuncMessage.REMOTE_OPERATION_MODE_X3)
        self.pump.set_options(opts)
        
    def _to_local_operation(self):
        opts = self.pump.prepare_options()
        opts.set_remote_operation_mode(SetOptionFuncMessage.REMOTE_OPERATION_MODE_POWER_SUPPLY)
        self.pump.set_options(opts)
