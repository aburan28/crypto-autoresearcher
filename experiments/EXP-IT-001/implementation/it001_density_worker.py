"""Multiprocessing worker for EXP-IT-001 density freeze (importable module)."""
from __future__ import annotations

from it001_lib import H_MAX_COFACTOR, unique_N_star


def worker_scan_chunk(args):
    """Process j in [j0, j1) over GF(p); return retained records + special counts."""
    p, j0, j1, bits = args
    from sage.all import GF, EllipticCurve_from_j

    F = GF(p)
    retained = []
    special = 0
    ordinary = 0
    tried = 0
    for j in range(j0, j1):
        tried += 1
        try:
            E = EllipticCurve_from_j(F(j))
        except Exception:
            continue
        try:
            if E.is_supersingular():
                continue
        except Exception:
            continue
        ordinary += 1
        try:
            order = int(E.order())
        except Exception:
            continue
        u = unique_N_star(order, bits, H_MAX_COFACTOR)
        if u is None:
            continue
        Nstar, hstar = u
        retained.append((int(j), int(Nstar), int(hstar), int(order)))
        is_spec = False
        if order == p:
            is_spec = True
        else:
            for k in range(1, 7):
                if (pow(p, k) - 1) % Nstar == 0:
                    is_spec = True
                    break
        if is_spec:
            special += 1
    return {
        "retained": retained,
        "special": special,
        "ordinary": ordinary,
        "tried": tried,
    }
