"""VC-7: own negative controls for every (closure, arm, format) kind present in
certificates.jsonl.gz and annihilators.jsonl.gz. All must reject.

Position rule: one numpy.random.Generator(numpy.random.PCG64(20260926401777)),
consumed in the order of this script (kinds sorted; per kind 5 base
certificates drawn without replacement from the kind's certificates that MY
checker verified, sorted by file line; then per base the types in order).
Refutation formats (a)-(c) corrupt the OUTPUT node's rows (wdag-v1) or C
(flat-v1), and each change is required to be a NONZERO element of B, so that
poly(output) != 1 by construction.

Usage: run_negctl.py <instances.jsonl.gz> <certificates.jsonl.gz> <annihilators.jsonl.gz> <workdir>"""
import copy
import gzip
import json
import sys
import time
from collections import defaultdict

import numpy as np

import certs
import kern
import layout as LY

NC_SEED = 20260926401777
g = np.random.Generator(np.random.PCG64(NC_SEED))


def ri(n):
    return int(g.integers(0, n))


def delta_nonzero(S, rows):
    return bool(S.rows_poly(rows).any())


def pick_entry(S, entries, cond):
    """Draw entry indices until cond holds (at most 200 draws)."""
    for _ in range(200):
        i = ri(len(entries))
        r = cond(i)
        if r is not None:
            return i, r
    raise RuntimeError("no admissible position")


def corrupt_rows(S, rows, typ):
    """rows: list of [mu, k]. Returns (new_rows, detail)."""
    present = {(tuple(m), k) for m, k in rows}
    if typ == "a":
        def cond(i):
            mu, k = rows[i]
            return True if delta_nonzero(S, [(LY.mask_of(mu), k)]) else None
        i, _ = pick_entry(S, rows, cond)
        new = rows[:i] + rows[i + 1:]
        return new, {"removed_entry_index": i, "removed": rows[i]}
    if typ == "b":
        def cond(i):
            mu, k = rows[i]
            for _ in range(40):
                k2 = ri(19)
                if k2 != k and (tuple(mu), k2) not in present and \
                        delta_nonzero(S, [(LY.mask_of(mu), k), (LY.mask_of(mu), k2)]):
                    return k2
            return None
        i, k2 = pick_entry(S, rows, cond)
        new = [list(e) for e in rows]
        new[i] = [rows[i][0], k2]
        new.sort(key=lambda e: (tuple(e[0]), e[1]))
        return new, {"entry_index": i, "old": rows[i], "new": [rows[i][0], k2]}
    if typ == "c":
        def cond(i):
            mu, k = rows[i]
            if len(mu) == 0:
                return None
            for _ in range(40):
                p = ri(len(mu))
                v = ri(20)
                if v in mu:
                    continue
                mu2 = sorted([x for a, x in enumerate(mu) if a != p] + [v])
                if (tuple(mu2), k) in present:
                    continue
                if delta_nonzero(S, [(LY.mask_of(mu), k), (LY.mask_of(mu2), k)]):
                    return mu2
            return None
        i, mu2 = pick_entry(S, rows, cond)
        new = [list(e) for e in rows]
        new[i] = [mu2, rows[i][1]]
        new.sort(key=lambda e: (tuple(e[0]), e[1]))
        return new, {"entry_index": i, "old": rows[i], "new": [mu2, rows[i][1]]}
    raise ValueError(typ)


