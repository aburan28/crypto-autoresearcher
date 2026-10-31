\\ Independent prime generation, Kronecker symbols and source-prime proofs.
check(x)={if(!x,error("assertion failed"))};
cert(D,k)={my(q=1,L=List(),Q=1);while(#L<k,q=nextprime(q+1);if(q>10000,error("prime cap"));if(kronecker(D,q)==1,listput(L,q);Q*=q));[Vec(L),Q,4*Q<abs(D)]};
check(cert(-23,1)==[[2],2,1]);check(cert(-15,1)==[[2],2,1]);check(qfbclassno(-23)==3);check(qfbclassno(-15)==2);
check(cert(-7,1)==[[2],2,0]);check(qfbclassno(-7)==1);check(!isfundamental(-75));check(cert(-23,1)==cert(-23,1));print("CONTROLS PASS");
for(i=1,#rows,my(r=rows[i],D=r[4],core=1,prod=1,seen=Set([]),v);if(D==0,print([r[1],0,24,[],0,0]),check(D<0);check(r[6]==(r[2]+1-r[3])^2-4*r[2]);check(r[6]==r[5]^2*D);for(j=1,#r[7],my(q=r[7][j][1],e=r[7][j][2]);check(isprime(q));check(e>0);check(!setsearch(seen,q));seen=setunion(seen,[q]);prod*=q^e;if(e%2,core*=q));check(prod==-r[6]);check(D==if((-core)%4==1,-core,-4*core));v=cert(D,24);print([r[1],D,24,v[1],v[2],v[3]])));
print("COMPLETE");quit;
