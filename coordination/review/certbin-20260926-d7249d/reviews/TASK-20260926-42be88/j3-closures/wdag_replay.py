"""J3 (6): replay ONE wdag-v1 extraction from the engine's trace with the validator's own code, and compare
with the archived certificate.

Trace: the pinned engine's Closure._w_closure, INHERITED UNCHANGED; my subclass only overrides _extract
to capture (itl, pstar) -- the per-level op logs and origins -- instead of extracting.
Own code: back-trace over the op log (ps, xoff, xs) in reverse; the grouped construction written from
the specification's "recommended construction" (certificate_format): the '1' row of iteration i is
(basis rows of iteration i-1) + sum_j v_j * (fallen basis rows of iteration i-1 used with j), each
group collapsed into one node and recursed; level 0 maps stack rows to Macaulay pairs (mu, k) with
row index = mu_index * 19 + k, mu in mu_order(2, 20) (degree ascending, then ascending sorted tuple).
Own multilinear arithmetic evaluates every node and checks rules (a)-(e) on the replayed DAG.
usage: python3 wdag_replay.py <snapshot_root> <key>
"""
import gzip
import json
import os
import sys
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "j2-population"))
import gf219 as G  # noqa: E402
from literal_w4 import eqs_from_E  # noqa: E402

ROOT, KEY = sys.argv[1], sys.argv[2]
RUN = os.path.join(ROOT, "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60")
sys.path.insert(0, os.path.join(ROOT, "src"))
from crypto_autoresearcher.gf2 import closure as gclosure  # noqa: E402


class Capture(gclosure.Closure):
    def _extract(self, itl, pstar):
        self.captured = (itl, pstar)
        return []


inst = {r["key"]: r for r in (json.loads(l) for l in gzip.open(os.path.join(RUN, "instances.jsonl.gz"), "rt"))}
arch = [json.loads(l) for l in gzip.open(os.path.join(RUN, "certificates.jsonl.gz"), "rt")]
arch_w = next(c for c in arch if c["key"] == KEY and c["format"] == "wdag-v1")["body"]
E = G.hex_to_E(inst[KEY]["E_hex"])
eqs = eqs_from_E(E)
cl = Capture(20, 4, 19)
rec, _ = cl.w_closure(eqs, want_cert=True)
itl, pstar = cl.captured

MUS = [sum(1 << i for i in c) for d in range(3) for c in combinations(range(20), d)]  # mu_order(2, 20)


def my_backtrace(log, targets, nrows):
    """targets: dict name -> iterable of final-state row indices. Returns dict name -> set of original rows."""
    names = list(targets)
    assert len(names) <= 64
    S = np.zeros(nrows, dtype=np.uint64)
    for b, nm in enumerate(names):
        for r in targets[nm]:
            S[r] ^= np.uint64(1 << b)
    ps = log.ps
    xoff = log.xoff
    xs = log.xs
    for k in range(len(ps) - 1, -1, -1):
        X = xs[int(xoff[k]):int(xoff[k + 1])]
        if X.size:
            par = np.bitwise_xor.reduce(S[X])
            if par:
                S[int(ps[k])] ^= par
    out = {nm: set() for nm in names}
    for r in np.flatnonzero(S):
        w = int(S[r])
        for b, nm in enumerate(names):
            if (w >> b) & 1:
                out[nm].add(int(r))
    return out


def nrows_at(level):
    if level == 0:
        return len(MUS) * 19
    o = itl[level]["origin"]
    return o["nb"] + 20 * o["nnew"]


