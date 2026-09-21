#!/usr/bin/env python3
"""J3.4 (cont.): recompute aggregate_total by running the committed certifier
(certify76.certify_instance) on a subset of R3 instances, using the recorded
instance fields + the coset from the R3 raw. Compare to the recorded
certificate aggregate_total / n_classes / class_keys / verdict."""
import json, os, sys
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/ecrank-73275e-review-20260908"
SRC = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", ROOT)
R3 = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json")

import ecrank_engine as E
import certify76 as C

with open(R3) as f: r3 = json.load(f)
cosets = E.eligible_cosets()
target_V = sorted(r3["coset_V"])
# The R3 raw records only coset_V (the direction space). The exact coset
# (m0, hence members) is recovered by requiring the first instance's class
# values to be coset member class values.
need0 = set(int(k) for k in r3["found"][0]["certificate"]["class_keys"])
cands = [c for c in cosets if sorted(c["V"]) == target_V
         and need0.issubset(set(E.class_value(m) for m in c["members"]))]
assert len(cands) == 1, "expected exactly one coset, got %d" % len(cands)
coset = cands[0]
print("coset used: m0=%s members=%s" % (coset.get("m0"), coset["members"]))
print("coset class values:", sorted(E.class_value(m) for m in coset["members"]))
# sanity: every instance's class_keys must be a subset of the coset class values
allcv = set(E.class_value(m) for m in coset["members"])
for rec in r3["found"]:
    ck = set(int(k) for k in rec["certificate"]["class_keys"])
    assert ck.issubset(allcv), "class_keys not in coset: %s" % ck
print("all 28 instances' class_keys are coset member class values: True")
ec, digest = E.load_exact_certify(ROOT)
assert digest == E.EXACT_CERTIFY_SHA

# pick a spread: indices 0 (agg 6), 4 (agg 2), 6 (agg 2), 8 (agg 6), 20 (agg 6)
picks = [0, 4, 6, 8, 20]
print("=== J3.4 aggregate_total recomputation via committed certifier ===")
for idx in picks:
    rec = r3["found"][idx]
    inst = rec["instance"]; cert_rec = rec["certificate"]
    cert = C.certify_instance(inst, coset, ec)
    agg = cert.get("aggregate_total")
    nc = len(cert.get("classes", {}))
    ck = sorted(str(k) for k in cert.get("classes", {}))
    verdict = cert.get("verdict")
    ok_agg = (agg == cert_rec["aggregate_total"])
    ok_nc = (nc == cert_rec["n_classes"])
    ok_ck = (ck == cert_rec["class_keys"])
    ok_v = (verdict == cert_rec["verdict"])
    print("idx=%d b_index=%s recorded(agg=%s nc=%s ck=%s v=%s) -> recomputed(agg=%s nc=%s ck=%s v=%s) %s" % (
        idx, rec["b_index"], cert_rec["aggregate_total"], cert_rec["n_classes"],
        cert_rec["class_keys"], cert_rec["verdict"], agg, nc, ck, verdict,
        "PASS" if (ok_agg and ok_nc and ok_ck and ok_v) else "FAIL"))
    # per-class certified for transparency
    for d, pc in sorted(cert.get("classes", {}).items()):
        print("    class %s: certified_Fl=%s eig_unit=%s n_pts=%s" % (
            d, pc["certified_Fl_within_class"], pc["eig_unit"], pc["n_forced_points"]))
    print("    aggregate_raw_sum=%s eig_units=%s fl_units=%s" % (
        cert.get("aggregate_raw_sum_certified"), cert.get("eig_units"), cert.get("fl_units")))
