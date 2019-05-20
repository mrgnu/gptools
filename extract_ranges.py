#!/usr/bin/env python3

import sys
import copy
import guitarpro
from utils import extract_measures, dump_tracks, dump_markers, get_marker_range

# M:<marker>:<track> or R:<first measure>:<last measure>:<track>
def next_range(song:       guitarpro.models.Song,
               range_spec: [str]) -> [int]:  # [<track>, <first measure>, <last measure>]
    parts = range_spec.split(":")
    track = int(parts[-1]) - 1
    r     = [track]
    if (parts[0] == "M"):
        return r + get_marker_range(song, parts[1])
    elif (parts[0] == "R"):
        r.append(int(parts[1]) - 1)
        r.append(int(parts[2]) - 1)
        return r

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print("This script will extract ranges of measures from a song."
              "Pass (1-based) range specs:\n"
              "  M:<marker title>:<track index>\n"
              "  R:<first measure>:<last measure>:<track index>\n")
        print("Usage: {} <infile> <outfile> <<track index> <first measure> <last measure>>+"
              .format(sys.argv[0]), file=sys.stderr)

        if len(sys.argv) >= 2:
            song = guitarpro.parse(sys.argv[1])
            dump_tracks(song)
            dump_markers(song)

        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    print("Parsing", src)
    song = guitarpro.parse(src)

    ranges = list(map(lambda range_spec: next_range(song, range_spec), sys.argv[3:]))

    print("Extracting {} ranges from {}".format(len(ranges), song.title))

    measures = []

    # Collect measure ranges
    for range_spec in ranges:
        track_idx     = range_spec[0]
        start_measure = range_spec[1]
        end_measure   = range_spec[2]

        measures = measures + extract_measures(song, track_idx, start_measure, end_measure)

    track = copy.deepcopy(song.tracks[0])
    track.name = song.title
    track.measures = measures

    song.tracks = [track]

    print("Writing to", dst)
    guitarpro.write(song, dst)
