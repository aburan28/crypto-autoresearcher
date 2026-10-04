"""Structural consistency checks on the four maximizers."""
import json
from gf2poly import deg, clmul, polymod, polygcd, frob_pow_mod, poly_str, is_irreducible
from gfk import Field
from method import count_roots, superset_poly
from rederive import FIELD_POLY, N_BITS, NPRIME
from crosschecks import translate

F = Field(FIELD_POLY)
data = json.load(open('../out/rederivation_results.json'))
ent = {e['lambda_packed']: e for e in data['attaining']}

print('per-maximizer detail')
for lam in sorted(ent):
    N, G = count_roots(lam, N_BITS, NPRIME, k=4, e=1, want_G=True)
    P = superset_poly(lam, 4, 1)
    g = polygcd(P, frob_pow_mod(N_BITS, P) ^ 2)
    q = [o for o in ent[lam]['orbits'] if o['orbit_size'] == 131][0]
    qp = q['minpoly_packed']
    small = [o for o in ent[lam]['orbits'] if o['orbit_size'] == 1][0]
    lin = small['minpoly_packed']
    print(f'  lambda={lam:4d} {poly_str(lam):40s}')
    print(f'    deg P = {deg(P)}   deg g = gcd(P, X^(2^131)+X) = {deg(g)}   deg G = {deg(G)} = N')
    print(f'    G = (linear factor {poly_str(lin)}) * (irreducible of degree {deg(qp)}): '
          f'{clmul(lin, qp) == G}')
    print(f'    minpoly of the big orbit irreducible over GF(2): {is_irreducible(qp)}')
    # condition verified in the ABSTRACT field GF(2)[X]/(q), independent of any embedding
    lhs = frob_pow_mod(NPRIME, qp)
    print(f'    X^(2^33) == lambda(X) mod q  (abstract field, no embedding): '
          f'{lhs == polymod(lam, qp)}')
    print(f'    F_2 root: {"0" if lin == 2 else "1"}   '
          f'(lambda(0)={lam & 1}, lambda(1)={bin(lam).count("1") % 2})')
    print(f'    q = 0x{qp:x}')

print()
print('translation involution on ROOT SETS:  x root for lambda  <=>  x+1 root for lambda(X+1)+1')
for a, b in [(132, 251), (161, 204)]:
    ra = set()
    for o in ent[a]['orbits']:
        ra |= {int(v[::-1], 2) for v in o['roots_bits_lsb_first']}
    rb = set()
    for o in ent[b]['orbits']:
        rb |= {int(v[::-1], 2) for v in o['roots_bits_lsb_first']}
    print(f'  lambda {a} -> translate = {translate(a)} (== {b}: {translate(a) == b}); '
          f'root sets are translates by 1: {({x ^ 1 for x in ra} == rb)}')

print()
print('closure / sanity on the root sets')
for lam in sorted(ent):
    rs = []
    for o in ent[lam]['orbits']:
        rs += [int(v[::-1], 2) for v in o['roots_bits_lsb_first']]
    assert len(set(rs)) == 132
    print(f'  lambda={lam}: {len(rs)} roots; all in K (bit length <= 131): '
          f'{all(x.bit_length() <= 131 for x in rs)}; '
          f'set closed under x->x^2: {set(F.sqr(x) for x in rs) == set(rs)}; '
          f'contains 0: {0 in rs}; contains 1: {1 in rs}')
