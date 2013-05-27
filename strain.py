#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import vlc
import subprocess

WGETOPTS = "-q -O-"
WGETS = 100
WGET = "/usr/bin/wget"

pipes = []
ivlc = vlc.Instance()

def runwget(url, pipelist):
	cmdline = WGET + " " + WGETOPTS + " " + url
	p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE)
	pipelist.append(p.stdout)

def attachvlc(pipe):
	p = ivlc.media_player_new()
	m = ivlc.media_new_fd(pipe.fileno())
	p.set_media(m)
	p.play()
	
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Use: " + sys.argv[0] + " http://your/url")
		sys.exit(1)
		
	url = sys.argv[1]

	for i in range(WGETS):
		runwget(url, pipes)

	attachvlc(pipes.pop())

	while (True):
		for i in pipes:
			i.read(1000)

	raw_input("Press Enter to stop")
