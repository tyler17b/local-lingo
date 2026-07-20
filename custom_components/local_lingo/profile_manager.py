"""Learner profile management."""

from __future__ import annotations

from datetime import UTC, datetime
import re
from uuid import uuid4

from .const import DEFAULT_DAILY_GOAL, DEFAULT_LANGUAGE
from .models import UserProfile
from .storage import JsonStoreManager

_SAFE_ID = re.compile(r"[^a-z0-9_]+")


class ProfileManager:
    """Create, update, disable, and list learner profiles."""

    def __init__(self, store: JsonStoreManager) -> None:
        self._store = store

    async def async_initialize(self) -> None:
        """Load profiles without creating any default learners."""
        await self._store.async_load()
        if "profiles" not in self._store.data:
            self._store.data["profiles"] = {}
            await self._store.async_save()

    @staticmethod
    def _build_profile(
        *, user_id: str, display_name: str, guest_mode: bool = False
    ) -> UserProfile:
        return UserProfile(
            user_id=user_id,
            display_name=display_name,
            enabled=True,
            avatar=None,
            default_language=DEFAULT_LANGUAGE,
            daily_goal_points=DEFAULT_DAILY_GOAL,
            guest_mode=guest_mode,
            created_at=datetime.now(UTC).isoformat(),
        )

    def list_profiles(self, *, include_disabled: bool = False) -> list[UserProfile]:
        profiles: list[UserProfile] = list(
            self._store.data.get("profiles", {}).values()
        )
        if not include_disabled:
            profiles = [profile for profile in profiles if profile["enabled"]]
        return sorted(profiles, key=lambda item: item["display_name"].casefold())

    def get_profile(self, user_id: str) -> UserProfile | None:
        return self._store.data.get("profiles", {}).get(user_id)

    async def async_upsert_profile(
        self,
        *,
        display_name: str,
        user_id: str | None = None,
        default_language: str | None = None,
        daily_goal_points: int | None = None,
        avatar: str | None = None,
        enabled: bool = True,
        guest_mode: bool = False,
    ) -> UserProfile:
        """Create or edit a learner profile."""
        clean_name = display_name.strip()
        if not clean_name:
            raise ValueError("display_name must not be empty")

        profiles = self._store.data.setdefault("profiles", {})
        profile = profiles.get(user_id) if user_id else None
        if profile is None:
            base_id = _SAFE_ID.sub("_", clean_name.casefold()).strip("_") or "user"
            candidate = base_id
            if candidate in profiles:
                candidate = f"{base_id}_{uuid4().hex[:6]}"
            profile = self._build_profile(
                user_id=candidate,
                display_name=clean_name,
                guest_mode=guest_mode,
            )
            profiles[candidate] = profile

        profile["display_name"] = clean_name
        profile["enabled"] = enabled
        profile["guest_mode"] = guest_mode
        if default_language is not None:
            profile["default_language"] = default_language
        if daily_goal_points is not None:
            profile["daily_goal_points"] = max(1, daily_goal_points)
        if avatar is not None:
            profile["avatar"] = avatar

        await self._store.async_save()
        return profile

    async def async_disable_profile(self, user_id: str) -> bool:
        profile = self.get_profile(user_id)
        if profile is None:
            return False
        profile["enabled"] = False
        await self._store.async_save()
        return True
