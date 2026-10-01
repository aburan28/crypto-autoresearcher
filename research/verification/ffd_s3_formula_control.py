"""Verify the third Semaev summation polynomial for binary curves
   E: y^2 + x*y = x^3 + a2*x^2 + a6  over F_{2^n},
by checking S_3(x_P, x_Q, x_{P+Q}) == 0 against real point arithmetic.

Claimed:  S_3(X1,X2,X3) = (X1X2 + X1X3 + X2X3)^2 + X1X2X3 + a6
"""
import random
MODS={2:0b111,3:0b1011,4:0b10011,5:0b100101,6:0b1000011,7:0b10000011,
      8:0b100011101,9:0b1000010001,10:0b10000001001}

def mul(a,b,n):
    m=MODS[n]; r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if (a>>n)&1: a^=m
    return r
def inv(a,n):
    # brute force for small n
    for c in range(1,1<<n):
        if mul(a,c,n)==1: return c
    raise ZeroDivisionError
def sq(a,n): return mul(a,a,n)

def on_curve(P,a2,a6,n):
    if P is None: return True
    x,y=P
    return (sq(y,n)^mul(x,y,n)) == (mul(x,sq(x,n),n) ^ mul(a2,sq(x,n),n) ^ a6)

def neg(P,n):
    if P is None: return None
    x,y=P; return (x, x^y)

def add(P,Q,a2,a6,n):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2 and (y1^y2)==x1 and x1!=0: return None   # Q == -P
    if P==Q:
        if x1==0: return None
        lam = x1 ^ mul(y1,inv(x1,n),n)
        x3 = sq(lam,n)^lam^a2
        y3 = sq(x1,n) ^ mul(lam^1,x3,n)
        return (x3,y3)
    lam = mul(y1^y2, inv(x1^x2,n), n)
    x3 = sq(lam,n)^lam^x1^x2^a2
    y3 = mul(lam,x1^x3,n)^x3^y1
    return (x3,y3)

def points(a2,a6,n):
    pts=[]
    for x in range(1<<n):
        for y in range(1<<n):
            if on_curve((x,y),a2,a6,n): pts.append((x,y))
    return pts

def S3(x1,x2,x3,a6,n):
    e2 = mul(x1,x2,n) ^ mul(x1,x3,n) ^ mul(x2,x3,n)
    e3 = mul(mul(x1,x2,n),x3,n)
    return sq(e2,n) ^ e3 ^ a6

random.seed(7)
total=0; ok=0; bad=[]
for n in (3,4,5):
    for a2 in (0,1):
        a6=1
        while not any(on_curve((x,y),a2,a6,n) for x in range(1<<n) for y in range(1<<n)):
            a6+=1
        P_all=points(a2,a6,n)
        if len(P_all)<4: continue
        for _ in range(120):
            P=random.choice(P_all); Q=random.choice(P_all)
            R=add(P,Q,a2,a6,n)
            if R is None: continue
            # P + Q + (-R) = O  -> the three x-coords satisfy S_3
            x1,x2,x3 = P[0],Q[0],neg(R,n)[0]
            v=S3(x1,x2,x3,a6,n)
            total+=1
            if v==0: ok+=1
            else: bad.append((n,a2,a6,x1,x2,x3,v))
print(f"S_3 vanishing on genuine decompositions: {ok}/{total}")
if bad:
    print("FAILURES (first 3):", bad[:3])
else:
    print("no failures -- formula (X1X2+X1X3+X2X3)^2 + X1X2X3 + a6 CONFIRMED")

# negative control: S_3 should NOT vanish on random unrelated triples
neg_hits=0; neg_tot=0
for n in (4,5):
    a2,a6=1,1
    for _ in range(400):
        x1,x2,x3=[random.randrange(1<<n) for _ in range(3)]
        neg_tot+=1
        if S3(x1,x2,x3,a6,n)==0: neg_hits+=1
print(f"negative control: random triples with S_3 == 0: {neg_hits}/{neg_tot} "
      f"(expect ~1/2^n, i.e. a few percent -- NOT ~0 and NOT ~all)")
