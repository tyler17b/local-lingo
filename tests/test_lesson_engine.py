"""Pure unit tests for the Local Lingo lesson engine."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import random
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "custom_components" / "local_lingo"

# Load the package modules without importing Home Assistant-dependent __init__.py.
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


def test_normalize_answer() -> None:
    assert normalize_answer("  DAS Haus! ") == "das haus"
    assert normalize_answer("¿Dónde está el baño?") == "dónde está el baño"


def test_start_lesson_builds_requested_question_count() -> None:
    registry = LanguageRegistry(PACKAGE_ROOT / "languages")
    import asyncio

    asyncio.run(registry.async_load())
    engine = LessonEngine(registry, rng=random.Random(7))
    session = engine.start_lesson(
        user_id="learner_one", language="de", question_count=10, category="home"
    )
    assert session["question_count"] == 10
    assert len(session["questions"]) == 10
    assert session["user_id"] == "learner_one"
    public = engine.public_session(session)
    assert "correct_answer" not in public["question"]


def test_correct_answer_advances_session() -> None:
    registry = LanguageRegistry(PACKAGE_ROOT / "languages")
    import asyncio

    asyncio.run(registry.async_load())
    engine = LessonEngine(registry, rng=random.Random(2))
    session = engine.start_lesson(
        user_id="learner_two", language="es", question_count=5
    )
    correct = session["questions"][0]["correct_answer"]
    result = engine.check_answer(session, correct)
    assert result["correct"] is True
    assert session["current_index"] == 1
