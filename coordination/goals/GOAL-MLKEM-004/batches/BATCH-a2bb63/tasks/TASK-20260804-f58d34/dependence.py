#!/usr/bin/env python3
"""
TASK-20260804-f58d34 / BATCH-a2bb63 (batch 5 of 6) / GOAL-MLKEM-004

T0  the deterministic-Y RANDDIR excess (DEC-20260804-5c9fe1 NA-1; RT-20260804-37a8f2
    section 5 reports 12.1507).  Bookkeeping, not the batch.
T1  ACROSS-CANDIDATE SCORE DEPENDENCE -- the quantity MATZOV.Nf's closed-form
    advantage law actually assumes, and the one quantity in this campaign whose
    value is not fixed by construction (DEC-20260804-5c9fe1 NA-2).
T2  the same measurement on the ADJACENT-FFT-BIN candidate family under
    BATCH-c45baf's admissible Stage B tuple (m=35, k_enum=0, k_fft=10,
    p in {2,3,5}, beta_sieve=50, k_lat=15), where the law's own correction term
    exp(k_fft/3 (sigma_s pi/p)^2) is NOT identically 1.

SCOPE, binding on every number this script emits: m=35, n=25, d=60, q=127,
secret centred-binomial eta=2, error rounded-Gaussian sigma=2; Stage B sieve at
dimension m+k_lat=50.  ONE LWE instance.  TOY SCALE.  No ML-KEM break claim, no
security proof, no FIPS 203 parameter set affected or cleared, no speedup, no
cost claim, no exponent moved.  AGENTS.md rule 12 UNMET and UNWAIVED, inherited:
this script changes the status of no EV-MLKEM-* record.  It states OBSERVATIONS.
It does not conclude that any heuristic is validated or refuted.

NO WALL-CLOCK TRUNCATION ANYWHERE.  Every loop in this file is bounded by a
count.  `time.time()` is read only to print elapsed seconds and never appears in
a loop condition.  (EV-MLKEM-ba6c25 OBS-2: batch 4's `_sample()` stopped on
elapsed time, so the same script and seeds produced a different family.)

==============================================================================
PRE-REGISTRATION.  Frozen in this file BEFORE the build and measure runs.
Not edited afterwards; both runs are scored against it exactly as written.
==============================================================================

--------------------------------------------------------------------------
0.  WHAT THE LAW ASSERTS, AND WHAT IS THEREFORE BEING MEASURED
--------------------------------------------------------------------------
MATZOV.Nf computes the number of dual vectors N from a closed-form advantage
law with no correlation term.  Two independence assumptions sit inside it:

    (I-a) the N per-vector contributions to ONE candidate's score behave as
          independent samples;
    (I-b) the scores of DIFFERENT wrong candidates behave as INDEPENDENT
          draws, so that max over candidates has the iid extreme-value law.

Batches 1-4 measured a row-permutation excess, which reads neither.  T1 and T2
measure (I-b) directly: the joint behaviour of per-candidate scores across a
candidate set over ONE shared database.

--------------------------------------------------------------------------
1.  THE STATISTICS, NAMED BEFORE THE RUN
--------------------------------------------------------------------------
Per-candidate score, exactly as in every prior batch of this campaign:

    S_k = (1/N) sum_i cos( 2 pi ( x_i . e + y_i . (s - c_k) ) / q )

The ensemble is D independent error draws e over ONE FIXED database.  For a
candidate group of size K this gives a D x K matrix of scores.  Statistics:

  ST-1  R_raw   = correlation matrix of the K raw score columns.
  ST-2  R_ctr   = correlation matrix after removing, per draw, the across-
                  candidate mean of the group (the "common mode").
  ST-3  offdiag(R) = mean off-diagonal entry of R.
  ST-4  spectrum(R): eigenvalues; lambda_max; participation ratio
                  K_eff_PR = K^2 / ||R||_F^2  (= trace(R)^2 / sum lambda^2).
  ST-5  K_eff_max: standardise each candidate column over draws to zero mean
                  and unit variance, giving W (D x K); take z_max(d) = max_k
                  W[d,k]; K_eff_max is the K' for which K' iid standard normals
                  have E[max] equal to the measured mean of z_max.  This is the
                  "effective number of independent candidates" in the sense
                  that enters an extreme-value advantage law.  Two versions:
                  K_eff_max_raw (on S) and K_eff_max_ctr (on the group-mean-
                  removed S).
  ST-6  K_eff_trail = (sum_{j>=2} lambda_j)^2 / sum_{j>=2} lambda_j^2, the
                  participation ratio of R_raw's spectrum WITH THE TOP
                  EIGENVALUE DROPPED.  THIS IS T1's PRIMARY OBSERVABLE; see
                  the amendment note in section 1a for why.
  ST-7  var_cv = coefficient of variation, across candidates, of the marginal
                  variance Var_d(S_k).  The law predicts every candidate has
                  the same variance 1/2N, and a common mode does not change
                  that, so this channel is independent of ST-6.

--------------------------------------------------------------------------
1a.  AMENDMENT TO THIS PRE-REGISTRATION, MADE BEFORE ANY MEASUREMENT RUN AND
     RECORDED RATHER THAN HIDDEN
--------------------------------------------------------------------------
The first draft of this file made offdiag(R_ctr) the primary observable.  A
SYNTHETIC smoke test of the analysis code -- no lattice, no sieve, no research
object, run before the build stage was ever executed -- showed that statistic
is FORCED:

    if Cov(S) = (1-rho) I + rho 11^T  (any exchangeable structure), then
    centring by P = I - J/K gives P Cov P = (1-rho) P, so the centred
    correlation matrix is the normalised projector and its mean off-diagonal
    is EXACTLY -1/(K-1) for EVERY rho.

More generally, whenever the marginal variances are equal, the centred
correlation matrix has row sums exactly zero, so offdiag(R_ctr) = -1/(K-1)
identically.  Measured on synthetic data with rho = 0.30: real -0.1428, and the
CAL-PERM comparator's spread across realisations was 0.0000.  A statistic whose
comparator has zero spread is KN-TECH-9d21c4 mode 1 -- a control that cannot
fail -- committed by this producer, in its own design, and caught by the
instrument check that exists for that purpose.

The consequence, stated plainly: an EXCHANGEABLE structure has exactly one
parameter, and the forced common mode F-1 already fixes it.  So the informative
question is not "is there correlation" (forced, F-1) but "is the structure
ONE common mode plus independent residual, or is there MORE".  That question is
answered by the TRAILING spectrum:

    under the law            R_raw = I      -> trailing eigenvalues all 1
    under law + common mode  R_raw = rank-1 + (1-rho)I
                                            -> trailing eigenvalues all equal
    in both cases            K_eff_trail = K - 1 EXACTLY

so K_eff_trail = K-1 is predicted by the law AND by the forced alternative,
and any departure is neither the law's prediction nor a construction artifact.
ST-6 is therefore the primary observable, with ST-5 (centred) and ST-7 as the
two other non-forced channels.  offdiag(R_ctr) is still reported, labelled
FORCED, because reporting it is the evidence that this defect was found.

Nothing had been measured when this amendment was made: the build stage had not
been run, no sieve had been called, and no research number existed.  The
amendment is a pre-registration, not an adjustment of a frozen prediction.

--------------------------------------------------------------------------
2.  WHAT THE LAW PREDICTS FOR EACH -- STATED BEFORE THE MEASUREMENT
--------------------------------------------------------------------------
Under (I-b), the K wrong-candidate scores are iid.  Then, with D draws:

  P-1  R_raw = I.  offdiag(R_raw) = 0, with sampling sd 1/sqrt(D)
       (D = 4000 -> 0.0158;  D = 2000 -> 0.0224).
  P-2  lambda_max(R_raw) ~ (1 + sqrt(K/D))^2  (Marchenko-Pastur edge).
       K=8, D=4000 -> 1.0904.   K=25, D=4000 -> 1.1671.
  P-3  K_eff_PR(R_raw) = K, less O(K(K-1)/D).
  P-4  Centring removes exactly one degree of freedom and is NOT evidence of
       dependence: under (I-b), R_ctr has offdiag = -1/(K-1) EXACTLY,
       eigenvalues {0 once, K/(K-1) with multiplicity K-1}, and
       K_eff_PR(R_ctr) = K-1 EXACTLY.
       K=8  -> offdiag -0.142857, lambda_max 1.142857, K_eff_PR 7.
       K=25 -> offdiag -0.041667, lambda_max 1.041667, K_eff_PR 24.
       Per section 1a this holds under the ALTERNATIVE too and is FORCED.
  P-5  K_eff_max_raw = K, K_eff_max_ctr = K.
  P-6  K_eff_trail = K-1.   K=8 -> 7,  K=25 -> 24,  K=512 -> 511.
       PREDICTED BY THE LAW AND BY THE FORCED COMMON-MODE ALTERNATIVE ALIKE.
  P-7  var_cv = 0 up to sampling noise sqrt(2/D) per candidate.

--------------------------------------------------------------------------
3.  FORCED VALUES -- WHAT THE CONTRAST MUST BE UNDER THE NULL NOT BEING
    TESTED (KN-TECH-9d21c4 obligation 4), DERIVED BEFORE MEASURING
--------------------------------------------------------------------------
The null NOT being tested here is the structural alternative: that the
across-candidate covariance is fixed by the geometry of the database and the
definition of the candidate set, independently of any independence assumption.
It has an EXACT closed form (exact, not first order, for Gaussian e):

    S_k = (1/N) sum_i [ cos(u_i) cos(phi_ik) - sin(u_i) sin(phi_ik) ],
        u_i   = 2 pi x_i . e / q ,     phi_ik = 2 pi (y_i.(s-c_k) mod q) / q

For e ~ N(0, sigma^2 I_m), u is centred Gaussian with
Cov(u_i,u_i') = (2 pi/q)^2 sigma^2 x_i.x_i'.  Writing c = (1/2)(2 pi sigma/q)^2,
n_i = ||x_i||^2, G = X X^T, P_ii' = exp(-c(n_i+n_i')), T = 2 c G:

    Cov(cos u) = C = P .* (cosh T - 1)          [E cos u_i = exp(-c n_i)]
    Cov(sin u) = S = P .* sinh T
    Cov(cos u_i, sin u_i') = 0                  EXACTLY, by u -> -u symmetry

    ==>  Cov(S_k, S_k') = (1/N^2) [ a_k^T C a_k'  +  b_k^T S b_k' ]
         with a_ik = cos phi_ik,  b_ik = sin phi_ik.

This predicts the ENTIRE correlation matrix WITH NO SCORING, from the x-database
Gram matrix and the y columns alone.  It is computed and printed BEFORE the
scoring block in the measure run; the log ordering is the evidence.

FORCED CONSEQUENCE F-1 (near-miss group, R_raw).  For near-miss candidates
c_k = s + unit_k the offset is phi_ik = -2 pi Y[i,k]/q with rms |Y| ~ 2.27, so
rms(phi) ~ 0.112 rad and cos(phi_ik) = 1 - O(0.006) for EVERY k.  The a_k^T C a_k'
term is then the same number for every pair (k,k'): a rank-one common mode.
Taking C, S diagonal for the estimate, with a_x = 0.888475 (archived),
    common var  ~ Cbar/N,  Cbar = (1+exp(-4 a_x))/2 - exp(-2 a_x) = 0.34518
    discrim var ~ Sbar rms(phi)^2 /N, Sbar = (1-exp(-4 a_x))/2 = 0.48568
    ratio       = 0.48568 * 0.012600 / 0.34518 = 0.017726
    ==> offdiag(R_raw, near-miss)  ~  1/(1+0.017726)  =  0.98258
R_raw on the near-miss group is therefore FORCED to sit just below 1 whatever
the answer to (I-b) is.  PRE-REGISTERED PREDICTION: 0.95 to 0.995.  Reporting a
large R_raw as a finding would be this campaign's fifth construction-determined
quantity, and it is declared uninformative HERE, before it is measured.

FORCED CONSEQUENCE F-2 (uniform group, R_raw).  For uniform candidates the
offsets phi_ik are uniform on the circle and independent across k, so there is
no common mode: offdiag(R_raw, uniform) ~ 0.  This is also forced, and it is
forced to agree with the law, so agreement there is not evidence either.
Consistency check the same algebra supplies: marginal Var(S_k) ~ (Cbar+Sbar)/2N
= 0.4154/N ~ 1/2N, which is why every batch's uniform group returns
sd_ratio_to_iid ~ 1.

CONSEQUENCE F-3.  Because R_raw is forced on BOTH groups, and because
offdiag(R_ctr) is forced to -1/(K-1) by centring (section 1a), the informative
observables are ST-6, ST-5-centred and ST-7.  Nothing forces those: the exact
closed form gives, to leading order in the small offsets,
    Cov_ctr(k,k') ~ (1/N^2) b_k^T S b_k' ,   b_ik = sin(phi_ik) ~ -2 pi Y[i,k]/q
and if the Y columns were orthogonal in the S-metric the trailing spectrum
would be exactly flat -- the law's own answer.  A departure is a statement
about the alignment of the Y columns with the x-database kernel S, and is NOT
implied by the definitions.

EXPECTATION STATED BEFORE THE RUN (falsifiable, and recorded whichever way it
falls).  Near-miss group: K_eff_trail BELOW K-1 and K_eff_max_ctr BELOW K,
because RT-20260804-37a8f2 measured rho = sum_{i!=i'} <y_i,y_i'>K(i,i') /
sum_i ||y_i||^2 K(i,i) = +0.718 on this same database, which is the same
quadratic form b^T S b contracted differently; MAGNITUDE NOT PREDICTED.
Uniform group: agreement with the law within sampling error.  If the near-miss
group also agrees, that is recorded as agreement -- agreement is as reportable
as departure (GOAL-MLKEM-004 scope_discipline).

--------------------------------------------------------------------------
4.  THE NULLS.  Object, statistic, comparator, threshold -- all before the run.
    (EV-MLKEM-ba6c25 INT-3: batch 4's sensitivity demonstration was scored
    against whichever arm flattered it.)
--------------------------------------------------------------------------
TWO COMPARATORS, and the rule that the COMPARATOR supplies the REFERENCE.
    A second synthetic instrument check, again before any measurement, showed
    that the law's ASYMPTOTIC values are the wrong reference at finite D:
    K_eff_trail's finite-D null sits at 6.989 rather than 7 for D=4000, K=8, and
    K_eff_max_ctr's null sits at ~9.6 rather than 8 because centring imposes
    sum_k W_k = 0 and inflates the standardised max by ~sqrt(K/(K-1)).  Scoring
    against K-1 and K would have manufactured a 4-sigma "departure" out of
    genuinely iid data.  So every z below takes BOTH its reference and its
    spread from a named comparator, and the asymptotic value is reported beside
    it as the population target rather than used as the test reference.

CAL-PERM  -- CALIBRATION ARM, EXPLICITLY NOT A NULL.
    Object removed: the sharing of a draw index between candidates.  Realised
    by permuting the draw index INDEPENDENTLY per candidate column of the
    already-computed score matrix.  This preserves every candidate's marginal
    distribution EXACTLY and destroys across-candidate dependence EXACTLY.
    It CANNOT fail: R = I is true by construction.  It is therefore labelled a
    calibration arm and NOT a null (the batch-1 failure, KN-TECH-9d21c4 mode 1,
    was to run exactly this kind of object and call it a control).  Its job is
    to supply the finite-D sampling distribution of every statistic under
    (I-b), which is the comparator all thresholds below are stated against.

CAL-IID  -- the LAW's OWN null object, also a calibration arm and not a null.
    iid standard-normal columns at the same (D, K).  Needed because var_cv
    (ST-7) is EXACTLY invariant under CAL-PERM's per-column permutation, so
    CAL-PERM is a zero-spread comparator for it -- KN-TECH-9d21c4 mode 1 a
    second time, again caught by a synthetic check before any measurement.
    ST-7's z is taken against CAL-IID; ST-6 and ST-5c take theirs against
    CAL-PERM, whose conditional-on-marginals construction is what makes them
    tests of DEPENDENCE rather than of marginal shape.

NULL-IIDPHASE -- the null that can fail.
    Object removed: the SHORTNESS AND STRUCTURE of the phase offsets, i.e. the
    fact that y is a short dual vector.  Y is replaced by uniform residues mod
    q on the SAME X.  Preserved: X, the database geometry, N, the candidate
    set, the error draws, the scoring code.  This is the law's own model of the
    offsets, so under (I-b) it must return the law's values.
    Statistic: ST-3 and ST-5 on R_ctr, same as the real arm.
    Can it fail: YES.  Archived dynamic range on this exact statistic family:
    sd_ratio 0.940056 measured (VAL-20260804-a84239 section 2) against
    SENS-1 (y := 0) at 6.19e-15 -- range [0, ~1].

SENS-GRADED -- THE SENSITIVITY DEMONSTRATION, with a NAMED COMPARATOR and a
    THRESHOLD DECLARED BEFORE THE RUN.
    Comparator: the CAL-PERM arm of the SAME group at the SAME D and K.
    Construction: synthetic score matrices W = sqrt(1-t) Z_k + sqrt(t) Z_0 with
    Z independent standard normal, D and K matched to the real arms, for
    t in {0.00, 0.05, 0.15, 0.30, 0.50, 0.75}.  The induced population
    off-diagonal correlation is EXACTLY t.
    THRESHOLD, declared here before the run:  the estimator passes only if
      (i) |offdiag(R_raw) - t| <= 0.02 for every t; AND
      (ii) K_eff_max is monotone non-increasing in t; AND
      (iii) at t = 0 the estimator returns offdiag within 3/sqrt(D) of 0 and
            K_eff_max within a factor 1.5 of K.
    If any of (i)-(iii) fails the instrument is declared unfit and T1 reports
    NO dependence measurement.  This is run BEFORE the real arms are scored.

--------------------------------------------------------------------------
5.  THE FROZEN DECISION RULE, WITH ITS ALTERNATIVE-EXHAUSTIVENESS ARGUMENT
    (the fifth obligation this batch adds; DEC-20260804-5c9fe1 NA-3)
--------------------------------------------------------------------------
On a group of size K let
    z1 = (K_eff_trail   - mean_CALPERM(K_eff_trail))   / sd_CALPERM(K_eff_trail)
    z2 = (K_eff_max_ctr - mean_CALPERM(K_eff_max_ctr)) / sd_CALPERM(K_eff_max_ctr)
    z3 = (var_cv        - mean_CALIID (var_cv))        / sd_CALIID (var_cv)
Named comparators: CAL-PERM for z1 and z2, CAL-IID for z3, each the arm of the
SAME group at the SAME D and K.  Threshold 3, declared here before the run.

  D1 NO_DETECTED_DEPARTURE      : |z1| <= 3 and |z2| <= 3 and |z3| <= 3.
  D2 DEPARTURE_FEWER_EFFECTIVE  : (z1 < -3 or z2 < -3) and not (z1 > 3 or z2 > 3).
  D3 DEPARTURE_MORE_EFFECTIVE   : (z1 >  3 or z2 >  3) and not (z1 < -3 or z2 < -3).
  D4 DEPARTURE_IN_VARIANCE_ONLY : |z1| <= 3 and |z2| <= 3 and |z3| > 3.
  D0 NEITHER                    : everything else.  This includes, and each is
       named because each is a way reality can supply an outcome the other four
       branches cannot hold: (i) z1 and z2 of OPPOSITE sign and both past 3 --
       the two effective-count channels disagreeing, which no directional label
       can honestly cover; (ii) any statistic non-finite; (iii) a degenerate or
       rank-deficient correlation matrix; (iv) the SENS-GRADED gate failing;
       (v) the CAL-PERM comparator not returning its own forced values, or
       returning zero spread, which would make every z above meaningless.

EXHAUSTIVENESS ARGUMENT, required before the rule is frozen (the fifth
obligation).  Restrict first to the case where z1, z2, z3 are all finite and
the instrument gates pass; call it the finite case.  Write
a = [z1 < -3 or z2 < -3] and b = [z1 > 3 or z2 > 3].  The pair (a,b) takes
exactly four values and they partition the finite case:
    (F,F) -> |z1|,|z2| <= 3, split by |z3| into D1 and D4;
    (T,F) -> D2;   (F,T) -> D3;   (T,T) -> D0(i).
There is no fifth value of a two-bit pair, so D1..D4 plus D0(i) exhaust the
finite case.  D0(ii)-(v) is exactly the complement of the finite case.  Hence
D0,D1,D2,D3,D4 partition the whole outcome space by construction, not by
enumeration of the outcomes I happened to think of.
ACTION IN D0, declared now: report the correlation matrices, the spectra and
every statistic verbatim, attach no directional label, name which sub-case
fired, and hand it to the Coordinator without a reading.  (Batch 4 froze a
two-outcome rule, reality supplied a third, and the producer had to report
C_NEITHER with no branch to put it in.  This rule has that branch, and the
(T,T) sub-case is there because two channels CAN disagree.)

--------------------------------------------------------------------------
6.  T0's RULE, likewise exhaustive
--------------------------------------------------------------------------
T0 measures the near-miss row-permutation excess of two arms that differ in ONE
line: NORMMATCH_RANDDIR_INDEP (Gx, Gy drawn independently -- surrogate.py
lines 685-688) and NORMMATCH_RANDDIR_COUPLED (y_i := normalise(R^T x_i) *
||y_i||_sieve, R a fixed random m x n matrix -- RT-20260804-37a8f2 section 5).
Reference value to confirm or refute: 12.1507.
  T0-CONFIRMS : coupled excess within +-15% of 12.1507.
  T0-SAME-DIRECTION : coupled excess > 3 x the sieve arm's excess but outside
                      +-15%.  Direction reproduced, magnitude not.
  T0-REFUTES  : coupled excess <= 3 x the sieve arm's excess.
  T0-NEITHER  : non-finite, or a failed certificate/instrument check.
Exhaustive: the first three partition the finite positive reals by two nested
comparisons; T0-NEITHER is the complement.

--------------------------------------------------------------------------
7.  WHAT IS NOT PRE-REGISTERED, STATED PLAINLY
--------------------------------------------------------------------------
- The closed form in section 3 is derived here for the first time in this
  campaign, but it is derived from the same score definition batches 1-4 used
  and it specialises to RT-20260804-37a8f2's rho and to VAL-20260804-a84239's
  first-order model.  It is pre-registered with respect to every number this
  run produces and post hoc with respect to those two archived reviews.
- The numeric prediction 0.98258 in F-1 uses the ARCHIVED a_x = 0.888475 and a
  diagonal approximation to C and S.  The exact closed form (no diagonal
  approximation) is computed in the run.  Both are reported.
- Sieve N is whatever bgj1 returns; no prediction is made about it.
==============================================================================
"""

