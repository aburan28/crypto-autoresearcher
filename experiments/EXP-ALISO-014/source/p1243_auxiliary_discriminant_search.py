#!/usr/bin/env python3
"""Deterministic search sweep for auxiliary splitting discriminants."""

from __future__ import annotations

import hashlib
import json
import statistics
import time
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "p1243_auxiliary_discriminant_search_result.json"
CONTRACT = (
    HERE.parent.parent
    / "research"
    / "p1243_auxiliary_discriminant_search_contract_20260729.md"
)
K_VALUES = (2, 4, 6, 8, 10, 12, 14, 16)
SEEDS = (2026072901, 2026072902, 2026072903)
MAXIMUM = 100_000_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scientific_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


def component_primes(seed: int, count: int) -> list[int]:
    values = []
    index = 0
    while len(values) < count:
        digest = hashlib.sha256(f"{seed}:{index}".encode("ascii")).digest()
        index += 1
        candidate = 10_000 + int.from_bytes(digest[:8], "big") % 990_000
        prime = int(sp.nextprime(candidate))
        if prime not in values:
            values.append(prime)
    return values


def split_symbol(delta: int, prime: int) -> int:
    value = pow((-delta) % prime, (prime - 1) // 2, prime)
    if value == 1:
        return 1
    if value == prime - 1:
        return -1
    return 0


def search(primes: list[int]) -> tuple[int, int, int]:
    trials = 0
    rejected = 0
    for delta in range(7, MAXIMUM, 8):
        if not sp.isprime(delta) or delta in primes:
            continue
        trials += 1
        symbols = [split_symbol(delta, prime) for prime in primes]
        if all(symbol == 1 for symbol in symbols):
            return delta, trials, rejected
        rejected += 1
    raise RuntimeError("auxiliary discriminant search bound exceeded")


def run_row(k: int, seed: int) -> dict:
    primes = component_primes(seed, k)
    delta, trials, rejected = search(primes)
    symbols = [split_symbol(delta, prime) for prime in primes]
    wrong_mod8 = delta - 4
    flipped_symbols = symbols[:]
    flipped_symbols[0] = -flipped_symbols[0]
    gates = {
        "delta_prime": bool(sp.isprime(delta)),
        "delta_mod8": delta % 8 == 7,
        "delta_coprime": delta not in primes,
        "all_symbols_split": all(symbol == 1 for symbol in symbols),
        "normalized_trials_below_bound": trials / (2**k) < 128,
    }
    mutations = {
        "wrong_mod8_rejected": wrong_mod8 % 8 != 7,
        "flipped_symbol_rejected": not all(
            symbol == 1 for symbol in flipped_symbols
        ),
        "component_prime_rejected": primes[0] in primes,
    }
    return {
        "k": k,
        "seed": seed,
        "component_primes": primes,
        "delta": delta,
        "trials": trials,
        "rejected_candidates": rejected,
        "reference_two_to_k": 2**k,
        "normalized_trials": trials / (2**k),
        "symbols": symbols,
        "gates": gates,
        "mutations": mutations,
        "pass": all(gates.values()) and all(mutations.values()),
    }


def main() -> None:
    started = time.perf_counter()
    rows = []
    for k in K_VALUES:
        selected_seeds = SEEDS if k < 16 else SEEDS[:2]
        for seed in selected_seeds:
            rows.append(run_row(k, seed))

    summaries = []
    for k in K_VALUES:
        values = [row["normalized_trials"] for row in rows if row["k"] == k]
        summaries.append(
            {
                "k": k,
                "row_count": len(values),
                "median_normalized_trials": statistics.median(values),
                "maximum_normalized_trials": max(values),
            }
        )
    scientific = {
        "claim_status": (
            "HEURISTIC SEARCH EVIDENCE / ARTIFICIAL PRIME SETS / "
            "NO LEAST-DISCRIMINANT THEOREM"
        ),
        "rows": rows,
        "summaries": summaries,
        "maximum_delta": max(row["delta"] for row in rows),
        "maximum_normalized_trials": max(
            row["normalized_trials"] for row in rows
        ),
        "all_pass": all(row["pass"] for row in rows),
    }
    result = {
        "schema": "p1243-auxiliary-discriminant-search-v2",
        **scientific,
        "runtime": {"wall_time_sec": time.perf_counter() - started},
        "artifact_hashes": {
            "contract_sha256": sha256(CONTRACT),
            "source_sha256": sha256(Path(__file__).resolve()),
        },
        "scientific_data_sha256": scientific_hash(scientific),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not scientific["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
