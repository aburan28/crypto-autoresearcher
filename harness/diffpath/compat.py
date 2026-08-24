"""Import-time compatibility for the shared run wrapper. See _compat/sympy.py.

MUST be imported BEFORE harness.runner.  Returns a record of what it did, so
the workaround appears in the run artifacts instead of only in the code.
"""
from __future__ import annotations

import importlib.util
import os
import sys

_COMPAT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_compat")


def ensure() -> dict:
    real = importlib.util.find_spec("sympy") if "sympy" not in sys.modules else None
    if real is not None and getattr(real, "origin", "") and _COMPAT_DIR not in (real.origin or ""):
        return {"sympy_shim_used": False,
                "reason": "a real sympy is importable; no shim installed"}
    if _COMPAT_DIR not in sys.path:
        sys.path.insert(0, _COMPAT_DIR)
    stub = _install_semaev_stub()
    return {
        "sympy_shim_used": True,
        "harness_semaev_stub_installed": stub,
        "reason": ("sympy is not installed in this environment and IR-10 "
                   "forbids acquiring it over the network; `uv pip install "
                   "--offline --system sympy` was attempted and FAILED (the "
                   "wheel is not in the local uv cache). IR-6 forbids editing "
                   "harness/runner.py, which imports sympy at module scope and "
                   "uses it only for sympy.__version__ in the environment "
                   "block."),
        "effect_on_results": ("NONE. Every certificate in EXP-DIFFP-fe894e is "
                              "kind: none, so no certificate-verification path "
                              "that could use a CAS is entered. The only "
                              "observable effect is that environment.json "
                              "records the sympy version as ABSENT, which is "
                              "the truth."),
        "shim_path": os.path.join(_COMPAT_DIR, "sympy.py"),
        "semaev_stub_reason": (
            "harness/runner.py::_verify imports harness.semaev UNCONDITIONALLY, "
            "before it dispatches on the certificate kind, and harness/semaev.py "
            "calls sympy.symbols at module scope. With no real sympy that import "
            "fails for every run, including runs whose certificate kind is "
            "`none`. A stub module is therefore placed in sys.modules for THIS "
            "PROCESS ONLY. Its verify_decomposition_certificate RAISES if it is "
            "ever called, so it cannot silently return a passing verification: "
            "if a decomposition certificate ever reached it, the run would fail "
            "loudly rather than record a fabricated verification. Every "
            "certificate in EXP-DIFFP-fe894e is kind `none`, so it is never "
            "called."),
    }


def _install_semaev_stub() -> bool:
    import types
    if "harness.semaev" in sys.modules:
        return False

    def verify_decomposition_certificate(*_a, **_k):
        raise RuntimeError(
            "harness.diffpath.compat stub: harness.semaev is unavailable "
            "because sympy is not installed in this environment. This stub "
            "REFUSES to verify anything rather than returning a value. "
            "EXP-DIFFP-fe894e emits only `kind: none` certificates, so "
            "reaching this line means a certificate of another kind was "
            "written and its verification MUST NOT be recorded as passed.")

    mod = types.ModuleType("harness.semaev")
    mod.verify_decomposition_certificate = verify_decomposition_certificate
    mod.__diffpath_stub__ = True
    sys.modules["harness.semaev"] = mod
    return True
