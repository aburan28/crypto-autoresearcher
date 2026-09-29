"""V1 steps (1)-(4) and proves_too_much object 1 -- validator's own arithmetic.

Run from /workspace:  python3 <this file> > scratch/v1_output.txt
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gf2n import (BinaryCurve, GF2n, f3_find_points, poly_from_string_be,
                  poly_from_string_le, to_string_le)

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"


def read_info(name):
    lines = open(f"{BENCH}/INFO{name}.dimacs").read().split("\n")
    n, l = map(int, lines[0].split())
    return dict(name=name, n=n, l=l, modulus=lines[1].strip(), xR=lines[2].strip(),
                label=lines[3].strip(), cert=lines[4].strip())


FIELDS = {}


def field_for(info):
    key = (info["n"], info["modulus"])
    if key not in FIELDS:
        FIELDS[key] = GF2n(info["modulus"])
        assert FIELDS[key].n == info["n"]
    return FIELDS[key]


def check_certificate(F, E, xs, xR, verbose_prefix=""):
    """Return (accepted: bool, n_sign_choices_matching: int, n_sign_choices_tried: int,
    all_x_on_curve: bool)."""
    lifts = []
    for x in xs:
        L = E.lift(x)
        if L is None:
            return False, 0, 0, False
        lifts.append(L)
    matches = 0
    tried = 0
    for s0 in range(2):
        for s1 in range(2):
            for s2 in range(2):
                P = E.add(E.add(lifts[0][s0], lifts[1][s1]), lifts[2][s2])
                tried += 1
                if P is not None and P[0] == xR:
                    matches += 1
    return matches > 0, matches, tried, True


def parse_anf(path):
    lines = open(path).read().strip().split("\n")
    hdr = lines[0].split()
    assert hdr[0] == "p" and hdr[1] == "cnf"
    nvars, neq = int(hdr[2]), int(hdr[3])
    eqs = []
    for ln in lines[1:]:
        toks = ln.split()
        assert toks[0] == "x", ln
        assert toks[-1] == "0", ln
        toks = toks[1:-1]
        const = 0
        monos = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t == "T":
                const ^= 1
                i += 1
            elif t.startswith("."):
                d = int(t[1:])
                monos.append(tuple(int(v) for v in toks[i + 1:i + 1 + d]))
                i += 1 + d
            else:
                monos.append((int(t),))
                i += 1
        eqs.append((monos, const))
    assert len(eqs) == neq, (len(eqs), neq)
    return nvars, eqs


def eval_anf(eqs, assign_bits):
    """assign_bits[i] is the value of variable i+1.  An XOR-clause is satisfied
    when (XOR of its terms) XOR const == 1  (dimacs.c: a T flips the constant and
    negates the first literal, i.e. clause with T  <=>  sum of terms = 0)."""
    unsat = []
    for k, (monos, const) in enumerate(eqs):
        v = const
        for mono in monos:
            p = 1
            for var in mono:
                p &= assign_bits[var - 1]
            v ^= p
        if v != 1:
            unsat.append(k)
    return unsat


def anf_shape(eqs):
    from collections import Counter
    c = Counter()
    for monos, const in eqs:
        for m in monos:
            c[len(m)] += 1
    return dict(sorted(c.items()))


def main():
    out = []
    P = out.append
    infos = {}
    for f in sorted(glob.glob(f"{BENCH}/INFO*.dimacs")):
        name = os.path.basename(f)[4:-7]
        infos[name] = read_info(name)
    P(f"# INFO files parsed: {len(infos)}")

    # ---- fields + irreducibility ----
    P("\n## Fields (modulus string lowest-degree-first; irreducibility by Rabin test)")
    for n in (15, 17, 19):
        inf = next(v for v in infos.values() if v["n"] == n)
        F = field_for(inf)
        terms = [i for i in range(F.n + 1) if (F.mod >> i) & 1]
        P(f"n={n}: modulus string {inf['modulus']} -> x^{' + x^'.join(map(str, reversed(terms)))} ; irreducible=True (constructor asserts); Tr(1)={F.trace(1)}")
        # all INFO files of this n share the modulus?
        mods = {v["modulus"] for v in infos.values() if v["n"] == n}
        P(f"   distinct moduli among INFO files with n={n}: {len(mods)}")

    # ---- (1) 30 certificates ----
    P("\n## V1(1): 30 shipped S certificates, own arithmetic (8 sign choices tried per certificate; the 8 = 2^3 y-choices; negating all three gives the same x so at most 4 distinct x(P1+P2+P3))")
    P("| instance | x1 (LE hex) | x2 | x3 | x_R (LE hex) | all x_i on E | Tr(c(x_R)) | sign choices matching / 8 | accepted | f3(x1,x2,x3,x_R) |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    cert_rows = []
    n_ok = 0
    for name in sorted(infos, key=lambda s: (int(s[1:3]), int(s.split('-')[1]))):
        inf = infos[name]
        if inf["label"] != "S":
            continue
        F = field_for(inf)
        E = BinaryCurve(F, 1, 1)
        parts = inf["cert"].split("-")
        assert len(parts) == 3 and all(len(p) == inf["l"] for p in parts), inf
        xs = [poly_from_string_le(p) for p in parts]
        assert len(inf["xR"]) == inf["n"]
        xR = poly_from_string_le(inf["xR"])
        acc, nm, nt, on = check_certificate(F, E, xs, xR)
        f3v = f3_find_points(F, xs[0], xs[1], xs[2], xR)
        trR = "n/a(x=0)" if xR == 0 else F.trace(E.curve_rhs_trace_arg(xR))
        n_ok += acc
        cert_rows.append(dict(name=name, xs=xs, xR=xR, accepted=acc, matches=nm, tried=nt, f3=f3v))
        P(f"| {name} | {xs[0]:#x} | {xs[1]:#x} | {xs[2]:#x} | {xR:#x} | {on} | {trR} | {nm}/{nt} | {acc} | {f3v:#x} |")
    P(f"\nACCEPTED {n_ok}/30 ; f3 == 0 on {sum(1 for r in cert_rows if r['f3'] == 0)}/30 certificates")

    # ---- (2) ANF evaluation at WDSat assignment and CMS model ----
    P("\n## V1(2): Xn19l6-19-U.anf parsed; equations evaluated at the solver assignments")
    nvars, eqs = parse_anf(f"{BENCH}/Xn19l6-19-U.anf")
    P(f"header: {nvars} vars, {len(eqs)} equations; monomials by degree: {anf_shape(eqs)}; equations with T: {sum(c for _, c in eqs)}")
    rows = [json.loads(l) for l in open(f"{RUN}/results.jsonl")]
    wd = [r for r in rows if r.get("instance") == "n19l6-19-U" and r.get("engine") == "wdsat" and r.get("config") == "default"][0]
    assign = wd["assignment"]
    P(f"WDSat default assignment string ({len(assign)} chars): {assign}")
    bits = [int(ch) for ch in assign]
    assert len(bits) == nvars
    unsat = eval_anf(eqs, bits)
    P(f"  interpretation A (char i = value of variable i+1): unsatisfied equations = {len(unsat)} {unsat}")
    unsat_rev = eval_anf(eqs, bits[::-1])
    P(f"  interpretation B (string reversed): unsatisfied equations = {len(unsat_rev)}")
    # sanity: a random assignment should violate many
    import random
    random.seed(1)
    rnd = [random.randint(0, 1) for _ in range(nvars)]
    P(f"  control: random assignment (seed 1) unsatisfied = {len(eval_anf(eqs, rnd))}")
    # per-config check of the other WDSat rows
    for cfg in ("core_order", "symmetry", "gauss_elim"):
        r = [r for r in rows if r.get("instance") == "n19l6-19-U" and r.get("engine") == "wdsat" and r.get("config") == cfg][0]
        b = [int(ch) for ch in r["assignment"]]
        P(f"  WDSat {cfg}: assignment == default? {r['assignment'] == assign}; unsatisfied = {len(eval_anf(eqs, b))}")
    # CMS model from log
    cms_log = open(f"{RUN}/logs/cms_xor_n19l6-19-U.out").read().split("\n")
    lits = []
    for ln in cms_log:
        if ln.startswith("v "):
            lits += [int(t) for t in ln[2:].split()]
    lits = [t for t in lits if t != 0]
    model = {abs(t): (1 if t > 0 else 0) for t in lits}
    P(f"CMS cnf_xor model: {len(model)} literals in v-lines; max var {max(model)}")
    cms_bits = [model[i + 1] for i in range(nvars)]
    P(f"  CMS first {nvars} vars as string: {''.join(map(str, cms_bits))}")
    P(f"  CMS model on the ANF (first {nvars} vars): unsatisfied equations = {len(eval_anf(eqs, cms_bits))}")

    # ---- (3) decode + f3 under both conventions ----
    P("\n## V1(3): decode first 3*l = 18 bits under both bit orders; f3 over GF(2^19)")
    inf = infos["n19l6-19-U"]
    F = field_for(inf)
    E = BinaryCurve(F, 1, 1)
    l = inf["l"]
    chunks = [assign[i * l:(i + 1) * l] for i in range(3)]
    P(f"chunks: {chunks}")
    xR_le = poly_from_string_le(inf["xR"])
    xR_be = poly_from_string_be(inf["xR"])
    P(f"x_R string: {inf['xR']} ; LE -> {xR_le:#x} ; BE -> {xR_be:#x}")
    P("| x-bit convention | x_R convention | x1 | x2 | x3 | f3 |")
    P("|---|---|---|---|---|---|")
    results = {}
    for xconv, xf in (("LE", poly_from_string_le), ("BE", poly_from_string_be)):
        xs = [xf(c) for c in chunks]
        for rconv, xR in (("LE", xR_le), ("BE", xR_be)):
            v = f3_find_points(F, xs[0], xs[1], xs[2], xR)
            results[(xconv, rconv)] = v
            P(f"| {xconv} | {rconv} | {xs[0]:#x} | {xs[1]:#x} | {xs[2]:#x} | {v:#x} |")
    # also CMS's order (x1,x2 swapped) -- f3 symmetric, check
    xs_cms = [poly_from_string_le(''.join(map(str, cms_bits[i * l:(i + 1) * l]))) for i in range(3)]
    P(f"CMS decoded (LE): {[hex(x) for x in xs_cms]} ; f3 (LE x_R) = {f3_find_points(F, *xs_cms, xR_le):#x}")

    # ---- (4) traces ----
    P("\n## V1(4): Tr(x + 1 + 1/x^2) over GF(2^19) (0 => x is an x-coordinate of E; 1 => x is an x-coordinate of the quadratic twist)")
    P("| element | value (hex) | Tr(x+1+1/x^2) | x-coordinate on E? | lift on E |")
    P("|---|---|---|---|---|")
    for lab, x in (("x1 (LE)", poly_from_string_le(chunks[0])), ("x2 (LE)", poly_from_string_le(chunks[1])),
                   ("x3 (LE)", poly_from_string_le(chunks[2])), ("x_R (LE)", xR_le),
                   ("x1 (BE)", poly_from_string_be(chunks[0])), ("x2 (BE)", poly_from_string_be(chunks[1])),
                   ("x3 (BE)", poly_from_string_be(chunks[2])), ("x_R (BE)", xR_be)):
        tr = F.trace(E.curve_rhs_trace_arg(x))
        L = E.lift(x)
        P(f"| {lab} | {x:#x} | {tr} | {E.x_on_curve(x)} | {None if L is None else [hex(p[1]) for p in L]} |")
    # Also: x_R of every U instance -- how many are x-coordinates on E vs twist
    P("\n### x_R of all 30 U instances: on E or on twist (LE reading)")
    for n in (15, 17, 19):
        onE = tw = 0
        names = []
        for name, iv in infos.items():
            if iv["n"] == n and iv["label"] == "U":
                Fn = field_for(iv)
                En = BinaryCurve(Fn, 1, 1)
                x = poly_from_string_le(iv["xR"])
                if En.x_on_curve(x):
                    onE += 1
                else:
                    tw += 1
                    names.append(name)
        P(f"n={n}: x_R on E: {onE}, on twist: {tw} (twist: {names})")

    # ---- twist-group check of the n19l6-19-U x-set: does P1+P2+P3 have x = x_R on the twist? ----
    P("\n## Twist check: lift the decoded x_i to the quadratic twist E': y^2 + xy = x^3 + (1 + w) x^2 + 1 with Tr(w)=1, and test x(P1+P2+P3) = x_R there")
    # find w with trace 1
    w = next(v for v in range(1, 1 << 8) if F.trace(v) == 1)
    Et = BinaryCurve(F, 1 ^ w, 1)
    xs_le = [poly_from_string_le(c) for c in chunks]
    acc, nm, nt, on = check_certificate(F, Et, xs_le, xR_le)
    P(f"twist a2 = 1 + {w:#x} (Tr(w)={F.trace(w)}); all x_i lift on E': {on}; x(P1+P2+P3)=x_R for {nm}/{nt} sign choices; accepted on twist: {acc}")
    # negative control on twist: the same x-set against n19l6-1-S's x_R
    xR_1S = poly_from_string_le(infos["n19l6-1-S"]["xR"])
    acc2, nm2, nt2, on2 = check_certificate(F, Et, xs_le, xR_1S)
    P(f"control: same x-set on E' against x_R of n19l6-1-S ({xR_1S:#x}): accepted {acc2} ({nm2}/{nt2})")

    # ---- proves_too_much object 1 ----
    P("\n## proves_too_much object 1: known-false inputs to the same checker")
    P("### (i) 30 shipped certificates with bit 0 of x1 flipped (x1 ^= 1)")
    P("| instance | x1' | x1' on E? | accepted | f3 |")
    P("|---|---|---|---|---|")
    n_acc = 0
    n_f3zero = 0
    for r in cert_rows:
        inf = infos[r["name"]]
        F_ = field_for(inf)
        E_ = BinaryCurve(F_, 1, 1)
        xs = list(r["xs"])
        xs[0] ^= 1
        acc, nm, nt, on = check_certificate(F_, E_, xs, r["xR"])
        f3v = f3_find_points(F_, xs[0], xs[1], xs[2], r["xR"])
        n_acc += acc
        n_f3zero += (f3v == 0)
        P(f"| {r['name']} | {xs[0]:#x} | {E_.x_on_curve(xs[0])} | {acc} | {f3v:#x} |")
    P(f"\nbit-flipped certificates ACCEPTED: {n_acc}/30 (must be 0); f3 == 0 on {n_f3zero}/30 (must be <= 1)")
    P("### (ii) the n19l6-19-U x-set (both bit orders, and the CMS ordering) against x_R of n19l6-1-S, on E and on E'")
    for lab, xs in (("LE", xs_le), ("BE", [poly_from_string_be(c) for c in chunks]), ("CMS-LE", xs_cms)):
        accE, nmE, ntE, onE = check_certificate(F, E, xs, xR_1S)
        accT, nmT, ntT, onT = check_certificate(F, Et, xs, xR_1S)
        P(f"{lab}: on E accepted={accE} ({nmE}/{ntE}, all x_i lift on E: {onE}); on E' accepted={accT} ({nmT}/{ntT}); f3 = {f3_find_points(F, *xs, xR_1S):#x}")
    # plus each of the five rows (4 wdsat + 1 cms), literal x_bits
    five = [r for r in rows if r.get("instance") == "n19l6-19-U" and r.get("status") == "SAT" and r.get("verification")]
    P(f"five SAT rows on n19l6-19-U: {[(r['engine'], r['config']) for r in five]}")
    for r in five:
        xs = [poly_from_string_le(b) for b in r["verification"]["x_bits"]]
        accE, nmE, ntE, onE = check_certificate(F, E, xs, xR_1S)
        P(f"  {r['engine']}/{r['config']}: x_bits {r['verification']['x_bits']} vs x_R(n19l6-1-S): accepted on E = {accE}; f3 = {f3_find_points(F, *xs, xR_1S):#x}; vs own x_R: f3 = {f3_find_points(F, *xs, xR_le):#x}")

    print("\n".join(out))


if __name__ == "__main__":
    main()
