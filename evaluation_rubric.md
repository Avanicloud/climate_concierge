# Evaluation Rubric

This rubric guides the Evaluator Agent and human reviewers when assessing generated climate action plans.

| Category     | Weight | Description                                                                                  | Example Questions                                                                 |
|--------------|--------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Feasibility  | 25%    | Are resources, sequencing, and stakeholders realistic for the stated scope and timeline?     | Are permitting steps included? Are staffing/volunteer needs matched to capacity? |
| Equity       | 25%    | Does the plan prioritize frontline communities, co-design, and accessibility?                | Are benefits distributed fairly? Are language/access accommodations included?    |
| Impact       | 30%    | Are emissions reductions, resilience gains, or co-benefits quantified or clearly articulated?| Are metrics tied to initiative goals? Are assumptions documented?               |
| Readiness    | 20%    | Are next actions, responsible owners, and schedules clear enough to start within 30 days?    | Are risks mitigated? Is there a call-to-action with clear deliverables?          |

### Automated Scoring
- The evaluator agent uses Gemini to score each category 1–5 and produce comments.
- Scores are persisted in long-term memory for trend analysis.

### Human-in-the-loop
- Facilitators can add feedback via CLI/Notebook prompts; comments are appended to long-term memory.
- Use the rubric table to guide peer or mentor review sessions and calibrate the automated scorer.

