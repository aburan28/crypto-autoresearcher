"""Recover interval factors from supplied idempotents, without root enumeration."""
import quotient as q


def column_basis(M, p):
    if not M or not M[0]:
        return [[] for _ in M]
    pivots = {}; originals = []
    for j in range(len(M[0])):
        original = [row[j] for row in M]; v = original[:]
        for i, w in sorted(pivots.items()):
            c = v[i]
            v = [(a-c*b) % p for a, b in zip(v, w)]
        i = next((i for i, a in enumerate(v) if a), None)
        if i is not None:
            c = q.inv(v[i], p); pivots[i] = [a*c % p for a in v]
            originals.append(original)
    return [[v[i] for v in originals] for i in range(len(M))]


def check_factor_certificate(U, certificate):
    p, u = q.modulus(U)
    q.require(type(certificate) is dict and set(certificate) == {'p','t','s','factors'}, 'factor certificate shape')
    q.require(certificate['p'] == p and type(certificate['p']) is int, 'factor field binding')
    t, s = certificate['t'], certificate['s']; q.interval(p,t,s)
    factors = certificate['factors']; q.require(type(factors) is list, 'factor list')
    last = -1; total = 0; product = [1]
    for pair in factors:
        q.require(type(pair) is list and len(pair) == 2, 'factor pair')
        x, m = pair; q.scalar(x,p); q.integer(m,'positive integer multiplicity',1)
        q.require(x > last, 'distinct sorted factor coordinates'); last = x
        q.require((x-t) % p < (1 << s), 'factor interval membership')
        total += m; q.require(total <= len(u)-1, 'factor degree bound')
        for _ in range(m):
            product = q.mul(product,[(-x)%p,1],p)
    q.require(total == len(u)-1 and product == u, 'independent factor product')
    return True


def recover_interval_factors(U,t,s,e):
    q.event('projector_recovery'); q.verify_quotient_witness(U,t,s,e)
    p,u = q.modulus(U); k=len(u)-1
    spaces = [([[int(i==j) for j in range(k)] for i in range(k)],0)] if k else []
    for bit,v in enumerate(e):
        columns=[q.rem([0]*j+v,u,p) for j in range(k)]
        E=[[col[i] if i<len(col) else 0 for col in columns] for i in range(k)]
        next_spaces=[]
        for V,label in spaces:
            for value in [0,1]:
                W=[[(sum(((E[i][a] if value else int(i==a)-E[i][a]))*V[a][b]
                           for a in range(k))) % p for b in range(len(V[0]))] for i in range(k)]
                B=column_basis(W,p)
                if B and B[0]:next_spaces.append((B,label+value*(1<<bit)))
        spaces=next_spaces
        q.require(sum(len(V[0]) for V,_ in spaces)==k,'projector dimension preservation')
        q.event('projector_depth'); q.event('projector_nonzero_spaces',len(spaces))
    factors=sorted([[(t+label)%p,len(V[0])] for V,label in spaces])
    certificate={'p':p,'t':t,'s':s,'factors':factors}
    check_factor_certificate(U,certificate)
    return certificate
