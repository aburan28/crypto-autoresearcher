# Family C: cross-field, lifting and dynamics structure for the ECDLP

Idea Synthesist pass, 2026-10-31. Claim boundary: mathematical ideation on toy
and public parameters only. No secret scalar, no deployed key, no exploit.
Nothing below was run; every "prediction" is a pre-registered expectation, not
an observation. Atlas matcher (`tools/lead_atlas.py --match`) was NOT run (no
shell); collision phrases are listed per candidate for the top-level session.

## 0. Bottom line

The family is saturated at theorem level. Every lifting route this program has
walked ends in one of two named obstructions, and every object the task lists
(global lifts, Heegner/CM reductions, Lattes dynamics, p-adic towers, Weil
restriction at small degree, F_p(t) specialisation, Frobenius eigenspaces,
local-global principles) lands on one of them:

- **Obstruction A (kernel of reduction).** For any ring R in {Z, O_K, F_p[t]}
  and any finitely generated group L of global points with a reduction or
  specialisation homomorphism red: L -> G = Z/N, the discrete logs ARE the
  kernel lattice ker(red) (index N). A short kernel vector with prescribed
  support is DL-equivalent; searching for one costs >= N^{1/2} by MITM
  whatever the rank. Appears as: F4b canonical height (hat h(T) = m^2 hat h(S)),
  the witness-lattice closure (H-ENDO-001), alpha = 3 for F_p(t) sections, the
  D2 kernel-height floor of EV-CZLIFT-376eee, and the knapsack in Candidate 1.
- **Obstruction B (curve statistics are k-independent; homomorphic invariants
  to coprime groups are trivial).** Preimage trees, torsion fields, Frobenius
  patterns, postcritical sets, multiplier spectra, Kolyvagin congruences: all
  functions of E (or of specific global points), never of the target scalar.
  Appears as: LEAD-STR-torsion-module-leak, LEAD-TRF-second-torsion-direction
  (Balasubramanian-Koblitz), LEAD-TRF-padic-canonical-section.

Of eight objects examined, four are plain rephrases of existing leads and are
dropped (section 2). Four are written up (section 1); none is rated promising
as an attack. Candidate 2 is rated promising as a *closure theorem* that would
collapse five `revisit_when` clauses into one named obstruction, and Candidate
1 is the first concrete construction that satisfies the XEDN leads' stated
reopening condition, which shows that condition is under-specified (section 3).

