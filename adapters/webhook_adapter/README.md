# Webhook Adapter

The webhook adapter turns incoming external events into MatVerse connection events.

It is explicit infrastructure: the service owner configures which webhook sources are accepted and which policy applies.

## P1 behavior

```text
Webhook payload
→ source verification
→ payload hash
→ connection event
→ MNB envelope
→ Ω-Gate
→ receipt
→ ledger append
→ replayable trace
```

## Required controls

- verify source identity when available
- hash the raw payload before processing
- reject unsigned or untrusted sources according to policy
- redact secrets before any export
- keep the original payload out of public artifacts unless explicitly allowed

## Fail-closed defaults

- unknown source: HOLD or BLOCK by policy
- missing payload hash: BLOCK
- missing policy: BLOCK
- suspected secret exposure: BLOCK_SECURITY
