"""Module for Smarter Kettle V3 device."""

from __future__ import annotations

from collections.abc import Generator, Iterable

from custom_components.smarter.const import (
    SERVICE_QUICK_BOIL,
    SERVICE_SCHEMA_QUICK_BOIL,
)
from custom_components.smarter.sensor import SmarterDeviceSensor
from homeassistant.components.number import (
    NumberDeviceClass,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from smarter_client.managed_devices.kettle_v3 import SmarterKettleV3

from .base import (
    DeviceConfig,
    ServiceMetadata,
    SmarterBinarySensorEntityDescription,
    SmarterEntityDescription,
    SmarterNumberEntityDescription,
    SmarterSensorEntityDescription,
    SmarterSwitchEntityDescription,
)

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

SWITCH_TYPES = [
    SmarterSwitchEntityDescription(
        key="start_boil",
        name="Boiling",
        get_fn=make_check_status("state", ["Boiling", "Keeping Warm", "Cooling"]),
        set_fn=set_boil,
        icon="mdi:kettle-steam",
    ),
]

NUMBER_TYPES = [
    SmarterNumberEntityDescription(
        key="boil_temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        name="Boil Temperature",
        set_fn=lambda device, value: device.set_boil_temperature(value),
    ),
    SmarterNumberEntityDescription(
        key="keep_warm_time",
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        name="Keep Warm Time",
        native_min_value=0,
        native_max_value=40,
        native_step=1,
        set_fn=lambda device, value: device.set_keep_warm_time(value),
    ),
]

ENTITY_TYPES = (
    *SENSOR_TYPES,
    *BINARY_SENSOR_TYPES,
    *SWITCH_TYPES,
)


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
