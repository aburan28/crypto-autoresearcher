"""Prime-power ideals by Hensel lifts and elementary Gauss reduction."""
import json,math,sys,traceback
from pathlib import Path
P=Path(__file__).resolve().parent
def prime(n):return n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))
def choice(D):
    for q in range(3,10001,2):
        if prime(q) and pow(D%q,(q-1)//2,q)==1:
            return q,next(b for b in range(1,2*q,2) if (b*b-D)%(4*q)==0)
    raise RuntimeError('fixed prime cap reached')
def reduce_form(a,b,c):
    D=b*b-4*a*c;assert D<0 and a>0 and math.gcd(a,math.gcd(b,c))==1
    for _ in range(10000):
        m=(a-b)//(2*a);c,b=c+b*m+a*m*m,b+2*a*m
        if a>c:a,b,c=c,-b,a;continue
        if (a==c or abs(b)==a) and b<0:b=-b
        assert abs(b)<=a<=c and b*b-4*a*c==D
        return [a,b,c]
    raise RuntimeError('reduction watchdog')
def powers(D,limit):
    assert D<0 and D%4==1
    q,b=choice(D);a=q;out=[];identity=[1,1,(1-D)//4];first=0
    for m in range(1,limit):
        c=(b*b-D)//(4*a);assert b*b-4*a*c==D
        r=reduce_form(a,b,c);out.append(r)
        if r==identity:first=m;break
        k=(-c*pow(b,-1,q))%q;b+=2*a*k;a*=q
    return [q,first,out]
def fundamental(D,factors):
    core=math.prod(int(q) for q,e in factors if e%2)
    return D==(-core if (-core)%4==1 else -4*core)
def controls():
    assert powers(-23,3)[1]==0 and powers(-23,4)[1]==3
    assert powers(-15,3)[1]==2 and powers(-7,200)[1]==1
    assert not fundamental(-75,[(3,1),(5,2)])
    assert powers(-23,4)==powers(-23,4)
    return [powers(-23,3),powers(-23,4),powers(-15,3),powers(-7,200)]
def body():
    if '--fault-exception' in sys.argv:raise RuntimeError('injected exception')
    if '--fault-early' in sys.argv:return False
    print('CONTROLS '+json.dumps(controls(),separators=(',',':')),flush=True)
    if '--controls-only' in sys.argv:return True
    for i,r in enumerate(json.loads((P/'INPUTS.json').read_text())['rows']):
        v=r['cm_record']
        if v:
            D=int(v['D_K']);delta=int(v['delta']);f=int(v['f_pi']);p,n=int(r['p']),int(r['n'])
            assert delta==(p+1-n)**2-4*p==f*f*D
            assert math.prod(int(q)**e for q,e in v['factors'])==-delta and fundamental(D,v['factors'])
            value=powers(D,200)
        else:D=0;value=[0,0,[]]
        raw=json.dumps(value,separators=(',',':'))+'\n';assert len(raw.encode())<65536
        (P/'runs/element-01/python'/('case-'+str(i)+'.json')).write_text(raw)
        print(json.dumps([i,D,value[0],value[1],len(value[2])],separators=(',',':')),flush=True)
    return True
if __name__=='__main__':
    try:
        if body() is not True:raise RuntimeError('missing completion sentinel')
        print('COMPLETE',flush=True)
    except BaseException:traceback.print_exc();sys.exit(1)
