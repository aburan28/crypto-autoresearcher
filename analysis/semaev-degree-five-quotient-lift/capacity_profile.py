#!/usr/bin/env python3
"""Derive quotient-lift coordinate counts from retained certificates.

No closure is run and no LFD claim is inferred. Outputs are write-once.
"""
import argparse
import datetime
import hashlib
import itertools
import json
import math
import mmap
from pathlib import Path
import struct


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def border_count(n, d, representatives):
    free = set(representatives)
    count = 0
    for c in itertools.combinations(range(n), d + 1):
        mask = sum(1 << j for j in c)
        if all((mask ^ (1 << j)) in free for j in c):
            count += 1
    return count


def border_reference(n, d, representatives):
    # Independent enumeration direction: extend each free degree-d monomial,
    # deduplicate candidates, then test every deletion. No full (d+1)-universe
    # enumeration is shared with border_count.
    free = set(representatives)
    candidates = set()
    for m in free:
        if bin(m).count('1') == d:
            for j in range(n):
                if not m & (1 << j):
                    candidates.add(m | (1 << j))
    return sum(all((m ^ (1 << j)) in free for j in range(n) if m & (1 << j))
               for m in candidates)


def profile(path, expected):
    if digest(path) != expected:
        raise ValueError('seed certificate hash mismatch')
    with open(path, 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
        n, d, columns, nq = struct.unpack_from('<4q', data)
        if not (1 <= d < n <= 63 and 0 < nq <= columns):
            raise ValueError('invalid header')
        width = 8 * max(1, (nq + 63) // 64)
        offset = 32 + 8 * columns
        if columns != sum(math.comb(n, k) for k in range(d + 1)) or len(data) != offset + columns * width:
            raise ValueError('invalid certificate length or universe size')
        masks = struct.unpack_from('<' + str(columns) + 'Q', data, 32)
        if len(set(masks)) != columns or any(m >= 1 << n or bin(m).count('1') > d for m in masks):
            raise ValueError('invalid monomial universe')
        if list(masks) != sorted(masks, key=lambda m: (-bin(m).count('1'), m)):
            raise ValueError('unsupported monomial order')
        representatives = [None] * nq
        for j, m in enumerate(masks):
            value = int.from_bytes(data[offset + j*width:offset + (j+1)*width], 'little')
            if value >> nq:
                raise ValueError('coordinate outside declared codomain')
            if value and not value & (value - 1):
                representatives[value.bit_length() - 1] = m
        if any(m is None for m in representatives):
            raise ValueError('missing unit representative')
        coords = {m: q for q, m in enumerate(representatives)}
        allowed = 0
        for j in range(columns - 1, -1, -1):
            m = masks[j]
            value = int.from_bytes(data[offset + j*width:offset + (j+1)*width], 'little')
            if m in coords:
                if value != 1 << coords[m]:
                    raise ValueError('nonunit representative')
                allowed |= value
            elif value & ~allowed:
                raise ValueError('seed rewriting is not triangular')
    border = border_count(n, d, representatives)
    reference = border_reference(n, d, representatives)
    if border != reference:
        raise ValueError('independent enumeration mismatch')
    work = nq + border
    next_columns = sum(math.comb(n, k) for k in range(d + 2))
    stride = 8 * ((work + 63) // 64)
    return dict(seed_sha256=expected, variables=n, seed_degree=d, seed_columns=columns,
        seed_codimension=nq, border_coordinates=border, working_coordinates=work,
        reference_border_coordinates=reference, reference_working_coordinates=nq+reference,
        next_degree_columns=next_columns, seed_triangular=True,
        provisional_map_payload_bytes=next_columns*stride,
        relation_basis_payload_ceiling_bytes=work*stride,
        note='Derived bit payloads only, not measured RSS or a certified native admission limit; export maps, indices, checker, allocator and workspace add memory. Seed C1-C3 acceptance comes from the prior replay receipts.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    plan = json.loads(args.plan.read_text())
    for item in plan['items']:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            value = profile(args.data/item['id']/'attempt-001/certificate.bin', item['expected_sha256'])
            value.update(status='completed')
        except Exception as error:
            value = dict(status='failed', error=str(error))
        value.update(id=item['id'], started_at=started, plan_sha256=digest(args.plan),
                     source_sha256=digest(Path(__file__)), wall_valid=False,
                     scope='Deterministic structural analysis of existing accepted certificate; no new closure run.')
        with open(args.out/(item['id']+'.json'), 'x') as f:
            json.dump(value, f, indent=2, sort_keys=True); f.write('\n')
        print(json.dumps({k:value[k] for k in ('id','status')}), flush=True)


if __name__ == '__main__':
    main()
