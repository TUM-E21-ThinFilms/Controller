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
from devcontroller.misc.thread import countdown

from devcontroller.insitu.instance import Instantiator

inst = Instantiator(Connection())

terranova = inst.get_ion_getter()
relay = inst.get_relay()
gun = inst.get_gun()
scroll = inst.get_scroll()
gauge = inst.get_gauge_main()
gauge_cryo = inst.get_gauge_cryo()
julabo = inst.get_julabo()

# TODO:
#   Add the following drivers to Instantiator ...
#

"""
julabo = JulaboController()

# terranova = TerranovaController()
adl_a = ADLController()
adl_b = ADLController(ADLSputterFactory().create_sputter_b())
vat_ar = VATController()
vat_o2 = VATController(VAT590Factory().create_oxygen_valve())

try:
    dc = TruPlasmaDC3000Controller()
except Exception as e:
    print(e)
    
shutter = ShutterController()
compressor = CompressorController()
lakeshore = LakeshoreController()
trumpfrf = TrumpfPFG600Controller()
heating = HeaterController()

turbovalve = TurboVATController()
# thermometer = VoltcraftIR1200Factory().create_thermometer()
phymotion = ThetaMotorController()
"""

DOC = """
         Available variables:
             adl_a, adl_b - ADLController
             terranova - TerranovaController
             vat_ar, vat_o2 - VATController
             shutter - ShutterController
             julabo  - JulaboController
             compressor - Cryo Compressor Controller
             lakeshore - Lakeshore Controller
             trumpfrf - Trumpf RF Sputter Controller
             relais - Relais Controller
             heating - Heating Controller for chamber
             gun  - Gun Motor (position=?, acc(), vstart(), vend())
             baurfac - Factory for baur motors (create_x_stage(), create_d_stage(), create_z_stage(), create_gun())
             gauge, gauge_cryo - Pfeiffer Gauge of the main chamber and the cryo
             thermometer - Voltcraft IR 1200 thermometer (get_temperature, clear, read() -> (get_ir(), get_ir_max/min/avg/diff, get_ktype))
             turbovalve - Controlls the valve between edwards turbo pump and main chamber
     Most deviced now support on() and off(). Sputtering via ADL/TrumpfRF with power mode can now be done via sputter()

     To exit, type "exit()"
"""

print(DOC)
