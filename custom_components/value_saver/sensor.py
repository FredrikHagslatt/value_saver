import logging
import asyncio
from datetime import datetime, timedelta
import homeassistant.util.dt as dt_util

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity

logger = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    entity_to_save = config.get("entity_to_save")
    logger.info("Preparing to setup value saver with dependency: %s", entity_to_save)
    # Wait until the dependent integration is ready
    for _ in range(20):  # Retry up to 10 times
        if hass.states.get(entity_to_save):
            logger.info("Dependency is ready, setting up platform.")
            async_add_entities([DailyValueSensor(hass, entity_to_save=entity_to_save)])
            return
        logger.info("Waiting for dependency to be ready...")
        await asyncio.sleep(5)

    logger.error("Dependency '%s' not ready, aborting setup.", entity_to_save)


class DailyValueSensor(RestoreEntity, SensorEntity):
    def __init__(self, hass, entity_to_save):
        self.hass = hass
        self._entity_to_save = entity_to_save
        self._state = None
        self._last_update = None
        logger.info("Setting up sensor to save: %s", entity_to_save)

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
        today = now.date().isoformat()
        logger.info(
            "Update called. Last update: %s, Today: %s", self._last_update, today
        )

        if self._last_update != today:
            self._state = self.get_new_value()
            self._last_update = today
            self.schedule_update_ha_state()
            logger.info("Updating value to: %s", self._state)
        else:
            logger.info("Not updating value")

    def get_new_value(self):
        state = self.hass.states.get(self._entity_to_save)
        if state:
            logger.info("The state of %s is %s", self._entity_to_save, state.state)
            return state.state
        else:
            logger.warning("Entity %s not found", self._entity_to_save)
            return 0
