"""Defines some helpers for unit tests."""

from custom_components.smarter.const import DOMAIN
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.entity import Entity

from tests.const import MOCK_DEVICE, MOCK_DEVICE_ID


def generate_unique_id(
    entity_key, device_id=MOCK_DEVICE_ID, device_type=MOCK_DEVICE.get("type")
) -> str:
    """Generate an entity id."""
    key = entity_key or "device"
    return "-".join([device_id, device_type, key])


def get_unique_id(hass: HomeAssistant, unique_id, platform=Platform.SENSOR) -> str:
    """Get entity_id from entity_registry given unique id."""
    er = entity_registry.async_get(hass)

    # there is a bug in the documentation of this function
    # the actual order is platform, domain, unique_id
    return er.async_get_entity_id(platform, DOMAIN, unique_id)


def get_entity(hass: HomeAssistant, unique_id: str, platform=Platform.SENSOR) -> Entity:
    """Get entity by unique id."""
    return next(
        (
            entity
            for entity in hass.data[platform].entities
            if entity.unique_id == unique_id
        ),
        None,
    )
