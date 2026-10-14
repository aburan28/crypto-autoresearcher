#!/usr/bin/env python3
"""Independently verify the frozen conductor-gap panel.

This verifier intentionally does not import ``build_panel.py``.  It checks the
generated panel against exact arithmetic and the archived source records, and
writes a deterministic receipt.  It does not construct an isogeny, certify a
point map, or measure an ECDLP transfer.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from sympy import __version__ as sympy_version
from sympy import factorint


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PANEL_PATH = HERE / "panel.json"
RECEIPT_PATH = HERE / "verification.json"
PANEL_SCHEMA = "crypto.conductor-gap-panel/v1"
RECEIPT_SCHEMA = "crypto.conductor-gap-panel-verification/v1"


class VerificationError(RuntimeError):
    """A deterministic panel verification failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def require_equal(observed: Any, expected: Any, label: str) -> None:
    if observed != expected:
        raise VerificationError(
            f"{label}: observed {observed!r}, expected {expected!r}"
        )


def read_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def product(values: list[int]) -> int:
    answer = 1
    for value in values:
        answer *= value
    return answer


def factor_pairs(value: int) -> list[tuple[int, int]]:
    factors = [(int(p), int(e)) for p, e in factorint(value).items()]
    factors.sort()
    require(product([p**e for p, e in factors]) == value,
            f"incomplete factorization of {value}")
    return factors


PRIME_CERTIFICATES: dict[int, dict[str, Any]] = {}


