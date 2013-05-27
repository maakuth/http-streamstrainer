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
import time
import subprocess

WGETOPTS = "-q -O-"
WGETS = 3 #How many wgets to spawn
PIPE_CHANGE_INTERVAL = 20 #How many seconds will we test one stream
WGET = "/usr/bin/wget"

ivlc = vlc.Instance()
vlcplayer = ivlc.media_player_new()

pipe_to_test = None

def runwget(url, pipes):
	cmdline = WGET + " " + WGETOPTS + " " + url
	p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE)
	pipes.append(p.stdout)

def attachvlc(pipe):
	m = ivlc.media_new_fd(pipe.fileno())
	vlcplayer.set_media(m)
	vlcplayer.play()

def testnext(pipes):
	global pipe_to_test
	if pipe_to_test is not None:
		pipes.append(pipe_to_test)
	pipe_to_test = pipes.pop()
	attachvlc(pipe_to_test)
	
if __name__ == "__main__":
	print ("HTTP Stream strainer by Markus Vuorio, 2013\nUsing VLC version " + vlc.libvlc_get_version())
	if len(sys.argv) < 2:
		print("Use: " + sys.argv[0] + " http://your/url")
		sys.exit(1)
		
	url = sys.argv[1]
	pipes = []

	for i in range(WGETS):
		runwget(url, pipes)

	testedpipes = 0
	last_time = time.time()
	testnext(pipes)

	while (True):
		if (time.time() - last_time > PIPE_CHANGE_INTERVAL):
			testnext(pipes)
			last_time = time.time()
		
		for i in pipes:
			i.read(1000)

	raw_input("Press Enter to stop")
