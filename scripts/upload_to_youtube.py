#!/usr/bin/env python3
"""
Upload a video directly to YouTube using the Data API v3.
Handles large files via resumable upload. Uploads as private for review.

Usage: python3 scripts/upload_to_youtube.py --video path/to/video.mp4 --metadata path/to/metadata.json
"""

import argparse, json, time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_FILE   = Path(__file__).parent.parent / "config" / "token.json"
SECRETS_FILE = Path(__file__).parent.parent / "config" / "client_secrets.json"
SCOPES       = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_client():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, title: str, description: str, tags: list,
                 privacy: str = "private") -> str:
    youtube = get_youtube_client()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,
            "madeForKids": False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=10 * 1024 * 1024,  # 10MB chunks
                            mimetype="video/mp4", resumable=True)

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"Uploading: {title}")
    print(f"File: {video_path} ({Path(video_path).stat().st_size / 1024 / 1024:.0f} MB)")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\nUploaded! Video ID: {video_id}")
    print(f"URL: {url}")
    return url


def main():
    parser = argparse.ArgumentParser(description="Upload video to YouTube")
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--metadata", help="Path to metadata JSON file")
    parser.add_argument("--title", help="Video title (if no metadata file)")
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    args = parser.parse_args()

    if args.metadata:
        meta = json.loads(Path(args.metadata).read_text())
        title       = meta.get("title", "Sleep Money Affirmations")
        description = meta.get("description", "")
        tags        = meta.get("tags", [])
    else:
        title       = args.title or "Sleep Money Affirmations"
        description = ""
        tags        = []

    url = upload_video(args.video, title, description, tags, args.privacy)
    print(f"\nDone! Review your video at: {url}")
    return url


if __name__ == "__main__":
    main()
