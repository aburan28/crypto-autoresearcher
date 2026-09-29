\\ =============================================================================
\\ build_lattices.gp -- EXP-SSIQ-6916e8 (frozen spec v1), task TASK-20260926-7d20e4
\\
\\ PARI/GP side of the determinant check. Pure quaternion-lattice arithmetic in
\\ B_{p,inf} = (a, b)_Q; no curve, isogeny or key is constructed (C-4).
\\
\\ Coordinates: every element is a column vector in PARI "basis form", i.e.
\\ coordinates w.r.t. the Z-basis e_1..e_4 of the maximal order O_0 stored by
\\ alginit (algbasis(al)). Every lattice is exported as the list of its basis
\\ vectors (columns) in these O_0-coordinates, as exact rational strings.
\\
\\ Instruments on this side: algnorm (reduced norm, checked by C-ALG (b)),
\\ algtrace (reduced trace), algmul, matdet over Q, mathnf, matkermod,
\\ matkerint, setrand/random (A4 only). The driver re-derives every Gram
\\ entry with an independent Python instrument (left-regular representation
\\ built from the structure constants exported here) and every determinant
\\ with Python Fraction elimination (C-CROSS).
\\
\\ Output: one line per stage prefixed with "@@JSON " followed by a JSON
\\ object. Nothing else on stdout is parsed.
\\ =============================================================================

\\ ---------------------------------------------------------------- JSON helpers
jq(s) = Str("\"", s, "\"");
jr(x) = jq(Str(x));                               \\ exact rational as a string
jb(x) = if(x, "true", "false");
jlist(L) = Str("[", strjoin(L, ","), "]");
jv(v) = jlist(apply(jr, Vec(v)));
jrows(M) = jlist(vector(matsize(M)[1], i, jv(M[i,])));  \\ matrix as list of rows
jcols(M) = jlist(vector(matsize(M)[2], j, jv(M[,j])));  \\ matrix as list of columns
jkv(k, v) = Str(jq(k), ":", v);
jobj(L) = Str("{", strjoin(L, ","), "}");
strclean(s) = {
  my(v = Vecsmall(s), w = List());
  for(i = 1, #v, if(v[i] >= 32 && v[i] != 34 && v[i] != 92, listput(w, v[i])));
  Strchr(Vec(w));
}
emit(L) = print("@@JSON ", jobj(L));

\\ ------------------------------------------------------------ algebra helpers
ALGINIT_SEED = 1;   \\ PARI RNG state set immediately before every alginit call
unitv(i) = matid(4)[, i];
one_of(al) = algalgtobasis(al, [1, 0]~);
conjq(al, v) = algtrace(al, v) * one_of(al) - v;

\\ Gram matrix of the reduced norm on the columns of M (convention:
\\ A_ii = q(e_i), A_ij = (q(e_i+e_j) - q(e_i) - q(e_j))/2), via algnorm.
gram_nrd(al, M) = {
  my(n = matsize(M)[2], A = matrix(n, n), q = vector(n, i, algnorm(al, M[, i])));
  for(i = 1, n,
    A[i, i] = q[i];
    for(j = i + 1, n,
      my(t = (algnorm(al, M[, i] + M[, j]) - q[i] - q[j]) / 2);
      A[i, j] = t; A[j, i] = t));
  A;
}
\\ n(I) measured as gcd of A_ii and 2 A_ij (= gcd of all values of Nrd on I).
normgcd(A) = {
  my(g = 0, n = matsize(A)[1]);
  for(i = 1, n, g = gcd(g, A[i, i]); for(j = i + 1, n, g = gcd(g, 2 * A[i, j])));
  g;
}
\\ Trace-form matrix T_ij = Trd(e_i conj(e_j)) (no halving; C-TRD).
trace_form(al, M) = {
  my(n = matsize(M)[2]);
  matrix(n, n, i, j, algtrace(al, algmul(al, M[, i], conjq(al, M[, j]))));
}
\\ Trd(e_i e_j) matrix (integral on an order), used to construct P.
trace_prod(al, M) = {
  my(n = matsize(M)[2]);
  matrix(n, n, i, j, algtrace(al, algmul(al, M[, i], M[, j])));
}

\\ Standard lattice record: basis (O_0 coords), unscaled algnorm Gram, form
\\ scale s (form = Nrd/s), scaled Gram, matdet of the scaled Gram.
latrec(al, name, arm, M, s, extra) = {
  my(G = gram_nrd(al, M), Gs = G / s);
  concat([jkv("name", jq(name)), jkv("arm", jq(arm)), jkv("rank", Str(matsize(M)[2])),
          jkv("basis", jcols(M)), jkv("form_scale", jr(s)),
          jkv("gram_nrd_unscaled", jrows(G)), jkv("gram", jrows(Gs)),
          jkv("det_pari", jr(matdet(Gs))), jkv("det_pari_unscaled", jr(matdet(G)))], extra);
}

\\ ------------------------------------------------------------ prime search
\\ Class codes: 1 = 3 mod 4, 2 = 5 mod 8, 3 = 1 mod 8.
pclass(p) = if(p % 4 == 3, 1, if(p % 8 == 5, 2, 3));
find_primes(B, cnt) = {
  my(res = vector(3, i, List()), q = B, prov = List());
  while(vecmin(apply(L -> #L, res)) < cnt,
    q = nextprime(q + 1);
    my(c = pclass(q));
    if(#res[c] < cnt, listput(res[c], q)));
  vector(3, c, Vec(res[c]));
}
emit_primes() = {
  my(M = find_primes(2^63, 2), L = find_primes(2^255, 1), out = List());
  for(c = 1, 3, for(t = 1, #M[c], listput(out, jobj([jkv("tier", jq("M")), jkv("class", Str(c)),
        jkv("p", jr(M[c][t])), jkv("isprime_proven", Str(isprime(M[c][t])))]))));
  for(c = 1, 3, for(t = 1, #L[c], listput(out, jobj([jkv("tier", jq("L")), jkv("class", Str(c)),
        jkv("p", jr(L[c][t])), jkv("isprime_proven", Str(isprime(L[c][t])))]))));
  emit([jkv("stage", jq("primes")), jkv("primes", jlist(Vec(out)))]);
}

