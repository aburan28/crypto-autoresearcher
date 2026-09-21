"""
Validator J2 -- fresh, independent, BLIND (not having read CORR-20260905-783157.yaml).

Hand-derivation performed first (see validator's own report text); this script is the
mechanical cross-check of that hand derivation, enumerating all 8 x 2 = 16 sign cases.

Setup (my own bookkeeping, derived from the verbatim code):
  u = chi(e1-e2), v = chi(e1-e3), w = chi(e2-e3)   (roots list is [e1,e2,e3], 0-indexed
  in the code as roots[0],roots[1],roots[2])

  code index i=0 (1st root): j,k = 1,2 -> a=chi(e1-e2)=u,              b=chi(e1-e3)=v
  code index i=1 (2nd root): j,k = 0,2 -> a=chi(e2-e1)=chi(-1)*u,      b=chi(e2-e3)=w
  code index i=2 (3rd root): j,k = 0,1 -> a=chi(e3-e1)=chi(-1)*v,      b=chi(e3-e2)=chi(-1)*w

  hp += 1 if a==1 and b==1 (per index); hm += 1 if a==-1 and b==-1 (per index).
"""

def h_pair_from_uvw(u, v, w, neg1):
    """Reimplementation of h_pair_from_characters's own exact logic,
    expressed directly in terms of u,v,w and chi(-1) (=neg1), derived
    independently (not copied) from the verbatim code in the handoff."""
    hp = hm = 0
    triples = [
        (u, v),               # index i=0 (1st root)
        (neg1 * u, w),        # index i=1 (2nd root)
        (neg1 * v, neg1 * w), # index i=2 (3rd root)
    ]
    for a, b in triples:
        if a == 1 and b == 1:
            hp += 1
        elif a == -1 and b == -1:
            hm += 1
    return hp, hm

for neg1, label in [(1, "p=1mod4 (chi(-1)=+1)"), (-1, "p=3mod4 (chi(-1)=-1)")]:
    print(f"=== {label} ===")
    achievable = {}
    for u in (1, -1):
        for v in (1, -1):
            for w in (1, -1):
                hp, hm = h_pair_from_uvw(u, v, w, neg1)
                achievable.setdefault((hp, hm), []).append((u, v, w))
    for pair, cases in sorted(achievable.items()):
        print(f"  (hp,hm)={pair}  <- (u,v,w) cases: {cases}")
    print(f"  ACHIEVABLE SET: {sorted(achievable.keys())}")
    print()

# proves-too-much control: u=v=w=+1 under chi(-1)=+1 must give (3,0)
hp, hm = h_pair_from_uvw(1, 1, 1, 1)
print(f"PROVES-TOO-MUCH CONTROL: u=v=w=+1, chi(-1)=+1 -> (hp,hm) = ({hp},{hm})  "
      f"(expected (3,0)): {'PASS' if (hp,hm)==(3,0) else 'FAIL'}")
