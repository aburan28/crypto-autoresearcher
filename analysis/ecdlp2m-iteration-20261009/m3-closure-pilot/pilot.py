#!/usr/bin/env python3
"""pilot.py -- PILOT (m3closure). EXPLORATORY, hypothesis-generating; not program
evidence. Bounded-degree refutation of chained S_3 (m = 3, t = 3) descents.

usage: pilot.py label  <n> <vtype> <ntargets>          -> instances/<cell>.json
       pilot.py run    <cell> <tasks> <workers> <memgb> [--sel unsat:U,sat:S,null:K] [--timeout s]
       pilot.py m2ctrl <ntargets>                       -> instances/m2ctrl.json

Results are appended to results/<cell>.jsonl (one line per instance x task).
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot_lib as L  # noqa: E402

INST = HERE / "instances"
RES = HERE / "results"
JOBS = HERE / "jobs"
for d in (INST, RES, JOBS):
    d.mkdir(exist_ok=True)


def label(n, vtype, ntargets, curve_seed=0, target_seed=0):
    import random
    cv = L.pick_curve(n, curve_seed)
    k = -(-n // 3)
    if vtype == "poly":
        basis = [1 << j for j in range(k)]
    else:
        basis = L.boolsys.random_subspace(random.Random(L.boolsys.derive_seed("m3closure-V", n, k)), n, k)
    V = L.VSpace(cv["F"], basis)
    zs = L.subgroup_targets(cv, ntargets, target_seed)
    insts = []
    seen = set()
    for i, z in enumerate(zs):
        dup = z in seen
        seen.add(z)
        t0 = time.time()
        sols = L.curve_solutions(cv["F"], V, cv["b"], z)
        t1 = time.time()
        sysm = L.build_chain3(n, k, basis, cv["b"], z, cv["modulus"])
        cnt, bsols = L.boolean_count_chain3(sysm)
        t2 = time.time()
        evals_ok = all(not any(L.eval_system(sysm["equations"], s)) for s in sols[:256])
        agree = (cnt == len(sols)) and (sorted(bsols) == sols[:len(bsols)] if cnt <= 4096 else True)
        insts.append({"id": f"n{n}-{vtype}-S3-{i:04d}", "family": "S3", "n": n, "k": k, "N": sysm["N"],
                      "vtype": vtype, "z": z, "dup_target": dup, "nsol": len(sols), "nsol_boolean": cnt,
                      "enum_agree": bool(agree), "eval_ok": bool(evals_ok), "solutions": sols[:256],
                      "enum_curve_s": t1 - t0, "enum_bool_s": t2 - t1})
    cell = {"n": n, "k": k, "vtype": vtype, "basis": basis, "modulus": cv["modulus"], "a": cv["a"], "b": cv["b"],
            "order": cv["order"], "q": cv["q"], "h": cv["h"], "curve_tries": cv["tries"], "instances": insts}
    name = f"n{n}-{vtype}"
    json.dump(cell, open(INST / f"{name}.json", "w"))
    ns = sum(1 for x in insts if x["nsol"] == 0)
    print(f"{name}: q={cv['q']} b={cv['b']} targets={len(insts)} unsat={ns} sat={len(insts)-ns} "
          f"enum_disagree={sum(not x['enum_agree'] for x in insts)} eval_fail={sum(not x['eval_ok'] for x in insts)}")


def make_nulls(cell, count):
    """Support-matched nulls from the first `count` S3 instances; labelled exhaustively."""
    out = []
    n, k = cell["n"], cell["k"]
    for x in cell["instances"][:count]:
        sysm = L.build_chain3(n, k, cell["basis"], cell["b"], x["z"], cell["modulus"])
        nl = L.support_null(sysm, x["id"])
        cnt, bs = L.boolean_count_chain3(nl)
        assert all(not any(L.eval_system(nl["equations"], s)) for s in bs)
        out.append({"id": x["id"].replace("-S3-", "-NULL-"), "family": "NULL", "n": n, "k": k, "N": nl["N"],
                    "vtype": cell["vtype"], "z": x["z"], "nsol": cnt, "solutions": bs[:256],
                    "equations": nl["equations"]})
    return out


def make_nulls2(cell, count):
    """Dense matched null (vendored boolsys.matched_null: same N, same number of
    monomials of each degree per equation, monomials uniform). Labelled by
    exhaustive evaluation over all 2^N points (count_affu with no u-variables);
    feasible only for small N."""
    out = []
    n, k = cell["n"], cell["k"]
    for i, x in enumerate(cell["instances"][:count]):
        sysm = L.build_chain3(n, k, cell["basis"], cell["b"], x["z"], cell["modulus"])
        fake = {"N": sysm["N"], "equations": sysm["equations"], "seed": 0, "draw": i,
                "var_names": [f"v{j}" for j in range(sysm["N"])], "n": n, "m": 3, "t": 3, "k": k}
        nl = L.boolsys.matched_null(fake, 1)
        cnt, bs = L.boolean_count_m2({"N": nl["N"], "equations": nl["equations"]})
        assert all(not any(L.eval_system(nl["equations"], s)) for s in bs)
        out.append({"id": x["id"].replace("-S3-", "-NULL2-"), "family": "NULL2", "n": n, "k": k, "N": nl["N"],
                    "vtype": cell["vtype"], "z": x["z"], "nsol": cnt, "solutions": bs[:256],
                    "equations": nl["equations"]})
    return out


def m2ctrl(ntargets):
    """Positive control: the KN-FIND-5a8d3e cell (n=17, t^17+t^3+1, A=97044,
    B=126251, #E = 4*32603, V = deg < 9, x(2E) targets), m = 2."""
    n, k, mod, A, B = 17, 9, (1 << 17) | (1 << 3) | 1, 97044, 126251
    F = L.Field(n, mod)
    E = L.Curve(F, A, B)
    order = E.count_points()
    import random
    rng = random.Random(L.boolsys.derive_seed("m3closure-m2ctrl", ntargets))
    basis = [1 << j for j in range(k)]
    V = L.VSpace(F, basis)
    insts = []
    while len(insts) < ntargets:
        x = rng.randrange(1, 1 << n)
        P = E.lift_x(x)
        if P is None:
            continue
        R = E.dbl(P)
        if R is None:
            continue
        z = R[0]
        sols = L.m2_solutions(F, V, B, z)
        sysm = L.build_m2(n, k, basis, B, z, mod)
        cnt, bs = L.boolean_count_m2(sysm)
        insts.append({"id": f"m2ctrl-{len(insts):04d}", "family": "M2CTRL", "n": n, "k": k, "N": 2 * k,
                      "vtype": "poly", "z": z, "nsol": len(sols), "nsol_boolean": cnt,
                      "enum_agree": cnt == len(sols) and sorted(bs) == sols, "solutions": sols,
                      "equations": sysm["equations"]})
    cell = {"n": n, "k": k, "vtype": "poly", "basis": basis, "modulus": mod, "a": A, "b": B, "order": order,
            "instances": insts}
    json.dump(cell, open(INST / "m2ctrl.json", "w"))
    print("m2ctrl: #E", order, "unsat", sum(x["nsol"] == 0 for x in insts), "sat", sum(x["nsol"] > 0 for x in insts),
          "enum_disagree", sum(not x["enum_agree"] for x in insts))


def run_job(inst, eqs, kind, D, memgb, timeout, tag):
    job = {"N": inst["N"], "equations": eqs, "kind": kind, "D": D, "mem_cap_gb": memgb,
           "witnesses": inst["solutions"][:64],
           "evalcheck": bool(inst["solutions"]) and kind in ("W", "M")}
    jp = JOBS / f"{tag}.json"
    op = JOBS / f"{tag}.out.json"
    lp = JOBS / f"{tag}.log"
    json.dump(job, open(jp, "w"))
    t0 = time.time()
    try:
        with open(lp, "w") as lf:
            r = subprocess.run([sys.executable, str(HERE / "worker.py"), str(jp), str(op)],
                               stdout=lf, stderr=lf, timeout=timeout)
        rc = r.returncode
        o = json.load(open(op)) if rc == 0 else {"status": f"worker_rc{rc}"}
    except subprocess.TimeoutExpired:
        o = {"status": "censored_timeout"}
    o["outer_wall_s"] = time.time() - t0
    # evalcheck log: count elimination lines flagged
    try:
        txt = open(lp).read()
        o["evalcheck_flagged_lines"] = txt.count("***")
        o["ech_check_faults_log"] = txt.count("[ech check]")
    except OSError:
        pass
    for p in (jp, op):
        try:
            p.unlink()
        except OSError:
            pass
    if o.get("evalcheck_flagged_lines", 0) == 0 and o.get("ech_check_faults_log", 0) == 0 and not os.environ.get("KEEP_LOGS"):
        try:
            lp.unlink()
        except OSError:
            pass
    return o


def run(cellname, tasks, workers, memgb, sel=None, timeout=1200, cell_file=None):
    cell = json.load(open(INST / f"{cell_file or cellname}.json"))
    insts = cell["instances"]
    n, k = cell["n"], cell["k"]
    pool = []
    if cellname == "m2ctrl":
        pool = insts
    else:
        sel = sel or {}
        U = [x for x in insts if x["nsol"] == 0 and not x["dup_target"]][: sel.get("unsat", 10**9)]
        S = [x for x in insts if x["nsol"] > 0 and not x["dup_target"]][: sel.get("sat", 10**9)]
        pool = U + S
        if sel.get("null"):
            nf = INST / f"{cellname}-nulls.json"
            nulls = json.load(open(nf)) if nf.exists() else []
            if len(nulls) < sel["null"]:
                nulls = make_nulls(cell, sel["null"])
                json.dump(nulls, open(nf, "w"))
            pool = pool + nulls[: sel["null"]]
        if sel.get("null2"):
            nf = INST / f"{cellname}-nulls2.json"
            nulls2 = json.load(open(nf)) if nf.exists() else []
            if len(nulls2) < sel["null2"]:
                nulls2 = make_nulls2(cell, sel["null2"])
                json.dump(nulls2, open(nf, "w"))
            pool = pool + nulls2[: sel["null2"]]
        if sel.get("nullonly"):
            pool = [x for x in pool if x["family"] in ("NULL", "NULL2")]
    outp = RES / f"{cellname}.jsonl"
    done = set()
    if outp.exists():
        for line in open(outp):
            r = json.loads(line)
            done.add((r["id"], r["kind"], r["D"]))
    todo = []
    for x in pool:
        for t in tasks:
            kind, D = t[:-1], int(t[-1])
            if (x["id"], kind, D) in done:
                continue
            todo.append((x, kind, D))

    def one(item):
        x, kind, D = item
        if "equations" in x:
            eqs = x["equations"]
        else:
            eqs = L.build_chain3(n, k, cell["basis"], cell["b"], x["z"], cell["modulus"])["equations"]
        tag = f"{x['id']}-{kind}{D}"
        o = run_job(x, eqs, kind, D, memgb, timeout, tag)
        row = {"id": x["id"], "family": x["family"], "n": n, "k": k, "N": x["N"], "vtype": x["vtype"],
               "z": x["z"], "nsol": x["nsol"], "kind": kind, "D": D, "mem_cap_gb": memgb, **o}
        return row

    print(f"{cellname}: {len(todo)} jobs, workers={workers}", flush=True)
    with ThreadPoolExecutor(workers) as ex, open(outp, "a") as f:
        for row in ex.map(one, todo):
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"  {row['id']} {row['kind']}{row['D']} nsol={row['nsol']} {row.get('status')} "
                  f"one={row.get('contains_one')} rank={row.get('rank')} cols={row.get('ncols')} "
                  f"wall={row.get('wall_s', row.get('outer_wall_s')):.1f}s rss={row.get('peak_rss_mb', 0):.0f}MB", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "label":
        label(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
    elif cmd == "m2ctrl":
        m2ctrl(int(sys.argv[2]))
    elif cmd == "run":
        cellname, tasks, workers, memgb = sys.argv[2], sys.argv[3].split(","), int(sys.argv[4]), float(sys.argv[5])
        sel, timeout = {}, 1200
        args = sys.argv[6:]
        i = 0
        while i < len(args):
            if args[i] == "--sel":
                for kv in args[i + 1].split(","):
                    kk, vv = kv.split(":")
                    sel[kk] = int(vv)
                i += 2
            elif args[i] == "--timeout":
                timeout = int(args[i + 1]); i += 2
            else:
                raise SystemExit(f"bad arg {args[i]}")
        run(cellname, tasks, workers, memgb, sel, timeout)
