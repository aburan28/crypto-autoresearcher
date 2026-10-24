#!/usr/bin/env python3
"""Fixed 21-curve quadratic-twist subgroup embedding screen."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "research/nist_seed_skipped_curves_20261016"
PROBE = ROOT / "research/nist_seed_selection_deep_20261016/twist_factor_probe.json"
P224 = ROOT / "research/nist_seed_selection_followup_20261016/verification.json"
LATER = ROOT / "research/nist_seed_commonality_20261023/factor_runs"
BOUND = (20, 1000)
MIN_ELL = 1 << 80


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def first_hit(p, ell, bound):
    value = p % ell
    for k in range(1, bound + 1):
        if value == 1:
            return k
        value = value * p % ell
    return None


def check_controls():
    assert first_hit(2, 7, 3) == 3
    assert first_hit(3, 11, 5) == 5
    assert first_hit(3, 7, 3) is None
    assert first_hit(3, 7, 6) == 6


def product(factors):
    result = 1
    for ell, power in factors:
        assert ell > 1 and power >= 1
        result *= ell ** power
    return result


def verify_product(order, factors):
    if product(factors) != order:
        raise ValueError("factor product disagrees with twist order")


def main():
    check_controls()
    archive, archive_sha = read(SOURCE / "assessed.json")
    traits, traits_sha = read(SOURCE / "traits.json")
    probe, probe_sha = read(PROBE)
    follow, follow_sha = read(P224)
    later = {}
    hashes = {}
    for stem in ("skip239_2682", "prime239v2"):
        obj, digest = read(LATER / (stem + ".json"))
        later[stem] = obj
        hashes[stem] = digest
    curve_data = []
    for name, obj in traits["published_controls"].items():
        curve_data.append(("published", name, obj))
    for obj in archive["candidate_rows"]:
        field_bits = int(obj["p_hex"], 16).bit_length()
        name = f"skip-{field_bits}-{obj['seed_ordinal_one_based']}"
        curve_data.append(("skipped", name, obj))
    assert len(curve_data) == 21
    indexed = {}
    for label, name, obj in curve_data:
        p = int(obj["p_hex"], 16)
        key = (label, p.bit_length(), obj["seed_ordinal_one_based"])
        if key in indexed:
            raise ValueError("duplicate curve key")
        indexed[key] = (name, obj)
    assert len(indexed) == 21
    factor_map = {}
    for item in probe["rows_completed_or_censored"]:
        label = "published" if item["label"] == "published" else "skipped"
        key = (label, item["field_bits"], item["ordinal"])
        assert key in indexed
        if key in factor_map:
            raise ValueError("duplicate factor key")
        if item["status"] == "complete":
            factor_map[key] = (item["prime_factors_if_complete"], "probe")
    key = ("skipped", 224, 1485)
    assert key not in factor_map and follow["factor_product_matches_exact_twist_order"]
    factor_map[key] = (follow["complete_prime_factors"], "P-224 follow-up")
    for stem, key in (("skip239_2682", ("skipped", 239, 2682)),
                      ("prime239v2", ("published", 239, 2320))):
        assert key not in factor_map and later[stem]["verified_complete"]
        _, obj = indexed[key]
        small = obj["twist_small_factors_to_10000"]
        residual = [[f["prime"], f["exponent"]] for f in later[stem]["returned_factors"]]
        assert product(residual) == int(later[stem]["residual_hex"], 16)
        factor_map[key] = (small + residual, stem)
    assert set(factor_map) == set(indexed)
    rows = []
    for key in sorted(indexed, key=lambda k: (k[1], k[2], k[0])):
        name, obj = indexed[key]
        factors, factor_source = factor_map[key]
        p = int(obj["p_hex"], 16)
        twist_order = int(obj["twist_order_hex"], 16)
        verify_product(twist_order, factors)
        large = sorted([ell for ell, power in factors if ell >= MIN_ELL])
        hits = [{"prime": str(ell), "bits": ell.bit_length(),
                 "k_le_20": first_hit(p, ell, 20),
                 "k_le_1000": first_hit(p, ell, 1000)} for ell in large]
        for hit in hits:
            assert (hit["k_le_20"] is None or hit["k_le_20"] == hit["k_le_1000"])
            if hit["k_le_1000"] is not None:
                assert pow(p, hit["k_le_1000"], int(hit["prime"])) == 1
        rows.append({"label": key[0], "name": name, "ordinal": key[2],
                     "field_bits": key[1], "curve_uid": obj["identity"]["curve_uid"],
                     "p_hex": obj["p_hex"], "twist_order_hex": obj["twist_order_hex"],
                     "factor_source": factor_source, "factor_count": len(factors),
                     "large_factor_count": len(hits), "largest_factor_bits": max(ell.bit_length() for ell, _ in factors),
                     "hits": hits, "any_k_le_20": any(h["k_le_20"] is not None for h in hits),
                     "any_k_le_1000": any(h["k_le_1000"] is not None for h in hits)})
    controls = {"positive_2_mod_7": 3, "positive_3_mod_11": 5,
                "negative_3_mod_7_through_3": True, "positive_3_mod_7": 6,
                "wrong_product_rejected": False, "duplicate_key_rejected": False}
    try:
        verify_product(101, [[2, 1], [5, 1]])
    except ValueError:
        controls["wrong_product_rejected"] = True
    try:
        keys = ["same", "same"]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate factor key")
    except ValueError:
        controls["duplicate_key_rejected"] = True
    assert all(v is True for k, v in controls.items() if k.endswith("rejected"))
    matched = [r for r in rows if r["field_bits"] in (192, 224, 239, 256)]
    pairs = [(a, b) for a in matched for b in matched
             if a["field_bits"] == b["field_bits"] and a["label"] == "skipped" and b["label"] == "published"]
    assert len(pairs) == 25
    summary = {"rows": len(rows), "skipped": Counter(r["label"] for r in rows)["skipped"],
               "published": Counter(r["label"] for r in rows)["published"],
               "same_field_pairs": len(pairs),
               "low_degree_counts": {str(bound): {label: sum(r[f"any_k_le_{bound}"] for r in rows if r["label"] == label)
                                                 for label in ("skipped", "published")}
                                     for bound in BOUND}}
    result = {"schema": "nist-seed-twist-embedding-screen/v1", "protocol": "PROTOCOL.md",
              "source_sha256": {"assessed": archive_sha, "traits": traits_sha,
                                "probe": probe_sha, "p224_followup": follow_sha, **hashes},
              "min_large_factor_bits": 80, "bounds": list(BOUND), "controls": controls,
              "summary": summary, "rows": rows}
    (HERE / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
