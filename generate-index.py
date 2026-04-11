#!/usr/bin/env python3
"""Generate index.json from amendment markdown frontmatter.

Reads all *.md files in the repo root, extracts YAML frontmatter,
and writes a sorted index.json. Skips files without valid frontmatter.
"""

import json
import pathlib
import sys
import re

FRONTMATTER_RE = re.compile(r"^---\s*\n(.+?)\n---", re.DOTALL)


def parse_frontmatter(text):
    """Extract YAML frontmatter as a dict (minimal parser, no PyYAML dependency)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None

    meta = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"').strip("'")
        # Convert numeric strings
        if value.isdigit():
            value = int(value)
        meta[key.strip()] = value
    return meta


def main():
    repo_root = pathlib.Path(__file__).parent
    index = []

    for md_file in sorted(repo_root.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        if not meta or "slug" not in meta:
            print(f"  skipping {md_file.name} (no frontmatter or missing slug)")
            continue
        index.append(meta)
        print(f"  indexed {meta['slug']}")

    index.sort(key=lambda a: a.get("order", 99))

    out = repo_root / "index.json"
    out.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(index)} amendments to index.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
