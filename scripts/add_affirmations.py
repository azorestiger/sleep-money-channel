#!/usr/bin/env python3
"""
Add affirmations from daily_affirmations.txt into all three video templates.

Usage: python3 scripts/add_affirmations.py

- Lines starting with # are comments (ignored)
- Numbered lines like "1. I am..." or plain lines are affirmations
- After processing, affirmations are archived in the txt file with a datestamp
- Templates updated: success_career_8hr, financial_abundance_8hr, debt_freedom_8hr
"""

import json, re
from datetime import date
from pathlib import Path

REPO = Path(__file__).parent.parent
AFFIRMATIONS_FILE = REPO / "daily_affirmations.txt"
TEMPLATES = [
    REPO / "templates" / "success_career_8hr.json",
    REPO / "templates" / "financial_abundance_8hr.json",
    REPO / "templates" / "debt_freedom_8hr.json",
]
SECTION_NAME = "User Additions"


def parse_affirmations(filepath: Path) -> list:
    lines = filepath.read_text().splitlines()
    affirmations = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Strip leading number like "1." or "1)"
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if cleaned:
            affirmations.append(cleaned)
    return affirmations


def add_to_template(template_path: Path, affirmations: list):
    data = json.loads(template_path.read_text())

    # Check if a User Additions section already exists — append to it
    for section in data["sections"]:
        if section.get("section_name") == SECTION_NAME:
            existing = section.get("affirmations", [])
            # Avoid duplicates
            for a in affirmations:
                if a not in existing:
                    existing.append(a)
            section["affirmations"] = existing
            print(f"  Updated existing '{SECTION_NAME}' section → {len(existing)} affirmations total")
            template_path.write_text(json.dumps(data, indent=2))
            return

    # No existing section — insert before the closing content section
    new_section = {
        "section_name": SECTION_NAME,
        "affirmations": affirmations,
        "repeat_times": 4
    }
    # Insert before the last section (closing/empowerment content)
    data["sections"].insert(-1, new_section)
    print(f"  Added new '{SECTION_NAME}' section with {len(affirmations)} affirmations")
    template_path.write_text(json.dumps(data, indent=2))


def archive_in_file(filepath: Path, affirmations: list):
    today = date.today().strftime("%Y-%m-%d")
    existing = filepath.read_text()

    # Build archive block
    archive_lines = [f"\n# --- Added to templates on {today} ---"]
    for i, a in enumerate(affirmations, 1):
        archive_lines.append(f"# {i}. {a}")
    archive_block = "\n".join(archive_lines) + "\n"

    # Remove the active (non-comment) lines and append archive
    kept_lines = []
    for line in existing.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            continue  # Remove active affirmations
        kept_lines.append(line)

    new_content = "\n".join(kept_lines).rstrip() + "\n" + archive_block
    filepath.write_text(new_content)


def main():
    affirmations = parse_affirmations(AFFIRMATIONS_FILE)

    if not affirmations:
        print("No new affirmations found in daily_affirmations.txt")
        print("Add lines without # to the file, then run this script.")
        return

    print(f"Found {len(affirmations)} new affirmations:")
    for a in affirmations:
        print(f"  • {a}")
    print()

    for template_path in TEMPLATES:
        print(f"{template_path.name}:")
        add_to_template(template_path, affirmations)

    archive_in_file(AFFIRMATIONS_FILE, affirmations)
    print(f"\nDone! Archived in daily_affirmations.txt. Ready for next batch.")
    print("Regenerate your videos to include the new affirmations.")


if __name__ == "__main__":
    main()
