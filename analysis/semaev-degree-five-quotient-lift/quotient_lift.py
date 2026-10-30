#!/usr/bin/env python3
"""Small-instance reference implementation of certified quotient lifting.

This is not the frontier runner. It bounds N before allocating monomial maps.
A seed is an onto triangular monomial map with a closed kernel containing F.
The caller must independently check both seed and output before any LFD claim.
"""
from collections import deque
from itertools import combinations
import struct


def degree(mask):
    return bin(mask).count('1')


def monomials(n, d):
    return sorted((sum(1 << j for j in c) for k in range(min(n, d) + 1)
                   for c in combinations(range(n), k)), key=lambda m: (-degree(m), m))


def bits(value):
    while value:
        b = value & -value
        yield b.bit_length() - 1
        value ^= b


def xor_images(value, images):
    out = 0
    for j in bits(value):
        out ^= images[j]
    return out


def seed_representatives(n, d, rows, nq):
    order = monomials(n, d)
    if set(rows) != set(order) or nq < 0:
        raise ValueError('seed monomial universe or dimension is invalid')
    representatives = [None] * nq
    for m in order:
        v = rows[m]
        if v < 0 or v >> nq:
            raise ValueError('seed coordinate outside codomain')
        if v and not (v & (v - 1)):
            representatives[v.bit_length() - 1] = m
    if any(m is None for m in representatives):
        raise ValueError('seed lacks unit monomial representatives')
    position = {m: j for j, m in enumerate(order)}
    # Choosing the last unit representative makes rewriting triangular, or
    # rejects the seed. Surjectivity alone does not guarantee this property.
    for m in order:
        if m in representatives:
            continue
        if any(position[representatives[q]] <= position[m] for q in bits(rows[m])):
            raise ValueError('seed is not triangular in the declared order')
    return representatives


def lift(n, d, rows, nq, *, max_variables=12):
    """Return an onto degree-(d+1) map and construction counters.

    Its kernel is the smallest closed superspace of the seed kernel at the
    new degree, assuming the seed hypotheses. A killed constant is labelled
    projection_kills_one, since seed equality with W_d is not assumed.
    """
    if not 1 <= d < n or n > max_variables:
        raise ValueError('reference implementation requires 1 <= d < N <= max_variables')
    representatives = seed_representatives(n, d, rows, nq)
    rep_set = set(representatives)
    high = [m for m in monomials(n, d + 1) if degree(m) == d + 1]
    rewrite = {}
    standard = []
    for m in high:
        options = [(m ^ (1 << x), x) for x in bits(m) if (m ^ (1 << x)) not in rep_set]
        if options:
            rewrite[m] = min(options)
        else:
            standard.append(m)
    nhigh = len(standard)
    coordinates = standard + representatives
    nf = {m: v << nhigh for m, v in rows.items()}
    for q, m in enumerate(standard):
        nf[m] = 1 << q
    # Replacing a degree-d leading term by a later same/lower-degree term,
    # and multiplying by its missing variable, strictly decreases the order.
    for m in reversed(high):
        if m not in rewrite:
            continue
        divisor, x = rewrite[m]
        value = 0
        for q in bits(rows[divisor]):
            target = representatives[q] | (1 << x)
            if target not in nf:
                raise ValueError('non-triangular degree extension')
            value ^= nf[target]
        nf[m] = value

    pivots = {}
    pending = deque()
    inserted = 0
    relations = 0

    def insert(value):
        nonlocal inserted
        while value:
            lead = (value & -value).bit_length() - 1
            if lead in pivots:
                value ^= pivots[lead]
            else:
                pivots[lead] = value
                inserted += 1
                if lead >= nhigh:
                    pending.append(value)
                break

    # Every m + seed(m), multiplied by every variable. Even seed low rows
    # are retained here so a future optimization cannot silently skip a gate.
    for m in monomials(n, d):
        if m in rep_set:
            continue
        for x in range(n):
            value = nf[m | (1 << x)]
            for q in bits(rows[m]):
                value ^= nf[representatives[q] | (1 << x)]
            insert(value)
            relations += 1
    propagated = 0
    while pending:
        value = pending.popleft()
        for x in range(n):
            product = 0
            for q in bits(value):
                product ^= nf[coordinates[q] | (1 << x)]
            insert(product)
            propagated += 1

    free = [q for q in range(len(coordinates)) if q not in pivots]
    quotient = [0] * len(coordinates)
    for q, c in enumerate(free):
        quotient[c] = 1 << q
    for lead in sorted(pivots, reverse=True):
        quotient[lead] = xor_images(pivots[lead] ^ (1 << lead), quotient)
    output = {m: xor_images(v, quotient) for m, v in nf.items()}
    return output, len(free), dict(seed_dimension=nq, border_coordinates=nhigh,
        working_coordinates=len(coordinates), relation_rank=inserted,
        seed_products=relations, propagated_products=propagated,
        status='candidate_certificate' if output[0] else 'projection_kills_one')


def write_certificate(path, n, d, rows, nq):
    order = monomials(n, d)
    if set(order) != set(rows):
        raise ValueError('wrong monomial universe')
    width = 8 * max(1, (nq + 63) // 64)
    with open(path, 'xb') as out:
        out.write(struct.pack('<4q', n, d, len(order), nq))
        out.write(struct.pack('<' + str(len(order)) + 'Q', *order))
        for m in order:
            out.write(rows[m].to_bytes(width, 'little'))
