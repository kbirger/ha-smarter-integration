"""Smarter base entity definitions."""

from __future__ import annotations

import logging
from typing import Protocol

from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from propcache import cached_property
from smarter_client.managed_devices.base import BaseDevice

from custom_components.smarter.helpers.device_config import SmarterEntityConfig

from .const import (
    DOMAIN,
    MANUFACTURER,
)

# from .const import LOGGER
_LOGGER = logging.getLogger(__name__)


class SmarterEntityConstructor(Protocol):
    """Type representing constructor of all Smarter entities."""

    def __init__(self, device: BaseDevice, config: SmarterEntityConfig):
        """Create instance of entity."""
        pass


class SmarterEntity:
    """Representation of a Smarter sensor."""

    # _attr_has_entity_name = True

    entity_description: EntityDescription

    device: BaseDevice

    config: SmarterEntityConfig

    def __init__(self, device: BaseDevice, config: SmarterEntityConfig, description: EntityDescription) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self.config = config
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
        _LOGGER.debug(
            "[%s] Received state update for %s",
            self.config.config_id,
            self.device.device.identifier,
        )
        _LOGGER.debug(state)
        self.schedule_update_ha_state()

    @cached_property
    def native_unit_of_measurement(self):
        """Return native unit of measurement."""
        if self.config.unit is not None:
            return self.config.unit
        if self.device_class == "temperature":
            return UnitOfTemperature.CELSIUS
        return None

    @property
    def should_poll(self):
        """Return whether device requires polling."""
        return False

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return self.config.unique_id(self.device.id)

    @property
    def name(self):
        """Return the name for the UI."""
        own_name = self.config.name
        if not own_name and not self.use_device_name:
            # super has the translation logic
            own_name = getattr(super(), "name")
        return own_name

    @property
    def use_device_name(self):
        """Return whether to use the device name for the entity name."""
        own_name = self.config.name or self.config.translation_key
        return not own_name

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
        if not self.config._is_primary:
            return {
                "device_id": self.device.id,
                "kettle_is_present": self.device.status.get("kettle_is_present"),
                "calibrated": self.device.status.get("calibrated"),
            }
        return {**self.device.status}


# @dataclass(frozen=True, kw_only=True)
# class SmarterEntityDescription(EntityDescription):
#     """Smarter entity base description."""

#     @property
#     @abstractmethod
#     def platform(self) -> Platform:
#         """Get the platform for this entity."""
#         raise NotImplementedError()


# @dataclass(frozen=True, kw_only=True)
# class SmarterSensorEntityDescription(SensorEntityDescription, SmarterEntityDescription):
#     """Represent the Smarter sensor entity description."""

#     platform = Platform.SENSOR


# @dataclass(frozen=True, kw_only=True)
# class SmarterBinarySensorEntityDescription(
#     SmarterEntityDescription, BinarySensorEntityDescription
# ):
#     """Represent the Smarter sensor entity description."""

#     platform = Platform.BINARY_SENSOR
#     get_status_field: str
#     state_on_values: tuple[str | bool]


# @dataclass(frozen=True, kw_only=True)
# class SmarterSwitchEntityDescription(SwitchEntityDescription):
#     """Represent the Smarter sensor entity description."""

#     get_fn: Callable[[BaseDevice], bool]
#     set_fn: Callable[[BaseDevice, Any], None]