# CHANGELOG (recorded, not hidden -- AGENTS.md rule 8)
#   v1  drafted with offdiag(R_ctr) as T1's primary observable.  NEVER RUN
#       against any research object: no build stage, no sieve call, no research
#       number.  Only the synthetic instrument checks were executed.
#   v2  the version run.  Amendment recorded in section 1a of the docstring: the
#       synthetic smoke test of v1's analysis code showed offdiag(R_ctr) is
#       forced to -1/(K-1) whenever the marginal variances are equal, with the
#       CAL-PERM comparator returning ZERO spread -- a KN-TECH-9d21c4 mode-1
#       defect in this producer's own design, caught before any measurement.
#       ST-6 (trailing-spectrum participation ratio) becomes the primary
#       observable because it equals K-1 under the law AND under the forced
#       common-mode alternative alike.  ST-5 gains a centred variant; ST-7 is
#       new.  The decision rule is rewritten in terms of ST-6/ST-5ctr/ST-7 and
#       its exhaustiveness argument is rewritten with it.  offdiag(R_ctr) is
#       still computed and reported, labelled FORCED.
#       This is a pre-registration made before the first measurement run, not an
#       adjustment of a frozen prediction after runs began.
#   v3  the version run.  A second synthetic instrument check, again with no
#       research object, found two more defects in this producer's own design
#       and both are fixed here and recorded rather than hidden:
#       (a) scoring z1/z2 against the ASYMPTOTIC values K-1 and K manufactured a
#           ~4-sigma departure out of genuinely iid data, because the finite-D
#           null of K_eff_trail sits at 6.989 not 7, and because centring
#           imposes sum_k W_k = 0 and inflates the standardised max so that
#           K_eff_max_ctr's null sits near 9.6 not 8 at K=8.  The comparator now
#           supplies BOTH reference and spread; the asymptotic value is reported
#           beside it, not used as the test reference.
#       (b) var_cv (ST-7) is EXACTLY invariant under CAL-PERM, so CAL-PERM was a
#           zero-spread comparator for it -- mode 1 a second time.  CAL-IID, the
#           law's own null at matched (D,K), is added and governs z3.
#       Verified on synthetic structures before the build run: iid -> z1 ~ 0;
#       pure common mode at rho = 0.3 and 0.9 -> z1 ~ 0 (ST-6 is invariant to
#       the forced common mode, as designed); common mode PLUS a second factor
#       -> z1 ~ -2500.  No research object was touched by any of this.

