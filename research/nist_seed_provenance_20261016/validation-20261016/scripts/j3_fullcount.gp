\\ J3 full counts (VAL-20261016-cd9156): no early abort.
\\ Input: GP file with a vector of [t, p, d, i, bsq] (from recensus_prep.py rows).
\\ For each row: b0 = bsq^((p+1)/4) (p = 3 mod 4) or a square root (p = 1 mod 4);
\\ N = ellcard(y^2 = x^3 - 3x + b0); Nt = 2(p+1) - N.
\\ Certificates independent of SEA: Hasse test; for prime N, N*P = O for 3 random P on E;
\\ for prime Nt, Nt*Q = O for 3 random Q on the twist y^2 = x^3 - 3 d^2 x + d^3 b0.
\\ Output line: "t i N Nt isprime(N) isprime(Nt) hasse certN certNt" (cert -1 = not applicable).
\\ demo != 0 additionally counts y^2 = x^3 - 3x - b0 fully and appends its order (J4).
fullcount(infile, outfile, demo) =
{
  my(V = read(infile));
  for (k = 1, #V,
    my(t = V[k][1], p = V[k][2], d = V[k][3], i = V[k][4], bsq = Mod(V[k][5], p), b0, E, Et, N, Nt, pN, pNt, hasse, cN = -1, cT = -1, extra = "");
    if (p % 4 == 3, b0 = bsq^((p + 1) / 4), b0 = sqrt(bsq));
    if (b0^2 != bsq, error("no square root at ", t, " ", i));
    E = ellinit([-3, lift(b0)], p);
    N = ellcard(E);
    Nt = 2 * (p + 1) - N;
    pN = isprime(N); pNt = isprime(Nt);
    hasse = ((N - (p + 1))^2 <= 4 * p);
    if (pN, cN = 1; for (j = 1, 3, my(P = random(E)); if (ellmul(E, P, N) != [0], cN = 0)));
    if (pNt,
      Et = ellinit([lift(Mod(-3 * d^2, p)), lift(b0 * d^3)], p);
      cT = 1; for (j = 1, 3, my(Q = random(Et)); if (ellmul(Et, Q, Nt) != [0], cT = 0)));
    if (demo, extra = Str(" ", ellcard(ellinit([-3, lift(-b0)], p))));
    write(outfile, Str(t, " ", i, " ", N, " ", Nt, " ", pN, " ", pNt, " ", hasse, " ", cN, " ", cT, extra));
  );
}
