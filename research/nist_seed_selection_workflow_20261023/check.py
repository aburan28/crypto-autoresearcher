"""Check the published X9.62 A.3.2 gates on the archived 21 prime curves.

This does not reproduce the historical generator or its random-point routine.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
SOURCES = [ARCH / "assessed.json", ARCH / "traits.json"]


def main():
    skipped = json.loads(SOURCES[0].read_text())["candidate_rows"]
    published = json.loads(SOURCES[1].read_text())["published_controls"]
    rows = [("omitted", x) for x in skipped] + [("published", x) for x in published.values()]
    assert len(skipped) == 11 and len(published) == 10
    out = []
    for label, x in rows:
        p, n = int(x["p_hex"], 16), int(x["n_hex"], 16)
        ident = x["identity"]
        assert ident["curve"]["subgroup_order"] == n
        assert ident["curve"]["cofactor"] == 1
        assert ident["field"]["characteristic"] == p
        # For an integer n, n > 4 sqrt(p) iff n^2 > 16p.
        gates = {
            "cofactor_one": True,
            "n_gt_2pow160": n > 2**160,
            "n_gt_4sqrtp": n * n > 16 * p,
            "nonanomalous": n != p,
            "mov_B100": all(pow(p, k, n) != 1 for k in range(1, 101)),
            "order_bitlength_consistent": x["n_bits"] == n.bit_length(),
        }
        assert all(gates.values())
        out.append({"class": label, "curve_uid": ident["curve_uid"],
                    "seed_ordinal": x["seed_ordinal_one_based"],
                    "field_bits": p.bit_length(), "order_bits": n.bit_length(),
                    "gates": gates})
    obj = {
        "scope": "Archived curve/order claims checked against X9.62-1998 A.3.2 numeric gates. Prime-order certificates are inherited, not proved anew here. B=100 exceeds the standard minimum B=20.",
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},
        "rows": out,
        "counts": {label: sum(r["class"] == label for r in out) for label in ["omitted", "published"]},
    }
    target = Path(__file__).with_name("check.json")
    target.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(target)


if __name__ == "__main__":
    main()
