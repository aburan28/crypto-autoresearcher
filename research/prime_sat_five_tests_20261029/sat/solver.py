"""A certificate-producing Boolean SAT / finite-field learning prototype.

This is an external theory-lemma loop around MiniSat, not a new CDCL engine.
Every learned clause has a checked Boolean polynomial-calculus identity on
the forbidden prefix. Enumerative truth tables are independent validation
and baseline work; they are never consulted by the learner.
"""
import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import BoolRing, generate_s3, refute, check_refutation


def learned_solve(ring, generators, degree_cap=2, row_cap=4096):
    from pysat.solvers import Minisat22
    proof, calls, row_attempts = [], 0, 0
    with Minisat22(bootstrap_with=[[i+1, -(i+1)] for i in range(ring.n)]) as sat:
        for round_index in range((1 << ring.n) + 1):
            if not sat.solve():
                return {"status": "unsat", "model": None, "learned": proof,
                        "candidate_rounds": round_index, "pc_calls": calls,
                        "pc_attempted_rows": row_attempts, "sat_stats": sat.accum_stats()}
            model = {abs(v)-1: int(v > 0) for v in sat.get_model() if abs(v) <= ring.n}
            bits = sum(model.get(i, 0) << i for i in range(ring.n))
            if all(ring.eval(f, bits) == 0 for f in generators):
                return {"status": "sat", "model": bits, "learned": proof,
                        "candidate_rounds": round_index+1, "pc_calls": calls,
                        "pc_attempted_rows": row_attempts, "sat_stats": sat.accum_stats()}
            learned = False
            for depth in range(ring.n+1):
                prefix = {i: (bits >> i) & 1 for i in range(depth)}
                residuals = [ring.restrict(f, prefix) for f in generators]
                result = refute(ring, residuals, degree_cap, row_cap)
                calls += 1
                row_attempts += result["attempted_rows"]
                if result["status"] != "refuted":
                    continue
                if not check_refutation(ring.p, ring.n, residuals, result["certificate"]):
                    raise AssertionError("invalid learned-clause certificate")
                clause = [-(i+1) if value else i+1 for i, value in prefix.items()]
                sat.add_clause(clause)
                proof.append({"prefix": prefix, "clause": clause, **result})
                learned = True
                break
            if not learned:
                return {"status": "unknown", "reason": "no certified blocking clause",
                        "model": None, "learned": proof, "pc_calls": calls,
                        "pc_attempted_rows": row_attempts}
    return {"status": "unknown", "reason": "round cap", "learned": proof}


def verify_learning(ring, generators, result):
    """Independent identity checks plus exhaustive final clause implication.

    Exhaustive implication is deliberately charged as verification, and is
    feasible only at this stage's small fixed sizes. UNSAT has no trusted
    dependency on MiniSat's response.
    """
    for row in result["learned"]:
        prefix = {int(i): int(v) for i, v in row["prefix"].items()}
        residuals = [ring.restrict(f, prefix) for f in generators]
        if not check_refutation(ring.p, ring.n, residuals, row["certificate"]):
            return False
        expected = [-(i+1) if v else i+1 for i, v in prefix.items()]
        if row["clause"] != expected:
            return False
    if result["status"] == "sat":
        model = result["model"]
        return isinstance(model, int) and 0 <= model < (1 << ring.n) and all(
            ring.eval(f, model) == 0 for f in generators)
    if result["status"] == "unsat":
        for bits in range(1 << ring.n):
            if all(any(((bits >> (abs(lit)-1)) & 1) == int(lit > 0)
                       for lit in row["clause"]) for row in result["learned"]):
                return False
        return True
    return False


def z3_solve(ring, generators):
    import z3
    variables = [z3.Bool("b"+str(i)) for i in range(ring.n)]
    solver = z3.Solver()
    solver.set(timeout=10000)
    for f in generators:
        # The total unsigned sum is <2**32 on every frozen input; therefore
        # this bit-vector encoding has no unmodelled integer overflow.
        if sum(f.values()) >= (1 << 32):
            return {"status": "unsupported", "reason": "sum overflow bound"}
        terms = []
        for m, c in f.items():
            condition = z3.And(*[variables[i] for i in range(ring.n) if m & (1 << i)])
            terms.append(z3.If(condition, z3.BitVecVal(c, 32), z3.BitVecVal(0, 32)))
        total = sum(terms, z3.BitVecVal(0, 32))
        solver.add(z3.URem(total, z3.BitVecVal(ring.p, 32)) == 0)
    answer = solver.check()
    if answer == z3.sat:
        model = solver.model()
        bits = sum(int(z3.is_true(model.eval(v, model_completion=True))) << i
                   for i, v in enumerate(variables))
        return {"status": "sat", "model": bits, "variables": ring.n,
                "encoding": "expanded Boolean monomials and 32-bit modular sums"}
    return {"status": "unsat" if answer == z3.unsat else "unknown",
            "reason": solver.reason_unknown() if answer == z3.unknown else None}


