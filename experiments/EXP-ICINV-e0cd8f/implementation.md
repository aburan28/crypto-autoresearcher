# EXP-ICINV-e0cd8f — implementation note

Task `TASK-20260810-5ad325`, goal `GOAL-ENDO-001`, batch `BATCH-d7e255`.
Snapshot commit at dispatch: `5ecab6c78`.

This note records HOW the frozen contract was executed and WHERE execution
departed from it. It records observations and deviations only. It does not
interpret the results, and it does not state whether the Semaev geometry is or
is not an isogeny-class invariant (handoff constraint SC-2).

## 1. Code

All new code is in one new module, `harness/exp_icinv_geometry.py`.
`harness/semaev.py` and `harness/exp_icinv.py` were **not edited**
(contract `source_constraints`, `invalidation_rules`); they are imported
read-only. The module re-derives the S_3 expression itself so the run's algebra
is self-contained, and checks at run time that it agrees symbolically with the
committed `harness.semaev.s3_expr`
(`support-derivation.json:s3_expression_agrees_with_committed_harness`, true in
every run).

Entry points, one run each, re-executable by a third party with no model in the
loop:

```
sage -python harness/exp_icinv_geometry.py --stage gates --run-id RUN-ICINV-geom-gates
sage -python harness/exp_icinv_geometry.py --stage m3    --run-id RUN-ICINV-geom-m3
sage -python harness/exp_icinv_geometry.py --stage m3    --run-id RUN-ICINV-geom-m3-v2
sage -python harness/exp_icinv_geometry.py --stage m4    --run-id RUN-ICINV-geom-m4
```

Every run manifest pins the sha256 of every executed source file
(`harness/runner.py:source_provenance`), plus the sha256 of the three records
whose values the run binds to: the specification, the handoff, and the
committed census reference.

## 2. Objects computed, stated exactly

* Ideal, per curve: `I_3(E) = <S_3, dS_3/dx1, dS_3/dx2, dS_3/dx3>` over
  `F_4001`, monomial order `degrevlex`. **No factor-base membership polynomial
  f_V appears in any ideal computed anywhere in this module.** This is the
  contract's defining constraint; it is enforced by construction — the module
  contains no f_V and never imports one.
* Singular locus: computed on the **un-homogenised** ideal. Dimension is Sage's
  Krull dimension; degree is Singular's `mult(std(I))`, the multiplicity of the
  leading-term ideal. On every zero-dimensional case the run additionally
  computes `vector_space_dimension()` and **raises** if the two disagree; they
  never disagreed.
* Betti table and regularity: computed on the **homogenised** ideal in
  `F_p[x0,x1,x2,x3]` with the standard grading, as declared by the contract.
  Homogenisation is **generator-wise** to each generator's own total degree.
  This is not in general the ideal-theoretic homogenisation; the run records
  `saturation_differs` per curve rather than silently choosing (it is `true` on
  the curves inspected). The resolution is Singular's minimal free resolution
  of `S/J`; `beta_{i,j}` is read off the graded shifts.
  `regularity_of_quotient_S_mod_J = max{j-i : beta_{i,j} != 0}` and
  `regularity_of_ideal_J` is that plus one; both conventions are recorded so a
  successor cannot mix them.
* Elimination polynomial: the monic generator of `I_3 ∩ F_p[x3]`, with its
  `F_p`-factorisation type recorded as a partition of its degree. The "empty"
  branch (zero elimination ideal, no degree invented) exists and was never
  taken.
* Koszul indicator: `is_regular_sequence` is defined as *codimension of the
  homogenised ideal in the 4-variable ring equals the number of Jacobian
  generators (4)*. Stated projectively deliberately: four elements can never be
  a regular sequence in the 3-variable affine ring, so an affine test would be
  vacuous. `betti_equals_koszul_table` is also recorded per curve.
* m = 4: `S_4 = Res_T(S_3(x1,x2,T), S_3(x3,x4,T))`; monomial support and affine
  singular locus only.

## 3. Randomness

Single seed `20260810`, as pre-registered. It governs exactly two auxiliary
choices, both recorded per curve: the gauge parameter `u` per curve
(`random.Random(20260810)` for the control set, `+1` for the class, `+2` for
m = 4) and the 138-curve control-set draw. No primary invariant depends on it.
The control set is drawn from the enumerated ordinary curves at p = 4001 with
trace not in {30, 0}; the drawn traces are listed in
`control-set-invariants.json:draw`.

