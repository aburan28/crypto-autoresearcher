#!/usr/bin/env python3
"""resolve.py  --  TASK-20260805-74a8e9,  BATCH-4bc9bc (batch 6 of 6),
GOAL-MLKEM-004.

SCOPE, binding on every number this script emits: m=35, n=25, d=60, q=127,
sigma=2, eta=2; ONE LWE instance (seed 20260803206); ONE shared sieve database;
Stage B sieve dimension 50.  TOY SCALE.  NO ML-KEM break claim, NO security
proof, NO FIPS 203 parameter set affected or cleared, NO speedup, NO cost
claim, NO exponent moved.  AGENTS.md rule 12 is UNMET and UNWAIVED, inherited:
this script changes the status of no EV-MLKEM-* record and proposes none.

WHAT THIS IS.  Two measurements, each a single count-bounded run.

  T1  RC-3 of RT-20260804-0ff29a: replicate the FAMILY-ABLATED NULL 16 times
      through the ARCHIVED closed form
      (coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/
       TASK-20260804-f58d34/dependence.py :: closed_form_cov, imported from
       that exact path, never copied) and report where the REAL certified dual
      family sits against that ensemble's interval.  No scoring, no g6k, no
      fpylll.

  T2  RC-4 of RT-20260804-0ff29a: put the CORRECT candidate into every group,
      on the adjacent-FFT-bin family at matched K -- the only candidate family
      a dual attack actually enumerates -- and measure the correlation of the
      wrong-candidate scores with the correct candidate's score and the
      separation of the correct candidate from the maximum over wrong ones,
      against an exactly-specified independence comparator.

NO WALL-CLOCK TRUNCATION ANYWHERE.  Every loop in this file is bounded by a
count.  time.time() appears only in elapsed-time prints and duration records,
never in a loop condition or a branch that decides what is measured.

CERTIFICATE DISCIPLINE (docs/claims-and-verification.md).  This is a PURE
MEASUREMENT RUN.  solve_claim_certificate = none: no discrete-log solve and no
factor-base relation is claimed.  The lattice-membership certificate of the
archived vectors IS re-verified here, from vectors.json and A alone, by code
written in this file that does not call the archived certify() and does not
use fpylll or g6k.
"""

import argparse, hashlib, importlib.util, json, os, platform, resource, sys, time
import numpy as np

SCRIPT_VERSION = "resolve.py v1 TASK-20260805-74a8e9"

REPO = "/home/user/crypto-autoresearcher"
ARCHIVE_DIR = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks",
    "TASK-20260804-f58d34")
ARCHIVED_SCRIPT = os.path.join(ARCHIVE_DIR, "dependence.py")
ARCHIVED_VECTORS = os.path.join(ARCHIVE_DIR, "vectors.json")
ARCHIVED_RESULTS = os.path.join(ARCHIVE_DIR, "results.json")

Q, M_, N_ = 127, 35, 25
SIGMA, ETA = 2.0, 2
INSTANCE_SEED = 20260803206
K_LAT, K_FFT = 15, 10
P_VALUES = (2, 3, 5)

# seeds inherited from the archive so the reconstruction is bit-identical
ARCH_SEEDS = dict(error_draws=20260805401, cal=20260805405,
                  candidates=20260805407, stageb=20260805409)
# seeds minted by THIS task; every source of randomness here is one of these
MY_SEEDS = dict(ablated_base=20260805740000,   # + draw index, 16 draws
                rank5_dirs=20260805740500,     # the 5-dim subspace
                rank5_rows=20260805740501,     # rows inside that subspace
                rank5_Y=20260805740502,        # Y for the positive control
                t2_calperm=20260805740600,     # + p + group offset
                t2_sens=20260805740700)        # SENS-T2 synthetic arm


