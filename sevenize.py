#!/usr/bin/env python
import sys

if len(sys.argv) != 3:
    print("This script will add a D5 string as new first string for all 6-string tracks.")
    print("Usage:", sys.argv[0], "<infile> <outfile>", file=sys.stderr)
    sys.exit(1)

import guitarpro

src = sys.argv[1]
dst = sys.argv[2]

print ("Parsing", src)
song = guitarpro.parse(src)

print("Processing", song.title)

# iterate over tracks, adding D5 string as new first string for all
# 6-string tracks
for track in song.tracks:
    if len(track.strings) != 6 or track.isPercussionTrack:
        continue

    print("* Adding D5 string to", track.name)

    # create D5 string
    d5 = guitarpro.base.GuitarString(1, 62)
    # modify index of existing string
    for string in track.strings:
        string.number = string.number + 1
    # add
    track.strings.insert(0, d5)

    # move all notes down one string
    for measure in track.measures:
        for voice in measure.voices:
            for beat in voice.beats:
                for note in beat.notes:
                    note.string = note.string + 1

    # re-tune 3rd string from E4 to F4 if needed
    if track.strings[2].value != 52:
        print("  WARNING: not retuning string 3, tuned to",
              str(track.strings[2].value))
        continue

    track.strings[2].value = track.strings[2].value + 1

    for measure in track.measures:
        for voice in measure.voices:
            for beat in voice.beats:
                for note in beat.notes:
                    if note.string != 3:
                        continue
                    if note.value == 0:
                        print("  WARNING: failed to re-tune note in measure", measure.number)
                        note.value = 35
                    else:
                        note.value = note.value - 1

print("Writing to", dst)
guitarpro.write(song, dst)
