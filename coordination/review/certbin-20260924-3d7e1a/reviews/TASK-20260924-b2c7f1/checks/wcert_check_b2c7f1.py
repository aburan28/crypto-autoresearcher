#!/usr/bin/env python3
"""TASK-20260924-b2c7f1 CP-3: minimal W-certificate checker (comparator's own).

Written BEFORE reading any file under reviews/TASK-20260924-1f6a3c/code/.
The format is taken from ledger/handoffs/TASK-20260924-1f6a3c.yaml BR-5
("certbin.wcert.v1": {label, D: 4, elements: [{id, rows, products}], output_id}).

Semantics checked, literally (CP-3 of TASK-20260924-b2c7f1):
  g_id = sum_{(mu,k) in rows} mu*f_k  +  sum_{(j,p) in products} v_j * g_p   in
  B = F_2[v_0..v_17]/(v_i^2 + v_i).
  C1  every mu in rows has degree <= 2 (well-formed: distinct ascending indices
      in 0..17; k in 0..16)
  C2  every product parent p is an EARLIER id (appears earlier in the list and
      p < id), and deg g_p <= 3; j in 0..17
  C3  every element g_id has degree <= 4
  C4  the output element is exactly the constant 1
  (plus structural: schema, D == 4, unique ids, output_id present)

Polynomials are Python sets of 18-bit monomial masks (symmetric-difference
arithmetic). Nothing is imported from the re-deriver's code or from
experiments/EXP-CERTBIN-e94b27/verifier/. For CURVE-kind instances, f_k is
built with the ARCHIVED construction impl/macaulay.py descended_E(TableField(),
B, x_R), decoded with macaulay.EQ_MONS (CP-3 instruction); bytecode writing is
disabled so impl/ is not touched. For EXPLICIT-kind instances, f_k is the
F_2-sum of the monomials listed at position k of blind-inputs.json.
"""
import argparse
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True

NV = 18
NEQ = 17


def mono_mask(idx_list):
    m = 0
    for i in idx_list:
        m |= 1 << i
    return m


def popcount(x):
    return bin(x).count("1")


def deg(poly):
    return max((popcount(m) for m in poly), default=-1)


def mul_mono(poly, mmask):
    out = set()
    for m in poly:
        x = m | mmask
        if x in out:
            out.remove(x)
        else:
            out.add(x)
    return out


def build_f_explicit(inst):
    eqs = inst["equations"]
    assert len(eqs) == NEQ
    fs = []
    for eq in eqs:
        p = set()
        for mon in eq:
            x = mono_mask(mon)
            if x in p:
                p.remove(x)
            else:
                p.add(x)
        fs.append(frozenset(p))
    return fs


_ARCH = {}


def build_f_curve(repo, B, xR):
    if "mac" not in _ARCH:
        sys.path.insert(0, os.path.join(repo, "experiments/EXP-CERTBIN-e94b27/impl"))
        import macaulay  # archived construction, read-only use
        import gf2n
        _ARCH["mac"] = macaulay
        _ARCH["F"] = gf2n.TableField()
    mac = _ARCH["mac"]
    E = mac.descended_E(_ARCH["F"], B, xR)
    fs = []
    for k in range(NEQ):
        p = set()
        for j in range(len(mac.EQ_MONS)):
            if E[k, j]:
                p.add(mono_mask(mac.EQ_MONS[j]))
        fs.append(frozenset(p))
    return fs


