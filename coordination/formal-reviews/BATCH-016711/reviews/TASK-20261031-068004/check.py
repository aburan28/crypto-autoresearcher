#!/usr/bin/env python3
"""Independent F16 Boolean ANF and compatible-row derivation."""
import json
from collections import defaultdict

BASIS = (9, 3, 2, 12)


def mul(a, b):
    out = 0
    for i in range(4):
        if (b >> i) & 1:
            out ^= a << i
    for i in range(6, 3, -1):
        if (out >> i) & 1:
            out ^= 0b10011 << (i - 4)
    return out


def sq(a):
    return mul(a, a)


def degree(mask):
    return bin(mask).count("1")


def masks_to_int(masks):
    out = 0
    for m in masks:
        out ^= 1 << m
    return out


def support(v):
    return [i for i in range(256) if (v >> i) & 1]


def bit_indices(v):
    out = []
    while v:
        low = v & -v
        out.append(low.bit_length() - 1)
        v ^= low
    return out


def anf_components():
    truth = [[0] * 256 for _ in range(4)]
    for bits in range(256):
        x1 = 0
        x2 = 0
        for i, b in enumerate(BASIS):
            if (bits >> i) & 1:
                x1 ^= b
            if (bits >> (i + 4)) & 1:
                x2 ^= b
        p = mul(x1, x2) ^ x1 ^ x2
        value = sq(p) ^ mul(x1, x2) ^ 1
        for c in range(4):
            truth[c][bits] = (value >> c) & 1
    originals = [list(t) for t in truth]
    for c in range(4):
        for i in range(8):
            for mask in range(256):
                if (mask >> i) & 1:
                    truth[c][mask] ^= truth[c][mask ^ (1 << i)]
    anfs = [masks_to_int(i for i, x in enumerate(t) if x) for t in truth]
    for c in range(4):
        for bits in range(256):
            assert originals[c][bits] == (sum(1 for m in support(anfs[c]) if (m & bits) == m) & 1)
    return anfs


def product(row, multiplier):
    return masks_to_int(m | multiplier for m in support(row))


def echelon_add(basis, vector, provenance=0):
    while vector:
        pivot = vector.bit_length() - 1
        if pivot in basis:
            old_v, old_p = basis[pivot]
            vector ^= old_v
            provenance ^= old_p
        else:
            basis[pivot] = (vector, provenance)
            return True, vector, provenance
    return False, 0, provenance


def compatible(components, D):
    rows = []
    for c, f in enumerate(components):
        for m in range(256):
            v = product(f, m)
            if all(degree(j) <= D for j in support(v)):
                rows.append((c, m, v))
    return rows


def rank(rows):
    basis = {}
    for _, _, v in rows:
        echelon_add(basis, v)
    return len(basis), basis


def row_labels(indices, rows):
    return [{"component": rows[i][0], "multiplier_mask": rows[i][1]} for i in indices]


def solve_separator(d2_rows, witness, low_masks):
    # A functional is a subset of low coordinates. Solve A lambda = b.
    equations = []
    for _, _, v in d2_rows:
        coeff = sum(((v >> m) & 1) << i for i, m in enumerate(low_masks))
        equations.append((coeff, 0))
    coeff = sum(((witness >> m) & 1) << i for i, m in enumerate(low_masks))
    equations.append((coeff, 1))
    pivots = {}
    for coeff, rhs in equations:
        while coeff:
            p = coeff.bit_length() - 1
            if p in pivots:
                coeff ^= pivots[p][0]
                rhs ^= pivots[p][1]
            else:
                pivots[p] = (coeff, rhs)
                break
        else:
            if rhs:
                raise AssertionError("No separator")
    sol = 0
    for p in sorted(pivots):
        coeff, rhs = pivots[p]
        rhs ^= degree(coeff & sol) & 1
        if rhs:
            sol |= 1 << p
    selected = [m for i, m in enumerate(low_masks) if (sol >> i) & 1]
    assert all(degree(v & masks_to_int(selected)) % 2 == 0 for _, _, v in d2_rows)
    assert degree(witness & masks_to_int(selected)) % 2 == 1
    return selected


