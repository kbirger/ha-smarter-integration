"""Helpers for retrieving entity configuration for a Smarter device."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from fnmatch import fnmatch
from os import walk
from os.path import dirname, join, splitext
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import EntityCategory, Platform, UnitOfTemperature
from homeassistant.helpers.entity import EntityDescription
from homeassistant.util import slugify
from homeassistant.util.yaml import load_yaml
from smarter_client.managed_devices.base import BaseDevice

import custom_components.smarter.devices as device_config_module

# from .smarter_coffee_v2 import SmarterKettleV3DeviceConfig


_LOGGER = logging.getLogger(__name__)


_CONFIG_DIR = dirname(device_config_module.__file__)

UNIT_ASCII_MAP = {
    "C": UnitOfTemperature.CELSIUS.value,
    "F": UnitOfTemperature.FAHRENHEIT.value,
}


def unit_from_ascii(unit):
    """Return unit from plain ascii representation."""
    if unit in UNIT_ASCII_MAP:
        return UNIT_ASCII_MAP[unit]

    return unit


class SmarterDeviceConfig:
    """Representation of a device configuration entry."""

    _filename: str
    _config: dict

    def __init__(self, filename: str):
        """Initialize the configuration from a file."""
        self._filename = filename
        config_path = join(_CONFIG_DIR, filename)
        config = load_yaml(config_path)

        if isinstance(config, dict):
            self._config = config
        else:
            raise ValueError(f"Invalid config {filename}")

    @property
    def name(self):
        """Return the friendly name for this device."""
        return self._config["name"]

    @property
    def filename(self):
        """Return the name of the config file associated with this device."""
        return self._filename

    @property
    def config_type(self):
        """Return the config type associated with this device."""
        return splitext(self._fname)[0]

    @property
    def primary_entity(self):
        """Return the primary type of entity for this device."""
        return SmarterEntityConfig(
            self,
            self._config["primary_entity"],
            primary=True,
        )

    @property
    def products(self) -> set[dict]:
        """Return list of supported product models."""
        return self._config.get("products", [])

    def secondary_entities(self):
        """Iterate through entites for any secondary entites supported."""
        for conf in self._config.get("secondary_entities", {}):
            yield SmarterEntityConfig(self, conf)

    def all_entities(self):
        """Iterate through all entities for this device."""
        yield self.primary_entity
        yield from self.secondary_entities()

    def get_all_entities(self, platform: Platform) -> Iterable[SmarterEntityConfig]:
        """Return configs for all entities in the device."""
        return (entity for entity in self.all_entities() if entity.entity == platform)

    def get_secondary_entities(self, platform: Platform) -> Iterable[SmarterEntityConfig]:
        """Get all non-device-level entities for platform."""
        return (entity for entity in self.secondary_entities() if entity.platform == platform)

    def get_primary_entities(self, platform: Platform) -> Iterable[SmarterEntityConfig]:
        """Get main device-level entities for target platform."""
        return [self.primary_entity] if self.primary_entity.platform == platform else []

    def matches(self, product_ids) -> bool:
        """Return true if this configuration matches any of the given product_ids."""
        return any(set(product_ids).intersection([product.get("model") for product in self.products]))


class SmarterEntityConfig:
    """Representation of an entity configuration."""

    _device: SmarterDeviceConfig
    _config: dict
    _is_primary: bool

    def __init__(self, device: SmarterDeviceConfig, config: dict, primary=False):
        """Construct an instance of the configuration."""
        self._device = device
        self._config = config
        self._is_primary = primary

    @property
    def name(self):
        """The friendly name for this entity."""
        return self._config.get("name")

    @property
    def translation_key(self):
        """The translation key for this entity."""
        translation_key = self._config.get("translation_key", self.name)
        return translation_key if translation_key is not None else self.name

    @property
    def translation_only_key(self):
        """The translation key for this entity, not used for unique_id."""
        return self._config.get("translation_only_key")

    @property
    def translation_placeholders(self):
        """The translation placeholders for this entity."""
        return self._config.get("translation_placeholders", {})

    def unique_id(self, device_uid):
        """Return a suitable unique_id for this entity."""
        return f"{device_uid}-{slugify(self.config_id)}"

    @property
    def entity(self) -> str:
        """The entity type of this entity."""
        return self._config["entity"]

    @property
    def config_id(self):
        """The identifier for this entity in the config."""
        own_name = self._config.get("name")
        if own_name:
            return f"{self.entity}_{slugify(own_name)}"
        if self.translation_key:
            slug = f"{self.entity}_{self.translation_key}"
            for key, value in self.translation_placeholders.items():
                if key in slug:
                    slug = slug.replace(key, slugify(value))
                else:
                    slug = f"{slug}_{value}"
            return slug
        return self.entity

    @property
    def device_class(self):
        """The device class of this entity."""
        return self._config.get("device_class")

    @property
    def icon(self):
        """Return the icon for this entity, with state as given."""
        return self._config.get("icon", None)

    @property
    def mode(self):
        """Return the mode (used by Number entities)."""
        return self._config.get("mode")

    @property
    def _range(self):
        """Get the range of values."""
        return self._config.get("range", {"min": 0.0, "max": 100.0})

    @property
    def min(self):
        """Return minimum valid value."""
        return self._range["min"]

    @property
    def max(self):
        """Return maximum valid value."""
        return self._range["max"]

    @property
    def _mappings(self):
        return self._config.get("mapping", [])

    def _get_value_for_native(self, native_value: Any):
        for mapping in self._mappings:
            if mapping.get("native_value") == native_value:
                return mapping.get("value")
        return native_value

    def _get_native_value_for_value(self, value):
        for mapping in self.setter_mapping:
            if mapping.get("value") == value:
                return mapping.get("native_value")

        return value

    @property
    def _set_command(self):
        return self._config.get("setter")

    @property
    def step(self):
        """Return step increment size."""
        return self._config.get("step")

    @property
    def category(self) -> EntityCategory | None:
        """Return entity category."""
        return self._config.get("category")

    @property
    def unit(self):
        """Return unit name."""
        unit = self._config.get("unit")
        return unit_from_ascii(unit) if unit is not None else None

    @property
    def state_class(self):
        """The state class of this measurement."""
        return self._config.get("state_class")

    @property
    def key(self):
        """Return config key."""
        return self._config.get("key")

    @property
    def setter(self):
        """Return name of setter for this field."""
        return self._config.get("setter", [])

    @property
    def setter_mapping(self):
        """
        Return mapping of setters based on value.

        Some fields require one service to switch to one value, and a different service for another.
        """
        return self._config.get("setter_mapping", [])

    @property
    def state_field(self):
        """Get the field name on the state object that is tracked by this entity."""
        return self._config.get("state_field", self.name or self.translation_key)

    def get_value(self, device: BaseDevice):
        """Return value of entity."""
        if device.device.status is None:
            return None
        native_value = _get_path(device.device.status, self.state_field)
        return self._get_value_for_native(native_value)

    def set_value(self, device: BaseDevice, value):
        """Set entity value."""
        setters = self.setter_mapping
        setter_name = self._set_command
        setter_mapping = next((setter for setter in setters if setter.get("value") == value), None)

        if setter_mapping:
            try:
                setter_name = setter_mapping["setter"]
            except KeyError:
                raise ValueError(f"No setter name provided for {self.config_id} setter mapping for {value}")

        native_value = self._get_native_value_for_value(value)

        device.send_command(setter_name, native_value)

    # def available(self, device):
    #     """Return whether this entity should be available, with state as given."""
    #     avail_dp = self.find_dps("available")
    #     if avail_dp and device.has_returned_state:
    #         return avail_dp.get_value(device)
    #     return True

    @property
    def entity_description(self) -> EntityDescription:
        """Return entity description."""
        return EntityDescription(
            key=self.key,
            device_class=self.device_class,
            entity_category=self.category,
            icon=self.icon,
            translation_key=self.translation_key,
            translation_placeholders=self.translation_placeholders,
            name=None if self._is_primary else self.name,
            has_entity_name=True,
        )

    @property
    def binary_sensor_entity_description(self) -> BinarySensorEntityDescription:
        """Return binary entity description."""
        return BinarySensorEntityDescription(
            **self.entity_description.__dict__,
        )

    @property
    def sensor_entity_description(self) -> SensorEntityDescription:
        """Return sensor entity description."""
        return SensorEntityDescription(
            **self.entity_description.__dict__,
            native_unit_of_measurement=self.unit,
            state_class=self.state_class,
        )

    @property
    def switch_entity_description(self) -> SwitchEntityDescription:
        """Return switch entity description."""
        return SwitchEntityDescription(**self.entity_description.__dict__)

    @property
    def number_entity_description(self) -> NumberEntityDescription:
        """Return number entity description."""
        return NumberEntityDescription(
            key=self.key,
            device_class=self.device_class,
            entity_category=self.category,
            icon=self.icon,
            translation_key=self.translation_key,
            translation_placeholders=self.translation_placeholders,
            name=self.name,
            has_entity_name=True,
            native_min_value=self.min,
            native_max_value=self.max,
            step=self.step,
            native_unit_of_measurement=self.unit,
        )


def get_device_config(device: BaseDevice) -> SmarterDeviceConfig:
    """Get config object for the device."""
    return next(_get_matching_configs(device.model))


def available_configs():
    """List the available config files."""
    for path, dirs, files in walk(_CONFIG_DIR):
        for basename in sorted(files):
            if fnmatch(basename, "*.yaml"):
                yield basename


def _get_matching_configs(product_id):
    for cfg in available_configs():
        parsed = SmarterDeviceConfig(cfg)
        if parsed.matches([product_id]):
            yield parsed

    raise ValueError(f"Invalid device model {product_id}")


def _get_path(bucket: dict, path: str) -> Any:
    if dict is None or path is None:
        return None

    iter = bucket
    for item in path.split("."):
        if not isinstance(iter, dict):
            raise ValueError("bucket is not a dict")

        iter = iter.get(item)

    return iter
