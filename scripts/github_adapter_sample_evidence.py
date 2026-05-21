from __future__ import annotations

import json
from pathlib import Path

from adapters.github_adapter.runner import process_github_event_file


EVENT_PATH = Path("adapters/github_adapter/sample_push_event.json")
LEDGER_PATH = Path("reports/github_ledger.jsonl")
RESULT_PATH = Path("reports/github_adapter_result.json")


def main() -> int:
    result = process_github_event_file("push", EVENT_PATH, LEDGER_PATH)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("replay", {}).get("matches") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
