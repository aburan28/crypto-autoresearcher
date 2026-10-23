#!/usr/bin/env python3
"""run_trimoska.py -- m4-sat-cost-pilot. EXPLORATORY; not program evidence.

Solver-build control: runs the pilot's patched WDSat build on the published
Trimoska-Ionica-Dequen S_4 (m = 3) benchmark instances vendored in the repository
(inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/Xn{n}l{l}-{i}-{S,U}.anf) with the
paper's two configurations, so the 2^(3l)/3! law (ctrial-harvest) can be checked on
the exact objects it was derived from. This validates the build and the counter
patch, not the pilot's exporter (which is checked by model verification instead).

usage: run_trimoska.py [--per-cell 8] [--deadline epoch]
"""
import argparse, json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wdsat_io as W  # noqa: E402

BENCH = Path("/home/user/crypto-autoresearcher/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks")
ap = argparse.ArgumentParser()
ap.add_argument("--per-cell", type=int, default=8); ap.add_argument("--deadline", type=float, default=0)
ap.add_argument("--sat", type=int, default=2)
ap.add_argument("--configs", default="xg,xg_b", help="comma list from xg, xg_b, b (b = -b without -x: no Gaussian elimination)")
a = ap.parse_args()


def sizing_of(text):
    nv, ne = None, None
    monos, maxdeg = set(), 1
    for ln in text.splitlines():
        t = ln.split()
        if not t:
            continue
        if t[0] == "p":
            nv, ne = int(t[2]), int(t[3]); continue
        if t[0] != "x":
            continue
        i = 1
        while i < len(t) - 1:
            if t[i].startswith("."):
                d = int(t[i][1:]); monos.add(tuple(sorted(int(v) for v in t[i + 1:i + 1 + d]))); maxdeg = max(maxdeg, d); i += 1 + d
            else:
                i += 1
    max_id = nv + len(monos)
    return {"MAX_ANF_ID": nv + 1, "MAX_DEGREE": maxdeg + 1, "MAX_ID": max_id, "MAX_EQ": sum(len(mo) + 1 for mo in monos) + 64,
            "MAX_EQ_SIZE": maxdeg + 2, "MAX_XEQ": ne + 1, "MAX_XEQ_SIZE": max_id + 1}, nv, ne, len(monos)


outp = HERE / "results" / "trimoska-control.jsonl"
done = set()
if outp.exists():
    for line in open(outp):
        r = json.loads(line); done.add((r["id"], r["config"]))
files = sorted(BENCH.glob("Xn*l*-*-*.anf"), key=lambda p: (p.stem.split("-")[0], p.stem.split("-")[2], int(p.stem.split("-")[1])))
cells = {}
for p in files:
    stem, idx, lab = p.stem.split("-")
    cells.setdefault((stem, lab), []).append(p)
with open(outp, "a") as f:
    for (stem, lab), ps in sorted(cells.items()):
        n, l = map(int, re.match(r"Xn(\d+)l(\d+)", stem).groups())
        for p in ps[: (a.per_cell if lab == "U" else a.sat)]:
            text = p.read_text()
            sz, nv, ne, nm = sizing_of(text)
            exe = W.build(sz)
            allcfg = {"xg": ["-x"], "xg_b": ["-x", "-b", "-m", "3", "-l", str(l)], "b": ["-b", "-m", "3", "-l", str(l)]}
            for config, flags in ((c, allcfg[c]) for c in a.configs.split(",")):
                if (p.stem, config) in done:
                    continue
                if a.deadline and time.time() > a.deadline:
                    sys.exit(0)
                r = W.run(exe, p, flags, 600)
                row = {"id": p.stem, "source": str(p.relative_to(BENCH.parents[2])), "m": 3, "n": n, "k": l, "l": l, "N": nv, "neq": ne,
                       "label": "UNSAT" if lab == "U" else "SAT", "family": "trimoska_S4", "config": config, "flags": flags,
                       "build_variant": "stock", "build": exe.parent.name, "sizing": sz, "anf_nonlinear_monomials": nm,
                       "exhaustive_2_ml": 2 ** (3 * l), "label_agrees_with_solver": (None if r["status"] not in ("SAT", "UNSAT") else r["status"] == row_lab) if (row_lab := ("UNSAT" if lab == "U" else "SAT")) else None,
                       "ts": time.time(), **{kk: v for kk, v in r.items() if kk != "assignment"}}
                f.write(json.dumps(row) + "\n"); f.flush()
                print(f"  {p.stem} {config} -> {r['status']} conf={r['conflicts']} nodes={r['nodes']} fails={r['fails']} wall={r['wall_s']:.2f}s", flush=True)
