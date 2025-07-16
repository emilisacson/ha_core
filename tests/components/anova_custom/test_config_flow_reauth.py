"""Test AnovaCustom config flow reauth step."""

from unittest.mock import patch

import pytest

from homeassistant.components.anova_custom.config_flow import CannotConnect, InvalidAuth
from homeassistant.components.anova_custom.const import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry


@pytest.mark.asyncio
async def test_reauth_success(hass: HomeAssistant) -> None:
    """Test successful reauth step."""

    with (
        patch(
            "homeassistant.components.anova_custom.config_flow.AnovaApi.authenticate",
            return_value=True,
        ),
        patch(
            "homeassistant.components.anova_custom.config_flow.AnovaApi.get_devices",
            return_value=[],
        ),
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_USERNAME: "test-user",
                CONF_PASSWORD: "test-pass",
                "jwt": "old-jwt",
                "devices": [],
            },
            unique_id="test-user",
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        flow = hass.config_entries.flow
        result = await flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
            data={CONF_USERNAME: "test-user", CONF_PASSWORD: "test-pass"},
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "reauth_successful"


@pytest.mark.asyncio
async def test_reauth_invalid_auth(hass: HomeAssistant) -> None:
    """Test reauth step with invalid auth error."""

    with (
        patch(
            "homeassistant.components.anova_custom.config_flow.AnovaApi.authenticate",
            side_effect=InvalidAuth,
        ),
        patch(
            "homeassistant.components.anova_custom.config_flow.AnovaApi.get_devices",
            return_value=[],
        ),
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_USERNAME: "test-user",
                CONF_PASSWORD: "test-pass",
                "jwt": "old-jwt",
                "devices": [],
            },
            unique_id="test-user",
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        flow = hass.config_entries.flow
        result = await flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
            data={CONF_USERNAME: "test-user", CONF_PASSWORD: "test-pass"},
        )
        result2 = await flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "test-user", CONF_PASSWORD: "bad-pass"},
        )
        assert result2["type"] == FlowResultType.FORM
        assert result2["errors"]["base"] == "invalid_auth"


@pytest.mark.asyncio
async def test_reauth_cannot_connect(hass: HomeAssistant) -> None:
    """Test reauth step with cannot connect error."""

    with (
        patch(
            "homeassistant.components.anova_custom.config_flow.AnovaApi.authenticate",
            side_effect=CannotConnect,
        ),
        patch(
            "homeassistant.components.anova_custom.config_flow.AnovaApi.get_devices",
            return_value=[],
        ),
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_USERNAME: "test-user",
                CONF_PASSWORD: "test-pass",
                "jwt": "old-jwt",
                "devices": [],
            },
            unique_id="test-user",
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        flow = hass.config_entries.flow
        result = await flow.async_init(
            DOMAIN,
            context={"source": "reauth", "entry_id": entry.entry_id},
            data={CONF_USERNAME: "test-user", CONF_PASSWORD: "test-pass"},
        )
        result2 = await flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "test-user", CONF_PASSWORD: "bad-pass"},
        )
        assert result2["type"] == FlowResultType.FORM
        assert result2["errors"]["base"] == "cannot_connect"
