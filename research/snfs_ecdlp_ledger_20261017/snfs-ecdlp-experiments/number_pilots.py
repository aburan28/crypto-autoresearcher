from core import *
from collections import Counter


def class_number(D):
    assert D<0 and D%4 in (0,1)
    forms=[]
    for a in range(1,math.isqrt(-D//3)+2):
        for b in range(-a,a+1):
            if (b*b-D)%(4*a):continue
            c=(b*b-D)//(4*a)
            if a>c or math.gcd(math.gcd(a,abs(b)),c)>1:continue
            if (abs(b)==a or a==c) and b<0:continue
            forms.append((a,b,c))
    return len(forms)


def c1():
    assert [class_number(D) for D in (-3,-4,-7,-15,-19,-43,-67,-163)]==[1,1,1,2,1,1,1,1]
    rows=[]
    for bits in (8,10,12,14,16):
        p=int(prevprime(2**bits));gen=rng('SNFS-C1',str(bits))
        for i in range(12):
            while True:
                a,b=gen.randrange(p),gen.randrange(p)
                if (4*a**3+27*b*b)%p:break
            E=EC(p,a,b);t=p+1-E.N
            if t%p==0:continue
            D=t*t-4*p
            rows.append(dict(p=p,a=a,b=b,trace=t,Frobenius_order_discriminant=D,
                Frobenius_order_class_number=class_number(D),
                endomorphism_order_certified=False))
    # Exact rational CM j contradicts any universal approximation-height bound.
    J=-960**3;p=11;k=20
    assert abs(J)<p**(k//2)
    write_result('SNFS-C1','Frobenius-order class-number sampling and a rational-CM exception',rows,
        ['These are class numbers of Z[pi], not certified End(E) orders.','No general canonical-lift Newton algorithm or endomorphism-ring algorithm executed.','Small-CM rational j is an exception to a universal statement, not evidence about typical random j.'],
        dict(class_number_positive_controls=True,rational_CM_exception=dict(p=p,precision_power=k,j=J,
            approximation_height=abs(J),claimed_threshold=p**(k//2),exact_error=0)))


def c3():
    rows=[];p=4093;B=31
    gen=rng('SNFS-C3','truncated-teichmuller')
    for k in (1,2,3,4):
        start=time.perf_counter();m=p**k;ts=us=0
        for a in range(1,p):
            w=pow(a,p**(k-1),m)
            assert w%p==a and pow(w,p,m)==w
            ts+=smooth(w,B)
            u=gen.randrange(1,m)
            while u%p==0:u=gen.randrange(1,m)
            us+=smooth(u,B)
        rows.append(dict(p=p,B=B,k=k,samples=p-1,
            Teichmuller_smooth_count=ts,uniform_unit_smooth_count=us,
            Teichmuller_fraction=ts/(p-1),uniform_fraction=us/(p-1),
                fixed_unit_one_always_smooth=1,
                Teichmuller_nontrivial_smooth_fraction=(ts-1)/(p-2),
            wall_seconds=time.perf_counter()-start))
    write_result('SNFS-C3','Exhaustive Teichmuller representatives at one small prime, with matched uniform-unit samples',rows,
        ['No proof of pseudorandomness or asymptotic Dickman behavior.','One-prime finite distribution; sparse counts require uncertainty and more primes before interpreting ratios.'])


def d1():
    P=(F(3),F(5));a=F(0);b=F(-2);h=height(P,a,b,6)
    assert 108%25!=0 # Nagell-Lutz excludes torsion for this integral point.
    rows=[]
    for p in (101,257,1021,4093):
        E=EC(p,0,-2);order=E.order((3,5))
        for M in (2,4,8):
            base={E.mul(v,(3,5)) for v in range(-M,M+1)}
            for m in (4,6,8):
                sums={E.mul(v,(3,5)) for v in range(-m*M,m*M+1)}
                assert len(sums)==min(order,2*m*M+1)
                assert len(sums)<=m*(2*M+1)
                rows.append(dict(p=p,N=E.N,point_order=order,cyclic_sublattice_rank=1,
                    coefficient_radius=M,m=m,base_size=len(base),sumset_size=len(sums),
                    coverage=len(sums)/E.N,height_bound=M*M*h,
                    full_MW_lattice_claim=False))
    write_result('SNFS-D1','Exact rank-one sublattice count/sumset control and reduction coverage',rows,
        ['No certified rank-5 to rank-31 lattices or saturation certificates were available.','This tests a non-torsion cyclic sublattice, not the full high-rank hypothesis or its cryptographic thresholds.'],
        dict(point_non_torsion_Nagell_Lutz=True,canonical_height_estimate=h,height_doubling_steps=6,
            corrected_coverage_inequality='r >= log(target_count/|F|)/log(m), where the model applies'))


def d2():
    P=(F(3),F(5));h=height(P,F(0),F(-2),6);rows=[]
    for bits in (8,12,16,20):
        p=int(prevprime(2**bits));a,b=0,p-2;s,t=0,-1
        assert a+p*s==0 and b+p*t==-2
        rows.append(dict(p=p,residue_a=a,residue_b=b,lift_s=s,lift_t=t,
            rational_curve='y^2=x^3-2',point=[3,5],height_estimate=h,
            height_over_log_p=h/math.log(p)))
    write_result('SNFS-D2','Fixed-small-curve lift control against a blanket log(p) height inference',rows,
        ['No rank distribution, conductor matching, 2-descent or full small-point coverage experiment executed.','This selected family is not a random-lift ensemble; it does not refute an empirical average-rank hypothesis.'])


def d3():
    rows=[]
    for p in (31,61):
        E=EC(p,2,3);gen=rng('SNFS-D3',str(p))
        for trial in range(30):
            while True:
                P0,Q0=gen.sample(E.points,2)
                if P0[0]==Q0[0]:continue
                x,y=map(F,P0);u,v=map(F,Q0)
                a=(y*y-v*v-x**3+u**3)/(x-u);b=y*y-x**3-a*x
                if 4*a**3+27*b*b:break
            P=(x,y);Q=(u,v)
            assert y*y==x**3+a*x+b and v*v==u**3+a*u+b
            assert (a.numerator*pow(a.denominator,-1,p))%p==E.a
            assert (b.numerator*pow(b.denominator,-1,p))%p==E.b
            relation=None
            ps={c:qmul(c,P,a,b) for c in range(-2,3)}
            qs={c:qmul(c,Q,a,b) for c in range(-2,3)}
            for c in range(-2,3):
                for d in range(-2,3):
                    if c==d==0:continue
                    if qadd(ps[c],qs[d],a,b) is None:relation=[c,d];break
                if relation:break
            rows.append(dict(p=p,trial=trial,lifted_points=[P0,Q0],
                relation_with_coefficients_at_most_2=relation,
                relation_kind=('single-point-torsion' if relation and 0 in relation
                               else 'two-point-relation' if relation else 'none-within-search'),
                rank_certified=False))
    # A planted exact dependence must be recovered by the same coefficient search.
    P=(F(3),F(5));Q=qmul(2,P,F(0),F(-2))
    assert qadd(qmul(2,P,F(0),F(-2)),qmul(-1,Q,F(0),F(-2)),F(0),F(-2)) is None
    write_result('SNFS-D3','Two-point fitted rational lifts; exhaustive small-coefficient dependence search',rows,
        ['Absence of a relation with |c_i|<=2 does not certify independence or rank.','The k=3,4 parametrized fitting families and exact full rank certificates remain unimplemented.'],
        dict(planted_dependence_control=[2,-1],trials=len(rows),
            small_dependence_count=sum(r['relation_with_coefficients_at_most_2'] is not None for r in rows)))


def mi(a,b):
    n=len(a);ct=Counter(zip(a,b));ca=Counter(a);cb=Counter(b)
    return sum(v/n*math.log2(v*n/(ca[x]*cb[y])) for (x,y),v in ct.items())


def d4():
    W=eds(0,-2,3,5);B=47;values=[W(n) for n in range(1,81)]
    sx=[smooth(v,B) for v in values];rows=[]
    for p in (53,59,61,67,71,73,79,83,89,97,101,127,151,191):
        E=EC(p,0,-2);order=E.order((3,5));ky=[v%p==0 for v in values]
        assert all(k==(n%order==0) for n,k in enumerate(ky,1))
        overlap=sum(s and k for s,k in zip(sx,ky));assert overlap==0
        rows.append(dict(p=p,point_order=order,B=B,indices=80,
            smooth_values=sum(sx),kernel_indices=sum(ky),smooth_kernel_overlap=overlap,
            descriptive_mutual_information_bits=mi(sx,ky)))
    write_result('SNFS-D4','Rank-one support falsification of the proposed smoothness/kernel independence test',rows,
        ['Rank-r net recurrence and HNF reconstruction were not implemented.','For every nonzero integral W and B<p, B-smooth(W) implies p does not divide W. This logical exclusion invalidates the original independence trigger; a nonzero MI here is not an exploitable attack signal.','The p-cofactor variant W/p requires prior kernel membership and does not itself find relations.'],
        dict(original_independence_test_invalid=True,zero_values_excluded=True,
            all_zero_apparition_checks_passed=True))


def BM(seq,p):
    C=[1];B=[1];L=0;m=1;b=1;profile=[]
    for N in range(len(seq)):
        d=(seq[N]+sum(C[i]*seq[N-i] for i in range(1,L+1)))%p
        if d==0:m+=1
        else:
            T=C[:];coef=d*pow(b,-1,p)%p
            if len(C)<len(B)+m:C += [0]*(len(B)+m-len(C))
            for i,v in enumerate(B):C[i+m]=(C[i+m]-coef*v)%p
            if 2*L<=N:L=N+1-L;B=T;b=d;m=1
            else:m+=1
        profile.append(L)
    return profile


def d5():
    rows=[]
    for p in (31,43,61,101,127):
        E=EC(p,0,-2);P=(3,5);order=E.order(P);W=eds(0,-2,3,5,p)
        length=10*order;seq=[W(i) for i in range(length)]
        prof=BM(seq,p)
        recurrence_checks=0
        for n in range(2,length-2):
            assert (seq[n+2]*seq[n-2]-seq[2]**2*seq[n+1]*seq[n-1]+seq[3]*seq[n]**2)%p==0
            recurrence_checks+=1
        # Discover quadratic relations in a window of five consecutive values.
        mons=[()] + [(i,) for i in range(5)] + [(i,j) for i in range(5) for j in range(i,5)]
        def feats(window):return [math.prod(window[i] for i in mon)%p for mon in mons]
        windows=[seq[i:i+5] for i in range(length-4)]
        train=[feats(w) for w in windows[:max(30,len(windows)//2)]]
        ns=nullspace(train,p);test=[feats(w) for w in windows[len(train):]]
        held=sum(all(sum(x*y for x,y in zip(v,row))%p==0 for row in test) for v in ns)
        rows.append(dict(p=p,point_order=order,sequence_length=length,
            profile=[dict(length=k*order,linear_complexity=prof[k*order-1]) for k in (1,2,4,10)],
            defining_quadratic_recurrence_checks=recurrence_checks,
            quadratic_window_span=4,training_nullity=len(ns),heldout_relations=held,
            interpretation='Includes the known defining Somos-type quadratic relation; no shortcut inferred'))
    write_result('SNFS-D5','Small-field EDS linear-complexity profiles and held-out quadratic recurrence controls',rows,
        ['No universal L/2 profile asserted; value period and zero-apparition rank are distinct.','Search covers quadratic degree and span four, not all degree-three/span-eight systems.','No period-finding acceleration or 40-bit-order sequence experiment demonstrated.'])


def f1():
    # K=Q(sqrt(3)), P=(0,sqrt(3)) on y^2=x^3+x+3.
    # It corresponds to (0,9) on the quadratic twist y^2=x^3+9x+81.
    twistP=(F(0),F(9));twice=qmul(2,twistP,F(9),F(81))
    assert twice[0]==F(1,4) # Nonintegral => not rational torsion, by Nagell-Lutz.
    h=height(twistP,F(9),F(81),6);rows=[]
    for n in range(4,41,2):
        p=2**n-3
        if not isprime(p):continue
        alpha=pow(2,n//2,p);assert alpha*alpha%p==3
        if (4+27*3**2)%p==0:
            rows.append(dict(p=p,n=n,status='bad-reduction-excluded',
                reason='The fixed curve discriminant vanishes; this is not an elliptic reduction.'))
            continue
        Q=(0,alpha);assert (Q[1]**2-Q[0]**3-Q[0]-3)%p==0
        rows.append(dict(p=p,n=n,status='good-degree-one-reduction',good_reduction=True,
            field_degree=2,field='Q(sqrt(3))',
            degree_one_prime_root=alpha,new_K_point='(0,sqrt(3))',
            twist_canonical_height_estimate=h,height_over_log_p=h/math.log(p)))
    write_result('SNFS-F1','Actual pseudo-Mersenne degree-one reductions of a fixed new non-torsion quadratic-field point',rows,
        ['No number-field descent, cubic/quintic fields, rank-gain distribution or full bounded-height coverage measurement executed.','The selected fixed curve/field supplies a height control, not a claim about a random ensemble.'],
        dict(non_torsion_control='Twice (0,9) on y^2=x^3+9x+81 has x=1/4, excluding rational torsion',
            height_convention='Canonical height on the isomorphic quadratic twist'))


if __name__=='__main__':
    for fn in (c1,c3,d1,d2,d3,d4,d5,f1):fn()
