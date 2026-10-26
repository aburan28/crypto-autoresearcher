#!/usr/bin/env python3
"""Constructed d=3 sum certificates; this is not a relation-search solver."""
import hashlib,json,sys,time
from pathlib import Path
from arithmetic import P,TARGET,TARGET_R,TARGET_B,add,mul,neg,on_curve

def determinant(matrix):
    matrix=[row[:] for row in matrix];value=1
    for k in range(len(matrix)):
        pivot=next((i for i in range(k,len(matrix)) if matrix[i][k]%P),None)
        if pivot is None:return 0
        if pivot!=k:matrix[pivot],matrix[k]=matrix[k],matrix[pivot];value=-value
        v=matrix[k][k]%P;value=value*v%P;iv=pow(v,-1,P)
        for i in range(k+1,len(matrix)):
            c=matrix[i][k]*iv%P
            for j in range(k+1,len(matrix)):matrix[i][j]=(matrix[i][j]-c*matrix[k][j])%P
    return value%P

def f3coeff(u,v):
    a=-3;b=TARGET_B
    return [((u-v)**2)%P,(-2*((u+v)*(u*v+a)+2*b))%P,
            ((u*v-a)**2-4*b*(u+v))%P]

def direct_s4(u,v,w,t):
    a,b,c=f3coeff(u,v);d,e,f=f3coeff(w,t)
    return determinant([[a,b,c,0],[0,a,b,c],[d,e,f,0],[0,d,e,f]])

def main():
    root=Path(__file__).resolve().parent;source=root/'receipts/validation-001'
    out=root/'receipts/relation-positive.json'
    if out.exists():raise SystemExit('refusing to overwrite receipt')
    baseline=root.parent.parent/'baseline/s4-symmetric.json'
    terms=json.loads(baseline.read_text())['terms'];checks=0;certs=[];start=time.monotonic()
    for sp in sorted((source/'cases').glob('*/summary.json')):
        summary=json.loads(sp.read_text());rows=[]
        for chunk in summary['certificate_chunks']:rows.extend(json.loads((source/chunk).read_text()))
        accepted=sorted((row for row in rows if row['target_point'] is not None),key=lambda row:row['x'])
        matched=accepted[:summary['matched_accepted_M']]
        points=[tuple(row['target_point']) for row in matched[:3]]
        target=add(add(points[0],points[1],TARGET),points[2],TARGET)
        assert target is not None and mul(TARGET_R,target,TARGET) is None;checks+=1
        xs=[point[0] for point in points];s1=sum(xs)%P;s2=(xs[0]*xs[1]+xs[0]*xs[2]+xs[1]*xs[2])%P;s3=xs[0]*xs[1]*xs[2]%P
        variables=dict(a=-3,b=TARGET_B,t=target[0])
        sym=sum(pow(s1,exponents[0],P)*pow(s2,exponents[1],P)*pow(s3,exponents[2],P)*
                eval(expression,{'__builtins__':{}},variables) for exponents,expression in terms)%P
        direct=direct_s4(*xs,target[0])
        assert sym==direct==0;checks+=1
        assert add(add(add(points[0],points[1],TARGET),points[2],TARGET),neg(target),TARGET) is None;checks+=1
        assert len(set(xs))==3 and all(row['x'] in {item['x'] for item in matched} for row in matched[:3]);checks+=1
        certs.append(dict(case=summary['case'],d=3,matched_M=summary['matched_accepted_M'],
                          points=[list(point) for point in points],target=list(target),
                          sign_vector=[1,1,1],direct_point_sum='P1+P2+P3-Q=O',
                          symmetric_variables=[s1,s2,s3],S4_symmetric_value=sym,S4_resultant_value=direct,
                          construction='first three accepted x in sorted matched base; Q is their sum',
                          recovery_claim=False))
    result=dict(status='PASS',checks=checks,cases=len(certs),certificates=certs,
                scope='constructed positive arithmetic controls, no search or target-distribution evidence',
                baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                command=[sys.executable,*sys.argv],validation_wall_seconds=time.monotonic()-start)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'checks':checks,'cases':len(certs)}))
if __name__=='__main__':main()
