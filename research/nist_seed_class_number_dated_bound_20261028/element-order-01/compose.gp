check(x)={if(!x,error("assertion failed"))};
choice(D)={my(q=2,b);while(1,q=nextprime(q+1);if(q>10000,error("prime cap"));if(kronecker(D,q)==1,b=1;while((b*b-D)%(4*q),b+=2);return([q,b])))};
classpowers(D,lim)={my(v=choice(D),q=v[1],b=v[2],F=Qfb(q,b,(b*b-D)/(4*q)),idf=Qfb(1,1,(1-D)/4),t=idf,L=List(),first=0);for(m=1,lim-1,t=qfbcomp(t,F);listput(L,Vec(t));if(t==idf,first=m;break));[q,first,Vec(L)]};
check(classpowers(-23,3)[2]==0);check(classpowers(-23,4)[2]==3);check(classpowers(-15,3)[2]==2);check(classpowers(-7,200)[2]==1);check(!isfundamental(-75));check(classpowers(-23,4)==classpowers(-23,4));print("CONTROLS ",[classpowers(-23,3),classpowers(-23,4),classpowers(-15,3),classpowers(-7,200)]);
for(i=1,#rows,my(r=rows[i],D=r[4],core=1,prod=1,v);if(D==0,v=[0,0,[]],check(D<0);check(r[6]==(r[2]+1-r[3])^2-4*r[2]);check(r[6]==r[5]^2*D);for(j=1,#r[7],my(q=r[7][j][1],e=r[7][j][2]);check(isprime(q));prod*=q^e;if(e%2,core*=q));check(prod==-r[6]);check(D==if((-core)%4==1,-core,-4*core));v=classpowers(D,200));write(Str("runs/element-01/gp/case-",i-1,".json"),v);print([r[1],D,v[1],v[2],#v[3]]));
print("COMPLETE");quit;
