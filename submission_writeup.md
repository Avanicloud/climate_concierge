## Title
Community Climate Action Concierge

## Subtitle
Multi-agent Gemini-powered copilot accelerating neighborhood climate initiatives

## Track
Agents for Good

## Problem
Neighborhood leaders and mutual-aid groups want to launch climate resilience projects—solarizing community centers, expanding tree canopy, or piloting clean mobility—but lack the time and expertise to digest regulations, hunt for grants, build timelines, and coordinate volunteers. The planning phase can take weeks, delaying impact for communities that feel climate stress the most.

## Solution
The Community Climate Action Concierge is a multi-agent system built with the Agent Development Kit (ADK) that fuses civic open data, grant intelligence, and collaborative planning skills into a single assistant. A liaison agent interviews organizers, specialized agents research policy and funding, a planner agent assembles budgets/timelines/impact forecasts, and a communications coach drafts outreach collateral. An evaluator agent scores the plan with an LLM rubric so organizers can iterate quickly.

## Technical Architecture
- **Multi-agent orchestration** with LangGraph + ADK: Liaison → Policy Researcher → Funding Scout → Action Planner → Communications Coach → Evaluator.
- **Tooling via MCP + custom Python actions**: civic climate datasets, grant catalogue, impact simulator, timeline builder, calendar/volunteer stubs.
- **Sessions & Memory**: `InMemorySessionService` abstraction and JSON-backed memory bank store conversation context, past initiatives, and evaluation feedback.
- **Observability**: Structured JSON logs, Prometheus metrics, and trace events persisted under `run_artifacts/` for every run.
- **Evaluation**: LLM-as-judge rubric (Gemini 1.5 Flash or stub) and human feedback capture.
- **Deployment readiness**: CLI + notebook demo locally; instructions and IaC snippets for Vertex AI Agent Engine / Cloud Run deployment.

## Implementation Highlights
1. **Specialized agents**: Each agent encapsulates prompt templates, tool access, and validated outputs using Pydantic schemas to control state passed to the next step.
2. **Context engineering**: Organizer profile, city metrics, grants, and timeline details are compacted into focused prompts to stay within context windows while retaining relevance.
3. **Observability-first**: Metrics track agent runtime, plan quality scores, and tool success. Traces reveal the cross-agent narrative, making debugging simple.
4. **Evaluation loop**: Automated rubric scoring plus a human feedback hook that writes to long-term memory—valuable for continuous improvement and future benchmarking.
5. **Deployment playbook**: Config-driven architecture allows switching between stub and Gemini-powered runs, enabling offline demos while keeping a path to production.

## Results & Impact
- Generates actionable plan artifacts (impact modeling, timeline, funding matches, outreach copy) in minutes.
- Surfaces grants tailored to geography and initiative keywords, increasing funding readiness.
- Produces observability artifacts for governance and showcases replicable agent evaluation practice.

## Bonus Elements
- Powered by **Gemini 1.5 Flash** for content generation (stub fallback for offline demo).
- **Deployment guide** for Vertex AI Agent Engine + Cloud Run containerization.
- Planned **<3 min demo video** walk-through using provided storyboard.

## Instructions
1. Clone repo and install requirements.
2. Set `GEMINI_API_KEY` (or `ALLOW_STUB_LLM=true` for offline).
3. Run `python -m src.cli --city "Oakland" --state "CA" --initiative "Solarize the community center roof" --allow-stub-llm`.
4. Inspect generated plan under `run_artifacts/plans/`.
5. Optional: open `notebooks/demo_run.ipynb` for guided workflow and metrics visualization.

## Future Work
- Integrate live Google Search & civic APIs via MCP manifests.
- Add volunteer-matching API connector (Mobilize/Slack).
- Expand evaluation dataset with human annotated baseline plans.
- Launch user-facing web experience leveraging the same orchestrator microservice.

## References
- ADK Python docs, Vertex AI Agent Engine docs, EPA & DOE open datasets.

