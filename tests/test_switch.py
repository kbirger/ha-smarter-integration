"""Test Smarter Kettle and Coffee integration switch."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
import smarter_client.domain.smarter_client
from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG

DEFAULT_NAME = "DEFAULT_NAME"
SWITCH = "switch"


# @pytest.mark.asyncio
# @patch("smarter_client.domain.smarter_client.SmarterClient")
@pytest.fixture(autouse=True)
def patch_SmarterClient(monkeypatch):
    pass


@pytest.mark.skip()
async def test_switch_services(hass, monkeypatch, patch_SmarterClient):
    """Test switch services."""

    monkeypatch.setattr(
        smarter_client.domain.smarter_client, "SmarterClient", MagicMock()
    )
    from custom_components.smarter import async_setup_entry
    from custom_components.smarter.const import DOMAIN

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    client = smarter_client.domain.smarter_client.SmarterClient
    # with patch("smarter_client.domain.smarter_client.SmarterClient") as client:
    client.sign_in.return_value = asyncio.Future()
    client.sign_in.set_result({"id": "test"})
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch("smarter_client.managed_devices.base.BaseDevice.device") as device:
        device.commands = {
            "start_boil": MagicMock(),
            "stop_boil": MagicMock(),
        }
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
            blocking=True,
        )
        # assert title_func.called
        # assert title_func.call_args == call("foo")

        # title_func.reset_mock()

        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
            blocking=True,
        )
        # assert title_func.called
        # assert title_func.call_args == call("bar")
