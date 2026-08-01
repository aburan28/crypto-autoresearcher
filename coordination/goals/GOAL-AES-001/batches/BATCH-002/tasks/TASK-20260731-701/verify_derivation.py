#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_derivation.py
====================

Independent recomputation of every numerical claim made in

    derivation_note_column_local_obstructions.md

(TASK-20260731-701, GOAL-AES-001 BATCH-002).

The script is SELF-CONTAINED: it implements GF(2^8) arithmetic, the AES
MixColumns matrix, the AES S-box affine layer and byte-wise inversion from
scratch and depends on nothing outside the Python standard library.  It
additionally attempts a READ-ONLY cross-check of its hard-coded constants
against the admitted TASK-20260731-602 harness (aes_reduced.py); if that file
is absent or fails to import, the cross-check reports SKIP and no other claim
is affected.

Every randomised check is seeded from a constant recorded in this file, so the
output is bit-for-bit reproducible.

Usage (from any working directory):

    python3 verify_derivation.py

Exit status is 0 iff no claim FAILs.  SKIP does not fail the run and is
reported explicitly.  Each claim prints exactly one line beginning "CLAIM ".

NOTHING IN THIS SCRIPT IS A CRYPTANALYTIC CLAIM ABOUT AES.  It checks
elementary algebraic facts about AES components, at no round count.

EXECUTION STATUS IN THE AUTHORING SESSION: NOT RUN.  The authoring agent had
no command-execution tool, so no output of this script is transcribed anywhere
in this task's artifacts.  Under AGENTS.md rule 9 an unobserved output is never
reported as observed.  The expected value of every claim is DERIVED
analytically in the accompanying note and is encoded in the PASS conditions
below; TASK-20260731-705 re-executes this file from committed source.

