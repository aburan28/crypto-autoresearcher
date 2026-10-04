# Analysis — EXP-ECDLP-a26bde

Reviewing dispatch: TASK-20260911-6bf4f9. This analysis is written by the
Coordinator review session, which has no Bash/Python execution tool; every
number below is read directly from committed run artifacts
(`experiments/EXP-ECDLP-a26bde/runs/*/manifest.yaml`,
`.../raw-result.json`), cross-checked with `Grep` counts across the full run
set, and reasoned from `driver/stage23.py` and `driver/instrument.py` as
committed. Nothing here was recomputed by running code. Facts about the
20/22/277/683/24 headline counts were also independently re-derived by the
dispatching session's blind rederivation (recorded in
`ledger/handoffs/TASK-20260911-6bf4f9.yaml`, `review_plan`); this analysis
treats those as a second, independently-obtained set of numbers and
reconciles them against direct reads of the committed files rather than
simply repeating them.

## 1. Observation

**Run package.** 22 official runs under `EXP-ECDLP-a26bde`:
`RUN-ECDLP-a26bde-000-selfchecks`, `-001` through `-020` (one per (curve,
prime) instance, 5 curves × 4 primes), and `-021-anomalous`. All 22
manifests read `status: completed_valid` (verified directly: `Grep` for
`status: completed_valid` across `runs/**/manifest.yaml` returns exactly two
matches — top-level and `result.status` — per official run, 44 total, plus
one further match belonging to the separate stray artifact discussed in
Limitations). All 22 share `git_commit: 9b8354...` and `recorded_at`
timestamps within the same ~65ms window on 2026-09-06T03:14:04Z, consistent
with a single batch write from `run_all.py`.

**Claim (1), the digit identity.** Across the 20 non-anomalous instances,
every one reports `digit_identity.agreement_rate: 1.0`, `n_agree == n_total
== 68` (the full non-skipped m-ladder: 64 dense values 1..64 plus 96, 128,
192, 256). Total 1360/1360 exact agreements, `d(mS^) == m*d(S^) mod p` on
every instance and every m with `n` not dividing m. Spot-checked directly in
`RUN-ECDLP-a26bde-009/raw-result.json` (curve 2, p=7477): every one of 68
`instances[]` entries has `"agree": true`, `d_mS == predicted_m_dS`
literally equal (e.g. m=2: `d_mS: 6183`, `predicted_m_dS: 6183`).
Independently re-derived by the dispatching session from raw per-datum
records using code that does not import the driver's own aggregation logic;
1360/1360, zero mismatches, reported in the handoff's `review_plan`.

**Claim (2), the size law.** `size_law.slope` per instance ranges over
[1.9985526674624952 (curve 2, p=7477, read directly), ...]; the handoff
reports the full range across all 20 instances as [1.9983, 1.9999], mean
1.9992, independently refit from each instance's own
`numerator_bits_by_m` and matching the reported slopes to ~1e-14. All values
sit inside the pre-registered 2.00 ± 0.05 band.

**Claim (3), the Teichmuller contrast.** Pooled: 24/1360 = 0.01765
agreement, matching the falsification threshold's design intent poorly (see
Comparison below). Per-instance breakdown, confirmed by direct `Grep` of
`n_agree` across all 20 raw-result.json files: 16 instances (curves 0, 1, 3,
4) show `n_agree: 1` (agreement only at m=1); the 4 instances of curve 2
(A=9, B=26, x0=1, y0=6; primes 7477, 7481, 7487, 7489 — runs 009, 010, 011,
012) each show `n_agree: 2` (agreement at m=1 AND m=2, nowhere else in the
67-value non-trivial ladder). 16×1 + 4×2 = 24, reconciling the pooled count
exactly. In every curve-2 instance the two agreeing digit values are
identical between `digit_identity.instances[m]` and
`teichmuller_contrast.records[m]` at m=1 and m=2 specifically (e.g. run 009:
digit identity `d_mS` at m=1/m=2 is 6830/6183; Teichmuller `u_mS` at m=1/m=2
is also 6830/6183 — same numbers, in the same run) and diverge at every
other m (e.g. m=3: `d_mS=5536` vs `u_mS=4238`).

