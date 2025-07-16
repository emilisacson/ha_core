"""Tests for Anova Custom diagnostics support."""

from unittest.mock import MagicMock

import pytest

from homeassistant.components.anova_custom.const import DOMAIN
from homeassistant.components.anova_custom.diagnostics import (
    async_get_config_entry_diagnostics,
)
from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_diagnostics_redacts_jwt(hass: HomeAssistant) -> None:
    """Test diagnostics redacts JWT and returns correct device/coordinator data."""
    entry = MagicMock()
    entry.data = {"jwt": "secret-token", "username": "user"}
    entry.entry_id = "test_entry"
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "dev1": MagicMock(
                    anova_device=MagicMock(device_key="key1"), data={"foo": "bar"}
                ),
                "dev2": MagicMock(
                    anova_device=MagicMock(device_key="key2"), data={"baz": "qux"}
                ),
            }
        }
    }
    result = await async_get_config_entry_diagnostics(hass, entry)
    assert result["entry_data"]["jwt"] == "**REDACTED**"
    assert result["entry_data"]["username"] == "user"
    assert set(result["devices"]) == {"key1", "key2"}
    assert result["coordinator_data"] == {
        "dev1": {"foo": "bar"},
        "dev2": {"baz": "qux"},
    }
