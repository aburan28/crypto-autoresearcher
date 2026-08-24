"""
vertical.py -- orchestration for one vertical conductor-q edge: CM-construct the
crater curve, descend to the floor curve via a genuine Velu q-isogeny
(vertical_isogeny.py), certify it (CTRL-END-RING-CERTIFICATE), build its matched
horizontal ell-neighbor baseline pair (CTRL-HORIZONTAL-BASELINE), compute the five
frozen primary meters (reused/meters.py UNCHANGED) on all objects, and run the
matched rho/BSGS baseline (reused/rho_bsgs.py UNCHANGED) on the edge's shared N.
"""
import math
import random
import time

from .reused import fp, curve, isogeny, isogeny_class, meters as meters_mod, rho_bsgs, analysis
from . import cm, vertical_isogeny as vi, fp_sampler

HIGH_METERS = analysis.HIGH_METERS
LOW_METER = analysis.LOW_METER
ALL_PRIMARY = analysis.ALL_PRIMARY

HORIZONTAL_ELLS = (2, 3, 5, 7)
CONDUCTOR_PRIME_CANDIDATES = (17, 19, 23, 29, 31)


def _sieve_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i in range(2, n + 1) if sieve[i]]


_SMALL_PRIMES_1000 = _sieve_primes(1000)


def ratio_with_zero_handling(v1, v2):
    lo, hi = min(v1, v2), max(v1, v2)
    if lo == 0:
        return 1.0 if hi == 0 else float("inf")
    return hi / lo


def all_D_K_q_candidates():
    out = []
    for D_K in cm.KNOWN_CM:
        for q in CONDUCTOR_PRIME_CANDIDATES:
            if cm.kronecker_symbol_odd_prime(D_K, q) == 1:
                out.append((D_K, q))
    return out


def compute_meters(a, b, p, fb_size, rng, gb_budget, macaulay_cap):
    return meters_mod.compute_curve_meters(
        a, b, p, fb_size, rng,
        n_samples_density=6, n_samples_prob=24,
        gb_budget=gb_budget, macaulay_cap=macaulay_cap, planted=False,
    )


def meter_ratios(m_floor, m_crater):
    ratios = {}
    for m in HIGH_METERS:
        ratios[m] = ratio_with_zero_handling(m_floor[m], m_crater[m])
    d_floor = m_floor[LOW_METER]
    d_crater = m_crater[LOW_METER]
    ratios[LOW_METER] = ratio_with_zero_handling(d_floor, d_crater)
    delta_d_reg = abs(d_floor - d_crater)
    return ratios, delta_d_reg


