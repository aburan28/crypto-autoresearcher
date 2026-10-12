#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J3 item (5): replay ONE iteration-1 wdag-v1 by
hand, on S3-U62 slot 0 (U62:F-S3:27; my literal W_4 has one_first_iteration 1
for it). The system and certificate are chosen by rule (S3-U62 at slot 0), not
by outcome. Own multilinear arithmetic over F_2 on full B (no degree cap, so a
degree violation would be visible). Imports nothing from impl/, verifier/, src/.
"""
from __future__ import annotations

import gzip
import json
import sys
from itertools import combinations
from pathlib import Path

WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
KEY = "U62:F-S3:27"
MONOS2 = [()] + [(i,) for i in range(18)] + list(combinations(range(18), 2))


def rows_to_masks(E_hex):
    out = []
    for h in E_hex:
        r = int(h, 16)
        f = set()
        for col, m in enumerate(MONOS2):
            if (r >> col) & 1:
                mk = 0
                for i in m:
                    mk |= 1 << i
                f ^= {mk}
        out.append(f)
    return out


def mu_mask(mu):
    mk = 0
    for i in mu:
        mk |= 1 << i
    return mk


def times(mk, poly):
    out = set()
    for m in poly:
        out ^= {m | mk}
    return out


def deg(poly):
    return max((bin(m).count("1") for m in poly), default=-1)


def main():
    inst = {}
    for l in gzip.open(RUN / "instances.jsonl.gz", "rt"):
        r = json.loads(l)
        inst[r["key"]] = r
    eqs = rows_to_masks(inst[KEY]["E_hex"])
    certs = [json.loads(l) for l in gzip.open(RUN / "certificates.jsonl.gz", "rt")]
    mine = [c for c in certs if c["key"] == KEY]
    out = {"key": KEY, "certificate_lines_for_key": [{f: c[f] for f in ("closure", "format", "source", "cid")} for c in mine]}
    wd = [c for c in mine if c["format"] == "wdag-v1"]
    assert len(wd) == 1
    body = wd[0]["body"]
    nodes = {n["id"]: n for n in body["nodes"]}
    ids = sorted(nodes)
    viol = []
    if body.get("D") != 4 or body.get("nv") != 18:
        viol.append("header D/nv")
    if ids != list(range(len(ids))):
        viol.append("node ids not 0..N-1")
    poly = {}
    level = {}
    for i in ids:
        n = nodes[i]
        p = set()
        for mu, k in n["rows"]:
            if len(mu) > 2 or not (0 <= k <= 16) or sorted(set(mu)) != mu or any(not 0 <= x < 18 for x in mu):
                viol.append(f"(b) node {i} row {mu},{k}")
            p ^= times(mu_mask(mu), eqs[k])
        lv = 0
        for j, c in n["prods"]:
            if not c < i:
                viol.append(f"(a) node {i} child {c}")
                continue
            if deg(poly[c]) > 3:
                viol.append(f"(c) node {i} child {c} degree {deg(poly[c])}")
            p ^= times(1 << j, poly[c])
            lv = max(lv, level[c] + 1)
        if deg(p) > 4:
            viol.append(f"(d) node {i} degree {deg(p)}")
        poly[i] = p
        level[i] = lv
    o = body["output"]
    e_ok = poly[o] == {0}
    if not e_ok:
        viol.append("(e) poly(output) != 1")
    # structure of the recommended iteration-1 construction
    outn = nodes[o]
    js = [j for j, _ in outn["prods"]]
    children = [c for _, c in outn["prods"]]
    struct = {
        "node_count": len(ids),
        "output": o,
        "output_level": level[o],
        "output_rows_M4": len(outn["rows"]),
        "output_prods_j": js,
        "distinct_j": len(set(js)) == len(js),
        "children_all_level0_flat_blocks": all(not nodes[c]["prods"] for c in children),
        "children_degrees": [deg(poly[c]) for c in children],
        "children_rows": [len(nodes[c]["rows"]) for c in children],
        "unreferenced_nodes": sorted(set(ids) - set(children) - {o}),
        "max_mu_over_all_rows": max(len(mu) for n in nodes.values() for mu, _ in n["rows"]),
        "deg_output_own_rows_sum": deg(set().union() ^ _rows_sum(outn, eqs)),
        "deg_v_j_times_child": [deg(times(1 << j, poly[c])) for j, c in outn["prods"]],
    }
    # the output decomposes as (element of rowspace(M_4) of degree <= 4) + sum_j v_j * (element of
    # rowspace(M_4) of degree <= 3): exactly "1 in W^(1)" with one level of products
    s = _rows_sum(outn, eqs)
    for j, c in outn["prods"]:
        s ^= times(1 << j, poly[c])
    struct["recomposed_output_equals_1"] = s == {0}
    out["checks"] = {"violations": viol, "rule_e_poly_output_is_1": e_ok, "structure": struct,
                     "depth_equals_one_first_iteration_1": level[o] == 1}
    # the engine's flat W_4 certificate for the same system (not counted toward W_4 unless max|mu|<=2)
    fl = [c for c in mine if c["closure"] == "W_4" and c["format"] == "flat-v1"]
    if fl:
        b = fl[0]["body"]
        acc = set()
        for mu, k in b:
            acc ^= times(mu_mask(mu), eqs[k])
        out["engine_flat_W4_certificate"] = {"rows": len(b), "max_mu": max(len(mu) for mu, _ in b),
                                             "sums_to_1": acc == {0}}
    cl = {}
    for l in gzip.open(RUN / "closures.jsonl.gz", "rt"):
        r = json.loads(l)
        if r["key"] == KEY and r["closure"] == "W_4":
            cl = r
    out["archived_W_4_record"] = {f: cl.get(f) for f in ("dims", "one_first_iteration", "final_dim", "wdag_extractor")}
    lit = json.load(open(OUTDIR / "j3-literal-ext.json"))["systems"][KEY]["W_4_literal"]
    out["my_literal_W_4"] = {f: lit[f] for f in ("dims", "one_first_iteration", "final_dim")}
    json.dump(out, open(OUTDIR / "j3-wdag-replay.json", "w"), indent=1)
    print(json.dumps(out, indent=1)[:4000])


def _rows_sum(n, eqs):
    p = set()
    for mu, k in n["rows"]:
        p ^= times(mu_mask(mu), eqs[k])
    return p


if __name__ == "__main__":
    main()