def main():
    inst, cert_path, ann_path, workdir = sys.argv[1:5]
    t0 = time.time()
    recs = {}
    for l in gzip.open(inst, "rt"):
        r = json.loads(l)
        recs[r["key"]] = r
    by_arm_unsat = defaultdict(list)
    for k, r in recs.items():
        if r["role"] == "unsat":
            by_arm_unsat[r["arm"]].append(k)
    for a in by_arm_unsat:
        by_arm_unsat[a].sort(key=lambda k: recs[k]["index"])
    mine = {}
    for l in gzip.open(workdir + "/certs.jsonl.gz", "rt"):
        o = json.loads(l)
        mine[o["line"]] = o
    kinds = defaultdict(list)
    flat_of_key = {}
    lines = {}
    for i, l in enumerate(gzip.open(cert_path, "rt")):
        rec = json.loads(l)
        lines[i] = rec
        kinds[(rec["closure"], rec["key"].split(":")[0], rec["format"])].append(i)
        if rec["format"] == "flat-v1":
            flat_of_key[rec["key"]] = rec
    cache = {}

    def sysof(key):
        if key not in cache:
            cache[key] = certs.System(LY.decode_E(recs[key]["E_hex"]))
        return cache[key]

    controls = []
    for kind in sorted(kinds):
        clo, arm, fmt = kind
        cand = [i for i in kinds[kind] if mine[i].get("verified")]
        pick = sorted(g.choice(len(cand), size=5, replace=False).tolist())
        bases = [cand[p] for p in pick]
        for bi in bases:
            rec = lines[bi]
            key = rec["key"]
            S = sysof(key)
            body = rec["body"]
            for typ in ("a", "b", "c", "d", "e"):
                entries = []
                if typ in ("a", "b", "c"):
                    if fmt == "flat-v1":
                        newC, det = corrupt_rows(S, body["C"], typ)
                        r = certs.check_flat(S, {"C": newC})
                        rej = not r["verified"]
                    else:
                        b2 = copy.deepcopy(body)
                        o = b2["output"]
                        b2["nodes"][o]["rows"], det = corrupt_rows(S, b2["nodes"][o]["rows"], typ)
                        det["node"] = o
                        r = certs.check_wdag(S, b2)
                        r.pop("node_degrees", None)
                        rej = not r["verified"]
                    entries.append((typ, det, r, rej, key))
                elif typ == "d":
                    if fmt == "flat-v1":
                        r = certs.check_flat_as_M4(S, body)
                        entries.append(("d", {"construction": "archived flat-v1 (max |mu| = %s) submitted as an M_4 "
                                                              "refutation" % r.get("max_mu")},
                                        r, not r["accepted_as_M4"], key))
                    else:
                        # (d1) a prods child of degree 4: new node N = one row (mu, k), |mu| = 2,
                        # deg(mu f_k) = 4; new output = old output rows/prods + [j, N] twice.
                        for _ in range(400):
                            mu = sorted(g.choice(20, size=2, replace=False).tolist())
                            k = ri(19)
                            if certs.degree(S.rows_poly([(LY.mask_of(mu), k)])) == 4:
                                break
                        j = ri(20)
                        b2 = copy.deepcopy(body)
                        n = len(b2["nodes"])
                        o = b2["output"]
                        b2["nodes"].append({"id": n, "rows": [[mu, k]], "prods": []})
                        b2["nodes"].append({"id": n + 1, "rows": b2["nodes"][o]["rows"],
                                            "prods": b2["nodes"][o]["prods"] + [[j, n], [j, n]]})
                        b2["output"] = n + 1
                        r = certs.check_wdag(S, b2)
                        r.pop("node_degrees", None)
                        entries.append(("d1_prods_child_degree4",
                                        {"new_node_row": [mu, k], "j": j, "pair_inserted_in_new_output": n + 1},
                                        r, not r["verified"], key))
                        # (d2) a one-node wdag-v1 with |mu| = 3: the same key's flat-v1 C as one node
                        fl = flat_of_key.get(key)
                        if fl is not None:
                            b3 = {"D": 4, "nv": 20, "neq": 19, "output": 0,
                                  "nodes": [{"id": 0, "rows": fl["body"]["C"], "prods": []}]}
                            r3 = certs.check_wdag(S, b3)
                            r3.pop("node_degrees", None)
                            entries.append(("d2_one_node_mu3", {"source": "flat-v1 of the same key"}, r3,
                                            not r3["verified"], key))
                elif typ == "e":
                    others = [k for k in by_arm_unsat[arm] if k != key]
                    tgt = others[ri(len(others))]
                    St = sysof(tgt)
                    if fmt == "flat-v1":
                        r = certs.check_flat(St, body)
                    else:
                        r = certs.check_wdag(St, body)
                        r.pop("node_degrees", None)
                    entries.append(("e", {"transplanted_to": tgt}, r, not r["verified"], tgt))
                for (t, det, r, rej, evalkey) in entries:
                    controls.append({"kind": list(kind), "type": t, "base_key": key, "base_line": bi,
                                     "evaluated_on": evalkey, "detail": det,
                                     "checker_verdict": {x: r.get(x) for x in
                                                         ("verified", "accepted_as_M4", "first_violated", "violated",
                                                          "residual_size", "max_mu")
                                                         if x in r},
                                     "rejected": bool(rej)})
        print(kind, "done", round(time.time() - t0, 1), flush=True)

    # ------------------------------------------------------------- ann-v1 kinds
    ann = [json.loads(l) for l in gzip.open(ann_path, "rt")]
    akinds = defaultdict(list)
    for i, rec in enumerate(ann):
        akinds[(rec["closure"], rec["key"].split(":")[0], rec["format"])].append(i)
    ann_keys = {rec["key"] for rec in ann}
    positives = []
    vacuous = []
    for kind in sorted(akinds):
        clo, arm, fmt = kind
        for ai in akinds[kind]:
            rec = ann[ai]
            key = rec["key"]
            S = sysof(key)
            body = rec["body"]
            # (e) transplant onto another unsat system of the arm (not an ann-v1 key)
            others = [k for k in by_arm_unsat[arm] if k not in ann_keys]
            tgt = others[ri(len(others))]
            r = certs.check_ann(sysof(tgt), body)
            controls.append({"kind": list(kind), "type": "e", "base_key": key, "evaluated_on": tgt,
                             "detail": {"transplanted_to": tgt},
                             "checker_verdict": {x: r.get(x) for x in ("verified", "first_violated")},
                             "A": {a: r[a]["pass"] for a in ("A1", "A2", "A3") if a in r},
                             "rejected": not r["verified"]})
            # (f) add a functional nonzero on a named M_4 row
            M4 = S.m4_packed()
            dense = kern.unpack_rows(M4, LY.NCOL4)
            nz_rows = np.flatnonzero(dense.any(axis=1))
            row = int(nz_rows[ri(nz_rows.size)])
            supp = np.flatnonzero(dense[row])
            c = int(supp[ri(supp.size)])
            mu_i, k = divmod(row, LY.NEQ)
            b2 = dict(body)
            b2["L_hex"] = list(body["L_hex"]) + [format(1 << c, "x")]
            r = certs.check_ann(S, b2)
            controls.append({"kind": list(kind), "type": "f", "base_key": key, "evaluated_on": key,
                             "detail": {"named_M4_row_index": row, "row_mu": list(LY.mu_order(2, 20)[mu_i]),
                                        "row_k": k, "added_functional": "e_c (coordinate %d)" % c},
                             "checker_verdict": {x: r.get(x) for x in ("verified", "first_violated")},
                             "A": {a: r[a]["pass"] for a in ("A1", "A2", "A3")},
                             "rejected": not r["verified"]})
            # (g) every functional's constant coordinate cleared
            b3 = dict(body)
            b3["L_hex"] = [format(int(h, 16) & ~(1 << LY.CONST_COL), "x") for h in body["L_hex"]]
            r = certs.check_ann(S, b3)
            controls.append({"kind": list(kind), "type": "g", "base_key": key, "evaluated_on": key,
                             "detail": {"cleared": "bit %d of every functional" % LY.CONST_COL},
                             "checker_verdict": {x: r.get(x) for x in ("verified", "first_violated")},
                             "A": {a: r[a]["pass"] for a in ("A1", "A2", "A3")},
                             "rejected": not r["verified"]})
        # (h) annihilator of M_4 alone on systems where own W_4 != M_4 (W^(1) != W^(0))
        step = []
        for role in ("unsat", "sat"):
            try:
                step += [json.loads(l) for l in gzip.open(workdir + "/step-%s-%s.jsonl.gz" % (arm, role), "rt")]
            except FileNotFoundError:
                pass
        diff = [o["key"] for o in step if o["W1_ne_W0"] and not o["one_in_M4"]]
        same = [o["key"] for o in step if not o["W1_ne_W0"] and not o["one_in_M4"]]
        hkeys = [diff[p] for p in sorted(g.choice(len(diff), size=min(5, len(diff)), replace=False).tolist())] \
            if diff else []
        pkeys = [same[p] for p in sorted(g.choice(len(same), size=min(2, len(same)), replace=False).tolist())] \
            if same else []
        for key2, want_reject in [(k, True) for k in hkeys] + [(k, False) for k in pkeys]:
            S2 = sysof(key2)
            R, rank, piv = kern.rref(S2.m4_packed(), LY.NCOL4)
            Rd = kern.unpack_rows(R[:rank], LY.NCOL4)
            free = np.setdiff1d(np.arange(LY.NCOL4), piv)
            Ld = np.zeros((free.size, LY.NCOL4), dtype=np.uint8)
            Ld[np.arange(free.size), free] = 1
            Ld[:, piv] = Rd[:, free].T
            Lp = kern.pack_rows(Ld, LY.WORDS4)
            body_h = {"D": 4, "nv": 20, "neq": 19, "L_hex": [certs.packed_to_hex(x) for x in Lp]}
            r = certs.check_ann(S2, body_h)
            item = {"kind": list(kind), "type": "h" if want_reject else "h_positive_control_W4_eq_M4",
                    "base_key": key2, "evaluated_on": key2,
                    "detail": {"L": "basis of the annihilator of rowspace(M_4) (%d functionals)" % free.size,
                               "own_W1_ne_W0": want_reject},
                    "checker_verdict": {x: r.get(x) for x in ("verified", "first_violated")},
                    "A": {a: r[a]["pass"] for a in ("A1", "A2", "A3")},
                    "dim_S": r.get("dim_S")}
            if want_reject:
                item["rejected"] = not r["verified"]
                controls.append(item)
            else:
                item["accepted"] = bool(r["verified"])
                positives.append(item)
        if not diff:
            roles = sorted({recs[o["key"]]["role"] for o in step})
            vacuous.append({"kind": list(kind), "type": "h",
                            "reason": "no scanned system of the arm (%d systems, roles %s) has own W^(1) != W^(0) "
                                      "with 1 not in M_4, so the annihilator of M_4 alone is a VALID ann-v1 there "
                                      "(it annihilates W_4 = M_4), not a corruption; its acceptance is recorded "
                                      "as a positive control" % (len(step), roles)})
        print(kind, "done", round(time.time() - t0, 1), flush=True)

    json.dump({"seed": NC_SEED, "controls": controls, "positive_controls": positives, "vacuous": vacuous,
               "seconds": round(time.time() - t0, 1)}, open(workdir + "/negctl.json", "w"), indent=1)
    nrej = sum(c["rejected"] for c in controls)
    print("controls", len(controls), "rejected", nrej, "positives", len(positives),
          "accepted", sum(p["accepted"] for p in positives), "vacuous", len(vacuous))


if __name__ == "__main__":
    main()
