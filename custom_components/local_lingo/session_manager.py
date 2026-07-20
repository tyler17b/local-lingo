"""Persist resumable lesson sessions."""

from __future__ import annotations

from typing import Any

from .storage import JsonStoreManager


class SessionManager:
    """CRUD wrapper for active lesson sessions."""

    def __init__(self, store: JsonStoreManager) -> None:
        self._store = store

    async def async_initialize(self) -> None:
        await self._store.async_load()
        self._store.data.setdefault("sessions", {})

    def get(self, session_id: str) -> dict[str, Any] | None:
        return self._store.data.get("sessions", {}).get(session_id)

    def get_active_for_user(self, user_id: str) -> dict[str, Any] | None:
        sessions = self._store.data.get("sessions", {}).values()
        active = [
            session
            for session in sessions
            if session.get("user_id") == user_id and not session.get("completed")
        ]
        if not active:
            return None
        return max(active, key=lambda item: item.get("updated_at", ""))

    async def async_save(self, session: dict[str, Any]) -> None:
        self._store.data.setdefault("sessions", {})[session["session_id"]] = session
        await self._store.async_save()

    async def async_delete(self, session_id: str) -> None:
        self._store.data.setdefault("sessions", {}).pop(session_id, None)
        await self._store.async_save()
