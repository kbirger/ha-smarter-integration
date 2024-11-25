"""Support for Smarter number fields."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from .const import DOMAIN
from .entity import SmarterEntity
from .helpers.config import async_setup_smarter_platform


@dataclass(frozen=True, kw_only=True)
class SmarterNumberEntityDescription(NumberEntityDescription):
    """Class describing Ecobee number entities."""

    set_fn: Callable[[BaseDevice, int], Awaitable]


NUMBER_TYPES = [
    SmarterNumberEntityDescription(
        key="boil_temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        name="Boil Temperature",
        set_fn=lambda device, value: device.set_boil_temperature(value),
    ),
    SmarterNumberEntityDescription(
        key="keep_warm_time",
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        name="Keep Warm Time",
        native_min_value=0,
        native_max_value=40,
        native_step=1,
        set_fn=lambda device, value: device.set_keep_warm_time(value),
    ),
]


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
