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

import threading

class StoppableThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = False

    def run(self):
        while not self._stop:
            self.do_execute()

    def is_running(self):
        return not self._stop

    def stop(self):
        self._stop = True

    def do_execute(self):
        pass
