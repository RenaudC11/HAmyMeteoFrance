"""Sensor platform for Mameteo (single sensor with attributes)."""
import logging
from datetime import timedelta
from typing import Any

import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

API_URL = "https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m"

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback):
    """Set up the mameteo sensor from a config entry."""
    cfg = hass.data[DOMAIN][entry.entry_id]
    api_key = cfg["api_key"]
    station = cfg["station"]
    update_interval = cfg["update_interval"]
    entity_name = cfg["entity_name"]

    async_add_entities([MeteoFranceSensor(api_key, station, update_interval, entity_name)], True)


class MeteoFranceSensor(SensorEntity):
    """Single sensor storing all Meteo-France fields in attributes."""

    def __init__(self, api_key: str, station: str, update_interval: int, entity_name: str):
        self._api_key = api_key
        self._station = station
        self._update_interval = timedelta(minutes=update_interval)
        self._entity_name = entity_name

        self._attr_name = entity_name
        self._attr_unique_id = f"{entity_name}_{station}"
        self._attr_should_poll = True
        self._attr_extra_state_attributes: dict[str, Any] = {}
        self._attr_native_value = None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"{self._entity_name}_{self._station}")},
            "name": f"Ma Météo France ({self._entity_name})",
            "manufacturer": "Météo-France",
            "model": "DPObs 6min",
        }

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._attr_extra_state_attributes

    @property
    def scan_interval(self) -> timedelta:
        return self._update_interval

    def update(self) -> None:
        """Fetch data from Meteo-France (synchronous)."""
        try:
            params = {"id_station": self._station, "format": "json", "apikey": self._api_key}
            resp = requests.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) == 0:
                _LOGGER.error("Unexpected API response or empty data: %s", data)
                return

            obs = data[0]

            t = obs.get("t")
            t_10 = obs.get("t_10")
            t_20 = obs.get("t_20")
            t_100 = obs.get("t_100")
            ff = obs.get("ff")
            fxi10 = obs.get("fxi10")
            p = obs.get("pres")
            rg = obs.get("ray_glo01")

            attrs: dict[str, Any] = {
                "reference_time": {"value": obs.get("reference_time"), "unit": "UTC"},
                "temperature": {"value": round((t - 273.15), 2) if t else None, "unit": "°C"},
                "temperature_10cm": {"value": round((t_10 - 273.15), 2) if t_10 else None, "unit": "°C"},
                "temperature_20cm": {"value": round((t_20 - 273.15), 2) if t_20 else None, "unit": "°C"},
                "temperature_100cm": {"value": round((t_100 - 273.15), 2) if t_100 else None, "unit": "°C"},
                "humidite": {"value": obs.get("u"), "unit": "%"},
                "pression": {"value": round((p / 100), 1) if p else None, "unit": "hPa"},
                "vent_direction": {"value": obs.get("dd"), "unit": "°"},
                "vent_force": {"value": round((ff * 3.6), 1) if ff else None, "unit": "km/h"},
                "rafale_direction": {"value": obs.get("dxi10"), "unit": "°"},
                "rafale_force": {"value": round((fxi10 * 3.6), 1) if fxi10 else None, "unit": "km/h"},
                "precipitation": {"value": obs.get("rr_per"), "unit": "mm"},
                "puissance_solaire": {"value": round((rg / 360), 2) if rg else None, "unit": "W/m²"},
                "ensoleillement": {"value": obs.get("insolh"), "unit": "min"},
                "visibilite": {"value": obs.get("vv"), "unit": "m"},
                """ "raw": obs, """
            }

            self._attr_native_value = attrs["temperature"]["value"]
            self._attr_extra_state_attributes = attrs

        except Exception as exc:
            _LOGGER.error("Error fetching Meteo-France data: %s", exc)
