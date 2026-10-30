"""Independent exact checker/reference for the coefficient-SAT follow-up.

This module never imports coefficients.py. No experiment runs at import time.
The reference walks coefficients and point tuples; neither is exposed to a
candidate learner before candidate search has finished.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


class Arithmetic:
    """Ordinary univariate F_p arithmetic, with primitive polynomial counters."""
    def __init__(self, p, counts=None):
        self.p = p
        self.counts = counts if counts is not None else Counter()

    def clean(self, a):
        a = [int(x) % self.p for x in a]
        while len(a) > 1 and a[-1] == 0:
            a.pop()
        return a or [0]

    def plus(self, a, b):
        n = max(len(a), len(b))
        self.counts["polynomial_coefficient_additions"] += n
        return self.clean([(a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0) for i in range(n)])

    def times(self, a, b):
        result = [0]*(len(a)+len(b)-1)
        self.counts["polynomial_coefficient_multiplications"] += len(a)*len(b)
        self.counts["polynomial_coefficient_additions"] += len(a)*len(b)
        for i, aa in enumerate(a):
            for j, bb in enumerate(b):
                result[i+j] = (result[i+j]+aa*bb) % self.p
        return self.clean(result)

    def negative(self, a):
        self.counts["polynomial_coefficient_negations"] += len(a)
        return self.clean([-x for x in a])

    def division(self, a, b):
        a, b = self.clean(a), self.clean(b)
        if b == [0]:
            raise ZeroDivisionError("zero polynomial divisor")
        q = [0]*max(1, len(a)-len(b)+1)
        self.counts["field_inverse_calls"] += 1
        inverse = pow(b[-1], -1, self.p)
        while len(a) >= len(b) and a != [0]:
            shift = len(a)-len(b)
            scale = a[-1]*inverse % self.p
            self.counts["polynomial_coefficient_multiplications"] += 1+len(b)
            self.counts["polynomial_coefficient_additions"] += len(b)
            q[shift] = scale
            for j, value in enumerate(b):
                a[j+shift] = (a[j+shift]-scale*value) % self.p
            a = self.clean(a)
        return self.clean(q), a

    def evaluate(self, a, x):
        ans = 0
        for c in reversed(a):
            ans = (ans*x+c) % self.p
        self.counts["polynomial_coefficient_multiplications"] += len(a)
        self.counts["polynomial_coefficient_additions"] += len(a)
        return ans


def scalar_residuals(inp, values, counts=None):
    """Independent straight polynomial reference, not a symbolic specialization."""
    counts = counts if counts is not None else Counter()
    ar = Arithmetic(inp["p"], counts)
    p, a, b, d, c = (inp[k] for k in ("p", "a", "b", "d", "c"))
    r, s = inp["target"]
    a2, a1, b1, b0 = values
    counts["norm_scalar_formula_evaluations"] += 1
    a0 = (s*(b1*r+b0)-r**3-a2*r*r-a1*r) % p
    A, B = [a0, a1, a2, 1], ar.clean([b0, b1])
    f = [b, a, 0, 1]
    norm = ar.plus(ar.times(A, A), ar.negative(ar.times(ar.times(B, B), f)))
    U, remainder = ar.division(norm, [-r, 1])
    if remainder != [0] or len(U) != 6 or U[-1] != 1:
        raise AssertionError("reference norm divisibility failed")
    power = [0, 1]
    for _ in range(d.bit_length()-1):
        power = ar.division(ar.times(power, power), U)[1]
    residuals = ar.plus(power, [-c])
    return residuals+[0]*(5-len(residuals)), A, B, U


def pack(values, p):
    out = 0
    for v in values:
        out = out*p+v
    return out


def unpack(value, p):
    if not isinstance(value, int) or not 0 <= value < p**4:
        raise ValueError("noncanonical coefficient assignment")
    ans = []
    for _ in range(4):
        value, digit = divmod(value, p)
        ans.append(digit)
    return list(reversed(ans))


def enumerate_coefficients(inp, retain_residuals=False):
    counts, models = Counter(), []
    residual_table = [] if retain_residuals else None
    for values in itertools.product(range(inp["p"]), repeat=4):
        counts["coefficient_assignments"] += 1
        residuals, _, _, _ = scalar_residuals(inp, values, counts)
        if retain_residuals:
            residual_table.append(residuals)
        if not any(residuals):
            models.append(list(values))
    result = {"models": models, "costs": dict(counts)}
    if retain_residuals:
        result["residual_table"] = residual_table
    return result


def add_points(P, Q, p, a, counts):
    counts["affine_group_addition_calls"] += 1
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    z, w = Q
    if x == z and (y+w) % p == 0:
        return None
    counts["field_inverse_calls"] += 1
    slope = ((3*x*x+a)*pow(2*y, -1, p) if x == z else (w-y)*pow(z-x, -1, p)) % p
    xx = (slope*slope-x-z) % p
    return (xx, (slope*(x-xx)-y) % p)


def point_inventory(p, a, b, d, c, counts=None):
    counts = counts if counts is not None else Counter()
    by_x = {}
    for x in range(p):
        counts["membership_pow_calls"] += 1
        if pow(x, d, p) != c:
            continue
        for y in range(p):
            counts["curve_membership_evaluations"] += 1
            if (y*y-x**3-a*x-b) % p == 0:
                by_x.setdefault(x, []).append((x, y))
    return by_x


def enumerate_relations(inp, exceptional_only=False):
    counts = Counter()
    p, a, b, d, c = (inp[k] for k in ("p", "a", "b", "d", "c"))
    R = tuple(inp["target"])
    by_x = point_inventory(p, a, b, d, c, counts)
    relations = []
    for xs in itertools.combinations(sorted(by_x), 5):
        counts["coordinate_subsets_considered"] += 1
        if exceptional_only and R[0] not in xs:
            counts["generic_subsets_skipped"] += 1
            continue
        for points in itertools.product(*(by_x[x] for x in xs)):
            counts["signed_point_tuples_enumerated"] += 1
            total = None
            for P in points:
                total = add_points(total, P, p, a, counts)
            if total == R:
                relations.append([list(P) for P in points])
    return {"relations": sorted(relations), "costs": dict(counts),
            "base_x": sorted(by_x), "scope": "five_affine_points_with_distinct_x"}


def certificate_check(p, proof):
    counts = Counter()
    ar = Arithmetic(p, counts)
    gens = [proof["field_polynomial"]]+proof["residuals"]
    multipliers = proof["multipliers"]
    if len(gens) != len(multipliers):
        return False, dict(counts)
    field = [0]*(p+1)
    field[1], field[p] = -1 % p, 1
    if gens[0] != field or len(proof["residuals"]) != 5:
        return False, dict(counts)
    total = [0]
    for f, multiplier in zip(gens, multipliers):
        total = ar.plus(total, ar.times(f, multiplier))
    gcd = proof["gcd"]
    valid = ar.clean(total) == gcd and gcd != [0] and gcd[-1] == 1
    for f in gens:
        valid = valid and ar.division(f, gcd)[1] == [0]
    return bool(valid), dict(counts)


def expected_cells(config):
    if config["primes"] != [17] or config["degrees"] != [8, 16]:
        raise ValueError("fixed p17 d8/d16 inventory required")
    p, a, b = 17, 2, 2
    points = [(x, y) for x in range(p) for y in range(1, p)
              if (y*y-x**3-a*x-b) % p == 0]
    reps = []
    for x, y in points:
        if not reps or reps[-1][0] != x:
            reps.append([x, y])
    return [{"p": p, "a": a, "b": b, "d": d, "c": 1, "target": R}
            for d in config["degrees"] for R in reps[:3]]


def cell_id(inp):
    return "coeff-p%d-d%d-r%d-y%d" % (inp["p"], inp["d"], *inp["target"])


def verify(payload):
    """Complete independent census and every certificate; no producer import."""
    payload = json.loads(json.dumps(payload))
    config = payload["config"]
    wanted = expected_cells(config)
    counts, failures = Counter(), []
    cells = payload.get("cells", [])
    if [c.get("id") for c in cells] != [cell_id(i) for i in wanted]:
        return {"valid": False, "counts": {}, "failures": ["cell_inventory"]}
    def require(ok, label):
        if not ok and len(failures) < 50:
            failures.append(label)
    for cell, inp in zip(cells, wanted):
        counts["cells"] += 1
        require(cell["input"] == inp, [cell["id"], "input_identity"])
        p = inp["p"]
        reference = enumerate_coefficients(inp, retain_residuals=True)
        point_reference = enumerate_relations(inp)
        counts.update({"oracle_"+k: v for k, v in reference["costs"].items()})
        counts.update({"point_oracle_"+k: v for k, v in point_reference["costs"].items()})
        require(cell["reference"]["coefficient_models"] == reference["models"], [cell["id"], "producer_coefficient_reference"])
        require(cell["reference"]["relations"] == point_reference["relations"], [cell["id"], "producer_point_reference"])
        proofs = cell["proofs"]
        verified_proofs = {}
        for key, proof in proofs.items():
            counts["prefix_certificates"] += 1
            require(hashlib.sha256(canonical(proof).encode()).hexdigest() == key, [cell["id"], "proof_hash"])
            ok, work = certificate_check(p, proof)
            counts.update({"proof_"+k: v for k, v in work.items()})
            require(ok, [cell["id"], "bezout", key])
            require(len(proof["prefix"]) == 3 and all(type(v) is int and 0 <= v < p for v in proof["prefix"]),
                    [cell["id"], "canonical_prefix", key])
            # Independently establish the exact specialization at every field
            # value. This is checker work, never candidate construction.
            ar = Arithmetic(p)
            roots = []
            for t in range(p):
                residuals = reference["residual_table"][pack(proof["prefix"]+[t], p)]
                counts["independent_residual_cache_lookups"] += 1
                require([ar.evaluate(f, t) for f in proof["residuals"]] == residuals,
                        [cell["id"], "residual_specialization", key, t])
                if not any(residuals):
                    roots.append(t)
            require([t for t in range(p) if ar.evaluate(proof["gcd"], t) == 0] == roots,
                    [cell["id"], "gcd_root_set", key])
            counts.update({"specialization_"+k: v for k, v in ar.counts.items()})
            verified_proofs[key] = roots
        require(set(cell["arms"]) == set(config["arms"]), [cell["id"], "arm_inventory"])
        expected_model_keys = {tuple(v) for v in reference["models"]}
        expected_relation_keys = {canonical(v) for v in point_reference["relations"]}
        for arm_name, arm in cell["arms"].items():
            counts["arms"] += 1
            complete = arm["status"] == "complete"
            require(arm["status"] in ("complete", "censored"), [cell["id"], arm_name, "completion_status"])
            model_keys = {tuple(v) for v in arm["coefficient_models"]}
            require(len(model_keys) == len(arm["coefficient_models"]), [cell["id"], arm_name, "duplicate_model"])
            require((arm["coefficient_models"] == reference["models"] if complete else model_keys <= expected_model_keys),
                    [cell["id"], arm_name, "coefficient_models"])
            relation_keys = {canonical(v) for v in arm["complete_relations"]}
            require((arm["complete_relations"] == point_reference["relations"] if complete else relation_keys <= expected_relation_keys),
                    [cell["id"], arm_name, "complete_or_censored_relations"])
            generic = {canonical(v) for v in arm["generic_relations"]}
            fallback = {canonical(v) for v in arm["fallback"]["relations"]}
            require(generic.isdisjoint(fallback) and generic | fallback == relation_keys and
                    (generic | fallback == expected_relation_keys if complete else generic | fallback <= expected_relation_keys),
                    [cell["id"], arm_name, "chart_partition"])
            require(all(inp["target"][0] not in [P[0] for P in v] for v in arm["generic_relations"]),
                    [cell["id"], arm_name, "generic_chart"])
            require(all(inp["target"][0] in [P[0] for P in v] for v in arm["fallback"]["relations"]),
                    [cell["id"], arm_name, "exceptional_chart"])
            if arm_name == "leaf_sat":
                covered = {pack(v, p) for v in arm["coefficient_models"]}
                for code, index, value in arm["search"]["learned_leaf"]:
                    counts["leaf_certificates"] += 1
                    vals = unpack(code, p)
                    rs = reference["residual_table"][code]
                    counts["independent_residual_cache_lookups"] += 1
                    require(code not in covered and 0 <= index < 5 and value == rs[index] and value != 0,
                            [cell["id"], "leaf_conflict", code])
                    covered.add(code)
                require((len(covered) == p**4 if complete else len(covered) <= p**4), [cell["id"], "leaf_coverage"])
            elif arm_name in ("prefix_univariate_gcd", "aa_reverse_prefix"):
                seen = set()
                intended_order = list(itertools.product(range(p), repeat=3))
                if arm_name == "aa_reverse_prefix":
                    intended_order.reverse()
                observed_order = [tuple(branch["prefix"]) for branch in arm["search"]["prefix_records"]]
                require(observed_order == intended_order[:len(observed_order)],
                        [cell["id"], arm_name, "declared_prefix_order"])
                for branch in arm["search"]["prefix_records"]:
                    prefix = tuple(branch["prefix"])
                    require(prefix not in seen, [cell["id"], arm_name, "duplicate_prefix"])
                    seen.add(prefix)
                    proof = proofs[branch["proof_id"]]
                    roots = verified_proofs[branch["proof_id"]]
                    require(proof["prefix"] == branch["prefix"] and roots == branch["roots"],
                            [cell["id"], arm_name, "prefix_proof_binding"])
                    require(branch["forbidden_values"] == [t for t in range(p) if t not in roots],
                            [cell["id"], arm_name, "guarded_nonroot_clauses"])
                require((seen == set(itertools.product(range(p), repeat=3)) if complete else
                         seen <= set(itertools.product(range(p), repeat=3))),
                        [cell["id"], arm_name, "prefix_complete_coverage"])
        require(all(bool(v) for v in cell["checks"].values()), [cell["id"], "producer_invariant"])
    control_names = {"positive_bezout_identity", "corrupted_bezout_rejected",
                     "negative_repeated_root_quotient_rejected", "finite_field_polynomial_reduces_to_zero"}
    require(set(payload.get("controls", {})) == control_names and
            all(value is True for value in payload["controls"].values()), "controls")
    # Reconstruct synthetic checks here rather than trusting the producer's
    # booleans. These are polynomial integrity fixtures, not elliptic trials.
    field = [0, 6, 0, 0, 0, 0, 0, 1]
    control_proof = {"prefix": [0, 0, 0], "field_polynomial": field,
                     "residuals": [[0, 1], [6, 1], [0], [0], [0]],
                     "gcd": [1], "multipliers": [[0], [1], [6], [0], [0], [0]]}
    positive, work = certificate_check(7, control_proof)
    counts.update({"control_"+k: v for k, v in work.items()})
    control_proof["multipliers"][1] = [2]
    corrupt, work = certificate_check(7, control_proof)
    counts.update({"control_"+k: v for k, v in work.items()})
    ar = Arithmetic(7)
    expected_controls = {
        "positive_bezout_identity": positive,
        "corrupted_bezout_rejected": not corrupt,
        "negative_repeated_root_quotient_rejected": ar.division([6, 0, 1], [1, 5, 1])[1] != [0],
        "finite_field_polynomial_reduces_to_zero": all(ar.evaluate(field, t) == 0 for t in range(7))}
    counts.update({"control_"+k: v for k, v in ar.counts.items()})
    require(payload.get("controls", {}) == expected_controls and all(expected_controls.values()),
            "independent_synthetic_control_checks")
    return {"valid": not failures, "counts": dict(counts), "failures": failures,
            "scope": "complete_finite_model_and_certificate_check_no_performance_claim"}
