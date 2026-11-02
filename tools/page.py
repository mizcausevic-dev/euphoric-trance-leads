"""Catalog page. The phrase is read from the lead MIDI."""

from __future__ import annotations

import json
from pathlib import Path

from tools.screening import lead_frames, render_media
from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

SPELL = {
    "s01": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
    "s02": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
    "s03": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
    "s04": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s05": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s06": ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
    "s07": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
    "s08": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
}


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    root = path.parent
    path.with_name("media.html").write_text(render_media({
        "pack_name": catalog["pack_name"],
        "subject": "The still is a lead phrase. The arc rises, breaks for a rest, peaks, and returns in violet. Ice is the line. The lower step is the harmonic horizon.",
        "colors": {
            "bg": "#071018",
            "paper": "#e7f6ff",
            "ink": "#071018",
            "accent": "#3ee0c8",
            "muted": "#9bb4c8",
        },
        "frames": lead_frames(root),
        "preview_seconds": preview["seconds_encoded"],
        "film_seconds": film["duration_seconds"],
    }), encoding="utf-8")


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    rows = []
    for part in catalog["parts"]:
        kind = "core" if part["core"] else "reference"
        rows.append(
            "<tr>"
            f"<td><a href=\"{part['path']}\">{part['id']}</a></td>"
            f"<td>{part['role']}</td>"
            f"<td>{part['variation']}</td>"
            f"<td>{kind}</td>"
            f"<td>{part['bpm']}</td>"
            f"<td>{part['notes']}</td>"
            "</tr>"
        )
    cards = []
    grouped: dict[str, list] = {}
    for part in catalog["parts"]:
        grouped.setdefault(part["study_id"], []).append(part)
    map_items = []
    for study in catalog["studies"]:
        cards.append(
            "<article class=\"study-card\">"
            f"<h3>{study['id']} {study['title']}</h3>"
            f"<p>{study['bpm']} BPM · {study['bars']} bars · {study['collection_name']} · tonic {study['tonal_reference']}</p>"
            f"<p>{study['identity']}</p>"
            f"<p>{study['harmonic_rhythm']}</p>"
            f"<p>{study['limitations']}</p>"
            "</article>"
        )
        names = ", ".join(
            f"{part['id']} ({'core' if part['core'] else 'reference'})"
            for part in grouped[study["id"]]
        )
        map_items.append(f"<li><strong>{study['id']}</strong> {names}</li>")
    payload = {
        "studies": [
            {
                "id": study["id"],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "voicing": study["voicing"],
                "layering": study["layering"],
                "accent": study["accent"],
                "departures": study["departures"],
                "harmonic_rhythm": study["harmonic_rhythm"],
                "changes": study["changes"],
                "change_bars": study["change_bars"],
                "phrases": study["phrases"],
                "tempo_us": study["tempo_us"],
                "spell": SPELL[study["id"]],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "path": part["path"],
            }
            for part in catalog["parts"]
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    seconds = f"{preview['seconds_encoded']:.2f}"
    film_seconds = f"{film['duration_seconds']:.2f}"
    html = TEMPLATE
    replacements = {
        "__ROWS__": "".join(rows),
        "__STUDIES__": "".join(cards),
        "__MAP__": "".join(map_items),
        "__SECONDS__": seconds,
        "__FILM_SECONDS__": film_seconds,
        "__RANGE__": catalog["range_statement"],
        "__WARNING__": WARNING,
        "__PROGRAM__": PROGRAM,
        "__AUDITION__": AUDITION,
        "__PUBLICATION__": PUBLICATION,
        "__PREVIEW_LINE__": PREVIEW_LINE,
        "__ON_PICTURE__": ON_PICTURE,
        "__RESULT__": report["result"],
        "__CORE__": str(catalog["core_part_count"]),
        "__REF__": str(catalog["reference_part_count"]),
        "__DATA__": data,
    }
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Euphoric Trance Leads</title>
  <style>
    :root {
      --bg: #071018;
      --paper: #e7f6ff;
      --ink: #071018;
      --ice: #3ee0c8;
      --violet: #9aa6ff;
      --muted: #9bb4c8;
      --line: rgba(231, 246, 255, .16);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; background: var(--bg); color: var(--paper);
      font-family: Georgia, "Iowan Old Style", Palatino, serif;
      line-height: 1.45; padding-bottom: 24px;
    }
    a { color: var(--ice); }
    button, .meta, .readout, .transport, .legend { font-family: ui-monospace, Menlo, Consolas, monospace; }
    .top {
      position: sticky; top: 0; z-index: 6;
      display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap;
      padding: 12px 20px; background: rgba(7, 16, 24, .94); border-bottom: 1px solid var(--line);
    }
    .brand { letter-spacing: .14em; text-transform: uppercase; font-size: .72rem; color: var(--paper); text-decoration: none; }
    .top nav { display: flex; gap: 14px; flex-wrap: wrap; font-size: .78rem; }
    main { width: min(1120px, calc(100% - 2rem)); margin: 0 auto; }
    .intro { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, .9fr); gap: 28px; align-items: start; padding: 28px 0 8px; }
    .intro > div { min-width: 0; }
    h1 { font-weight: 500; font-size: clamp(2.2rem, 5vw, 4.2rem); line-height: .92; margin: 8px 0 10px; }
    h2 { font-weight: 500; font-size: 1.5rem; margin: 28px 0 8px; }
    h3 { font-weight: 500; margin: 0 0 6px; }
    .kicker { letter-spacing: .16em; text-transform: uppercase; color: var(--ice); font-size: .74rem; margin: 0; }
    .meta, .note { color: var(--muted); font-size: .82rem; }
    .hero img, .study-card, video, audio { max-width: 100%; }
    .hero img { display: block; width: 100%; height: auto; border-radius: 14px; }
    .rail, .phrases, .switch, .stepper, .toggles { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }
    .rail { overflow-x: auto; flex-wrap: nowrap; max-width: 100%; padding-bottom: 4px; }
    button {
      border: 1px solid var(--line); background: transparent; color: var(--paper);
      border-radius: 999px; padding: 7px 11px; cursor: pointer;
    }
    button[aria-pressed="true"], .note-pill.on { background: var(--ice); color: var(--ink); border-color: var(--ice); }
    .readout {
      background: #102033; border-radius: 12px; padding: 12px 14px; min-height: 4.5rem;
    }
    .scroller { overflow-x: auto; max-width: 100%; background: #e7f6ff; color: var(--ink); border-radius: 16px; padding: 10px 0 14px; }
    .sheet { position: relative; }
    .ruler { position: relative; height: 28px; }
    .change {
      position: absolute; top: 4px; height: 20px; border-left: 2px solid #0b7f78;
      padding-left: 5px; font-size: 11px; white-space: nowrap; overflow: hidden;
    }
    .lane { position: relative; height: 210px; }
    .support { position: relative; height: 54px; border-top: 1px solid rgba(7, 16, 24, .12); }
    .support[hidden] { display: none; }
    .note-pill, .rest-mark, .harm-block, .counter-mark {
      position: absolute; border: 0; border-radius: 999px;
    }
    .note-pill {
      background: #102033; color: #e7f6ff; font-size: 11px; padding: 0 6px;
      overflow: hidden; text-align: left; cursor: pointer;
    }
    .rest-mark {
      top: 96px; height: 8px; background: repeating-linear-gradient(90deg, #7d93a8 0 4px, transparent 4px 8px);
      border-radius: 0;
    }
    .harm-block { top: 16px; height: 22px; background: rgba(11, 127, 120, .35); }
    .counter-mark { top: 18px; height: 16px; background: #3a3f86; }
    .legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: .78rem; color: var(--muted); }
    .swatch { display: inline-block; width: 10px; height: 10px; border-radius: 99px; margin-right: 4px; }
    .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .study-card { border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px; }
    .study-card p { margin: 6px 0; }
    .table-scroll { overflow-x: auto; max-width: 100%; }
    table { width: 100%; border-collapse: collapse; font-size: .8rem; }
    th, td { text-align: left; padding: 7px 6px; border-bottom: 1px solid var(--line); white-space: nowrap; }
    .flow { display: flex; flex-wrap: wrap; gap: 8px; }
    .flow span { border: 1px solid var(--line); border-radius: 999px; padding: 4px 8px; font-size: .78rem; }
    audio, video { display: block; width: 100%; height: auto; margin: 10px 0 16px; background: #000; }
    .transport {
      position: static;
      display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
      margin-top: 28px; padding: 12px 16px; background: #050b12; border-top: 1px solid var(--line);
    }
    @media (max-width: 800px) {
      .intro, .cards { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header class="top">
    <a class="brand" href="index.html">Euphoric Trance Leads</a>
    <nav>
      <a href="#phrase">Phrase</a>
      <a href="#files">Files</a>
      <a href="#reading">Recorded reading</a>
      <a href="media.html">Stills</a>
      <a href="midi/arrangement.mid">Arrangement</a>
    </nav>
  </header>
  <main>
    <section class="intro">
      <div>
        <p class="kicker">Eight studies · phrase arcs, rests, transformed returns</p>
        <h1>Euphoric Trance Leads</h1>
        <p>Step through one monophonic lead at a time. The notes are read from the MIDI file for the study you pick. Harmony and counterphrase stay off until you ask for them. They are reference parts.</p>
        <p>__RANGE__</p>
        <p class="note">__PUBLICATION__</p>
      </div>
      <figure class="hero">
        <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of a broken lead phrase on a midnight field, with a rest in the arc and a violet return. Not a photograph of a studio or of performers.">
        <figcaption class="meta">Illustration of a phrase arc. Not a photograph of a session or of performers.</figcaption>
      </figure>
    </section>

    <section id="phrase">
      <h2>Lead phrase</h2>
      <div class="rail" id="rail"></div>
      <div class="switch">
        <button type="button" id="var-a" aria-pressed="true">Variation A</button>
        <button type="button" id="var-b" aria-pressed="false">Variation B</button>
      </div>
      <p class="kicker" id="study-id"></p>
      <h2 id="title">Lifted Fifth</h2>
      <p id="identity"></p>
      <p class="meta" id="facts"></p>
      <p id="rhythm"></p>
      <p id="voicing"></p>
      <p id="accent-copy"></p>
      <div class="phrases" id="phrases"></div>
      <div class="readout" id="readout">Reading the lead MIDI.</div>
      <div class="stepper">
        <button type="button" id="step-prev">Previous note</button>
        <button type="button" id="step-next">Next note</button>
      </div>
      <div class="scroller" id="scroller">
        <div class="sheet" id="sheet">
          <div class="ruler" id="ruler"></div>
          <div class="lane" id="lane"></div>
          <div class="support" id="harm-lane" hidden></div>
          <div class="support" id="counter-lane" hidden></div>
        </div>
      </div>
      <p class="legend">
        <span><i class="swatch" style="background:#102033"></i>lead note</span>
        <span><i class="swatch" style="background:#3ee0c8"></i>selected note</span>
        <span><i class="swatch" style="background:#7d93a8"></i>rest</span>
        <span><i class="swatch" style="background:#0b7f78"></i>harmonic reference</span>
        <span><i class="swatch" style="background:#3a3f86"></i>counterphrase</span>
      </p>
      <div class="toggles">
        <button type="button" id="harm-toggle" aria-pressed="false">Harmonic reference</button>
        <button type="button" id="counter-toggle" aria-pressed="false">Counterphrase</button>
      </div>
      <p class="note" id="status"></p>
      <p class="note" id="limits"></p>
      <p class="note" id="departures"></p>
    </section>

    <h2>Studies</h2>
    <div class="cards">__STUDIES__</div>

    <h2>Set map</h2>
    <ul>__MAP__</ul>

    <h2>File contract</h2>
    <div class="flow">
      <span>Canonical score</span><span>MIDI</span><span>Reopened validation</span><span>MP3 preview</span><span>Film</span>
    </div>
    <div class="flow">
      <span>Stills</span><span>Social drafts</span><span>Catalog</span><span>This page</span>
    </div>
    <p class="note"><a href="articles/medium-draft-Cursor.md">Article draft</a> · <a href="articles/medium-paste-Cursor.txt">plain text</a> · <a href="score/canonical-score-Cursor.json">canonical score</a></p>
    <p>__WARNING__</p>

    <h2 id="files">Files</h2>
    <p class="meta">Validation __RESULT__. Core leads __CORE__. Reference files __REF__. <a href="midi/validation-Cursor.json">validation report</a> · <a href="catalog/catalog-Cursor.json">catalog</a> · <a href="midi/arrangement.mid">arrangement.mid</a></p>
    <div class="table-scroll">
      <table>
        <thead><tr><th>Part</th><th>Role</th><th>Var</th><th>Count</th><th>BPM</th><th>Notes</th></tr></thead>
        <tbody>__ROWS__</tbody>
      </table>
    </div>

    <section id="reading">
      <p class="kicker">Recorded reading</p>
      <h2>Study 01, variation A, all 16 bars</h2>
      <p>This is a separate file from the phrase player above. The MP3 is __SECONDS__ seconds. __PREVIEW_LINE__. The film is __FILM_SECONDS__ seconds and shows __ON_PICTURE__.</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a> · <a href="preview/preview-manifest-Cursor.txt">preview manifest</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
      <p><a href="film/preview.mp4">film/preview.mp4</a> · <a href="film/preview.vtt">film/preview.vtt</a> · <a href="media.html">stills</a></p>
    </section>
    <p>__PROGRAM__</p>
    <p>__AUDITION__</p>
  </main>
  <div class="transport">
    <button type="button" id="play">Play lead</button>
    <span id="transport-label">Space plays and stops. J and K change study.</span>
  </div>
  <script id="pack" type="application/json">__DATA__</script>
  <script>
    const pack = JSON.parse(document.getElementById("pack").textContent);
    const rail = document.getElementById("rail");
    const phrases = document.getElementById("phrases");
    const scroller = document.getElementById("scroller");
    const sheet = document.getElementById("sheet");
    const ruler = document.getElementById("ruler");
    const lane = document.getElementById("lane");
    const harmLane = document.getElementById("harm-lane");
    const counterLane = document.getElementById("counter-lane");
    const readout = document.getElementById("readout");
    const status = document.getElementById("status");
    let studyId = "s01";
    let variation = "a";
    let leadNotes = [];
    let harmNotes = [];
    let counterNotes = [];
    let cursor = 0;
    let showHarm = false;
    let showCounter = false;
    let audio = null;
    let playing = false;
    let followId = 0;
    let sheetWidth = 1200;

    function study() {
      return pack.studies.find((item) => item.id === studyId);
    }
    function pitchName(pitch) {
      return study().spell[pitch % 12] + (Math.floor(pitch / 12) - 1);
    }
    function readVlq(view, offset) {
      let value = 0;
      let byte = 0;
      do {
        byte = view.getUint8(offset);
        offset += 1;
        value = (value << 7) | (byte & 0x7f);
      } while (byte & 0x80);
      return [value, offset];
    }
    function parseMidi(buffer) {
      const view = new DataView(buffer);
      if (String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3)) !== "MThd" || view.getUint16(12) !== 960) {
        throw new Error("unexpected MIDI header");
      }
      const tracks = view.getUint16(10);
      let offset = 14;
      const notes = [];
      for (let track = 0; track < tracks; track += 1) {
        if (String.fromCharCode(view.getUint8(offset), view.getUint8(offset + 1), view.getUint8(offset + 2), view.getUint8(offset + 3)) !== "MTrk") {
          throw new Error("missing track");
        }
        const length = view.getUint32(offset + 4);
        offset += 8;
        const end = offset + length;
        let tick = 0;
        let running = 0;
        const open = new Map();
        while (offset < end) {
          let delta;
          [delta, offset] = readVlq(view, offset);
          tick += delta;
          let byte = view.getUint8(offset);
          if (byte >= 0x80) {
            running = byte;
            offset += 1;
          }
          if (running === 0xff) {
            offset += 1;
            let metaLen;
            [metaLen, offset] = readVlq(view, offset);
            offset += metaLen;
            continue;
          }
          const kind = running & 0xf0;
          const data1 = byte < 0x80 ? byte : view.getUint8(offset);
          if (byte >= 0x80) offset += 1;
          let data2 = 0;
          if (kind !== 0xc0 && kind !== 0xd0) {
            data2 = view.getUint8(offset);
            offset += 1;
          }
          const key = (running & 0x0f) + ":" + data1;
          if (kind === 0x90 && data2 > 0) open.set(key, { tick: tick, velocity: data2 });
          else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {
            const started = open.get(key);
            if (started) {
              notes.push({ pitch: data1, start: started.tick, duration: tick - started.tick, velocity: started.velocity });
              open.delete(key);
            }
          }
        }
      }
      notes.sort((a, b) => a.start - b.start || a.pitch - b.pitch);
      return notes;
    }
    function partPath(role) {
      const found = pack.parts.find((part) => part.study_id === studyId && part.role === role && part.variation === variation);
      if (!found) throw new Error("missing " + role);
      return found.path;
    }
    function renderCopy() {
      const item = study();
      document.getElementById("title").textContent = item.title;
      document.getElementById("study-id").textContent = item.id;
      document.getElementById("identity").textContent = item.identity;
      document.getElementById("facts").textContent = item.bpm + " BPM · " + item.bars + " bars · " + item.collection + " · tonic " + item.tonic;
      document.getElementById("rhythm").textContent = item.harmonic_rhythm;
      document.getElementById("voicing").textContent = item.voicing;
      document.getElementById("accent-copy").textContent = item.accent;
      document.getElementById("limits").textContent = item.limitations;
      document.getElementById("departures").textContent = item.departures.length ? item.departures.join(" ") : "No pitch in this study is flagged as a departure.";
      document.getElementById("transport-label").textContent = item.title + " " + variation.toUpperCase() + " · Space plays and stops · J and K change study";
      for (const button of rail.querySelectorAll("button")) button.setAttribute("aria-pressed", button.dataset.id === studyId ? "true" : "false");
      document.getElementById("var-a").setAttribute("aria-pressed", variation === "a" ? "true" : "false");
      document.getElementById("var-b").setAttribute("aria-pressed", variation === "b" ? "true" : "false");
      phrases.innerHTML = "";
      item.phrases.forEach((phrase) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = phrase.name;
        button.addEventListener("click", () => selectPhrase(phrase));
        phrases.appendChild(button);
      });
    }
    function selectPhrase(phrase) {
      const start = phrase.start_bar * 3840;
      const end = start + phrase.bars * 3840;
      const index = leadNotes.findIndex((note) => note.start >= start && note.start < end);
      cursor = index < 0 ? 0 : index;
      draw();
      const note = leadNotes[cursor];
      if (note) scroller.scrollLeft = Math.max(0, (note.start / (study().bars * 3840)) * sheetWidth - 24);
    }
    function describe() {
      if (!leadNotes.length) {
        readout.textContent = "No lead notes loaded.";
        return;
      }
      const note = leadNotes[cursor];
      const bar = Math.floor(note.start / 3840) + 1;
      const beat = ((note.start % 3840) / 960).toFixed(2);
      const previousEnd = cursor === 0 ? 0 : leadNotes[cursor - 1].start + leadNotes[cursor - 1].duration;
      const restBeats = ((note.start - previousEnd) / 960).toFixed(2);
      readout.textContent = "Note " + (cursor + 1) + " of " + leadNotes.length + ". " + pitchName(note.pitch) + ". Bar " + bar + ", beat " + beat + ". Duration " + (note.duration / 960).toFixed(2) + " beats. Rest before it: " + restBeats + " beats.";
    }
    function place(node, start, duration, container) {
      node.style.left = (start / container) * sheetWidth + "px";
      node.style.width = Math.max(4, (duration / container) * sheetWidth - 2) + "px";
    }
    function draw() {
      const item = study();
      const container = item.bars * 3840;
      sheetWidth = Math.max(880, item.bars * 168);
      sheet.style.width = sheetWidth + "px";
      ruler.innerHTML = "";
      lane.innerHTML = "";
      harmLane.innerHTML = "";
      counterLane.innerHTML = "";
      let bar = 0;
      item.changes.forEach((name, index) => {
        const span = item.change_bars[index];
        const mark = document.createElement("div");
        mark.className = "change";
        mark.textContent = name;
        mark.style.left = (bar / item.bars) * sheetWidth + "px";
        mark.style.width = (span / item.bars) * sheetWidth + "px";
        ruler.appendChild(mark);
        bar += span;
      });
      let previousEnd = 0;
      leadNotes.forEach((note, index) => {
        if (note.start > previousEnd) {
          const rest = document.createElement("div");
          rest.className = "rest-mark";
          rest.title = "rest";
          place(rest, previousEnd, note.start - previousEnd, container);
          lane.appendChild(rest);
        }
        const pill = document.createElement("button");
        pill.type = "button";
        pill.className = "note-pill" + (index === cursor ? " on" : "");
        pill.textContent = pitchName(note.pitch);
        pill.title = pitchName(note.pitch) + " · velocity " + note.velocity;
        pill.setAttribute("aria-current", index === cursor ? "true" : "false");
        const low = 60;
        const high = 84;
        const y = 12 + (1 - (note.pitch - low) / (high - low)) * 150;
        place(pill, note.start, note.duration, container);
        pill.style.top = y + "px";
        pill.style.height = "28px";
        pill.addEventListener("click", () => { cursor = index; draw(); });
        lane.appendChild(pill);
        previousEnd = note.start + note.duration;
      });
      if (previousEnd < container) {
        const rest = document.createElement("div");
        rest.className = "rest-mark";
        place(rest, previousEnd, container - previousEnd, container);
        lane.appendChild(rest);
      }
      harmLane.hidden = !showHarm;
      counterLane.hidden = !showCounter;
      if (showHarm) {
        const placed = [];
        harmNotes.forEach((note) => {
          const end = note.start + note.duration;
          let laneIndex = 0;
          while (placed.some((other) => other.lane === laneIndex && note.start < other.end && other.start < end)) laneIndex += 1;
          placed.push({ lane: laneIndex, start: note.start, end: end });
          const block = document.createElement("div");
          block.className = "harm-block";
          block.title = pitchName(note.pitch);
          place(block, note.start, note.duration, container);
          block.style.top = (4 + laneIndex * 16) + "px";
          block.style.height = "12px";
          harmLane.appendChild(block);
        });
      }
      if (showCounter) {
        counterNotes.forEach((note) => {
          const block = document.createElement("div");
          block.className = "counter-mark";
          block.title = pitchName(note.pitch);
          place(block, note.start, note.duration, container);
          counterLane.appendChild(block);
        });
      }
      describe();
      status.textContent = leadNotes.length + " lead notes read from the MIDI. " + (showHarm ? harmNotes.length + " harmonic notes. " : "") + (showCounter ? counterNotes.length + " counterphrase notes." : "");
    }
    async function loadStudy() {
      stopPlayback();
      cursor = 0;
      renderCopy();
      readout.textContent = "Reading the lead MIDI.";
      try {
        const leadRes = await fetch(partPath("principal-lead"));
        const harmRes = await fetch(partPath("harmonic-reference"));
        const counterRes = await fetch(partPath("counterphrase"));
        if (!leadRes.ok || !harmRes.ok || !counterRes.ok) throw new Error("MIDI request failed");
        leadNotes = parseMidi(await leadRes.arrayBuffer());
        harmNotes = parseMidi(await harmRes.arrayBuffer());
        counterNotes = parseMidi(await counterRes.arrayBuffer());
        draw();
      } catch (error) {
        leadNotes = [];
        harmNotes = [];
        counterNotes = [];
        status.textContent = "The MIDI did not load. " + error.message;
        readout.textContent = "The lead MIDI did not load.";
      }
    }
    function stepNote(direction) {
      if (!leadNotes.length) return;
      cursor = (cursor + direction + leadNotes.length) % leadNotes.length;
      draw();
      const note = leadNotes[cursor];
      scroller.scrollLeft = Math.max(0, (note.start / (study().bars * 3840)) * sheetWidth - 24);
    }
    function freq(pitch) {
      return 440 * Math.pow(2, (pitch - 69) / 12);
    }
    function schedule(ctx, note, origin, amount) {
      const item = study();
      const seconds = (tick) => tick / 960 * item.tempo_us / 1000000;
      const when = origin + seconds(note.start);
      const duration = Math.max(0.05, seconds(note.duration));
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.value = freq(note.pitch);
      const level = amount * (note.velocity / 110);
      const attack = Math.min(0.03, duration * 0.2);
      gain.gain.setValueAtTime(0.0001, when);
      gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, level), when + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(when);
      osc.stop(when + duration + 0.02);
    }
    function stopPlayback() {
      playing = false;
      cancelAnimationFrame(followId);
      if (audio) audio.close();
      audio = null;
      document.getElementById("play").textContent = "Play lead";
    }
    function playLead() {
      if (!leadNotes.length) return;
      stopPlayback();
      const ctx = new AudioContext();
      audio = ctx;
      playing = true;
      document.getElementById("play").textContent = "Stop";
      const origin = ctx.currentTime + 0.05;
      leadNotes.forEach((note) => schedule(ctx, note, origin, 0.08));
      if (showHarm) harmNotes.forEach((note) => schedule(ctx, note, origin, 0.03));
      if (showCounter) counterNotes.forEach((note) => schedule(ctx, note, origin, 0.04));
      const item = study();
      const container = item.bars * 4 * 60 / item.bpm;
      const follow = () => {
        if (!playing || !audio) return;
        if (audio.currentTime - origin < container) followId = requestAnimationFrame(follow);
        else stopPlayback();
      };
      follow();
    }
    function stepStudy(direction) {
      const index = pack.studies.findIndex((item) => item.id === studyId);
      studyId = pack.studies[(index + direction + pack.studies.length) % pack.studies.length].id;
      loadStudy();
    }
    pack.studies.forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.id = item.id;
      button.textContent = item.id.slice(1) + " " + item.title;
      button.addEventListener("click", () => { studyId = item.id; loadStudy(); });
      rail.appendChild(button);
    });
    document.getElementById("var-a").addEventListener("click", () => { variation = "a"; loadStudy(); });
    document.getElementById("var-b").addEventListener("click", () => { variation = "b"; loadStudy(); });
    document.getElementById("step-prev").addEventListener("click", () => stepNote(-1));
    document.getElementById("step-next").addEventListener("click", () => stepNote(1));
    document.getElementById("play").addEventListener("click", () => { if (playing) stopPlayback(); else playLead(); });
    document.getElementById("harm-toggle").addEventListener("click", () => {
      showHarm = !showHarm;
      document.getElementById("harm-toggle").setAttribute("aria-pressed", showHarm ? "true" : "false");
      if (leadNotes.length) draw();
    });
    document.getElementById("counter-toggle").addEventListener("click", () => {
      showCounter = !showCounter;
      document.getElementById("counter-toggle").setAttribute("aria-pressed", showCounter ? "true" : "false");
      if (leadNotes.length) draw();
    });
    window.addEventListener("keydown", (event) => {
      const target = event.target;
      if (target && target.closest && target.closest("video, audio, input, textarea")) return;
      if (event.code === "Space") { event.preventDefault(); if (playing) stopPlayback(); else playLead(); }
      else if (event.key === "j" || event.key === "J") stepStudy(-1);
      else if (event.key === "k" || event.key === "K") stepStudy(1);
      else if (event.key === "ArrowRight") { event.preventDefault(); stepNote(1); }
      else if (event.key === "ArrowLeft") { event.preventDefault(); stepNote(-1); }
    });
    loadStudy();
  </script>
</body>
</html>
"""
