"""
Configuration utilities for the Community Climate Action Concierge.

Handles environment variable parsing, default paths, and model selection.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RUN_ARTIFACTS_DIR = PROJECT_ROOT / "run_artifacts"
RUN_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
(RUN_ARTIFACTS_DIR / "logs").mkdir(exist_ok=True)
(RUN_ARTIFACTS_DIR / "metrics").mkdir(exist_ok=True)
(RUN_ARTIFACTS_DIR / "plans").mkdir(exist_ok=True)


@dataclass(slots=True)
class ModelConfig:
    """Settings that describe the LLMs used by the agents."""

    model_name: str = "models/gemini-1.5-flash"
    temperature: float = 0.2
    max_output_tokens: int = 2048


@dataclass(slots=True)
class ObservabilityConfig:
    """Paths and toggles for logging, tracing, and metrics."""

    logs_path: Path = RUN_ARTIFACTS_DIR / "logs"
    traces_path: Path = RUN_ARTIFACTS_DIR / "logs" / "traces.jsonl"
    metrics_path: Path = RUN_ARTIFACTS_DIR / "metrics" / "latest.prom"
    enable_console_logs: bool = True
    log_level: str = "INFO"


@dataclass(slots=True)
class MemoryConfig:
    """Configuration for session and long-term memory persistence."""

    long_term_path: Path = RUN_ARTIFACTS_DIR / "memory_bank.json"
    session_ttl_minutes: int = 1440  # 24h default


@dataclass(slots=True)
class ToolConfig:
    """Configuration for tool integrations."""

    civic_data_path: Path = DATA_DIR / "city_emissions_sample.csv"
    grant_catalog_path: Path = DATA_DIR / "grants_catalog_sample.json"
    google_search_api_key: Optional[str] = None
    use_live_search: bool = False


@dataclass(slots=True)
class ConciergeConfig:
    """Aggregate configuration object shared across the orchestrator."""

    model: ModelConfig = ModelConfig()
    observability: ObservabilityConfig = ObservabilityConfig()
    memory: MemoryConfig = MemoryConfig()
    tools: ToolConfig = ToolConfig()
    allow_stub_llm: bool = False

    @property
    def gemini_api_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY")

    @property
    def run_id(self) -> str:
        return os.getenv("CONCIERGE_RUN_ID", "")


def load_config() -> ConciergeConfig:
    """Factory to produce a fully-populated configuration instance."""
    model = ModelConfig(
        model_name=os.getenv("GEMINI_MODEL_NAME", ModelConfig.model_name),
        temperature=float(os.getenv("GEMINI_TEMPERATURE", ModelConfig.temperature)),
        max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", ModelConfig.max_output_tokens)),
    )
    observability = ObservabilityConfig(
        logs_path=Path(os.getenv("CONCIERGE_LOGS_PATH", str(ObservabilityConfig.logs_path))),
        traces_path=Path(os.getenv("CONCIERGE_TRACES_PATH", str(ObservabilityConfig.traces_path))),
        metrics_path=Path(os.getenv("CONCIERGE_METRICS_PATH", str(ObservabilityConfig.metrics_path))),
        enable_console_logs=os.getenv("ENABLE_CONSOLE_LOGS", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", ObservabilityConfig.log_level),
    )
    memory = MemoryConfig(
        long_term_path=Path(os.getenv("CONCIERGE_MEMORY_PATH", str(MemoryConfig.long_term_path))),
        session_ttl_minutes=int(os.getenv("SESSION_TTL_MINUTES", MemoryConfig.session_ttl_minutes)),
    )
    tools = ToolConfig(
        civic_data_path=Path(os.getenv("CIVIC_DATA_PATH", str(ToolConfig.civic_data_path))),
        grant_catalog_path=Path(os.getenv("GRANT_CATALOG_PATH", str(ToolConfig.grant_catalog_path))),
        google_search_api_key=os.getenv("GOOGLE_API_KEY"),
        use_live_search=os.getenv("ENABLE_LIVE_SEARCH", "false").lower() == "true",
    )
    cfg = ConciergeConfig(
        model=model,
        observability=observability,
        memory=memory,
        tools=tools,
        allow_stub_llm=os.getenv("ALLOW_STUB_LLM", "false").lower() == "true",
    )
    if not cfg.gemini_api_key and not cfg.allow_stub_llm:
        raise EnvironmentError(
            "GEMINI_API_KEY must be set to run the Concierge. "
            "Set ALLOW_STUB_LLM=true to use the offline rule-based fallback."
        )
    return cfg

