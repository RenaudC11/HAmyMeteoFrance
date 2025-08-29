import logging
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client

import math

DOMAIN = "mameteo"
_LOGGER = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

class MaMeteoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.api_key = user_input["api_key"]
            self.city = user_input["city"]
            self.entity_name = user_input["entity_name"]

            # Étape suivante : récupérer les stations
            return await self.async_step_station()

        schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("city"): str,
            vol.Required("entity_name", default="MaMeteo"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_station(self, user_input=None):
        session = aiohttp_client.async_get_clientsession(self.hass)

        # 1. Géocodage avec Nominatim
        async with session.get(f"https://nominatim.openstreetmap.org/search",
                               params={"q": self.city, "format": "json", "limit": 1}) as resp:
            data = await resp.json()
            if not data:
                return self.async_abort(reason="city_not_found")
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])

        # 2. Liste des stations Météo-France
        headers = {"apikey": self.api_key}
        async with session.get("https://public-api.meteofrance.fr/public/DPObs/v1/station", headers=headers) as resp:
            stations = await resp.json()

        # 3. Calcul des distances
        nearby = []
        for st in stations:
            s_lat, s_lon = st["lat"], st["lon"]
            dist = haversine(lat, lon, s_lat, s_lon)
            nearby.append({
                "id": st["id"],
                "name": st["nom"],
                "dist": round(dist, 1)
            })

        # 4. Tri par distance
        nearby.sort(key=lambda x: x["dist"])
        self.stations = nearby[:10]  # garder les 10 plus proches

        if user_input is not None:
            chosen = user_input["station"]
            return self.async_create_entry(
                title=f"{self.entity_name} ({chosen})",
                data={
                    "api_key": self.api_key,
                    "city": self.city,
                    "entity_name": self.entity_name,
                    "station": chosen,
                }
            )

        # Créer une liste de choix {id: "Nom (X km)"}
        options = {st["id"]: f'{st["name"]} ({st["dist"]} km)' for st in self.stations}
        schema = vol.Schema({
            vol.Required("station"): vol.In(options)
        })
        return self.async_show_form(step_id="station", data_schema=schema)


