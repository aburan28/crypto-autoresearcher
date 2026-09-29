import hashlib
import json
import os

TASKDIR = os.path.dirname(os.path.abspath(__file__))
BASE = "coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-f5e58b/"

# ---------- from-scratch AES (written fresh for this validation) ----------
def gf8_inv(a):
    if a == 0:
        return 0
    r, e, b = 1, 254, a  # a^254 = a^{-1} in GF(2^8)
    while e:
        if e & 1:
            r = gf8_mul(r, b)
        b = gf8_mul(b, b)
        e >>= 1
    return r

def gf8_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r

def build_sbox_fresh():
    s = []
    for i in range(256):
        inv = gf8_inv(i)
        b = inv
        rot = lambda x, n: ((x << n) | (x >> (8 - n))) & 0xFF
        s.append(inv ^ rot(inv, 1) ^ rot(inv, 2) ^ rot(inv, 3) ^ rot(inv, 4) ^ 0x63)
    return s

SBOX = build_sbox_fresh()
INV = [0] * 256
for i, v in enumerate(SBOX):
    INV[v] = i

RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

def key_expansion(key):
    w = [key[4 * i:4 * i + 4] for i in range(4)]
    for i in range(4, 44):
        t = w[i - 1][:]
        if i % 4 == 0:
            t = t[1:] + t[:1]
            t = [SBOX[b] for b in t]
            t[0] ^= RCON[i // 4 - 1]
        w.append([w[i - 4][j] ^ t[j] for j in range(4)])
    return w

def aes_encrypt(pt, key, rounds):
    w = key_expansion(key)
    # state column-major: s[r][c] = pt[r+4c]
    s = [[pt[r + 4 * c] for c in range(4)] for r in range(4)]
    def ark(rn):
        for c in range(4):
            for r in range(4):
                s[r][c] ^= w[4 * rn + c][r]
    def sub():
        for r in range(4):
            for c in range(4):
                s[r][c] = SBOX[s[r][c]]
    def shift():
        for r in range(1, 4):
            s[r] = s[r][r:] + s[r][:r]
    def mix():
        for c in range(4):
            col = [s[r][c] for r in range(4)]
            nc = [gf8_mul(2, col[0]) ^ gf8_mul(3, col[1]) ^ col[2] ^ col[3],
                  col[0] ^ gf8_mul(2, col[1]) ^ gf8_mul(3, col[2]) ^ col[3],
                  col[0] ^ col[1] ^ gf8_mul(2, col[2]) ^ gf8_mul(3, col[3]),
                  gf8_mul(3, col[0]) ^ col[1] ^ col[2] ^ gf8_mul(2, col[3])]
            for r in range(4):
                s[r][c] = nc[r]
    ark(0)
    for rn in range(1, rounds):
        sub(); shift(); mix(); ark(rn)
    sub(); shift(); ark(rounds)
    return bytes(s[r][c] for c in range(4) for r in range(4))

def aes_decrypt(ct, key, rounds):
    w = key_expansion(key)
    s = [[ct[r + 4 * c] for c in range(4)] for r in range(4)]
    def ark(rn):
        for c in range(4):
            for r in range(4):
                s[r][c] ^= w[4 * rn + c][r]
    def isub():
        for r in range(4):
            for c in range(4):
                s[r][c] = INV[s[r][c]]
    def ishift():
        for r in range(1, 4):
            s[r] = s[r][4 - r:] + s[r][:4 - r]
    def imix():
        for c in range(4):
            col = [s[r][c] for r in range(4)]
            nc = [gf8_mul(14, col[0]) ^ gf8_mul(11, col[1]) ^ gf8_mul(13, col[2]) ^ gf8_mul(9, col[3]),
                  gf8_mul(9, col[0]) ^ gf8_mul(14, col[1]) ^ gf8_mul(11, col[2]) ^ gf8_mul(13, col[3]),
                  gf8_mul(13, col[0]) ^ gf8_mul(9, col[1]) ^ gf8_mul(14, col[2]) ^ gf8_mul(11, col[3]),
                  gf8_mul(11, col[0]) ^ gf8_mul(13, col[1]) ^ gf8_mul(9, col[2]) ^ gf8_mul(14, col[3])]
            for r in range(4):
                s[r][c] = nc[r]
    ark(rounds)
    for rn in range(rounds - 1, 0, -1):
        ishift(); isub(); ark(rn); imix()
    ishift(); isub(); ark(0)
    return bytes(s[r][c] for c in range(4) for r in range(4))

hx = lambda s: bytes.fromhex(s)
out = {}

# ---------- pin re-verification ----------
kat_key = hx("000102030405060708090a0b0c0d0e0f")
kat_pt = hx("00112233445566778899aabbccddeeff")
kat_ct10 = aes_encrypt(kat_pt, kat_key, 10).hex()
kat_dec10 = aes_decrypt(hx("69c4e0d86a7b0430d8cdb78070b4c55a"), kat_key, 10).hex()
anchor_key = hx("2b7e151628aed2a6abf7158809cf4f3c")
r5_ct = aes_encrypt(kat_pt, anchor_key, 5).hex()
r5_back = aes_decrypt(hx("4167e8f8367c38cdb7bde2ade620a7a8"), anchor_key, 5).hex()
rt_fail = 0
for i in range(10):
    k = bytes([(i * 17 + j * 31) & 0xFF for j in range(16)])
    p = bytes([(i * 13 + j * 7 + 5) & 0xFF for j in range(16)])
    for rn in (1, 5, 10):
        if aes_decrypt(aes_encrypt(p, k, rn), k, rn) != p:
            rt_fail += 1
pin_aes = json.load(open(BASE + "pin_aes.json"))
out["aes_from_scratch"] = {
    "sbox_table_matches_committed": bytes(SBOX).hex() == pin_aes["sbox_table_hex"],
    "inv_sbox_matches_committed": bytes(INV).hex() == pin_aes["inv_sbox_table_hex"],
    "kat_r10_ct_fresh": kat_ct10,
    "kat_r10_match": kat_ct10 == "69c4e0d86a7b0430d8cdb78070b4c55a",
    "kat_r10_decrypt_restores_pt": kat_dec10 == kat_pt.hex(),
    "r5_anchor_ct_fresh": r5_ct,
    "r5_anchor_match": r5_ct == "4167e8f8367c38cdb7bde2ade620a7a8",
    "r5_anchor_decrypts_to_pt": r5_back == kat_pt.hex(),
    "fresh_roundtrip_failures_30_checks": rt_fail,
}

# ---------- random sbox determinism: splitmix64 + Fisher-Yates ----------
def sm64_stream(seed, n):
    state = seed & 0xFFFFFFFFFFFFFFFF
    out_ = []
    for _ in range(n):
        state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        out_.append(z ^ (z >> 31))
    return out_

def fy_desc(seed):
    s = list(range(256))
    r = sm64_stream(seed, 255)
    for i in range(255, 0, -1):
        j = r[255 - i] % (i + 1)
        s[i], s[j] = s[j], s[i]
    return s

def fy_asc(seed):
    s = list(range(256))
    r = sm64_stream(seed, 255)
    for i in range(255):
        j = i + r[i] % (256 - i)
        s[i], s[j] = s[j], s[i]
    return s

recon = {}
for name, seed, fn in (("sbox1", 424242201, None), ("sbox2", 424242202, None)):
    pin = json.load(open(BASE + ("pinsbox1.json" if name == "sbox1" else "pinsbox2.json")))
    committed = bytes.fromhex(pin["sbox_table_hex"])
    inv_c = bytes.fromhex(pin["inv_sbox_table_hex"])
    bijective = sorted(committed) == list(range(256))
    inv_ok = all(inv_c[v] == i for i, v in enumerate(committed))
    d = fy_desc(seed)
    a = fy_asc(seed)
    recon[name] = {
        "seed": seed,
        "committed_seed": pin["sbox_seed"],
        "bijective_fresh": bijective,
        "inv_exact_inverse_fresh": inv_ok,
        "matches_fy_descending_splitmix64": bytes(d) == committed,
        "matches_fy_ascending_splitmix64": bytes(a) == committed,
        "first8_committed": list(committed[:8]),
        "first8_fy_desc": d[:8],
        "first8_fy_asc": a[:8],
    }
out["random_sbox_reconstruction"] = recon

sv = json.load(open(BASE + "sbox_verify.json"))
out["sbox_verify_sha256_recomputed"] = {
    "aes": hashlib.sha256(bytes(SBOX)).hexdigest() == sv["aes_sha256"],
    "sbox1": hashlib.sha256(bytes.fromhex(json.load(open(BASE + "pinsbox1.json"))["sbox_table_hex"])).hexdigest() == sv["sbox1_sha256"],
    "sbox2": hashlib.sha256(bytes.fromhex(json.load(open(BASE + "pinsbox2.json"))["sbox_table_hex"])).hexdigest() == sv["sbox2_sha256"],
}

# ---------- RANK 3 arms ----------
CLAIMS = {"R3-A1": 59, "R3-A2": 58, "R3-A3": 51, "R3-A4": 3, "R3-A5": 4, "R3-A6": 2, "R3-A7": 4}
PREREQ = {
    "R3-A1": dict(sbox="aes", rounds=5, amask=1, smask=1, seed=424242101, arm_id=101),
    "R3-A2": dict(sbox="random_seed_424242201", rounds=5, amask=1, smask=1, seed=424242102, arm_id=102),
    "R3-A3": dict(sbox="random_seed_424242202", rounds=5, amask=1, smask=1, seed=424242103, arm_id=103),
    "R3-A4": dict(sbox="aes", rounds=10, amask=1, smask=1, seed=424242104, arm_id=104),
    "R3-A5": dict(sbox="aes", rounds=5, amask=15, smask=1, seed=424242105, arm_id=105),
    "R3-A6": dict(sbox="random_seed_424242201", rounds=5, amask=15, smask=1, seed=424242106, arm_id=106),
    "R3-A7": dict(sbox="random_seed_424242202", rounds=5, amask=15, smask=1, seed=424242107, arm_id=107),
}
PIN_TABLE = {
    "aes": pin_aes["sbox_table_hex"],
    "random_seed_424242201": json.load(open(BASE + "pinsbox1.json"))["sbox_table_hex"],
    "random_seed_424242202": json.load(open(BASE + "pinsbox2.json"))["sbox_table_hex"],
}
arms = {}
for arm, claimed in CLAIMS.items():
    d = json.load(open(BASE + f"runs/arm_{arm}.json"))
    W = d["W_ge1_nontrivial"]
    fresh_W = sum(d["whist"][1:])
    fresh_nontrivial = d["trials"] - d["trivial_swaps_excluded"]
    excess = W / (d["nontrivial_trials"] * 2 ** -30) if d["nontrivial_trials"] else None
    prereq = PREREQ[arm]
    sbox_name = d["sbox"]
    arms[arm] = {
        "claimed_W": claimed,
        "recorded_W": W,
        "fresh_W_from_whist": fresh_W,
        "W_match_claim": W == claimed,
        "whist_consistent": fresh_W == W and sum(d["whist"]) == d["nontrivial_trials"],
        "nontrivial_consistent": fresh_nontrivial == d["nontrivial_trials"],
        "zhist_sums_to_nontrivial": sum(d["zhist"]) == d["nontrivial_trials"],
        "by_word_sums_to_W": sum(d["W_ge1_by_word"]) == W,
        "excess_vs_null_4.0": round(excess, 4),
        "N_is_2pow32": d["trials"] == 2 ** 32,
        "params_match_prereg": all(d.get(k) == v for k, v in prereq.items()),
        "sbox_name_recorded": sbox_name,
        "sbox_table_matches_pin": d.get("sbox_table_hex") == PIN_TABLE.get(sbox_name),
        "sbox_bijective_fresh": sorted(bytes.fromhex(d["sbox_table_hex"])) == list(range(256)),
        "inside_0_12_band": 0 <= W <= 12,
    }
out["arms"] = arms
out["control_band_check"] = {
    "band": [0, 12],
    "controls": {a: arms[a]["inside_0_12_band"] for a in ("R3-A4", "R3-A5", "R3-A6", "R3-A7")},
    "all_inside": all(arms[a]["inside_0_12_band"] for a in ("R3-A4", "R3-A5", "R3-A6", "R3-A7")),
}
out["signal_arms_outside_null_interval"] = {
    a: arms[a]["recorded_W"] > 12 for a in ("R3-A1", "R3-A2", "R3-A3")
}

# ---------- RANK 2 positive control ----------
r2 = json.loads(open(BASE + "run_true_hint.stdout").read().strip())
hist = {}
for diag in r2["diagonals"]:
    hist[diag["survivor_count"]] = hist.get(diag["survivor_count"], 0) + 1
out["rank2_positive_control"] = {
    "survivor_histogram_fresh": hist,
    "predicted": {1: 4},
    "match_prediction": hist == {1: 4},
    "all_true_bytes_among_survivors": all(d["true_byte_among_survivors"] == 1 for d in r2["diagonals"]),
    "diagonals_unique_and_correct_recorded": r2["diagonals_unique_and_correct"],
    "slotmask": r2["slotmask"],
    "params_match_prereg": (r2["mode"], r2["rounds"], r2["nstruct"], r2["seed"], r2["nthreads"],
                            r2["target_key"], r2["hint_key"]) ==
                           ("attack6n", 6, 2, 90009, 1,
                            "2b7e151628aed2a6abf7158809cf4f3c", "53787ef6b300ea19f0a43d4915afd440"),
}

print(json.dumps(out, indent=1))
with open(os.path.join(TASKDIR, "f5e58b_result.json"), "w") as f:
    json.dump(out, f, indent=1)
