# Family A — arithmetic structure of the numbers (p, N, t, D, f, h, p±1, N±1, special forms)

Idea Synthesist pass, 2026-10-31. Toy and public parameters only; no secret scalar, no
deployed key. Everything below is a hypothesis for the Coordinator and an independent
Validator, not a finding.

## What I read

- `knowledge/leads/ecdlp/README.md`; every `forecloses:` block under `structure/`,
  `transfer/`, `exotic/`, `ic-prime/`, and the `generic/` and `ic-*` leads the keyword
  sweep (trace, discriminant, conductor, class number, smooth, p±1, Hasse, cyclotomic,
  Solinas, Mersenne, twist, norm form) pointed at.
- Full text of: LEAD-STR-small-cm-disc-nonunit-endo, LEAD-STR-class-group-ecdlp-bridge,
  LEAD-STR-class-representative-ic-selection, LEAD-STR-isogeny-class-generic-invariance,
  LEAD-STR-curve-generation-provenance-seeds, LEAD-STR-endo-scalar-action-generic,
  LEAD-TRF-global-lift-small-height, LEAD-TRF-cm-canonical-lift-heights,
  LEAD-TRF-miller-cocycle-nonhom-transfer, LEAD-EXO-global-lift-height,
  LEAD-EXO-miller-pairing-cocycle, LEAD-EXO-augmented-oracle-ggm,
  LEAD-ICP-char0-lifting-xedni-smoothness, LEAD-ICE-curve-presentation-invariance,
  LEAD-RHO-cheon-deployed-applicability, LEAD-RHO-lhw-modular-filter-price,
  LEAD-RHO-non-automorphism-equivalence, LEAD-RHO-matched-rho-calibration;
  KR rows KR-RHO-53c89f, KR-RHO-817bf8; frontier README and all KR titles.
- Ledger title sweep (`ledger/**`, indentation-tolerant) for the family keywords.

## Honest overview before the candidates

Almost every "number-shaped" lever has a lead already, and the closures are of three kinds:

1. **Order-determined weaknesses are isogeny-class invariants** (Tate; KR-RHO-817bf8):
   anomalous, small embedding degree, smooth order, twist orders. Walking cannot reach them.
2. **Cheap endomorphisms have large eigenvalue orbits** (orbit theorem, n^h >= (sqrt N - 1)^2,
   IDEA-20260901-6b63a4) and every endomorphism-image oracle is GGM-simulable
   (KN-FIND-002, KN-FIND-b7e091): on a prime-order G, End acts through Z/N, so arithmetic
   of (p, t, D, f) enters generic cost only through |Aut| and the step-cost model.
3. **Lifts grow** (heights (log B)^{r/2}; class polynomial degree h(D) ~ p^{1/2}).

So the family is close to saturated for *exponent* claims. What is genuinely missing is
(a) a single **measured** statement of (2) across arithmetic strata (every closure so far
varied the curve inside one (p, N) class, never (p, N, t) at fixed size), (b) the one
**construction** the atlas itself names as its reopen condition, (c) two **instruments**
that use arithmetic structure of p or of the (p, N) pair to run open leads at larger scale.
I found no candidate in this family with a credible exponent mechanism, and I say so.

I found five candidates worth filing; three more were drafted and dropped as rephrases
(listed at the end with the lead that forecloses each).

---

## C1. Arithmetic-rigidity control: regress charged rho and IC meters on arithmetic invariants of (p, N, t, D, f) across toy strata

**Class**: measurement / control. **Rank 1** (the connection that, if it failed, would
change the most leads; if it holds, it replaces a dozen scattered closures with one measured
row).

1. **Title**: Charged ECDLP cost as a function of the arithmetic of (p, N, t) only through
   N, |Aut| and field-step cost — a stratified, preregistered regression on existing and new
   toy runs.
2. **Object**: the invariant vector per prime-order toy curve: Sato–Tate angle
   theta = arccos(t / 2 sqrt p); squarefree part D_0 and conductor f of D = t^2 - 4p;
   log h(D) proxy (via f and h(D_0) for small D_0, Kronecker class number otherwise);
   smoothness profile (largest prime factor exponent, omega) of N-1, N+1, p-1, p+1;
   p mod 8, p mod 12, N mod 12; embedding-degree class ord_N(p) bucketed (< 2^10 vs larger);
   special-form flag (p = 2^k - c with c < 2^{k/4}).
