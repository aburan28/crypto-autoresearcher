\\ Real-field SEA null shard: random prime-order curves y^2 = x^3 - 3x + b over one
\\ NIST/ANSI field, one JSON row per prime-order curve.
\\ Called by run_shard.sh as:
\\   gp -q -f -D datadir=/usr/share/pari sea_null_shard.gp
\\ with FIELD, P_HEX, SEED, TARGET and OUT set in the environment.

field  = getenv("FIELD");
p      = eval(Str("0x", getenv("P_HEX")));
seed   = eval(getenv("SEED"));
target = eval(getenv("TARGET"));
out    = getenv("OUT");

default(parisizemax, 2*10^9);   \\ SEA at 256 bits outgrows the 8 MB default stack
if(!ispseudoprime(p), error("P_HEX is not prime"));
setrand(seed);
ells = primes([3, 691]);             \\ the 124 odd primes 3..691
attempts = 0; found = 0;
{
while(found < target,
  b = random(p); attempts++;
  if((4*(-3)^3 + 27*b^2) % p == 0, next);
  E = ellinit([-3, b], p);
  N = ellsea(E, 1);                    \\ early abort: 0 if a small factor is found
  if(N == 0 || !isprime(N), next);
  t = p + 1 - N; D = t^2 - 4*p;
  S = sum(i = 1, #ells, kronecker(D, ells[i]) == 1);
  found++;
  write(out, Str("{\"field\":\"", field, "\",\"seed\":", seed, ",\"i\":", found,
                 ",\"attempts\":", attempts, ",\"b\":\"", b, "\",\"N\":\"", N,
                 "\",\"t\":\"", t, "\",\"split\":", S, "}"))
);
}
quit;
