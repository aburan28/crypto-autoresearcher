import os, re, sys
from math import gcd

txt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'binary-curve-params.txt')).read()
blocks = re.split(r'===== (\S+) =====', txt)[1:]
pairs = list(zip(blocks[0::2], blocks[1::2]))

def hexblob(body, label):
    m = re.search(re.escape(label) + r':\s*\n((?:\s+[0-9a-f:]+\n)+)', body)
    if not m:
        m = re.search(re.escape(label) + r':\s*((?:[0-9a-f]{2}:)+[0-9a-f]{2})', body)
        if not m: return None
    h = re.sub(r'[^0-9a-f]', '', m.group(1))
    return int(h, 16) if h else None

def clmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r

def red(a, f, m):
    fb = f.bit_length() - 1
    while a.bit_length() - 1 >= fb:
        a ^= f << (a.bit_length() - 1 - fb)
    return a

def mul(a, b, f, m): return red(clmul(a, b), f, m)
def sq(a, f, m): return mul(a, a, f, m)

def in_subfield(a, d, f, m):
    x = a
    for _ in range(d): x = sq(x, f, m)
    return x == a

def divisors(n):
    return sorted({d for i in range(1, int(n**0.5)+1) if n % i == 0 for d in (i, n//i)})

print(f"{'curve':<12} {'m':>4} {'prime_m':>7} {'A_in':>18} {'B_in':>18} {'cofactor':>10}")
rows = []
for name, body in pairs:
    if 'characteristic-two-field' not in body: continue
    f = hexblob(body, 'Polynomial')
    A = hexblob(body, 'A')
    B = hexblob(body, 'B')
    order = hexblob(body, 'Order')
    cof = re.search(r'Cofactor:\s*(\d+)', body)
    cof = int(cof.group(1)) if cof else None
    if f is None: continue
    m = f.bit_length() - 1
    divs = [d for d in divisors(m) if d < m]
    Ain = [d for d in divs if A is not None and in_subfield(A, d, f, m)]
    Bin = [d for d in divs if B is not None and in_subfield(B, d, f, m)]
    isprime = all(m % p for p in range(2, int(m**0.5)+1)) and m > 1
    rows.append((name, m, isprime, min(Ain) if Ain else None, min(Bin) if Bin else None, cof, order))
    print(f"{name:<12} {m:>4} {str(isprime):>7} {str(min(Ain) if Ain else '-'):>18} {str(min(Bin) if Bin else '-'):>18} {str(cof):>10}")

print()
print("Composite-m curves, subfield check detail:")
for name, m, isprime, Ad, Bd, cof, order in rows:
    if not isprime:
        d = max(x for x in (Ad or 1, Bd or 1))
        print(f"  {name}: m={m}={' * '.join(str(p) for p in ([2]*0))}{m}, smallest subfield containing A: {Ad}, B: {Bd}, cofactor {cof}, order_bits {order.bit_length() if order else None}")
