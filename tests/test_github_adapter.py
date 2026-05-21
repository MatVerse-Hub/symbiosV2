from pathlib import Path

from adapters.github_adapter.event_to_connection import (
    github_event_to_connection_event,
    payload_hash,
)
from adapters.github_adapter.runner import process_github_event, process_github_event_file
from core.ledger import read_jsonl, replay_records


def sample_push_payload():
    return {
        "ref": "refs/heads/main",
        "after": "5743936fc2d70f521271223c206098eeeb50ab70",
        "timestamp": "2026-05-21T00:25:00Z",
        "repository": {
            "full_name": "MatVerse-Hub/symbiosV2",
            "private": False,
        },
        "sender": {
            "login": "MatVerse-py",
        },
        "head_commit": {
            "id": "5743936fc2d70f521271223c206098eeeb50ab70",
            "message": "Merge PR #10: Harden CI evidence command execution",
        },
    }


def test_payload_hash_is_deterministic():
    payload = sample_push_payload()
    assert payload_hash(payload) == payload_hash(payload)
    assert payload_hash(payload).startswith("sha256:")
    assert len(payload_hash(payload)) == 71


def test_push_event_converts_to_connection_event():
    payload = sample_push_payload()
    event = github_event_to_connection_event("push", payload)
    assert event["event_id"] == "github-push-5743936fc2d7"
    assert event["source_node"] == "github:MatVerse-Hub/symbiosV2"
    assert event["target_node"] == "matverse:native-network-layer"
    assert event["action"] == "github.push"
    assert event["identity"]["sender"] == "MatVerse-py"
    assert event["policy"]["name"] == "github-adapter-p4-default"
    assert event["evidence"]["payload_hash"] == event["payload_hash"]


def test_github_adapter_processes_event_and_replays(tmp_path: Path):
    ledger_path = tmp_path / "github_ledger.jsonl"
    result = process_github_event("push", sample_push_payload(), ledger_path)
    assert result["decision"] == "PASS"
    assert result["replay"]["matches"] is True
    assert ledger_path.exists()

    records = read_jsonl(ledger_path)
    assert len(records) == 1
    replay = replay_records(records)
    assert replay[0]["matches"] is True


def test_github_adapter_processes_event_file(tmp_path: Path):
    event_path = tmp_path / "push.json"
    event_path.write_text(
        '{"repository":{"full_name":"MatVerse-Hub/symbiosV2"},'
        '"sender":{"login":"MatVerse-py"},'
        '"after":"5743936fc2d70f521271223c206098eeeb50ab70",'
        '"timestamp":"2026-05-21T00:25:00Z"}',
        encoding="utf-8",
    )
    ledger_path = tmp_path / "github_ledger.jsonl"
    result = process_github_event_file("push", event_path, ledger_path)
    assert result["decision"] == "PASS"
    assert result["connection_event"]["source_node"] == "github:MatVerse-Hub/symbiosV2"
    assert result["replay"]["record_hash_valid"] is True
