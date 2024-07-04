"""Support for Smarter sensors."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SmarterEntity


@dataclass(frozen=True, kw_only=True)
class SmarterBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Represent the Smarter sensor entity description."""

    get_status_field: str
    state_on_values: tuple[str]


BINARY_SENSOR_TYPES = [
    SmarterBinarySensorEntityDescription(
        key="is_boiling",
        name="Boiling",
        get_status_field="state",
        state_on_values=("Boiling",),
    ),
    SmarterBinarySensorEntityDescription(
        key="is_cooling",
        name="Cooling",
        get_status_field="state",
        state_on_values=("Cooling",),
    ),
    SmarterBinarySensorEntityDescription(
        key="is_keep_warm",
        name="Keeping warm",
        get_status_field="state",
        state_on_values=("Keeping Warm",),
    ),
    SmarterBinarySensorEntityDescription(
        key="kettle_is_present",
        name="Kettle is Present",
        icon="mdi:kettle",
        get_status_field="kettle_is_present",
        state_on_values=(True,),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        SmarterBinarySensor(device, description)
        for device in data.get("devices")
        for description in BINARY_SENSOR_TYPES
    ]

    async_add_entities(entities, True)


class SmarterBinarySensor(SmarterEntity, BinarySensorEntity):
    """Representation of a Smarter binary sensor."""

    entity_description: SmarterBinarySensorEntityDescription

    _attr_has_entity_name = True

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        description = self.entity_description
        return (
            self.device.status.get(description.get_status_field)
            in description.state_on_values
        )
