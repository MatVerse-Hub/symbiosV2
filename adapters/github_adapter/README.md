# GitHub Adapter

The GitHub adapter turns repository activity into MatVerse connection events.

It is designed for pull requests, commits, issues, releases, workflow runs, and code-review events.

## P1 behavior

```text
GitHub event
→ repository identity
→ payload hash
→ connection event
→ MNB envelope
→ Ω-Gate
→ receipt
→ ledger append
→ replayable trace
```

## Candidate event types

- pull_request.opened
- pull_request.merged
- push
- release.published
- workflow_run.completed
- issue.opened
- issue.closed

## Required controls

- include repository full name
- include commit SHA or event delivery ID when available
- hash webhook payload before transformation
- preserve review comments as evidence when relevant
- classify generated agent commits as agent-originated evidence

## Fail-closed defaults

- missing repository identity: BLOCK
- missing event payload hash: BLOCK
- missing policy: BLOCK
- failed workflow for protected path: HOLD or BLOCK by policy
