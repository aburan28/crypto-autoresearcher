#!/usr/bin/env python3
"""Stage 2: toy ord(pi_q), pi_2 checks, null/degenerate/composite-search controls.

Requires stage0/ artifacts to exist. Certificates for every order claim.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import resource
import sys
import time
from datetime import datetime, timezone
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-BINSTD-9d1b8e"
IMPL = Path(__file__).resolve().parent
sys.path.insert(0, str(IMPL))

from curve import Curve  # noqa: E402
from gf2n import Field, find_irreducible, is_irreducible  # noqa: E402

import yaml  # noqa: E402

D = 4
Q = 1 << D
F16_MOD = 0b10011  # t^4 + t + 1
B_HINT = 0b1001  # t^3 + 1
A0 = 0
PRIMARY_SEED = 20260926
N_PI2 = 100
COMPOSITE_MAX = 64


def weil_order(q: int, t: int, k: int) -> int:
    s0, s1 = 2, t
    for _ in range(k - 1):
        s0, s1 = s1, t * s1 - q * s0
    return q**k + 1 - s1


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


def factor_small(n: int) -> list[int]:
    fac = []
    x = n
    d = 2
    while d * d <= x:
        while x % d == 0:
            fac.append(d)
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        fac.append(x)
    return fac


def embed_f16_generator(Fbig: Field) -> int:
    """Return a root of t^4+t+1 in Fbig (which must contain F_16)."""
    assert Fbig.n % 4 == 0
    for a in range(Fbig.q):
        a2 = Fbig.sqr(a)
        a4 = Fbig.sqr(a2)
        if (a4 ^ a ^ 1) == 0 and a not in (0, 1):
            return a
    raise RuntimeError("no root of t^4+t+1 in extension")


def b_from_hint(Fbig: Field) -> int:
    t = embed_f16_generator(Fbig)
    return Fbig.mul(Fbig.mul(t, t), t) ^ 1  # t^3+1


def random_point(E: Curve, rng: random.Random):
    F = E.F
    for _ in range(10_000):
        x = rng.randrange(F.q)
        P = E.lift_x(x)
        if P is not None:
            return P
    raise RuntimeError("failed to sample curve point")


def point_of_prime_order(E: Curve, h: int, r: int, rng: random.Random):
    """Return P of order r (r prime), or raise."""
    for _ in range(10_000):
        R = random_point(E, rng)
        P = E.mul(h, R)
        if P is None:
            continue
        if E.mul(r, P) is None:
            # order divides r; r prime => order r
            return P
    raise RuntimeError("failed to find order-r point")


def ord_pi_q(E: Curve, P, d: int, k_max: int) -> int:
    """Least j>=1 with pi_q^j(P)=P, q=2^d."""
    Q = P
    for j in range(1, k_max + 1):
        Q = E.frobenius_point(Q, d)  # apply pi_q once more
        if Q == P:
            return j
    raise RuntimeError("ord_pi_q not found within k_max")


def certificate_ord(E: Curve, P, d: int, j: int) -> dict:
    """Independently re-check ord claim: pi_q^j(P)=P and no smaller positive."""
    Q = P
    for i in range(1, j + 1):
        Q = E.frobenius_point(Q, d)
        if i < j and Q == P:
            return {"verified": False, "reason": f"smaller_exponent_{i}", "claimed_j": j}
        if i == j and Q != P:
            return {"verified": False, "reason": "pi_q^j_ne_P", "claimed_j": j}
    return {
        "verified": True,
        "claimed_j": j,
        "check": "pi_q^j(P)=P and no smaller positive exponent",
        "point_x": P[0],
        "point_y": P[1],
        "d": d,
    }


def rss() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def ensure_stage0():
    p = EXP / "stage0" / "five-row-symmetry-certificate.yaml"
    if not p.exists():
        raise SystemExit("specification_error: stage0/ missing; Stage 2 blocked")


def build_extension(n: int) -> Field:
    # Prefer known irreducibles when available
    known = {
        4: F16_MOD,
        8: (1 << 8) | (1 << 4) | (1 << 3) | (1 << 1) | 1,  # may need verify
        12: None,
        20: (1 << 20) | (1 << 3) | 1,  # t^20+t^3+1
        24: None,
        28: None,
    }
    mod = known.get(n)
    if mod is not None and is_irreducible(mod):
        return Field(n, mod)
    return Field(n, find_irreducible(n))


def run_prime_cell(d: int, k_prime: int, seed: int, cert_dir: Path) -> dict:
    n = d * k_prime
    F = build_extension(n)
    B = b_from_hint(F)
    assert F.frobenius(B, d) == B  # B in F_q
    E = Curve(F, A0, B)
    # Base order over F16 via Weil from known t=5, h=12
    t_base = 5
    h = Q + 1 - t_base  # 12
    N = weil_order(Q, t_base, k_prime)
    assert N % h == 0
    r = N // h
    assert is_prime(r), f"r not prime: {r}"
    assert gcd(h, r) == 1
    rng = random.Random(seed)
    P = point_of_prime_order(E, h, r, rng)
    # sanity: order r
    assert E.mul(r, P) is None and P is not None
    j = ord_pi_q(E, P, d, k_prime)
    cert = certificate_ord(E, P, d, j)
    cert_path = cert_dir / f"ord-pi-q-d{d}-k{k_prime}.yaml"
    cert_doc = {
        "kind": "frobenius_order",
        "cell": {"d": d, "k_prime": k_prime, "n": n},
        "r": r,
        "h": h,
        "expected_ord": k_prime,
        "measured_ord": j,
        "certificate": cert,
        "independent_of_solver_note": (
            "Re-applies pi_q via schoolbook squaring; does not trust the search loop's "
            "last comparison alone."
        ),
    }
    cert_path.write_text(yaml.safe_dump(cert_doc, sort_keys=False))

    # pi_2 checks on N_PI2 prime-subgroup points (scalar multiples of one generator)
    failures = 0  # image NOT on curve
    on_curve_unexpected = 0
    anomalous = None
    x_notin_f2 = 0
    gen = P
    for i in range(N_PI2):
        scalar = rng.randrange(1, r)
        Pi = E.mul(scalar, gen)
        assert Pi is not None
        on = E.is_endomorphism_image_on_curve(Pi, 1)  # pi_2
        x = Pi[0]
        in_f2 = x in (0, 1)
        if not in_f2:
            x_notin_f2 += 1
            if on:
                on_curve_unexpected += 1
                anomalous = {"index": i, "x": x, "pi2_on_curve": True}
            else:
                failures += 1
    pi2 = {
        "d": d,
        "k_prime": k_prime,
        "N": N_PI2,
        "x_notin_F2_count": x_notin_f2,
        "pi2_off_curve_failures_among_notin_F2": failures,
        "pi2_on_curve_unexpected_among_notin_F2": on_curve_unexpected,
        "expect_failures_eq_notin_F2": failures == x_notin_f2 and on_curve_unexpected == 0,
        "anomalous": anomalous,
        "seed": seed,
    }
    return {
        "d": d,
        "k_prime": k_prime,
        "n": n,
        "field_mod": F.mod,
        "A": A0,
        "B": B,
        "t_base": t_base,
        "h": h,
        "N": N,
        "r": r,
        "r_prime": True,
        "gcd_h_r": 1,
        "ord_pi_q": j,
        "expected_ord": k_prime,
        "ord_match": j == k_prime,
        "certificate_path": str(cert_path.relative_to(ROOT)),
        "certificate_verified": cert["verified"],
        "pi2": pi2,
        "hard_fail_ord": j != k_prime,
    }


def run_k1_control(seed: int, cert_dir: Path) -> dict:
    F = Field(4, F16_MOD)
    E = Curve(F, A0, B_HINT)
    h = E.count_by_trace()
    t = Q + 1 - h
    assert h == 12 and t == 5
    rng = random.Random(seed)
    # On E(F_q), pi_q fixes coordinates => ord=1
    P = random_point(E, rng)
    j = ord_pi_q(E, P, D, 2)
    cert = certificate_ord(E, P, D, j)
    path = cert_dir / "ord-pi-q-k1-embedding.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "kind": "frobenius_order",
                "control": "k1_embedding",
                "measured_ord": j,
                "expected_ord": 1,
                "symmetry_group_order_with_negation": 2 if j == 1 else None,
                "certificate": cert,
            },
            sort_keys=False,
        )
    )
    return {
        "control": "k1_embedding",
        "ord_pi_q": j,
        "expected_ord": 1,
        "pass": j == 1,
        "symmetry_order_with_negation": 2 if j == 1 else None,
        "certificate_path": str(path.relative_to(ROOT)),
        "certificate_verified": cert["verified"],
    }


def run_null(seed: int) -> dict:
    """Ordinary curve over F_{2^20} with B notin F_16; pi_16 not endomorphism."""
    F = build_extension(20)
    rng = random.Random(seed)
    # Find ordinary A,B with B not in F16 and odd t
    chosen = None
    for trial in range(200):
        A = rng.randrange(F.q)
        B = rng.randrange(1, F.q)
        if F.frobenius(B, 4) == B:
            continue  # in F16
        E = Curve(F, A, B)
        N = E.count_by_trace()
        t = F.q + 1 - N
        if t % 2 == 0:
            continue  # supersingular candidate / even trace
        chosen = (A, B, N, t, E)
        break
    if chosen is None:
        return {
            "control": "null_no_subfield",
            "pass": False,
            "error": "no_ordinary_B_notin_F16_within_budget",
        }
    A, B, N, t, E = chosen
    # Sample points; pi_16 image must be off-curve
    off = 0
    on = 0
    for _ in range(50):
        P = random_point(E, rng)
        if E.is_endomorphism_image_on_curve(P, 4):  # pi_16
            on += 1
        else:
            off += 1
    # Instrument invalid if ANY finite endomorphism order claimed — we report
    # whether pi_16 ever landed on-curve.
    reports_endomorphism = on > 0 and off == 0
    # Stronger: even one on-curve hit for a random point with coords not in F16
    # would be suspicious; require off==50 for clean pass
    return {
        "control": "null_no_subfield",
        "n": 20,
        "A": A,
        "B": B,
        "B_in_F16": False,
        "N": N,
        "t": t,
        "t_odd": t % 2 == 1,
        "samples": 50,
        "pi16_off_curve": off,
        "pi16_on_curve": on,
        "null_reports_no_endomorphism": on == 0,
        "pass": on == 0,
        "instrument_invalid_if_endomorphism": on > 0,
        "peak_rss_bytes": rss(),
    }


def run_degenerate(seed: int) -> dict:
    """B in F_2 => pi_2 IS an endomorphism (positive control)."""
    F = build_extension(20)
    E = Curve(F, 0, 1)  # B=1 in F_2
    assert F.frobenius(1, 1) == 1
    N = E.count_by_trace()
    t = F.q + 1 - N
    rng = random.Random(seed)
    on = 0
    for _ in range(50):
        P = random_point(E, rng)
        if E.is_endomorphism_image_on_curve(P, 1):
            on += 1
    return {
        "control": "degenerate_B_in_F2",
        "n": 20,
        "A": 0,
        "B": 1,
        "N": N,
        "t": t,
        "samples": 50,
        "pi2_on_curve": on,
        "degenerate_detects_pi2_endomorphism": on == 50,
        "pass": on == 50,
        "peak_rss_bytes": rss(),
    }


def run_composite_search(seed: int, cert_dir: Path) -> dict:
    """Search E/F_16 odd t for proper-divisor phenomenon at k'=6."""
    F = Field(4, F16_MOD)
    rng = random.Random(seed)
    tried = 0
    found = None
    log = []
    # Enumerate some (A,B) with B!=0; also include systematic A=0 sweep
    candidates = []
    for A in range(16):
        for B in range(1, 16):
            candidates.append((A, B))
    rng.shuffle(candidates)
    candidates = candidates[:COMPOSITE_MAX]
    for A, B in candidates:
        tried += 1
        E = Curve(F, A, B)
        h = E.count_by_trace()
        t = Q + 1 - h
        if t % 2 == 0:
            log.append({"A": A, "B": B, "t": t, "skip": "even_t"})
            continue
        # Orders at extensions for p|6
        N6 = weil_order(Q, t, 6)
        N2 = weil_order(Q, t, 2)  # F_{q^2} = F_{2^8}
        N3 = weil_order(Q, t, 3)  # F_{q^3} = F_{2^{12}}
        # Look for prime r > 2^12 dividing N2 or N3, and check if that r divides N6
        # and whether ord(mu) would be proper divisor: r | #E(F_{q^{k/p}})
        entry = {"A": A, "B": B, "t": t, "h": h, "N6": N6, "N2": N2, "N3": N3}
        hit = None
        for label, Nm, pdiv in (("N2", N2, 2), ("N3", N3, 3)):
            for fac in set(factor_small(Nm)):
                if fac > (1 << 12) and is_prime(fac) and N6 % fac == 0:
                    hit = {
                        "prime_r": fac,
                        "divides": label,
                        "p": pdiv,
                        "k_prime": 6,
                        "proper_divisor_of_k": 6 // pdiv,
                        "note": (
                            "r | #E(F_{q^{k'/p}}) with p|k' implies ord(mu) | (k'/p) "
                            "proper divisor of k' on the r-primary component"
                        ),
                    }
                    break
            if hit:
                break
        entry["hit"] = hit
        log.append(entry)
        if hit:
            found = {"A": A, "B": B, "t": t, "h": h, **hit}
            # Certificate on the toy extension if affordable (n=24)
            break
    report = {
        "control": "composite_curve_search",
        "d": 4,
        "k_prime": 6,
        "max_curves_tried": COMPOSITE_MAX,
        "curves_tried": tried,
        "composite_search_found": found is not None,
        "found": found,
        "outcome": "found" if found is not None else "not-found-within-budget",
        "forced_prediction": False,
        "seed": seed,
        "log_head": log[:10],
        "n_log": len(log),
    }
    if found:
        # Optional mechanical ord check on F_{2^{24}} if we can embed
        try:
            F24 = build_extension(24)
            # Map A,B from F16 into F24
            gen = embed_f16_generator(F24)
            # Build isomorphism F16 -> subfield: send t |-> gen where t^4+t+1=0
            # Elements of F16 are polys in t; encode int bits via gen powers
            def embed(v: int) -> int:
                out = 0
                gpow = 1
                for i in range(4):
                    if (v >> i) & 1:
                        out ^= gpow
                    gpow = F24.mul(gpow, gen)
                return out

            A24, B24 = embed(found["A"]), embed(found["B"])
            E24 = Curve(F24, A24, B24)
            r = found["prime_r"]
            h = found["h"]
            N6 = weil_order(Q, found["t"], 6)
            # Cofactor for the r-part
            # Find a point of order r
            rng2 = random.Random(seed + 1)
            P = None
            for _ in range(5000):
                R = random_point(E24, rng2)
                # multiply by N6/r
                Qp = E24.mul(N6 // r, R)
                if Qp is not None and E24.mul(r, Qp) is None:
                    P = Qp
                    break
            if P is not None:
                j = ord_pi_q(E24, P, D, 6)
                cert = certificate_ord(E24, P, D, j)
                cpath = cert_dir / "ord-pi-q-composite-found.yaml"
                cpath.write_text(
                    yaml.safe_dump(
                        {
                            "kind": "frobenius_order",
                            "control": "composite_search_found",
                            "measured_ord": j,
                            "expected_proper_divisor": True,
                            "k_prime": 6,
                            "certificate": cert,
                            "curve": found,
                        },
                        sort_keys=False,
                    )
                )
                report["measured_ord_on_found"] = j
                report["ord_is_proper_divisor"] = j < 6 and (6 % j == 0)
                report["certificate_path"] = str(cpath.relative_to(ROOT))
                report["certificate_verified"] = cert["verified"]
        except Exception as e:
            report["ord_check_error"] = str(e)
    return report


def write_stage2_artifacts(prime_cells, pi2_rows, controls, composite):
    stage2 = EXP / "stage2"
    stage2.mkdir(parents=True, exist_ok=True)
    ord_table = {
        "experiment_id": "EXP-BINSTD-9d1b8e",
        "stage": 2,
        "kind": "ord_pi_q_table",
        "cells": [
            {
                "d": c["d"],
                "k_prime": c["k_prime"],
                "expected_ord": c["expected_ord"],
                "ord_pi_q_on_G": c["ord_pi_q"],
                "match": c["ord_match"],
                "r": c["r"],
                "h": c["h"],
                "certificate_verified": c["certificate_verified"],
                "certificate_path": c["certificate_path"],
                "measured": True,
            }
            for c in prime_cells
        ],
        "k1_control": next(x for x in controls if x["control"] == "k1_embedding"),
        "hard_fail_ord": any(c["hard_fail_ord"] for c in prime_cells),
        "break_claim": False,
    }
    pi2_doc = {
        "experiment_id": "EXP-BINSTD-9d1b8e",
        "stage": 2,
        "kind": "pi2_endomorphism_checks",
        "rows": pi2_rows,
        "prediction": "pi_2 is NOT an endomorphism on B-notin-F_2 cells (failures = N/N for x notin F_2)",
        "break_claim": False,
    }
    null = next(x for x in controls if x["control"] == "null_no_subfield")
    deg = next(x for x in controls if x["control"] == "degenerate_B_in_F2")
    k1 = next(x for x in controls if x["control"] == "k1_embedding")
    controls_doc = {
        "experiment_id": "EXP-BINSTD-9d1b8e",
        "stage": 2,
        "kind": "controls_report",
        "controls": {
            "k1_embedding": k1,
            "null_no_subfield": null,
            "degenerate_B_in_F2": deg,
            "composite_curve_search": {
                "outcome": composite["outcome"],
                "found": composite["composite_search_found"],
            },
        },
        "null_reports_no_endomorphism": null.get("null_reports_no_endomorphism"),
        "degenerate_detects_pi2_endomorphism": deg.get("degenerate_detects_pi2_endomorphism"),
        "memory_accounting": {
            "peak_rss_bytes_null": null.get("peak_rss_bytes"),
            "peak_rss_bytes_degenerate": deg.get("peak_rss_bytes"),
            "analytic_note": (
                "Dominant structures are F_{2^{dk}} field elements O(dk) bits; "
                "measured RSS recorded per control run."
            ),
        },
        "certificate_pass_rate": (
            1.0
            if all(c["certificate_verified"] for c in prime_cells)
            and k1["certificate_verified"]
            else 0.0
        ),
        "break_claim": False,
    }
    (stage2 / "ord-pi-q-table.yaml").write_text(yaml.safe_dump(ord_table, sort_keys=False))
    (stage2 / "pi2-endomorphism-checks.yaml").write_text(yaml.safe_dump(pi2_doc, sort_keys=False))
    (stage2 / "controls-report.yaml").write_text(yaml.safe_dump(controls_doc, sort_keys=False))
    (stage2 / "composite-search-report.yaml").write_text(yaml.safe_dump(composite, sort_keys=False))
    return ord_table, pi2_doc, controls_doc


def write_run(run_id: str, stage_label: str, params: dict, metrics: dict, valid: bool,
              termination_reason: str, wall_s: float, started: str, finished: str,
              stdout: str, raw_extra: dict | None = None):
    run_dir = EXP / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    commit = os.popen("git rev-parse HEAD").read().strip()
    dirty = bool(os.popen("git status --porcelain").read().strip())
    cmd = (
        f"python3 experiments/EXP-BINSTD-9d1b8e/implementation/stage2_run.py "
        f"--run-id {run_id} --arm {stage_label}"
    )
    (run_dir / "command.txt").write_text(cmd + "\n")
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "dependencies": {"pyyaml": yaml.__version__},
    }
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    raw = {"stage": 2, "arm": stage_label, "metrics": metrics, "break_claim": False}
    if raw_extra:
        raw.update(raw_extra)
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2, default=str) + "\n")
    (run_dir / "stdout.log").write_text(stdout)
    (run_dir / "stderr.log").write_text("")
    status = "completed_valid" if valid else (
        "failed_infrastructure" if termination_reason in ("timeout", "memory_abort", "crash")
        else "invalid_measurement"
    )
    if termination_reason == "hard_fail_ord":
        status = "completed_valid"  # observation exists; hard-fail is a metric flag
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-BINSTD-9d1b8e",
            "task_id": "TASK-20261001-0fc34d",
            "stage": 2,
            "arm": stage_label,
            "status": status,
            "termination_reason": termination_reason,
            "code": {"commit": commit, "dirty": dirty, "command": cmd},
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "backend": None,
                "provider": None,
                "resolved_model_id": None,
                "model_provenance": "not-applicable",
                "model_verified": False,
                "requested_reasoning_effort": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "fallback_reason": None,
                "degraded_requirements": [],
                "independent_session": False,
                "adapter_version": None,
                "config_digest": None,
            },
            "environment": env,
            "inputs": {"curve_id": None, "seed": params.get("seed"), "parameters": params},
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": wall_s,
            },
            "resources": {"peak_rss_bytes": rss(), "cpu_seconds": None},
            "result": {
                "metrics": metrics,
                "valid": valid,
                "invalid_reason": None if valid else termination_reason,
                "certificate": {
                    "kind": "none" if stage_label in ("null", "degenerate", "pi2") else "frobenius_order",
                    "verified": metrics.get("certificate_verified"),
                },
            },
        }
    }
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument(
        "--arm",
        required=True,
        choices=["all", "cell45", "cell47", "pi2", "k1", "null", "degenerate", "composite"],
    )
    ap.add_argument("--seed", type=int, default=PRIMARY_SEED)
    ap.add_argument("--run-id-cell45")
    ap.add_argument("--run-id-cell47")
    ap.add_argument("--run-id-pi2")
    ap.add_argument("--run-id-k1")
    ap.add_argument("--run-id-null")
    ap.add_argument("--run-id-degenerate")
    ap.add_argument("--run-id-composite")
    args = ap.parse_args()

    ensure_stage0()
    cert_dir = EXP / "stage2" / "certificates"
    cert_dir.mkdir(parents=True, exist_ok=True)

    if args.arm == "all":
        # Orchestrate all arms with provided run IDs
        ids = {
            "cell45": args.run_id_cell45,
            "cell47": args.run_id_cell47,
            "pi2": args.run_id_pi2,
            "k1": args.run_id_k1,
            "null": args.run_id_null,
            "degenerate": args.run_id_degenerate,
            "composite": args.run_id_composite,
        }
        missing = [k for k, v in ids.items() if not v]
        if missing:
            raise SystemExit(f"all-arm requires run ids for {missing}")
        # Run sequentially
        results = {}
        for arm in ["cell45", "cell47", "k1", "null", "degenerate", "composite"]:
            sys.argv = [
                sys.argv[0],
                "--run-id",
                ids[arm],
                "--arm",
                arm,
                "--seed",
                str(args.seed),
            ]
            # call recursively via functions instead
        # Direct execution below by re-entering logic
        prime_cells = []
        for arm, kp, rid in [("cell45", 5, ids["cell45"]), ("cell47", 7, ids["cell47"])]:
            t0 = time.time()
            started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                cell = run_prime_cell(D, kp, args.seed, cert_dir)
                term = "hard_fail_ord" if cell["hard_fail_ord"] else "completed"
                valid = cell["certificate_verified"] and not (
                    term == "crash"
                )
                # hard_fail_ord is still a valid measurement
                valid = cell["certificate_verified"]
            except Exception as e:
                finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                write_run(
                    rid, arm, {"seed": args.seed, "k_prime": kp},
                    {"error": str(e)}, False, "crash", time.time() - t0, started, finished,
                    f"CRASH: {e}\n",
                )
                raise
            finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            write_run(
                rid, arm, {"seed": args.seed, "d": D, "k_prime": kp},
                {
                    "ord_pi_q": cell["ord_pi_q"],
                    "expected_ord": cell["expected_ord"],
                    "ord_match": cell["ord_match"],
                    "certificate_verified": cell["certificate_verified"],
                    "hard_fail_ord": cell["hard_fail_ord"],
                },
                valid,
                term,
                time.time() - t0,
                started,
                finished,
                json.dumps(cell, default=str, indent=2) + "\n",
                {"cell": cell},
            )
            prime_cells.append(cell)
            results[arm] = cell

        # pi2 aggregate run from cells
        t0 = time.time()
        started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        pi2_rows = [c["pi2"] for c in prime_cells]
        pi2_ok = all(r["expect_failures_eq_notin_F2"] for r in pi2_rows)
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        write_run(
            ids["pi2"], "pi2", {"seed": args.seed, "N": N_PI2},
            {
                "pi2_endomorphism_false_on_B_notin_F2": pi2_ok,
                "rows": pi2_rows,
            },
            pi2_ok, "completed" if pi2_ok else "instrument_invalid",
            time.time() - t0, started, finished,
            json.dumps(pi2_rows, indent=2) + "\n",
        )

        controls = []
        for arm, fn, rid in [
            ("k1", lambda: run_k1_control(args.seed, cert_dir), ids["k1"]),
            ("null", lambda: run_null(args.seed), ids["null"]),
            ("degenerate", lambda: run_degenerate(args.seed), ids["degenerate"]),
        ]:
            t0 = time.time()
            started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                out = fn()
                term = "completed"
                if arm == "null" and out.get("instrument_invalid_if_endomorphism"):
                    term = "instrument_invalid"
                valid = bool(out.get("pass"))
                if arm == "null" and term == "instrument_invalid":
                    valid = False
            except Exception as e:
                finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                write_run(rid, arm, {"seed": args.seed}, {"error": str(e)}, False, "crash",
                          time.time() - t0, started, finished, f"CRASH: {e}\n")
                raise
            finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            write_run(
                rid, arm, {"seed": args.seed}, out, valid if arm != "k1" else out.get("pass", False),
                term, time.time() - t0, started, finished,
                json.dumps(out, default=str, indent=2) + "\n", {"control": out},
            )
            controls.append(out)

        t0 = time.time()
        started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        composite = run_composite_search(args.seed, cert_dir)
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        write_run(
            ids["composite"], "composite", {"seed": args.seed, "max_curves": COMPOSITE_MAX},
            {
                "composite_search_found": composite["composite_search_found"],
                "outcome": composite["outcome"],
                "curves_tried": composite["curves_tried"],
            },
            True,  # search outcome is never forced failure
            "completed",
            time.time() - t0, started, finished,
            json.dumps(composite, default=str, indent=2) + "\n",
            {"composite": composite},
        )

        write_stage2_artifacts(prime_cells, pi2_rows, controls, composite)
        print(json.dumps({
            "prime_ords": [c["ord_pi_q"] for c in prime_cells],
            "pi2_ok": pi2_ok,
            "controls": {c["control"]: c.get("pass") for c in controls},
            "composite": composite["outcome"],
        }))
        return

    # Single-arm mode
    t0 = time.time()
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.arm == "cell45":
        cell = run_prime_cell(D, 5, args.seed, cert_dir)
        print(json.dumps({"ord": cell["ord_pi_q"]}, default=str))
    elif args.arm == "cell47":
        cell = run_prime_cell(D, 7, args.seed, cert_dir)
        print(json.dumps({"ord": cell["ord_pi_q"]}, default=str))
    elif args.arm == "k1":
        print(json.dumps(run_k1_control(args.seed, cert_dir), default=str))
    elif args.arm == "null":
        print(json.dumps(run_null(args.seed), default=str))
    elif args.arm == "degenerate":
        print(json.dumps(run_degenerate(args.seed), default=str))
    elif args.arm == "composite":
        print(json.dumps(run_composite_search(args.seed, cert_dir), default=str))
    else:
        raise SystemExit("use --arm all for pi2 aggregate")


if __name__ == "__main__":
    main()
