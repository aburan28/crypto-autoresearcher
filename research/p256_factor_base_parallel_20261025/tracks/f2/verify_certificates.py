#!/usr/bin/env python3
"""Certificate replay using independent Jacobian subgroup checks.

The producer uses affine addition/inversion; this replayer uses projective
short-Weierstrass formulas for target [r] checks and degree/cardinality
completeness rather than the producer's polynomial product check.
"""
import argparse,hashlib,json,math,sys,time,traceback
from pathlib import Path
from arithmetic import P,TARGET_B,TARGET_R,AUX,TARGET,on_curve,map_chain

def jd(point,a):
    x,y,z=point
    if not z or not y: return (1,1,0)
    aa=x*x%P;bb=y*y%P;cc=bb*bb%P
    dd=2*((x+bb)**2-aa-cc)%P
    ee=(3*aa+a*pow(z,4,P))%P;ff=ee*ee%P
    xx=(ff-2*dd)%P
    return xx,(ee*(dd-xx)-8*cc)%P,2*y*z%P

def jm(left,right,a):
    x,y,z=left;u,v=right
    if z==0: return u,v,1
    zz=z*z%P;uu=u*zz%P;ss=v*zz*z%P
    h=(uu-x)%P;r=(ss-y)%P
    if h==0: return jd(left,a) if r==0 else (1,1,0)
    hh=h*h%P;hhh=hh*h%P;xh=x*hh%P
    xx=(r*r-hhh-2*xh)%P
    return xx,(r*(xh-xx)-y*hhh)%P,z*h%P

def scalar(n,point,a):
    q=(1,1,0)
    for bit in bin(n)[2:]:
        q=jd(q,a)
        if bit=='1': q=jm(q,point,a)
    return q

def affine(q):
    x,y,z=q
    if not z:return None
    zi=pow(z,-1,P)
    return x*zi*zi%P,y*zi*zi*zi%P

def replay(source,corrupt=False):
    checks=0
    def require(truth,message):
        nonlocal checks
        checks+=1
        if not truth: raise AssertionError(message)
    receipt=json.loads((source/'receipt.json').read_text())
    for relative,digest in receipt['artifact_sha256'].items():
        require(hashlib.sha256((source/relative).read_bytes()).hexdigest()==digest,'receipt digest '+relative)
    gen=json.loads((source/'generator.json').read_text());h=tuple(gen['generator'])
    require(on_curve(h,AUX),'aux generator equation')
    require(scalar(2**96,h,1)[2]==0 and scalar(2**95,h,1)[2]!=0,'independent exact 2^96 order')
    require(math.gcd(P+1,TARGET_R)==1,'no nonzero rational target-to-aux group homomorphism')
    require(P+1-TARGET_R!=0,'target and auxiliary rational isogeny classes differ')
    chain=json.loads((source/'chain.json').read_text());edges=chain['edges']
    total=0;accepted=0;cases=[];corruption_used=False
    for summarypath in sorted((source/'cases').glob('*/summary.json')):
        summary=json.loads(summarypath.read_text());rows=[]
        for chunk in summary['certificate_chunks']: rows.extend(json.loads((source/chunk).read_text()))
        family=summary['family'];meta=summary['metadata'];values=set();acc=0
        for row in rows:
            xx=row['x'];values.add(xx)
            if family=='elliptic_generic':
                aux=tuple(row['auxiliary_point'])
                require(aux[0]==xx and on_curve(aux,AUX),'auxiliary coset equation')
                require(map_chain(aux,edges[:meta['chain_length']])==tuple(meta['endpoint']),'generic fibre exact image')
            elif family=='elliptic_kernel':
                aux=tuple(row['auxiliary_point'])
                require(aux[0]==xx and on_curve(aux,AUX),'auxiliary kernel equation')
                require(map_chain(aux,edges[:meta['chain_length']]) is None,'kernel exact image')
            else:
                a,b=row['torus_point']
                require((a*a+b*b)%P==1 and 2*a%P==xx,'torus coordinate certificate')
                value=xx
                for _ in range(meta['composition_depth']):value=(value*value-2)%P
                require(value==meta['terminal'],'Dickson exact fibre membership')
            target=row['target_point']
            if target is None:
                require(pow((xx**3-3*xx+TARGET_B)%P,(P-1)//2,P)==P-1,'certified target lift rejection')
            else:
                if corrupt and not corruption_used:
                    target[1]=(target[1]+1)%P;corruption_used=True
                target=tuple(target)
                require(target[0]==xx and on_curve(target,TARGET),'target lift equation')
                require(0<target[1]<=P//2,'target canonical sign')
                require(scalar(TARGET_R,target,-3)[2]==0,'independent target [r] certificate')
                acc+=1
            total+=1
        require(len(values)==summary['raw_x_size']==len(rows),'complete distinct domain cardinality')
        require(acc==summary['accepted_x_size'],'accepted count')
        require(len(rows)-acc==summary['rejected_x_size'],'rejected count')
        # Completeness follows from the degree bound for generic finite fibres,
        # or from the known cyclic kernel cardinality modulo +/- and O.
        if family=='elliptic_kernel':
            require(summary['raw_x_size']==meta['kernel_order']//2,'complete kernel x domain bound')
        elif family=='elliptic_generic':
            require(summary['raw_x_size']==2**meta['chain_length'],'complete degree bound')
            require(meta['endpoint'][1]!=0,'generic sign-pair disjointness')
        else:
            require(summary['raw_x_size']==2**meta['composition_depth'],'complete polynomial degree bound')
        accepted+=acc;cases.append(dict(case=summary['case'],rows=len(rows),accepted=acc))
    require(not corrupt or corruption_used,'corruption control found a target')
    # Independent Jacobian-vs-affine base controls at small known scalars.
    from arithmetic import mul
    for n in [0,1,2,3,7,31,256,65537]:
        require(affine(scalar(n,h,1))==mul(n,h,AUX),'Jacobian arithmetic cross-check')
    return dict(status='PASS',checks=checks,rows=total,accepted_lifts=accepted,cases=cases,
                target_trace=P+1-TARGET_R,gcd_target_order_auxiliary_order=math.gcd(P+1,TARGET_R),
                independent_arithmetic='Jacobian target subgroup check vs affine producer',
                independent_session=False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--receipt',required=True,type=Path);parser.add_argument('--corrupt-target',action='store_true')
    args=parser.parse_args();start=time.monotonic()
    if args.receipt.exists():raise SystemExit('refusing to overwrite receipt')
    error=None
    try:result=replay(args.source,args.corrupt_target)
    except BaseException as exception:
        error=type(exception).__name__+': '+str(exception)
        result=dict(status='FAIL',error=error,traceback=traceback.format_exc())
    result.update(command=[sys.executable,*sys.argv],validation_wall_seconds=time.monotonic()-start,
                  verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  arithmetic_sha256=hashlib.sha256(Path(__file__).with_name('arithmetic.py').read_bytes()).hexdigest(),
                  control='mutated target y' if args.corrupt_target else None)
    args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result))
    return 1 if error else 0
if __name__=='__main__':sys.exit(main())
