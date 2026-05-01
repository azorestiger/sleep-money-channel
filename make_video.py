#!/usr/bin/env python3
"""
Sleep Money Affirmations — Production Video Generator
Generates an 8-hour sleep affirmations video with:
  - ElevenLabs River TTS with word-level timestamp sync
  - Cormorant Garamond SemiBold font, centered, size 78
  - 3-word subtitle chunks for tight audio/text sync
  - 432Hz binaural ambient background music
  - 55% voice / 55% music mix
  - 5fps, 1920x1080, 8 hours
Usage: python3 make_video.py [--index 0|1|2|3|4]
"""

import argparse, base64, json, math, os, random, subprocess, time, urllib.request
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

FFMPEG    = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR   = Path("/tmp/sleep_video"); OUT_DIR.mkdir(exist_ok=True)
REPO_DIR  = Path(__file__).parent
FONT_FILE = REPO_DIR / "config" / "CormorantGaramond-SemiBoldItalic.ttf"
DURATION  = 28800  # 8 hours

ELEVENLABS_KEY = "sk_2b10cb0ae0378f907827112def4d0c23813b3853a448bee9"
VOICE_ID       = "SAz9YHcvj6GT2YYXdXww"  # River
MODEL_ID       = "eleven_turbo_v2_5"

VOICE_INTRO = {"stability": 0.88, "similarity_boost": 0.75, "style": 0.10, "use_speaker_boost": True}
VOICE_AFF   = {"stability": 0.80, "similarity_boost": 0.75, "style": 0.25, "use_speaker_boost": True}

GUIDED_INTRO = (
    "Find a comfortable position and allow your body to begin to relax. "
    "Take a long slow breath in... and gently breathe out. "
    "With every breath you are becoming more and more deeply relaxed. "
    "There is nothing you need to do right now. Nowhere you need to be. "
    "Simply allow yourself to drift... deeper... and deeper... into a beautiful peaceful sleep. "
    "As you relax completely your mind becomes open and receptive, "
    "ready to receive these powerful truths about who you are and what you are capable of creating. "
    "You are safe. You are supported. "
    "And as you sleep tonight your subconscious mind will absorb every word that follows, "
    "planting the seeds of unlimited success abundance and prosperity deep within you. "
    "Simply breathe... and let go..."
)


# ── TTS ────────────────────────────────────────────────────────────────────────

def tts_with_timestamps(text: str, voice_settings: dict) -> tuple:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    payload = json.dumps({"text": text, "model_id": MODEL_ID, "voice_settings": voice_settings}).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    audio = base64.b64decode(data["audio_base64"])
    al = data["alignment"]
    words, word, w_start, w_end = [], "", None, None
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch in (" ", "\n"):
            if word.strip(): words.append((word.strip(), w_start, w_end))
            word, w_start, w_end = "", None, None
        else:
            word += ch
            if w_start is None: w_start = s
            w_end = e
    if word.strip(): words.append((word.strip(), w_start, w_end))
    return audio, words


def build_chunks(template: dict) -> list:
    sections, chunk, length = [], [], 0
    for sec in template["sections"]:
        if "content" in sec: sections.append(sec["content"])
        if "affirmations" in sec:
            for _ in range(sec.get("repeat_times", 1)):
                for a in sec["affirmations"]:
                    line = a + ". "
                    if length + len(line) > 3800:
                        sections.append(" ".join(chunk)); chunk, length = [], 0
                    chunk.append(line.strip()); length += len(line)
            if chunk: sections.append(" ".join(chunk)); chunk, length = [], 0
    return sections


def group_3words(words: list) -> list:
    lines = []
    for i in range(0, len(words), 3):
        chunk = words[i:i+3]
        lines.append((" ".join(w for w, _, _ in chunk), chunk[0][1], chunk[-1][2]))
    return lines


# ── ASS subtitles ──────────────────────────────────────────────────────────────

