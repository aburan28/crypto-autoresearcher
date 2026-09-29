# TASK-20260814-c87a24 — THE LEAD PRODUCER

    goal / batch    GOAL-MLKEM-005 / BATCH-a5b13c
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      TASK-20260814-487c0f
    review_required true
    archived_by     TASK-20260814-07bfae
    budget          3600 s HARD CAP (wall clock), 2 GB, 1 run.
                    Component-summed, not a round-number guess — see
                    budget_justification below.
    claim tier      DERIVATION (C1) / MEDIUM (C2) — NOT TOY

## What it must do, in order

**(1) SECTION 1 — infrastructure re-verification, performed fresh in this
session.** Clone `lattice-estimator` at pin
`3e48ef421ec256afddb3e7d2249a77eab6e9ba12` (network required). Run
`tools/sage_free_estimator/known_answer_control.py` and confirm exit 0:
`primal_bdd` must reproduce the archived Sage reference for Kyber512/768 at
**exact** delta 0.0, and `dual_hybrid(fft=True)` within its own declared
`1e-9` tolerance. **A non-exact `primal_bdd` delta halts this entire batch at
Stage B** — report `T-CIPHNOISE-NODATA` branch (b) and stop; Stage A is
unaffected either way. Independently confirm `estimator.schemes.Kyber512/
768/1024` carry `q=3329`, `k in {2,3,4}`, and CBD parameters matching FIPS
203 Table 2 (`eta1 in {3,2,2}`, `eta2=2`). **Before constructing any modified
instance**, independently determine and REPORT exactly what the installed
`estimator`'s `LWEParameters`/`NoiseDistribution` API supports for (a) an
explicit finite non-parametric-family error distribution, and (b) a reduced
sample/equation count relative to the base `Kyber1024` object. If the API
cannot represent either within budget by any construction you can build and
defend, that is INFRASTRUCTURE SIGNAL for Stage B specifically — report
`T-CIPHNOISE-NODATA` (b) and stop Stage B there; Stage A stands
independently. **No Branch-B hand-rolled cost-model contingency is
commissioned or attempted.**

**(2) STAGE A — C1, the exact fibre census.** Write ONE small,
self-contained script (no external dependency, pure Python/numpy integer
arithmetic) that, for each `d` in `{4, 5, 10, 11, 12}`, computes
`Compress_d(x)` for every `x` in `0..q-1` under the EXACT FIPS 203
definition. **State explicitly, before reporting any census number, which
rounding convention FIPS 203 specifies and which your own implementation
uses** — checked against `inputs/MLKEM-DUAL-SOURCES-20260802`, never
assumed. Group residues by codeword and report the exact fibre-size
histogram. For `d_u=11`, additionally compute the
`Decompress_11(Compress_11(x))` roundtrip-agreement count. For `d=12`,
additionally compute `I(delta;bin)` and confirm it is exactly zero because
every fibre is a singleton — state that the census itself, not a separate
Monte Carlo estimate, already forces this. Read `F(a)` (singleton count at
`d_u=11` exactly 767, `d_u=10` exactly 767 fibres of size 3 and 257 of size
4) and `F(d)` (the `d=12` gate returns every fibre a singleton with
`I(delta;bin)=0` exactly) directly from the census. **If `F(a)` fails, the
whole package halts there. If both clear, Stage A is complete and stands
regardless of what Stage B does.**

