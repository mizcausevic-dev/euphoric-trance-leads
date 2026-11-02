# Euphoric Trance Leads

Original note-only MIDI studies of euphoric trance leads. Eight studies, two variations of the principal lead. Each lead is a monophonic phrase with an arc, rests, and a transformed return. Harmonic references and counterphrases are cataloged separately and are not part of the core count. They are not merged into the lead files.

This repository is the pack. The GitHub repository is https://github.com/mizcausevic-dev/euphoric-trance-leads and it is public. The catalog page is https://mizcausevic-dev.github.io/euphoric-trance-leads/ .

## What you can open

- `index.html` is the file catalog. The lead phrase is drawn from the MIDI bytes, one note at a time.
- `media.html` is the stills page. The film sits under the pictures.
- `midi/arrangement.mid` is a Format 1 preview arrangement of study 01, variation A: principal lead, harmonic reference, and counterphrase.
- Individual Format 0 parts live under `midi/`.
- `midi/validation-Cursor.json` is the report from reopening those exact bytes.
- `preview/preview.mp3` is the primary music preview. It is 27.826 seconds in the encoded file. preview, not a master.
- `film/preview.mp4` and `film/preview.vtt` are the film. On-picture and caption text is `preview, not master`.
- `art/hero.jpg` is a 1280x720 illustration. `art/square.jpg` is 1080x1080. Neither is a photograph.

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

## Studies

- s01 Lifted Fifth: 138 BPM, 16 bars, A natural minor, tonic reference A.
- s02 Open Fourth: 136 BPM, 16 bars, D dorian, tonic reference D.
- s03 Held Third: 140 BPM, 8 bars, F major, tonic reference F.
- s04 Broken Arc: 134 BPM, 16 bars, E natural minor, tonic reference E.
- s05 Late Call: 132 BPM, 16 bars, B natural minor, tonic reference B.
- s06 Neighbor Turn: 137 BPM, 8 bars, G natural minor, tonic reference G.
- s07 Wide Leap: 135 BPM, 16 bars, C major without B, tonic reference C.
- s08 Soft Return: 139 BPM, 8 bars, F# natural minor, tonic reference F#.

Core files: 16. Reference files: 32.

The principal lead is monophonic, MIDI 60 to 84. The harmonic reference uses MIDI 48 to 76, at most four notes at once, and is not part of the core count. The counterphrase is monophonic, MIDI 55 to 81, and is also reference only. C4 is 60. PPQ is 960. Meter is 4/4. Offsets are 0. Seeds identify studies and are not random draws. Generator 1.0.0. Phrase shape, harmonic context, and accent contour are written on each study.

Container lengths were fixed before the notes. Study 01 is 16 bars at 138 BPM so the full study is the preview and lands between 10 and 40 seconds.

## Preview path

The preview renders the canonical notes for `s01.lead.a`, `s01.harmony.a`, and `s01.counter.a` with `simple-synth-1.0.0`. Tempo authority is the encoded microsecond value in the MIDI, 434783 us per quarter note. Sample positions use `floor(seconds * 44100 + 0.5)` from tick 0. Intervals are not summed. Sample-exact repeating loops at an arbitrary BPM are not promised.

The synth mapping is a triangle plus a quiet same-pitch sine for the lead, a quieter triangle for the harmony, and a sine for the counterphrase. No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary. The mapping is not encoded in the MIDI. The renderer does not add delay.

Encoded MP3 settings: libmp3lame, 192 kbps. Film audio is AAC at 160 kbps re-encoded from that MP3, so the decoded film audio is not byte-identical to the MP3. Film duration probe: 27.826 seconds. MP3 container probe 27.826 seconds. MP4 probe 27.826 seconds. The film ends on a video frame, so it is slightly shorter than the MP3 container. The music is the same preview, not a different excerpt. The picture is a still illustration with rasterized disclosure text. DejaVu Sans Bold from the build machine supplies the glyphs. The font file is not in this pack.

No human listening audition was performed for this build. A sample peak is recorded in the preview manifest. It is not a loudness measurement and it is not a true peak.

## Build

From the repository root, with Python 3.11+ and ffmpeg (libmp3lame, aac, libx264):

```bash
python3 tools/build_pack.py
python3 -m http.server 43131
```

The page is static. It is served with Python's HTTP server so the MIDI and media keep working relative paths. There is no application server and no package install. Standard library only.

`build/` holds the intermediate WAV, the procedural PPM, and the film plate. Those files are gitignored. The delivered audio is the MP3.

## Checks the validator actually runs

File existence, parse, PPQ, tempo, 4/4, end-of-track boundary, note pairing, ranges, monophonic lead, monophonic counterphrase, harmonic polyphony cap of four, note-off before note-on at a shared tick, absence of program changes and other channel messages, departure flags against the declared pitch-class set, unique variation A attack times, agreement with the canonical score, and agreement between `arrangement.mid` and the three source files. Arrangement track count follows the arrangement tracks. A negative overlap fixture is written outside the pack and must be rejected.

## Drafts and publication

Social captions, the X post, and the Medium article are drafts. They are not access controls. If this repository is public, the drafts are public. Do not treat them as posted to Instagram, X, or Medium.

Prepared repository description: Original note-only MIDI studies of euphoric trance leads, with phrase arcs, rests, and transformed returns.

Prepared topics: midi, trance, leads, music-production, composition, general-midi, study-pack.

No release tag was created. `index.html` keeps its name because players and links depend on it. This page is the file catalog the pack requires.

## Limitations

Variation compatibility is per study and is written on the page. Variation A and variation B of a study are alternatives. Pair harmony A and counterphrase A with lead A, and the B files with lead B. The arrangement is only study 01. Stacking it with the part files doubles those notes. These leads are original. The preview is a simple-synth reading, not a performance.
