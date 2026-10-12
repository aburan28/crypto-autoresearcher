# EXP-PFDR-7c8bf2 -- Stage 0 analysis (composition of the Stage 0 review round)

- Experiment: EXP-PFDR-7c8bf2 (frozen specification v1, approved by DEC-20260928-b3afc2)
- Hypothesis: H-PFDR-0cc7e8
- Run: RUN-PFDR-7c8bf2-stage0 (archived at 1a037688c by TASK-20260928-f15632)
- Review round: plan inline on ledger/handoffs/TASK-20260929-c40e48.yaml
  (handoff.review_plan). Reports sealed at dc61c5e1e by TASK-20260929-599b4b.
  - validator TASK-20260929-c40e48 owns J1-J3
  - red team TASK-20260929-69b7c5 owns J4-J6 and proves_too_much
- Evidence record: EV-PFDR-cf6ee5. Decision: DEC-20260929-1b779a.
  Ledger archive: TASK-20260929-091c3a.
- Written by the Coordinator. Four sections, kept apart. Observation holds only
  what the archived files state. Comparison sets those against the frozen
  predictions and the review plan's prior. Inference is the Coordinator's
  reading. Limitation lists what the reading cannot carry.

Every number below is copied from a committed file named beside it. No number
was recomputed by this Coordinator, which holds no shell.

---

## 1. Observation

### 1.1 The run, as produced

Source: experiments/EXP-PFDR-7c8bf2/execution-report.yaml and
RUN-PFDR-7c8bf2-stage0/raw-result.json, as traced by the validator (J3).

- One analysis run, zero solver runs, over five committed sweep files.
  - Curves: generated prime-order ordinary curves E/F_p.
  - Size: log2 p in 12..32 bits, 11 rungs, 5 curves per rung per series.
  - Engine: crypto_autoresearcher.index_calculus mitm, default |F| per arity, min_fill.
- Invalidation checks I-1..I-4 were reported as passing.
- Outcome id reported: OUT-SLOPE-INTERVAL.
  - It is met by S6-smallx alone (F-3 as worded).
  - S6-smallx 12..32 slope and interval: 0.1036 [0.0841, 0.1242], against 1/12 = 0.0833.
  - S6-smallx 20..32 sensitivity fit: 0.0843 [0.0651, 0.1029].
- Every primary point estimate lies inside its window.
  - S4-smallx: 0.1321 [0.1174, 0.1480], window [0.095, 0.155].
  - Odd-m series: |slope| at most 0.0176 (S7-smallx).
- Minimum ratio over 955 IC rows: 1.4835.
  - Row: sweep-minfill-20260926, 12 bits, curve 1, ic_m3, small_x, mitm.
  - No row lies below 1.0, so none lies below 0.9. TW-FLOOR did not fire.
- The three m = 3 base geometric means (20..32) have pairwise-overlapping intervals.
  - small_x 2.814, random 2.761, subgroup 2.847.
- HEUR-0cc7e8-H2 (r/|F| slope, 20..32): all eight point slopes lie between -0.007 and -0.001.
  - Per-series intervals are in raw-result.json and were not read by this Coordinator.
- Two anomalies were recorded by the producer.
  - P7(a): the unfiltered rho set has n = 92, not 110.
  - P7(c), descriptive only: the randomized-PIT KS rejects at 1% for m = 7 (p = 0.0098).

### 1.2 Validator, J1-J3

Source: coordination/review/pfdr-7c8bf2-20260929/reviews/TASK-20260929-c40e48/validation-report.yaml and attestation.yaml.

| joint | verdict | what it rests on |
|---|---|---|
| J1 package and bindings | holds | 13/13 package files hash-equal to git objects, checksums.sha256 and the f15632 receipt. The five inputs are identical at c06f1ad8c and 1a037688c. No solver import. P1 twin check re-derived: 330 pairs, 3960 comparisons, 0 unequal. Defects D-1..D-4 are minor, disclosed or cosmetic. |
| J2 blind re-derivation | holds | Sealed before any blind_from read (seal 04:05:57Z, sealed file sha256 dd8d1dd6...431f). All 16 slope triples are bit-for-bit equal to the archive under the frozen method in file order. Min ratio exactly equal. P6 equal to Monte Carlo error. Own OLS and bootstrap agree within 3 MC s.d. on all 32 endpoints. |
| J3 raw/summary and reproducibility | holds | One re-execution is byte-identical: floor-rows, fits.json, raw-result.json. 62/62 raw-to-summary checks and 61/61 report values trace to raw outputs. |

