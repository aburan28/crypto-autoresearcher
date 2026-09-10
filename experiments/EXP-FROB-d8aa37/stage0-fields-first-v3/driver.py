#!/usr/bin/env python3
"""Frozen EXP-FROB-d8aa37 v3 fields-first stage0 producer. No computation on import.

Only --run-dir launches the fixed scientific panel, after adapter custody and
Linux guard checks. --self-test uses fixed F2 polynomial/matrix fixtures only.
The driver uses Sage absolute-field arithmetic behind a fully audited canonical
F2 -> F8 -> K tower isomorphism. The checker has separate nested arithmetic.
"""
import argparse
from collections import Counter, OrderedDict
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import subprocess
import time
import traceback
import zlib

EXPERIMENT = 'EXP-FROB-d8aa37'
RUN = 'RUN-FROB-b0a1f4'
SCIENCE = ('manifest.yaml', 'raw-result.json', 'fixtures.json', 'metrics.json',
           'certificates.json', 'report.md', 'roots.jsonl.gz', 'tuples.jsonl.gz')
RESERVED = ('launch.json', 'execution-receipt.json', 'command.txt', 'environment.json',
            'stdout.log', 'stderr.log', 'check.stdout.log', 'check.stderr.log')
CACHE_LIMIT = 65536
ORDER_ID = "fields_first_custom_grevlex_v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii') + b'\n'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


class Costs:
    def __init__(self):
        self.operations = Counter()
        self.stages = []

    @contextmanager
    def stage(self, name):
        w, c = time.perf_counter(), time.process_time()
        before = self.operations.copy()
        try:
            yield
        finally:
            self.stages.append(dict(name=name, wall_seconds=time.perf_counter()-w,
                cpu_seconds=time.process_time()-c,
                peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                    (1 if sys.platform == 'darwin' else 1024),
                operations=dict(self.operations-before)))


class Stream:
    def __init__(self, path, kind):
        self.path = path
        self.raw = open(path, 'xb')
        self.gz = gzip.GzipFile(filename='', mode='wb', compresslevel=6,
                                fileobj=self.raw, mtime=0)
        self.digest = hashlib.sha256()
        self.lines = self.bytes = 0
        self.put(dict(type='header', schema='frob.stage0.'+kind+'.v1', experiment=EXPERIMENT))

    def put(self, value):
        data = canonical(value)
        self.digest.update(data)
        self.bytes += len(data)
        self.lines += 1
        self.gz.write(data)

    def close(self):
        self.gz.close()
        self.raw.close()
        return dict(compressed_sha256=sha(self.path), compressed_bytes=self.path.stat().st_size,
                    decompressed_sha256=self.digest.hexdigest(), decompressed_bytes=self.bytes,
                    lines=self.lines, gzip_mtime=0, gzip_filename='', compresslevel=6,
                    zlib_version=zlib.ZLIB_VERSION, zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION)


class BoundedCache:
    def __init__(self):
        self.data = OrderedDict()
        self.hits = self.misses = self.evictions = 0

    def get(self, key, build):
        if key in self.data:
            self.hits += 1
            value = self.data.pop(key)
            self.data[key] = value
            return value, True
        self.misses += 1
        value = build()
        if len(self.data) == CACHE_LIMIT:
            self.data.popitem(last=False)
            self.evictions += 1
        self.data[key] = value
        return value, False

    def stats(self):
        return dict(limit=CACHE_LIMIT, entries=len(self.data), hits=self.hits,
                    misses=self.misses, evictions=self.evictions)


class Tower:
    """Sage representation with explicit canonical-bit embeddings, never F8(k)."""
    def __init__(self, sage, costs):
        self.s, self.cost = sage, costs
        s = sage
        R = s.PolynomialRing(s.GF(2), 'u')
        u = R.gen()
        self.f_attempts = []
        for coeff in itertools.product(range(2), repeat=3):
            f = u**3 + sum(R(coeff[i])*u**i for i in range(3))
            ok = bool(f.is_irreducible())
            costs.operations['opaque_Sage_irreducibility'] += 1
            self.f_attempts.append(dict(coefficients=list(coeff)+[1], irreducible=ok))
            if ok:
                break
        self.f = list(coeff)+[1]
        self.F = s.GF(8, 'u', modulus=f)
        self.base = [sum((self.F.gen()**i for i in range(3) if (a>>i)&1), self.F.zero())
                     for a in range(8)]
        self.base_index = {v: i for i, v in enumerate(self.base)}
        RG = s.PolynomialRing(self.F, 'z')
        z = RG.gen()
        self.g_attempts = []
        for coeff in itertools.product(range(8), repeat=3):
            g = z**3 + sum(self.base[coeff[i]]*z**i for i in range(3))
            ok = bool(g.is_irreducible())
            costs.operations['opaque_Sage_irreducibility'] += 1
            self.g_attempts.append(dict(coefficients=list(coeff)+[1], irreducible=ok))
            if ok:
                break
        self.g = list(coeff)+[1]
        # Absolute field is only a computational presentation. Its encoding is
        # never exposed as the canonical tower encoding.
        RA = s.PolynomialRing(s.GF(2), 'w')
        w = RA.gen()
        self.absolute_attempts = []
        for coeff in itertools.product(range(2), repeat=9):
            h = w**9 + sum(RA(coeff[i])*w**i for i in range(9))
            ok = bool(h.is_irreducible())
            costs.operations['opaque_Sage_irreducibility'] += 1
            self.absolute_attempts.append(dict(coefficients=list(coeff)+[1], irreducible=ok))
            if ok:
                break
        self.absolute_modulus = list(coeff)+[1]
        self.K = s.GF(512, 'w', modulus=h)
        absolute = [sum((self.K.gen()**i for i in range(9) if (a>>i)&1), self.K.zero())
                    for a in range(512)]
        abs_index = {a: i for i, a in enumerate(absolute)}
        U = next(a for a in absolute if sum((self.K(self.f[i])*a**i for i in range(4)), self.K.zero()) == 0)
        emb_base = [sum((U**i for i in range(3) if (a>>i)&1), self.K.zero()) for a in range(8)]
        Z = next(a for a in absolute if sum((emb_base[self.g[i]]*a**i for i in range(4)), self.K.zero()) == 0)
        self.values = [sum((emb_base[(a >> (3*i)) & 7]*Z**i for i in range(3)), self.K.zero())
                       for a in range(512)]
        self.index = {a: i for i, a in enumerate(self.values)}
        require(len(self.index) == 512, 'tower isomorphism is not bijective')
        self.absolute_bits = [abs_index[a] for a in self.values]
        self.embedding_matrix = [[(self.absolute_bits[1<<j] >> i)&1 for j in range(9)] for i in range(9)]
        require(s.matrix(s.GF(2), self.embedding_matrix).rank() == 9, 'singular encoding conversion')
        # Exhaustive addition and multiplication check against reduction in the
        # declared physical tower. This audit is part of future scientific cost.
        for a in range(512):
            for b in range(512):
                require(self.index[self.values[a]+self.values[b]] == (a ^ b), 'addition embedding')
                aa, bb = self.digits(a), self.digits(b)
                prod = [self.F.zero() for _ in range(5)]
                for i in range(3):
                    for j in range(3):
                        prod[i+j] += self.base[aa[i]]*self.base[bb[j]]
                for i in (4, 3):
                    for j in range(3):
                        prod[i-3+j] += prod[i]*self.base[self.g[j]]
                expected = sum(self.base_index[prod[i]] << (3*i) for i in range(3))
                require(self.index[self.values[a]*self.values[b]] == expected, 'multiplication embedding')
                costs.operations['tower_isomorphism_product_checks'] += 1
        costs.operations['opaque_Sage_tower_conversion_audits']+=1
        self.phi = s.matrix(self.F, 3, 3, lambda i,j: self.base[self.digits(self.pow(1<<(3*j),8))[i]])
        require(self.phi**3 == s.identity_matrix(self.F,3), 'Frobenius cube')
        self.normal_attempts = []
        for a in range(512):
            orbit = [self.pow(a, 8**i) for i in range(3)]
            mat = s.matrix(self.F, 3, 3, lambda i,j: self.base[self.digits(orbit[j])[i]])
            rank = int(mat.rank())
            self.normal_attempts.append(dict(candidate=a, conjugates=orbit, rank=rank))
            costs.operations['opaque_Sage_matrix_rank'] += 1
            if rank == 3:
                self.normal = a
                self.normal_matrix = mat
                break
        require(self.normal_attempts[-1]['rank'] == 3, 'no normal generator')
        self.mul_matrices = [s.matrix(self.F,3,3,lambda i,j:
            self.base[self.digits(self.mul(1<<(3*k),1<<(3*j)))[i]]) for k in range(3)]

    @staticmethod
    def digits(a):
        return [(a >> (3*i)) & 7 for i in range(3)]

    def matrix_encoding(self, mat):
        return [[self.base_index[x] for x in row] for row in mat.rows()]

    def add(self, a, b):
        self.cost.operations['K_add'] += 1
        return a ^ b

    def mul(self, a, b):
        self.cost.operations['K_multiply'] += 1
        return self.index[self.values[a]*self.values[b]]

    def pow(self, a, n):
        self.cost.operations['opaque_Sage_K_power'] += 1
        return self.index[self.values[a]**n]

    def record(self):
        return dict(f=self.f,g=self.g,f_attempts=self.f_attempts,g_attempts=self.g_attempts,
            absolute_modulus=self.absolute_modulus,absolute_attempts=self.absolute_attempts,
            canonical_to_absolute=self.absolute_bits,embedding_matrix=self.embedding_matrix,
            isomorphism_pairs_checked=512*512,phi=self.matrix_encoding(self.phi),
            normal_attempts=self.normal_attempts,normal=self.normal,
            normal_matrix=self.matrix_encoding(self.normal_matrix),
            multiplication_matrices=[self.matrix_encoding(x) for x in self.mul_matrices],
            coefficient_bitlength=3,extension_encoding_bits=9)


