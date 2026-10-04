#!/usr/bin/env python3
"""Validator J1: INDEPENDENT quadrature re-solve.

Method deliberately different from the producer's (manifest: "bisection
bracketing (100 iterations, bracket [1e-9, 50]) plus Newton refinement"):
here we use PURE bisection, no Newton, on a different bracket [1e-6, 20],
200 iterations, math.erfc from the standard library.

Equation (specification.yaml definitions.C_max(a); derivation Lemma 5):
    f(x) = 2 x^{-1/2} e^{-x/2} - sqrt(2 pi) erfc(sqrt(x/2)) = a sqrt(2 pi)
    C_max(a) = erfc(sqrt(x*/2))
"""
import json
import math

SQ2PI = math.sqrt(2.0 * math.pi)


def f(x, a):
    return 2.0 * x ** -0.5 * math.exp(-x / 2.0) - SQ2PI * math.erfc(math.sqrt(x / 2.0)) - a * SQ2PI


def bisect(a, lo=1e-6, hi=20.0, iters=200):
    flo, fhi = f(lo, a), f(hi, a)
    assert flo > 0 > fhi, f"bracket failed for a={a}: f(lo)={flo}, f(hi)={fhi}"
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm = f(mid, a)
        if fm > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    anchors = {
        1.0:   {"x_star": 0.1903808702719756, "c_max": 0.6625998114129124},
        0.5:   {"x_star": 0.4045307067767451, "c_max": 0.5247586384598776},
        0.25:  {"x_star": 0.7423409681771704, "c_max": 0.3889120129663709},
        0.125: {"x_star": 1.2085522833979216, "c_max": 0.27161902810059757},
    }
    print("=== Q1: independent root solve vs committed anchors (tol 5e-5) ===")
    q1_ok = True
    for a in (1.0, 0.5, 0.25, 0.125):
        x = bisect(a)
        c = math.erfc(math.sqrt(x / 2.0))
        dx = abs(x - anchors[a]["x_star"])
        dc = abs(c - anchors[a]["c_max"])
        ok = dx < 5e-5 and dc < 5e-5
        q1_ok &= ok
        print(f"a={a:<6} x*={x!r}  dev_x={dx:.3e}   C_max={c!r}  dev_c={dc:.3e}  within_5e-5={ok}")
    print(f"Q1 (all four a within 5e-5): {q1_ok}")

    print()
    print("=== Q2: assembly minimum of sqrt(a)/C_max(a) on fine grid [0.05, 2] step 0.001 ===")
    best = None
    n = 0
    for i in range(1951):
        a = 0.05 + i * 0.001
        a = round(a, 3)
        x = bisect(a)
        c = math.erfc(math.sqrt(x / 2.0))
        v = math.sqrt(a) / c
        n += 1
        if best is None or v < best[1]:
            best = (a, v, x, c)
    a_min, v_min, x_min, c_min = best
    in_band = 0.2 <= a_min <= 0.25
    near_128 = abs(v_min - 1.28) <= 0.01
    print(f"grid points: {n}")
    print(f"minimum at a={a_min}  value={v_min!r}  (x*={x_min!r}, C_max={c_min!r})")
    print(f"location in [0.2, 0.25]: {in_band}; value within 0.01 of 1.28: {near_128} (|dev|={abs(v_min-1.28):.6f})")
    # neighbours, to show the minimum is stable
    for da in (-0.002, -0.001, 0.001, 0.002):
        a = round(a_min + da, 3)
        x = bisect(a)
        c = math.erfc(math.sqrt(x / 2.0))
        print(f"  neighbour a={a}: sqrt(a)/C_max = {math.sqrt(a)/c!r}")
    print(f"Q2: {in_band and near_128}")

    print()
    print("=== Q3: baseline-embedding values (tol 5e-3) ===")
    c_rand_1 = 1.0 - (1.0 + 2.0) ** -0.5
    x1 = bisect(1.0)
    c_max_1 = math.erfc(math.sqrt(x1 / 2.0))
    d1 = abs(c_rand_1 - 0.423)
    d2 = abs(c_max_1 - 0.66)
    print(f"c_rand(a_m=1) = 1 - 3^(-1/2) = {c_rand_1!r}  dev from 0.423 = {d1:.3e}  within 5e-3: {d1 < 5e-3}")
    print(f"c_max(a=1)    = {c_max_1!r}  dev from 0.66 = {d2:.3e}  within 5e-3: {d2 < 5e-3}")
    print(f"Q3: {d1 < 5e-3 and d2 < 5e-3}")

    print()
    print("=== residual check: f(x*) at the solved roots (should be ~0) ===")
    for a in (1.0, 0.5, 0.25, 0.125):
        x = bisect(a)
        print(f"a={a:<6} f(x*) = {f(x, a):.3e}")

    out = {
        "q1": [
            {"a": a, "x_star": bisect(a),
             "c_max": math.erfc(math.sqrt(bisect(a) / 2.0))}
            for a in (1.0, 0.5, 0.25, 0.125)
        ]
    }
    out["q2"] = {"a": a_min, "value": v_min, "x_star": x_min, "c_max": c_min,
                 "in_band": in_band, "near_128": near_128}
    out["q3"] = {"c_rand_1": c_rand_1, "c_max_1": c_max_1,
                 "dev_c_rand": d1, "dev_c_max": d2}
    with open("/Volumes/SSD990/llm/tmp/opencode/review-e962f6-20260910/experiments/EXP-ECDLP-e962f6/tasks/TASK-20260910-6d6bd3/work/j1_quadrature_independent.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nwritten: work/j1_quadrature_independent.json")


if __name__ == "__main__":
    main()
