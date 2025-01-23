"""Support for Smarter number fields."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
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
        Platform.SELECT,
        SmarterSelect,
    )


class SmarterSelect(SmarterEntity, SelectEntity):
    """Representation of a Smarter number."""

    entity_description: SelectEntityDescription
    _attr_has_entity_name = True

    def __init__(self, device: BaseDevice, config: SmarterEntityConfig):
        """Create instance."""
        super().__init__(device, config, config.select_entity_description)

    @property
    def options(self):
        """Return the list of possible options."""
        return self.config.options

    @property
    def current_option(self):
        """Return the currently selected option."""
        return self.config.get_value(self.device)

    def select_option(self, option):
        """Set the option."""
        self.config.set_value(self.device, option)
