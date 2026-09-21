#!/usr/bin/env python3
"""EXP-XEDN-002 shared library: frozen-predicate access, closed forms,
independent square references, vectorized section fibering, run-record writers.

Provenance
----------
The square predicate is NOT reimplemented here. It is loaded verbatim by file
path from experiments/EXP-XEDN-001/xedni_sections.py (read-only; never edited)
and its sha256 is recorded in every run's raw-result.json. The module's main()
is guarded by __name__ == "__main__", so importing it has no side effects.

Frozen predicate semantics (established by reading the frozen code, verified in
arm B and control 1):
  is_square_poly(f, p) returns h != None  iff  f is a nonzero perfect square in
  F_p[t] of even degree WHOSE SQUARE ROOT IS SQUAREFREE.
    * f = [0] (the y = 0 two-torsion section) -> None (lc = 0 fails the QR test)
    * odd degree -> None
    * lc(f) must be a quadratic residue
    * h = gcd(f, f') is monic; the test 2*deg(h) == deg(f) holds iff the square
      root of f is squarefree, so squares with non-squarefree roots (e.g. t^4)
      are FALSE NEGATIVES of the predicate
    * the re-squaring check f == lc(f) * h^2 makes false positives impossible
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import platform
import resource
import subprocess
import sys
from fractions import Fraction

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FROZEN_PATH = os.path.join(REPO_ROOT, "experiments", "EXP-XEDN-001",
                           "xedni_sections.py")
EXP_DIR = os.path.join(REPO_ROOT, "experiments", "EXP-XEDN-002")

SEEDS = [20260718, 20260724]

# ---------------------------------------------------------------- frozen oracle


def load_frozen():
    """Import the frozen EXP-XEDN-001 module by path; return (module, sha256)."""
    with open(FROZEN_PATH, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    spec = importlib.util.spec_from_file_location("xedn001_frozen", FROZEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, digest


# ------------------------------------------------------- closed forms (arm A/D)
# Derivation in experiments/EXP-XEDN-002/derivation.md.  Every formula below is
# also checked against a direct enumeration (arm B / control run).


def n_slots(p: int) -> int:
    """#{(b, x)}: b of degree exactly 6, x monic quadratic."""
    return (p - 1) * p**6 * p**2


def monic_squarefree(n: int, p: int) -> int:
    """# monic squarefree polynomials of degree exactly n over F_p."""
    if n == 0:
        return 1
    if n == 1:
        return p
    return p**n - p**(n - 1)


def q_pred(p: int) -> int:
    """#{f : deg f <= 6, [t^6]f != 1, frozen predicate accepts f}.

    = (1/2) * #{y != 0 squarefree, deg y <= 3, lc-of-degree-3 not +-1}
    """
    return (p**4 - 3 * p**3 + 2 * p**2 + p - 1) // 2


def q_pred_by_parts(p: int) -> dict:
    """The same count assembled from its four degree strata (self-check)."""
    parts = {
        "y_deg0": (p - 1) * monic_squarefree(0, p),
        "y_deg1": (p - 1) * monic_squarefree(1, p),
        "y_deg2": (p - 1) * monic_squarefree(2, p),
        "y_deg3_lc_not_pm1": (p - 3) * monic_squarefree(3, p),
    }
    parts["total_y"] = sum(parts.values())
    parts["total_f"] = parts["total_y"] // 2
    return parts


def q_true_square(p: int) -> int:
    """Same count under the MATHEMATICAL predicate (any nonzero square)."""
    return (p**4 - 2 * p**3 - 1) // 2


def q_missed_by_frozen(p: int) -> int:
    """Nonzero squares with non-squarefree root: frozen false negatives."""
    return (p**3 - 2 * p**2 - p) // 2


def n_hit(p: int) -> int:
    """Arm A: exact number of hit slots under the frozen predicate."""
    return p**2 * q_pred(p)


def n_hit_true_square(p: int) -> int:
    return p**2 * q_true_square(p)


def n_hit_including_zero_section(p: int) -> int:
    """If the excluded y = 0 section were counted (f = 0, i.e. b = -x^3)."""
    return p**2 * (q_pred(p) + 1)


def p_lift(p: int) -> Fraction:
    return Fraction(n_hit(p), n_slots(p))


