"""SHA256 seed labels (specification seed_rule; AMD-20260926-a7d25d C-3, C-6).

Frozen namespace: ``EXP-RELN-c5a377/v2``. Smoke checks use namespaces that
contain the word ``smoke`` (``smoke|EXP-RELN-c5a377/v2``) so that no frozen
target/attempt/rewire label is evaluated before an admitted run.

Label shapes (``|``-joined):
  <ns>|target|<bits>|<seed>                               C-3, verbatim
  <ns>|attempt|<bits>|<seed>|<j>                          C-3, verbatim; a_j, b_j are drawn
                                                          as '<label>|a' and '<label>|b'
  <ns>|rewire|<i>                                         C-6, verbatim; per-draw labels append
                                                          '|<bits>|<seed>|<budget>|<draw>'
  <ns>|er|<i>|<bits>|<seed>|<budget>|<draw>               not in protocol (ER replicate i)
  <ns>|planted|<bits>|<seed>|<budget>|<draw>              not in protocol
  <ns>|scramble|<bits>|<seed>|<budget>|<draw>             not in protocol
  <ns>|rho|<bits>|<seed>|<t>                              not in protocol (C-6 rho targets)
  <ns>|rho_walk|<bits>|<seed>|<t>|<restart>.<j><c|d>      not in protocol (walk multipliers)
  <ns>|audit|<bits>|<seed>|<j>                            not in protocol (C-6 10% selection)

Uniform draws use rejection sampling on one SHA256 value; a rejected draw
(probability < n / 2^256) retries with the suffix '|rej<r>' (r = 1, 2, ...).
"""

from __future__ import annotations

import hashlib

FROZEN_NS = "EXP-RELN-c5a377/v2"
SMOKE_NS = "smoke|EXP-RELN-c5a377/v2"


def h(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def lab(ns: str, kind: str, *parts) -> str:
    return "|".join([ns, kind] + [str(x) for x in parts])


def uniform(label: str, n: int) -> int:
    """Uniform integer in [0, n) by rejection sampling on SHA256."""
    if n <= 0:
        raise ValueError("n must be positive")
    limit = ((1 << 256) // n) * n
    v = h(label)
    r = 0
    while v >= limit:
        r += 1
        v = h(f"{label}|rej{r}")
    return v % n


def is_smoke_ns(ns: str) -> bool:
    return "smoke" in ns


def target_label(ns, bits, seed):
    return lab(ns, "target", bits, seed)


def attempt_label(ns, bits, seed, j):
    return lab(ns, "attempt", bits, seed, j)


def rewire_label(ns, i):
    return lab(ns, "rewire", i)


def audit_selected(ns, bits, seed, j) -> bool:
    """10% SHA256 selection, prefix-consistent across the A1 / A2 budgets."""
    return h(lab(ns, "audit", bits, seed, j)) % 10 == 0
