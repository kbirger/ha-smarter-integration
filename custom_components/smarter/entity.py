"""Smarter base entity definitions."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import Platform
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity, EntityDescription
from smarter_client.managed_devices.base import BaseDevice

from .const import (
    DOMAIN,
    MANUFACTURER,
)

# from .const import LOGGER


class SmarterEntity(Entity):
    """Representation of a Smarter sensor."""

    _attr_has_entity_name = True

    entity_description: EntityDescription

    device: BaseDevice

    def __init__(
        self,
        device: BaseDevice,
        description: EntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self.device = device
        self._state = None
        # self._attr_supported_features = (
        #     SmarterSensorEntityFeature.SERVICE_AGENT
        #     if description.key == "device"
        #     else None
        # )

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass.

        To be extended by integrations.
        """
        self.device.subscribe_status(self._on_state_update)

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass.

        To be extended by integrations.
        """
        self.device.unsubscribe_status(self._on_state_update)

    @callback
    def _on_state_update(self, state):
        """Handle state update."""
        # LOGGER.debug(
        #     "[%s] Received state update for %s",
        #     self.unique_id,
        #     self.device.device.identifier,
        # )
        # LOGGER.debug(state)
        self.schedule_update_ha_state()

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return "-".join(
            (
                self.device.id,
                self.device.type,
                self.entity_description.key if self.entity_description else "device",
            )
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information for this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device.device.identifier)},
            manufacturer=MANUFACTURER,
            model=self.device.model,
            name=self.device.friendly_name,
            suggested_area="Kitchen",
            sw_version=self.device.firmware_version,
        )

    @property
    def available(self) -> bool:
        """Return true if device is available."""
        return self.device is not None

    @property
    def extra_state_attributes(self):
        """Return extra device attributes associated with entity."""
        return {
            "device_id": self.device.id,
            "kettle_is_present": self.device.status.get("kettle_is_present"),
            "calibrated": self.device.status.get("calibrated"),
        }


@dataclass(frozen=True, kw_only=True)
class SmarterEntityDescription(EntityDescription):
    """Smarter entity base description."""

    @property
    @abstractmethod
    def platform(self) -> Platform:
        """Get the platform for this entity."""
        raise NotImplementedError()


@dataclass(frozen=True, kw_only=True)
class SmarterSensorEntityDescription(SensorEntityDescription, SmarterEntityDescription):
    """Represent the Smarter sensor entity description."""

    platform = Platform.SENSOR


@dataclass(frozen=True, kw_only=True)
class SmarterBinarySensorEntityDescription(
    SmarterEntityDescription, BinarySensorEntityDescription
):
    """Represent the Smarter sensor entity description."""

    platform = Platform.BINARY_SENSOR
    get_status_field: str
    state_on_values: tuple[str | bool]


@dataclass(frozen=True, kw_only=True)
class SmarterSwitchEntityDescription(SwitchEntityDescription):
    """Represent the Smarter sensor entity description."""

    get_fn: Callable[[BaseDevice], bool]
    set_fn: Callable[[BaseDevice, Any], None]
