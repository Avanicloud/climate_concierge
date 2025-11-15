"""
Base agent class providing common utilities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..config import ConciergeConfig
from ..memory import LongTermMemory, SessionMemory
from ..observability.logger import log_event
from ..observability.metrics import MetricsRegistry
from ..observability.tracer import TraceRecorder


@dataclass
class AgentContext:
    session: SessionMemory
    long_term_memory: LongTermMemory
    config: ConciergeConfig
    metrics: MetricsRegistry
    tracer: TraceRecorder
    logger: Any
    llm: "LLMClient"


@dataclass
class AgentResult:
    agent: str
    payload: Dict[str, Any]
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


class BaseAgent:
    name: str = "base-agent"

    def run(self, context: AgentContext, state: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def _log(self, context: AgentContext, message: str, **kwargs) -> None:
        log_event(context.logger, f"[{self.name}] {message}", context=kwargs)
        context.tracer.record(self.name, message, kwargs)

