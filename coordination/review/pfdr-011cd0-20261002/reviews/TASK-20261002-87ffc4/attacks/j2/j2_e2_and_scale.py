"""Re-run (second attempt; the first was stopped by the runtime background time limit before writing anything) of the parts of j2_toy_enum2.py that the reviewer stopped (s = 30 scale points took
~20 min each in pure Python): E2 (PTM-L early-return selection, N 1009, s 8, h 2, 20000 draws,
seed SeedSequence([0x87ffc4, 4])) and ONE reduced scale point (s 30, N 100003, h 2, 3000 draws,
seed SeedSequence([0x87ffc4, 3, 30, 100003])). The stop was the reviewer's (time), not a failure.
Command: nice -n 19 $PY attacks/j2/j2_e2_and_scale.py --out attacks/j2/out/toy_enum2_rest.json"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from j2_toy_enum2 import part_E2, part_C3_G
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
ap2 = a
res = {"E2_early_return_mc": part_E2(),
       "G_h2_admissible_scale_s30": "NOT COMPUTED: the first attempt of this script was stopped by the runtime's background time limit (infrastructure, not a finding); the reviewer dropped the s = 30 point on the re-run because the s = 10 and s = 20 points already show the trend"}
json.dump(res, open(a.out, "w"), indent=1)
print(json.dumps(res["E2_early_return_mc"]))
