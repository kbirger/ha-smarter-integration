"""The Smarter Kettle and Coffee integration."""
from __future__ import annotations

import itertools

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from smarter_client.domain.models import User
from smarter_client.domain.smarter_client import SmarterClient
from smarter_client.managed_devices import load_from_network
from smarter_client.managed_devices.base import BaseDevice

from .const import DOMAIN
from .const import LOGGER

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_discover_devices(hass: HomeAssistant, user: User) -> list[BaseDevice]:
    """Asynchronously discover devices."""
    return await hass.async_add_executor_job(discover_devices, user)


def discover_devices(user: User) -> list[BaseDevice]:
    """Get a list of device wrappers from the user's networks."""
    return list(
        itertools.chain.from_iterable(
            load_from_network(network, user.identifier)
            for network in user.networks.values()
        )
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smarter Kettle and Coffee from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    client = SmarterClient()
    session = await hass.async_add_executor_job(
        client.sign_in, entry.data["username"], entry.data["password"]
    )
    user: User = User.from_id(client, session.local_id)
    await hass.async_add_executor_job(user.fetch)
    devices = await async_discover_devices(hass, user)
    for device in devices:
        device.set_logger(LOGGER)

    hass.data[DOMAIN] = {"client": client, "user": user, "devices": devices}
    # TODO Create a wrapper
    # TODO Make package async

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
