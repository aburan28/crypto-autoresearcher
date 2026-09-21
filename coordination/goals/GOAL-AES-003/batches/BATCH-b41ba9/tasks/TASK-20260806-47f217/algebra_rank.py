#!/usr/bin/env python3
"""TASK-20260806-47f217 -- algebraic rank computation for the identity/affine arm.

Computes, in code, the four 32x32 GF(2) word maps of the r=5 yoyo trial under
the identity S-box (cipher affine over GF(2)) and their ranks, then freezes
the expected W-count.

The cipher's linear structure is ported EXACTLY from probe_sbox.c
(column-major state byte[4*col+row]; sub_shift/inv_sub_shift with SBOX =
identity; mix_columns/inv_mix_columns with the same xt tables; enc_r/dec_r
round order). Round keys are zeroed: the linear part of an affine map is the
map with constants dropped, and ARK contributes identity to the linear part.

Trial algebra (probe_sbox.c worker, amask=1, smask=1, rounds=5):
  p1 = p0 with word-0 bytes re-randomised, zero word-0 diff rejected
  c0 = E(p0), c1 = E(p1)
  swap ciphertext bytes of CW[0] between c0,c1   (swap preserves XOR diff)
  q0 = D(c0), q1 = D(c1);  d = q0^q1
  W = # words j with d zero on PW[j]
With E affine: c0^c1 = M.(p0^p1); after swap c0'^c1' = c0^c1; and
q0^q1 = M^{-1}.(c0'^c1') = M^{-1}.M.(p0^p1) = p0^p1.  So the word-j map is
  A_j : (p0^p1)|PW[0]  ->  (q0^q1)|PW[j]  =  P_j . (D.M) . P_0^T
which is the identity on word 0 and the zero map on words 1..3 IF D.M = I.
This script verifies D.M = I numerically and computes rank(A_j) for j=0..3.
"""
import json, random

# ---------------- cipher linear structure (port of probe_sbox.c) ----------------
def xt(a): return ((a << 1) ^ ((a >> 7) * 0x1b)) & 0xff
XT2 = [xt(i) for i in range(256)]
XT4 = [xt(XT2[i]) for i in range(256)]
XT8 = [xt(XT4[i]) for i in range(256)]

def mix_columns(s):
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0 ^ a1 ^ a2 ^ a3; u = a0
        s[4*c]   = a0 ^ t ^ XT2[a0 ^ a1]
        s[4*c+1] = a1 ^ t ^ XT2[a1 ^ a2]
        s[4*c+2] = a2 ^ t ^ XT2[a2 ^ a3]
        s[4*c+3] = a3 ^ t ^ XT2[a3 ^ u]

def inv_mix_columns(s):
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        w0, v0, u0 = XT8[a0], XT4[a0], XT2[a0]
        w1, v1, u1 = XT8[a1], XT4[a1], XT2[a1]
        w2, v2, u2 = XT8[a2], XT4[a2], XT2[a2]
        w3, v3, u3 = XT8[a3], XT4[a3], XT2[a3]
        s[4*c]   = w0 ^ v0 ^ u0   ^ w1 ^ u1 ^ a1 ^ w2 ^ v2 ^ a2 ^ w3 ^ a3
        s[4*c+1] = w0 ^ a0       ^ w1 ^ v1 ^ u1 ^ w2 ^ u2 ^ a2 ^ w3 ^ v3 ^ a3
        s[4*c+2] = w0 ^ v0 ^ a0  ^ w1 ^ a1    ^ w2 ^ v2 ^ u2 ^ w3 ^ u3 ^ a3
        s[4*c+3] = w0 ^ u0 ^ a0  ^ w1 ^ v1 ^ a1 ^ w2 ^ a2    ^ w3 ^ v3 ^ u3

def sub_shift(s):            # identity SBOX: t[4c+r] = s[4*((c+r)&3)+r]
    t = [0]*16
    for c in range(4):
        for r in range(4):
            t[4*c+r] = s[4*((c+r) & 3) + r]
    return t

