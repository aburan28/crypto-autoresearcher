#!/usr/bin/env python3
"""Validator fresh re-derivation (RUN 1): GF(2) census ranks, TASK-20260901-d004bb.

Built ONLY from:
  - IDEA-20260901-ec54fe.yaml object/claim definitions (T_{r,S} = M_r^{-1} Z_{CW[S]} M_r)
  - pinned cipher convention E_K^r = ARK_r.SR.SB.[ARK_i.MC.SR.SB]_{i=r-1..1}.ARK_0
  - BATCH-b41ba9 probe_sbox.c byte-level formulas (sub_shift/inv_sub_shift/
    mix_columns/inv_mix_columns) and build_geom PW/CW formulas + geom.json values
No producer code read or reused (producer census.py NOT imported).
"""
import json, sys

N = 128

def xtime(a):
    a &= 0xff
    r = (a << 1) & 0xff
    if a & 0x80: r ^= 0x1b
    return r

def gmul(a, b):  # GF(2^8) mult, poly 0x11b
    p = 0
    for _ in range(8):
        if b & 1: p ^= a
        b >>= 1
        a = xtime(a)
    return p

# ---- byte permutations from pinned probe_sbox.c (SBOX = id) ----
def sr_perm():      # sub_shift: t[4*c+r] = s[4*((c+r)&3)+r]
    out_from = {}
    for c in range(4):
        for r in range(4):
            out_from[4*c+r] = 4*((c+r) & 3)+r
    return out_from

def isr_perm():     # inv_sub_shift: t[4*c+r] = s[4*((c-r+4)&3)+r]
    out_from = {}
    for c in range(4):
        for r in range(4):
            out_from[4*c+r] = 4*((c-r+4) & 3)+r
    return out_from

def perm_matrix(out_from):
    M = [0]*N
    for obit in range(N):
        obyte, b = divmod(obit, 8)
        ibyte = out_from[obyte]
        M[obit] = 1 << (ibyte*8 + b)
    return M

# ---- MixColumns from harness byte formula, applied to basis vectors ----
def harness_mc(s):
    out = list(s)
    for c in range(4):
        a0,a1,a2,a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0^a1^a2^a3
        u = a0
        out[4*c]   = a0 ^ t ^ xtime(a0^a1)
        out[4*c+1] = a1 ^ t ^ xtime(a1^a2)
        out[4*c+2] = a2 ^ t ^ xtime(a2^a3)
        out[4*c+3] = a3 ^ t ^ xtime(a3^u)
    return out

def harness_imc(s):
    XT2 = {i: xtime(i) for i in range(256)}
    XT4 = {i: xtime(XT2[i]) for i in range(256)}
    XT8 = {i: xtime(XT4[i]) for i in range(256)}
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

