"""Module for configuring integration platforms."""

from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from itertools import chain
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HassJobType, HomeAssistant, SupportsResponse
from homeassistant.helpers import service
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from smarter_client.managed_devices.base import BaseDevice

from ..const import (
    DOMAIN,
    SmarterSensorEntityFeature,
)
from ..entity import SmarterEntity
from ..sensor import SmarterDeviceSensor
from .base import DeviceConfig
from .device_config import get_device_config


def async_setup_smarter_platform(
    hass: HomeAssistant,
    data: Any,
    async_add_entities: AddEntitiesCallback,
    platform: Platform,
    entity_constructor: type[SmarterEntity],
    device_entity_constructor: type[SmarterEntity] | None,
):
    """Set up target platform and services."""
    drivers: list[BaseDevice] = data.get("devices")

    configs_and_drivers = ((driver, get_device_config(driver)) for driver in drivers)

    all_entities = (
        entity_constructor(device, entity_config)
        for (device, config) in configs_and_drivers
        for entity_config in config.get_secondary_entities(platform)
    )

    constructor = device_entity_constructor or entity_constructor
    device_entities = (
        constructor(device, device_entity_config)
        for (device, config) in configs_and_drivers
        for device_entity_config in config.get_device_entities(platform)
    )

    # Create detailed sensor entities for each device
    async_add_entities(all_entities, True)

    # Create special "device" entities that represent the main device
    # These will be the entities targeted by the services
    configs = (config for (_, config) in configs_and_drivers)
    _register_services(hass, configs, device_entities)


def _register_services(
    hass: HomeAssistant,
    configs: Iterable[DeviceConfig],
    device_entities: Iterable[Entity],
):
    # metadata for services defined by specific entities
    device_metadata = _get_entity_specific_metadata(configs)

    # metadata for services that apply to all devices
    global_metadata = _get_global_metadata(device_entities)

    # register services for all devices that support them
    for metadata, entity_map in chain(device_metadata, global_metadata):
        hass.services.async_register(
            DOMAIN,
            metadata.service_name,
            partial(
                service.entity_service_call,
                hass,
                entity_map,
                metadata.handler_name,
                required_features=[SmarterSensorEntityFeature.SERVICE_AGENT],
            ),
            metadata.schema,
            SupportsResponse.OPTIONAL,
            job_type=HassJobType.Coroutinefunction,
        )


def async_unload_smarter_platform(hass: HomeAssistant, data: Any, platform: Platform):
    """Unload target platform and services."""
    drivers: list[BaseDevice] = data.get("devices")

    configs = (get_device_config(driver) for driver in drivers)

    device_services = (
        service_metadata.service_name
        for config in configs
        for service_metadata in config.get_service_metadata(platform)
    )

    global_services = (
        metadata.service_name for metadata in SmarterDeviceSensor.get_service_metadata()
    )

    service_names = chain(global_services, device_services)
    for service_name in service_names:
        hass.services.async_remove(DOMAIN, service_name)


def _get_global_metadata(device_entities):
    device_entities_map = {entity.entity_id: entity for entity in device_entities}
    return (
        (metadata, device_entities_map)
        for metadata in SmarterDeviceSensor.get_service_metadata()
    )


def _get_entity_specific_metadata(configs):
    return (
        (
            service_name,
            handler_name,
            schema,
            {config.device_entity.entity_id: config.device_entity},
        )
        for config in configs
        for (service_name, handler_name, schema) in config.service_metadata
    )
