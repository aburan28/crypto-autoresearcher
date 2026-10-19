# Analysis of EXP-CMFB-cea1d2 (Coordinator review, DEC-20261019-f33f3e)

Hypothesis H-CMFB-9b2eed, question RQ-CMFB-33610e, evidence EV-CMFB-e3d1ec.
Runs RUN-CMFB-2373be (t1), RUN-CMFB-5905c0 (t2), RUN-CMFB-66b0fe (t3),
RUN-CMFB-3dc120 (t4, C16 and C20), RUN-CMFB-42a578 (t5, C24 FAM),
RUN-CMFB-e13f0e (t6, C24 N-A), RUN-CMFB-c71d35 (t7, C24 N-B),
RUN-CMFB-2010d3 (t8, analysis). Reviews: VAL-20261019-1b97f5
(`coordination/tasks/TASK-20261019-bbb351/validation_report.yaml`, verdict
passed) and RT-20261019-520123
(`experiments/EXP-CMFB-cea1d2/reviews/red-team/red_team_report.yaml`, verdict
conclusion_requires_narrowing). Review plan, written after both verdicts:
`experiments/EXP-CMFB-cea1d2/reviews/review_plan.yaml`.

**CORRECTION (owner review P2, CORR-20261019-a89bfa): the 1.582 ratio is
model-conditional, not a universal theorem.** Wherever this analysis, EV-CMFB-e3d1ec,
DEC-20261019-f33f3e or the review report call min(1, mu)/(1 - e^-mu) <= 1.582 a
theorem or a ceiling that holds "for every base", read the following instead.
(1) Exact identity (proved): sum_r c(r) = binomial(B+2,3). (2) Exact bound
(proved): coverage <= min(1, mu); the multiplicity distribution is left free,
so for a specified positive baseline coverage c0 the ratio is bounded by
min(1, mu)/c0. (3) Conditional model estimate (not proved): taking the random
base's coverage to be the Poisson value c0 = 1 - exp(-mu), which is heuristic
H2, gives 1.582 at mu = 1. That substitutes a model for the baseline; it is not
a finite-instance ratio theorem and says nothing about end-to-end cost. The
empirical small-x coverage comparison keeps its stated scope. The measured
random-base coverage (recorded `random_seen`) could replace the Poisson value;
that computation is not done here. Inference 5 and the closing cost paragraph
below are to be read with this correction; they are left unedited as the
archived Coordinator text.

How this analysis was made. No shell was available to the Coordinator subagent.
Every number below is read from `RUN-CMFB-2010d3/raw-result.json` (t8) by key,
from the two review reports, or is arithmetic on those values, shown and
labelled "derived". The Coordinator did not recount any coverage; the recount is
VAL-20261019-1b97f5 M4 (26,331 of 26,331 bases, independent code). Nothing under
`runs/`, `implementation/`, `specification.yaml`, `trial-plan.json` or the run
report was edited. The calling session spot-checked the T, MDE, randomization p
and Holm p values of the table in Observation item 3 and item 4 against
`raw-result.json` before saving this file.

Percent values are percentages of the coverage ratio against the matched random
base (T = mean over members of ratio - 1, times 100).

## Validity (checked before interpreting anything)

- Run count and schema: 8 of 8 trials, every manifest complete, every receipt
  `output_validated`, instance-list sha256
  38cf55093614d8f8761e392d75e17ae5f0266e50b69b7abd58d6f01c3b2fa314 identical in
  all eight (VAL A2, A4, A5; 72 of 72 artifact hashes recomputed equal).
- Seed integrity: seeds 7001 to 7010 in all manifests; 200 random bases per
  member on 131 of 131 items; no repeated prime within N-A or N-B per cell
  (VAL C9).
