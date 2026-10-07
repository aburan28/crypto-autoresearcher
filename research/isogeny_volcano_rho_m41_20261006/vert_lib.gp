\\ One vertical isogeny from the crater (y^2+xy=x^3+1, defined over F_2) to each floor.
\\ Kernel x-coordinates via x-only Lopez-Dahab arithmetic in F_2^(41k) (no subfield embedding needed).
\\ Char-2 Velu with a1=1,a2=a3=a4=0,a6=1: E' : y^2+xy = x^3 + v x + (1+v), v = sum of kernel half x-coords,
\\ so Delta' = 1 + v + v^2 and the normalised b' = 1/j' = Delta'.
g=ffgen(Mod(1,2)*(x^41+x^3+1),'g); q=2^41; E41=ellinit([1,0,0,0,1],g); N=ellcard(E41);
toint(z)=subst(lift(z.pol),variable(z.pol),2);
trk(k)=my(P=lift(Mod(-x,x^2-x+2)^(41*k))); 2*polcoeff(P,0)+polcoeff(P,1);
xdbl(R)=my(X2=R[1]^2,Z2=R[2]^2); [X2^2+Z2^2, X2*Z2];
xadd(R,S,xD)=my(A=R[1]*S[2],B=S[1]*R[2],Z=(A+B)^2); [xD*Z+A*B, Z];
{ladder(x0,n)=my(R0=[x0,x0^0],R1=xdbl(R0)); forstep(i=#binary(n)-2,0,-1, if(bittest(n,i), R0=xadd(R0,R1,x0); R1=xdbl(R1), R1=xadd(R0,R1,x0); R0=xdbl(R0))); R0}
{vert(lp,k,twist)=my(K=ffgen(ffinit(2,41*k),'h), t=trk(k), G=if(twist, q^k+1+t, q^k+1-t), v=valuation(G,lp), cof=G/lp^v, xq=0, tries=0);
  print("l'=",lp,": F_2^",41*k,", ",if(twist,"twist","E")," group, v_l'(#)=",v);
  while(!xq, tries++; my(x0=random(K), R=ladder(x0,cof)); if(R[2]==0, next); my(xr=R[1]/R[2]);
    for(s=1,v, my(T=ladder(xr,lp)); if(T[2]==0, xq=xr; break); xr=T[1]/T[2]));
  my(n=(lp-1)/2, sm=xq, Rm=[xq,xq^0], R=xdbl(Rm)); sm+=R[1]/R[2];
  for(i=3,n, my(S=xadd(R,[xq,xq^0],Rm[1]/Rm[2])); Rm=R; R=S; sm+=R[1]/R[2]);
  if(ladder(xq,lp)[2]!=0, error("generator order"));
  my(D=1+sm+sm^2, cj=vector(41), c=D); for(i=1,41, cj[i]=c; c=c^2); if(c!=D, error("Delta' not in F_2^41"));
  my(mp=lift(prod(i=1,41,'X-cj[i])), mp2=Pol(apply(z->if(z==0,0,if(z==1,1,error("minpoly not over F_2"))), Vec(mp)),'X));
  write("minpoly_"lp".gp", mp2); print("  minpoly saved (degree ",poldegree(mp2),", tries ",tries,")"); finish(mp2)}

\\ roots of the F_2-minimal polynomial of Delta' in F_2^41; pick the smallest as the orbit representative
{finish(mp2)=my(F=factor(subst(mp2,'X,'X)*g^0)[,1], rts=apply(f->-polcoeff(f,0)/polcoeff(f,1), select(f->poldegree(f)==1, F~)));
  if(#rts!=poldegree(mp2), error("expected all roots in F_2^41"));
  my(bsel=vecmin(apply(toint,rts)), bs=0*g, nn=bsel, kk=0); while(nn, if(nn%2, bs+=g^kk); nn\=2; kk++);
  my(a2=-1); for(a=0,1, if(ellcard(ellinit([1,a,0,0,bs],g))==N, a2=a));
  if(a2<0, error("no twist of E' has #E = N"));
  print("  ",#rts," conjugate roots; chosen b'=",bsel," a2=",a2," #E'=N ok"); bsel}
