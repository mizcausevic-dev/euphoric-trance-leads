"""Procedural raster artwork and ffmpeg media steps.

The painter is original and deterministic. It draws a broken lead phrase: an
arc that rises, rests, peaks, and returns in a different color. It is an
illustration, not a photograph of a session or of performers.

DejaVu Sans Bold is used only to rasterize the disclosure into the film and the
poster. The font file is not shipped.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ON_PICTURE = "preview, not master"


def _clamp(value: int) -> int:
    return 0 if value < 0 else 255 if value > 255 else value


def _put(pixels: bytearray, width: int, height: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    if not 0 <= x < width or not 0 <= y < height:
        return
    index = (y * width + x) * 3
    pixels[index] = color[0]
    pixels[index + 1] = color[1]
    pixels[index + 2] = color[2]


def _ink(kind: str) -> tuple[int, int, int]:
    if kind == "peak":
        return (186, 246, 255)
    if kind == "return":
        return (154, 156, 255)
    return (46, 214, 204)


def paint(width: int, height: int, framing: str) -> bytes:
    """Midnight field, staff, and a broken phrase arc. Square and wide differ."""
    pixels = bytearray(width * height * 3)
    for y in range(height):
        shade = y / max(1, height - 1)
        red = int(6 + 16 * (1 - shade))
        green = int(12 + 24 * (1 - shade))
        blue = int(26 + 40 * (1 - shade))
        row = y * width * 3
        for x in range(width):
            pixels[row + x * 3] = red
            pixels[row + x * 3 + 1] = green
            pixels[row + x * 3 + 2] = blue
    for mark in range(1, 17):
        x = int(width * mark / 17)
        for y in range(int(height * 0.16), int(height * 0.86)):
            _put(pixels, width, height, x, y, (16, 30, 48))
    for line in range(5):
        y = int(height * (0.28 + line * 0.09))
        for x in range(int(width * 0.07), int(width * 0.93)):
            _put(pixels, width, height, x, y, (24, 46, 68))
    if framing == "square":
        segments = [
            (0.18, 0.68, 0.36, 0.46, "ice"),
            (0.44, 0.52, 0.60, 0.30, "peak"),
            (0.68, 0.44, 0.84, 0.64, "return"),
        ]
        horizon = [(0.18, 0.78), (0.40, 0.74), (0.62, 0.80), (0.84, 0.76)]
    else:
        segments = [
            (0.08, 0.64, 0.24, 0.44, "ice"),
            (0.31, 0.50, 0.46, 0.32, "ice"),
            (0.53, 0.38, 0.68, 0.22, "peak"),
            (0.75, 0.46, 0.93, 0.62, "return"),
        ]
        horizon = [(0.08, 0.80), (0.28, 0.76), (0.52, 0.82), (0.74, 0.74), (0.93, 0.78)]
    for x0, y0, x1, y1, kind in segments:
        steps = max(12, int(abs(x1 - x0) * width))
        color = _ink(kind)
        for step in range(steps + 1):
            blend = step / steps
            x = int((x0 + (x1 - x0) * blend) * (width - 1))
            y = int((y0 + (y1 - y0) * blend) * (height - 1))
            for dy in range(-4, 5):
                for dx in range(-2, 3):
                    if dx * dx + dy * dy > 18:
                        continue
                    _put(pixels, width, height, x + dx, y + dy, color)
        for end_x, end_y in ((x0, y0), (x1, y1)):
            cx = int(end_x * (width - 1))
            cy = int(end_y * (height - 1))
            for dy in range(-7, 8):
                for dx in range(-7, 8):
                    if dx * dx + dy * dy <= 36:
                        _put(pixels, width, height, cx + dx, cy + dy, color)
    for index in range(len(horizon) - 1):
        x0, y0 = horizon[index]
        x1, y1 = horizon[index + 1]
        steps = max(8, int(abs(x1 - x0) * width))
        for step in range(steps + 1):
            blend = step / steps
            x = int((x0 + (x1 - x0) * blend) * (width - 1))
            y = int((y0 + (y1 - y0) * blend) * (height - 1))
            _put(pixels, width, height, x, y, (64, 104, 140))
            _put(pixels, width, height, x, y + 1, (64, 104, 140))
    for sx, sy in ((0.12, 0.12), (0.22, 0.18), (0.41, 0.10), (0.63, 0.14), (0.81, 0.11), (0.9, 0.2)):
        _put(pixels, width, height, int(sx * width), int(sy * height), (170, 210, 220))
    return bytes(pixels)

def write_ppm(path: Path, width: int, height: int, rgb: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            + " ".join(command)
            + "\n"
            + completed.stderr[-2000:]
        )


def ppm_to_jpeg(ppm: Path, jpeg: Path, quality: int = 3) -> None:
    jpeg.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(ppm), "-frames:v", "1", "-q:v", str(quality), str(jpeg)])


def draw_disclosure(source: Path, dest: Path, textfile: Path) -> list[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf",
        (
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-frames:v", "1",
        "-q:v", "3",
        str(dest),
    ]
    run(command)
    return command


def encode_mp3(wav: Path, mp3: Path) -> list[str]:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3),
    ]
    run(command)
    return command


def encode_film(plate: Path, mp3: Path, mp4: Path, textfile: Path, duration: str) -> list[str]:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(plate),
        "-i", str(mp3),
        "-t", duration,
        "-vf",
        (
            "scale=1280:720,"
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4),
    ]
    run(command)
    return command


def derive_social(hero: Path, square: Path, portrait: Path, card: Path) -> dict[str, list[str]]:
    portrait.parent.mkdir(parents=True, exist_ok=True)
    card.parent.mkdir(parents=True, exist_ok=True)
    portrait_cmd = [
        "ffmpeg", "-y", "-i", str(square),
        "-vf", "crop=864:1080:108:0,scale=1080:1350",
        "-q:v", "3",
        str(portrait),
    ]
    card_cmd = [
        "ffmpeg", "-y", "-i", str(hero),
        "-vf", "scale=1600:900",
        "-q:v", "3",
        str(card),
    ]
    run(portrait_cmd)
    run(card_cmd)
    return {"portrait": portrait_cmd, "card": card_cmd}
