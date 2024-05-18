import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN


@callback
def configured_instances(hass):
    """Return a set of configured instances."""
    return set(
        entry.data.get("entity_to_save")
        for entry in hass.config_entries.async_entries(DOMAIN)
    )


class ValueSaverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Value Saver."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            entity_to_save = user_input["entity_to_save"]
            if entity_to_save in configured_instances(self.hass):
                errors["base"] = "already_configured"
            else:
                return self.async_create_entry(title=entity_to_save, data=user_input)

        schema = vol.Schema(
            {
                vol.Required("entity_to_save"): cv.entity_id,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
