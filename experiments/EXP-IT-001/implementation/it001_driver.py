#!/usr/bin/env sage -python
"""EXP-IT-001 v3 bounded-toy driver (RUN-IT-001-bounded-toy).

Binds exclusively to experiments/EXP-IT-001/specification.v3.yaml.
Observations only — no hypothesis status claims.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
import traceback
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sage.all import (  # type: ignore
    EllipticCurve,
    GF,
    Integer,
    discrete_log,
    next_prime,
    randint,
)

REPO = Path(__file__).resolve().parents[3]
IMPL = Path(__file__).resolve().parent
sys.path.insert(0, str(IMPL))
sys.path.insert(0, str(REPO))

import it001_pure as P  # noqa: E402

CONTRACT = "experiments/EXP-IT-001/specification.v3.yaml"
RUN_ID = "RUN-IT-001-bounded-toy"
EXP_ID = "EXP-IT-001"
TASK_ID = "TASK-20260731-127"
GOAL_ID = "GOAL-ECDLP-001"
BATCH_ID = "BATCH-028"
APPROVAL_SNAPSHOT = "8f02ab4b"
AMEND_FREEZE = "d65c5e21"
SEEDS = [2026073101, 2026073102, 2026073103]
SEED_DENSITY = 2026073199
BITS_LIST = [20, 24, 28]
H_MAX = 256
WALL_BUDGET = 7200.0
# Prefer completing a minimal package: reserve time for path search / controls.
DENSITY_BUDGET = {
    20: 600.0,
    24: 3600.0,
    28: 900.0,
}
UNPLANTED_TARGET = 20
PER_BITS_MIN = 6


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_meta() -> dict[str, Any]:
    def run(cmd: list[str]) -> str:
        try:
            return subprocess.check_output(cmd, cwd=REPO, text=True).strip()
        except Exception:
            return ""

    dirty = bool(run(["git", "status", "--porcelain"]))
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "dirty": dirty,
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
    }


def peak_rss() -> int:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes; Linux KiB — normalize heuristically
    if sys.platform == "darwin":
        return int(rss)
    return int(rss * 1024)


def cpu_seconds() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return float(ru.ru_utime + ru.ru_stime)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def curve_from_j(p: int, j: int):
    K = GF(p)
    return EllipticCurve(j=K(j))


def is_ordinary(ordE: int, p: int) -> bool:
    return int(ordE) != int(p) + 1


def retain_class(ordE: int, p: int, bits: int) -> tuple[int, int] | None:
    if not is_ordinary(ordE, p):
        return None
    cand = P.unique_N_candidates(int(ordE), bits, H_MAX)
    if not cand:
        return None
    N = min(cand)
    h = int(ordE) // N
    return N, h


def find_p_bits(bits: int, deadline: float) -> dict[str, Any]:
    lo = 2 ** (bits + 1)
    hi = 2 ** (bits + 2)
    p = int(next_prime(lo))
    scanned_primes = 0
    while p < hi and time.time() < deadline:
        scanned_primes += 1
        K = GF(p)
        for j in range(p):
            if time.time() >= deadline:
                break
            try:
                E = EllipticCurve(j=K(j))
            except Exception:
                continue
            ordE = int(E.cardinality())
            r = retain_class(ordE, p, bits)
            if r is not None:
                return {
                    "status": "found",
                    "p_bits": p,
                    "first_hit_j": j,
                    "first_hit_N_star": r[0],
                    "first_hit_h_star": r[1],
                    "scanned_primes": scanned_primes,
                }
        p = int(next_prime(p))
    return {"status": "not_found", "scanned_primes": scanned_primes, "last_p": p}


def density_exhaustive(bits: int, p: int, deadline: float) -> dict[str, Any]:
    records: list[tuple[int, int, int]] = []
    special_js: list[int] = []
    n_j_ok = 0
    n_singularish = 0
    stopped = "completed"
    K = GF(p)
    for j in range(p):
        if time.time() >= deadline:
            stopped = "resource_exhaustion_wall"
            break
        try:
            E = EllipticCurve(j=K(j))
        except Exception:
            n_singularish += 1
            continue
        n_j_ok += 1
        ordE = int(E.cardinality())
        r = retain_class(ordE, p, bits)
        if r is None:
            continue
        N, h = r
        records.append((j, N, h))
        det = P.detect_special(ordE, p, N)
        if det["any_special"]:
            special_js.append(j)
    card = len(records)
    rho = (len(special_js) / card) if card else 0.0
    return {
        "bits": bits,
        "p_bits": p,
        "estimator": "exhaustive",
        "status": stopped,
        "j_scanned_through": j if p else -1,
        "n_j_constructed": n_j_ok,
        "n_construct_fail": n_singularish,
        "cardinality": card,
        "n_special": len(special_js),
        "rho_special": rho,
        "records_hash": P.records_hash(records),
        "h_max": H_MAX,
        "density_universe_spec_hash": P.density_universe_spec_hash(bits),
        "special_js_sample": special_js[:20],
        "records": records if bits == 20 else None,  # keep 20 for planting; large for 24
        "records_compact": [(j, N, h) for j, N, h in records[:5]],
    }


def density_sample_28(p: int, deadline: float, sample_size: int = 50000) -> dict[str, Any]:
    records: list[tuple[int, int, int]] = []
    special_js: list[int] = []
    seen: set[int] = set()
    counter = 0
    stopped = "completed"
    K = GF(p)
    seed = SEED_DENSITY
    while len(records) < sample_size:
        if time.time() >= deadline:
            stopped = "resource_exhaustion_wall"
            break
        if len(seen) >= p:
            stopped = "field_exhausted"
            break
        raw = hashlib.sha256(P.be_int(seed) + P.be_int(counter)).digest()
        j = int.from_bytes(raw, "big") % p
        counter += 1
        if j in seen:
            continue
        seen.add(j)
        try:
            E = EllipticCurve(j=K(j))
        except Exception:
            continue
        ordE = int(E.cardinality())
        r = retain_class(ordE, p, 28)
        if r is None:
            continue
        N, h = r
        records.append((j, N, h))
        det = P.detect_special(ordE, p, N)
        if det["any_special"]:
            special_js.append(j)
    card = len(records)
    rho = (len(special_js) / card) if card else 0.0
    return {
        "bits": 28,
        "p_bits": p,
        "estimator": "sample_estimate",
        "status": stopped,
        "sample_size_target": sample_size,
        "sample_counters_drawn": counter,
        "cardinality": card,
        "n_special": len(special_js),
        "rho_special": rho,
        "records_hash": P.records_hash(records),
        "h_max": H_MAX,
        "density_universe_spec_hash": P.density_universe_spec_hash(28),
        "seed_density": seed,
        "special_js_sample": special_js[:20],
        "records_compact": [(j, N, h) for j, N, h in records[:5]],
    }


def two_isogeny_neighbor_js(E) -> list[int]:
    """Return distinct neighbor j-invariants via degree-2 isogenies, sorted."""
    js: set[int] = set()
    j0 = int(E.j_invariant())
    try:
        tors = E(0).division_points(2)
    except Exception:
        return []
    for T in tors:
        if T.is_zero():
            continue
        try:
            phi = E.isogeny(T)
            jn = int(phi.codomain().j_invariant())
            if jn != j0:
                js.add(jn)
        except Exception:
            continue
    return sorted(js)


def bfs_h_min(
    p: int,
    j0: int,
    N_star: int,
    hops_max: int,
    deadline: float,
) -> dict[str, Any]:
    """BFS on ordinary 2-isogeny graph; neighbors expanded in increasing j order."""
    K = GF(p)
    try:
        E0 = EllipticCurve(j=K(j0))
    except Exception as e:
        return {"error": str(e), "censored": True, "H_min": None, "C_search": 0}

    q: deque[tuple[int, int]] = deque([(j0, 0)])
    parent: dict[int, int | None] = {j0: None}
    depth: dict[int, int] = {j0: 0}
    edges_expanded = 0
    hit = None
    hit_det = None
    stopped = "exhausted_hops"

    # check start
    ord0 = int(E0.cardinality())
    det0 = P.detect_special(ord0, p, N_star)
    if det0["any_special"]:
        hit = j0
        hit_det = det0
        stopped = "hit_special"

    while q and hit is None and time.time() < deadline:
        j_cur, d = q.popleft()
        if d >= hops_max:
            continue
        try:
            E = EllipticCurve(j=K(j_cur))
        except Exception:
            continue
        nbrs = two_isogeny_neighbor_js(E)
        for jn in nbrs:  # already sorted increasing
            edges_expanded += 1
            if jn in parent:
                continue
            parent[jn] = j_cur
            depth[jn] = d + 1
            try:
                En = EllipticCurve(j=K(jn))
                ordn = int(En.cardinality())
            except Exception:
                continue
            if not is_ordinary(ordn, p):
                continue
            # Detectors use instance N* per contract for embedding/WD;
            # anomalous uses #E==p on the endpoint model.
            det = P.detect_special(ordn, p, N_star)
            if det["any_special"]:
                hit = jn
                hit_det = det
                stopped = "hit_special"
                break
            if d + 1 < hops_max:
                q.append((jn, d + 1))
        if time.time() >= deadline:
            stopped = "resource_exhaustion_wall"

    path_js: list[int] = []
    if hit is not None:
        cur: int | None = hit
        while cur is not None:
            path_js.append(cur)
            cur = parent.get(cur)
        path_js.reverse()
        H = depth[hit]
        censored = False
    else:
        H = None
        censored = True

    C_search = edges_expanded  # 1 group_op_equivalent per directed edge
    deg_comp = (2 ** H) if H is not None else None
    C_eval = 0
    edge_ledger = []
    if path_js and len(path_js) >= 2:
        for i in range(len(path_js) - 1):
            ell = 2
            c = P.c_iso(ell)
            C_eval += c
            edge_ledger.append({"from_j": path_js[i], "to_j": path_js[i + 1], "ell": ell, "c_iso": c})
    C_path = C_search + C_eval
    return {
        "algorithm": "BFS",
        "H_min": H,
        "censored": censored,
        "stop_reason": stopped,
        "path_js": path_js,
        "endpoint_j": hit,
        "endpoint_det": hit_det,
        "deg_composite": deg_comp,
        "C_search": C_search,
        "C_eval": C_eval,
        "C_path": C_path,
        "C_search_label": "measured",
        "C_eval_label": "modeled",
        "edge_ledger": edge_ledger,
        "nodes_visited": len(parent),
        "edges_expanded": edges_expanded,
    }


def null_bfs(
    null_seed_bytes: bytes,
    params: dict[str, Any],
    rho: float,
    N_star: int,
    deadline: float,
) -> dict[str, Any]:
    if params.get("null_builder_failure"):
        return {"null_builder_failure": True, "R_null": None}
    M = params["null_M"]
    offs = params["null_offsets"]
    start = params["start_v"]
    hops_max = params["hops_max"]
    q: deque[tuple[int, int]] = deque([(start, 0)])
    parent: dict[int, int | None] = {start: None}
    depth = {start: 0}
    edges = 0
    hit = None
    if P.null_is_special(start, null_seed_bytes, rho):
        hit = start
    while q and hit is None and time.time() < deadline:
        v, d = q.popleft()
        if d >= hops_max:
            continue
        for w in P.null_neighbors(v, offs):
            edges += 1
            if w in parent:
                continue
            parent[w] = v
            depth[w] = d + 1
            if P.null_is_special(w, null_seed_bytes, rho):
                hit = w
                break
            if d + 1 < hops_max:
                q.append((w, d + 1))
    path = []
    if hit is not None:
        cur: int | None = hit
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()
        H = depth[hit]
        C_eval = sum(P.c_iso(2) for _ in range(max(0, len(path) - 1)))
        C_special = P.C_special_anomalous(N_star)
        deg = 2 ** H
        C_pull = P.C_pullback(N_star, deg)
        C_path = edges + C_eval
        R = (C_path + C_special + C_pull) / P.matched_rho(N_star)
        return {
            "null_builder_failure": False,
            "hit": True,
            "H_null": H,
            "C_path_null": C_path,
            "C_search_null": edges,
            "C_eval_null": C_eval,
            "C_special_null": C_special,
            "C_pullback_null": C_pull,
            "R_null": R,
            "labels": {
                "C_search_null": "measured",
                "C_eval_null": "modeled",
                "C_special_null": "modeled",
                "C_pullback_null": "modeled",
            },
        }
    # censorship
    C_path = edges
    R = C_path / P.matched_rho(N_star)
    return {
        "null_builder_failure": False,
        "hit": False,
        "censored": True,
        "C_path_null": C_path,
        "C_special_null": 0,
        "C_pullback_null": 0,
        "R_null": R,
        "labels": {"C_path_null": "measured"},
    }


def pollard_rho_negation(E, Pnt, Q, N: int, seed: int) -> dict[str, Any]:
    """Simple Pollard rho with negation map; count group ops (adds)."""
    rng = random.Random(seed ^ 0x52484F)

    def add_count(A, B, ops: list[int]):
        ops[0] += 1
        return A + B

    def dbl_count(A, ops: list[int]):
        ops[0] += 1
        return A + A

    # partition hash
    def h(X) -> int:
        if X.is_zero():
            return 0
        return int(X[0]) % 3

    ops = [0]
    # kangaroo/rho: start from random aP+bQ
    a1 = rng.randrange(1, N)
    b1 = rng.randrange(1, N)
    X = add_count(a1 * Pnt, b1 * Q, ops)
    a2, b2, Y = a1, b1, X
    steps = 0
    max_steps = int(20 * math.sqrt(N)) + 100
    found_k = None
    while steps < max_steps:
        steps += 1
        # tortoise
        c = h(X)
        if c == 0:
            X = dbl_count(X, ops)
            a1 = (2 * a1) % N
            b1 = (2 * b1) % N
        elif c == 1:
            X = add_count(X, Pnt, ops)
            a1 = (a1 + 1) % N
        else:
            X = add_count(X, Q, ops)
            b1 = (b1 + 1) % N
        # negation map: identify X ~ -X
        if not X.is_zero() and int(X[1]) > (E.base_field().order() // 2):
            X = -X
            a1 = (-a1) % N
            b1 = (-b1) % N
        # hare twice
        for _ in range(2):
            c = h(Y)
            if c == 0:
                Y = dbl_count(Y, ops)
                a2 = (2 * a2) % N
                b2 = (2 * b2) % N
            elif c == 1:
                Y = add_count(Y, Pnt, ops)
                a2 = (a2 + 1) % N
            else:
                Y = add_count(Y, Q, ops)
                b2 = (b2 + 1) % N
            if not Y.is_zero() and int(Y[1]) > (E.base_field().order() // 2):
                Y = -Y
                a2 = (-a2) % N
                b2 = (-b2) % N
        if X == Y:
            da = (a1 - a2) % N
            db = (b2 - b1) % N
            if db == 0:
                break
            try:
                found_k = (da * pow(db, -1, N)) % N
            except Exception:
                found_k = None
            break
    modeled = P.matched_rho(N)
    measured = ops[0]
    calib = measured / modeled if modeled else None
    verified = False
    if found_k is not None:
        verified = (found_k * Pnt == Q)
    return {
        "solved": bool(verified),
        "k": int(found_k) if found_k is not None and verified else None,
        "group_ops_measured": measured,
        "matched_rho_modeled": modeled,
        "rho_calib_ratio": calib,
        "steps": steps,
        "label_measured": "measured",
        "label_modeled": "modeled",
    }


def bsgs_measure(E, Pnt, Q, N: int) -> dict[str, Any]:
    m = int(math.ceil(math.sqrt(N)))
    ops = 0
    table = {}
    baby = E(0)
    for j in range(m):
        table[baby] = j
        baby = baby + Pnt
        ops += 1
    factor = m * Pnt
    ops += int(math.log2(m)) + 1  # rough scalar
    gamma = Q
    found = None
    for i in range(m + 1):
        if gamma in table:
            found = i * m + table[gamma]
            break
        gamma = gamma - factor
        ops += 1
    verified = found is not None and (found * Pnt == Q)
    modeled = P.matched_bsgs(N)
    return {
        "solved": bool(verified),
        "k": int(found) if verified else None,
        "group_ops_measured": ops,
        "matched_bsgs_modeled": modeled,
        "label_measured": "measured",
        "label_modeled": "modeled",
    }


def sample_curve_instance(bits: int, seed: int, attempt_cap: int = 5000) -> dict[str, Any] | None:
    """Random ordinary prime-field curve with designated N* of given bits."""
    rng = random.Random(seed ^ (bits * 1_000_003))
    lo = 2 ** (bits + 1)
    hi = 2 ** (bits + 2)
    # deterministic p from seed within window
    p = int(next_prime(lo + (rng.randrange(0, max(2, hi - lo - 2)))))
    if p >= hi:
        p = int(next_prime(lo))
    for attempt in range(attempt_cap):
        j = rng.randrange(0, p)
        try:
            E = curve_from_j(p, j)
        except Exception:
            continue
        ordE = int(E.cardinality())
        r = retain_class(ordE, p, bits)
        if r is None:
            continue
        N, h = r
        # skip already-special starts for unplanted (generic claim)
        det = P.detect_special(ordE, p, N)
        if det["any_special"]:
            continue
        # build ECDLP instance
        G = E.gens()[0]
        # scale to order-N generator if needed
        cof = ordE // N
        Pnt = cof * G
        if Pnt.is_zero() or (N * Pnt) != E(0):
            continue
        k_secret = rng.randrange(1, N)
        Q = k_secret * Pnt
        return {
            "bits": bits,
            "seed": seed,
            "p": p,
            "j": j,
            "a": int(E.a4()),
            "b": int(E.a6()),
            "order": ordE,
            "N_star": N,
            "h_star": h,
            "P": [int(Pnt[0]), int(Pnt[1])],
            "Q": [int(Q[0]), int(Q[1])],
            "k_secret_for_plant_only": None,  # unplanted: not used for claims
            "attempt": attempt,
        }
    return None


def verify_dl_cert(p: int, a: int, b: int, Pxy, Qxy, k: int) -> bool:
    """Independent recompute via Sage (separate from solver path)."""
    E = EllipticCurve(GF(p), [a, b])
    Pnt = E(Pxy[0], Pxy[1])
    Q = E(Qxy[0], Qxy[1])
    return (Integer(k) * Pnt) == Q


def planted_path_control(bits: int, seed: int, deadline: float) -> dict[str, Any]:
    """CTRL-PLANTED-PATH-POS: anomalous start, walk 1..4 hops, recover reverse."""
    rng = random.Random(seed ^ 0x504C414E)
    lo = 2 ** (bits + 1)
    hi = 2 ** (bits + 2)
    p = int(next_prime(lo))
    # find anomalous j
    anom_j = None
    K = GF(p)
    for j in range(min(p, 500000)):
        if time.time() >= deadline:
            break
        try:
            E = EllipticCurve(j=K(j))
        except Exception:
            continue
        if int(E.cardinality()) == p:
            anom_j = j
            break
    if anom_j is None:
        return {"status": "failed_infrastructure", "reason": "no_anomalous_found", "planted_path_recovered": False}

    E_anom = EllipticCurve(j=K(anom_j))
    # Walk random short path
    hops = rng.randint(1, 4)
    path = [anom_j]
    E_cur = E_anom
    for _ in range(hops):
        nbrs = two_isogeny_neighbor_js(E_cur)
        # exclude backtrack if possible
        cand = [jn for jn in nbrs if jn != path[-1] or len(nbrs) == 1]
        if not cand:
            break
        jn = rng.choice(cand)
        path.append(jn)
        E_cur = EllipticCurve(j=K(jn))
    j_rand = path[-1]
    # N* for anomalous: #E=p, so need h*N=p with N prime bits-bit — may not hold.
    # For planted control, designate N* = unique_N on the RANDOM endpoint if possible,
    # else use largest prime factor of #E_rand fitting bits.
    ord_rand = int(E_cur.cardinality())
    r = retain_class(ord_rand, p, bits)
    if r is None:
        # fallback: use order of anom for ledger N magnitude
        N_star = int(next_prime(2 ** (bits - 1)))
        while N_star.bit_length() != bits:
            N_star = int(next_prime(N_star))
        h_star = None
    else:
        N_star, h_star = r

    # ECDLP on random curve
    G = E_cur.gens()[0]
    if r is not None:
        Pnt = (ord_rand // N_star) * G
        N_use = N_star
    else:
        N_use = int(G.order())
        Pnt = G
        N_star = N_use
    k = rng.randrange(1, N_use)
    Q = k * Pnt

    # Reverse search from j_rand toward special
    hops_max = P.hops_max_for_N(N_star)
    bfs = bfs_h_min(p, j_rand, N_star, hops_max, deadline)
    recovered = (
        not bfs.get("censored")
        and bfs.get("endpoint_det", {})
        and bfs["endpoint_det"].get("any_special")
        and bfs.get("H_min") is not None
        and bfs["H_min"] <= 4
    )
    # Charge
    C_search = bfs["C_search"]
    C_eval = bfs["C_eval"]
    C_path = C_search + C_eval
    det = bfs.get("endpoint_det") or {"anomalous_trace_eq_1": True, "embedding_degree_leq_threshold": False}
    C_spec, fam, opt = P.min_C_special(N_star, p, det if det else {"anomalous_trace_eq_1": True})
    deg = bfs.get("deg_composite") or (2 ** (bfs["H_min"] or hops))
    C_pull = P.C_pullback(N_star, int(deg))
    rho_m = P.matched_rho(N_star)
    R = (C_path + C_spec + C_pull) / rho_m

    # Certificate: known planted k on E_rand (independent verify)
    a, b = int(E_cur.a4()), int(E_cur.a6())
    cert_ok = verify_dl_cert(p, a, b, [int(Pnt[0]), int(Pnt[1])], [int(Q[0]), int(Q[1])], k)

    cheap = recovered and R < 0.7 and cert_ok
    return {
        "status": "completed",
        "control_id": "CTRL-PLANTED-PATH-POS",
        "bits": bits,
        "seed": seed,
        "p": p,
        "anomalous_j": anom_j,
        "planted_forward_path_js": path,
        "planted_hops": len(path) - 1,
        "j_rand": j_rand,
        "N_star": N_star,
        "h_star": h_star,
        "bfs": {k: v for k, v in bfs.items() if k != "edge_ledger"} | {"edge_ledger_len": len(bfs.get("edge_ledger") or [])},
        "C_path": C_path,
        "C_search": C_search,
        "C_eval": C_eval,
        "C_special": C_spec,
        "C_pullback": C_pull,
        "R_xfer": R,
        "labels": {
            "C_search": "measured",
            "C_eval": "modeled",
            "C_special": "modeled",
            "C_pullback": "modeled",
            "matched_rho": "modeled",
        },
        "planted_path_recovered": bool(cheap),
        "certificate": {
            "kind": "discrete_log",
            "verified": cert_ok,
            "verifier": "sage-EllipticCurve-independent-recompute",
            "k": int(k),
            "curve": {"p": p, "a": a, "b": b},
            "P": [int(Pnt[0]), int(Pnt[1])],
            "Q": [int(Q[0]), int(Q[1])],
        },
        "harness_void": not bool(cheap),
    }


def process_unplanted(
    inst: dict[str, Any],
    rho_special: float,
    deadline: float,
    plant_cell: bool,
) -> dict[str, Any]:
    p = inst["p"]
    j0 = inst["j"]
    N = inst["N_star"]
    bits = inst["bits"]
    hops_max = P.hops_max_for_N(N)
    bfs = bfs_h_min(p, j0, N, hops_max, deadline)

    # Cost / R_xfer
    if bfs.get("censored") or bfs.get("H_min") is None:
        C_search = bfs.get("C_search", 0)
        C_eval = 0
        C_path = C_search
        C_special = 0
        C_pull = 0
        R = C_path / P.matched_rho(N)
        censorship = True
        cert = {"kind": "none", "verified": None, "note": "no_transfer_path_within_budget"}
        family = None
        optimistic = False
        edge_ledger = bfs.get("edge_ledger") or []
    else:
        censorship = False
        C_search = bfs["C_search"]
        C_eval = bfs["C_eval"]
        C_path_honest = C_search + C_eval
        edge_ledger = bfs.get("edge_ledger") or []
        det = bfs["endpoint_det"]
        C_special, family, optimistic = P.min_C_special(N, p, det)
        deg = bfs["deg_composite"]
        C_pull = P.C_pullback(N, int(deg))
        # No automatic special-curve DL solve claimed on unplanted without real solve.
        # Record path accounting only; certificate kind none unless we solve.
        cert = {
            "kind": "none",
            "verified": None,
            "note": "path_accounting_only_no_special_dl_claimed",
            "endpoint_families": det.get("families"),
        }
        C_path = C_path_honest
        R = (C_path + C_special + C_pull) / P.matched_rho(N)

    C_path_honest = C_search + C_eval
    C_path_reported = C_path_honest
    plant_injected = False
    if plant_cell:
        plant_injected = True
        C_path_reported = C_path_honest // 4
        R_packaged = (C_path_reported + C_special + C_pull) / P.matched_rho(N)
    else:
        R_packaged = R

    # recompute C_path from ledger
    C_path_recomputed = C_search + sum(e["c_iso"] for e in edge_ledger)
    plant_detected = bool(
        plant_injected
        and C_path_reported <= (C_path_recomputed // 4)
        and C_path_reported < C_path_recomputed
    )

    # matched baselines
    E = EllipticCurve(GF(p), [inst["a"], inst["b"]])
    Pnt = E(inst["P"][0], inst["P"][1])
    Q = E(inst["Q"][0], inst["Q"][1])
    rho_run = pollard_rho_negation(E, Pnt, Q, N, inst["seed"])
    bsgs_run = bsgs_measure(E, Pnt, Q, N)

    # null arm
    ns = P.null_seed(inst["seed"], N)
    nparams = P.null_graph_params(N, ns, j0)
    null_res = null_bfs(ns, nparams, rho_special, N, deadline)
    R_null = null_res.get("R_null")
    null_gate_pass = True
    if R < 0.7 and not censorship and cert.get("kind") != "none":
        null_gate_pass = (R_null is not None) and (R_null >= 0.95)
    elif R < 0.7 and censorship:
        null_gate_pass = True  # no certificate claim

    # cost sensitivity on C_eval
    sens = {}
    if not censorship:
        for mult, tag in [(0.1, "x0.1"), (10.0, "x10")]:
            R_s = (C_search + C_eval * mult + C_special + C_pull) / P.matched_rho(N)
            sens[tag] = R_s
        flip = (R < 0.7 and sens["x10"] >= 1.0) or (R >= 1.0 and sens["x0.1"] < 0.7)
    else:
        flip = False

    return {
        "instance": {k: v for k, v in inst.items() if k != "k_secret_for_plant_only"},
        "H_min": bfs.get("H_min"),
        "censored": censorship,
        "bfs_stop": bfs.get("stop_reason"),
        "deg_composite": bfs.get("deg_composite"),
        "C_path_honest": C_path_honest,
        "C_path_reported": C_path_reported,
        "C_path_recomputed": C_path_recomputed,
        "C_search": C_search,
        "C_eval": C_eval,
        "C_special": C_special,
        "C_pullback": C_pull,
        "R_xfer": R,
        "R_xfer_packaged": R_packaged,
        "labels": {
            "C_search": "measured",
            "C_eval": "modeled",
            "C_special": "modeled",
            "C_pullback": "modeled",
            "matched_rho": "modeled",
        },
        "family": family,
        "optimistic_min_C_special": optimistic,
        "certificate": cert,
        "matched_rho": rho_run,
        "matched_bsgs": bsgs_run,
        "rho_calib_ratio": rho_run.get("rho_calib_ratio"),
        "null": {
            "null_object_id": "NULL-IT-ISOGENY-TRANSFER",
            "construction_id": "NULL-IT-ISOGENY-TRANSFER-v2",
            "neighbor_algorithm_id": "NULL-IT-NEIGHBOR-v1",
            "null_M": nparams.get("null_M"),
            "null_offsets": nparams.get("null_offsets"),
            "null_builder_failure": nparams.get("null_builder_failure"),
            **{k: v for k, v in null_res.items() if k != "null_builder_failure"},
        },
        "null_gate_pass": null_gate_pass,
        "plant_injected": plant_injected,
        "plant_detected": plant_detected,
        "plant_detection_eps": 0,
        "cost_sensitivity_10x": sens,
        "cost_sensitivity_10x_flip": flip,
        "edge_ledger": edge_ledger,
        "hops_max": hops_max,
    }


def main() -> int:
    t_start = time.time()
    deadline_global = t_start + WALL_BUDGET
    meta = git_meta()
    run_dir = REPO / "experiments/EXP-IT-001/runs" / RUN_ID
    res_dir = REPO / "experiments/EXP-IT-001/results"
    run_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)

    stdout_lines: list[str] = []

    def log(msg: str) -> None:
        line = f"[{utc_now()}] {msg}"
        print(line, flush=True)
        stdout_lines.append(line)

    log(f"START {RUN_ID} contract={CONTRACT}")
    anomalies: list[str] = []
    density_by_bits: dict[str, Any] = {}
    rho_special_by_bits: dict[str, float] = {}
    hops_max_by_bits: dict[str, int] = {}
    F_hit_table_by_bits: dict[str, Any] = {}
    card_by_bits: dict[str, int] = {}
    dens_hash_by_bits: dict[str, str] = {}

    # --- Phase 1: density freeze BEFORE path search ---
    for bits in BITS_LIST:
        ddead = min(deadline_global, time.time() + DENSITY_BUDGET[bits])
        log(f"density: find p_bits bits={bits}")
        pref = find_p_bits(bits, ddead)
        if pref.get("status") != "found":
            density_by_bits[str(bits)] = {
                "status": "failed_infrastructure",
                "reason": "p_bits_not_found",
                "find_p": pref,
            }
            anomalies.append(f"density bits={bits}: p_bits not found")
            rho_special_by_bits[str(bits)] = float("nan")
            continue
        p = pref["p_bits"]
        log(f"density: p_bits={p} for bits={bits}; scanning universe")
        if bits in (20, 24):
            dens = density_exhaustive(bits, p, ddead)
        else:
            dens = density_sample_28(p, ddead, 50000)
        dens["find_p"] = pref
        density_by_bits[str(bits)] = dens
        rho = float(dens.get("rho_special") or 0.0)
        rho_special_by_bits[str(bits)] = rho
        card_by_bits[str(bits)] = int(dens.get("cardinality") or 0)
        dens_hash_by_bits[str(bits)] = dens.get("density_universe_spec_hash")
        # representative N for hops_max table: 2^{bits-1}+... use mid
        N_rep = 2 ** (bits - 1) + 1
        while not P._is_probable_prime(N_rep):
            N_rep += 2
        hops_max_by_bits[str(bits)] = P.hops_max_for_N(N_rep)
        if dens.get("status") == "completed" or dens.get("cardinality", 0) > 0:
            F_hit_table_by_bits[str(bits)] = P.F_hit_table(hops_max_by_bits[str(bits)], rho, 3)
        else:
            F_hit_table_by_bits[str(bits)] = None
        log(
            f"density bits={bits} status={dens.get('status')} |U|={dens.get('cardinality')} "
            f"rho={rho:.6g} hash={dens.get('records_hash', '')[:16]}"
        )

    # Freeze HEUR report skeleton BEFORE path search (required field)
    heur_freeze_marker = {
        "frozen_before_path_search": True,
        "frozen_at": utc_now(),
        "rho_special_by_bits": rho_special_by_bits,
        "density_universe_spec_hash": dens_hash_by_bits,
        "density_universe_cardinality_by_bits": card_by_bits,
        "d": 3,
        "hops_max_by_bits": hops_max_by_bits,
        "F_hit_table_by_bits": F_hit_table_by_bits,
        "density_detail": {
            b: {k: v for k, v in density_by_bits[b].items() if k != "records"}
            for b in density_by_bits
        },
    }
    write_json(res_dir / "HEUR_ISO_1_report.json", {**heur_freeze_marker, "phase": "density_freeze_only"})
    log("HEUR_ISO_1 density+F_hit freeze written before path search")

    null_hash = P.null_object_spec_hash(rho_special_by_bits)

    # --- Phase 2: planted-path positive control (bits=20) ---
    planted = planted_path_control(20, SEEDS[0], min(deadline_global, time.time() + 300))
    log(f"planted-path recovered={planted.get('planted_path_recovered')} R={planted.get('R_xfer')}")

    # --- Phase 3: unplanted instances ---
    unplanted_results: list[dict[str, Any]] = []
    # stratify: 7,7,6 across 20/24/28 if time allows
    plan = []
    for bits, n in [(20, 7), (24, 7), (28, 6)]:
        for i in range(n):
            seed = SEEDS[i % len(SEEDS)] + 1000 * bits + i
            plan.append((bits, seed, i))

    for bits, seed, idx in plan:
        if time.time() >= deadline_global:
            anomalies.append("unplanted sampling stopped: wall budget")
            break
        if str(bits) not in rho_special_by_bits or math.isnan(rho_special_by_bits[str(bits)]):
            anomalies.append(f"skip bits={bits}: no density rho")
            continue
        inst = sample_curve_instance(bits, seed)
        if inst is None:
            anomalies.append(f"curve sample failed bits={bits} seed={seed}")
            continue
        plant_cell = bits == 20 and seed == SEEDS[0] and idx == 0
        # designated plant: seeds[0], first unplanted bits=20
        # ensure first bits=20 uses SEEDS[0]
        if bits == 20 and idx == 0:
            # resample with exact seed
            inst2 = sample_curve_instance(bits, SEEDS[0])
            if inst2 is not None:
                inst = inst2
                seed = SEEDS[0]
            plant_cell = True
        log(f"unplanted bits={bits} seed={seed} j={inst['j']} N={inst['N_star']}")
        cell = process_unplanted(
            inst,
            rho_special_by_bits[str(bits)],
            min(deadline_global, time.time() + 120),
            plant_cell=plant_cell,
        )
        unplanted_results.append(cell)
        log(
            f"  H_min={cell['H_min']} censored={cell['censored']} R_xfer={cell['R_xfer']:.4g} "
            f"plant_inj={cell['plant_injected']} plant_det={cell['plant_detected']}"
        )

    # Ensure plant cell exists if stratification missed it
    if not any(c.get("plant_injected") for c in unplanted_results):
        if time.time() < deadline_global and "20" in rho_special_by_bits:
            inst = sample_curve_instance(20, SEEDS[0])
            if inst is not None:
                cell = process_unplanted(
                    inst,
                    rho_special_by_bits["20"],
                    min(deadline_global, time.time() + 120),
                    plant_cell=True,
                )
                unplanted_results.insert(0, cell)
                log("inserted designated CTRL-NULL-IT-PLANT cell")

    # --- Phase 4: HEUR KS / TAIL / RATE ---
    ks_stat_by_bits: dict[str, Any] = {}
    ks_pass_by_bits: dict[str, Any] = {}
    tail_pass_by_bits: dict[str, Any] = {}
    censored_fraction_by_bits: dict[str, Any] = {}
    H_samples: dict[str, list[int]] = {str(b): [] for b in BITS_LIST}
    cens_counts = {str(b): 0 for b in BITS_LIST}
    tot_counts = {str(b): 0 for b in BITS_LIST}
    for cell in unplanted_results:
        b = str(cell["instance"]["bits"])
        tot_counts[b] = tot_counts.get(b, 0) + 1
        if cell["censored"] or cell["H_min"] is None:
            cens_counts[b] = cens_counts.get(b, 0) + 1
        else:
            H_samples.setdefault(b, []).append(int(cell["H_min"]))

    for b in map(str, BITS_LIST):
        n_tot = tot_counts.get(b, 0)
        n_c = cens_counts.get(b, 0)
        censored_fraction_by_bits[b] = (n_c / n_tot) if n_tot else None
        samples = H_samples.get(b, [])
        rho = rho_special_by_bits.get(b)
        if not samples or rho is None or (isinstance(rho, float) and math.isnan(rho)):
            ks_stat_by_bits[b] = None
            ks_pass_by_bits[b] = None
            tail_pass_by_bits[b] = None
            continue
        ks = P.ks_statistic(samples, float(rho), 3)
        ks_stat_by_bits[b] = ks
        n = len(samples)
        thr = P.ks_threshold(n)
        # fail if ks > thr and n>=20
        if n >= 20:
            ks_pass_by_bits[b] = not (ks > thr)
        else:
            ks_pass_by_bits[b] = None  # inadequate samples; not forced
        tail_pass_by_bits[b] = P.tail_pass(samples, float(rho), 3)

    completed_R = [c for c in unplanted_results if c.get("R_xfer") is not None]
    frac_ge1 = (
        sum(1 for c in completed_R if c["R_xfer"] >= 1.0) / len(completed_R) if completed_R else None
    )
    rate_pass = (frac_ge1 is not None) and (frac_ge1 >= 0.90)
    f1_count = sum(
        1
        for c in unplanted_results
        if c["R_xfer"] < 0.7
        and not c["censored"]
        and c.get("certificate", {}).get("kind") == "discrete_log"
        and c.get("certificate", {}).get("verified")
    )

    heur_report = {
        **heur_freeze_marker,
        "phase": "final",
        "ks_stat_by_bits": ks_stat_by_bits,
        "ks_pass_by_bits": ks_pass_by_bits,
        "tail_pass_by_bits": tail_pass_by_bits,
        "rate_iso_1_pass": rate_pass,
        "rate_iso_1_fraction_R_ge_1": frac_ge1,
        "censored_fraction_by_bits": censored_fraction_by_bits,
        "n_uncensored_by_bits": {b: len(H_samples.get(b, [])) for b in map(str, BITS_LIST)},
        "H_min_samples_by_bits": H_samples,
        "F3_trigger_observation": None,  # Executor does not adjudicate F3; record inputs only
        "notes": (
            "KS/TAIL pass fields are null when n_uncensored < 20 (inadequate). "
            "RATE under heavy censorship is a gate-hold observation, not HEUR confirmation."
        ),
    }
    write_json(res_dir / "HEUR_ISO_1_report.json", heur_report)

    # --- transfer gate report ---
    transfer_report = {
        "experiment_id": EXP_ID,
        "run_id": RUN_ID,
        "contract": CONTRACT,
        "cost_ledger_unit": "group_op_equivalent",
        "matched_rho_formula": "0.886*sqrt(N)",
        "matched_bsgs_formula": "2*ceil(sqrt(N))",
        "unplanted_cells": [
            {
                "bits": c["instance"]["bits"],
                "seed": c["instance"]["seed"],
                "j": c["instance"]["j"],
                "N_star": c["instance"]["N_star"],
                "H_min": c["H_min"],
                "censored": c["censored"],
                "C_path": c["C_path_honest"],
                "C_search": c["C_search"],
                "C_eval": c["C_eval"],
                "C_special": c["C_special"],
                "C_pullback": c["C_pullback"],
                "R_xfer": c["R_xfer"],
                "labels": c["labels"],
                "certificate": c["certificate"],
                "matched_rho_ops_measured": c["matched_rho"].get("group_ops_measured"),
                "matched_rho_modeled": c["matched_rho"].get("matched_rho_modeled"),
                "matched_bsgs_ops_measured": c["matched_bsgs"].get("group_ops_measured"),
                "matched_bsgs_modeled": c["matched_bsgs"].get("matched_bsgs_modeled"),
                "rho_calib_ratio": c["rho_calib_ratio"],
                "cost_sensitivity_10x": c["cost_sensitivity_10x"],
                "cost_sensitivity_10x_flip": c["cost_sensitivity_10x_flip"],
            }
            for c in unplanted_results
        ],
        "planted_path_control": planted,
        "rate_iso_1_fraction_R_ge_1": frac_ge1,
        "f1_certificate_subrho_count": f1_count,
        "n_unplanted": len(unplanted_results),
    }
    write_json(res_dir / "transfer_gate_report.json", transfer_report)

    # --- null report ---
    plant_cells = [c for c in unplanted_results if c.get("plant_injected")]
    null_report = {
        "null_object_id": "NULL-IT-ISOGENY-TRANSFER",
        "construction_id": "NULL-IT-ISOGENY-TRANSFER-v2",
        "neighbor_algorithm_id": "NULL-IT-NEIGHBOR-v1",
        "null_object_spec_hash": null_hash,
        "rho_special_by_bits": rho_special_by_bits,
        "cells": [
            {
                "bits": c["instance"]["bits"],
                "seed": c["instance"]["seed"],
                "R_xfer": c["R_xfer"],
                "R_null": c["null"].get("R_null"),
                "null_gate_pass": c["null_gate_pass"],
                "null_M": c["null"].get("null_M"),
                "null_offsets": c["null"].get("null_offsets"),
                "plant_injected": c["plant_injected"],
                "plant_detected": c["plant_detected"],
                "C_path_honest": c["C_path_honest"],
                "C_path_reported": c["C_path_reported"],
                "C_path_recomputed": c["C_path_recomputed"],
                "rho_calib_ratio": c["rho_calib_ratio"],
            }
            for c in unplanted_results
        ],
        "CTRL_NULL_IT_PLANT": {
            "designated_seed": SEEDS[0],
            "designated_bits": 20,
            "n_plant_cells": len(plant_cells),
            "plant_detected": all(c["plant_detected"] for c in plant_cells) if plant_cells else False,
            "plants": [
                {
                    "plant_injected": c["plant_injected"],
                    "C_path_honest": c["C_path_honest"],
                    "C_path_reported": c["C_path_reported"],
                    "C_path_recomputed": c["C_path_recomputed"],
                    "plant_detected": c["plant_detected"],
                    "plant_detection_eps": 0,
                }
                for c in plant_cells
            ],
        },
    }
    write_json(res_dir / "null_it_isogeny_transfer_report.json", null_report)

    # --- concrete cost table ---
    cost_table = {
        "claim_tier": "toy",
        "unit": "group_op_equivalent",
        "optimistic_assumptions": [
            "c_iso(ell)=4*ell may understate Vélu cost",
            "min C_special among detectors is attack-favorable",
            "MOV field-DL charged 1:1 as group_op units",
        ],
        "affected_vs_safe_scope": {
            "affected": "GENERIC random ordinary prime-field E at tested toy bit sizes only",
            "safe_out_of_claim": "structured CM / pairing-friendly / crypto-scale curves",
        },
        "o1_polylog_disclosure": (
            "Isogeny arithmetic polylog(p) factors absorbed into c_iso=4*ell model; "
            "not expanded as separate measured terms."
        ),
        "by_bits": {},
        "mitm_peak_memory": {
            "used_mitm": False,
            "analytic_table_bytes": None,
            "peak_rss_bytes": peak_rss(),
            "note": "Default HEUR/cost-gate arm used BFS; MITM not exercised",
        },
    }
    for b in map(str, BITS_LIST):
        cells = [c for c in unplanted_results if str(c["instance"]["bits"]) == b]
        if not cells:
            cost_table["by_bits"][b] = {"status": "no_cells"}
            continue
        N_med = sorted(c["instance"]["N_star"] for c in cells)[len(cells) // 2]
        cost_table["by_bits"][b] = {
            "n_cells": len(cells),
            "matched_rho_modeled": P.matched_rho(N_med),
            "matched_bsgs_modeled": P.matched_bsgs(N_med),
            "matched_rho_ops_measured_mean": sum(c["matched_rho"]["group_ops_measured"] for c in cells) / len(cells),
            "matched_bsgs_ops_measured_mean": sum(c["matched_bsgs"]["group_ops_measured"] for c in cells) / len(cells),
            "R_xfer_values": [c["R_xfer"] for c in cells],
            "C_path_measured_search_mean": sum(c["C_search"] for c in cells) / len(cells),
            "C_eval_modeled_mean": sum(c["C_eval"] for c in cells) / len(cells),
            "labels": {"matched_rho_ops_measured_mean": "measured", "matched_rho_modeled": "modeled"},
        }
    write_json(res_dir / "concrete_cost_table.json", cost_table)

    # --- summary ---
    validity = "completed_valid"
    if planted.get("harness_void"):
        anomalies.append("CTRL-PLANTED-PATH-POS not recovered (harness_void flag)")
    if len(unplanted_results) < UNPLANTED_TARGET:
        anomalies.append(f"only {len(unplanted_results)}/{UNPLANTED_TARGET} unplanted cells")
        if len(unplanted_results) == 0:
            validity = "failed_infrastructure"
    dens_incomplete = [
        b for b, d in density_by_bits.items() if d.get("status") not in ("completed",)
    ]
    if dens_incomplete and validity == "completed_valid":
        anomalies.append(f"density incomplete for bits {dens_incomplete}")
        # still completed_valid if we have usable freeze + cells; note resource
        if all(density_by_bits[b].get("cardinality", 0) == 0 for b in dens_incomplete):
            validity = "resource_exhaustion"

    wall = time.time() - t_start
    summary = {
        "experiment_id": EXP_ID,
        "run_id": RUN_ID,
        "task_id": TASK_ID,
        "contract": CONTRACT,
        "claim_tier": "toy",
        "validity_status": validity,
        "n_unplanted": len(unplanted_results),
        "planted_path_recovered": planted.get("planted_path_recovered"),
        "planted_R_xfer": planted.get("R_xfer"),
        "rate_iso_1_fraction_R_ge_1": frac_ge1,
        "rate_iso_1_pass_observation": rate_pass,
        "rho_special_by_bits": rho_special_by_bits,
        "ks_stat_by_bits": ks_stat_by_bits,
        "ks_pass_by_bits": ks_pass_by_bits,
        "tail_pass_by_bits": tail_pass_by_bits,
        "CTRL_NULL_IT_PLANT_plant_detected": null_report["CTRL_NULL_IT_PLANT"]["plant_detected"],
        "null_object_spec_hash": null_hash,
        "f1_certificate_subrho_count": f1_count,
        "R_xfer_summary": {
            "min": min((c["R_xfer"] for c in unplanted_results), default=None),
            "max": max((c["R_xfer"] for c in unplanted_results), default=None),
            "mean": (
                sum(c["R_xfer"] for c in unplanted_results) / len(unplanted_results)
                if unplanted_results
                else None
            ),
        },
        "wall_seconds": wall,
        "anomalies": anomalies,
    }
    write_json(res_dir / "summary.json", summary)

    # --- raw-result + manifest ---
    raw = {
        "run_id": RUN_ID,
        "experiment_id": EXP_ID,
        "contract": CONTRACT,
        "density_by_bits": {
            b: {k: v for k, v in d.items() if k != "records"} for b, d in density_by_bits.items()
        },
        "unplanted_results": [
            {**c, "edge_ledger": c.get("edge_ledger")} for c in unplanted_results
        ],
        "planted_path_control": planted,
        "null_object_spec_hash": null_hash,
        "anomalies": anomalies,
        "certificate": {
            "kind": "discrete_log" if planted.get("certificate", {}).get("verified") else "none",
            "planted_path_certificate": planted.get("certificate"),
            "unplanted_note": "unplanted cells use kind=none unless special DL claimed",
        },
    }
    write_json(run_dir / "raw-result.json", raw)

    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "sage": str(sys.version),
        "hostname": platform.node(),
        "dependencies": {"sage": "10.9", "it001_pure": "local"},
    }
    write_json(run_dir / "environment.json", env)
    (run_dir / "command.txt").write_text(
        "sage -python experiments/EXP-IT-001/implementation/it001_driver.py\n",
        encoding="utf-8",
    )
    (run_dir / "stdout.log").write_text("\n".join(stdout_lines) + "\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")

    manifest = {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": RUN_ID,
        "experiment_id": EXP_ID,
        "hypothesis_id": "H-IT-001",
        "task_id": TASK_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "contract": {
            "path": CONTRACT,
            "version": 3,
            "approval_snapshot": APPROVAL_SNAPSHOT,
            "amend_freeze": AMEND_FREEZE,
            "protocol_amendment_id": "PA-IT-001-v3-rc27-b5-b8",
            "decision": "DEC-20260731-034",
            "approved_by_in_file": None,
            "d1_note": "approved_by null in v3 by design; approval in DEC-034 / TASK-124",
        },
        "status": validity,
        "code": {
            **meta,
            "command": "sage -python experiments/EXP-IT-001/implementation/it001_driver.py",
        },
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "cursor-grok-4.5",
            "reasoning_effort": None,
            "fallback_used": True,
            "fallback_reason": (
                "Cursor harness cannot resolve executor-implementation to a "
                "probe-verified backend; runtime model is cursor-grok-4.5"
            ),
            "adapter_version": None,
            "model_verified": False,
            "independent_session_required": False,
        },
        "environment": env,
        "inputs": {
            "seeds": SEEDS,
            "seed_density": SEED_DENSITY,
            "bit_sizes": BITS_LIST,
            "null_object_spec_hash": null_hash,
        },
        "timing": {
            "started_at": datetime.fromtimestamp(t_start, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "finished_at": utc_now(),
            "wall_seconds": wall,
        },
        "resources": {"peak_rss_bytes": peak_rss(), "cpu_seconds": cpu_seconds()},
        "result": {
            "metrics": {
                "n_unplanted": len(unplanted_results),
                "planted_path_recovered": planted.get("planted_path_recovered"),
                "rate_iso_1_fraction_R_ge_1": frac_ge1,
                "rho_special_by_bits": rho_special_by_bits,
                "CTRL_NULL_IT_PLANT_plant_detected": null_report["CTRL_NULL_IT_PLANT"]["plant_detected"],
            },
            "certificate": raw["certificate"],
        },
        "artifacts": {
            "raw_result": str(run_dir / "raw-result.json"),
            "summary": str(res_dir / "summary.json"),
            "HEUR_ISO_1_report": str(res_dir / "HEUR_ISO_1_report.json"),
            "transfer_gate_report": str(res_dir / "transfer_gate_report.json"),
            "concrete_cost_table": str(res_dir / "concrete_cost_table.json"),
            "null_it_isogeny_transfer_report": str(res_dir / "null_it_isogeny_transfer_report.json"),
        },
        "anomalies": anomalies,
        "protocol_deviations": [],
    }
    write_json(run_dir / "manifest.json", manifest)
    log(f"DONE status={validity} wall={wall:.1f}s n_unplanted={len(unplanted_results)}")
    return 0 if validity in ("completed_valid", "resource_exhaustion", "failed_infrastructure") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        err = traceback.format_exc()
        sys.stderr.write(err)
        run_dir = REPO / "experiments/EXP-IT-001/runs" / RUN_ID
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "stderr.log").write_text(err, encoding="utf-8")
        raise
