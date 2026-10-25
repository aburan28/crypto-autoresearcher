#!/usr/bin/env python3
"""Write the descended system of a named instance of results/instances.json to a .sys file
(the format read by lfdclose2), without searching for a new instance.
usage: mksys.py instances.json NAME out.sys"""
import json, sys
from gf2n import Field
from s3sys import Subspace, s3_descent, write_system
recs = {r["name"]: r for r in json.load(open(sys.argv[1]))}
r = recs[sys.argv[2]]
F = Field(r["n"], int(r["modulus_hex"], 16))
V = Subspace(F, [int(x, 16) for x in r["V_basis_hex"]])
polys = s3_descent(F, V, int(r["z_hex"], 16), int(r["a6_hex"], 16))
with open(sys.argv[3], "w") as fh:
    write_system(polys, 2 * len(V.basis), fh)
print("wrote", sys.argv[3], "N =", 2 * len(V.basis), "equations", len(polys))
