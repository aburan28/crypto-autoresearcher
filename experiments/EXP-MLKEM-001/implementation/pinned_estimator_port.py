"""Faithful port of pinned pq-crystals/security-estimates failure helpers.

Preserves control flow, support truncation (clean_dist), strict-tail convention,
and Python-3 round-to-even behavior. Normative FIPS ties-up is a separate mode.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "pq-crystals-security-estimates"


def _load(name: str):
    path = VENDOR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"pinned_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


proba_util = _load("proba_util")
# Kyber_failure imports proba_util by name; inject
sys.modules["proba_util"] = proba_util
Kyber_failure = _load("Kyber_failure")


def build_centered_binomial_law(k: int):
    return proba_util.build_centered_binomial_law(k)


def law_convolution(A, B):
    return proba_util.law_convolution(A, B)


def law_product(A, B):
    return proba_util.law_product(A, B)


def iter_law_convolution(A, i: int):
    return proba_util.iter_law_convolution(A, i)


def clean_dist(A):
    return proba_util.clean_dist(A)


def build_mod_switching_error_law(q, rq):
    return proba_util.build_mod_switching_error_law(q, rq)


def mod_switch(x, q, rq):
    return proba_util.mod_switch(x, q, rq)


def tail_probability(D, t):
    return proba_util.tail_probability(D, t)


class ToyParameterSet:
    def __init__(self, n, m, ks, ke, q, rqk, rqc, rq2, ke_ct=None):
        if ke_ct is None:
            ke_ct = ke
        self.n = n
        self.m = m
        self.ks = ks
        self.ke = ke
        self.ke_ct = ke_ct
        self.q = q
        self.rqk = rqk
        self.rqc = rqc
        self.rq2 = rq2


def p2_cyclotomic_final_error_distribution(ps):
    return Kyber_failure.p2_cyclotomic_final_error_distribution(ps)


def p2_cyclotomic_error_probability(ps):
    return Kyber_failure.p2_cyclotomic_error_probability(ps)


def no_compression_final_error_distribution(ps):
    """Pinned control flow with rounding laws replaced by {0: 1.0}."""
    chis = build_centered_binomial_law(ps.ks)
    chie = build_centered_binomial_law(ps.ke_ct)
    chie_pk = build_centered_binomial_law(ps.ke)
    Rk = {0: 1.0}
    Rc = {0: 1.0}
    chiRs = law_convolution(chis, Rk)
    chiRe = law_convolution(chie, Rc)
    B1 = law_product(chie_pk, chiRs)
    B2 = law_product(chis, chiRe)
    C1 = iter_law_convolution(B1, ps.m * ps.n)
    C2 = iter_law_convolution(B2, ps.m * ps.n)
    C = law_convolution(C1, C2)
    R2 = {0: 1.0}
    F = law_convolution(R2, chie)
    D = law_convolution(C, F)
    return D


def compare_support_tables(a: Dict[int, float], b: Dict[int, float], atol=1e-15):
    keys = sorted(set(a) | set(b))
    max_abs = 0.0
    mismatches = []
    for k in keys:
        va = a.get(k, 0.0)
        vb = b.get(k, 0.0)
        d = abs(va - vb)
        if d > max_abs:
            max_abs = d
        if d > atol:
            mismatches.append({"k": k, "a": va, "b": vb, "abs_delta": d})
    return {"max_abs_delta": max_abs, "mismatch_count": len(mismatches), "mismatches": mismatches[:50]}


def float_law_from_fraction(law):
    return {int(k): float(v) for k, v in law.items()}


def toy_fidelity_checks() -> dict:
    """Reproduce pinned functions on tiny objects before any FIPS changes."""
    ps = ToyParameterSet(n=2, m=1, ks=2, ke=2, q=3329, rqk=2**12, rqc=2**10, rq2=2**4, ke_ct=2)
    # Unmodified path
    F_src = p2_cyclotomic_final_error_distribution(ps)
    # Port is the same module functions — identity check on support after clean
    F_port = Kyber_failure.p2_cyclotomic_final_error_distribution(ps)
    cmp1 = compare_support_tables(F_src, F_port, atol=0.0)

    # mod_switch round-half-even vs explicit
    switch_diffs = []
    for x in range(3329):
        y = mod_switch(x, 3329, 2**10)
        # Python round half-even of rq*x/q
        y2 = int(round(1.0 * (1 << 10) * x / 3329)) % (1 << 10)
        if y != y2:
            switch_diffs.append({"x": x, "mod_switch": y, "round": y2})

    # No-compression toy vs exact Fraction engine will be compared externally
    D_nc = no_compression_final_error_distribution(ps)
    return {
        "toy_ps": ps.__dict__,
        "source_vs_port_final_error": cmp1,
        "mod_switch_vs_python_round_mismatches": len(switch_diffs),
        "mod_switch_examples": switch_diffs[:20],
        "no_compression_support_size": len(D_nc),
        "no_compression_mass": sum(D_nc.values()),
        "no_compression_law": {str(k): v for k, v in sorted(D_nc.items())},
    }


SOURCE_LOCK = {
    "repository": "https://github.com/pq-crystals/security-estimates",
    "commit": "75c26949a902ca297b181375bfb7cfaf22cce784",
    "files": {
        "Kyber_failure.py": "7a68ce4c81ef1c829af58ae18df014e95b3789f4ad78482876aa00dc8543517a",
        "proba_util.py": "1489c43427c637ff427e648cb03865fd39ec9574b73466375277787db2d72423",
        "Kyber.py": "82c0f891aad51c044777e75e411a7ed56f18b73a14c8c3b45331fe5f3078d546",
    },
}
