#!/usr/bin/env python3
"""EXP-BINSTD-38f216 Stages 0-2 driver.

Observations only. The frozen prediction is not edited. Bands are comparison
statistics, not a hypothesis verdict.

Relation-phase total, locked before any Stage 2 number is read back:

    coverage_per_pair_sum = n_covered / n_pairs
    total(arm) = (R_need / coverage_per_pair_sum) * cost_per_attempt
    cost_per_attempt = 1
    R_need(V_W) = iota-orbit count of the enumerated x-set
    R_need(matched) = cardinality of the matched subspace (x-set)
    relation_phase_total_ratio = total(V_W) / total(matched)

Certificate comparison:

    Exhaustive multiset counts subgroup sums R = P+Q over unordered distinct
    pairs from the full point set.
    Orbit loop takes one point from each {P, P+T} pair. Each unordered pair
    of those representatives is one operation and contributes A+B and A+B+T,
    each with multiplicity 2. expanded_multiset_equality is that prediction
    against the exhaustive multiset. Random pairing uses shuffled points
    instead of T-orbits and runs the same expansion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import resource
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_curve import (  # noqa: E402
    Curve,
    Field,
    complete_basis,
    gaussian_binomial,
    iter_rref_bases,
    lift_quotient_basis,
    rho_group_ops,
    rref_basis,
    span_elements,
)

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-BINSTD-38f216"
AUDIT = ROOT / "analysis" / "binstd-curve-audit" / "audit-scan.txt"
COMMIT = "c1a6a657daca5f3289999f0a4bf608104fe2b66c"
CENSUS_N = [6, 7, 8, 9, 10, 11, 12, 13]
EXHAUSTIVE_CAP = 1_500_000
SAMPLE_HIGHER = 256
SEED = 20260926
N17_MOD = (1 << 17) | (1 << 3) | 1
KOBLITZ_ORDER = 2 * 65587
M2 = 2
L8 = 8

INFERENCE = {
    "requested_policy": "executor-implementation",
    "canonical_policy": "executor-implementation",
    "backend": None,
    "provider": None,
    "resolved_model_id": None,
    "model_provenance": "unbound",
    "model_verified": False,
    "requested_reasoning_effort": None,
    "reasoning_effort": None,
    "fallback_used": True,
    "fallback_reason": (
        "This executor process did not expose a probe-verified model id. "
        "A local `python3 -m orchestration.adapter resolve --role executor` "
        "printed anthropic:claude-sonnet-5; that identifier was not probe-verified "
        "and is not recorded as the model that produced these artifacts. "
        "No Bedrock endpoint was contacted. degraded_allowed is false."
    ),
    "degraded_requirements": [],
    "degraded_allowed": False,
    "independent_session": False,
    "adapter_version": None,
    "config_digest": None,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def peak_rss_bytes() -> int:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(rss)
    return int(rss) * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git_dirty_paths() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["<git status failed>"]
    return [line for line in out.splitlines() if line.strip()]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def is_stable(basis: tuple[int, ...], curve: Curve) -> bool:
    f = curve.field
    sqrt_b = curve.sqrt_b
    elems = span_elements(basis)
    have = set(elems)
    for v in elems:
        if v == 0:
            continue
        if f.mul(sqrt_b, f.inv(v)) not in have:
            return False
    return True


def enumerate_stable(curve: Curve, k: int, cap: int) -> dict:
    """Enumerate k-dim subspaces containing b^{1/4}. k==n is the whole space."""
    field = curve.field
    n = field.n
    beta = curve.fourth_b
    if k == n:
        # The whole space is the unique n-dimensional subspace. iota permutes F^*.
        ok = True
        checked = 0
        for x in range(1, field.q):
            y = curve.iota(x)
            if y == 0 or y >= field.q:
                ok = False
                break
            checked += 1
            if checked > 8 and n > 13:
                break
        return {
            "k": k,
            "mode": "whole_space",
            "tested": 1,
            "stable_basis": [list(rref_basis(span_elements(complete_basis(n, beta))))] if ok else [],
            "stable_count": 1 if ok else 0,
            "gaussian_containing_beta": 1,
            "cap": cap,
        }
    if k < 1:
        return {"k": k, "mode": "empty", "tested": 0, "stable_count": 0, "stable_basis": []}
    g = gaussian_binomial(n - 1, k - 1)
    full_basis = complete_basis(n, beta)
    stable = []
    tested = 0
    mode = "exhaustive_containing_beta"
    if g > cap and k > 3:
        mode = "sample_containing_beta"
        rng = random.Random(SEED + 10007 * n + 17 * k + curve.b)
        target = min(SAMPLE_HIGHER, g)
        seen = set()
        attempts = 0
        while tested < target and attempts < target * 80:
            attempts += 1
            rows = []
            guard = 0
            while len(rows) < k - 1 and guard < 4000:
                guard += 1
                v = rng.randrange(1 << (n - 1))
                rows.append(v)
                if _rank_lowdim(rows) < len(rows):
                    rows.pop()
            if len(rows) < k - 1:
                continue
            ident = tuple(sorted(rows))
            if ident in seen:
                continue
            seen.add(ident)
            basis = lift_quotient_basis(tuple(rows), full_basis)
            tested += 1
            if is_stable(basis, curve):
                stable.append(list(rref_basis(span_elements(basis))))
        return {
            "k": k,
            "mode": mode,
            "tested": tested,
            "attempts": attempts,
            "stable_count": len(stable),
            "stable_basis": stable,
            "gaussian_containing_beta": g,
            "cap": cap,
            "exhaustive": False,
        }
    for qrows in iter_rref_bases(n - 1, k - 1):
        basis = lift_quotient_basis(qrows, full_basis)
        tested += 1
        if is_stable(basis, curve):
            stable.append(list(rref_basis(span_elements(basis))))
    return {
        "k": k,
        "mode": mode,
        "tested": tested,
        "stable_count": len(stable),
        "stable_basis": stable,
        "gaussian_containing_beta": g,
        "cap": cap,
        "exhaustive": True,
    }


def _rank_lowdim(rows: list[int]) -> int:
    piv = {}
    for v in rows:
        x = v
        for p in sorted(piv, reverse=True):
            if (x >> p) & 1:
                x ^= piv[p]
        if x == 0:
            continue
        p = x.bit_length() - 1
        for q, row in list(piv.items()):
            if (row >> p) & 1:
                piv[q] = row ^ x
        piv[p] = x
    return len(piv)


def predicted_vd(curve: Curve, d: int) -> list[int]:
    field = curve.field
    beta = curve.fourth_b
    return [field.mul(beta, s) for s in field.subfield_elements(d)]


def basis_id(elems: list[int]) -> list[int]:
    return list(rref_basis(elems))


def census_cell(curve: Curve, b_label: str) -> dict:
    field = curve.field
    n = field.n
    divisors = field.divisors()
    predicted = {}
    predicted_ids = []
    for d in divisors:
        elems = predicted_vd(curve, d)
        bid = basis_id(elems)
        stable = is_stable(tuple(bid), curve)
        contains_b = field.in_subfield(curve.b, d)
        predicted[str(d)] = {
            "dimension": d,
            "cardinality": len(elems),
            "iota_stable_measured": stable,
            "is_subfield_containing_b": contains_b and set(elems) == set(field.subfield_elements(d)),
            "b_in_F_2_d": contains_b,
            "basis": bid,
        }
        predicted_ids.append(bid)
    found = []
    dim_reports = []
    t0 = time.perf_counter()
    for k in range(1, n + 1):
        # Dim <= 3 is exhaustive (contract). Higher dims are exhaustive only
        # under EXHAUSTIVE_CAP; otherwise a seeded sample.
        cap = 10**12 if k <= 3 else EXHAUSTIVE_CAP
        rep = enumerate_stable(curve, k, cap)
        # Drop bulky bases from the per-dim report; keep them for the match.
        bases = rep.pop("stable_basis")
        rep["stable_basis_count_kept"] = len(bases)
        dim_reports.append(rep)
        for bse in bases:
            found.append(bse)
    found_ids = {tuple(b) for b in found}
    pred_ids = {tuple(b) for b in predicted_ids}
    # Whole-space and other predicted spaces of non-enumerated dims may be
    # missing from a sample. Count extras only inside exhaustive dimensions.
    exhaustive_dims = {r["k"] for r in dim_reports if r.get("exhaustive") or r.get("mode") == "whole_space"}
    found_ex = []
    for bse in found:
        dim = len(bse)
        if dim in exhaustive_dims or any(r["k"] == dim and r.get("exhaustive") for r in dim_reports):
            found_ex.append(tuple(bse))
    found_ex_set = set(found_ex)
    pred_ex = {tuple(b) for b in predicted_ids if len(b) in exhaustive_dims or len(b) == n}
    # k==n report uses mode whole_space and exhaustive may be absent.
    for r in dim_reports:
        if r.get("mode") == "whole_space":
            exhaustive_dims.add(r["k"])
    pred_ex = {tuple(b) for b in predicted_ids if len(b) in exhaustive_dims}
    found_ex_set = set()
    for bse in found:
        if len(bse) in exhaustive_dims:
            found_ex_set.add(tuple(bse))
    extras = found_ex_set - pred_ex
    missing = pred_ex - found_ex_set
    original_divisors = [d for d in divisors if field.in_subfield(curve.b, d)]
    original_dim_le_3 = [d for d in original_divisors if d <= 3]
    # Every F_2-line is {0, v} for a unique nonzero v. Counting stable lines
    # does not use the beta filter.
    unfiltered_dim1 = sum(1 for v in range(1, field.q) if is_stable((v,), curve))
    dim_le_3_stable = 0
    for r in dim_reports:
        if r["k"] <= 3:
            dim_le_3_stable += r["stable_count"]
    return {
        "n": n,
        "b": curve.b,
        "b_label": b_label,
        "b_poly": field.poly_str(curve.b),
        "modulus": field.modulus_str(),
        "divisors": divisors,
        "tau_n": len(divisors),
        "predicted_by_divisor": predicted,
        "original_lemma_divisor_count": len(original_divisors),
        "original_lemma_divisors": original_divisors,
        "original_lemma_dim_le_3_count": len(original_dim_le_3),
        "dimensions": dim_reports,
        "iota_stable_subspace_count_exhaustive_dims": len(found_ex_set),
        "exhaustive_dims": sorted(exhaustive_dims),
        "predicted_present_in_exhaustive_dims": len(pred_ex),
        "extra_stable_in_exhaustive_dims": len(extras),
        "missing_predicted_in_exhaustive_dims": len(missing),
        "unfiltered_dim1_stable": unfiltered_dim1,
        "iota_stable_subspace_count_dim_le_3": dim_le_3_stable,
        "all_predicted_vd_iota_stable": all(v["iota_stable_measured"] for v in predicted.values()),
        "wall_s_cell": time.perf_counter() - t0,
        "measured_vs_modeled": {
            "iota_stable_subspace_count_dim_le_3": "measured",
            "tau_n": "modeled_from_divisors",
            "original_lemma_divisor_count": "computed_from_subfield_test",
        },
    }


def unfiltered_dim_le_3(curve: Curve) -> int:
    """Full RREF census, no beta filter. Used only as an instrument check at n=6."""
    n = curve.field.n
    count = 0
    for k in range(1, min(3, n) + 1):
        for rows in iter_rref_bases(n, k):
            if is_stable(rows, curve):
                count += 1
    return count


def b_values_for(field: Field) -> list[tuple[int, str]]:
    out = [(1, "b=1")]
    # Primitive element: in no proper subfield.
    out.append((field.generator, "primitive_generator"))
    if field.n % 2 == 0:
        sub = field.subfield_elements(2)
        outside_f2 = [x for x in sub if x not in (0, 1)]
        if not outside_f2:
            raise RuntimeError("F_4 element missing")
        out.append((outside_f2[0], "F_4_minus_F_2"))
    return out


def self_check() -> dict:
    t0 = time.perf_counter()
    field = Field(6)
    sub = field.subfield_elements(2)
    b = [x for x in sub if x not in (0, 1)][0]
    curve = Curve(field, a=1, b=b)
    if field.pow(field.fourth_root(b), 4) != b:
        raise RuntimeError("fourth root failed")
    if field.mul(b, field.inv(b)) != 1:
        raise RuntimeError("inverse failed")
    # trace mask agrees with the definition on a sample
    for x in (1, 2, 3, 5, b, field.generator):
        if field.trace(x) != field.trace_define(x):
            raise RuntimeError(f"trace mismatch at {x}")
    unfiltered = unfiltered_dim_le_3(curve)
    cell = census_cell(curve, "F_4_minus_F_2")
    # x(P+T) on every affine point
    checked = 0
    failed = 0
    for x in range(field.q):
        for pt in curve.points_at_x(x):
            sm = curve.add(pt, (0, curve.sqrt_b))
            checked += 1
            if pt[0] == 0:
                if sm is not None:
                    failed += 1
                continue
            if sm is None or sm[0] != curve.iota(pt[0]):
                failed += 1
    ok = (
        unfiltered == 3
        and cell["iota_stable_subspace_count_dim_le_3"] == 3
        and cell["tau_n"] == 4
        and cell["all_predicted_vd_iota_stable"]
        and cell["original_lemma_dim_le_3_count"] == 1
        and cell["extra_stable_in_exhaustive_dims"] == 0
        and failed == 0
        and checked > 0
    )
    return {
        "ok": ok,
        "n": 6,
        "b": b,
        "unfiltered_dim_le_3_stable": unfiltered,
        "filtered_dim_le_3_stable": cell["iota_stable_subspace_count_dim_le_3"],
        "tau_n": cell["tau_n"],
        "original_dim_le_3": cell["original_lemma_dim_le_3_count"],
        "extras": cell["extra_stable_in_exhaustive_dims"],
        "missing": cell["missing_predicted_in_exhaustive_dims"],
        "x_P_plus_T_checked": checked,
        "x_P_plus_T_failed": failed,
        "wall_s": time.perf_counter() - t0,
        "review_fixture": "n=6, b in F_4\\F_2, dim<=3 stable count 3; original dim<=3 count 1",
    }


def load_audit_rows() -> list[dict]:
    rows = []
    for line in AUDIT.read_text().splitlines():
        parts = line.split()
        if len(parts) < 6:
            continue
        name = parts[0]
        if not (name.startswith("sect") or name.startswith("c2")):
            continue
        if not parts[1].isdigit():
            continue
        def cell(v: str):
            return None if v == "-" else int(v) if v.lstrip("-").isdigit() else v
        rows.append({
            "curve": name,
            "n": int(parts[1]),
            "n_prime": parts[2] == "True",
            "A_in": cell(parts[3]),
            "B_in": cell(parts[4]),
            "cofactor_audit": int(parts[5]),
            "source": "analysis/binstd-curve-audit/audit-scan.txt",
        })
    return rows


def stage0_table() -> dict:
    rows_out = []
    for row in load_audit_rows():
        n = row["n"]
        prime = row["n_prime"]
        b_in = row["B_in"]
        if prime:
            verdict = "STRUCTURALLY_EMPTY"
            named = [1, n]
            reason = "corrected lemma + primality of n; nonzero iota-stable subspaces are dim 1 and dim n only"
        else:
            if n % 16 != 0:
                verdict = "OPEN"
                k = None
                named = []
                reason = "composite degree not of the form 16k in this audit row; cell left OPEN, V_d not named from the 16k pattern"
            else:
                k = n // 16
                named = [1, 2, 4, 8, k, 2 * k, 4 * k, 8 * k]
                # unique, and each must divide n
                named = sorted(set(named))
                verdict = "OPEN"
                reason = (
                    "composite 16k row; V_d = b^{1/4} F_{2^d} for d in {1,2,4,8,k,2k,4k,8k} "
                    "are the named scaled-subfield objects; cell not closed"
                )
        vd = []
        for d in named:
            if n % d != 0:
                b_in_d = None
                subfield = None
            else:
                if b_in is None:
                    b_in_d = d == n
                else:
                    b_in_d = (int(b_in) % d == 0) if False else (d % int(b_in) == 0)
                # b lies in F_{2^{B_in}} and hence in F_{2^d} iff B_in divides d.
                # B_in is the smallest such degree from the audit. d == n always works
                # when B_in is None (b in no proper subfield).
                subfield = bool(b_in_d)
            vd.append({
                "d": d,
                "divides_n": n % d == 0,
                "b_in_F_2_d_from_audit_B_in": b_in_d,
                "V_d_is_subfield_iff_b_in_F_2_d": subfield,
            })
        rows_out.append({
            **row,
            "verdict": verdict,
            "reason": reason,
            "named_d": named,
            "V_d": vd,
            "kind": "structural_verdict_from_lemma_plus_audit_degree",
            "not_a_measured_attack_cost": True,
        })
    rows_out.append({
        "curve": "ECC2K-130",
        "n": 131,
        "n_prime": True,
        "A_in": 1,
        "B_in": 1,
        "cofactor_audit": None,
        "source": "hypothesis H-BINSTD-dba2ab statement and review ecc2k130_bearing; not a row of audit-scan.txt",
        "verdict": "STRUCTURALLY_EMPTY",
        "reason": "n=131 prime and b=1; corrected lemma gives only {0,1}=F_2 and the whole field",
        "named_d": [1, 131],
        "V_d": [
            {"d": 1, "divides_n": True, "b_in_F_2_d_from_audit_B_in": True, "V_d_is_subfield_iff_b_in_F_2_d": True},
            {"d": 131, "divides_n": True, "b_in_F_2_d_from_audit_B_in": True, "V_d_is_subfield_iff_b_in_F_2_d": True},
        ],
        "kind": "structural_verdict_from_lemma_plus_stated_prime_degree",
        "not_a_measured_attack_cost": True,
    })
    return {"rows": rows_out, "row_count": len(rows_out)}


LEMMA = """# Corrected iota-stable subspace lemma (Stage 0)

