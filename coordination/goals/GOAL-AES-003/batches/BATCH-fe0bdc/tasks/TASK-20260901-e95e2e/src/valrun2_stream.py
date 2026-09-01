#!/usr/bin/env python3
"""TASK-20260901-e95e2e validator RUN 2 -- fresh byte-level stream replication.

Fresh Python implementation of the pinned instrument semantics, written from
the pinned convention statements (cipher convention block; FIPS-197 key
schedule; trial worker semantics) -- NOT from producer Python code.

Part A: exact replication of the CAL-DET arm stream (1 thread, 2^16, rounds 6,
        amask=smask=1, seed 46061601, arm_id 9) -> compare every counter with
        runs/cal_det_a.json; additionally count q0^q1 == p0^p1 per trial
        (identity-law check, expected 65536/65536).
Part B: 256 fresh keyed anchor trials (r=5, amask=smask=1) under a validator
        seed -> independent Gate-0-style keyed check.
Part C: KAT pins recomputed with fresh AES-128 (own S-box construction):
        FIPS-197 C.1 enc+dec r=10; BATCH-003 anchor key r=10 (full AES check
        of the internal constant) and r=5 (pinned 5-round convention);
        identity-table roundtrips r=1..10; fixture-arm key_hex and
        thread_seeds recomputed from (seed 46063001, arm_id 1, 8 threads).
"""
import json, sys

MASK64 = (1 << 64) - 1

def sm64_next(state):
    state = (state + 0x9E3779B97F4A7C15) & MASK64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return state, (z ^ (z >> 31)) & MASK64

class RNG:
    def __init__(self, seed):
        self.s = seed & MASK64
    def next(self):
        self.s, z = sm64_next(self.s)
        return z

