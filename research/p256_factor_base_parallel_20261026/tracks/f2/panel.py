"""Frozen F2 panel body. Imported only after root release and real S3 gate."""
import gzip
import hashlib
from itertools import islice
import json
from math import isqrt
from pathlib import Path

from arithmetic import (P, B, R, G, add, mul, neg, on_curve, point_from_seed,
                        root_with_witness, rhs, map_x_chain, map_point_chain,
                        raw_membership, signed_base, pair_table, solve_three,
                        classify_solutions)
import independent as oracle
from failclosed import SENTINEL, guarded_call

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OLD = REPO / "research/p256_factor_base_parallel_20261025/tracks/f2"
FIXED_SEED = 2026102602
CHUNK = 256


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(obj, handle, separators=(",", ":"), sort_keys=True)
        handle.write("\n")
    if path.stat().st_size > 65536:
        raise RuntimeError("record exceeds in-Git data policy: "+str(path))


def require(condition, message, state):
    state["checks"] = state.get("checks", 0)+1
    if not condition:
        raise AssertionError(message)


def input_json(relative):
    return json.loads((OLD / relative).read_text())


def target_order_certificate(state):
    from flint import fmpz
    require(bool(fmpz(P).is_prime()), "P-256 field primality", state)
    require(bool(fmpz(R).is_prime()), "P-256 subgroup primality", state)
    require(on_curve(G) and oracle.on_curve(G), "standard generator curve equation", state)
    require(mul(R, G, counts=state["counts"]) is None, "affine [r]G=O", state)
    require(oracle.scalar(R, G, counts=state["oracle_counts"])[2] == 0,
            "independent Jacobian [r]G=O", state)
    radius = isqrt(4*P)
    lower, upper = P+1-radius, P+1+radius
    first_multiple, last_multiple = (lower+R-1)//R, upper//R
    require(first_multiple == last_multiple == 1, "unique order multiple in Hasse interval", state)
    require((4*(-3)**3+27*B*B) % P != 0, "target nonsingular", state)
    return {
        "p": P, "r": R, "generator": list(G), "p_prime": True, "r_prime": True,
        "primality_method": "FLINT fmpz.is_prime rigorous backend; no portable proof object",
        "generator_nonzero": True, "rG_affine": None, "rG_jacobian_is_infinity": True,
        "hasse_interval": [lower, upper], "multiple_indices": [first_multiple, last_multiple],
        "certified_total_order": R, "cofactor": 1,
        "lift_subgroup_method": "independent curve equation plus certified #E(Fp)=r",
        "individual_lift_r_multiplications": 0,
    }


def write_chunk(out, index, rows):
    relative = f"full-fibre/rows-{index:05d}.json.gz"
    path = out/relative
    path.parent.mkdir(exist_ok=True)
    raw = (json.dumps(rows, separators=(",", ":"), sort_keys=True)+"\n").encode()
    packed = gzip.compress(raw, mtime=0)
    if len(packed) > 65536:
        raise RuntimeError("fibre chunk exceeds the fixed file envelope")
    with path.open("xb") as handle:
        handle.write(packed)
    return relative


def read_full_rows(out, chunks):
    for relative in chunks:
        yield from json.loads(gzip.decompress((out/relative).read_bytes()))


