"""Checker for EXP-CZLIFT-14f6d5: verifies sample points on the retrieved curves, re-counts at H = 300, re-derives the summary."""
from __future__ import annotations
import json, math, os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run as driver  # noqa: E402


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr); return 1
    rd = args[0]
    raw = json.load(open(os.path.join(rd, "raw-result.json"))); man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    if man["experiment_id"] != driver.EXP_ID or man["status"] != "completed_valid":
        print("manifest mismatch", file=sys.stderr); return 1
    Cm = driver.load_c()
    curves = raw["raw"]["curves"]
    if [c["label"] for c in curves] != [c[0] for c in driver.CURVES] or [c["ainvs"] for c in curves] != [c[1] for c in driver.CURVES]:
        print("curve list or equations differ from the frozen retrieved list", file=sys.stderr); return 1
    for cv in curves:
        b2, b4, b6, _ = Cm.b_invariants(cv["ainvs"])
        for a, d, c in cv["points_sample"]:
            if Cm.g_exact(a, d, b2, b4, b6) != c * c or math.gcd(a, d) != 1:
                print(f"sample point on {cv['label']} fails", file=sys.stderr); return 1
        # slow recount at H = 300 for every curve (cheap)
        n = 1
        for d in range(1, math.isqrt(300) + 1):
            for a in range(-300, 301):
                if math.gcd(a, d) != 1:
                    continue
                g = Cm.g_exact(a, d, b2, b4, b6)
                if g >= 0 and math.isqrt(g) ** 2 == g:
                    n += 1 if g == 0 else 2
        if cv["counts"].get("300") != n:
            print(f"height-300 recount differs on {cv['label']}", file=sys.stderr); return 1
    fresh = Cm.summarize(curves)
    for k, v in fresh.items():
        if raw["metrics"].get(k) != v:
            print(f"summary {k} does not re-derive", file=sys.stderr); return 1
    print("check ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
