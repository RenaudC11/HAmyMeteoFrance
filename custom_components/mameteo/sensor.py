import logging
import requests
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_API_KEY, CONF_STATION_ID, CONF_DISPLAY_MODE, MODE_ATTRIBUTES

_LOGGER = logging.getLogger(__name__)
API_URL = "https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m"
SCAN_INTERVAL = timedelta(minutes=10)

SENSOR_MAP = {
    "t": {"name": "Température", "unit": "°C", "device_class": "temperature", "state_class": "measurement"},
    "td": {"name": "Température rosée", "unit": "°C", "device_class": "temperature", "state_class": "measurement"},
    "tx": {"name": "Température max", "unit": "°C", "device_class": "temperature", "state_class": "measurement"},
    "tn": {"name": "Température min", "unit": "°C", "device_class": "temperature", "state_class": "measurement"},
    "u": {"name": "Humidité", "unit": "%", "device_class": "humidity", "state_class": "measurement"},
    "ux": {"name": "Humidité max", "unit": "%", "device_class": "humidity", "state_class": "measurement"},
    "un": {"name": "Humidité min", "unit": "%", "device_class": "humidity", "state_class": "measurement"},
    "dd": {"name": "Direction vent", "unit": "°", "device_class": None, "state_class": "measurement"},
    "ff": {"name": "Vitesse vent", "unit": "m/s", "device_class": "wind_speed", "state_class": "measurement"},
    "dxy": {"name": "Dir rafale max", "unit": "°", "device_class": None, "state_class": "measurement"},
    "fxy": {"name": "Vit rafale max", "unit": "m/s", "device_class": "wind_speed", "state_class": "measurement"},
    "dxi": {"name": "Dir vent instant", "unit": "°", "device_class": None, "state_class": "measurement"},
    "fxi": {"name": "Vit vent instant", "unit": "m/s", "device_class": "wind_speed", "state_class": "measurement"},
    "rr1": {"name": "Pluie 1h", "unit": "mm", "device_class": "precipitation", "state_class": "measurement"},
    "t_50": {"name": "Température sol 50cm", "unit": "°C", "device_class": "temperature", "state_class": "measurement"},
    "etat_sol": {"name": "État sol", "unit": None, "device_class": None, "state_class": None},
    "sss": {"name": "Neige sol", "unit": "cm", "device_class": None, "state_class": "measurement"},
    "n": {"name": "Nébulosité", "unit": "%", "device_class": None, "state_class": "measurement"},
    "ray_glo01": {"name": "Rayonnement global", "unit": "W/m²", "device_class": "irradiance", "state_class": "measurement"},
    "pres": {"name": "Pression station", "unit": "hPa", "device_class": "pressure", "state_class": "measurement"},
    "pmer": {"name": "Pression mer", "unit": "hPa", "device_class": "pressure", "state_class": "measurement"},
}

async def async_setup_entry(hass, entry, async_add_entities):
    api_key = entry.data[CONF_API_KEY]
    station_id = entry.data[CONF_STATION_ID]
    mode = entry.data.get(CONF_DISPLAY_MODE, MODE_ATTRIBUTES)
    entity_name = entry.data.get("entity_name", "mameteo")

    if mode == MODE_ATTRIBUTES:
        async_add_entities([MameteoUniqueSensor(api_key, station_id, entity_name)], True)
    else:
        entities = []
        for code, meta in SENSOR_MAP.items():
            entities.append(MameteoSingleSensor(api_key, station_id, f"{entity_name} {meta['name']}", code, meta))
        async_add_entities(entities, True)


class MameteoUniqueSensor(SensorEntity):
    def __init__(self, api_key, station_id, name):
        self._api_key = api_key
        self._station_id = station_id
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{station_id}_unique"
        self._attr_native_value = None
        self._attributes = {}

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        data = await self._fetch_data()
        if data:
            self._attr_native_value = data.get("t")
            self._attributes = data

    async def _fetch_data(self):
        try:
            headers = {"apikey": self._api_key}
            url = f"{API_URL}/{self._station_id}"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            json_data = resp.json()
            return json_data.get("obs", [{}])[-1]
        except Exception as e:
            _LOGGER.error("Erreur récupération Météo-France: %s", e)
            return None


class MameteoSingleSensor(SensorEntity):
    def __init__(self, api_key, station_id, name, code, meta):
        self._api_key = api_key
        self._station_id = station_id
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{code}"
        self._code = code
        self._meta = meta
        self._attr_device_class = meta.get("device_class")
        self._attr_native_unit_of_measurement = meta.get("unit")
        self._attr_state_class = meta.get("state_class")
        self._attr_native_value = None

    async def async_update(self):
        data = await self._fetch_data()
        if data:
            val = data.get(self._code)
            if val is not None and self._meta["unit"] == "°C":
                val = round(val - 273.15, 2)
            self._attr_native_value = val

    async def _fetch_data(self):
        try:
            headers = {"apikey": self._api_key}
            url = f"{API_URL}/{self._station_id}"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            json_data = resp.json()
            return json_data.get("obs", [{}])[-1]
        except Exception as e:
            _LOGGER.error("Erreur récupération Météo-France: %s", e)
            return None
