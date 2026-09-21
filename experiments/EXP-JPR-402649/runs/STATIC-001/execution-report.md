# Execution report — EXP-JPR-402649 / STATIC-001 (zero-run derivation package)

Task TASK-20260902-19eacf, batch BATCH-67be49, hypothesis H-JPR-5e33d6,
question RQ-ECDLP-160d89, contract experiments/EXP-JPR-402649/specification.yaml
(status approved, approved_by coordinator, DEC-20260902-52868a).

**certificate kind: none; no run occurred.** Zero runs occurred, no code was
written, no curve was generated or sampled, no point was sampled, no ECDLP
instance exists. The package contains no manifest.yaml, command.txt,
environment.json, stdout/stderr log, or raw-result.json, by contract. The
N = 23, w = 5 fixture is a hand enumeration (derivation.md 0.4). No
mechanical arithmetic check was performed by machine; every number in the
package was computed by hand in the text.

Claim ceiling honoured: derivation tier only; no ECDLP evidence, no speedup,
no sub-rho claim, no closure, no lower bound, no status change of any
hypothesis, experiment, question, or goal. This report records observations;
whether the hypothesis is supported or refuted is for /review-evidence.

## Stage-by-stage

- **Stage 0 (controls, hard gate).** T1 written in full with the dihedral
  step (derivation.md 0.1, Steps 1-6, boundary widths, complementation
  extension confirmed). CTRL-COMPOSITE-COSET: FAILS at Step 1 (distinct
  translates; stabilizer H), consequently Steps 2 and 4 — as forced.
  CTRL-XOR-LEX: SILENT; prime-order row fails, Step 1 fails (stabilizer is
  D), additivity false; join-core rows only — as forced. CTRL-ZN-IDENTITY:
  rho = -id, a = 1, c = 0, nu = id recovered; T2 zero defect; T3 vacuous; the
  23 intervals and 23 translates enumerated, coincide as sets, rotation by
  -T — as forced. NULL-1/NULL-2: soundness 1/L, EXPECTED TIME N (JPR-REV-4
  wording), T1 not applied to NULL-2. Pareto rows as controls only, no
  domination. Gate passed; stopping rule 1 did not fire.
- **Stage 1 (T2, tau_0, HEUR-001).** Steps A, B, Markov and the 3*delta union
  bound written with explicit constants (derivation.md 1.1-1.3). The
  translate-comparison step is NOT available as sketched: the argument is
  circular (a translate of a nu-interval has no start); what is derived is
  the approximate translation-invariance (C1) and the O(w) fallback (FB),
  whose scope is the emitted sound pairs only (1.4). tau_0 derived with its
  chain, conditional on the missing lemma (TC): 0.0238 ~ 1/42, inside
  (0, 1/6), below the predicted order 1/20 by a factor ~2 (1.7,
  threshold.yaml); prediction not adjusted. HEUR-001 second-moment bound
  written with the shared-leaf term charged (constant 3, order unchanged)
  (1.8). Unexpected observation (U1) recorded (1.5).
- **Stage 2 (T3 lemmas).** Lemma (i): identity, extraction, exclusion of
  xi_0 = 0 (exact for bijective keys; the contract's |D| route does not
  close for keys with ties, carried as a hypothesis), uniqueness with the
  spectral gap. Lemma (ii): transfer, coefficients at xi_0 and xi_0*x, query
  cost. Lemma (iii): two SFT calls, Chebyshev isolation, division,
  verification, retry bookkeeping; conditional on AGS-1, stated verbatim in
  external-obligations.yaml, recalled/unopened.
- **Stage 3.** HEUR-002 obligation stated; HNP-ERR-1 written verbatim;
  nothing claimed.
- **Stage 4.** Placement on the 3f0f4b surface recorded (exponent 0 off the
  surface, conditional; realized position: no attack); dominated_by and
  sota_delta restated with labels; uncovered primitives listed with reasons.

## Success-criterion checklist (contract success_criterion (1)-(8))

| # | criterion | outcome | cited artifact section |
|---|---|---|---|
| 1 | three controls as forced, failing hypotheses named, rho = -id, N = 23 fixture written | PASS | derivation.md 0.2, 0.3, 0.4; stage0-controls.yaml |
| 2 | explicit C and explicit constant in delta; translate-comparison written in full OR O(w) fallback declared | PASS (fallback declared; scope: emitted sound pairs only, not 1 - 3 delta of all pairs — recorded as observation A1) | derivation.md 1.3, 1.4; threshold.yaml constants |
| 3 | tau_0 derived with chain, strictly in (0, 1/6) | PASS-CONDITIONAL: value 0.0238 in (0, 1/6) with full chain; chain's premise (all-pairs T2) rests on undischarged internal lemma (TC) | derivation.md 1.7; threshold.yaml |
| 4 | three lemmas written; lemma (iii) obligation verbatim, recalled/unopened | PASS | derivation.md Stage 2; external-obligations.yaml AGS-1 |
| 5 | HEUR-002 obligation stated, not claimed | PASS | derivation.md Stage 3; external-obligations.yaml HNP-ERR-1 |
| 6 | uncovered join primitives listed | PASS | uncovered-primitives.yaml; derivation.md Stage 4 |
| 7 | placement on 3f0f4b surface recorded | PASS | surface-placement.yaml; derivation.md Stage 4 |
| 8 | NULL-1/NULL-2 expected time N; Pareto rows no domination | PASS | derivation.md 0.5, 0.6; stage0-controls.yaml |

