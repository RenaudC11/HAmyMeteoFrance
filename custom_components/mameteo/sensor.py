import logging
from datetime import timedelta
import requests
from homeassistant.helpers.entity import SensorEntity
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

API_URL = "https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m"

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup du capteur depuis une config entry (UI)."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api_key = entry_data.get("api_key")
    station = entry_data.get("station")
    update_interval = entry_data.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    entity_name = entry_data.get("entity_name", "mameteo")

    async_add_entities([MeteoFranceSensor(api_key, station, update_interval, entity_name)], True)


class MeteoFranceSensor(SensorEntity):
    """Capteur unique pour toutes les données Météo-France."""

    def __init__(self, api_key, station, update_interval, entity_name):
        self._api_key = api_key
        self._station = station
        self._attrs = {}
        self._state = None
        self._update_interval = timedelta(minutes=update_interval)
        self._entity_name = entity_name

    @property
    def name(self):
        return self._entity_name

    @property
    def unique_id(self):
        return f"{self._entity_name}_{self._station}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"{self._entity_name}_{self._station}")},
            "name": f"Ma Météo France ({self._entity_name})",
            "manufacturer": "Météo-France",
            "model": "DPObs 6 min",
        }

    @property
    def should_poll(self):
        return True

    @property
    def scan_interval(self):
        return self._update_interval

    @property
    def state(self):
        return self._attrs.get("temperature", {}).get("value")

    @property
    def extra_state_attributes(self):
        return self._attrs

    def update(self):
        """Récupération des données depuis l'API Météo-France avec unités."""
        try:
            params = {"id_station": self._station, "format": "json", "apikey": self._api_key}
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
            resp = response.json()[0]

            # Conversions utiles
            t = resp.get('t')
            t_10 = resp.get('t_10')
            t_20 = resp.get('t_20')
            t_100 = resp.get('t_100')
            ff = resp.get('ff')
            fxi10 = resp.get('fxi10')
            p = resp.get('pres')
            rg = resp.get('ray_glo01')

            self._attrs = {
                "reference_time": {"value": resp.get("reference_time"), "unit": "UTC"},
                "temperature": {"value": t-273.15 if t is not None else None, "unit": "°C"},
                "temperature_10cm": {"value": t_10-273.15 if t_10 is not None else None, "unit": "°C"},
                "temperature_20cm": {"value": t_20-273.15 if t_20 is not None else None, "unit": "°C"},
                "temperature_100cm": {"value": t_100-273.15 if t_100 is not None else None, "unit": "°C"},
                "humidite": {"value": resp.get("u"), "unit": "%"},
                
                # Pression atmosphérique réduite au niveau de la mer en hPa
                "pression": {"value": p/100 if p is not None else None, "unit": "hPa"},
                "vent_direction": {"value": resp.get("dd"), "unit": "°"},
                "vent_force": {"value": ff*3.6 if ff is not None else None, "unit": "km/h"},
                "rafale_direction": {"value": resp.get("dxi10"), "unit": "°"},
                "rafale_force": {"value": fxi10*3.6 if fxi10 is not None else None, "unit": "km/h"},
                "precipitation": {"value": resp.get("rr_per"), "unit": "mm"},
                "puissance_solaire": {"value": rg/360 if rg is not None else None, "unit": "W/m²"},
                "ensoleillement": {"value": resp.get("insolh"), "unit": "min"},
                "visibilite": {"value": resp.get("vv"), "unit": "m"},
                "raw": resp
            }

        except Exception as e:
            _LOGGER.error("Erreur lors de l'appel API Météo-France : %s", e)
