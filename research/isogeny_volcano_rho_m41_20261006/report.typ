#set document(title: "Isogeny volcano of a Koblitz curve: Pollard rho on equal terms, m = 41", date: datetime(year: 2026, month: 10, day: 6))
#set page(paper: "a4", margin: (x: 2cm, y: 2cm), numbering: "1")
#set text(size: 10pt)
#set heading(numbering: "1.")
#show link: underline

#let st(s) = box(inset: (x: 3pt, y: 1pt), radius: 2pt, fill: luma(232), text(size: 8pt, weight: "bold", s))
#let D = st("DERIVED")
#let M = st("MEASURED")
#let V = st("INDEPENDENTLY VERIFIED")
#let P = st("PROPOSED")

#align(center, text(size: 15pt, weight: "bold")[Isogeny volcano of a Koblitz curve: Pollard rho on equal terms (m = 41)])

Report dated 2026-10-06. Study directory `research/isogeny_volcano_rho_m41_20261006/`;
this replicates `research/isogeny_volcano_rho_20261005/` (m = 37). It is a standalone study:
no `H-*`, `EV-*`, `DEC-*` or `RUN-*` record was written, and it is not a sealed `measured_bound`.
The run artifacts cited below are the files in the study directory.

Status labels: #D follows by proof or exact computation from stated facts; #M observed in this
study's runs; #V checked by a second, independent method; #P a hypothesis, not shown here.

= Question and search scope

Is any curve isogenous to the Koblitz curve $E_1: y^2 + x y = x^3 + 1$ over $FF_(2^41)$, at any level of
its isogeny volcano, better for Pollard rho when compared on equal terms (same group, solver and cost
accounting)? Search scope: the whole $a_2 = 0$ isogeny class (708,153 curves), every level, all
endomorphisms whose degree is at most $2^44$ and factors over primes $<= 43$, and the GHS descent invariant.

= Object (exact identities)

- Field $FF_2[x]/(x^41 + x^3 + 1)$; a curve $E_b: y^2 + x y = x^3 + b$ is named by the integer of its bits. #D
- $\#E = 4 dot ell$, $ell = 549756390943$ (prime, $approx 2^39$), trace $-2308219$. #D
- $[cal(O)_K : ZZ[pi]] = 409 dot 1721$, $K = QQ(sqrt(-7))$, $h(cal(O)_K) = 1$, both primes inert. #D
- Levels: crater 1 curve; 409-floor 410; 1721-floor 1,722; bottom 706,020. #D
- Embedding degree 6,704,346,231; twist order $2 dot 739 dot 2543 dot 585071$; cyclic group; $"Aut" = {plus.minus 1}$. #D