def p_lift_true_square(p: int) -> Fraction:
    return Fraction(n_hit_true_square(p), n_slots(p))


def p_lift_with_zero_section(p: int) -> Fraction:
    return Fraction(n_hit_including_zero_section(p), n_slots(p))


def mean_sections_per_surface(p: int) -> Fraction:
    """Exact expected number of hit SLOTS per surface (= p^2 * P_lift)."""
    return Fraction(n_hit(p), (p - 1) * p**6)


def alpha_eff(p1: int, p2: int, prob) -> float:
    """Exact finite-size exponent between two sizes: -log(P2/P1)/log(p2/p1)."""
    import math
    return -math.log(float(prob(p2)) / float(prob(p1))) / math.log(p2 / p1)


def sextic_square_rate(p: int) -> Fraction:
    """Frozen-predicate hit rate among polynomials of degree EXACTLY 6.

    (the EXP-XEDN-001 part-4 negative-control population)
    """
    hits = (p - 1) * monic_squarefree(3, p) // 2
    return Fraction(hits, (p - 1) * p**6)


# ---- arm D: free (non-monic) x variant, exact -------------------------------


def n_hit_free_x(p: int) -> int:
    """Exact hit count when x ranges over ALL polys of degree <= 2.

    Slot space becomes {(b, x) : deg b = 6, deg x <= 2}; the constraint
    deg b = 6 becomes [t^6](y^2 - x^3) = y_3^2 - x_2^3 != 0.  This is OUTSIDE
    the frozen slot definition and is reported only as arm-D corroboration.
    """
    # squarefree y of degree <= 3 with prescribed leading coefficient y_3
    sf_by_lc = {}
    sf_by_lc[0] = ((p - 1) * monic_squarefree(0, p)
                   + (p - 1) * monic_squarefree(1, p)
                   + (p - 1) * monic_squarefree(2, p))
    for c in range(1, p):
        sf_by_lc[c] = monic_squarefree(3, p)
    pairs = 0
    for x2 in range(p):
        cube = pow(x2, 3, p)
        for y3 in range(p):
            if (y3 * y3 - cube) % p != 0:
                pairs += sf_by_lc[y3]
    pairs *= p**2                     # x_1, x_0 free
    assert pairs % 2 == 0
    return pairs // 2


def n_slots_free_x(p: int) -> int:
    return (p - 1) * p**6 * p**3


def codim_slot(A, B, d, e, has_a=True) -> int:
    """Parameter-count codimension of the section condition, per SLOT.

    c_slot = max(B, 3d, 2e, A+d) - e     (A+d term present only if a != 0)
    """
    terms = [B, 3 * d, 2 * e]
    if has_a:
        terms.append(A + d)
    return max(terms) - e


def codim_surface(A, B, d, e, delta, has_a=True) -> int:
    """Same, per SURFACE: c_surf = c_slot - delta, delta = # free x parameters."""
    return codim_slot(A, B, d, e, has_a) - delta


