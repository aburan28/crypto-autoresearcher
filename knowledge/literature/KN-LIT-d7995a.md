---
id: KN-LIT-d7995a
type: literature
title: "Weak Fields for ECC (Menezes, Teske, Weng) -- full read: exact GHS-versus-rho accounting for F_{2^{5l}}, F_{2^{4l}} and F_{2^{210}}, and the isogeny-walk extension"
authors:
  - "Alfred Menezes"
  - "Edlyn Teske"
  - "Annegret Weng"
year: 2004
venue: "Topics in Cryptology -- CT-RSA 2004, LNCS 2964, pp. 366-386; IACR ePrint 2003/128 (posted 2003-06-27)"
identifiers:
  eprint: "iacr:2003/128"
  doi: "10.1007/978-3-540-24660-2_28"
  arxiv: null
  url: "https://eprint.iacr.org/2003/128"
tags: [weak-fields, ghs, weil-descent, binary-field, composite-degree, magic-number, enge-gaudry, index-calculus, hyperelliptic, isogeny-walk, galbraith-hess-smart, hess, pollard-rho, exact-analysis, ecdlp, f2-210, f2-161, oakley]
confidence: reported
citation_verified: read
added: "2026-10-09"
superseded_by: null
supersedes: KN-LIT-fa389d
---

## What this entry is

A full read of the ePrint version (2003/128, the only free copy; the PDF is
behind a bot wall, the PostScript is not) on 2026-10-09, with the authors'
ECC 2003 slides as a cross-check. It replaces the abstract-only stub
KN-LIT-fa389d. Every number below is the paper's own; nothing is re-derived
here except where marked. The companion paper on Hess' generalized GHS attack
is KN-LIT-f64d86; the 2018 proof of this paper's Conjecture 15 is
KN-LIT-fc822d. Sources are vendored under `inputs/MTW-WEAK-FIELDS-20261009/`.

## Definitions (Section 1)

- **Bad field** (Def. 1): rho is intractable for some curves over F_q, *and*
  known algorithms feasibly solve every ECDLP instance for every curve over
  F_q. "No bad fields for ECC are presently known."
- **Weak field** (Def. 2): rho is intractable for some curves, *and* known
  algorithms solve every instance for every curve over F_q in significantly
  less time than rho needs on the hardest instances. "Significantly less" is
  deliberately left unquantified; the paper's own yardstick is the sqrt(N)
  Koblitz-curve speedup (factor 13 at N = 163, 17 at N = 283), which it
  wants to beat by a wide margin.
- Subfield curves (coefficients in F_{2^l}) are excluded throughout: for them
  #E(F_{2^l}) | #E(F_{2^N}) and rho already runs in 2^{(N-l)/2}.

## Main claims

1. **F_{2^N} with N in [185, 600] and 5 | N is weak** (Section 3; "debatable"
   at N = 185, Remark 5(ii), the OAKLEY field).