3. **Mechanism**: no gain is claimed. The hypothesis H_rig: "for ordinary prime-order
   E/F_p, every charged meter the program ranks (rho.negation S, BSGS S, IC relation yield,
   charged IC S, Semaev solving degree) depends on the arithmetic of (p, N, t) only through
   N, |Aut(E)| and the F_p step cost." For rho this is the generic lower bound and any
   measured dependence is instrument bias (useful to know: LEAD-RHO-matched-rho-calibration
   has an unexplained toy excess, alpha 0.31–0.45). For IC meters it is an honest open
   question: the small-x factor base is an integer-lift object, so p mod small primes and
   the size of p-1's smooth part could plausibly move yield at the constant level. Gain
   level if H_rig fails: **constant**; the value of the experiment is the measured closure
   itself.
4. **Closest leads and why not foreclosed**:
   - LEAD-STR-isogeny-class-generic-invariance (closed): 403,168-run census varies the
     *curve within a fixed (p, N)* — whole volcanoes, level ratios. It never varies
     (p, N, t) at fixed size. Its `revisit_when` names "a level-dependent change in step
     cost" — C1 measures exactly the complementary axis.
   - LEAD-ICE-curve-presentation-invariance (open): within-class ICC ~ 0 for Koblitz m = 3;
     same within-class scope.
   - LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale): bias of the small-x set
     in log order; C1 does not re-measure the character sum, it asks whether any coarse
     arithmetic invariant predicts *charged* yield after that bias is controlled.
   - LEAD-STR-curve-generation-provenance-seeds (exhausted): 21 preregistered features on
     21 NIST classes, none ECDLP-bearing; C1 uses toy curves where cost can actually be
     measured, not deployed classes where it cannot.
   - LEAD-EXO-augmented-oracle-ggm / LEAD-STR-endo-scalar-action-generic (closed, theorem):
     the theorem side of H_rig. C1 is its measured complement, not a re-derivation.
   - Forecloses-phrase check: none of "volcano level changes Pollard rho cost",
     "conductor of End(E) affects generic ECDLP", "small CM discriminant makes ECDLP
     easier" is claimed; C1 predicts the null for all of them.
5. **Toy experiment**: primes 24–40 bits. Sample ~240 prime-order curves stratified:
   (i) random curves (control stratum); (ii) CM-constructed curves at extreme theta
   (|t| within 2^8 of the Hasse bound, D_0 in {-3,-4,-7,-8,-11,-19,-43,-67,-163}) and at
   theta ~ pi/2 (|t| < 2^8); (iii) curves with p-1 2^10-smooth; (iv) curves with N-1
   2^10-smooth (constructed by choosing N first, then searching t, p via the CM method with
   D_0 of class number <= 4); (v) special-form p = 2^k - c. Per curve: rho.negation and
   bsgs.negation charged S with >= 24 runs (ecbench, section 5a band), IC yield and
   charged S at the leaderboard's fixed B/arity. Preregister the feature list and a linear
   mixed model with stratum random effects; hold out 1/3 of curves. **Control arms**:
   label-permutation null; planted positive control = a stratum of cofactor-4 curves solved
   in the full group (a known arithmetic effect of exactly log 4 / 2 bits), which the
   instrument must recover. **Counted quantity**: charged S residual after N and |Aut|.
   **Falsifies H_rig**: a preregistered invariant whose held-out effect on any IC meter has
   a 95% CI excluding 0 and magnitude above the instrument floor (ICC detection limit as
   in LEAD-ICE-curve-presentation-invariance, ~0.2). Any such effect on rho/BSGS S is
   reported as instrument bias, not as a mechanism. **Supports H_rig**: all effects inside
   the floor; the atlas then gets one `measured` row that every future "numbers" idea must
   escape.
