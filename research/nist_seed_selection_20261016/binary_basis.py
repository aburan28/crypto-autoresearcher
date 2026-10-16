#!/usr/bin/env python3
"""FIPS 186-2 Appendix 6.9 Gaussian-normal to polynomial basis conversion.

The constants are the top rows of the conversion matrices in Appendix 6.9,
also reproduced by NIST SP 800-186 Appendix G.3.3.  Bit strings are read
from most significant bit to least significant bit.
"""

from functools import lru_cache


TOP_ROWS = {
    233: "1499e398ac5d79e368559b35ca49bb7305da6c0390bcf9e2300253203c9",
    283: "31e0ed791c3282dc5624a720818049d053e8c7ab8663792bc1d792eba9867fc7b317a99",
    409: "0dfa06be206aa97b7a41fffb9b0c55f8f048062fbe8381b4248adf92912ccc8e3f91a24e1cfb3950532b988971c23042e85708d",
    571: "452186bbf5840a0bcf8c9f02a54efa04e813b43c3d4149606c4d27b487bf107393c8907f79d9778beb35ee87467d3288274caebda6ce05aeb4ca5cf3c3044bd4372232f2c1a27c4",
}


def square_mod(value: int, polynomial: int, degree: int) -> int:
    squared = 0
    while value:
        low = value & -value
        squared ^= 1 << (2 * (low.bit_length() - 1))
        value ^= low
    while squared.bit_length() > degree:
        squared ^= polynomial << (squared.bit_length() - degree - 1)
    return squared


@lru_cache(maxsize=None)
def conversion_rows(degree: int, polynomial: int) -> tuple[int, ...]:
    first = int(TOP_ROWS[degree], 16)
    if first.bit_length() > degree or polynomial.bit_length() != degree + 1:
        raise ValueError("invalid conversion basis parameters")
    rows = [first]
    for _ in range(degree - 1):
        rows.append(square_mod(rows[-1], polynomial, degree))
    if square_mod(rows[-1], polynomial, degree) != first:
        raise ArithmeticError("normal basis cycle does not close")
    return tuple(rows)


def normal_to_polynomial(bits: int, degree: int, polynomial: int) -> int:
    if bits < 0 or bits.bit_length() > degree:
        raise ValueError("normal element outside field width")
    result = 0
    for position, row in enumerate(conversion_rows(degree, polynomial)):
        if bits & (1 << (degree - position - 1)):
            result ^= row
    return result
