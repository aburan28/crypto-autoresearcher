"""Checker for EXP-CZLIFT-f5e06c: reproduces the first curve of each arm and re-derives both summaries."""
from __future__ import annotations
import json, os, sys, yaml
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
    seed, P = man["inputs"]["seed"], man["inputs"]["parameters"]
    A = driver.load(driver.SRC_A, "chk_a"); B = driver.load(driver.SRC_B, "chk_b")
    ca, cb = raw["raw"]["curves_anomalous"], raw["raw"]["curves_torsion"]
    if not ca or not cb:
        print("empty arm", file=sys.stderr); return 1
    c = ca[0]
    if A.measure_curve(c["D"], c["p"], c["A"], c["B"], c["j_cm"], seed=seed, samples=P["samples_a"], per_class=1)["rows"] != c["rows"]:
        print("anomalous curve does not reproduce", file=sys.stderr); return 1
    for arm in ("cm_canonical", "random_naive"):
        c = next((x for x in cb if x["arm"] == arm), None)
        if c is None:
            print(f"arm {arm} missing", file=sys.stderr); return 1
        if B.measure_curve(arm, c["p"], c["A"], c["B"], c["N"], c["n"], seed=seed, samples=P["samples_b"], label=c["label"])["rows"] != c["rows"]:
            print(f"{arm} curve does not reproduce", file=sys.stderr); return 1
    ma, mb = A.summarize(ca), B.summarize(cb)
    for k, v in ma.items():
        key = {"by_class": "anomalous_by_class", "degenerate_by_section": "anomalous_degenerate_by_section"}.get(k)
        if (raw["metrics"][key] if key else raw["metrics"]["anomalous"].get(k)) != v:
            print(f"anomalous summary {k} does not re-derive", file=sys.stderr); return 1
    for k, v in mb.items():
        if (raw["metrics"]["torsion_sections"] if k == "sections" else raw["metrics"]["torsion"].get(k)) != v:
            print(f"torsion summary {k} does not re-derive", file=sys.stderr); return 1
    print("check ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
