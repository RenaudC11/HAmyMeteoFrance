"""Ma Météo France - Custom Component (Config Flow)."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, DEFAULT_STATION, DEFAULT_UPDATE_INTERVAL

async def async_setup(hass: HomeAssistant, config) -> bool:
    """Setup minimal, no YAML support."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up mameteo from a config entry."""
    # Stocke la config pour sensor.py
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_key": entry.data.get("api_key"),
        "station": entry.data.get("station", DEFAULT_STATION),
        "update_interval": entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL),
        "entity_name": entry.data.get("entity_name", "mameteo"),
    }

    # Forward vers le sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
