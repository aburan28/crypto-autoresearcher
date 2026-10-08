m=131; P=lift(Mod(-x,x^2-x+2)^m); X=polcoeff(P,0); Y=polcoeff(P,1); tr=2*X+Y; N=2^m+1-tr; f=abs(Y);
print("trace ",tr); print("N = ",factor(N)); print("conductor [O_K:Z[pi]] = ",factor(f));
foreach(factor(f)[,1]~, p, c=X%p; print("l=",p,": kron(-7,l)=",kronecker(-7,p),"  pi = c mod l, c=",c, "  ord(c)=",znorder(Mod(c,p)),"  ord(-c)=",znorder(Mod(-c,p)), "  isprime ",isprime(p)));
hf(ff)=my(G=factor(ff)[,1]); ff*prod(i=1,#G,1-kronecker(-7,G[i])/G[i]);
F=factor(f)[,1]; foreach([1,F[1],F[2],f],ff, print("conductor ",ff,": h = ",hf(ff)));
ordq(D,p,cap)=my(Q=qfbprimeform(D,p),R=Q,k=1,I=qfbpow(Q,0)); while(qfbred(R)!=qfbred(I) && k<cap, R=qfbcomp(R,Q); k++); k;
forprime(p=3,60, if(kronecker(-7,p)==1 && p!=263, print("ord[l_",p,"] in Cl(-7*263^2): ",ordq(-7*263^2,p,1000))));
