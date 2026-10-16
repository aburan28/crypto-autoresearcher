\\ Exact validator and endpoint-only 271-ascent for the m=51 deep scan.
\\
\\ Required driver variables:
\\   EMBED_SEED, WITNESS_COUNT, MAX_WITNESS_ATTEMPTS, BATCH_ROWS.
\\ Each row is [GLOBAL_INDEX, BINT, WITNESS_SEED, TARGET_WITNESS_SEED,
\\              CONTROL_MODE, CERT_OUT].
\\
\\ The output is an append-free key=value certificate parsed and sealed by
\\ pipeline.py.  A positive order-271^2 source witness, an F_q-stable kernel,
\\ and a positive rank-two target certificate establish the 271 ascent from
\\ f_E=271*120871 to f_E=120871; the complete f=271 census is corroborating.
\\ This constructs an endpoint up to the serialized target isomorphism data;
\\ it does not serialize a normalized point evaluator, dual, or transfer.

if(type(EMBED_SEED) != "t_INT", error("EMBED_SEED must be an integer"));
if(type(WITNESS_COUNT) != "t_INT" || WITNESS_COUNT < 1, error("WITNESS_COUNT must be positive"));
if(type(MAX_WITNESS_ATTEMPTS) != "t_INT" || MAX_WITNESS_ATTEMPTS < WITNESS_COUNT, error("MAX_WITNESS_ATTEMPTS is too small"));
if(type(BATCH_ROWS) != "t_VEC", error("BATCH_ROWS must be a vector"));
\\ pipeline.py supplies a freshly reserved empty path; GP 2.15 has no portable
\\ file-existence predicate of its own.  Mode 0 is scientific.  Modes 1 and 2
\\ are hard-bound replay controls and their statuses are never selectable.

emit(k, v) = write(CERT_OUT, Str(k, "=", v));
finish_status(s) = { emit("status", s); s };
benign(s) = { emit("admitted_failure", 0); finish_status(s); };
fatal(s) = { emit("admitted_failure", 1); finish_status(s); };

m = 51;
MOD = x^51 + x^6 + x^3 + x + 1;
q = 2^m;
N_EXPECTED = 2251799852369764;
F_PI = 32756041;
LP = 271;
KERNEL_K = 45;
TWIST = 1;
PILOT_BOTTOM_ORBIT = 99224513745505;
PILOT_PARENT_ORBIT = 7746411922983;
PILOT_BOTTOM_RAW_B = 675235026289400;
F271_CONTROL_B = 623162416261;
F271_CENSUS_SHA256 = "bb4b64d5e8d53b323cd7493af435c738198b90b0ba8696316bb36e8709150fbe";
F271_SOURCE_REVISION = "f0bdf9f739462766a9060532c59f9bfed69d00b1";
F271_SOURCE_SHA256 = "a73ef01d0cb78be9f1c3df131c5598eae394541ce85a55fab5b33efaeca8d91b";
F271_ORBITS = [623162416261, 25640824825979, 30885819784827, 57318330399736, 67694307705004, 72881269935803, 115635957935040, 116461223646592, 116511665573478, 121360481466206, 130246110195364, 147686731444433, 213718369432541, 237711860122495, 360860333097189, 370376419722289];

if(!polisirreducible(Mod(1, 2) * MOD), error("field modulus is reducible"));
if(kronecker(-7, LP) != -1, error("271 must be inert in Q(sqrt(-7))"));
T_BASE = q + 1 - N_EXPECTED;
DISC_PI = T_BASE^2 - 4*q;
if(DISC_PI != -7*F_PI^2, error("class discriminant identity failed"));
if(F_PI != LP*120871 || !isprime(LP) || !isprime(120871), error("conductor factorization failed"));
if(gcd(LP, 120871) != 1, error("conductor factors are not coprime"));
if(valuation(DISC_PI, LP) != 2, error("class discriminant has wrong 271 valuation"));
if(gcd(KERNEL_K, LP) != 1, error("kernel extension degree is not coprime to 271"));
if((m*KERNEL_K) % 2 != 1, error("kernel field degree must be odd"));
if(qfbclassno(-7) != 1, error("maximal order class number is not one"));

