#!/usr/bin/env python3
"""J2 (1)+(2) supplement: does the archived engine's SEMI-NAIVE W_D equal the
LITERAL rule where the two can actually differ, i.e. on systems whose fixpoint
needs >= 2 iterations? TASK-20260924-c83b05.

Why: the archived self-test (selftest.json, C-SELF item
W_D_vs_brute_force_random_systems) compared 23 systems, all with
iterations_to_fixpoint <= 1; and every archived instance of RUN-CERTBIN-c417e0
has W_4 (and W_5) iterations_to_fixpoint <= 1. The semi-naive shortcut
(multiply only rows whose low lead is new) can only lose products from
iteration 2 on, so neither exercised it where it could fail.

Construction (constructed systems, not archived instances; no RUN-id):
  * seed 2026092483050 (chosen here), numpy PCG64;
  * nv in {5, 6, 7, 8}, D in {3, 4, 5} (D <= nv), neq in 2..nv, and each
    equation a SPARSE random Boolean polynomial of degree <= 2 (1..4 random
    monomials of degree <= 2) -- sparse systems need several mutant rounds;
  * for each system: engine Closure(nv, D, neq).w_closure (archived code,
    imported unchanged) versus own_algebra.literal_W (validator's literal
    rule); compare dims per iteration, fixpoint index, "1 in W", first
    iteration containing 1, and dims by degree; for every engine refutation,
    the engine's certificate is evaluated with the validator's own
    multilinear arithmetic (sum mu*f_k must be exactly 1);
  * POSITIVE CONTROL of the comparison's power: a validator-written TRUNCATED
    rule (stop after W^(1), i.e. what a semi-naive step that lost every
    product from iteration 2 on would compute) is compared with the literal
    rule on the same systems; the number of systems on which it differs is
    reported. If that number is 0 the comparison has no power.
BATCH B (added after batch A showed 0 refutations first reached at an
iteration >= 2, so batch A never exercised the certificate back-trace across
two or more iteration boundaries): seed 2026092483053, nv in 6..10, D = 3,
neq in nv-3..nv, 2..4 random monomials of degree <= 2 per equation, 12000
draws; same engine-vs-literal comparison and own certificate evaluation.
BATCH C (deep chains): the implication chain v_0 = 1, v_{i-1}(v_i + 1) = 0,
v_{L} = 0 on nv = L + 1 variables (L = 3..11), D in {2, 3}, with a random
variable relabelling and a random invertible F_2-mixing of the equations
(seed 2026092483054, 5 mixes per (L, D)); unsatisfiable by construction and
needing many mutant rounds at D = 2.
Output: j2-constructions/seminaive_stress_results.json
"""
import json
import os
import resource
import sys
import time
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import own_algebra as oa  # noqa: E402

SEED = 2026092483050
N_SYSTEMS = 3000


def eval_cert_own(cert, eqs):
    acc = {}
    for mu, k in cert:
        for m in eqs[k]:
            x = mu | m
            acc[x] = acc.get(x, 0) ^ 1
    return sorted(x for x, p in acc.items() if p)


def truncated_W(space, eqs, D):
    """W^(1) only (positive control)."""
    top_low = space.top_pos_le[D - 1]
    basis = oa.span_basis(oa.macaulay_rows(space, eqs, D))
    gens = list(basis.values())
    for h, g in list(basis.items()):
        if h <= top_low:
            for j in range(space.nv):
                gens.append(space.mul_var(j, g))
    nb = oa.span_basis(gens)
    return len(nb), 0 in nb


