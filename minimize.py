#!/usr/bin/env python

import sys
import copy
import guitarpro
import utils

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print("This script will combine several tracks into one, "
              "after which an attempt to detect and collapse repeats is made. "
              "Pass the (0-based) index of the tracks to combine, "
              "in order of priority.")
        print("Usage: {} <infile> <outfile> <track index>+".
              format(sys.argv[0]), file=sys.stderr)

        if len(sys.argv) >= 2:
            song = guitarpro.parse(sys.argv[1])
            for idx, track in enumerate(song.tracks):
                print("* track {}: {}".format(idx, track.name))

        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    print("Parsing", src)
    song = guitarpro.parse(src)

    print("Processing", song.title)

    indices = []
    for s in sys.argv[3:]: indices.append(int(s))

    # collect regions
    regions = utils.flatten_to_regions(song, indices)

    # create new track
    flattened = copy.deepcopy(song.tracks[indices[0]])
    flattened.number = 1
    flattened.name = "Flattened"
    flattened.measures = []

    # fold repeats and add to track
    for r in regions: flattened.measures.extend(utils.fold_repeats(r))

    song.tracks = [flattened]

    print("Writing to", dst)
    guitarpro.write(song, dst)
