\\ Separate exhaustive verification of the K-283 conductor-1697 CM census.
\\ Input is the single vector written by run_k283_f1697.gp.
\\ This certifies structure only: it does not construct a degree-1697 map or
\\ establish an ECDLP speedup.

m = 283;
F = 1697;
S = 37;
EXPECTED_FLOOR = 1698;
EXPECTED_ORBITS = 6;
EXPECTED_SUBGROUP_ORDER = 3885337784451458141838923813647037813284811733793061324295874997529815829704422603873;
EXPECTED_ORDER = 4*EXPECTED_SUBGROUP_ORDER;
EXPECTED_TRACE = 7777244870872830999287791970962823977569917;
EXPECTED_FPI = 489878522800087734083485536590018444665943;
MOD = x^283+x^12+x^7+x^5+1;
D = -7*F^2;

must(ok, msg) =
{
  if(!ok, error(msg));
};

must(D == -20158663, Str("wrong order discriminant: ", D));
must(polisirreducible(Mod(1,2)*MOD),
  "the NIST degree-283 field polynomial is not irreducible");

g = ffgen(Mod(1,2)*MOD, 'g);

toint(z) =
{
  subst(lift(z.pol), variable(z.pol), 2);
};

fromint(n) =
{
  my(s = 0*g, k = 0);
  while(n,
    if(n % 2, s += g^k);
    n \= 2;
    k++;
  );
  return(s);
};

\\ Pin the source to the standardized K-283 group, trace and Frobenius order.
Q = 2^m;
E0 = ellinit([1,0,0,0,1], g);
N0 = ellcard(E0);
T0 = Q+1-N0;
DELTA0 = T0^2-4*Q;
must(isprime(EXPECTED_SUBGROUP_ORDER),
  "the pinned SEC2 subgroup order is not prime");
must(N0 == EXPECTED_ORDER,
  Str("wrong K-283 group order: ", N0));
must(T0 == EXPECTED_TRACE,
  Str("wrong K-283 trace: ", T0));
must(DELTA0 == -7*EXPECTED_FPI^2,
  Str("wrong Frobenius discriminant: ", DELTA0));
must(EXPECTED_FPI % F == 0,
  "1697 does not divide the pinned Frobenius conductor");

\\ Fail closed on a stale write()-appended census or malformed rows.
RAW = readvec("floor_k283_f1697.txt");
must(#RAW == 1,
  Str("expected exactly one GP expression in floor file; got ", #RAW,
      " (a stale rerun may have appended another line)"));

L = RAW[1];
must(type(L) == "t_VEC", "floor file does not contain a vector");

for(i = 1, #L,
  must(type(L[i]) == "t_VEC",
    Str("floor row ", i, " is not a vector"));
  must(#L[i] == 2,
    Str("floor row ", i, " does not have exactly two fields"));
  must(type(L[i][1]) == "t_INT",
    Str("floor row ", i, " has a non-integer b"));
  must(type(L[i][2]) == "t_INT",
    Str("floor row ", i, " has a non-integer a2"));
);

must(#L == EXPECTED_FLOOR,
  Str("wrong floor row count: ", #L, " != ", EXPECTED_FLOOR));

for(i = 1, #L,
  must(L[i][1] > 0 && L[i][1] < Q,
    Str("floor row ", i, " has b outside 1..2^m-1"));
  must(L[i][2] == 0,
    Str("floor row ", i, " has a2=", L[i][2], " instead of 0"));
);

ALL = Set(apply(z -> z[1], L));
must(#ALL == EXPECTED_FLOOR,
  Str("floor b-values are not distinct: ", #ALL, " != ", EXPECTED_FLOOR));
must(!setsearch(ALL, 1), "the crater b=1 leaked into the floor census");

\\ Recompute the Weber class polynomial and the complete root set, rather than
\\ trusting the producer's row count.
CLASS_NUMBER = qfbclassno(D);
must(CLASS_NUMBER == EXPECTED_FLOOR,
  Str("wrong class number: ", CLASS_NUMBER, " != ", EXPECTED_FLOOR));

H = polclass(D, 1);
must(poldegree(H) == EXPECTED_FLOOR,
  Str("wrong Weber class-polynomial degree: ", poldegree(H)));
H2 = lift(H*Mod(1,2));
H = 0;
FA = factormod(H2, 2);
must(matsize(FA)[1] == EXPECTED_ORBITS,
  Str("wrong number of factors modulo 2: ", matsize(FA)[1]));
must(Set(apply(poldegree, FA[,1]~)) == Set([m]),
  Str("unexpected factor degrees modulo 2: ",
      Set(apply(poldegree, FA[,1]~))));
must(Set(FA[,2]~) == Set([1]),
  Str("class polynomial is not squarefree modulo 2: ", Set(FA[,2]~)));

{
  ROOTS = List();
  foreach(FA[,1]~, P,
    my(LP = factor(subst(lift(P), variable(lift(P)), 'Y)*g^0)[,1]);
    my(r = 0);
    foreach(LP~, f,
      if(poldegree(f) == 1,
        r = -polcoeff(f,0)/polcoeff(f,1);
        break
      )
    );
    must(r != 0, "an irreducible factor has no nonzero root in F_2^283");
    my(c = r);
    for(k = 1, poldegree(P),
      listput(ROOTS, c);
      c = c^2;
    );
    must(c == r, "a reconstructed Frobenius orbit did not close");
  );
}
EXPECTED_B = vecsort(apply(z -> toint(1/z^48), Vec(ROOTS)));
must(#EXPECTED_B == EXPECTED_FLOOR,
  Str("wrong reconstructed CM-root count: ", #EXPECTED_B));
must(#Set(EXPECTED_B) == EXPECTED_FLOOR,
  "reconstructed CM roots are not distinct");
must(Set(EXPECTED_B) == ALL,
  "census b-values differ from the independently reconstructed CM root set");

\\ Check every model against the standardized group order.
BAD_ORDERS = 0;
for(i = 1, #L,
  if(ellcard(ellinit([1,L[i][2],0,0,fromint(L[i][1])], g))
      != EXPECTED_ORDER,
    BAD_ORDERS++;
  )
);
must(BAD_ORDERS == 0,
  Str(BAD_ORDERS, " floor models have the wrong group order"));

orbit_size(z) =
{
  my(c = z^2, n = 1);
  while(c != z && n <= m,
    c = c^2;
    n++;
  );
  must(c == z, "Frobenius orbit failed to close within degree 283");
  return(n);
};

ORBIT_SIZES = Set(apply(b -> orbit_size(fromint(b)), ALL));
must(ORBIT_SIZES == Set([m]),
  Str("unexpected Frobenius orbit sizes: ", ORBIT_SIZES));

ORBIT_REPRESENTATIVES =
  Set(apply(b -> {
    my(z = fromint(b), c = z^2, least = b);
    while(c != z,
      least = min(least, toint(c));
      c = c^2;
    );
    least;
  }, ALL));
must(#ORBIT_REPRESENTATIVES == EXPECTED_ORBITS,
  Str("unexpected Frobenius orbit count: ",
      #ORBIT_REPRESENTATIVES, " != ", EXPECTED_ORBITS));

ordq(disc, p, cap) =
{
  my(P = qfbprimeform(disc, p));
  my(R = P);
  my(I = qfbpow(P, 0));
  my(k = 1);

  while(qfbred(R) != qfbred(I) && k < cap,
    R = qfbcomp(R, P);
    k++;
  );

  if(qfbred(R) != qfbred(I),
    error(Str("class-group order search exceeded cap ", cap)));

  return(k);
};

must(kronecker(D, S) == 1,
  "37 does not split in the order discriminant");
IDEAL_ORDER = ordq(D, S, EXPECTED_FLOOR + 1);
must(IDEAL_ORDER == EXPECTED_FLOOR,
  Str("wrong order for [l_37]: ", IDEAL_ORDER,
      " != ", EXPECTED_FLOOR));

PHI = polmodular(S, , , 'Y);

linear_roots(j) =
{
  my(fac, factors, roots);

  fac = factor(subst(PHI, 'x, j)*g^0);
  factors = fac[,1];
  roots = apply(
    f -> -polcoeff(f,0)/polcoeff(f,1),
    select(f -> poldegree(f) == 1, factors~)
  );
  for(k = 1, #roots,
    must(roots[k] != 0, "a rational 37-neighbour has j=0")
  );

  return(roots);
};

walk(bb, expected_roots, cap) =
{
  my(j0, roots, prev, cur, out, next_roots, nx, backtracks, successors);

  j0 = 1/fromint(bb);
  roots = linear_roots(j0);
  must(#roots == expected_roots,
    Str("start vertex has ", #roots,
        " distinct rational 37-neighbours; expected ", expected_roots));

  prev = j0;
  cur = roots[1];
  out = List([bb]);

  while(cur != j0,
    must(#out < cap,
      Str("37-walk failed to close within ", cap, " vertices"));

    listput(out, toint(1/cur));

    next_roots = linear_roots(cur);
    must(#next_roots == expected_roots,
      Str("walk vertex has ", #next_roots,
          " distinct rational 37-neighbours; expected ", expected_roots));

    nx = 0;
    backtracks = 0;
    successors = 0;
    for(k = 1, #next_roots,
      if(next_roots[k] == prev,
        backtracks++;
      ,
        successors++;
        nx = next_roots[k];
      )
    );
    must(backtracks == 1,
      Str("37-walk has ", backtracks, " dual/backtracking neighbours"));
    must(successors == 1,
      Str("37-walk has ", successors, " non-backtracking neighbours"));

    prev = cur;
    cur = nx;
  );

  must(cur == j0, "37-walk exited without closing at its start");
  return(Vec(out));
};

CRATER_CYCLE = walk(1, 1, 1);
must(#CRATER_CYCLE == 1,
  Str("crater 37-cycle length is ", #CRATER_CYCLE, " instead of 1"));

FLOOR_CYCLE = walk(ALL[1], 2, EXPECTED_FLOOR);
FLOOR_SET = Set(FLOOR_CYCLE);
OUTSIDE = setminus(FLOOR_SET, ALL);
MISSING = setminus(ALL, FLOOR_SET);

must(#FLOOR_CYCLE == EXPECTED_FLOOR,
  Str("floor 37-cycle length is ", #FLOOR_CYCLE,
      " instead of ", EXPECTED_FLOOR));
must(#FLOOR_SET == EXPECTED_FLOOR,
  Str("floor walk contains only ", #FLOOR_SET,
      " unique vertices instead of ", EXPECTED_FLOOR));
must(#OUTSIDE == 0,
  Str("floor walk visited ", #OUTSIDE, " vertices outside the CM census"));
must(#MISSING == 0,
  Str("floor walk missed ", #MISSING, " CM endpoints"));

print("source prime subgroup order = ", EXPECTED_SUBGROUP_ORDER);
print("source cofactor = 4");
print("source group order = ", N0);
print("source trace = ", T0);
print("Frobenius conductor = ", EXPECTED_FPI);
print("D = ", D);
print("h(D) = ", CLASS_NUMBER);
print("CM factors modulo 2 = ", matsize(FA)[1], " x degree ", m);
print("floor models with wrong order = ", BAD_ORDERS);
print("Frobenius orbit sizes = ", ORBIT_SIZES);
print("Frobenius orbit count = ", #ORBIT_REPRESENTATIVES);
print("ord[l_", S, "] = ", IDEAL_ORDER);
print("crater 37-cycle length = ", #CRATER_CYCLE);
print("floor 37-cycle length = ", #FLOOR_CYCLE);
print("unique floor vertices visited = ", #FLOOR_SET);
print("vertices outside CM census = ", #OUTSIDE);
print("CM endpoints missed = ", #MISSING);
print("K-283 conductor-1697 structural verification: PASS");