def byte_linear_matrix(fn):
    M = [0]*N
    for ibit in range(N):
        s = [0]*16
        s[ibit//8] = 1 << (ibit % 8)
        o = fn(s)
        col = 0
        for byte in range(16):
            col |= o[byte] << (8*byte)
        for obit in range(N):
            if (col >> obit) & 1:
                M[obit] |= 1 << ibit
    return M

# ---- GF(2) dense ops, rows as ints ----
def mat_mul(A, B):  # A after B: (AB)[i] = XOR_{k in A[i]} B[k]
    out = [0]*N
    for i in range(N):
        row = A[i]
        v = 0
        r = row
        while r:
            lsb = r & (-r)
            k = lsb.bit_length()-1
            v ^= B[k]
            r ^= lsb
        out[i] = v
    return out

def transpose(M):
    T = [0]*N
    for i in range(N):
        row = M[i]
        r = row
        while r:
            lsb = r & (-r)
            j = lsb.bit_length()-1
            T[j] |= 1 << i
            r ^= lsb
    return T

def identity(): return [1 << i for i in range(N)]

def mat_inv(M):
    aug = [ (M[i], 1 << i) for i in range(N) ]
    for col in range(N):
        piv = None
        for r in range(col, N):
            if (aug[r][0] >> col) & 1: piv = r; break
        if piv is None: return None
        aug[col], aug[piv] = aug[piv], aug[col]
        for r in range(N):
            if r != col and (aug[r][0] >> col) & 1:
                aug[r] = (aug[r][0] ^ aug[col][0], aug[r][1] ^ aug[col][1])
    return [aug[i][1] for i in range(N)]

def rows_rank(rows):
    piv = {}
    for v in rows:
        x = v
        while x:
            hb = x.bit_length() - 1
            if hb in piv:
                x ^= piv[hb]
            else:
                piv[hb] = x
                break
    return len(piv)

# ---- word/geometry ----
PW = [[4*(((j+row)%4+4)%4)+row for row in range(4)] for j in range(4)]
CW = [[4*(((j-row)%4+4)%4)+row for row in range(4)] for j in range(4)]
GEOM_JSON_PW = [[0,5,10,15],[4,9,14,3],[8,13,2,7],[12,1,6,11]]
GEOM_JSON_CW = [[0,13,10,7],[4,1,14,11],[8,5,2,15],[12,9,6,3]]
assert PW == GEOM_JSON_PW, "PW formula vs geom.json mismatch"
assert CW == GEOM_JSON_CW, "CW formula vs geom.json mismatch"

def word_bits(j):
    bits = []
    for byte in PW[j]:
        bits += [8*byte + b for b in range(8)]
    return bits

def mask_keep_bytes(bytelist):
    m = 0
    for byte in bytelist:
        m |= 0xff << (8*byte)
    return m

def apply(M, v):
    # M stored row-wise (M[i] = output equation for bit i); image of v uses COLUMNS
    MT = transpose(M)
    out = 0
    r = v
    while r:
        lsb = r & (-r)
        k = lsb.bit_length()-1
        out ^= MT[k]
        r ^= lsb
    return out

def restrict_map(T, dom_bits, cod_bits):
    # columns = images of domain basis vectors, restricted to codomain bits
    # image of basis vector e_p is column p of T = row p of transpose(T)
    TC = transpose(T)
    cols = []
    cod_mask_set = {b: i for i, b in enumerate(cod_bits)}
    for p in dom_bits:
        v = TC[p]
        c = 0
        for b in cod_bits:
            if (v >> b) & 1:
                c |= 1 << cod_mask_set[b]
        cols.append(c)
    return cols

def rank_of_map(cols, codim):
    # row-rank of codim x len(cols) matrix given by columns
    rows = [0]*codim
    for k, c in enumerate(cols):
        r = c
        while r:
            lsb = r & (-r)
            i = lsb.bit_length()-1
            rows[i] |= 1 << k
            r ^= lsb
    return rows_rank(rows)

out = {"schema": "validator.census_rederivation.v1", "task_id": "TASK-20260901-d004bb"}

# ---- build and cross-check linear layers ----
SR_h = perm_matrix(sr_perm())
ISR_h = perm_matrix(isr_perm())
MC_h = byte_linear_matrix(harness_mc)
IMC_h = byte_linear_matrix(harness_imc)

# independent cross-check: FIPS-197 standard matrices
def std_col_matrix(col0):
    # circulant over columns: row r of col c gets col0[(r - 0)%4] * e_{...}
    M = [0]*N
    for c in range(4):
        for k in range(4):  # input row
            for r in range(4):  # output row
                coef = col0[(r - k) % 4]
                if coef == 0: continue
                for b in range(8):
                    # e_k * coef in GF(2^8): multiply basis vector 2^b by coef
                    prod = gmul(coef, 1 << b)
                    obyte = 4*c + r
                    ibyte = 4*c + k
                    for ob in range(8):
                        if (prod >> ob) & 1:
                            M[8*obyte + ob] |= 1 << (8*ibyte + b)
    return M

MC_std = std_col_matrix([2,1,1,3])    # first COLUMN of FIPS-197 MC (first row [2,3,1,1])
IMC_std = std_col_matrix([14,9,13,11])  # first COLUMN of FIPS-197 IMC (first row [14,11,13,9])
# composition self-test of mat_mul vs byte-level apply
import random as _rnd
_rng = _rnd.Random(20260901)
def _randvec():
    return _rng.getrandbits(N)
_comp_ok = True
for _ in range(200):
    v = _randvec()
    if apply(mat_mul(MC_h, SR_h), v) != apply(MC_h, apply(SR_h, v)):
        _comp_ok = False; break
    if apply(mat_mul(IMC_h, ISR_h), v) != apply(IMC_h, apply(ISR_h, v)):
        _comp_ok = False; break

out["cross_checks"] = {
    "mat_mul_composition_selftest": _comp_ok,
    "MC_harness_equals_FIPS197": MC_h == MC_std,
    "IMC_harness_equals_FIPS197": IMC_h == IMC_std,
    "SR_harness_is_perm": all(bin(row).count("1") == 1 for row in SR_h),
    "SR_ISR_inverse": mat_mul(SR_h, ISR_h) == identity() and mat_mul(ISR_h, SR_h) == identity(),
    "MC_IMC_inverse": mat_mul(MC_h, IMC_h) == identity() and mat_mul(IMC_h, MC_h) == identity(),
}
assert all(out["cross_checks"].values()), "FATAL: linear-layer construction cross-check failed"

SR, ISR, MC, IMC = SR_h, ISR_h, MC_h, IMC_h
I128 = identity()

def M_enc(r):
    # M_r = SR . (MC . SR)^{r-1}
    P = identity()
    MCS = mat_mul(MC, SR)
    for _ in range(r-1):
        P = mat_mul(MCS, P)
    return mat_mul(SR, P)

def M_dec(r):
    # D_r = (ISR . IMC)^{r-1} . ISR
    P = identity()
    ISRI = mat_mul(ISR, IMC)
    for _ in range(r-1):
        P = mat_mul(ISRI, P)
    return mat_mul(P, ISR)

inv_checks = {}
Ms, Ds = {}, {}
for r in range(1, 11):
    M = M_enc(r); D = M_dec(r)
    Ms[r], Ds[r] = M, D
    inv_checks[f"r{r}"] = (mat_mul(D, M) == I128, mat_mul(M, D) == I128)
out["D_r_times_M_r_is_I128_both_directions"] = inv_checks

def Z_matrices(S):
    keep_bytes = []
    for j in S:
        keep_bytes += CW[j]
    keep = mask_keep_bytes(keep_bytes)
    Zzero = [row & ~keep for row in I128]
    Zkeep = [row & keep for row in I128]
    # Z_zero + Z_keep = I
    assert all(Zzero[i] ^ Zkeep[i] == I128[i] for i in range(N))
    return Zzero, Zkeep

def record_object(r, S):
    Zzero, _ = Z_matrices(S)
    return mat_mul(mat_mul(Ds[r], Zzero), Ms[r])

def keep_object(r, S):
    _, Zkeep = Z_matrices(S)
    return mat_mul(mat_mul(Ds[r], Zkeep), Ms[r])

def cell_analysis(r, A, S):
    T = record_object(r, S)
    Tk = keep_object(r, S)
    dom = []
    for j in A:
        dom += word_bits(j)
    res = {"r": r, "A": A, "S": S, "domain_dim": len(dom)}
    for name, Top in (("T_zero_record", T), ("T_keep", Tk)):
        ranks = {}
        for j in range(4):
            cols = restrict_map(Top, dom, word_bits(j))
            ranks[str(j)] = rank_of_map(cols, 32)
        res[name + "_ranks"] = ranks
    # exact W-bin sizes for record object via Mobius over joint kernels
    # exact_ker_dims[sub] = dim of intersection of ker T_j for j in sub
    dom_dim = len(dom)
    ker_dim = {}
    for sub in range(16):
        if sub == 0:
            ker_dim[sub] = dom_dim
            continue
        rows = []
        for j in range(4):
            if (sub >> j) & 1:
                cols = restrict_map(T, dom, word_bits(j))
                for c in cols:
                    rows.append(c)
        rk = rows_rank(rows)
        ker_dim[sub] = dom_dim - rk
    # size of {d : W(d) = k} via Mobius: f(sub) = |{d vanishing on all j in sub}| = 2^{ker_dim[sub]}
    # g(exact set E) = sum_{sub >= E} (-1)^{|sub|-|E|} f(sub)
    exact_W = [0]*5
    for E in range(16):
        acc = 0
        sup = E
        while True:
            bits_sup = bin(sup).count("1"); bits_E = bin(E).count("1")
            acc += ((-1) ** (bits_sup - bits_E)) * (2 ** ker_dim[sup])
            if sup == 15: break
            sup = (sup + 1) | E
        exact_W[bin(E).count("1")] += acc
    res["record_T_exact_W_bins"] = {str(k): exact_W[k] for k in range(5)}
    total = 2 ** dom_dim
    wge1 = total - exact_W[0]
    res["record_T_P_Wge1_all_d"] = {"num": wge1, "den": total}
    res["record_T_mobius_consistent"] = (sum(exact_W) == total) and all(x >= 0 for x in exact_W)
    return res

# ---- anchor cell: full analysis incl. archived object ----
anchor = cell_analysis(5, [0], [0])
# archived object: P_j (D5 M5) P_0^T
DM = mat_mul(Ds[5], Ms[5])
arch_ranks = {}
for j in range(4):
    cols = restrict_map(DM, word_bits(0), word_bits(j))
    arch_ranks[str(j)] = rank_of_map(cols, 32)
anchor["archived_object_DM_ranks"] = arch_ranks
anchor["DM_is_I128"] = DM == I128
# swap-invariance of the pair XOR difference, COMPUTED on random pairs:
# swapping coordinates between c0 and c1 leaves c0^c1 unchanged pointwise.
_sw_ok = True
for _ in range(1000):
    c0 = _rng.getrandbits(N); c1 = _rng.getrandbits(N)
    d_before = c0 ^ c1
    keep = mask_keep_bytes(CW[0])
    c0s = (c0 & ~keep) | (c1 & keep)
    c1s = (c1 & ~keep) | (c0 & keep)
    if (c0s ^ c1s) != d_before:
        _sw_ok = False; break
anchor["swap_invariance_of_xor_difference_computed"] = _sw_ok
out["anchor_cell"] = anchor

# ---- one cell per round count (validator-chosen: A={0}, S={0} geometry) ----
per_round = {}
for r in range(1, 11):
    ca = cell_analysis(r, [0], [0])
    per_round[f"r{r}"] = {
        "T_zero_record_ranks": ca["T_zero_record_ranks"],
        "record_T_P_Wge1_all_d": ca["record_T_P_Wge1_all_d"],
    }
out["per_round_A0_S0"] = per_round

# ---- extra validator-chosen cells at r=5 ----
out["extra_cells_r5"] = {
    "A0_S1": cell_analysis(5, [0], [1]),
    "A01_S0": cell_analysis(5, [0,1], [0]),
    "A0123_S0": cell_analysis(5, [0,1,2,3], [0]),
}

out["required_by_F1"] = {"ranks": [32,0,0,0], "P_Wge1": 1.0}
rec = anchor["T_zero_record_ranks"]
out["verdict_anchor"] = {
    "record_object_ranks_recomputed": [rec["0"], rec["1"], rec["2"], rec["3"]],
    "archived_object_ranks_recomputed": [arch_ranks["0"], arch_ranks["1"], arch_ranks["2"], arch_ranks["3"]],
    "record_object_matches_F1_requirement": [rec["0"], rec["1"], rec["2"], rec["3"]] == [32,0,0,0] and anchor["record_T_P_Wge1_all_d"]["num"] == anchor["record_T_P_Wge1_all_d"]["den"],
    "archived_object_matches_F1_requirement": [arch_ranks["0"], arch_ranks["1"], arch_ranks["2"], arch_ranks["3"]] == [32,0,0,0],
}

with open(sys.argv[1], "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out["verdict_anchor"], indent=1))
print("per_round anchor-cell ranks:", [per_round["r5"]["T_zero_record_ranks"][str(j)] for j in range(4)])
print("OK")
