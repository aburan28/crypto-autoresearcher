\\ horizontal isogeny cycles over F_2^41 with classical modular polynomials (l split in Q(sqrt(-7)), l not | conductor)
g=ffgen(Mod(1,2)*(x^41+x^3+1),'g);
fromint(n)=my(s=0*g,k=0); while(n, if(n%2, s+=g^k); n\=2; k++); s;
toint(z)=subst(lift(z.pol),variable(z.pol),2);
PHI=Map(); phi(l)=if(!mapisdefined(PHI,l), mapput(PHI,l,polmodular(l,,,'Y))); mapget(PHI,l);
roots_q(l,j)=my(F=factor(subst(phi(l),'x,j)*g^0)[,1]); apply(f->-polcoeff(f,0)/polcoeff(f,1), select(f->poldegree(f)==1, F~));
\\ walk the horizontal l-cycle through E_b; return the list of b' = 1/j' visited (stops on return or after cap steps)
{walkl(l,b,cap)=my(j0=1/fromint(b), r=roots_q(l,j0), prev=j0, cur=r[1], out=List([b]));
  while(cur!=j0 && #out<cap, listput(out,toint(1/cur)); my(rr=roots_q(l,cur), nx=0);
    for(i=1,#rr, if(rr[i]!=prev, nx=rr[i])); if(nx==0,nx=prev); prev=cur; cur=nx);
  [cur==j0, Vec(out)]}
cyc(l,b,cap)=my(w=walkl(l,b,cap)); if(w[1], #w[2], -1);
