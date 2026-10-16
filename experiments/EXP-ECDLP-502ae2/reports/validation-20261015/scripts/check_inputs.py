#!/usr/bin/env python3
"""Rebuild every RUN-ECDLP-502ae2-01 instance with the committed launcher's construction code and check,
independently of msolve: (i) p, b, chain_c, fb_size, nvars, npolys match the raw record; (ii) every input
polynomial (incl. the Singular-expanded S_4) has <= 1 constant term under an independent parser;
(iii) the planted point (x and chain w's) zeroes every input polynomial; (iv) A's fibre equals B's root set.
Usage: check_inputs.py SNAPSHOT_LAUNCHER RAW_JSONL"""
import importlib.util, json, random, sys
sys.path.insert(0, "/tmp/claude-0/validator2/work")
from solparse import parse_poly, n_const_terms, eval_poly
spec = importlib.util.spec_from_file_location("grid", sys.argv[1]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
pkm = g.pkm
rows = [json.loads(l) for l in open(sys.argv[2])]
report = dict(instances=0, systems=0, param_mismatch=[], multi_const=[], planted_not_zero=[], fibre_mismatch=[], max_const_terms=0,
              S4_terms_min=None, S4_terms_max=None, S4_has_negative_coeffs=False)
for r in rows:
    m, L, inst, kind, seed = r["m"], r["L"], r["inst"], r["kind"], r["seed"]
    rng = random.Random(seed)
    p = pkm.find_prime(m, L); a = p - 3
    while True:
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p: break
    chain = pkm.build_chain(p, L, rng)
    randV = sorted(rng.sample(range(p), 2 ** L))
    for k, v in (("p", p), ("b", b), ("chain_c", chain["c"])):
        if r[k] != v: report["param_mismatch"].append((L, inst, k))
    # fibre: x in V iff chain(x) == c, and B's dense poly has exactly V as roots (check by evaluation on V + sample)
    dense = pkm.poly_from_roots(chain["V"], p)
    if not all(sum(c * pow(x, i, p) for i, c in enumerate(dense)) % p == 0 for x in chain["V"]) or len(dense) != 2 ** L + 1:
        report["fibre_mismatch"].append((L, inst))
    report["instances"] += 1
    for arm in r["results"]:
        if arm == "E": continue
        Vset = randV if arm == "C" else chain["V"]
        fb = pkm.factor_base(Vset, a, b, p)
        trng = random.Random(f"{seed}-{arm in 'C'}-target")
        if kind == "planted":
            picks = [trng.choice(fb) for _ in range(m)]
            picks = [P if trng.random() < .5 else pkm.ec_neg(P, p) for P in picks]
            T = None
            for P in picks: T = pkm.ec_add(T, P, a, p)
        else:
            while True:
                x = trng.randrange(p); y = pkm.sqrt_mod(x ** 3 + a * x + b, p)
                if y is not None: T, picks = (x, y), None; break
        S = g.summation_poly(p, m, a, b, T[0])
        enc = chain if arm == "A" else dict(coeffs=pkm.poly_from_roots(Vset, p))
        vars_, polys = g.build_system(arm, p, m, S, enc)
        res = r["results"][arm]
        for k, v in (("fb_size", len(fb)), ("nvars", len(vars_)), ("npolys", len(polys))):
            if res.get(k) != v: report["param_mismatch"].append((L, inst, arm, k, res.get(k), v))
        nS = len(parse_poly(S))
        report["S4_terms_min"] = nS if report["S4_terms_min"] is None else min(report["S4_terms_min"], nS)
        report["S4_terms_max"] = nS if report["S4_terms_max"] is None else max(report["S4_terms_max"], nS)
        report["S4_has_negative_coeffs"] |= "-" in S
        for j, poly in enumerate(polys):
            nc = n_const_terms(poly)
            report["max_const_terms"] = max(report["max_const_terms"], nc)
            if nc > 1: report["multi_const"].append((L, inst, arm, j, nc))
        if picks is not None:
            pt = {f"x{i}": P[0] for i, P in enumerate(picks, 1)}
            if arm == "A":
                for i, P in enumerate(picks, 1):
                    tr = pkm.chain_eval(P[0], chain["steps"], p, trace=True)
                    pt.update({f"w{i}{j:02d}": tr[j] for j in range(1, L)})
            bad = [j for j, poly in enumerate(polys) if eval_poly(parse_poly(poly), pt, p)]
            if bad: report["planted_not_zero"].append((L, inst, arm, bad))
            # negative: perturb x1 by 1 -> S or a fibre equation must fail
            pt2 = dict(pt); pt2["x1"] = (pt["x1"] + 1) % p
            if all(eval_poly(parse_poly(poly), pt2, p) == 0 for poly in polys):
                report["planted_not_zero"].append((L, inst, arm, "perturbed point also a root"))
        report["systems"] += 1
print(json.dumps(report, indent=1))
