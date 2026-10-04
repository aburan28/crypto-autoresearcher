"""C-VERIFIER negative controls (specification controls C-VERIFIER).

Per kind (closure, arm) with >= 1 engine refutation under that closure, at
least 3 corrupted certificates of each type:
  (a) one row removed; (b) one k changed; (c) degree violation; (d) re-keyed
  to another system of the same arm.
The corruption is chosen with THIS module's own evaluator (never by
consulting the verifier), so that each corrupted certificate is
algebraically wrong or discipline-violating by construction; the
separate-process verifier must then reject every one.
"""
from __future__ import annotations

import copy

import numpy as np

from common import NEQ


def _parity(arr):
    if arr.size == 0:
        return arr
    u, c = np.unique(arr, return_counts=True)
    return u[(c & 1) == 1]


def _mm(mu):
    s = 0
    for i in mu:
        s |= 1 << i
    return s


def eval_flat(body, F):
    parts = [F[k] | _mm(mu) for mu, k in body]
    s = _parity(np.concatenate(parts)) if parts else np.zeros(0, dtype=np.int64)
    return bool(s.size == 1 and int(s[0]) == 0)


def eval_wdag(body, F, D=4):
    """-> (discipline_ok, output_is_1) with this module's own arithmetic."""
    polys = []
    ok = True
    for i, nd in enumerate(body["nodes"]):
        parts = []
        for mu, k in nd["rows"]:
            if len(mu) > D - 2 or not 0 <= k < NEQ:
                ok = False
            parts.append(F[k] | _mm(mu))
        for j, c in nd["prods"]:
            if c >= i:
                return False, False
            pc = polys[c]
            if pc.size and int(np.bitwise_count(pc).max()) > D - 1:
                ok = False
            parts.append(pc | (1 << j))
        p = _parity(np.concatenate(parts)) if parts else np.zeros(0, dtype=np.int64)
        if p.size and int(np.bitwise_count(p).max()) > D:
            ok = False
        polys.append(p)
    po = polys[body["output"]]
    return ok, bool(po.size == 1 and int(po[0]) == 0)


def masks_of(rows_int, col_mask):
    out = []
    for r in rows_int:
        ms = []
        x = r
        while x:
            b = (x & -x).bit_length() - 1
            ms.append(col_mask[b])
            x &= x - 1
        out.append(np.array(ms, dtype=np.int64))
    return out


def _valid(fmt, body, F, closure):
    if fmt == "flat-v1":
        good = eval_flat(body, F)
        if closure == "M_4" and max((len(mu) for mu, _ in body), default=0) > 2:
            return False
        return good
    ok, one = eval_wdag(body, F)
    return ok and one


def _remove_row(fmt, body, F, closure, nth):
    """Remove the nth row (in deterministic order) whose removal makes it invalid."""
    cands = []
    if fmt == "flat-v1":
        for p in range(len(body)):
            cands.append(("flat", p))
    else:
        for ni in range(len(body["nodes"]) - 1, -1, -1):
            for p in range(len(body["nodes"][ni]["rows"])):
                cands.append((ni, p))
    found = 0
    for c in cands:
        b = copy.deepcopy(body)
        if c[0] == "flat":
            del b[c[1]]
        else:
            del b["nodes"][c[0]]["rows"][c[1]]
        if not _valid(fmt, b, F, closure):
            if found == nth:
                return b, f"row {c} removed"
            found += 1
        if found > nth + 50:
            break
    return None, None


def _change_k(fmt, body, F, closure, nth):
    cands = []
    if fmt == "flat-v1":
        for p in range(len(body)):
            cands.append(("flat", p))
    else:
        for ni in range(len(body["nodes"]) - 1, -1, -1):
            for p in range(len(body["nodes"][ni]["rows"])):
                cands.append((ni, p))
    found = 0
    for c in cands:
        b = copy.deepcopy(body)
        if c[0] == "flat":
            mu, k = b[c[1]]
            b[c[1]] = [mu, (k + 1) % NEQ]
        else:
            mu, k = b["nodes"][c[0]]["rows"][c[1]]
            b["nodes"][c[0]]["rows"][c[1]] = [mu, (k + 1) % NEQ]
        if not _valid(fmt, b, F, closure):
            if found == nth:
                return b, f"row {c}: k -> k+1 mod 17"
            found += 1
    return None, None