\\ ------------------------------------------------------------ stage 1
\\ Algebra construction, C-ALG (a) ramification, C-ALG (b) reduced norm,
\\ structure constants, algmul products of basis elements, images of i, j,
\\ arm A1 (the stored maximal order O_0, Z-basis = unit vectors).
stage1(p, a, b) = {
  my(al, err = "", t0 = getabstime());
  setrand(ALGINIT_SEED);  \\ alginit may use PARI's RNG; fixed, recorded state
  al = iferr(alginit(nfinit(y), [a, b]), E, err = strclean(Str(E)); 0);
  if(err != "", emit([jkv("stage", jq("stage1")), jkv("p", jr(p)), jkv("error", jq(err))]); return(0));
  my(one = one_of(al), rp = algramifiedplaces(al), fin = List(), ninf = 0);
  for(i = 1, #rp, if(type(rp[i]) == "t_INT", ninf++, listput(fin, rp[i].p)));
  my(hp = factor(abs(2 * a * b))[, 1], hil = List());
  for(i = 1, #hp, listput(hil, jobj([jkv("place", jr(hp[i])), jkv("symbol", Str(hilbert(a, b, hp[i])))])));
  listput(hil, jobj([jkv("place", jq("inf")), jkv("symbol", Str(hilbert(a, b, 0)))]));
  my(mt = algmultable(al));
  my(prods = List());
  for(i = 1, 4, for(j = 1, 4, listput(prods, jv(algmul(al, unitv(i), unitv(j))))));
  my(pol = algsplittingfield(al).pol, vv = variable(pol));
  my(Ii = algalgtobasis(al, [vv, 0]~), Jj = algalgtobasis(al, [0, 1]~), Kk = algmul(al, Ii, Jj));
  my(rel_ok = (algmul(al, Ii, Ii) == a * one) && (algmul(al, Jj, Jj) == b * one) && (algmul(al, Jj, Ii) == -Kk));
  my(A1 = latrec(al, "A1", "A1", matid(4), 1, [jkv("trd_basis", jv(vector(4, i, algtrace(al, unitv(i)))))]));
  emit([jkv("stage", jq("stage1")), jkv("p", jr(p)), jkv("a", jr(a)), jkv("b", jr(b)),
        jkv("error", "null"),
        jkv("one", jv(one)),
        jkv("nrd_one", jr(algnorm(al, one))), jkv("nrd_two", jr(algnorm(al, 2 * one))),
        jkv("trd_one", jr(algtrace(al, one))),
        jkv("ramified_finite", jv(Vec(fin))), jkv("ramified_infinite_count", Str(ninf)),
        jkv("hasse_inf", jv(Vec(alghassei(al)))),
        jkv("hilbert", jlist(Vec(hil))),
        jkv("multable", jlist(vector(4, i, jrows(mt[i])))),
        jkv("algmul_products", jlist(Vec(prods))),
        jkv("algbasis_natural", jcols(algbasis(al))),
        jkv("splitting_pol", jq(Str(pol))),
        jkv("i_image", jv(Ii)), jkv("j_image", jv(Jj)), jkv("k_image", jv(Kk)),
        jkv("ijk_relations_ok", jb(rel_ok)),
        jkv("A1", jobj(A1)),
        jkv("ms", Str(getabstime() - t0))]);
  1;
}

\\ ------------------------------------------------------------ stage 2
\\ B      : 4x4 rational matrix, columns = base-order Z-basis in O_0 coords
\\          (identity unless the base-order fallback to A2 is used)
\\ Ns     : the 20 frozen target norms (A4 order)
\\ seeds  : the 20 PARI setrand seeds for A4 (derived by the driver)
\\ Hs     : the 22 A6 matrices (driver-generated, Python random.Random)
\\ extraG : Python-built Gram matrices (arm A2) whose matdet PARI must supply
\\ maxatt : cap on random alpha attempts per A4 ideal
stage2(p, a, b, B, Ns, seeds, Hs, extraG, maxatt) = {
  my(al, err = "", t0 = getabstime());
  setrand(ALGINIT_SEED);  \\ alginit may use PARI's RNG; fixed, recorded state
  al = iferr(alginit(nfinit(y), [a, b]), E, err = strclean(Str(E)); 0);
  if(err != "", emit([jkv("stage", jq("stage2")), jkv("p", jr(p)), jkv("error", jq(err))]); return(0));
  my(one = one_of(al), Binv = B^(-1), recs = List(), mt = algmultable(al));

  \\ base order O (arm A1's O_0 or fallback) under Nrd
  listput(recs, jobj(latrec(al, "base", "base", B, 1, [])));

  \\ C-TRD: trace form without halving on the base
  my(T = trace_form(al, B));
  listput(recs, jobj([jkv("name", jq("C-TRD")), jkv("arm", jq("C-TRD")), jkv("basis", jcols(B)),
        jkv("gram", jrows(T)), jkv("det_pari", jr(matdet(T)))]));

  \\ C-NONMAX: Z + 2 O
  my(oneb = Binv * one, HN = mathnf(matconcat([oneb, 2 * matid(4)])), NB = B * HN);
  listput(recs, jobj(latrec(al, "C-NONMAX", "C-NONMAX", NB, 1,
        [jkv("index_matrix_in_base", jcols(HN)), jkv("index_pari", jr(abs(matdet(HN)))),
         jkv("trace_form", jrows(trace_form(al, NB))), jkv("trace_form_det_pari", jr(matdet(trace_form(al, NB))))])));

  \\ A3: P = {x in O : p | Nrd(x)} constructed as pO + (lifted kernel of the
  \\ Trd(x y) matrix of O reduced mod p). Verified afterwards by C-ALG (e).
  my(T0 = trace_prod(al, B), Kp = matkermod(T0, p), HP = mathnf(matconcat([p * matid(4), Kp])), PB = B * HP);
  my(GP0 = gram_nrd(al, PB));
  listput(recs, jobj(latrec(al, "A3", "A3", PB, p,
        [jkv("index_matrix_in_base", jcols(HP)), jkv("index_pari", jr(abs(matdet(HP)))),
         jkv("n_pari", jr(normgcd(GP0))), jkv("kernel_mod_p_dim", Str(matsize(Kp)[2]))])));

  \\ C-NEAR: O^0 and P^0 (trace-zero sublattices, rank 3)
  my(K0 = matkerint(Mat(vector(4, i, algtrace(al, B[, i])))), O0B = B * K0);
  listput(recs, jobj(latrec(al, "C-NEAR-O0", "C-NEAR-O0", O0B, 1, [])));
  my(K1 = matkerint(Mat(vector(4, i, algtrace(al, PB[, i])))), P0B = PB * K1);
  listput(recs, jobj(latrec(al, "C-NEAR-P0", "C-NEAR-P0", P0B, p, [])));

  \\ A4 left ideals and A5 right orders
  my(IBs = vector(#Ns), nIs = vector(#Ns));
  for(k = 1, #Ns,
    my(N = Ns[k], fl = factor(N)[, 1], att = 0, found = 0, v, alpha, nr);
    setrand(seeds[k]);
    while(!found && att < maxatt,
      att++;
      v = vector(4, i, random(N))~;
      my(prim = 1);
      for(t = 1, #fl, if(v % fl[t] == 0, prim = 0));
      if(prim,
        alpha = B * v; nr = algnorm(al, alpha);
        if(denominator(nr) == 1 && nr % N == 0, found = 1)));
    if(!found,
      listput(recs, jobj([jkv("name", jq(Str("A4_", k))), jkv("arm", jq("A4")), jkv("idx", Str(k)),
            jkv("target_norm", jr(N)), jkv("seed", jr(seeds[k])), jkv("attempts", Str(att)),
            jkv("error", jq("no primitive alpha found within maxatt"))]));
      IBs[k] = 0; next);
    my(gens = matconcat([matconcat(vector(4, i, Binv * algmul(al, B[, i], alpha))), N * matid(4)]));
    my(HI = mathnf(gens));
    if(matsize(HI)[2] != 4,
      listput(recs, jobj([jkv("name", jq(Str("A4_", k))), jkv("arm", jq("A4")), jkv("idx", Str(k)),
            jkv("error", jq("HNF not of rank 4"))]));
      IBs[k] = 0; next);
    my(IB = B * HI, GI = gram_nrd(al, IB), nI = normgcd(GI));
    IBs[k] = IB; nIs[k] = nI;
    listput(recs, jobj(latrec(al, Str("A4_", k), "A4", IB, nI,
          [jkv("idx", Str(k)), jkv("target_norm", jr(N)), jkv("seed", jr(seeds[k])),
           jkv("attempts", Str(att)), jkv("alpha_base_coords", jv(v)), jkv("alpha", jv(alpha)),
           jkv("nrd_alpha", jr(nr)),
           jkv("index_matrix_in_base", jcols(HI)), jkv("index_pari", jr(abs(matdet(HI)))),
           jkv("n_pari", jr(nI))])));
    \\ A5: O_R(I) = {x : I x subset I} = dual (dot product) of the row
    \\ lattice of Phi, Phi = stack_i IB^{-1} [c_i e_1 | ... | c_i e_4].
    my(IBinv = IB^(-1), Xs = vector(4, i, IBinv * matconcat(vector(4, kk, algmul(al, IB[, i], unitv(kk))))));
    my(PhiT = matconcat(vector(4, i, Xs[i]~)));   \\ 4 x 16; its columns are the rows of Phi
    my(Phi = PhiT~);
    my(d = denominator(Phi), Hn = mathnf(d * PhiT));
    if(matsize(Hn)[2] != 4,
      listput(recs, jobj([jkv("name", jq(Str("A5_", k))), jkv("arm", jq("A5")), jkv("idx", Str(k)),
            jkv("error", jq("row lattice not of rank 4"))])); next);
    my(G = Hn / d, OR = (G^(-1))~, d2 = denominator(OR), ORB = mathnf(d2 * OR) / d2);
    listput(recs, jobj(latrec(al, Str("A5_", k), "A5", ORB, 1, [jkv("idx", Str(k))]))));

  \\ A6 sublattices: parents [base, P, I_1..I_20] with forms [1, p, n(I_k)]
  my(Ms = concat([B, PB], Vec(IBs)), sc = concat([1, p], Vec(nIs)));
  for(k = 0, 21,
    my(M = Ms[k + 1], H = Hs[k + 1]);
    if(type(M) == "t_INT",
      listput(recs, jobj([jkv("name", jq(Str("A6_", k))), jkv("arm", jq("A6")), jkv("idx", Str(k)),
            jkv("error", jq("parent lattice missing"))])); next);
    listput(recs, jobj(latrec(al, Str("A6_", k), "A6", M * H, sc[k + 1],
          [jkv("idx", Str(k)), jkv("H", jcols(H)), jkv("index_pari", jr(abs(matdet(H))))]))));

  \\ PARI matdet of Python-built Grams (arm A2, C-CROSS (i))
  my(xd = vector(#extraG, i, jr(matdet(extraG[i]))));

  emit([jkv("stage", jq("stage2")), jkv("p", jr(p)), jkv("error", "null"),
        jkv("one", jv(one)),
        jkv("multable", jlist(vector(4, i, jrows(mt[i])))),
        jkv("lattices", jlist(Vec(recs))),
        jkv("extra_dets_pari", jlist(xd)),
        jkv("ms", Str(getabstime() - t0))]);
  1;
}
