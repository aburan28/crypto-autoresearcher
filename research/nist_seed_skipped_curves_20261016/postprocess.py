"""Group sign-equivalent models and add bounded CM and twist screens.

The raw audit deliberately keeps both square roots of b^2. Over the 224-bit
field those roots give isomorphic curves; this file makes one row per seed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from sage.all import GF, Integer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness.endosweep.quadorder import small_discriminant_scan

HERE = Path(__file__).resolve().parent
RAW = HERE / "traits.json"
OUT = HERE / "assessed.json"
CM_BOUND = 2_000_000


def primality(value: int) -> str:
    n = Integer(value)
    if not n.is_prime(proof=False):
        return "composite"
    return "proven_prime" if n.is_prime(proof=True) else "probable_prime_only"


def main() -> None:
    raw = json.loads(RAW.read_text())
    rows = raw["unpublished_candidates"]
    groups = {}
    for row in rows:
        key = (row["timestamp"], row["seed_ordinal_one_based"])
        groups.setdefault(key, []).append(row)
    assessed = []
    for key in sorted(groups):
        alternatives = sorted(groups[key], key=lambda row: int(row["b_hex"], 16))
        row = dict(alternatives[0])
        p = int(row["p_hex"], 16)
        n = int(row["n_hex"], 16)
        if len(alternatives) == 2:
            assert p % 4 == 1
            assert int(alternatives[0]["n_hex"], 16) == int(alternatives[1]["n_hex"], 16)
            assert (int(alternatives[0]["b_hex"], 16) + int(alternatives[1]["b_hex"], 16)) % p == 0
            u = int(GF(p)(-1).sqrt())
            assert pow(u, 2, p) == p - 1
            row["alternate_sign_model"] = {
                "b_hex": alternatives[1]["b_hex"],
                "curve_uid": alternatives[1]["identity"]["curve_uid"],
                "isomorphism_u_hex": hex(min(u, p - u)),
                "isomorphism": "(x,y) -> (-x,u^3*y), u^2=-1 mod p",
            }
        else:
            assert len(alternatives) == 1
            row["alternate_sign_model"] = None
        delta = int(row["delta_pi_hex_signed"], 16)
        scan = small_discriminant_scan(delta, CM_BOUND)
        row["cm_scan"] = {
            "bound_abs_fundamental_discriminant": CM_BOUND,
            "found_fundamental_discriminant": scan.found,
            "found_frobenius_conductor": scan.conductor,
            "minimum_noninteger_endomorphism_degree": CM_BOUND // 4 if scan.found is None else None,
            "certificate": scan.certificate,
            "representative_endo_conductor": None,
        }
        twist_rest = int(row["twist_unfactored_rest_hex"], 16)
        row["twist_residual_primality"] = primality(twist_rest)
        if row["twist_residual_primality"] == "proven_prime":
            row["twist_full_factorization_proven"] = True
            row["twist_largest_prime_factor_bits"] = max(
                [q.bit_length() for q, _ in row["twist_small_factors_to_10000"]] + [twist_rest.bit_length()]
            )
        else:
            row["twist_full_factorization_proven"] = False
            row["twist_largest_prime_factor_bits"] = None
        row["published_same_field_order_matches"] = list(row["published_same_field_order_matches"])
        assessed.append(row)
        print(f"screened {key[0]}:{key[1]}, CM <= {CM_BOUND}: {scan.found}, twist residual: {row['twist_residual_primality']}", flush=True)
    assert len(assessed) == 11
    output = {
        "raw_traits_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "postprocess_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "number_of_seed_candidates": len(assessed),
        "number_of_curve_models_in_raw_audit": len(rows),
        "cm_scan_bound": CM_BOUND,
        "candidate_rows": assessed,
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