def main():
    sys.path.insert(0, IMPL)
    from closure import Closure
    rng = np.random.default_rng(SEED)
    t0 = time.time()
    spaces, closures = {}, {}
    rows = []
    mism = []
    cert_bad = []
    trunc_diff = 0
    it_hist = Counter()
    refuted_at = Counter()
    for n in range(N_SYSTEMS):
        nv = int(rng.integers(5, 9))
        D = int(rng.integers(3, 6))
        if D > nv:
            D = nv
        neq = int(rng.integers(2, nv + 1))
        allq = oa.monomials(nv, 2)
        eqs = []
        for _ in range(neq):
            t = int(rng.integers(1, 5))
            pick = rng.choice(len(allq), size=t, replace=False)
            eqs.append(sorted(int(allq[i]) for i in pick))
        if (nv, D) not in spaces:
            spaces[(nv, D)] = oa.Space(nv, D)
        sp = spaces[(nv, D)]
        if (nv, D, neq) not in closures:
            closures[(nv, D, neq)] = Closure(nv, D, neq)
        cl = closures[(nv, D, neq)]
        erec, ecert = cl.w_closure(eqs, want_cert=True)
        lit, _, _ = oa.literal_W(sp, eqs, D)
        fields = ["dims", "iterations_to_fixpoint", "final_dim", "one", "one_first_iteration", "dims_by_deg"]
        eq = {f: erec[f] == lit[f] for f in fields}
        it_hist[lit["iterations_to_fixpoint"]] += 1
        if lit["one"]:
            refuted_at[lit["one_first_iteration"]] += 1
        if not all(eq.values()):
            mism.append({"n": n, "nv": nv, "D": D, "neq": neq, "eqs": eqs, "engine": erec, "literal": lit})
        if erec["one"]:
            ok = eval_cert_own(ecert, eqs) == [0]
            if not ok:
                cert_bad.append({"n": n, "nv": nv, "D": D, "eqs": eqs})
        tdim, tone = truncated_W(sp, eqs, D)
        if (tdim, tone) != (lit["final_dim"], lit["one"]):
            trunc_diff += 1
        if lit["iterations_to_fixpoint"] >= 2 and len(rows) < 40:
            rows.append({"n": n, "nv": nv, "D": D, "neq": neq, "literal_dims": lit["dims"],
                         "engine_dims": erec["dims"], "engine_new_fallen": erec["new_fallen_per_iteration"],
                         "one_first_iteration": lit["one_first_iteration"], "match": all(eq.values())})
    ge2 = sum(v for k, v in it_hist.items() if k >= 2)
    ge3 = sum(v for k, v in it_hist.items() if k >= 3)
    refuted_ge2 = sum(v for k, v in refuted_at.items() if k is not None and k >= 2)
    out = {"task_id": "TASK-20260924-c83b05", "joint": "J2", "construction": "semi-naive vs literal W_D stress",
           "seed": SEED, "systems": N_SYSTEMS,
           "iterations_to_fixpoint_histogram": {str(k): v for k, v in sorted(it_hist.items())},
           "systems_with_ge2_iterations": ge2, "systems_with_ge3_iterations": ge3,
           "refutations_by_first_iteration": {str(k): v for k, v in sorted(refuted_at.items(), key=lambda x: (x[0] is None, x[0]))},
           "refutations_first_at_iteration_ge2": refuted_ge2,
           "engine_vs_literal_mismatches": len(mism), "mismatch_examples": mism[:5],
           "engine_certificates_failing_own_evaluation": len(cert_bad), "cert_fail_examples": cert_bad[:5],
           "positive_control_truncated_rule_differs_from_literal_on": trunc_diff,
           "examples_ge2_iterations": rows,
           "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
           "wall_seconds": round(time.time() - t0, 1)}
    out["batch_B"] = batch_B(Closure)
    out["batch_C"] = batch_C(Closure)
    out["wall_seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "seminaive_stress_results.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("examples_ge2_iterations", "mismatch_examples",
                                                                 "cert_fail_examples", "batch_B", "batch_C")}))
    print(json.dumps({k: v for k, v in out["batch_B"].items() if k != "examples_refuted_at_ge2"}))
    print(json.dumps({k: v for k, v in out["batch_C"].items() if k != "rows"}))


def compare_one(Closure, cls, spaces, nv, D, eqs):
    key = (nv, D, len(eqs))
    if key not in cls:
        cls[key] = Closure(nv, D, len(eqs))
    if (nv, D) not in spaces:
        spaces[(nv, D)] = oa.Space(nv, D)
    erec, ecert = cls[key].w_closure(eqs, want_cert=True)
    lit, _, _ = oa.literal_W(spaces[(nv, D)], eqs, D)
    fields = ["dims", "iterations_to_fixpoint", "final_dim", "one", "one_first_iteration", "dims_by_deg"]
    match = all(erec[f] == lit[f] for f in fields)
    cert_ok = None
    if erec["one"]:
        cert_ok = eval_cert_own(ecert, eqs) == [0]
    return erec, lit, match, cert_ok, ecert


