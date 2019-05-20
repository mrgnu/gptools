#!/usr/bin/env python3

import sys
import copy
import guitarpro
from utils import dump_tracks, dump_markers

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("This script will dump track info.")
        print("Usage: {} <gp5-file>"
              .format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    src = sys.argv[1]

    print("Parsing}", src)
    song = guitarpro.parse(src)

    dump_tracks(song)
    dump_markers(song)
