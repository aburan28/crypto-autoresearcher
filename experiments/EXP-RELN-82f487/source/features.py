"""Feature computation, F0/F1, per specification.yaml's
independent_variables.gnn_architecture.feature_set_F0/F1. Coordinates-only:
this module MUST NOT import the label/enumeration code path
(enumerate_counts.py, lookup_labels.py) or any discrete-logarithm scalar.
source/leak_audit.py enforces this statically; see that module for the
planted-leak diagnostic that a modified copy of this file must be rejected
by.

E-arm features operate on affine points (x, y). Z/N-arm features operate on
a residue r standing in for x; y is absent (per spec).
"""
from __future__ import annotations

import numpy as np


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def _low4(v: int) -> int:
    return v & 0xF


def fixed_translate_points_E(curve, base_seed: int, k: int = 8):
    """k fixed points P_i on the curve, chosen deterministically by
    base_seed, independent of D and of the target-generation scalar."""
    import hashlib

    pts = []
    x = 1
    for i in range(k):
        h = hashlib.sha256(f"{base_seed}:translate_E:{i}".encode()).hexdigest()
        xv = int(h, 16) % curve.p
        R = curve.lift_x(xv)
        tries = 0
        while R is None and tries < 200:
            xv = (xv + 1) % curve.p
            R = curve.lift_x(xv)
            tries += 1
        pts.append(R)
    return pts


def fixed_translate_residues_ZN(N: int, base_seed: int, k: int = 8):
    import hashlib
    ds = []
    for i in range(k):
        h = hashlib.sha256(f"{base_seed}:translate_ZN:{i}".encode()).hexdigest()
        ds.append(1 + (int(h, 16) % (N - 1)))
    return ds


def base_summary_E(curve, D):
    xs = [pt[0] if pt is not None else 0 for pt in D]
    p = curve.p
    hist, _ = np.histogram(xs, bins=16, range=(0, p))
    hist = hist.astype(np.float64) / max(1, len(xs))
    legs = [legendre(x, p) for x in xs]
    profile = np.array([
        sum(1 for v in legs if v == 1) / max(1, len(legs)),
        sum(1 for v in legs if v == -1) / max(1, len(legs)),
        sum(1 for v in legs if v == 0) / max(1, len(legs)),
    ])
    return np.concatenate([hist, profile])


def base_summary_ZN(N, D):
    hist, _ = np.histogram(D, bins=16, range=(0, N))
    hist = hist.astype(np.float64) / max(1, len(D))
    legs = [legendre(d, N) for d in D]
    profile = np.array([
        sum(1 for v in legs if v == 1) / max(1, len(legs)),
        sum(1 for v in legs if v == -1) / max(1, len(legs)),
        sum(1 for v in legs if v == 0) / max(1, len(legs)),
    ])
    return np.concatenate([hist, profile])


def compute_features_E(curve, targets, translate_points, regime: str, base_summary=None):
    """targets: list of (x,y) points (never None/identity in this
    experiment's target universe, since the point at infinity is not a
    scorable target). Returns (n, d) float array."""
    p = curve.p
    n = len(targets)
    rows = []
    for (x, y) in targets:
        feats = [
            x / p, y / p,
            _low4(x) / 15.0, _low4(y) / 15.0,
            legendre(x, p), legendre((x + 1) % p, p),
            1.0, x / p, y / p, (x * x % p) / p,
        ]
        for Pi in translate_points:
            if Pi is None:
                feats.extend([0.0, 0.0])
                continue
            Rp = curve.add((x, y), Pi)
            Rm = curve.add((x, y), curve.negate(Pi))
            feats.append((Rp[0] / p) if Rp is not None else -1.0)
            feats.append((Rm[0] / p) if Rm is not None else -1.0)
        rows.append(feats)
    arr = np.array(rows, dtype=np.float64)
    if regime == "F1":
        assert base_summary is not None
        arr = np.concatenate([arr, np.tile(base_summary, (n, 1))], axis=1)
    return arr


def compute_features_ZN(N, targets, translate_residues, regime: str, base_summary=None):
    n = len(targets)
    rows = []
    for r in targets:
        feats = [
            r / N,
            _low4(r) / 15.0,
            legendre(r, N), legendre((r + 1) % N, N),
            1.0, r / N, (r * r % N) / N,
        ]
        for d in translate_residues:
            feats.append(((r + d) % N) / N)
            feats.append(((r - d) % N) / N)
        rows.append(feats)
    arr = np.array(rows, dtype=np.float64)
    if regime == "F1":
        assert base_summary is not None
        arr = np.concatenate([arr, np.tile(base_summary, (n, 1))], axis=1)
    return arr


def plant_log_feature_MODULE_FOR_AUDIT_DIAGNOSTIC_ONLY():
    """Deliberately-bad reference kept OUT of the real feature path; used
    only by leak_audit.py's static scan of a synthetic planted-leak source
    string, never executed. See leak_audit.py.
    """
    raise RuntimeError("this function must never be called")
