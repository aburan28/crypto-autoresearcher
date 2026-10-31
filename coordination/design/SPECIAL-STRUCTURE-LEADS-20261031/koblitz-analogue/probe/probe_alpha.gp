\\ Probe 4 (NOT a result): alpha := Velu isogeny with rational 2-torsion kernel, composed with the
\\ F_p-isomorphism E'->E (x -> u2*x).  Check x(alpha(P)) = x([lambda]P) for lambda of order h.
{
run(p,l,m,h)=
  my(E0=ellinit([-35,-98],p),E,rts,s,lam,lamsols);
  E=if(ellcard(E0)==4*l*m,E0,ellinit(elltwist(E0)));
  print("p=",p," #E=",ellcard(E)," =4*l*m? ",ellcard(E)==4*l*m);
  rts=polrootsmod(x^3+E.a4*x+E.a6,p);
  s=qfbsolve(Qfb(1,1,2),l); lam=Mod(-s[1],l)/s[2];
  lamsols=[lift(lam),lift(1-lam)];
  for(k=1,#rts,
    my(isog=ellisogeny(E,[lift(rts[k]),0]),Ep=ellinit(isog[1]),u2,P,Q,xs,R,kk,n=0,ok=0,ordk=0);
    if(Ep.j!=E.j,print(" kernel ",k,": j(E') differs (conductor-2 order), not alpha");next);
    u2=(E.a6*Ep.a4)/(E.a4*Ep.a6);
    for(t=1,10,
      P=ellmul(E,random(E),4*m); if(P==[0],next); n++;
      Q=ellisogenyapply(isog[2],P); xs=Q[1]*u2;
      for(j=1,2, R=ellmul(E,P,lamsols[j]); if(R!=[0]&&R[1]==xs, ok++; ordk=lamsols[j])));
    print(" kernel ",k,": u2 square? ",issquare(u2),"  x(alpha P) = x([root]P) for ",ok,"/",n," points; matching root ",ordk,
          if(ordk,Str(" has order ",znorder(Mod(ordk,l))," mod l"),"")));
}
run(1051373,262543,1,19);
run(16781629,4196903,1,23);
quit
