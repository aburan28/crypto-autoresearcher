---
id: KN-LIT-f64d86
type: literature
title: "Cryptographic implications of Hess' generalized GHS attack (Menezes, Teske) -- full read: which F_{2^{nl}} are (potentially, partially) weak, with the vulnerable families, membership tests, walk lengths and cost tables for n = 3, 6, 7, 8"
authors:
  - "Alfred Menezes"
  - "Edlyn Teske"
year: 2005
venue: "Applicable Algebra in Engineering, Communication and Computing 16(6) (2005/2006) 439-460; CACR technical report CORR 2004-25 (dated 2004-09-08); IACR ePrint 2004/235"
identifiers:
  eprint: "iacr:2004/235"
  doi: "10.1007/s00200-005-0186-8"
  arxiv: null
  url: "https://cacr.uwaterloo.ca/techreports/2004/corr2004-25.pdf"
tags: [weak-fields, ghs, generalized-ghs, hess, weil-descent, binary-field, composite-degree, isogeny-walk, galbraith-hess-smart, enge-gaudry, gaudry-thome, genus-3, genus-7, genus-12, genus-14, genus-24, non-hyperelliptic, ecdlp, f2-210]
confidence: reported
citation_verified: read
added: "2026-10-09"
superseded_by: null
supersedes: KN-LIT-3305
---

## What this entry is

A full read of the CACR technical-report copy (CORR 2004-25, 22 pages) on
2026-10-09. It replaces the bulk stub KN-LIT-3305, which was built from the
first two pages. The DOI and journal volume are from the stub KN-LIT-fa389d
(verified on the web on 2026-09-26) and from the program's existing
citations; the journal version itself was not read, so section numbers below
are the technical report's. The source is vendored under
`inputs/MTW-WEAK-FIELDS-20261009/`. The paper it extends is KN-LIT-d7995a.

## Vocabulary (Sections 1 and 3.3)

- **Weak** (as in KN-LIT-d7995a): every ECDLP instance for every curve over
  the field in significantly less time than rho on the hardest instances.
- **Potentially weak**: weak under Assumptions A and B below, which stand in
  for the unknown cost of arithmetic and index calculus on Hess'
  non-hyperelliptic curves.
- **(Potentially) partially weak**: the same for a non-negligible proportion
  of all curves, "something like one-half or one-quarter".
