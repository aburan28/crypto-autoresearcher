import os, re
txt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'binary-curve-params.txt')).read()
blocks = re.split(r'===== (\S+) =====', txt)[1:]
pairs = list(zip(blocks[0::2], blocks[1::2]))

def blob(body, label):
    m = re.search(re.escape(label)+r':\s*\n((?:\s+[0-9a-f:]+\n)+)', body)
    if m:
        return int(re.sub(r'[^0-9a-f]','',m.group(1)), 16)
    m = re.search(re.escape(label)+r':\s*(\d+)(?:\s*\(0x[0-9a-fA-F]+\))?\s*\n', body)   # "A:    0"
    if m: return int(m.group(1))
    return None

def clmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1; b>>=1
    return r
def red(a,f):
    fb=f.bit_length()-1
    while a.bit_length()-1>=fb: a^=f<<(a.bit_length()-1-fb)
    return a
def sq(a,f): return red(clmul(a,a),f)
def in_sub(a,d,f):
    x=a
    for _ in range(d): x=sq(x,f)
    return x==a

for name, body in pairs:
    if 'characteristic-two-field' not in body: continue
    f=blob(body,'Polynomial'); A=blob(body,'A'); B=blob(body,'B')
    order=blob(body,'Order'); cm=re.search(r'Cofactor:\s*(\d+)',body)
    cof=int(cm.group(1)) if cm else None
    m=f.bit_length()-1
    if m in (163,191,193,233,239,283,359,409,431,571,131): continue
    d=16; k=m//d
    okA = (A==0) or in_sub(A,d,f); okB = (B==0) or in_sub(B,d,f)
    N = cof*order
    # trace over F_{2^16} implied by the cofactor, then check the k-th extension count
    q=2**d; t=q+1-cof
    s0,s1=2,t
    for _ in range(k-1): s0,s1 = s1, t*s1-q*s0
    Nk = q**k + 1 - s1
    print(f"{name}: m={m}=16*{k}  A in F_2^16: {okA}  B in F_2^16: {okB}")
    print(f"    cofactor={cof} -> t={t} (|t|<=2*sqrt(q)={2*2**(d//2)}: {abs(t)<=2*2**(d//2)})")
    print(f"    #E(F_2^{m}) from subfield trace == cofactor*order : {Nk==N}   (order is {order.bit_length()} bits, prime-ish subgroup)")
