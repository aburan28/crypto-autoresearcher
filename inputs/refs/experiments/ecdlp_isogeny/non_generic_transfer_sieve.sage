# Non-generic transfer/decomposition channel sieve.
#
# Scope: controlled research instances only.  This script does not attack any
# deployed key.  It scores public toy/generated curves and two standard-curve
# parameter sets for transfer channels that change the visible DLP object:
#   1. same-field isogeny class invariants;
#   2. quadratic-twist / extension-field isogenous object;
#   3. scalar Weil-restriction sanity checks.
#
# The output is a JSON evidence file, not a breakthrough claim.

import json
import random
import time


def json_clean(value):
    if isinstance(value, dict):
        return {str(k): json_clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_clean(v) for v in value]
    if value is None or isinstance(value, (bool, str, int, float)):
        return value
    try:
        if value in ZZ:
            return int(value)
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return str(value)


def rho_exp_bits(order):
    return float(log(0.886, 2) + 0.5 * log(Integer(order), 2))


def ph_exp_bits_from_lpf(lpf):
    return 0.5 * float(log(Integer(lpf), 2))


def cm_summary(p, n):
    t = Integer(p) + 1 - Integer(n)
    D = t * t - 4 * Integer(p)
    sf = Integer(D).squarefree_part()
    DK = sf if Integer(sf) % 4 == 1 else 4 * sf
    f2 = D // DK
    return {
        "trace": int(t),
        "cm_discriminant_bits": int(abs(DK).nbits()),
        "conductor_square": int(f2),
        "small_cm_disc": bool(abs(DK) <= 200),
    }


def factor_status(N, full=True, limit=None):
    t0 = time.time()
    if full:
        fac = factor(Integer(N), proof=False)
    else:
        fac = factor(Integer(N), limit=limit or 10**6, proof=False)
    elapsed = time.time() - t0
    entries = []
    full_factored = True
    largest_prime = Integer(1)
    largest_composite = Integer(1)
    for q, e in fac:
        q = Integer(q)
        prime = bool(q.is_prime(proof=False))
        entries.append({"factor": int(q), "exp": int(e), "prime": prime, "bits": int(q.nbits())})
        if prime:
            largest_prime = max(largest_prime, q)
        else:
            full_factored = False
            largest_composite = max(largest_composite, q)
    return {
        "elapsed_seconds": elapsed,
        "full_factored": full_factored,
        "factors": entries,
        "largest_prime_factor": int(largest_prime),
        "largest_prime_factor_bits": int(largest_prime.nbits()),
        "largest_composite_cofactor_bits": int(largest_composite.nbits()) if largest_composite > 1 else int(0),
    }


def curve_summary(name, p, a, b, factor_twist_full=True, factor_limit=None):
    F = GF(Integer(p))
    E = EllipticCurve(F, [Integer(a) % p, Integer(b) % p])
    n = Integer(E.order())
    t = Integer(p) + 1 - n
    twist_order = Integer(p) + 1 + t
    twist_factor = factor_status(twist_order, full=factor_twist_full, limit=factor_limit)
    base_rho = rho_exp_bits(n)
    if twist_factor["full_factored"]:
        twist_ph = ph_exp_bits_from_lpf(twist_factor["largest_prime_factor"])
        speedup = base_rho - twist_ph
        verdict = "positive_twist_channel" if speedup >= 10.0 else "twist_not_meaningfully_easier"
    else:
        twist_ph = None
        speedup = None
        verdict = "twist_factorization_incomplete"

    return {
        "name": name,
        "p_bits": int(Integer(p).nbits()),
        "order_bits": int(n.nbits()),
        "order_prime": bool(n.is_prime(proof=False)),
        "rho_exp_bits": base_rho,
        "cm": cm_summary(p, n),
        "twist_order_bits": int(twist_order.nbits()),
        "twist_factor": twist_factor,
        "twist_ph_exp_bits": twist_ph,
        "twist_speedup_bits_vs_base_rho": speedup,
        "twist_verdict": verdict,
        "same_field_isogeny_channel": {
            "status": "closed_for_order_based_channels",
            "reason": "F_p-isogenous curves have the same trace and order; rho, anomalous, MOV embedding-degree input, and CM-field inputs are class-invariant.",
        },
        "scalar_weil_restriction_channel": {
            "status": "diagnostic_only",
            "reason": "The target subgroup embeds in scalar Weil restrictions, but the scalar basis split preserves Semaev per-variable degree and adds variables.",
        },
    }


def find_prime_order_toy(p, seed):
    rng = random.Random(int(seed))
    F = GF(Integer(p))
    for attempt in range(5000):
        a = Integer(rng.randrange(0, int(p)))
        b = Integer(rng.randrange(0, int(p)))
        if (4 * a**3 + 27 * b**2) % p == 0:
            continue
        E = EllipticCurve(F, [a, b])
        n = Integer(E.order())
        if n.is_prime(proof=False):
            return int(a), int(b), int(n), attempt + 1
    raise RuntimeError("no prime-order toy curve found for p=%s" % p)


def main():
    p256 = Integer(2)**256 - Integer(2)**224 + Integer(2)**192 + Integer(2)**96 - 1
    a256 = p256 - 3
    b256 = Integer(0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B)

    p224 = Integer(2)**224 - Integer(2)**96 + 1
    a224 = p224 - 3
    b224 = Integer(0xB4050A850C04B3ABF54132565044B0B7D7BFD8BA270B39432355FFB4)

    curves = []
    # P-256 is intentionally partial: a full factorization is unnecessary for the
    # sieve and can dominate runtime.  The older dedicated artifact contains the
    # full twist-security result.
    curves.append(curve_summary("NIST P-256", p256, a256, b256, factor_twist_full=False, factor_limit=10**6))
    curves.append(curve_summary("NIST P-224", p224, a224, b224, factor_twist_full=True))

    for idx, p in enumerate([101, 211, 431, 809, 1601, 4099]):
        a, b, n, attempts = find_prime_order_toy(Integer(p), 20260610 + idx)
        item = curve_summary("toy_prime_order_F_%s" % p, Integer(p), Integer(a), Integer(b), factor_twist_full=True)
        item["toy_generation"] = {"seed": 20260610 + idx, "attempts": attempts, "a": a, "b": b}
        curves.append(item)

    result = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_or_task": "Search for non-generic transfer/decomposition channels exposed by isogenous or corresponding objects.",
        "status": "OBSERVATION",
        "assumptions": [
            "Controlled public/toy curves only.",
            "Same-field isogeny channel is evaluated by class invariants, not graph enumeration.",
            "Quadratic twist is used as the positive-control extension-field isogenous object.",
            "Scalar Weil restriction is scored only as a diagnostic channel because prior proof notes cover its degree invariance.",
        ],
        "curves": curves,
    }
    print(json.dumps(json_clean(result), indent=2, sort_keys=True))


main()
