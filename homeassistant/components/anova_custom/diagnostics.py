"""Diagnostics support for Anova Custom integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry as TypedConfigEntry
if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry as TypedConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import DOMAIN

TO_REDACT = {"jwt"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: TypedConfigEntry
) -> Mapping[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "devices": [c.anova_device.device_key for c in data.values()],
        "coordinator_data": {k: c.data for k, c in data.items()},
    }
