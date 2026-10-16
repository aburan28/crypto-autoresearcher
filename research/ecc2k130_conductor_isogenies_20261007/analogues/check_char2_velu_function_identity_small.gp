\\ Bounded exact-symbolic fixture for the function-field identity gate in
\\ kernel163_45641_map_relative.gp.  The curve
\\   y^2 + x*y = x^3 + x^2 + 1 over F_(2^3)
\\ has the explicit order-seven point Q below.  Its three nonzero kernel
\\ abscissae give a degree-three h, exercising Hasse derivatives [2] and [3].
\\ Execute through run_check_char2_velu_function_identity_small.gp so an
\\ unexpected GP exception is converted to a nonzero process status.
{if(type(FAIL_CLOSED_DRIVER) != "t_INT" || FAIL_CLOSED_DRIVER != 1,
  print("RESULT=FAIL reason=use_run_check_char2_velu_function_identity_small_driver");
  quit(1)
)};
if(getenv("GP_FAIL_CLOSED_FAULT") == "1", error("injected fail-closed fault"));

{fail_closed(message) =
  print("RESULT=FAIL reason=", message);
  quit(1)
};
{must(ok, message) =
  if(!ok, fail_closed(message))
};

Xvar = varhigher("X");
tvar = varlower("t", Xvar);
g = ffgen(ffinit(2, 3, tvar), 'g);
a2 = 1;
E0 = ellinit([1, a2, 0, 0, 1], g);
Q = [g^2 + g + 1, g^2 + g + 1];
must(ellisoncurve(E0, Q), "frozen fixture point is off curve");
must(ellmul(E0, Q, 7) == [0], "fixture point is not killed by seven");
must(ellmul(E0, Q, 1) != [0], "fixture point is infinity");

half = 3;
h = prod(i = 1, half, Xvar + ellmul(E0, Q, i)[1]);
hp = deriv(h);
must(poldegree(h) == half && pollead(h) == 1, "bad fixture kernel polynomial");
must(poldegree(gcd(h, hp)) == 0, "fixture kernel polynomial is not squarefree");

{hasse_polynomial(H, j) =
  my(d = poldegree(H), z = 0*g);
  if(d < j, return(z));
  Polrev(vector(d-j+1, t,
    if(bitand(t+j-1, j) == j, polcoef(H, t+j-1, Xvar), z)
  ), Xvar)
};

\\ Return denominator-cleared and direct-rational checks for the two
\\ identities.  The cleared numerators use denominators H^4 and H^6.
{identity_checks(H, H1, btarget) =
  my(n = poldegree(H), parity = n % 2,
     H2 = hasse_polynomial(H, 2), H3 = hasse_polynomial(H, 3),
     Hsq = H^2, Hcube = H^3,
     a_num, x_num, alpha_num, p3_num, z3_num, beta_num,
     source_rhs, cleared_y, cleared_constant,
     L, E2, E3, A, Xout, alpha, P3, z3sum, beta,
     direct_y, direct_constant);
  a_num = parity*H + Xvar*H1;
  x_num = Xvar*Hsq + a_num*H + a_num^2;
  alpha_num = Hsq + H1*H + Xvar*H1^2;
  p3_num = H1^3 + H1*H2*H + H3*Hsq;
  z3_num = parity*Hcube + Xvar*H1*Hsq + Xvar^2*H1^2*H + Xvar^3*p3_num;
  beta_num = Xvar*(a_num^2 + a_num*H)*H + a_num*Hsq + z3_num;
  source_rhs = Xvar^3 + a2*Xvar^2 + 1;
  cleared_y = (Xvar*alpha_num^2 + x_num*alpha_num == 0);
  cleared_constant = (alpha_num^2*source_rhs*Hsq + beta_num^2
                    + x_num*beta_num*H + x_num^3
                    + a2*x_num^2*Hsq + btarget*Hcube^2 == 0);

  L = H1/H;
  E2 = H2/H;
  E3 = H3/H;
  A = parity + Xvar*L;
  Xout = Xvar + A + A^2;
  alpha = 1 + L + Xvar*L^2;
  P3 = L^3 + L*E2 + E3;
  z3sum = parity + Xvar*L + Xvar^2*L^2 + Xvar^3*P3;
  beta = Xvar*(A^2 + A) + A + z3sum;
  direct_y = (alpha^2*Xvar + Xout*alpha == 0);
  direct_constant = (alpha^2*source_rhs + beta^2 + Xout*beta
                   + Xout^3 + a2*Xout^2 + btarget == 0);
  [cleared_y, cleared_constant, direct_y, direct_constant]
};

tcoef = polcoef(h, half-1, Xvar);
b_endpoint = 1 + tcoef + tcoef^2;
checks = identity_checks(h, hp, b_endpoint);
must(checks == [1, 1, 1, 1], "valid order-seven fixture failed exact identities");

\\ Paired negative control: changing only b' leaves the y-coefficient
\\ identity intact and must falsify both forms of the constant identity.
wrong_endpoint_b = b_endpoint + g;
must(wrong_endpoint_b != 0 && wrong_endpoint_b != b_endpoint, "wrong-endpoint control must remain nonsingular and distinct");
negative_checks = identity_checks(h, hp, wrong_endpoint_b);
must(negative_checks == [1, 0, 1, 0], "wrong-endpoint negative control did not fail selectively");

print("FIXTURE field_degree=3 ell=7 h=", h, " hasse2=", hasse_polynomial(h, 2), " hasse3=", hasse_polynomial(h, 3), " endpoint_b=", b_endpoint, " wrong_nonsingular_b=", wrong_endpoint_b);
print("CHECK exact_denominator_cleared=PASS direct_rational=PASS wrong_endpoint_control=PASS");
print("RESULT=PASS");
RUN_COMPLETE = 1;
