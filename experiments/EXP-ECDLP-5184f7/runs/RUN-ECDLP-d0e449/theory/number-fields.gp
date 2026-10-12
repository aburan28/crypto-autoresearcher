F=[x^3-x-1,x^7-x^3+1];K=[64,32];
for(i=1,2,f=F[i];nf=nfinit(f);p=subst(f,x,2^K[i]);print([i,polisirreducible(f),poldegree(f),nf.sign,poldisc(f),nf.disc,nf.index,p,subst(f,x,2^K[i])%p]));
quit;
