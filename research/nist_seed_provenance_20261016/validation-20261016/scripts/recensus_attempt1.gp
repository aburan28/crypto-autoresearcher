\\ Independent early-abort re-census driver (VAL-20261016-cd9156), written from the
\\ statement only: count the curve y^2 = x^3 - 3x + b0 and its quadratic twist
\\ y^2 = x^3 - 3 d^2 x + d^3 b0 (d = smallest non-residue) with ellsea(.,1) early abort.
\\ Input: a GP file holding a vector of [t, p, d, i, bsq]; output lines "t i N0 Nt".
\\ mode 0: early abort (ellsea(E,1)); mode 1: full count (ellcard) of the curve only,
\\ plus N*P = O on 3 random points and the Hasse test, written "t i N isprime cert hasse".
census(infile, outfile, mode) =
{
  my(V = read(infile));
  for (k = 1, #V,
    my(t = V[k][1], p = V[k][2], d = V[k][3], i = V[k][4], bsq = Mod(V[k][5], p), b0, E, Et, N0, Nt);
    if (p % 4 == 3, b0 = bsq^((p + 1) / 4), b0 = sqrt(bsq));
    if (b0^2 != bsq, error("no square root at ", t, " ", i));
    E = ellinit([-3, lift(b0)], p);
    if (mode == 0,
      Et = ellinit([lift(Mod(-3 * d^2, p)), lift(b0 * d^3)], p);
      N0 = ellsea(E, 1);
      Nt = ellsea(Et, 1);
      write(outfile, Str(t, " ", i, " ", N0, " ", Nt))
    ,
      my(N = ellcard(E), ip = isprime(N), cert = -1, hasse);
      hasse = ((N - (p + 1))^2 <= 4 * p);
      cert = 1;
      for (j = 1, 3, my(P = random(E)); if (ellmul(E, P, N) != [0], cert = 0));
      write(outfile, Str(t, " ", i, " ", N, " ", ip, " ", cert, " ", hasse))
    );
  );
}
