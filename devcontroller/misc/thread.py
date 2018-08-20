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

from math import ceil

import threading
import time
import sys

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

class CountdownThread(StoppableThread):

    def __init__(self):
        super(CountdownThread, self).__init__()
        self.t = 0

    def set_time(self, time):
        self.t = time

    def do_execute(self):
        #print("waiting %s seconds:" % self.t)
        self.t = int(ceil(self.t))
        while self.t and not self._stop:
            mins, secs = divmod(self.t, 60)
            sys.stdout.write('\rremaining ' + '{:02d}:{:02d}'.format(mins, secs))
            sys.stdout.flush()
            time.sleep(1)
            self.t -= 1
        print("\rdone.                  \n")
        self.stop()

def countdown(time):
    thread = CountdownThread()
    thread.set_time(time)
    thread.daemon = True
    thread.start()