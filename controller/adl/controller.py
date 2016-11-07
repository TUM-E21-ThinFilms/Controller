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

from adl_547.factory import ADLSputterFactory
from adl_547.driver import ADLSputterDriver
from controller.logger import LoggerFactory

class ADLController(object):
        
    def __init__(self, sputter=None)
        if logger is None:
            logger = LoggerFactory().get_adl_sputter_logger()
        
        self.logger = logger
        
        if sputter is None:
            factory = ADLSputterFactory()
            self.sputter  = factory.create_sputter()
        else:
            self.sputter = sputter
            
        self.thread = None
            
    def get_sputter(self):
        return self.sputter
            
    def get_logger(self):
        return self.logger
    
    def sputter_power(self, power=50):
        power_coeff = self.sputter.convert_into_power(power)
        self.sputter.clear()
        self.sputter.set_mode_p(power_coeff)
        self.sputter.set_ramp(2000) # 2 seconds
        self.sputter.activate_ramp()
        self.turn_on()
        
    def turn_on(self):
        self.thread = TurnOnThread()
        self.thread.daemon = True
        self.thread.set_driver(self.sputter)
        self.thread.start()	
        
    def turn_off(self):
        if not self.thread is None:
            self.thread.stop()

        self.sputter.turn_off()
        
class StoppableThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = False

    def run(self):
	    while not self._stop:
	        self.do_execute()

    def stop(self):
        self._stop = True

    def do_execute():
	    pass

class TurnOnThread(StoppableThread):

    def set_driver(self, driver):
	    self.driver = driver

    def do_execute(self):
	    self.driver.turn_on()
	    time.sleep(1)		
