"""Tests for Anova Custom config flow error handling and reauth."""

from unittest.mock import patch

import pytest

from homeassistant.components.anova_custom import config_flow
from homeassistant.components.anova_custom.config_flow import (
    CannotConnect,
    InvalidAuth,
    NoDevicesFound,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_no_devices_found_error(hass: HomeAssistant) -> None:
    """Test config flow handles NoDevicesFound error."""
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    with patch.object(config_flow.AnovaApi, "authenticate", side_effect=NoDevicesFound):
        result = await flow.async_step_user(
            {CONF_USERNAME: "user", CONF_PASSWORD: "pass"}
        )
        assert result["type"] == "abort"
        assert result["reason"] == "not_implemented"


@pytest.mark.asyncio
async def test_cannot_connect_error(hass: HomeAssistant) -> None:
    """Test config flow handles CannotConnect error."""
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    with patch.object(config_flow.AnovaApi, "authenticate", side_effect=CannotConnect):
        result = await flow.async_step_user(
            {CONF_USERNAME: "user", CONF_PASSWORD: "pass"}
        )
        assert result["type"] == "abort"
        assert result["reason"] == "not_implemented"


@pytest.mark.asyncio
async def test_invalid_auth_error(hass: HomeAssistant) -> None:
    """Test config flow handles InvalidAuth error."""
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    with patch.object(config_flow.AnovaApi, "authenticate", side_effect=InvalidAuth):
        result = await flow.async_step_user(
            {CONF_USERNAME: "user", CONF_PASSWORD: "pass"}
        )
        assert result["type"] == "abort"
        assert result["reason"] == "not_implemented"