**Claim (4), leak and break.** Leak arm: `Grep` for `"certified": true`
across the 20 instance files returns exactly 277 occurrences (0 files show
`"certified": false`); `Grep` for `"skipped":
"infeasible_estimated_bits_exceeds_cap"` returns exactly 683. Anomalous
run (`RUN-ECDLP-a26bde-021-anomalous/raw-result.json`): `"refused_at":
"division by n inside E_1 (pow(n, -1, p^K) with p | n)"`,
`"refused_correctly": true` — the single predicted failure mode, no other
error. Self-check 5 (anomalous positive control,
`selfcheck_transcripts/selfcheck_transcript.json`): `"total": 24,
"certified": 24, "passed": true`.

**Certificate/budget accounting (joint 3).** The leak arm's recorded
combinatorics reconcile exactly: `LEAK_M_SAMPLE` has 12 values, `J_RANGE`
has 7 values (-3..3), giving 84 candidate (m, j) pairs per instance, but
`stage23.py` line ~172 (`if mj <= 0: continue`) silently drops any pair
whose `m + j*n` is non-positive *before* appending any record. Because every
tested m (≤256) is smaller than every tested n (≥303, from
`derivation_note.md`'s frozen-curve table), `j ∈ {-3,-2,-1}` always yields
`m + jn < 0` and is dropped without a record, leaving exactly `j ∈
{0,1,2,3}` (4 of 7 values) as ever eligible: 12 × 4 = 48 candidate records
per instance × 20 instances = 960, which equals 277 certified + 683 skipped
exactly. This is a real, mechanically-forced consequence of `m < n`
throughout the tested ladder, not a hidden exclusion — but it is also not
narrated anywhere in `derivation_note.md` or the specification, so it is
recorded here as an unremarked (not incorrect) accounting gap. All 683 skips
carry the pre-declared reason `infeasible_estimated_bits_exceeds_cap` with
`cap: 300000` fixed before the run per `derivation_note.md` section E; none
is a post-hoc exclusion of an unfavorable result.

## 2. Comparison

Against the pre-registered `success_criterion`
(`specification.yaml`): claims (1), (2), and the leak/break half of claim
(4) meet their criteria exactly on every instance — digit agreement 1.0,
slope inside 2.00 ± 0.05, certified recovery on every attempted leak pair,
anomalous refusal at exactly the named step.

Claim (3)'s falsification condition ("Teichmuller digit linear at a rate
far above 3/p") was written against `p` in the 10-14 bit range, i.e.
3/p ≤ 3/1009 ≈ 0.0030 at the smallest tested p. But the ladder samples only
68 m-values per instance, so the coarsest *measurable* nonzero rate is
1/68 ≈ 0.0147 — already ~5x the threshold. Any single nonzero count on any
instance was therefore close to guaranteed to read as "far above 3/p"
regardless of whether the section is truly non-homomorphic; the pooled
statistic as specified cannot discriminate "no systematic linearity" from
"one structural coincidence" at this resolution. This is a pre-existing
design-resolution mismatch, not a data anomaly, and it means the
`agreement_rate` field as computed is not a fair reading of the intended
falsification test without the correction below.

## 3. Inference

**The m=1 entry is a mathematical tautology, not a trial.** In
`stage23.py`, `u_S` (the baseline "delta_1(s(S))") is computed at line 135:
`teichmuller_defect_digit(p, Kreq, S_mod_K, t_S_big, 1, A, fg, Kreq)`. The
m=1 iteration of the main loop (lines 96-131) computes `u_mS` for m=1 via
`teichmuller_defect_digit(p, Kreq, mS_mod_K, t_S_big, m % n, A, fg, Kreq)`
with `m=1`: `mS_exact = exactcurve.mul(A, B, 1, S_exact) == S_exact`, so
`mS_mod_K == S_mod_K`, and `m % n == 1`. The two calls have byte-identical
arguments (`S_mod_K`, `t_S_big`, `m_mod_n=1`) — this is the function called
twice on the same input, not two independent measurements of `s` at `S` and
at `1·S`. Confirmed directly by reading `stage23.py` as committed (lines
124-135 above); no execution needed to see the two call sites are the same
call. The comparison `u_1S == 1 * u_S` is therefore true by construction on
every instance regardless of whether `s` is homomorphic, exactly the
`proves_too_much` failure mode the review plan flags: a statistic that
"detects" homomorphism in a section that provably cannot be homomorphic
(the pro-p gate, `KN-TECH-73630e`) has proved too much. **The corrected,
non-tautological count is 4 agreements out of 20×67 = 1340 trials, all four
in curve 2 at m=2.**

**The curve-2/m=2 agreement is explained, not merely observed.** Curve 2's
frozen point is `S^=(1,6)` on `y^2=x^3+9x+26`. The standard Weierstrass
doubling law gives `λ = (3x0^2+A)/(2y0) = (3·1+9)/(2·6) = 12/12 = 1`
exactly, so `x(2S^) = λ^2 - 2x0 = 1-2 = -1` and `y(2S^) = λ(x0-x(2S^))-y0 =
1·(1-(-1))-6 = -4`, i.e. `2S^ = (-1,-4)` exactly over `Q` — confirmed
against the raw data: `digit_identity.instances[m=2].numerator_bits == 1`
in every curve-2 run, i.e. `|numerator(x(2S^))| = 1`, consistent with
`x(2S^)=-1`. `instrument.teichmuller_section(a,b,p,K,x0_true,y0_true)`
(lines 363-383) builds `s(R) = (omega(x0 mod p), Hensel-sqrt(y0 mod p))`
where `omega` is the Teichmuller lift (`teichmuller_lift_scalar`, lines
341-360): the unique `(p-1)`-th root of unity congruent to the input mod
`p`. **`1` and `-1` are the only rational integers that are `(p-1)`-th
roots of unity for every odd prime `p`** (since `1^{p-1}=1` and
`(-1)^{p-1}=1` trivially, `p-1` being even), so for these two residues the
Newton iteration in `teichmuller_lift_scalar` starts already at an exact
fixed point and returns exactly `1` or `p^K-1` (≡ `-1`) at every precision,
for every `p` — no p-adic correction ever occurs. The paired
`hensel_lift_sqrt` branch similarly converges to the exact rational integer
`y` whenever the RHS is a perfect square of an already-known integer (`36`
at `x=1`→`y=6`; `16` at `x=-1`→`y=-4`), again with no correction. The
consequence: `s(mS)` for this curve at `m=1` and `m=2` is not merely *close*
to the true reduction of the exact global point `mS^` — it is *identical*
to it, at every prime and every precision, because both coordinates are
"self-lifting" integers independent of `p`. This is directly confirmed in
the raw data: `teichmuller_contrast.records[m].u_mS` equals
`digit_identity.instances[m].d_mS` exactly at `m=1` and `m=2` in every
curve-2 run, and diverges at every other `m` (e.g. run 009, m=3: `d_mS=5536`
vs `u_mS=4238`). Since `d(2S^) = 2·d(S^) mod p` holds exactly (claim 1,
verified independently above), and `s(2S)` coincidentally *is* the actual
lift whose digit *is* `d(2S)`, the Teichmuller-section digit at `m=2`
inherits claim (1)'s exact linearity by coincidence, not because `s` is
homomorphic. No other multiple in the tested ladder (m up to 256) reduces to
`x=±1` on any of the five curves — confirmed by scanning
`numerator_bits_by_m` for any other entry equal to 1; none exists past
m=1,2 on curve 2, and none at all on the other four curves, whose `x0`
values (7, 9, 5, 5) are not units of this kind and whose recorded `n_agree`
is uniformly 1 (m=1 only).

This is a checkable, elementary derivation (standard doubling formula plus
the definition of a Teichmuller lift), cross-validated against three
independent pieces of the raw data (the `numerator_bits=1` entries, the
exact `u_mS == d_mS` coincidence at m=1/m=2 only, and its absence at every
other m and on every other curve) rather than a numerical re-run. It
explains all of the review's puzzling features simultaneously: (a) why it
reproduces identically across all four of curve 2's primes — it is a global
rational-coordinate coincidence (`2S^=(-1,-4)` holds over `Q`, before any
reduction), not four independent per-prime accidents, so the >5σ-style
Poisson-null tension the review computed is not evidence against the null
model of "the digit is essentially random" — it is evidence that this
specific trial was never a random draw from that model at all; (b) why it
does not recur at m=4, 8, 16, ...: those multiples' x-coordinates are large,
generic rationals, not ±1; (c) why the other four curves are entirely clean:
none of their tested x0 or multiples' x-coordinates land on ±1.

**Reading for claim (3).** The pooled 24/1360 and even the corrected 4/1340
counts do not represent 24 (or 4) independent draws testing whether the
canonical Teichmuller section is linear in `m`. Zero of the tested,
non-tautological instances show an *unexplained* deviation from the
"non-homomorphic, agrees only by chance" prediction: the one deviation found
is fully accounted for by a specific, named degeneracy of *this
instrument's* realization of the contrast section (fixed-x-Teichmuller +
Hensel-y), triggered only when a tested multiple's x-coordinate happens to
be a rational integer that is its own `(p-1)`-th root of unity for every
prime (i.e., ±1) — a construction-specific artifact, not a property of `mS`
being linear in the elliptic-curve sense. This neither confirms nor
contradicts the mechanism claim (uniqueness of the homomorphic section,
`KN-TECH-73630e`'s pro-p gate) one way or the other: it identifies a
measurement-instrument blind spot in *this* test of it. The test as
specified cannot currently distinguish "no systematic linearity" from "one
explained coincidence" at its declared resolution (68 samples), and the
pre-registered 3/p threshold was, independent of this anomaly, already
un-satisfiable as a discriminating criterion at this sample size (Comparison
above). Both defects are in the experiment's design, not in the mechanism
being tested.

## 4. Limitation

- Toy tier throughout: 5 curves, 20 (curve, prime) pairs, primes 10-14
  bits, `m` to 256, one anomalous object. No claim here transfers beyond
  this tested range without restating the transfer argument.
- Claim (3)'s falsification threshold (3/p) is not calibrated to the
  ladder's 68-sample resolution; any future replication of this specific
  test needs a resolution-matched threshold (e.g., a binomial confidence
  interval on the corrected rate, or a much denser or larger-sample ladder)
  before "agreement rate ≤ X" can discriminate the intended hypothesis.
- The curve-2/m=2 explanation is a derivation cross-checked against the
  committed raw data, not a re-executed computation; this dispatch has no
  Bash/Python tool. It is checkable by any reader from the doubling formula
  and `instrument.py`'s definitions of `teichmuller_lift_scalar` and
  `hensel_lift_sqrt` without running anything, and it is corroborated
  three ways in the raw data (numerator-bit-length, exact digit coincidence
  at m=1/2 only, absence elsewhere), but no fifth independent execution
  confirmed it numerically inside this dispatch.
- A stray, differently-named run artifact, `RUN-ECDLP-a26bde-1` (not one of
  the 22 official runs; distinct naming convention, distinct git commit
  `286d48d8...`, distinct timestamp), sits under
  `experiments/EXP-ECDLP-a26bde/runs/`. Its own manifest records
  `stage1_self_check_C_literal_construction_pass: false` while still
  marking the run `status: completed_valid` and reporting digit-identity and
  size-law numbers (slope range 1.9966-2.0004, slightly wider than the
  official package's 1.9983-1.9999) — this contradicts the specification's
  own blocking rule ("Stage 1 is blocking; no multiple is computed before
  the self-checks pass") and is consistent with being a preliminary,
  pre-bugfix attempt (matching `derivation_note.md` section E's mention of
  "a previous, unreviewed attempt" left on disk). It is **not** included in
  this evidence record's `run_ids` and does not contribute to any claim
  above; it is flagged here as a data-hygiene item for a separate
  administrative decision, per this task's instruction not to touch
  anything under `runs/`.
- This experiment verifies a derivation numerically at toy scale; it is not
  a proof, and `H-ECDLP-6a9479` states no attack and no exponent claim.
  Nothing here should be read as bearing on cryptographic-scale hardness.
