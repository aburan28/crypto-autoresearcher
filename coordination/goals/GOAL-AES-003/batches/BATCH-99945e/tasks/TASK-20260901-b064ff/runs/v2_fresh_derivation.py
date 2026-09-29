#!/usr/bin/env python3
# VALIDATOR RUN 2 (TASK-20260901-b064ff): FRESH re-derivation, zero producer code.
# Part A: sparse GF(2) census r=1..16 over the frozen 10-cell set, built from the
#         pinned definitions in ledger/proposals/IDEA-20260901-04606c.yaml
#         (M_r = SR.(MC.SR)^{r-1}, D_r = (ISR.IMC)^{r-1}.ISR, object
#         A_{r,S,j} = P_j (D_r M_r) Pi_A, rho = rank(d|PW[A] -> (M_r d)|CW[S])).
# Part B: from-scratch AES (FIPS-197) KATs incl. recomputed r5/r10 anchors.
# Part C: fresh keyed-law smoke trials (single-thread python, fresh seeds).
import json, random

MASK128 = (1 << 128) - 1

# ---------- GF(2) 128x128 matrices as lists of 128 row-ints ----------
def mat_mul(A, B):
    # C = A @ B ; rows of C = XOR of rows of B selected by bits of rows of A
    C = []
    for r in A:
        row = 0
        x = r
        while x:
            lb = x & (-x)
            i = lb.bit_length() - 1
            row ^= B[i]
            x ^= lb
        C.append(row)
    return C

def mat_vec_rows(A, v):
    # returns A*v with A rows: bit j of result = popcount(A[j] & v) % 2
    out = 0
    for j in range(128):
        if bin(A[j] & v).count("1") & 1:
            out |= 1 << j
    return out

def identity():
    return [1 << i for i in range(128)]

def mat_inv(M):
    # Gauss-Jordan over GF(2); returns inverse or None
    n = 128
    aug = [M[i] | (((1 << i)) << n) for i in range(n)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if (aug[r] >> col) & 1:
                piv = r
                break
        if piv is None:
            return None
        aug[col], aug[piv] = aug[piv], aug[col]
        for r in range(n):
            if r != col and (aug[r] >> col) & 1:
                aug[r] ^= aug[col]
    return [(aug[i] >> n) & ((1 << n) - 1) for i in range(n)]

def rank_of(cols):
    # cols: list of ints (column vectors); GF(2) rank via elimination
    basis = []
    for c in cols:
        v = c
        for b in basis:
            if v and (v ^ b) < v:
                v ^= b
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)

def rank_rows(rows):
    basis = []
    for v0 in rows:
        v = v0
        for b in basis:
            if (v ^ b) < v:
                v ^= b
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)

# ---------- FIPS-197 geometry (derived from scratch) ----------
# state byte index = 4*col + row (column-major, pinned state_layout)
def sr_perm():
    # FIPS-197 ShiftRows: out[r][c] = in[r][(c+r)%4] (row r shifted LEFT by r)
    rows = [0] * 128
    for c in range(4):
        for r in range(4):
            new = 4 * c + r
            old = 4 * ((c + r) % 4) + r
            for b in range(8):
                rows[8 * new + b] = 1 << (8 * old + b)
    return rows

def xtime_byte(a):
    a &= 0xFF
    hi = a & 0x80
    a = (a << 1) & 0xFF
    if hi:
        a ^= 0x1B
    return a

def mc_perm():
    # MixColumns per column: out row0 = 2*b0 ^ 3*b1 ^ b2 ^ b3 etc (FIPS-197 matrix)
    mat = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]
    rows = [0] * 128
    for c in range(4):
        for r in range(4):
            acc = [0] * 8  # output byte bits as xor of input bits
            for k in range(4):  # input row k of this column
                coef = mat[r][k]
                inbyte = 4 * c + k
                # contribution of each input bit to output byte = coef * x^bit in GF(2^8)
                vals = []
                v = coef
                for bit in range(8):
                    vals.append(v)
                    v = xtime_byte(v)
                for bit in range(8):
                    vv = vals[bit]
                    for ob in range(8):
                        if (vv >> ob) & 1:
                            rows[8 * (4 * c + r) + ob] |= 1 << (8 * inbyte + bit)
    return rows

