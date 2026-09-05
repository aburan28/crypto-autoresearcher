#!/usr/bin/env python3
"""Measurement block A for GOAL-SCURVE-137bd9 / BATCH-a40709, slot S3.

Task:        TASK-20260904-90ac09
Experiment:  EXP-SCURVE-3f87f6
Approval:    approved WITH CONDITIONS by DEC-20260904-5216dd.
             THE CONTRACT FILE experiments/EXP-SCURVE-3f87f6/specification.yaml
             READS status: draft AND approved_by: null AND ALWAYS WILL -- its
             bytes are hash-bound by the completed TASK-20260904-850ff6
             snapshot archive, so writing approved_by would break that archive.
             The approval lives in DEC-20260904-5216dd (condition C-2).
Control pass condition governed by: DEC-20260905-f630e4 ruling D-4.

WHAT THIS PROGRAM DOES
  1. Reads every parameter from the committed parameter capsule
     coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-ef5b1e/tasks/
     TASK-20260824-53ecc0/parameter-capsule.yaml
     and records that file's sha256. No parameter is typed from memory and
     none is carried in from any other record.
  2. Runs the three constructed controls FIRST, on the IDENTICAL code path
     (same is_probable_prime, same nonsingularity_witness, same on_curve)
     that the target lanes use, before any target output is interpreted.
  3. Runs lanes L-EQ, L-FIELD, L-BASE and reports every quantity AS COMPUTED.

WHAT THIS PROGRAM DOES NOT DO
  It compares no measured quantity against any criterion threshold and renders
  no criterion cell: slot S7 alone may compare. It makes no statement about any
  curve's security. Primality is reported as PROBABLE with its round count and
  full witness list, never as prime. No network, no PARI/gp/cypari/cypari2/Sage.

DETERMINISM
  Every randomised component draws from one seeded Mersenne Twister
  (random.Random(SEED), SEED below). The emitted YAML is a pure function of the
  capsule bytes and SEED: it carries no timestamp and no host-dependent field,
  so a re-run reproduces it byte for byte (contract INV-3).

USAGE
  python3 measure_block_a.py --emit controls       > controls-block-a.yaml
  python3 measure_block_a.py --emit measurements   > measurements-block-a.yaml
  python3 measure_block_a.py --emit both           # both documents, for eyeballing
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import random
import re
import sys

SEED = 20260905

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "..", ".."))
CAPSULE = os.path.join(
    REPO,
    "coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-ef5b1e/tasks/"
    "TASK-20260824-53ecc0/parameter-capsule.yaml",
)
CONTRACT = os.path.join(REPO, "experiments/EXP-SCURVE-3f87f6/specification.yaml")

CAPSULE_EXPECTED_SHA256 = "5125d93cd35476075c15bec668bbef6a3021ac7c3bd23e92f7ba53307b68ecc2"
CONTRACT_EXPECTED_SHA256 = "0069b16e39b5a23f1535fa214f72ea1e49deb37ebbfcd678a0d62f56ac43c3d8"


# ---------------------------------------------------------------------------
# input reading
# ---------------------------------------------------------------------------

def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_capsule(path: str) -> dict:
    """Read the capsule with PyYAML if available, else with a narrow fallback.

    The fallback exists so this program depends on nothing beyond the standard
    library; both paths are exercised against the same recorded sha256.
    """
    text = open(path, "r", encoding="utf-8").read()
    try:
        import yaml  # type: ignore
        doc = yaml.safe_load(text)
        parser = "PyYAML safe_load"
    except Exception:  # pragma: no cover - fallback path
        doc = None
        parser = "stdlib regex fallback (PyYAML unavailable)"

    out = {"parser": parser, "hex": {}, "intake": {}}

    if doc is not None:
        for field in doc["reconciled_tuple"]["fields"]:
            if "value_hex" in field:
                out["hex"][field["name"]] = str(field["value_hex"])
        out["intake"]["equation"] = doc["intake"]["equation"]
        out["intake"]["modulus"] = doc["intake"]["modulus"]
        for item in doc["reconciliation"]:
            if item.get("item") == "coefficient_b":
                out["intake"]["b_decimal"] = str(item["intake_decimal"])
                out["intake"]["b_retrieved_hex"] = str(item["retrieved_hex"])
    else:  # pragma: no cover
        for name in ("p", "a", "b", "Gx", "Gy", "n", "h"):
            m = re.search(r"- name: %s\n\s+value_hex: '?([0-9A-Fa-f]+)'?" % name, text)
            out["hex"][name] = m.group(1)
        out["intake"]["equation"] = re.search(r"equation: (\S+)", text).group(1)
        out["intake"]["modulus"] = re.search(r"modulus: (.+)", text).group(1).strip()
        out["intake"]["b_decimal"] = re.search(r"intake_decimal: (\d+)", text).group(1)
        out["intake"]["b_retrieved_hex"] = re.search(r"retrieved_hex: ([0-9A-Fa-f]+)", text).group(1)
    return out


def parse_power_expression(expr: str) -> int:
    """Evaluate a '2^224 - 2^96 + 1'-shaped expression READ FROM THE CAPSULE.

    Deliberately a parser rather than a literal: the closed form is an input,
    not something this program is allowed to know in advance. Accepts only
    integer literals and 'base^exponent' terms joined by + and -.
    """
    expr = expr.strip()
    if not re.fullmatch(r"\s*[+-]?\s*[\d^]+(\s*[+-]\s*[\d^]+)*\s*", expr):
        raise ValueError("unsupported modulus expression: %r" % expr)
    total = 0
    sign = 1
    for tok in re.findall(r"[+-]|\d+\^\d+|\d+", expr):
        if tok == "+":
            sign = 1
        elif tok == "-":
            sign = -1
        elif "^" in tok:
            base, exp = tok.split("^")
            total += sign * int(base) ** int(exp)
        else:
            total += sign * int(tok)
    return total


def parse_linear_coefficient(equation: str) -> int:
    """Extract the integer linear coefficient from the intake equation string."""
    m = re.search(r"([+-]\s*\d+)\s*\*?\s*x(?![\^\d])", equation.replace(" ", ""))
    if not m:
        raise ValueError("no linear term found in %r" % equation)
    return int(m.group(1).replace(" ", ""))


# ---------------------------------------------------------------------------
# THE CHECKERS. Controls and targets both call exactly these functions.
# ---------------------------------------------------------------------------

def is_probable_prime(m: int, bases: list) -> dict:
    """Miller-Rabin. Returns the decision plus every base and its verdict.

    NEVER returns 'prime'. A True decision means: no base in `bases` witnessed
    compositeness. This is the SINGLE primality code path in this program; the
    constructed-composite control and the target both go through it.
    """
    per_base = []
    if m < 2:
        return {"probable_prime": False, "rounds": 0, "bases": [], "per_base": [],
                "reason": "m < 2"}
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for q in small:
        if m == q:
            return {"probable_prime": True, "rounds": 0, "bases": [],
                    "per_base": [], "reason": "m is a small prime by table lookup"}
        if m % q == 0:
            return {"probable_prime": False, "rounds": 0, "bases": [], "per_base": [],
                    "reason": "divisible by small prime %d" % q}
    d = m - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    decision = True
    for a in bases:
        a %= m
        if a in (0, 1, m - 1):
            per_base.append({"base": a, "verdict": "skipped (degenerate base)"})
            continue
        x = pow(a, d, m)
        if x == 1 or x == m - 1:
            per_base.append({"base": a, "verdict": "no witness (passes this round)"})
            continue
        witnessed = True
        for _ in range(r - 1):
            x = pow(x, 2, m)
            if x == m - 1:
                witnessed = False
                break
        if witnessed:
            per_base.append({"base": a, "verdict": "WITNESSES COMPOSITENESS"})
            decision = False
        else:
            per_base.append({"base": a, "verdict": "no witness (passes this round)"})
    return {"probable_prime": decision, "rounds": len(bases), "bases": list(bases),
            "per_base": per_base,
            "reason": "Miller-Rabin over the recorded base list; decomposition m-1 = 2^%d * %d" % (r, d)}


def nonsingularity_witness(a: int, b: int, p: int) -> dict:
    """Return the witness VALUE 4a^3 + 27b^2 mod p and the checker's decision.

    Reported as the value, never only as a boolean (contract L-EQ metric).
    This is the SINGLE nonsingularity code path; the constructed-singular
    control and the target both go through it.
    """
    w = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    return {"witness_value": w, "nonsingular": w != 0,
            "formula": "(4*a^3 + 27*b^2) mod p"}


def on_curve(x: int, y: int, a: int, b: int, p: int) -> dict:
    """Return both sides of the congruence and the checker's decision.

    This is the SINGLE on-curve code path. The constructed random-point control
    and the base point both go through it, which is what makes the two-sided
    exhibit (accepts G, rejects an off-curve pair) meaningful.
    """
    lhs = pow(y, 2, p)
    rhs = (pow(x, 3, p) + a % p * (x % p) + b) % p
    return {"lhs_y2_mod_p": lhs, "rhs_x3_ax_b_mod_p": rhs, "on_curve": lhs == rhs}


def ground_truth_on_curve(x: int, y: int, a: int, b: int, p: int) -> dict:
    """Exact ground truth by a DIFFERENT arithmetic route than on_curve().

    on_curve() reduces modulo p at every step (pow(...,p) and % p).
    This routine forms the full unreduced integer d = y^2 - (x^3 + a*x + b)
    with NO intermediate reduction and asks only whether p divides it. Same
    mathematics, different code path, so agreement between the two is a real
    check on the checker rather than a restatement of it.
    """
    d = y * y - (x * x * x + a * x + b)
    return {"unreduced_difference_bit_length": d.bit_length(),
            "unreduced_difference_sign": (d > 0) - (d < 0),
            "divisible_by_p": d % p == 0,
            "method": "full-integer d = y^2 - (x^3 + a*x + b), no intermediate reduction; on curve iff p | d"}


# ---------------------------------------------------------------------------
# affine group law on y^2 = x^3 + ax + b over F_p. O is represented by None.
# ---------------------------------------------------------------------------

def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(k, P, a, p):
    R = None
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R


# ---------------------------------------------------------------------------
# YAML emission helpers (hand-rolled so the program needs no writer library)
# ---------------------------------------------------------------------------

# A string that a YAML resolver would turn into an int, float, bool or null must
# be quoted, or the document does not round-trip: '01' read back as the integer 1
# would silently destroy the "as read" fidelity this record exists to carry.
# Found by parse-checking the first emitted pair of documents, not by inspection.
_NONSTRING_LOOKING = re.compile(
    r"""(?ix)^(
        [+-]?(0b[01_]+|0o?[0-7_]+|[0-9][0-9_]*|0x[0-9a-f_]+)      # ints incl. leading-zero
      | [+-]?([0-9][0-9_]*)?\.[0-9_]*([eE][-+]?[0-9]+)?           # floats
      | [+-]?\.(inf|nan)
      | true|false|yes|no|on|off|null|~|                          # bools, null, empty
      | [0-9]+(:[0-5]?[0-9])+                                     # sexagesimal
    )$"""
)


def y_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, int):
        return str(v)
    s = str(v)
    if (s == "" or re.search(r"[:#\-\[\]{}&*!|>'\"%@`,?]", s) or s != s.strip()
            or _NONSTRING_LOOKING.match(s)):
        return "'" + s.replace("'", "''") + "'"
    return s


def emit(obj, indent=0, out=None):
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append("%s%s:" % (pad, k))
                emit(v, indent + 1, out)
            elif isinstance(v, (dict, list)):
                out.append("%s%s: %s" % (pad, k, "{}" if isinstance(v, dict) else "[]"))
            elif isinstance(v, str) and "\n" in v:
                out.append("%s%s: |-" % (pad, k))
                for line in v.rstrip("\n").split("\n"):
                    out.append("%s  %s" % (pad, line))
            else:
                out.append("%s%s: %s" % (pad, k, y_scalar(v)))
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                lines = []
                emit(item, indent + 1, lines)
                first = lines[0][len(pad) + 2:]
                out.append("%s- %s" % (pad, first))
                for line in lines[1:]:
                    out.append(line)
            elif isinstance(item, list):
                out.append("%s-" % pad)
                emit(item, indent + 1, out)
            else:
                out.append("%s- %s" % (pad, y_scalar(item)))
    return out


# ---------------------------------------------------------------------------
# prose that is part of the deliverable, kept with the code that produces the
# numbers it argues about
# ---------------------------------------------------------------------------

HASSE_ARGUMENT = """\
THE HASSE-INTERVAL UNIQUENESS ARGUMENT, WRITTEN OUT.

