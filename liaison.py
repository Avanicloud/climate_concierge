"""
Community Liaison agent: gathers organizer intent and personas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from .base import AgentContext, AgentResult, BaseAgent


@dataclass
class LiaisonInput:
    organizer: str
    city: str
    state: str
    initiative: str
    scale: str
    community_profile: str


class CommunityLiaisonAgent(BaseAgent):
    name = "community-liaison"

    def run(self, context: AgentContext, state: Dict[str, Any]) -> AgentResult:
        self._log(context, "Collecting organizer intent", state=state)

        liaison_input = LiaisonInput(**state)
        description = (
            f"{liaison_input.organizer} is planning a {liaison_input.scale.lower()} initiative "
            f"in {liaison_input.city}, {liaison_input.state}: {liaison_input.initiative}."
            f" Community notes: {liaison_input.community_profile}"
        )
        context.session.set("organizer_summary", description)
        context.session.append_conversation("organizer", description)

        persona = {
            "lead": liaison_input.organizer,
            "city": liaison_input.city,
            "state": liaison_input.state,
            "initiative": liaison_input.initiative,
            "scale": liaison_input.scale,
            "community_profile": liaison_input.community_profile,
        }
        context.long_term_memory.set(
            f"profile::{liaison_input.city.lower()}::{liaison_input.organizer.lower()}",
            persona,
        )

        return AgentResult(agent=self.name, payload={"persona": persona})

