"""Persistent storage helpers for Local Lingo."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store


class JsonStoreManager:
    """Small versioned wrapper around Home Assistant Store."""

    def __init__(
        self,
        hass: HomeAssistant,
        version: int,
        key: str,
        default: dict[str, Any],
    ) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, version, key)
        self._default = default
        self.data: dict[str, Any] = deepcopy(default)

    async def async_load(self) -> dict[str, Any]:
        """Load data, applying defaults when no store exists."""
        loaded = await self._store.async_load()
        self.data = loaded if loaded is not None else deepcopy(self._default)
        return self.data

    async def async_save(self) -> None:
        """Persist current data."""
        await self._store.async_save(self.data)
