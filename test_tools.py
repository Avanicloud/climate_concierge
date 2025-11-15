from pathlib import Path

from projects.climate_concierge.src.tools import CivicDataTool, GrantFinderTool, ImpactSimulatorTool


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_civic_data_tool_returns_metrics():
    tool = CivicDataTool(DATA_DIR / "city_emissions_sample.csv")
    profile = tool.city_profile("Oakland", "CA")
    assert profile["city"] == "Oakland"
    assert profile["metrics"], "Expected metrics for Oakland"


def test_grant_finder_matches_keywords():
    tool = GrantFinderTool(DATA_DIR / "grants_catalog_sample.json")
    results = tool.search(city="Oakland", state="CA", keywords=["solar"])
    assert results, "Should find at least one solar grant"
    assert any("solar" in g["title"].lower() for g in results)


def test_impact_simulator_scale_adjustment():
    tool = ImpactSimulatorTool()
    small = tool.estimate("solar rooftop", "small")
    large = tool.estimate("solar rooftop", "large")
    assert large["co2_reduction_tonnes"] > small["co2_reduction_tonnes"]

