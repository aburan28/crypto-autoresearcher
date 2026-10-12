#!/usr/bin/env python3
"""
msparse.py -- from-scratch parser for the msolve-format Boolean systems of TASK-20261004-095926.

Format (as stated on the card): line 1 = variable names, comma separated, in order (x_1 first);
line 2 = characteristic (2); then polynomials separated by commas (the last has no trailing comma;
a trailing comma is tolerated).  '+' is sum, '*' is product (binds tighter than '+'), '1' is the
constant, 'v^e' is a power (only e=2 occurs in the files; e>=1 is read as idempotent in B).

Two representations are produced:
  * B-representation   : a polynomial is a set (python frozenset) of square-free monomials, a
                         monomial is an int bitmask (bit j-1 set iff x_j occurs).  v^e -> v (e>=1).
  * raw exponent form  : a polynomial is a dict {tuple(sorted (var,exp) pairs): coeff mod 2}; used to
                         check that the B-representation and a direct F_2-point evaluation agree.

The parser keeps every polynomial exactly as written, including field-equation lines x^2+x (which
are the zero polynomial in B); `parse_ms(..., drop_field_lines=...)` reports both counts.
"""
import sys, hashlib, re


def parse_term_raw(term, idx):
    """term: product of factors joined by '*'. returns (exponent-tuple, coeff) or None for 0."""
    expo = {}
    const = 1
    for fac in term.split('*'):
        fac = fac.strip()
        if fac == '':
            raise ValueError('empty factor in term %r' % term)
        if fac == '1':
            continue
        if fac == '0':
            return None
        if '^' in fac:
            v, e = fac.split('^')
            e = int(e)
        else:
            v, e = fac, 1
        if v not in idx:
            raise ValueError('unknown variable %r' % v)
        if e < 0:
            raise ValueError('negative exponent')
        if e == 0:
            continue
        expo[idx[v]] = expo.get(idx[v], 0) + e
    return tuple(sorted(expo.items()))


def parse_poly_raw(s, idx):
    """returns dict exponent-tuple -> 1 (coefficients mod 2; repeated terms cancel)."""
    s = s.strip()
    out = {}
    if s == '':
        return out
    for term in s.split('+'):
        term = term.strip()
        if term == '':
            raise ValueError('empty term in %r' % s[:60])
        m = parse_term_raw(term, idx)
        if m is None:
            continue
        if m in out:
            del out[m]
        else:
            out[m] = 1
    return out


def raw_to_B(raw):
    """reduce an exponent-form polynomial into the Boolean ring: exponents >=1 become 1."""
    res = set()
    for expo in raw:
        mask = 0
        for v, e in expo:
            if e >= 1:
                mask |= 1 << v
        res ^= {mask}
    return frozenset(res)


def read_ms(path):
    data = open(path, 'rb').read()
    txt = data.decode('ascii')
    lines = txt.split('\n')
    names = [x.strip() for x in lines[0].split(',')]
    char = int(lines[1].strip())
    body = ''.join(l.strip() for l in lines[2:])
    parts = body.split(',')
    empty_tail = 0
    while parts and parts[-1] == '':
        parts.pop()
        empty_tail += 1
    return names, char, parts, empty_tail, hashlib.sha256(data).hexdigest()


def is_field_poly_raw(raw, nvars):
    """True iff raw == x_i^2 + x_i for one variable i (as written)."""
    if len(raw) != 2:
        return False
    ks = sorted(raw.keys())
    d = {k: 1 for k in ks}
    for v in range(nvars):
        if ((v, 2),) in d and ((v, 1),) in d:
            return True
    return False


def parse_ms(path, drop_field_lines=True):
    names, char, parts, empty_tail, sha = read_ms(path)
    idx = {n: i for i, n in enumerate(names)}
    assert char == 2, 'characteristic %d' % char
    assert len(idx) == len(names)
    raws = [parse_poly_raw(p, idx) for p in parts]
    N = len(names)
    flags = [is_field_poly_raw(r, N) for r in raws]
    polysB = [raw_to_B(r) for r in raws]
    info = dict(path=path, sha256=sha, N=N, names=names, n_polys_total=len(parts),
                n_field_lines=sum(flags), n_nonfield=len(parts) - sum(flags),
                n_empty_tail=empty_tail,
                n_B_zero=sum(1 for p in polysB if len(p) == 0))
    if drop_field_lines:
        keepB = [p for p, fl in zip(polysB, flags) if not fl]
        keepR = [r for r, fl in zip(raws, flags) if not fl]
    else:
        keepB, keepR = polysB, raws
    return N, keepB, keepR, info


def deg(poly):
    return max((bin(m).count('1') for m in poly), default=-1)


def eval_B(poly, a):
    """a: int bitmask of the point (bit j-1 = value of x_j).  evaluates the B-polynomial."""
    s = 0
    for m in poly:
        if (m & a) == m:
            s ^= 1
    return s


def eval_raw(raw, a):
    """direct evaluation from the exponent form (x^e with e>=1 equals x on F_2, x^0 = 1)."""
    s = 0
    for expo in raw:
        t = 1
        for v, e in expo:
            if e >= 1 and not ((a >> v) & 1):
                t = 0
                break
        s ^= t
    return s


def monomial_str(m):
    return '*'.join('x%d' % (j + 1) for j in range(m.bit_length()) if (m >> j) & 1) or '1'


if __name__ == '__main__':
    N, B, R, info = parse_ms(sys.argv[1])
    print(info['N'], info['n_nonfield'], info['n_field_lines'], [deg(p) for p in B][:5])