Source of the correction: `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-29b1c5.yaml`,
frozen into H-BINSTD-dba2ab / EXP-BINSTD-38f216 by DEC-20260930-492bf6.
This note writes the corrected steps the contract requires. It is not a new
status change and it does not say the hypothesis is supported.

## Setting

E: y^2 + x y = x^3 + a x^2 + b over F_{2^n}, b != 0. The unique rational
2-torsion point is T = (0, sqrt(b)).

## Step A — translation identity

For an affine point P = (x, y) with x != 0,

    x(P + T) = sqrt(b) / x.

Write iota(x) = sqrt(b) / x on F^*. Squaring is bijective on F_{2^n}, so
iota has exactly one fixed point, beta = b^{1/4}, the unique solution of
x^2 = sqrt(b).

## Step B — corrected classification

Let V be a nonzero F_2-subspace of F_{2^n} with iota(V \\ {0}) = V \\ {0}.

The nonzero cardinality 2^{dim V} - 1 is odd, and every iota-orbit in F^* has
size 2 except {beta}. Therefore beta lies in V.

The review's corrected stabilizer argument, copied as the Stage 0 steps:

1. For nonzero u, w in V the hypothesis of the original proof produced
   u^2 / w in V. Combined with iota-stability, 1/V = V / sqrt(b), so the
   stabilizer S = {lambda : lambda V = V} contains u^2 / sqrt(b), not u^2.
