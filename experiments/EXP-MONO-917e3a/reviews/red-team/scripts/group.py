from itertools import permutations, product

def V_classes(n):           # V = F_2^n / <all-ones>, n = m-1
    seen=set(); reps=[]
    for v in product([0,1],repeat=n):
        c=tuple(1-a for a in v)
        if v in seen or c in seen: continue
        seen.add(v); seen.add(c); reps.append(frozenset([v,c]))
    return reps

def act(pi, cls, n):
    out=set()
    for v in cls:
        w=[0]*n
        for i in range(n): w[pi[i]] = v[i]     # permute coordinates
        out.add(tuple(w))
    # close under complement
    full=set()
    for w in out:
        full.add(w); full.add(tuple(1-a for a in w))
    for c in V_classes(n):
        if set(c) <= full: return c
    raise RuntimeError

for m in (3,4,5):
    n=m-1
    cls=V_classes(n)
    print(f"m={m}: |V| = {len(cls)}  (expect 2^(m-2) = {2**(m-2)})")
    imgs={}
    for pi in permutations(range(n)):
        perm=tuple(cls.index(act(pi,c,n)) for c in cls)
        imgs.setdefault(perm,[]).append(pi)
    trivial=tuple(range(len(cls)))
    kernel=imgs.get(trivial,[])
    print(f"   |S_(m-1)| = {len(list(permutations(range(n))))}, image size = {len(imgs)}, kernel size = {len(kernel)}")
    print(f"   injective? {len(kernel)==1}   kernel elements: {kernel}")
    # Aut(V) order = |GL_{m-2}(F_2)|
    d=m-2
    g=1
    for i in range(d): g *= (2**d - 2**i)
    print(f"   |Aut(V)| = |GL_{d}(F_2)| = {g};  surjective? {len(imgs)==g}")
    print(f"   claimed |V x| S_(m-1)| = {2**(m-2)}*{len(list(permutations(range(n))))} = {2**(m-2)*len(list(permutations(range(n))))}"
          f" ;  |Sym(2^(m-2))| = {__import__('math').factorial(2**(m-2))}")
    if 2**(m-2)*len(list(permutations(range(n)))) > __import__('math').factorial(2**(m-2)):
        print("   *** IMPOSSIBLE as a faithful permutation group on the roots ***")
    print(f"   ACTUAL image of V x| S_(m-1) in Sym(roots) has order "
          f"{2**(m-2)*len(imgs)} (translations x image of S_(m-1))")
    print()
