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

from error import ExecutionError

class SputterChecker(object):
    def __init__(self, julabo=None):
        if julabo is None:
            # TODO
            self.julabo = None
        else:
            self.julabo = julabo

        self.checked = False

    def check(self):
        if self.checked == True:
            return

        x = raw_input("Is the shutter closed and the flowmeter at maximum? (yes/no) : ")
        if (x != "yes" and x != "y"):
            print('Command aborted!')
            raise ExecutionError("Command aborted by user input")

        self.checked = True

class DisabledSputterChecker(SputterChecker):
    def check(self):
        pass
