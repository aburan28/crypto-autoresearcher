# BATCH-038 — scope decision

**Goal:** GOAL-ECDLP-001 · **Authority:** DEC-20260803-155a86 · **Opened:** 2026-08-03

## What this batch does

Performs **OPEN-BATCH023-A**: the direct B-smoothness measurement of the
half-arity Semaev partial-map integer invariants (HEUR-DS-1), against a
**measured** null, under the frozen contract `EXP-SMTH-71b1b0`.

## Why this and not the alternative

The goal's recorded `next_action` targets a second gated repair of
`EXP-IT-001` v3. That path is **blocked** and this one is not.

`EV-IT-001` and `EV-IT-002` cite `RUN-IT-001-bounded-toy` and
`RUN-IT-001-rerun`. Both runs exist with complete artifacts. Both fail
validation as "unknown run", because `tools/validate_ledger.py` scans runs only
at `experiments/*/runs/*/manifest.yaml` and registers flat JSON manifests only
for *frozen legacy* runs — and BATCH-028 wrote these as flat `manifest.json`.
Resolving that means ruling on whether those runs are citable evidence, which
is a Coordinator decision about evidence admissibility, not a lint fix. It is
deferred, not abandoned, and is named as this goal's other open thread.

`OPEN-BATCH023-A` was ranked **first** by `DEC-20260801-011`, was never
performed, and needs no such ruling.

## Why it reduces uncertainty

It replaces an *inferred* smoothness rate with a *measured distribution*. The
contract's success criterion is a two-sided distributional test against a
measured null at the actual X, with four blocking controls. Both outcomes are
informative: support at toy scale narrows HEUR-DS-1's plausible range, and
failure closes the exact tested scope.

## What it may never conclude

**TOY TIER under every outcome.** Two field sizes at 16 and 20 bits,
`|FB| = 512`, `m = 4`, INT-1 / ENC-B, on the declared ladder. No cost saving,
no exponent, no crypto-scale validity, no consequence for any deployed scheme.
Per `DEC-20260731-019` ruling 3, a recollection of the literature may be used
neither to promote nor to dismiss any outcome.

## Defects carried into this batch, unresolved

Both recorded in `CORR-20260803-a1c41e`, both defects of the freezing task
`TASK-20260802-80f5e9`, neither hidden:

1. **The freeze receipt did not exist.** `freeze_rule` declares that the
   contract's sha256 "is recorded in freeze_receipt.json and is re-hashed by
   the measurement task, which HALTS if the digest differs" — and no such file
   existed anywhere in the repository. The declared halt protection was not in
   force. `TASK-20260803-bc2e31` writes it now, marked `written_late`.

2. **The supersession receipt is unverifiable.** The contract states that
   `EXP-SMTH-4403c4` "is left unedited with its sha256 `80b75c41…` standing".
   That file is absent from the tree, and it has exactly one version in the
   entire git history (commit `f846c8dd`) whose sha256 is `664e37a3…`. The
   declared digest matches nothing that ever existed. This is recorded as
   unverifiable, **not** as fabrication — a digest computed from a working tree
   that was edited again before archiving would produce exactly this. It does
   not block the measurement: the contract states its measured quantity
   directly rather than by reference to the superseded one.

## Contested point, flagged for review rather than settled

`EXP-SMTH-71b1b0` carries `execution_authorized: false`, and its `freeze_rule`
forbids edits. `DEC-20260803-155a86` authorizes execution **externally** — the
frozen record states what was true at freeze time; a committed decision states
what is true now, exactly as corrections supersede rather than overwrite.

The competing reading — that `freeze_rule` requires a *superseding contract*
with `execution_authorized: true` — is defensible. It is put to the Red Team
(`TASK-20260803-51fb7d`) as an explicit challenge. If it carries, the batch
re-opens against a new contract id.

## Binding constraint on the Executor

The run package **must** be `manifest.yaml` with a nested top-level `run:` key.
This is the defect that made `EV-IT-001`/`EV-IT-002` uncitable. A run this
batch cannot cite is a run this batch wasted.

## Known tree state

`tools/check_merge_hygiene.py` **passes**. `tools/validate_ledger.py` reports
**20** new errors, all pre-existing on `origin/main`, none introduced here, none
depended on by this batch. They are named in `INPUT-CAPSULE.md`.
