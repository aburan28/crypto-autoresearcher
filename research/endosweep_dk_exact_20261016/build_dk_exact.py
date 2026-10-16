#!/usr/bin/env python3
"""Exact CM discriminants of the curves whose 4q - t^2 the factoring driver finished.

Reads
  research/endosweep_dk_exact_20261016/factorizations.jsonl   (the complete factorisations)
  STD_CURVES_CHECKOUT                                          (J08nY/std-curves, commit below)
  ARK_ROOT                                                     (a directory holding arkworks/curves.json;
                                                                research/endosweep_curves_20261006 in the repo)
Writes
  dk_exact.json, dk_exact.md (next to this script)

Everything is recomputed from the curve constants: each curve is reloaded with
corpus.load_std_curves and re-verified with targets.verify (n prime, h*n in the Hasse
interval, a point killed by h*n), t = q + 1 - h*n, N = 4q - t^2.  The certificate's
factors must multiply back to N exactly and each must be proved prime by PARI isprime.
D_K and f come from nist.exact_discriminant (the odd-exponent primes give the
squarefree part s of N; D_K = -s if -s = 1 mod 4, else -4s with f halved), and the
result is re-checked independently: t^2 - 4q = D_K f^2, D_K = 0 or 1 mod 4, and D_K is
fundamental (D_K or D_K/4 squarefree with the right residue).

    nice -n 10 python3 research/endosweep_dk_exact_20261016/build_dk_exact.py \
        STD_CURVES_CHECKOUT research/endosweep_curves_20261006
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

STD_CURVES_COMMIT = "77fe6e3585ca2c2225b59d7df24b7c775437276f"
# Already certified, with the same 4q - t^2, in research/endosweep_nist_20261006/factorizations.jsonl.
EXCLUDED_NIST = {"nist/P-256": "P-256", "nist/P-384": "P-384", "nist/P-521": "P-521",
                 "other/Curve25519": "Curve25519"}

# Where each curve comes from, i.e. where its D_K might already be public.  None of this was
# checked against the literature; the std-curves column below is the only comparison made.
SOURCES = {
    "x962": "ANSI X9.62 (1998)",
    "nums": "NUMS curves, Black-Bos-Costello-Longa-Naehrig, ePrint 2014/130",
    "other/MDC201601": "Million Dollar Curve (2016)",
    "other/BADA55-R-256": "BADA55 paper, bada55.cr.yp.to (2015)",
    "other/ssc-288": "MIRACL standard curves",
    "other/ssc-512": "MIRACL standard curves",
    "gost": "TC26 GOST R 34.10-2012 parameter set C",
    "bls": "BLS12 pairing-friendly family (RELIC; ePrint 2012/232)",
    "bn": "BN pairing-friendly family",
    "arkworks": "arkworks / ZEXE pairing-friendly curves",
}


def pari():
    import cypari2
    P = cypari2.Pari()
    P.allocatemem(2 * 10 ** 8, silent=True)
    return P


_P = None


def pari_isprime(n: int) -> bool:
    """PARI isprime: a primality proof (BPSW then APR-CL/Pocklington-Lehmer), not a pseudoprime test."""
    global _P
    if _P is None:
        _P = pari()
    return bool(_P.isprime(n))


def load_curves(std: str, ark: str):
    """The verified prime-field curves of the corpus, as survey.py loads them (first name per curve)."""
    from harness.endosweep.corpus import load_std_curves
    from harness.endosweep.curvesweep import _key
    from harness.endosweep.targets import verify
    out, seen = [], set()
    for T, _, raw in load_std_curves(std) + load_std_curves(ark):
        if T is None or T.ext_degree != 1:
            continue
        verify(T)
        if not T.verified:
            continue
        T.raw = raw
        T.dup_key = _key(T)
        if T.dup_key in seen:
            T.duplicate = True
        else:
            T.duplicate = False
            seen.add(T.dup_key)
        out.append(T)
    return out


def squarefree_ok(fac) -> bool:
    return all(x == 1 for _, x in fac)


def is_fundamental_from(DK: int, odd: list[int]) -> bool:
    """D_K fundamental, given that the odd-exponent primes `odd` are distinct primes with product s."""
    s = prod(odd)
    if len(set(odd)) != len(odd):
        return False
    if DK == -s:
        return DK % 4 == 1
    if DK == -4 * s:
        return (-s) % 4 in (2, 3)
    return False


def source(name: str) -> str:
    return SOURCES.get(name) or SOURCES[name.split("/")[0]]


def build(std: str, ark: str) -> dict:
    from harness.endosweep import quadorder as QO
    from harness.endosweep.nist import exact_discriminant
    curves = load_curves(std, ark)
    by_name = {T.name: T for T in curves if not T.duplicate}
    recs = [json.loads(l) for l in open(HERE / "factorizations.jsonl") if l.strip()]
    rows = []
    for r in recs:
        T = by_name[r["curve"]]
        assert r["curve"] not in EXCLUDED_NIST
        p, n, h = T.q, T.n, T.h
        t = p + 1 - h * n
        assert t == T.trace and abs(t) <= 2 * math.isqrt(p) + 2
        N = 4 * p - t * t
        assert int(r["N"]) == N, r["curve"]
        fac = [(int(a), int(x)) for a, x in r["factors"]]
        assert fac == sorted(fac) and len({a for a, _ in fac}) == len(fac)
        assert prod(a ** x for a, x in fac) == N, r["curve"]
        assert all(pari_isprime(a) for a, _ in fac), r["curve"]
        assert len(r["found_by"]) == len(fac)
        D_frob = t * t - 4 * p
        DK, f = exact_discriminant(D_frob, fac)
        odd = [a for a, x in fac if x % 2]
        s = prod(odd)
        assert DK * f * f == D_frob and DK % 4 in (0, 1) and QO.is_discriminant(DK)
        assert is_fundamental_from(DK, odd)
        deg = QO.min_nonscalar_degree(DK)
        assert deg == (abs(DK) + DK % 2) // 4
        others = sorted(U.name for U in curves if U.dup_key == T.dup_key and U.name != T.name)
        ch = (T.raw or {}).get("characteristics") or {}
        std_cm = ch.get("cm_disc")
        std_f = ch.get("conductor")
        if std_cm is None:
            std_check = "std-curves records no cm_disc"
        else:
            ok = int(std_cm) == DK and (std_f is None or int(std_f) == f)
            std_check = (f"std-curves records cm_disc{' and conductor' if std_f is not None else ''}: "
                         f"{'agrees' if ok else 'DISAGREES'}")
            assert ok, (r["curve"], std_cm, std_f, DK, f)
        rows.append({
            "curve": r["curve"], "same_curve_as": others, "model": T.model,
            "p": str(p), "p_bits": p.bit_length(), "n": str(n), "h": h, "t": str(t),
            "N_4q_minus_t2": str(N), "N_digits": len(str(N)), "N_bits": N.bit_length(),
            "factorization": [[str(a), x] for a, x in fac], "found_by": r["found_by"],
            "squarefree_part": str(s), "squarefree_part_digits": len(str(s)),
            "conductor_f": str(f), "D_K": str(DK), "D_K_digits": len(str(abs(DK))),
            "D_K_case": "-s (s = 3 mod 4)" if DK == -s else "-4s (s = 1, 2 mod 4)",
            "log2_abs_D_K": round(math.log2(abs(DK)), 2),
            "min_nonscalar_degree": str(deg), "log2_min_nonscalar_degree": round(math.log2(deg), 2),
            "source": source(r["curve"]), "std_curves_check": std_check,
            "literature": "not checked against literature",
        })
    rows.sort(key=lambda x: (x["p_bits"], x["curve"]))
    return {
        "question": "exact D_K, conductor and least non-scalar endomorphism degree for every curve whose "
                    "4q - t^2 the factoring driver completed",
        "std_curves_commit": STD_CURVES_COMMIT,
        "std_curves_checkout_head": _git_head(std),
        "excluded_already_certified": {k: "research/endosweep_nist_20261006/factorizations.jsonl (" + v + ")"
                                       for k, v in EXCLUDED_NIST.items()},
        "primality": "PARI isprime on every factor (proof)",
        "curves": rows,
    }


def _git_head(path: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


def _fac_str(fac) -> str:
    parts = []
    for a, x in fac:
        a = str(a)
        s = a if len(a) <= 12 else f"p{len(a)}"
        parts.append(s + (f"^{x}" if x > 1 else ""))
    return " · ".join(parts)


def markdown(doc: dict) -> str:
    L = ["# Exact CM discriminants (endosweep_dk_exact_20261016)", "",
         f"std-curves commit `{doc['std_curves_commit']}`.  Every factor is proved prime by PARI `isprime`; "
         "`pN` is an N-digit prime written out in `dk_exact.json`.  No D_K here was checked against the "
         "literature (see the `std-curves` column for the one comparison made).", "",
         "| curve | p bits | t | 4q−t² digits | factorisation of 4q−t² | squarefree part s | f | D_K | log2 \\|D_K\\| "
         "| least non-scalar degree ≈ \\|D_K\\|/4 | std-curves |",
         "|:--|--:|--:|--:|:--|:--|:--|:--|--:|--:|:--|"]
    for r in doc["curves"]:
        t = r["t"] if len(r["t"]) <= 14 else f"({len(r['t'].lstrip('-'))} digits)"
        s = r["squarefree_part"] if len(r["squarefree_part"]) <= 12 else f"({r['squarefree_part_digits']} digits)"
        f = r["conductor_f"] if len(r["conductor_f"]) <= 16 else f"({len(r['conductor_f'])} digits)"
        DK = r["D_K"] if len(r["D_K"]) <= 8 else f"−({r['D_K_digits']} digits)"
        deg = r["min_nonscalar_degree"] if len(r["min_nonscalar_degree"]) <= 8 else f"2^{r['log2_min_nonscalar_degree']}"
        fac = [(a, x) for a, x in r["factorization"]]
        L.append(f"| {r['curve']} | {r['p_bits']} | {t} | {r['N_digits']} | {_fac_str(fac)} | {s} | {f} | {DK} | "
                 f"{r['log2_abs_D_K']} | {deg} | {r['std_curves_check'].replace('std-curves records ', '')} |")
    L += ["", "## Who found each factor the survey did not", "",
          "Every other factor came from the survey's `PARI factor(N, 2^32)`.  Both parts of a split carry the "
          "split's method (the found factor and its cofactor).", ""]
    for r in doc["curves"]:
        big = [(a, b) for (a, _), b in zip(r["factorization"], r["found_by"]) if not b.startswith("PARI factor(")]
        L.append(f"* **{r['curve']}**: " + "; ".join(f"{a if len(a) <= 12 else 'p' + str(len(a))} — {b}"
                                                   for a, b in big))
    L += ["", "Excluded (already certified in research/endosweep_nist_20261006/factorizations.jsonl): "
          + ", ".join(sorted(doc["excluded_already_certified"])) + ".", ""]
    return "\n".join(L)


def main(argv):
    doc = build(argv[1], argv[2])
    (HERE / "dk_exact.json").write_text(json.dumps(doc, indent=1) + "\n")
    (HERE / "dk_exact.md").write_text(markdown(doc))
    print(f"{len(doc['curves'])} curves")


if __name__ == "__main__":
    main(sys.argv)
