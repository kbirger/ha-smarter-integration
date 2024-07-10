"""Test Smarter Kettle and Coffee integration switches."""

from types import SimpleNamespace
from unittest.mock import call

import pytest
from custom_components.smarter.sensor import SmarterSensor
from custom_components.smarter.switch import SWITCH_TYPES
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import generate_unique_id, get_entity, get_unique_id


@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize(
    "expected_unique_id",
    [generate_unique_id(description.key) for description in SWITCH_TYPES],
    indirect=False,
)
def test_expected_switches(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    expected_unique_id,
):
    """Test that the expected sensor entities are created."""
    # for expected_unique_id in expected_switches:
    entity_id = get_unique_id(hass, expected_unique_id, Platform.SWITCH)
    assert entity_id is not None, f"entity {expected_unique_id} should exist"


@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize(
    "service_data",
    [
        SimpleNamespace(
            switch_key="start_boil", on_command="start_boil", off_command="stop_boil"
        )
    ],
)
async def test_switch_services(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    service_data: SimpleNamespace,
):
    """Test sensor entity services."""
    unique_id = generate_unique_id(service_data.switch_key)
    entity: SmarterSensor = get_entity(hass, unique_id, platform=Platform.SWITCH)
    device = entity.device
    device.send_command.return_value = "executed"

    await hass.services.async_call(
        Platform.SWITCH,
        SERVICE_TURN_ON,
        service_data={
            ATTR_ENTITY_ID: entity.entity_id,
        },
        blocking=True,
    )

    # Assert that the command was invoked with the correct args
    assert device.send_command.called
    assert device.send_command.call_args == call(
        service_data.on_command,
        True,
    )

    await hass.services.async_call(
        Platform.SWITCH,
        SERVICE_TURN_OFF,
        service_data={
            ATTR_ENTITY_ID: entity.entity_id,
        },
        blocking=True,
    )

    assert device.send_command.called
    assert device.send_command.call_args == call(
        service_data.off_command,
        True,
    )
