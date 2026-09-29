#!/usr/bin/env python3
"""V3 supplement: recompute, with my own arithmetic, the number of digit-space
solutions (x1, x2) in {0..7}^2 of S_3(x1, x2, x_R) = 0 mod p for each declared
instance, and compare with the N_sol_values recorded in the m2-s3 manifest."""
import yaml, sys
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5")
from v3_instance_certificates import INSTANCES

def S3(x1, x2, x3, a, b, p):
    return ((x1 - x2) ** 2 * x3 ** 2 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p

mine = []
for (p, cs, a, b, ts, xR) in INSTANCES:
    sols = [(x1, x2) for x1 in range(8) for x2 in range(8) if S3(x1, x2, xR, a, b, p) == 0]
    in_window = [s for s in sols if s[0] < 4 and s[1] < 4]
    mine.append((p, cs, ts, len(sols), sorted(sols), len(in_window)))
m = yaml.safe_load(open("experiments/EXP-PFDR-5726af/runs/RUN-PFDR-5726af-m2-s3/manifest.yaml"))["run"]
rec = m["result"]["metrics"]["N_sol_values"]
res = m["result"]["metrics"]["residuals"]
print(f"{'p':>6} {'cseed':>5} {'t':>2}  my_N_sol  manifest_N_sol  agree  solutions(x1,x2) in {{0..7}}^2")
ok = True
for (row, n_rec, r) in zip(mine, rec, res):
    p, cs, ts, n, sols, nw = row
    assert (r["p"], r["curve_seed"], r["target_seed"]) == (p, cs, ts), "ordering mismatch"
    agree = (n == n_rec)
    ok &= agree
    print(f"{p:6d} {cs:5d} {ts:2d}  {n:8d}  {n_rec:14d}  {str(agree):5s}  {sols}")
print()
print("my N_sol agrees with every manifest N_sol_values entry:", bool(ok))
print("every recorded solution lies inside the planting window [0,4)^2:",
      all(row[3] == row[5] for row in mine))