Ranking (which connection, if confirmed, changes the most records):
1. C2 kernel-of-reduction lemma (touches 5 leads, 2 goals, rewrites 3 revisit_when).
2. C1 Ulmer dimension-surplus control (bridges XEDN <-> PKM; corrects 2 revisit_when).
3. C3 Lattes closure row (adds a missing atlas row; closes 3 rejected ideas' family).
4. C4 Heegner/Kolyvagin (adds forecloses phrases only).

---

## 1. Candidates

### C1. Ulmer / Legendre high-rank surfaces over F_p(t): the dimension-surplus specialisation that the XEDN leads ask for (F5 face)

**1. Title.** Specialising explicit unbounded-rank elliptic surfaces over F_p(t)
(Ulmer curves) at t = t0 in F_p as a lift family for E_{t0}(F_p).

**2. Object.** (a) Ulmer's curve U_d: y^2 + xy = x^3 - t^d over F_p(t) with
d = p + 1. Rank over F_p(t) is sum_{e | d, e not | 6} phi(e)/o_e(p) + eps,
o_e(p) the order of p mod e; for d = p + 1 every o_e(p) <= 2, so rank is about
(p+1)/2, unconditionally (Ulmer, Annals 2002; BSD proved for these curves)
[recalled; existence of the paper retrieved by search]. Fibre at t0 in F_p^*:
t0^{p+1} = t0^2, so E_{t0}: y^2 + xy = x^3 - t0^2, with j = 1/(c(1 - 432 c)),
c = t0^2: roughly p/4 of all F_p-isomorphism classes of curves over F_p are
fibres. (b) Legendre curve L: y^2 = x(x+1)(x+t) over F_p(u), u^d = t,
d = p^f + 1, with the explicit points P(zeta u) = (zeta u, zeta u (zeta u + 1)^{d/2}),
zeta in mu_d (Ulmer, JNT 2014; checked here: x + t = u(1 + u^{d-1}) and
(u+1)^{d-1} = u^{d-1} + 1 in characteristic p). The d points P(zeta u) span a
subgroup of rank d - 2 (two identically-true relations) [recalled]. Fibre at
t0 (f = 1): u ranges over the p + 1 roots of u^{p+1} = t0 in F_{p^2} (the norm
torus T_{t0}), and P(u) in L_{t0}(F_{p^2}); traces P(u) + P(t0/u) give about
(p+1)/2 explicit points of L_{t0}(F_p). L_{t0} has full rational 2-torsion
(cofactor >= 4), so the target subgroup G has index >= 4.

**3. Mechanism and where it ends.** The XEDN closure is alpha = 3: on rational
elliptic surfaces (rank <= 8, frozen section shapes) the probability that a
prescribed fibre point lies on a bounded-height section is ~ p^{-3}. On U_d or
L with rank r ~ p/2, the number of sections of bounded height is >= 3^r >> p,
so every fibre point is the specialisation of a short section: the lift
*exists* with probability ~ 1 (alpha ~ 0 by counting). The route would be:
find a short section s_Q = sum c_i g_i through Q, likewise s_P through P, and
read k from the lattice. The step "find s_Q" is the knapsack
sum c_i g_i(t0) = Q with r ~ p/2 explicit items in G, which is Obstruction A
(generic representation problem, >= N^{1/2} by MITM) unless the items' algebraic
form helps. For L the items are exactly the points with x in the norm torus
T_{t0} (and y automatically F_{p^2}-rational, a factor-2 density saving), so
a weight-w knapsack is the point-decomposition problem with the *torus factor
base* over F_{p^2}: LEAD-ICP-pkm-tower-algebraic-oracle measured that oracle
(torus = split Dickson = Kummer; F4 solving degree grows with N), and the
whole-group cost is the Gaudry n = 2 tie O~(p) against rho's p^{1/2} on G.
The function-field lattice contributes only ~2 free relations among ~p+1
specialised points (span rank d - 2), so the free-relation supply is O(1),
not Theta(B). Gain level: no exponent; constant (factor 2 membership) at
best; as an attack it is a reformulation of the torus-base PDP. The one
genuinely open quantity is whether the explicit family's logs
zeta -> log_G(Tr P(zeta u0)) carry mu_{p+1}-character structure (prior: null;
there is no morphism from the genus-0 torus curve to E_{t0}, so no algebraic
reason for structure is visible).

**4. Closest leads and why not already foreclosed.**
LEAD-ICP-xedni-function-field-sections (closed_obstructed; its revisit_when is
"a surface family with a dimension surplus ... whose measured lift exponent is
below 1/2") and LEAD-TRF-function-field-xedni-lift (closed_obstructed; revisit
"a section shape with prescribed-fibre lift probability exponent below 1/2,
derived before measurement"): Ulmer surfaces satisfy both clauses by counting,
derived before measurement, so the recorded obstruction (alpha = 3, a proof
about rank <= 8 rational surfaces with frozen shapes) does not apply. The
mechanism then meets a different, already-measured obstruction
(LEAD-ICP-pkm-tower-algebraic-oracle, open_blocked; KN-TECH-4409e1 n = 2 tie).
Also: LEAD-EXO-global-lift-height (open_next_step, IDEA-20261009-581f5d
T_section) and DEC-20261023-26a6de next_action "(a) global lifts whose rank
grows like log p / log log p and that reduce to a prescribed target curve":
Ulmer gives rank p/2 over F_p(t), far beyond that request.
Collision phrases to match: "function field xedni", "elliptic surface section
lifting", "Mordell-Weil sections over F_p(t)", "specialise sections of a
rational elliptic surface", "torus tower decomposition oracle", "Dickson or
torus tower decomposition oracle", "high-rank lift through a prescribed fibre".

**5. Toy discriminating experiment** (class: control). p in {11, 13, 17, 19, 23},
d = p + 1, every t0 in F_p^*, curve L_{t0}, N = largest prime factor of
#L_{t0}(F_p), G its subgroup. Arms:
(A) Correctness gate: the d explicit points lie on L_{t0}(F_{p^2}); compute the
Z-span rank of {P(zeta u0)} in L_{t0}(F_{p^2}) and the number of 0/+-1 relations
of weight <= 4. Prediction: the two identically-true relations plus
fibre-specific relations at exactly the count of a null of d uniformly random
points of the same group. Falsifier: weight-<= 4 relation count above the null
at >= 3 primes (would mean the lattice carries fibre information).
(B) Lift coverage: fraction of G hit by traces of sections of lattice height
<= H as H grows, versus the coupon model with M(H) sections and versus a
random multiset of size M(H). Prediction: alpha ~ 0 (coverage saturates
once M(H) >= N ln N), identical to the random control.
(C) Character test: for zeta -> ell(zeta) = log_G(Tr P(zeta u0)) in Z/N,
max over chi in hat(mu_{p+1}), a in Z/N of |sum_zeta chi(zeta) e(a ell(zeta)/N)|
against the random-permutation null (10^3 reps), with a planted positive
control (ell replaced by a linear function of log zeta). Falsifier of the null
(keeps the lead alive): a coefficient above the null's 99.9th percentile at
>= 3 primes.
(D) Lift-finder cost: F_p multiplications to find a weight-w 0/+-1
representation of a random target among the d items by Semaev S_{w+1} with
membership u^{p+1} = t0 (the existing pkm-semaev torus arm) versus a 2-list
MITM. Prediction: >= MITM, consistent with the measured D growth.
Counted quantities: span rank, relation counts, coverage ratio, max Fourier
coefficient, F_p mults. Expected outcome: closes with the named obstruction
"specialisation is a generic homomorphism; dimension surplus makes the lift
exist, not findable", and rewrites the XEDN revisit_when.

**6. Prior-art risk.** Ulmer 2002 (Annals) and Ulmer 2014 (JNT) retrieved by
title/abstract; explicit-point formula verified algebraically above; rank
formula recalled. Web search found no cryptanalytic use of these surfaces.
novelty_status: unverified (as an ECDLP object); the terminal mechanism is
known (torus PDP, Gaudry n = 2).

**7. Rating.** likely-closed-on-inspection: the attack reading collapses to
the torus-base PDP over F_{p^2} and the Gaudry n = 2 tie; file it anyway as a
control because it is the first construction meeting the XEDN reopening
clause and arms (A)-(C) cost minutes.

### C2. The kernel-of-reduction lemma: one obstruction under five leads, with a function-field floor test

**1. Title.** Short vectors of ker(red: L -> E(F_p)) are discrete logs for
every ring and every rank; the F5 kernel floor is p-independent.

**2. Object.** L a finitely generated group of global points (E(Q), E(K),
E(F_p(t)), or the span of an explicit family), red the reduction or
specialisation homomorphism onto G = Z/N, K = ker(red) of index N, and the
coset red^{-1}(Q).

**3. Mechanism (proof-oriented; moves no exponent).** Lemma to write and
check: (i) an oracle returning a K-vector with prescribed nonzero support on
two coordinates whose images are P and Q returns k in O(1) calls (rank-2
case IS the DL), so for any rank r >= 2 "find a kernel vector of prescribed
support" is DL-hard; (ii) the shortest K-vector has sup-norm ~ N^{1/r}, and
enumeration or MITM over the N^{1/r}-box costs N^{1/2} independent of r, which
is the witness-lattice closure restated (H-ENDO-001: augmenting coordinates
leaves the index at N); (iii) lattice reduction cannot find K without the
logs because K is defined by them. This is the single obstruction behind
F4b (hat h(T) = m^2 hat h(S)), alpha = 3 in F5, the D2 kernel floor
hat h >= 2 log p - c_E (EV-CZLIFT-376eee), and C1's knapsack. New content:
in F5 a section through O at t0 has a double pole of x at t0, so the kernel
height floor is a fixed intersection number (about 2), independent of p,
whereas over Z it is 2 log p. Hence the "coverage excess / kernel clumping"
that broke C2 of H-CZLIFT-9a32e9 should be absent for F_p(t) specialisation.
This discriminates the D2 mechanism from alternatives and shows the excess is
ring-specific (and useless to an attacker in both rings, by the D6 pigeonhole
bound). Gain level: none; closure instrument. proof_search_map: bottleneck =
finding short kernel vectors; baseline embedding = rank 2 (P, Q); quantifier
order = for all (L, red) with generic access to images, no algorithm below
N^{1/2} unless DL; method ceiling = theorem in the generic-group model for
the images; nearby object where it fails = anomalous curves (#E = p), where
the formal logarithm exhibits K directly; the lemma must exclude the p-adic
formal-group channel explicitly.

**4. Closest leads and why not a rephrase.** LEAD-TRF-global-lift-small-height
(closed_known; DEC-20261023-26a6de next_action (b) asks for exactly this
pre-screen), LEAD-STR-endo-scalar-action-generic (closed_obstructed, witness
lattice), LEAD-ICP-xedni-function-field-sections and
LEAD-TRF-function-field-xedni-lift (closed_obstructed, alpha = 3),
LEAD-EXO-global-lift-height (open_next_step), LEAD-TRF-cm-canonical-lift-heights.
No lead states the obstruction ring-independently, none names the F5 floor
difference, and the atlas currently carries four differently-worded
revisit_when clauses for one obstruction. Bridges: GOAL-CZLIFT-1516d5 <->
GOAL-XEDN-00x <-> GOAL-ENDO-001.
Collision phrases: "Mordell-Weil relation of lifted points", "small height
global lift", "endomorphism-augmented witness lattice", "kernel of reduction
short vector", "height-compressing global lift".

**5. Toy discriminating experiment.** (i) Z arm: replicate the D2 floor on
37a1 and 389a1 at p = 103..2417 (prediction: min hat h over kernel points
>= 2 log p + c, c about 0.9 as measured). (ii) F5 arm: the EV-XEDN rational
surface families at p in {7, 13, 19, 31}, all fibres t0: minimum height of a
section with s(t0) = O. Prediction: constant floor (minimal intersection
number, about 2) across p; control: a random homomorphism L -> Z/N of the same
index gives the same floor statistics (floor is geometric, not a log leak).
Falsifier: an F5 floor growing with p (then F5 inherits F4b's floor and the
"not inherited" line of KN-TECH-06bb4e is wrong), or any ring where kernel
vectors are found below MITM without DL (that would be a real lead).
(iii) Lemma check on toy groups: implement the oracle reduction and verify
O(1) calls recover k for N in {1009, 10007}.

**6. Prior-art risk.** JKSST 2000 (recalled), Silverman ECC 2007 taxonomy
(KN-LIT-6935a1, kb), Shoup 1997 (recalled), Lang 1983 Ch. 5 (recalled; cited in
DEC-26a6de). The witness-lattice half exists internally (KN-FIND-009,
H-ENDO-001). novelty_status: adaptation (internal results unified); unverified
against literature.

**7. Rating.** promising as a closure theorem and atlas simplification; it
moves no exponent and is not an attack.

### C3. Lattes maps and x-line dynamics: a closed row the atlas lacks

**1. Title.** Lattes-map dynamics on P^1(F_p) (orbits, preimage trees,
postcritical and multiplier data) as ECDLP structure.

**2. Object.** phi_d with x o [d] = phi_d o x; CM Lattes maps phi_alpha of
degree N(alpha); periodic points = x(E_tors) (everything over F_p);
postcritical set x(E[2]) union infinity for d = 2; iterated preimage trees of
x(Q); multipliers d^{2n}.

**3. Mechanism and closure chain.** (a) phi_d(x(R)) = x([d]R): every forward
iterate is a group operation, so any forward-dynamics algorithm is
GGM-simulable (KN-FIND-002 pattern) and Shoup's N^{1/2} applies. (b) The
phi_alpha-orbit of x(Q) is the coset of <lambda> in (Z/N)^* acting on k;
orbit length ord_N(lambda) >= log N / log N(alpha) (IDEA-20260901-6b63a4), so
dynamics quotients give sqrt|Aut| for units and nothing for non-units
(LEAD-STR-small-cm-disc-nonunit-endo, LEAD-STR-automorphism-quotient-rho).
(c) Preimage trees: roots of phi_d^{(n)}(x) - x(Q) are x(Q_n + T), Q_n = d^{-n}Q
rational, T in E[d^n]; the F_p-factorisation pattern is the Frobenius orbit
structure on E[d^n], hence k-independent (the LEAD-STR-torsion-module-leak
argument; H-TORS-3bed8a measured the analogue for psi_5); a source-faithful
quotient of the tree has N^{1-o(1)} leaves (ideas/rejected/ECDLP-IDEA-113).
(d) Postcritical sets and multiplier spectra are curve constants. Gain:
none beyond the known sqrt|Aut| constant; pure reformulation otherwise.

**4. Closest leads.** No atlas row covers Lattes/x-line dynamics, although
ECDLP-IDEA-113 (rejected), the Lattes Cauchy-accumulator closures
(EV-ECDLP-0c0f51, EV-ECDLP-a8af77) and the scout kill K9 ("Elliptic-torsion /
Lattes / Velu x-map towers") exist. Closure follows from
LEAD-STR-torsion-module-leak + LEAD-STR-small-cm-disc-nonunit-endo +
LEAD-STR-automorphism-quotient-rho + the GGM finding. Not a rephrase of one
lead; a missing row. Collision phrases: "Lattes map", "x-line dynamics",
"arboreal preimage tree", "periodic points of multiplication map",
"postcritical set", "multiplier spectrum", "dynatomic polynomial".

**5. Toy check (only if a row with `kind: measured` is wanted; `kind: proof`
suffices).** p in {1009, 2003}, d in {2, 3}, n <= 4: factor-degree multiset of
phi_d^{(n)}(x) - x(kP) over 50 k-resampled targets. Prediction: identical
multiset for all k. Falsifier: any k-dependence at matched curve.

**6. Prior-art risk.** Milnor "On Lattes maps" (recalled); ePrint 2024/539
(Lattes maps for hashing; retrieved, states no attack); METU 2023 thesis on
value sets of Lattes maps (retrieved). No source links Lattes dynamics to an
ECDLP speedup. novelty_status: known (closure).

**7. Rating.** likely-closed-on-inspection; recommend adding
LEAD-EXO-lattes-xline-dynamics with disposition closed_obstructed, kind proof.

### C4. Reductions of Heegner / CM points and Kolyvagin congruences

**1. Title.** Relations among reductions of Heegner points (Kolyvagin
congruences, Hecke trace relations) as a DL-free relation source.

**2. Object.** E/Q modular, K imaginary quadratic, Heegner points y_n in
E(K_n); Kolyvagin primes ell (inert in K, ell + 1 = a_ell = 0 mod M); at the
prime lambda | ell of K_ell, red_lambda(y_ell) = Frob_ell(red_lambda(y_1)) in
E(F_{ell^2}) (Gross 1991, recalled); Tr_{K_{n ell}/K_n} y_{n ell} = a_ell y_n.

**3. Mechanism and why it stops.** These are exact relations among reductions
of specific global points, obtained without any DL. For a target Q in G in
E(F_p): (i) Q is the reduction of a global point only at height ~ k^2 hat h
(F4b), and the number of global points of bounded height is (log H)^{r/2} with
r = rank E(K_n) bounded (Obstruction A, C1 of DEC-26a6de); (ii) the
Frobenius relation lives in the trace-zero (eigenvalue -1) part of E(F_{ell^2})
and is the identity on E(F_ell), so on a prime-order subgroup of E(F_ell) it
says red(y_ell) = red(y_1): no scalar; (iii) the Euler-system relations are
Hecke relations, and Hecke/Atkin-Lehner relation sources were tried on
X_0(11)/F_367 with "no IC advantage" (evidence in
LEAD-ICP-lattice-ic-relation-construction). Gain: none.

**4. Closest leads.** LEAD-TRF-global-lift-small-height,
LEAD-TRF-cm-canonical-lift-heights, LEAD-STR-torsion-module-leak,
LEAD-TRF-second-torsion-direction, LEAD-ICP-lattice-ic-relation-construction.
Not a single-lead rephrase (needs two obstructions), but closed by their
composition. Collision phrases: "Heegner point reduction", "Kolyvagin
congruence", "Gross-Zagier", "Euler system relations mod p", "modular
parametrisation relations", "Hecke correspondence relations".

**5. Toy check (optional, correctness only).** 37a1 with a Heegner field,
Kolyvagin primes ell <= 200: verify the congruence and that
red(y_ell) - red(y_1) lies in the trace-zero part of E(F_{ell^2}). No target
enters, so there is no attack metric; the falsifier is only of the recalled
congruence itself.

**6. Prior-art risk.** Gross 1991 and Gross-Zagier 1986 recalled; no ECDLP use
found. novelty_status: known (closure).

**7. Rating.** likely-closed-on-inspection; dropped as an attack lead, kept
so the global-lift lead gains the forecloses phrases above.

---

## 2. Dropped as rephrases of existing leads

5. **Weil restriction at n = 2, 3 (GLS / Q-curves over F_{p^2}; Res E' ~ Jac(C)
   with real multiplication).** n = 2: genus-2 double-large-prime IC O~(p) vs
   rho p on a p^2 group, a tie (KN-TECH-4409e1); n = 3: Diem q^{4/3} via
   LEAD-TRF-odd-char-descent-smith-quartic; the Torelli census is already
   LEAD-TRF-weil-restriction-jacobian-class's next step. RM gives constants.
6. **Frobenius-eigenspace / trace-zero companion for G.** Balasubramanian-
   Koblitz: E(F_{p^k})[N] exceeds the rational line iff the embedding degree
   divides k. LEAD-TRF-second-torsion-direction, LEAD-TRF-one-point-self-pairing.
7. **Several primes above one prime (E over K with p split; Q-curves; the h
   reductions of a CM class).** The reductions are F_p-isogenous (same order,
   Tate) or unrelated; LEAD-TRF-prime-field-isogeny-to-weak,
   LEAD-STR-isogeny-class-generic-invariance.
8. **p-adic and l-adic towers beyond Smart (Coleman integrals, E(Z/p^2),
   ramification breaks, canonical sections, Mazur-Tate heights).**
   LEAD-TRF-padic-canonical-section, LEAD-EXO-padic-jet-canonical-lift,
   ECDLP-IDEA-160 theorem receipt (functorial towers closed).
9. **Isotrivial-surface sections = covers C -> E.** LEAD-TRF-same-field-genus-g-
   embedding (Tate multiplicativity; never for same-field covers).
10. **Multi-prime EDS / rank of apparition.** LEAD-EXO-elliptic-net-eds.
11. **Modular parametrisation X_0(M)_{F_p} -> E as a factor base.** Same-field
    cover plus the X_0(11)/F_367 Hecke result.

## 3. Possible mis-dispositions and bookkeeping for the atlas

- **Under-specified revisit_when (two leads).** LEAD-ICP-xedni-function-field-
  sections and LEAD-TRF-function-field-xedni-lift reopen on "a dimension-
  surplus family / section shape with lift exponent below 1/2 derived before
  measurement". Ulmer surfaces (rank about p/2 over F_p(t), explicit points)
  satisfy this by counting. The operative obstruction is the lift-finder
  (Obstruction A; for Legendre fibres literally the torus PDP of
  LEAD-ICP-pkm-tower-algebraic-oracle), not lift existence. Dispositions stay
  closed_obstructed; the clauses should name the finder cost.
- **Wording in LEAD-TRF-global-lift-small-height.** Its obstruction.statement
  says the program "re-measured uniform reduction of small points"; DEC-
  20261023-26a6de records C2 (uniform reduction) as contradicted and rests the
  closure on the counting law C1 plus the kernel floor D2. Disposition
  (closed_known) is right; the statement should cite counting, not uniformity.
- **Stale citation.** DEC-20261023-26a6de next_actions tell the idea generator
  to pre-screen kernel short vectors "against KN-LIT-7593"; that id resolves to
  an AES meet-in-the-middle paper. The intended reference (probably the
  witness-lattice / Bambury-Nguyen note near KN-LIT-7603) should be fixed.
- **Missing row.** No lead covers Lattes / x-line dynamics though
  ideas/rejected/ECDLP-IDEA-113, EV-ECDLP-0c0f51, EV-ECDLP-a8af77 and scout
  kill K9 exist; coverage.tsv presumably maps them elsewhere. See C3.
- **KN-TECH-06bb4e** says the F4a Masser obstruction's F5 analogue "has not
  been measured" and that ECDLP-IDEA-435 (target-coefficient audit) is the
  decisive control; the XEDN lead now says the max|coeff| = 1 census "carried
  no discriminating power" (lattice-forced). The target-blindness reading
  (H-B of IDEA-435) should be stated explicitly as the reason, or the audit
  run; it is cheap.

## 4. Compact idea records (ids to be minted by the allocator)

```yaml
idea:
  id: IDEA-PENDING-ulmer-f5-surplus
  title: Ulmer/Legendre unbounded-rank surfaces over F_p(t) as the XEDN dimension-surplus family
  class: control
  claim: >-
    For Legendre fibres L_t0/F_p, sections of bounded height cover G with the
    uniform coupon law (lift exponent ~0), the explicit family's logs show no
    mu_{p+1}-character structure above a permutation null, and the best
    lift-finder costs at least a 2-list MITM; so dimension surplus does not
    escape the lifting obstruction.
  bridges: [LEAD-ICP-xedni-function-field-sections, LEAD-TRF-function-field-xedni-lift, LEAD-ICP-pkm-tower-algebraic-oracle, DEC-20261023-26a6de, KN-TECH-4409e1]
  novelty_status: unverified
  citations:
    - {ref: "Ulmer, Annals 155 (2002) 295-315", provenance: retrieved, claim: unbounded rank over F_p(t) for y^2+xy=x^3-t^d, verified_by: search-result title only}
    - {ref: "Ulmer, J. Number Theory 136 (2014)", provenance: retrieved, claim: explicit points on the Legendre curve, verified_by: abstract}
  target_complexity: {time_exponent: none claimed, memory_exponent: none claimed, best_known: N^{1/2}, hidden_overhead: n/a, tradeoff_note: reduces to torus PDP over F_{p^2}}
  predictions:
    - {metric: coverage ratio vs coupon model, direction: different, minimum_effect: none expected}
    - {metric: max Fourier coefficient of logs over mu_{p+1}, direction: higher, minimum_effect: above null 99.9th pct at 3 primes}
  falsification_conditions: [structure in (C), sub-MITM finder in (D)]
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: low
idea:
  id: IDEA-PENDING-kernel-reduction-lemma
  title: Kernel-of-reduction short vectors are discrete logs for every ring and rank; F5 floor is p-independent
  class: mechanism
  claim: >-
    Prescribed-support kernel vectors are DL-equivalent for rank >= 2 in any
    ring; the F_p(t) kernel height floor is a p-independent intersection
    number while the Z floor is 2 log p.
  bridges: [LEAD-TRF-global-lift-small-height, LEAD-STR-endo-scalar-action-generic, LEAD-ICP-xedni-function-field-sections, LEAD-EXO-global-lift-height, EV-CZLIFT-376eee, H-ENDO-001]
  novelty_status: adaptation
  target_complexity: {time_exponent: none, memory_exponent: none, best_known: N^{1/2}, hidden_overhead: n/a}
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: medium
idea:
  id: IDEA-PENDING-lattes-closure-row
  title: Lattes / x-line dynamics closure (new atlas row)
  class: control
  bridges: [ECDLP-IDEA-113, LEAD-STR-torsion-module-leak, LEAD-STR-small-cm-disc-nonunit-endo, LEAD-STR-automorphism-quotient-rho, KN-FIND-002]
  novelty_status: known
  recommended_priority: low
idea:
  id: IDEA-PENDING-heegner-kolyvagin-forecloses
  title: Heegner/Kolyvagin reduction relations (forecloses phrases for the global-lift lead)
  class: control
  bridges: [LEAD-TRF-global-lift-small-height, LEAD-STR-torsion-module-leak, LEAD-ICP-lattice-ic-relation-construction]
  novelty_status: known
  recommended_priority: low
```

## 5. Honest accounting

- Read in full: docs/agent-runtime-core.md, agents/idea-synthesist.md,
  agents/idea-generator.md, knowledge/leads/ecdlp/README.md, every lead YAML
  under transfer/ (24) and structure/ (17), 8 exotic and 7 ic-prime leads in
  this family, knowledge/frontiers/ecdlp/README.md, KR-IC-cd159a, KR-RHO-53c89f,
  KR-RHO-817bf8, KR-IC-5ea2f8, KN-TECH-4409e1, KN-TECH-06bb4e, KN-FIND-3a7d42,
  KN-OPEN-cc1988, DEC-20261023-26a6de, H-CZLIFT-9a32e9, RQ-XEDN-3bfe2e,
  ideas/rejected/ECDLP-IDEA-113, ideas/ECDLP-IDEA-435 and -160 (first 80-90
  lines), the lead-discovery GRAVEYARD headings and two scout dossiers'
  headings. Grep scans for Lattes/Heegner/Selmer/Weil-restriction/function-
  field/trace-zero/CRT terms across the repository.
- Not read: the remaining generic/, ic-binary/, ic-engine/ leads (outside this
  family); the full ledger of proposals (title-level grep returned nothing
  because titles are folded; a few proposal files were listed by keyword but
  not opened).
- Not run: anything. No atlas matcher, no computation. All predictions are
  pre-registered expectations.
- Recalled (unverified) ingredients: Ulmer's rank formula and the rank d - 2
  of the explicit-point span; Gross's Kolyvagin congruence; Milnor on Lattes
  maps; JKSST 2000; Shoup 1997; Lang 1983. Retrieved: existence and abstracts
  of Ulmer 2002/2014, ePrint 2024/539, METU thesis (web search results).
  Verified here by hand: the Legendre explicit-point identity and the
  j-invariant of y^2 + xy = x^3 + a6.
- Imagined outcomes: none reported. Claims of "closure" in sections 1-2 are
  derivations from recorded leads, not new evidence; each still needs the
  Coordinator and an independent Validator.
- Scope: toy parameters only; nothing here touches a deployed key or a secret
  scalar.

Sources consulted via web search:
- https://annals.math.princeton.edu/2002/155-1/p09
- https://archive.math.arizona.edu/ulmer/research/papers/2014a.pdf
- https://archive.math.arizona.edu/ulmer/research/papers/2013a.pdf
- https://eprint.iacr.org/2024/539.pdf
- https://open.metu.edu.tr/handle/11511/104466
- https://arxiv.org/pdf/2407.17042
