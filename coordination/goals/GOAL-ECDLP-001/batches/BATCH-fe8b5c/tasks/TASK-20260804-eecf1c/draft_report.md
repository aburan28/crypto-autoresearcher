# EXP-SMTH-92d322 approval-facing draft

## Why a successor is needed

`TASK-20260803-e50765` correctly refused before constructing a driver, creating
data, or attempting a run. `EXP-SMTH-71b1b0` had status
`frozen_awaiting_execution`, `execution_authorized: false`, no `approved_by`,
and no `freeze_receipt.json`. This is an authorization/specification-binding
defect, not evidence about `H-SMTH-001`.

## Retained, fully specified protocol boundary

- Two toy prime-field sizes: 16 and 20 bits; one deterministic curve per size.
- `m=4`, strict `i<j` enumeration of a deterministic 512-coordinate factor
  base, for exactly 130816 treatment pairs and no diagonal.
- `INT-1` / `ENC-B`, measured uniform null on `[1,p**2]`, null factored and
  hash-committed before treatment, complete factorization, and the declared
  power, identity, completeness, and pair-count controls.
- Frozen metric thresholds: KS2-DS-1 `0.006373`, TAIL-DS-1 `0.01`, KS-DS-1
  `0.05`, and DECAY-1 `0.006404`; Dickman comparisons remain descriptive only.
- Seed strategy retains master seed `4403196` and separates the successor with
  domain `EXP-SMTH-92d322/v1`.
- Budget: one planned run, 5400 seconds, 4 GiB peak RSS, four workers, no
  network, and the predecessor's declared CPU/disk/resume limits.

Every possible outcome remains toy tier only. No branch makes an ECDLP cost,
exponent, crypto-scale, or deployed-scheme claim.

## Required review before approval

The predecessor did not fully specify the deterministic curve/factor-base
selection algorithm, the exact INT-1/ENC-B/root-multiset arithmetic and
exception handling, the factorization solver configuration and raw-result
schema, or numerical RSS preflight tolerances/margins for its 5/10/20% probes.
The draft names these as approval requirements rather than inventing values.
It also requires a new approval decision, a non-null approver in the future
approved contract, a new freeze receipt binding its SHA-256, and a separate
authorized execution task.

## Requested user approval

Please approve **review and freezing of this draft only**, after the unresolved
specification items above are resolved. This is not a request to execute an
experiment. A later, separate explicit authorization is required before any
Executor task, run, code, or data is created.
