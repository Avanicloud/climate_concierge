"""
Rudimentary impact simulator providing emissions and equity estimations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ImpactScenario:
    co2_reduction_tonnes: float
    households_benefiting: int
    equity_score: str
    assumptions: str


class ImpactSimulatorTool:
    def estimate(self, initiative: str, scale: str) -> Dict:
        initiative_lower = initiative.lower()
        if "solar" in initiative_lower:
            base = ImpactScenario(
                co2_reduction_tonnes=25.0,
                households_benefiting=120,
                equity_score="High",
                assumptions="3,000 sqft rooftop solar array; offsets ~25 tonnes CO₂ annually.",
            )
        elif "tree" in initiative_lower or "canopy" in initiative_lower:
            base = ImpactScenario(
                co2_reduction_tonnes=8.0,
                households_benefiting=200,
                equity_score="Medium",
                assumptions="50 shade trees planted; offsets ~8 tonnes CO₂ and reduces heat island effect.",
            )
        elif "mobility" in initiative_lower or "bike" in initiative_lower:
            base = ImpactScenario(
                co2_reduction_tonnes=15.0,
                households_benefiting=300,
                equity_score="High",
                assumptions="E-bike lending library serving 300 residents.",
            )
        else:
            base = ImpactScenario(
                co2_reduction_tonnes=10.0,
                households_benefiting=150,
                equity_score="Medium",
                assumptions="General community climate initiative baseline.",
            )

        scale_multiplier = 1.0
        if scale.lower() in {"large", "regional"}:
            scale_multiplier = 2.5
        elif scale.lower() in {"medium"}:
            scale_multiplier = 1.5
        elif scale.lower() in {"pilot", "small"}:
            scale_multiplier = 0.75

        return {
            "co2_reduction_tonnes": round(base.co2_reduction_tonnes * scale_multiplier, 2),
            "households_benefiting": int(base.households_benefiting * scale_multiplier),
            "equity_score": base.equity_score,
            "assumptions": base.assumptions,
        }

