#!/usr/bin/env python3
"""
Independent re-derivation of PREREG-7 Stage A (the exact Compress_d fibre
census over Z_q, q=3329) for the Validator task TASK-20260814-b13873.

Written FROM SCRATCH from FIPS 203 (NIST.FIPS.203, fetched independently by
this validator session from https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf,
sha256 fe1f12f32a7e44ec9fdebbf400cda843a40b506dee676725234dc6f7923b6cac,
extracted with pdftotext -layout) -- section 2.3 (rounding operator) and
section 4.2.1 (Compress/Decompress), WITHOUT importing or reading
coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/tasks/TASK-20260814-c87a24/ciphertext_noise_census.py.

FIPS 203 section 2.3: "ceil(x rfloor" rounding operator (rendered here as
round_half_up): "The rounding of x to the nearest integer. If x = y + 1/2
for some y in Z, then round(x) = y + 1." I.e. floor(x + 1/2) -- ties go up.

FIPS 203 section 4.2.1, eq (4.7)/(4.8):
    Compress_d : Z_q -> Z_{2^d},   x |-> round((2^d/q) * x) mod 2^d
    Decompress_d : Z_{2^d} -> Z_q, y |-> round((q/2^d) * y)
"Division and rounding ... performed in the set of rational numbers.
Floating-point computations shall not be used." -- honoured here via
fractions.Fraction exclusively; no float appears anywhere in this script.
"""
from fractions import Fraction
from collections import Counter
import json
import sys

Q = 3329


def round_half_up(v: Fraction) -> int:
    """floor(v + 1/2); ties (v = y + 1/2) round to y+1, per FIPS 203 sec 2.3."""
    return (v + Fraction(1, 2)).__floor__()


def compress(x: int, d: int) -> int:
    """FIPS 203 eq (4.7) states 'For d < 12, define Compress_d ...' -- the
    formula is formally scoped to d < 12 only; FIPS 203's own treatment of
    d=12 is a DIFFERENT mechanism (ByteEncode12/ByteDecode12, direct
    integer-mod-q encoding using 12 bits, not a compression map) documented
    separately in section 4.2.1. PREREG-7 section 2.3 point 1 and the
    producer's own ciphertext_noise_census.py both apply THIS SAME formula
    at d=12 anyway, as a natural extension (not itself in FIPS 203's own
    Compress_d domain) -- this validator reproduces that same extension
    (matching what is actually being measured) but FLAGS the scope
    discrepancy explicitly rather than silently endorsing it as an FIPS
    203-literal Compress_12. Mathematically the extension is well-defined
    for any d, and (checked below) happens to be injective at d=12 because
    2^12=4096 > q=3329, so the qualitative claim (every fibre a singleton at
    that extension) still holds -- but it is not, strictly, 'FIPS 203's own
    Compress_12', because FIPS 203 does not define that function at all."""
    assert 0 <= x < Q
    val = Fraction(2 ** d, Q) * x
    return round_half_up(val) % (2 ** d)


def decompress(y: int, d: int) -> int:
    val = Fraction(Q, 2 ** d) * y
    return round_half_up(val)
    # FIPS 203 eq (4.8) states Decompress_d(y) = round((q/2^d)*y) with no
    # explicit "mod q" in the formula; its stated codomain is Z_q. Checked
    # empirically below (see decompress_range_check) that round((q/2^d)*y)
    # never leaves [0, q-1] for y in [0, 2^d-1] on this domain, so applying
    # or omitting a mod-q reduction makes no observable difference here.


def census(d: int):
    fibres = {}
    for x in range(Q):
        y = compress(x, d)
        fibres.setdefault(y, []).append(x)
    hist = Counter(len(v) for v in fibres.values())
    return fibres, dict(sorted(hist.items()))


