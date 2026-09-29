#!/usr/bin/env python3
"""TASK-20260901-e95e2e validator RUN 1 -- fresh sparse GF(2) re-derivation.

Independent of producer code (census046.py / gate0.py never read; definitions
taken from IDEA-20260901-04606c claim/object/convention text and the pinned
cipher convention E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB] . ARK_0,
FIPS-197 ShiftRows/MixColumns, column-major state byte[4*col+row]).

Matrices are 128x128 over GF(2), stored as 128 column integers
(col[j] bit i = image row of input bit j).
"""
import json, sys

N = 128

def mat_cols_apply(f):
    """build matrix whose columns are f(e_j)."""
    return [f(1 << j) for j in range(N)]

def mat_vec(M, x):
    y = 0
    j = 0
    while x:
        if x & 1:
            y ^= M[j]
        x >>= 1
        j += 1
    return y

def mat_mul(A, B):
    return [mat_vec(A, c) for c in B]

def is_identity(M):
    return all(M[j] == (1 << j) for j in range(N))

def gf256_mul(a, b):
    # fresh GF(2^8) multiply, poly 0x11b (FIPS-197), russian-peasant
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r

def xt(a):
    return gf256_mul(a, 2)

# ---- ShiftRows / InvShiftRows as bit permutation matrices (FIPS-197 offsets 0,1,2,3)
def build_sr():
    cols = [0] * N
    for i in range(16):            # input byte index
        ci, ri = divmod(i, 4)      # column-major: i = 4*col + row
        oc = (ci - ri) & 3         # output byte that receives input (ci,ri)
        o = 4 * oc + ri
        for b in range(8):
            cols[8 * i + b] = 1 << (8 * o + b)
    return cols

def build_isr():
    cols = [0] * N
    for o in range(16):            # output byte index
        co, ro = divmod(o, 4)
        ic = (co - ro) & 3         # inv_sub_shift: t[4c+r] = s[4*((c-r+4)&3)+r]
        i = 4 * ic + ro
        for b in range(8):
            cols[8 * i + b] = 1 << (8 * o + b)
    return cols

# ---- MixColumns / InvMixColumns from the FIPS-197 spec matrices
def block_matrix(rows_consts):
    """4x4 byte-block circulant given first-column constants, as 32x32 GF(2) cols.
    FIPS-197: M[i][c] = consts[(c - i) mod 4]  (out[i] = sum_c M[i][c] * in[c])."""
    cols = [0] * 32
    for j in range(32):            # input bit j = byte bj = j//8, bit bb = j%8
        bj, bb = divmod(j, 8)
        out = [0, 0, 0, 0]
        for i in range(4):         # output byte i
            if rows_consts[(bj - i) % 4]:
                out[i] = gf256_mul(rows_consts[(bj - i) % 4], 1 << bb)
        v = 0
        for i in range(4):
            v |= out[i] << (8 * i)
        cols[j] = v
    return cols

def lift_blocks(block):
    """lift a 32x32 column block to a 128x128 matrix acting identically on all 4 columns."""
    M = [0] * N
    for colbyte in range(4):
        for j in range(32):
            i = 32 * colbyte
            M[i + j] = block[j] << i
    return M

SR = build_sr()
ISR = build_isr()
MC = lift_blocks(block_matrix([2, 3, 1, 1]))       # FIPS-197 MixColumns first column
IMC = lift_blocks(block_matrix([0x0E, 0x0B, 0x0D, 0x09]))

# ---- cross-check my spec matrices against the PINNED byte-level expressions
# (expressions copied from the pinned convention header, implemented fresh here):
#   mix:  t=a0^a1^a2^a3; s_i = a_i ^ t ^ xt(a_i ^ a_{i+1})
#   invmix via xt2/xt4/xt8 table expression of probe lineage
def pinned_mix(col):
    a0, a1, a2, a3 = col
    t = a0 ^ a1 ^ a2 ^ a3
    return [a0 ^ t ^ xt(a0 ^ a1), a1 ^ t ^ xt(a1 ^ a2),
            a2 ^ t ^ xt(a2 ^ a3), a3 ^ t ^ xt(a3 ^ a0)]

