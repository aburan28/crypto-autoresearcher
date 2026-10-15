#!/usr/bin/env python3
"""Compare the validator re-run with RUN-ECDLP-502ae2-01 and post-check kept msolve outputs with independent parsers.
Usage: postcheck.py SNAPSHOT_LAUNCHER ORIG_RAW RERUN_DIR"""
import importlib.util, json, os, random, sys
sys.path.insert(0, "/tmp/claude-0/validator2/work")
from solparse import parse_poly, eval_poly, gb_polys, parse_sol, poly_roots_fp
spec = importlib.util.spec_from_file_location("grid", sys.argv[1]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
pkm = g.pkm
orig = {(r["L"], r["inst"]): r for r in map(json.loads, open(sys.argv[2]))}
rer = [json.loads(l) for l in open(os.path.join(sys.argv[3], "rerun-raw.jsonl"))]
DET = ("fb_size", "nvars", "npolys", "gb_status", "solve_status", "status", "f4_max_deg", "quotient_dim", "planted_in_variety")
out = dict(deterministic_mismatches=[], timing=[], gb_checks=[], sol_checks=[])
for r in rer:
    o = orig[(r["L"], r["inst"])]
    for k in ("seed", "p", "b", "chain_c"):
        if r[k] != o[k]: out["deterministic_mismatches"].append((r["L"], r["inst"], k))
    for arm, v in r["results"].items():
        ov = o["results"][arm]
        for k in DET:
            if v.get(k) != ov.get(k): out["deterministic_mismatches"].append((r["L"], r["inst"], arm, k, ov.get(k), v.get(k)))
        out["timing"].append(dict(L=r["L"], inst=r["inst"], arm=arm, kind=r["kind"], gb_orig=ov.get("gb_wall_s"), gb_rerun=v.get("gb_wall_s"),
                                  solve_orig=ov.get("solve_wall_s"), solve_rerun=v.get("solve_wall_s"),
                                  gb_ratio=round(v["gb_wall_s"] / ov["gb_wall_s"], 3), solve_ratio=round(v["solve_wall_s"] / ov["solve_wall_s"], 3)))
    # rebuild planted point
    rng = random.Random(r["seed"]); p = r["p"]; a = p - 3
    while True:
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p: break
    chain = pkm.build_chain(p, r["L"], rng)
    d = os.path.join(sys.argv[3], "files", f"L{r['L']}-inst{r['inst']}")
    for f in sorted(x for x in os.listdir(d) if x.endswith(".ms")):
        vars_ = open(os.path.join(d, f)).readline().strip().split(",")
        arm = "A" if any(v.startswith("w") for v in vars_) else "B"
        trng = random.Random(f"{r['seed']}-False-target")
        fb = pkm.factor_base(chain["V"], a, b, p)
        pt = None
        if r["kind"] == "planted":
            picks = [trng.choice(fb) for _ in range(3)]
            picks = [P if trng.random() < .5 else pkm.ec_neg(P, p) for P in picks]
            pt = {f"x{i}": P[0] for i, P in enumerate(picks, 1)}
            if arm == "A":
                for i, P in enumerate(picks, 1):
                    tr = pkm.chain_eval(P[0], chain["steps"], p, trace=True)
                    pt.update({f"w{i}{j:02d}": tr[j] for j in range(1, r["L"])})
        gbt = open(os.path.join(d, f + ".gb")).read()
        G = gb_polys(gbt)
        rec = dict(L=r["L"], inst=r["inst"], arm=arm, kind=r["kind"], gb_len=len(G), gb_is_one=(G == ["1"]))
        if pt:
            rec["planted_zero_on_all_gb"] = all(eval_poly(parse_poly(q), pt, p) == 0 for q in G)
            pt2 = dict(pt); pt2["x1"] = (pt["x1"] + 1) % p
            rec["perturbed_rejected"] = any(eval_poly(parse_poly(q), pt2, p) for q in G)
            rec["producer_eval_gb_at"] = g.eval_gb_at(gbt, pt, p)
        out["gb_checks"].append(rec)
        sol = parse_sol(open(os.path.join(d, f + ".sol")).read())
        srec = dict(L=r["L"], inst=r["inst"], arm=arm, kind=r["kind"])
        if sol == [-1]:
            srec["result"] = "no_solution"
        else:
            body = sol[1]
            svars, deg, w, params = body[3], body[2], body[5][1][0][1], body[5][1][2]
            srec.update(result="param", vars_added=[v for v in svars if v not in vars_], elim_deg=len(w) - 1, deg_field=deg)
            if pt:
                ts = poly_roots_fp(w, p)
                found = []
                for t in ts:
                    xs = {svars[i]: (-sum(c * pow(t, k, p) for k, c in enumerate(pp[0][1]))) % p for i, pp in enumerate(params)}
                    xs[svars[-1]] = t
                    found.append(all(xs[k] == v for k, v in pt.items() if k in xs))
                srec.update(fp_roots_of_elim=len(ts), planted_recovered=any(found))
        out["sol_checks"].append(srec)
print(json.dumps(out, indent=1))
