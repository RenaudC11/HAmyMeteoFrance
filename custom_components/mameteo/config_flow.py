from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_STATION_ID,
    CONF_ENTITY_NAME,
    CONF_MODE,
    CONF_UPDATE_MINUTES,
    DEFAULT_ENTITY_NAME,
    DEFAULT_STATION_ID,
    DEFAULT_UPDATE_MINUTES,
    MODE_SINGLE,
    MODE_SPLIT,
)

class MameteoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Création de l'entrée
            return self.async_create_entry(
                title=user_input.get(CONF_ENTITY_NAME, DEFAULT_ENTITY_NAME),
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_API_KEY, description={"suggested_value": ""}): str,
            vol.Required(CONF_STATION_ID, default=DEFAULT_STATION_ID): str,
            vol.Optional(CONF_ENTITY_NAME, default=DEFAULT_ENTITY_NAME): str,
            vol.Required(CONF_MODE, default=MODE_SINGLE): vol.In({
                MODE_SINGLE: "Un seul capteur (température) avec toutes les autres valeurs en attributs",
                MODE_SPLIT: "Un capteur par valeur",
            }),
            vol.Optional(CONF_UPDATE_MINUTES, default=DEFAULT_UPDATE_MINUTES): vol.All(int, vol.Range(min=1, max=60)),
        })

        return self.async_show_form(step_id="user", data_schema=schema)
