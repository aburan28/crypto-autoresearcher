\\ Probe 3 (NOT a result): build one instance end to end and verify alpha on real points.
W=Mod(w,w^2-w+2);
{
find(h,l)=my(s,x,y,res=0);
  s=qfbsolve(Qfb(1,1,2),l); x=s[1]; y=s[2];
  for(c=1,2,
    my(lam=Mod(-x,l)/y, ll=if(c==1,lam,1-lam), dl);
    if(znorder(ll)!=h,next);
    dl=if(c==1,x+y*W,x+y*(1-W));
    for(m=1,40,
      if(m%7==0||gcd(m,l)>1,next);
      for(u=-8,8,for(v=-8,8,
        if(u^2+u*v+2*v^2!=m,next);
        my(d=dl*(u+v*W));
        for(sg=-1,1,
          if(sg==0,next);
          my(q=lift(1+2*sg*d),a0=polcoeff(q,0),a1=polcoeff(q,1),p=a0^2+a0*a1+2*a1^2);
          if(res==0&&isprime(p),res=[c,m,p,ll]))))));
  res;
}
{
chk(h,l)=my(r=find(h,l),c,m,p,ll,E0,E,card,rts,G,isog,Ep,P,Q,R,lam,ok);
  if(r==0,print("no instance");return);
  c=r[1];m=r[2];p=r[3];ll=r[4];
  print("h=",h," l=",l," m=",m," p=",p," (",#binary(p)," bit) conj-choice c=",c);
  E0=ellinit([-35,-98],p); card=ellcard(E0);
  E=if(card==4*l*m,E0,ellinit(elltwist(E0)));
  print("#E=",ellcard(E)," expected 4*l*m=",4*l*m," group ",ellgroup(E));
  rts=polrootsmod(x^3+E.a4*x+E.a6,p);
  print("rational 2-torsion points: ",#rts);
  P=ellmul(E,random(E),4*m);
  while(P==[0],P=ellmul(E,random(E),4*m));
  for(k=1,#rts,
    isog=ellisogeny(E,[lift(rts[k]),0]); Ep=ellinit(isog[1]);
    print(" kernel x0=",lift(rts[k])," j(E')=",Ep.j," CM-7 j=",Mod(-3375,p)));
  print("lambda conj root orders: ord(lam)=",znorder(ll)," ord(2/lam)=",znorder(2/ll));
}
chk(19,262543);
chk(23,4196903);
quit