def rigorous_upper_bound_exponent(A, B, d, e, has_a=True) -> int:
    """E - B with E = min(e, floor(max(3d, A+d, B)/2)); P_slot <= p^(E-B)."""
    terms = [3 * d, B]
    if has_a:
        terms.append(A + d)
    E = min(e, max(terms) // 2)
    return E - B


# --------------------------------------------- independent square references
# Algorithmically disjoint from the frozen gcd-based predicate.


def sqrt_table(p: int) -> dict:
    """c -> a square root of c (one of the two), for c a nonzero QR."""
    tab = {}
    for a in range(1, p):
        tab.setdefault(a * a % p, a)
    return tab


def _trim(f: list) -> list:
    """Return a trimmed copy (the frozen module's coefficient convention)."""
    g = list(f)
    while len(g) > 1 and g[-1] == 0:
        g.pop()
    return g


def ref_poly_sqrt(f: list, p: int, sqrts: dict):
    """Independent perfect-square test by top-down square-root extraction.

    Coefficients low-to-high; trailing zeros are trimmed defensively so the
    result cannot depend on the caller's convention.
    Returns y with y^2 == f, or None.  Uses no gcd and no factorization:
    y's coefficients are solved one at a time from the top, then verified.
    """
    f = _trim(f)
    if f == [0]:
        return None
    n = len(f) - 1
    if n % 2:
        return None
    d = n // 2
    lead = sqrts.get(f[n])
    if lead is None:
        return None
    y = [0] * (d + 1)
    y[d] = lead
    inv2lead = pow(2 * lead % p, p - 2, p)
    for k in range(1, d + 1):
        # [t^(2d-k)] y^2 = 2*y_d*y_(d-k) + sum_{i=d-k+1}^{d-1} y_i*y_(2d-k-i)
        acc = 0
        for i in range(d - k + 1, d):
            j = 2 * d - k - i
            if 0 <= j <= d:
                acc += y[i] * y[j]
        y[d - k] = (f[2 * d - k] - acc) % p * inv2lead % p
    # verify
    sq = [0] * (2 * d + 1)
    for i in range(d + 1):
        if y[i]:
            for j in range(d + 1):
                if y[j]:
                    sq[i + j] = (sq[i + j] + y[i] * y[j]) % p
    return y if sq == f else None


def ref_is_squarefree_disc(y: list, p: int) -> bool:
    """Squarefree test by DISCRIMINANT (no gcd, no factorization); deg y <= 3.

    Valid for p > 3.  deg 0/1 always squarefree; deg 2: b^2-4ac != 0;
    deg 3: 18abcd - 4b^3 d + b^2 c^2 - 4 a c^3 - 27 a^2 d^2 != 0
    with y = a t^3 + b t^2 + c t + d.
    """
    y = _trim(y)
    n = len(y) - 1
    if y == [0]:
        return False
    if n <= 1:
        return True
    if n == 2:
        c, b, a = y[0], y[1], y[2]
        return (b * b - 4 * a * c) % p != 0
    if n == 3:
        d3, c, b, a = y[0], y[1], y[2], y[3]
        disc = (18 * a * b * c * d3 - 4 * b**3 * d3 + b**2 * c**2
                - 4 * a * c**3 - 27 * a**2 * d3**2)
        return disc % p != 0
    raise ValueError("degree > 3 not supported by this reference")


def ref_predicate_hit(f: list, p: int, sqrts: dict) -> bool:
    """Independent reimplementation of the FROZEN predicate's semantics."""
    y = ref_poly_sqrt(f, p, sqrts)
    if y is None:
        return False
    return ref_is_squarefree_disc(y, p)


def sympy_square_class(f: list, p: int) -> str:
    """Third, fully independent classifier via factorization over GF(p).

    Returns 'square_squarefree_root' | 'square_other_root' | 'not_square'
    | 'zero'.  Slow; used on subsamples as a cross-check of the other two.
    """
    from sympy import GF, Poly, Symbol
    if all(c % p == 0 for c in f):
        return "zero"
    f = _trim([c % p for c in f])
    t = Symbol("t")
    poly = Poly(list(reversed(f)), t, domain=GF(p))
    lc = f[-1]
    lc_is_qr = pow(lc, (p - 1) // 2, p) == 1
    _, facs = poly.factor_list()
    exps = [m for _, m in facs]
    if any(m % 2 for m in exps) or not lc_is_qr:
        return "not_square"
    if all(m == 2 for m in exps):
        return "square_squarefree_root"
    return "square_other_root"


# ------------------------------------------------------- polynomial utilities


def poly_cube_monic_quadratic(x0: int, x1: int, p: int, frozen) -> list:
    xt = [x0, x1, 1]
    return frozen.pmul(frozen.pmul(xt, xt, p), xt, p)


def enumerate_deg6_b(p: int):
    """All b with deg b exactly 6, low-to-high coefficient lists."""
    for tail in itertools.product(*([range(p)] * 6)):
        for b6 in range(1, p):
            yield list(tail) + [b6]


# --------------------------------------------------------- run-record writers


def git_state() -> dict:
    def run(cmd):
        return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True,
                              text=True, check=True).stdout
    commit = run(["git", "rev-parse", "HEAD"]).strip()
    porcelain = run(["git", "status", "--porcelain"])
    lines = [l for l in porcelain.splitlines() if l.strip()]
    return {
        "commit": commit,
        "dirty_tree": bool(lines),
        "dirty_entries": len(lines),
        "dirty_detail": ("; ".join(lines[:12]) + (" ..." if len(lines) > 12 else ""))
                        if lines else "",
    }


def environment_json() -> dict:
    import numpy
    import sympy
    return {
        "python": platform.python_version(),
        "python_full": sys.version,
        "os": " ".join(os.uname()),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": {"numpy": numpy.__version__, "sympy": sympy.__version__,
                     "pyyaml": __import__("yaml").__version__},
        "cpu_count": os.cpu_count(),
        "memory_gb": 15,
        "frozen_predicate_path": os.path.relpath(FROZEN_PATH, REPO_ROOT),
        "frozen_predicate_sha256": load_frozen()[1],
    }


