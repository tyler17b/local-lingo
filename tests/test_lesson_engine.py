"""Pure unit tests for the Local Lingo lesson engine."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import random
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "custom_components" / "local_lingo"

pkg = types.ModuleType("local_lingo_testpkg")
pkg.__path__ = [str(PACKAGE_ROOT)]
sys.modules[pkg.__name__] = pkg

for module_name in ("models", "language_registry", "lesson_engine"):
    spec = importlib.util.spec_from_file_location(
        f"{pkg.__name__}.{module_name}", PACKAGE_ROOT / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

LanguageRegistry = sys.modules[f"{pkg.__name__}.language_registry"].LanguageRegistry
LessonEngine = sys.modules[f"{pkg.__name__}.lesson_engine"].LessonEngine
normalize_answer = sys.modules[f"{pkg.__name__}.lesson_engine"].normalize_answer


def registry() -> LanguageRegistry:
    result = LanguageRegistry(PACKAGE_ROOT / "languages")
    asyncio.run(result.async_load())
    return result


def test_normalize_answer() -> None:
    assert normalize_answer("  DAS Haus! ") == "das haus"
    assert normalize_answer("¿Dónde está el baño?") == "dónde está el baño"


def test_language_packs_are_expanded() -> None:
    languages = registry()
    assert len(languages.vocabulary("de")) == 103
    assert len(languages.vocabulary("es")) == 103
    assert len(languages.sentences("de")) == 30
    assert len(languages.sentences("es")) == 30
    assert languages.language("de")["difficulty_levels"] == [1, 2]


def test_start_lesson_builds_requested_question_count() -> None:
    engine = LessonEngine(registry(), rng=random.Random(7))
    session = engine.start_lesson(
        user_id="learner_one",
        language="de",
        question_count=10,
        category="home",
        difficulty=1,
    )
    assert session["question_count"] == 10
    assert len(session["questions"]) == 10
    assert session["difficulty"] == 1
    public = engine.public_session(session)
    assert "correct_answer" not in public["question"]
    assert "answer_tts" not in public["question"]
    assert public["question"]["question_tts"]


def test_level_two_uses_reviewed_sentence_questions() -> None:
    engine = LessonEngine(registry(), rng=random.Random(4))
    session = engine.start_lesson(
        user_id="learner_two", language="es", question_count=5, difficulty=2
    )
    assert all(question["type"] == "cloze" for question in session["questions"])
    question = session["questions"][0]
    assert "___" in question["prompt"]
    assert question["completed_text"]
    assert question["answer_tts_language"] == "es-ES"


def test_mixed_lesson_contains_both_levels() -> None:
    engine = LessonEngine(registry(), rng=random.Random(8))
    session = engine.start_lesson(
        user_id="learner_three", language="de", question_count=10, difficulty="mixed"
    )
    types_found = {question["type"] for question in session["questions"]}
    assert "cloze" in types_found
    assert types_found - {"cloze"}


def test_natural_instruction_uses_language_name() -> None:
    class SourceRandom(random.Random):
        def choice(self, sequence):
            if "source_to_target" in sequence:
                return "source_to_target"
            return super().choice(sequence)

    engine = LessonEngine(registry(), rng=SourceRandom(3))
    session = engine.start_lesson(
        user_id="learner_four", language="es", question_count=1, difficulty=1
    )
    question = session["questions"][0]
    assert "Spanish" in question["instruction"]
    assert "ES translation" not in question["instruction"]
    assert question["choice_tts_language"] == "es-ES"


def test_article_question_explains_goal_and_supports_tts() -> None:
    class ArticleRandom(random.Random):
        def choice(self, sequence):
            if "article" in sequence:
                return "article"
            return super().choice(sequence)

    engine = LessonEngine(registry(), rng=ArticleRandom(3))
    session = engine.start_lesson(
        user_id="learner_five",
        language="de",
        question_count=1,
        category="home",
        difficulty=1,
    )
    question = session["questions"][0]
    assert question["type"] == "article"
    assert question["prompt"].startswith("___ ")
    assert question["instruction"] == "Which article completes this German noun?"
    assert set(question["choice_tts"]) == {"der", "die", "das"}


def test_answer_result_includes_spoken_completed_answer() -> None:
    engine = LessonEngine(registry(), rng=random.Random(2))
    session = engine.start_lesson(
        user_id="learner_six", language="es", question_count=1, difficulty=2
    )
    correct = session["questions"][0]["correct_answer"]
    result = engine.check_answer(session, correct)
    assert result["correct"] is True
    assert result["answer_tts"]
    assert result["answer_tts_language"] == "es-ES"
    assert result["completed_text"]
