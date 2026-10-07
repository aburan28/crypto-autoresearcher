#set document(title: "Conductor-changing prime-degree isogenies of ECC2K-130", date: datetime(year: 2026, month: 10, day: 7))
#set page(paper: "a4", margin: (x: 2cm, y: 2cm), numbering: "1")
#set text(size: 10pt)
#set heading(numbering: "1.")

#let st(s) = box(inset: (x: 3pt, y: 1pt), radius: 2pt, fill: luma(232), text(size: 8pt, weight: "bold", s))
#let D = st("DERIVED")
#let M = st("MEASURED")
#let V = st("INDEPENDENTLY VERIFIED")
#let P = st("PROPOSED")

#align(center, text(size: 15pt, weight: "bold")[Conductor-changing prime-degree isogenies of ECC2K-130])

Report dated 2026-10-07. Study directory `research/ecc2k130_conductor_isogenies_20261007/`. Standalone study: no
`H-*`, `EV-*`, `DEC-*` or `RUN-*` record was written. Run artifacts are the `.out` files in the directory.
Labels: #D proof or exact computation from stated facts; #M observed in this study's runs; #V confirmed by a second,
independent method; #P a hypothesis, not shown here.

= Question and scope

Which prime-degree isogenies from ECC2K-130 change the conductor of the endomorphism ring, and which of them can be
computed? The scope is the whole $a_2 = 0$ isogeny class over $FF_(2^131)$, all prime degrees.

= Object

- $E: y^2 + x y = x^3 + 1$ over $FF_2[x] \/ (x^131 + x^8 + x^3 + x^2 + 1)$. A curve $E_b$ is named by the integer of the bits of $b$. #D
- $\#E = 4 ell$ with $ell = 680564733841876926932320129493409985129$ prime; the trace is $-22283658519494248867$. #D
- $"End"(E) = cal(O)_K$ with $K = QQ(sqrt(-7))$ and $h = 1$. The Frobenius conductor is $f_pi = [cal(O)_K : ZZ[pi]] = 263 dot 146505763881528721$; the prime 263 splits and the other is inert. #D

#figure(image("volcano_ecc2k130.svg", width: 100%),
  caption: [The isogeny class by level. Solid: computed here, with endpoints verified. Dashed: exists by theory but cannot be computed. Source: `volcano_ecc2k130.dot`.])

= Which prime degrees can change the conductor

An $ell$-isogeny between ordinary curves changes the conductor by a factor of at most $ell$, and can change it only if $ell | f_pi$ (Kohel). Every other prime degree gives a horizontal isogeny, with conductor ratio 1. Here that leaves exactly two degrees: *263* and *146505763881528721*. #D

= The 263-isogenies (computed)

- $pi equiv -1 space (mod 263)$, so $E[263]$ is $FF_q$-rational on the quadratic twist $E_t: y^2+x y=x^3+x^2+1$, with the same x-coordinates. No extension field is needed. #D
- $\#E_t = 2 dot 263^2 dot 19678316408850118605767852657510239$ and $E_t (FF_q) ≅ ZZ\/(\#E_t \/ 263) times ZZ\/263$, so $E_t [263]$ is all rational. #M
- All 264 kernels, via char-2 Vélu ($b' = 1 + v + v^2$, checked 6/6 against PARI `ellisogeny` at $m = 37$):
  - 2 map back to $E$. These are the horizontal isogenies; since 263 splits and $h = 1$, they are endomorphisms. #M
  - 262 give 262 distinct curves, the whole 263-floor ($h(cal(O)_263) = 262$). Every one has $\#E = N$ by `ellcard`. #M
- *Level checks.* Each image's twist has a cyclic $ZZ\/263^2$ 263-part (262/262), against $(ZZ\/263)^2$ on the crater. The horizontal 11-isogeny cycle has length 131 (262/262), equal to $"ord"[frak(l)_11]$ in $"Cl"(-7 dot 263^2)$; on the crater it is 1. #V
- The 262 curves form 2 Galois orbits of 131, with representatives $b' =$ `0x3415808f755dad3868860b0a0fb8103` and `0xa05d3c82ee7321154f4f4fd13cea070` ($a_2 = 0$). #M

= The 146505763881528721-isogenies: why they cannot be computed

All $ell + 1 = 146505763881528722$ of them exist and descend. #D Every route to one is out of reach:

#table(columns: (auto, 1fr), inset: 5pt, stroke: 0.5pt + luma(180),
  [*Route*], [*Barrier*],
  [Kernel points (Vélu, √élu)], [$pi equiv c space (mod ell)$, with $"ord"(c) = 1.22 dot 10^16$ and $-1 in ⟨ c ⟩$. The kernel x-coordinates first appear in $FF_(2^(131 k))$ with $k = 6104406828397030$, where one element takes $8.0 dot 10^17 approx 2^59.5$ bits. #D],
  [Kernel polynomial over $FF_(2^131)$], [Degree $(ell - 1)\/2 = 7.3 dot 10^16$; about 1.2 EB just to store. #D],
  [Modular polynomial $Phi_ell (1, Y)$], [Degree $ell + 1 approx 1.5 dot 10^17$, with integer coefficients of order $ell log ell$ bits. #D],
  [CM / Hilbert class polynomial], [Discriminant $-7 ell^2$, degree $h = 1.5 dot 10^17$. #D],
  [Random search for an image], [A random $b$ lands on that floor with probability $2^(-74)$. #D],
  [√élu], [About $sqrt(ell) approx 2^28.5$ operations, but each is in the $2^59.5$-bit field. #D],
)

Every route costs at least about $2^56$. Pollard rho on ECC2K-130 with Frobenius costs about $2^60.8$, so just writing one of these isogenies down costs about as much as solving the discrete logarithm. The same barrier holds for the $ell$-isogenies from the 263-floor and for every curve at the bottom: a random $b$ lies in the class at all with probability $2^(-66)$, and every route from a known curve passes through an $ell$-isogeny. #D

= ECDLP consequence (scoped) and limitations

- The 263-isogenies make transferring a discrete logarithm to the 263-floor essentially free. #D
- A 263-floor curve has no Frobenius endomorphism; its cheapest non-integer endomorphism has degree $>= 7 dot 263^2 \/ 4 approx 121045$. #D
- The volcano studies at $m = 37$ and $m = 41$ measured that rho on such curves runs with negation only, $approx sqrt(m)$ times more steps than the crater with Frobenius. At $m = 131$ that predicts about $11.4 times$ more steps. That is an extrapolation, not measured here. #P

= Next checks

- Run the `audit-curve` skill on one representative from each 263-floor orbit: twist, MOV/FR, anomalous and GHS descent checks. #P
