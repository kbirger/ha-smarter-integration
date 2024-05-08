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
