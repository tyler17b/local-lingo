"""Question generation and lesson state transitions."""

from __future__ import annotations

from datetime import UTC, datetime
import random
import re
import unicodedata
from uuid import uuid4

from .language_registry import LanguageRegistry
from .models import VocabularyItem

_NON_WORD = re.compile(r"[^\w\s]+", re.UNICODE)


def normalize_answer(value: str) -> str:
    """Normalize free-text answers without destroying accented characters."""
    normalized = unicodedata.normalize("NFKC", value).strip().casefold()
    normalized = _NON_WORD.sub("", normalized)
    return " ".join(normalized.split())


class LessonEngine:
    """Create and advance local lesson sessions."""

    def __init__(self, languages: LanguageRegistry, rng: random.Random | None = None) -> None:
        self._languages = languages
        self._rng = rng or random.SystemRandom()

    def start_lesson(
        self,
        *,
        user_id: str,
        language: str,
        question_count: int,
        category: str | None = None,
    ) -> dict:
        vocabulary = list(self._languages.vocabulary(language))
        if category:
            filtered = [item for item in vocabulary if item.get("category") == category]
            if filtered:
                vocabulary = filtered
        if not vocabulary:
            raise ValueError("No vocabulary is available for this lesson")

        chosen = self._rng.sample(vocabulary, k=min(question_count, len(vocabulary)))
        while len(chosen) < question_count:
            chosen.append(self._rng.choice(vocabulary))

        questions = [self._build_question(language, item, vocabulary) for item in chosen]
        now = datetime.now(UTC).isoformat()
        return {
            "session_id": uuid4().hex,
            "user_id": user_id,
            "language": language,
            "question_count": question_count,
            "category": category,
            "questions": questions,
            "current_index": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "points_earned": 0,
            "completed": False,
            "created_at": now,
            "updated_at": now,
        }

    def _build_question(
        self,
        language: str,
        item: VocabularyItem,
        vocabulary: list[VocabularyItem],
    ) -> dict:
        candidates = [value for value in vocabulary if value["id"] != item["id"]]
        question_types = ["target_to_source", "source_to_target"]
        if language == "de" and item.get("gender_or_article"):
            question_types.append("article")
        question_type = self._rng.choice(question_types)

        if question_type == "article":
            choices = ["der", "die", "das"]
            noun = item["target_text"].split(maxsplit=1)[-1]
            return {
                "question_id": uuid4().hex,
                "word_id": item["id"],
                "type": "article",
                "prompt": f"___ {noun}",
                "instruction": (
                    f"Choose the correct way to say “{item['source_text']}” in German"
                ),
                "choices": choices,
                "correct_answer": item["gender_or_article"],
                "attempts": 0,
                "answered": False,
            }

        if question_type == "target_to_source":
            correct = item["source_text"]
            pool = [value["source_text"] for value in candidates]
            prompt = item["target_text"]
            instruction = "Choose the English translation"
        else:
            correct = item["target_text"]
            pool = [value["target_text"] for value in candidates]
            prompt = item["source_text"]
            instruction = f"Choose the {language.upper()} translation"

        distractors = list(dict.fromkeys(item.get("distractors", [])))
        if question_type == "source_to_target":
            distractors = []
        pool = [value for value in pool if normalize_answer(value) != normalize_answer(correct)]
        self._rng.shuffle(pool)
        distractors.extend(pool[: max(0, 3 - len(distractors))])
        choices = list(dict.fromkeys([correct, *distractors]))[:4]
        self._rng.shuffle(choices)

        return {
            "question_id": uuid4().hex,
            "word_id": item["id"],
            "type": question_type,
            "prompt": prompt,
            "instruction": instruction,
            "choices": choices,
            "correct_answer": correct,
            "attempts": 0,
            "answered": False,
        }

    @staticmethod
    def public_session(session: dict) -> dict:
        """Return session state without exposing future correct answers."""
        result = {key: value for key, value in session.items() if key != "questions"}
        if session["completed"]:
            result["question"] = None
            return result

        question = session["questions"][session["current_index"]]
        result["question"] = {
            key: value for key, value in question.items() if key not in {"correct_answer"}
        }
        return result

    @staticmethod
    def check_answer(session: dict, answer: str) -> dict:
        if session["completed"]:
            raise ValueError("Lesson is already complete")
        question = session["questions"][session["current_index"]]
        question["attempts"] += 1
        correct = normalize_answer(answer) == normalize_answer(question["correct_answer"])
        first_try = question["attempts"] == 1
        question["answered"] = correct
        if correct:
            session["correct_count"] += 1
            session["current_index"] += 1
            if session["current_index"] >= len(session["questions"]):
                session["completed"] = True
        else:
            session["incorrect_count"] += 1
        session["updated_at"] = datetime.now(UTC).isoformat()
        return {
            "correct": correct,
            "first_try": first_try,
            "correct_answer": question["correct_answer"],
            "word_id": question["word_id"],
            "lesson_completed": session["completed"],
        }
