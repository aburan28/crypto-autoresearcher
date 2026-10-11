g=ffgen(Mod(1,2)*(x^37+x^9+x^2+x+1),'g);
fromint(n)=my(s=0*g,k=0); while(n, if(n%2, s+=g^k); n\=2; k++); s;
Phi=polmodular(11,,,'Y);
roots_q(j)=my(F=factor(subst(Phi,'x,j)*g^0)[,1]); apply(f->-polcoeff(f,0)/polcoeff(f,1), select(f->poldegree(f)==1, F~));
\\ length of the horizontal 11-isogeny cycle through E_b (= order of [l_11] in Cl(End E))
{cyc11(b)=my(j0=1/fromint(b), r=roots_q(j0), prev=j0, cur=r[1], n=1);
  while(cur!=j0 && n<300000, my(rr=roots_q(cur), nx=0);
    for(i=1,#rr, if(rr[i]!=prev, nx=rr[i])); if(nx==0,nx=prev); prev=cur; cur=nx; n++); n}
