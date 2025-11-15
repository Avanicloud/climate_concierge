"""
Evaluator agent producing rubric-based scores using LLM or heuristics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

from ..agents.base import AgentContext, AgentResult, BaseAgent
from .prompts import EVALUATOR_PROMPT


@dataclass
class EvaluationScores:
    feasibility: int
    equity: int
    impact: int
    readiness: int
    comments: str

    @property
    def average(self) -> float:
        return (self.feasibility + self.equity + self.impact + self.readiness) / 4.0


class EvaluatorAgent(BaseAgent):
    name = "plan-evaluator"

    def run(self, context: AgentContext, state: Dict[str, Dict]) -> AgentResult:
        plan_text = state["plan_text"]
        self._log(context, "Scoring plan against rubric")
        prompt = EVALUATOR_PROMPT.format(plan=plan_text)
        raw = context.llm.generate(prompt, agent=self.name)
        scores = self._parse_scores(raw)
        context.long_term_memory.append_to_list(
            "evaluations",
            {
                "plan_text": plan_text[:5000],
                "scores": scores.__dict__,
            },
        )
        return AgentResult(
            agent=self.name,
            payload={
                "scores": scores.__dict__,
                "average_score": round(scores.average, 2),
                "raw_response": raw,
            },
        )

    @staticmethod
    def _parse_scores(raw: str) -> EvaluationScores:
        try:
            data = json.loads(raw)
            return EvaluationScores(
                feasibility=int(data.get("feasibility", 3)),
                equity=int(data.get("equity", 3)),
                impact=int(data.get("impact", 3)),
                readiness=int(data.get("readiness", 3)),
                comments=str(data.get("comments", "")),
            )
        except json.JSONDecodeError:
            return EvaluationScores(feasibility=3, equity=3, impact=3, readiness=3, comments=raw[:200])

