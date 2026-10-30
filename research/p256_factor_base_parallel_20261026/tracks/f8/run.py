#!/usr/bin/env python3
"""Frozen F8 undisclosed-label orbit panel. Import and --help take no data."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TASK = "TASK-20261026-7324bb"


class Watchdog(Exception):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, obj):
    data = json.dumps(obj, indent=2, allow_nan=False).encode()+b"\n"
    if len(data) > 60000:
        raise ValueError("Retain large arrays in explicit shards: "+str(path))
    with path.open("xb") as stream:
        stream.write(data)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def observed_source():
    rel = str(Path(__file__).resolve().relative_to(REPO))
    return {"head": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain")),
            "instrument_commit": git("log", "-1", "--format=%H", "--", rel), "instrument_path": rel,
            "instrument_source_sha256": sha(Path(__file__).read_bytes()),
            "binary_path": str(Path(sys.executable).resolve()),
            "binary_sha256": sha(Path(sys.executable).resolve().read_bytes()),
            "analysis_sha256": sha((HERE/"analysis.py").read_bytes())}


def host_record():
    model = next((x.partition(":")[2].strip() for x in Path("/proc/cpuinfo").read_text().splitlines()
                  if x.startswith("model name")), None)
    return {"cpu_model": model, "logical_cpus": os.cpu_count(), "kernel": platform.release(),
            "python": platform.python_version(), "host": platform.node(), "threads": 1,
            "isolation": {"tier": "L0", "blockers": ["shared managed host; no timing claim"]}}


def parameters():
    return {"name": "secp256k1", "p": 2**256-2**32-977, "a": 0, "b": 7,
            "r": int("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141", 16), "h": 1,
            "G": (int("79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798", 16),
                  int("483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8", 16)),
            "authority": "SEC 2 v2.0 section 2.4.1; published group facts inherited"}


def arithmetic(C, counts):
    p = C["p"]
    def count(name):
        counts[name] = counts.get(name, 0)+1
    def neg(P):
        return None if P is None else (P[0], -P[1] % p)
    def add(P, Q):
        count("affine_add_calls")
        if P is None:
            return Q
        if Q is None:
            return P
        x, y = P
        u, v = Q
        if x == u:
            if (y+v) % p == 0:
                return None
            slope = 3*x*x*pow(2*y, -1, p) % p
        else:
            slope = (v-y)*pow((u-x) % p, -1, p) % p
        count("affine_inversions")
        z = (slope*slope-x-u) % p
        return z, (slope*(x-z)-y) % p
    def mul(k, P):
        count("affine_mul_calls")
        if k < 0:
            return mul(-k, neg(P))
        R = None
        while k:
            if k & 1:
                R = add(R, P)
            P = add(P, P)
            k >>= 1
        return R
    def jpoint(P):
        return (0, 1, 0) if P is None else (P[0], P[1], 1)
    def jdouble(P):
        count("jacobian_double_calls")
        X, Y, Z = P
        if not Z or not Y:
            return (0, 1, 0)
        YY = Y*Y % p
        S = 4*X*YY % p
        M = 3*X*X % p
        x = (M*M-2*S) % p
        return x, (M*(S-x)-8*YY*YY) % p, 2*Y*Z % p
    def jadd(P, Q):
        count("jacobian_add_calls")
        X, Y, Z = P
        U, V, W = Q
        if not Z:
            return Q
        if not W:
            return P
        z2, w2 = Z*Z % p, W*W % p
        a, b = X*w2 % p, U*z2 % p
        c, d = Y*W*w2 % p, V*Z*z2 % p
        if a == b:
            return jdouble(P) if c == d else (0, 1, 0)
        h, rr = (b-a) % p, (d-c) % p
        h2 = h*h % p
        h3 = h*h2 % p
        x = (rr*rr-h3-2*a*h2) % p
        return x, (rr*(a*h2-x)-c*h3) % p, h*Z*W % p
    def normalize(P):
        X, Y, Z = P
        if not Z:
            return None
        count("jacobian_normalization_inversions")
        inverse = pow(Z, -1, p)
        return X*inverse*inverse % p, Y*inverse**3 % p
    def jmul(k, P):
        count("jacobian_mul_calls")
        if k < 0:
            return jmul(-k, neg(P))
        R, Q = (0, 1, 0), jpoint(P)
        for bit in bin(k)[2:]:
            R = jdouble(R)
            if bit == "1":
                R = jadd(R, Q)
        return normalize(R)
    def lift(x):
        rhs = (x*x*x+7) % p
        y = pow(rhs, (p+1)//4, p)
        return (x % p, min(y, p-y)) if y*y % p == rhs else None
    return neg, add, mul, jpoint, jadd, normalize, jmul, lift


def hashed_point(seed, label, C, lift, draws, forbidden=None, beta=None):
    for attempt in range(4096):
        message = f"p256-factor-pass2/F8/{seed}/{label}/{attempt}".encode()
        x = int.from_bytes(hashlib.sha256(message).digest(), "big") % C["p"]
        P = lift(x)
        collision = False
        if P is not None and forbidden is not None:
            collision = any((beta**j*P[0] % C["p"], sign*P[1] % C["p"]) in forbidden
                            for j in range(3) for sign in (1, -1))
        draws.append({"label": label, "attempt": attempt, "x": x,
                      "lifts": P is not None, "orbit_collision": collision,
                      "accepted": P is not None and not collision})
        if P is not None and not collision:
            return P
    raise RuntimeError("Fixed 4096-attempt fixture limit reached; no retrospective replacement")


def rank_mod(rows, columns, r):
    A = [[v % r for v in row] for row in rows]
    if not A:
        return 0
    assert all(len(row) == columns for row in A)
    pivot = 0
    for column in range(columns):
        selected = next((j for j in range(pivot, len(A)) if A[j][column]), None)
        if selected is None:
            continue
        A[pivot], A[selected] = A[selected], A[pivot]
        inverse = pow(A[pivot][column], -1, r)
        A[pivot] = [value*inverse % r for value in A[pivot]]
        for j in range(pivot+1, len(A)):
            coefficient = A[j][column]
            if coefficient:
                A[j] = [(a-coefficient*b) % r for a, b in zip(A[j], A[pivot])]
        pivot += 1
        if pivot == len(A):
            break
    return pivot


def independent_rank(rows, columns, r):
    if not rows:
        return 0
    import sympy as S
    from sympy.polys.matrices import DomainMatrix
    return int(DomainMatrix.from_Matrix(S.Matrix(rows)).convert_to(S.GF(r)).rank())


def pair_table(points, add):
    table = {}
    count = 0
    for i in range(len(points)):
        for j in range(i, len(points)):
            table.setdefault(add(points[i], points[j]), []).append((i, j))
            count += 1
    return table, count


def collect(target, points, table, add, neg):
    matches = []
    for k, P in enumerate(points):
        for i, j in table.get(add(target, neg(P)), []):
            if j <= k:
                matches.append((i, j, k))
    return sorted(matches)


def complete_oracle(points, requested, jpoint, jadd, normalize):
    """Independent projective enumeration of every unordered signed triple."""
    found = {target: [] for target in requested}
    digest = hashlib.sha256()
    count = 0
    J = [jpoint(P) for P in points]
    for i in range(len(points)):
        for j in range(i, len(points)):
            pair = jadd(J[i], J[j])
            for k in range(j, len(points)):
                value = normalize(jadd(pair, J[k]))
                if value in found:
                    found[value].append((i, j, k))
                digest.update(canonical([i, j, k, value])+b"\n")
                count += 1
    return {key: sorted(value) for key, value in found.items()}, count, digest.hexdigest()


def coefficient_row(triple, length):
    row = [0]*length
    for i in triple:
        row[i] += 1
    return row


def compressed(row, representative_index, factors, r):
    out = [0]*8
    for coefficient, rep, factor in zip(row, representative_index, factors):
        out[rep] = (out[rep]+coefficient*factor) % r
    return out


def sparse(row):
    return [[i, v] for i, v in enumerate(row) if v]


def checked_ranks(R, Crows, constraints, r):
    objects = {"full_relations": (R, 48), "symmetry": (constraints, 48),
               "stacked": (R+constraints, 48), "compressed": (Crows, 8)}
    result = {}
    for label, (rows, columns) in objects.items():
        first, second = rank_mod(rows, columns, r), independent_rank(rows, columns, r)
        assert first == second
        result[label] = first
    assert result["stacked"]-result["symmetry"] == result["compressed"]
    return result


def historical_control(C, neg, add, mul):
    old = REPO/"research/p256_factor_base_parallel_20261025/tracks/f8"
    identity = json.loads((old/"orbit_certificate.json").read_text())
    points = [tuple(P) for P in identity["points"]]
    rows, reduced, inputs = [], [], []
    for path in sorted(old.glob("matrix_block_*.json")):
        raw = path.read_bytes()
        inputs.append({"path": str(path.relative_to(REPO)), "sha256": sha(raw)})
        for item in json.loads(raw):
            row = item["full"]
            total = None
            for value, P in zip(row, points):
                if value:
                    total = add(total, mul(value, P))
            assert total is None
            small = compressed(row, identity["representative_index"], identity["compression_factor"], C["r"])
            assert small == item["compressed"]
            rows.append(row)
            reduced.append(small)
    constraints = json.loads((old/"symmetry_constraints.json").read_text())
    ranks = checked_ranks(rows, reduced, constraints, C["r"])
    assert ranks == {"full_relations": 42, "symmetry": 40, "stacked": 47, "compressed": 7}
    return {"constructed_historical_regression_only": True, "rows": len(rows), "ranks": ranks,
            "input_sha256": inputs, "expected_ranks_are_prior_control_values": True}


def panel(seed, out, records, counters):
    from math import comb
    C = parameters()
    p, r, G = C["p"], C["r"], C["G"]
    neg, add, mul, jpoint, jadd, normalize, jmul, lift = arithmetic(C, counters)
    beta = pow(2, (p-1)//3, p)
    lam = 37718080363155996902926221483475020450927657555482586988616620542887997980018
    assert beta != 1 and (beta*beta+beta+1) % p == 0
    assert lam != 1 and (lam*lam+lam+1) % r == 0
    psi = lambda P: None if P is None else (beta*P[0] % p, P[1])
    assert (G[1]*G[1]-G[0]**3-7) % p == 0
    assert mul(r, G) is None and jmul(r, G) is None
    assert mul(lam, G) == psi(G) == jmul(lam, G)
    draws, representatives, forbidden = [], [], set()
    for i in range(8):
        P = hashed_point(seed, f"representative-{i}", C, lift, draws, forbidden, beta)
        representatives.append(P)
        for j in range(3):
            for sign in (1, -1):
                forbidden.add((beta**j*P[0] % p, sign*P[1] % p))
    points, factors, rep_index = [], [], []
    map_checks = []
    for i, P in enumerate(representatives):
        assert mul(r, P) is None and jmul(r, P) is None
        for j in range(3):
            for sign in (1, -1):
                point = (beta**j*P[0] % p, sign*P[1] % p)
                factor = sign*pow(lam, j, r) % r
                assert mul(factor, P) == point == jmul(factor, P)
                assert psi(point) == mul(lam, point) == jmul(lam, point)
                points.append(point)
                factors.append(factor)
                rep_index.append(i)
                map_checks.append({"point_index": len(points)-1, "representative": i, "power": j,
                                   "sign": sign, "psi_equals_lambda": True})
    assert len(points) == len(set(points)) == 48
    write_json(out/"orbit-input.json", {"curve": C, "beta": beta, "lambda": lam,
                 "representatives": representatives, "points": points, "factors": factors,
                 "representative_index": rep_index, "supplied_scalar_labels": False,
                 "sampler_not_claimed_uniform_or_RFC9380": True})
    write_json(out/"map-checks.json", map_checks)
    records.append({"case_id": "orbit-and-actions", "status": "completed", "points": 48,
                    "representatives": 8, "point_action_checks": len(map_checks)})
    targets = [hashed_point(seed, f"ordinary-target-{i}", C, lift, draws) for i in range(8)]
    planted = add(add(representatives[0], representatives[1]), representatives[2])
    if planted is None:
        raise ValueError("Prespecified positive target became identity; retain, do not choose another")
    table, pairs = pair_table(points, add)
    production = [collect(Q, points, table, add, neg) for Q in targets]
    zero = collect(None, points, table, add, neg)
    positive = collect(planted, points, table, add, neg)
    requested = targets+[None, planted]
    oracle, states, oracle_digest = complete_oracle(points, requested, jpoint, jadd, normalize)
    assert states == comb(len(points)+2, 3)
    for i, Q in enumerate(targets):
        assert production[i] == oracle[Q]
        write_json(out/f"ordinary-target-{i}.json", {"case_id": f"ordinary-target-{i}", "target": Q,
                   "constructed": False, "matches": production[i], "oracle_matches": oracle[Q],
                   "baseline_same_signed_point_set": True, "pair_table_entries": pairs,
                   "canonical_multisets_checked_by_baseline": states})
        records.append({"case_id": f"ordinary-target-{i}", "status": "completed", "relations": len(production[i])})
    assert zero == oracle[None] and positive == oracle[planted]
    assert (0, 6, 12) in positive
    write_json(out/"positive-target.json", {"target": planted, "constructed": True,
                 "known_summands": [0, 6, 12], "matches": positive, "oracle_matches": oracle[planted]})
    records.append({"case_id": "positive-target", "status": "completed", "constructed": True,
                    "relations": len(positive), "detector_found_known_relation": True})
    R = [coefficient_row(triple, 48) for triple in zero]
    RC = [compressed(row, rep_index, factors, r) for row in R]
    pure = [i for i, row in enumerate(RC) if not any(row)]
    retained = [row for row in RC if any(row)]
    constraints = []
    for j in range(48):
        representative_column = 6*rep_index[j]
        if j == representative_column:
            continue
        row = [0]*48
        row[j], row[representative_column] = 1, -factors[j] % r
        constraints.append(row)
    ranks = checked_ranks(R, RC, constraints, r)
    assert ranks["symmetry"] == 40
    assert rank_mod(retained, 8, r) == ranks["compressed"]
    write_json(out/"zero-target.json", {"triples": zero, "oracle_matches": oracle[None],
                 "full_rows_sparse": [sparse(row) for row in R],
                 "compressed_rows_sparse": [sparse(row) for row in RC],
                 "pure_symmetry_row_indices_removed": pure, "quotient_ranks": ranks,
                 "independent_quotient_rows": len(retained),
                 "symmetry_rows_sparse": [sparse(row) for row in constraints]})
    records.append({"case_id": "zero-target", "status": "completed", "relations": len(zero),
                    "pure_symmetry_rows": len(pure), "quotient_rank": ranks["compressed"]})
    # A nonidentity point cannot be admitted as a homogeneous relation.
    forged = [1]+[0]*7
    assert representatives[0] is not None
    assert rank_mod(RC+[forged], 8, r) == ranks["compressed"]+1
    wrong_beta_point = (2*G[0] % p, G[1])
    assert (wrong_beta_point[1]**2-wrong_beta_point[0]**3-7) % p != 0
    other_lambda = (-1-lam) % r
    assert mul(other_lambda, G) != psi(G) and jmul(other_lambda, G) != psi(G)
    write_json(out/"negative-controls.json", {"wrong_beta_2_off_curve": True,
                 "conjugate_lambda_branch_rejected": True, "nonidentity_false_relation_rejected": True,
                 "false_row_would_increase_quotient_rank": True})
    records.append({"case_id": "negative-controls", "status": "completed", "rejected": 3})
    history = historical_control(C, neg, add, mul)
    write_json(out/"historical-constructed-control.json", history)
    records.append({"case_id": "historical-control", "status": "completed", "constructed": True,
                    "rows": history["rows"], "ranks": history["ranks"]})
    write_json(out/"fixture-draws.json", draws)
    write_json(out/"oracle-completeness.json", {"method": "independent Jacobian arithmetic, all i<=j<=k",
                 "signed_points": len(points), "canonical_multisets": states,
                 "enumeration_sha256": oracle_digest, "pair_table_entries": pairs,
                 "query_count": 10, "all_outputs_match": True,
                 "no_statistical_yield_or_timing_claim": True})
    return {"curve": C, "ordinary_queries": 8, "ordinary_relations": sum(map(len, production)),
            "zero_relations": len(zero), "pure_symmetry_rows": len(pure), "quotient_rank": ranks["compressed"],
            "positive_relations": len(positive), "positive_detected": True,
            "oracle_multisets": states, "pair_table_entries": pairs,
            "checker_ordinary_relations": sum(len(oracle[Q]) for Q in targets),
            "checker_zero_relations": len(oracle[None]),
            "checker_quotient_rank": independent_rank(RC, 8, r),
            "scope": "complete fixed signed-base/domain observations; no natural-yield law or ECDLP advantage"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--protocol", type=Path, default=HERE/"protocol.json")
    parser.add_argument("--release", type=Path, default=HERE/"phase-b-release.json")
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Optimization disables certificate assertions; run without -O")
    if args.seed != 2026102608:
        raise SystemExit("Frozen F8 seed is 2026102608; an amendment must precede affected data")
    if not args.protocol.is_file() or json.loads(args.protocol.read_text())["freeze"]["status"] != "frozen":
        raise SystemExit("No frozen protocol; Phase A does not authorize data collection")
    protocol = json.loads(args.protocol.read_text())
    if sha(canonical({key: value for key, value in protocol.items() if key != "freeze"})) != protocol["freeze"]["protocol_sha256"]:
        raise SystemExit("Frozen protocol contents changed; a prospective amendment is required")
    sys.path.insert(0, str(HERE.parents[1]/"runtime"))
    from checkpoint_gate import require_gate
    gate = require_gate(REPO, args.release, protocol, TASK)
    source, host = observed_source(), host_record()
    args.out.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = resource.getrusage(resource.RUSAGE_SELF)
    records, counters, result = [], {}, {}
    status, reason = "succeeded", None
    def expired(signum, frame):
        raise Watchdog("112-second infrastructure watchdog; uncompleted cases stay unknown")
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(112)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
        result = panel(args.seed, args.out, records, counters)
    except Watchdog as error:
        status, reason = "timeout", str(error)
    except Exception as error:
        status, reason = "failed", f"{type(error).__name__}: {error}"
        (args.out/"failure.txt").write_text(traceback.format_exc())
    finally:
        signal.alarm(0)
    after = resource.getrusage(resource.RUSAGE_SELF)
    finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
    planned = ["orbit-and-actions"]+[f"ordinary-target-{i}" for i in range(8)]
    planned += ["positive-target", "zero-target", "negative-controls", "historical-control"]
    done = {row["case_id"] for row in records}
    receipt = {"task": TASK, "track": "F8", "status": status, "reason": reason, "seed": args.seed,
               "source": source, "host": host, "checkpoint_gate": gate,
               "started_at": started, "finished_at": finished, "result": result, "counters": counters,
               "planned_internal_cases": len(planned), "completed_internal_cases": len(records),
               "uncompleted_case_ids": [case for case in planned if case not in done],
               "rusage": {"user_seconds": after.ru_utime-before.ru_utime, "sys_seconds": after.ru_stime-before.ru_stime,
                          "max_rss_bytes": after.ru_maxrss*1024, "wall_valid": False},
               "protocol_path": str(args.protocol.resolve()), "protocol_sha256": protocol["freeze"]["protocol_sha256"]}
    write_json(args.out/"case-index.json", records)
    write_json(args.out/"execution.json", receipt)
    row = {"run_id": "F8/"+args.out.name, "arm": "producer", "instance_id": "0", "seed": args.seed,
           "replicate": 0, "warmup": False, "status": status,
           "verification": "verified" if status == "succeeded" else "error", "completed_cases": len(records),
           "ordinary_relations": result.get("ordinary_relations"), "zero_relations": result.get("zero_relations"),
           "pure_symmetry_rows": result.get("pure_symmetry_rows"), "quotient_rank": result.get("quotient_rank"),
           "positive_detected": int(result["positive_detected"]) if "positive_detected" in result else None,
           "oracle_multisets": result.get("oracle_multisets"),
           "mismatches": 0 if status == "succeeded" else None,
           "native_counters": {key: value for key, value in counters.items() if key.startswith("affine_")},
           "tier": "L0"}
    checker = {**row, "arm": "checker", "ordinary_relations": result.get("checker_ordinary_relations"),
               "zero_relations": result.get("checker_zero_relations"),
               "quotient_rank": result.get("checker_quotient_rank"),
               "native_counters": {key: value for key, value in counters.items() if key.startswith("jacobian_")}}
    row["run_id"] += "/producer"
    checker["run_id"] += "/checker"
    with (args.out/"rows.jsonl").open("xb") as stream:
        for item in (row, checker):
            stream.write(canonical(item)+b"\n")
    print(json.dumps({"status": status, "completed_internal_cases": len(records), "reason": reason}))
    return 0 if status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
