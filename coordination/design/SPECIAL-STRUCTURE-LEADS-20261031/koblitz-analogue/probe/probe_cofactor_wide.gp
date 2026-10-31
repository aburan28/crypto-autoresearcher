\\ Probe 2 (NOT a result): relax #E=4N to #E=4*l*m (m<=MMAX, l prime = the order of G).
\\ pool of primes l | 2^h+1-L_h with exact ord_l(lambda)=h, l in [2^20,2^34], 7 splits.
lucas(n)={my(a=2,b=1,t);if(n==0,return(2));for(i=2,n,t=b-2*a;a=b;b=t);b};
MMAX=40;
{
W=Mod(w,w^2-w+2);
tot=0; pool=0;
for(h=16,110,
  M=2^h+1-lucas(h); F=factor(M)[,1]~;
  for(i=1,#F, l=F[i];
    if(l<2^18||l>2^34||l%7==0||kronecker(-7,l)!=1,next);
    s=qfbsolve(Qfb(1,1,2),l); x=s[1]; y=s[2];
    for(c=1,2,
      lam=Mod(-x,l)/y; ll=if(c==1,lam,1-lam);
      if(znorder(ll)!=h,next);
      dl=if(c==1,x+y*W,x+y*(1-W)); \\ ideal generator whose reduction gives lambda
      n=0;
      for(m=1,MMAX, if(m%7==0||gcd(m,l)>1,next);
        for(u=-8,8,for(v=-8,8,
          if(u^2+u*v+2*v^2!=m,next);
          mu=u+v*W; d=dl*mu;
          for(sg=-1,1,if(sg==0,next);
            pi=1+2*sg*d; q=lift(pi); \\ poly in w
            \\ p = norm = pi*conj(pi); conj(w)=1-w
            a0=polcoeff(q,0); a1=polcoeff(q,1);
            p=a0^2+a0*a1+2*a1^2;
            if(isprime(p),n++))))
      );
      if(n>0,pool++;tot+=n;print("h=",h," l=",l," (",#binary(l)," bit) c=",c," #(m,mu,sign) giving prime p: ",n))
  )));
print("pool primes (l,c): ",pool," total curves: ",tot);
}
quit
