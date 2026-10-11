\\ usage: gp -q -s 1G classify_all.gp < /dev/null  with input list in hits_in.gp (hits=[...])
read("classify.gp"); read("floor73_set.gp"); read("hits_in.gp");
F73=Set(floor73);
conjmin(b)=my(z=fromint(b),m=b); for(i=1,36, z=z^2; m=min(m,toint(z))); m;
orbsize(b)=my(z=fromint(b),w=z); for(i=1,37, w=w^2; if(w==z, return(i)));
{for(i=1,#hits, my(b=hits[i], z=fromint(b), E=ellinit([1,0,0,0,z],g), c=ellcard(E), s=scalar73(z), lev);
  if(c!=N, print("REJECT ",b," card ",c); next);
  lev = if(b==1,"crater", if(s, "floor2663", if(setsearch(F73,b), "floor73", "bottom")));
  print("CLS ",b,",",lev,",",s,",",ellgroup(E)[1],",",orbsize(b),",",conjmin(b)))}
