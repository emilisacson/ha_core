"""Support for Anova Coordinators."""

from __future__ import annotations

from asyncio import timeout
from datetime import timedelta
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import UNDEFINED, UndefinedType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .vendor.anova_wifi_set.src.anova_wifi import AnovaOffline, AnovaPrecisionCooker

_LOGGER = logging.getLogger(__name__)


class AnovaCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for Anova Precision Cooker device."""

    def __init__(
        self: AnovaCoordinator,
        hass: HomeAssistant,
        anova_device: AnovaPrecisionCooker,
        config_entry: config_entries.ConfigEntry[Any]
        | UndefinedType
        | None = UNDEFINED,
    ) -> None:
        """Initialize the Anova coordinator."""
        super().__init__(
            hass,
            name="Anova Precision Cooker",
            logger=_LOGGER,
            update_interval=timedelta(seconds=30),
            config_entry=config_entry,
        )
        self.device_unique_id: str = anova_device.device_key
        self.anova_device: AnovaPrecisionCooker = anova_device
        self.device_info: DeviceInfo | None = None

    @callback
    def async_setup(self, firmware_version: str) -> None:
        """Set up device info for registry."""
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device_unique_id)},
            name="Anova Precision Cooker",
            manufacturer="Anova",
            model="Precision Cooker",
            sw_version=firmware_version,
        )

    async def _async_update_data(self) -> dict:
        """Fetch latest data from the Anova device asynchronously."""
        try:
            async with timeout(5):
                return await self.anova_device.update()
        except AnovaOffline as err:
            raise UpdateFailed(f"Device offline: {err}") from err