- Raw and summary agreement: every one of the 26,331 coverage counts recomputed
  by independent code, 0 mismatches (VAL M4); all nine T rows, intervals and
  randomization p-values recomputed from the specification text equal the
  recorded values to 1e-12 (VAL M6); all eight trials rebuilt from scratch give
  identical raw results outside timings (VAL M9).
- Control comparability: the member base and its 200 matched random bases pass
  through the same counter; M0 holds on every counted base (VAL M5); the
  60-case brute-force check, curve and twist validity (131 curves), labelling,
  the qr_window positive and negative controls and the planted-base gate pass
  on recomputation (VAL C1 to C7).
- No solve, relation or key-recovery claim is made by any run; there is no
  certificate to verify. Correction made by the calling session after the
  Coordinator draft: the eight run manifests carry no `result.certificate`
  block at all (the draft said "kind none in every manifest"), and
  `tools/validate_ledger.py` line 1203 therefore reports eight errors,
  "run.result.certificate.kind must be one of discrete_log|decomposition|none",
  one per run directory. This is a record-schema defect of the published run
  manifests, not a result defect; the run directories are immutable and were
  not touched. See the Limitation section.
- Verdict on validity: the run set is complete and admissible for the tested
  scope. Two discrepancies between frozen text and frozen code (D1, D2 below)
  do not void it; the Coordinator's determination on D1 is in the Limitation
  section.

## Observation

All values are recorded in RUN-CMFB-2010d3 unless marked derived.

1. Instances. FAM members (exhaustive in the band): C16 4, C20 10, C24 13
   (Bateman-Horn expectation 3.11 / 8.01 / 14.42; exact over expected 1.28 /
   1.25 / 0.90, all within a factor of 2). N-A: 8 / 16 / 16. N-B: 8 / 16 / 16.
   Total 107 members. Mean log2 p: FAM 16.49 / 20.46 / 23.69, N-A 15.57 / 19.58 /
   23.59, N-B 15.28 / 20.03 / 23.93 (C16 / C20 / C24). Rule P1 not applied.
2. Exact yield identity: sum_r c_D(r) = binomial(B+2,3) on every counted base
   (rules I2 and I3 true; VAL M5).
3. Coverage excess T of the small-x base against 200 matched random bases, with
   the recorded 95 percent moving-block-bootstrap interval and the two-sided
   randomization p (20,000 draws):

| arm | cell | n | T (%) | 95% interval (%) | randomization p |
|---|---|---|---|---|---|
| FAM | C16 | 4 | -0.1742 | [-0.1742, -0.0340] | 0.4113 |
| FAM | C20 | 10 | -0.0296 | [-0.0741, +0.0482] | 0.4408 |
| FAM | C24 | 13 | -0.0224 | [-0.0381, -0.0060] | 0.0312 |
| N-A | C16 | 8 | -0.0849 | [-0.4046, +0.2630] | 0.6864 |
| N-A | C20 | 16 | -0.0085 | [-0.0612, +0.0389] | 0.8430 |
| N-A | C24 | 16 | -0.0004 | [-0.0237, +0.0267] | 0.9691 |
| N-B | C16 | 8 | -0.0094 | [-0.1862, +0.1661] | 0.9693 |
| N-B | C20 | 16 | +0.0102 | [-0.0384, +0.0570] | 0.7953 |
| N-B | C24 | 16 | +0.0161 | [-0.0012, +0.0346] | 0.0794 |

   All nine intervals lie inside +-0.5 percent. The largest absolute interval
   end is 0.4046 percent (N-A C16, n = 8, excluded from every reading); at C20
   the intervals lie inside [-0.074, +0.057] percent and at C24 inside
   [-0.038, +0.035] percent. The FAM C16 interval has T at its lower end; with
   n = 4 and block length 3 only two block starts exist, four possible resample
   means, so that interval is degenerate (VAL D3, derived by enumeration).
