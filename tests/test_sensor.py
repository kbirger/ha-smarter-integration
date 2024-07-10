"""Test Smarter Kettle and Coffee integration sensors."""

from types import SimpleNamespace
from unittest.mock import call

import pytest
from custom_components.smarter.const import (
    DOMAIN,
    SERVICE_ATTR_COMMAND_DATA_BOOLEAN,
    SERVICE_ATTR_COMMAND_DATA_NUMBER,
    SERVICE_ATTR_COMMAND_DATA_TEXT,
    SERVICE_ATTR_COMMAND_NAME,
    SERVICE_QUICK_BOIL,
    SERVICE_SEND_COMMAND,
)
from custom_components.smarter.sensor import SENSOR_TYPES, SmarterSensor
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import generate_unique_id, get_entity, get_unique_id


@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize(
    "service_data",
    [
        SimpleNamespace(
            # name of service
            service_name=SERVICE_QUICK_BOIL,
            # data attribute name (to simplify verification)
            data_key=SERVICE_ATTR_COMMAND_DATA_BOOLEAN,
            # send Smarter command data in HA service call. False for services that
            # generate command data themselves
            send_data=False,
            # command data. if `send_data` is true, this is sent in HA call.
            # otherwise it is only used to verify the command call to Smarter API
            data={
                SERVICE_ATTR_COMMAND_NAME: "start_auto_boil",
                SERVICE_ATTR_COMMAND_DATA_BOOLEAN: True,
            },
        ),
        SimpleNamespace(
            service_name=SERVICE_SEND_COMMAND,
            data_key=SERVICE_ATTR_COMMAND_DATA_TEXT,
            send_data=True,
            data={
                SERVICE_ATTR_COMMAND_NAME: "start_boil",
                SERVICE_ATTR_COMMAND_DATA_TEXT: "yes",  # not realistic value
            },
        ),
        SimpleNamespace(
            service_name=SERVICE_SEND_COMMAND,
            data_key=SERVICE_ATTR_COMMAND_DATA_BOOLEAN,
            send_data=True,
            data={
                SERVICE_ATTR_COMMAND_NAME: "stop_boil",
                SERVICE_ATTR_COMMAND_DATA_BOOLEAN: True,
            },
        ),
        SimpleNamespace(
            service_name=SERVICE_SEND_COMMAND,
            data_key=SERVICE_ATTR_COMMAND_DATA_NUMBER,
            send_data=True,
            data={
                SERVICE_ATTR_COMMAND_NAME: "set_boil_temperature",
                SERVICE_ATTR_COMMAND_DATA_NUMBER: 1.1,
            },
        ),
    ],
    indirect=False,
)
async def test_sensor_services(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    service_data: SimpleNamespace,
):
    """Test sensor entity services."""
    unique_id = generate_unique_id(None)
    entity: SmarterSensor = get_entity(hass, unique_id)
    device = entity.device
    device.send_command.return_value = "executed"

    result = await hass.services.async_call(
        DOMAIN,
        service_data.service_name,
        service_data={
            ATTR_ENTITY_ID: entity.entity_id,
            **(service_data.data if service_data.send_data else {}),
        },
        blocking=True,
        return_response=True,
    )

    # Assert that the command was invoked with the correct args
    # and returned expected result
    assert device.send_command.called
    assert device.send_command.call_args == call(
        service_data.data[SERVICE_ATTR_COMMAND_NAME],
        service_data.data[service_data.data_key],
    )
    assert result == {entity.entity_id: "executed"}


@pytest.mark.parametrize("init_integration", [(False,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
@pytest.mark.parametrize(
    "expected_unique_id",
    [generate_unique_id(description.key) for description in SENSOR_TYPES],
    indirect=False,
)
def test_expected_sensors(
    hass: HomeAssistant,
    bypass_get_data,
    init_integration: MockConfigEntry,
    expected_unique_id,
):
    """Test that the expected sensor entities are created."""
    entity_id = get_unique_id(hass, expected_unique_id)
    assert entity_id is not None, f"sensor {expected_unique_id} should exist"