SR = sr_perm()
MC = mc_perm()
ISR = mat_inv(SR)
IMC = mat_inv(MC)
I128 = identity()
assert ISR is not None and IMC is not None
assert mat_mul(SR, ISR) == I128 and mat_mul(MC, IMC) == I128

# probe word geometry, derived: PW[j] = {4c + (c-j)%4}, CW[j] = {4c + (j-c)%4}
PW = [sorted(4 * c + ((c - j) % 4) for c in range(4)) for j in range(4)]
CW = [sorted(4 * c + ((j - c) % 4) for c in range(4)) for j in range(4)]
RECORDED_PW = [[0, 5, 10, 15], [4, 9, 14, 3], [8, 13, 2, 7], [12, 1, 6, 11]]
RECORDED_CW = [[0, 13, 10, 7], [4, 1, 14, 11], [8, 5, 2, 15], [12, 9, 6, 3]]
geom_ok = all(set(PW[j]) == set(RECORDED_PW[j]) for j in range(4)) and \
          all(set(CW[j]) == set(RECORDED_CW[j]) for j in range(4))

def pw_bits(ws):
    # bits of the PW bytes for word indices ws
    return [8 * b + k for j in ws for b in PW[j] for k in range(8)]

def cw_bits(ws):
    # bits of the CW bytes for word indices ws
    return [8 * b + k for j in ws for b in CW[j] for k in range(8)]

# frozen 10-cell set (verbatim from record P2)
CELLS = [
    ("C1", [0], [0]), ("C2", [0], [1]), ("C3", [0], [2]), ("C4", [0], [3]),
    ("C5", [1], [1]), ("C6", [2], [2]), ("C7", [3], [3]),
    ("C8", [0, 1], [0]), ("C9", [0], [0, 1]), ("C10", [0, 1, 2, 3], [0]),
]

# M_r = SR.(MC.SR)^{r-1}, D_r = (ISR.IMC)^{r-1}.ISR
def mat_pow(A, k):
    R = identity()
    for _ in range(k):
        R = mat_mul(A, R)
    return R

def build_M(r):
    # M_r = SR . (MC.SR)^{r-1}  (apply (MC.SR) r-1 times, then SR)
    return mat_mul(SR, mat_pow(mat_mul(MC, SR), r - 1))

def build_D(r):
    # D_r = (ISR.IMC)^{r-1} . ISR  (apply ISR, then (ISR.IMC) r-1 times)
    return mat_mul(mat_pow(mat_mul(ISR, IMC), r - 1), ISR)

def col_of(M, bit):
    return sum(((M[j] >> bit) & 1) << j for j in range(128))

PR1 = {  # preregistered rho table, IDEA-20260901-04606c PR-1 verbatim
    "C1": [8, 32, 8, 32, 32, 32, 32, 32, 8, 32],
    "C2": [8, 0, 8, 32, 32, 32, 32, 32, 8, 0],
    "C3": [8, 0, 8, 32, 32, 32, 32, 32, 8, 0],
    "C4": [8, 0, 8, 32, 32, 32, 32, 32, 8, 0],
    "C5": [8, 32, 8, 32, 32, 32, 32, 32, 8, 32],
    "C6": [8, 32, 8, 32, 32, 32, 32, 32, 8, 32],
    "C7": [8, 32, 8, 32, 32, 32, 32, 32, 8, 32],
    "C8": [16, 32, 16, 32, 32, 32, 32, 32, 16, 32],
    "C9": [16, 32, 16, 32, 32, 32, 32, 32, 16, 32],
    "C10": [32, 32, 32, 32, 32, 32, 32, 32, 32, 32],
}

out = {"checks": [], "census": {}}
fails = []

def check(name, cond, detail=""):
    out["checks"].append({"name": name, "ok": bool(cond), "detail": detail})
    if not cond:
        fails.append(name)

