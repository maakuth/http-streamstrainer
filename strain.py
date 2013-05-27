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

"""
strain.py
Program to load HTTP streams with VLC to see how the streaming server copes.
"""

import os
import sys
import vlc
import time
import subprocess

WGETOPTS = "-q -O-"
WGETS = 1000 #How many wgets to spawn
PIPE_CHANGE_INTERVAL = 20 #How many seconds will we test one stream
NULLREAD = 4096 #How many bytes to read to discard
WGET = "/usr/bin/wget"

#These options should disable media decoding, we are only interested in mux wellbeing
ivlc = vlc.Instance( "--no-audio", "--novideo", "--quiet") 
vlcplayer = ivlc.media_player_new()
pipe_to_test = None
allstats = {
	'total_corrupted':0,
	'decoded_delta':0,
}

def runwget(url, pipes):
	"""
	Start one wget instance and add it's stdout to global pipes list
	"""
	cmdline = WGET + " " + WGETOPTS + " " + url
	p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE)
	pipes.append(p.stdout)

def startwgets(url, pipes):
	"""
	Start a lot of wgets
	"""
	print("Starting " + str(WGETS) + " wgets")
        for i in range(WGETS):
                runwget(url, pipes)

def attachvlc(pipe):
	"""
	Attach VLC instance to a pipe fd
	"""
	print("Attaching VLC to pipe " + str(pipe))
	m = ivlc.media_new_fd(pipe.fileno())
	vlcplayer.set_media(m)
	vlcplayer.play()

def getstats():
	"""
	Gather VLC statistics
	"""
	m = vlcplayer.get_media()
	stats = vlc.MediaStats()
	m.get_stats(stats)
	return stats

def buildstats(allstats, stats, start_time):
	allstats['total_corrupted'] += stats.demux_corrupted
	runtime = time.time() - start_time
	allstats['decoded_delta'] += runtime - stats.decoded_video

def testnext(pipes):
	"""
	Move to next pipe to test
	"""
	global pipe_to_test
	if pipe_to_test is not None:
		pipes.append(pipe_to_test)
	pipe_to_test = pipes.pop(0)
	attachvlc(pipe_to_test)
	
if __name__ == "__main__":
	print("HTTP Stream strainer by Markus Vuorio, 2013")
	print("Using VLC version " + vlc.libvlc_get_version())
	if len(sys.argv) < 2:
		print("Use: " + sys.argv[0] + " http://your/url")
		sys.exit(1)
		
	url = sys.argv[1]
	pipes = []

	startwgets(url, pipes)

	testedpipes = 0
	total_corrupted = 0
	start_time = time.time()
	last_time = time.time()
	testnext(pipes)
	try:
		print("Test running, interrupt with ctrl+c")
		while (True):
			if (time.time() - last_time > PIPE_CHANGE_INTERVAL):
				buildstats(allstats, getstats(), start_time)
				testnext(pipes)
				testedpipes += 1
				last_time = time.time()
			
			for i in pipes:
				i.read(NULLREAD)

	except KeyboardInterrupt:
			run_time = time.time() - start_time
			print ("Test run for {0:.3g} seconds, got total of {1} demux corruptions. Tested {2} pipes.".format(run_time, allstats['total_corrupted'], testedpipes))
