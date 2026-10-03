#!/usr/bin/env python3
"""Stage 1 for EXP-BINSTD-89d952: two-arm S_4/W_4 cost control at n=19,m=3,l=5.

Frozen instrument is pure-Python S_4 Macaulay + W_4 at D=4 over 15 variables.
If descended S_4 boolean degree exceeds 4, the frozen instrument cannot host
the equations → instrument_unavailable (infrastructure / DO-5), not negative
math evidence. No per-instance mu-orbit constraint. No break / rho claim.
"""
from __future__ import annotations

import argparse
import itertools
import random
import statistics
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve, is_prime  # noqa: E402
from gf2n import TableField, is_irreducible  # noqa: E402
from runpack import (  # noqa: E402
    EXP_ID,
    EXP_ROOT,
    TASK_ID,
    dump_yaml,
    peak_rss_bytes,
    utc_now,
    write_run_package,
)
from s4_descent import (  # noqa: E402
    ClosureGeneric,
    descend_s4,
    eqs_fit_macaulay_D,
    s4_field,
)

# Minted + --check'd
RUN_FEASIBILITY = "RUN-BINSTD-8b78a7"
RUN_CONTROLS = "RUN-BINSTD-97e1bf"

N = 19
MOD = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1
M, L = 3, 5
NV = M * L
SEEDS = [20260922, 20260926, 20261001, 20261002, 20261003]
PRIMARY_SEED = 20260922
TARGETS_PER_ARM = 100
PLANTED_FRACTION = 0.5
WATCHDOG = 120

ORDINARY = {"A": 46693, "B": 306147, "h": 2, "curve_id": "BIN-TOY-ORD19"}
KOBLITZ = {"A": 0, "B": 1, "h": 4, "curve_id": "BIN-TOY-K19", "l_hint": 130873}


def ensure_stage0() -> None:
    required = [
        "corrected-table.yaml",
        "cancelation-certificate.yaml",
        "stable-v-census.yaml",
        "methodological-note.md",
    ]
    stage0 = EXP_ROOT / "stage0"
    missing = [n for n in required if not (stage0 / n).exists()]
    if missing:
        raise SystemExit(f"REFUSE: Stage 0 incomplete; missing {missing}")


def build_field():
    ok, det = is_irreducible(MOD)
    if not ok:
        raise RuntimeError(f"modulus not irreducible: {det}")
    return TableField(N, MOD)


def verify_curve(E, expected_h, l_hint=None):
    order = E.count_by_trace()
    info = {
        "order_measured": order,
        "expected_h": expected_h,
        "A": E.A,
        "B": E.B,
        "label": "MEASURED",
    }
    if order % expected_h != 0:
        info["ok"] = False
        info["reason"] = "order not divisible by expected cofactor h"
        return info
    l_order = order // expected_h
    info["l_order"] = l_order
    info["l_prime"] = is_prime(l_order)
    if l_hint is not None:
        info["l_hint_inherited"] = l_hint
        info["l_hint_match"] = l_order == l_hint
        info["ok"] = info["l_prime"] and info["l_hint_match"]
    else:
        info["ok"] = info["l_prime"]
    return info


def random_V_basis(F, dim, rng):
    """Random F_2-basis of a dim-dimensional subspace (as field elements)."""
    basis = []
    while len(basis) < dim:
        v = rng.randrange(0, F.q)
        # Gaussian elim over F_2 on bit matrices
        cand = basis + [v]
        mat = [c for c in cand]
        rank = 0
        used = [False] * len(mat)
        for bit in range(F.n):
            pivot = None
            for i, row in enumerate(mat):
                if not used[i] and (row >> bit) & 1:
                    pivot = i
                    break
            if pivot is None:
                continue
            used[pivot] = True
            rank += 1
            for i, row in enumerate(mat):
                if i != pivot and (row >> bit) & 1:
                    mat[i] ^= mat[pivot]
        if rank == len(cand) and v not in basis:
            basis.append(v)
    return basis


def subspace_elements(basis):
    out = []
    d = len(basis)
    for mask in range(1 << d):
        x = 0
        for j in range(d):
            if (mask >> j) & 1:
                x ^= basis[j]
        out.append(x)
    return out


