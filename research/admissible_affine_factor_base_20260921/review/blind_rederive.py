#!/usr/bin/env python3
"""Permanent-blind, coordinate-only N19 geometry and coverage derivation.

This program reads the frozen public pool, protocol/amendment and neutral
selected coordinates. It imports no experiment code or reports, launches no
solver, and creates no scientific timing sample.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import resource
import time
from collections import defaultdict
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'research/admissible_affine_factor_base_20260921'
READS = []
MOD = 524327
MASK = (1 << 19) - 1
R = 262543


def load(rel):
    path = P / rel
    READS.append(str(path.relative_to(ROOT)))
    b = path.read_bytes()
    return json.loads(b), hashlib.sha256(b).hexdigest()


def mul(a, b):
    z = 0
    while b:
        if b & 1:
            z ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 19):
            a ^= MOD
    return z


def square(a):
    return mul(a, a)


def power(a, k):
    out = 1
    while k:
        if k & 1:
            out = mul(out, a)
        a = square(a)
        k >>= 1
    return out


def schoolbook(a,b):
    """Independent unreduced carryless polynomial product and long division."""
    z=0
    for j in range(19):
        if b >> j & 1:
            z ^= a << j
    while z.bit_length() > 19:
        z ^= MOD << (z.bit_length() - 20)
    return z


def alt_inv(a):
    assert a
    z,base,k=1,a,(1<<19)-2
    while k:
        if k&1:
            z=schoolbook(z,base)
        base=schoolbook(base,base)
        k>>=1
    return z


@cache
def inv(a):
    assert 0 < a <= MASK
    u, v = a, MOD
    g, h = 1, 0
    while u != 1:
        if not u:
            raise AssertionError('reducible modulus or zero input')
        j = u.bit_length() - v.bit_length()
        if j < 0:
            u, v = v, u
            g, h = h, g
            j = -j
        u ^= v << j
        g ^= h << j
    while g.bit_length() > 19:
        g ^= MOD << (g.bit_length() - 20)
    assert mul(a, g) == 1
    return g


def neg(p):
    return None if p is None else (p[0], p[0] ^ p[1])


def add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    x, y = p
    u, v = q
    if x == u:
        if y != v or x == 0:
            return None
        lam = x ^ mul(y, inv(x))
        xx = square(lam) ^ lam ^ 1
        return (xx, square(x) ^ mul(lam ^ 1, xx))
    lam = mul(y ^ v, inv(x ^ u))
    xx = square(lam) ^ lam ^ x ^ u ^ 1
    return (xx, mul(lam, x ^ xx) ^ xx ^ y)


def alt_add(p,q):
    """Group law with a separately coded field product/inversion path."""
    if p is None:
        return q
    if q is None:
        return p
    x,y=p
    u,v=q
    if x==u:
        if y!=v or x==0:
            return None
        slope=x ^ schoolbook(y,alt_inv(x))
        xx=schoolbook(slope,slope)^slope^1
        return (xx,schoolbook(x,x)^schoolbook(slope^1,xx))
    slope=schoolbook(y^v,alt_inv(x^u))
    xx=schoolbook(slope,slope)^slope^x^u^1
    return (xx,schoolbook(slope,x^xx)^xx^y)


def on_curve(p):
    if p is None:
        return True
    x, y = p
    return square(y) ^ mul(x, y) == mul(square(x), x) ^ square(x) ^ 1


def multiple(p, k):
    out = None
    while k:
        if k & 1:
            out = add(out, p)
        p = add(p, p)
        k >>= 1
    return out


def fixed_base_powers(g):
    out = []
    while len(out) < R.bit_length():
        out.append(g)
        g = add(g, g)
    return out


def fixed_multiple(powers, k):
    out = None
    bit = 0
    while k:
        if k & 1:
            out = add(out, powers[bit])
        k >>= 1
        bit += 1
    return out


def frob(p):
    return None if p is None else (square(p[0]), square(p[1]))


def point_orbit(p):
    rows = set()
    q = p
    for _ in range(19):
        rows.add(q)
        rows.add(neg(q))
        q = frob(q)
    assert q == p and len(rows) == 38
    return sorted(rows)


def canonical_x(x):
    best = x
    y = x
    for _ in range(18):
        y = square(y)
        if y < best:
            best = y
    assert square(y) == x
    return best


def independent_field_controls():
    assert power(2, 1 << 19) == 2
    assert math.gcd(MOD, 2) == 1
    # Polynomial Euclidean gcd of x^(2)-x and the degree-19 modulus.
    def pgcd(a,b):
        while b:
            while a and a.bit_length() >= b.bit_length():
                a ^= b << (a.bit_length() - b.bit_length())
            a,b = b,a
        return a
    assert pgcd(MOD, square(2) ^ 2) == 1
    inversions=0
    for i in range(19):
        for j in range(19):
            assert mul(1<<i,1<<j) == schoolbook(1<<i,1<<j)
        assert square(1<<i) == schoolbook(1<<i,1<<i)
        assert mul(1<<i, inv(1<<i)) == 1
    for k in range(4096):
        d=hashlib.sha256(f'N19-AFFINE-v1-field-{k}'.encode()).digest()
        a=int.from_bytes(d[0:4],'little') & MASK
        b=int.from_bytes(d[4:8],'little') & MASK
        assert mul(a,b)==schoolbook(a,b)
        if a:
            assert mul(a,inv(a))==1
            inversions+=1
    return {'field_label_pairs':4096,'monomial_pairs':361,
            'monomial_inverses':19,'nonzero_labeled_inversions':inversions,
            'irreducibility_frobenius_gcd':True}


def expand_pool(pool):
    reps=[tuple(p) for p in pool['pool_representatives']]
    assert len(reps)==37 and len(set(reps))==37
    g=reps[0]
    assert g is not None and on_curve(g) and multiple(g,R) is None
    assert all(R % k for k in range(2,math.isqrt(R)+1))
    orbits=[]
    point_owner={}
    x_owner={}
    for i,p in enumerate(reps):
        assert on_curve(p) and multiple(p,R) is None
        full=point_orbit(p)
        assert len(full)==38
        for q in full:
            assert on_curve(q) and multiple(q,R) is None
            assert q not in point_owner
            point_owner[q]=i
            if q[0] in x_owner:
                assert x_owner[q[0]]==i
            else:
                x_owner[q[0]]=i
        orbits.append(full)
    assert len(point_owner)==1406 and len(x_owner)==703
    assert [list(x) for x in reps] == pool['pool_representatives']
    return g,reps,orbits,x_owner


def independent_group_controls(reps,orbits):
    for p in reps:
        assert add(p,None)==alt_add(p,None)==p
        assert add(p,neg(p))==alt_add(p,neg(p)) is None
        assert add(p,p)==alt_add(p,p)
        assert on_curve(add(p,p)) and multiple(add(p,p),R) is None
    repeats=opposites=0
    for k in range(4096):
        d=hashlib.sha256(f'N19-AFFINE-v1-group-{k}'.encode()).digest()
        limbs=[int.from_bytes(d[j:j+4],'little') for j in (0,4,8,12)]
        p=orbits[limbs[0]%37][limbs[2]%38]
        q=orbits[limbs[1]%37][limbs[3]%38]
        if p==q:
            repeats+=1
        if p==neg(q):
            opposites+=1
        s=add(p,q)
        assert s==alt_add(p,q)
        assert on_curve(s) and multiple(s,R) is None
        assert add(p,neg(p)) is None and add(q,neg(q)) is None
    return {'deterministic_group_pairs':4096,'representative_self_cancel_and_double':37,
            'sampled_repeated_pairs':repeats,'sampled_opposite_pairs':opposites,
            'independent_schoolbook_fermat_group_law_agreement':True}


def canonical_plane(vertices, square_lookup):
    v=tuple(sorted(vertices))
    best=v
    for _ in range(18):
        v=tuple(sorted(square_lookup[x] for x in v))
        if v < best:
            best=v
    assert tuple(sorted(square_lookup[x] for x in v))==tuple(sorted(vertices))
    return best


def enumerate_planes(orbits,x_owner):
    t0=time.perf_counter()
    xx=[sorted({p[0] for p in orbit}) for orbit in orbits]
    assert all(len(x)==19 for x in xx)
    square_lookup={x:square(x) for x in x_owner}
    assert all(square_lookup[x] in x_owner and x_owner[square_lookup[x]]==i
               for x,i in x_owner.items())
    buckets=defaultdict(list)
    pair_count=0
    for i in range(37):
        for j in range(i+1,37):
            for x in xx[i]:
                for y in xx[j]:
                    buckets[x^y].append((x,y,i,j))
                    pair_count+=1
    assert pair_count==240426
    planes={}
    collisions=0
    valid_partitions=0
    for rows in buckets.values():
        if len(rows)<2:
            continue
        for a,b in itertools.combinations(rows,2):
            collisions+=1
            ids={a[2],a[3],b[2],b[3]}
            if len(ids)!=4:
                continue
            v=(a[0],a[1],b[0],b[1])
            assert len(set(v))==4 and v[0]^v[1]^v[2]^v[3]==0
            valid_partitions+=1
            key=canonical_plane(v,square_lookup)
            oid=tuple(sorted(ids))
            assert tuple(sorted(x_owner[x] for x in key))==oid
            prior=planes.setdefault(key,oid)
            assert prior==oid
    by_base=defaultdict(list)
    for key,oid in planes.items():
        by_base[oid].append(key)
    for keys in by_base.values():
        keys.sort()
    # Independent triple-membership enumeration restricted to first 8 orbits.
    x8=sorted(x for x,i in x_owner.items() if i<8)
    first8=set()
    for x,y,z in itertools.combinations(x8,3):
        ids={x_owner[x],x_owner[y],x_owner[z]}
        if len(ids)!=3:
            continue
        w=x^y^z
        if w in x_owner and x_owner[w]<8 and x_owner[w] not in ids:
            first8.add(canonical_plane((x,y,z,w),square_lookup))
    pair_first8={key for key,oid in planes.items() if max(oid)<8}
    assert first8==pair_first8
    # The bit-reversal map is invertible and F2-linear. Rediscover rectangles
    # in its transformed coordinates, map vertices back, then canonicalize in
    # the original field basis where Frobenius is defined.
    def reverse19(x):
        return int(f'{x:019b}'[::-1],2)
    reversed_buckets=defaultdict(list)
    for i in range(37):
        for j in range(i+1,37):
            for x in xx[i]:
                rx=reverse19(x)
                for y in xx[j]:
                    ry=reverse19(y)
                    reversed_buckets[rx^ry].append((rx,ry,i,j))
    reversed_keys=set()
    for rows in reversed_buckets.values():
        for a,b in itertools.combinations(rows,2):
            if len({a[2],a[3],b[2],b[3]})==4:
                original=[reverse19(z) for z in (a[0],a[1],b[0],b[1])]
                reversed_keys.add(canonical_plane(original,square_lookup))
    assert reversed_keys==set(planes)
    return planes,by_base,{'cross_orbit_pairs':pair_count,
                           'equal_xor_record_collisions':collisions,
                           'four_distinct_orbit_pair_partitions':valid_partitions,
                           'first_eight_triple_control_planes':len(first8),
                           'bit_reversal_control_planes':len(reversed_keys),
                           'enumeration_elapsed_seconds_own_replay':time.perf_counter()-t0}


def targets_from_pool(pool,g):
    t0=time.perf_counter()
    scalars=pool['public_target_scalar_representatives']
    assert len(scalars)==6909 and len(set(scalars))==6909
    powers=fixed_base_powers(g)
    targets={}
    distinct_points=set()
    for d in scalars:
        assert 0<d<R
        q=fixed_multiple(powers,d)
        assert q is not None and on_curve(q) and multiple(q,R) is None
        orbit=point_orbit(q)
        key=canonical_x(q[0])
        assert key not in targets
        targets[key]=q
        assert not distinct_points.intersection(orbit)
        distinct_points.update(orbit)
    assert len(targets)==6909 and len(distinct_points)==R-1
    return dict(sorted(targets.items())),{'representatives':len(targets),
           'signed_orbit_points':len(distinct_points),
           'construction_elapsed_seconds_own_replay':time.perf_counter()-t0}


def coordinate_mitm(base_ids,orbits,targets):
    t0=time.perf_counter()
    base=sorted(p for i in base_ids for p in orbits[i])
    assert len(base)==152 and len(set(base))==152
    bset=set(base)
    pair={}
    for a,p in enumerate(base):
        for q in base[a:]:
            pair.setdefault(add(p,q),(p,q))
    rows=[]
    exact3=atmost3=0
    witness_checks=0
    for key,Q in targets.items():
        w3=None
        for p in base:
            w=pair.get(add(Q,neg(p)))
            if w is not None:
                triple=(p,w[0],w[1])
                assert all(t in bset for t in triple)
                assert add(add(*triple[:2]),triple[2])==Q
                w3=triple
                witness_checks+=1
                break
        if w3 is not None:
            exact3+=1
        wsmall=None
        if Q in bset:
            wsmall=(Q,)
        elif Q in pair:
            wsmall=pair[Q]
        if wsmall is not None:
            assert all(t in bset for t in wsmall)
            assert (wsmall[0] if len(wsmall)==1 else add(*wsmall))==Q
            witness_checks+=1
        wle3=w3 if w3 is not None else wsmall
        if wle3 is not None:
            atmost3+=1
        rows.append({'canonical_x':key,'exact3':w3 is not None,
                     'at_most3':wle3 is not None,
                     'exact3_witness':[list(p) for p in w3] if w3 else None,
                     'at_most3_witness':[list(p) for p in wle3] if wle3 else None})
    assert len(rows)==6909 and exact3<=atmost3
    return {'orbit_ids':list(base_ids),'base_points':len(base),
            'distinct_pair_sums_including_infinity':len(pair),
            'exact_three_coverage':exact3,'at_most_three_coverage':atmost3,
            'group_witnesses_replayed':witness_checks,
            'rows':rows,
            'elapsed_seconds_own_replay':time.perf_counter()-t0}


def anchored_support_crosscheck(base_ids,orbits,rows):
    """Separate symmetry-normalized enumeration for just the three reviewed bases.

    Any first point in a full signed-Frobenius orbit can be moved to its
    anchor by applying the same group automorphism to all summands and target.
    Thus 38^2 completions per orbit multiset suffice for exact triple support.
    """
    t0=time.perf_counter()
    exact=set()
    pair=set()
    singleton=set()
    triple_sums=pair_sums=0
    for i in base_ids:
        singleton.add(canonical_x(orbits[i][0][0]))
    for i,j in itertools.combinations_with_replacement(base_ids,2):
        anchor=orbits[i][0]
        for q in orbits[j]:
            v=add(anchor,q)
            pair_sums+=1
            if v is not None:
                pair.add(canonical_x(v[0]))
    for i,j,k in itertools.combinations_with_replacement(base_ids,3):
        anchor=orbits[i][0]
        for q in orbits[j]:
            partial=add(anchor,q)
            for t in orbits[k]:
                v=add(partial,t)
                triple_sums+=1
                if v is not None:
                    exact.add(canonical_x(v[0]))
    seen_exact={v['canonical_x'] for v in rows if v['exact3']}
    seen_atmost={v['canonical_x'] for v in rows if v['at_most3']}
    assert exact==seen_exact
    assert exact|pair|singleton==seen_atmost
    return {'triple_multisets':20,'pair_multisets':10,
            'anchored_triple_sums':triple_sums,'anchored_pair_sums':pair_sums,
            'exact_three_keys':len(exact),'at_most_three_keys':len(seen_atmost),
            'agreement_with_direct_mitm':True,
            'elapsed_seconds_own_replay':time.perf_counter()-t0}


def main():
    whole_t0=time.perf_counter()
    protocol,protocol_sha=load('protocol.json')
    amendment,amendment_sha=load('baseline_amendment.json')
    pool,pool_sha=load('inputs/pool.json')
    coordinates,coordinates_sha=load('review/selected_coordinates_only.json')
    assert protocol['curve']['modulus']==MOD and protocol['curve']['prime_subgroup_order']==R
    assert protocol['inputs']['pool_sha256']==pool_sha
    assert amendment['original_protocol']['sha256']==protocol_sha
    assert pool['field_modulus_low_terms']==[0,1,2,5]
    assert coordinates['curve']['modulus']==MOD and coordinates['curve']['r']==R
    field=independent_field_controls()
    g,reps,orbits,x_owner=expand_pool(pool)
    group=independent_group_controls(reps,orbits)
    assert list(g)==coordinates['curve']['generator']
    planes,by_base,geometry=enumerate_planes(orbits,x_owner)
    selected_ids=tuple(coordinates['selected']['orbit_ids'])
    selected_key=tuple(coordinates['selected']['plane_key'])
    prior_ids=tuple(coordinates['prior']['orbit_ids'])
    null_ids=tuple(coordinates['null']['orbit_ids'])
    assert all(len(ids)==4 and tuple(sorted(set(ids)))==ids for ids in (selected_ids,prior_ids,null_ids))
    assert selected_key in planes and planes[selected_key]==selected_ids
    assert selected_key==by_base[selected_ids][0]
    assert prior_ids==tuple(pool['prior_selected_indices'])
    assert null_ids not in by_base
    assert null_ids==next(ids for ids in itertools.combinations(range(37),4) if ids not in by_base)
    a,b,c=selected_key[0],selected_key[0]^selected_key[1],selected_key[0]^selected_key[2]
    assert b and c and b!=c and tuple(sorted((a,a^b,a^c,a^b^c)))==selected_key
    # Known-invalid geometry and label certificates must fail our verifier.
    def valid_cert(key,ids):
        return (len(key)==4 and len(set(key))==4 and not (key[0]^key[1]^key[2]^key[3])
                and key in planes and planes[key]==ids)
    assert valid_cert(selected_key,selected_ids)
    flipped=tuple(sorted((selected_key[0]^1,*selected_key[1:])))
    assert not valid_cert(flipped,selected_ids)
    bad_ids=tuple(sorted((0,*selected_ids[1:])))
    assert bad_ids!=selected_ids and not valid_cert(selected_key,bad_ids)
    assert not valid_cert((selected_key[0],selected_key[0],*selected_key[2:]),selected_ids)
    targets,target_info=targets_from_pool(pool,g)
    coverage={}
    for name,ids in [('selected',selected_ids),('prior',prior_ids),('null',null_ids)]:
        coverage[name]=coordinate_mitm(ids,orbits,targets)
        coverage[name]['anchored_support_crosscheck']=anchored_support_crosscheck(
            ids,orbits,coverage[name]['rows'])
    assert coverage['prior']['exact_three_coverage']==pool['prior_exact_three_orbits']==6224
    assert coverage['prior']['at_most_three_coverage']==pool['prior_at_most_three_orbits']==6257
    result={'schema':'crypto.autoresearch.affine_blind_derivation.v1',
            'task_id':'TASK-20260921-c1a993',
            'input_sha256':{'protocol':protocol_sha,'amendment':amendment_sha,
                            'pool':pool_sha,'selected_coordinates_only':coordinates_sha},
            'field_controls':field,'group_controls':group,'generator':list(g),
            'pool':{'orbits':37,'signed_points':1406,'x_values':703},
            'geometry':{**geometry,'canonical_full_admission_planes':len(planes),
                        'compatible_four_orbit_bases':len(by_base),
                        'planes_per_compatible_base':{'-'.join(map(str,k)):len(v) for k,v in sorted(by_base.items())},
                        'all_planes':[{'key':list(k),'orbit_ids':list(v)} for k,v in sorted(planes.items())],
                        'selected_plane':{'orbit_ids':list(selected_ids),'key':list(selected_key),
                                          'a_b_c':[a,b,c],
                                          'planes_in_selected_base':len(by_base[selected_ids])},
                        'negative_controls':{'one_vertex_flip_rejected':True,
                                             'false_orbit_label_rejected':True,
                                             'repeated_vertex_rejected':True,
                                             'null_base_has_no_plane':True}},
            'targets':target_info,
            'coverage':coverage,
            'selected_ratio_to_prior_exact_three':coverage['selected']['exact_three_coverage']/6224,
            'own_replay_elapsed_seconds':time.perf_counter()-whole_t0,
            'own_process_maxrss_raw':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'own_process_maxrss_unit':'platform-dependent getrusage ru_maxrss; not a run receipt',
            'sources_read':READS}
    out=P/'review/blind_results.json'
    out.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'planes':len(planes),'compatible_bases':len(by_base),
                      'selected':(coverage['selected']['exact_three_coverage'],coverage['selected']['at_most_three_coverage']),
                      'prior':(coverage['prior']['exact_three_coverage'],coverage['prior']['at_most_three_coverage']),
                      'null':(coverage['null']['exact_three_coverage'],coverage['null']['at_most_three_coverage']),
                      'elapsed_own_replay_seconds':result['own_replay_elapsed_seconds']}))


if __name__=='__main__':
    main()
