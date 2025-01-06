"""Module for configuring integration platforms."""

from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from itertools import chain
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HassJobType, HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import service
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from ..const import (
    DOMAIN,
    SERVICE_GET_COMMANDS,
    SERVICE_SCHEMA_GET_COMMANDS,
    SERVICE_SCHEMA_SEND_COMMAND,
    SERVICE_SEND_COMMAND,
    SmarterSensorEntityFeature,
)
from ..entity import SmarterEntityConstructor

# from ..sensor import SmarterDeviceSensor
from .base import ServiceMetadata
from .device_config import SmarterDeviceConfig, get_device_config


async def async_setup_smarter_platform(
    hass: HomeAssistant,
    data: Any,
    async_add_entities: AddEntitiesCallback,
    platform: Platform,
    entity_constructor: SmarterEntityConstructor,
):
    """Set up target platform and services."""
    drivers: list[BaseDevice] = [hass.data[DOMAIN][device_id] for device_id in data.get("device_id")]

    def get_configs():
        return [(driver, get_device_config(driver)) for driver in drivers]

    configs_and_drivers = await hass.async_add_executor_job(get_configs)

    all_entities = [
        entity_constructor(device, entity_config)
        for (device, config) in configs_and_drivers
        for entity_config in config.get_all_entities(platform)
    ]

    primary_entities = [entity for entity in all_entities if entity.config.is_primary]

    # Create detailed sensor entities for each device
    async_add_entities(all_entities, True)

    # Create special "device" entities that represent the main device
    # These will be the entities targeted by the services
    configs = (config for (_, config) in configs_and_drivers)
    _register_services(hass, configs, primary_entities)


def _register_services(
    hass: HomeAssistant,
    configs: Iterable[SmarterDeviceConfig],
    device_entities: list[Entity],
):
    if not any(device_entities):
        return

    # metadata for services defined by specific entities
    device_metadata = _get_entity_specific_metadata(configs)

    # metadata for services that apply to all devices
    global_metadata = _get_global_metadata(device_entities)

    # register services for all devices that support them
    for metadata, entity_map in chain(device_metadata, global_metadata):
        print(metadata)
        print(entity_map)
        hass.services.async_register(
            DOMAIN,
            metadata.service_name,
            _get_service_call(hass, metadata, entity_map),
            metadata.schema,
            SupportsResponse.OPTIONAL,
            job_type=HassJobType.Coroutinefunction,
        )


def _get_service_call(hass: HomeAssistant, metadata: ServiceMetadata, entity_map: dict[str, Entity]):
    if metadata.command_name is not None:

        async def handler(service_call: ServiceCall):
            service_call.data["command_name"] = metadata.command_name
            service_call.data["command_data"] = metadata.command_data
            return await service.entity_service_call(
                hass,
                entity_map,
                "async_send_command",
                service_call,
                required_features=[SmarterSensorEntityFeature.SERVICE_AGENT],
            )

        return handler

    return partial(
        service.entity_service_call,
        hass,
        entity_map,
        metadata.handler_name,
        required_features=[SmarterSensorEntityFeature.SERVICE_AGENT],
    )


def async_unload_smarter_platform(hass: HomeAssistant, data: Any, platform: Platform):
    """Unload target platform and services."""
    drivers: list[BaseDevice] = data.get("devices")

    configs = (get_device_config(driver) for driver in drivers)

    (service_metadata.service_name for config in configs for service_metadata in config.get_service_metadata(platform))

    # global_services = (metadata.service_name for metadata in SmarterDeviceSensor.get_service_metadata())

    # service_names = chain(global_services, device_services)
    # for service_name in service_names:
    #     hass.services.async_remove(DOMAIN, service_name)


def _get_global_metadata(device_entities) -> Iterable[tuple[ServiceMetadata, dict[str, Entity]]]:
    all_entities_map = {entity.entity_id: entity for entity in device_entities}

    return (
        (metadata, all_entities_map)
        for metadata in (
            ServiceMetadata(
                service_name=SERVICE_GET_COMMANDS,
                handler_name="async_get_commands",
                schema=SERVICE_SCHEMA_GET_COMMANDS,
            ),
            ServiceMetadata(
                service_name=SERVICE_SEND_COMMAND,
                handler_name="async_send_command",
                schema=SERVICE_SCHEMA_SEND_COMMAND,
            ),
        )
    )


# {entity.entity_id: entity for entity in device_entities}
# return ((metadata, device_entities_map) for metadata in SmarterDeviceSensor.get_service_metadata())


def _get_entity_specific_metadata(
    configs: Iterable[SmarterDeviceConfig],
) -> Iterable[tuple[ServiceMetadata, dict[str, Entity]]]:
    return (
        (
            metadata,
            {config.primary_entity.config_id: config.primary_entity},
        )
        for config in configs
        for metadata in config.services
    )