The contract notes that (1)+(2) without (3) is a valid negative derivation
result. Here (3) is met numerically but conditionally; the classification
of that outcome is left to review.

## Falsification criteria

- **F1** (T1 concludes a log order on the composite or XOR object): NOT
  triggered; both fail at Step 1 with the stabilizer named.
- **F2** (injective nu on a prime-order group, translation-invariant
  interval system, not a log order): NOT triggered; none exhibited, and T1's
  derivation excludes one at derivation tier.
- **F5** (tau_0 excludes every eta compatible with Theta(L) output): NOT
  triggered; eta = eta' = 0 at w' = w = N^(2/3) is admitted.
- **M3** (independent derivation finds the cascade costs N^c): NOT triggered
  as stated: under (TC) and AGS-1 the cascade is (log N)^{O(1)}. Recorded
  alongside: the unconditional consequence (U1) yields only a
  N^(-1/6)/log N coefficient, under which an SFT-based cascade would cost
  N^Theta(1); this bears on whether T3's hypotheses are available, not on
  the cascade's cost under them.
- F3, F4: not applicable (no key exhibited; no source opened). F6: not
  applicable (no key exhibited; nothing routed to review-breakthrough).

## Anomalies and unexpected observations (recorded, none discarded)

- **A1.** The translate-comparison step of T2 is circular as sketched; the
  all-pairs form of T2 is not derived; the O(w) fallback holds only on
  emitted sound pairs, contrary to the contract's expectation that it still
  gives N^(-1/3+o(1)) precision on most pairs (derivation.md 1.4).
- **A2.** The frozen shape's two constants (C and c_1) cannot both be
  absolute from a first-moment argument; C*delta = 2/(1-eta) is fixed, and
  tau_0 emerges from the non-vacuity limit of the Markov parameter
  (derivation.md 1.3, 1.7).
- **A3.** Unconditional weak Fourier consequence (U1): soundness of a
  bijective key forces a coefficient >= (w'/w) sqrt(w/N)(1-eta-w/N)/(2+ln w')
  for some dilate e(m nu/N), m != 0, at a frequency xi != 0 (derivation.md
  1.5). Not requested; recorded under AGENTS.md rule 8.
- **A4.** Exclusion of xi_0 = 0 via |D| = Theta(N/L) does not close for keys
  with ties; it is exact for bijective keys (lemma (i)).
- **A5.** With ties, the width form of size matching does not imply the set
  form the derivation needs (derivation.md 1.6).
- **A6.** Derived tau_0 is ~1/42, about half the predicted order 1/20;
  inside the frozen interval; attributed to c_1 = 2.

## Protocol deviations of this attempt

None. Stages executed as specified; write scope respected; no source opened;
no git invoked; no code, curve, sample, or run.

Process note (not a deviation of this attempt): a prior attempt at this task
was terminated when a single response exceeded the 64,000-output-token cap
while reading all inputs in one pass; it wrote nothing. This attempt read
inputs one at a time and wrote derivation.md in three parts.

## Stopping rules (all four checked)

1. Wrong Stage 0 disposition: did not fire (all as forced).
2. Code / curve sample / run needed: did not fire.
3. Recalled source needed to SUPPORT a conclusion: did not fire; AGS-1,
   HNP-ERR-1, BSG, Green-Ruzsa, Kazhdan, Boneh-Venkatesan, Hoeffding are
   pointed at as obligations or not used; Chebyshev and Parseval are
   re-derived inline.
4. All five stages and this report written: fired (normal termination).

## Completion gate G1-G11 (handoff)

G1 met; G2 met (fallback declared with scope); G3 met (value in interval,
reported with its conditionality, not repaired); G4 met; G5 met; G6 met;
G7 met; G8 met; G9 met (seven files only, no run-shaped file; verified by
`ls` of the package directory, the only Bash use); G10 met (every external
statement carries provenance recalled with verified_by null); G11 met (this
report, inference block below, zero-run statement above).

## Sources actually read (all internal, provenance internal)

