"""Bounded reproduction of Cheon--Lee--Hahn--Chee, section 4 (2000).

Only the paper's published polynomial family and synthetic F_353 points are used.
Primality uses 16 Miller--Rabin bases and is a probable-prime test, not a proof.
"""

import json
import platform
import time

P = 353
T1, T2 = 703, 439
X1, X2 = T1 * T1, -(T2 * T2)
Y1, Y2 = T1 * -21, T2 * 154
BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)


def probable_prime(n):
    if n < 2:
        return False
    for a in BASES:
        if n == a:
            return True
        if n % a == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def factors(n):
    b = 635728705996536026 * n - 1792587436107314570824479
    f1 = 124609 * n * n + 303443264744 * n + 8697969664620875680
    f2 = 124609 * n * n + 303442272108 * n + 8697963332447929000
    return b, f1, f2


def curve_coefficients(n):
    dx = X1 - X2
    def ordinate(t, y):
        gamma = pow(t * P, -1, dx)
        delta, remainder = divmod(1 - gamma * t * P, dx)
        assert remainder == 0
        return y * delta * dx + t * t * P * n
    y1, y2 = ordinate(T1, Y1), ordinate(T2, Y2)
    z1 = y1 * y1 // X1 - X1 * X1
    z2 = y2 * y2 // X2 - X2 * X2
    assert y1 * y1 % X1 == y2 * y2 % abs(X2) == 0
    a, r = divmod(z1 - z2, dx)
    assert r == 0
    b = z1 - a * X1
    return a, b, y1, y2


def main():
    start = time.monotonic()
    output = {
        "source": "https://www.math.snu.ac.kr/~jhcheon/publications/2000/JWISC00_CLH.pdf",
        "paper_section": 4,
        "python": platform.python_version(),
        "parameters": {"p": P, "a0": -1, "b0": 16, "t1": T1, "t2": T2,
                       "n_min": -2000, "n_max": 2000, "mr_bases": BASES},
        "input_points": [[9, 63], [17, 183]],
        "lift_x_reductions": [X1 % P, X2 % P],
        "lift_y_reductions": [Y1 % P, Y2 % P],
        "rejection_counts_first_failed_factor": {"b": 0, "f1": 0, "f2": 0},
        "passes": [], "failures": [],
    }
    for n in range(-2000, 2001):
        b, f1, f2 = factors(n)
        checks = [probable_prime(abs(v)) for v in (b, f1, f2)]
        if not all(checks):
            first = checks.index(False)
            output["rejection_counts_first_failed_factor"][('b', 'f1', 'f2')[first]] += 1
            continue
        try:
            a, b_calc, y1, y2 = curve_coefficients(n)
            assert b_calc == b
            assert a * a - 4 * b == f1 * f2
            assert (a % P, b_calc % P) == (-1 % P, 16)
            assert y1 * y1 == X1 * (X1 * X1 + a * X1 + b)
            assert y2 * y2 == X2 * (X2 * X2 + a * X2 + b)
            assert (y1 % P, y2 % P) == (63, 183)
            output["passes"].append({"n": n, "a": a, "b": b,
                                     "factors": [b, f1, f2],
                                     "point_y": [y1, y2]})
        except Exception as exc:
            output["failures"].append({"n": n, "error": repr(exc)})
    output["elapsed_seconds"] = round(time.monotonic() - start, 6)
    output["tested_n"] = 4001
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
