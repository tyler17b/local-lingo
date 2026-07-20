"""Progress and scoring persistence."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import EVENT_PROGRESS_UPDATED, SIGNAL_PROGRESS_UPDATED
from .models import UserLanguageProgress
from .storage import JsonStoreManager


class ProgressManager:
    """Track points, streaks, lesson totals, and word history."""

    def __init__(self, hass: HomeAssistant, store: JsonStoreManager) -> None:
        self._hass = hass
        self._store = store

    async def async_initialize(self) -> None:
        await self._store.async_load()
        self._store.data.setdefault("progress", {})

    @staticmethod
    def _key(user_id: str, language: str) -> str:
        return f"{user_id}:{language}"

    @staticmethod
    def _new_progress(user_id: str, language: str) -> UserLanguageProgress:
        return UserLanguageProgress(
            user_id=user_id,
            language=language,
            points_total=0,
            points_today=0,
            points_date=None,
            streak_current=0,
            streak_best=0,
            lessons_completed_total=0,
            lessons_completed_today=0,
            words_seen=0,
            words_mastered=0,
            correct_answers=0,
            incorrect_answers=0,
            last_activity_date=None,
            word_progress={},
        )

    def get(self, user_id: str, language: str) -> UserLanguageProgress:
        progress = self._store.data.setdefault("progress", {})
        key = self._key(user_id, language)
        if key not in progress:
            progress[key] = self._new_progress(user_id, language)
        item: UserLanguageProgress = progress[key]
        self._roll_daily_values(item)
        return item

    @staticmethod
    def _roll_daily_values(item: UserLanguageProgress) -> None:
        today = date.today().isoformat()
        if item["points_date"] != today:
            item["points_today"] = 0
            item["lessons_completed_today"] = 0
            item["points_date"] = today

    def _notify_updated(self, *, user_id: str, language: str) -> None:
        async_dispatcher_send(self._hass, SIGNAL_PROGRESS_UPDATED)
        self._hass.bus.async_fire(
            EVENT_PROGRESS_UPDATED,
            {"user_id": user_id, "language": language},
        )

    async def async_record_answer(
        self,
        *,
        user_id: str,
        language: str,
        word_id: str,
        correct: bool,
        first_try: bool,
    ) -> int:
        item = self.get(user_id, language)
        word = item["word_progress"].setdefault(
            word_id,
            {
                "times_seen": 0,
                "times_correct_first_try": 0,
                "times_correct_after_retry": 0,
                "times_incorrect": 0,
                "mastery_score": 0.0,
            },
        )
        first_seen = word["times_seen"] == 0
        word["times_seen"] += 1
        if first_seen:
            item["words_seen"] += 1

        if correct:
            points = 10 if first_try else 6
            item["correct_answers"] += 1
            key = "times_correct_first_try" if first_try else "times_correct_after_retry"
            word[key] += 1
            word["mastery_score"] = min(
                1.0,
                float(word["mastery_score"]) + (0.18 if first_try else 0.1),
            )
        else:
            points = 0
            item["incorrect_answers"] += 1
            word["times_incorrect"] += 1
            word["mastery_score"] = max(
                0.0, float(word["mastery_score"]) - 0.12
            )

        item["points_total"] += points
        item["points_today"] += points
        item["words_mastered"] = sum(
            1
            for value in item["word_progress"].values()
            if float(value.get("mastery_score", 0)) >= 0.8
        )
        await self._store.async_save()
        self._notify_updated(user_id=user_id, language=language)
        return points

    async def async_complete_lesson(
        self, *, user_id: str, language: str, perfect: bool
    ) -> int:
        item = self.get(user_id, language)
        today = date.today()
        last = (
            date.fromisoformat(item["last_activity_date"])
            if item["last_activity_date"]
            else None
        )

        if last == today:
            pass
        elif last == today - timedelta(days=1):
            item["streak_current"] += 1
        else:
            item["streak_current"] = 1

        item["streak_best"] = max(item["streak_best"], item["streak_current"])
        item["last_activity_date"] = today.isoformat()
        item["lessons_completed_total"] += 1
        item["lessons_completed_today"] += 1

        bonus = 20 + (10 if perfect else 0)
        item["points_total"] += bonus
        item["points_today"] += bonus
        await self._store.async_save()
        self._notify_updated(user_id=user_id, language=language)
        return bonus

    async def async_reset(self, *, user_id: str, language: str) -> None:
        progress = self._store.data.setdefault("progress", {})
        progress[self._key(user_id, language)] = self._new_progress(user_id, language)
        await self._store.async_save()
        self._notify_updated(user_id=user_id, language=language)

    def summary(self) -> list[dict[str, Any]]:
        return list(self._store.data.setdefault("progress", {}).values())
