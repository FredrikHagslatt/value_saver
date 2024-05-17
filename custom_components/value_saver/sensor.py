import logging
from datetime import datetime, timedelta
import homeassistant.util.dt as dt_util

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity

logger = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    logger.info("Setting up platform with hass: %s", hass)
    async_add_entities([DailyValueSensor(hass)])


"""
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Wait until the dependent integration is ready
    for _ in range(10):  # Retry up to 10 times
        if 'sensor.dependency_sensor' in hass.states.async_entity_ids():
            logger.info("Dependency is ready, setting up platform.")
            async_add_entities([DailyValueSensor(hass)])
            return
        logger.info("Waiting for dependency to be ready...")
        await asyncio.sleep(10)

    logger.error("Dependency not ready, aborting setup.")
"""


class DailyValueSensor(RestoreEntity, SensorEntity):
    def __init__(self, hass):
        self.hass = hass
        self._state = None
        self._last_update = None
        logger.info("DailyValueSensor initialized with hass: %s", hass)

    @property
    def name(self):
        return "Daily Value"

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._state = last_state.state
            self._last_update = last_state.attributes.get("last_update")
        logger.info("async_added_to_hass called. Current state: %s", self._state)

    @property
    def extra_state_attributes(self):
        return {"last_update": self._last_update}

    def update(self):
        now = dt_util.now()
        today = now.date()
        logger.info("Update called. Now: %s, Today: %s", now, today)

        if self._last_update != today:
            self._state = self.get_new_value()
            self._last_update = today
            self.schedule_update_ha_state()

    def get_new_value(self):
        entity_id = "sensor.some_other_sensor"
        state = self.hass.states.get(entity_id)
        if state:
            logger.info("The state of %s is %s", entity_id, state.state)
            return state.state
        else:
            logger.warning("Entity %s not found", entity_id)
            return 42
