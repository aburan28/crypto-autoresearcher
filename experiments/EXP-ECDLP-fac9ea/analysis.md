# EXP-ECDLP-fac9ea v3 — evidence-round analysis (RUN-ECDLP-8e13c2)

Review round TASK-20260921-915847, run against the run package committed in
`experiments/EXP-ECDLP-fac9ea/runs/TASK-20260921-4888d4/` (PR #1339, merged).
The review plan (prior, joints, proves-too-much objects, blind re-derivation
assignment) was committed BEFORE this file exists; the plan's
`procedure_deviations` declare the four degradations of this round, the
largest being that it is a SELF-REVIEW under the role-runtime outage (no
independent reviewer session exists today; independence is not claimed).

## Observation

Raw facts from `registry.json` (470 cells: 406 ok, 38 unavailable with
congruence certificates, 26 resource_exhaustion at the appended 2^26-class
tail prime 67108879) and `fits.json` (all fits exclude every 67108879 cell;
fitted primes run 4099..16777259):

- Gate-table readings (probability normalisation, nontrivial L1 norm,
  lambda fitted on log||vhat||_1^* vs log p, 16 ladder points for the
  full-ladder rows): R01 interval 0.0806 ± 0.0020; R02 AP 0.0806 ± 0.0020;
  R03 popcount level 0.4191 ± 0.0062; R04 base-3 level 0.4088 ± 0.0040;
  R05 base-10 level 0.3806 ± 0.0046; R06 index-3 coset 0.5013 ± 0.0037
  (10 points); R07 index-5 coset 0.5709 ± 0.0349 (4 points); R08 QR
  0.5000 ± 0.0000 (16 points); R09 low-bit 0.1133 ± 0.0047.
- Controls: C01 exact numerical zero at every prime; C02A 0.4996 ± 0.0006,
  C02B 0.5001 ± 0.0002, seed sets agree within 2SE; R03B recomputation
  bit-identical to R03; vhat(0) = 1 within 1e-9 in 406/406 ok cells.
- Checker (`checker-report.json`): ALL PASSED — naive O(p^2) DFT agreement
  1.0e-14 / 9.8e-15 at the smallest ladder prime (4099, a registry prime),
  second independently structured chirp-z agreement 4.4e-16 at 65537 (a
  registry prime), gate-algebra thresholds verified present in the two
  cited records' own text, and every reported verdict reproduced by an
  independently coded verdict function.
- PGL_2 battery: the Moebius-conjugated variant of every structured
  additive row (R01, R02, R03, R04, R05, R09) deviates beyond 2SE from its
  parent; the coset rows R06, R07, R08 do not (stable).
- Resource accounting: all 406 ok cells were recorded with the legacy
  byte/KiB-misread RSS conversion (disclosed in the manifest); converted,
  the maximum ok-cell high-water is 4.49 GiB, within the frozen 8 GiB cap.
  The 26 tail-prime cells recorded 9.6–13.8 GiB after the unit fix and are
  checkpointed resource_exhaustion, excluded from every fit (verified: no
  fits.json primes list contains 67108879).

## Comparison

Against the pre-registered predictions of H-ECDLP-4e1880 (and the idea
record's registered priors):

- "Interval and AP indicators lambda <= 0.05": FALSIFIED at the measured
  range — both read 0.0806 ± 0.0020. The reading is consistent with slow
  logarithmic growth of the probability-normalised interval L1 (c·log p
  mimics a small power over a finite ladder) trending toward zero
  asymptotically, but the pre-registered number was 0.05 and the
  measurement says 0.0806 at these sizes.
- "Multiplicative-coset and quadratic-residue indicators: prior lambda
  near 0 (square-root cancellation)": FLATLY FALSIFIED — R08 reads exactly
  0.5000, R06 0.5013. Square-root cancellation governs each COEFFICIENT
  (|vhat(k)| ~ p^{-1/2}), but the L1 sum accumulates p such coefficients:
  the two effects cancel and the level is 1/2, the random-set level. The
  prior confused per-coefficient scale with summed scale.
- "Digit-sum reproduction in [0.36, 0.42]": MARGINAL PASS — 0.4191 against
  the 0.42 edge; the ±2SE interval [0.4068, 0.4314] overshoots the band.
  The reproduction is band-edge, not comfortable (see J2 adjudication in
  the review plan: the frozen text names the fitted value, which is the
  semantics implemented; the marginality is disclosed in every artifact).
- "Random-sign null lambda ~ 1/2": PASSED — 0.4996/0.5001.
- The lane's dd041a statement that the lambda >= 1/6 band "has exactly one
  corpus inhabitant" (digit-sum): the census adds R06/R07/R08 above 1/4 —
  but at the random-set level, which is exactly where a key carries no
  usable bias structure. The band's census is now: digit family
  (representation-UNSTABLE, marginal reproduction), cosets (stable, at
  random level), R07 (stable, 0.5709 on 4 points, ~2σ above random —
  unresolved).

## Inference

Durable (normalisation-invariant — see Limitation 3 and the J3 derivation):

1. PGL_2 STABILITY SPLIT. Every structured additive set-statistic in the
   registry has an embedding-dependent lambda (Moebius deviation beyond
   2SE); every multiplicative coset statistic has an embedding-stable
   lambda. This split is invariant under any uniform rescaling of the
   transform (a prefactor c shifts log||vhat||_1 by log c in every row and
   in every Moebius image, cancelling in the difference), so it survives
   the concurrent normalisation conflict (commit 4785243985 vs amendment
   DEC-20260921-f1d95a) unchanged.
2. COSETS SIT AT THE RANDOM-SET LEVEL. For R08 this is a theorem, not a
   measurement: the blind re-derivation (review plan J-blind, derived from
   the quantity's definition and the classical quadratic Gauss sum
   |G(k)| = sqrt(p), never opening the producer's implementation, report,
   or fits) gives |vhat(k)| = |G(k) − 1|/(2|QR|) = Theta(p^{-1/2}) for
   every k != 0, hence ||vhat||_1^* = (p−1)·Theta(p^{-1/2}) =
   Theta(sqrt(p)) and lambda = 1/2 exactly — matching the measured
   0.5000 ± 0.0000. R06 is within 2SE of the same level (0.5013). A
   statistic spectrally indistinguishable from a matched random set at
   these sizes carries no measured bias structure a construction can key
   on; the census does NOT establish the stronger claim that no
   construction could ever use it.
3. THE ONLY OPEN CANDIDATE IS R07. The index-5 coset level reads
   0.5709 ± 0.0349 on 4 primes — stable under PGL_2 and ~2σ above the
   random level. Four points cannot decide a level; this is the named
   successor measurement, not a finding of structure.

Not durable (convention-relative, not promoted):

- Every gate VERDICT (corner/learning open-blocked against the thresholds
  1/4 and 1/6). Under the concurrent unitary normalisation every lambda
  shifts by −1/2 and the verdicts flip; the thresholds are calibrated to
  the lane's committed normalisation, which the concurrent edit disputes.
  The census records the verdicts it measured (frozen vocabulary) and the
  evidence record does not carry them as findings.
- The R03 0.4191 reproduction of KN-FIND-ffe1df's 0.39 is bound to the
  executed probability normalisation and the mode-level-indicator
  construction; under the concurrent edit's Thue–Morse/unimodular
  construction the reproduction target is a different quantity. The
  marginal reproduction is recorded, not promoted.

Scoped negative the data justify (negative-result phrasing): within the
frozen 12-row registry, at the measured ladders (4099–16777259, 16 points
full-ladder rows; 10 and 4 points for R06/R07), under the executed
probability normalisation, and by the frozen PGL_2 rule — no natural
coordinate statistic is simultaneously PGL_2-stable and measured above the
random-set spectral level, except R07 at 4 points and ~2σ, which is
unresolved.

## Limitation

1. SELF-REVIEW: this analysis, the evidence record, and the decision were
   produced by the same session that produced the run, under the
   role-runtime outage (five consecutive role-agent bootstrap failures
   today, recorded in DEC-20260921-4d1b40). No independent adversarial
   review has read this package. The transition is therefore the
   conservative one (weaken), knowledge promotion is deferred, and the
   independent review is an owed, queued next action.
2. SCALE: ok cells reach p = 16777259 (2^24.0); the 2^26-class tail point
   is checkpointed resource_exhaustion after the disclosed machine-cap
   breach, with values preserved in registry.json for a chunked-convolution
   amendment. All lambda readings are finite-ladder fits with the
   two-ladder and jackknife guards passing; asymptotic extrapolation
   beyond the ladder carries the fitted error bar (HEUR-1) and the
   interval row's 0.0806 demonstrates that short ladders can mimic
   power-law behaviour in slowly-growing quantities.
3. NORMALISATION CONFLICT: the branch carries two pre-run repairs of the
   same frozen-contract defect — the executed amendments
   (DEC-20260921-d3fafb, DEC-20260921-f1d95a: probability normalisation,
   level-indicator constructions) and a concurrent in-place rewrite of
   specification.yaml by another session (4785243985: unitary
   normalisation, Thue–Morse/character constructions), which bypassed the
   amendments path and was not pulled before execution. The run executed
   its own manifest's contract exactly. Inference items 1–3 are invariant
   under the difference; the gate verdicts and the R03 reproduction are
   not, and are excluded from promotion. Which normalisation is canonical
   for the lambda-registry is an owed adjudication.
4. R07's 4 points: the only above-level candidate is decided on 4 of a
   possible 10+ primes (the index-5 congruence p ≡ 1 mod 5 excludes most
   ladder primes); its level is unresolved and its reading names a
   measurement, not a mechanism.
5. The frozen rule's term "artifactual" is a protocol verdict (voided from
   the gate table), not a mathematical impossibility claim: PGL_2
   instability means the lambda is a property of the embedding; a
   construction that fixes an embedding could still use an unstable
   statistic, and the census does not test that.
