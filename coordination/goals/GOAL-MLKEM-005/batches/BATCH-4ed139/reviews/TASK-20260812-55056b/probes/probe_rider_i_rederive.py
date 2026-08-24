#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAL TASK-20260812-55056b probe E -- INDEPENDENT re-derivation of rider (i).

Reads ONLY the committed, pinned source
    BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json
    sha256 c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d
and re-derives, from scratch, every count rider (i) reports. It does NOT read
tabulate_c1res.py or results_c1res.json. Rider (i) adjudicates a direct
contradiction between two prior validators and must not be taken on trust.

Checks, in the order the task card names them:
  (1) bit-identity of the 8 per-basis values at all 29 entries, BOTH
      normalizations -- the claim that the READING AXIS cannot explain C-1;
  (2) wave 1's "15 of 19 G-REL2 below 6x" under maxfloor + RULE B;
  (3) that wave 2's "two of 29" corresponds to a 5.71x threshold, not a 6x one;
  (4) the agreed range 4.87x-31.03x and its minimum's location;
  (5) the IEEE boundary 6.0*0.10 = 0.6000000000000001;
  (6) the absX qualifier 5.71x-37.50x.

Standard library only. Read-only. Run from the repository root.
"""
import hashlib
import json
import math
import sys

SRC = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
       "TASK-20260809-cda2f6/results_relvar.json")
EXPECT_SHA = "c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d"
TAU_REL = 0.10
NORMS = ("value_maxfloor", "value_absX")


def readings(per_basis, norm):
    """The THREE declared readings of PREREG-1 8.1, computed independently."""
    vals = [pb[norm] for pb in per_basis]
    r_i0 = vals[0]
    r_npass = sum(1 for v in vals if v >= TAU_REL)
    r_mean = math.fsum(vals) / len(vals)
    return vals, r_i0, r_npass, r_mean


def main():
    h = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    print("source sha256 :", h)
    print("expected      :", EXPECT_SHA)
    print("PINNED SOURCE MATCHES:", h == EXPECT_SHA)
    d = json.load(open(SRC))

    entries = []          # (kind, label, per_basis)
    for lat, rec in d["G_REL1"]["null"].items():
        entries.append(("G-REL1", lat, rec["per_basis"]))
    for pair, betas in d["G_REL2"]["null"].items():
        for beta, rec in betas.items():
            entries.append(("G-REL2", "%s_b%s" % (pair, beta),
                            rec["per_basis"]))
    n_rel1 = sum(1 for e in entries if e[0] == "G-REL1")
    n_rel2 = sum(1 for e in entries if e[0] == "G-REL2")
    print(f"\nentries: G-REL1 {n_rel1}, G-REL2 {n_rel2}, total {len(entries)}")
    assert len(entries) == 29, len(entries)

    # ---- (1) bit-identity and reading coincidence
    print("\n=== (1) BIT-IDENTITY OF THE 8 PER-BASIS VALUES ===")
    nonident = []
    reading_disagree = []
    for norm in NORMS:
        for kind, label, pb in entries:
            vals, r_i0, r_npass, r_mean = readings(pb, norm)
            hexes = {float(v).hex() for v in vals}
            if len(hexes) != 1:
                nonident.append((norm, kind, label, len(hexes)))
            # do the three declared readings return the same double?
            if not (float(r_i0).hex() == float(r_mean).hex()
                    and r_npass == len(vals)):
                reading_disagree.append((norm, kind, label, r_i0, r_npass,
                                         r_mean))
    print(f"  entries x normalizations checked : {len(entries) * len(NORMS)}")
    print(f"  entries with >1 distinct IEEE-754 value over 8 bases : "
          f"{len(nonident)}")
    for x in nonident[:10]:
        print("     ", x)
    print(f"  entries where the three declared readings do NOT coincide "
          f"bitwise (i0 vs fsum-mean, and n_pass != 8) : "
          f"{len(reading_disagree)}")
    for x in reading_disagree[:10]:
        print("     ", x)
    print("  VERDICT on rider (i) OBSERVATION 1 "
          "(the reading axis cannot explain C-1):",
          "CONFIRMED" if not nonident and not reading_disagree
          else "CONTRADICTED")

    # ---- (5) the boundary constant
    print("\n=== (5) THE IEEE BOUNDARY ===")
    b = 6.0 * TAU_REL
    print(f"  6.0 * 0.10 = {b!r}   == 0.6 ? {b == 0.6}")
    print(f"  repr(0.6)  = {0.6!r}   b > 0.6 ? {b > 0.6}")

    # ---- counts per normalization and boundary rule
    print("\n=== (2)(3)(4)(6) COUNTS, PER NORMALIZATION AND BOUNDARY RULE ===")
    out = {}
    for norm in NORMS:
        vals_by_kind = {"G-REL1": [], "G-REL2": []}
        for kind, label, pb in entries:
            v = pb[0][norm]
            vals_by_kind[kind].append((v, label))
        allv = vals_by_kind["G-REL1"] + vals_by_kind["G-REL2"]

        def below_A(v):                       # strict IEEE
            return v < b

        def below_B(v):                       # within 1e-12 relative == AT 6x
            return v < b and abs(v - b) / b > 1e-12

        rowA2 = sum(1 for v, _ in vals_by_kind["G-REL2"] if below_A(v))
        rowB2 = sum(1 for v, _ in vals_by_kind["G-REL2"] if below_B(v))
        rowA1 = sum(1 for v, _ in vals_by_kind["G-REL1"] if below_A(v))
        rowB1 = sum(1 for v, _ in vals_by_kind["G-REL1"] if below_B(v))
        at6 = sum(1 for v, _ in vals_by_kind["G-REL2"]
                  if abs(v - b) / b <= 1e-12)
        four_sevenths = 4.0 / 7.0
        at571 = sum(1 for v, _ in allv
                    if abs(v - four_sevenths) / four_sevenths <= 1e-12)
        bitwise471 = sum(1 for v, _ in vals_by_kind["G-REL2"]
                         if float(v).hex() == float(four_sevenths).hex())
        strictly_below_571 = [(v, lab) for v, lab in allv
                              if v < four_sevenths
                              and abs(v - four_sevenths) / four_sevenths > 1e-12]
        mn = min(allv)
        mx = max(allv)
        out[norm] = dict(rowA2=rowA2, rowB2=rowB2, rowA1=rowA1, rowB1=rowB1,
                         at6=at6, at571=at571, bitwise471=bitwise471,
                         strictly_below_571=strictly_below_571, mn=mn, mx=mx)
        print(f"\n  --- {norm} ---")
        print(f"    min  {mn[0]!r} = {mn[0]/TAU_REL:.4f}x  at {mn[1]}")
        print(f"    max  {mx[0]!r} = {mx[0]/TAU_REL:.4f}x  at {mx[1]}")
        print(f"    below 6x RULE A (strict): {rowA2} of {n_rel2} G-REL2, "
              f"{rowA1} of {n_rel1} G-REL1, {rowA2 + rowA1} of 29")
        print(f"    below 6x RULE B (1e-12) : {rowB2} of {n_rel2} G-REL2, "
              f"{rowB1} of {n_rel1} G-REL1, {rowB2 + rowB1} of 29")
        print(f"    at 6x within 1e-12      : {at6} of {n_rel2} G-REL2")
        print(f"    at 4/7=5.7143x w/in 1e-12: {at571} of 29")
        print(f"    bitwise == 4/7          : {bitwise471} of {n_rel2} G-REL2")
        print(f"    STRICTLY below 5.7143x  : {len(strictly_below_571)} of 29 "
              f"-> {[(round(v,6), lab) for v, lab in strictly_below_571]}")
        # the multiset
        from collections import Counter
        c = Counter(round(v / TAU_REL, 4) for v, _ in allv)
        print(f"    multiset of ratios      : "
              f"{sorted(c.items())}")

    # ---- adjudication of the two conflicting counts
    print("\n=== THE TWO CONFLICTING COUNTS, ADJUDICATED INDEPENDENTLY ===")
    mf = out["value_maxfloor"]
    ax = out["value_absX"]
    print(f"  wave 1 'FIFTEEN of the 19 G-REL2 below 6x'")
    print(f"    maxfloor + RULE B -> {mf['rowB2']} of 19   "
          f"{'REPRODUCES' if mf['rowB2'] == 15 else 'DOES NOT REPRODUCE'}")
    print(f"    maxfloor + RULE A -> {mf['rowA2']} of 19")
    print(f"    absX     + RULE B -> {ax['rowB2']} of 19")
    print(f"    wave 1's '13 at 5.71x'  -> maxfloor at571 (over 29) = "
          f"{mf['at571']}")
    print(f"  wave 2 'TWO of 29 below 6x'")
    smallest = min(mf["rowA2"] + mf["rowA1"], mf["rowB2"] + mf["rowB1"],
                   ax["rowA2"] + ax["rowA1"], ax["rowB2"] + ax["rowB1"])
    print(f"    smallest 'below 6x' count over any normalization x rule "
          f"= {smallest}  -> a count of 2 "
          f"{'DOES NOT REPRODUCE' if smallest != 2 else 'reproduces'}")
    print(f"    entries STRICTLY below the 4/7 = 5.7143x plateau (maxfloor) "
          f"= {len(mf['strictly_below_571'])}  -> a 5.71x threshold yields "
          f"{len(mf['strictly_below_571'])}")
    print("    CONCLUSION: the count of 2 corresponds to a 5.71x threshold, "
          "NOT a 6x one." if len(mf["strictly_below_571"]) == 2
          else "    CONCLUSION: NOT ESTABLISHED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