4. Recorded powered set and Holm values. The recorded analysis lists C24 only as
   powered (`powered_cells` = [C24], C20 `mde_ok` false); recorded Holm-adjusted
   p for the three C24 tests: FAM 0.0936, N-A 0.9691, N-B 0.1589; no Holm
   rejection; `holm_rejection_below_delta` empty; the three C24 99 percent
   contrasts (FAM - N-A, FAM - N-A near-family stratum, N-A - N-B) include 0;
   growth not assessable; classification NULL_AT_RESOLUTION.
5. Recorded MDE (percent) and the contract-text MDE. Recorded: C16 1.332 /
   1.318 / 1.537, C20 0.243 / 0.268 / 0.245, C24 0.065 / 0.063 / 0.057 (FAM /
   N-A / N-B). Contract text (MDE = 3.61 rms sd / sqrt(n), no inflation factor),
   derived as recorded / (sqrt(3) x 1.0025) = recorded / 1.7364 and equal to
   VAL D1 and RT-O2: C16 0.767 / 0.759 / 0.885, C20 0.140 / 0.154 / 0.141, C24
   0.037 / 0.037 / 0.033.
6. Planted-relation gate (t3): detected 7 of 8 (C16), 8 of 8 (C20), 8 of 8
   (C24). Pooled planted ratio against the Poisson-law known value: C16 1.02667
   vs 1.03035 (tolerance 0.842 percent), C20 1.01091 vs 1.01247 (tolerance
   0.173 percent; observed difference 0.156 percent), C24 1.00525 vs 1.00521
   (tolerance 0.100 percent); pooled randomization p = 5.0e-5 in each cell. The
   specification discloses before the run that these numbers were seen in a
   pre-freeze smoke test on the same seeds.
7. qr_window control (residuosity of f(x)): R_pool 1.9940 to 2.0009 in all nine
   pools (N-B pools 1.9940 / 2.0009 / 1.9980), inside [1.98, 2.02]; FAM and N-A
   pools differ from 2 by at most 0.0047, i.e. at most 1.3 standard errors.
   Legendre(x) negative control R_wrong 0.9970 to 1.0006. No scan-efficiency
   branch fires.
8. Tail diagnostics: smallest member rank p 0.0050 (N-B C24, Sidak 0.0767),
   0.0149 (FAM C20 and N-A C24); no Sidak flag below 0.01; Kolmogorov-Smirnov
   uniform p 0.064 to 0.59 and normal p 0.38 to 0.97; none flagged. FAM lag-1
   autocorrelation of (ratio - 1) in t order: 0.416 (C16), 0.018 (C20), 0.324
   (C24).
9. Null spread (I10). Recorded measured over the draft formula
   (`count.sigma_rel_formula`, about 0.49/sqrt(N)): 2.39 to 2.77, flag true in
   all nine arm-cells. Against the frozen 1.4/sqrt(N) (VAL D2, rms over members
   of sd x sqrt(N)/1.4): FAM 0.878 / 0.896 / 0.940, N-A 0.815 / 0.896 / 0.925,
   N-B 0.842 / 0.945 / 0.971 (C16 / C20 / C24); RT-O5 by its own aggregation:
   FAM 0.892 / 0.903 / 0.935, N-A 0.853 / 0.891 / 0.931, N-B 0.852 / 0.942 /
   0.960. All 18 values lie inside the band [0.75, 1.33]; at member level 106 of
   107 are inside (VAL D2: N-A C16 member N = 19081 at 0.739). The two
   reviewers' aggregations differ by at most 0.04.
10. Resource record (VAL K2): wall 703 s over 8 trials, 0.73 core-hours, measured
    tau 13.3 to 14.9 ns per triple against the 14 ns pilot and the budgeted 40 ns;
    peak RSS up to 819 MB per process (the analytic memory model gave 0.45 GB
    per worker).

## Comparison

