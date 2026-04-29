#!/usr/bin/env python3
"""
Generate 8-hour sleep affirmations video with:
- Starfield background (Pillow-generated)
- Affirmation text overlay cycling every 10 seconds
- ElevenLabs River voice audio
"""

import json, os, subprocess, random, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import imageio_ffmpeg
FFMPEG     = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR    = Path(__file__).parent.parent / "output_videos"
TEMPLATE   = Path(__file__).parent.parent / "templates" / "success_career_8hr.json"
FONT_PATH  = "/System/Library/Fonts/Supplemental/Arial.ttf"
AUDIO      = OUT_DIR / "audio_8hr_river.aac"
OUT_MP4    = OUT_DIR / "success_career_8hr_river_visual.mp4"
DURATION   = 28800  # 8 hours


def generate_starfield(width=1920, height=1080, seed=42) -> Path:
    random.seed(seed)
    bg_color = (5, 5, 20)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Subtle nebula — soft radial gradient in deep blue/purple
    cx, cy = width // 2, height // 2
    for r in range(min(width, height) // 2, 0, -4):
        alpha = int(8 * (1 - r / (min(width, height) / 2)))
        if alpha <= 0:
            continue
        nebula = Image.new("RGB", (width, height), bg_color)
        nd = ImageDraw.Draw(nebula)
        nd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(10 + alpha, 8 + alpha // 2, 30 + alpha))
        img = Image.blend(img, nebula, 0.04)

    draw = ImageDraw.Draw(img)

    # Stars — varied brightness and size
    for _ in range(2800):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        b = random.randint(140, 255)
        size = random.choices([1, 2, 3], weights=[78, 18, 4])[0]
        tint = random.choice(["cool", "warm", "white"])
        if tint == "cool":
            color = (max(0, b - 30), max(0, b - 10), b)
        elif tint == "warm":
            color = (b, max(0, b - 20), max(0, b - 40))
        else:
            color = (b, b, b)
        if size == 1:
            draw.point((x, y), fill=color)
        else:
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

    # Soft glow pass
    glow = img.filter(ImageFilter.GaussianBlur(radius=1))
    img = Image.blend(img, glow, 0.12)

    out = OUT_DIR / "starfield.png"
    img.save(str(out))
    print(f"  Starfield saved: {out}")
    return out


def get_affirmations(template: dict) -> list:
    result = []
    for section in template["sections"]:
        if "affirmations" in section:
            for a in section["affirmations"]:
                result.append(a)
    return result


def escape_ff(text: str) -> str:
    """Escape text for ffmpeg drawtext filter."""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "’")   # replace straight apostrophe with curly
    text = text.replace(":", "\\:")
    text = text.replace("%", "%%")
    return text


def build_video(starfield: Path, affirmations: list):
    display_secs = 10
    cycle = len(affirmations) * display_secs

    # Build one drawtext entry per affirmation
    dt_parts = []
    for i, text in enumerate(affirmations):
        t0 = i * display_secs
        t1 = t0 + display_secs
        safe = escape_ff(text)
        enable = f"lt(mod(t\\,{cycle})\\,{t1})*gte(mod(t\\,{cycle})\\,{t0})"
        dt_parts.append(
            f"drawtext=fontfile='{FONT_PATH}'"
            f":text='{safe}'"
            f":x=(w-text_w)/2"
            f":y=(h-text_h)/2+20"
            f":fontcolor=white"
            f":fontsize=46"
            f":alpha=0.92"
            f":shadowcolor=black@0.6"
            f":shadowx=2:shadowy=2"
            f":enable='{enable}'"
        )

    # Channel watermark at bottom
    watermark = (
        f"drawtext=fontfile='{FONT_PATH}'"
        f":text='Sleep Money Affirmations'"
        f":x=(w-text_w)/2:y=h-60"
        f":fontcolor=white@0.35:fontsize=24"
    )

    dt_chain = ",".join(dt_parts) + "," + watermark

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(starfield),        # static starfield
        "-i", str(AUDIO),                           # 8hr audio
        "-filter_complex", f"[0:v]{dt_chain}[vout]",
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "33",
        "-r", "1",
        "-c:a", "copy",
        "-t", str(DURATION),
        "-shortest",
        str(OUT_MP4)
    ]

    print(f"Encoding {DURATION // 3600}h video with starfield + text overlay...")
    print("  This will take a few minutes...")
    subprocess.run(cmd, check=True)
    size = OUT_MP4.stat().st_size / 1024 / 1024
    print(f"  Done! {size:.0f} MB → {OUT_MP4}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    template = json.loads(TEMPLATE.read_text())
    affirmations = get_affirmations(template)
    print(f"Loaded {len(affirmations)} unique affirmations")

    print("Generating starfield background...")
    starfield = generate_starfield()

    build_video(starfield, affirmations)
    print(f"\nVideo ready: {OUT_MP4}")


if __name__ == "__main__":
    main()
