#!/usr/bin/env python

import sys
import copy
import guitarpro

if len(sys.argv) <= 3:
    print("This script will combine several tracks into one. " \
          "Pass the (0-based) index of the tracks to combine, " \
          "in order of priority.")
    print("Usage:", sys.argv[0], "<infile> <outfile> <track index>+", file=sys.stderr)

    if len(sys.argv) >= 2:
        song = guitarpro.parse(sys.argv[1])
        for idx, track in enumerate(song.tracks):
            print("* track {}: {}".format(idx, track.name))

    sys.exit(1)

def isMeasureEmpty(measure):
    for voice in measure.voices:
        for beat in voice.beats:
            if beat.notes: return False
    return True

src = sys.argv[1]
dst = sys.argv[2]

print ("Parsing", src)
song = guitarpro.parse(src)

print("Processing", song.title)

tracks = []

for i in sys.argv[3:]:
    tracks.append(song.tracks[int(i)])

flattened = copy.deepcopy(tracks[0])
flattened.measures = []
flattened.name = "Flattened"

last = None
for i in range(len(tracks[0].measures)):
    measure = tracks[-1].measures[i]
    for track in tracks[:-1]:
        if not isMeasureEmpty(track.measures[i]):
            measure = track.measures[i]
            break

    # set track title when changing
    if last != measure.track:
        last = measure.track
        text = guitarpro.base.BeatText()
        text.value = last.name
        measure.voices[0].beats[0].text = text

    flattened.measures.append(measure)
    
flattened.number = 1
song.tracks = []
song.addTrack(flattened)

print("Writing to", dst)
guitarpro.write(song, dst)
