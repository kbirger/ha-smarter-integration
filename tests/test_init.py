"""Test Smarter Kettle and Coffee integration setup process."""

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.smarter.const import DOMAIN


@pytest.mark.parametrize("init_integration", [(True,)], indirect=True)
@pytest.mark.parametrize("bypass_get_data", [{}], indirect=True)
async def test_async_setup_entry(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    bypass_get_data,
):
    entry = init_integration

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]
    assert entry.state == ConfigEntryState.LOADED

    # make sure all child entries have loaded
    assert set(
        ["smarter", "smarter.switch", "smarter.sensor", "smarter.binary_sensor"]
    ).issubset(hass.config.components)

    # Unload
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]
