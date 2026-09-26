"""VC-2 (system binding and rebuild) and VC-3 (satisfiability) over every kept
system of instances.jsonl.gz. Writes work/rebuild.jsonl.gz and
work/rebuild-context.json. Usage: run_rebuild.py <instances.jsonl.gz> <workdir> [nproc]"""
import gzip
import hashlib
import json
import sys
import time
from multiprocessing import Pool

import numpy as np

import descent
import gf19
import layout as LY

B_LIT = 306147
CURVE_ARMS = ("S3-U400", "S3-SAT100", "F-RANDX19")

CTX = {}


def build_context():
    E0 = descent.route_A(0, B_LIT)
    Ej = [descent.route_A(1 << j, B_LIT) ^ E0 for j in range(19)]
    U = E0.astype(bool).copy()
    for e in Ej:
        U |= e.astype(bool)
    tau = [gf19.trace(1 << j) for j in range(19)]
    ell_lin = np.zeros(211, dtype=np.uint8)
    for j in range(10):
        if tau[j]:
            ell_lin[1 + j] ^= 1
            ell_lin[11 + j] ^= 1
    return {"E0": E0, "Ej": Ej, "U": U, "S_L": U[:, :21], "tau": tau, "ell_lin": ell_lin}


def affine(xR):
    E = CTX["E0"].copy()
    for j in range(19):
        if (xR >> j) & 1:
            E ^= CTX["Ej"][j]
    return E


def first_diff(A, B):
    d = np.argwhere(A != B)
    return [int(d[0][0]), int(d[0][1])] if d.size else None


def sha_hex(hexlist):
    return hashlib.sha256(json.dumps(hexlist, separators=(",", ":")).encode()).hexdigest()


def init(ctx, s3x):
    CTX.update(ctx)
    CTX["s3x"] = s3x


def work(r):
    out = {"key": r["key"], "arm": r["arm"], "role": r["role"], "index": r["index"]}
    E = LY.decode_E(r["E_hex"])
    canon = LY.encode_E(E)
    out["codec_round_trip"] = [int(h, 16) for h in canon] == [int(h, 16) for h in r["E_hex"]]
    out["E_hex_canonical_form"] = canon == list(r["E_hex"])
    out["E_sha256_match"] = sha_hex(r["E_hex"]) == r["E_sha256"]
    out["E_sha256_of_canonical_reencoding_match"] = sha_hex(canon) == r["E_sha256"]
    # VC-3 satisfiability by exhaustive 2^20 evaluation of the archived system
    s, sol = descent.s_from_E(E)
    out["s_mine"] = s
    out["s_archived"] = r.get("s")
    out["s_match"] = s == r.get("s")
    out["role_consistent"] = (s == 0) == (r["role"] == "unsat")
    if r.get("solutions") is not None or r["role"] == "sat":
        listed = r.get("solutions") or []
        sat_each = [not any(descent.eval_system_at(E, int(u))) for u in listed]
        out["listed_solutions"] = len(listed)
        out["listed_solutions_all_satisfy"] = all(sat_each)
        out["listed_equals_full_solution_set"] = sorted(int(u) for u in listed) == sol.tolist()
    # VC-2 rebuild / structure
    arm = r["arm"]
    U = CTX["U"]
    if arm in CURVE_ARMS:
        xR = int(r["x_R"])
        EA = descent.route_A(xR, B_LIT)
        EB, s_direct = descent.route_B(xR, B_LIT)
        out["x_R"] = xR
        out["route_A_eq_route_B"] = bool(np.array_equal(EA, EB))
        out["rebuild_eq_archived"] = bool(np.array_equal(EA, E))
        out["first_diff_row_col"] = first_diff(EA, E)
        out["s_direct_S3_zero_count"] = s_direct
        out["s_direct_match"] = s_direct == r.get("s")
        out["affine_decomposition_ok"] = bool(np.array_equal(affine(xR), EA))
        out["rebuild_sha256_match"] = sha_hex(LY.encode_E(EA)) == r["E_sha256"]
    elif arm == "N-CONV19":
        slot = int(r["slot"])
        xs = CTX["s3x"].get(slot)
        out["slot"] = slot
        out["s3_key_consistent"] = r.get("s3_key") == "S3-U400:%d" % slot and r.get("x_R") == xs
        ES = descent.route_A(xs, B_LIT)
        out["quadratic_part_eq_E_S3"] = bool(np.array_equal(ES[:, 21:], E[:, 21:]))
        out["first_diff_quadratic"] = first_diff(ES[:, 21:], E[:, 21:])
        out["lower_part_inside_S_L"] = bool(not (E[:, :21].astype(bool) & ~CTX["S_L"]).any())
        out["not_identity_draw"] = bool(not np.array_equal(ES, E))
    elif arm == "N-ELL19":
        out["rows_0_17_inside_U"] = bool(not (E[:18].astype(bool) & ~U[:18]).any())
        row18 = E[18].copy()
        c = int(row18[0])
        row18[0] = 0
        out["row18_eq_ell_lin_plus_c"] = bool(np.array_equal(row18, CTX["ell_lin"]))
        out["row18_c"] = c
    elif arm == "N-F219":
        out["inside_U"] = bool(not (E.astype(bool) & ~U).any())
    elif arm == "N-AFF19":
        out["inside_U"] = bool(not (E.astype(bool) & ~U).any())
        xR = int(r["x_R"])
        supp = CTX["E0"].astype(bool).copy()
        for j in range(19):
            if (xR >> j) & 1:
                supp |= CTX["Ej"][j].astype(bool)
        out["inside_affine_support_at_x_R"] = bool(not (E.astype(bool) & ~supp).any())
        out["family"] = r.get("family")
    return out


def main():
    inst, workdir = sys.argv[1], sys.argv[2]
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    t0 = time.time()
    recs = [json.loads(l) for l in gzip.open(inst, "rt")]
    ctx = build_context()
    s3x = {int(r["index"]): int(r["x_R"]) for r in recs if r["arm"] == "S3-U400"}
    with Pool(nproc, initializer=init, initargs=(ctx, s3x)) as pool:
        res = pool.map(work, recs, chunksize=8)
    with gzip.open(workdir + "/rebuild.jsonl.gz", "wt") as f:
        for o in res:
            f.write(json.dumps(o, sort_keys=True) + "\n")
    U = ctx["U"]
    json.dump({
        "tau": ctx["tau"],
        "ell_lin_columns": [int(j) for j in np.flatnonzero(ctx["ell_lin"])],
        "U_row_sizes": [int(x) for x in U.sum(axis=1)],
        "U_size": int(U.sum()),
        "S_L_size": int(ctx["S_L"].sum()),
        "S_L_row_sizes": [int(x) for x in ctx["S_L"].sum(axis=1)],
        "E0_sha256_canonical": sha_hex(LY.encode_E(ctx["E0"])),
        "seconds": round(time.time() - t0, 1),
        "n_records": len(res),
    }, open(workdir + "/rebuild-context.json", "w"), indent=1)
    print("done", len(res), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