The validator recorded four findings for composition.

- M1: the single exclusion that produces the outcome id is a Monte Carlo event.
  - S6 lower end at seed 0 is 0.084138; the MC s.d. of a 2000-replicate endpoint is 0.00069.
  - At 2e6 replicates the lower end is 0.083314, which is below 1/12, and 2.51% of the bootstrap mass lies below 1/12.
  - Over frozen-function seeds 0..199: 88/200 exclude 1/12, and 71/200 give OUT-CONSISTENT.
  - S7-smallx sits in the same position against 0: 69/200 seeds exclude.
- G-1: P4 fixes the bootstrap seed but not the row order.
  - Sorted (bits, curve) order at seed 0 gives OUT-SLOPE-INTERVAL met by S7-smallx alone (F-2), not S6.
- G-2: analysis_outcomes has no precedence rule. G-3: P6 names no RNG. Neither is outcome-bearing here.
- T-1: tools/check_review_independence.py ignores read order.
  - It will flag the validator's post-seal reads of three blind_from paths as a leak.
  - Those reads were analyze_floor.py, the run directory and execution-report.yaml, which the card itself commissioned for J1/J3.

### 1.3 Red team, J4-J6 and proves-too-much

Source: coordination/review/pfdr-7c8bf2-20260929/reviews/TASK-20260929-69b7c5/red-team-report.yaml (RT-20260929-58a1c7) and attestation.yaml.

