# EXP-HZM-001 analysis

## 1. Observation

`RUN-HZM-001-a` retrieved the pinned manuscript (Mahalanobis,
arXiv:2607.09814v1) live from arXiv and extracted the exact displayed
equations for the success law `q`, candidate mass `M`, and signature/
hashtable-length quantity `H`. It found:

- `q` and `M` (Conclusion, Section 8; Equation 4 and Table 1, Section 6):
  displayed with exponent/candidate-mass base `l'`, the paper's post-
  halving reduced kernel dimension.
- `H` (Section 4.1, "the table A' is the hashtable ... has a maximum
  length of `C(l+d, d-1)`"): displayed with base `l = 2*l'`, the paper's
  pre-halving full kernel dimension -- a DIFFERENT symbol than `M`/`q`'s
  base, confirmed unambiguously from the arXiv HTML's LaTeX source markup
  (`\ell^{\prime}` vs plain `\ell`), in the same subsection, two sentences
  apart.

`specification.yaml`'s pinned `preregistered_prediction.formula` states
`H = binom(L+d, d-1) = M*d/(L+1)`, which requires `M` and `H` to share one
base `L`. The manuscript's own displayed equations do not share a base.

Full anchors, exact quoted LaTeX, and the symbolic identity check are in
`manuscript_alignment.md` and `runs/RUN-HZM-001-a/raw-result.json`.

No worked example fully parameterizing `p`, the curve, matrix `K`, chosen
index sets, or a recovered zero minor/scalar could be located in the pinned
manuscript (`CTRL-HZM-WORKED-EXAMPLE`: `control_unavailable`).

## 2. Comparison

Against the specification's own pre-registered stopping rule
(`stopping_rules[0]` and `CTRL-HZM-MANUSCRIPT-ALIGNMENT`'s
`pass_condition`), the finding above is a **FAIL**: `q`, `M`, and `H` are
not mapped to one outer trial/defect/stopping rule using one shared base
parameter. This is exactly the concern independently raised in
`RT-20260723-303` (`RT303-O3`) against the earlier snapshot quote, now
independently reproduced against the manuscript itself.

## 3. Inference

Per `specification.yaml`'s `falsification_criterion(a)`: *"systematic
deviation: measured counts depart from the pinned formulas beyond the
factor of 2 at any tested config -- the manuscript-alignment premise fails
and the cost claim is recorded `inconclusive_misalignment`."* Here the
misalignment is found at the formula-anchoring stage itself, before any
toy-scale measurement -- the specification's own Stage 1 stop rule
(`stopping_rules[0]`) applies directly: *"Stop the experiment as
inconclusive_misalignment if CTRL-HZM-MANUSCRIPT-ALIGNMENT fails; a toy run
is never opened on unaligned formulas."*

Consequently:

- `RUN-HZM-001-b` (formal 9-config x 3-seed toy enumeration grid) and
  `RUN-HZM-001-c` (formal brute-force control subset + primary-gate charged-
  cost ledger) were never opened.
- No candidate-completion, signature-enumeration, or charged-cost
  measurement exists for this experiment.
- No certificate was ever generated (`certificate.kind: none` throughout;
  claim_tier remains `toy`, and no discrete-log-solve or factor-base-
  relation claim is made anywhere in this experiment).

The three implementation modules required by `required_artifacts`
(`signature_enumeration.py`, `cost_ledger.py`, `brute_force_control.py`)
were nonetheless written as genuine, working code and unit-smoke-tested in
isolation (`implementation/SELFTEST.md`) -- this satisfies the artifact
requirement and leaves a reusable implementation for a future protocol
amendment, but the smoke test is explicitly **not** the formal protocol
measurement and carries no evidentiary status.

**Experiment-level classification: `inconclusive_misalignment`.**

This is neither a `support` (gate survival) nor a `reject_scoped`
(falsification-b, non-sub-rho) outcome. It is the third, pre-registered
branch: the specification's own pinned formula pair does not correspond
one-to-one to the manuscript's displayed equations, so no scientific
conclusion about gate survival or falsification can be drawn from this
experiment as specified. Per this program's rules, this Executor makes no
determination of whether the underlying heuristic (`HEUR-001`) or the
hypothesis (`H-HZM-001`) is supported or refuted -- that judgment, and any
`replicate`/`refine`/`inconclusive` transition, belongs to the Coordinator
and Validator/Red Team per `docs/task-lifecycle.md` Section 9.

## 4. Limitation

- This audit establishes only that the specification's *pinned formula
  pair, as literally written*, does not match the manuscript's displayed
  equations for `H` versus `M`/`q`. It does **not** establish that the
  manuscript's underlying algorithm is incorrect, that `q<=min(1,M/N)` is
  false, or that the correct `H` (using base `l=2*l'`) would change the
  qualitative Omega(N^(1-o(1))) conclusion of the prior static audit
  (`TASK-20260723-301`/`RT-20260723-303`) -- indeed, using the LARGER base
  `l=2L` for `H` would only increase the manuscript's own signature count
  relative to the spec's assumed `H=binom(L+d,d-1)`, which if anything
  would strengthen rather than weaken the prior audit's non-sub-rho
  expectation, but this Executor does not draw that conclusion here since
  it is outside this experiment's frozen scope and would require a new,
  re-anchored formula pair and a protocol amendment, not a silent
  substitution.
- No toy-scale, standardized-curve, key-recovery, or crypto-tier claim is
  made or implied anywhere in this experiment (claim_tier: toy throughout,
  and in fact no toy computation of the pinned mechanism occurred at all).
- This experiment closes only the question of whether
  `specification.yaml`'s specific pinned formula pair anchors to the
  manuscript as written; it does not close `H-HZM-001`, `HEUR-001`, or the
  broader defect-scaled hyperplane-signature zero-minor route.
- A protocol amendment could re-pin `H` using the manuscript's own base
  `l = 2*L` (rather than `L`) and re-open Stage 2/3 under a corrected,
  internally-consistent formula pair; that amendment is a Coordinator
  decision, not made here.
