#!/usr/bin/env python3
"""pilot3.py -- PILOT #3 (block-local closure). EXPLORATORY, hypothesis-generating;
not program evidence. Measures the degree-4 mutant closure W_4 restricted to
block-local monomials (locality L <= Lmax) against the full W_4 on the SAME
labelled instances as pilots #1 and #2 (instances/*.json are byte-identical
copies; PROVENANCE.sha256).

usage: pilot3.py run <cell> <variants> <memgb> [--sel unsat:U,sat:S] [--timeout s] [--D 4]
  cell     n9-poly | n11-poly (m = 3, pilot #1) | m4-n7 | m4-n9 (pilot #2)
  variants comma list of  full | L1 | L2 | L3 | adj0 | adj1 | L1adj0 | L2adj1 ...
           L<k>   : columns = monomials of locality <= k (products with a
                    non-local monomial are dropped as a whole)
           adj<r> : multiply a row only by variables whose block interval meets
                    the row's block window widened by r on each side
           full   : no filter (Lmax = number of blocks, adj = -1) == W_D
Rows are appended to results/<cell>.jsonl (one per instance x variant); a
(id, variant, D) already present is skipped.

Variable blocks (chained S_3, boolsys.generate layout u_0..u_{m-3}, x_0..x_{m-1}):
  B_0 = (u_0, x_0, x_1); B_i = (u_{i-1}, u_i, x_{i+1}), i = 1..m-3; B_{m-2} = (u_{m-3}, x_{m-1}).
  u_i lies in blocks [i, i+1]; x_0, x_1 in block 0; x_j (j >= 2) in block j-1.
Every generator (one Boolean equation of one S_3 block) has locality 1.
"""
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
import boolsys  # noqa: E402

INST = HERE / "instances"
RES = HERE / "results"
JOBS = HERE / "jobs"
for d in (RES, JOBS):
    d.mkdir(exist_ok=True)


def build_chain(n, k, m, basis, b, z, modulus):
    """Identical to pilot #2 pilot2_lib.build_chain (and to pilot #1 build_chain3 at m = 3;
    checked equal on n9-poly instance 0 before this pilot ran)."""
    assert m >= 3
    F = boolsys.GF2n(n, modulus)
    N = (m - 2) * n + m * k
    U = [boolsys.linear_form([1 << j for j in range(n)], i * n) for i in range(m - 2)]
    X = [boolsys.linear_form(basis, (m - 2) * n + i * k) for i in range(m)]
    zc = {0: z} if z else {}
    polys = [boolsys.s3(F, U[0], X[0], X[1], b)]
    for i in range(1, m - 2):
        polys.append(boolsys.s3(F, U[i - 1], U[i], X[i + 1], b))
    polys.append(boolsys.s3(F, U[m - 3], X[m - 1], zc, b))
    eqs = []
    for p in polys:
        eqs += boolsys.descend(p, n)
    return {"N": N, "equations": eqs, "n": n, "k": k, "m": m}


def blocks(n, k, m):
    """lo[j], hi[j]: block interval of Boolean variable j. nblocks = m - 1."""
    N = (m - 2) * n + m * k
    lo = [0] * N; hi = [0] * N
    for i in range(m - 2):
        for j in range(i * n, (i + 1) * n):
            lo[j], hi[j] = i, i + 1
    for jx in range(m):
        blk = 0 if jx <= 1 else jx - 1
        for j in range((m - 2) * n + jx * k, (m - 2) * n + (jx + 1) * k):
            lo[j], hi[j] = blk, blk
    return lo, hi, m - 1


def locality(mask, lo, hi):
    A = min((hi[j] for j in range(len(lo)) if mask >> j & 1), default=0)
    B = max((lo[j] for j in range(len(lo)) if mask >> j & 1), default=0)
    return max(1, B - A + 1)


def parse_variant(v, nblocks):
    Lmax, adj = nblocks, -1
    if v == "full":
        return Lmax, adj
    s = v
    if s.startswith("L"):
        num = ""
        s = s[1:]
        while s and s[0].isdigit():
            num += s[0]; s = s[1:]
        Lmax = int(num)
    if s.startswith("adj"):
        adj = int(s[3:]); s = ""
    if s:
        raise SystemExit(f"bad variant {v}")
    return Lmax, adj


