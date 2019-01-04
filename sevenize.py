#!/usr/bin/env python
import sys
import guitarpro

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("This script will add a D5 string as new first string for all "
              "6-string tracks.")
        print("Usage:", sys.argv[0], "<infile> <outfile>", file=sys.stderr)
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    print("Parsing", src)
    song = guitarpro.parse(src)

    print("Processing", song.title)

    for track in song.tracks:
        if track.isPercussionTrack: continue
        if len(track.strings) != 6: continue

        print("* Adding D5 string to", track.name)

        # modify index of existing strings
        for string in track.strings:
            string.number = string.number + 1

        # create and add D5 string
        d5 = guitarpro.base.GuitarString(1, 62)
        track.strings.insert(0, d5)

        # move all notes down one string
        for measure in track.measures:
            for voice in measure.voices:
                for beat in voice.beats:
                    for note in beat.notes:
                        note.string = note.string + 1

    print("Writing to", dst)
    guitarpro.write(song, dst)
