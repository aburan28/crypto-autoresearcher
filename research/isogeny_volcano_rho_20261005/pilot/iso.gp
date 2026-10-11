default(parisize,"1G");
m=37; lp=73;
\\ pick irreducible pentanomial/trinomial of degree 37 (lowest terms)
mod37=0; forstep(k=1,36,1, p=Mod(1,2)*(x^37+x^k+1); if(polisirreducible(p), mod37=p; break));
if(!mod37, forvec(v=[[1,35],[1,35],[1,35]], p=Mod(1,2)*(x^37+x^v[3]+x^v[2]+x^v[1]+1); if(polisirreducible(p),mod37=p;break),2));
print("MODULUS ", lift(mod37));
g=ffgen(mod37,'g); E=ellinit([1,0,0,0,1],g); N=ellcard(E); print("N ",N," = ",factor(N));
\\ order of Frobenius eigenvalue c=41 mod 73 is 18 => work in degree 37*18
n6=m*18; K=ffgen(ffinit(2,n6),'h); EK=ellinit([1,0,0,0,1],K);
P2=lift(Mod(-x,x^2-x+2)^n6); N6=2^n6+1-(2*polcoeff(P2,0)+polcoeff(P2,1)); e=valuation(N6,lp); print("v73(#E(F_2^666)) = ",e);
emb=ffembed(g,K); inv=ffinvmap(emb);
curves=List(); js=List([E.j]);
setrand(20261005);
for(trial=1,40, R=random(EK); P=ellmul(EK,R,N6/lp^e); if(P==[0],next); \
  while(ellmul(EK,P,lp)!=[0], P=ellmul(EK,P,lp)); \
  xs=vector((lp-1)/2,i,ellmul(EK,P,i)[1]); h=prod(i=1,#xs,'X-xs[i]); \
  hc=vector(poldegree(h,'X)+1,i,ffmap(inv,polcoeff(h,i-1,'X))); \
  if(#select(c->c==[],hc), print("coeff not in subfield?"); next); \
  h37=sum(i=1,#hc,hc[i]*'X^(i-1)); \
  Ei=ellisogeny(E,h37,1); Ei=ellinit(Ei,g); \
  if(ellcard(Ei)!=N, print("CARD MISMATCH"); next); \
  j=Ei.j; if(setsearch(Set(Vec(js)),j), next); listput(js,j); \
  a2=-1; for(t=0,1, C=ellinit([1,t,0,0,1/j],g); if(ellcard(C)==N, a2=t; break)); \
  listput(curves,[a2,1/j]); print("curve ",#curves,": j-invariant new, a2=",a2," #E'=N ok"); \
  if(#curves>=8, break));
\\ export: integers for b in polynomial basis
toint(z)=subst(lift(z.pol),variable(z.pol),2);
print("EXPORT_MOD ", subst(lift(mod37),x,2));
print("EXPORT_N ", N);
for(i=1,#curves, print("EXPORT_CURVE ", curves[i][1], " ", toint(curves[i][2])));
