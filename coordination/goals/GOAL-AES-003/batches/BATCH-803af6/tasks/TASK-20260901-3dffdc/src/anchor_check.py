#!/usr/bin/env python3
# anchor_check.py -- TASK-20260901-3dffdc RUN 1 (BLOCKING per F1).
#
# INDEPENDENT recomputation of the BATCH-b41ba9 anchor cell
# (r=5, A={0}, S={0}, SBOX=id): the record's baseline_embedding requires the
# rank quadruple 32,0,0,0 "recomputed independently of the census code".
#
# Independence path: this file builds M_5 / D_5 by BYTE-LEVEL SIMULATION of
# the pinned round functions on basis vectors (the method class of the
# archived algebra_rank.py, re-derived fresh here), NOT by the explicit
# SR/MC matrix products used in census.py. Agreement between the two
# constructions is itself a check.
#
# This file ALSO carries a byte-level empirical check of the executor's
# identity-law preregistration (PREREGISTRATION.md section 7):
#   q0^q1 = p0^p1 and W = 4-|A| on every nontrivial trial, several cells,
# with a real identity-S-box key schedule (FIPS-197 expansion, SubWord =
# identity rotation) -- verifying the linear-algebra identity on actual
# cipher values before any 2^30 arm runs.
import json, sys, datetime

# ---------------- pinned round functions, byte-level (SBOX = id) ----------------
def xt(a): return ((a << 1) ^ ((a >> 7) * 0x1b)) & 0xFF
XT2 = [xt(i) for i in range(256)]
XT4 = [xt(XT2[i]) for i in range(256)]
XT8 = [xt(XT4[i]) for i in range(256)]

def sub_shift(s):      # SB=id then SR: t[4c+r] = s[4*((c+r)&3)+r]
    return [s[4 * ((c + r) & 3) + r] for c in range(4) for r in range(4)]

def inv_sub_shift(s):  # ISR then ISB=id: t[4c+r] = s[4*((c-r+4)&3)+r]
    return [s[4 * ((c - r + 4) & 3) + r] for c in range(4) for r in range(4)]

def mix_columns(s):
    out = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0 ^ a1 ^ a2 ^ a3
        out[4*c]   = a0 ^ t ^ XT2[a0 ^ a1]
        out[4*c+1] = a1 ^ t ^ XT2[a1 ^ a2]
        out[4*c+2] = a2 ^ t ^ XT2[a2 ^ a3]
        out[4*c+3] = a3 ^ t ^ XT2[a3 ^ a0]
    return out

def inv_mix_columns(s):
    out = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        w = [XT8[x] for x in (a0, a1, a2, a3)]
        v = [XT4[x] for x in (a0, a1, a2, a3)]
        u = [XT2[x] for x in (a0, a1, a2, a3)]
        out[4*c]   = w[0]^v[0]^u[0] ^ w[1]^u[1]^a1 ^ w[2]^v[2]^a2 ^ w[3]^a3
        out[4*c+1] = w[0]^a0 ^ w[1]^v[1]^u[1] ^ w[2]^u[2]^a2 ^ w[3]^v[3]^a3
        out[4*c+2] = w[0]^v[0]^a0 ^ w[1]^a1 ^ w[2]^v[2]^u[2] ^ w[3]^u[3]^a3
        out[4*c+3] = w[0]^u[0]^a0 ^ w[1]^v[1]^a1 ^ w[2]^a2 ^ w[3]^v[3]^u[3]
    return out

def enc_linear(st, rounds):   # enc_r with all round keys dropped (linear part)
    for _ in range(1, rounds):
        st = mix_columns(sub_shift(st))
    return sub_shift(st)

def dec_linear(st, rounds):   # dec_r with all round keys dropped (linear part)
    st = inv_sub_shift(st)
    for _ in range(rounds - 1, 0, -1):
        st = inv_sub_shift(inv_mix_columns(st))
    return st

def pack(s): return sum(b << (8 * i) for i, b in enumerate(s))

def apply_cols(cols, v):
    r = 0
    while v:
        lsb = v & -v
        r ^= cols[lsb.bit_length() - 1]
        v ^= lsb
    return r

def gf2_rank(cols):
    basis = {}
    for v in cols:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in basis: x ^= basis[h]
            else: basis[h] = x; break
    return len(basis)

def gf2_inv_from_cols(cols):
    # invert the map given as 128 column ints: solve on augmented rows
    n = len(cols)
    rows = [0] * n
    for i in range(n):
        for j in range(n):
            if (cols[j] >> i) & 1:
                rows[i] |= 1 << j
    aug = [rows[i] | (1 << (n + i)) for i in range(n)]
    for c in range(n):
        piv = next((i for i in range(c, n) if (aug[i] >> c) & 1), None)
        if piv is None: return None
        aug[c], aug[piv] = aug[piv], aug[c]
        for i in range(n):
            if i != c and ((aug[i] >> c) & 1):
                aug[i] ^= aug[c]
    inv_cols = [0] * n
    for i in range(n):
        for j in range(n):
            if (aug[j] >> (n + i)) & 1:
                inv_cols[i] |= 1 << j
    return inv_cols

