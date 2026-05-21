from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run_command(command: list[str]) -> tuple[str, str]:
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    status = "PASS" if completed.returncode == 0 else "FAIL"
    return status, (completed.stdout + completed.stderr).strip()


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate MatVerse Native Layer CI evidence report.")
    parser.add_argument("--output", default="reports/native_layer_ci_report.json")
    args = parser.parse_args()

    pytest_status, pytest_output = run_command(["python", "-m", "pytest"])
    py_compile_status, py_compile_output = run_command([
        "python",
        "-m",
        "compileall",
        "-q",
        "core",
    ])

    overall = "PASS" if pytest_status == "PASS" and py_compile_status == "PASS" else "BLOCK"
    commit_sha = os.environ.get("GITHUB_SHA") or os.environ.get("COMMIT_SHA") or "unknown"

    report = {
        "component": "matverse-native-network-layer",
        "commit_sha": commit_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tests": pytest_status,
        "py_compile": py_compile_status,
        "status": overall,
        "outputs": {
            "pytest": pytest_output[-4000:],
            "py_compile": py_compile_output[-4000:],
        },
    }

    write_report(Path(args.output), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
