#!/usr/bin/env python3
"""
Sleep Money Affirmations — YouTube Shorts Generator
Creates a 45-55 second vertical (9:16) Short from the current day's template.
Picks the most powerful affirmations, generates River TTS, animated starfield, uploads.

Usage: python3 make_short.py [--index 0|1|2|3|4]
"""

import argparse, base64, json, math, random, subprocess, time, urllib.request
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

FFMPEG    = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR   = Path("/tmp/sleep_short"); OUT_DIR.mkdir(exist_ok=True)
REPO_DIR  = Path(__file__).parent
FONT_FILE = REPO_DIR / "config" / "CormorantGaramond-SemiBoldItalic.ttf"

ELEVENLABS_KEY = "sk_2b10cb0ae0378f907827112def4d0c23813b3853a448bee9"
VOICE_ID       = "SAz9YHcvj6GT2YYXdXww"  # River
MODEL_ID       = "eleven_turbo_v2_5"
TARGET_SECS    = 50  # target ~50 seconds

VOICE_SETTINGS = {"stability": 0.82, "similarity_boost": 0.75, "style": 0.20, "use_speaker_boost": True}

TEMPLATE_MAP = {
    0: "success_career_8hr.json",
    1: "financial_abundance_8hr.json",
    2: "debt_freedom_8hr.json",
    3: "gratitude_manifestation_8hr.json",
    4: "health_vitality_abundance_8hr.json",
}

SHORTS_HOOKS = {
    0: "Did you know you can reprogram your mind for success WHILE you sleep?",
    1: "Money is flowing to you RIGHT NOW. Here's how to receive it...",
    2: "You are one night of sleep away from financial freedom. Listen to this...",
    3: "Gratitude is the fastest path to abundance. Repeat these tonight...",
    4: "Your health IS your wealth. Let these sink in while you sleep...",
}


def pick_affirmations(template: dict, count: int = 7) -> list:
    """Pick the most powerful short affirmations for a Short."""
    all_affs = []
    for sec in template["sections"]:
        for a in sec.get("affirmations", []):
            if len(a) < 60:  # keep punchy, short ones
                all_affs.append(a)
    # Deduplicate and pick evenly spread
    seen = set()
    unique = []
    for a in all_affs:
        if a.lower() not in seen:
            seen.add(a.lower())
            unique.append(a)
    step = max(1, len(unique) // count)
    return unique[::step][:count]


def build_short_script(hook: str, affirmations: list) -> str:
    lines = [hook, ""]
    for a in affirmations:
        lines.append(a + ".")
    lines.append("")
    lines.append("Follow for daily sleep affirmations.")
    return " ".join(lines)


def tts(text: str) -> tuple:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    payload = json.dumps({"text": text, "model_id": MODEL_ID, "voice_settings": VOICE_SETTINGS}).encode()
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


def group_3words(words):
    lines = []
    for i in range(0, len(words), 3):
        chunk = words[i:i+3]
        lines.append((" ".join(w for w, _, _ in chunk), chunk[0][1], chunk[-1][2]))
    return lines


def secs_to_ass(s):
    h = int(s//3600); m = int((s%3600)//60); sec = s%60
    return f"{h}:{m:02d}:{int(sec):02d}.{int((sec%1)*100):02d}"


def generate_vertical_starfield():
    random.seed(99)
    img = Image.new("RGB", (1080, 1920), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    for _ in range(2500):
        x, y = random.randint(0, 1079), random.randint(0, 1919)
        b = random.randint(140, 255)
        sz = random.choices([1, 2, 3], weights=[78, 18, 4])[0]
        t = random.choice(["cool", "warm", "white"])
        c = (max(0,b-30),max(0,b-10),b) if t=="cool" else (b,max(0,b-20),max(0,b-40)) if t=="warm" else (b,b,b)
        if sz == 1: draw.point((x, y), fill=c)
        else: draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=c)
    img = Image.blend(img, img.filter(ImageFilter.GaussianBlur(1)), 0.12)
    sf = OUT_DIR / "starfield_vertical.png"; img.save(str(sf)); return sf


def build_ass(lines, out, duration, font_name="Cormorant Garamond SemiBold"):
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font_name},72,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "0,1,0,0,100,100,2,0,1,2,0,5,40,40,0,1\n"
        f"Style: Watermark,{font_name},32,&H4DFFFFFF,&H000000FF,&H00000000,&H00000000,"
        "0,0,0,0,100,100,0,0,1,1,0,2,20,20,60,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        f"Dialogue: 0,0:00:00.00,{secs_to_ass(duration)},Watermark,,0,0,0,,Sleep Money Affirmations\n"
    )
    with open(out, "w", encoding="utf-8") as f:
        f.write(header)
        for text, start, end in lines:
            safe = text.replace("\\","\\\\").replace("{","\\{").replace("}","\\}")
            f.write(f"Dialogue: 0,{secs_to_ass(start)},{secs_to_ass(end)},Default,,0,0,0,,{safe}\n")