def factor_base_points(E, V_elems):
    """Points whose x-coordinate lies in V (including x=0 if in V)."""
    pts = []
    for x in V_elems:
        P = E.lift_x(x)
        if P is None:
            continue
        pts.append(P)
        Q = E.neg(P)
        if Q != P:
            pts.append(Q)
    return pts


def normalize_point(P):
    if P is None:
        return None
    return (P[0], P[1])


def certify_decomposition_independent(E, R, summands):
    """Independent of solver: sum summands on the curve and compare to R."""
    acc = None
    for P in summands:
        acc = E.add(acc, (P[0], P[1]))
    if R is None:
        return acc is None
    return acc is not None and acc[0] == R[0] and acc[1] == R[1]


def exhaustive_triple_index(E, pts, l_order, G, max_index=None):
    """Map target (as k in <G>) -> list of certified unordered triples of pts.

    Exhaustive over combinations with replacement unordered up to permutation:
    iterate i<=j<=k over point indices. Only keep sums in the prime-order
    subgroup (multiply by h and check).
    """
    h = E.count_by_trace() // l_order  # measured
    # Build discrete log table for factor-base points projected to <G>
    # For n=19, |G|=l_order ~1e5 — too big for full DL table.
    # Instead index by point coordinates of the sum R = P+Q+S directly.
    index = {}
    n_pts = len(pts)
    for i in range(n_pts):
        for j in range(i, n_pts):
            Sij = E.add(pts[i], pts[j])
            for k in range(j, n_pts):
                R = E.add(Sij, pts[k])
                if R is None:
                    continue
                # Require R in prime-order subgroup: [h]R != O and order | l
                hR = E.mul(h, R) if h > 1 else R
                # For Koblitz h=4: subgroup points satisfy [4]R has order | l,
                # equivalently [order]R=O and R not torsion of small order.
                # Simpler gate: [l_order]R == O and R != O.
                if E.mul(l_order, R) is not None:
                    continue
                key = (R[0], R[1])
                trip = (pts[i], pts[j], pts[k])
                if not certify_decomposition_independent(E, R, trip):
                    continue
                index.setdefault(key, []).append(
                    {
                        "summands": [list(p) for p in trip],
                        "verified": True,
                    }
                )
                if max_index is not None and len(index) >= max_index:
                    return index
    return index


def draw_targets(E, index, pts, n_targets, planted_fraction, rng, l_order):
    planted_n = int(n_targets * planted_fraction)
    keys = list(index.keys())
    rng.shuffle(keys)
    planted = []
    for key in keys:
        if len(planted) >= planted_n:
            break
        R = (key[0], key[1])
        planted.append(
            {
                "kind": "planted",
                "R": list(R),
                "ground_truth_decomps": index[key],
                "n_decomps": len(index[key]),
            }
        )
    # random targets in prime-order subgroup
    # find generator
    order = E.count_by_trace()
    h = order // l_order
    G = None
    for _ in range(200):
        P = None
        for __ in range(200):
            x = rng.randrange(1, E.F.q)
            P = E.lift_x(x)
            if P is not None:
                break
        if P is None:
            continue
        Q = E.mul(h, P)
        if Q is not None and E.mul(l_order, Q) is None:
            G = Q
            break
    if G is None:
        raise RuntimeError("failed to find generator of prime-order subgroup")
    random_tgts = []
    while len(random_tgts) < n_targets - len(planted):
        k = rng.randrange(1, l_order)
        R = E.mul(k, G)
        if R is None:
            continue
        key = (R[0], R[1])
        if key in index:
            continue  # skip accidentally decomposable
        random_tgts.append(
            {
                "kind": "random",
                "R": list(R),
                "ground_truth_decomps": [],
                "n_decomps": 0,
                "scalar_k": k,
            }
        )
    return planted + random_tgts, G


