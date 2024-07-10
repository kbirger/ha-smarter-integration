"""Test Smarter Kettle and Coffee integration numberes."""

from unittest.mock import call

import pytest
from custom_components.smarter.number import (
    NUMBER_TYPES,
    SmarterNumberEntityDescription,
)
from custom_components.smarter.sensor import SmarterSensor
from homeassistant.components.number import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import generate_unique_id, get_entity, get_unique_id


@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize(
    "expected_unique_id",
    [generate_unique_id(description.key) for description in NUMBER_TYPES],
    indirect=False,
)
def test_expected_numbers(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    expected_unique_id,
):
    """Test that the expected sensor entities are created."""
    # for expected_unique_id in expected_numberes:
    entity_id = get_unique_id(hass, expected_unique_id, Platform.NUMBER)
    assert entity_id is not None, f"entity {expected_unique_id} should exist"


@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("description", NUMBER_TYPES)
async def test_number_services(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    description: SmarterNumberEntityDescription,
):
    """Test sensor entity services."""
    key = description.key
    unique_id = generate_unique_id(key)
    value = description.native_max_value
    entity: SmarterSensor = get_entity(hass, unique_id, platform=Platform.NUMBER)
    device = entity.device
    device.send_command.return_value = "executed"

    await hass.services.async_call(
        Platform.NUMBER,
        SERVICE_SET_VALUE,
        service_data={ATTR_ENTITY_ID: entity.entity_id, ATTR_VALUE: value},
        blocking=True,
    )

    # Assert that the command was invoked with the correct args
    handler = getattr(device, f"set_{key}")
    assert handler.called
    assert handler.call_args == call(value)