- **Assumption A**: a Jacobian addition on a generalized-GHS curve costs
  about what it costs on a hyperelliptic curve (Hess' algorithm is O(g^4)
  versus Cantor's O(g^2) field operations). **Assumption B**: solving the
  DLP there costs about what Enge-Gaudry costs on a hyperelliptic curve of
  the same genus. Remark 5: the conclusions survive even if the
  non-hyperelliptic algorithms are "several orders of magnitude slower".
- **Assumption C**: if a vulnerable family W has density 2^-v in the union X
  of the isogeny classes it meets, then it has density 2^-v in each
  endomorphism class (fails only for tiny class groups, Remark 6).
- Subfield curves are excluded; curves are E_{a,b}: y^2 + xy = x^3 + a x^2 +
  b with a in {0, alpha}, Tr(alpha) = 1; E_0 (Tr(a) = 0) and E_1 (Tr(a) = 1)
  each hold half of the 2(q^n - 1) isomorphism classes.

## The generalized GHS reduction (Section 2)

For b = (gamma_1 gamma_2)^2, s_i = deg Ord_{gamma_i} (Ord = minimal
polynomial of the q-Frobenius acting on gamma_i), t = deg lcm(Ord_{gamma_1},
Ord_{gamma_2}[, X+1 if Tr(a) = 1]), and, when Tr(a) = 1, the extra condition
that Tr_{K/k}(gamma_1) or Tr_{K/k}(gamma_2) is nonzero, Hess constructs
phi: E(K) -> J_C(k) with

    g = 2^t - 2^{t-s_1} - 2^{t-s_2} + 1.

Remark 2: gamma_1 = 1, gamma_2 = b^{1/2} recovers GHS, hyperelliptic of
genus 2^{m-1} or 2^{m-1} - 1 with m the magic number (deg Ord_b, plus 1 if
(X+1) does not divide Ord_b). Remark 3: one needs g >= n since #J ~ q^g must
contain the order-r subgroup, r ~ q^n; t <= n so g <= 2^n - 1. Theorem 1
(from KN-LIT-d7995a) gives the existence and the count
#B = Phi(m_1) Phi(m_2) / (q - 1) of products gamma_1 gamma_2 with prescribed
orders, and a constructive decomposition via relative traces.

## Cost model (Sections 3 and 4), units as stated

- Rho: R_rho ~ 2^{0.5(N+5)} (2^{(N-1)/2} steps x 8 F_{2^N}-multiplications,
  tau_N dropped).
- Enge-Gaudry relation stage: R_RG ~ g^2 l q g!/4 (smoothness test ~ g^2 l/2
  F_{2^l}-multiplications per step, q g!/2 steps). Linear algebra:
  R_LA ~ g q^2/4 (Lanczos, mod-r multiplications).
- Isogeny walk: Kohel to the maximal order (negligible); then a walk on the
  class group with the 16 smallest split primes with pairwise distinct ideal
  classes; over 20000 random discriminants max p < 313, so one step costs
  about N p_max^2 / 3 ~ N 2^15 K-operations; with 2^v expected steps,
  R_W = N 2^{v+15}. Explicit isogeny via GHS stages 2-3: O(2^{N/4+eps}),
  always below R_W here, ignored. Remark 7: more than half of the
  discriminants need only p <= 157 (factor 3.6 cheaper); Karatsuba root
  finding another ~10x on the larger primes.

## Results by descent degree

### n = 7 (Section 5): F_{2^{7l}} potentially partially weak

X^7 + 1 = (X+1)(X^3+X+1)(X^3+X^2+1). W_0 = curves in E_0 with b = (gamma_1
gamma_2)^2 and Ord_{gamma_1} = Ord_{gamma_2} = X^3+X+1 (or both X^3+X^2+1):
s_1 = s_2 = t = 3, **genus 7**, #J ~ #E. Algorithm 8 decides membership and
produces the decomposition: solve the quadratic w(u) = u^2 + (beta^{q^3-1} +
beta^{q-1} + 1) u + beta^{q-1} over F_{q^7} (beta = b^{1/2}), keep a root
with u^{q^2+q+1} + u + 1 = 0 and u^{(q^7-1)/(q-1)} = 1, extract gamma_1 with
gamma_1^{q-1} = u (one F_{q^7}^* DLP, Lemma 9, run once per attack); the
second family uses s = (q+1)^{-1} mod q^7 - 1 and u^{q+s} + u + 1 = 0.
Theorem 10 proves correctness. Counting (Section 5.1.2, with a heuristic on
repeated representations, "confirmed experimentally for N = 7, 14, 21"):
#B = (q^3 - 1)(q^2 + q + 2)/2 per family, #W_0 ~ q^5/2, so under
Assumption C the walk needs **2 q^2 expected steps**. Table 1 (Tr(a) = 0,
genus 7; log2 of R_rho, R_RG, R_LA, R_W):

| N | l | rho | relations | matrix | walk |
|---|---|---|---|---|---|
| 161 | 23 | 83 | 43 | 47 | 69 |
| 210 | 30 | 108 | 51 | 61 | 84 |
| 301 | 43 | 153 | 64 | 87 | 110 |
| 399 | 57 | 202 | 79 | 115 | 139 |
| 497 | 71 | 251 | 93 | 143 | 167 |
| 595 | 85 | 300 | 107 | 171 | 195 |

The walk dominates and R_RG << R_W, so the verdict does not depend on
Assumptions A and B being tight. For **Tr(a) = 1** (Section 5.2): W_1 with
Ord_{gamma_1} = X^3+X+1, Ord_{gamma_2} = (X^3+X+1)(X+1) gives genus 14 and
#W_1 ~ q^6 (about q walk steps), but no membership test faster than q^{2.5}
was found, so E_1 over F_{2^{7l}} is left **open**.

### n = 6 (Section 6): F_{2^{6l}} potentially weak

X^6 + 1 = (X+1)^2 (X^2+X+1)^2. Two families:

1. Ord_{gamma_1} = X^3+1, Ord_{gamma_2} = (X+1)(X^3+1): s_1 = 3, s_2 = t = 4,
   **genus 14**. Theorem 11: with beta = b^{1/2}, gamma_1 = Tr_{K/K_1}(beta)
   (K_1 = F_{q^3}), gamma_2 = beta/gamma_1, E is in W iff Ord_{gamma_1} =
   X^3+1 and Ord_{gamma_2} != X^2+1; #W = 2q(q-1)(q^2-1)^2 ~ 2q^6, i.e.
   essentially **every** non-subfield curve, so the walk is "a few steps".
   Table 2 (log2 R_rho, R_RG, R_LA): 162/27: 84, 74, 56; 210/35: 108, 82,
   72; 300/50: 153, 98, 102; 402/67: 204, 115, 136; 498/83: 252, 131, 168;
   600/100: 303, 149, 202.
2. Ord_{gamma_1} = X^2+X+1, Ord_{gamma_2} = (X+1)^2 (X^2+X+1): s_1 = 2,
   s_2 = t = 4, **genus 12**; #W = 2q(q^2-1)^2 ~ 2q^5; decomposition
   gamma_1 = beta^{q^3} + beta. Membership forces Tr(b) = 0, hence (Lemma 7
   of KN-LIT-d7995a) 8 | #E when Tr(a) = 0; X = non-subfield curves with
   #E = 0 or 2 (mod 8), #X ~ q^6, density 2^-(l-1). Table 3 (log2 R_rho,
   R_RG, R_LA, R_W): 162/27: 84, 66, 56, 48; 210/35: 108, 72, 72, 57;
   300/50: 153, 90, 102, 72; 402/67: 204, 107, 136, 90; 498/83: 252, 123,
   168, 106; 600/100: 303, 141, 202, 123.

