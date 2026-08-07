# EXP-ICINV-4d33aa — implementation note

Executor: TASK-20260807-3414fc (GOAL-ENDO-001, BATCH-aa267f).
Contract: `experiments/EXP-ICINV-4d33aa/specification.yaml` (status `approved`,
`approved_by: coordinator`, `approved_at: 2026-08-07`). The contract is FROZEN;
nothing below changes a prime, a factor-base size, a target count, a seed, a
threshold or a terminal-state rule.

This note records **what was built, what deviates from the contract, and why**.
It contains no interpretation of the result.

## Modules

- `harness/exp_icinv_fullgroup.py` — measurement module. All frozen parameters
  are module constants copied verbatim from the contract, so any change to one
  is a reviewable diff rather than a command-line flag.
- `harness/run_fullgroup.py` — stage driver and run-record writer.

`harness/exp_icinv.py` **is not edited**. Every run checks this mechanically:
`fg.committed_file_digest()` compares the worktree file's SHA-256 against
`git show HEAD:harness/exp_icinv.py` and the run refuses to start if they
differ. Recorded in every run's `raw.integrity.exp_icinv_digest`
(`byte_identical: true` in all runs).

`exp_icinv.permutation_null` (NULL-C) is never used. `fg.self_audit_no_null_c()`
scans the source text of both new modules for the call pattern (assembled at
runtime so the auditor does not count itself) and the run refuses to start if
the count is non-zero. Recorded in every run's `raw.integrity.null_c_audit`
(`call_sites_total: 0` in all runs).

## Contract requirements implemented mechanically, not by assertion

| Requirement | Mechanism | Where recorded |
|---|---|---|
| Sum set computed **once** per (curve, fb_size), shared by every arm/seed/T | `measure_curve_all_arms` holds one sum set per (curve, fb_size) and scores every arm against it; a module counter tags each enumeration and every measurement row carries its tag | `sumset_sharing` in each sweep run + the `sumsets` table in `per-curve-measurements.json` |
| Arm A0 calls the committed sampler | `targets_A0` is a one-line call to `exp_icinv.targets_uniform` | `per-curve-measurements.json`, `committed_hit_checks` |
| Arm A support certificate | `<G>` built by repeated addition (closes on O after exactly `gen_order` steps), contained in the independently enumerated point set, `gen_order == n2` | `coverage-certificates.json` |
| The re-derived base point IS the committed function's | every returned target checked for membership in `<G>`, plus element-by-element prediction of the first 200 draws per (curve, seed) | `committed_sampler_replication_verified` |
| Arm B support certificate | set equality of `{[u]P + [v]G2}` against the independently enumerated `E(F_p)` | `coverage-certificates.json` |
| Arm C support certificate | image of the doubling homomorphism, size checked against `#E/2`, index certified as `#E[2] = 1 + r = 2`, and (when `n1 = 1`) cross-checked against `<[2]G2>` built by repeated addition | `coverage-certificates.json` |
| Group structure `(n1, n2)` | proposed cheaply (lcm of 40 point orders), then CERTIFIED: `ord(G2) = n2` exactly, `[n2]P = O`, `n1 | n2`, and `{[u]P + [v]G2}` equals `E(F_p)` as a set | `coverage-certificates.json` |
| SR1 stage gate | stages 2 and 3 refuse to start unless this prime's stage-1 record exists on disk and reports `premise_failed: false`; the dependency's SHA-256 is recorded | `raw.dependencies` |
| SR2 null-first | stage 3 refuses to start unless this prime's stage-2 (NULL-R) record exists on disk; its SHA-256 is recorded | `raw.dependencies` |
| SR3 baseline gate | evaluated and written **before** any Arm B statistic is computed; on failure the Arm B aggregate is not produced and the driver halts | `baseline-reproduction.json` |
| SR6 no outcome shopping | the terminal state is computed by `evaluate_decision_rule` inside the decision run; the metric set is identical whatever fires | `decision-rule-evaluation.json` |

