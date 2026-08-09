---
id: KN-OPEN-5b3a08
type: open_problem
title: Does the shared harness/semaev.py's confirmed s4_expr bug, or build_factor_base's whole-curve (not target-subgroup) sampling, materially affect other Semaev/point-decomposition index-calculus experiments?
tags: [semaev, groebner, harness-bug, factor-base, cofactor, point-decomposition, index-calculus, cross-experiment, shared-harness, open]
confidence: established
status: open
source_refs: [EXP-DTREE-001, EV-DTREE-2e8f6a, H-DTREE-001, RUN-DTREE-001, RUN-DTREE-006, EXP-MTIC-001, EXP-FIB-001]
added: 2026-08-09
superseded_by: null
---

## Statement

EXP-DTREE-001 (reviewed 2026-08-09, EV-DTREE-2e8f6a) surfaced two properties
of shared `harness/semaev.py` code while measuring depth-2 descent cost. Both
are established facts about the harness, independently confirmed during that
review; what is **open** is whether either one materially affects any other
experiment's already-committed or future results.

## Q1 — the `s4_expr` variable-collision bug

`harness/semaev.py`'s `s4_expr(a, b)` builds the 4th Semaev summation
polynomial via `sympy.resultant` after two `.subs()` calls that are **not**
`simultaneous=True`:

```python
def s4_expr(a: int, b: int):
    x4 = sympy.symbols("x4")
    left = s3_expr(a, b).subs(x3, _t)
    right = s3_expr(a, b).subs({x1: x3, x2: x4, x3: _t})
    return sympy.resultant(left, right, _t)
```

