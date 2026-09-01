#!/usr/bin/env python3
# census.py -- TASK-20260901-3dffdc (BATCH-803af6, GOAL-AES-003).
#
# FRESH implementation of the IDEA-20260901-ec54fe Stage-0 census:
#   T_{r,S} = M_r^{-1} . Z_{CW[S]} . M_r   over GF(2),
#   M_r = SR . (MC . SR)^{r-1}  (SBOX = id; AddRoundKey drops out on differences),
# frozen cell set C at r = 1..10. ZERO cipher evaluations: everything here is
# exact GF(2) linear algebra on 128-bit integers.
#
# CONVENTION (pinned, BATCH-002 / FIPS-197-shaped toy SPN):
#   E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
#   state column-major: byte index = 4*col + row
#   PW[j][row] = 4*((j+row)%4) + row   (forward diagonals, plaintext words)
#   CW[j][row] = 4*((j-row)%4) + row   (inverse-ShiftRows diagonals, ciphertext words)
#   bit convention: bit b of byte i is bit (8*i + b) of the 128-bit vector
#
# NO AES ROUND CONTENT in this file: no S-box table, no key schedule, no KAT.
# The only AES-lineage constants are the probe-geometry ones the census is
# ABOUT (ShiftRows geometry via the pinned PW/CW tables, and the MixColumns
# GF(2^8) column map {2,3,1,1}), both cross-checked below against the
# harness's byte-level formulas. Disclosed in INDEPENDENCE_AUDIT.md with
# source citations.
import json, sys, hashlib, datetime

N = 128

# ---------------- GF(2) matrix machinery (rows = list of 128 ints) ----------------
def eye(n=N): return [1 << i for i in range(n)]

def mat_mul(A, B):
    out = []
    for a in A:
        r = 0
        x = a
        while x:
            lsb = x & -x
            r ^= B[lsb.bit_length() - 1]
            x ^= lsb
        out.append(r)
    return out

def mat_inv(A):
    n = len(A)
    aug = [A[i] | (1 << (n + i)) for i in range(n)]
    for c in range(n):
        piv = None
        for i in range(c, n):
            if (aug[i] >> c) & 1:
                piv = i
                break
        if piv is None:
            return None
        aug[c], aug[piv] = aug[piv], aug[c]
        for i in range(n):
            if i != c and ((aug[i] >> c) & 1):
                aug[i] ^= aug[c]
    for i in range(n):
        if aug[i] & ((1 << n) - 1) != 1 << i:
            return None
    return [aug[i] >> n for i in range(n)]

def mat_apply(A, v):
    r = 0
    for i, row in enumerate(A):
        if bin(row & v).count("1") & 1:
            r |= 1 << i
    return r

def col_of(A, p):
    r = 0
    for i, row in enumerate(A):
        if (row >> p) & 1:
            r |= 1 << i
    return r

def rank_of_cols(cols):
    basis = {}
    for v in cols:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return len(basis)

# ---------------- probe geometry (pinned; citations in INDEPENDENCE_AUDIT.md) ----
PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

def perm_matrix(perm):
    return [1 << (8 * perm[b] + bit) for b in range(16) for bit in range(8)]

