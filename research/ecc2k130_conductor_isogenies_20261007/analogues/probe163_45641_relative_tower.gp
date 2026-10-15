\\ Bounded compatibility probe for the K-163 conductor-45641 descent.
\\
\\ This is deliberately separate from the frozen full-map producer.  It
\\ replaces the absolute F_(2^(163*20)) field plus ffembed/ffinvmap with the
\\ relative tower F_(2^163)[u]/P_20(u).  Since gcd(163,20)=1, an irreducible
\\ degree-20 polynomial over F_2 remains irreducible over F_(2^163), and the
\\ standard NIST base field embeds as the constant coefficients.
\\
\\ The probe deterministically constructs one exact-order 45641-torsion
\\ x-coordinate, certifies whether its line is horizontal or descending by
\\ testing the two tau-eigenlines, and constructs the normalized endpoint.
\\ It stops before constructing the degree-22820 kernel polynomial or a point
\\ map.  Execute through run_probe163_45641_relative_tower.gp with PARI/GP
\\ 2.15.2 so unexpected GP exceptions fail closed.

{if(type(FAIL_CLOSED_DRIVER) != "t_INT" || FAIL_CLOSED_DRIVER != 1,
  print("RESULT=FAIL reason=use_run_probe163_45641_relative_tower_driver");
  quit(1)
)};
if(getenv("GP_FAIL_CLOSED_FAULT") == "1", error("injected fail-closed fault"));

SCHEMA = "k163-degree45641-relative-tower-probe-v2";
MOD = x^163 + x^7 + x^6 + x^3 + 1;
m = 163;
a2 = 1;
ell = 45641;
k = 20;
seed = 45641;
max_tries = 64;
batch_size = 256;
r = 0x4000000000000000000020108A2E0CC0D99F8A5EF;

