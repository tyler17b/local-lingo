#!/usr/bin/env python3
"""Validate packaged Local Lingo language JSON without Home Assistant."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "local_lingo" / "languages"
VOCAB_REQUIRED = {"id", "target_text", "source_text", "category", "difficulty"}
SENTENCE_REQUIRED = {
    "id",
    "difficulty",
    "category",
    "prompt",
    "completed_text",
    "translation",
    "choices",
    "correct_answer",
}


def main() -> int:
    errors: list[str] = []
    for directory in sorted(path for path in ROOT.iterdir() if path.is_dir()):
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        vocabulary: list[dict] = []
        for path in sorted(directory.glob("vocabulary.*.json")):
            vocabulary.extend(json.loads(path.read_text(encoding="utf-8")))
        sentences: list[dict] = []
        for path in sorted(directory.glob("sentences.*.json")):
            sentences.extend(json.loads(path.read_text(encoding="utf-8")))

        ids: set[str] = set()
        for index, item in enumerate(vocabulary):
            missing = VOCAB_REQUIRED - item.keys()
            if missing:
                errors.append(f"{directory.name} vocabulary[{index}] missing {sorted(missing)}")
            item_id = item.get("id")
            if item_id in ids:
                errors.append(f"{directory.name} duplicate vocabulary id: {item_id}")
            ids.add(item_id)
            if item.get("difficulty") != 1:
                errors.append(f"{directory.name} vocabulary {item_id} must use difficulty 1")

        sentence_ids: set[str] = set()
        for index, item in enumerate(sentences):
            missing = SENTENCE_REQUIRED - item.keys()
            if missing:
                errors.append(f"{directory.name} sentence[{index}] missing {sorted(missing)}")
            item_id = item.get("id")
            if item_id in sentence_ids:
                errors.append(f"{directory.name} duplicate sentence id: {item_id}")
            sentence_ids.add(item_id)
            if item.get("difficulty") != 2:
                errors.append(f"{directory.name} sentence {item_id} must use difficulty 2")
            if "___" not in item.get("prompt", ""):
                errors.append(f"{directory.name} sentence {item_id} needs a ___ blank")
            if item.get("correct_answer") not in item.get("choices", []):
                errors.append(f"{directory.name} sentence {item_id} answer is missing from choices")

        print(
            f"{manifest['name']}: {len(vocabulary)} vocabulary entries, "
            f"{len(sentences)} sentence exercises"
        )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
