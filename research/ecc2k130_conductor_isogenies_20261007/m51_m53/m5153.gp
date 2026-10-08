hf(ff)=my(G=factor(ff)[,1]); ff*prod(i=1,#G,1-kronecker(-7,G[i])/G[i]);
{foreach([51,53], m, for(a=0,1, my(mu=if(a,1,-1), P=lift(Mod(x,x^2-mu*x+2)^m), X=polcoeff(P,0), Y=polcoeff(P,1), tr=2*X+mu*Y, N=2^m+1-tr, F=factor(N), l=F[#F~,1], f=abs(Y));
  print("m=",m," a=",a,"  #E = ",F,"  largest prime 2^",round(log(l)/log(2)*10)/10,"  cofactor ",N/l);
  print("   f_pi = ",factor(f));
  foreach(factor(f)[,1]~, p, my(c=Mod(X,p), o=znorder(c), k=if(o%2==0 && c^(o/2)==-1, o/2, o));
    print("   l'=",p,": ",if(kronecker(-7,p)==1,"split",if(kronecker(-7,p)==-1,"inert","ramified")),", k=",k," -> kernel field F_2^",m*k,", floor class number h=",hf(p),
      ", |D| = 7*l'^2 = ",7*p^2))))}
