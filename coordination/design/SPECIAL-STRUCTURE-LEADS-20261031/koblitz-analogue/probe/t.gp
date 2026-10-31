p=1051373;l=262543;
E0=ellinit([-35,-98],p);print(ellcard(E0)," ",4*l);
E=if(ellcard(E0)==4*l,E0,ellinit(elltwist(E0)));print(E[1..5]);
rts=polrootsmod(x^3+E.a4*x+E.a6,p);
for(k=1,3,
 isog=ellisogeny(E,[lift(rts[k]),0]);Ep=ellinit(isog[1]);
 if(Ep.j!=E.j,next);
 P=ellmul(E,random(E),4);while(P==[0],P=ellmul(E,random(E),4));
 Q=ellisogenyapply(isog[2],P);
 print("on curve E': ",ellisoncurve(Ep,Q)," Ep a4,a6=",Ep.a4," ",Ep.a6," E ",E.a4," ",E.a6);
 u2=(E.a6*Ep.a4)/(E.a4*Ep.a6);
 xs=Q[1]*u2; 
 print(" u2 is square? ",issquare(u2));
 R=P; found=0;
 for(j=1,l, if(R!=[0]&&R[1]==xs,print(" x match at k=",j," lam=",j%l);found=1;break); R=elladd(E,R,P));
 if(!found,print(" no k found for x*u2"));
 R=P; xs2=Q[1]/u2; for(j=1,l, if(R!=[0]&&R[1]==xs2,print(" x match (1/u2) at k=",j);break); R=elladd(E,R,P));
);
s=qfbsolve(Qfb(1,1,2),l);x=s[1];y=s[2];lam=Mod(-x,l)/y;print("roots: ",lift(lam)," ",lift(1-lam));
quit
