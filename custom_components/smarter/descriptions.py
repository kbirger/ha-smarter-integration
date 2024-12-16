# """Smarter base entity definitions."""

# from __future__ import annotations

# from abc import abstractmethod
# from collections.abc import Awaitable, Callable
# from dataclasses import dataclass
# from typing import Any

# from homeassistant.components.binary_sensor import (
#     BinarySensorEntityDescription,
# )
# from homeassistant.components.number import (
#     NumberEntityDescription,
# )
# from homeassistant.components.sensor import (
#     SensorEntityDescription,
# )
# from homeassistant.components.switch import (
#     SwitchEntityDescription,
# )
# from homeassistant.const import Platform
# from homeassistant.helpers.entity import EntityDescription
# from homeassistant.helpers.typing import VolSchemaType
# from smarter_client.managed_devices.base import BaseDevice


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
# class SmarterNumberEntityDescription(NumberEntityDescription):
#     """Class describing Ecobee number entities."""

#     set_fn: Callable[[BaseDevice, int], Awaitable]


# @dataclass(frozen=True, kw_only=True)
# class SmarterSwitchEntityDescription(SwitchEntityDescription):
#     """Represent the Smarter sensor entity description."""

#     get_fn: Callable[[BaseDevice], bool]
#     set_fn: Callable[[BaseDevice, Any], None]


# @dataclass(frozen=True, kw_only=True)
# class ServiceMetadata:
#     """Metadata for service registration."""

#     service_name: str
#     handler_name: str
#     schema: VolSchemaType
