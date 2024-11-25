"""Defines module for integrating HomeAssistant with the Smarter API Client."""

from collections.abc import Generator
from typing import Any

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

    def __init__(self, hass: HomeAssistant):
        """Create a new instance of the SmarterHub class."""
        self.hass = hass
        self.client = SmarterClient()

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
                device
                for network in user.networks.values()
                for device in load_from_network(network, user.identifier)
            )

        return await self.hass.async_add_executor_job(_discover_devices)

    def _domain_data(self, config_entry_id: str) -> dict[str, Any]:
        return self.hass.data[DOMAIN][config_entry_id]

    def _get_devices(self, config_entry_id: str) -> list[BaseDevice]:
        return self._domain_data(config_entry_id)["devices"]

    def _get_device(self, external_device_id: str, config_entry_id: str) -> BaseDevice:
        try:
            return next(
                device
                for device in self._get_devices(config_entry_id)
                if device.id == external_device_id
            )
        except StopIteration:
            raise DeviceNotFoundError(external_device_id)

    def get_commands(
        self,
        external_device_id: str,
        config_entry_id: str,
    ) -> Generator[tuple[str, dict]]:
        """
        Retrieve a list of commands supported by the specified device.

        Args:
            external_device_id: Device ID in Smarter API
            config_entry_id: HASS config entry ID that owns the device
        Returns:
            Generator of tuple[str,str] where the items are:
            [0] name of the command
            [1] example data, as provided by Smarter API
        """
        device = self._get_device(external_device_id, config_entry_id)
        for command in device.device.commands.values():
            yield (command.name, command.example)

    async def send_command(
        self,
        external_device_id: str,
        config_entry_id: str,
        command_name: str,
        command_data: Any,
    ):
        """
        Send a command to the specified device.

        Args:
            external_device_id: Device ID in Smarter API
            config_entry_id: HASS config entry ID that owns the device
            command_name: name of command (see `get_commands`)
            command_data: (optional) data for given command
        """
        try:
            device = self._get_device(external_device_id, config_entry_id)
            await self.hass.async_add_executor_job(
                device.send_command,
                command_name,
                command_data,
            )
        except KeyError:
            raise ValueError(f"Device does not support command '{command_name}'")
        except DeviceNotFoundError:
            return "not found"
