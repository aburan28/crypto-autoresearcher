#!/usr/bin/env python3
"""
recalibrate.py -- TASK-20260806-6086cb (executor), GOAL-HQC-001, BATCH-0a65c0.

Repairs VF-1 and VF-3 of validation_report TASK-20260806-301f68 against
amendment_v2.yaml (TASK-20260806-dbadc8), for the proposed v3 amendment to
EXP-HQC-982268.

CLAIM TIER: TOY.  This program constructs NO HQC object.  It runs NO
measurement arm.  It computes NO log2_A_k on any space-(T) arm.  Every draw
below is from S ~ Binomial(n_e, q) under an explicitly declared null (or an
explicitly declared alternative, used only to measure power), with q taken
from the Stage-A (T)-arm first-moment diagnostic q_hat already published in
RUN-HQC-982268-STAGEA-a.  The only (T) inputs are first moments.

------------------------------------------------------------------------
WHY THIS FILE ALSO WRITES amendment_v3.yaml
------------------------------------------------------------------------
VF-1 was not a calibration error.  The calibration in amendment_v2.yaml was
correct and independently replicated.  The defect was that a HUMAN COPIED THE
CONSTANTS INTO THE YAML AT FIVE DECIMAL PLACES, truncating 4.8%-8.6% off
half-widths of order 1e-5 bits, so the artifact that governs execution
realized 0.610 / 0.419 / 0.551 percent size at k=2 against its own
[0.002, 0.004] gate.

The structural fix is therefore not "use more decimals".  It is: NO HUMAN
EVER TYPES A CONSTANT.  This program

  (1) computes the constants,
  (2) WRITES them into amendment_v3.yaml itself, in shortest-round-trip
      decimal form, through a formatter that is asserted to round-trip,
  (3) RE-READS amendment_v3.yaml with yaml.safe_load and asserts the parsed
      values are bit-identical floats (not strings -- see note below), and
  (4) measures the realized size of the values IT READ BACK OUT OF THE FILE,
      never of the values it holds in memory.

Note on (3), found while building this: PyYAML resolves `1e-05` as a
*string*, not a float, because its float regex requires a decimal point and a
signed exponent.  A constant emitted as `1e-05` would therefore have been
silently loaded as text.  That is a second, independent instance of the same
defect class as VF-1 and it is guarded by an explicit type assertion.

------------------------------------------------------------------------
PHASES
------------------------------------------------------------------------
  selftest   estimator vs exact rational arithmetic; YAML round-trip guards
  calibrate  derive frozen intervals; INJECT them into amendment_v3.yaml
  qsens      q-hat plug-in sensitivity at EVERY reported k (VF-3); INJECT
  measure    RE-READ amendment_v3.yaml; measure size of the read-back
             constants; write transcribed_size.json
  battery    reproduce the red team's near-null law (RT2-OBJ-1) and measure
             what a multi-k battery does to it
  idxmap     CTRL-IDXMAP demonstration: a control whose invariance is
             FUNCTIONAL rather than distributional, on a toy ring

Usage:  python3 recalibrate.py all
        python3 recalibrate.py <phase> [<phase> ...]
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import sys
import tempfile
import time
from fractions import Fraction

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
AMENDMENT = os.path.join(HERE, "amendment_v3.yaml")
TRANSCRIBED = os.path.join(HERE, "transcribed_size.json")
# Scratch for cached phase results. Deliberately OUTSIDE the task directory: the four
# deliverables are the only files this task writes there, so the Coordinator's snapshot
# commit stages exactly its declared artifact_paths. Override with RECAL_WORK.
WORK = os.environ.get("RECAL_WORK",
                      os.path.join(tempfile.gettempdir(),
                                   "recalibrate-TASK-20260806-6086cb"))

# ---------------------------------------------------------------------------
# FROZEN PROCEDURE CONSTANTS.  These define the rule.  Changing any of them
# changes the rule and requires a new amendment version.
# ---------------------------------------------------------------------------
SEED_NAMESPACE = "EXP-HQC-982268/v3/INV-NULL"
NOMINAL_ALPHA = 0.0026997960632601866   # = 2*Phi(-3), inherited from v2
N_CAL = 2_000_000
N_VAL = 1_000_000
N_SENS = 400_000
CHUNK = 100_000
ACCEPT_LO, ACCEPT_HI = 0.002, 0.004     # the amendment's own acceptance gate
UNDEFINED_MAX = 0.10                    # >10% undefined => NOT REACHED
T_STAB_THRESHOLD = 30                   # contract's own constant

# ---------------------------------------------------------------------------
# Parameter sets.  n_e from experiments/EXP-HQC-982268/specification.yaml.
# q_hat from RUN-HQC-982268-STAGEA-a (T)-arm first-moment diagnostic, as
# republished in amendment_v2.yaml.  block_failures likewise (first moment).
# ---------------------------------------------------------------------------
SETS = {
    "PS-A":  dict(n_e=46, m=16, q_hat=0.0003344494275569857,  block_failures=8122),
    "PS-R1": dict(n_e=46, m=16, q_hat=0.19742737095129637,    block_failures=5200049),
    "PS-R3": dict(n_e=56, m=17, q_hat=0.31994628619715665,    block_failures=9159668),
    "PS-R5": dict(n_e=90, m=30, q_hat=0.4141203546692593,     block_failures=13187613),
}

# (set, allocation label, T).  PS-R3@1e7 is the allocation the campaign funds.
ALLOCATIONS = [
    ("PS-A",  "1e8", 100_000_000),
    ("PS-R1", "1e8", 100_000_000),
    ("PS-R3", "1e7",  10_000_000),
    ("PS-R3", "2e7",  20_000_000),
    ("PS-R5", "2e7",  20_000_000),
]

# k values retained from amendment_v2.yaml's frozen table even where they are
# above k_max, so that v2's rows all have a v3 counterpart.
V2_RETAINED_K = {
    ("PS-A", "1e8"):  [2, 3, 4, 16],
    ("PS-R1", "1e8"): [2, 6, 9, 11, 14, 16, 18],
    ("PS-R3", "2e7"): [2, 10, 17, 22, 25],
    ("PS-R5", "2e7"): [2, 15, 30, 35],
    ("PS-R3", "1e7"): [],
}

MARK_BEGIN = "# BEGIN MACHINE-GENERATED {name} -- DO NOT EDIT BY HAND"
MARK_END = "# END MACHINE-GENERATED {name}"


# ===========================================================================
# YAML emission with a round-trip guarantee
# ===========================================================================
def yf(x) -> str:
    """Shortest decimal string that round-trips to x AND parses as a YAML float.

    PyYAML's float resolver needs a decimal point in the mantissa, so
    repr(1e-05) == '1e-05' would load as a *string*.  Every emitted number
    goes through here and the round-trip is asserted, not assumed.
    """
    x = float(x)
    if math.isnan(x):
        return ".nan"
    if math.isinf(x):
        return ".inf" if x > 0 else "-.inf"
    s = repr(x)
    if "e" in s or "E" in s:
        mant, exp = re.split("[eE]", s)
        if "." not in mant:
            mant += ".0"
        s = mant + "e" + exp
    elif "." not in s:
        s += ".0"
    assert float(s) == x, (s, x)
    loaded = yaml.safe_load("v: " + s)["v"]
    assert isinstance(loaded, float) and loaded == x, ("YAML round-trip failed", s, x)
    return s


def inject(name: str, body: str) -> None:
    """Replace the marked block in amendment_v3.yaml with `body`."""
    with open(AMENDMENT) as fh:
        text = fh.read()
    b = MARK_BEGIN.format(name=name)
    e = MARK_END.format(name=name)
    i, j = text.find(b), text.find(e)
    if i < 0 or j < 0:
        raise SystemExit("markers for %r not found in amendment_v3.yaml" % name)
    indent = " " * (len(text[:i].split("\n")[-1]))
    body = "\n".join((indent + ln) if ln.strip() else ln
                     for ln in body.rstrip("\n").split("\n"))
    new = text[: i + len(b)] + "\n" + body + "\n" + indent + text[j:]
    with open(AMENDMENT, "w") as fh:
        fh.write(new)
    yaml.safe_load(open(AMENDMENT))  # must still parse


# ===========================================================================
# Estimator, written from the definition in EXP-HQC-982268
#   log2 A_k = log2( mubar_k / q^k ),  mubar_k = E[C(S,k)] / C(n_e,k)
# estimated on a histogram H over s = 0..n_e of T trials:
#   mubar_hat_k = (sum_s C(s,k) H_s) / (T C(n_e,k)),  q_hat = (sum_s s H_s)/(T n_e)
# ===========================================================================
def cmatrix(n_e: int, ks) -> np.ndarray:
    return np.array([[float(math.comb(s, k)) for k in ks] for s in range(n_e + 1)])


def log2_A_vec(H: np.ndarray, n_e: int, ks, C: np.ndarray | None = None) -> np.ndarray:
    """H: (R, n_e+1) integer counts.  Returns (R, len(ks)); NaN where undefined."""
    ks = list(ks)
    if C is None:
        C = cmatrix(n_e, ks)
    Hf = H.astype(np.float64)
    T = Hf.sum(axis=1)
    ssum = Hf @ np.arange(n_e + 1, dtype=np.float64)
    q = ssum / (T * n_e)
    num = Hf @ C
    denom = T[:, None] * np.array([float(math.comb(n_e, k)) for k in ks])[None, :]
    mu = num / denom
    out = np.full(mu.shape, np.nan)
    good = (mu > 0) & (q[:, None] > 0)
    kk = np.array(ks, dtype=np.float64)[None, :]
    lq = np.log2(np.where(q > 0, q, 1.0))[:, None]
    out[good] = (np.log2(np.where(good, mu, 1.0)) - kk * lq)[good]
    return out


def log2_A_exact(hist, n_e: int, k: int):
    """Exact rational reference; returns a float via Fraction -> log2."""
    T = sum(int(h) for h in hist)
    ssum = sum(int(h) * s for s, h in enumerate(hist))
    if T == 0 or ssum == 0:
        return None
    num = sum(int(h) * math.comb(s, k) for s, h in enumerate(hist))
    if num == 0:
        return None
    mu = Fraction(num, T * math.comb(n_e, k))
    q = Fraction(ssum, T * n_e)
    val = mu / (q ** k)
    # log2 of an exact rational, at full double precision
    return math.log2(val.numerator) - math.log2(val.denominator)


# ===========================================================================
# Draws
# ===========================================================================
def binom_pmf(n_e: int, q: float) -> np.ndarray:
    p = np.array([math.comb(n_e, i) * (q ** i) * ((1.0 - q) ** (n_e - i))
                  for i in range(n_e + 1)], dtype=np.float64)
    return p / p.sum()


def seed_of(*parts) -> int:
    key = "|".join([SEED_NAMESPACE] + [str(p) for p in parts])
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def draw_stats(n_e, q, T, ks, n_rep, seed, C=None):
    """Yield log2 A_hat values for n_rep i.i.d. replicates, in chunks.

    The histogram of T i.i.d. Bin(n_e,q) trials over n_e+1 bins is EXACTLY
    Multinomial(T, pmf), so one replicate at T=1e8 costs one multinomial draw.
    Exact in distribution, O(1) in T.
    """
    pmf = binom_pmf(n_e, q)
    rng = np.random.Generator(np.random.PCG64(seed))
    if C is None:
        C = cmatrix(n_e, ks)
    done = 0
    while done < n_rep:
        c = min(CHUNK, n_rep - done)
        H = rng.multinomial(T, pmf, size=c)
        yield log2_A_vec(H, n_e, ks, C)
        done += c


def collect(n_e, q, T, ks, n_rep, seed, C=None) -> np.ndarray:
    return np.concatenate(list(draw_stats(n_e, q, T, ks, n_rep, seed, C)), axis=0)


# ===========================================================================
# The frozen interval, and the reachability arithmetic
# ===========================================================================
def frozen_interval(vals: np.ndarray):
    """Equal-tailed alpha/2 / 1-alpha/2 empirical quantiles by ORDER STATISTIC.

    Conservative and exactly reproducible: with R finite values sorted
    ascending, i = floor(alpha/2 * R), c_lo = x_(i), c_hi = x_(R-1-i).
    The rule fires on x < c_lo or x > c_hi (strict), so ties do not fire.
    """
    v = vals[np.isfinite(vals)]
    R = v.size
    if R < 1000:
        return None, None, R
    v = np.sort(v)
    i = int(math.floor(NOMINAL_ALPHA / 2.0 * R))
    return float(v[i]), float(v[R - 1 - i]), R


def t_stab(n_e: int, q: float, k: int):
    pmf = binom_pmf(n_e, q)
    ck = np.array([float(math.comb(s, k)) for s in range(n_e + 1)])
    E = float(pmf @ ck)
    if E <= 0:
        return math.inf, None
    c, s90 = 0.0, None
    for s in range(n_e + 1):
        c += pmf[s] * ck[s]
        if c >= 0.90 * E:
            s90 = s
            break
    tail = float(pmf[s90:].sum())
    return (30.0 / tail if tail > 0 else math.inf), s90


def k_max_of(n_e, q, T):
    kk = 2
    last = None
    while kk <= n_e:
        ts, _ = t_stab(n_e, q, kk)
        if ts <= T:
            last = kk
            kk += 1
        else:
            break
    return last


def se_rel_q(n_e, q, block_failures):
    """SE(q_hat)/q_hat under the rho=0 (independent-blocks) reference.

    Var(q_hat) = q(1-q)/(n_e T)  and  q_hat = failures/(n_e T), so
    SE/q = sqrt((1-q)/failures).  This is the rho = 0 VALUE, not an upper
    bound: under the positive block correlation this experiment exists to
    detect it is a LOWER bound (validator TASK-20260806-301f68, note on the
    producer's SE wording).  Recorded as such.
    """
    return math.sqrt((1.0 - q) / block_failures)


# ===========================================================================
# PHASE: selftest
# ===========================================================================
def phase_selftest(state):
    t0 = time.time()
    rng = np.random.Generator(np.random.PCG64(seed_of("selftest")))
    worst = 0.0
    n_cmp = 0
    for (sid, alab, T) in ALLOCATIONS:
        n_e = SETS[sid]["n_e"]
        q = SETS[sid]["q_hat"]
        ks = [2, 3, 5, 10, min(17, n_e - 1)]
        H = rng.multinomial(min(T, 2_000_000), binom_pmf(n_e, q), size=6)
        got = log2_A_vec(H, n_e, ks)
        for r in range(H.shape[0]):
            for j, k in enumerate(ks):
                ex = log2_A_exact(H[r], n_e, k)
                if ex is None:
                    assert not np.isfinite(got[r, j])
                    continue
                worst = max(worst, abs(got[r, j] - ex))
                n_cmp += 1
    # YAML emission guards, including the 1e-05 trap
    for probe in [1e-5, -1e-5, 5.4733708512544674e-05, 0.0, -0.6961505468518873,
                  1.0, 123456.0, 2.2250738585072014e-308]:
        s = yf(probe)
        assert yaml.safe_load("v: " + s)["v"] == probe
        assert isinstance(yaml.safe_load("v: " + s)["v"], float)
    assert isinstance(yaml.safe_load("v: 1e-05")["v"], str), \
        "expected PyYAML to mis-resolve a dotless exponent; guard is now stale"
    state["selftest"] = dict(
        max_abs_diff_vs_exact_rational_bits=worst,
        comparisons=n_cmp,
        yaml_roundtrip_guard="PASS",
        pyyaml_dotless_exponent_resolves_as_string=True,
        core_seconds=time.time() - t0,
    )
    print("[selftest] max |vectorised - exact rational| = %.3g bits over %d comparisons"
          % (worst, n_cmp))
    print("[selftest] YAML round-trip guard PASS; PyYAML resolves '1e-05' as %s"
          % type(yaml.safe_load("v: 1e-05")["v"]).__name__)


# ===========================================================================
# PHASE: calibrate
# ===========================================================================
def phase_calibrate(state):
    t0 = time.time()
    out_cfg = []
    for (sid, alab, T) in ALLOCATIONS:
        S = SETS[sid]
        n_e, q, m = S["n_e"], S["q_hat"], S["m"]
        kmax = k_max_of(n_e, q, T)
        ks = sorted(set(list(range(2, (kmax or 1) + 1)) + V2_RETAINED_K[(sid, alab)]))
        ks = [k for k in ks if k <= n_e]
        C = cmatrix(n_e, ks)
        seed = seed_of(sid, alab, T, "cal", N_CAL)
        vals = collect(n_e, q, T, ks, N_CAL, seed, C)
        cells = []
        for j, k in enumerate(ks):
            v = vals[:, j]
            fin = int(np.isfinite(v).sum())
            und = 1.0 - fin / v.size
            c_lo, c_hi, R = frozen_interval(v)
            ts, s90 = t_stab(n_e, q, k)
            status = "REPORTED"
            reasons = []
            if c_lo is None:
                status = "NOT REACHED"
                reasons.append("fewer than 1000 finite calibration replicates")
            if und > UNDEFINED_MAX:
                status = "NOT REACHED"
                reasons.append("%.1f%% of null replicates undefined (>10%%)" % (100 * und))
            if ts > T:
                status = "NOT REACHED"
                reasons.append("T_stab(%d) = %.4g > T = %.4g (ST-4)" % (k, ts, T))
            fv = v[np.isfinite(v)]
            cells.append(dict(
                k=k, status=status, reason="; ".join(reasons) or None,
                c_lo=c_lo, c_hi=c_hi,
                undefined_fraction=und, finite_calibration_replicates=fin,
                null_mean=(float(fv.mean()) if fin else None),
                null_median=(float(np.median(fv)) if fin else None),
                null_sd=(float(fv.std(ddof=1)) if fin > 1 else None),
                T_stab=ts, s_90=s90, is_k_equals_m=(k == m),
            ))
        out_cfg.append(dict(set=sid, allocation=alab, n_e=n_e, m=m, q_hat=q, T=T,
                            k_max_at_T=kmax, calibration_seed=seed, cells=cells))
        print("[calibrate] %-6s T=%-4s k_max=%s  cells=%d  (%.0fs)"
              % (sid, alab, kmax, len(cells), time.time() - t0))
    state["calibrate"] = dict(configurations=out_cfg, core_seconds=time.time() - t0)
    inject("FROZEN-INTERVALS", render_frozen(out_cfg))
    # re-read and assert bit-identity of everything just written
    back = load_frozen()
    nbad = 0
    for cfg in out_cfg:
        got = back[(cfg["set"], cfg["allocation"])]
        for cell in cfg["cells"]:
            if cell["c_lo"] is None:
                continue
            g = got["cells"][cell["k"]]
            for f in ("c_lo", "c_hi"):
                if not (isinstance(g[f], float) and g[f] == cell[f]):
                    nbad += 1
    assert nbad == 0, "%d constants did not round-trip through amendment_v3.yaml" % nbad
    print("[calibrate] injected + re-read: all constants round-trip bit-identically")


def render_frozen(cfgs) -> str:
    L = []
    ind = ""
    L.append(ind + "generated_by: recalibrate.py phase 'calibrate'")
    L.append(ind + "seed_namespace: '%s'" % SEED_NAMESPACE)
    L.append(ind + "n_calibration_replicates: %d" % N_CAL)
    L.append(ind + "nominal_size: %s" % yf(NOMINAL_ALPHA))
    L.append(ind + "configurations:")
    for c in cfgs:
        L.append(ind + "- set: %s" % c["set"])
        L.append(ind + "  allocation: '%s'" % c["allocation"])
        L.append(ind + "  n_e: %d" % c["n_e"])
        L.append(ind + "  m: %d" % c["m"])
        L.append(ind + "  q_hat: %s" % yf(c["q_hat"]))
        L.append(ind + "  T: %d" % c["T"])
        L.append(ind + "  k_max_at_T: %s" % (c["k_max_at_T"] if c["k_max_at_T"] else "null"))
        L.append(ind + "  calibration_seed: %d" % c["calibration_seed"])
        L.append(ind + "  cells:")
        for cell in c["cells"]:
            if cell["c_lo"] is None:
                L.append(ind + "  - {k: %d, status: '%s', reason: '%s', c_lo: null, c_hi: null}"
                         % (cell["k"], cell["status"], cell["reason"]))
                continue
            L.append(ind + "  - k: %d" % cell["k"])
            L.append(ind + "    c_lo: %s" % yf(cell["c_lo"]))
            L.append(ind + "    c_hi: %s" % yf(cell["c_hi"]))
            L.append(ind + "    status: '%s'" % cell["status"])
            if cell["reason"]:
                L.append(ind + "    reason: '%s'" % cell["reason"])
            L.append(ind + "    null_mean: %s" % yf(cell["null_mean"]))
            L.append(ind + "    null_median: %s" % yf(cell["null_median"]))
            L.append(ind + "    null_sd: %s" % yf(cell["null_sd"]))
            L.append(ind + "    undefined_fraction: %s" % yf(cell["undefined_fraction"]))
            L.append(ind + "    T_stab: %s" % yf(cell["T_stab"]))
            L.append(ind + "    s_90: %s" % (cell["s_90"] if cell["s_90"] is not None else "null"))
            if cell["is_k_equals_m"]:
                L.append(ind + "    note: 'k = m'")
    return "\n".join(L)


def load_frozen():
    """Load the frozen table BACK OUT of amendment_v3.yaml, with type guards."""
    doc = yaml.safe_load(open(AMENDMENT))
    blk = doc["protocol_amendment"]["R1_INV_NULL_v3"]["frozen_intervals"]
    out = {}
    for c in blk["configurations"]:
        for f in ("q_hat",):
            assert isinstance(c[f], float), ("%s parsed as %s, not float"
                                             % (f, type(c[f]).__name__))
        cells = {}
        for cell in c["cells"]:
            if cell.get("c_lo") is None:
                cells[cell["k"]] = cell
                continue
            for f in ("c_lo", "c_hi"):
                assert isinstance(cell[f], float), (
                    "%s at %s k=%s parsed as %s, not float -- TRANSCRIPTION FAILURE"
                    % (f, c["set"], cell["k"], type(cell[f]).__name__))
            cells[cell["k"]] = cell
        out[(c["set"], str(c["allocation"]))] = dict(
            n_e=c["n_e"], m=c["m"], q_hat=c["q_hat"], T=int(c["T"]),
            k_max_at_T=c["k_max_at_T"], cells=cells)
    return out


# ===========================================================================
# PHASE: measure  (THE VF-1 GATE)
# ===========================================================================
def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]


def phase_measure(state):
    t0 = time.time()
    frozen = load_frozen()
    results = []
    for (sid, alab, T) in ALLOCATIONS:
        F = frozen[(sid, alab)]
        n_e, q = F["n_e"], F["q_hat"]
        ks = [k for k, c in sorted(F["cells"].items()) if c.get("c_lo") is not None]
        if not ks:
            continue
        lo = np.array([F["cells"][k]["c_lo"] for k in ks])
        hi = np.array([F["cells"][k]["c_hi"] for k in ks])
        C = cmatrix(n_e, ks)
        seed = seed_of(sid, alab, T, "val", N_VAL)
        fire = np.zeros(len(ks), dtype=np.int64)
        fin = np.zeros(len(ks), dtype=np.int64)
        for blk in draw_stats(n_e, q, T, ks, N_VAL, seed, C):
            ok = np.isfinite(blk)
            fin += ok.sum(axis=0)
            fire += (ok & ((blk < lo[None, :]) | (blk > hi[None, :]))).sum(axis=0)
        for j, k in enumerate(ks):
            cell = F["cells"][k]
            size = float(fire[j]) / float(fin[j]) if fin[j] else None
            ci = wilson(int(fire[j]), int(fin[j]))
            in_band = bool(size is not None and ACCEPT_LO <= size <= ACCEPT_HI)
            results.append(dict(
                set=sid, allocation=alab, T=T, k=k,
                c_lo_as_read_from_amendment_v3=cell["c_lo"],
                c_hi_as_read_from_amendment_v3=cell["c_hi"],
                half_width_lo_bits=abs(cell["c_lo"]), half_width_hi_bits=abs(cell["c_hi"]),
                status_in_amendment=cell["status"],
                validation_replicates=int(N_VAL),
                finite_validation_replicates=int(fin[j]),
                firings=int(fire[j]),
                measured_size_of_transcribed_constants=size,
                measured_size_ci95=ci,
                nominal_size=NOMINAL_ALPHA,
                inside_acceptance_gate=in_band,
                reported=bool(cell["status"] == "REPORTED" and in_band),
            ))
        print("[measure] %-6s T=%-4s  %d cells  size %.5f..%.5f  (%.0fs)"
              % (sid, alab, len(ks),
                 min(r["measured_size_of_transcribed_constants"] for r in results
                     if r["set"] == sid and r["allocation"] == alab),
                 max(r["measured_size_of_transcribed_constants"] for r in results
                     if r["set"] == sid and r["allocation"] == alab),
                 time.time() - t0))
    state["measure"] = dict(rows=results, core_seconds=time.time() - t0)


# ===========================================================================
# PHASE: qsens  (VF-3)
# ===========================================================================
def sens_grid(se_rel):
    g = {0.0}
    for mult in (1, 2, 3):
        g |= {mult * se_rel, -mult * se_rel}
    for d in (0.0025, 0.005, 0.01, 0.02, 0.04):
        g |= {d, -d}
    return sorted(g)


def phase_qsens(state):
    t0 = time.time()
    frozen = load_frozen()
    out = []
    for (sid, alab, T) in ALLOCATIONS:
        F = frozen[(sid, alab)]
        n_e, q0 = F["n_e"], F["q_hat"]
        ks = [k for k, c in sorted(F["cells"].items())
              if c.get("c_lo") is not None and c["status"] == "REPORTED"]
        if not ks:
            continue
        lo = np.array([F["cells"][k]["c_lo"] for k in ks])
        hi = np.array([F["cells"][k]["c_hi"] for k in ks])
        C = cmatrix(n_e, ks)
        se_rel = se_rel_q(n_e, q0, SETS[sid]["block_failures"])
        rows = []
        for d in sens_grid(se_rel):
            q = q0 * (1.0 + d)
            seed = seed_of(sid, alab, T, "sens", repr(d), N_SENS)
            fire = np.zeros(len(ks), dtype=np.int64)
            fin = np.zeros(len(ks), dtype=np.int64)
            for blk in draw_stats(n_e, q, T, ks, N_SENS, seed, C):
                ok = np.isfinite(blk)
                fin += ok.sum(axis=0)
                fire += (ok & ((blk < lo[None, :]) | (blk > hi[None, :]))).sum(axis=0)
            for j, k in enumerate(ks):
                s = float(fire[j]) / float(fin[j]) if fin[j] else None
                rows.append(dict(k=k, rel_shift=d, se_multiple=(d / se_rel if se_rel else None),
                                 size=s, in_band=bool(s is not None and ACCEPT_LO <= s <= ACCEPT_HI),
                                 finite=int(fin[j]), firings=int(fire[j])))
        # per-k breakdown shift: smallest |rel_shift| at which the size leaves the band
        per_k = []
        for k in ks:
            rk = [r for r in rows if r["k"] == k]
            bad = [abs(r["rel_shift"]) for r in rk if not r["in_band"] and r["rel_shift"] != 0.0]
            bd = min(bad) if bad else None
            at3 = [r for r in rk if abs(abs(r["se_multiple"]) - 3.0) < 1e-9]
            per_k.append(dict(
                k=k,
                size_at_q_hat=[r["size"] for r in rk if r["rel_shift"] == 0.0][0],
                size_at_minus_3SE=min((r["size"] for r in at3 if r["se_multiple"] < 0), default=None),
                size_at_plus_3SE=min((r["size"] for r in at3 if r["se_multiple"] > 0), default=None),
                all_in_band_over_pm_3SE=all(r["in_band"] for r in rk
                                            if abs(r["se_multiple"]) <= 3.0 + 1e-9),
                breakdown_rel_shift=bd,
                margin_factor=(bd / (3 * se_rel) if bd else None),
            ))
        out.append(dict(set=sid, allocation=alab, q_hat=q0,
                        block_failures=SETS[sid]["block_failures"],
                        se_rel_q_hat=se_rel, three_se_rel=3 * se_rel,
                        rows=rows, per_k=per_k))
        robust = all(p["all_in_band_over_pm_3SE"] for p in per_k)
        print("[qsens] %-6s T=%-4s 3SE=%.4f%%  robust over +-3SE: %s  (%.0fs)"
              % (sid, alab, 300 * se_rel, robust, time.time() - t0))
    state["qsens"] = dict(configurations=out, core_seconds=time.time() - t0)
    inject("Q-SENSITIVITY", render_qsens(out))


def render_qsens(cfgs) -> str:
    ind = ""
    L = [ind + "generated_by: recalibrate.py phase 'qsens'",
         ind + "n_validation_replicates_per_point: %d" % N_SENS,
         ind + "se_reference: 'rho = 0 (independent blocks): SE(q_hat)/q_hat = sqrt((1-q)/block_failures).",
         ind + "  This is the rho = 0 VALUE and is a LOWER bound under the positive block correlation",
         ind + "  this experiment exists to detect (validator TASK-20260806-301f68). Not an upper bound.'",
         ind + "configurations:"]
    for c in cfgs:
        L.append(ind + "- set: %s" % c["set"])
        L.append(ind + "  allocation: '%s'" % c["allocation"])
        L.append(ind + "  block_failures_stage_A: %d" % c["block_failures"])
        L.append(ind + "  se_rel_q_hat: %s" % yf(c["se_rel_q_hat"]))
        L.append(ind + "  three_se_rel: %s" % yf(c["three_se_rel"]))
        L.append(ind + "  robust_over_plus_minus_3SE_at_every_reported_k: %s"
                 % str(all(p["all_in_band_over_pm_3SE"] for p in c["per_k"])).lower())
        L.append(ind + "  per_k:")
        for p in c["per_k"]:
            L.append(ind + "  - {k: %d, size_at_q_hat: %s, size_at_minus_3SE: %s, "
                           "size_at_plus_3SE: %s, all_in_band_over_pm_3SE: %s, "
                           "breakdown_rel_shift: %s, margin_over_3SE: %s}"
                     % (p["k"], yf(p["size_at_q_hat"]),
                        yf(p["size_at_minus_3SE"]) if p["size_at_minus_3SE"] is not None else "null",
                        yf(p["size_at_plus_3SE"]) if p["size_at_plus_3SE"] is not None else "null",
                        str(p["all_in_band_over_pm_3SE"]).lower(),
                        yf(p["breakdown_rel_shift"]) if p["breakdown_rel_shift"] else "null",
                        yf(p["margin_factor"]) if p["margin_factor"] else "null"))
    return "\n".join(L)


# ===========================================================================
# PHASE: battery  (RT2-OBJ-1, carried forward not closed)
# ===========================================================================
def _near_null(n_e, q, k_target, s_add, s_rem):
    """Tail-directed perturbation of Bin(n_e,q) preserving sum p, E[S] and
    E[C(S,k_target)] exactly, supported on {s_add} u s_rem.

    This is the red team's RT2-OBJ-1 construction (TASK-20260806-42c153 section 2.2),
    re-derived here rather than copied.  It is a DECLARED ALTERNATIVE law used only
    to measure the rule's size off its calibration point.  It is not an HQC object.
    """
    base = binom_pmf(n_e, q)
    idx = [s_add] + list(s_rem)
    M = np.array([[1.0] * len(idx),
                  [float(s) for s in idx],
                  [float(math.comb(s, k_target)) for s in idx]])
    _, _, Vt = np.linalg.svd(M)
    u4 = Vt[-1]
    if u4[idx.index(s_add)] < 0:
        u4 = -u4
    u = np.zeros(n_e + 1)
    for c, s in zip(u4, idx):
        u[s] = c
    neg = u < 0
    dmax = float(np.min(base[neg] / (-u[neg]))) if neg.any() else math.inf
    return base, u, dmax


def _exact_log2_A(p, n_e, ks):
    Es = float(p @ np.arange(n_e + 1))
    qq = Es / n_e
    out = {}
    for k in ks:
        ck = np.array([float(math.comb(s, k)) for s in range(n_e + 1)])
        mu = float(p @ ck) / math.comb(n_e, k)
        out[k] = (math.log2(mu) - k * math.log2(qq)) if mu > 0 else None
    return out


def phase_battery(state):
    """RT2-OBJ-1, carried forward: the rule is sized at the binomial POINT, and
    the red team exhibited a law at TV 8.9e-5 from it on which log2 A_m is
    identically 0 and the k=m cell fires 91.4% of the time.

    Measured here at TWO cells: PS-R1 k=16 (the red team's own cell -- an
    independent reproduction of their objection) and PS-R3 k=17 at T=1e7, which
    is the cell this campaign actually funds and which the red team did not test.
    Also measured: what the MULTI-k battery does to the same law, which is the
    mitigation v3 adopts.  This does NOT close RT2-OBJ-1; see the amendment.
    """
    t0 = time.time()
    frozen = load_frozen()
    targets = [("PS-R1", "1e8", 16, 36, (17, 19, 21)),
               ("PS-R3", "1e7", 17, 45, (20, 22, 24))]
    out = []
    for (sid, alab, ktg, s_add, s_rem) in targets:
        F = frozen[(sid, alab)]
        n_e, q, T = F["n_e"], F["q_hat"], F["T"]
        base, u, dmax = _near_null(n_e, q, ktg, s_add, s_rem)
        ks_rep = [k for k, c in sorted(F["cells"].items())
                  if c.get("c_lo") is not None and c["status"] == "REPORTED"]
        ks_all = sorted(set(ks_rep + ([ktg] if F["cells"].get(ktg, {}).get("c_lo")
                                      is not None else [])))
        lo = np.array([F["cells"][k]["c_lo"] for k in ks_all])
        hi = np.array([F["cells"][k]["c_hi"] for k in ks_all])
        rep_mask = np.array([k in ks_rep for k in ks_all])
        C = cmatrix(n_e, ks_all)
        rows = []
        for frac in (0.0, 0.01, 0.1, 0.98):
            p = np.clip(base + frac * dmax * u, 0.0, None)
            p = p / p.sum()
            tv = 0.5 * float(np.abs(p - base).sum())
            exact = _exact_log2_A(p, n_e, ks_all)
            n_rep = 200_000
            rng = np.random.Generator(np.random.PCG64(seed_of("battery", sid, alab, repr(frac))))
            fire = np.zeros(len(ks_all), dtype=np.int64)
            fin = np.zeros(len(ks_all), dtype=np.int64)
            anyfire = 0
            done = 0
            while done < n_rep:
                c = min(CHUNK, n_rep - done)
                H = rng.multinomial(T, p, size=c)
                v = log2_A_vec(H, n_e, ks_all, C)
                ok = np.isfinite(v)
                f = ok & ((v < lo[None, :]) | (v > hi[None, :]))
                fin += ok.sum(axis=0)
                fire += f.sum(axis=0)
                anyfire += int(f[:, rep_mask].any(axis=1).sum())
                done += c
            j = ks_all.index(ktg)
            rows.append(dict(
                delta_fraction_of_bound=frac,
                total_variation_from_binomial=tv,
                exact_log2_A_at_k_target=exact[ktg],
                exact_log2_A_relative_error_at_k_target=abs(exact[ktg]),
                size_at_k_target_alone=float(fire[j] / fin[j]) if fin[j] else None,
                rejection_by_multi_k_reported_battery=anyfire / n_rep,
                replicates=n_rep,
                per_k_firing_rate={int(k): float(fire[i] / fin[i]) if fin[i] else None
                                   for i, k in enumerate(ks_all)},
                exact_log2_A_per_k={int(k): exact[k] for k in ks_all}))
            print("[battery] %-6s k=%-3d frac=%.2f TV=%.3g log2A_k=%.3g "
                  "size@k_alone=%.4f multi-k-reject=%.4f"
                  % (sid, ktg, frac, tv, exact[ktg] if exact[ktg] is not None else float('nan'),
                     rows[-1]["size_at_k_target_alone"],
                     rows[-1]["rejection_by_multi_k_reported_battery"]))
        out.append(dict(set=sid, allocation=alab, k_target=ktg, T=T,
                        construction=dict(support_added=s_add, support_removed=list(s_rem),
                                          constraints="sum u = 0; sum s*u = 0; "
                                                      "sum C(s,k_target)*u = 0",
                                          delta_max_nonnegativity=dmax),
                        reported_k_in_battery=ks_rep, rows=rows))
    state["battery"] = dict(targets=out, core_seconds=time.time() - t0)


# ===========================================================================
# PHASE: idxmap  (CTRL-IDXMAP: a control with a DIFFERENT invariance)
# ===========================================================================
def _reference_index_map(n, N, n_e, L):
    """The block index map as the SPECIFICATION defines it, computed from the
    frozen parameters alone.  trunc[i] = i (coordinate i of e'' for i < N);
    block j reads truncated coordinates [j*L, (j+1)*L)."""
    trunc = list(range(N))
    blocks = [[trunc[j * L + t] for t in range(L)] for j in range(n_e)]
    return trunc, blocks


def _instrument_index_map(n, N, n_e, L, defect="none"):
    """A stand-in 'instrument' that EMITS the coordinates it actually reads.
    The defects are the three CTRL-POSHOM was measured blind to."""
    if defect == "none":
        off = 0
        trunc = [(i + off) % n for i in range(N)]
        blocks = [[trunc[j * L + t] for t in range(L)] for j in range(n_e)]
    elif defect == "V1-truncation-offset":            # whole window shifted by 1
        trunc = [(i + 1) % n for i in range(N)]
        blocks = [[trunc[j * L + t] for t in range(L)] for j in range(n_e)]
    elif defect == "V2-interleaved-partition":        # blocks decimated, not contiguous
        trunc = list(range(N))
        blocks = [[trunc[j + t * n_e] for t in range(L)] for j in range(n_e)]
    elif defect == "V3-last-block-early":             # last block's window off by -1
        trunc = list(range(N))
        blocks = [[trunc[j * L + t - (1 if j == n_e - 1 else 0)] for t in range(L)]
                  for j in range(n_e)]
    else:
        raise ValueError(defect)
    return trunc, blocks


def phase_idxmap(state):
    """Deterministic demonstration on a TOY ring.  Constructs no HQC object and
    no parameter-set instance; the point being demonstrated is that the
    control's detection probability is 1 BY CONSTRUCTION, not statistical."""
    t0 = time.time()
    n, N, n_e, L = 71, 60, 6, 10          # toy: n prime, n_e*L = N < n
    ref_t, ref_b = _reference_index_map(n, N, n_e, L)
    rows = []
    for defect in ("none", "V1-truncation-offset", "V2-interleaved-partition",
                   "V3-last-block-early"):
        got_t, got_b = _instrument_index_map(n, N, n_e, L, defect)
        mismatch_t = sum(1 for a, b in zip(ref_t, got_t) if a != b)
        mismatch_b = sum(1 for A, B in zip(ref_b, got_b)
                         for a, b in zip(A, B) if a != b)
        fires = (mismatch_t + mismatch_b) > 0
        rows.append(dict(defect=defect, truncation_index_mismatches=mismatch_t,
                         block_index_mismatches=mismatch_b, CTRL_IDXMAP_fires=fires,
                         detection="deterministic" if fires else "n/a"))
        print("[idxmap] %-26s trunc-mismatch=%-3d block-mismatch=%-4d fires=%s"
              % (defect, mismatch_t, mismatch_b, fires))
    state["idxmap"] = dict(
        toy_parameters=dict(n=n, N=N, n_e=n_e, L=L),
        rows=rows,
        scope=("Toy ring, no HQC object. Demonstrates the MECHANISM only: the "
               "control compares emitted read indices against indices derived "
               "from the frozen parameters, so its detection probability for an "
               "index-arithmetic defect is 1 by construction rather than "
               "statistical. It does NOT demonstrate anything about stage_a.py, "
               "which this task did not read, run, or instrument."),
        core_seconds=time.time() - t0)


# ===========================================================================
# main
# ===========================================================================
def phase_reinject(state):
    """Re-write both machine-generated blocks from the cached phase results.

    Deterministic and free: the constants are a pure function of the frozen
    procedure and its seeds, so re-injection cannot change them. Exists so the
    surrounding PROSE of amendment_v3.yaml can be edited without paying for a
    recalibration -- and the `measure` phase, which re-reads the file, is the
    check that the edit did not disturb a constant.
    """
    inject("FROZEN-INTERVALS", render_frozen(state["calibrate"]["configurations"]))
    inject("Q-SENSITIVITY", render_qsens(state["qsens"]["configurations"]))
    print("[reinject] both machine-generated blocks rewritten from cache")


PHASES = dict(selftest=phase_selftest, calibrate=phase_calibrate,
              qsens=phase_qsens, measure=phase_measure,
              battery=phase_battery, idxmap=phase_idxmap,
              reinject=phase_reinject)
ORDER = ["selftest", "calibrate", "qsens", "measure", "battery", "idxmap"]


def main(argv):
    want = argv[1:] or ["all"]
    if want == ["all"]:
        want = ORDER
    os.makedirs(WORK, exist_ok=True)
    statef = os.path.join(WORK, "state.json")
    state = json.load(open(statef)) if os.path.exists(statef) else {}
    t0 = time.time()
    for ph in want:
        PHASES[ph](state)
        json.dump(state, open(statef, "w"), indent=1, default=str)
    state["_meta"] = dict(
        task="TASK-20260806-6086cb", batch="BATCH-0a65c0", goal="GOAL-HQC-001",
        experiment="EXP-HQC-982268", role="executor", claim_tier="toy",
        constructs_no_hqc_object=True, runs_no_measurement_arm=True,
        computes_no_log2_A_k_on_any_T_arm=True,
        environment=dict(python=platform.python_version(), numpy=np.__version__,
                         pyyaml=yaml.__version__, platform=platform.platform()),
        phases_run=want, wall_seconds=time.time() - t0)
    json.dump(state, open(statef, "w"), indent=1, default=str)
    if "measure" in want:
        write_transcribed(state)
    print("\n[done] %s in %.1f s" % (",".join(want), time.time() - t0))


def write_transcribed(state):
    rows = state["measure"]["rows"]
    bad = [r for r in rows if r["status_in_amendment"] == "REPORTED"
           and not r["inside_acceptance_gate"]]
    doc = dict(
        schema="transcribed_size/v1",
        task="TASK-20260806-6086cb", batch="BATCH-0a65c0", goal="GOAL-HQC-001",
        experiment="EXP-HQC-982268", amends="AMD-EXP-HQC-982268-v3", claim_tier="toy",
        what_this_measures=(
            "The realized two-sided size of the INV-NULL v3 decision rule USING THE "
            "CONSTANTS AS THEY APPEAR IN amendment_v3.yaml. The constants were read "
            "back out of that file with yaml.safe_load, type-asserted to be floats, "
            "and scored on validation draws INDEPENDENT of the calibration draws that "
            "produced them. This is the check VF-1 exists to force: a rule is only as "
            "calibrated as its encoding."),
        boundary=(
            "TOY. No HQC object was constructed, no measurement arm was run, and no "
            "log2_A_k was computed on any space-(T) arm. Every draw is from "
            "S ~ Binomial(n_e, q_hat) under the declared null. Nothing here is a "
            "statement about HQC, assumption A17 or A5, any decoding-failure rate, or "
            "any standardized parameter set."),
        acceptance_gate=[ACCEPT_LO, ACCEPT_HI],
        nominal_size=NOMINAL_ALPHA,
        n_calibration_replicates=N_CAL,
        n_validation_replicates=N_VAL,
        validation_independent_of_calibration=True,
        constants_read_back_from="amendment_v3.yaml",
        roundtrip=dict(
            method=("every constant emitted through yf(); asserted to satisfy "
                    "float(str)==value AND yaml.safe_load(str) is a float equal to "
                    "the value; the whole table was re-read after injection and "
                    "compared bit-for-bit against the in-memory values"),
            max_abs_difference_readback_vs_generated=0.0,
            all_constants_parse_as_float=True,
            pyyaml_dotless_exponent_trap_guarded=True),
        estimator_selftest=state.get("selftest"),
        summary=dict(
            cells_measured=len(rows),
            cells_with_status_REPORTED=sum(1 for r in rows
                                           if r["status_in_amendment"] == "REPORTED"),
            reported_cells_outside_gate=len(bad),
            reported_cells_outside_gate_detail=bad,
            min_size_over_reported=min((r["measured_size_of_transcribed_constants"]
                                        for r in rows
                                        if r["status_in_amendment"] == "REPORTED"), default=None),
            max_size_over_reported=max((r["measured_size_of_transcribed_constants"]
                                        for r in rows
                                        if r["status_in_amendment"] == "REPORTED"), default=None),
            v2_comparison=dict(
                note=("amendment_v2.yaml's transcribed constants at k=2, measured by "
                      "validator TASK-20260806-301f68 on 1e6 fresh draws per cell"),
                PS_R1_k2=0.00610, PS_R3_k2=0.00419, PS_R5_k2=0.00551,
                gate=[ACCEPT_LO, ACCEPT_HI])),
        cells=rows,
        q_sensitivity=state.get("qsens"),
        environment=state.get("_meta", {}).get("environment"),
    )
    json.dump(doc, open(TRANSCRIBED, "w"), indent=1)
    print("[transcribed_size.json] %d cells; %d REPORTED cells outside the gate"
          % (len(rows), len(bad)))


if __name__ == "__main__":
    main(sys.argv)
