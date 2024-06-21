"""Support for Smarter sensors."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HassJobType, HomeAssistant, SupportsResponse
from homeassistant.helpers import service
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SERVICE_GET_COMMANDS,
    SERVICE_QUICK_BOIL,
    SERVICE_SCHEMA_GET_COMMANDS,
    SERVICE_SCHEMA_QUICK_BOIL,
    SERVICE_SCHEMA_SEND_COMMAND,
    SERVICE_SEND_COMMAND,
    SmarterSensorEntityFeature,
)
from .entity import SmarterEntity


@dataclass(frozen=True, kw_only=True)
class SmarterSensorEntityDescription(SensorEntityDescription):
    """Represent the Smarter sensor entity description."""


SENSOR_TYPES: tuple[SmarterSensorEntityDescription, ...] = (
    SmarterSensorEntityDescription(
        key="water_temperature",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SmarterSensorEntityDescription(
        key="boil_temperature",
        # native_unit_of_measurement=PERCENTAGE,
        name="Boil Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SmarterSensorEntityDescription(
        key="target_temperature",
        name="Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SmarterSensorEntityDescription(
        key="state",
        name="State",
        icon="mdi:kettle",
    ),
    SmarterSensorEntityDescription(
        key="water_level",
        name="Water Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cup-water",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices = data.get("devices")

    # Create detailed sensor entities for each device
    entities = [
        SmarterSensor(device, description)
        for device in devices
        for description in SENSOR_TYPES
    ]

    # Create special "device" entities that represent the main device
    # These will be the entities targeted by the services
    device_entities = [
        SmarterDeviceSensor(
            device,
            SmarterSensorEntityDescription(
                key="device", name=None, has_entity_name=True, icon="mdi:kettle"
            ),
        )
        for device in data.get("devices")
    ]

    async_add_entities(entities + device_entities, True)

    device_entities_map = {entity.entity_id: entity for entity in device_entities}

    _register_services(hass, device_entities_map)


def _register_services(hass, device_entities_map):
    for (
        service_name,
        handler_name,
        schema,
    ) in SmarterDeviceSensor.get_service_metadata():
        hass.services.async_register(
            DOMAIN,
            service_name,
            partial(
                service.entity_service_call,
                hass,
                device_entities_map,
                handler_name,
                required_features=[SmarterSensorEntityFeature.SERVICE_AGENT],
            ),
            schema,
            SupportsResponse.ONLY,
            job_type=HassJobType.Coroutinefunction,
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    for (service_name,) in SmarterDeviceSensor.get_service_metadata():
        hass.services.async_remove(DOMAIN, service_name)


class SmarterSensor(SmarterEntity, SensorEntity):
    """Representation of a Smarter sensor."""

    _attr_has_entity_name = False

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
    def get_service_metadata(clazz):
        """
        Get metadata for supported services.

        Returns:
            tuple[str,str,Schema]: (Service Name, Handler name, Schema)
        """
        return (
            (
                SERVICE_GET_COMMANDS,
                clazz.async_get_commands.__name__,
                SERVICE_SCHEMA_GET_COMMANDS,
            ),
            (
                SERVICE_QUICK_BOIL,
                clazz.async_quick_boil.__name__,
                SERVICE_SCHEMA_QUICK_BOIL,
            ),
            (
                SERVICE_SEND_COMMAND,
                clazz.async_send_command.__name__,
                SERVICE_SCHEMA_SEND_COMMAND,
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

    async def async_quick_boil(self):
        """
        Send the quick_boil command on the device.

        Equivalent to send_command("start_auto_boil", True).
        """
        return self.async_send_command("start_auto_boil", True)

    async def async_send_command(
        self,
        command_name: str,
        command_data_text: str = None,
        command_data_number: float = None,
        command_data_boolean: bool = None,
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
