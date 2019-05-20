import guitarpro


class Region:
    """Container for a sequence of consecutive measures from the same
    track.
    """
    def __init__(self, start_index: int):
        self.start_index = start_index
        self.measures = []

    def add_measure(self, measure: guitarpro.models.Measure):
        self.measures.append(measure)


def dump_tracks(song: guitarpro.models.Song) -> None:
    tracks = song.tracks
    print("{} tracks".format(len(tracks)))
    for idx, track in enumerate(tracks):
        print("* track {}: {}".format(idx + 1, track.name))


def dump_markers(song: guitarpro.models.Song) -> None:
    measureHeaders = song.measureHeaders
    print("markers:")
    for header in measureHeaders:
        if (not header.marker): continue
        print("* {}: {}".format(header.number, header.marker.title))


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


def add_beat_comment(track:      guitarpro.models.Track,
                     measureIdx: int,
                     comment:    str) -> None:
    text = guitarpro.models.BeatText()
    text.value = comment
    track.measures[measure].voices[0].beats[0].text = text


def add_marker_comment(track:      guitarpro.models.Track,
                       measureIdx: int,
                       comment:    str) -> None:
    """Adds a new marker at 'measure' (0-based) with title 'comment'.
    If a marker already exists, appends 'comment'.
    """
    measure = track.measures[measureIdx]
    header  = measure.header
    marker  = header.marker
    if (marker):
        marker.title = "{} - {}".format(marker.title, comment)
    else:
        marker = guitarpro.models.Marker(comment)
        header.marker = marker
    track.song.measureHeaders[measureIdx] = header


def extract_measures(song: guitarpro.models.Song,
                     trackIdx:        int,
                     firstMeasureIdx: int,
                     lastMeasureIdx:  int) -> [guitarpro.models.Measure]:
    "Extract measures (0-based, inclusive) from track (0-based), with folding."

    track = song.tracks[trackIdx]

    print("Extracting measures [{}:{}] from track {}"
          .format(firstMeasureIdx + 1,
                  lastMeasureIdx  + 1,
                  track.name))

    # add a comment with start measure and track name
    add_marker_comment(track,
                       firstMeasureIdx,
                       "M:{} {}".format(firstMeasureIdx + 1, track.name))

    # fold repeats
    region = Region(0)
    region.measures = track.measures[firstMeasureIdx:lastMeasureIdx + 1]
    measures = fold_repeats(region)

    return measures


def flatten_to_regions(song: guitarpro.models.Song,
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

        # create new region
        if last != measure.track:
            regions.append(Region(i))
            last = measure.track
            # set track title when changing
            add_beat_comment(last, i, last.name)

        regions[-1].add_measure(measure)

    return regions


def fold_repeats(r: Region) -> [guitarpro.models.Measure]:
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
