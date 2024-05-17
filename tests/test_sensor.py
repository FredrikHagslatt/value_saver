import os
import sys

# Add the root directory of your integration to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import homeassistant.util.dt as dt_util
from custom_components.value_saver.sensor import DailyValueSensor


async def test_async_added_to_hass():
    hass_mock = MagicMock()
    sensor = DailyValueSensor(hass_mock)

    # Mock async_get_last_state to return a mock state
    mock_state = MagicMock()
    mock_state.state = "mock_state"
    mock_state.attributes = {"last_update": "mock_last_update"}
    with patch.object(sensor, "async_get_last_state", return_value=mock_state):
        await sensor.async_added_to_hass()

    # Assert that state and last_update were updated
    assert sensor._state == "mock_state"
    assert sensor._last_update == "mock_last_update"


def test_update():
    hass_mock = MagicMock()
    sensor = DailyValueSensor(hass_mock)

    # Mock get_new_value to return a mock value
    sensor.get_new_value = MagicMock(return_value="mock_value")

    # Set _last_update to yesterday
    yesterday = datetime.now().date() - timedelta(days=1)
    sensor._last_update = yesterday

    # Call update
    sensor.update()

    # Assert that state and last_update were updated
    assert sensor._state == "mock_value"
    assert sensor._last_update == datetime.now().date()


def test_get_new_value():
    hass_mock = MagicMock()
    sensor = DailyValueSensor(hass_mock)

    # Mock hass.states.get to return a mock state
    mock_state = MagicMock()
    mock_state.state = "mock_state"
    with patch.object(sensor.hass.states, "get", return_value=mock_state):
        value = sensor.get_new_value()

    # Assert that get_new_value returns the expected value
    assert value == "mock_state"
