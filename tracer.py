"""
Simple trace recorder for agent transitions.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TraceEvent:
    timestamp: float
    agent: str
    event: str
    detail: Dict[str, Any]


class TraceRecorder:
    def __init__(self, sink_path: Path) -> None:
        self.sink_path = sink_path
        self.events: List[TraceEvent] = []

    def record(self, agent: str, event: str, detail: Optional[Dict[str, Any]] = None) -> None:
        self.events.append(
            TraceEvent(
                timestamp=time.time(),
                agent=agent,
                event=event,
                detail=detail or {},
            )
        )

    def flush(self) -> None:
        self.sink_path.parent.mkdir(parents=True, exist_ok=True)
        with self.sink_path.open("a", encoding="utf-8") as fp:
            for event in self.events:
                payload = asdict(event)
                payload["timestamp_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp))
                fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.events.clear()

