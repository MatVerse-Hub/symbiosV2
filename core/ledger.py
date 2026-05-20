from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .mnb_envelope import MNBEnvelope, canonical_json, sha256_text
from .omega_gate import decide
from .receipt import create_receipt


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(record) + "\n")


def process_connection_event(event: dict[str, Any], ledger_path: str | Path) -> dict[str, Any]:
    envelope = MNBEnvelope.from_connection_event(event)
    decision = decide(envelope)
    receipt = create_receipt(envelope, decision)
    record = {
        "event": event,
        "mnb": envelope.to_dict(),
        "mnb_hash": envelope.hash(),
        "decision": {
            "decision": decision.decision,
            "reason": decision.reason,
            "omega_score": decision.omega_score,
            "replay_required": decision.replay_required,
        },
        "receipt": receipt.to_dict(),
    }
    record["record_hash"] = sha256_text(canonical_json(record))
    append_jsonl(ledger_path, record)
    return record


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]


def replay_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    replayed: list[dict[str, Any]] = []
    for record in records:
        event = record["event"]
        envelope = MNBEnvelope.from_connection_event(event)
        decision = decide(envelope)
        receipt = create_receipt(envelope, decision)
        replayed.append({
            "event_id": envelope.event_id,
            "mnb_hash": envelope.hash(),
            "decision": decision.decision,
            "receipt_hash": receipt.receipt_hash,
            "matches": (
                envelope.hash() == record.get("mnb_hash")
                and decision.decision == record.get("decision", {}).get("decision")
                and receipt.receipt_hash == record.get("receipt", {}).get("receipt_hash")
            ),
        })
    return replayed
