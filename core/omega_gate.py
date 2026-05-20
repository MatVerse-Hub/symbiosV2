from __future__ import annotations

from dataclasses import dataclass

from .mnb_envelope import MNBEnvelope


@dataclass(frozen=True)
class OmegaDecision:
    decision: str
    reason: str
    omega_score: float
    replay_required: bool = True
    replay_valid: bool = False


def decide(envelope: MNBEnvelope) -> OmegaDecision:
    """Fail-closed admissibility decision for P0 connection events."""
    if not envelope.event_id or not envelope.source_node or not envelope.target_node:
        return OmegaDecision("BLOCK", "missing identity-bearing event fields", 0.0)

    if not envelope.identity_present:
        return OmegaDecision("BLOCK", "missing identity", 0.0)

    if not envelope.policy_present:
        return OmegaDecision("BLOCK", "missing policy", 0.0)

    if not envelope.payload_hash.startswith("sha256:") or len(envelope.payload_hash) != 71:
        return OmegaDecision("BLOCK", "missing or invalid payload hash", 0.0)

    if envelope.risk >= 0.85:
        return OmegaDecision("BLOCK", "risk above block threshold", 0.1)

    if not envelope.evidence_present:
        return OmegaDecision("HOLD", "missing evidence", 0.5)

    if envelope.risk >= 0.65:
        return OmegaDecision("ESCALATE", "risk requires human or external review", 0.7)

    return OmegaDecision("PASS", "identity, policy, evidence and risk are admissible", 0.95)
