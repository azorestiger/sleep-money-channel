#!/usr/bin/env python3
"""
Generate 8-hour sleep affirmations video using ElevenLabs TTS + ffmpeg.
"""

import json, os, subprocess, time, urllib.request, urllib.error
from pathlib import Path

API_KEY    = "sk_2b10cb0ae0378f907827112def4d0c23813b3853a448bee9"
VOICE_ID   = "SAz9YHcvj6GT2YYXdXww"  # River
MODEL_ID   = "eleven_turbo_v2_5"
OUT_DIR    = Path(__file__).parent.parent / "output_videos"
TEMPLATE   = Path(__file__).parent.parent / "templates" / "success_career_8hr.json"

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

VOICE_SETTINGS = {
    "stability": 0.80,
    "similarity_boost": 0.75,
    "style": 0.25,
    "use_speaker_boost": True
}


def build_sections(template):
    """Return list of text sections, each safe to send to ElevenLabs (~4000 chars)."""
    sections = []
    for sec in template["sections"]:
        if "content" in sec:
            sections.append(sec["content"])
        if "affirmations" in sec:
            chunk, chunk_len = [], 0
            for _ in range(sec.get("repeat_times", 1)):
                for a in sec["affirmations"]:
                    line = a + ". "
                    if chunk_len + len(line) > 3800:
                        sections.append(" ".join(chunk))
                        chunk, chunk_len = [], 0
                    chunk.append(line.strip())
                    chunk_len += len(line)
            if chunk:
                sections.append(" ".join(chunk))
    return sections


def tts_chunk(text, out_mp3, retries=3):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    payload = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": VOICE_SETTINGS
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    })
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                out_mp3.write_bytes(resp.read())
            return
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code} on attempt {attempt+1}: {e.read().decode()}")
            if attempt < retries - 1:
                time.sleep(3)
                raise


def generate_segment(sections, segment_mp3):
    print(f"Generating {len(sections)} TTS chunks via ElevenLabs (River)...")
    chunk_files = []
    for i, text in enumerate(sections):
        cf = OUT_DIR / f"chunk_{i:03d}.mp3"
        print(f"  [{i+1}/{len(sections)}] {len(text)} chars")
        tts_chunk(text, cf)
        chunk_files.append(cf)
        time.sleep(0.3)  # be gentle on the API

    concat_txt = OUT_DIR / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{cf}'" for cf in chunk_files))

    print("Stitching chunks...")
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c:a", "libmp3lame", str(segment_mp3)
    ], check=True, capture_output=True)
    print(f"  Segment: {segment_mp3.stat().st_size / 1024 / 1024:.1f} MB")


def loop_to_8hr(segment_mp3, looped_aac):
    print("Looping to 8 hours...")
    subprocess.run([
        FFMPEG, "-y", "-stream_loop", "-1", "-i", str(segment_mp3),
        "-t", "28800", "-c:a", "aac", "-b:a", "128k", str(looped_aac)
    ], check=True, capture_output=True)
    print(f"  8hr audio: {looped_aac.stat().st_size / 1024 / 1024:.0f} MB")


def encode_video(looped_aac, out_mp4):
    print("Encoding video...")
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi", "-i", "color=c=0x050510:s=1920x1080:r=1",
        "-i", str(looped_aac),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "35",
        "-c:a", "copy", "-t", "28800", "-shortest",
        str(out_mp4)
    ], check=True)
    print(f"  Video: {out_mp4.stat().st_size / 1024 / 1024:.0f} MB")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    template = json.loads(TEMPLATE.read_text())

    sections    = build_sections(template)
    segment_mp3 = OUT_DIR / "segment_river.mp3"
    looped_aac  = OUT_DIR / "audio_8hr_river.aac"
    out_mp4     = OUT_DIR / "success_career_8hr_river.mp4"

    generate_segment(sections, segment_mp3)
    loop_to_8hr(segment_mp3, looped_aac)
    encode_video(looped_aac, out_mp4)

    print(f"\nDone! Video ready: {out_mp4}")


if __name__ == "__main__":
    main()
