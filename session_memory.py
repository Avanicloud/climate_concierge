"""
Session memory implementation using in-memory dict with TTL.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionMemory:
    session_id: str
    ttl_minutes: int = 60
    created_at: float = field(default_factory=lambda: time.time())
    state: Dict[str, Any] = field(default_factory=dict)
    conversation: List[Dict[str, str]] = field(default_factory=list)

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_minutes * 60

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.state[key] = value

    def append_conversation(self, role: str, content: str) -> None:
        self.conversation.append({"role": role, "content": content})


class SessionStore:
    """
    Basic session store keyed by session ID.
    """

    def __init__(self, ttl_minutes: int) -> None:
        self.ttl_minutes = ttl_minutes
        self._sessions: Dict[str, SessionMemory] = {}

    def get_session(self, session_id: str) -> SessionMemory:
        session = self._sessions.get(session_id)
        if session is None or session.is_expired():
            session = SessionMemory(session_id=session_id, ttl_minutes=self.ttl_minutes)
            self._sessions[session_id] = session
        return session

