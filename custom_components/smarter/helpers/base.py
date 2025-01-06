"""Base classes for entity configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.helpers.typing import VolSchemaType

# from smarter_client.managed_devices.base import BaseDevice


@dataclass(frozen=True, kw_only=True)
class ServiceMetadata:
    """Metadata for service registration."""

    handler_name: str
    service_name: str
    command_name: str | None = None
    command_data: dict[str, Any] | None = None
    schema: VolSchemaType
