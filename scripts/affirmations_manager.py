#!/usr/bin/env python3
"""
Affirmations Manager for Sleep Money Affirmations
Manages daily affirmation collections and updates templates automatically
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class AffirmationsManager:
    """Manage and organize affirmations for the sleep money channel"""

    def __init__(self, affirmations_db="config/affirmations_database.json"):
        self.affirmations_db = Path(affirmations_db)
        self.templates_dir = Path("templates")
        self.db = self._load_database()

    def _load_database(self) -> Dict:
        """Load or create affirmations database"""
        if self.affirmations_db.exists():
            with open(self.affirmations_db, "r") as f:
                return json.load(f)
        return {
            "categories": {
                "financial": [],
                "success": [],
                "debt_free": [],
                "abundance": [],
                "general": []
            },
            "daily_imports": [],
            "last_updated": None,
            "total_affirmations": 0
        }

    def _save_database(self):
        """Save database to file"""
        self.db["last_updated"] = datetime.now().isoformat()
        self.db["total_affirmations"] = sum(len(affs) for affs in self.db["categories"].values())

        with open(self.affirmations_db, "w") as f:
            json.dump(self.db, f, indent=2)

    def add_affirmations(self, affirmations: List[str], category: str = "financial", source: str = "daily_import"):
        """
        Add new affirmations to the database

        Args:
            affirmations: List of affirmation strings
            category: Category to add to (financial, success, debt_free, abundance, general)
            source: Source of the affirmations (for tracking)
        """
        if category not in self.db["categories"]:
            self.db["categories"][category] = []

        # Add new affirmations (avoid duplicates)
        existing = set(self.db["categories"][category])
        new_affirmations = [aff for aff in affirmations if aff not in existing]

        self.db["categories"][category].extend(new_affirmations)

        # Track the import
        import_record = {
            "date": datetime.now().isoformat(),
            "source": source,
            "category": category,
            "count": len(new_affirmations),
            "affirmations": new_affirmations
        }
        self.db["daily_imports"].append(import_record)

        self._save_database()

        print(f"✓ Added {len(new_affirmations)} new affirmations to '{category}' category")
        if len(affirmations) > len(new_affirmations):
            print(f"  (Skipped {len(affirmations) - len(new_affirmations)} duplicates)")

    def get_affirmations(self, category: str, count: Optional[int] = None) -> List[str]:
        """Get affirmations from a specific category"""
        if category not in self.db["categories"]:
            return []

        affirmations = self.db["categories"][category]
        if count:
            return affirmations[:count]
        return affirmations

    def update_template(self, template_file: str, category: str, section_name: str = "Money Flow Affirmations"):
        """
        Update a template with fresh affirmations from the database

        Args:
            template_file: Path to template JSON file
            category: Category to pull affirmations from
            section_name: Which section in the template to update
        """
        template_path = self.templates_dir / template_file
        if not template_path.exists():
            print(f"❌ Template file not found: {template_path}")
            return

        # Load template
        with open(template_path, "r") as f:
            template = json.load(f)

        # Get fresh affirmations
        fresh_affirmations = self.get_affirmations(category, 12)  # Get up to 12

        if not fresh_affirmations:
            print(f"❌ No affirmations found in category '{category}'")
            return

        # Find and update the section
        section_found = False
        for section in template.get("sections", []):
            if section.get("section_name") == section_name:
                section["affirmations"] = fresh_affirmations
                section_found = True
                break

        if not section_found:
            print(f"❌ Section '{section_name}' not found in template")
            return

        # Save updated template
        with open(template_path, "w") as f:
            json.dump(template, f, indent=2)

        print(f"✓ Updated {template_file} with {len(fresh_affirmations)} fresh affirmations")

    def show_stats(self):
        """Display database statistics"""
        print("\n=== AFFIRMATIONS DATABASE STATS ===")
        print(f"Total affirmations: {self.db['total_affirmations']}")
        print(f"Last updated: {self.db.get('last_updated', 'Never')}")
        print(f"Daily imports: {len(self.db['daily_imports'])}")

        print("\nBy Category:")
        for category, affirmations in self.db["categories"].items():
            print(f"  {category}: {len(affirmations)} affirmations")

        print("\nRecent Imports:")
        for import_record in self.db["daily_imports"][-3:]:  # Last 3
            print(f"  {import_record['date'][:10]}: {import_record['count']} from {import_record['source']}")

    def export_category(self, category: str, filename: str):
        """Export a category to a text file"""
        affirmations = self.get_affirmations(category)
        if not affirmations:
            print(f"❌ No affirmations in category '{category}'")
            return

        with open(filename, "w") as f:
            f.write(f"# {category.title()} Affirmations\n\n")
            for i, aff in enumerate(affirmations, 1):
                f.write(f"{i}. {aff}\n")

        print(f"✓ Exported {len(affirmations)} affirmations to {filename}")

    def import_from_file(self, filename: str, category: str = "financial"):
        """Import affirmations from a text file"""
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            return

        with open(filename, "r") as f:
            content = f.read()

        # Try to parse as numbered list
        affirmations = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                if line[0].isdigit():
                    line = line.split(')', 1)[-1].strip() if ')' in line else line.split('.', 1)[-1].strip()
                elif line.startswith('-'):
                    line = line[1:].strip()
                affirmations.append(line)

        if affirmations:
            self.add_affirmations(affirmations, category, f"file_import_{filename}")
        else:
            print("❌ No affirmations found in file. Expected format: '1. Affirmation text' or '- Affirmation text'")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Manage affirmations for Sleep Money Affirmations")
    parser.add_argument("--add", nargs="+", help="Add affirmations (provide as arguments)")
    parser.add_argument("--category", default="financial", help="Category for affirmations")
    parser.add_argument("--import-file", help="Import affirmations from text file")
    parser.add_argument("--update-template", help="Update template with fresh affirmations")
    parser.add_argument("--export", help="Export category to file")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")

    args = parser.parse_args()

    manager = AffirmationsManager()

    if args.add:
        manager.add_affirmations(args.add, args.category)
    elif args.import_file:
        manager.import_from_file(args.import_file, args.category)
    elif args.update_template:
        manager.update_template(args.update_template, args.category)
    elif args.export:
        manager.export_category(args.category, args.export)
    elif args.stats:
        manager.show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
