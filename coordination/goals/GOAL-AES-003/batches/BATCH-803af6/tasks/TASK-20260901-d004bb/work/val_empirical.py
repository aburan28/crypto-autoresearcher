#!/usr/bin/env python3
"""Validator fresh re-derivation (RUN 2): byte-level empirical identity-law check.

Fresh implementation of the pinned probe trial semantics from
BATCH-b41ba9 probe_sbox.c (read directly): p0 draw, active-word re-randomisation
with zero-word-diff rejection, enc/enc, CW-word ciphertext swap with trivial-swap
detection, dec/dec, W over PW words. SBOX = id throughout. Key schedule with
identity SubWord (rotation + rcon), exactly key_expand under SBOX[i]=i.
No producer code imported. Matrices rebuilt from the same pinned byte formulas.
"""
import json, random, sys

MASK64 = (1 << 64) - 1

def xtime(a):
    a &= 0xff
    r = (a << 1) & 0xff
    if a & 0x80: r ^= 0x1b
    return r

# ---- pinned round functions (probe_sbox.c, SBOX = id) ----
def sub_shift(s):
    t = [0]*16
    for c in range(4):
        for r in range(4):
            t[4*c+r] = s[4*((c+r) & 3)+r]
    return t

def inv_sub_shift(s):
    t = [0]*16
    for c in range(4):
        for r in range(4):
            t[4*c+r] = s[4*((c-r+4) & 3)+r]
    return t

def mix_columns(s):
    out = list(s)
    for c in range(4):
        a0,a1,a2,a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0^a1^a2^a3; u = a0
        out[4*c]   = a0 ^ t ^ xtime(a0^a1)
        out[4*c+1] = a1 ^ t ^ xtime(a1^a2)
        out[4*c+2] = a2 ^ t ^ xtime(a2^a3)
        out[4*c+3] = a3 ^ t ^ xtime(a3^u)
    return out

XT2 = [xtime(i) for i in range(256)]
XT4 = [XT2[XT2[i]] for i in range(256)]
XT8 = [XT2[XT4[i]] for i in range(256)]

def inv_mix_columns(s):
    out = list(s)
    for c in range(4):
        a0,a1,a2,a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        w0,v0,u0 = XT8[a0],XT4[a0],XT2[a0]
        w1,v1,u1 = XT8[a1],XT4[a1],XT2[a1]
        w2,v2,u2 = XT8[a2],XT4[a2],XT2[a2]
        w3,v3,u3 = XT8[a3],XT4[a3],XT2[a3]
        out[4*c]   = w0^v0^u0 ^ w1^u1^a1 ^ w2^v2^a2 ^ w3^a3
        out[4*c+1] = w0^a0   ^ w1^v1^u1 ^ w2^u2^a2 ^ w3^v3^a3
        out[4*c+2] = w0^v0^a0 ^ w1^a1   ^ w2^v2^u2 ^ w3^u3^a3
        out[4*c+3] = w0^u0^a0 ^ w1^v1^a1 ^ w2^a2   ^ w3^v3^u3
    return out

def add_rk(s, rk):
    return [s[i] ^ rk[i] for i in range(16)]

RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]

def key_expand_identity(key):
    # FIPS-197 expansion with SubWord = identity (SBOX[i]=i): rotate + rcon
    rk = [[list(key[4*w:4*w+4]) for w in range(4)]]
    for i in range(1, 11):
        t = list(rk[i-1][3])
        t = [t[1], t[2], t[3], t[0]]
        t[0] ^= RCON[i-1]
        nw = []
        for w in range(4):
            prev = rk[i-1][w]
            if w == 0:
                nw.append([prev[b] ^ t[b] for b in range(4)])
            else:
                nw.append([prev[b] ^ nw[w-1][b] for b in range(4)])
        rk.append(nw)
    flat = []
    for i in range(11):
        flat.append([b for w in range(4) for b in rk[i][w]])
    return flat

def enc_r(p, rks, r):
    st = add_rk(list(p), rks[0])
    for i in range(1, r):
        st = add_rk(mix_columns(sub_shift(st)), rks[i])
    return add_rk(sub_shift(st), rks[r])

def dec_r(c, rks, r):
    st = add_rk(list(c), rks[r])
    st = inv_sub_shift(st)
    for i in range(r-1, 0, -1):
        st = inv_sub_shift(inv_mix_columns(add_rk(st, rks[i])))
    return add_rk(st, rks[0])

