#!/usr/bin/env python3
"""VAL TASK-20260812-55056b probe B: classify the fixture-rebuild differences.

Both committed fixtures are re-run by the Validator and their outputs compared
to the COMMITTED outputs. The question this probe answers is not "are the JSONs
equal" (they are not, and the reason matters) but:

  (1) which routes carry any difference at all,
  (2) what the maximum RELATIVE difference is per route,
  (3) whether ANY qualitative field -- bit_identical, G_VAR_REFUSES,
      ESCAPES_G_VAR_WHILE_BLIND, pass/fail Booleans, integer counts -- differs.

(3) is the load-bearing one: the lead's F0 FAILURE rests on bit-identity being
broken on the fibre under R2/R4/R5, and on it holding under R0/R1/R3. If the
Booleans reproduce while the last ulps do not, the failure is environment-robust
and the float values are not.

Read-only apart from printing. Run from the repository root.
"""
import json
import sys

BASE = "coordination/goals/GOAL-MLKEM-005/batches"
MINE = (f"{BASE}/BATCH-4ed139/reviews/TASK-20260812-55056b/probes")

PAIRS = [
    ("F0/probe_nullroute",
     f"{BASE}/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/"
     "probe_nullroute_output.json",
     f"{MINE}/rebuild_probe_nullroute_output.json"),
    ("F1/probe_gvar_family",
     f"{BASE}/BATCH-9e3584/reviews-wave2/TASK-20260812-aadafd/probes/"
     "probe_gvar_family.json",
     f"{MINE}/rebuild_probe_gvar_family.json"),
]

SKIP_KEYS = {"seconds", "environment", "git_revision", "wall_clock_seconds"}


def walk(x, y, path, out):
    if isinstance(x, dict):
        for k in x:
            if k in SKIP_KEYS:
                continue
            if k not in y:
                out.append((path + "/" + k, "MISSING", None, "bool/struct"))
                continue
            walk(x[k], y[k], path + "/" + k, out)
    elif isinstance(x, list):
        if len(x) != len(y):
            out.append((path, len(x), len(y), "bool/struct"))
            return
        for i, (u, v) in enumerate(zip(x, y)):
            walk(u, v, f"{path}[{i}]", out)
    else:
        if x == y:
            return
        if isinstance(x, bool) or isinstance(y, bool) or x is None or y is None:
            kind = "QUALITATIVE"
        elif isinstance(x, int) and isinstance(y, int):
            kind = "QUALITATIVE"
        elif isinstance(x, str) or isinstance(y, str):
            kind = "QUALITATIVE"
        else:
            kind = "float"
        out.append((path, x, y, kind))


def main():
    bad = 0
    for name, cpath, rpath in PAIRS:
        c = json.load(open(cpath))
        r = json.load(open(rpath))
        diffs = []
        walk(c, r, "", diffs)
        qual = [d for d in diffs if d[3] != "float"]
        flt = [d for d in diffs if d[3] == "float"]
        print(f"=== {name} ===")
        print(f"  committed: {cpath}")
        print(f"  rebuilt:   {rpath}")
        print(f"  total differing scalars : {len(diffs)}")
        print(f"  QUALITATIVE differences : {len(qual)}   "
              "(bools, ints, strings, structure)")
        for q in qual[:40]:
            print(f"    {q[0]}: committed={q[1]!r} rebuilt={q[2]!r}")
        print(f"  float-only differences  : {len(flt)}")
        # per-route breakdown and max relative difference
        byroute = {}
        worst = 0.0
        for p, a, b, _ in flt:
            tag = "OTHER"
            for rt in ("R0_closed_form", "R1_slogdet", "R2_QR_of_BT",
                       "R3_slogdet_of_UB", "R4_gram_half_slogdet",
                       "R5_slogdet_of_BH"):
                if rt in p:
                    tag = rt
                    break
            rel = abs(a - b) / max(abs(a), abs(b)) if max(abs(a), abs(b)) else 0.0
            byroute.setdefault(tag, [0, 0.0])
            byroute[tag][0] += 1
            byroute[tag][1] = max(byroute[tag][1], rel)
            worst = max(worst, rel)
        for tag, (n, mx) in sorted(byroute.items()):
            print(f"    {tag:24s} n={n:5d}  max_rel_diff={mx:.3e}")
        print(f"  MAX RELATIVE FLOAT DIFFERENCE ANYWHERE: {worst:.3e}")
        print(f"  VERDICT: qualitative fields "
              f"{'REPRODUCE EXACTLY' if not qual else 'DIFFER  <<< DEFECT'}")
        print()
        bad += len(qual)
    print("QUALITATIVE REPRODUCTION ACROSS BOTH FIXTURES:",
          "CLEAN" if bad == 0 else f"{bad} DIFFERENCES")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