## 4. Stopping-rule mechanics

* **SR1 runs first.** The symbolic re-derivation is done in SymPy with `a` and
  `b` symbolic over ZZ — a different system from the one that computes the
  per-curve values — then the S_3 support is computed over F_4001 on all 138
  class members. Class enumeration is a prerequisite of both SR1 and SR2 and is
  performed before them; gate *evaluation* order is SR1 → SR2 → SR3, as the
  contract gives them.
* **SR2** re-emits the enumeration and compares it against the committed record
  `experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json`, read at
  run time and bound by sha256 — count, and the full 138-element set of `(a,b)`
  pairs. No reference value is transcribed.
* **SR3** is performed and recorded by the run itself, before any resolution is
  computed. The dispatching session's precondition probe is **not** cited as
  the record. Backend A self-tests inside the run on `(xy, yz, zx)` in
  `QQ[x,y,z]`.
* **SR4** is ordering, not paperwork. `control-set-invariants.json` is written
  and closed at artifact sequence 4, before any class invariant is computed.
  Each artifact's write order, timestamp and sha256 are in
  `manifest.run.artifact_write_order`, so the ordering is checkable after the
  fact rather than asserted.
* **SR6** is checked between curves against a 7200 s wall clock and an 8 GB
  peak-RSS ceiling. It did not fire in any run.
* **SR7**: verdicts are computed inside the run, from a metric set fixed in
  code before any verdict is reachable.

## 5. Protocol deviations

### D-1 — inference policy (UPWARD, structural, Coordinator-authorised)

The handoff requests `executor-implementation` with `fallback_allowed: false`
and `degraded_allowed: false`. On this worktree
`python3 -m orchestration.adapter resolve --role executor` resolves that policy
to `anthropic:claude-sonnet-5` (effort medium). The model that actually
answered is `claude-opus-5`.

The cause is **structural, not discretionary**: every `.claude/agents/*.md`
carries `model: inherit`, so this runtime cannot honour a per-role model
binding at subagent level at all. CLAUDE.md's model-policy note prescribes the
remedy as process-level (launch the session through
`orchestration.adapter env`); it is a harness change, not an executor one. The
dispatching Coordinator was informed **before any compute was spent** and
authorised proceeding with the deviation recorded.

Recorded as `protocol_deviation`, never as a satisfied policy, with
`fallback_used: true` in every run manifest. The direction is **upward**, and
that **must not be cited as strengthening any result**: a more capable model
does not raise the claim tier, does not widen scope, and does not license a
conclusion the contract would otherwise deny. Nothing else was changed because
of it — no threshold, scope, budget, stopping rule or metric moved.

The claim that no reported number depends on model identity is made
**checkable, not asserted**: every number comes from the exact symbolic
computation in the pinned module, re-executable with the recorded commands. The
steps that turned on model *judgement* rather than exact computation are named
individually in `manifest.run.inference.model_judgement_steps` — the choice of
backends, the choice of the committed record bound as the census reference, the
definitions selected for affine degree and for the Koszul indicator, and the
choice of `deglex` as the second monomial order. None of these is a measured
value.

### D-2 — second backend, and a disagreement with the precondition probe

The handoff records the dispatching session's probe as finding Macaulay2,
standalone Singular and Magma absent. **This run's own probe disagrees on two
points**, recorded here as the handoff directs:

1. **msolve 0.9.5 IS present** at `/opt/homebrew/bin/msolve` and works through
   Sage (`algorithm='msolve'`). It is a genuine third-party engine
   (Berthomieu, Eder, Safey El Din) sharing no code with Singular, and it is
   used here as **backend B**.
2. A standalone `Singular` binary **is** present inside the Sage tree at
   `/var/tmp/sage-10.9-current/local/bin/Singular`. It is the same engine as
   libsingular, so it is **not** an independent backend and is not used as one.

Macaulay2, Magma and giac are confirmed absent, so there is **no second
off-the-shelf engine for minimal free resolutions** on this host. Graded Betti
numbers are therefore cross-checked by an independent **route** rather than a
second engine: **backend C** computes `beta_{i,j} = dim Tor_i(S/J,k)_j` as the
homology of the Koszul complex on `x0..x3` tensored with `S/J`, using SymPy's
Buchberger for the Groebner basis and normal forms and a local GF(p) Gaussian
elimination for the ranks. No Singular code is on that path. It reproduced
Singular's Betti table exactly on all 30 cross-check curves.