def secs_to_ass(s: float) -> str:
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s % 60
    return f"{h}:{m:02d}:{int(sec):02d}.{int((sec % 1) * 100):02d}"


def build_ass(all_lines: list, out: Path, font_name: str = "Cormorant Garamond SemiBold"):
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font_name},78,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "0,1,0,0,100,100,2,0,1,2,0,5,20,20,0,1\n"
        f"Style: Watermark,{font_name},26,&H4DFFFFFF,&H000000FF,&H00000000,&H00000000,"
        "0,0,0,0,100,100,0,0,1,1,0,2,10,10,40,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:00.00,8:00:00.00,Watermark,,0,0,0,,Sleep Money Affirmations\n"
    )
    with open(out, "w", encoding="utf-8") as f:
        f.write(header)
        for text, start, end in all_lines:
            safe = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
            f.write(f"Dialogue: 0,{secs_to_ass(start)},{secs_to_ass(end)},Default,,0,0,0,,{safe}\n")
    print(f"  Subtitles: {len(all_lines)} lines → {out.name}")


# ── Visuals & music ────────────────────────────────────────────────────────────

def generate_starfield(out: Path):
    random.seed(42)
    img = Image.new("RGB", (1920, 1080), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    for _ in range(2800):
        x, y = random.randint(0, 1919), random.randint(0, 1079)
        b = random.randint(140, 255)
        sz = random.choices([1, 2, 3], weights=[78, 18, 4])[0]
        t = random.choice(["cool", "warm", "white"])
        c = (max(0,b-30),max(0,b-10),b) if t=="cool" else (b,max(0,b-20),max(0,b-40)) if t=="warm" else (b,b,b)
        if sz == 1: draw.point((x, y), fill=c)
        else: draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=c)
    img = Image.blend(img, img.filter(ImageFilter.GaussianBlur(1)), 0.12)
    img.save(str(out))


def generate_music(out: Path):
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi", "-i", "sine=frequency=432:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=436:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=108:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=864:sample_rate=44100",
        "-filter_complex",
        "[0][2][3]amix=inputs=3:weights=0.4 0.15 0.08[L];"
        "[1][2][3]amix=inputs=3:weights=0.4 0.15 0.08[R];"
        "[L][R]join=inputs=2:channel_layout=stereo[M];"
        "[M]volume=0.18[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "128k", "-t", str(DURATION), str(out)
    ], check=True, capture_output=True)


