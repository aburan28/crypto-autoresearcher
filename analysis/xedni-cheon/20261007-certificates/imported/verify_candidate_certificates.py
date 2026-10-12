"""Independent exact verifier: no factor searches or probable-prime tests.

The rank conclusion uses the standard two-isogeny squareclass theorem;
the accompanying mathematical proof specifies why the checked conditions suffice.
"""

import copy
import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_primes(nodes):
    done = set()
    active = set()
    modular_checks = 0
    def check(n):
        nonlocal modular_checks
        if n in done:
            return
        require(n not in active, "certificate cycle")
        require(str(n) in nodes, "missing prime node")
        d = nodes[str(n)]
        require(type(d['n']) is int and d['n'] == n, "node identity mismatch")
        active.add(n)
        if d['method'] == 'base_case':
            require(n == 2, "invalid prime base case")
        else:
            require(d['method'] == 'lucas_full_n_minus_1' and n > 2, "invalid criterion")
            product = 1
            require(bool(d['factors']), "empty factorization")
            require(set(d['factors']) == set(d['witnesses']), "witness coverage mismatch")
            for key, exponent in d['factors'].items():
                q = int(key)
                require(2 <= q < n and type(exponent) is int and exponent > 0,
                        "invalid prime factor or exponent")
                check(q)
                product *= q ** exponent
            require(product == n - 1, "n-1 factorization mismatch")
            for key, a in d['witnesses'].items():
                q = int(key)
                require(type(a) is int and 1 <= a < n, "invalid Lucas witness")
                require(pow(a, n - 1, n) == 1, "Fermat identity failed")
                require(math.gcd(pow(a, (n - 1) // q, n) - 1, n) == 1,
                        "Lucas gcd identity failed")
                modular_checks += 1
        active.remove(n)
        done.add(n)
    for key in nodes:
        check(int(key))
    return done, modular_checks


def on_curve(point, a, b):
    if point is None:
        return True
    x, y = point
    return y * y == x * (x * x + a * x + b)


def phi(point, a, b):
    if point is None or point[0] == 0:
        return None
    x, y = point
    return (F(y * y, x * x), F(y * (x * x - b), x * x))


def dual(point, a, b):
    if point is None or point[0] == 0:
        return None
    x, y = point
    D = a * a - 4 * b
    return (F(y * y, 4 * x * x), F(y * (x * x - D), 8 * x * x))


def double(point, a, b):
    if point is None or point[1] == 0:
        return None
    x, y = point
    slope = F(3 * x * x + 2 * a * x + b, 2 * y)
    nx = slope * slope - a - 2 * x
    return (nx, slope * (x - nx) - y)


def verify(data):
    require(not data['failures'], "generation reported failures")
    proved, modular_checks = verify_primes(data['prime_nodes'])
    require(len(data['candidates']) == 2, "expected exactly two candidates")
    rows = []
    for c in data['candidates']:
        n, a, b, D = c['n'], c['a'], c['b'], c['D']
        r, f1, f2 = c['prime_roots']
        require(all(v in proved for v in (r, f1, f2)), "unproved factor")
        require(n in (-1793, 181), "unexpected source parameter")
        require(b == 635728705996536026 * n - 1792587436107314570824479,
                "source B polynomial mismatch")
        require(f1 == 124609*n*n + 303443264744*n + 8697969664620875680,
                "source factor 1 mismatch")
        require(f2 == 124609*n*n + 303442272108*n + 8697963332447929000,
                "source factor 2 mismatch")
        require(a > 0 and b == -r and D == a*a - 4*b == f1*f2,
                "coefficient or discriminant mismatch")
        require(r > 2 and f1 > 2 and f2 > 2 and f1 != f2,
                "distinct-prime squareclasses unavailable")
        require(c['Eprime_a'] == -2*a and c['Eprime_b'] == D,
                "isogenous curve mismatch")
        P, Q, R = tuple(c['P']), tuple(c['Q']), tuple(c['R'])
        require(c['T'] == c['Tprime'] == [0, 0], "torsion point mismatch")
        require(P[0] == 703**2 and Q[0] == -439**2, "signed-square x mismatch")
        require(on_curve(P, a, b) and on_curve(Q, a, b), "lifted point equation failed")
        require(on_curve(R, -2*a, D), "isogenous witness equation failed")
        require(R[0] == f2 and dual(R, a, b) == P, "dual preimage identity failed")
        for point in (P, Q):
            image = phi(point, a, b)
            require(on_curve(image, -2*a, D), "phi curve identity failed")
            require(dual(image, a, b) == double(point, a, b), "dual(phi(point)) != 2 point")
        require(a % 353 == 352 and b % 353 == 16,
                "finite curve reduction failed")
        require(tuple(v % 353 for v in P) == (9, 63) and
                tuple(v % 353 for v in Q) == (17, 183), "point reduction failed")
        require((16*b*b*D) % 353 != 0, "bad source reduction")
        require(all(353 % d for d in range(2, math.isqrt(353) + 1)),
                "source modulus not prime")
        require(c['alpha_generators'] == [-1, b] and
                c['alpha_prime_generators'] == [f2, D], "descent label mismatch")
        require(math.isqrt(D)**2 != D, "extra rational 2-torsion")
        # E has only signed squarefree divisors of b as x-squareclasses.
        # They all occur: Q supplies -1 and T supplies -r.
        # Eprime has no negative x because a>0,D>0.
        # Its four allowed positive squareclasses all occur via R and Tprime.
        # The standard descent formula gives rank=log2(4)+log2(4)-2=2.
        # alpha(Q) and alpha(T) are independent; P is not in 2E since
        # alpha_prime(R)=f2 is neither 1 nor D. Thus P,Q,T are independent
        # in E/2E; as E has just one rational 2-torsion generator, P,Q
        # are independent in the free part (even modulo all torsion).
        rows.append({"n": n, "certified_primes": [r, f1, f2],
                     "alpha_image": [1, -1, r, -r],
                     "alpha_prime_image": [1, f1, f2, D],
                     "rank_lower_bound": 2, "rank_upper_bound": 2,
                     "P_Q_independent_modulo_torsion": True,
                     "usable_rational_dependency": False,
                     "dual_preimage_identity_checked": True})
    require({r['n'] for r in rows} == {-1793, 181}, "duplicate candidates")
    return {"verified_prime_nodes": len(proved), "Lucas_modular_witness_checks": modular_checks,
            "candidates": rows}


def negative_controls(data):
    cases = []
    bad = copy.deepcopy(data)
    node = bad['prime_nodes'][str(bad['candidates'][0]['prime_roots'][0])]
    node['witnesses'][next(iter(node['witnesses']))] = 1
    cases.append(('invalid_Lucas_witness', bad))
    bad = copy.deepcopy(data)
    bad['candidates'][0]['P'][1] += 1
    cases.append(('off_curve_point', bad))
    bad = copy.deepcopy(data)
    bad['candidates'][0]['R'][1] *= -1
    cases.append(('wrong_dual_preimage_sign', bad))
    bad = copy.deepcopy(data)
    bad['candidates'][0]['D'] += 1
    cases.append(('wrong_discriminant', bad))
    controls = []
    for name, bad in cases:
        try:
            verify(bad)
        except ValueError as exc:
            controls.append({"name": name, "rejected": True, "reason": str(exc)})
        else:
            raise ValueError(f"negative control accepted: {name}")
    return controls


def main():
    started = time.monotonic()
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('candidate_certificates.json')
    data = json.loads(source.read_text())
    result = verify(data)
    result['negative_controls'] = negative_controls(data)
    result['verification_elapsed_seconds'] = time.monotonic() - started
    result['status'] = 'verified'
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