PW = [[4*(((j+row)%4+4)%4)+row for row in range(4)] for j in range(4)]
CW = [[4*(((j-row)%4+4)%4)+row for row in range(4)] for j in range(4)]

# ---- GF(2) matrices (row-wise), rebuilt fresh ----
N = 128

def perm_matrix(out_from):
    M = [0]*N
    for obit in range(N):
        obyte, b = divmod(obit, 8)
        M[obit] = 1 << (out_from[obyte]*8 + b)
    return M

def byte_linear_matrix(fn):
    M = [0]*N
    for ibit in range(N):
        s = [0]*16
        s[ibit//8] = 1 << (ibit % 8)
        o = fn(s)
        for obyte in range(16):
            for ob in range(8):
                if (o[obyte] >> ob) & 1:
                    M[8*obyte + ob] |= 1 << ibit
    return M

def transpose(M):
    T = [0]*N
    for i in range(N):
        r = M[i]
        while r:
            lsb = r & (-r)
            j = lsb.bit_length()-1
            T[j] |= 1 << i
            r ^= lsb
    return T

def mat_mul(A, B):
    out = [0]*N
    for i in range(N):
        r = A[i]; v = 0
        while r:
            lsb = r & (-r)
            k = lsb.bit_length()-1
            v ^= B[k]
            r ^= lsb
        out[i] = v
    return out

def identity(): return [1 << i for i in range(N)]

def apply_mat(MT, v):  # MT = transpose(M); image of v via columns
    out = 0
    r = v
    while r:
        lsb = r & (-r)
        k = lsb.bit_length()-1
        out ^= MT[k]
        r ^= lsb
    return out

SR = perm_matrix({4*c+r: 4*((c+r) & 3)+r for c in range(4) for r in range(4)})
ISR = perm_matrix({4*c+r: 4*((c-r+4) & 3)+r for c in range(4) for r in range(4)})
MC = byte_linear_matrix(mix_columns)
IMC = byte_linear_matrix(inv_mix_columns)
I128 = identity()
assert mat_mul(SR, ISR) == I128 and mat_mul(MC, IMC) == I128

def M_enc(r):
    P = identity(); MCS = mat_mul(MC, SR)
    for _ in range(r-1): P = mat_mul(MCS, P)
    return mat_mul(SR, P)

def M_dec(r):
    P = identity(); ISRI = mat_mul(ISR, IMC)
    for _ in range(r-1): P = mat_mul(ISRI, P)
    return mat_mul(P, ISR)

def Zkeep_matrix(S):
    keep_bytes = []
    for j in S: keep_bytes += CW[j]
    keep = 0
    for b in keep_bytes: keep |= 0xff << (8*b)
    return [row & keep for row in I128]

def Zzero_matrix(S):
    keep_bytes = []
    for j in S: keep_bytes += CW[j]
    keep = 0
    for b in keep_bytes: keep |= 0xff << (8*b)
    return [row & ~keep for row in I128]

def state_to_int(x):
    v = 0
    for i in range(16): v |= x[i] << (8*i)
    return v

def int_to_state(v):
    return [(v >> (8*i)) & 0xff for i in range(16)]

rng = random.Random(901125)

# ---- self-check: byte-level enc/dec match the GF(2) matrices (affine part) ----
_chk_key = bytes(rng.getrandbits(8) for _ in range(16))
_chk_rks = key_expand_identity(list(_chk_key))
for _r in (2, 5, 6, 10):
    _MT = transpose(M_enc(_r)); _DT = transpose(M_dec(_r))
    _e0 = state_to_int(enc_r([0]*16, _chk_rks, _r))
    _d0 = state_to_int(dec_r([0]*16, _chk_rks, _r))
    for _ in range(50):
        _p = [rng.getrandbits(8) for _ in range(16)]
        _pv = state_to_int(_p)
        assert state_to_int(enc_r(_p, _chk_rks, _r)) == (apply_mat(_MT, _pv) ^ _e0)
        assert state_to_int(dec_r(_p, _chk_rks, _r)) == (apply_mat(_DT, _pv) ^ _d0)
        assert dec_r(enc_r(_p, _chk_rks, _r), _chk_rks, _r) == _p

out = {"schema": "validator.empirical_identity_law.v1", "task_id": "TASK-20260901-d004bb",
       "seed": 901125, "cells": [],
       "selfcheck": "byte-level enc/dec == matrix affine maps + exact roundtrip, r in {2,5,6,10}, 50 states each: PASS"}

mat_cache = {}
def ops_for(r, S):
    key = (r, tuple(S))
    if key not in mat_cache:
        M = M_enc(r); D = M_dec(r)
        assert mat_mul(D, M) == I128 and mat_mul(M, D) == I128
        Tk = mat_mul(mat_mul(D, Zkeep_matrix(S)), M)
        Tz = mat_mul(mat_mul(D, Zzero_matrix(S)), M)
        mat_cache[key] = (transpose(Tk), transpose(Tz))
    return mat_cache[key]

cells = [
    (5, [0],       [0]),
    (5, [0],       [1]),
    (6, [0],       [0]),
    (5, [0,1],     [0]),
    (2, [0],       [0]),
    (5, [0,1,2,3], [0]),
]
TRIALS = 1000

for (r, A, S) in cells:
    TkT, TzT = ops_for(r, S)
    amask = 0
    for j in A: amask |= 1 << j
    smask = 0
    for j in S: smask |= 1 << j
    key = bytes(rng.getrandbits(8) for _ in range(16))
    rks = key_expand_identity(list(key))
    c = {"r": r, "A": A, "S": S, "trials": TRIALS,
         "qdiff_equals_pdiff": 0, "W_equals_4_minus_absA": 0,
         "trivial_swaps": 0,
         "q0_xor_p0_equals_Tkeep_d": 0, "q0_xor_p0_equals_Tzero_d": 0,
         "whist": [0]*5}
    for _ in range(TRIALS):
        p0 = [rng.getrandbits(8) for _ in range(16)]
        p1 = list(p0)
        ok = False
        while not ok:
            ok = True
            for j in range(4):
                if amask & (1 << j):
                    rnd = rng.getrandbits(64)
                    nz = False
                    for row in range(4):
                        nb = (rnd >> (8*row)) & 0xff
                        p1[PW[j][row]] = nb
                        if nb != p0[PW[j][row]]: nz = True
                    if not nz: ok = False
        c0 = enc_r(p0, rks, r); c1 = enc_r(p1, rks, r)
        trivial = True
        for j in range(4):
            if smask & (1 << j):
                for row in range(4):
                    i = CW[j][row]
                    x, y = c0[i], c1[i]
                    if x != y: trivial = False
                    c0[i], c1[i] = y, x
        if trivial: c["trivial_swaps"] += 1
        q0 = dec_r(c0, rks, r); q1 = dec_r(c1, rks, r)
        p0v = state_to_int(p0); p1v = state_to_int(p1)
        q0v = state_to_int(q0); q1v = state_to_int(q1)
        pdiff = p0v ^ p1v; qdiff = q0v ^ q1v
        dv = pdiff
        if qdiff == pdiff: c["qdiff_equals_pdiff"] += 1
        W = 0
        for j in range(4):
            z = True
            for row in range(4):
                if q0[PW[j][row]] != q1[PW[j][row]]:
                    z = False; break
            if z: W += 1
        if not trivial:
            c["whist"][W] += 1
            if W == 4 - len(A): c["W_equals_4_minus_absA"] += 1
        if (q0v ^ p0v) == apply_mat(TkT, dv): c["q0_xor_p0_equals_Tkeep_d"] += 1
        if (q0v ^ p0v) == apply_mat(TzT, dv): c["q0_xor_p0_equals_Tzero_d"] += 1
    out["cells"].append(c)

out["predictions"] = {
    "qdiff_equals_pdiff": "all trials, all cells (identity law of the affine limit)",
    "W_equals_4_minus_absA": "all nontrivial trials",
    "q0_xor_p0_equals_Tkeep_d": "all trials (one-sided yoyo difference = keep-mask perturbation)",
    "q0_xor_p0_equals_Tzero_d": "expected ~0 (record's zero-mask object describes no instrument quantity)",
}
with open(sys.argv[1], "w") as f:
    json.dump(out, f, indent=1)
for c in out["cells"]:
    print(f"r={c['r']} A={c['A']} S={c['S']}: qdiff==pdiff {c['qdiff_equals_pdiff']}/{c['trials']}, "
          f"W=4-|A| {c['W_equals_4_minus_absA']}/{c['trials']-c['trivial_swaps']}, "
          f"trivial {c['trivial_swaps']}, q0^p0==Tkeep {c['q0_xor_p0_equals_Tkeep_d']}/{c['trials']}, "
          f"q0^p0==Tzero {c['q0_xor_p0_equals_Tzero_d']}/{c['trials']}, whist {c['whist']}")
print("OK")
