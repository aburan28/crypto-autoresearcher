#!/usr/bin/env python3
"""Independent pure-Python reduced-round AES-128 reference + 3-way pin.
Compares: (a) FIPS-197 C.1 KAT, (b) pycryptodome at r=10, (c) C AES-NI dumps
at r=1..10 in BOTH directions, (d) round-trip.  No code shared with yoyo6.c."""
import sys, json, subprocess

SB=[0]*256; ISB=[0]*256
def _init():
    p=q=1
    sbox=[0]*256
    while True:
        p = p ^ ((p<<1)&0xff) ^ (0x1b if p&0x80 else 0)
        q ^= q<<1; q&=0xff; q ^= q<<2; q&=0xff; q ^= q<<4; q&=0xff
        if q&0x80: q^=0x09
        x = q ^ ((q<<1)|(q>>7)) ^ ((q<<2)|(q>>6)) ^ ((q<<3)|(q>>5)) ^ ((q<<4)|(q>>4))
        sbox[p] = (x^0x63)&0xff
        if p==1: break
    sbox[0]=0x63
    for i in range(256):
        SB[i]=sbox[i]; ISB[sbox[i]]=i
_init()
def xt(a): return ((a<<1)^0x1b)&0xff if a&0x80 else (a<<1)
def mul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a=xt(a); b>>=1
    return r
def keyexp(key):
    w=[list(key[4*i:4*i+4]) for i in range(4)]
    rc=1
    for i in range(4,44):
        t=list(w[i-1])
        if i%4==0:
            t=t[1:]+t[:1]; t=[SB[x] for x in t]; t[0]^=rc; rc=xt(rc)
        w.append([w[i-4][j]^t[j] for j in range(4)])
    return [bytes(b for c in w[4*i:4*i+4] for b in c) for i in range(11)]
def ark(s,k): return bytes(a^b for a,b in zip(s,k))
def sub(s,box): return bytes(box[b] for b in s)
def sr(s):
    o=[0]*16
    for c in range(4):
        for t in range(4): o[4*c+t]=s[4*((c+t)%4)+t]
    return bytes(o)
def isr(s):
    o=[0]*16
    for c in range(4):
        for t in range(4): o[4*((c+t)%4)+t]=s[4*c+t]
    return bytes(o)
def mc(s):
    o=[0]*16
    for c in range(4):
        a=s[4*c:4*c+4]
        o[4*c+0]=mul(a[0],2)^mul(a[1],3)^a[2]^a[3]
        o[4*c+1]=a[0]^mul(a[1],2)^mul(a[2],3)^a[3]
        o[4*c+2]=a[0]^a[1]^mul(a[2],2)^mul(a[3],3)
        o[4*c+3]=mul(a[0],3)^a[1]^a[2]^mul(a[3],2)
    return bytes(o)
def imc(s):
    o=[0]*16
    for c in range(4):
        a=s[4*c:4*c+4]
        o[4*c+0]=mul(a[0],14)^mul(a[1],11)^mul(a[2],13)^mul(a[3],9)
        o[4*c+1]=mul(a[0],9)^mul(a[1],14)^mul(a[2],11)^mul(a[3],13)
        o[4*c+2]=mul(a[0],13)^mul(a[1],9)^mul(a[2],14)^mul(a[3],11)
        o[4*c+3]=mul(a[0],11)^mul(a[1],13)^mul(a[2],9)^mul(a[3],14)
    return bytes(o)
def E(key,p,r):
    rk=keyexp(key); s=ark(p,rk[0])
    for i in range(1,r): s=ark(mc(sr(sub(s,SB))),rk[i])
    return ark(sr(sub(s,SB)),rk[r])
def D(key,c,r):
    rk=keyexp(key); s=sub(isr(ark(c,rk[r])),ISB)
    for i in range(r-1,0,-1): s=sub(isr(imc(ark(s,rk[i]))),ISB)
    return ark(s,rk[0])

def main():
    exe=sys.argv[1]
    out=subprocess.run([exe,"pin"],capture_output=True,text=True).stdout.strip().split("\n")
    res={"kat":None,"enc_mismatch":0,"dec_mismatch":0,"roundtrip_fail":0,
         "pycrypto_mismatch":0,"vectors":0,"involution":None}
    # FIPS-197 C.1
    fk=bytes(range(16)); fp=bytes.fromhex("00112233445566778899aabbccddeeff")
    expected="69c4e0d86a7b0430d8cdb78070b4c55a"
    mine=E(fk,fp,10).hex()
    res["kat_python_ref"]=mine
    res["kat_expected_fips197"]=expected
    res["kat_python_ok"]= (mine==expected)
    from Crypto.Cipher import AES
    res["kat_pycryptodome"]=AES.new(fk,AES.MODE_ECB).encrypt(fp).hex()
    for ln in out:
        f=ln.split()
        if f[0]=="KAT":
            res["kat"]=f[1]; res["kat_c_ok"]=(f[1]==expected)
        elif f[0]=="V":
            r=int(f[1]); k=bytes.fromhex(f[2]); p=bytes.fromhex(f[3]); c=bytes.fromhex(f[4])
            res["vectors"]+=1
            if E(k,p,r)!=c: res["enc_mismatch"]+=1
            if D(k,c,r)!=p: res["roundtrip_fail"]+=1
            if f[5]!="rtOK": res["roundtrip_fail"]+=1
            if r==10 and AES.new(k,AES.MODE_ECB).encrypt(p)!=c: res["pycrypto_mismatch"]+=1
        elif f[0]=="D":
            r=int(f[1]); k=bytes.fromhex(f[2]); c=bytes.fromhex(f[3]); p=bytes.fromhex(f[4])
            if D(k,c,r)!=p: res["dec_mismatch"]+=1
            if E(k,p,r)!=c: res["dec_mismatch"]+=1
            if r==10 and AES.new(k,AES.MODE_ECB).decrypt(c)!=p: res["pycrypto_mismatch"]+=1
        elif f[0]=="INVOL":
            res["involution"]={"tested":int(f[2]),"bad":int(f[4])}
    res["PASS"]= (res["kat_c_ok"] and res["kat_python_ok"]
                  and res["kat_pycryptodome"]==expected
                  and res["enc_mismatch"]==0 and res["dec_mismatch"]==0
                  and res["roundtrip_fail"]==0 and res["pycrypto_mismatch"]==0)
    print(json.dumps(res,indent=1))
main()
