"""Support for Smarter sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from custom_components.smarter.helpers.device_config import SmarterEntityConfig

# from .const import DOMAIN
from .entity import SmarterEntity
from .helpers.config import async_setup_smarter_platform


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = {**config_entry.data, **config_entry.options}

    # data = hass.data[DOMAIN][config_entry.entry_id]
    await async_setup_smarter_platform(
        hass,
        data,
        async_add_entities,
        Platform.BINARY_SENSOR,
        SmarterBinarySensor,
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Remove services and unload binary sensor entry."""
    # data = hass.data[DOMAIN][entry.entry_id]

    # async_unload_smarter_platform(hass, data, Platform.BINARY_SENSOR)


class SmarterBinarySensor(SmarterEntity, BinarySensorEntity):
    """Representation of a Smarter binary sensor."""

    entity_description: BinarySensorEntityDescription  # SmarterBinarySensorEntityDescription

    _attr_has_entity_name = True

    def __init__(self, device: BaseDevice, config: SmarterEntityConfig):
        """Create instance of the binary sensor."""
        super().__init__(device, config, config.sensor_entity_description)

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.config.get_value(self.device)
