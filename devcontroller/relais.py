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

from relais_197720.factory import RelaisFactory
from relais_197720.driver import RelaisDriver

class RelaisController(object):
    
    SCROLL_PORT = RelaisDriver.RELAIS_K1
    LAMP_PORT   = RelaisDriver.RELAIS_K3
    BYPASS_PORT = RelaisDriver.RELAIS_K4

    DOC = """
        RelaisController - Controls the Conrad 197720 Relais.

        Usage:
            scroll_on(), scroll_off(): Turns the scroll pump on/off
            lamp_on(), lamp_off()    : Turns the lamp on/off
            bypass_on(), bypass_off(): Opens/Closes the bypass
            off()                    : Turns all off (scroll, lamp, bypass)
            is_scroll_on(), ....     : Returns True if the scroll(...) is On.
            get_relais               : Returns the RelaisDriver

    """

    def __init__(self, relais=None):
        if relais is None:
            self.factory = RelaisFactory()
            self.relais  = self.factory.create_relais()  
        else:
            self.relais = relais
            
        self.relais.setup()

        print(self.DOC)
    
    def scroll_on(self):
        self.relais.set_single(self.SCROLL_PORT)
        
    def scroll_off(self):
        self.relais.del_single(self.SCROLL_PORT)
        
    def lamp_on(self):
        self.relais.set_single(self.LAMP_PORT)
        
    def lamp_off(self):
        self.relais.del_single(self.LAMP_PORT)
        
    def bypass_on(self):
        self.relais.set_single(self.BYPASS_PORT)
        
    def bypass_off(self):
        self.relais.del_single(self.BYPASS_PORT)
        
    def off(self):
        self.relais.set_port(0)
        
    def is_scroll_on(self):
        return self.relais.get_port().get_port() & self.SCROLL_PORT > 0
    
    def is_lamp_on(self):
        return self.relais.get_port().get_port() & self.LAMP_PORT > 0
    
    def is_bypass_on(self):
        return self.relais.get_port().get_port() & self.BYPASS_PORT > 0
        
    def get_relais(self):
        return self.relais
