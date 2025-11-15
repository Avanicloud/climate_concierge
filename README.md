# Deployment Guide

This project can be deployed either as a Vertex AI Agent Engine agent or a containerized microservice (Cloud Run / Cloud Functions). The steps below outline both options.

## 1. Prerequisites
- Google Cloud project with billing enabled.
- `gcloud` CLI installed and authenticated.
- Vertex AI API enabled (for Agent Engine).
- Artifact Registry repository (for container deployments).

## 2. Environment Variables
Create a `.env` file or configure Secret Manager entries with:

```
GEMINI_API_KEY=<your key>
GOOGLE_API_KEY=<optional search key>
LOG_LEVEL=INFO
```

## 3. Vertex AI Agent Engine (Optional Bonus)
1. Package the orchestrator as an HTTP handler (see `src/cli.py` for entrypoint reference).
2. Define an Agent Engine manifest referencing the handler and required environment variables.
3. Deploy via `gcloud beta agent-engines deploy --project <PROJECT_ID> --config agent_engine.yaml`.
4. Update README with the public endpoint (if any) and reproduction steps.

## 4. Cloud Run Deployment
1. Build container:
   ```bash
   gcloud builds submit --tag gcr.io/<PROJECT_ID>/climate-concierge
   ```
2. Deploy:
   ```bash
   gcloud run deploy climate-concierge \
     --image gcr.io/<PROJECT_ID>/climate-concierge \
     --region <REGION> \
     --set-env-vars GEMINI_API_KEY=projects/<PROJECT_ID>/secrets/gemini_api_key:latest \
     --allow-unauthenticated
   ```
3. Expose a `/generate` endpoint that proxies to the orchestrator `run` method.

## 5. Observability in Production
- Stream JSON logs to Cloud Logging using structured log fields (already compatible).
- Export Prometheus metrics via `/metrics` endpoint and hook into Cloud Monitoring.
- Persist long-term memory to Firestore or Cloud Storage by replacing the local JSON store.

## 6. Post-Deployment Checklist
- Smoke test using sample payloads.
- Update `submission_writeup.md` with deployment details and endpoint.
- Capture screenshots or screen recordings for the optional demo video.