1. Against the preregistered prediction T = 0 with delta = 0.5 percent
   (specification `preregistered_prediction`, `resolution_delta`): in every
   cell and arm the interval of T is inside +-0.5 percent, and in the cells the
   contract text calls powered (C20, C24) it is inside +-0.08 percent. No
   DETECTED_EXCESS (needs Holm p <= 0.05 and T > +0.5 percent) and no
   DETECTED_DEFICIT exists. Decision rule R3 matches: NULL_AT_RESOLUTION. The
   recorded classification follows from the frozen rule under the recorded
   powered set {C24} and, per VAL M7, also under the contract-text set
   {C20, C24}.
2. Against the contract-text powered set. Derived from the recorded
   randomization p-values: with C20 and C24 powered the Holm family has six
   tests; sorted raw p 0.0312 (FAM C24), 0.0794 (N-B C24), 0.4408 (FAM C20),
   0.7953 (N-B C20), 0.8430 (N-A C20), 0.9691 (N-A C24) give Holm-adjusted
   p = 6 x 0.0312 = 0.1872, 5 x 0.0794 = 0.3972, and 1.0 for the other four
   (arithmetic; equal to VAL M7). Nothing is rejected under either family. The
   smallest recorded p (0.031, FAM C24, a deficit) has probability about 0.25
   of arising as the minimum of nine tests under the null (derived:
   1 - (1 - 0.0312)^9 = 0.25; RT-O6).
3. Against the sensitivity control. The planted B+1 base has a known excess of
   +0.52 percent at the C24 control sizes and is recovered at +0.525 percent
   (pooled ratio 1.00525, tolerance 0.100 percent, 8 of 8 curves). The largest
   absolute C24 interval end (0.038 percent) is 13 times smaller than delta
   (derived: 0.5 / 0.038 = 13.2). The instrument therefore resolves effects an
   order of magnitude below the declared delta at C24, but the sensitivity
   ladder has one rung (RT-O4, verified in structure by VAL C7): detection is
   demonstrated at +3.0, +1.2 and +0.5 percent, not between 0.04 and 0.5
   percent at the repository's own instrument.
4. Against the sibling arms. The FAM C24 contrasts against N-A and against the
   near-family N-A stratum, and N-A against N-B, all have 99 percent intervals
   that include 0 (recorded contrasts). A post hoc contrast FAM minus N-B at C24
   of -0.0385 +- 0.0139 percent is reported by RT-O6 only and is not in the
   preregistered contrast set.
5. Against the null-spread reference. All 18 aggregate ratios against
   1.4/sqrt(N) are inside [0.75, 1.33] (0.815 to 0.971). The coefficient of the
   null spread is not constant: mean sd x sqrt(N) is about 1.20 for N < 2^18,
   1.275 to 1.28 for 2^18 to 2^22 and 1.32 to 1.33 above 2^22 (RT-O5), so the
   contract's 1.4 is conservative by 5 to 14 percent. The first-principles
   estimate of RT-O4 is 1.235/sqrt(N) at mu = 1.
6. Against H2 and H3 as the hypothesis states them. H2 (planted effect within
   max(0.1 percent, 3 standard errors) of the Poisson-law value; null spread
   0.75x to 1.33x of 1.4/sqrt(N)): holds on both counts as recomputed; the
   planted increment is 12 percent below the Poisson-law value at C16 and C20
   (RT-O9), within tolerance. H3 (exact member count within a factor 2 of
   Bateman-Horn): holds (1.28 / 1.25 / 0.90).

## Inference

1. What the data support. Within the tested instances, base definition and
   resolution, the exact m = 3 coverage of the unsigned canonical-sign small-x
   liftable-window base of size ceil((6N)^(1/3)) is indistinguishable from that
   of 200 matched random bases per member: at C24, for FAM (13 of 13 members in
   the band), N-A and N-B, every 95 percent interval is inside +-0.04 percent;
   at C20 (powered under the contract text) inside [-0.074, +0.057] percent.
   H1, the exchangeability of the small-x window with a random base for
   coverage, survived a test it could have failed (planted base recovered;
   excess of either sign detectable at 0.04 percent at C24).
