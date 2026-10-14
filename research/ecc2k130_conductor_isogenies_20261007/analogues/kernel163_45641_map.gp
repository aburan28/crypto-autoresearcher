\\ Construct one replayable degree-45641 K-163 kernel polynomial over the
\\ standard NIST base field, then exercise the complete normalized
\\ characteristic-2 Velu point evaluator on the standard prime subgroup.
\\
\\ This is the forward-map gate only.  It does not construct the algebraic
\\ dual; see MAP163_45641_PROTOCOL.md.  Run from this directory with OUT set
\\ by run163_45641_map.gp.  The driver must resize the PARI stack before
\\ read() enters this file: resizing it here makes GP abandon the rest of
\\ this included file and return success without constructing an artifact.

if(type(OUT) != "t_STR", error("OUT must be set by the driver"));
out_exists = 1;
iferr(readstr(OUT), E, out_exists = 0);
if(out_exists, error(Str("refusing to append to existing ", OUT)));

SCHEMA = "k163-degree45641-forward-map-v1";
MOD = x^163 + x^7 + x^6 + x^3 + 1;
m = 163;
a2 = 1;
lp = 45641;
k = 20;
seed = 45641;
hom_samples = 16;
planted = 0x123456789abcdef0123456789abcdef;
r = 0x4000000000000000000020108A2E0CC0D99F8A5EF;
gx_int = 0x02fe13c0537bbc11acaa07d793de4e6d5e5c94eee8;
gy_int = 0x0289070fb05d38ff58321f2e800536d538ccdaa3d9;
archived_orbit_minima = Set([20183018253319052689704116247546275258431720285, 1699056145793825809974781818934579013935268431, 71177121262957429327531167482112665894165601519, 86418753047285346854356540661746105839786105877, 41105051057298702718687969060611106606052833369, 9458681452661928675008670406069307198816595651]);

g = ffgen(Mod(1, 2) * MOD, 'g);
q = 2^m;
E = ellinit([1, a2, 0, 0, 1], g);
N = ellcard(E);
if(N != 2*r, error("standard K-163 order mismatch"));
if(!isprime(r), error("standard K-163 subgroup order is not prime"));
if(!polisirreducible(Mod(1, 2) * MOD), error("NIST field modulus is reducible"));
if(!isprime(lp) || gcd(lp, r) != 1, error("bad isogeny degree"));

toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, j = 0); while(n, if(n % 2, s += g^j); n \= 2; j++); s;
orbmin(z) = my(c = z^2, mn = toint(z)); while(c != z, mn = min(mn, toint(c)); c = c^2); mn;
canon_index(j) = my(u = j % lp); if(u < 0, u += lp); min(u, lp-u);

G0 = [fromint(gx_int), fromint(gy_int)];
if(!ellisoncurve(E, G0), error("standard generator is off curve"));
if(ellmul(E, G0, r) != [0], error("standard generator fails subgroup check"));
if(planted <= 0 || planted >= r, error("planted scalar outside subgroup"));

