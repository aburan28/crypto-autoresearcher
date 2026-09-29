#!/usr/bin/env python3
"""R1c: extended exhaustive sweep (frequency of the fall_dim exception)."""
import json, sys
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f")
from r1b_rowdep_sweep import sweep
out=[]
for p in (29,31,37,41):
    out.append(sweep(p,2))
for p in (19,23):
    out.append(sweep(p,3))
json.dump(out, sys.stdout, indent=1)
