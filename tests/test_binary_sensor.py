"""Test Smarter Kettle and Coffee integration binary_sensors."""

from unittest.mock import patch

import pytest
from custom_components.smarter.binary_sensor import (
    BINARY_SENSOR_TYPES,
    SmarterBinarySensorEntityDescription,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import generate_unique_id, get_entity, get_unique_id


@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize(
    "expected_unique_id",
    [generate_unique_id(description.key) for description in BINARY_SENSOR_TYPES],
    indirect=False,
)
def test_expected_binary_sensors(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    expected_unique_id,
):
    """Test that the expected sensor entities are created."""
    entity_id = get_unique_id(hass, expected_unique_id, Platform.BINARY_SENSOR)
    assert entity_id is not None, f"entity {expected_unique_id} should exist"


@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize(
    "data",
    BINARY_SENSOR_TYPES,
    indirect=False,
)
def test_binary_sensor_values(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    data: SmarterBinarySensorEntityDescription,
):
    """Test binary sensor values."""
    entity = get_entity(
        hass, generate_unique_id(data.key), platform=Platform.BINARY_SENSOR
    )

    device = entity.device

    for value in data.state_on_values:
        with patch.dict(device.status, {data.get_status_field: value}):
            assert (
                entity.is_on
            ), f"expected entity {entity.unique_id} to be on when status is {value}"
