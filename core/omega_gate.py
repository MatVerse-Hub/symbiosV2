from __future__ import annotations

from dataclasses import dataclass

from .config import DEFAULT_CONFIG, NativeLayerConfig
from .mnb_envelope import MNBEnvelope


@dataclass(frozen=True)
class OmegaDecision:
    decision: str
    reason: str
    omega_score: float
    replay_required: bool = True
    replay_valid: bool = False


def _valid_payload_hash(payload_hash: str, config: NativeLayerConfig) -> bool:
    if not payload_hash.startswith(config.payload_hash_prefix):
        return False
    if len(payload_hash) != config.payload_hash_length:
        return False
    digest = payload_hash.removeprefix(config.payload_hash_prefix)
    return all(char in "0123456789abcdefABCDEF" for char in digest)


def decide(envelope: MNBEnvelope, config: NativeLayerConfig = DEFAULT_CONFIG) -> OmegaDecision:
    """Fail-closed admissibility decision for connection events."""
    if not envelope.event_id or not envelope.source_node or not envelope.target_node:
        return OmegaDecision("BLOCK", "missing identity-bearing event fields", config.score_block)

    if not envelope.identity_present:
        return OmegaDecision("BLOCK", "missing identity", config.score_block)

    if not envelope.policy_present:
        return OmegaDecision("BLOCK", "missing policy", config.score_block)

    if not _valid_payload_hash(envelope.payload_hash, config):
        return OmegaDecision("BLOCK", "missing or invalid payload hash", config.score_block)

    if envelope.risk >= config.risk_block_threshold:
        return OmegaDecision("BLOCK", "risk above block threshold", config.score_high_risk_block)

    if not envelope.evidence_present:
        return OmegaDecision("HOLD", "missing evidence", config.score_hold)

    if envelope.risk >= config.risk_escalate_threshold:
        return OmegaDecision("ESCALATE", "risk requires human or external review", config.score_escalate)

    return OmegaDecision("PASS", "identity, policy, evidence and risk are admissible", config.score_pass)
