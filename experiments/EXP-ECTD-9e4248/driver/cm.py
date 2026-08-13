"""
cm.py -- NEW driver code (genuinely new relative to EXP-ECTD-001, per the handoff:
"the conductor/volcano/vertical-isogeny logic is genuinely new implementation").

Implements the Hilbert-class-polynomial CONSTRUCTION ROUTE preferred by
spec.replication.conductor_search_cost_estimate / DEC-20260806-160175 D4 for
building a genuine vertical (conductor-q) edge, restricted to the tractable
CLASS-NUMBER-1 special case documented in detail in implementation.md
("Vertical-edge construction method").

Summary of the method (full derivation in implementation.md):
  1. Pick a fundamental discriminant D_K with class number h(D_K)=1 (a "Heegner"
     discriminant) -- computed and independently verified via elementary reduced
     binary-quadratic-form enumeration (`class_number_and_forms`), not merely
     asserted from a memorized table.
  2. Pick a target conductor prime q from spec.inputs.conductor_prime_candidates,
     filtered to q SPLIT in K (Kronecker symbol (D_K/q)=1) -- the standard
     precondition for q to give an actual vertical (not purely-horizontal-or-inert)
     isogeny volcano gap of depth >=1.
  3. Solve 4p = t^2 - q^2*D_K for p, t with t chosen (via CRT) to satisfy
     t = -2 (mod q), which pins the repeated eigenvalue of Frobenius mod q to
     lambda = t/2 = -1 (mod q) -- this is the SAME restricted case
     ("Frobenius acts as -1") that reused/isogeny.py's kernel-finding code already
     covers, letting the vertical q-isogeny kernel be found by REUSING that code
     UNCHANGED rather than writing a new general-eigenvalue kernel isolator.
  4. Construct the CRATER curve (End(E) = O_K, the maximal order, disc D_K) directly
     via the KNOWN integer CM j-invariant for D_K (there are only 13 such
     discriminants in total; the 9 fundamental ones are hardcoded below and
     INDEPENDENTLY VALIDATED at runtime against freshly-computed small test primes
     before ever being trusted in a real edge -- never asserted from the literature
     alone). This requires NO floating-point Hilbert-class-polynomial evaluation,
     because h(D_K)=1 means H_{D_K}(x) = x - j_K exactly (a degree-1 polynomial).
  5. Descend from crater to FLOOR via a single degree-q Velu isogeny, reusing
     reused/isogeny.py's kernel_representative_sets / velu_codomain /
     verify_order_preserved functions UNCHANGED (the object -- a Velu-formula
     isogeny construction and its order-preservation check -- is identical to
     EXP-ECTD-001's).

This sidesteps needing the FLOOR's own (much higher-degree, h(q^2 D_K) ~ q) Hilbert
class polynomial, and sidesteps needing Kohel's general modular-polynomial volcano
classification algorithm (which would otherwise be required to determine an
ARBITRARY curve's exact End-ring level) -- both were assessed, and are documented in
implementation.md, as infeasible to build and self-test correctly from scratch
within this session's realistic implementation budget. This is a disclosed scoping
decision, not a silent one.
"""
import math
import random

from .reused import fp, curve, isogeny

# Fundamental discriminants with class number 1 (the 9 "Heegner numbers" excluding
# D=-3,-4, which are skipped here because their curves have extra automorphisms
# (j=0, j=1728) that complicate the generic a=3*gamma,b=2*gamma / twist-by-d
# construction used uniformly below for every other discriminant).
#
# D=-7 is ALSO excluded here, for a reason discovered empirically by
# selftest_cm.py's independent validation (not asserted, MEASURED): D=-7 = 1 (mod 8),
# and for the odd t required by t^2=D (mod 4), t^2 = 1 (mod 8) always (odd-square
# fact), so t^2 - D = 0 (mod 8) always, forcing p=(t^2-D)/4 to be EVEN for every
# integer t -- i.e. D=-7's principal-form Pell relation 4p=t^2-D has NO odd-prime
# solution at all via this direct construction (only p=2). The other 6 discriminants
# below all satisfy D = 5 (mod 8) (or are even, D=-8), giving p ODD for every odd t,
# and validate_known_j confirms all 6 against freshly-computed small test primes.
# This is a real, disclosed scoping decision (one usable discriminant fewer), not a
# hidden failure -- selftest_cm.py's test_known_j_validated would have failed loudly
# had D=-7 been left in KNOWN_CM.
KNOWN_CM = {
    -8: 8000,
    -11: -32768,
    -19: -884736,
    -43: -884736000,
    -67: -147197952000,
    -163: -262537412640768000,
}


