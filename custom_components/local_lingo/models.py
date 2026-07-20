"""Data models for Local Lingo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class UserProfile(TypedDict):
    """Persisted learner profile."""

    user_id: str
    display_name: str
    enabled: bool
    avatar: str | None
    default_language: str
    daily_goal_points: int
    guest_mode: bool
    created_at: str


class VocabularyItem(TypedDict, total=False):
    """Language-pack vocabulary item."""

    id: str
    target_text: str
    source_text: str
    normalized_target: str
    part_of_speech: str
    category: str
    difficulty: int
    gender_or_article: str | None
    audio_hint: str | None
    distractors: list[str]
    examples: list[str]
    tags: list[str]


class UserLanguageProgress(TypedDict):
    """Persisted summary progress for one learner and one language."""

    user_id: str
    language: str
    points_total: int
    points_today: int
    points_date: str | None
    streak_current: int
    streak_best: int
    lessons_completed_total: int
    lessons_completed_today: int
    words_seen: int
    words_mastered: int
    correct_answers: int
    incorrect_answers: int
    last_activity_date: str | None
    word_progress: dict[str, dict[str, Any]]


@dataclass(slots=True)
class LocalLingoRuntime:
    """Runtime objects attached to the config entry."""

    profiles: Any
    progress: Any
    languages: Any
    sessions: Any
    lesson_engine: Any