top = len(itl) - 1
# node identity: ("out",) or ("g", parent_identity, j, level)
nodes = {("out",): {"level": top, "rows": {}, "prods": set()}}
pending = {top: {("out",): {pstar}}}
for level in range(top, -1, -1):
    tg = {k: v for k, v in pending.pop(level, {}).items() if v}
    if not tg:
        continue
    orig = my_backtrace(itl[level]["log"], tg, nrows_at(level))
    org = itl[level]["origin"]
    for name, rows in orig.items():
        for r in sorted(rows):
            if org is None:
                mu, k = MUS[r // 19], r % 19
                nodes[name]["rows"][(mu, k)] = nodes[name]["rows"].get((mu, k), 0) ^ 1
            elif r < org["nb"]:
                pending.setdefault(level - 1, {}).setdefault(name, set()).symmetric_difference_update({int(org["prow"][r])})
            else:
                j, f = divmod(r - org["nb"], org["nnew"])
                child = ("g", name, j, level - 1)
                if child not in nodes:
                    nodes[child] = {"level": level - 1, "rows": {}, "prods": set()}
                nodes[name]["prods"].add((j, child))
                pending.setdefault(level - 1, {}).setdefault(child, set()).symmetric_difference_update({int(org["newrows"][f])})


def ml(mu):
    return [i for i in range(20) if mu >> i & 1]


mine = {nm: {"rows": sorted([ml(mu), k] for (mu, k), p in nd["rows"].items() if p),
             "prods": sorted((j, c) for j, c in nd["prods"])} for nm, nd in nodes.items()}

# align with the archived certificate by structure: output node, then children by (parent, j)
A = {n["id"]: n for n in arch_w["nodes"]}
align = {("out",): arch_w["output"]}
queue = [("out",)]
while queue:
    nm = queue.pop()
    aid = align[nm]
    for j, c in mine[nm]["prods"]:
        match = [cid for jj, cid in A[aid]["prods"] if jj == j]
        if len(match) == 1:
            align[c] = match[0]
            queue.append(c)
cmp = []
for nm, aid in align.items():
    a = A[aid]
    mrows = [[list(x[0]), x[1]] for x in mine[nm]["rows"]]
    arows = sorted([list(x[0]), x[1]] for x in a["rows"])
    mprods = sorted([j, align.get(c)] for j, c in mine[nm]["prods"])
    aprods = sorted(a["prods"])
    cmp.append({"node": str(nm), "archived_id": aid, "rows_mine": len(mrows), "rows_archived": len(arows),
                "rows_equal": mrows == arows, "prods_mine": mprods, "prods_archived": aprods, "prods_equal": mprods == aprods})

# own evaluation of the replayed DAG (rules (a)-(e) semantics, own multilinear arithmetic)
eqm = eqs


def poly_rows(rows):
    acc = {}
    for mu_list, k in rows:
        mu = sum(1 << i for i in mu_list)
        for m in eqm[k]:
            y = mu | m
            acc[y] = acc.get(y, 0) ^ 1
    return {m for m, p in acc.items() if p}


def times(j, P):
    acc = {}
    for m in P:
        y = m | (1 << j)
        acc[y] = acc.get(y, 0) ^ 1
    return {m for m, p in acc.items() if p}


val = {}
order = sorted(nodes, key=lambda nm: nodes[nm]["level"])
checks = []
for nm in order:
    P = poly_rows(mine[nm]["rows"])
    for j, c in mine[nm]["prods"]:
        deg_c = max((bin(m).count("1") for m in val[c]), default=0)
        checks.append({"node": str(nm), "child": str(c), "child_deg_le_3": deg_c <= 3})
        P ^= times(j, val[c])
    val[nm] = P
    checks.append({"node": str(nm), "deg_le_4": max((bin(m).count("1") for m in P), default=0) <= 4,
                   "max_mu_le_2": all(len(x[0]) <= 2 for x in mine[nm]["rows"])})
out_is_one = val[("out",)] == {0}
res = {"key": KEY, "engine_record_equals_archived": rec == json.loads(
           next(l for l in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt") if json.loads(l)["key"] == KEY))["W_4"],
       "levels": top + 1, "nodes_mine": len(nodes), "nodes_archived": len(arch_w["nodes"]),
       "node_comparison": cmp, "all_nodes_aligned": len(align) == len(nodes) == len(arch_w["nodes"]),
       "replayed_output_equals_1_own_arithmetic": out_is_one,
       "replayed_rule_checks": checks,
       "reproduces_archived_certificate": (len(align) == len(nodes) == len(arch_w["nodes"])
                                            and all(c["rows_equal"] and c["prods_equal"] for c in cmp))}
json.dump(res, open(os.path.join(HERE, f"wdag-replay-{KEY.replace(':', '_')}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "replayed_rule_checks"}, indent=1))
print("rule checks all true:", all(all(v for kk, v in c.items() if kk not in ("node", "child")) for c in checks))
