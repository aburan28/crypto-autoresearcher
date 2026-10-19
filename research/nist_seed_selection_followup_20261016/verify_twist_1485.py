"""Replay the bounded P-224 slot-1485 twist-factor check.

The expensive PARI factorization is recorded in factorization.json. This
script verifies its factors against the previously frozen twist order and
checks primality with PARI's isprime. It does not rerun the search.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_selection_deep_20261016" / "twist_factor_probe.json"
EXPECTED_SOURCE_SHA256 = "2ba269867f1bf0477aa79d29e72a2e0947ccaae299b92e44c9b3b8259ea92054"
FACTOR_A = 103338691145424448535900484671
FACTOR_B = 2805260028296929757374709219448951881


def main() -> None:
    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == EXPECTED_SOURCE_SHA256
    rows = json.loads(source)["rows_completed_or_censored"]
    selected = {
        row["ordinal"]: row
        for row in rows
        if row["timestamp"] == 891607927 and row["field_bits"] == 224
    }
    skipped = selected[1485]
    published = selected[7026]
    residual = int(skipped["residual_hex"], 16)
    order = int(skipped["twist_order_hex"], 16)
    assert skipped["status"] == "timeout"
    assert residual == FACTOR_A * FACTOR_B
    assert order == 3 * 31 * FACTOR_A * FACTOR_B

    gp_input = f"print(isprime({FACTOR_A})); print(isprime({FACTOR_B})); quit\n"
    gp = subprocess.run(
        ["gp", "-q", "-s", "134217728"],
        input=gp_input,
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    assert not gp.stderr and gp.stdout.splitlines() == ["1", "1"], (
        gp.stdout,
        gp.stderr,
    )
    assert published["status"] == "complete"
    published_factors = published["prime_factors_if_complete"]
    assert math.prod(prime**power for prime, power in published_factors) == int(
        published["twist_order_hex"], 16
    )
    assert max(prime.bit_length() for prime, _ in published_factors) == 118
    result = {
        "source": str(SOURCE.relative_to(HERE.parent.parent)),
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "gp_version": subprocess.check_output(["gp", "--version-short"], text=True).strip(),
        "field_bits": 224,
        "timestamp": 891607927,
        "skipped_ordinal": 1485,
        "twist_order_hex": skipped["twist_order_hex"],
        "complete_prime_factors": [[3, 1], [31, 1], [FACTOR_A, 1], [FACTOR_B, 1]],
        "gp_isprime_results_for_new_factors": [1, 1],
        "new_largest_prime_factor_bits": max(FACTOR_A.bit_length(), FACTOR_B.bit_length()),
        "published_ordinal": 7026,
        "published_largest_prime_factor_bits": 118,
        "other_p224_slots_largest_prime_factor_bits": {
            str(ordinal): selected[ordinal]["largest_prime_factor_bits_if_complete"]
            for ordinal in (777, 5736)
        },
        "factor_product_matches_exact_twist_order": True,
        "historical_selection_rule_inferred": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