def build_vertical_edge(seed, fb_size, gb_budget, macaulay_cap, bit_candidates,
                         per_pair_attempts=6000, kernel_search_attempts_note=None):
    """Construct one vertical conductor-q edge for a given master seed. Returns a
    dict with status in {"ok", "infra_failure"} and full detail (never fabricated:
    every failure records WHY)."""
    rng = random.Random(seed)
    target_bits = fp_sampler.draw_target_bits(rng, bit_candidates)
    candidates = all_D_K_q_candidates()
    rng.shuffle(candidates)

    t_search0 = time.time()
    search = cm.search_vertical_edge_multi(candidates, target_bits, rng,
                                            per_pair_attempts=per_pair_attempts)
    search_elapsed = time.time() - t_search0
    if "failure" in search:
        return {"status": "infra_failure", "seed": seed, "target_bits": target_bits,
                "reason": "no_q_divisible_conductor_found_within_attempt_budget",
                "search_log": search, "search_elapsed_s": search_elapsed}

    D_K, q, p, t, N = search["D_K"], search["q"], search["p"], search["t"], search["N"]
    j_K = cm.KNOWN_CM[D_K]
    crater = cm.build_crater_matching_trace(D_K, j_K, p, t, rng)
    if crater is None:
        return {"status": "infra_failure", "seed": seed, "target_bits": target_bits,
                "reason": "crater_cm_construction_failed_trace_mismatch",
                "D_K": D_K, "q": q, "p": p, "t": t, "N": N}
    a_c, b_c, N_c, used_twist = crater
    if N_c != N:
        return {"status": "infra_failure", "seed": seed, "target_bits": target_bits,
                "reason": "crater_order_mismatch", "D_K": D_K, "q": q, "p": p, "N_target": N, "N_c": N_c}

    t0 = time.time()
    crater_kernels = vi.kernel_representative_sets_q(q, a_c, b_c, p, rng)
    kernel_search_elapsed = time.time() - t0
    if not crater_kernels:
        return {"status": "infra_failure", "seed": seed, "target_bits": target_bits,
                "reason": "no_rational_q_kernel_found_at_crater",
                "D_K": D_K, "q": q, "p": p, "N": N}

    rep = crater_kernels[0]
    a_f, b_f = vi.velu_codomain(a_c, b_c, p, rep, q)
    order_ok = vi.verify_order_preserved(a_f, b_f, p, N, rng, trials=5)
    if not order_ok:
        return {"status": "infra_failure", "seed": seed, "target_bits": target_bits,
                "reason": "velu_floor_failed_order_preservation_check",
                "D_K": D_K, "q": q, "p": p, "N": N}

    # CTRL-END-RING-CERTIFICATE: independent cross-checks beyond order-preservation.
    floor_kernels = vi.kernel_representative_sets_q(q, a_f, b_f, p, rng)
    j_check_p = None
    try:
        # independent recomputation of the crater's j-invariant from its own (a,b),
        # cross-checked against the KNOWN CM value used to construct it (never
        # trusting the construction call alone)
        num = (a_c * a_c * a_c) % p
        # j = 1728 * 4a^3 / (4a^3+27b^2)
        denom = (4 * num + 27 * b_c * b_c) % p
        j_check_p = (1728 * 4 * num * fp.inv(denom, p)) % p if denom != 0 else None
    except Exception:
        j_check_p = None
    j_expected = j_K % p
    certificate = {
        "kind": "none",  # pure measurement construction, no discrete-log/relation solve claimed here
        "degree_claimed": q,
        "kernel_size_representatives": len(rep),
        "kernel_size_expected": (q - 1) // 2,
        "kernel_size_matches": len(rep) == (q - 1) // 2,
        "order_preservation_verified": order_ok,
        "crater_num_kernels": len(crater_kernels),
        "crater_num_kernels_expected_if_h1_crater": q + 1,
        "crater_num_kernels_matches_volcano_theory": len(crater_kernels) == q + 1,
        "floor_num_kernels": len(floor_kernels),
        "floor_num_kernels_expected_if_depth1_floor": 1,
        "floor_num_kernels_matches_volcano_theory": len(floor_kernels) == 1,
        "crater_j_recomputed_independently": j_check_p,
        "crater_j_expected_from_KNOWN_CM_table": j_expected,
        "crater_j_matches": (j_check_p == j_expected),
        "verified": bool(
            order_ok and (len(rep) == (q - 1) // 2)
            and (j_check_p == j_expected)
        ),
    }

    # meters on floor and crater
    m_floor = compute_meters(a_f, b_f, p, fb_size, random.Random(seed * 1000 + 1), gb_budget, macaulay_cap)
    m_crater = compute_meters(a_c, b_c, p, fb_size, random.Random(seed * 1000 + 2), gb_budget, macaulay_cap)
    ratios, delta_d_reg = meter_ratios(m_floor, m_crater)
    max_ratio = max(v for v in ratios.values() if v != float("inf")) if any(
        v != float("inf") for v in ratios.values()) else float("inf")

    # horizontal baseline from the FLOOR curve
    horiz = build_horizontal_pair_independent(
        random.Random(seed * 1000 + 3), bit_candidates, fb_size, gb_budget, macaulay_cap)

    # matched rho/bsgs on this edge's (floor curve, N)
    rho_receipt = rho_bsgs.run_matched_baselines(a_f, b_f, p, N, seed=seed * 1000 + 7,
                                                  rho_max_steps=40_000_000)

    return {
        "status": "ok",
        "seed": seed,
        "target_bits": target_bits,
        "achieved_bits": N.bit_length(),
        "D_K": D_K, "q": q, "p": p, "t": t, "N": N,
        "crater": {"a": a_c, "b": b_c, "used_twist": used_twist},
        "floor": {"a": a_f, "b": b_f},
        "certificate": certificate,
        "meters_floor": m_floor,
        "meters_crater": m_crater,
        "ratios": ratios,
        "delta_d_reg": delta_d_reg,
        "max_ratio": max_ratio,
        "horizontal": horiz,
        "rho_bsgs": rho_receipt,
        "search_attempts": search.get("total_attempts"),
        "search_elapsed_s": search_elapsed,
        "kernel_search_elapsed_s": kernel_search_elapsed,
    }


def build_horizontal_pair_independent(rng, bit_candidates, fb_size, gb_budget, macaulay_cap,
                                       max_seed_attempts=12):
    """CTRL-HORIZONTAL-BASELINE, constructed INDEPENDENTLY of any specific vertical
    edge's CM curve (per pass_condition's own wording: pairs need only be "matched
    in N-bit range to the vertical sample", not tied to one edge's exact p/N).

    PROTOCOL DEVIATION discovered empirically and disclosed here (see
    implementation.md "CTRL-HORIZONTAL-BASELINE construction"): the CM-constructed
    floor/crater curves used for vertical edges were found, in every seed tried, to
    have ZERO restricted-kernel ("-1 eigenvalue") ell-neighbors for ell in
    {2,3,5,7} -- i.e. reused/isogeny_class.build_class run from a CM curve
    deterministically exhausted at size 1 every time this was tried (not a rare
    event; it recurred across every (D_K,q) pair sampled during development). An
    attempted fix (forcing an auxiliary CRT congruence on t to guarantee an
    eigenvalue-(-1) kernel for one ell_h) was tried and found mathematically
    unsound on inspection (it would require ell_h^2 | D_K, impossible for a
    SQUAREFREE fundamental discriminant) and is NOT used in the final driver.
    RANDOM ordinary curves (reused/isogeny_class.find_seed_curve, EXACTLY
    EXP-ECTD-001's own working method, reused unchanged), by contrast, were
    measured to have restricted-kernel neighbors roughly 60% of the time (6/10 in a
    quick check) -- consistent with EXP-ECTD-001 successfully building 64-curve
    classes this same way. This driver therefore builds each horizontal pair from a
    FRESH independent random ordinary curve (same bit-range convention as the
    vertical sample), retrying up to `max_seed_attempts` seeds, rather than walking
    from the CM curve itself.

    Every ell used (2,3,5,7) is coprime to EVERY conductor_prime_candidates value
    (17,19,23,29,31) by construction, so the standard volcano fact ("an ell-isogeny
    only changes the ell-adic valuation of [O_K:End(E)]") certifies the q-part of
    the conductor is UNCHANGED for every q simultaneously -- no per-edge q needs to
    be threaded through here."""
    for attempt in range(max_seed_attempts):
        bits = fp_sampler.draw_target_bits(rng, bit_candidates)
        p = fp_sampler.prime_of_exact_bits(bits, rng)
        seed_res = isogeny_class.find_seed_curve(p, rng, bits, bits, max_attempts=4000)
        if seed_res is None:
            continue
        a0, b0, N = seed_res
        cls = isogeny_class.build_class(p, a0, b0, N, rng, min_size=2, ells=HORIZONTAL_ELLS,
                                         max_nodes_expand=300, wall_budget_s=30)
        if len(cls["curves"]) < 2 or not cls["edges"]:
            continue
        i, j, ell = cls["edges"][0]
        a1, b1 = cls["curves"][i]
        a2, b2 = cls["curves"][j]
        m1 = compute_meters(a1, b1, p, fb_size, random.Random(rng.randrange(1 << 30)), gb_budget, macaulay_cap)
        m2 = compute_meters(a2, b2, p, fb_size, random.Random(rng.randrange(1 << 30)), gb_budget, macaulay_cap)
        ratios, delta_d_reg = meter_ratios(m1, m2)
        max_ratio = max(v for v in ratios.values() if v != float("inf")) if any(
            v != float("inf") for v in ratios.values()) else float("inf")
        return {
            "status": "ok", "attempts": attempt + 1, "bits": bits, "p": p, "N": N, "ell": ell,
            "conductor_q_part_unchanged_certificate": {
                "method": "gcd(ell,q)==1 for every q in conductor_prime_candidates "
                          "=> ell-isogeny cannot change the q-adic valuation of "
                          "[O_K:End(E)] for any candidate q (standard volcano fact)",
                "ell": ell, "conductor_prime_candidates": CONDUCTOR_PRIME_CANDIDATES,
                "gcd_ell_q_all": {q: math.gcd(ell, q) for q in CONDUCTOR_PRIME_CANDIDATES},
                "verified_unchanged": all(math.gcd(ell, q) == 1 for q in CONDUCTOR_PRIME_CANDIDATES),
            },
            "curve1": {"a": a1, "b": b1}, "curve2": {"a": a2, "b": b2},
            "meters1": m1, "meters2": m2,
            "ratios": ratios, "delta_d_reg": delta_d_reg, "max_ratio": max_ratio,
        }
    return {"status": "no_horizontal_pair_found_within_attempt_budget", "attempts": max_seed_attempts}


def coordinate_null_check(a, b, p, rng, fb_size, gb_budget, macaulay_cap):
    """CTRL-COORDINATE-NULL: F_p-isomorphism (x,y)->(u^2 x, u^3 y) applied to the
    Weierstrass model; recompute meters on the isomorphic model and check they
    coincide (same object, different coordinates)."""
    u = rng.randrange(2, p)
    u2 = (u * u) % p
    u4 = (u2 * u2) % p
    u6 = (u4 * u2) % p
    a_iso = (a * fp.inv(u4, p)) % p
    b_iso = (b * fp.inv(u6, p)) % p
    m_orig = compute_meters(a, b, p, fb_size, random.Random(rng.randrange(1 << 30)), gb_budget, macaulay_cap)
    m_iso = compute_meters(a_iso, b_iso, p, fb_size, random.Random(rng.randrange(1 << 30)), gb_budget, macaulay_cap)
    d_reg_match = m_orig[LOW_METER] == m_iso[LOW_METER]
    mac_match = m_orig["macaulay_rank_defect_at_first_fall"] == m_iso["macaulay_rank_defect_at_first_fall"]
    return {
        "u": u, "curve_orig": {"a": a, "b": b}, "curve_iso": {"a": a_iso, "b": b_iso},
        "d_reg_match": d_reg_match, "macaulay_defect_match": mac_match,
        "meters_orig": m_orig, "meters_iso": m_iso,
        "pass": bool(d_reg_match and mac_match),
    }


def glv_instrument(rng, fb_size, gb_budget, macaulay_cap, target_bits=40, max_attempts=2000):
    """CTRL-GLV-CHANNEL: a curve E: y^2=x^3+b (j=0, D=-3) over a prime p=1(mod3),
    with the standard GLV endomorphism phi(x,y)=(zeta3*x,y), zeta3 a primitive cube
    root of unity mod p (phi^2+phi+1=0). Measured ONLY on the separate
    endomorphism-evaluation-cost channel; Semaev meters are also recorded here for
    completeness but MUST NOT be promoted as vertical-discontinuity evidence
    (enforced downstream in decision.py, which never reads glv_instrument's meters
    into the KS sample)."""
    p = None
    for _ in range(max_attempts):
        cand = fp_sampler.prime_of_exact_bits(target_bits, rng)
        if cand % 3 == 1:
            p = cand
            break
    if p is None:
        return {"status": "no_suitable_prime_found"}
    # p = 1 (mod 3): a primitive cube root of unity is g^((p-1)//3) for a random g,
    # as long as that value != 1 (BUG FIX: an earlier version of this function did
    # a linear scan `for z in range(2,p)` checking z^2+z+1=0 mod p directly, which
    # is O(p) and infeasible at 40+ bit p -- caught only by measuring the smoke run
    # hang for several CPU-minutes, killed, and fixed here; recorded per AGENTS.md
    # rule 4 as an implementation_error caught during development, not silently
    # patched over).
    zeta3 = None
    exp = (p - 1) // 3
    for _ in range(200):
        g = rng.randrange(2, p)
        z = pow(g, exp, p)
        if z != 1 and (z * z + z + 1) % p == 0:
            zeta3 = z
            break
    if zeta3 is None:
        return {"status": "no_cube_root_of_unity_found"}
    a = 0
    N = None
    N_full = None
    cofactor = None
    b = None
    # j=0 curves (y^2=x^3+b) ALWAYS have #E(F_p) divisible by 6 when p=1(mod3) --
    # a standard structural fact (the sextic-twist automorphism group), discovered
    # here empirically (10/10 draws gave a multiple of 6, never prime) before being
    # understood -- so #E(F_p) itself can never be prime; the standard GLV setup
    # instead uses the LARGE PRIME-ORDER COFACTOR subgroup (exactly as real GLV
    # curves in the literature are specified), found here by trial-dividing out
    # small factors.
    for _ in range(200):
        b = rng.randrange(1, p)
        N_try = curve.find_curve_order(a, b, p, rng, tries=8, agreement_needed=4)
        if N_try is None:
            continue
        n = N_try
        for sp in _SMALL_PRIMES_1000:
            while n % sp == 0:
                n //= sp
        if fp.is_probable_prime(n) and n > 1000:
            N_full, cofactor, N = N_try, N_try // n, n
            break
    if N is None:
        return {"status": "order_finding_failed"}

    def phi(P):
        if P is None:
            return None
        x, y = P
        return ((zeta3 * x) % p, y)

    # project into the prime-order (N) subgroup by multiplying out the cofactor
    P = curve.scalar_mul(cofactor, curve.random_point(a, b, p, rng), a, p)
    phiP = phi(P)
    on_curve_ok = curve.on_curve(phiP, a, b, p)
    # lambda with lambda^2+lambda+1 = 0 mod N (N prime, group cyclic); x^2+x+1=0 has
    # TWO roots mod N (lambda and its conjugate -1-lambda) -- phi corresponds to
    # exactly one of them depending on which primitive cube root zeta3 was picked
    # mod p, so try both and independently verify via scalar_mul, never assume.
    lam = None
    verified_scalar = False
    r = fp.sqrt_mod((-3) % N, N) if fp.is_qr((-3) % N, N) else None
    if r is not None:
        cand1 = ((-1 + r) * fp.inv(2, N)) % N
        cand2 = ((-1 - r) * fp.inv(2, N)) % N
        for cand in (cand1, cand2):
            if curve.scalar_mul(cand, P, a, p) == phiP:
                lam = cand
                verified_scalar = True
                break
        if lam is None:
            lam = cand1
    t0 = time.time()
    for _ in range(2000):
        phi(P)
    phi_cost_2000 = time.time() - t0
    t0 = time.time()
    if lam is not None:
        for _ in range(50):
            curve.scalar_mul(lam, P, a, p)
        scalar_cost_50 = time.time() - t0
    else:
        scalar_cost_50 = None
    m = compute_meters(a, b, p, fb_size, random.Random(rng.randrange(1 << 30)), gb_budget, macaulay_cap)
    return {
        "status": "ok",
        "curve": {"a": a, "b": b, "p": p, "N_full": N_full, "cofactor": cofactor,
                  "N_prime_subgroup": N, "j": 0, "D_K": -3},
        "zeta3": zeta3, "lambda": lam,
        "phi_is_on_curve": on_curve_ok,
        "phi_equals_scalar_mul_lambda": verified_scalar,
        "cost_channel": {
            "phi_eval_time_per_2000_calls_s": phi_cost_2000,
            "scalar_mul_by_lambda_time_per_50_calls_s": scalar_cost_50,
            "note": "phi is O(1) modmul; scalar_mul(lambda,...) is O(log N) point "
                    "doublings -- this ratio is the GLV endomorphism-evaluation-cost "
                    "channel, kept separate from the Semaev meters below",
        },
        "semaev_meters_recorded_not_promoted": m,
        "invalidation_reminder": "per CTRL-GLV-CHANNEL / invalidation_rules: any Semaev "
                                  "meter movement here must NEVER be read into the vertical "
                                  "KS sample or decision_table; see decision.py.",
    }
