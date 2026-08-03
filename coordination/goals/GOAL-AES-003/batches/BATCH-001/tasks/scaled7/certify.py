"""certify.py -- INDEPENDENT certificate verifier for MINI-AES-64 key recoveries.

A certificate here is: the RECOVERED key reproduces the EXACT target
ciphertexts, at the STATED ROUND COUNT, under ref4.py -- an implementation
that shares no code with the attack (sq4.c).

The round count is part of the certificate. A certificate at r rounds is a
statement about r-round MINI-AES-64 and about nothing else. MINI-AES-64 is a
4-bit-cell analogue; a certificate here is NOT a statement about AES-128.

usage: certify.py <attack_out.json> <targets.json> <rounds>
"""
import json
import sys

import ref4

atk = json.load(open(sys.argv[1]))
tgt = json.load(open(sys.argv[2]))
rounds = int(sys.argv[3])

recovered = atk["recovered_master"]
assert tgt["rounds"] == rounds, "target round count does not match the claim"
assert atk["rounds"] == rounds, "attack round count does not match the claim"

results = []
allok = True
for pt, ct in tgt["pairs"]:
    got = ref4.encrypt(pt, recovered, rounds)
    ok = (got == ct)
    allok &= ok
    results.append({"pt": pt, "target_ct": ct, "ct_under_recovered_key": got, "match": ok})

cert = {
    "certificate": {
        "kind": "key_recovery",
        "cipher": "MINI-AES-64 (4-bit cells, 64-bit block, 64-bit key)",
        "round_count": rounds,
        "NOT_A_CLAIM_ABOUT": "AES-128 at any round count",
        "recovered_key": recovered,
        "blocks_checked": len(results),
        "all_match": bool(allok),
        "verified": bool(allok),
        "independent_implementation": "ref4.py (row-major matrix state, log/antilog GF tables); shares no code with sq4.c",
        "verified_by": "certify.py, which does not import or read sq4.c",
    },
    "pairs": results,
}
print(json.dumps(cert, indent=2))
sys.exit(0 if allok else 1)
