"""Equivalent finite encodings with proof-producing Boolean SAT learning.

The degree cap belongs to an incomplete polynomial-calculus search. It is
neither a degree-of-regularity estimate nor a lower bound after UNKNOWN.
No complete-model oracle is available to the learner.
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "prime_sat_five_tests_20261029"))
from core import BoolRing, refute
from pysat.solvers import Minisat22


class CountedRing(BoolRing):
    def eval(self, poly, bits):
        self.counts["evaluation_term_visits"] = self.counts.get("evaluation_term_visits", 0) + len(poly)
        return super().eval(poly, bits)

    def restrict(self, poly, assignments):
        self.counts["restriction_term_visits"] = self.counts.get("restriction_term_visits", 0) + len(poly)
        return super().restrict(poly, assignments)

    def from_values(self, values):
        self.counts["membership_transform_subtractions"] = self.counts.get("membership_transform_subtractions", 0) + self.n * (1 << (self.n - 1))
        return super().from_values(values)


def delta(before, after):
    return {k: after.get(k, 0) - before.get(k, 0) for k in set(before) | set(after)}


def build(cell, arm):
    p, s, a, b = (cell[k] for k in ("p", "s", "a", "b"))
    r, sy = cell["target"]
    if p <= 3 or sy % p == 0 or (4*a**3 + 27*b*b) % p == 0 or 1 << s > p:
        raise ValueError("nonsingular odd-characteristic curve, non-two-torsion target, distinct digits required")
    if (sy*sy-r*r*r-a*r-b) % p:
        raise ValueError("target is not a curve point")
    lifted = arm in ("quadratic", "quadratic_aa")
    width = p.bit_length() if lifted else 0
    ring = CountedRing(2*s+width, p)
    def digit(start, n):
        value = {}
        for i in range(n):
            value = ring.add(value, ring.scale(ring.var(start+i), 1 << i))
        return value
    x, y = digit(0, s), digit(s, s)
    add, sub, mul, scale, c = ring.add, ring.sub, ring.mul, ring.scale, ring.const
    xy, summ, diff = mul(x, y), add(x, y), sub(x, y)
    if lifted:
        lam = digit(2*s, width)
        polys = [sub(mul(lam, lam), add(summ, c(r))),
                 sub(scale(lam, 2*sy), sub(sub(xy, scale(summ, r)), c(2*r*r+a)))]
        if arm == "quadratic_aa":
            polys.reverse()
    else:
        polys = [add(sub(scale(mul(diff, diff), r*r),
                         scale(add(mul(summ, add(xy, c(a))), c(2*b)), 2*r)),
                     sub(mul(sub(xy, c(a)), sub(xy, c(a))), scale(summ, 4*b)))]
        if arm == "membership":
            for start in (0, s):
                values = []
                for mask in range(1 << ring.n):
                    xx = (mask >> start) & ((1 << s)-1)
                    rhs = (xx**3 + a*xx + b) % p
                    values.append(int(rhs != 0 and pow(rhs, (p-1)//2, p) != 1))
                    ring.counts["legendre_pow_calls"] = ring.counts.get("legendre_pow_calls", 0) + int(rhs != 0)
                ring.counts["membership_curve_tests"] = ring.counts.get("membership_curve_tests", 0) + len(values)
                polys.append(ring.from_values(values))
    domain = []
    for value in range(p, 1 << width) if lifted else ():
        domain.append([-(2*s+i+1) if value >> i & 1 else 2*s+i+1 for i in range(width)])
    ring.counts["domain_clauses"] = len(domain)
    return ring, polys, domain


def certificate_check(p, generators, multipliers):
    """Independent term-pair identity check, including full multiplication cost."""
    cost = Counter()
    if multipliers is None or len(multipliers) != len(generators):
        return False, dict(cost)
    total = Counter()
    for f, q in zip(generators, multipliers):
        for m, c in f.items():
            for k, v in q.items():
                total[int(m) | int(k)] = (total[int(m) | int(k)] + c*v) % p
                cost["coefficient_multiplications"] += 1
                cost["coefficient_additions"] += 1
    return {m:c for m,c in total.items() if c} == {0:1}, dict(cost)


def block(bits, depth):
    return [-(i+1) if bits >> i & 1 else i+1 for i in range(depth)]


def clause_true(clause, bits):
    return any(bool(bits >> (abs(lit)-1) & 1) == (lit > 0) for lit in clause)


def solve(ring, polys, domain, projected_bits, limits):
    before = dict(ring.counts)
    learned, models = [], []
    unknown_prefixes = set()
    counters, verification_cost = Counter(), Counter()
    status = "censored"
    with Minisat22(bootstrap_with=domain + [[i+1, -(i+1)] for i in range(ring.n)]) as sat:
        while counters["sat_candidates"] < limits["sat_candidates"]:
            counters["sat_calls"] += 1
            if not sat.solve():
                status = "complete"
                break
            bits = sum(1 << (lit-1) for lit in sat.get_model() if lit > 0)
            counters["sat_candidates"] += 1
            if all(ring.eval(f, bits) == 0 for f in polys):
                models.append(bits)
                sat.add_clause(block(bits, projected_bits))
                continue
            success = False
            # Identical fixed prefix schedule for every arm. Full restriction
            # is a checked leaf explanation; never a trusted oracle clause.
            for depth in sorted(set((0, projected_bits//2, projected_bits, ring.n))):
                key = (depth, bits & ((1 << depth)-1))
                if key in unknown_prefixes:
                    continue
                if counters["pc_calls"] >= limits["pc_calls"]:
                    break
                assignments = {i:(bits >> i)&1 for i in range(depth)}
                residual = [ring.restrict(f, assignments) for f in polys]
                answer = refute(ring, residual, limits["degree"], limits["rows"])
                counters["pc_calls"] += 1
                counters["pc_attempted_rows"] += answer["attempted_rows"]
                counters["field_inverse_calls"] += answer["rank"]
                counters["pc_capped_calls"] += int(answer["resource_capped"])
                counters["max_accepted_row_degree"] = max(counters["max_accepted_row_degree"], answer["max_accepted_row_degree"])
                if answer["status"] != "refuted":
                    unknown_prefixes.add(key)
                    continue
                ok, count = certificate_check(ring.p, residual, answer["certificate"])
                verification_cost.update(count)
                if not ok:
                    raise AssertionError("invalid learned certificate")
                clause = block(bits, depth)
                learned.append({"depth":depth, "prefix":key[1], "clause":clause,
                                "certificate":answer["certificate"],
                                "rank":answer["rank"], "attempted_rows":answer["attempted_rows"]})
                sat.add_clause(clause)
                success = True
                break
            if not success:
                break
        stats = sat.accum_stats()
    return {"status":status, "models":models, "learned":learned,
            "costs":{"search_arithmetic":delta(before, ring.counts),
                     "search_events":dict(counters), "online_certificate_check":dict(verification_cost),
                     "sat_native":stats},
            "certificate_bytes":len(json.dumps(learned, sort_keys=True, separators=(",", ":")).encode())}


def affine_add(P, Q, p, a, counts=None):
    if counts is not None:
        counts["group_addition_calls"] += 1
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P; z, w = Q
    if x == z and (y+w) % p == 0:
        return None
    if counts is not None:
        counts["field_inverse_calls"] += 1
    slope = ((3*x*x+a)*pow(2*y, -1, p) if P == Q else (w-y)*pow(z-x, -1, p)) % p
    out = (slope*slope-x-z) % p
    return out, (slope*(x-out)-y) % p


def reference(cell):
    p, a, b, s = (cell[k] for k in ("p", "a", "b", "s"))
    cost = Counter()
    points = []
    for x in range(1 << s):
        for y in range(p):
            cost["curve_equation_tests"] += 1
            if (y*y-x*x*x-a*x-b) % p == 0:
                points.append((x, y))
    target = tuple(cell["target"])
    models = set()
    for P, Q in itertools.product(points, repeat=2):
        if affine_add(P, Q, p, a, cost) == target:
            models.add((P[0], Q[0]))
    return sorted(models), dict(cost)


def reconstruct(cell, projections):
    p, a, b = (cell[k] for k in ("p", "a", "b"))
    r, sy = cell["target"]
    costs = Counter(); witnesses = []
    for x, z in projections:
        costs["field_inverse_calls"] += 1
        costs["witnesses"] += 1
        lam = (x*z-r*(x+z)-2*r*r-a)*pow(2*sy, -1, p) % p
        P = (x, (lam*(x-r)-sy) % p)
        Q = (z, (lam*(z-r)-sy) % p)
        costs["curve_equation_tests"] += 2
        if any((Y*Y-X**3-a*X-b) % p for X, Y in (P,Q)) or affine_add(P,Q,p,a,costs) != tuple(cell["target"]):
            raise AssertionError("lift does not reconstruct the target")
        witnesses.append({"x":[x,z], "lambda":lam, "points":[P,Q]})
    return witnesses, dict(costs)


def census(cell, ring, polys, domain):
    before = dict(ring.counts); models = []; visits = 0
    mask = (1 << cell["s"])-1
    for bits in range(1 << ring.n):
        visits += 1
        if all(clause_true(cl, bits) for cl in domain) and all(ring.eval(f,bits) == 0 for f in polys):
            models.append(bits)
    projections = sorted({(bits & mask, (bits >> cell["s"]) & mask) for bits in models})
    return {"complete_models":models, "projected_models":projections,
            "costs":{**delta(before,ring.counts),"boolean_assignments_visited":visits}}


def verify_search(cell, ring, polys, domain, answer, expected):
    before = dict(ring.counts)
    cost = Counter(); learned = answer["learned"]
    for item in learned:
        depth, prefix = item["depth"], item["prefix"]
        if not 0 <= depth <= ring.n or not 0 <= prefix < 1 << depth or item["clause"] != block(prefix, depth):
            raise AssertionError("malformed prefix clause")
        residual = [ring.restrict(f,{i:(prefix>>i)&1 for i in range(depth)}) for f in polys]
        ok, counts = certificate_check(ring.p, residual, item["certificate"])
        cost.update(counts)
        if not ok:
            raise AssertionError("certificate identity rejected")
    projected = []
    for bits in answer["models"]:
        if not 0 <= bits < 1 << ring.n or not all(clause_true(c,bits) for c in domain) or any(ring.eval(f,bits) for f in polys):
            raise AssertionError("invalid returned model")
        projected.append((bits & ((1 << cell["s"])-1), (bits >> cell["s"]) & ((1 << cell["s"])-1)))
    if len(set(projected)) != len(projected) or not set(projected) <= set(expected):
        raise AssertionError("wrong or repeated projection")
    if answer["status"] == "complete":
        clauses = domain + [item["clause"] for item in learned] + [block(bits, 2*cell["s"]) for bits in answer["models"]]
        for bits in range(1 << ring.n):
            cost["exhaustive_unsat_assignments"] += 1
            if all(clause_true(c,bits) for c in clauses):
                raise AssertionError("claimed SAT exhaustion is incomplete")
        if sorted(projected) != expected:
            raise AssertionError("complete solver projected set mismatch")
    elif answer["status"] != "censored":
        raise AssertionError("unknown status")
    cost.update(delta(before,ring.counts))
    return dict(cost)


def controls():
    ring = CountedRing(1,17)
    good = refute(ring,[ring.var(0),ring.sub(ring.var(0),ring.const(1))],1,32)
    ok,_ = certificate_check(17,[ring.var(0),ring.sub(ring.var(0),ring.const(1))],good["certificate"])
    bad,_ = certificate_check(17,[ring.var(0),ring.sub(ring.var(0),ring.const(1))],[{},{}])
    sat = refute(ring,[ring.var(0)],1,32)
    limits = {"sat_candidates":16,"pc_calls":32,"degree":1,"rows":32}
    positive = solve(CountedRing(1,17),[{1:1}],[],1,limits)
    negative = solve(CountedRing(1,17),[{1:1},{1:1,0:16}],[],1,limits)
    return {"affine_unsat_certificate":ok,"tampered_certificate_rejected":not bad,
            "satisfiable_not_refuted":sat["status"]=="unknown",
            "positive_sat_complete":positive["status"]=="complete" and positive["models"]==[0],
            "negative_unsat_complete":negative["status"]=="complete" and negative["models"]==[]}


def run(config, checkpoint=None):
    cells = []
    for curve in config["curves"]:
        p, a, b = (curve[k] for k in ("p", "a", "b"))
        targets = [(x,next(y for y in range(1,p) if (y*y-x**3-a*x-b)%p == 0))
                   for x in range(p) if any((y*y-x**3-a*x-b)%p == 0 for y in range(1,p))]
        for s in config["digits"]:
            for target in targets:
                spec = {**curve,"s":s,"target":list(target)}
                row = {"id":f"p{p}-s{s}-r{target[0]}","input":spec,"arms":[]}
                # Reference is deliberately computed only after all learner runs.
                built = []
                for arm in config["arms"]:
                    ring, polys, domain = build(spec, arm)
                    build_cost = dict(ring.counts)
                    answer = solve(ring,polys,domain,2*s,config["limits"])
                    built.append((ring,polys,domain))
                    row["arms"].append({"arm":arm,"variables":ring.n,
                        "input_degrees":[ring.degree(f) for f in polys],
                        "construction_cost":build_cost,"search":answer})
                refs, ref_cost = reference(spec)
                row["reference_models"],row["reference_cost"] = refs,ref_cost
                for output,(ring,polys,domain) in zip(row["arms"],built):
                    output["census"] = census(spec,ring,polys,domain)
                    if output["census"]["projected_models"] != refs:
                        raise AssertionError("equivalent-encoding census mismatch")
                    output["verification_cost"] = verify_search(spec,ring,polys,domain,output["search"],refs)
                    output["witnesses"],output["reconstruction_cost"] = reconstruct(spec,refs)
                cells.append(row)
                if checkpoint:
                    checkpoint(row)
    checks = controls()
    if not all(checks.values()):
        raise AssertionError("integrity control failed")
    return {"config":config,"cells":cells,"controls":checks}


def verify(payload):
    cfg = payload["config"]
    expected = []
    for curve in cfg["curves"]:
        for s in cfg["digits"]:
            for x in range(curve["p"]):
                ys = [y for y in range(1,curve["p"]) if (y*y-x**3-curve["a"]*x-curve["b"])%curve["p"]==0]
                if ys:
                    expected.append({**curve,"s":s,"target":[x,min(ys)]})
    if [row["input"] for row in payload["cells"]] != expected or not all(payload["controls"].values()) or payload["controls"] != controls():
        raise AssertionError("fixture or control coverage mismatch")
    counts = Counter()
    for row in payload["cells"]:
        refs,_ = reference(row["input"])
        if refs != [tuple(x) for x in row["reference_models"]] or [x["arm"] for x in row["arms"]] != cfg["arms"]:
            raise AssertionError("reference or arm mismatch")
        for arm in row["arms"]:
            ring,polys,domain = build(row["input"],arm["arm"])
            if dict(ring.counts) != arm["construction_cost"]:
                raise AssertionError("construction counters mismatch")
            got = census(row["input"],ring,polys,domain)
            if (got["complete_models"] != arm["census"]["complete_models"]
                    or got["projected_models"] != refs
                    or got["projected_models"] != [tuple(x) for x in arm["census"]["projected_models"]]
                    or got["costs"] != arm["census"]["costs"]):
                raise AssertionError("full assignment census mismatch")
            events = arm["search"]["costs"]["search_events"]
            if (events.get("sat_candidates",0) > cfg["limits"]["sat_candidates"]
                    or events.get("pc_calls",0) > cfg["limits"]["pc_calls"]
                    or events.get("sat_candidates",0) < len(arm["search"]["models"])+len(arm["search"]["learned"])):
                raise AssertionError("search budget/counter contradiction")
            verify_search(row["input"],ring,polys,domain,arm["search"],refs)
            witnesses,cost = reconstruct(row["input"],refs)
            s = row["input"]["s"]
            expected_full = sorted(w["x"][0] + (w["x"][1] << s) +
                ((w["lambda"] << (2*s)) if arm["arm"] in ("quadratic","quadratic_aa") else 0)
                for w in witnesses)
            if got["complete_models"] != expected_full:
                raise AssertionError("independent lifted full-model set mismatch")
            if json.dumps(witnesses,sort_keys=True) != json.dumps(arm["witnesses"],sort_keys=True) or cost != arm["reconstruction_cost"]:
                raise AssertionError("witness reconstruction mismatch")
            counts[arm["search"]["status"]] += 1
            counts["certificates"] += len(arm["search"]["learned"])
    return {"valid":True,"cells":len(expected),"counts":dict(counts)}
