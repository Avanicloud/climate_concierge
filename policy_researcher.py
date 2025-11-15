"""
Policy researcher agent uses civic data and LLM summarization.
"""

from __future__ import annotations

from typing import Dict, List

from .base import AgentContext, AgentResult, BaseAgent
from ..tools import CivicDataTool


class PolicyResearcherAgent(BaseAgent):
    name = "policy-researcher"

    def __init__(self, civic_tool: CivicDataTool):
        self.civic_tool = civic_tool

    def run(self, context: AgentContext, state: Dict[str, Any]) -> AgentResult:
        persona = state["persona"]
        city = persona["city"]
        state_code = persona["state"]
        self._log(context, "Fetching civic data", city=city, state=state_code)
        profile = self.civic_tool.city_profile(city, state_code)

        metrics_text = "\n".join(
            f"- {m['sector'].title()} {m['metric'].replace('_', ' ')}: {m['value']} {m['unit']} ({m['year']})"
            for m in profile.get("metrics", [])
        )
        prompt = (
            "Summarize the following civic climate metrics and suggest two policy considerations.\n"
            f"{metrics_text or 'No local metrics available.'}\n"
            f"Community notes: {persona['community_profile']}"
        )
        summary = context.llm.generate(prompt, agent=self.name)
        recommendations = self._extract_recommendations(summary)

        payload = {
            "civic_profile": profile,
            "policy_summary": summary,
            "policy_recommendations": recommendations,
        }
        return AgentResult(agent=self.name, payload=payload)

    @staticmethod
    def _extract_recommendations(summary: str) -> List[str]:
        bullet_points = []
        for line in summary.splitlines():
            if line.strip().startswith("-"):
                bullet_points.append(line.strip("- ").strip())
        if not bullet_points:
            bullet_points = [summary]
        return bullet_points[:3]

