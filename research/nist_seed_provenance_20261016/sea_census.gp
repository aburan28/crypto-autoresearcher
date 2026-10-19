\\ Point-count census for one chunk of candidates (PARI/GP >= 2.15 with seadata).
\\ Globals set by the caller: P (field prime), CAND (path of a file written by
\\ `cargo run --release --example nist_seed_candidates`, lines "i seed r b2 b0").
\\ Prints "i N0 Nt": N0 = #E(F_p) for y^2 = x^3 - 3x + b0, Nt = order of its
\\ quadratic twist; 0 means ellsea's early abort found a small factor.
default(parisizemax, 3*10^9);
{
my(L = readstr(CAND));
for (k = 1, #L,
  my(f = strsplit(L[k], " "), i = eval(f[1]), b2 = eval(f[4]), b0 = eval(f[5]));
  if (b0 == 0, b0 = lift(sqrt(Mod(b2, P))));
  my(E0 = ellinit([-3, b0], P), N0 = ellsea(E0, 1), Nt);
  if (N0, Nt = 2*P + 2 - N0, Nt = ellsea(elltwist(E0), 1));
  print(i, " ", N0, " ", Nt));
}
quit;
