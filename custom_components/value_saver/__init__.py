from homeassistant.helpers.restore_state import RestoreEntity

DOMAIN = "value_saver"


async def async_setup(hass, config):
    hass.states.async_set(f"{DOMAIN}.ready", "Integration loaded")
    return True
