"""Test Smarter Kettle and Coffee integration config flow."""

from unittest.mock import MagicMock, patch

import pytest
from custom_components.smarter.const import DOMAIN
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_USERNAME

from .const import MOCK_CONFIG, MOCK_SESSION


@patch("smarter_client.domain.smarter_client.SmarterClient")
def mock_client():
    """Mock SmarterClient."""
    return MagicMock()


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with (
        patch(
            "custom_components.smarter.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.smarter.async_setup_entry",
            return_value=True,
        ),
        patch(
            "custom_components.smarter.async_unload_entry",
            return_value=True,
        ),
    ):
        yield


# Here we simiulate a successful config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
async def test_successful_config_flow(hass, bypass_get_data):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        "smarter", context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `test_username` for username and `test_password`
    # for password, it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert (
        result["title"] == MOCK_CONFIG[CONF_USERNAME]
    )  # later will move to config entry per device
    assert result["data"] == {
        **MOCK_CONFIG,
        "refresh_token": MOCK_SESSION["refresh_token"],
    }
    assert result["result"]


@pytest.mark.parametrize("bypass_get_data", [{"session": None}], indirect=True)
async def test_failed_config_flow_invalid_auth(hass, bypass_get_data):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_failed_config_flow_error(hass, error_on_get_data):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"base": "cannot_connect"}
