\\ Koblitz curves y^2+xy=x^3+a x^2+1 over F_2^m (m prime), ECC2K-130-like: near-prime order (cofactor 2 or 4).
\\ For each conductor prime l of [O_K:Z[pi]]: pi = c (mod l); kernel x-coords of the l-isogenies live in F_2^(m*k),
\\ k = smallest with c^k = +-1. k = 1 means "rational on E or its twist", as for 263 at ECC2K-130.
{forprime(m=53,173, for(a=0,1, my(mu=if(a,1,-1), P=lift(Mod(x,x^2-mu*x+2)^m), X=polcoeff(P,0), Y=polcoeff(P,1), tr=2*X+mu*Y, N=2^m+1-tr, F=factor(N), l=F[#F~,1], cof=N/l);
  if(cof>4 || !isprime(l), next);
  my(f=abs(Y), fp=factor(f)[,1]~, s="");
  foreach(fp, p, my(c=Mod(X,p), o=znorder(c), k=if(o%2==0 && c^(o/2)==-1, o/2, o));
    s=Str(s, "  l=", p, "(", if(kronecker(-7,p)==1,"split",if(kronecker(-7,p)==-1,"inert","ram")), ", k=", k, ", field 2^", m*k, ")"));
  print("m=",m," a=",a," cof=",cof," log2(l)=",round(log(l)/log(2)), " |", s)))}
