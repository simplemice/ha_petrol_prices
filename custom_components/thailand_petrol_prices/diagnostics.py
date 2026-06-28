"""Diagnostics support for Thailand Petrol Prices."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ThailandPetrolCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator: ThailandPetrolCoordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "options": dict(entry.options),
        "last_update_success": coordinator.last_update_success,
        "data": coordinator.data,
    }
