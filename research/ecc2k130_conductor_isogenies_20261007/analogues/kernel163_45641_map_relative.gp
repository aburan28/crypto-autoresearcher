\\ Construct one replayable degree-45641 K-163 forward map using the direct
\\ relative tower F_(2^163)[u]/P_20(u).  This is a separate implementation
\\ from the retained absolute-field/ffembed producer.
\\
\\ The driver must size the PARI stack before read() enters this file.  This
\\ producer writes only after every field, kernel, endpoint, map, subgroup,
\\ planted-log, and homomorphism check passes.

{fail_closed(message) =
  print("RESULT=FAIL reason=", message);
  quit(1)
};
{must(ok, message) =
  if(!ok, fail_closed(message))
};

if(type(OUT) != "t_STR", fail_closed("OUT must be set by the relative driver"));
out_exists = 1;
iferr(readstr(OUT), E, out_exists = 0);
if(out_exists, fail_closed(Str("refusing to append to existing ", OUT)));

SCHEMA = "k163-degree45641-forward-map-relative-v1";
MOD = x^163 + x^7 + x^6 + x^3 + 1;
m = 163;
a2 = 1;
ell = 45641;
k = 20;
seed = 45641;
max_tries = 64;
batch_size = 256;
hom_samples = 16;
planted = 0x123456789abcdef0123456789abcdef;
r = 0x4000000000000000000020108A2E0CC0D99F8A5EF;
gx_int = 0x02fe13c0537bbc11acaa07d793de4e6d5e5c94eee8;
gy_int = 0x0289070fb05d38ff58321f2e800536d538ccdaa3d9;
expected_endpoint_orbit_min = 664574991296028830578085892445595444511031875;
archived_orbit_minima = Set([20183018253319052689704116247546275258431720285, 1699056145793825809974781818934579013935268431, 71177121262957429327531167482112665894165601519, 86418753047285346854356540661746105839786105877, 41105051057298702718687969060611106606052833369, 9458681452661928675008670406069307198816595651]);

run_start_ms = getwalltime();
print("CHECKPOINT phase=init schema=", SCHEMA);

