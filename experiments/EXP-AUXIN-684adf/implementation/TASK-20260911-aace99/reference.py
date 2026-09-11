"""Independently structured full-domain reference; it never imports crt."""
from __future__ import annotations

def full_domain(n: int, pairs: list[tuple[int,int]], counters: dict | None = None) -> list[int]:
    answer=[]
    for exponent in range(n):
        ok=True
        for residue, modulus in pairs:
            if counters is not None: counters["residue_tests"] = counters.get("residue_tests",0)+1
            if exponent % modulus != residue: ok=False; break
        if ok: answer.append(exponent)
    return answer

def scalar_matches(zeta: int, prime: int, exponents: list[int], truth: int, counters: dict | None=None) -> dict:
    matches=[]
    for index, exponent in enumerate(exponents):
        if counters is not None: counters["pow_calls"] = counters.get("pow_calls",0)+1; counters["scalar_equalities"] = counters.get("scalar_equalities",0)+1
        if pow(zeta, exponent, prime) == truth: matches.append(index)
    return {"match_count":len(matches),"first_match_index":matches[0] if matches else None}

def compare(reference: list[int], producer: list[int]) -> dict:
    duplicate = len(producer) != len(set(producer))
    ro, po = sorted(set(reference)-set(producer)), sorted(set(producer)-set(reference))
    return {"equal":not duplicate and not ro and not po and producer == sorted(producer),"duplicate_producer":duplicate,"reference_only":ro,"producer_only":po}