def _child_deg4(body, F):
    """wdag with an extra child of degree 4 used twice with the same v_j
    (net zero): output still 1, rule (c) violated."""
    # a degree-4 row mu*f_k: k with a quadratic monomial m, mu two variables outside m
    for k in range(NEQ):
        quads = [int(m) for m in F[k].tolist() if bin(int(m)).count("1") == 2]
        if not quads:
            continue
        m = quads[0]
        outside = [i for i in range(18) if not (m >> i) & 1][:2]
        mu = outside
        new_nodes = [{"id": 0, "rows": [[mu, k]], "prods": []}]
        for nd in body["nodes"]:
            new_nodes.append({"id": nd["id"] + 1, "rows": nd["rows"],
                              "prods": [[j, c + 1] for j, c in nd["prods"]]})
        out = body["output"] + 1
        j = [i for i in range(18) if i not in mu and not (m >> i) & 1][0]
        new_nodes[out]["prods"] = new_nodes[out]["prods"] + [[j, 0], [j, 0]]
        b = {"D": body["D"], "nv": body["nv"], "nodes": new_nodes, "output": out}
        return b, f"child node 0 = v_{mu} * f_{k} (degree 4) used twice with v_{j}"
    return None, None


def build(certs, systems_by_arm, F_of, want=3):
    """certs: list of certificate lines (with cid, key, arm, closure, format, body,
    and for W_4 flat also max_mu). -> (nc lines, per-kind plan)."""
    nc = []
    plan = {}
    kinds = {}
    for c in certs:
        if c["closure"] == "M_4" and c["format"] == "flat-v1":
            kinds.setdefault(("M_4", c["arm"]), []).append(c)
        if c["closure"] == "W_4" and c["format"] == "wdag-v1":
            kinds.setdefault(("W_4", c["arm"]), []).append(c)
    w4flat3 = {}
    for c in certs:
        if c["closure"] == "W_4" and c["format"] == "flat-v1" and c.get("max_mu") == 3:
            w4flat3.setdefault(c["arm"], []).append(c)
    nid = 0
    for (clo, arm), srcs in sorted(kinds.items()):
        kname = f"{clo}|{arm}"
        kp = {"sources": len(srcs), "types": {}}
        # keep only sources that pass the impl-side evaluation
        good = [s for s in srcs if _valid(s["format"], s["body"], F_of(s["key"]), clo)]
        kp["sources_valid_impl_side"] = len(good)
        for typ in ["a", "b", "c", "d"]:
            made = []
            vac = None
            if typ in ("a", "b"):
                for i in range(want):
                    src = good[i % len(good)] if good else None
                    if src is None:
                        break
                    nth = i // max(1, len(good))
                    fn = _remove_row if typ == "a" else _change_k
                    b, note = fn(src["format"], src["body"], F_of(src["key"]), clo, nth)
                    if b is not None:
                        made.append((src, src["key"], src["format"], clo, b, note))
            elif typ == "c":
                if clo == "M_4":
                    fl = w4flat3.get(arm, [])
                    if not fl:
                        vac = "no flat certificate with max |mu| = 3 in this arm"
                    for i in range(min(want, len(fl)) if fl else 0):
                        made.append((fl[i], fl[i]["key"], "flat-v1", "M_4", fl[i]["body"],
                                     "W_4 flat certificate with max |mu| = 3 submitted as M_4"))
                    # variants if fewer than `want` distinct sources exist
                    v = 0
                    while fl and len(made) < want:
                        s0 = fl[v % len(fl)]
                        b = list(s0["body"]) + [[[], v % NEQ], [[], v % NEQ]]
                        made.append((s0, s0["key"], "flat-v1", "M_4", b,
                                     "same, with a cancelling duplicate pair appended (variant)"))
                        v += 1
                else:
                    fl = w4flat3.get(arm, [])
                    for i in range(min(want, len(fl))):
                        wd = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": fl[i]["body"], "prods": []}],
                              "output": 0}
                        made.append((fl[i], fl[i]["key"], "wdag-v1", "W_4", wd,
                                     "engine flat W_4 certificate (max |mu| = 3) as a one-node wdag"))
                    i = 0
                    while len(made) < want and good:
                        src = good[i % len(good)]
                        b, note = _child_deg4(src["body"], F_of(src["key"]))
                        if b is None:
                            break
                        made.append((src, src["key"], "wdag-v1", "W_4", b, note))
                        i += 1
            elif typ == "d":
                syskeys = systems_by_arm.get(arm, [])
                for i in range(want):
                    if not good:
                        break
                    src = good[i % len(good)]
                    pos = syskeys.index(src["key"]) if src["key"] in syskeys else 0
                    for step in range(1, len(syskeys)):
                        tgt = syskeys[(pos + step + i) % len(syskeys)]
                        if tgt == src["key"]:
                            continue
                        if not _valid(src["format"], src["body"], F_of(tgt), clo):
                            made.append((src, tgt, src["format"], clo, src["body"],
                                         f"re-keyed from {src['key']} to {tgt}"))
                            break
            for (src, key, fmt, cl2, body, note) in made:
                nc.append({"nc_id": nid, "kind": kname, "type": typ, "key": key, "arm": arm,
                           "closure": cl2, "format": fmt, "body": body, "source_cid": src["cid"],
                           "source_key": src["key"], "note": note})
                nid += 1
            kp["types"][typ] = {"built": len(made), "vacuous": vac}
        plan[kname] = kp
    return nc, plan