def isqrt(n):
    return math.isqrt(n)


def class_number_and_forms(D):
    """Class number h(D) of the (fundamental or non-fundamental) discriminant D<0,
    via brute-force enumeration of REDUCED primitive positive-definite binary
    quadratic forms (a,b,c) with b^2-4ac=D, -a<b<=a<=c, b>=0 if a==c or a==|b|.
    Standard algorithm (e.g. Cohen, "A Course in Computational Algebraic Number
    Theory", Algorithm 5.3.5), implemented from scratch and cross-checked in
    selftest_cm.py against known class numbers."""
    assert D < 0 and D % 4 in (0, 1)
    forms = []
    amax = isqrt(abs(D) // 3) + 1
    for a in range(1, amax + 1):
        for b in range(-a + 1, a + 1):
            if (b - D) % 2 != 0:
                continue
            num = b * b - D
            if num % (4 * a) != 0:
                continue
            c = num // (4 * a)
            if c < a:
                continue
            if a == c and b < 0:
                continue
            g = math.gcd(math.gcd(a, b), c)
            if g != 1:
                continue
            forms.append((a, b, c))
    return len(forms), forms


def is_fundamental(D):
    """D is a fundamental discriminant iff D=1 or (D%4==1 and squarefree) or
    (D%4==0 and D/4%4 in (2,3) and D/4 squarefree). Only used defensively in
    selftest_cm.py."""
    if D % 4 == 1:
        m = D
    elif D % 4 == 0:
        m = D // 4
        if m % 4 not in (2, 3):
            return False
    else:
        return False
    # squarefree check
    n = abs(m)
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        d += 1
    return True


def kronecker_symbol_odd_prime(D, q):
    """(D/q) for odd prime q not dividing D, via Euler's criterion mod q."""
    Dq = D % q
    if Dq == 0:
        return 0
    r = pow(Dq, (q - 1) // 2, q)
    return -1 if r == q - 1 else r


def j_to_curve(j, p):
    """Standard formula: E: y^2=x^3+ax+b with j-invariant j (j != 0, 1728 mod p).
    gamma = j / (1728 - j) mod p; a = 3*gamma, b = 2*gamma."""
    j %= p
    denom = (1728 - j) % p
    if denom == 0 or j == 0:
        raise ValueError("j-invariant 0 or 1728 not supported by this constructor")
    gamma = (j * fp.inv(denom, p)) % p
    a = (3 * gamma) % p
    b = (2 * gamma) % p
    return a, b


def quadratic_twist(a, b, p, d):
    """Quadratic twist of y^2=x^3+ax+b by non-residue d: y^2=x^3+(a*d^2)x+(b*d^3).
    Flips the sign of the trace of Frobenius."""
    return (a * d * d) % p, (b * d * d * d) % p


def random_nonresidue(p, rng):
    while True:
        d = rng.randrange(2, p)
        if fp.legendre(d, p) == -1:
            return d


def validate_known_j(D_K, j_K, rng, n_test_primes=3, max_attempts_per_prime=4000):
    """Independent re-verification (never trust the hardcoded table alone, per
    AGENTS.md 'never fabricate'): for several small primes p with
    4p = t^2 - D_K for small integer t, construct the curve with j=j_K mod p
    (twisting if needed to match the sign of t), and confirm its measured order
    (via reused/curve.find_curve_order, independent of this module) gives EXACTLY
    trace t (i.e. t^2 - 4p == D_K exactly). Returns (ok: bool, receipts: list)."""
    receipts = []
    found = 0
    t = 2 if D_K % 2 == 0 else 1
    attempts = 0
    while found < n_test_primes and attempts < max_attempts_per_prime:
        attempts += 1
        num = t * t - D_K
        if num % 4 == 0:
            p = num // 4
            if p > 10 and fp.is_probable_prime(p):
                try:
                    a, b = j_to_curve(j_K, p)
                    N = curve.find_curve_order(a, b, p, rng, tries=8, agreement_needed=4)
                    ok_this = False
                    used_twist = False
                    if N is not None:
                        trace = p + 1 - N
                        if trace == t:
                            ok_this = True
                        elif trace == -t:
                            d = random_nonresidue(p, rng)
                            a2, b2 = quadratic_twist(a, b, p, d)
                            N2 = curve.find_curve_order(a2, b2, p, rng, tries=8, agreement_needed=4)
                            ok_this = (N2 is not None) and (p + 1 - N2 == t)
                            used_twist = True
                    receipts.append({"p": p, "t": t, "N": N, "ok": ok_this, "used_twist": used_twist})
                    if ok_this:
                        found += 1
                except Exception as e:
                    receipts.append({"p": p, "t": t, "error": str(e)})
        t += 2
    return found == n_test_primes, receipts


def crt_combine(mods_residues):
    """Combine a list of (modulus, residue) pairs (pairwise-coprime moduli) via
    sequential CRT. Returns (combined_modulus, combined_residue)."""
    M, R = 1, 0
    for m, r in mods_residues:
        # solve x = R (mod M), x = r (mod m)  -> x = R + M*k
        inv = pow(M, -1, m)
        k = ((r - R) * inv) % m
        R = R + M * k
        M = M * m
        R %= M
    return M, R


def crt_t0(q, par, ell_h=None):
    """Solve t = -2 (mod q) [pins the vertical eigenvalue], t = par (mod 2)
    [discriminant parity], and OPTIONALLY t = -2 (mod ell_h) for an auxiliary small
    prime ell_h in {2,3,5,7} -- this last congruence is what GUARANTEES the
    constructed floor curve also has a genuine "-1-type" ell_h horizontal kernel,
    letting reused/isogeny.py's kernel_representative_sets(ell_h,...) find a real
    horizontal neighbor UNCHANGED (see implementation.md "CTRL-HORIZONTAL-BASELINE
    construction", discovered necessary empirically: a floor curve's trace t is
    otherwise 'generic' mod small ell, and the restricted kernel finder then finds
    ZERO horizontal neighbors deterministically for that edge, not merely rarely)."""
    parts = [(q, (-2) % q), (2, par)]
    if ell_h is not None and ell_h != 2:
        parts.append((ell_h, (-2) % ell_h))
    elif ell_h == 2:
        # ell_h=2 -> t=-2=0 (mod2); already covered by the parity congruence only
        # if par==0; otherwise infeasible (caller should pick a different ell_h)
        if par != 0:
            raise ValueError("ell_h=2 incompatible with required parity")
    M, R = crt_combine(parts)
    return M, R


def search_vertical_p_t(D_K, q, target_bits, rng, max_attempts=8000, ell_h=None):
    """Search for (p, t) with 4p = t^2 - q^2*D_K, p prime, t = -2 (mod q) (pins the
    repeated Frobenius eigenvalue mod q to -1, so reused/isogeny.py's restricted
    kernel finder applies unchanged), t = -2 (mod ell_h) if ell_h is given (see
    crt_t0), and N = p+1-t (the trace sign matching this exact t) prime with
    bit-length near target_bits. Returns dict or None."""
    Dpi = q * q * D_K
    par = Dpi % 2
    try:
        M, t0 = crt_t0(q, par, ell_h=ell_h)
    except ValueError as e:
        return {"failure": f"crt_infeasible: {e}", "attempts": 0}
    t_target = isqrt(4 * (1 << target_bits))
    k_center = max(0, (t_target - t0) // M)
    tried = set()
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        span = 2 + attempts // 3
        k = k_center + rng.randint(-span, span)
        if k < 0 or k in tried:
            continue
        tried.add(k)
        t = t0 + k * M
        if t <= 0:
            continue
        num = t * t - Dpi
        if num <= 0 or num % 4 != 0:
            continue
        p = num // 4
        if not fp.is_probable_prime(p):
            continue
        N = p + 1 - t
        if N > 0 and fp.is_probable_prime(N) and 40 <= N.bit_length() <= 60:
            return {"p": p, "t": t, "N": N, "Dpi": Dpi, "attempts": attempts, "ell_h": ell_h}
    return {"failure": "no (p,t,N) found within attempt budget", "attempts": attempts}


def pair_small_prime_viable(D_K, q, ell_h=None, ells=(3, 5, 7, 11, 13)):
    """Structural feasibility pre-check, discovered empirically while debugging this
    driver (not a hypothetical corner case -- see implementation.md "small-prime
    obstruction"): for a FIXED (D_K, q), the congruence class t = -2 (mod q) plus the
    parity constraint can force p = (t^2-Dpi)/4 and N = p+1-t to be simultaneously
    divisible by some small prime ell across EVERY t in the admissible class (e.g.
    D_K=-11, q=23 forces 3 | p or 3 | N for every single admissible t -- verified
    directly, not assumed). This checks, for each small prime ell coprime to 2q,
    whether SOME residue of t mod ell avoids ell | p and ell | N simultaneously;
    if any ell admits no such residue, this (D_K, q) pair can never yield a prime
    (p, N) pair and is skipped before spending any search budget on it."""
    Dpi = q * q * D_K
    for ell in ells:
        if ell == q or Dpi % ell == 0:
            continue
        inv4 = pow(4, -1, ell)
        ok = False
        if ell_h is not None and ell == ell_h:
            candidate_rs = [(-2) % ell]
        else:
            candidate_rs = list(range(ell))
        for r in candidate_rs:
            p_mod = ((r * r - Dpi) * inv4) % ell
            N_mod = (p_mod + 1 - r) % ell
            if p_mod != 0 and N_mod != 0:
                ok = True
                break
        if not ok:
            return False
    return True


def search_vertical_edge_multi(candidates, target_bits, rng, per_pair_attempts=6000,
                                horizontal_ells=(3, 5, 7, 2)):
    """Try a list of (D_K, q) candidate pairs (already filtered by the split
    condition (D_K/q)=1 by the caller); for EACH pair, additionally try pinning an
    auxiliary small prime ell_h in `horizontal_ells` (CTRL-HORIZONTAL-BASELINE
    needs the constructed floor curve to have a genuine ell_h-horizontal kernel --
    see crt_t0's docstring for why this must be engineered in, not left to chance),
    skipping any (pair, ell_h) combination the small-prime feasibility check rules
    out, and running search_vertical_p_t until one succeeds or the list is
    exhausted. Returns a dict with the winning (D_K,q,ell_h) and (p,t,N), plus the
    full attempt log for honest reporting."""
    log = []
    total_attempts = 0
    for D_K, q in candidates:
        for ell_h in horizontal_ells:
            if not pair_small_prime_viable(D_K, q, ell_h=ell_h):
                log.append({"D_K": D_K, "q": q, "ell_h": ell_h, "skipped": "small_prime_obstruction"})
                continue
            res = search_vertical_p_t(D_K, q, target_bits, rng,
                                       max_attempts=per_pair_attempts, ell_h=ell_h)
            total_attempts += res.get("attempts", 0)
            log.append({"D_K": D_K, "q": q, "ell_h": ell_h, "result": res})
            if "failure" not in res:
                return {"D_K": D_K, "q": q, "ell_h": ell_h, **res,
                        "pair_log": log, "total_attempts": total_attempts}
    return {"failure": "no viable (D_K,q,ell_h) combination produced a valid (p,t,N)",
            "pair_log": log, "total_attempts": total_attempts}


def build_crater_matching_trace(D_K, j_K, p, t_target, rng):
    """Construct the curve with j=j_K mod p, twisting if necessary so its measured
    trace of Frobenius is exactly t_target. Returns (a,b,N,used_twist) or None."""
    a, b = j_to_curve(j_K, p)
    N = curve.find_curve_order(a, b, p, rng, tries=8, agreement_needed=4)
    if N is None:
        return None
    trace = p + 1 - N
    if trace == t_target:
        return a, b, N, False
    if trace == -t_target:
        d = random_nonresidue(p, rng)
        a2, b2 = quadratic_twist(a, b, p, d)
        N2 = curve.find_curve_order(a2, b2, p, rng, tries=8, agreement_needed=4)
        if N2 is not None and p + 1 - N2 == t_target:
            return a2, b2, N2, True
        return None
    return None
