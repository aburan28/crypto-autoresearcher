#!/usr/bin/env python3
"""Check every number in README.md / REPORT.typ (and REPORT.pdf text, which
equals REPORT.typ) that is a ratio, interval, S, band value or percent
against the blind re-derivation. A displayed number matches when it equals
my value rounded to the displayed precision (half-up, as printf does).

Usage: python3 -I check_prose.py <campaign_dir> <rederive_out.json>
"""
import json
import sys
from decimal import ROUND_HALF_EVEN, Decimal

camp, mine_p = sys.argv[1], sys.argv[2]
M = json.load(open(mine_p))
R, C = ["r24", "r26", "r28"], ["c24", "c28", "c30"]
readme = open(f"{camp}/README.md").read().splitlines()
typ = open(f"{camp}/REPORT.typ").read().splitlines()


def disp(x, shown):
    """Round x to the precision of the displayed string `shown`."""
    if "." in shown:
        q = Decimal(1).scaleb(-len(shown.split(".")[1]))
    else:
        q = Decimal(1)
    return str(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_EVEN))


def cmp(s, a):
    return M[s]["compare"][f"plan__{a}"]


def bandr(s, a, wi):
    return M[s]["band_ratios"][a]["per_weight"][wi]["ratio_of_band_means"]


def bm(s, a, wi):
    return M[s]["band"][a]["mean_s"][wi]


pr = lambda s: M[s]["compare"]["rho-neg__plan"]
PRED = {"r24": 12.233956652458087, "r26": 14.453197377819107, "r28": 20.078173411100984,
        "c24": 11.461210709103137, "c28": 19.325980413591978, "c30": 24.54954651510073}
res = []


def check(where, shown, value, note=""):
    ok = disp(value, shown) == shown
    res.append((where, shown, f"{value:.6g}", "match" if ok else "MISMATCH", note))


def find(lines, needle, fname):
    for i, l in enumerate(lines, 1):
        if needle in l:
            return f"{fname}:{i}"
    return f"{fname}:?"


ARMROW = {"half-base": "base ⌈N/2⌉", "double-base": "base 2N", "rootfind": "rootfind",
          "full-rank": "full-rank", "random-targets": "random targets"}
SHOWN = {  # README table rows 34-38 (identical strings in REPORT.typ:29-33)
    "half-base": [("1.56", "1.35", "1.77"), ("1.55", "1.41", "1.69"), ("1.43", "1.28", "1.60")],
    "double-base": [("1.51", "1.40", "1.64"), ("1.60", "1.50", "1.70"), ("1.57", "1.49", "1.68")],
    "rootfind": [("171", "164", "176"), ("233", "226", "239"), ("439", "424", "450")],
    "full-rank": [("3.64", "3.24", "4.14"), ("3.84", "3.43", "4.21"), ("4.56", "4.10", "5.12")],
    "random-targets": [("44.8", "39.0", "50.6"), ("49.1", "43.7", "54.0"), ("51.5", "43.8", "58.5")],
}
for fname, lines in (("README.md", readme), ("REPORT.typ", typ)):
    for arm, cells in SHOWN.items():
        loc = find(lines, ARMROW[arm] if arm != "full-rank" else "full-rank stop", fname)
        for s, (p, lo, hi) in zip(R, cells):
            c = cmp(s, arm)
            check(loc, p, c["ratio"], f"{s} {arm}/plan")
            check(loc, lo, c["ci95"][0], f"{s} {arm} lo")
            check(loc, hi, c["ci95"][1], f"{s} {arm} hi")
    loc = find(lines, "A/A", fname)
    for s in R:
        check(loc, "1.000", cmp(s, "plan-aa")["ratio"], f"{s} A/A")
    # supplementary ranges
    loc = find(lines, "1.36–1.53", fname)
    for arm, lo, hi in (("half-base", "1.36", "1.53"), ("double-base", "1.49", "1.60"),
                        ("rootfind", "150", "637"), ("full-rank", "3.30", "4.81"),
                        ("random-targets", "41.5", "58.7")):
        v = [cmp(s, arm)["ratio"] for s in C]
        check(loc, lo, min(v), f"supplementary {arm} min")
        check(loc, hi, max(v), f"supplementary {arm} max")
    # rho table
    loc = find(lines, "14.4 [11.6, 18.5]", fname)
    ROWS = {"r24": ("12.2", "14.4", "11.6", "18.5"), "r26": ("14.5", "14.6", "11.2", "19.6"),
            "r28": ("20.1", "21.7", "17.0", "28.3"), "c24": ("11.5", "12.6", "9.75", "16.5"),
            "c28": ("19.3", "21.8", "17.0", "29.8"), "c30": ("24.5", "25.8", "19.9", "35.2")}
    for s, (pp, m, lo, hi) in ROWS.items():
        check(loc, pp, PRED[s], f"{s} predicted")
        check(loc, m, pr(s)["ratio"], f"{s} plan/rho")
        check(loc, lo, pr(s)["ci95"][0], f"{s} plan/rho lo")
        check(loc, hi, pr(s)["ci95"][1], f"{s} plan/rho hi")
    # percent statements
    loc = find(lines, "2–8%", fname)
    pct = {s: 100 * (1 - bandr(s, "double-base", 2)) for s in R + C}
    check(loc, "2", min(pct[s] for s in R), "registered: double cheaper than plan at w=1, min %")
    check(loc, "8", max(pct[s] for s in R), "registered: max %")
    check(loc, "4", min(pct[s] for s in C), "supplementary: min %")
    check(loc, "9", max(pct[s] for s in C), "supplementary: max %")
    loc = find(lines, "within 18%", fname)
    dev = {s: 100 * (pr(s)["ratio"] / PRED[s] - 1) for s in R + C}
    check(loc, "18", max(dev.values()), "max |measured/pred - 1| %")
    check(loc, "1", min(dev.values()), "min (measured/pred - 1) % ('1–18%')")
    loc = find(lines, "12.6", fname)
    check(loc, "12.6", min(pr(s)["ratio"] for s in R + C), "min plan/rho")
    check(loc, "25.8", max(pr(s)["ratio"] for s in R + C), "max plan/rho")