def batch_B(Closure):
    rng = np.random.default_rng(2026092483053)
    cls, spaces = {}, {}
    it_hist, first_hist = Counter(), Counter()
    mism, certbad, ex = 0, 0, []
    for n in range(12000):
        nv = int(rng.integers(6, 11))
        D = 3
        neq = int(rng.integers(nv - 3, nv + 1))
        allq = oa.monomials(nv, 2)
        eqs = []
        for _ in range(neq):
            t = int(rng.integers(2, 5))
            pick = rng.choice(len(allq), size=t, replace=False)
            eqs.append(sorted(int(allq[i]) for i in pick))
        erec, lit, match, cert_ok, cert = compare_one(Closure, cls, spaces, nv, D, eqs)
        it_hist[lit["iterations_to_fixpoint"]] += 1
        first_hist[lit["one_first_iteration"]] += 1
        mism += (not match)
        certbad += (cert_ok is False)
        if lit["one"] and lit["one_first_iteration"] >= 2 and len(ex) < 10:
            ex.append({"n": n, "nv": nv, "neq": neq, "dims": lit["dims"], "engine_dims": erec["dims"],
                       "one_first_iteration": lit["one_first_iteration"], "cert_size": len(cert),
                       "cert_max_deg_mu": max(bin(m).count("1") for m, k in cert), "cert_ok_own": cert_ok,
                       "match": match})
    return {"seed": 2026092483053, "systems": 12000,
            "iterations_to_fixpoint_histogram": {str(k): v for k, v in sorted(it_hist.items())},
            "first_iteration_of_1_histogram": {str(k): v for k, v in sorted(first_hist.items(), key=lambda x: (x[0] is None, x[0] or 0))},
            "refutations_first_at_iteration_ge2": sum(v for k, v in first_hist.items() if k is not None and k >= 2),
            "engine_vs_literal_mismatches": mism, "engine_certificates_failing_own_evaluation": certbad,
            "examples_refuted_at_ge2": ex}


def batch_C(Closure):
    rng = np.random.default_rng(2026092483054)
    cls, spaces = {}, {}
    rows, mism, certbad = [], 0, 0
    for L in range(3, 12):
        nv = L + 1
        for D in (2, 3):
            for mix in range(5):
                perm = [int(x) for x in rng.permutation(nv)]
                V = lambda *ix: sum(1 << perm[i] for i in ix)  # noqa: E731
                base = [[V(0), 0]] + [[V(i - 1, i), V(i - 1)] for i in range(1, L + 1)] + [[V(L)]]
                neq = len(base)
                while True:
                    A = rng.integers(0, 2, size=(neq, neq))
                    # invertible over F_2?
                    Mx = A.copy() % 2
                    r = 0
                    for c in range(neq):
                        piv = [i for i in range(r, neq) if Mx[i, c]]
                        if not piv:
                            continue
                        Mx[[r, piv[0]]] = Mx[[piv[0], r]]
                        for i in range(neq):
                            if i != r and Mx[i, c]:
                                Mx[i] ^= Mx[r]
                        r += 1
                    if r == neq:
                        break
                eqs = []
                for i in range(neq):
                    acc = {}
                    for k in range(neq):
                        if A[i, k]:
                            for m in base[k]:
                                acc[m] = acc.get(m, 0) ^ 1
                    eqs.append(sorted(m for m, p in acc.items() if p))
                erec, lit, match, cert_ok, cert = compare_one(Closure, cls, spaces, nv, D, eqs)
                mism += (not match)
                certbad += (cert_ok is False)
                rows.append({"L": L, "D": D, "mix": mix, "dims": lit["dims"], "engine_dims": erec["dims"],
                             "iterations_to_fixpoint": lit["iterations_to_fixpoint"],
                             "one_first_iteration": lit["one_first_iteration"], "match": match,
                             "cert_ok_own": cert_ok,
                             "cert_size": None if cert is None else len(cert)})
    return {"seed": 2026092483054, "systems": len(rows), "engine_vs_literal_mismatches": mism,
            "engine_certificates_failing_own_evaluation": certbad,
            "max_one_first_iteration": max((r["one_first_iteration"] or 0) for r in rows),
            "max_iterations_to_fixpoint": max(r["iterations_to_fixpoint"] for r in rows),
            "refuted": sum(1 for r in rows if r["one_first_iteration"] is not None),
            "rows": rows}


if __name__ == "__main__":
    main()
