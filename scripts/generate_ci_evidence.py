from __future__ import annotations

import argparse
import compileall
import contextlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Mapping

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
COMMANDS: Final[Mapping[str, tuple[str, ...]]] = {
    "pytest": ("pytest",),
    "py_compile": ("compileall", "core"),
}


def ensure_repo_root_on_path() -> None:
    """Ensure in-process checks can import repository packages from CI."""
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def run_pytest() -> tuple[str, str]:
    """Run pytest in-process to avoid shell or subprocess execution."""
    ensure_repo_root_on_path()
    try:
        import pytest
    except ImportError as exc:
        return "FAIL", f"pytest import failed: {exc}"

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = pytest.main([str(REPO_ROOT / "tests")])
    output = (stdout.getvalue() + stderr.getvalue()).strip()
    return ("PASS" if exit_code == 0 else "FAIL"), output


def run_py_compile() -> tuple[str, str]:
    """Compile core Python files in-process using compileall."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        ok = compileall.compile_dir(str(REPO_ROOT / "core"), quiet=1)
    output = (stdout.getvalue() + stderr.getvalue()).strip()
    return ("PASS" if ok else "FAIL"), output


def run_command(command_name: str) -> tuple[str, str]:
    """Run an internal allowlisted in-process command."""
    if command_name not in COMMANDS:
        return "FAIL", f"command not allowlisted: {command_name}"
    if command_name == "pytest":
        return run_pytest()
    if command_name == "py_compile":
        return run_py_compile()
    return "FAIL", f"command has no handler: {command_name}"


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate MatVerse Native Layer CI evidence report.")
    parser.add_argument("--output", default="reports/native_layer_ci_report.json")
    args = parser.parse_args()

    pytest_status, pytest_output = run_command("pytest")
    py_compile_status, py_compile_output = run_command("py_compile")

    overall = "PASS" if pytest_status == "PASS" and py_compile_status == "PASS" else "BLOCK"
    commit_sha = os.environ.get("GITHUB_SHA") or os.environ.get("COMMIT_SHA") or "unknown"

    report = {
        "component": "matverse-native-network-layer",
        "commit_sha": commit_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tests": pytest_status,
        "py_compile": py_compile_status,
        "status": overall,
        "command_policy": {
            "allowlisted_commands": sorted(COMMANDS),
            "execution_mode": "in_process",
            "repo_root": str(REPO_ROOT),
            "shell": False,
            "subprocess": False,
        },
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