g = ffgen(Mod(1, 2) * MOD, 'g);
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
tointK(z) = subst(lift(z.pol), variable(z.pol), 2);

{orbit_meta(n) = my(z = fromint(n), c = z, best = n, best_i = 0, d = 0);
  while(1, d++; c = c^2; if(c == z, break);
    my(ci = toint(c)); if(ci < best, best = ci; best_i = d));
  [best, d, best_i]}

mu = -1;
trk(kk) = my(P = lift(Mod(x, x^2 - mu*x + 2)^(m*kk))); 2*polcoeff(P, 0) + mu*polcoeff(P, 1);

K = ffgen(ffinit(2, m*KERNEL_K), 'h);
{emb_x() = my(e = (2^(m*KERNEL_K)-1)/(2^m-1), w = 0, cj, c,
                   mp, attempts = 0);
  setrand(EMBED_SEED);
  while(attempts < 4096,
    attempts++;
    w = random(K)^e;
    cj = vector(m); c = w;
    for(i = 1, m, cj[i] = c; c = c^2);
    if(c != w, error("embedding candidate not in subfield"));
    if(#Set(cj) == m, break));
  if(attempts >= 4096 && #Set(cj) != m, return([0, attempts]));
  mp = Pol(apply(z -> if(z == 0, 0,
                         if(z == 1, 1, error("embedding minpoly not binary"))),
                 Vec(lift(prod(i = 1, m, 'X - cj[i])))), 'X);
  my(S = ffgen(Mod(1, 2) * subst(mp, 'X, 't), 't),
     FF = factor(subst(MOD, x, 'Y) * S^0)[, 1], r = 0);
  for(i = 1, #FF, if(poldegree(FF[i]) == 1,
    r = -polcoeff(FF[i], 0) / polcoeff(FF[i], 1); break));
  if(r == 0, error("no root of base modulus in generated subfield"));
  my(Rp = lift(r.pol), X = subst(Rp*K^0, variable(Rp), w));
  if(subst(MOD, x, X) != 0, error("embedding does not satisfy modulus"));
  [X, attempts]}

embedding = emb_x();
if(embedding[1] != 0, Xk = embedding[1]);
embed(n) = my(s = 0*K, p = K^0); while(n, if(n % 2, s += p); n \= 2; p *= Xk); s;

xdbl(R) = my(X2 = R[1]^2, Z2 = R[2]^2); [X2^2 + BK*Z2^2, X2*Z2];
{xadd(R, S, xD) = my(Aa = R[1]*S[2], Bb = S[1]*R[2],
                      Z = (Aa+Bb)^2); [xD*Z + Aa*Bb, Z]}
{ladder(x0, n) = my(R0 = [x0, x0^0], R1 = xdbl(R0));
  forstep(i = #binary(n)-2, 0, -1,
    if(bittest(n, i),
      R0 = xadd(R0, R1, x0); R1 = xdbl(R1),
      R1 = xadd(R0, R1, x0); R0 = xdbl(R0)));
  R0}

tt = trk(KERNEL_K);
if(trk(1) != T_BASE, error("trace recurrence disagrees at base field"));
tr_prev = 2; tr_now = T_BASE;
for(i = 2, KERNEL_K, tr_next = T_BASE*tr_now-q*tr_prev; tr_prev=tr_now; tr_now=tr_next);
if(tr_now != tt, error("trace recurrence disagrees at kernel field"));
G = if(TWIST, q^KERNEL_K + 1 + tt, q^KERNEL_K + 1 - tt);
G_OTHER = if(TWIST, q^KERNEL_K + 1 - tt, q^KERNEL_K + 1 + tt);
v_lp = valuation(G, LP);
if(v_lp != 2, error("unexpected 271-adic extension-group valuation"));
if(valuation(G_OTHER, LP) != 0, error("other twist unexpectedly has 271-torsion"));
cofactor = G / LP^v_lp;

{kernel_sum(xq) = my(n = (LP-1)/2, sm = xq,
                           Rm = [xq, xq^0], R = xdbl([xq, xq^0]));
  if(R[2] == 0, error("order-271 kernel doubled to infinity too early"));
  sm += R[1]/R[2];
  for(i = 3, n,
    my(S = xadd(R, [xq, xq^0], Rm[1]/Rm[2]));
    if(S[2] == 0, error("kernel enumeration reached infinity early"));
    Rm = R; R = S; sm += R[1]/R[2]);
  sm}

{cyclic_x_set(xq) = my(n = (LP-1)/2, xs = List([tointK(xq)]),
                          Rm = [xq, xq^0], R = xdbl([xq, xq^0]));
  if(R[2] == 0, error("order-271 point doubled to infinity too early"));
  listput(xs, tointK(R[1]/R[2]));
  for(i = 3, n,
    my(S = xadd(R, [xq, xq^0], Rm[1]/Rm[2]));
    if(S[2] == 0, error("order-271 enumeration reached infinity early"));
    Rm = R; R = S; listput(xs, tointK(R[1]/R[2])));
  Set(Vec(xs))}

{frobenius_kernel_multiplier(xq) = my(want = xq^q, Rm, R, S);
  if(want == xq, return(1));
  Rm = [xq, xq^0]; R = xdbl(Rm);
  if(R[2] != 0 && R[1]/R[2] == want, return(2));
  for(i = 3, (LP-1)/2,
    S = xadd(R, [xq, xq^0], Rm[1]/Rm[2]);
    if(S[2] == 0, error("kernel Frobenius enumeration reached infinity"));
    Rm = R; R = S;
    if(R[1]/R[2] == want, return(i)));
  0}

{rank2_certificate(seed) = my(p1 = 0, p1set = 0, p2 = 0, attempts = 0,
                                other = 0, infinity = 0, raw_x, R, xr, T1, T2);
  setrand(seed);
  while(p2 == 0 && attempts < MAX_WITNESS_ATTEMPTS,
    attempts++;
    raw_x = random(K); R = ladder(raw_x, cofactor);
    if(R[2] == 0, infinity++; next);
    xr = R[1]/R[2]; T1 = ladder(xr, LP);
    if(T1[2] == 0,
      if(p1 == 0,
        p1 = xr; p1set = cyclic_x_set(p1),
        if(!setsearch(p1set, tointK(xr)), p2 = xr));
      next);
    T2 = ladder(xr, LP^2);
    if(T2[2] == 0, return([-1, attempts, other, infinity, xr, 0, 0]));
    other++);
  if(p2 == 0, return([0, attempts, other, infinity, p1, 0, p1set]));
  if(#p1set != (LP-1)/2, return([-2, attempts, other, infinity, p1, p2, p1set]));
  [1, attempts, other, infinity, p1, p2, p1set]}

{classify_one() =
if(type(GLOBAL_INDEX) != "t_INT", error("GLOBAL_INDEX must be an integer"));
if(type(BINT) != "t_INT" || BINT <= 0 || BINT >= q, error("BINT outside nonzero base-field range"));
if(type(WITNESS_SEED) != "t_INT", error("WITNESS_SEED must be an integer"));
if(type(TARGET_WITNESS_SEED) != "t_INT", error("TARGET_WITNESS_SEED must be an integer"));
if(type(CONTROL_MODE) != "t_INT" || CONTROL_MODE < 0 || CONTROL_MODE > 2, error("CONTROL_MODE must be 0, 1, or 2"));
if(type(CERT_OUT) != "t_STR", error("CERT_OUT must be a path string"));

source_orbit = orbit_meta(BINT);
source_curve = ellinit([1, 0, 0, 0, fromint(BINT)], g);
source_order = ellcard(source_curve);

emit("schema", "m51-deep-endpoint-certificate/v1");
emit("global_index", GLOBAL_INDEX);
emit("source_b", BINT);
emit("source_a2", 0);
emit("source_order", source_order);
emit("expected_order", N_EXPECTED);
emit("source_orbit_rep", source_orbit[1]);
emit("source_orbit_size", source_orbit[2]);
emit("source_to_orbit_rep_frobenius_power", source_orbit[3]);
emit("field_degree", m);
emit("field_modulus_bits", 2^51 + 2^6 + 2^3 + 2 + 1);
emit("class_trace", T_BASE);
emit("class_discriminant", DISC_PI);
emit("f_pi", F_PI);
emit("f_pi_factorization", "271*120871");
emit("f_pi_factor_primality", 1);
emit("class_discriminant_271_valuation", valuation(DISC_PI, LP));
emit("kernel_extension_coprime_to_271", gcd(KERNEL_K, LP) == 1);
emit("maximal_order_class_number", qfbclassno(-7));
emit("f271_census_sha256", F271_CENSUS_SHA256);
emit("f271_census_source_revision", F271_SOURCE_REVISION);
emit("f271_census_source_sha256", F271_SOURCE_SHA256);
emit("f271_census_complete_orbit_count", #F271_ORBITS);
emit("control_mode", CONTROL_MODE);

if(CONTROL_MODE == 1 && (BINT != PILOT_BOTTOM_RAW_B || source_orbit[1] != PILOT_BOTTOM_ORBIT), error("mode-1 control is not the frozen pilot bottom"));
if(CONTROL_MODE == 2 && (BINT != F271_CONTROL_B || source_orbit[1] != F271_CONTROL_B), error("mode-2 control is not m51-floor-o01"));

if(source_order != N_EXPECTED, return(benign("SIEVE_FALSE_POSITIVE_ORDER")));
if(source_orbit[1] == 1, return(benign("KNOWN_CRATER")));
if(setsearch(Set(F271_ORBITS), source_orbit[1]) && CONTROL_MODE != 2, return(benign("KNOWN_F271")));
if(source_orbit[1] == PILOT_BOTTOM_ORBIT && CONTROL_MODE != 1,
  emit("pilot_exclusion_scope", "source-orbit"); return(benign("EXCLUDED_PILOT_ORBIT")));
if(CONTROL_MODE == 2,
  if(source_orbit[2] != 17, return(fatal("WRONG_ORBIT_SIZE"))),
  if(source_orbit[2] != 51, return(fatal("WRONG_ORBIT_SIZE"))));
if(embedding[1] == 0,
  emit("embedding_attempts", embedding[2]); return(fatal("UNKNOWN_EMBEDDING_EXHAUSTED")));

BK = embed(BINT);
if(BK^(2^m) != BK, error("embedded coefficient is not base-field fixed"));
emit("kernel_prime", LP);
emit("kernel_field_degree", m*KERNEL_K);
emit("kernel_extension_degree", KERNEL_K);
emit("kernel_twist", TWIST);
emit("extension_trace", tt);
emit("extension_group_271_valuation", v_lp);
emit("other_twist_271_valuation", valuation(G_OTHER, LP));
emit("extension_group_cofactor", cofactor);
emit("extension_modulus_bits", subst(lift(K.mod), variable(lift(K.mod)), 2));
emit("embedding_seed", EMBED_SEED);
emit("embedding_attempts", embedding[2]);
emit("embedding_x_int", tointK(Xk));
emit("embedding_modulus_check", 1);
emit("embedded_b_int", tointK(BK));
emit("witness_seed", WITNESS_SEED);
emit("target_witness_seed", TARGET_WITNESS_SEED);
emit("witness_count_required", WITNESS_COUNT);
emit("witness_attempt_cap", MAX_WITNESS_ATTEMPTS);

setrand(WITNESS_SEED);
witnesses = List(); rank1_x = 0; rank1_set = 0; rank2_x = 0; attempt = 0; other_twist_skips = 0; infinity_skips = 0;
while(#witnesses < WITNESS_COUNT && rank2_x == 0 && attempt < MAX_WITNESS_ATTEMPTS,
  attempt++;
  my(raw_x = random(K), R = ladder(raw_x, cofactor));
  if(R[2] == 0, infinity_skips++; next);
  my(x2712 = R[1]/R[2], T1 = ladder(x2712, LP));
  if(T1[2] == 0,
    if(rank1_x == 0,
      rank1_x = x2712; rank1_set = cyclic_x_set(rank1_x),
      if(!setsearch(rank1_set, tointK(x2712)), rank2_x = x2712));
    next);
  my(T2 = ladder(x2712, LP^2));
  if(T2[2] != 0, other_twist_skips++; next);
  my(x271 = T1[1]/T1[2], T3 = ladder(x271, LP));
  if(T3[2] != 0, error("derived kernel point is not killed by 271"));
  listput(witnesses, [attempt, raw_x, x2712, x271, kernel_sum(x271)]));

emit("witness_attempts_used", attempt);
emit("witness_count_found", #witnesses);
emit("witness_other_twist_skips", other_twist_skips);
emit("witness_infinity_skips", infinity_skips);
if(rank2_x != 0 && #witnesses, return(fatal("INVALID_CERTIFICATE")));
if(rank2_x != 0,
  if(#rank1_set != (LP-1)/2, return(fatal("INVALID_CERTIFICATE")));
  emit("direct_parent_point_1_x_int", tointK(rank1_x));
  emit("direct_parent_point_2_x_int", tointK(rank2_x));
  emit("direct_parent_point_1_xset_count", #rank1_set);
  emit("direct_parent_point_1_xset", Vec(rank1_set));
  emit("direct_parent_point_2_absent_from_point_1_subgroup", 1);
  emit("source_f_E", 120871);
  emit("source_conductor_derivation", "two-independent-order271-x-points-full-rank");
  return(benign("DIRECT_PARENT")));
if(#witnesses < WITNESS_COUNT, return(fatal("UNKNOWN_WITNESS_EXHAUSTED")));

for(i = 1, #witnesses,
  emit(Str("witness_", i, "_attempt"), witnesses[i][1]);
  emit(Str("witness_", i, "_raw_x_int"), tointK(witnesses[i][2]));
  emit(Str("witness_", i, "_order_2712_x_int"), tointK(witnesses[i][3]));
  emit(Str("witness_", i, "_order_271_x_int"), tointK(witnesses[i][4]));
  emit(Str("witness_", i, "_mul_271_nonzero"), 1);
  emit(Str("witness_", i, "_mul_2712_zero"), 1));

kernel_x = witnesses[1][4];
velu_sum = witnesses[1][5];
for(i = 2, #witnesses, if(witnesses[i][5] != velu_sum, return(fatal("INVALID_CERTIFICATE"))));
kernel_frobenius_u = frobenius_kernel_multiplier(kernel_x);
if(kernel_frobenius_u == 0, return(fatal("ASCENT_FAILED")));
if(velu_sum^q != velu_sum, return(fatal("ASCENT_FAILED")));

\\ Characteristic-two Velu quotient [1,0,0,v,B+v], v=velu_sum. Translating
\\ y -> y+v normalizes it to [1,0,0,0,B+v+v^2]. Only this endpoint invariant,
\\ the kernel generator, and its replay data are retained; no point map/dual.
raw_delta = BK + velu_sum + velu_sum^2;
if(raw_delta == 0, return(fatal("ASCENT_FAILED")));
if(raw_delta^(2^m) != raw_delta, return(fatal("ASCENT_FAILED")));

cj = List([raw_delta]);
c = raw_delta^2;
while(c != raw_delta && #cj <= m, listput(cj, c); c = c^2);
if(c != raw_delta || m % #cj, return(fatal("ASCENT_FAILED")));
target_orbit_size_ext = #cj;
mp_raw = lift(prod(i = 1, #cj, 'X - cj[i]));
mp = Pol(apply(z -> if(z == 0, 0, if(z == 1, 1, error("codomain minpoly not binary"))), Vec(mp_raw)), 'X);
FF = factor(mp * g^0)[, 1];
roots = apply(f -> -polcoeff(f, 0)/polcoeff(f, 1), select(f -> poldegree(f) == 1, FF~));
if(#roots != poldegree(mp), return(fatal("ASCENT_FAILED")));

raw_target_b = -1;
for(i = 1, #roots,
  my(bi = toint(roots[i]));
  if(embed(bi) == raw_delta, raw_target_b = bi; break));
if(raw_target_b < 0, return(fatal("ASCENT_FAILED")));

target_b = vecmin(apply(toint, roots));
target_a2 = -1;
target_model_count = 0;
for(aa = 0, 1,
  if(ellcard(ellinit([1, aa, 0, 0, fromint(target_b)], g)) == N_EXPECTED,
    target_a2 = aa; target_model_count++));
if(target_model_count != 1, return(fatal("WRONG_PARENT_ORDER")));
if(target_a2 != 0, return(fatal("WRONG_PARENT_ORDER")));
target_order = ellcard(ellinit([1, target_a2, 0, 0, fromint(target_b)], g));
target_orbit = orbit_meta(raw_target_b);
if(target_orbit[1] != target_b, return(fatal("INVALID_CERTIFICATE")));

source_BK = BK;
BK = embed(raw_target_b);
target_rank2 = rank2_certificate(TARGET_WITNESS_SEED);
BK = source_BK;
if(target_rank2[1] == 0, return(fatal("TARGET_RANK2_WITNESS_EXHAUSTED")));
if(target_rank2[1] != 1, return(fatal("INVALID_CERTIFICATE")));

source_f_E = if(CONTROL_MODE == 2, 271, F_PI);
target_f_E = if(CONTROL_MODE == 2, 1, 120871);
emit("source_f_E", source_f_E);
emit("source_conductor_derivation", if(CONTROL_MODE == 2, "control-order2712-witness-plus-frozen-source-binding", "exact-order2712-source-plus-Fq-stable-271-kernel-plus-certified-f120871-target"));
emit("f271_census_exclusion_role", if(CONTROL_MODE == 2, "control-source-binding", "corroborating-not-load-bearing"));
emit("kernel_x_int", tointK(kernel_x));
emit("kernel_mul_271_zero", 1);
emit("kernel_frobenius_x_multiplier_abs", kernel_frobenius_u);
emit("kernel_frobenius_stable", 1);
emit("kernel_sums_agree", 1);
emit("velu_half_kernel_sum_int", tointK(velu_sum));
emit("velu_half_kernel_sum_frobenius_fixed", 1);
emit("raw_codomain_a1", 1);
emit("raw_codomain_a2", 0);
emit("raw_codomain_a3", 0);
emit("raw_codomain_a4_int", tointK(velu_sum));
emit("raw_codomain_a6_int", tointK(BK + velu_sum));
emit("normalization_y_translation_int", tointK(velu_sum));
emit("raw_codomain_delta_int", tointK(raw_delta));
emit("raw_codomain_delta_nonzero", 1);
emit("raw_codomain_frobenius_fixed", 1);
emit("raw_target_b", raw_target_b);
emit("codomain_minpoly_bits", subst(mp, variable(mp), 2));
emit("target_b", target_b);
emit("target_a2", target_a2);
emit("target_order", target_order);
emit("target_orbit_rep", target_orbit[1]);
emit("target_orbit_size", target_orbit[2]);
emit("raw_target_to_rep_frobenius_power", target_orbit[3]);
emit("target_f_E", target_f_E);
emit("target_rank2_attempts_used", target_rank2[2]);
emit("target_rank2_other_twist_skips", target_rank2[3]);
emit("target_rank2_infinity_skips", target_rank2[4]);
emit("target_rank2_point_1_x_int", tointK(target_rank2[5]));
emit("target_rank2_point_2_x_int", tointK(target_rank2[6]));
emit("target_rank2_point_1_mul_271_zero", 1);
emit("target_rank2_point_2_mul_271_zero", 1);
emit("target_rank2_point_1_xset_count", #target_rank2[7]);
emit("target_rank2_point_1_xset", Vec(target_rank2[7]));
emit("target_rank2_point_2_absent_from_point_1_subgroup", 1);
emit("target_conductor_derivation", if(CONTROL_MODE == 2, "complete-crater-binding-plus-independent-271-torsion", "crater-exclusion-plus-independent-271-torsion"));
emit("coprime_conductor_component_preserved", 120871);
emit("coprime_conductor_preservation_check", gcd(LP, 120871) == 1);
emit("edge_degree", LP);
emit("edge_separable", 1);
emit("edge_direction", "ascending");
emit("edge_direction_derivation", "depth-one-271-volcano-inert-prime-unique-order271-subgroup");
emit("map_evaluator_serialized", 0);
emit("dual_serialized", 0);
emit("transfer_claim_permitted", 0);

if(target_order != N_EXPECTED, return(fatal("WRONG_PARENT_ORDER")));
if(CONTROL_MODE == 2,
  if(target_orbit_size_ext != 1 || target_orbit[2] != 1, return(fatal("WRONG_ORBIT_SIZE"))),
  if(target_orbit_size_ext != 51 || target_orbit[2] != 51, return(fatal("WRONG_ORBIT_SIZE"))));
if(CONTROL_MODE == 2,
  if(target_orbit[1] != 1 || target_f_E != 1, return(fatal("INVALID_CERTIFICATE")));
  return(benign("POSITIVE_CONTROL_F271_TO_CRATER")));
if(target_orbit[1] == PILOT_PARENT_ORBIT,
  emit("pilot_exclusion_scope", "entire-parent-fiber");
  if(CONTROL_MODE == 1, return(benign("POSITIVE_CONTROL_BOTTOM_PARENT")), return(benign("EXCLUDED_PILOT_ORBIT"))));
if(CONTROL_MODE != 0, return(fatal("INVALID_CERTIFICATE")));

emit("admitted_failure", 0);
finish_status("CERTIFIED_BOTTOM_PARENT")}

{run_batch() = my(ii, row);
  for(ii = 1, #BATCH_ROWS,
    row = BATCH_ROWS[ii];
    if(type(row) != "t_VEC" || #row != 6, error("malformed batch row"));
    GLOBAL_INDEX = row[1];
    BINT = row[2];
    WITNESS_SEED = row[3];
    TARGET_WITNESS_SEED = row[4];
    CONTROL_MODE = row[5];
    CERT_OUT = row[6];
    iferr(classify_one(), batch_error, 0));}
run_batch();
