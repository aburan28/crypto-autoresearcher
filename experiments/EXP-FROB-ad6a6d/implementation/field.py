"""Arithmetic in F_7[z]/(z^3 + z + 1).

The modulus is the one named by IDEA-20261006-922612: a root alpha
satisfies alpha^3 + alpha + 1 = 0. This module does not enumerate
curve points and does not compute a slope image.
"""

from __future__ import annotations

P = 7
ORDER = P ** 3  # 343

# z^3 = -z - 1 = 6 + 6z in F_7.
_Z3 = (6, 6, 0)  # 6 + 6z + 0 z^2


def _mod_p(value: int) -> int:
    return value % P


def norm(element: tuple[int, int, int]) -> tuple[int, int, int]:
    return (_mod_p(element[0]), _mod_p(element[1]), _mod_p(element[2]))


def encode(element: tuple[int, int, int]) -> int:
    a0, a1, a2 = norm(element)
    return a0 + P * a1 + (P * P) * a2


def decode(value: int) -> tuple[int, int, int]:
    value %= ORDER
    return (value % P, (value // P) % P, (value // (P * P)) % P)


def add(left: tuple[int, int, int], right: tuple[int, int, int]) -> tuple[int, int, int]:
    return norm((left[0] + right[0], left[1] + right[1], left[2] + right[2]))


def sub(left: tuple[int, int, int], right: tuple[int, int, int]) -> tuple[int, int, int]:
    return norm((left[0] - right[0], left[1] - right[1], left[2] - right[2]))


def neg(element: tuple[int, int, int]) -> tuple[int, int, int]:
    return norm((-element[0], -element[1], -element[2]))


def mul(left: tuple[int, int, int], right: tuple[int, int, int]) -> tuple[int, int, int]:
    """Schoolbook product reduced by z^3 = 6 + 6z and z^4 = 6z + 6z^2."""
    coeff = [0] * 5
    for i in range(3):
        for j in range(3):
            coeff[i + j] = _mod_p(coeff[i + j] + left[i] * right[j])
    # c3 * z^3 contributes 6*c3 to the constant and to z.
    # c4 * z^4 contributes 6*c4 to z and to z^2.
    return (
        _mod_p(coeff[0] + 6 * coeff[3]),
        _mod_p(coeff[1] + 6 * coeff[3] + 6 * coeff[4]),
        _mod_p(coeff[2] + 6 * coeff[4]),
    )


def pow_elem(element: tuple[int, int, int], exponent: int) -> tuple[int, int, int]:
    result = (1, 0, 0)
    base = norm(element)
    exp = exponent
    while exp:
        if exp & 1:
            result = mul(result, base)
        base = mul(base, base)
        exp >>= 1
    return result


def inv_fermat(element: tuple[int, int, int]) -> tuple[int, int, int]:
    if element == (0, 0, 0):
        raise ZeroDivisionError("fermat inverse of zero")
    return pow_elem(element, ORDER - 2)


def _trim(poly: list[int]) -> list[int]:
    trimmed = [_mod_p(c) for c in poly]
    while len(trimmed) > 1 and trimmed[-1] == 0:
        trimmed.pop()
    if not trimmed:
        return [0]
    return trimmed


def _poly_mul(left: list[int], right: list[int]) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = _mod_p(out[i + j] + a * b)
    return _trim(out)


def _poly_sub(left: list[int], right: list[int]) -> list[int]:
    width = max(len(left), len(right))
    out = [0] * width
    for i in range(width):
        a = left[i] if i < len(left) else 0
        b = right[i] if i < len(right) else 0
        out[i] = _mod_p(a - b)
    return _trim(out)


def _poly_divmod(numer: list[int], denom: list[int]) -> tuple[list[int], list[int]]:
    numer = _trim(numer)
    denom = _trim(denom)
    if denom == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    lead_inv = pow(denom[-1], P - 2, P)
    quotient = [0] * max(1, len(numer) - len(denom) + 1)
    remainder = numer[:]
    while remainder != [0] and len(remainder) >= len(denom):
        coef = _mod_p(remainder[-1] * lead_inv)
        shift = len(remainder) - len(denom)
        if shift >= len(quotient):
            quotient.extend([0] * (shift + 1 - len(quotient)))
        quotient[shift] = coef
        for index, term in enumerate(denom):
            remainder[index + shift] = _mod_p(remainder[index + shift] - coef * term)
        remainder = _trim(remainder)
    return _trim(quotient), remainder


def inv_egcd(element: tuple[int, int, int]) -> tuple[int, int, int]:
    """Inverse via the extended Euclidean algorithm on z^3 + z + 1."""
    if element == (0, 0, 0):
        raise ZeroDivisionError("egcd inverse of zero")
    modulus = [1, 1, 0, 1]
    other = _trim(list(element))
    s_prev, s_curr = [1], [0]
    t_prev, t_curr = [0], [1]
    r_prev, r_curr = modulus, other
    while r_curr != [0]:
        quotient, remainder = _poly_divmod(r_prev, r_curr)
        r_prev, r_curr = r_curr, remainder
        s_prev, s_curr = s_curr, _poly_sub(s_prev, _poly_mul(quotient, s_curr))
        t_prev, t_curr = t_curr, _poly_sub(t_prev, _poly_mul(quotient, t_curr))
    gcd = _trim(r_prev)
    if len(gcd) != 1 or gcd[0] == 0:
        raise ZeroDivisionError("element is not invertible")
    scale = pow(gcd[0], P - 2, P)
    bezout = _trim([_mod_p(c * scale) for c in t_prev])
    _, reduced = _poly_divmod(bezout, modulus)
    while len(reduced) < 3:
        reduced.append(0)
    return (reduced[0], reduced[1], reduced[2])


def is_base_field(element: tuple[int, int, int]) -> bool:
    return element[1] == 0 and element[2] == 0


def poly_cube_plus_linear_plus_one(value: int) -> int:
    """t^3 + t + 1 in the prime field F_7."""
    return _mod_p(value * value * value + value + 1)
