cm(D,bits)={my(v,p,t,N,H,r,E,tries=0,m);
 H=polclass(D);
 while(tries<200000,
  tries++;
  v=random(2^(bits\2-3))+1; m=2^(bits\2)+random(2^(bits\2));
  t=m; if((t^2-D*v^2)%4!=0,next);
  p=(t^2-D*v^2)/4; if(p<2^(bits-1)||p>=2^bits||!isprime(p),next);
  r=polrootsmod(H,p); if(#r==0,next);
  E=ellinit(ellfromj(r[1]),p);
  N=ellcard(E); if(isprime(N),return([p,N,p+1-N,D,v]));
  N=ellcard(ellinit(elltwist(E),p)); if(isprime(N),return([p,N,"twist",D,v])));
 0}
default(parisize,"256M");
print(cm(-163,30));print(cm(-163,30));print(cm(-3*49,30));print(cm(-7*9,32));