inference:
  policy: research-deep
  requested_policy: research-deep
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    Structural. Under this Claude Code harness the orchestration/model-policies.yaml
    policy aliases cannot be resolved by subagent frontmatter (CLAUDE.md, "Model
    policy note"); all subagents run `model: inherit`.
  model_verified: false          # `python3 -m orchestration.adapter doctor --probe` NOT run
  reasoning_effort: unrecorded
  independent_session: false
  standing_basis: inference-amendment commit 0137a051eb5828789eb267fa83c8278086578d4c
"""

from __future__ import annotations

import os
import random
import sys
from typing import List, Sequence, Tuple

# ---------------------------------------------------------------------------
# Recorded seeds and sample sizes.  Changing any of these changes the output.
# ---------------------------------------------------------------------------
SEED_C6B = 202608010001      # Inv-collinearity, all coordinates nonzero
SEED_C6C = 202608010002      # Inv-collinearity, at least one zero coordinate
SEED_C7A = 202608010003      # collinearity under the affine layer L
SEED_C7B = 202608010004      # collinearity under the full S-box S = L o Inv

N_SAMPLES = 4000             # samples per randomised collinearity check

Q = 256                      # |GF(2^8)|
MODULUS = 0x11B              # x^8 + x^4 + x^3 + x + 1


# ---------------------------------------------------------------------------
# GF(2^8): a slow reference multiplication, then log/antilog tables built from
# it, then a table-based fast path.  Claim C_TAB checks the two agree on all
# 65536 ordered pairs, so the tables are not taken on trust.
# ---------------------------------------------------------------------------

def gmul_ref(a: int, b: int) -> int:
    """Reference GF(2^8) multiplication (shift-and-add), used to build and to
    audit the tables."""
    a &= 0xFF
    b &= 0xFF
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & 0x100:
            a ^= MODULUS
    return r & 0xFF


def _build_tables():
    exp = [0] * 512
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x = gmul_ref(x, 0x03)        # 0x03 is a generator of GF(2^8)^*
    for i in range(255, 512):
        exp[i] = exp[i - 255]
    return exp, log


_EXP, _LOG = _build_tables()


def gmul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def ginv(a: int) -> int:
    """Multiplicative inverse in GF(2^8).  ginv(0) = 0 is the AES convention
    and is applied explicitly here rather than left undefined."""
    if a == 0:
        return 0
    return _EXP[255 - _LOG[a]] if _LOG[a] else 1


# ---------------------------------------------------------------------------
# The AES MixColumns matrix M (circulant, first row 02 03 01 01)
# ---------------------------------------------------------------------------

M = (
    (0x02, 0x03, 0x01, 0x01),
    (0x01, 0x02, 0x03, 0x01),
    (0x01, 0x01, 0x02, 0x03),
    (0x03, 0x01, 0x01, 0x02),
)

I4 = tuple(tuple(1 if i == j else 0 for j in range(4)) for i in range(4))


def mat_mul(a, b):
    n = len(a)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            acc = 0
            for k in range(n):
                acc ^= gmul(a[i][k], b[k][j])
            row.append(acc)
        out.append(tuple(row))
    return tuple(out)


def mat_pow(a, e: int):
    r = I4
    for _ in range(e):
        r = mat_mul(r, a)
    return r


def mat_add(a, b):
    return tuple(tuple(x ^ y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def mat_vec(a, v: Sequence[int]) -> Tuple[int, ...]:
    return tuple(
        gmul(a[i][0], v[0]) ^ gmul(a[i][1], v[1])
        ^ gmul(a[i][2], v[2]) ^ gmul(a[i][3], v[3])
        for i in range(4)
    )


def rank_gf256(a) -> int:
    """Rank over GF(2^8) by Gauss-Jordan elimination."""
    m = [list(row) for row in a]
    n = len(m)
    row = 0
    rank = 0
    for col in range(n):
        piv = None
        for r in range(row, n):
            if m[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        m[row], m[piv] = m[piv], m[row]
        pinv = ginv(m[row][col])
        m[row] = [gmul(pinv, x) for x in m[row]]
        for r in range(n):
            if r != row and m[r][col]:
                f = m[r][col]
                m[r] = [x ^ gmul(f, y) for x, y in zip(m[r], m[row])]
        row += 1
        rank += 1
    return rank


# ---------------------------------------------------------------------------
# The AES S-box factorisation S = L o Inv
# ---------------------------------------------------------------------------

def affine_L(b: int) -> int:
    """The AES S-box GF(2)-affine layer:
       b'_i = b_i ^ b_{i+4} ^ b_{i+5} ^ b_{i+6} ^ b_{i+7} ^ c_i, i mod 8,
       c = 0x63.  This is L; the S-box is S = L o Inv."""
    out = 0
    for i in range(8):
        bit = (
            ((b >> i) & 1)
            ^ ((b >> ((i + 4) % 8)) & 1)
            ^ ((b >> ((i + 5) % 8)) & 1)
            ^ ((b >> ((i + 6) % 8)) & 1)
            ^ ((b >> ((i + 7) % 8)) & 1)
            ^ ((0x63 >> i) & 1)
        )
        out |= bit << i
    return out


def sbox(b: int) -> int:
    return affine_L(ginv(b))


def vec_inv(v):
    return tuple(ginv(x) for x in v)


def vec_L(v):
    return tuple(affine_L(x) for x in v)


def vec_S(v):
    return tuple(sbox(x) for x in v)


def scal(lam: int, v):
    return tuple(gmul(lam, x) for x in v)


def is_zero(v) -> bool:
    return all(x == 0 for x in v)


def is_constant(v) -> bool:
    return len(set(v)) == 1


def collinear(v, w) -> bool:
    """True iff v and w are both nonzero and w = lambda * v for some
    lambda in GF(2^8)^*.  Collinearity is defined on NONZERO vectors only."""
    if is_zero(v) or is_zero(w):
        return False
    idx = next(i for i, x in enumerate(v) if x != 0)
    lam = gmul(w[idx], ginv(v[idx]))
    if lam == 0:
        return False
    return all(w[i] == gmul(lam, v[i]) for i in range(len(v)))


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

_RESULTS: List[Tuple[str, str, str]] = []


def report(cid: str, ok, detail: str) -> None:
    status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
    _RESULTS.append((cid, status, detail))
    print("CLAIM %-5s %-4s %s" % (cid, status, detail))


# ===========================================================================
# CLAIMS
# ===========================================================================

def claim_CTAB_table_audit() -> None:
    """C-TAB: the log/antilog fast path agrees with the reference
    shift-and-add multiplication on all 256 x 256 ordered pairs, and the
    inverse table satisfies a * ginv(a) = 1 for all a != 0 with ginv(0) = 0."""
    bad_mul = 0
    for a in range(256):
        for b in range(256):
            if gmul(a, b) != gmul_ref(a, b):
                bad_mul += 1
    bad_inv = sum(1 for a in range(1, 256) if gmul_ref(a, ginv(a)) != 1)
    bad_inv += 0 if ginv(0) == 0 else 1
    report("C-TAB", bad_mul == 0 and bad_inv == 0,
           "table multiplication matches the reference on %d/65536 ordered pairs; "
           "inverse table correct on 255/255 nonzero elements with ginv(0)=0; "
           "%d mul failures, %d inv failures" % (65536 - bad_mul, bad_mul, bad_inv))


def claim_C0_harness_crosscheck() -> None:
    """C0: this script's hard-coded constants agree with the admitted
    TASK-20260731-602 harness.  READ-ONLY.  SKIP if unavailable."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(
        os.path.join(here, "..", "..", "..", "BATCH-001", "tasks",
                     "TASK-20260731-602", "aes_reduced.py")
    )
    if not os.path.isfile(path):
        report("C0", None, "harness aes_reduced.py not found at %s; skipped" % path)
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("aes_reduced_readonly", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception as exc:
        report("C0", None, "harness import failed (%s: %s); skipped"
               % (type(exc).__name__, exc))
        return
    ok_mix = tuple(tuple(r) for r in mod.AES_MIX) == M
    ok_sbox = tuple(sbox(x) for x in range(256)) == tuple(mod.aes_sbox())
    ok_inv = all(ginv(x) == mod.GF.inv(x) for x in range(256))
    report("C0", ok_mix and ok_sbox and ok_inv,
           "MixColumns matrix, derived S-box (256/256) and GF(2^8) inverse (256/256) "
           "all agree with TASK-20260731-602 aes_reduced.py (module sha256 %s)"
           % getattr(mod, "MODULE_SHA256", "unavailable"))


def claim_C1_order_of_M() -> None:
    """C1 (Proposition 1): the multiplicative order of M in GL(4, GF(2^8))
    is exactly 4."""
    powers = {e: mat_pow(M, e) for e in range(1, 6)}
    order = next((e for e in range(1, 6) if powers[e] == I4), None)
    report("C1", order == 4,
           "order(M) = %s ; M^1 != I, M^2 != I, M^3 != I, M^4 = I ; "
           "M^2 = %s" % (order, [list(r) for r in powers[2]]))


def claim_C2_index_in_GL() -> None:
    """C2 (Consequence 1.1): |<M>| = 4 against |GL(4, GF(2^8))|."""
    q = Q
    gl = (q**4 - 1) * (q**4 - q) * (q**4 - q**2) * (q**4 - q**3)
    prod = 1
    for i in range(4):
        prod *= (q**4 - q**i)
    ratio = 4.0 / gl
    report("C2", (gl == prod) and (1.0e-38 < ratio < 1.4e-38),
           "|GL(4,GF(2^8))| = prod_{i=0..3}(q^4 - q^i) = %d ; "
           "|<M>|/|GL| = 4/that = %.3e" % (gl, ratio))


def claim_C3_orbit_of_e1() -> None:
    """C3 (Consequence 1.2): the <M>-orbit of e1 = (1,0,0,0) has size 4."""
    e1 = (1, 0, 0, 0)
    orb = []
    v = e1
    for _ in range(4):
        orb.append(v)
        v = mat_vec(M, v)
    report("C3", (v == e1) and (len(set(orb)) == 4),
           "orbit(e1) under <M> = %s ; size %d ; returns to e1 after 4 steps"
           % ([[hex(x) for x in o] for o in orb], len(set(orb))))


def claim_C4_orbit_count_bound() -> None:
    """C4 (Consequence 1.3): there are q^4 - 1 = 4294967295 nonzero vectors,
    every <M>-orbit has size dividing 4, hence at least
    ceil((q^4-1)/4) = 1073741824 orbits -- which in particular is at least the
    figure 1073741823 recorded in EV-AES-001 observation B-3."""
    nz = Q**4 - 1
    lower = -(-nz // 4)
    report("C4", nz == 4294967295 and lower == 1073741824 and lower >= 1073741823,
           "q^4 - 1 = %d nonzero vectors ; orbit count >= ceil((q^4-1)/4) = %d "
           "(>= 1073741823, the figure recorded in EV-AES-001 B-3)" % (nz, lower))


def claim_C5_exact_orbit_count() -> None:
    """C5 (Consequence 1.3, sharp form): the exact number of <M>-orbits on
    nonzero vectors, by Burnside, cross-checked by orbit-size stratification."""
    nz = Q**4 - 1
    fixed = {}
    dims = {}
    for e in range(4):
        d = 4 - rank_gf256(mat_add(mat_pow(M, e), I4))
        dims[e] = d
        fixed[e] = Q**d - 1
    total = sum(fixed[e] for e in range(4))
    burnside = total // 4
    orb1 = fixed[1]
    orb2 = (fixed[2] - fixed[1]) // 2
    orb4 = (nz - fixed[2]) // 4
    strat = orb1 + orb2 + orb4
    ok = (total % 4 == 0 and burnside == strat and burnside == 1073758335
          and dims[1] == 1 and dims[2] == 2 and dims[3] == 1
          and fixed[1] == 255 and fixed[2] == 65535 and fixed[3] == 255)
    report("C5", ok,
           "dim ker(M^e - I) for e = 0,1,2,3 = %d,%d,%d,%d ; nonzero fixed points "
           "%d,%d,%d,%d ; Burnside count = %d ; stratified %d(size 1) + %d(size 2) "
           "+ %d(size 4) = %d"
           % (dims[0], dims[1], dims[2], dims[3],
              fixed[0], fixed[1], fixed[2], fixed[3],
              burnside, orb1, orb2, orb4, strat))


def claim_C6a_scalar_identity() -> None:
    """C6a (Proposition 2, scalar form, EXHAUSTIVE): for every lambda in
    GF(2^8)^* and every x in GF(2^8), Inv(lambda*x) = lambda^{-1}*Inv(x),
    INCLUDING x = 0 under the AES convention Inv(0) = 0."""
    bad = 0
    bad_at_zero = 0
    for lam in range(1, 256):
        li = ginv(lam)
        for x in range(256):
            if ginv(gmul(lam, x)) != gmul(li, ginv(x)):
                bad += 1
                if x == 0:
                    bad_at_zero += 1
    total = 255 * 256
    report("C6a", bad == 0,
           "exhaustive over 255 scalars x 256 field elements: %d/%d identities hold; "
           "255 of the checked cases are x = 0, where the convention Inv(0)=0 gives "
           "0 = lambda^{-1}*0; failures %d (of which %d at x = 0)"
           % (total - bad, total, bad, bad_at_zero))


def _random_vector(rng, force_zero_coord: bool, exclude_constant: bool):
    while True:
        if force_zero_coord:
            v = [rng.randrange(0, 256) for _ in range(4)]
            v[rng.randrange(0, 4)] = 0
        else:
            v = [rng.randrange(1, 256) for _ in range(4)]
        if is_zero(v):
            continue
        if exclude_constant and is_constant(v):
            continue
        return tuple(v)


def _collinearity_experiment(seed: int, force_zero_coord: bool, mapname: str,
                             exclude_constant: bool):
    """Draw N_SAMPLES collinear pairs (v, w = lambda*v) with lambda not in
    {0,1} and count how many stay collinear after the named byte-wise map."""
    rng = random.Random(seed)
    fn = {"Inv": vec_inv, "L": vec_L, "S": vec_S}[mapname]
    preserved = 0
    exact_identity = 0
    degenerate = 0
    for _ in range(N_SAMPLES):
        v = _random_vector(rng, force_zero_coord, exclude_constant)
        lam = rng.randrange(2, 256)
        w = scal(lam, v)
        fv, fw = fn(v), fn(w)
        if is_zero(fv) or is_zero(fw):
            degenerate += 1
            continue
        if collinear(fv, fw):
            preserved += 1
        if mapname == "Inv" and fw == scal(ginv(lam), fv):
            exact_identity += 1
    return preserved, exact_identity, degenerate


def claim_C6b_inv_all_coords_nonzero() -> None:
    p, ident, deg = _collinearity_experiment(SEED_C6B, False, "Inv", False)
    report("C6b", p == N_SAMPLES and ident == N_SAMPLES and deg == 0,
           "seed %d: %d/%d collinear pairs with ALL coordinates nonzero remain "
           "collinear under byte-wise Inv, and %d/%d satisfy "
           "Inv(lambda*v) = lambda^{-1}*Inv(v) exactly; %d degenerate images"
           % (SEED_C6B, p, N_SAMPLES, ident, N_SAMPLES, deg))


def claim_C6c_inv_with_zero_coord() -> None:
    p, ident, deg = _collinearity_experiment(SEED_C6C, True, "Inv", False)
    report("C6c", p == N_SAMPLES and ident == N_SAMPLES and deg == 0,
           "seed %d: %d/%d collinear pairs with AT LEAST ONE ZERO coordinate remain "
           "collinear under byte-wise Inv, and %d/%d satisfy the identity exactly "
           "(zero coordinates are fixed by the Inv(0)=0 convention); %d degenerate "
           "images" % (SEED_C6C, p, N_SAMPLES, ident, N_SAMPLES, deg))


def claim_C7a_L_breaks_collinearity() -> None:
    """C7a (Corollary 2.1): the byte-wise GF(2)-affine layer L does not
    preserve GF(2^8)-collinearity.  Constant vectors -- the degenerate family
    on which L DOES preserve it, see C8 -- are excluded from the sample."""
    p, _, deg = _collinearity_experiment(SEED_C7A, False, "L", True)
    report("C7a", p == 0,
           "seed %d: %d/%d non-constant collinear pairs remain collinear after the "
           "byte-wise affine layer L. Predicted 0. Two random nonzero 4-byte vectors "
           "are accidentally collinear with probability 255/(2^32-1) = 5.94e-08, so "
           "the expected accidental count over %d draws is 2.4e-04; the PASS "
           "condition is deliberately strict at exactly 0 so that any hit is "
           "surfaced. %d degenerate images"
           % (SEED_C7A, p, N_SAMPLES, N_SAMPLES, deg))


def claim_C7b_S_breaks_collinearity() -> None:
    """C7b: the full AES S-box S = L o Inv likewise does not preserve
    GF(2^8)-collinearity -- the failure is contributed entirely by L, since
    C6a-C6c show Inv preserves it."""
    p, _, deg = _collinearity_experiment(SEED_C7B, False, "S", True)
    report("C7b", p == 0,
           "seed %d: %d/%d non-constant collinear pairs remain collinear after the "
           "full S-box S = L o Inv. Predicted 0, same accidental rate as C7a. "
           "%d degenerate images" % (SEED_C7B, p, N_SAMPLES, deg))


def claim_C7c_deterministic_counterexample() -> None:
    """C7c (Corollary 2.1, deterministic form): an explicit hand-checkable
    counterexample.  v = (01,00,00,00), lambda = 02, w = (02,00,00,00).
    L(01) = 0x7C and L(02) = 0x5D and L(00) = 0x63, so
    L(v) = (7C,63,63,63) and L(w) = (5D,63,63,63): the three equal
    coordinates force the scalar to be 1, but 0x7C != 0x5D."""
    v = (0x01, 0x00, 0x00, 0x00)
    w = scal(0x02, v)
    lv, lw = vec_L(v), vec_L(w)
    ok = (w == (0x02, 0x00, 0x00, 0x00)
          and lv == (0x7C, 0x63, 0x63, 0x63)
          and lw == (0x5D, 0x63, 0x63, 0x63)
          and not collinear(lv, lw)
          and collinear(v, w)
          and collinear(vec_inv(v), vec_inv(w)))
    report("C7c", ok,
           "v=%s, w=02*v=%s ; L(v)=%s, L(w)=%s ; collinear(v,w)=%s, "
           "collinear(Inv v, Inv w)=%s, collinear(L v, L w)=%s"
           % ([hex(x) for x in v], [hex(x) for x in w],
              [hex(x) for x in lv], [hex(x) for x in lw],
              collinear(v, w), collinear(vec_inv(v), vec_inv(w)),
              collinear(lv, lw)))


def claim_C8_constant_vector_exception() -> None:
    """C8 (Corollary 2.2, EXHAUSTIVE): on the degenerate family of CONSTANT
    vectors v = (a,a,a,a), L DOES preserve collinearity, because a constant
    vector maps to a constant vector and any two nonzero constant vectors are
    collinear.  Recorded so that Corollary 2.1 is stated as 'not preserved IN
    GENERAL' and never as 'never preserved'."""
    preserved = degenerate = broken = total = 0
    for a in range(1, 256):
        for lam in range(2, 256):
            b = gmul(lam, a)
            lv, lw = vec_L((a,) * 4), vec_L((b,) * 4)
            total += 1
            if is_zero(lv) or is_zero(lw):
                degenerate += 1
            elif collinear(lv, lw):
                preserved += 1
            else:
                broken += 1
    report("C8", broken == 0 and preserved + degenerate == total,
           "exhaustive over constant vectors: %d/%d (a,lambda) pairs preserved under "
           "L, %d degenerate (L(a)=0 for exactly one a in GF(2^8)), %d broken"
           % (preserved, total, degenerate, broken))


def _mult_order(a: int) -> int:
    n, x = 1, a
    while x != 1:
        x = gmul(x, a)
        n += 1
    return n


def claim_C9_entries_nonzero() -> None:
    """C9 (Appendix A, auxiliary): every entry of M is nonzero."""
    zeros = sum(1 for i in range(4) for j in range(4) if M[i][j] == 0)
    entries = sorted({M[i][j] for i in range(4) for j in range(4)})
    report("C9", zeros == 0,
           "all 16 entries of M are nonzero; distinct values %s"
           % [hex(e) for e in entries])


def claim_C10_entries_generate() -> None:
    """C10 (Appendix A, auxiliary): the multiplicative subgroup of GF(2^8)^*
    generated by the entries of M is all of GF(2^8)^*."""
    gens = {M[i][j] for i in range(4) for j in range(4)}
    seen = {1}
    stack = [1]
    while stack:
        x = stack.pop()
        for g in gens:
            y = gmul(x, g)
            if y not in seen:
                seen.add(y)
                stack.append(y)
    report("C10", len(seen) == 255,
           "<entries of M> has multiplicative order %d of 255; ord(0x02) = %d, "
           "ord(0x03) = %d" % (len(seen), _mult_order(0x02), _mult_order(0x03)))


def claim_C11_scalar_index_graph() -> None:
    """C11 (Appendix A, auxiliary): the directed graph on the 255*4 = 1020
    nodes (lambda, k), lambda in GF(2^8)^*, k in {0,1,2,3}, with edges
    (lambda,k) -> (lambda*M[j][k], j) for every j, is strongly connected.

    Recorded because a companion argument in this task's candidate_report.yaml
    uses exactly this fact.  NO claim of Proposition 1 or Proposition 2 depends
    on it, and the note remains complete without it."""
    nodes = [(lam, k) for lam in range(1, 256) for k in range(4)]
    index = {n: i for i, n in enumerate(nodes)}
    fwd = [[] for _ in nodes]
    rev = [[] for _ in nodes]
    for (lam, k) in nodes:
        u = index[(lam, k)]
        for j in range(4):
            t = index[(gmul(lam, M[j][k]), j)]
            fwd[u].append(t)
            rev[t].append(u)

    def reach(adj, src):
        seen = {src}
        stack = [src]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen)

    f, r = reach(fwd, 0), reach(rev, 0)
    report("C11", f == len(nodes) and r == len(nodes),
           "graph on %d nodes: %d forward-reachable and %d reverse-reachable from "
           "(0x01, k=0) -> strongly connected = %s"
           % (len(nodes), f, r, f == len(nodes) and r == len(nodes)))


# ===========================================================================

def main() -> int:
    print("verify_derivation.py -- TASK-20260731-701 (GOAL-AES-001 BATCH-002)")
    print("Recomputes every numerical claim in "
          "derivation_note_column_local_obstructions.md")
    print("python %s" % sys.version.split()[0])
    print("seeds: C6b=%d C6c=%d C7a=%d C7b=%d ; N_SAMPLES=%d"
          % (SEED_C6B, SEED_C6C, SEED_C7A, SEED_C7B, N_SAMPLES))
    print("-" * 78)

    claim_CTAB_table_audit()
    claim_C0_harness_crosscheck()
    claim_C1_order_of_M()
    claim_C2_index_in_GL()
    claim_C3_orbit_of_e1()
    claim_C4_orbit_count_bound()
    claim_C5_exact_orbit_count()
    claim_C6a_scalar_identity()
    claim_C6b_inv_all_coords_nonzero()
    claim_C6c_inv_with_zero_coord()
    claim_C7a_L_breaks_collinearity()
    claim_C7b_S_breaks_collinearity()
    claim_C7c_deterministic_counterexample()
    claim_C8_constant_vector_exception()
    claim_C9_entries_nonzero()
    claim_C10_entries_generate()
    claim_C11_scalar_index_graph()

    print("-" * 78)
    npass = sum(1 for _, s, _ in _RESULTS if s == "PASS")
    nfail = sum(1 for _, s, _ in _RESULTS if s == "FAIL")
    nskip = sum(1 for _, s, _ in _RESULTS if s == "SKIP")
    print("SUMMARY %d PASS, %d FAIL, %d SKIP of %d claims"
          % (npass, nfail, nskip, len(_RESULTS)))
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