def prove_prime(n: int) -> None:
    """Build a recursive Lucas n-1 certificate for n.

    ``factorint`` proposes the factorization.  The recursive certificates and
    Lucas conditions establish primality; a probable-prime predicate is not
    used as the acceptance condition.
    """
    if n in PRIME_CERTIFICATES:
        return
    require(n >= 2, f"invalid prime candidate {n}")
    if n == 2:
        PRIME_CERTIFICATES[n] = {
            "n": "2", "n_minus_1_factorization": [], "witnesses": []
        }
        return
    require(n % 2 == 1, f"even composite prime candidate {n}")
    factors = factor_pairs(n - 1)
    for q, _ in factors:
        prove_prime(q)
    witnesses: list[tuple[str, int]] = []
    for q, _ in factors:
        witness = None
        for candidate in range(2, min(n, 10_000)):
            if (
                pow(candidate, n - 1, n) == 1
                and math.gcd(pow(candidate, (n - 1) // q, n) - 1, n) == 1
            ):
                witness = candidate
                break
        require(witness is not None,
                f"no Lucas n-1 witness below 10000 for n={n}, q={q}")
        witnesses.append((str(q), witness))
    PRIME_CERTIFICATES[n] = {
        "n": str(n),
        "n_minus_1_factorization": [[str(q), e] for q, e in factors],
        "witnesses": [[q, a] for q, a in witnesses],
    }


def verify_prime_certificate(n: int, active: set[int] | None = None) -> None:
    active = set() if active is None else active
    require(n not in active, f"cycle in primality certificate for {n}")
    node = PRIME_CERTIFICATES.get(n)
    require(node is not None, f"missing primality certificate for {n}")
    if n == 2:
        require_equal(node["n_minus_1_factorization"], [], "prime 2 factors")
        return
    active.add(n)
    factors = [(int(q), int(e)) for q, e in node["n_minus_1_factorization"]]
    require_equal(product([q**e for q, e in factors]), n - 1,
                  f"certificate product for {n}")
    witnesses = {int(q): int(a) for q, a in node["witnesses"]}
    require_equal(set(witnesses), {q for q, _ in factors},
                  f"certificate witnesses for {n}")
    for q, _ in factors:
        verify_prime_certificate(q, active)
        a = witnesses[q]
        require_equal(pow(a, n - 1, n), 1,
                      f"Lucas Fermat condition for n={n}, q={q}")
        require_equal(math.gcd(pow(a, (n - 1) // q, n) - 1, n), 1,
                      f"Lucas gcd condition for n={n}, q={q}")
    active.remove(n)


def kronecker_minus_7(p: int) -> int:
    if p == 7:
        return 0
    value = pow((-7) % p, (p - 1) // 2, p)
    require(value in {1, p - 1}, f"invalid Euler criterion result for {p}")
    return 1 if value == 1 else -1


def tau_power_linear(m: int, mu: int) -> tuple[int, int]:
    """Return x,y for tau^m=x+y*tau by a linear recurrence."""
    x, y = 1, 0
    for _ in range(m):
        x, y = -2 * y, x + mu * y
    return x, y


def exact_multiplicative_order(value: int, prime: int) -> int:
    factors = [
        (int(q), int(e))
        for q, e in PRIME_CERTIFICATES[prime]["n_minus_1_factorization"]
    ]
    order = prime - 1
    for q, exponent in factors:
        for _ in range(exponent):
            if order % q == 0 and pow(value, order // q, prime) == 1:
                order //= q
            else:
                break
    require_equal(pow(value, order, prime), 1,
                  f"multiplicative order terminal power modulo {prime}")
    for q, _ in factors:
        if order % q == 0:
            require(pow(value, order // q, prime) != 1,
                    f"multiplicative order not minimal modulo {prime}")
    return order


def rankdata(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for cursor in range(index, end):
            ranks[ordered[cursor][0]] = rank
        index = end
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - x_mean) ** 2 for x in xs)
        * sum((y - y_mean) ** 2 for y in ys)
    )
    return numerator / denominator


def expected_csv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


def verify_csv(relative_path: str, rows: list[dict[str, Any]]) -> None:
    path = HERE / relative_path
    require(path.is_file(), f"missing CSV {path}")
    expected_fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in expected_fields:
                expected_fields.append(key)
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        require_equal(reader.fieldnames, expected_fields, f"{relative_path} header")
        observed_rows = list(reader)
    require_equal(len(observed_rows), len(rows), f"{relative_path} row count")
    for index, (observed, expected) in enumerate(zip(observed_rows, rows), 1):
        for key in expected_fields:
            require_equal(observed[key], expected_csv_cell(expected.get(key)),
                          f"{relative_path} row {index} field {key}")


def verify_source_hashes(panel: dict[str, Any]) -> int:
    source_rows = panel["sources"]
    source_paths = [row["path"] for row in source_rows]
    require_equal(len(source_paths), len(set(source_paths)), "source path uniqueness")
    for row in source_rows:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing source {row['path']}")
        require_equal(sha256(path), row["sha256"], f"source hash {row['path']}")
    cited: set[str] = set()
    for section in (
        "classes", "gaps", "controls", "measured_effects",
        "construction_measurements",
    ):
        for row in panel[section]:
            if isinstance(row.get("evidence_path"), str):
                cited.add(row["evidence_path"])
    cited.add(panel["p224_candidate"]["evidence_path"])
    require(cited <= set(source_paths),
            f"unhashed cited evidence paths: {sorted(cited - set(source_paths))}")
    return len(source_rows)


def verify_measured_effects(panel: dict[str, Any]) -> dict[str, int]:
    effects = {row["comparison_id"]: row for row in panel["measured_effects"]}
    require_equal(len(effects), len(panel["measured_effects"]),
                  "measured-effect id uniqueness")

    level_source = read_json(
        "research/isogeny_volcano_level_replication_20261013/results.json"
    )
    level_index = {
        (row["study"], row["factor"], row["context"]): row
        for row in level_source["contrasts"]
        if row["kind"] == "vertical_edge" and row["metric"] == "ops"
    }
    level_specs = {
        "m37-73-other-absent": ("m37", "73", "other_factor_absent"),
        "m37-73-other-present": ("m37", "73", "other_factor_present"),
        "m37-2663-other-absent": ("m37", "2663", "other_factor_absent"),
        "m37-2663-other-present": ("m37", "2663", "other_factor_present"),
        "m41-409-other-absent": ("m41", "409", "other_factor_absent"),
        "m41-409-other-present": ("m41", "409", "other_factor_present"),
        "m41-1721-other-absent": ("m41", "1721", "other_factor_absent"),
        "m41-1721-other-present": ("m41", "1721", "other_factor_present"),
    }
    for comparison_id, key in level_specs.items():
        archived = level_index[key]
        row = effects[comparison_id]
        require_equal(row["estimate_bits"], archived["log2_ratio"],
                      f"{comparison_id} estimate")
        require_equal(row["ci_lower_bits"], archived["pointwise95_bits_lo"],
                      f"{comparison_id} lower CI")
        require_equal(row["ci_upper_bits"], archived["pointwise95_bits_hi"],
                      f"{comparison_id} upper CI")

    accepted_source = read_json(
        "research/isogeny_volcano_m51_rho_20261013/analysis.json"
    )
    require_equal(accepted_source["status"], "VALID_FOR_SCOPED_INFERENCE",
                  "m51 accepted source status")
    accepted = next(
        row for row in accepted_source["contrasts"]
        if row["contrast_id"] == "primary-floor-tau17-vs-crater-tau17"
    )
    row = effects["m51-271-same-tau17-accepted"]
    require_equal(row["estimate_bits"], accepted["observed_bits"],
                  "m51 accepted estimate")
    require_equal(row["ci_lower_bits"], accepted["ci95_low"],
                  "m51 accepted lower CI")
    require_equal(row["ci_upper_bits"], accepted["ci95_high"],
                  "m51 accepted upper CI")

    deep_source = read_json(
        "research/isogeny_volcano_m51_deep_rho_20261013/analysis.json"
    )
    require_equal(deep_source["status"], "aa_alert_labels_withheld",
                  "m51 deep source status")
    deep_index = {row["id"]: row for row in deep_source["contrasts"]}
    deep_specs = {
        "m51-deep-271-other-absent": "A-C",
        "m51-deep-120871-other-absent": "P-C",
        "m51-deep-120871-other-present": "B-A",
        "m51-deep-271-other-present": "B-P",
    }
    for comparison_id, source_id in deep_specs.items():
        archived = deep_index[source_id]
        row = effects[comparison_id]
        require_equal(row["estimate_bits"], archived["bits"],
                      f"{comparison_id} estimate")
        require_equal(row["ci_lower_bits"], archived["modeled_population_lower_bits"],
                      f"{comparison_id} lower CI")
        require_equal(row["ci_upper_bits"], archived["modeled_population_upper_bits"],
                      f"{comparison_id} upper CI")
        require_equal(row["inference_status"], "withheld_aa_gate_failed",
                      f"{comparison_id} inference gate")
    require_equal(set(effects), set(level_specs) | {
        "m51-271-same-tau17-accepted", *deep_specs
    }, "measured-effect row set")
    return {"admitted_rows": 9, "withheld_rows": 4}


def extract_seconds(path: str, pattern: str) -> list[int]:
    text = (ROOT / path).read_text()
    return [int(value) for value in re.findall(pattern, text, flags=re.MULTILINE)]


def verify_construction_measurements(panel: dict[str, Any]) -> dict[str, int]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in panel["construction_measurements"]:
        stem, separator, suffix = row["measurement_id"].rpartition("-")
        require(separator == "-" and suffix.isdigit(),
                f"invalid measurement id {row['measurement_id']}")
        groups.setdefault(stem, []).append(row)
    for rows in groups.values():
        rows.sort(key=lambda row: row["sample_index"])
        require_equal(
            [row["sample_index"] for row in rows],
            list(range(1, len(rows) + 1)),
            f"sample indices for {rows[0]['measurement_id']}",
        )
        require(all(row["sample_count"] == len(rows) for row in rows),
                f"sample-count mismatch for {rows[0]['measurement_id']}")

    expected: dict[str, list[float]] = {
        "m41-409": extract_seconds(
            "research/isogeny_volcano_rho_m41_20261006/v409.out",
            r"^VERT409 .* (\d+) s$",
        ),
        "m41-1721": extract_seconds(
            "research/isogeny_volcano_rho_m41_20261006/v1721.out",
            r"^VERT1721 .* (\d+) s$",
        ),
        "m41-409floor-1721": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/second_level/down41.out",
            r"isogeny \d+:.*\((\d+) s\)",
        ),
        "m83-6473-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/cm_route/cm83.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m101-5857-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m101_a1_f5857.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m101-18583-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m101_a1_f18583.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m103-11329-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m103_a0_f11329.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m107a0-3209-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m107_a0_f3209.out",
            r"polclass.*?, (\d+) s$",
        ),
        "m107a1-3209-cm": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/survey/run_m107_a1_f3209.out",
            r"polclass.*?, (\d+) s$",
        ),
        "k163-45641": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_45641.out",
            r"isogeny \d+:.*\((\d+) s\)",
        ),
        "k163-82153": extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/analogues/run163_82153.out",
            r"isogeny \d+:.*\((\d+) s\)",
        ),
    }
    level2_paths = [
        "down163b.out", "down163c.out", "down163_s1.out",
        "down163_s2.out", "down163_s3.out", "down163_s4.out",
    ]
    expected["k163-level2-82153"] = [
        extract_seconds(
            "research/ecc2k130_conductor_isogenies_20261007/second_level/" + path,
            r"isogeny \d+:.*\((\d+) s\)",
        )[0]
        for path in level2_paths
    ]
    scan_session = read_json(
        "research/isogeny_volcano_m51_deep_scan_20261013/results/session.json"
    )
    scan_receipt = read_json(
        "research/isogeny_volcano_m51_deep_scan_20261013/results/classification-receipt.json"
    )
    require_equal(scan_session["sieve_hits"], 42, "m51 deep scan hit count")
    require_equal(scan_receipt["certified_pairs"], 42,
                  "m51 deep scan certified-pair count")
    expected["m51-deep-scan"] = [scan_session["elapsed_seconds"]]
    require_equal(set(groups), set(expected), "construction measurement group set")
    for name, times in expected.items():
        require_equal([row["elapsed_seconds"] for row in groups[name]], times,
                      f"construction times for {name}")

    conditional = groups["m41-409floor-1721"]
    require(all("exclude the separately logged 5-second embedding" in row["note"]
                for row in conditional), "m41 embedding exclusion not disclosed")
    level2 = groups["k163-level2-82153"]
    require(all("exclude each separately logged 29-second embedding" in row["note"]
                for row in level2), "K163 embedding exclusion not disclosed")
    scan = groups["m51-deep-scan"][0]
    require_equal(scan["source_f_E"], str(271 * 120871),
                  "m51 scan observed source conductor")
    require_equal(scan["target_f_E"], "120871",
                  "m51 scan observed target conductor")
    require("ascending bottom-to-parent" in scan["note"],
            "m51 scan direction not disclosed")
    return {"series": len(groups), "rows": len(panel["construction_measurements"])}


