"""
Communications coach agent drafts outreach collateral and volunteer flows.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import AgentContext, AgentResult, BaseAgent
from ..tools import CalendarTool


class CommunicationsCoachAgent(BaseAgent):
    name = "communications-coach"

    def __init__(self, calendar_tool: CalendarTool):
        self.calendar_tool = calendar_tool

    def run(self, context: AgentContext, state: Dict[str, Any]) -> AgentResult:
        persona = state["persona"]
        timeline = state["timeline"]
        plan_text = state["plan_text"]
        city = persona["city"]
        events = self.calendar_tool.create_events(timeline, city)

        self._log(context, "Drafting outreach collateral", events=len(events))
        prompt = (
            "Draft two outreach artifacts for the initiative '{initiative}':\n"
            "1. A community email (<=180 words)\n"
            "2. A social media post.\n"
            "Base it on the following plan summary and timeline.\n"
            "Plan:\n{plan}\nTimeline:\n{timeline}"
        ).format(initiative=persona["initiative"], plan=plan_text, timeline=timeline)
        outreach = context.llm.generate(prompt, agent=self.name)

        payload = {
            "events": events,
            "outreach_copy": outreach,
        }
        context.long_term_memory.append_to_list(
            f"outreach::{persona['city'].lower()}::{persona['initiative'].lower()}",
            {"copy": outreach, "events": events},
        )
        return AgentResult(agent=self.name, payload=payload)

