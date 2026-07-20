"""Question generation and lesson state transitions."""

from __future__ import annotations

from datetime import UTC, datetime
import random
import re
import unicodedata
from uuid import uuid4

from .language_registry import LanguageRegistry
from .models import SentenceExercise, VocabularyItem

_NON_WORD = re.compile(r"[^\w\s]+", re.UNICODE)
_HIDDEN_QUESTION_FIELDS = {
    "correct_answer",
    "answer_tts",
    "answer_tts_language",
    "completed_text",
    "translation",
}


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
        difficulty: int | str = 1,
    ) -> dict:
        if difficulty not in (1, 2, "mixed"):
            raise ValueError("Difficulty must be 1, 2, or mixed")

        questions: list[dict] = []
        vocabulary = list(self._languages.vocabulary(language))
        sentences = list(self._languages.sentences(language))

        selected_vocabulary = self._filter_category(vocabulary, category)
        selected_sentences = self._filter_category(sentences, category)

        if difficulty == 1:
            questions = self._word_questions(
                language, selected_vocabulary, vocabulary, question_count
            )
        elif difficulty == 2:
            if not selected_sentences:
                raise ValueError("No sentence exercises are available for this lesson")
            questions = self._sentence_questions(language, selected_sentences, question_count)
        else:
            if not selected_sentences:
                raise ValueError("Mixed practice requires sentence exercises")
            word_count = (question_count + 1) // 2
            sentence_count = question_count - word_count
            questions.extend(
                self._word_questions(
                    language, selected_vocabulary, vocabulary, word_count
                )
            )
            questions.extend(
                self._sentence_questions(language, selected_sentences, sentence_count)
            )
            self._rng.shuffle(questions)

        now = datetime.now(UTC).isoformat()
        return {
            "session_id": uuid4().hex,
            "user_id": user_id,
            "language": language,
            "question_count": question_count,
            "category": category,
            "difficulty": difficulty,
            "questions": questions,
            "current_index": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "points_earned": 0,
            "completed": False,
            "created_at": now,
            "updated_at": now,
        }

    @staticmethod
    def _filter_category(items: list[dict], category: str | None) -> list[dict]:
        if not category:
            return items
        filtered = [item for item in items if item.get("category") == category]
        return filtered or items

    def _sample_with_replacement(self, items: list[dict], count: int) -> list[dict]:
        if not items:
            raise ValueError("No content is available for this lesson")
        chosen = self._rng.sample(items, k=min(count, len(items)))
        while len(chosen) < count:
            chosen.append(self._rng.choice(items))
        return chosen

    def _word_questions(
        self,
        language: str,
        selected: list[VocabularyItem],
        all_vocabulary: list[VocabularyItem],
        count: int,
    ) -> list[dict]:
        chosen = self._sample_with_replacement(selected, count)
        return [
            self._build_word_question(language, item, all_vocabulary) for item in chosen
        ]

    def _sentence_questions(
        self, language: str, sentences: list[SentenceExercise], count: int
    ) -> list[dict]:
        chosen = self._sample_with_replacement(sentences, count)
        return [self._build_sentence_question(language, item) for item in chosen]

    def _build_word_question(
        self,
        language: str,
        item: VocabularyItem,
        vocabulary: list[VocabularyItem],
    ) -> dict:
        meta = self._languages.language(language)
        language_name = meta["name"]
        target_tts = meta.get("tts_language", language)
        source_tts = meta.get("source_tts_language", "en-US")
        candidates = [value for value in vocabulary if value["id"] != item["id"]]
        question_types = ["target_to_source", "source_to_target"]
        article_choices = list(meta.get("article_choices", []))
        if item.get("gender_or_article") in article_choices:
            question_types.append("article")
        question_type = self._rng.choice(question_types)

        if question_type == "article":
            noun = item["target_text"].split(maxsplit=1)[-1]
            choices = article_choices
            return {
                "question_id": uuid4().hex,
                "word_id": item["id"],
                "type": "article",
                "prompt": f"___ {noun}",
                "instruction": f"Which article completes this {language_name} noun?",
                "choices": choices,
                "choice_tts": {choice: f"{choice} {noun}" for choice in choices},
                "choice_tts_language": target_tts,
                "question_tts": noun,
                "question_tts_language": target_tts,
                "correct_answer": item["gender_or_article"],
                "completed_text": item["target_text"],
                "translation": item["source_text"],
                "answer_tts": item.get("tts_text") or item["target_text"],
                "answer_tts_language": target_tts,
                "attempts": 0,
                "answered": False,
            }

        if question_type == "target_to_source":
            correct = item["source_text"]
            pool = [value["source_text"] for value in candidates]
            prompt = item["target_text"]
            instruction = f"What does “{prompt}” mean in English?"
            question_tts = item.get("tts_text") or prompt
            question_tts_language = target_tts
            choice_tts_language = source_tts
            completed_text = prompt
            translation = correct
        else:
            correct = item["target_text"]
            pool = [value["target_text"] for value in candidates]
            prompt = item["source_text"]
            instruction = f"How do you say “{prompt}” in {language_name}?"
            question_tts = instruction
            question_tts_language = source_tts
            choice_tts_language = target_tts
            completed_text = correct
            translation = prompt

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
            "choice_tts": {choice: choice for choice in choices},
            "choice_tts_language": choice_tts_language,
            "question_tts": question_tts,
            "question_tts_language": question_tts_language,
            "correct_answer": correct,
            "completed_text": completed_text,
            "translation": translation,
            "answer_tts": item.get("tts_text") or completed_text,
            "answer_tts_language": target_tts,
            "attempts": 0,
            "answered": False,
        }

    def _build_sentence_question(
        self, language: str, item: SentenceExercise
    ) -> dict:
        meta = self._languages.language(language)
        target_tts = meta.get("tts_language", language)
        choices = list(dict.fromkeys(item["choices"]))
        self._rng.shuffle(choices)
        prompt = item["prompt"]
        return {
            "question_id": uuid4().hex,
            "word_id": item.get("word_id") or item["id"],
            "type": "cloze",
            "prompt": prompt,
            "instruction": "Which word completes this sentence?",
            "choices": choices,
            "choice_tts": {
                choice: prompt.replace("___", choice) for choice in choices
            },
            "choice_tts_language": target_tts,
            "question_tts": prompt.replace("___", "…"),
            "question_tts_language": target_tts,
            "correct_answer": item["correct_answer"],
            "completed_text": item["completed_text"],
            "translation": item["translation"],
            "answer_tts": item["completed_text"],
            "answer_tts_language": target_tts,
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
            key: value
            for key, value in question.items()
            if key not in _HIDDEN_QUESTION_FIELDS
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
            "completed_text": question.get("completed_text", question["correct_answer"]),
            "translation": question.get("translation"),
            "answer_tts": question.get("answer_tts", question["correct_answer"]),
            "answer_tts_language": question.get("answer_tts_language"),
            "word_id": question["word_id"],
            "lesson_completed": session["completed"],
        }
