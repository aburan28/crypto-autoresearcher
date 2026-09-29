"""Seeded deterministic draws, per this contract's
`census_procedure.k_gte_2_sampled_members` domain-string SHA256 rule,
generalising EXP-MONO-4c7479's `random_quartic_control_seed_rule` rejection
sampling to F_{p^k} coefficient tuples.

msg = domain || "|coord|" || decimal(p) || "|" || decimal(k) || "|" ||
      decimal(j) || "|" || decimal(coord_index) || "|" || decimal(coeff_index)
      || "|" || decimal(counter)
val = int(SHA256(msg), big-endian)
accept iff val < floor(2^256/p)*p; else counter += 1 and redraw.
"""
from __future__ import annotations

import hashlib


def draw_coeff(domain: str, p: int, k: int, j: int, coord_index: int, coeff_index: int):
    threshold = (2 ** 256 // p) * p
    counter = 0
    rejections = 0
    while True:
        msg = f"{domain}|coord|{p}|{k}|{j}|{coord_index}|{coeff_index}|{counter}".encode("ascii")
        digest = hashlib.sha256(msg).digest()
        val = int.from_bytes(digest, "big")
        if val < threshold:
            return val % p, rejections
        counter += 1
        rejections += 1


def draw_field_element(domain: str, p: int, k: int, j: int, coord_index: int):
    """Draw one uniformly random element of F_{p^k} (a k-tuple), for draw
    index j and base-coordinate index `coord_index` (0 for a 1-D base like
    N2/N2-twin/e; 0 or 1 for N1's 2-D base e1,e2)."""
    coeffs = []
    total_rej = 0
    for ci in range(k):
        v, rej = draw_coeff(domain, p, k, j, coord_index, ci)
        coeffs.append(v)
        total_rej += rej
    return tuple(coeffs), total_rej


class DeterministicFieldRNG:
    """A deterministic, reproducible generator of F_{p^k} elements for
    Cantor-Zassenhaus root-splitting (N4), seeded via the same SHA256
    domain-string family (a dedicated `coord_index` string), so no
    hidden/undeclared randomness source is introduced."""

    def __init__(self, domain: str, p: int, k: int, tag: str):
        self.domain = domain + "|" + tag
        self.p = p
        self.k = k
        self.j = 0

    def __iter__(self):
        return self

    def __next__(self):
        val, _ = draw_field_element(self.domain, self.p, self.k, self.j, 0)
        self.j += 1
        return val
