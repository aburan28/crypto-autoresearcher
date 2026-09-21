"""V1 step (1): verify the 30 shipped certificates with the validator's own
arithmetic, plus the proves-too-much control (object 1) on perturbed
certificates and the f3 evaluation at both.

Run: python3 v1_certs.py
"""

from __future__ import annotations

import glob
import json
import os
import sys

from valgf import GF2n, BinaryCurve, INF, f3_summation, parse_info

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
OUT = os.path.dirname(os.path.abspath(__file__))


def field_selftest(F: GF2n, curve: BinaryCurve, brute_count: bool):
    res = {"n": F.n, "modulus_int": F.mod, "modulus_poly": poly_str(F.mod)}
    # irreducibility: x^(2^n) == x mod f and gcd-free of lower-degree factors
    # (cheap sufficient test: the multiplicative order of a generator / the
    # standard Rabin test)
    res["rabin_irreducible"] = rabin_irreducible(F)
    res["trace_of_1"] = F.trace(1)
    # a few algebraic identities
    ok = True
    for v in (2, 3, 5, 7, 11, 1 << (F.n - 1)):
        v = v % (1 << F.n)
        if v == 0:
            continue
        ok &= F.mul(v, F.inv(v)) == 1
        ok &= F.sqr(F.sqrt(v)) == v
        ok &= F.trace(F.add(F.sqr(v), v)) == 0
    res["identities_ok"] = bool(ok)
    if brute_count:
        cnt = 1  # point at infinity
        for x in range(1 << F.n):
            cnt += len(curve.points_with_x(x))
        res["brute_force_point_count"] = cnt
    return res


def poly_str(m: int) -> str:
    terms = []
    for i in range(m.bit_length() - 1, -1, -1):
        if (m >> i) & 1:
            terms.append("1" if i == 0 else ("x" if i == 1 else f"x^{i}"))
    return " + ".join(terms)


def rabin_irreducible(F: GF2n) -> bool:
    n = F.n
    # x^(2^n) = x
    x = 2
    v = x
    for _ in range(n):
        v = F.mul(v, v)
    if v != x:
        return False
    for p in prime_factors(n):
        m = n // p
        v = x
        for _ in range(m):
            v = F.mul(v, v)
        if gcd_poly(v ^ x, F.mod) != 1:
            return False
    return True


def prime_factors(n: int):
    fs = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            fs.add(d)
            n //= d
        d += 1
    if n > 1:
        fs.add(n)
    return fs


def gcd_poly(a: int, b: int) -> int:
    while b:
        if a.bit_length() < b.bit_length():
            a, b = b, a
        a ^= b << (a.bit_length() - b.bit_length())
        if a < b:
            a, b = b, a
    return a


def decode_cert(F: GF2n, l: int, cert_raw: str, msb_first: bool):
    parts = cert_raw.split("-")
    assert len(parts) == 3, cert_raw
    conv = F.from_bits_msb_first if msb_first else F.from_bits_lsb_first
    for p in parts:
        assert len(p) == l, (cert_raw, l)
    return [conv(p) for p in parts]


def check_certificate(F, curve, xs, xr):
    """Try every choice of y for each x; report which sign combinations give
    x(P1+P2+P3) = xr."""
    pts = [curve.points_with_x(x) for x in xs]
    if any(len(p) == 0 for p in pts):
        return {"all_on_curve": False, "combinations_tried": 0, "matches": 0,
                "match_indices": []}
    tried = 0
    matches = []
    for i, P1 in enumerate(pts[0]):
        for j, P2 in enumerate(pts[1]):
            for k, P3 in enumerate(pts[2]):
                tried += 1
                S = curve.add(curve.add(P1, P2), P3)
                if S is INF:
                    continue
                if S[0] == xr:
                    matches.append((i, j, k))
    return {"all_on_curve": True, "combinations_tried": tried,
            "matches": len(matches), "match_indices": matches}


