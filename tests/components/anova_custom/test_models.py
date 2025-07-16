"""Tests for Anova Custom models."""

from unittest.mock import MagicMock

from homeassistant.components.anova_custom.coordinator import AnovaCoordinator
from homeassistant.components.anova_custom.models import AnovaData
from homeassistant.components.anova_custom.vendor.anova_wifi_set.src.anova_wifi.precission_cooker import (
    AnovaPrecisionCooker,
)


def test_anova_data_model() -> None:
    """Test AnovaData dataclass instantiation and attributes."""
    session = MagicMock()
    cooker = AnovaPrecisionCooker(session, "device_key", "type", "jwt-token")
    coordinator = AnovaCoordinator(None, cooker, None)
    data = AnovaData(
        api_jwt="jwt-token", precision_cookers=[cooker], coordinators=[coordinator]
    )
    assert data.api_jwt == "jwt-token"
    assert data.precision_cookers == [cooker]
    assert data.coordinators == [coordinator]
    session.close()
