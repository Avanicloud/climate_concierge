# Architecture Overview

This document explains how the Community Climate Action Concierge satisfies the Kaggle capstone scoring rubric while remaining production-ready.

## 1. High-Level Diagram

See `architecture.mmd` for the Mermaid source. The system is composed of:

- **Client Interface**: CLI or Jupyter notebook front-end that initiates sessions and displays outputs.
- **Orchestrator**: Coordinates the lifecycle of the agent team using a LangGraph state machine built atop the Agent Development Kit (ADK).
- **Agents**:
  - *Community Liaison*: intake agent using Gemini 1.5 Flash, responsible for session setup and persona gathering.
  - *Policy Researcher*: retrieves regulations and contextual data.
  - *Funding Scout*: surfaces grants and eligibility summaries.
  - *Action Planner*: composes initiative plan, timeline, and budget.
  - *Communications Coach*: drafts outreach copy and volunteer instructions.
  - *Evaluator*: runs automated rubric scoring, enabling continuous improvement.
- **Memory Layer**:
  - `Session Memory Service` retains in-progress conversation context.
  - `Memory Bank` stores multi-session history (community profile, past grants, evaluation feedback).
- **Tools**:
  - `civic_data_tool`: queries open datasets (CSV + optional live API).
  - `grant_finder_tool`: filters grants by geography, match requirement, and topic.
  - `impact_simulator`: models emissions and equity outcomes.
  - `timeline_builder`: generates milestone schedule, integrates with calendar stub.
  - `calendar_tool`: stubs integration with volunteer platforms (MCP compatible).
- **Observability**: Logs, metrics, and traces persisted in `run_artifacts/`.

## 2. Data Flow
1. Organizer prompts CLI → Liaison collects requirements and stores in session memory.
2. Orchestrator triggers specialized agents sequentially, passing normalized state.
3. Agents invoke tools via MCP endpoints (local Python functions or external APIs).
4. Outputs are validated via Pydantic models and appended to the shared plan state.
5. Long-term memory is updated with new insights, grants pursued, and evaluation feedback.
6. Observability hooks stream structured events for debugging and metrics.
7. Evaluator agent scores the plan; optional human feedback appended for reinforcement.

## 3. Deployment View
- **Local**: `python -m projects.climate_concierge.src.cli` for CLI run; `notebooks/demo_run.ipynb` for guided execution.
- **Cloud (optional)**:
  - Vertex AI Agent Engine deployment instructions (`deployment/vertex/`).
  - Cloud Run container with REST endpoint exposing the orchestrator.
  - Secrets stored in Secret Manager; Prometheus metrics exported via Cloud Monitoring.

## 4. Security & Compliance
- No API keys stored in repository; `.env.example` documents required secrets.
- Tools default to offline datasets; live API usage requires explicit opt-in.
- Logging avoids PII by design—stores aggregated metrics and anonymized user segments.

## 5. Extensibility
- New agents can be registered by extending `BaseAgent` and updating the orchestrator graph.
- Tool registry is decoupled via MCP manifest, enabling drop-in replacements.
- Memory backends can be swapped (e.g., Firestore, Redis) by implementing the `BaseMemoryStore`.
- Evaluation rubrics can be tuned per city or initiative type via YAML config.

## 6. Testing Strategy
- Unit tests cover tool filtering and planner assembly.
- Integration test ensures orchestrator runs with stub LLM (`ALLOW_STUB_LLM=true`).
- Notebook includes cell to verify metrics and evaluation outputs.

## 7. Observability & Evaluation
- JSONL logs and Prometheus metrics for request counts, latencies, tool failures.
- Traces capture agent transitions, enabling debugging of stuck plans.
- Evaluator agent uses Gemini rubric plus optional human-in-the-loop feedback to continuously improve plan quality.

This architecture balances hackathon velocity with production discipline—showcasing the course concepts while ready for real-world expansion.

