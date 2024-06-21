# """Module for handling service calls."""

# from __future__ import annotations

# import logging
# from collections.abc import Generator
# from itertools import chain

# import voluptuous as vol
# from homeassistant.const import (
#     ATTR_AREA_ID,
#     ATTR_DEVICE_ID,
#     ATTR_ENTITY_ID,
#     ATTR_LABEL_ID,
# )
# from homeassistant.core import (
#     HomeAssistant,
#     HomeAssistantError,
#     ServiceCall,
#     SupportsResponse,
# )
# from homeassistant.helpers import config_validation as cv
# from homeassistant.helpers import entity_registry
# from homeassistant.helpers.entity_registry import RegistryEntry

# from custom_components.smarter.smarter_hub import SmarterHub

# from .const import (
#     DOMAIN,
#     SERVICE_ATTR_COMMAND_DATA,
#     SERVICE_ATTR_COMMAND_NAME,
#     SERVICE_GET_COMMANDS,
#     SERVICE_QUICK_BOIL,
#     SERVICE_SEND_COMMAND,
# )

# _LOGGER = logging.getLogger(__name__)


# async def async_setup_services(hass: HomeAssistant, hub: SmarterHub):
#     _LOGGER.debug("Setting up services")

#     async def handle_quick_boil(call: ServiceCall):
#         _LOGGER.debug(f"Invoked handle_quick_boil with {call.data}")
#         devices = await _get_device_info(hass, call)

#         return await send_command(devices, "quick_boil", None)

#     async def handle_send_command(call: ServiceCall):
#         _LOGGER.debug(f"Invoked handle_send_command with {call.data}")
#         devices = await _get_device_info(hass, call)

#         command_name = call.data.get(SERVICE_ATTR_COMMAND_NAME)
#         command_data = call.data.get(SERVICE_ATTR_COMMAND_DATA)

#         return await send_command(devices, command_name, command_data)

#     async def send_command(devices, command_name, command_data):
#         _LOGGER.info("Sending command to devices")
#         results = []
#         for device_id, config_entry_id in devices:
#             _LOGGER.debug(
#                 f"Sending command to device. device_id={device_id};"
#                 f"command_name={command_name}; data={command_data}",
#             )
#             try:
#                 result = (
#                     True,
#                     device_id,
#                     await hub.send_command(
#                         device_id, config_entry_id, command_name, command_data
#                     ),
#                 )
#             except Exception as ex:
#                 result = (False, device_id, ex)

#             _LOGGER.debug("Success: %s, Result: %s", result[0], result[1])
#             results.append(result)

#         failures = [result[1:] for result in results if not result[0]]
#         successes = [result[1:] for result in results if not result[1]]
#         if len(failures) > 0:
#             raise HomeAssistantError(
#                 [f"{failure[0]}: {failure[1]}" for failure in failures]
#             )

#         return dict(successes)

#     async def handle_get_commands(call: ServiceCall):
#         """Get commands supported by all devices covered by ServiceCall selector."""
#         _LOGGER.debug(f"Invoked handle_get_commands with {call.data}")
#         devices = await _get_device_info(hass, call)

#         {
#             device_id: hub.get_commands(device_id, config_entry_id)
#             for (device_id, config_entry_id) in devices
#         }

#     hass.services.async_register(
#         DOMAIN,
#         SERVICE_QUICK_BOIL,
#         handle_quick_boil,
#         vol.Schema({}),
#         supports_response=SupportsResponse.ONLY,
#     )
#     hass.services.async_register(
#         DOMAIN,
#         SERVICE_SEND_COMMAND,
#         handle_send_command,
#         vol.Schema(
#             vol.All(
#                 {
#                     vol.Optional(ATTR_AREA_ID): vol.All(cv.ensure_list, [cv.string]),
#                     vol.Optional(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
#                     vol.Optional(ATTR_LABEL_ID): vol.All(cv.ensure_list, [cv.string]),
#                     vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
#                     vol.Required(SERVICE_ATTR_COMMAND_NAME): cv.string,
#                     vol.Optional(SERVICE_ATTR_COMMAND_DATA): cv.string,
#                 },
#                 cv.has_at_least_one_key(
#                     ATTR_DEVICE_ID, ATTR_ENTITY_ID, ATTR_AREA_ID, ATTR_LABEL_ID
#                 ),
#             )
#         ),
#         supports_response=SupportsResponse.ONLY,
#     )
#     hass.services.async_register(
#         DOMAIN,
#         SERVICE_GET_COMMANDS,
#         handle_get_commands,
#         vol.Schema({}),
#         supports_response=SupportsResponse.ONLY,
#     )


# async def _get_device_info(
#     hass: HomeAssistant, call: ServiceCall
# ) -> list[tuple[str, str]]:
#     # extract data from service call
#     data = call.data
#     device_ids: list[str] = data.get(ATTR_DEVICE_ID) or []
#     area_ids: list[str] = data.get(ATTR_AREA_ID) or []
#     entity_ids: list[str] = data.get(ATTR_ENTITY_ID) or []
#     label_ids: list[str] = data.get(ATTR_LABEL_ID) or []

#     return _get_devices(hass, device_ids, area_ids, entity_ids, label_ids)


# def _get_devices(
#     hass: HomeAssistant,
#     device_ids: list[str],
#     area_ids: list[str],
#     entity_ids: list[str],
#     label_ids: list[str],
# ) -> Generator[tuple[str, str]]:
#     er = entity_registry.async_get(hass)

#     entities_merged: set[tuple[str, str]] = set(
#         chain(
#             _get_devices_from_entity_ids(er, entity_ids),
#             _get_devices_from_device_ids(er, device_ids),
#             _get_devices_from_area_ids(er, area_ids),
#             _get_devices_from_label_ids(er, label_ids),
#         )
#     )

#     _LOGGER.debug(f"Extracted devices: {entities_merged}")
#     return entities_merged


# def _get_devices_from_label_ids(er, label_ids) -> Generator[tuple[str, str]]:
#     entities: Generator[tuple[str, str]] = (
#         (entity.device_id, entity.config_entry_id)
#         for label_id in label_ids
#         for entity in entity_registry.async_entries_for_label(er, label_id)
#         if entity.config_entry_id is not None
#     )

#     return entities


# def _get_devices_from_area_ids(er, area_ids) -> Generator[tuple[str, str]]:
#     entities: Generator[tuple[str, str]] = (
#         (entity.device_id, entity.config_entry_id)
#         for area_id in area_ids
#         for entity in entity_registry.async_entries_for_area(er, area_id)
#         if entity.config_entry_id is not None
#     )

#     return entities


# def _get_devices_from_device_ids(er, device_ids) -> Generator[tuple[str, str]]:
#     entities: Generator[tuple[str, str]] = (
#         (entity.device_id, entity.config_entry_id)
#         for device_id in device_ids
#         for entity in entity_registry.async_entries_for_device(er, device_id)
#         if entity.config_entry_id is not None
#     )

#     return entities


# def _get_devices_from_entity_ids(er, entity_ids) -> Generator[tuple[str, str]]:
#     entities_from_ids: Generator[RegistryEntry] = (
#         er.async_get(entity_id) for entity_id in entity_ids
#     )

#     for entity in entities_from_ids:
#         if entity is not None and entity.config_entry_id is not None:
#             yield (entity.device_id, entity.config_entry_id)
