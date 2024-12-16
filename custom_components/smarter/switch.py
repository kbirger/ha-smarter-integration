"""Support for Smarter sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
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

from custom_components.smarter.entity import SmarterEntity
from custom_components.smarter.helpers.config import async_setup_smarter_platform
from custom_components.smarter.helpers.device_config import SmarterEntityConfig

# def make_check_status(key: str, values: list[Any]) -> Callable[[BaseDevice], bool]:
#     """Return a function that checks the status of a device."""

#     def _check_status(device: BaseDevice) -> bool:
#         return device.device.status.get(key) in values if device.device.status is not None else False

#     return _check_status


# def set_boil(device: BaseDevice, value: bool):
#     """Invoke or cancel the boil command."""
#     device.send_command("start_boil" if value else "stop_boil", True)


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
        Platform.SWITCH,
        SmarterSwitch,
    )


#     data = hass.data[DOMAIN][config_entry.entry_id]
#     await async_setup_smarter_platform(
#         hass, data, async_add_entities, Platform.SWITCH, SmarterSwitch, None
#     )


class SmarterSwitch(SmarterEntity, SwitchEntity):
    """Representation of a Smarter binary sensor."""

    entity_description: SwitchEntityDescription

    _attr_has_entity_name = True

    def __init__(self, device: BaseDevice, config: SmarterEntityConfig):
        super().__init__(device, config, config.switch_entity_description)

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self.config.get_value(self.device)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self.config.set_value(self.device, True)
        self._attr_is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self.config.set_value(self.device, False)
        self._attr_is_on = False
