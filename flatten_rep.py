#!/usr/bin/env python

import sys

if len(sys.argv) <= 3:
    print("This script will combine several tracks into one. Pass the (0-based) index of the tracks to combine, in order of priority.")
    print("Usage:", sys.argv[0], "<infile> <outfile> <track index>+", file=sys.stderr)
    sys.exit(1)

import copy
import guitarpro

def isMeasureEmpty(measure):
    for voice in measure.voices:
        for beat in voice.beats:
            if beat.notes: return False
    return True

def isMeasureEqual(m1, m2):
    if (len(m1.voices) != len(m2.voices)): return False
    for v1, v2 in zip(m1.voices, m2.voices):
        if (len(v1.beats) != len(v2.beats)): return False
        for b1, b2 in zip(v1.beats, v2.beats):
            if (len(b1.notes) != len(b2.notes)): return False
            for n1, n2 in zip(b1.notes, b2.notes):
                if n1 != n2: return False
    return True

def getRepeatCount(region, start, l):
    n = 1
    while start + (n + 1) * l <= len(region):
        for i in range(l):
            if not isMeasureEqual(region[start + i], region[start + i + n * l]):
                return n
        n = n + 1
    return n

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
regions = []
for i in range(len(tracks[0].measures)):
    measure = tracks[-1].measures[i]
    for track in tracks[:-1]:
        if not isMeasureEmpty(track.measures[i]):
            measure = track.measures[i]
            break

    # set track title when changing
    if last != measure.track.name:
        regions.append({ "start": i, "measures": []})
        last = measure.track.name
        text = guitarpro.base.BeatText()
        text.value = last
        measure.voices[0].beats[0].text = text

    regions[-1]["measures"].append(measure)

for r in regions:
    start    = r["start"]
    measures = r["measures"]
    l = len(measures)
    print("Checking for repeats in {} measure range {}:{}".format(l, start + 1, start + l))
    p = 0
    while p < l:

        rl = 0
        rc = 1

        # while it's possible to grow match
        while p + 2 * rc * rl <= l:
            s = p
            t = s + rc * rl + 1

            # skip until first measure re-occurs
            while t < l and not isMeasureEqual(measures[s], measures[t]):
                t = t + 1

            candRl = t - s
            candRc = getRepeatCount(measures, s, candRl)

            if candRc > 1:
                print("  Found {} time repeat of length {} at {}".format(candRc, candRl, start + s + 1))
                rc = candRc
                rl = candRl
                # try to grow further

            else:
                if rc == 1:
                    # nothing found, grow initial pattern
                    rl = t - s
                else:
                    break

        print("* Using {} time repeat of length {} at {}".format(rc, rl, start + p + 1))
        # mark repeat if needed
        if rc > 1:
            measures[p].header.isRepeatOpen = True
            measures[p + rl - 1].header.repeatClose = rc
        for i in range(rl):
            flattened.measures.append(measures[p + i])
        p = p + rl * rc

flattened.number = 1
song.tracks = []
song.addTrack(flattened)

print("Writing to", dst)
guitarpro.write(song, dst)
