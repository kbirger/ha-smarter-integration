"""Module for Smarter Kettle V3 device."""

from collections.abc import Generator, Iterable

from custom_components.smarter.const import (
    SERVICE_QUICK_BOIL,
    SERVICE_SCHEMA_QUICK_BOIL,
)
from custom_components.smarter.sensor import SmarterDeviceSensor
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from smarter_client.managed_devices.kettle_v3 import SmarterKettleV3

from ..entity import (
    SmarterBinarySensorEntityDescription,
    SmarterEntityDescription,
    SmarterSensorEntityDescription,
)
from .base import DeviceConfig, ServiceMetadata

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

BINARY_SENSOR_TYPES = [
    SmarterBinarySensorEntityDescription(
        key="is_boiling",
        name="Boiling",
        get_status_field="state",
        state_on_values=("Boiling",),
    ),
    SmarterBinarySensorEntityDescription(
        key="is_cooling",
        name="Cooling",
        get_status_field="state",
        state_on_values=("Cooling",),
    ),
    SmarterBinarySensorEntityDescription(
        key="is_keep_warm",
        name="Keeping warm",
        get_status_field="state",
        state_on_values=("Keeping Warm",),
    ),
    SmarterBinarySensorEntityDescription(
        key="kettle_is_present",
        name="Kettle is Present",
        icon="mdi:kettle",
        get_status_field="kettle_is_present",
        state_on_values=(True,),
    ),
]


ENTITY_TYPES = (*SENSOR_TYPES, *BINARY_SENSOR_TYPES)


class SmarterKettleV3DeviceConfig(DeviceConfig):
    """
    Represents configuration for smarter kettle v3.
    Contains metadata for sensors and services.
    """  # noqa: D205

    _device: SmarterKettleV3

    def __init__(self, device: SmarterKettleV3):
        """Construct new instance of configuration object."""
        self._device = device

    @property
    def device_entity(self) -> SmarterEntityDescription:
        """Get main entity for the device that represents the kettle as a whole."""
        return SmarterSensorEntityDescription(
            key="device", name=None, has_entity_name=True, icon="mdi:kettle"
        )

    @property
    def secondary_entities(self) -> Generator[SmarterEntityDescription]:
        """Get all secondary entities for the device."""
        return (description for description in ENTITY_TYPES)

    @property
    def service_metadata(self):
        """Get global service metadata for Smarter Kettle."""
        return SmarterKettleDeviceSensor.get_service_metadata()


class SmarterKettleDeviceSensor(SmarterDeviceSensor):
    """Implementation of the main sensor for the smarter kettle integration."""

    @classmethod
    def get_service_metadata(clazz) -> Iterable[ServiceMetadata]:
        """Get metadata for services for this device type."""
        return (
            ServiceMetadata(
                service_name=SERVICE_QUICK_BOIL,
                handler_name=clazz.async_quick_boil.__name__,
                schema=SERVICE_SCHEMA_QUICK_BOIL,
            ),
        )

    async def async_quick_boil(self):
        """
        Send the quick_boil command on the device.

        Equivalent to send_command("start_auto_boil", True).
        """
        return self.async_send_command("start_auto_boil", True)
