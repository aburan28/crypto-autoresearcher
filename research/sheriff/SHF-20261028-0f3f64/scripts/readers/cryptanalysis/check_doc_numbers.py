#!/usr/bin/env python3
"""Check every §5a band number quoted in the README, docs/ic/baselines.json open item and
docs/ic/BASELINES.md against the independently re-derived values (out/reimpl_result.json).

A quoted number passes when it equals the derived value rounded to the quoted number of significant
figures (trailing zeros count: "29.00" claims 4 significant figures). Reads the clone as data only.
"""
import json
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path

CLONE = Path(sys.argv[1])
RES = json.loads(Path(sys.argv[2]).read_text())
OUT = Path(sys.argv[3])
EXP = CLONE / "experiments/koblitz-n83-opcounts-20261023"

band = RES["band"]
frob = RES["band_frobenius_as_group"]


def sig(q):
    """significant figures claimed by a quoted decimal string"""
    s = q.lstrip("0").replace(".", "")
    if "." in q and q.startswith("0"):
        s = q.split(".")[1].lstrip("0")
    elif "." not in q:
        s = q.rstrip("0") or "0"
    return len(s)


def rounds_to(value, quoted):
    """value rounded to len(sig(quoted)) significant figures equals quoted (half-up and half-even both tried)"""
    q = Decimal(quoted)
    n = sig(quoted)
    if value == 0:
        return q == 0
    e = math.floor(math.log10(abs(value)))
    quant = Decimal(1).scaleb(e - n + 1)
    ok = []
    for mode in (ROUND_HALF_UP, ROUND_HALF_EVEN):
        ok.append(Decimal(repr(value)).quantize(quant, rounding=mode) == q)
    return any(ok)


def gap(arm, w, j=0, which="ratio", b=band):
    cell = b["gap"][arm][w][j]
    if which == "ratio":
        return cell["ratio"]
    return cell["ci_declared"][0 if which == "lo" else 1]


def pair_ratio(name, w, b=band, bidx=0):
    cells = [c for c in b["pairs"][name]["cells"] if abs(c["w"] - w) < 1e-12 and abs(c["b"] - (0 if bidx == 0 else 104)) < 1e-9]
    return cells[0]["ratio"]


W = {"0": "0", "0.1": "0.1", "1": "1"}
expected = []  # (label, derived value, quoted string)
for arm, vals in (("S", [("0", "0.01138", "0.008767", "0.01552"), ("0.1", "29.00", "22.33", "39.54"), ("1", "115.5", "88.94", "157.5")]),
                  ("P", [("0", "0.01141", "0.00879", "0.01556"), ("0.1", "43.93", "33.83", "59.92"), ("1", "175.0", "134.8", "238.7")])):
    for w, r, lo, hi in vals:
        wk = {"0": "0", "0.1": "1/10", "1": "1"}[w]
        expected.append(("%s gap w=%s" % (arm, w), gap(arm, wk), r))
        expected.append(("%s gap w=%s ci_lo" % (arm, w), gap(arm, wk, which="lo"), lo))
        expected.append(("%s gap w=%s ci_hi" % (arm, w), gap(arm, wk, which="hi"), hi))
for arm, vals in (("S", ["56.08", "70.99", "115.5"]), ("P", ["84.00", "106.8", "175.0"])):
    for wk, q in zip(("0", "1/10", "1"), vals):
        expected.append(("%s/rT Frobenius-sensitivity w=%s" % (arm, wk), gap(arm, wk, b=frob), q))
expected += [("S/rT Frob w=0 ci_lo", gap("S", "0", which="lo", b=frob), "43.18"),
             ("S/rT Frob w=0 ci_hi", gap("S", "0", which="hi", b=frob), "76.48"),
             ("P/rT Frob w=0 ci_lo", gap("P", "0", which="lo", b=frob), "64.69"),
             ("P/rT Frob w=0 ci_hi", gap("P", "0", which="hi", b=frob), "114.6")]
for w, q in ((0.0, "0.9973"), (0.1, "0.6600"), (1.0, "0.6599")):
    expected.append(("S/P w=%s" % w, pair_ratio("S vs P", w), q))
for arm, g, u in (("S", "1.011e5", "3.093e9"), ("P", "1.014e5", "4.688e9"), ("rT", "8.882e6", "1.79e7")):
    m, e = g.split("e"); expected.append(("%s mean group ops" % arm, band["arms"][arm]["mean_group"] / 10 ** int(e), m))
    m, e = u.split("e"); expected.append(("%s mean unpriced ops" % arm, band["arms"][arm]["mean_unpriced"] / 10 ** int(e), m))

results = []
for label, value, quoted in expected:
    results.append({"label": label, "derived": value, "quoted": quoted, "pass": rounds_to(value, quoted)})

# Where each quoted string appears
readme = (EXP / "README.md").read_text()
bmd = (CLONE / "docs/ic/BASELINES.md").read_text()
bj = json.loads((CLONE / "docs/ic/baselines.json").read_text())
open5 = [s for s in bj["open"] if "section 5a 0 / 0.1 / 1 GAE band for the stacked producer row" in s]
bullet = bmd[bmd.index("**n=83, §5a band (stacked producer row"):]
bullet = bullet[:bullet.index("- **n=83, construction time X")]
docs = {"README": readme[readme.index("## Results: run 39882571652"):readme.index("## What is left")],
        "baselines.json open": open5[0] if open5 else "", "BASELINES.md bullet": bullet}
presence = {}
for label, value, quoted in expected:
    presence[label] = {d: (quoted in t) for d, t in docs.items()}

# Other quoted claims
max_move = 0.0
for b in (band, frob):
    for arm in ("S", "P"):
        for w, cells in b["gap"][arm].items():
            a, c = cells[0], cells[1]
            for k in ("ratio",):
                max_move = max(max_move, abs(c[k] - a[k]) / a[k])
            for i in (0, 1):
                max_move = max(max_move, abs(c["ci_declared"][i] - a["ci_declared"][i]) / a["ci_declared"][i])
other = {
    "max relative move of any gap cell (ratio or CI bound) from 0 to 104 GAE": max_move,
    "claim '< 0.1%' holds": max_move < 1e-3,
    "1 / (S gap at w=0) ('about 88x cheaper')": 1 / gap("S", "0"),
    "S gap at w=0.1, w=1 ('29x to 116x dearer')": [gap("S", "1/10"), gap("S", "1")],
}
# README's 'mean group ops' rounding uses 4 s.f. but writes 1.79e7 for rT unpriced (3 s.f. of 1.790e7?)
other["rT mean unpriced exact"] = band["arms"]["rT"]["mean_unpriced"]

summary = {"quoted_numbers": len(results), "pass": sum(r["pass"] for r in results),
           "fail": [r for r in results if not r["pass"]], "presence": presence, "other": other, "results": results}
OUT.write_text(json.dumps(summary, indent=1) + "\n")
print(json.dumps({"quoted_numbers": summary["quoted_numbers"], "pass": summary["pass"], "fail": summary["fail"],
                  "other": other}, indent=1))
missing = {k: v for k, v in presence.items() if not all(v.values())}
print("labels not quoted in all three docs:", json.dumps(missing, indent=0))
