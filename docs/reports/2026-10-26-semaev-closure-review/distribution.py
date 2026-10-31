"""Audit all 80 archived Semaev draws in a degree-bounded Boolean quotient.

This reconstructs equations independently from the field S3 polynomial,
replays archived selected-row profiles, and computes a distinct quotient
closure. It does not identify either space with polynomial-ring V_{F,D}.
"""

from collections import Counter
import hashlib
import json
import subprocess

import audit
import closure as finite


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def gf_mul(left, right, modulus, degree):
    raw = 0
    for bit in range(degree):
        if right & (1 << bit):
            raw ^= left << bit
    for bit in range(2 * degree - 2, degree - 1, -1):
        if raw & (1 << bit):
            raw ^= modulus << (bit - degree)
    return raw


def check_field_modulus(modulus, degree):
    require(modulus >> degree == 1 and modulus & 1,
            "field modulus degree or constant term changed")
    require(all(gf_mul(left, right, modulus, degree) != 0
                for left in range(1, 1 << degree)
                for right in range(1, 1 << degree)),
            "field modulus admits zero divisors")


def derive_equations(draw, modulus):
    n = draw["n"]
    nprime = draw["nprime"]
    nvars = 2 * nprime
    multiply = lambda a, b: gf_mul(a, b, modulus, n)
    values = [[0] * (1 << nvars) for _ in range(n)]
    for assignment in range(1 << nvars):
        x1 = x2 = 0
        for j, element in enumerate(draw["basis"]):
            if assignment & (1 << j):
                x1 ^= element
            if assignment & (1 << (j + nprime)):
                x2 ^= element
        target = draw["xR"]
        e2 = multiply(x1, x2) ^ multiply(x1, target) ^ multiply(x2, target)
        s3 = multiply(e2, e2) ^ multiply(multiply(x1, x2), target) ^ 1
        for bit in range(n):
            values[bit][assignment] = (s3 >> bit) & 1
    equations = []
    for truth_table in values:
        coefficients = truth_table[:]
        for bit in range(nvars):
            for mask in range(1 << nvars):
                if mask & (1 << bit):
                    coefficients[mask] ^= coefficients[mask ^ (1 << bit)]
        equations.append([mask for mask, coefficient in enumerate(coefficients)
                          if coefficient])
    return equations


def direct_rows(equations, bound, nvars):
    rows = []
    for equation in equations:
        polynomial = audit.packed(equation)
        for multiplier in range(1 << nvars):
            product = audit.multiply_boolean(polynomial, multiplier)
            if finite.row_degree(product) <= bound:
                rows.append(product)
    return rows


def profile(rows, bound, nvars):
    full_rank = audit.rank(rows)
    top = audit.packed(mask for mask in range(1 << nvars)
                       if audit.degree(mask) == bound)
    projected_rank = audit.rank(row & top for row in rows)
    return {"rank": full_rank, "projected_rank": projected_rank,
            "lowdim": full_rank - projected_rank}


