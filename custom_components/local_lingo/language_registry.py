"""Load and validate packaged language packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import VocabularyItem


class LanguageRegistry:
    """Read-only registry of packaged language content."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._languages: dict[str, dict[str, Any]] = {}
        self._vocabulary: dict[str, list[VocabularyItem]] = {}

    async def async_load(self) -> None:
        """Load all language directories."""
        self._languages.clear()
        self._vocabulary.clear()
        for directory in sorted(path for path in self._root.iterdir() if path.is_dir()):
            manifest_path = directory / "manifest.json"
            vocabulary_path = directory / "vocabulary.core.json"
            if not manifest_path.exists() or not vocabulary_path.exists():
                continue

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            code = manifest["code"]
            vocabulary = json.loads(vocabulary_path.read_text(encoding="utf-8"))
            self._validate_vocabulary(code, vocabulary)
            self._languages[code] = manifest
            self._vocabulary[code] = vocabulary

    @staticmethod
    def _validate_vocabulary(code: str, vocabulary: list[dict[str, Any]]) -> None:
        ids: set[str] = set()
        for index, item in enumerate(vocabulary):
            for required in ("id", "target_text", "source_text", "category", "difficulty"):
                if not item.get(required):
                    raise ValueError(
                        f"Language {code} item {index} is missing required field {required}"
                    )
            if item["id"] in ids:
                raise ValueError(f"Language {code} contains duplicate id {item['id']}")
            ids.add(item["id"])

    def list_languages(self) -> list[dict[str, Any]]:
        return [self._languages[key] for key in sorted(self._languages)]

    def has_language(self, code: str) -> bool:
        return code in self._languages

    def vocabulary(self, code: str) -> list[VocabularyItem]:
        if code not in self._vocabulary:
            raise KeyError(f"Unknown language: {code}")
        return self._vocabulary[code]
