#!/usr/bin/env python3
"""
Generate the final video with word-synced text overlay using ElevenLabs timestamps API.
Builds an ASS subtitle file from character-level alignment data, then burns it in.
"""

import json, os, subprocess, time, base64, math, urllib.request
from pathlib import Path

API_KEY   = "sk_2b10cb0ae0378f907827112def4d0c23813b3853a448bee9"
VOICE_ID  = "SAz9YHcvj6GT2YYXdXww"  # River
MODEL_ID  = "eleven_turbo_v2_5"
OUT_DIR   = Path(__file__).parent.parent / "output_videos"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
DURATION  = 28800  # 8 hours

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

VOICE_SETTINGS_INTRO = {"stability": 0.88, "similarity_boost": 0.75, "style": 0.10, "use_speaker_boost": True}
VOICE_SETTINGS_AFFIRMATIONS = {"stability": 0.80, "similarity_boost": 0.75, "style": 0.25, "use_speaker_boost": True}

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


def tts_with_timestamps(text: str, voice_settings: dict) -> tuple[bytes, list]:
    """Returns (mp3_bytes, word_timings) where word_timings = [(word, start, end), ...]"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    payload = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": voice_settings
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())

    audio_bytes = base64.b64decode(data["audio_base64"])
    alignment = data["alignment"]
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    # Group characters into words
    words = []
    word, w_start, w_end = "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch in (" ", "\n", "\t"):
            if word.strip():
                words.append((word.strip(), w_start, w_end))
            word, w_start, w_end = "", None, None
        else:
            word += ch
            if w_start is None:
                w_start = s
            w_end = e
    if word.strip():
        words.append((word.strip(), w_start, w_end))

    return audio_bytes, words


def group_into_lines(words: list, max_chars: int = 38) -> list:
    """Group words into subtitle lines [(text, start, end), ...]"""
    lines, line_words, line_len = [], [], 0
    for word, start, end in words:
        if line_words and line_len + len(word) + 1 > max_chars:
            line_text = " ".join(w for w, _, _ in line_words)
            lines.append((line_text, line_words[0][1], line_words[-1][2]))
            line_words, line_len = [], 0
        line_words.append((word, start, end))
        line_len += len(word) + 1
    if line_words:
        line_text = " ".join(w for w, _, _ in line_words)
        lines.append((line_text, line_words[0][1], line_words[-1][2]))
    return lines


def secs_to_ass(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = secs % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass_file(all_lines: list, out_path: Path):
    """all_lines = [(text, start_secs, end_secs), ...]"""
    header = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,58,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,2,0,1,3,0,2,20,20,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        for text, start, end in all_lines:
            # Escape special ASS characters
            safe = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
            f.write(f"Dialogue: 0,{secs_to_ass(start)},{secs_to_ass(end)},Default,,0,0,0,,{safe}\n")
    print(f"  Subtitle file: {out_path} ({len(all_lines)} lines)")


def get_audio_duration(mp3_path: Path) -> float:
    result = subprocess.run([FFMPEG, "-i", str(mp3_path), "-f", "null", "-"],
                            capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            t = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])
    return 0.0


def build_sections(template):
    sections, chunk, chunk_len = [], [], 0
    for sec in template["sections"]:
        if "content" in sec:
            sections.append(sec["content"])
        if "affirmations" in sec:
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
                chunk, chunk_len = [], 0
    return sections


def main():
    OUT_DIR.mkdir(exist_ok=True)
    template = json.loads((Path(__file__).parent.parent / "templates" / "success_career_8hr.json").read_text())
    starfield = OUT_DIR / "starfield.png"

    # ── STEP 1: Intro with timestamps ──────────────────────────────────────
    print("Step 1: Generating guided intro with timestamps...")
    intro_mp3 = OUT_DIR / "intro_sync.mp3"
    intro_bytes, intro_words = tts_with_timestamps(GUIDED_INTRO, VOICE_SETTINGS_INTRO)
    intro_mp3.write_bytes(intro_bytes)
    intro_dur = get_audio_duration(intro_mp3)
    intro_lines = group_into_lines(intro_words)
    print(f"  Intro: {intro_dur:.1f}s, {len(intro_lines)} subtitle lines")

    # ── STEP 2: Affirmations segment with timestamps ────────────────────────
    print("\nStep 2: Generating affirmations segment with timestamps...")
    sections = build_sections(template)
    segment_chunks = []  # (mp3_bytes, words)
    all_seg_words = []
    cumulative = 0.0

    seg_mp3_files = []
    for i, text in enumerate(sections):
        print(f"  Chunk {i+1}/{len(sections)}: {len(text)} chars")
        audio_bytes, words = tts_with_timestamps(text, VOICE_SETTINGS_AFFIRMATIONS)
        cf = OUT_DIR / f"seg_chunk_{i:03d}.mp3"
        cf.write_bytes(audio_bytes)
        seg_mp3_files.append(cf)
        # Offset word timings by cumulative duration
        chunk_dur = get_audio_duration(cf)
        for word, start, end in words:
            all_seg_words.append((word, start + cumulative, end + cumulative))
        cumulative += chunk_dur
        time.sleep(0.3)

    seg_dur = cumulative
    seg_lines = group_into_lines(all_seg_words)
    print(f"  Segment: {seg_dur:.1f}s, {len(seg_lines)} subtitle lines")

    # ── STEP 3: Concatenate audio ───────────────────────────────────────────
    print("\nStep 3: Building 8-hour audio...")
    concat_txt = OUT_DIR / "_sync_concat.txt"
    # Stitch segment mp3 files
    seg_concat = OUT_DIR / "segment_sync.mp3"
    concat_txt.write_text("\n".join(f"file '{f}'" for f in seg_mp3_files))
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
                    "-c:a", "libmp3lame", str(seg_concat)], check=True, capture_output=True)

    # Loop segment to fill remaining time after intro
    remaining = DURATION - intro_dur
    looped_seg = OUT_DIR / "segment_sync_looped.mp3"
    subprocess.run([FFMPEG, "-y", "-stream_loop", "-1", "-i", str(seg_concat),
                    "-t", str(remaining), "-c:a", "libmp3lame", str(looped_seg)],
                   check=True, capture_output=True)

    # Final concat: intro + looped segment
    final_concat_txt = OUT_DIR / "_final_concat.txt"
    final_concat_txt.write_text(f"file '{intro_mp3}'\nfile '{looped_seg}'")
    combined_mp3 = OUT_DIR / "combined_sync.mp3"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(final_concat_txt),
                    "-c:a", "libmp3lame", str(combined_mp3)], check=True, capture_output=True)
    full_aac = OUT_DIR / "combined_sync.aac"
    subprocess.run([FFMPEG, "-y", "-i", str(combined_mp3),
                    "-c:a", "aac", "-b:a", "128k", str(full_aac)], check=True, capture_output=True)
    print(f"  Full audio: {full_aac.stat().st_size / 1024 / 1024:.0f} MB")

    # ── STEP 4: Build subtitle file ────────────────────────────────────────
    print("\nStep 4: Building synced subtitle file...")
    all_lines = list(intro_lines)  # intro timing is exact
    # Add affirmations loops with time offsets
    num_loops = math.ceil(remaining / seg_dur)
    for loop in range(num_loops):
        offset = intro_dur + loop * seg_dur
        loop_end = intro_dur + remaining
        for text, start, end in seg_lines:
            abs_start = start + offset
            abs_end = end + offset
            if abs_start >= loop_end:
                break
            all_lines.append((text, abs_start, min(abs_end, loop_end)))

    ass_file = OUT_DIR / "subtitles_sync.ass"
    build_ass_file(all_lines, ass_file)

    # ── STEP 5: Encode final video ──────────────────────────────────────────
    print("\nStep 5: Encoding final video with synced word overlay...")
    watermark = (f"drawtext=fontfile='{FONT_PATH}':text='Sleep Money Affirmations'"
                 f":x=(w-text_w)/2:y=h-60:fontcolor=white@0.35:fontsize=24")
    ass_filter = f"ass='{ass_file}'"
    filter_chain = f"[0:v]{watermark},{ass_filter}[vout]"

    out_mp4 = OUT_DIR / "success_career_8hr_synced.mp4"
    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1", "-i", str(starfield),
        "-i", str(full_aac),
        "-filter_complex", filter_chain,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "33", "-r", "1",
        "-c:a", "copy", "-t", str(DURATION), "-shortest",
        str(out_mp4)
    ], check=True)

    print(f"\nDone! {out_mp4.stat().st_size / 1024 / 1024:.0f} MB → {out_mp4}")


if __name__ == "__main__":
    main()
