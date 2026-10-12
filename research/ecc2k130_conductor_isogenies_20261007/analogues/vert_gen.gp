\\ Descending vertical isogenies of prime degree lp from a Koblitz crater E: y^2+xy=x^3+a x^2+1 over F_2^m.
\\ pi = c (mod lp) is a scalar on E[lp]; kernel x-coordinates lie in F_2^(m*k), on E (c^k = 1) or on its quadratic
\\ twist (c^k = -1). x-only Lopez-Dahab arithmetic is independent of a and of the twist, and b = 1 lies in F_2, so no
\\ subfield embedding is needed. Char-2 Velu for a1=1, a3=a4=0, a6=1 (any a2): E' : y^2+xy = x^3+a x^2+v x+(1+v),
\\ v = sum of half-kernel x-coordinates, Delta' = 1+v+v^2 = 1/j'. Delta' is pulled down to F_2^m through its
\\ F_2-minimal polynomial (one conjugate = one curve of the same Galois orbit, hence the same level).
\\ usage (set before reading): MOD = modulus polynomial in x over F_2, m, a, lp, k, twist, NISO, OUT
g = ffgen(Mod(1,2)*MOD, 'g); q = 2^m;
E0 = ellinit([1,a,0,0,1], g); N = ellcard(E0);
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
mu = if(a, 1, -1);
trk(kk) = my(P = lift(Mod(x, x^2 - mu*x + 2)^(m*kk))); 2*polcoeff(P,0) + mu*polcoeff(P,1);
xdbl(R) = my(X2 = R[1]^2, Z2 = R[2]^2); [X2^2 + Z2^2, X2*Z2];
xadd(R, S, xD) = my(A = R[1]*S[2], B = S[1]*R[2], Z = (A+B)^2); [xD*Z + A*B, Z];
{ladder(x0, n) = my(R0 = [x0, x0^0], R1 = xdbl(R0));
  forstep(i = #binary(n)-2, 0, -1, if(bittest(n, i), R0 = xadd(R0, R1, x0); R1 = xdbl(R1), R1 = xadd(R0, R1, x0); R0 = xdbl(R0))); R0}
K = ffgen(ffinit(2, m*k), 'h); t = trk(k); G = if(twist, q^k + 1 + t, q^k + 1 - t); v_l = valuation(G, lp); cof = G / lp^v_l;
print("m=", m, " a=", a, "  l'=", lp, "  kernel field F_2^", m*k, " (", if(twist, "twist", "E"), "), v_l'(#)=", v_l);
{one_isogeny() = my(xq = 0, tries = 0);
  while(!xq, tries++; my(x0 = random(K), R = ladder(x0, cof)); if(R[2] == 0, next); my(xr = R[1]/R[2]);
    for(s = 1, v_l, my(T = ladder(xr, lp)); if(T[2] == 0, xq = xr; break); xr = T[1]/T[2]));
  my(n = (lp-1)/2, sm = xq, Rm = [xq, xq^0], R = xdbl(Rm)); sm += R[1]/R[2];
  for(i = 3, n, my(S = xadd(R, [xq, xq^0], Rm[1]/Rm[2])); Rm = R; R = S; sm += R[1]/R[2]);
  if(ladder(xq, lp)[2] != 0, error("kernel generator does not have order l'"));
  my(D = 1 + sm + sm^2, cj = vector(m), c = D); for(i = 1, m, cj[i] = c; c = c^2); if(c != D, error("Delta' not in F_2^m"));
  my(mp = lift(prod(i = 1, m, 'X - cj[i])), mp2 = Pol(apply(z -> if(z == 0, 0, if(z == 1, 1, error("minpoly not over F_2"))), Vec(mp)), 'X));
  my(F = factor(mp2*g^0)[,1], rts = apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f) == 1, F~)));
  if(#rts != poldegree(mp2), error("roots not all in F_2^m"));
  my(bsel = vecmin(apply(toint, rts)), a2 = -1); for(aa = 0, 1, if(ellcard(ellinit([1,aa,0,0,fromint(bsel)], g)) == N, a2 = aa));
  if(a2 < 0, error("no model of E' with #E = N"));
  [bsel, a2, poldegree(mp2), tries]}
{res = List(); for(i = 1, NISO, my(t0 = getabstime(), r = one_isogeny()); listput(res, r);
   print("  isogeny ", i, ": b' (Galois-orbit min) = ", r[1], "  a2=", r[2], "  orbit size ", r[3], "  #E'=N ok  (", (getabstime()-t0)\1000, " s)");
   write(OUT, r));}
print("distinct Galois orbits reached: ", #Set(apply(r -> r[1], Vec(res))), " of ", NISO);