def pinned_invmix(col):
    a0, a1, a2, a3 = col
    x2 = [xt(a) for a in col]
    x4 = [xt(a) for a in x2]
    x8 = [xt(a) for a in x4]
    # verbatim from the pinned inv_mix_columns C expression
    return [x8[0] ^ x4[0] ^ x2[0] ^ x8[1] ^ x2[1] ^ a1 ^ x8[2] ^ x4[2] ^ a2 ^ x8[3] ^ a3,
            x8[0] ^ a0 ^ x8[1] ^ x4[1] ^ x2[1] ^ x8[2] ^ x2[2] ^ a2 ^ x8[3] ^ x4[3] ^ a3,
            x8[0] ^ x4[0] ^ a0 ^ x8[1] ^ a1 ^ x8[2] ^ x4[2] ^ x2[2] ^ x8[3] ^ x2[3] ^ a3,
            x8[0] ^ x2[0] ^ a0 ^ x8[1] ^ x4[1] ^ a1 ^ x8[2] ^ a2 ^ x8[3] ^ x4[3] ^ x2[3]]

def spec_block_vec(block, col):
    v = col[0] | col[1] << 8 | col[2] << 16 | col[3] << 24
    y = mat_vec(block, v)
    return [y & 255, (y >> 8) & 255, (y >> 16) & 255, (y >> 24) & 255]

