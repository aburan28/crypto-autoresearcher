"""Proves-too-much control for RUN-RELN-a695fe (review plan, assigned to TASK-20261001-25c0f3).

Builds SYNTHETIC planted graphs, wraps each in a raw-result.json of the run's
schema (9 fixtures x 2 budgets, each fixture's real L), and feeds that file to
the frozen analysis.py CLI unchanged. Graph metrics come from the frozen
lpgraph.metrics; ER / rewire nulls and the known positive come from the frozen
nulls.py / celltask.known_positive, all under a synthetic namespace that is
neither the frozen namespace nor a smoke namespace. No frozen-label draw.

Objects (V = the run's |V| for b20-s11; both budgets' values are used):
  ER3       Erdos-Renyi G(V, ceil(1.5 V)), simple, mean degree ~3, every slot.
            Must NOT classify certified-subcritical.
  TREE      one spanning tree (cycle rank 0, giant 1), every slot. Must NOT be
            supercritical.
  FOREST3   disjoint 3-vertex paths (cycle rank 0, giant < 0.05), every slot.
            Must NOT be supercritical.
  MIX       FOREST3 everywhere except b20-s11 (both budgets) = ER3. Must NOT be
            certified-subcritical (one planted giant must not be averaged away).
  DENSE     supplementary: planted-dense (tree + ceil(V^1.5) edges) every slot.
  FOREST2   perfect matching (giant <= 3/V): sanity that the subcritical rule can fire.
  MIX2      FOREST2 everywhere except b20-s11 (both budgets) = ER3. Must NOT be
            certified-subcritical.
  FRAG      supplementary positive reachability: per-fixture core of cycle rank
            ceil(L^1.5) plus 200 disjoint K2 components.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import sys
from collections import deque
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
IMPL = REPO / "experiments/EXP-RELN-c5a377/implementation"
RUN = REPO / "experiments/EXP-RELN-c5a377/runs/RUN-RELN-a695fe"
sys.path.insert(0, str(IMPL))
import celltask  # noqa: E402  (frozen; only pure functions used)
import lpgraph  # noqa: E402
import nulls  # noqa: E402

NS = "validator-synthetic|TASK-20261001-25c0f3"
assert "smoke" not in NS and NS != "EXP-RELN-c5a377/v2"


def er_graph(n, m, rng):
    chosen, edges = set(), []
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        k = (min(u, v), max(u, v))
        if k in chosen:
            continue
        chosen.add(k)
        edges.append(k)
    return {"n": n, "edges": edges}


def tree_graph(n, rng):
    return {"n": n, "edges": [(i, rng.randrange(i)) for i in range(1, n)]}


def forest3(n):
    edges = []
    for s in range(0, n - 2, 3):
        edges += [(s, s + 1), (s + 1, s + 2)]
    r = n % 3
    if r == 2:
        edges.append((n - 2, n - 1))
    elif r == 1:
        edges.append((n - 1, n - 2))  # attach the leftover vertex to the last path
    return {"n": n, "edges": edges}


def forest2(n):
    """perfect matching (one 3-path if n is odd): giant fraction <= 3/n"""
    edges = [(s, s + 1) for s in range(0, n - 1, 2)]
    if n % 2:
        edges.append((n - 2, n - 1))
    return {"n": n, "edges": edges}


def frag(L, k=200):
    """Positive reachability object: a 2-vertex core with ceil(L^1.5)+1 parallel
    edges (cycle rank ceil(L^1.5), so delta_proof ~ 1/2 at the fixture's own L)
    plus k disjoint K2 components (fragmentation the simple ER null lacks)."""
    cr = math.ceil(L ** 1.5)
    edges = [(0, 1)] * (cr + 1)
    edges += [(2 + 2 * i, 3 + 2 * i) for i in range(k)]
    return {"n": 2 + 2 * k, "edges": edges}


def dense(n, rng):
    g = tree_graph(n, rng)
    for _ in range(math.ceil(n ** 1.5)):
        u = rng.randrange(n)
        v = rng.randrange(n - 1)
        g["edges"].append((u, v if v < u else v + 1))
    return g


def my_metrics(g):
    """Independent BFS check of the planted object (not the frozen code)."""
    n, edges = g["n"], g["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    comp, sizes = [-1] * n, []
    for s in range(n):
        if comp[s] >= 0:
            continue
        comp[s] = len(sizes)
        dq, k = deque([s]), 0
        while dq:
            u = dq.popleft()
            k += 1
            for w in adj[u]:
                if comp[w] < 0:
                    comp[w] = comp[s]
                    dq.append(w)
        sizes.append(k)
    return {"V": n, "E": len(edges), "c": len(sizes), "cycle_rank": len(edges) - n + len(sizes),
            "giant": max(sizes) / n, "mean_degree": 2 * len(edges) / n}


def block(g, L, bits, seed, budget, A):
    ctx = f"{bits}|{seed}|{budget}"
    met = lpgraph.metrics(g, L)
    rew, er = [], []
    for i in range(32):
        rew.append(celltask._null_row(lpgraph.metrics(nulls.rewire(g, NS, i, ctx), L)))
        ge = nulls.erdos_renyi(g["n"], len(g["edges"]), NS, i, ctx)
        er.append(None if ge is None else celltask._null_row(lpgraph.metrics(ge, L)))
    defects = []
    kp = celltask.known_positive(g["n"], L, NS, ctx, budget, defects)
    return {"budget": budget, "attempts": A, "graph": met,
            "null_er": {"replicates": er, "feasible": sum(1 for r in er if r is not None)},
            "null_rewire": {"replicates": rew}, "known_positive": kp,
            "known_false": {"status": "not_exercised", "note": "synthetic: not applicable"},
            "recovery": {"lp_recovery_fraction": None}, "charged": {"charged_work_over_sqrt_q": None},
            "synthetic_defects": defects}


def main():
    real = {}
    for f in sorted((RUN / "cells").glob("b*-s*.json")):
        c = json.loads(f.read_text())
        real[c["fixture_id"]] = c
    vb = {b["budget"]: b["graph"]["V"] for b in real["b20-s11"]["budgets"]}
    print("b20-s11 |V| per budget:", vb)
    objects = {}
    rng = random.Random("validator-ptm-25c0f3")
    for name in ("ER3", "TREE", "FOREST3", "FOREST2", "DENSE"):
        objects[name] = {}
        for bu, n in vb.items():
            if name == "ER3":
                g = er_graph(n, math.ceil(1.5 * n), rng)
            elif name == "TREE":
                g = tree_graph(n, rng)
            elif name == "FOREST3":
                g = forest3(n)
            elif name == "FOREST2":
                g = forest2(n)
            else:
                g = dense(n, rng)
            objects[name][bu] = g
    summary = {"namespace": NS, "b20_s11_V": vb, "objects": {}, "runs": {}}
    for name, gs in objects.items():
        summary["objects"][name] = {bu: my_metrics(g) for bu, g in gs.items()}

    def make(assign):
        cells = []
        for fid, c in real.items():
            fx = c["fixture"]
            L = c["header"]["L"]
            blocks = []
            for b in c["budgets"]:
                g = assign(fid, b["budget"])
                blocks.append(block(g, L, fx["bits"], fx["seed"], b["budget"], b["attempts"]))
            cells.append({"fixture_id": fid, "fixture": fx, "ns": NS, "budgets": blocks})
        return {"run_id": "SYNTHETIC-not-a-run", "status": "synthetic", "cells": cells}

    variants = {
        "ER3": lambda fid, bu: objects["ER3"][bu],
        "TREE": lambda fid, bu: objects["TREE"][bu],
        "FOREST3": lambda fid, bu: objects["FOREST3"][bu],
        "MIX": lambda fid, bu: objects["ER3"][bu] if fid == "b20-s11" else objects["FOREST3"][bu],
        "DENSE": lambda fid, bu: objects["DENSE"][bu],
        "FOREST2": lambda fid, bu: objects["FOREST2"][bu],
        "MIX2": lambda fid, bu: objects["ER3"][bu] if fid == "b20-s11" else objects["FOREST2"][bu],
        "FRAG": lambda fid, bu: frag(real[fid]["header"]["L"]),
    }
    for fid, c in real.items():
        summary["objects"].setdefault("FRAG", {})[fid] = my_metrics(frag(c["header"]["L"]))
    expect = {"ER3": "not certified-subcritical", "TREE": "not supercritical-enriched",
              "FOREST3": "not supercritical-enriched", "MIX": "not certified-subcritical",
              "DENSE": "supplementary (no required outcome)",
              "FOREST2": "not supercritical-enriched (sanity: subcritical rule should be able to fire)",
              "MIX2": "not certified-subcritical (FOREST2 baseline with one planted giant fixture)",
              "FRAG": "supplementary positive reachability: supercritical-enriched expected"}
    for vname, assign in variants.items():
        raw = make(assign)
        rp = OUT / f"ptm_{vname}_raw.json"
        rp.write_text(json.dumps(raw))
        ap = OUT / f"ptm_{vname}_analysis.json"
        if ap.exists():
            ap.unlink()
        cmd = [sys.executable, str(IMPL / "analysis.py"), str(rp), "--out", str(ap)]
        cp = subprocess.run(cmd, capture_output=True, text=True)
        res = json.loads(ap.read_text()) if ap.exists() else None
        v = res["verdict"] if res else None
        if vname in ("ER3", "MIX", "MIX2"):
            ok = v is not None and v != "certified-subcritical"
        elif vname in ("TREE", "FOREST3", "FOREST2"):
            ok = v is not None and v != "supercritical-enriched"
        else:
            ok = None
        defects = [d for c in raw["cells"] for b in c["budgets"] for d in b["synthetic_defects"]]
        summary["runs"][vname] = {"command": " ".join(cmd), "exit": cp.returncode, "stdout": cp.stdout.strip(),
                                  "stderr": cp.stderr.strip(), "verdict": v, "reason": res and res["reason"],
                                  "clauses": res and res["clauses"], "required": expect[vname],
                                  "result": {True: "PASS", False: "FAIL", None: "INFO"}[ok],
                                  "synthetic_known_positive_defects": defects}
        print(vname, v, summary["runs"][vname]["result"], flush=True)
    (OUT / "ptm_summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
