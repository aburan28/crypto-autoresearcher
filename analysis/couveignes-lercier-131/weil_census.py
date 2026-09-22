#!/usr/bin/env python3
"""Is there a commutative algebraic group over F_2 with a rational point of order 131?

Background. Couveignes-Lercier build Galois-invariant subsets of F_{q^n} from a
commutative algebraic group G/F_q carrying a rational subgroup T of order exactly
n, via the quotient isogeny G -> G/T; Galbraith-Granger-Merz-Petit section 4.2
turns those into Frobenius-invariant factor bases for index calculus on subfield
curves. The two instantiations written down need a one-dimensional group:

  * dimension-1 torus     -- needs n | q + 1
  * elliptic curve H/F_q  -- needs n to have a squarefree multiple N with
                             N != 1 mod p and q + 1 - 2 sqrt q < N < q + 1 + 2 sqrt q

For a binary Koblitz curve the acting Frobenius is the 2-power one, so q = 2 is
forced and n = 131. Both conditions then fail on integers alone: q + 1 = 3, and
the Hasse interval at q = 2 is (0.17, 5.83) so N <= 5. No computation needed.

What this script does. It probes the CONJECTURAL extension -- Couveignes-Lercier
suggest other commutative groups may contribute -- by asking whether ANY abelian
variety over F_2 of small dimension has 131 dividing its point count. An abelian
variety of dimension g over F_q has

    #A(F_q) = P(1) = h(q + 1)

where P is its characteristic polynomial of Frobenius, degree 2g, and h is the
degree-g REAL Weil polynomial whose roots are beta_i = alpha_i + q/alpha_i, real
and in [-2 sqrt q, 2 sqrt q]. Isogeny classes correspond to such P (Honda-Tate,
Tate), and the substitution P(T) = T^g h(T + q/T) is a bijection onto integer h,
so enumerating integer real-rooted h in the box enumerates the classes.

HONEST STATUS, AND IT IS WHY THE COMPANION KNOWLEDGE ENTRY IS AN OPEN PROBLEM
RATHER THAN A FINDING. The enumerator below reproduces the known isogeny-class
count EXACTLY at g = 1 (5) and g = 2 (35), and finds 211 at g = 3 where LMFDB
lists 215. Four classes at g = 3 are unaccounted for. Numerical root-finding on
a degree-3 polynomial with a repeated root at the boundary +-2 sqrt 2 is the
suspected cause and is NOT fixed here. So a zero at g = 3 and g = 4 is
"no candidate found by an enumerator with a known 4-class gap", never a proof.

exact_targets.py removes that dependence for the question actually asked: it
enumerates only the h whose point count is a multiple of the modulus and decides
real-rootedness exactly, so its zero does not rest on this script's gap. Read the
two together -- this one for the validation counts and the point-count ranges,
that one for the exclusion.

Run: python3 weil_census.py [--max-dim 4] [--modulus 131] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import math
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    sys.exit("needs numpy")

Q = 2
BOX = 2 * math.sqrt(Q)          # |beta_i| <= 2 sqrt q
# Known isogeny-class counts of abelian varieties over F_2, for validation.
# g = 1, 2 from the classical tables; g = 3 from the LMFDB isogeny-class search
# https://www.lmfdb.org/Variety/Abelian/Fq/?q=2&g=3 which reported 215 matches
# when this script was written. RELAYED, not recomputed here.
KNOWN_CLASS_COUNTS = {1: 5, 2: 35, 3: 215}


def real_rooted_in_box(coeffs: list[int]) -> bool:
    """All roots real and within [-2 sqrt q, 2 sqrt q]."""
    roots = np.roots(coeffs)
    if np.max(np.abs(roots.imag)) > 1e-7:
        return False
    return bool(np.max(np.abs(roots.real)) <= BOX + 1e-9)


def census(g: int, modulus: int | None) -> dict:
    """Enumerate integer real Weil polynomials of degree g over F_2.

    Coefficients are chosen top-down and pruned by Rolle: if h is real-rooted in
    the box then so is every derivative, and each derivative of order g - k
    depends only on a_0..a_k, so a partial choice that fails is abandoned early.
    """
    found: list[tuple[int, list[int]]] = []
    hits: list[tuple[int, list[int]]] = []
    # |a_k| <= C(g, k) * BOX^k, the bound on the k-th elementary symmetric
    # function of g reals of modulus at most BOX
    bounds = [math.comb(g, k) * BOX ** k for k in range(g + 1)]

    def recurse(k: int, chosen: list[int]) -> None:
        limit = int(bounds[k]) + 1
        for a_k in range(-limit, limit + 1):
            partial = chosen + [a_k]
            derivative = [
                partial[i] * math.factorial(g - i) // math.factorial(k - i)
                for i in range(k + 1)
            ]
            if not real_rooted_in_box(derivative):
                continue
            if k == g:
                points = sum(c * (Q + 1) ** (g - i) for i, c in enumerate(partial))
                if points > 0:
                    found.append((points, partial))
                    if modulus is not None and points % modulus == 0:
                        hits.append((points, partial))
            else:
                recurse(k + 1, partial)

    recurse(1, [1])
    counts = sorted({p for p, _ in found})
    return {
        "dimension": g,
        "classes_found": len(found),
        "classes_known": KNOWN_CLASS_COUNTS.get(g),
        "validates": (len(found) == KNOWN_CLASS_COUNTS[g]) if g in KNOWN_CLASS_COUNTS else None,
        "max_points": max(counts) if counts else 0,
        "weil_upper_bound": round((1 + math.sqrt(Q)) ** (2 * g), 2),
        "multiples_of_modulus_in_range": (
            [] if modulus is None else
            [k for k in range(modulus, (max(counts) if counts else 0) + 1, modulus)]
        ),
        "hits": [{"points": p, "h": h} for p, h in hits],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-dim", type=int, default=4)
    ap.add_argument("--modulus", type=int, default=131)
    ap.add_argument("--json", type=str, default=None)
    args = ap.parse_args()

    report = {
        "base_field": Q,
        "modulus": args.modulus,
        "written_constructions_at_n_131_over_F2": {
            "dimension_1_torus": {
                "condition": "n divides q + 1",
                "value": f"q + 1 = {Q + 1}",
                "admits_131": (Q + 1) % 131 == 0,
            },
            "elliptic_curve": {
                "condition": "n has a squarefree multiple N in the Hasse interval",
                "hasse_interval": [round(Q + 1 - 2 * math.sqrt(Q), 4),
                                   round(Q + 1 + 2 * math.sqrt(Q), 4)],
                "largest_admissible_N": math.floor(Q + 1 + 2 * math.sqrt(Q)),
                "admits_131": 131 <= math.floor(Q + 1 + 2 * math.sqrt(Q)),
            },
        },
        "census": [],
    }
    for g in range(1, args.max_dim + 1):
        row = census(g, args.modulus)
        report["census"].append(row)
        flag = "" if row["validates"] is None else (
            "  [validates]" if row["validates"] else
            f"  [GAP: {row['classes_known'] - row['classes_found']} classes unaccounted]"
        )
        print(
            f"g={g}: {row['classes_found']} classes"
            + (f" (known {row['classes_known']})" if row["classes_known"] else "")
            + f" | max #A(F_2) = {row['max_points']}"
            + f" (Weil bound {row['weil_upper_bound']})"
            + f" | multiples of {args.modulus} in range: {row['multiples_of_modulus_in_range']}"
            + f" | found: {len(row['hits'])}"
            + flag,
            flush=True,
        )
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
