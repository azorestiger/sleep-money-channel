#!/usr/bin/env python3
"""
Regenerate the Success & Career video with a guided relaxation intro
prepended before the affirmations loop.
"""

import json, os, subprocess, time, urllib.request
from pathlib import Path

API_KEY   = "sk_2b10cb0ae0378f907827112def4d0c23813b3853a448bee9"
VOICE_ID  = "SAz9YHcvj6GT2YYXdXww"  # River
MODEL_ID  = "eleven_turbo_v2_5"
OUT_DIR   = Path(__file__).parent.parent / "output_videos"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
DURATION  = 28800  # 8 hours

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

GUIDED_INTRO = """Find a comfortable position and allow your body to begin to relax.
Take a long, slow breath in... and gently breathe out.
With every breath, you are becoming more and more deeply relaxed.
There is nothing you need to do right now. Nowhere you need to be.
Simply allow yourself to drift... deeper... and deeper... into a beautiful, peaceful sleep.
As you relax completely, your mind becomes open and receptive,
ready to receive these powerful truths about who you are and what you are capable of creating.
You are safe. You are supported.
And as you sleep tonight, your subconscious mind will absorb every word that follows,
planting the seeds of unlimited success, abundance, and prosperity deep within you.
Simply breathe... and let go..."""

VOICE_SETTINGS_INTRO = {
    "stability": 0.88,
    "similarity_boost": 0.75,
    "style": 0.10,
    "use_speaker_boost": True
}

VOICE_SETTINGS_AFFIRMATIONS = {
    "stability": 0.80,
    "similarity_boost": 0.75,
    "style": 0.25,
    "use_speaker_boost": True
}


def tts(text: str, out_mp3: Path, voice_settings: dict):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    payload = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": voice_settings
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        out_mp3.write_bytes(resp.read())
    print(f"  {out_mp3.name}: {out_mp3.stat().st_size / 1024:.0f} KB")


def concat_audio(files: list, out: Path):
    concat_txt = OUT_DIR / "_concat.txt"
    concat_txt.write_text("\n".join(f"file '{f}'" for f in files))
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c:a", "libmp3lame", str(out)
    ], check=True, capture_output=True)


def build_full_audio(intro_mp3: Path, segment_mp3: Path, out_aac: Path):
    """Combine: intro (once) + affirmations looped to fill 8 hours."""
    # Get intro duration
    result = subprocess.run([
        FFMPEG, "-i", str(intro_mp3), "-f", "null", "-"
    ], capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            parts = line.strip().split("Duration:")[1].split(",")[0].strip().split(":")
            intro_secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            break

    affirmations_secs = DURATION - intro_secs
    print(f"  Intro: {intro_secs:.0f}s | Affirmations fill: {affirmations_secs:.0f}s")

    # Loop affirmations to fill remaining time
    looped_mp3 = OUT_DIR / "_affirmations_looped.mp3"
    subprocess.run([
        FFMPEG, "-y", "-stream_loop", "-1", "-i", str(segment_mp3),
        "-t", str(affirmations_secs), "-c:a", "libmp3lame", str(looped_mp3)
    ], check=True, capture_output=True)

    # Concatenate intro + looped affirmations
    combined_mp3 = OUT_DIR / "_combined.mp3"
    concat_audio([intro_mp3, looped_mp3], combined_mp3)

    # Convert to AAC
    subprocess.run([
        FFMPEG, "-y", "-i", str(combined_mp3),
        "-c:a", "aac", "-b:a", "128k", str(out_aac)
    ], check=True, capture_output=True)
    print(f"  Full 8hr audio: {out_aac.stat().st_size / 1024 / 1024:.0f} MB")


def get_affirmations():
    template = json.loads(
        (Path(__file__).parent.parent / "templates" / "success_career_8hr.json").read_text()
    )
    return [a for s in template["sections"] if "affirmations" in s for a in s["affirmations"]]


def escape_ff(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "%%")


def encode_video(audio_aac: Path, starfield: Path, affirmations: list, out_mp4: Path):
    display_secs = 10
    cycle = len(affirmations) * display_secs
    dt_parts = []
    for i, text in enumerate(affirmations):
        t0 = i * display_secs
        t1 = t0 + display_secs
        safe = escape_ff(text)
        enable = f"lt(mod(t\\,{cycle})\\,{t1})*gte(mod(t\\,{cycle})\\,{t0})"
        dt_parts.append(
            f"drawtext=fontfile='{FONT_PATH}':text='{safe}'"
            f":x=(w-text_w)/2:y=(h-text_h)/2+20"
            f":fontcolor=white:fontsize=46:alpha=0.92"
            f":shadowcolor=black@0.6:shadowx=2:shadowy=2"
            f":enable='{enable}'"
        )
    watermark = (
        f"drawtext=fontfile='{FONT_PATH}':text='Sleep Money Affirmations'"
        f":x=(w-text_w)/2:y=h-60:fontcolor=white@0.35:fontsize=24"
    )
    dt_chain = ",".join(dt_parts) + "," + watermark

    print(f"Encoding final video → {out_mp4.name}...")
    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1", "-i", str(starfield),
        "-i", str(audio_aac),
        "-filter_complex", f"[0:v]{dt_chain}[vout]",
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "33", "-r", "1",
        "-c:a", "copy", "-t", str(DURATION), "-shortest",
        str(out_mp4)
    ], check=True)
    print(f"  Done! {out_mp4.stat().st_size / 1024 / 1024:.0f} MB → {out_mp4}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    starfield = OUT_DIR / "starfield.png"
    intro_mp3  = OUT_DIR / "guided_intro.mp3"
    segment_mp3 = OUT_DIR / "segment_river.mp3"
    full_aac    = OUT_DIR / "audio_8hr_with_intro.aac"
    final_mp4   = OUT_DIR / "success_career_8hr_final.mp4"

    print("Step 1: Generating guided relaxation intro (River, slower/calmer)...")
    tts(GUIDED_INTRO, intro_mp3, VOICE_SETTINGS_INTRO)

    print("\nStep 2: Building full 8-hour audio (intro + looped affirmations)...")
    build_full_audio(intro_mp3, segment_mp3, full_aac)

    print("\nStep 3: Encoding video with starfield + text overlay...")
    affirmations = get_affirmations()
    encode_video(full_aac, starfield, affirmations, final_mp4)

    print(f"\nAll done! Final video: {final_mp4}")


if __name__ == "__main__":
    main()
