"""Module for handling service calls."""

from __future__ import annotations

from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_DEVICE_ID,
    ATTR_ENTITY_ID,
    ATTR_LABEL_ID,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry, entity_registry

from custom_components.smarter.smarter_hub import SmarterHub

from .const import (
    DOMAIN,
    SERVICE_ATTR_COMMAND_DATA,
    SERVICE_ATTR_COMMAND_NAME,
    SERVICE_GET_COMMANDS,
    SERVICE_QUICK_BOIL,
    SERVICE_SEND_COMMAND,
)


async def async_setup_services(hass: HomeAssistant, hub: SmarterHub):
    async def handle_quick_boil(call: ServiceCall):
        call.data["command_name"] = "quick_boil"
        return handle_send_command(call)

    async def handle_send_command(call: ServiceCall):
        devices = get_device_ids(hass, call)
        command_name = call.data[SERVICE_ATTR_COMMAND_NAME]
        command_data = call.data[SERVICE_ATTR_COMMAND_DATA]
        results = []
        for device in devices:
            try:
                result = (
                    True,
                    device,
                    hub.send_command(device, command_name, command_data),
                )
            except Exception as ex:
                result = (False, device, ex)

            results.append(result)

        failures = [result[1:] for result in results if not result[0]]
        successes = [result[1:] for result in results if not result[1]]
        if len(failures) > 0:
            raise Exception([f"{failure[0]}: {failure[1]}" for failure in failures])

        return dict(successes)

    async def handle_get_commands(call: ServiceCall):
        pass

    hass.services.async_register(DOMAIN, SERVICE_QUICK_BOIL, handle_quick_boil)
    hass.services.async_register(DOMAIN, SERVICE_SEND_COMMAND, handle_send_command)
    hass.services.async_register(DOMAIN, SERVICE_GET_COMMANDS, handle_get_commands)


async def get_device_ids(hass: HomeAssistant, call: ServiceCall):
    dr = device_registry.async_get(hass)
    er = entity_registry.async_get(hass)

    device_ids: list[str] = call.get(ATTR_DEVICE_ID) or []
    area_ids: list[str] = call.get(ATTR_AREA_ID) or []
    entity_ids: list[str] = call.get(ATTR_ENTITY_ID) or []
    label_ids: list[str] = call.get(ATTR_LABEL_ID) or []

    entity_ids_merged = (
        entity.entity_id
        for device_id in device_ids
        for entity in entity_registry.async_entries_for_device(er, device_id)
    ) + entity_ids

    external_devices = list(
        set(
            hass.states(entity_id).extra_state_attributes.get("device_id")
            for entity_id in entity_ids_merged
        )
    )
    # devices: list[DeviceEntry] = [
    #     device
    #     for device_id in device_ids
    #     for device in dr.async_get(device_id)
    #     if device is not None
    # ]

    # devices_from_areas: list[DeviceEntry] = (
    #     device
    #     for area_id in area_ids
    #     for device in device_registry.async_entries_for_area(dr, area_id)
    # )

    # devices_from_entities: list[DeviceEntry] = (
    #     device
    #     for entity_id in entity_ids
    #     for entity in er.async_get(entity_id)
    #     for device in dr.async_get(entity.device_id)
    #     if entity is not None
    #     if device is not None
    # )

    # devices_from_labels: list[DeviceEntry] = (
    #     device
    #     for label_id in label_ids
    #     for device in device_registry.async_entries_for_label(dr, label_id)
    # )

    return external_devices
