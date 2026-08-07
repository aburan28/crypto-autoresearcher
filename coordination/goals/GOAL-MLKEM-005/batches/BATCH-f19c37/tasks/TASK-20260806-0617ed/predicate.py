#!/usr/bin/env python3
"""
TASK-20260806-0617ed / BATCH-f19c37 / GOAL-MLKEM-005
AM-2 of DEC-20260806-00deff: construct an adjudication predicate and DEMONSTRATE,
on already-committed BATCH-436ddd / BATCH-a51f91 data, that it returns DIFFERENT
verdicts on the Haar null arm and the real arm in at least one cell.

CLAIM TIER: TOY.  Nothing computed here supports any statement about ML-KEM
security or about any FIPS 203 parameter set.  Every frame is at d <= 140,
beta <= 60, q = 3329, k = d/2.

WHAT THIS SCRIPT DOES NOT DO
  * It draws NO error vectors.  Zero.  The statistic is a deterministic scalar
    of the tail frame, so the entire 2^20-draw measurement layer of the
    incumbent instrument is not merely reduced, it is absent.
  * It creates NO new lattices, NO new arms and NO new seeds.  Every frame is
    regenerated bit-exactly from the seed scheme committed in
    b2a_results.json:seed_scheme, and the regeneration is verified against the
    committed per-basis diagnostics before any predicate number is computed.
  * It fits NO parameter.  See the spec below.

Invocation used for the recorded run is in predicate_report.md.  fpylll is
imported from a path given by the environment variable AUTORESEARCH_EXTRA_PYTHONPATH
when set, so the committed script hard-codes no machine-local path.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import time
from concurrent.futures import ProcessPoolExecutor

_EXTRA = os.environ.get("AUTORESEARCH_EXTRA_PYTHONPATH")
if _EXTRA:
    for _p in _EXTRA.split(os.pathsep):
        if _p:
            sys.path.insert(0, _p)

import numpy as np

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(TASK_DIR, *([".."] * 7)))
B2A_RESULTS = os.path.join(
    REPO, "coordination", "goals", "GOAL-MLKEM-005", "batches", "BATCH-436ddd",
    "tasks", "TASK-20260806-09ec68", "b2a_results.json")

# ===================================================================== frozen
SPEC_MD = r"""
## P3 -- the adjudication predicate, specified before it is run

### 1. The statistic

For a `d x beta` orthonormal tail frame `Q`, write `P = Q Q^T` and

```
V(Q) = sum_{a=1}^{d} ( P_aa - beta/d )^2
```

`V` is a DETERMINISTIC scalar of the frame.  It requires no error draws, no
quantile estimation and no Monte Carlo.  `trace(P) = beta` is forced, so `V` is
the sum of squared deviations of the diagonal of `P` from a mean it cannot
avoid; `V` is the second central moment of the coordinate-participation profile,
scaled by `d`.

### 2. Why THIS statistic, and not one chosen because it happened to separate

Three facts, all exact, none fitted.

**(a) `V` is the exact null-mean-known quantity.**  For a Haar-random rank-`beta`
subspace of `R^d`, `P_aa ~ Beta(beta/2, (d-beta)/2)` marginally, so

```
mu_0(d,beta) = E_Haar[V] = 2 * beta * (d - beta) / ( d * (d + 2) )      EXACT
```

There is no reference arm to draw and no constant to fit.

**(b) `V` exhausts the second-order content of `P`.**  The error law the goal
measures against (CBD_{eta=2}) is iid across coordinates and sign-symmetric, so
any admissible statistic is a function of `P` invariant under signed permutation
of coordinates -- a rotation-invariant function of `Q` alone is constant and
therefore useless.  At second order in the entries of `P` there are exactly two
signed-permutation invariants, `sum_a P_aa^2` and `sum_{a!=b} P_ab^2`, and they
are not independent:

```
sum_{a,b} P_ab^2 = trace(P^2) = beta        (P is a projector)
=> sum_{a!=b} P_ab^2 = beta - sum_a P_aa^2 = beta - beta^2/d - V
```

The off-diagonal energy is an AFFINE FUNCTION of `V` with no freedom.  `V` is
therefore not one statistic among many at this order; it is the only one.

**(c) `V` is the exact sufficient statistic for the incumbent instrument's own
signal.**  For iid coordinates of unit variance and fourth moment `mu_4`, and
any symmetric `A`, `Var(e^T A e) = (mu_4 - 3) sum_a A_aa^2 + 2 trace(A^2)`.
With `A = P`,

