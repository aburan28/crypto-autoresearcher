"""SHA256 seed labels (AMD-20260926-3479cf C-1, C-2, C-5, C-6, C-8).

Frozen namespace: ``EXP-SDEG-85eefd/v2``. Smoke checks use the namespace
``smoke|EXP-SDEG-85eefd/v2`` so that no frozen planted/random/rho label is
ever evaluated before the admitted run.

Label shapes (``|``-joined):
  <ns>|random_x|L<L>|<seed>|<i>                     C-2, verbatim
  <ns>|planted|L<L>|<seed>|<deck>|<j>|<k>           C-5, verbatim
  <ns>|random|L<L>|<seed>|<deck>|<j>                C-5 '.../random|...' (literal reading)
  <ns>|rho|L<L>|<seed>|<t>                          C-8 '.../rho|...' (literal reading)
  <ns>|rho_walk|L<L>|<seed>|<t>|<j>                 not in protocol (walk multipliers)
  <ns>|identity|L<L>|<seed>|<i>|<field>             not in protocol (C-3 identity tuples)
  <ns>|audit|<query_id>                             not in protocol (C-8 10% audit selection)
  <ns>|bootstrap                                    C-6, verbatim
"""

from __future__ import annotations

import hashlib

FROZEN_NS = "EXP-SDEG-85eefd/v2"
SMOKE_NS = "smoke|EXP-SDEG-85eefd/v2"


class RejectionFailure(RuntimeError):
    """A single-label uniform draw fell in the rejection zone (prob < n / 2^256)."""


def h(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def lab(ns: str, kind: str, *parts) -> str:
    return "|".join([ns, kind] + [str(x) for x in parts])


def cell_lab(ns: str, kind: str, L: int, seed: int, *rest) -> str:
    return lab(ns, kind, f"L{L}", seed, *rest)


def uniform(label: str, n: int) -> int:
    """Uniform integer in [0, n) by rejection sampling on one SHA256 value."""
    v = h(label)
    limit = ((1 << 256) // n) * n
    if v >= limit:
        raise RejectionFailure(label)
    return v % n


def rng_seed(label: str) -> int:
    """64-bit seed for numpy.random.Generator(PCG64) from a label (bootstrap)."""
    return h(label) >> 192
