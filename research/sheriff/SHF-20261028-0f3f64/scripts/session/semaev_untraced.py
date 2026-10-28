"""Trace the six paper.untraced_number leads of the sweep in
papers/semaev-conservation-specialization/paper.tex against the run's raw result."""
import json
R = "experiments/EXP-SMON-e5cbe6/runs/RUN-SMON-e5cbe6-001/raw-result.json"
d = json.load(open(R))
c = d["C2_C4_generic_fibre"]
e = d["C6_exhaustive"]
n = d["C7_null_controls"]
out = {
    "18000 (line 885) = sum C2 samples": sum(v["samples"] for v in c.values()),
    "16737 (885, 952) = sum C2 good": sum(v["good"] for v in c.values()),
    "224906 (952) = sum C6 good": sum(r["good"] for v in e.values() for r in v),
    "241643 (952) = 16737 + 224906": sum(v["good"] for v in c.values()) + sum(r["good"] for v in e.values() for r in v),
    "13.7% (896) = NULL-A fraction": n["NULL-A"]["fraction_obeying_the_C4_dichotomy"],
    "48.9% (896) = NULL-B fraction": n["NULL-B"]["fraction_obeying_the_C4_dichotomy"],
    "256 (869)": "SHA-256 in prose, not a measurement",
    "53101211 (928)": "tokeniser joined the set {53,101,211}; each prime is a C6 p",
}
print(json.dumps(out, indent=1))
