"""Tests for Anova Custom climate platform coverage."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.anova_custom.climate import AnovaSousVideClimateDevice
from homeassistant.components.anova_custom.coordinator import AnovaCoordinator
from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.precission_cooker import (
    AnovaPrecisionCooker,
)
from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_hvac_action_and_modes(hass: HomeAssistant) -> None:
    """Test all HVAC actions and mode changes."""
    coordinator = MagicMock(spec=AnovaCoordinator)
    coordinator.anova_device = MagicMock()
    coordinator.device_info = MagicMock()
    coordinator.device_unique_id = "test-device-unique-id"
    coordinator.data = {
        "binary_sensors": {
            "cooking": True,
            "preheating": False,
            "maintaining": False,
        },
        "sensors": {
            "water_temperature": 60.0,
            "target_temperature": 65.0,
        },
    }
    climate = AnovaSousVideClimateDevice(coordinator)

    # Test HVACAction.HEATING
    assert climate.hvac_action == HVACAction.HEATING
    # Test HVACAction.IDLE
    coordinator.data["binary_sensors"]["cooking"] = False
    coordinator.data["binary_sensors"]["maintaining"] = True
    assert climate.hvac_action == HVACAction.IDLE
    # Test HVACAction.OFF
    coordinator.data["binary_sensors"]["cooking"] = False
    coordinator.data["binary_sensors"]["maintaining"] = False
    assert climate.hvac_action == HVACAction.OFF


@pytest.mark.asyncio
async def test_set_hvac_mode_and_temperature(hass: HomeAssistant) -> None:
    """Test setting HVAC mode and temperature."""
    coordinator = AsyncMock(spec=AnovaCoordinator)
    coordinator.anova_device = AsyncMock(spec=AnovaPrecisionCooker)
    coordinator.device_info = MagicMock()
    coordinator.device_unique_id = "test-device-unique-id"

    climate = AnovaSousVideClimateDevice(coordinator)
    await climate.async_set_hvac_mode(HVACMode.OFF)
    coordinator.anova_device.set_mode.assert_awaited_with("IDLE")
    await climate.async_set_hvac_mode(HVACMode.HEAT)
    coordinator.anova_device.set_mode.assert_awaited_with("COOK")
    await climate.async_set_temperature(temperature=62.5)
    coordinator.anova_device.set_target_temperature.assert_awaited_with(62.5)
    await climate.async_turn_off()
    coordinator.anova_device.set_mode.assert_awaited_with("IDLE")