2. (u/v)^2 lies in S for nonzero u, v in V. Squaring is a bijection of F^*,
   so u/v lies in S.
3. K = span(S) is a subfield F_{2^d}. V = c K for any nonzero c in V.
4. iota-stability forces sqrt(b) / c^2 in K, hence V = b^{1/4} F_{2^d}.

So the nonzero iota-stable F_2-subspaces are exactly

    V_d = b^{1/4} F_{2^d}

for the divisors d of n, one each. V_d is a subfield if and only if b lies in
F_{2^d}.

## Prime rows

If n is prime the only nonzero stable subspaces are

- dim 1: {0, b^{1/4}}, size 2 (equal to F_2 exactly when b = 1),
- dim n: the whole field.

The (subspace factor base, 2-torsion quotient) cell is recorded as
STRUCTURALLY EMPTY on those rows. The certificate used here is this
classification together with primality of n. That is a structural verdict,
not a measured attack cost.

## Composite rows

For the five audit rows with n = 16k, the subspaces V_d for

    d in {1, 2, 4, 8, k, 2k, 4k, 8k}

are the named objects. Those with b not in F_{2^d} are not subfields. The
cell is recorded OPEN. Pricing that object is outside this experiment.

## What Stage 0 does not say

No exponent moves. No claim that a deployed curve's cost changed. The
per-row table is the classification above applied to degrees in
`analysis/binstd-curve-audit/audit-scan.txt`, plus the ECC2K-130 row named
in the hypothesis (n = 131, b = 1), which is not a line of that scan.
"""


def element_in_subspace(x: int, basis: tuple[int, ...]) -> bool:
    y = x
    for b in basis:
        hb = b.bit_length() - 1
        if hb >= 0 and (y >> hb) & 1:
            y ^= b
    return y == 0


def random_subspace(field: Field, dim: int, rng: random.Random) -> tuple[int, ...]:
    rows: list[int] = []
    guard = 0
    while len(rows) < dim and guard < 10000:
        guard += 1
        trial = rref_basis(rows + [rng.randrange(field.q)])
        if len(trial) == len(rows) + 1:
            rows = list(trial)
    if len(rows) != dim:
        raise RuntimeError(f"failed to sample a {dim}-dimensional subspace")
    return tuple(rows)


def vw_x_set(curve: Curve, w_basis: tuple[int, ...]) -> dict:
    field = curve.field
    xs = []
    t_hits = 0
    sqrt_b = curve.sqrt_b
    for w in span_elements(w_basis):
        if w == 0:
            continue
        if field.trace(field.mul(sqrt_b, field.inv(field.square(w)))) == 0:
            t_hits += 1
    for x in range(1, field.q):
        if element_in_subspace(curve.u_coord(x), w_basis):
            xs.append(x)
    orbits = {}
    for x in xs:
        ix = curve.iota(x)
        key = min(x, ix)
        orbits.setdefault(key, set()).add(x)
        if ix in xs or ix == x:
            orbits[key].add(ix)
    # orbits may point outside xs only if u-set is not closed; record that
    closed = all(curve.iota(x) in xs for x in xs if curve.iota(x) != x or True)
    closed = all(curve.iota(x) in set(xs) for x in xs)
    return {
        "x_values": xs,
        "cardinality": len(xs),
        "trace_hits_W_nonzero": t_hits,
        "one_plus_twice_trace_hits": 1 + 2 * t_hits,
        "identity_holds": len(xs) == 1 + 2 * t_hits,
        "orbit_count": len(orbits),
        "orbit_size_1": sum(1 for s in orbits.values() if len(s) == 1),
        "iota_closed": closed,
        "representatives": sorted(orbits),
    }


def points_from_x(curve: Curve, xs: list[int]) -> list[tuple[int, int]]:
    pts = []
    xset = set(xs)
    for x in xset:
        pts.extend(curve.points_at_x(x))
    return pts


def subgroup_points(curve: Curve, r: int) -> set[tuple[int, int]]:
    field = curve.field
    out = set()
    for x in range(field.q):
        for pt in curve.points_at_x(x):
            if curve.mul_scalar(r, pt) is None:
                out.add(pt)
    return out


def pair_tally(curve: Curve, points: list[tuple[int, int]], subgroup: set[tuple[int, int]]) -> dict:
    counts: Counter[tuple[int, int]] = Counter()
    n_pairs = 0
    n = len(points)
    add = curve.add
    for i in range(n):
        pi = points[i]
        for j in range(i + 1, n):
            s = add(pi, points[j])
            n_pairs += 1
            if s is not None and s in subgroup:
                counts[s] += 1
    n_covered = len(counts)
    total = int(sum(counts.values()))
    return {
        "n_points": n,
        "n_pairs": n_pairs,
        "n_covered": n_covered,
        "decomposition_instances": total,
        "multiplicity_per_covered_target": (total / n_covered) if n_covered else None,
        "coverage_per_pair_sum": (n_covered / n_pairs) if n_pairs else None,
        "max_decompositions_one_target": max(counts.values()) if counts else 0,
        "counts": counts,
    }


def arm_total(r_need: int, coverage_per_pair_sum: float | None) -> float | None:
    if coverage_per_pair_sum is None or coverage_per_pair_sum == 0:
        return None
    return (r_need / coverage_per_pair_sum) * 1.0


def point_t_reps(curve: Curve, points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """One affine point from each {P, P+T} pair."""
    t_pt = (0, curve.sqrt_b)
    used: set[tuple[int, int]] = set()
    reps = []
    for p in points:
        if p in used:
            continue
        q = curve.add(p, t_pt)
        used.add(p)
        if q is not None:
            used.add(q)
        reps.append(p)
    return reps


def orbit_loop_expand(curve: Curve, reps: list[tuple[int, int]], subgroup: set[tuple[int, int]]) -> tuple[Counter, int]:
    """One operation per unordered rep pair emits R=A+B and A+B+T, each with exhaustive multiplicity 2.

    Checked against a full pair tally on one debug window before the official runs:
    the resulting multiset matched. A rep set that is not the true T-orbits does not.
    """
    t_pt = (0, curve.sqrt_b)
    pred: Counter = Counter()
    n_ops = 0
    for i, a in enumerate(reps):
        for b in reps[i + 1 :]:
            n_ops += 1
            r = curve.add(a, b)
            bt = curve.add(b, t_pt)
            rt = curve.add(a, bt) if bt is not None else None
            if r is not None and r in subgroup:
                pred[r] += 2
            if rt is not None and rt in subgroup:
                pred[rt] += 2
    return pred, n_ops


def certificate_from_expansion(full_counts: Counter, expanded: Counter, n_ops: int) -> dict:
    return {
        "expanded_multiset_equality": expanded == full_counts,
        "support_equality": set(expanded) == set(full_counts),
        "full_support": len(full_counts),
        "orbit_support": len(expanded),
        "orbit_loop_operations": n_ops,
        "exhaustive_decomposition_instances": int(sum(full_counts.values())),
        "expansion_rule": "point reps of {P,P+T}; each rep pair emits A+B and A+B+T with multiplicity 2",
    }


def fake_orbit_reps(xs: list[int], curve: Curve, rng: random.Random) -> list[int]:
    """Pair distinct x-values arbitrarily, refusing the true iota partner."""
    pool = xs[:]
    rng.shuffle(pool)
    used = set()
    reps = []
    by_x = set(xs)
    for x in pool:
        if x in used:
            continue
        partner = curve.iota(x)
        # choose a unused y != x, != partner if possible
        y = None
        for cand in pool:
            if cand in used or cand == x:
                continue
            if cand != partner:
                y = cand
                break
        used.add(x)
        if y is None:
            reps.append(x)
            continue
        used.add(y)
        reps.append(x)
    return reps


def koblitz_tau_bar_check(curve: Curve, points_all_sample: list[tuple[int, int]]) -> dict:
    failed = 0
    checked = 0
    for pt in points_all_sample:
        if pt[0] == 0:
            continue
        doubled = curve.add(pt, pt)
        checked += 1
        if doubled is None:
            failed += 1
            continue
        x_tb = curve.field.sqrt(doubled[0])
        if x_tb != curve.u_coord(pt[0]):
            failed += 1
    return {"checked": checked, "failed": failed, "identity": "x(tau_bar P)=x+sqrt(b)/x via sqrt(x(2P))"}


def one_w_measurement(curve: Curve, subgroup: set[tuple[int, int]], r_group: int, w_index: int, kind: str) -> dict:
    field = curve.field
    rng_w = random.Random(SEED + 100003 * w_index + (0 if kind == "koblitz" else 17))
    w_basis = random_subspace(field, L8, rng_w)
    vw = vw_x_set(curve, w_basis)
    if not vw["identity_holds"]:
        return {
            "w_index": w_index,
            "termination_reason": "invalid_measurement",
            "reason": "|V_W| != 1 + 2 * trace hits; instrument check failed",
            "vw": {k: vw[k] for k in vw if k not in {"x_values", "representatives"}},
        }
    pts_vw = points_from_x(curve, vw["x_values"])
    dim_match = max(1, min(field.n - 1, int(round(math_log2(max(vw["cardinality"], 2))))))
    rng_m = random.Random(SEED + 200003 * w_index + 9 + (0 if kind == "koblitz" else 19))
    m_basis = random_subspace(field, dim_match, rng_m)
    xs_m = [x for x in span_elements(m_basis) if x != 0]
    # cardinality match is impossible unless |V_W| is a power of two; record both
    pts_m = points_from_x(curve, xs_m)
    tally_vw = pair_tally(curve, pts_vw, subgroup)
    tally_m = pair_tally(curve, pts_m, subgroup)
    reps = point_t_reps(curve, pts_vw)
    expanded, n_ops = orbit_loop_expand(curve, reps, subgroup)
    cert = certificate_from_expansion(tally_vw["counts"], expanded, n_ops)
    # random pairing: adjacent points after a shuffle, not T-orbits
    rng_p = random.Random(SEED + 300011 * w_index + 4)
    shuffled = pts_vw[:]
    rng_p.shuffle(shuffled)
    fake_reps = shuffled[::2]
    fake_expanded, fake_ops = orbit_loop_expand(curve, fake_reps, subgroup)
    cert_fake = certificate_from_expansion(tally_vw["counts"], fake_expanded, fake_ops)
    r_vw = vw["orbit_count"]
    r_m = len(xs_m)
    tot_vw = arm_total(r_vw, tally_vw["coverage_per_pair_sum"])
    tot_m = arm_total(r_m, tally_m["coverage_per_pair_sum"])
    ratio = (tot_vw / tot_m) if tot_vw is not None and tot_m not in (None, 0) else None
    out = {
        "w_index": w_index,
        "seed_w": SEED + 100003 * w_index + (0 if kind == "koblitz" else 17),
        "seed_matched": SEED + 200003 * w_index + 9 + (0 if kind == "koblitz" else 19),
        "W_basis": list(w_basis),
        "V_W_cardinality": vw["cardinality"],
        "V_W_over_2_l": vw["cardinality"] / (1 << L8),
        "trace_hits_W_nonzero": vw["trace_hits_W_nonzero"],
        "one_plus_twice_trace_hits": vw["one_plus_twice_trace_hits"],
        "trace_identity_holds": vw["identity_holds"],
        "orbit_count": vw["orbit_count"],
        "orbit_size_1": vw["orbit_size_1"],
        "iota_closed": vw["iota_closed"],
        "matched_dimension": dim_match,
        "matched_x_cardinality": len(xs_m),
        "matched_cardinality_note": "subspace sizes are powers of two; dimension is round(log2(|V_W|))",
        "V_W": strip_counts(tally_vw),
        "orbit_loop_operations": n_ops,
        "exhaustive_pairs": tally_vw["n_pairs"],
        "operation_count_ratio_orbit_over_exhaustive": (n_ops / tally_vw["n_pairs"]) if tally_vw["n_pairs"] else None,
        "matched_subspace": strip_counts(tally_m),
        "R_need_V_W": r_vw,
        "R_need_matched": r_m,
        "total_V_W": tot_vw,
        "total_matched": tot_m,
        "relation_phase_total_ratio": ratio,
        "relation_phase_total_ratio_label": "measured",
        "predicted_ratio_modeled": 0.5,
        "certificate_orbit_loop": cert,
        "random_pairing_certificate": {
            "expanded_multiset_equality": cert_fake["expanded_multiset_equality"],
            "support_equality": cert_fake["support_equality"],
            "control": "known-false pairing; expanded multiset equality is expected to be false",
        },
        "termination_reason": "completed",
    }
    return out


def math_log2(x: int) -> float:
    return x.bit_length() - 1 + math_frac(x)


def math_frac(x: int) -> float:
    # crude log2 fractional part via float, exact enough for round()
    import math
    return math.log2(x) - (x.bit_length() - 1)


def strip_counts(tally: dict) -> dict:
    return {k: v for k, v in tally.items() if k != "counts"}


def mean(xs: list[float]) -> float | None:
    if not xs:
        return None
    return sum(xs) / len(xs)


def stage2_cell(kind: str) -> dict:
    field = Field(17, N17_MOD)
    if kind == "koblitz":
        a, b = 1, 1
        expected = KOBLITZ_ORDER
    elif kind == "rc1":
        a, b = 97044, 126251
        expected = None
    else:
        raise ValueError(kind)
    curve = Curve(field, a, b)
    if field.modulus != N17_MOD:
        raise RuntimeError("modulus drifted")
    order, order2 = curve.count_points()
    if order != order2:
        return {
            "kind": kind,
            "termination_reason": "invalid_measurement",
            "reason": "two point-count methods disagreed",
            "order_trace": order,
            "order_image": order2,
        }
    if expected is not None and order != expected:
        return {
            "kind": kind,
            "termination_reason": "invalid_measurement",
            "reason": "recomputed #E disagreed with the contract figure 2*65587",
            "order": order,
            "expected": expected,
        }
    # odd part
    r = order
    cofactor_2 = 0
    while r % 2 == 0:
        r //= 2
        cofactor_2 += 1
    # trial prime test
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        d = 3
        while d * d <= n:
            if n % d == 0:
                return False
            d += 2
        return True
    r_prime = is_prime(r)
    subgroup = subgroup_points(curve, r)
    ident = koblitz_tau_bar_check(curve, list(subgroup)[:5000] if kind != "koblitz" else list(subgroup))
    # For Koblitz, check the identity on all subgroup points (about 65k). That
    # is the contract's "on all points" as far as the prime-order subgroup.
    # Also check every affine point's x-identity via a direct loop limited to
    # all x, which is the literal reading.
    all_fail = 0
    all_checked = 0
    if kind == "koblitz":
        for x in range(1, field.q):
            for pt in curve.points_at_x(x):
                doubled = curve.add(pt, pt)
                all_checked += 1
                if doubled is None or field.sqrt(doubled[0]) != curve.u_coord(x):
                    all_fail += 1
    windows = []
    t0 = time.perf_counter()
    for i in range(20):
        windows.append(one_w_measurement(curve, subgroup, r, i, kind))
        if time.perf_counter() - t0 > 1700:
            break
    ratios = [w["relation_phase_total_ratio"] for w in windows if w.get("relation_phase_total_ratio") is not None]
    mults = [
        w["V_W"]["multiplicity_per_covered_target"]
        for w in windows
        if w.get("V_W") and w["V_W"].get("multiplicity_per_covered_target") is not None
    ]
    ratios_vw = [w["V_W_over_2_l"] for w in windows if "V_W_over_2_l" in w]
    cert_ok = [w.get("certificate_orbit_loop", {}).get("expanded_multiset_equality") for w in windows if "certificate_orbit_loop" in w]
    fake_ok = [w.get("random_pairing_certificate", {}).get("expanded_multiset_equality") for w in windows if "random_pairing_certificate" in w]
    # Poisson tail report: max count vs Poisson(lambda = n_pairs / |subgroup|)
    import math
    poisson = []
    for w in windows:
        if "V_W" not in w:
            continue
        n_pairs = w["V_W"]["n_pairs"]
        lam = n_pairs / max(len(subgroup), 1)
        mx = w["V_W"]["max_decompositions_one_target"]
        # P(X >= mx) rough: 1 - cdf, compute pmf sum
        # survival from 0..mx-1
        if lam <= 0:
            surv = None
        else:
            term = math.exp(-lam)
            cdf = term
            for k in range(1, mx):
                term *= lam / k
                cdf += term
                if term < 1e-18 and k > lam:
                    break
            surv = max(0.0, 1.0 - cdf)
        poisson.append({"w_index": w["w_index"], "lambda_pairs_over_subgroup": lam, "max_decompositions": mx, "poisson_sf_at_max": surv})
    k_sym = field.n if kind == "koblitz" else 1
    rho = rho_group_ops(r, k_sym)
    return {
        "kind": kind,
        "a": a,
        "b": b,
        "modulus": field.modulus_str(),
        "order": order,
        "order_methods_agree": True,
        "cofactor_power_of_two": cofactor_2,
        "odd_part_r": r,
        "odd_part_is_prime": r_prime,
        "subgroup_point_count_including_only_kernel": len(subgroup),
        "koblitz_tau_bar_all_affine": {"checked": all_checked, "failed": all_fail} if kind == "koblitz" else None,
        "koblitz_tau_bar_sample": ident,
        "n_W_completed": len(windows),
        "n_W_planned": 20,
        "windows": windows,
        "mean_relation_phase_total_ratio": mean(ratios),
        "mean_multiplicity_V_W": mean(mults),
        "min_V_W_over_2_l": min(ratios_vw) if ratios_vw else None,
        "max_V_W_over_2_l": max(ratios_vw) if ratios_vw else None,
        "orbit_loop_expanded_multiset_equality_counts": {
            "true": sum(1 for v in cert_ok if v is True),
            "false": sum(1 for v in cert_ok if v is False),
        },
        "random_pairing_expanded_multiset_equality_counts": {
            "true": sum(1 for v in fake_ok if v is True),
            "false": sum(1 for v in fake_ok if v is False),
        },
        "comparison_to_frozen_band": {
            "relation_phase_total_ratio_band": [0.4, 0.6],
            "mean_inside_band": (
                None if mean(ratios) is None else 0.4 <= mean(ratios) <= 0.6
            ),
            "multiplicity_band_m2": [1.5, 2.5],
            "mean_multiplicity_inside_band": (
                None if mean(mults) is None else 1.5 <= mean(mults) <= 2.5
            ),
            "V_W_over_2_l_band_H1": [0.7, 1.3],
            "all_windows_inside_H1_band": all(0.7 <= v <= 1.3 for v in ratios_vw) if ratios_vw else None,
            "labels": "comparison statistics against the frozen bands; not a hypothesis verdict",
        },
        "poisson_tail_reported_not_gated": poisson,
        "rho_group_ops_modeled": {
            "value": rho,
            "formula": "sqrt(pi*r/(4k))",
            "r": r,
            "k": k_sym,
            "k_meaning": "k=n Frobenius on Koblitz; k=1 negation-only on the ordinary cell",
            "label": "modeled",
        },
        "optimistic_assumptions_affecting_modeled_rho": [
            "rho figure is a closed-form group-operation estimate, not a wall-clock measurement",
        ],
        "wall_s": time.perf_counter() - t0,
        "termination_reason": "completed" if len(windows) == 20 else "timeout",
    }


def covered_set_koblitz(curve: Curve, subgroup: set[tuple[int, int]], window_index: int = 0) -> dict:
    """One W: covered point-set of V_W versus tau_bar^{-1} of covered set of F_W."""
    field = curve.field
    rng = random.Random(SEED + 100003 * window_index)
    w_basis = random_subspace(field, L8, rng)
    vw = vw_x_set(curve, w_basis)
    xs_w = [x for x in span_elements(w_basis) if x != 0]
    pts_vw = points_from_x(curve, vw["x_values"])
    pts_w = points_from_x(curve, xs_w)
    cov_vw = pair_tally(curve, pts_vw, subgroup)["counts"]
    cov_w = pair_tally(curve, pts_w, subgroup)["counts"]
    # tau_bar^{-1} = [2]^{-1} o Frobenius, with 2^{-1} mod r.
    r = KOBLITZ_ORDER // 2
    inv2 = (r + 1) // 2  # only valid if r odd, which 65587 is
    image = set()
    for s in cov_w:
        fr = (field.square(s[0]), field.square(s[1]))
        image.add(curve.mul_scalar(inv2, fr))
    image.discard(None)
    return {
        "w_index": window_index,
        "covered_vw": len(cov_vw),
        "covered_fw": len(cov_w),
        "tau_bar_inverse_image": len(image),
        "set_equality": set(cov_vw) == image,
        "map": "tau_bar^{-1} = [2]^{-1} o Frobenius, 2^{-1} = (r+1)/2 mod r",
    }


def write_run_package(run_id: str, command: str, started: str, payload: dict, status: str, valid: bool, invalid_reason: str | None) -> Path:
    run_dir = EXP / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    finished = now_iso()
    stdout = payload.get("_stdout", "")
    if stdout and not stdout.endswith("\n"):
        stdout += "\n"
    (run_dir / "stdout.txt").write_text(stdout)
    (run_dir / "stdout.log").write_text(stdout)
    (run_dir / "stderr.log").write_text(payload.get("_stderr", ""))
    (run_dir / "command.txt").write_text(command + "\n")
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "numpy": None,
        "dependencies": {"stdlib_only": True},
        "tmpdir": os.environ.get("TMPDIR"),
    }
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-BINSTD-38f216",
            "status": status,
            "code": {
                "commit": COMMIT,
                "dirty": True,
                "dirty_note": "implementation and run artifacts are uncommitted in the origin/main worktree",
                "command": command,
            },
            "inference": INFERENCE,
            "environment": env,
            "inputs": payload.get("inputs", {}),
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": payload.get("wall_s"),
            },
            "resources": {
                "peak_rss_bytes": peak_rss_bytes(),
                "cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime
                + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
            },
            "result": {
                "metrics": payload.get("metrics_summary", {}),
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "artifacts": {
                "raw-result.json": sha256_file(raw_path),
            },
            "termination_reason": payload.get("termination_reason"),
        }
    }
    (run_dir / "manifest.yaml").write_text(json_to_yaml(manifest) + "\n")
    return run_dir


def json_to_yaml(obj, indent: int = 0) -> str:
    import yaml
    return yaml.safe_dump(obj, sort_keys=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=["self-check", "0", "1", "2"])
    parser.add_argument("--cell", choices=["koblitz", "rc1"], default=None)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    started = now_iso()
    t0 = time.perf_counter()
    command = "python3 " + " ".join(sys.argv)
    stderr = ""
    try:
        if args.stage == "self-check":
            payload = self_check()
            payload["wall_s"] = time.perf_counter() - t0
            payload["termination_reason"] = "completed" if payload["ok"] else "implementation_error"
            payload["inputs"] = {"n": 6, "seed": None, "parameters": {"fixture": "F_4 minus F_2"}}
            payload["metrics_summary"] = {"self_check_ok": payload["ok"]}
            text = json.dumps({k: payload[k] for k in payload if k != "predicted_by_divisor"}, indent=2)
            payload["_stdout"] = text + "\n"
            valid = bool(payload["ok"])
            status = "completed_valid" if valid else "invalid_measurement"
            reason = None if valid else "self-check fixture failed"
        elif args.stage == "0":
            table = stage0_table()
            write_text(EXP / "stage0" / "lemma-writeup.md", LEMMA)
            write_text(EXP / "stage0" / "per-row-verdict-table.yaml", json_to_yaml(table))
            payload = {
                "stage": 0,
                "lemma_path": "experiments/EXP-BINSTD-38f216/stage0/lemma-writeup.md",
                "table_path": "experiments/EXP-BINSTD-38f216/stage0/per-row-verdict-table.yaml",
                "row_count": table["row_count"],
                "verdict_counts": dict(Counter(r["verdict"] for r in table["rows"])),
                "wall_s": time.perf_counter() - t0,
                "termination_reason": "completed",
                "inputs": {"parameters": {"source": str(AUDIT.relative_to(ROOT))}, "seed": None, "curve_id": "audit-scan"},
                "metrics_summary": {"row_count": table["row_count"]},
            }
            payload["_stdout"] = json.dumps(payload["verdict_counts"]) + "\n"
            valid, status, reason = True, "completed_valid", None
        elif args.stage == "1":
            check = self_check()
            if not check["ok"]:
                payload = {
                    "stage": 1,
                    "self_check": check,
                    "termination_reason": "implementation_error",
                    "wall_s": time.perf_counter() - t0,
                    "inputs": {"seed": SEED},
                    "metrics_summary": {},
                    "_stdout": "self-check failed\n",
                }
                valid, status, reason = False, "invalid_measurement", "n=6 fixture failed before census"
            else:
                cells = []
                for n in CENSUS_N:
                    field = Field(n)
                    for b, label in b_values_for(field):
                        curve = Curve(field, a=1, b=b)
                        cell = census_cell(curve, label)
                        # shrink predicted bases in the stored cell? keep them; they are small
                        cells.append(cell)
                        print(f"n={n} {label} dim<=3 {cell['iota_stable_subspace_count_dim_le_3']} extras {cell['extra_stable_in_exhaustive_dims']} wall {cell['wall_s_cell']:.2f}", flush=True)
                summary = {
                    "cells": [
                        {
                            "n": c["n"],
                            "b": c["b"],
                            "b_label": c["b_label"],
                            "tau_n": c["tau_n"],
                            "iota_stable_subspace_count_dim_le_3": c["iota_stable_subspace_count_dim_le_3"],
                            "iota_stable_subspace_count_exhaustive_dims": c["iota_stable_subspace_count_exhaustive_dims"],
                            "extra_stable_in_exhaustive_dims": c["extra_stable_in_exhaustive_dims"],
                            "missing_predicted_in_exhaustive_dims": c["missing_predicted_in_exhaustive_dims"],
                            "original_lemma_divisor_count": c["original_lemma_divisor_count"],
                            "original_lemma_dim_le_3_count": c["original_lemma_dim_le_3_count"],
                            "all_predicted_vd_iota_stable": c["all_predicted_vd_iota_stable"],
                            "exhaustive_dims": c["exhaustive_dims"],
                            "wall_s_cell": c["wall_s_cell"],
                        }
                        for c in cells
                    ]
                }
                write_text(EXP / "stage1" / "census-summary.json", json.dumps(summary, indent=2) + "\n")
                payload = {
                    "stage": 1,
                    "self_check": check,
                    "census_summary_path": "experiments/EXP-BINSTD-38f216/stage1/census-summary.json",
                    "cells": cells,
                    "wall_s": time.perf_counter() - t0,
                    "termination_reason": "completed",
                    "inputs": {
                        "seed": SEED,
                        "parameters": {"n": CENSUS_N, "exhaustive_cap_above_dim3": EXHAUSTIVE_CAP},
                        "curve_id": "F_2^n polynomial basis, lowest irreducible except where noted",
                    },
                    "metrics_summary": {
                        "n_cells": len(cells),
                        "cells_with_extra_stable": sum(1 for c in cells if c["extra_stable_in_exhaustive_dims"]),
                        "cells_missing_predicted": sum(1 for c in cells if c["missing_predicted_in_exhaustive_dims"]),
                    },
                }
                payload["_stdout"] = json.dumps(payload["metrics_summary"]) + "\n"
                valid, status, reason = True, "completed_valid", None
        else:
            if args.cell is None:
                raise SystemExit("stage 2 requires --cell")
            check = self_check()
            if not check["ok"]:
                payload = {
                    "stage": 2,
                    "self_check": check,
                    "termination_reason": "implementation_error",
                    "wall_s": time.perf_counter() - t0,
                    "inputs": {"seed": SEED, "curve_id": args.cell},
                    "metrics_summary": {},
                    "_stdout": "self-check failed\n",
                }
                valid, status, reason = False, "invalid_measurement", "n=6 fixture failed before stage 2"
            else:
                cell = stage2_cell(args.cell)
                extra = None
                if args.cell == "koblitz" and cell.get("termination_reason") == "completed":
                    field = Field(17, N17_MOD)
                    curve = Curve(field, 1, 1)
                    # subgroup already counted; recompute r
                    r = 65587
                    subgroup = subgroup_points(curve, r)
                    extra = covered_set_koblitz(curve, subgroup, 0)
                cell["self_check"] = check
                cell["koblitz_covered_set_one_W"] = extra
                cell["stage"] = 2
                cell["inputs"] = {
                    "seed": SEED,
                    "curve_id": args.cell,
                    "parameters": {"n": 17, "m": M2, "l": L8, "modulus": "t^17+t^3+1", "W": 20},
                }
                # metrics summary without per-window bulk
                cell["metrics_summary"] = {
                    "mean_relation_phase_total_ratio": cell.get("mean_relation_phase_total_ratio"),
                    "mean_multiplicity_V_W": cell.get("mean_multiplicity_V_W"),
                    "min_V_W_over_2_l": cell.get("min_V_W_over_2_l"),
                    "max_V_W_over_2_l": cell.get("max_V_W_over_2_l"),
                    "comparison_to_frozen_band": cell.get("comparison_to_frozen_band"),
                    "order": cell.get("order"),
                    "rho_group_ops_modeled": cell.get("rho_group_ops_modeled"),
                }
                cell["wall_s"] = cell.get("wall_s", time.perf_counter() - t0)
                # stage summary file is written after both cells by the caller; each cell
                # also drops a partial summary.
                partial = EXP / "stage2" / f"{args.cell}-summary.json"
                storable = {k: v for k, v in cell.items() if k not in {"windows", "self_check"}}
                storable["windows_brief"] = [
                    {kk: ww.get(kk) for kk in (
                        "w_index", "V_W_cardinality", "V_W_over_2_l", "orbit_count", "orbit_size_1",
                        "relation_phase_total_ratio", "trace_identity_holds", "termination_reason",
                    )}
                    for ww in cell.get("windows", [])
                ]
                write_text(partial, json.dumps(storable, indent=2) + "\n")
                cell["_stdout"] = json.dumps(cell["metrics_summary"], default=str) + "\n"
                if cell.get("termination_reason") == "invalid_measurement":
                    valid, status, reason = False, "invalid_measurement", cell.get("reason")
                elif cell.get("termination_reason") == "timeout":
                    valid, status, reason = False, "failed_infrastructure", "wall clock stopped the cell before 20 W"
                else:
                    valid, status, reason = True, "completed_valid", None
                payload = cell
        payload["_stderr"] = stderr
        payload.setdefault("wall_s", time.perf_counter() - t0)
        run_dir = write_run_package(args.run_id, command, started, payload, status, valid, reason)
        print(f"run_dir={run_dir} status={status} valid={valid}")
        return 0 if valid else 2
    except Exception:
        stderr = traceback.format_exc()
        payload = {
            "termination_reason": "crash",
            "wall_s": time.perf_counter() - t0,
            "inputs": {"seed": SEED},
            "metrics_summary": {},
            "_stdout": "",
            "_stderr": stderr,
        }
        write_run_package(args.run_id, command, started, payload, "failed_infrastructure", False, "uncaught exception")
        sys.stderr.write(stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
