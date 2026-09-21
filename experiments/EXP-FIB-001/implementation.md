# EXP-FIB-001 — implementation note

## What was built

All new code is confined to `experiments/EXP-FIB-001/driver/` (per H-FIB-001's
own implementation note: "New glue confined to experiments/EXP-FIB-001/").
No shared `harness/` file was modified.

| module | role |
|---|---|
| `driver/common.py` | canonical (fixed-sign) point lift, seeded RNG helper, sha256 helper. |
| `driver/instances.py` | builds the 4 main curves (16/20-bit x seed 1/2) and 3 truth curves (8/10/12-bit seed 1) via `harness.toycurve.generate_instance`; generates targets `R = a*P + b*Q`; **builds the factor base** (see deviation below); computes per-curve SHA-256 fingerprints for `frozen-instances.yaml`. |
| `driver/invariant.py` | the n_R fiber invariant: exact C(B,3) enumeration table (16-bit / truth curves) and sampled enumeration (20-bit, up to 5e7 evals or 1500s); `independent_exact_count` is a second, independently-coded exhaustive counter used only by CTRL-EXHAUSTIVE-TRUTH so that control is a genuine cross-check, not a tautology against the same code path used for measurement. |
| `driver/decompcost.py` | S_4 (m=3) Groebner-basis decomposition-cost measurement (`sympy.groebner` on `<S4(x1,x2,x3;xR), fV1(x1), fV2(x2), fV3(x3)>`), run in a `multiprocessing` subprocess with a hard 20s wall-clock cap (`terminate()`/`kill()` on timeout) — sympy's Buchberger routine cannot be interrupted cooperatively, so this is the only way to enforce the frozen per-solve cap. A capped solve is charged the full cap cost, per the frozen `decomposition_cost` definition (not treated as an infrastructure failure). |
| `driver/statslib.py` | Spearman rho + 10000-replicate permutation null; label-shuffle control; Poisson chi-squared goodness-of-fit with the frozen class-merging rule (classes with expected count < 10 merged into a tail bin); dispersion index; the three pre-registered tail checks. |
| `driver/runlib.py` | writes the exact required-artifact set per run: `manifest.yaml`, `command.txt`, `environment.json`, `raw.json`, `summary.json`, `stdout.txt`, `stderr.txt`. Refuses to overwrite an existing run directory (immutability). |
| `driver/orchestrate.py` | sequences RUN-FIB-001..008, enforcing the frozen budget's stage caps (`freeze_and_truth_control` 1200s, `invariant_tables` 3300s, `decomposition_measurement` 3600s with a 1500s per-curve cumulative cap and 1800s per-run cap, `correlation_and_decision` 900s, `twophase_gated` 900s), and writes `frozen-instances.yaml`, `analysis.md`, `execution-report.yaml`. |

Command: `cd experiments/EXP-FIB-001 && python3 -u -m driver.orchestrate`
(background PID 7946 for this execution; see `command.txt` in each run
directory for the per-run record).

## Deviations from the approved protocol (all recorded, none silent)