2. Which explanations are compatible. E1, E2 and E3 (twist/QR structure shared
   by all curves, the D = -19 class, the family polynomial or maximal Frobenius
   conductor) are each compatible with no coupling of size above 0.04 percent
   (C24) between the integer size of x in the integral chart and the logarithm
   labelling; they are not separated from one another because no arm shows an
   effect to attribute. The data do not discriminate among E1, E2 and E3 above
   that bound.
3. What the data do not discriminate. A coupling smaller than the C24 interval;
   a coupling that grows with N inside the unexplored range (the powered window
   is 3 bits wide, 2^22 to 2^25, FAM is exhaustive in the band so n cannot be
   enlarged, and an effect c N^eps with eps above about 0.13 that is below 0.04
   percent at 2^24 is unconstrained at 2^52; RT-O4, derived by the red team);
   structure invisible to 3-sum collision counts (multiplicative orbits,
   algebraic membership structure); the signed (x-only) convention, for which
   the coverage ceiling is about 1.0003 at the experiment's B (RT-O7); and
   decomposition cost, relation rank and linear algebra, which this experiment
   did not measure.
4. The FAM deficit. FAM T is negative in all three cells (-0.174, -0.030, -0.022
   percent); the C24 value has recorded Holm p 0.094 (0.187 under the
   contract-text family). A deficit means more pair-sum collisions than random,
   the wrong direction for an advantage, of order 10 to 20 coincidences per
   member (RT-O6, RT-O4). It is recorded as exploratory and descriptive; it is
   not detected under the pre-registered rule and is not a finding. Only a fresh
   FAM population (the next cell up) can discriminate it.
5. The coverage ceiling is not a result of this run. For every base of size B at
   every N, coverage ratio against a matched random base is at most
   min(1, mu)/(1 - e^-mu), which is 1.582 at mu = 1 (KN-FIND-007,
   `experiments/EXP-FB3-001/conservation.md`; a derivation, label `derivation`,
   not a machine-checked proof). The experiment runs at B = ceil((6N)^(1/3)),
   mu = 1.00 to 1.08. So 'the small-x channel cannot beat a constant' follows
   from the theorem before any run; the run adds the narrower measured
   statement that this particular base sits at the random value and not at any
   of the sites a designed base occupies (a Bose-Chowla base reaches 1.107 on
   the same instrument, EV-FBG-001).
6. The CM structure was not tested. The tested base selects abscissae by the
   integer size of x; the CM data (b = a + 2, conductor v, the degree-5
   endomorphism w) never enter the construction. RT-O3: the d = 1 chart has
   exactly one integral point for -12 <= x < 200000, so the window contains at
   most one point with rational structure. Endomorphism-chain, isogeny-pullback,
   canonical-lift, other-model and joint x-y bases, and the floor curve, were
   not run. For FAM, w acts on G = E(F_p) as the scalar lambda = 2/v mod N (RT-O3,
   checked on t = 1211: lambda^2 - lambda + 5 = 0 mod N, ord(lambda) = 136193
   far above B = 354), so a w-orbit base has labels l x lambda^j with no extra
   discrete logarithm work. This is a derivation by the red team; the
   Coordinator did not recompute it.
7. Reading of the contract's statements 'constant-only (no effect)' and 'retire
   the channel' in `decision_impact.on_positive`. The text is broader than the
   measurement. The narrowest statement the data support is the one in
   Inference items 1 to 3, scoped as in the Limitation section;
   'constant-only' is the ceiling theorem of item 5, and 'channel' means the
   small-x window base only.
8. Negative-result phrasing. No coverage excess exceeding the predefined
   resolution of 0.5 percent was observed over the tested instances (FAM, N-A
   and N-B at 2^14 < p <= 2^25), base (small-x liftable window), counting
   convention (m = 3, unsigned canonical-sign multisets, targets uniform over
   Z_N) and resource budget. This does not say that no factor base can beat a
   random one, nor that CM structure carries no usable coupling, nor anything
   about decomposition cost.

