#!/usr/bin/env python3
"""STEP 1: 4-round integral (Square) distinguisher on the campaign's pinned
reduced-round AES, with a matched random-permutation control.

Instrument: coordination/.../TASK-20260731-602/aes_reduced.py (imported, not rebuilt).
Convention: (C1) final round drops MixColumns, (C2) initial ARK not a round,
(C3) untruncated FIPS-197 key schedule.

Claim tested: for a Lambda-set of 256 plaintexts active in one byte and constant
elsewhere, EVERY byte of the state after 3 rounds XOR-sums to 0 over the set
(= the state at the INPUT of round 4).  Controls: (a) same measurement after 4
rounds, (b) same measurement on a matched random permutation.
"""
import hashlib, importlib.util, json, os, random, sys, time

REPO = "/home/user/crypto-autoresearcher"
MOD = os.path.join(REPO, "coordination/goals/GOAL-AES-001/batches/BATCH-001/"
                         "tasks/TASK-20260731-602/aes_reduced.py")
spec = importlib.util.spec_from_file_location("aes_reduced", MOD)
aes_reduced = importlib.util.module_from_spec(spec)
sys.modules["aes_reduced"] = aes_reduced
spec.loader.exec_module(aes_reduced)
AES = aes_reduced.AES

SEED = 20260801
rng = random.Random(SEED)

def lam_set(base, pos):
    return [bytes(base[:pos]) + bytes([v]) + bytes(base[pos+1:]) for v in range(256)]

def xor_sum(states):
    acc = bytearray(16)
    for s in states:
        for i in range(16):
            acc[i] ^= s[i]
    return bytes(acc)

out = {"seed": SEED, "module_sha256": aes_reduced.MODULE_SHA256, "utc_start": time.time()}

# --- sanity: the instrument is FIPS-197 at 10 rounds, cross-checked vs pycryptodome
from Crypto.Cipher import AES as PyAES
k = bytes(range(16)); p = bytes.fromhex("00112233445566778899aabbccddeeff")
ref = PyAES.new(k, PyAES.MODE_ECB).encrypt(p)
assert AES(k, rounds=10).encrypt_block(p) == ref, "instrument != pycryptodome at 10 rounds"
out["instrument_matches_pycryptodome_10r"] = True

# --- A. balance after r rounds, real AES, many keys/positions ------------------
TRIALS = 40
res = {}
for r in (2, 3, 4, 5):
    zero_bytes = 0; total_bytes = 0; fully_balanced_sets = 0
    for t in range(TRIALS):
        key = bytes(rng.randrange(256) for _ in range(16))
        base = bytes(rng.randrange(256) for _ in range(16))
        pos = rng.randrange(16)
        c = AES(key, rounds=max(r, 1))
        sts = [c.encrypt_partial(c.whiten(pt), 0, r) for pt in lam_set(base, pos)]
        xs = xor_sum(sts)
        z = sum(1 for b in xs if b == 0)
        zero_bytes += z; total_bytes += 16
        fully_balanced_sets += (z == 16)
    res[f"level_{r}"] = {"lambda_sets": TRIALS, "balanced_bytes": zero_bytes,
                         "total_bytes": total_bytes,
                         "fully_balanced_sets": fully_balanced_sets}
out["A_real_aes_balance_by_level"] = res

# --- B. control: matched random permutation ----------------------------------
# Null object of the same shape: a 128-bit permutation that is not 3-round AES.
# (b1) full 10-round AES under an independent random key, used as a PRP;
# (b2) the pinned module's own null objects (random S-box / identity MixColumns)
#      at the same round count, so the control differs in ONE component.
ctl = {}
zero_bytes = 0; total = 0; full = 0
for t in range(TRIALS):
    key = bytes(rng.randrange(256) for _ in range(16))
    base = bytes(rng.randrange(256) for _ in range(16)); pos = rng.randrange(16)
    c = AES(key, rounds=10)
    xs = xor_sum([c.encrypt_block(pt) for pt in lam_set(base, pos)])
    z = sum(1 for b in xs if b == 0); zero_bytes += z; total += 16; full += (z == 16)
ctl["prp_aes10"] = {"lambda_sets": TRIALS, "balanced_bytes": zero_bytes,
                    "total_bytes": total, "fully_balanced_sets": full}

for label, mk in (("random_sbox_3r", lambda key: AES(key, rounds=3).with_random_sbox(seed=777)),
                  ("identity_mixcolumns_3r", lambda key: AES(key, rounds=3).with_identity_mixcolumns())):
    zb = 0; tb = 0; fb = 0
    for t in range(TRIALS):
        key = bytes(rng.randrange(256) for _ in range(16))
        base = bytes(rng.randrange(256) for _ in range(16)); pos = rng.randrange(16)
        c = mk(key)
        xs = xor_sum([c.encrypt_partial(c.whiten(pt), 0, 3) for pt in lam_set(base, pos)])
        z = sum(1 for b in xs if b == 0); zb += z; tb += 16; fb += (z == 16)
    ctl[label] = {"lambda_sets": TRIALS, "balanced_bytes": zb, "total_bytes": tb,
                  "fully_balanced_sets": fb}
out["B_controls"] = ctl

# --- C. per-byte false-positive rate of the balance test on the PRP control ---
N = 200  # small here; the large-sample false-positive measurement is done in C (step4)
hits = 0
c = AES(bytes(rng.randrange(256) for _ in range(16)), rounds=10)
for t in range(N):
    base = bytes(rng.randrange(256) for _ in range(16)); pos = rng.randrange(16)
    xs = xor_sum([c.encrypt_block(pt) for pt in lam_set(base, pos)])
    hits += sum(1 for b in xs if b == 0)
out["C_prp_per_byte_balance_rate"] = {"trials_bytes": N * 16, "balanced": hits,
                                      "rate": hits / (N * 16), "expected_1_over_256": 1 / 256}
out["utc_end"] = time.time()
print(json.dumps(out, indent=2))
