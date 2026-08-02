#!/usr/bin/env python3
"""CERTIFICATE VERIFIER (independent of the attack code path).

The attack lives in sq.c (C, AES-NI + its own GF-derived tables). This verifier
uses TWO implementations that share no code with it:
  V1 = aes_reduced.py, the campaign's pinned instrument (pure Python, derived
       tables) -- reproduces the reduced-round target ciphertexts;
  V2 = pycryptodome    -- reproduces a full 10-round challenge ciphertext, which
       pins the recovered MASTER KEY itself under a third-party implementation.

A certificate is: recovered key K'  =>  both V1 and V2 reproduce, byte for byte,
ciphertexts that were produced by the oracle before K' was known.

usage: certify.py <recovered_key_hex> <rounds> <targets.json>
"""
import importlib.util, json, os, subprocess, sys

REPO = "/home/user/crypto-autoresearcher"
MOD = os.path.join(REPO, "coordination/goals/GOAL-AES-001/batches/BATCH-001/"
                         "tasks/TASK-20260731-602/aes_reduced.py")
spec = importlib.util.spec_from_file_location("aes_reduced", MOD)
aes_reduced = importlib.util.module_from_spec(spec); sys.modules["aes_reduced"] = aes_reduced
spec.loader.exec_module(aes_reduced)
from Crypto.Cipher import AES as PyAES

khex, rounds, tf = sys.argv[1], int(sys.argv[2]), sys.argv[3]
K = bytes.fromhex(khex)
tg = json.load(open(tf))
assert tg["rounds"] == rounds, "target round count mismatch"

cip = aes_reduced.AES(K, rounds=rounds)          # V1
ok_v1 = all(cip.encrypt_block(bytes.fromhex(p)) == bytes.fromhex(c) for p, c in tg["pairs"])

# V2: full 10-round challenge. The oracle published these before the attack ran.
chal = json.load(open(os.path.join(os.path.dirname(tf), "challenge_full10.json")))
v2 = PyAES.new(K, PyAES.MODE_ECB)
ok_v2 = all(v2.encrypt(bytes.fromhex(p)).hex() == c for p, c in chal["pairs"])

cert = {
    "kind": "key_recovery",
    "cipher": "AES-128 reduced to %d rounds (convention C1/C2/C3 of aes_reduced.py)" % rounds,
    "recovered_key": khex,
    "targets_file": os.path.abspath(tf),
    "n_reduced_round_pairs": len(tg["pairs"]),
    "verifier_1": {"impl": "aes_reduced.py (pinned instrument, pure Python)",
                   "module_sha256": aes_reduced.MODULE_SHA256,
                   "reproduces_all_target_ciphertexts": ok_v1},
    "verifier_2": {"impl": "pycryptodome %s, full 10-round AES-128" % __import__("Crypto").__version__,
                   "n_pairs": len(chal["pairs"]),
                   "reproduces_full_round_challenge": ok_v2},
    "verified": bool(ok_v1 and ok_v2),
}
print(json.dumps(cert, indent=2))
sys.exit(0 if cert["verified"] else 1)