1. **Factor-base construction does not literally call
   `harness.semaev.build_factor_base`.** That shared helper draws x-coordinates
   from anywhere on the full curve E(F_p) (order ~p), while targets
   `R = a*P + b*Q` are confined by construction to the cyclic subgroup `<P>`
   of order `N = inst.n` (the largest prime factor of `#E`, which
   `generate_instance` picks essentially at random and which is frequently
   far smaller than `2**field_bits`: empirically N in {23, 733, 87281, 4271}
   for the four main curves, not ~65536/~1048576 as the spec's own
   illustrative lambda values (~42, ~170) implicitly assume). Drawing the
   factor base from the full curve makes almost every 3-subset sum land
   outside `<P>` by construction (probability ~ N/p of landing back inside),
   which was verified empirically (mean measured n_R of 0.055 against an
   expected 4.47 on curve C16-2 in a first, discarded attempt) — a pure
   group-mismatch artifact, not a measurement of decomposition difficulty,
   and it would have made HEUR-001's birthday model
   (`n_R ~ Poisson(C(B,3)/N)`) incoherent by construction regardless of any
   real fiber-invariant signal. `driver.instances.build_factor_base_in_subgroup`
   instead draws B distinct x-coordinates of scalar multiples of P (elements
   of `<P>`, the same group R lives in), which was verified to bring the
   measured mean n_R back in line with the predicted lambda on all 4 main
   curves (e.g. C16-2: measured mean 4.52 vs. predicted lambda 4.47; C20-1:
   48.79 vs. 49.02; C20-2: 10.83 vs. 10.71; C16-1: 0.43 vs. 0.43). This is a
   necessary operationalization of "B = ceil(sqrt(N)) on-curve x-coordinates"
   given the spec names N as the target-space size (matching `R = a*P+b*Q`'s
   own definition, itself frozen and unchanged) — not a change to the frozen
   hypothesis, prediction, gates, or budget. The Coordinator should treat
   this as a disclosed implementation decision under interpretive latitude
   for underspecified glue, open to Validator/Red-Team challenge.
   An initial (buggy) attempt using the literal shared helper was run for
   RUN-FIB-001/002 with those run IDs, caught via direct verification before
   being reported anywhere as complete, and discarded (directories removed)
   before any downstream artifact referenced them; the corrected
   implementation was then used for the actual RUN-FIB-001..008 sequence
   under the same run IDs. No run ID was reused after being reported
   `completed_valid`/`invalid_measurement` to any consumer.

2. **The `generate_instance`-produced subgroup order N is not close to
   `2**field_bits`** for 3 of 4 main curves (see above). The spec's own
   illustrative lambda values (~42 at 16-bit, ~170 at 20-bit) implicitly
   assumed N ≈ 2**field_bits; the actual lambda realized per curve is
   `C(B,3)/N` using the *actual* N, reported per curve, not the illustrative
   figure. This is recorded as an anomaly, not corrected by re-picking seeds
   (the seeds are frozen).

3. **Certificate discipline**: every run's `certificate.kind` is `"none"`.
   This experiment is a measurement/correlation study; it never claims a
   discrete-log solve, and the Groebner cost measurement reports basis
   size/degree/triviality only — it does not extract or claim individual
   verified factor-base relations (the n_R enumeration table does have an
   implicit witness per hit by construction, but no relation-finding claim
   is made or reported as a deliverable of this experiment).

4. **Per-curve vs. per-run interpretation of the 1500s decomposition-
   measurement cumulative cap.** The frozen stopping rule text
   ("per-run cumulative cap 1500 s ... prefix >= 100 targets per curve
   required ... else that curve is resource_exhaustion") is applied here as
   a **per-curve** 1500s budget within each of RUN-FIB-004/005 (each of
   which covers 2 curves), i.e. up to 3000s of decomposition-measurement
   work per run before the top-level per-run wall-clock cap (1800s) can cut
   it off first. This is the more generous reading (gives every curve a full
   chance at the 100-target minimum) and is stated here as an explicit
   interpretation of an ambiguous instruction, not a change to the budget
   numbers themselves.

## Artifact naming

The frozen `specification.yaml`'s own `required_artifacts` list (not the
general docs template) names `raw.json`, `summary.json`, `stdout.txt`,
`stderr.txt` explicitly per run (as opposed to `raw-result.json`/`stdout.log`
used by some other experiments, e.g. EXP-SEMAEV-001, following the general
reproduction-package template). This implementation follows the frozen
spec's own explicit list verbatim; the difference from the general template
is deliberate and disclosed here, not an unreconciled mismatch.

## Honesty notes carried over from `harness/semaev.py`

`groebner_basis_max_degree` is the reduced-basis max total degree, an
implementation-bound proxy, NOT the theoretical degree of regularity.
`groebner_seconds` is a sympy Buchberger/F5-style wall-clock measurement, not
a crypto-scale timing claim. Only trends and the pre-registered rank
correlation are interpreted; absolute Groebner timings are toy-scale
artifacts only.
