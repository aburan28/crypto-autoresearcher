#!/usr/bin/env python3
from sage.all import *
proof.all(False)

r'''
Simple proof-of-concept implementation of Benjamin Wesolowski's
2026 attack against the OneEnd problem with time complexity
    p^(1/3+o(1)),
which directly implies a p^(1/3+o(1)) attack against the EndRing
problem by a known (in context negligible) reduction.

Written by Lorenz Panny, tested with SageMath version 10.9.
'''

################################################################

# generate an example instance

p = previous_prime(2**40)
print(f'{p = } ≈ 2^{p.bit_length()}')

s = GF(p).one()
while s.is_square():
    s += 1
F = GF((p, 2), modulus=[-s,0,1], name='T')

E = special_supersingular_curve(F)
for _ in range(3 * p.bit_length()):  # or something
    E = choice(E.isogenies_prime_degree(2)).codomain()
print(f'\x1b[33mattacking {E = }\x1b[0m')

################################################################

# generate all smooth isogenies up to a given degree

def count(smooth, max_deg, degs=(1,)):
    ret = 1
    for l in prime_range(degs[-1], min(floor(max_deg), smooth) + 1):
        num = l + (l != degs[-1])
        ret += num * count(smooth, max_deg / l, degs + (l,))
    return ret

def isogs(smooth, max_deg, chain):
    # BFS ordering
    yield chain
    prev_deg = chain[-2] if len(chain) >= 2 else 1
    for l in prime_range(prev_deg, min(floor(max_deg), smooth) + 1):
        for j in classical_modular_polynomial(l, chain[-1]).roots(multiplicities=False):
            if len(chain) >= 3 and j == chain[-3]:
                continue
            yield from isogs(smooth, max_deg / l, chain + [l, j])

################################################################

# attack: find a B-smooth isogeny of degree up to X to the conjugate

B = ceil(exp(1/3 * sqrt(log(p/2))))
print(f'\x1b[35mattack parameter {B = }\x1b[0m')

X = ceil(B * (p/2)**(1/6))
print(f'\x1b[35mattack parameter {X = }\x1b[0m')

print(f'estimated table size: {count(B, X)}')

tab = dict()
for _, chain in enumerate(isogs(B, X, [E.j_invariant()])):
    if _ % 100 == 0:
        print(f'\x1b[K{len(tab) = :9}', end='\r', file=sys.stderr, flush=True)
    j = chain[-1]
    try:
        hit = tab[j**p]
    except KeyError:
        pass
    else:
        break
    tab[j] = chain
else:
    print('\n\x1b[31mno solution found (try re-running)\x1b[0m')
    exit(1)

print(f'\n\x1b[36mfound a solution!\x1b[0m')
assert hit[-1] == j**p
sol = chain
for i in reversed(range(0, len(hit)-1, 2)):
    sol.append(hit[i+1])
    sol.append(hit[i+0]**p)

################################################################

# verify the solution

print(f'\x1b[32m{sol = }\x1b[0m')

assert sol[0] == E.j_invariant()
assert sol[-1] == E.j_invariant()**p
ls = []
for i in range(0, len(sol)-1, 2):
    j0 = sol[i+0]
    l  = sol[i+1]
    j1 = sol[i+2]
    assert classical_modular_polynomial(l)(j0, j1) == 0
    ls.append(l)

deg = prod(ls)
print(f'\x1b[36m{deg = } ≈ p^{RR(log(deg,p))}\x1b[0m')
print(f'{ls = }')