def get_duration(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
    for line in r.stderr.split("\n"):
        if "Duration" in line:
            t = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])
    return 0.0


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, default=None)
    args = parser.parse_args()

    # Load template
    template_map = {
        0: "success_career_8hr.json",
        1: "financial_abundance_8hr.json",
        2: "debt_freedom_8hr.json",
        3: "gratitude_manifestation_8hr.json",
        4: "health_vitality_abundance_8hr.json",
    }
    # Rotate through 5 templates based on day of week (Mon=0 ... Fri=4)
    idx = args.index if args.index is not None else date.today().weekday() % 5
    template_path = REPO_DIR / "templates" / template_map[idx]
    template = json.loads(template_path.read_text())
    print(f"Template {idx}: {template['title']}")

    # 1. Guided intro
    print("\n[1/7] Generating guided intro...")
    intro_mp3 = OUT_DIR / "intro.mp3"
    intro_bytes, intro_words = tts_with_timestamps(GUIDED_INTRO, VOICE_INTRO)
    intro_mp3.write_bytes(intro_bytes)
    intro_dur = get_duration(intro_mp3)
    intro_lines = group_3words(intro_words)
    print(f"  {intro_dur:.1f}s, {len(intro_lines)} subtitle lines")

    # 2. Affirmation chunks
    print("\n[2/7] Generating affirmations...")
    chunks = build_chunks(template)
    seg_files, all_words, cumulative = [], [], 0.0
    for i, text in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)}: {len(text)} chars")
        ab, words = tts_with_timestamps(text, VOICE_AFF)
        cf = OUT_DIR / f"chunk_{i:03d}.mp3"; cf.write_bytes(ab)
        dur = get_duration(cf)
        for w, s, e in words: all_words.append((w, s + cumulative, e + cumulative))
        cumulative += dur; seg_files.append(cf)
        time.sleep(0.3)
    seg_lines = group_3words(all_words)
    print(f"  Segment: {cumulative:.1f}s, {len(seg_lines)} subtitle lines")

    # 3. Build 8-hour audio
    print("\n[3/7] Building 8-hour audio...")
    concat_txt = OUT_DIR / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{f}'" for f in seg_files))
    seg_mp3 = OUT_DIR / "segment.mp3"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c:a", "libmp3lame", str(seg_mp3)], check=True, capture_output=True)
    remaining = DURATION - intro_dur
    looped = OUT_DIR / "looped.mp3"
    subprocess.run([FFMPEG, "-y", "-stream_loop", "-1", "-i", str(seg_mp3), "-t", str(remaining), "-c:a", "libmp3lame", str(looped)], check=True, capture_output=True)
    fc = OUT_DIR / "final_concat.txt"; fc.write_text(f"file '{intro_mp3}'\nfile '{looped}'")
    combined_mp3 = OUT_DIR / "combined.mp3"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(fc), "-c:a", "libmp3lame", str(combined_mp3)], check=True, capture_output=True)
    voice_aac = OUT_DIR / "voice.aac"
    subprocess.run([FFMPEG, "-y", "-i", str(combined_mp3), "-c:a", "aac", "-b:a", "128k", str(voice_aac)], check=True, capture_output=True)
    print(f"  Voice audio: {voice_aac.stat().st_size/1024/1024:.0f} MB")

    # 4. Ambient music
    print("\n[4/7] Generating 432Hz ambient music...")
    music_aac = OUT_DIR / "music.aac"
    generate_music(music_aac)
    print(f"  Music: {music_aac.stat().st_size/1024/1024:.0f} MB")

    # 5. Subtitles
    print("\n[5/7] Building synced subtitle file...")
    ass_path = OUT_DIR / "subtitles.ass"
    all_lines = list(intro_lines)
    num_loops = math.ceil(remaining / cumulative)
    loop_end = intro_dur + remaining
    for loop in range(num_loops):
        offset = intro_dur + loop * cumulative
        for text, s, e in seg_lines:
            abs_s = s + offset
            if abs_s >= loop_end: break
            all_lines.append((text, abs_s, min(e + offset, loop_end)))
    # Copy font to /tmp for fontsdir
    import shutil; font_tmp = Path("/tmp/CormorantGaramond.ttf"); shutil.copy(str(FONT_FILE), str(font_tmp))
    build_ass(all_lines, ass_path)

    # 6. Starfield
    print("\n[6/7] Generating starfield background...")
    sf = OUT_DIR / "starfield.png"; generate_starfield(sf)

    # 7. Encode
    print("\n[7/7] Encoding final video (8hr @ 5fps)...")
    out_mp4 = OUT_DIR / template_map[idx]
    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1", "-i", str(sf),
        "-i", str(voice_aac), "-i", str(music_aac),
        "-filter_complex",
        f"[0:v]ass={ass_path}:fontsdir=/tmp[vout];"
        f"[1:a][2:a]amix=inputs=2:weights=0.55 0.55:normalize=0[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "33", "-r", "5",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(DURATION), "-shortest", str(out_mp4)
    ], check=True)
    print(f"  Video: {out_mp4.stat().st_size/1024/1024:.0f} MB → {out_mp4}")

    # Save metadata
    meta = {"title": template["title"], "description": template.get("description", ""), "tags": template.get("seo_keywords", []), "filename": template_map[idx], "video_path": str(out_mp4), "privacyStatus": "private"}
    (OUT_DIR / "metadata.json").write_text(json.dumps(meta))
    print(f"\nDone! Metadata saved to {OUT_DIR}/metadata.json")


if __name__ == "__main__":
    main()
