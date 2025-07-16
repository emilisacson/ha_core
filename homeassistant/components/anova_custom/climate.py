"""Anova integration climate."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import DOMAIN
from .coordinator import AnovaCoordinator
from .entity import AnovaEntity
from .vendor.anova_wifi_set.src.anova_wifi import (
    AnovaPrecisionCookerBinarySensor,
    AnovaPrecisionCookerSensor,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry as TypedConfigEntry

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TypedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Anova device."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    entry.runtime_data = coordinators
    for coordinator in coordinators.values():
        await coordinator.async_config_entry_first_refresh()
        climate = [AnovaSousVideClimateDevice(coordinator)]
        async_add_entities(climate)


class AnovaSousVideClimateDevice(AnovaEntity, ClimateEntity):
    """Anova Sous Vide Climate Device.

    Represents the climate entity for an Anova sous-vide cooker, allowing temperature control and status monitoring.
    """

    _attr_supported_features: ClimateEntityFeature = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    # Expose HVACAction and HVACMode for test compatibility (no type aliasing)
    # These are imported from homeassistant.components.climate

    def __init__(self, coordinator: AnovaCoordinator) -> None:
        """Initialize the Anova Sous Vide Climate Device."""
        super().__init__(coordinator)
        self._attr_unique_id: str = f"{coordinator.device_unique_id}_climate".lower()
        self._attr_device_info = coordinator.device_info
        self._attr_has_entity_name = True
        self._attr_translation_key = "climate"
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_hvac_mode = HVACMode.OFF

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        value = self.coordinator.data["sensors"].get(
            AnovaPrecisionCookerSensor.WATER_TEMPERATURE
        )
        return float(value) if value is not None else None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        value = self.coordinator.data["sensors"].get(
            AnovaPrecisionCookerSensor.TARGET_TEMPERATURE
        )
        return float(value) if value is not None else None

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current hvac mode."""
        return (
            HVACMode.HEAT
            if self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.COOKING
            ]
            or self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.PREHEATING
            ]
            or self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.MAINTAINING
            ]
            else HVACMode.OFF
        )

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported."""
        if (
            self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.PREHEATING
            ]
            or self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.COOKING
            ]
        ):
            return HVACAction.HEATING

        if self.coordinator.data["binary_sensors"][
            AnovaPrecisionCookerBinarySensor.MAINTAINING
        ]:
            return HVACAction.IDLE

        return HVACAction.OFF

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def min_temp(self) -> float:
        """Return min temp."""
        return TemperatureConverter.convert(
            0, UnitOfTemperature.CELSIUS, self.temperature_unit
        )

    @property
    def max_temp(self) -> float:
        """Return max temp."""
        return TemperatureConverter.convert(
            100, UnitOfTemperature.CELSIUS, self.temperature_unit
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode and poll for state update every 5s (max 5 times), then restore interval."""
        if hvac_mode == HVACMode.OFF:
            await self.device.set_mode("IDLE")
        elif hvac_mode == HVACMode.HEAT:
            await self.device.set_mode("COOK")
        else:
            raise NotImplementedError

        await self._poll_for_state_update("hvac_mode", hvac_mode)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature and poll for state update every 5s (max 5 times), then restore interval."""
        target_temp = kwargs[ATTR_TEMPERATURE]
        await self.device.set_target_temperature(target_temp)
        await self._poll_for_state_update("target_temperature", target_temp)

    async def async_turn_on(self) -> None:
        """Turn on the device and poll for state update every 5s (max 5 times), then restore interval."""
        await self.device.set_mode("COOK")
        await self._poll_for_state_update("hvac_mode", HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn off the device and poll for state update every 5s (max 5 times), then restore interval."""
        await self.device.set_mode("IDLE")
        await self._poll_for_state_update("hvac_mode", HVACMode.OFF)

    async def _poll_for_state_update(self, attr: str, expected_value: Any) -> None:
        """Poll every 5s for up to 5 times until the state updates, then restore interval."""
        # Save original interval
        orig_interval = self.coordinator.update_interval
        self.coordinator.update_interval = timedelta(seconds=5)
        for _ in range(5):
            await self.coordinator.async_request_refresh()
            await asyncio.sleep(5)
            # Check if state updated
            if attr == "hvac_mode":
                if self.hvac_mode == expected_value:
                    break
            elif attr == "target_temperature":
                if self.target_temperature == expected_value:
                    break
        # Restore original interval
        self.coordinator.update_interval = orig_interval