# ==========================================================================
#  THE FROZEN PRE-REGISTRATION.
#  Written into this file before the run and not edited after.  It is printed
#  in full before any research number is produced, and dumped verbatim into
#  results.json.
# ==========================================================================
PREREG = dict(
  frozen_note=("Written into this file before either measurement run and not "
               "edited after.  Printed before any research number."),

  # ------------------------------------------------------------------ T1
  T1=dict(
    question=("Is the 4-9% object-specific residual recorded in "
              "EV-MLKEM-d777f0 (validator DEF-1; red team, real family 3-11% "
              "below every ablated control) a property of the real dual "
              "family, or a draw from the ablated ensemble?  It is "
              "unreplicated at n = 2."),

    null=dict(
      name="ABL  (family-ablated null at fixed candidate set; RC-1/RC-3)",
      object_removed=("the ENTIRE dual family: the q-ary lattice, the matrix "
                      "A, the modulus, the sieve geometry of X, the shortness "
                      "of the dual vectors, and the X-Y coupling.  Nothing "
                      "algebraic survives."),
      object_preserved=("N = 17919 rows; m = 35 columns of X; the EXACT "
                        "per-row ||x_i|| of the sieve database, row for row; "
                        "the entrywise standard deviation of Y; the candidate "
                        "set C1 at identical indices; K; and the closed form "
                        "itself, imported unmodified from the archived path."),
      construction=("X_ab[i] = ||x_i||_sieve * g_i/||g_i|| with g_i iid "
                    "N(0,I_35);  Y_ab = rint(N(0, sd_entrywise(Y_sieve))) "
                    "elementwise, independent of X_ab."),
      statistic=("ST-6 ratio = K_eff_trail / (K-1), where K_eff_trail is the "
                 "trailing-spectrum participation ratio of the correlation "
                 "matrix produced by the ARCHIVED closed_form_cov.  NO "
                 "SCORING.  This is the same statistic and the same code path "
                 "as the archived T1 primary observable."),
      n_draws=16,
      can_it_fail=("YES.  The interval is an empirical min/max over 16 "
                   "independent draws of the null ensemble; the real family "
                   "lies outside it or it does not, and both outcomes are "
                   "reachable.  The positive control SENS-T1 below exhibits "
                   "the OUTSIDE end on an object built to differ.")),

    sensitivity_demonstration=dict(
      name="SENS-T1",
      comparator=("RANK5 -- the SAME ablated construction except that the "
                  "rows of X are confined to a fixed random 5-dimensional "
                  "subspace of R^35 before being rescaled to the sieve's "
                  "exact row norms.  Named comparator: the ABL ensemble's own "
                  "16-draw interval on the uniform_25 group."),
      why_this_comparator=("RT-20260804-0ff29a OBJ-3 establishes that the "
                           "uniform group's ST-6 ratio moves with the "
                           "effective rank of X and with nothing else that "
                           "varies between arms.  A rank-5 X is therefore an "
                           "object the statistic is known to be able to read, "
                           "and it is the honest positive control for whether "
                           "a 16-draw interval can resolve an object "
                           "difference at all."),
      threshold_declared_before_the_run=(
          "RANK5's uniform_25 ST-6 ratio must lie BELOW the ABL ensemble's "
          "uniform_25 minimum by at least 0.05 in absolute value.  If it does "
          "not, the instrument cannot resolve a structural difference of that "
          "size at this ensemble size and the T1 comparison is declared "
          "UNINTERPRETABLE for every group."),
      dynamic_range_both_ends=("low end: RANK5's uniform_25 value; high end: "
                               "the ABL ensemble's uniform_25 interval.  Both "
                               "are printed.")),

    derived_before_measuring_any_contrast=dict(
      the_null_i_am_NOT_testing=(
          "I am testing 'the real family is a draw from ABL'.  The null I am "
          "NOT testing is 'my own verdict function discriminates'.  Under it, "
          "the leave-one-out application of the frozen interval rule to ABL's "
          "OWN 16 members must return OUTSIDE for EXACTLY 2 of the 16 -- "
          "EXACTLY ONE OUTSIDE_LOW (the ensemble minimum) and EXACTLY ONE "
          "OUTSIDE_HIGH (the ensemble maximum) -- on EVERY group.  This is "
          "forced by the definition of a min/max interval whenever the 16 "
          "values are pairwise distinct, which is checked."),
      value=dict(loo_outside_count=2, loo_outside_low=1, loo_outside_high=1,
                 loo_false_outside_rate="2/16 = 0.125"),
      if_violated=("my verdict function is wrong and T1 is void -- reported "
                   "as implementation_error, not as a measurement.")),

    null_arm_runs_first=(
        "KN-TECH-6c0e15 mode 4.  The 16 ABL draws are computed and passed "
        "through the frozen verdict function, leave-one-out, and their "
        "verdicts are PRINTED, BEFORE the real family's closed form is "
        "evaluated.  The log ordering and the recorded per-arm elapsed times "
        "are the evidence."),

    frozen_rule=dict(
      inputs="the real family's ST-6 ratio r, and the 16 ABL draws",
      branches=["OUTSIDE_LOW", "INSIDE", "OUTSIDE_HIGH", "NEITHER"],
      definition=("lo = min(draws), hi = max(draws).  OUTSIDE_LOW iff r < lo; "
                  "INSIDE iff lo <= r <= hi; OUTSIDE_HIGH iff r > hi; "
                  "NEITHER iff r or lo or hi is non-finite, or fewer than 8 "
                  "draws are available."),
      exhaustiveness_argument=(
          "The three substantive branches partition the FULL INPUT SPACE, not "
          "merely the statistic's observed range: for finite real r and "
          "finite lo <= hi, trichotomy of the order relation on R gives "
          "exactly one of r < lo, lo <= r <= hi, r > hi, and the three are "
          "pairwise disjoint.  NEITHER is a total catch-all for every "
          "non-finite or under-sampled input, so the rule is defined on every "
          "input and emits exactly one label.  DISCRIMINATION is a separate "
          "question from exhaustiveness (this is the DEV-3 lesson of "
          "KN-TECH-6c0e15 mode 4) and is addressed by the null-first "
          "leave-one-out check and by SENS-T1, not by this argument."),
      secondary_reported="z = (r - mean(draws)) / sd(draws), reported never dispositive"),

    what_a_result_would_and_would_not_mean=(
        "INSIDE means the real family is not separated from a structureless "
        "object of the same shape by this statistic at this ensemble size; it "
        "does NOT prove the residual is zero.  OUTSIDE_LOW means the real "
        "family sits below the whole ablated ensemble on this statistic, on "
        "ONE instance and ONE database; it is NOT an ML-KEM statement, NOT a "
        "cost claim, and NOT an operational sign.")),

  # ------------------------------------------------------------------ T2
  T2=dict(
    question=("RC-4.  Every candidate group in five batches has EXCLUDED the "
              "correct candidate, so no operational sign exists in either "
              "direction (RT-20260804-0ff29a OBJ-8).  Put it in, on the "
              "adjacent-FFT-bin family at matched K."),

    what_is_measured=dict(
      family="STAGEB_LAT, the archived Stage B dual family, N = 4253",
      groups=("adjacent_bins_10 + correct  and  uniform_bins_10 + correct, "
              "K = 11 each -- MATCHED K, the same matching the archive used "
              "for its K=10 groups."),
      s1="mean, min and max of corr(S_correct, S_k) over the 10 wrong candidates",
      s2=("standardised margin m_z = mean(M)/sd(M) with "
          "M_d = S_correct[d] - max_{k wrong} S_k[d].  LARGER m_z = the "
          "correct candidate is more cleanly separated = FEWER samples needed "
          "= EASIER than the independence model predicts."),
      s3="P_lose = fraction of draws with M_d < 0, i.e. some wrong candidate outscores the correct one",
      s4="ST-6 ratio on the K=11 group, adjacent vs uniform at matched K"),

    null=dict(
      name="CAL-PERM-11 (exact independence comparator)",
      object_removed=("ALL across-candidate dependence, including the "
                      "dependence between each wrong candidate and the "
                      "CORRECT candidate.  The draw index is permuted "
                      "independently in every one of the 11 columns."),
      object_preserved=("every column's marginal distribution EXACTLY -- a "
                        "per-column permutation of the draw index is a "
                        "bijection on that column's values."),
      statistic="the same m_z, P_lose and ST-6 ratio, recomputed on each permuted realisation",
      n_realisations=8,
      why_it_is_the_right_null=("MATZOV.Nf's advantage law assumes the "
                                "wrong-candidate scores are independent of "
                                "each other AND of the correct candidate's "
                                "score.  CAL-PERM-11 is that assumption "
                                "imposed on the measured marginals exactly, "
                                "so the contrast isolates dependence and "
                                "nothing else."),
      can_it_fail=("It cannot fail AS A CALIBRATION -- independence is true "
                   "of it by construction, exactly as the archive declares "
                   "for CAL-PERM.  It is used as a COMPARATOR supplying both "
                   "reference and spread, not as a null that could surprise "
                   "us.  The arm that can fail is the REAL one.")),

    sensitivity_demonstration=dict(
      name="SENS-T2",
      comparator="CAL-PERM-11 applied to the same synthetic matrix",
      construction=("synthetic D x 11: correct column = mu + Z_0; each of the "
                    "10 wrong columns = sqrt(1-t) Z_k + sqrt(t) Z_0, with "
                    "Z_0, Z_k iid N(0,1) and mu = 0.5.  t is the fraction of "
                    "each wrong candidate's score shared with the correct "
                    "candidate.  At t = 0 the columns are independent; as t "
                    "grows the common part cancels in M and m_z rises."),
      thresholds_declared_before_the_run=(
          "at t = 0 the frozen rule must emit OP-NULL; at t = 0.75 it must "
          "emit OP-EASIER.  Both ends of the range are exhibited.  If either "
          "fails, the T2 instrument is declared unfit and no T2 verdict is "
          "reported."),
      t_grid=[0.0, 0.10, 0.25, 0.50, 0.75]),

    derived_before_measuring_any_contrast=dict(
      the_null_i_am_NOT_testing=(
          "I am testing 'the real dependence shifts the correct candidate's "
          "separation relative to independence'.  The null I am NOT testing "
          "is 'the CAL-PERM-11 spread is a trustworthy denominator'.  Under "
          "it, the leave-one-out application of the frozen rule to "
          "CAL-PERM-11's OWN 8 realisations must return OP-NULL on the large "
          "majority of them, because every one of them IS an independent "
          "draw of the comparator."),
      threshold=("at least 6 of 8 leave-one-out realisations must return "
                 "OP-NULL in every (p, group) cell.  If 3 or more fire "
                 "OP-HARDER or OP-EASIER, the comparator spread is not "
                 "trustworthy and that cell's T2 verdict is declared "
                 "UNINTERPRETABLE.")),

    null_arm_runs_first=(
        "KN-TECH-6c0e15 mode 4.  In every cell the CAL-PERM-11 arm is built "
        "and passed through the frozen verdict function leave-one-out, and "
        "those verdicts are PRINTED, before the real arm's m_z is compared to "
        "anything.  SENS-T2 runs before either, on synthetic data only."),

    frozen_rule=dict(
      inputs="m_z of the real arm, and the 8 CAL-PERM-11 realisations of m_z",
      branches=["OP-EASIER", "OP-NULL", "OP-HARDER", "OP-NEITHER"],
      definition=("z = (m_z_real - mean(m_z_perm)) / sd(m_z_perm).  "
                  "OP-EASIER iff z > +3; OP-HARDER iff z < -3; OP-NULL iff "
                  "|z| <= 3; OP-NEITHER iff any input is non-finite or "
                  "sd(m_z_perm) <= 0."),
      sign_convention=("m_z is the standardised margin of the CORRECT "
                       "candidate over the maximum wrong candidate.  Real "
                       "dependence RAISING it means the correct candidate is "
                       "better separated than the independence model says, "
                       "i.e. the model is PESSIMISTIC and the attack is "
                       "EASIER than modelled.  Lowering it means HARDER.  "
                       "This is a statement about ONE toy instance and is "
                       "NOT a cost claim."),
      exhaustiveness_argument=(
          "For finite z the three substantive branches are z > 3, |z| <= 3, "
          "z < -3, which partition R by trichotomy and are pairwise "
          "disjoint.  OP-NEITHER is a total catch-all for non-finite inputs "
          "and for a degenerate comparator spread, so the rule is defined on "
          "every input and emits exactly one label.  P_lose is reported "
          "beside m_z and is NOT used by the rule, precisely because it can "
          "saturate at 0 or 1 and a saturated statistic reads nothing -- "
          "declaring that in advance is the point."),
      secondary_reported=["P_lose real and CAL-PERM", "corr(S_correct, S_k)",
                          "ST-6 ratio at matched K = 11"]),

    expectation_stated_before_the_measurement=dict(
      provenance=("Batch 5's matched-K FFT departures were SIGN-INCONSISTENT "
                  "(-3.95%, -1.98%, +2.41% -- VAL-20260804-264ab9 DEF-6, "
                  "RT-20260804-0ff29a OBJ-6), so a directional expectation "
                  "must be stated in advance or it is worthless.  These "
                  "expectations are informed by the archived batch-5 numbers "
                  "-- they are NOT blind -- and that is stated rather than "
                  "hidden."),
      E1=("corr(S_correct, S_k) will be LARGER on average for the "
          "adjacent-bin group than for the uniform-bin group, on at least 2 "
          "of the 3 p values.  Reason: an adjacent-bin candidate agrees with "
          "c* in 9 of its 10 FFT coordinates, so its phase relative to the "
          "correct candidate is a single-coordinate rotation, whereas a "
          "uniform-bin candidate's phase relative to c* is pseudo-random in "
          "all 10."),
      E2=("both mean correlations will be SMALL in absolute value, "
          "|mean corr| < 0.15 in every cell.  Reason: VAL-20260804-264ab9 "
          "MR-10 measures offdiag(R_raw) ~ 0.006 among adjacent-bin wrong "
          "candidates because an adjacent bin differs by a FULL bin 2 pi/p, "
          "so no rank-one common mode forms; I expect the correct candidate "
          "to sit in the same regime."),
      E3=("m_z will be LARGER for the adjacent group than for the uniform "
          "group at matched K = 11.  Reason: fewer effective independent "
          "wrong candidates on the adjacent side means a smaller expected "
          "maximum over them."),
      E4_THE_ONE_I_CANNOT_PREDICT=(
          "I do NOT predict the sign of the frozen rule's verdict, in either "
          "group.  Two effects of OPPOSITE sign are present and I cannot "
          "derive which dominates: adjacent-bin candidates have HIGHER mean "
          "scores than uniform ones, which pushes m_z DOWN (toward "
          "OP-HARDER), while they are more correlated with the correct "
          "candidate, which cancels common noise in M and pushes m_z UP "
          "(toward OP-EASIER).  Declaring this in advance is what stops a "
          "post-hoc reading of whichever sign appears."),
      what_would_refute_each=("E1 is refuted if the uniform group's mean "
                              "correlation exceeds the adjacent group's on 2 "
                              "or more p values; E2 if any cell has "
                              "|mean corr| >= 0.15; E3 if uniform m_z exceeds "
                              "adjacent m_z on 2 or more p values.")),

    what_a_result_would_and_would_not_mean=(
        "Whatever sign appears, it is ONE toy instance, ONE database, D=4000 "
        "error draws, K=11.  It is NOT an ML-KEM statement, NOT a security "
        "claim in either direction, NOT a cost model, NOT a correction to "
        "MATZOV.Nf, and NOT a statement about any FIPS 203 parameter set.  It "
        "is the first measurement in this campaign in which the correct "
        "candidate is present at all.")),

  explicit_non_claims=[
    "No ML-KEM break.  No attack implemented, run, or claimed.  No speedup.",
    "No security proof and no security claim in either direction.",
    "No FIPS 203 parameter set affected or cleared.  Toy scale, AGENTS.md rules 4 and 7.",
    "No cost claim, no exponent moved, no Nf recomputed or corrected.",
    "No heuristic declared validated or refuted.  No lane closed or opened.",
    "No EV-MLKEM-* or KN-* status change made or proposed.  Rule 12 UNMET and UNWAIVED.",
    "solve_claim_certificate = none.  The membership certificate certifies VECTORS only.",
  ],
)


