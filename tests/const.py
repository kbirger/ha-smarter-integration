"""Constants for Smarter Kettle and Coffee integration tests."""

from datetime import datetime
from unittest.mock import MagicMock

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

MOCK_CONFIG = {CONF_USERNAME: "test_username", CONF_PASSWORD: "test_password"}

MOCK_SESSION = {
    "kind": "mock_kind",
    "local_id": "mock_local_id",
    "email": "mock_email",
    "display_name": "mock_display_name",
    "id_token": "mock_id_token",
    "registered": True,
    "refresh_token": "mock_refresh_token",
    "session_duration": 100,
    "expires_at": datetime.max,
}
MOCK_USER = {
    "email": "mock_email",
    "accepted": 1,
    "first_name": "mock_first_name",
    "last_name": "mock_last_name",
    "location_accepted": 1,
    "networks_index": {"1": "mock_network_1"},
    "temperature_unit": 0,
}

MOCK_DEVICE_ID = "test_kettle1"
MOCK_DEVICE_NAME = "Test Kettle"
MOCK_DEVICE_INTERNAL = {
    "commands": MagicMock(spec=dict),
    "status": {"state": "Idle"},
    "identifier": MOCK_DEVICE_ID,
    "is_stub": False,
}

MOCK_DEVICE = {
    "identifier": MOCK_DEVICE_ID,
    "type": "kettle",
    "status": {
        "device_model": "TEST_KETTLE1",
        "state": "Idle",
        "boil_temperature": 99.0,
        "target_temperature": 99.0,
        "water_temperature": 80.0,
        "kettle_is_present": True,
        "keep_warm_time": 5.0,
    },
    "settings": MagicMock(**{"setting": 1}),
    "model": "TEST_KETTLE1",
    "firmware_version": "0.0.0",
    "id": "TEST01",
    "friendly_name": MOCK_DEVICE_NAME,
    "device": MagicMock(**MOCK_DEVICE_INTERNAL),
}


MOCK_NETWORK = {
    "access_tokens_fcm": dict(),
    "associated_devices": [MagicMock(**MOCK_DEVICE)],
    "name": "Mock Network",
    "owner": MagicMock(MOCK_USER),
}

MOCK_DEVICE_INTERNAL["settings"] = (
    MagicMock(identifier="/", model="TEST_KETTLE1", network=MagicMock(**MOCK_NETWORK)),
)