def main():
    fields = {}
    rows = []
    infos = sorted(glob.glob(os.path.join(BENCH, "INFO*.dimacs")))
    selftests = {}

    for path in infos:
        info = parse_info(path)
        n, l = info["n"], info["l"]
        key = (n, info["modulus_bits"])
        if key not in fields:
            F = GF2n(n, info["modulus_bits"])
            fields[key] = (F, BinaryCurve(F, 1, 1))
            selftests[f"n{n}"] = field_selftest(F, fields[key][1], brute_count=(n == 15))
        F, curve = fields[key]

    for path in infos:
        info = parse_info(path)
        if info["label"] != "S":
            continue
        n, l = info["n"], info["l"]
        F, curve = fields[(n, info["modulus_bits"])]
        name = os.path.basename(path)[4:-7]
        xr_lsb = F.from_bits_lsb_first(info["xr_bits"])
        xr_msb = F.from_bits_msb_first(info["xr_bits"])
        row = {"instance": name, "n": n, "l": l}
        for convname, msb in (("lsb_first", False), ("msb_first", True)):
            xs = decode_cert(F, l, info["cert_raw"], msb)
            xr = xr_msb if msb else xr_lsb
            r = check_certificate(F, curve, xs, xr)
            r["xs_hex"] = [hex(v) for v in xs]
            r["xr_hex"] = hex(xr)
            r["traces_x"] = [curve.F.trace(F.add(F.add(v, 1), F.inv(F.mul(v, v)))) if v else 0
                             for v in xs]
            r["f3"] = hex(f3_summation(F, xs[0], xs[1], xs[2], xr))
            row[convname] = r
        rows.append(row)

    # ---- proves-too-much object 1: perturb one bit of x1 ------------------
    ptm = []
    for path in infos:
        info = parse_info(path)
        if info["label"] != "S":
            continue
        n, l = info["n"], info["l"]
        F, curve = fields[(n, info["modulus_bits"])]
        name = os.path.basename(path)[4:-7]
        xr = F.from_bits_lsb_first(info["xr_bits"])
        base = decode_cert(F, l, info["cert_raw"], msb_first=False)
        per_bit = []
        for bit in range(l):
            xs = list(base)
            xs[0] ^= 1 << bit
            r = check_certificate(F, curve, xs, xr)
            per_bit.append({
                "flipped_bit": bit,
                "x1_hex": hex(xs[0]),
                "accepted": bool(r["all_on_curve"] and r["matches"] > 0),
                "x1_on_curve": bool(curve.is_x_coord(xs[0])),
                "f3_zero": f3_summation(F, xs[0], xs[1], xs[2], xr) == 0,
            })
        ptm.append({"instance": name, "per_bit": per_bit})

    # ---- proves-too-much object 1b: the five n19l6-19-U x-sets with x_R
    #      replaced by the x_R of n19l6-1-S ---------------------------------
    info19u = parse_info(os.path.join(BENCH, "INFOn19l6-19-U.dimacs"))
    info19s = parse_info(os.path.join(BENCH, "INFOn19l6-1-S.dimacs"))
    F19, curve19 = fields[(19, info19u["modulus_bits"])]
    xr_s = F19.from_bits_lsb_first(info19s["xr_bits"])
    swapped = {}
    for convname, msb in (("lsb_first", False), ("msb_first", True)):
        conv = F19.from_bits_msb_first if msb else F19.from_bits_lsb_first
        xs = [conv(b) for b in ("001010", "010001", "100101")]
        r = check_certificate(F19, curve19, xs, xr_s)
        r["xs_hex"] = [hex(v) for v in xs]
        r["xr_from_n19l6_1_S_hex"] = hex(xr_s)
        r["f3"] = hex(f3_summation(F19, xs[0], xs[1], xs[2], xr_s))
        swapped[convname] = r

    out = {
        "field_selftests": selftests,
        "certificates": rows,
        "ptm_object1_bitflips": ptm,
        "ptm_object1b_xr_swapped": swapped,
    }
    with open(os.path.join(OUT, "v1_certs.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    # ---- console summary --------------------------------------------------
    for k, v in selftests.items():
        print(k, "irreducible", v["rabin_irreducible"], "Tr(1)", v["trace_of_1"],
              "identities", v["identities_ok"],
              ("brute #E=" + str(v["brute_force_point_count"])) if "brute_force_point_count" in v else "")
    for conv in ("lsb_first", "msb_first"):
        ok = sum(1 for r in rows if r[conv]["matches"] > 0)
        f3z = sum(1 for r in rows if int(r[conv]["f3"], 16) == 0)
        oncurve = sum(1 for r in rows if r[conv]["all_on_curve"])
        print(f"convention {conv}: certificates verifying {ok}/30, "
              f"all three x on curve {oncurve}/30, f3==0 {f3z}/30")
    acc = sum(1 for p in ptm for b in p["per_bit"] if b["accepted"])
    tot = sum(len(p["per_bit"]) for p in ptm)
    f3z = sum(1 for p in ptm for b in p["per_bit"] if b["f3_zero"])
    print(f"PTM object 1 (single-bit flips of x1): accepted {acc}/{tot}, f3==0 {f3z}/{tot}")
    bit0 = [b for p in ptm for b in p["per_bit"] if b["flipped_bit"] == 0]
    print(f"  restricted to flipping bit 0 only: accepted "
          f"{sum(1 for b in bit0 if b['accepted'])}/{len(bit0)}, "
          f"f3==0 {sum(1 for b in bit0 if b['f3_zero'])}/{len(bit0)}")
    for conv, r in swapped.items():
        print(f"PTM object 1b x_R swapped ({conv}): all_on_curve={r['all_on_curve']} "
              f"matches={r['matches']} f3={r['f3']}")


if __name__ == "__main__":
    sys.exit(main())
