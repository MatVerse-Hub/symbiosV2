from __future__ import annotations

import json
from pathlib import Path

from adapters.github_adapter.runner import process_github_event_file


REPO_ROOT = Path(__file__).resolve().parents[1]
EVENT_PATH = REPO_ROOT / "adapters" / "github_adapter" / "sample_push_event.json"
LEDGER_PATH = REPO_ROOT / "reports" / "github_ledger.jsonl"
RESULT_PATH = REPO_ROOT / "reports" / "github_adapter_result.json"


def main() -> int:
    result = process_github_event_file("push", EVENT_PATH, LEDGER_PATH)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True)
    RESULT_PATH.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if result.get("replay", {}).get("matches") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
