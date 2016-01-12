#!/usr/bin/env python
import sys

if len(sys.argv) != 3:
    print("This script will re-tune 3rd string from E4 to F4 on 7-string tracks as " \
          "needed. Notes on empty 3rd string will be marked as fretted on 35th fret.")
    print("Usage:", sys.argv[0], "<infile> <outfile>", file=sys.stderr)
    sys.exit(1)

import guitarpro

src = sys.argv[1]
dst = sys.argv[2]

print ("Parsing", src)
song = guitarpro.parse(src)

print("Processing", song.title)

for track in song.tracks:
    if track.isPercussionTrack: continue
    if len(track.strings) != 7 or track.strings[2].value != 52: continue

    # re-tune 3rd string from E4 to F4
    print("* Re-tuning string 3 of track", track.name)
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