Whether that discharges control **C-BACKEND** in full for the Betti family is a
**reviewer judgement, not the executor's**, and is flagged as such in
`backend-provenance.json:resolution_backend_limitation`.

### D-3 — volcano covariate not computed

The contract states it does not rebuild the 2-volcano, and the committed
reference supplies only the level **histogram** `{0:3, 1:9, 2:18, 3:36, 4:72}`,
not per-curve levels. The secondary metric *contingency table of each primary
invariant against true 2-volcano level* is therefore reported as
`not_computed`, and the tail-check listing of deviating curves carries
`true_volcano_level: "not_computed (deviation D-3)"` rather than an imputed
value. The computable covariate `two_torsion_x_count` (from the committed,
unedited `harness/exp_icinv.py`) is recorded per curve instead. This is a
recorded gap, not an imputation.

### D-4 — defective cross-check predicate in RUN-ICINV-geom-m3, superseded

`RUN-ICINV-geom-m3` compared msolve's set of `F_p`-rational `x3` values against
the number of **degree-1 factors of the elimination polynomial**. Those are
different quantities: a rational root of the elimination polynomial need not
extend to an `F_p`-rational point of the variety. The predicate therefore
reported `backend_B_all_agree: false` on 14 of 30 cross-check curves where
msolve and Singular in fact agree exactly — verified directly, e.g. for
`(a,b) = (148, 2766)` both engines return 0 `F_p` points while the elimination
polynomial `x3^3 + 148 x3 - 1235` factors as `(x3-615)(x3^2+615x3-1722)`.

This is an `implementation_error` in one derived agreement flag. It affects no
primary invariant: every primary value in that run agrees with the corrected
run. Run records are immutable, so the defective run was **not edited**. It is
retained, reported as **invalid/superseded**, and replaced by a new run ID,
`RUN-ICINV-geom-m3-v2`, in which the predicate compares like with like — msolve's
`F_p` point count and `x3`-value set against Sage/Singular's `variety()` on the
same ideal. Backend A now records `fp_rational_points` and
`fp_rational_x3_values` for that purpose.

## 6. Controls, and how each was discharged

| Control | How | Where |
|---|---|---|
| C-CONTROL-SET | 138 random ordinary curves at p = 4001, traces != 30, identical pipeline; exact multiset comparison, **no p-value anywhere** | `control-set-invariants.json`, `verdict.json:per_family` |
| C-GAUGE | every invariant recomputed on `(u^4 a, u^6 b)` for a recorded per-curve `u` | `gauge-recheck.json` |
| C-BACKEND | msolve 0.9.5 on the cross-check subsample; Betti by the independent Koszul route (see D-2) | `backend-crosscheck.json`, `backend-provenance.json` |
| C-ORDER | dimension, degree, Betti table and regularity recomputed under `deglex` on the subsample | `backend-crosscheck.json:second_order_backend_A` |
| C-KOSZUL | regular-sequence indicator reported per curve, for class and control | `koszul-indicator.json` |
| C-CENSUS | re-emitted enumeration vs the sha256-bound committed record, plus the Hurwitz-Kronecker certificate | `class-census.json` |
| C-SUPPORT | symbolic re-derivation of 13 / 9 / 10 in a separate CAS before any class-wide computation | `support-derivation.json` |

Cross-check subsample selection was fixed in code before any verdict was
reachable: every curve realising a distinct value of any family, in either set,
plus filler to exceed the contract's minimum of 20.

## 7. Compliance ceilings

`claim_tier: toy`, `sota_delta: 0`, no ECDLP claim in either direction, no
p-value, no null-object test, no permutation test and no dispersion statistic
anywhere in the output. Scope is exactly p = 4001, t = 30,
D = -15104 = -59 · 16^2, arities m ∈ {3,4}, `degrevlex`, the declared
x0-homogenised standard grading, and the f_V-free ideal. **No transfer is
claimed** to any other prime, class, arity or grading, nor to the deployed
f_V-bearing formulation the harness actually runs — by the contract's own
argument, removing f_V is what makes the measured object a functional of the
curve, and is equally what makes the result non-transferable to that
formulation's solving time.