\\ q-Frobenius is scalar c on E[lp].  Derive c from either root of the
\\ absolute-Frobenius polynomial T^2-T+2 and fail unless both roots agree
\\ after the m-th power.
tau_roots = polrootsmod('T^2 - 'T + 2, lp);
if(#tau_roots != 2, error("tau polynomial did not split modulo lp"));
c1 = lift(tau_roots[1]^m);
c2 = lift(tau_roots[2]^m);
if(c1 != c2, error("q-Frobenius is not scalar modulo lp"));
c = c1;
if(znorder(Mod(c, lp)) != 2*k, error("unexpected Frobenius order"));
if(lift(Mod(c, lp)^k) != lp-1, error("kernel x-field is not the frozen twist field"));

\\ Kernel x-coordinate witness in F_(2^(163*20)).  The full kernel points
\\ live over twice that relative degree; x-only Lopez-Dahab arithmetic keeps
\\ this construction in the smaller field.
t0 = getabstime();
K = ffgen(ffinit(2, m*k), 'z);
emb = ffembed(g, K);
inv = ffinvmap(emb);
mu = 1;
trk(kk) = my(P = lift(Mod(x, x^2 - mu*x + 2)^(m*kk))); 2*polcoeff(P, 0) + mu*polcoeff(P, 1);
xdbl(R) = my(X2 = R[1]^2, Z2 = R[2]^2); [X2^2 + Z2^2, X2*Z2];
xadd(R, S, xD) = my(A = R[1]*S[2], B = S[1]*R[2], Z = (A+B)^2); [xD*Z + A*B, Z];
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
}

ext_order = q^k + 1 + trk(k);
v_lp = valuation(ext_order, lp);
if(v_lp != 2, error("unexpected lp-adic valuation in twist order"));
cofactor = ext_order / lp^v_lp;
setrand(seed);
xq = 0;
tries = 0;
{
while(!xq,
  tries++;
  x0 = random(K);
  R0 = ladder(x0, cofactor);
  if(R0[2] == 0, next);
  xr = R0[1]/R0[2];
  for(s = 1, v_lp,
    T0 = ladder(xr, lp);
    if(T0[2] == 0, xq = xr; break);
    xr = T0[1]/T0[2]
  )
);
}
if(ladder(xq, lp)[2] != 0, error("kernel witness does not have order lp"));
print("KERNEL_WITNESS tries=", tries, " field_seconds=", (getabstime()-t0)\1000);

\\ Enumerate each x([i]Q), 1 <= i <= (lp-1)/2, once.
t1 = getabstime();
half = (lp-1)/2;
xs = vector(half);
xs[1] = xq;
Rm = [xq, xq^0];
R1 = xdbl(Rm);
xs[2] = R1[1]/R1[2];
{
for(i = 3, half,
  S0 = xadd(R1, [xq, xq^0], Rm[1]/Rm[2]);
  Rm = R1;
  R1 = S0;
  xs[i] = R1[1]/R1[2]
);
}
if(#Set(xs) != half, error("half-kernel abscissae are not distinct"));
print("KERNEL_XS count=", half, " seconds=", (getabstime()-t1)\1000);

\\ Split the half-kernel into q-Frobenius orbits of length k.  Descend each
\\ degree-k orbit polynomial separately, then multiply in the 163-bit base
\\ field.  This avoids materialising a degree-22820 polynomial over the
\\ 3260-bit extension.
{product_tree(V) =
  my(L = V, n);
  if(#L == 0, return(1));
  while(#L > 1,
    n = (#L + 1) \ 2;
    L = vector(n, j, if(2*j <= #L, L[2*j-1] * L[2*j], L[2*j-1]))
  );
  L[1]
}

t2 = getabstime();
seen = vector(half);
orbit_factors = List();
{
for(i = 1, half,
  if(seen[i], next);
  inds = vector(k);
  u = i;
  for(j = 1, k,
    idx = canon_index(u);
    if(idx == 0 || seen[idx], error("Frobenius orbit collision"));
    inds[j] = idx;
    seen[idx] = 1;
    u = lift(Mod(u, lp) * Mod(c, lp))
  );
  if(canon_index(u) != i, error("Frobenius orbit did not close"));
  fK = prod(j = 1, k, 'X + xs[inds[j]]);
  coeffs = vector(k+1);
  for(j = 0, k,
    coeffs[j+1] = ffmap(inv, polcoeff(fK, j));
    if(coeffs[j+1] == [], error("orbit coefficient did not descend"));
    if(ffmap(emb, coeffs[j+1]) != polcoeff(fK, j), error("embedding round trip failed"))
  );
  listput(orbit_factors, Polrev(coeffs, 'X))
);
}
if(vecsum(seen) != half, error("incomplete half-kernel coverage"));
if(#orbit_factors != half/k, error("wrong number of Frobenius factors"));
h = product_tree(Vec(orbit_factors));
if(poldegree(h) != half || pollead(h) != 1, error("bad kernel polynomial"));
{
print("KERNEL_POLY degree=", poldegree(h), " orbit_factors=", #orbit_factors,
      " seconds=", (getabstime()-t2)\1000);
}

\\ Normalized characteristic-2 Velu map.  h^{[j]} denotes the j-th Hasse
\\ derivative.  The formulas are independently exercised by the native Rust
\\ degree-73 control before this full-size run is admitted.
{hasse_eval(H, j, xx) =
  my(acc = 0*g, d = poldegree(H));
  forstep(i = d, j, -1,
    acc *= xx;
    if(bitand(i, j) == j, acc += polcoeff(H, i))
  );
  acc
}

hp = deriv(h);
{velu_point(P) =
  if(P == [0], return([0]));
  my(xx = P[1], yy = P[2], hv = subst(h, 'X, P[1]));
  if(hv == 0, return([0]));
  my(hinv = 1/hv, L = subst(hp, 'X, xx)*hinv,
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
}

tcoef = polcoeff(h, half-1);
b_endpoint = 1 + tcoef + tcoef^2;
endpoint_orbit_min = orbmin(b_endpoint);
{
if(!setsearch(archived_orbit_minima, endpoint_orbit_min),
  error("endpoint does not match an archived conductor-45641 orbit"));
}
E1 = ellinit([1, a2, 0, 0, b_endpoint], g);
if(ellcard(E1) != N, error("endpoint point count mismatch"));

t3 = getabstime();
phiG = velu_point(G0);
if(phiG == [0] || !ellisoncurve(E1, phiG), error("mapped generator invalid"));
if(ellmul(E1, phiG, r) != [0], error("mapped generator failed subgroup check"));
Q0 = ellmul(E, G0, planted);
phiQ = velu_point(Q0);
if(phiQ != ellmul(E1, phiG, planted), error("planted logarithm was not preserved"));
setrand(seed + 1);
{
for(i = 1, hom_samples,
  u = random(r-1) + 1;
  v = random(r-1) + 1;
  P0 = ellmul(E, G0, u);
  Q1 = ellmul(E, G0, v);
  if(velu_point(elladd(E, P0, Q1)) != elladd(E1, velu_point(P0), velu_point(Q1)),
    error(Str("homomorphism sample failed: ", i)))
);
}
{
print("FORWARD_MAP endpoint_orbit_min=", endpoint_orbit_min,
      " subgroup=PASS planted=PASS hom_samples=", hom_samples,
      " map_seconds=", (getabstime()-t3)\1000);
}

kernel_coefficients = vector(half+1, i, toint(polcoeff(h, i-1)));
{
receipt = [
  SCHEMA,
  ["m", m],
  ["ell", lp],
  ["relative_kernel_x_degree", k],
  ["kernel_polynomial_degree", half],
  ["seed", seed],
  ["tries", tries],
  ["frobenius_scalar", c],
  ["source_order", N],
  ["subgroup_order", r],
  ["source_generator", [gx_int, gy_int]],
  ["endpoint_b", toint(b_endpoint)],
  ["endpoint_orbit_min", endpoint_orbit_min],
  ["image_generator", [toint(phiG[1]), toint(phiG[2])]],
  ["planted_scalar", planted],
  ["homomorphism_samples", hom_samples],
  ["kernel_coefficients_low_to_high", kernel_coefficients]
];
}
write(OUT, receipt);
print("ARTIFACT ", OUT, " coefficients=", #kernel_coefficients);
