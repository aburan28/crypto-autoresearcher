default(parisize,"1G");
g=ffgen(Mod(1,2)*(x^37+x^9+x^2+x+1),'g); E=ellinit([1,0,0,0,1],g); N=ellcard(E); lp=73;
toint(z)=subst(lift(z.pol),variable(z.pol),2);
K=ffgen(ffinit(2,37*18),'h); EK=ellinit([1,0,0,0,1],K); emb=ffembed(g,K); inv=ffinvmap(emb);
P18=lift(Mod(-x,x^2-x+2)^(37*18)); N18=2^(37*18)+1-(2*polcoeff(P18,0)+polcoeff(P18,1));
setrand(1); js=Map(); res=List();
{while(#res<74, my(P=ellmul(EK,random(EK),N18/lp^2)); if(P==[0]||ellmul(EK,P,lp)!=[0],next);
  my(h=prod(i=1,36,'X-ellmul(EK,P,i)[1])); my(h37=sum(i=0,36,ffmap(inv,polcoeff(h,i,'X))*'X^i));
  my(Ei=ellinit(ellisogeny(E,h37,1),g)); if(ellcard(Ei)!=N,error("card"));
  my(j=Ei.j); if(mapisdefined(js,j),next); mapput(js,j,1); listput(res,toint(1/j)));}
print("FLOOR73 ", Vec(res));
\\ order of the class of a prime above 11 in Cl(-7 f^2) for each conductor
ordq(D,p)=my(Q=qfbprimeform(D,p),R=Q,k=1,I=qfbpow(Q,0)); while(qfbred(R)!=qfbred(I), R=qfbcomp(R,Q); k++); k;
foreach([1,73,2663,194399],f, print("CYCLE11 f=",f," ord=",ordq(-7*f^2,11)," h=",qfbclassno(-7*f^2)));
