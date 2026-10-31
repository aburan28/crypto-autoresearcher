"""Replay 200 frozen matched-null systems under Boolean quotient closure.

These are archived controls, not new random draws or cryptographic benchmarks.
The precise quotient rule is the one implemented in closure.py.
"""

from collections import Counter
import hashlib
import json
import subprocess

import audit
import closure as finite
from distribution import direct_rows, profile, require


def support_signature(equations):
    return [sorted(audit.degree(mask) for mask in equation)
            for equation in equations]


def first_positive(profiles):
    return next((bound for bound in range(1, 7)
                 if profiles[str(bound)]["new_falls"] > 0), ">6")


def audit_null(draw, source):
    identity = (draw["n"], draw["nprime"], draw["draw"])
    label = str(identity)
    nvars = 2 * draw["nprime"]
    equations = draw["equations"]
    require(len(equations) == draw["n"] and
            all(0 <= mask < 1 << nvars for eq in equations for mask in eq),
            label + " null equation shape changed")
    encoded = json.dumps(equations, separators=(",", ":")).encode()
    require(hashlib.sha256(encoded).hexdigest() == draw["equations_sha256"],
            label + " null equation hash changed")
    require(draw["support_profile_matches"] is True and
            support_signature(equations) == support_signature(source["equations"]),
            label + " matched-null support profile changed")
    selected = {}
    closed = {}
    spaces = {}
    previous_direct = previous_closed = 0
    for bound in range(1, 7):
        rows = direct_rows(equations, bound, nvars)
        direct = profile(rows, bound, nvars)
        direct["row_count"] = len(rows)
        direct["new_falls"] = direct["lowdim"] - previous_direct
        archived = draw["boolean_parity_profile"][str(bound)]
        require((direct["rank"], direct["lowdim"], direct["row_count"],
                 direct["new_falls"]) ==
                (archived["rank"], archived["lowdim"],
                 archived["compatible_rows"], archived["new_falls"]),
                label + " archived null profile changed at D=" + str(bound))

        variables, a = finite.closure(equations, bound, "variables", nvars)
        monomials, b = finite.closure(equations, bound, "all_monomials", nvars)
        kernel, c = finite.projection_kernel_closure(equations, bound, nvars)
        require((a["rank"], a["projected_rank"]) ==
                (b["rank"], b["projected_rank"]) ==
                (c["rank"], c["projected_rank"]) and
                audit.rank(variables.rows() + monomials.rows() +
                           kernel.rows()) == a["rank"],
                label + " null closure methods disagree at D=" + str(bound))
        if bound > 1:
            require(audit.rank(variables.rows() + spaces[bound - 1].rows()) ==
                    a["rank"], label + " null closure is not nested")
        entry = {"rank": a["rank"],
                 "projected_rank": a["projected_rank"],
                 "lowdim": a["low_degree_dimension"],
                 "new_falls": a["low_degree_dimension"] - previous_closed,
                 "direct_outside_closed_dimension":
                 audit.rank(variables.rows() + rows) - a["rank"]}
        require(entry["new_falls"] >= 0,
                label + " negative null quotient new-class count")
        selected[str(bound)] = direct
        closed[str(bound)] = entry
        spaces[bound] = variables
        previous_direct = direct["rank"]
        previous_closed = a["rank"]
    require(first_positive(selected) == draw["boolean_parity_first_fall"],
            label + " archived null first positive degree changed")
    return {"n": identity[0], "nprime": identity[1], "draw": identity[2],
            "seed": draw["seed"], "source_semaev_draw":
            draw["source_semaev_draw"],
            "equations_sha256": draw["equations_sha256"],
            "selected": selected, "closed": closed}


def main():
    raw = subprocess.check_output(["git", "show", "HEAD:" + audit.ARCHIVE])
    archive = json.loads(raw)
    nulls = archive["null_draws"]
    require(len(nulls) == 200, "archived matched-null count changed")
    sources = {(row["n"], row["nprime"], row["draw"]): row
               for row in archive["draws"]}
    require(len(sources) == 80, "archived Semaev source set changed")
    results = []
    for draw in nulls:
        key = (draw["n"], draw["nprime"], draw["source_semaev_draw"])
        require(key in sources, "matched-null source draw missing")
        results.append(audit_null(draw, sources[key]))
    identities = [(row["n"], row["nprime"], row["draw"])
                  for row in results]
    require(len(set(identities)) == 200, "duplicate null draw identity")
    selected_grades = Counter(first_positive(row["selected"])
                              for row in results)
    closed_grades = Counter(first_positive(row["closed"])
                            for row in results)
    transitions = Counter((first_positive(row["selected"]),
                           first_positive(row["closed"])) for row in results)
    changed_ranks = {str(d): sum(row["selected"][str(d)]["rank"] !=
                                 row["closed"][str(d)]["rank"]
                                 for row in results) for d in range(1, 7)}
    changed_new_counts = {str(d): sum(
        row["selected"][str(d)]["new_falls"] !=
        row["closed"][str(d)]["new_falls"] for row in results)
        for d in range(1, 7)}
    outside = {str(d): sum(
        row["closed"][str(d)]["direct_outside_closed_dimension"] > 0
        for row in results) for d in range(1, 7)}
    return {"schema": "semaev-matched-null-boolean-closure/v1",
            "archive_sha256": hashlib.sha256(raw).hexdigest(),
            "ring": "F2[u0..u(2*nprime-1)]/(ui^2-ui), squarefree monomial degree",
            "scope": "200 archived matched nulls; no new sampling or polynomial-ring transfer",
            "methods": ["degree-filtered variable fixed point",
                        "degree-filtered all-monomial fixed point",
                        "numeric-pivot projection-kernel fixed point"],
            "selected_first_positive": dict(selected_grades),
            "closed_first_positive": dict(closed_grades),
            "transitions": [{"selected": a, "closed": b, "count": count}
                            for (a, b), count in sorted(transitions.items())],
            "changed_ranks": changed_ranks,
            "changed_new_counts": changed_new_counts,
            "selected_outside_closure": outside,
            "draws": results}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
