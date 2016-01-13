import guitarpro


class Region:
    """Container for a sequence of consecutive measures from the same
    track.
    """
    def __init__(self, start_index: int):
        self.start_index = start_index
        self.measures = []

    def add_measure(self, measure: guitarpro.base.Measure):
        self.measures.append(measure)


def is_measure_empty(measure):
    for voice in measure.voices:
        for beat in voice.beats:
            if beat.notes: return False
    return True


def are_beats_equal(b1, b2):
    for f in ["octave", "notes", "effect", "duration", "status"]:
        if not b1.__dict__[f] == b2.__dict__[f]: return False
    return True


def are_measures_equal(m1, m2):
    if (len(m1.voices) != len(m2.voices)): return False
    for v1, v2 in zip(m1.voices, m2.voices):
        if (len(v1.beats) != len(v2.beats)): return False
        for b1, b2 in zip(v1.beats, v2.beats):
            if not are_beats_equal(b1, b2): return False
    return True


def get_repeat_count(region: Region, start: int, l: int) -> int:
    """Returns number of times the 'l' measures in 'region', starting at
    index 'start', occur in sequence. Returned value is >= 1.
    """
    n = 1
    while start + (n + 1) * l <= len(region.measures):
        for i in range(l):
            if not are_measures_equal(region.measures[start + i],
                                      region.measures[start + i + n * l]):
                return n
        n = n + 1
    return n


def flatten_to_regions(song: guitarpro.base.Song,
                       indices: [int]) -> [Region]:
    """Iterates over song, flattening tracks in order of priority. Returns
    a list of regions.
    """
    # collect relevant tracks
    tracks = []
    for i in indices:
        tracks.append(song.tracks[i])

    for t in tracks[1:]:
        if len(tracks[0].measures) != len(t.measures):
            raise Exception(
                "track {} has wrong number of measures".format(t.name))
        if len(tracks[0].strings) != len(t.strings):
            raise Exception(
                "track {} has wrong number of strings".format(t.name))

    # merge into regions
    last = None
    regions = []
    for i in range(len(tracks[0].measures)):
        # find measure in order of priority
        measure = tracks[-1].measures[i]
        for track in tracks[:-1]:
            if not is_measure_empty(track.measures[i]):
                measure = track.measures[i]
                break

        # set track title when changing
        if last != measure.track:
            regions.append(Region(i))
            last = measure.track
            text = guitarpro.base.BeatText()
            text.value = last.name
            measure.voices[0].beats[0].text = text

        regions[-1].add_measure(measure)

    return regions


def fold_repeats(r: Region) -> [guitarpro.base.Measure]:
    out = []

    l = len(r.measures)
    print("Checking for repeats in {} measure range {}:{}".format(
        l, r.start_index + 1, r.start_index + l))
    s = 0
    while s < l:

        rl = 1
        rc = 1

        e = s + 1

        # while it's possible to find a repeat
        while s + 2 * (e - s) <= l:

            # skip until first measure re-occurs
            while e < l and not are_measures_equal(
                    r.measures[s], r.measures[e]):
                e = e + 1

            candRl = e - s
            candRc = get_repeat_count(r, s, candRl)

            if candRc > 1:
                print("  Found {} time repeat of length {} at {}".format(
                    candRc, candRl, r.start_index + s + 1))
                rl = candRl
                rc = candRc
                e = s + rl * rc + 1
                # try to grow further

            else:
                # nothing found, grow initial pattern
                e = e + 1
                if e >= l: break

        print("* Using {} time repeat of length {} at {}".format(
            rc, rl, r.start_index + s + 1))
        # mark repeat if needed
        if rc > 1:
            r.measures[s].header.isRepeatOpen = True
            r.measures[s + rl - 1].header.repeatClose = rc
        out.extend(r.measures[s:s + rl])
        s = s + rl * rc
    return out