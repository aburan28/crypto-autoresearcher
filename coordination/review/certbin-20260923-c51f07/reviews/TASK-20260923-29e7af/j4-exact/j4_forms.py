#!/usr/bin/env python3
"""J4 step 1 (TASK-20260923-29e7af, red team). Exact affine pivot forms
e_k(r) = a_{k,0} + <a_k, r> for every F-S3 reference at D = 4 (and D = 3),
computed from the ARCHIVED op logs by an INDEPENDENT replay written here.

What is imported from the archived impl/ (read-only, unmodified):
  - macaulay.MacaulayShape (the fixed-shape matrix constructor; J1 owns it)
  - macaulay.affine_basis / descended_E (E^0, E^j; J1 owns them)
  - gf2n.TableField (field arithmetic used by the constructor)
What is NOT imported: elim.replay_planes, elim.affine_forms, elim.eval_forms,
engine.* . The replay below is my own: full-row XOR, no word-offset shortcut.

This script reads NO hazard value: it does not open pivot-hazards.json,
cell-summary.json, decision-rules.json, raw-result.json or any checkpoint, and
it reads no 'replay_first_zero' field. From references.json it reads only
x_R, rank, len_strict, T_strict, K_exact and K_rank (no hazard is stored there).

Output: forms-D{3,4}.json (per reference: x_R, rank, a0 list, a list as ints,
self-replay check, direct-replay spot checks, agreement with references.json).
The modal reference's op log is included in the archived op-log file.
"""
import gzip
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np

REPO = "/home/user/crypto-autoresearcher"
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/impl")
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IMPL)

from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape, affine_basis, descended_E  # noqa: E402

ONE = np.uint64(1)


def load_oplogs(D):
    logs = defaultdict(list)
    xr = {}
    with gzip.open(os.path.join(RUN, f"F-S3-reference-oplogs-D{D}.jsonl.gz"), "rt") as f:
        for line in f:
            d = json.loads(line)
            logs[d["ref"]].append((d["k"], d["p"], d["c"], d["X"]))
            xr[d["ref"]] = d["x_R"]
    out = {}
    for lab, ops in logs.items():
        ops.sort()
        assert [o[0] for o in ops] == list(range(len(ops))), lab
        out[lab] = [(p, c, np.array(X, dtype=np.int64)) for _, p, c, X in ops]
    return out, xr


def my_replay(planes, ops):
    """planes (P, R, W) uint64, modified in place. Returns e (P, K):
    entry (p_k, c_k) of each plane immediately BEFORE step k's XORs.
    Full-row XOR of row p_k into every row of X_k (no column offset)."""
    P = planes.shape[0]
    K = len(ops)
    e = np.zeros((P, K), dtype=np.uint8)
    for k, (p, c, X) in enumerate(ops):
        e[:, k] = ((planes[:, p, c >> 6] >> np.uint64(c & 63)) & ONE).astype(np.uint8)
        if X.size:
            planes[:, X, :] ^= planes[:, p, :][:, None, :]
    return e


def main():
    t0 = time.time()
    F = TableField()
    curve = json.load(open(os.path.join(RUN, "curve.json")))
    B = curve["B"]
    E0, Ej = affine_basis(F, B)
    refs_json = json.load(open(os.path.join(RUN, "references.json")))
    summary = {}
    for D in (4, 3):
        S = MacaulayShape(D)
        ops_by_ref, xr = load_oplogs(D)
        base = np.stack([S.build(E0)] + [S.build(x) for x in Ej])  # (18, R, W)
        res = {}
        for lab in sorted(ops_by_ref):
            ops = ops_by_ref[lab]
            e = my_replay(base.copy(), ops)
            a0 = e[0].astype(int)
            a = np.zeros(e.shape[1], dtype=np.int64)
            for j in range(17):
                a |= e[1 + j].astype(np.int64) << j
            # self-replay: e_k(r_ref) must be 1 for all k
            r = xr[lab]
            par = (np.bitwise_count(a & np.int64(r)) & 1).astype(int)
            self_e = a0 ^ par
            # direct replay on the reference's own matrix (my replay code)
            Mref = S.build(descended_E(F, B, r))[None]
            e_dir = my_replay(Mref.copy(), ops)[0]
            # direct replay on 3 other r values (spot check of affinity)
            spot = []
            for rr in (0x1abcd, 0x0f0f1, 0x13579):
                Mt = S.build(descended_E(F, B, rr))[None]
                ed = my_replay(Mt, ops)[0]
                ea = a0 ^ (np.bitwise_count(a & np.int64(rr)) & 1).astype(int)
                spot.append({"r": rr, "equal": bool(np.array_equal(ed, ea))})
            res[lab] = {
                "x_R": r, "K_steps": len(ops),
                "a0": a0.tolist(), "a": a.tolist(),
                "self_replay_all_one_affine": bool((self_e == 1).all()),
                "self_replay_all_one_direct": bool((e_dir == 1).all()),
                "direct_vs_affine_spot": spot,
            }
        # compare with references.json (rank, len_strict, K_exact, K_rank, T_strict, x_R);
        # the archived forms themselves sit in the phase-2 checkpoint next to the
        # hazards, so that comparison is deferred to j4_compare.py (after sealing).
        arch = refs_json["F-S3"]["references"]
        cmp_ = {}
        for lab, v in res.items():
            if lab not in arch:
                continue
            ad = arch[lab][f"D{D}"]
            a = v["a"]
            nz = [x for x in a if x]
            basis = {}
            for x in nz:
                while x:
                    h = x.bit_length() - 1
                    if h in basis:
                        x ^= basis[h]
                    else:
                        basis[h] = x
                        break
            ops = ops_by_ref[lab]
            cmp_[lab] = {"x_R_equal": arch[lab].get("x_R", "modal: no x_R key") == v["x_R"] if "x_R" in arch[lab] else "modal (x_R via instance_idx_per_D)",
                         "rank_equal": ad["rank"] == v["K_steps"],
                         "len_strict_equal": ad["len_strict"] == v["K_steps"],
                         "T_strict_equal": ad["T_strict"] == [[p, c] for p, c, _ in ops],
                         "K_exact_mine": len(nz), "K_exact_archived": ad["K_exact"],
                         "K_rank_mine": len(basis), "K_rank_archived": ad["K_rank"]}
        with open(os.path.join(OUT, f"forms-D{D}.json"), "w") as f:
            json.dump({"D": D, "refs": res, "compare_with_references_json": cmp_}, f,
                      separators=(",", ":"))
        summary[f"D{D}"] = {lab: {"K_steps": v["K_steps"], "self_affine": v["self_replay_all_one_affine"],
                                  "self_direct": v["self_replay_all_one_direct"],
                                  "spot_all_equal": all(s["equal"] for s in v["direct_vs_affine_spot"]),
                                  "archived_match": cmp_.get(lab)} for lab, v in res.items()}
    summary["wall_seconds"] = round(time.time() - t0, 1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
