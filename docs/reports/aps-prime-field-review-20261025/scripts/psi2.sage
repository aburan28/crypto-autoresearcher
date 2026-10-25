# Sparsity / structure check of Psi_2(z) = prod_{x1,x2 in V} S3(x1,x2,z) for subgroup and interval V.
import time
p = 65537; F = GF(p); R.<z> = PolynomialRing(F)
a = F(0); b = F(7)   # j=0 curve like secp256k1; also try random
for (aa,bb,label) in [(F(0),F(7),"j0 a=0 b=7"), (F.random_element(),F.random_element(),"random a,b")]:
    def S3(u,v,w):
        return (u-v)^2*w^2 - 2*((u+v)*(u*v+aa)+2*bb)*w + (u*v-aa)^2 - 4*bb*(u+v)
    B = 64
    g = F.multiplicative_generator(); h = g^((p-1)//B)
    muB = [h^i for i in range(B)]
    interval = [F(i) for i in range(B)]
    for V,name in [(muB,"subgroup mu_64"),(interval,"interval [0,64)")]:
        t0=time.time()
        facs = [S3(u,v,z) for u in V for v in V if u != v]
        Psi = prod(facs)
        nz = sum(1 for c in Psi.list() if c != 0)
        # structure probes: gcd with z^B-1 (roots in V), number of roots in F_p, is Psi a poly in z^k?
        roots_in_Fp = len(Psi.roots(multiplicities=False))
        gcdV = Psi.gcd(prod(z - v for v in V)).degree()
        print(f"{label:14s} {name:18s}: deg {Psi.degree()}, nonzero coeffs {nz} of {Psi.degree()+1}, roots in F_p {roots_in_Fp}, roots in V {gcdV}, {time.time()-t0:.1f}s")