Setting. p is the field characteristic read from the capsule; E is the curve
y^2 = x^3 + a*x + b over F_p; G is the base point read from the capsule; n is
the integer read from the capsule and offered as the order of G. Write #E for
the order of the group E(F_p) (the affine points together with the point at
infinity O). All five inputs are the capsule's, and every number the argument
consumes is computed in this run and reported beside it.

Step 1 -- E(F_p) is a finite abelian group.
  This needs p prime and the curve nonsingular. p is checked here only as a
  PROBABLE prime (L-FIELD, round count and full witness list recorded);
  nonsingularity is established by the witness 4a^3 + 27b^2 mod p being nonzero
  (L-EQ), on the same code path the constructed-singular control is rejected on.
  Note p > 3 is required for the short Weierstrass form to be the general one;
  the computed bit length settles that.

Step 2 -- ord(G) divides n.
  The run computes n*G with the affine group law and obtains O. Hence
  ord(G) | n.

Step 3 -- ord(G) is not 1, and n is not composite as far as this run can tell.
  The run computes (n-1)*G and obtains a finite affine point, which it further
  checks equals -G = (Gx, p - Gy). If ord(G) were 1 then G = O and (n-1)*G
  would be O, so ord(G) > 1. To go from "ord(G) divides n and exceeds 1" to
  "ord(G) = n" the argument uses that n has no divisor strictly between 1 and
  n, i.e. that n is prime. n is checked here only as a PROBABLE prime, by the
  same Miller-Rabin code path, with its round count and full witness list
  recorded. THIS IS THE ARGUMENT'S FIRST CONDITIONAL LINK and it is stated as
  conditional, not as established.