check("A.geometry_PW_CW_derived==recorded_convention_block", geom_ok, f"PW={PW} CW={CW}")

# ---------- Part A: census r=1..16 ----------
guards, rho_all, rank_all = {}, {}, {}
for r in range(1, 17):
    M = build_M(r)
    D = build_D(r)
    DM = mat_mul(D, M)
    MD = mat_mul(M, D)
    guards[r] = (DM == I128, MD == I128)
    for cid, A, S in CELLS:
        abits = pw_bits(A)
        sbits = cw_bits(S)
        # rho = rank of columns {M e_i restricted to CW[S] rows} for i in PW[A] bits
        cols = []
        for i in abits:
            v = col_of(M, i)
            cols.append(sum(((v >> j) & 1) << sbits.index(j) for j in sbits if (v >> j) & 1))
        rho = rank_of(cols)
        rho_all.setdefault(cid, {})[r] = rho
        # word-map ranks of A_{r,S,j} = P_j (DM) Pi_A
        rk = []
        for j in range(4):
            jbits = pw_bits([j])
            cols2 = []
            for i in abits:
                v = mat_vec_rows(DM, 1 << i)
                cols2.append(sum(((v >> j2) & 1) << abits.index(i) for j2 in jbits if (v >> j2) & 1))
            rk.append(rank_of(cols2))
        rank_all.setdefault(cid, {})[r] = rk
check("A.guards_DrMr_MrDr_I128_all_r1_16", all(a and b for a, b in guards.values()),
      str({r: (a, b) for r, (a, b) in guards.items() if not (a and b)}))
flat_ok = True
for cid, A, S in CELLS:
    want = [32 if j in A else 0 for j in range(4)]
    for r in range(1, 17):
        if rank_all[cid][r] != want:
            flat_ok = False
check("A.word_map_ranks_flat_32xinA_all_160", flat_ok)
mm_pr1 = {cid: {r: rho_all[cid][r] for r in range(1, 11) if rho_all[cid][r] != PR1[cid][r - 1]} for cid in PR1}
mm_pr1 = {k: v for k, v in mm_pr1.items() if v}
check("A.rho_r1_10==PR1_preregistered_table", len(mm_pr1) == 0, str(mm_pr1))
out["census"]["rho_fresh"] = {cid: [rho_all[cid][r] for r in range(1, 17)] for cid, _, _ in CELLS}
out["census"]["rho_r11_16_fresh"] = {cid: [rho_all[cid][r] for r in range(11, 17)] for cid, _, _ in CELLS}
out["census"]["ranks_sample_C1_r16"] = rank_all["C1"][16]
out["census"]["ranks_sample_C10_r16"] = rank_all["C10"][16]

# ---------- Part B: from-scratch AES KATs ----------
def gf8_inv(a):
    if a == 0:
        return 0
    r, p = 1, a
    for _ in range(6):
        p = xtime_byte(p)
        r ^= p if _ in (0, 1, 3, 5) else 0  # a^254 = a^(2+4+16+64+128)
    return r

def gf8_inv2(a):
    if a == 0:
        return 0
    x = a
    for _ in range(6):
        x = xtime_byte(x)
    # a^2^7? safer: brute a*b==1
    for b in range(1, 256):
        # multiply a*b in GF(2^8)
        acc, aa, bb = 0, a, b
        while bb:
            if bb & 1:
                acc ^= aa
            aa = xtime_byte(aa)
            bb >>= 1
        if acc == 1:
            return b
    return None

SBOX = [0] * 256
for a in range(256):
    inv = gf8_inv2(a)
    s = 0
    for i in range(8):
        bit = ((inv >> i) & 1) ^ ((inv >> ((i + 4) % 8)) & 1) ^ ((inv >> ((i + 5) % 8)) & 1) ^ \
              ((inv >> ((i + 6) % 8)) & 1) ^ ((inv >> ((i + 7) % 8)) & 1) ^ ((0x63 >> i) & 1)
        s |= bit << i
    SBOX[a] = s
