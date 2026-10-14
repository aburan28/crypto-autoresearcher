\\ Exact same-degree horizontal control on standard NIST K-163.
\\
\\ In End(E)=Z[tau], tau^2-tau+2=0.  The split-prime element
\\ alpha=51-160*tau has norm 45641 and true conjugate
\\ alpha_bar=-109+160*tau, so alpha_bar*alpha=[45641].  This control
\\ exercises the target degree without crossing conductor.  It is not a
\\ substitute for the descending map.
\\ Execute through run_control163_45641_horizontal_endomorphism.gp.
{if(type(FAIL_CLOSED_DRIVER) != "t_INT" || FAIL_CLOSED_DRIVER != 1,
  print("RESULT=FAIL reason=use_run_control163_45641_horizontal_endomorphism_driver");
  quit(1)
)};
if(getenv("GP_FAIL_CLOSED_FAULT") == "1", error("injected fail-closed fault"));

SCHEMA = "k163-degree45641-horizontal-control-v1";
MOD = x^163 + x^7 + x^6 + x^3 + 1;
ell = 45641;
samples = 1024;
r = 0x4000000000000000000020108A2E0CC0D99F8A5EF;
gx_int = 0x02fe13c0537bbc11acaa07d793de4e6d5e5c94eee8;
gy_int = 0x0289070fb05d38ff58321f2e800536d538ccdaa3d9;

{must(ok, message) =
  if(!ok, print("RESULT=FAIL reason=", message); quit(1))
};
g = ffgen(Mod(1,2) * MOD, 'g);
E = ellinit([1,1,0,0,1], g);
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, j = 0); while(n, if(n % 2, s += g^j); n \= 2; j++); s;

G = [fromint(gx_int), fromint(gy_int)];
must(ellcard(E) == 2*r, "source order mismatch");
must(isprime(r), "subgroup order is not prime");
must(ellisoncurve(E,G), "standard generator is off curve");
must(ellmul(E,G,r) == [0], "standard generator has wrong order");

{tau(P) =
  if(P == [0], [0], [P[1]^2, P[2]^2])
};
{alpha(P) =
  if(P == [0], return([0]));
  elladd(E, ellmul(E,P,51), ellneg(E,ellmul(E,tau(P),160)))
};
{alpha_bar(P) =
  if(P == [0], return([0]));
  elladd(E, ellmul(E,tau(P),160), ellneg(E,ellmul(E,P,109)))
};

\\ Multiply (a0+a1*tau)(b0+b1*tau) with tau^2=tau-2.
{cm_mul(A,B) =
  [A[1]*B[1]-2*A[2]*B[2], A[1]*B[2]+A[2]*B[1]+A[2]*B[2]]
};
cm_product = cm_mul([51,-160],[-109,160]);
must(cm_product == [ell,0], "CM norm/composition identity failed");
must(kronecker(-7,ell) == 1, "45641 is not split");

tauG = tau(G);
must(ellisoncurve(E,tauG), "absolute Frobenius image is off curve");
lambda_roots = polrootsmod('T^2-'T+2,r);
lambda = -1;
{for(i=1,#lambda_roots,
  candidate = lift(lambda_roots[i]);
  if(ellmul(E,G,candidate) == tauG, lambda = candidate)
);};
must(lambda >= 0, "could not identify tau scalar on the standard subgroup");
alpha_scalar = lift(Mod(51-160*lambda,r));
dual_scalar = lift(Mod(-109+160*lambda,r));
must(lift(Mod(alpha_scalar,r)*Mod(dual_scalar,r)) == ell % r, "subgroup scalar composition failed");

image_G = alpha(G);
dual_image_G = alpha_bar(G);
must(image_G == ellmul(E,G,alpha_scalar), "alpha generator action mismatch");
must(dual_image_G == ellmul(E,G,dual_scalar), "dual generator action mismatch");
must(alpha_bar(image_G) == ellmul(E,G,ell), "dual(alpha(G)) != [45641]G");
must(alpha(dual_image_G) == ellmul(E,G,ell), "alpha(dual(G)) != [45641]G");

setrand(45641);
t0 = getwalltime();
{for(i=1,samples,
  scalar = random(r-1)+1;
  P = ellmul(E,G,scalar);
  A = alpha(P);
  B = alpha_bar(P);
  must(A == ellmul(E,P,alpha_scalar), Str("alpha scalar mismatch at sample ",i));
  must(B == ellmul(E,P,dual_scalar), Str("dual scalar mismatch at sample ",i));
  must(alpha_bar(A) == ellmul(E,P,ell), Str("left composition mismatch at sample ",i));
  must(alpha(B) == ellmul(E,P,ell), Str("right composition mismatch at sample ",i))
);};
elapsed_ms = getwalltime()-t0;

print("SCHEMA=", SCHEMA);
{print("CM alpha=[51,-160] dual=[-109,160] product=", cm_product,
       " degree=", ell, " direction=horizontal");}
{print("SUBGROUP order=", r, " tau_scalar=", lambda,
       " alpha_scalar=", alpha_scalar, " dual_scalar=", dual_scalar);}
print("COMPOSITIONS samples=", samples, " left=PASS right=PASS elapsed_ms=", elapsed_ms);
print("CLAIM_BOUNDARY=same_degree_horizontal_control_not_conductor_transfer");
print("RESULT=PASS");
RUN_COMPLETE = 1;
