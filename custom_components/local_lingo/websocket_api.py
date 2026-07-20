"""Authenticated WebSocket API for Local Lingo cards."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, QUESTION_COUNT_OPTIONS
from .models import LocalLingoRuntime


def _runtime(hass: HomeAssistant) -> LocalLingoRuntime:
    entries = hass.config_entries.async_entries(DOMAIN)
    for entry in entries:
        if entry.state is ConfigEntryState.LOADED and entry.runtime_data is not None:
            return entry.runtime_data
    raise ValueError("Local Lingo is not loaded")


@callback
def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register commands once for the Home Assistant process."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("websocket_registered"):
        return
    websocket_api.async_register_command(hass, websocket_list_users)
    websocket_api.async_register_command(hass, websocket_upsert_user)
    websocket_api.async_register_command(hass, websocket_list_languages)
    websocket_api.async_register_command(hass, websocket_start_lesson)
    websocket_api.async_register_command(hass, websocket_get_active_session)
    websocket_api.async_register_command(hass, websocket_submit_answer)
    websocket_api.async_register_command(hass, websocket_progress_summary)
    websocket_api.async_register_command(hass, websocket_reset_progress)
    domain_data["websocket_registered"] = True


@websocket_api.websocket_command({vol.Required("type"): "local_lingo/list_users"})
@websocket_api.async_response
async def websocket_list_users(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.send_result(msg["id"], _runtime(hass).profiles.list_profiles())


@websocket_api.websocket_command(
    {
        vol.Required("type"): "local_lingo/upsert_user",
        vol.Required("display_name"): str,
        vol.Optional("user_id"): str,
        vol.Optional("default_language"): str,
        vol.Optional("daily_goal_points"): vol.All(int, vol.Range(min=1, max=5000)),
        vol.Optional("avatar"): vol.Any(str, None),
        vol.Optional("enabled", default=True): bool,
        vol.Optional("guest_mode", default=False): bool,
    }
)
@websocket_api.async_response
async def websocket_upsert_user(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    payload = {key: value for key, value in msg.items() if key not in {"id", "type"}}
    try:
        profile = await _runtime(hass).profiles.async_upsert_profile(**payload)
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_profile", str(err))
        return
    connection.send_result(msg["id"], profile)


@websocket_api.websocket_command({vol.Required("type"): "local_lingo/list_languages"})
@websocket_api.async_response
async def websocket_list_languages(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.send_result(msg["id"], _runtime(hass).languages.list_languages())


@websocket_api.websocket_command(
    {
        vol.Required("type"): "local_lingo/start_lesson",
        vol.Required("user_id"): str,
        vol.Required("language"): str,
        vol.Optional("question_count", default=10): vol.In(QUESTION_COUNT_OPTIONS),
        vol.Optional("category"): vol.Any(str, None),
    }
)
@websocket_api.async_response
async def websocket_start_lesson(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    runtime = _runtime(hass)
    if runtime.profiles.get_profile(msg["user_id"]) is None:
        connection.send_error(msg["id"], "unknown_user", "Unknown learner profile")
        return
    if not runtime.languages.has_language(msg["language"]):
        connection.send_error(msg["id"], "unknown_language", "Unknown language")
        return
    try:
        session = runtime.lesson_engine.start_lesson(
            user_id=msg["user_id"],
            language=msg["language"],
            question_count=msg["question_count"],
            category=msg.get("category"),
        )
    except ValueError as err:
        connection.send_error(msg["id"], "lesson_error", str(err))
        return
    await runtime.sessions.async_save(session)
    connection.send_result(msg["id"], runtime.lesson_engine.public_session(session))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "local_lingo/get_active_session",
        vol.Required("user_id"): str,
    }
)
@websocket_api.async_response
async def websocket_get_active_session(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    runtime = _runtime(hass)
    session = runtime.sessions.get_active_for_user(msg["user_id"])
    connection.send_result(
        msg["id"], runtime.lesson_engine.public_session(session) if session else None
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "local_lingo/submit_answer",
        vol.Required("session_id"): str,
        vol.Required("answer"): str,
    }
)
@websocket_api.async_response
async def websocket_submit_answer(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    runtime = _runtime(hass)
    session = runtime.sessions.get(msg["session_id"])
    if session is None:
        connection.send_error(msg["id"], "unknown_session", "Lesson session not found")
        return
    try:
        result = runtime.lesson_engine.check_answer(session, msg["answer"])
    except ValueError as err:
        connection.send_error(msg["id"], "lesson_error", str(err))
        return

    points = await runtime.progress.async_record_answer(
        user_id=session["user_id"],
        language=session["language"],
        word_id=result["word_id"],
        correct=result["correct"],
        first_try=result["first_try"],
    )
    session["points_earned"] += points
    lesson_bonus = 0
    if result["lesson_completed"]:
        lesson_bonus = await runtime.progress.async_complete_lesson(
            user_id=session["user_id"],
            language=session["language"],
            perfect=session["incorrect_count"] == 0,
        )
        session["points_earned"] += lesson_bonus
    await runtime.sessions.async_save(session)

    connection.send_result(
        msg["id"],
        {
            **result,
            "points_awarded": points,
            "lesson_bonus": lesson_bonus,
            "session": runtime.lesson_engine.public_session(session),
        },
    )


@websocket_api.websocket_command(
    {vol.Required("type"): "local_lingo/get_progress_summary"}
)
@websocket_api.async_response
async def websocket_progress_summary(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    runtime = _runtime(hass)
    users = {item["user_id"]: item for item in runtime.profiles.list_profiles()}
    summaries = []
    for user in users.values():
        for language in runtime.languages.list_languages():
            progress = runtime.progress.get(user["user_id"], language["code"])
            summaries.append(
                {
                    **{key: value for key, value in progress.items() if key != "word_progress"},
                    "display_name": user["display_name"],
                    "language_name": language["name"],
                    "daily_goal_points": user["daily_goal_points"],
                }
            )
    connection.send_result(msg["id"], summaries)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "local_lingo/reset_progress",
        vol.Required("user_id"): str,
        vol.Required("language"): str,
    }
)
@websocket_api.async_response
async def websocket_reset_progress(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    await _runtime(hass).progress.async_reset(
        user_id=msg["user_id"], language=msg["language"]
    )
    connection.send_result(msg["id"], {"success": True})
