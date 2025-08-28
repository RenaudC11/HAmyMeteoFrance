"""Ma Météo France - Custom Component (UI config entries)."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_API_KEY, CONF_STATION, CONF_UPDATE_INTERVAL, CONF_ENTITY_NAME, DEFAULT_UPDATE_INTERVAL, DEFAULT_ENTITY_NAME

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Minimal setup for mameteo component."""
    # No YAML setup required – config via UI (Config Flow)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up mameteo from a config entry created in the UI."""
    hass.data.setdefault(DOMAIN, {})

    # Save config data for sensor setup
    hass.data[DOMAIN][entry.entry_id] = {
        "api_key": entry.data.get(CONF_API_KEY),
        "station": entry.data.get(CONF_STATION, DEFAULT_STATION),
        "update_interval": entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        "entity_name": entry.data.get(CONF_ENTITY_NAME, DEFAULT_ENTITY_NAME),
    }

    # Forward setup to sensor platform
    from homeassistant.helpers.discovery import async_load_platform
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {"entry_id": entry.entry_id}, {})
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
