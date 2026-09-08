#!/usr/bin/env python3
"""J1 n=8 certified-total localization.

Reconstructs the R7 n=8 b-tuples from seed 760812, builds each d=(1..1)
instance, runs the committed F_l certifier (byte-identical exact_certify) via
certify76.certify_instance, and reports aggregate_total per tuple.
Localizes every shortfall vs expected 7.
"""
import os, sys, json, random
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../../../../../.."))
SRC = os.path.join(REPO, "experiments/EXP-ECRANK-73275e/source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", REPO)

import ecrank_engine as E
import construct as CT
import certify76 as C

B_INTS = CT.B_INTS

def reconstruct_r7_n8():
    rng = random.Random(760812)
    # consume the n=6 draws first (8 tuples x 4)
    for bi in range(8):
        rng.sample(B_INTS, 4)
    per = []
    for bi in range(8):
        rest = rng.sample(B_INTS, 6)
        b = [Fr(0), Fr(1)] + [Fr(x) for x in rest]
        per.append(b)
    return per

tuples = reconstruct_r7_n8()

# the coset exactly as run_r7() selects it
cosets = E.eligible_cosets()
coset = next(c for c in cosets if 1 in [E.class_value(m) for m in c["members"]])
print("coset m0 =", coset["m0"], "V =", coset["V"])
print("coset member values =", [E.class_value(m) for m in coset["members"]])

ec, digest = E.load_exact_certify(REPO)
print("exact_certify sha ok:", digest == E.EXACT_CERTIFY_SHA)

recorded = [5, 6, 7, 7, 7, 7, 6, 7]
print("\n%-4s %-40s %-6s %-6s %-8s %-8s" % ("bi", "b", "built", "deg_s", "agg_tot", "recorded"))
for bi, b in enumerate(tuples):
    p, g, s = E.mestre_polys(list(b))
    r = [E.peval(g, x) for x in b]
    inst, why = E.build_instance(list(b), [1]*8, r, 8)
    if inst is None:
        print("%-4d %-40s %-6s %-6s %-8s %-8s  REJECTED %s" % (bi, [str(x) for x in b], False, "-", "-", recorded[bi], why))
        continue
    cert = C.certify_instance(inst, coset, ec)
    agg = cert.get("aggregate_total")
    raw = cert.get("aggregate_raw_sum_certified")
    eig = cert.get("eig_units")
    fl = cert.get("fl_units")
    verdict = cert.get("verdict")
    strict = cert.get("errors_strict")
    withholds = cert.get("withholds")
    # per-class certified
    classes = cert.get("classes", {})
    cls_cert = {k: v["certified_Fl_within_class"] for k, v in classes.items()}
    print("%-4d %-40s %-6s %-6s %-8s %-8s  raw=%s eig=%s fl=%s verdict=%s strict=%s" % (
        bi, [str(x) for x in b], True, inst["deg_s"], agg, recorded[bi], raw, eig, fl, verdict, strict))
    if withholds:
        print("      withholds:", json.dumps(withholds))
    print("      classes certified:", cls_cert)
