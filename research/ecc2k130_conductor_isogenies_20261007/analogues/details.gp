ordq(D,p,cap)=my(Q=qfbprimeform(D,p),R=Q,k=1,I=qfbpow(Q,0)); while(qfbred(R)!=qfbred(I) && k<cap, R=qfbcomp(R,Q); k++); k;
hf(ff)=my(G=factor(ff)[,1]); ff*prod(i=1,#G,1-kronecker(-7,G[i])/G[i]);
{foreach([[163,1,[45641,82153]],[109,1,[3271]],[103,0,[11329]]], C,
  my(m=C[1], a=C[2], mu=if(a,1,-1), P=lift(Mod(x,x^2-mu*x+2)^m), X=polcoeff(P,0));
  print("== m=",m," a=",a);
  foreach(C[3], p, my(c=Mod(X,p), o=znorder(c), half=(o%2==0 && c^(o/2)==-1), k=if(half,o/2,o));
    print("  l'=",p," kron=",kronecker(-7,p)," ord(c)=",o," k=",k," kernel on ",if(half,"TWIST","E")," over F_2^(",m,"*",k,")  h(floor)=",hf(p)));
  my(lv=concat([1],C[3])); if(#C[3]==2, lv=concat(lv,[C[3][1]*C[3][2]]));
  forprime(s=3,80, if(kronecker(-7,s)==1 && !setsearch(Set(C[3]),s), print1("  ord[l_",s,"] by level ",lv,": "); foreach(lv,ff, print1(ordq(-7*ff^2,s,100000)," ")); print())))}
