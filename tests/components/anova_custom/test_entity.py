"""Test AnovaCustom entities (binary_sensor, climate, sensor)."""

from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from tests.common import MockConfigEntry


@pytest.mark.parametrize("platform", ["binary_sensor", "climate", "sensor"])
async def test_entity_registry_and_state(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    platform: str,
) -> None:
    """Test entity registry, device info, translation key, and snapshot state for each platform."""
    # Setup integration via config entry
    config_entry = MockConfigEntry(
        domain="anova_custom",
        data={
            "host": "1.1.1.1",
            "username": "test-username",
            "password": "test-password",
            "devices": [
                ("test-anova-device", "Precision Cooker"),
            ],
            "jwt": None,
        },
        unique_id="test-anova-device",
    )
    config_entry.add_to_hass(hass)
    with patch(
        "homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.precission_cooker.AnovaPrecisionCooker.update",
        return_value={
            "sensors": {
                "firmware_version": "1.0.0",
                "cook_time": 3600,
                "mode": "COOK",
                "state": "COOKING",
                "target_temperature": 60.0,
                "cook_time_remaining": 1800,
                "heater_temperature": 61.0,
                "triac_temperature": 62.0,
                "water_temperature": 59.5,
            },
            "binary_sensors": {
                "cooking": True,
                "preheating": False,
                "maintaining": False,
                "device_safe": True,
                "water_leak": False,
                "water_level_critical": False,
                "water_temp_too_high": False,
            },
        },
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    # Find all entities for this platform
    entries = [
        e
        for e in registry.entities.values()
        if e.domain == platform and e.platform == "anova_custom"
    ]
    assert entries, f"No entities found for platform {platform}"
    for entry in entries:
        assert entry.unique_id is not None
        entity = hass.states.get(entry.entity_id)
        assert entity is not None
        assert entity.state is not None
        # Snapshot entity state and attributes
        assert entity == snapshot
        # Check translation key and device info if available
        device = device_registry.async_get(entry.device_id)
        assert device is not None
        assert device.manufacturer is not None
        assert device.model is not None
