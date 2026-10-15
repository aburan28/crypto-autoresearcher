\\ Independent endpoint-level validator for the seed-45641 preflight.
\\ This is deliberately separate from the kernel-line certificate in
\\ kernel163_45641_map.gp.
\\ Execute through run_verify163_45641_seed_endpoint.gp.
{if(type(FAIL_CLOSED_DRIVER) != "t_INT" || FAIL_CLOSED_DRIVER != 1,
  print("ENDPOINT_FLOOR_CERTIFICATE FAIL reason=use_run_verify163_45641_seed_endpoint_driver");
  quit(1)
)};
if(getenv("GP_FAIL_CLOSED_FAULT") == "1", error("injected fail-closed fault"));

MOD = x^163 + x^7 + x^6 + x^3 + 1;
lp = 45641;
bb = 24362196697750487851526857852297647817644684697;
expected_cycle = 9128;
CAP = 20000;

g = ffgen(Mod(1,2) * MOD, 'g);
{must(ok, message) =
  if(!ok,
    print("ENDPOINT_FLOOR_CERTIFICATE FAIL reason=", message);
    quit(1)
  )
};
fromint(n) = my(s = 0*g, k = 0); while(n, if(n % 2, s += g^k); n \= 2; k++); s;
source = ellinit([1,1,0,0,1], g);
target = ellinit([1,1,0,0,fromint(bb)], g);
wrong_twist = ellinit([1,0,0,0,fromint(bb)], g);
source_order = ellcard(source);
target_order = ellcard(target);
wrong_twist_order = ellcard(wrong_twist);
must(target_order == source_order, "target is outside the source isogeny class");
must(wrong_twist_order != source_order, "a2 twist discriminator failed");

Phi = polmodular(11, , , 'Y);
roots_q(j) = my(L = factor(subst(Phi, 'x, j)*g^0)[,1]); apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f) == 1, L~));
{cycle11(b) =
  my(j0 = 1/fromint(b), roots = roots_q(j0), previous = j0,
     current, steps = 1, next_j);
  if(#roots == 1 && roots[1] == j0, return(1));
  must(#roots == 2, "cycle start does not have exactly two rational 11-neighbours");
  current = roots[1];
  while(current != j0,
    must(steps < CAP, "11-cycle hit CAP before closing");
    roots = roots_q(current);
    must(#roots == 2, "cycle vertex does not have exactly two rational 11-neighbours");
    next_j = 0;
    if(roots[1] == previous, next_j = roots[2]);
    if(roots[2] == previous, next_j = roots[1]);
    must(next_j != 0, "cycle predecessor is absent");
    previous = current;
    current = next_j;
    steps++
  );
  steps
}

crater_cycle = cycle11(1);
target_cycle = cycle11(bb);
must(crater_cycle == 1, "crater cycle control failed");
must(target_cycle == expected_cycle, "endpoint cycle does not certify conductor 45641");

D = -7 * lp^2;
class_number = qfbclassno(D);
Q11 = qfbprimeform(D, 11);
I11 = qfbpow(Q11, 0);
must(class_number == 45640, "unexpected ring class number");
must(qfbred(qfbpow(Q11, expected_cycle)) == qfbred(I11), "declared 11-class order does not divide 9128");
{foreach([2,7,163], p,
  must(qfbred(qfbpow(Q11, expected_cycle/p)) != qfbred(I11),
    "declared 11-class order is not exact"));}

print("SOURCE_ORDER ", source_order);
print("ENDPOINT_B ", bb);
print("TARGET_ORDER ", target_order, " a2=1 match=PASS");
print("WRONG_TWIST_ORDER ", wrong_twist_order, " differs=PASS");
print("CYCLE11 crater=", crater_cycle, " endpoint=", target_cycle);
{print("RING_CLASS discriminant=", D, " class_number=", class_number,
       " order_l11=", expected_cycle);}
print("ENDPOINT_FLOOR_CERTIFICATE PASS");
RUN_COMPLETE = 1;
