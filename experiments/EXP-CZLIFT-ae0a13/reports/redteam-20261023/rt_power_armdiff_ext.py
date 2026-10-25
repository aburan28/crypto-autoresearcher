"""Extension of rt_power.py: arm-difference power for larger effects and both directions."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_power import rows_by_arm, armdiff_power, RUN_IDS
data = {r: rows_by_arm(r) for r in RUN_IDS}
out = {}
for direction in ("cm_leaks", "random_leaks"):
    for c in (12, 16, 20, 25, 30, 40):
        rec = {}
        for r in RUN_IDS:
            psa, psb = data[r]["cm_canonical"], data[r]["random_naive"]
            ra = [min(1, (c if direction == "cm_leaks" else 1) / p) for p in psa]
            rb = [min(1, (c if direction == "random_leaks" else 1) / p) for p in psb]
            rec[r] = armdiff_power(psa, ra, psb, rb)
        rec["both_seeds"] = rec[RUN_IDS[0]] * rec[RUN_IDS[1]]
        out[f"{direction} c={c}"] = rec
        print(f"{direction} leak rate {c}/p, other arm 1/p: P(|z|>3) " + ", ".join(f"{k}:{v:.3f}" for k, v in rec.items()))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rt_power_armdiff_ext_output.json"), "w"), indent=1)
