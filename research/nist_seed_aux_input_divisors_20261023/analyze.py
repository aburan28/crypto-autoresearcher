"""Exact divisor-opportunity screen from already verified n±1 factorizations."""
from __future__ import annotations

import hashlib
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CURVES = ROOT / "research/nist_seed_skipped_curves_20261016"
SOURCE = ROOT / "research/nist_seed_order_certificate_20261023/runs/certificate-20261023T1747Z"
CAP = 2_000_000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def factors(path: Path) -> list[tuple[int, int]]:
    lines = path.read_text().strip().splitlines()
    assert lines[0].startswith("COUNT=") and lines[-1] == "DONE"
    out = [tuple(map(int, line.split(","))) for line in lines[1:-1]]
    assert len(out) == int(lines[0].split("=", 1)[1])
    assert all(p > 1 and e > 0 for p, e in out)
    assert [p for p, _ in out] == sorted(set(p for p, _ in out))
    return out


def divisors(fs: list[tuple[int, int]]) -> list[int]:
    out = [1]
    for p, e in fs:
        powers = [p**k for k in range(e + 1)]
        assert len(out) * len(powers) <= CAP, "divisor cap reached"
        out = [d * pk for d in out for pk in powers]
    return sorted(out)


def icbrt(n: int) -> int:
    assert n >= 0
    lo, hi = 0, 1 << ((n.bit_length() + 2) // 3 + 1)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**3 <= n:
            lo = mid
        else:
            hi = mid
    assert lo**3 <= n < (lo + 1) ** 3
    return lo


def max_le(values: list[int], bound: int) -> int:
    import bisect

    j = bisect.bisect_right(values, bound)
    assert j > 0
    return values[j - 1]


def verify_product(fs: list[tuple[int, int]], expected: int) -> None:
    product = 1
    for p, e in fs:
        product *= p**e
    assert product == expected, (product, expected)


def control() -> dict:
    assert icbrt(101) == 4 and isqrt(101) == 10
    minus = divisors([(2, 2), (5, 2)])
    plus = divisors([(2, 1), (3, 1), (17, 1)])
    assert minus == [d for d in range(1, 101) if 100 % d == 0]
    assert plus == [d for d in range(1, 103) if 102 % d == 0]
    assert max_le(minus, isqrt(101)) == 10
    assert max_le(plus, icbrt(101)) == 3
    for fs, wrong in (([(2, 2), (5, 2)], 101), ([(2, 2), (5, 1)], 100)):
        try:
            verify_product(fs, wrong)
        except AssertionError:
            pass
        else:
            raise AssertionError("injected wrong order or factor passed")
    return {"n": 101, "minus_divisors": minus, "plus_divisors": plus,
            "max_minus_sqrt": 10, "max_plus_cuberoot": 3,
            "wrong_order_and_factor_rejected": True}


def main() -> None:
    assert (SOURCE / "complete.ok").read_text() == "verified\n"
    verified = json.loads((SOURCE / "verification.json").read_text())
    vrows = [r for r in verified["rows"] if r["label"] != "control"]
    assert len(vrows) == 38 and all(r["status"] == "verified" for r in vrows)
    assessed = json.loads((CURVES / "assessed.json").read_text())
    traits = json.loads((CURVES / "traits.json").read_text())
    entries = [("omitted", r) for r in assessed["candidate_rows"]]
    entries += [("published", r) for r in traits["published_controls"].values()
                if r["identity"]["field"]["characteristic"].bit_length() in (192, 224, 239, 256)]
    assert len(entries) == 19
    by_uid = {r["identity"]["curve_uid"]: (label, r) for label, r in entries}
    assert len(by_uid) == 19
    rows = []
    for receipt in vrows:
        label, curve = by_uid[receipt["curve_uid"]]
        assert label == receipt["label"]
        n = int(curve["n_hex"], 16)
        direction = "minus" if receipt["name"].endswith("_minus") else "plus"
        fpath = SOURCE / f"{receipt['name']}.stdout"
        fs = factors(fpath)
        assert len(fs) == receipt["factor_count"]
        verify_product(fs, n - 1 if direction == "minus" else n + 1)
        ds = divisors(fs)
        bound = isqrt(n) if direction == "minus" else icbrt(n)
        best = max_le(ds, bound)
        assert (n - 1 if direction == "minus" else n + 1) % best == 0
        row = {"name": receipt["name"], "label": label,
               "curve_uid": receipt["curve_uid"], "field_bits": int(curve["p_hex"], 16).bit_length(),
               "seed_ordinal_one_based": curve["seed_ordinal_one_based"],
               "direction": direction, "n": str(n), "source_sha256": sha(fpath),
               "factor_count": len(fs), "divisor_count": len(ds),
               "bound": str(bound), "largest_divisor_at_bound": str(best),
               "gap_numerator": str(bound), "gap_denominator": str(best)}
        if direction == "plus":
            row["largest_divisor_at_1024"] = str(max_le(ds, 1024))
        rows.append(row)
    assert len(rows) == 38
    metrics = {}
    for direction, metric in (("minus", "gap"), ("plus", "gap"), ("plus", "largest_divisor_at_1024")):
        selected = [r for r in rows if r["direction"] == direction]
        better = ties = worse = 0
        counterexamples = []
        for field in (192, 224, 239, 256):
            skips = [r for r in selected if r["field_bits"] == field and r["label"] == "omitted"]
            pubs = [r for r in selected if r["field_bits"] == field and r["label"] == "published"]
            for s in skips:
                for p in pubs:
                    if metric == "gap":
                        cmp = int(s["gap_numerator"]) * int(p["gap_denominator"]) - int(p["gap_numerator"]) * int(s["gap_denominator"])
                        cmp = -cmp  # smaller gap is more favorable
                    else:
                        cmp = int(s[metric]) - int(p[metric])
                    if cmp > 0:
                        better += 1
                    elif cmp < 0:
                        worse += 1
                        counterexamples.append([s["name"], p["name"]])
                    else:
                        ties += 1
        assert better + ties + worse == 25
        metrics[f"{direction}_{metric}"] = {"omitted_more_favorable_pairs": better,
                                            "ties": ties, "published_more_favorable_pairs": worse,
                                            "counterexamples": counterexamples[:5]}
    output = {"schema": "nist-seed-auxiliary-divisor-screen/v1", "scope": "19 same-field curves, 38 complete order-neighbor factorizations",
              "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in (CURVES / "assessed.json", CURVES / "traits.json", SOURCE / "verification.json")},
              "control": control(), "rows": rows, "pair_comparisons": metrics,
              "ordinary_ecdlp_auxiliary_inputs_observed": False,
              "historical_1997_cheons_algorithm_documented": False}
    (HERE / "analysis.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
