"""Independent answer check (not the producer, not the pinned oracle): for every panel point of a run,
every IC process and the rT process report one scalar d, and [d]G == Q on the Koblitz curve
y^2 + xy = x^3 + a x^2 + 1 over GF(2^83), modulus x^83 + x^7 + x^4 + x^2 + 1 (record field_modulus_low_terms
[0,2,4,7]), a = 1, polynomial-basis integers. Also checks G and Q on the curve and [r]G = O."""
import json, base64, sys, collections
M = (1 << 83) | (1 << 7) | (1 << 4) | (1 << 2) | 1
def mul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 83: a ^= M
    return r
def sq(a): return mul(a, a)
def inv(a):
    # a^(2^83 - 2)
    r = 1; e = (1 << 83) - 2; base = a
    while e:
        if e & 1: r = mul(r, base)
        base = sq(base); e >>= 1
    return r
A = 1
def on_curve(P):
    if P is None: return True
    x, y = P; return (sq(y) ^ mul(x, y)) == (mul(sq(x), x) ^ mul(A, sq(x)) ^ 1)
def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y2 == (x1 ^ y1): return None
        if x1 == 0: return None
        l = x1 ^ mul(y1, inv(x1)); x3 = sq(l) ^ l ^ A; y3 = sq(x1) ^ mul(l ^ 1, x3); return (x3, y3)
    l = mul(y1 ^ y2, inv(x1 ^ x2)); x3 = sq(l) ^ l ^ x1 ^ x2 ^ A; y3 = mul(l, x1 ^ x3) ^ x3 ^ y1; return (x3, y3)
def smul(k, P):
    R = None
    for bit in bin(k)[2:]:
        R = add(R, R)
        if bit == '1': R = add(R, P)
    return R
r = 8569786107849059
G = (6614244651398184860292015, 8868260410029249391539529)
res = dict(G_on_curve=on_curve(G), rG_is_O=smul(r, G) is None)
d = sys.argv[1]; rows = [json.loads(l) for l in open(d + '/runs.jsonl')]
by_point = collections.defaultdict(set); pts = {}
for row in rows:
    t = open(d + '/runs/' + row['stdout_file'].split('/')[-1]).read().split('\n')[0]
    rec = json.loads(base64.b64decode(t.split('=', 1)[1]))
    p = rec.get('panel'); by_point[p].add(str(rec['fields']['recovered_scalar'])); pts[p] = tuple(int(v) for v in rec['point'])
bad = []; ok = 0
for p, sc in by_point.items():
    Q = pts[p]
    if len(sc) != 1 or not on_curve(Q) or smul(int(next(iter(sc))), G) != Q: bad.append(p)
    else: ok += 1
res.update(points=len(by_point), verified=ok, failed=bad)
print(json.dumps(res))
