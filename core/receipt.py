from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .mnb_envelope import MNBEnvelope, canonical_json, sha256_text
from .omega_gate import OmegaDecision


@dataclass(frozen=True)
class Receipt:
    event_id: str
    mnb_hash: str
    decision: str
    reason: str
    omega_score: float
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_receipt(envelope: MNBEnvelope, decision: OmegaDecision) -> Receipt:
    mnb_hash = envelope.hash()
    core = {
        "event_id": envelope.event_id,
        "mnb_hash": mnb_hash,
        "decision": decision.decision,
        "reason": decision.reason,
        "omega_score": decision.omega_score,
    }
    receipt_hash = sha256_text(canonical_json(core))
    return Receipt(
        event_id=envelope.event_id,
        mnb_hash=mnb_hash,
        decision=decision.decision,
        reason=decision.reason,
        omega_score=decision.omega_score,
        receipt_hash=receipt_hash,
    )
