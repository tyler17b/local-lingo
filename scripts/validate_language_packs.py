#!/usr/bin/env python3
"""Validate packaged Local Lingo language JSON without Home Assistant."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "local_lingo" / "languages"
REQUIRED = {"id", "target_text", "source_text", "category", "difficulty"}


def main() -> int:
    errors: list[str] = []
    for directory in sorted(path for path in ROOT.iterdir() if path.is_dir()):
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        items = json.loads((directory / "vocabulary.core.json").read_text(encoding="utf-8"))
        ids: set[str] = set()
        for index, item in enumerate(items):
            missing = REQUIRED - item.keys()
            if missing:
                errors.append(f"{directory.name}[{index}] missing {sorted(missing)}")
            item_id = item.get("id")
            if item_id in ids:
                errors.append(f"{directory.name} duplicate id: {item_id}")
            ids.add(item_id)
        print(f"{manifest['name']}: {len(items)} starter entries")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
