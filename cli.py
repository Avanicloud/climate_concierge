"""
Command-line interface for running the Climate Concierge.
"""

from __future__ import annotations

import argparse
import json
import os

from .config import load_config
from .orchestrator import ClimateConciergeOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Community Climate Action Concierge")
    parser.add_argument("--organizer", required=False, default="Neighborhood Climate Team")
    parser.add_argument("--city", required=True, help="City (e.g., Oakland)")
    parser.add_argument("--state", required=True, help="State postal code (e.g., CA)")
    parser.add_argument("--initiative", required=True, help="Initiative description")
    parser.add_argument("--scale", default="Pilot", help="Scale (Pilot/Medium/Large)")
    parser.add_argument(
        "--community-profile",
        default="Frontline neighborhood seeking resilient infrastructure upgrades.",
        help="Community profile or notes",
    )
    parser.add_argument(
        "--allow-stub-llm",
        action="store_true",
        default=False,
        help="Enable rule-based fallback instead of Gemini",
    )
    args = parser.parse_args()

    if args.allow_stub_llm:
        os.environ["ALLOW_STUB_LLM"] = "true"

    config = load_config()
    orchestrator = ClimateConciergeOrchestrator(config)
    result = orchestrator.run(
        organizer=args.organizer,
        city=args.city,
        state=args.state,
        initiative=args.initiative,
        scale=args.scale,
        community_profile=args.community_profile,
    )

    print(f"\n✅ Run completed. Run ID: {result.run_id}")
    print(f"Plan saved to: {result.artifact_path}")

    highlights = {
        "Impact": result.plan.get("impact"),
        "Top Grants": [grant["title"] for grant in result.plan.get("grants", [])],
        "Average Score": result.plan.get("average_score"),
    }
    print("\n--- Highlights ---")
    print(json.dumps(highlights, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

