#!/usr/bin/env python3
"""Exact twelve-card typed-scope evaluator for EXP-ENDO-c6c7a7.

Generic finite arithmetic only. Labels are produced from predicates on the
declared domain; the oracle is loaded only after every raw row exists.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

Point = tuple[int, ...]


def mod(n: int, p: int) -> int:
    return n % p


def vec_add(u: Point, v: Point, p: int) -> Point:
    return tuple(mod(a + b, p) for a, b in zip(u, v))


def vec_scale(lam: int, v: Point, p: int) -> Point:
    return tuple(mod(lam * a, p) for a in v)


def mat_vec(A: list[list[int]], x: Point, p: int) -> Point:
    dim = len(x)
    out = []
    for i in range(dim):
        s = 0
        for j in range(dim):
            s += mod(A[i][j], p) * x[j]
        out.append(mod(s, p))
    return tuple(out)


def apply_f(A: list[list[int]], b: list[int], x: Point, p: int) -> Point:
    return vec_add(mat_vec(A, x, p), tuple(mod(bi, p) for bi in b), p)


def enumerate_domain(p: int, dim: int, C: dict[str, Any]) -> list[Point]:
    kind = C["kind"]
    if kind == "full":
        return list(itertools.product(range(p), repeat=dim))
    if kind == "line":
        g = tuple(mod(int(c), p) for c in C["generator"])
        if len(g) != dim:
            raise ValueError(f"generator length {len(g)} != dimension {dim}")
        pts = [vec_scale(t, g, p) for t in range(p)]
        # Deduplicate while preserving generator order (zero appears once).
        seen: set[Point] = set()
        out: list[Point] = []
        for pt in pts:
            if pt not in seen:
                seen.add(pt)
                out.append(pt)
        return out
    raise ValueError(f"unknown domain kind {kind!r}")


def evaluate_completion(completion: dict[str, Any]) -> dict[str, Any]:
    p = int(completion["p"])
    dim = int(completion["dimension"])
    A = [[int(x) for x in row] for row in completion["A"]]
    b = [int(x) for x in completion["b"]]
    if len(A) != dim or any(len(row) != dim for row in A) or len(b) != dim:
        raise ValueError("A/b shape does not match dimension")

    domain = enumerate_domain(p, dim, completion["C"])
    images = [apply_f(A, b, x, p) for x in domain]
    image_set = set(images)
    domain_set = set(domain)
    zero = tuple(0 for _ in range(dim))

    origin_preserving = apply_f(A, b, zero, p) == zero

    additive = True
    additive_witness = None
    for x, y in itertools.product(domain, repeat=2):
        lhs = apply_f(A, b, vec_add(x, y, p), p)
        rhs = vec_add(apply_f(A, b, x, p), apply_f(A, b, y, p), p)
        if lhs != rhs:
            additive = False
            additive_witness = {"x": list(x), "y": list(y), "f_x_plus_y": list(lhs),
                                "fx_plus_fy": list(rhs)}
            break

    invariant = image_set <= domain_set
    invariance_failures = [
        {"x": list(x), "f_x": list(fx)}
        for x, fx in zip(domain, images)
        if fx not in domain_set
    ]

    # Permutation of C is independent of scalar candidates: bijection C -> C.
    permutation = invariant and len(image_set) == len(domain_set)

    scalar_candidates: list[int] = []
    for lam in range(p):
        if all(apply_f(A, b, x, p) == vec_scale(lam, x, p) for x in domain):
            scalar_candidates.append(lam)
    nonzero = [lam for lam in scalar_candidates if lam != 0]

    failure_witnesses: dict[str, Any] = {}
    if not origin_preserving:
        failure_witnesses["origin"] = {"f_0": list(apply_f(A, b, zero, p))}
    if additive_witness is not None:
        failure_witnesses["additivity"] = additive_witness
    if invariance_failures:
        failure_witnesses["invariance"] = invariance_failures
    if not permutation:
        failure_witnesses["permutation"] = {
            "image_size": len(image_set),
            "domain_size": len(domain_set),
            "invariant": invariant,
        }
    if not nonzero:
        # Exhibit a pair that no single nonzero scalar can cover, if possible.
        if domain:
            nonzero_pts = [x for x in domain if x != zero]
            if not nonzero_pts:
                failure_witnesses["nonzero_scalar"] = {
                    "reason": "domain is {0}; no nonzero test vector"
                }
            else:
                # For each nonzero lambda, a witness x with f(x) != λx.
                witnesses = []
                for lam in range(1, p):
                    for x in nonzero_pts:
                        fx = apply_f(A, b, x, p)
                        if fx != vec_scale(lam, x, p):
                            witnesses.append({
                                "lambda": lam,
                                "x": list(x),
                                "f_x": list(fx),
                                "lambda_x": list(vec_scale(lam, x, p)),
                            })
                            break
                failure_witnesses["nonzero_scalar"] = witnesses

    # Spec: certified iff a nonzero scalar works for every x and maps C to itself.
    certified = bool(nonzero) and invariant
    completion_label = "certified" if certified else "contradicted"

    weaker_true: list[str] = []
    if origin_preserving:
        weaker_true.append("origin_preserving")
    if additive:
        weaker_true.append("additive")
    if invariant:
        weaker_true.append("invariant")
    if permutation:
        weaker_true.append("permutation_of_C")
    if 0 in scalar_candidates:
        weaker_true.append("zero_scalar")
    if nonzero:
        weaker_true.append("nonzero_scalar_restriction")

    return {
        "p": p,
        "dimension": dim,
        "field": f"F_{p}",
        "domain_kind": completion["C"]["kind"],
        "domain_points": [list(x) for x in domain],
        "image_points": [list(fx) for fx in images],
        "origin_preserving": origin_preserving,
        "additive": additive,
        "invariant": invariant,
        "scalar_candidates_including_zero": scalar_candidates,
        "nonzero_scalar_candidates": nonzero,
        "permutation": permutation,
        "failure_witnesses": failure_witnesses,
        "weaker_true_properties": weaker_true,
        "label": completion_label,
        "map_f": {"A": [[mod(x, p) for x in row] for row in A], "b": [mod(x, p) for x in b]},
    }


def classify_card(card: dict[str, Any]) -> dict[str, Any]:
    completions = [evaluate_completion(c) for c in card["completions"]]
    labels = [c["label"] for c in completions]
    missing = card.get("missing")
    if missing is None and isinstance(card.get("statement"), dict):
        missing = card["statement"].get("missing_premise")

    if len(completions) == 1:
        card_label = labels[0]
        opposite = False
    else:
        opposite = len(set(labels)) > 1
        # Incomplete card is underdeclared only when completions disagree.
        card_label = "underdeclared" if opposite else labels[0]

    return {
        "card_id": card["id"],
        "statement": card.get("statement"),
        "missing_datum": missing,
        "completions": completions,
        "completion_labels": labels,
        "opposite_completion_outcomes": opposite,
        "label": card_label,
    }


def build_certificate(card_row: dict[str, Any], question: str) -> dict[str, Any]:
    first = card_row["completions"][0]
    # Domain/map text from the first completion; underdeclared cards keep both.
    cert = {
        "card_id": card_row["card_id"],
        "exact_question": question,
        "field_and_characteristic": first["field"],
        "ambient_object": f"{first['field']}^{first['dimension']}" if first["dimension"] > 1 else first["field"],
        "domain_C": {
            "kind": first["domain_kind"],
            "points": first["domain_points"],
        },
        "map_f": first["map_f"],
        "origin_and_additivity": {
            "origin_preserving": first["origin_preserving"],
            "additive": first["additive"],
        },
        "invariance_witness": {
            "invariant": first["invariant"],
            "failure_witnesses": first["failure_witnesses"].get("invariance", []),
        },
        "scalar_candidate_and_witness": {
            "including_zero": first["scalar_candidates_including_zero"],
            "nonzero": first["nonzero_scalar_candidates"],
        },
        "nonzero_check": bool(first["nonzero_scalar_candidates"]),
        "label": card_row["label"],
        "counterexample_or_missing_premise": (
            card_row["missing_datum"]
            if card_row["label"] == "underdeclared"
            else first["failure_witnesses"]
        ),
        "two_completions_if_underdeclared": (
            [
                {
                    "completion_index": i,
                    "field": c["field"],
                    "domain_points": c["domain_points"],
                    "image_points": c["image_points"],
                    "label": c["label"],
                    "nonzero_scalar_candidates": c["nonzero_scalar_candidates"],
                    "invariant": c["invariant"],
                    "permutation": c["permutation"],
                    "failure_witnesses": c["failure_witnesses"],
                }
                for i, c in enumerate(card_row["completions"])
            ]
            if card_row["label"] == "underdeclared"
            else None
        ),
        "transfer_limits": (
            "Toy finite additive spaces F_2/F_5 of dimension at most 2. "
            "No elliptic curve, no cryptographic parameter, no transfer."
        ),
        "weaker_true_properties": first["weaker_true_properties"],
    }
    if len(card_row["completions"]) > 1:
        cert["all_completion_fields"] = [c["field"] for c in card_row["completions"]]
        cert["all_completion_domains"] = [c["domain_points"] for c in card_row["completions"]]
        cert["all_completion_maps"] = [c["map_f"] for c in card_row["completions"]]
    return cert


def metrics_from(card_rows: list[dict[str, Any]], oracle_by_id: dict[str, str] | None) -> dict[str, Any]:
    by_id = {r["card_id"]: r for r in card_rows}
    v_ids = ["V1", "V2", "V3", "V4"]
    n_ids = ["N1", "N2", "N3", "N4"]
    u_ids = ["U1", "U2", "U3", "U4"]

    positive_retention = sum(1 for i in v_ids if by_id[i]["label"] == "certified")
    false_certifications = sum(1 for i in n_ids if by_id[i]["label"] == "certified")
    underdeclared_ok = sum(
        1 for i in u_ids
        if by_id[i]["label"] == "underdeclared" and by_id[i]["opposite_completion_outcomes"]
    )
    # Evaluator never upgrades a weaker true property into the target claim.
    unsupported_strengthenings = 0
    for row in card_rows:
        if row["label"] == "certified":
            # A certified card must actually have a nonzero scalar on C.
            if not any(c["nonzero_scalar_candidates"] and c["invariant"] for c in row["completions"]):
                unsupported_strengthenings += 1
        if row["label"] == "underdeclared" and not row["opposite_completion_outcomes"]:
            unsupported_strengthenings += 1

    oracle_matches = None
    complete_correct = None
    if oracle_by_id is not None:
        oracle_matches = {cid: by_id[cid]["label"] == oracle_by_id[cid] for cid in by_id}
        complete_correct = sum(1 for ok in oracle_matches.values() if ok)

    return {
        "complete_correct_certificates": complete_correct,
        "oracle_label_matches": oracle_matches,
        "false_certifications_negative_controls": false_certifications,
        "negative_control_ids": n_ids,
        "positive_retention_valid_controls": positive_retention,
        "positive_control_ids": v_ids,
        "underdeclared_preservation": underdeclared_ok,
        "underdeclared_ids": u_ids,
        "unsupported_strengthenings": unsupported_strengthenings,
        "card_count": len(card_rows),
        "completion_count": sum(len(r["completions"]) for r in card_rows),
        "predicted_formula": "12/12; zero false certifications; 4 positive and 4 underdeclared retained.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures",
        default="experiments/EXP-ENDO-c6c7a7/fixtures.json",
    )
    parser.add_argument(
        "--oracle",
        default="experiments/EXP-ENDO-c6c7a7/oracle-key.json",
    )
    parser.add_argument(
        "--out-dir",
        default="experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Recorded only; evaluation is deterministic.",
    )
    args = parser.parse_args(argv)

    fixtures_path = Path(args.fixtures)
    oracle_path = Path(args.oracle)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures = json.loads(fixtures_path.read_text())
    question = fixtures["question"]
    cards = fixtures["cards"]
    if len(cards) != 12:
        raise SystemExit(f"expected 12 cards, found {len(cards)}")

    # --- raw evaluation, oracle unread ---
    card_rows = [classify_card(card) for card in cards]
    raw_rows = []
    for row in card_rows:
        for idx, completion in enumerate(row["completions"]):
            raw_rows.append({
                "card_id": row["card_id"],
                "completion_index": idx,
                "field": completion["field"],
                "domain_points": completion["domain_points"],
                "image_points": completion["image_points"],
                "origin_preserving": completion["origin_preserving"],
                "additive": completion["additive"],
                "invariant": completion["invariant"],
                "scalar_candidates_including_zero": completion["scalar_candidates_including_zero"],
                "nonzero_scalar_candidates": completion["nonzero_scalar_candidates"],
                "permutation": completion["permutation"],
                "failure_witnesses": completion["failure_witnesses"],
                "label": completion["label"],
                "missing_datum": row["missing_datum"],
                "card_label": row["label"],
            })

    certificates = [build_certificate(row, question) for row in card_rows]

    # --- oracle comparison only after raw rows exist ---
    oracle = json.loads(oracle_path.read_text())
    oracle_by_id = {e["card_id"]: e["label"] for e in oracle["entries"]}
    metrics = metrics_from(card_rows, oracle_by_id)
    metrics["oracle_compared_after_raw"] = True
    metrics["seed"] = args.seed

    raw_result = {
        "experiment_id": "EXP-ENDO-c6c7a7",
        "run_id": "RUN-ENDO-c6c7a7-single",
        "seed": args.seed,
        "question": question,
        "scalar_meaning": fixtures.get("scalar_meaning"),
        "interpretation": fixtures.get("interpretation"),
        "cards": card_rows,
        "raw_rows": raw_rows,
        "oracle_loaded_after_raw": True,
        "oracle_expected_labels": oracle_by_id,
    }

    (out_dir / "raw-result.json").write_text(json.dumps(raw_result, indent=2) + "\n")
    (out_dir / "certificates.json").write_text(
        json.dumps({"experiment_id": "EXP-ENDO-c6c7a7", "certificates": certificates}, indent=2) + "\n"
    )
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    print("EXP-ENDO-c6c7a7 RUN-ENDO-c6c7a7-single")
    print(f"cards={len(card_rows)} completions={metrics['completion_count']} seed={args.seed}")
    for row in card_rows:
        print(
            f"  {row['card_id']}: card_label={row['label']} "
            f"completion_labels={row['completion_labels']} "
            f"opposite={row['opposite_completion_outcomes']}"
        )
    print(
        "metrics: "
        f"complete_correct={metrics['complete_correct_certificates']} "
        f"false_cert_N={metrics['false_certifications_negative_controls']} "
        f"positive_V={metrics['positive_retention_valid_controls']} "
        f"underdeclared_U={metrics['underdeclared_preservation']} "
        f"unsupported_strengthenings={metrics['unsupported_strengthenings']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
