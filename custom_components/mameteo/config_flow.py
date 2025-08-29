import logging
import requests
import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, CONF_API_KEY, CONF_STATION_ID, CONF_CITY, CONF_NAME, CONF_DISPLAY_MODE, MODE_ATTRIBUTES, MODE_MULTIPLE

_LOGGER = logging.getLogger(__name__)

STATION_URL = "https://public-api.meteofrance.fr/public/DPObs/v1/station"

class MameteoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.user_input = {}
        self.stations = []

    async def async_step_user(self, user_input=None):
        if user_input:
            self.user_input[CONF_CITY] = user_input["city"]
            return await self.async_step_select_station()
        schema = vol.Schema({vol.Required("city"): str})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_select_station(self, user_input=None):
        if user_input:
            self.user_input[CONF_STATION_ID] = user_input.get("station_id")
            return await self.async_step_finalize()

        city = self.user_input[CONF_CITY]
        try:
            response = requests.get(f"{STATION_URL}/search?commune={city}")
            response.raise_for_status()
            data = response.json()
            self.stations = data.get("results", [])
        except Exception as e:
            _LOGGER.warning("Impossible de récupérer les stations: %s", e)
            return await self.async_step_manual_station()

        if not self.stations:
            return await self.async_step_manual_station()

        options = {st["id"]: f"{st['nom']} ({st['id']})" for st in self.stations[:10]}
        schema = vol.Schema({vol.Required("station_id"): vol.In(options)})
        return self.async_show_form(step_id="select_station", data_schema=schema)

    async def async_step_manual_station(self, user_input=None):
        if user_input:
            self.user_input[CONF_STATION_ID] = user_input["station_id"]
            return await self.async_step_finalize()
        schema = vol.Schema({vol.Required("station_id"): str})
        return self.async_show_form(step_id="manual_station", data_schema=schema)

    async def async_step_finalize(self, user_input=None):
        if user_input:
            self.user_input.update(user_input)
            return self.async_create_entry(title=f"Météo {self.user_input[CONF_CITY]}", data=self.user_input)
        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_NAME, default="mameteo"): str,
            vol.Required(CONF_DISPLAY_MODE, default=MODE_ATTRIBUTES): vol.In({
                MODE_ATTRIBUTES: "Un sensor avec attributs",
                MODE_MULTIPLE: "Un sensor par valeur"
            })
        })
        return self.async_show_form(step_id="finalize", data_schema=schema)