g = ffgen(Mod(1, 2) * MOD, 'g);
q = 2^m;
E0 = ellinit([1, a2, 0, 0, 1], g);
N = ellcard(E0);

{base_to_int(z) =
  if(z == 0, 0, subst(lift(z.pol), variable(z.pol), 2))
};
{fromint(n) =
  my(s = 0*g, j = 0);
  while(n, if(n % 2, s += g^j); n \= 2; j++);
  s
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
{canon_index(j) =
  my(v = j % ell);
  if(v < 0, v += ell);
  min(v, ell-v)
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
must(qfbclassno(-7) == 1, "source CM order is not the expected maximal order");
must(kronecker(-7, ell) == 1, "45641 does not split in Q(sqrt(-7))");

G0 = [fromint(gx_int), fromint(gy_int)];
must(ellisoncurve(E0, G0), "standard generator is off curve");
must(ellmul(E0, G0, r) == [0], "standard generator fails subgroup check");
must(planted > 0 && planted < r, "planted scalar outside subgroup");

\\ Give the kernel-polynomial variable higher priority than the relative
\\ tower variable.  Coefficients of an X-polynomial may then be t_POLMODs in
\\ u without PARI attempting an invalid variable reordering.
Xvar = varhigher("X");
uvar = varlower("u", Xvar);

t_field_ms = getwalltime();
P20_binary = lift(ffinit(2, k, uvar));
P20 = P20_binary * g^0;
must(polisirreducible(P20), "degree-20 binary polynomial became reducible over F_(2^163)");
uK = Mod(uvar, P20);
must(uK^(q^k) == uK, "relative generator failed absolute Frobenius closure");
must(g^q == g, "base generator is not fixed by q-Frobenius");
field_ms = getwalltime() - t_field_ms;
print("CHECKPOINT phase=field_ready relative_degree=", k, " setup_ms=", field_ms, " modulus=", P20_binary);

random_K() = Mod(Polrev(vector(k, i, random(g)), uvar), P20);

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

\\ Convert one bounded batch of projective x-coordinates with one inverse.
{batch_affine_x(Xs, Zs, n) =
  my(prefix = vector(n), affine = vector(n), inverse_product, inverse_zi);
  must(n > 0, "empty inversion batch");
  prefix[1] = Zs[1];
  for(i = 2, n, prefix[i] = prefix[i-1]*Zs[i]);
  must(prefix[n] != 0, "kernel enumeration reached infinity early");
  inverse_product = 1/prefix[n];
  forstep(i = n, 2, -1,
    inverse_zi = inverse_product*prefix[i-1];
    affine[i] = Xs[i]*inverse_zi;
    inverse_product *= Zs[i]
  );
  affine[1] = Xs[1]*inverse_product;
  affine
};

\\ q-Frobenius is scalar c on E[ell].  Absolute Frobenius tau satisfies
\\ T^2-T+2, and its two eigenspaces are exactly the horizontal ell-lines.
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

t_witness_ms = getwalltime();
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

fq = xq;
x_orbit = 0;
{for(d = 1, k, fq = fq^q; if(fq == xq, x_orbit = d; break));};
must(x_orbit == k, "kernel x-coordinate has the wrong relative degree");

\\ Certify the absolute F_2 degree independently of the relative q-orbit.
\\ Since 3260=2^2*5*163, exclusion from the three maximal proper subfields
\\ at exponents 1630, 652, and 20 plus 3260-step closure proves degree 3260.
t_absolute_degree_ms = getwalltime();
xq_abs_frob = xq;
absolute_equal_20 = -1;
absolute_equal_652 = -1;
absolute_equal_1630 = -1;
{
for(j = 1, m*k,
  xq_abs_frob = xq_abs_frob^2;
  if(j == 20, absolute_equal_20 = (xq_abs_frob == xq));
  if(j == 652, absolute_equal_652 = (xq_abs_frob == xq));
  if(j == 1630, absolute_equal_1630 = (xq_abs_frob == xq))
);
};
must(xq_abs_frob == xq, "kernel witness failed absolute 3260-step Frobenius closure");
must(absolute_equal_1630 == 0, "kernel witness lies in the degree-1630 subfield");
must(absolute_equal_652 == 0, "kernel witness lies in the degree-652 subfield");
must(absolute_equal_20 == 0, "kernel witness lies in the degree-20 subfield");
absolute_x_degree = m*k;
absolute_degree_ms = getwalltime() - t_absolute_degree_ms;
absolute_subfield_exponents = [1630, 652, 20];
absolute_subfield_equalities = [absolute_equal_1630, absolute_equal_652, absolute_equal_20];
print("CHECKPOINT phase=absolute_degree_ready degree=", absolute_x_degree, " closure_exponent=", m*k, " excluded_subfield_exponents=", absolute_subfield_exponents, " degree_ms=", absolute_degree_ms);
kill(xq_abs_frob);

Fc = ladder(xq, c);
must(Fc[2] != 0 && Fc[1] == xq^q*Fc[2], "q-Frobenius scalar action failed on sampled kernel line");

tau_matches = vector(#tau_roots);
{for(i = 1, #tau_roots, Ti = ladder(xq, lift(tau_roots[i])); tau_matches[i] = Ti[2] != 0 && Ti[1] == xq^2*Ti[2]);};
tau_line_stable = vecsum(tau_matches) != 0;
must(!tau_line_stable, "deterministic witness selected a horizontal line, not a floor descent");
witness_ms = getwalltime() - t_witness_ms;
xq_lift = lift(xq);
xq_coefficients = vector(k, i, base_to_int(polcoef(xq_lift, i-1, uvar)));
print("CHECKPOINT phase=witness_ready tries=", tries, " exact_order=", ell, " relative_x_degree=", x_orbit, " tau_matches=", tau_matches, " classification=descending witness_ms=", witness_ms);

\\ Enumerate all half-kernel x-coordinates projectively.  Each 256-element
\\ batch uses one inversion, is converted to affine form, and is retained for
\\ the Frobenius-orbit factorization.  The running sum independently checks
\\ the eventual X^(half-1) kernel coefficient.
t_enum_ms = getwalltime();
half = (ell-1)/2;
xs = vector(half);
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
    must(Li[2] != 0 && Li[1]*Rcur[2] == Rcur[1]*Li[2], Str("projective recurrence mismatch at multiple ", i))
  );
  fill++;
  Xbatch[fill] = Rcur[1];
  Zbatch[fill] = Rcur[2];
  if(fill == batch_size || i == half,
    affine_batch = batch_affine_x(Xbatch, Zbatch, fill);
    batch_start = i-fill+1;
    for(j = 1, fill,
      xs[batch_start+j-1] = affine_batch[j];
      sum_x += affine_batch[j]
    );
    batches++;
    if(batches % 10 == 0 || i == half, print("PROGRESS phase=kernel_x batches=", batches, " points=", i, "/", half));
    fill = 0
  )
);};
must(fill == 0, "final inversion batch was not flushed");
must(#Set(xs) == half, "half-kernel abscissae are not distinct");
enum_ms = getwalltime() - t_enum_ms;
print("CHECKPOINT phase=kernel_x_ready count=", half, " inversion_batches=", batches, " enum_ms=", enum_ms);

\\ A q-Frobenius orbit factor must have every relative-tower coefficient in
\\ the constant subfield.  Descent requires literal u-degree zero and a
\\ round trip back into the tower; no root search or inverse embedding map is
\\ used.
{descend_relative(z) =
  my(v = lift(z), b);
  if(type(v) == "t_POL",
    must(poldegree(v) <= 0, "relative coefficient retained a nonconstant u term");
    b = polcoef(v, 0, uvar),
    b = v
  );
  b *= g^0;
  must(b^q == b, "descended coefficient is not in F_(2^163)");
  must(b*uK^0 == z, "relative coefficient failed constant-subfield round trip");
  b
};
{product_tree(V) =
  my(L = V, n, level = 0);
  if(#L == 0, return(1));
  while(#L > 1,
    n = (#L+1) \ 2;
    L = vector(n, j, if(2*j <= #L, L[2*j-1]*L[2*j], L[2*j-1]));
    level++;
    print("PROGRESS phase=product_tree level=", level, " factors=", #L)
  );
  L[1]
};

t_factors_ms = getwalltime();
seen = vector(half);
orbit_factors = List();
{
for(i = 1, half,
  if(seen[i], next);
  inds = vector(k);
  scalar_index = i;
  for(j = 1, k,
    idx = canon_index(scalar_index);
    must(idx != 0 && !seen[idx], "Frobenius orbit collision");
    inds[j] = idx;
    seen[idx] = 1;
    scalar_index = lift(Mod(scalar_index, ell)*Mod(c, ell))
  );
  must(canon_index(scalar_index) == i, "Frobenius orbit did not close");
  fK = prod(j = 1, k, Xvar + xs[inds[j]]);
  must(poldegree(fK) == k && pollead(fK) == 1, "bad relative orbit factor");
  coeffs = vector(k+1, j, descend_relative(polcoef(fK, j-1, Xvar)));
  factor_base = Polrev(coeffs, Xvar);
  must(factor_base*uK^0 == fK, "orbit factor failed relative/base round trip");
  listput(orbit_factors, factor_base);
  if(#orbit_factors % 100 == 0, print("PROGRESS phase=orbit_factors built=", #orbit_factors, "/", half/k))
);
};
must(vecsum(seen) == half, "incomplete half-kernel coverage");
must(#orbit_factors == half/k, "wrong number of Frobenius orbit factors");
factors_ms = getwalltime() - t_factors_ms;
print("CHECKPOINT phase=orbit_factors_ready count=", #orbit_factors, " factors_ms=", factors_ms);

t_product_ms = getwalltime();
h = product_tree(Vec(orbit_factors));
product_ms = getwalltime() - t_product_ms;
must(poldegree(h) == half && pollead(h) == 1, "bad kernel polynomial");
hp = deriv(h);
must(poldegree(gcd(h, hp)) == 0, "kernel polynomial is not squarefree");
must(subst(h, Xvar, xq) == 0, "kernel witness is not a root of the kernel polynomial");
sum_x_base = descend_relative(sum_x);
tcoef = polcoef(h, half-1, Xvar);
must(tcoef == sum_x_base, "kernel trace coefficient disagrees with batched x-sum");
print("CHECKPOINT phase=kernel_polynomial_ready degree=", poldegree(h), " squarefree=1 product_ms=", product_ms);

\\ The exact identity gate needs h, hp, and xq but not the retained
\\ enumeration/factorization workspaces.  Drop those references before its
\\ degree-six numerator arithmetic so a later PARI repile can reclaim them.
kill(xs);
kill(Xbatch);
kill(Zbatch);
kill(affine_batch);
kill(seen);
kill(orbit_factors);
kill(inds);
kill(fK);
kill(coeffs);
kill(factor_base);
kill(sum_x);
kill(sum_x_base);
kill(Qx);
kill(Rprev);
kill(Rcur);
kill(Rnext);
print("CHECKPOINT phase=enumeration_workspace_released");

\\ Audited normalized characteristic-2 Velu evaluator.  h^[j] is the j-th
\\ Hasse derivative.  Infinity and kernel-x-root dispatch are explicit.  The
\\ latter uses a dummy y-coordinate because dispatch occurs before y is read;
\\ it is not represented as a point-level kernel test.
{hasse_eval(H, j, xx) =
  my(acc = 0*g, d = poldegree(H));
  forstep(i = d, j, -1,
    acc *= xx;
    if(bitand(i, j) == j, acc += polcoef(H, i, Xvar))
  );
  acc
};
\\ Construct an exact Hasse derivative as a polynomial.  Lucas's theorem
\\ gives binomial(i,j) mod 2 through the bit-subset test below.
{hasse_polynomial(H, j) =
  my(d = poldegree(H), z = 0*g);
  if(d < j, return(z));
  Polrev(vector(d-j+1, t,
    if(bitand(t+j-1, j) == j, polcoef(H, t+j-1, Xvar), z)
  ), Xvar)
};
{velu_point(P) =
  if(P == [0], return([0]));
  my(xx = P[1], yy = P[2], hv = subst(h, Xvar, xx));
  if(hv == 0, return([0]));
  my(hinv = 1/hv, L = subst(hp, Xvar, xx)*hinv,
     E2 = hasse_eval(h, 2, xx)*hinv,
     E3 = hasse_eval(h, 3, xx)*hinv,
     parity = poldegree(h) % 2,
     A = parity + xx*L,
     P3 = L^3 + L*E2 + E3,
     Xout, Yout, z3sum, ycoeff);
  Xout = xx + A + A^2;
  ycoeff = 1 + L + xx*L^2;
  z3sum = parity + xx*L + xx^2*L^2 + xx^3*P3;
  Yout = ycoeff*yy + xx*(A^2+A) + A + z3sum;
  [Xout, Yout]
};

\\ Exact function-field gate for the same normalized Velu terms used above.
\\ It clears only powers of the nonzero kernel polynomial H; consequently
\\ each zero numerator is equivalent to the corresponding rational-function
\\ identity in F_(2^163)(X).  With
\\   A=a_num/H, X'=x_num/H^2, alpha=alpha_num/H^2,
\\   beta=beta_num/H^3,
\\ the two checked numerators have denominators H^4 and H^6 respectively.
{velu_function_field_identity_gate(H, H1, btarget) =
  my(n = poldegree(H), parity = n % 2,
     H2 = hasse_polynomial(H, 2), H3 = hasse_polynomial(H, 3),
     Hsq = H^2, H6,
     a_num, x_num, alpha_num, p3_num, z3_num, beta_num,
     beta_simplified, alpha_sq, lhs, rhs,
     x_numerator_reduction_ok, beta_numerator_reduction_ok,
     y_coefficient_ok, constant_ok);
  must(H != 0, "zero kernel polynomial in function-field identity gate");
  a_num = parity*H + Xvar*H1;
  x_num = Xvar*Hsq + a_num*H + a_num^2;
  alpha_num = Hsq + H1*H + Xvar*H1^2;
  p3_num = H1^3 + H1*H2*H + H3*Hsq;
  z3_num = parity*H*Hsq + Xvar*H1*Hsq + Xvar^2*H1^2*H + Xvar^3*p3_num;
  beta_num = Xvar*(a_num^2 + a_num*H)*H + a_num*Hsq + z3_num;

  \\ Audit the raw Velu numerators before using their lower-peak reductions.
  x_numerator_reduction_ok = (x_num == Xvar*alpha_num);
  beta_simplified = Xvar^2*Hsq*H1
                  + Xvar^2*(1+Xvar)*H*H1^2 + Xvar^3*p3_num;
  beta_numerator_reduction_ok = (beta_num == beta_simplified);

  \\ alpha^2*x + X'*alpha = 0 after multiplication by H^4.
  alpha_sq = alpha_num^2;
  y_coefficient_ok = (Xvar*alpha_sq + x_num*alpha_num == 0);

  \\ alpha^2*(x^3+a2*x^2+1) + beta^2 + X'*beta
  \\   + X'^3 + a2*X'^2 + btarget = 0 after multiplication by H^6.
  \\ After x_num=X*alpha_num, the two a2*X^2 terms cancel in
  \\ characteristic two.  Comparing the following sides is exactly the
  \\ same denominator-cleared identity, with a lower peak allocation.
  H6 = Hsq^3;
  lhs = beta_num*(beta_num + Xvar*H*alpha_num);
  rhs = alpha_sq*(Hsq + Xvar^3*(Hsq + alpha_num)) + btarget*H6;
  constant_ok = (lhs == rhs);
  [y_coefficient_ok, constant_ok,
   x_numerator_reduction_ok, beta_numerator_reduction_ok]
};

b_endpoint = 1 + tcoef + tcoef^2;
endpoint_orbit_min = orbmin(b_endpoint);
endpoint_orbit_size = orbit_size(b_endpoint);
archived_orbit_match = setsearch(archived_orbit_minima, endpoint_orbit_min) != 0;
must(endpoint_orbit_min == expected_endpoint_orbit_min, "deterministic relative endpoint replay mismatch");
must(b_endpoint != 0 && b_endpoint != 1, "descending endpoint is singular or equals the source j-invariant");
E1 = ellinit([1, a2, 0, 0, b_endpoint], g);
must(ellcard(E1) == N, "endpoint point count mismatch");
print("CHECKPOINT phase=endpoint_ready b=", base_to_int(b_endpoint), " orbit_min=", endpoint_orbit_min, " orbit_size=", endpoint_orbit_size, " target_conductor=", ell);

t_identity_ms = getwalltime();
function_field_identity_checks = velu_function_field_identity_gate(h, hp, b_endpoint);
must(function_field_identity_checks[1], "exact function-field y-coefficient identity failed");
must(function_field_identity_checks[2], "exact function-field constant identity failed");
must(function_field_identity_checks[3], "raw X-map numerator reduction failed");
must(function_field_identity_checks[4], "raw beta numerator reduction failed");
identity_ms = getwalltime() - t_identity_ms;
print("CHECKPOINT phase=function_field_identity_ready y_coefficient=PASS constant=PASS raw_numerator_reductions=PASS denominator_powers=[4,6] identity_ms=", identity_ms);

t_map_ms = getwalltime();
must(velu_point([0]) == [0], "infinity exception failed");
must(velu_point([xq, 0]) == [0], "kernel-x-root exception failed");
phiG = velu_point(G0);
must(phiG != [0] && ellisoncurve(E1, phiG), "mapped generator invalid");
must(ellmul(E1, phiG, r) == [0], "mapped generator failed exact prime-subgroup check");
Q0 = ellmul(E0, G0, planted);
phiQ = velu_point(Q0);
must(phiQ == ellmul(E1, phiG, planted), "planted logarithm was not preserved");

setrand(seed+1);
{
for(i = 1, hom_samples,
  scalar_u = random(r-1)+1;
  scalar_v = random(r-1)+1;
  P0 = ellmul(E0, G0, scalar_u);
  Q1 = ellmul(E0, G0, scalar_v);
  mapped_P = velu_point(P0);
  mapped_Q = velu_point(Q1);
  mapped_sum = velu_point(elladd(E0, P0, Q1));
  must(mapped_P == [0] || ellisoncurve(E1, mapped_P), Str("mapped P off endpoint at sample ", i));
  must(mapped_Q == [0] || ellisoncurve(E1, mapped_Q), Str("mapped Q off endpoint at sample ", i));
  must(mapped_sum == elladd(E1, mapped_P, mapped_Q), Str("homomorphism sample failed: ", i));
  if(i % 4 == 0, print("PROGRESS phase=homomorphism samples=", i, "/", hom_samples))
);
};
map_ms = getwalltime() - t_map_ms;
print("CHECKPOINT phase=forward_map_ready subgroup=PASS planted=PASS infinity=PASS kernel_x_root=PASS hom_samples=", hom_samples, " map_ms=", map_ms);

kernel_coefficients = vector(half+1, i, base_to_int(polcoef(h, i-1, Xvar)));
total_ms = getwalltime() - run_start_ms;
{
receipt = [
  SCHEMA,
  ["construction", "relative_tower"],
  ["m", m],
  ["ell", ell],
  ["relative_kernel_x_degree", k],
  ["absolute_kernel_x_degree", absolute_x_degree],
  ["absolute_frobenius_closure_exponent", m*k],
  ["absolute_frobenius_closure_check", 1],
  ["absolute_subfield_exclusion_exponents", absolute_subfield_exponents],
  ["absolute_subfield_equality_checks", absolute_subfield_equalities],
  ["absolute_degree_scope", "all_nonzero_multiples_on_sampled_prime_order_kernel_line"],
  ["absolute_degree_scope_status", "DERIVED"],
  ["relative_modulus", P20_binary],
  ["kernel_polynomial_degree", half],
  ["kernel_polynomial_squarefree", 1],
  ["coefficient_descent", "constant_u_degree_with_round_trip"],
  ["seed", seed],
  ["max_tries", max_tries],
  ["tries", tries],
  ["witness_x_coefficients_low_to_high", xq_coefficients],
  ["frobenius_scalar", c],
  ["tau_roots", apply(lift, tau_roots)],
  ["tau_eigenline_matches", tau_matches],
  ["source_cm_discriminant", -7],
  ["source_frobenius_conductor", fpi],
  ["target_endomorphism_conductor", ell],
  ["tau_kernel_line_stable", tau_line_stable],
  ["source_order", N],
  ["subgroup_order", r],
  ["source_generator", [gx_int, gy_int]],
  ["endpoint_b", base_to_int(b_endpoint)],
  ["endpoint_orbit_size", endpoint_orbit_size],
  ["endpoint_orbit_min", endpoint_orbit_min],
  ["archived_orbit_match_non_gating", archived_orbit_match],
  ["image_generator", [base_to_int(phiG[1]), base_to_int(phiG[2])]],
  ["planted_scalar", planted],
  ["endpoint_point_count_check", 1],
  ["mapped_subgroup_check", 1],
  ["planted_log_check", 1],
  ["infinity_exception_check", 1],
  ["kernel_x_root_exception_check", 1],
  ["function_field_identity_method", "exact_denominator_cleared_factored_polynomial"],
  ["function_field_y_coefficient_identity_check", function_field_identity_checks[1]],
  ["function_field_constant_identity_check", function_field_identity_checks[2]],
  ["function_field_x_numerator_reduction_check", function_field_identity_checks[3]],
  ["function_field_beta_numerator_reduction_check", function_field_identity_checks[4]],
  ["function_field_identity_denominator_powers", [4, 6]],
  ["function_field_identity_scope", "target_curve_equation_away_from_kernel_denominator"],
  ["homomorphism_samples", hom_samples],
  ["batch_size", batch_size],
  ["inversion_batches", batches],
  ["field_ms", field_ms],
  ["witness_including_absolute_degree_and_classification_ms", witness_ms],
  ["absolute_degree_check_nested_ms", absolute_degree_ms],
  ["kernel_x_ms", enum_ms],
  ["orbit_factors_ms", factors_ms],
  ["product_tree_ms", product_ms],
  ["function_field_identity_ms", identity_ms],
  ["map_checks_ms", map_ms],
  ["total_before_artifact_serialization_ms", total_ms],
  ["claim_boundary", "forward_map_only_no_dual_or_weakness_claim"],
  ["kernel_coefficients_low_to_high", kernel_coefficients]
];
};
write(OUT, receipt);
print("ARTIFACT ", OUT, " coefficients=", #kernel_coefficients, " total_ms=", total_ms);
RUN_COMPLETE = 1;
print("RESULT=PASS");
