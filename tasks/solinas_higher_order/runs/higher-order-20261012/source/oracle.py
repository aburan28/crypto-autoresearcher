"""Separate Python integer EC and SHA-counter implementations for verification.

Affine oracle adapted from the previous immutable generator-cohort verifier.
"""
import hashlib


def add(curve, left, right):
    if left is None: return right
    if right is None: return left
    p, a = curve['p'], curve['A']
    x, y = left; u, v = right
    if x == u and (y+v) % p == 0: return None
    slope = ((3*x*x+a)*pow(2*y, -1, p) if left == right else (v-y)*pow(u-x, -1, p)) % p
    rx = (slope*slope-x-u) % p
    return (rx, (slope*(x-rx)-y) % p)


def multiply(curve, point, scalar):
    result = None
    while scalar:
        if scalar & 1: result = add(curve, result, point)
        point = add(curve, point, point); scalar >>= 1
    return result


def scalar_draw(seed, limit, counter=0):
    bits = limit.bit_length(); width = (bits+7)//8
    while True:
        block = bytearray(hashlib.sha256(seed+counter.to_bytes(8, 'big')).digest()[:width]); counter += 1
        block[0] &= 0xff >> (8*width-bits)
        value = int.from_bytes(block, 'big')
        if 0 < value < limit: return value, counter


def sqrt_mod(value, p):
    """Deterministic Tonelli-Shanks; None for nonsquares; canonical smaller root."""
    value %= p
    if value == 0: return 0
    if pow(value, (p-1)//2, p) != 1: return None
    if p % 4 == 3:
        root = pow(value, (p+1)//4, p)
        return min(root, p-root)
    q, s = p-1, 0
    while not q & 1: q >>= 1; s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    c, root, t, m = pow(z, q, p), pow(value, (q+1)//2, p), pow(value, q, p), s
    while t != 1:
        i, temp = 1, t*t % p
        while temp != 1:
            temp = temp*temp % p; i += 1
        b = pow(c, 1 << (m-i-1), p)
        root, t, c, m = root*b % p, t*b*b % p, b*b % p, i
    return min(root, p-root)
