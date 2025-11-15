"""
Stub calendar/volunteer tool to simulate sign-up flows.
"""

from __future__ import annotations

from typing import Dict, List


class CalendarTool:
    def create_events(self, timeline: List[Dict], city: str) -> List[Dict]:
        events = []
        for milestone in timeline:
            events.append(
                {
                    "title": f"{city} - {milestone['name']}",
                    "start": milestone["start_date"],
                    "end": milestone["end_date"],
                    "location": f"{city} Community Center",
                    "volunteer_slots": 20,
                    "status": "draft",
                }
            )
        return events

