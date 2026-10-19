#!/usr/bin/env python3
"""H3 / protocol I-2: price the isogeny transport against the rho cost for
every binary Koblitz class on the ladder (n = 11 .. 131) and the two
constructed ordinary classes (n = 16 Koblitz f = 3*31; n = 51 ordinary f = 49).

For the Koblitz curve K_a : y^2 + xy = x^3 + a x^2 + 1 over F_{2^n}, the
Frobenius pi = tau^n with tau^2 + (-1)^a tau... concretely tau^2 - mu tau + 2 = 0,
mu = (-1)^{1-a}, so t_n = tr(tau^n) follows t_k = mu t_{k-1} - 2 t_{k-2},
t_0 = 2, t_1 = mu.  Then D = t^2 - 4 q = -7 f^2 and f = cond(Z[pi]).

For each prime ell | f (the only degrees along which the class has vertical
structure, h(-7) = 1): pi acts on E[ell] as the scalar lambda = t/2 mod ell
(since pi in Z + ell O_K), and the kernel points of a descending ell-isogeny
live in F_{q^d} with d = ord(lambda mod ell).  Costs, all in F_q
multiplications, as in docs/ic/RESEARCH_ISOGENY_CONDUCTOR_GAP_20261007.md:

  construct the isogeny (kernel route): find an ell-torsion point over F_{q^d}
    ~ (log2 #E(F_{q^d})) scalar multiplications in F_{q^d}, each ~ d^2 F_q-mults
    per F_{q^d}-mult (schoolbook) times ~1.5 log2 q^d ... we charge
    T_kernel = 2 * d^2 * (n d) * 8   [two scalar mults with Montgomery-ladder
    style ~8 F_{q^d}-mults per bit, over n d bits]
  Velu evaluation of one point: ~ 12 * ell F_q-mults (ell kernel multiples,
    each a few mults; x-only Velu would be ~6 ell), two points per instance;
    sqrt-Velu ~ 12 * sqrt(ell) log ell when ell > ~100.
  transfer_total = T_kernel + 2 * T_eval
  rho (negation only, no Frobenius on the floor): sqrt(pi r / 4) group
    operations, each ~ 10 F_q-mults (affine binary addition ~ 1 I + 2 M + 1 S
    ~ 10 M with batched inversion); the crater's signed-Frobenius rho divides
    the group operations by sqrt(2n).

The blueprint's H3 quantity: direct_attack_advantage must survive pricing of
map construction and subgroup transfer; here the ratio
transfer_total / rho_floor says how much any "direct advantage" on a floor
curve would have to be worth before transport to the crater is the cheaper
route.  For large ell the kernel route is infeasible and the table says so.
"""
import json, math, sys

out = sys.argv[1] if len(sys.argv) > 1 else "transport_cost_table.json"


def trace(n, a):
    mu = 1 if a == 1 else -1
    t0, t1 = 2, mu
    for _ in range(n - 1):
        t0, t1 = t1, mu * t1 - 2 * t0
    return t1 if n >= 1 else t0


def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True


def pollard(n):
    if n % 2 == 0: return 2
    import random
    while True:
        c = random.randrange(1, n); f = lambda x: (x * x + c) % n
        x = y = 2; d = 1
        while d == 1:
            x = f(x); y = f(f(y)); d = math.gcd(abs(x - y), n)
        if d != n: return d


