#!/usr/bin/env python3
"""Stages 2-3 drivers for EXP-BINSTD-591d28 (TASK-20261002-d8df85).

Does not rewrite stage0/, stage1/, or RESULTS.md from Stages 0-1.
Writes stage2/, stage3/, and RESULTS-stages2-3.md only.
No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from datetime import datetime, timezone
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

# Local Field / S4 helpers from sibling run.py namespace via importlib would
# re-enter main; duplicate the tiny field kernel here instead.
EXPERIMENT_ID = "EXP-BINSTD-591d28"
HYPOTHESIS_ID = "H-BINSTD-5fdceb"
APPROVED_BY = "DEC-20261002-397fcd"
TASK_ID = "TASK-20261002-d8df85"
EXP_ROOT = Path(__file__).resolve().parents[1]
IMPL_DIR = Path(__file__).resolve().parent
MASTER_SEED = 2026092731
N_RC1 = 17
MOD_RC1 = (1 << 17) | (1 << 3) | 1
A_RC1 = 97044
B_RC1 = 126251
A_KOB = 1
B_KOB = 1
M = 3
L_LEVELS = (4, 5, 6)
N_TARGETS = 50
N_TARGETS_E = 10
N_KOBLITZ_TARGETS = 5
G_SIGMA = 0b100111001
SAMPLE_E_BUDGET_S23 = {4: 1 << 16, 5: 1 << 14, 6: 1 << 12}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def write_yaml_manifest(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")

    def dump(obj: Any, indent: int = 0) -> list[str]:
        pad = "  " * indent
        lines: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{pad}{k}:")
                    lines.extend(dump(v, indent + 1))
                elif isinstance(v, bool):
                    lines.append(f"{pad}{k}: {'true' if v else 'false'}")
                elif v is None:
                    lines.append(f"{pad}{k}: null")
                elif isinstance(v, (int, float)):
                    lines.append(f"{pad}{k}: {v}")
                else:
                    s = str(v).replace('"', '\\"')
                    lines.append(f'{pad}{k}: "{s}"')
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(dump(item, indent + 1))
                else:
                    lines.append(f"{pad}- {item}")
        return lines

    path.write_text("\n".join(dump(data)) + "\n", encoding="utf-8")


def peak_rss_bytes() -> int | None:
    try:
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception:
        return None


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


class Field:
    def __init__(self, n: int, mod: int):
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r


def formula_dim(k: int, l: int, n: int) -> int:
    return min(k * (l - 1) + 1, n)


def predicted_spurious(l: int, n: int = N_RC1, m: int = M) -> float:
    dims = [formula_dim(k, l, n) for k in range(1, m + 1)]
    return float(math.factorial(m) * (2 ** (sum(dims) - m * l)))


def s3_coeffs_field(F: Field, B: int, x: int, y: int) -> tuple[int, int, int]:
    xy = F.mul(x, y)
    xp = x ^ y
    alpha = F.mul(xp, xp)
    beta = xy
    gamma = F.mul(xy, xy) ^ B
    return alpha, beta, gamma


def s4_field(F: Field, B: int, x1: int, x2: int, x3: int, x4: int) -> int:
    a1, b1, c1 = s3_coeffs_field(F, B, x1, x2)
    a2, b2, c2 = s3_coeffs_field(F, B, x3, x4)
    t1 = F.mul(a1, c2) ^ F.mul(a2, c1)
    t2 = F.mul(a1, b2) ^ F.mul(a2, b1)
    t3 = F.mul(b1, c2) ^ F.mul(b2, c1)
    return F.mul(t1, t1) ^ F.mul(t2, t3)


def elementary_symmetric(x1: int, x2: int, x3: int, F: Field) -> tuple[int, int, int]:
    e1 = x1 ^ x2 ^ x3
    e2 = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    e3 = F.mul(F.mul(x1, x2), x3)
    return e1, e2, e3


def expand_cubic_from_roots(F: Field, r1: int, r2: int, r3: int) -> tuple[int, int, int]:
    e1 = r1 ^ r2 ^ r3
    e2 = F.mul(r1, r2) ^ F.mul(r1, r3) ^ F.mul(r2, r3)
    e3 = F.mul(F.mul(r1, r2), r3)
    return e1, e2, e3


def s4_sym(F: Field, B: int, e1: int, e2: int, e3: int, xR: int) -> int:
    B2 = F.mul(B, B)
    e1_2 = F.mul(e1, e1)
    e1_4 = F.mul(e1_2, e1_2)
    e2_2 = F.mul(e2, e2)
    e2_4 = F.mul(e2_2, e2_2)
    e3_2 = F.mul(e3, e3)
    e3_3 = F.mul(e3_2, e3)
    e3_4 = F.mul(e3_2, e3_2)
    xR_2 = F.mul(xR, xR)
    xR_3 = F.mul(xR_2, xR)
    xR_4 = F.mul(xR_2, xR_2)
    acc = 0
    acc ^= F.mul(B2, e1_4)
    acc ^= F.mul(B, F.mul(e1_2, F.mul(e3, xR)))
    acc ^= F.mul(e1_2, F.mul(e3_2, xR_2))
    acc ^= F.mul(B, F.mul(e2_2, xR_2))
    acc ^= F.mul(e2_2, F.mul(e3, xR_3))
    acc ^= F.mul(e2_4, xR_4)
    acc ^= F.mul(B, e3_2)
    acc ^= F.mul(B, F.mul(e3, xR_3))
    acc ^= F.mul(e3_2, xR_4)
    acc ^= F.mul(e3_3, xR)
    acc ^= e3_4
    acc ^= F.mul(B2, xR_4)
    return acc


def _f2_basis(vectors: list[int]) -> list[int]:
    basis: list[int] = []
    for v in vectors:
        x = v
        for b in basis:
            if x == 0:
                break
            if x.bit_length() == b.bit_length():
                x ^= b
        if x:
            basis.append(x)
            basis.sort(key=lambda z: -z.bit_length())
            cleaned: list[int] = []
            for g in basis:
                y = g
                for c in cleaned:
                    if y.bit_length() == c.bit_length():
                        y ^= c
                if y:
                    cleaned.append(y)
                    cleaned.sort(key=lambda z: -z.bit_length())
            basis = cleaned
    return basis


def coords_to_field(bits: int, basis: list[int]) -> int:
    acc = 0
    j = 0
    m = bits
    while m:
        if m & 1:
            acc ^= basis[j]
        m >>= 1
        j += 1
    return acc


def enumerate_subspace(basis: list[int]) -> list[int]:
    out = []
    for mask in range(1 << len(basis)):
        out.append(coords_to_field(mask, basis))
    return out


def random_basis(l: int, n: int, rng: random.Random) -> list[int]:
    basis: list[int] = []
    used: list[tuple[int, int]] = []
    while len(basis) < l:
        v = rng.randrange(1, 1 << n)
        x = v
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
        basis.append(v)
    return basis


def product_bases_from_V(V_basis: list[int], F: Field, m: int = M) -> tuple[list[int], list[list[int]]]:
    dims: list[int] = []
    bases: list[list[int]] = []
    for k in range(1, m + 1):
        elems = set()
        for tup in combinations_with_replacement(V_basis, k):
            acc = 1
            for b in tup:
                acc = F.mul(acc, b)
            elems.add(acc)
        basis = _f2_basis(sorted(elems))
        dims.append(len(basis))
        bases.append(basis)
    return dims, bases


def poly_basis(l: int) -> list[int]:
    return [1 << j for j in range(l)]


def genuine_census_cell(
    F: Field,
    B: int,
    V_list: list[int],
    targets: list[int],
) -> dict[str, Any]:
    V_set = set(V_list)
    genuine_total = 0
    lift_recover = 0
    lift_denom = 0
    ordered_over_unique: list[float] = []
    unique_e_total = 0
    for xR in targets:
        gcount = 0
        e_mult: dict[tuple[int, int, int], int] = {}
        e_witness: dict[tuple[int, int, int], tuple[int, int, int]] = {}
        for x1 in V_list:
            for x2 in V_list:
                for x3 in V_list:
                    if s4_field(F, B, x1, x2, x3, xR) == 0:
                        gcount += 1
                        e = elementary_symmetric(x1, x2, x3, F)
                        e_mult[e] = e_mult.get(e, 0) + 1
                        e_witness.setdefault(e, (x1, x2, x3))
        genuine_total += gcount
        unique_e_total += len(e_mult)
        if e_mult:
            ordered_over_unique.append(gcount / len(e_mult))
        for (e1, e2, e3), w in e_witness.items():
            lift_denom += 1
            if (
                expand_cubic_from_roots(F, *w) == (e1, e2, e3)
                and all(r in V_set for r in w)
                and s4_field(F, B, w[0], w[1], w[2], xR) == 0
            ):
                lift_recover += 1
    n_t = max(len(targets), 1)
    return {
        "genuine_total_pooled": genuine_total,
        "mean_genuine_per_target": genuine_total / n_t,
        "mean_unique_genuine_e_per_target": unique_e_total / n_t,
        "mean_ordered_per_unique_e": (
            sum(ordered_over_unique) / len(ordered_over_unique) if ordered_over_unique else None
        ),
        "lift_agreement": (lift_recover / lift_denom) if lift_denom else 1.0,
        "lift_recover": lift_recover,
        "lift_denom": lift_denom,
    }


def e_space_sample(
    F: Field,
    B: int,
    bases: list[list[int]],
    targets: list[int],
    n_samples: int,
    rng: random.Random,
) -> dict[str, Any]:
    d1, d2, d3 = (len(b) for b in bases)
    space = 1 << (d1 + d2 + d3)
    hits = 0
    for xR in targets:
        for _ in range(n_samples):
            e1 = coords_to_field(rng.randrange(1 << d1), bases[0])
            e2 = coords_to_field(rng.randrange(1 << d2), bases[1])
            e3 = coords_to_field(rng.randrange(1 << d3), bases[2])
            if s4_sym(F, B, e1, e2, e3, xR) == 0:
                hits += 1
    n_assign = n_samples * len(targets)
    rate = hits / n_assign if n_assign else 0.0
    return {
        "enumeration_mode": "sampled",
        "n_samples_per_target": n_samples,
        "n_targets_e": len(targets),
        "n_assignments": n_assign,
        "e_hits": hits,
        "hit_rate": rate,
        "e_space_bits": d1 + d2 + d3,
        "e_space_size": space,
        "estimated_e_solutions_per_target": rate * space,
        "count_is_lower_bound": True,
    }


def stage2(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    stage1_path = EXP_ROOT / "stage1" / "spurious-lift-census.json"
    if not stage1_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 2,
            "outcome": "O-IMPEDIMENT",
            "impediment": "stage1/spurious-lift-census.json missing",
            "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
            "wall_clock_seconds": time.time() - t0,
            "peak_rss_bytes": peak_rss_bytes(),
            "amazon_bedrock": "NOT SELECTED",
            "task_id": TASK_ID,
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "schema": "crypto.autoresearch.run_manifest.v1",
                "experiment_id": EXPERIMENT_ID,
                "stage": 2,
                "outcome": "O-IMPEDIMENT",
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        print(json.dumps({"stage": 2, "outcome": "O-IMPEDIMENT"}, sort_keys=True))
        return raw

    stage1 = json.loads(stage1_path.read_text(encoding="utf-8"))
    F = Field(N_RC1, MOD_RC1)
    B = B_RC1
    rng = random.Random(MASTER_SEED)
    targets = [rng.randrange(1, F.q) for _ in range(N_TARGETS)]
    rng_e = random.Random(MASTER_SEED + 17)
    targets_e = targets[:N_TARGETS_E]
    rng_rand = random.Random(MASTER_SEED + 999)

    poly_cells = []
    rand_cells = []
    for l in L_LEVELS:
        # Poly P1 fill-in (sampled e-space); genuine from Stage 1
        V_poly = poly_basis(l)
        dims_p, bases_p = product_bases_from_V(V_poly, F, M)
        e_poly = e_space_sample(F, B, bases_p, targets_e, SAMPLE_E_BUDGET_S23[l], rng_e)
        s1_cell = next((c for c in stage1.get("cells", []) if c.get("l") == l), {})
        mean_g = s1_cell.get("mean_genuine_per_target")
        est_e = e_poly["estimated_e_solutions_per_target"]
        p1_est = (est_e / mean_g) if isinstance(mean_g, (int, float)) and mean_g > 0 else None
        poly_cells.append(
            {
                "l": l,
                "kind": "polynomial_basis",
                "dims": dims_p,
                "e_space": e_poly,
                "mean_genuine_per_target_from_stage1": mean_g,
                "spurious_factor_estimated": p1_est,
                "predicted_spurious_factor": predicted_spurious(l),
                "lift_agreement_stage1": s1_cell.get("lift_agreement"),
            }
        )

        # Random subspace null
        V_r = random_basis(l, N_RC1, rng_rand)
        dims_r, bases_r = product_bases_from_V(V_r, F, M)
        V_list = enumerate_subspace(V_r)
        genu = genuine_census_cell(F, B, V_list, targets)
        e_rand = e_space_sample(F, B, bases_r, targets_e, SAMPLE_E_BUDGET_S23[l], rng_e)
        mean_gr = genu["mean_genuine_per_target"]
        est_er = e_rand["estimated_e_solutions_per_target"]
        p3_est = (est_er / mean_gr) if mean_gr and mean_gr > 0 else None
        p3_ge = None
        if p3_est is not None and p1_est is not None:
            p3_ge = p3_est >= p1_est
        elif mean_gr is not None and isinstance(mean_g, (int, float)):
            # Fallback: faster saturation → fewer genuines / higher e-rate
            p3_ge = None
        rand_cells.append(
            {
                "l": l,
                "kind": "random_matched",
                "V_basis": V_r,
                "dims": dims_r,
                "sum_dims": sum(dims_r),
                "genuine": genu,
                "e_space": e_rand,
                "spurious_factor_estimated": p3_est,
                "poly_spurious_factor_estimated": p1_est,
                "P3_ge_poly": p3_ge,
                "P3_compare_note": (
                    "numeric estimated spurious comparison"
                    if p3_ge is not None
                    else "P1 and/or P3 undefined (zero genuine or null estimate); compare dims/e-rates"
                ),
            }
        )

    artifact = any(c["genuine"]["lift_agreement"] != 1.0 for c in rand_cells)
    outcome = "O-ARTIFACT" if artifact else "O-STAGES-2-PARTIAL"

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 2,
        "metric": "P3",
        "poly_p1_fillin": poly_cells,
        "random_null": rand_cells,
        "outcome": outcome,
        "note": (
            "Stage 2 random-subspace null + sampled e-space P1 fill-in. "
            "Does not rewrite stage0/stage1/RESULTS.md. Full O-* decided in Stage 3."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage2" / "random-subspace-summary.json", summary)
    write_json(
        EXP_ROOT / "stage2" / "p1-fillin-summary.json",
        {"poly_p1_fillin": poly_cells, "amazon_bedrock": "NOT SELECTED"},
    )

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 2,
        "outcome": outcome,
        "poly_p1_fillin": poly_cells,
        "random_null": rand_cells,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "schema": "crypto.autoresearch.run_manifest.v1",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 2,
            "outcome": outcome,
            "frozen": True,
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    print(json.dumps({"stage": 2, "outcome": outcome}, sort_keys=True))
    return raw


def _ker_g_sigma(F: Field, g: int) -> list[int]:
    def apply(poly: int, x: int) -> int:
        acc = 0
        y = x
        p = poly
        while p:
            if p & 1:
                acc ^= y
            y = F.sqr(y)
            p >>= 1
        return acc

    V = [x for x in range(F.q) if apply(g, x) == 0]
    used: list[tuple[int, int]] = []
    basis: list[int] = []
    for v in V:
        x = v
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
        basis.append(v)
    return basis


def _w4_work(F, B: int, basis: list[int], xR: int) -> dict[str, Any]:
    if str(IMPL_DIR) not in sys.path:
        sys.path.insert(0, str(IMPL_DIR))
    certbin = EXP_ROOT.parent / "EXP-CERTBIN-e94b27" / "impl"
    if str(certbin) not in sys.path:
        sys.path.insert(0, str(certbin))
    from closure import Closure  # type: ignore
    from descent_s3 import descend_s3  # type: ignore

    eqs, meta = descend_s3(F, B, basis, xR)
    cl = Closure(meta["nv"], 4, meta["neq"])
    t0 = time.time()
    rec, _cert = cl.w_closure(eqs, want_cert=False)
    wall = time.time() - t0
    dims = rec.get("dims") or []
    work = int(sum(dims) + rec.get("final_dim", 0))
    return {
        "first_iteration_containing_1": rec.get("one_first_iteration"),
        "final_dim": rec.get("final_dim"),
        "iterations_to_fixpoint": rec.get("iterations_to_fixpoint"),
        "one": rec.get("one"),
        "W4_work_units": work,
        "wall_s": wall,
        "nv": meta["nv"],
        "neq": meta["neq"],
    }


def _frobenius_orbit(F: Field, xR: int, n: int = 17) -> list[int]:
    orbit = []
    x = xR
    for _ in range(n):
        orbit.append(int(x))
        x = F.sqr(x)
    return orbit


def _pick_targets(F: Field, n: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    out = []
    seen = set()
    while len(out) < n:
        x = rng.randrange(1, F.q)
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def stage3(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    stage2_path = EXP_ROOT / "stage2" / "random-subspace-summary.json"
    if not stage2_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 3,
            "outcome": "O-IMPEDIMENT",
            "impediment": "stage2/random-subspace-summary.json missing",
            "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
            "wall_clock_seconds": time.time() - t0,
            "peak_rss_bytes": peak_rss_bytes(),
            "amazon_bedrock": "NOT SELECTED",
            "task_id": TASK_ID,
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "schema": "crypto.autoresearch.run_manifest.v1",
                "experiment_id": EXPERIMENT_ID,
                "stage": 3,
                "outcome": "O-IMPEDIMENT",
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        print(json.dumps({"stage": 3, "outcome": "O-IMPEDIMENT"}, sort_keys=True))
        return raw

    stage2 = json.loads(stage2_path.read_text(encoding="utf-8"))
    F = Field(N_RC1, MOD_RC1)

    # Koblitz arm
    basis_k = _ker_g_sigma(F, G_SIGMA)
    assert len(basis_k) == 8, len(basis_k)
    kob_targets = _pick_targets(F, N_KOBLITZ_TARGETS, MASTER_SEED ^ 0xA77711)
    kob_rows = []
    for xR in kob_targets:
        one = _w4_work(F, B_KOB, basis_k, xR)
        conj = _frobenius_orbit(F, xR, 17)
        conj_recs = [_w4_work(F, B_KOB, basis_k, x) for x in conj]
        sum_work = sum(r["W4_work_units"] for r in conj_recs)
        ratio = sum_work / (17 * one["W4_work_units"]) if one["W4_work_units"] else None
        kob_rows.append(
            {
                "x_R": xR,
                "one_instance": one,
                "orbit_sum_W4_work_units": sum_work,
                "orbit_closure_ratio": ratio,
            }
        )
    kob_mean = sum(r["orbit_closure_ratio"] for r in kob_rows if r["orbit_closure_ratio"] is not None) / max(
        len([r for r in kob_rows if r["orbit_closure_ratio"] is not None]), 1
    )

    # Ordinary null: dim-8 poly window, 17 unrelated targets
    basis_o = [1 << j for j in range(8)]
    ord_targets = _pick_targets(F, N_KOBLITZ_TARGETS, MASTER_SEED + 123)
    rng_u = random.Random(MASTER_SEED + 321)
    ord_rows = []
    for xR in ord_targets:
        one = _w4_work(F, B_RC1, basis_o, xR)
        unrelated = []
        seen = {xR}
        while len(unrelated) < 17:
            x = rng_u.randrange(1, F.q)
            if x in seen:
                continue
            seen.add(x)
            unrelated.append(x)
        urecs = [_w4_work(F, B_RC1, basis_o, x) for x in unrelated]
        sum_work = sum(r["W4_work_units"] for r in urecs)
        ratio = sum_work / (17 * one["W4_work_units"]) if one["W4_work_units"] else None
        ord_rows.append(
            {
                "x_R": xR,
                "one_instance": one,
                "unrelated_sum_W4_work_units": sum_work,
                "orbit_closure_ratio": ratio,
            }
        )
    ord_mean = sum(r["orbit_closure_ratio"] for r in ord_rows if r["orbit_closure_ratio"] is not None) / max(
        len([r for r in ord_rows if r["orbit_closure_ratio"] is not None]), 1
    )

    # P4 null reading: Koblitz-only drop absent on ordinary → reportable;
    # preregistered null is no drop attributable to Frobenius structure.
    # Shape comparison: ratios near 1 on both arms → null holds.
    p4_koblitz_drop = kob_mean < 0.85
    p4_ordinary_drop = ord_mean < 0.85
    p4_null_holds = not (p4_koblitz_drop and not p4_ordinary_drop)

    # Decide O-* from H-BINSTD-5fdceb using Stage-2 fill-in + Stage-3 P4
    poly = stage2.get("poly_p1_fillin") or []
    rand = stage2.get("random_null") or []
    artifact = stage2.get("outcome") == "O-ARTIFACT" or any(
        (c.get("genuine") or {}).get("lift_agreement") not in (None, 1.0) for c in rand
    )

    band_hits = []
    surprise_l6 = False
    for cell in poly:
        l = cell["l"]
        est = cell.get("spurious_factor_estimated")
        pred = cell.get("predicted_spurious_factor")
        if est is None or not pred:
            continue
        ratio = est / pred
        in_band = (1 / 4) <= ratio <= 4
        band_hits.append({"l": l, "est": est, "pred": pred, "ratio_to_pred": ratio, "in_band": in_band})
        if l == 6 and est > 0 and (est / pred) < (1 / 8) and est < 8:
            # near 1 relative to predicted huge factor: treat as surprise if est ~ O(1)
            surprise_l6 = est <= 8

    p3_oks = [c.get("P3_ge_poly") for c in rand]
    p3_ok = all(x is True for x in p3_oks if x is not None) and any(x is True for x in p3_oks)

    if artifact:
        outcome = "O-ARTIFACT"
    elif surprise_l6:
        outcome = "O-SURPRISE"
    elif len(band_hits) >= 2 and sum(1 for b in band_hits if not b["in_band"]) >= 2:
        outcome = "O-NEGATIVE"
    elif (
        band_hits
        and all(b["in_band"] for b in band_hits)
        and p3_ok
        and p4_null_holds
    ):
        outcome = "O-POSITIVE"
    elif band_hits and all(b["in_band"] for b in band_hits) and p4_null_holds and not p3_ok:
        # P3 failed while P1 in band
        outcome = "O-NEGATIVE"
    elif not band_hits:
        outcome = "O-IMPEDIMENT"
    else:
        outcome = "O-NEGATIVE"

    p4_summary = {
        "experiment_id": EXPERIMENT_ID,
        "metric": "P4",
        "task_id": TASK_ID,
        "koblitz": {
            "dim_V": 8,
            "g_sigma": bin(G_SIGMA),
            "V_basis": basis_k,
            "orbit_closure_ratio_mean": kob_mean,
            "rows": kob_rows,
        },
        "ordinary_null": {
            "dim_V": 8,
            "V_basis": basis_o,
            "orbit_closure_ratio_mean": ord_mean,
            "rows": ord_rows,
        },
        "p4_null_holds": p4_null_holds,
        "p4_koblitz_drop": p4_koblitz_drop,
        "p4_ordinary_drop": p4_ordinary_drop,
        "outcome": outcome,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage3" / "frobenius-arm-summary.json", p4_summary)
    write_json(
        EXP_ROOT / "stage3" / "p4-comparison.json",
        {
            "koblitz_mean": kob_mean,
            "ordinary_mean": ord_mean,
            "p4_null_holds": p4_null_holds,
            "amazon_bedrock": "NOT SELECTED",
        },
    )

    results = (
        f"# RESULTS — {EXPERIMENT_ID} Stages 2–3\n\n"
        f"**Outcome:** `{outcome}`\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}. Approved: {APPROVED_BY}. Task: {TASK_ID}.\n\n"
        "Stages 0–1 RESULTS.md left immutable (O-STAGES-0-1-COMPLETE).\n\n"
        "## P1 fill-in (sampled e-space, Stage 2)\n\n"
    )
    for cell in poly:
        results += (
            f"- l={cell['l']}: est_spurious={cell.get('spurious_factor_estimated')} "
            f"predicted={cell.get('predicted_spurious_factor')} "
            f"e_hits={cell['e_space']['e_hits']}/{cell['e_space']['n_assignments']}\n"
        )
    results += "\n## P3 random-subspace null\n\n"
    for cell in rand:
        results += (
            f"- l={cell['l']}: dims={cell['dims']} "
            f"P3_ge_poly={cell.get('P3_ge_poly')} "
            f"est_spurious={cell.get('spurious_factor_estimated')} "
            f"lift={cell['genuine']['lift_agreement']}\n"
        )
    results += (
        f"\n## P4 Frobenius arm\n\n"
        f"- Koblitz orbit_closure_ratio_mean={kob_mean}\n"
        f"- Ordinary null mean={ord_mean}\n"
        f"- p4_null_holds={p4_null_holds}\n\n"
        "## Scope\n\n"
        "Stages 2–3 under trial-plan-v2 / TASK-20261002-d8df85. "
        "No Magma/Sage/AUXIN/Bedrock. No ECDLP break. No exponent claim.\n"
        "Amazon Bedrock: NOT SELECTED.\n"
    )
    write_text(EXP_ROOT / "RESULTS-stages2-3.md", results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 3,
        "outcome": outcome,
        "p1_band_hits": band_hits,
        "p3_oks": p3_oks,
        "p4_null_holds": p4_null_holds,
        "koblitz_orbit_closure_ratio_mean": kob_mean,
        "ordinary_orbit_closure_ratio_mean": ord_mean,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "schema": "crypto.autoresearch.run_manifest.v1",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 3,
            "outcome": outcome,
            "frozen": True,
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    print(json.dumps({"stage": 3, "outcome": outcome, "p4_null_holds": p4_null_holds}, sort_keys=True))
    return raw
