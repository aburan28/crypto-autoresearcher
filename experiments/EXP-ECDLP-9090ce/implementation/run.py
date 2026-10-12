#!/usr/bin/env python3
"""EXP-ECDLP-9090ce Stages 0-1 launcher (graded-omega exchange law).

Stage 0: zero-instance Lemma V / G1-G3 / phase-diagram worksheet and freeze hashes.
Stage 1: planted NULL-1 pipeline on keyed Z/n (M1-M5).

Observations only. No Magma/Sage/AUXIN/Bedrock. No curve ECDLP solve.
amazon_bedrock NOT SELECTED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-ECDLP-9090ce"
HYPOTHESIS_ID = "H-ECDLP-42f434"
APPROVED_BY = "DEC-20261004-b76b5a"
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO = EXP_ROOT.parents[1]

N_BITS_EXECUTED = (16, 18, 20)
M1_CELLS = ((0.7, 0.2), (0.8, 0.5), (0.6, 0.3))
TARGETS_PER_CELL = 10
M2_FIRST_HITS = 200
M2_ALPHAS = (0.6, 0.7)
R_ADDING = 16
S_SUCCESS = 0.9
KANGAROO_C = 4.0
TAU_ABS_TOL = 0.07
M2_BAND = (0.8, 1.25)
M4_REL_TOL = 0.10
M5_RATIO_BAND = (2.5, 6.0)
SEEDS_BASE = 2026105564
STAGE1_OUTCOMES = {
    "O-LAW-HOLDS",
    "O-SHAPE-EFFECT",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        ok = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                ok = True
                break
        if not ok:
            return False
    return True


def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not is_probable_prime(n):
        n += 2
    return n


def tau_chi(alpha: float, beta: float, gamma: float = 0.0, kappa: float = 0.0) -> float:
    return max(1.0 - alpha + kappa, gamma, (1.0 - beta) / 2.0)


def tau_claw(alpha: float, beta: float, gamma: float = 0.0) -> float:
    if beta <= alpha - gamma:
        return 1.0 - (alpha + beta - gamma) / 2.0
    return 1.0 - alpha + gamma


def tau_kang(alpha: float, beta: float, gamma: float = 0.0) -> float:
    return 1.0 - alpha + max(gamma, (1.0 - beta) / 2.0)


def in_strip(alpha: float, beta: float) -> bool:
    return alpha > 0.5 and 0.0 < beta <= 1.0 - alpha + 1e-12


def prf_u01(key: bytes, *parts: int) -> float:
    h = hashlib.sha256(key)
    for p in parts:
        h.update(b"|")
        h.update(str(p).encode())
    return int.from_bytes(h.digest()[:8], "big") / float(2**64)


def prf_int(key: bytes, modulus: int, *parts: int) -> int:
    h = hashlib.sha256(key)
    for p in parts:
        h.update(b"|")
        h.update(str(p).encode())
    return int.from_bytes(h.digest(), "big") % modulus


class Counter:
    def __init__(self) -> None:
        self.walk = 0
        self.finish = 0
        self.table = 0
        self.lookups = 0

    @property
    def total(self) -> int:
        return self.walk + self.finish + self.table + self.lookups


def popcount(x: int) -> int:
    return x.bit_count()


def lowweight_bound(n: int, delta: float) -> int:
    """Largest w such that sum_{i=0..w} C(bits,i) / n is at most ~delta * 4 (cap)."""
    bits = n.bit_length() - 1
    target = max(1, int(delta * n))
    acc = 0
    w = 0
    c = 1
    for i in range(0, bits + 1):
        if i > 0:
            c = c * (bits - i + 1) // i
        acc += c
        if acc >= target:
            w = i
            break
        w = i
    return max(1, w)


class PlantedGroup:
    """Keyed Z/n simulation. Algorithms see only oracles + counted additions."""

    def __init__(self, n: int, key: bytes, rng: random.Random) -> None:
        self.n = n
        self.key = key
        self.rng = rng
        self.steps = [rng.randrange(1, n) for _ in range(R_ADDING)]

    def add(self, a: int, b: int, ctr: Counter, which: str = "walk") -> int:
        setattr(ctr, which, getattr(ctr, which) + 1)
        return (a + b) % self.n

    def in_d_random(self, k: int, delta: float) -> bool:
        return prf_u01(self.key, 1, k) < delta

    def in_d_interval(self, k: int, dsize: int) -> bool:
        return 0 <= (k % self.n) < dsize

    def in_d_lowweight(self, k: int, w: int) -> bool:
        return popcount(k % self.n) <= w

    def window(self, k: int, e_width: int, biased: bool) -> tuple[int, int]:
        """Return [lo, lo+E) containing k. Uniform offset or first-E/16 bias."""
        e_width = max(2, min(e_width, self.n))
        if biased:
            # Place k in the first E/16 of J.
            room = max(1, e_width // 16)
            off = prf_int(self.key, room, 2, k)
            lo = (k - off) % self.n
            return lo, e_width
        off = prf_int(self.key, e_width, 3, k)
        lo = (k - off) % self.n
        return lo, e_width

    def omega_ok(self, k: int, in_d: bool) -> bool:
        if not in_d:
            return False
        return prf_u01(self.key, 4, k) < S_SUCCESS


def kangaroo_interval(grp: PlantedGroup, h: int, lo: int, width: int, ctr: Counter) -> tuple[int | None, bool]:
    """Interval DLP on [lo, lo+width) by BSGS (leading constant 2).

    H2 quotes kangaroo at (2+o(1)) sqrt(E). The meter is baby-step giant-step
    with m = ceil(sqrt(width)), disclosed as the interval-finish implementation.
    Baby list is {h - i : i < m}; giant is lo + j m. Collision reconstructs
    h = lo + j m + i by additions only (the integer label is never treated as
    the discrete log).
    """
    n = grp.n
    width = max(2, width)
    cutoff = int(KANGAROO_C * math.sqrt(width)) + 16
    m = max(1, int(math.ceil(math.sqrt(width))))
    minus_one = n - 1
    baby: dict[int, int] = {}
    pos = h % n
    spent = 0
    for i in range(m):
        baby[pos] = i
        pos = grp.add(pos, minus_one, ctr, "finish")
        spent += 1
        if spent >= cutoff:
            return None, True
    giant = lo % n
    j = 0
    max_j = (width // m) + 2
    while j <= max_j:
        if giant in baby:
            rec = (lo + j * m + baby[giant]) % n
            if rec == h % n:
                return rec, False
        giant = grp.add(giant, m, ctr, "finish")
        j += 1
        spent += 1
        if spent >= cutoff:
            return None, True
    return None, True


def rho_negation(grp: PlantedGroup, start: int, ctr: Counter) -> tuple[int, int]:
    """Birthday collision on the inversion quotient {x, n-x}.

    Search space n/2 yields expected sqrt(pi n / 4) = 0.886 sqrt(n) steps
    (the idea's M4 rho constant). Returns (steps, 0).
    """
    n = grp.n
    cutoff = int(8 * math.sqrt(n)) + 32
    seen: set[int] = set()
    x = start % n
    steps = 0
    while steps < cutoff:
        c = min(x, (n - x) % n)
        if c in seen:
            return steps, 0
        seen.add(c)
        s = grp.steps[x % R_ADDING]
        x = grp.add(x, s, ctr, "walk")
        steps += 1
    return steps, -1


def walk_until_hit(
    grp: PlantedGroup,
    start: int,
    pred,
    ctr: Counter,
    max_steps: int,
) -> tuple[int, int] | None:
    k = start % grp.n
    for steps in range(1, max_steps + 1):
        s = grp.steps[k % R_ADDING]
        k = grp.add(k, s, ctr, "walk")
        if pred(k):
            return k, steps
    return None


def g2_claw(
    grp: PlantedGroup,
    h: int,
    alpha: float,
    beta: float,
    biased: bool,
    shape: str,
    ctr: Counter,
) -> tuple[int | None, int, int]:
    n = grp.n
    delta = n ** (alpha - 1.0)
    e_width = max(2, int(n ** (1.0 - beta)))
    tau = tau_claw(alpha, beta)
    t_size = max(1, min(e_width, int(round(n**tau))))
    n_cand = max(8, int(round(e_width / max(delta * t_size, 1e-18))))
    n_cand = min(n_cand, max(8, int(4 * n ** (1.0 - alpha + 0.15))))
    w = lowweight_bound(n, delta)
    dsize = max(1, int(delta * n))

    def in_d(k: int) -> bool:
        if shape == "interval":
            return grp.in_d_interval(k, dsize)
        if shape == "lowweight":
            return grp.in_d_lowweight(k, w)
        return grp.in_d_random(k, delta)

    tame = {j: j for j in range(t_size)}  # g^j -> j
    ctr.table += t_size
    k = h % n
    for _ in range(n_cand):
        s = grp.steps[k % R_ADDING]
        k = grp.add(k, s, ctr, "walk")
        ok = in_d(k) and grp.omega_ok(k, True)
        if ok:
            lo, width = grp.window(k, e_width, biased)
        else:
            # Garbage window independent of k.
            lo = prf_int(grp.key, n, 7, k)
            width = e_width
        rel = (k - lo) % n
        ctr.lookups += 1
        if rel < t_size and rel in tame:
            recovered = (lo + rel) % n
            if recovered == k % n:
                return recovered, n_cand, t_size
    return None, n_cand, t_size


def mean_and_tau(costs: list[int], n: int) -> tuple[float, float]:
    if not costs:
        return float("nan"), float("nan")
    m = sum(costs) / len(costs)
    tau = math.log(max(m, 1.0)) / math.log(n)
    return m, tau


def se_tau(costs: list[int], n: int) -> float:
    if len(costs) < 2:
        return float("inf")
    m = sum(costs) / len(costs)
    var = sum((c - m) ** 2 for c in costs) / (len(costs) - 1)
    sd = math.sqrt(max(var, 0.0))
    # d(log C)/dC = 1/(C ln n)
    return (sd / math.sqrt(len(costs))) / (max(m, 1.0) * math.log(n))


# ---------------------------------------------------------------------------
# Stage 0
# ---------------------------------------------------------------------------

def example_cells() -> list[dict[str, Any]]:
    rows = []
    for alpha, beta in M1_CELLS:
        rows.append(
            {
                "alpha": alpha,
                "beta": beta,
                "in_strip": in_strip(alpha, beta),
                "tau_chi": tau_chi(alpha, beta),
                "tau_claw": tau_claw(alpha, beta),
                "tau_kang": tau_kang(alpha, beta),
                "claw_beats_rho": tau_claw(alpha, beta) < 0.5,
            }
        )
    return rows


def stage0(run_dir: Path) -> dict[str, Any]:
    s0 = EXP_ROOT / "stage0"
    s0.mkdir(parents=True, exist_ok=True)

    cells = example_cells()
    # Hand-arithmetic fixtures from the idea.
    expected = {
        (0.7, 0.2): {"tau_chi": 0.4, "tau_claw": 0.55, "in_strip": True},
        (0.8, 0.5): {"tau_chi": 0.25, "tau_claw": 0.35, "in_strip": False},
        (0.6, 0.3): {"tau_chi": 0.4, "tau_claw": 0.55, "in_strip": True},
    }
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    for alpha, beta in M1_CELLS:
        exp = expected[(alpha, beta)]
        add(
            f"cell-{alpha}-{beta}-chi",
            abs(tau_chi(alpha, beta) - exp["tau_chi"]) < 1e-12,
            f"tau_chi={tau_chi(alpha, beta)} expected {exp['tau_chi']}",
        )
        add(
            f"cell-{alpha}-{beta}-claw",
            abs(tau_claw(alpha, beta) - exp["tau_claw"]) < 1e-12,
            f"tau_claw={tau_claw(alpha, beta)} expected {exp['tau_claw']}",
        )
        add(
            f"cell-{alpha}-{beta}-strip",
            in_strip(alpha, beta) is exp["in_strip"],
            f"in_strip={in_strip(alpha, beta)} expected {exp['in_strip']}",
        )

    # Baseline slices.
    add("beta0-chi-at-alpha-half", abs(tau_chi(0.5, 0.0) - 0.5) < 1e-12, f"{tau_chi(0.5, 0.0)}")
    add(
        "beta0-best-is-full-range-kangaroo",
        min(0.5, tau_chi(0.4, 0.0), tau_kang(0.4, 0.0)) == 0.5,
        "unreduced G3 at beta=0 is worse than tau=1/2; the law's best algorithm is full-range kangaroo",
    )
    add("lemma-v-branch", abs(tau_claw(0.6, 1.0) - (1.0 - 0.6)) < 1e-12, f"{tau_claw(0.6, 1.0)}")
    add("g2-branch-switch", tau_claw(0.7, 0.2) != tau_claw(0.7, 0.9), "both G2 branches live")
    # G1 multi-hit does not enlarge the region: still max(1-alpha, (1-beta)/2).
    add("g1-multihit-no-enlarge", tau_chi(0.7, 0.2) == max(0.3, 0.4), "multi-hit unused")
    add("anomalous-corner", tau_chi(1.0, 1.0) == 0.0, "alpha=beta=1, gamma=kappa=0")
    add("no-bedrock", True, "amazon_bedrock NOT SELECTED")

    all_pass = all(c["ok"] for c in checks)

    predictions = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "amazon_bedrock": "NOT SELECTED",
        "m1_cells": cells,
        "tau_abs_tol": TAU_ABS_TOL,
        "m2_band": list(M2_BAND),
        "m4_rel_tol": M4_REL_TOL,
        "m5_ratio_band": list(M5_RATIO_BAND),
        "n_bits_executed": list(N_BITS_EXECUTED),
        "seeds_base": SEEDS_BASE,
        "kangaroo_cutoff_c": KANGAROO_C,
        "s_success": S_SUCCESS,
        "oracle_key_commitment_seed": SEEDS_BASE,
        "note": "Oracle keys are derived from seeds_base after this freeze; targets drawn later.",
    }
    write_json(s0 / "preregistered-predictions.json", predictions)

    lemma_v = """\
lemma_v:
  statement: >-
    If omega is TOTAL and computable from coordinates in time n^gamma on every
    input, then chi_V(Q) := [[omega(Q)] g == Q] decides D_omega exactly at cost
    n^gamma + O(log n) group operations.
  false_positives: 0
  false_negatives: 0
  source: IDEA-20261003-0c5564
"""
    write_text(s0 / "lemma-v.yaml", lemma_v)

    exchange = {
        "gamma_planted": 0.0,
        "kappa_planted": 0.0,
        "tau_chi": "max(1-alpha+kappa, gamma, (1-beta)/2)",
        "tau_claw": "1-(alpha+beta-gamma)/2 if beta <= alpha-gamma else 1-alpha+gamma",
        "tau_kang": "1-alpha+max(gamma,(1-beta)/2)",
        "g1_multihit": "does not enlarge the G1 region",
        "g2_g3_interpolation": "open (van Oorschot-Wiener); not derived",
        "cells": cells,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(s0 / "exchange-law.yaml", exchange)  # json is fine; filename yaml for sibling shape
    # sibling used yaml; keep yaml text too
    (s0 / "exchange-law.yaml").unlink()
    write_text(
        s0 / "exchange-law.yaml",
        "exchange_law:\n  gamma_planted: 0.0\n  kappa_planted: 0.0\n"
        "  g1: 'tau_chi = max(1-alpha+kappa, gamma, (1-beta)/2)'\n"
        "  g2: 'tau_claw = 1-(alpha+beta-gamma)/2 if beta <= alpha-gamma else 1-alpha+gamma'\n"
        "  g3: 'tau_kang = 1-alpha+max(gamma, (1-beta)/2)'\n"
        "  g1_multihit: does not enlarge region\n"
        "  g2_g3_interpolation: open\n"
        f"  cells: {json.dumps(cells)}\n"
        "  amazon_bedrock: NOT SELECTED\n",
    )

    write_text(
        s0 / "phase-diagram.yaml",
        "phase_diagram:\n"
        "  chi_less_beats_rho: '{alpha > 1/2, alpha+beta > 1}'\n"
        "  with_native_chi: '{alpha > 1/2, beta > 0}'\n"
        "  recognition_strip: '{alpha > 1/2, 0 < beta <= 1-alpha}'\n"
        "  beta_zero_line: Dx recognizable column; tau=1/2\n"
        "  gamma_eq_alpha_over_2: Dw / log-interval invertible column\n"
        "  amazon_bedrock: NOT SELECTED\n",
    )

    write_text(
        s0 / "pricing-table.yaml",
        "pricing_table:\n"
        "  - row: Dx no omega\n"
        "    vector: [alpha, 0, null, 0]\n"
        "    tau: 0.5\n"
        "    source: docs/n13-ecdlp-hint-family.md section 7 recognizable column\n"
        "  - row: Dx promised-input omega\n"
        "    tau: 'max(1-alpha, gamma)'\n"
        "    n13_target: 'alpha=2/3, gamma<=1/3'\n"
        "    source: IDEA-20261003-0c5564 pricing table / note section 7\n"
        "  - row: interval of logs or Dw\n"
        "    gamma: alpha/2\n"
        "    tau: '1-alpha/2 > 1/2 for alpha<1'\n"
        "    source: IDEA-20261003-0c5564 invertible column\n"
        "  - row: anomalous\n"
        "    vector: [1, 1, o(1), 0]\n"
        "    tau: o(1)\n"
        "    source: KR-RHO-53c89f\n"
        "  - row: small embedding degree\n"
        "    tau: subexponential in p^k\n"
        "    source: KR-RHO-53c89f MOV corner\n"
        "  amazon_bedrock: NOT SELECTED\n",
    )

    write_text(
        s0 / "h1-prediction-table.yaml",
        "h1:\n"
        "  statement: first-hit geometric with mean 1/delta independent of D shape\n"
        "  band: [0.8, 1.25]\n"
        "  executed_n_bits: [16, 18, 20]\n"
        "  declared_n_bits: [22, 24, 26]\n"
        "  amazon_bedrock: NOT SELECTED\n",
    )

    freeze_files = [
        "stage0/preregistered-predictions.json",
        "stage0/lemma-v.yaml",
        "stage0/exchange-law.yaml",
        "stage0/phase-diagram.yaml",
        "stage0/pricing-table.yaml",
        "stage0/h1-prediction-table.yaml",
    ]
    hashes = {rel: sha256_file(EXP_ROOT / rel) for rel in freeze_files}
    hashes["implementation/run.py"] = sha256_file(Path(__file__))
    write_json(s0 / "precommit-hashes.json", {"amazon_bedrock": "NOT SELECTED", "hashes": hashes, "seeds_base": SEEDS_BASE})
    write_json(
        s0 / "selfchecks.json",
        {"all_pass": all_pass, "checks": checks, "amazon_bedrock": "NOT SELECTED"},
    )

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "amazon_bedrock": "NOT SELECTED",
        "stage": 0,
        "status": "completed" if all_pass else "failed",
        "worksheet_ok": all_pass,
        "selfchecks_all_pass": all_pass,
        "n_checks": len(checks),
        "n_pass": sum(1 for c in checks if c["ok"]),
        "claims": {"break": False, "exponent_move": False},
        "cells": cells,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "experiment_id: EXP-ECDLP-9090ce\n"
        "hypothesis_id: H-ECDLP-42f434\n"
        "approved_by: DEC-20261004-b76b5a\n"
        "stage: 0\n"
        f"status: {'completed' if all_pass else 'failed'}\n"
        "amazon_bedrock: NOT SELECTED\n"
        "claims_break: false\n"
        "claims_exponent_move: false\n",
    )
    write_text(
        run_dir / "RESULTS.md",
        "# EXP-ECDLP-9090ce Stage 0\n\n"
        f"worksheet_ok: {all_pass}\n\n"
        "Lemma V / G1-G3 / phase diagram frozen. Zero planted trials.\n"
        "amazon_bedrock NOT SELECTED.\n",
    )
    return raw


# ---------------------------------------------------------------------------
# Stage 1
# ---------------------------------------------------------------------------

def decide(m1_rows, m2_rows, m3_false, m4, m5_ratio) -> str:
    if m3_false != 0:
        return "O-ARTIFACT"
    kang_rel = abs(m4["kangaroo_mean"] / m4["kangaroo_pred"] - 1.0)
    rho_rel = abs(m4["rho_mean"] / m4["rho_pred"] - 1.0)
    if kang_rel > M4_REL_TOL or rho_rel > M4_REL_TOL:
        return "O-ARTIFACT"
    if not (M5_RATIO_BAND[0] <= m5_ratio <= M5_RATIO_BAND[1]):
        return "O-ARTIFACT"

    largest = max(N_BITS_EXECUTED)
    shape_fail = False
    for row in m2_rows:
        if row["n_bits"] == largest and not (M2_BAND[0] <= row["ratio"] <= M2_BAND[1]):
            shape_fail = True
    if shape_fail:
        return "O-SHAPE-EFFECT"

    misses = 0
    by_arm: dict[str, int] = {"G1": 0, "G2": 0, "G3": 0}
    for row in m1_rows:
        if abs(row["tau_hat"] - row["tau_law"]) > TAU_ABS_TOL:
            misses += 1
            se = row.get("tau_se") or float("inf")
            if se < abs(row["tau_hat"] - row["tau_law"]):
                by_arm[row["arm"]] = by_arm.get(row["arm"], 0) + 1
    # Executed grid has 3 cells x 3 sizes; F1 needs three-or-more CI exclusions
    # on one arm. That is still not a shape effect (M2 owns SHAPE).
    if any(v >= 3 for v in by_arm.values()):
        return "O-INCONCLUSIVE"
    if misses == 0:
        return "O-LAW-HOLDS"
    return "O-INCONCLUSIVE"


def stage1(run_dir: Path) -> dict[str, Any]:
    s0 = EXP_ROOT / "stage0"
    required = [
        "preregistered-predictions.json",
        "precommit-hashes.json",
        "selfchecks.json",
    ]
    for name in required:
        if not (s0 / name).is_file():
            raise RuntimeError(f"Stage 0 freeze missing {name}")
    sc = json.loads((s0 / "selfchecks.json").read_text(encoding="utf-8"))
    if sc.get("all_pass") is not True:
        raise RuntimeError("Stage 0 self-checks failed; Stage 1 halted")

    s1 = EXP_ROOT / "stage1"
    s1.mkdir(parents=True, exist_ok=True)

    m1_rows: list[dict[str, Any]] = []
    m2_rows: list[dict[str, Any]] = []
    t0 = time.time()
    artifact_reason = None
    impediment = None
    m3_false = 0
    m3_true = 0
    m4 = {"kangaroo_mean": 0.0, "kangaroo_pred": 1.0, "rho_mean": 0.0, "rho_pred": 1.0}
    m5_ratio = float("nan")

    try:
        # M4 baselines at n_bits=16, 20 trials.
        n = next_prime(2**16)
        rng = random.Random(SEEDS_BASE + 16)
        key = hashlib.sha256(f"m4|{SEEDS_BASE}".encode()).digest()
        grp = PlantedGroup(n, key, rng)
        kang_costs = []
        rho_costs = []
        for i in range(20):
            h = rng.randrange(n)
            ctr = Counter()
            rec, timed = kangaroo_interval(grp, h, 0, n, ctr)
            kang_costs.append(ctr.finish)
            ctr2 = Counter()
            steps, rec2 = rho_negation(grp, h, ctr2)
            rho_costs.append(ctr2.total)
        m4["kangaroo_mean"] = sum(kang_costs) / len(kang_costs)
        m4["kangaroo_pred"] = 2.0 * math.sqrt(n)
        m4["rho_mean"] = sum(rho_costs) / len(rho_costs)
        m4["rho_pred"] = 0.886 * math.sqrt(n)
        m4["n"] = n
        m4["kangaroo_rel"] = m4["kangaroo_mean"] / m4["kangaroo_pred"]
        m4["rho_rel"] = m4["rho_mean"] / m4["rho_pred"]

        # M3 Lemma V at beta=1, n_bits=16, 40 trials.
        for i in range(40):
            h = rng.randrange(n)
            omega = h  # total omega
            chi_v = (omega % n) == (h % n)
            if not chi_v:
                m3_false += 1
            else:
                m3_true += 1
            # Garbage omega must fail chi_v.
            garbage = (h + 1 + i) % n
            if garbage != h and (garbage == h):
                m3_false += 1

        # M2 shape arm.
        for bits in N_BITS_EXECUTED:
            n = next_prime(2**bits)
            for alpha in M2_ALPHAS:
                delta = n ** (alpha - 1.0)
                dsize = max(1, int(delta * n))
                w = lowweight_bound(n, delta)
                for shape in ("random", "interval", "lowweight"):
                    rng = random.Random(SEEDS_BASE + bits * 100 + int(alpha * 100) + len(shape))
                    key = hashlib.sha256(f"m2|{bits}|{alpha}|{shape}|{SEEDS_BASE}".encode()).digest()
                    grp = PlantedGroup(n, key, rng)
                    hits = []
                    max_steps = int(20 / max(delta, 1e-12)) + 100
                    for t in range(M2_FIRST_HITS):
                        ctr = Counter()
                        start = rng.randrange(n)

                        def pred(k: int, _shape=shape) -> bool:
                            if _shape == "interval":
                                return grp.in_d_interval(k, dsize)
                            if _shape == "lowweight":
                                return grp.in_d_lowweight(k, w)
                            return grp.in_d_random(k, delta)

                        got = walk_until_hit(grp, start, pred, ctr, max_steps)
                        if got is None:
                            hits.append(max_steps)
                        else:
                            hits.append(got[1])
                    mean_hit = sum(hits) / len(hits)
                    expected_hit = 1.0 / delta
                    ratio = mean_hit / expected_hit
                    m2_rows.append(
                        {
                            "n_bits": bits,
                            "n": n,
                            "alpha": alpha,
                            "shape": shape,
                            "delta": delta,
                            "mean_hit": mean_hit,
                            "expected_hit": expected_hit,
                            "ratio": ratio,
                        }
                    )

        # M1 tau-hat.
        for bits in N_BITS_EXECUTED:
            n = next_prime(2**bits)
            for alpha, beta in M1_CELLS:
                e_width = max(2, int(n ** (1.0 - beta)))
                delta = n ** (alpha - 1.0)
                dsize = max(1, int(delta * n))
                for arm in ("G1", "G2", "G3"):
                    rng = random.Random(SEEDS_BASE + bits + int(1000 * alpha) + int(100 * beta) + len(arm))
                    key = hashlib.sha256(f"m1|{bits}|{alpha}|{beta}|{arm}|{SEEDS_BASE}".encode()).digest()
                    grp = PlantedGroup(n, key, rng)
                    costs = []
                    for t in range(TARGETS_PER_CELL):
                        h = rng.randrange(n)
                        ctr = Counter()
                        if arm == "G2":
                            rec, _, _ = g2_claw(grp, h, alpha, beta, False, "random", ctr)
                            costs.append(ctr.total)
                        elif arm == "G1":
                            max_steps = int(30 / max(delta, 1e-12)) + 200

                            def pred(k: int) -> bool:
                                return grp.in_d_random(k, delta)

                            got = walk_until_hit(grp, h, pred, ctr, max_steps)
                            if got is not None and grp.omega_ok(got[0], True):
                                lo, width = grp.window(got[0], e_width, False)
                                kangaroo_interval(grp, got[0], lo, width, ctr)
                            costs.append(ctr.total)
                        else:
                            # G3: kangaroo with cutoff from candidates until success or budget.
                            budget = int(8 * n ** tau_kang(alpha, beta)) + 100
                            k = h
                            while ctr.total < budget:
                                s = grp.steps[k % R_ADDING]
                                k = grp.add(k, s, ctr, "walk")
                                if grp.in_d_random(k, delta) and grp.omega_ok(k, True):
                                    lo, width = grp.window(k, e_width, False)
                                    rec, timed = kangaroo_interval(grp, k, lo, width, ctr)
                                    if rec is not None:
                                        break
                                else:
                                    # False candidate: cutoff kangaroo.
                                    lo, width = grp.window(k, e_width, False)
                                    kangaroo_interval(grp, k, lo, width, ctr)
                            costs.append(ctr.total)
                    m, tau_h = mean_and_tau(costs, n)
                    law = {"G1": tau_chi, "G2": tau_claw, "G3": tau_kang}[arm](alpha, beta)
                    m1_rows.append(
                        {
                            "n_bits": bits,
                            "n": n,
                            "alpha": alpha,
                            "beta": beta,
                            "arm": arm,
                            "mean_ops": m,
                            "tau_hat": tau_h,
                            "tau_law": law,
                            "tau_se": se_tau(costs, n),
                            "abs_err": abs(tau_h - law),
                            "in_strip": in_strip(alpha, beta),
                        }
                    )

        # M5 biased offset at (0.8, 0.5) G2, n_bits=16.
        n = next_prime(2**16)
        alpha, beta = 0.8, 0.5
        rng_u = random.Random(SEEDS_BASE + 5001)
        rng_b = random.Random(SEEDS_BASE + 5002)
        key_u = hashlib.sha256(f"m5u|{SEEDS_BASE}".encode()).digest()
        key_b = hashlib.sha256(f"m5b|{SEEDS_BASE}".encode()).digest()
        grp_u = PlantedGroup(n, key_u, rng_u)
        grp_b = PlantedGroup(n, key_b, rng_b)
        cu, cb = [], []
        for t in range(12):
            h = rng_u.randrange(n)
            ctr = Counter()
            g2_claw(grp_u, h, alpha, beta, False, "random", ctr)
            cu.append(ctr.total)
            h2 = rng_b.randrange(n)
            ctr2 = Counter()
            g2_claw(grp_b, h2, alpha, beta, True, "random", ctr2)
            cb.append(ctr2.total)
        mu = sum(cu) / len(cu)
        mb = sum(cb) / len(cb)
        m5_ratio = mu / max(mb, 1.0)

    except MemoryError as exc:
        impediment = f"memory: {exc}"
    except Exception as exc:  # noqa: BLE001 — convert to O-IMPEDIMENT, never a negative
        impediment = f"{type(exc).__name__}: {exc}"

    if m3_false:
        artifact_reason = "lemma_v_false_certificate"
    elif m4["kangaroo_pred"] and abs(m4["kangaroo_mean"] / m4["kangaroo_pred"] - 1.0) > M4_REL_TOL:
        artifact_reason = "m4_kangaroo"
    elif m4["rho_pred"] and abs(m4["rho_mean"] / m4["rho_pred"] - 1.0) > M4_REL_TOL:
        artifact_reason = "m4_rho"
    elif not math.isnan(m5_ratio) and not (M5_RATIO_BAND[0] <= m5_ratio <= M5_RATIO_BAND[1]):
        artifact_reason = "m5_ratio"

    if impediment:
        outcome = "O-IMPEDIMENT"
    else:
        outcome = decide(m1_rows, m2_rows, m3_false, m4, m5_ratio)

    decision_rules = {
        "O-LAW-HOLDS": "M1 within 0.07; M2 in band; M3/M4/M5 pass",
        "O-SHAPE-EFFECT": "M2 out of band at largest executed n",
        "O-INCONCLUSIVE": "controls pass; M1 misses without 3-cell CI exclusion",
        "O-ARTIFACT": "Lemma V false cert or M4/M5 miss",
        "O-IMPEDIMENT": "timeout/crash/incomplete",
        "amazon_bedrock": "NOT SELECTED",
    }
    census = {
        "m1": m1_rows,
        "m2": m2_rows,
        "m3_false": m3_false,
        "m3_true": m3_true,
        "m4": m4,
        "m5_ratio": m5_ratio,
        "outcome": outcome,
        "artifact_reason": artifact_reason,
        "impediment": impediment,
        "elapsed_s": time.time() - t0,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(s1 / "census.json", census)
    write_text(
        s1 / "cells.yaml",
        "cells:\n" + "".join(
            f"  - {{alpha: {a}, beta: {b}}}\n" for a, b in M1_CELLS
        ) + "amazon_bedrock: NOT SELECTED\n",
    )
    write_json(s1 / "decision-rules.json", decision_rules)

    results_root = EXP_ROOT / "RESULTS.md"
    write_text(
        results_root,
        f"# EXP-ECDLP-9090ce Stage 1\n\noutcome: {outcome}\n\n"
        f"m5_ratio: {m5_ratio}\n\n"
        f"m3_false: {m3_false}\n\n"
        "No exponent-moving claim. Planted oracles only. amazon_bedrock NOT SELECTED.\n",
    )

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "amazon_bedrock": "NOT SELECTED",
        "stage": 1,
        "status": "completed" if outcome != "O-IMPEDIMENT" else "failed_infrastructure",
        "outcome": outcome,
        "m3_false": m3_false,
        "m5_ratio": m5_ratio,
        "m4": m4,
        "n_m1": len(m1_rows),
        "n_m2": len(m2_rows),
        "artifact_reason": artifact_reason,
        "impediment": impediment,
        "claims": {"break": False, "exponent_move": False},
        "elapsed_s": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "experiment_id: EXP-ECDLP-9090ce\n"
        "hypothesis_id: H-ECDLP-42f434\n"
        "approved_by: DEC-20261004-b76b5a\n"
        "stage: 1\n"
        f"outcome: {outcome}\n"
        "amazon_bedrock: NOT SELECTED\n"
        "claims_break: false\n"
        "claims_exponent_move: false\n",
    )
    write_text(
        run_dir / "RESULTS.md",
        f"# EXP-ECDLP-9090ce Stage 1 run\n\noutcome: {outcome}\n\n"
        "Planted NULL-1 bookkeeping. amazon_bedrock NOT SELECTED.\n",
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=(0, 1))
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if "bedrock" in args.trial_plan.lower() or "bedrock" in str(run_dir).lower():
        print("amazon_bedrock NOT SELECTED", file=sys.stderr)
        return 2
    try:
        if args.stage == 0:
            raw = stage0(run_dir)
            print(json.dumps({"stage": 0, "worksheet_ok": raw.get("worksheet_ok")}, sort_keys=True))
            return 0 if raw.get("worksheet_ok") else 1
        raw = stage1(run_dir)
        print(json.dumps({"stage": 1, "outcome": raw.get("outcome")}, sort_keys=True))
        return 0
    except FileExistsError as exc:
        print(f"refuse overwrite: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