def audit_draw(draw, modulus):
    identity = (draw["n"], draw["nprime"], draw["draw"])
    label = str(identity)
    nvars = 2 * draw["nprime"]
    require(len(draw["basis"]) == draw["nprime"],
            label + " basis length changed")
    subset_sums = []
    for mask in range(1 << draw["nprime"]):
        subset_sums.append(0 if mask == 0 else
                           subset_sums[mask & (mask - 1)] ^
                           draw["basis"][(mask & -mask).bit_length() - 1])
    require(len(set(subset_sums)) == 1 << draw["nprime"],
            label + " basis is not linearly independent")
    require(0 <= draw["xR"] < (1 << draw["n"]),
            label + " target abscissa outside field")
    multiply = lambda a, b: gf_mul(a, b, modulus, draw["n"])
    target = draw["xR"]
    right = multiply(multiply(target, target), target) ^ \
            multiply(target, target) ^ 1
    require(any(multiply(y, y) ^ multiply(target, y) == right
                for y in range(1 << draw["n"])),
            label + " target abscissa has no curve point")
    equations = draw["equations"]
    require(len(equations) == draw["n"] == draw["equation_count"],
            label + " equation count changed")
    encoded = json.dumps(equations, separators=(",", ":")).encode()
    require(hashlib.sha256(encoded).hexdigest() == draw["equations_sha256"],
            label + " equation hash changed")
    require(all(0 <= mask < (1 << nvars) for eq in equations for mask in eq),
            label + " equation mask is outside ring")
    require(derive_equations(draw, modulus) == equations,
            label + " independent S3 derivation disagrees")

    selected = {}
    closed = {}
    spaces = {}
    previous_direct = previous_closed = 0
    for bound in (1, 2, 3):
        rows = direct_rows(equations, bound, nvars)
        direct = profile(rows, bound, nvars)
        direct["row_count"] = len(rows)
        direct["new_falls"] = direct["lowdim"] - previous_direct
        archived = draw["boolean_parity_profile"][str(bound)]
        require((direct["rank"], direct["lowdim"], direct["row_count"],
                 direct["new_falls"]) ==
                (archived["rank"], archived["lowdim"],
                 archived["compatible_rows"], archived["new_falls"]),
                label + " archived selected-row profile changed at D=" +
                str(bound))

        variable, a = finite.closure(equations, bound, "variables", nvars)
        all_products, b = finite.closure(equations, bound, "all_monomials", nvars)
        kernel, c = finite.projection_kernel_closure(equations, bound, nvars)
        require((a["rank"], a["projected_rank"]) ==
                (b["rank"], b["projected_rank"]) ==
                (c["rank"], c["projected_rank"]) and
                audit.rank(variable.rows() + all_products.rows() +
                           kernel.rows()) == a["rank"],
                label + " quotient closure methods disagree at D=" +
                str(bound))
        if bound > 1:
            require(audit.rank(variable.rows() + spaces[bound - 1].rows()) ==
                    a["rank"], label + " quotient filtration is not nested")
        closed_entry = {"rank": a["rank"],
                        "projected_rank": a["projected_rank"],
                        "lowdim": a["low_degree_dimension"],
                        "new_falls": a["low_degree_dimension"] - previous_closed,
                        "direct_outside_closed_dimension":
                        audit.rank(variable.rows() + rows) - a["rank"]}
        require(closed_entry["new_falls"] >= 0,
                label + " negative closed new-fall dimension")
        selected[str(bound)] = direct
        closed[str(bound)] = closed_entry
        spaces[bound] = variable
        previous_direct = direct["rank"]
        previous_closed = a["rank"]

    return {"n": identity[0], "nprime": identity[1], "draw": identity[2],
            "seed": draw["seed"], "xR": draw["xR"],
            "equations_sha256": draw["equations_sha256"],
            "selected": selected, "closed": closed}


def first_positive(profiles):
    return next((bound for bound in (2, 3)
                 if profiles[str(bound)]["new_falls"] > 0), ">3")


def main():
    raw = subprocess.check_output(["git", "show", "HEAD:" + audit.ARCHIVE])
    archive = json.loads(raw)
    draws = archive["draws"]
    require(len(draws) == 80, "archived Semaev draw count changed")
    moduli = {int(n): value for n, value in
              archive["curve_model"]["field_moduli"].items()}
    require(set(moduli) == {4, 5, 6, 7}, "archive field set changed")
    for degree, modulus in moduli.items():
        check_field_modulus(modulus, degree)
    results = [audit_draw(draw, moduli[draw["n"]]) for draw in draws]
    keys = [(row["n"], row["nprime"], row["draw"]) for row in results]
    require(len(set(keys)) == 80, "duplicate draw identity")
    selected_grades = Counter(first_positive(row["selected"]) for row in results)
    closed_grades = Counter(first_positive(row["closed"]) for row in results)
    transitions = Counter((first_positive(row["selected"]),
                           first_positive(row["closed"])) for row in results)
    return {"schema": "semaev-boolean-closure-distribution/v1",
            "archive_sha256": hashlib.sha256(raw).hexdigest(),
            "ring": "F2[u0..u(2*nprime-1)]/(ui^2-ui), squarefree monomial degree",
            "scope": "80 archived Semaev draws; Boolean quotient only; no polynomial-ring transfer",
            "methods": ["degree-filtered variable fixed point",
                        "degree-filtered all-monomial fixed point",
                        "numeric-pivot projection-kernel fixed point"],
            "selected_first_positive": dict(sorted(selected_grades.items(),
                                                   key=lambda x: str(x[0]))),
            "closed_first_positive": dict(sorted(closed_grades.items(),
                                                 key=lambda x: str(x[0]))),
            "transitions": [
                {"selected": a, "closed": b, "count": count}
                for (a, b), count in sorted(transitions.items(),
                                            key=lambda x: str(x[0]))],
            "draws": results}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
