"""Frontend resource hosting for Local Lingo."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

FRONTEND_URL = "/local_lingo"
FRONTEND_DIRECTORY = Path(__file__).parent / "frontend"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Expose the bundled Local Lingo cards through Home Assistant."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("frontend_registered"):
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(FRONTEND_DIRECTORY), False)]
    )
    domain_data["frontend_registered"] = True
