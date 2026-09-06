# Analysis — EXP-ARGON-2608c2

Task: TASK-20260812-300522 | Batch: BATCH-ba7b2f | Goal: GOAL-ARGON-001
Hypothesis: H-ARGON-ef2f0b | Contract: `experiments/EXP-ARGON-2608c2/specification.yaml`
(status: approved, version 1)

This analysis is written by the Coordinator under `/review-evidence`
(`docs/task-lifecycle.md` step 8), against the run package snapshot-committed
at `1977b5ae83ebfe2a849c3ef6d9a6ccb7a2effecd`
(`coordination/goals/GOAL-ARGON-001/batches/BATCH-ba7b2f/archives/TASK-20260812-300522/snapshot-receipt.json`,
`verification_status: content_verified`). Every number below was independently
re-read from `runs/RUN-ARGON-2608c2-*/manifest.yaml` and
`raw-result.json`, not taken from `execution_report.md`'s prose alone, and one
q=16 cell of each calibration family was independently re-derived by brute
force (see "Independent re-derivation" under Comparison) as a pipeline check
before trusting the ILP solver's output on the cell that failed.

## 0. Validity check (docs/task-lifecycle.md step 7/8 gate, run before analysis)

- **Run count.** 6 of 6 planned `calibration_exact_tier` runs completed and
  are present: `RUN-ARGON-2608c2-{294e74,868a32,2ba6b8,4da88e,1a1711,e0b77a}`,
  matching `execution_report.md`'s `runs.completed`+`runs.failed` list
  exactly (2 families × 3 `exact_tier_sizes`). No other run was planned for
  this task per the calibration gate's ordering (`calibration_greedy_tier`
  and every Argon2-stage run are `not_run`, with reasons recorded).
- **Schema validity.** All 6 `manifest.yaml` files carry every field
  `docs/evidence-and-reproducibility.md`'s minimum run manifest requires:
  `code.commit`/`dirty`/`command`, `inference.*` (with `fallback_used: true`
  correctly disclosed, not silently substituted), `environment.*`,
  `inputs.*`, `timing.wall_seconds`, `result.metrics`/`valid`/
  `invalid_reason`/`certificate`, `artifacts.*`. `certificate.kind: none` in
  every run, consistent with a pure-measurement contract that claims no
  solve or relation (see Section 3 below).
- **Seed integrity.** `rng_seeds: []` in every manifest, with an explicit
  `rng_seeds_note` explaining why: both calibration families are
  deterministic constructions, the greedy heuristic is a deterministic
  fixed-tie-break DP, and CBC branch-and-cut is deterministic given a fixed
  formulation and solver version. No RNG-dependent step exists anywhere in
  this run set (Argon2's synthetic-seed-material machinery was never
  invoked). This is internally consistent and leaves nothing unaccounted.
- **Raw/summary agreement.** Checked cell-by-cell, `raw-result.json` against
  both `manifest.yaml`'s `result.metrics` and `execution_report.md`'s
  `calibration_exact_tier_table`:

  | family | q | greedy (raw/manifest/report) | exact (raw/manifest/report) | ratio (raw/manifest/report) | agree? |
  |---|---|---|---|---|---|
  | A | 16 | 6/6/6 | 5/5/5 | 1.2/1.2/1.2000 | yes |
  | A | 32 | 11/11/11 | 8/8/8 | 1.375/1.375/1.3750 | yes |
  | A | 64 | 21/21/21 | 17 (upper bound)/17/17 (upper bound) | 1.2353/1.235294/[1.235,4.20] | yes (report additionally states the widened uncertified bracket using the dual bound, which the raw file does not itself compute as a ratio — consistent, not contradictory) |
  | B | 16 | 1/1/1 | 1/1/1 | 1.0/1.0/1.0000 | yes |
  | B | 32 | 1/1/1 | 1/1/1 | 1.0/1.0/1.0000 | yes |
  | B | 64 | 1/1/1 | 1/1/1 | 1.0/1.0/1.0000 | yes |

  No discrepancy found in either direction.
- **Control comparability.** Not applicable in the usual G_real-vs-G_unif
  sense — this run set never reached that stage. The relevant comparability
  check here is instead that the exact solver and the greedy heuristic were
  run on the *same* graph object per cell (confirmed: both operate on the
  same `family`/`q` construction, and `verify_removal`/`verify_ok: true` in
  every `raw-result.json` independently re-checks that both the greedy and
  exact removal sets actually reach `target_depth` on that graph — this is
  itself a cheap internal control against a solver returning a set that
  merely claims to work).
