"""The Smarter Kettle and Coffee integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant

from custom_components.smarter.services import async_setup_services
from custom_components.smarter.smarter_hub import SmarterHub

from .const import DOMAIN, LOGGER, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smarter Kettle and Coffee from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hub = SmarterHub(hass, entry)
    session = await hub.sign_in(entry.data["username"], entry.data["password"])
    user = await hub.get_user(session)

    devices = await hub.discover_devices(user)
    for device in devices:
        device.set_logger(LOGGER)

    hass.data[DOMAIN][entry.entry_id] = {"user": user, "devices": devices}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await async_setup_services(hass, hub)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
