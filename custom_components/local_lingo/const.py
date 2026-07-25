"""Constants for Local Lingo."""

from __future__ import annotations

from typing import Final

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN: Final = "local_lingo"
NAME: Final = "Local Lingo"
PLATFORMS: Final = ["sensor"]

DEFAULT_DAILY_GOAL: Final = 100
DEFAULT_LANGUAGE: Final = "de"
DEFAULT_QUESTION_COUNT: Final = 10
QUESTION_COUNT_OPTIONS: Final = (5, 10, 15)
DIFFICULTY_OPTIONS: Final = (1, 2, "mixed")

PROFILE_STORE_VERSION: Final = 1
PROGRESS_STORE_VERSION: Final = 1
SESSION_STORE_VERSION: Final = 1

PROFILE_STORE_KEY: Final = "local_lingo_profiles"
PROGRESS_STORE_KEY: Final = "local_lingo_progress"
SESSION_STORE_KEY: Final = "local_lingo_sessions"

SIGNAL_PROGRESS_UPDATED: Final = f"{DOMAIN}_progress_updated"
EVENT_PROGRESS_UPDATED: Final = f"{DOMAIN}_progress_updated"

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: cv.empty_config_schema(DOMAIN)},
    extra=vol.ALLOW_EXTRA,
)
