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