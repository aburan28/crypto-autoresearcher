"""Independent Sage arithmetic check of the two PARI/GP factor receipts."""

import hashlib
import json
from pathlib import Path
from sage.version import version as sage_version

here = Path(__file__).resolve().parent
traits_path = here.parent / "nist_seed_skipped_curves_20261016" / "traits.json"
traits_raw = traits_path.read_bytes()
traits_digest = hashlib.sha256(traits_raw).hexdigest()
if traits_digest != "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67":
    raise ValueError("Exact trait input changed")
traits = json.loads(traits_raw)
out = []
for name in ("prime239v2", "skip239_2682"):
    path = here / "factor_runs" / (name + ".json")
    raw = path.read_bytes()
    receipt = json.loads(raw)
    residual = ZZ(int(receipt["residual_hex"], 0))
    twist = ZZ(int(receipt["twist_order_hex"], 0))
    factors = [
        {"prime": str(ZZ(item["prime"])), "exponent": item["exponent"],
         "sage_is_prime_proof_true": bool(ZZ(item["prime"]).is_prime(proof=True))}
        for item in receipt["returned_factors"]
    ]
    product = prod(ZZ(item["prime"]) ** item["exponent"] for item in factors)
    row = (traits["published_controls"]["prime239v2"] if name == "prime239v2"
           else next(r for r in traits["unpublished_candidates"]
                     if r["timestamp"] == 863711343 and r["seed_ordinal_one_based"] == 2682))
    known = prod(ZZ(p) ** e for p, e in row["twist_small_factors_to_10000"])
    out.append({
        "name": name,
        "receipt_sha256": hashlib.sha256(raw).hexdigest(),
        "all_factors_proven_prime": all(item["sage_is_prime_proof_true"] for item in factors),
        "residual_product_matches": bool(product == residual),
        "full_twist_product_matches": bool(known * product == twist),
        "known_small_factors": row["twist_small_factors_to_10000"],
        "returned_factors": factors,
        "largest_prime_factor_bits": max(ZZ(item["prime"]).nbits() for item in factors),
    })

result = {
    "schema": "nist-seed-twist-independent-check/v1",
    "sage_version": sage_version,
    "input_traits_sha256": traits_digest,
    "rows": out,
    "all_pass": all(row["all_factors_proven_prime"] and row["residual_product_matches"]
                    and row["full_twist_product_matches"] for row in out),
}
(here / "sage_verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print("PASS" if result["all_pass"] else "FAIL")
