#!/usr/bin/env python3
"""
Build affirmations audio from template using macOS `say` TTS.
Generates a loopable segment, then uses ffmpeg to extend it to full duration.
"""

import json
import subprocess
import os
import sys


FFMPEG = "/Users/azorestiger/Library/Python/3.9/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
VOICE = "Samantha"
RATE = 120  # words per minute — slow, meditative pace

PAUSE_SHORT = "[[slnc 1500]]"   # between affirmations
PAUSE_LONG  = "[[slnc 3000]]"   # between sections


def build_script(template: dict) -> str:
    parts = []
    for section in template["sections"]:
        name = section["section_name"]
        parts.append(PAUSE_LONG)

        if "content" in section:
            parts.append(section["content"])
            parts.append(PAUSE_LONG)

        if "affirmations" in section:
            for _ in range(section.get("repeat_times", 1)):
                for affirmation in section["affirmations"]:
                    parts.append(affirmation)
                    parts.append(PAUSE_SHORT)
                parts.append(PAUSE_LONG)

    return "  ".join(parts)


def generate_segment(script_text: str, out_aiff: str):
    print(f"Generating TTS narration → {out_aiff}")
    result = subprocess.run(
        ["say", "-v", VOICE, "-r", str(RATE), "-o", out_aiff, script_text],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("say error:", result.stderr)
        sys.exit(1)
    size = os.path.getsize(out_aiff)
    print(f"  Segment: {size / 1024 / 1024:.1f} MB")


def aiff_to_aac(in_aiff: str, out_aac: str):
    print(f"Converting to AAC → {out_aac}")
    subprocess.run([
        FFMPEG, "-y", "-i", in_aiff,
        "-c:a", "aac", "-b:a", "128k",
        out_aac
    ], check=True, capture_output=True)


def loop_audio_to_duration(in_aac: str, out_aac: str, duration_seconds: int):
    print(f"Looping audio to {duration_seconds // 3600}h → {out_aac}")
    subprocess.run([
        FFMPEG, "-y",
        "-stream_loop", "-1", "-i", in_aac,
        "-t", str(duration_seconds),
        "-c:a", "copy",
        out_aac
    ], check=True, capture_output=True)


def create_video(audio_path: str, out_mp4: str, duration_seconds: int):
    print(f"Encoding video ({duration_seconds // 3600}h) → {out_mp4}")
    print("  This will take several minutes. Please wait...")
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x050510:s=1920x1080:r=1",  # near-black, 1fps (saves encoding time)
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "35",
        "-c:a", "copy",
        "-t", str(duration_seconds),
        "-shortest",
        out_mp4
    ], check=True)
    size = os.path.getsize(out_mp4)
    print(f"  Done! File size: {size / 1024 / 1024:.0f} MB")


def main():
    template_path = os.path.join(
        os.path.dirname(__file__), "..", "templates", "success_career_8hr.json"
    )
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_videos")
    os.makedirs(out_dir, exist_ok=True)

    with open(template_path) as f:
        template = json.load(f)

    duration_seconds = template["duration_minutes"] * 60

    segment_aiff = os.path.join(out_dir, "segment.aiff")
    segment_aac  = os.path.join(out_dir, "segment.aac")
    looped_aac   = os.path.join(out_dir, "audio_8hr.aac")
    final_mp4    = os.path.join(out_dir, "success_career_8hr.mp4")

    script = build_script(template)
    generate_segment(script, segment_aiff)
    aiff_to_aac(segment_aiff, segment_aac)
    loop_audio_to_duration(segment_aac, looped_aac, duration_seconds)
    create_video(looped_aac, final_mp4, duration_seconds)

    print(f"\nVideo ready: {final_mp4}")


if __name__ == "__main__":
    main()