def peak_memory_mb() -> float:
    self_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    child_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return round(max(self_kb, child_kb) / 1024.0, 1)


INFERENCE_BLOCK = {
    "requested_policy": "executor-terra",
    "resolved_model": "claude-opus-5-thinking-max",
    "resolved_model_source": (
        "verified from the harness itself: cursor-cloud run-info originalModelName for "
        "run bc-019f9556-c64d-7309-8a8d-c9483ea64e70; this executor subagent inherits "
        "the session model (CLAUDE.md: .claude/agents entries use model: inherit)"),
    "reasoning_effort": ("unspecified: no numeric reasoning-effort setting is exposed to "
                        "the agent; the resolved model name reports 'thinking-max'"),
    "fallback_used": True,
    "fallback_reason": ("orchestration/model-policies.yaml routes the executor to a "
                        "GPT-5.6 Terra alias that this Claude-family harness cannot "
                        "resolve (CLAUDE.md model policy note)."),
}


def run_dir(run_id: str) -> str:
    d = os.path.join(EXP_DIR, "runs", run_id)
    os.makedirs(d, exist_ok=True)
    return d


def write_run_record(run_id: str, purpose: str, entrypoint: str, parameters: dict,
                     started_at: str, finished_at: str, wall: float,
                     validity: str, validity_reason: str, summary: str,
                     raw: dict, status: str = "completed") -> dict:
    """Write manifest.yaml, environment.json, raw-result.json for a run."""
    import yaml
    d = run_dir(run_id)
    env = environment_json()
    git = git_state()
    command = os.environ.get("XEDN2_COMMAND", "")
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-XEDN-002",
            "purpose": purpose,
            "status": status,
            "code": {
                "commit": git["commit"],
                "dirty_tree": git["dirty_tree"],
                "dirty_tree_detail": (
                    f"{git['dirty_entries']} porcelain entries at run time "
                    f"(this task's own new EXP-XEDN-002 files are untracked)"),
                "command": command,
                "entrypoint": entrypoint,
                "frozen_predicate_sha256": env["frozen_predicate_sha256"],
            },
            "environment": {
                "python": env["python"],
                "os": env["os"],
                "packages": env["packages"],
                "cpu_count": env["cpu_count"],
                "memory_gb": 15,
            },
            "inputs": {"parameters": parameters, "seeds": SEEDS},
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_clock_seconds": round(wall, 3),
                "peak_memory_mb": peak_memory_mb(),
            },
            "result": {
                "validity": validity,
                "validity_reason": validity_reason,
                "certificate": {
                    "kind": "none",
                    "note": ("pure counting experiment: no discrete-log solve and no "
                             "factor-base relation is claimed, so there is nothing to "
                             "certify (docs/claims-and-verification.md)"),
                },
                "summary": summary,
            },
            "inference": dict(INFERENCE_BLOCK),
        }
    }
    with open(os.path.join(d, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100)
    with open(os.path.join(d, "environment.json"), "w") as fh:
        json.dump(env, fh, indent=2)
    raw_out = dict(raw)
    raw_out["_meta"] = {
        "run_id": run_id,
        "experiment_id": "EXP-XEDN-002",
        "git_commit": git["commit"],
        "dirty_tree": git["dirty_tree"],
        "command": command,
        "entrypoint": entrypoint,
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_clock_seconds": round(wall, 3),
        "peak_memory_mb": peak_memory_mb(),
        "seeds": SEEDS,
        "frozen_predicate_path": env["frozen_predicate_path"],
        "frozen_predicate_sha256": env["frozen_predicate_sha256"],
        "inference": dict(INFERENCE_BLOCK),
    }
    with open(os.path.join(d, "raw-result.json"), "w") as fh:
        json.dump(raw_out, fh, indent=2, sort_keys=False)
    return manifest
