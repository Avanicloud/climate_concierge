"""
Persistent memory backed by JSON file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class MemoryRecord:
    key: str
    value: Dict[str, Any]


@dataclass
class LongTermMemory:
    """
    Simple key-value store persisted to disk.
    """

    store_path: Path
    records: Dict[str, MemoryRecord] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.store_path.exists():
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
            self.records = {key: MemoryRecord(key=key, value=value) for key, value in raw.items()}

    def get(self, key: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
        record = self.records.get(key)
        if record:
            return record.value
        return default or {}

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self.records[key] = MemoryRecord(key=key, value=value)
        self._flush()

    def append_to_list(self, key: str, value: Dict[str, Any]) -> None:
        record = self.records.get(key)
        if not record:
            record = MemoryRecord(key=key, value={"items": []})
            self.records[key] = record
        record.value.setdefault("items", [])
        record.value["items"].append(value)
        self._flush()

    def list(self, key: str) -> List[Dict[str, Any]]:
        record = self.records.get(key)
        if not record:
            return []
        return record.value.get("items", [])

    def _flush(self) -> None:
        payload = {key: record.value for key, record in self.records.items()}
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

