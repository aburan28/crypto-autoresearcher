\\ Exact degree-73 forward/dual control for the m=37 Koblitz proxy.
\\
\\ The base field is the repository's basis A.  A deterministic order-73
\\ line constructs the normalized forward map.  On the floor endpoint the
\\ unique upward line is selected algebraically as
\\
\\   gcd(psi_73(X), X^(q^9) - X).
\\
\\ Both maps use the normalized characteristic-2 Velu formula below.  The
\\ dual sign is fixed by requiring dual(phi(G)) = [73]G.  The script then
\\ checks both compositions and exact recovery on every one of 1,024 frozen,
\\ distinct prime-subgroup targets, plus a separate planted target.
\\
\\ Run this file directly: resizing the GP stack from a file included with
\\ read() can make GP return to the caller before executing the remainder.
\\ If the GP variable OUT or environment variable OUT is a nonempty string,
\\ the script writes one receipt there and refuses to overwrite a file.

default(parisizemax, "4G");
default(parisize, "1G");

{must(ok, message) =
  if(!ok,
    print("MAP73_DUAL_CONTROL FAIL ", message);
    quit(1)
  )
}

source_gate = 0;
forward_gate = 0;
dual_gate = 0;
generator_gate = 0;
target_gate = 0;
planted_gate = 0;

