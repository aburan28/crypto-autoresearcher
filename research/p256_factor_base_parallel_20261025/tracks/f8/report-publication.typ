#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F8: signed secp256k1 orbit-compressed relation matrix")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("25 October 2026. TASK-20261025-f439ca. This is an implementation and algebra control on public synthetic points. It makes no speed, generic-security, unknown-target recovery, or scaling claim. No performance trial or official state transition occurred.")
#parbreak()

#heading(level: 2)[#text("Checked objects and results")]

#text("Run from the repository root:")
#parbreak()

#text(size: 7.2pt)[#raw("python3 research/p256_factor_base_parallel_20261025/tracks/f8/orbit_matrix.py\npython3 research/p256_factor_base_parallel_20261025/tracks/f8/verify_artifacts.py", block: true)]

#text("The complete curve, standard generator, beta, scalar eigenvalue lambda, 48 points and their representative/factor map are retained in orbit_certificate.json (orbit_certificate.json). Published p=2^256-2^32-977, a=0, b=7, subgroup order r and cofactor h=1 come from the fixed baseline. No fresh primality or point-count proof is claimed. The standard generator is checked on-curve and killed by r using both affine and independent Jacobian formulas.")
#parbreak()

#text("There are eight representatives [i]G, i=1,...,8. Applying psi^j and both signs gives exactly 48 distinct points. All 48 map/eigenvalue point identities agree under the baseline affine and separately implemented Jacobian multiplication. The relation rows are the 16 additive identities [a]G+[b]G=[a+b]G for 1<=a<=b, a+b<=8, transformed by all six signed automorphisms. All 96 point sums vanish. These are constructed labelled positives; they measure neither the rate of finding ordinary relations nor their cost.")
#parbreak()

