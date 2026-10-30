"""Published field/curve constants; see sources.json for primary references."""
def hx(s):return int(s.replace(' ',''),16)

CURVES=[
 dict(name='P-224',p=2**224-2**96+1,a=-3,
      b=hx('b4050a85 0c04b3ab f5413256 5044b0b7 d7bfd8ba 270b3943 2355ffb4'),
      r=hx('ffffffff ffffffff ffffffff ffff16a2 e0b8f03e 13dd2945 5c5c2a3d'),h=1,mode='split',S=64),
 dict(name='P-256',p=2**256-2**224+2**192+2**96-1,a=-3,
      b=hx('5ac635d8 aa3a93e7 b3ebbd55 769886bc 651d06b0 cc53b0f6 3bce3c3e 27d2604b'),
      r=hx('ffffffff 00000000 ffffffff ffffffff bce6faad a7179e84 f3b9cac2 fc632551'),h=1,mode='torus',S=64),
 dict(name='P-384',p=2**384-2**128-2**96+2**32-1,a=-3,
      b=hx('b3312fa7 e23ee7e4 988e056b e3f82d19 181d9c6e fe814112 0314088f 5013875a c656398d 8a2ed19d 2a85c8ed d3ec2aef'),
      r=hx('ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff c7634d81 f4372ddf 581a0db2 48b0a77a ecec196a ccc52973'),h=1,mode='torus',S=64),
 dict(name='P-521',p=2**521-1,a=-3,
      b=hx('0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00'),
      r=hx('01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409'),h=1,mode='torus',S=64),
 dict(name='secp256k1',p=2**256-2**32-977,a=0,b=7,
      r=hx('ffffffff ffffffff ffffffff fffffffe baaedce6 af48a03b bfd25e8c d0364141'),h=1,mode='torus',S=16),
]
for name,p,A,r,h in [
 ('Curve25519',2**255-19,486662,2**252+hx('14def9dea2f79cd65812631a5cf5d3ed'),8),
 ('Curve448',2**448-2**224-1,156326,2**446-hx('8335dc163bb124b65129c96fde933d8d723a70aadc873d6d54a7bb0d'),4)]:
    inv3=pow(3,-1,p)
    CURVES.append(dict(name=name,p=p,a=(1-A*A*inv3)%p,
                       b=(2*A**3*pow(27,-1,p)-A*inv3)%p,r=r,h=h,
                       montgomery_A=A,mode='torus' if name=='Curve448' else 'split',
                       S=64 if name=='Curve448' else 4))

def valuation2(n):return (n&-n).bit_length()-1