## Limitation

Scope and transfer.
- Tested: prime-order curves y^2 = x^3 + A x + B over F_p with 2^14 < p <= 2^25;
  FAM members of p = 5t^2 + 19t + 19 (t odd, p and N prime), N-A crater-type
  D = -19 curves with b != a + 2, N-B random curves with |A|, |B| <= 1000; the
  small-x liftable-window base only; m = 3; unsigned canonical-sign multisets;
  targets uniform over Z_N; exact counting; one confirmatory pass with fixed
  seeds 7001 to 7010. Claim tier toy.
- No transfer to 2^52 or to the 53-bit pair p = 5947698030651343 is claimed or
  argued; there is no growth arm (one powered cell by the recorded code, two by
  the contract text, three needed); the floor curve was not constructed.
- Powered cells: C24 only as recorded; C20 and C24 by the contract text. C16 is
  underpowered under every reading (FAM n = 4, contract MDE 0.77 to 0.89
  percent) and enters no conclusion.

Defects of the frozen analysis code (recorded, not corrected; the code and the
recorded t8 are untouched).
- D1 (VAL D1, RT-O2, moderate). `analyze.py` line 44 `VAR_INFLATION = 3.0` and
  lines 218 to 220 compute MDE = 3.61 x sqrt(3) x 1.0025 x sd / sqrt(n), and
  `check.py` lines 560 to 561 repeat the factor. The frozen text (specification
  lines 166 to 171 and 471 to 475) says "with no inflation factor", and its own
  worked case (line 461) is the no-inflation arithmetic. The factor is a
  constant carried from an earlier draft into code that was frozen with the
  contract (commit adef9cd65e), so it is a text-versus-code inconsistency at
  freeze, not a post-approval edit (I11 does not fire). Measured effect:
  powered set {C24} (recorded) instead of {C20, C24}; Holm family of 3 instead
  of 6; FAM C24 Holm-adjusted p 0.0936 instead of 0.1872 (derived above), N-B
  C24 0.1589 instead of 0.3972; classification NULL_AT_RESOLUTION unchanged;
  growth not assessable under both. The departure is in the conservative
  direction (fewer cells in the conclusion) and cannot have created a spurious
  null in a cell the text excludes. The checker shares the factor, so a passing
  `check.py` is not evidence on D1 (VAL D5).
- D2 (VAL D2, RT-O5, low). `analyze.py` lines 387 and 407 to 409 compare the
  measured null spread to `count.sigma_rel_formula`, the superseded
  independent-balls occupancy value (about 0.49/sqrt(N)) that the contract
  declares 2.4 to 2.75 times too small and replaces by 1.4/sqrt(N) before
  freezing. The flag `sigma_flag_I10` therefore fires in all nine arm-cells
  (ratios 2.39 to 2.77) as a false positive; against 1.4/sqrt(N) every
  arm-cell ratio is 0.815 to 0.971. I10 is a reviewer flag, not an automatic
  void, is not read by `classify()`, and does not feed the MDE or powered tests
  (they use the measured sd). The recorded fields `sigma_rel_rms_formula`,
  `sigma_ratio` and `sigma_flag_I10` are not to be quoted as evidence of an
  overdispersed null; the values in Observation item 9 replace them. The
  producer's run report discloses D2 (with an approximate x0.35 rescaling) but
  not D1 (VAL A8).
