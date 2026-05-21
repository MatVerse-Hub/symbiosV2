from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_hash(payload: Mapping[str, Any]) -> str:
    encoded = canonical_json(payload).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _repository_full_name(payload: Mapping[str, Any]) -> str:
    repository = payload.get("repository")
    if isinstance(repository, Mapping):
        full_name = repository.get("full_name")
        if full_name:
            return str(full_name)
    return "unknown/repository"


def _sender_login(payload: Mapping[str, Any]) -> str:
    sender = payload.get("sender")
    if isinstance(sender, Mapping):
        login = sender.get("login")
        if login:
            return str(login)
    return "unknown-sender"


def _event_action(event_type: str, payload: Mapping[str, Any]) -> str:
    action = payload.get("action")
    if action:
        return f"github.{event_type}.{action}"
    return f"github.{event_type}"


def _event_id(event_type: str, payload: Mapping[str, Any]) -> str:
    delivery = payload.get("delivery_id") or payload.get("hook_id")
    if delivery:
        return f"github-{event_type}-{delivery}"

    after = payload.get("after")
    if after:
        return f"github-{event_type}-{str(after)[:12]}"

    number = payload.get("number")
    if number:
        return f"github-{event_type}-{number}"

    return f"github-{event_type}-{payload_hash(payload)[7:19]}"


def github_event_to_connection_event(event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a GitHub webhook-like payload into a MatVerse ConnectionEvent."""
    repository = _repository_full_name(payload)
    sender = _sender_login(payload)
    event_hash = payload_hash(payload)

    return {
        "event_id": _event_id(event_type, payload),
        "source_node": f"github:{repository}",
        "target_node": "matverse:native-network-layer",
        "action": _event_action(event_type, payload),
        "timestamp": str(payload.get("timestamp") or payload.get("created_at") or "unknown"),
        "payload_hash": event_hash,
        "identity": {
            "source": "github",
            "repository": repository,
            "sender": sender,
            "event_type": event_type,
        },
        "policy": {
            "name": "github-adapter-p4-default",
            "allow_events": ["push", "pull_request", "issues"],
        },
        "evidence": {
            "payload_hash": event_hash,
            "repository": repository,
            "event_type": event_type,
        },
        "risk": 0.2,
        "metadata": {
            "ref": payload.get("ref"),
            "after": payload.get("after"),
            "number": payload.get("number"),
        },
    }
