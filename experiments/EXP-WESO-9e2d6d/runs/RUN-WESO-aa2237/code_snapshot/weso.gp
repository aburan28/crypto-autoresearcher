\\ EXP-WESO-9e2d6d -- PARI/GP core library (quaternion arithmetic, sampler,
\\ delta extraction, units, Gross-lattice labels, verified factorisation).
\\ Algebra B_{p,inf} = (-1,-p | Q): i^2=-1, j^2=-p, k=ij (p = 3 mod 4).
\\ Elements: column vectors [a,b,c,d]~ = a + b i + c j + d k (rationals).
\\ Lattices: 4 x 4 matrices whose COLUMNS are a Z-basis in (1,i,j,k) coords.

qmul(x,y,p)={[x[1]*y[1]-x[2]*y[2]-p*x[3]*y[3]-p*x[4]*y[4],
             x[1]*y[2]+x[2]*y[1]+p*x[3]*y[4]-p*x[4]*y[3],
             x[1]*y[3]+x[3]*y[1]-x[2]*y[4]+x[4]*y[2],
             x[1]*y[4]+x[4]*y[1]+x[2]*y[3]-x[3]*y[2]]~};
qconj(x)=[x[1],-x[2],-x[3],-x[4]]~;
qnrd(x,p)=x[1]^2+x[2]^2+p*x[3]^2+p*x[4]^2;
qtrd(x)=2*x[1];

