#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J4: per-control rechecks from raw archived bytes.

  C-SRC      own re-hash of the 7 bound inputs
  C-REG      (a)-(d) recomputed from the run's closures.jsonl.gz against the
             archived RC-1 flags/records, the red-team profiles and o2 rows
  C-TOP      P equality recomputed from closures.jsonl.gz
  C-ORACLE2  own exhaustive s (and solution lists) for the 288 archived-arm
             systems (fresh systems were covered attempt by attempt in J2)
  C-PS       per arm: refutations of satisfiable controls, codim vs s
  C-VERIFIER every negative control re-evaluated with OWN arithmetic: is it
             really wrong or discipline-violating, and which rule does it
             violate (so that "can fail" is shown, not assumed)
  C-CERT     certificate-verification.json totals
Reports violations and per-control facts. Imports nothing from impl/,
verifier/ or src/; imports this task's own j2_replay_sweep.py for the
exhaustive evaluator.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
MONOS2 = [()] + [(i,) for i in range(18)] + list(combinations(range(18), 2))
sp = importlib.util.spec_from_file_location("j2own", OUTDIR.parent / "j2-construction/j2_replay_sweep.py")
j2 = importlib.util.module_from_spec(sp)
sys.argv_saved = sys.argv
sp.loader.exec_module(j2)   # builds truth tables only; main() is not run


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]


def masks(E_hex):
    out = []
    for h in E_hex:
        r = int(h, 16)
        f = set()
        for col, m in enumerate(MONOS2):
            if (r >> col) & 1:
                f ^= {sum(1 << i for i in m)}
        out.append(f)
    return out


OUT = {}
# C-SRC
bound = {
    "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json": "64dffd01f693289ac533aec3348319cea6c85ffaaea11c4d63ddcd607cd85a7a",
    "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/closures.jsonl.gz": "d0186e69b8492f65dd51ac5eb10295d90031ec711e4adbb0d62e7b5090ef917a",
    "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/certificates.jsonl.gz": "cb87db676674af28246bd3c8d2631e78d057ad91f48535879294b48a2b8fd53f",
    "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json": "aa3eb4d0f3e9da68d710b8946e2e4c3d13de1b991882f23218d259df9615201d",
    "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/checkpoint/p1-instances.json.gz": "5ab5f4b60a983570a1edde9fd40ad4d90fc6683c412b00847ac7db40f7e45f11",
    "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/n-ell-instances.json": "d9f37b17519daff42d462be30200c1f56fb45f87de83aa61e45d393e12ca997b",
    "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-engine-and-own.json": "b39e113f33f846ae5eb4b0f70570efcd736f868fd12dbee7ae56d7e33b471793",
}   # transcribed from the specification's inputs.files
OUT["C-SRC"] = {p: sha(WT / p) == h for p, h in bound.items()}

