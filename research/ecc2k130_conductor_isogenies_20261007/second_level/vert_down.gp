\\ Descending prime-degree isogeny from a NON-crater Koblitz-class curve E': y^2+xy=x^3+A2 x^2+B over F_2^m.
\\ As in vert_gen.gp, but B is a general element of F_2^m, so it must be embedded in K = F_2^(m*k):
\\   w = z^((2^(mk)-1)/(2^m-1)) generates the subfield F_2^m of K; its F_2-minimal polynomial mu_w gives
\\   S = F_2[t]/mu_w ~ F_2^m; a root R(t) of MOD in S defines x -> R(w), an embedding F_2[x]/MOD -> K.
\\ Velu (a1=1, a3=a4=0, a6=B, any a2): E'' : y^2+xy = x^3+A2 x^2+v x+(B+v), Delta'' = B+v+v^2 = 1/j''.
\\ The chosen embedding is one of m; a different one yields a Galois conjugate, which lies on the same level.
\\ set before reading: MOD, m, A2, BINT, lp, k, twist, NISO, OUT
g = ffgen(Mod(1,2)*MOD, 'g); q = 2^m;
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
Eb = ellinit([1,A2,0,0,fromint(BINT)], g); N = ellcard(Eb);
mu = if(A2, 1, -1);
trk(kk) = my(P = lift(Mod(x, x^2 - mu*x + 2)^(m*kk))); 2*polcoeff(P,0) + mu*polcoeff(P,1);
K = ffgen(ffinit(2, m*k), 'h);
\\ --- embedding F_2[x]/MOD -> K
{emb_x() = my(e = (2^(m*k)-1)/(2^m-1), w, cj, c, mp);
  while(1, w = random(K)^e; cj = vector(m); c = w; for(i = 1, m, cj[i] = c; c = c^2); if(c != w, error("not in subfield"));
    if(#Set(cj) == m, break));
  mp = Pol(apply(z -> if(z == 0, 0, if(z == 1, 1, error("minpoly"))), Vec(lift(prod(i = 1, m, 'X - cj[i])))), 'X);
  my(S = ffgen(Mod(1,2)*subst(mp, 'X, 't), 't), F = factor(subst(MOD, x, 'Y)*S^0)[,1], r = 0);
  for(i = 1, #F, if(poldegree(F[i]) == 1, r = -polcoeff(F[i],0)/polcoeff(F[i],1); break));
  if(r == 0, error("no root of MOD in S"));
  my(Rp = lift(r.pol));  \\ polynomial in t with F_2 coefficients
  subst(Rp*K^0, variable(Rp), w)}
t0 = getabstime(); Xk = emb_x(); \\ image of the generator x of F_2[x]/MOD
if(subst(MOD, x, Xk) != 0, error("embedding does not satisfy MOD"));
embed(n) = my(s = 0*K, p = K^0); while(n, if(n % 2, s += p); n \= 2; p *= Xk); s;
BK = embed(BINT); print("embedded B into F_2^", m*k, " (", (getabstime()-t0)\1000, " s); check B^(2^m) = B: ", BK^(2^m) == BK);
xdbl(R) = my(X2 = R[1]^2, Z2 = R[2]^2); [X2^2 + BK*Z2^2, X2*Z2];
xadd(R, S, xD) = my(Aa = R[1]*S[2], Bb = S[1]*R[2], Z = (Aa+Bb)^2); [xD*Z + Aa*Bb, Z];
{ladder(x0, n) = my(R0 = [x0, x0^0], R1 = xdbl(R0));
  forstep(i = #binary(n)-2, 0, -1, if(bittest(n, i), R0 = xadd(R0, R1, x0); R1 = xdbl(R1), R1 = xadd(R0, R1, x0); R0 = xdbl(R0))); R0}
tt = trk(k); G = if(twist, q^k + 1 + tt, q^k + 1 - tt); v_l = valuation(G, lp); cof = G / lp^v_l;
print("from b=", BINT, " (a2=", A2, "): l'=", lp, " kernel field F_2^", m*k, " (", if(twist,"twist","E"), "), v_l'=", v_l);
{one() = my(xq = 0, tries = 0);
  while(!xq, tries++; my(x0 = random(K), R = ladder(x0, cof)); if(R[2] == 0, next); my(xr = R[1]/R[2]);
    for(s = 1, v_l, my(T = ladder(xr, lp)); if(T[2] == 0, xq = xr; break); xr = T[1]/T[2]));
  if(ladder(xq, lp)[2] != 0, error("generator order"));
  my(n = (lp-1)/2, sm = xq, Rm = [xq, xq^0], R = xdbl(Rm)); sm += R[1]/R[2];
  for(i = 3, n, my(S = xadd(R, [xq, xq^0], Rm[1]/Rm[2])); Rm = R; R = S; sm += R[1]/R[2]);
  my(Dl = BK + sm + sm^2, cj = vector(m), c = Dl); for(i = 1, m, cj[i] = c; c = c^2); if(c != Dl, error("Delta'' not in subfield"));
  my(mp = Pol(apply(z -> if(z == 0, 0, if(z == 1, 1, error("minpoly"))), Vec(lift(prod(i = 1, m, 'X - cj[i])))), 'X));
  my(F = factor(mp*g^0)[,1], rts = apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f) == 1, F~)));
  if(#rts != poldegree(mp), error("roots"));
  my(bsel = vecmin(apply(toint, rts)), a2 = -1); for(aa = 0, 1, if(ellcard(ellinit([1,aa,0,0,fromint(bsel)], g)) == N, a2 = aa));
  if(a2 < 0, error("no model with #E = N"));
  [bsel, a2, poldegree(mp), tries]}
{for(i = 1, NISO, my(t1 = getabstime(), r = one());
   print("  isogeny ", i, ": b'' (Galois-orbit min) = ", r[1], "  a2=", r[2], "  orbit size ", r[3], "  #E''=N ok  (", (getabstime()-t1)\1000, " s)");
   write(OUT, r));}
