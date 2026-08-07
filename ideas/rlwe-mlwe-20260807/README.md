# R-LWE / M-LWE lane — experiment designs and new ideas, 2026-08-07

Follow-up to `ideas/rlwe-mlwe-20260806/` (merged in [PR #209](https://github.com/aburan28/crypto-autoresearcher/pull/209)),
which proposed nine mechanisms and was then pressure-tested — 7 of 7 claim
clusters partially wrong, all 12 blocking corrections applied. This directory
turns the two GO-cleared lanes into formal hypothesis/experiment records and
adds five new ideas, each targeting a specific gap the pressure test exposed
rather than a fresh untested speculation.

**Nothing here is a ledger record.** IDs verified free 2026-08-07. Promote via
Coordinator only.

## Experiments

| file | status | what it does |
|---|---|---|
| `H-RLWE-1fb603.draft.yaml` + `EXP-RLWE-a2253c.draft.yaml` | **ready to run** | Formalizes M9. The prediction is already a proof (signed-permutation collapse of the Galois orbit under symmetric error support); this experiment discharges the two remaining proof obligations by direct computation and tries to falsify, not confirm. |
| `EXP-RLWE-59d3fb.draft.yaml` | **Stage A blocked, Stage B preregistered** | M1's prior-art gate (is Karenin–Kirshanova arbitrary-rank or rank-2 only?) plus the contingent DSD/NTRU-control sweep, calibrated on the *concrete* fatigue curve this time — the pressure test's central correction, baked in rather than left to be rediscovered. |

M9 is the one to run first: it needs no external acquisition, and the mechanism is already derived — the experiment is verification, not discovery.

## Five new ideas, each closing a specific gap

- **`IDEA-20260807-7caf6e`** — GOAL-RLWE-001's own success criterion currently has no legitimate NTRU reference value, because DvW's constant is calibrated on *matrix* NTRU and the goal's object is *circulant*. This measures the circulant fatigue point directly, reusing the same detector — a prerequisite, not an option.
- **`IDEA-20260807-a80c17`** — a cheap, acquisition-independent test of whether Ogilvie 2026/279 (the pressure test's highest-value unresolved gap in the κ-surface lane) subsumes the κ-surface: does any secondary source state her framework's ML-KEM-scale number, and does it match the corrected `233`?
- **`IDEA-20260807-aee47c`** — scopes M8's reopened question down to a toy-scale gate test (does log-embedding search beat brute force on rank-2 BDD *at all*) rather than leaving it as an unscoped moonshot tied to M7.
- **`IDEA-20260807-04d21f`** — connects two threads that don't currently talk to each other: the κ-surface's subring-descent construction already builds non-ideal R'-submodule objects; M4's surviving novelty is exactly the non-ideal case Peikert's bound doesn't cover. Feed one into the other as a search strategy instead of only testing known instances.
- **`IDEA-20260807-b2ccb3`** — tests the explicit boundary of H-RLWE-1fb603's proof: the Galois-orbit collapse needs a *symmetric* error support. Does the deficit reopen under asymmetric error? This is the one idea here with a genuine positive prediction — if confirmed, it's a real (if narrow) case where ring structure helps an algebraic attack.

## Sequencing

1. `EXP-RLWE-a2253c` (M9) — no blockers, run now.
2. `IDEA-20260807-b2ccb3` — sequence directly after, reuses the same harness.
3. `EXP-RLWE-59d3fb` Stage A (M1's PDF gate) — start the acquisition attempt in parallel; it has nothing to do with the M9 lane.
4. `IDEA-20260807-7caf6e` (circulant NTRU reference) — needed before Stage B of `EXP-RLWE-59d3fb` is interpretable, not before it runs.
5. `IDEA-20260807-a80c17` (Ogilvie test) and `IDEA-20260807-aee47c` (M7/M8 gate test) — independent of the above, cheap, can run any time but stay behind the existing goal-level gates (M2+M5's novelty grade, M1+M9 respectively).
6. `IDEA-20260807-04d21f` — deliberately last; depends on both `IDEA-20260807-a80c17` resolving and M4's re-scoping landing.
