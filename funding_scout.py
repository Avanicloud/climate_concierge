"""
Funding scout agent identifies suitable grants.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .base import AgentContext, AgentResult, BaseAgent
from ..tools import GrantFinderTool


class FundingScoutAgent(BaseAgent):
    name = "funding-scout"

    def __init__(self, grant_tool: GrantFinderTool):
        self.grant_tool = grant_tool

    def run(self, context: AgentContext, state: Dict[str, Any]) -> AgentResult:
        persona = state["persona"]
        initiative = persona["initiative"]
        keywords = self._extract_keywords(initiative)
        self._log(context, "Searching grants", keywords=keywords)
        grants = self.grant_tool.search(city=persona["city"], state=persona["state"], keywords=keywords)
        summary_prompt = (
            "Given the initiative '{initiative}', summarize the following grants highlighting fit:\n"
            "{grants}"
        ).format(initiative=initiative, grants=grants)
        summary = context.llm.generate(summary_prompt, agent=self.name)
        return AgentResult(
            agent=self.name,
            payload={
                "grants": grants,
                "funding_summary": summary,
            },
        )

    @staticmethod
    def _extract_keywords(initiative: str) -> List[str]:
        keywords = []
        lowered = initiative.lower()
        mapping = {
            "solar": ["solar", "renewables"],
            "tree": ["tree canopy", "cooling"],
            "bike": ["mobility", "transportation"],
            "mobility": ["mobility", "transportation"],
            "energy": ["energy efficiency", "buildings"],
        }
        for needle, tags in mapping.items():
            if needle in lowered:
                keywords.extend(tags)
        if not keywords:
            keywords.append(lowered.split()[0])
        return keywords