#figure(image("volcano_diagram.svg", width: 100%),
  caption: [Volcano and the isogenies used. Solid: computed here, with endpoint verified ($\#E = N$, both cycle invariants). Dashed: implied by volcano theory, not computed. Source: `volcano_diagram.dot`.])

= Methods

+ *Vertical isogenies* (`vert_lib.gp`, `v409.gp`, `v1721.gp`). Kernel generators were found by x-only López–Dahab ladders in $FF_(2^8364)$ (409, quadratic twist) and $FF_(2^8815)$ (1721, $E$). The image comes from char-2 Vélu: $b' = 1/j' = 1 + v + v^2$, with $v$ the sum of the kernel x-coordinates. #D The formula was checked against PARI `ellisogeny` on 6 random 73-isogenies at $m = 37$: 6/6 exact. #V Results: 409-floor $b = 5031829425$ and 1721-floor $b = 14893930241$, both with $\#E = N$ by `ellcard`. #M
+ *Floor enumeration* (`floors.gp`). One horizontal 29-isogeny cycle from each seed: lengths 410 and 1722, equal to $h$, giving all 410 and all 1,722 floor curves, each with $\#E = N$. #M
+ *Bottom* (`search.c`, `select.py`). A scan of $3 dot 10^8$ random $b$ gave 82 class members, all on the bottom by exclusion from the fully enumerated floors. #M
+ *Level check on all 91 sampled curves* (`chk_*.out`). $\#E = N$, plus the measured 23- and 11-cycle lengths: 1/1, 205/82, 574/861, 2870/1722. 91/91 match the class-group orders. #V
+ *Rho* (`rho.c`, `params.h`). van Oorschot–Wiener distinguished points, $theta = 2^(-5)$, a 128-adding walk with look-ahead and cycle escape; every group operation after $Q$ is known is counted; every solve is verified against the secret and by recomputing $[k]P = Q$. Samples: 3,000 solves of the crater in each mode, and 200 on each of 30 curves per lower level. #M

= Results

#figure(image("volcano_rho_study.png", width: 100%),
  caption: [Mean group operations per curve (95% CI), level ratios against the crater (90% CI, ±3% band), cost per step, available endomorphisms, and the modelled best class speedup. Data: `results.json`, `data/raw_solves.tar.gz`, `data/raw_idle.tar.gz`; sample sizes in panels.])

*Positive or negative?* Negative for the question as posed: no curve below the crater is better.

- All 24,000 solves verified. #M
- *Negation only, steps.* No level effect (Kruskal–Wallis $p = 0.76$; ANOVA on curve means $p = 0.83$). Ratios against the crater, with 90% CIs: 409-floor 1.001 [0.983, 1.021], 1721-floor 1.005 [0.986, 1.024], bottom 0.998 [0.980, 1.017]. All equivalent within ±3% by TOST. #M
- *Main-run time:* also equivalent within ±3% (0.997, 1.000, 0.992; $p = 0.52$). *Cost per step:* within 0.4% ($p = 0.50$). #M
- *Frobenius on the crater:* 6.36× fewer steps [6.20, 6.53], against $sqrt(41) = 6.40$, and 3.0× less time. No curve is faster than crater + Frobenius (Holm-adjusted $p = 1.0$, all 91 curves). #M
- *Endomorphisms.* $tau^k in "End"$ only for $41 | k$ below the crater. #D The minimal non-integer endomorphism degree is 2 (crater), 292,742 (409-floor), 5,183,222 (1721-floor) and $8.7 dot 10^11$ (bottom). #D The smallest orbit from any smooth endomorphism is 41 (crater, $tau$), then $6.8 dot 10^7$, $6.8 dot 10^7$ and $6.7 dot 10^9$. #D With the stated cost model, the best class speedup is 2.31× (crater) and $<= 6 dot 10^(-5)$× below it. That cost model is #P, not measured.
- *GHS:* $m(b) = 1$ at the crater and 41 on all 90 sampled lower curves. #D

= Contradictions and limitations

- *Phase 3 (idle-machine timing) is inconclusive.* Its time ratios were 0.929 [0.874, 0.985], 1.000 [0.941, 1.063] and 0.964 [0.910, 1.022]; the CIs exceed ±3%. Splitting the time into factors, cost per operation is equal within 0.2%, and the 409-floor deviation is step-count noise: its 600 solves needed 7.3% fewer steps, while 6,000 main-run solves give 1.001. #M That phase was underpowered, at 300–600 solves per arm.
- At $m = 37$ a load confound caused a timing failure, which an amendment then resolved. It did not recur here: nothing else ran during the timed phases. #M
- *Pre-data bugs, all caught by built-in checks:* a `Q2[]` table overflow in `rho.c` (the verifier rejected the solves); a Frobenius-power error and a root-finding type error in `vert.gp`. See `PRE_DATA_FIXES.md`, which also corrects an overstated sentence in the frozen `PROTOCOL.md`.
- *Scale:* $m = 41$, this solver, this machine. Transfer to ECC2K-130 ($m = 131$, conductor $263 dot 146505763881528721$) rests on exact facts, not on measurement: the class shares $ell$; $"Aut" = {plus.minus 1}$ throughout; $h(cal(O)_K) = 1$ places $tau$ only at the crater; and non-integer endomorphisms in $ZZ + f cal(O)_K$ have degree $>= 7 f^2 \/ 4$. #D

= Next checks

- Rerun phase 3 with about 3,000 solves per arm, so the time intervals reach ±3%. #P
- Re-express this result as a sealed `measured_bound` (constant with an interval) through the harness in `aburan28/crypto`, if a Coordinator wants it in the evidence record. #P
- Carry the GHS and endomorphism-orbit computations to the ECC2K-130 class itself; they are exact and need no rho runs. #P
