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
    ),
    SmarterSensorEntityDescription(
        key="boil_temperature",
        # native_unit_of_measurement=PERCENTAGE,
        name="Boil Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        runtime_key=None,
    ),
    SmarterSensorEntityDescription(
        key="target_temperature",
        name="Target Temperature",
        # native_unit_of_measurement=PERCENTAGE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        runtime_key=None,
    ),
    SmarterSensorEntityDescription(
        key="state",
        runtime_key=None,
        name="State",
    ),
    SmarterSensorEntityDescription(
        key="kettle_is_present",
        runtime_key=None,
        name="Kettle is Present",
    ),
    SmarterSensorEntityDescription(
        key="water_level",
        runtime_key=None,
        name="Water Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN]
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

    # async def async_update(self) -> None:
    #     """Get the latest state of the sensor."""
    #     await self.data.update()
    #     for sensor in self.data.ecobee.get_remote_sensors(self.index):
    #         if sensor["name"] != self.sensor_name:
    #             continue
    #         for item in sensor["capability"]:
    #             if item["type"] != self.entity_description.key:
    #                 continue
    #             if self.entity_description.runtime_key is None:
    #                 self._state = item["value"]
    #             else:
    #                 thermostat = self.data.ecobee.get_thermostat(self.index)
    #                 self._state = thermostat["runtime"][
    #                     self.entity_description.runtime_key
    #                 ]
    #             break
