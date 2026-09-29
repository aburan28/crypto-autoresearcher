import json, struct

path = "/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/results_hkz_indep.json"
d = json.load(open(path))

cells = d["R_V_OUT_2_per_cell"]

def bits(x):
    return struct.unpack('<Q', struct.pack('<d', x))[0]

for cell, v in cells.items():
    p = v["route_p_values"]
    ii = v["route_ii_values"]
    print("=== %s (d=%d beta=%d) ===" % (cell, v["d"], v["beta"]))
    diffs = []
    for idx,(a,b) in enumerate(zip(p, ii)):
        diff = a - b
        ulp_a = bits(a)
        ulp_b = bits(b)
        ulp_diff = ulp_a - ulp_b
        diffs.append(abs(diff))
        if diff != 0:
            print("  idx=%d  a=%.20g  b=%.20g  diff=%.6e  bits_a=%d bits_b=%d bits_diff=%d" % (idx, a, b, diff, ulp_a, ulp_b, ulp_diff))
        else:
            print("  idx=%d  IDENTICAL bit pattern (bits=%d)" % (idx, ulp_a))
    print("  max abs diff = %.17e   (reported D_route_pp = %.17e)" % (max(diffs), v["D_route_pp"]))
    print()
