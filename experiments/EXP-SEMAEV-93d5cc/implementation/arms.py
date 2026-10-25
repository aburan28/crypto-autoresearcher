"""The two arms of EXP-SEMAEV-93d5cc: which ``s4_expr`` a cell runs with.

The arms differ in one function only.  ``legacy`` is ``s4_expr`` from the
exact bytes of ``harness/semaev.py`` that every exposed archived run recorded
(sha256 53a23952..., vendored under ``vendor/``); ``repaired`` is ``s4_expr``
from the current ``harness/semaev.py`` (pinned below).  Every other function
the cells call (S3, factor bases, curve arithmetic, Groebner, Singular) comes
from the current tree in both arms, so the arm contrast isolates the S4
construction.  Each consumer module binds ``s4_expr`` by name at import, so the
arm is installed by assigning that module attribute (``install``).
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LEGACY_PATH = HERE / "vendor" / "semaev_legacy_53a23952.py"
LEGACY_SHA256 = "53a23952420f8ee724b70746eb7c872e54cbb33dc4cb24be1e88dcdcbef4817e"
REPAIRED_PATH = REPO / "harness" / "semaev.py"
REPAIRED_SHA256 = "c417f1948d7df7bb1864726e169d885e4d3163cb62036393f2616ef71c630de6"
ARMS = ("legacy", "repaired")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _legacy_module():
    name = "harness._semaev_legacy_53a23952"
    if name in sys.modules:
        return sys.modules[name]
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    import harness  # noqa: F401  -- the vendored file uses package-relative imports
    spec = importlib.util.spec_from_file_location(name, LEGACY_PATH)
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "harness"
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def s4_function(arm: str):
    """Return (s4_expr, provenance) for one arm, refusing on any hash drift."""
    if arm == "legacy":
        digest = sha256(LEGACY_PATH)
        if digest != LEGACY_SHA256:
            raise RuntimeError(f"legacy semaev bytes changed: {digest}")
        fn = _legacy_module().s4_expr
        path = LEGACY_PATH
    elif arm == "repaired":
        digest = sha256(REPAIRED_PATH)
        if digest != REPAIRED_SHA256:
            raise RuntimeError(f"repaired semaev bytes changed: {digest}")
        if str(REPO) not in sys.path:
            sys.path.insert(0, str(REPO))
        import harness.semaev as semaev
        fn = semaev.s4_expr
        path = REPAIRED_PATH
    else:
        raise ValueError(f"unknown arm: {arm}")
    return fn, {"arm": arm, "s4_source": str(path.relative_to(REPO)),
                "s4_source_sha256": digest}


def self_test(fn) -> dict:
    """Instrument fingerprint of an arm's S4 on the frozen EXP-SEMAEV-a097b5
    fixture (y^2 = x^3 + 2x + 3 over F_101, abscissae 1, 3, 5, 41): free
    symbols, total degree and the witness residue.  Recorded, never gated on
    by the worker; the checker compares it with the arm's expected fingerprint."""
    import sympy
    expr = sympy.expand(fn(2, 3))
    syms = sorted(str(s) for s in expr.free_symbols)
    x1, x2, x3, x4 = sympy.symbols("x1 x2 x3 x4")
    poly = sympy.Poly(expr, x1, x2, x3, x4)
    value = int(poly.eval({x1: 1, x2: 3, x3: 5, x4: 41})) % 101
    return {"free_symbols": syms, "total_degree": poly.total_degree(),
            "terms_over_Z": len(poly.terms()), "witness_residue_mod_101": value}


def install(module, arm: str, *, fingerprint: bool = True) -> dict:
    """Bind ``module.s4_expr`` to the arm's function; return the provenance.

    ``fingerprint=False`` skips the ~1 s symbolic self-test; the timed
    EXP-FIB-001 spawn child uses it so the per-solve cap sees no added work."""
    fn, prov = s4_function(arm)
    if not hasattr(module, "s4_expr"):
        raise RuntimeError(f"{module.__name__} has no s4_expr binding to replace")
    module.s4_expr = fn
    prov["installed_into"] = module.__name__
    prov["installed_function_module"] = module.s4_expr.__module__
    if fingerprint:
        prov["installed_fingerprint"] = self_test(module.s4_expr)
    return prov