class Curve:
    def __init__(self, tower, A, B):
        self.t = tower
        self.A, self.B = A,B
        self.E = tower.s.EllipticCurve(tower.K, [1,tower.values[A],0,0,tower.values[B]])
        self.O = self.E(0)

    def point(self, p):
        return self.O if p is None else self.E(self.t.values[p[0]],self.t.values[p[1]])

    def enc(self, p):
        return None if p.is_zero() else (self.t.index[p[0]],self.t.index[p[1]])

    def add(self, p, q):
        self.t.cost.operations['opaque_Sage_group_add'] += 1
        return self.enc(self.point(p)+self.point(q))

    def scale(self, n, p):
        self.t.cost.operations['opaque_Sage_group_scalar_multiply'] += 1
        return self.enc(n*self.point(p))

    def neg(self,p):
        return None if p is None else (p[0],p[0]^p[1])

    def frob(self,p,k=1):
        return None if p is None else (self.t.pow(p[0],8**k),self.t.pow(p[1],8**k))

    def sum(self, points):
        out = None
        for p in points:
            out = self.add(out,p)
        return out

    def points(self, size):
        result=[]
        for x in range(size):
            xx = self.t.values[x]
            rhs = xx**3+self.t.values[self.A]*xx**2+self.t.values[self.B]
            for y in range(size):
                yy = self.t.values[y]
                self.t.cost.operations['opaque_Sage_curve_equation_evaluation'] += 1
                if yy**2+xx*yy == rhs:
                    result.append((x,y))
        return result


def bsgs_mu(curve, P, target, N):
    M = math.isqrt(N)
    if M*M < N:
        M += 1
    baby, trace = {}, []
    p = None
    for j in range(M):
        baby.setdefault(p,j)
        trace.append(dict(kind='baby',index=j,point=p))
        p = curve.add(p,P)
    step=curve.neg(curve.scale(M,P))
    q=target
    for i in range(M+1):
        trace.append(dict(kind='giant',index=i,point=q))
        if q in baby:
            mu=(i*M+baby[q])%N
            if curve.scale(mu,P)==target:
                return mu, dict(M=M,trace=trace)
        q=curve.add(q,step)
    return None,dict(M=M,trace=trace)


