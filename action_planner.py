"""
Action planner agent composes implementation roadmap combining insights.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import AgentContext, AgentResult, BaseAgent
from ..tools import ImpactSimulatorTool, TimelineBuilderTool


class ActionPlannerAgent(BaseAgent):
    name = "action-planner"

    def __init__(self, impact_tool: ImpactSimulatorTool, timeline_tool: TimelineBuilderTool):
        self.impact_tool = impact_tool
        self.timeline_tool = timeline_tool

    def run(self, context: AgentContext, state: Dict[str, Any]) -> AgentResult:
        persona = state["persona"]
        policy_summary = state.get("policy_summary")
        grants = state.get("grants", [])
        funding_summary = state.get("funding_summary")

        self._log(context, "Composing implementation plan", initiative=persona["initiative"])
        impact = self.impact_tool.estimate(persona["initiative"], persona["scale"])
        timeline = self.timeline_tool.build(persona["initiative"])

        prompt = (
            "Create a concise implementation plan based on the following inputs:\n"
            f"Initiative: {persona['initiative']}\n"
            f"Policy Summary: {policy_summary}\n"
            f"Grants: {grants}\n"
            f"Funding Summary: {funding_summary}\n"
            f"Impact Estimate: {impact}\n"
            f"Timeline: {timeline}\n"
            "Structure the output with sections for Goals, Key Workstreams, Risks, and Metrics."
        )
        plan_text = context.llm.generate(prompt, agent=self.name)

        payload = {
            "impact": impact,
            "timeline": timeline,
            "plan_text": plan_text,
        }
        return AgentResult(agent=self.name, payload=payload)

