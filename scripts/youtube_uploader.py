#!/usr/bin/env python3
"""
YouTube Uploader for Sleep Money Affirmations Channel
Automates video upload, scheduling, and metadata management
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_resources import youtube_v3
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import argparse

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "config/client_secrets.json"
TOKEN_FILE = "config/token.pickle"


class YouTubeUploader:
    def __init__(self):
        self.youtube = self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube API using OAuth2"""
        creds = None

        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)

        return build("youtube", "v3", credentials=creds)

    def upload_video(self, file_path, metadata):
        """
        Upload video to YouTube with metadata
        
        Args:
            file_path: Path to video file
            metadata: Dict with title, description, tags, categoryId, etc.
        """
        if not os.path.exists(file_path):
            print(f"Error: Video file not found - {file_path}")
            return None

        request_body = {
            "snippet": {
                "title": metadata.get("title", "Sleep Money Affirmations"),
                "description": metadata.get("description", ""),
                "tags": metadata.get("tags", []),
                "categoryId": metadata.get("categoryId", "22"),  # 22 = People & Blogs
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en",
            },
            "status": {
                "privacyStatus": metadata.get("privacyStatus", "public"),
                "publishAt": metadata.get(
                    "publishAt", None
                ),  # ISO 8601 format for scheduling
            },
        }

        media = MediaFileUpload(file_path, chunksize=256 * 1024, resumable=True)

        print(f"Uploading: {metadata.get('title', 'Untitled')}")
        request = self.youtube.videos().insert(
            part="snippet,status", body=request_body, media_body=media
        )

        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"Upload progress: {progress}%")
            except Exception as e:
                print(f"Error during upload: {e}")
                return None

        video_id = response["id"]
        print(f"✓ Video uploaded successfully! Video ID: {video_id}")
        return video_id

    def schedule_upload(self, file_path, metadata, publish_time):
        """
        Schedule video for publishing at specific time
        
        Args:
            file_path: Path to video file
            metadata: Video metadata dict
            publish_time: Datetime object for publication
        """
        metadata["publishAt"] = publish_time.isoformat() + "Z"
        metadata["privacyStatus"] = "scheduled"
        return self.upload_video(file_path, metadata)

    def batch_upload(self, videos_list):
        """
        Upload multiple videos from a JSON list
        
        Args:
            videos_list: List of dicts with 'file' and 'metadata' keys
        """
        successful = []
        failed = []

        for video in videos_list:
            try:
                video_id = self.upload_video(video["file"], video["metadata"])
                if video_id:
                    successful.append(
                        {"title": video["metadata"]["title"], "video_id": video_id}
                    )
            except Exception as e:
                failed.append({"title": video["metadata"]["title"], "error": str(e)})

        print(f"\n✓ Successful uploads: {len(successful)}")
        print(f"✗ Failed uploads: {len(failed)}")
        return successful, failed


def load_batch_config(config_file):
    """Load batch upload configuration from JSON"""
    with open(config_file, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Upload videos to YouTube Sleep Money Affirmations channel"
    )
    parser.add_argument("-f", "--file", help="Path to video file")
    parser.add_argument("-c", "--config", help="Path to batch config JSON file")
    parser.add_argument("-s", "--schedule", help="Publish time (ISO 8601 format)")
    parser.add_argument("-m", "--metadata", help="Path to metadata JSON file")

    args = parser.parse_args()

    uploader = YouTubeUploader()

    if args.config:
        # Batch upload mode
        config = load_batch_config(args.config)
        uploader.batch_upload(config["videos"])
    elif args.file and args.metadata:
        # Single upload mode
        with open(args.metadata, "r") as f:
            metadata = json.load(f)

        if args.schedule:
            publish_time = datetime.fromisoformat(args.schedule.replace("Z", "+00:00"))
            uploader.schedule_upload(args.file, metadata, publish_time)
        else:
            uploader.upload_video(args.file, metadata)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
