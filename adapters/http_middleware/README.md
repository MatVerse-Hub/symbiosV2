# HTTP Middleware Adapter

This adapter is the non-invasive entry point for web services.

A service calls the MatVerse Native Network Layer before accepting a critical connection, request, webhook, agent action, or API operation.

## P0 behavior

```text
HTTP request
→ connection event
→ MNB envelope
→ Ω-Gate
→ receipt
→ JSONL ledger
→ replayable trace
```

## Integration contract

The middleware must be explicitly installed and configured by the service owner. It must not inject itself, persist secretly, or modify traffic without policy.

## Fail-closed defaults

- missing identity: BLOCK
- missing policy: BLOCK
- missing evidence: HOLD
- invalid payload hash: BLOCK
- high risk: BLOCK