The point set of each curve is enumerated **independently of `toycurve.lift_x`**
(a full inverted square table rather than sympy's `sqrt_mod`), and the resulting
count is cross-checked against `isogeny_class.trace_of_frobenius` — a third,
character-sum path. For the first three curves of every class the two
enumerations are additionally compared for set equality
(`liftx_agreement_sample`, all `true`).

## Protocol deviations

Every run manifest carries this list verbatim in `run.protocol_deviations`.

### D1 — the primary-class tie-break (material)

The contract states the primary rule twice and the two statements disagree:
"maximum member count; ties broken by smallest |t|, then smallest t" **and**
"IDENTICAL to `harness/run_saturation.py:run`". `run_saturation` sorts
`(len(v), t)` with `reverse=True`, so ties break to the **largest** t. At all
three required primes the largest ordinary class is tied between `t` and `-t`
(quadratic twists have equal class size), and the two readings select different
classes with different group orders:

| p | run_saturation picks | contract-literal text picks |
|---|---|---|
| 2003 | t = +36, #E = 1968 | t = −36, #E = 2040 |
| 4001 | t = +30, #E = 3972 | t = −30, #E = 4032 |
| 6007 | t = +8, #E = 6000 | t = −8, #E = 6016 |

**Resolved as `run_saturation.run`'s actual idiom**, reproduced verbatim in
`select_classes()`. This is forced rather than chosen: the committed
EV-ENDO-10109d runs measured t = +30 (order 3972) and t = +8 (order 6000), and
the contract's BLOCKING baseline-reproduction control requires Arm A0 to
reproduce those numbers — which is only defined on the same class. Under the
literal tie-break text SR3 would be unsatisfiable by construction at both
baseline primes. The choice is on class identity only, was fixed before any rate
or variance was computed, and is applied identically at all three primes.
Reported to the Coordinator as a contract ambiguity; the frozen file is not
edited (AGENTS.md rule 4).

The same tie-break (largest t) is used for the NULL-R rule, for which the
contract states no tie-break at all. Selected NULL-R classes: p=2003 t=+6
(#E=1998, n=54), p=4001 t=+72 (#E=3930, n=72), p=6007 t=+22 (#E=5986, n=112).
All have #E ≡ 2 (mod 4) and ≥ 30 members, so no odd-order substitution was
needed at any prime.

### D2 — the committed p=6007 baseline was measured at different parameters (material)

The contract freezes T = 400 and the grid {4,5,6,7,8,9,10,11,12,13,15,18,22},
and H-ICINV-6c7920 asserts these are "byte-identical to … the parameters of
RUN-ICINV-p4001-fixed and RUN-ICINV-p6007-fixed". They are not: the committed
p=6007 run used **T = 500** and the grid {5,6,7,8,9,10,11,12,14,17,21}. p=4001's
committed run does match the frozen grid exactly.

**Resolved as: run the frozen grid as written** (SR4 forbids adding a row or a
target count without an amendment). Arm A0 at p=6007 is therefore a
re-measurement at a different T rather than a bit-exact reproduction.
`baseline-reproduction.json` marks each row's `committed_counterpart_exists` and
records the parameter mismatch explicitly. The frozen ±0.25 tolerance on the
operating row is applied exactly as written, against a committed 1.591 that was
measured at T = 500. No threshold was adjusted and no committed run was
re-scored.

### D3 — SR3 versus the sum-set sharing requirement (procedural)

SR3 says "do not run Arm B" if the Arm A0 gate fails, while
`inputs.cost_sharing_requirement` makes recomputing the sum set per arm an
invalidation rule. Both cannot be honoured literally: deferring Arm B needs
either a second sum-set pass (invalid) or holding every sum set in memory (about
1 GB at p=6007, against a 4 GB cap).

**Resolved as:** one shared pass scores every arm, and the baseline gate is
evaluated and written **before any Arm B statistic is computed, aggregated or
reported**. On a gate failure the run is written `invalid` with the defect, no
Arm B aggregate is produced, and the driver halts before any further prime.

### D4 — origin/main merge (procedural)

The handoff asks the Executor to merge new `origin/main` changes into the
branch; `agents/executor.md` forbids the Executor from merging main, pushing, or
opening PRs. **Resolved as:** `origin/main` was fetched and compared and the
comparison is recorded in every run manifest (`raw.git_context`); no merge was
performed. At the time of every run the branch was **0 behind / 10 ahead** of
`origin/main`, with `merge-base == origin/main = 2d0c26c71f4a729ce70bf9764fd604aba3a6eacf`,
so no merge was needed.

### D5 — two nulls for the stratum ratios (reporting)

The STEP-2 variance identity is an identity only when VR₁ and VR₃ are taken
against the **pooled** null v = μ̄(1−μ̄)/T, whereas the controls block requires
each stratum's acceptance band to come from that cell's **own** df and mean.
**Resolved as:** both are computed, reported side by side and labelled
(`own_null` and `ratio_pooled_null`). The 1e-9 identity check uses the pooled-null
version; the per-cell verdicts and bands, and the S3 comparison, use the own-null
version, which is what `variance_ratio_by_r_stratum` denotes in the metrics block.

### D6 — which seed and T feed the decision rule (reporting)

The frozen rule indexes VR by `[arm][prime][class][density][seed]` but never says
which seed or target count feeds F_p. **Resolved as:** F_p and the S1/S2/S3 rows
are computed at the contract's own `target_count_primary = 400` and at seed
20260807 — the first frozen seed and the one the bit-exact baseline requires.
F_p at all three seeds and all three target counts is reported in
`sensitivity_all_seeds_and_T` in every case, whatever the verdict.

## Other implementation facts worth a reviewer's attention

- **Arm C's hash tag** (`"{seed}:pl:{i}"`) is this module's choice; the contract
  freezes only the `fg1`/`fg2` tags for Arm B and leaves Arm C's stream
  unspecified.
- **Arm C's planted half** is the first ⌊n/2⌋ members of the NULL-R class in
  ascending (a, b) order — an arbitrary but declared and deterministic half, as
  the contract requires. The other half is measured under Arm B, and the
  "planted" cell is the pooled mixture; the restricted half alone is reported
  separately.
- **Index-stream uniformity.** u and v are `sha256(...) mod n`, non-uniform by
  under 2⁻²⁴⁰ at these moduli. Declared by the contract, restated here, not
  hidden.
- **A scratch validation execution** of stages 1–3 at p = 2003 was run in a
  temporary directory (not under `experiments/`) before the official runs, to
  test the driver end to end. It is deterministic and produced the same numbers
  as the official p=2003 records. It is recorded here for completeness; no
  parameter, threshold or code path was changed in response to its numbers.
- **`runner.write_run` is not used.** It emits only the six core artifacts and
  hardcodes `requested_policy: executor-terra`, and `harness/runner.py` is listed
  under `reused_unmodified`, so it could not be edited to carry the handoff's
  policy or the five extra blocking artifacts. `run_fullgroup.write_run_package`
  writes the manifest instead, reusing `runner.environment()` and
  `runner.git_state()` so environment and revision come from exactly the
  committed code every other run in this repository uses. Like `write_run`, it
  refuses to overwrite an existing run directory.
- **Certificate kind is `none`**, explicitly: no discrete log is solved and no
  factor-base relation is claimed. The exact *support* certificates are controls
  and live in `coverage-certificates.json`, each verified against an
  independently enumerated point set.

## Run inventory

| Run ID | Stage | Prime | Class role |
|---|---|---|---|
| `RUN-ICINV-fg-stage1-p2003` | 1 | 2003 | premise check (both classes) |
| `RUN-ICINV-fg-stage1-p4001` | 1 | 4001 | premise check (both classes) |
| `RUN-ICINV-fg-stage1-p6007` | 1 | 6007 | premise check (both classes) |
| `RUN-ICINV-fg-nullr-p2003` | 2 | 2003 | NULL-R (matched null + planted) |
| `RUN-ICINV-fg-nullr-p4001` | 2 | 4001 | NULL-R (matched null + planted) |
| `RUN-ICINV-fg-nullr-p6007` | 2 | 6007 | NULL-R (matched null + planted) |
| `RUN-ICINV-fg-primary-p4001` | 3 | 4001 | primary |
| `RUN-ICINV-fg-primary-p6007` | 3 | 6007 | primary |
| `RUN-ICINV-fg-primary-p2003` | 3 | 2003 | primary |
| `RUN-ICINV-fg-decision` | decide | all | aggregate terminal state |

p = 10007 is a permitted stretch only ("not required and its absence is not a
defect") and was **not run**; the decision run records that explicitly.
