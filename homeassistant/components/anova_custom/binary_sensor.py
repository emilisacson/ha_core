"""The Anova integration Binary sensor."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry as TypedConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import AnovaCoordinator
from .entity import AnovaEntity
from .vendor.anova_wifi_set.src.anova_wifi import AnovaPrecisionCookerBinarySensor

PARALLEL_UPDATES = 1

SENSOR_DESCRIPTIONS: list[BinarySensorEntityDescription] = [
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.COOKING, name="Cooking"
    ),
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.PREHEATING, name="Preheating"
    ),
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.MAINTAINING, name="Maintaining"
    ),
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.DEVICE_SAFE, name="Device is safe"
    ),
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.WATER_LEAK, name="Water leak"
    ),
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.WATER_LEVEL_CRITICAL,
        name="Water level critical",
    ),
    BinarySensorEntityDescription(
        key=AnovaPrecisionCookerBinarySensor.WATER_TEMP_TOO_HIGH,
        name="Water temperature too high",
    ),
]


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
        sensors = [
            AnovaPrecissionCookerBinarySensor(coordinator, description)
            for description in SENSOR_DESCRIPTIONS
            if coordinator.data["binary_sensors"][description.key] is not None
        ]
        async_add_entities(sensors)


class AnovaPrecissionCookerBinarySensor(AnovaEntity, BinarySensorEntity):
    """Representation of an Anova Precision Cooker binary sensor."""

    def __init__(
        self, coordinator: AnovaCoordinator, description: BinarySensorEntityDescription
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description: BinarySensorEntityDescription = description
        self._sensor_update_key: str = description.key
        self._attr_unique_id: str = (
            f"{coordinator.device_unique_id}_{description.key}".lower()
        )
        self._attr_device_info = coordinator.device_info
        self._attr_has_entity_name = True
        self._attr_translation_key = description.key.lower()

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        value = self.coordinator.data["binary_sensors"].get(self._sensor_update_key)
        return bool(value)