- **Calibration-gate ordering honored.** Searched every artifact under
  `experiments/EXP-ARGON-2608c2/runs/` (`stdout.log`, `stderr.log`,
  `raw-result.json`, `command.txt`, `environment.json`, and the `_lib/`
  source) for any reference to `argon2`, `G_real`, `G_unif`, `rho`, or `KS`:
  no match anywhere. `runs/_lib/argon2_lane.py` and `runs/_lib/ks.py` exist
  as source (declared `implementation_snapshot`) but every
  `command.txt`/manifest `code.command` invokes only
  `calibration_exact_cell.py --family ... --q ... --time-limit-seconds ...`.
  The invalidation rule ("A run set claiming a completed rho reading... is
  INVALID if the REQUIRED calibration gate was not run and passed before
  that cell's G_real/G_unif construction began") is therefore satisfied by
  construction: no rho reading is claimed, and no G_real/G_unif graph exists
  to have been built out of order.
- **Independent re-derivation (pipeline check, not part of the frozen
  protocol, done here as due diligence before trusting the tool on the cell
  that failed).** Brute force over all node subsets of size 0..q for
  `family_A_doubling_graph` and `family_B_pure_chain` at q=16 (the smallest
  exact-tier size) reproduces both reported exact values exactly:
  family_A q=16 -> minimum removal size 5 (matches
  `RUN-ARGON-2608c2-294e74`); family_B q=16 -> minimum removal size 1
  (matches `RUN-ARGON-2608c2-4da88e`). This corroborates that the graph
  constructors, the target-depth definition, and the exact-value reporting
  are correct on the cells that did certify, using a method independent of
  both the greedy heuristic and the ILP formulation. It does not and cannot
  resolve the q=64 tractability question (brute force over 2^64 subsets is
  infeasible); the q=64 gap is a genuine solver-tractability finding, not an
  artifact traceable to a construction bug, to the extent this smaller-scale
  check can speak to it.

**Conclusion of the validity check: the run package is VALID.** 6/6 expected
runs, complete and schema-consistent manifests, accounted-for absence of
RNG, exact raw/summary/report agreement, and confirmed absence of any
out-of-order Argon2 construction. This run package is admissible evidence.

## 1. Observation

Five of six required `calibration_exact_tier` cells certified
`calibration_error_ratio = greedy_|S*| / exact_|S*|` inside `[1.0, 1.5]`,
each backed by a CBC branch-and-cut run whose `LpStatus` was independently
confirmed (via OS-level fd redirection fixing a prior mis-classification
bug, `implementation.md` "Exact-computation tractability finding") to have
actually proved optimality, not merely returned an unproven incumbent:

- `family_A_doubling_graph`, q=16: ratio 1.2000, `proven_optimal` (5.3s).
- `family_A_doubling_graph`, q=32: ratio 1.3750, `proven_optimal` (39.3s).
- `family_B_pure_chain`, q=16/32/64: ratio 1.0000 at all three, each
  `proven_optimal` in well under 1s (the minimum removal set for the pure
  chain is always exactly 1 node — the chain's own midpoint — independent
  of q, a structurally obvious closed form the exact solver reproduces
  trivially).

The sixth required cell, `family_A_doubling_graph` at q=64, did **not**
certify: CBC exhausted a declared 150s time limit (and a 300s ad hoc
diagnostic extension) with an incumbent of 17 (a valid, `verify_ok: true`
upper bound on the true minimum) and a dual (lower) bound that only reached
4.433 (rounds to 5), never closing the branch-and-bound gap. The true exact
value for this cell is therefore only known to lie in `[5, 17]`, which
implies `calibration_error_ratio` (greedy 21 over the true exact value)
lies somewhere in `[1.235, 4.20]` — a range, not a point, and one that is
not contained in, but also not confirmed to be excluded from, the required
`[1.0, 1.5]` window.

## 2. Comparison against the frozen protocol

The frozen `specification.yaml` `stopping_rules` (first entry, mirrored in
`invalidation_rules`) requires ratio-in-`[1.0,1.5]` certification for BOTH
calibration families at ALL THREE `exact_tier_sizes` (16, 32, 64) **before**
any `G_real`/`G_unif` Argon2 graph may be constructed, worded as binding
procedurally, not merely numerically. 5 of 6 cells meeting the bound does
not satisfy an "at every exact_tier_size" gate for both families — the text
admits no partial-credit reading, and the Executor's halt before any Argon2
construction is the contractually correct response, independently confirmed
here rather than accepted on the Executor's own characterization.

This is not the calibration_error_ratio the gate anticipated failing
*outside* the bound (i.e., a confirmed bad ratio) — it is a case the
contract's designers did not explicitly distinguish from that: an
**uncertified** ratio, where the true value might still be inside the
window (best case 21/17 ≈ 1.235, inside) or well outside it (worst case
21/5 = 4.20, far outside). The contract's stopping rule reads most naturally
as requiring certified compliance, not merely "not confirmed to be
non-compliant," so treating this as a gate failure (rather than searching
for a reason to wave it through) is the reading consistent with the
contract's own emphasis that "the measurement pipeline is not yet
trustworthy enough to interpret any Argon2-derived rho number."