def check_cert(rec, fs):
    """Return (status, detail). status in {valid, invalid}."""
    if rec.get("schema") != "certbin.wcert.v1":
        return "invalid", "schema is not certbin.wcert.v1"
    if rec.get("D") != 4:
        return "invalid", "D != 4"
    elems = rec.get("elements")
    if not isinstance(elems, list) or not elems:
        return "invalid", "no elements"
    g = {}
    order = []
    rowcache = {}
    stats = {"n_elements": len(elems), "n_rows": 0, "n_products": 0,
             "max_deg_mu": -1, "max_deg_parent": -1, "max_deg_element": -1}
    for pos, e in enumerate(elems):
        eid = e.get("id")
        if not isinstance(eid, int) or eid in g:
            return "invalid", f"C0 element at position {pos}: id missing or duplicated ({eid})"
        acc = set()
        for r in e.get("rows", []):
            mu, k = r[0], r[1]
            if not (isinstance(k, int) and 0 <= k < NEQ):
                return "invalid", f"C1 element {eid}: k={k} out of range"
            if list(mu) != sorted(set(mu)) or any((not isinstance(i, int)) or i < 0 or i >= NV for i in mu):
                return "invalid", f"C1 element {eid}: malformed mu {mu}"
            if len(mu) > 2:
                return "invalid", f"C1 element {eid}: mu {mu} has degree {len(mu)} > 2"
            stats["max_deg_mu"] = max(stats["max_deg_mu"], len(mu))
            key = (tuple(mu), k)
            if key not in rowcache:
                rowcache[key] = frozenset(mul_mono(fs[k], mono_mask(mu)))
            acc ^= rowcache[key]
            stats["n_rows"] += 1
        for pr in e.get("products", []):
            j, p = pr[0], pr[1]
            if not (isinstance(j, int) and 0 <= j < NV):
                return "invalid", f"C2 element {eid}: j={j} out of range"
            if p not in g:
                return "invalid", f"C2 element {eid}: parent {p} is not an earlier element"
            if not (isinstance(p, int) and p < eid):
                return "invalid", f"C2 element {eid}: parent id {p} not < {eid}"
            dp = deg(g[p])
            if dp > 3:
                return "invalid", f"C2 element {eid}: parent {p} has degree {dp} > 3"
            stats["max_deg_parent"] = max(stats["max_deg_parent"], dp)
            acc ^= mul_mono(g[p], 1 << j)
            stats["n_products"] += 1
        d = deg(acc)
        if d > 4:
            return "invalid", f"C3 element {eid}: degree {d} > 4"
        stats["max_deg_element"] = max(stats["max_deg_element"], d)
        g[eid] = frozenset(acc)
        order.append(eid)
    oid = rec.get("output_id")
    if oid not in g:
        return "invalid", f"C4 output_id {oid} is not an element"
    if g[oid] != frozenset({0}):
        return "invalid", f"C4 output element {oid} is not exactly 1 (|terms|={len(g[oid])}, deg={deg(g[oid])})"
    return "valid", stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--certs", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    bi = json.load(open(a.inputs))
    B = bi["curve"]["B"]
    insts = {x["label"]: x for x in bi["instances"]}
    recs = [json.loads(l) for l in gzip.open(a.certs, "rt")]
    by_label = {}
    dup = []
    for r in recs:
        if r.get("label") in by_label:
            dup.append(r.get("label"))
        by_label.setdefault(r.get("label"), []).append(r)
    out = {"schema": "certbin.b2c7f1.wcert_check.v1", "checker": os.path.basename(__file__),
           "n_records": len(recs), "duplicate_labels": dup, "per_label": {}}
    fcache = {}
    for lab in sorted(insts):
        inst = insts[lab]
        if lab not in by_label:
            out["per_label"][lab] = {"status": "absent", "kind": inst["kind"]}
            continue
        if inst["kind"] == "explicit":
            fs = build_f_explicit(inst)
        else:
            fs = build_f_curve(a.repo, B, inst["x_R"])
        fcache[lab] = fs
        res = []
        for r in by_label[lab]:
            st, det = check_cert(r, fs)
            res.append({"status": st, "detail": det})
        status = "valid" if all(x["status"] == "valid" for x in res) else "invalid"
        out["per_label"][lab] = {"status": status, "kind": inst["kind"], "records": res}
    unknown = sorted(l for l in by_label if l not in insts)
    out["records_with_unknown_label"] = unknown
    from collections import Counter
    out["counts"] = dict(Counter(v["status"] for v in out["per_label"].values()))
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    print(json.dumps(out["counts"]), "unknown", unknown, "dup", dup)


if __name__ == "__main__":
    main()
