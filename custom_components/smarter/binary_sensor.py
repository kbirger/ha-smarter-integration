"""Support for Smarter sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SmarterBinarySensorEntityDescription, SmarterEntity
from .helpers.config import async_setup_smarter_platform, async_unload_smarter_platform


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_setup_smarter_platform(
        hass,
        data,
        async_add_entities,
        Platform.BINARY_SENSOR,
        SmarterBinarySensor,
        None,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Remove services and unload binary sensor entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    async_unload_smarter_platform(hass, data, Platform.BINARY_SENSOR)


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
