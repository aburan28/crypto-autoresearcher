# Independent replication of the FROB-q11-n5-object01 null-witness finding

Written during `/review-evidence EXP-FROB-b8cf21`, TASK-20260921-e107c8.

## What this is

Two from-scratch, plain-Python implementations of finite-field and elliptic-
curve arithmetic (`replication_q11n5_object01.py`, `positive_control_q7n3_object01.py`),
sharing **zero code** with `runs/TASK-20260907-ee1e3c/implementation.py` or
`.../checker.py`. Inputs are read by hand from `fixtures.json` (curve
coefficients, field modulus, subgroup order, raw base-point coordinate lists)
and hard-coded as constants — these are immutable run artifacts, not code
under test.

They independently re-derive whether any 3-point relation `P1+P2+P3=O` exists
with all three points drawn from the stated base union, for:
- `FROB-q11-n5-object01`, covers `"1"`, `"2"`, `"1,2"` — the producer's claim
  is `accepted_count = 0` on all three (metrics.json: `all_rank=0` throughout).
- `FROB-q7-n3-object01`, covers `"1"`, `"1,2,3"` — a **positive control**,
  since the producer's own data shows nonzero relations there
  (`all_rank=1` and `all_rank=8` respectively). This rules out "the
  independent code just always returns zero."

## Result

```
q11-n5-object01: accepted_count = 0, 0, 0   (covers 1 / 2 / 1,2)
q7-n3-object01:  accepted_count = 12, 180   (covers 1 / 1,2,3)
```

Both independently reproduced exactly. All 20 base points independently
verified to lie on their respective curves.

## What this is NOT

**This is not the `blind_rederivation` AGENTS.md "Review architecture"
requires.** That control demands deriving the quantity "from the statement of
the quantity and the parameters alone, never reading the producer's
implementation, notes, or report." This script's `accepted`/`Q3`/`same`
predicate (arity-3 relation `P1+P2+P3=O` with `P3` also constrained to lie in
the union) was taken from reading `implementation.py` lines 480–528, not
derived independently from `specification.yaml`'s prose alone (the
`primary_quantity`/`quotient` sections). A genuinely blind first reading of
that prose does not unambiguously rule out an arity-2 reading
(`P1+P2=O` directly) — this session's own first guess, before opening the
code, was exactly that arity-2 reading, and it was wrong.

So: this is an independent **replication**, code-informed, valuable for
ruling out an implementation bug in the rank/accept-counting logic (the
positive control) and for confirming the raw group-theoretic fact holds
against a completely independent arithmetic stack (not merely a shared-Sage
re-run). It does **not** discharge `review_plan.blind_rederivation`, which
remains assigned separately with `blind_from` including this directory.
