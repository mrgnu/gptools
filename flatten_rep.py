#!/usr/bin/env python

import sys
import copy
import guitarpro

if len(sys.argv) <= 3:
    print("This script will combine several tracks into one, "
          "after which an attempt to detect and collapse repeats is made. "
          "Pass the (0-based) index of the tracks to combine, "
          "in order of priority.")
    print("Usage: {} <infile> <outfile> <track index>+".format(sys.argv[0]),
          file=sys.stderr)

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


def areBeatsEqual(b1, b2):
    for f in ["octave", "notes", "effect", "duration", "status"]:
        if not b1.__dict__[f] == b2.__dict__[f]: return False
    return True


def areMeasuresEqual(m1, m2):
    if (len(m1.voices) != len(m2.voices)): return False
    for v1, v2 in zip(m1.voices, m2.voices):
        if (len(v1.beats) != len(v2.beats)): return False
        for b1, b2 in zip(v1.beats, v2.beats):
            if not areBeatsEqual(b1, b2): return False
    return True


def getRepeatCount(region, start, l):
    n = 1
    while start + (n + 1) * l <= len(region):
        for i in range(l):
            if not areMeasuresEqual(region[start + i],
                                    region[start + i + n * l]):
                return n
        n = n + 1
    return n

src = sys.argv[1]
dst = sys.argv[2]

print("Parsing", src)
song = guitarpro.parse(src)

print("Processing", song.title)

tracks = []

for i in sys.argv[3:]:
    tracks.append(song.tracks[int(i)])

flattened = copy.deepcopy(tracks[0])
flattened.measures = []
flattened.name = "Flattened"

# merge tracks, consecutive measures from same track are considered a region
last = None
regions = []
for i in range(len(tracks[0].measures)):
    measure = tracks[-1].measures[i]
    for track in tracks[:-1]:
        if not isMeasureEmpty(track.measures[i]):
            measure = track.measures[i]
            break

    # set track title when changing
    if last != measure.track:
        regions.append({"start": i, "measures": []})
        last = measure.track
        text = guitarpro.base.BeatText()
        text.value = last.name
        measure.voices[0].beats[0].text = text

    regions[-1]["measures"].append(measure)

# attempt to detect and collapse repeats within regions
for r in regions:
    start    = r["start"]
    measures = r["measures"]
    l = len(measures)
    print("Checking for repeats in {} measure range {}:{}".format(
        l, start + 1, start + l))
    s = 0
    while s < l:

        rl = 1
        rc = 1

        e = s + 1

        # while it's possible to find a repeat
        while s + 2 * (e - s) <= l:

            # skip until first measure re-occurs
            while e < l and not areMeasuresEqual(measures[s], measures[e]):
                e = e + 1

            candRl = e - s
            candRc = getRepeatCount(measures, s, candRl)

            if candRc > 1:
                print("  Found {} time repeat of length {} at {}".format(
                    candRc, candRl, start + s + 1))
                rl = candRl
                rc = candRc
                e = s + rl * rc + 1
                # try to grow further

            else:
                # nothing found, grow initial pattern
                e = e + 1
                if e >= l: break

        print("* Using {} time repeat of length {} at {}".format(
            rc, rl, start + s + 1))
        # mark repeat if needed
        if rc > 1:
            measures[s].header.isRepeatOpen = True
            measures[s + rl - 1].header.repeatClose = rc
        for i in range(rl):
            flattened.measures.append(measures[s + i])
        s = s + rl * rc

flattened.number = 1
song.tracks = []
song.addTrack(flattened)

print("Writing to", dst)
guitarpro.write(song, dst)