def cvc5_solve(ring, generators):
    import cvc5
    from cvc5 import Kind
    try:
        tm = cvc5.TermManager()
        solver = cvc5.Solver(tm)
        solver.setOption("produce-models", "true")
        solver.setOption("tlimit-per", "10000")
        solver.setLogic("QF_FF")
        field = tm.mkFiniteFieldSort(str(ring.p))
        elem = lambda c: tm.mkFiniteFieldElem(str(c % ring.p), field)
        zero, one = elem(0), elem(1)
        variables = [tm.mkConst(field, "b"+str(i)) for i in range(ring.n)]
        for v in variables:
            square = tm.mkTerm(Kind.FINITE_FIELD_MULT, v, v)
            solver.assertFormula(tm.mkTerm(Kind.EQUAL, square, v))
        for f in generators:
            terms = []
            for m, c in f.items():
                factors = [elem(c)] + [variables[i] for i in range(ring.n) if m & (1 << i)]
                terms.append(factors[0] if len(factors) == 1 else tm.mkTerm(Kind.FINITE_FIELD_MULT, *factors))
            total = zero if not terms else terms[0] if len(terms) == 1 else tm.mkTerm(Kind.FINITE_FIELD_ADD, *terms)
            solver.assertFormula(tm.mkTerm(Kind.EQUAL, total, zero))
        answer = solver.checkSat()
        if answer.isSat():
            bits = 0
            for i, v in enumerate(variables):
                vv = solver.getValue(v)
                if vv != zero and vv != one:
                    raise AssertionError("non-Boolean field model")
                bits |= int(vv == one) << i
            return {"status": "sat", "model": bits}
        return {"status": "unsat" if answer.isUnsat() else "unknown"}
    except RuntimeError as exc:
        if "CoCoA" in str(exc) or "not configured" in str(exc):
            return {"status": "unsupported", "reason": str(exc)}
        raise


def finite_points(p, a=1, b=1):
    return [(x, y) for x in range(p) for y in range(p) if (y*y-x*x*x-a*x-b) % p == 0]


def ec_add(p, P, Q, a=1):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u and (y+v) % p == 0:
        return None
    slope = ((3*x*x+a)*pow(2*y, -1, p) if P == Q else (v-y)*pow(u-x, -1, p)) % p
    xx = (slope*slope-x-u) % p
    return xx, (slope*(x-xx)-y) % p


def lift_check(metadata, bits):
    p, s, r = metadata["p"], metadata["s"], metadata["target"]
    a, b = metadata["a"], metadata["b"]
    x, u = bits & ((1 << s)-1), bits >> s
    points = finite_points(p,a,b)
    R = next((P for P in points if P[0] == r), None)
    if R is None:
        return {"target_has_curve_lift": False, "point_decomposition": None}
    pairs = [(P, Q) for P in points if P[0] == x for Q in points
             if Q[0] == u and ec_add(p, P, Q,a) == R]
    return {"target_has_curve_lift": True, "point_decomposition": bool(pairs),
            "witness": pairs[0] if pairs else None, "target_point": R}