# README-only lines 59-61 (S at w=1) and P2/P3 ranges, log2 r
for s, d, p in (("r24", "29.6", "32.3"), ("r26", "35.1", "35.7"), ("r28", "45.1", "48.4")):
    loc = find(readme, f"{s}: {d} against", "README.md")
    check(loc, d, bm(s, "double-base", 2), f"{s} double-base S(w=1)")
    check(loc, p, bm(s, "plan", 2), f"{s} plan S(w=1)")
loc = find(readme, "Measured\n", "README.md")
loc = find(readme, "1.36–1.56", "README.md")
v = [cmp(s, "half-base")["ratio"] for s in R + C]
check(loc, "1.36", min(v), "P2 half min"); check(loc, "1.56", max(v), "P2 half max")
v = [cmp(s, "double-base")["ratio"] for s in R + C]
check(loc, "1.49", min(v), "P2 double min"); check(loc, "1.60", max(v), "P2 double max")
loc = find(readme, "150–637×", "README.md")
for arm, lo, hi in (("rootfind", "150", "637"), ("full-rank", "3.30", "4.81"), ("random-targets", "41.5", "58.7")):
    v = [cmp(s, arm)["ratio"] for s in R + C]
    check(loc, lo, min(v), f"P3 {arm} min"); check(loc, hi, max(v), f"P3 {arm} max")
for s, shown in (("r24", "24.00"), ("r26", "25.35"), ("r28", "28.00"), ("c24", "23.47"), ("c28", "27.69"), ("c30", "29.62")):
    check(find(readme, shown, "README.md"), shown, M[s]["curve"]["log2_r"], f"{s} log2 r")
for s, shown in (("r24", "24.0"), ("r26", "25.3"), ("r28", "28.0"), ("c24", "23.5"), ("c28", "27.7"), ("c30", "29.6")):
    check(find(typ, "log#sub[2] r", "REPORT.typ"), shown, M[s]["curve"]["log2_r"], f"{s} log2 r")
# README:84 "Every prediction lies inside the measured interval"
inside = all(pr(s)["ci95"][0] <= PRED[s] <= pr(s)["ci95"][1] for s in R + C)
res.append((find(readme, "Every prediction lies inside", "README.md"), "inside", str(inside),
            "match" if inside else "MISMATCH", "all six predictions inside plan/rho CI"))

for r in res:
    print(*r, sep="\t")
bad = [r for r in res if r[3] != "match"]
print(f"checked {len(res)} prose numbers; mismatches {len(bad)}")
for r in bad:
    print("MISMATCH", *r, sep="\t")
