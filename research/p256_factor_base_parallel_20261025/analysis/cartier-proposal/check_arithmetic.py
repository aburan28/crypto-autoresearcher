"""Reproduce only the explicit arithmetic in the Cartier proposal."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1]
sys.path.insert(0, str(STUDY/"baseline"))
from parameters import CURVES


def check():
    curve = next(c for c in CURVES if c["name"] == "P-256")
    p, r = curve["p"], curve["r"]
    assert p % 4 == 3
    assert pow(p, -1, 4) == 3
    # Infinity valuations; finite ramification orders are nonnegative too.
    infinity = [-5+6, -5+9, -4-5+9]
    finite = [3-2, 3-3, 3-3]
    assert infinity == [1, 4, 0] and min(finite) >= 0
    rows = []
    for c in range(-2, 3):
        value = p*p+c*p+1
        residue = value % r
        assert residue != 0
        rows.append({"c": c, "order_candidate": str(value), "mod_r": str(residue)})
    return {"status": "PASS", "scope": "arithmetic only; geometric derivation is a separate obligation",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "basis_infinity_orders": infinity, "basis_finite_orders": finite,
            "inverse_p_mod_4": 3, "candidate_residues": rows}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