def select_curves(t, stream):
    selected, records, seen_j = [], [], set()
    for A,B in itertools.product(range(8),repeat=2):
        rec=dict(A=A,B=B)
        if not B:
            rec['rejection']='singular_B_zero'
        else:
            c=Curve(t,A,B)
            # For this a1=1 binary model discriminant=B and j=1/B; these
            # identities are checked against Sage rather than inferred by tags.
            rec['discriminant']=t.index[c.E.discriminant()]
            rec['j']=t.index[c.E.j_invariant()]
            require(rec['discriminant']==B and c.E.j_invariant()==1/t.values[B], 'binary invariants')
            rec['ordinary']=not bool(c.E.is_supersingular())
            t.cost.operations['opaque_Sage_supersingularity_test'] += 1
            if not rec['ordinary']:
                rec['rejection']='supersingular'
            elif rec['j'] in seen_j:
                rec['rejection']='duplicate_j'
            else:
                base=c.points(8)
                h0=1+len(base)
                trace=9-h0
                ss=[2,trace]
                for _ in range(2):
                    ss.append(trace*ss[-1]-8*ss[-2])
                order=513-ss[3]
                fac=[(int(p),int(e)) for p,e in t.s.factor(order)]
                t.cost.operations['opaque_Sage_integer_factorization'] += 1
                rec.update(base_points=base,base_order=h0,trace=trace,power_sums=ss,order=order,factors=fac)
                eligible=[p for p,e in fac if p>=17 and e==1 and h0%p]
                if not eligible:
                    rec['rejection']='no_eligible_prime'
                else:
                    N=max(eligible)
                    points=c.points(512)
                    rec.update(N=N,cofactor=order//N,points=points,point_count=1+len(points))
                    require(len(points)+1==order,'trace point count mismatch')
                    rec['generator_attempts']=[]
                    P=None
                    for q in points:
                        P=c.scale(order//N,q)
                        rec['generator_attempts'].append(dict(input=q,output=P))
                        if P is not None:
                            break
                    if P is None or c.scale(N,P) is not None:
                        rec['rejection']='generator_order_gate'
                    else:
                        require(bool(t.s.is_prime(N)), 'N not prime')
                        mu,mu_trace=bsgs_mu(c,P,c.frob(P),N)
                        rec.update(P=P,mu=mu,bsgs=mu_trace)
                        if mu is None or mu==1 or pow(mu,3,N)!=1:
                            rec['rejection']='Frobenius_order_gate'
                        elif c.sum([P,c.frob(P),c.frob(P,2)]) is not None:
                            rec['rejection']='point_trace_gate'
                        else:
                            G=[]
                            q=P
                            for _ in range(1,N):
                                G.append(q)
                                q=c.add(q,P)
                            require(q is None and len(set(G))==N-1,'subgroup enumeration')
                            rec.update(selected_index=len(selected),G=sorted(G),status='selected',trace_point=None)
                            rec['exceptional_checks']=[]
                            for q in sorted(G):
                                require(c.add(q,None)==q and c.add(None,q)==q and c.add(q,c.neg(q)) is None,'exceptional addition')
                                rec['exceptional_checks'].append(dict(P=q,double=c.add(q,q),inverse_sum=None))
                            require(P is not None, 'invalid relation [1]P=O accepted')
                            require(c.scale(N,P) is None, 'generator order')
                            selected.append((c,rec))
                            seen_j.add(rec['j'])
        records.append(rec)
        stream.put(dict(type='curve_candidate',record=rec))
        if len(selected)==2:
            break
    return selected,records


def rref_candidates(t,dim):
    s=t.s
    candidates=[]
    for pivots in itertools.combinations(range(3),dim):
        slots=[(i,j) for i in range(dim) for j in range(3) if j not in pivots and j>pivots[i]]
        for values in itertools.product(range(8), repeat=len(slots)):
            rows=[[0]*3 for _ in range(dim)]
            for i,p in enumerate(pivots):
                rows[i][p]=1
            for (i,j),v in zip(slots,values):
                rows[i][j]=v
            candidates.append(rows)
    return sorted(candidates,key=lambda rows:tuple(itertools.chain.from_iterable(rows)))


def subspaces(t,stream):
    stable=[]
    all_candidates=[]
    for dim in (1,2):
        for rows in rref_candidates(t,dim):
            mat=t.s.matrix(t.F,[[t.base[v] for v in r] for r in rows])
            transformed=mat*t.phi.transpose()
            ok=mat.stack(transformed).rank()==dim
            rec=dict(dimension=dim,basis=rows,stable=bool(ok))
            all_candidates.append(rec)
            stream.put(dict(type='subspace_candidate',record=rec))
            t.cost.operations['opaque_Sage_subspace_rank']+=1
            if ok:
                basis=[sum(v<<(3*j) for j,v in enumerate(row)) for row in rows]
                pivots=mat.pivots()
                phi=t.s.matrix(t.F,dim,dim,lambda i,j:transformed[j,pivots[i]])
                require(phi**3==t.s.identity_matrix(t.F,dim),'induced cube')
                elements=[]
                coordinate_map={}
                for coords in itertools.product(range(8),repeat=dim):
                    v=sum((t.base[c]*row for c,row in zip(coords,mat.rows())),t.s.vector(t.F,[0,0,0]))
                    enc=sum(t.base_index[v[j]]<<(3*j) for j in range(3))
                    elements.append(enc)
                    coordinate_map[enc]=coords
                stable.append(dict(dimension=dim,basis=rows,basis_enc=basis,elements=sorted(elements),
                                   phi=t.matrix_encoding(phi),coordinate_map=coordinate_map))
    RT=t.s.PolynomialRing(t.F,'T'); T=RT.gen()
    factors=list((T**3-1).factor())
    kernels=[]
    for p,e in factors:
        mat=sum((coeff*(t.phi**i) for i,coeff in enumerate(p.list())),t.s.zero_matrix(t.F,3,3))
        ker=mat.right_kernel().basis_matrix().echelon_form()
        kernels.append(dict(factor=[t.base_index[c] for c in p.list()],multiplicity=int(e),
                            dimension=int(ker.nrows()),basis=t.matrix_encoding(ker)))
    require(all(e==1 for _,e in factors),'not semisimple')
    factor_subspaces=[]
    for n in range(1,len(kernels)+1):
        for subset in itertools.combinations(kernels,n):
            rows=sum((k['basis'] for k in subset),[])
            mat=t.s.matrix(t.F,[[t.base[v] for v in r] for r in rows]).row_space().basis_matrix().echelon_form()
            if mat.nrows() in (1,2):
                factor_subspaces.append(t.matrix_encoding(mat))
    require(sorted(factor_subspaces)==sorted(v['basis'] for v in stable),'factor/kernel complete census mismatch')
    return stable,dict(candidates=all_candidates,kernels=kernels,stable=[{k:v for k,v in x.items() if k!='coordinate_map'} for x in stable])


def poly_record(poly,encode):
    return [[list(map(int,e)),encode(c)] for e,c in sorted(poly.dict().items())]


def formal_polynomials(s):
    ring=s.PolynomialRing(s.GF(2),names=('a','b','c','d','B'),order='lex')
    a,b,c,d,B=ring.gens()
    s3=(a*b+a*c+b*c)**2+a*b*c+B
    # Descending coefficient order. Degree is formally two before any x values.
    aa=[(a+b)**2,a*b,(a*b)**2+B]
    cc=[(c+d)**2,c*d,(c*d)**2+B]
    syl=s.matrix(ring,[aa+[0],[0]+aa,cc+[0],[0]+cc])
    terms=[]
    determinant=ring.zero()
    for perm in itertools.permutations(range(4)):
        term=ring.one()
        for i,j in enumerate(perm):
            term*=syl[i,j]
        determinant+=term  # signs coincide in characteristic two
        terms.append(dict(permutation=list(perm),polynomial=poly_record(term,int)))
    require(determinant==syl.det(),'formal determinant disagreement')
    require(determinant+1!=syl.det(),'formal coefficient corruption accepted')
    return ring,s3,determinant,dict(s3=poly_record(s3,int),s4=poly_record(determinant,int),
        sylvester=[[poly_record(ring(x),int) for x in row] for row in syl.rows()],
        determinant_terms=terms,normalization_scalar=1,original_degrees=[2,2])


def specialize(t,formal,xs,target_x,B):
    values=list(xs)+([target_x] if len(xs)==3 else [target_x,0])+[B]
    t.cost.operations['opaque_Sage_formal_polynomial_evaluation']+=1
    return formal(*[t.values[v] for v in values])


def fiber(t,xs,target,B):
    a,b,c=map(lambda x:t.values[x],xs)
    d=t.values[target]; bb=t.values[B]
    A=[(a*b)**2+bb,a*b,(a+b)**2]
    C=[(c*d)**2+bb,c*d,(c+d)**2]
    R=t.s.PolynomialRing(t.K,'t'); z=R.gen()
    p=sum((v*z**i for i,v in enumerate(A)),R.zero())
    q=sum((v*z**i for i,v in enumerate(C)),R.zero())
    gcd=p.gcd(q)
    t.cost.operations['opaque_Sage_K_polynomial_gcd']+=1
    factors=[]
    if gcd:
        for f,e in gcd.monic().factor():
            factors.append(dict(coefficients=[t.index[v] for v in f.list()],degree=int(f.degree()),multiplicity=int(e)))
            t.cost.operations['opaque_Sage_K_polynomial_factor']+=1
    finite=[]
    if not p and not q:
        finite=[dict(root=i,multiplicity=None) for i in range(512)]
    else:
        for factor in factors:
            if factor['degree']==1:
                f=factor['coefficients']
                finite.append(dict(root=t.index[-t.values[f[0]]/t.values[f[1]]],multiplicity=factor['multiplicity']))
    def infinity(coeff):
        return next((i for i,v in enumerate(reversed(coeff)) if v),None)
    ia,ic=infinity(A),infinity(C)
    inf=(ia is None or ia>0) and (ic is None or ic>0)
    finite_exists=bool(factors) or (not p and not q)
    category=('mixed_or_degenerate' if inf and finite_exists else 'infinity_only' if inf else 'finite_common_root' if finite_exists else 'no_common_projective_root')
    return dict(A=[t.index[v] for v in A],C=[t.index[v] for v in C],
        affine_degrees=[int(p.degree()) if p else None,int(q.degree()) if q else None],
        gcd=[t.index[v] for v in gcd.list()],factors=factors,
        finite_K_roots=sorted(finite,key=lambda x:x['root']),non_K_factors=[f for f in factors if f['degree']>1],
        infinity_orders=[ia,ic],infinity_common=inf,both_zero=not p and not q,
        zero_polynomial_means='whole_projective_line',category=category)


def build_ideal(t, V, m, target_x, B, formal, D, order='degrevlex'):
    t.cost.operations['opaque_Sage_descended_ideal_construction']+=1
    names=tuple('u_%d_%d'%(i,j) for i in range(m) for j in range(V['dimension']))
    RK=t.s.PolynomialRing(t.K,names=names,order=order)
    RF=t.s.PolynomialRing(t.F,names=names,order=order)
    uu=RK.gens()
    xx=[sum((t.values[b]*uu[i*V['dimension']+j] for j,b in enumerate(V['basis_enc'])),RK.zero()) for i in range(m)]
    args=xx+([RK(t.values[target_x])] if m==3 else [RK(t.values[target_x]),RK.zero()])+[RK(t.values[B])]
    sem=RK.zero()
    for powers,coef in formal.dict().items():
        term=RK(int(coef))
        for x,e in zip(args,powers):
            term*=x**int(e)
        sem+=term
    def descend(p):
        coeffs=[{} for _ in range(3)]
        for e,a in p.dict().items():
            for j,k in enumerate(t.digits(t.index[a])):
                if k:
                    coeffs[j][e]=t.base[k]
        return [RF(v) for v in coeffs]
    eq=descend(sem)
    domains=[]
    for x in xx:
        g=RK.one()
        for d in D:
            g*=x-t.values[d]
        domains+=descend(g)
    fields=[u**8-u for u in RF.gens()]
    generators=eq+domains+fields
    return RF,generators,dict(variable_order=list(names),term_order=order,
        semaev=poly_record(sem,t.index.__getitem__),descended=[poly_record(g,t.base_index.__getitem__) for g in eq],
        domain_generators=[poly_record(g,t.base_index.__getitem__) for g in domains],
        field_generators=[poly_record(g,t.base_index.__getitem__) for g in fields])



def fields_first_view(generators, m, d, encode):
    """Separate insertion view; canonical ideal/lex/covariance inputs survive."""
    f=3+3*m
    require(len(generators)==f+m*d,'canonical generator block length')
    permutation=list(range(f,f+m*d))+list(range(f))
    require(sorted(permutation)==list(range(len(generators))),'order bijection')
    inverse=[permutation.index(i) for i in range(len(generators))]
    ordered=[generators[i] for i in permutation]
    require(all(ordered[inverse[i]]==g for i,g in enumerate(generators)),'inverse generator recovery')
    encoded=[poly_record(g,encode) for g in generators]
    require([poly_record(ordered[inverse[i]],encode) for i in range(len(generators))]==encoded,'coefficient order recovery')
    metadata=dict(order_id=ORDER_ID,permutation=permutation,inverse=inverse,
                  canonical_generator_sha256=hashlib.sha256(canonical(encoded)).hexdigest())
    return ordered,metadata

def buchberger(ring, generators, encode, trace_stream, key):
    basis=[]; dsolve=0; trace_records=0; trace_bytes=0
    def emit(rec):
        nonlocal trace_records,trace_bytes
        row=dict(type='buchberger',cell_target=key,record=rec)
        trace_records+=1;trace_bytes+=len(canonical(row))
        trace_stream.put(row)
    def normal(poly):
        nonlocal dsolve
        remainder=ring.zero()
        while poly:
            dsolve=max(dsolve,int(poly.total_degree()))
            lt=poly.lt()
            applied=False
            for j,g in enumerate(basis):
                if g.lm().divides(poly.lm()):
                    quotient=ring.monomial_quotient(poly.lm(),g.lm())*(poly.lc()/g.lc())
                    emit(dict(kind='reduce',reducer=j,before=poly_record(poly,encode),multiplier=poly_record(quotient,encode)))
                    poly-=quotient*g
                    applied=True
                    break
            if not applied:
                remainder+=lt
                poly-=lt
        return remainder
    for i,g in enumerate(generators):
        h=normal(g)
        if h:
            h/=h.lc(); basis.append(h)
            emit(dict(kind='initial_basis',generator=i,index=len(basis)-1,polynomial=poly_record(h,encode)))
    pairs={(i,j) for j in range(len(basis)) for i in range(j)}
    while pairs:
        def pkey(ij):
            i,j=ij
            return (int(ring.monomial_lcm(basis[i].lm(),basis[j].lm()).total_degree()),i,j)
        i,j=min(pairs,key=pkey); pairs.remove((i,j))
        lcm=ring.monomial_lcm(basis[i].lm(),basis[j].lm())
        sp=ring.monomial_quotient(lcm,basis[i].lm())*basis[i]-ring.monomial_quotient(lcm,basis[j].lm())*basis[j]
        emit(dict(kind='pair',indices=[i,j],lcm=poly_record(lcm,encode),spoly=poly_record(sp,encode)))
        dsolve=max(dsolve,int(sp.total_degree()) if sp else 0)
        h=normal(sp)
        if h:
            h/=h.lc(); n=len(basis)
            basis.append(h); pairs.update((k,n) for k in range(n))
            emit(dict(kind='new_basis',index=n,polynomial=poly_record(h,encode)))
    return basis,dict(basis=[poly_record(g,encode) for g in basis],operational_d_solve=dsolve,
                      theoretical_d_reg=None,first_fall_degree=None,
                      trace_records=trace_records,trace_bytes=trace_bytes)


def roots_by_triangular_backtracking(t,ring,basis):
    # A lex Groebner basis plus field equations makes this exact finite root
    # enumeration. Every branch is tested; no variety() external process.
    variables=ring.gens(); found=[]; partial={}; nodes=0
    def walk(i):
        nonlocal nodes
        if i<0:
            found.append(tuple(t.base_index[partial[u]] for u in variables)); return
        for a in t.base:
            nodes+=1;partial[variables[i]]=a
            bad=False
            for g in basis:
                reduced=ring(g.subs(partial))
                if reduced.is_constant() and reduced!=0:
                    bad=True;break
            if not bad:
                walk(i-1)
        partial.pop(variables[i],None)
    walk(len(variables)-1)
    return sorted(found),nodes


def covariance(t,V,m,ordinary,transported):
    ring,gens,record=ordinary
    r2,g2,rec2=transported
    dim=V['dimension']; us=ring.gens()
    subs={us[i*dim+j]:sum((t.base[V['phi'][j][k]]*us[i*dim+k] for k in range(dim)),ring.zero()) for i in range(m) for j in range(dim)}
    witnesses=[]
    # q-Frobenius acts on tower coefficients, while F8 scalar variables stay
    # formal variables. Equation vector changes by the physical phi matrix.
    for offset,length in ((0,3),(3,3*m)):
        for block in range(offset,offset+length,3):
            for j in range(3):
                left=ring(g2[block+j]).subs(subs)
                right=sum((t.phi[j,k]*gens[block+k] for k in range(3)),ring.zero())
                require(left==right,'coefficient/domain Frobenius covariance')
                witnesses.append(dict(generator=block+j,left=poly_record(left,t.base_index.__getitem__),right=poly_record(right,t.base_index.__getitem__)))
    field_offset=3+3*m
    for i in range(m):
        for j in range(dim):
            left=ring(g2[field_offset+i*dim+j]).subs(subs)
            right=sum((t.base[V['phi'][j][k]]*gens[field_offset+i*dim+k] for k in range(dim)),ring.zero())
            require(left==right,'field equation transport')
            witnesses.append(dict(generator=field_offset+i*dim+j,left=poly_record(left,t.base_index.__getitem__),right=poly_record(right,t.base_index.__getitem__)))
    require(ring.one()!=ring.zero(),'corrupted coefficient witness not rejected')
    # Explicit corrupted equality uses an actual witnessed polynomial.
    require(witnesses and witnesses[0]['left']==witnesses[0]['right'],'missing transport witness')
    return dict(witnesses=witnesses,corrupted_add_one_rejected=True)


def panel(t,curves,spaces,polys,roots,tuples,costs):
    _,S3,S4,formal_record=polys
    cells=[]; calibrations=[]; overlaps=[]; domain_records=[]
    controls={'formal_resultant_determinant':True,'invalid_generator_relation_rejection':True,
              'projective_fixed_controls':fixed_projective_controls(t.s)}
    calibration_selected=None
    for ci,(curve,rec) in enumerate(curves):
        G=[tuple(p) for p in rec['G']]
        for vi,V in enumerate(spaces):
            vset=set(V['elements'])
            F=sorted(p for p in G if p[0] in vset)
            D=sorted({p[0] for p in F})
            lifts={x:sorted(p for p in F if p[0]==x) for x in D}
            wrong_base=V['elements']==list(range(8))
            if wrong_base:
                all_lifts=[p for p in rec['points'] if p[0]<8]
                require(all(p[1]<8 for p in all_lifts),'base-field x has non-base y')
                require(not [p for p in G if p[0]<8 and p[1]<8],'G/base intersection')
                require(not F,'nonempty wrong-base subgroup domain')
            for p in F:
                require(curve.scale(rec['N'],p) is None and p in G,'factor base order/membership')
                require(curve.frob(p) in F,'signed domain stability')
            domain_records.append(dict(curve=ci,subspace=vi,F=F,D=D,wrong_base=wrong_base,
                                       wrong_base_control_pass=bool(wrong_base),empty=not D))
            for m in (2,3):
                key=[ci,vi,m]
                if calibration_selected is None and D:
                    calibration_selected=key
                selected=key==calibration_selected
                formal=S3 if m==2 else S4
                tuple_count=0; sum_counts=Counter(); routed=Counter()
                with costs.stage('signed_tuple_census:'+str(key)):
                    for points in itertools.product(F,repeat=m):
                        total=curve.sum(points)
                        xs=tuple(p[0] for p in points)
                        stab=[k for k in range(3) if tuple(curve.frob(p,k) for p in points)==points]
                        tuples.put(dict(type='signed_tuple',cell=key,points=points,xs=xs,sum=total,
                                        intermediate_sums=[curve.sum(points[:j]) for j in range(1,m+1)],
                                        stabilizer=stab))
                        sum_counts[total]+=1; routed[(xs,total)]+=1;tuple_count+=1
                        costs.operations['executed_signed_tuples']+=1
                require(tuple_count==len(F)**m,'signed tuple count')
                tuples.put(dict(type='signed_cell_total',cell=key,expected=len(F)**m,executed=tuple_count,
                                sum_counts=[dict(target=q,count=n) for q,n in sorted(sum_counts.items(),key=lambda item:(item[0] is not None,item[0] or ()))],
                                domain_empty=not F))
                rootsets={}; lifted_sets={}; target_metrics=[]
                ideal_cache=BoundedCache(); calibration_cache=BoundedCache()
                def ideal_for(rx):
                    return build_ideal(t,V,m,rx,curve.B,formal,D)
                with costs.stage('x_root_lift_covariance:'+str(key)):
                    for target in G:
                        pi=curve.frob(target); pi2=curve.frob(target,2)
                        require(len({target,pi,pi2})==3 and curve.frob(target,3)==target,'target orbit length')
                        rootset=set(); lifted=set(); valid_lifts=0; raw=0;spurious=0;enumerated=0
                        for xs in itertools.product(D,repeat=m):
                            enumerated+=1
                            val=specialize(t,formal,xs,target[0],curve.B)
                            if val!=0:
                                require(routed[(xs,target)]==0,'signed tuple violates polynomial necessity')
                                continue
                            raw+=1;rootset.add(xs)
                            good=[];all_lifts=[]
                            for points in itertools.product(*(lifts[x] for x in xs)):
                                total=curve.sum(points)
                                all_lifts.append(dict(points=points,sum=total))
                                costs.operations['executed_root_lift_checks']+=1
                                if total==target:
                                    good.append(points)
                            require(len(good)==routed[(xs,target)],'independent signed/lift reconciliation')
                            valid_lifts+=len(good)
                            if good:lifted.add(xs)
                            else:spurious+=1
                            mapped=tuple(t.pow(x,8) for x in xs)
                            require(specialize(t,formal,mapped,pi[0],curve.B)==0,'root covariance')
                            for points in good:
                                require(curve.sum([curve.frob(p) for p in points])==pi,'signed lift transport')
                            row=dict(type='root',cell=key,target=target,xs=xs,lifts=all_lifts,
                                     valid_lifts=good,multiplicity=len(good),transported_xs=mapped,
                                     stabilizer=[k for k in range(3) if tuple(t.pow(x,8**k) for x in xs)==xs],
                                     repeated_coordinates=len(set(xs))<m)
                            if m==3: row['fiber']=fiber(t,xs,target[0],curve.B)
                            roots.put(row)
                        require(enumerated==len(D)**m,'x domain count')
                        require(valid_lifts==sum_counts[target],'target signed coverage')
                        ordinary,hit=ideal_cache.get(target[0],lambda:ideal_for(target[0]))
                        transformed,phit=ideal_cache.get(pi[0],lambda:ideal_for(pi[0]))
                        witness=covariance(t,V,m,ordinary,transformed)
                        equation_key=hashlib.sha256(canonical(ordinary[2])).hexdigest()
                        roots.put(dict(type='ideal',cell=key,target=target,record=ordinary[2],
                                       equation_key=equation_key,cache_hit=hit,pi_cache_hit=phit,covariance=witness))
                        # Negative controls mutate a real equation value and a
                        # real target point, and never overwrite retained data.
                        require((ordinary[1][0]+1)!=ordinary[1][0],'equation mutation undetected')
                        require(curve.add(target,rec['P'])!=target,'target mutation undetected')
                        cal=None
                        if selected:
                            def solve():
                                with costs.stage('calibration:'+str(key)+':'+str(target[0])):
                                    ring,gens,_=ordinary
                                    lr=t.s.PolynomialRing(t.F,names=ring.variable_names(),order='lex')
                                    lg=[lr(g) for g in gens]
                                    gb=list(lr.ideal(lg).groebner_basis(algorithm='libsingular:std'))
                                    costs.operations['opaque_inprocess_libsingular_lex_basis']+=1
                                    lexroots,nodes=roots_by_triangular_backtracking(t,lr,gb)
                                    ordered,order_metadata=fields_first_view(gens,m,V['dimension'],t.base_index.__getitem__)
                                    grev,grevrecord=buchberger(ring,ordered,t.base_index.__getitem__,roots,key+[list(target)])
                                    grevrecord.update(order_metadata)
                                    # In-process ideal reduction verifies custom
                                    # basis equality in both directions.
                                    require(all(g.reduce(gb)==0 for g in lg),'lex generator reduction')
                                    require(all(lr(g).reduce(gb)==0 for g in grev),'grev in original ideal')
                                    require(all(ring(g).reduce(grev)==0 for g in gb),'original ideal in grev')
                                    gcoords=[]
                                    for coords in itertools.product(range(8),repeat=m*V['dimension']):
                                        if all(g(*[t.base[c] for c in coords])==0 for g in grev):gcoords.append(coords)
                                    require(sorted(gcoords)==lexroots,'lex/grev roots mismatch')
                                    return dict(lex_basis=[poly_record(g,t.base_index.__getitem__) for g in gb],
                                        coordinate_roots=lexroots,lex_nodes=nodes,grevlex=grevrecord,
                                        lex_order=list(lr.variable_names()),equation_key=equation_key)
                            cal,calhit=calibration_cache.get((ORDER_ID,equation_key),solve)
                            expected=sorted(tuple(c for x in xs for c in V['coordinate_map'][x]) for xs in rootset)
                            require(expected==[tuple(x) for x in cal['coordinate_roots']],'calibration/enumeration roots')
                            roots.put(dict(type='calibration',cell=key,target=target,record=cal,cache_hit=calhit,
                                           exact_signed_lift_count=valid_lifts,order_id=ORDER_ID,
                                           trace_records_emitted=0 if calhit else cal['grevlex']['trace_records'],
                                           trace_bytes_emitted=0 if calhit else cal['grevlex']['trace_bytes']))
                            calibrations.append(dict(cell=key,target=target,equation_key=equation_key,
                                                      cache_hit=calhit,root_count=raw,lift_count=valid_lifts))
                        metric=dict(target=target,x_tuples=enumerated,raw_roots=raw,
                                    valid_lifts=valid_lifts,roots_with_lifts=len(lifted),spurious_roots=spurious)
                        roots.put(dict(type='target_total',cell=key,record=metric))
                        target_metrics.append(metric);rootsets[target]=rootset;lifted_sets[target]=lifted
                    for target in G:
                        orbit=[target,curve.frob(target),curve.frob(target,2)]
                        A,B,C=(rootsets[r] for r in orbit)
                        shared=sorted(A&B);union=sorted(A|B)
                        for xs in shared:
                            roots.put(dict(type='overlap_witness',cell=key,targets=orbit[:2],xs=xs,
                                target_lifts=[[points for points in itertools.product(*(lifts[x] for x in xs)) if curve.sum(points)==r] for r in orbit[:2]]))
                        record=dict(cell=key,target=target,orbit=orbit,
                            zero_set_ideal_sum_overlap=len(shared),zero_set_ideal_intersection_union=len(union),
                            prefix_union_cardinalities=[len(A),len(A|B),len(A|B|C)],
                            shared_roots=shared,union_roots=union,
                            shared_roots_with_both_signed_targets=sorted(lifted_sets[target]&lifted_sets[orbit[1]]))
                        roots.put(dict(type='set_operations',record=record));overlaps.append({k:v for k,v in record.items() if k not in ('shared_roots','union_roots','shared_roots_with_both_signed_targets')})
                cell=dict(cell=key,F_size=len(F),D_size=len(D),signed_tuples=tuple_count,
                          targets=len(G),target_metrics=target_metrics,calibration=selected,
                          ideal_cache=ideal_cache.stats(),calibration_cache=calibration_cache.stats(),empty=not D)
                cells.append(cell);roots.put(dict(type='cell_total',record=cell))
    controls['coverage']={
        'A2_sign_fiber':{'target_comparisons':len(overlaps),'completed_without_early_stop':True},
        'wrong_base_Fq':{'domains_checked':sum(d['wrong_base'] for d in domain_records)},
        'stableV1_V2':{'stable_subspaces':len(spaces),'complete_RREF_and_kernel_checks':True},
        'k1_identity_and_set_operations':{'target_orbits_checked':len(overlaps)},
        'Frobenius_covariance_and_stabilizers':{'targets_checked':sum(c['targets'] for c in cells)},
        'S3_S4_independent_construction':{'producer_formal_determinant':True,'independent_checker_pending':True},
        'projective_degree_drop':{'fixed_controls':3,'all_m3_roots_retained':True},
        'exceptional_point_addition':{'selected_curve_nonzero_points_checked':sum(len(r['G']) for _,r in curves)},
        'complete_lex_calibration':{'cell':calibration_selected,'targets_checked':len(calibrations),'status':'complete' if calibration_selected is not None else 'calibration_unavailable'},
        'invalid_relation_rejection':{'selected_generators_checked':len(curves),'target_coefficient_mutations_checked':sum(c['targets'] for c in cells)}}
    return dict(cells=cells,domains=domain_records,calibration_selected=calibration_selected,
                calibration_status='complete' if calibration_selected is not None else 'calibration_unavailable',
                calibration_targets=calibrations,set_operations=overlaps,controls=controls,formal=formal_record)


def fixed_projective_controls(s):
    R=s.PolynomialRing(s.GF(2),'t'); x=R.gen()
    # Original homogeneous degree two: t*w and (t+w)*w. Both vanish at
    # [1:0], while gcd(t,t+1)=1. Also explicitly retain zero/constant cases.
    cases=[([0,1,0],[1,1,0]),([0,0,0],[0,0,0]),([1,0,0],[0,0,0])]
    output=[]
    for a,b in cases:
        p=R(a);q=R(b)
        mat=s.matrix(s.GF(2),[list(reversed(a))+[0],[0]+list(reversed(a)),list(reversed(b))+[0],[0]+list(reversed(b))])
        require(mat.det()==0,'fixed formal degree-drop control')
        output.append(dict(A=a,C=b,gcd=list(map(int,p.gcd(q).list())),formal_resultant=int(mat.det()),
                           infinity_common=True,both_zero=not p and not q))
    require(R(cases[0][0]).gcd(R(cases[0][1]))==1,'infinity-only control has affine root')
    return output


def guard_and_inputs(run_dir):
    require(platform.system()=='Linux','scientific run requires admitted Linux runtime')
    soft,hard=resource.getrlimit(resource.RLIMIT_AS)
    require(soft==8192*1024*1024,'adapter RLIMIT_AS must equal 8192 MiB')
    require(os.getpgrp()>0,'missing POSIX process group')
    require(run_dir.name==RUN,'unexpected run identity')
    require(run_dir.is_dir(),'adapter must create run directory')
    require(not any((run_dir/p).exists() for p in SCIENCE),'refuse existing scientific artifacts')
    inputs={name:json.loads((run_dir/name).read_text()) for name in ('launch.json','environment.json')}
    require((run_dir/'command.txt').is_file(),'missing adapter command')
    require(inputs['launch.json'].get('authority',{}).get('commit'),'missing launch authority commit')
    repo=Path(__file__).resolve().parents[3]
    for relative,expected in inputs['environment.json']['source_sha256'].items():
        require(sha(repo/relative)==expected,'bound source hash mismatch: '+relative)
    require(sha(repo/'experiments/EXP-FROB-d8aa37/specification-stage0-fields-first-v3.yaml')==inputs['environment.json']['specification_sha256'],'bound specification mismatch')
    lock_path=repo/'coordination/frobenius/BATCH-e42ce7/admission/linux-runtime-lock.json'
    require(lock_path.is_file(),'missing committed Linux runtime lock')
    lock=json.loads(lock_path.read_text())
    # The adapter owns authoritative lock-schema/admission verification; retain
    # all actual lock bytes and hashes without fabricating unexposed fields.
    require(lock,'empty runtime lock')
    return repo,inputs,lock


def write_json(path,value):
    with open(path,'xb') as f:f.write(canonical(value))


def execute(run_dir):
    start=stamp();w=time.perf_counter();c=time.process_time();cost=Costs()
    with cost.stage('runtime_admission_and_imports'):
        repo,adapter,runtime_lock=guard_and_inputs(run_dir)
        import sage.all as s
        from sage.env import SAGE_VERSION
        require(SAGE_VERSION=='10.9','Sage version differs from frozen runtime')
    git_head=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
    require(git_head==adapter['launch.json']['authority']['commit'],'executing HEAD differs from launch')
    git_status=subprocess.run(['git','status','--porcelain=v1','--untracked-files=all'],cwd=repo,text=True,capture_output=True,check=True).stdout
    cost.operations['read_only_git_processes']+=2
    roots=Stream(run_dir/'roots.jsonl.gz','roots');tuples=Stream(run_dir/'tuples.jsonl.gz','tuples')
    fixtures={};certificates={};data={};error=None;status='completed_valid'
    try:
        with cost.stage('field_acquisition'):
            t=Tower(s,cost);fixtures['field']=t.record()
        with cost.stage('curve_acquisition'):
            curves,records=select_curves(t,tuples);fixtures['curve_candidates']=records
        with cost.stage('subspace_acquisition'):
            spaces,space_record=subspaces(t,tuples);fixtures['subspaces']=space_record
        with cost.stage('formal_polynomials'):
            polys=formal_polynomials(s);cost.operations['opaque_Sage_formal_determinant']+=1
        data=panel(t,curves,spaces,polys,roots,tuples,cost)
        certificates=dict(formal=data.pop('formal'),controls=data['controls'])
        domain_complete=True
        outcome='complete' if len(curves)==2 and data['calibration_selected'] is not None else 'structural_unavailable' if len(curves)<2 else 'calibration_unavailable'
        result=dict(valid=True,outcome=outcome,selected_curves=len(curves),
                    domain_census_complete=domain_complete,stage0_gate_complete=False,
                    producer_stage0_checks_complete=outcome=='complete',
                    independent_review_pending=True,full_v1_complete=False,
                    cells=data['cells'],calibration_selected=data['calibration_selected'],
                    calibration_status=data['calibration_status'],invalid_reason=None,
                    certificate={'kind':'none'})
    except BaseException as exc:
        status='resource_exhaustion' if isinstance(exc,MemoryError) else 'failed_implementation'
        error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        result=dict(valid=False,outcome=status,domain_census_complete=False,stage0_gate_complete=False,
                    producer_stage0_checks_complete=False,independent_review_pending=True,
                    full_v1_complete=False,invalid_reason=error,certificate={'kind':'none'})
        print(error['traceback'],file=sys.stderr)
    roots.put(dict(type='terminal',status=status,outcome=result['outcome']))
    tuples.put(dict(type='terminal',status=status,outcome=result['outcome']))
    with cost.stage('serialization'):
        streams={'roots.jsonl.gz':roots.close(),'tuples.jsonl.gz':tuples.close()}
        fixtures['domains']=data.get('domains',[])
        certificates['calibration_targets']=data.get('calibration_targets',[])
        certificates['set_operations']=data.get('set_operations',[])
        write_json(run_dir/'fixtures.json',fixtures)
        write_json(run_dir/'certificates.json',certificates)
        write_json(run_dir/'raw-result.json',result)
        with open(run_dir/'report.md','x') as f:
            f.write('# EXP-FROB-d8aa37 mandatory stage0\n\n'+
                    'Outcome: '+result['outcome']+'.\n\n'+
                    'Complete frozen q=8,n=3 signed/x-only census when available. '+
                    'No scalar recovery, full-v1 completion, asymptotic conclusion, or independent review is claimed.\n\n'+
                    'The manifest separates census completion, producer checks and the independent stage gate. '+
                    'Every unavailable or failed outcome remains explicit.\n')
    metrics=dict(stages=cost.stages,operations=dict(cost.operations),streams=streams,
                 opaque_primitive_internals='Sage field, curve, matrix, polynomial and libsingular internals are opaque; named calls and enclosing CPU/wall are charged, not invented base operation counts.',
                 coefficient_bitlength=3,extension_encoding_bits=9,cache_limit=CACHE_LIMIT,
                 timing_excludes='final metrics/manifest serialization, driver exit, and later independent checker process',
                 unavailable_full_v1_costs=None)
    write_json(run_dir/'metrics.json',metrics)
    artifact_hashes={name:sha(run_dir/name) for name in SCIENCE if name!='manifest.yaml'}
    stable_hashes={name:sha(run_dir/name) for name in ('launch.json','command.txt','environment.json')}
    manifest={'run':dict(id=RUN,experiment_id=EXPERIMENT,status=status,
        code=dict(commit=adapter['launch.json']['authority']['commit'],
                  dirty=bool(git_status),dirty_status_at_driver_start=git_status,
                  command=(run_dir/'command.txt').read_text(),argv=adapter['launch.json'].get('argv')),
        environment=dict(adapter_environment=adapter['environment.json'],python=sys.version,sage=SAGE_VERSION,
                         platform=platform.platform(),machine=platform.machine(),runtime_lock=runtime_lock,
                         runtime_lock_sha256=sha(repo/'coordination/frobenius/BATCH-e42ce7/admission/linux-runtime-lock.json')),
        inputs=dict(parameters={'q':8,'n':3,'curves':2,'dimensions':[1,2],'arities':[2,3],'targets':'all_nonzero_G'},
                    specification_sha256=sha(repo/'experiments/EXP-FROB-d8aa37/specification-stage0-fields-first-v3.yaml'),
                    launch=adapter['launch.json'],stable_adapter_hashes=stable_hashes),
        timing=dict(started_at=start,finished_at=stamp(),wall_seconds=time.perf_counter()-w,
                    cpu_seconds=time.process_time()-c,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    excludes=metrics['timing_excludes']),result=result,artifact_sha256=artifact_hashes)}
    write_json(run_dir/'manifest.yaml',manifest)
    print(canonical(dict(status=status,result=result['outcome'],driver_artifact_hashes=artifact_hashes)).decode(),end='')
    return 0 if error is None else 1


def self_test():
    """Fixed nonstage fixtures only; never constructs the stage0 field/panel."""
    import sage.all as s
    assert canonical({'z':1,'a':[True,None]})==b'{"a":[true,null],"z":1}\n'
    F=s.GF(2);R=s.PolynomialRing(F,names=('x','y'),order='degrevlex');x,y=R.gens()
    require(R.monomial_quotient(x*x*y,x)==x*y,'monomial quotient API')
    require(R.monomial_lcm(x*x,y*y)==x*x*y*y,'lcm API')
    require(x.lm().divides((x*y).lm()),'monomial divisibility API')
    require(s.matrix(F,[[0,1],[1,0]])**2==s.identity_matrix(F,2),'fixed matrix identity')
    class TinyBase:
        base=[F(0),F(1)]
        base_index={F(0):0,F(1):1}
    tiny=TinyBase()
    LR=s.PolynomialRing(F,names=('x','y'),order='lex');lx,ly=LR.gens()
    fixed_roots,nodes=roots_by_triangular_backtracking(tiny,LR,[ly*ly+ly,lx+ly])
    require(fixed_roots==[(0,0),(1,1)] and nodes==6,'fixed triangular lex root solver')
    cases=fixed_projective_controls(s)
    require(len(cases)==3,'fixed projective fixture count')
    require((x+y).subs({x:y})==0,'simultaneous polynomial substitution API')
    class FixedTower:
        def __init__(self):
            self.s=s;self.K=F;self.F=F;self.values=[F(0),F(1)];self.base=self.values;self.index={F(0):0,F(1):1};self.base_index=self.index;self.cost=Costs();self.phi=s.identity_matrix(F,3)
        digits=staticmethod(Tower.digits)
    fixed_tower=FixedTower()
    generic=s.PolynomialRing(F,names=('a','b','c','d','B'),order='lex')
    a,b,c,d,B=generic.gens()
    V={'dimension':1,'basis_enc':[1],'phi':[[1]]}
    ideal=build_ideal(fixed_tower,V,2,1,1,a+b+c+B,[0,1])
    canonical_before=canonical(ideal[2])
    ordered,order_metadata=fields_first_view(ideal[1],2,1,int)
    require(len(ordered)==len(ideal[1]) and ordered[:2]==ideal[1][-2:],'fields-first view')
    require(canonical_before==canonical(ideal[2]),'canonical equation records changed')
    witness=covariance(fixed_tower,V,2,ideal,ideal)
    require(len(witness['witnesses'])==11,'fixed descended ideal/covariance API')
    curve=Curve(fixed_tower,0,1)
    P=(1,0);T=(0,1)
    require(curve.add(P,P)==T and curve.add(P,curve.neg(P)) is None,'fixed F2 binary group formulas')
    points=[None,(0,1),(1,0),(1,1)]
    require(all(curve.add(curve.add(a,b),c)==curve.add(a,curve.add(b,c)) for a,b,c in itertools.product(points,repeat=3)),'fixed F2 associativity')
    class Sink:
        def __init__(self):self.rows=[]
        def put(self,row):self.rows.append(row)
    sink=Sink();basis,rec=buchberger(R,[x*x+x,y+x],int,sink,['fixed_F2_fixture'])
    require(all(g.reduce(basis)==0 for g in [x*x+x,y+x]),'fixed custom Buchberger')
    lex=s.PolynomialRing(F,names=('x','y'),order='lex')
    gb=list(lex.ideal([lex(x*x+x),lex(y+x)]).groebner_basis(algorithm='libsingular:std'))
    require(all(g.reduce(gb)==0 for g in [lex(x*x+x),lex(y+x)]),'fixed libsingular API')
    ordered_sink=Sink()
    ob,om=buchberger(ideal[0],ordered,int,ordered_sink,['fixed',0,2,[1,0]])
    require(all(g.reduce(ob)==0 for g in ideal[1]),'fields-first original-generator membership')
    original_basis,_=buchberger(ideal[0],ideal[1],int,Sink(),['fixed_canonical_F2'])
    require(all(g.reduce(original_basis)==0 for g in ob),'fields-first reverse ideal membership')
    require(sorted(c for c in itertools.product(range(2),repeat=2) if all(g(*c)==0 for g in ob))==sorted(c for c in itertools.product(range(2),repeat=2) if all(g(*c)==0 for g in ideal[1])),'fields-first complete F2 roots')
    require(om['trace_records']==len(ordered_sink.rows) and om['trace_bytes']==sum(len(canonical(row)) for row in ordered_sink.rows),'emitted byte counts')
    duplicate_fixture=list(ideal[1]);duplicate_fixture[1]=duplicate_fixture[0]
    duplicate_view,duplicate_meta=fields_first_view(duplicate_fixture,2,1,int)
    require([duplicate_view[duplicate_meta['inverse'][i]] for i in range(len(duplicate_fixture))]==duplicate_fixture,'zero/duplicate generator position retention')
    cache=BoundedCache()
    for i in range(CACHE_LIMIT+1):cache.get((ORDER_ID,str(i)),lambda i=i:i)
    require(len(cache.data)==CACHE_LIMIT and cache.evictions==1 and (ORDER_ID,'0') not in cache.data,'cache capacity/oldest eviction')
    value,hit=cache.get((ORDER_ID,str(CACHE_LIMIT)),lambda:None)
    require(hit and value==CACHE_LIMIT,'cache hit retains value')
    value,hit=cache.get(('other_order',str(CACHE_LIMIT)),lambda:-1)
    require(not hit and value==-1 and cache.evictions==2,'cache separates order IDs')
    print(canonical(dict(test='fixed_nonstage_F2',cache_fixture=cache.stats(),fields_first_trace_sha256=hashlib.sha256(b''.join(canonical(row) for row in ordered_sink.rows)).hexdigest(),fields_first_trace_utf8=b''.join(canonical(row) for row in ordered_sink.rows).decode(),order_metadata=order_metadata,fields_first_trace_records=om['trace_records'],fields_first_trace_bytes=om['trace_bytes'],passed=True,projective_cases=cases,
                         buchberger_trace_records=len(sink.rows),fixed_generic_ideal_sha256=hashlib.sha256(canonical(ideal[2])).hexdigest(),stage0_constructions=0)).decode(),end='')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run-dir',type=Path)
    group.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test();return 0
    return execute(args.run_dir.resolve())


if __name__=='__main__':
    sys.exit(main())