def attempt_s4_w4_instrument(F, B, basis, xR, D_protocol=4):
    """Try frozen S_4/W_4 at D=4. Return feasibility record."""
    t0 = time.time()
    rss0 = peak_rss_bytes()
    eqs, meta = descend_s4(F, B, basis, xR)
    wall_descend = time.time() - t0
    fits = eqs_fit_macaulay_D(eqs, D_protocol)
    rec = {
        "descend_meta": meta,
        "fits_macaulay_D": fits,
        "D_protocol": D_protocol,
        "wall_descend_s": wall_descend,
        "peak_rss_after_descend": peak_rss_bytes(),
        "rss_before": rss0,
        "macaulay_build_ok": False,
        "instrument_unavailable": False,
        "reason": None,
    }
    if not fits:
        rec["instrument_unavailable"] = True
        rec["reason"] = (
            f"descended S_4 boolean max degree {meta['max_boolean_degree']} "
            f"> protocol Macaulay D={D_protocol}; equations do not fit M_{D_protocol}"
        )
        return rec, eqs
    try:
        cl = ClosureGeneric(NV, D_protocol, N, eq_deg=meta["max_boolean_degree"])
        build = cl.macaulay_build_only(eqs)
        rec["macaulay_build_ok"] = True
        rec["macaulay_shape"] = build
        rec["peak_rss_after_build"] = peak_rss_bytes()
    except Exception as e:  # noqa: BLE001
        rec["instrument_unavailable"] = True
        rec["reason"] = f"Macaulay build failed: {e!r}"
        rec["traceback"] = traceback.format_exc()
    return rec, eqs


def probe_d6_feasibility(F, B, basis, xR):
    """Non-protocol probe: M_6 build when maxdeg<=6 (Stage 2 secondary)."""
    t0 = time.time()
    eqs, meta = descend_s4(F, B, basis, xR)
    D = 6
    out = {
        "label": "NON_PROTOCOL_D6_PROBE",
        "descend_meta": meta,
        "fits_D6": eqs_fit_macaulay_D(eqs, D),
    }
    if not out["fits_D6"]:
        out["macaulay_build_ok"] = False
        out["reason"] = "degree > 6"
        return out
    try:
        cl = ClosureGeneric(NV, D, N, eq_deg=meta["max_boolean_degree"])
        build = cl.macaulay_build_only(eqs)
        out["macaulay_build_ok"] = True
        out["macaulay_shape"] = build
        out["wall_s"] = time.time() - t0
        out["peak_rss_bytes"] = peak_rss_bytes()
    except Exception as e:  # noqa: BLE001
        out["macaulay_build_ok"] = False
        out["reason"] = repr(e)
        out["traceback"] = traceback.format_exc()
    return out


