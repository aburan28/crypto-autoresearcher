#!/usr/bin/env python3
"""Build the proves-too-much variants of the producer's gfpn_audit.py.

RC-3: "a harness that feeds it a different curve or self-report is allowed, a
modification of its decision logic is not."  gfpn_audit.py takes no curve or
self-report arguments: `--curve` accepts only EcGFp5 | EcMasFp5 (line 239) and
every curve coefficient and self-reported figure is a Python literal inside
main().  The ONLY way to feed it another object is therefore to replace those
literals.  This script does exactly that and nothing else:

  * every substitution is an exact string replacement of an INPUT literal
    (curve coefficients, a self-reported integer / figure, the declared
    rigidity tuple), asserted to occur exactly once in the pristine file;
  * no operator, comparison, branch, label string, threshold or function body
    is touched -- the unified diff written next to each variant is the proof;
  * gfpn_arith.py is copied byte-identical.

The pristine copy is hash-checked against the committed file (sha256
d635a89b10f929a4c7e5e6ad04a2f069ed525a39882c4ee617fe0c6498c3ef80, the value
in trial-plan.json and in snapshot receipt TASK-20260921-b59aad).
"""
import difflib, hashlib, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(HERE)
PRISTINE = os.path.join(SCR, "pipeline_pristine")
AUDIT_SHA = "d635a89b10f929a4c7e5e6ad04a2f069ed525a39882c4ee617fe0c6498c3ef80"
ARITH_SHA = "d4586286c42b56882d866bc5b4414def478a4b0cfe44bc8764a717c644a8c0eb"

N_MAS = "0xfffffffb0000000effffffe20000002cffffffcc2c13f5f892042da0dfcde3fc8f4b2caf22360ee3"
D_MAS = "-0x350910d76c19ff80472df1f236bda8f251edc59a20563b4f1bcb88ad47f9892d334755425f4369e43"
D_MAS_TAMPERED = D_MAS[:-1] + "7"          # last hex digit 3 -> 7

VARIANTS = {
    # OBJECT A: supersingular E_A: y^2 = x^3 - 35x + 98 (j = -3375, CM by -7; -7 inert mod p),
    # fed through the short-Weierstrass (EcMasFp5) branch: only the curve coefficients change.
    "objA_supersingular": {
        "curve_flag": "EcMasFp5",
        "subs": [
            ("        A = Fq(3); B = Fq((0, 0, 0, 0, 8))\n",
             "        A = Fq(-35); B = Fq(98)\n"),
        ],
    },
    # OBJECT B: subfield curve E_0: y^2 = x^3 + 3x + 8 over F_p viewed over F_{p^5};
    # only the curve coefficients change (B = 8 instead of 8 z^4).
    "objB_subfield": {
        "curve_flag": "EcMasFp5",
        "subs": [
            ("        A = Fq(3); B = Fq((0, 0, 0, 0, 8))\n",
             "        A = Fq(3); B = Fq(8)\n"),
        ],
    },
    # OBJECT C: EcMasFp5 itself, with three tampered self-reports:
    # order n + 2; twist security 101.95 (outside the 0.01 tolerance); CM integer D last digit altered.
    "objC_tampered_selfreports": {
        "curve_flag": "EcMasFp5",
        "subs": [
            (f"        n_note = {N_MAS}\n", f"        n_note = {N_MAS} + 2\n"),
            (f"            D_note = {D_MAS}\n", f"            D_note = {D_MAS_TAMPERED}\n"),
            ('                tw["self_reported_twist_security_bits"] = 101.93\n',
             '                tw["self_reported_twist_security_bits"] = 101.95\n'),
            ('                tw["abs_difference"] = round(abs(tw["twist_security_bits"] - 101.93), 4)\n',
             '                tw["abs_difference"] = round(abs(tw["twist_security_bits"] - 101.95), 4)\n'),
            ('        figs.append({"id": "twist_security_101_93", "claimed_bits": 101.93, "curve": "EcMasFp5",\n',
             '        figs.append({"id": "twist_security_101_93", "claimed_bits": 101.95, "curve": "EcMasFp5",\n'),
        ],
    },
    # OBJECT D (EcMasFp5 part): the real curve, rigidity claim declared as (A=3, c=8, i=3).
    "objD_mas_shifted_rigidity": {
        "curve_flag": "EcMasFp5",
        "subs": [
            ('            rg["published_first_hit"] = {"A": 3, "c": 8, "i": 4}\n',
             '            rg["published_first_hit"] = {"A": 3, "c": 8, "i": 3}\n'),
            ('                same = (hit["A"], hit["c"], hit["i"]) == (3, 8, 4)\n',
             '                same = (hit["A"], hit["c"], hit["i"]) == (3, 8, 3)\n'),
        ],
    },
    # OBJECT D (EcGFp5 part): the real curve, rigidity claim declared as b = 263 z^2.
    "objD_gf_shifted_rigidity": {
        "curve_flag": "EcGFp5",
        "subs": [
            ('            rg["published_first_hit"] = {"c": 263, "i": 1, "sign": "+"}\n',
             '            rg["published_first_hit"] = {"c": 263, "i": 2, "sign": "+"}\n'),
            ('                same = (hit["c"], hit["i"], hit["sign"]) == (263, 1, "+")\n',
             '                same = (hit["c"], hit["i"], hit["sign"]) == (263, 2, "+")\n'),
        ],
    },
}

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def main():
    src = os.path.join(PRISTINE, "gfpn_audit.py")
    assert sha(src) == AUDIT_SHA, "pristine gfpn_audit.py hash mismatch"
    assert sha(os.path.join(PRISTINE, "gfpn_arith.py")) == ARITH_SHA, "pristine gfpn_arith.py hash mismatch"
    text = open(src).read()
    for name, v in VARIANTS.items():
        out = text
        for old, new in v["subs"]:
            n = out.count(old)
            assert n == 1, f"{name}: substitution target occurs {n} times: {old!r}"
            out = out.replace(old, new)
        d = os.path.join(SCR, "variants", name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "gfpn_audit.py"), "w").write(out)
        shutil.copyfile(os.path.join(PRISTINE, "gfpn_arith.py"), os.path.join(d, "gfpn_arith.py"))
        diff = "".join(difflib.unified_diff(text.splitlines(True), out.splitlines(True),
                                            "pipeline_pristine/gfpn_audit.py", f"variants/{name}/gfpn_audit.py"))
        open(os.path.join(d, "variant.diff"), "w").write(diff)
        open(os.path.join(d, "curve_flag.txt"), "w").write(v["curve_flag"] + "\n")
        print(f"{name}: {len(v['subs'])} literal substitution(s); diff lines changed = "
              f"{sum(1 for l in diff.splitlines() if l.startswith(('+', '-')) and not l.startswith(('+++', '---')))}; "
              f"variant sha256 {sha(os.path.join(d, 'gfpn_audit.py'))}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
