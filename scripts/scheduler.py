#!/usr/bin/env python3
"""
Content Scheduler for Sleep Money Affirmations
Manages upload schedule, content calendar, and automated publishing
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
import csv
from pathlib import Path


class ContentScheduler:
    """Manage content upload calendar and scheduling"""

    def __init__(self, schedule_file="config/upload_schedule.json"):
        self.schedule_file = schedule_file
        self.schedule = self._load_schedule()

    def _load_schedule(self) -> Dict:
        """Load existing schedule or create new one"""
        if Path(self.schedule_file).exists():
            with open(self.schedule_file, "r") as f:
                return json.load(f)
        return {"uploads": []}

    def _save_schedule(self):
        """Save schedule to file"""
        with open(self.schedule_file, "w") as f:
            json.dump(self.schedule, f, indent=2, default=str)

    def add_upload(
        self,
        title: str,
        publish_time: datetime,
        video_file: str,
        description: str = "",
        tags: List[str] = None,
        theme: str = "general",
    ) -> Dict:
        """
        Add video to upload schedule

        Args:
            title: Video title
            publish_time: Datetime for publication
            video_file: Path to video file
            description: Video description
            tags: List of tags
            theme: Content theme (financial, sleep, success, etc.)

        Returns:
            Upload entry dict
        """

        entry = {
            "id": len(self.schedule["uploads"]) + 1,
            "title": title,
            "publish_time": publish_time.isoformat(),
            "video_file": video_file,
            "description": description,
            "tags": tags or [],
            "theme": theme,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
        }

        self.schedule["uploads"].append(entry)
        self._save_schedule()

        print(
            f"✓ Added to schedule: {title} - {publish_time.strftime('%Y-%m-%d %H:%M')}"
        )
        return entry

    def generate_monthly_calendar(
        self, year: int, month: int, uploads_per_week: int = 3
    ) -> List[datetime]:
        """
        Generate optimal upload times for a month

        Args:
            year: Year
            month: Month (1-12)
            uploads_per_week: Number of uploads per week (default: 3)

        Returns:
            List of recommended upload datetime objects
        """

        upload_times = []

        # Best upload times: 6-8 PM (18:00-20:00) and 6-9 AM (06:00-09:00)
        time_slots = [18, 6]  # 6 PM and 6 AM
        slot_index = 0

        for day in range(1, 32):
            try:
                upload_date = datetime(year, month, day)

                # Distribute across week
                if upload_date.weekday() < 5 and len(upload_times) % (
                    7 // uploads_per_week
                ) == 0:
                    hour = time_slots[slot_index % len(time_slots)]
                    upload_time = upload_date.replace(hour=hour, minute=0)
                    upload_times.append(upload_time)
                    slot_index += 1

            except ValueError:
                break

        return upload_times

    def export_schedule_csv(self, output_file: str = "schedule.csv"):
        """Export schedule to CSV for calendar apps"""

        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "Date",
                "Time",
                "Title",
                "Theme",
                "Video File",
                "Description",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for upload in self.schedule["uploads"]:
                pub_time = datetime.fromisoformat(upload["publish_time"])
                writer.writerow(
                    {
                        "Date": pub_time.strftime("%Y-%m-%d"),
                        "Time": pub_time.strftime("%H:%M"),
                        "Title": upload["title"],
                        "Theme": upload["theme"],
                        "Video File": upload["video_file"],
                        "Description": upload["description"],
                    }
                )

        print(f"✓ Schedule exported to {output_file}")

    def get_next_uploads(self, count: int = 10) -> List[Dict]:
        """Get next scheduled uploads"""

        uploads = sorted(self.schedule["uploads"], key=lambda x: x["publish_time"])
        upcoming = [u for u in uploads if u["status"] == "scheduled"]
        return upcoming[:count]

    def display_schedule(self):
        """Display current schedule nicely"""

        print("\n=== CONTENT SCHEDULE ===\n")
        for upload in self.get_next_uploads(10):
            pub_time = datetime.fromisoformat(upload["publish_time"])
            print(f"{pub_time.strftime('%Y-%m-%d %H:%M')} | {upload['title']}")
            print(f"  Theme: {upload['theme']} | File: {upload['video_file']}\n")


def create_sample_schedule():
    """Create a sample schedule for demonstration"""

    scheduler = ContentScheduler()

    # Sample uploads for next month
    base_date = datetime.now().replace(day=1, hour=18, minute=0, second=0)

    themes = ["financial", "sleep", "success", "abundance", "debt-free", "manifestation"]
    theme_index = 0

    for day in range(1, 32, 3):  # Every 3 days
        try:
            pub_time = base_date.replace(day=day)
            if pub_time < datetime.now():
                pub_time = pub_time + timedelta(days=30)

            scheduler.add_upload(
                title=f"Sleep Affirmations - {themes[theme_index % len(themes)].title()}",
                publish_time=pub_time,
                video_file=f"videos/affirmations_{day:02d}.mp4",
                description="8-hour sleep affirmations for wealth and abundance",
                tags=[
                    "sleep",
                    "affirmations",
                    "money",
                    "meditation",
                    "manifestation",
                ],
                theme=themes[theme_index % len(themes)],
            )
            theme_index += 1
        except ValueError:
            break

    scheduler.display_schedule()
    scheduler.export_schedule_csv("config/schedule.csv")


if __name__ == "__main__":
    create_sample_schedule()
