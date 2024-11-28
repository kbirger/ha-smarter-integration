"""Support for Smarter number fields."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SmarterEntity
from .helpers.base import SmarterNumberEntityDescription
from .helpers.config import async_setup_smarter_platform


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_setup_smarter_platform(
        hass, data, async_add_entities, Platform.BINARY_SENSOR, SmarterNumber, None
    )


class SmarterNumber(SmarterEntity, NumberEntity):
    """Representation of a Smarter number."""

    entity_description: SmarterNumberEntityDescription
    _attr_has_entity_name = True

    def set_native_value(self, value: float) -> None:
        """Set value."""
        self.entity_description.set_fn(self.device, int(value))

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return float(self.device.status.get(self.entity_description.key))
