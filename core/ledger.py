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


def compute_record_hash(record: dict[str, Any]) -> str:
    """Recompute the canonical record hash excluding the stored hash field."""
    unsigned = {key: value for key, value in record.items() if key != "record_hash"}
    return sha256_text(canonical_json(unsigned))


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
    record["record_hash"] = compute_record_hash(record)
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
        stored_record_hash = record.get("record_hash")
        recomputed_record_hash = compute_record_hash(record)
        record_hash_valid = stored_record_hash == recomputed_record_hash
        trace_matches = (
            envelope.hash() == record.get("mnb_hash")
            and decision.decision == record.get("decision", {}).get("decision")
            and receipt.receipt_hash == record.get("receipt", {}).get("receipt_hash")
        )
        replayed.append({
            "event_id": envelope.event_id,
            "mnb_hash": envelope.hash(),
            "decision": decision.decision,
            "receipt_hash": receipt.receipt_hash,
            "stored_record_hash": stored_record_hash,
            "recomputed_record_hash": recomputed_record_hash,
            "record_hash_valid": record_hash_valid,
            "trace_matches": trace_matches,
            "matches": record_hash_valid and trace_matches,
        })
    return replayed