g = ffgen(Mod(1, 2) * MOD, 'g);
q = 2^m;
E0 = ellinit([1, a2, 0, 0, 1], g);
N = ellcard(E0);

{must(ok, message) =
  if(!ok,
    print("RESULT=FAIL reason=", message);
    quit(1)
  )
};
{base_to_int(z) =
  if(z == 0, 0, subst(lift(z.pol), variable(z.pol), 2))
};
{orbmin(z) =
  my(c = z^2, least = base_to_int(z));
  while(c != z, least = min(least, base_to_int(c)); c = c^2);
  least
};
{orbit_size(z) =
  my(c = z^2, n = 1);
  while(c != z && n <= m, c = c^2; n++);
  must(c == z, "endpoint Frobenius orbit did not close");
  n
};

must(polisirreducible(Mod(1, 2) * MOD), "NIST K-163 field polynomial is reducible");
must(N == 2*r, "standard K-163 group order mismatch");
must(isprime(r), "standard subgroup order is not prime");
must(isprime(ell) && gcd(ell, r) == 1, "bad isogeny degree");

source_trace = q + 1 - N;
fpi_squared = (4*q - source_trace^2) / 7;
fpi = sqrtint(fpi_squared);
must(fpi^2 == fpi_squared, "source Frobenius conductor is not integral");
must(valuation(fpi, ell) == 1, "45641 does not occur exactly once in the Frobenius conductor");
must(qfbclassno(-7) == 1, "Z[tau] is not the maximal order expected here");
must(kronecker(-7, ell) == 1, "45641 does not split in Q(sqrt(-7))");

\\ Build a direct relative tower.  No subfield root search or inverse
\\ embedding map is involved.
t_field = getwalltime();
P20_binary = lift(ffinit(2, k, 'u));
P20 = P20_binary * g^0;
must(polisirreducible(P20), "degree-20 binary polynomial became reducible over F_(2^163)");
uK = Mod('u, P20);
must(uK^(q^k) == uK, "relative generator failed absolute Frobenius closure");
must(g^q == g, "base generator is not fixed by q-Frobenius");
field_ms = getwalltime() - t_field;

random_K() = Mod(Polrev(vector(k, i, random(g)), 'u), P20);

mu = 1;
{trk(kk) =
  my(P = lift(Mod(x, x^2 - mu*x + 2)^(m*kk)));
  2*polcoef(P, 0) + mu*polcoef(P, 1)
};
{xdbl(R) =
  my(X2 = R[1]^2, Z2 = R[2]^2);
  [X2^2 + Z2^2, X2*Z2]
};
{xadd(R, S, xD) =
  my(A = R[1]*S[2], B = S[1]*R[2], Z = (A+B)^2);
  [xD*Z + A*B, Z]
};
\\ Differential addition with a projective difference D.  This lets the
\\ endpoint census avoid one inversion for every kernel abscissa.
{xadd_projective(R, S, D) =
  my(A = R[1]*S[2], B = S[1]*R[2], Z = (A+B)^2);
  [D[1]*Z + D[2]*A*B, D[2]*Z]
};
{ladder(x0, n) =
  if(n == 0, return([1, 0]));
  my(R0 = [x0, x0^0], R1 = xdbl(R0));
  forstep(i = #binary(n)-2, 0, -1,
    if(bittest(n, i),
      R0 = xadd(R0, R1, x0); R1 = xdbl(R1),
      R1 = xadd(R0, R1, x0); R0 = xdbl(R0)
    )
  );
  R0
};

\\ Sum X_i/Z_i with a single inversion for a bounded batch.
{batch_sum_x(Xs, Zs, n) =
  my(prefix = vector(n), inverse_product, inverse_zi,
     total = 0*Xs[1]);
  must(n > 0, "empty inversion batch");
  prefix[1] = Zs[1];
  for(i = 2, n, prefix[i] = prefix[i-1]*Zs[i]);
  must(prefix[n] != 0, "kernel enumeration reached infinity early");
  inverse_product = 1/prefix[n];
  forstep(i = n, 2, -1,
    inverse_zi = inverse_product*prefix[i-1];
    total += Xs[i]*inverse_zi;
    inverse_product *= Zs[i]
  );
  total + Xs[1]*inverse_product
};

\\ q-Frobenius is scalar c on E[ell].  The absolute Frobenius tau has
\\ characteristic polynomial T^2-T+2.
tau_roots = polrootsmod('T^2 - 'T + 2, ell);
must(#tau_roots == 2, "tau polynomial did not have two roots modulo 45641");
c1 = lift(tau_roots[1]^m);
c2 = lift(tau_roots[2]^m);
must(c1 == c2, "q-Frobenius is not scalar modulo 45641");
c = c1;
must(znorder(Mod(c, ell)) == 2*k, "unexpected q-Frobenius order");
must(lift(Mod(c, ell)^k) == ell-1, "kernel x-coordinate is not in the expected twist field");

ext_order = q^k + 1 + trk(k);
v_ell = valuation(ext_order, ell);
must(v_ell == 2, "unexpected 45641-adic valuation in the twist order");
cofactor = ext_order / ell^v_ell;

t_witness = getwalltime();
setrand(seed);
xq = 0;
tries = 0;
{
while(xq == 0 && tries < max_tries,
  tries++;
  x0 = random_K();
  R0 = ladder(x0, cofactor);
  if(R0[2] == 0, next);
  xr = R0[1]/R0[2];
  for(j = 1, v_ell,
    T0 = ladder(xr, ell);
    if(T0[2] == 0, xq = xr; break);
    xr = T0[1]/T0[2]
  )
);
};
must(xq != 0, "bounded witness search exhausted max_tries");
must(ladder(xq, ell)[2] == 0, "kernel witness does not have exact order 45641");

\\ Certify the relative degree and the q-Frobenius scalar action.
fq = xq;
x_orbit = 0;
{for(d = 1, k, fq = fq^q; if(fq == xq, x_orbit = d; break));};
must(x_orbit == k, "kernel x-coordinate has the wrong relative degree");
Fc = ladder(xq, c);
must(Fc[2] != 0 && Fc[1] == xq^q*Fc[2], "q-Frobenius scalar action failed on the sampled line");

\\ Certify the concrete witness's minimal absolute x-coordinate degree.
\\ Closure at 3260 plus exclusion at N/p for every distinct p|3260 is an
\\ exact-order certificate.  Because ell is prime, the same certificate
\\ applies to every nonzero multiple in this cyclic kernel line.
t_absolute_orbit = getwalltime();
absolute_x_degree = m*k;
absolute_exclusion_degrees = [absolute_x_degree/2, absolute_x_degree/5, absolute_x_degree/163];
absolute_exclusion_passes = vector(#absolute_exclusion_degrees);
absolute_frobenius = xq;
{for(d = 1, absolute_x_degree,
  absolute_frobenius = absolute_frobenius^2;
  for(j = 1, #absolute_exclusion_degrees,
    if(d == absolute_exclusion_degrees[j],
      absolute_exclusion_passes[j] = absolute_frobenius != xq
    )
  )
);};
must(absolute_frobenius == xq, "absolute Frobenius orbit did not close at degree 3260");
must(vecmin(absolute_exclusion_passes) == 1, "absolute x-coordinate degree is a proper divisor of 3260");
absolute_orbit_ms = getwalltime() - t_absolute_orbit;

\\ The only horizontal ell-kernels from the maximal crater are the two
\\ tau-eigenlines.  Equality of projective x-coordinates is sufficient here:
\\ tau(Q) has x-coordinate x(Q)^2 and x cannot distinguish Q from -Q.
tau_matches = vector(#tau_roots);
{for(i = 1, #tau_roots, Ti = ladder(xq, lift(tau_roots[i])); tau_matches[i] = Ti[2] != 0 && Ti[1] == xq^2*Ti[2]);};
tau_line_stable = vecsum(tau_matches) != 0;
classification = if(tau_line_stable, "horizontal", "descending");
must(!tau_line_stable, "deterministic witness selected a horizontal line, not a floor descent");
witness_ms = getwalltime() - t_witness;

\\ Enumerate the half-kernel projectively and recover only its first
\\ symmetric sum.  That sum is the coefficient needed for the endpoint;
\\ no degree-22820 polynomial is materialized.
t_endpoint = getwalltime();
half = (ell-1)/2;
Xbatch = vector(batch_size);
Zbatch = vector(batch_size);
fill = 0;
batches = 0;
sum_x = 0*uK;

Qx = [xq, xq^0];
Rprev = Qx;
Rcur = xdbl(Qx);
fill++; Xbatch[fill] = Rprev[1]; Zbatch[fill] = Rprev[2];
fill++; Xbatch[fill] = Rcur[1]; Zbatch[fill] = Rcur[2];

{for(i = 3, half,
  Rnext = xadd_projective(Rcur, Qx, Rprev);
  Rprev = Rcur;
  Rcur = Rnext;
  must(Rcur[2] != 0, "kernel enumeration reached infinity early");
  if(i <= 8,
    Li = ladder(xq, i);
    must(Li[2] != 0 && Li[1]*Rcur[2] == Rcur[1]*Li[2],
      Str("projective recurrence mismatch at multiple ", i))
  );
  fill++;
  Xbatch[fill] = Rcur[1];
  Zbatch[fill] = Rcur[2];
  if(fill == batch_size || i == half,
    sum_x += batch_sum_x(Xbatch, Zbatch, fill);
    batches++;
    fill = 0
  )
);};
must(fill == 0, "final inversion batch was not flushed");

b_endpoint_K = 1 + sum_x + sum_x^2;
must(b_endpoint_K^q == b_endpoint_K, "endpoint coefficient did not descend to F_(2^163)");
b_lift = lift(b_endpoint_K);
{if(type(b_lift) == "t_POL",
  must(poldegree(b_lift) <= 0, "q-fixed endpoint retained a nonconstant relative-tower term");
  b_endpoint = polcoef(b_lift, 0),
  b_endpoint = b_lift
);};
must(b_endpoint != 1, "descending endpoint equals the source j-invariant");
E1 = ellinit([1, a2, 0, 0, b_endpoint], g);
must(ellcard(E1) == N, "endpoint point count differs from the source");
endpoint_ms = getwalltime() - t_endpoint;

xq_lift = lift(xq);
xq_coefficients = vector(k, i, base_to_int(polcoef(xq_lift, i-1, 'u)));
endpoint_int = base_to_int(b_endpoint);
endpoint_orbit = orbit_size(b_endpoint);
endpoint_orbit_min = orbmin(b_endpoint);

print("SCHEMA=", SCHEMA);
print("FIELD relative_degree=", k, " binary_modulus=", P20_binary, " setup_ms=", field_ms);
print("SOURCE order=", N, " trace=", source_trace, " v_45641_fpi=", valuation(fpi, ell), " split=", kronecker(-7, ell));
print("WITNESS seed=", seed, " tries=", tries, " exact_order=", ell, " relative_x_degree=", x_orbit, " cofactor_bits=", #binary(cofactor), " witness_ms=", witness_ms);
print("WITNESS_X_COEFFICIENTS=", xq_coefficients);
print("ABSOLUTE_X_ORBIT degree=", absolute_x_degree, " closure=PASS excluded_degrees=", absolute_exclusion_degrees, " exclusions=", absolute_exclusion_passes, " all_nonzero_kernel_multiples=DERIVED orbit_ms=", absolute_orbit_ms);
print("TAU roots=", apply(lift, tau_roots), " eigenline_matches=", tau_matches, " classification=", classification, " classification_basis=DERIVED target_conductor=", ell);
print("ENDPOINT b=", endpoint_int, " a2=", a2, " orbit_size=", endpoint_orbit, " orbit_min=", endpoint_orbit_min, " point_count=PASS", " half_kernel_count=", half, " inversion_batches=", batches, " endpoint_ms=", endpoint_ms);
print("STOP=before_kernel_polynomial_and_point_map");
print("RESULT=PASS");
RUN_COMPLETE = 1;
