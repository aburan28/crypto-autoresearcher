# Observations — EXP-ECRANK-76a70d execution (TASK-20260905-54bcbf)

Executor observations only. Interpretation, claim-tier, and state transitions
are the Coordinator's. Every number below is read from the run artifacts
(`results/run_record.yaml`, `results/summary.json`, `results/controls.json`,
`logs.txt`); none is recalled.

## What was implemented

- `engine.py` — the delta-multiplier engine (H-ECRANK-ee6e0e M2/M3):
  - exact polynomial arithmetic over Q (copied from the committed
    `construct_highrank.py`);
  - exact linear algebra over Q (`fractions.Fraction`, stdlib) for the
    5-dimensional subspace W'(b) = D⁻¹W(b) (left kernel of the 5×n
    Vandermonde at b) and the delta interpolant;
  - the seeded fibration search (fix 5 of the n r-coordinates in a seeded
    sub-box; solve the remaining n−5 u-coordinates from the n−5 linear
    relations; check each is a nonzero rational square — this covers the
    Bézout ≤ 8 sign-combinations at once);
  - the degeneracy filter (gcd-based repeated-root test on the quartic);
  - the quartic/cubic → Weierstrass reduction (copied from the committed
    machinery, with built-in exact on-curve rechecks);
  - the exact F_l-reduction within-class certifier (copied from
    `exact_certify.py`, IDEA-20260829-d53906 design) plus the eigenspace
    cross-class argument (copied from `verify_certificate.py`);
  - the coset/mask/transport machinery (copied from `coset_structure.py`);
  - an `OpCounter` with 10⁷ checkpoints and a 10⁸ per-arm cap.
- `run_all.py` — the 8-run driver with op counting, checkpointing, the
  IV-7 determinism check, the metric fits, the Fisher test, and the
  YAML/JSON output writers.

No edit was made to any committed module (`construct_highrank.py`,
`coset_structure.py`, `exact_certify.py`, `verify_certificate.py`). All
reused code was copied into `engine.py` (EV-ECRANK-6695dc defect D4 remedy
rule).

## Per-run results

| run | name | status | key result |
|-----|------|--------|------------|
| 1 | smoke self-test | completed | all 6 checks pass |
| 2 | arm A (n=6, seed 760706, N_b=10³) | completed | 0 instances, 7.10×10⁶ ops, 2.7 s |
| 3 | arm B (n=8, seed 760708, N_b=10⁴) | completed | 0 instances, 7.10×10⁷ ops, 9.8 s |
| 4 | arm B re-run (seed 760708) | completed | 0 instances, bit-for-bit identical to run 3 |
| 5 | arm C (n=10, seed 760710, N_b=10⁴) | completed | 0 instances, 7.10×10⁷ ops, 17.3 s |
| 6 | augmentation scan + null objects | completed | no constructed instance; F6 inconclusive |
| 7 | known-false d=(1..1) control | completed | n8=7, n10=9 (expected 7, 9) — IV-1 passes |
| 8 | repair/restart margin | not_needed | no prior run failed_infrastructure |

## Key observations

1. **Fibration yield is far below the declared sample's detection power.**
   The bounded 8-draw fibration search has a very low per-draw square-hit
   rate. For n=6 the single solved coordinate u₅ has numerator of size
   ~10¹⁵, so the probability it is a perfect square is ~(10¹⁵)⁻¹ᐟ² ≈
   10⁻⁷·⁵. A direct measurement over 31 990 draws (4000 b-tuples × 8 draws,
   n=6, H=10⁴) found **0/31 990** solved coordinates that are rational
   squares. For n=8 and n=10 the rate is lower still (3 and 5 solved
   coordinates must all be squares). Over the declared sample
   (10³–10⁴ b-tuples × 8 draws) the expected instance count is ≪ 1, so
   finding 0 is the expected outcome, not an anomaly.

2. **F1 fires for arm B (n=8).** The pre-registered 10⁴ seeded b-tuple
   sample was exhausted within the counted-ops and wall caps with no
   nonsingular instance. Per the frozen contract this is the declared
   negative outcome F1 on the declared sample scope. Arms A (n=6) and C
   (n=10) also found 0 instances; F1 is defined only for n=8, so these are
   measurements, not F1.