ISBOX = [0] * 256
for a in range(256):
    ISBOX[SBOX[a]] = a

def hex_to_state(h):
    b = bytes.fromhex(h)
    return list(b)  # byte i = state byte i (column-major input per FIPS-197)

def state_hex(s):
    return bytes(s).hex()

def sub_bytes(s, box):
    return [box[x] for x in s]

def shift_rows(s):
    # out[r][c] = in[r][(c+r)%4]
    t = [0] * 16
    for c in range(4):
        for r in range(4):
            t[4 * c + r] = s[4 * ((c + r) % 4) + r]
    return t

def inv_shift_rows(s):
    t = [0] * 16
    for c in range(4):
        for r in range(4):
            t[4 * c + r] = s[4 * ((c - r) % 4) + r]
    return t

def mix_cols(s):
    t = [0] * 16
    m = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]
    for c in range(4):
        b = [s[4 * c + r] for r in range(4)]
        for r in range(4):
            acc = 0
            for k in range(4):
                v = b[k]
                coef = m[r][k]
                aa, bb, p2 = v, coef, 0
                while bb:
                    if bb & 1:
                        p2 ^= aa
                    aa = xtime_byte(aa)
                    bb >>= 1
                acc ^= p2
            t[4 * c + r] = acc
    return t

def inv_mix_cols(s):
    m = [[14, 11, 13, 9], [9, 14, 11, 13], [13, 9, 14, 11], [11, 13, 9, 14]]
    t = [0] * 16
    for c in range(4):
        b = [s[4 * c + r] for r in range(4)]
        for r in range(4):
            acc = 0
            for k in range(4):
                aa, bb, p2 = b[k], m[r][k], 0
                while bb:
                    if bb & 1:
                        p2 ^= aa
                    aa = xtime_byte(aa)
                    bb >>= 1
                acc ^= p2
            t[4 * c + r] = acc
    return t