| joint | verdict | key measurements (red team's; K = 20000 unless stated) |
|---|---|---|
| J4 overread | breaks | Per-series coverage of the frozen 95% interval is 0.857-0.909 over 48 cells. S6 against 1/12 is 0.893-0.906. Family-wise P(at least one of eight excludes its true model value) = 0.57-0.61. Over 500 seeds S6 excludes in 0.446, with seed-averaged lower end 0.0833 +- 0.0006; OUT-SLOPE-INTERVAL occurs in 0.648 of seeds. The S6 exclusion vanishes under a 1/log2N term, a quadratic tangent, dropping the 12-bit rung, the 20..32 range, the F-adjusted residual slope and the same-curve S6 - S7 contrast (0.0860 [0.0568, 0.1192]). An undeclared 24..32 look excludes by 0.0002 (J4-g); the red team reports this and does not discount it. |
| J5 rho de-duplication | holds | First-seen de-duplication removes only exact duplicates (294/294 within-label pairs identical). 18 curves are shared across the two labels with identical walks. Per-set unfiltered walk exponent is 0.5066 [0.4825, 0.5317] (n = 110), beside the archived 0.5088 (n = 92). No outcome condition reads the rho set. |
| J6 hidden assumptions and P7(c) | breaks | Six of 13 single-convention alternatives turn the outcome id into OUT-CONSISTENT: r = rank (A2a); one unit per stored tail (A3c); the comparator evaluated at the committed \|F\| design (A6a 0.0963, A6b 0.0855); log-of-mean (A7) and median (A8) estimands. S4 contains 1/8 under all 13. The P7(c) m = 7 statistic arises with probability about 0.001 under the declared stopping-rule confound with Poisson arrivals. The across-m pattern (four of five p below 0.09) arose in 0 of 2000 replicates. |
| proves-too-much | breaks | On synthetic S6 and S4 designs with the model true, per-series exclusion is 0.092-0.112 against the nominal 0.05. At the committed design, family-wise exclusion is 0.62-0.64. The rho r = 1 slice passes: 1/2 is inside all three rho intervals, and synthetic rho coverage is 0.918-0.935. |

The red team's own statement of the narrowest supported reading is quoted in
full in its report. Its proposed next action:

- a paired m = 6 / m = 7 replication;
- at least 15 curves per rung over 12..26 bits;
- a pre-registered same-curve S6 - S7 primary compared with the design-evaluated model difference;
- a family-wise-calibrated interval and at least 20000 bootstrap replicates.

### 1.4 Round procedure

- Blindness was declared mutual and is attested by both reviewers.
  - Neither read the other's directory.
  - The red team read the validator's card with `git show` to obtain the inline plan.
- The validator disclosed two incidents.
  - INC-1: a stray file in the detached worktree, removed; no tracked file touched.
  - INC-2: one commit subject line displayed before the seal; it names task ids only.
- The red team disclosed ad hoc read-only inspections run before its declared scripts. Every number it used from them was reproduced by a declared script.
- tools/check_review_independence.py was not run by this Coordinator (no shell).
  - The validator's own restricted run is in checks/t1-independence-checker-own-attestation.txt.
  - Of the four lines it reports, three concern the sibling's absence from that restricted run. The fourth is the T-1 leak line.

---

## 2. Comparison

### 2.1 Against the frozen outcome table

- The producer's outcome id, OUT-SLOPE-INTERVAL, is what the frozen procedure returns on the committed rows at seed 0 in input-file order.
  - J2 derived it blind and bit-for-bit. J3 reproduced it byte-for-byte.
  - The red team's check_pipeline.py reproduced fits.json exactly from its own series membership.
- The pre-registered success criterion was OUT-CONSISTENT. **It was not met.**
- No other falsification condition was met at seed 0. F-1 was not met: min ratio 1.4835.

### 2.2 Against the Coordinator's recorded prior (plan, written before any report; PD-1: written after reading the producer's report)

| joint | prior | result |
|---|---|---|
| J1-J3 | holds | Confirmed. |
| J4 | Marginal exclusion; undercoverage; family-wise 0.2-0.4; at most a scoped weaken with replication | Direction confirmed; strength exceeded. Family-wise is 0.57-0.61, not 0.2-0.4. The exclusion is also seed- and row-order-contingent, and at 2e6 replicates 1/12 lies inside the interval. The prior did not anticipate this. |
| J5 | n = 92 is a labelling artefact with no outcome effect | Confirmed. |
| J6 | m = 7 rejection is borderline and explained by the stopping-rule confound | Partly overturned. The rejection is not produced by the stopping rule under Poisson arrivals. Separately, the outcome id depends on undeclared conventions, which the prior did not anticipate. |

### 2.3 Against the proves-too-much control declared in the plan

- The failure signature was: a procedure that excludes known-true values materially more often than 5%.
- That signature was met: about 10% per series and 57-64% family-wise.
- The rho slice, the one known-answer object with 10 curves per rung and a single test, passed.

---

## 3. Inference (Coordinator)

1. **The run is valid.** J1-J3 hold.
   - RUN-PFDR-7c8bf2-stage0 is a complete, correctly bound, byte-reproducible execution of the frozen analysis.
   - Its outcome id follows from the frozen table.
2. **The outcome id does not discriminate.** OUT-SLOPE-INTERVAL rests on one interval endpoint (S6 at 12..32).
   - That endpoint is 0.0008 above 1/12, which is inside the endpoint's own Monte Carlo error (M1).
   - It is reversed by row order (G-1) and by 35% of bootstrap seeds (J4-c).
   - It comes from a procedure that the round's proves-too-much control shows excluding true model values in most eight-series families (O7).
   - The event is therefore not evidence against the even-m gap explanation (clause (iii) of H-PFDR-0cc7e8) at any strength this review can defend.
   - The outcome table's permitted "weaken" would overread it. That is the failure J4 was set up to detect.
3. **The rows do not resolve the m = 6 slope finer than about +-0.03.**
   - The quantity is the m = 6 ratio slope on these rows at 12..32 bits.
   - This is the red team's method-ceiling finding. It is consistent with the 20..32 interval width, the lack-of-fit test (p = 0.18) and the size of the identified lower-order components (0.005-0.019).
   - So these rows cannot confirm 1/12 either. The data cannot discriminate between the even-m gap value 1/12 and an excess of order 0.02-0.03.
   - The J4-g 24..32 look is recorded, not discounted. It is one of seven overlapping looks, and at least two of seven exclude with p = 0.20 under the model.
   - The only route to a finer reading is new rows with a better-designed test. No zero-run re-read of these rows can give one.
4. **The other clauses are observations only, not support.** Specifically:
   - min ratio at least 1.0 on all 955 rows;
   - odd-m point estimates inside [-0.03, 0.03];
   - S4 consistent under 13 conventions;
   - m = 3 base overlap;
   - H2 point slopes inside +-0.03.

   None of these is read as support, for three reasons:
   - the pre-registered success criterion was not met;
   - F-1's non-firing depends on two declared conventions: S includes the table, and one S_3 unit is two encodings (J6 A-S-table, A3a);
   - the hypothesis carries an asymptotic claim that cannot pass the promotion gates on this experiment.
5. **Decision class: inconclusive**, below the DEC-20260929-523aab ceiling (at most weaken with replication; reject_scoped forbidden).
   - Nothing adverse is decided, so no refutation artifact is required.
   - proof_status is not_applicable.
6. **The P7(c) observation is a descriptive departure** of relation yield from a single pooled Poisson constant across m at 12..32 bits.
   - It is not explained by the stopping-rule confound the specification named.
   - It concerns relations counted at a stop, not HEUR-0cc7e8-H1's x-key coincidence counts. It bears on H1 only through the clean fixed-budget test that EXP-PFDR-1b78f7 carries.
   - It is routed there. It changes nothing here.

Scoped statement (negative-result phrasing per docs/evidence-and-reproducibility.md):

> On the five committed sweep files (generated prime-order curves, log2 p in 12..32, five curves per rung, mitm engine, default |F|, min_fill; RUN-PFDR-7c8bf2-stage0), no departure of the m = 6 ratio slope from 1/12 was observed that survives the Monte Carlo resolution, the row order or the measured calibration of the frozen interval procedure (EV-PFDR-cf6ee5). The same rows do not resolve that slope more finely than about +-0.03, so this is not evidence that the even-m gap explanation holds. No row fell below the floor ratio 1.0 under the declared conventions.

---

## 4. Limitation

- **Scale and object.** The scale is toy: at most 32 bits, generated curves, one engine.
  - No transfer beyond 32 bits, to other engines or to deployed curves is asserted.
  - The GGM derivation behind the floor is not reviewed by this experiment.
- **One unreplicated re-read.** The five files are fixed. Five curves per rung is the design ceiling.
  - The eight series are not independent: they share curves, and the filtered S3 residual correlation is 0.60-0.70.
- **Reviewer computations are synthetic calibrations.** The coverage, family-wise and design-null figures are the red team's simulations on the committed designs.
  - They calibrate the procedure and are not new observations of the engine.
  - No second agent has re-run them.
- **Blind re-derivation independence rests partly on attestation.** The validator's J2 seal order is attested with a read log and a sealed-file digest, not proved by a commit made between the seal and the post-seal reads.
  - The mechanical checker cannot see the order (T-1).
  - The quantities it re-derived were reproduced by two further routes: the J3 byte-identical re-execution and the red team's independent pipeline check.
  - The decision does not rest on J2's independence. It rests on J4, J6 and the proves-too-much control, which weaken the outcome rather than support it.
- **Specification gaps, recorded and not repaired.** None of these was fixed pre-registration; each is left for any future test to declare:
  - row order and precedence (G-1, G-2);
  - the P6 RNG (G-3);
  - the r convention: the hypothesis glosses r as independent relations, but P2 fixes r = logged relations, and rank = relations - 1 on every primary row (O5);
  - the finite-range comparator (O4);
  - the estimand (A-estimand);
  - multiplicity (A-multiplicity).
- **Prior disclosure.** The Coordinator's prior was written after reading the producer's report (plan PD-1). Concurrence with it is weighed accordingly.
- **Checker not run by this Coordinator.** check_review_independence.py is run by the ledger-archive task TASK-20260929-091c3a, and its output is archived with this analysis. Any problem other than the T-1 line stops that archive.
