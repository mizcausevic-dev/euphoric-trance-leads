"""Original euphoric trance leads.

Container lengths and tempos are fixed before any note is written.
Study 01 is 16 bars at 138 BPM so the primary preview is 16 * 4 * 60 / 138
seconds, about 27.826. The other containers are 16 or 8 bars at an integer
tempo from 132 to 140. Nothing is random. The lead is monophonic. The
harmonic reference and the counterphrase are cataloged as reference parts
and are not part of the core count.

Phrase arcs, rests, and transformed returns carry the themes. Scale runs,
supersaw stacking, and delay are not used as a substitute for the line.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "euphoric-trance-leads"
PACK_NAME = "Euphoric Trance Leads"
BAR = BAR_TICKS_4_4


class Part:
    def __init__(self, study, part_id, role, variation, core, channel, slug, mono, poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = core
        self.channel = channel
        self.file_slug = slug
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration} pitch {pitch}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        if not 1 <= velocity <= 127:
            raise ValueError(f"{self.part_id} velocity {velocity}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{start} with {other['pitch']}@{o0}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": start, "offset": 0, "performed_start": start,
            "duration": duration, "pitch": pitch, "velocity": velocity,
            "channel": self.channel, "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda n: (n["performed_start"], n["pitch"]))
        if self.core and len(ordered) < 8:
            raise ValueError(f"{self.part_id} too few notes")
        if not ordered:
            raise ValueError(f"{self.part_id} empty")
        for index, note in enumerate(ordered, 1):
            note["id"] = f"{self.part_id}.n{index:04d}"
        return {
            "id": self.part_id, "study_id": self.study["id"], "slug": self.study["slug"],
            "role": self.role, "variation": self.variation, "core": self.core,
            "channel": self.channel, "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": self.monophonic, "max_poly": self.max_poly,
            "container_ticks": self.container_ticks, "container_bars": self.study["bars"],
            "bpm": self.study["bpm"], "tempo_us": self.study["tempo_us"], "notes": ordered,
        }


def lead(study, variation):
    return Part(
        study, f"{study['id']}.lead.{variation}", "principal-lead", variation,
        True, 0, f"lead-{variation}", True, 1, 60, 84,
    )


def harmony(study, variation):
    return Part(
        study, f"{study['id']}.harmony.{variation}", "harmonic-reference", variation,
        False, 1, f"harmony-{variation}", False, 4, 48, 76,
    )


def counter(study, variation):
    return Part(
        study, f"{study['id']}.counter.{variation}", "counterphrase", variation,
        False, 2, f"counter-{variation}", True, 1, 55, 81,
    )


def lay(part, rows):
    for row in rows:
        bar, start, dur, pitch, vel = row[:5]
        departure = bool(row[5]) if len(row) > 5 else False
        part.add(bar * BAR + start, dur, pitch, vel, departure=departure)


def chords(part, rows):
    for bar, start, dur, pitches, vel in rows:
        for pitch in pitches:
            part.add(bar * BAR + start, dur, pitch, vel)


def studies():
    common = {"meter": "4/4", "bar_ticks": BAR, "ppq": PPQ, "stochastic_draws": 0}
    rows = [
        {**common, "id": "s01", "slug": "s01-lifted-fifth", "title": "Lifted Fifth",
         "bpm": 138, "bars": 16, "tonic": "A", "tonal_reference": "A",
         "collection_name": "A natural minor", "pitch_classes": [9, 11, 0, 2, 4, 5, 7],
         "departures": [], "seed": 13801,
         "harmonic_rhythm": "Am for three bars, a rest, F, C, a rest, Am, a rest, F, Em, a rest.",
         "changes": ["Am", "rest", "F", "C", "rest", "Am", "rest", "F", "Em", "rest"],
         "change_bars": [3, 1, 2, 1, 1, 2, 1, 3, 1, 1],
         "phrases": [
             {"name": "Theme", "start_bar": 0, "bars": 4},
             {"name": "Answer", "start_bar": 4, "bars": 4},
             {"name": "Rise", "start_bar": 8, "bars": 4},
             {"name": "Return", "start_bar": 12, "bars": 4},
         ],
         "identity": "The lead waits an eighth, states E then C then A, answers from a lower E, climbs an Am7 arpeggio, and returns to the fifth on the downbeat. Variation B starts on the downbeat with C and reaches C6 before a late return.",
         "limitations": "Pair lead A with harmony A and counterphrase A. Variation B is an alternate lead, not a second layer. Harmony and counterphrase are reference files and are not in the core count.",
         "voicing": "Lead is one note at a time from E4 to C6. Harmony is a separate triad in a lower register. Counterphrase answers in the gaps.",
         "layering": "Three files. The arrangement already contains study 01 variation A. Do not stack the part files on it.",
         "accent": "Velocity sits near 84 in the theme, 96 in the answer, 112 on the rise, and 92 on the return."},
        {**common, "id": "s02", "slug": "s02-open-fourth", "title": "Open Fourth",
         "bpm": 136, "bars": 16, "tonic": "D", "tonal_reference": "D",
         "collection_name": "D dorian", "pitch_classes": [2, 4, 5, 7, 9, 11, 0],
         "departures": [], "seed": 13602,
         "harmonic_rhythm": "Dm, G, F, then Dm again, each for four bars except a final rest.",
         "changes": ["Dm", "G", "F", "Dm", "rest"],
         "change_bars": [4, 4, 4, 3, 1],
         "phrases": [
             {"name": "Fourth", "start_bar": 0, "bars": 4},
             {"name": "Fall", "start_bar": 4, "bars": 4},
             {"name": "Lift", "start_bar": 8, "bars": 4},
             {"name": "Return", "start_bar": 12, "bars": 4},
         ],
         "identity": "A rising fourth opens the phrase, then a rest, then a lower answer. The return flips the fourth so G falls to D. Variation B starts on A and moves the fourth onto the downbeat.",
         "limitations": "Pair each lead variation with the harmony and counterphrase of the same letter. The counterphrase is reference only.",
         "voicing": "Lead stays monophonic between D4 and A5. Harmony holds triads in a lower register and does not double the fourth figure.",
         "layering": "The fourth is the foreground. Harmony is a slow reference. They are separate files.",
         "accent": "The opening fourth is quieter than the lifted A5. The final D5 is the weight of the phrase, not the loudest note."},
        {**common, "id": "s03", "slug": "s03-held-third", "title": "Held Third",
         "bpm": 140, "bars": 8, "tonic": "F", "tonal_reference": "F",
         "collection_name": "F major", "pitch_classes": [5, 7, 9, 10, 0, 2, 4],
         "departures": [], "seed": 14003,
         "harmonic_rhythm": "F, Bb, C, F, two bars each.",
         "changes": ["F", "Bb", "C", "F"],
         "change_bars": [2, 2, 2, 2],
         "phrases": [
             {"name": "Hold", "start_bar": 0, "bars": 4},
             {"name": "Return", "start_bar": 4, "bars": 4},
         ],
         "identity": "Long tones carry the major third as the color, with air between the hold and the cadence. Variation B begins on that third and cuts the holds shorter.",
         "limitations": "Eight bars, not sixteen. The third is a written pitch, not a synth interval. Pair matching variation letters.",
         "voicing": "Lead notes are long and monophonic from Bb4 to A5. Harmony changes on the two-bar groups underneath.",
         "layering": "Do not fill the rests with delay. The silence is part of the phrase.",
         "accent": "The held F5 is moderate. The A5 third is the louder color. The cadence settles."},
        {**common, "id": "s04", "slug": "s04-broken-arc", "title": "Broken Arc",
         "bpm": 134, "bars": 16, "tonic": "E", "tonal_reference": "E",
         "collection_name": "E natural minor", "pitch_classes": [4, 6, 7, 9, 11, 0, 2],
         "departures": [], "seed": 13404,
         "harmonic_rhythm": "Em, C, a bar of rest, Am, Em, a bar of rest.",
         "changes": ["Em", "C", "rest", "Am", "Em", "rest"],
         "change_bars": [4, 4, 1, 3, 3, 1],
         "phrases": [
             {"name": "Climb", "start_bar": 0, "bars": 4},
             {"name": "Fall", "start_bar": 4, "bars": 4},
             {"name": "Break", "start_bar": 8, "bars": 4},
             {"name": "Return", "start_bar": 12, "bars": 4},
         ],
         "identity": "The line climbs by thirds, falls, leaves a bar empty, and returns with the opening third compressed and higher. Variation B starts on B5 and takes its rest earlier.",
         "limitations": "The empty bar is intentional. It is not a missing file. Thirds are not a scale run.",
         "voicing": "Lead is monophonic from E4 to B5. Harmony drops out with the break.",
         "layering": "Counterphrase speaks in the empty bar. It is still a reference part.",
         "accent": "The top B5 is the peak. The return is softer than the climb."},
        {**common, "id": "s05", "slug": "s05-late-call", "title": "Late Call",
         "bpm": 132, "bars": 16, "tonic": "B", "tonal_reference": "B",
         "collection_name": "B natural minor", "pitch_classes": [11, 1, 2, 4, 6, 7, 9],
         "departures": [], "seed": 13205,
         "harmonic_rhythm": "Bm, G, A, a rest, Bm, a rest.",
         "changes": ["Bm", "G", "A", "rest", "Bm", "rest"],
         "change_bars": [4, 4, 3, 1, 3, 1],
         "phrases": [
             {"name": "Late call", "start_bar": 0, "bars": 4},
             {"name": "Answer", "start_bar": 4, "bars": 4},
             {"name": "Peak", "start_bar": 8, "bars": 4},
             {"name": "Downbeat return", "start_bar": 12, "bars": 4},
         ],
         "identity": "The call sits on beat 3 until the return, which moves the B-D-F# shape onto the downbeat and up to B5. Variation B opens on the downbeat with a sixth and saves the late call for the return.",
         "limitations": "Beat 3 is the identity of variation A. Do not quantize it back to the downbeat. Pair matching letters.",
         "voicing": "Lead is monophonic from F#4 to B5. Harmony is a slow reference and does not state the call.",
         "layering": "The late entry is the foreground. Harmony may already be sounding. That is support, not a second lead.",
         "accent": "The beat-3 call is moderate. B5 at the peak is stronger. The final B4 settles."},
        {**common, "id": "s06", "slug": "s06-neighbor-turn", "title": "Neighbor Turn",
         "bpm": 137, "bars": 8, "tonic": "G", "tonal_reference": "G",
         "collection_name": "G natural minor", "pitch_classes": [7, 9, 10, 0, 2, 3, 5],
         "departures": ["Variation A bar 7 uses F#5 (78) for one note into G5. It is flagged. No other note leaves G natural minor."],
         "seed": 13706,
         "harmonic_rhythm": "Gm, Eb, a rest, Gm.",
         "changes": ["Gm", "Eb", "rest", "Gm"],
         "change_bars": [3, 2, 1, 2],
         "phrases": [
             {"name": "Neighbor", "start_bar": 0, "bars": 4},
             {"name": "Turn", "start_bar": 4, "bars": 4},
         ],
         "identity": "A neighbor turn around G, a rest, then one flagged F#5 into G5. Variation B turns downward to F and stays inside the collection, with a different rhythm.",
         "limitations": "The F# is one flagged departure in variation A only. Do not treat it as part of the collection. Eight bars.",
         "voicing": "Lead is monophonic. The neighbor is a short upper or lower tone, not a scale. Harmony stays inside the collection, including under the F#.",
         "layering": "The chromatic note is only in the lead file for variation A. Counterphrase does not copy it.",
         "accent": "The neighbor is lighter than the G it decorates. The F# is firm, and the G after it is the arrival."},
        {**common, "id": "s07", "slug": "s07-wide-leap", "title": "Wide Leap",
         "bpm": 135, "bars": 16, "tonic": "C", "tonal_reference": "C",
         "collection_name": "C major without B", "pitch_classes": [0, 2, 4, 5, 7, 9],
         "departures": [], "seed": 13507,
         "harmonic_rhythm": "C, F, Am, a rest, C, a rest. No B is written.",
         "changes": ["C", "F", "Am", "rest", "C", "rest"],
         "change_bars": [4, 4, 3, 1, 3, 1],
         "phrases": [
             {"name": "Leap", "start_bar": 0, "bars": 4},
             {"name": "Answer", "start_bar": 4, "bars": 4},
             {"name": "Breath", "start_bar": 8, "bars": 4},
             {"name": "Inverted return", "start_bar": 12, "bars": 4},
         ],
         "identity": "A leap from C4 to A5, a rest, and a two-note answer. The return leaps downward. Variation B leaps from C5 down to E4 and brings C6 in after a rest.",
         "limitations": "B is outside the collection and is not used. The leap is the motif. Do not fill it with passing tones.",
         "voicing": "Lead is monophonic from C4 to C6. Harmony uses C, F, and Am only.",
         "layering": "Wide space in the lead is not a cue for a scale. The counterphrase is a short reference in the gaps.",
         "accent": "The leap's top note is stronger than the takeoff. The final C4 is quiet."},
        {**common, "id": "s08", "slug": "s08-soft-return", "title": "Soft Return",
         "bpm": 139, "bars": 8, "tonic": "F#", "tonal_reference": "F#",
         "collection_name": "F# natural minor", "pitch_classes": [6, 8, 9, 11, 1, 2, 4],
         "departures": [], "seed": 13908,
         "harmonic_rhythm": "F#m, D, a rest, F#m.",
         "changes": ["F#m", "D", "rest", "F#m"],
         "change_bars": [3, 2, 1, 2],
         "phrases": [
             {"name": "Soft call", "start_bar": 0, "bars": 4},
             {"name": "Return", "start_bar": 4, "bars": 4},
         ],
         "identity": "A soft call on beat 2, a peak on B5, a bar of rest, and a return an octave lower. Variation B starts low on the downbeat and saves the high B for late in the phrase.",
         "limitations": "Eight bars. The octave return is written out. It is not a transpose of the whole file. Pair matching letters.",
         "voicing": "Lead is monophonic from F#4 to B5. Harmony is F#m then D, and it rests before the return.",
         "layering": "The lower return is the same role, not a new part. Counterphrase stays a reference.",
         "accent": "The opening is the quietest lead in the pack. B5 is the only strong peak. The low return is gentle."},
    ]
    for study in rows:
        study["tempo_us"] = bpm_to_us(study["bpm"])
        study["effective_bpm"] = effective_bpm(study["tempo_us"])
        if sum(study["change_bars"]) != study["bars"]:
            raise ValueError(f"{study['id']} change bars")
    return rows


def _s01(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 480, 960, 76, 84), (0, 1920, 480, 72, 80), (0, 2880, 720, 69, 86),
        (1, 480, 1440, 67, 82), (1, 2400, 960, 69, 88),
        (2, 0, 480, 72, 90), (2, 960, 1440, 76, 94), (2, 2880, 480, 74, 88),
        (3, 1920, 1440, 69, 86),
        (4, 1440, 960, 64, 90), (4, 2880, 720, 67, 92),
        (5, 480, 480, 69, 94), (5, 1440, 1920, 72, 98),
        (6, 1920, 960, 74, 96), (6, 3360, 480, 72, 90),
        (7, 960, 1920, 69, 92),
        (8, 0, 480, 69, 100), (8, 720, 480, 72, 104), (8, 1440, 480, 76, 110), (8, 2400, 960, 79, 114),
        (9, 480, 1440, 81, 116), (9, 2400, 960, 79, 108),
        (10, 1920, 1440, 76, 104),
        (11, 0, 960, 74, 100), (11, 1440, 1920, 72, 96),
        (12, 0, 720, 76, 98), (12, 960, 480, 72, 94), (12, 1920, 1440, 81, 102),
        (13, 480, 960, 79, 96), (13, 1920, 1440, 76, 92),
        (14, 960, 480, 74, 90), (14, 1920, 1440, 72, 88),
        (15, 480, 2880, 69, 84),
    ])
    lay(b, [
        (0, 0, 1440, 72, 86), (0, 1920, 960, 69, 84), (0, 3360, 480, 67, 80),
        (1, 0, 960, 64, 82), (1, 1440, 1920, 69, 90),
        (2, 480, 480, 72, 92), (2, 1440, 1440, 76, 96),
        (3, 0, 720, 74, 94), (3, 1440, 1440, 72, 90),
        (4, 960, 1920, 81, 108),
        (5, 0, 480, 79, 104), (5, 960, 960, 76, 100), (5, 2400, 960, 72, 96),
        (6, 1440, 1920, 69, 92),
        (7, 480, 480, 67, 88), (7, 1440, 1440, 69, 90),
        (8, 240, 720, 76, 102), (8, 1440, 480, 79, 108), (8, 2400, 960, 81, 112),
        (9, 0, 1920, 84, 116), (9, 2400, 960, 81, 104),
        (10, 960, 1440, 79, 100),
        (11, 480, 960, 76, 96), (11, 1920, 1440, 74, 92),
        (12, 1440, 960, 76, 98), (12, 2880, 720, 72, 90),
        (13, 0, 1440, 69, 88), (13, 1920, 1440, 67, 84),
        (14, 480, 960, 64, 82), (14, 1920, 1440, 69, 86),
        (15, 0, 2880, 72, 90),
    ])
    chords(ha, [
        (0, 0, 3 * BAR, (57, 60, 64), 68),
        (4, 0, 2 * BAR, (53, 57, 60), 70),
        (6, 0, BAR, (48, 52, 55), 72),
        (8, 0, 2 * BAR, (60, 64, 69), 76),
        (11, 0, 3 * BAR, (53, 60, 65), 74),
        (14, 0, BAR, (52, 55, 59), 70),
    ])
    chords(hb, [
        (0, 480, 1440, (60, 64, 69), 78),
        (2, 0, 1920, (53, 60, 65), 74),
        (4, 960, 1920, (48, 55, 64), 76),
        (6, 480, 1440, (55, 59, 62), 72),
        (8, 0, 2880, (57, 64, 72), 80),
        (11, 480, 1920, (53, 57, 65), 74),
        (13, 0, 1440, (52, 59, 64), 72),
        (14, 1920, 1440, (57, 60, 64), 70),
    ])
    lay(ca, [
        (3, 0, 960, 64, 74), (3, 1440, 960, 60, 70),
        (4, 0, 960, 60, 72),
        (6, 0, 1440, 67, 76),
        (7, 0, 720, 65, 74), (7, 1440, 960, 64, 72),
        (10, 0, 960, 72, 80), (10, 1440, 960, 69, 76),
        (15, 0, 480, 67, 70),
    ])
    lay(cb, [
        (1, 2880, 480, 72, 74),
        (2, 2880, 720, 69, 72),
        (4, 0, 720, 67, 76),
        (5, 2880, 720, 64, 74),
        (7, 0, 480, 60, 70),
        (9, 1920, 960, 76, 82),
        (11, 0, 480, 74, 78),
        (13, 2880, 720, 67, 74),
        (15, 2880, 720, 72, 76),
    ])
    return [a, b, ha, hb, ca, cb]


def _s02(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 240, 720, 74, 86), (0, 1440, 480, 79, 92), (0, 2400, 960, 69, 84),
        (1, 240, 1440, 71, 88), (1, 2160, 1200, 74, 90),
        (2, 0, 960, 72, 92), (2, 1440, 480, 71, 88), (2, 2400, 960, 67, 84),
        (3, 1920, 1440, 74, 90),
        (4, 720, 960, 77, 96), (4, 2160, 1200, 74, 92),
        (5, 240, 480, 72, 90), (5, 1200, 1440, 69, 86),
        (6, 960, 1920, 67, 84),
        (7, 0, 480, 65, 80), (7, 960, 1920, 62, 78),
        (8, 240, 480, 74, 100), (8, 960, 480, 77, 106), (8, 1680, 1440, 81, 112),
        (9, 480, 1920, 79, 108),
        (10, 1440, 960, 76, 100), (10, 2880, 720, 74, 96),
        (11, 240, 2880, 71, 92),
        (12, 960, 480, 79, 98), (12, 1920, 960, 74, 94), (12, 3360, 480, 69, 88),
        (13, 240, 1440, 67, 86), (13, 2160, 1200, 74, 92),
        (14, 720, 720, 72, 90), (14, 1920, 1440, 71, 88),
        (15, 0, 2880, 74, 96),
    ])
    lay(b, [
        (0, 0, 1440, 69, 84), (0, 1920, 1440, 74, 90),
        (1, 480, 960, 76, 94), (1, 1920, 1440, 74, 90),
        (2, 0, 720, 72, 88), (2, 1200, 1920, 67, 84),
        (3, 960, 1920, 74, 92),
        (4, 0, 480, 79, 100), (4, 960, 1440, 74, 96), (4, 2880, 720, 71, 90),
        (5, 480, 2880, 69, 88),
        (6, 240, 720, 65, 82), (6, 1440, 1440, 62, 78),
        (7, 960, 1920, 67, 84),
        (8, 0, 960, 81, 112), (8, 1440, 1920, 79, 106),
        (9, 480, 480, 77, 100), (9, 1440, 1920, 74, 94),
        (10, 0, 1440, 72, 90), (10, 1920, 1440, 71, 88),
        (11, 720, 2400, 74, 92),
        (12, 1920, 1440, 79, 98),
        (13, 0, 960, 76, 94), (13, 1440, 1920, 74, 90),
        (14, 480, 960, 71, 86), (14, 1920, 1440, 69, 84),
        (15, 240, 2880, 62, 80),
    ])
    chords(ha, [
        (0, 0, 4 * BAR, (50, 53, 57), 66),
        (4, 0, 4 * BAR, (55, 59, 62), 70),
        (8, 0, 4 * BAR, (53, 57, 60), 74),
        (12, 0, 3 * BAR, (50, 57, 62), 72),
    ])
    chords(hb, [
        (0, 0, 1440, (62, 65, 69), 78),
        (2, 960, 1920, (57, 62, 65), 74),
        (4, 240, 1680, (55, 59, 67), 76),
        (6, 0, 2880, (59, 62, 71), 72),
        (8, 480, 1440, (53, 60, 65), 80),
        (10, 0, 1920, (57, 60, 69), 76),
        (12, 720, 1440, (50, 57, 62), 74),
        (14, 0, 2400, (62, 69, 74), 78),
    ])
    lay(ca, [
        (3, 0, 960, 69, 74), (3, 1440, 720, 67, 72),
        (7, 1920, 1440, 65, 70),
        (8, 3120, 480, 72, 76),
        (11, 3120, 480, 74, 78),
        (12, 0, 720, 67, 74),
        (14, 0, 480, 71, 76),
        (15, 2880, 720, 69, 74),
    ])
    lay(cb, [
        (2, 3120, 480, 74, 76),
        (5, 0, 480, 72, 74),
        (6, 2880, 720, 69, 72),
        (9, 2880, 720, 76, 80),
        (10, 3360, 480, 71, 74),
        (12, 0, 960, 74, 76),
        (13, 2880, 720, 72, 74),
        (15, 3120, 480, 67, 70),
    ])
    return [a, b, ha, hb, ca, cb]


def _s03(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 0, 2880, 77, 88),
        (1, 960, 1920, 81, 104),
        (2, 0, 1440, 79, 96), (2, 2400, 960, 77, 90),
        (3, 480, 2880, 74, 86),
        (4, 0, 1920, 72, 90),
        (5, 1440, 1920, 70, 84),
        (6, 0, 960, 77, 96), (6, 1920, 1440, 81, 108),
        (7, 480, 2880, 77, 92),
    ])
    lay(b, [
        (0, 960, 1440, 81, 100),
        (1, 0, 1920, 77, 92), (1, 2400, 960, 74, 86),
        (2, 480, 2400, 72, 88),
        (3, 0, 1440, 70, 84), (3, 1920, 1440, 69, 82),
        (4, 720, 1920, 74, 90),
        (5, 0, 960, 76, 94), (5, 1440, 1920, 77, 98),
        (6, 480, 960, 79, 102), (6, 1920, 1440, 81, 108),
        (7, 0, 3360, 77, 94),
    ])
    chords(ha, [
        (0, 0, 2 * BAR, (53, 57, 60), 66),
        (2, 0, 2 * BAR, (58, 62, 65), 70),
        (4, 0, 2 * BAR, (48, 52, 55), 72),
        (6, 0, 2 * BAR, (53, 57, 60), 74),
    ])
    chords(hb, [
        (0, 0, 2880, (60, 65, 69), 76),
        (2, 480, 1920, (58, 62, 65), 74),
        (4, 0, 1440, (48, 55, 64), 72),
        (5, 1920, 1440, (52, 55, 60), 70),
        (6, 0, 1920, (53, 60, 65), 76),
    ])
    lay(ca, [
        (0, 2880, 720, 74, 72),
        (1, 0, 720, 72, 70),
        (2, 1440, 720, 76, 74),
        (3, 3360, 480, 70, 68),
        (4, 1920, 1440, 69, 72),
        (5, 0, 960, 77, 76),
        (6, 960, 720, 74, 74),
        (7, 3360, 480, 72, 70),
    ])
    lay(cb, [
        (0, 0, 720, 77, 74),
        (1, 1920, 480, 74, 72),
        (2, 2880, 720, 72, 70),
        (3, 1440, 480, 70, 68),
        (4, 0, 480, 69, 70),
        (5, 960, 480, 76, 74),
        (6, 1440, 480, 79, 78),
        (7, 3360, 480, 77, 74),
    ])
    return [a, b, ha, hb, ca, cb]


def _s04(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 0, 720, 64, 82), (0, 960, 1440, 71, 90),
        (1, 0, 480, 74, 94), (1, 960, 1920, 76, 98),
        (2, 480, 960, 79, 104), (2, 1920, 1440, 81, 108),
        (3, 0, 2880, 83, 116),
        (4, 720, 720, 81, 104), (4, 1920, 1440, 79, 98),
        (5, 0, 960, 76, 96), (5, 1440, 480, 71, 90), (5, 2400, 960, 72, 92),
        (6, 480, 2880, 71, 88),
        (7, 960, 1920, 69, 84),
        (9, 0, 1440, 76, 100), (9, 1920, 1440, 72, 94),
        (10, 240, 720, 74, 96), (10, 1440, 1920, 71, 90),
        (11, 0, 960, 69, 86), (11, 1440, 1920, 67, 82),
        (12, 0, 480, 76, 100), (12, 720, 960, 83, 112), (12, 2160, 1200, 81, 104),
        (13, 480, 1440, 79, 98), (13, 2400, 960, 76, 92),
        (14, 0, 1920, 74, 88), (14, 2400, 960, 71, 84),
        (15, 960, 2400, 64, 80),
    ])
    lay(b, [
        (0, 480, 1440, 83, 110), (0, 2400, 960, 76, 100),
        (1, 0, 1920, 79, 104), (1, 2400, 960, 74, 96),
        (2, 720, 2400, 71, 92),
        (3, 0, 960, 69, 86), (3, 1920, 1440, 67, 82),
        (5, 1440, 1920, 64, 80),
        (6, 0, 720, 72, 88), (6, 1200, 1440, 76, 96),
        (7, 480, 960, 78, 100), (7, 1920, 1440, 81, 106),
        (8, 0, 2880, 83, 114),
        (9, 960, 480, 81, 104), (9, 1920, 1440, 79, 98),
        (10, 0, 1440, 76, 94), (10, 1920, 1440, 71, 88),
        (11, 480, 2880, 69, 84),
        (12, 1920, 1440, 74, 90),
        (13, 0, 960, 72, 88), (13, 1440, 1920, 76, 96),
        (14, 240, 1200, 79, 102), (14, 1920, 1440, 83, 112),
        (15, 0, 1920, 81, 100), (15, 2400, 960, 76, 92),
    ])
    chords(ha, [
        (0, 0, 4 * BAR, (52, 55, 59), 66),
        (4, 0, 4 * BAR, (48, 52, 55), 70),
        (9, 0, 3 * BAR, (57, 60, 64), 74),
        (12, 0, 3 * BAR, (52, 59, 64), 72),
    ])
    chords(hb, [
        (0, 0, 1920, (59, 64, 71), 78),
        (2, 480, 2400, (55, 62, 67), 74),
        (4, 0, 1440, (48, 55, 60), 72),
        (6, 960, 1920, (52, 55, 64), 74),
        (9, 0, 2880, (57, 60, 64), 78),
        (12, 240, 1680, (52, 59, 64), 74),
        (14, 960, 1440, (55, 59, 62), 70),
    ])
    lay(ca, [
        (4, 0, 480, 76, 74),
        (5, 960, 480, 74, 72),
        (8, 960, 1920, 72, 76),
        (10, 0, 240, 71, 70),
        (11, 3360, 480, 69, 72),
        (13, 0, 480, 67, 70),
        (14, 1920, 480, 64, 68),
        (15, 0, 720, 71, 72),
    ])
    lay(cb, [
        (1, 1920, 480, 76, 74),
        (4, 480, 1920, 74, 76),
        (5, 0, 960, 72, 72),
        (8, 2880, 720, 69, 70),
        (11, 0, 480, 67, 68),
        (12, 0, 1440, 64, 70),
        (14, 1440, 480, 71, 74),
        (15, 1920, 480, 74, 72),
    ])
    return [a, b, ha, hb, ca, cb]


def _s05(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 1920, 1440, 71, 86),
        (1, 1920, 480, 74, 90), (1, 2880, 720, 78, 96),
        (2, 0, 960, 76, 92), (2, 1920, 1440, 74, 88),
        (3, 1440, 1920, 71, 84),
        (4, 1920, 960, 69, 86), (4, 3360, 480, 67, 82),
        (5, 960, 960, 66, 80), (5, 2400, 960, 71, 88),
        (6, 1920, 1440, 74, 92),
        (7, 480, 2880, 73, 90),
        (8, 1920, 480, 78, 104), (8, 2880, 720, 81, 110),
        (9, 0, 1440, 83, 116), (9, 1920, 1440, 79, 104),
        (10, 960, 1920, 76, 98),
        (12, 0, 1440, 71, 92), (12, 1920, 480, 74, 96), (12, 2880, 720, 78, 102),
        (13, 0, 960, 81, 108), (13, 1440, 1920, 83, 114),
        (14, 480, 1440, 79, 100), (14, 2400, 960, 76, 94),
        (15, 0, 2880, 71, 86),
    ])
    lay(b, [
        (0, 0, 960, 71, 84), (0, 1440, 1440, 79, 96),
        (1, 480, 1920, 78, 94),
        (2, 0, 480, 76, 90), (2, 960, 1440, 74, 88), (2, 2880, 720, 71, 84),
        (3, 1920, 1440, 69, 82),
        (4, 0, 2880, 66, 80),
        (5, 1440, 960, 73, 88), (5, 2880, 720, 74, 90),
        (6, 480, 1440, 78, 98), (6, 2400, 960, 81, 106),
        (7, 0, 1920, 83, 112),
        (9, 1920, 1440, 76, 96),
        (10, 0, 960, 74, 90), (10, 1440, 1920, 71, 86),
        (11, 720, 1440, 69, 84), (11, 2640, 960, 67, 80),
        (12, 1920, 1440, 71, 90),
        (13, 480, 480, 74, 94), (13, 1440, 1920, 78, 102),
        (14, 0, 1440, 81, 108), (14, 1920, 1440, 83, 114),
        (15, 960, 2400, 79, 98),
    ])
    chords(ha, [
        (0, 0, 4 * BAR, (59, 62, 66), 66),
        (4, 0, 4 * BAR, (55, 59, 62), 70),
        (8, 0, 3 * BAR, (57, 61, 64), 74),
        (12, 0, 3 * BAR, (59, 62, 66), 72),
    ])
    chords(hb, [
        (0, 1920, 1440, (59, 66, 71), 76),
        (2, 0, 2880, (62, 66, 74), 74),
        (4, 480, 1920, (55, 59, 67), 72),
        (6, 0, 1440, (55, 62, 71), 74),
        (8, 960, 1920, (57, 61, 64), 78),
        (12, 0, 2400, (59, 66, 74), 76),
        (14, 1440, 1440, (62, 66, 71), 72),
    ])
    lay(ca, [
        (0, 0, 1440, 66, 70),
        (2, 960, 480, 69, 72),
        (5, 0, 720, 71, 74),
        (7, 3360, 480, 74, 72),
        (11, 480, 1920, 76, 78),
        (13, 960, 480, 73, 74),
        (14, 0, 480, 71, 72),
        (15, 2880, 720, 66, 70),
    ])
    lay(cb, [
        (3, 0, 1440, 74, 74),
        (4, 2880, 720, 71, 72),
        (7, 1920, 1440, 69, 70),
        (8, 960, 1920, 78, 80),
        (10, 3360, 480, 73, 74),
        (12, 0, 1440, 76, 76),
        (14, 1440, 480, 74, 72),
        (15, 0, 720, 71, 70),
    ])
    return [a, b, ha, hb, ca, cb]


def _s06(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 0, 480, 79, 90), (0, 720, 240, 81, 82), (0, 1200, 960, 79, 94), (0, 2640, 720, 82, 98),
        (1, 480, 1440, 77, 92), (1, 2400, 960, 75, 86),
        (2, 0, 1920, 74, 88), (2, 2400, 960, 72, 84),
        (3, 960, 1920, 70, 82),
        (4, 0, 480, 67, 80), (4, 720, 240, 69, 76), (4, 1200, 1440, 67, 84),
        (6, 480, 480, 78, 108, True), (6, 1200, 1920, 79, 114),
        (7, 0, 720, 82, 100), (7, 1200, 1920, 79, 104),
    ])
    lay(b, [
        (0, 240, 720, 79, 88), (0, 1200, 480, 77, 84), (0, 1920, 1440, 79, 94),
        (1, 0, 960, 82, 98), (1, 1440, 1920, 77, 90),
        (2, 480, 2880, 75, 86),
        (3, 0, 1440, 74, 84), (3, 1920, 1440, 72, 82),
        (4, 960, 480, 70, 80), (4, 1920, 1440, 67, 84),
        (5, 0, 960, 75, 88), (5, 1440, 1920, 74, 86),
        (6, 240, 720, 77, 96), (6, 1440, 1920, 79, 104),
        (7, 480, 2880, 82, 100),
    ])
    chords(ha, [
        (0, 0, 3 * BAR, (55, 58, 62), 66),
        (3, 0, 2 * BAR, (51, 55, 58), 70),
        (6, 0, 2 * BAR, (55, 58, 62), 74),
    ])
    chords(hb, [
        (0, 0, 1440, (58, 62, 67), 76),
        (1, 1920, 1440, (55, 62, 70), 74),
        (3, 480, 1920, (51, 58, 63), 72),
        (6, 240, 1680, (55, 62, 67), 76),
        (7, 0, 960, (58, 62, 70), 74),
    ])
    lay(ca, [
        (1, 0, 480, 74, 72),
        (2, 1920, 480, 72, 70),
        (3, 0, 720, 79, 76),
        (4, 2640, 720, 77, 74),
        (5, 480, 1920, 70, 72),
        (6, 0, 480, 75, 74),
        (6, 3120, 480, 77, 76),
        (7, 720, 480, 74, 72),
    ])
    lay(cb, [
        (0, 0, 240, 75, 70),
        (2, 3360, 480, 74, 72),
        (3, 3360, 480, 72, 70),
        (4, 0, 720, 70, 72),
        (5, 960, 480, 70, 74),
        (6, 960, 480, 77, 76),
        (7, 0, 480, 79, 78),
        (7, 3360, 480, 75, 72),
    ])
    return [a, b, ha, hb, ca, cb]


def _s07(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 0, 720, 60, 82), (0, 960, 960, 81, 108), (0, 2880, 720, 79, 96),
        (1, 480, 1440, 76, 92), (1, 2400, 960, 72, 86),
        (2, 0, 1920, 74, 88),
        (3, 1440, 1920, 72, 84),
        (4, 0, 480, 67, 86), (4, 960, 1440, 84, 114), (4, 2880, 720, 81, 104),
        (5, 960, 2400, 77, 96),
        (7, 1920, 1440, 76, 90),
        (8, 0, 960, 72, 88), (8, 1440, 480, 65, 80), (8, 2400, 960, 69, 84),
        (9, 480, 2880, 67, 82),
        (10, 0, 720, 72, 90), (10, 1200, 1440, 81, 108),
        (11, 0, 960, 79, 100), (11, 1920, 1440, 76, 94),
        (12, 480, 960, 81, 104), (12, 1920, 1440, 60, 84),
        (13, 0, 1440, 64, 82), (13, 1920, 1440, 67, 86),
        (14, 960, 480, 69, 88), (14, 1920, 1440, 72, 92),
        (15, 0, 2880, 60, 78),
    ])
    lay(b, [
        (0, 480, 1440, 72, 88), (0, 2400, 960, 64, 80),
        (1, 0, 960, 67, 84), (1, 1440, 1920, 69, 86),
        (2, 240, 1200, 74, 92), (2, 1920, 1440, 77, 98),
        (3, 0, 2880, 79, 104),
        (4, 960, 480, 81, 108), (4, 1920, 1440, 72, 94),
        (5, 480, 1920, 76, 96),
        (6, 0, 720, 74, 90), (6, 1440, 1920, 72, 86),
        (8, 1920, 1440, 84, 116),
        (9, 0, 960, 81, 108), (9, 1440, 1920, 79, 100),
        (10, 480, 1440, 77, 96), (10, 2400, 960, 76, 92),
        (11, 0, 1920, 74, 88), (11, 2400, 960, 72, 84),
        (12, 0, 480, 69, 86), (12, 960, 1920, 60, 80),
        (13, 480, 960, 64, 82), (13, 1920, 1440, 67, 86),
        (14, 0, 1440, 72, 90), (14, 1920, 480, 65, 82), (14, 2880, 720, 69, 86),
        (15, 240, 3120, 72, 92),
    ])
    chords(ha, [
        (0, 0, 4 * BAR, (48, 52, 55), 66),
        (4, 0, 4 * BAR, (53, 57, 60), 70),
        (8, 0, 3 * BAR, (57, 60, 64), 74),
        (12, 0, 3 * BAR, (48, 55, 64), 72),
    ])
    chords(hb, [
        (0, 0, 960, (60, 64, 67), 76),
        (2, 480, 1920, (52, 55, 60), 72),
        (4, 0, 1440, (53, 60, 65), 76),
        (6, 960, 1440, (57, 60, 69), 74),
        (8, 0, 2880, (57, 64, 69), 78),
        (12, 480, 1920, (48, 55, 64), 74),
        (14, 0, 1440, (60, 64, 72), 76),
    ])
    lay(ca, [
        (1, 0, 480, 69, 70),
        (3, 0, 960, 67, 72),
        (6, 480, 1920, 72, 76),
        (7, 0, 1440, 74, 74),
        (9, 0, 480, 76, 76),
        (11, 960, 480, 77, 74),
        (12, 0, 480, 79, 78),
        (15, 2880, 720, 64, 68),
    ])
    lay(cb, [
        (0, 0, 480, 76, 74),
        (3, 2880, 720, 74, 72),
        (5, 2400, 960, 72, 74),
        (7, 960, 1920, 69, 72),
        (8, 0, 1440, 67, 70),
        (10, 1920, 480, 65, 68),
        (13, 0, 480, 64, 66),
        (15, 3360, 480, 60, 64),
    ])
    return [a, b, ha, hb, ca, cb]


def _s08(study):
    a, b = lead(study, "a"), lead(study, "b")
    ha, hb = harmony(study, "a"), harmony(study, "b")
    ca, cb = counter(study, "a"), counter(study, "b")
    lay(a, [
        (0, 960, 1440, 78, 76), (0, 2880, 720, 81, 84),
        (1, 480, 1920, 80, 90), (1, 2880, 720, 78, 86),
        (2, 0, 960, 76, 88), (2, 1440, 1920, 73, 84),
        (3, 960, 2400, 81, 98),
        (4, 0, 480, 83, 112), (4, 960, 1440, 81, 104), (4, 2880, 720, 78, 96),
        (6, 960, 480, 69, 80), (6, 1920, 1440, 66, 76),
        (7, 0, 960, 68, 78), (7, 1440, 1920, 66, 74),
    ])
    lay(b, [
        (0, 0, 1920, 66, 74), (0, 2400, 960, 69, 80),
        (1, 480, 960, 71, 84), (1, 1920, 1440, 73, 88),
        (2, 0, 2880, 74, 90),
        (3, 960, 480, 76, 94), (3, 1920, 1440, 78, 100),
        (4, 240, 1200, 80, 106), (4, 1920, 1440, 81, 110),
        (5, 0, 1440, 83, 116), (5, 1920, 1440, 81, 104),
        (6, 1440, 1920, 78, 96),
        (7, 480, 480, 76, 88), (7, 1440, 1920, 73, 84),
    ])
    chords(ha, [
        (0, 0, 3 * BAR, (54, 57, 61), 64),
        (3, 0, 2 * BAR, (50, 54, 57), 68),
        (6, 0, 2 * BAR, (54, 57, 61), 72),
    ])
    chords(hb, [
        (0, 960, 1440, (61, 66, 69), 74),
        (2, 0, 1920, (54, 61, 66), 72),
        (3, 480, 1440, (50, 57, 62), 70),
        (6, 0, 2880, (54, 61, 69), 76),
        (7, 1440, 1440, (57, 61, 66), 72),
    ])
    lay(ca, [
        (0, 0, 720, 73, 68),
        (1, 0, 480, 76, 70),
        (2, 960, 480, 74, 72),
        (3, 0, 720, 76, 74),
        (5, 480, 2400, 78, 80),
        (6, 0, 720, 73, 72),
        (6, 3360, 480, 71, 70),
        (7, 960, 480, 69, 68),
    ])
    lay(cb, [
        (0, 1920, 480, 71, 70),
        (1, 1440, 480, 73, 72),
        (2, 2880, 720, 76, 74),
        (4, 1440, 480, 78, 78),
        (5, 1440, 480, 80, 80),
        (6, 0, 960, 74, 72),
        (7, 0, 480, 71, 70),
        (7, 3360, 480, 69, 68),
    ])
    return [a, b, ha, hb, ca, cb]


BUILDERS = {f"s0{i}": fn for i, fn in enumerate([_s01, _s02, _s03, _s04, _s05, _s06, _s07, _s08], 1)}


def _sig(notes):
    return tuple((note["performed_start"], note["pitch"], note["duration"]) for note in notes)


def assert_collections(catalog_studies, parts):
    allowed = {study["id"]: set(study["pitch_classes"]) for study in catalog_studies}
    for part in parts:
        pool = allowed[part["study_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")


def assert_identities(parts):
    leads = [part for part in parts if part["role"] == "principal-lead"]
    by = {}
    for part in leads:
        by.setdefault(part["study_id"], {})[part["variation"]] = part
    rhythms = {}
    report = []
    for study_id, vars_ in by.items():
        if _sig(vars_["a"]["notes"]) == _sig(vars_["b"]["notes"]):
            raise ValueError(f"{study_id} variations match in start, pitch, and duration")
        rhythm = tuple(note["performed_start"] for note in vars_["a"]["notes"])
        if rhythm in rhythms:
            raise ValueError(f"{study_id} variation A attack times repeat {rhythms[rhythm]}")
        rhythms[rhythm] = study_id
        report.append({"study_id": study_id, "a": len(vars_["a"]["notes"]), "b": len(vars_["b"]["notes"])})
    if len(report) != 8:
        raise ValueError("expected eight leads")
    return {
        "studies": report,
        "method": "lead variations differ in start, pitch, or duration; variation A attack times are unique across the eight studies",
    }


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    assert_collections(catalog_studies, parts)
    identity = assert_identities(parts)
    core = [part for part in parts if part["core"]]
    refs = [part for part in parts if not part["core"]]
    if len(core) != 16 or len(refs) != 32:
        raise ValueError((len(core), len(refs)))
    preview = next(study for study in catalog_studies if study["id"] == "s01")
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": preview["bars"] * BAR,
        "bpm": preview["bpm"],
        "tempo_us": preview["tempo_us"],
        "meter": "4/4",
        "description": "Study 01 variation A: principal lead, harmonic reference, and counterphrase. The reference parts are not inside the lead file.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Principal Lead", "source_part": "s01.lead.a", "channel": 0},
            {"name": "Harmonic Reference", "source_part": "s01.harmony.a", "channel": 1},
            {"name": "Counterphrase", "source_part": "s01.counter.a", "channel": 2},
        ],
    }
    catalog = {
        "pack_id": PACK_ID, "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION, "generator_version": GENERATOR_VERSION,
        "ppq": PPQ, "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [48, 84], "c4": 60,
        "note_policy": "note-only MIDI. No program changes, controllers, pitch bend, or delay data.",
        "microtiming": "offset is 0; performed_start = nominal_start",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is random.",
        "core_part_count": len(core), "reference_part_count": len(refs),
        "core_role": "principal-lead",
        "reference_roles": ["harmonic-reference", "counterphrase"],
        "range_statement": "The principal lead is monophonic, MIDI 60 to 84. The harmonic reference uses MIDI 48 to 76, at most four notes at once, and is not part of the core count. The counterphrase is monophonic, MIDI 55 to 81, and is also reference only.",
        "container_plan": [
            {"id": study["id"], "bars": study["bars"], "bpm": study["bpm"],
             "seconds": study["bars"] * 4 * 60 / study["bpm"]}
            for study in catalog_studies
        ],
        "studies": [{key: study[key] for key in (
            "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "meter", "bar_ticks",
            "tonic", "tonal_reference", "collection_name", "pitch_classes", "departures", "seed",
            "harmonic_rhythm", "changes", "change_bars", "phrases", "identity", "limitations",
            "voicing", "layering", "accent", "stochastic_draws",
        )} for study in catalog_studies],
        "parts": [{
            "id": part["id"], "study_id": part["study_id"], "role": part["role"], "variation": part["variation"],
            "core": part["core"], "channel": part["channel"], "path": part["path"], "notes": len(part["notes"]),
            "container_bars": part["container_bars"], "bpm": part["bpm"], "monophonic": part["monophonic"],
        } for part in parts],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.lead.a", "s01.harmony.a", "s01.counter.a"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID, "generator_version": GENERATOR_VERSION, "ppq": PPQ,
        "parts": parts, "arrangement": arrangement, "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
