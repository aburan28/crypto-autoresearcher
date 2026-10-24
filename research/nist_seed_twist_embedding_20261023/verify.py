#!/usr/bin/env python3
"""Independent direct-pow replay of the bounded twist embedding screen."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
data = json.loads((HERE / "analysis.json").read_text())
assert data["bounds"] == [20, 1000]
assert len(data["rows"]) == 21
assert sum(len(row["hits"]) for row in data["rows"]) == 25
assert len({row["curve_uid"] for row in data["rows"]}) == 21
for name, path in {
    "assessed": ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json",
    "traits": ROOT / "research/nist_seed_skipped_curves_20261016/traits.json",
    "probe": ROOT / "research/nist_seed_selection_deep_20261016/twist_factor_probe.json",
    "p224_followup": ROOT / "research/nist_seed_selection_followup_20261016/verification.json",
    "skip239_2682": ROOT / "research/nist_seed_commonality_20261023/factor_runs/skip239_2682.json",
    "prime239v2": ROOT / "research/nist_seed_commonality_20261023/factor_runs/prime239v2.json",
}.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == data["source_sha256"][name]
for row in data["rows"]:
    p = int(row["p_hex"], 16)
    assert row["large_factor_count"] == len(row["hits"])
    for hit in row["hits"]:
        ell = int(hit["prime"])
        assert ell.bit_length() == hit["bits"] and ell >= 2**80
        assert int(row["twist_order_hex"], 16) % ell == 0
        for bound in data["bounds"]:
            matches = [k for k in range(1, bound + 1) if pow(p, k, ell) == 1]
            observed = matches[0] if matches else None
            assert observed == hit[f"k_le_{bound}"]
    for bound in data["bounds"]:
        assert row[f"any_k_le_{bound}"] == any(hit[f"k_le_{bound}"] is not None for hit in row["hits"])
print(json.dumps({"status": "PASS", "rows": len(data["rows"]),
                  "large_prime_factors": sum(len(row["hits"]) for row in data["rows"]),
                  "direct_pow_checks": 25 * (20 + 1000)}, sort_keys=True))