### n = 3 (Section 7): F_{2^{3l}} partially weak (no assumptions A, B)

X^3 + 1 = (X+1)(X^2+X+1). W: Ord_{gamma_1} = X+1, Ord_{gamma_2} = X^2+X+1,
s_1 = 1, s_2 = 2, t = 3, **genus 3**; here generalized GHS and GHS coincide
(gamma_1 = 1), E_{a,b} is in W iff Ord_b = X^2+X+1, i.e. b^{q^2} + b^q + b =
0; q^2 - 1 such b, ~2(q^2 - 1) curves, and C is **hyperelliptic**. Tr(b) =
0 again, so X = non-subfield curves with #E = 0 or 2 (mod 8), #X ~ q^3,
and the walk needs **q/2 expected steps**. Gaudry-Thome's double large
prime variant solves genus-3 HCDLP in O(q^{4/3+eps}), faster than rho's
O(q^{1.5}) "even for rather small jacobian sizes (about 2^81)"; hence
partially weak, with no non-hyperelliptic assumption.

### F_{2^210} summary (Section 8), R_rho ~ 2^108

1. n = 5: essentially all curves, genus 15/16 over F_{2^42}: R_RG ~ 2^98,
   R_LA ~ 2^86.
2. n = 6, GHS: ~2^175 classes genus 15/16 over F_{2^35}: R_RG ~ 2^90,
   R_LA ~ 2^75; via walks, a quarter of all curves (Tr(a) = Tr(b) = 0).
3. n = 7: ~2^149 curves in E_0, genus 7 over F_{2^30}: R_RG ~ 2^53,
   R_LA ~ 2^61; via walks all of E_0 in ~2^84 F_{2^210}-operations.
4. n = 6, genus 14 over F_{2^35}: almost all curves, R_RG ~ 2^82,
   R_LA ~ 2^72, a few walk steps.
5. n = 6, genus 12: ~2^176 curves, R_RG ~ 2^72, R_LA ~ 2^72; via walks all
   curves with #E = 0 or 2 (mod 8).
6. n = 3: ~2^140 curves, genus 3 over F_{2^70}; via walks all curves with
   #E = 0 or 2 (mod 8), then Gaudry-Thome.

### Everything else (Section 9)

- **N prime** in [160, 600]: X^N + 1 = (X+1) f_1 ... f_s with deg f_i = d =
  ord_N(2) >= 16, best genus 2^d - 1 over F_2; fails for every curve.
- **n = 2**: only genus 2; no DLP solver beats rho; fails.
- **n = 4**: GHS gives genus 8 for most curves ("only slightly weak",
  KN-LIT-d7995a); generalized GHS gives a genus-6 non-hyperelliptic curve
  (Ord_{gamma_1} = X^2+1, Ord_{gamma_2} = (X+1)^3), no further weakening.
- **n = 5**: generalized GHS also gives genus 15; nothing beyond GHS.
- **n = 8** (Section 9.2): W in E_0 with Ord_{gamma_1} = X^2+1,
  Ord_{gamma_2} = (X+1)^5, **genus 24** (GHS on the same curves: genus 32).
  Theorem 12: E in W iff Ord_b = (X+1)^6; #W = q^6 - q^5 per a-class;
  Tr(b) = 0 so 8 | #E; density 2^-(2l-1) in X. Table 4 (log2 R_rho; R_RG,
  R_LA at g = 24; R_RG, R_LA at g = 32; R_W): 160/20: 83; 86, 81; 104, 81;
  61. 200/25: 103; 96, 101; 114, 101; 72. 304/38: 155; 129, 79; 140, 153;
  98. 400/50: 203; 142, 103; 181, 103; 123. 504/63: 255; 155, 129; 195,
  129; 149. 600/75: 303; 167, 153; 207, 153; 173. (Footnote: at the small
  N the factor base also holds degree-two divisors.) Verdict: potentially
  partially weak "for sufficiently large N".
