# Sleep Money Affirmations - Complete Production Workflow

## Overview
This document outlines the complete workflow from affirmation creation to YouTube upload for maximum efficiency.

---

## 📋 Phase 1: Content Planning & Scripting

### 1. Choose Theme
Select from: `financial`, `debt-free`, `success`, `abundance`, `manifestation`

### 2. Create Affirmation Script
**Template files available in `templates/`:**
- `financial_abundance_8hr.json` - Wealth & money flow
- `debt_freedom_8hr.json` - Debt elimination
- `success_career_8hr.json` - Career & income growth

**Script Requirements:**
- 12-20 unique affirmations per theme
- Each affirmation: 15-30 words max
- Pacing: 8-second pause between each affirmation
- 4-6 repetitions per affirmation (for 8-hour video)

### 3. Organize in JSON Format
```json
{
  "title": "Video Title",
  "theme": "financial",
  "duration_minutes": 480,
  "affirmations": [
    "Money flows to me easily",
    "I am wealthy and abundant"
  ]
}
```

---

## 🎬 Phase 2: Video Production

### Option A: DIY Production (Recommended for Beginners)

#### Requirements:
- FFmpeg installed (`brew install ffmpeg`)
- Audacity (free audio editor) - [audacityteam.org](https://audacityteam.org)
- Background music (royalty-free sources below)

#### Steps:
1. **Record narration** (Audacity or garage band)
   - Use calm, soothing voice
   - Add 8-10 second pauses between affirmations
   - Export as MP3

2. **Find background music** (royalty-free sources)
   - Epidemic Sound
   - AudioJungle
   - YouTube Audio Library
   - Pixabay (free)
   - Search: "8-hour sleep music," "ambient meditation"

3. **Generate video** using script:
   ```bash
   cd /Users/azorestiger/Claude\ 4:27/sleep-money-channel
   python3 scripts/video_generator.py \
     --template templates/financial_abundance_8hr.json \
     --music "your_music.mp3" \
     --duration 480 \
     --output "final_video.mp4"
   ```

#### Video Specs:
- Resolution: 1920x1080 (Full HD)
- Frame rate: 24 fps
- Format: MP4 (H.264 codec)
- Duration: 480 minutes (8 hours)
- Background: Black gradient or nature scenes
- Text overlay: White affirmations (optional)

### Option B: Use Video Creation Tools
**Recommended platforms:**
- Descript (excellent for text-to-speech + editing)
- Adobe Premiere Pro (professional)
- CapCut (free, easy)
- InShot (mobile-friendly)

**Settings:**
- Background: Calming visuals (stars, nature, gradient)
- Text: Display affirmations on screen (increases retention)
- Audio: Narrator (can use text-to-speech) + background music

---

## 🖼️ Phase 3: Thumbnail & Metadata Creation

### Create Thumbnail
**Specifications:**
- Size: 1280x720 pixels
- Format: PNG or JPG
- Tools: Canva (free), Photoshop, or GIMP

**Design Elements:**
- Bold, readable text (e.g., "💰 MONEY SLEEP")
- Calming colors (gold, purple, white)
- Moon or prosperity symbols
- Clear contrast

### Prepare Metadata
Use the template generator:
```bash
python3 scripts/video_generator.py --create-metadata financial_abundance_8hr.json
```

**Metadata includes:**
- Title (with SEO keywords)
- Description (with affiliate links)
- Tags (15-20 tags)
- Category: People & Blogs
- Privacy: Public

---

## 📅 Phase 4: Upload Scheduling

### Step 1: Plan Schedule
```bash
python3 scripts/scheduler.py
```

This generates:
- Upload calendar for optimal times
- 30-day content roadmap
- CSV export for your calendar app

### Step 2: Add Videos to Schedule
**Best upload times:**
- **6-8 PM** (when people prep for bed) — Primary
- **6-9 AM** (morning meditation window) — Secondary
- **Frequency:** 3-4 videos per week

**Theme rotation example:**
- Monday: Financial Abundance
- Wednesday: Debt Elimination
- Friday: Success & Career
- Sunday: General Abundance

### Step 3: Configure Upload Settings
Create batch upload config (`config/batch_upload.json`):
```json
{
  "videos": [
    {
      "file": "output_videos/affirmations_01.mp4",
      "metadata": {
        "title": "8-Hour Sleep Affirmations...",
        "description": "...",
        "tags": ["sleep", "money", "affirmations"],
        "categoryId": "22"
      },
      "publish_time": "2026-04-28T20:00:00Z"
    }
  ]
}
```

---

## 🔗 Phase 5: YouTube Upload & Optimization

### Setup YouTube API Access
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project "Sleep Money Channel"
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `client_secrets.json` → `config/`

### Upload Videos
**Single upload:**
```bash
python3 scripts/youtube_uploader.py \
  --file "output_videos/affirmations_01.mp4" \
  --metadata "config/metadata_01.json"
```

**Batch upload with scheduling:**
```bash
python3 scripts/youtube_uploader.py \
  --batch "config/batch_upload.json"
```

### Post-Upload Optimization
1. **Add closed captions** (YouTube auto-generates, but review)
   - Settings → Subtitles → Auto-generate
2. **Create engaging playlist** (boosts watch time)
   - Add to relevant playlists
3. **Add cards** to other videos (internal cross-promotion)
4. **Pin comment** with call-to-action

---

## 📊 Phase 6: Distribution & Marketing

### YouTube Shorts
**Create 30-60 second clips:**
- Best affirmations from full video
- Eye-catching visuals
- Bold text overlays
- **Upload 2-3x per week** (algorithm boost)

```bash
ffmpeg -i affirmations_full.mp4 \
  -ss 00:02:00 -t 00:01:00 \
  -c:v libx264 -c:a aac \
  affirmations_short.mp4
```

### Cross-Platform Distribution
| Platform | Format | Frequency | Notes |
|----------|--------|-----------|-------|
| TikTok | 30-60 sec clips | Daily | Use trending sounds |
| Instagram Reels | 30-60 sec | 3x/week | Link to YouTube |
| Spotify | Audio-only podcast version | Weekly | Monetizable |
| Pinterest | Affirmation graphics | 2-3x/week | Drive traffic to YT |
| Reddit | Share in communities | 2x/week | r/manifestation, r/sleep |

### Email List (Free Tool: Substack/Mailchimp)
- Build email list from YouTube
- Weekly manifestation tips
- New video announcements
- Exclusive affirmations

---

## 💰 Phase 7: Monetization Setup

### 1. **Ad Revenue**
- Eligible after: 1K subscribers + 4K watch hours
- CPM typical range: $2-8 per 1000 views
- Expected earnings: Grows with viewership

### 2. **Affiliate Marketing**
**Links in description:**
- Meditation apps (Calm, Headspace)
- Affirmation books & courses
- Sleep tech (weighted blankets, sound machines)
- Amazon Associate program

**Template:**
```
📚 Resources Mentioned:
→ [Best Meditation App] - [Affiliate Link]
→ [Sleep Tech Recommendation] - [Link]
```

### 3. **Channel Memberships** (after 1K subs)
- Tiers: $0.99, $4.99, $9.99
- Perks: Custom affirmations, early access, community

### 4. **Digital Products**
- Affirmation journal templates
- 30-day manifestation challenges
- Custom affirmation packages
- Sell on Gumroad/Etsy

---

## 🔄 Ongoing Management Checklist

### Daily
- [ ] Respond to all comments
- [ ] Check analytics for trending content
- [ ] Engage with similar channels (like/comment)

### Weekly
- [ ] Upload new video
- [ ] Create 2-3 Shorts
- [ ] Post community update
- [ ] Share to social media

### Monthly
- [ ] Review analytics for top performers
- [ ] Adjust strategy based on metrics
- [ ] Plan next month's content calendar
- [ ] Update SEO tags based on trends

### Quarterly
- [ ] Analyze 90-day performance
- [ ] Identify winning themes
- [ ] Plan seasonal content boosts
- [ ] Research new monetization opportunities

---

## 🛠️ Tools Summary

| Tool | Purpose | Cost | Notes |
|------|---------|------|-------|
| Audacity | Record narration | FREE | Open-source audio editor |
| FFmpeg | Video encoding | FREE | Command-line video tool |
| Canva | Thumbnail design | FREE/Paid | Easy drag-and-drop |
| YouTube Studio | Upload & analytics | FREE | Built into YouTube |
| Descript | Text-to-speech + editing | Paid | Excellent for affirmations |
| TubeBuddy | SEO optimization | Paid | Keyword research |
| VidIQ | Analytics | Free/Paid | Video intelligence |
| Epidemic Sound | Background music | Paid | High quality, legal |

---

## 📈 Success Metrics

### Track These:
- **Watch time**: Target 30+ min per viewer
- **Click-through rate**: 4%+ on description links
- **Subscriber growth**: 10-20% monthly growth
- **Playlist adds**: High = strong content fit
- **Engagement**: Comments, likes, shares

### Adjust If:
- Watch time drops below 10 min → Make videos shorter
- No comments → Engage more in comments
- Low click-through → Better description/CTA
- Subscribers declining → Review thumbnails/titles

---

## 🚀 Quick Start Checklist

- [ ] Record affirmations script
- [ ] Find 5+ royalty-free background music tracks
- [ ] Create first thumbnail in Canva
- [ ] Prepare metadata (title, description, tags)
- [ ] Set up YouTube API access
- [ ] Generate first video with video_generator.py
- [ ] Upload to YouTube with youtube_uploader.py
- [ ] Create 3 Shorts clips
- [ ] Post to TikTok/Instagram
- [ ] Start weekly upload schedule

**Start with this, then optimize based on analytics!**
