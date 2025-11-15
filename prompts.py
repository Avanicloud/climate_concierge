EVALUATOR_PROMPT = """You are an evaluator scoring community climate action plans.
Score each category from 1 (poor) to 5 (excellent) and justify briefly.

Plan Summary:
{plan}

Scoring rubric:
- Feasibility: Is the plan realistic and resourced?
- Equity: Does it prioritize frontline communities?
- Climate Impact: Are emissions reductions or resilience benefits clear?
- Readiness: Are next steps and owner assignments concrete?

Respond in JSON with fields: feasibility, equity, impact, readiness, comments.
"""

