# Pure-Python AES-128 written from FIPS-197 by the validator. No pycryptodome,
# no repo code. Reduced-round convention: s^=RK0; rounds 1..r-1 full; round r
# = SB,SR,ARK (no MixColumns).
import sys, json
def gmul(a,b):
    p=0
    for _ in range(8):
        if b&1: p^=a
        hi=a&0x80; a=(a<<1)&0xff
        if hi: a^=0x1b
        b>>=1
    return p
def ginv(a):
    if a==0: return 0
    r=1
    for _ in range(254): r=gmul(r,a)
    return r
def sbox_byte(x):
    b=ginv(x); o=0
    for i in range(8):
        bit=((b>>i)&1)^((b>>((i+4)%8))&1)^((b>>((i+5)%8))&1)^((b>>((i+6)%8))&1)^((b>>((i+7)%8))&1)^((0x63>>i)&1)
        o|=bit<<i
    return o
SB=[sbox_byte(x) for x in range(256)]
RCON=[0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]
def expand(key):
    w=[list(key[4*i:4*i+4]) for i in range(4)]
    for i in range(4,44):
        t=list(w[i-1])
        if i%4==0:
            t=t[1:]+t[:1]; t=[SB[x] for x in t]; t[0]^=RCON[i//4-1]
        w.append([w[i-4][j]^t[j] for j in range(4)])
    return [[b for c in range(4) for b in w[4*r+c]] for r in range(11)]
def enc(pt,key,r):
    rk=expand(key); s=[pt[i]^rk[0][i] for i in range(16)]
    for rd in range(1,r+1):
        s=[SB[b] for b in s]
        # ShiftRows: state[row][col]=s[4*col+row], row t rotated left by t
        t=[0]*16
        for col in range(4):
            for row in range(4):
                t[4*col+row]=s[4*((col+row)%4)+row]
        s=t
        if rd!=r:
            o=[0]*16
            for col in range(4):
                a=s[4*col:4*col+4]
                o[4*col+0]=gmul(a[0],2)^gmul(a[1],3)^a[2]^a[3]
                o[4*col+1]=a[0]^gmul(a[1],2)^gmul(a[2],3)^a[3]
                o[4*col+2]=a[0]^a[1]^gmul(a[2],2)^gmul(a[3],3)
                o[4*col+3]=gmul(a[0],3)^a[1]^a[2]^gmul(a[3],2)
            s=o
        s=[s[i]^rk[rd][i] for i in range(16)]
    return bytes(s)
if __name__=='__main__':
    # FIPS-197 C.1 self test at 10 rounds
    k=bytes(range(16)); p=bytes.fromhex('00112233445566778899aabbccddeeff')
    assert enc(p,k,10).hex()=='69c4e0d86a7b0430d8cdb78070b4c55a', enc(p,k,10).hex()
    print("SELFTEST_FIPS197_OK")
    d=json.load(open(sys.argv[1])); key=bytes.fromhex(sys.argv[2]); r=int(sys.argv[3])
    pairs=d['pairs'] if 'pairs' in d else d
    ok=0; bad=0
    for e in pairs:
        p=bytes.fromhex(e['pt']); c=bytes.fromhex(e['ct'])
        if enc(p,key,r)==c: ok+=1
        else: bad+=1
    print(json.dumps({"checked":ok+bad,"match":ok,"mismatch":bad}))