inst = {r["key"]: r for r in jl(RUN / "instances.jsonl.gz")}
cl = {(r["key"], r["closure"]): r for r in jl(RUN / "closures.jsonl.gz")}
iset = json.load(open(WT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"))["sets"]
arch = {r["key"]: r for s in iset.values() for r in s}
rc1 = {(r["key"], r["closure"]): r for r in jl(WT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/closures.jsonl.gz")}

# C-REG
reg = defaultdict(list)
REG_W4 = ["iterations_to_fixpoint", "dims", "final_dim", "one", "one_first_iteration", "dims_by_deg",
          "new_fallen_per_iteration", "stack_rows_per_iteration"]
nreg = Counter()
for k, r in inst.items():
    if r["arm"] not in ("S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262"):
        continue
    a = arch[k]["archived"]
    m3, m4 = cl[(k, "M_3")], cl[(k, "M_4")]
    nreg["a"] += 1
    if (m3["rank"], m3["one"], m4["rank"], m4["one"]) != (a["rank_3"], a["one_in_R_3"], a["rank_4"], a["one_in_R_4"]):
        reg["a"].append(k)
    ref = rc1.get((k, "W_4"))
    nreg["b"] += 1
    if ref is None or any(cl[(k, "W_4")].get(f) != ref.get(f) for f in REG_W4):
        reg["b"].append(k)
    if r["arm"].startswith("S3-"):
        rb = cl[(k, "rc_b")]
        if rb["ell_linear_support"] != [0, 9]:
            reg["c"].append(k + " support")
        prof = cl[(k, "R'_4")]["dims_by_deg"]
        if r["arm"] in ("S3-U62", "S3-C20"):
            nreg["c"] += 1
            want = [1, 17, 153, 833, 2212] if arch[k]["idx"] == 893 and r["arm"] == "S3-U62" else [1, 18, 154, 834, 2213]
            if prof != want:
                reg["c"].append(k)
s62 = sorted([k for k, r in inst.items() if r["arm"] == "S3-S62"], key=lambda k: arch[k]["idx"])[:10]
for k in s62:
    nreg["c"] += 1
    sv = inst[k]["s"]
    if cl[(k, "R'_4")]["dims_by_deg"][:4] != [0, 18 - sv, 154 - sv, 834 - sv]:
        reg["c"].append(k)
o2 = json.load(open(WT / "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-engine-and-own.json"))
o2rows = {r["label"]: r["engine"] for r in o2["rows"]}
for k, r in inst.items():
    if r["arm"] != "NELL-A20":
        continue
    nreg["d"] += 1
    ref = o2rows[k.split(":", 1)[1]]
    w = cl[(k, "W_4")]
    if any(w.get(f) != ref[f] for f in ref if f != "certificate_emitted") or ref.get("certificate_emitted") != bool(w["one"]):
        reg["d"].append(k)
    if cl[(k, "R'_4")]["dims_by_deg"] != [0, 0, 16, 288, 2328]:
        reg["d"].append(k + " R'_4")
OUT["C-REG_recheck"] = {"checked": dict(nreg), "violations": {k: v for k, v in reg.items()},
                        "u62_idx893_present": any(arch[k]["idx"] == 893 for k in inst if inst[k]["arm"] == "S3-U62"),
                        "o2_fields_compared": sorted(next(iter(o2rows.values())).keys()),
                        "note": "field-by-field against archived bytes, independent of driver.py's comparison"}

# C-TOP
P = {k[0]: r["P"] for k, r in cl.items() if k[1] == "M_4"}
s3slot = {r["slot"]: k for k, r in inst.items() if r["arm"].startswith("S3-")}
top_bad = [k for k, r in inst.items() if r["arm"] in ("N-CONV", "N-CONVL") and P[k] != P[s3slot[r["slot"]]]]
OUT["C-TOP_recheck"] = {"checked": sum(1 for r in inst.values() if r["arm"] in ("N-CONV", "N-CONVL", "N-CONV17")),
                        "violations": top_bad,
                        "N-CONV17_distinct_P": sorted({P[k] for k, r in inst.items() if r["arm"] == "N-CONV17"}),
                        "distinct_P_by_arm": {a: sorted({P[k] for k, r in inst.items() if r["arm"] == a})
                                              for a in sorted({r["arm"] for r in inst.values()})}}

# C-ORACLE2 on the 288 archived-arm systems (own evaluator)
bad_s = []
n = 0
for k, r in inst.items():
    if r["arm"] in ("N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"):
        continue
    rows = [int(h, 16) for h in r["E_hex"]]
    s, sols = j2.count_s(rows, want=True)
    n += 1
    want_s = arch[k]["archived"]["s"] if k in arch else 0
    if s != r["s"] or s != want_s or (r["role"] == "sat" and sols != r.get("solutions")):
        bad_s.append(k)
OUT["C-ORACLE2_recheck_archived"] = {"checked": n, "violations": bad_s,
                                     "fresh": "covered in J2: every attempt's s and every kept control's solution list equal"}

# C-PS per arm (satisfiable controls)
ps = defaultdict(lambda: Counter())
for k, r in inst.items():
    if r["role"] != "sat":
        continue
    m4, w4 = cl[(k, "M_4")], cl[(k, "W_4")]
    c = ps[r["arm"]]
    c["n"] += 1
    c["refuted_M4_or_W4"] += int(bool(m4["one"] or w4["one"]))
    if r["s"] <= 31:
        cd = 4048 - w4["final_dim"]
        c["s<=31"] += 1
        c["codim==s"] += int(cd == r["s"])
        c["codim>s"] += int(cd > r["s"])
        c["codim<s"] += int(cd < r["s"])
        c["codim_values:" + str(cd)] += 1 if r["arm"] == "N-ELL144" else 0
    c["s_max"] = max(c["s_max"], r["s"])
    c["s_min"] = r["s"] if c["s_min"] == 0 else min(c["s_min"], r["s"])
OUT["C-PS_recheck"] = {a: {k2: v for k2, v in c.items() if v or not k2.startswith("codim_values")} for a, c in ps.items()}

# C-VERIFIER: own evaluation of every negative control
ncb = {c["nc_id"]: c for c in jl(RUN / "negative-controls-certificates.jsonl.gz")}
ncv = {c["nc_id"]: c for c in json.load(open(RUN / "negative-controls-verification.json"))["controls"]}


def deg(p):
    return max((bin(m).count("1") for m in p), default=-1)


def own_eval(c):
    F = masks(inst[c["key"]]["E_hex"])
    b = c["body"]
    if c["format"] == "flat-v1":
        acc = set()
        mx = 0
        for mu, k in b:
            mx = max(mx, len(mu))
            for m in F[k]:
                acc ^= {sum(1 << i for i in mu) | m}
        return {"sum_is_1": acc == {0}, "max_mu": mx,
                "violates": (["sum != 1"] if acc != {0} else []) + (["M_4 max|mu| > 2"] if c["closure"] == "M_4" and mx > 2 else [])}
    polys = {}
    v = []
    for nd in sorted(b["nodes"], key=lambda n: n["id"]):
        p = set()
        for mu, k in nd["rows"]:
            if len(mu) > 2:
                v.append("(b)")
            for m in F[k]:
                p ^= {sum(1 << i for i in mu) | m}
        for j, ch in nd["prods"]:
            if ch >= nd["id"]:
                v.append("(a)")
                continue
            if deg(polys[ch]) > 3:
                v.append("(c)")
            for m in polys[ch]:
                p ^= {m | (1 << j)}
        if deg(p) > 4:
            v.append("(d)")
        polys[nd["id"]] = p
    if polys[b["output"]] != {0}:
        v.append("(e)")
    return {"violates": sorted(set(v))}


tab = defaultdict(lambda: {"built": 0, "rejected_by_run_verifier": 0, "own_invalid": 0, "own_rules": Counter(), "sources": set()})
odd = []
for i, c in ncb.items():
    e = own_eval(c)
    t = tab[(c["kind"], c["type"])]
    t["built"] += 1
    t["rejected_by_run_verifier"] += int(ncv[i]["rejected"])
    t["own_invalid"] += int(bool(e["violates"]))
    for x in e["violates"]:
        t["own_rules"][x] += 1
    t["sources"].add(c["source_key"])
    if c["type"] == "c" and c["format"] == "wdag-v1" and "(e)" in e["violates"]:
        odd.append({"nc_id": i, "kind": c["kind"], "key": c["key"], "source_key": c["source_key"], "note": c.get("note"),
                    "own": e["violates"], "run_verifier_reason": ncv[i].get("reason")})
OUT["C-VERIFIER_table"] = {f"{k[0]}|{k[1]}": {"built": v["built"], "rejected_by_run_verifier": v["rejected_by_run_verifier"],
                                               "own_arith_invalid": v["own_invalid"], "own_rules_violated": dict(v["own_rules"]),
                                               "distinct_source_systems": len(v["sources"])} for k, v in sorted(tab.items())}
OUT["C-VERIFIER_type_c_wdag_with_output_not_1"] = odd

cv = json.load(open(RUN / "certificate-verification.json"))
OUT["C-CERT"] = {"n_submitted": cv["n_submitted"], "n_verified": cv["n_verified"], "n_failed": cv["n_failed"],
                 "lines_in_certificates_jsonl": sum(1 for _ in gzip.open(RUN / "certificates.jsonl.gz", "rt"))}
json.dump(OUT, open(OUTDIR / "j4-controls.json", "w"), indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
print(json.dumps(OUT, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))[:9000])
