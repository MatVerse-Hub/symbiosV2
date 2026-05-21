import json
from pathlib import Path

from scripts import github_adapter_sample_evidence as evidence


def test_github_adapter_sample_evidence_writes_result_and_ledger(tmp_path: Path, monkeypatch):
    result_path = tmp_path / "github_adapter_result.json"
    ledger_path = tmp_path / "github_ledger.jsonl"

    monkeypatch.setattr(evidence, "RESULT_PATH", result_path)
    monkeypatch.setattr(evidence, "LEDGER_PATH", ledger_path)

    exit_code = evidence.main()

    assert exit_code == 0
    assert result_path.exists()
    assert ledger_path.exists()

    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["decision"] == "PASS"
    assert result["replay"]["matches"] is True
    assert result["record_hash"].startswith("sha256:")

    ledger_lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(ledger_lines) == 1
    assert json.loads(ledger_lines[0])["record_hash"] == result["record_hash"]
