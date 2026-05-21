from pathlib import Path

from core.config import DEFAULT_CONFIG
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
    assert first.startswith(DEFAULT_CONFIG.payload_hash_prefix)


def test_omega_passes_valid_event():
    envelope = MNBEnvelope.from_connection_event(valid_event())
    decision = decide(envelope)
    assert decision.decision == "PASS"
    assert decision.omega_score == DEFAULT_CONFIG.score_pass


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
    assert replayed[0]["record_hash_valid"] is True
    assert replayed[0]["trace_matches"] is True
    assert replayed[0]["decision"] == "PASS"


def test_replay_detects_modified_record_hash(tmp_path: Path):
    ledger_path = tmp_path / "ledger.jsonl"
    process_connection_event(valid_event(), ledger_path)
    records = read_jsonl(ledger_path)
    records[0]["record_hash"] = "sha256:" + "0" * 64
    replayed = replay_records(records)
    assert replayed[0]["record_hash_valid"] is False
    assert replayed[0]["matches"] is False


def test_replay_detects_modified_decision_payload(tmp_path: Path):
    ledger_path = tmp_path / "ledger.jsonl"
    process_connection_event(valid_event(), ledger_path)
    records = read_jsonl(ledger_path)
    records[0]["decision"]["decision"] = "BLOCK"
    replayed = replay_records(records)
    assert replayed[0]["record_hash_valid"] is False
    assert replayed[0]["trace_matches"] is False
    assert replayed[0]["matches"] is False
