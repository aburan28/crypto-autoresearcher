default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
budget = 14400000; t0 = getwalltime(); idx = 0; found = 0; c = 1; nfilt = 0;
{
while(!found,
  for(i = 1, 4, for(s = 0, 1,
    idx++; b = if(s == 0, c*z^i, -c*z^i);
    if(issquare(b) || issquare(4 - 4*b), nfilt++; print("CAND idx=", idx, " c=", c, " i=", i, " s=", s, " filtered=1"); next);
    A = b - 4/3; B = 16/27 - 2*b/3; E = ellinit([A, B]);
    t1 = getwalltime(); N = ellsea(E, 2); dt = getwalltime() - t1;
    pr = if(N == 0 || N % 2 != 0, 0, isprime(N/2));
    print("CAND idx=", idx, " c=", c, " i=", i, " s=", s, " sea=", N, " twoprime=", pr, " ms=", dt);
    if(pr, found = 1; print("FOUND=", idx, " ", c, " ", i, " ", s); break(2));
    if(getwalltime() - t0 > budget, found = -1; print("BUDGET=", idx); break(2))));
  if(!found, c++));
}
print("NFILT=", nfilt); print("DONE=", found);
