#!/usr/bin/env python3
"""TASK-20260924-b2c7f1 CP-3: positive and negative controls for
wcert_check_b2c7f1.py (the comparator's own W-certificate checker).

Positive: two synthetic hand-derived certificates (one M_4-only, one using a
product), whose validity is derived by hand in the comments.
Negative: corruptions of the REAL archived certificates (one per kind per
chosen instance), a transplant onto a different instance of the same set, and
synthetic cases for C2 (parent degree > 3) and C3 (element degree > 4).
Every negative must be rejected; every positive accepted.
"""
import copy
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wcert_check_b2c7f1 as W  # noqa: E402

REPO = sys.argv[1]
R = os.path.join(REPO, "coordination/review/certbin-20260924-3d7e1a")
bi = json.load(open(os.path.join(R, "blind/blind-inputs.json")))
key = json.load(open(os.path.join(R, "blind-inputs-key.json")))
B = bi["curve"]["B"]
insts = {x["label"]: x for x in bi["instances"]}
recs = {json.loads(l)["label"]: json.loads(l) for l in gzip.open(os.path.join(R, "reviews/TASK-20260924-1f6a3c/wcerts.jsonl.gz"), "rt")}


def fs_of(lab):
    x = insts[lab]
    return W.build_f_explicit(x) if x["kind"] == "explicit" else W.build_f_curve(REPO, B, x["x_R"])


def synth_explicit(eqs):
    eqs = eqs + [[] for _ in range(17 - len(eqs))]
    return W.build_f_explicit({"equations": eqs})


results = []


def record(name, expect, rec, fs):
    st, det = W.check_cert(rec, fs)
    ok = (st == expect)
    results.append({"control": name, "expected": expect, "got": st,
                    "detail": det if isinstance(det, str) else "stats", "pass": ok})


# ---- positives (synthetic, derived by hand) ----
# P1: f_0 = v_0, f_1 = v_0 + 1: f_0 + f_1 = 1.
fsP1 = synth_explicit([[[0]], [[0], []]])
record("P1 synthetic M4-only", "valid",
       {"schema": "certbin.wcert.v1", "D": 4, "output_id": 0,
        "elements": [{"id": 0, "rows": [[[], 0], [[], 1]], "products": []}]}, fsP1)
# P2: f_0 = v_0 + v_1, f_1 = v_0 v_1 + v_1 + 1.
# g_0 = f_0 (deg 1); g_1 = f_1 + v_1 * g_0 = v0v1+v1+1 + v0v1+v1 = 1.
fsP2 = synth_explicit([[[0], [1]], [[0, 1], [1], []]])
record("P2 synthetic with product", "valid",
       {"schema": "certbin.wcert.v1", "D": 4, "output_id": 1,
        "elements": [{"id": 0, "rows": [[[], 0]], "products": []},
                     {"id": 1, "rows": [[[], 1]], "products": [[1, 0]]}]}, fsP2)
# N-syn-C2: g_0 = v0v1 * f_0 with f_0 = v2 v3 (deg 4) used as a parent.
fsN = synth_explicit([[[2, 3]], [[]]])
record("N synthetic parent degree 4 (C2)", "invalid",
       {"schema": "certbin.wcert.v1", "D": 4, "output_id": 1,
        "elements": [{"id": 0, "rows": [[[0, 1], 0]], "products": []},
                     {"id": 1, "rows": [[[], 1]], "products": [[4, 0]]}]}, fsN)
# N-syn-C3: f_0 = v2 v3 v4 (cubic, synthetic only), mu = v0 v1 -> degree 5.
fsN3 = synth_explicit([[[2, 3, 4]], [[]]])
record("N synthetic element degree 5 (C3)", "invalid",
       {"schema": "certbin.wcert.v1", "D": 4, "output_id": 0,
        "elements": [{"id": 0, "rows": [[[0, 1], 0]], "products": []}]}, fsN3)
# N-syn-P2-noproduct: P2 without the product must fail (output != 1).
record("N synthetic P2 without product (C4)", "invalid",
       {"schema": "certbin.wcert.v1", "D": 4, "output_id": 1,
        "elements": [{"id": 0, "rows": [[[], 0]], "products": []},
                     {"id": 1, "rows": [[[], 1]], "products": []}]}, fsP2)

# ---- negatives on real certificates ----
by_set = {}
for lab in sorted(recs):
    by_set.setdefault(key[lab]["set"], []).append(lab)
chosen = []
for s, labs in sorted(by_set.items()):
    chosen += labs[:5]
for lab in chosen:
    rec = recs[lab]
    fs = fs_of(lab)
    record(f"{lab} unmodified", "valid", rec, fs)
    out = [e for e in rec["elements"] if e["id"] == rec["output_id"]][0]
    # drop one row of the output element
    r = copy.deepcopy(rec)
    o = [e for e in r["elements"] if e["id"] == r["output_id"]][0]
    if o["rows"]:
        del o["rows"][len(o["rows"]) // 2]
        record(f"{lab} drop one output row", "invalid", r, fs)
    # change k of one row
    r = copy.deepcopy(rec)
    o = [e for e in r["elements"] if e["id"] == r["output_id"]][0]
    if o["rows"]:
        o["rows"][0][1] = (o["rows"][0][1] + 1) % 17
        record(f"{lab} change k of one row", "invalid", r, fs)
    # mu of degree 3
    r = copy.deepcopy(rec)
    o = [e for e in r["elements"] if e["id"] == r["output_id"]][0]
    if o["rows"]:
        o["rows"][0][0] = [0, 1, 2]
        record(f"{lab} mu degree 3", "invalid", r, fs)
    if out["products"]:
        # change j of one product
        r = copy.deepcopy(rec)
        o = [e for e in r["elements"] if e["id"] == r["output_id"]][0]
        o["products"][0][0] = (o["products"][0][0] + 1) % 18
        record(f"{lab} change j of one product", "invalid", r, fs)
        # drop the product
        r = copy.deepcopy(rec)
        o = [e for e in r["elements"] if e["id"] == r["output_id"]][0]
        o["products"] = o["products"][1:]
        record(f"{lab} drop one product", "invalid", r, fs)
        # parent not earlier: move output before its parents
        r = copy.deepcopy(rec)
        oi = [i for i, e in enumerate(r["elements"]) if e["id"] == r["output_id"]][0]
        r["elements"].insert(0, r["elements"].pop(oi))
        record(f"{lab} output moved before parents", "invalid", r, fs)
        # output_id pointed at a parent
        r = copy.deepcopy(rec)
        r["output_id"] = out["products"][0][1]
        record(f"{lab} output_id at parent", "invalid", r, fs)
    # transplant onto another instance of the same set
    others = [l for l in by_set[key[lab]["set"]] if l != lab]
    if others:
        record(f"{lab} transplanted onto {others[0]}", "invalid", rec, fs_of(others[0]))

summary = {"n_controls": len(results), "all_pass": all(x["pass"] for x in results),
           "n_positive": sum(1 for x in results if x["expected"] == "valid"),
           "n_negative": sum(1 for x in results if x["expected"] == "invalid"),
           "failures": [x for x in results if not x["pass"]], "results": results}
json.dump(summary, open(os.path.join(HERE, "wcert-check-controls-output.json"), "w"), indent=1)
print(json.dumps({k: summary[k] for k in ("n_controls", "n_positive", "n_negative", "all_pass")}),
      len(summary["failures"]))
