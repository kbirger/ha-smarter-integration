"""Defines module for integrating HomeAssistant with the Smarter API Client."""

import itertools

from smarter_client.domain.models import LoginSession, User
from smarter_client.domain.smarter_client import SmarterClient
from smarter_client.managed_devices import load_from_network
from smarter_client.managed_devices.base import BaseDevice


class SmarterHub:
    """Provide a facade around the Smarter API."""

    def __init__(self, hass):
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
                itertools.chain.from_iterable(
                    load_from_network(network, user.identifier)
                    for network in user.networks.values()
                )
            )

        return await self.hass.async_add_executor_job(_discover_devices)
