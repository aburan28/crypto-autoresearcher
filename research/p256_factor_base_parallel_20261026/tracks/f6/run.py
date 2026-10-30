#!/usr/bin/env python3
"""Frozen F6 total-degree/ordinary-target panel. Import and --help take no data."""
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
TASK = "TASK-20261026-2746d0"


class Watchdog(Exception):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, obj):
    data = json.dumps(obj, indent=2, allow_nan=False).encode() + b"\n"
    if len(data) > 60000:
        raise ValueError("Retain large arrays in explicit shards: " + str(path))
    with path.open("xb") as stream:
        stream.write(data)


def write_rows(path, rows):
    with path.open("xb") as stream:
        for row in rows:
            stream.write(canonical(row) + b"\n")


def shard_rows(directory, stem, rows):
    parts, batch, size = [], [], 0
    for row in rows:
        amount = len(canonical(row)) + 3
        if batch and size + amount > 45000:
            name = f"{stem}-{len(parts)+1:02d}.json"
            write_json(directory / name, batch)
            parts.append(name)
            batch, size = [], 0
        batch.append(row)
        size += amount
    if batch:
        name = f"{stem}-{len(parts)+1:02d}.json"
        write_json(directory / name, batch)
        parts.append(name)
    return parts


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def observed_source():
    rel = str(Path(__file__).resolve().relative_to(REPO))
    return {
        "head": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "instrument_commit": git("log", "-1", "--format=%H", "--", rel),
        "instrument_path": rel,
        "instrument_source_sha256": sha(Path(__file__).read_bytes()),
        "binary_path": str(Path(sys.executable).resolve()),
        "binary_sha256": sha(Path(sys.executable).resolve().read_bytes()),
        "analysis_sha256": sha((HERE / "analysis.py").read_bytes()),
    }


def host_record():
    model = next((line.partition(":")[2].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                  if line.startswith("model name")), None)
    return {"cpu_model": model, "logical_cpus": os.cpu_count(), "kernel": platform.release(),
            "python": platform.python_version(), "host": platform.node(),
            "threads": 1, "isolation": {"tier": "L0", "blockers": ["shared managed host; no timing claim"]}}


def parameters():
    return {"name": "P-256", "p": 2**256-2**224+2**192+2**96-1, "a": -3,
            "b": int("5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b", 16),
            "r": int("ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551", 16), "h": 1,
            "authority": "SEC 2 v2.0 section 2.4.2; published order/primality inherited"}


