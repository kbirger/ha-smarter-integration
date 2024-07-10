"""Constants for the Smarter Kettle and Coffee integration."""

import logging
from enum import IntFlag

import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

DOMAIN = "smarter"

MANUFACTURER = "Smarter"

CONF_REFRESH_TOKEN = "refresh_token"

LOGGER = logging.getLogger(__package__)

# Platforms
PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

SERVICE_QUICK_BOIL = "quick_boil"
SERVICE_SEND_COMMAND = "send_command"
SERVICE_GET_COMMANDS = "get_commands"

SERVICE_ATTR_COMMAND_NAME = "command_name"
SERVICE_ATTR_COMMAND_DATA_TEXT = "command_data_text"
SERVICE_ATTR_COMMAND_DATA_NUMBER = "command_data_number"
SERVICE_ATTR_COMMAND_DATA_BOOLEAN = "command_data_boolean"

SERVICES: list[str] = [
    SERVICE_QUICK_BOIL,
    SERVICE_SEND_COMMAND,
    SERVICE_GET_COMMANDS,
]

SERVICE_SCHEMA_SEND_COMMAND = vol.Schema(
    vol.All(
        vol.Schema(
            {
                # The frontend stores data here. Don't use in core.
                vol.Remove("metadata"): dict,
                vol.Required(SERVICE_ATTR_COMMAND_NAME): cv.string,
                vol.Optional(SERVICE_ATTR_COMMAND_DATA_NUMBER): vol.Coerce(float),
                vol.Optional(SERVICE_ATTR_COMMAND_DATA_TEXT): cv.string,
                vol.Optional(SERVICE_ATTR_COMMAND_DATA_BOOLEAN): cv.boolean,
                **cv.ENTITY_SERVICE_FIELDS,
            },
            extra=vol.PREVENT_EXTRA,
        ),
        cv.has_at_least_one_key(*cv.ENTITY_SERVICE_FIELDS),
        cv.has_at_most_one_key(
            SERVICE_ATTR_COMMAND_DATA_BOOLEAN,
            SERVICE_ATTR_COMMAND_DATA_TEXT,
            SERVICE_ATTR_COMMAND_DATA_NUMBER,
        ),
    )
)

SERVICE_SCHEMA_QUICK_BOIL = cv.make_entity_service_schema({})
SERVICE_SCHEMA_GET_COMMANDS = cv.make_entity_service_schema({})


class SmarterSensorEntityFeature(IntFlag):
    """Defines entity features for sensors."""

    SERVICE_AGENT = 1
