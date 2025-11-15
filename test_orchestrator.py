import os

from projects.climate_concierge.src.config import load_config
from projects.climate_concierge.src.orchestrator import ClimateConciergeOrchestrator


def test_orchestrator_stub_run(monkeypatch, tmp_path):
    monkeypatch.setenv("ALLOW_STUB_LLM", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "")

    config = load_config()
    # Override run artifacts to temporary directory during test
    monkeypatch.setattr(config.observability, "logs_path", tmp_path / "logs")
    monkeypatch.setattr(config.observability, "metrics_path", tmp_path / "metrics.prom")
    monkeypatch.setattr(config.observability, "traces_path", tmp_path / "traces.jsonl")
    monkeypatch.setattr(config.memory, "long_term_path", tmp_path / "memory.json")

    orchestrator = ClimateConciergeOrchestrator(config)
    result = orchestrator.run(
        organizer="Test Org",
        city="Oakland",
        state="CA",
        initiative="Solarize the community center roof",
        scale="Pilot",
        community_profile="Frontline neighborhood with high energy burden.",
    )

    assert result.plan["impact"]["co2_reduction_tonnes"] > 0
    assert result.plan["grants"], "Expected at least one grant"
    assert result.plan["average_score"] >= 0
    assert result.artifact_path.exists()

