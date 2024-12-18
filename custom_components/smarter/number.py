"""Support for Smarter number fields."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry

# from custom_components.smarter.entity import (
#     SmarterEntity,
#     SmarterSensorEntityDescription,
# )
# from custom_components.smarter.helpers.base import ServiceMetadata
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from custom_components.smarter.helpers.device_config import SmarterEntityConfig

# from custom_components.smarter.entity import SmarterEntity
# from custom_components.smarter.helpers.config import async_setup_smarter_platform
# from custom_components.smarter.helpers.device_config import SmarterEntityConfig
from .entity import SmarterEntity
from .helpers.config import async_setup_smarter_platform

# from custom_components.smarter.entity import (
#     SmarterEntity,
#     SmarterSensorEntityDescription,
# )
# from custom_components.smarter.helpers.base import ServiceMetadata


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = {**config_entry.data, **config_entry.options}
    await async_setup_smarter_platform(
        hass,
        data,
        async_add_entities,
        Platform.NUMBER,
        SmarterNumber,
    )


#     data = hass.data[DOMAIN][config_entry.entry_id]
#     await async_setup_smarter_platform(
#         hass, data, async_add_entities, Platform.BINARY_SENSOR, SmarterNumber, None
#     )


class SmarterNumber(SmarterEntity, NumberEntity):
    """Representation of a Smarter number."""

    entity_description: NumberEntityDescription
    _attr_has_entity_name = True

    def __init__(self, device: BaseDevice, config: SmarterEntityConfig):
        """Create instance."""
        super().__init__(device, config, config.number_entity_description)

    def set_native_value(self, value: float) -> None:
        """Set value."""
        self.config.set_value(self.device, int(value))

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        if (value := self.config.get_value(self.device)) is not None:
            return float(value)
        return None
