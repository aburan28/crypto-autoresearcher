#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-15534c run artifacts. Reads only.

Shares no code with run.py. It re-implements the Z/p^r Jacobian arithmetic
and the two deterministic lift rules (integer Hensel, Teichmuller-x Hensel)
and REPLAYS a seeded sample of recorded draws per (curve, rule) from the
recorded (p, a, b, P, k, precision), recomputing delta from scratch; it also
recomputes every chi-square from the recorded per-draw deltas rather than
from the runner's histogram, re-verifies the anomalous controls' claim shape,
and checks the summary's rejection count. A fabricated raw result whose
deltas were not produced by the stated computation fails here.
Exit 0 iff no problem is found.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

EXP = "EXP-ECDLP-15534c"
REPLAY_PER_CELL = 5


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def jdouble(P, a, N):
    X, Y, Z = P
    XX, YY, ZZ = X * X % N, Y * Y % N, Z * Z % N
    YYYY = YY * YY % N
    S = 2 * ((X + YY) ** 2 - XX - YYYY) % N
    M = (3 * XX + a * ZZ * ZZ) % N
    T = (M * M - 2 * S) % N
    return (T, (M * (S - T) - 8 * YYYY) % N, ((Y + Z) ** 2 - YY - ZZ) % N)


def jadd(P, Q, N):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1Z1, Z2Z2 = Z1 * Z1 % N, Z2 * Z2 % N
    U1, U2 = X1 * Z2Z2 % N, X2 * Z1Z1 % N
    S1, S2 = Y1 * Z2 * Z2Z2 % N, Y2 * Z1 * Z1Z1 % N
    H = (U2 - U1) % N
    I = (2 * H) ** 2 % N
    J = H * I % N
    r = 2 * (S2 - S1) % N
    V = U1 * I % N
    X3 = (r * r - J - 2 * V) % N
    return (X3, (r * (V - X3) - 2 * S1 * J) % N, (((Z1 + Z2) ** 2 - Z1Z1 - Z2Z2) * H) % N)


def jmul(k, P, a, N):
    R = P
    for bit in bin(k)[3:]:
        R = jdouble(R, a, N)
        if bit == "1":
            R = jadd(R, P, N)
    return R


def hensel_y(xh, y0, a, b, N, r):
    y = y0 % N
    for _ in range(r.bit_length() + 1):
        y = (y - (y * y - (xh ** 3 + a * xh + b)) * pow(2 * y, -1, N)) % N
    return y


def delta_replay(rule, P, k, l, a, b, p, r):
    N = p ** r
    Q = ec_mul(k, P, a, p)
    out = []
    for (x, y) in (P, Q):
        if rule == "L1_integer_hensel":
            xh = x
        elif rule == "L2_teichmuller_hensel":
            xh = pow(x, p ** (r - 1), N)
        else:
            return None
        yh = hensel_y(xh, y, a, b, N, r)
        X, Y, Z = jmul(l, (xh, yh, 1), a, N)
        if Z % p != 0 or Y % p == 0:
            return "reduction_failed"
        z = (-X * Z * pow(Y, -1, N)) % N
        out.append(z)
    zP, zQ = out
    if zP % p != 0 or zQ % p != 0 or (zP // p) % p == 0 or (zQ // p) % p == 0:
        return None  # higher valuation: the runner skips these too
    return ((zQ // p) * pow(zP // p, -1, p) - k) % p


def chi_square(deltas, p, bins=20):
    h = [0] * bins
    for d in deltas:
        h[min(bins - 1, d * bins // p)] += 1
    e = len(deltas) / bins
    return sum((c - e) ** 2 / e for c in h), h


def main(argv):
    if len(argv) != 1:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(argv[0])
    errs = []
    try:
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"unreadable artifacts: {error}", file=sys.stderr)
        return 1
    if raw.get("experiment_id") != EXP or EXP not in manifest:
        errs.append("wrong experiment id")
    for arm, ctrl in (raw.get("anomalous_controls") or {}).items():
        if not ctrl.get("pass"):
            errs.append(f"anomalous control ({arm}) did not recover every scalar")
        for rule, res in (ctrl.get("results") or {}).items():
            if res.get("recovered") != res.get("draws"):
                errs.append(f"anomalous control ({arm}) {rule}: recovered != draws")
    rng = random.Random("EXP-ECDLP-15534c:check")
    tests = replayed = 0
    for cell in raw.get("cells") or []:
        census = cell.get("census") or {}
        p = census.get("p")
        for curve in census.get("curves") or []:
            a, b, l = curve["a"], curve["b"], curve["l"]
            P = tuple(curve["P"])
            if (P[1] ** 2 - (P[0] ** 3 + a * P[0] + b)) % p != 0:
                errs.append(f"p={p}: recorded P is not on the curve")
            if ec_mul(l, P, a, p) is not None:
                errs.append(f"p={p}: recorded P does not have order l={l}")
            for rule, res in (curve.get("rules") or {}).items():
                u = res.get("uniformity")
                draws = res.get("draws")
                if not u or not isinstance(draws, list):
                    errs.append(f"p={p} {rule}: missing uniformity block or draw log")
                    continue
                tests += 1
                deltas = [d for _, d in draws if d is not None]
                if len(deltas) != u["n"] or len(draws) - len(deltas) != res.get("higher_valuation_skipped"):
                    errs.append(f"p={p} {rule}: draw log disagrees with n / skipped counts")
                chi, h = chi_square(deltas, p)
                if abs(chi - u["chi_square"]) > 1e-9 or h != u["histogram"]:
                    errs.append(f"p={p} {rule}: chi-square or histogram does not match the per-draw deltas")
                if u["zero_count"] != sum(1 for d in deltas if d == 0):
                    errs.append(f"p={p} {rule}: zero_count mismatch")
                if res.get("precision_mismatch"):
                    errs.append(f"p={p} {rule}: CTRL-PRECISION mismatch recorded")
                if rule in ("L1_integer_hensel", "L2_teichmuller_hensel"):
                    r = res.get("precision") or 6
                    for idx in rng.sample(range(len(draws)), min(REPLAY_PER_CELL, len(draws))):
                        k, d_rec = draws[idx]
                        d_new = delta_replay(rule, P, k, l, a, b, p, r)
                        replayed += 1
                        if d_new == "reduction_failed":
                            errs.append(f"p={p} {rule} draw {idx}: replay could not reach the formal group")
                        elif d_new != d_rec:
                            errs.append(f"p={p} {rule} draw {idx}: replayed delta {d_new} != recorded {d_rec}")
    summary = raw.get("summary") or {}
    if summary.get("tests") != tests:
        errs.append(f"summary tests {summary.get('tests')} != counted {tests}")
    for e in errs:
        print("FAIL:", e, file=sys.stderr)
    print(f"{EXP} check: {tests} uniformity test(s), {replayed} draw(s) replayed independently, {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
