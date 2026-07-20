"""Local Lingo integration for Home Assistant."""

from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PROFILE_STORE_KEY,
    PROFILE_STORE_VERSION,
    PROGRESS_STORE_KEY,
    PROGRESS_STORE_VERSION,
    SESSION_STORE_KEY,
    SESSION_STORE_VERSION,
)
from .language_registry import LanguageRegistry
from .lesson_engine import LessonEngine
from .models import LocalLingoRuntime
from .profile_manager import ProfileManager
from .progress_manager import ProgressManager
from .session_manager import SessionManager
from .storage import JsonStoreManager
from .websocket_api import async_register_websocket_commands

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Local Lingo domain."""
    hass.data.setdefault(DOMAIN, {})
    async_register_websocket_commands(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry[LocalLingoRuntime]
) -> bool:
    """Set up Local Lingo from a config entry."""
    profiles_store = JsonStoreManager(
        hass, PROFILE_STORE_VERSION, PROFILE_STORE_KEY, {"profiles": {}}
    )
    progress_store = JsonStoreManager(
        hass, PROGRESS_STORE_VERSION, PROGRESS_STORE_KEY, {"progress": {}}
    )
    session_store = JsonStoreManager(
        hass, SESSION_STORE_VERSION, SESSION_STORE_KEY, {"sessions": {}}
    )

    profiles = ProfileManager(profiles_store)
    progress = ProgressManager(hass, progress_store)
    sessions = SessionManager(session_store)
    languages = LanguageRegistry(Path(__file__).parent / "languages")

    await profiles.async_initialize()
    await progress.async_initialize()
    await sessions.async_initialize()
    await languages.async_load()

    runtime = LocalLingoRuntime(
        profiles=profiles,
        progress=progress,
        languages=languages,
        sessions=sessions,
        lesson_engine=LessonEngine(languages),
    )
    entry.runtime_data = runtime

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry[LocalLingoRuntime]
) -> bool:
    """Unload the config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
