default(parisizemax, 2000000000);
p = 18446744069414584321; z = ffgen(Mod(1,p)*(x^5-3), 'z);
budget = 14400000; t0 = getwalltime(); idx = 0; found = 0; A = 0; c = 1;
{
while(!found,
  for(i = 1, 4,
    idx++; E = ellinit([A, c*z^i]); t1 = getwalltime(); N = ellsea(E, 1); dt = getwalltime() - t1;
    pr = if(N == 0, 0, isprime(N));
    print("CAND idx=", idx, " A=", A, " c=", c, " i=", i, " sea=", N, " prime=", pr, " ms=", dt);
    if(pr, found = 1; print("FOUND=", idx, " ", A, " ", c, " ", i); break);
    if(getwalltime() - t0 > budget, found = -1; print("BUDGET=", idx); break));
  if(!found, c++; if(c == 50, c = 1; A++)));
}
print("DONE=", found);
