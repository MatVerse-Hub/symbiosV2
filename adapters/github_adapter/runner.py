from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from core.ledger import process_connection_event, read_jsonl, replay_records

from .event_to_connection import github_event_to_connection_event

DEFAULT_LEDGER_PATH = Path("reports/github_ledger.jsonl")


def load_event(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def process_github_event(
    event_type: str,
    payload: dict[str, Any],
    ledger_path: str | Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    connection_event = github_event_to_connection_event(event_type, payload)
    record = process_connection_event(connection_event, ledger_path)
    replay = replay_records([record])[0]
    return {
        "event_type": event_type,
        "connection_event": connection_event,
        "decision": record["decision"]["decision"],
        "reason": record["decision"]["reason"],
        "mnb_hash": record["mnb_hash"],
        "receipt_hash": record["receipt"]["receipt_hash"],
        "record_hash": record["record_hash"],
        "ledger_path": str(ledger_path),
        "replay": replay,
    }


def process_github_event_file(
    event_type: str,
    event_path: str | Path,
    ledger_path: str | Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    payload = load_event(event_path)
    return process_github_event(event_type, payload, ledger_path)


def read_github_ledger(ledger_path: str | Path = DEFAULT_LEDGER_PATH) -> list[dict[str, Any]]:
    return read_jsonl(ledger_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Process a GitHub event through MatVerse Native Layer.")
    parser.add_argument("--event-type", required=True, choices=["push", "pull_request", "issues"])
    parser.add_argument("--event-path", required=True)
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    args = parser.parse_args()

    result = process_github_event_file(args.event_type, args.event_path, args.ledger_path)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] in {"PASS", "HOLD", "ESCALATE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