def main():
    out = {}
    out["fips203_scope_finding"] = (
        "FIPS 203 eq (4.7) restricts Compress_d/Decompress_d to 'd < 12' "
        "literally. d=12 in FIPS 203 is handled by a DIFFERENT mechanism "
        "(ByteEncode12/ByteDecode12), not by extending Compress_d/"
        "Decompress_d. PREREG-7 sec 2.3(1) and the producer's own script "
        "both apply the SAME Compress_d/Decompress_d formula at d=12 "
        "anyway (an extrapolation past FIPS 203's own stated domain, not "
        "an error in arithmetic) -- this is reported as a naming/scope "
        "finding, not a defect, since (checked below) the extension is "
        "well-defined and the claimed properties (singleton fibres, exact "
        "roundtrip) hold for it regardless."
    )
    decompress_out_of_range = []
    for d in (4, 5, 10, 11, 12):
        for y in range(2 ** d):
            r = decompress(y, d)
            if not (0 <= r < Q):
                decompress_out_of_range.append((d, y, r))
    out["decompress_range_check"] = {
        "checked_all_y_for_d_in_4_5_10_11_12": True,
        "out_of_range_count": len(decompress_out_of_range),
        "examples": decompress_out_of_range[:5],
    }
    for d in (4, 5, 10, 11, 12):
        fibres, hist = census(d)
        num_codewords = 2 ** d
        out[d] = {
            "d": d,
            "num_codewords_2pow_d": num_codewords,
            "num_fibres_populated": len(fibres),
            "fibre_size_histogram": hist,
            "sum_check": sum(k * v for k, v in hist.items()),
        }
        assert out[d]["sum_check"] == Q, f"sum check failed at d={d}"

    # d_u = 11 roundtrip check
    fibres11, _ = census(11)
    singleton_residues_11 = sorted(
        v[0] for v in fibres11.values() if len(v) == 1
    )
    doublet_fibres_11 = [v for v in fibres11.values() if len(v) == 2]
    total_roundtrip_matches = 0
    singleton_mismatches = 0
    for x in range(Q):
        y = compress(x, 11)
        if decompress(y, 11) == x:
            total_roundtrip_matches += 1
    for x in singleton_residues_11:
        y = compress(x, 11)
        if decompress(y, 11) != x:
            singleton_mismatches += 1

    out["d11_roundtrip"] = {
        "total_roundtrip_matches": total_roundtrip_matches,
        "total_residues": Q,
        "singleton_fibre_count": len(singleton_residues_11),
        "doublet_fibre_count": len(doublet_fibres_11),
        "singleton_mismatches": singleton_mismatches,
    }

    # d=12 gate
    fibres12, hist12 = census(12)
    every_singleton = all(len(v) == 1 for v in fibres12.values())
    # delta(x) = x - Decompress_12(Compress_12(x)); if every fibre is a
    # singleton, delta is identically 0 (Compress_12 then Decompress_12 must
    # recover x exactly, since the fibre map is injective and a bijection on
    # its image at this domain size 2^12=4096 > q=3329).
    deltas12 = set()
    for x in range(Q):
        y = compress(x, 12)
        d12 = x - decompress(y, 12)
        deltas12.add(d12)
    out["d12_gate"] = {
        "every_fibre_singleton": every_singleton,
        "delta_set": sorted(deltas12),
        "delta_identically_zero": deltas12 == {0},
        "I_delta_bin_forced_zero_because_delta_constant": deltas12 == {0},
    }

    # F(a) / F(d) falsification reads
    hist10 = out[10]["fibre_size_histogram"]
    hist11 = out[11]["fibre_size_histogram"]
    F_a = (
        hist11.get(1) == 767
        and hist11.get(2) == 1281
        and hist10.get(3) == 767
        and hist10.get(4) == 257
    )
    F_d = out["d12_gate"]["every_fibre_singleton"] and out["d12_gate"][
        "delta_identically_zero"
    ]
    out["falsification"] = {"F_a_clears": F_a, "F_d_clears": F_d}

    print(json.dumps(out, indent=2, default=str))
    return out


if __name__ == "__main__":
    main()
