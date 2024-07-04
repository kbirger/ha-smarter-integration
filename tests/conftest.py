"""Global fixtures for Smarter Kettle and Coffee integration integration."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from custom_components.smarter.smarter_hub import SmarterHub
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG, MOCK_DEVICE, MOCK_NETWORK, MOCK_SESSION, MOCK_USER

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom integrations."""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss
# persistent notifications. These calls would fail without this fixture since the
# persistent_notification integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is
# useful for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with (
        patch(
            "custom_components.smarter.smarter_hub.SmarterHub.sign_in",
            side_effect=Exception,
        ),
        patch(
            "custom_components.smarter.smarter_hub.SmarterHub.get_user",
            side_effect=Exception,
        ),
        patch(
            "custom_components.smarter.smarter_hub.SmarterHub.discover_devices",
            side_effect=Exception,
        ),
    ):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    # config = getattr(request, "param", MOCK_CONFIG)
    return MockConfigEntry(
        domain="smarter",
        data=MOCK_CONFIG,
        version=1,
    )


@pytest.fixture
def mock_session():
    """Return mock session object."""
    return MagicMock(**MOCK_SESSION)


@pytest.fixture
def mock_network():
    """Return mock network object."""
    return MagicMock(**MOCK_NETWORK)


@pytest.fixture
def mock_user(mock_network):
    """Return mock user object."""
    return MagicMock(**MOCK_USER, networks={"1": mock_network})


@pytest.fixture
def mock_device():
    """Return mock device object."""
    return MagicMock(**MOCK_DEVICE)


# This fixture, when used, will result in calls to async_get_data to return None. To
# have the call return a value, we would add the `return_value=<VALUE_TO_RETURN>`
# parameter to the patch call.
@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture(mock_session, mock_user, mock_device, request):
    """Skip calls to get data from API."""
    params: dict[str, Any] = request.param

    def get_param(param: str, default: Any):
        if param in params:
            return params[param]

        return default

    with (
        patch(
            "custom_components.smarter.smarter_hub.SmarterHub.sign_in",
            return_value=get_param("session", mock_session),
        ),
        patch(
            "custom_components.smarter.smarter_hub.SmarterHub.get_user",
            return_value=get_param("user", mock_user),
        ),
        patch(
            "custom_components.smarter.smarter_hub.SmarterHub.discover_devices",
            return_value=get_param("devices", [mock_device]),
        ),
    ):
        yield


@pytest.fixture
def mock_hub(hass, mock_session, mock_user):
    """Return a mock hub object."""
    hub = SmarterHub(hass)
    hub.client = MagicMock()

    hub.client.sign_in.return_value = mock_session
    hub.client.get_user.return_value = mock_user

    return hub


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_hub, request
):
    """
    Patch the SmarterHub in the integration and add ConfigEntry to hass.

    Pass `skip_setup` flag as first arg in the `request` to skip caling integration
    setup. Useful for fixtures that need to perform additonal mocking before setup.
    """
    mock_config_entry.add_to_hass(hass)

    skip_setup = False
    if len(request.param) == 1:
        skip_setup = request.param[0]

    if not skip_setup:
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    return mock_config_entry