def curve_functions(C, counters):
    p, a, b = C["p"], C["a"], C["b"]
    def neg(P):
        return None if P is None else (P[0], -P[1] % p)
    def add(P, Q):
        counters["affine_add_calls"] = counters.get("affine_add_calls", 0) + 1
        if P is None:
            return Q
        if Q is None:
            return P
        x, y = P
        u, v = Q
        if x == u:
            if (y+v) % p == 0:
                return None
            slope = (3*x*x+a)*pow(2*y, -1, p) % p
        else:
            slope = (v-y)*pow((u-x) % p, -1, p) % p
        counters["affine_inversions"] = counters.get("affine_inversions", 0) + 1
        w = (slope*slope-x-u) % p
        return w, (slope*(x-w)-y) % p
    def lift(x):
        value = (x*x*x+a*x+b) % p
        y = pow(value, (p+1)//4, p)
        return (x % p, min(y, p-y)) if y*y % p == value else None
    return neg, add, lift


def hashed_point(seed, label, C, lift, draws):
    for attempt in range(4096):
        message = f"p256-factor-pass2/F6/{seed}/{label}/{attempt}".encode()
        x = int.from_bytes(hashlib.sha256(message).digest(), "big") % C["p"]
        P = lift(x)
        draws.append({"label": label, "attempt": attempt, "x": x, "accepted": P is not None})
        if P is not None:
            return P
    raise RuntimeError("Fixed 4096-attempt fixture construction limit reached")


def f3_expr(S, x, y, target_x, C):
    a, b = C["a"], C["b"]
    return (x-y)**2*target_x**2 - 2*((x+y)*(x*y+a)+2*b)*target_x + (x*y-a)**2 - 4*b*(x+y)


def centered_lift(S, expression, variables, p):
    poly = S.Poly(S.expand(expression), *variables, domain=S.ZZ)
    terms = {}
    for exponent, coefficient in poly.terms():
        value = int(coefficient) % p
        if value > p//2:
            value -= p
        if value:
            terms[exponent] = value
    return terms


def multiply_terms(left, right):
    out = {}
    for a, u in left.items():
        for b, v in right.items():
            exponent = (a[0]+b[0], a[1]+b[1])
            out[exponent] = out.get(exponent, 0) + u*v
    return {e: c for e, c in out.items() if c}


def term_expression(S, terms, x, y):
    return sum(c*x**e[0]*y**e[1] for e, c in terms.items())


def staircase(S, terms, p, m, offset, B, x, y):
    """Two independent coefficient constructions, then a triangular rank proof."""
    from math import comb
    D = 4*m+offset
    monomials = sorted(((i, j) for i in range(D+1) for j in range(D+1-i)), key=lambda a: (sum(a), a))
    n = len(monomials)
    assert n == comb(D+2, 2)
    powers = [{(0, 0): 1}]
    for _ in range(m):
        powers.append(multiply_terms(powers[-1], terms))
    expression = term_expression(S, terms, x, y)
    # SymPy's polynomial powers are distinct from the sparse convolution above.
    independent_powers = [S.Poly(expression**k, x, y, domain=S.ZZ) for k in range(m+1)]
    index = {a: i for i, a in enumerate(monomials)}
    matrix, pivots, row_hashes = [], [], []
    for row_index, alpha in enumerate(monomials):
        k = min(m, alpha[0]//2, alpha[1]//2)
        shift = (alpha[0]-2*k, alpha[1]-2*k)
        coefficients = {(e[0]+shift[0], e[1]+shift[1]): c*p**(m-k) for e, c in powers[k].items()}
        independently = S.Poly(p**(m-k)*x**shift[0]*y**shift[1]*independent_powers[k].as_expr(), x, y)
        assert coefficients == {e: int(c) for e, c in independently.terms()}
        row = [0]*n
        for exponent, coefficient in coefficients.items():
            assert exponent in index
            assert index[exponent] <= row_index
            row[index[exponent]] = coefficient*B**sum(exponent)
        expected_pivot = p**(m-k)*B**sum(alpha)
        assert row[row_index] == expected_pivot != 0
        matrix.append(row)
        pivots.append(expected_pivot)
        row_hashes.append(sha(canonical(row)))
    K = sum(comb(D-4*k+2, 2) for k in range(1, m+1))
    weight = 2*comb(D+2, 3)
    det = p**(m*n-K)*B**weight
    product = 1
    for pivot in pivots:
        product *= pivot
    assert product == det
    assert sum(sum(alpha) for alpha in monomials) == weight
    # Cauchy--Schwarz and the delta=3/4 first-vector LLL bound, raised to 4n.
    lhs = n**(2*n) * 2**(n*(n-1)) * B**(4*weight)
    rhs = p**(4*K)
    record = {"m": m, "offset": offset, "D": D, "B": B, "rank": n, "dimension": n,
              "K": K, "determinant": {"p_exponent": m*n-K, "B_exponent": weight},
              "determinant_sha256_hex_bigendian": sha(det.to_bytes((det.bit_length()+7)//8, "big")),
              "triangularity_and_independent_coefficients_checked": True,
              "row_sha256": row_hashes,
              "sufficient_first_vector_inequality": {"holds": lhs < rhs, "strict": True,
                  "lhs_bit_length": lhs.bit_length(), "rhs_bit_length": rhs.bit_length(),
                  "formula": "n^(2n)*2^(n(n-1))*B^(4w)<p^(4K)"},
              "extraction_not_implied_by_bound": True}
    return matrix, monomials, record, det


def enumerate_box(C, c1, c2, B, target, neg, add, lift):
    p = C["p"]
    f = lambda X, Y: ((X-Y)**2*target[0]**2 - 2*((X+Y)*(X*Y+C["a"])+2*C["b"])*target[0]
                       +(X*Y-C["a"])**2-4*C["b"]*(X+Y)) % p
    candidates, rational = [], []
    for u, v in itertools.product(range(B+1), repeat=2):
        X, Y = (c1+u) % p, (c2+v) % p
        P, R = lift(X), lift(Y)
        zero = f(X, Y) == 0
        signs = []
        if P is not None and R is not None:
            for a, b in itertools.product((1, -1), repeat=2):
                if add(P if a == 1 else neg(P), R if b == 1 else neg(R)) == target:
                    signs.append([a, b])
        if signs:
            assert zero
            rational.append({"u": u, "v": v, "signs": signs})
        candidates.append({"u": u, "v": v, "modular_zero": zero, "first_lifts": P is not None,
                           "second_lifts": R is not None, "signed_matches": signs})
    return {"B": B, "target": target, "offsets": [c1, c2], "cells": len(candidates),
            "modular_zeros": [r for r in candidates if r["modular_zero"]],
            "rational_relations": rational, "all_cells": candidates}


def extract_integer_pairs(S, polys, x, y, B):
    if not polys:
        return {"state": "no_certified_integer_zero_polynomials", "basis": [], "roots": []}
    basis = S.groebner(polys, x, y, order="lex", domain=S.QQ)
    expressions = [p.as_expr() for p in basis.polys]
    if expressions == [S.Integer(1)]:
        return {"state": "unit_ideal_empty", "basis": ["1"], "roots": []}
    if not basis.is_zero_dimensional:
        return {"state": "positive_dimensional_open", "basis": list(map(str, expressions)), "roots": []}
    univariate = next((p for p in expressions if p.free_symbols <= {y} and S.Poly(p, y).degree() > 0), None)
    if univariate is None:
        return {"state": "eliminant_missing_open", "basis": list(map(str, expressions)), "roots": []}
    roots = []
    for v in S.Poly(univariate, y, domain=S.QQ).ground_roots():
        if not v.is_Integer or not 0 <= int(v) <= B:
            continue
        substitutions = [S.Poly(p.subs(y, v), x, domain=S.QQ) for p in expressions if p.subs(y, v) != 0]
        if not substitutions:
            return {"state": "specialization_component_open", "basis": list(map(str, expressions)), "roots": roots}
        common = substitutions[0]
        for polynomial in substitutions[1:]:
            common = S.gcd(common, polynomial)
        for u in common.ground_roots():
            if u.is_Integer and 0 <= int(u) <= B and all(p.subs({x: u, y: v}) == 0 for p in expressions):
                roots.append([int(u), int(v)])
    return {"state": "zero_dimensional_integer_extraction_complete", "basis": list(map(str, expressions)), "roots": sorted(roots)}


def lll_case(S, C, target, offsets, B, directory, label):
    p = C["p"]
    x, y = S.symbols("u v")
    terms = centered_lift(S, f3_expr(S, offsets[0]+x, offsets[1]+y, target[0], C), (x, y), p)
    matrix, monomials, screen, determinant = staircase(S, terms, p, 1, 0, B, x, y)
    A = S.Matrix(matrix)
    assert abs(int(A.det(method="domain-ge"))) == determinant
    reduced, transform = A.lll_transform(delta=S.Rational(3, 4))
    assert transform*A == reduced
    assert abs(int(transform.det())) == 1
    assert abs(int(reduced.det(method="domain-ge"))) == determinant
    qualified, vector_certificates = [], []
    for i in range(reduced.rows):
        row = list(map(int, reduced.row(i)))
        coefficients = []
        for value, exponent in zip(row, monomials):
            scale = B**sum(exponent)
            assert value % scale == 0
            coefficients.append(value//scale)
        polynomial = sum(c*x**a[0]*y**a[1] for c, a in zip(coefficients, monomials))
        norm_squared = sum(value*value for value in row)
        valid = len(monomials)*norm_squared < p*p
        if valid:
            qualified.append(polynomial)
        vector_certificates.append({"index": i, "norm_squared": norm_squared,
                                    "integer_zero_norm_qualified": valid,
                                    "polynomial_terms": [[*a, c] for a, c in zip(monomials, coefficients) if c]})
    extraction = extract_integer_pairs(S, qualified, x, y, B)
    input_parts = shard_rows(directory, label+"-input", matrix)
    reduced_parts = shard_rows(directory, label+"-reduced", [list(map(int, reduced.row(i))) for i in range(reduced.rows)])
    transform_parts = shard_rows(directory, label+"-transform", [list(map(int, transform.row(i))) for i in range(transform.rows)])
    vector_parts = shard_rows(directory, label+"-vectors", vector_certificates)
    record = {"label": label, "target": target, "offsets": list(offsets), "B": B,
              "screen": screen, "monomials": monomials,
              "input_parts": input_parts, "reduced_parts": reduced_parts,
              "transform_parts": transform_parts, "vector_parts": vector_parts,
              "unimodular_transform_checked": True, "determinant_checked_directly": True,
              "qualified_count": len(qualified), "extraction": extraction,
              "scaling_corruption_rejected": matrix[0][0]+1 != matrix[0][0],
              "wrong_determinant_rejected": determinant+1 != abs(int(A.det(method="domain-ge"))),
              "nonzero_constant_p_rejected_by_norm": not (len(monomials)*p*p < p*p)}
    # Check a concrete incorrectly scaled matrix against reconstruction.
    corrupt = [row[:] for row in matrix]
    corrupt[0][0] += 1
    assert corrupt != matrix and abs(int(S.Matrix(corrupt).det(method="domain-ge"))) != determinant
    write_json(directory / (label+".json"), record)
    return record


def panel(seed, out, records, counters):
    import sympy as S
    C = parameters()
    p = C["p"]
    neg, add, lift = curve_functions(C, counters)
    draws = []
    Q = hashed_point(seed, "ordinary-target", C, lift, draws)
    offsets = tuple(int.from_bytes(hashlib.sha256(f"F6-offset/{seed}/{i}".encode()).digest(), "big") % p for i in (0, 1))
    x, y = S.symbols("u v")
    terms = centered_lift(S, f3_expr(S, offsets[0]+x, offsets[1]+y, Q[0], C), (x, y), p)
    assert terms[(2, 2)] == 1
    write_json(out / "ordinary-input.json", {"curve": C, "target": Q, "offsets": offsets,
                  "offset_law": "SHA256 F6-offset/seed/index mod p, independent of a root",
                  "centered_polynomial_terms": [[*e, c] for e, c in sorted(terms.items())]})
    for m in (1, 2, 3):
        for offset in (0, 1, 2, 3):
            family = []
            for bits in (8, 16, 32, 64, 84):
                _, _, record, _ = staircase(S, terms, p, m, offset, 2**bits, x, y)
                record["case_id"] = f"m{m}-t{offset}-b{bits}"
                record["width_bits"] = bits
                family.append(record)
                records.append({"case_id": record["case_id"], "status": "completed",
                                "bound_holds": record["sufficient_first_vector_inequality"]["holds"],
                                "rank": record["rank"]})
            write_json(out / f"family-m{m}-t{offset}.json", family)
    ordinary_box = enumerate_box(C, *offsets, 7, Q, neg, add, lift)
    write_json(out / "ordinary-box.json", ordinary_box)
    records.append({"case_id": "ordinary-box", "status": "completed", "cells": ordinary_box["cells"],
                    "relations": len(ordinary_box["rational_relations"])})
    ordinary_lll = lll_case(S, C, Q, offsets, 7, out, "ordinary-lll")
    ordinary_roots = {tuple(r) for r in ordinary_lll["extraction"]["roots"]}
    modular_roots = {(r["u"], r["v"]) for r in ordinary_box["modular_zeros"]}
    assert modular_roots <= ordinary_roots or ordinary_lll["extraction"]["state"].endswith("open") or not ordinary_lll["qualified_count"]
    records.append({"case_id": "ordinary-lll", "status": "completed", "extraction": ordinary_lll["extraction"]["state"],
                    "qualified_count": ordinary_lll["qualified_count"], "finite_box_modular_roots_covered": modular_roots <= ordinary_roots})
    P = hashed_point(seed, "positive-P", C, lift, draws)
    R = hashed_point(seed, "positive-R", C, lift, draws)
    T = add(P, R)
    if T is None:
        raise ValueError("Fixed positive construction unexpectedly gives identity; retain and amend before replacement")
    positive_offsets = P[0]-1, R[0]-1
    positive_box = enumerate_box(C, *positive_offsets, 2, T, neg, add, lift)
    assert any(row["u"] == row["v"] == 1 for row in positive_box["rational_relations"])
    write_json(out / "known-root-box.json", {**positive_box, "constructed": True,
                    "offsets_derived_from_solution": True, "P": P, "R": R})
    records.append({"case_id": "positive-box", "status": "completed", "cells": positive_box["cells"],
                    "relations": len(positive_box["rational_relations"]), "constructed": True})
    positive_lll = lll_case(S, C, T, positive_offsets, 2, out, "positive-lll")
    detected = [1, 1] in positive_lll["extraction"]["roots"]
    records.append({"case_id": "positive-lll", "status": "completed", "constructed": True,
                    "detector_found_known_root": detected, "extraction": positive_lll["extraction"]["state"],
                    "qualified_count": positive_lll["qualified_count"]})
    for label in ("ordinary-lll", "positive-lll"):
        record = json.loads((out / (label+".json")).read_text())
        assert record["scaling_corruption_rejected"] and record["wrong_determinant_rejected"] and record["nonzero_constant_p_rejected_by_norm"]
    records.append({"case_id": "negative-controls", "status": "completed", "corruptions_rejected": 6})
    write_json(out / "fixture-draws.json", draws)
    return {"curve": C, "sympy": S.__version__, "screen_cases": 60,
            "ordinary_box_cells": ordinary_box["cells"], "ordinary_rational_relations": len(ordinary_box["rational_relations"]),
            "producer_ordinary_relations": sum((r["u"], r["v"]) in ordinary_roots for r in ordinary_box["rational_relations"]),
            "checker_positive_detected": any(row["u"] == row["v"] == 1 for row in positive_box["rational_relations"]),
            "positive_extraction_detected": detected, "positive_detector_valid": detected,
            "ordinary_extraction": ordinary_lll["extraction"]["state"],
            "scope": "exact stated staircase/window and finite-domain correctness; no general extraction or speed claim"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--protocol", type=Path, default=HERE / "protocol.json")
    parser.add_argument("--release", type=Path, default=HERE / "phase-b-release.json")
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Optimization disables certificate assertions; run without -O")
    if args.seed != 2026102606:
        raise SystemExit("The frozen panel seed is 2026102606; change needs a prospective amendment")
    if not args.protocol.is_file() or json.loads(args.protocol.read_text())["freeze"]["status"] != "frozen":
        raise SystemExit("No frozen protocol; Phase A preparation does not authorize data collection")
    protocol = json.loads(args.protocol.read_text())
    if sha(canonical({key: value for key, value in protocol.items() if key != "freeze"})) != protocol["freeze"]["protocol_sha256"]:
        raise SystemExit("Frozen protocol contents changed; a prospective amendment is required")
    sys.path.insert(0, str(HERE.parents[1] / "runtime"))
    from checkpoint_gate import require_gate
    gate = require_gate(REPO, args.release, protocol, TASK)
    source, host = observed_source(), host_record()
    args.out.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = resource.getrusage(resource.RUSAGE_SELF)
    records, counters, result = [], {}, {}
    status, reason = "succeeded", None
    def expired(signum, frame):
        raise Watchdog("112-second machine-protection watchdog; uncompleted cases remain unknown")
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(112)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
        result = panel(args.seed, args.out, records, counters)
    except Watchdog as error:
        status, reason = "timeout", str(error)
    except Exception as error:
        status, reason = "failed", f"{type(error).__name__}: {error}"
        (args.out / "failure.txt").write_text(traceback.format_exc())
    finally:
        signal.alarm(0)
    finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
    after = resource.getrusage(resource.RUSAGE_SELF)
    planned = [f"m{m}-t{t}-b{b}" for m in (1, 2, 3) for t in (0, 1, 2, 3) for b in (8, 16, 32, 64, 84)]
    planned += ["ordinary-box", "ordinary-lll", "positive-box", "positive-lll", "negative-controls"]
    complete = {r["case_id"] for r in records}
    receipt = {"task": TASK, "track": "F6", "status": status, "reason": reason,
               "seed": args.seed, "source": source, "host": host, "checkpoint_gate": gate,
               "started_at": started, "finished_at": finished,
               "result": result, "counters": counters, "planned_internal_cases": len(planned),
               "completed_internal_cases": len(records), "uncompleted_case_ids": [x for x in planned if x not in complete],
               "rusage": {"user_seconds": after.ru_utime-before.ru_utime, "sys_seconds": after.ru_stime-before.ru_stime,
                          "max_rss_bytes": after.ru_maxrss*1024, "wall_valid": False},
               "protocol_path": str(args.protocol.resolve()),
               "protocol_sha256": json.loads(args.protocol.read_text())["freeze"]["protocol_sha256"]}
    write_json(args.out / "case-index.json", records)
    write_json(args.out / "execution.json", receipt)
    row = {"run_id": "F6/"+args.out.name, "arm": "producer", "instance_id": "0", "seed": args.seed,
           "replicate": 0, "warmup": False, "status": status, "verification": "verified" if status == "succeeded" else "error",
           "completed_cases": len(records), "screen_cases": sum(x["case_id"].startswith("m") for x in records),
           "ordinary_relations": result.get("producer_ordinary_relations"),
           "positive_detected": int(bool(result["positive_extraction_detected"])) if "positive_extraction_detected" in result else None,
           "mismatches": 0 if status == "succeeded" else None,
           "tier": "L0"}
    # These are two real implementation stages of one shared panel, not two
    # timing trials: sparse polynomial production versus independent SymPy
    # coefficient reconstruction/direct determinant and transform checks.
    matrix_rows = sum(record.get("rank", 0) for record in records)
    row["native_counters"] = {"screen_staircase_rows_generated": matrix_rows}
    checker = {**row, "arm": "checker", "ordinary_relations": result.get("ordinary_rational_relations"),
               "positive_detected": int(result["checker_positive_detected"]) if "checker_positive_detected" in result else None,
               "native_counters": {"screen_staircase_rows_reconstructed": matrix_rows}}
    row["run_id"] += "/producer"
    checker["run_id"] += "/checker"
    write_rows(args.out / "rows.jsonl", [row, checker])
    print(json.dumps({"status": status, "completed_internal_cases": len(records), "reason": reason}))
    return 0 if status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
