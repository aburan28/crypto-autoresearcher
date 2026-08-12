#!/usr/bin/env python3
"""Four-way pinning: C AES-NI, C software, aes_reduced.py, pycryptodome.
BOTH directions, r = 1..10, FIPS-197 KAT + random vectors.
Emits pin_receipt.json. Non-zero exit iff any disagreement."""
import hashlib, importlib.util, json, os, subprocess, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
REF = "/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/aes_reduced.py"

spec = importlib.util.spec_from_file_location("aes_reduced", REF)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod          # D-705-2 defect avoided deliberately
spec.loader.exec_module(mod)
AES = mod.AES

from Crypto.Cipher import AES as PCAES

def c(mode, *args):
    out = subprocess.run([os.path.join(HERE, "yoyo"), mode, *[str(a) for a in args]],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)

fails = []
checks = 0

FIPS_KEY = "000102030405060708090a0b0c0d0e0f"
FIPS_PT  = "00112233445566778899aabbccddeeff"
FIPS_CT  = "69c4e0d86a7b0430d8cdb78070b4c55a"

rng = random.Random(20260802)
vectors = [(FIPS_KEY, FIPS_PT)]
for _ in range(24):
    vectors.append((bytes(rng.randrange(256) for _ in range(16)).hex(),
                    bytes(rng.randrange(256) for _ in range(16)).hex()))

# --- FIPS-197 known answer, r=10, all four implementations -------------------
r10 = c("selftest", FIPS_KEY, FIPS_PT)["rounds"]["10"]
kat = {"c_ni": r10["ni_enc"], "c_sw": r10["sw_enc"],
       "aes_reduced": AES(bytes.fromhex(FIPS_KEY), rounds=10).encrypt_block(bytes.fromhex(FIPS_PT)).hex(),
       "pycryptodome": PCAES.new(bytes.fromhex(FIPS_KEY), PCAES.MODE_ECB).encrypt(bytes.fromhex(FIPS_PT)).hex(),
       "fips197_expected": FIPS_CT}
checks += 4
for k, v in kat.items():
    if v != FIPS_CT:
        fails.append(("FIPS197-KAT", k, v))

# --- forward direction, r = 1..10, C(2 impls) vs aes_reduced.py --------------
# --- backward direction: decrypt an ARBITRARY ciphertext (not an image) ------
detail = []
for keyh, pth in vectors:
    st = c("selftest", keyh, pth)["rounds"]
    dv = c("decvec", keyh, pth)["rounds"]      # treat pth as a ciphertext
    K = bytes.fromhex(keyh); P = bytes.fromhex(pth)
    for r in range(1, 11):
        A = AES(K, rounds=r)
        e_ref = A.encrypt_block(P).hex()
        d_ref = A.decrypt_block(P).hex()          # arbitrary ct
        checks += 6
        row = {"key": keyh, "pt": pth, "r": r}
        if not (st[str(r)]["sw_enc"] == st[str(r)]["ni_enc"] == e_ref):
            fails.append(("ENC", keyh, pth, r, st[str(r)], e_ref))
        # decryption of the software ciphertext must return the plaintext
        if not (st[str(r)]["sw_dec_of_sw_enc"] == st[str(r)]["ni_dec_of_sw_enc"] == pth):
            fails.append(("DEC-ROUNDTRIP", keyh, pth, r, st[str(r)]))
        # decryption of an arbitrary block must agree three ways
        if not (dv[str(r)]["sw_dec"] == dv[str(r)]["ni_dec"] == d_ref):
            fails.append(("DEC-ARBITRARY", keyh, pth, r, dv[str(r)], d_ref))
        detail.append(row)

# --- pycryptodome at r=10 on every random vector, both directions -----------
for keyh, pth in vectors:
    K = bytes.fromhex(keyh); P = bytes.fromhex(pth)
    cph = PCAES.new(K, PCAES.MODE_ECB)
    st = c("selftest", keyh, pth)["rounds"]["10"]
    dv = c("decvec", keyh, pth)["rounds"]["10"]
    checks += 2
    if cph.encrypt(P).hex() != st["ni_enc"]:
        fails.append(("PYCRYPTO-ENC", keyh, pth))
    if PCAES.new(K, PCAES.MODE_ECB).decrypt(P).hex() != dv["ni_dec"]:
        fails.append(("PYCRYPTO-DEC", keyh, pth))

receipt = {
    "utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
    "aes_reduced_module_sha256": mod.MODULE_SHA256,
    "yoyo_c_sha256": hashlib.sha256(open(os.path.join(HERE, "yoyo.c"), "rb").read()).hexdigest(),
    "pycryptodome_version": __import__("Crypto").__version__,
    "fips197_kat": kat,
    "vectors": len(vectors),
    "rounds_tested": list(range(1, 11)),
    "directions": ["encrypt", "decrypt(roundtrip)", "decrypt(arbitrary ciphertext)"],
    "implementations": ["C AES-NI", "C software (GF-derived tables)", "aes_reduced.py", "pycryptodome"],
    "total_equality_checks": checks,
    "failures": fails,
    "PASS": len(fails) == 0,
}
json.dump(receipt, open(os.path.join(HERE, "pin_receipt.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in receipt.items() if k != "fips197_kat"}, indent=1))
sys.exit(0 if not fails else 1)