# ShiftRows: out byte (col,row) <- in byte (col+row mod 4, row)
SR = perm_matrix([4 * (((b // 4) + (b % 4)) % 4) + (b % 4) for b in range(16)])
# inverse ShiftRows: out byte (col,row) <- in byte (col-row mod 4, row)
ISR = perm_matrix([4 * (((b // 4) - (b % 4)) % 4) + (b % 4) for b in range(16)])

def xt(a): return ((a << 1) ^ ((a >> 7) * 0x1b)) & 0xFF

def mixcol(a0, a1, a2, a3):
    # FIPS-197 MixColumns column map: b_i = 2 a_i + 3 a_{i+1} + a_{i+2} + a_{i+3}
    a = [a0, a1, a2, a3]
    return [xt(a[i]) ^ xt(a[(i + 1) % 4]) ^ a[(i + 1) % 4] ^ a[(i + 2) % 4] ^ a[(i + 3) % 4]
            for i in range(4)]

def invmixcol(a0, a1, a2, a3):
    # inverse MixColumns column map {14,11,13,9}
    def gmul8(c, a):
        r, x, k = 0, a, c
        while k:
            if k & 1: r ^= x
            x = xt(x); k >>= 1
        return r
    a = [a0, a1, a2, a3]
    cs = [0x0e, 0x0b, 0x0d, 0x09]
    return [sum(gmul8(cs[j], a[(i + j) % 4]) for j in range(4)) & 0xFF for i in range(4)]

def block_matrix(bytefun):
    # 128x128 GF(2) rows of a column-wise byte map, built on bit basis vectors
    rows = [0] * N
    for c in range(4):
        for k in range(4):
            for bit in range(8):
                ins = [0, 0, 0, 0]
                ins[k] = 1 << bit
                outs = bytefun(*ins)
                srcbit = 8 * (4 * c + k) + bit
                for m in range(4):
                    for obit in range(8):
                        if (outs[m] >> obit) & 1:
                            rows[8 * (4 * c + m) + obit] |= 1 << srcbit
    return rows

MC = block_matrix(mixcol)
IMC = block_matrix(invmixcol)

# ---------------- sanity of the geometry matrices ----------------
def check(name, cond):
    if not cond:
        print(json.dumps({"fatal": name}))
        sys.exit(1)

check("SR_inv_is_ISR", mat_mul(SR, ISR) == eye())
check("MC_inv_is_IMC", mat_mul(MC, IMC) == eye())

# cross-check MC / IMC against the harness's byte-level xt formulas
# (BATCH-b41ba9 probe_sbox.c mix_columns / inv_mix_columns) on exhaustive samples
def harness_mix(a0, a1, a2, a3):
    t = a0 ^ a1 ^ a2 ^ a3
    return [a0 ^ t ^ xt(a0 ^ a1), a1 ^ t ^ xt(a1 ^ a2),
            a2 ^ t ^ xt(a2 ^ a3), a3 ^ t ^ xt(a3 ^ a0)]

XT2 = [xt(i) for i in range(256)]
XT4 = [xt(XT2[i]) for i in range(256)]
XT8 = [xt(XT4[i]) for i in range(256)]

def harness_inv_mix(a0, a1, a2, a3):
    w = [XT8[x] for x in (a0, a1, a2, a3)]
    v = [XT4[x] for x in (a0, a1, a2, a3)]
    u = [XT2[x] for x in (a0, a1, a2, a3)]
    return [w[0] ^ v[0] ^ u[0] ^ w[1] ^ u[1] ^ a1 ^ w[2] ^ v[2] ^ a2 ^ w[3] ^ a3,
            w[0] ^ a0 ^ w[1] ^ v[1] ^ u[1] ^ w[2] ^ u[2] ^ a2 ^ w[3] ^ v[3] ^ a3,
            w[0] ^ v[0] ^ a0 ^ w[1] ^ a1 ^ w[2] ^ v[2] ^ u[2] ^ w[3] ^ u[3] ^ a3,
            w[0] ^ u[0] ^ a0 ^ w[1] ^ v[1] ^ a1 ^ w[2] ^ a2 ^ w[3] ^ v[3] ^ u[3]]

sample = [0x00, 0x01, 0x02, 0x57, 0x83, 0x9c, 0xd4, 0xff]
for a0 in sample:
    for a1 in sample:
        for a2 in (0x00, 0x7a, 0xff):
            for a3 in (0x00, 0x11, 0xff):
                check("MC_harness_formula", mixcol(a0, a1, a2, a3) == harness_mix(a0, a1, a2, a3))
                check("IMC_harness_formula", invmixcol(a0, a1, a2, a3) == harness_inv_mix(a0, a1, a2, a3))

# ---------------- frozen cell set (CLOSED -- record P2, verbatim order) ----------------
CELLS = [
    ("C1", [0], [0]),
    ("C2", [0], [1]),
    ("C3", [0], [2]),
    ("C4", [0], [3]),
    ("C5", [1], [1]),
    ("C6", [2], [2]),
    ("C7", [3], [3]),
    ("C8", [0, 1], [0]),
    ("C9", [0], [0, 1]),
    ("C10", [0, 1, 2, 3], [0]),
]

def domain_positions(A):
    pos = []
    for j in sorted(A):
        for row in range(4):
            for bit in range(8):
                pos.append((j, row, bit, 8 * PW[j][row] + bit))
    return pos

def word_positions(j):
    return [8 * PW[j][row] + bit for row in range(4) for bit in range(8)]

def cw_positions(S):
    pos = []
    for j in sorted(S):
        for row in range(4):
            for bit in range(8):
                pos.append(8 * CW[j][row] + bit)
    return pos

def project(x, positions):
    v = 0
    for k, p in enumerate(positions):
        if (x >> p) & 1:
            v |= 1 << k
    return v

def z_matrix(S):
    z = eye()
    for p in cw_positions(S):
        z[p] = 0
    return z

# ---------------- per-r matrices ----------------
def build_round_matrices(rmax=10):
    Ms, Minvs = {}, {}
    acc = eye()                      # acc = (MC.SR)^{r-1}
    for r in range(1, rmax + 1):
        M = mat_mul(SR, acc)         # M_r = SR . (MC.SR)^{r-1}
        Minv = mat_inv(M)
        check(f"M_{r}_invertible", Minv is not None)
        check(f"Minv_{r}_M_{r}_is_I", mat_mul(Minv, M) == eye())
        # decrypt-path matrix D_r = (ISR.IMC)^{r-1} . ISR (independent cross-check)
        D = ISR
        for _ in range(r - 1):
            D = mat_mul(D, IMC)
            D = mat_mul(D, ISR)
        check(f"D_{r}_M_{r}_is_I", mat_mul(D, M) == eye())
        check(f"Minv_{r}_eq_D_{r}", Minv == D)
        Ms[r] = M
        Minvs[r] = Minv
        acc = mat_mul(MC, acc)
    return Ms, Minvs

def mobius_hist(dom_dim, word_maps_cols):
    # word_maps_cols: {j: list of dom_dim column ints (width 32)}.
    # V_J = {d : T_j d = 0 for all j in J}; g[J] = |V_J| = 2^{dom_dim - rank(stack J)}.
    g = {}
    for mask in range(16):
        if mask == 0:
            g[0] = 1 << dom_dim
            continue
        cols = [0] * dom_dim
        width = 0
        for j in range(4):
            if mask & (1 << j):
                for p in range(dom_dim):
                    cols[p] |= word_maps_cols[j][p] << width
                width += 32
        g[mask] = 1 << (dom_dim - rank_of_cols(cols))
    # Mobius: f[S] = #{d with EXACT vanishing set S} = sum_{J >= S} (-1)^{|J|-|S|} g[J]
    f = {}
    for S in range(16):
        acc = 0
        for J in range(16):
            if J & S == S:
                sign = -1 if bin(J ^ S).count("1") & 1 else 1
                acc += sign * g[J]
        f[S] = acc
    check("mobius_nonneg", all(v >= 0 for v in f.values()))
    check("mobius_sum", sum(f.values()) == 1 << dom_dim)
    hist = [0] * 5
    for S, v in f.items():
        hist[bin(S).count("1")] += v
    return hist, f, g

def census_cell(M, Minv, A, S, r):
    T = mat_mul(Minv, mat_mul(z_matrix(S), M))
    dpos = domain_positions(A)
    dom_dim = len(dpos)
    wcols = {j: [] for j in range(4)}
    for (j, row, bit, p) in dpos:
        v = col_of(T, p)
        for jj in range(4):
            wcols[jj].append(project(v, word_positions(jj)))
    ranks = [rank_of_cols(wcols[jj]) for jj in range(4)]
    hist, f, g = mobius_hist(dom_dim, wcols)
    total = 1 << dom_dim
    num_all = total - f[0]
    num_nz = num_all - 1
    den_nz = total - 1
    # trivial-exclusion subspace: d -> (M d)|CW[S]; exact probability over the
    # worker's sampled space D_A = {d : every active word-diff nonzero}
    cwpos = cw_positions(S)
    Fcols = [project(col_of(M, p), cwpos) for (j, row, bit, p) in dpos]
    rankF = rank_of_cols(Fcols)
    def ker_dim_with_zeroed(B):
        stacked = []
        for idx, (j, row, bit, p) in enumerate(dpos):
            c = Fcols[idx]
            if j in B:
                k = sorted(B).index(j)
                c |= 1 << (len(cwpos) + 32 * k + 8 * row + bit)
            stacked.append(c)
        return dom_dim - rank_of_cols(stacked)
    AA = sorted(A)
    kerDA = 0
    for sub in range(1 << len(AA)):
        B = [AA[k] for k in range(len(AA)) if sub & (1 << k)]
        sign = -1 if bin(sub).count("1") & 1 else 1
        kerDA += sign * (1 << ker_dim_with_zeroed(B))
    sizeDA = ((1 << 32) - 1) ** len(A)
    return {
        "r": r,
        "word_map_ranks": ranks,
        "word_map_nullities": [dom_dim - rk for rk in ranks],
        "kernel_intersection_dims": {
            ("".join(str(j) for j in range(4) if mask & (1 << j)) or "empty"):
                (g[mask].bit_length() - 1) for mask in range(16)
        },
        "whist_all_trials": hist,
        "whist_nonzero_d": [hist[0], hist[1], hist[2], hist[3], hist[4] - 1],
        "P_Wge1_all_trials": {"num": num_all, "den": total, "float": num_all / total},
        "P_Wge1_nonzero_d": {"num": num_nz, "den": den_nz,
                             "float": (num_nz / den_nz) if den_nz else 0.0},
        "trivial_exclusion": {
            "map_rank": rankF,
            "ker_dim_on_full_domain": dom_dim - rankF,
            "ker_intersect_sampled_space_size": kerDA,
            "sampled_space_size": sizeDA,
            "prob_exact": f"{kerDA}/{sizeDA}",
            "expected_trivial_at_2^30_trials": kerDA * (1 << 30) / sizeDA,
        },
    }

def label_of(num, den):
    # record PR-2 labels on P_all: ALIVE if P > 2^-30, NULL if P == 2^-30, else intermediate
    cmp = num * (1 << 30) - den  # sign of P - 2^-30
    if cmp > 0:
        return "SKELETON-ALIVE"
    if cmp == 0:
        return "SKELETON-NULL"
    return "intermediate"

def main():
    Ms, Minvs = build_round_matrices(10)
    cells_out = []
    for cid, A, S in CELLS:
        amask = sum(1 << j for j in A)
        smask = sum(1 << j for j in S)
        rounds = []
        for r in range(1, 11):
            c = census_cell(Ms[r], Minvs[r], A, S, r)
            c["label"] = label_of(c["P_Wge1_all_trials"]["num"],
                                  c["P_Wge1_all_trials"]["den"])
            c["label_refined"] = ("SKELETON-DEAD (P=0)"
                                  if c["P_Wge1_all_trials"]["num"] == 0 else c["label"])
            c["identity_law_prediction"] = {
                "W_on_every_nontrivial_trial": 4 - len(A),
                "P_Wge1": 1.0 if len(A) <= 3 else 0.0,
            }
            rounds.append(c)
        cells_out.append({"cell_id": cid, "A": A, "S": S,
                          "amask": amask, "smask": smask, "rounds": rounds})

    c1 = cells_out[0]["rounds"]
    r_star = None
    for c in c1:
        if c["r"] >= 2 and c["P_Wge1_all_trials"]["num"] * (1 << 30) <= c["P_Wge1_all_trials"]["den"]:
            r_star = c["r"]
            break
    c10 = cells_out[9]["rounds"]
    pr5 = []
    for c in c10:
        num, den = c["P_Wge1_all_trials"]["num"], c["P_Wge1_all_trials"]["den"]
        pr5.append({"r": c["r"], "P_float": num / den,
                    "within_factor_3_of_2^-30": num * (1 << 30) <= 3 * den})
    out = {
        "schema": "crypto.autoresearch.census.v1",
        "task_id": "TASK-20260901-3dffdc",
        "idea_record": "IDEA-20260901-ec54fe",
        "object": "T_{r,S} = M_r^{-1} . Z_{CW[S]} . M_r over GF(2), M_r = SR.(MC.SR)^{r-1}, SBOX=id",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "convention": {
            "cipher": "E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0, SB=id, differences",
            "state_layout": "column-major byte index 4*col+row; bit b of byte i = bit 8i+b",
            "PW": PW, "CW": CW,
        },
        "matrix_checks": {
            "SR_ISR_identity": True, "MC_IMC_identity": True,
            "MC_matches_harness_xt_formula_exhaustive_sample": True,
            "IMC_matches_harness_XT248_formula_exhaustive_sample": True,
            "Minv_r_M_r_identity_all_r": True,
            "decrypt_path_D_r_equals_Minv_r_all_r": True,
            "D_r_M_r_identity_all_r": True,
        },
        "frozen_cell_set_closed": True,
        "cells": cells_out,
        "r_star_aff": {
            "definition": "smallest r >= 2 with census P_all(W>=1) for cell (A={0},S={0}) <= 2^-30; null if none in r<=10",
            "value": r_star,
            "per_r_P_all": [{"r": c["r"], "num": c["P_Wge1_all_trials"]["num"],
                             "den": c["P_Wge1_all_trials"]["den"],
                             "P_float": c["P_Wge1_all_trials"]["float"],
                             "label": c["label"]} for c in c1],
        },
        "PR5_structure_destroyed_cell": {
            "cell": "C10 (A={0,1,2,3}, S={0})",
            "rule": "census must predict per-trial P within a factor 3 of 2^-30 (record PR-5/F4)",
            "per_r": pr5,
            "verdict_at_r5": pr5[4]["within_factor_3_of_2^-30"],
        },
        "null_cells_exact_2^-30": [
            {"cell_id": ce["cell_id"], "A": ce["A"], "S": ce["S"], "r": c["r"],
             "P": f"{c['P_Wge1_all_trials']['num']}/{c['P_Wge1_all_trials']['den']}"}
            for ce in cells_out for c in ce["rounds"]
            if c["label"] == "SKELETON-NULL"
        ],
        "parse_attestation": "this file is machine-generated JSON; parsed whole with python3 json.load before task completion (stated in RESULTS.json)",
        "inference": {
            "policy": "executor-implementation",
            "requested_policy": "executor-implementation",
            "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
            "model_verified": False,
            "fallback_used": True,
            "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
            "degraded_requirements": [],
            "amendment": "DEC-20260831-0d1eeb",
            "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
        },
    }
    txt = json.dumps(out, indent=1)
    with open(sys.argv[1] if len(sys.argv) > 1 else "runs/census.json", "w") as f:
        f.write(txt)
    print(json.dumps({
        "census_written": True,
        "sha256": hashlib.sha256(txt.encode()).hexdigest(),
        "r_star_aff": r_star,
        "n_null_cells_exact": len(out["null_cells_exact_2^-30"]),
        "PR5_r5_within_band": out["PR5_structure_destroyed_cell"]["verdict_at_r5"],
    }, indent=1))

if __name__ == "__main__":
    main()
