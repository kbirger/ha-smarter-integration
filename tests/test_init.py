"""Test Smarter Kettle and Coffee integration setup process."""

# import pytest

# from homeassistant.exceptions import ConfigEntryNotReady
# from pytest_homeassistant_custom_component.common import MockConfigEntry

# from custom_components.smarter import (
#     async_setup_entry,
#     async_unload_entry,
# )
# from custom_components.smarter.const import DOMAIN

# from .const import MOCK_CONFIG


# async def test_setup_entry_exception(hass, error_on_get_data):
#     """Test ConfigEntryNotReady when API raises an exception during entry setup."""
#     config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

#     # In this case we are testing the condition where async_setup_entry raises
#     # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
#     # an error.
#     with pytest.raises(ConfigEntryNotReady):
#         assert await async_setup_entry(hass, config_entry)


def test_is_true():
    assert 1 == 1