# ==========================================================================
#  import the ARCHIVED closed form from its exact archived path.
#  Not copied, not reimplemented, not vendored: loaded from the file the
#  Coordinator committed in snapshot 82bcbbe4.
# ==========================================================================
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):   # count-bounded by EOF
            h.update(chunk)
    return h.hexdigest()


def load_archived_module():
    spec = importlib.util.spec_from_file_location("archived_dependence",
                                                  ARCHIVED_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ==========================================================================
#  independent certificate re-verification -- my own code, stock numpy,
#  no g6k, no fpylll, and NOT the archived certify()
# ==========================================================================
def recertify(X, Y, A, q, label):
    """y == A^T x (mod q), recomputed from the archived integers and A alone."""
    resid = np.mod(X.dot(A) - Y, q)
    viol = int(np.count_nonzero(resid))
    V = np.concatenate([X, Y], axis=1)
    # exact Python bigint on a fixed row sample: cannot silently overflow
    rng = np.random.default_rng(20260805740999)
    rows = rng.choice(X.shape[0], size=min(60, X.shape[0]), replace=False)
    Al, bad_big = A.tolist(), 0
    for i in rows:                                    # count-bounded
        xi, yi = X[i].tolist(), Y[i].tolist()
        for j in range(A.shape[1]):
            acc = 0
            for t in range(A.shape[0]):
                acc += int(xi[t]) * int(Al[t][j])
            if (acc - int(yi[j])) % q != 0:
                bad_big += 1
    return dict(family=label, kind="lattice_membership",
                checked_vectors=int(X.shape[0]),
                checked_entries=int(X.shape[0] * A.shape[1]),
                violating_entries=viol,
                bigint_rows_checked=int(len(rows)),
                bigint_violating_entries=int(bad_big),
                all_zero_vectors=int(np.count_nonzero(np.all(V == 0, axis=1))),
                duplicate_x_rows=int(X.shape[0] - len(set(map(tuple, X.tolist())))),
                verified=bool(viol == 0 and bad_big == 0),
                method=("numpy int64 over all rows AND exact Python bigint on "
                        "60 rows, from A and the emitted vectors only; written "
                        "in resolve.py, independent of the archived certify()"),
                solve_claim_certificate="none -- pure measurement run")


# ==========================================================================
#  statistics
# ==========================================================================
def st6_ratio_from_cov(dep, cov, sub):
    """ST-6 = trailing-spectrum participation ratio of R, as a ratio to K-1.
    Same definition as dependence.py dep_stats()['K_eff_trail']."""
    sl = np.ix_(sub, sub)
    R = dep.cov_to_corr(cov[sl])
    K = R.shape[0]
    ev = np.sort(np.linalg.eigvalsh(R))[::-1]
    tr = ev[1:]
    return float((tr.sum() ** 2 / (tr ** 2).sum()) / (K - 1))


T1_MIN_DRAWS = 8


def t1_verdict(r, draws):
    """FROZEN.  Four branches, total on every input.  See PREREG.T1.frozen_rule."""
    d = [float(x) for x in draws if np.isfinite(x)]
    if (not np.isfinite(r)) or len(d) < T1_MIN_DRAWS:
        return "NEITHER", ("non-finite statistic or fewer than %d usable draws "
                           "(%d)" % (T1_MIN_DRAWS, len(d)))
    lo, hi = min(d), max(d)
    if r < lo:
        return "OUTSIDE_LOW", "r=%.6f < ensemble min %.6f" % (r, lo)
    if r > hi:
        return "OUTSIDE_HIGH", "r=%.6f > ensemble max %.6f" % (r, hi)
    return "INSIDE", "ensemble min %.6f <= r=%.6f <= ensemble max %.6f" % (lo, r, hi)


def t2_verdict(mz_real, mz_perm):
    """FROZEN.  Four branches, total on every input.  See PREREG.T2.frozen_rule."""
    a = np.asarray([x for x in mz_perm if np.isfinite(x)], dtype=float)
    if (not np.isfinite(mz_real)) or a.size < 2:
        return "OP-NEITHER", "non-finite real statistic or fewer than 2 comparator draws", float("nan")
    sd = float(a.std(ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        return "OP-NEITHER", "comparator spread is zero or non-finite", float("nan")
    z = float((mz_real - a.mean()) / sd)
    if z > 3.0:
        return "OP-EASIER", "z=%+.2f > +3" % z, z
    if z < -3.0:
        return "OP-HARDER", "z=%+.2f < -3" % z, z
    return "OP-NULL", "|z|=%.2f <= 3" % abs(z), z


def margin_stats(G, correct_col, wrong_cols):
    """m_z, P_lose and the correlation profile on a D x K score block."""
    sc = np.asarray(G[:, correct_col], dtype=np.float64)
    W = np.asarray(G[:, wrong_cols], dtype=np.float64)
    M = sc - W.max(axis=1)
    sd = float(M.std(ddof=1))
    mz = float(M.mean() / sd) if sd > 0 else float("nan")
    cs = []
    ssd = sc.std(ddof=1)
    for j in range(W.shape[1]):
        wsd = W[:, j].std(ddof=1)
        cs.append(float(np.corrcoef(sc, W[:, j])[0, 1]) if (ssd > 0 and wsd > 0)
                  else float("nan"))
    cs = np.array(cs, dtype=float)
    return dict(m_z=mz, margin_mean=float(M.mean()), margin_sd=sd,
                P_lose=float(np.mean(M < 0.0)),
                corr_mean=float(np.nanmean(cs)), corr_min=float(np.nanmin(cs)),
                corr_max=float(np.nanmax(cs)),
                corr_all=[float(x) for x in cs],
                score_mean_correct=float(sc.mean()),
                score_mean_wrong=float(W.mean()))


def calperm11(G, cols, n_real, seed):
    """CAL-PERM-11: permute the draw index INDEPENDENTLY in every column,
    including the correct candidate's.  Marginals exact, all dependence
    destroyed exactly.  Count-bounded."""
    B = np.asarray(G[:, cols], dtype=np.float64)
    D, K = B.shape
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_real):                              # count-bounded
        H = np.empty_like(B)
        for k in range(K):                               # count-bounded
            H[:, k] = B[rng.permutation(D), k]
        out.append(H)
    return out


# ==========================================================================
def env_block():
    return dict(python=sys.version.split()[0], numpy=np.__version__,
                platform=platform.platform(), executable=sys.executable,
                cpu_count=os.cpu_count())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["t1", "t2"], required=True)
    ap.add_argument("--outdir", default=os.path.dirname(os.path.abspath(__file__)))
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
    say("SCOPE: m=%d n=%d q=%d sigma=%.1f eta=%d, ONE instance, ONE database, "
        "TOY SCALE.  No ML-KEM break claim, no security proof, no FIPS 203 "
        "parameter set affected or cleared, no speedup, no cost claim, no "
        "exponent moved." % (M_, N_, Q, SIGMA, ETA))
    say("rule12_status: UNMET and UNWAIVED, inherited.  No EV-MLKEM-* status change.")
    say("certificate: solve_claim_certificate = none (pure measurement run).")
    say("")
    say("FROZEN PRE-REGISTRATION, printed IN FULL before any research number:")
    for ln in json.dumps(PREREG[args.stage.upper()], indent=1).splitlines():
        say("  PREREG| " + ln)
    say("  PREREG| explicit_non_claims: " + json.dumps(PREREG["explicit_non_claims"]))
    say("")

    res = dict(task="TASK-20260805-74a8e9", batch="BATCH-4bc9bc",
               goal="GOAL-MLKEM-004", script_version=SCRIPT_VERSION,
               stage=args.stage, states_a_conclusion=False,
               scope=("m=35 n=25 d=60 q=127 sigma=2 eta=2; Stage B sieve dim "
                      "50.  ONE instance, ONE database.  TOY SCALE.  No ML-KEM "
                      "break claim, no security proof, no FIPS 203 parameter "
                      "set affected or cleared, no speedup, no cost claim, no "
                      "exponent moved."),
               rule12_status=("UNMET and UNWAIVED, inherited.  No EV-MLKEM-* "
                              "status change is made or proposed."),
               certificate_kind_for_solve_claims=("none -- pure measurement "
                      "run (docs/claims-and-verification.md).  The "
                      "lattice-membership certificate below certifies the "
                      "VECTORS only."),
               prereg=PREREG, seeds_inherited=ARCH_SEEDS, seeds_minted=MY_SEEDS)

    # ---------------------------------------------------------------- setup
    say("importing the ARCHIVED closed form from its committed path (not copied):")
    say("  %s" % ARCHIVED_SCRIPT)
    dep = load_archived_module()
    hashes = {p: sha256_of(p) for p in (ARCHIVED_SCRIPT, ARCHIVED_VECTORS,
                                        ARCHIVED_RESULTS)}
    for p, h in hashes.items():
        say("  sha256 %s  %s" % (h[:16], os.path.relpath(p, REPO)))
    res["archived_inputs_sha256"] = {os.path.relpath(p, REPO): h
                                     for p, h in hashes.items()}
    say("  archived module exposes closed_form_cov=%s dep_stats=%s "
        "score_means=%s phases=%s cov_to_corr=%s"
        % (hasattr(dep, "closed_form_cov"), hasattr(dep, "dep_stats"),
           hasattr(dep, "score_means"), hasattr(dep, "phases"),
           hasattr(dep, "cov_to_corr")))

    # instance regeneration from the seed, bit for bit
    rgi = np.random.default_rng(INSTANCE_SEED)
    A = rgi.integers(0, Q, size=(M_, N_), dtype=np.int64)
    s = dep.centered_binomial(rgi, ETA, N_)

    V = json.load(open(ARCHIVED_VECTORS))
    A_arch = np.array(V["A"], dtype=np.int64)
    s_arch = np.array(V["secret_s"], dtype=np.int64)
    a_ok = bool(np.array_equal(A, A_arch))
    s_ok = bool(np.array_equal(s, s_arch))
    say("instance regenerates from seed %d: A identical=%s  s identical=%s"
        % (INSTANCE_SEED, a_ok, s_ok))
    res["instance_regenerates_from_seed"] = dict(A_identical=a_ok, s_identical=s_ok)
    if not (a_ok and s_ok):
        say("INSTANCE MISMATCH -- run is implementation_error, no measurement reported")
        res["status"] = "implementation_error"
        res["reason"] = "archived instance does not regenerate from the recorded seed"
        json.dump(res, open(os.path.join(args.outdir,
                  "results_%s.json" % args.stage), "w"), indent=1)
        return

    # ------------------------------------------------- known-answer controls
    say("")
    say("KNOWN-ANSWER CONTROLS (answers known independently of this run), run "
        "BEFORE any research number.  These are the ARCHIVED instrument checks, "
        "executed from the archived module:")
    kac = dep.known_answer_controls(say)
    res["known_answer_controls"] = kac
    if not kac["passed"]:
        say("KNOWN-ANSWER CONTROL FAILED -- instrument unfit, run is "
            "implementation_error, no measurement reported")
        res["status"] = "implementation_error"
        res["reason"] = "archived known-answer control failed"
        json.dump(res, open(os.path.join(args.outdir,
                  "results_%s.json" % args.stage), "w"), indent=1)
        return

    if args.stage == "t1":
        stage_t1(args, res, say, dep, A, s, V, t_start)
    else:
        stage_t2(args, res, say, dep, A, s, V, t_start)

    res["environment"] = env_block()
    res["timings"] = dict(total_seconds=round(time.time() - t_start, 1),
                          peak_rss_mb=round(
                              resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                              / 1024.0, 1))
    res["log"] = log
    outp = os.path.join(args.outdir, "results_%s.json" % args.stage)
    json.dump(res, open(outp, "w"), indent=1)
    say("wrote %s" % outp)
    say("STAGE %s COMPLETE.  %.1fs, peak RSS %.0f MB"
        % (args.stage.upper(), time.time() - t_start,
           res["timings"]["peak_rss_mb"]))


# ==========================================================================
#                                   T1
# ==========================================================================
def stage_t1(args, res, say, dep, A, s, V, t_start):
    Xs = np.array(V["families"]["SIEVE"]["X"], dtype=np.int64)
    Ys = np.array(V["families"]["SIEVE"]["Y"], dtype=np.int64)
    N = Xs.shape[0]
    say("")
    say("re-certifying the archived family from vectors.json and A ALONE, with "
        "code written in resolve.py (not the archived certify()):")
    cert = recertify(Xs, Ys, A, Q, "SIEVE")
    say("  SIEVE verified=%s violating=%d/%d bigint_violating=%d/%d dup_x=%d"
        % (cert["verified"], cert["violating_entries"], cert["checked_entries"],
           cert["bigint_violating_entries"],
           cert["bigint_rows_checked"] * A.shape[1], cert["duplicate_x_rows"]))
    res["certificate"] = cert
    if not cert["verified"]:
        say("CERTIFICATE FAILED -- run is invalid_measurement")
        res["status"] = "invalid_measurement"
        res["reason"] = "lattice-membership certificate failed on re-verification"
        return

    # candidate set, reconstructed with the archived seed and the archived
    # constructor -- so the columns are the SAME columns the archive measured
    rgc1 = np.random.default_rng(ARCH_SEEDS["candidates"])
    c1 = dep.make_candidates_A(rgc1, s, Q, N_, ETA, 25, 512, 64)
    C1 = np.array([c[2] for c in c1], dtype=np.int64)
    g1 = dep.group_index([c[1] for c in c1])
    say("  candidate set reconstructed: %s" % {k: len(v) for k, v in g1.items()})

    idx_cf = (g1["near_miss"][:25] + g1["uniform"][:25]
              + g1["secret_distribution"][:25])
    SUB = dict(near_miss=list(range(8)), near_miss_25=list(range(25)),
               uniform_8=list(range(25, 33)), uniform_25=list(range(25, 50)),
               secret_distribution_25=list(range(50, 75)))
    GROUPS = ["near_miss", "near_miss_25", "uniform_8", "uniform_25",
              "secret_distribution_25"]

    xs2 = (Xs * Xs).sum(axis=1).astype(np.float64)
    sdY = float(Ys.astype(np.float64).std())          # entrywise, population
    say("  ablation targets: N=%d  mean||x||^2=%.6f  entrywise sd(Y)=%.6f"
        % (N, xs2.mean(), sdY))
    res["ablation_targets"] = dict(N=int(N), mean_xnorm2=float(xs2.mean()),
                                   entrywise_sd_Y=sdY)

    def cf_ratios(X, Y, tag):
        t = time.time()
        cP, sP = dep.phases(Y, s, C1[idx_cf], Q, True)
        cov, _, _ = dep.closed_form_cov(X, cP, sP, SIGMA, Q)
        out = {g: st6_ratio_from_cov(dep, cov, SUB[g]) for g in GROUPS}
        out["_seconds"] = round(time.time() - t, 1)
        say("    %-22s %s  (%.0fs)"
            % (tag, "  ".join("%s=%.4f" % (g[:6], out[g]) for g in GROUPS),
               out["_seconds"]))
        return out

    def make_ablated(seed):
        rng = np.random.default_rng(seed)
        G = rng.normal(size=(N, M_))
        G /= np.linalg.norm(G, axis=1, keepdims=True)
        Xa = G * np.sqrt(xs2)[:, None]
        Ya = np.rint(rng.normal(0.0, sdY, size=(N, N_))).astype(np.int64)
        return Xa, Ya

    # ---------------- NULL ARM FIRST (KN-TECH-6c0e15 mode 4) ----------------
    n_draws = PREREG["T1"]["null"]["n_draws"]
    say("")
    say("=== T1 NULL ARM, RUN FIRST.  %d draws of ABL, the family-ablated null. "
        "The real family is NOT touched until every line below is printed. ==="
        % n_draws)
    abl = []
    for d in range(n_draws):                            # count-bounded
        Xa, Ya = make_ablated(MY_SEEDS["ablated_base"] + d)
        abl.append(cf_ratios(Xa, Ya, "ABL draw %02d (seed %d)"
                             % (d, MY_SEEDS["ablated_base"] + d)))
        del Xa, Ya

    ens = {g: [a[g] for a in abl] for g in GROUPS}
    say("")
    say("  ABL ensemble, %d draws:" % n_draws)
    for g in GROUPS:
        v = np.array(ens[g])
        say("    %-24s min %.4f  max %.4f  mean %.4f  sd %.4f  distinct %s"
            % (g, v.min(), v.max(), v.mean(), v.std(ddof=1),
               len(set(v.tolist())) == v.size))

    # the value DERIVED BEFORE MEASURING: leave-one-out on the null's own members
    say("")
    say("  NULL-FIRST leave-one-out through MY OWN frozen verdict function.")
    say("  DERIVED BEFORE THE RUN: exactly 2 of %d OUTSIDE per group, exactly "
        "1 LOW and 1 HIGH, whenever the draws are pairwise distinct." % n_draws)
    loo = {}
    for g in GROUPS:
        vs = ens[g]
        labs = []
        for i in range(len(vs)):                        # count-bounded
            lab, _ = t1_verdict(vs[i], vs[:i] + vs[i + 1:])
            labs.append(lab)
        cnt = {k: labs.count(k) for k in
               ("OUTSIDE_LOW", "INSIDE", "OUTSIDE_HIGH", "NEITHER")}
        ok = (cnt["OUTSIDE_LOW"] == 1 and cnt["OUTSIDE_HIGH"] == 1
              and cnt["NEITHER"] == 0)
        loo[g] = dict(counts=cnt, matches_derived_value=bool(ok), labels=labs)
        say("    %-24s %s   matches derived value: %s"
            % (g, json.dumps(cnt), ok))
    all_ok = all(loo[g]["matches_derived_value"] for g in GROUPS)
    say("  derived-value check: %s" % ("PASS on every group" if all_ok
                                       else "FAIL -- verdict function is wrong"))
    res["T1_null_first_loo"] = dict(
        derived_before_the_run=PREREG["T1"]["derived_before_measuring_any_contrast"],
        per_group=loo, all_groups_match_derived_value=bool(all_ok))
    if not all_ok:
        say("T1 VOID: my own verdict function does not emit the value derived "
            "for it under the null.  implementation_error, no T1 measurement "
            "is reported.")
        res["T1"] = dict(status="implementation_error",
                         reason="verdict function failed its derived null value")
        res["status"] = "implementation_error"
        return

    # ---------------- SENS-T1, the sensitivity demonstration ----------------
    say("")
    say("=== SENS-T1 sensitivity demonstration.  Comparator: the ABL ensemble's "
        "own uniform_25 interval.  Threshold declared BEFORE the run: RANK5 "
        "must sit at least 0.05 BELOW the ensemble minimum. ===")
    rq = np.random.default_rng(MY_SEEDS["rank5_dirs"])
    Qb, _ = np.linalg.qr(rq.normal(size=(M_, 5)))       # 35 x 5 orthonormal
    rr = np.random.default_rng(MY_SEEDS["rank5_rows"])
    G5 = rr.normal(size=(N, 5)).dot(Qb.T)
    G5 /= np.linalg.norm(G5, axis=1, keepdims=True)
    X5 = G5 * np.sqrt(xs2)[:, None]
    ry = np.random.default_rng(MY_SEEDS["rank5_Y"])
    Y5 = np.rint(ry.normal(0.0, sdY, size=(N, N_))).astype(np.int64)
    say("  RANK5: rows of X confined to a fixed random 5-dim subspace of R^35, "
        "rescaled to the sieve's exact row norms; rank(X)=%d"
        % int(np.linalg.matrix_rank(X5)))
    r5 = cf_ratios(X5, Y5, "RANK5 positive control")
    del X5, Y5, G5
    lo_u = float(np.min(ens["uniform_25"]))
    gap = lo_u - r5["uniform_25"]
    sens_pass = bool(gap >= 0.05)
    say("  uniform_25: ABL ensemble min %.4f, RANK5 %.4f, gap %.4f, "
        "threshold 0.0500 -> %s"
        % (lo_u, r5["uniform_25"], gap, "PASS" if sens_pass else "FAIL"))
    say("  dynamic range exhibited, both ends: RANK5 %.4f ... ABL [%.4f, %.4f]"
        % (r5["uniform_25"], lo_u, float(np.max(ens["uniform_25"]))))
    res["T1_sensitivity"] = dict(
        declared=PREREG["T1"]["sensitivity_demonstration"],
        rank5=r5, ensemble_uniform25_min=lo_u, gap=float(gap),
        threshold=0.05, passed=sens_pass)

    # ---------------- the REAL arm, last ----------------
    say("")
    say("=== T1 REAL ARM.  The certified dual family, same closed form, same "
        "candidate columns. ===")
    real = cf_ratios(Xs, Ys, "SIEVE (certified)")
    say("  archived cross-check (RT-20260804-0ff29a OBJ-1 table, closed form, "
        "ratio to K-1): near_miss_25 0.7283, secret_distribution_25 0.4149, "
        "uniform_25 0.9194")

    say("")
    say("=== T1 VERDICTS, from the frozen rule, emitted mechanically ===")
    verdicts = {}
    for g in GROUPS:
        lab, why = t1_verdict(real[g], ens[g])
        v = np.array(ens[g])
        z = float((real[g] - v.mean()) / v.std(ddof=1))
        verdicts[g] = dict(branch=lab, reason=why, real=real[g],
                           ensemble_min=float(v.min()), ensemble_max=float(v.max()),
                           ensemble_mean=float(v.mean()),
                           ensemble_sd=float(v.std(ddof=1)), z=z)
        say("  %-24s real %.4f  interval [%.4f, %.4f]  z=%+.2f  -> %s"
            % (g, real[g], v.min(), v.max(), z, lab))
    if not sens_pass:
        say("  NOTE: SENS-T1 FAILED its pre-declared threshold, so every branch "
            "above is declared UNINTERPRETABLE per the pre-registration.")

    res["T1"] = dict(
        what_is_measured=("ST-6 ratio K_eff_trail/(K-1) from the ARCHIVED "
                          "closed_form_cov, no scoring, on identical candidate "
                          "columns"),
        n_ablated_draws=n_draws,
        ablated_seeds=[MY_SEEDS["ablated_base"] + d for d in range(n_draws)],
        ablated_draws={g: ens[g] for g in GROUPS},
        ablated_per_draw=abl,
        real=real, verdicts=verdicts,
        sensitivity_passed=sens_pass,
        interpretable=bool(sens_pass),
        status="completed_valid" if sens_pass else "uninterpretable_by_prereg")
    res["status"] = res["T1"]["status"]


# ==========================================================================
#                                   T2
# ==========================================================================
def stage_t2(args, res, say, dep, A, s, V, t_start):
    Xb = np.array(V["families"]["STAGEB_LAT"]["X"], dtype=np.int64)
    Yb = np.array(V["families"]["STAGEB_LAT"]["Y"], dtype=np.int64)
    Nb = Xb.shape[0]
    say("")
    say("re-certifying STAGEB_LAT from vectors.json and A[:, :%d] ALONE, with "
        "code written in resolve.py:" % K_LAT)
    cert = recertify(Xb, Yb, A[:, :K_LAT], Q, "STAGEB_LAT")
    say("  STAGEB_LAT verified=%s violating=%d/%d bigint_violating=%d/%d"
        % (cert["verified"], cert["violating_entries"], cert["checked_entries"],
           cert["bigint_violating_entries"], cert["bigint_rows_checked"] * K_LAT))
    res["certificate"] = cert
    if not cert["verified"]:
        say("CERTIFICATE FAILED -- run is invalid_measurement")
        res["status"] = "invalid_measurement"
        res["reason"] = "lattice-membership certificate failed on re-verification"
        return

    D = 4000
    n_cal = PREREG["T2"]["null"]["n_realisations"]

    # ---------------- SENS-T2, before any research object is touched --------
    say("")
    say("=== SENS-T2 sensitivity demonstration, on SYNTHETIC data only.  "
        "Thresholds declared BEFORE the run: t=0 must emit OP-NULL, t=0.75 "
        "must emit OP-EASIER. ===")
    sens_rows = []
    for t in PREREG["T2"]["sensitivity_demonstration"]["t_grid"]:   # count-bounded
        rng = np.random.default_rng(MY_SEEDS["t2_sens"] + int(round(t * 100)))
        Z0 = rng.standard_normal(D)
        W = np.empty((D, 11))
        W[:, 0] = 0.5 + Z0
        for k in range(10):                             # count-bounded
            W[:, k + 1] = (np.sqrt(1.0 - t) * rng.standard_normal(D)
                           + np.sqrt(t) * Z0)
        st = margin_stats(W, 0, list(range(1, 11)))
        perms = calperm11(W, list(range(11)), n_cal, MY_SEEDS["t2_sens"] + 9000)
        mzp = [margin_stats(H, 0, list(range(1, 11)))["m_z"] for H in perms]
        lab, why, z = t2_verdict(st["m_z"], mzp)
        sens_rows.append(dict(t=t, m_z=st["m_z"], m_z_perm_mean=float(np.mean(mzp)),
                              corr_mean=st["corr_mean"], P_lose=st["P_lose"],
                              z=z, branch=lab))
        say("  t=%.2f  m_z %8.4f  CAL-PERM m_z %8.4f  mean corr %+.4f  "
            "P_lose %.4f  z=%+8.2f -> %s"
            % (t, st["m_z"], float(np.mean(mzp)), st["corr_mean"],
               st["P_lose"], z, lab))
    s_t0 = [r for r in sens_rows if r["t"] == 0.0][0]["branch"]
    s_t75 = [r for r in sens_rows if r["t"] == 0.75][0]["branch"]
    sens_pass = bool(s_t0 == "OP-NULL" and s_t75 == "OP-EASIER")
    say("  SENS-T2 gate: t=0 -> %s (need OP-NULL); t=0.75 -> %s (need "
        "OP-EASIER)  -> %s" % (s_t0, s_t75, "PASS" if sens_pass else "FAIL"))
    res["T2_sensitivity"] = dict(
        declared=PREREG["T2"]["sensitivity_demonstration"],
        rows=sens_rows, t0_branch=s_t0, t75_branch=s_t75, passed=sens_pass)
    if not sens_pass:
        say("T2 INSTRUMENT UNFIT by its own pre-declared gate.  No T2 verdict "
            "is reported.")
        res["T2"] = dict(status="instrument_unfit",
                         reason="SENS-T2 failed its pre-declared thresholds")
        res["status"] = "instrument_unfit"
        return

    # ---------------- the Stage B construction, from the archive ------------
    A_fft, s_fft, s_lat = A[:, K_LAT:], s[K_LAT:], s[:K_LAT]
    psi = 2.0 * np.pi * np.mod(Yb.dot(s_lat), Q).astype(np.float64) / Q
    alpha = np.mod(Xb.dot(A_fft), Q)
    arch = json.load(open(ARCHIVED_RESULTS))

    t2 = dict(design=dict(m=M_, n=N_, k_lat=K_LAT, k_fft=K_FFT, k_enum=0,
                          p_values=list(P_VALUES), beta_sieve=M_ + K_LAT,
                          n_vectors=int(Nb), n_draws=D,
                          source=("reconstructed from the archived "
                                  "dependence.py T2 block with the archived "
                                  "seeds; the K=10 groups are re-derived and "
                                  "checked against the archive bit for bit")),
         per_p={})

    for p in P_VALUES:                                   # count-bounded
        say("")
        say("=== T2  p=%d ===" % p)
        ahat = np.mod(np.rint(p * alpha.astype(np.float64) / Q).astype(np.int64), p)
        c_star = np.mod(s_fft, p)
        cands = [("correct_bin", "correct", c_star.copy())]
        seen = {tuple(c_star.tolist())}
        for j in range(K_FFT):                           # count-bounded
            for dlt in (1, -1):                          # count-bounded
                c = c_star.copy(); c[j] = (c[j] + dlt) % p
                tk = tuple(c.tolist())
                if tk in seen:
                    continue
                seen.add(tk)
                cands.append(("adjbin_%02d_%+d" % (j, dlt), "near_miss", c))
        rngc = np.random.default_rng(ARCH_SEEDS["stageb"] + p)
        for i in range(256):                             # count-bounded
            cands.append(("uniform_%03d" % i, "uniform",
                          rngc.integers(0, p, size=K_FFT, dtype=np.int64)))
        Cb = np.array([c[2] for c in cands], dtype=np.int64)
        gb = dep.group_index([c[1] for c in cands])

        base = 2.0 * np.pi * alpha.dot(s_fft).astype(np.float64) / Q
        theta = base[:, None] - 2.0 * np.pi * ahat.dot(Cb.T).astype(np.float64) / p
        cosT, sinT = np.cos(theta), np.sin(theta)
        cP = np.cos(psi)[:, None] * cosT - np.sin(psi)[:, None] * sinT
        sP = np.sin(psi)[:, None] * cosT + np.cos(psi)[:, None] * sinT
        tt = time.time()
        Mb = dep.score_means(Xb.astype(np.float64), cP, sP, D, 250,
                             ARCH_SEEDS["error_draws"] + p, M_, Q, SIGMA)
        say("  scored D=%d K=%d in %.0fs (archived seeds, archived scorer)"
            % (D, Cb.shape[0], time.time() - tt))

        # ---- known-answer check against the archive, BEFORE new statistics
        kacp = {}
        for gname, idxs in (("adjacent_bins_10", gb["near_miss"][:10]),
                            ("uniform_bins_10", gb["uniform"][:10])):
            mine = dep.dep_stats(Mb, idxs, store_R=False)["K_eff_trail"]["value"]
            theirs = arch["T2"]["per_p"][str(p)]["groups"][gname]["K_eff_trail"]["value"]
            kacp[gname] = dict(mine=float(mine), archived=float(theirs),
                               abs_delta=float(abs(mine - theirs)))
            say("  KAC-T2 %-18s K_eff_trail mine %.10f  archived %.10f  "
                "delta %.2e" % (gname, mine, theirs, abs(mine - theirs)))
        t2_kac_ok = all(v["abs_delta"] < 1e-9 for v in kacp.values())
        say("  KAC-T2: the reconstruction reproduces the archived K=10 "
            "statistics: %s" % t2_kac_ok)

        correct_idx = gb["correct"][0]
        cells = dict(
            adjacent_plus_correct=gb["near_miss"][:10],
            uniform_plus_correct=gb["uniform"][:10])

        pres = dict(p=p, known_answer_vs_archive=kacp,
                    reproduces_archive=bool(t2_kac_ok), cells={})
        for cname, wrong in cells.items():               # count-bounded
            cols = [correct_idx] + list(wrong)
            block = Mb[:, cols]
            perms = calperm11(Mb, cols, n_cal,
                              MY_SEEDS["t2_calperm"] + p + len(cname))
            mzp = [margin_stats(H, 0, list(range(1, 11)))["m_z"] for H in perms]

            # ---- NULL ARM FIRST: the comparator's own members, LOO
            loo_lab = []
            for i in range(len(mzp)):                    # count-bounded
                lab, _, _ = t2_verdict(mzp[i], mzp[:i] + mzp[i + 1:])
                loo_lab.append(lab)
            n_null = loo_lab.count("OP-NULL")
            loo_ok = bool(n_null >= 6)
            say("  [%s] NULL ARM FIRST -- CAL-PERM-11 leave-one-out through my "
                "own verdict function: %s  (need >=6 OP-NULL of %d) -> %s"
                % (cname, json.dumps({k: loo_lab.count(k) for k in set(loo_lab)}),
                   n_cal, "trustworthy" if loo_ok else "UNINTERPRETABLE"))

            st = margin_stats(block, 0, list(range(1, 11)))
            st6_real = dep.dep_stats(Mb, cols, store_R=False)["K_eff_trail"]["value"] / 10.0
            st6_perm = [dep.dep_stats(H, list(range(11)),
                                      store_R=False)["K_eff_trail"]["value"] / 10.0
                        for H in perms]
            lab, why, z = t2_verdict(st["m_z"], mzp)
            if not loo_ok:
                lab_eff = "UNINTERPRETABLE"
            else:
                lab_eff = lab
            say("  [%s] K=11  mean corr(S_correct,S_k) %+.4f  [%+.4f, %+.4f]"
                % (cname, st["corr_mean"], st["corr_min"], st["corr_max"]))
            say("  [%s] m_z %8.4f   CAL-PERM-11 m_z %8.4f +- %.4f   z=%+.2f"
                % (cname, st["m_z"], float(np.mean(mzp)),
                   float(np.std(mzp, ddof=1)), z))
            say("  [%s] P_lose real %.5f   CAL-PERM-11 %.5f   (secondary, can "
                "saturate)" % (cname, st["P_lose"],
                               float(np.mean([margin_stats(H, 0, list(range(1, 11)))["P_lose"]
                                              for H in perms]))))
            say("  [%s] ST-6 ratio at matched K=11: real %.4f  CAL-PERM-11 %.4f"
                % (cname, st6_real, float(np.mean(st6_perm))))
            say("  [%s] VERDICT (frozen rule): %s  (%s)" % (cname, lab_eff, why))
            pres["cells"][cname] = dict(
                K=11, wrong_candidates=len(wrong),
                null_first_loo=dict(labels=loo_lab, n_op_null=n_null,
                                    threshold=6, trustworthy=loo_ok),
                real=st, m_z_perm=mzp,
                m_z_perm_mean=float(np.mean(mzp)),
                m_z_perm_sd=float(np.std(mzp, ddof=1)),
                P_lose_perm_mean=float(np.mean(
                    [margin_stats(H, 0, list(range(1, 11)))["P_lose"] for H in perms])),
                st6_ratio_K11_real=float(st6_real),
                st6_ratio_K11_perm_mean=float(np.mean(st6_perm)),
                z=z, branch=lab, branch_effective=lab_eff, reason=why)
        t2["per_p"][str(p)] = pres
        del Mb, cP, sP, cosT, sinT, theta

    # ---- score the pre-declared expectations E1-E3 mechanically
    say("")
    say("=== T2 EXPECTATIONS, declared BEFORE the measurement, scored "
        "mechanically ===")
    e1 = e3 = 0
    e2_max = 0.0
    for p in P_VALUES:
        ca = t2["per_p"][str(p)]["cells"]["adjacent_plus_correct"]
        cu = t2["per_p"][str(p)]["cells"]["uniform_plus_correct"]
        if ca["real"]["corr_mean"] > cu["real"]["corr_mean"]:
            e1 += 1
        if ca["real"]["m_z"] > cu["real"]["m_z"]:
            e3 += 1
        e2_max = max(e2_max, abs(ca["real"]["corr_mean"]),
                     abs(cu["real"]["corr_mean"]))
        say("  p=%d  corr adj %+.4f vs unif %+.4f   |   m_z adj %8.4f vs unif "
            "%8.4f" % (p, ca["real"]["corr_mean"], cu["real"]["corr_mean"],
                       ca["real"]["m_z"], cu["real"]["m_z"]))
    exp_res = dict(
        E1_adjacent_corr_greater=dict(held_on=e1, of=3, met=bool(e1 >= 2)),
        E2_abs_mean_corr_below_0p15=dict(max_abs=float(e2_max),
                                         met=bool(e2_max < 0.15)),
        E3_adjacent_mz_greater=dict(held_on=e3, of=3, met=bool(e3 >= 2)),
        E4=("no prediction was made and none is scored -- the sign of the "
            "frozen rule's verdict was declared unpredictable in advance"))
    for k, v in exp_res.items():
        say("  %s: %s" % (k, json.dumps(v) if isinstance(v, dict) else v))
    t2["expectations_scored"] = exp_res
    t2["status"] = "completed_valid"
    res["T2"] = t2
    res["status"] = "completed_valid"


if __name__ == "__main__":
    main()
