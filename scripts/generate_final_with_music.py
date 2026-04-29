#!/usr/bin/env python3
"""
Re-encode the final video with:
- Cormorant Garamond Italic font, centered on screen
- 432Hz ambient binaural background music mixed under the voice
"""

import subprocess, struct, math, os
from pathlib import Path

import imageio_ffmpeg
FFMPEG    = imageio_ffmpeg.get_ffmpeg_exe()
BASE      = Path(__file__).parent.parent
OUT_DIR   = BASE / "output_videos"
FONT_PATH = str(BASE / "config" / "CormorantGaramond-SemiBoldItalic.ttf")
DURATION  = 28800

VOICE_AAC  = "/tmp/combined_sync.aac"
ASS_IN     = "/tmp/subtitles_sync.ass"
ASS_OUT    = "/tmp/subtitles_centered.ass"
MUSIC_AAC  = "/tmp/ambient_music.aac"
STARFIELD  = "/tmp/starfield.png"
OUT_MP4    = "/tmp/success_career_final.mp4"


def update_ass_font():
    """Update ASS file: center alignment, Cormorant Garamond, larger size."""
    text = Path(ASS_IN).read_text(encoding="utf-8")
    # Replace the Style line
    old_style = "Style: Default,Arial,58,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,2,0,1,3,0,2,20,20,60,1"
    new_style = "Style: Default,Cormorant Garamond,64,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,2,0,1,2,0,5,20,20,0,1"
    #                                                                                                                         ^ alignment 5 = middle-center
    text = text.replace(old_style, new_style)
    # Add font file reference
    if "Fonts]" not in text:
        text = text.replace("[Script Info]",
            f"[Script Info]\n; Font: {FONT_PATH}")
    Path(ASS_OUT).write_text(text, encoding="utf-8")
    print(f"  Updated ASS: center-aligned, Cormorant Garamond SemiBold Italic")


def generate_ambient_music():
    """Generate 432Hz binaural ambient pad using ffmpeg sine generators."""
    print("  Generating 432Hz ambient binaural music...")
    # Left channel: 432Hz (crown chakra / calming)
    # Right channel: 436Hz → 4Hz binaural beat (delta wave, deep sleep)
    # Plus a low 108Hz undertone (432/4) and soft 864Hz overtone
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=432:sample_rate=44100",   # L: 432Hz
        "-f", "lavfi",
        "-i", "sine=frequency=436:sample_rate=44100",   # R: 436Hz (4Hz beat)
        "-f", "lavfi",
        "-i", "sine=frequency=108:sample_rate=44100",   # bass undertone
        "-f", "lavfi",
        "-i", "sine=frequency=864:sample_rate=44100",   # soft overtone
        "-filter_complex",
        # Mix: L=(432*0.4 + 108*0.15 + 864*0.08), R=(436*0.4 + 108*0.15 + 864*0.08)
        "[0][2][3]amix=inputs=3:weights=0.4 0.15 0.08[left];"
        "[1][2][3]amix=inputs=3:weights=0.4 0.15 0.08[right];"
        "[left][right]join=inputs=2:channel_layout=stereo[music];"
        "[music]volume=0.18[out]",  # 18% volume — quiet under voice
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(DURATION),
        MUSIC_AAC
    ], check=True, capture_output=True)
    print(f"  Music: {Path(MUSIC_AAC).stat().st_size / 1024 / 1024:.0f} MB")


def encode_video():
    """Encode final video: starfield + centered subtitles + mixed audio."""
    print("  Encoding final video...")

    # Copy font so ffmpeg/libass can find it
    font_dest = "/tmp/CormorantGaramond-SemiBoldItalic.ttf"
    import shutil
    shutil.copy(FONT_PATH, font_dest)

    # Watermark drawtext (bottom center)
    watermark = (
        f"drawtext=fontfile='{FONT_PATH}'"
        f":text='Sleep Money Affirmations'"
        f":x=(w-text_w)/2:y=h-60"
        f":fontcolor=white@0.3:fontsize=28"
    )

    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1", "-i", STARFIELD,
        "-i", VOICE_AAC,
        "-i", MUSIC_AAC,
        "-filter_complex",
        f"[0:v]{watermark},ass={ASS_OUT}[vout];"
        f"[1:a][2:a]amix=inputs=2:weights=1 1:normalize=0[aout]",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "33", "-r", "1",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(DURATION), "-shortest",
        OUT_MP4
    ], check=True)

    dest = OUT_DIR / "success_career_8hr_final.mp4"
    import shutil
    shutil.copy(OUT_MP4, str(dest))
    print(f"  Done! {dest.stat().st_size / 1024 / 1024:.0f} MB → {dest}")


def main():
    print("Step 1: Updating subtitle style (center + Cormorant Garamond)...")
    update_ass_font()

    print("\nStep 2: Generating ambient 432Hz binaural music...")
    generate_ambient_music()

    print("\nStep 3: Encoding final video...")
    encode_video()

    print("\nAll done!")


if __name__ == "__main__":
    main()
