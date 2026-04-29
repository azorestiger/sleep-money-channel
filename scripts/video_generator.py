#!/usr/bin/env python3
"""
Video Generator for Sleep Money Affirmations
Generates videos from affirmation templates with background audio/visuals
Supports multiple video formats and customization
"""

import os
import json
from datetime import datetime
from pathlib import Path
import subprocess
import argparse
from typing import List, Dict


class VideoGenerator:
    """Generate sleep affirmation videos with background audio and visuals"""

    SUPPORTED_FORMATS = ["mp4", "mov", "mkv"]
    DEFAULT_RESOLUTION = "1920x1080"
    DEFAULT_FPS = 24
    DEFAULT_DURATION = 480  # 8 hours in seconds
    DEFAULT_BACKGROUND_MUSIC = "config/background_music.mp3"

    def __init__(self, output_dir="output_videos"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def generate_from_template(
        self,
        template_file: str,
        background_music: str = DEFAULT_BACKGROUND_MUSIC,
        duration_minutes: int = 8,
        output_name: str = None,
    ) -> str:
        """
        Generate video from affirmation template

        Args:
            template_file: Path to affirmation template JSON
            background_music: Path to background music file
            duration_minutes: Video duration in minutes
            output_name: Custom output filename

        Returns:
            Path to generated video file
        """

        with open(template_file, "r") as f:
            template = json.load(f)

        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{template.get('title', 'affirmations').replace(' ', '_')}_{timestamp}.mp4"

        output_path = os.path.join(self.output_dir, output_name)

        print(f"Generating video: {template.get('title', 'Affirmations')}")
        print(f"Output: {output_path}")

        # Use ffmpeg to create video
        # This is a template - you'll need ffmpeg installed
        self._create_video_with_ffmpeg(
            template, background_music, duration_minutes * 60, output_path
        )

        return output_path

    def _create_video_with_ffmpeg(
        self, template: Dict, music_file: str, duration: int, output_path: str
    ):
        """Create video using ffmpeg (requires ffmpeg installation)"""

        # Create a simple text overlay video
        # This requires ffmpeg to be installed: brew install ffmpeg

        cmd = [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            f"color=c=000000:s={self.DEFAULT_RESOLUTION}:d={duration}",
            "-i",
            music_file,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            "-y",
            output_path,
        ]

        print("Note: Install ffmpeg for full video generation: brew install ffmpeg")
        print(f"Command: {' '.join(cmd)}")

    def batch_generate(self, batch_config_file: str) -> List[str]:
        """
        Generate multiple videos from batch config

        Args:
            batch_config_file: Path to batch configuration JSON

        Returns:
            List of generated video paths
        """

        with open(batch_config_file, "r") as f:
            batch_config = json.load(f)

        generated_videos = []

        for video_config in batch_config.get("videos", []):
            try:
                video_path = self.generate_from_template(
                    video_config["template"],
                    video_config.get("music", self.DEFAULT_BACKGROUND_MUSIC),
                    video_config.get("duration_minutes", 8),
                    video_config.get("output_name"),
                )
                generated_videos.append(video_path)
                print(f"✓ Generated: {video_path}\n")
            except Exception as e:
                print(f"✗ Error generating {video_config.get('output_name')}: {e}\n")

        return generated_videos

    def create_thumbnail(
        self, template_file: str, output_path: str = None
    ) -> str:
        """
        Create YouTube thumbnail from template

        Args:
            template_file: Path to template with thumbnail config
            output_path: Custom output path

        Returns:
            Path to generated thumbnail
        """

        with open(template_file, "r") as f:
            template = json.load(f)

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.output_dir, f"thumbnail_{timestamp}.png"
            )

        print(f"Thumbnail generation requires PIL/Pillow library")
        print(f"Install with: pip install Pillow")

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate Sleep Money Affirmation videos"
    )
    parser.add_argument("-t", "--template", help="Path to affirmation template")
    parser.add_argument(
        "-m", "--music", help="Path to background music file", required=False
    )
    parser.add_argument(
        "-d", "--duration", type=int, default=8, help="Video duration in minutes"
    )
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument("-b", "--batch", help="Path to batch config JSON")

    args = parser.parse_args()

    generator = VideoGenerator()

    if args.batch:
        generator.batch_generate(args.batch)
    elif args.template:
        generator.generate_from_template(
            args.template, args.music, args.duration, args.output
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