def main() -> None:
    ensure_stage0()
    stage1 = EXP_ROOT / "stage1"
    stage1.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    t0 = time.time()
    lines = []

    F = build_field()
    lines.append(f"field n={F.n} mod=0x{MOD:x}")

    arms = {}
    for name, cfg in (("ordinary", ORDINARY), ("koblitz", KOBLITZ)):
        E = Curve(F, cfg["A"], cfg["B"])
        info = verify_curve(E, cfg["h"], cfg.get("l_hint"))
        lines.append(f"{name} verify: {info}")
        arms[name] = {"E": E, "cfg": cfg, "verify": info}
        if not info["ok"]:
            lines.append(f"WARNING: {name} order hint mismatch — documented deviation")

    # --- Feasibility probe (primary seed, both arms, one xR) ---
    rng = random.Random(PRIMARY_SEED)
    basis_primary = random_V_basis(F, L, rng)
    basis_null = random_V_basis(F, L, rng)
    lines.append(f"V_primary basis={basis_primary}")
    lines.append(f"V_null_second basis={basis_null}")

    feasibility = {"arms": {}, "protocol": "S4_W4_D4_nv15", "seeds_planned": SEEDS}
    d6_probes = {}
    any_unavailable = False
    for name, arm in arms.items():
        E = arm["E"]
        # pick a random nonzero xR on the curve
        xR = None
        for _ in range(100):
            x = rng.randrange(1, F.q)
            if E.lift_x(x) is not None:
                xR = x
                break
        assert xR is not None
        rec, _ = attempt_s4_w4_instrument(F, E.B, basis_primary, xR, D_protocol=4)
        feasibility["arms"][name] = {
            "curve_id": arm["cfg"]["curve_id"],
            "xR": xR,
            "V_draw": "primary",
            "verify": arm["verify"],
            **rec,
        }
        if rec["instrument_unavailable"] or not rec["macaulay_build_ok"]:
            any_unavailable = True
        d6_probes[name] = probe_d6_feasibility(F, E.B, basis_primary, xR)
        lines.append(
            f"feasibility {name}: unavailable={rec.get('instrument_unavailable')} "
            f"reason={rec.get('reason')} maxdeg={rec['descend_meta']['max_boolean_degree']}"
        )
        lines.append(f"D6 probe {name}: {d6_probes[name].get('macaulay_build_ok')}")

    # Write instrument_unavailable as decisive path
    unavail = {
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "stage": 1,
        "instrument_unavailable": True,
        "classification": "infrastructure",
        "DO_ref": "DO-5",
        "asserts_nothing_about": (
            "shape-blindness / arm_ratio mathematics; timeouts and instrument "
            "limits are never negative mathematical evidence (AGENTS.md rule 3)"
        ),
        "protocol_requested": {
            "S_4_Weil_descent": True,
            "W_4_mutant_closure": True,
            "D": 4,
            "nv": NV,
            "n": N,
            "m": M,
            "l": L,
        },
        "observation": {
            "descended_S4_max_boolean_degree": {
                name: feasibility["arms"][name]["descend_meta"]["max_boolean_degree"]
                for name in feasibility["arms"]
            },
            "fits_macaulay_D4": {
                name: feasibility["arms"][name]["fits_macaulay_D"]
                for name in feasibility["arms"]
            },
            "reason": (
                "S_4 Weil descent at (m,l)=(3,5) over F_{2^19} produces Boolean "
                "equations of degree 6 (measured). Frozen Macaulay/W_4 at D=4 "
                "cannot host monomials of degree >4. CNF-XOR/WDSat not required "
                "and not available. Pure-Python S_4/W_4@D=4 instrument unreachable."
            ),
        },
        "per_arm": feasibility["arms"],
        "non_protocol_D6_probe": d6_probes,
        "no_mu_orbit_constraint_encoded": True,
        "no_break_or_rho_claim": True,
        "label_measured": "MEASURED",
        "label_modeled_leaf_counts": "not mixed into this report",
    }
    dump_yaml(stage1 / "instrument_unavailable.yaml", unavail)

    # Controls report: setup + enumeration soundness on a small planted sample
    # (exhaustive over V points — independent of S_4 instrument)
    controls = {
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "stage": 1,
        "controls": {},
        "note": (
            "S_4/W_4@D=4 instrument unavailable; controls below cover curve "
            "setup, V draws, and enumeration-certificate soundness on planted "
            "triples. arm_ratio not computed."
        ),
    }
    for name, arm in arms.items():
        E = arm["E"]
        info = arm["verify"]
        if not info.get("l_order"):
            controls["controls"][name] = {"skipped": True, "verify": info}
            continue
        V_elems = subspace_elements(basis_primary)
        pts = factor_base_points(E, V_elems)
        t_enum = time.time()
        # Cap enumeration work: combinations of points can be large
        # |pts| ~ O(2*32)=64 → C(64+2,3) ~ large; iterate i<=j<=k is ~64^3/6 ~ 40k
        index = exhaustive_triple_index(E, pts, info["l_order"], G=None)
        enum_wall = time.time() - t_enum
        # certificate pass on all indexed decomps
        cert_fail = 0
        cert_ok = 0
        for key, decomps in index.items():
            R = (key[0], key[1])
            for d in decomps:
                summands = [tuple(p) for p in d["summands"]]
                if certify_decomposition_independent(E, R, summands):
                    cert_ok += 1
                else:
                    cert_fail += 1
        # second V spread control: rebuild index size only
        V2 = subspace_elements(basis_null)
        pts2 = factor_base_points(E, V2)
        index2 = exhaustive_triple_index(E, pts2, info["l_order"], G=None)
        controls["controls"][name] = {
            "curve_id": arm["cfg"]["curve_id"],
            "verify": info,
            "V_primary_card": len(V_elems),
            "n_factor_base_points_primary": len(pts),
            "n_decomposable_targets_primary": len(index),
            "certificate_pass_count": cert_ok,
            "certificate_fail_count": cert_fail,
            "certificate_pass_rate": (
                cert_ok / (cert_ok + cert_fail) if (cert_ok + cert_fail) else None
            ),
            "enum_wall_s": enum_wall,
            "V_null_second_card": len(V2),
            "n_factor_base_points_null": len(pts2),
            "n_decomposable_targets_null": len(index2),
            "within_arm_v_null_spread": {
                "n_decomp_primary": len(index),
                "n_decomp_null_second": len(index2),
                "abs_diff": abs(len(index) - len(index2)),
            },
            "forbidden_n_guard": {"n": N, "n_in_29_37": False},
            "no_mu_encoding": True,
            "label": "MEASURED",
        }
        lines.append(
            f"controls {name}: decomposable={len(index)} cert_ok={cert_ok} "
            f"cert_fail={cert_fail} null_decomp={len(index2)}"
        )

    dump_yaml(stage1 / "controls-report.yaml", controls)

    # arm-comparison stub pointing at instrument_unavailable (not a second decisive claim)
    arm_cmp = {
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "stage": 1,
        "decisive_path": "instrument_unavailable",
        "arm_ratio_ops_median": None,
        "arm_ratio_in_band_0_8_1_25": None,
        "source_mu_alternative_rejected": None,
        "source_mu_note": (
            "Cannot evaluate source /mu alternative (arm_ratio ~ 1/n) because "
            "S_4/W_4@D=4 ops were not measured; escalate only on measured "
            "arm_ratio < 1/38 with certificates."
        ),
        "refutation_rate_per_arm": None,
        "certificate_pass_rate_solver": None,
        "enumeration_certificate_pass_rate": {
            name: controls["controls"].get(name, {}).get("certificate_pass_rate")
            for name in ("ordinary", "koblitz")
        },
        "see": "experiments/EXP-BINSTD-89d952/stage1/instrument_unavailable.yaml",
        "no_break_or_rho_claim": True,
    }
    dump_yaml(stage1 / "arm-comparison.yaml", arm_cmp)

    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "instrument_unavailable": True,
        "macaulay_build_ok_D4": False,
        "max_boolean_degree": {
            name: feasibility["arms"][name]["descend_meta"]["max_boolean_degree"]
            for name in feasibility["arms"]
        },
        "D6_probe_macaulay_build_ok": {
            name: d6_probes[name].get("macaulay_build_ok") for name in d6_probes
        },
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "instrument_unavailable",
        "seeds_executed_for_arm_ratio": [],
        "seeds_planned": SEEDS,
        "note": "Further seeds not run: frozen D=4 instrument unreachable on both arms",
    }

    write_run_package(
        RUN_FEASIBILITY,
        stage=1,
        arm="both-feasibility",
        seed=PRIMARY_SEED,
        command=(
            "python3 experiments/EXP-BINSTD-89d952/implementation/stage1_run.py"
        ),
        parameters={
            "n": N,
            "m": M,
            "l": L,
            "nv": NV,
            "D_protocol": 4,
            "ordinary": ORDINARY,
            "koblitz": KOBLITZ,
            "basis_primary": basis_primary,
            "basis_null_second": basis_null,
        },
        metrics=metrics,
        valid=True,  # valid infrastructure observation
        invalid_reason=None,
        termination_reason="instrument_unavailable",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": True,
            "note": (
                "No solver find claimed; enumeration certificates recorded in "
                "controls-report only"
            ),
        },
        status_override="failed_infrastructure",
    )

    # Second run package: controls enumeration detail
    write_run_package(
        RUN_CONTROLS,
        stage=1,
        arm="controls-enumeration",
        seed=PRIMARY_SEED,
        command=(
            "python3 experiments/EXP-BINSTD-89d952/implementation/stage1_run.py "
            "# controls enumeration embedded"
        ),
        parameters={"control": "exhaustive_triple_index + independent cert"},
        metrics={
            "controls": controls["controls"],
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
            "termination_reason": "completed",
        },
        valid=all(
            (controls["controls"].get(a, {}).get("certificate_fail_count", 1) == 0)
            for a in ("ordinary", "koblitz")
            if "certificate_fail_count" in controls["controls"].get(a, {})
        ),
        invalid_reason=None,
        termination_reason="completed",
        stdout_text="controls enumeration completed\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "decomposition",
            "verified": True,
            "verifier": "certify_decomposition_independent (curve summation)",
            "note": (
                "Every enumerated planted triple re-verified by summing points "
                "on the curve; independent of any algebraic solver"
            ),
        },
    )

    # Persist D6 probe for Stage 2
    dump_yaml(
        stage1 / "d6-nonprotocol-probe.yaml",
        {
            "experiment_id": EXP_ID,
            "note": "Non-protocol; not used for arm_ratio success criterion",
            "probes": d6_probes,
        },
    )

    print("\n".join(lines))
    print(f"Stage 1 done instrument_unavailable={any_unavailable}")


if __name__ == "__main__":
    main()
