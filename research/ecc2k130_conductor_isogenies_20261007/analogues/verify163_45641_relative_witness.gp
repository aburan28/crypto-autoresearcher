\\ Independent verifier for the retained K-163 degree-45641 relative-tower
\\ witness.  This script does not repeat the randomized witness search or
\\ construct an isogeny map.  It reconstructs the recorded x-coordinate
\\ from its 20 low-to-high tower coefficients and verifies the exact field
\\ and prime-kernel-line claims needed by the preflight receipt.
\\
\\ Run this file directly with PARI/GP 2.15.2.  Every expected or unexpected
\\ failure terminates with a nonzero process status.

default(parisizemax, "1G");
default(parisize, "64M");

{must(ok, message) =
  if(!ok,
    print("RESULT=FAIL reason=", message);
    quit(1)
  )
};

{base_from_int(n, gg) =
  my(bits, z = 0*gg);
  must(type(n) == "t_INT" && n >= 0, "invalid base-field integer coefficient");
  bits = binary(n);
  for(i = 1, #bits, z = z*gg + bits[i]);
  z
};

{base_to_int(z) =
  if(z == 0, 0, subst(lift(z.pol), variable(z.pol), 2))
};

{xdbl(R) =
  my(X2 = R[1]^2, Z2 = R[2]^2);
  [X2^2 + Z2^2, X2*Z2]
};

{xadd(R, S, xD) =
  my(A = R[1]*S[2], B = S[1]*R[2], Z = (A+B)^2);
  [xD*Z + A*B, Z]
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

{run_verifier() =
SCHEMA = "k163-degree45641-relative-witness-verifier-v1";
MOD = x^163 + x^7 + x^6 + x^3 + 1;
P20_binary = u^20 + u^17 + u^16 + u^12 + u^9 + u^6 + u^5 + u^4 + u^3 + u^2 + 1;
m = 163;
k = 20;
q = 2^m;
ell = 45641;
a2 = 1;
r = 0x4000000000000000000020108A2E0CC0D99F8A5EF;
expected_order = 2*r;

\\ These are the retained coefficients of x_Q in the basis
\\ 1,u,...,u^19.  Each integer encodes a base-field element in the basis
\\ 1,g,...,g^162, with its binary digits interpreted low-to-high.
witness_coefficient_ints = [
  8416914329311737206877341783647981268260531216998,
  10387836817098093773703417770172075822643813861483,
  11141751882429427672694856431327970270832357091156,
  8580726175355152578781285989030698227137619552212,
  10166214974330763067438780031962548728573764715051,
  3445126340816646533179104493833292689181909409927,
  3010815635619347532580045553766513295665545658348,
  8249342885619861820175312382546199363447643451311,
  4563313416945655303543230130341618123253862730075,
  9647461779805602444999938575222316455808143316622,
  1216081951483248905271941039956883284365440135780,
  3007569193289768688471509781097639851036002275758,
  6606036553356497149109090861104326406394417533069,
  7807657772775863131863758555036966454234684883664,
  3875172395631038601668517690519297787085992693597,
  8296325341989476682811920611923134299020274064843,
  1294569333446305620282170578782555557388868160564,
  1776719410388431020004287143865544296632087815454,
  7463206397965831487018630427914793380857945424932,
  10132638735371964362345638452223886397397956765823
];

t0 = getwalltime();
must(polisirreducible(Mod(1, 2)*MOD), "NIST K-163 field polynomial is reducible");
must(poldegree(P20_binary) == k && pollead(P20_binary) == 1,
     "binary tower polynomial is not monic of degree 20");
must(polisirreducible(Mod(1, 2)*P20_binary), "binary degree-20 polynomial is reducible");
g = ffgen(Mod(1, 2)*MOD, 'g);
must(g^q == g, "base-field generator failed 2^163-Frobenius closure");
must(g^2 != g, "base-field generator collapsed to F_2");

P20 = P20_binary*(g^0);
must(polisirreducible(P20), "degree-20 polynomial is reducible over F_(2^163)");
uK = Mod('u, P20);
must(uK^(q^k) == uK, "relative generator failed degree-20 closure");
must(uK^(q^(k/2)) != uK && uK^(q^(k/5)) != uK,
     "relative generator lies in a proper maximal subfield");
field_ms = getwalltime() - t0;

E0 = ellinit([1, a2, 0, 0, 1], g);
source_order = ellcard(E0);
must(source_order == expected_order, "standard K-163 group order mismatch");
must(isprime(r), "standard K-163 subgroup order is not prime");
must(isprime(ell) && gcd(ell, source_order) == 1, "invalid prime isogeny degree");
source_trace = q + 1 - source_order;
fpi_squared = (4*q - source_trace^2)/7;
fpi = sqrtint(fpi_squared);
must(fpi^2 == fpi_squared, "source Frobenius conductor is not integral");
must(isfundamental(-7), "tau discriminant -7 is not fundamental");
must(qfbclassno(-7) == 1, "Z[tau] is not the maximal CM order expected here");
must(kronecker(-7, ell) == 1, "45641 does not split in Q(sqrt(-7))");
must(valuation(fpi, ell) == 1,
     "45641 does not occur exactly once in the Frobenius conductor");

must(#witness_coefficient_ints == k, "witness coefficient count is not 20");
must(vecmin(vector(k, i, witness_coefficient_ints[i] >= 0 && witness_coefficient_ints[i] < q)) == 1,
     "witness coefficient is outside the canonical base-field range");
witness_coefficients = vector(k, i, base_from_int(witness_coefficient_ints[i], g));
must(vecmin(vector(k, i, base_to_int(witness_coefficients[i]) == witness_coefficient_ints[i])) == 1,
     "base-field coefficient round trip failed");
xq = Mod(Polrev(witness_coefficients, 'u), P20);

t_witness = getwalltime();
one_multiple = ladder(xq, 1);
ell_multiple = ladder(xq, ell);
must(one_multiple[2] != 0, "retained x-coordinate is not finite");
must(ell_multiple[2] == 0 && ell_multiple[1] != 0,
     "retained x-coordinate does not have exact prime order 45641");

\\ Find the first positive q-Frobenius return.  Testing every divisor is
\\ implicit in this first-return loop and independently gives relative
\\ x-coordinate degree exactly 20.
relative_frobenius = xq;
relative_x_degree = 0;
for(d = 1, k,
  relative_frobenius = relative_frobenius^q;
  if(relative_frobenius == xq, relative_x_degree = d; break)
);
must(relative_x_degree == k, "retained x-coordinate does not have relative degree 20");

\\ q-Frobenius is scalar on E[45641].  Verify its scalar action on the
\\ retained line as a separate representation check.
tau_roots = polrootsmod('T^2 - 'T + 2, ell);
must(#tau_roots == 2, "tau polynomial does not split modulo 45641");
q_scalars = apply(z -> lift(z^m), tau_roots);
must(q_scalars[1] == q_scalars[2], "q-Frobenius is not scalar modulo 45641");
q_scalar = q_scalars[1];
must(znorder(Mod(q_scalar, ell)) == 2*k, "q-Frobenius scalar has the wrong order");
q_scalar_multiple = ladder(xq, q_scalar);
must(q_scalar_multiple[2] != 0 && q_scalar_multiple[1] == xq^q*q_scalar_multiple[2],
     "q-Frobenius scalar action failed on the retained line");

\\ On this Koblitz curve tau has x-coordinate action x -> x^2.  The only
\\ horizontal ell-lines are its two eigenlines.  Projective x equality is
\\ enough because x(P)=x(-P).
tau_matches = vector(#tau_roots);
for(i = 1, #tau_roots,
  tau_multiple = ladder(xq, lift(tau_roots[i]));
  tau_matches[i] = tau_multiple[2] != 0 && tau_multiple[1] == xq^2*tau_multiple[2]
);
must(vecsum(tau_matches) == 0, "retained witness lies on a tau eigenline");

\\ Exact absolute x-degree certificate.  Since
\\ 3260 = 2^2 * 5 * 163, closure at 3260 and nonclosure at n/p for each
\\ distinct prime p exclude every proper divisor.
absolute_x_degree = m*k;
absolute_exclusion_degrees = [absolute_x_degree/2, absolute_x_degree/5, absolute_x_degree/163];
absolute_exclusion_passes = vector(#absolute_exclusion_degrees);
absolute_frobenius = xq;
absolute_closure = 0;
for(d = 1, absolute_x_degree,
  absolute_frobenius = absolute_frobenius^2;
  for(j = 1, #absolute_exclusion_degrees,
    if(d == absolute_exclusion_degrees[j],
      absolute_exclusion_passes[j] = absolute_frobenius != xq
    )
  );
  if(d == absolute_x_degree, absolute_closure = absolute_frobenius == xq)
);
must(absolute_closure, "absolute Frobenius orbit did not close at degree 3260");
must(vecmin(absolute_exclusion_passes) == 1,
     "absolute x-coordinate degree is a proper divisor of 3260");

\\ Prime-line inheritance is a mathematical scope assertion, not a sample
\\ census.  For every a in F_ell^*, Frobenius commutes with [a], and [a]
\\ is invertible on the ell-line.  Thus Frob^d([a]Q)=+/-[a]Q iff
\\ Frob^d(Q)=+/-Q, so all nonzero multiples have the same x-orbit degree.
must(isprime(ell) && gcd(ell, 2) == 1,
     "prime-line inheritance requires an odd prime kernel order");
prime_line_scope = ell - 1;

\\ Transcript negative control: dropping the recorded u^19 coefficient
\\ must not be accepted as the retained prime-order witness.  This is cheap
\\ and targets coefficient count/order/truncation errors directly.
must(witness_coefficient_ints[k] != 0, "negative control did not alter the witness");
truncated_coefficients = vector(k, i, if(i == k, 0*g, witness_coefficients[i]));
truncated_xq = Mod(Polrev(truncated_coefficients, 'u), P20);
must(truncated_xq != xq, "truncated-coefficient control equals the witness");
truncated_ell_multiple = ladder(truncated_xq, ell);
truncated_rejected = !(truncated_ell_multiple[2] == 0 && truncated_ell_multiple[1] != 0);
must(truncated_rejected, "truncated-coefficient control passed the exact-order gate");
witness_ms = getwalltime() - t_witness;

print("SCHEMA=", SCHEMA);
print("FIELD base_modulus=", MOD,
      " base_irreducible=PASS base_closure=PASS relative_modulus=", P20_binary,
      " relative_irreducible_over_f2=PASS relative_irreducible_over_base=PASS relative_generator_degree=", k,
      " setup_ms=", field_ms);
print("SOURCE order=", source_order, " subgroup_order=", r, " ell=", ell,
      " v_ell_fpi=", valuation(fpi, ell), " split=", kronecker(-7, ell),
      " curve_and_prime_gates=PASS");
print("TRANSCRIPT coefficient_order=low_to_high coefficient_count=", #witness_coefficient_ints,
      " base_encoding=low_to_high_bits round_trip=PASS");
print("WITNESS exact_x_order=", ell, " relative_x_degree=", relative_x_degree,
      " q_scalar=", q_scalar, " q_scalar_action=PASS");
print("TAU roots=", apply(lift, tau_roots), " eigenline_matches=", tau_matches,
      " classification=descending classification_basis=DERIVED");
print("ABSOLUTE_X_DEGREE degree=", absolute_x_degree, " closure=PASS excluded_degrees=",
      absolute_exclusion_degrees, " exclusions=", absolute_exclusion_passes);
print("PRIME_LINE_SCOPE quantified_nonzero_multipliers=", prime_line_scope,
      " inherited_absolute_x_degree=", absolute_x_degree,
      " status=DERIVED proof=frobenius_commutes_with_invertible_scalars_and_x_identifies_plus_or_minus");
print("NEGATIVE_CONTROL kind=drop_u19_coefficient exact_order_gate=REJECT");
print("CLAIM_BOUNDARY=verifies_retained_kernel_line_not_isogeny_map_or_ecdlp_advantage");
print("VERIFY_MS=", witness_ms);
print("RESULT=PASS");
};

{iferr(run_verifier(), verifier_error,
  print("RESULT=FAIL reason=uncaught_gp_exception detail=", verifier_error);
  quit(1)
)};