{setup() =
out_path = getenv("OUT");
if(type(OUT) == "t_STR", out_path = OUT);
write_receipt = type(out_path) == "t_STR" && #out_path > 0;
if(write_receipt,
  out_exists = 1;
  iferr(readstr(out_path), E, out_exists = 0);
  must(!out_exists, Str("refusing to overwrite existing ", out_path))
);

SCHEMA = "m37-degree73-dual-control-v1";
FORMULA = "char2-normalized-velu-hasse-v1";
MOD = x^37 + x^9 + x^2 + x + 1;
m = 37;
q = 2^m;
lp = 73;
half = (lp - 1) / 2;
N_expected = 137439487532;
r = 230603167;
cofactor_r = 596;
forward_seed = 1;
generator_seed = 73003701;
forward_max_tries = 100000;
generator_max_tries = 100000;
expected_endpoint_b = 4770292313;
target_count = 1024;
target_offset = 0x005A17D3;
target_stride = 104729;
planted_scalar = 0x1234567;

g = ffgen(Mod(1, 2) * MOD, 'g);
E0 = ellinit([1, 0, 0, 0, 1], g);
N = ellcard(E0);
must(polisirreducible(Mod(1, 2) * MOD), "basis-A modulus is reducible");
must(N == N_expected, "source order mismatch");
must(N == cofactor_r * r, "source cofactor mismatch");
must(isprime(r), "prime-subgroup order is not prime");
must(isprime(lp) && gcd(lp, N) == 1, "invalid isogeny degree");
must(planted_scalar > 0 && planted_scalar < r,
     "planted scalar outside prime subgroup");
source_gate = 1;
}

{iferr(setup(), setup_error,
  print("MAP73_DUAL_CONTROL FAIL unexpected setup error: ", setup_error);
  quit(1)
)}

{toint(z) = subst(lift(z.pol), variable(z.pol), 2);}

\\ Evaluate the j-th Hasse derivative without constructing it.
{hasse_eval(H, j, xx) =
  my(acc = 0*g, d = poldegree(H));
  forstep(i = d, j, -1,
    acc *= xx;
    if(bitand(i, j) == j, acc += polcoeff(H, i))
  );
  acc
}

\\ Normalized Velu map between models y^2 + xy = x^3 + b.  A root of H
\\ maps to infinity.  H is monic and contains one x-coordinate for each
\\ nonzero kernel pair {T,-T}.
{velu_point(P, H) =
  if(P == [0], return([0]));
  my(xx = P[1], yy = P[2], v = variable(H), hv = subst(H, v, xx));
  if(hv == 0, return([0]));
  my(hinv = 1/hv,
     L = subst(deriv(H), v, xx)*hinv,
     E2 = hasse_eval(H, 2, xx)*hinv,
     E3 = hasse_eval(H, 3, xx)*hinv,
     parity = poldegree(H) % 2,
     A = parity + xx*L,
     P3 = L^3 + L*E2 + E3,
     Xout, Yout, z3sum, ycoeff);
  Xout = xx + A + A^2;
  ycoeff = 1 + L + xx*L^2;
  z3sum = parity + xx*L + xx^2*L^2 + xx^3*P3;
  Yout = ycoeff*yy + xx*(A^2 + A) + A + z3sum;
  [Xout, Yout]
}

\\ PARI returns an unnormalized image [1,0,0,a4,a6].  The change
\\ y_normalized = y_raw + a4 kills a4 and gives b = a6 + a4^2.
{normalized_image_b(E, H) =
  my(A = ellisogeny(E, H, 1));
  must(#A == 5 && A[1] == 1 && A[2] == 0 && A[3] == 0,
       "unexpected raw isogeny image model");
  A[5] + A[4]^2
}

{dual_point(P) =
  my(Q = velu_point(P, h_dual));
  if(dual_sign == -1 && Q != [0], Q = ellneg(E0, Q));
  Q
}

{run_control() =
\\ Construct the first valid order-73 line under the frozen GP RNG seed in
\\ F_(q^18).  q-Frobenius is scalar on E0[73], so its kernel polynomial
\\ descends coefficient-by-coefficient to basis A.
t_forward = getabstime();
K = ffgen(ffinit(2, m*18), 'h);
EK = ellinit([1, 0, 0, 0, 1], K);
emb = ffembed(g, K);
inv = ffinvmap(emb);
P18 = lift(Mod(-x, x^2 - x + 2)^(m*18));
N18 = 2^(m*18) + 1 - (2*polcoeff(P18, 0, x) + polcoeff(P18, 1, x));
must(valuation(N18, lp) == 2, "unexpected 73-adic extension order");
setrand(forward_seed);
T = [0];
forward_tries = 0;
while(T == [0] || ellmul(EK, T, lp) != [0],
  forward_tries++;
  must(forward_tries <= forward_max_tries,
       "forward kernel search exhausted forward_max_tries");
  T = ellmul(EK, random(EK), N18/lp^2)
);
must(T != [0] && ellmul(EK, T, lp) == [0], "deterministic kernel witness has wrong order");
hK = prod(i = 1, half, 'X - ellmul(EK, T, i)[1]);
must(poldegree(hK) == half && pollead(hK) == 1, "bad extension-field kernel polynomial");
forward_coefficients = vector(half + 1);
for(i = 0, half,
  cK = polcoeff(hK, i);
  c0 = ffmap(inv, cK);
  must(c0 != [], Str("forward coefficient failed to descend: ", i));
  must(ffmap(emb, c0) == cK,
       Str("forward coefficient embedding mismatch: ", i));
  forward_coefficients[i + 1] = c0
);
h_forward = Polrev(forward_coefficients, 'X);
must(poldegree(h_forward) == half && pollead(h_forward) == 1, "bad descended forward kernel polynomial");
must(poldegree(gcd(h_forward, deriv(h_forward))) == 0, "forward kernel polynomial is not squarefree");
D73_source = elldivpol(E0, lp, 'X);
must(poldegree(D73_source) == (lp^2 - 1)/2, "wrong source 73-division-polynomial degree");
must(divrem(D73_source, h_forward)[2] == 0, "forward kernel polynomial does not divide source psi_73");
tcoef = polcoeff(h_forward, half - 1);
b1 = 1 + tcoef + tcoef^2;
must(toint(b1) == expected_endpoint_b, "deterministic forward endpoint replay mismatch");
must(normalized_image_b(E0, h_forward) == b1, "forward normalized codomain mismatch");
E1 = ellinit([1, 0, 0, 0, b1], g);
must(ellcard(E1) == N, "forward endpoint order mismatch");
forward_gate = 1;
forward_ms = getabstime() - t_forward;

\\ The floor has one Frobenius-stable upward 73-line.  Its nonzero
\\ x-coordinates are in F_(q^9), while the other division-polynomial factors
\\ are excluded by the exact gcd selector.
t_dual = getabstime();
D73 = elldivpol(E1, lp, 'X);
must(poldegree(D73) == (lp^2 - 1)/2, "wrong degree for the 73-division polynomial");
must(poldegree(gcd(D73, deriv(D73))) == 0, "endpoint 73-division polynomial is not squarefree");
zq9 = Mod('X, D73);
for(i = 1, m*9, zq9 = zq9^2);
h_dual = gcd(D73, lift(zq9) - 'X);
h_dual /= pollead(h_dual);
must(poldegree(h_dual) == half, "q^9 selector did not isolate one 73-kernel line");
must(pollead(h_dual) == 1, "dual kernel polynomial is not monic");
must(poldegree(gcd(h_dual, deriv(h_dual))) == 0, "dual kernel polynomial is not squarefree");
dual_division = divrem(D73, h_dual);
must(dual_division[2] == 0, "dual kernel polynomial does not divide psi_73");
tcoef_dual = polcoeff(h_dual, half - 1);
b0_back = b1 + tcoef_dual + tcoef_dual^2;
must(b0_back == 1, "dual Velu codomain is not the exact source model");
must(normalized_image_b(E1, h_dual) == 1, "dual normalized codomain mismatch");
dual_gate = 1;
dual_ms = getabstime() - t_dual;

\\ Freeze a prime-subgroup generator independently of the kernel RNG.
setrand(generator_seed);
G = [0];
generator_tries = 0;
while(G == [0],
  generator_tries++;
  must(generator_tries <= generator_max_tries,
       "generator search exhausted generator_max_tries");
  G = ellmul(E0, random(E0), cofactor_r)
);
must(ellisoncurve(E0, G), "source generator is off curve");
must(ellmul(E0, G, r) == [0], "source generator has wrong order");

phiG = velu_point(G, h_forward);
must(phiG != [0] && ellisoncurve(E1, phiG), "mapped generator is invalid");
must(ellmul(E1, phiG, r) == [0], "mapped generator has wrong order");

\\ Fix the dual's otherwise ambiguous sign on the prime subgroup.
raw_dual_phiG = velu_point(phiG, h_dual);
want_dual_phiG = ellmul(E0, G, lp);
if(raw_dual_phiG == want_dual_phiG,
  dual_sign = 1,
  if(ellneg(E0, raw_dual_phiG) == want_dual_phiG,
    dual_sign = -1,
    must(0, "neither sign of the candidate dual composes to [73] on G")
  )
);

must(velu_point([0], h_forward) == [0], "forward map does not preserve infinity");
must(dual_point([0]) == [0], "dual map does not preserve infinity");
must(dual_point(phiG) == want_dual_phiG, "signed dual orientation failed on generator");
must(velu_point(dual_point(phiG), h_forward) == ellmul(E1, phiG, lp), "right composition failed on generator");
generator_gate = 1;

degree_inverse_mod_r = lift(Mod(lp, r)^(-1));
target_scalars = vector(target_count, i, lift(Mod(target_offset + (i - 1)*target_stride, r)));
must(vecmin(target_scalars) > 0, "frozen target set contains zero");
must(#Set(target_scalars) == target_count, "frozen target scalars are not distinct");

\\ Exhaust the frozen 1,024-target set.  Each iteration independently checks
\\ the forward bridge, left composition, right composition, and inverse-degree
\\ recovery.  Any mismatch aborts before a receipt can be written.
t_targets = getabstime();
scalar_sum = 0;
scalar_sumsq = 0;
scalar_roll = 0;
target_passes = 0;
roll_modulus = 2^127 - 1;
for(i = 1, target_count,
  s = target_scalars[i];
  P0 = ellmul(E0, G, s);
  P1 = velu_point(P0, h_forward);
  expected_P1 = ellmul(E1, phiG, s);
  must(P0 != [0] && ellisoncurve(E0, P0),
       Str("invalid source target: ", i));
  must(P1 == expected_P1 && ellisoncurve(E1, P1),
       Str("forward bridge failed: ", i));
  back = dual_point(P1);
  must(back == ellmul(E0, P0, lp),
       Str("dual o forward composition failed: ", i));
  must(velu_point(dual_point(expected_P1), h_forward)
         == ellmul(E1, expected_P1, lp),
       Str("forward o dual composition failed: ", i));
  recovered = ellmul(E0, back, degree_inverse_mod_r);
  must(recovered == P0, Str("target recovery failed: ", i));
  scalar_sum += s;
  scalar_sumsq += s^2;
  scalar_roll = (scalar_roll*1000003 + s) % roll_modulus;
  target_passes++
);
must(target_passes == target_count, "frozen target loop did not complete");
target_gate = 1;
targets_ms = getabstime() - t_targets;

\\ A separate planted scalar checks the same bridge and recovery path.
planted_source = ellmul(E0, G, planted_scalar);
planted_endpoint = velu_point(planted_source, h_forward);
must(planted_endpoint == ellmul(E1, phiG, planted_scalar), "planted logarithm was not preserved");
planted_back = dual_point(planted_endpoint);
must(planted_back == ellmul(E0, planted_source, lp), "planted dual composition failed");
planted_recovered = ellmul(E0, planted_back, degree_inverse_mod_r);
must(planted_recovered == planted_source, "planted recovery failed");
must(velu_point(dual_point(planted_endpoint), h_forward) == ellmul(E1, planted_endpoint, lp), "planted right composition failed");
planted_gate = 1;

must(source_gate && forward_gate && dual_gate && generator_gate && target_gate && planted_gate, "not all fail-closed gates completed");

forward_coefficients_int = vector(half + 1, i, toint(forward_coefficients[i]));
dual_coefficients_int = vector(half + 1, i, toint(polcoeff(h_dual, i - 1)));
receipt = [
  SCHEMA,
  ["status", "PASS"],
  ["field_basis", "x^37+x^9+x^2+x+1"],
  ["m", m],
  ["ell", lp],
  ["source_b", 1],
  ["endpoint_b", toint(b1)],
  ["source_order", N],
  ["subgroup_order", r],
  ["formula", FORMULA],
  ["forward_seed", forward_seed],
  ["forward_max_tries", forward_max_tries],
  ["forward_tries", forward_tries],
  ["forward_kernel_degree", poldegree(h_forward)],
  ["forward_kernel_coefficients_low_to_high", forward_coefficients_int],
  ["dual_selector", "gcd(psi_73,X^(q^9)-X)"],
  ["dual_selector_relative_degree", 9],
  ["dual_kernel_degree", poldegree(h_dual)],
  ["dual_kernel_coefficients_low_to_high", dual_coefficients_int],
  ["dual_orientation_sign", dual_sign],
  ["degree_inverse_mod_subgroup", degree_inverse_mod_r],
  ["generator_seed", generator_seed],
  ["generator_max_tries", generator_max_tries],
  ["generator_tries", generator_tries],
  ["source_generator", [toint(G[1]), toint(G[2])]],
  ["endpoint_generator", [toint(phiG[1]), toint(phiG[2])]],
  ["target_count", target_count],
  ["target_scheme", "(offset+(i-1)*stride) mod r, i=1..1024"],
  ["target_offset", target_offset],
  ["target_stride", target_stride],
  ["target_first", target_scalars[1]],
  ["target_last", target_scalars[target_count]],
  ["target_scalar_sum", scalar_sum],
  ["target_scalar_sumsq", scalar_sumsq],
  ["target_scalar_rolling_digest", scalar_roll],
  ["forward_bridge_passes", target_passes],
  ["dual_o_forward_passes", target_passes],
  ["forward_o_dual_passes", target_passes],
  ["inverse_degree_recovery_passes", target_passes],
  ["planted_scalar", planted_scalar],
  ["planted_recovery", "PASS"],
  ["forward_construction_ms", forward_ms],
  ["dual_construction_ms", dual_ms],
  ["target_checks_ms", targets_ms]
];

if(write_receipt,
  write(out_path, receipt);
  print("ARTIFACT ", out_path)
);
print("MAP73_DUAL_CONTROL PASS endpoint_b=", toint(b1),
      " dual_sign=", dual_sign,
      " targets=", target_count,
      " planted=PASS");
}

{iferr(run_control(), run_error,
  print("MAP73_DUAL_CONTROL FAIL unexpected execution error: ", run_error);
  quit(1)
)}
