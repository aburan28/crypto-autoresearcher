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

Report dated 2026-10-07, extended 2026-10-08 (§8). Study directory `research/ecc2k130_conductor_isogenies_20261007/`. Standalone study: no
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

= Analogues: m = 83, m = 109, NIST K-163 (`analogues/`)

For each conductor prime $ell'$, $pi equiv c$ on $E[ell']$, and the kernel lives in $FF_(2^(m k))$, where $k$ is the least integer with $c^k = plus.minus 1$. #D

#table(columns: (auto, auto, 1fr), inset: 5pt, stroke: 0.5pt + luma(180),
  [*Curve*], [*Prime, k*], [*Result*],
  [ECC2K-130 ($m = 131$)], [263, $k = 1$], [All 262 computed (this report). #M],
  [$m = 83$, $a = 0$], [6473, $k = 3236$], [Kernel field $FF_(2^268588)$; PARI cannot build it in 4 GB #M; about 7 weeks extrapolated #P. *Not computed.*],
  [$m = 109$, $a = 1$], [3271, $k = 5$], [6 computed in under 1 s each, 6 distinct orbits, $\#E' = N$; 23-cycle 545. #M #V],
  [NIST K-163], [45641, $k = 20$], [6 computed, about 1 min each; $\#E' = N$; 11-cycle 9128. #M #V],
  [NIST K-163], [82153, $k = 63$], [6 computed, about 15 min each; $\#E' = N$; 11-cycle 10269. #M #V],
)

ECC2K-130's 263 is unusually cheap: $k = 1$. $m = 83$ has no such prime, while K-163 has two computable ones. #D

= ECDLP consequence (scoped) and limitations

- The 263-isogenies make transferring a discrete logarithm to the 263-floor essentially free. #D
- A 263-floor curve has no Frobenius endomorphism; its cheapest non-integer endomorphism has degree $>= 7 dot 263^2 \/ 4 approx 121045$. #D
- The volcano studies at $m = 37$ and $m = 41$ measured that rho on such curves runs with negation only, $approx sqrt(m)$ times more steps than the crater with Frobenius. At $m = 131$ that predicts about $11.4 times$ more steps. That is an extrapolation, not measured here. #P

= Extensions (2026-10-08): the CM route, $m = 51 \/ 53$, a second level on K-163

Details and all run outputs are in `EXTENSIONS.md` and in the directories `cm_route/`, `survey/`, `m51_m53/` and
`second_level/`.

#figure(image("reachability.svg", width: 100%),
  caption: [Conductor levels reached on each Koblitz class, and the route used. Green: kernel route (Vélu on kernel
  points). Blue: CM route. Dotted: estimated, not completed. Grey dashed: out of reach. Source: `reachability.dot`.])

*CM route.* The $F$-floor of a Koblitz crater consists of the roots mod 2 of the class polynomial for $D = -7 F^2$. PARI
`polclass(D, 1)` uses the Weber $f$ invariant (allowed because $D equiv 1 space (mod 8)$ and $3 divides.not D$). Mod 2 the relation
$(f^24 - 16)^3 = j f^24$ becomes $j = f^48$, so each root $r$ gives $b = r^(-48)$. #D No kernel field is needed.

An earlier draft read the roots as $gamma_2$ and used $b = r^(-3)$. That labelling was wrong, but the sets were still
exact: $r^(-3) = (r^(-48))^(1\/16)$ is a Galois conjugate, and every floor is Galois-stable. The corrected scripts reproduce
the same files byte for byte. #M

- *Validation.* At $m = 37$ ($f = 73$) and $m = 41$ ($f = 409$), the root sets equal the floors enumerated by explicit
  isogenies: 74/74 and 410/410. #V
- *$m = 83$, the 6473-floor.* The kernel route needs $FF_(2^268588)$. By the CM route, `polclass` takes 20 s and gives
  6474 roots in $FF_(2^83)$, all with $\#E = N$, in 78 Galois orbits of 83. #M For the level: $"ord"[frak(l)_11] = 1079$ in
  $"Cl"(-7 dot 6473^2)$, and six 11-cycles of length 1079 tile all 6474 curves. #V
- *Survey.* The floors $m = 101$: 5857 and 18583; $m = 103$: 11329; $m = 107$: 3209 (for $a = 0$ and $a = 1$) were all computed in
  6–313 s each. Every root has a model with $\#E = N$, and the sampled 11-cycles equal $"ord"[frak(l)_11]$. #V
- *Cost.* `polclass` time grows as about $|D|^(1.2 - 1.3)$ (3 sizes, one run each), so $h approx 10^5$ is the practical
  limit here. #M

#figure(image("cm_route/polclass_scaling.svg", width: 70%),
  caption: [`polclass(D, 1)` wall time against $|D|$; one run per point; dashed: power-law fit; square: extrapolation to
  the $m = 51$ 120871-floor. Source: `cm_route/scale_polclass.out`, `cm_route/plot_scaling.py`.])

*$m = 51$ and $m = 53$.*
- At $m = 51$, $f_pi = 271 dot 120871$.
- *The 271-floor.* 271 is the conductor of $ZZ[tau^17]$, so the floor is defined over $FF_(2^17)$ (orbits of 17). #D
  Both routes compute it. CM gives 272 curves; 40 explicit 271-isogenies with kernels in $FF_(2^2295)$ all land in that
  set (40/40), reaching 14 of the 16 orbits. #V
- *The 120871-floor.* The kernel route needs $FF_(2^60435)$. The CM route needs $h = 120870$, estimated at 7–10 h.
  It was started twice, and container restarts killed it both times; no result is claimed. #P
- *$m = 53$.* $f_pi = 68476319$: the kernel route needs $FF_(2^34238159)$ and the CM route a degree-$6.8 dot 10^7$ class
  polynomial. Out of reach. #D

*Second level on K-163.* `vert_down.gp` descends from a non-crater curve. The curve's $b$ is embedded in the kernel field
through a root of the field modulus in the subfield generated by $w = z^((2^(m k) - 1)\/(2^m - 1))$.
- *Validation at $m = 41$.* From a 409-floor curve, two 1721-isogenies land on curves with 23-cycle 2870 and 11-cycle
  1722, the bottom-level values. #V
- *K-163.* From the 45641-floor curve $b' = $ `20183018253319052689704116247546275258431720285`, one 82153-isogeny
  (kernel in $FF_(2^10269)$) gives $b'' = $ `115992596105510058325208044366752339422280521227` ($a_2 = 1$, $\#E = N$). #M
- *Level of $b''$.* Its 45641-part and 82153-part are both cyclic ($ZZ\/ell'^2$), against rank 2 for both on the crater
  and rank 2 for the 82153-part on $b'$. So both primes divide the conductor of its endomorphism ring, and the conductor
  is $45641 dot 82153$. Its horizontal 11-cycle has length 82152, which is $"ord"[frak(l)_11]$ at that level (crater 1, 45641-floor 9128, 82153-floor 10269). #V A rerun with PARI's default seed reproduced $b''$ exactly. A run with a different seed gave a second, independent image, $b''' = $ `52997549064096697226797992255204505576485896783`, in another Galois orbit; it passes the same two checks (both torsion parts cyclic; 11-cycle 82152). #V

*Limits.* The CM route gives the image curves, not the isogenies themselves; no 6473-isogeny of $m = 83$ was written
down. #P

= Next checks

- Run the `audit-curve` skill on one representative from each 263-floor orbit: twist, MOV/FR, anomalous and GHS descent checks. #P
