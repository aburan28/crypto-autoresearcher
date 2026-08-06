# Independent AES-128 reference written for TASK-20260802-447db8.
# Not copied from cnt.c / sq_null.c / count5.c. Used to (a) produce the 176-byte
# round-key expansion count5.c needs, (b) pin the r-round C1 ciphertext.
SB=[None]*256
def _mk():
    p=q=1; sb=[0]*256
    while True:
        p = p ^ ((p<<1)&0xff) ^ (0x1b if p&0x80 else 0)
        q ^= q<<1; q^=q<<2; q^=q<<4; q&=0xff
        if q&0x80: q^=0x09
        x = q ^ ((q<<1)|(q>>7)) ^ ((q<<2)|(q>>6)) ^ ((q<<3)|(q>>5)) ^ ((q<<4)|(q>>4))
        sb[p]= (x^0x63)&0xff
        if p==1: break
    sb[0]=0x63
    return sb
SB=_mk()
def xt(a): return ((a<<1)^0x1b)&0xff if a&0x80 else (a<<1)
def gm(a,b):
    r=0
    for i in range(8):
        if b&1: r^=a
        a=xt(a); b>>=1
    return r
def expand(key):
    rk=list(key); rcon=1
    for i in range(16,176,4):
        t=rk[i-4:i]
        if i%16==0:
            t=[SB[t[1]]^rcon,SB[t[2]],SB[t[3]],SB[t[0]]]
            rcon=xt(rcon)
        rk += [rk[i-16+j]^t[j] for j in range(4)]
    return rk
def encr(pt,rk,r):
    s=[pt[i]^rk[i] for i in range(16)]
    for rnd in range(1,r+1):
        s=[SB[b] for b in s]
        # ShiftRows: state byte 4c+row -> row r shifted left by r
        t=[0]*16
        for c in range(4):
            for row in range(4):
                t[4*c+row]=s[4*((c+row)%4)+row]
        s=t
        if rnd!=r:  # C1: final round has no mixing layer
            t=[0]*16
            for c in range(4):
                col=s[4*c:4*c+4]
                t[4*c+0]=gm(2,col[0])^gm(3,col[1])^col[2]^col[3]
                t[4*c+1]=col[0]^gm(2,col[1])^gm(3,col[2])^col[3]
                t[4*c+2]=col[0]^col[1]^gm(2,col[2])^gm(3,col[3])
                t[4*c+3]=gm(3,col[0])^col[1]^col[2]^gm(2,col[3])
            s=t
        s=[s[i]^rk[16*rnd+i] for i in range(16)]
    return s
def hx(b): return ''.join('%02x'%x for x in b)
def uh(h): return [int(h[2*i:2*i+2],16) for i in range(len(h)//2)]
if __name__=='__main__':
    import sys,json
    # FIPS-197 C.1 known-answer, full 10 rounds
    k=uh('000102030405060708090a0b0c0d0e0f'); p=uh('00112233445566778899aabbccddeeff')
    kat=hx(encr(p,expand(k),10))
    KEY='2b7e151628aed2a6abf7158809cf4f3c'
    BASE='00112233445566778899aabbccddeeff'
    rk=expand(uh(KEY))
    out={'sbox_sha_check':hx(SB[:16]),
         'fips197_c1_expect':'69c4e0d86a7b0430d8cdb78070b4c55a','fips197_c1_got':kat,
         'fips197_c1_pass': kat=='69c4e0d86a7b0430d8cdb78070b4c55a',
         'anchor_key':KEY,'anchor_rk176':hx(rk),
         'pin_pt':BASE,'pin_r5_ct':hx(encr(uh(BASE),rk,5)),
         'pin_r10_ct':hx(encr(uh(BASE),rk,10))}
    print(json.dumps(out,indent=1))
