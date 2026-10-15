# EigenX identity and claim boundary

`EigenX` is the user-facing alias for the existing **CEST-PKE** candidate, not a second scheme or a new version. Its canonical repository identity is:

- proposal: `IDEA-20261007-560bcb`
- hypothesis: `H-SSI-fbe68d`
- candidate task: `TASK-20261007-913665`
- candidate: [candidate.md](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/candidate.md)
- six-obligation draft: [scheme-contract.yaml](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/scheme-contract.yaml)
- proof-search map: [proof-search-map.yaml](../../../coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/proof-search-map.yaml)
- canonical blocker: [EigenX/CEST EndRing reduction is not established](../../../problems/eigenx-cest-endring-reduction-not-established.md)

The defining transfer is

```text
A = psi_E(P),  R = [r]P,
sender:    S = [r]A,
recipient: S = psi_E(R).
```

The accepted-key correctness identity is conditional and algebraic. The current security argument reaches only the separately named `CEST-XFER-KI` game in the classical ROM. It does not supply a correctly directed reduction from an EigenX attacker to a complete EndRing solver, a QPT/QROM theorem, CCA security, concrete parameters, or a deployment claim.

The active successor is `BATCH-44a1ce`, which studies the upstream adaptive OneEnd coverage and extraction obligations before any new encryption wrapper. A surviving bridge would be an input to a later construction review; it would not automatically complete EigenX.
