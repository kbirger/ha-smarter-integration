"""Defines module for integrating HomeAssistant with the Smarter API Client."""

import itertools
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from smarter_client.domain.models import LoginSession, User
from smarter_client.domain.smarter_client import SmarterClient
from smarter_client.managed_devices import load_from_network
from smarter_client.managed_devices.base import BaseDevice

from custom_components.smarter.const import DOMAIN


class DeviceNotFoundError(Exception):
    """Error raised when device is not found in API instance."""

    def __init__(self, external_device_id: str) -> None:
        """
        Instantiate DeviceNotFoundError.

        Params:
            external_device_id: ID of device
        """
        super().__init__(f"No device found with id {external_device_id}")


class SmarterHub:
    """Provide a facade around the Smarter API."""

    hass: HomeAssistant
    client: SmarterClient
    entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Create a new instance of the SmarterHub class."""
        self.hass = hass
        self.client = SmarterClient()
        self.entry = entry

    async def sign_in(self, username, password):
        """
        Asynchronously logs in to the Smarter API.

        Consumes provided credentials and returns a LoginSession or None, if sign-in
        fails.
        """
        return await self.hass.async_add_executor_job(
            self.client.sign_in, username, password
        )

    async def get_user(self, session: LoginSession):
        """Retrieve Smarter API user from current session."""
        user: User = User.from_id(self.client, session.local_id)
        await self.hass.async_add_executor_job(user.fetch)

        return user

    async def discover_devices(self, user: User) -> list[BaseDevice]:
        """Asynchronously discover devices."""

        def _discover_devices() -> list[BaseDevice]:
            """Get a list of device wrappers from the user's networks."""
            return list(
                itertools.chain.from_iterable(
                    load_from_network(network, user.identifier)
                    for network in user.networks.values()
                )
            )

        return await self.hass.async_add_executor_job(_discover_devices)

    @property
    def _domain_data(self) -> dict[str, Any]:
        return self.hass.data[DOMAIN]

    @property
    def _devices(self) -> list[BaseDevice]:
        return self._domain_data["devices"]

    def _get_device(self, external_device_id: str) -> BaseDevice:
        try:
            return next(
                device for device in self._devices if device.id == external_device_id
            )
        except StopIteration:
            raise DeviceNotFoundError(external_device_id)

    async def send_command(
        self, external_device_id: str, command_name: str, command_data: Any
    ):
        """
        Send a command to the specified device.

        Args:
            external_device_id: Device ID in Smarter API
            command_name: name of command (see `get_commands`)
            command_data: (optional) data for given command
        """
        try:
            device = self._get_device(external_device_id)
            device.send_command
            await self.hass.async_add_executor_job(
                device.send_command,
                command_name,
                command_data,
            )
        except KeyError:
            raise ValueError(f"Device does not support command '{command_data}'")
        except DeviceNotFoundError:
            return "not found"
