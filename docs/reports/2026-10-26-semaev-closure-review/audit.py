"""Independent finite-model check of the published Semaev row-space boundary.

Reads the frozen draw from Git, rebuilds S3 by a truth table and Mobius transform,
then checks two row-generation policies and a concrete failure of closure.
Python 3.9+; no external packages or scientific trial inputs are needed.
"""

import hashlib
import json
import subprocess


ARCHIVE = "docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json"
EQUATIONS_SHA256 = "89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb"
WITNESS_TERMS = (1, 2, 4, 8, 9, 10, 12, 16, 18, 20, 32, 40, 48, 64, 65, 128, 144, 192)


def degree(mask):
    return bin(mask).count("1")


def gf16_mul(a, b):
    """Multiply in F2[X]/(X^4 + X + 1), with reduction after convolution."""
    raw = 0
    for bit in range(4):
        if b & (1 << bit):
            raw ^= a << bit
    for bit in (6, 5, 4):
        if raw & (1 << bit):
            raw ^= 0b10011 << (bit - 4)
    return raw


def derive_equations(basis, target):
    values = [[0] * 256 for _ in range(4)]
    for assignment in range(256):
        x1 = x2 = 0
        for j, element in enumerate(basis):
            if assignment & (1 << j):
                x1 ^= element
            if assignment & (1 << (j + 4)):
                x2 ^= element
        e2 = gf16_mul(x1, x2) ^ gf16_mul(x1, target) ^ gf16_mul(x2, target)
        s3 = gf16_mul(e2, e2) ^ gf16_mul(gf16_mul(x1, x2), target) ^ 1
        for component in range(4):
            values[component][assignment] = (s3 >> component) & 1
    equations = []
    for truth_table in values:
        anf = truth_table[:]
        for bit in range(8):
            for mask in range(256):
                if mask & (1 << bit):
                    anf[mask] ^= anf[mask ^ (1 << bit)]
        equations.append([mask for mask, coefficient in enumerate(anf) if coefficient])
    return equations


def packed(terms):
    result = 0
    for term in terms:
        result ^= 1 << term
    return result


def multiply_boolean(poly, monomial):
    result = 0
    while poly:
        bit = poly & -poly
        result ^= 1 << ((bit.bit_length() - 1) | monomial)
        poly ^= bit
    return result


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def rows_for_degree(equations, bound, policy):
    rows = []
    high = packed(m for m in range(256) if degree(m) > bound)
    for equation in equations:
        polynomial = packed(equation)
        source_degree = max(map(degree, equation))
        for multiplier in range(256):
            product = multiply_boolean(polynomial, multiplier)
            if policy == "strict_multiplier_budget":
                include = degree(multiplier) <= bound - source_degree
            elif policy == "product_degree":
                include = product & high == 0
            else:
                raise ValueError(policy)
            if include:
                rows.append(product)
    return rows


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    archive_bytes = subprocess.check_output(["git", "show", "HEAD:" + ARCHIVE])
    archive = json.loads(archive_bytes)
    matches = [row for row in archive["draws"] if
               (row["n"], row["nprime"], row["draw"]) == (4, 4, 1)]
    check(len(matches) == 1, "frozen draw identity is not unique")
    draw = matches[0]
    check((draw["seed"], draw["xR"], draw["basis"]) ==
          (32201, 1, [9, 3, 2, 12]), "frozen draw inputs changed")
    equations = draw["equations"]
    encoded = json.dumps(equations, separators=(",", ":")).encode()
    check(hashlib.sha256(encoded).hexdigest() == EQUATIONS_SHA256 ==
          draw["equations_sha256"], "frozen equation hash changed")
    check(derive_equations(draw["basis"], draw["xR"]) == equations,
          "independent finite-field S3 derivation disagrees")
    curve_y = [y for y in range(16) if
               gf16_mul(y, y) ^ gf16_mul(draw["xR"], y) ==
               gf16_mul(draw["xR"], gf16_mul(draw["xR"], draw["xR"])) ^
               gf16_mul(draw["xR"], draw["xR"]) ^ 1]
    check(curve_y == [6, 7], "target is not the expected curve abscissa")

    profiles = {}
    for policy in ("strict_multiplier_budget", "product_degree"):
        by_degree = {}
        for bound in (1, 2, 3):
            rows = rows_for_degree(equations, bound, policy)
            top = packed(m for m in range(256) if degree(m) == bound)
            by_degree[bound] = {
                "row_count": len(rows), "rank": rank(rows),
                "projected_rank": rank(row & top for row in rows),
            }
        profiles[policy] = by_degree
        check([(by_degree[d]["rank"], by_degree[d]["projected_rank"])
               for d in (1, 2, 3)] == [(1, 1), (11, 10), (53, 41)],
              "published finite ranks do not reproduce under " + policy)

    rows_three = rows_for_degree(equations, 3, "product_degree")
    witness = packed(WITNESS_TERMS)
    check(rank(rows_three + [witness]) == 53,
          "published degree-three witness not in literal row span")
    rows_two = rows_for_degree(equations, 2, "product_degree")
    check(rank(rows_two + [witness]) == 12,
          "published witness is in the degree-two row span")
    check(max(map(degree, WITNESS_TERMS)) == 2,
          "witness no longer has degree two")
    closure_counterexample = multiply_boolean(witness, 1)
    check(rank(rows_three + [closure_counterexample]) == 54,
          "literal degree-three row span is closed under this product")
    check(max(degree(m) for m in range(256) if
              closure_counterexample & (1 << m)) == 3,
          "closure counterexample exceeds degree three")

    result = {
        "schema": "semaev-closure-audit/v1",
        "archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "equations_sha256": EQUATIONS_SHA256,
        "curve_target_y_witnesses": curve_y,
        "profiles": profiles,
        "degree_three_witness_terms": list(WITNESS_TERMS),
        "degree_three_witness_in_literal_span": True,
        "degree_three_witness_outside_degree_two_span": True,
        "closure_multiplier": 1,
        "closure_product_terms": [m for m in range(256) if
                                  closure_counterexample & (1 << m)],
        "literal_degree_three_rank": 53,
        "rank_after_adjoining_closure_product": 54,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
