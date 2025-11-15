"""
Generates initiative timeline milestones.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Dict


@dataclass
class Milestone:
    name: str
    start_week: int
    duration_weeks: int
    owner: str


class TimelineBuilderTool:
    def build(self, initiative: str) -> List[Dict]:
        now = datetime.utcnow()
        baseline = [
            Milestone("Kickoff meeting & resource inventory", 1, 1, "Community lead"),
            Milestone("Feasibility research & site assessment", 2, 2, "Policy research pod"),
            Milestone("Grant preparation & submission", 4, 3, "Funding team"),
            Milestone("Community outreach & volunteer onboarding", 4, 4, "Communications"),
            Milestone("Implementation sprint", 8, 4, "Operations"),
            Milestone("Measurement & celebration event", 12, 2, "All stakeholders"),
        ]
        if "solar" in initiative.lower():
            baseline.insert(3, Milestone("Solar contractor RFP & selection", 4, 2, "Facilities"))
        elif "tree" in initiative.lower():
            baseline.insert(3, Milestone("Nursery partnership & species selection", 4, 2, "Urban forestry"))

        timeline = []
        for milestone in baseline:
            start = now + timedelta(weeks=milestone.start_week - 1)
            end = start + timedelta(weeks=milestone.duration_weeks)
            timeline.append(
                {
                    "name": milestone.name,
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d"),
                    "owner": milestone.owner,
                }
            )
        return timeline

