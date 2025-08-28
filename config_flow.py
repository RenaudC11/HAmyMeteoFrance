import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_KEY, CONF_STATION, DEFAULT_STATION, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL, CONF_ENTITY_NAME, DEFAULT_ENTITY_NAME

class MameteoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MaMétéo."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input.get(CONF_ENTITY_NAME, "Ma Météo France"), data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY, default=""): str,
            vol.Optional(CONF_STATION, default=DEFAULT_STATION): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
            vol.Optional(CONF_ENTITY_NAME, default=DEFAULT_ENTITY_NAME): str
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
