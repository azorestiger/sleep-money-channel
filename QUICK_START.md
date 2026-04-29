# 🚀 Sleep Money Affirmations - Quick Start Guide

## Get Running in 5 Steps

### 1️⃣ Install Dependencies
```bash
cd /Users/azorestiger/Claude\ 4:27/sleep-money-channel
pip install -r requirements.txt
```

### 2️⃣ Create YouTube API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Sleep Money Channel"
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON file → Rename to `config/client_secrets.json`

### 3️⃣ Generate First Video
```bash
python3 scripts/video_generator.py \
  --template templates/financial_abundance_8hr.json \
  --music "path/to/your/music.mp3" \
  --output "first_video.mp4"
```

**Need background music?**
- YouTube Audio Library (free, built-in)
- Epidemic Sound (paid, professional)
- Pixabay (free, diverse)
- Pexels Music (free)

### 4️⃣ Create Content Schedule
```bash
python3 scripts/scheduler.py
```

This generates:
- 30-day upload calendar
- Optimal posting times
- CSV export for your calendar app

### 5️⃣ Upload to YouTube
```bash
python3 scripts/youtube_uploader.py \
  --file "first_video.mp4" \
  --metadata "config/metadata_template.json"
```

---

## 📝 Managing Daily Affirmations

### Add New Affirmations Daily
```bash
# Option 1: Add directly from command line
python3 scripts/affirmations_manager.py --add "I am worthy of abundance" "Money flows to me easily"

# Option 2: Import from text file
# Edit daily_affirmations.txt with your affirmations, then:
python3 scripts/affirmations_manager.py --import-file daily_affirmations.txt
```

### Update Templates with Fresh Affirmations
```bash
# Update financial template with latest affirmations
python3 scripts/affirmations_manager.py --update-template financial_abundance_8hr.json --category financial
```

### View Your Affirmations Database
```bash
python3 scripts/affirmations_manager.py --stats
```

### Export Affirmations for Review
```bash
python3 scripts/affirmations_manager.py --export financial --export financial_affirmations.txt
```

---

## 📂 File Structure

```
sleep-money-channel/
├── scripts/
│   ├── youtube_uploader.py      # YouTube upload automation
│   ├── video_generator.py       # Video creation from templates
│   └── scheduler.py             # Upload scheduling
├── templates/
│   ├── financial_abundance_8hr.json
│   ├── debt_freedom_8hr.json
│   └── success_career_8hr.json
├── config/
│   ├── channel_setup.json       # Channel branding & SEO
│   ├── client_secrets.json      # YouTube API (create yourself)
│   ├── batch_upload_example.json
│   └── upload_schedule.json     # Auto-generated schedule
├── output_videos/               # Generated videos go here
├── CHANNEL_SETUP.md             # Complete channel setup guide
├── PRODUCTION_WORKFLOW.md       # Full production workflow
├── QUICK_START.md              # This file
└── requirements.txt             # Python dependencies
```

---

## 🎬 Recommended Workflow

### Week 1: Setup & Production
1. Install dependencies
2. Set up YouTube API credentials
3. Generate 5-10 videos using templates
4. Create thumbnails (Canva)
5. Prepare metadata (use `channel_setup.json` template)

### Week 2: Launch
1. Upload first 5 videos
2. Create YouTube playlists
3. Set up branding (banner, profile pic)
4. Create Shorts (30-60 sec clips)
5. Share to TikTok/Instagram

### Week 3+: Scale
1. Upload 3-4 videos per week
2. Create 2-3 Shorts daily
3. Monitor analytics
4. Engage with community
5. Optimize based on performance

---

## 🎯 Key Tools & Links

| Task | Tool | Link | Cost |
|------|------|------|------|
| Thumbnails | Canva | [canva.com](https://canva.com) | Free/Paid |
| Background Music | YouTube Audio Library | [YouTube Studio](https://studio.youtube.com) | Free |
| Video Editing | CapCut | [capcut.com](https://capcut.com) | Free |
| Narration | Text-to-Speech | Descript or Google Cloud | Free/Paid |
| Analytics | YouTube Studio | Built-in | Free |
| Scheduling | GhostPing or Buffer | Varies | Paid |

---

## 🔗 API Setup (Detailed)

### Get YouTube API Access:

1. **Create Project**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Click "Select a project" → "New Project"
   - Name: "Sleep Money Channel"
   - Click "Create"

2. **Enable YouTube API**
   - Search for "YouTube Data API v3"
   - Click "Enable"

3. **Create Credentials**
   - Click "Create Credentials"
   - Application type: "Desktop app"
   - Click "Create OAuth client ID"
   - Consent screen: Fill in app name "Sleep Money Affirmations"

4. **Download JSON**
   - Download the JSON file
   - Save as: `config/client_secrets.json`

5. **First Upload (will prompt login)**
   ```bash
   python3 scripts/youtube_uploader.py --help
   ```
   - Browser will open for YouTube login
   - Grants permission to upload videos
   - Token saves to `config/token.pickle`

---

## 🛠️ Troubleshooting

### "Video file not found"
```bash
# Make sure video exists:
ls -la output_videos/
```

### "YouTube API error: 403"
- Regenerate credentials
- Check `config/client_secrets.json` exists
- Delete `config/token.pickle` to re-authenticate

### "FFmpeg not found"
```bash
# Install FFmpeg (required for video generation)
brew install ffmpeg
```

### "No watch time on videos"
- Ensure videos are PUBLIC (not private/unlisted)
- Add to playlists (boosts watch time)
- Create compelling thumbnails
- Improve video titles for SEO

---

## 💡 Pro Tips

1. **Create playlists immediately**
   - Group by theme (Money, Success, Sleep)
   - Playlists = massive watch time increase

2. **Use Shorts relentlessly**
   - 30-60 second clips from full videos
   - Post 5-7x per week
   - Drives massive traffic to full videos

3. **Pin a comment**
   - Welcome message + CTA
   - Link to playlists
   - Link to social media

4. **Optimize titles for search**
   - Include keywords: sleep, affirmations, money
   - Format: `[LENGTH] Sleep Affirmations for [BENEFIT]`

5. **Build email list early**
   - Start newsletter (Substack is free)
   - Add signup link in descriptions
   - Email new video announcements

6. **Analyze performance weekly**
   - Watch YouTube analytics
   - See where viewers drop-off
   - Adjust video length/pacing accordingly

---

## 📊 Success Metrics (Month 1)

| Metric | Target |
|--------|--------|
| Subscribers | 100-500 |
| Total views | 5,000-20,000 |
| Hours watched | 100-500 |
| Avg watch duration | 30+ minutes |
| Click-through rate | 3-5% |

---

## 📚 Full Documentation

For **complete details**, see:
- **Channel Setup:** [CHANNEL_SETUP.md](CHANNEL_SETUP.md)
- **Production:** [PRODUCTION_WORKFLOW.md](PRODUCTION_WORKFLOW.md)
- **Scripts:** Review Python files in `scripts/`

---

## 🚀 Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set up YouTube API credentials
3. Generate first video: `python3 scripts/video_generator.py ...`
4. Upload to YouTube: `python3 scripts/youtube_uploader.py ...`
5. Check [CHANNEL_SETUP.md](CHANNEL_SETUP.md) for branding & optimization

**You've got this! 💪💰**
