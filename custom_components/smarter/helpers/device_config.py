"""Helpers for retrieving entity configuration for a Smarter device."""

from typing import cast

from smarter_client.managed_devices.base import BaseDevice
from smarter_client.managed_devices.kettle_v3 import SmarterKettleV3

from .base import DeviceConfig
from .smarter_kettle_v3 import SmarterKettleV3DeviceConfig


def get_device_config(device: BaseDevice) -> DeviceConfig:
    """Get config object for the device."""
    if device.model == "SMKET01":
        return SmarterKettleV3DeviceConfig(cast(SmarterKettleV3, device))
    # elif device.model == "SMCOF01":
    #     return None

    raise ValueError(f"Invalid device model {device.model}")
