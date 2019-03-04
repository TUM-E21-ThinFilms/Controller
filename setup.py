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

import sys
import platform
from setuptools import setup, find_packages

requires_insitu = ['slave', 'relais_197720', 'stp_ix455', 'tpg26x', 'adl_x547', 'truplasmadc_3000', 'vat_590',
                   'vat_641', 'trinamic_pd110', 'lakeshore336', 'pfg_600', 'julabo_fl', 'ps9000', 'phytron_phymotion',
                   'baur_pdcx85', 'terranova_751a']

requires_pvd = ['cesar136']

requires_all = requires_insitu + requires_pvd

required = requires_all
user = platform.node()

if user == 'sputter-control':
    required = requires_insitu
elif user == 'e21-big-chamber':
    required = requires_pvd

setup(
    name='devcontroller',
    version=__import__('devcontroller').__version__,
    author='Alexander Book',
    author_email='alexander.book@frm2.tum.de',
    license='GNU General Public License (GPL), Version 3',
    url='https://github.com/TUM-E21-ThinFilms/Controller',
    description='Controller',
    long_description=open('README.md').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
)
