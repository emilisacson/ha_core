"""Config flow for Anova."""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN
from .vendor.anova_wifi_set.src.anova_wifi import (
    AnovaApi,
    AnovaOffline as CannotConnect,
    InvalidLogin as InvalidAuth,
    NoDevicesFound,
)


class AnovaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Anova Sous Vide integration."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user.

        Args:
            user_input: Optional dictionary of user input values.

        Returns:
            ConfigFlowResult: The result of the config flow step.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            api = AnovaApi(
                aiohttp_client.async_get_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()
            try:
                await api.authenticate()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            # Only catch known exceptions; let others propagate for visibility
            else:
                try:
                    devices = await api.get_devices()
                    device_list = [
                        (device.device_key, device.type) for device in devices
                    ]
                    return self.async_create_entry(
                        title="Anova Sous Vide",
                        data={"jwt": api.jwt, "devices": device_list},
                    )
                except NoDevicesFound:
                    errors["base"] = "no_devices_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, user_input: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication if credentials expire or change.

        Args:
            user_input: Optional mapping of user input values.

        Returns:
            ConfigFlowResult: The result of the reauthentication step.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            api = AnovaApi(
                aiohttp_client.async_get_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            try:
                await api.authenticate()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            # Only catch known exceptions; let others propagate for visibility
            else:
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth",
            data_schema=vol.Schema(
                {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=errors,
        )
