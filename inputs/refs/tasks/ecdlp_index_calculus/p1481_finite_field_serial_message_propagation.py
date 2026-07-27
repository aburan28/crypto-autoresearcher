#!/usr/bin/env python3
"""Measure exact native-group messages for complete five-term membership."""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, is_prime


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1481_finite_field_serial_message_propagation.md"
OUT = STATE_DIR / "p1481_finite_field_serial_message_propagation.json"
NOTE = RESEARCH_DIR / "p1481_finite_field_serial_message_propagation.md"

SCHEMA = "ecdlp.p1481_finite_field_serial_message_propagation.v1"
EXPECTED = {
    CONTRACT: "9761a1834bac39b10948585514c30d948056ff00d2c0593fdfeb7dd5cecb8c23",
    STATE_DIR / "p1476_m_ary_sparse_deck_exponent_boundary.json":
        "c29426c61c687560b45e38cae1c50f18e89c2846a6d599c6f4583fc98ec70e5f",
    STATE_DIR / "p1476_m_ary_sparse_deck_exponent_boundary_audit.json":
        "752190e01263740ed8b0db73ae4fe3d092797ff1e1991a48438a8f66d2bcc138",
    STATE_DIR / "p1477_serial_s3_state_compression.json":
        "ca41939ef8f05d2579ac392d2651fc6bb3199f0e38b10b1d0e20a197caa51ae5",
    STATE_DIR / "p1477_serial_s3_state_compression_audit.json":
        "8b6eb71141b5a3deba12bd6969ddd0c10d9d6092c32e52e173d0145371f01245",
    STATE_DIR / "p1480_bitvector_serial_s3_membership.json":
        "d8107a1272a9ab0fd29c8243ea3527fadcc950d734c3b530d6a948c8a0cfd7e2",
    STATE_DIR / "p1480_bitvector_serial_s3_membership_audit.json":
        "cb84adfd3b88edcebe776b0ba1359649c6e486b569c1da96bc503455dc8efbf0",
}
FIXTURES = [
    {"L": 4, "p": 1033, "order": 1061, "a": 1, "b": 1},
    {"L": 8, "p": 32801, "order": 32479, "a": 1, "b": 5},
    {"L": 16, "p": 1048609, "order": 1047539, "a": 5, "b": 7},
    {"L": 32, "p": 33554593, "order": 33563891, "a": 3, "b": 9},
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_int(*parts: object) -> int:
    material = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


def point_key(point: Any) -> tuple[int, int] | tuple[str]:
    return ("O",) if point.is_zero() else (int(point[0]), int(point[1]))


def point_json(point: Any) -> dict[str, Any]:
    if point.is_zero():
        return {"infinity": True}
    return {"x": int(point[0]), "y": int(point[1])}


def build_context(fixture: dict[str, int]) -> dict[str, Any]:
    p, q, L = fixture["p"], fixture["order"], fixture["L"]
    if not is_prime(p) or not is_prime(q) or (p - 1) % L:
        raise RuntimeError("P1481 fixture arithmetic failure")
    field = GF(p)
    curve = EllipticCurve(field, [fixture["a"], fixture["b"]])
    if int(curve.cardinality()) != q or curve.is_supersingular():
        raise RuntimeError("P1481 curve validation failure")
    generator = None
    for x_integer in range(p):
        lifts = sorted(curve.lift_x(field(x_integer), all=True), key=lambda point: int(point[1]))
        if lifts:
            generator = lifts[0]
            break
    if generator is None or int(generator.order()) != q:
        raise RuntimeError("P1481 generator failure")
    h = field.multiplicative_generator() ** ((p - 1) // L)
    if int(h.multiplicative_order()) != L:
        raise RuntimeError("P1481 subgroup order failure")
    return {
        "fixture": fixture,
        "field": field,
        "curve": curve,
        "generator": generator,
        "identity": 0 * generator,
        "h": h,
    }


def subgroup_roots(context: dict[str, Any]) -> list[int]:
    roots = []
    value = context["field"].one()
    for _ in range(context["fixture"]["L"]):
        if context["curve"].lift_x(value, all=True):
            roots.append(int(value))
        value *= context["h"]
    return sorted(set(roots))


def random_x_roots(context: dict[str, Any], count: int) -> list[int]:
    fixture = context["fixture"]
    roots: set[int] = set()
    counter = 0
    while len(roots) < count:
        x_integer = digest_int("P1480", "random_x", fixture["L"], counter) % fixture["p"]
        counter += 1
        if x_integer not in roots and context["curve"].lift_x(context["field"](x_integer), all=True):
            roots.add(x_integer)
    return sorted(roots)


def deck_points(context: dict[str, Any], roots: list[int]) -> list[Any]:
    points = []
    for root in roots:
        lifts = sorted(
            context["curve"].lift_x(context["field"](root), all=True),
            key=lambda point: int(point[1]),
        )
        if len(lifts) != 2 or lifts[0] != -lifts[1]:
            raise RuntimeError("P1481 expected sign-complete roots")
        points.extend(lifts)
    return sorted(points, key=point_key)


def make_queries(
    context: dict[str, Any], deck_name: str, roots: list[int]
) -> list[dict[str, Any]]:
    lifts = [
        sorted(context["curve"].lift_x(context["field"](root), all=True), key=lambda point: int(point[1]))
        for root in roots
    ]
    fixture = context["fixture"]
    queries = []
    for index in range(8):
        if index < 4:
            nonce = 0
            while True:
                indices = [
                    digest_int("P1480", deck_name, fixture["L"], "planted-index", index, nonce, slot)
                    % len(roots)
                    for slot in range(5)
                ]
                signs = [
                    digest_int("P1480", deck_name, fixture["L"], "planted-sign", index, nonce, slot) & 1
                    for slot in range(5)
                ]
                endpoints = [lifts[root_index][sign] for root_index, sign in zip(indices, signs)]
                target = sum(endpoints, context["identity"])
                if not target.is_zero():
                    break
                nonce += 1
            queries.append({
                "query_index": index,
                "kind": "planted_positive",
                "target": target,
                "target_scalar": None,
            })
        else:
            scalar = 1 + digest_int(
                "P1480", deck_name, fixture["L"], "random-scalar", index
            ) % (fixture["order"] - 1)
            queries.append({
                "query_index": index,
                "kind": "random_scalar",
                "target": scalar * context["generator"],
                "target_scalar": scalar,
            })
    return queries


def support_summary(support: dict[Any, Any], ordered_count: int) -> dict[str, Any]:
    return {
        "ordered_generation_count": ordered_count,
        "point_support_count": len(support),
        "x_orbit_support_count": len({key[0] for key in support if key != ("O",)}),
        "identity_supported": ("O",) in support,
        "collision_excess": ordered_count - len(support),
    }


def forward_setup(deck: list[Any]) -> dict[str, Any]:
    started = time.perf_counter()
    support: dict[Any, tuple[Any, tuple[Any, Any]]] = {}
    additions = 0
    probes = 0
    for first in deck:
        for second in deck:
            additions += 1
            total = first + second
            probes += 1
            support.setdefault(point_key(total), (total, (first, second)))
    summary = support_summary(support, additions)
    insertions = len(support)
    collisions = additions - insertions
    summary.update({
        "group_additions": additions,
        "hash_probes": probes,
        "hash_insertions": insertions,
        "stored_point_records": insertions,
        "setup_work": additions + probes + insertions + collisions + insertions,
        "witness_failure_count": 0,
        "wall_seconds": time.perf_counter() - started,
    })
    for key, (point, witness) in support.items():
        if point_key(point) != key or witness[0] + witness[1] != point:
            raise RuntimeError("P1481 forward witness failure")
    return {"support": support, "summary": summary}


def candidate_query(
    context: dict[str, Any], deck: list[Any], setup: dict[str, Any], target: Any
) -> dict[str, Any]:
    started = time.perf_counter()
    b1: dict[Any, tuple[Any, tuple[Any]]] = {}
    b1_additions = 0
    for fifth in deck:
        b1_additions += 1
        state = target - fifth
        b1.setdefault(point_key(state), (state, (fifth,)))

    b2: dict[Any, tuple[Any, tuple[Any, Any]]] = {}
    b2_additions = 0
    for key in sorted(b1, key=repr):
        state, fifth_witness = b1[key]
        for fourth in deck:
            b2_additions += 1
            prior = state - fourth
            b2.setdefault(point_key(prior), (prior, (fourth, fifth_witness[0])))

    join_additions = 0
    hash_probes = 0
    hit_count = 0
    hit_states: set[Any] = set()
    first_source = None
    witness_failures = 0
    for key in sorted(b2, key=repr):
        state, backward_witness = b2[key]
        for third in deck:
            join_additions += 1
            needed = state - third
            hash_probes += 1
            needed_key = point_key(needed)
            if needed_key not in setup["support"]:
                continue
            hit_count += 1
            hit_states.add((key, point_key(third), needed_key))
            source = setup["support"][needed_key][1] + (third,) + backward_witness
            total = sum(source, context["identity"])
            if len(source) != 5 or total != target:
                witness_failures += 1
            elif first_source is None:
                first_source = source
    if witness_failures:
        raise RuntimeError("P1481 candidate witness failure")
    b1_summary = support_summary(b1, b1_additions)
    b2_summary = support_summary(b2, b2_additions)
    b2_summary["source_metadata_endpoint_references"] = 2 * len(b2)
    b2_summary["storage_units_with_source_metadata"] = 3 * len(b2)
    complete_work = b1_additions + b2_additions + join_additions + hash_probes
    return {
        "status": "sat" if first_source is not None else "unsat",
        "b1": b1_summary,
        "b2": b2_summary,
        "join": {
            "group_additions": join_additions,
            "forward_hash_probes": hash_probes,
            "hit_count": hit_count,
            "distinct_hit_state_count": len(hit_states),
            "full_scan_after_first_hit": True,
        },
        "complete_candidate_work": complete_work,
        "verified_source": [point_json(point) for point in first_source] if first_source else None,
        "source_replayed": first_source is not None,
        "witness_failure_count": witness_failures,
        "wall_seconds": time.perf_counter() - started,
    }


def extend_oracle_support(
    prior: dict[Any, tuple[Any, tuple[Any, ...]]], deck: list[Any]
) -> tuple[dict[Any, tuple[Any, tuple[Any, ...]]], int]:
    output: dict[Any, tuple[Any, tuple[Any, ...]]] = {}
    generated = 0
    for key in sorted(prior, key=repr):
        point, witness = prior[key]
        for endpoint in deck:
            generated += 1
            total = point + endpoint
            output.setdefault(point_key(total), (total, witness + (endpoint,)))
    return output, generated


def exact_a5_oracle(deck: list[Any]) -> dict[str, Any]:
    started = time.perf_counter()
    support = {point_key(point): (point, (point,)) for point in deck}
    levels = [{
        "endpoint_length": 1,
        "ordered_generation_count": len(deck),
        "point_support_count": len(support),
    }]
    for length in range(2, 6):
        support, generated = extend_oracle_support(support, deck)
        levels.append({
            "endpoint_length": length,
            "ordered_generation_count": generated,
            "point_support_count": len(support),
        })
    return {"support": support, "levels": levels, "wall_seconds": time.perf_counter() - started}


def run_deck(
    context: dict[str, Any], deck_name: str, roots: list[int]
) -> dict[str, Any]:
    deck = deck_points(context, roots)
    setup = forward_setup(deck)
    queries = make_queries(context, deck_name, roots)
    candidate_rows = [candidate_query(context, deck, setup, query["target"]) for query in queries]
    candidate_phase_sealed_at = time.time_ns()
    oracle = exact_a5_oracle(deck)
    scored = []
    for query, candidate in zip(queries, candidate_rows):
        target = query["target"]
        oracle_sat = point_key(target) in oracle["support"] or point_key(-target) in oracle["support"]
        scored.append({
            "query_index": query["query_index"],
            "kind": query["kind"],
            "target": point_json(target),
            "target_scalar": query["target_scalar"],
            "candidate": candidate,
            "oracle_sat": oracle_sat,
            "candidate_oracle_agreement": (candidate["status"] == "sat") == oracle_sat,
            "planted_positive_verified": query["kind"] != "planted_positive" or candidate["status"] == "sat",
        })
    return {
        "deck_name": deck_name,
        "root_count": len(roots),
        "endpoint_count": len(deck),
        "root_sha256": hashlib.sha256(
            b"|".join(str(root).encode("ascii") for root in roots)
        ).hexdigest(),
        "setup": setup["summary"],
        "queries": scored,
        "oracle": {
            "started_after_all_candidate_decisions": True,
            "candidate_phase_sealed_at_ns": candidate_phase_sealed_at,
            "levels": oracle["levels"],
            "wall_seconds": oracle["wall_seconds"],
        },
        "all_agree": all(row["candidate_oracle_agreement"] for row in scored),
        "all_planted_verified": all(row["planted_positive_verified"] for row in scored),
        "all_sat_sources_replayed": all(
            row["candidate"]["status"] != "sat" or row["candidate"]["source_replayed"]
            for row in scored
        ),
    }


def fit_slope(xs: list[float], ys: list[float]) -> dict[str, Any]:
    def slope(sub_x: list[float], sub_y: list[float]) -> float:
        log_x = [math.log(value) for value in sub_x]
        log_y = [math.log(value) for value in sub_y]
        mean_x, mean_y = statistics.mean(log_x), statistics.mean(log_y)
        return sum((x - mean_x) * (y - mean_y) for x, y in zip(log_x, log_y)) / sum(
            (x - mean_x) ** 2 for x in log_x
        )

    full = slope(xs, ys)
    leave_one_out = [
        slope(
            [value for index, value in enumerate(xs) if index != omitted],
            [value for index, value in enumerate(ys) if index != omitted],
        )
        for omitted in range(len(xs))
    ]
    return {
        "slope": full,
        "leave_one_out": leave_one_out,
        "leave_one_out_min": min(leave_one_out),
        "leave_one_out_max": max(leave_one_out),
    }


def deck_metric(cells: list[dict[str, Any]], deck_name: str, metric: str) -> list[float]:
    values = []
    for cell in cells:
        deck = next(row for row in cell["decks"] if row["deck_name"] == deck_name)
        if metric == "setup_work":
            values.append(deck["setup"]["setup_work"])
        elif metric == "complete_work":
            values.append(max(row["candidate"]["complete_candidate_work"] for row in deck["queries"]))
        elif metric == "b2_point_support":
            values.append(max(row["candidate"]["b2"]["point_support_count"] for row in deck["queries"]))
        elif metric == "b2_x_support":
            values.append(max(row["candidate"]["b2"]["x_orbit_support_count"] for row in deck["queries"]))
        elif metric == "b2_storage":
            values.append(max(row["candidate"]["b2"]["storage_units_with_source_metadata"] for row in deck["queries"]))
        elif metric == "join_work":
            values.append(max(
                row["candidate"]["join"]["group_additions"]
                + row["candidate"]["join"]["forward_hash_probes"]
                for row in deck["queries"]
            ))
        else:
            raise ValueError(metric)
    return values


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError(f"refusing symlink output: {path}")
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    fit = payload["fits"]["subgroup_x_complete_work"]
    b2_fit = payload["fits"]["subgroup_x_b2_storage"]
    return "\n".join([
        "# P1481 finite-field serial-message propagation",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        f"Subgroup complete-work slope: `{fit['slope']:.6f}`; leave-one-out max `{fit['leave_one_out_max']:.6f}`.",
        "",
        f"Subgroup B2-storage slope: `{b2_fit['slope']:.6f}`; leave-one-out max `{b2_fit['leave_one_out_max']:.6f}`.",
        "",
        f"All candidate/oracle decisions agree: `{payload['gates']['all_candidate_oracle_decisions_agree']}`.",
        "",
        "Native group propagation restores exact SAT/UNSAT and source replay.",
        "Promotion still requires strict complete-query exponent below 3/2 and",
        "an exact representation smaller than the raw backward frontier.",
        "",
    ])


def main() -> int:
    os.chdir(ROOT)
    observed = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    expected = {str(path.relative_to(ROOT)): digest for path, digest in EXPECTED.items()}
    if observed != expected:
        raise RuntimeError("frozen P1481 input mismatch")

    cells = []
    for fixture in FIXTURES:
        context = build_context(fixture)
        subgroup = subgroup_roots(context)
        deck_rows = [
            run_deck(context, "subgroup_x", subgroup),
            run_deck(context, "random_x", random_x_roots(context, len(subgroup))),
        ]
        cells.append({
            "fixture": fixture,
            "generator": point_json(context["generator"]),
            "decks": deck_rows,
        })
        print(json.dumps({
            "L": fixture["L"],
            "decks": {
                deck["deck_name"]: {
                    "setup_work": deck["setup"]["setup_work"],
                    "max_b2": max(row["candidate"]["b2"]["point_support_count"] for row in deck["queries"]),
                    "max_complete_work": max(row["candidate"]["complete_candidate_work"] for row in deck["queries"]),
                    "all_agree": deck["all_agree"],
                }
                for deck in deck_rows
            },
        }, sort_keys=True), flush=True)

    xs = [cell["fixture"]["L"] for cell in cells]
    fits = {}
    metrics = ("setup_work", "complete_work", "b2_point_support", "b2_x_support", "b2_storage", "join_work")
    for deck_name in ("subgroup_x", "random_x"):
        for metric in metrics:
            fits[f"{deck_name}_{metric}"] = fit_slope(xs, deck_metric(cells, deck_name, metric))

    all_decks = [deck for cell in cells for deck in cell["decks"]]
    all_agree = all(deck["all_agree"] for deck in all_decks)
    all_planted = all(deck["all_planted_verified"] for deck in all_decks)
    all_sources = all(deck["all_sat_sources_replayed"] for deck in all_decks)
    setup_fit = fits["subgroup_x_setup_work"]
    complete_fit = fits["subgroup_x_complete_work"]
    storage_fit = fits["subgroup_x_b2_storage"]
    setup_gate = setup_fit["slope"] <= 2 + 1e-12 and setup_fit["leave_one_out_max"] <= 2 + 1e-12
    complete_gate = complete_fit["slope"] < 1.5 and complete_fit["leave_one_out_max"] < 1.5
    storage_gate = storage_fit["slope"] < 1.5 and storage_fit["leave_one_out_max"] < 1.5
    subgroup_beats_control = all(
        max(row["candidate"]["b2"]["point_support_count"] for row in cell["decks"][0]["queries"])
        < max(row["candidate"]["b2"]["point_support_count"] for row in cell["decks"][1]["queries"])
        for cell in cells
    )
    signal = all((all_agree, all_planted, all_sources, setup_gate, complete_gate, storage_gate, subgroup_beats_control))
    status = (
        "OBSERVATION_P1481_FINITE_FIELD_SERIAL_MESSAGE_SIGNAL"
        if signal
        else "NEGATIVE_RESULT_P1481_RAW_SERIAL_MESSAGE_FRONTIER_EXCEEDS_GATE"
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "cells": cells,
        "fits": fits,
        "gates": {
            "all_candidate_oracle_decisions_agree": all_agree,
            "all_planted_positives_verified": all_planted,
            "all_sat_sources_replayed": all_sources,
            "setup_all_slopes_at_most_two": setup_gate,
            "subgroup_complete_work_all_slopes_below_three_halves": complete_gate,
            "subgroup_b2_storage_all_slopes_below_three_halves": storage_gate,
            "subgroup_b2_strictly_smaller_than_random_x_every_fixture": subgroup_beats_control,
            "candidate_materializes_no_a3_through_a5": True,
            "oracle_started_after_candidate_decisions": all(
                deck["oracle"]["started_after_all_candidate_decisions"] for deck in all_decks
            ),
            "relation_rank_descent_not_waived": True,
        },
        "finite_field_serial_message_signal": signal,
        "frozen_files": observed,
        "boundary": (
            "The candidate is complete and source-resolving, but raw B2 messages and the full "
            "third-endpoint join remain charged. A negative does not rule out a compressed exact message."
        ),
        "next_action": (
            "If the raw frontier fails, freeze its point/x-orbit counts and test an exact subgroup-specific "
            "message representation. Do not rerun the same traversal with a faster hash table."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "note": str(NOTE.relative_to(ROOT)),
        "status": status,
        "subgroup_complete_fit": complete_fit,
        "subgroup_b2_storage_fit": storage_fit,
        "signal": signal,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
