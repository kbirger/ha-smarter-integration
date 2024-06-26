"""Support for Smarter sensors."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SmarterEntity


@dataclass(frozen=True, kw_only=True)
class SmarterSensorEntityDescription(SensorEntityDescription):
    """Represent the Smarter sensor entity description."""

    runtime_key: str | None


SENSOR_TYPES: tuple[SmarterSensorEntityDescription, ...] = (
    SmarterSensorEntityDescription(
        key="water_temperature",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        runtime_key=None,
        icon="mdi:thermometer",
    ),
    SmarterSensorEntityDescription(
        key="boil_temperature",
        # native_unit_of_measurement=PERCENTAGE,
        name="Boil Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        runtime_key=None,
        icon="mdi:thermometer",
    ),
    SmarterSensorEntityDescription(
        key="target_temperature",
        name="Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        runtime_key=None,
        icon="mdi:thermometer",
    ),
    SmarterSensorEntityDescription(
        key="state",
        runtime_key=None,
        name="State",
        icon="mdi:kettle",
    ),
    SmarterSensorEntityDescription(
        key="kettle_is_present",
        runtime_key=None,
        name="Kettle is Present",
        icon="mdi:kettle",
    ),
    SmarterSensorEntityDescription(
        key="water_level",
        runtime_key=None,
        name="Water Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cup-water",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        SmarterSensor(device, description)
        for device in data.get("devices")
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities, True)


class SmarterSensor(SmarterEntity, SensorEntity):
    """Representation of a Smarter sensor."""

    _attr_has_entity_name = True

    entity_description: SmarterSensorEntityDescription

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device.status.get(self.entity_description.key)
