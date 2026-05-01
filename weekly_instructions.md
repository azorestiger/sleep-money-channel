# Daily Agent Instructions

You are a daily automation agent for the Sleep Money Affirmations YouTube channel.
This repo is cloned at your working directory.
The script rotates through 5 templates based on day of week (Mon=Success, Tue=Financial Abundance, Wed=Debt Freedom, Thu=Gratitude, Fri=Health & Vitality).

## STEP 1 — Install dependencies
```bash
pip3 install imageio[ffmpeg] pillow --quiet
```

## STEP 2 — Generate the video
```bash
python3 make_video.py
```
Wait for it to complete (15-20 minutes). It saves output to `/tmp/sleep_video/metadata.json`.

## STEP 3 — Upload to YouTube as PRIVATE via Blotato MCP

1. Read `/tmp/sleep_video/metadata.json` — get title, description, tags, filename, video_path.
2. Call `blotato_create_presigned_upload_url` with the filename.
3. Upload the file:
   ```bash
   curl -X PUT "<presignedUrl>" --data-binary "@<video_path>" -H "Content-Type: video/mp4"
   ```
   Confirm HTTP 200.
4. Call `blotato_create_post`:
   - accountId: "35057"
   - platform: "youtube"
   - title: (from metadata)
   - text: (description from metadata)
   - mediaUrls: [publicUrl from step 2]
   - **privacyStatus: "private"** ← upload private, not public
   - shouldNotifySubscribers: false
   - isMadeForKids: false
5. Poll `blotato_get_post_status` every 15 seconds until published or failed.
6. Save the YouTube URL from the response.

## STEP 4 — Email review notification via Gmail MCP

Send an email to **azorestiger@gmail.com** with:
- **Subject**: `🎬 Sleep Money Affirmations — New Video Ready to Review`
- **Body**:
  ```
  Your new Sleep Money Affirmations video has been uploaded privately and is ready for your review.

  Title: [title from metadata]

  Watch it here (private link): [YouTube URL from step 3]

  When you're happy with it:
  → Go to YouTube Studio
  → Click the video
  → Change visibility from Private to Public

  Reply to this email or open Claude Code to make any changes before publishing.
  ```

The job is complete when the email is sent.
