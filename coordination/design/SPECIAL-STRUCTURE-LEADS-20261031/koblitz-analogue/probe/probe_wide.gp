\\ Feasibility probe (NOT a result). Question: do prime-order-N instances with CM by
\\ Z[(1+sqrt(-7))/2] and ord_N(lambda)=h exist for h in 16..24?  Recipe as in the idea:
\\ N | 2^h+1-L_h. Corrections tested here: p = N(1 +- 2*delta) (not 1 +- delta), #E = 4N.
lucas(n)={my(a=2,b=1,t);if(n==0,return(2));for(i=2,n,t=b-2*a;a=b;b=t);b};
{
tot=0;
for(h=16,100,
  M=2^h+1-lucas(h);
  F=factor(M)[,1]~;
  nN=0; ninst=0; line="";
  for(i=1,#F,
    N=F[i];
    if(N<2^16||N>2^34||N%7==0||kronecker(-7,N)!=1,next);
    nN++;
    s=qfbsolve(Qfb(1,1,2),N); x=s[1]; y=s[2];
    lam=Mod(-x,N)/y;
    for(c=1,2,
      l=if(c==1,lam,1-lam);
      if(znorder(l)!=h,next);
      a=2*x+y;
      for(sg=-1,1,
        if(sg==0,next);
        p=1+2*sg*a+4*N;
        if(!isprime(p),next);
        ninst++;
        neg=if(h%2==0,l^(h/2)==-1,0);
        line=concat(line,Str(" [N=",N," (",ceil(log(N)/log(2))," bit) p=",p," c=",c," sg=",sg," minus1_in_orbit=",neg,"]"))
      )
    )
  );
  tot+=ninst;
  if(ninst>0,print("h=",h," instances=",ninst,line))
);
print("total instances h=16..100: ",tot);
}
quit
