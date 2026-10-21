"""Factorisation survey of the curve corpus: which derived numbers are not quickly factorable.
Per curve (p, n, h): t = p+1-h*n; numbers: D=4p-t^2, twist=p+1+t, n-1, n+1, p-1, p+1.
Each: PARI factorint under a per-number wall-clock limit (subprocess); on timeout, PARI factor(N, 2^32)
partial result and the composite cofactor size."""
import json, sys, subprocess, os
sys.path.insert(0, '/home/user/wt/native-export')
from harness.endosweep.corpus import load_std_curves
from harness.endosweep import arkworks as AK
LIMIT = float(os.environ.get('LIMIT', '30'))
CHILD = r'''
import sys, cypari2; pari=cypari2.Pari(); pari.allocatemem(2*10**8, silent=True)
N=int(sys.argv[1]); mode=sys.argv[2]
if mode=='full':
    F=pari.factorint(N)
else:
    F=pari.factor(N, 2**32)
ps=[int(x) for x in F[0]]; es=[int(x) for x in F[1]]
print(" ".join(f"{p}^{e}:{1 if pari.ispseudoprime(p) else 0}" for p,e in zip(ps,es)))
'''
def run(N, mode, t):
    try:
        r = subprocess.run([sys.executable, '-c', CHILD, str(N), mode], capture_output=True, text=True, timeout=t)
        return [(int(a.split('^')[0]), int(a.split('^')[1].split(':')[0]), a.endswith(':1')) for a in r.stdout.split()]
    except subprocess.TimeoutExpired:
        return None
def fac(N):
    f = run(N, 'full', LIMIT)
    if f is not None and all(pr for _,_,pr in f):
        return {"status": "FF", "factors": [[str(p), e] for p,e,_ in f]}
    f = run(N, 'partial', 30) or []
    comp = [p for p,_,pr in f if not pr]
    return {"status": "CF", "known": [[str(p), e] for p,e,pr in f if pr],
            "composite_digits": [len(str(c)) for c in comp], "composite": [str(c) for c in comp]}
from harness.endosweep.targets import verify
from harness.endosweep.curvesweep import _key
curves, seen = [], set()
for T, e, _ in load_std_curves(sys.argv[1]) + load_std_curves(sys.argv[2]):
    if T is None or T.ext_degree != 1: continue
    verify(T)
    if not T.verified or _key(T) in seen: continue
    seen.add(_key(T)); curves.append(T)
print(len(curves), "verified prime-field curves", flush=True)
out = open(sys.argv[3], 'a'); done = set()
if os.path.exists(sys.argv[3]):
    done = {json.loads(l)['name'] for l in open(sys.argv[3]) if l.strip()}
import time
for T in curves:
    while os.path.exists(os.environ.get('PAUSE', '/nonexistent')): time.sleep(20)
    if T.name in done: continue
    p, n, h, t = T.q, T.n, T.h, T.trace
    assert p + 1 - t == h * n
    nums = {"4p-t^2": 4*p - t*t, "twist": p + 1 + t, "n-1": n-1, "n+1": n+1, "p-1": p-1, "p+1": p+1}
    rec = {"name": T.name, "p_bits": p.bit_length(), "t": str(t)}
    for k, N in nums.items():
        rec[k] = fac(N) if N > 1 else {"status": "FF", "factors": []}
    out.write(json.dumps(rec) + "\n"); out.flush()
    cf = [k for k in nums if rec[k]["status"] != "FF"]
    print(T.name, "all FF" if not cf else "unfactored: " + ", ".join(f"{k}(C{max(rec[k]['composite_digits'] or [0])})" for k in cf), flush=True)