```
Var(e^T P e) = 2*beta + (mu_4 - 3) * ( V + beta^2/d )
```

`beta`, `d` and `mu_4` are fixed by the cell, so the ONLY frame-dependent term
is `V`.  The incumbent `T2` statistic `R = ||Q^T e||^2 / ||e||^2` is a
`2^20`-sample estimator of a tail quantile whose leading frame dependence is
this variance.  `T2` estimates `V` noisily; `P3` computes it.

### 3. The verdict rule

Fix `n` frames of an arm `A`.  Compute `V_i` for each, then

```
Vbar_A = mean_i V_i
s_A    = sd_i V_i          (ddof = 1)
SE_A   = s_A / sqrt(n)
z_A    = ( Vbar_A - mu_0(d,beta) ) / SE_A
```

* **DEPARTURE** when `z_A >= GATE_K`.
* **AGREEMENT_UPPER_BOUND** otherwise.  The verdict is then reported as an
  UPPER BOUND and never as an absence:
  `excess_A <= (Vbar_A - mu_0) + GATE_K * SE_A`, and the arm is described as
  "no departure resolved above a floor of `FLOOR_A`", never as "no departure".

`GATE_K = 4.0`.  This constant is INHERITED VERBATIM from the incumbent
instrument frozen by DEC-20260805-4823db (`b2a.py:GATE_K = 4.0`).  It was not
chosen by this task and is not tuned to this data.  `mu_0` is a theorem.  There
is no other parameter.

The rule is ONE-SIDED (`z >= GATE_K`, not `|z|`).  Coordinate confinement can
only raise the dispersion of the participation profile above the Haar value; a
significantly NEGATIVE `z` is an instrument fault, not a finding, and is
reported as `ANOMALY_BELOW_NULL`.

### 4. The detection floor, declared in the statistic's own units

```
FLOOR_A = GATE_K * SE_A = 4 * s_A / sqrt(n)          [units of V]
```

`FLOOR_A` is reported for EVERY arm, positive verdict or negative.  Every
AGREEMENT verdict this predicate emits is an upper bound at `FLOOR_A` and is
labelled as such in `separation.json` and in the report.  This is the field
DEC-20260806-00deff makes mandatory, and it is why the incumbent's "absent below
gate" is not a sentence this predicate can produce.

The floor scales as `1/sqrt(n)` and is a property of the arm's own between-frame
dispersion, not of the predicate.  At `n = 8` committed frames the realized
floors are reported per cell in `separation.json`.

### 5. The separation demonstration required by AM-2

For the Haar null arm `H` and any real-lattice arm `A` in the same cell,

```
SE_diff = sqrt( SE_A^2 + SE_H^2 )
z_diff  = ( Vbar_A - Vbar_H ) / SE_diff
```

AM-2 is met if `verdict(A) != verdict(H)` in at least one cell, with `z_diff`
reported.  The Haar arm is NOT needed by the predicate itself -- `mu_0` is
exact -- so its role here is (i) the AM-2 comparison and (ii) an implementation
check: `Vbar_H` must agree with `mu_0`.

### 6. Two out-of-sample anchors, both with values fixed before measurement

* **Exact point prediction.**  A frame that is a coordinate selector onto a
  `beta`-subset has `P_aa in {0,1}` and therefore
  `V_aligned(d,beta) = beta * (1 - beta/d)` EXACTLY.  The graded family at
  `t = 0` is that frame.  Predicted `V` at `(100,30)` is `21.000000`, at
  `(100,40)` `24.000000`, at `(140,30)` `23.571429`, at `(140,40)` `28.571429`.
  A predicate whose statistic is what it claims must reproduce these to
  floating-point precision.  This is a falsification test, not a fit.
* **Independent-seed null.**  The graded family at `t = 1` is a Haar frame drawn
  from the `seed_graded` family, which is DISJOINT from the `seed_haar` family
  the demonstration uses.  `P3` must return AGREEMENT there.  These frames were
  not used to construct anything in this task.

### 7. What P3 cannot do, stated now rather than after

