#!/usr/bin/env python3
"""
Validator-built control for TASK-20260814-b13873 target #2: is
beta(M2)=617 (reduced_m=236, base m=n=1024) a smooth continuation of how
primal_bdd's beta scales with m, or does the m<<n regime behave
discontinuously/anomalously?

Sweeps m from 1024 (=base Kyber1024 m, using base Xe -- must reproduce
beta=855, the known-answer-controlled key-side reference, as a sanity
self-check) down through the M2 value (236) and below, keeping Xe/Xs at
their BASE Kyber1024 values throughout (i.e. this sweep uses the KEY-SIDE
noise, not the M2-construction noise, to isolate the effect of m alone from
the effect of also changing the noise distribution -- a second, separate
sweep at the M2 stddev is included for direct comparison).
"""
import sys
import math
import json

from estimator import RC, schemes
from estimator.lwe_primal import primal_bdd

M_VALUES = [1024, 900, 800, 700, 600, 500, 450, 400, 350, 300, 260, 236, 220, 200, 180, 150, 120, 100, 80, 60, 40, 20]

M2_STDDEV = (2 / 2) ** 0.5  # eta1=2 for Kyber1024, Var(CBD(2))=eta1/2=1, stddev=1.0
from estimator.nd import DiscreteGaussian


def sweep(scheme, xe_override_stddev=None, label=""):
    out = []
    for m in M_VALUES:
        params = scheme.updated(m=m, tag=f"{label}-m{m}")
        if xe_override_stddev is not None:
            params = params.updated(Xe=DiscreteGaussian(xe_override_stddev))
        try:
            r = primal_bdd(params, red_cost_model=RC.MATZOV)
            out.append({
                "m": m,
                "beta": int(r["beta"]),
                "eta": int(r["eta"]),
                "d": int(r["d"]),
                "log2_rop": math.log2(float(r["rop"])),
            })
        except Exception as exc:
            out.append({"m": m, "error": f"{type(exc).__name__}: {exc}"})
    return out


def main():
    base_sweep = sweep(schemes.Kyber1024, xe_override_stddev=None, label="base-Xe")
    m2_noise_sweep = sweep(schemes.Kyber1024, xe_override_stddev=M2_STDDEV, label="M2-noise")

    # sanity self-check: m=1024 with base Xe must equal the known-answer-
    # controlled key-side reference (beta=855) exactly.
    m1024_entry = next(e for e in base_sweep if e["m"] == 1024)
    self_check_pass = m1024_entry.get("beta") == 855

    out = {
        "base_Xe_sweep_key_side_noise_varying_m_only": base_sweep,
        "M2_noise_sweep_M2_stddev_varying_m": m2_noise_sweep,
        "self_check_m1024_matches_known_answer_855": self_check_pass,
        "self_check_m1024_beta_observed": m1024_entry.get("beta"),
    }
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
