"""Support for Smarter sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from .const import DOMAIN
from .entity import SmarterEntity


@dataclass(frozen=True, kw_only=True)
class SmarterBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Represent the Smarter sensor entity description."""

    get_fn: Callable[[BaseDevice], bool]


def make_check_status(key: str, value: Any) -> bool:
    """Return a function that checks the status of a device."""

    def _check_status(device: BaseDevice) -> bool:
        return device.device.status.get(key) == value

    return _check_status


# TODO: Refactor this so that instead of setting up get_fn, the status key and on values
# are passed
BINARY_SENSOR_TYPES = [
    SmarterBinarySensorEntityDescription(
        key="is_boiling", name="Boiling", get_fn=make_check_status("state", "Boiling")
    ),
    SmarterBinarySensorEntityDescription(
        key="is_cooling", name="Cooling", get_fn=make_check_status("state", "Cooling")
    ),
    SmarterBinarySensorEntityDescription(
        key="is_keep_warm",
        name="Keeping warm",
        get_fn=make_check_status("state", "Keeping Warm"),
    ),
    SmarterBinarySensorEntityDescription(
        key="kettle_is_present",
        name="Kettle is Present",
        icon="mdi:kettle",
        get_fn=make_check_status("kettle_is_present", True),
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
        return self.entity_description.get_fn(self.device)