def factor(n):
    out = {}
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        while n % p == 0: out[p] = out.get(p, 0) + 1; n //= p
    stack = [n] if n > 1 else []
    while stack:
        m = stack.pop()
        if m == 1: continue
        if is_prime(m): out[m] = out.get(m, 0) + 1; continue
        d = pollard(m); stack += [d, m // d]
    return dict(sorted(out.items()))


def mult_order(l, m):
    if math.gcd(l, m) != 1: return None
    o, x = 1, l % m
    while x != 1:
        x = x * l % m; o += 1
        if o > 10 ** 7: return None
    return o


def row(n, a, t, q, f, fac, r, label):
    rows = []
    for ell, e in fac.items():
        lam = (t * pow(2, -1, ell)) % ell if ell != 2 else None
        d = mult_order(lam, ell) if lam not in (None, 0) else None
        if d is None:
            rows.append(dict(ell=ell, height=e, lambda_mod_ell=lam, kernel_field_degree=None, feasible=False,
                             note="kernel field degree above 10^7 (order of lambda mod ell not computed); infeasible")); continue
        T_kernel = 2 * d * d * (n * d) * 8
        T_eval = 12 * ell if ell < 100 else 12 * int(math.sqrt(ell)) * max(1, int(math.log2(ell)))
        transfer = T_kernel + 2 * T_eval
        rho_floor = math.sqrt(math.pi * r / 4) * 10
        rho_crater = rho_floor / math.sqrt(2 * n)
        rows.append(dict(ell=ell, height=e, lambda_mod_ell=lam, kernel_field_degree=d, log2_T_kernel=math.log2(T_kernel),
                         log2_T_eval=math.log2(T_eval), log2_transfer_total=math.log2(transfer), log2_rho_floor_Fq_mults=math.log2(rho_floor),
                         log2_rho_crater_Fq_mults=math.log2(rho_crater), transfer_over_rho_floor=transfer / rho_floor,
                         feasible=(d <= 4096), largest_floor_advantage_that_survives_transport_bits=max(0.0, math.log2(rho_floor / transfer))))
    return dict(label=label, n=n, a2=a, trace=t, order=q + 1 - t, r=r, conductor=f, conductor_factors={str(k): v for k, v in fac.items()}, per_ell=rows)


def largest_prime_factor(m):
    return max(factor(m).keys())


table = []
for n in (11, 16, 17, 19, 23, 31, 37, 41, 53, 61, 71, 73, 83, 97, 131):
    q = 2 ** n
    for a in (0, 1):
        t = trace(n, a); D = t * t - 4 * q; assert D % -7 == 0 and D < 0
        f2 = D // -7; f = math.isqrt(f2); assert f * f == f2
        order = q + 1 - t
        r = largest_prime_factor(order)
        if n <= 31 or (n, a) in ((37, 0), (41, 0), (53, 0), (61, 0), (71, 0), (73, 0), (83, 0), (97, 0), (131, 0)):
            table.append(row(n, a, t, q, f, factor(f), r, f"Koblitz K_{a} n={n}"))
# the n = 51 ordinary class from binary_level_yield (f_pi = 49, ell = 7, order given by the run)
try:
    r51 = json.loads(open("/home/user/crypto/isogeny_algos/results/binary_level_yield_n51.jsonl").readline())
    t, q = r51["trace"], 2 ** 51; f = r51["f_pi"]; fac = {int(p): e for p, e in r51["f_pi_factored"]}
    table.append(row(51, int(r51["a2"], 16), t, q, f, fac, r51["r"], "ordinary random-b n=51 (binary_level_yield)"))
except Exception as e:  # noqa
    table.append(dict(label="ordinary n=51", error=repr(e)))
json.dump({"schema": "transport_cost_table/v1", "cost_model": __doc__, "classes": table}, open(out, "w"), indent=1)
print("| class | n | r bits | f = cond(Z[pi]) | ell (height) | kernel field degree d | log2 transfer (F_q mults) | log2 rho floor | log2 rho crater | floor advantage that survives transport (bits) | feasible |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for c in table:
    if "error" in c:
        print(f"| {c['label']} | | | | error: {c['error']} | | | | | | |"); continue
    for e in c["per_ell"]:
        if e.get("kernel_field_degree") is None:
            print(f"| {c['label']} | {c['n']} | {math.log2(c['r']):.1f} | {c['conductor']} | {e['ell']} ({e['height']}) | — | — | — | — | — | {e.get('note')} |"); continue
        print(f"| {c['label']} | {c['n']} | {math.log2(c['r']):.1f} | {c['conductor']} | {e['ell']} ({e['height']}) | {e['kernel_field_degree']} | {e['log2_transfer_total']:.1f} | {e['log2_rho_floor_Fq_mults']:.1f} | {e['log2_rho_crater_Fq_mults']:.1f} | {e['largest_floor_advantage_that_survives_transport_bits']:.1f} | {'yes' if e['feasible'] else 'no (kernel field too large)'} |")