import argparse, hashlib, json, os, platform, resource, subprocess, sys, time
import numpy as np

SCRIPT_VERSION = "dependence.py v1 TASK-20260804-f58d34"
TWOPI = 2.0 * np.pi
Q, M_, N_ = 127, 35, 25
D_ = M_ + N_
SIGMA = 2.0
ETA = 2
INSTANCE_SEED = 20260803206          # BATCH-f75059 replicate 0, inherited

K_LAT, K_FFT, K_ENUM = 15, 10, 0     # BATCH-c45baf admissible Stage B tuple
P_VALUES = (2, 3, 5)
BETA_SIEVE = 50                      # = m + k_lat, the Stage B sieve dimension

ARCHIVE = dict(
    source="BATCH-c45baf/TASK-20260803-db170f/stage_a_results.json; "
           "BATCH-d3a45a/TASK-20260804-7e6b54/results.json",
    rep0_seed=20260803206, rep0_n_vectors=17919,
    rep0_a_x=0.888475041394716, rep0_mean_xnorm2=181.49430213739606,
    rep0_mean_ynorm2=129.08153357330208,
    b4_sieve_excess=1.2704, b4_matched_bkz_excess=5.4311,
    b4_randdir_indep_excess=1.0868,
    rt_coupled_randdir_excess=12.1507,          # the number T0 confirms/refutes
    rt_rho_sieve=0.718,
    stage_b_n_vectors=4253,
)

PREREG = dict(
    frozen_note="Written into this file before the build run and not edited after.",
    law_R_raw="identity; offdiag 0 +- 1/sqrt(D)",
    law_offdiag_ctr_K8=-1.0 / 7.0,
    law_offdiag_ctr_K25=-1.0 / 24.0,
    law_lambda_max_ctr_K8=8.0 / 7.0,
    law_K_eff_PR_ctr_K8=7.0,
    law_K_eff_max="= K (both raw and centred)",
    law_K_eff_trail="= K-1, under the law AND under the forced common-mode "
                    "alternative alike -- ST-6 is T1's PRIMARY observable",
    law_var_cv="0 up to sampling noise sqrt(2/D) per candidate",
    forced_offdiag_R_ctr="-1/(K-1) EXACTLY whenever the marginal variances are "
                         "equal; FORCED, reported but not read (section 1a)",
    forced_F1_nearmiss_R_raw_offdiag=0.98258,
    forced_F1_predicted_band=[0.95, 0.995],
    forced_F2_uniform_R_raw_offdiag=0.0,
    expectation_nearmiss="K_eff_trail BELOW K-1 and K_eff_max_ctr BELOW K "
                         "(branch D2); MAGNITUDE NOT PREDICTED",
    expectation_uniform="agreement with the law within sampling error (D1)",
    expectation_note="Agreement is as reportable as departure.  If the near-miss "
                     "group returns D1 that is recorded as the observation.",
    sens_graded_thresholds=dict(offdiag_abs_err_max=0.02,
                                K_eff_max_monotone_in_t=True,
                                t0_offdiag_within="3/sqrt(D) of 0",
                                t0_Keffmax_within_factor=1.5),
    T0_reference_value=12.1507, T0_confirm_band_rel=0.15,
    T0_same_direction_multiple_of_sieve=3.0,
    decision_branches=["D1", "D2", "D3", "D4", "D0"],
    T0_branches=["T0-CONFIRMS", "T0-SAME-DIRECTION", "T0-REFUTES", "T0-NEITHER"],
)


# --------------------------------------------------------------------------
# helpers copied VERBATIM from BATCH-d3a45a/surrogate.py (itself verbatim from
# BATCH-c45baf/stage_a.py) so the instance regenerates bit for bit
# --------------------------------------------------------------------------
def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def to_intmat(M):
    from fpylll import IntegerMatrix
    A = IntegerMatrix(M.shape[0], M.shape[1])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            A[i, j] = int(M[i, j])
    return A


