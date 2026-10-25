"""Curve-free permutation model of KN-FIND-bdcd60 (1) and (2), computed with Sage/GAP.

Points: sign vectors eps in {+-1}^n modulo global sign (n = m-1), 2^{n-1} of them.
Generators: coordinate sign flips and adjacent transpositions of coordinates.
Ordered base = image of the sign subgroup; symmetric base = image of everything.
Outputs orders, regularity, primitivity, block systems, the S_4 identification at
m = 4, and cycle-type class densities (the Chebotarev predictions used by the
symmetric-base measurements at m = 5 and m = 6, which no record has measured).
"""
import json, itertools, sys
from sage.all import PermutationGroup, SymmetricGroup, Integer

OUT = sys.argv[1] if len(sys.argv) > 1 else 'rt_groups_out.json'


def model(n):
    vecs = [v for v in itertools.product([1, -1], repeat=n) if v[0] == 1]
    idx = {v: i + 1 for i, v in enumerate(vecs)}

    def canon(v):
        return v if v[0] == 1 else tuple(-c for c in v)

    def perm_of(fn):
        return [idx[canon(fn(v))] for v in vecs]

    flips = [perm_of(lambda v, i=i: tuple(-c if j == i else c for j, c in enumerate(v))) for i in range(n)]

    def swap(v, i):
        w = list(v)
        w[i], w[i + 1] = w[i + 1], w[i]
        return tuple(w)

    swaps = [perm_of(lambda v, i=i: swap(v, i)) for i in range(n - 1)]
    return vecs, PermutationGroup(flips), PermutationGroup(flips + swaps)


def class_densities(G, npts):
    dens = {}
    order = G.order()
    for C in G.conjugacy_classes():
        ct = tuple(sorted(len(c) for c in C.representative().cycle_tuples(singletons=True)))
        dens[ct] = dens.get(ct, 0) + Integer(C.cardinality())
    return {str(list(k)): float(v / order) for k, v in sorted(dens.items())}


res = {}
for m in range(3, 8):
    n = m - 1
    vecs, Gord, Gsym = model(n)
    npts = len(vecs)
    e = {
        'm': m, 'n_points': npts,
        'ordered_order': int(Gord.order()),
        'ordered_is_abelian': bool(Gord.is_abelian()),
        'ordered_is_transitive': bool(Gord.is_transitive()),
        'ordered_is_regular': bool(Gord.is_transitive() and Gord.order() == npts),
        'ordered_elementary_abelian_2': bool(Gord.is_abelian() and all((g * g).is_one() for g in Gord.gens())),
        'symmetric_order': int(Gsym.order()),
        'symmetric_is_transitive': bool(Gsym.is_transitive()),
        'symmetric_is_primitive': bool(Gsym.is_primitive()),
        'symmetric_is_full_symmetric_group': bool(Gsym.order() == SymmetricGroup(npts).order()),
    }
    if m == 4:
        e['symmetric_isomorphic_S4'] = bool(Gsym.is_isomorphic(SymmetricGroup(4)))
    if not Gsym.is_primitive():
        blocks = Gsym.blocks_all()
        e['symmetric_block_systems_all_blocks_containing_1'] = [[int(x) for x in bl] for bl in blocks]
        e['symmetric_number_of_nontrivial_block_systems'] = len(blocks)
        mb = sorted(int(x) for x in min(blocks, key=len))
        par = sorted(i + 1 for i, v in enumerate(vecs) if sum(1 for c in v if c == -1) % 2 == 0)
        e['minimal_block_is_even_minus_parity_class'] = (mb == par)
        e['minimal_block_size'] = len(mb)
    e['symmetric_cycle_type_densities'] = class_densities(Gsym, npts)
    e['ordered_cycle_type_densities'] = class_densities(Gord, npts)
    res[m] = e
    print(f"m={m}: pts={npts} ordered |G|={e['ordered_order']} regular={e['ordered_is_regular']} "
          f"elem-ab-2={e['ordered_elementary_abelian_2']} | symmetric |G|={e['symmetric_order']} "
          f"primitive={e['symmetric_is_primitive']} fullSym={e['symmetric_is_full_symmetric_group']}"
          + (f" isoS4={e['symmetric_isomorphic_S4']}" if m == 4 else '')
          + (f" blocksystems={e['symmetric_number_of_nontrivial_block_systems']} minblock=parity:{e['minimal_block_is_even_minus_parity_class']} size={e['minimal_block_size']}"
             if not e['symmetric_is_primitive'] else ''))

json.dump(res, open(OUT, 'w'), indent=1)
print('wrote', OUT)
