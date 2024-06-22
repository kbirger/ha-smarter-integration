"""Test Smarter Kettle and Coffee integration switch."""

from unittest.mock import MagicMock, call, patch

import pytest
from custom_components.smarter import async_setup_entry
from custom_components.smarter.const import DOMAIN
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG, MOCK_DEVICE, MOCK_SESSION

DEFAULT_NAME = "DEFAULT_NAME"
SWITCH = "switch"


@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
async def test_switch_services(hass, bypass_get_data):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    with patch(
        "smarter_client.managed_devices.base.BaseDevice", spec=MOCK_DEVICE
    ) as device:
        device.device = MagicMock()
        device.device.commands = {
            "start_boil": MagicMock(),
            "stop_boil": MagicMock(),
        }
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
            blocking=True,
        )
        assert device.commands["stop_boil"].called
        assert device.commands["stop_boil"].call_args == call(
            MOCK_SESSION["local_id"], True
        )

        # title_func.reset_mock()

        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
            blocking=True,
        )
        assert device.commands["start_boil"].called
        assert device.commands["start_boil"].call_args == call(
            MOCK_SESSION["local_id"], True
        )
