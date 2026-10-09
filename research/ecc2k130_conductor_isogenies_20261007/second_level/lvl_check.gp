\\ Level check by torsion structure. For a prime l' | f_pi with pi = c (mod l') of kernel-field degree k, let G be the order
\\ of E(F_{q^k}) (twist = 0) or of its quadratic twist (twist = 1); isogenous curves share G. If l' divides
\\ [End(E):Z[pi]], pi is a scalar on E[l'] and the l'-part of the group has rank 2, so its exponent is < l'^v (v = v_l'(G) >= 2).
\\ If l' does not divide it, pi is not a scalar and the l'-part is cyclic, exponent l'^v. The exponent is sampled from
\\ random x in F_{q^k}: Q = cof*P, then the least e with l'^e Q = O (points on the other twist give no l'-power and are skipped).
\\ x-only Lopez-Dahab arithmetic depends only on b, so b is embedded into F_{q^k} as in vert_down.gp.
\\ set before reading: MOD, m, CURVES = [[name, A2, BINT], ...], PRIMES = [[lp, k, twist], ...], NGOOD
g = ffgen(Mod(1,2)*MOD, 'g); q = 2^m;
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
A0 = CURVES[1][2]; mu = if(A0, 1, -1);
N = ellcard(ellinit([1,A0,0,0,fromint(CURVES[1][3])], g));
{for(i = 1, #CURVES, if(ellcard(ellinit([1,CURVES[i][2],0,0,fromint(CURVES[i][3])], g)) != N, error("curve ", CURVES[i][1], " not in the class")));}
print("m=", m, ": all ", #CURVES, " curves have #E = ", N);
trk(kk) = my(P = lift(Mod(x, x^2 - mu*x + 2)^(m*kk))); 2*polcoeff(P,0) + mu*polcoeff(P,1);
{emb_x(K, k) = my(e = (2^(m*k)-1)/(2^m-1), w, cj, c, mp);
  while(1, w = random(K)^e; cj = vector(m); c = w; for(i = 1, m, cj[i] = c; c = c^2); if(c != w, error("not in subfield"));
    if(#Set(cj) == m, break));
  mp = Pol(apply(z -> if(z == 0, 0, if(z == 1, 1, error("minpoly"))), Vec(lift(prod(i = 1, m, 'X - cj[i])))), 'X);
  my(S = ffgen(Mod(1,2)*subst(mp, 'X, 't), 't), F = factor(subst(MOD, x, 'Y)*S^0)[,1], r = 0);
  for(i = 1, #F, if(poldegree(F[i]) == 1, r = -polcoeff(F[i],0)/polcoeff(F[i],1); break));
  if(r == 0, error("no root of MOD in S"));
  my(Rp = lift(r.pol), X = subst(Rp*K^0, variable(Rp), w)); if(subst(MOD, x, X) != 0, error("embedding")); X}
embed(n, Xk, K) = my(s = 0*K, p = K^0); while(n, if(n % 2, s += p); n \= 2; p *= Xk); s;
xdbl(R, BK) = my(X2 = R[1]^2, Z2 = R[2]^2); [X2^2 + BK*Z2^2, X2*Z2];
xadd(R, S, xD) = my(Aa = R[1]*S[2], Bb = S[1]*R[2], Z = (Aa+Bb)^2); [xD*Z + Aa*Bb, Z];
{ladder(x0, n, BK) = my(R0 = [x0, x0^0], R1 = xdbl(R0, BK));
  forstep(i = #binary(n)-2, 0, -1, if(bittest(n, i), R0 = xadd(R0, R1, x0); R1 = xdbl(R1, BK), R1 = xadd(R0, R1, x0); R0 = xdbl(R0, BK))); R0}
{foreach(PRIMES, PR, my(lp = PR[1], k = PR[2], tw = PR[3], t0 = getabstime(), K = ffgen(ffinit(2, m*k), 'h), Xk = emb_x(K, k));
  my(tt = trk(k), G = if(tw, q^k + 1 + tt, q^k + 1 - tt), v = valuation(G, lp), cof = G / lp^v);
  print("l'=", lp, ": field F_2^", m*k, " (", if(tw, "twist", "E"), "), v_l'(G) = ", v, "; embedding ", (getabstime()-t0)\1000, " s");
  foreach(CURVES, C, my(BK = embed(C[3], Xk, K), es = List(), skipped = 0, t1 = getabstime());
    while(#es < NGOOD, my(x0 = random(K), R = ladder(x0, cof, BK)); if(R[2] == 0, next); my(xr = R[1]/R[2], e = 0);
      for(s = 1, v, my(T = ladder(xr, lp, BK)); if(T[2] == 0, e = s; break); xr = T[1]/T[2]);
      if(e, listput(es, e), skipped++));
    my(ex = vecmax(Vec(es)));
    print("   ", C[1], ": sampled l'-power orders l'^", Vec(es), " (", skipped, " x on the other twist skipped; ", (getabstime()-t1)\1000, " s)",
          " -> exponent l'^", ex, if(ex == v, ": cyclic, pi NOT scalar on E[l'], l' divides the conductor of End",
                                         ": rank 2, pi scalar on E[l'], l' does not divide the conductor of End"))))}
