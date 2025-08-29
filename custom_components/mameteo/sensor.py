from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import requests
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_STATION_ID,
    CONF_ENTITY_NAME,
    CONF_MODE,
    CONF_UPDATE_MINUTES,
    MODE_SINGLE,
    MODE_SPLIT,
    SENSOR_SPECS,
)

_LOGGER = logging.getLogger(__name__)

API_URL = "https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m"

def _convert_value(key: str, value: Any) -> Any:
    """Convert raw API values to display units."""
    if value is None:
        return None
    try:
        # Températures K -> °C
        if key in ("t", "td", "t_10", "t_20", "t_50", "t_100", "tx", "tn"):
            return round(float(value) - 273.15, 2)
        # Vent m/s -> km/h
        if key in ("ff", "fxi", "fxy"):
            return round(float(value) * 3.6, 1)
        # Pression Pa -> hPa
        if key in ("pres", "pmer"):
            return round(float(value) / 100.0, 1)
        # Rayonnement J/m² (6 min) -> W/m²
        if key == "ray_glo01":
            return round(float(value) / 360.0, 2)
        # Précipitations, directions, visibilité, ensoleillement: brut
        return value
    except Exception as err:
        _LOGGER.debug("Conversion error for %s: %s (raw=%s)", key, err, value)
        return value


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    api_key: str = data[CONF_API_KEY]
    station_id: str = data[CONF_STATION_ID]
    base_name: str = data.get(CONF_ENTITY_NAME)
    mode: str = data.get(CONF_MODE, MODE_SINGLE)
    minutes: int = data.get(CONF_UPDATE_MINUTES, 6)

    async def _async_fetch():
        """Do the HTTP GET in executor (requests is blocking)."""
        def _do():
            params = {
                "id_station": station_id,
                "format": "json",
                "apikey": api_key,  # l'API MF accepte la clé en query string
            }
            r = requests.get(API_URL, params=params, timeout=15)
            r.raise_for_status()
            js = r.json()
            # L'endpoint retourne une liste; on prend le 1er élément
            if isinstance(js, list) and js:
                return js[0]
            # Ou un dict avec "obs"
            if isinstance(js, dict) and "obs" in js and isinstance(js["obs"], list) and js["obs"]:
                return js["obs"][0]
            return {}
        return await hass.async_add_executor_job(_do)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_method=_async_fetch,
        update_interval=timedelta(minutes=minutes),
    )

    await coordinator.async_config_entry_first_refresh()

    if mode == MODE_SINGLE:
        # Capteur unique: valeur = température, device_class/units pour température
        entity = MameteoSingleEntity(coordinator, entry.entry_id, base_name, station_id)
        async_add_entities([entity], True)
    else:
        # Un capteur par mesure
        entities = []
        for key, spec in SENSOR_SPECS.items():
            entities.append(MameteoSplitEntity(coordinator, entry.entry_id, base_name, station_id, key, spec))
        async_add_entities(entities, True)


class _MameteoBase(CoordinatorEntity, SensorEntity):
    """Base commune: device info + utilitaires."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, base_name: str, station_id: str):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._base_name = base_name
        self._station_id = station_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry_id}_{self._station_id}")},
            name=f"{self._base_name} ({self._station_id})",
            manufacturer="Météo-France",
            model="DPObs v1 - infrahoraire 6m",
        )


class MameteoSingleEntity(_MameteoBase):
    """Un seul capteur : valeur de type température (°C), autres valeurs en attributs."""

    _attr_device_class = "temperature"
    _attr_native_unit_of_measurement = "°C"
    _attr_state_class = "measurement"

    def __init__(self, coordinator, entry_id, base_name, station_id):
        super().__init__(coordinator, entry_id, base_name, station_id)
        self._attr_name = base_name
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_single"

    @property
    def native_value(self):
        obs = self.coordinator.data or {}
        return _convert_value("t", obs.get("t"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        obs = self.coordinator.data or {}
        attrs: dict[str, Any] = {}
        # toutes les clés connues converties
        for key, spec in SENSOR_SPECS.items():
            attrs[key] = _convert_value(key, obs.get(key))
        # informations utiles supplémentaires
        if "reference_time" in obs:
            attrs["reference_time"] = obs.get("reference_time")  # UTC ISO
        attrs["_raw"] = obs  # brut pour debug
        return attrs


class MameteoSplitEntity(_MameteoBase):
    """Un capteur par mesure, avec unit/device_class/state_class adaptés."""

    def __init__(self, coordinator, entry_id, base_name, station_id, key: str, spec: dict):
        super().__init__(coordinator, entry_id, base_name, station_id)
        self._key = key
        self._spec = spec
        self._attr_name = f"{base_name} {spec['name']}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"
        self._attr_native_unit_of_measurement = spec["unit"]
        self._attr_device_class = spec["device_class"]
        self._attr_state_class = spec["state_class"]

    @property
    def native_value(self):
        obs = self.coordinator.data or {}
        return _convert_value(self._key, obs.get(self._key))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        obs = self.coordinator.data or {}
        out = {}
        if "reference_time" in obs:
            out["reference_time"] = obs.get("reference_time")
        # valeur brute non convertie (pour debug)
        out["raw"] = obs.get(self._key)
        return out
