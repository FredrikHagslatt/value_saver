import os
import sys

# Add the root directory of your integration to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
import homeassistant.util.dt as dt_util
from homeassistant.core import State
from custom_components.value_saver.sensor import DailyValueSensor, async_setup_platform


@pytest.fixture
def hass_mock():
    hass = MagicMock()
    hass.states = MagicMock()

    def get_state(entity_id):
        if entity_id == "sensor.mock":
            return State(entity_id, 42)
        else:
            return None

    hass.states.get = get_state
    return hass


@pytest.mark.asyncio
async def test_async_setup_platform(hass_mock):

    config = {"entity_to_save": "sensor.mock"}

    async_add_entities_mock = AsyncMock()
    # Patch asyncio.sleep to avoid actual waiting during the test
    with patch("asyncio.sleep", return_value=None) as sleep_mock:
        await async_setup_platform(hass_mock, config, async_add_entities_mock)

    # Ensure that the async_add_entities was called once with a DailyValueSensor instance
    async_add_entities_mock.assert_called_once()
    sleep_mock.assert_not_called()
    assert isinstance(async_add_entities_mock.call_args[0][0][0], DailyValueSensor)


@pytest.mark.asyncio
async def test_async_setup_platform_failed(hass_mock):

    config = {"entity_to_save": "sensor.missing_sensor"}

    async_add_entities_mock = AsyncMock()
    # Patch asyncio.sleep to avoid actual waiting during the test
    with patch("asyncio.sleep", return_value=None) as sleep_mock:
        await async_setup_platform(hass_mock, config, async_add_entities_mock)

    # Ensure that the async_add_entities was called once with a DailyValueSensor instance
    async_add_entities_mock.assert_not_called()
    # entity_ids_mock.assert_called()
    sleep_mock.assert_called()


def test_update_new_day(hass_mock):
    sensor = DailyValueSensor(hass_mock, entity_to_save="sensor.mock")
    sensor.get_new_value = MagicMock(return_value="mock_value")

    # Set _last_update to yesterday
    yesterday = datetime.now().date() - timedelta(days=1)
    sensor._last_update = yesterday

    # Call update
    sensor.update()

    # Assert that state and last_update were updated
    sensor.get_new_value.assert_called_once()
    assert sensor._state == "mock_value"
    assert sensor._last_update == datetime.now().date()


def test_update_same_day(hass_mock):
    sensor = DailyValueSensor(hass_mock, entity_to_save="sensor.mock")
    sensor._state = "init_value"

    # Mock get_new_value to return a mock value
    sensor.get_new_value = MagicMock(return_value="mock_value")

    # Set _last_update to today
    yesterday = datetime.now().date()
    sensor._last_update = yesterday

    # Call update
    sensor.update()

    # Assert that state and last_update were not updated
    sensor.get_new_value.assert_not_called()
    assert sensor._state == "init_value"
    assert sensor._last_update == datetime.now().date()


def test_get_new_value(hass_mock):
    sensor = DailyValueSensor(hass_mock, entity_to_save="sensor.mock")

    # Mock hass.states.get to return a mock state
    mock_state = MagicMock()
    mock_state.state = "mock_value"
    with patch.object(sensor.hass.states, "get", return_value=mock_state):
        value = sensor.get_new_value()

    # Assert that get_new_value returns the expected value
    assert value == "mock_value"
