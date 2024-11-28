"""Support for Smarter sensors."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from .const import DOMAIN
from .entity import SmarterEntity, SmarterSwitchEntityDescription
from .helpers.config import async_setup_smarter_platform


def make_check_status(key: str, values: list[Any]) -> Callable[[BaseDevice], bool]:
    """Return a function that checks the status of a device."""

    def _check_status(device: BaseDevice) -> bool:
        return (
            device.device.status.get(key) in values
            if device.device.status is not None
            else False
        )

    return _check_status


def set_boil(device: BaseDevice, value: bool):
    """Invoke or cancel the boil command."""
    device.send_command("start_boil" if value else "stop_boil", True)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_setup_smarter_platform(
        hass, data, async_add_entities, Platform.SWITCH, SmarterSwitch, None
    )


class SmarterSwitch(SmarterEntity, SwitchEntity):
    """Representation of a Smarter binary sensor."""

    entity_description: SmarterSwitchEntityDescription

    _attr_has_entity_name = True

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self.entity_description.get_fn(self.device)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self.entity_description.set_fn(self.device, True)
        self._attr_is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self.entity_description.set_fn(self.device, False)
        self._attr_is_on = False