# ---------------- geometry (pinned) ----------------
PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

def embed_word(v32, j):
    x = 0
    for k in range(4):
        x |= ((v32 >> (8 * k)) & 0xFF) << (8 * PW[j][k])
    return x

def project_word(x, j):
    v = 0
    for k in range(4):
        v |= ((x >> (8 * PW[j][k])) & 0xFF) << (8 * k)
    return v

# ---------------- key schedule, identity S-box (FIPS-197 expansion, SubWord=id) ----
def key_expand_identity(key):
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
    rk = [list(key)]
    for i in range(1, 11):
        t = list(rk[i-1][12:16])
        tmp = t[0]; t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = tmp  # SubWord = id
        t[0] ^= rcon[i-1]
        row = list(rk[i-1])
        for w in range(4):
            for b in range(4):
                row[4*w+b] = rk[i-1][4*w+b] ^ (t[b] if w == 0 else row[4*(w-1)+b])
        rk.append(row)
    return rk

def enc_rk(pt, rk, rounds):
    st = [pt[i] ^ rk[0][i] for i in range(16)]
    for i in range(1, rounds):
        st = mix_columns(sub_shift(st))
        st = [st[k] ^ rk[i][k] for k in range(16)]
    st = sub_shift(st)
    return [st[k] ^ rk[rounds][k] for k in range(16)]

def dec_rk(ct, rk, rounds):
    st = [ct[i] ^ rk[rounds][i] for i in range(16)]
    st = inv_sub_shift(st)
    for i in range(rounds - 1, 0, -1):
        st = [st[k] ^ rk[i][k] for k in range(16)]
        st = inv_sub_shift(inv_mix_columns(st))
    return [st[k] ^ rk[0][k] for k in range(16)]

# ---------------- main ----------------
ROUNDS = 5

M = [0] * 128
D = [0] * 128
for i in range(128):
    st = [0] * 16
    st[i >> 3] = 1 << (i & 7)
    M[i] = pack(enc_linear(st, ROUNDS))
    D[i] = pack(dec_linear(st, ROUNDS))

dm_ok = all(apply_cols(D, apply_cols(M, 1 << i)) == (1 << i) for i in range(128))
md_ok = all(apply_cols(M, apply_cols(D, 1 << i)) == (1 << i) for i in range(128))

Minv = gf2_inv_from_cols(M)
minv_ok = Minv is not None and all(apply_cols(Minv, apply_cols(M, 1 << i)) == (1 << i) for i in range(128))
minv_eq_D = minv_ok and Minv == D

# --- record's census object at the anchor: T = M^{-1} Z_{CW[0]} M -------------
def zmask_cw0(x):
    for i in CW[0]:
        x &= ~(0xFF << (8 * i))
    return x

Tcols = [apply_cols(Minv, zmask_cw0(apply_cols(M, 1 << i))) for i in range(128)]

def word_map_cols_anchor(A_word):
    maps = {j: [] for j in range(4)}
    for k in range(32):
        v = apply_cols(Tcols, embed_word(1 << k, A_word))
        for j in range(4):
            maps[j].append(project_word(v, j))
    return maps

wmaps = word_map_cols_anchor(0)
ranks_T = {j: gf2_rank(wmaps[j]) for j in range(4)}

# --- archived object: P_j (D.M) P_0^T -----------------------------------------
ranks_DM = {}
for j in range(4):
    cols = []
    for k in range(32):
        v = apply_cols(D, apply_cols(M, embed_word(1 << k, 0)))
        cols.append(project_word(v, j))
    ranks_DM[j] = gf2_rank(cols)

# --- census-law P(hit) at the anchor from the joint kernel structure -----------
# domain = PW[0] (32 bits); kernels via stacked ranks
g = {}
for mask in range(16):
    if mask == 0:
        g[0] = 1 << 32
        continue
    cols = [0] * 32
    width = 0
    for j in range(4):
        if mask & (1 << j):
            for p in range(32):
                cols[p] |= wmaps[j][p] << width
            width += 32
    g[mask] = 1 << (32 - gf2_rank(cols))
f = {}
for S in range(16):
    acc = 0
    for J in range(16):
        if J & S == S:
            acc += (-1 if bin(J ^ S).count("1") & 1 else 1) * g[J]
    f[S] = acc
mobius_ok = all(v >= 0 for v in f.values()) and sum(f.values()) == (1 << 32)
num_all = (1 << 32) - f[0]
P_all = num_all / (1 << 32)

