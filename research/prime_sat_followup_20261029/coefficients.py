"""Shared-norm coefficient search with certified finite-field SAT conflicts.

The only scientific interface is run(config, checkpoint=None). Inputs are fixed
public finite cells. Symbolic prefixes are constructed algebraically, never by
interpolating a truth table or consulting the reference model set.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

from pysat.solvers import Minisat22
import check_coefficients as independent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class PolynomialRing:
    """Dense F_p[t], optionally reduced by t^p-t after multiplication."""
    def __init__(self, p, counts=None, finite=False):
        self.p = p
        self.counts = counts if counts is not None else Counter()
        self.finite = finite

    def clean(self, a):
        a = [int(v) % self.p for v in a]
        while len(a) > 1 and a[-1] == 0:
            a.pop()
        return a or [0]

    def reduce(self, a):
        if not self.finite or len(a) <= self.p:
            return self.clean(a)
        out = list(a[:self.p])
        for k in range(self.p, len(a)):
            j = 1+(k-1) % (self.p-1)
            out[j] = (out[j]+a[k]) % self.p
            self.counts["polynomial_coefficient_additions"] += 1
            self.counts["finite_field_reduction_terms"] += 1
        return self.clean(out)

    def add(self, a, b):
        n = max(len(a), len(b))
        self.counts["polynomial_coefficient_additions"] += n
        return self.clean([(a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0) for i in range(n)])

    def neg(self, a):
        self.counts["polynomial_coefficient_negations"] += len(a)
        return self.clean([-v for v in a])

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def scale(self, a, v):
        self.counts["polynomial_coefficient_multiplications"] += len(a)
        return self.clean([v*x for x in a])

    def mul(self, a, b):
        result = [0]*(len(a)+len(b)-1)
        aa = [(i, c) for i, c in enumerate(a) if c]
        bb = [(i, c) for i, c in enumerate(b) if c]
        pairs = len(aa)*len(bb)
        self.counts["polynomial_coefficient_multiplications"] += pairs
        self.counts["polynomial_coefficient_additions"] += pairs
        for i, x in aa:
            for j, y in bb:
                result[i+j] = (result[i+j]+x*y) % self.p
        return self.reduce(result)

    def div(self, a, b):
        if self.finite:
            raise ValueError("Euclidean division needs ordinary polynomial ring")
        r, b = self.clean(a), self.clean(b)
        if b == [0]:
            raise ZeroDivisionError("zero polynomial")
        self.counts["field_inverse_calls"] += 1
        inv = pow(b[-1], -1, self.p)
        q = [0]*max(1, len(r)-len(b)+1)
        while r != [0] and len(r) >= len(b):
            j = len(r)-len(b)
            scale = r[-1]*inv % self.p
            self.counts["polynomial_coefficient_multiplications"] += 1+len(b)
            self.counts["polynomial_coefficient_additions"] += len(b)
            q[j] = scale
            for i, c in enumerate(b):
                r[i+j] = (r[i+j]-scale*c) % self.p
            r = self.clean(r)
        return self.clean(q), r

    def evaluate(self, a, t):
        value = 0
        for c in reversed(a):
            value = (value*t+c) % self.p
        self.counts["polynomial_coefficient_multiplications"] += len(a)
        self.counts["polynomial_coefficient_additions"] += len(a)
        return value


def xmul(a, b, ring):
    out = [[0] for _ in range(len(a)+len(b)-1)]
    for i, aa in enumerate(a):
        for j, bb in enumerate(b):
            out[i+j] = ring.add(out[i+j], ring.mul(aa, bb))
    return out


def xreduce(poly, U, ring):
    out = [f[:] for f in poly]
    for i in range(len(out)-1, 4, -1):
        leading = out[i]
        if leading != [0]:
            for j in range(5):
                out[i-5+j] = ring.sub(out[i-5+j], ring.mul(leading, U[j]))
        out[i] = [0]
    return out[:5]+[[0]]*max(0, 5-len(out))


def norm_data(inp, prefix, t, ring):
    """A,B,U as polynomials in X with coefficients in the supplied t ring."""
    p, a, b = (inp[k] for k in ("p", "a", "b"))
    r, s = inp["target"]
    a2, a1, b1 = prefix
    ring.counts["norm_scalar_formula_evaluations"] += 1
    constant = (s*b1*r-r**3-a2*r*r-a1*r) % p
    A = [ring.add(ring.scale(t, s), [constant]), [a1], [a2], [1]]
    B = [t, [b1]]
    aa = xmul(A, A, ring)
    bb = xmul(xmul(B, B, ring), [[b], [a], [0], [1]], ring)
    norm = [ring.sub(aa[i] if i < len(aa) else [0], bb[i] if i < len(bb) else [0])
            for i in range(max(len(aa), len(bb)))]
    U = [[0] for _ in range(6)]
    U[5] = norm[6]
    for i in range(5, 0, -1):
        U[i-1] = ring.add(norm[i], ring.scale(U[i], r))
    remainder = ring.add(norm[0], ring.scale(U[0], r))
    if remainder != [0] or U[5] != [1]:
        raise AssertionError("symbolic norm target constraint failed")
    return A, B, U


def symbolic_residuals(inp, prefix, counts):
    ring = PolynomialRing(inp["p"], counts, finite=True)
    _, _, U = norm_data(inp, prefix, [0, 1], ring)
    R = [[0], [1], [0], [0], [0]]
    for _ in range(inp["d"].bit_length()-1):
        R = xreduce(xmul(R, R, ring), U, ring)
        counts["membership_squaring_layers"] += 1
    R[0] = ring.sub(R[0], [inp["c"]])
    return R


def scalar_residuals(inp, values, counts):
    ring = PolynomialRing(inp["p"], counts)
    A, B, U = norm_data(inp, values[:3], [values[3]], ring)
    R = [[0], [1], [0], [0], [0]]
    for _ in range(inp["d"].bit_length()-1):
        R = xreduce(xmul(R, R, ring), U, ring)
        counts["membership_squaring_layers"] += 1
    R[0] = ring.sub(R[0], [inp["c"]])
    return [f[0] for f in R], [f[0] for f in A], [f[0] for f in B], [f[0] for f in U]


def egcd(a, b, ring):
    r0, r1 = a, b
    u0, u1, v0, v1 = [1], [0], [0], [1]
    while r1 != [0]:
        q, r2 = ring.div(r0, r1)
        r0, r1 = r1, r2
        u0, u1 = u1, ring.sub(u0, ring.mul(q, u1))
        v0, v1 = v1, ring.sub(v0, ring.mul(q, v1))
    if r0 == [0]:
        return [0], u0, v0
    ring.counts["field_inverse_calls"] += 1
    inv = pow(r0[-1], -1, ring.p)
    return ring.scale(r0, inv), ring.scale(u0, inv), ring.scale(v0, inv)


def prefix_proof(inp, prefix, construction, search):
    residuals = symbolic_residuals(inp, prefix, construction)
    p = inp["p"]
    field = [0]*(p+1)
    field[1], field[p] = p-1, 1
    ring = PolynomialRing(p, search)
    gcd = field
    multipliers = [[1]]+[[0] for _ in residuals]
    for index, residual in enumerate(residuals, 1):
        if residual == [0]:
            continue
        gcd, u, v = egcd(gcd, residual, ring)
        multipliers = [ring.mul(u, m) for m in multipliers]
        multipliers[index] = ring.add(multipliers[index], v)
        search["gcd_refinement_steps"] += 1
        if gcd == [1]:
            break
    return {"prefix": list(prefix), "field_polynomial": field, "residuals": residuals,
            "gcd": gcd, "multipliers": multipliers}


def value_literals(values, p):
    width = p.bit_length()
    return [((j*width+i+1) if value >> i & 1 else -(j*width+i+1))
            for j, value in enumerate(values) for i in range(width)]


def block(values, p):
    return [-v for v in value_literals(values, p)]


def domain_clauses(p):
    width = p.bit_length()
    clauses = []
    for j in range(4):
        for value in range(p, 1 << width):
            clauses.append([-(j*width+i+1) if value >> i & 1 else j*width+i+1 for i in range(width)])
    return clauses


def decode(model, p):
    positive = {v for v in model if v > 0}
    width = p.bit_length()
    values = [sum((1 << i) for i in range(width) if j*width+i+1 in positive) for j in range(4)]
    if any(v >= p for v in values):
        raise AssertionError("SAT returned noncanonical field encoding")
    return values


def solve(inp, arm, config):
    p = inp["p"]
    construction, search, checking = Counter(), Counter(), Counter()
    domain = domain_clauses(p)
    construction["domain_clauses"] += len(domain)
    construction["domain_clause_literals"] += sum(map(len, domain))
    prefixes = list(itertools.product(range(p), repeat=3))
    if arm == "aa_reverse_prefix":
        prefixes.reverse()
    models, learned, branches, proofs = [], [], [], {}
    status = "complete"
    max_prefix = config.get("max_prefixes_per_cell", p**3)
    max_leaves = config.get("max_coefficient_assignments_per_cell", p**4)
    with Minisat22(bootstrap_with=domain+[[i, -i] for i in range(1, 4*p.bit_length()+1)]) as sat:
        for prefix in prefixes:
            if search["prefixes_visited"] >= max_prefix:
                status = "censored"
                break
            search["prefixes_visited"] += 1
            if arm != "leaf_sat":
                proof = prefix_proof(inp, prefix, construction, search)
                ok, work = independent.certificate_check(p, proof)
                checking.update(work)
                if not ok:
                    raise AssertionError("prefix certificate rejected before clause publication")
                key = hashlib.sha256(canonical(proof).encode()).hexdigest()
                proofs[key] = proof
                root_ring = PolynomialRing(p, search)
                roots = [t for t in range(p) if root_ring.evaluate(proof["gcd"], t) == 0]
                search["root_candidates_evaluated"] += p
                forbidden = [t for t in range(p) if t not in roots]
                branches.append({"prefix": list(prefix), "proof_id": key, "roots": roots,
                                 "forbidden_values": forbidden})
                if not roots:
                    # This is a genuine 15-bit prefix clause, excluding all17
                    # legal b0 values before full coefficient assignments.
                    sat.add_clause(block(prefix, p))
                    search["whole_prefix_conflicts"] += 1
                    search["field_assignments_pruned_by_prefix"] += p
                    search["learned_clause_literals"] += 3*p.bit_length()
                    continue
                for t in forbidden:
                    sat.add_clause(block(list(prefix)+[t], p))
                    search["guarded_gcd_nonroot_clauses"] += 1
                    search["learned_clause_literals"] += 4*p.bit_length()
                search["field_assignments_pruned_by_gcd_nonroots"] += len(forbidden)
            assumptions = value_literals(prefix, p)
            while True:
                search["sat_calls"] += 1
                if not sat.solve(assumptions=assumptions):
                    break
                if search["coefficient_assignments_evaluated"] >= max_leaves:
                    status = "censored"
                    break
                values = decode(sat.get_model(), p)
                if values[:3] != list(prefix):
                    raise AssertionError("SAT assumptions not respected")
                search["coefficient_assignments_evaluated"] += 1
                residuals, _, _, _ = scalar_residuals(inp, values, search)
                violated = next((i for i, v in enumerate(residuals) if v), None)
                if violated is None:
                    models.append(values)
                    search["verified_coefficient_models"] += 1
                else:
                    if arm != "leaf_sat":
                        raise AssertionError("gcd admitted a root outside the original residual zero set")
                    # Independent scalar arithmetic checks a leaf certificate
                    # before the full-assignment clause is learned.
                    ref_residuals, _, _, _ = independent.scalar_residuals(inp, values, checking)
                    if ref_residuals[violated] != residuals[violated]:
                        raise AssertionError("leaf certificate failed independent arithmetic")
                    learned.append([independent.pack(values, p), violated, residuals[violated]])
                    search["leaf_conflicts"] += 1
                sat.add_clause(block(values, p))
                search["learned_clause_literals"] += 4*p.bit_length()
            if status != "complete":
                break
        stats = sat.accum_stats()
    return {"status": status, "coefficient_models": sorted(models),
            "search": {"counts": {k:v for k,v in search.items() if not k.startswith("polynomial_")},
                       "sat_native": stats, "learned_leaf": learned, "prefix_records": branches},
            "costs": {"construction": dict(construction), "search": dict(search),
                      "proof_check": dict(checking)}, "_proofs": proofs}


def projective_add(P, Q, p, a, counts):
    counts["jacobian_group_addition_calls"] += 1
    X, Y, Z = P
    U, V, W = Q
    if not Z:
        return Q
    if not W:
        return P
    u, v = X*W*W % p, U*Z*Z % p
    s, t = Y*W**3 % p, V*Z**3 % p
    if u == v:
        if s != t or Y == 0:
            return (0, 1, 0)
        M = (3*X*X+a*Z**4) % p
        S = 4*X*Y*Y % p
        xx = (M*M-2*S) % p
        return (xx, (M*(S-xx)-8*Y**4) % p, 2*Y*Z % p)
    h, rr = (v-u) % p, (t-s) % p
    xx = (rr*rr-h**3-2*u*h*h) % p
    return (xx, (rr*(u*h*h-xx)-s*h**3) % p, h*Z*W % p)


def projective_sum(points, p, a, counts):
    ans = (0, 1, 0)
    for x, y in points:
        ans = projective_add(ans, (x, y, 1), p, a, counts)
    if ans[2] == 0:
        return None
    counts["field_inverse_calls"] += 1
    zi = pow(ans[2], -1, p)
    return [ans[0]*zi*zi % p, ans[1]*zi**3 % p]


def reconstruct(inp, models):
    counts, statuses = Counter(), Counter()
    relations = set()
    p, a, b = (inp[k] for k in ("p", "a", "b"))
    R = inp["target"]
    for values in models:
        counts["coefficient_models_reconstructed"] += 1
        residuals, A, B, U = scalar_residuals(inp, values, counts)
        if any(residuals):
            raise AssertionError("invalid coefficient model during recovery")
        ring = PolynomialRing(p, counts)
        if ring.evaluate(U, R[0]) == 0:
            statuses["excluded_target_coordinate"] += 1
            continue
        roots = [x for x in range(p) if ring.evaluate(U, x) == 0]
        counts["root_candidates_evaluated"] += p
        if len(roots) != 5:
            raise AssertionError("squarefree quotient predicate did not give five distinct rational roots")
        points = []
        for x in roots:
            denominator = ring.evaluate(B, x)
            if not denominator:
                # For squarefree U and U(r)!=0 this is algebraically impossible;
                # preserve failure instead of silently hiding it in fallback.
                raise AssertionError("unexpected generic recovery denominator zero")
            counts["field_inverse_calls"] += 1
            y = -ring.evaluate(A, x)*pow(denominator, -1, p) % p
            counts["curve_membership_evaluations"] += 1
            if (y*y-x**3-a*x-b) % p:
                raise AssertionError("recovered off-curve point")
            points.append([x, y])
        if projective_sum(points, p, a, counts) != R:
            raise AssertionError("recovered points have wrong sum")
        relations.add(canonical(points))
        statuses["generic_recovered"] += 1
    return {"relations": [json.loads(v) for v in sorted(relations)], "costs": dict(counts),
            "chart_status_counts": dict(statuses)}


def fallback(inp):
    """Complete charged target-coordinate chart for distinct-x finite tuples.

    This enumerates explicit point tuples in the exceptional chart. It does not
    use the independent oracle's model set. Repeated coordinates and identity
    summands are outside the declared predicate, not silently discarded charts.

    Coverage argument on the declared domain: if r is absent from the five
    distinct summand coordinates, sum(P_i)=R gives a principal divisor
    sum(P_i)+(-R)-6O with six distinct affine support points. Its function in
    L(6O) must have pole order6, hence nonzero x^3 coefficient, so it admits the
    normalized A3+B1*y representation. If B vanishes at a root of U, A also
    vanishes there and the norm has multiplicity at least2. Since that root is
    not r this contradicts squarefree U. Thus no additional leading-coefficient
    or recovery-denominator fallback is missing away from target-coordinate
    overlap. The independent full point census checks this coverage per cell.
    """
    counts = Counter()
    p, a, b, d, c = (inp[k] for k in ("p", "a", "b", "d", "c"))
    R = inp["target"]
    base = {}
    for x in range(p):
        counts["membership_pow_calls"] += 1
        if pow(x, d, p) != c:
            continue
        for y in range(p):
            counts["curve_membership_evaluations"] += 1
            if (y*y-x**3-a*x-b) % p == 0:
                base.setdefault(x, []).append([x, y])
    relations = []
    for xs in itertools.combinations(sorted(base), 5):
        counts["coordinate_subsets_considered"] += 1
        if R[0] not in xs:
            counts["generic_subsets_skipped"] += 1
            continue
        for points in itertools.product(*(base[x] for x in xs)):
            counts["signed_point_tuples_enumerated"] += 1
            if projective_sum(points, p, a, counts) == R:
                relations.append(list(points))
    return {"relations": sorted(relations), "costs": dict(counts),
            "chart_status_counts": {"target_coordinate_relations": len(relations)},
            "scope": "target_coordinate_chart_only_distinct_x_affine_summands"}


def instrument_controls():
    """Synthetic polynomial/certificate controls, no selected elliptic fixture."""
    p = 7
    # t and t-1 cannot vanish together: t-(t-1)=1.
    field = [0, p-1]+[0]*(p-2)+[1]
    proof = {"prefix": [0, 0, 0], "field_polynomial": field,
             "residuals": [[0, 1], [p-1, 1], [0], [0], [0]],
             "gcd": [1], "multipliers": [[0], [1], [p-1], [0], [0], [0]]}
    valid, _ = independent.certificate_check(p, proof)
    corrupted = json.loads(json.dumps(proof))
    corrupted["multipliers"][1] = [2]
    bad, _ = independent.certificate_check(p, corrupted)
    ar = independent.Arithmetic(p)
    # A repeated-root modulus cannot divide the squarefree polynomial X^2-1.
    repeated = ar.division([p-1, 0, 1], [1, p-2, 1])[1] != [0]
    finite = PolynomialRing(p, finite=True)
    field_reduction = finite.reduce(field) == [0]
    return {"positive_bezout_identity": valid, "corrupted_bezout_rejected": not bad,
            "negative_repeated_root_quotient_rejected": repeated,
            "finite_field_polynomial_reduces_to_zero": field_reduction}


def run(config, checkpoint=None):
    if config["arms"] != ["leaf_sat", "prefix_univariate_gcd", "exhaustive_reference", "aa_reverse_prefix"]:
        raise ValueError("unexpected arm inventory")
    if config.get("coset_c", 1) != 1:
        raise ValueError("fixed coset c=1 required")
    if config.get("curves", [{"p":17,"a":2,"b":2}]) != [{"p":17,"a":2,"b":2}]:
        raise ValueError("fixed public curve required")
    inputs = independent.expected_cells(config)
    cells = []
    for inp in inputs:
        cell = {"id": independent.cell_id(inp), "input": inp, "arms": {}, "proofs": {}}
        # Candidate searches complete before either exhaustive reference census.
        for arm in ("leaf_sat", "prefix_univariate_gcd", "aa_reverse_prefix"):
            answer = solve(inp, arm, config)
            proofs = answer.pop("_proofs")
            for key, proof in proofs.items():
                if key in cell["proofs"] and cell["proofs"][key] != proof:
                    raise AssertionError("proof digest collision")
                cell["proofs"][key] = proof
            recovered = reconstruct(inp, answer["coefficient_models"])
            exception = fallback(inp)
            answer["generic_relations"] = sorted(recovered["relations"])
            answer["reconstruction"] = {"chart_status_counts": recovered["chart_status_counts"]}
            answer["fallback"] = exception
            answer["complete_relations"] = sorted(recovered["relations"]+exception["relations"])
            answer["costs"]["reconstruction"] = recovered["costs"]
            answer["costs"]["chart_fallback"] = exception["costs"]
            cell["arms"][arm] = answer
        coefficient_reference = independent.enumerate_coefficients(inp)
        point_reference = independent.enumerate_relations(inp)
        cell["reference"] = {"coefficient_models": coefficient_reference["models"],
                             "relations": point_reference["relations"],
                             "costs": {"coefficient_oracle": coefficient_reference["costs"],
                                       "point_oracle": point_reference["costs"]}}
        recovered = reconstruct(inp, coefficient_reference["models"])
        exception = fallback(inp)
        cell["arms"]["exhaustive_reference"] = {
            "status": "complete", "coefficient_models": coefficient_reference["models"],
            "generic_relations": sorted(recovered["relations"]), "fallback": exception,
            "complete_relations": sorted(recovered["relations"]+exception["relations"]),
            "search": {"counts": {"coefficient_assignments_evaluated": inp["p"]**4}},
            "costs": {"construction": {}, "search": coefficient_reference["costs"],
                      "proof_check": {}, "reconstruction": recovered["costs"],
                      "chart_fallback": exception["costs"]}}
        cell["checks"] = {
            "complete_coefficient_model_agreement": all(arm["coefficient_models"] == coefficient_reference["models"]
                                                       for arm in cell["arms"].values() if arm["status"] == "complete"),
            "complete_chart_union_agreement": all(arm["complete_relations"] == point_reference["relations"]
                                                 for arm in cell["arms"].values() if arm["status"] == "complete"),
            "aa_semantic_equality_when_both_complete":
                (cell["arms"]["prefix_univariate_gcd"]["coefficient_models"] == cell["arms"]["aa_reverse_prefix"]["coefficient_models"])
                if all(cell["arms"][name]["status"] == "complete" for name in ("prefix_univariate_gcd", "aa_reverse_prefix")) else True}
        cells.append(cell)
        if checkpoint:
            checkpoint(cell)
    return {"schema": "prime-sat-coefficients-result/v1", "config": config,
            "cells": cells, "controls": instrument_controls(),
            "scope": "complete_finite_squarefree_coordinate_predicate_not_repeated_root_or_full_ECDLP_coverage",
            "cost_scope": "polynomial_field_primitives_and_explicit_group_oracle_events_separate_by_phase_no_universal_operation_total"}