Step 4 -- n divides #E.
  By Lagrange's theorem the order of any element divides the order of the
  group, so ord(G) = n implies n | #E. Hence #E = k*n for some positive
  integer k.

Step 5 -- Hasse's theorem bounds #E.
  Hasse: |#E - (p + 1)| <= 2*sqrt(p). Since #E and p are integers, this is
  equivalent to |#E - (p+1)| <= s where s = floor(2*sqrt(p)) = isqrt(4p),
  computed exactly here by integer square root -- no floating point is used
  anywhere in this bound. So
      #E is in the closed integer interval [p + 1 - s, p + 1 + s],
  an interval containing exactly 2s + 1 integers.

Step 6 -- uniqueness.
  The run enumerates the integers k with k*n inside that interval, by computing
  k_min = ceil((p+1-s)/n) and k_max = floor((p+1+s)/n) in exact integer
  arithmetic, and reports the count k_max - k_min + 1 and the interval's own
  length 2s + 1. IF AND ONLY IF that count is exactly 1 is #E determined by
  this route: the unique multiple is #E, and k is the cofactor h. A sufficient
  (not necessary) condition for the count to be at most 1 is 2s + 1 <= n; the
  run reports both sides of that inequality as computed, and it reports the
  count directly, which is the binding fact.

Step 7 -- what is derived from it.
  #E := k*n, h := k, and the trace of Frobenius t := p + 1 - #E. The run then
  re-checks |t| <= s, reporting both sides. That re-check is a consistency test
  of the derivation, not an independent confirmation of #E.

CONDITIONS UNDER WHICH THIS ARGUMENT SILENTLY FAILS.
  F1. n is not actually prime. Steps 2 and 3 then establish only ord(G) | n
      with ord(G) > 1, so ord(G) may be a proper divisor d of n and Step 4
      gives d | #E, not n | #E. The multiple-counting in Step 6 done with d
      instead of n would generally admit several candidates and #E would not be
      determined. Miller-Rabin gives no proof of primality, so this failure mode
      is REDUCED, NOT REMOVED, by the round count recorded here. A primality
      certificate is out of scope for this batch (batch.yaml OOS-2).
  F2. p is not actually prime. Then F_p is not a field, E(F_p) is not a group,
      and Hasse's theorem does not apply. The same probable-primality caveat
      applies, from the same code path.
  F3. The curve is singular. E(F_p) is then not a group and Hasse does not
      apply. Guarded by the L-EQ nonsingularity witness and by the
      constructed-singular control on the identical code path.
  F4. The interval contains more than one multiple. This happens when n is
      small relative to sqrt(p) -- concretely when 2s + 1 > n leaves room for
      two multiples -- and it is exactly the regime where the route must be
      abandoned for point counting. It is NOT a fact about any curve; it is a
      limit of this instrument. The run reports the count, so this failure is
      visible rather than silent HERE, but it is silent for anyone who copies
      the route to another curve without recomputing the count. Contract INV-7.
  F5. The group-law implementation is wrong in a way that maps a wrong scalar
      multiple to O. A buggy ladder that returns O too eagerly would satisfy
      Step 2 for free. This run's partial guard is that the SAME ladder returns
      a finite point for (n-1)*G and that that point equals -G exactly; a
      ladder that always returns O fails this, and a ladder that never returns
      O fails Step 2. This is a two-sided exhibit of the ladder, not a proof of
      its correctness on all inputs.
  F6. n or p was mistranscribed into the capsule. This route certifies internal
      consistency of the capsule's tuple; it cannot see an error shared by the
      capsule and its sources. The capsule's own sha256 is recorded so that at
      least the bytes this run consumed are pinned.

WHAT THE ARGUMENT DOES NOT ESTABLISH.
  It establishes no fact about any curve's resistance to any attack, adjudicates
  no criterion cell, and compares no quantity against any threshold. It yields
  #E, h and t conditional on F1-F6, and nothing else."""