# ---- GF(2^8), fresh
def mul_poly(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r

def gf256_inv(a):
    if a == 0:
        return 0
    # exponentiation: a^254 in GF(2^8) mod 0x11b
    r = 1
    e = 254
    base = a
    while e:
        if e & 1:
            r = gf256_mul(r, base)
        base = gf256_mul(base, base)
        e >>= 1
    return r

def gf256_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r

def build_aes_sbox():
    sbox = [0] * 256
    for i in range(256):
        x = gf256_inv(i)
        y = 0
        for bit in range(8):
            v = (((x >> bit) & 1) ^ ((x >> ((bit + 4) & 7)) & 1) ^
                 ((x >> ((bit + 5) & 7)) & 1) ^ ((x >> ((bit + 6) & 7)) & 1) ^
                 ((x >> ((bit + 7) & 7)) & 1) ^ ((0x63 >> bit) & 1))
            y |= v << bit
        sbox[i] = y
    return sbox

AES_SBOX = build_aes_sbox()
AES_INV = [0] * 256
for i in range(256):
    AES_INV[AES_SBOX[i]] = i
ID_SBOX = list(range(256))

# known external check of my fresh S-box construction: FIPS-197 sbox values
sbox_spot = {0x00: 0x63, 0x01: 0x7C, 0x10: 0xCA, 0x53: 0xED, 0xFF: 0x16, 0x63: 0xFB}

def xt(a):
    return gf256_mul(a, 2)

XT2 = [xt(i) for i in range(256)]
XT4 = [XT2[XT2[i]] for i in range(256)]
XT8 = [XT2[XT4[i]] for i in range(256)]

# ---- key schedule (FIPS-197 AES-128, SubWord via the CURRENT sbox)
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

def key_expand(key, sbox):
    rk = [list(key)]
    for i in range(1, 11):
        prev = rk[i - 1]
        t = list(prev[12:16])
        t = [sbox[t[1]], sbox[t[2]], sbox[t[3]], sbox[t[0]]]
        t[0] ^= RCON[i - 1]
        row = [0] * 16
        for w in range(4):
            for b in range(4):
                row[4 * w + b] = prev[4 * w + b] ^ (t[b] if w == 0 else row[4 * (w - 1) + b])
        rk.append(row)
    return rk

# ---- pinned round functions (expression-faithful)
def sub_shift(s, sbox):
    t = [0] * 16
    for c in range(4):
        for r in range(4):
            t[4 * c + r] = sbox[s[4 * ((c + r) & 3) + r]]
    return t

def inv_sub_shift(s, inv):
    t = [0] * 16
    for c in range(4):
        for r in range(4):
            t[4 * c + r] = inv[s[4 * ((c - r + 4) & 3) + r]]
    return t

def mix_columns(s):
    s = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0 ^ a1 ^ a2 ^ a3
        u = a0
        s[4*c]   = a0 ^ t ^ XT2[a0 ^ a1]
        s[4*c+1] = a1 ^ t ^ XT2[a1 ^ a2]
        s[4*c+2] = a2 ^ t ^ XT2[a2 ^ a3]
        s[4*c+3] = a3 ^ t ^ XT2[a3 ^ u]
    return s

def inv_mix_columns(s):
    s = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        w0, v0, u0 = XT8[a0], XT4[a0], XT2[a0]
        w1, v1, u1 = XT8[a1], XT4[a1], XT2[a1]
        w2, v2, u2 = XT8[a2], XT4[a2], XT2[a2]
        w3, v3, u3 = XT8[a3], XT4[a3], XT2[a3]
        s[4*c]   = w0^v0^u0 ^ w1^u1^a1 ^ w2^v2^a2 ^ w3^a3
        s[4*c+1] = w0^a0 ^ w1^v1^u1 ^ w2^u2^a2 ^ w3^v3^a3
        s[4*c+2] = w0^v0^a0 ^ w1^a1 ^ w2^v2^u2 ^ w3^u3^a3
        s[4*c+3] = w0^u0^a0 ^ w1^v1^a1 ^ w2^a2 ^ w3^v3^u3
    return s

def add_rk(s, rk):
    return [s[i] ^ rk[i] for i in range(16)]

def enc_r(inp, rk, r, sbox):
    st = add_rk(list(inp), rk[0])
    for i in range(1, r):
        st = add_rk(mix_columns(sub_shift(st, sbox)), rk[i])
    return add_rk(sub_shift(st, sbox), rk[r])

def dec_r(inp, rk, r, sbox, inv):
    st = inv_sub_shift(add_rk(list(inp), rk[r]), inv)
    for i in range(r - 1, 0, -1):
        st = inv_sub_shift(inv_mix_columns(add_rk(st, rk[i])), inv)
    return add_rk(st, rk[0])

PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

def worker_stream(rng, n, rounds, amask, smask, rk, sbox, inv, count_identity):
    trivial = 0
    wge1 = 0
    zhist = [0] * 17
    whist = [0] * 5
    wword = [0] * 4
    idlaw = 0
    for _ in range(n):
        a = rng.next()
        b = rng.next()
        p0 = list(a.to_bytes(8, 'little')) + list(b.to_bytes(8, 'little'))
        p1 = list(p0)
        ok = False
        while not ok:
            ok = True
            for j in range(4):
                if amask & (1 << j):
                    rnd = rng.next()
                    nz = False
                    for row in range(4):
                        nb = (rnd >> (8 * row)) & 0xFF
                        p1[PW[j][row]] = nb
                        if nb != p0[PW[j][row]]:
                            nz = True
                    if not nz:
                        ok = False
        c0 = enc_r(p0, rk, rounds, sbox)
        c1 = enc_r(p1, rk, rounds, sbox)
        trivial_flag = True
        for j in range(4):
            if smask & (1 << j):
                for row in range(4):
                    i = CW[j][row]
                    x, y = c0[i], c1[i]
                    if x != y:
                        trivial_flag = False
                    c0[i], c1[i] = y, x
        q0 = dec_r(c0, rk, rounds, sbox, inv)
        q1 = dec_r(c1, rk, rounds, sbox, inv)
        if count_identity:
            if all(q0[i] ^ q1[i] == p0[i] ^ p1[i] for i in range(16)):
                idlaw += 1
        Z = sum(1 for i in range(16) if q0[i] == q1[i])
        W = 0
        for j in range(4):
            zv = True
            for row in range(4):
                if q0[PW[j][row]] != q1[PW[j][row]]:
                    zv = False
                    break
            if zv:
                W += 1
                if not trivial_flag:
                    wword[j] += 1
        if trivial_flag:
            trivial += 1
            continue
        zhist[Z] += 1
        whist[W] += 1
        if W >= 1:
            wge1 += 1
    return dict(trivial=trivial, wge1=wge1, zhist=zhist, whist=whist,
                wword=wword, idlaw=idlaw)

def derive_key(seed, sbox):
    kst = (seed ^ 0xA5A5A5A5A5A5A5A5) & MASK64
    rng = RNG(kst)
    key = list(rng.next().to_bytes(8, 'little')) + list(rng.next().to_bytes(8, 'little'))
    return key

out = {}

# ---- Part C1: fresh AES sbox spot checks (external FIPS-197 constants)
out["aes_sbox_spot_checks"] = {("%02x" % k): (AES_SBOX[k] == v) for k, v in sbox_spot.items()}
out["aes_sbox_bijective"] = sorted(AES_SBOX) == list(range(256))

# ---- Part C2: FIPS-197 C.1 KAT with fresh full AES (my enc_r/dec_r, r=10)
kat_key = bytes(range(16))
kat_pt = bytes.fromhex("00112233445566778899aabbccddeeff")
kat_ct_expected = "69c4e0d86a7b0430d8cdb78070b4c55a"
rk_kat = key_expand(kat_key, AES_SBOX)
ct = bytes(enc_r(list(kat_pt), rk_kat, 10, AES_SBOX))
out["fips197_c1_kat"] = {
    "computed": ct.hex(),
    "expected": kat_ct_expected,
    "enc_match": ct.hex() == kat_ct_expected,
}
pt_back = bytes(dec_r(list(ct), rk_kat, 10, AES_SBOX, AES_INV))
out["fips197_c1_kat"]["dec_match"] = pt_back == kat_pt

# ---- Part C3: BATCH-003 anchor key, r=10 (full-AES check of internal constant) and r=5 (pinned convention)
anchor_key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
rk_a = key_expand(anchor_key, AES_SBOX)
ct10 = bytes(enc_r(list(kat_pt), rk_a, 10, AES_SBOX))
out["anchor_r10"] = {
    "computed": ct10.hex(),
    "pinned_value": "8df4e9aac5c7573a27d8d055d6e4d64b",
    "match": ct10.hex() == "8df4e9aac5c7573a27d8d055d6e4d64b",
}
ct5 = bytes(enc_r(list(kat_pt), rk_a, 5, AES_SBOX))
out["anchor_r5"] = {
    "computed": ct5.hex(),
    "pinned_value": "4167e8f8367c38cdb7bde2ade620a7a8",
    "match": ct5.hex() == "4167e8f8367c38cdb7bde2ade620a7a8",
    "decrypts_back": bytes(dec_r(list(ct5), rk_a, 5, AES_SBOX, AES_INV)) == kat_pt,
}

# identity-table roundtrips r=1..10 (fresh)
rt_fails = 0
rng = RNG(0xE95E2E)
for v in range(64):
    key = bytes([rng.next() & 0xFF for _ in range(16)])
    ptv = bytes([rng.next() & 0xFF for _ in range(16)])
    rk_i = key_expand(key, ID_SBOX)
    for r in range(1, 11):
        c = enc_r(list(ptv), rk_i, r, ID_SBOX)
        e = bytes(dec_r(c, rk_i, r, ID_SBOX, ID_SBOX))
        if e != ptv:
            rt_fails += 1
out["identity_roundtrips"] = {"vectors": 64, "rounds_each": "1..10", "failures": rt_fails}

# ---- Part A: exact CAL-DET replication (producer receipt parameters)
seedA, armidA, threadsA, log2N_A, roundsA, amaskA, smaskA = 46061601, 9, 1, 16, 6, 1, 1
NA = 1 << log2N_A
keyA = derive_key(seedA, ID_SBOX)
rkA = key_expand(keyA, ID_SBOX)
tseedA = (seedA ^ ((armidA * 0x1234567891) & MASK64) ^ ((1 * 0x9E3779B97F4A7C15) & MASK64)) & MASK64
resA = worker_stream(RNG(tseedA), NA, roundsA, amaskA, smaskA, rkA, ID_SBOX, ID_SBOX, True)
cal = json.load(open(sys.argv[1]))
partA = {
    "key_hex_recomputed": bytes(keyA).hex(),
    "key_hex_receipt": cal["key_hex"],
    "key_match": bytes(keyA).hex() == cal["key_hex"],
    "thread_seed_recomputed": tseedA,
    "thread_seed_receipt": cal["thread_seeds"][0],
    "thread_seed_match": tseedA == cal["thread_seeds"][0],
    "trivial_recomputed": resA["trivial"], "trivial_receipt": cal["trivial_swaps_excluded"],
    "nontrivial_recomputed": NA - resA["trivial"], "nontrivial_receipt": cal["nontrivial_trials"],
    "wge1_recomputed": resA["wge1"], "wge1_receipt": cal["W_ge1_nontrivial"],
    "wword_recomputed": resA["wword"], "wword_receipt": cal["W_ge1_by_word"],
    "whist_recomputed": resA["whist"], "whist_receipt": cal["whist"],
    "zhist_recomputed": resA["zhist"], "zhist_receipt": cal["zhist"],
    "identity_law_qdiff_eq_pdiff": resA["idlaw"],
    "identity_law_expected": NA,
    "all_fields_match": (bytes(keyA).hex() == cal["key_hex"] and tseedA == cal["thread_seeds"][0]
        and resA["trivial"] == cal["trivial_swaps_excluded"]
        and NA - resA["trivial"] == cal["nontrivial_trials"]
        and resA["wge1"] == cal["W_ge1_nontrivial"]
        and resA["wword"] == cal["W_ge1_by_word"]
        and resA["whist"] == cal["whist"]
        and resA["zhist"] == cal["zhist"]),
}
out["partA_cal_det_replication"] = partA

# ---- Part B: validator-seed fresh keyed anchor trials (r=5, A={0}, S={0})
seedB = 0xE95E2E5E2E & MASK64
keyB = derive_key(seedB, ID_SBOX)
rkB = key_expand(keyB, ID_SBOX)
tseedB = (seedB ^ ((7 * 0x1234567891) & MASK64) ^ ((1 * 0x9E3779B97F4A7C15) & MASK64)) & MASK64
resB = worker_stream(RNG(tseedB), 256, 5, 1, 1, rkB, ID_SBOX, ID_SBOX, True)
out["partB_validator_anchor_trials"] = {
    "r": 5, "A": [0], "S": [0], "trials": 256, "validator_seed": seedB,
    "key_hex": bytes(keyB).hex(),
    "qdiff_eq_pdiff": resB["idlaw"], "qdiff_eq_pdiff_expected": 256,
    "trivial": resB["trivial"],
    "whist": resB["whist"],
    "W3_on_all_nontrivial": resB["whist"][3] == 256 - resB["trivial"],
    "pass": resB["idlaw"] == 256 and resB["whist"][3] == 256 - resB["trivial"] and sum(resB["whist"]) == 256 - resB["trivial"],
}

# ---- fixture arm key and thread seeds recomputed from declared parameters
seedF, armidF, threadsF = 46063001, 1, 8
keyF = derive_key(seedF, ID_SBOX)
out["fixture_arm_params_recomputed"] = {
    "key_hex_recomputed": bytes(keyF).hex(),
    "thread_seeds_recomputed": [
        (seedF ^ ((armidF * 0x1234567891) & MASK64) ^ (((t + 1) * 0x9E3779B97F4A7C15) & MASK64)) & MASK64
        for t in range(threadsF)],
}

json.dump(out, sys.stdout, indent=1)
print()
