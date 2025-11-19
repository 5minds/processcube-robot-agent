#!/usr/bin/env python3
"""
Extract release notes for a specific version from CHANGELOG.md

This script is used by GitHub Actions to automatically extract release notes
from the CHANGELOG.md file and use them in GitHub Releases.

Usage:
    python scripts/extract_release_notes.py <version>

Example:
    python scripts/extract_release_notes.py 0.0.1
    python scripts/extract_release_notes.py v0.0.1
"""

import re
import sys
from pathlib import Path


def extract_version_section(version_str: str) -> str | None:
    """
    Extract release notes for a specific version from CHANGELOG.md

    Args:
        version_str: Version to extract (with or without 'v' prefix)

    Returns:
        Release notes section or None if not found
    """
    # Normalize version (remove 'v' prefix if present)
    version = version_str.lstrip('v')

    # Read CHANGELOG.md
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"

    if not changelog_path.exists():
        print(f"❌ CHANGELOG.md not found at {changelog_path}", file=sys.stderr)
        return None

    changelog_content = changelog_path.read_text(encoding='utf-8')

    # Pattern: ## [version] - date ... up to next ## section or EOF
    # Matches: ## [0.0.1] - 2025-11-19
    #          ### 🎉 Initial Release
    #          ...
    #          (continues until next ## or end of file)
    pattern = rf"## \[{re.escape(version)}\].*?(?=\n## |\Z)"

    match = re.search(pattern, changelog_content, re.DOTALL)

    if not match:
        print(
            f"❌ Version [{version}] not found in CHANGELOG.md",
            file=sys.stderr
        )
        return None

    section = match.group(0).strip()

    # Remove the version header (we'll add it separately in the action)
    # Optional: keep just the content below the header
    lines = section.split('\n')
    if len(lines) > 1:
        # Keep everything except the first line (version header)
        content = '\n'.join(lines[1:]).strip()
        return content

    return section


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python extract_release_notes.py <version>", file=sys.stderr)
        print("Example: python extract_release_notes.py 0.0.1", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    notes = extract_version_section(version)

    if notes:
        print(notes)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()