#!/usr/bin/env python3
"""Parser tests (W2): precedence, trailing comma, constant term, idempotence, cancellation, raw-vs-B evaluation."""
import os, sys, tempfile, itertools, random
sys.path.insert(0, os.path.dirname(__file__))
from msparse import *

def write(txt):
    fd, p = tempfile.mkstemp(suffix='.ms', dir=os.environ.get('TMPDIR','.'))
    os.write(fd, txt.encode()); os.close(fd); return p

fails = 0
def check(name, cond):
    global fails
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond: fails += 1

# T1 precedence: a+b*c is {a, bc}; (not (a+b)*c = {ac, bc})
p = write("a,b,c\n2\na+b*c,\nb+c\n")
N,B,R,info = parse_ms(p)
check('precedence a+b*c = {a,bc}', B[0] == frozenset({0b001, 0b110}))
check('last poly without trailing comma', B[1] == frozenset({0b010, 0b100}) and info['n_polys_total']==2)
os.remove(p)
# T2 trailing comma tolerated (and constant)
p = write("a,b\n2\n1+a*b,\na+1,\n")
N,B,R,info = parse_ms(p)
check('trailing comma tolerated, 2 polys', len(B)==2 and info['n_empty_tail']==1)
check('constant 1 is the empty monomial', B[0]==frozenset({0,0b11}) and B[1]==frozenset({0,0b01}))
os.remove(p)
# T3 idempotence, cancellation, field lines are zero in B
p = write("a,b\n2\na^2+a,\nb^2+b,\na*a*b+a*b,\na+a+b,\nb*a+a*b+1\n")
N,B,R,info = parse_ms(p, drop_field_lines=False)
check('a^2+a == 0 in B', len(B[0])==0 and len(B[1])==0)
check('a*a*b+a*b == 0 in B', len(B[2])==0)
check('a+a+b == b (repeated term cancels)', B[3]==frozenset({0b10}))
check('b*a+a*b+1 == 1', B[4]==frozenset({0}))
check('field-line detection', info['n_field_lines']==2 and info['n_nonfield']==3)
N,B2,R2,info2 = parse_ms(p, drop_field_lines=True)
check('drop_field_lines keeps the other 3 polys', len(B2)==3)
os.remove(p)
# T4 raw evaluation == B evaluation on all points, random polys written with powers
random.seed(5)
names = ['x%d' % i for i in range(1,7)]
for trial in range(200):
    terms=[]
    for _ in range(random.randint(1,8)):
        k=random.randint(0,3)
        fac=[random.choice(names)+random.choice(['','','^2','^3']) for _ in range(k)]
        terms.append('*'.join(fac) if fac else '1')
    s='+'.join(terms)
    p = write(','.join(names)+"\n2\n"+s+"\n")
    N,B,R,info = parse_ms(p, drop_field_lines=False)
    os.remove(p)
    ok=all(eval_B(B[0],a)==eval_raw(R[0],a) for a in range(64))
    # independent reference: python evaluation of the string with ints mod 2
    def ref(a):
        env={n:(a>>i)&1 for i,n in enumerate(names)}
        return eval(s.replace('^','**'), {}, env) % 2
    ok = ok and all(ref(a)==eval_B(B[0],a) for a in range(64))
    if not ok:
        check('random power-polynomial %r' % s, False); break
else:
    check('200 random polys with ^2,^3, products: B-eval == raw-eval == python eval', True)
print('FAILS', fails)
sys.exit(1 if fails else 0)