`P3` sees the coordinate-participation profile and nothing else.  A tail frame
whose relationship to the coordinate basis is Haar-like in `V` but structured in
some other invariant -- a third-order diagonal moment, an off-diagonal pattern
of fixed total energy, alignment with a secret direction -- is INVISIBLE to
`P3` at any `n`.  An `AGREEMENT` verdict from `P3` is a statement about `V` at
the stated floor.  It is not a statement that the frame is Haar.
"""

SPEC_SHA256 = hashlib.sha256(SPEC_MD.encode("utf-8")).hexdigest()

# ============================================================ frozen constants
Q_MOD = 3329
CELLS = [(100, 30), (100, 40), (140, 30), (140, 40)]
BETA_MAX = 60
GATE_K = 4.0
N_DRAW = 8
GRADED_T = [0.0, 1.0]          # the two out-of-sample anchors of spec section 6
EXTRA_WINDOWS = [50, 60]       # free tail windows on frames already produced


# ==================================================================== seeds
# Identical to b2a_results.json:seed_scheme (BATCH-436ddd), which is itself
# identical to BATCH-a51f91 for basis and Haar.
def seed_basis(d, beta, i):
    return 700000 + d * 1000 + beta * 10 + i


def seed_haar(d, beta, j):
    return 900000 + d * 1000 + beta * 10 + j


def seed_graded(d, beta, j):
    return 500000 + d * 1000 + beta * 10 + j


# ================================================================= statistic
def v_stat(Q):
    """V = sum_a (P_aa - beta/d)^2 for P = Q Q^T.  Q is d x beta, orthonormal."""
    Q = np.asarray(Q, dtype=np.float64)
    d, beta = Q.shape
    diag = np.einsum("ij,ij->i", Q, Q)          # P_aa without forming P
    return float(np.sum((diag - beta / d) ** 2))


def mu0(d, beta):
    """EXACT Haar expectation of V."""
    return 2.0 * beta * (d - beta) / (d * (d + 2.0))


def v_aligned(d, beta):
    """EXACT V of a coordinate-selector frame onto beta distinct coordinates."""
    return beta * (1.0 - beta / d)


def adjudicate(vs, d, beta, gate_k=GATE_K):
    """P3 applied to one arm.  `vs` is the list of per-frame V values."""
    v = np.asarray(vs, dtype=np.float64)
    n = v.size
    m = float(v.mean())
    s = float(v.std(ddof=1))
    se = s / np.sqrt(n)
    m0 = mu0(d, beta)
    z = (m - m0) / se if se > 0 else float("inf")
    floor = gate_k * se
    if z >= gate_k:
        verdict = "DEPARTURE"
    elif z <= -gate_k:
        verdict = "ANOMALY_BELOW_NULL"
    else:
        verdict = "AGREEMENT_UPPER_BOUND"
    out = {
        "n_frames": int(n),
        "V_mean": m,
        "V_sd": s,
        "V_se": se,
        "mu0_haar_exact": m0,
        "excess_over_mu0": m - m0,
        "z_vs_exact_null": z,
        "gate_k": gate_k,
        "detection_floor_V_units": floor,
        "verdict": verdict,
        "frames_with_positive_excess": int(np.sum(v > m0)),
        "V_per_frame": [float(x) for x in v],
    }
    if verdict == "AGREEMENT_UPPER_BOUND":
        out["upper_bound_on_excess_V_units"] = (m - m0) + floor
        out["reported_as"] = (
            "no departure resolved above a floor of %.6f V-units; this is an "
            "UPPER BOUND, not an absence" % floor)
    return out


def separation(arm_a, arm_h):
    """AM-2 separation of two arms, in SE of the difference."""
    diff = arm_a["V_mean"] - arm_h["V_mean"]
    se = float(np.sqrt(arm_a["V_se"] ** 2 + arm_h["V_se"] ** 2))
    return {
        "delta_V": diff,
        "SE_of_difference": se,
        "separation_in_SE": diff / se if se > 0 else float("inf"),
        "verdict_arm": arm_a["verdict"],
        "verdict_haar_null": arm_h["verdict"],
        "verdicts_differ": arm_a["verdict"] != arm_h["verdict"],
    }


# ================================================== frame regeneration (seeds)
def reduce_one(job):
    """Regenerate one committed basis and return its three tail frames.

    Byte-identical construction path to b2a.py:reduce_one.  Frames are kept in
    float64 here (b2a stored float32); V is O(1) and the cast is irrelevant, but
    the difference is reported rather than assumed.
    """
    d, beta, i = job
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from fpylll import IntegerMatrix, LLL, GSO, BKZ, FPLLL
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz2 import BKZReduction

    tag = "d%d_b%d_i%d" % (d, beta, i)
    s = seed_basis(d, beta, i)
    FPLLL.set_random_seed(s)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)

    def to_np(M):
        return np.array([[M[r, c] for c in range(d)] for r in range(d)],
                        dtype=np.float64)

    def tail(M):
        Qf, Rm = np.linalg.qr(to_np(M).T)
        return (np.ascontiguousarray(Qf[:, d - BETA_MAX:], dtype=np.float64),
                np.abs(np.diag(Rm)))

    Q_raw, gs_raw = tail(A)
    t0 = time.time()
    LLL.reduction(A)
    t1 = time.time()
    Q_lll, gs_lll = tail(A)
    strategies = [Strategy(b) for b in range(beta + 1)]
    par = BKZ.Param(block_size=beta, strategies=strategies,
                    max_loops=2, flags=BKZ.MAX_LOOPS)
    BKZReduction(A)(par)
    t2 = time.time()
    Q_bkz, gs_bkz = tail(A)

    lg = np.log2(gs_bkz)
    meta = {
        "tag": tag, "d": d, "beta": beta, "basis_index": i, "fplll_seed": s,
        "lll_seconds": round(t1 - t0, 3), "bkz_seconds": round(t2 - t1, 3),
        "b0_norm": float(gs_bkz[0]),
        "b0_norm_raw": float(gs_raw[0]),
        "b0_norm_lll": float(gs_lll[0]),
        "gso_log2_slope_per_index": float(np.polyfit(np.arange(d), lg, 1)[0]),
        "gso_log2_slope_lll": float(np.polyfit(np.arange(d), np.log2(gs_lll), 1)[0]),
        "gso_log2_slope_raw": float(np.polyfit(np.arange(d), np.log2(gs_raw), 1)[0]),
        "Q_orthonormality_max_abs_dev": float(np.max(np.abs(
            Q_bkz.T @ Q_bkz - np.eye(BETA_MAX)))),
    }
    return tag, Q_raw, Q_lll, Q_bkz, meta


def haar_frame(d, betap, j):
    g = np.random.default_rng(seed_haar(d, betap, j))
    return np.linalg.qr(g.standard_normal((d, betap)))[0]


def graded_frame(d, betap, j, t):
    g = np.random.default_rng(seed_graded(d, betap, j))
    S = g.choice(d, size=betap, replace=False)
    G = g.standard_normal((d, betap))
    E = np.zeros((d, betap))
    E[S, np.arange(betap)] = 1.0
    return np.linalg.qr(np.sqrt(1.0 - t) * E + np.sqrt(t) * G)[0]


def tail_slice(Qfull, betap):
    return np.ascontiguousarray(Qfull[:, BETA_MAX - betap:])


def cpu_seconds():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


# ======================================================================= main
def calibrate(cells, n_ref=4000, n_boot=20000, seed=20260806):
    """NULL CALIBRATION -- not part of the AM-2 demonstration.

    Added to this file AFTER the recorded run of `main()`, in response to a
    Haar arm reaching z = +3.98 against the gate of 4.0 in the held-out window
    sweep.  It touches no frozen constant, no statistic and no verdict rule;
    SPEC_SHA256 is unchanged and `separation.json` is not regenerated.

    It samples the predicate's OWN NULL -- Haar frames, a mathematical object.
    No lattice, no committed record and no research datum enters here, and
    deleting this function changes no verdict in `separation.json`.
    """
    rng = np.random.default_rng(seed)
    rows = {}
    for (d, beta) in cells:
        vs = np.array([v_stat(np.linalg.qr(rng.standard_normal((d, beta)))[0])
                       for _ in range(n_ref)])
        idx = rng.integers(0, n_ref, size=(n_boot, N_DRAW))
        blk = vs[idx]
        z = (blk.mean(1) - mu0(d, beta)) / (blk.std(1, ddof=1) / np.sqrt(N_DRAW))
        rows["d%d_b%d" % (d, beta)] = {
            "mu0_exact": mu0(d, beta),
            "null_mean_%d_frames" % n_ref: float(vs.mean()),
            "null_mean_se": float(vs.std(ddof=1) / np.sqrt(n_ref)),
            "null_sd_of_V": float(vs.std(ddof=1)),
            "n8_sample_se_gate_false_positive_rate_one_sided": float((z >= GATE_K).mean()),
            "n8_z_sd": float(z.std()),
        }
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(TASK_DIR, "separation.json"))
    ap.add_argument("--spec-only", action="store_true")
    ap.add_argument("--calibrate", action="store_true",
                    help="null calibration only; writes nothing")
    args = ap.parse_args()

    # The spec hash is emitted BEFORE any research number is computed.
    print("P3 spec sha256: %s" % SPEC_SHA256, flush=True)
    if args.spec_only:
        print(SPEC_MD)
        return
    if args.calibrate:
        print(json.dumps(calibrate(CELLS + [(100, 50), (100, 60),
                                            (140, 50), (140, 60)]), indent=1))
        return

    t_start = time.time()
    c_start = cpu_seconds()

    out = {
        "task_id": "TASK-20260806-0617ed",
        "batch_id": "BATCH-f19c37",
        "goal_id": "GOAL-MLKEM-005",
        "governed_by": "DEC-20260806-00deff AM-2",
        "claim_tier": "TOY",
        "spec_sha256": SPEC_SHA256,
        "spec_text": SPEC_MD,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "error_draws_used": 0,
        "new_seeds_introduced": 0,
        "data_provenance": (
            "Every frame regenerated bit-exactly from the seed scheme committed "
            "in BATCH-436ddd/tasks/TASK-20260806-09ec68/b2a_results.json:seed_scheme "
            "(itself identical to BATCH-a51f91 for basis and Haar seeds). No new "
            "lattice, no new arm, no new seed, no error draw."),
    }

    # ---------------------------------------------------------------- verify
    with open(B2A_RESULTS) as fh:
        committed = json.load(fh)
    out["committed_source_sha256"] = hashlib.sha256(
        open(B2A_RESULTS, "rb").read()).hexdigest()
    out["committed_seed_scheme"] = committed["seed_scheme"]

    jobs = [(d, b, i) for (d, b) in CELLS for i in range(N_DRAW)]
    frames = {}
    metas = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for tag, qr, ql, qb, meta in ex.map(reduce_one, jobs):
            frames[tag] = (qr, ql, qb)
            metas[tag] = meta
    t_red_wall = time.time() - t_start
    c_red = cpu_seconds() - c_start

    cm = {r["tag"]: r for r in committed["reductions"]}
    checks = []
    worst = 0.0
    for tag, meta in sorted(metas.items()):
        ref = cm[tag]
        row = {"tag": tag}
        for f in ("b0_norm_raw", "b0_norm_lll", "b0_norm",
                  "gso_log2_slope_raw", "gso_log2_slope_lll",
                  "gso_log2_slope_per_index"):
            rel = abs(meta[f] - ref[f]) / max(abs(ref[f]), 1e-300)
            row[f + "_rel_dev"] = rel
            worst = max(worst, rel)
        row["Q_orthonormality_max_abs_dev"] = meta["Q_orthonormality_max_abs_dev"]
        checks.append(row)
    out["regeneration_check"] = {
        "bases_checked": len(checks),
        "fields_per_basis": 6,
        "max_relative_deviation_vs_committed": worst,
        "verified": bool(worst < 1e-12),
        "per_basis": checks,
    }
    if not out["regeneration_check"]["verified"]:
        out["ABORT"] = ("Regenerated bases do not match the committed diagnostics; "
                        "the demonstration would not be on committed data.")
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
        print("ABORT: regeneration mismatch, worst rel dev %.3e" % worst)
        return
    print("regeneration verified, worst rel dev %.3e" % worst, flush=True)

    # ------------------------------------------------------------ statistics
    cells_out = {}
    for (d, beta) in CELLS:
        key = "d%d_b%d" % (d, beta)
        arms = {}

        def collect(name, mats, bp):
            arms[name] = adjudicate([v_stat(m) for m in mats], d, bp)

        raw = [frames["d%d_b%d_i%d" % (d, beta, i)][0] for i in range(N_DRAW)]
        lll = [frames["d%d_b%d_i%d" % (d, beta, i)][1] for i in range(N_DRAW)]
        bkz = [frames["d%d_b%d_i%d" % (d, beta, i)][2] for i in range(N_DRAW)]

        collect("unreduced", [tail_slice(m, beta) for m in raw], beta)
        collect("lll_only", [tail_slice(m, beta) for m in lll], beta)
        collect("real_bkz", [tail_slice(m, beta) for m in bkz], beta)
        collect("haar_null", [haar_frame(d, beta, j) for j in range(N_DRAW)], beta)
        for t in GRADED_T:
            collect("graded_t%.2f" % t,
                    [graded_frame(d, beta, j, t) for j in range(N_DRAW)], beta)

        # float32 sensitivity: b2a stored frames as float32.
        f32 = [v_stat(np.asarray(tail_slice(m, beta), dtype=np.float32))
               for m in lll]
        f64 = [v_stat(tail_slice(m, beta)) for m in lll]
        cast_dev = float(np.max(np.abs(np.array(f32) - np.array(f64))
                                / np.array(f64)))

        seps = {}
        for a in ("unreduced", "lll_only", "real_bkz",
                  "graded_t0.00", "graded_t1.00"):
            seps[a + "_vs_haar_null"] = separation(arms[a], arms["haar_null"])

        cells_out[key] = {
            "d": d, "beta": beta, "k": d // 2, "q": Q_MOD,
            "mu0_haar_exact": mu0(d, beta),
            "V_aligned_exact_prediction": v_aligned(d, beta),
            "V_aligned_measured_graded_t0": arms["graded_t0.00"]["V_mean"],
            "V_aligned_max_abs_error": float(np.max(np.abs(
                np.array(arms["graded_t0.00"]["V_per_frame"])
                - v_aligned(d, beta)))),
            "haar_null_mean_vs_mu0_abs_error": abs(
                arms["haar_null"]["V_mean"] - mu0(d, beta)),
            "float32_cast_max_rel_dev_on_V": cast_dev,
            "arms": arms,
            "separations_vs_haar_null": seps,
        }
        print("%s done" % key, flush=True)

    out["cells"] = cells_out

    # ------------------------------------------- held-out tail-window sweep
    # Free: reduce_one retains BETA_MAX = 60 GSO columns, so windows at
    # betap in {50,60} are available on frames already produced.  These
    # (arm, betap) combinations were not used to set anything.
    sweep = {}
    for (d, beta) in CELLS:
        for bp in EXTRA_WINDOWS:
            if bp <= beta:
                continue
            key = "d%d_bkzblock%d_window%d" % (d, beta, bp)
            row = {}
            for idx, name in ((1, "lll_only"), (2, "real_bkz")):
                mats = [tail_slice(frames["d%d_b%d_i%d" % (d, beta, i)][idx], bp)
                        for i in range(N_DRAW)]
                row[name] = adjudicate([v_stat(m) for m in mats], d, bp)
            row["haar_null"] = adjudicate(
                [v_stat(haar_frame(d, bp, j)) for j in range(N_DRAW)], d, bp)
            row["seps"] = {n + "_vs_haar_null": separation(row[n], row["haar_null"])
                           for n in ("lll_only", "real_bkz")}
            sweep[key] = row
    out["held_out_window_sweep"] = sweep

    # ------------------------------------------------------------- summary
    am2 = []
    for key, c in cells_out.items():
        for name, s in c["separations_vs_haar_null"].items():
            if s["verdicts_differ"]:
                am2.append({"cell": key, "comparison": name,
                            "separation_in_SE": s["separation_in_SE"],
                            "verdict_arm": s["verdict_arm"],
                            "verdict_haar_null": s["verdict_haar_null"]})
    out["AM2_admissibility"] = {
        "requirement": ("different verdicts on the Haar null arm and the real arm "
                        "in at least one cell, separation stated in SE of the "
                        "difference, on already-committed data"),
        "cells_with_differing_verdicts": sorted(
            {a["cell"] for a in am2 if not a["comparison"].startswith("graded")}),
        "met": bool([a for a in am2 if not a["comparison"].startswith("graded")]),
        "all_differing_verdicts": am2,
    }
    out["detection_floors_V_units"] = {
        key: {n: c["arms"][n]["detection_floor_V_units"] for n in c["arms"]}
        for key, c in cells_out.items()}

    out["timings"] = {
        "reduction_wall_seconds": round(t_red_wall, 2),
        "reduction_cpu_core_seconds": round(c_red, 2),
        "total_wall_seconds": round(time.time() - t_start, 2),
        "total_cpu_core_seconds": round(cpu_seconds() - c_start, 2),
    }
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["peak_rss_gb"] = round(
        (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
         + resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss) / 1048576.0, 3)
    out["environment"] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
    }
    try:
        import fpylll
        out["environment"]["fpylll"] = fpylll.__version__
    except Exception:
        pass

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote %s" % args.out)
    print("AM-2 met: %s  cells: %s" % (out["AM2_admissibility"]["met"],
                                       out["AM2_admissibility"]["cells_with_differing_verdicts"]))
    print("timings: %s" % out["timings"])


if __name__ == "__main__":
    main()