def key_schedule(key, nr):
    w = [key[4 * i:4 * i + 4] for i in range(4)]
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
    while len(rcon) < nr:
        rcon.append(xtime_byte(rcon[-1]))
    for i in range(4, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % 4 == 0:
            t = t[1:] + t[:1]
            t = [SBOX[x] for x in t]
            t[0] ^= rcon[i // 4 - 1]
        w.append([w[i - 4][k] ^ t[k] for k in range(4)])
    return w, rcon[:nr]

def encrypt(state, key, nr):
    w, _ = key_schedule(key, nr)
    s = [state[i] ^ w[i // 4][i % 4] for i in range(16)]
    for rnd in range(1, nr):
        s = sub_bytes(s, SBOX)
        s = shift_rows(s)
        s = mix_cols(s)
        s = [s[i] ^ w[4 * rnd + i // 4][i % 4] for i in range(16)]
    s = sub_bytes(s, SBOX)
    s = shift_rows(s)
    s = [s[i] ^ w[4 * nr + i // 4][i % 4] for i in range(16)]
    return s

def decrypt(state, key, nr):
    w, _ = key_schedule(key, nr)
    s = [state[i] ^ w[4 * nr + i // 4][i % 4] for i in range(16)]
    s = inv_shift_rows(s)
    s = sub_bytes(s, ISBOX)
    for rnd in range(nr - 1, 0, -1):
        s = [s[i] ^ w[4 * rnd + i // 4][i % 4] for i in range(16)]
        s = inv_mix_cols(s)
        s = inv_shift_rows(s)
        s = sub_bytes(s, ISBOX)
    s = [s[i] ^ w[i // 4][i % 4] for i in range(16)]
    return s

# FIPS-197 Appendix C.1 KAT (key 000102...0f; provenance: recalled spec constant,
# verified computationally here) with AES S-box
C1_KEY = hex_to_state("000102030405060708090a0b0c0d0e0f")
C1_PT = hex_to_state("00112233445566778899aabbccddeeff")
ct10 = state_hex(encrypt(C1_PT, C1_KEY, 10))
check("B.FIPS197_C1_KAT_r10_fresh", ct10 == "69c4e0d86a7b0430d8cdb78070b4c55a", ct10)
rt = state_hex(decrypt(hex_to_state(ct10), C1_KEY, 10))
check("B.decrypt_roundtrip_r10", rt == "00112233445566778899aabbccddeeff", rt)
# BATCH-003 anchors recomputed fresh: key 2b7e.../pt 0011... (as in the receipt)
ANK_KEY = hex_to_state("2b7e151628aed2a6abf7158809cf4f3c")
ct5 = state_hex(encrypt(C1_PT, ANK_KEY, 5))
check("B.r5_anchor_recomputed==receipt_pin", ct5 == "4167e8f8367c38cdb7bde2ade620a7a8", ct5)
ct10b = state_hex(encrypt(C1_PT, ANK_KEY, 10))
check("B.r10_anchor_recomputed==receipt_pin", ct10b == "8df4e9aac5c7573a27d8d055d6e4d64b", ct10b)
# rcon continuation verification
_, rcons = key_schedule(C1_KEY, 16)
check("B.rcon_11_16==6c,d8,ab,4d,9a,2f", [hex(x)[2:].rjust(2, "0") for x in rcons[10:16]] == ["6c", "d8", "ab", "4d", "9a", "2f"],
      str([hex(x) for x in rcons[10:16]]))
# identity-sbox roundtrip r=1..16 (the affine cipher used by the arms)
id_ok = True
rng = random.Random(90112)  # validator-chosen fresh seed
for nr in range(1, 17):
    key = [rng.randrange(256) for _ in range(16)]
    pt = [rng.randrange(256) for _ in range(16)]
    # affine cipher = same structure with SBOX=id
    def enc_id(state, key, nr):
        w, _ = key_schedule(key, nr)
        s = [state[i] ^ w[i // 4][i % 4] for i in range(16)]
        for rnd in range(1, nr):
            s = shift_rows(s)
            s = mix_cols(s)
            s = [s[i] ^ w[4 * rnd + i // 4][i % 4] for i in range(16)]
        s = shift_rows(s)
        s = [s[i] ^ w[4 * nr + i // 4][i % 4] for i in range(16)]
        return s
    def dec_id(state, key, nr):
        w, _ = key_schedule(key, nr)
        s = [state[i] ^ w[4 * nr + i // 4][i % 4] for i in range(16)]
        s = inv_shift_rows(s)
        for rnd in range(nr - 1, 0, -1):
            s = [s[i] ^ w[4 * rnd + i // 4][i % 4] for i in range(16)]
            s = inv_mix_cols(s)
            s = inv_shift_rows(s)
        s = [s[i] ^ w[i // 4][i % 4] for i in range(16)]
        return s
    if dec_id(enc_id(pt, key, nr), key, nr) != pt:
        id_ok = False
check("B.identity_sbox_roundtrip_r1_16", id_ok)

# linear-part extraction check: M_r from basis-vector simulation of enc_id must equal census M_r
sim_ok = True
for nr in (6, 16):
    key = [0] * 16
    base = encrypt  # not used; simulate enc_id with zero key on basis vectors
    def enc_id0(v_int, nr):
        st = [(v_int >> (8 * i)) & 0xFF for i in range(16)]
        out = enc_id(st, [0] * 16, nr)
        return sum(out[i] << (8 * i) for i in range(16))
    zc = enc_id0(0, nr)  # cipher is affine (zero-key schedule nonzero); remove constant
    Msim = [0] * 128
    for bit in range(128):
        Msim[bit] = enc_id0(1 << bit, nr) ^ zc
    Mrows = [0] * 128
    for j in range(128):
        for i in range(128):
            if (Msim[i] >> j) & 1:
                Mrows[j] |= 1 << i
    if Mrows != build_M(nr):
        sim_ok = False
check("B.M_r_basis_simulation==census_matrix_r6_r16", sim_ok)

# ---------- Part C: fresh keyed-law smoke (1 thread, fresh seeds) ----------
def trial(rng, nr, A, S, idlaw=True):
    key = [rng.randrange(256) for _ in range(16)]
    p0 = [rng.randrange(256) for _ in range(16)]
    d = {}
    for j in A:
        wd = 0
        while wd == 0:
            wd = rng.randrange(1, 1 << 32)
        d[j] = wd
    p1 = list(p0)
    for j, wd in d.items():
        for b in PW[j]:
            p1[b] ^= (wd >> (8 * PW[j].index(b))) & 0xFF
    c0 = enc_id(p0, key, nr)
    c1 = enc_id(p1, key, nr)
    # swap ciphertext bytes of CW[S] between c0 and c1
    c0s, c1s = list(c0), list(c1)
    for j in S:
        for b in CW[j]:
            c0s[b], c1s[b] = c1[b], c0[b]
    q0 = dec_id(c0s, key, nr)
    q1 = dec_id(c1s, key, nr)
    qd = [q0[i] ^ q1[i] for i in range(16)]
    pd = [p0[i] ^ p1[i] for i in range(16)]
    law = qd == pd
    W = sum(1 for j in range(4) if all(pd2 == 0 for pd2 in (qd[PW[j][k]] for k in range(4))))
    # a swap is trivial iff the swapped bytes of c0 and c1 are already equal
    trivial = all(c0[b] == c1[b] for j in S for b in CW[j])
    return law, W, trivial

smoke = {}
rng = random.Random(46099)  # validator-chosen, distinct from all producer seeds
for nr, A, S, n in [(3, [0], [0], 600), (6, [0], [0], 600), (7, [0], [0], 600), (16, [0], [0], 600),
                    (2, [0], [1], 200), (6, [0, 1, 2, 3], [0], 200)]:
    laws = trivs = 0
    ws = []
    for _ in range(n):
        l, W, t = trial(rng, nr, A, S)
        laws += l
        trivs += t
        ws.append(W)
    tag = f"r{nr}_A{'-'.join(map(str,A))}_S{'-'.join(map(str,S))}"
    smoke[tag] = {"n": n, "identity_law": laws, "trivial": trivs,
                  "whist": [ws.count(k) for k in range(5)]}
check("C.identity_law_100pct_r3_r6_r7_r16", all(smoke[f"r{r}_A0_S0"]["identity_law"] == 600 for r in (3, 6, 7, 16)),
      str({k: v["identity_law"] for k, v in smoke.items()}))
check("C.W_eq_3_all_trials_r3_r6_r7_r16", all(smoke[f"r{r}_A0_S0"]["whist"] == [0, 0, 0, 600, 0] for r in (3, 6, 7, 16)),
      str({k: v["whist"] for k, v in smoke.items()}))
check("C.degenerate_r2_A0_S1_all_trivial(rho=0)", smoke["r2_A0_S1"]["trivial"] == 200 and smoke["r2_A0_S1"]["identity_law"] == 200,
      str(smoke["r2_A0_S1"]))
check("C.structure_destroyed_W0_all", smoke["r6_A0-1-2-3_S0"]["whist"][0] == 200 and smoke["r6_A0-1-2-3_S0"]["identity_law"] == 200,
      str(smoke["r6_A0-1-2-3_S0"]))
# trivial counts vs rho predictions: r=6 rho=32 -> E[T]~600*2^-32~0; r=3 rho=8 -> E[T]~2.34
check("C.trivial_r6_zero(consistent rho=32)", smoke["r6_A0_S0"]["trivial"] == 0, str(smoke["r6_A0_S0"]))
check("C.trivial_r3_in_band(rho=8)", 0 <= smoke["r3_A0_S0"]["trivial"] <= 12, f"T={smoke['r3_A0_S0']['trivial']} E~2.34")
out["smoke"] = smoke
out["fails"] = fails
out["n_checks"] = len(out["checks"])

with open("coordination/goals/GOAL-AES-003/batches/BATCH-99945e/tasks/TASK-20260901-b064ff/runs/v2_fresh_derivation.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"n_checks": out["n_checks"], "fails": fails,
                  "rho_r11_16_fresh": out["census"]["rho_r11_16_fresh"]}, indent=1))
