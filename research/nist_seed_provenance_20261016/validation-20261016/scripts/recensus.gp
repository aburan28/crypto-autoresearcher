\\ Independent early-abort re-census driver (VAL-20261016-cd9156), written from the
\\ statement only: count the curve y^2 = x^3 - 3x + b0 and its quadratic twist
\\ y^2 = x^3 - 3 d^2 x + d^3 b0 (d = smallest non-residue) with ellsea(.,1) early abort.
\\ Input: a GP file holding a vector of [t, p, d, i, bsq]; output lines "t i N0 Nt".
\\ Attempt 2 (after a stack overflow in attempt 1, see scripts/recensus_attempt1.gp):
\\ identical mathematics; each row is wrapped in iferr so that an infrastructure error is
\\ written as "t i ERR <message>" (a not_run row) instead of stopping the shard.
\\ Run with: gp -q --default parisize=200000000 --default parisizemax=3000000000
census(infile, outfile, mode) =
{
  my(V = read(infile));
  for (k = 1, #V,
    my(t = V[k][1], p = V[k][2], d = V[k][3], i = V[k][4], bsq = Mod(V[k][5], p));
    iferr(
      my(b0, E, Et, N0, Nt);
      if (p % 4 == 3, b0 = bsq^((p + 1) / 4), b0 = sqrt(bsq));
      if (b0^2 != bsq, error("no square root"));
      E = ellinit([-3, lift(b0)], p);
      Et = ellinit([lift(Mod(-3 * d^2, p)), lift(b0 * d^3)], p);
      N0 = ellsea(E, 1);
      Nt = ellsea(Et, 1);
      write(outfile, Str(t, " ", i, " ", N0, " ", Nt))
    , err,
      write(outfile, Str(t, " ", i, " ERR ", errname(err)))
    );
  );
}