def analyze(components):
    low_masks = [m for m in range(256) if degree(m) <= 2]
    low_projection = masks_to_int(low_masks)
    d2 = compatible(components, 2)
    d3 = compatible(components, 3)
    r2, b2 = rank(d2)
    r3, _ = rank(d3)
    high_elim = {}
    low_basis = {}
    witness = None
    for i, (_, _, v) in enumerate(d3):
        hi = v & ~low_projection
        _, rem, prov = echelon_add(high_elim, hi, 1 << i)
        if rem == 0:
            combo = prov
            low = 0
            for j in bit_indices(combo):
                low ^= d3[j][2]
            assert low & ~low_projection == 0
            echelon_add(low_basis, low)
            if witness is None and echelon_add(dict(b2), low)[0]:
                witness = (low, combo)
    out = {
        "component_anf_masks": [support(f) for f in components],
        "D2_rows": [{"component": c, "multiplier_mask": m, "output_support": support(v), "output_hex": hex(v)} for c, m, v in d2],
        "D3_rows": [{"component": c, "multiplier_mask": m, "output_support": support(v), "output_hex": hex(v)} for c, m, v in d3],
        "D2": {"compatible_count": len(d2), "per_component": [sum(c == j for c, _, _ in d2) for j in range(4)], "rank": r2},
        "D3": {"compatible_count": len(d3), "per_component": [sum(c == j for c, _, _ in d3) for j in range(4)], "rank": r3,
               "high_projection_rank": len(high_elim), "low_intersection_rank": len(low_basis)},
        "new_class_exists": witness is not None,
    }
    if witness:
        low, combo = witness
        indices = bit_indices(combo)
        sep = solve_separator(d2, low, low_masks)
        out["witness"] = {"D3_row_indices": indices, "rows": row_labels(indices, d3),
                          "sum_support": support(low), "sum_hex": hex(low),
                          "separator_support": sep, "separator_on_witness": 1,
                          "separator_on_D2_rows_values": [(degree(v & masks_to_int(sep)) & 1) for _, _, v in d2]}
    # Find duplicate monomial in one raw Boolean product and expose its parity.
    for c, f in enumerate(components):
        for m in range(256):
            groups = defaultdict(list)
            for mon in support(f):
                groups[mon | m].append(mon)
            duplicate = next(((outmon, terms) for outmon, terms in groups.items() if len(terms) >= 2 and len(terms) % 2 == 0), None)
            if duplicate:
                outmon, terms = duplicate
                out["xor_parity_control"] = {"component": c, "multiplier_mask": m,
                    "output_mask": outmon, "input_masks": terms,
                    "multiplicity": len(terms), "output_coefficient": (product(f, m) >> outmon) & 1}
                return out
    raise AssertionError("No duplicate parity example")


def main():
    components = anf_components()
    base = analyze(components)
    # Mutate the first component by toggling Boolean monomial mask 1.
    changed = list(components)
    changed[0] ^= 1 << 1
    mutated = analyze(changed)
    base_d2 = {(r["component"], r["multiplier_mask"]) for r in base["D2_rows"]}
    base_d3 = {(r["component"], r["multiplier_mask"]) for r in base["D3_rows"]}
    mut_d2 = {(r["component"], r["multiplier_mask"]) for r in mutated["D2_rows"]}
    mut_d3 = {(r["component"], r["multiplier_mask"]) for r in mutated["D3_rows"]}
    result = {"field_modulus": "X^4+X+1", "basis": BASIS,
              "component_order": "low polynomial coefficient bit first",
              "base": base,
              "mutation": {"component": 0, "toggled_anf_mask": 1,
                           "mutated_anf_masks": mutated["component_anf_masks"],
                           "D2": mutated["D2"], "D3": mutated["D3"],
                           "D2_added_keys": sorted(mut_d2 - base_d2), "D2_removed_keys": sorted(base_d2 - mut_d2),
                           "D3_added_keys": sorted(mut_d3 - base_d3), "D3_removed_keys": sorted(base_d3 - mut_d3),
                           "D2_rows": mutated["D2_rows"], "D3_rows": mutated["D3_rows"],
                           "new_class_exists": mutated["new_class_exists"],
                           "witness": mutated.get("witness")}}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
