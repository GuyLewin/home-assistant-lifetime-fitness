"""The lifetime-fitness integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import Api
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lifetime-fitness from a config entry."""
    username, password = entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = Api(hass, username, password)

    entry.async_on_unload(entry.add_update_listener(options_update_listener))
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
