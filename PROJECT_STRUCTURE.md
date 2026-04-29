# Sleep Money Affirmations - Complete File Structure

## Project Overview

```
sleep-money-channel/
│
├── README.md                      # Project overview & getting started
├── QUICK_START.md                # 5-minute setup guide
├── CHANNEL_SETUP.md              # Complete YouTube channel optimization
├── PRODUCTION_WORKFLOW.md        # Full production pipeline guide
├── requirements.txt              # Python dependencies
├── setup.sh                       # Automated setup script
│
├── scripts/                       # Python automation scripts
│   ├── youtube_uploader.py       # YouTube upload automation
│   │   ├── Authenticate with YouTube API
│   │   ├── Single video upload
│   │   ├── Schedule video publishing
│   │   └── Batch upload multiple videos
│   │
│   ├── video_generator.py        # Video generation from templates
│   │   ├── Create 8-hour video from affirmations
│   │   ├── Add background music
│   │   ├── Generate thumbnails
│   │   └── Batch video generation
│   │
│   └── scheduler.py              # Content scheduling
│       ├── Generate upload calendar
│       ├── Optimal posting times
│       ├── Theme rotation schedule
│       └── Export to CSV for calendar apps
│
├── templates/                     # Affirmation script templates (JSON)
│   ├── financial_abundance_8hr.json
│   │   └── 8-hour wealth & money manifestation affirmations
│   │
│   ├── debt_freedom_8hr.json
│   │   └── Debt elimination & financial peace affirmations
│   │
│   └── success_career_8hr.json
│       └── Career growth & income increase affirmations
│
├── config/                        # Configuration & setup files
│   ├── client_secrets.json       # YouTube API credentials (YOU CREATE THIS)
│   ├── channel_setup.json        # Channel branding, SEO, monetization
│   ├── metadata_template.json    # Video metadata template (customize per video)
│   ├── batch_upload_example.json # Batch upload configuration template
│   ├── token.pickle              # YouTube auth token (auto-generated)
│   └── upload_schedule.json      # Generated schedule (auto-created by scheduler.py)
│
├── output_videos/                # Generated videos (auto-created)
│   ├── affirmations_01.mp4
│   ├── affirmations_02.mp4
│   └── [output video files]
│
└── [other files created at runtime]
    ├── schedule.csv              # Calendar export of upload schedule
    └── [any downloaded/generated files]
```

---

## 📄 Key Files Explained

### Core Documentation

#### `README.md`
- **Purpose:** Project overview, revenue expectations, quick start
- **Read when:** First time exploring the project
- **What it covers:** Features, expected revenue, file guide, tech stack

#### `QUICK_START.md`
- **Purpose:** Get running in 5 minutes
- **Read when:** Ready to start immediately
- **What it covers:** Installation, API setup, first video generation, troubleshooting

#### `CHANNEL_SETUP.md`
- **Purpose:** Complete YouTube channel optimization guide
- **Read when:** Setting up your YouTube channel
- **What it covers:** 
  - Pre-launch checklist
  - Branding & customization
  - SEO & metadata optimization
  - Video upload settings
  - Monetization setup
  - Success metrics

#### `PRODUCTION_WORKFLOW.md`
- **Purpose:** Full production pipeline from affirmation script to YouTube upload
- **Read when:** Need detailed workflow instructions
- **What it covers:**
  - Content planning
  - Video production (DIY + tools)
  - Thumbnail creation
  - Upload & scheduling
  - Distribution strategy
  - Monetization
  - Management checklist

#### `requirements.txt`
- **Purpose:** Python package dependencies
- **Use:** `pip install -r requirements.txt`
- **Contains:** Google APIs, authentication, image processing libraries

---

### Python Scripts (Automation)

#### `scripts/youtube_uploader.py`
**Purpose:** Upload videos to YouTube with full automation

**Features:**
- OAuth2 authentication with YouTube API
- Single video upload with metadata
- Schedule video publishing for specific date/time
- Batch upload multiple videos at once
- Includes thumbnail, title, description, tags

