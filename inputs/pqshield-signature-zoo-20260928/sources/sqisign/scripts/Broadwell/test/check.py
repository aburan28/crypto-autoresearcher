import sys
c, t, N = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
p = c*(1<<t) - 1
bits = p.bit_length()
R = 1 << (64*N)
Rinv = pow(R, -1, p)
LIM = 1 << bits

cur, bad, cnt, invop = {}, {}, {}, {}
inv_bad = inv_n = 0
for line in sys.stdin:
    k, v = line.split()
    v = int(v, 16)
    cur[k] = v
    if k in ('add','sub','mul','sqr','m0','m1','s0','s1'):
        a, b = cur.get('a',0), cur.get('b',0)
        A0,A1,B0,B1 = cur.get('A0',0),cur.get('A1',0),cur.get('B0',0),cur.get('B1',0)
        exp = {'add':a+b, 'sub':a-b, 'mul':a*b*Rinv, 'sqr':a*a*Rinv,
               'm0':(A0*B0-A1*B1)*Rinv, 'm1':(A0*B1+A1*B0)*Rinv,
               's0':(A0+A1)*(A0-A1)*Rinv, 's1':2*A0*A1*Rinv}[k]
        cnt[k] = cnt.get(k,0)+1
        if (v-exp) % p != 0: bad[k] = bad.get(k,0)+1
        inv_n += 1
        if v >= LIM:
            inv_bad += 1; invop[k] = invop.get(k,0)+1
if inv_n == 0:
    print("  NO OUTPUT - harness crashed"); sys.exit(2)
for op in ('add','sub','mul','sqr','m0','m1','s0','s1'):
    n, e = cnt.get(op,0), bad.get(op,0)
    print("  %-4s %6d checks  %s" % (op, n, "OK" if e==0 else "FAIL %d"%e))
print("  invariant v < 2^%d: %d/%d hold" % (bits, inv_n-inv_bad, inv_n))
if invop: print("    out-of-domain by op:", dict(sorted(invop.items())))
sys.exit(1 if sum(bad.values()) else 0)
