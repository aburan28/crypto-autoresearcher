"""Recheck the bounded traits and published controls discussed in the addendum.

This reads the frozen reconstruction records. It does not rerun point counting
or infer the historical acceptance rule. Run with Python 3 and PARI/GP. Supply
the original sheet to reproduce its row-by-row comparison:

    python3 supplemental_checks.py --sheet /path/to/supplied-sheet.txt > supplemental_checks.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
LIMIT = 1_000_000
SUPPLIED_SHEET_SHA256 = (
    "4076201e051737c9c7086ed577ddfb7912d0c729611b5a67f153e53d80765f34"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_embedding_degree_at_most(p: int, n: int, limit: int) -> int | None:
    power = 1
    reduced_p = p % n
    for k in range(1, limit + 1):
        power = (power * reduced_p) % n
        if power == 1:
            return k
    return None


def small_prime_factors(value: int, limit: int) -> list[int]:
    factors = []
    remaining = abs(value)
    for candidate in range(2, limit + 1):
        if candidate > remaining:
            break
        while remaining % candidate == 0:
            factors.append(candidate)
            remaining //= candidate
    return factors


def gp_isprime(value: int) -> bool:
    result = subprocess.run(
        ["gp", "-q"],
        input=f"print(isprime({value}))\n\\q\n",
        text=True,
        capture_output=True,
        check=True,
        timeout=120,
    )
    answer = result.stdout.strip()
    if answer not in {"0", "1"}:
        raise RuntimeError(f"unexpected GP primality result: {answer!r}")
    return answer == "1"


def compare_supplied_sheet(
    path: Path, published: dict, skipped: list[dict]
) -> dict:
    source_hash = sha256(path)
    if source_hash != SUPPLIED_SHEET_SHA256:
        raise ValueError(f"sheet SHA-256 differs: {source_hash}")
    source = path.read_text()
    heads = list(
        re.finditer(
            r"(?m)^([^\n]+?) - (PUBLISHED|REJECTED \(no known reason\))\s*$",
            source,
        )
    )
    if len(heads) != 21:
        raise ValueError(f"expected 21 per-curve sections, found {len(heads)}")
    published_aliases = {
        "P-192 (prime192v1)": "prime192v1",
        "P-256 (prime256v1)": "prime256v1",
        "P-224": "secp224r1",
        "P-384": "secp384r1",
        "P-521": "secp521r1",
    }
    exceptions = []
    factor_list_mismatches = []
    exact = 0
    equivalent_sign = 0
    for index, head in enumerate(heads):
        title = head.group(1)
        end = heads[index + 1].start() if index + 1 < len(heads) else source.index("4. Findings")
        body = source[head.end() : end]
        if head.group(2) == "PUBLISHED":
            row = published[published_aliases.get(title, title)]
        else:
            ordinal = int(re.search(r"#(\d+)", title).group(1))
            timestamp = int(re.search(r"srand48\((\d+)\)", body).group(1))
            row = next(
                item
                for item in skipped
                if item["seed_ordinal_one_based"] == ordinal
                and item["timestamp"] == timestamp
            )
        p = int(row["p_hex"], 16)
        n = int(row["n_hex"], 16)
        trace = p + 1 - n
        twist = 2 * (p + 1) - n
        expected = {
            "seed": int(row["seed_hex"], 16),
            "p": p,
            "b": int(row["b_hex"], 16),
            "n_hex": n,
            "n_decimal": n,
            "trace": trace,
            "twist_order": twist,
        }
        patterns = {
            "seed": (r"Seed \(160-bit SHA-1 input\):\s*([0-9a-fA-F]+)", 16),
            "p": (r"p \(\d+ bits\):\s*([0-9a-fA-F]+)", 16),
            "b": (r"b \(derived\):\s*([0-9a-fA-F]+)", 16),
            "n_hex": (r"n \(hex\):\s*([0-9a-fA-F]+)", 16),
            "n_decimal": (r"n \(\d+ bits, decimal\):\s*([\d\s]+?)\s*n \(hex\)", 10),
            "trace": (r"Trace t = p\+1-n:\s*([+-]?\d+)", 10),
            "twist_order": (r"Twist order 2p\+2-n \(\d+ bits\):\s*([+-]?[\d\s]+?)\s*Twist:", 10),
        }
        deviations = {}
        sign_equivalent = False
        for field, (pattern, base) in patterns.items():
            match = re.search(pattern, body)
            if match is None:
                raise ValueError(f"could not parse {field} in {title}")
            observed = int("".join(match.group(1).split()), base)
            if observed == expected[field]:
                continue
            if field == "b" and p % 4 == 1 and observed == (-expected[field]) % p:
                sign_equivalent = True
                deviations[field] = "opposite isomorphic sign"
            else:
                deviations[field] = {
                    "sheet": str(observed),
                    "verified": str(expected[field]),
                }
        if deviations:
            exceptions.append({"curve": title, "fields": deviations})
        if sign_equivalent:
            equivalent_sign += 1
        elif not deviations:
            exact += 1

        expected_factors = {
            "discriminant": trace * trace - 4 * p,
            "n_minus_one": n - 1,
            "twist_minus_one": twist - 1,
        }
        factor_patterns = {
            "discriminant": r"small prime factors:\s*([^\n]*)",
            "n_minus_one": r"n-1 small factors:\s*([^\n]*)",
            "twist_minus_one": r"twist-1 small factors:\s*([^\n]*)",
        }
        for field, pattern in factor_patterns.items():
            match = re.search(pattern, body)
            if match is None:
                raise ValueError(f"could not parse {field} factors in {title}")
            stated = match.group(1).strip()
            listed = [] if stated.startswith(("none", "-")) else [
                int(value) for value in re.findall(r"\d+", stated)
            ]
            calculated = small_prime_factors(expected_factors[field], 100_000)
            if listed != calculated:
                factor_list_mismatches.append(
                    {"curve": title, "field": field, "sheet": listed, "verified": calculated}
                )

    dates = {}
    for timestamp_text, stated in re.findall(
        r"(?m)^(\d{9}) (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d UTC)", source
    ):
        timestamp = int(timestamp_text)
        expected = datetime.fromtimestamp(timestamp, timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
        dates[timestamp_text] = {"sheet": stated, "verified": expected, "match": stated == expected}
    if len(dates) != 6:
        raise ValueError(f"expected 6 timestamp conversions, found {len(dates)}")

    return {
        "rows_checked": len(heads),
        "exact_rows": exact,
        "rows_with_isomorphic_opposite_sign": equivalent_sign,
        "rows_with_incorrect_fields": len(heads) - exact - equivalent_sign,
        "row_exceptions": exceptions,
        "small_factor_lists_checked_to": 100_000,
        "small_factor_list_mismatches": factor_list_mismatches,
        "timestamp_conversions": dates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, help="original supplied sheet, checked by SHA-256")
    args = parser.parse_args()
    raw_path = HERE / "traits.json"
    assessed_path = HERE / "assessed.json"
    raw = json.loads(raw_path.read_text())
    assessed = json.loads(assessed_path.read_text())
    published = raw["published_controls"]
    skipped = assessed["candidate_rows"]
    assert len(published) == 10 and len(skipped) == 11

    rows = list(published.items()) + [
        (f"skip-{row['timestamp']}-{row['seed_ordinal_one_based']}", row)
        for row in skipped
    ]
    embedding = {}
    for name, row in rows:
        p = int(row["p_hex"], 16)
        n = int(row["n_hex"], 16)
        embedding[name] = first_embedding_degree_at_most(p, n, LIMIT)

    p521 = published["secp521r1"]
    p521_p = int(p521["p_hex"], 16)
    p521_n = int(p521["n_hex"], 16)
    p521_trace = p521_p + 1 - p521_n
    p521_twist = 2 * (p521_p + 1) - p521_n
    assert p521_p == 2**521 - 1
    assert p521_trace * p521_trace < 4 * p521_p
    p384 = published["secp384r1"]
    p384_twist = 2 * (int(p384["p_hex"], 16) + 1) - int(p384["n_hex"], 16)

    timestamps = sorted({row["timestamp"] for _, row in rows})
    result = {
        "source": {
            "supplied_trait_sheet_title": "NIST/ANSI Pseudorandom Prime Curves Complete Trait Analysis",
            "supplied_trait_sheet_sha256": SUPPLIED_SHEET_SHA256,
            "traits_json_sha256": sha256(raw_path),
            "assessed_json_sha256": sha256(assessed_path),
            "script_sha256": sha256(Path(__file__)),
        },
        "counts": {
            "published_controls": len(published),
            "skipped_candidates": len(skipped),
            "total": len(rows),
        },
        "timestamps_utc": {
            str(timestamp): datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
            for timestamp in timestamps
        },
        "embedding_degree_screen": {
            "limit_inclusive": LIMIT,
            "method": "successive modular multiplication of p modulo prime order n",
            "first_k_at_most_limit_or_null": embedding,
            "all_21_greater_than_limit": all(value is None for value in embedding.values()),
        },
        "published_control_corrections": {
            "prime192v2_b_hex": published["prime192v2"]["b_hex"],
            "secp384r1_twist_prime_gp_isprime": gp_isprime(p384_twist),
            "secp521r1": {
                "p_hex": p521["p_hex"],
                "p_bits": p521_p.bit_length(),
                "trace_decimal": str(p521_trace),
                "twist_order_decimal": str(p521_twist),
                "twist_order_bits": p521_twist.bit_length(),
                "twist_prime_gp_isprime": gp_isprime(p521_twist),
                "twist_small_prime_factors_at_most_100000": small_prime_factors(
                    p521_twist, 100_000
                ),
                "frobenius_discriminant_small_prime_factors_at_most_100000": small_prime_factors(
                    p521_trace * p521_trace - 4 * p521_p, 100_000
                ),
            },
        },
    }
    if args.sheet is not None:
        result["supplied_sheet_comparison"] = compare_supplied_sheet(
            args.sheet, published, skipped
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