specification.yaml; ledger/handoffs/TASK-20260902-19eacf.yaml; the
BATCH-67be49 dispatch_queue.json task card; H-JPR-5e33d6; IDEA-20260901-a66d70;
DEC-20260902-52868a; RQ-ECDLP-160d89; AGENTS.md (core rules, artifact
policy); agents/executor.md; docs/claims-and-verification.md (claim tiers,
refutation artifacts, heuristic-conditional claims); docs/inventor-protocol.md
section 8; claim/mechanism/target sections of IDEA-20260829-3f0f4b,
IDEA-20260829-390ccc, IDEA-20260829-7169d6, IDEA-20260807-df906f. No external
source opened; no KB query (none required by the contract).

## Inference block

- requested_policy: executor-implementation
- requested_reasoning_effort: medium
- resolved_model_id: claude-fable-5-1 (as reported by the runtime to this
  session; not probe-verified)
- model_verified: false
- fallback_used: false
- degraded_requirements: []
- bedrock_used: false

## execution_report (agents/executor.md schema)

```yaml
execution_report:
  experiment_id: EXP-JPR-402649
  implementation_commit: 32fa633bcf439640cb9ea5a55f071b8bb1d64451
  implementation_commit_note: >-
    HEAD of branch claude/elliptic-curve-goals-0ym3o3 read from .git/HEAD and
    .git/refs/heads (git not invoked per task instruction); dirty-tree state
    not determinable without git; nothing was implemented, so this binds the
    inputs' revision only. The snapshot task TASK-20260902-69de74 binds the
    package by content hash.
  protocol_deviations: []
  runs:
    completed: []
    invalid: []
    failed: []
  runs_note: 'maximum_runs 0; zero runs by contract; STATIC-001 is a written package, not a run'
  certificate:
    kind: none
    note: 'no run occurred; no solve or relation claimed'
  observations:
    - 'Stage 0: composite fails at Step 1 (stabilizer H); XOR silent, fails at Step 1 (stabilizer D), prime-order row fails, additivity false; identity returns rho = -id, T2 defect 0, T3 vacuous; N = 23 fixture enumerated.'
    - 'Stage 1: constants a_R = eta_prime + 2 eta_R/(1-eta), delta = 1/K, c_1 = 2/((1-eta)(1-eta_prime)), C_fb = max(1, w_prime/w); translate-comparison NOT derivable as sketched; fallback (FB) on emitted sound pairs only.'
    - 'tau_0 (frozen prediction (0, 1/6), order 1/20): derived 0.023826 ~ 1/42, inside (0, 1/6), conditional on internal lemma (TC); prediction not adjusted.'
    - 'HEUR-001 second-moment bound: Var <= 3L at p = 1/L, relative deviation O(L^(-1/2)); shared-leaf term changes the constant only. No conclusion drawn.'
    - 'Stage 2: lemmas (i)-(iii) written; xi_0 = 0 excluded exactly for bijective keys, hypothesis for ties; AGS-1 obligation verbatim, recalled/unopened.'
    - 'Stage 3: HEUR-002 obligation and HNP-ERR-1 stated; nothing claimed.'
    - 'Stage 4: exponent 0 off the 3f0f4b surface, conditional; realized position no attack; 11 uncovered primitives listed.'
  anomalies:
    - 'A1 translate-comparison step circular as sketched; all-pairs T2 not derived.'
    - 'A2 C and c_1 tied by C*delta = 2/(1-eta); not both absolute.'
    - 'A3 unconditional weak coefficient (U1) of size N^(-1/6)/log N for some dilate of the key.'
    - 'A4 xi_0 = 0 exclusion via |D| = Theta(N/L) does not close for keys with ties.'
    - 'A5 width-form size matching insufficient with ties.'
    - 'A6 tau_0 about 1/42, half the predicted order; inside the frozen interval.'
    - 'Process note: prior attempt terminated at the output-token cap; wrote nothing.'
  artifact_paths:
    - experiments/EXP-JPR-402649/runs/STATIC-001/derivation.md
    - experiments/EXP-JPR-402649/runs/STATIC-001/stage0-controls.yaml
    - experiments/EXP-JPR-402649/runs/STATIC-001/threshold.yaml
    - experiments/EXP-JPR-402649/runs/STATIC-001/external-obligations.yaml
    - experiments/EXP-JPR-402649/runs/STATIC-001/uncovered-primitives.yaml
    - experiments/EXP-JPR-402649/runs/STATIC-001/surface-placement.yaml
    - experiments/EXP-JPR-402649/runs/STATIC-001/execution-report.md
  inference:
    requested_policy: executor-implementation
    requested_reasoning_effort: medium
    resolved_model_id: claude-fable-5-1 (runtime-reported; not probe-verified)
    model_verified: false
    fallback_used: false
    degraded_requirements: []
    bedrock_used: false
  executor_assessment:
    protocol_complete: true
    data_quality: limited
    data_quality_note: 'derivation tier; the all-pairs form of T2 and hence tau_0 are conditional on the undischarged internal lemma (TC); classification of that outcome belongs to review'
    requires_rerun: false
```