def run(config=None, checkpoint=None):
    config = config or {}
    rows = []
    for p, s, target, membership in itertools.product(config.get("primes", [17,97,257]),
            config.get("digits", config.get("digit_bits", [2,3])), config.get("targets", [0,1,2]), [False,True]):
        current = {"input": {"p": p, "s": s, "target": target,
                              "curve_membership": membership}}
        stage = "construct_instance"
        try:
            instance = generate_s3(p, s, target, **config.get("curve", {"a":1,"b":1}), curve_membership=membership)
            ring, polys = instance["ring"], instance["polynomials"]
            current.update({"instance": instance["metadata"], "generators": polys})
            ring.counts = dict.fromkeys(ring.counts, 0)
            stage = "learn"
            learned = learned_solve(ring, polys, config.get("degree_cap", 2), config.get("row_cap",4096))
            current["learner"] = learned
            solver_counts = dict(ring.counts)
            current["solver_counts"] = solver_counts
            stage = "verify_learner"
            checked = verify_learning(ring, polys, learned)
            current["verified"] = checked
            # Enumerative oracle comes after the candidate solver and does not
            # modify any solver policy or parameter.
            stage = "enumerative_oracle"
            solutions = [bits for bits in range(1 << ring.n) if all(ring.eval(f,bits)==0 for f in polys)]
            expected = "sat" if solutions else "unsat"
            current.update({"oracle_solution_count": len(solutions),
                            "oracle_assignments": 1 << ring.n})
            stage = "independent_backends"
            z3_result, ff_result = z3_solve(ring,polys), cvc5_solve(ring,polys)
            current.update({"z3": z3_result, "cvc5": ff_result})
            for backend in (z3_result,ff_result):
                if backend["status"] in ("sat","unsat") and backend["status"] != expected:
                    raise AssertionError("backend/oracle disagreement")
                if backend["status"] == "sat" and backend["model"] not in solutions:
                    raise AssertionError("invalid backend witness")
            if learned["status"] != expected or not checked:
                raise AssertionError("certificate learner failed exact cell")
            current["lift"] = (lift_check(instance["metadata"], learned["model"])
                                if learned["status"] == "sat" else None)
            rows.append({k: v for k, v in current.items() if k != "input"})
        except Exception as exc:
            if checkpoint is not None:
                checkpoint({"schema": "prime-five-sat-progress/v1", "status": "failed",
                            "config": config, "completed_rows": rows,
                            "failing_cell": {**current, "stage": stage,
                                "error": str(exc), "exception_type": type(exc).__name__}})
            raise
        if checkpoint is not None:
            checkpoint({"schema": "prime-five-sat-progress/v1", "status": "running",
                        "config": config, "completed_rows": rows,
                        "next_cell": {"p": p, "s": s, "target": target,
                                      "curve_membership": membership}})
    control_ring = BoolRing(2,17)
    controls=[]
    for name,polys in (("positive_sat", [{1:1}]),
                       ("negative_unsat", [{1:1},{0:16,1:1}])):
        result=learned_solve(control_ring,polys)
        controls.append({"name":name,"generators":polys,"result":result,
                         "verified":verify_learning(control_ring,polys,result)})
    # Deterministic A/A rerun of the first instance, separately charged.
    first=rows[0]
    inst=first["instance"]
    aa_instance=generate_s3(inst["p"],inst["s"],inst["target"],a=inst["a"],b=inst["b"],curve_membership=inst["curve_membership"])
    aa=learned_solve(aa_instance["ring"],aa_instance["polynomials"])
    comparable=lambda x:{k:v for k,v in x.items() if k!="sat_stats"}
    aa_equal=comparable(aa)==comparable(first["learner"])
    return {"schema":"prime-five-sat/v1", "config":config, "scope":"bounded proof-producing external theory learning",
            "counter_scope":"partial arithmetic instrument; excludes inversions, direct evaluation, restriction and backend internals",
            "exact_degree_of_regularity_claim":False,"rows":rows,"controls":controls,
            "aa":{"equal":aa_equal,"replay":aa},
            "all_verified":all(r["verified"] for r in rows) and all(c["verified"] for c in controls) and aa_equal}


def verify(data):
    config=data["config"]
    expected=list(itertools.product(config.get("primes",[17,97,257]),
        config.get("digits",config.get("digit_bits",[2,3])),config.get("targets",[0,1,2]),[False,True]))
    observed=[(r["instance"]["p"],r["instance"]["s"],r["instance"]["target"],r["instance"]["curve_membership"]) for r in data["rows"]]
    if observed!=expected:
        return False
    for row in data["rows"]:
        m=row["instance"]
        instance=generate_s3(m["p"],m["s"],m["target"],a=m["a"],b=m["b"],curve_membership=m["curve_membership"])
        saved=[instance["ring"].clean(f) for f in row["generators"]]
        if saved != instance["polynomials"] or not verify_learning(instance["ring"],saved,row["learner"]):
            return False
        assignments = 1 << instance["ring"].n
        solution_count = sum(all(instance["ring"].eval(f, bits) == 0 for f in saved)
                             for bits in range(assignments))
        if (type(row.get("oracle_assignments")) is not int or
                row["oracle_assignments"] != assignments or
                type(row.get("oracle_solution_count")) is not int or
                row["oracle_solution_count"] != solution_count):
            return False
    if [c["name"] for c in data["controls"]]!=["positive_sat","negative_unsat"]:
        return False
    ring=BoolRing(2,17)
    for control, expected_status, equations in zip(data["controls"],["sat","unsat"],[[{1:1}],[{1:1},{0:16,1:1}]]):
        if [ring.clean(f) for f in control["generators"]]!=equations or control["result"]["status"]!=expected_status:
            return False
        if not verify_learning(ring,equations,control["result"]):
            return False
    first=data["rows"][0]
    m=first["instance"]
    instance=generate_s3(m["p"],m["s"],m["target"],a=m["a"],b=m["b"],curve_membership=m["curve_membership"])
    comparable=lambda x:{k:v for k,v in x.items() if k!="sat_stats"}
    return (verify_learning(instance["ring"],instance["polynomials"],data["aa"]["replay"])
            and comparable(data["aa"]["replay"])==comparable(first["learner"])
            and data["aa"]["equal"] is True and data["all_verified"] is True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    config=json.loads(Path(args.config).read_text()) if args.config else {}
    Path(args.output).write_text(json.dumps(run(config),sort_keys=True,indent=2)+"\n")
