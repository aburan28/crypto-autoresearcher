#!/usr/bin/env python3
"""Citation check for the record-curve a-invariants (TASK-20261022-a846f4, J3 second half).

Usage: source_check.py RK8_HTML RK9_HTML BLIND_SIEVE_JSON OUT_JSON

Parses the curve equation and the listed independent points from Dujella's
rk8.html / rk9.html (the sources the specification cites), compares the
a-invariants with the specification's verbatim values, verifies every listed
point on the curve with exact arithmetic, and checks that each listed point
with naive height <= 3 x 10^5 appears in the sealed blind point list.
Run before any blind_from path was opened.
"""
import hashlib
import json
import re
import sys
from fractions import Fraction

SPEC = {
    "rk8": ("grunewald_zimmert_1977_rank_ge_8", [1, -1, 1, -6494556985832, 6351402068900282539]),
    "rk9": ("brumer_kramer_1977_rank_ge_9", [1, -1, 1, -1608154463, 25555312501831]),
}
EQ = re.compile(
    r"y<sup>2</sup>\s*\+\s*xy\s*\+\s*y\s*=\s*x<sup>3</sup>\s*-\s*x<sup>2</sup>\s*([+-])\s*(\d+)x\s*([+-])\s*(\d+)")
PT = re.compile(r"P<sub>(\d+)</sub>\s*=\s*\[(-?\d+),\s*(-?\d+)\]")


def on_curve(ai, x, y):
    a1, a2, a3, a4, a6 = ai
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def main():
    rk8, rk9, sieve_json, out = sys.argv[1:5]
    blind = json.load(open(sieve_json))
    res = {"schema": "validator.source_check.v1", "task_id": "TASK-20261022-a846f4", "pages": {}}
    for key, path in (("rk8", rk8), ("rk9", rk9)):
        raw = open(path, "rb").read()
        txt = raw.decode("utf-8", "replace")
        m = EQ.search(txt)
        title = re.search(r'<p align=center>([^<]+)</p>', txt)
        ai_src = None
        if m:
            s4, v4, s6, v6 = m.groups()
            ai_src = [1, -1, 1, int(v4) * (1 if s4 == "+" else -1), int(v6) * (1 if s6 == "+" else -1)]
        name, ai_spec = SPEC[key]
        listed = []
        bpts = {(p["x"], p["y"]) for p in blind["curves"][name]["points"]}
        bxs = {p["x"] for p in blind["curves"][name]["points"]}
        for idx, x, y in PT.findall(txt):
            x, y = int(x), int(y)
            listed.append({
                "P": int(idx), "x": x, "y": y, "on_curve": on_curve(ai_spec, Fraction(x), Fraction(y)),
                "naive_height": abs(x),
                "in_blind_list_xy": (str(x), str(y)) in bpts,
                "in_blind_list_x": str(x) in bxs,
            })
        res["pages"][key] = {
            "file_sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "attribution": title.group(1).strip() if title else None,
            "a_invariants_from_source": ai_src, "a_invariants_spec": ai_spec,
            "match": ai_src == ai_spec, "listed_points": listed,
            "all_listed_on_curve": all(p["on_curve"] for p in listed),
            "all_listed_h_le_3e5_in_blind": all(p["in_blind_list_x"] for p in listed if p["naive_height"] <= 300000),
        }
    json.dump(res, open(out, "w"), indent=1)
    for k, v in res["pages"].items():
        print(k, v["attribution"], "match=", v["match"], "on_curve=", v["all_listed_on_curve"],
              "listed_in_blind=", v["all_listed_h_le_3e5_in_blind"],
              [(p["P"], p["naive_height"], p["in_blind_list_x"]) for p in v["listed_points"]])


if __name__ == "__main__":
    main()