def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
    for line in r.stderr.split("\n"):
        if "Duration" in line:
            t = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(t[0])*3600 + int(t[1])*60 + float(t[2])
    return 0.0


def encode_short(sf, audio_mp3, ass_path, out_mp4, duration):
    import shutil
    shutil.copy(str(FONT_FILE), "/tmp/CormorantGaramond.ttf")
    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1", "-i", str(sf),
        "-i", str(audio_mp3),
        "-filter_complex",
        f"[0:v]scale=2160:3840,zoompan=z='1.55+0.25*sin(3.14159*on/60)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=24[bg];"
        f"[bg]ass={ass_path}:fontsdir=/tmp[vout]",
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration), "-shortest",
        str(out_mp4)
    ], check=True)


def upload_short(video_path, title, description, tags):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    token_file = REPO_DIR / "config" / "token.json"
    creds = Credentials.from_authorized_user_file(str(token_file), ["https://www.googleapis.com/auth/youtube.upload"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.write_text(creds.to_json())

    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
        "status": {"privacyStatus": "private", "madeForKids": False}
    }
    media = MediaFileUpload(str(video_path), chunksize=10*1024*1024, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    retries = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status: print(f"  Short upload: {int(status.progress()*100)}%")
            retries = 0
        except Exception as e:
            retries += 1
            if retries > 10: raise
            wait = min(2**retries, 60)
            print(f"  Retry {retries}/10 in {wait}s...")
            time.sleep(wait)
    url = f"https://www.youtube.com/watch?v={response['id']}"
    print(f"Short uploaded: {url}")
    return url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, default=None)
    args = parser.parse_args()

    idx = args.index if args.index is not None else date.today().weekday() % 5
    template = json.loads((REPO_DIR / "templates" / TEMPLATE_MAP[idx]).read_text())
    hook = SHORTS_HOOKS[idx]
    print(f"Generating Short for template {idx}: {template['title']}")

    # Pick affirmations and build script
    affirmations = pick_affirmations(template, count=6)
    script = build_short_script(hook, affirmations)
    print(f"Script: {len(script)} chars, ~{len(script.split())} words")

    # TTS
    print("Generating River TTS...")
    audio_bytes, words = tts(script)
    audio_mp3 = OUT_DIR / "short_audio.mp3"
    audio_mp3.write_bytes(audio_bytes)
    duration = get_duration(audio_mp3)
    print(f"  Duration: {duration:.1f}s")

    # Subtitles
    subtitle_lines = group_3words(words)
    ass_path = OUT_DIR / "short_subs.ass"
    build_ass(subtitle_lines, str(ass_path), duration)

    # Starfield + encode
    print("Generating vertical starfield and encoding...")
    sf = generate_vertical_starfield()
    out_mp4 = OUT_DIR / f"short_{TEMPLATE_MAP[idx].replace('.json','')}.mp4"
    encode_short(sf, audio_mp3, str(ass_path), out_mp4, duration)
    print(f"  Short ready: {out_mp4} ({out_mp4.stat().st_size/1024/1024:.1f} MB)")

    # Build YouTube metadata
    theme_titles = {
        0: "I Am Unstoppable 🌙 Success Affirmations #Shorts #SleepAffirmations",
        1: "Money Is Flowing To You RIGHT NOW 💰 #Shorts #MoneyAffirmations",
        2: "You Are Financially FREE 💚 #Shorts #SleepAffirmations",
        3: "The Universe Is Working For You ✨ #Shorts #ManifestationAffirmations",
        4: "You Are Healthy Wealthy & Thriving 💫 #Shorts #HealthAffirmations",
    }
    title = theme_titles[idx]
    description = f"{hook}\n\n{chr(10).join(affirmations)}\n\nFollow @SleepMoneyAffirmations for daily sleep affirmations 🌙\n\n#Shorts #SleepAffirmations #Affirmations #Manifestation #Abundance"
    tags = ["shorts", "sleep affirmations", "affirmations", "manifestation", "abundance", "short affirmations"]

    # Save metadata
    meta = {"title": title, "description": description, "tags": tags, "video_path": str(out_mp4)}
    (OUT_DIR / "short_metadata.json").write_text(json.dumps(meta))

    # Upload
    print("Uploading Short to YouTube (private for review)...")
    url = upload_short(out_mp4, title, description, tags)
    print(f"\nShort ready for review: {url}")
    return url


if __name__ == "__main__":
    main()
