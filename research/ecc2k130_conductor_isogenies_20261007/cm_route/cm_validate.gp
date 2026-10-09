\\ Floor curves as roots of the class polynomial mod 2 (PARI invariant 1 = Weber f; mod 2, (f^24-16)^3 = j f^24 gives j = f^48), compared with the
\\ floors previously enumerated by explicit vertical isogenies + horizontal walks.
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
{floor_by_cm(MOD, f) = my(g = ffgen(Mod(1,2)*MOD, 'g), D = -7*f^2, t = getabstime(), H = polclass(D, 1), tc = getabstime() - t);
  my(F = factor(H*g^0)[,1], rts = apply(r -> -polcoeff(r,0)/polcoeff(r,1), select(r -> poldegree(r) == 1, F~)));
  [poldegree(H), #rts, Set(apply(z -> toint(1/z^48), rts)), tc, round(log(normlp(Vec(H), oo))/log(2)), Set(apply(z -> toint(1/z^3), rts))]}
read("L37.gp");
read("L41.gp");
{foreach([[x^37+x^9+x^2+x+1, 73, L37], [x^41+x^3+1, 409, L41]], C,
  my(r = floor_by_cm(C[1], C[2]));
  print("f=", C[2], ": deg H_D = ", r[1], " (h), roots in F_2^m: ", r[2], ", polclass ", r[4], " ms, max coeff ~2^", r[5],
        ";  b = f^-48 matches isogeny-enumerated floor: ", r[3] == C[3], " (", #setintersect(r[3], C[3]), "/", #C[3], ")",
        ";  f^-3 = (f^-48)^(1/16) gives the same set (Galois-stable): ", r[6] == r[3]))}
