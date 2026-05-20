from pathlib import Path

from core.ledger import process_connection_event, read_jsonl, replay_records
from core.mnb_envelope import MNBEnvelope
from core.omega_gate import decide


VALID_HASH = "sha256:" + "a" * 64


def valid_event(**overrides):
    event = {
        "event_id": "evt-001",
        "source_node": "agent-a",
        "target_node": "api-b",
        "action": "connect",
        "timestamp": "2026-05-20T00:00:00Z",
        "payload_hash": VALID_HASH,
        "identity": {"node_id": "agent-a"},
        "policy": {"name": "default-connect"},
        "evidence": {"kind": "signed-request"},
        "risk": 0.1,
    }
    event.update(overrides)
    return event


def test_mnb_hash_is_deterministic():
    first = MNBEnvelope.from_connection_event(valid_event()).hash()
    second = MNBEnvelope.from_connection_event(valid_event()).hash()
    assert first == second
    assert first.startswith("sha256:")


def test_omega_passes_valid_event():
    envelope = MNBEnvelope.from_connection_event(valid_event())
    decision = decide(envelope)
    assert decision.decision == "PASS"
    assert decision.omega_score == 0.95


def test_omega_blocks_missing_identity():
    envelope = MNBEnvelope.from_connection_event(valid_event(identity={}))
    decision = decide(envelope)
    assert decision.decision == "BLOCK"
    assert "identity" in decision.reason


def test_omega_holds_missing_evidence():
    envelope = MNBEnvelope.from_connection_event(valid_event(evidence={}))
    decision = decide(envelope)
    assert decision.decision == "HOLD"


def test_ledger_append_and_replay(tmp_path: Path):
    ledger_path = tmp_path / "ledger.jsonl"
    record = process_connection_event(valid_event(), ledger_path)
    assert ledger_path.exists()
    assert record["decision"]["decision"] == "PASS"
    records = read_jsonl(ledger_path)
    replayed = replay_records(records)
    assert len(replayed) == 1
    assert replayed[0]["matches"] is True
    assert replayed[0]["decision"] == "PASS"