- Coordinator determination on D1 and I9 (made here, explicit because VAL D1
  leaves it to the Coordinator). I9 is defined in the contract as agreement
  between t8 and the recomputation in `check.py`, and that agreement holds. The
  affected fields (powered, mde, mde_ok, holm_p) are derived reporting
  quantities downstream of measured coverages that were independently
  recounted without a mismatch; the departure is conservative; and the
  classification is invariant under both formulas. The Coordinator therefore
  does not read I9 as firing and does not void the run (R1 not applied). Had R1
  fired, no scientific reading would be made; this determination is the one
  point at which the evidence's standing depends on a judgment, and it is
  therefore one reason the evidence is capped at `preliminary` and a superseding
  analysis is ordered. The frozen text, not the frozen code, is taken as
  governing where they differ; this applies the success criterion as written and
  changes none, so no protocol_amendment is required.

Record-schema defect (found by running `tools/validate_ledger.py` on the review
branch, not by either reviewer). The manifests of RUN-CMFB-2373be, 5905c0,
66b0fe, 3dc120, 42a578, e13f0e, c71d35 and 2010d3 lack `result.certificate`
(`kind: none` with a reason, as in `experiments/EXP-FB3-001/runs/*/manifest.yaml`).
The ledger validator reports them as errors, they are not in
`tools/validate_ledger_baseline.txt`, and the ledger CI job would fail on them
once the `changes` job is fixed. The run directories were not edited; the
remedy (a correction record, a baseline entry, or a Coordinator-authorized
manifest addendum) is a decision not made here.

Evidence-quality limits.
- One confirmatory pass; replication of the effect on fresh instances is not
  done (the contract: "a lead is replicated by a new contract with new seeds").
  The from-scratch rebuild (VAL M9) shows determinism and absence of hidden
  state on the same host, not replication of a statistical conclusion.
- The planted-base gate margins are thin at C16 (7 of 8, the minimum; one
  detected curve at the k <= 1 boundary) and at C20 (0.156 against 0.173
  percent), and the gate numbers were seen before the run (pre-freeze
  disclosure). The gate is a one-rung ladder (RT-O4, RT-O9).
- The qr_window "positive control" is the density identity R = 2 / (1 + chi-sum
  / S); it validates the implementation and cannot detect a structure of the
  base (VAL limitations, RT-O8). M0 is an enumerator self-check. The scan
  efficiency channel has a negligible cost share (RT-O8), so its confirmation
  retires nothing that carries cost.
- The blind re-derivation required by the review plan was not blind (VAL
  limitations); the review plan itself was written after the verdicts.
- N-A and N-B draws were verified instance by instance but their distributional
  fidelity (log-uniform p, uniform Frobenius angle) was not tested beyond the arm
  means of log2 p; arms are size-matched by cell band only and differ from FAM
  in mean log2 p by up to 1.21 bit (N-B C16; 0.10 and 0.23 bit at C24).
- FAM is an exhaustive population in each band, so the FAM arm cannot be
  enlarged without larger p; its sample size is the population.
- The structural translation (about 20 extra additive pair-sum coincidences per
  member excluded at C24) and the occupancy constant 1.235/sqrt(N) are the red
  team's analysis, calibrated by its own simulation; the producer's instrument
  has not reproduced the dose-response (RC-5).

Cost and distance remaining. No cost, ECDLP speed or pair-46-scale claim is
made and none follows. The measured improvement of the small-x base over the
index-calculus baseline (a random factor base) is none: the base equals the
baseline to within 0.04 percent at C24 (interval ends -0.038 to +0.035 percent);
the outcome is neither an improvement nor a regression. The red team's
analytic, unmeasured estimate of matched-rho distance for a generic-group index
calculus with a pair table is index calculus over rho of 88 to 3400 at
N = 2^24 across the 0, 0.1 and 1 GAE-per-unpriced-operation band (RT
baseline_comparison; sparse linear algebra 88 / 100 / 152, dense 88 / 700 /
3400), with an order that holds across the band. It is quoted as context
labelled estimate; this review adopts it as neither measured nor ranked, makes
no cross-method comparison, and no coverage result of either sign could move
that distance by more than the coverage constant of at most 1.582.
