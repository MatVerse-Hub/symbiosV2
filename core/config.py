from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NativeLayerConfig:
    payload_hash_prefix: str = "sha256:"
    payload_hash_hex_length: int = 64
    risk_escalate_threshold: float = 0.65
    risk_block_threshold: float = 0.85
    score_block: float = 0.0
    score_high_risk_block: float = 0.1
    score_hold: float = 0.5
    score_escalate: float = 0.7
    score_pass: float = 0.95

    @property
    def payload_hash_length(self) -> int:
        return len(self.payload_hash_prefix) + self.payload_hash_hex_length


DEFAULT_CONFIG = NativeLayerConfig()
