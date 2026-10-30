# EXP-SEMAEV-93d5cc analysis: matched legacy/repaired `s4_expr` rerun

Experiment EXP-SEMAEV-93d5cc and its successors EXP-SEMAEV-88c46c (interrupted) and EXP-SEMAEV-6e9dcf. Hypothesis H-SEMAEV-94dab2. Runs:

| Cell | Run |
| --- | --- |
| icinv-m4 | RUN-SEMAEV-9cab7b |
| fib-004 | RUN-SEMAEV-3e69b6 |
| fib-005 | RUN-SEMAEV-4be606 |
| fib-decision | RUN-SEMAEV-894e27 |
| mtic-007 | RUN-SEMAEV-2a8498 |
| mtic-008 | RUN-SEMAEV-fcd67c |
| mtic-010b | RUN-SEMAEV-0e5876 |

RUN-SEMAEV-500a81 and RUN-SEMAEV-980e8c are interrupted attempts and are not results.

Validation: `experiments/EXP-SEMAEV-93d5cc/reviews/TASK-20261018-83a561/validation-report.md`.

Run report: `experiments/EXP-SEMAEV-93d5cc/reports/run-20261018T2156Z/`.

## Observation

1. **Legacy-arm reproduction.** The legacy arm reproduces every deterministic archived field in every cell (CTRL-LEGACY-REPRO passed seven of seven):
   - icinv-m4: all 552 m4 tuples equal;
   - FIB: per-target (capped, basis size, basis max degree, trivial) equal on 200 + 75 (C16) and 75 + 15 (C20) targets;
   - MTIC: per-target tuples equal on 25, 13 and 12 attempted targets;
   - MTIC-010b: regime and K\* equal.
   Wall-clock caps truncated the same counts as in the archive (MTIC 25, 13 and 12 attempted; FIB 75 and 15 measured).
2. **icinv-m4.** The repaired arm changes every m4 record:
   - `s4_support` 439 on 550 records and 391 on 2 (one class curve and its gauge twin), against archived 227 on 546, 225 on 4 and 210 on 2;
   - singular-locus dim/degree 2/39 on all 552 against 2/60;
   - gauge agreement 276/276 in every arm;
   - class and control m4 tuple sets differ in every arm.
3. **fib-004, C16-1.** All 200 targets are solved uncapped in every arm.
   - Repaired median Groebner time is 3.678 s (range 3.03 to 7.07 s); the legacy rerun's is 0.0579 s, the archive's 0.0279 s.
   - Basis size is 14 to 19 elements (14: 61, 16: 28, 17: 36, 18: 16, 19: 59) against 3 to 4 (3: 16, 4: 184); max degree is 5 or 6 against 5.
   - The repaired times split exactly by max degree: all 109 degree-6 bases took under 4.5 s and all 91 degree-5 bases at least 4.5 s.
   - No ideal is trivial in any arm.
4. **fib-004, C16-2.** All measured solves are capped (20 s) in every arm. Repaired measures 31 targets, stopped by the 1800 s run cap, against 75 (per-curve cap) in the legacy rerun and the archive.
5. **fib-005.** C20-1 has 75 measured and C20-2 has 15, all capped, with identical stop reasons in every arm.
6. **fib-decision.** C16-1 Spearman rho\_s between n\_R and cost:
   - archived −0.024 (p 0.742); legacy rerun −0.097 (p 0.171); repaired −0.366 (permutation p recorded as 0.0 from 10,000 replicates; null 95% band ±0.139).
   - Correlation gate: no curve passing in any arm.
   - Predictor-cost gate passes in every arm; C16-1 ratio 8.6e−6, 4.2e−6 and 6.5e−8 respectively.
   - RUN-FIB-008 stays cancelled by the gate.
7. **mtic-007, -008, -010b.** Every attempted descent is capped at 60 s in every arm. Regime (i) with K\* infinite holds under all three accountings at 16, 20 and 24 bits and for both ablation bases, in every arm.

## Comparison

C-aa-legacy-archive is the A/A comparison (same function, different host and date):
- zero differences on every deterministic field;
- C16-1 timing medians 0.0279 s against 0.0579 s;
- C16-1 rho\_s spread 0.073.

C-defect (repaired against legacy, one factor):
- ICINV: 552 of 552 m4 tuples differ.
- FIB C16-1: every one of 200 basis tuples differs; median time ratio 63.5; rho\_s difference 0.269, above the 0.073 A/A spread.
- FIB C16-2: measured count 31 against 75, a run-cap consequence of the C16-1 change.
- FIB C20 and all MTIC cells: no S4-dependent output differs.

Frozen conclusion fields:
- Repaired against archive, the icinv-m4 `s4_support` and singular-locus value sets differ.
- Every FIB and MTIC conclusion field is equal: resource\_exhaustion and all-capped flags, gates, the RUN-FIB-008 outcome, regime and K\*.

## Inference

- The defect changed the recorded S4-dependent outputs where the legacy polynomial was actually solved or analysed to completion:
  - every m4 invariant of RUN-ICINV-e0cd8f-m3class;
  - the C16-1 decomposition cost, basis structure and cost correlation of RUN-FIB-004/006C.
  The legacy reproduction control passed, so these differences are attributable to the defect, not to host drift.
- Where every solve hit its cap (all MTIC cells, FIB C16-2 and C20), the defect left the recorded outputs unchanged because the caps bind in both arms. Unchanged here means the caps still bind with the exact S4; it does not mean S4 is irrelevant to decomposition cost.
- Recorded conclusions, run by run:
  - **RUN-ICINV-e0cd8f-m3class:** the CLASS-VARYING verdict rests on m3 families only and is unaffected. Its m4 secondaries (`s4_support`, singular-locus degree) are superseded by RUN-SEMAEV-9cab7b's repaired values.
  - **RUN-FIB-004/005/006C/007/008:** the gate decision (correlation gate fail, cost gate pass, RUN-FIB-008 cancelled) is unchanged. The C16-1 association moves out of the frozen |rho\_s| < 0.2 falsification band into the 0.2 ≤ |rho\_s| < 0.4 inconclusive band. It is negative, as the predictor hypothesis predicts, but below the 0.4 gate. EXP-FIB-001's archived C16-1 reading ("no association") was therefore produced by the defect, while its experiment-level gate outcome stands. This band is not one of this contract's frozen conclusion fields; it is reported as an additional observation.
  - **RUN-MTIC-007/008/010b:** unchanged in every frozen field.

## Limitation

- Toy tier: the archived instances only.
- One execution per arm. The timing-derived quantities (median costs, rho\_s) rest on a single repaired execution with the A/A spread as their noise floor. The deterministic fields (m4 tuples, basis sizes and degrees, capped flags) are exact.
- Wall-clock caps are host-dependent. The legacy arm reproduced the archived truncation counts on this host, which supports this host as a stand-in, not as identical hardware.
- The archived programs were untracked at their run commits. Their run-time bytes are evidenced only by the exact legacy reproduction.
- The 2026-10-19 interruptions cost two attempts of the mtic-010b cell. Both are preserved; neither is evidence.
- No cost, speedup, security or ECDLP claim, and no improvement over any index-calculus baseline.
