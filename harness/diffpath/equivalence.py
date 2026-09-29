"""The DECLARED EQUIVALENCE RELATION: generators E1..E6, each VERIFIED or EXCLUDED.

"Two paths are the same object" is a DECLARATION, not a discovery, and the
declaration is only worth something if each generator is CHECKED.  Every
function `check_E*` below returns integer pass/fail counts and a verdict; a
generator whose check fails is EXCLUDED and named, and the strict group is
exactly the verified subset (IR-5).

QUANTIFIER ORDER, restated because every record restating the verdict must
restate it: FOR EVERY candidate path P, THERE EXISTS a census entry C and THERE
EXISTS a group element g in <verified generators> with g(P) = C, where g may
depend on BOTH P and C.  It is NOT claimed that one g works for all P, and NOT
claimed that the group is the full symmetry group of the difference space.

DECLARED INTERPRETATION, recorded because two clauses of the frozen contract
would otherwise read as contradictory.  E1 identifies a DV "read at a different
offset", while `declared_non_generators` says "a different step_range" is a
genuinely different object.  The only reading under which both hold is:
E1 shifts the WINDOW OFFSET at CONSTANT LENGTH; a different step_range LENGTH
(or extent) is never absorbed.  That is what is implemented, and a reviewer who
disagrees is disagreeing with a stated choice rather than with a hidden one.
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

from . import primitives as P
from .pathobj import (Condition, PathObject, bsdr_alternative, bsdr_decode,
                      bsdr_encode, plant_from_pair, seeded_pair, signed_bit_diff)
from .verifier import conforms

MASK32 = P.MASK32

E1_SHIFTS = (1, 2, 3, 4, 5, 6, 7, 8)   # declared shift set for E1 orbit images
E5_VARS = 8                            # bounded condition alphabet for E5
E5_STRINGS = 256
E6_RANGES = ((0, 0), (0, 3))           # BOTH gate E6; see check_E6


@dataclass
class GeneratorVerdict:
    id: str
    name: str
    statement: str
    verification_check: str
    passed: int
    failed: int
    verdict: str                       # VERIFIED | EXCLUDED
    failing_case: str | None = None
    scope_limit: str | None = None
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# generator ACTIONS on path objects
# ---------------------------------------------------------------------------

def act_E1_shift(obj: PathObject, s: int) -> PathObject:
    """Read the same SHA-1 codeword at offset +s, at constant length."""
    if obj.primitive != "sha1" or obj.dv is None:
        raise ValueError("E1 acts on sha1 objects only")
    full = P.sha1_expand(list(obj.dv_seed_window), 80 + max(E1_SHIFTS) + obj.length)
    a, b = obj.step_range
    new = PathObject(
        id=f"{obj.id}~E1s{s}", primitive="sha1", step_range=(a + s, b + s),
        provenance=obj.provenance, source_ref=obj.source_ref, status=obj.status,
        conditions=tuple(Condition(c.step + s, c.operand, c.bit, c.value, c.value_p)
                         for c in obj.conditions),
        path_data={"kind": "E1_image", "of": obj.id, "shift": s},
        step_delta=obj.step_delta, step_delta_signed=obj.step_delta_signed,
        dv=tuple(full[a + s:b + s + 1]),
        dv_seed_window=tuple(full[s:s + 16]),
        in_linearized_code=obj.in_linearized_code,
        cv=obj.cv, m=obj.m, mp=obj.mp, block_index=obj.block_index,
    )
    return new


def align_E1(obj: PathObject) -> PathObject:
    """E1 normalisation: re-read the object at offset 0, at constant length."""
    if obj.primitive != "sha1" or obj.dv is None:
        return obj
    s = obj.step_range[0]
    if s == 0:
        return obj
    full = P.sha1_expand_back(list(obj.dv_seed_window), s)   # s words prepended
    seed0 = tuple(full[:16])
    expanded = P.sha1_expand(list(seed0), 80 + obj.length)
    a, b = obj.step_range
    out = PathObject(
        id=obj.id, primitive="sha1", step_range=(0, obj.length - 1),
        provenance=obj.provenance, source_ref=obj.source_ref, status=obj.status,
        conditions=tuple(Condition(c.step - s, c.operand, c.bit, c.value, c.value_p)
                         for c in obj.conditions),
        path_data=obj.path_data,
        step_delta=obj.step_delta, step_delta_signed=obj.step_delta_signed,
        dv=tuple(expanded[0:obj.length]), dv_seed_window=seed0,
        in_linearized_code=obj.in_linearized_code,
        cv=obj.cv, m=obj.m, mp=obj.mp, block_index=obj.block_index,
    )
    return out


def act_E2_rotate(obj: PathObject, b: int, with_conditions: bool = True) -> PathObject:
    """E2 (CONJECTURED): relabel every bit by a simultaneous left-rotation."""
    if obj.primitive != "sha1":
        raise ValueError("E2 acts on sha1 objects only")
    rot_signed = tuple(tuple(((j + b) % 32, s) for (j, s) in sd)
                       for sd in obj.step_delta_signed)
    new_delta = tuple(bsdr_decode(sd) for sd in rot_signed)
    return PathObject(
        id=f"{obj.id}~E2r{b}", primitive="sha1", step_range=obj.step_range,
        provenance=obj.provenance, source_ref=obj.source_ref, status=obj.status,
        conditions=(tuple(Condition(c.step, c.operand, (c.bit + b) % 32,
                                    c.value, c.value_p) for c in obj.conditions)
                    if with_conditions else ()),
        path_data={"kind": "E2_image", "of": obj.id, "rot": b},
        step_delta=new_delta, step_delta_signed=rot_signed,
        dv=tuple(P.rotl(w, b) for w in obj.dv) if obj.dv else None,
        dv_seed_window=(tuple(P.rotl(w, b) for w in obj.dv_seed_window)
                        if obj.dv_seed_window else None),
        in_linearized_code=obj.in_linearized_code,
        cv=obj.cv,
        m=tuple(P.rotl(w, b) for w in obj.m) if obj.m else None,
        mp=tuple(P.rotl(w, b) for w in obj.mp) if obj.mp else None,
        block_index=obj.block_index,
    )


def act_E3_negate(obj: PathObject, with_conditions: bool = True) -> PathObject:
    """E3: swap the two members of the pair; every signed difference negates."""
    neg_signed = tuple(tuple((j, -s) for (j, s) in sd) for sd in obj.step_delta_signed)
    return PathObject(
        id=f"{obj.id}~E3", primitive=obj.primitive, step_range=obj.step_range,
        provenance=obj.provenance, source_ref=obj.source_ref, status=obj.status,
        conditions=(tuple(c.swapped() for c in obj.conditions)
                    if with_conditions else ()),
        path_data={"kind": "E3_image", "of": obj.id},
        step_delta=tuple((-d) & MASK32 for d in obj.step_delta),
        step_delta_signed=neg_signed,
        delta_m=(tuple((-d) & MASK32 for d in obj.delta_m)
                 if obj.delta_m is not None else None),
        delta_m_signed=(tuple(bsdr_encode((-d) & MASK32) for d in obj.delta_m)
                        if obj.delta_m is not None else None),
        dv=obj.dv, dv_seed_window=obj.dv_seed_window,
        in_linearized_code=obj.in_linearized_code,
        cv=obj.cv, m=obj.mp, mp=obj.m, block_index=obj.block_index,
    )


def act_E6_reindex(obj: PathObject, new_index: int) -> PathObject:
    """E6: the SAME per-block characteristic at a different block index."""
    out = PathObject(**{**obj.__dict__})
    out.id = f"{obj.id}~E6b{new_index}"
    out.block_index = new_index
    out.path_data = {"kind": "E6_image", "of": obj.id, "block_index": new_index}
    return out


# ---------------------------------------------------------------------------
# E5: the condition-set normal form, on a BOUNDED alphabet
# ---------------------------------------------------------------------------

def e5_normal_form(atoms):
    """Normal form of a condition string over the bounded alphabet.

    Atoms: ('lit', i, v) meaning x_i == v; ('eq', i, j); ('neq', i, j).
    The normal form runs union-find over equalities, propagates constants,
    detects contradiction (returning the UNSAT sentinel), and emits a sorted,
    deduplicated canonical atom list.  DECIDABLE by construction on this
    alphabet -- and E5 is EXCLUDED rather than weakened into a syntactic match
    if the enumeration below ever disagrees with it.
    """
    parent = list(range(E5_VARS))
    parity = [0] * E5_VARS

    def find(a):
        if parent[a] == a:
            return a, 0
        r, p = find(parent[a])
        parent[a] = r
        parity[a] ^= p
        return r, parity[a]

    def union(a, b, rel):        # x_a == x_b ^ rel
        ra, pa = find(a)
        rb, pb = find(b)
        if ra == rb:
            return (pa ^ pb) == rel
        parent[ra] = rb
        parity[ra] = pa ^ pb ^ rel
        return True

    const: dict[int, int] = {}
    ok = True
    for at in atoms:
        if at[0] == "eq":
            ok &= union(at[1], at[2], 0)
        elif at[0] == "neq":
            ok &= union(at[1], at[2], 1)
    for at in atoms:
        if at[0] == "lit":
            r, p = find(at[1])
            v = at[2] ^ p
            if r in const and const[r] != v:
                ok = False
            const[r] = v
    if not ok:
        return ("UNSAT",)
    out = []
    for i in range(E5_VARS):
        r, p = find(i)
        if r in const:
            out.append(("lit", i, const[r] ^ p))
        elif r != i:
            out.append(("eq" if p == 0 else "neq", min(i, r), max(i, r)))
    return tuple(sorted(set(out)))


def e5_solutions(atoms) -> frozenset:
    if atoms == ("UNSAT",):
        return frozenset()
    sols = []
    for a in range(1 << E5_VARS):
        bits = [(a >> i) & 1 for i in range(E5_VARS)]
        good = True
        for at in atoms:
            if at[0] == "lit" and bits[at[1]] != at[2]:
                good = False
            elif at[0] == "eq" and bits[at[1]] != bits[at[2]]:
                good = False
            elif at[0] == "neq" and bits[at[1]] == bits[at[2]]:
                good = False
            if not good:
                break
        if good:
            sols.append(a)
    return frozenset(sols)


# ---------------------------------------------------------------------------
# the six verification checks
# ---------------------------------------------------------------------------

def check_E1(seed: int, trials: int = 64) -> GeneratorVerdict:
    rng = random.Random(seed + 1)
    ok = bad = 0
    failing = None
    for _ in range(trials):
        w16 = [rng.getrandbits(32) for _ in range(16)]
        base = P.sha1_expand(w16, 80)
        for s in E1_SHIFTS:
            shifted = P.sha1_expand(base[s:s + 16], 80 - s)
            if shifted == base[s:80]:
                ok += 1
            else:
                bad += 1
                failing = failing or f"forward shift s={s}"
        # backward: recover the offset-0 reading from a shifted window
        for s in (1, 4, 8):
            back = P.sha1_expand_back(base[s:s + 16], s)
            if back[:16] == base[s - s:16] and P.sha1_expand(back[:16], 80) == base:
                ok += 1
            else:
                bad += 1
                failing = failing or f"backward shift s={s}"
    return GeneratorVerdict(
        "E1", "step_shift_sha1",
        "A SHA-1 DV is a codeword of the linearized expansion; two DVs related "
        "by a whole-step shift of the expansion window are the same codeword "
        "read at a different offset.",
        f"expand from the shifted seed window and require exact equality over "
        f"the overlapping steps, forward shifts {E1_SHIFTS} and backward shifts "
        f"(1,4,8), on {trials} seeded random codewords",
        ok, bad, "VERIFIED" if bad == 0 else "EXCLUDED", failing,
        scope_limit="Shift at CONSTANT LENGTH only; a different step_range "
                    "length or extent is a declared_non_generator and is never "
                    "absorbed.")


def check_E2(seed: int, trials: int = 64) -> GeneratorVerdict:
    """E2 IS A CONJECTURE AND IS TREATED AS ONE.

    Two independent parts, and the contract requires BOTH: the expansion part
    and the STEP-FUNCTION part.  A generator that commutes with the linear
    expansion but not with the step function is not an equivalence of PATHS.
    """
    rng = random.Random(seed + 2)
    exp_ok = exp_bad = 0
    for _ in range(trials):
        w16 = [rng.getrandbits(32) for _ in range(16)]
        base = P.sha1_expand(w16, 80)
        for b in range(32):
            lhs = [P.rotl(x, b) for x in base]
            rhs = P.sha1_expand([P.rotl(x, b) for x in w16], 80)
            if lhs == rhs:
                exp_ok += 1
            else:
                exp_bad += 1

    step_ok = step_bad = 0
    failing = None
    for _ in range(8):
        cv, m, mp = seeded_pair(rng, "sha1")
        obj = plant_from_pair("E2-probe", "sha1", cv, m, mp, (0, 79))
        for b in range(1, 32):
            img = act_E2_rotate(obj, b)
            rm = [P.rotl(x, b) for x in m]
            rmp = [P.rotl(x, b) for x in mp]
            res = conforms(img, cv, rm, rmp)
            if res.conforming:
                step_ok += 1
            else:
                step_bad += 1
                if failing is None:
                    failing = (f"rotation b={b}: the rotated pair conforms to the "
                               f"rotated path at only {res.steps_matching}/"
                               f"{res.steps_total} steps (first mismatch at step "
                               f"{res.first_mismatch_step}); SHA-1's step "
                               f"function adds modularly and adds a FIXED "
                               f"constant K_t, neither of which commutes with a "
                               f"bit rotation")
    verdict = "VERIFIED" if (exp_bad == 0 and step_bad == 0) else "EXCLUDED"
    return GeneratorVerdict(
        "E2", "bit_rotation_sha1",
        "CONJECTURE: SHA-1's expansion and step function commute with a "
        "simultaneous left-rotation of every message word.",
        f"part 1, expansion: rot(expand(DV),b) == expand(rot(DV,b)) for all "
        f"b in 0..31 on {trials} seeded codewords; part 2, step function: a "
        f"conforming pair is carried to a conforming pair for the rotated path. "
        f"EITHER failing excludes E2.",
        exp_ok + step_ok, exp_bad + step_bad, verdict, failing,
        extra={"expansion_pass": exp_ok, "expansion_fail": exp_bad,
               "step_function_pass": step_ok, "step_function_fail": step_bad,
               "recalled_pointer_note":
                   "The Coordinator's recollection that published DV families "
                   "carry a rotation index is a `recalled` pointer and was NOT "
                   "treated as a reason to admit E2."})


def check_E3(seed: int, trials: int = 64) -> GeneratorVerdict:
    rng = random.Random(seed + 3)
    ok = bad = 0
    failing = None
    for prim, steps in (("md5", 64), ("sha1", 80)):
        for _ in range(trials):
            cv, m, mp = seeded_pair(rng, prim)
            obj = plant_from_pair("E3-probe", prim, cv, m, mp, (0, steps - 1))
            neg = act_E3_negate(obj)
            swapped = plant_from_pair("E3-swap", prim, cv, mp, m, (0, steps - 1))
            same = (neg.step_delta == swapped.step_delta
                    and sorted(c.key() for c in neg.conditions)
                    == sorted(c.key() for c in swapped.conditions))
            res = conforms(neg, cv, mp, m)
            if same and res.conforming:
                ok += 1
            else:
                bad += 1
                failing = failing or f"{prim}: negated path not conforming for swapped pair"
    return GeneratorVerdict(
        "E3", "global_sign_flip",
        "Swapping the two members of the message pair negates every signed "
        "difference; a path and its negation are the same object.",
        f"negate every signed difference and require the negated path to be "
        f"conforming for the swapped pair, exactly, on {trials} seeded planted "
        f"paths per primitive",
        ok, bad, "VERIFIED" if bad == 0 else "EXCLUDED", failing)


def check_E4(seed: int, trials: int = 4096) -> GeneratorVerdict:
    rng = random.Random(seed + 4)
    rt_ok = rt_bad = 0
    for _ in range(trials):
        d = rng.getrandbits(32)
        if bsdr_decode(bsdr_encode(d)) == d:
            rt_ok += 1
        else:
            rt_bad += 1
    alt_ok = alt_bad = 0
    failing = None
    for _ in range(256):
        d = rng.getrandbits(32)
        r1, r2 = bsdr_encode(d), bsdr_alternative(d)
        if r1 != r2 and bsdr_decode(r1) == bsdr_decode(r2) == d:
            alt_ok += 1
        else:
            alt_bad += 1
            failing = failing or f"alternative representation of delta={d:#010x}"
    # two distinct signed representations of one modular difference must
    # canonicalise identically AND admit the same conforming pairs.
    pair_ok = pair_bad = 0
    for _ in range(16):
        cv, m, mp = seeded_pair(rng, "md5")
        obj = plant_from_pair("E4-probe", "md5", cv, m, mp, (0, 63))
        variant = PathObject(**{**obj.__dict__})
        variant.delta_m_signed = tuple(bsdr_alternative(d) for d in obj.delta_m)
        variant.step_delta_signed = tuple(bsdr_alternative(d) for d in obj.step_delta)
        if (variant.delta_m == obj.delta_m
                and variant.step_delta == obj.step_delta
                and conforms(variant, cv, m, mp).conforming):
            pair_ok += 1
        else:
            pair_bad += 1
            failing = failing or "re-represented path did not admit the same pair"
    bad = rt_bad + alt_bad + pair_bad
    return GeneratorVerdict(
        "E4", "signed_digit_representation_md5",
        "A modular difference in Z/2^32 has many binary signed-digit "
        "representations; the canonical form is the modular difference itself.",
        f"round-trip {trials} seeded random modular differences through the "
        f"signed-digit encoder/decoder; then require two DISTINCT signed "
        f"representations of one modular difference to canonicalise identically "
        f"and to admit the same conforming pairs on a planted path",
        rt_ok + alt_ok + pair_ok, bad,
        "VERIFIED" if bad == 0 else "EXCLUDED", failing,
        extra={"roundtrip_pass": rt_ok, "roundtrip_fail": rt_bad,
               "distinct_representation_pass": alt_ok,
               "distinct_representation_fail": alt_bad,
               "conforming_pair_pass": pair_ok, "conforming_pair_fail": pair_bad})


def check_E5(seed: int, trials: int = E5_STRINGS) -> GeneratorVerdict:
    rng = random.Random(seed + 5)
    ok = bad = 0
    failing = None
    for _ in range(trials):
        n = rng.randrange(1, 9)
        atoms = []
        for _ in range(n):
            kind = rng.choice(["lit", "eq", "neq"])
            if kind == "lit":
                atoms.append(("lit", rng.randrange(E5_VARS), rng.randrange(2)))
            else:
                i, j = rng.sample(range(E5_VARS), 2)
                atoms.append((kind, i, j))
        nf = e5_normal_form(atoms)
        if e5_solutions(atoms) == e5_solutions(nf):
            ok += 1
        else:
            bad += 1
            failing = failing or f"condition string {atoms} vs normal form {nf}"
    return GeneratorVerdict(
        "E5", "condition_set_normalisation",
        "Two paths whose sufficient-condition sets have the same solution set "
        "are the same object; the canonical form is a declared normal form of "
        "the condition set.",
        f"on a bounded condition alphabet ({E5_VARS} boolean variables; atoms "
        f"lit/eq/neq), enumerate the solution set of the condition string and "
        f"of its normal form over all 2^{E5_VARS} assignments and require exact "
        f"set equality, on {trials} seeded random condition strings",
        ok, bad, "VERIFIED" if bad == 0 else "EXCLUDED", failing,
        scope_limit=(f"DECIDED ON THE BOUNDED ALPHABET ONLY: {E5_VARS} variables, "
                     f"atoms lit/eq/neq, full 2^{E5_VARS} enumeration. This is "
                     f"NOT a claim that the normal form is decidable on the full "
                     f"per-step 32-bit condition sets of a real characteristic; "
                     f"that is untested here and is a stated limit."))


def check_E6(seed: int) -> GeneratorVerdict:
    """E6, gated on the CONJUNCTION of two step ranges, declared before running.

    Part (a) is structural: `verifier.conforms()` takes no block-index
    parameter, so the conformance predicate CANNOT read it; the check exercises
    that by re-indexing an object and requiring identical verdicts.

    Part (b) is the chaining-value clause, and it is where a vacuous pass is
    possible: "a conforming pair at one chaining value yields a conforming pair
    at a second one WHENEVER THE CONDITIONS ARE SATISFIED" is trivially true if
    no draw ever satisfies the conditions.  So the check requires
    satisfied > 0 as well as violations == 0, and reports both integers.

    THE RANGE SET IS THE CONJUNCTION OF (0,0) AND (0,3), FIXED BEFORE THE RUN.
    (0,0) is the range where this module's carry-window condition set is
    PROVABLY sufficient (the step's only difference is delta_m, so no Boolean-
    function difference arises).  (0,3) is not, and could fail.  Gating on both
    is the stricter choice and was taken precisely so that the range could not
    be selected after seeing which one passes.
    """
    rng = random.Random(seed + 6)
    ok = bad = 0
    failing = None
    per_range = {}

    # part (a): block-index independence, structural
    for _ in range(16):
        cv, m, mp = seeded_pair(rng, "md5")
        obj = plant_from_pair("E6-probe", "md5", cv, m, mp, (0, 63))
        r0 = conforms(obj, cv, m, mp)
        r1 = conforms(act_E6_reindex(obj, 7), cv, m, mp)
        if (r0.conforming and r1.conforming
                and (r0.steps_matching, r0.conditions_failed)
                == (r1.steps_matching, r1.conditions_failed)):
            ok += 1
        else:
            bad += 1
            failing = failing or "conformance verdict changed with block index"

    # part (b): second chaining value
    for rng_pair in E6_RANGES:
        sat = viol = 0
        cv1 = P.MD5_IV
        rr = random.Random(seed + 600 + rng_pair[1])
        m0 = [rr.getrandbits(32) for _ in range(16)]
        delta = [0] * 16
        delta[0] = 1 << rr.randrange(28)
        mp0 = [P.add32(m0[j], delta[j]) for j in range(16)]
        obj = plant_from_pair("E6-block", "md5", cv1, m0, mp0, rng_pair)
        cv2 = tuple(rr.getrandbits(32) for _ in range(4))     # second seeded CV
        for _ in range(4096):
            n = [rr.getrandbits(32) for _ in range(16)]
            npr = [P.add32(n[j], delta[j]) for j in range(16)]
            res = conforms(obj, cv2, n, npr)
            if res.conditions_satisfied:
                sat += 1
                if not res.conforming:
                    viol += 1
        per_range[str(rng_pair)] = {"draws": 4096, "conditions_satisfied": sat,
                                    "condition_satisfying_nonconforming": viol}
        if sat > 0 and viol == 0:
            ok += 1
        else:
            bad += 1
            if failing is None:
                failing = (f"step_range {rng_pair}: {sat} of 4096 seeded draws at "
                           f"the second chaining value satisfied the conditions, "
                           f"{viol} of those did not conform"
                           + (" (VACUOUS: no draw satisfied the conditions, so "
                              "the implication is empty and is NOT reported as a "
                              "pass)" if sat == 0 else ""))
    return GeneratorVerdict(
        "E6", "block_index_reuse",
        "The same per-block characteristic used at a different block index or "
        "from a different chaining value is the same object AS A PER-BLOCK "
        "CHARACTERISTIC.",
        "part (a) the conformance predicate does not read the block index "
        "(structural: conforms() has no such parameter) and re-indexing leaves "
        "every verdict identical; part (b) at a second seeded chaining value, "
        f"4096 seeded draws per step_range in {E6_RANGES}, require "
        "condition-satisfying draws > 0 (non-vacuity) and zero "
        "condition-satisfying non-conforming draws. GATED ON THE CONJUNCTION "
        "OF BOTH RANGES, fixed before the run.",
        ok, bad, "VERIFIED" if bad == 0 else "EXCLUDED", failing,
        extra={"per_step_range": per_range})


ALL_GENERATORS = ("E1", "E2", "E3", "E4", "E5", "E6")


def run_all_checks(seed: int) -> dict:
    verdicts = [check_E1(seed), check_E2(seed), check_E3(seed),
                check_E4(seed), check_E5(seed), check_E6(seed)]
    return {v.id: v for v in verdicts}


DECLARED_NON_GENERATORS = (
    "a different set of active message words",
    "a different Hamming weight of delta_m or of the DV",
    "a different number of near-collision blocks",
    "a DV outside the linearized code",
    "a different step_range (length/extent)",
)


def ground_truth_signature(obj: PathObject) -> tuple:
    """The declared_non_generators, as a computable signature.

    Two objects with DIFFERENT signatures are declared-distinct ground-truth
    objects: an adjudicator that gives them one canonical form is broken, and
    CTL-OBS direction (i) is where that shows up.
    """
    if obj.primitive == "md5":
        active = tuple(j for j, d in enumerate(obj.delta_m or ()) if d)
        weight = sum(bin(d).count("1") for d in (obj.delta_m or ()))
        code = None
    else:
        active = tuple(j for j, d in enumerate(obj.dv_seed_window or ()) if d)
        weight = sum(bin(d).count("1") for d in (obj.dv or ()))
        code = obj.in_linearized_code
    return (obj.primitive, active, weight, code, obj.length,
            obj.notes.get("blocks", 1))
