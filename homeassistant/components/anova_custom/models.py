"""Dataclass models for the Anova integration."""

from dataclasses import dataclass

from .coordinator import AnovaCoordinator
from .vendor.anova_wifi_set.src.anova_wifi import AnovaPrecisionCooker


@dataclass
class AnovaData:
    """Data for the Anova integration."""

    api_jwt: str
    precision_cookers: list[AnovaPrecisionCooker]
    coordinators: list[AnovaCoordinator]