**Usage:**
```bash
# Single upload
python3 scripts/youtube_uploader.py \
  --file "video.mp4" \
  --metadata "config/metadata.json"

# Schedule upload
python3 scripts/youtube_uploader.py \
  --file "video.mp4" \
  --metadata "config/metadata.json" \
  --schedule "2026-04-28T20:00:00Z"

# Batch upload
python3 scripts/youtube_uploader.py \
  --batch "config/batch_upload.json"
```

**Dependencies:** google-auth-oauthlib, google-api-python-client

---

#### `scripts/video_generator.py`
**Purpose:** Generate videos from affirmation templates

**Features:**
- Create videos from JSON affirmation templates
- Combine audio narration with background music
- Generate thumbnail images
- Batch video generation from config file
- Customizable video duration

**Usage:**
```bash
# Generate single video
python3 scripts/video_generator.py \
  --template templates/financial_abundance_8hr.json \
  --music "background_music.mp3" \
  --duration 480 \
  --output "final_video.mp4"

# Batch generate
python3 scripts/video_generator.py \
  --batch "config/batch_video_config.json"
```

**Dependencies:** FFmpeg (system), Pillow (Python)

---

#### `scripts/scheduler.py`
**Purpose:** Create content calendar & optimal upload schedule

**Features:**
- Generate month-long upload calendar
- Calculate optimal posting times (6-8 PM, 6-9 AM)
- Distribute videos by theme throughout month
- Export schedule to CSV for calendar apps
- Display readable schedule

**Usage:**
```bash
# Generate sample schedule
python3 scripts/scheduler.py

# Or import in your code:
from scheduler import ContentScheduler
scheduler = ContentScheduler()
scheduler.add_upload("Title", datetime(...), "video.mp4", tags=[...])
scheduler.display_schedule()
scheduler.export_schedule_csv("schedule.csv")
```

**Output:**
- `config/upload_schedule.json` — Schedule database
- `schedule.csv` — Calendar export (import to Google/Outlook Calendar)

---

### Templates (Affirmation Scripts)

#### `templates/financial_abundance_8hr.json`
**Theme:** Money flow, wealth manifestation
**Affirmations:** 12 unique affirmations
**Structure:**
- Opening relaxation (2 min)
- Money flow affirmations (30 min)
- Wealth mindset affirmations (20 min)
- Debt release (15 min)
- Closing gratitude (5 min)

**Key Affirmations:**
- "Money flows to me easily and effortlessly"
- "I am a magnet for financial abundance"
- "Wealth is my natural state of being"

---

#### `templates/debt_freedom_8hr.json`
**Theme:** Debt elimination, financial peace
**Affirmations:** 7 unique affirmations
**Focus:** Release debt stress, attract financial freedom

**Key Affirmations:**
- "I am breaking free from debt"
- "My debts dissolve and disappear"
- "Financial peace flows through me"

---

#### `templates/success_career_8hr.json`
**Theme:** Career growth, income increase
**Affirmations:** 7 unique affirmations
**Focus:** Success, confidence, entrepreneurship

**Key Affirmations:**
- "My career is growing and flourishing"
- "I attract success effortlessly"
- "My income is rapidly increasing"

**Template Structure (all templates):**
```json
{
  "title": "Video title",
  "duration_minutes": 480,
  "theme": "financial|debt-free|success",
  "sections": [
    {
      "section_name": "Opening",
      "content": "Intro narration",
      "affirmations": ["Affirmation 1", "Affirmation 2"]
    }
  ],
  "seo_keywords": ["keyword1", "keyword2"],
  "description_template": "YouTube description"
}
```

---

### Configuration Files

#### `config/channel_setup.json`
**Purpose:** Complete channel strategy & optimization