def inv_sub_shift(s):        # identity SBOX: t[4c+r] = s[4*((c-r+4)&3)+r]
    t = [0]*16
    for c in range(4):
        for r in range(4):
            t[4*c+r] = s[4*((c - r + 4) & 3) + r]
    return t

def enc_linear(st, rounds):  # enc_r with all round keys zeroed
    for _ in range(1, rounds):
        st = sub_shift(st)
        mix_columns(st)
    return sub_shift(st)

def dec_linear(st, rounds):  # dec_r with all round keys zeroed
    st = inv_sub_shift(st)
    for _ in range(rounds - 1, 0, -1):
        inv_mix_columns(st)
        st = inv_sub_shift(st)
    return st

def pack(s): return sum(s[i] << (8*i) for i in range(16))

# --------------- GF(2) linear algebra ---------------
def gf2_rank(cols, width=32):
    """Rank of the span of `cols` (each an int < 2^width) over GF(2)."""
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

def mat_apply(cols, v):
    """cols: list of 128 columns (each an int); returns XOR of cols[i] for set bits i of v."""
    r = 0
    while v:
        lsb = v & -v
        i = lsb.bit_length() - 1
        r ^= cols[i]
        v ^= lsb
    return r

# --------------- geometry (identical to probe_sbox.c) ---------------
PW = [[4*((j+row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4*((j-row) % 4) + row for row in range(4)] for j in range(4)]

ROUNDS = 5

# --------------- build the 128x128 linear matrices M (enc) and D (dec) ---------------
M = [0]*128   # M[i] = column i = enc_linear(e_i)
D = [0]*128   # D[i] = column i = dec_linear(e_i)
for i in range(128):
    st = [0]*16
    st[i >> 3] = 1 << (i & 7)
    M[i] = pack(enc_linear(st, ROUNDS))
    D[i] = pack(dec_linear(st, ROUNDS))

# verify D.M = I and M.D = I
dm_ok = all(mat_apply(D, mat_apply(M, 1 << i)) == (1 << i) for i in range(128))
md_ok = all(mat_apply(M, mat_apply(D, 1 << i)) == (1 << i) for i in range(128))

# --------------- the four 32x32 word maps A_j = P_j . (D.M) . P_0^T ---------------
def embed_word0(v32):
    """embed a 32-bit word-0 diff into the 128-bit plaintext-diff space."""
    x = 0
    for k in range(4):
        x |= ((v32 >> (8*k)) & 0xff) << (8 * PW[0][k])
    return x

def project_word(x, j):
    v = 0
    for k in range(4):
        v |= ((x >> (8 * PW[j][k])) & 0xff) << (8*k)
    return v

word_maps = {}   # j -> 32 columns of A_j
for j in range(4):
    cols = []
    for k in range(32):
        e = 1 << k
        x = mat_apply(D, mat_apply(M, embed_word0(e)))   # full 128-bit q-diff
        cols.append(project_word(x, j))
    word_maps[j] = cols

ranks = {j: gf2_rank(word_maps[j]) for j in range(4)}

# --- trivial-swap map: word-0 diff -> (M.diff)|CW[0] (ciphertext bytes) ---
tcols = []
for k in range(32):
    e = 1 << k
    x = mat_apply(M, embed_word0(e))
    v = 0
    for kk in range(4):
        v |= ((x >> (8 * CW[0][kk])) & 0xff) << (8*kk)
    tcols.append(v)
rank_trivial = gf2_rank(tcols)

# --------------- frozen expectation ---------------
N = 1 << 32
p_word = {j: 2.0 ** (-ranks[j]) for j in range(4)}
E_W_per_trial = sum(p_word.values())                 # E[W] per trial (2^-rank formula)
p_trivial = 2.0 ** (-rank_trivial)
E_trivial_count = N * p_trivial
# exact per-trial E[W_ge1]: word-0 input is conditioned NONZERO (the worker
# rejects an all-equal re-randomisation), so the word-0 output (identity map)
# is never zero; words 1..3 are deterministic zeros -> W>=1 on every
# nontrivial trial.
E_Wge1_per_trial = 1.0
E_Wge1_count = (N - E_trivial_count) * E_Wge1_per_trial
excess_E = E_Wge1_count / ((N - E_trivial_count) * 2.0 ** -30)

# --------------- empirical byte-level confirmation (affine cipher, real key) ---------------
def key_expand_identity(key):
    rcon = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]
    rk = [list(key)]
    for i in range(1, 11):
        t = rk[i-1][12:16]
        tmp = t[0]; t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = tmp   # SBOX=identity
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
        st = sub_shift(st); mix_columns(st)
        st = [st[k] ^ rk[i][k] for k in range(16)]
    st = sub_shift(st)
    return [st[k] ^ rk[rounds][k] for k in range(16)]

def dec_rk(ct, rk, rounds):
    st = [ct[i] ^ rk[rounds][i] for i in range(16)]
    st = inv_sub_shift(st)
    for i in range(rounds - 1, 0, -1):
        st = [st[k] ^ rk[i][k] for k in range(16)]
        inv_mix_columns(st)
        st = inv_sub_shift(st)
    return [st[k] ^ rk[0][k] for k in range(16)]

rng = random.Random(424242301)
emp = {"trials": 0, "qdiff_equals_pdiff": 0, "W_always_3": 0, "Wge1_always": 0,
       "zhist": [0]*17, "whist": [0]*5}
for _ in range(2000):
    key = [rng.randrange(256) for _ in range(16)]
    rk = key_expand_identity(key)
    p0 = [rng.randrange(256) for _ in range(16)]
    p1 = list(p0)
    while True:
        for row in range(4):
            p1[PW[0][row]] = rng.randrange(256)
        if any(p1[PW[0][row]] != p0[PW[0][row]] for row in range(4)):
            break
    c0 = enc_rk(p0, rk, ROUNDS); c1 = enc_rk(p1, rk, ROUNDS)
    for i in CW[0]:
        c0[i], c1[i] = c1[i], c0[i]
    q0 = dec_rk(c0, rk, ROUNDS); q1 = dec_rk(c1, rk, ROUNDS)
    pdiff = [p0[i] ^ p1[i] for i in range(16)]
    qdiff = [q0[i] ^ q1[i] for i in range(16)]
    emp["trials"] += 1
    if qdiff == pdiff: emp["qdiff_equals_pdiff"] += 1
    Z = sum(1 for i in range(16) if q0[i] == q1[i]); emp["zhist"][Z] += 1
    W = 0
    for j in range(4):
        if all(q0[PW[j][row]] == q1[PW[j][row]] for row in range(4)):
            W += 1
    emp["whist"][W] += 1
    if W == 3: emp["W_always_3"] += 1
    if W >= 1: emp["Wge1_always"] += 1

# --------------- print ---------------
print(json.dumps({
    "rounds": ROUNDS,
    "geometry": {"PW": PW, "CW": CW},
    "D_times_M_is_identity": dm_ok,
    "M_times_D_is_identity": md_ok,
    "word_maps_rank": ranks,
    "word_maps_nullity": {j: 32 - ranks[j] for j in range(4)},
    "word_maps_hex": {j: ["%08x" % c for c in word_maps[j]] for j in range(4)},
    "per_word_zero_prob_2^-rank": {j: p_word[j] for j in range(4)},
    "E_W_per_trial_sum_2^-rank": E_W_per_trial,
    "E_Wge1_per_trial_exact": E_Wge1_per_trial,
    "trivial_swap_map_rank": rank_trivial,
    "trivial_swap_probability": p_trivial,
    "E_trivial_count_at_2^32": E_trivial_count,
    "E_Wge1_count_at_2^32": E_Wge1_count,
    "excess_E": excess_E,
    "empirical_affine_check": emp,
}, indent=1))