anchor_ranks_ok = [ranks_T[j] for j in range(4)] == [32, 0, 0, 0]
anchor_P_ok = num_all == (1 << 32)  # P(hit) = 1.0 exactly
f1_gate = bool(dm_ok and md_ok and minv_ok and minv_eq_D and mobius_ok and anchor_ranks_ok and anchor_P_ok)

# --- empirical identity-law check on actual cipher values ----------------------
import random
rng = random.Random(20260901)
emp_cells = [
    (5, [0], [0]),
    (5, [0], [1]),
    (6, [0], [0]),
    (5, [0, 1], [0]),
    (2, [0], [0]),
    (5, [0, 1, 2, 3], [0]),
]
emp = []
for (r, A, S) in emp_cells:
    stat = {"r": r, "A": A, "S": S, "trials": 0, "qdiff_equals_pdiff": 0,
            "W_equals_4_minus_absA": 0, "trivial_swaps": 0, "whist": [0]*5}
    for _ in range(1000):
        key = [rng.randrange(256) for _ in range(16)]
        rk = key_expand_identity(key)
        p0 = [rng.randrange(256) for _ in range(16)]
        p1 = list(p0)
        while True:
            ok = True
            for j in A:
                nz = False
                for row in range(4):
                    nb = rng.randrange(256)
                    p1[PW[j][row]] = nb
                    if nb != p0[PW[j][row]]: nz = True
                if not nz: ok = False
            if ok: break
        c0 = enc_rk(p0, rk, r); c1 = enc_rk(p1, rk, r)
        trivial = True
        for j in S:
            for row in range(4):
                i = CW[j][row]
                if c0[i] != c1[i]: trivial = False
                c0[i], c1[i] = c1[i], c0[i]
        q0 = dec_rk(c0, rk, r); q1 = dec_rk(c1, rk, r)
        stat["trials"] += 1
        if trivial: stat["trivial_swaps"] += 1
        pdiff = [p0[i] ^ p1[i] for i in range(16)]
        qdiff = [q0[i] ^ q1[i] for i in range(16)]
        if qdiff == pdiff: stat["qdiff_equals_pdiff"] += 1
        W = 0
        for j in range(4):
            if all(q0[PW[j][row]] == q1[PW[j][row]] for row in range(4)):
                W += 1
        stat["whist"][W] += 1
        if W == 4 - len(A): stat["W_equals_4_minus_absA"] += 1
    emp.append(stat)

emp_ok = all(s["qdiff_equals_pdiff"] == s["trials"] and s["W_equals_4_minus_absA"] == s["trials"]
             for s in emp)

out = {
    "schema": "crypto.autoresearch.anchor_check.v1",
    "task_id": "TASK-20260901-3dffdc",
    "run": "RUN 1 (BLOCKING per F1)",
    "idea_record": "IDEA-20260901-ec54fe",
    "anchor_cell": {"r": ROUNDS, "A": [0], "S": [0], "amask": 1, "smask": 1, "sbox": "identity"},
    "independence_note": "byte-level basis-vector simulation of the pinned round functions; no import of or code sharing with census.py (explicit SR/MC matrix products)",
    "D_times_M_is_identity": dm_ok,
    "M_times_D_is_identity": md_ok,
    "gauss_jordan_inverse_ok": minv_ok,
    "gauss_jordan_inverse_equals_D": minv_eq_D,
    "record_census_object_T_at_anchor": {
        "definition": "T = M_5^{-1} . Z_{CW[0]} . M_5; word maps PW[0] -> PW[j]",
        "word_map_ranks": ranks_T,
        "mobius_consistency": mobius_ok,
        "kernel_exact_sizes": {str(S): v for S, v in f.items()},
        "P_Wge1_all_trials": {"num": num_all, "den": 1 << 32, "float": P_all},
    },
    "archived_object_D_compose_M": {
        "definition": "P_j . (D.M) . P_0^T (the archived algebra_rank.py object)",
        "word_map_ranks": ranks_DM,
    },
    "f1_gate": {
        "required": "word_map_ranks == [32,0,0,0] AND P(hit) == 1.0 AND D.M = I (record F1 / PR-1)",
        "ranks_match": anchor_ranks_ok,
        "P_hit_is_1": anchor_P_ok,
        "pass": f1_gate,
    },
    "empirical_identity_law_check": {
        "prediction": "q0^q1 = p0^p1 and W = 4-|A| on every trial, all cells, all keys (PREREGISTRATION.md section 7)",
        "seed": 20260901,
        "cells": emp,
        "pass": emp_ok,
    },
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
with open(sys.argv[1] if len(sys.argv) > 1 else "runs/anchor_recompute.json", "w") as fwrite:
    fwrite.write(txt)
print(json.dumps({
    "f1_gate_pass": f1_gate,
    "T_anchor_ranks": ranks_T,
    "DM_anchor_ranks": ranks_DM,
    "P_hit_all_trials": P_all,
    "empirical_identity_law_pass": emp_ok,
}, indent=1))
sys.exit(0 if f1_gate else 5)
