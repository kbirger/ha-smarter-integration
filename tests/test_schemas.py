"""Tests for various schemas, to make sure they are decalred correctly."""

import pytest
import voluptuous as vol
from custom_components.smarter.const import SERVICE_SCHEMA_SEND_COMMAND


@pytest.mark.parametrize(
    ["data"],
    [
        [
            {
                "entity_id": ["foo"],
                "command_name": "test",
                "command_data_text": "foo",
            }
        ],
        [
            {
                "device_id": ["foo"],
                "command_name": "test",
                "command_data_text": "foo",
            }
        ],
        [
            {
                "area_id": ["foo"],
                "command_name": "test",
                "command_data_text": "foo",
            }
        ],
        [
            {
                "label_id": ["foo"],
                "command_name": "test",
                "command_data_text": "foo",
            }
        ],
    ],
)
def test_send_command_schema(data):
    """Test all valid inputs."""
    schema = SERVICE_SCHEMA_SEND_COMMAND

    result = schema(data)

    assert result


def test_fails_on_missing_command_name():
    """Test missing command name."""
    with pytest.raises(vol.error.MultipleInvalid) as ex_info:
        input = {"entity_id": ["foo"], "command_data_number": 5.5}

        schema = SERVICE_SCHEMA_SEND_COMMAND

        schema(input)

    assert ex_info.value.msg == "required key not provided"


def test_fails_on_missing_target():
    """Test missing target."""
    with pytest.raises(vol.error.MultipleInvalid) as ex_info:
        input = {"command_name": "test", "command_data_number": 5.5}

        schema = SERVICE_SCHEMA_SEND_COMMAND

        schema(input)

    assert ex_info.value.msg == (
        "must contain at least one of entity_id, device_id, area_id,"
        " floor_id, label_id."
    )


@pytest.mark.parametrize(
    ["data"],
    [
        [
            {
                "entity_id": ["foo"],
                "command_name": "test",
                "command_data_text": "foo",
                "command_data_number": 5.5,
            }
        ],
        [
            {
                "entity_id": ["foo"],
                "command_name": "test",
                "command_data_text": "foo",
                "command_data_boolean": True,
            }
        ],
        [
            {
                "entity_id": ["foo"],
                "command_name": "test",
                "command_data_number": 5.5,
                "command_data_boolean": True,
            }
        ],
        [
            {
                "entity_id": ["foo"],
                "command_name": "test",
                "command_data_number": 5.5,
                "command_data_text": "foo",
                "command_data_boolean": True,
            }
        ],
    ],
)
def test_fails_on_duplicate_command_data(data):
    """Test more than one instance of command_data."""
    with pytest.raises(vol.error.MultipleInvalid) as ex_info:
        schema = SERVICE_SCHEMA_SEND_COMMAND

        schema(data)

    assert ex_info.value.msg == (
        "must contain at most one of command_data_boolean, "
        "command_data_text, command_data_number."
    )
