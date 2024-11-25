"""Support for Smarter sensors."""

from __future__ import annotations

from collections.abc import Iterable

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.smarter.entity import (
    SmarterEntity,
    SmarterSensorEntityDescription,
)
from custom_components.smarter.helpers.base import ServiceMetadata

from .const import (
    DOMAIN,
    SERVICE_GET_COMMANDS,
    SERVICE_SCHEMA_GET_COMMANDS,
    SERVICE_SCHEMA_SEND_COMMAND,
    SERVICE_SEND_COMMAND,
    SmarterSensorEntityFeature,
)
from .helpers.config import async_setup_smarter_platform


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_setup_smarter_platform(
        hass,
        data,
        async_add_entities,
        Platform.SENSOR,
        SmarterSensor,
        SmarterDeviceSensor,
    )


class SmarterSensor(SmarterEntity, SensorEntity):
    """Representation of a Smarter sensor."""

    _attr_has_entity_name = True

    entity_description: SmarterSensorEntityDescription

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device.status.get(self.entity_description.key)


class SmarterDeviceSensor(SmarterSensor):
    """
    Representation of a sensor that represents the physical device.

    This is the main sensor for a device, and is the target of all of the service calls
    for the integration.
    """

    _attr_supported_features = SmarterSensorEntityFeature.SERVICE_AGENT

    @classmethod
    def get_service_metadata(clazz) -> Iterable[ServiceMetadata]:
        """
        Get metadata for supported services.

        Returns:
            tuple[str,str,Schema]: (Service Name, Handler name, Schema)
        """
        return (
            ServiceMetadata(
                service_name=SERVICE_GET_COMMANDS,
                handler_name=clazz.async_get_commands.__name__,
                schema=SERVICE_SCHEMA_GET_COMMANDS,
            ),
            ServiceMetadata(
                service_name=SERVICE_SEND_COMMAND,
                handler_name=clazz.async_send_command.__name__,
                schema=SERVICE_SCHEMA_SEND_COMMAND,
            ),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device.status.get("state")

    @property
    def extra_state_attributes(self):
        """Return extra device attributes associated with entity."""
        return {"device_id": self.device.id, **self.device.status}

    async def async_send_command(
        self,
        command_name: str,
        command_data_text: str | None = None,
        command_data_number: float | None = None,
        command_data_boolean: bool | None = None,
    ):
        """Send command to device."""
        # The API requires a `value` to be set. The official client sends `True` if no
        # actual value is needed
        return await self.hass.async_add_executor_job(
            self.device.send_command,
            command_name,
            command_data_text or command_data_number or command_data_boolean or True,
        )

    async def async_get_commands(self):
        """
        Get list of commands supported by the underlying device.

        Returns a list of dictionaries. Each dictionary has `name` and `example` keys.
        The value under the `example` key is a dictionary providing information on the
        data that can be passed to the command.

        Returns:
            list[dict["name"|"example]]
        """
        return [
            {"name": command.name, "example": command.example}
            for command in self.device.device.commands.values()
        ]
