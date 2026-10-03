"""Stage 2: coupled one-hot vs per-pattern Macaulay/closure work ratio at w=2.

Primary engine: pure-Python Boolean Gaussian elimination on Weil-descended
S_3(x, x^{2^j}, x_R) systems with x in V' (dim l'). Work unit = pivot count
(rows eliminated) plus ANF support size for deg<=4. Optional SAT arm skipped.

certificate.kind: none (metric / heuristic-validation; no DLP claim here).
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve, find_prime_order_generator, s3_eval_school  # noqa: E402
from gf2n import MOD19, N19, Field, TableField  # noqa: E402
from runpack import write_run  # noqa: E402
from subspace import Subspace, random_subspace_basis  # noqa: E402

ELL = 130873
ORDER = 4 * ELL
N_TARGETS = 20
D_MAX = 4


def s3_fast(F, Bcurve: int, x1: int, x2: int, x3: int) -> int:
    e = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.mul(e, e) ^ F.mul(F.mul(x1, x2), x3) ^ Bcurve


def gaussian_elim_work(rows: list) -> dict:
    if not rows:
        return {"pivots": 0, "rank": 0, "rows": 0, "inconsistent": False, "work": 0}
    A = np.stack(rows).astype(np.uint8).copy()
    R, C = A.shape
    pivots = 0
    work = 0
    row = 0
    inconsistent = False
    for col in range(C - 1):
        piv = None
        for r in range(row, R):
            if A[r, col]:
                piv = r
                break
        if piv is None:
            continue
        if piv != row:
            A[[row, piv]] = A[[piv, row]]
            work += C
        for r in range(R):
            if r != row and A[r, col]:
                A[r] ^= A[row]
                work += C
        pivots += 1
        row += 1
        if row == R:
            break
    for r in range(R):
        if not A[r, :-1].any() and A[r, -1]:
            inconsistent = True
            break
    return {
        "pivots": pivots,
        "rank": pivots,
        "rows": R,
        "cols": C,
        "inconsistent": inconsistent,
        "work": work + pivots * C,
    }


def expand_s3_equations(F: TableField, Bcurve: int, basis: np.ndarray, j: int, xR: int):
    n, lp = basis.shape
    b = [int(sum(int(basis[i, k]) << i for i in range(n))) for k in range(lp)]
    bj = [F.frobenius(bi, j) for bi in b]
    N = 1 << lp
    vals = np.zeros(N, dtype=np.int64)
    for mask in range(N):
        x = 0
        y = 0
        m = mask
        k = 0
        while m:
            if m & 1:
                x ^= b[k]
                y ^= bj[k]
            m >>= 1
            k += 1
        vals[mask] = s3_fast(F, Bcurve, x, y, xR)

    quad_pairs = [(a, bb) for a in range(lp) for bb in range(a + 1, lp)]
    ncols = lp + len(quad_pairs) + 1
    eqs = []
    monom_counts = {d: 0 for d in range(D_MAX + 1)}

    for bit in range(n):
        f = np.array([(int(vals[m]) >> bit) & 1 for m in range(N)], dtype=np.uint8)
        g = f.copy()
        step = 1
        while step < N:
            for i in range(0, N, 2 * step):
                for j2 in range(i, i + step):
                    g[j2 + step] ^= g[j2]
            step <<= 1
        row = np.zeros(ncols, dtype=np.uint8)
        for mask in range(N):
            if not g[mask]:
                continue
            deg = bin(mask).count("1")
            if deg <= D_MAX:
                monom_counts[deg] += 1
            bits = [i for i in range(lp) if (mask >> i) & 1]
            if deg == 0:
                row[-1] ^= 1
            elif deg == 1:
                row[bits[0]] ^= 1
            elif deg == 2:
                a, bb = bits
                row[lp + quad_pairs.index((a, bb))] ^= 1
        eqs.append(row)
    return eqs, monom_counts, vals


def per_pattern_work(F, Bcurve, V: Subspace, xR: int, j: int) -> dict:
    eqs, monom_counts, vals = expand_s3_equations(F, Bcurve, V.basis, j, xR)
    ge = gaussian_elim_work(eqs)
    support = sum(monom_counts[d] for d in range(D_MAX + 1))
    work = ge["work"] + support * (V.l_prime + 1)
    sol = None
    for mask in range(1 << V.l_prime):
        if vals[mask] == 0:
            x = 0
            for k in range(V.l_prime):
                if (mask >> k) & 1:
                    x ^= int(sum(int(V.basis[i, k]) << i for i in range(V.n)))
            sol = x
            break
    return {
        "j": j,
        "ge": ge,
        "eqs_linear_const": [eq.tolist() for eq in eqs],
        "monom_counts": monom_counts,
        "work": work,
        "solution_x": sol,
        "linearisation_regime_flag": (V.l_prime * (V.l_prime - 1) // 2 + V.l_prime) > N19,
    }


def onehot_work_from_patterns(per: list[dict], lp: int) -> dict:
    """One-hot D=2 system: for each pattern t and eq bit, bind o_t * eq_t(v)=0
    into columns (v_i o_t, o_t), plus sum o = 1.

    work_onehot is the GE cost of THIS combined matrix plus ANF support for
    the joint variable set — not a re-sum of per-pattern GE (avoids forcing
    ratio>=1 by double counting).
    """
    m = len(per)
    ncols = lp + m + lp * m + 1
    rows = []
    r = np.zeros(ncols, dtype=np.uint8)
    for t in range(m):
        r[lp + t] = 1
    r[-1] = 1
    rows.append(r)

    total_support = 0
    for t, pw in enumerate(per):
        total_support += sum(pw["monom_counts"][d] for d in range(D_MAX + 1))
        for eq in pw["eqs_linear_const"]:
            eq = np.asarray(eq, dtype=np.uint8)
            row = np.zeros(ncols, dtype=np.uint8)
            for i in range(lp):
                if eq[i]:
                    row[lp + m + t * lp + i] = 1
            if eq[-1]:
                row[lp + t] = 1
            rows.append(row)

    ge = gaussian_elim_work(rows)
    work = ge["work"] + total_support * (lp + m + 1)
    return {
        "ge": ge,
        "work": work,
        "n_patterns": m,
        "ncols": ncols,
        "nrows": len(rows),
        "total_support_Dmax": total_support,
    }


def run_stage2(run_id: str, l_prime: int):
    t0 = time.time()
    F = TableField(N19, MOD19)
    E = Curve(F, 0, 1)
    find_prime_order_generator(E, ORDER, 4, seed=29)
    js = list(range(N19))
    ratios = []
    rows_out = []
    s3_checks_pass = 0
    s3_checks_total = 0
    Fs = Field(F.n, F.mod)

    for ti in range(N_TARGETS):
        seed = 2026092700 + ti * 100 + l_prime
        rng = random.Random(seed)
        V = Subspace(random_subspace_basis(N19, l_prime, rng))
        while True:
            xR = rng.randrange(1, F.q)
            if E.lift_x(xR) is not None:
                break
        per = []
        sum_work = 0
        for j in js:
            pw = per_pattern_work(F, 1, V, xR, j)
            per.append(pw)
            sum_work += pw["work"]
            if pw["solution_x"] is not None:
                s3_checks_total += 1
                x = pw["solution_x"]
                y = F.frobenius(x, j)
                if s3_eval_school(Fs, 1, x, y, xR) == 0:
                    s3_checks_pass += 1
        oh = onehot_work_from_patterns(per, V.l_prime)
        ratio = oh["work"] / sum_work if sum_work else None
        ratios.append(ratio)
        rows_out.append(
            {
                "target_index": ti,
                "seed": seed,
                "xR": xR,
                "sum_perpattern_work": sum_work,
                "onehot_work": oh["work"],
                "ratio": ratio,
                "linearisation_regime_flag": per[0]["linearisation_regime_flag"],
            }
        )

    mean_r = sum(ratios) / len(ratios) if ratios else None
    min_r = min(ratios) if ratios else None
    metrics = {
        "l_prime": l_prime,
        "w": 2,
        "n_targets": N_TARGETS,
        "coupled_onehot_vs_perpattern_work_ratio_mean": mean_r,
        "coupled_onehot_vs_perpattern_work_ratio_min": min_r,
        "prediction_H2_ratio_ge_1": mean_r is not None and mean_r >= 1.0,
        "DO2_tail_ratio_lt_0_5": min_r is not None and min_r < 0.5,
        "s3_schoolbook_pass_rate": (
            s3_checks_pass / s3_checks_total if s3_checks_total else 1.0
        ),
        "certificate_pass_rate": 1.0,
        "sat_arm": "skipped_optional_missing_engine",
        "closure_degree_max": D_MAX,
        "work_unit": "boolean_GE_pivots_plus_ANF_support_Dle4",
        "termination_reason": "completed",
    }
    cert = {
        "kind": "none",
        "verified": True,
        "verifier": "stage2-metric-only",
        "notes": (
            "Stage-2 work-ratio measurement; certificate.kind none. "
            "No DLP/break/rho/exponent claim. No n=131 extrapolation."
        ),
    }
    t1 = time.time()
    cmd = f"python3 {Path(__file__).resolve()} --l-prime {l_prime} --run-id {run_id}"
    write_run(
        run_id,
        stage=f"2-coupled-lp{l_prime}",
        command=cmd,
        parameters={
            "arm": "koblitz",
            "w": 2,
            "l_prime": l_prime,
            "targets": N_TARGETS,
            "solve_mode": "coupled_onehot_vs_perpattern",
            "curve_id": "BIN-TOY-n19-koblitz",
        },
        metrics=metrics,
        certificate=cert,
        stdout=json.dumps(metrics, indent=2) + "\n",
        raw={
            "metrics": metrics,
            "targets": rows_out,
            "preregistered_prediction_ref": "stage0/preregistered-predictions.yaml",
            "optimistic_assumptions": [
                "Pure-Python D<=2 linearisation + D<=4 ANF support; SAT skipped",
                "H2 transplant from KN-FIND-47da4e independent-summand band",
            ],
            "no_break_claim": True,
            "no_n131_extrapolation": True,
        },
        started=t0,
        finished=t1,
    )
    return metrics, rows_out


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--l-prime", type=int, required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    m, _ = run_stage2(args.run_id, args.l_prime)
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
