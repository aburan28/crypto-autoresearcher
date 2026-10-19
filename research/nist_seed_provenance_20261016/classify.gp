\\ Classify census output with the criteria of F. Valsorda's seeds.go:
\\ prime order, bitlen(n) <= bitlen(p), n != p, and p^k != 1 mod n for k < 2^10.
\\ Globals: P, ORDERS (path of concatenated "i N0 Nt" lines), RUN (label).
{
my(L = readstr(ORDERS), acc = List(), bl = List(), tw = List(), rows = List());
for (k = 1, #L, listput(rows, apply(eval, strsplit(L[k], " "))));
rows = vecsort(Vec(rows), 1);
for (k = 1, #rows,
  my(i = rows[k][1], n = rows[k][2], nt = rows[k][3]);
  if (n && isprime(n),
    if (#binary(n) > #binary(P), listput(bl, i),
      my(x = Mod(1, n), mov = 1);
      for (e = 1, 2^10 - 1, x *= P; if (x == 1, mov = 0; break));
      if (n != P && mov, listput(acc, i))),
    if (nt && isprime(nt), listput(tw, i))));
print(RUN, " p", #binary(P), " candidates ", #rows);
print("  accepted:           ", Vec(acc));
print("  n longer than p:    ", Vec(bl));
print("  only twist prime:   ", Vec(tw));
print("JSON {\"run\": \"", RUN, "\", \"p_bits\": ", #binary(P), ", \"candidates\": ", #rows, ", \"accepted\": ", Vec(acc), ", \"n_longer_than_p\": ", Vec(bl), ", \"only_twist_prime\": ", Vec(tw), "}");
}
quit;
