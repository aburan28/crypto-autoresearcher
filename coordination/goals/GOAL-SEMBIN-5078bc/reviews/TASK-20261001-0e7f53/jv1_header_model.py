"""JV-1 (TASK-20261001-0e7f53): independent implementation of TOTAL from the
header block of AMD-20261001-e61f2b ALONE.

Written by the JV-1 validator before reading any file under
experiments/EXP-SEMBIN-04ec3c/code/v2/. Sources used: the amendment header block
(commit b8019a6fb) and r from the frozen input
inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md (sha256 a21e56ef...).

All quantities are log2. For a cell (n, m, d, s):
  N   = log2 r at n = 131, n elsewhere
  L   = log2(m!)
  S   = floor(m/2)
  K   = d
  TPR = N + L - m*d
  CALLS = K + TPR
  o   : FREE 0; ENUM (m-1)d; MITM (m-S)d with s = S;
        MITM_CAPPED (m-s)d with s = min(S, floor(log2 B / d))
  PROBE = K + TPR + o
  FILL  = s*d for MITM and MITM_CAPPED when s >= 1; 0 for FREE and ENUM
  LA    = 2d
  TOTAL = log2(2^PROBE + 2^FILL + 2^LA)
  VOW   = log2(0.886) + N/2
  PUB   = 60.8090 only at n = 131
"""
from __future__ import annotations

import math

# r copied from the frozen input text (line 230 of the talk transcript).
R_ECC2K130 = 680564733841876926932320129493409985129
DEGREES = (97, 109, 131, 163, 191, 233, 239, 283, 409, 571)
PUB_131 = 60.8090
MODELS = ("FREE", "ENUM", "MITM", "MITM_CAPPED")


def is_probable_prime(x: int) -> bool:
    if x < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if x % p == 0:
            return x == p
    d, r = x - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
        y = pow(a, d, x)
        if y in (1, x - 1):
            continue
        for _ in range(r - 1):
            y = y * y % x
            if y == x - 1:
                break
        else:
            return False
    return True


def N_of(n: int) -> float:
    return math.log2(R_ECC2K130) if n == 131 else float(n)


def L_of(m: int) -> float:
    return math.log2(math.factorial(m))


def log2sumexp2(*xs: float) -> float:
    mx = max(xs)
    return mx + math.log2(sum(2.0 ** (x - mx) for x in xs))


def vow(n: int) -> float:
    return math.log2(0.886) + N_of(n) / 2.0


def s_for(model: str, m: int, d: float, log2B: float | None) -> int:
    S = m // 2
    if model in ("FREE", "ENUM"):
        return 0
    if model == "MITM":
        return S
    if model == "MITM_CAPPED":
        if log2B is None:  # unlimited budget
            return S
        return min(S, int(math.floor(log2B / d)))
    raise ValueError(model)


def cell(n: int, m: int, d: float, model: str, log2B: float | None = None,
         s: int | None = None) -> dict:
    """Header-block cell. If s is None it is derived from the model's law."""
    N = N_of(n)
    L = L_of(m)
    S = m // 2
    if s is None:
        s = s_for(model, m, d, log2B)
    K = d
    TPR = N + L - m * d
    CALLS = K + TPR
    if model == "FREE":
        o = 0.0
    elif model == "ENUM":
        o = (m - 1) * d
    elif model in ("MITM", "MITM_CAPPED"):
        o = (m - s) * d
    else:
        raise ValueError(model)
    PROBE = K + TPR + o
    FILL = s * d if (model in ("MITM", "MITM_CAPPED") and s >= 1) else 0.0
    LA = 2.0 * d
    TOTAL = log2sumexp2(PROBE, FILL, LA)
    return dict(n=n, m=m, d=d, model=model, log2B=log2B, s=s, S=S, N=N, L=L,
                K=K, TPR=TPR, CALLS=CALLS, o=o, PROBE=PROBE, FILL=FILL, LA=LA,
                TOTAL=TOTAL, out_of_domain=CALLS < 0,
                probe_only_v1_reference=log2sumexp2(PROBE, LA),
                VOW=vow(n), PUB=PUB_131 if n == 131 else None)


if __name__ == "__main__":
    print("r prime:", is_probable_prime(R_ECC2K130))
    print("log2 r =", math.log2(R_ECC2K130))
    print("log2(4r) - 131 =", math.log2(4 * R_ECC2K130) - 131)
    print("VOW(131) =", vow(131), " PUB-VOW =", PUB_131 - vow(131),
          " log2 sqrt(131) =", 0.5 * math.log2(131))