- **n = 9**: best genus 63 (Ord_{gamma_1} = X^6+X^3+1, Ord_{gamma_2} = X+1);
  fails. **n = 10**: best genus 32, no gain over GHS. **11 <= n <= 300**:
  checked; only negligible proportions succumb, curves not hyperelliptic.

## Conclusions and open problems (Section 10)

Fields F_{2^N} with N divisible by 3, 5, 6, 7 or 8 "should not be used".
Open: characterize the generalized-GHS curves and their best DLP solvers;
whether E_1 over F_{2^{7l}} is weak.

## Key claims: verified versus reported

| Claim | Status here |
| --- | --- |
| Genus formula and Remark 2 specialization | Read; Hess' theorems not read (KN-LIT-6987 is abstract-only). |
| Theorems 10, 11, 12 (membership tests) | Read with proofs; elementary Frobenius-order arguments, checkable at toy l. |
| #W_0 ~ q^5/2 for n = 7 | Heuristic count, authors' experiments at N = 7, 14, 21. |
| Tables 1-4 | Transcribed from the technical report; the n = 8 row 304/38 "R_LA = 79" at g = 24 is as printed. |
| Walk step cost N 2^15 | Order-of-magnitude, 2004 experiments on 20000 discriminants. |
| Gaudry-Thome genus-3 O(q^{4/3}) | Reported from their ePrint 2004/153 via this paper. |

## Relevance to this program

- Fixes the n = 3, 7 and 8 "Menezes-Teske rates" that
  `PROTOCOL-I3-class-screens.md` Q1 (aburan28/crypto,
  `research/isogeny_class_difficulty_20261008/`) invokes: n = 3 density
  2^-(l-1) of genus-3 curves inside the #E = 0, 2 (mod 8) classes (that is
  the eps ~ 2^-58 of KN-LIT-0cb87e at l = 59); n = 7 density ~2^-(2l+1) of
  genus-7 curves in E_0; n = 8 density 2^-(2l-1) in the 8 | #E classes;
  n = 6 genus-14 density ~1 and genus-12 density 2^-(l-1). Only the n = 3
  family is visible to an Ord_b screen; n = 6 (genus 12, 14), n = 7 and
  n = 8 (genus 24) families need the gamma_1, gamma_2 decomposition test.
- KN-TECH-36e667's reading of Section 7 (genus-3 route is hyperelliptic;
  reach ~q^2 directly, q/2 walk steps) is confirmed against the full text.
- aburan28/crypto `research/ghs-c2pnb/ghs_poc.py` cites "Menezes-Teske
  2006" for a c2pnb176w1 break "at m' = 5", cost ~2^57. **This paper does
  not mention c2pnb176w1 or any X9.62 curve** (full text read). The claim
  traces to Maurer-Menezes-Teske 2001/2002 Section 6 (KN-LIT-0e854b), which
  finds that an isogenous curve with (n, m) = (8, 5) would give genus 16
  over F_{2^22} at 2^61 to 2^65 against rho 2^87 and judges finding it
  harder than rho. For the shape 176 = 8 * 22 this paper's Section 9.2
  (genus 24 or 32 family, density 2^-(2l-1) = 2^-43) and n = 4 (genus 8
  over F_{2^44}, "not further weakened") are the only statements it makes,
  and Table 4 here does not list N = 176.
- No prime-degree binary field (ECC2K-130's F_{2^131}, sect113, sect163) is
  touched, by Section 9.1.

## Limits of applicability

Binary fields, composite N, l large enough for the asymptotic smoothness
counts; everything but n = 3 rests on Assumptions A, B (cost of Hess'
non-hyperelliptic Jacobians) and C (uniform density of W across
endomorphism classes); all costs are time only, tau factors dropped.

## Provenance

Retrieved 2026-10-09 from `https://cacr.uwaterloo.ca/techreports/2004/corr2004-25.pdf`
(364,856 bytes, 22 pages) after the ePrint PDF URL returned a Cloudflare
challenge; text extracted with `pdftotext -layout`. Retrieval record:
`inputs/MTW-WEAK-FIELDS-20261009/provenance.json`.

## Local copies

- `inputs/MTW-WEAK-FIELDS-20261009/sources/menezes-teske-corr2004-25.pdf` and `.txt`
- The stub KN-LIT-3305 named `downloads/corr2004-25.pdf`, which is not in the repository.