\\ Z-basis (HNF, canonical) of the lattice spanned by the columns of M.
lathnf(M)={my(d=denominator(M),H=mathnf(d*M)); if(#H!=4, error("lathnf: rank ",#H)); H/d};
\\ Canonical string of a lattice (scaled HNF), used for hashing.
latcanon(B)={my(d=denominator(B)); Str(d,":",mathnf(d*B))};

\\ Trd(x conj y) Gram matrix (x^T G x = 2 Nrd(x)).
trdgram(B,p)={my(n=#B); matrix(n,n,a,b,qtrd(qmul(B[,a],qconj(B[,b]),p)))};

\\ Standard maximal order O_0 = Z<1, i, (i+j)/2, (1+k)/2>.
O0basis()=[1,0,0,1/2; 0,1,1/2,0; 0,0,1/2,0; 0,0,0,1/2];

\\ Product lattice L1*L2.
latmul(B1,B2,p)={my(v=vector(16,t,qmul(B1[,(t-1)\4+1],B2[,(t-1)%4+1],p))); lathnf(Mat(v))};

\\ U-2 style order check: contains 1, closed under multiplication, |det Trd-Gram| = p^2.
isorder(B,p)={my(Bi=B^-1,ok=1,c);
  c=Bi*[1,0,0,0]~; if(denominator(c)!=1,return(0));
  for(a=1,4,for(b=1,4, c=Bi*qmul(B[,a],B[,b],p); if(denominator(c)!=1,return(0))));
  ok};
discrd2(B,p)=abs(matdet(trdgram(B,p)));

\\ ---- ell-adic matrix units in O/ell^K (O given by basis B) ----------------
\\ returns [e11,e12,e21] as integer coordinate vectors (in basis B) mod ell^K
mulc(B,Bi,x,y,p)=Bi*qmul(B*x,B*y,p);
matunits(B,p,ell,K)={my(Bi=B^-1,N=ell^K,x,f,r,t,n,eps,one,e12,f21,lam,j0,cand,found=0);
  one=Bi*[1,0,0,0]~;
  forvec(c=vector(4,t,[-2,2]), if(found,break);
    x=B*c~; t=qtrd(x); n=qnrd(x,p);
    f='X^2-t*'X+n;
    if(#polrootsmod(f,ell)==2 && poldegree(f)==2,
      r=polrootspadic(f,ell,K+2); if(#r==2, found=1; cand=[c~,r])));
  if(!found, error("matunits: no split element"));
  r=[truncate(cand[2][1]), truncate(cand[2][2])];
  eps=((cand[1]-r[2]*one)*lift(Mod(r[1]-r[2],N)^-1))%N;
  \\ check idempotent
  if(((mulc(B,Bi,eps,eps,p)-eps)%N)!=0, error("matunits: eps not idempotent"));
  my(ome=(one-eps)%N, basisv);
  e12=0; for(a=1,4, my(y=vectorv(4,t,t==a)); my(z=mulc(B,Bi,mulc(B,Bi,eps,y,p),ome,p)%N);
     if(z%ell!=0, e12=z; break));
  if(e12==0, error("matunits: no e12"));
  j0=0; for(a=1,4, if(eps[a]%ell!=0, j0=a; break));
  my(e21=0);
  for(a=1,4, my(y=vectorv(4,t,t==a)); my(z=mulc(B,Bi,mulc(B,Bi,ome,y,p),eps,p)%N);
     my(pr=mulc(B,Bi,e12,z,p)%N);
     lam=(pr[j0]*lift(Mod(eps[j0],N)^-1))%N;
     if(lam%ell!=0 && ((pr-lam*eps)%N)==0, e21=(z*lift(Mod(lam,N)^-1))%N; break));
  if(e21==0, error("matunits: no e21"));
  \\ checks: e12*e21 = e11, e21*e12 = 1-e11, e11*e12=e12, e12*e11=0
  if((mulc(B,Bi,e12,e21,p)-eps)%N!=0, error("mu chk1"));
  if((mulc(B,Bi,e21,e12,p)-ome)%N!=0, error("mu chk2"));
  if((mulc(B,Bi,eps,e12,p)-e12)%N!=0, error("mu chk3"));
  if(mulc(B,Bi,e12,eps,p)%N!=0, error("mu chk4"));
  [eps,e12,e21]};

\\ P^1(Z/ell^m) point number idx in [0, ell^m + ell^(m-1)):
\\   idx < ell^m -> v = (1, idx); else v = (ell*(idx - ell^m), 1)
p1point(ell,m,idx)=if(idx<ell^m,[1,idx],[ell*(idx-ell^m),1]);

\\ Cyclic left ideal of O (basis B) of norm ell^m with kernel point v:
\\ I = O*alpha + ell^m O, alpha = v2*e11 - v1*e12 (matrix [[v2,-v1],[0,0]]).
\\ MU = matunits(B,p,ell,K) with K >= m.
cycideal(B,p,MU,ell,m,idx)={my(N=ell^m,v=p1point(ell,m,idx),al,A,gens);
  al=((v[2]*MU[1]-v[1]*MU[2])%N); A=B*al;
  gens=concat(vector(4,t,qmul(B[,t],A,p)), vector(4,t,N*B[,t]));
  lathnf(Mat(gens))};
\\ Right order O_R(I) = conj(I) I / Nrd(I)
rightorder(Id,p,nrdI)={my(Ic=matrix(4,4,a,b,if(a==1,Id[a,b],-Id[a,b])));
  latmul(Ic,Id,p)/nrdI};

\\ LLL-reduce an order basis with respect to Nrd.
lllorder(B,p)={my(G=trdgram(B,p),U=qflllgram(G)); B*U};

\\ delta(O): P = {x in O : p | Nrd x}; min of Nrd/p over P (exact via qfminim).
\\ Returns [delta, Gp (Trd-Gram of P divided by p, LLL basis), PB].
deltaorder(B,p)={my(G=trdgram(B,p),K,PB,Gp,U,mm,v);
  K=lift(matker(G*Mod(1,p)));
  if(#K!=2, error("deltaorder: kernel dim ",#K));
  PB=B*mathnf(concat(p*matid(4),K));
  Gp=trdgram(PB,p)/p;
  if(denominator(Gp)!=1, error("deltaorder: nonintegral"));
  U=qflllgram(Gp); PB=PB*U; Gp=U~*Gp*U;
  mm=qfminim(Gp,,2,0);
  \\ exact check of one minimal vector
  v=mm[3][,1]; if(v~*Gp*v!=mm[2], error("deltaorder: min check"));
  if(qnrd(PB*v,p)!=p*mm[2]/2, error("deltaorder: nrd check"));
  [mm[2]/2, Gp, PB]};
\\ C-2 independent recomputation: qfminim on the UNREDUCED P Gram with bound 2*d.
deltarecheck(B,p,d)={my(G=trdgram(B,p),K,PB,Gp,mm);
  K=lift(matker(G*Mod(1,p))); PB=B*mathnf(concat(p*matid(4),K));
  Gp=trdgram(PB,p)/p; mm=qfminim(Gp,2*d,,0); if(mm[1]==0, 0, mm[2]/2)};

\\ number of units |O^x| = #{x : Nrd x = 1}
nunits(B,p)={my(G=trdgram(B,p),mm=qfminim(qflllgram(G)~*G*qflllgram(G),2,,0)); mm[1]};

\\ Gross lattice {x in Z + 2O : Trd x = 0}; LLL-reduced Trd-Gram (3x3).
grossgram(B,p)={my(L=lathnf(concat([1,0,0,0]~,2*B)),t=vector(4,a,qtrd(L[,a])),K,GB,G);
  K=matkerint(Mat(t)); GB=L*K; G=trdgram(GB,p); qflllgram(G)~*G*qflllgram(G)};
\\ theta prefix: counts of Nrd = 1..T (half counts), from Trd-Gram
thetakey(G,T)=qfrep(G,T,1);

\\ verified factorisation: returns [fac, ok] ; fac as [[q,e],...]; ok=1 iff
\\ product equals n and every q passes isprime (proof).
vfactor(n)={my(F=factor(n),pr=1,ok=1,v=vector(#F~,t,[F[t,1],F[t,2]]));
  for(t=1,#v, pr*=v[t][1]^v[t][2]; if(!isprime(v[t][1]),ok=0));
  if(pr!=n,ok=0); [v,ok]};

\\ ------------------------------------------------------------------------
\\ Sampler context: set by setctx(p, B (start order), Kmax)
setctx(p,B,Kmax)={CTXp=p; CTXB=B; CTXMU=matunits(B,p,2,Kmax); CTXK=Kmax;};

\\ One draw at walk length k from the context start order, P^1 index idx.
\\ Output string: delta|fac|ok|ideal_canon|order_canon|c2
wsample(k,idx)={my(p=CTXp,B=CTXB,Id,Ord,dd,fv,c2=1,bnd);
  if(k==0, Ord=B; Id=B,
    Id=cycideal(B,p,CTXMU,2,k,idx); Ord=rightorder(Id,p,2^k));
  Ord=lathnf(Ord);
  dd=deltaorder(lllorder(Ord,p),p)[1];
  bnd=sqrtnint(p\2,3);
  if(dd>bnd, c2=0; my(d2=deltarecheck(Ord,p,dd)); if(d2!=dd, c2=-1));
  fv=vfactor(dd);
  Str(dd,"|",fv[1],"|",fv[2],"|",latcanon(Id),"|",latcanon(Ord),"|",c2)};
