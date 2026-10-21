#!/usr/bin/env python3
"""pilot2.py -- PILOT #2 (m45closure). EXPLORATORY, hypothesis-generating; not
program evidence. Bounded-degree closure refutation of chained S_3 descents with
chain length t = m in {4, 5} (pilot #1 did m = 3).

usage: pilot2.py label <m> <n> <ntargets>                  -> instances/m{m}-n{n}.json
       pilot2.py run <cell> <tasks> <workers> <memgb> [--sel unsat:U,sat:S,null:K,null2:K,nullonly:1] [--timeout s]
       pilot2.py export                                     -> data.csv, aggregate.md
Results are appended to results/<cell>.jsonl (one line per instance x task).
Cell naming: m{m}-n{n}; V = polynomial basis deg < k, k = ceil(n/m).
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
import pilot2_lib as P  # noqa: E402

INST = HERE / "instances"
RES = HERE / "results"
JOBS = HERE / "jobs"
for d in (INST, RES, JOBS):
    d.mkdir(exist_ok=True)

DENSE_ENUM_MAX_N = 24


def label(m, n, ntargets, curve_seed=0, target_seed=0, k=None):
    cv = L.pick_curve(n, curve_seed)
    kdef = -(-n // m)
    name = f"m{m}-n{n}" if k is None or k == kdef else f"m{m}-n{n}k{k}"
    k = k or kdef
    basis = [1 << j for j in range(k)]
    V = L.VSpace(cv["F"], basis)
    zs = L.subgroup_targets(cv, ntargets, target_seed)
    insts, seen = [], set()
    for i, z in enumerate(zs):
        dup = z in seen
        seen.add(z)
        t0 = time.time()
        sols = P.chain_solutions(cv["F"], V, cv["b"], z, m)
        t1 = time.time()
        sysm = P.build_chain(n, k, m, basis, cv["b"], z, cv["modulus"])
        cnt, bsols = P.boolean_count_chain(sysm)
        t2 = time.time()
        evals_ok = all(not any(L.eval_system(sysm["equations"], s)) for s in sols[:256])
        agree = (cnt == len(sols)) and (bsols == sols[:len(bsols)])
        pc = [P.point_check(cv, V, m, s, z) for s in sols[:4]]
        degs = sorted(set(max(bin(mm).count("1") for mm in e) for e in sysm["equations"] if e))
        insts.append({"id": f"{name}-S3-{i:04d}", "family": "S3", "m": m, "n": n, "k": k, "N": sysm["N"],
                      "neq": len(sysm["equations"]), "gen_degrees": degs,
                      "vtype": "poly", "z": z, "dup_target": dup, "nsol": len(sols), "nsol_boolean": cnt,
                      "enum_agree": bool(agree), "eval_ok": bool(evals_ok),
                      "point_check": pc, "solutions": sols[:256],
                      "enum_curve_s": t1 - t0, "enum_bool_s": t2 - t1})
    cell = {"m": m, "n": n, "k": k, "vtype": "poly", "basis": basis, "modulus": cv["modulus"], "a": cv["a"], "b": cv["b"],
            "order": cv["order"], "q": cv["q"], "h": cv["h"], "curve_tries": cv["tries"], "instances": insts}
    json.dump(cell, open(INST / f"{name}.json", "w"))
    ns = sum(1 for x in insts if x["nsol"] == 0 and not x["dup_target"])
    nsat = sum(1 for x in insts if x["nsol"] > 0 and not x["dup_target"])
    pcs = [v for x in insts for v in x["point_check"]]
    print(f"{name}: N={insts[0]['N']} neq={insts[0]['neq']} q={cv['q']} b={cv['b']} targets={len(insts)} "
          f"unsat={ns} sat={nsat} dups={sum(x['dup_target'] for x in insts)} "
          f"enum_disagree={sum(not x['enum_agree'] for x in insts)} eval_fail={sum(not x['eval_ok'] for x in insts)} "
          f"point_check={sum(pcs)}/{len(pcs)} gen_degs={insts[0]['gen_degrees']} "
          f"enum_s(curve,bool)=({sum(x['enum_curve_s'] for x in insts):.1f},{sum(x['enum_bool_s'] for x in insts):.1f})")


def make_nulls(cell, count):
    """Support-matched nulls (same monomials, i.i.d. coefficients) from the first
    UNSAT S3 instances; labelled exhaustively by count_chain (block structure kept)."""
    out = []
    m, n, k = cell["m"], cell["n"], cell["k"]
    src = [x for x in cell["instances"] if not x["dup_target"]][:count]
    for x in src:
        sysm = P.build_chain(n, k, m, cell["basis"], cell["b"], x["z"], cell["modulus"])
        nl = P.support_null(sysm, x["id"])
        cnt, bs = P.boolean_count_chain(nl)
        assert all(not any(L.eval_system(nl["equations"], s)) for s in bs)
        out.append({"id": x["id"].replace("-S3-", "-NULL-"), "family": "NULL", "m": m, "n": n, "k": k, "N": nl["N"],
                    "vtype": "poly", "z": x["z"], "nsol": cnt, "label": "enumerated", "solutions": bs[:256],
                    "equations": nl["equations"]})
    return out


def make_nulls2(cell, count):
    """Dense matched null (boolsys.matched_null: same N, same monomial count per
    degree per equation, uniform monomials). Labelled exhaustively only when
    N <= DENSE_ENUM_MAX_N; otherwise label = 'unenumerated' and the expected
    number of solutions 2^(N - neq) of a uniformly random system is recorded."""
    out = []
    m, n, k = cell["m"], cell["n"], cell["k"]
    src = [x for x in cell["instances"] if not x["dup_target"]][:count]
    for i, x in enumerate(src):
        sysm = P.build_chain(n, k, m, cell["basis"], cell["b"], x["z"], cell["modulus"])
        nl = P.dense_null(sysm, f"m45closure-{x['id']}", i)
        if nl["N"] <= DENSE_ENUM_MAX_N:
            cnt, bs = P.boolean_count_dense(nl)
            assert all(not any(L.eval_system(nl["equations"], s)) for s in bs)
            lab = "enumerated"
        else:
            cnt, bs, lab = -1, [], "unenumerated"
        out.append({"id": x["id"].replace("-S3-", "-NULL2-"), "family": "NULL2", "m": m, "n": n, "k": k, "N": nl["N"],
                    "vtype": "poly", "z": x["z"], "nsol": cnt, "label": lab,
                    "expected_nsol_random": 2.0 ** (nl["N"] - len(nl["equations"])),
                    "solutions": bs[:256], "equations": nl["equations"]})
    return out


def run_job(inst, eqs, kind, D, memgb, timeout, tag):
    job = {"N": inst["N"], "equations": eqs, "kind": kind, "D": D, "mem_cap_gb": memgb,
           "witnesses": inst["solutions"][:64],
           "evalcheck": bool(inst["solutions"]) and kind in ("W", "M")}
    jp, op, lp = JOBS / f"{tag}.json", JOBS / f"{tag}.out.json", JOBS / f"{tag}.log"
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
    try:
        txt = open(lp).read()
        o["evalcheck_flagged_lines"] = txt.count("***")
        o["ech_check_faults_log"] = txt.count("[ech check]")
        if o["status"] != "completed":
            o["log_tail"] = txt[-600:]
    except OSError:
        pass
    for p in (jp, op):
        try:
            p.unlink()
        except OSError:
            pass
    if o.get("evalcheck_flagged_lines", 0) == 0 and o.get("ech_check_faults_log", 0) == 0 and o["status"] == "completed" and not os.environ.get("KEEP_LOGS"):
        try:
            lp.unlink()
        except OSError:
            pass
    return o


def run(cellname, tasks, workers, memgb, sel=None, timeout=1200):
    cell = json.load(open(INST / f"{cellname}.json"))
    insts = cell["instances"]
    m, n, k = cell["m"], cell["n"], cell["k"]
    sel = sel or {}
    U = [x for x in insts if x["nsol"] == 0 and not x["dup_target"]][: sel.get("unsat", 10**9)]
    S = [x for x in insts if x["nsol"] > 0 and not x["dup_target"]][: sel.get("sat", 10**9)]
    pool = U + S
    for key, maker, suffix in (("null", make_nulls, "-nulls.json"), ("null2", make_nulls2, "-nulls2.json")):
        if sel.get(key):
            nf = INST / f"{cellname}{suffix}"
            nulls = json.load(open(nf)) if nf.exists() else []
            if len(nulls) < sel[key]:
                nulls = maker(cell, sel[key])
                json.dump(nulls, open(nf, "w"))
            pool = pool + nulls[: sel[key]]
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
        eqs = x["equations"] if "equations" in x else P.build_chain(n, k, m, cell["basis"], cell["b"], x["z"], cell["modulus"])["equations"]
        tag = f"{x['id']}-{kind}{D}"
        o = run_job(x, eqs, kind, D, memgb, timeout, tag)
        row = {"id": x["id"], "family": x["family"], "m": m, "n": n, "k": k, "N": x["N"], "vtype": "poly",
               "z": x["z"], "nsol": x["nsol"], "label": x.get("label", "enumerated"), "kind": kind, "D": D,
               "mem_cap_gb": memgb, "timeout_s": timeout, "nworkers": workers, **o}
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
        label(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), k=(int(sys.argv[5]) if len(sys.argv) > 5 else None))
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
    else:
        raise SystemExit("export is in export.py")
