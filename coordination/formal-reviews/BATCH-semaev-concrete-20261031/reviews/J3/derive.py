#!/usr/bin/env python3
"""Blind, dependency-free derivation from blind-input.yaml's literal parameters."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASIS = (9, 3, 2, 12)
def popcount(v):
    return bin(v).count('1')


LOW = tuple(m for m in range(256) if popcount(m) <= 2)
LOW3 = tuple(m for m in range(256) if popcount(m) <= 3)
MASK2 = sum(1 << m for m in LOW)
MASK3 = sum(1 << m for m in LOW3)


def fm(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        b >>= 1
        a <<= 1
        if a & 16:
            a ^= 0x13  # X^4 + X + 1
    return p


def xval(bits, offset):
    v = 0
    for i, b in enumerate(BASIS):
        if bits & (1 << (offset + i)):
            v ^= b
    return v


def component_anfs():
    vals = [0] * 256
    for bits in range(256):
        x1, x2 = xval(bits, 0), xval(bits, 4)
        pair = fm(x1, x2) ^ x1 ^ x2
        vals[bits] = fm(pair, pair) ^ fm(x1, x2) ^ 1
    assert set(vals) <= set(range(16))
    anfs = []
    for k in range(4):
        a = [(v >> k) & 1 for v in vals]
        for i in range(8):
            for mask in range(256):
                if mask & (1 << i):
                    a[mask] ^= a[mask ^ (1 << i)]
        support = [m for m, v in enumerate(a) if v]
        assert all(sum(a[m] for m in support if m & bits == m) % 2 == (vals[bits] >> k) & 1 for bits in range(256))
        anfs.append(support)
    return anfs


def rows_for(anfs, degree):
    rows = []
    allowed = MASK2 if degree == 2 else MASK3
    for k, support in enumerate(anfs):
        for mult in range(256):
            v = 0
            for mon in support:
                v ^= 1 << (mon | mult)
            if v & ~allowed == 0 and v:
                rows.append((k, mult, v))
    return rows


def echelon(rows):
    basis = {}
    for _, _, v in rows:
        t = v
        while t:
            p = t.bit_length() - 1
            if p not in basis:
                basis[p] = t
                break
            t ^= basis[p]
    return basis


def reduce(v, basis):
    t = v
    for p in sorted(basis, reverse=True):
        if t & (1 << p):
            t ^= basis[p]
    return t


def witness(rows3, basis2):
    high_basis = {}
    for index, (_, _, v) in enumerate(rows3):
        high = v & ~MASK2
        combo = 1 << index
        while high:
            p = high.bit_length() - 1
            if p not in high_basis:
                high_basis[p] = (high, combo)
                break
            h, c = high_basis[p]
            high ^= h
            combo ^= c
        if high == 0:
            low = 0
            for j in range(len(rows3)):
                if combo & (1 << j):
                    low ^= rows3[j][2]
            if low and low & ~MASK2 == 0 and reduce(low, basis2):
                return combo, low
    raise RuntimeError('No new low degree class')


def separator(rows2, witness_vector):
    coordinates = list(LOW)
    systems = []
    for _, _, v in rows2:
        systems.append((sum(((v >> m) & 1) << i for i, m in enumerate(coordinates)), 0))
    systems.append((sum(((witness_vector >> m) & 1) << i for i, m in enumerate(coordinates)), 1))
    pivots = {}
    for coeff, rhs in systems:
        while coeff:
            p = (coeff & -coeff).bit_length() - 1
            if p not in pivots:
                pivots[p] = (coeff, rhs)
                break
            c, b = pivots[p]
            coeff ^= c
            rhs ^= b
        if not coeff and rhs:
            raise RuntimeError('Witness lies in D2 span')
    sol = 0
    for p in sorted(pivots, reverse=True):
        coeff, rhs = pivots[p]
        if rhs ^ (popcount(coeff & sol) & 1):
            sol |= 1 << p
    result = sum(1 << m for i, m in enumerate(coordinates) if sol & (1 << i))
    assert all(popcount(v & result) % 2 == 0 for _, _, v in rows2)
    assert popcount(witness_vector & result) % 2 == 1
    return result


def hexvec(v):
    return f'0x{v:064x}'


def pack_rows(rows):
    return [{'component': k, 'multiplier_mask': m, 'vector_hex': hexvec(v),
             'support_masks': [i for i in range(256) if v >> i & 1]}
            for k, m, v in rows]


def write_json(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    anfs = component_anfs()
    rows2, rows3 = rows_for(anfs, 2), rows_for(anfs, 3)
    basis2, basis3 = echelon(rows2), echelon(rows3)
    combo, low = witness(rows3, basis2)
    sep = separator(rows2, low)
    chosen = [i for i in range(len(rows3)) if combo >> i & 1]
    # Find explicit duplicate outputs in one real multiplication.
    parity = None
    for k, mult, vec in rows3:
        grouped = {}
        for mon in anfs[k]:
            grouped.setdefault(mon | mult, []).append(mon)
        duplicates = [(out, inputs) for out, inputs in grouped.items() if len(inputs) >= 2]
        if duplicates:
            out, inputs = duplicates[0]
            parity = {'component': k, 'multiplier_mask': mult, 'output_mask': out,
                      'input_masks_mapping_to_output': inputs,
                      'raw_count': len(inputs), 'parity_coefficient': len(inputs) % 2,
                      'row_coefficient': (vec >> out) & 1}
            break
    mutated = [s[:] for s in anfs]
    mutation_mask = 1
    if mutation_mask in mutated[0]:
        mutated[0].remove(mutation_mask)
    else:
        mutated[0].append(mutation_mask)
        mutated[0].sort()
    mut2, mut3 = rows_for(mutated, 2), rows_for(mutated, 3)
    key = lambda rows: {(k, m): v for k, m, v in rows}
    orig2, orig3, mod2, mod3 = map(key, (rows2, rows3, mut2, mut3))
    row_changes = {}
    for d, original, modified in ((2, orig2, mod2), (3, orig3, mod3)):
        changed = [(k, m) for k, m in sorted(original.keys() | modified.keys())
                   if original.get((k, m)) != modified.get((k, m))]
        row_changes[str(d)] = {'changed_count': len(changed), 'examples': [
            {'component': k, 'multiplier_mask': m,
             'before_hex': hexvec(original[(k, m)]) if (k, m) in original else None,
             'after_hex': hexvec(modified[(k, m)]) if (k, m) in modified else None}
            for k, m in changed[:8]]}
    raw = {
        'field': 'F2[X]/(X^4+X+1)', 'basis': BASIS,
        'anf_support_masks': anfs,
        'anf_support_hex': [hexvec(sum(1 << m for m in s)) for s in anfs],
        'D2': {'row_count': len(rows2), 'rank': len(basis2), 'rows': pack_rows(rows2)},
        'D3': {'row_count': len(rows3), 'rank': len(basis3), 'rows': pack_rows(rows3)},
        'new_low_degree_class': {
            'vector_hex': hexvec(low), 'support_masks': [m for m in LOW if low >> m & 1],
            'D2_remainder_hex': hexvec(reduce(low, basis2)),
            'row_combination_indices': chosen,
            'row_combination': [pack_rows([rows3[i]])[0] for i in chosen],
            'separator_hex': hexvec(sep),
            'separator_support_masks': [m for m in LOW if sep >> m & 1],
            'separator_on_witness': popcount(sep & low) % 2,
            'separator_on_all_D2_rows': [popcount(sep & v) % 2 for _, _, v in rows2]},
        'parity_control': parity,
        'mutation_control': {'component': 0, 'flipped_monomial_mask': mutation_mask,
                             'D2_row_count': len(mut2), 'D2_rank': len(echelon(mut2)),
                             'D3_row_count': len(mut3), 'D3_rank': len(echelon(mut3)),
                             'row_changes': row_changes},
    }
    digest = write_json('raw.json', raw)
    print(json.dumps({'raw_sha256': digest, 'D2_rank': len(basis2), 'D3_rank': len(basis3),
                      'D2_rows': len(rows2), 'D3_rows': len(rows3),
                      'witness_rows': len(chosen), 'parity': parity,
                      'mutation_changes': row_changes}, indent=2))


if __name__ == '__main__':
    main()