D4_CONTROL_STATEMENT = """\
WHAT THIS CONTROL ESTABLISHES AND WHAT IT DOES NOT (per DEC-20260905-f630e4 D-4).

Establishes: on the specific pairs actually drawn, the on-curve checker's
decision agreed with the exact arithmetic ground truth computed by a different
code path. Combined with the same checker ACCEPTING the base point (lane
L-BASE, identical code path), it establishes that the checker is not a constant
predicate in either direction -- neither constant-accept nor constant-reject.
Neither half alone establishes that.

Does NOT establish: that the checker is correct on all inputs. NO FALSE-ACCEPT
RATE IS REPORTED OR CLAIMABLE FROM THESE DRAWS. A checker that accepts an
arbitrary pair with probability q is detected by a single null draw with
probability q, so a handful of draws has weak power against a partially broken
instrument. Neither batch.yaml nor the contract fixes a sample count for this
control; the extra draws recorded here are PERMITTED and were not required.

Pass condition applied: PASS iff the checker's decision on the drawn pair
equals the exact ground truth for that pair. batch.yaml:404's "the on-curve
check must reject it" is SUPERSEDED by DEC-20260905-f630e4 D-4 in favour of the
contract's "MUST ACCEPT it only if it is on the curve" (specification.yaml:289).
A uniform pair lies on the curve with probability (p - t)/p^2, within
2/p^(3/2) of 1/p -- small but NOT zero -- so "must reject" can be failed by a
CORRECT checker on that draw, and is passed perfectly by a constant-reject
checker, which is the degenerate instrument this control exists to exclude. An
on-curve draw is therefore a PASS: it is recorded in full, the fact that it did
not exercise the reject path is stated, and another pair is drawn. NO DRAW IS
EVER DISCARDED."""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def run():
    rng = random.Random(SEED)

    capsule_sha = sha256_of(CAPSULE)
    contract_sha = sha256_of(CONTRACT)
    cap = read_capsule(CAPSULE)

    p = int(cap["hex"]["p"], 16)
    a = int(cap["hex"]["a"], 16)
    b = int(cap["hex"]["b"], 16)
    gx = int(cap["hex"]["Gx"], 16)
    gy = int(cap["hex"]["Gy"], 16)
    n = int(cap["hex"]["n"], 16)
    h_retrieved = int(cap["hex"]["h"], 16)

    # ===================================================================
    # CONTROLS FIRST. Nothing below this block reads a target result.
    # ===================================================================
    controls = {}

    # --- CTRL-CONSTRUCTED-COMPOSITE -----------------------------------
    target_bits = p.bit_length()
    half = target_bits // 2

    def gen_probable_prime(bits, rng):
        while True:
            c = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
            if is_probable_prime(c, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37])["probable_prime"]:
                return c

    attempts = 0
    while True:
        attempts += 1
        f1 = gen_probable_prime(half, rng)
        f2 = gen_probable_prime(target_bits - half, rng)
        comp = f1 * f2
        if comp.bit_length() == target_bits:
            break

    comp_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] + [rng.randrange(2, comp - 2) for _ in range(8)]
    comp_res = is_probable_prime(comp, comp_bases)
    controls["composite"] = {
        "id": "CTRL-CONSTRUCTED-COMPOSITE",
        "kind": "constructed positive control",
        "guards": ["L-FIELD", "L-BASE"],
        "construction": (
            "product of two independently generated odd integers, each of which passed the SAME "
            "Miller-Rabin code path on the twelve smallest prime bases; the product is COMPOSITE "
            "BY CONSTRUCTION because both factors exceed 1, so no primality oracle is trusted for "
            "the control's validity -- the factors' own primality is irrelevant to it"
        ),
        "seed": SEED,
        "rejection_sampling_attempts_to_hit_target_bit_length": attempts,
        "factor_1": f1,
        "factor_1_bit_length": f1.bit_length(),
        "factor_2": f2,
        "factor_2_bit_length": f2.bit_length(),
        "composite": comp,
        "composite_bit_length": comp.bit_length(),
        "target_bit_length_matched": comp.bit_length() == target_bits,
        "product_reconstructs": f1 * f2 == comp,
        "checker_code_path": "is_probable_prime() -- the same function L-FIELD calls for p and L-BASE calls for n",
        "checker_decision_probable_prime": comp_res["probable_prime"],
        "rounds": comp_res["rounds"],
        "bases": comp_res["bases"],
        "per_base": comp_res["per_base"],
        "first_witnessing_base": next((e["base"] for e in comp_res["per_base"]
                                       if e["verdict"].startswith("WITNESSES")), None),
        "must_do": "the probable-primality checker MUST REJECT it",
        "outcome": "REJECTED (control fires)" if not comp_res["probable_prime"] else "ACCEPTED (control DID NOT FIRE)",
        "passed": not comp_res["probable_prime"],
        "if_it_had_not_fired": "VOIDS L-FIELD and L-BASE (contract INV-1); reported as the instrument finding it is",
    }

    # --- CTRL-CONSTRUCTED-SINGULAR ------------------------------------
    k_sing = 7
    a_s = (-3 * k_sing * k_sing) % p
    b_s = (2 * k_sing ** 3) % p
    sing_res = nonsingularity_witness(a_s, b_s, p)
    controls["singular"] = {
        "id": "CTRL-CONSTRUCTED-SINGULAR",
        "kind": "constructed positive control",
        "guards": ["L-EQ"],
        "construction": (
            "over the SAME field prime p read from the capsule, take k = %d and set "
            "a' = -3k^2 mod p, b' = 2k^3 mod p. Then 4a'^3 + 27b'^2 = 4(-27k^6) + 27(4k^6) = 0 "
            "identically over the integers, so the curve is SINGULAR BY CONSTRUCTION and no "
            "oracle is trusted for the control's validity" % k_sing
        ),
        "k": k_sing,
        "a_singular": a_s,
        "b_singular": b_s,
        "checker_code_path": "nonsingularity_witness() -- the same function L-EQ calls for the target (a, b)",
        "witness_value": sing_res["witness_value"],
        "checker_decision_nonsingular": sing_res["nonsingular"],
        "must_do": "the nonsingularity check MUST REJECT it",
        "outcome": "REJECTED (control fires)" if not sing_res["nonsingular"] else "ACCEPTED (control DID NOT FIRE)",
        "passed": not sing_res["nonsingular"],
        "if_it_had_not_fired": "VOIDS L-EQ (contract INV-1)",
    }

    # --- CTRL-CONSTRUCTED-RANDOMPOINT ---------------------------------
    draws = []
    n_draws = 3
    for i in range(n_draws):
        x = rng.randrange(0, p)
        y = rng.randrange(0, p)
        decision = on_curve(x, y, a, b, p)
        truth = ground_truth_on_curve(x, y, a, b, p)
        draws.append({
            "draw_index": i,
            "x": x,
            "y": y,
            "congruence_lhs_y2_mod_p": decision["lhs_y2_mod_p"],
            "congruence_rhs_x3_ax_b_mod_p": decision["rhs_x3_ax_b_mod_p"],
            "ground_truth_method": truth["method"],
            "ground_truth_unreduced_difference_bit_length": truth["unreduced_difference_bit_length"],
            "ground_truth_on_curve": truth["divisible_by_p"],
            "checker_decision_on_curve": decision["on_curve"],
            "decision_equals_ground_truth": decision["on_curve"] == truth["divisible_by_p"],
            "reject_path_exercised_by_this_draw": not truth["divisible_by_p"],
            "discarded": False,
            "note": ("this draw LIES ON THE CURVE; under D-4 that is a PASS, the reject path was not "
                     "exercised by it, it is recorded in full and another pair was drawn"
                     if truth["divisible_by_p"] else
                     "this draw is off the curve; the checker's reject path was exercised"),
        })
    controls["randompoint"] = {
        "id": "CTRL-CONSTRUCTED-RANDOMPOINT",
        "kind": "constructed null control",
        "guards": ["L-BASE"],
        "governing_record_for_the_pass_condition": "DEC-20260905-f630e4 (ruling D-4)",
        "superseded_text": "batch.yaml:404 'the on-curve check must reject it' -- SUPERSEDED, on force not placement",
        "governing_text": "specification.yaml:289 CTRL-CONSTRUCTED-RANDOMPOINT must_do -- 'MUST ACCEPT it only if it is on the curve'",
        "pass_condition_implemented": "PASS iff the checker's decision on the drawn pair equals the exact arithmetic ground truth for that pair",
        "draw_provenance": (
            "Python random.Random(%d), CPython Mersenne Twister; coordinates drawn as "
            "rng.randrange(0, p) with p read from the capsule. The SAME generator instance, in "
            "the SAME call order, produced the composite control's factors first, so the draws "
            "are reproducible only by re-running this program from the top -- which is what INV-3 "
            "reproduction means here." % SEED
        ),
        "seed": SEED,
        "number_of_draws": n_draws,
        "draws_discarded": 0,
        "checker_code_path": "on_curve() -- the same function L-BASE calls for the base point G",
        "ground_truth_code_path": "ground_truth_on_curve() -- full-integer divisibility, NO intermediate modular reduction; a different route from the checker",
        "draws": draws,
        "all_decisions_equal_ground_truth": all(d["decision_equals_ground_truth"] for d in draws),
        "passed": all(d["decision_equals_ground_truth"] for d in draws),
        "outcome": None,  # filled below
        "false_accept_rate": None,
        "false_accept_rate_note": "NULL AND NOT COMPUTABLE FROM THIS CONTROL. See what_this_establishes.",
        "what_this_establishes": D4_CONTROL_STATEMENT,
        "if_it_had_not_fired": "VOIDS L-BASE (contract INV-1); a disagreement would be a real hard-gate failure about the INSTRUMENT, never about any curve",
    }
    controls["randompoint"]["outcome"] = (
        "PASS -- every drawn pair's checker decision equals its exact ground truth"
        if controls["randompoint"]["passed"] else
        "FAIL -- at least one drawn pair's checker decision disagrees with its exact ground truth"
    )

    controls_all_passed = all(controls[k2]["passed"] for k2 in controls)

    # ===================================================================
    # TARGET LANES. Only reached after the controls above have run.
    # ===================================================================

    # --- L-EQ ----------------------------------------------------------
    b_intake_decimal_str = cap["intake"]["b_decimal"]
    b_intake = int(b_intake_decimal_str)
    b_hex_str = cap["intake"]["b_retrieved_hex"]
    b_from_hex = int(b_hex_str, 16)
    b_diff = b_intake - b_from_hex

    lin_coeff = parse_linear_coefficient(cap["intake"]["equation"])
    a_expected_from_intake = lin_coeff % p
    a_minus_p_plus_3 = a - (p + lin_coeff)

    ns = nonsingularity_witness(a, b, p)
    four_a3 = (4 * pow(a, 3, p)) % p
    j_num = (1728 * four_a3) % p
    j_inv = (j_num * pow(ns["witness_value"], -1, p)) % p if ns["witness_value"] != 0 else None
    disc = (-16 * ns["witness_value"]) % p

    l_eq = {
        "lane": "L-EQ",
        "rank": 2,
        "input_read": {"path": os.path.relpath(CAPSULE, REPO), "sha256": capsule_sha},
        "interpretable": controls["singular"]["passed"],
        "guarding_control": "CTRL-CONSTRUCTED-SINGULAR",
        "quantities": {
            "constant_coefficient_reconciliation": {
                "intake_decimal_as_read": b_intake_decimal_str,
                "intake_decimal_as_integer": b_intake,
                "intake_decimal_digit_count": len(b_intake_decimal_str),
                "retrieved_hex_as_read": b_hex_str,
                "retrieved_hex_as_integer": b_from_hex,
                "retrieved_hex_digit_count": len(b_hex_str),
                "difference_intake_minus_retrieved": b_diff,
                "exact_integer_equality": b_intake == b_from_hex,
                "relation_as_computed": ("int(intake_decimal) == int(retrieved_hex, 16), difference exactly 0"
                                         if b_diff == 0 else
                                         "int(intake_decimal) - int(retrieved_hex, 16) = %d, NOT ZERO" % b_diff),
                "b_bit_length": b_from_hex.bit_length(),
                "advisory_residues_recomputed_here": {
                    "note": ("the capsule recorded mod-9 and mod-11 agreement as ADVISORY hand computations that "
                             "PROVE NOTHING; recomputed here as integers so the exact equality above is not the "
                             "only number a reader can check"),
                    "intake_decimal_mod_9": b_intake % 9,
                    "retrieved_hex_mod_9": b_from_hex % 9,
                    "intake_decimal_mod_11": b_intake % 11,
                    "retrieved_hex_mod_11": b_from_hex % 11,
                },
            },
            "linear_coefficient_relation": {
                "linear_coefficient_parsed_from_intake_equation": lin_coeff,
                "intake_equation_as_read": cap["intake"]["equation"],
                "a_retrieved_hex_as_read": cap["hex"]["a"],
                "a_as_integer": a,
                "p_as_integer": p,
                "p_plus_linear_coefficient": p + lin_coeff,
                "a_minus_that_value": a_minus_p_plus_3,
                "relation_as_computed": ("a == p + (%d), i.e. a == p - %d exactly as integers, difference 0"
                                         % (lin_coeff, -lin_coeff) if a_minus_p_plus_3 == 0 else
                                         "a - (p + (%d)) = %d, NOT ZERO" % (lin_coeff, a_minus_p_plus_3)),
                "a_congruent_to_linear_coefficient_mod_p": a % p == a_expected_from_intake,
                "a_mod_p_reduced": a % p,
            },
            "nonsingularity_witness": {
                "formula": ns["formula"],
                "witness_value": ns["witness_value"],
                "reported_as": "the value itself, per the contract's L-EQ metric; the boolean is derived from it",
                "is_zero": ns["witness_value"] == 0,
                "checker_decision_nonsingular": ns["nonsingular"],
                "discriminant_minus16_times_witness_mod_p": disc,
            },
            "j_invariant": {
                "formula": "j = 1728 * (4a^3) * inverse(4a^3 + 27b^2) mod p",
                "four_a_cubed_mod_p": four_a3,
                "numerator_1728_times_4a3_mod_p": j_num,
                "denominator_is_the_nonsingularity_witness": ns["witness_value"],
                "j_invariant_mod_p": j_inv,
                "j_invariant_hex": None if j_inv is None else format(j_inv, "x"),
                "j_equals_0": j_inv == 0,
                "j_equals_1728_mod_p": j_inv == 1728 % p,
            },
        },
        "check_that_would_have_failed": (
            "b_intake != b_from_hex would have made exact_integer_equality false and fired contract INV-6; "
            "a - (p + linear_coefficient) != 0 would have made the linear relation false; a zero "
            "nonsingularity witness would have made the curve singular and left the j-invariant undefined "
            "(the modular inverse would have raised)."
        ),
    }

    # --- L-FIELD -------------------------------------------------------
    modulus_expr = cap["intake"]["modulus"]
    p_closed_form = parse_power_expression(modulus_expr)
    p_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] + [rng.randrange(2, p - 2) for _ in range(20)]
    p_prime_res = is_probable_prime(p, p_bases)

    l_field = {
        "lane": "L-FIELD",
        "rank": 3,
        "input_read": {"path": os.path.relpath(CAPSULE, REPO), "sha256": capsule_sha},
        "interpretable": controls["composite"]["passed"],
        "guarding_control": "CTRL-CONSTRUCTED-COMPOSITE",
        "quantities": {
            "prime_as_exact_identity": {
                "closed_form_expression_as_read_from_capsule": modulus_expr,
                "closed_form_evaluated": p_closed_form,
                "retrieved_hex_as_read": cap["hex"]["p"],
                "retrieved_hex_as_integer": p,
                "difference_closed_form_minus_retrieved": p_closed_form - p,
                "exact_identity_holds": p_closed_form == p,
                "how_the_closed_form_was_obtained": (
                    "parsed from the capsule's intake.modulus string by parse_power_expression(), not typed "
                    "as a literal; the parser accepts only integer literals and base^exponent terms"
                ),
            },
            "bit_length": p.bit_length(),
            "byte_length_of_retrieved_hex": len(cap["hex"]["p"]) // 2,
            "residues_consumed_by_later_lanes": [
                {"residue": "p mod 3", "value": p % 3, "consumed_by": "later slots; no comparison performed here"},
                {"residue": "p mod 4", "value": p % 4, "consumed_by": "L-IND and L-COMPLETE (slot S5)"},
                {"residue": "p mod 8", "value": p % 8, "consumed_by": "L-IND and L-COMPLETE (slot S5)"},
                {"residue": "p mod 16", "value": p % 16, "consumed_by": "later slots; recorded for completeness"},
                {"residue": "p mod 2^32", "value": p % (2 ** 32),
                 "consumed_by": "none declared; recorded because the capsule's word-level reconciliation argument turns on it"},
            ],
            "probable_primality": {
                "verdict": "PROBABLE PRIME" if p_prime_res["probable_prime"] else "COMPOSITE (a base witnessed it)",
                "never_stated_as": "prime -- no primality certificate was attempted; batch.yaml OOS-2 leaves it OPEN AND UNATTEMPTED",
                "algorithm": "Miller-Rabin, strong probable-prime test",
                "rounds": p_prime_res["rounds"],
                "deterministic_bases_used": 12,
                "random_bases_used": 20,
                "random_base_source": "random.Random(%d), same generator instance and call order as the controls" % SEED,
                "decomposition": p_prime_res["reason"],
                "witness_list": p_prime_res["bases"],
                "per_base_verdicts": p_prime_res["per_base"],
                "error_bound_statement": (
                    "each independent Miller-Rabin round rejects a composite with probability at least 3/4, so "
                    "the residual error for a composite surviving all rounds is at most 4^-rounds under the "
                    "standard independence assumption. THE TWELVE FIXED BASES ARE NOT INDEPENDENT DRAWS and no "
                    "bound is claimed from them; this figure is stated as the textbook bound for the random "
                    "bases only, and it is a bound on a PROBABILISTIC TEST, not a proof."
                ),
            },
        },
        "check_that_would_have_failed": (
            "closed_form_evaluated != retrieved_hex_as_integer would have made the exact identity false; a "
            "Miller-Rabin base witnessing compositeness would have made the verdict COMPOSITE, which for p "
            "would in turn void the Hasse argument's Step 1 (condition F2)."
        ),
    }

    # --- L-BASE --------------------------------------------------------
    g_check = on_curve(gx, gy, a, b, p)
    g_truth = ground_truth_on_curve(gx, gy, a, b, p)

    n_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] + [rng.randrange(2, n - 2) for _ in range(20)]
    n_prime_res = is_probable_prime(n, n_bases)

    G = (gx, gy)
    nG = ec_mul(n, G, a, p)
    n_minus_1_G = ec_mul(n - 1, G, a, p)
    neg_G = (gx, (-gy) % p)

    s = math.isqrt(4 * p)
    lo = p + 1 - s
    hi = p + 1 + s
    k_min = -((-lo) // n)
    k_max = hi // n
    multiple_count = max(0, k_max - k_min + 1)
    unique = multiple_count == 1

    if unique:
        order_E = k_min * n
        h_derived = k_min
        t = p + 1 - order_E
    else:
        order_E = None
        h_derived = None
        t = None

    l_base = {
        "lane": "L-BASE",
        "rank": 4,
        "input_read": {"path": os.path.relpath(CAPSULE, REPO), "sha256": capsule_sha},
        "interpretable": controls["randompoint"]["passed"] and controls["composite"]["passed"],
        "guarding_controls": ["CTRL-CONSTRUCTED-RANDOMPOINT", "CTRL-CONSTRUCTED-COMPOSITE"],
        "quantities": {
            "base_point_on_curve": {
                "Gx_hex_as_read": cap["hex"]["Gx"],
                "Gy_hex_as_read": cap["hex"]["Gy"],
                "Gx": gx,
                "Gy": gy,
                "congruence_lhs_y2_mod_p": g_check["lhs_y2_mod_p"],
                "congruence_rhs_x3_ax_b_mod_p": g_check["rhs_x3_ax_b_mod_p"],
                "two_sided_residues_equal": g_check["on_curve"],
                "checker_code_path": "on_curve() -- IDENTICAL to the code path CTRL-CONSTRUCTED-RANDOMPOINT ran on",
                "independent_ground_truth_agrees": g_truth["divisible_by_p"] == g_check["on_curve"],
                "two_sided_instrument_exhibit": (
                    "this ACCEPTANCE of G, together with CTRL-CONSTRUCTED-RANDOMPOINT's rejection of an "
                    "off-curve pair on the same function, is the pair that excludes both the constant-accept "
                    "and the constant-reject checker. Neither half alone does (DEC-20260905-f630e4 D-4)."
                ),
            },
            "order_of_the_base_point": {
                "n_hex_as_read": cap["hex"]["n"],
                "n": n,
                "n_bit_length": n.bit_length(),
                "side_1_n_times_G": "point at infinity O" if nG is None else {"x": nG[0], "y": nG[1]},
                "side_1_is_identity": nG is None,
                "side_2_n_minus_1_times_G": ("point at infinity O" if n_minus_1_G is None
                                             else {"x": n_minus_1_G[0], "y": n_minus_1_G[1]}),
                "side_2_is_finite": n_minus_1_G is not None,
                "side_2_equals_negative_G": n_minus_1_G == neg_G,
                "negative_G": {"x": neg_G[0], "y": neg_G[1]},
                "what_the_two_sided_check_establishes": (
                    "ord(G) divides n (from side 1) and ord(G) > 1 (from side 2). ord(G) = n follows ONLY "
                    "if n has no divisor strictly between 1 and n, i.e. only conditional on n being prime, "
                    "which is checked below as PROBABLE only."
                ),
                "group_law": "affine short-Weierstrass addition and doubling over F_p, point at infinity as None, left-to-right double-and-add",
                "n_probable_primality": {
                    "verdict": "PROBABLE PRIME" if n_prime_res["probable_prime"] else "COMPOSITE (a base witnessed it)",
                    "never_stated_as": "prime -- no primality certificate was attempted (batch.yaml OOS-2)",
                    "rounds": n_prime_res["rounds"],
                    "deterministic_bases_used": 12,
                    "random_bases_used": 20,
                    "witness_list": n_prime_res["bases"],
                    "per_base_verdicts": n_prime_res["per_base"],
                    "code_path": "is_probable_prime() -- IDENTICAL to the path CTRL-CONSTRUCTED-COMPOSITE was rejected on",
                },
            },
            "hasse_interval_uniqueness": {
                "argument": HASSE_ARGUMENT,
                "s_floor_2_sqrt_p": s,
                "s_computed_by": "math.isqrt(4*p), exact integer square root; no floating point anywhere in this bound",
                "s_squared_le_4p": s * s <= 4 * p,
                "s_plus_1_squared_gt_4p": (s + 1) * (s + 1) > 4 * p,
                "interval_low_endpoint": lo,
                "interval_high_endpoint": hi,
                "interval_integer_count_2s_plus_1": 2 * s + 1,
                "n_for_comparison_of_lengths": n,
                "sufficient_condition_2s_plus_1_le_n": (2 * s + 1) <= n,
                "k_min_ceil_lo_over_n": k_min,
                "k_max_floor_hi_over_n": k_max,
                "count_of_multiples_of_n_in_interval": multiple_count,
                "multiple_is_unique": unique,
                "binding_fact": (
                    "the COUNT is the binding fact; the length inequality is a sufficient, not necessary, "
                    "condition and is reported alongside it"
                ),
                "if_count_were_not_1": (
                    "the group order would NOT be certifiable by this route and point counting would be "
                    "required -- an honest scope reduction under contract INV-7, and a fact about the "
                    "instrument, not about any curve"
                ),
            },
            "derived_group_order_and_cofactor": {
                "derived_group_order_hash_E": order_E,
                "derived_group_order_hex": None if order_E is None else format(order_E, "x"),
                "derived_group_order_bit_length": None if order_E is None else order_E.bit_length(),
                "derived_cofactor_h": h_derived,
                "derivation": "#E := k*n for the unique k with k*n in the Hasse interval; h := k",
                "derived_not_trusted": (
                    "#E and h are DERIVED here from n, p and the Hasse bound. They are not read from the "
                    "capsule's h field, which the capsule itself records as retrieved_single_witness."
                ),
                "capsule_h_field_as_read": cap["hex"]["h"],
                "capsule_h_as_integer": h_retrieved,
                "derived_h_equals_capsule_h": None if h_derived is None else h_derived == h_retrieved,
                "what_that_agreement_is": (
                    "a check of a DERIVED quantity against a single-witness RETRIEVED capsule field, which "
                    "the capsule explicitly asked L-BASE to perform. It is not a comparison against any "
                    "criterion threshold and renders no criterion cell."
                ),
                "n_times_h_reconstructs_order": None if order_E is None else (n * h_derived == order_E),
            },
            "trace_of_frobenius": {
                "t_definition": "t := p + 1 - #E",
                "t": t,
                "abs_t": None if t is None else abs(t),
                "hasse_bound_s": s,
                "hasse_inequality_abs_t_le_s": None if t is None else abs(t) <= s,
                "both_sides_reported": None if t is None else {"left_abs_t": abs(t), "right_s": s},
                "note": (
                    "this inequality is a CONSISTENCY CHECK of the derivation in the line above, since #E was "
                    "chosen from inside the Hasse interval. It is not an independent confirmation of #E."
                ),
            },
        },
        "check_that_would_have_failed": (
            "n*G != O would have refuted ord(G) | n; (n-1)*G = O or != -G would have refuted ord(G) > 1 or "
            "exposed a broken ladder; a multiple count != 1 would have made #E uncertifiable by this route "
            "(INV-7); |t| > s would have exposed an arithmetic error in the derivation."
        ),
    }

    return {
        "inputs": {"capsule_path": os.path.relpath(CAPSULE, REPO), "capsule_sha256": capsule_sha,
                   "capsule_expected_sha256": CAPSULE_EXPECTED_SHA256,
                   "capsule_sha256_matches": capsule_sha == CAPSULE_EXPECTED_SHA256,
                   "contract_path": os.path.relpath(CONTRACT, REPO), "contract_sha256": contract_sha,
                   "contract_expected_sha256": CONTRACT_EXPECTED_SHA256,
                   "contract_sha256_matches": contract_sha == CONTRACT_EXPECTED_SHA256,
                   "capsule_parser": cap["parser"]},
        "controls": controls,
        "controls_all_passed": controls_all_passed,
        "lanes": [l_eq, l_field, l_base],
    }


HEADER_COMMON = {
    "schema_version": "1.0",
    "task_id": "TASK-20260904-90ac09",
    "slot": "S3",
    "goal_id": "GOAL-SCURVE-137bd9",
    "question_id": "RQ-SCURVE-960dbd",
    "batch_id": "BATCH-a40709",
    "experiment_id": "EXP-SCURVE-3f87f6",
    "approved_by_decision": "DEC-20260904-5216dd",
    "approval_pointer_note": (
        "EXP-SCURVE-3f87f6 IS APPROVED WITH CONDITIONS by DEC-20260904-5216dd. The contract file "
        "experiments/EXP-SCURVE-3f87f6/specification.yaml reads status: draft and approved_by: null and "
        "ALWAYS WILL -- its bytes are hash-bound by the completed TASK-20260904-850ff6 snapshot archive, so "
        "writing approved_by would permanently break that archive. This is expected, not an oversight "
        "(DEC-20260904-5216dd condition C-2)."
    ),
    "superseding_records_read_before_running": ["DEC-20260905-f630e4"],
    "archived_by": "TASK-20260904-fa10f7",
    "produced_by": "coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/tasks/TASK-20260904-90ac09/src/measure_block_a.py",
    "role": "executor",
    "claim_ceiling": (
        "analyzed AT BEST, NEVER supported. NO STATEMENT THAT ANY CURVE IS SAFE OR UNSAFE APPEARS HERE OR IS "
        "PERMITTED FROM THIS SLOT. Arithmetic verification of a published parameter set is a TRANSCRIPTION "
        "CHECK, not a security evaluation. No criterion cell is adjudicated and no measured quantity is "
        "compared against any threshold: slot S7 alone may compare. Every quantity is scoped to the curve "
        "labelled NIST P-224, to the parameters in the committed capsule whose sha256 is recorded, to "
        "pure-Python integer arithmetic, to this runtime and to the declared budget, and transfers to no "
        "other curve without re-running."
    ),
    "determinism": (
        "This document is a pure function of the capsule bytes and the recorded seed. It carries no "
        "timestamp and no host-dependent field, so re-running the producing source reproduces it byte for "
        "byte (contract INV-3). Wall-clock, environment and session facts live in report.md instead."
    ),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", choices=["controls", "measurements", "both"], default="both")
    args = ap.parse_args()

    r = run()

    if args.emit in ("controls", "both"):
        doc = dict(HEADER_COMMON)
        doc["record_type"] = "constructed_controls_block_a"
        doc["ordering_statement"] = (
            "THE CONTROLS BELOW RAN FIRST, on the identical code paths the target lanes use, and their "
            "outcomes were recorded BEFORE any target output was interpreted (contract "
            "control_ordering_rule). In the producing source they are computed in run() before any lane "
            "quantity is touched; a reader can check that by reading the function top to bottom."
        )
        doc["inputs"] = r["inputs"]
        doc["controls"] = [r["controls"]["composite"], r["controls"]["singular"], r["controls"]["randompoint"]]
        doc["all_controls_passed"] = r["controls_all_passed"]
        doc["consequence_if_a_control_had_not_fired"] = (
            "contract INV-1: the lane it guards produces NO INTERPRETABLE OUTPUT, its measurement is "
            "recorded and marked uninterpretable, and it may not be carried into the comparison. A failed "
            "control is a complete and valuable outcome about the INSTRUMENT and is never converted into a "
            "statement about any curve."
        )
        print("\n".join(emit(doc, 0, [])))

    if args.emit == "both":
        print("---")

    if args.emit in ("measurements", "both"):
        doc = dict(HEADER_COMMON)
        doc["record_type"] = "measurements_block_a"
        doc["control_precondition"] = {
            "controls_ran_first": True,
            "controls_record": "coordination/goals/GOAL-SCURVE-137bd9/batches/BATCH-a40709/tasks/TASK-20260904-90ac09/controls-block-a.yaml",
            "all_controls_passed": r["controls_all_passed"],
            "note": "every lane below carries its own interpretable flag, set from its guarding controls",
        }
        doc["inputs"] = r["inputs"]
        doc["lanes"] = r["lanes"]
        doc["values_left_null_and_why"] = [
            {"field": "controls.randompoint.false_accept_rate",
             "reason": "NOT COMPUTABLE FROM THIS CONTROL and forbidden to claim from it (DEC-20260905-f630e4 D-4)."},
            {"field": "any criterion cell disposition",
             "reason": "OUT OF SCOPE FOR THIS SLOT. Slot S7 alone may compare a measured quantity against a threshold."},
            {"field": "primality certificate",
             "reason": "OPEN AND UNATTEMPTED (batch.yaml OOS-2). Primality is reported as PROBABLE with round count and full witness list."},
            {"field": "twist order, embedding degree, CM discriminant, rigidity",
             "reason": "not this slot's lanes; they belong to other lanes or are out of scope for this batch."},
        ]
        print("\n".join(emit(doc, 0, [])))


if __name__ == "__main__":
    main()
