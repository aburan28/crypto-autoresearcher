#!/usr/bin/env python3
"""SEPARATE CROSS-CHECK (phase B, NOT the blind re-derivation).

Feeds the generator S~ built by MY OWN phase-A code into the shared meter
harness/macaulay_fp and compares the meter's per-layer (full_rank, top_rank,
fall_dim) with my independently computed values.  Reported as its own line in
the validation report; it is not part of joint V1's re-derivation, which was
completed and written before this file existed.
"""
import sys
sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5")
from v1_blind_rederive import ell, S3_in_B, profile, INSTANCES, NMASK, POP
from harness.macaulay_fp import Ring, analyze_layer

print(f"{'p':>6} {'cs':>5} {'t':>2}  D   mine(full,top,fall)   meter(full,top,fall)  agree")
agree_all = True
for (p, cs, a, b, ts, xR) in INSTANCES:
    St = S3_in_B(ell(0, p), ell(1, p), xR, a, b, p)
    prof, d_ff = profile(St, p)
    ring = Ring(p=p, n_sq=6, n_free=0)
    gen = {(m, ()): c for m, c in enumerate(St) if c}      # my S~, meter representation
    meter_dff = None
    for D in (4, 5, 6, 7):
        lr = analyze_layer(ring, [gen], D, convention="per_layer")
        mine = (prof[D]["full_rank"], prof[D]["top_rank"], prof[D]["fall_dim"])
        theirs = (lr.full_rank, lr.top_rank, lr.fall_dim)
        ok = mine == theirs
        agree_all &= ok
        if meter_dff is None and lr.fall_dim > 0:
            meter_dff = D
        print(f"{p:6d} {cs:5d} {ts:2d}  {D}   {str(mine):20s}  {str(theirs):20s}  {ok}")
    print(f"{'':6s} {'':5s} {'':2s}  ->  my d_ff={d_ff} fall={prof[d_ff]['fall_dim']}   "
          f"meter d_ff={meter_dff}   agree={d_ff == meter_dff}")
    agree_all &= (d_ff == meter_dff)
print()
print("meter agrees with my independent per-layer ranks on every instance and degree:", bool(agree_all))
