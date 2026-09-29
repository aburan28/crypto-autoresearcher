\\ TASK-20260923-404bf9 -- OBJECT A truth set (independent of the producer's code).
\\ Global dump of S4 = {P1+P2+P3+P4 : x(Pi) in F_p} \ {O} for ONE configuration,
\\ one line per point: [xcoeffs, ycoeffs, inS2, witness_x_values].
\\ Called by run_objA_pipeline.py with p, c, a2, a4coeffs, a6coeffs, outfile set.
cf(u) = my(q = u.pol); vector(5, i, polcoef(q, i - 1));
ptkey(P) = if(#P == 1, "O", Str(cf(P[1]), cf(P[2])));
fromcf(v, z) = sum(i = 1, #v, v[i] * z^(i - 1));
{
  my(z = ffgen(Mod(1, P_) * ('t^5 - C_), 'z));
  my(a2 = fromcf(A2_, z) + 0 * z, a4 = fromcf(A4_, z) + 0 * z, a6 = fromcf(A6_, z) + 0 * z);
  my(E = ellinit([0, a2, 0, a4, a6]));
  my(FB = List());
  for(x = 0, P_ - 1,
    my(X = x * z^0, rhs = X^3 + a2 * X^2 + a4 * X + a6);
    if(rhs == 0, listput(FB, [X, 0 * z]),
       if(issquare(rhs), my(Y = sqrt(rhs)); listput(FB, [X, Y]); listput(FB, [X, -Y]))));
  my(nF = #FB, S2 = Map(), S4 = Map(), W = Map());
  for(i = 1, nF, for(j = i, nF, my(S = elladd(E, FB[i], FB[j])); if(#S > 1, mapput(S2, ptkey(S), 1))));
  for(i = 1, nF, for(j = i, nF, my(Sij = elladd(E, FB[i], FB[j]));
    for(k = j, nF, my(Sijk = elladd(E, Sij, FB[k]));
      for(l = k, nF, my(S = elladd(E, Sijk, FB[l]));
        if(#S > 1, my(key = ptkey(S));
          if(!mapisdefined(S4, key), mapput(S4, key, S);
             mapput(W, key, [cf(FB[i][1])[1], cf(FB[j][1])[1], cf(FB[k][1])[1], cf(FB[l][1])[1]])))))));
  my(keys = Vec(S4), fh = fileopen(OUT_, "w"));
  for(t = 1, #keys, my(S = mapget(S4, keys[t]));
    filewrite(fh, Str([cf(S[1]), cf(S[2]), mapisdefined(S2, keys[t]), mapget(W, keys[t])])));
  fileclose(fh);
  print("#E=", ellcard(E), " #FB=", nF, " #S4=", #keys, " #S2=", #Vec(S2));
  \\ order of the pipeline's base point G, if supplied
  if(GX_ != 0,
     my(G = [fromcf(GX_, z) + 0 * z, fromcf(GY_, z) + 0 * z]);
     if(!ellisoncurve(E, G), error("G not on curve"));
     print("ordG=", ellorder(E, G));
     \\ membership of each S4 point in <G> and its discrete log (known scalar)
     my(fh2 = fileopen(Str(OUT_, ".logs"), "w"));
     \\ elllog is only trusted after re-multiplication: E(F_q) need not be cyclic
     for(t = 1, #keys, my(S = mapget(S4, keys[t]), k = elllog(E, S, G));
        if(type(k) != "t_INT" || ellmul(E, G, k) != S, k = -1);
        filewrite(fh2, Str([cf(S[1]), cf(S[2]), k])));
     print("group=", ellgroup(E));
     fileclose(fh2));
}
