# Free 2-relations among base points: count z in V with S3(u,v,z)=0 for some u!=v in V; compare with random-model expectation.
import time
p = next_prime(2^20); F = GF(p); R.<z> = PolynomialRing(F)
g = F.multiplicative_generator()
for (aa,bb,label) in [(F(0),F(7),"j0 a=0 b=7"), (F.random_element(),F.random_element(),"random a,b")]:
    def S3(u,v,w):
        return (u-v)^2*w^2 - 2*((u+v)*(u*v+aa)+2*bb)*w + (u*v-aa)^2 - 4*bb*(u+v)
    B = 400
    # subgroup of order dividing p-1 closest to 400
    divs = [d for d in divisors(p-1) if 300 <= d <= 600]
    Bsub = divs[0] if divs else None
    bases = [([F(i) for i in range(B)], f"interval [0,{B})")]
    if Bsub: 
        h = g^((p-1)//Bsub); bases.append(([h^i for i in range(Bsub)], f"subgroup mu_{Bsub}"))
    for V,name in bases:
        t0=time.time(); Bv=len(V)
        Psi = prod(S3(u,v,z) for u in V for v in V if u != v)
        gcdV = Psi.gcd(prod(z - v for v in V)).degree()
        exp_cnt = float(Bv*(Bv-1)*Bv/p)   # ~1 F_p-root per ordered pair on average, prob Bv/p each lands in V
        print(f"{label:14s} {name:20s}: roots in V {gcdV}, random-model expectation ~{exp_cnt:.1f}, {time.time()-t0:.1f}s")