def verify_panel() -> dict[str, Any]:
    panel = json.loads(PANEL_PATH.read_text())
    require_equal(panel["schema"], PANEL_SCHEMA, "panel schema")
    source_count = verify_source_hashes(panel)

    classes = panel["classes"]
    gaps = panel["gaps"]
    levels = panel["levels"]
    adjacencies = panel["adjacencies"]
    controls = panel["controls"]
    summary = panel["summary"]
    class_by_id = {row["class_id"]: row for row in classes}
    require_equal(len(class_by_id), len(classes), "class id uniqueness")

    top_level_primes = sorted({int(row["edge_degree"]) for row in gaps})
    for prime in top_level_primes:
        prove_prime(prime)

    nist = read_json("research/endosweep_nist_20261006/nist.json")
    nist_names = {
        "nist-k163": "nist/K-163", "nist-k233": "nist/K-233",
        "nist-k283": "nist/K-283", "nist-k409": "nist/K-409",
        "nist-k571": "nist/K-571",
    }
    class_receipts: list[dict[str, Any]] = []
    for row in classes:
        match = re.fullmatch(r"y\^2\+xy=x\^3\+([01])\*x\^2\+1", row["curve_model"])
        require(match is not None, f"unrecognized curve model {row['curve_model']}")
        a = int(match.group(1))
        mu = 1 if a else -1
        m = int(row["extension_degree"])
        x, y = tau_power_linear(m, mu)
        q = 1 << m
        trace = 2 * x + mu * y
        f_pi = abs(y)
        factors = [int(value) for value in row["f_pi_factorization"]]
        require_equal(len(factors), len(set(factors)),
                      f"squarefree factor list for {row['class_id']}")
        require_equal(product(factors), f_pi, f"factor product for {row['class_id']}")
        require_equal(int(row["q"]), q, f"q for {row['class_id']}")
        require_equal(int(row["trace"]), trace, f"trace for {row['class_id']}")
        require_equal(int(row["ambient_order"]), q + 1 - trace,
                      f"ambient order for {row['class_id']}")
        require_equal(int(row["f_pi"]), f_pi, f"f_pi for {row['class_id']}")
        require_equal(trace * trace - 4 * q, -7 * f_pi * f_pi,
                      f"CM discriminant identity for {row['class_id']}")
        require_equal(row["D_K"], "-7", f"D_K for {row['class_id']}")
        require_equal(row["source_f_E"], "1", f"source order for {row['class_id']}")
        require_equal(row["prime_factor_count"], len(factors),
                      f"factor count for {row['class_id']}")
        require_equal(row["conductor_level_count"], 1 << len(factors),
                      f"level count for {row['class_id']}")
        require_equal(row["conditional_adjacency_count"],
                      len(factors) * (1 << (len(factors) - 1)),
                      f"adjacency count for {row['class_id']}")
        expected_class_number = product(
            [prime - kronecker_minus_7(prime) for prime in factors]
        )
        require_equal(int(row["global_bottom_class_number"]), expected_class_number,
                      f"bottom class number for {row['class_id']}")
        if row["class_id"] in nist_names:
            archived = nist["curves"][nist_names[row["class_id"]]]
            require_equal(q, int(archived["q"]), f"NIST q for {row['class_id']}")
            require_equal(trace, int(archived["t"]), f"NIST trace for {row['class_id']}")
            require_equal(f_pi, int(archived["exact"]["f"]),
                          f"NIST f_pi for {row['class_id']}")
            require_equal(a, int(archived["a"]), f"NIST a for {row['class_id']}")
        class_receipts.append({
            "class_id": row["class_id"], "m": m, "trace": str(trace),
            "f_pi": str(f_pi), "factor_count": len(factors),
            "discriminant_identity": "t^2-4q=-7*f_pi^2",
        })

    gap_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    gap_receipts: list[dict[str, Any]] = []
    for row in gaps:
        key = (row["class_id"], int(row["edge_degree"]))
        require(key not in gap_by_key, f"duplicate gap row {key}")
        gap_by_key[key] = row
        curve_class = class_by_id[row["class_id"]]
        ell = key[1]
        require(ell in [int(value) for value in curve_class["f_pi_factorization"]],
                f"gap prime {ell} absent from {row['class_id']} conductor")
        chi = kronecker_minus_7(ell)
        split = {1: "split", -1: "inert", 0: "ramified"}[chi]
        require_equal(row["kronecker_minus_7"], chi, f"Kronecker for {row['gap_id']}")
        require_equal(row["split_type"], split, f"split type for {row['gap_id']}")
        m = int(curve_class["extension_degree"])
        a = int(re.search(r"x\^3\+([01])\*x\^2", curve_class["curve_model"]).group(1))
        x, _ = tau_power_linear(m, 1 if a else -1)
        scalar = x % ell
        require_equal(int(row["q_frobenius_scalar_mod_ell"]), scalar,
                      f"Frobenius scalar for {row['gap_id']}")
        scalar_order = exact_multiplicative_order(scalar, ell)
        k = scalar_order // 2 if scalar_order % 2 == 0 else scalar_order
        sign = pow(scalar, k, ell)
        require(sign in {1, ell - 1}, f"invalid +/-1 power for {row['gap_id']}")
        require_equal(int(row["scalar_order_mod_ell"]), scalar_order,
                      f"scalar order for {row['gap_id']}")
        require_equal(int(row["relative_kernel_x_field_degree"]), k,
                      f"minimal kernel x-field degree for {row['gap_id']}")
        require_equal(int(row["absolute_kernel_x_field_degree"]), m * k,
                      f"absolute kernel field for {row['gap_id']}")
        require_equal(row["kernel_support"],
                      "source_curve" if sign == 1 else "quadratic_twist",
                      f"kernel support for {row['gap_id']}")
        kernel_degree = (ell - 1) // 2
        require_equal(int(row["kernel_polynomial_degree"]), kernel_degree,
                      f"kernel degree for {row['gap_id']}")
        require_equal(int(row["dense_packed_kernel_bytes"]),
                      (m * (kernel_degree + 1) + 7) // 8,
                      f"packed-kernel proxy for {row['gap_id']}")
        require_equal(int(row["local_ring_class_number"]), ell - chi,
                      f"local class number for {row['gap_id']}")
        require(math.isclose(row["gap_log2"], math.log2(ell),
                             rel_tol=0.0, abs_tol=1e-15),
                f"gap log2 for {row['gap_id']}")
        require_equal(row["valuation_in_f_pi"], 1,
                      f"conductor valuation for {row['gap_id']}")
        gap_receipts.append({
            "gap_id": row["gap_id"], "ell": str(ell), "split_type": split,
            "scalar_order": str(scalar_order), "minimal_k": str(k),
        })

    expected_gaps = {
        (row["class_id"], int(prime))
        for row in classes for prime in row["f_pi_factorization"]
    }
    require_equal(set(gap_by_key), expected_gaps, "complete class-prime gap set")

    level_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    expected_level_keys: set[tuple[str, int]] = set()
    expected_adjacency_keys: set[tuple[str, int, int, int]] = set()
    for curve_class in classes:
        class_id = curve_class["class_id"]
        factors = [int(value) for value in curve_class["f_pi_factorization"]]
        for mask in range(1 << len(factors)):
            selected = [p for index, p in enumerate(factors) if mask & (1 << index)]
            f_e = product(selected)
            expected_level_keys.add((class_id, f_e))
            for index, ell in enumerate(factors):
                if not mask & (1 << index):
                    expected_adjacency_keys.add((class_id, f_e, f_e * ell, ell))
    for row in levels:
        key = (row["class_id"], int(row["f_E"]))
        require(key not in level_by_key, f"duplicate level row {key}")
        level_by_key[key] = row
        curve_class = class_by_id[row["class_id"]]
        factors = [int(value) for value in curve_class["f_pi_factorization"]]
        selected = [int(value) for value in row["f_E_factorization"]]
        require_equal(product(selected), key[1], f"level factor product for {row['level_id']}")
        require(all(prime in factors for prime in selected),
                f"foreign prime in {row['level_id']}")
        require_equal(int(row["remaining_index"]), int(curve_class["f_pi"]) // key[1],
                      f"remaining index for {row['level_id']}")
        require_equal(int(row["ring_discriminant"]), -7 * key[1] * key[1],
                      f"ring discriminant for {row['level_id']}")
        require_equal(row["distance_from_crater"], len(selected),
                      f"level depth for {row['level_id']}")
        require_equal(int(row["ring_class_number"]), product(
            [prime - kronecker_minus_7(prime) for prime in selected]
        ), f"ring class number for {row['level_id']}")
    require_equal(set(level_by_key), expected_level_keys, "complete conductor-level set")

    observed_adjacency_keys: set[tuple[str, int, int, int]] = set()
    for row in adjacencies:
        key = (
            row["class_id"], int(row["source_f_E"]),
            int(row["target_f_E"]), int(row["edge_degree"]),
        )
        require(key not in observed_adjacency_keys, f"duplicate adjacency {key}")
        observed_adjacency_keys.add(key)
        require_equal(key[1] * key[3], key[2], f"adjacency multiplication for {key}")
        require_equal(row["direction"], "descending", f"adjacency direction for {key}")
        require((key[0], key[1]) in level_by_key and (key[0], key[2]) in level_by_key,
                f"adjacency endpoints absent for {key}")
    require_equal(observed_adjacency_keys, expected_adjacency_keys,
                  "complete conditional adjacency set")

    controls_by_name = {row["curve"]: row for row in controls}
    require_equal(len(controls_by_name), len(controls), "control name uniqueness")
    exact_control_names = {
        "P-192", "P-256", "P-384", "P-521",
        "B-163", "B-233", "B-283", "B-409",
    }
    for name in exact_control_names:
        archived = nist["curves"][f"nist/{name}"]
        row = controls_by_name[name]
        require_equal(archived["exact"]["f"], 1, f"NIST exact f for {name}")
        require_equal(row["f_pi"], "1", f"control f_pi for {name}")
        require_equal(int(row["D_K"]), int(archived["exact"]["D_K"]),
                      f"control D_K for {name}")
        require_equal(int(archived["t"]) ** 2 - 4 * int(archived["q"]),
                      int(row["D_K"]), f"control discriminant for {name}")

    parameter_receipt = (
        ROOT / "research/conductor_gap_panel_20261014/"
        "sect113r1-openssl-parameters.txt"
    ).read_text()
    order_match = re.search(r"Order:\s*\n\s*([0-9a-f:]+)", parameter_receipt)
    cofactor_match = re.search(r"Cofactor:\s+(\d+)", parameter_receipt)
    require(order_match is not None, "sect113r1 order absent from OpenSSL receipt")
    require(cofactor_match is not None,
            "sect113r1 cofactor absent from OpenSSL receipt")
    q113 = 1 << 113
    n113 = int(order_match.group(1).replace(":", ""), 16)
    require_equal(int(cofactor_match.group(1)), 2, "sect113r1 cofactor")
    trace113 = q113 + 1 - 2 * n113
    discriminant113 = trace113 * trace113 - 4 * q113
    factors113 = factor_pairs(abs(discriminant113))
    require_equal(discriminant113 % 4, 1, "sect113r1 discriminant residue")
    require(all(exponent == 1 for _, exponent in factors113),
            "sect113r1 discriminant is not squarefree")
    for prime, _ in factors113:
        prove_prime(prime)
    sect113 = controls_by_name["sect113r1"]
    require_equal(int(sect113["D_K"]), discriminant113, "sect113r1 D_K")
    require_equal(sect113["f_pi"], "1", "sect113r1 f_pi")
    require_equal(controls_by_name["B-571"]["status"], "exact_conductor_unresolved",
                  "B-571 unresolved status")
    require(controls_by_name["B-571"]["f_pi"] is None,
            "B-571 must not acquire an unsupported conductor")
    b571_bound = nist["curves"]["nist/B-571"]["bound"]
    require_equal(
        int(controls_by_name["B-571"]["abs_D_K_at_least"]),
        int(b571_bound["abs_D_K_at_least"]),
        "B-571 discriminant lower bound",
    )
    require_equal(
        controls_by_name["B-571"]["log2_abs_D_K_at_least"],
        b571_bound["log2"],
        "B-571 log2 discriminant lower bound",
    )
    require_equal(
        int(controls_by_name["B-571"]["min_nonscalar_degree_at_least"]),
        int(b571_bound["min_nonscalar_degree_at_least"]),
        "B-571 nonscalar-degree lower bound",
    )

    p224 = panel["p224_candidate"]
    nist_p224 = nist["curves"]["nist/P-224"]
    require_equal(nist_p224["exact"]["f"], 3, "P-224 f_pi")
    require_equal(p224["f_pi"], "3", "P-224 panel f_pi")
    require_equal(int(nist_p224["exact"]["D_K"]) % 3, 0,
                  "P-224 ramification")
    require_equal(p224["split_type"], "ramified", "P-224 split type")
    require_equal(p224["certified_vertical_gap"], False,
                  "P-224 vertical-gap certification gate")

    effects_receipt = verify_measured_effects(panel)
    construction_receipt = verify_construction_measurements(panel)

    action_audit = read_json("docs/reports/koblitz-rho-transfer-20261013/audit.json")
    action_index = {row["curve"]: row for row in action_audit["curves"]}
    source_action_rows: list[dict[str, Any]] = []
    for curve_class in classes:
        if curve_class["family"] != "nist-k":
            continue
        short_name = curve_class["label"].removeprefix("NIST ")
        archived = action_index[short_name]
        gain = archived["random_map_model"]["signed_tau_gain_vs_negation_bits"]
        require_equal(curve_class["source_signed_tau_gain_vs_negation_bits"], gain,
                      f"signed tau gain for {curve_class['class_id']}")
        require_equal(archived["tau"]["signed_action_order"],
                      2 * int(curve_class["extension_degree"]),
                      f"signed action order for {curve_class['class_id']}")
        source_action_rows.append({
            "schema": PANEL_SCHEMA,
            "class_id": curve_class["class_id"],
            "curve": curve_class["label"],
            "m": curve_class["extension_degree"],
            "signed_tau_orbit_size": 2 * curve_class["extension_degree"],
            "ideal_gain_vs_negation_bits": gain,
            "evidence_kind": "exact_random_map_prediction",
            "scope": "source_action_not_transfer_or_wall_time",
            "evidence_path": "docs/reports/koblitz-rho-transfer-20261013/audit.json",
        })

    csv_sections = {
        "gap-panel.csv": gaps,
        "level-panel.csv": levels,
        "adjacency-panel.csv": adjacencies,
        "controls.csv": controls,
        "measured-effects.csv": panel["measured_effects"],
        "construction-measurements.csv": panel["construction_measurements"],
        "source-actions.csv": source_action_rows,
    }
    for path, rows in csv_sections.items():
        verify_csv(path, rows)

    expected_twist_families = len({
        (row["extension_degree"], tuple(row["f_pi_factorization"]))
        for row in classes
    })
    expected_summary = {
        "certified_prime_direction_rows": len(gaps),
        "vertical_direction_rows": len(gaps),
        "horizontal_direction_rows": 0,
        "horizontal_search_status": "not_assessed_in_this_panel",
        "distinct_prime_degrees": len(top_level_primes),
        "finite_field_trace_isogeny_classes": len(classes),
        "twist_deduplicated_geometry_families": expected_twist_families,
        "exact_conductor_levels": len(levels),
        "conditional_adjacent_level_rows": len(adjacencies),
        "nist_k_prime_direction_rows": sum(row["family"] == "nist-k" for row in gaps),
        "p224_potential_direction_rows": 1,
        "exact_zero_vertical_gap_controls": sum(
            row["control_type"] == "exact_zero_vertical_gap" for row in controls
        ),
        "unresolved_controls": sum(row["control_type"] == "unresolved" for row in controls),
        "fully_charged_transfer_rows": 0,
        "weakness_eligible_rows": 0,
    }
    for key, expected in expected_summary.items():
        require_equal(summary[key], expected, f"summary {key}")
    xs = [float(row["gap_log2"]) for row in gaps]
    ys = [math.log2(int(row["absolute_kernel_x_field_degree"])) for row in gaps]
    rho = pearson(rankdata(xs), rankdata(ys))
    require(math.isclose(summary["descriptive_association"]["rho"], rho,
                         rel_tol=0.0, abs_tol=1e-15),
            "descriptive Spearman association")
    require_equal(summary["descriptive_association"]["n_rows"], len(gaps),
                  "descriptive association row count")

    require(all(row["point_map_status"] == "not_certified" for row in gaps),
            "a gap row unexpectedly claims a certified point map")
    require(all(row["dual_status"] == "not_certified" for row in gaps),
            "a gap row unexpectedly claims a certified dual")
    require(all(row["subgroup_certificate_status"] == "not_certified" for row in gaps),
            "a gap row unexpectedly claims a subgroup certificate")
    require(all(row["full_transfer_cost_status"] == "unmeasured" for row in gaps),
            "a gap row unexpectedly claims a full transfer measurement")
    require(not any(row["weakness_eligible"] for row in gaps),
            "a gap row unexpectedly claims weakness eligibility")

    for prime in list(PRIME_CERTIFICATES):
        verify_prime_certificate(prime)
    certificate_nodes = [PRIME_CERTIFICATES[n] for n in sorted(PRIME_CERTIFICATES)]
    certificate_digest = hashlib.sha256(json.dumps(
        certificate_nodes, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()

    return {
        "schema": RECEIPT_SCHEMA,
        "panel_path": str(PANEL_PATH.relative_to(ROOT)),
        "panel_sha256": sha256(PANEL_PATH),
        "verifier_path": str(Path(__file__).resolve().relative_to(ROOT)),
        "verifier_sha256": sha256(Path(__file__).resolve()),
        "factorization_dependency": f"sympy {sympy_version}",
        "status": "pass",
        "checks": [
            {"id": "source_hashes", "status": "pass", "rows": source_count},
            {"id": "recursive_lucas_primality", "status": "pass",
             "top_level_primes": len(top_level_primes),
             "certificate_nodes": len(certificate_nodes),
             "largest_top_level_prime_bits": max(n.bit_length() for n in top_level_primes),
             "certificate_graph_sha256": certificate_digest},
            {"id": "class_cm_arithmetic", "status": "pass", "rows": len(classes)},
            {"id": "minimal_kernel_field_orders", "status": "pass", "rows": len(gaps)},
            {"id": "conductor_levels", "status": "pass", "rows": len(levels)},
            {"id": "conditional_adjacencies", "status": "pass",
             "rows": len(adjacencies)},
            {"id": "zero_gap_and_p224_controls", "status": "pass",
             "rows": len(controls) + 1},
            {"id": "measured_effect_sources", "status": "pass", **effects_receipt},
            {"id": "construction_sources", "status": "pass", **construction_receipt},
            {"id": "source_action_audit", "status": "pass",
             "rows": len(source_action_rows)},
            {"id": "csv_projections", "status": "pass", "files": len(csv_sections)},
            {"id": "claim_gates", "status": "pass",
             "fully_charged_transfer_rows": 0, "weakness_eligible_rows": 0},
        ],
        "class_receipts": class_receipts,
        "gap_receipts": gap_receipts,
        "primality_certificate_nodes": certificate_nodes,
        "limitations": [
            "This receipt verifies exact arithmetic, source transcription, and status gates; it does not construct or evaluate an isogeny.",
            "No row has a certified point map, dual, subgroup-preservation certificate, or fully charged transfer cost.",
            "The Spearman coefficient is descriptive only because rows are clustered within trace/isogeny classes and twist-paired geometry families.",
        ],
    }


def main() -> int:
    try:
        receipt = verify_panel()
        exit_status = 0
    except (VerificationError, KeyError, StopIteration, ValueError) as error:
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "panel_path": str(PANEL_PATH.relative_to(ROOT)),
            "panel_sha256": sha256(PANEL_PATH) if PANEL_PATH.is_file() else None,
            "verifier_path": str(Path(__file__).resolve().relative_to(ROOT)),
            "verifier_sha256": sha256(Path(__file__).resolve()),
            "factorization_dependency": f"sympy {sympy_version}",
            "status": "fail",
            "error": f"{type(error).__name__}: {error}",
        }
        exit_status = 1
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "status": receipt["status"],
        "receipt": str(RECEIPT_PATH.relative_to(ROOT)),
        "checks": len(receipt.get("checks", [])),
        "error": receipt.get("error"),
    }, indent=2))
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
