"""EXP-SEMBIN-79a02d Stage 1 -- builder equality at n=12, m=t=3, k=4.

The DREG builder (src/semaev_tree.py via src/h012_peel_rank.py:build_system)
needs Sage, which is excluded and not installed. Its exact output for the
anchor instance (t=3, ti=0, seed 2026) is pinned in EXP-DREG-001 by
system_hash = sha256 over the ordered generator monomial lists
(src/h012c_block_m4ri.py:45-55). This script rebuilds the descent of eq. (5)
INDEPENDENTLY (implementation/semaev_core.py) for every z in F_{2^n}^* under
candidate field moduli and searches for a byte-identical hash. A match is a
coefficient-wise equality of every generator (sha256 collision resistance);
it is confirmed through a second channel by the D=5 Macaulay nrows / ncols
recorded by EXP-DREG-001, recomputed here by both arms.
usage: stage1_builder_equality.py <run_dir>
"""
import json, os, sys, time, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from semaev_core import *
from harness import write_gens, run_tool

EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = {
    12: {"k": 4, "hash": "c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818",
         "nrows_D5": 31512, "ncols_D5": 46717,
         "source": "experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N12-A/raw-result.json"},
    15: {"k": 5, "hash": "23c234edb06c27dff137ac0c2f950706257fa8de87435953bdeeb0d140788403",
         "nrows_D5": 74880, "ncols_D5": 143421,
         "source": "experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N15-A/raw-result.json"},
}


def hash_prefix(polys_first, N):
    h = hashlib.sha256()
    for f in polys_first:
        encoded = sorted(tuple(i for i in range(N) if (m >> i) & 1) for m in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h


def search(n, k, target, time_cap):
    L = Layout(n, k)
    cands = [("conway_candidate", CONWAY[n])]
    others = sorted((p for p in range((1 << n) + 1, 1 << (n + 1), 2) if p != CONWAY[n] and is_irreducible(p, n)),
                    key=lambda p: (bin(p).count("1"), p))
    cands += [("irreducible_weight_order", p) for p in others]
    t0 = time.time(); tried = 0
    for label, mod in cands:
        if time.time() - t0 > time_cap:
            break
        F = GF2n(n, mod)
        if not is_irreducible(mod, n):
            continue
        B = 2  # alpha
        first = [p for p in coordinates(descend_S3_vars(F, L, B), n)]
        assert all(first)
        h0 = hash_prefix(first, L.N)
        tried += 1
        for z in range(1, 1 << n):
            second = [p for p in coordinates(descend_S3_const(F, L, B, z), n) if p]
            h = h0.copy()
            for f in second:
                encoded = sorted(tuple(i for i in range(L.N) if (m >> i) & 1) for m in f)
                h.update(len(encoded).to_bytes(8, "big"))
                for mono in encoded:
                    h.update(len(mono).to_bytes(4, "big"))
                    for v in mono:
                        h.update(v.to_bytes(4, "big"))
            if h.hexdigest() == target:
                return {"matched": True, "modulus_int": mod, "modulus_label": label,
                        "modulus_poly": " + ".join(f"X^{i}" for i in range(n, -1, -1) if (mod >> i) & 1),
                        "z_int": z, "moduli_tried": tried, "seconds": round(time.time() - t0, 1)}
    return {"matched": False, "moduli_tried": tried, "seconds": round(time.time() - t0, 1)}


def main():
    rd = sys.argv[1]
    scratch = os.environ.get("SCRATCH", "/tmp")
    out = {"schema": "EXP-SEMBIN-79a02d.stage1.builder-equality.v1", "cells": {}}
    for n in (12, 15):
        T = TARGETS[n]; k = T["k"]
        res = search(n, k, T["hash"], time_cap=900 if n == 12 else 600)
        cell = {"n": n, "m": 3, "t": 3, "k": k, "dreg_target": T, "search": res}
        if res["matched"]:
            F = GF2n(n, res["modulus_int"]); L = Layout(n, k); B = 2
            polys = build_system(F, L, B, res["z_int"])
            cell["rebuilt_hash"] = monosets_hash(polys, L.N)
            cell["hash_equal"] = cell["rebuilt_hash"] == T["hash"]
            cell["n_generators"] = len(polys)
            cell["generator_degrees"] = [poly_deg(f) for f in polys]
            cell["generator_term_counts"] = [len(f) for f in polys]
            sols = enumerate_field(F, L, B, res["z_int"])
            cell["E1_solution_count"] = len(sols)
            cell["z_is_decomposable_R_x"] = len(sols) > 0
            E = Curve(F, 1, B)
            cell["z_on_curve_x"] = len(E.lift_x(res["z_int"])) > 0
            g = os.path.join(scratch, f"stage1_n{n}.gens"); write_gens(g, polys, L.N)
            json.dump({"n": n, "k": k, "modulus_int": res["modulus_int"], "z_int": res["z_int"], "B": B},
                      open(os.path.join(rd, f"anchor_n{n}.json"), "w"))
            if n == 12:
                a = run_tool(["gf2_armA", "mac", g, 5], 3000); b = run_tool(["gf2_armB", "mac", g, 5], 3000)
                cell["D5_armA"] = a; cell["D5_armB"] = b
                cell["D5_nrows_equal_dreg"] = a["nrows"] == b["nrows"] == T["nrows_D5"]
                cell["D5_ncols_occurring_equal_dreg"] = a["ncols_occurring"] == b["ncols_occurring"] == T["ncols_D5"]
                cell["D5_matrix_fingerprint_equal_AB"] = a["fingerprint"] == b["fingerprint"]
        out["cells"][str(n)] = cell
    c12 = out["cells"]["12"]
    passed = bool(c12.get("hash_equal")) and bool(c12.get("D5_nrows_equal_dreg")) and bool(c12.get("D5_ncols_occurring_equal_dreg"))
    out["builder_equality_pass"] = passed
    out["gate"] = "PASS" if passed else "O-BUILDER-MISMATCH"
    out["manifest_summary"] = {"status": "completed_valid",
                               "validity_reason": "Stage-1 gate evaluated: " + out["gate"],
                               "builder_equality_pass": passed}
    json.dump(out, open(os.path.join(rd, "raw-result.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "cells"}))


if __name__ == "__main__":
    main()
