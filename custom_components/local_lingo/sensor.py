"""Summary sensors for Local Lingo."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_PROGRESS_UPDATED
from .models import LocalLingoRuntime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[LocalLingoRuntime],
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime = entry.runtime_data
    entities: list[LocalLingoProgressSensor] = []
    for profile in runtime.profiles.list_profiles():
        for language in runtime.languages.list_languages():
            entities.append(
                LocalLingoProgressSensor(
                    entry.entry_id,
                    runtime,
                    profile["user_id"],
                    profile["display_name"],
                    language["code"],
                    language["name"],
                )
            )
    async_add_entities(entities)


class LocalLingoProgressSensor(SensorEntity):
    """One compact progress sensor per user-language pair."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:school"

    def __init__(
        self,
        entry_id: str,
        runtime: LocalLingoRuntime,
        user_id: str,
        display_name: str,
        language: str,
        language_name: str,
    ) -> None:
        self._runtime = runtime
        self._user_id = user_id
        self._language = language
        self._attr_unique_id = f"{entry_id}_{user_id}_{language}_progress"
        self._attr_name = f"{display_name} {language_name} progress"

    @property
    def native_value(self) -> int:
        return self._runtime.progress.get(self._user_id, self._language)["points_total"]

    @property
    def extra_state_attributes(self) -> dict:
        progress = self._runtime.progress.get(self._user_id, self._language)
        return {
            "language": self._language,
            "points_today": progress["points_today"],
            "streak_current": progress["streak_current"],
            "streak_best": progress["streak_best"],
            "lessons_completed_total": progress["lessons_completed_total"],
            "lessons_completed_today": progress["lessons_completed_today"],
            "words_seen": progress["words_seen"],
            "words_mastered": progress["words_mastered"],
            "correct_answers": progress["correct_answers"],
            "incorrect_answers": progress["incorrect_answers"],
        }

    async def async_added_to_hass(self) -> None:
        @callback
        def _handle_update() -> None:
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_PROGRESS_UPDATED, _handle_update)
        )