The Executor's protocol deviations (documented in `implementation.md` and
`execution_report.md`) are accurately and completely disclosed: the
tooling limitation (open-source CBC only, no commercial solver), the
formulation history (three rejected approaches before the final tight-`M`
MILP), the fd-redirection bug-and-fix for correctly detecting
non-optimality, and the never-exercised Argon2/KS code paths. No deviation
silently changed a reported number's correctness.

## 3. Inference

**What this run set establishes:** the calibration precondition
(`bcf891_independent_known_family_calibration`) that gates this
hypothesis's substantive measurement did not reach a pass determination,
for reasons that are a genuine combinatorial-optimization tractability
finding — `family_A_doubling_graph`'s adversarial, many-overlapping-path
structure produces a weak LP relaxation that open-source CBC cannot close
within budget at q=64 — not an implementation defect (three independent
formulation attempts, plus the brute-force cross-check at q=16, converge on
the same picture) and not evidence of anything about Argon2.

**What this run set does NOT establish:** anything about H-ARGON-ef2f0b's
actual claim. No `G_real` or `G_unif` graph was ever constructed for any
variant (Argon2i/d/id), at any (t, q). No rho value, no KS statistic, no
seed-consistency check exists anywhere in this run set. The hypothesis's
mechanism (RFC 9106's within-window offset transform concentrating
probability toward recent blocks, making the Argon2 DAG cheaper to shatter
than a uniform-reference null) was simply never brought into contact with
data by this task. Per AGENTS.md rule 3, a resource-exhaustion/procedural
halt is never negative evidence about a hypothesis's substantive claim, and
there is here no substantive-claim data of either sign to weigh in any
case — this is a stronger statement than "the evidence doesn't count
against H-ARGON-ef2f0b," namely "no evidence bearing on H-ARGON-ef2f0b
exists in this run set at all."

**No certificate is required or implicated.** Per
`docs/claims-and-verification.md`, `certificate: {kind: none}` is the
correct declaration for a pure-measurement contract, and every run's
manifest carries it. No run in this set claims a solve or a relation of any
kind (not even the calibration exact values, which are measurements of a
graph property, not a discrete-log-style witness), so the certificate
discipline's independent-re-verification requirement is inapplicable, not
merely unmet.

**Refutation-artifact seeking (docs/claims-and-verification.md, "Refutation
artifacts") does not apply here.** That discipline governs an *adverse*
transition against a hypothesis (`weaken`, `reject_scoped`, hypothesis ->
`rejected`) resting on a result that speaks to the hypothesis's prediction.
Nothing here speaks to H-ARGON-ef2f0b's prediction in either direction —
there is no rho/KS reading to be a counterexample, a derivation target, or
an empirical-only contradiction of. Seeking a counterexample certificate or
derivation note for a claim that was never measured would be a category
error, not rigor. This determination is `inconclusive`/procedural, not
`weaken` or `reject_scoped`, precisely because the refutation-artifact
ladder has no rung to climb: there is nothing here to refute.

## 4. Limitations

- Scope: exactly two synthetic calibration graph families
  (`family_A_doubling_graph`, `family_B_pure_chain`), at exactly three exact
  sizes (16, 32, 64), using exactly one open-source ILP solver (CBC 2.10.3
  via pulp 3.3.2) under a 150s (declared) / 300s (diagnostic) time budget on
  a 4-vCPU/15GiB host. Nothing here transfers to a different solver, a
  longer budget, a different family construction, or Argon2 itself.
- The `[5, 17]` bracket for `family_A_doubling_graph` at q=64 is a genuine
  measured fact (a certified feasible upper bound and a certified dual lower
  bound), but the *true* minimum within that bracket is unknown; this
  analysis does not guess at it, narrow it further, or treat either
  endpoint as more likely than the other.
- The brute-force cross-check in Section 0 covers only q=16 for both
  families; it corroborates the pipeline's correctness on a *certified*
  cell and cannot speak to whether the q=64 tractability wall reflects any
  latent defect specific to larger instances (none is suspected — three
  independent formulation attempts converge on the same qualitative
  picture — but this analysis does not claim to have ruled it out beyond
  what those three attempts already show).
- This analysis makes no claim, positive or negative, about Argon2, RFC
  9106, HEUR-001, HEUR-002, or any parameter set's suitability. No password,
  credential, leaked corpus, or third-party dataset was used or referenced
  anywhere in this task, consistent with GOAL-ARGON-001's binding
  constraint.
- claim_tier: `toy` (finite calibration graphs at q<=64, well inside the
  toy-tier bound); this analysis does not extrapolate to any larger scale.
