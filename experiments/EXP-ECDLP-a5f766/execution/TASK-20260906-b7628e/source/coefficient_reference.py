"""Separate closed coefficient expansions; no direct-ring module imports."""
def calculate(p,name,u0,v,c):
    if name == "C":
        A,B,x,y = (3,0),(-11,0),(3,0),(5,0)
    elif name == "V":
        A,B,x,y = (3,6),(-11,-8),(3,0),(5,1)
    else:
        A,B,x,y = (3,12),(-11,-66),(3,6),(5,15)
    q=[]
    for (a,b),weight in zip((A,B,x,y),(4,6,2,3)):
        scale=pow(u0,weight,p)
        q.append([(scale*a)%p,(c*scale*(b+weight*v*a))%p])
    a0,a1=q[0]
    x0,x1=q[2]
    inv=pow(a0,-1,p)
    return dict(coords=q,F=[x0*x0*inv%p,(2*x0*x1*inv-x0*x0*a1*inv*inv)%p])

def hasse(p):
    coeff=[1]
    for _ in range((p-1)//2):
        out=[0]*(len(coeff)+3)
        for i,a in enumerate(coeff):
            for j,b in ((0,-11),(1,3),(3,1)):
                out[i+j]=(out[i+j]+a*b)%p
        coeff=out
    return coeff[p-1]