def run_job(inst, eqs, D, lo, hi, Lmax, adj, memgb, timeout, tag):
    job = {"N": inst["N"], "equations": eqs, "D": D, "lo": lo, "hi": hi, "Lmax": Lmax, "adj": adj,
           "stop_at_one": 1, "witnesses": inst["solutions"][:16]}
    jp, op = JOBS / f"{tag}.json", JOBS / f"{tag}.out.json"
    json.dump(job, open(jp, "w"))
    t0 = time.time()
    lim = int(memgb * (1 << 30))

    def pre():
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    try:
        r = subprocess.run([sys.executable, str(HERE / "worker3.py"), str(jp), str(op)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout, preexec_fn=pre)
        rc = r.returncode
        o = json.load(open(op)) if rc == 0 else {"status": f"worker_rc{rc}", "stderr_tail": r.stderr.decode(errors="replace")[-300:]}
    except subprocess.TimeoutExpired:
        o = {"status": "censored_timeout"}
    o["outer_wall_s"] = time.time() - t0
    for p in (jp, op):
        try:
            p.unlink()
        except OSError:
            pass
    return o


def run(cellname, variants, memgb, sel=None, timeout=1200, D=4):
    cell = json.load(open(INST / f"{cellname}.json"))
    insts = cell["instances"]
    m = cell.get("m", 3); n, k = cell["n"], cell["k"]
    sel = sel or {}
    U = [x for x in insts if x["nsol"] == 0 and not x["dup_target"]][: sel.get("unsat", 10**9)]
    S = [x for x in insts if x["nsol"] > 0 and not x["dup_target"]][: sel.get("sat", 10**9)]
    pool = U + S
    lo, hi, nb = blocks(n, k, m)
    outp = RES / f"{cellname}.jsonl"
    done = set()
    if outp.exists():
        for line in open(outp):
            r = json.loads(line)
            done.add((r["id"], r["variant"], r["D"]))
    todo = [(x, v) for x in pool for v in variants if (x["id"], v, D) not in done]
    print(f"{cellname}: m={m} n={n} k={k} N={(m-2)*n+m*k} blocks={nb} jobs={len(todo)}", flush=True)
    with open(outp, "a") as f:
        for x, v in todo:
            Lmax, adj = parse_variant(v, nb)
            sysm = build_chain(n, k, m, cell["basis"], cell["b"], x["z"], cell["modulus"])
            eqs = sysm["equations"]
            assert sysm["N"] == x["N"]
            gl = max(locality(mm, lo, hi) for e in eqs for mm in e)
            assert gl == 1, gl
            o = run_job(x, eqs, D, lo, hi, Lmax, adj, memgb, timeout, f"{x['id']}-{v}")
            row = {"id": x["id"], "family": x["family"], "m": m, "n": n, "k": k, "N": x["N"], "nblocks": nb,
                   "z": x["z"], "nsol": x["nsol"], "label": "UNSAT" if x["nsol"] == 0 else "SAT",
                   "variant": v, "Lmax": Lmax, "adj": adj, "D": D, "mem_cap_gb": memgb, "timeout_s": timeout, **o}
            if row.get("status") == "completed":
                row["codim"] = row["ncols"] - row["rank"]
                row["false_refutation"] = bool(row["contains_one"] and x["nsol"] > 0)
                if row["false_refutation"] or any(row.get("eval_rows_not_vanishing", [])):
                    f.write(json.dumps(row) + "\n"); f.flush()
                    raise SystemExit(f"SOUNDNESS FAULT on {x['id']} {v}: {row}")
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"  {x['id']} {v} {row['label']} nsol={x['nsol']} {row.get('status')} one={row.get('contains_one')} "
                  f"cols={row.get('ncols')} rank={row.get('rank')} rows={row.get('rows')} drop={row.get('products_dropped')} "
                  f"wall={row.get('wall_s', row.get('outer_wall_s')):.1f}s rss={row.get('peak_rss_mb', 0):.0f}MB", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd != "run":
        raise SystemExit(__doc__)
    cellname, variants, memgb = sys.argv[2], sys.argv[3].split(","), float(sys.argv[4])
    sel, timeout, D = {}, 1200, 4
    args = sys.argv[5:]
    i = 0
    while i < len(args):
        if args[i] == "--sel":
            for kv in args[i + 1].split(","):
                kk, vv = kv.split(":")
                sel[kk] = int(vv)
            i += 2
        elif args[i] == "--timeout":
            timeout = int(args[i + 1]); i += 2
        elif args[i] == "--D":
            D = int(args[i + 1]); i += 2
        else:
            raise SystemExit(f"bad arg {args[i]}")
    run(cellname, variants, memgb, sel, timeout, D)
