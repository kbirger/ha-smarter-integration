"""Constants for the Smarter Kettle and Coffee integration."""

import logging

from homeassistant.const import Platform

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
SERVICE_ATTR_COMMAND_DATA = "command_data"

SERVICES: list[str] = [
    SERVICE_QUICK_BOIL,
    SERVICE_SEND_COMMAND,
    SERVICE_QUICK_BOIL,
]
