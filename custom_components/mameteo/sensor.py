"""Sensor platform for Mameteo (single sensor with attributes)."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
    CONF_API_KEY,
    CONF_STATION,
    CONF_UPDATE_INTERVAL,
    CONF_ENTITY_NAME,
)

_LOGGER = logging.getLogger(__name__)

# API endpoint used (DPObs 6-minute observations)
API_URL = "https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m"


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback):
    """Set up the mameteo sensor from a config entry."""
    # read stored config in hass.data (populated by async_setup_entry in __init__.py)
    cfg = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    api_key = cfg.get("api_key")
    station = cfg.get("station")
    update_interval = cfg.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    entity_name = cfg.get("entity_name", "mameteo")

    async_add_entities([MeteoFranceSensor(api_key, station, update_interval, entity_name)], True)


class MeteoFranceSensor(SensorEntity):
    """Single sensor that stores all Meteo-France fields in attributes."""

    def __init__(self, api_key: str, station: str, update_interval: int, entity_name: str):
        """Initialize the sensor."""
        self._api_key = api_key
        self._station = station
        self._update_interval = timedelta(minutes=update_interval)
        self._entity_name = entity_name

        # use HA's recommended internal attributes
        self._attr_name = entity_name
        self._attr_unique_id = f"{entity_name}_{station}"
        self._attr_should_poll = True  # entity will be polled
        self._attr_extra_state_attributes: dict[str, Any] = {}
        self._attr_native_value = None  # state

    @property
    def device_info(self):
        """Return device info for grouping in UI."""
        return {
            "identifiers": {(DOMAIN, f"{self._entity_name}_{self._station}")},
            "name": f"Ma Météo France ({self._entity_name})",
            "manufacturer": "Météo-France",
            "model": "DPObs 6min",
        }

    @property
    def native_value(self):
        """Main state is the temperature value (°C)."""
        return self._attr_native_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._attr_extra_state_attributes

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def scan_interval(self) -> timedelta:
        """Return the polling interval chosen by the user."""
        return self._update_interval

    def update(self) -> None:
        """Fetch data from Meteo-France (synchronous)."""
        try:
            params = {"id_station": self._station, "format": "json", "apikey": self._api_key}
            resp = requests.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) == 0:
                _LOGGER.error("Unexpected API response format or empty data: %s", data)
                return

            obs = data[0]

            # extract and convert values with units
            t = obs.get("t")
            t_10 = obs.get("t_10")
            t_20 = obs.get("t_20")
            t_100 = obs.get("t_100")
            ff = obs.get("ff")
            fxi10 = obs.get("fxi10")
            p = obs.get("pres")
            rg = obs.get("ray_glo01")

            # build attributes with unit metadata
            attrs: dict[str, Any] = {
                "reference_time": {"value": obs.get("reference_time"), "unit": "UTC"},
                "temperature": {"value": round((t - 273.15), 2) if t is not None else None, "unit": "°C"},
                "temperature_10cm": {"value": round((t_10 - 273.15), 2) if t_10 is not None else None, "unit": "°C"},
                "temperature_20cm": {"value": round((t_20 - 273.15), 2) if t_20 is not None else None, "unit": "°C"},
                "temperature_100cm": {"value": round((t_100 - 273.15), 2) if t_100 is not None else None, "unit": "°C"},
                "humidite": {"value": obs.get("u"), "unit": "%"},
                "pression": {"value": round((p / 100), 1) if p is not None else None, "unit": "hPa"},
                "vent_direction": {"value": obs.get("dd"), "unit": "°"},
                "vent_force": {"value": round((ff * 3.6), 1) if ff is not None else None, "unit": "km/h"},
                "rafale_direction": {"value": obs.get("dxi10"), "unit": "°"},
                "rafale_force": {"value": round((fxi10 * 3.6), 1) if fxi10 is not None else None, "unit": "km/h"},
                "precipitation": {"value": obs.get("rr_per"), "unit": "mm"},
                "puissance_solaire": {"value": round((rg / 360), 2) if rg is not None else None, "unit": "W/m²"},
                "ensoleillement": {"value": obs.get("insolh"), "unit": "min"},
                "visibilite": {"value": obs.get("vv"), "unit": "m"},
                "raw": obs,
            }

            # set main state (temperature) and attributes
            self._attr_native_value = attrs["temperature"]["value"]
            self._attr_extra_state_attributes = attrs

        except Exception as exc:  # broad-catching to avoid breaking HA
            _LOGGER.error("Error fetching Meteo-France data: %s", exc)
