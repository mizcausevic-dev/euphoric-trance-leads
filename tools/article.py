"""Factual article draft. Not published."""

from __future__ import annotations

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

TITLE = "Euphoric Trance Leads is a note-only MIDI study pack"
SUBTITLE = "Eight studies with phrase arcs, rests, and transformed returns, plus a simple-synth preview that is not a master"
TAGS = ["midi", "trance", "leads", "composition", "music-production"]
TAG_LINE = "Tags: " + ", ".join(TAGS)

PARAGRAPHS = [
    "DRAFT. " + PUBLICATION,
    TAG_LINE,
    "The pack is eight trance-lead studies in 4/4. Tempos are integers from 132 to 140 BPM. Container lengths were chosen before the notes. Study 01, Lifted Fifth, variation A, is 16 bars at 138 BPM. The encoded preview is 27.873 seconds, and that full study is the preview. Studies 03, 06, and 08 are 8 bars. The others are 16. Each study has two variations of the principal lead. Those sixteen files are the core. Each study also has two harmonic references and two counterphrases. Those thirty-two files are reference only and are not in the core count.",
    "Lifted Fifth waits an eighth, states a fifth, and returns to it on the downbeat after an Am7 rise. Open Fourth lifts a fourth and later lets that fourth fall. Held Third keeps long tones and gives the major third the color. Broken Arc climbs by thirds, leaves a bar empty, and compresses the opening on the way back. Late Call speaks on beat 3 until the return moves the same shape onto the downbeat. Neighbor Turn decorates G, rests, and in variation A uses one flagged F#5 into G5. Wide Leap jumps from C4 to A5 and later leaps back down, with no B in the collection. Soft Return starts on beat 2, peaks, rests, and comes back an octave lower. Variation B of each study changes the start, the pitch, or the duration. Velocity alone does not make the variation.",
    "The lead is monophonic by default, from MIDI 60 to 84. C4 is 60. The resolution is 960 ticks per quarter note. Offsets are 0. The harmonic reference is a separate file from MIDI 48 to 76, at most four notes at once. The counterphrase is a separate monophonic file from MIDI 55 to 81. Supersaw patches, scale runs, and delay are not the composition and they are not in the files. These themes are original.",
    PROGRAM,
    "The preview synth uses a triangle plus a quiet same-pitch sine for the lead, a quieter triangle for the harmony, and a sine for the counterphrase. That mapping is documented. It is not a program change. There is no delay line in the renderer.",
    "The primary preview is study 01, Lifted Fifth, variation A, for all 16 bars at 138 BPM. The encoded MP3 is 27.873 seconds. It is the lead, the harmonic reference, and the counterphrase together. The other studies are in the MIDI and are not in that audio file. "
    + PREVIEW_LINE
    + ". The film takes its audio from that preview file and shows the words "
    + ON_PICTURE
    + " on the picture and in the WebVTT captions.",
    AUDITION
    + " The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not a loudness measurement.",
    "The stills are procedural illustrations of a broken phrase arc on a midnight field. The gaps in the arc are rests. The violet segment is the transformed return. They are not photographs of a session or of performers.",
    "When a public URL exists, use either the combined arrangement or the separate parts. " + WARNING,
    "Call to action: the MIDI, the matched report, and the preview belong together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.",
]


def markdown() -> str:
    body = "\n\n".join(PARAGRAPHS)
    return f"# {TITLE}\n\n{SUBTITLE}\n\n{body}\n"


def plain_text() -> str:
    lines = [TITLE, "", SUBTITLE, "", *PARAGRAPHS, ""]
    return "\n".join(lines) + "\n"
