"""Tests for AnovaApi authentication and device discovery logic."""

import sys
import time as real_time
from unittest.mock import AsyncMock

import aiohttp
import pytest

from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.exceptions import (
    InvalidLogin,
    NoDevicesFound,
)
from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.parser import (
    AnovaApi,
)
from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.precission_cooker import (
    AnovaPrecisionCooker,
)


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    """Test successful authentication with Firebase and Anova API."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    # Patch session.post to be awaitable and return correct responses
    firebase_response = AsyncMock()
    firebase_response.json = AsyncMock(return_value={"idToken": "fake_token"})
    anova_response = AsyncMock()
    anova_response.json = AsyncMock(return_value={"jwt": "fake_jwt"})
    session.post = AsyncMock(side_effect=[firebase_response, anova_response])
    api = AnovaApi(session, "user", "pass")
    result = await api.authenticate()
    assert result is True
    assert getattr(api, "_firebase_jwt", None) == "fake_token"
    assert api.jwt == "fake_jwt"


@pytest.mark.asyncio
async def test_authenticate_invalid_login() -> None:
    """Test authentication failure with invalid Firebase credentials."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    firebase_response = AsyncMock()
    firebase_response.json = AsyncMock(return_value={})
    session.post = AsyncMock(return_value=firebase_response)
    api = AnovaApi(session, "user", "pass")
    with pytest.raises(InvalidLogin):
        await api.authenticate()


@pytest.mark.asyncio
async def test_get_devices_no_devices() -> None:
    """Test get_devices raises NoDevicesFound when no devices returned."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    api = AnovaApi(session, "user", "pass")
    api._firebase_jwt = "fake_token"
    api.jwt = "fake_jwt"
    response = AsyncMock()
    response.json = AsyncMock(return_value={"devices": []})
    session.get = AsyncMock(return_value=response)
    # Patch websocket receive chain
    ws_mock = AsyncMock()
    msg_mock = AsyncMock()
    msg_mock.data = '{"devices": []}'
    ws_mock.receive.return_value = msg_mock

    # Properly mock async context manager for ws_connect
    class _WS:
        async def __aenter__(self):
            return ws_mock

        async def __aexit__(self, exc_type, exc, tb):
            return None

    session.ws_connect = lambda *a, **kw: _WS()
    with pytest.raises(NoDevicesFound):
        await api.get_devices()


@pytest.mark.asyncio
async def test_get_devices_success() -> None:
    """Test get_devices returns AnovaPrecisionCooker instance for valid device."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    api = AnovaApi(session, "user", "pass")
    api._firebase_jwt = "fake_token"
    api.jwt = "fake_jwt"
    response = AsyncMock()
    response.json = AsyncMock(
        return_value={"devices": [{"key": "dev1", "type": "Precision Cooker"}]}
    )
    session.get = AsyncMock(return_value=response)
    # Patch websocket receive chain
    ws_mock = AsyncMock()
    msg_discovery = AsyncMock()
    msg_discovery.data = '{"command": "EVENT_APC_WIFI_VERSION", "payload": [{"cookerId": "dev1", "type": "Precision Cooker"}]}'
    ws_mock.receive = AsyncMock(side_effect=[msg_discovery, TimeoutError()])

    # Properly mock async context manager for ws_connect
    class _WS:
        async def __aenter__(self):
            return ws_mock

        async def __aexit__(self, exc_type, exc, tb):
            return None

    session.ws_connect = lambda *a, **kw: _WS()

    # Patch time.time so the loop exits after one iteration
    orig_time = real_time.time
    times = [orig_time(), orig_time() + 1, orig_time() + 10]

    def fake_time():
        return times.pop(0) if times else orig_time() + 10

    sys.modules["time"].time = fake_time

    devices = await api.get_devices()

    # Restore time.time
    sys.modules["time"].time = orig_time

    assert isinstance(devices[0], AnovaPrecisionCooker)
    assert devices[0].device_key == "dev1"
    assert devices[0].type == "Precision Cooker"
