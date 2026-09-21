#!/usr/bin/env python3
# gate0.py -- TASK-20260901-f5d3a4 RUN 1 (GATE 0, BLOCKING per record PR-0/F1).
#
# Fresh-code anchor reproduction for IDEA-20260901-04606c:
#   (a) D_5 M_5 = I_128 and M_5 D_5 = I_128 via byte-level basis-vector
#       simulation of the pinned round functions (independent of the census
#       matrix-product code in census046.py by construction);
#   (b) ranks of A_{5,{0},j} = P_j (D_5 M_5) P_0^T exactly (32,0,0,0), with the
#       word maps checked COLUMN-EQUAL to the 32-bit identity (j=0) and zero
#       maps (j=1,2,3) -- stronger than rank equality;
#   (c) exact P(W>=1 | nontrivial) = 1.0 derived from the word maps (word-0
#       identity never vanishes on the conditioned-nonzero input; words 1..3
#       vanish identically);
#   (d) 1000 fresh keyed trials: q0^q1 = p0^p1 on 1000/1000 and W = 3 on 100%
#       of nontrivial trials.
#
# Any failure: exit 5 -> task HALTS as invalid_measurement (F1), never
# negative evidence (rule 5). This is the exact gate that voided the
# predecessor object.
#
# CONVENTION (pinned, BATCH-002 / FIPS-197-shaped toy SPN):
#   E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0, SB=id
#   state column-major: byte index = 4*col + row
#   PW[j][row] = 4*((j+row)%4)+row ; CW[j][row] = 4*((j-row)%4)+row
#   key schedule = FIPS-197 expansion with SubWord = identity rotation.
import json, sys, random, datetime

def xt(a): return ((a << 1) ^ ((a >> 7) * 0x1b)) & 0xFF
XT2 = [xt(i) for i in range(256)]
XT4 = [xt(XT2[i]) for i in range(256)]
XT8 = [xt(XT4[i]) for i in range(256)]

def sub_shift(s):      # SB=id then SR
    return [s[4 * ((c + r) & 3) + r] for c in range(4) for r in range(4)]

def inv_sub_shift(s):  # ISR then ISB=id
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

def enc_linear(st, rounds):
    for _ in range(1, rounds):
        st = mix_columns(sub_shift(st))
    return sub_shift(st)

def dec_linear(st, rounds):
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

wmaps = {j: [] for j in range(4)}
for k in range(32):
    v = apply_cols(D, apply_cols(M, embed_word(1 << k, 0)))
    for j in range(4):
        wmaps[j].append(project_word(v, j))

ranks = {j: gf2_rank(wmaps[j]) for j in range(4)}
id_cols = [1 << k for k in range(32)]
map0_is_identity = wmaps[0] == id_cols
maps123_are_zero = all(all(c == 0 for c in wmaps[j]) for j in (1, 2, 3))

P_exact = 1.0 if (map0_is_identity and maps123_are_zero) else None

rng = random.Random("2026090104606c")
stat = {"trials": 0, "nontrivial": 0, "trivial_swaps": 0,
        "qdiff_equals_pdiff": 0, "W_is_3_nontrivial": 0,
        "W_is_3_all_trials": 0, "whist": [0]*5}
for _ in range(1000):
    key = [rng.randrange(256) for _ in range(16)]
    rk = key_expand_identity(key)
    p0 = [rng.randrange(256) for _ in range(16)]
    p1 = list(p0)
    while True:
        nz = False
        for row in range(4):
            nb = rng.randrange(256)
            p1[PW[0][row]] = nb
            if nb != p0[PW[0][row]]: nz = True
        if nz: break
    c0 = enc_rk(p0, rk, ROUNDS); c1 = enc_rk(p1, rk, ROUNDS)
    trivial = True
    for i in CW[0]:
        if c0[i] != c1[i]: trivial = False
        c0[i], c1[i] = c1[i], c0[i]
    q0 = dec_rk(c0, rk, ROUNDS); q1 = dec_rk(c1, rk, ROUNDS)
    stat["trials"] += 1
    if trivial: stat["trivial_swaps"] += 1
    else: stat["nontrivial"] += 1
    pdiff = [p0[i] ^ p1[i] for i in range(16)]
    qdiff = [q0[i] ^ q1[i] for i in range(16)]
    if qdiff == pdiff: stat["qdiff_equals_pdiff"] += 1
    W = 0
    for j in range(4):
        if all(q0[PW[j][row]] == q1[PW[j][row]] for row in range(4)):
            W += 1
    stat["whist"][W] += 1
    if W == 3: stat["W_is_3_all_trials"] += 1
    if not trivial and W == 3: stat["W_is_3_nontrivial"] += 1

keyed_ok = (stat["qdiff_equals_pdiff"] == 1000
            and stat["W_is_3_nontrivial"] == stat["nontrivial"])

gate_pass = bool(dm_ok and md_ok and ranks == {0: 32, 1: 0, 2: 0, 3: 0}
                 and map0_is_identity and maps123_are_zero
                 and P_exact == 1.0 and keyed_ok)

out = {
    "schema": "crypto.autoresearch.gate0.v1",
    "task_id": "TASK-20260901-f5d3a4",
    "run": "RUN 1 (GATE 0, BLOCKING per record PR-0/F1)",
    "idea_record": "IDEA-20260901-04606c",
    "anchor_cell": {"r": ROUNDS, "A": [0], "S": [0], "sbox": "identity"},
    "object": "A_{5,{0},j} = P_j (D_5 M_5) P_0^T (repaired census object at the anchor)",
    "independence_note": "byte-level basis-vector simulation of the pinned round functions; shares no code with census046.py (explicit SR/MC matrix products)",
    "checks": {
        "a_D5M5_is_I128": dm_ok,
        "a_M5D5_is_I128": md_ok,
        "b_word_map_ranks": ranks,
        "b_ranks_required": [32, 0, 0, 0],
        "b_word0_map_column_equal_identity": map0_is_identity,
        "b_words123_maps_column_equal_zero": maps123_are_zero,
        "c_P_Wge1_nontrivial_exact": P_exact,
        "d_keyed_trials": stat,
        "d_keyed_ok": keyed_ok,
    },
    "gate0_pass": gate_pass,
    "on_failure": "exit 5 -> HALT invalid_measurement (F1); all prospective census readings VOID; never negative evidence (rule 5)",
    "seed_keyed_trials": "2026090104606c",
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
with open(sys.argv[1] if len(sys.argv) > 1 else "runs/gate0.json", "w") as f:
    f.write(txt)
print(json.dumps({
    "gate0_pass": gate_pass,
    "ranks": ranks,
    "D5M5_I": dm_ok, "M5D5_I": md_ok,
    "word0_identity": map0_is_identity, "words123_zero": maps123_are_zero,
    "P_exact": P_exact,
    "keyed": {"qdiff_eq": stat["qdiff_equals_pdiff"],
              "W3_nontrivial": stat["W_is_3_nontrivial"],
              "nontrivial": stat["nontrivial"],
              "trivial_swaps": stat["trivial_swaps"]},
}, indent=1))
sys.exit(0 if gate_pass else 5)
