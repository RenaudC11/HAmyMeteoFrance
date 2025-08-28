from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, CONF_API_KEY, CONF_STATION, CONF_UPDATE_INTERVAL, CONF_ENTITY_NAME

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup minimal du composant."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup via Config Flow (UI)."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_key": entry.data.get(CONF_API_KEY),
        "station": entry.data.get(CONF_STATION),
        "update_interval": entry.data.get(CONF_UPDATE_INTERVAL, 6),
        "entity_name": entry.data.get(CONF_ENTITY_NAME, "mameteo")
    }

    from homeassistant.helpers.discovery import async_load_platform
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {"entry_id": entry.entry_id}, {})
    )

    return True
