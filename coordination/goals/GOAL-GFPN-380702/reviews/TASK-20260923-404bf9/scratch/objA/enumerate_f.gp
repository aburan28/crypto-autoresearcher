\\ TASK-20260923-404bf9 (red team) -- proves-too-much OBJECT A, exact enumeration.
\\ Independent of the producer's code: PARI/GP only, no msolve, no python-flint,
\\ no file from experiments/EXP-GFPN-05ff43/implementation/.
\\
\\ For p' in {11, 31, 41} (each = 1 mod 5), c = smallest positive non-fifth-power
\\ mod p', F_q = F_p'[z]/(z^5 - c), and the two curves fixed by the review plan
\\   C1: y^2 = x^3 + 3x + 8 z^4            (EcMasFp5-shaped)
\\   C2: y^2 = x (x^2 + 2x + (263 mod p') z) (EcGFp5-shaped, double-odd model)
\\ compute EXACTLY
\\   FB   = { P in E(F_q) : x(P) in F_p' }                     (factor base, +-)
\\   S4   = { P1 + P2 + P3 + P4 : Pi in FB } \ {O}  (repetition allowed)
\\   S2   = { P1 + P2 : Pi in FB } \ {O}
\\   n    = largest prime factor of #E, G-subgroup = E[n] (targets R = [k]G live there)
\\   f_global = #S4 / #E,   f_sub = #(S4 cap E[n] \ {O}) / (n - 1)
\\ and write, for the configuration used by the pipeline run, the x-coordinates
\\ (coefficient vectors [c0..c4] in the basis 1, z, .., z^4) of every point of
\\ S4 cap E[n], with a flag for membership in S2 (positive-dimensional m = 4 system
\\ expected there) and one witness decomposition (x-values).

smallest_non5(p) = for(c = 1, p - 1, if(!ispower(Mod(c, p), 5), return(c)));
cf(u) = my(q = u.pol); vector(5, i, polcoef(q, i - 1));
ptkey(P) = if(#P == 1, "O", Str(cf(P[1]), cf(P[2])));

enumerate_cfg(p, which, dumpfile) =
{
  my(c = smallest_non5(p), irr = polisirreducible(Mod(1, p) * ('t^5 - c)));
  my(z = ffgen(Mod(1, p) * ('t^5 - c), 'z));
  my(a2, a4, a6, name);
  if(which == 1, a2 = 0; a4 = 3 * z^0; a6 = 8 * z^4; name = "C1_ecmas_shaped",
                 a2 = 2; a4 = (263 % p) * z; a6 = 0 * z; name = "C2_ecgfp5_shaped");
  my(E = ellinit([0, a2, 0, a4, a6]));
  my(disc = E.disc, N = ellcard(E), fa = factor(N), n = fa[#fa~, 1], cof = N / n);
  \\ factor base
  my(FB = List());
  for(x = 0, p - 1,
    my(X = x * z^0, rhs = X^3 + a2 * X^2 + a4 * X + a6);
    if(rhs == 0, listput(FB, [X, 0 * z]),
       if(issquare(rhs), my(Y = sqrt(rhs)); listput(FB, [X, Y]); listput(FB, [X, -Y]))));
  my(nF = #FB);
  \\ two-sums
  my(S2 = Map());
  for(i = 1, nF, for(j = i, nF,
     my(S = elladd(E, FB[i], FB[j]));
     if(#S > 1, mapput(S2, ptkey(S), 1))));
  \\ four-sums, with witness x-values
  my(S4 = Map(), W = Map(), cnt = 0);
  for(i = 1, nF, for(j = i, nF, my(Sij = elladd(E, FB[i], FB[j]));
    for(k = j, nF, my(Sijk = elladd(E, Sij, FB[k]));
      for(l = k, nF,
        my(S = elladd(E, Sijk, FB[l]));
        cnt++;
        if(#S > 1,
          my(key = ptkey(S));
          if(!mapisdefined(S4, key),
             mapput(S4, key, S);
             mapput(W, key, [cf(FB[i][1])[1], cf(FB[j][1])[1], cf(FB[k][1])[1], cf(FB[l][1])[1]])))))));
  my(keys = Vec(S4), nS4 = #keys, nsub = 0, nsub2 = 0, subpts = List());
  for(t = 1, nS4,
    my(S = mapget(S4, keys[t]));
    if(#ellmul(E, S, n) == 1,
       nsub++;
       my(in2 = mapisdefined(S2, keys[t]));
       if(in2, nsub2++);
       listput(subpts, [cf(S[1]), cf(S[2]), in2, mapget(W, keys[t])])));
  \\ distinct x-coordinates among subgroup decomposables (targets are recorded by x_R only)
  my(res = [p, c, irr, name, [0, a2, 0, a4, a6], disc != 0, N, fa, n, cof, nF, cnt, nS4, nsub, nsub2,
            nS4 / N, nsub / (n - 1)]);
  if(dumpfile != "",
     my(fh = fileopen(dumpfile, "w"));
     for(t = 1, #subpts, filewrite(fh, Str(subpts[t])));
     fileclose(fh));
  res;
}

{
  out = "objA_enumeration.txt";
  fh = fileopen(out, "w");
  foreach([11, 31, 41], p,
    if(!isprime(p) || p % 5 != 1, error("bad prime ", p));
    for(which = 1, 2,
      my(dump = Str("objA_S4sub_p", p, "_C", which, ".txt"));
      my(r = enumerate_cfg(p, which, dump));
      filewrite(fh, Str("p=", r[1], " c=", r[2], " z^5-c_irreducible=", r[3], " curve=", r[4],
         " coeffs[a1,a2,a3,a4,a6]=", r[5], " nonsingular=", r[6], " #E=", r[7], " factor=", r[8],
         " n=", r[9], " cofactor=", r[10], " #FB=", r[11], " four_multisets=", r[12],
         " #S4=", r[13], " #(S4 cap E[n])=", r[14], " #(S4 cap S2 cap E[n])=", r[15],
         " f_global=", r[16], " (", r[16] * 1., ")", " f_sub=", r[17], " (", r[17] * 1., ")"));
      print("done p=", p, " curve ", which, " f_sub=", r[17] * 1.)));
  fileclose(fh);
}
