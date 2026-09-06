---
id: KN-FIND-3245f1
type: internal_finding
title: "Standard scalar-coefficient linear self-reduction cannot supply Simon 2026's DCP-route sample requirement against a single ML-KEM public key -- combinatorial-ceiling axis, all three standardized levels"
tags:
- ml-kem
- module-lwe
- dcp-route
- self-reduction
- access-model-audit
- crypto-scale
confidence: reported
internal_refs:
- H-MLKEM-36f511
- EV-QALG-8d85be
- DEC-20260906-cc4fb6
proof_status: derivation
proof_refs:
- experiments/EXP-MLKEM-12d9b8/runs/RUN-MLKEM-12d9b8-001/raw-result.json
- coordination/goals/GOAL-QALG-001/reviews/RUN-MLKEM-12d9b8-001-validation/independent_recompute.py
added: '2026-09-06'
superseded_by: null
---

## Artifacts

- `experiments/EXP-MLKEM-12d9b8/` -- frozen specification, `amendments/v1.yaml`
  (resulting_version 2), `runs/RUN-MLKEM-12d9b8-001/`.
- `ledger/decisions/DEC-20260906-b60887.yaml` (dispatch authorization),
  `DEC-20260906-cc4fb6.yaml` (evidence-review decision closing this record).
- Independent review: `coordination/goals/GOAL-QALG-001/reviews/RUN-MLKEM-12d9b8-001-validation/report.yaml`
  (CONFIRM) and `.../RUN-MLKEM-12d9b8-001-redteam/report.yaml` (REVISE, on an
  unrelated stage-0 completeness point -- see `CORR-20260906-69ff2a`).

## The finding

Simon 2026 (KN-LIT-e204ab, an unverified, self-labelled "[Preliminary Draft]"
preprint) proposes a polynomial-time quantum DCP algorithm requiring
`Q = k*n^(c+1)` (c >= 12) roughly-independent, roughly-faulty samples within a
`1/O(log n)` fault-rate tolerance. `IDEA-20260813-02479f` / `H-MLKEM-36f511`
asked whether ML-KEM's own real Module-LWE structure could supply this sample
count against a single standard public key, via the most natural
sample-generation mechanism: standard linear self-reduction (a bounded
scalar-coefficient combination of up to `k_mlkem` real rows).

**It cannot, by an overwhelming combinatorial margin, independent of the
noise-budget question entirely.** At the amendment's own operative ceiling
(coefficient magnitude bounded by ML-KEM's modulus, `B <= q = 3329` --
already the most generous ring-compatible bound, since no coefficient beyond
`q` induces a new residue class), the number of *distinct virtual samples*
this mechanism can produce is at most `(2B+1)^k_mlkem`. Compared against
Simon's own stated minimum sample requirement at each ML-KEM level and
c-sweep value:

| level | k_mlkem | ceiling at B=q | Q (c=12) | shortfall (orders of magnitude) |
|---|---|---|---|---|
| ML-KEM-512 | 2 | 44,342,281 (~4.4e7) | ~3.3e35 | ~28 |
| ML-KEM-768 | 3 | 295,275,249,179 (~3.0e11) | ~9.7e37 | ~26 |
| ML-KEM-1024 | 4 | 1,966,237,884,282,961 (~2.0e15) | ~5.4e39 | ~24 |

The shortfall widens further as `c` increases across the paper's own valid
sweep range (24 to 50 orders of magnitude across `c` in `{12,13,15,20}`, all
three levels). This holds *before* accounting for noise budget at all: at
`B=q`, the induced per-term noise variance (`~q^2*eta/2`) is itself ~6-7
orders of magnitude above ML-KEM's genuine per-coordinate noise, so a
noise-coherent `B` would sit far below `q`, making the true ceiling even
smaller. **The combinatorial axis alone forecloses this access-model
regardless of how the noise-budget question resolves.**

## Independence and robustness

Reproduced exactly, with zero discrepancy, by three independent
implementations: the Executor's `compute.py`, the Validator's from-scratch
`independent_recompute.py` (written from the frozen formulas alone, before
reading `compute.py`), and the Red Team's own hand/script verification. A
dedicated proves-too-much control found no self-reduction technique known to
be realizable that this counting method would falsely reject *within the
claim's own declared scope* (standard, scalar-coefficient self-reduction);
the one credible richer construction that could plausibly evade this ceiling
(a ring-element / Galois-orbit self-reduction exploiting ML-KEM's polynomial
ring structure, using a full ring-element multiplier rather than a bounded
integer scalar) is independently identified by the red-team review and found
to be *already, explicitly* named and excluded as out-of-scope by
`H-MLKEM-36f511`'s own `assumptions`/`interpretation_limits` -- not silently
ignored.

## Why this is a barrier result and not an attack, and what it is not

`sota_delta = 0`; no solve, relation, speedup, or security-margin revision is
claimed. `certificate.kind: none`. This is a pre-compute access-model
realizability gate (KN-TECH-080 vocabulary): it checks whether the abstract
algorithm's assumed input interface is instantiable from a concrete ML-KEM
public key, independent of whether Simon's algorithm, once given that
interface, would actually work.

**What is NOT established:**
1. **Stage 0's faulty-rate axis** -- the noise-variance-to-faulty-rate
   conversion chain remains explicitly `NOT COMPUTED` (no source in this
   program's corpus supplies the required formula; see
   `CORR-20260906-69ff2a` for a related, corrected completeness gap in that
   search). This finding does not depend on that axis at all.
2. **Richer self-reduction constructions** (ring-element/Galois-orbit) are
   an open direction, not ruled out.
3. **Simon 2026's Lemma 3** and the rest of the DCP paper's correctness are
   untouched -- audited separately by `IDEA-20260813-4aecda`, not this
   record.
4. **The base reduction's own noise rate** (`IDEA-20260813-0cf345`) is a
   separate, not-yet-tested question.

## Promotion-gate status

`DEC-20260906-cc4fb6` records `support` for `H-MLKEM-36f511` at evidence
strength `strong` (three independent exact-arithmetic reproductions, zero
discrepancy, a survived adversarial falsification attempt), scoped exactly
as this entry states. Per CLAUDE.md's knowledge-promotion gate, a `support`
decision at `strong` strength promotes this finding rather than stating
`not_warranted`.
