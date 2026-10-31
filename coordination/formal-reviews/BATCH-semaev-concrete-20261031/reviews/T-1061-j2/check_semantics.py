#!/usr/bin/env python3
"""Small independent Boolean-row and separator check at the frozen Git tree."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

SOURCE_COMMIT = "ad91212179e737d829076ca593d608261590ba89"
ROOT = Path(__file__).resolve().parents[4]
PATHS = [
    "formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean",
    "formal/CryptoResearch/Semaev/BooleanParityFiltrationCertificate.lean",
    "formal/CryptoResearch/Semaev/BooleanParityFiniteCertificate.lean",
    "formal/targets/semaev-s3-concrete-first-fall-20261023.yaml",
    "formal/lean-toolchain",
    "formal/lake-manifest.json",
]


def blob(path):
    return subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{path}"], cwd=ROOT)


finite = blob(PATHS[2]).decode()
theorem = blob(PATHS[0]).decode()
equations = json.loads(re.search(r"def equations : List \(List Nat\) :=\s*(\[\[.*?\]\])", finite, re.S).group(1))
witness = int(re.search(r"def witnessNat : Nat := (\d+)", theorem).group(1))
combo = int(re.search(r"def comboMask : Nat := (\d+)", theorem).group(1))


def product_row(equation, multiplier):
    result = 0
    for monomial in equation:
        result ^= 1 << (monomial | multiplier)
    return result


def rows(degree):
    return [
        value
        for equation in equations
        for multiplier in range(256)
        for value in [product_row(equation, multiplier)]
        if all(not (value >> mask & 1) or bin(mask).count("1") <= degree for mask in range(256))
    ]


rows2, rows3 = rows(2), rows(3)
computed = 0
for index, value in enumerate(rows3):
    if combo >> index & 1:
        computed ^= value
assert len(equations) == 4 and len(rows2) == 28 and len(rows3) == 80
assert computed == witness
assert all(not (witness >> mask & 1) or bin(mask).count("1") <= 2 for mask in range(256))
assert all(((value >> 80) & 1) ^ ((value >> 192) & 1) == 0 for value in rows2)
assert ((witness >> 80) & 1) ^ ((witness >> 192) & 1) == 1
mutant_row = next(index for index, value in enumerate(rows2)
                  if (((value >> 80) & 1) ^ (value & 1)) == 1)
result = {
    "source_commit": SOURCE_COMMIT,
    "hashes": {path: hashlib.sha256(blob(path)).hexdigest() for path in PATHS},
    "rows2": len(rows2),
    "rows3": len(rows3),
    "selected": bin(combo).count("1"),
    "witness_match": computed == witness,
    "witness_bit_count": bin(witness).count("1"),
    "degree_at_most_two": True,
    "separator_rows2_zero": True,
    "separator_witness_one": True,
    "negative_control": {
        "replace_192_with": 0,
        "row_index": mutant_row,
        "mutant_value": 1,
    },
}
print(json.dumps(result, sort_keys=True, indent=2))