6. **Prior art**: Shoup 1997 generic lower bound (known, KR-RHO-13bf67); walk constants
   depend on the walk, not on arithmetic (Teske 2001; Bernstein–Lange 2012 "Two grumpy
   giants" — recalled). I recall no published regression of IC yield on arithmetic
   invariants of (p, N, t). `novelty_status: unverified` (the measurement, not the theorem).
7. **Rating**: speculative. Expected outcome is the null; the reason to run it is that
   the null is currently asserted from theorems about oracles plus within-class censuses,
   never measured across arithmetic strata, and the toy rho excess is unexplained.

Atlas phrases for the matcher: "arithmetic invariants predict charged ECDLP cost",
"Sato–Tate angle and rho constant", "smooth p-1 changes index calculus yield",
"arithmetic rigidity of ECDLP cost", "regress IC yield on conductor and class number".

---

## C2. Prime-field Koblitz analogue: the equality case of the orbit theorem, constructed and priced

**Class**: control (construction + cost measurement). **Rank 4.**

1. **Title**: Ordinary prime-field curves with CM by D_0 in {-7, -8, -4} whose group order
   N is a prime divisor of Norm(alpha^h - 1), alpha of norm 2, h ~ log_2 N — the extremal
   case of the cheap-endomorphism orbit theorem — and the charged price of rho on
   <alpha>-orbits.
2. **Object**: order O = Z[alpha] with Norm(alpha) = 2 (alpha = (1 + sqrt(-7))/2,
   sqrt(-2), or 1 + i). Norm(alpha^h - 1) = #E_0(F_{2^h}) for the binary curve E_0/F_2 with
   Frobenius alpha, so N := its prime part for h in [25, 45] (the K-163-style prime
   subgroup orders at toy m). A prime p = Norm(pi) with pi in O and Norm(1 - pi) = c N,
   c in {1, 2, 4}: pi = 1 - beta (alpha^h - 1) with beta a unit, alpha, or alpha-bar, giving
   e.g. p = Norm(2 - alpha^h) = 2N - 2^h + 2. On the resulting E/F_p with #E = cN, alpha
   acts on G as lambda with ord_N(lambda) = h exactly: the equality case
   n^h = 2^h ~ N of IDEA-20260901-6b63a4.
3. **Mechanism**: rho on classes {±alpha^i P} gains sqrt(2h) in steps; canonicalising a
   class costs s evaluations of alpha when only the subgroup <alpha^{h/s}> of order s is
   used. Net factor sqrt(s) / (1 + s c_alpha / c_step). With c_alpha (a degree-2 rational
   map, ~1I + 1M affine) about 0.4–0.6 of a point addition, the optimum s = 2 / c_alpha
   gives at most 1 / sqrt(2 c_alpha) ~ 1.0–1.1 and more likely < 1 once the negation
   class is already in use. Gain level: **constant, plausibly <= 1.1x, likely a loss**.
   This candidate exists because LEAD-STR-small-cm-disc-nonunit-endo's `revisit_when`
   names precisely this construction ("a prime-field curve where a norm-2 or norm-3
   endomorphism has eigenvalue order near log_n N ... Findings file NEW LEAD 1") and nobody
   has built it or priced it.
4. **Closest leads and why not foreclosed**:
   - LEAD-STR-small-cm-disc-nonunit-endo (closed_obstructed, kind: theorem). The theorem
     gives h >= log N / log n; the *net factor* clause is a cost-model estimate
     (sqrt(h)/kappa, kappa ~ h c(alpha)) that was never measured at the equality case.
     C2 does not claim "small CM discriminant makes ECDLP easier" generically; it builds the
     one family where the obstruction is tight and measures the constant. Partial-orbit
     canonicalisation (s << h) is not discussed in the lead.
   - LEAD-RHO-non-automorphism-equivalence (open_unexamined): multiplier subgroups H of
     (Z/N)^* with canonicalisation by scalar multiplication. C2 is the only case where the
     multiplier subgroup is realised by a degree-2 map rather than a scalar
     multiplication, so it is the best case for that lead's cost bound too.
   - LEAD-STR-automorphism-quotient-rho, LEAD-RHO-automorphism-class-walks (closed_known):
     |Aut| <= 6; C2 is explicitly beyond Aut.
5. **Toy experiment**: h in {29, 31, 37, 41} (N ~ 2^28–2^40); for each h try the 12 sign /
   conjugate / beta variants of pi, keep those with p prime (expected a few hits per h).
   Arms: (a) rho.negation on E (control); (b) rho on <-1, alpha^{h/s}> classes for
   s in {2, 3, 4, 8}, canonicalisation charged in the same ecbench cost model (counted field
   ops, not wall time); (c) the same s-class walk with alpha replaced by a *scalar*
   multiplication by lambda^{h/s} (prices the "cheap map" premium alone). Counted quantity:
   charged S ratio (b)/(a) with 95% CI over >= 24 runs. **Falsified** (lead stays closed,
   now with a measured constant) if every s gives ratio >= 0.95; **kept alive** only if some
   s gives ratio < 0.90 with CI excluding 1, which would be a new constant-level lead and
   would also decide LEAD-RHO-non-automorphism-equivalence's cost question at its best case.
6. **Prior art**: Koblitz 1991, Solinas 2000 (Frobenius classes on binary curves, known);
   Duursma–Gaudry–Morain 1999 (rho with automorphisms, known); Galbraith, *Mathematics of
   Public Key Cryptography* ch. 14 remarks that non-automorphism endomorphisms do not give
   usable equivalence classes because the orbit must be computed (recalled, unverified).
   I know of no published construction of this equality-case family. `unverified`.
7. **Rating**: likely-closed-on-inspection. Constant at best; its value is turning a
   cost-model clause in a `kind: theorem` closure into a measurement and discharging the
   atlas's own reopen condition.

Atlas phrases: "prime-field Koblitz analogue", "norm-2 endomorphism orbit rho",
"equality case of the orbit theorem", "N divides Norm(alpha^h - 1)", "partial orbit
canonicalisation".

---

## C3. Smooth-(p-1) toy fields as the instrument for the open pairing-free F_p^* exits

**Class**: tooling / measurement. **Rank 3.**

1. **Title**: Run the Miller-cocycle / zeta-defect equidistribution test at 48–64-bit p by
   choosing p with p-1 B-smooth, so the F_p^* discrete log is free and the only cost is the
   curve side.
2. **Object**: primes p with p - 1 2^12-smooth and a prime-order curve E/F_p with
   gcd(N, p-1) = 1 (the lead's standing assumption). Deployed analogue: the STARK prime
   p = 2^251 + 17·2^192 + 1 has p - 1 = 2^192 · (2^59 + 17), and 2^59 + 17 ends in 5, so
   5 | (2^59 + 17) (checked by arithmetic); the remaining cofactor ~2^56.7 is of unverified
   primality, so F_p^* DLP there costs at most ~2^29 generic steps by Pohlig–Hellman.
3. **Mechanism**: none for ECDLP cost. The open test in LEAD-TRF-miller-cocycle-nonhom-
   transfer (`open_unexamined`) and LEAD-EXO-miller-pairing-cocycle (`open_next_step`) needs
   ell(k) = log_g U(kP) in Z/(p-1) for many k; at p beyond ~2^30 the F_p^* log becomes the
   experiment's bottleneck unless one implements NFS. Smooth p-1 removes that bottleneck,
   letting the equidistribution and character-correlation statistics run where finite-size
   artefacts (small N, few k) no longer confound a null. Secondary observation, stated as a
   conditional only: *if* any non-homomorphic F_p^* exit ever carried structure in k,
   fields with smooth p-1 (the STARK field) are where its F_p^* side is cheapest, so they
   are the natural first targets of such a test — not a weakness claim.
4. **Closest leads and why not foreclosed**: LEAD-TRF-miller-cocycle-nonhom-transfer and
   LEAD-EXO-miller-pairing-cocycle own the hypothesis; C3 advances their `next_action` with
   a better instrument rather than proposing a different step. LEAD-TRF-mov-small-embedding-
   degree / KR-RHO-53c89f: not a pairing transfer (N does not divide p-1 by construction).
   LEAD-ICP-algebraic-membership-factor-base uses B | p-1 for a multiplicative-subgroup
   factor base; different use of the same arithmetic. No forecloses phrase matches
   "smooth p-1 as an experimental instrument".
5. **Toy experiment**: p in [2^48, 2^64] with p-1 2^12-smooth (dense enough to find by
   sieving k·M + 1); E with prime N (Schoof/SEA via PARI at this size), gcd(N, p-1) = 1.
   Compute ell(k) for k in a random sample of 2^16 scalars and for structured k (powers of
   2, small k). Statistics: chi-square against uniform on Z/(p-1) at the 1/p rate; max
   correlation with additive characters of Z/N; the lead's "Smart-ratio" success. **Positive
   control**: a toy with N | p-1 (embedding degree 1) where U is replaced by the reduced
   Tate pairing, which *is* a homomorphism — the statistic must detect it. **Negative
   control**: a random oracle in place of U. **Falsifies the transfer lead** (closes it at a
   scale where "toy" is no longer an excuse): equidistribution at the 1/p rate and no
   character correlation above the random-oracle arm. Any correlation would be the first
   one-point transfer signal and would need full cost accounting.
6. **Prior art**: Pohlig–Hellman 1978 (known). The use of smooth-(p-1) fields as a test
   bed for non-homomorphic exits: none recalled. `unverified`.
7. **Rating**: speculative, instrument only. It cannot produce a speedup; it can close two
   open leads cleanly or surface the one signal they are waiting for.

Atlas phrases: "smooth p-1 toy field for Miller cocycle test", "Pohlig–Hellman side of a
pairing-free exit", "STARK prime multiplicative group smooth", "F_p^* log free at
medium scale".

---

## C4. The (p, N) dual curve: E~/F_N with #E~(F_N) = p and the same CM order, as a cross-field same-order control

**Class**: control. **Rank 5.**

1. **Title**: For every ordinary prime-order E/F_p there is a curve E~ over F_N with p
   points and End order containing the same Z[pi] (D = t^2 - 4p = (2 - t)^2 - 4N); use the
   pair as a same-order, different-field control for "attack cost is a class invariant".
2. **Object**: the ideal n = (1 - pi) of norm N in O = Z[pi]; the Frobenius of E~ is
   1 - pi (trace 2 - t). (E, E~) is an amicable pair / 2-cycle in the sense of
   Silverman–Stange; deployed 2-cycles exist (Pallas/Vesta, BN254/Grumpkin, MNT4/MNT6), all
   with small D_0.
3. **Mechanism**: no cost mechanism is known or claimed; the groups have coprime orders
   and no homomorphism relates them. What the pair offers is two ECDLP instances in
   *different* fields whose End orders and class groups coincide. RESEARCH_ISOGENY_FIBERS_
   ECDLP R5.4 asserts every known attack-family cost is a class invariant *within F_p*; the
   dual asks whether any heuristic IC meter is an *End-order* invariant across fields. The
   rigidity prediction (C1) is: no shared deviation beyond size normalisation. Gain level if
   the prediction fails: constant.
4. **Closest leads and why not foreclosed**: LEAD-STR-class-group-ecdlp-bridge (open): the
   simulation lemma must hold for E and E~ with the same Cl(O) simultaneously — a sanity
   check, not a bridge map; none of "class group action solves ECDLP", "ray class group
   torsor bridge" is claimed. LEAD-STR-isogeny-class-generic-invariance and
   LEAD-ICE-curve-presentation-invariance: within one field. LEAD-TRF-cm-canonical-lift-
   heights (closed): C4 never lifts; it works with two finite reductions, constructible
   for small D_0 only (the Hilbert class polynomial is needed to write E~, so at
   deployed-size D the dual exists but cannot be written — this is the same h(D) ~ p^{1/2}
   wall and C4 does not pretend otherwise).
5. **Toy experiment**: D_0 in {-3, -4, -7, -8, -11, -19, -43}, conductors f in {1, 3, 5},
   24–32-bit (p, N) pairs with both p and N prime and both curves of prime order
   (CM construction on both sides). Measure charged IC yield and S (fixed B/arity) on E and
   on E~, normalise by field size, and compare the paired residual against residuals of
   random (p, N') pairs of the same sizes. Counted quantity: paired correlation of
   normalised IC residuals; **falsified as a lever** if it is indistinguishable from the
   random-pair control (expected). Secondary: confirm rho S is identical after size
   normalisation (sanity for the instrument).
6. **Prior art**: Silverman–Stange, "Amicable pairs and aliquot cycles for elliptic
   curves", Exp. Math. 2011 (retrieved: existence of cycles of every length; no
   cryptanalytic content); Chiesa–Chua–Weidner, "On cycles of pairing-friendly elliptic
   curves", 2018 (recalled from a citation list, not opened; constructs cycles, no attack).
   Web search found no attack literature on cycles. `unverified`.
7. **Rating**: speculative / low. A clean control that costs little; no mechanism.

Atlas phrases: "dual curve over F_N with p points", "amicable pair of elliptic curves
ECDLP", "2-cycle of curves same CM order", "swap p and N", "cross-field same-order
invariance".

---

## C5. Recurring-obstruction statement (synthesis, no new experiment)

Not filed as a lead; recorded so the Coordinator can see the bridge. Across this family,
closures cite three obstructions (Tate class-invariance; orbit theorem + GGM simulability of
endomorphism images; lift growth). The theorem side is complete internally
(KN-FIND-002, KN-FIND-b7e091, IDEA-20260901-6b63a4, KR-RHO-817bf8). The measurement side
is C1. I recommend the atlas record, once C1 runs, a single `measured` row "arithmetic of
(p, t, D, f, p±1, N±1) does not move charged cost beyond N, |Aut|, step cost at toy scale"
and point every number-structure lead's `related` at it.

---

## Candidates drafted and dropped (rephrases)

- **Smooth quadratic-twist order N' = p + 1 + t as a lever via x-only (Kummer) walks**:
  the x-only multiplication maps preserve each half of P^1(F_p); E(F_{p^2}) ~ E(F_p) x
  E'(F_p) separates by Pohlig–Hellman; no transfer. Foreclosed by LEAD-STR-safecurves-
  parameter-audit ("twist security breaks the discrete log") and KR-RHO-817bf8.
- **Smooth N-1 / N+1 without auxiliary inputs**: every route needs [k^i]P or a cheap
  multiplier of small order; LEAD-RHO-cheon-aux-acquisition ("self-supplied auxiliary
  powers"), LEAD-RHO-cheon-deployed-applicability, LEAD-RHO-non-automorphism-equivalence.
- **Special-form p (Solinas / Crandall / Mersenne) and polynomial p(u) families as a
  relation source**: LEAD-TRF-global-lift-small-height, LEAD-EXO-global-lift-height,
  LEAD-ICP-char0-lifting-xedni-smoothness ("SNFS number field lift", "smoothness of
  integer lifts"), LEAD-ICP-xedni-function-field-sections ("specialise sections").
- **Hasse-boundary traces (|t| ~ 2 sqrt p)**: equivalent to small |D|;
  LEAD-STR-small-cm-disc-nonunit-endo, LEAD-STR-special-j-ic-semaev.
- **Conductor f divisible by small l giving cheap full l-torsion over F_{p^m},
  m = ord_l(t/2)**: LEAD-STR-torsion-module-leak ("l-torsion Galois module carries
  information about k"); the Tate pairing with E[l] kills G.
- **u-adic scalar structure of BN/BLS orders N(u)**: u^2 is already the j = 0
  automorphism eigenvalue; u itself is not a cheap endomorphism; LEAD-STR-automorphism-
  quotient-rho and LEAD-RHO-cheon-deployed-applicability ("powers-of-tau").
- **Genus characters of Cl(O) computable by pairings**: published (Castryck–Sotáková–
  Vercauteren 2020, recalled) and about the class-group action, not ECDLP.

## Possible mis-dispositions or atlas hygiene noticed

1. **Duplicate coverage**: LEAD-TRF-miller-cocycle-nonhom-transfer (`open_unexamined`)
   and LEAD-EXO-miller-pairing-cocycle (`open_next_step`) both own IDEA-20261017-e3a6f1
   with the same hypothesis H1/K1/K2 and neither lists the other in `related`. One should
   name the other (or be `closed_dominated`); their dispositions also disagree on whether
   a concrete next step exists.
2. **Kind of closure**: LEAD-STR-small-cm-disc-nonunit-endo is `closed_obstructed` with
   `kind: theorem`, but the load-bearing "net factor" clause is a cost-model estimate
   (sqrt(h)/kappa) never measured at the equality case its own `revisit_when` describes.
   `kind: cost_model` would be the honest label; C2 is the measurement that would settle it.
3. **KR-RHO-53c89f** rests on five `abstract_read` sources and no curated full text for
   the Semaev/Satoh–Araki/Smart claim; fine as a textbook fact, but a reviewer chasing it
   has nothing to open.

## Honest-accounting block

- **Imagined outcomes**: none reported; every predicted direction above is labelled as
  prediction. Expected outcomes for C1, C3, C4 are nulls.
- **Exponent claims**: none. Best case anywhere in this family is a constant (C2,
  <= ~1.1x and probably < 1).
- **Unverified facts**: 2^59 + 17 is divisible by 5 (last digit); the cofactor's
  primality is unverified. All literature marked `recalled` was not opened this session;
  Silverman–Stange is `retrieved` (abstract-level via search results only).
- **What I did not do**: run `tools/lead_atlas.py --match` (no shell); read `ledger/
  proposals` bodies beyond titles and keyword hits; check `tools/obstruction_registry.py
  --unexamined`. The top-level session should run `--match` with the atlas phrases listed
  under each candidate.
- **Scope**: toy and public parameters; no deployed key; the STARK-field remark is a
  conditional statement about where a hypothetical signal would be cheapest to test, not a
  claim of weakness.
