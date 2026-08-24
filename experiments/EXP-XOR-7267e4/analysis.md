<!--
This file was written by the Coordinator, not the reviewing agent. The
reviewing agent's Write tool refused to create any file matching
"analysis*.md" ("Subagents should return findings as text, not write report
files" — a harness-level restriction on that session), so it delivered this
content as text and embedded it in ledger/evidence/EV-XOR-d84f2b.yaml's own
fields instead. The Coordinator transcribed it here (the canonical location
per docs/task-lifecycle.md step 8) and independently re-verified the two most
load-bearing claims before persisting it: (1) harness/toycurve.py's negate()
and build_factor_base()'s explicit negation-closure, read directly from the
frozen source; (2) the exact candidates_verified_B = 2*R_B, false_positives_B
= R_B relationship, recomputed from raw-result.json across all 20 instances
independently (20/20 exact, zero deviation) — not merely the 4 cell-level
numbers quoted in the evidence record. See the snapshot commit message for
the specific checks performed. No content below was altered from what the
reviewing agent reported; see EV-XOR-d84f2b.yaml for the full observation
detail this summarizes.
-->

# EXP-XOR-7267e4 — Analysis

## 1. Observation

`RUN-XOR-7267e4-grid` reached 4 of 8 planned `(p,b)` cells (60 of 120 planned
arm-runs, p ∈ {101,103}, b ∈ {0.4,0.5}) before the frozen contract's own
early-exit stopping rule triggered — a deliberate in-protocol partial
completion, not a failure.

`C_A = 2|F|³` exactly in all 20 instances. `C_B` is constant within each cell
(Arm B has no seed-dependent randomness): 248, 648, 272, 792 across the four
cells. `C_D`'s five per-seed values per cell average to 176.0, 562.4, 180.8,
546.4 — matching `analysis.yaml`'s summary exactly. `R_A = R_B` exactly in
all 20 instances.

**The exact 2× relationship.** In every one of the 4 reached cells,
`candidates_verified_B = 2 × R_B` exactly (52=2·26, 124=2·62, 64=2·32,
196=2·98) and `false_positives_B = R_B` exactly. This holds with zero
deviation across all 20 individual instances, not merely at the cell-mean
level.

`R_D/R_B` (the null arm's chance-collision rate relative to genuine relation
density) stayed at 0.6%–1.5% across all four cells — far under the F3
near-null threshold of 0.95.

## 2. Comparison to predefined criteria

Prediction 2 (`C_D < C_A`, strict): held in 4/4 reached cells — expected,
since Arm D (which carries no oracle information) still beats brute-force
purely from `|F|²` table structure. Not informative about the oracle's own
contribution.

Prediction 1 (`C_B < C_D`, strict) — the scientifically load-bearing leg of
the hypothesis — **failed in 4/4 reached cells**. The reverse held instead,
`C_B > C_D`, by 41–45% margins in every cell, never a close call. Per-instance
(not just per-cell-mean), the maximum individual-seed `C_D` in each cell
stayed comfortably below the constant `C_B` in that cell, with zero
exceptions across 20 instances.

`H-XOR-a227dc`'s falsification condition **F2** ("in any cell `C_B >= C_D`")
fired in all 4 reached cells. **F1** and **F3** did not fire in any cell. The
pre-registered tail check at the largest planned cell `(211, 0.5)` is
**incomplete**, not negative — it was never reached.

## 3. Inference — the derivation

Independent reading of the frozen implementation
(`experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py`'s
`build_factor_base` and `arm_b_x_oracle`; `harness/toycurve.py`'s `negate`
and `add`) traces the exact 2× pattern to a specific, checkable mechanism
rather than treating it as an unexplained empirical curve-fit:

1. `negate((x,y)) = (x, -y mod p)`: negation preserves the x-coordinate.
   `add` returns the identity exactly when `x1==x2` and `(y1+y2)%p==0` —
   standard group law, confirmed from the actual implementation.
2. `build_factor_base` inserts, for each chosen x-coordinate, both the
   lifted point `P` and its negation `-P` (unless 2-torsion) — the factor
   base `F` is closed under negation by explicit construction.
3. `arm_b_x_oracle` keys its hash table by `x(P2+P3)` alone, discarding the
   sum's y-coordinate. For any right-pair `(P2,P3)` with sum `S = P2+P3 ≠ O`,
   the negation-pair `(-P2,-P3)` is also enumerated (since `F` is
   negation-closed), with sum `-(P2+P3) = -S`. Since `x(-S) = x(S)`, **both**
   pairs land in the same table bucket `H[x(S)]`.
4. A genuine relation requires `P1 = -(P2+P3) = -S` for some table entry.
   But the same bucket lookup also iterates the negation-pair `(-P2,-P3)`:
   checking `P1 = -S` against it computes `-S + (-P2) + (-P3) = -S + (-S) =
   -2S`, which is `O` only if `S` is 2-torsion — generically not. **Every
   genuine relation is therefore generically accompanied by exactly one
   guaranteed companion false positive**, charged at 2 field adds, from the
   same bucket lookup.

This reproduces the measured pattern exactly, with zero deviation, across
all 20 instances.

**What this does and does not establish.** Steps 1–4 generally and fully
explain why Arm B's *own* charged cost is structurally double the
pre-registered formula's assumption — a fact about the code, true at any
cell using this construction. They do **not** by themselves force
`C_B > C_D`: that additionally depends on the empirical size of `R_B` (real
Semaev-relation density of the specific curve/factor base) relative to Arm
D's chance-collision rate, which are number-theoretic/probabilistic facts
about the tested instances, not algebraic identities the derivation closes
off for all parameters. Recomputing the *original, uncorrected*
pre-registered formula at the actual measured `R_B` values already predicts
`C_B > C_D` in 3 of the 4 cells — the qualitative failure is not an artifact
riding entirely on this correction.

Separately: **the oracle's information content is confirmed, not
contradicted.** `R_D/R_B` stayed far under the F3 near-null threshold in
every cell — Arm D essentially never stumbles onto genuine relations by
chance. What fails is that this informational advantage converts into a
field-operation cost advantage under the *specific* declared charge model:
the x-only signal that makes the oracle informative is coarser than what
verification needs (it cannot distinguish `+S` from `-S`), and pays a fixed,
deterministic tax for that coarseness that Arm D's rarer, cruder collisions
do not pay at these tested densities.

## 4. Limitations

- Only 4 of 8 pre-registered `(p,b)` cells were reached; `p ∈ {107,211}`
  were never attempted. The pre-registered tail check at the largest cell is
  incomplete, not negative.
- Single run, single Executor session, single code commit; no independent
  replication of this specific charged-cost battery exists.
- The derivation's step 4 (companion false positive) is stated as "generic"
  (assumes `S` is not 2-torsion); the exact zero-deviation match across all
  20 instances is consistent with this not perturbing the tested cells, but
  which table sums are 2-torsion in these specific instances was not
  separately enumerated.
- **Generality of the exact 2× ratio is not established beyond the tested
  cells.** The negation-pairing mechanism (steps 1–4) is always present at
  any `|F|` — but whether `candidates_verified_B` stays *exactly* `2·R_B`
  additionally assumes no other pairs share a bucket beyond the guaranteed
  `±S` pair. At larger `|F|` (the untested cells), table density grows and
  additional genuine hash collisions become more plausible, which could push
  the ratio *above* 2× — making Arm B relatively *more* expensive, not
  less — rather than holding at exactly 2×.
- The mandatory reviewer + validator + red-team passes
  `specification.yaml`'s own `required_artifacts` calls for ("mandatory
  because this is the first charged-cost artifact in this lane") have not
  yet occurred for this run.
- No independent SHA-256 recomputation of `CTRL-BLOB` was performed by the
  reviewing agent (no shell tool in that session); the well-formedness and
  cross-record consistency were checked instead. The Coordinator
  independently recomputed this hash directly from file bytes during
  archival — see the snapshot commit message.