**Sections:**
- **Channel branding** — Description, keywords, about section
- **Playlist strategy** — Pre-defined playlists for organization
- **Monetization settings** — AdSense, memberships, merchandise ideas
- **SEO optimization** — Title formula, hashtags, thumbnail design
- **Growth strategies** — Shorts, engagement, collaborations
- **Analytics tracking** — Key metrics, 6-month/1-year goals
- **Consistency checklist** — Weekly/monthly tasks

---

#### `config/metadata_template.json`
**Purpose:** Template for video metadata

**Use:** Copy for each video, customize with:
- Title (use SEO formula)
- Description (use template with specific benefits)
- Tags (include 15-20 relevant keywords)
- Category (always "22" = People & Blogs)
- Privacy status (Public, Unlisted, Private, Scheduled)
- Publish time (ISO 8601 format)

---

#### `config/batch_upload_example.json`
**Purpose:** Configure batch uploading of multiple videos

**Structure:**
```json
{
  "videos": [
    {
      "file": "path/to/video.mp4",
      "metadata": { /* metadata object */ },
      "publish_time": "2026-04-28T20:00:00Z"
    }
  ],
  "batch_settings": {
    "upload_interval_hours": 48,
    "start_date": "2026-04-28"
  }
}
```

---

## 🔄 Workflow Steps

1. **Choose affirmation theme** → Select from templates
2. **Generate video** → Use `video_generator.py`
3. **Create thumbnail** → Use Canva (template in channel_setup.json)
4. **Prepare metadata** → Use `metadata_template.json`
5. **Create schedule** → Run `scheduler.py`
6. **Upload videos** → Use `youtube_uploader.py`
7. **Monitor analytics** → YouTube Studio
8. **Create Shorts** → Clips from full videos
9. **Cross-promote** → TikTok, Instagram, Reddit
10. **Optimize** → Adjust based on metrics

---

## 📊 File Relationships

```
Templates (JSON)
    ↓
video_generator.py (generates videos)
    ↓
Output Videos (MP4 files)
    ↓ + Metadata from metadata_template.json
    ↓
youtube_uploader.py (uploads to YouTube)
    ↓
YouTube Channel

scheduler.py (generates optimal times)
    ↓
upload_schedule.json (stores schedule)
    ↓
Can batch upload with youtube_uploader.py
```

---

## 🚀 Typical Project Flow

1. Read: `README.md` (overview)
2. Read: `QUICK_START.md` (setup)
3. Run: `setup.sh` (install dependencies)
4. Set up: YouTube API credentials
5. Read: `CHANNEL_SETUP.md` (customize channel)
6. Run: `scripts/video_generator.py` (create videos)
7. Prepare: Thumbnails & metadata
8. Read: `PRODUCTION_WORKFLOW.md` (detailed pipeline)
9. Run: `scripts/youtube_uploader.py` (upload)
10. Monitor: YouTube Analytics

---

## 📁 What Gets Created at Runtime

These files are generated automatically:

- `config/token.pickle` — YouTube authentication token (created after first upload)
- `config/upload_schedule.json` — Content schedule (created by scheduler.py)
- `output_videos/` — Generated video files
- `schedule.csv` — Calendar export (created by scheduler.py)

---

## 🛠️ Tools Used

| Tool | Files | Purpose |
|------|-------|---------|
| Python 3 | scripts/*.py | Automation |
| Google APIs | youtube_uploader.py | YouTube auth & upload |
| FFmpeg | video_generator.py | Video encoding |
| JSON | templates/*, config/* | Data storage |
| Bash | setup.sh | Installation |

---

## 📝 How to Use This Project

1. **Start here:** Open `README.md`
2. **Quick setup:** Follow `QUICK_START.md`
3. **Generate videos:** Use `scripts/video_generator.py`
4. **Schedule uploads:** Run `scripts/scheduler.py`
5. **Upload:** Use `scripts/youtube_uploader.py`
6. **Optimize channel:** Follow `CHANNEL_SETUP.md`
7. **Full workflow:** Reference `PRODUCTION_WORKFLOW.md`

---

*Last Updated: April 2026*
*For questions, refer to script docstrings: `python3 scripts/youtube_uploader.py --help`*