def full_fibre(out, compact, edges, state):
    counts = state["counts"]
    offset = tuple(compact["generic_offset"])
    kernel = tuple(compact["kernel_generator"])
    endpoint = tuple(compact["generic_endpoint"])
    size = compact["degree"]
    require(size == 65536 and len(edges) == 16, "frozen full fibre degree", state)
    require(on_curve(offset, 1, 0) and on_curve(kernel, 1, 0), "auxiliary input equations", state)
    require(mul(size, kernel, 1, counts) is None and mul(size//2, kernel, 1, counts) is not None,
            "affine exact full-fibre kernel order", state)
    require(map_point_chain(offset, edges, counts) == endpoint, "offset maps to frozen endpoint", state)
    require(map_point_chain(kernel, edges, counts) is None, "kernel maps to infinity", state)
    require(endpoint[1] != 0, "endpoint not two-torsion", state)
    unique, chunks, rows = set(), [], []
    state["pending_full_fibre_rows"] = rows
    point = offset
    accepted = rejected = 0
    state["full_fibre_chunks"] = chunks
    for index in range(size):
        require(point is not None and on_curve(point, 1, 0), "coset point equation", state)
        x, aux_y = point
        require(x not in unique, "full-fibre x values distinct", state)
        unique.add(x)
        y, witness = root_with_witness(rhs(x), counts)
        if y is None:
            require(witness*witness % P == -rhs(x) % P and rhs(x) != 0,
                    "exact nonlift witness", state)
            target = None
            rejected += 1
        else:
            target = (x, y)
            require(y != 0 and on_curve(target) and oracle.on_curve(target),
                    "target lift and independent curve equation", state)
            accepted += 1
        rows.append({"index": index, "x": x, "auxiliary_point": [x, aux_y],
                     "target_point": None if target is None else list(target),
                     "sqrt_witness": witness})
        counts["classified_x"] = counts.get("classified_x", 0)+1
        state["full_fibre_partial"] = {"rows": index+1, "accepted": accepted, "rejected": rejected}
        if len(rows) == CHUNK:
            chunks.append(write_chunk(out, index+1-CHUNK, rows))
            rows = []
            state["pending_full_fibre_rows"] = rows
        point = add(point, kernel, 1, counts)
    if rows:
        chunks.append(write_chunk(out, size-len(rows), rows))
        state["pending_full_fibre_rows"] = []
    require(point == offset and len(unique) == size, "full coset closed and complete", state)
    replay = oracle.replay_coset(read_full_rows(out, chunks), compact, state["oracle_counts"])
    require(replay["accepted"] == accepted and replay["rejected"] == rejected,
            "independent full lift classification agrees", state)
    result = {"degree": size, "rows": size, "accepted": accepted, "rejected": rejected,
              "signed_target_points": 2*accepted, "distinct_x": len(unique), "complete": True,
              "chunks": chunks, "replay": replay,
              "domain_proof": "exact cyclic coset, non-two-torsion image, degree upper bound",
              "per_point_chain_evaluation": False, "individual_lift_r_multiplications": 0}
    dump(out/"full-fibre-summary.json", result)
    return result


def matched_case(family, raw_size, expected_m, edges, state):
    base = f"receipts/validation-001/cases/{family}-M{raw_size}"
    summary = input_json(base+"/summary.json")
    rows = []
    for relative in summary["certificate_chunks"]:
        rows.extend(input_json("receipts/validation-001/"+relative))
    require(summary["matched_accepted_M"] == expected_m, "frozen matched size", state)
    require(len(rows) == raw_size == len({row["x"] for row in rows}),
            "fixed input domain cardinality", state)
    for row in rows:
        require(raw_membership(row["x"], family, summary["metadata"], edges, state["counts"]),
                "raw coordinate belongs to declared membership predicate", state)
        if row["target_point"] is not None:
            value = tuple(row["target_point"])
            require(value[0] == row["x"] and on_curve(value) and oracle.on_curve(value),
                    "retained target point curve equations", state)
    accepted = sorted((row for row in rows if row["target_point"] is not None),
                      key=lambda row: row["x"])
    canonical = [tuple(row["target_point"]) for row in accepted[:expected_m]]
    require(len(canonical) == expected_m, "matched prefix complete", state)
    points = signed_base(canonical)
    for point in points:
        require(oracle.on_curve(point), "signed base checked independently", state)
    return summary, canonical, points


def expect_refusal(name, function, state, owner="producer"):
    try:
        function()
    except (ValueError, RuntimeError, AssertionError) as exception:
        state["controls"].append({"name": name, "owner": owner, "rejected": True,
                                  "exception": type(exception).__name__, "detail": str(exception)})
        state["controls_passed"] += 1
        return
    raise AssertionError("negative control accepted: "+name)


def run_panel(out, seed, state):
    if seed != FIXED_SEED:
        raise ValueError("seed differs from the frozen F2 card")
    state.update(checks=0, counts={}, oracle_counts={}, controls=[], controls_passed=0,
                 queries=[], completed_queries=0)
    group_order = target_order_certificate(state)
    dump(out/"target-order-certificate.json", group_order)
    chain = input_json("receipts/validation-001/chain.json")
    compact = input_json("receipts/validation-001/compact-full-chain.json")
    edges = chain["edges"]
    full = full_fibre(out, compact, edges, state)
    # Removing the first real row exercises the actual recurrence/index guard
    # immediately; the producer's sealed data is never mutated.
    expect_refusal("omitted-first-fibre-point",
                   lambda: oracle.replay_coset(islice(read_full_rows(out, full["chunks"]), 1, None),
                                               compact, state["oracle_counts"]), state, owner="oracle")
    ordinary, rejected_draws = [], []
    for index in range(2):
        point, rejects = point_from_seed(f"F2-pass2:{seed}:unplanted:{index}", state["counts"])
        ordinary.append(point)
        rejected_draws.append({"label": f"unplanted-{index}", "rejected_draws": rejects})
    require(ordinary[0] != ordinary[1], "ordinary targets distinct", state)
    dump(out/"ordinary-targets.json", {
        "seed": seed, "points": [list(point) for point in ordinary],
        "sampling_rule": "SHA256(label:counter) mod p; first nonzero rational lift; fixed labels",
        "scalar_witnesses_used": False, "draws": rejected_draws,
        "scope": "two deterministic unplanted targets, no uniform-target yield estimate"})
    for raw_size, matched_m in ((64, 26), (256, 121)):
        for family in ("elliptic_generic", "elliptic_kernel", "Dickson_generic"):
            summary, canonical, points = matched_case(family, raw_size, matched_m, edges, state)
            base_path = f"bases/{family}-M{matched_m}.json"
            dump(out/base_path, {"family": family, "raw_size": raw_size, "matched_M": matched_m,
                                 "canonical_points": [list(point) for point in canonical],
                                 "signed_points": [list(point) for point in points],
                                 "matching": "sorted accepted x prefix, first-pass frozen rule"})
            table = pair_table(points, state["counts"])
            positive = add(add(canonical[0], canonical[1], counts=state["counts"]),
                           canonical[2], counts=state["counts"])
            require(positive is not None, "constructed positive target is nonzero", state)
            targets = [
                ("unplanted-0", "unplanted", ordinary[0]),
                ("unplanted-1", "unplanted", ordinary[1]),
                ("constructed-positive", "constructed-positive", positive),
                ("constructed-cancellation", "constructed-cancellation", canonical[0]),
            ]
            for label, kind, target in targets:
                answers = solve_three(target, points, table, state["counts"])
                case_name = f"{family}-M{matched_m}-{label}"
                dump(out/f"queries/{case_name}-producer.json",
                     {"case": case_name, "target": list(target), "kind": kind, "base": base_path,
                      "solutions": [list(triple) for triple in answers], "producer_complete": True})
                other = oracle.solve_three(target, points, state["oracle_counts"])
                require(answers == other, "complete independent signed solution sets agree", state)
                for triple in answers:
                    require(oracle.verify_solution(target, points, triple, state["oracle_counts"]),
                            "independent point-sum certificate", state)
                if kind == "constructed-positive":
                    require((0, 2, 4) in answers, "planted distinct-coordinate triple recovered", state)
                if kind == "constructed-cancellation":
                    require(any(points[i] == neg(points[j]) for triple in answers
                                for i in triple for j in triple if i != j),
                            "cancellation relation recovered", state)
                query = {
                    "case": case_name, "family": family,
                    "raw_size": raw_size, "matched_M": matched_m, "kind": kind,
                    "target": list(target), "base": base_path,
                    "solutions": [list(triple) for triple in answers],
                    "oracle_solutions": [list(triple) for triple in other],
                    "oracle_solution_count": len(other),
                    "counts": classify_solutions(answers, points),
                    "complete": True, "includes_repetitions": True,
                    "source_summary": f"cases/{family}-M{raw_size}/summary.json",
                    "oracle_method": "separate Jacobian pair/complement traversal",
                }
                dump(out/f"queries/{query['case']}.json", query)
                state["queries"].append({k: query[k] for k in
                                          ("case", "family", "matched_M", "kind", "counts")})
                state["queries"][-1]["oracle_solution_count"] = len(other)
                state["completed_queries"] += 1
            bad = (ordinary[0][0], (ordinary[0][1]+1) % P)
            while on_curve(bad):
                bad = bad[0], (bad[1]+1) % P
            expect_refusal(f"corrupt-target-y-{family}-M{matched_m}",
                           lambda: solve_three(bad, points, table, state["counts"]), state)
            expect_refusal(f"oracle-corrupt-target-y-{family}-M{matched_m}",
                           lambda: oracle.solve_three(bad, points, state["oracle_counts"]),
                           state, owner="oracle")
            if family == "elliptic_generic":
                pole = edges[0]["r"]
                value, pole_edge = map_x_chain(pole, edges[:summary["metadata"]["chain_length"]],
                                               state["counts"])
                require(value is None and pole_edge == 0, "explicit finite-fibre pole", state)
                require(not raw_membership(pole, family, summary["metadata"], edges, state["counts"]),
                        "pole rejected from finite generic fibre before prefix selection", state)
                state["controls"].append({"name": f"finite-fibre-pole-M{matched_m}", "owner": "producer",
                                          "x": pole, "pole_edge": pole_edge, "rejected": True,
                                          "note": "kernel-domain infinity membership is a distinct predicate"})
                state["controls_passed"] += 1
    expect_refusal("unexpected-exception-completion-guard",
                   lambda: guarded_call(lambda: (_ for _ in ()).throw(
                       RuntimeError("intentional producer exception"))), state)
    expect_refusal("missing-sentinel-completion-guard", lambda: guarded_call(lambda: {}), state)
    require(state["completed_queries"] == 24, "all frozen domain queries retained", state)
    dump(out/"controls.json", state["controls"])
    return {
        "schema": "p256-pass2-f2-panel/v1", "task": "TASK-20261026-e8fd72",
        "seed": seed, "status": "completed", "completion_sentinel": SENTINEL,
        "full_fibre": {k: v for k, v in full.items() if k != "chunks"},
        "queries": state["queries"], "checks": state["checks"],
        "controls_passed": state["controls_passed"], "native_counters": state["counts"],
        "oracle_native_counters": state["oracle_counts"],
        "subgroup_basis": "target-order-certificate.json, #E(Fp)=r and h=1; no individual [r] per lift",
        "unmeasured": ["implicit large-base solving", "natural useful-relation yield",
                       "full ECDLP cost", "rank/target attachment", "comparative performance"],
        "source_novelty_claim": False, "scientific_transition": False,
        "independent_implementation": True, "independent_session_review": False,
    }