2. **F_{2^210} is particularly weak** (Section 5): every curve 2^13 faster than
   the hardest rho instance; a quarter of all curves (Tr(a) = Tr(b) = 0,
   equivalently 8 | #E) 2^20 faster; so a curve over F_{2^210} with order
   twice a prime has a security level of at most 91 bits, not 104, the same
   as a curve over F_{2^183}.
3. **F_{2^600}: 2^69 faster**, so at most 230 bits of security.
4. **F_{2^N} with 4 | N shows "some signs of being weak"** but far less than
   5 | N (Section 4).
5. Candidate bad field: **F_{2^161}** (Section 6), if an isogeny into its
   2^94 GHS-weak classes could be found. "No such mapping is known."

## Section 3: N = 5l, exact accounting

Setting: N = 5l, q = 2^l, l in [32, 120]. x^5 + 1 = (x+1)(x^4+x^3+x^2+x+1)
over F_2, so a non-subfield curve y^2 + xy = x^3 + a x^2 + b has magic
number m = 5 (Menezes-Qu, Cor. 9) and the GHS reduction yields a
hyperelliptic C/F_{2^l} of genus 15 or 16.

- **Theorem 3.** Exactly 2^{4l+1} - 2 isomorphism classes of curves over
  F_{2^N} \ F_{2^l} give genus 15: those with Tr_{F_{2^N}/F_{2^l}}(b) = 0,
  equivalently Ord_b(x) = x^4+x^3+x^2+x+1. All other
  2^{N+1} - 2^{l+1} - (2^{4l+1} - 2) classes give genus 16, so genus 16 is
  "the vast majority" and the analysis is done for g = 16.
- **Rho.** Hardest instances have #E = 2r; T = 2^{(N-1)/2} = 2^{2.5l - 0.5}
  steps (Teske's walk; Teske 2000 Cor. 5.1 makes the asymptotic formula
  accurate at fixed r). Mixed-coordinate addition = 8 multiplications in
  F_{2^N}, so R ~ tau_N * 2^{2.5(l+1)}.
- **Enge-Gaudry, smoothness bound t = 1.** Factor base w ~ 2^{l-1}
  degree-one prime divisors. 1-smooth divisors ~ q^g / g! (Lemma 4 gives the
  exact count; they checked q^g/g! is accurate for every l in [32, 120]).
  Relation stage T1 = w * #J / M(1) ~ 2^l * g! = 2^{l+43} for g = 16, each
  step dominated by the smoothness test (u^{2^l} mod a, (128 l - 288)
  F_{2^l}-multiplications; NUCOMP Jacobian addition is cheaper, Jacobson:
  tau_S ~ 2.3 tau_J at l = 37). So R1 ~ (128 l - 288) * tau_l * 2^{l+43}.
  Lanczos on the ~2^{l-1}-dimensional sparse system with ~g entries per row:
  T2 ~ g w^2 = 2^{2l+2} multiplications mod r, R2 ~ tau_r * 2^{2l+2}.
- **Relative timings** (Hankerson, Pentium II 400 MHz, 2003; NTL gives
  tau_N/tau_l ratios 2.3 to 10.5 instead, Remark 5(i)). Table 1, time unit
  = one F_{2^l}-multiplication:

  | N | l | tau_N | tau_r | log2 R (rho) | log2 R1 (relations) | log2 R2 (matrix) |
  |---|---|---|---|---|---|---|
  | 160 | 32 | 7.7 | 5.8 | 85.5 | 87 | 69 |
  | 185 | 37 | 7.9 | 5.8 | 98 | 92 | 79 |
  | 210 | 42 | 10.3 | 8.0 | 110.5 | 97 | 89 |
  | 255 | 51 | 11.0 | 7.7 | 133 | 107 | 107 |
  | 385 | 77 | 15.0 | 9.4 | 199 | 133 | 160 |
  | 515 | 103 | 15.3 | 11.1 | 264 | 160 | 212 |
  | 600 | 120 | 17.7 | 12.5 | 306.5 | 177 | 246 |

- **Factor-base thinning** (Remark 5(iii)): keeping 1/2^d of the degree-one
  divisors divides R2 by 2^{2d} and multiplies R1 by 2^{d(g-1)}. Balanced
  choices: (N, d) = (385, 1.5): R1 = 2^{155.5}, R2 = 2^{157}; (515, 3):
  2^{205}, 2^{206}; (600, 4): 2^{237}, 2^{238}, which is the 2^69 claim.
- The ECC 2003 slides tabulate the resulting speedup delta and the field size
  N_equiv whose hardest rho instance costs the same: N = 185: 2^6 (173);
  210: 2^13 (183); 255: 2^26 (202); 385: 2^39 (309); 515: 2^52 (412);
  600: 2^60 (479); with thinning 385: 2^42 (302), 515: 2^58 (401),
  600: 2^68.5 (463).
- Caveat the paper itself raises (Section 3.3): the comparison counts time
  only. Rho parallelizes with no communication; relation generation does
  too; the matrix stage is not known to, and its storage may be the real
  bottleneck. They lean on Bernstein/Wiener's D^{7/3+o(1)} full-cost result
  for sparse linear algebra and call the time-only comparison "adequate",
  more so when tau_r T2 << tau_E T.

## Section 4: N = 4l

Non-subfield curves descend to genus 7 or 8 (mostly 8). R ~ tau_N
2^{2l+2.5}, R1 ~ tau_l (32 l - 48) 2^{l+14}, R2 ~ tau_r 2^{2l+1}: rho and the
matrix stage nearly coincide, so thinning (R2 / 2^{2d}, R1 x 2^{7d}) is
needed. Table 2 (units as printed: tau_N, tau_l, tau_r respectively):
(N, l, d; R, R1, R2) = (160, 40, 2; 2^82.5, 2^78, 2^77), (192, 48, 3;
2^98.5, 2^94, 2^91), (224, 56, 4; 2^114.5, 2^109, 2^104), (256, 64, 5;
2^130.5, 2^124, 2^119), (384, 96, 8; 2^194.5, 2^178, 2^177), (512, 128, 12;
2^258.5, 2^238, 2^233), (600, 150, 14; 2^302.5, 2^274, 2^273). Verdict:
"some signs of being weak, but not as weak as the fields F_{2^{5l}}".
(Smart 2001 had given experimental evidence for 4 | N.)

## Section 5: F_{2^210} with (n, m) = (6, 5)

- About 2^175 isomorphism classes have magic number 5 relative to n = 6
  (l = 35). The GHS reduction needs Tr(a) = 0 here (Maurer-Menezes-Teske
  Lemma 8, Hess), so E: y^2 + xy = x^3 + b with b in F_{2^210} \ F_{2^35}.
  Exactly 2^140 - 2^70 of these give genus 15 (t(x) = x^4 + x^2 + 1), and
  (2^140 - 2^70)(2^35 - 1) ~ 2^175 give genus 16. For g = 16: w ~ 2^34,
  R1 ~ tau_35 2^90, R2 ~ tau_r 2^72.
- **Theorem 6.** 6 | N and m = 5 relative to n = 6 imply Tr_{F_{2^N}/F_2}(b)
  = 0 (Ord_b = (x-1)^j (x^2+x+1)^2, j in {0, 1}).
- **Lemma 7** (proved from the 8-division polynomial, "probably well known"):
  for y^2 + xy = x^3 + b over F_{2^N}, N >= 3: Tr(b) = 0 iff 8 | #E(F_{2^N}).
- **Corollary 8.** Every (6, 5) curve over F_{2^210} has 8 | #E.
- **Assumption A.** A curve drawn uniformly from the endomorphism class of
  E = E_{0,b} with 8 | #E has (6, 5) with probability 2^175 / 2^209 = 2^-34.
  Remark 9 generalizes: q^5 - q^3 classes with (6, 5) among 2^{N-1} with
  Tr(b) = 0 gives 2^-(N/6 - 1); "confirmed in extensive experiments" for
  36 <= N <= 84. Remark 10: fails only when the class group is tiny
  (Delta < 2^150 affects at most 1/2^63 of curves; Delta < 2^100 at most
  1/2^113; a conductor f >~ 2^30 is "most unlikely for non-subfield
  curves").
- **Isogeny walk** (Galbraith-Hess-Smart 2002 machinery): Kohel's algorithm
  to the maximal order first (O(s^3), s the largest conductor prime,
  negligible in practice); then a pseudo-random walk on the class group via
  the 30 smallest split primes with pairwise distinct ideal-class pairs.
  Over 5000 random discriminants max p in [190, 530] (only 2 above 500;
  [150, 380] with 20 primes). Root-finding in Phi_p(j, X) costs ~210 * 500^2
  ~ 2^26 F_{2^210}-operations per step, so 2^34 steps ~ 2^60 operations,
  parallelizable, negligible against R1, R2. Making the isogeny explicit
  (GHS stages 2-3, Velu) is O(2^{N/4+eps}) ~ 2^53.
- **Section 5.3, Hess' generalized GHS for Tr(a) = 0.** With b = (gamma_1
  gamma_2)^2, s_i = deg Ord_{gamma_i}, t = deg lcm, Hess gives a curve C
  (in general not hyperelliptic) of genus 2^t - 2^{t-s_1} - 2^{t-s_2} + 1.
  Ord_{gamma_1} = Ord_{gamma_2} = x^4+x^2+1 gives genus 15; Ord_{gamma_1} =
  x^2+x+1 gives genus 12. **Algorithm 11** decides whether such a
  decomposition exists: solve w(u) = u^2 + (beta^{q^4-1} + beta^{q^2-1} +
  1) u + beta^{q^2-1} over F_{q^6} (beta = b^{1/2}), keep a root with
  u^{q^2+1} + u + 1 = 0, take a (q^2-1)-th root (Lemma 12; one finite-field
  DLP, run once per attack). Theorem 13 proves soundness and completeness.
  Lemma 14 characterizes the genus-12 case (a root of order dividing
  q^2+q+1). **Conjecture 15**: if w(u) has two roots in F_{q^6} they both
  satisfy u^{q^2+1} + u + 1 = 0 (Lemma 16 proves it for the second root
  given the first). Table 3: for each N in {30, 36, 42, 48, 54, 60, 114,
  120, 126, 204, 210, 216, 222}, of 10000 random beta about half (4924 to
  5100) make w solvable and every solvable case satisfied the conjecture;
  genus-12 cases were 6 to 72 at N <= 60 and 0 at every N >= 114. So about
  half of all curves with Tr(a) = 0 reduce to genus 15 (or 12) directly,
  and with the walk "this reduction should be possible for any elliptic
  curve over F_{2^N} with Tr(a) = 0"; no exact cost analysis is given for
  the non-hyperelliptic Jacobian.
- **Table 4** (F_{2^210}, unit = F_{2^l}-multiplication): n = 5, l = 42:
  (R, R1, R2) = (2^110.5, 2^97, 2^89); n = 6, l = 35: (2^110.5, 2^90, 2^75).
  Hence 2^13 for all curves, 2^20 for the quarter with Tr(a) = Tr(b) = 0,
  "presumably" faster for the quarter with Tr(a) = 0, Tr(b) = 1.

## Section 6: conclusions and open problems

- Fundamental open problem: is any field bad? F_{2^210} is "a prime
  candidate".
- F_{2^161}: 2^94 of the 2^162 isomorphism classes descend to genus 7 or 8
  over F_{2^23}; R = tau_E 2^80, R1 = (tau_J + tau_S) 2^37, R2 = tau_r 2^47.
  A mapping from an arbitrary curve into those classes would make the field
  bad; none is known (cf. Teske's trapdoor, ePrint 2003/058, which is the
  constructive reading of the same gap).
- Faster HCDLP than Enge-Gaudry, even by constants (sieving), matters here.
- Weak fields for genus-2 HECC (Galbraith's Weil descent of Jacobians) are
  open.

## Key claims: verified versus reported

| Claim | Status here |
| --- | --- |
| Theorem 3 count 2^{4l+1} - 2 and the Ord_b characterization | Read; proof is three lines from Menezes-Qu Cor. 6 and Cor. 8, not re-run. |
| Enge-Gaudry cost formulas (7), (5) and Table 1 | Read; depend on 2003 timing ratios. The structure (2^{l+43} relations, 2^{2l+2} Lanczos) is checkable; the tau ratios are not reproducible today. |
| Lemma 7 (Tr(b) = 0 iff 8 divides the order) | Read with proof; elementary and checkable at toy size. |
| Assumption A / 2^-34 | Heuristic, experimentally supported by the authors at 36 <= N <= 84 only. |
| 2^26 per walk step, 2^60 total, 2^53 explicit isogeny | Read; order-of-magnitude. |
| Conjecture 15 | Proved by Mesnager-Kim-Choe-Tang (KN-LIT-fc822d). |
| "No bad field is known" | 2003 statement; still the position of KN-LIT-f64d86 (2004/2005). Later work (Hess' generalization, Gaudry-Thome genus 3, Diem) tightens costs but no field has been declared bad in the corpus. |

## Relevance to this program

- **Which fields are touched.** Of the binary fields this program measures or
  cites, F_{2^131} (ECC2K-130), F_{2^113} and F_{2^163} are prime degree and
  untouched by this paper (see Menezes-Qu). The X9.62 c2pnb176w1 /
  c2pnb208w1 / c2pnb272w1 / c2pnb304w1 / c2pnb368w1 fields have N = 16 * 11,
  16 * 13, 16 * 17, 16 * 19, 16 * 23: 4 | N and 8 | N, but the curves are
  defined over F_{2^16}, and a subfield curve is not weakened by GHS at
  all (Maurer-Menezes-Teske Remark 21, KN-LIT-0e854b); the program's
  "c2pnb176w1 fell at m' = 5" claim is not in any Menezes-Teske paper, see
  the correction in KN-LIT-0e854b. F_{2^161} = F_{2^{7 * 23}}, Teske's trapdoor field
  (KN-TECH-8ef4c3), gets the exact numbers above. OAKLEY's F_{2^185} =
  F_{2^{5 * 37}} is the marginal case.
- **Rates for the I-3 class screens** (aburan28/crypto,
  `research/isogeny_class_difficulty_20261008/PROTOCOL-I3-class-screens.md`,
  prediction Q1 "within a factor 2 of the Menezes-Teske rate for that (n, l)
  shape"). This paper fixes the n = 5 and n = 6 shapes; the companion fixes
  n = 3, 7, 8 (KN-LIT-f64d86):
  - n = 5: *no class variation*. Every non-subfield curve already has m = 5;
    the screen `min m(b)` is constant 5 on every node that is not a subfield
    curve, and the genus-15 subset has density 2^{4l+1}/2^{N+1} = 2^{-l}.
  - n = 6: the (6, 5) family has density 2^{-(l-1)} inside the
    8 | #E classes (Tr(a) = 0 required), and density 0 in classes with
    #E not divisible by 8 (Theorem 6 + Lemma 7). A screen that ignores the
    order mod 8 will see a bimodal rate.
  - A screen that only reads Ord_b (the GHS magic number) is blind to every
    Hess-decomposition family (genus 12 and 14 at n = 6, genus 7 and 14 at
    n = 7, genus 24 at n = 8): those need the Algorithm 11 / Algorithm 8
    quadratic test, not Ord_b.
- **The isogeny-walk cost model** is the one the program's weak-curve
  methodology prices as T(E -> E'): expected 2^v steps at ~N * p_max^2
  F_{2^N}-operations per step with 2^{-v} the density of the weak family in
  the class, plus O(2^{N/4}) to make the isogeny explicit. The program's
  `binary_isogeny` walker (aburan28/crypto `src/cryptanalysis/ghs_full_attack.rs`)
  implements the j-invariant walk but not the explicit Velu step, which is
  exactly the stage this paper prices at 2^{N/4+eps}.
- **Trapdoor and KKM links.** KN-LIT-0cb87e's "eps ~ 2^-58" for a random
  curve over F_{2^{3*59}} is the n = 3 density from the companion paper, not
  this one. KN-TECH-8ef4c3's F_{2^161} parameters are Section 6 here.

## Limits of applicability

- Binary fields only, composite N only, l >= 32 for the exact tables.
- All speedups are relative to the hardest rho instance over the *same*
  field and count time, not memory or full cost.
- Timing ratios are 2003 software on one platform; the exponents (2^{l+43},
  2^{2l+2}, 2^{2.5l+2}) are the durable content.
- Weak is not bad: at N = 210 the attack still costs ~2^90 to 2^97
  F_{2^35}- or F_{2^42}-multiplications.
- The generalized-GHS half of Section 5.3 has no cost analysis for the
  non-hyperelliptic Jacobian; Menezes-Teske later make Assumptions A and B
  explicit for that (KN-LIT-f64d86).

## Provenance

Retrieved 2026-10-09. eprint.iacr.org served a Cloudflare challenge for the
HTML and PDF URLs (HTTP 403 via WebFetch, challenge page via curl), but
`https://eprint.iacr.org/2003/128.ps.gz` returned the uncompressed
PostScript (232,811 bytes). Converted with Ghostscript 10.02.1 (`ps2pdf`)
and `pdftotext -layout`; the Type-3 fonts drop the letters "c", "ff", "fi",
"fl" from the extraction ("ellipti urve" = "elliptic curve"), so the text
file is for search only and the PostScript is the record. The ECC 2003 slide
deck (`cacr.uwaterloo.ca/conferences/2003/ecc2003/teske.ps`) was read the
same way and agrees with the paper on every number quoted. Bibliographic
metadata (LNCS 2964, pp. 366-386, DOI) from the companion paper's reference
[18] and the Springer search record; the Springer page itself redirected to
an authorization wall and was not read. Full retrieval record:
`inputs/MTW-WEAK-FIELDS-20261009/provenance.json`.

## Local copies

- `inputs/MTW-WEAK-FIELDS-20261009/sources/mtw-eprint-2003-128.ps` (original bytes) and `.txt` (lossy extraction)
- `inputs/MTW-WEAK-FIELDS-20261009/sources/teske-ecc2003-weak-fields-slides.ps` and `.txt`
