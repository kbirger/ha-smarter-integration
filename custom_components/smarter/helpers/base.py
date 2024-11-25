"""Base classes for entity configuration."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain

from custom_components.smarter.entity import SmarterEntityDescription
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import VolSchemaType


@dataclass(frozen=True, kw_only=True)
class ServiceMetadata:
    """Metadata for service registration."""

    service_name: str
    handler_name: str
    schema: VolSchemaType


class DeviceConfig:
    """Represents configuration for a Smarter device."""

    @property
    @abstractmethod
    def device_entity(self) -> SmarterEntityDescription:
        """Get device-level entity associated with this device."""
        pass

    @property
    @abstractmethod
    def secondary_entities(self) -> Iterable[SmarterEntityDescription]:
        """Get all non-device-level entities associated with this device."""
        pass

    @property
    @abstractmethod
    def service_metadata(self) -> Iterable[ServiceMetadata]:
        """Get metadata for all services associated with this device."""
        pass

    @property
    def all_entities(self) -> Iterable[SmarterEntityDescription]:
        """Get all entities."""
        return chain([self.device_entity], self.secondary_entities)

    def get_secondary_entities(
        self, platform: Platform
    ) -> Iterable[SmarterEntityDescription]:
        """Get all non-device-level entities for platform."""
        return (
            entity for entity in self.secondary_entities if entity.platform == platform
        )

    def get_device_entities(self, platform: Platform) -> Iterable[EntityDescription]:
        """Get main device-level entities for target platform."""
        return [self.device_entity] if self.device_entity.platform == platform else []

    def get_service_metadata(self, platform: Platform) -> Iterable[ServiceMetadata]:
        """Get metadata for services on target platform."""
        return self.service_metadata if self.device_entity.platform == platform else []
