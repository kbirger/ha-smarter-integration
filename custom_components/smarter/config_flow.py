"""Config flow for Smarter Kettle and Coffee integration."""

from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any

import voluptuous as vol

# from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

# from homeassistant.core import callback
from homeassistant.helpers.selector import SelectOptionDict, SelectSelector, SelectSelectorConfig, SelectSelectorMode
from smarter_client.domain.models import LoginSession, User
from smarter_client.managed_devices.base import BaseDevice

from custom_components.smarter.smarter_hub import CannotConnect, InvalidAuth, SmarterHub

from .const import CONF_REFRESH_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        # vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class SmarterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smarter Kettle and Coffee."""

    VERSION = 1

    __hub: SmarterHub | None = None
    __session: LoginSession | None = None
    __user: User | None = None
    __devices: list[BaseDevice]
    data: dict[str, str] = {}

    def __init_hub(self) -> SmarterHub:
        if not self.hass:
            raise RuntimeError("hass object is not available")

        self.__hub = self.__hub or SmarterHub(self.hass)

        return self.__hub

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        hub = self.__init_hub()

        if self.__hub is None:
            errors["base"] = "unknown"
        else:
            if user_input is not None:
                try:
                    username = user_input[CONF_USERNAME]
                    password = user_input[CONF_PASSWORD]
                    self.__session = await hub.sign_in(None, username, password)
                    user = await hub.get_user(self.__session)
                    self.__user = user
                    self.__devices = await hub.discover_devices(user)

                    self.data.update(
                        {
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                            CONF_REFRESH_TOKEN: self.__session.refresh_token,
                        }
                    )
                except CannotConnect as ex:
                    errors["base"] = "cannot_connect"
                    _LOGGER.exception(ex)
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception as ex:
                    _LOGGER.exception("Unexpected exception")
                    _LOGGER.exception(ex)
                    errors["base"] = "unknown"
                else:
                    return await self.async_step_choose_devices()

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

    async def async_step_choose_devices(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title=self.data[CONF_USERNAME], data={**self.data, **user_input})

        fields: OrderedDict[vol.Marker, Any] = OrderedDict()
        device_list = [
            SelectOptionDict(
                value=device.id,
                label=f"{device.friendly_name} ({device.model})",
            )
            for device in self.__devices
        ]
        fields[vol.Required("device_id")] = SelectSelector(
            SelectSelectorConfig(options=device_list, multiple=True, mode=SelectSelectorMode.LIST)
        )

        return self.async_show_form(step_id="choose_devices", errors=errors, data_schema=vol.Schema(fields))

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry):
    #     return OptionsFlowHandler(config_entry)


# class OptionsFlowHandler(config_entries.OptionsFlow):
#     def __init__(self, config_entry):
#         """Initialize options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(self, user_input=None):
#         pass

#     return await self.async_step_user(user_input)

# async def async_step_user(self, user_input=None):
#     """Manage the options."""
#     errors = {}
#     config = {**self.config_entry.data, **self.config_entry.options}

#     if user_input is not None:
#         config = {**config, **user_input}
#         device = await async_test_connection(config, self.hass)
#         if device:
#             return self.async_create_entry(title="", data=user_input)
#         errors["base"] = "connection"

#     schema = {
#         vol.Required(
#             CONF_LOCAL_KEY,
#             default=config.get(CONF_LOCAL_KEY, ""),
#         ): str,
#         vol.Required(CONF_HOST, default=config.get(CONF_HOST, "")): str,
#         vol.Required(
#             CONF_PROTOCOL_VERSION,
#             default=config.get(CONF_PROTOCOL_VERSION, "auto"),
#         ): vol.In(["auto"] + API_PROTOCOL_VERSIONS),
#         vol.Required(CONF_POLL_ONLY, default=config.get(CONF_POLL_ONLY, False)): bool,
#     }
#     cfg = await self.hass.async_add_executor_job(
#         get_config,
#         config[CONF_TYPE],
#     )
#     if cfg is None:
#         return self.async_abort(reason="not_supported")

#     return self.async_show_form(
#         step_id="user",
#         data_schema=vol.Schema(schema),
#         errors=errors,
#     )