**(3) STAGE B — C2, the block-size readout (gated on `F(a)`/`F(d)` clearing
and section 1's API check succeeding).** For each of ML-KEM-512/768/1024,
read `beta(key-side)` directly from `primal_bdd(schemes.KyberXXX,
red_cost_model=RC.MATZOV)`. Build and call `primal_bdd(PARAMS,
red_cost_model=RC.MATZOV)` for every DEFINED `(parameter set, model)` pair:
**M0** (population-average compression-error distribution, full dimension,
every set); **M1** (exact class-correct mixture — probability `767/3329` the
coordinate's noise is `Xe` alone, probability `2*1281/3329` `Xe` convolved
with the doublet-class-only compression-error distribution — full
dimension, every set); **M2** (ML-KEM-1024 ONLY — retain only the singleton
coordinates with noise `Xe` alone, drop every doublet coordinate; VACUOUS
and `NOT_APPLICABLE` for ML-KEM-512/768, never missing or failed). Report
the exact M1 construction (support, probabilities, resulting variance) and
the exact M2 reduced-dimension convention used. Identify whatever tunable
constant `RC.MATZOV` (or the core-SVP-bit conversion) actually exposes and
print a small sensitivity sweep bracketing it — or state plainly that none
is exposed and OMIT the table.

**(4)** Report, per parameter set: `beta(key-side)`; `beta(M0)`, `beta(M1)`,
`beta(M2)` where defined; `beta(best of M0/M1/M2)` = the MAXIMUM of the
defined values; `beta(best) - beta(M0)` in bits; `beta(ciphertext-side,best)
- beta(key-side)` in bits. Check `HEUR-MLKEM-11aabf-1`'s own `F(b)`
(`beta(M2) >= beta(M0)` at ML-KEM-1024) FIRST and independently of the
CLOSED/OPEN question, reporting it regardless of which branch fires. Report
the per-set CLOSED/OPEN verdict and the aggregate (CLOSED-ALL or
OPEN-AT-LEAST-ONE). Read the termination branch (`T-CIPHNOISE-NODATA /
-CLOSED / -OPEN / -MIXED`) off PREREG-7 section 3.6's frozen precedence —
NODATA dominates and fires alone; among the rest, MIXED fires whenever the
three sets disagree, CLOSED/OPEN fire only when all three agree. Report all
five outcome rows (`R-CN-OUT-0` through `R-CN-OUT-4`) per section 4.

## Absolute constraints

**NO LATTICE REDUCTION OF ANY KIND (fpylll/BKZ/HKZ), ANYWHERE, FOR ANY
REASON.** Every number is either exact integer arithmetic (Stage A) or a
closed-form estimator readout (Stage B). SCOPE: `q=3329`; Stage A `d in
{4,5,10,11,12}`, all 3329 residues; Stage B ML-KEM-512/768/1024 exactly,
`RC.MATZOV` exactly, `primal_bdd` exactly, the pinned estimator commit
exactly. No other cost model, attack, secret/error distribution, real
ML-KEM key/ciphertext/decapsulation call, or timing side channel. CLAIM
TIER STAYS DERIVATION (C1) / MEDIUM (C2) — never a measured attack cost or
a security-estimate revision. Do not touch, reopen or re-score the
hkz/HKZ-independence lineage or `DEC-20260813-9c7353`'s deferred
epsilon-sweep candidate. Whichever branch fires, do not claim it closes
`RQ-MLKEM-001`, says anything about best-of-M ciphertext selection, or
extrapolates beyond the pinned estimator/cost model tested. This task's
outcome does not close, pause or complete `GOAL-MLKEM-005`. Do not change
`H-MLKEM-11aabf`'s status — that is the ledger archive's act. `PREREG-7` is
frozen; do not change a success criterion after seeing an outcome — report
a disagreement as a finding and score the frozen clause anyway. Commit
nothing.

## Budget justification (see the task's own `budget_justification` field
## in `dispatch_queue.json` for the full text)

3600 s hard cap, arrived at by an explicit component sum against
**TASK-20260805-9672b3** (`BATCH-a51f91`)'s MEASURED wall-clock data for
this identical pinned harness and estimator commit — **not**
`EXP-MLKEM-bfdb63`, which despite being named as a precedent in PREREG-7
section 1 point 1 was **never executed** (no runs, no measured timing
anywhere) and so cannot ground a real number. TASK-20260805-9672b3 measured
its known-answer control at ~28 s and a 208-call protocol run at 238.02 s
(peak RSS 0.118 GB). Components here: clone (unmeasured, generously bounded)
≤1200 s; known-answer control ≤120 s; section-1 API-surface exploration
≤900 s (modelled on that task's five preflight probes); Stage A census
≤60 s; Stage B compute (~10-40 estimator calls at the measured ~1.1 s/call
rate) ≤600 s; writeup/manifest overhead ≤600 s. Sum ≤3480 s, rounded to
3600 s.

## Artifacts — NINE PATHS

    tasks/TASK-20260814-c87a24/ciphertext_noise_census.py
    tasks/TASK-20260814-c87a24/ciphertext_noise_readout.py
    tasks/TASK-20260814-c87a24/results_ciphertext_noise.json
    tasks/TASK-20260814-c87a24/ciphertext_noise_writeup.md
    tasks/TASK-20260814-c87a24/command.txt
    tasks/TASK-20260814-c87a24/stdout.log
    tasks/TASK-20260814-c87a24/stderr.log
    tasks/TASK-20260814-c87a24/run_manifest.yaml
    tasks/TASK-20260814-c87a24/environment.json

`ciphertext_noise_writeup.md` must list every path this task wrote, exactly
as this goal's every prior lead producer has done, so the snapshot archive's
change-set-equality check is verifiable. File names are this Coordinator's
suggestion; the executor may adjust them (e.g. splitting or merging the two
`.py` scripts) if it records the actual names used consistently across
`command.txt`, `run_manifest.yaml` and the report, matching this goal's own
established renaming precedent.
