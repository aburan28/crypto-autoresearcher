"""Spawn-safe Groebner child for the EXP-FIB-001 cells.

``driver.decompcost.measure_s4_decomposition`` runs each solve in a ``spawn``
child, which re-imports ``driver.decompcost`` from scratch, so an arm
installed in the parent never reaches the child.  The parent replaces
``decompcost._worker`` with ``solve`` below; the child reads the arm from the
inherited ``EXP_S4RR_ARM`` environment variable, installs it into its own fresh
``driver.decompcost`` and runs the original, unmodified ``_worker``.
"""
from __future__ import annotations

import os
import sys


def solve(p, a, b, V, xR, q):
    import arms
    from driver import decompcost
    prov = arms.install(decompcost, os.environ["EXP_S4RR_ARM"], fingerprint=False)
    print(f"fib_child arm={prov['arm']} module={prov['installed_function_module']} "
          f"sha256={prov['s4_source_sha256'][:12]}", file=sys.stderr, flush=True)
    decompcost._worker(p, a, b, V, xR, q)
