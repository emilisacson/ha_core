"""Tests for AnovaPrecisionCooker control and monitoring."""

from unittest.mock import AsyncMock

import aiohttp
import pytest

from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.exceptions import (
    AnovaException,
    AnovaOffline,
)
from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.precission_cooker import (
    AnovaPrecisionCooker,
    AnovaPrecisionCookerBinarySensor,
    AnovaPrecisionCookerSensor,
)


@pytest.mark.asyncio
async def test_update_success() -> None:
    """Test successful update of AnovaPrecisionCooker."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", "jwt")
    # Mock response JSON
    status_json = [
        {
            "body": {
                "job": {
                    "mode": "COOK",
                    "cook-time-seconds": 3600,
                    "target-temperature": 55.5,
                    "temperature-unit": "C",
                },
                "job-status": {"state": "COOKING", "cook-time-remaining": 1800},
                "system-info": {"firmware-version": "1.2.3"},
                "temperature-info": {
                    "heater-temperature": 56.0,
                    "triac-temperature": 54.0,
                    "water-temperature": 55.0,
                },
                "pin-info": {
                    "device-safe": 1,
                    "water-leak": 1,
                    "water-level-critical": 1,
                    "water-temp-too-high": 1,
                },
            }
        }
    ]
    http_response = AsyncMock()
    http_response.json = AsyncMock(return_value=status_json)
    session.get = AsyncMock(return_value=http_response)
    result = await cooker.update()
    assert result["sensors"][AnovaPrecisionCookerSensor.COOK_TIME] == 3600
    assert result["sensors"][AnovaPrecisionCookerSensor.MODE] == "Cook"
    assert result["sensors"][AnovaPrecisionCookerSensor.STATE] == "Cooking"
    assert result["sensors"][AnovaPrecisionCookerSensor.TARGET_TEMPERATURE] == 55.5
    assert result["sensors"][AnovaPrecisionCookerSensor.FIRMWARE_VERSION] == "1.2.3"
    assert result["binary_sensors"][AnovaPrecisionCookerBinarySensor.COOKING] is True
    assert (
        result["binary_sensors"][AnovaPrecisionCookerBinarySensor.DEVICE_SAFE] is True
    )
    assert result["binary_sensors"][AnovaPrecisionCookerBinarySensor.WATER_LEAK] is True
    assert (
        result["binary_sensors"][AnovaPrecisionCookerBinarySensor.WATER_LEVEL_CRITICAL]
        is True
    )
    assert (
        result["binary_sensors"][AnovaPrecisionCookerBinarySensor.WATER_TEMP_TOO_HIGH]
        is True
    )


@pytest.mark.asyncio
async def test_update_index_error() -> None:
    """Test update method raises AnovaOffline on index error."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    http_response = AsyncMock()
    http_response.json = AsyncMock(return_value=[])
    session.get = AsyncMock(return_value=http_response)
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", "jwt")
    with pytest.raises(AnovaOffline):
        await cooker.update()


@pytest.mark.asyncio
async def test_update_connector_error() -> None:
    """Test update method raises AnovaOffline on connection error."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.get = AsyncMock(side_effect=aiohttp.ClientConnectorError(None, OSError()))
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", "jwt")
    with pytest.raises(AnovaOffline):
        await cooker.update()


@pytest.mark.asyncio
async def test_build_request_jwt_missing() -> None:
    """Test build_request raises AnovaException if JWT is missing."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", None)
    with pytest.raises(AnovaException):
        await cooker.build_request()


@pytest.mark.asyncio
async def test_build_request_success() -> None:
    """Test successful build_request method."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", "jwt")
    resp = AsyncMock()
    resp.ok = True
    resp.json = AsyncMock(
        return_value={
            "cook-time-seconds": 3600,
            "mode": "COOK",
            "target-temperature": 55.5,
            "temperature-unit": "C",
        }
    )
    session.put = AsyncMock(return_value=resp)
    await cooker.build_request(
        cook_time=3600, mode="COOK", target_temperature=55.5, temperature_unit="C"
    )
    assert cooker.cook_time == 3600
    assert cooker.mode == "COOK"
    assert cooker.target_temperature == 55.5
    assert cooker.temperature_unit == "C"


@pytest.mark.asyncio
async def test_build_request_not_ok() -> None:
    """Test build_request raises AnovaException if response is not OK."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", "jwt")
    resp = AsyncMock()
    resp.ok = False
    resp.text = AsyncMock(return_value="error")
    session.put = AsyncMock(return_value=resp)
    with pytest.raises(AnovaException):
        await cooker.build_request(cook_time=3600)


@pytest.mark.asyncio
async def test_setters_delegate() -> None:
    """Test that setter methods delegate to build_request."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    cooker = AnovaPrecisionCooker(session, "devkey", "Precision Cooker", "jwt")
    cooker.build_request = AsyncMock()
    await cooker.set_cook_time(123)
    cooker.build_request.assert_called_with(cook_time=123)
    await cooker.set_mode("COOK")
    cooker.build_request.assert_called_with(mode="COOK")
    await cooker.set_target_temperature(54.3)
    cooker.build_request.assert_called_with(target_temperature=54.3)
    await cooker.set_temperature_unit("F")
    cooker.build_request.assert_called_with(temperature_unit="F")
