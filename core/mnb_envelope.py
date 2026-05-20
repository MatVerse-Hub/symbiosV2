from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    """Return deterministic JSON for hashing and replay."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MNBEnvelope:
    event_id: str
    source_node: str
    target_node: str
    action: str
    timestamp: str
    payload_hash: str
    identity_present: bool
    policy_present: bool
    evidence_present: bool
    risk: float = 0.0

    @classmethod
    def from_connection_event(cls, event: Mapping[str, Any]) -> "MNBEnvelope":
        return cls(
            event_id=str(event.get("event_id", "")),
            source_node=str(event.get("source_node", "")),
            target_node=str(event.get("target_node", "")),
            action=str(event.get("action", "")),
            timestamp=str(event.get("timestamp", "")),
            payload_hash=str(event.get("payload_hash", "")),
            identity_present=bool(event.get("identity")),
            policy_present=bool(event.get("policy")),
            evidence_present=bool(event.get("evidence")),
            risk=float(event.get("risk", 0.0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def hash(self) -> str:
        return sha256_text(canonical_json(self.to_dict()))
