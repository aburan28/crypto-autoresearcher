#!/usr/bin/env python3
"""EXP-ECDLP-420e73 Stage 0 planted-affine instrument. Certificate kind none."""
from __future__ import annotations

import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np

N = 8191
D = 20
PLANTED_A = 3
PLANTED_B = 7
SHUFFLE_SEED = 20260908
HEADER_BITS = 64
V = list(range(D))
SOURCE = "experiments/EXP-ECDLP-420e73/implementation/stage0_planted_affine.py"


def identity_residuals(n: int = N) -> dict:
    """N-unit identity from IDEA-20260904-d84512 (B) / H-ECDLP-77caa5 P-S0-IDENTITY.

    At gamma=0, S = N^theta and T = N^{1-theta}, so log_N(S*T^2) = 2-theta.
    The specification also writes 'S = D * log2 N' for the bit length; that
    log2 N cofactor is recorded separately and is not the 1e-12 gate.
    """
    logn = math.log(n)
    rows = []
    ok = True
    bit_rows = []
    for theta in (1.0 / 3.0, 0.5, 1.0):
        s = n**theta
        t = n ** (1.0 - theta)
        predicted = 2.0 - theta
        realized = math.log(s * t * t) / logn
        rel = abs(realized - predicted) / max(abs(predicted), 1e-18)
        rows.append(
            {
                "theta": theta,
                "predicted_logN_ST2": predicted,
                "realized_logN_ST2": realized,
                "relative_error": rel,
            }
        )
        if rel > 1e-12:
            ok = False
        s_bits = (n**theta) * math.log2(n)
        bit_realized = math.log(s_bits * t * t) / logn
        bit_rows.append(
            {
                "theta": theta,
                "bitlength_logN_ST2": bit_realized,
                "cofactor_logN": math.log(math.log2(n)) / logn,
            }
        )
    return {
        "identity_pass": ok,
        "units": "N-unit S=N^theta from idea (B)",
        "rows": rows,
        "bitlength_cofactor_rows": bit_rows,
    }


def recover_affine(vs: list[int], ks: list[int]) -> tuple[int | None, int | None, bool]:
    if len(vs) < 2:
        return None, None, False
    v0, v1 = vs[0], vs[1]
    k0, k1 = ks[0], ks[1]
    dv = (v1 - v0) % N
    if dv == 0:
        return None, None, False
    a = ((k1 - k0) * pow(dv, -1, N)) % N
    b = (k0 - a * v0) % N
    exact = all((a * v + b) % N == k for v, k in zip(vs, ks))
    return a, b, exact


def s_c_bits() -> int:
    return 2 * math.ceil(math.log2(N)) + HEADER_BITS


def gammas(s_bits: int) -> dict:
    denom_power = D * math.log2(N)
    denom_linear = D * math.log2(N / D)
    return {
        "S_C_bits": s_bits,
        "gamma_power": 1.0 - math.log(s_bits) / math.log(denom_power),
        "gamma_linear": 1.0 - s_bits / denom_linear,
    }


def main() -> int:
    t0 = time.perf_counter()
    identity = identity_residuals()
    planted_k = [(PLANTED_A * v + PLANTED_B) % N for v in V]
    pa, pb, planted_exact = recover_affine(V, planted_k)
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffled_k = rng.permutation(np.array(planted_k, dtype=np.int64)).tolist()
    sa, sb, shuffle_exact = recover_affine(V, shuffled_k)
    s_bits = s_c_bits()
    planted_g = gammas(s_bits)
    shuffle_g = gammas(s_bits)
    fixture_pass = (
        identity["identity_pass"]
        and planted_exact
        and pa == PLANTED_A
        and pb == PLANTED_B
        and not shuffle_exact
    )
    raw = {
        "run_id": "RUN-ECDLP-420e73-S0",
        "experiment_id": "EXP-ECDLP-420e73",
        "hypothesis_id": "H-ECDLP-77caa5",
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_curve_measurement": True,
        "not_an_H1_claim": True,
        "fixture": {
            "N": N,
            "D": D,
            "V": V,
            "planted_a": PLANTED_A,
            "planted_b": PLANTED_B,
            "shuffle_seed": SHUFFLE_SEED,
        },
        "identity": identity,
        "planted": {
            "recovers_exact_affine": planted_exact,
            "a_hat": pa,
            "b_hat": pb,
            **planted_g,
        },
        "shuffle": {
            "recovers_exact_affine": shuffle_exact,
            "a_hat": sa,
            "b_hat": sb,
            **shuffle_g,
        },
        "fixture_pass": fixture_pass,
        "validity_status": "valid" if fixture_pass else "failed_infrastructure",
        "scientific_boundary": (
            "Synthetic 20-row planted-affine instrument only. "
            "Not a curve. Not H1. Not a W class. No a98ea9 Stage 5."
        ),
        "wall_clock_seconds": time.perf_counter() - t0,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    print(json.dumps(raw, indent=2, sort_keys=True))
    return 0 if fixture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