mc_block = block_matrix([2, 3, 1, 1])
imc_block = block_matrix([0x0E, 0x0B, 0x0D, 0x09])
mc_expr_ok = imc_expr_ok = True
for j in range(32):  # linearity: basis agreement == exhaustive agreement
    col = [0, 0, 0, 0]
    col[j // 8] = 1 << (j % 8)
    if spec_block_vec(mc_block, col) != pinned_mix(col):
        mc_expr_ok = False
    if spec_block_vec(imc_block, col) != pinned_invmix(col):
        imc_expr_ok = False

# ---- geometry from the pinned formulas (record object / probe header)
PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

# ---- round-count linear parts under SBOX = id (ARK drops on differences):
# enc_r order applied to p: SR, MC, SR, MC, ..., SR  (r SRs, r-1 MCs, SR first)
#   => M_r = (SR.MC)^{r-1} . SR
# dec_r order applied to c: ISR, IMC, ISR, IMC, ..., ISR (r ISRs, r-1 IMCs)
#   => D_r = ISR . (IMC.ISR)^{r-1}
Mr = {}
cur = SR
for r in range(1, 11):
    Mr[r] = cur
    cur = mat_mul(SR, mat_mul(MC, cur))   # M_{r+1} = SR.MC . M_r
Dr = {}
cur = ISR
for r in range(1, 11):
    Dr[r] = cur
    cur = mat_mul(ISR, mat_mul(IMC, cur))  # D_{r+1} = ISR.IMC . D_r

guards = {}
for r in range(1, 11):
    guards[r] = {
        "DrMr_is_I": is_identity(mat_mul(Dr[r], Mr[r])),
        "MrDr_is_I": is_identity(mat_mul(Mr[r], Dr[r])),
    }

def word_map_matrix(r, A, j):
    """return 32-bit columns: image of each domain bit restricted to PW[j]."""
    DM = mat_mul(Dr[r], Mr[r])
    pj_rows = []
    for row in range(4):
        for b in range(8):
            pj_rows.append(8 * PW[j][row] + b)
    domain_bits = []
    for w in sorted(A):
        for row in range(4):
            for b in range(8):
                domain_bits.append(8 * PW[w][row] + b)
    cols = []
    for db in domain_bits:
        y = mat_vec(DM, 1 << db)
        c = 0
        for k, rb in enumerate(pj_rows):
            if (y >> rb) & 1:
                c |= 1 << k
        cols.append(c)
    return cols  # 32*|A| columns, each 32-bit

def rank_proper(cols):
    basis = []
    for v in cols:
        for b in basis:
            if v & (1 << (b.bit_length() - 1)):
                v ^= b
        if v:
            basis.append(v)
            basis.sort(key=lambda x: x.bit_length() - 1, reverse=True)
    return len(basis)

def expected_word_map(A, j):
    """P_j Pi_A: identity block for word j if j in A, else zero. Domain words asc."""
    cols = []
    for p, w in enumerate(sorted(A)):
        for k in range(32):
            if w == j:
                cols.append(1 << k)
            else:
                cols.append(0)
    return cols

def rho(r, A, S):
    """rank of d|PW[A] -> (M_r d)|CW[S]."""
    rows = []
    for w in sorted(S):
        for row in range(4):
            for b in range(8):
                rows.append(8 * CW[w][row] + b)
    cols = []
    for w in sorted(A):
        for row in range(4):
            for b in range(8):
                y = mat_vec(Mr[r], 1 << (8 * PW[w][row] + b))
                c = 0
                for k, rb in enumerate(rows):
                    if (y >> rb) & 1:
                        c |= 1 << k
                cols.append(c)
    return rank_proper(cols)

PR1 = {  # transcribed verbatim from IDEA-20260901-04606c predictions PR-1
    ((0,), (0,)):        [8,32,8,32,32,32,32,32,8,32],
    ((0,), (1,)):        [8,0,8,32,32,32,32,32,8,0],
    ((0,), (2,)):        [8,0,8,32,32,32,32,32,8,0],
    ((0,), (3,)):        [8,0,8,32,32,32,32,32,8,0],
    ((1,), (1,)):        [8,32,8,32,32,32,32,32,8,32],
    ((2,), (2,)):        [8,32,8,32,32,32,32,32,8,32],
    ((3,), (3,)):        [8,32,8,32,32,32,32,32,8,32],
    ((0,1), (0,)):       [16,32,16,32,32,32,32,32,16,32],
    ((0,), (0,1)):       [16,32,16,32,32,32,32,32,16,32],
    ((0,1,2,3), (0,)):   [32,32,32,32,32,32,32,32,32,32],
}

out = {}
out["mc_spec_vs_pinned_expr"] = mc_expr_ok
out["imc_spec_vs_pinned_expr"] = imc_expr_ok
out["sanity_ISR_inverts_SR"] = is_identity(mat_mul(ISR, SR)) and is_identity(mat_mul(SR, ISR))
out["sanity_IMC_inverts_MC"] = is_identity(mat_mul(IMC, MC)) and is_identity(mat_mul(MC, IMC))
out["PW"] = PW
out["CW"] = CW
out["per_r_guards"] = guards

# Gate-0 anchor re-derivation (r=5, A={0})
A0 = (0,)
anchor = {"r": 5, "A": list(A0)}
ranks = []
col_eq = []
for j in range(4):
    wm = word_map_matrix(5, A0, j)
    ranks.append(rank_proper(wm))
    col_eq.append(wm == expected_word_map(A0, j))
anchor["word_map_ranks"] = ranks
anchor["word_maps_column_equal_PjPiA"] = col_eq
anchor["required_ranks"] = [32, 0, 0, 0]
anchor["D5M5_I128"] = guards[5]["DrMr_is_I"]
anchor["M5D5_I128"] = guards[5]["MrDr_is_I"]
out["anchor_gate0_rederivation"] = anchor

# Validator-chosen census subset
subset_cells = [
    ("anchor", (0,), (0,), 5),
    ("A1_rho8_r9", (0,), (0,), 9),
    ("A1_word3_r5", (3,), (3,), 5),
    ("A4_structure_destroyed_r5", (0,1,2,3), (0,), 5),
    ("degenerate_rho0_r2_S1", (0,), (1,), 2),
    ("degenerate_rho0_r10_S3", (0,), (3,), 10),
    ("A2_rho16_r1", (0,1), (0,), 1),
    ("S2_rho16_r3", (0,), (0,1), 3),
]
subset = []
for name, A, S, r in subset_cells:
    entry = {"name": name, "r": r, "A": list(A), "S": list(S)}
    wmaps = [word_map_matrix(r, A, j) for j in range(4)]
    entry["word_map_ranks"] = [rank_proper(w) for w in wmaps]
    entry["required_rank_pattern"] = [32 if j in A else 0 for j in range(4)]
    entry["word_maps_column_equal_PjPiA"] = [wmaps[j] == expected_word_map(A, j) for j in range(4)]
    entry["W_deterministic"] = 4 - len(A)
    entry["P_Wge1_nontrivial"] = 1.0 if len(A) <= 3 else 0.0
    rr = rho(r, A, S)
    entry["rho_rederived"] = rr
    entry["rho_preregistered"] = PR1[(A, S)][r - 1]
    entry["rho_ok"] = rr == PR1[(A, S)][r - 1]
    entry["cell_ok"] = (entry["word_map_ranks"] == entry["required_rank_pattern"]
                        and all(entry["word_maps_column_equal_PjPiA"])
                        and entry["rho_ok"])
    subset.append(entry)
out["census_subset_rederived"] = subset

# full PR-1 rho table re-derivation for all 10 cells x r=1..10 (cheap: 100 ranks of <=32-col matrices)
full = {}
allrho_ok = True
for (A, S), row in PR1.items():
    got = [rho(r, A, S) for r in range(1, 11)]
    full["%s|%s" % (A, S)] = {"rederived": got, "preregistered": row, "match": got == row}
    if got != row:
        allrho_ok = False
out["full_rho_table_rederived"] = full
out["full_rho_table_match"] = allrho_ok

json.dump(out, sys.stdout, indent=1)
print()