Because the second `.subs()` is not simultaneous, a variable intended to
become an independent free variable (`x3`, renamed from the original `x1`)
silently collapses into the dummy `_t`. **Confirmed via brute-force
reference check** (EXP-DTREE-001's `implementation.md`): evaluated at a
genuine witness `P1 + P2 + P3 = S`, `harness.semaev.s4_expr(a,b)` at
`(x(P1), x(P2), x(P3), x(S))` is nonzero — it must be exactly 0 for a correct
S4. Adding `simultaneous=True` reproduces the textbook construction and
passes exact-witness checks (199/200 in one seeded trial; the sole
non-match was independently confirmed to be a target genuinely outside the
factor base, not an instrument failure).

EXP-DTREE-001 worked around this **locally** (`semaev_fix.py`'s
`s4_expr_fixed`) rather than editing the shared file, which was out of that
experiment's declared scope. `harness/semaev.py` itself is **unmodified** as
of this entry.

**Confirmed blast radius** (verified by reading both files directly during
this review, 2026-08-09): `harness.semaev.s4_expr` is imported and called
directly by:

- `experiments/EXP-MTIC-001/code/run_mtic.py` (`from harness.semaev import
  build_factor_base, s4_expr, x1, x2, x3`; `S4 = s4_expr(a, b)`)
- `experiments/EXP-FIB-001/driver/decompcost.py` (`from harness.semaev
  import s4_expr, x1, x2, x3`; `S4 = s4_expr(a, b)`)

**CORRECTION, added after this entry's initial draft (2026-08-09, same
review pass) — the claim above was checked and found FALSE, not left
unchecked: both experiments have MANY already-executed, already-committed
runs, not zero.** `experiments/EXP-MTIC-001/runs/` contains 11 complete run
directories (`RUN-MTIC-001` through `RUN-MTIC-010`, plus a repair run
`RUN-MTIC-010b`), committed in `0ec36f637` ("snapshot TASK-20260727-912:
EXP-MTIC-001 v2 run package (10/10 terminal: 9 valid + 1 failed_implementation
+ repair 010b valid)"). `experiments/EXP-FIB-001/runs/` contains 10 complete
run directories (`RUN-FIB-001` through `RUN-FIB-008`, including `RUN-FIB-006B`
and `RUN-FIB-006C`), committed in `5a0d24c27` ("research: TASK-20260807-b62d4f
EXP-FIB-001 producer runs"). Confirmed by direct directory listing during this
review, not the frozen `specification.yaml`'s stale claim.

`s4_expr` is NOT a peripheral or guarded call in either file: in
`run_mtic.py`, `s4_setup(a, b, p, fb_xs)` computes `S4 = s4_expr(a, b)` as its
very first line, and `S4` is the "S_4 resultant" this function's own docstring
says is used for the actual per-target decomposition search downstream — this
is on the critical result path, not dead or diagnostic code.

**What this does and does not establish, checked before writing this
correction**: `EXP-MTIC-001`'s results ARE referenced by at least one existing
Coordinator decision — `DEC-20260805-48b52e` (2026-08-05), which cites
"matching EXP-MTIC-001" as a single informal, in-passing data point supporting
a finding about a DIFFERENT experiment (`EXP-MTBK-306bdb`)'s rescue-window
cell requirements. That decision is NOT a dedicated `/review-evidence` pass on
`EXP-MTIC-001` itself — no `EV-MTIC-*` evidence record exists anywhere in
`ledger/evidence/`, and no decision record targets `EXP-MTIC-001` as its
primary subject. So as of this entry, no official hypothesis-status-changing
decision is KNOWN to rest on these specific numbers — but an already-archived
result has already been informally leaned on at least once, and neither
`EXP-MTIC-001` nor `EXP-FIB-001` has been independently checked against the
`s4_expr` bug's actual numeric impact (if any) on their committed results.
This entry does NOT claim any specific committed number is wrong — only that
the mechanism for it to be wrong is confirmed, the exposure is on 21 total
archived runs (not zero), and at least one has already been cited elsewhere.

**Q1 resolution needed, escalated**: before treating any `EXP-MTIC-001` or
`EXP-FIB-001` run's committed numbers as reliable, someone should (a) fix
`harness/semaev.py`'s `s4_expr` directly (`simultaneous=True`), (b) re-run
each experiment's own exact-witness/audit check (if one exists) against the
ALREADY-COMMITTED run parameters to determine whether the specific instances
tested happened to be immune (e.g., because the collapsed variable didn't
matter for those particular witnesses) or were genuinely affected, and (c) if
affected, follow this program's correction discipline (a new `CORR-*` record,
never a silent edit of the archived run) rather than quietly re-running and
overwriting. This is now a higher-priority item than "flag for whoever
executes next" — it is "audit what may already be wrong."

## Q2 — `build_factor_base` samples the whole curve, not the target's subgroup

`harness.semaev.build_factor_base` draws x-coordinates from the full curve
`E(F_p)`, not from the order-`n` subgroup `<P>` that an ECDLP target always
lies in by construction:

```python
def build_factor_base(inst: ECDLPInstance, size: int, seed: int = 0) -> list[int]:
    E = inst.curve()
    p = E.p
    ...
    if E.lift_x(x) is not None:
        xs.append(x)
    return xs
```

This is used very widely across the program (100+ files reference
`build_factor_base`; most are planning/reference material rather than live
experiment code, and this entry does not claim to have audited them). It is
not obviously "wrong" — sampling the whole curve is the historically
standard construction in the point-decomposition index-calculus literature
— but its **statistical interaction with cofactor size** is, at minimum,
under-examined, and EXP-DTREE-001 measured a concrete case where it appears
to dominate the measured effect.

**What EXP-DTREE-001 measured** (EV-DTREE-2e8f6a): main-curve cofactors of
2280 (16-bit), 196 (20-bit), and 31512 (24-bit). Measured single-level
decomposition probability P(m=3,B) — 0.0, 0.32, 0.0 at 16/20/24-bit — does
not track HEUR-001's own `(B/N)^2` point-prediction (0.047, 0.000239, 0.003)
in either direction or magnitude at any of the three sizes. 20-bit, the
smallest of the three cofactors, is the **only** size where any
decomposition success (single-level or depth-2 stage-2) was ever observed
at all. This pattern is consistent with cofactor size being a first-order
driver of whether decomposition is measurable at all under this
construction — but EXP-DTREE-001 could not isolate this from competing
explanations, because the experiment designed to do so under controlled,
exact conditions (the C1 exact-enumeration slope fit) hit an unrelated
design-infeasibility (see H-DTREE-001, EV-DTREE-b47c19) before it could run.

**Q2 resolution needed**: any experiment that (a) uses
`harness.semaev.build_factor_base` (or a derivative) AND (b) either assumes
measured `P(m, B')` tracks the `(B'/N)^(m-1)` heuristic cleanly, or compares
decomposition rates across curves/instances with different cofactors,
should check whether this same confound applies to its own results before
relying on that comparison. This entry does not claim any specific other
experiment IS affected — only that the mechanism by which it plausibly could
be is now a documented, verified property of shared harness code, not a
one-off observation confined to EXP-DTREE-001.

## Why it matters here

Both properties live in code multiple experiments import, so a fix or a
documented caveat in one place is cheaper than every future experiment
rediscovering (or silently inheriting) the same issue independently. Neither
`H-MTIC-001` nor `H-FIB-001` is currently `supported` (both remain
`status: approved`, unchanged by any of this) — so no already-`supported`
conclusion in this program rests on either issue. That is narrower than "no
committed data is affected": see the correction above Q1's original text —
21 already-executed, already-archived runs across the two experiments used
the confirmed-buggy `s4_expr` on their result path, and at least one has
already been cited (informally, in passing) by an unrelated decision. This
entry does not assert any specific committed number is wrong — only that the
mechanism is confirmed, the exposure is real and non-trivial, and it has not
been audited.

## Current state

Open. As of 2026-08-09, `harness/semaev.py` is unmodified; no audit of
whether `EXP-MTIC-001`'s or `EXP-FIB-001`'s ALREADY-COMMITTED run results
were numerically affected by the `s4_expr` bug has been performed (this was
checked and found to be an open question, not a settled "zero risk" —
correcting this same entry's own earlier, false "zero executed runs" claim).
Neither experiment's hypothesis has been promoted to `supported` on the
strength of these runs. EXP-DTREE-001's own
results are unaffected (it worked around Q1 locally via `semaev_fix.py`, and
its own analysis explicitly declines to diagnose Q2 further than reporting
the measured pattern — see EV-DTREE-2e8f6a).

## Cheapest next step

For Q1: a one-line fix (`simultaneous=True` in `s4_expr`'s second `.subs()`
call) plus re-running `harness/semaev.py`'s own exact-witness check (already
exists in outline in EXP-DTREE-001's `implementation.md`) would resolve it
directly — cheaper than auditing every importer for whether the bug
mattered to them. For Q2: before any experiment leans on `P(m, B')`
matching HEUR-001's clean prediction, check the target curve's cofactor and
consider whether restricting `build_factor_base` to the target's own
subgroup (an opt-in parameter, not necessarily a default change, since some
experiments may deliberately want the whole-curve behavior) would change the
measured rate materially.