def from_intmat(A):
    return np.array([[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
                    dtype=np.int64)


def build_dual_basis(A, q, m, n):
    d = m + n
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A
    B[m:, m:] = q * np.eye(n, dtype=np.int64)
    return B


def c4(k):
    from math import lgamma, sqrt, exp
    return sqrt(2.0 / (k - 1)) * exp(lgamma(k / 2.0) - lgamma((k - 1) / 2.0))


def certify(X, Y, A, q, label, bigint_rows=400, seed=1):
    """Dual-lattice membership certificate.  Recomputed from A and the emitted
    integers alone, independent of whatever produced them.  Two arithmetics:
    numpy int64, and EXACT Python bigint on a random row sample, which cannot
    silently overflow.  This certifies the VECTORS.  It is not a solve
    certificate: no discrete log is claimed and no factor-base relation."""
    N = X.shape[0]
    resid = np.mod(X.dot(A) - Y, q)
    n_bad = int(np.count_nonzero(resid))
    V = np.concatenate([X, Y], axis=1)
    n_zero = int(np.count_nonzero(np.all(V == 0, axis=1)))
    n_dup = int(N - len(set(map(tuple, V.tolist()))))
    n_dup_x = int(N - len(set(map(tuple, X.tolist()))))
    rng = np.random.default_rng(seed)
    rows = rng.choice(N, size=min(bigint_rows, N), replace=False)
    bad_big = 0
    Al = A.tolist()
    for i in rows:
        xi = [int(t) for t in X[i]]
        for j in range(A.shape[1]):
            acc = 0
            for k in range(A.shape[0]):
                acc += xi[k] * int(Al[k][j])
            if (acc - int(Y[i, j])) % q != 0:
                bad_big += 1
    headroom = int(np.abs(X).max()) * (q - 1) * A.shape[0]
    return dict(
        kind="lattice_membership", family=label,
        statement="every emitted vector v=(x,y) satisfies y == A^T x (mod q)",
        checked_vectors=int(N), checked_entries=int(N * A.shape[1]),
        violating_entries=n_bad,
        bigint_rows_checked=int(len(rows)), bigint_violating_entries=int(bad_big),
        int64_headroom_bound=headroom, int64_headroom_ok=bool(headroom < 2 ** 62),
        all_zero_vectors=n_zero, duplicate_vectors=n_dup, duplicate_x_rows=n_dup_x,
        verified=bool(n_bad == 0 and n_zero == 0 and n_dup == 0 and bad_big == 0),
        method="numpy int64 AND exact Python bigint on a random row sample, "
               "from A and the emitted vectors only",
        solve_claim_certificate="none -- pure measurement run.  No discrete-log "
                                "solve and no factor-base relation is claimed, "
                                "so docs/claims-and-verification.md kind=none "
                                "applies to the SOLVE claim; the membership "
                                "certificate above certifies the vectors only.")


def run_sieve(B_int, sieve_name, fpylll_seed, sieve_seed, split):
    """g6k is used HERE ONLY.  B_int is the integer dual basis; `split` is the
    number of leading coordinates that form x."""
    from fpylll import LLL, FPLLL
    from g6k import Siever, SieverParams
    Bfp = to_intmat(B_int)
    FPLLL.set_random_seed(fpylll_seed)
    t0 = time.time()
    Bred = LLL.reduction(Bfp)
    t_lll = time.time() - t0
    g = Siever(Bred, SieverParams(threads=1), seed=sieve_seed)
    g.initialize_local(0, 0, B_int.shape[0])
    t0 = time.time()
    getattr(g, sieve_name)()
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    V = coeffs.dot(from_intmat(g.M.B))
    return V[:, :split], V[:, split:], dict(lll_seconds=round(t_lll, 3),
                                            sieve_seconds=round(t_sieve, 3))


def canonical_keys(V):
    Vc = V.copy()
    nz = np.argmax(Vc != 0, axis=1)
    lead = Vc[np.arange(Vc.shape[0]), nz]
    Vc[lead < 0] *= -1
    return [bytes(row) for row in Vc.astype(np.int64).view(np.uint8).reshape(
        Vc.shape[0], -1)]


# --------------------------------------------------------------------------
# scoring core -- identical in form to surrogate.py / stage_a.py
# --------------------------------------------------------------------------
def score_means(Xf, cosPhi, sinPhi, D, block, seed, m, q, sigma):
    """means[draw, candidate].  BOUNDED BY COUNTS ONLY."""
    N, K = cosPhi.shape
    means = np.empty((D, K))
    rng = np.random.default_rng(seed)
    off = 0
    while off < D:                      # count-bounded; no clock in the test
        b = min(block, D - off)
        E = np.rint(rng.normal(0.0, sigma, size=(m, b))).astype(np.int64)
        U = Xf.dot(E.astype(np.float64))
        Cu = np.cos(TWOPI * U / q).T
        Su = np.sin(TWOPI * U / q).T
        means[off:off + b] = (Cu.dot(cosPhi) - Su.dot(sinPhi)) / N
        off += b
    return means


def phases(Y, s, C, q, integer_Y=True):
    off = Y.dot((s[None, :] - C).T)
    if integer_Y:
        off = np.mod(off, q).astype(np.float64)
    return np.cos(TWOPI * off / q), np.sin(TWOPI * off / q)


def sd_ratio(means, idxs, N):
    return means[:, idxs].std(axis=1, ddof=1) / np.sqrt(0.5 / N)


# --------------------------------------------------------------------------
# T0: the row-permutation excess, exactly the batch-4 statistic
# --------------------------------------------------------------------------
def rowperm_excess(X, Y, s, C, idxs, cfg, seeds, tag, integer_Y=True):
    N = X.shape[0]
    Xf = X.astype(np.float64)
    cosPhi, sinPhi = phases(Y, s, C, cfg["q"], integer_Y)
    m_real = score_means(Xf, cosPhi, sinPhi, cfg["draws"], cfg["block"],
                         seeds["error_draws"], cfg["m"], cfg["q"], cfg["sigma"])
    real = float(sd_ratio(m_real, idxs, N).mean())
    rng = np.random.default_rng(seeds["rowperm"] + (sum(map(ord, tag)) % 10 ** 6))
    rp = []
    for _ in range(cfg["n_rowperm"]):          # count-bounded
        pi = rng.permutation(N)
        mm = score_means(Xf, cosPhi[pi], sinPhi[pi], cfg["draws"], cfg["block"],
                         seeds["error_draws"], cfg["m"], cfg["q"], cfg["sigma"])
        rp.append(float(sd_ratio(mm, idxs, N).mean()))
    rp = np.array(rp)
    return dict(real_sd_ratio_to_iid=real,
                rowperm_sd_ratio_to_iid_mean=float(rp.mean()),
                rowperm_sd_across_realisations=float(rp.std(ddof=1)),
                n_rowperm_realisations=int(rp.size),
                excess_real_over_rowperm=float(real / rp.mean()),
                excess_z_vs_surrogate_spread=float((real - rp.mean())
                                                   / (rp.std(ddof=1) + 1e-300)))


# --------------------------------------------------------------------------
# T1/T2: the dependence statistics  (ST-1 .. ST-5)
# --------------------------------------------------------------------------
_AK_CACHE = {}
_ZGRID = np.linspace(-12.0, 18.0, 300001)
_PHI = 0.5 * (1.0 + np.vectorize(__import__("math").erf)(_ZGRID / np.sqrt(2.0)))


def expected_max_iid(Kp):
    """E[max of Kp iid standard normals], by quadrature of
       E[max] = int_0^inf (1 - Phi^K) dz  -  int_{-inf}^0 Phi^K dz.
    Deterministic, no Monte Carlo, valid for any K.  Cached."""
    Kp = int(Kp)
    if Kp in _AK_CACHE:
        return _AK_CACHE[Kp]
    with np.errstate(divide="ignore"):
        logPhi = np.where(_PHI > 0, np.log(np.maximum(_PHI, 1e-300)), -np.inf)
    F = np.exp(Kp * logPhi)
    pos = _ZGRID >= 0.0
    v = float(np.trapezoid(1.0 - F[pos], _ZGRID[pos])
              - np.trapezoid(F[~pos], _ZGRID[~pos]))
    _AK_CACHE[Kp] = v
    return v


def expected_max_iid_mc(Kp, n_mc=100000, seed=987654321):
    """Monte-Carlo cross-check of expected_max_iid.  Control only."""
    Kp = int(Kp)
    rng = np.random.default_rng(seed + Kp)
    blk = max(1, min(20000, 2_000_000 // max(1, Kp)))
    tot, done = 0.0, 0
    while done < n_mc:                          # count-bounded
        b = min(blk, n_mc - done)
        tot += rng.standard_normal((b, Kp)).max(axis=1).sum()
        done += b
    return tot / n_mc


_AK_GRID = None


def keff_from_max(zmax_mean):
    """Invert E[max of K' iid standard normals] = zmax_mean for K'."""
    global _AK_GRID
    if _AK_GRID is None:
        ks = np.unique(np.round(np.logspace(np.log10(2), np.log10(1e7), 160))
                       ).astype(np.int64)
        _AK_GRID = (ks, np.array([expected_max_iid(int(k)) for k in ks]))
    ks, av = _AK_GRID
    if not np.isfinite(zmax_mean):
        return float("nan")
    if zmax_mean <= av[0]:
        return float(ks[0])
    if zmax_mean >= av[-1]:
        return float(ks[-1])
    return float(np.exp(np.interp(zmax_mean, av, np.log(ks.astype(float)))))


R_STORE_MAX_K = 32          # full matrices archived only for small groups


def dep_stats(M, idxs, store_R=True):
    """All five statistics on the D x |idxs| block of a score matrix."""
    G = np.asarray(M[:, idxs], dtype=np.float64)
    D, K = G.shape
    out = dict(K=int(K), D=int(D))
    offmask = ~np.eye(K, dtype=bool)
    _spec = {}
    for name, A in (("raw", G), ("ctr", G - G.mean(axis=1, keepdims=True))):
        sd = A.std(axis=0, ddof=1)
        if not np.all(np.isfinite(sd)) or np.any(sd <= 0):
            out[name] = dict(degenerate=True)
            continue
        R = np.corrcoef(A, rowvar=False)
        if not np.all(np.isfinite(R)):
            out[name] = dict(degenerate=True)
            continue
        ev = np.sort(np.linalg.eigvalsh(R))[::-1]
        _spec[name] = ev
        off = R[offmask]
        out[name] = dict(
            degenerate=False,
            offdiag_mean=float(off.mean()), offdiag_mean_abs=float(np.abs(off).mean()),
            offdiag_sd=float(off.std(ddof=1)),
            offdiag_min=float(off.min()), offdiag_max=float(off.max()),
            lambda_max=float(ev[0]), lambda_min=float(ev[-1]),
            frob_sq=float((R ** 2).sum()),
            K_eff_PR=float(K ** 2 / (R ** 2).sum()),
            eigenvalues_top20=[float(v) for v in ev[:20]],
            R=([[float(v) for v in row] for row in R]
               if (store_R and K <= R_STORE_MAX_K) else
               "not archived: K=%d > %d; recompute from vectors.json"
               % (K, R_STORE_MAX_K)))
    # ST-5, on temporally standardised columns.  raw and group-mean-removed.
    for name, A in (("K_eff_max", G), ("K_eff_max_ctr",
                                       G - G.mean(axis=1, keepdims=True))):
        mu, sd = A.mean(axis=0), A.std(axis=0, ddof=1)
        if np.all(np.isfinite(sd)) and np.all(sd > 0):
            zmax = ((A - mu) / sd).max(axis=1)
            out[name] = dict(
                zmax_mean=float(zmax.mean()),
                zmax_sd=float(zmax.std(ddof=1)),
                zmax_sem=float(zmax.std(ddof=1) / np.sqrt(D)),
                iid_reference_E_max_K=float(expected_max_iid(K)),
                K_eff_max=float(keff_from_max(float(zmax.mean()))),
                K_nominal=int(K))
        else:
            out[name] = dict(degenerate=True)

    # ST-6, the PRIMARY observable: trailing-spectrum participation ratio.
    # Reuses R_raw's spectrum, computed once in the loop above.
    if not out["raw"].get("degenerate"):
        ev = _spec["raw"]
        tr = ev[1:]
        out["K_eff_trail"] = dict(
            value=float(tr.sum() ** 2 / (tr ** 2).sum()),
            law_and_common_mode_prediction=float(K - 1),
            lambda_1=float(ev[0]),
            trailing_mean=float(tr.mean()), trailing_sd=float(tr.std(ddof=1)),
            trailing_max=float(tr.max()), trailing_min=float(tr.min()),
            note="K-1 under the law (R=I) AND under law-plus-one-common-mode; "
                 "a departure is neither the law's value nor a forced artifact")
    else:
        out["K_eff_trail"] = dict(degenerate=True)

    # ST-7, marginal-variance heterogeneity across candidates.
    v = G.var(axis=0, ddof=1)
    out["var_cv"] = dict(
        value=float(v.std(ddof=1) / v.mean()) if v.mean() > 0 else float("nan"),
        mean_variance=float(v.mean()),
        law_prediction="0 up to sampling noise sqrt(2/D) per candidate",
        sampling_noise_scale=float(np.sqrt(2.0 / D)))
    return out


def cal_perm_arm(M, idxs, n_real, seed):
    """CALIBRATION arm.  Permutes the draw index independently per candidate
    column.  Marginals exact, dependence destroyed exactly.  CANNOT FAIL --
    declared a calibration arm, not a null."""
    G = np.asarray(M[:, idxs], dtype=np.float64)
    D, K = G.shape
    rng = np.random.default_rng(seed)
    reals = []
    for _ in range(n_real):                     # count-bounded
        H = np.empty_like(G)
        for k in range(K):
            H[:, k] = G[rng.permutation(D), k]
        reals.append(dep_stats(H, list(range(K)), store_R=False))
    def gather(path):
        vals = []
        for r in reals:
            v = r
            for p in path:
                v = v[p]
            vals.append(float(v))
        a = np.array(vals)
        return dict(mean=float(a.mean()),
                    sd=float(a.std(ddof=1)) if a.size > 1 else None,
                    n=int(a.size))
    return dict(
        n_realisations=int(n_real),
        raw_offdiag=gather(["raw", "offdiag_mean"]),
        raw_lambda_max=gather(["raw", "lambda_max"]),
        raw_K_eff_PR=gather(["raw", "K_eff_PR"]),
        ctr_offdiag=gather(["ctr", "offdiag_mean"]),
        ctr_lambda_max=gather(["ctr", "lambda_max"]),
        ctr_K_eff_PR=gather(["ctr", "K_eff_PR"]),
        K_eff_trail=gather(["K_eff_trail", "value"]),
        K_eff_max=gather(["K_eff_max", "K_eff_max"]),
        K_eff_max_ctr=gather(["K_eff_max_ctr", "K_eff_max"]),
        var_cv=gather(["var_cv", "value"]),
        zmax_mean=gather(["K_eff_max", "zmax_mean"]))


def cal_iid_arm(D, K, n_real, seed):
    """CAL-IID: the LAW's own null object -- iid standard normal columns at the
    same (D, K).  Unlike CAL-PERM it is NOT conditional on the observed
    marginals, so it is the only comparator that can supply a null for ST-7
    (var_cv is EXACTLY invariant under CAL-PERM's per-column permutation, which
    would make CAL-PERM a zero-spread comparator for it -- mode 1 again)."""
    rng = np.random.default_rng(seed)
    reals = [dep_stats(rng.standard_normal((D, K)), list(range(K)), store_R=False)
             for _ in range(n_real)]                # count-bounded

    def gather(path):
        vals = []
        for r in reals:
            v = r
            for p in path:
                v = v[p]
            vals.append(float(v))
        a = np.array(vals)
        return dict(mean=float(a.mean()),
                    sd=float(a.std(ddof=1)) if a.size > 1 else None, n=int(a.size))
    return dict(n_realisations=int(n_real),
                K_eff_trail=gather(["K_eff_trail", "value"]),
                K_eff_max=gather(["K_eff_max", "K_eff_max"]),
                K_eff_max_ctr=gather(["K_eff_max_ctr", "K_eff_max"]),
                var_cv=gather(["var_cv", "value"]),
                raw_offdiag=gather(["raw", "offdiag_mean"]))


def sens_graded(D, K, seed, ts=(0.0, 0.05, 0.15, 0.30, 0.50, 0.75)):
    """SENS-GRADED.  Known population off-diagonal correlation exactly t."""
    rng = np.random.default_rng(seed)
    rows, ok_i, prev = [], True, None
    keffs = []
    for t in ts:
        Z0 = rng.standard_normal((D, 1))
        Zk = rng.standard_normal((D, K))
        W = np.sqrt(1.0 - t) * Zk + np.sqrt(t) * Z0
        st = dep_stats(W, list(range(K)))
        err = abs(st["raw"]["offdiag_mean"] - t)
        ok_i = ok_i and (err <= 0.02)
        keffs.append(st["K_eff_max"]["K_eff_max"])
        rows.append(dict(t=float(t), offdiag_raw=st["raw"]["offdiag_mean"],
                         abs_error_vs_t=float(err),
                         lambda_max_raw=st["raw"]["lambda_max"],
                         K_eff_PR_raw=st["raw"]["K_eff_PR"],
                         K_eff_max=st["K_eff_max"]["K_eff_max"],
                         zmax_mean=st["K_eff_max"]["zmax_mean"]))
    ok_ii = all(keffs[i + 1] <= keffs[i] * 1.0 + 1e-9 for i in range(len(keffs) - 1))
    r0 = rows[0]
    ok_iii = (abs(r0["offdiag_raw"]) <= 3.0 / np.sqrt(D)
              and (K / 1.5) <= r0["K_eff_max"] <= (K * 1.5))
    return dict(
        comparator="CAL-PERM arm of the same group at the same D and K",
        thresholds_declared_before_run=PREREG["sens_graded_thresholds"],
        rows=rows,
        gate_i_offdiag_within_0p02=bool(ok_i),
        gate_ii_Keffmax_monotone_in_t=bool(ok_ii),
        gate_iii_t0_calibrated=bool(ok_iii),
        passed=bool(ok_i and ok_ii and ok_iii))


# --------------------------------------------------------------------------
# the EXACT closed form -- the forced value, computed WITH NO SCORING
# --------------------------------------------------------------------------
def closed_form_cov(X, cosPhi, sinPhi, sigma, q, block=600):
    """Cov(S_k,S_k') = (1/N^2)[a^T C a' + b^T S b'] with
       C = P.*(cosh T - 1), S = P.*sinh T, P_ii' = exp(-c(n_i+n_i')),
       T = 2 c X X^T, c = (1/2)(2 pi sigma/q)^2.
    EXACT for Gaussian e (the run uses a ROUNDED Gaussian -- stated, not hidden).
    One blocked N x N pass, no scoring of any kind."""
    Xf = np.asarray(X, dtype=np.float64)
    N = Xf.shape[0]
    c = 0.5 * (TWOPI * sigma / q) ** 2
    n = (Xf * Xf).sum(axis=1)
    w = np.exp(-c * n)                                   # E[cos u_i]
    A = np.ascontiguousarray(cosPhi)
    B = np.ascontiguousarray(sinPhi)
    K = A.shape[1]
    accA = np.zeros((K, K))
    accB = np.zeros((K, K))
    off = 0
    while off < N:                                       # count-bounded
        b = min(block, N - off)
        T = (2.0 * c) * Xf[off:off + b].dot(Xf.T)        # b x N
        E = np.exp(T)                                    # one exp per entry
        Ei = 1.0 / E
        P = w[off:off + b, None] * w[None, :]
        Sb = P * (0.5 * (E - Ei))                        # Cov(sin u)
        Cb = P * (0.5 * (E + Ei) - 1.0)                  # Cov(cos u)
        accA += A[off:off + b].T.dot(Cb.dot(A))
        accB += B[off:off + b].T.dot(Sb.dot(B))
        del T, E, Ei, P, Sb, Cb
        off += b
    cov = (accA + accB) / float(N) ** 2
    return cov, accA / float(N) ** 2, accB / float(N) ** 2


def known_answer_controls(say):
    """Instrument checks with answers known independently of this run.
    Run BEFORE any research number is produced."""
    ks = []

    def add(cid, what, expect, got, ok, note=""):
        ks.append(dict(id=cid, check=what, expected=expect, got=got,
                       passed=bool(ok), note=note))
        say("    %s %-52s expected %-22s got %-22s %s"
            % (cid, what, str(expect)[:22], str(got)[:22], "PASS" if ok else "FAIL"))

    # KAC-1  the EXACT closed form against brute-force Monte Carlo, on a small
    #        synthetic instance with EXACTLY Gaussian (unrounded) errors.
    rng = np.random.default_rng(4242)
    Ns, ms, Ks, sg, qq = 300, 6, 5, 2.0, 127.0
    Xt = rng.normal(0.0, 3.0, size=(Ns, ms))
    Ph = rng.normal(0.0, 0.5, size=(Ns, Ks))
    cP, sP = np.cos(Ph), np.sin(Ph)
    cov_cf, _, _ = closed_form_cov(Xt, cP, sP, sg, qq, block=100)
    Dm = 400000
    acc = np.zeros((Ks, Ks)); accm = np.zeros(Ks); done = 0
    while done < Dm:                                   # count-bounded
        b = min(20000, Dm - done)
        Ee = rng.normal(0.0, sg, size=(ms, b))         # UNROUNDED, as derived
        U = Xt.dot(Ee)
        Cu = np.cos(TWOPI * U / qq).T
        Su = np.sin(TWOPI * U / qq).T
        S = (Cu.dot(cP) - Su.dot(sP)) / Ns
        acc += S.T.dot(S); accm += S.sum(axis=0); done += b
    emp = acc / Dm - np.outer(accm / Dm, accm / Dm)
    rel = float(np.abs(emp - cov_cf).max() / np.abs(cov_cf).max())
    add("KAC-1", "exact closed-form Cov vs 4e5-draw Monte Carlo (rel max err)",
        "< 0.02", round(rel, 5), rel < 0.02,
        "verifies section 3's derivation against brute force, unrounded e")

    # KAC-2  the E[max] quadrature against Monte Carlo
    for kk in (8, 25, 512):
        a_q, a_mc = expected_max_iid(kk), expected_max_iid_mc(kk)
        add("KAC-2.%d" % kk, "E[max of %d iid N(0,1)]: quadrature vs MC" % kk,
            round(a_q, 4), round(a_mc, 4), abs(a_q - a_mc) < 0.02)

    # KAC-3  keff_from_max round-trips
    for kk in (8, 25, 512):
        rt = keff_from_max(expected_max_iid(kk))
        add("KAC-3.%d" % kk, "keff_from_max(E[max of %d]) round-trip" % kk,
            kk, round(rt, 2), abs(rt - kk) / kk < 0.05)

    # KAC-4  dep_stats returns the law's values on genuinely iid data
    Wi = np.random.default_rng(77).standard_normal((4000, 8))
    st = dep_stats(Wi, list(range(8)))
    add("KAC-4a", "offdiag(R_raw) on iid data", "|.| < 0.05",
        round(st["raw"]["offdiag_mean"], 4), abs(st["raw"]["offdiag_mean"]) < 0.05)
    add("KAC-4b", "offdiag(R_ctr) on iid data = -1/(K-1)", round(-1 / 7, 5),
        round(st["ctr"]["offdiag_mean"], 5),
        abs(st["ctr"]["offdiag_mean"] + 1 / 7) < 0.05)
    add("KAC-4c", "K_eff_PR(R_ctr) on iid data = K-1", 7,
        round(st["ctr"]["K_eff_PR"], 3), abs(st["ctr"]["K_eff_PR"] - 7) < 0.3)
    return dict(checks=ks, passed=all(c["passed"] for c in ks))


def cov_to_corr(cov):
    d = np.sqrt(np.diag(cov))
    return cov / np.outer(d, d)


def corr_summary(R, tag):
    K = R.shape[0]
    ev = np.sort(np.linalg.eigvalsh(R))[::-1]
    return dict(tag=tag, K=int(K),
                offdiag_mean=float((R.sum() - np.trace(R)) / (K * (K - 1))),
                lambda_max=float(ev[0]),
                K_eff_PR=float(K ** 2 / (R ** 2).sum()),
                R=[[float(v) for v in row] for row in R])


def centre_cov(cov):
    """Covariance of the group-mean-removed scores."""
    K = cov.shape[0]
    Pm = np.eye(K) - np.ones((K, K)) / K
    return Pm.dot(cov).dot(Pm)


# --------------------------------------------------------------------------
# candidate construction
# --------------------------------------------------------------------------
def make_candidates_A(rng, s, q, n, eta, n_near, n_unif, n_sdist):
    """The batch-1..4 candidate family, extended in COUNT only.  near-miss
    c = s + unit_j (surrogate.py make_candidates, verbatim in form)."""
    cands = [("correct", "correct", s.copy())]
    for i in range(n_near):
        c = s.copy(); c[i % n] = c[i % n] + 1
        cands.append(("nearmiss_%02d" % i, "near_miss", c))
    for i in range(n_unif):
        cands.append(("uniform_%03d" % i, "uniform",
                      rng.integers(0, q, size=n, dtype=np.int64)))
    for i in range(n_sdist):
        cands.append(("secretdist_%03d" % i, "secret_distribution",
                      centered_binomial(rng, eta, n)))
    cands.append(("zero_vector", "reference_zero", np.zeros(n, dtype=np.int64)))
    return cands


def group_index(groups):
    gidx = {}
    for i, g in enumerate(groups):
        gidx.setdefault(g, []).append(i)
    return gidx


# --------------------------------------------------------------------------
def env_block(venv_python):
    def pv(mod):
        try:
            r = subprocess.run([venv_python, "-c",
                                "import %s,sys;print(getattr(%s,'__version__','?'))"
                                % (mod, mod)], capture_output=True, text=True,
                               timeout=120)
            return r.stdout.strip() or r.stderr.strip()[:120]
        except Exception as e:
            return repr(e)
    try:
        blas = str(np.__config__.show(mode="dicts")["Build Dependencies"]["blas"])
    except Exception as e:
        blas = "unavailable: " + repr(e)[:80]
    return dict(python=sys.version, platform=platform.platform(),
                numpy=np.__version__, executable=sys.executable,
                fpylll=pv("fpylll"), g6k_import_ok=pv("g6k"), blas=blas)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ==========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["build", "measure"], required=True)
    ap.add_argument("--work", default="/tmp/f58d34_work.npz")
    ap.add_argument("--outdir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--draws-t0", type=int, default=2000)
    ap.add_argument("--draws-t1", type=int, default=4000)
    ap.add_argument("--draws-big", type=int, default=2000)
    ap.add_argument("--n-rowperm", type=int, default=6)
    ap.add_argument("--n-cal", type=int, default=8)
    ap.add_argument("--n-unif-big", type=int, default=512)
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
    args = ap.parse_args()

    t_start = time.time()
    if args.mem_cap_gb > 0:
        cap = int(args.mem_cap_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    log = []

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        log.append(line)

    say(SCRIPT_VERSION + "  stage=" + args.stage)
    say("SCOPE: m=%d n=%d q=%d sigma=%.1f eta=%d, ONE instance, TOY SCALE. "
        "No ML-KEM break claim, no security proof, no FIPS 203 parameter set "
        "affected or cleared, no speedup, no exponent moved." % (M_, N_, Q, SIGMA, ETA))
    say("rule12_status: UNMET and UNWAIVED, inherited.  No EV-MLKEM-* status change.")

    seeds = dict(instance=INSTANCE_SEED, error_draws=20260805401,
                 rowperm=20260805402, randdir=20260805403, iidphase=20260805404,
                 cal=20260805405, sens=20260805406, candidates=20260805407,
                 sums=20260805408, stageb=20260805409)

    rgi = np.random.default_rng(INSTANCE_SEED)
    A = rgi.integers(0, Q, size=(M_, N_), dtype=np.int64)
    s = centered_binomial(rgi, ETA, N_)

    # ------------------------------------------------------------- BUILD
    if args.stage == "build":
        say("regenerating BATCH-f75059 replicate 0 (seed %d)" % INSTANCE_SEED)
        Xs, Ys, tim = run_sieve(build_dual_basis(A, Q, M_, N_), "bgj1_sieve",
                                INSTANCE_SEED + 1, INSTANCE_SEED + 2, M_)
        N = Xs.shape[0]
        xs2 = (Xs * Xs).sum(axis=1).astype(np.float64)
        ys2 = (Ys * Ys).sum(axis=1).astype(np.float64)
        a_x = float(2 * np.pi ** 2 * SIGMA ** 2 * xs2.mean() / Q ** 2)
        cert_s = certify(Xs, Ys, A, Q, "SIEVE")
        say("SIEVE N=%d cert=%s mean||x||^2=%.5f mean||y||^2=%.5f a_x=%.15f "
            "(%.1fs sieve)" % (N, cert_s["verified"], xs2.mean(), ys2.mean(),
                               a_x, tim["sieve_seconds"]))
        say("  provenance vs archive: N match=%s  a_x delta=%.3e  "
            "mean||x||^2 delta=%.3e" % (N == ARCHIVE["rep0_n_vectors"],
                                        abs(a_x - ARCHIVE["rep0_a_x"]),
                                        abs(xs2.mean() - ARCHIVE["rep0_mean_xnorm2"])))

        # a SECOND certified valid dual family of the same lattice, sieve
        # provenance, count-bounded, no clock:  v_i +- v_j over random pairs.
        rngs = np.random.default_rng(seeds["sums"])
        ii = rngs.integers(0, N, size=3 * N)
        jj = rngs.integers(0, N, size=3 * N)
        sg = rngs.choice(np.array([-1, 1]), size=3 * N)
        keep = ii != jj
        Vsum = (np.concatenate([Xs, Ys], axis=1)[ii[keep]]
                + sg[keep, None] * np.concatenate([Xs, Ys], axis=1)[jj[keep]])
        seen, idx = set(), []
        for t, k in enumerate(canonical_keys(Vsum)):
            if k in seen:
                continue
            seen.add(k)
            idx.append(t)
            if len(idx) >= N:
                break
        Vsum = Vsum[np.array(idx, dtype=np.int64)]
        Xu, Yu = Vsum[:, :M_], Vsum[:, M_:]
        cert_u = certify(Xu, Yu, A, Q, "SIEVE_SUMS")
        say("SIEVE_SUMS N=%d cert=%s mean||x||^2=%.4f mean||y||^2=%.4f"
            % (Xu.shape[0], cert_u["verified"], (Xu * Xu).sum(axis=1).mean(),
               (Yu * Yu).sum(axis=1).mean()))

        # ---- Stage B instance, BATCH-c45baf's admissible tuple
        A_lat, A_fft = A[:, :K_LAT], A[:, K_LAT:]
        Bl = np.zeros((M_ + K_LAT, M_ + K_LAT), dtype=np.int64)
        Bl[:M_, :M_] = np.eye(M_, dtype=np.int64)
        Bl[:M_, M_:] = A_lat
        Bl[M_:, M_:] = Q * np.eye(K_LAT, dtype=np.int64)
        Xb, Yb, timb = run_sieve(Bl, "bgj1_sieve", INSTANCE_SEED + 11,
                                 INSTANCE_SEED + 12, M_)
        cert_b = certify(Xb, Yb, A_lat, Q, "STAGEB_LAT")
        say("STAGEB (m=%d k_lat=%d k_fft=%d k_enum=%d, sieve dim %d) N=%d "
            "cert=%s mean||x||^2=%.4f (%.1fs sieve)"
            % (M_, K_LAT, K_FFT, K_ENUM, M_ + K_LAT, Xb.shape[0],
               cert_b["verified"], (Xb * Xb).sum(axis=1).mean(),
               timb["sieve_seconds"]))
        say("  archive Stage B N was %d; this run %d"
            % (ARCHIVE["stage_b_n_vectors"], Xb.shape[0]))

        np.savez_compressed(args.work, A=A, s=s, Xs=Xs, Ys=Ys, Xu=Xu, Yu=Yu,
                            Xb=Xb, Yb=Yb, a_x=a_x,
                            cert_s=json.dumps(cert_s), cert_u=json.dumps(cert_u),
                            cert_b=json.dumps(cert_b),
                            tim=json.dumps(tim), timb=json.dumps(timb),
                            log=json.dumps(log))

        # ARCHIVE RAW VECTORS so the certificate is checkable from the snapshot
        # alone (EV-MLKEM-ba6c25 OBS-3 / VAL-20260804-a84239 DEF-2).
        vpath = os.path.join(args.outdir, "vectors.json")
        with open(vpath, "w") as f:
            json.dump(dict(
                task="TASK-20260804-f58d34", batch="BATCH-a2bb63",
                goal="GOAL-MLKEM-004", script_version=SCRIPT_VERSION,
                scope="m=35 n=25 q=127 sigma=2 eta=2, ONE instance, TOY SCALE. "
                      "No ML-KEM break claim, no security proof, no FIPS 203 "
                      "parameter set affected or cleared.",
                purpose="RAW VECTORS, archived so every certificate in "
                        "results.json is checkable from the snapshot alone "
                        "without regenerating anything (EV-MLKEM-ba6c25 OBS-3).",
                how_to_check="for each family F: numpy.mod(numpy.array(F['X'])."
                             "dot(numpy.array(A)) - numpy.array(F['Y']), 127) "
                             "must be all zero.  For STAGEB use A_lat = A[:, :15].",
                instance_seed=INSTANCE_SEED, q=Q, m=M_, n=N_, k_lat=K_LAT,
                A=A.tolist(), secret_s=s.tolist(),
                families={
                    "SIEVE": dict(provenance="g6k bgj1_sieve, dual basis dim 60",
                                  N=int(Xs.shape[0]),
                                  X=Xs.tolist(), Y=Ys.tolist(),
                                  certificate=cert_s),
                    "SIEVE_SUMS": dict(provenance="v_i +- v_j over random pairs "
                                                  "of SIEVE vectors, dedup, "
                                                  "count-bounded",
                                       N=int(Xu.shape[0]),
                                       X=Xu.tolist(), Y=Yu.tolist(),
                                       certificate=cert_u),
                    "STAGEB_LAT": dict(provenance="g6k bgj1_sieve, dual basis of "
                                                  "A_lat, dim m+k_lat=50",
                                       N=int(Xb.shape[0]),
                                       X=Xb.tolist(), Y=Yb.tolist(),
                                       certificate=cert_b)}), f)
        say("wrote %s (%.1f MB) and %s" % (vpath,
                                           os.path.getsize(vpath) / 1e6, args.work))
        say("BUILD COMPLETE.  peak RSS %.0f MB"
            % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0))
        return

    # ----------------------------------------------------------- MEASURE
    Z = np.load(args.work, allow_pickle=False)
    Xs, Ys, Xu, Yu, Xb, Yb = (Z["Xs"], Z["Ys"], Z["Xu"], Z["Yu"], Z["Xb"], Z["Yb"])
    N = Xs.shape[0]
    a_x = float(Z["a_x"])
    say("loaded work: SIEVE N=%d, SIEVE_SUMS N=%d, STAGEB N=%d"
        % (N, Xu.shape[0], Xb.shape[0]))
    res = dict(task="TASK-20260804-f58d34", batch="BATCH-a2bb63",
               goal="GOAL-MLKEM-004", script_version=SCRIPT_VERSION,
               states_a_conclusion=False,
               scope="m=35 n=25 d=60 q=127 sigma=2 eta=2; Stage B sieve dim 50. "
                     "ONE instance. TOY SCALE. No ML-KEM break claim, no security "
                     "proof, no FIPS 203 parameter set affected or cleared, no "
                     "speedup, no cost claim, no exponent moved.",
               rule12_status="UNMET and UNWAIVED, inherited. No EV-MLKEM-* status "
                             "change is made or proposed.",
               certificate_kind_for_solve_claims="none -- pure measurement run "
                     "(docs/claims-and-verification.md). Lattice-membership "
                     "certificates below certify the VECTORS only.",
               prereg=PREREG, archive_anchors=ARCHIVE, seeds=seeds)

    # KNOWN-ANSWER CONTROLS, before any research number is produced
    say("known-answer controls (answers known independently of this run):")
    kac = known_answer_controls(say)
    res["known_answer_controls"] = kac
    if not kac["passed"]:
        say("KNOWN-ANSWER CONTROL FAILED -- instrument unfit, run is "
            "implementation_error, no measurement reported")
        res["status"] = "implementation_error"
        res["reason"] = "known-answer control failed"
        json.dump(res, open(os.path.join(args.outdir, "results.json"), "w"), indent=1)
        return

    # re-certify from the archived integers before measuring anything
    certs = {}
    for lbl, Xa, Ya, Am in (("SIEVE", Xs, Ys, A), ("SIEVE_SUMS", Xu, Yu, A),
                            ("STAGEB_LAT", Xb, Yb, A[:, :K_LAT])):
        c = certify(Xa, Ya, Am, Q, lbl)
        certs[lbl] = c
        say("re-certified %s: verified=%s violating=%d/%d bigint_violating=%d/%d "
            "dup=%d dup_x=%d" % (lbl, c["verified"], c["violating_entries"],
                                 c["checked_entries"], c["bigint_violating_entries"],
                                 c["bigint_rows_checked"] * Am.shape[1],
                                 c["duplicate_vectors"], c["duplicate_x_rows"]))
        if not c["verified"]:
            say("CERTIFICATE FAILED for %s -- run is invalid_measurement" % lbl)
            res["status"] = "invalid_measurement"
            res["reason"] = "certificate failed for " + lbl
            json.dump(res, open(os.path.join(args.outdir, "results.json"), "w"),
                      indent=1)
            return
    res["certificates"] = certs

    cfg = dict(m=M_, n=N_, q=Q, sigma=SIGMA, draws=args.draws_t0, block=250,
               n_rowperm=args.n_rowperm)

    # =================================================================== T0
    say("")
    say("=== T0  deterministic-Y RANDDIR excess.  Reference to confirm or "
        "refute: RT-20260804-37a8f2 = %.4f ===" % ARCHIVE["rt_coupled_randdir_excess"])
    rgc = np.random.default_rng(INSTANCE_SEED + 3)
    c0 = make_candidates_A(rgc, s, Q, N_, ETA, 8, 8, 4)
    C0 = np.array([c[2] for c in c0], dtype=np.int64)
    g0 = group_index([c[1] for c in c0])
    xs2 = (Xs * Xs).sum(axis=1).astype(np.float64)
    ys2 = (Ys * Ys).sum(axis=1).astype(np.float64)

    t0arms = {}
    t = time.time()
    t0arms["SIEVE"] = rowperm_excess(Xs, Ys, s, C0, g0["near_miss"], cfg, seeds,
                                     "SIEVE")
    say("  SIEVE                     excess %.4f (%.0fs)  [archive 1.2704]"
        % (t0arms["SIEVE"]["excess_real_over_rowperm"], time.time() - t))

    rngd = np.random.default_rng(seeds["randdir"])
    Gx = rngd.normal(size=(N, M_)); Gx /= np.linalg.norm(Gx, axis=1, keepdims=True)
    Gy = rngd.normal(size=(N, N_)); Gy /= np.linalg.norm(Gy, axis=1, keepdims=True)
    Xr = Gx * np.sqrt(xs2)[:, None]
    Yr_indep = Gy * np.sqrt(ys2)[:, None]
    t = time.time()
    t0arms["RANDDIR_INDEP"] = rowperm_excess(Xr, Yr_indep, s, C0, g0["near_miss"],
                                             cfg, seeds, "RANDDIR", integer_Y=False)
    say("  RANDDIR_INDEP  (Gy indep) excess %.4f (%.0fs)  [archive 1.0868, RT 0.9767]"
        % (t0arms["RANDDIR_INDEP"]["excess_real_over_rowperm"], time.time() - t))

    # THE ONE-LINE MUTATION: y a DETERMINISTIC function of x, norms exact.
    rngR = np.random.default_rng(seeds["randdir"] + 1)
    Rmat = rngR.normal(size=(M_, N_))
    Yc = Xr.dot(Rmat)
    Yc = Yc / np.linalg.norm(Yc, axis=1, keepdims=True) * np.sqrt(ys2)[:, None]
    t = time.time()
    t0arms["RANDDIR_COUPLED"] = rowperm_excess(Xr, Yc, s, C0, g0["near_miss"],
                                               cfg, seeds, "RANDDIRC",
                                               integer_Y=False)
    ec = t0arms["RANDDIR_COUPLED"]["excess_real_over_rowperm"]
    es = t0arms["SIEVE"]["excess_real_over_rowperm"]
    say("  RANDDIR_COUPLED (y=f(x))  excess %.4f (%.0fs)  [RT-20260804-37a8f2 "
        "reports 12.1507]" % (ec, time.time() - t))
    say("  norm match, row for row: mean||x||^2 %.4f vs sieve %.4f ; "
        "mean||y||^2 %.4f vs sieve %.4f"
        % ((Xr * Xr).sum(axis=1).mean(), xs2.mean(),
           (Yc * Yc).sum(axis=1).mean(), ys2.mean()))
    ref = ARCHIVE["rt_coupled_randdir_excess"]
    if not np.isfinite(ec) or not np.isfinite(es) or es <= 0:
        t0v = "T0-NEITHER"
    elif abs(ec - ref) <= PREREG["T0_confirm_band_rel"] * ref:
        t0v = "T0-CONFIRMS"
    elif ec > PREREG["T0_same_direction_multiple_of_sieve"] * es:
        t0v = "T0-SAME-DIRECTION"
    else:
        t0v = "T0-REFUTES"
    say("  T0 VERDICT (mechanical, frozen rule): %s   band [%.4f, %.4f]  "
        "3x sieve = %.4f" % (t0v, ref * 0.85, ref * 1.15, 3.0 * es))
    res["T0"] = dict(
        question="does the RANDDIR arm separate when Y is a DETERMINISTIC "
                 "function of X instead of an independent draw",
        reference_value=ref, reference_source="RT-20260804-37a8f2 section 5",
        one_line_mutation="y_i := normalise(R^T x_i) * ||y_i||_sieve, R a fixed "
                          "random m x n Gaussian matrix; x_i random direction "
                          "carrying the sieve's own ||x_i||",
        arms=t0arms, verdict=t0v,
        norms=dict(mean_xnorm2_randdir=float((Xr * Xr).sum(axis=1).mean()),
                   mean_xnorm2_sieve=float(xs2.mean()),
                   mean_ynorm2_coupled=float((Yc * Yc).sum(axis=1).mean()),
                   mean_ynorm2_sieve=float(ys2.mean())),
        caveat="y is real-valued here and the map is linear, so there is NO "
               "mod-q wrapping.  RT-20260804-37a8f2 states the same caveat.  "
               "This arm is NOT in any lattice and carries no certificate.",
        status="completed_valid")

    # =================================================================== T1
    say("")
    say("=== T1  ACROSS-CANDIDATE DEPENDENCE.  Law predictions were frozen in "
        "the PRE-REGISTRATION block before this run. ===")
    say("  law: offdiag(R_raw)=0+-1/sqrt(D); offdiag(R_ctr)=-1/(K-1) EXACTLY; "
        "K_eff_PR(R_ctr)=K-1; K_eff_max=K")
    say("  forced F-1 (near-miss R_raw, hand-computed before the run): 0.98258, "
        "band [0.95, 0.995] -- declared UNINFORMATIVE in advance")
    say("  forced F-2 (uniform R_raw): ~0, also forced, also uninformative")

    # ---- SENS-GRADED gate, BEFORE the real arms are scored
    sg8 = sens_graded(args.draws_t1, 8, seeds["sens"])
    sg25 = sens_graded(args.draws_t1, 25, seeds["sens"] + 1)
    say("  SENS-GRADED K=8  : %s" % json.dumps(
        [dict(t=r["t"], offdiag=round(r["offdiag_raw"], 4),
              err=round(r["abs_error_vs_t"], 4),
              Keffmax=round(r["K_eff_max"], 2)) for r in sg8["rows"]]))
    say("  SENS-GRADED K=25 : %s" % json.dumps(
        [dict(t=r["t"], offdiag=round(r["offdiag_raw"], 4),
              err=round(r["abs_error_vs_t"], 4),
              Keffmax=round(r["K_eff_max"], 2)) for r in sg25["rows"]]))
    say("  SENS-GRADED gates: K=8 (i)%s (ii)%s (iii)%s -> %s ; "
        "K=25 (i)%s (ii)%s (iii)%s -> %s"
        % (sg8["gate_i_offdiag_within_0p02"], sg8["gate_ii_Keffmax_monotone_in_t"],
           sg8["gate_iii_t0_calibrated"], sg8["passed"],
           sg25["gate_i_offdiag_within_0p02"], sg25["gate_ii_Keffmax_monotone_in_t"],
           sg25["gate_iii_t0_calibrated"], sg25["passed"]))
    instrument_fit = bool(sg8["passed"] and sg25["passed"])

    # ---- candidate set
    rgc1 = np.random.default_rng(seeds["candidates"])
    c1 = make_candidates_A(rgc1, s, Q, N_, ETA, 25, args.n_unif_big, 64)
    C1 = np.array([c[2] for c in c1], dtype=np.int64)
    g1 = group_index([c[1] for c in c1])
    say("  candidate set: %s" % {k: len(v) for k, v in g1.items()})

    groups_small = dict(near_miss=g1["near_miss"][:8],
                        near_miss_25=g1["near_miss"],
                        uniform_8=g1["uniform"][:8],
                        uniform_25=g1["uniform"][:25],
                        secret_distribution_25=g1["secret_distribution"][:25])
    groups_big = dict(uniform_512=g1["uniform"], secret_distribution_64=g1["secret_distribution"])

    def measure_family(lbl, Xa, Ya, integer_Y=True, D=None):
        D = D or args.draws_t1
        t = time.time()
        cP, sP = phases(Ya, s, C1, Q, integer_Y)
        Mm = score_means(Xa.astype(np.float64), cP, sP, D, 250,
                         seeds["error_draws"], M_, Q, SIGMA)
        say("  [%s] scored D=%d K=%d in %.0fs" % (lbl, D, C1.shape[0],
                                                  time.time() - t))
        out = dict(n_vectors=int(Xa.shape[0]), n_draws=int(D), groups={})
        for gname, idxs in list(groups_small.items()) + list(groups_big.items()):
            st = dep_stats(Mm, idxs)
            st["CAL_PERM"] = cal_perm_arm(Mm, idxs, args.n_cal,
                                          seeds["cal"] + len(gname))
            st["CAL_IID"] = cal_iid_arm(D, len(idxs), args.n_cal,
                                        seeds["cal"] + 7919 + len(gname))
            st["sd_ratio_to_iid"] = float(sd_ratio(Mm, idxs, Xa.shape[0]).mean())
            out["groups"][gname] = st
        return out, Mm

    # ---- the frozen decision rule
    def verdict_for(st, instrument_ok):
        """The frozen five-branch rule of PRE-REGISTRATION section 5.  Emitted
        mechanically.  Returns (branch, reason, z-scores)."""
        zs = {}
        if not instrument_ok:
            return "D0", "D0(iv): SENS-GRADED gate failed", zs
        for key in ("raw", "ctr"):
            if st[key].get("degenerate"):
                return "D0", "D0(iii): degenerate %s correlation matrix" % key, zs
        if st["K_eff_trail"].get("degenerate") or st["K_eff_max_ctr"].get("degenerate"):
            return "D0", "D0(iii): degenerate spectrum or max statistic", zs
        K = st["K"]
        cal, cid = st["CAL_PERM"], st["CAL_IID"]
        # The COMPARATOR supplies BOTH the reference and the spread.  The law's
        # asymptotic values (K-1, K) are the population targets and are reported
        # beside these, but at finite D -- and, for the centred max, under the
        # sum-to-zero constraint that inflates it by ~sqrt(K/(K-1)) -- the
        # comparator's own mean is the only honest reference.
        spec = [("z1", st["K_eff_trail"]["value"], cal, "K_eff_trail", "CAL-PERM"),
                ("z2", st["K_eff_max_ctr"]["K_eff_max"], cal, "K_eff_max_ctr",
                 "CAL-PERM"),
                ("z3", st["var_cv"]["value"], cid, "var_cv", "CAL-IID")]
        for zn, val, comp, cname, which in spec:
            sd = comp[cname]["sd"]
            ref = comp[cname]["mean"]
            if (sd is None or not np.isfinite(sd) or sd <= 0
                    or not np.isfinite(val) or not np.isfinite(ref)):
                return ("D0", "D0(v): %s gave no usable reference or spread for "
                        "%s (or the statistic is non-finite)" % (which, cname), zs)
            zs[zn] = float((val - ref) / sd)
        z1, z2, z3 = zs["z1"], zs["z2"], zs["z3"]
        a = (z1 < -3.0) or (z2 < -3.0)
        b = (z1 > 3.0) or (z2 > 3.0)
        if a and b:
            return ("D0", "D0(i): the two effective-count channels DISAGREE in "
                    "direction (z1=%+.1f, z2=%+.1f); no directional label is "
                    "honest" % (z1, z2), zs)
        if a:
            return ("D2", "FEWER effective independent candidates than the "
                    "comparator: z1=%+.1f (K_eff_trail %.3f vs CAL-PERM %.3f, "
                    "law %d), z2=%+.1f (K_eff_max_ctr %.2f vs CAL-PERM %.2f, "
                    "law %d)"
                    % (z1, st["K_eff_trail"]["value"], cal["K_eff_trail"]["mean"],
                       K - 1, z2, st["K_eff_max_ctr"]["K_eff_max"],
                       cal["K_eff_max_ctr"]["mean"], K), zs)
        if b:
            return ("D3", "MORE effective independent candidates than the law: "
                    "z1=%+.1f, z2=%+.1f" % (z1, z2), zs)
        if abs(z3) > 3.0:
            return ("D4", "both effective-count channels at the law's values but "
                    "marginal-variance heterogeneity departs: z3=%+.1f" % z3, zs)
        return ("D1", "all three channels within 3 CAL sd of the law's values "
                "(z1=%+.1f, z2=%+.1f, z3=%+.1f)" % (z1, z2, z3), zs)

    def show(famname, gname):
        st = fam[famname]["groups"][gname]
        cal, cid = st["CAL_PERM"], st["CAL_IID"]
        v, why, zs = verdict_for(st, instrument_fit)
        say("    %-14s %-22s K=%3d | FORCED R_raw off %+.4f, R_ctr off %+.4f "
            "(forced %+.4f) | ST-6 %9.3f vs CAL-PERM %9.3f+-%.3f (law %4d) "
            "z1=%+8.1f ratio %.4f | ST-5c %9.2f vs %9.2f+-%.2f z2=%+7.1f "
            "ratio %.4f | ST-7 %.4f vs CAL-IID %.4f z3=%+6.1f | %s"
            % (famname, gname, st["K"], st["raw"]["offdiag_mean"],
               st["ctr"]["offdiag_mean"], -1.0 / (st["K"] - 1),
               st["K_eff_trail"]["value"], cal["K_eff_trail"]["mean"],
               cal["K_eff_trail"]["sd"] or 0.0, st["K"] - 1,
               zs.get("z1", float("nan")),
               st["K_eff_trail"]["value"] / max(cal["K_eff_trail"]["mean"], 1e-30),
               st["K_eff_max_ctr"]["K_eff_max"], cal["K_eff_max_ctr"]["mean"],
               cal["K_eff_max_ctr"]["sd"] or 0.0, zs.get("z2", float("nan")),
               st["K_eff_max_ctr"]["K_eff_max"]
               / max(cal["K_eff_max_ctr"]["mean"], 1e-30),
               st["var_cv"]["value"], cid["var_cv"]["mean"],
               zs.get("z3", float("nan")), v))

    SHOW_GROUPS = ("near_miss", "near_miss_25", "uniform_8", "uniform_25",
                   "uniform_512", "secret_distribution_25")
    fam = {}
    fam["SIEVE"], M_sieve = measure_family("SIEVE", Xs, Ys)
    for gname in SHOW_GROUPS:
        show("SIEVE", gname)

    # NULL-IIDPHASE on the same X
    rngi = np.random.default_rng(seeds["iidphase"])
    Yi = rngi.integers(0, Q, size=(N, N_), dtype=np.int64)
    fam["NULL_IIDPHASE"], _ = measure_family("NULL_IIDPHASE", Xs, Yi)
    for gname in SHOW_GROUPS:
        show("NULL_IIDPHASE", gname)
    # second certified valid dual family, sieve provenance
    fam["SIEVE_SUMS"], _ = measure_family("SIEVE_SUMS", Xu, Yu)
    for gname in SHOW_GROUPS:
        show("SIEVE_SUMS", gname)

    # ---- the EXACT closed form, computed with NO SCORING, on the same objects
    say("  closed form (EXACT for Gaussian e, ONE blocked N x N pass, "
        "NO SCORING) on SIEVE:")
    idx_cf = groups_small["near_miss_25"] + groups_small["uniform_25"]
    cP, sP = phases(Ys, s, C1[idx_cf], Q, True)
    t = time.time()
    cov_cf, covA, covB = closed_form_cov(Xs, cP, sP, SIGMA, Q)
    say("    kernel pass %.0fs" % (time.time() - t))
    nm = list(range(25)); un = list(range(25, 50))
    cf = {}
    for gname, sub in (("near_miss_25", nm), ("uniform_25", un),
                       ("near_miss", nm[:8]), ("uniform_8", un[:8])):
        sl = np.ix_(sub, sub)
        cf[gname] = dict(
            predicted_raw=corr_summary(cov_to_corr(cov_cf[sl]), gname + "_raw"),
            predicted_ctr=corr_summary(cov_to_corr(centre_cov(cov_cf[sl])),
                                       gname + "_ctr"),
            common_mode_var_share=float(np.trace(covA[sl]) /
                                        (np.trace(covA[sl]) + np.trace(covB[sl]))))
        mstat = fam["SIEVE"]["groups"][gname]
        say("    %-14s predicted R_raw offdiag %+.4f (measured %+.4f) | "
            "predicted R_ctr offdiag %+.4f (measured %+.4f) | "
            "cos-term variance share %.4f"
            % (gname, cf[gname]["predicted_raw"]["offdiag_mean"],
               mstat["raw"]["offdiag_mean"],
               cf[gname]["predicted_ctr"]["offdiag_mean"],
               mstat["ctr"]["offdiag_mean"],
               cf[gname]["common_mode_var_share"]))

    verdicts = {}
    for famname in ("SIEVE", "NULL_IIDPHASE", "SIEVE_SUMS"):
        verdicts[famname] = {}
        for gname, st in fam[famname]["groups"].items():
            v, why, zs = verdict_for(st, instrument_fit)
            verdicts[famname][gname] = dict(branch=v, reason=why, z=zs)
    say("  T1 VERDICTS (mechanical, from the frozen five-branch rule):")
    for famname in ("SIEVE", "NULL_IIDPHASE", "SIEVE_SUMS"):
        for gname in ("near_miss", "near_miss_25", "uniform_8", "uniform_512"):
            vv = verdicts[famname][gname]
            say("    %-14s %-16s %s  (%s)" % (famname, gname, vv["branch"],
                                              vv["reason"]))

    res["T1"] = dict(
        what_is_measured="joint behaviour of per-candidate scores ACROSS "
                         "DIFFERENT CANDIDATES over ONE shared database; the "
                         "quantity assumption (I-b) of MATZOV.Nf is about",
        ensemble="D independent rounded-Gaussian error draws over one FIXED "
                 "database.  The complementary ensemble -- independent "
                 "databases at fixed error -- is NOT measured here and is "
                 "named as a limitation.",
        instrument_fit_for_purpose=instrument_fit,
        SENS_GRADED=dict(K8=sg8, K25=sg25),
        closed_form_prediction_no_scoring=cf,
        families=fam, verdicts=verdicts, status="completed_valid")

    # =================================================================== T2
    say("")
    say("=== T2  the ADJACENT-FFT-BIN family under BATCH-c45baf's admissible "
        "Stage B tuple (m=%d, k_enum=%d, k_fft=%d, p in %s, beta_sieve=%d, "
        "k_lat=%d) ===" % (M_, K_ENUM, K_FFT, P_VALUES, BETA_SIEVE, K_LAT))
    A_fft = A[:, K_LAT:]
    s_fft = s[K_LAT:]
    s_lat = s[:K_LAT]
    Nb = Xb.shape[0]
    psi = TWOPI * np.mod(Yb.dot(s_lat), Q).astype(np.float64) / Q
    alpha = np.mod(Xb.dot(A_fft), Q)
    sigma_s = float(np.sqrt(ETA / 2.0))     # centred binomial eta=2 -> var 1
    t2 = dict(design=dict(m=M_, n=N_, k_lat=K_LAT, k_fft=K_FFT, k_enum=K_ENUM,
                          p_values=list(P_VALUES), beta_sieve=BETA_SIEVE,
                          sieve_dimension=M_ + K_LAT, n_vectors=int(Nb),
                          source="BATCH-c45baf stage_b.py B3_config; the tuple "
                                 "DEC-20260803-81b778 / BATCH-c45baf recorded "
                                 "as admissible"),
              sigma_s=sigma_s, per_p={})
    for p in P_VALUES:
        adj_term = float(np.exp(K_FFT / 3.0 * (sigma_s * np.pi / p) ** 2))
        ahat = np.mod(np.rint(p * alpha.astype(np.float64) / Q).astype(np.int64), p)
        c_star = np.mod(s_fft, p)
        cands = [("correct_bin", "correct", c_star.copy())]
        seen = {tuple(c_star.tolist())}
        for j in range(K_FFT):
            for dlt in (1, -1):
                c = c_star.copy(); c[j] = (c[j] + dlt) % p
                tk = tuple(c.tolist())
                if tk in seen:
                    continue
                seen.add(tk)
                cands.append(("adjbin_%02d_%+d" % (j, dlt), "near_miss", c))
        rngc = np.random.default_rng(seeds["stageb"] + p)
        for i in range(256):
            cands.append(("uniform_%03d" % i, "uniform",
                          rngc.integers(0, p, size=K_FFT, dtype=np.int64)))
        Cb = np.array([c[2] for c in cands], dtype=np.int64)
        gb = group_index([c[1] for c in cands])
        base = TWOPI * alpha.dot(s_fft).astype(np.float64) / Q
        theta = base[:, None] - TWOPI * ahat.dot(Cb.T).astype(np.float64) / p
        cosT, sinT = np.cos(theta), np.sin(theta)
        cP = np.cos(psi)[:, None] * cosT - np.sin(psi)[:, None] * sinT
        sP = np.sin(psi)[:, None] * cosT + np.cos(psi)[:, None] * sinT
        t = time.time()
        Mb = score_means(Xb.astype(np.float64), cP, sP, args.draws_t1, 250,
                         seeds["error_draws"] + p, M_, Q, SIGMA)
        gsub = dict(adjacent_bins=gb["near_miss"],
                    adjacent_bins_10=gb["near_miss"][:10],
                    uniform_bins_256=gb["uniform"],
                    uniform_bins_10=gb["uniform"][:10])
        gres = {}
        for gname, idxs in gsub.items():
            st = dep_stats(Mb, idxs)
            st["CAL_PERM"] = cal_perm_arm(Mb, idxs, args.n_cal,
                                          seeds["cal"] + p + len(gname))
            st["CAL_IID"] = cal_iid_arm(args.draws_t1, len(idxs), args.n_cal,
                                        seeds["cal"] + 7919 + p + len(gname))
            st["sd_ratio_to_iid"] = float(sd_ratio(Mb, idxs, Nb).mean())
            v, why, zs = verdict_for(st, instrument_fit)
            st["verdict"] = dict(branch=v, reason=why, z=zs)
            gres[gname] = st
        say("  p=%d  K_adj=%d  correction term exp(k_fft/3 (sigma_s pi/p)^2) = "
            "%.4g  (MODELED, and NOT 1)  scored %.0fs"
            % (p, len(gb["near_miss"]), adj_term, time.time() - t))
        for gname in ("adjacent_bins", "uniform_bins_10", "uniform_bins_256"):
            st = gres[gname]
            cal = st["CAL_PERM"]
            say("    p=%d %-18s K=%3d | FORCED R_raw offdiag %+.4f | ST-6 "
                "K_eff_trail %8.3f (law %4d, CAL %8.3f +-%.3f) | ST-5c "
                "K_eff_max_ctr %8.2f (law %4d, CAL %8.2f +-%.2f) -> %s"
                % (p, gname, st["K"], st["raw"]["offdiag_mean"],
                   st["K_eff_trail"]["value"], st["K"] - 1,
                   cal["K_eff_trail"]["mean"], cal["K_eff_trail"]["sd"] or 0.0,
                   st["K_eff_max_ctr"]["K_eff_max"], st["K"],
                   cal["K_eff_max_ctr"]["mean"], cal["K_eff_max_ctr"]["sd"] or 0.0,
                   st["verdict"]["branch"]))
        t2["per_p"][str(p)] = dict(
            p=p, adjacent_fft_bin_correction_term_MODELED=adj_term,
            correction_term_is_identically_one=False,
            n_adjacent_bins=len(gb["near_miss"]), n_candidates=len(cands),
            n_draws=int(args.draws_t1), groups=gres)
    t2["status"] = "completed_valid"
    t2["note"] = ("The correction term is a COST-MODEL quantity (MODELED). It is "
                  "printed beside the MEASURED dependence statistics and is not "
                  "combined with them.")
    res["T2"] = t2

    res["environment"] = env_block(sys.executable)
    res["timings"] = dict(total_seconds=round(time.time() - t_start, 1),
                          peak_rss_mb=round(
                              resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                              / 1024.0, 1))
    res["log"] = log
    res["status"] = "completed_valid"
    outp = os.path.join(args.outdir, "results.json")
    json.dump(res, open(outp, "w"), indent=1)
    say("wrote %s" % outp)
    say("MEASURE COMPLETE.  %.0fs, peak RSS %.0f MB"
        % (time.time() - t_start, res["timings"]["peak_rss_mb"]))


if __name__ == "__main__":
    main()
