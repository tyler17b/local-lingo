"""Load and validate packaged language packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SentenceExercise, VocabularyItem


class LanguageRegistry:
    """Read-only registry of packaged language content."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._languages: dict[str, dict[str, Any]] = {}
        self._vocabulary: dict[str, list[VocabularyItem]] = {}
        self._sentences: dict[str, list[SentenceExercise]] = {}

    async def async_load(self) -> None:
        """Load all language directories and optional content shards."""
        self._languages.clear()
        self._vocabulary.clear()
        self._sentences.clear()

        for directory in sorted(path for path in self._root.iterdir() if path.is_dir()):
            manifest_path = directory / "manifest.json"
            vocabulary_paths = sorted(directory.glob("vocabulary.*.json"))
            if not manifest_path.exists() or not vocabulary_paths:
                continue

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            code = manifest["code"]

            vocabulary: list[VocabularyItem] = []
            for path in vocabulary_paths:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, list):
                    raise ValueError(f"Language {code} file {path.name} must contain a list")
                vocabulary.extend(payload)
            self._validate_vocabulary(code, vocabulary)

            sentences: list[SentenceExercise] = []
            for path in sorted(directory.glob("sentences.*.json")):
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, list):
                    raise ValueError(f"Language {code} file {path.name} must contain a list")
                sentences.extend(payload)
            self._validate_sentences(code, sentences)

            language = dict(manifest)
            language["vocabulary_count"] = len(vocabulary)
            language["sentence_count"] = len(sentences)
            language["difficulty_levels"] = [1, *([2] if sentences else [])]
            self._languages[code] = language
            self._vocabulary[code] = vocabulary
            self._sentences[code] = sentences

    @staticmethod
    def _validate_vocabulary(code: str, vocabulary: list[dict[str, Any]]) -> None:
        ids: set[str] = set()
        for index, item in enumerate(vocabulary):
            for required in ("id", "target_text", "source_text", "category", "difficulty"):
                if item.get(required) in (None, ""):
                    raise ValueError(
                        f"Language {code} item {index} is missing required field {required}"
                    )
            if item["id"] in ids:
                raise ValueError(f"Language {code} contains duplicate id {item['id']}")
            if int(item["difficulty"]) != 1:
                raise ValueError(
                    f"Language {code} vocabulary item {item['id']} must use difficulty 1"
                )
            ids.add(item["id"])

    @staticmethod
    def _validate_sentences(code: str, sentences: list[dict[str, Any]]) -> None:
        ids: set[str] = set()
        required = (
            "id",
            "difficulty",
            "category",
            "prompt",
            "completed_text",
            "translation",
            "choices",
            "correct_answer",
        )
        for index, item in enumerate(sentences):
            for field in required:
                if item.get(field) in (None, "", []):
                    raise ValueError(
                        f"Language {code} sentence {index} is missing required field {field}"
                    )
            if item["id"] in ids:
                raise ValueError(f"Language {code} contains duplicate sentence id {item['id']}")
            if int(item["difficulty"]) != 2:
                raise ValueError(
                    f"Language {code} sentence {item['id']} must use difficulty 2"
                )
            if "___" not in item["prompt"]:
                raise ValueError(
                    f"Language {code} sentence {item['id']} must contain a ___ blank"
                )
            if item["correct_answer"] not in item["choices"]:
                raise ValueError(
                    f"Language {code} sentence {item['id']} does not include its answer"
                )
            ids.add(item["id"])

    def list_languages(self) -> list[dict[str, Any]]:
        return [self._languages[key] for key in sorted(self._languages)]

    def language(self, code: str) -> dict[str, Any]:
        if code not in self._languages:
            raise KeyError(f"Unknown language: {code}")
        return self._languages[code]

    def has_language(self, code: str) -> bool:
        return code in self._languages

    def vocabulary(self, code: str) -> list[VocabularyItem]:
        if code not in self._vocabulary:
            raise KeyError(f"Unknown language: {code}")
        return self._vocabulary[code]

    def sentences(self, code: str) -> list[SentenceExercise]:
        if code not in self._sentences:
            raise KeyError(f"Unknown language: {code}")
        return self._sentences[code]