3. **Known-false control (IV-1) passes.** The d=(1..1) control (which
   degenerates to the Mestre construction, s = g² − p) produced certified
   total = 7 at n=8 and 9 at n=10, exactly the expected values, with zero
   verifier errors. This validates the relation bookkeeping and the
   certification pipeline: a pipeline reporting total = n at d=1 would be
   broken and all runs void; this one does not.

4. **Determinism (IV-7) passes.** The arm B re-run (same seed 760708) was
   bit-for-bit identical to the original arm B run (same b-tuple order,
   same fibration draws, same op counter, same 0-instance result).

5. **Smoke self-test passes all checks.** (a) dependent triple on Cremona
   5077a1 → certified 2; (b) independent pair on the same curve → certified
   2; (c) known-false n8=7, n10=9; (d) reduction round-trip on-curve and
   nonsingular.

6. **F6 scan is inconclusive.** No constructed instance was available from
   arms B/C, so the scan stage had no constructed core to scan. The 8 null
   random quartics (32 null cells) were still scanned for the background
   table (yield: 5 nonzero cells out of 32, max 2). The one-sided Fisher
   test is not computed (no constructed yield to compare). F6 is
   inconclusive, not fired.

7. **Metric fits are null.** With 0 instances per arm, the log-log slope
   fits have no data. The predicted exponents (5 − n/2: 2.0 for n=6, 1.0
   for n=8, 0.0 for n=10) are recorded but not validated. The
   flatness-artifact tell is false (no signal to be flat).

## Deviations from the frozen spec

1. **Source location.** The spec says "Source archived under
   `experiments/EXP-ECRANK-76a70d/source/`". The handoff's `write_scope` is
   the task directory only, so the source (`engine.py`, `run_all.py`) is in
   the task directory. Archival to the spec's location is a Coordinator
   action, not an Executor action.
2. **Smoke self-test fixtures.** The spec says "committed fixtures" without
   naming them. This run uses the DEV-A-01 dependent triple, an independent
   pair, the known-false control, and a reduction round-trip. These validate
   the same certification pipeline as the committed certificates at
   `experiments/EXP-ECRANK-e1e30e/certificates/` but are not those specific
   files.
3. **F6 null-object classes.** The spec says "32 null cells" (8 quartics ×
   4 classes). With no constructed instance available, the 4 classes were
   taken as the canonical default set [1, 2, 3, 5] rather than the
   constructed instance's non-forced classes. The F6 scan is inconclusive
   regardless.

## Limitations and caveats

1. **The bounded fibration is too low-yield to test HEUR-1 at the declared
   sample size.** The per-draw square-hit rate (~10⁻⁷·⁵ for n=6) means the
   8-draw-per-b search finds ≪ 1 instance over the declared sample. This is
   a limitation of the search, not a mathematical conclusion about
   HEUR-1. The design's prediction of "abundant" solutions is not realized
   by the bounded fibration search. A more effective search (more draws per
   b, a different parameterization, or a larger sample) would be needed to
   test HEUR-1, but that is outside the frozen contract.
2. **F6 is inconclusive** (no constructed instance). The null-object
   background table is provided, but the Fisher test is not computed.
3. **The metric fits are null** (no instances to fit). The predicted
   exponents are recorded but not validated.

## Infrastructure

- Python 3.12.8, macOS-26.6-arm64-arm-64bit.
- Stdlib only: no PARI, no cypari, no 2-descent, no root numbers, no
  network. Every claim is a lower bound from verifier-checked exhibited
  points.
- Peak RSS: ~50 MB (well within the 8 GiB cap).
- Total wall: ~39 s (well within the 7200 s per-run cap).
- Counted ops: 7.10×10⁶ (arm A), 7.10×10⁷ (arms B/C), well within the
  10⁸ per-arm cap. No run exhausted its op or wall budget.
- Requested policy: `executor-implementation` at reasoning effort medium.