#table(columns: 5, inset: 4pt, stroke: 0.3pt + rgb("#b0bdc9"), [#text(size: 8pt, "Matrix over GF(r)")],
[#text(size: 8pt, "Columns")],
[#text(size: 8pt, "Rows")],
[#text(size: 8pt, "Custom rank")],
[#text(size: 8pt, "SymPy domain rank")],
[#text(size: 8pt, "Constructed relations R")],
[#text(size: 8pt, "48")],
[#text(size: 8pt, "96")],
[#text(size: 8pt, "42")],
[#text(size: 8pt, "42")],
[#text(size: 8pt, "Known symmetry constraints S")],
[#text(size: 8pt, "48")],
[#text(size: 8pt, "40")],
[#text(size: 8pt, "40")],
[#text(size: 8pt, "40")],
[#text(size: 8pt, "R stacked with S")],
[#text(size: 8pt, "48")],
[#text(size: 8pt, "136")],
[#text(size: 8pt, "47")],
[#text(size: 8pt, "47")],
[#text(size: 8pt, "Compressed relations RC")],
[#text(size: 8pt, "8")],
[#text(size: 8pt, "96")],
[#text(size: 8pt, "7")],
[#text(size: 8pt, "7")])

#text("The second script reloads the emitted matrix blocks, checks each full point sum and compressed coefficient row, then independently recomputes the four ranks with modular DomainMatrix arithmetic. verification.json (verification.json) identifies this as a separate implementation cross-check in the same session; no independent research review is implied. Matrix blocks split by signed automorphism retain all rows without oversized files. A false row increasing compressed rank to eight is an explicit rejection control, never an admitted relation. The conjugate scalar root and beta=2 are also rejected.")
#parbreak()

#heading(level: 2)[#text("Map, degree, subgroup action, and exceptions")]

#text("Choose beta=2^((p-1)/3) mod p and check beta!=1 and beta^2+beta+1=0. The map")
#parbreak()

#text("psi(x,y)=(beta*x,y), psi(O)=O")
#parbreak()

#text("is a degree-one automorphism over F_p: substituting gives y^2=(beta*x)^3+7=x^3+7 because beta^3=1. In projective coordinates it is (X:Y:Z)->(beta*X:Y:Z), an invertible linear projective map preserving the cubic and the identity. It therefore preserves the group law. Its inverse is psi^2; no denominator or affine exceptional point occurs. It has exact order three since beta!=1 and psi(G)!=G. Negation commutes with it and gives the six signed maps.")
#parbreak()

#text("Solve lambda^2+lambda+1=0 mod r by a modular square root of -3. There are two candidate roots; the actual acting root is identified by psi(G)=[lambda]G, checked using two scalar-multiplication implementations. Linearity then proves psi([k]G)=[lambda*k]G for every subgroup point, with no point-sampling inference. Lambda!=1 and lambda^3=1 certify order three, while -1 has order two because r is odd. Consequently {+/-lambda^j:j=0,1,2} has size six. Under the inherited prime-order assumption every nonidentity subgroup point has orbit size six: a stabilizer would imply a nonidentity scalar factor equals one mod r.")
#parbreak()

#text("This map is actual secp256k1 structure. A proposed map x->beta*x on P-256 with a=-3 would additionally need a*beta=a, forcing beta=1 when p>3. Thus this particular order-three map does not transfer to P-256. That observation excludes this formula on P-256 and does not exclude every other endomorphism construction.")
#parbreak()

#heading(level: 2)[#text("Exact compression and baseline fairness")]

#text("For representative R_i with unknown log z_i=log_G(R_i), an orbit point P_j=s_j*psi^k(R_i) has log (s_j*lambda^k)z_i. Define the 48 by 8 matrix C with one such factor in each row. For any row vector v of full-point relation coefficients, v*C is the compressed relation. This is an exact congruence over GF(r). The known symmetry constraints S say each nonrepresentative log equals its certified factor times its representative log; S has rank 40. The observations satisfy")
#parbreak()

#text("rank([S;R])-rank(S)=47-40=7=rank(RC).")
#parbreak()

#text("The apparent 42 full-column relation rank includes copies of seven independent relations on each automorphism image. It is not 42 additional independent pieces of information after symmetry is known. Compressing the eight-unknown system gives exactly seven independent relations; one scale direction remains, as it must for homogeneous relations. The known labels i of the constructed representatives are used solely to construct/check positives; there is no new logarithm oracle.")
#parbreak()

#text("The fixed factor six in unknown count is exact for this orbit-closed base. It does not grow with r. X-only or negation-quotiented storage already has 24 columns, so the additional automorphism factor there is three. No elapsed-time ratio is measured or inferred from these dimensions. Modular coefficients lambda may increase coefficient-handling work compared with signed unit entries, and canonicalizing each point evaluates/cross-compares orbit representatives; those costs remain unmeasured.")
#parbreak()

#text("Every comparator receives the same six maps, identical subgroup, and the same target/setup reuse assumptions. A conventional many-relation solver can use the identical compression matrix C; assigning it 48 unrelated unknowns would manufacture a difference. Generic rho can use the same signed automorphism action subject to its own walk/cycle and canonicalization costs. No rho runtime constant is estimated here. Fixed-base and many-target comparators must also receive matching reusable setup. This control establishes algebra and dimension accounting, not a new exponent or an advantage over those baselines.")
#parbreak()

#heading(level: 2)[#text("Failures, limitations, next decisive step")]

#text("The scientific implementation and verification commands completed without failures. Initial profile reads encountered sparse-checkout paths; the first lazy fetch failed at proxy port 8080, and reading the tracked blobs with permitted network access succeeded. During final validation the F8 verifier briefly overlapped a yielded F6 check, exceeding the handoff's one-process concurrency limit. The final checks were rerun sequentially; the procedural deviation remains recorded and no timing or performance result was collected. commands.log (commands.log) retains those outcomes.")
#parbreak()

#text("The remaining construction problem is an orbit-aware base/solver that obtains enough useful ordinary-target relations after charging construction, canonicalization, modular coefficients, root extraction, rank, and target attachment. This bundle proves none of those rates or costs. A decisive next step is a separately specified matched solver validation on independently chosen public targets: use identical orbit-closed bases and C in both arms, retain full point-sum and target-coefficient certificates, and check whether any difference remains once both receive symmetry. A difference in correctness would identify a solver bug; a verified implementation would permit a subsequent admitted cost study. No such trial was launched here.")
#parbreak()

#text("Sources: internally derived projective automorphism/group argument and linked exact certificates; published curve parameters inherited from the committed baseline. Repository endo, audit-curve and endomorphism-rules profiles were consulted. The referenced FGHR2014 paper in the historical plan is not needed for, and has not been independently retrieved as support for, these elementary derivations. The new editable diagram.svg (diagram.svg) depicts the checked quotient. Shared canonical graphs lie outside the assigned scope and were not edited. Root renders the aggregate PDF.")
#parbreak()
