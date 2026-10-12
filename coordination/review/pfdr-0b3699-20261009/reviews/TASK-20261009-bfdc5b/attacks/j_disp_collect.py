"""Assemble out/j_disp.json from j_disp.py's run log (part 1, the fits and the six departure
laws, all of which completed before the per-rung variant stopped) and j_disp_part3.py's output.
No computation. TASK-20261009-bfdc5b.
"""
import json
import sys
LOG, P3, CAL, OUT = sys.argv[1:5]
cal = json.load(open(CAL))
res = {"task": "TASK-20261009-bfdc5b", "joint": "J-DISP", "t_dec": cal["t_dec"], "t_perm": cal["t_perm"]["mean"],
       "laws": {}, "source": {"part1_fits_laws": LOG + " (j_disp.py run 1; stopped in part 3 after the laws)",
                              "subset_variants": P3 + " (j_disp_part3.py)"}}
for line in open(LOG):
    name, _, rest = line.partition(" ")
    if name == "part1":
        res["part1"] = json.loads(rest)
    elif name == "fits":
        res["fits_to_null_arms"] = json.loads(rest)
    elif rest.startswith("{") and ("t_A_alt" in rest):
        res["laws"][name] = json.loads(rest)
res["subset_variants"] = json.load(open(P3))
json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
print(len(res["laws"]), "laws;", list(res["subset_variants"]))
