"""
Orchestrates the Community Climate Action Concierge pipeline.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .agents import (
    ActionPlannerAgent,
    AgentContext,
    AgentResult,
    CommunicationsCoachAgent,
    CommunityLiaisonAgent,
    FundingScoutAgent,
    PolicyResearcherAgent,
)
from .config import ConciergeConfig, DATA_DIR, load_config
from .evaluation import EvaluatorAgent
from .memory import LongTermMemory, SessionStore
from .observability.logger import get_logger, log_event
from .observability.metrics import MetricsRegistry
from .observability.tracer import TraceRecorder
from .tools import (
    CalendarTool,
    CivicDataTool,
    GrantFinderTool,
    ImpactSimulatorTool,
    TimelineBuilderTool,
)


class LLMClient:
    """
    Thin adapter for Gemini or stubbed LLM responses.
    """

    def __init__(self, config: ConciergeConfig, logger) -> None:
        self.config = config
        self.logger = logger
        self._client = None
        if config.gemini_api_key:
            try:
                import google.generativeai as genai  # type: ignore

                genai.configure(api_key=config.gemini_api_key)
                self._client = genai.GenerativeModel(config.model.model_name)
            except Exception as exc:  # pragma: no cover - best effort
                log_event(
                    logger,
                    "Falling back to stub LLM due to Gemini init failure",
                    level="warning",
                    context={"error": str(exc)},
                )
                self._client = None
        elif not config.allow_stub_llm:
            raise EnvironmentError(
                "No LLM available. Set GEMINI_API_KEY or ALLOW_STUB_LLM=true."
            )

    def generate(self, prompt: str, *, agent: str) -> str:
        if self._client:
            try:
                response = self._client.generate_content(prompt, safety_settings=None)
                return response.text if hasattr(response, "text") else str(response)
            except Exception as exc:  # pragma: no cover
                log_event(
                    self.logger,
                    "Gemini generation failed; falling back to stub",
                    level="warning",
                    context={"error": str(exc), "agent": agent},
                )
        return self._stub_response(prompt, agent)

    def _stub_response(self, prompt: str, agent: str) -> str:
        # Simple deterministic heuristics
        if agent == "policy-researcher":
            return (
                "Policy insights:\n"
                "- Prioritize frontline neighborhoods impacted by energy burden.\n"
                "- Coordinate with city sustainability office for streamlined permits."
            )
        if agent == "funding-scout":
            return (
                "Top grants:\n"
                "- Community Solar Acceleration Microgrant is a strong fit (low match).\n"
                "- Urban Heat Island Fund supports cooling co-benefits."
            )
        if agent == "action-planner":
            return (
                "Goals:\n"
                "- Install rooftop solar to offset 25 tonnes CO₂ annually.\n"
                "Workstreams: Site prep, contractor selection, community outreach.\n"
                "Risks: Permitting delays, volunteer capacity.\n"
                "Metrics: kWh generated, households served."
            )
        if agent == "communications-coach":
            return (
                "Email:\n"
                "Neighbors,\n"
                "Join us to solarize the community center!\n"
                "\n"
                "Social post:\n"
                "#Oakland is going solar ☀️ Volunteer sign-up link coming soon!"
            )
        if agent == "plan-evaluator":
            return json.dumps(
                {
                    "feasibility": 4,
                    "equity": 4,
                    "impact": 5,
                    "readiness": 4,
                    "comments": "Strong alignment with community goals.",
                }
            )
        return "Summary not available in stub mode."


@dataclass
class ConciergeResult:
    run_id: str
    plan: Dict
    artifact_path: Path


class ClimateConciergeOrchestrator:
    def __init__(self, config: Optional[ConciergeConfig] = None) -> None:
        self.config = config or load_config()
        self.logger = get_logger(
            "climate-concierge",
            log_path=self.config.observability.logs_path / "concierge.log",
            enable_console=self.config.observability.enable_console_logs,
            level=self.config.observability.log_level,
        )
        self.metrics = MetricsRegistry(self.config.observability.metrics_path)
        self.tracer = TraceRecorder(self.config.observability.traces_path)
        self.session_store = SessionStore(self.config.memory.session_ttl_minutes)
        self.long_term_memory = LongTermMemory(self.config.memory.long_term_path)
        self.llm_client = LLMClient(self.config, self.logger)
        self._init_agents()

    def _init_agents(self) -> None:
        data_dir = DATA_DIR
        civic_path = self.config.tools.civic_data_path
        if not civic_path.exists():
            civic_path = data_dir / "city_emissions_sample.csv"
        grant_path = self.config.tools.grant_catalog_path
        if not grant_path.exists():
            grant_path = data_dir / "grants_catalog_sample.json"

        self.civic_tool = CivicDataTool(civic_path)
        self.grant_tool = GrantFinderTool(grant_path)
        self.impact_tool = ImpactSimulatorTool()
        self.timeline_tool = TimelineBuilderTool()
        self.calendar_tool = CalendarTool()

        self.agents = {
            "liaison": CommunityLiaisonAgent(),
            "policy": PolicyResearcherAgent(self.civic_tool),
            "funding": FundingScoutAgent(self.grant_tool),
            "planner": ActionPlannerAgent(self.impact_tool, self.timeline_tool),
            "comms": CommunicationsCoachAgent(self.calendar_tool),
            "evaluator": EvaluatorAgent(),
        }

    def run(
        self,
        *,
        organizer: str,
        city: str,
        state: str,
        initiative: str,
        scale: str,
        community_profile: str,
        session_id: Optional[str] = None,
    ) -> ConciergeResult:
        run_id = uuid.uuid4().hex[:12]
        session = self.session_store.get_session(session_id or run_id)
        ctx = AgentContext(
            session=session,
            long_term_memory=self.long_term_memory,
            config=self.config,
            metrics=self.metrics,
            tracer=self.tracer,
            logger=self.logger,
            llm=self.llm_client,
        )
        state: Dict[str, Dict] = {
            "organizer": organizer,
            "city": city,
            "state": state,
            "initiative": initiative,
            "scale": scale,
            "community_profile": community_profile,
        }
        plan_state: Dict[str, Dict] = {}

        def update_state(result: AgentResult) -> None:
            plan_state.update(result.payload)
            self.metrics.counter("agent_runs_total", "Number of agent runs").inc()

        log_event(self.logger, "Starting concierge run", context={"run_id": run_id})

        update_state(self.agents["liaison"].run(ctx, state))
        state.update(plan_state)
        update_state(self.agents["policy"].run(ctx, state))
        state.update(plan_state)
        update_state(self.agents["funding"].run(ctx, state))
        state.update(plan_state)
        update_state(self.agents["planner"].run(ctx, state))
        state.update(plan_state)
        update_state(self.agents["comms"].run(ctx, state))
        state.update(plan_state)
        update_state(self.agents["evaluator"].run(ctx, state))

        self.metrics.emit()
        self.tracer.flush()

        artifact_path = self._persist_plan(run_id, plan_state)
        return ConciergeResult(run_id=run_id, plan=plan_state, artifact_path=artifact_path)

    def _persist_plan(self, run_id: str, plan: Dict) -> Path:
        path = self.config.observability.logs_path.parent / "plans" / f"{run_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

