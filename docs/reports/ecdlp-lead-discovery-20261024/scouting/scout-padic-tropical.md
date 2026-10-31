# Scout dossier: p-adic and tropical geometry (final lead-discovery round, round 2)

Field: Berkovich/tropical structure of E over Q_p, formal groups and canonical lifts, Kedlaya/Harvey-style
p-adic (and étale) cohomology for point-count and character-sum statistics, p-adic valuations of Semaev systems,
tropical root counting, Newton-polygon methods for decomposition. Written 2026-10-24 by one agent. This is a
proposal dossier: nothing here changes any record, and no repository was edited.

**Round-1 file.** An earlier session wrote a dossier at this path (18:50). I copied it unchanged to
`scout/scout-padic-tropical.prev-1850.md` (and `scout/scout-padic-tropical.round1.md`). I did not run its scripts
and I report none of its numbers as mine. Section 8 lists which of its claims I reproduced with my own code.

**Labels.**
- **produced**: I computed it in this session. The script and output files are listed in section 7, all under
  `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/padic-tropical-r2/`.
- **derivation**: an argument I wrote here. It has not been reviewed.
- **prediction**: an expected value that nobody has measured. Each one cites a numbered heuristic (H1-H6).
- **Citation provenance**:
  - **retrieved**: I fetched the source in this session (arXiv page or PDF text) and checked the statement used.
  - **recalled**: from memory, not checked.

## 0. Verdict

Two walls close this field for exponent-moving prime-field work.

**Wall P (coprimality).**
- Every p-adic object attached to E/F_p is a pro-p group or a Z_p-module. This covers the formal group, the
  kernel of reduction E(Z/p^k) -> E(F_p), Witt and Teichmüller digits, and Serre-Tate deformations.
- The prime-order subgroup G has order N != p. So Hom(G, A) = 0 and Ext^1(Z/N, A) = 0.
- Every homomorphic read-out is therefore zero, and every non-homomorphic one is a function of the encoding.
- This is SO-PADIC.

**Wall T (trivial valuation).**
- F_p carries only the trivial valuation. Every lift of E/F_p to Q_p has good reduction, so its Berkovich skeleton
  is a point (Baker-Payne-Rabinoff; recalled).
- On the factor-base locus, every lift of a Semaev system has exactly one source-bearing tropical cell: w = 0.
  Its initial form is the mod-p system itself (C3).

What the field does supply is **cheap proofs that decide open leads** (C1-C4) and **one census instrument** on the
Koblitz side (C5).

- **C1 and C2 decide both B7 Miller leads.** They use two external ingredients:
  - the Lauter-Stange perfectly periodic EDS;
  - a Weil-Deligne bound, with constant 2, on character sums of the Miller function twisted by group characters.
  Both are verified at toy size with my own code. The Weil bound is attained to 1.99995·sqrt(p) and never exceeded.
  The Smart-ratio arm of H1, which no character bound covers, is measured null (|z| ≤ 2.01, 3 curves per arm).
  The zeta-defect component of the transfer lead stays open.
- **C3 closes the p-adic tropical decoder proposal (B1).**
- **C4 is a MERGE item for the lattice scout's corner lemma (B1).** It is an unconditional "no short vector at
  all" version.
- **C5 lifts the g = 6 census impediment** of LEAD-ICB-nonlinear-frob-stable-bases (617 classes). It also
  exhibits an explicit genus-6 curve over F_2 whose Jacobian has exactly 131 points, recounted to F_{2^12}. The
  g = 5 hits were already in EV-BINSTD-2d41c3.

Every candidate's predicted exponent gain is 0. That is the correct reading of this field, not a shortfall in the
search. I found no in-field ingredient for B2, B3, B4 or B6 (section 5). One out-of-field note on B6 goes in
section 4 (K15) as a correction.

## 1. Inputs read

**Program files.**
- ATLAS.md, all eight families and the open-steps table, read fully.
- KRMAP.md, all 51 rows.
- object-frame-ideation.md, sections 1-3.
- idea-generator.md: "Search heuristics" and "Obstructions as generative material".
- target-result-profile.md, Parts A-B.
- LEADERBOARD Tables A-D and the phase shares.
- FRONTIER (prime toy and Koblitz sections).

**Lead YAMLs, read in full.**
- Leads I act on: LEAD-EXO-miller-pairing-cocycle, LEAD-TRF-miller-cocycle-nonhom-transfer,
  LEAD-RHO-non-automorphism-equivalence, LEAD-ICP-lattice-ic-relation-construction, LEAD-EXO-elliptic-net-eds,
  LEAD-ICB-nonlinear-frob-stable-bases.
- I extracted the obstruction.statement of every SO lead I quote below by script from the YAMLs, not from the
  atlas rendering.

**Ledger records, read by path.**
- IDEA-20261017-e3a6f1 (the Miller primitive U and its claims K1, K2, H1).
- IDEA-20260814-c3af09 (the p-adic tropical decoder).
- IDEA-20261016-09fd08 and IDEA-20261009-c8433d (claims only).
- EV-BINSTD-2d41c3 and EV-FROB-a85eaf (census status).
- KN-LIT-247: a bulk-seeded Lauter-Stange entry, abstract only, `citation_verified: read`.

**Dedup.**
- I grepped `ledger/.index/{proposals,hypotheses}.jsonl` for: Lauter, perfectly periodic, Kummer sheaf, Weil
  bound, Deligne, Kohel, tropical, initial form, strong Gr, leading coefficient ideal, Couveignes, 131
  hyperelliptic, LMFDB, H-EWALK.
- No record states C1-C4. Lauter-Stange appears only as an elliptic-net zero-set citation. The "Weil bound" hits
  are about subspace-base abscissa density and conductors.
- I grepped the sibling scout files for Lauter, Stange, corner, strong Gr, H-EWALK, Couveignes, "131 |" and
  tropical. Two overlaps matter:
  - `scout-lattice-smallroot.md` already holds the corner lemma (determinant form). C4 is filed as a merge.
  - No sibling has the Miller/EDS identity, the Weil bound or the valuation lemma.

**Matching.** I ran `lead_atlas.py --match` and `build_frontier_map.py --match` on all 15 phrasings below. The
log is `padic-tropical-r2/match-log-r2.txt`.

## 2. Field walls, written out

**Wall P.** The quoted obstruction.statement of LEAD-TRF-padic-canonical-section (SO-PADIC) is:

> "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal
> logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any
> non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen
> criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope:
> non-anomalous prime-field curves, all lifts of E."

The companion statement, LEAD-EXO-padic-jet-canonical-lift, reads:

> "For gcd(n,p)=1 the prime-to-p torsion lifts uniquely (finite etale) with zero formal defect and multiplication by
> l is invertible on every native jet, formal and p-typical target, so every additive order-l image is zero ...
> IDEA-436 D1 valuation profile collapses to the +/- fibre indicator (KN-FIND-1ba0fe). Scope: ordinary prime-field
> curves, toy primes 10-14 bits for the measured parts."

**Wall T.** A non-zero residue coefficient is a unit in every lift. A non-zero residue coordinate is a unit in
every lift. C3 turns this into a statement about tropical branches.

## 3. Candidates

### C1 (prime field, B7). The Miller primitive U is the Lauter-Stange perfectly periodic EDS ratio. Extracting k from it is EDS Association.

**Bottleneck.** B7. The lead is LEAD-EXO-miller-pairing-cocycle (open_next_step). Its next step is:

> "Verify ... K1 ... and K2 (U(kP)=c*r_k*C^(k/N), r_k=psi_{k-1}/psi_k) exactly on toy prime-order curves with
> gcd(N,p-1)=1, then measure whether k can be recovered from U(kP) in fewer than sqrt(N) group operations once r_k is
> charged."

It pre-registered this discriminator:

> "If K2 holds and r_k needs k (division-polynomial values), the primitive collapses into the closed elliptic-net
> lead and this lead closes as obstructed".

**External ingredient.** K. E. Lauter and K. E. Stange, "The elliptic curve discrete logarithm problem and
equivalent hard problems for elliptic divisibility sequences", SAC 2008, LNCS 5381 (2009), pp. 309-327,
arXiv:0803.0728. **Retrieved**: I fetched the arXiv page and the v2 PDF this session and extracted the text. The
parts used:
- **Theorem 6, eq. (3).** For P of order coprime to q-1 and greater than 3, φ(P) = (W_{E,P}(q-1)/W_{E,P}(q-1+ord P))^{1/ord(P)^2}.
  The sequence φ([n]P) is a perfectly periodic EDS equivalent to W_{E,P}.
- **Theorem 8.** φ(Q) is computable from Q in O((log q)^3), without knowing k.
- **Theorem 10 and eq. (6).** Given W(k), W(k+1), W(k+2), computing k reduces to one discrete log in F_q^*.
- **Problem 2 (EDS Association).** Determine W_{E,P}(k) from P and Q = [k]P.
- **Theorem 1.** EDS Association (non-perfectly-periodic case) is sub-exponential iff ECDLP is.
- **Theorem 7 (Shipsey).** W(t) costs O(log t (log q)^2).

**Erratum candidate (produced).** In the pdftotext extraction, eq. (4) reads φ([n]P) = φ(P)^{n^2-1} W(n). The
superscript layout is ambiguous, and I did not check the LNCS version.
- As extracted, the formula fails at n = 1 unless φ(P) = 1.
- With φ defined by eq. (3), φ([n]P) = φ(P)^{n^2} W(n) holds on 600/600 random k (150 on each of 4 curves), and the
  n^2-1 form on 0/600 (`ls_eq4_check_r2.out`).
- Eq. (6) and everything below are unaffected, because only ratios are used.

**Derivation.**
1. From the corrected eq. (4), r_k = W(k-1)/W(k) = φ(P)^{2k-1} · φ((k-1)P)/φ(kP).
2. U(kP) and φ((k-1)P)/φ(kP) depend only on k mod N. So K2's factor φ(P)^{2k} C^{k/N} must be N-periodic. Since
   gcd(N, p-1) = 1, F_p^* has no non-trivial N-th roots of unity, which forces D := C^{1/N} = φ(P)^{-2}.
3. Hence **U(R) = c' · φ(R-P)/φ(R) on G \ {O, P}**. All the k-dependence of K2 sits in r_k, the
   non-perfectly-periodic EDS ratio.
4. Computing r_k (with one neighbouring term) from kP yields k after one F_p^* discrete log, which costs
   L_p[1/3] (LS Theorem 10; it needs φ(P) of large order). Conversely, r_k costs O(log k) once k is known
   (Theorem 7).
5. So "remove r_k without k" is EDS Association, which is ECDLP up to a sub-exponential F_p^* DLP (LS Theorem 1).
   U itself is a function of R that is computable in O(log N) by Miller's loop. Recovering k from U(kP) is
   therefore recovering k from kP.

**Produced verification** (`miller_eds_r2.py` -> `miller_eds_r2.out`, written from scratch).
- **Setup.** Six random prime-order curves (so gcd(N, p-1) = 1):
  - p = 10007, 20011, 30011 (random primes);
  - p = 16381 = 2^14-3, 19681 = 3^9-2 and 32749 = 2^15-19 (special-form primes).
  - U is computed by a binary Miller loop with monic lines and verticals. φ comes from eq. (3) and the corrected
    eq. (4).
- **Results.**
  - U(R)·φ(R)/φ(R-P) takes **exactly 1 value** per curve, over all 9,932 / 20,066 / 29,882 / 16,232 / 19,444 /
    32,564 evaluable k. The pole hits of the chain are 37-43 per curve.
  - The other candidate form, U(R)·φ(R+P)/φ(R), takes N/2 values.
  - K2 holds on **100% of evaluable k** on all six curves. The fitted D equals the predicted φ(P)^{-2} on 6/6.

**Pair and class.** The representation is an F_p^*-valued EDS normalisation of the point (R3, non-function
coordinates). The operation set is translation by P, acting through the line cocycle (K1). The class is
**coordinate-dependent**: U is a fixed function of R and carries nothing beyond R.

**SO codes touched, and the premise each one escapes.**
- **SO-NET** (LEAD-EXO-elliptic-net-eds):
  > "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002:
  > net oracle GGM-simulable with O(log N) overhead); standard Hankel displacement rank of translated x-blocks is
  > tautological and consecutive blocks have linear complexity >= (M-2)/3 (IDEA-006 gate). Measured at toy prime
  > fields p in {101,431,1601}, n <= 1607: collision statistics are random-oracle-equivalent and the charged
  > k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting, with the sieve/BSGS gap growing
  > (24x -> 135x)." (no Scope clause in the YAML)

  The Miller idea escaped the premise "net relations": U is a one-point map into F_p^*, not a relation. C1 shows
  that the map is the perfectly periodic member of the same EDS family. So it lands inside SO-NET after all, with
  EDS Association (LS Problem 2) as the hard core.
- **SO-PAIR** (LEAD-TRF-second-torsion-direction):
  > "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k -
  > 1 ... Scope: ordinary and supersingular curves over F_p, prime N."

  U needs no second torsion direction (escapes the premise "E(F_{p^k})[N] larger than the rational line"). Nothing
  is gained by escaping it.
- **SO-GEN** (LEAD-EXO-augmented-oracle-ggm):
  > "Each named oracle is GGM-simulable ... Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."

  U reads coordinates, so it escapes "GGM-simulable oracle". The closure comes from the LS reduction, not from GGM.

**First discriminating step** (already run at toy size): exact toy identity plus the derivation above. The
remaining step is a review of the derivation. Outcomes map to dispositions as follows.
- **Identity holds and the derivation survives review →** LEAD-EXO-miller-pairing-cocycle becomes
  **closed_obstructed (kind: proof)**, by its own pre-registered rule. It collapses into LEAD-EXO-elliptic-net-eds.
  KN-LIT-247 should be upgraded from abstract-only, and a KR row is warranted.
- **Identity fails on some family →** **open_next_step** for that family. best_measured: "U·φ(R)/φ(R-P) constant
  on 6/6 curves, 100% of evaluable k" (j = 0 and j = 1728 families with gcd(N, p-1) = 1 were not tested).
- **Someone exhibits a cheap r_k from kP →** that is itself a sub-sqrt ECDLP algorithm by LS Theorem 10. That
  would be **open_next_step** with a full charged comparison. It is not predicted.

**Tier and gain.** Tier X. **Predicted gain: 0 in the exponent.**
- H1: none needed for the closure. It is a reduction (LS Theorems 1 and 10, plus Theorem 7 for the converse),
  plus an identity checked exactly on toy curves.

**Costs.** Implementation: done (about 2 h). Compute: minutes. Self-kill risk: low (it is a closure).

**Match phrasings.**
1. "Miller primitive U = f_{N,P}^{1/N} equals the Lauter-Stange perfectly periodic EDS ratio phi(R-P)/phi(R)"
2. "recovering the scalar from the Miller function value is as hard as computing the elliptic divisibility
   sequence term"
3. "Somos identities hold for every k so net relations encode the group law on one k-fibre and not k; EDS
   association"

Atlas top hits: LEAD-EXO-miller-pairing-cocycle, LEAD-TRF-miller-cocycle-nonhom-transfer and
LEAD-EXO-elliptic-net-eds. No KR row matches. The map has no Lauter-Stange row.

### C2 (prime field, B7). A Weil-Deligne bound with constant 2 for the Miller primitive twisted by group characters. The character-correlation part of H1 of e3a6f1 becomes a theorem; its Smart-ratio part is measured null.

**Bottleneck.** B7. The lead is LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined). Its next step is:

> "Test H1 of IDEA-20261017-e3a6f1 at toy size: equidistribution of ell(k) = log_g U(kP) in Z/(p-1), Smart-ratio
> success and correlation with characters of Z/N, on special and matched random p, with planted-structure positive
> control."

Its discriminator:

> "Equidistribution at the 1/p rate closes the lead (a non-homomorphic map of this kind is a hash); any character
> correlation would be the first one-point transfer signal".

**External ingredients.**
- The Weil bound for multiplicative character sums on curves, in the étale form: Grothendieck-Ogg-Shafarevich for
  the Euler characteristic of a tame rank-one sheaf, plus Deligne's Weil II for weights. **Recalled.**
- Kohel-Shparlinski, "On exponential sums and group generators for elliptic curves over finite fields", ANTS-IV,
  LNCS 1838 (2000), pp. 395-404, Corollary 1: sums over E(F_q) twisted by a group character are << q^{1/2}.
  **Retrieved**, as restated in Ahmadi-Shparlinski, arXiv:1302.4210, Lemma 1, whose text I extracted this session.
  That lemma is the additive-character version. The multiplicative version with explicit constant 2 below is my
  **derivation**.

**Theorem (derivation).** Let E/F_p have prime order N, let P generate it, and let f = f_{N,P} be monic at O. Set
N' = N^{-1} mod (p-1). Then for every non-trivial character χ of F_p^* and every character ψ of E(F_p):

  |S(χ, ψ)| = |Σ_{R ∈ E(F_p) \ {O,P}} χ(U(R)) ψ(R)| ≤ 2 sqrt(p).

*Proof sketch.*
1. χ(U(R)) = χ^{N'}(f(R)). Let F = L_{χ^{N'}}(f) ⊗ L_ψ on V = E - {P, O}. Here L_ψ is the rank-one lisse
   sheaf pushed from the Lang torsor X -> Frob(X) - X. It is unramified, with weight 0.
2. div f = N(P) - N(O). So F is tamely ramified at P with local monodromy (χ^{N'})^N = χ ≠ 1, and similarly at O.
3. Grothendieck-Ogg-Shafarevich gives χ_c(V, F) = 2 - 2g - 2 = -2.
4. H^0_c vanishes because V is open. H^2_c vanishes because F is geometrically non-trivial (it is ramified at P).
   So dim H^1_c = 2. Weights are ≤ 1, so |S| ≤ 2 sqrt(p).
5. The **control** is N | p-1. There χ can be chosen with χ^N trivial at P. F is then unramified and can be
   geometrically trivial. The sum peaks: that is the Tate pairing.

*Consequence.* Every bilinear character test of (log U(kP), k) has square-root cancellation. That is the
character-correlation part of H1 of e3a6f1, "ell is uniform on Z/(p-1) jointly with characters of Z/N", and it now
follows from the bound. Its discrepancy is O(sqrt(p) log p), and normalised correlations are at most 2/sqrt(p).

H1 has a third clause, "Smart-ratio success 1/p". It concerns a specific predictor, not a character, so the bound
does not cover it. I measured it instead (below).

**Produced verification** (`weil_bound_r2.py` -> `weil_job{0..7}.out`; full sums with no missing terms).
- **Setup.**
  - Six fresh prime-order curves: random p = 10007, 20011, 30011 and special p = 2^14-3, 3^9-2, 2^15-19.
  - Every R ∈ E(F_p) \ {O, P}. Pole hits of the binary chain were refilled through K1.
  - K1 was first verified on about 3,990 random pairs per curve. It takes a single constant value ε = -1 on every
    curve, so T(R)T(S) = -T(R+S)·g_{R,S}(P)^N.
  - A NAF Miller chain agreed with the binary chain on all doubly evaluable points.
  - Worst case over 256 multiplicative characters (including a = 1, 2, (p-1)/2, (p-1)/q and N mod (p-1)) × all N
    group characters.
- **Results.**

  | p | N | terms | max \|S\|/sqrt(p) |
  |--:|--:|--:|--:|
  | 10007 | 10069 | 10067 | 1.99995 |
  | 20011 | 20231 | 20229 | 1.99996 |
  | 30011 | 30347 | 30345 | 1.99998 |
  | 16381 (2^14-3) | 16187 | 16185 | 1.99995 |
  | 19681 (3^9-2) | 19753 | 19751 | 1.99996 |
  | 32749 (2^15-19) | 32869 | 32867 | 1.99996 |

  The bound 2 sqrt(p) is attained to five digits and never exceeded.
- **Positive controls** (N | p-1, #E = p-1 = 2N; p = 10007 with N = 5003, and p = 20123 with N = 10061): |S| =
  5001 and 10059, i.e. every term aligned, a full peak.
- **The pre-registered spectral statistic** (`miller_eds_r2.out`, partial sums over evaluable k): max |F|^2/n over
  256 multipliers × N frequencies is 4.43-4.74 on the six curves. Compare:

  | statistic | value |
  |:--|--:|
  | max \|F\|^2/n, the six test curves | 4.43-4.74 |
  | shuffled-ell null | 14.3-16.1 |
  | random-function null | 14.4-15.4 |
  | ln(MN) | 14.8-15.9 |
  | pre-registered threshold ln(256N)+12 | 26.8-27.9 |
  | fraction of cells with \|F\|^2/n > 4, test curves | 0.0010-0.0021 |
  | fraction of cells with \|F\|^2/n > 4, nulls (about e^{-4}) | 0.018 |

  The spectrum is *flatter* than random, which is what h^1 = 2 predicts.
- **Smart-ratio arm (produced; `smart_ratio_r2.py` -> `smart_job0..5.out`).** This uses the same six curves as
  `miller_eds_r2`. e3a6f1 defines no formula for the test. I transplanted the ratio test from IDEA-20261016-09fd08
  ("Z's Smart ratio equals d iff ...") to the multiplicative primitive:
  - Take k0 = the smallest k ≥ 2 with ell(k0) a unit mod p-1. Guess khat = k0·ell(k)/ell(k0) mod (p-1), and count
    successes khat ≡ k.
  - Successes were 1, 2, 1 on the random-prime arm (expected about 1.0; z = 0.01, 1.00, 0.00) and 0, 0, 3 on the
    special-prime arm (z = -1.00, -0.99, 2.01).
  - So |diff| < 4 sd on both arms, which is e3a6f1's pre-registered reading.
  - The strong linear form is the largest number of k sharing one c = ell(k)/k mod (p-1). It came out at 4-6,
    against Poisson 5% maxima of 5-7.
  - **Scale caveat:** 3 curves per arm, against the 30 per arm that e3a6f1's minimal_test specifies.
- Arbitrary (table) predictors are not covered by any test or bound. U is a function of R, so "solve the DLP from
  R" is formally a predictor.

**Pair and class.** As in C1, the class is **coordinate-dependent**. The bound says the coordinate dependence is
invisible to every multiplicative × group character test.

**SO codes touched.**
- **SO-PADIC** (quoted in section 2). U is not a section of reduction and not a p-adic object, so it escapes the
  premises "section" and "all lifts of E". The theorem gives the analogue of that obstruction's "recovers d only at
  the random 1/p rate" for this non-p-adic map.
- **SO-TORS** (LEAD-STR-torsion-module-leak):
  > "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the
  > prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A
  > non-homomorphic point statistic is a function of the encoding of Q. ... Scope: prime-order G, any l != N."

  The target F_p^* is not l-primary in general, so U escapes the premise "l-primary group". Same conclusion.
- **SO-PAIR** (quoted in C1). The N | p-1 control is exactly the case that obstruction keeps open, and it peaks as
  it should.

**First discriminating step** (run). Dispositions:
- **Bound holds on every curve, the controls peak and the Smart-ratio arm is null (all observed) →** two
  components are decided:
  - the U component: its character part by proof, its Smart-ratio part measured at 3 curves per arm;
  - the generalized-Jacobian component (c8433d), which its own claim identifies with the Tate pairing, i.e. SO-PAIR.

  For both, the record is **closed_obstructed (kind: proof for the character part; Smart-ratio arm measured at
  reduced scale)**. A 30-curve-per-arm Smart-ratio replication is a cheap optional confirmation.
- **The zeta-defect component (IDEA-20261016-09fd08) is not covered.** Z is the additive primitive of the slope
  cocycle, Z(R+S) = Z(R)+Z(S)+λ(R,S). By its own definition Z(R) = -(1/n)Σ_S λ(R,S), a sum over all N points, so
  it is not shown to be a low-degree function. An Artin-Schreier analogue of this bound would be vacuous for it.
  - What I can add is a one-line derivation (mine, not run). Unrolling the cocycle gives Z(kP) = kZ(P) + g_k with
    g_k = Σ_{i<k} λ(iP, P). So a cheap carry g_k from kP would give k mod p whenever Z(P) ≠ 0. The carry is
    ECDLP-equivalent, which is the same pattern as r_k in C1.
  - So the lead as a whole is **open_next_step**, with only the Z component (and optionally the full-scale
    Smart-ratio replication) left. It goes to **closed_obstructed** if the coordinator accepts the carry derivation
    for Z. best_measured: "max |S| = 1.99995 sqrt(p) on 6 curves; controls peak at N; Smart-ratio |z| ≤ 2.01 on
    both arms".
- **Any curve with |S| > 2 sqrt(p) →** the derivation is wrong. The lead goes to **open_next_step**, with that
  curve as best_measured.

**Tier and gain.** Tier X. **Predicted gain: 0.**
- H2 (rigorous bound, not a heuristic): every non-trivial (χ, ψ) correlation is at most 2/sqrt(p) in normalised
  size. The prediction for unrun curves is max |S|/sqrt(p) ∈ [1.9, 2.0] whenever about 256 multipliers × N
  frequencies are scanned (the bound is near-attained when the scan is large).

**Costs.** Implementation: done. Compute: about 2 minutes per curve. Self-kill risk: low.

**Match phrasings.**
1. "Weil-Deligne bound 2 sqrt(p) for multiplicative characters of the Miller function twisted by group characters
   of E(F_p)"
2. "the log of the Miller value is equidistributed and uncorrelated with the discrete log"
3. "any non-homomorphic section recovers d only at the random 1/p rate"

Top atlas hits for these phrasings: LEAD-EXO-miller-pairing-cocycle, LEAD-TRF-miller-cocycle-nonhom-transfer and
LEAD-EXO-dl-character-sum-pseudorandom.

### C3 (prime field, B1). Valuation-triviality lemma: a p-adic tropical decoder for a Semaev system has one source-bearing branch, and it is the residue solve

**Bottleneck.** B1, the non-enumerative oracle. IDEA-20260814-c3af09 (status: proposed; coverage.tsv maps it to
LEAD-ICP-coppersmith-smallroot-semaev) proposes "tropical initial-form cancellations" to prune the Semaev solve.
Its own pre-registered metric is:

> "median visited-branch ratio versus the branch-order-erased decoder ... At most 0.70 on each of three increasing
> sizes and at least two arities".

**External ingredient.** The fundamental theorem of tropical geometry (Kapranov; Einsiedler-Kapranov-Lind 2006;
Maclagan-Sturmfels, *Introduction to Tropical Geometry*, 2015). **Recalled.** Valuations of roots lie on trop(f),
and roots of valuation w reduce to roots of in_w(f).

**Lemma (derivation).** Let f ∈ F_p[x_1..x_m] be a Semaev decomposition polynomial with support A_0. Let f~ be any
Z_p-lift, with p-multiples added to coefficients on or off A_0.
1. Every coefficient on A_0 is a unit, so v = 0. Off A_0, v ≥ 1.
2. A source tuple with all x_i ≢ 0 (mod p) lifts to valuation vector w = 0, whatever the lift rule (integer
   representative, Teichmüller, or other).
3. At w = 0, trop(f~)(0) = 0, attained exactly on A_0. So in_0(f~) = f mod p.
4. Hence the only branch that holds sources with unit coordinates is "solve f mod p over F_p, then Hensel-lift".
   That is the proposal's own baseline embedding ("all valuation branches tied").
5. Branches with w ≠ 0 are faces of the Newton polytope (for unit-coefficient lifts) or lift artifacts. Their roots
   have non-unit coordinates, i.e. x_i = 0 (one point pair) or infinity.
6. **Corollary.** The ≤ 0.70 metric can be met in *branch-count* units: one visited branch out of K. It is
   vacuous in *work* units, because the visited branch is the whole residue system. So c3af09's interface reduces
   exactly to the prime-field Groebner/residue solve, which is B2 (KR-IC-5931ee, closed_known).

**Produced toy check** (`tropical_r2.py` -> `tropical_r2.out`).
- **Setup:** p = 211, small-x base.
  - S_3 (m = 2): base of 20, 60 targets, 59 exhaustive sources.
  - S_4 (m = 3): base of 8, 12 targets, 10 sources.
  - Lift ensemble: 10 lifts per target, each adding random p-multiples on A_0 and on 5 off-support monomials.
- **Results.**
  - Sources with non-zero valuation: **0 of 69**.
  - in_0(lift) equal to the residue polynomial: **600/600** (S_3) and **120/120** (S_4).
  - Newton polytopes: a square for S_3 (4 vertices, 4 edges) and a cube for S_4 (8 vertices, 6 facets).

**Pair and class.** The representation is a Z_p-lift of coordinates and system (R1). The operation set is initial
forms, substitution and Hensel refinement. The class is **coordinate-dependent**, and the lemma shows the
dependence is constant on the factor-base locus.

**SO codes touched.**
- **SO-PADIC** (quoted in section 2). The decoder lifts the *polynomial system*, not points, so it escapes the
  premises "section" and "lifts of E". The lemma closes it from the valuation side.
- **SO-ALGFB** (LEAD-ICP-algebraic-membership-factor-base):
  > "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has
  > description degree >= B/3 and membership polynomial prod(x - v) of degree B ...; mean per-target yield is
  > binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation ...). Scope: prime-order E/F_p, any
  > base of size B."

  The decoder is target-conditioned, so it escapes the premise "target-independent". That does not save it, since
  the conditioned branch is the full system.
- **SO-TABLE** (LEAD-ICP-generic-table-decomposition):
  > "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory
  > trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup) ... Scope: any generic
  > (enumeration/table) decomposition over F_p."

  The decoder is algebraic, not enumerative, so it escapes the premise "enumerates or table-looks-up". It falls
  back into B2 instead.

**First step** (about 1 h of review; the toy check is already run). Dispositions:
- **Lemma survives review →** c3af09 is falsified on its own interface. The p-adic Newton-polygon sub-family is
  **closed_obstructed (kind: proof)**. It should be filed under SO-PADIC / LEAD-EXO-padic-jet-canonical-lift
  rather than the Coppersmith lead: the atlas match puts it nearest LEAD-EXO-padic-jet-canonical-lift and the digit
  lead, not the Coppersmith lead it is mapped to.
- **A counterexample →** a lift whose w = 0 initial form differs from the residue, or a source with non-zero
  valuation. Then the lemma is wrong, and c3af09 stays proposed with **open_next_step**.

**Tier and gain.** Tier X. **Predicted gain: 0.**
- H3 (prediction, for the optional c3af09 panel): measured in residue-solve work, the visited-branch work ratio is
  ≥ 1 - O(face-solve share), i.e. ≥ 0.95 at m ∈ {3, 4}. In branch count it is 1/K, with K = number of cones of
  the tropical hypersurface of a unit-coefficient lift. That is one per face of dimension ≥ 1 of the Newton
  polytope, the apex included: K = 4 + 1 = 5 for the square (S_3) and 12 + 6 + 1 = 19 for the cube (S_4).

**Costs.** Implementation: 1 h (done). Compute: seconds. Self-kill risk: very low. Its value is modest: it
closes one proposal and one sub-family, and corrects a mis-specified metric.

**Match phrasings.**
1. "p-adic tropical initial-form decoder for Semaev systems collapses to the w=0 cell whose initial form is the
   residue system"
2. "lifting the decomposition polynomial to the p-adics and using Newton polygons gives no pruning"
3. "valuation profile collapses to the fibre indicator; computable Teichmuller-style contrast reads as chance"

Atlas hits: LEAD-ICP-digit-presentation-solving-degree and LEAD-EXO-padic-jet-canonical-lift (the latter for
phrasing 3).

### C4 (prime field, B1) [MERGE into scout-lattice-smallroot C1]. Unconditional strong-Groebner form of the corner ceiling: no short vector exists at all

**Status.** The lattice scout's corner lemma (sibling, internal) proves that the Howgrave-Graham *determinant
criterion* fails whenever D·vol ≥ 1, for every shift set and every GAP rank. My statement is complementary.
- It proves that **no** polynomial g ∈ (p, f)^t satisfies ||g(Xx)||_∞ < p^t. Its conclusion is stronger: it covers
  lattices whose short vectors beat det^{1/dim}, and any search method over the ideal.
- Its region is smaller: rank-1 boxes, and GAP rank r ≤ 2^{m-1}.
- It does not count toward my two prime-field candidates.

**Bottleneck.** B1. The lead is LEAD-ICP-coppersmith-smallroot-semaev (open_next_step).
- Its atlas best_measured, and `analysis/smallroot-reach/CLOSURE.md` (which I read this session), give margin
  -0.0481 at (m,w) = (4,2): JM extended reach 0.8408 against demand 8/9.
- The round-1 file cites a corrected margin of -0.6086 from `CORRECTION.md` (CORR-20261024-b2a799). That file is
  not in `analysis/smallroot-reach/` (only CLOSURE.md is). I did not verify that number and do not use it.

**External ingredients.** All **recalled**:
- strong Groebner bases over Z (Adams-Loustaunau, *An Introduction to Groebner Bases*, 1994, ch. 4);
- Howgrave-Graham, "Finding small roots of univariate modular equations revisited", 1997.

**Lemma (derivation).**
- **Setup.** Suppose a monomial a_0 of f has a unit coefficient and is LM(f) in some monomial order <. Let the
  box be X_i = p^{β_i}.
- **Step 1.** {p^{t-k} f^k : 0 ≤ k ≤ t} is a strong Groebner basis of (p, f)^t over Z:
  - S-polynomials are multiples of p^{t-k}f^k, so they reduce to 0;
  - G-polynomials are basis elements.
- **Step 2.** Hence every g ∈ (p,f)^t with LM(g) = x^a has lc(g) ∈ p^{t-k(a)}Z, where
  k(a) = max{k ≤ t : a - k·a_0 ≥ 0}.
- **Step 3.** If β·a_0 ≥ 1, then ||g(Xx)|| ≥ |lc(g)| X^a ≥ p^{t-k(a)+k(a)β·a_0} ≥ p^t.
- **Conclusion.** No useful polynomial exists, at any t, with any shifts or any lattice dimension.
- **For S_{m+1} (x_R known):**
  - The corner (x_1⋯x_m)^{2^{m-1}} has coefficient 1 and is the unique top-degree monomial. I checked this for
    m = 2, 3 myself; the sibling checked m = 4.
  - **Rank-1 boxes** (window, AP, digits) are closed when Σβ ≥ 2^{1-m}. The IC demand is Σβ ≥ 1.
  - **Rank-r GAP bases** x_i = x_0 + Σ_j d_j t_{ij}: the maximal-weight corner term has weight
    2^{m-1}·Σ_i max_j β_{ij}. So the unconditional version closes r ≤ 2^{m-1} only. The sibling's determinant
    lemma covers every r for the HG criterion.

**Produced checks** (`tropical_r2.py` -> `tropical_r2.out`).
- Corner coefficient = 1 and unique top monomial: S_3 (9 terms, total degree 4) and S_4 with x_R fixed (125 terms,
  total degree 12), 3 random (a, b, x_R) each, mod 10007.
- **The strong-Groebner description, verified on the actual S_3.** I took the echelon form over Z_(p), in a graded
  order, of all generators p^{t-k} f^k x^b in a box. The pivot valuation at every monomial equals t - k(a):
  **36/36** (t = 2, box 5) and **49/49** (t = 3, box 6), at p = 101.

**Pair and class.** The representation is the integer representative of x(P) (R1), with an archimedean box. The
operation set is shifts by monomials and by (p, f)^t. The class is **coordinate-dependent**.

**SO codes touched.**
- **SO-TABLE** (quoted in C3): the lattice escapes the premise "enumerates or table-looks-up".
- **SO-ALGFB** (quoted in C3): interval membership is an archimedean inequality, which escapes the premise
  "algebraic locus" (this is KN-OPEN-020's lattice-describable cell).
- **SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound):
  > "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a
  > prime-order-r group (KR-RHO-13bf67). ... Scope: all generic algorithms, any field, any r."

  The lattice escapes the premise "generic".
- The lemma closes the escape for single-equation ideal lattices.

**First step.** Merge with the lattice scout's C1. Run cuso (Ryan 2025, recalled) on S_3, t ≤ 4.
- **Certified reach ≤ 1/2 →** consistent with the lemma. The single-equation cells are **closed_obstructed (theorem)**.
- **Certified reach > 1/2 →** the lemma is wrong. Record it as a correction.
- **Joint multi-equation lattices, and GAP rank > 2^{m-1} in the unconditional form →** these stay
  **open_next_step**. best_measured: margin -0.0481 at (4,2) (CLOSURE.md).

**Tier and gain.** Tier X. **Predicted gain: 0.**
- H4 (prediction): cuso's certified S_3 reach lies in [0.28, 0.50] in Σβ units. The lower end is the sibling's
  exact-probe value; the upper end is the ceiling.

**Costs.** Implementation: hours (cuso). Compute: hours. Self-kill risk: it is a duplicate by design (merge).

**Match phrasings.**
1. "strong Groebner basis of (p,f)^t: no lattice polynomial is short once the corner monomial of the summation
   polynomial exceeds p on the box"
2. "no Coppersmith lattice built from the modulus and the summation polynomial can find small decompositions"
3. "small-root Coppersmith Jochemsz-May decomposition with lattice-describable window AP GAP factor bases reach
   below demand"

Atlas: LEAD-ICP-coppersmith-smallroot-semaev is the top hit for phrasings 2 and 3.

### C5 (Koblitz, B5). Census instrument: abelian varieties over F_2 with 131 | #A, and an explicit genus-6 Jacobian with J(F_2) ≅ Z/131

**Bottleneck.** B5. The lead is LEAD-ICB-nonlinear-frob-stable-bases (open_next_step). Its next step includes:

> "finish the dimension-5/6 Weil-polynomial census over F_2 for 131 | #A (H-FROB-ff99bf hit an impediment at dims
> 5-6; H-BINSTD-944a66 has preliminary support)"

Its discriminator includes:

> "A census with no dimension-5/6 abelian variety having 131 | #A closes the Couveignes-Lercier route at g <= 6."

EV-BINSTD-2d41c3, read in this session, records g = 6 as "failed_infrastructure (IMP-H1 ...)". It also says it
"Does NOT upgrade a_r>=0 to 'is a Jacobian'".

**External ingredients.**
- Dupuy, Kedlaya, Roe and Vincent, "Isogeny classes of abelian varieties over finite fields in the LMFDB",
  arXiv:2003.05380. **Retrieved**: PDF text extracted. Two statements matter:
  - Completeness: "For small dimension g and prime power q = p^r, the database contains searchable lists of
    complete sets of isogeny classes of abelian varieties of dimension g over F_q".
  - The caveat: "the LMFDB does not currently contain complete information about Jacobians of curves of genus at
    least 4". So the has_jacobian counts below are lower bounds.
- Kedlaya, root-unitary search, 2008 (recalled); Honda-Tate (recalled); Couveignes-Lercier, "Elliptic periods for
  finite fields", FFA 15 (2009) (recalled).

**Produced results.**
1. **LMFDB `av_fq_isog`, q = 2** (my SQL; `lmfdb_census_r2.json`). Classes with 131 | #A(F_2), by g = 1..6:
   **0, 0, 0, 0, 24, 617** (class totals 5, 35, 215, 1645, 14325, 164937).

   | g | classes with 131 \| #A | #A = 131 | simple | contain a Jacobian (lower bound) | hyperelliptic |
   |--:|--:|--:|--:|--:|--:|
   | 5 | 24 | 21 | 24 | 11 | 0 |
   | 6 | 617 | 375 | 497 | 173 | 8 |

   - The g = 5 list matches EV-BINSTD-2d41c3's own 24 hits.
   - **I found no g = 6 filtered count anywhere in the ledger.** I grepped EV-BINSTD-2d41c3, H-BINSTD-944a66,
     H-BINSTD-6feaa2 and `analysis/couveignes-lercier-131/census.json` for "617". Those records carry only the
     unfiltered LMFDB totals 1645/14325/164937, used as a completeness control. EV-BINSTD-2d41c3 records g = 6 as
     failed_infrastructure.
2. **An explicit Jacobian** (`koblitz_g6_r2.py` -> `koblitz_g6_r2.out`). The curve is
   C: y^2 + (x^7+x+1) y = x^6+x^3+x^2 over F_2 (LMFDB class 6.2.b_b_ab_b_d_l).
   - Brute-force counts #C(F_{2^k}) for k = 1..12 are 4, 6, 4, 26, 44, 102, 123, 258, 490, 1066, 2116, 4154. The
     model has 2 points at infinity, since deg h = g+1.
   - L(T) rebuilt from k ≤ 6 is [1,1,1,-1,1,3,11,6,4,-8,16,32,64]. It equals the LMFDB polynomial and **predicts
     k = 7..12 exactly**.
   - All |α| = sqrt(2). L is irreducible over Q. The middle coefficient is odd, so the curve is ordinary.
   - h is irreducible, gcd(h, f'^2 + h'^2 f) = 1 (smooth affine), and Y^2 + Y has distinct roots at infinity.
   - **#J(F_2) = L(1) = 131**, so J(F_2) ≅ Z/131. That upgrades one g = 6 class to "is a Jacobian".
3. **Minimal-g table for toy ladders** (LMFDB, g ≤ 6): the least g with n | #A(F_2) for prime n ≤ 293.
   - g = 2 at n = 11, 13, 19; g = 3 at 17, 23, 29, 31, 37, 41, 71.
   - g = 5 at 107, 127, 131, 151-199 (including 163, the K-163 degree), and most n > 220.
   - The full table is in `lmfdb_census_r2.json`.

**Mechanism (derivation, the degree half not built).**
- Let T generate J(F_2). The Lang fibre {R : Frob(R) - R = T} is a Z/131-torsor. Its points satisfy
  Frob^i R = R + iT, so they are defined over F_{2^131}.
- Frobenius acts on the fibre as translation by T. Low-degree functions of the Mumford coordinates along the
  fibre give **non-linear Frobenius-stable subsets of F_{2^131}**: an abelian-period model in the
  Couveignes-Lercier sense.

**Pair and class.** The representation is torsor coordinates on a genus-6 Jacobian over F_2 (R3). The operation set
is Frobenius, acting as translation by T. The class is **partial-action**.

**SO codes touched.**
- **SO-FROB** (LEAD-ICB-frobenius-orbit-factor-base):
  > "For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable
  > subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on
  > relations (n^2 on LA) and never more ... At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions
  > are empty ... Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. ...
  > Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."

  The base is non-linear, so it escapes the premise "V is sigma-stable". The cap "exactly n ... never more" still
  applies by the same orbit argument.
- **SO-TABLE (binary)** (LEAD-ICB-generic-table-oracle):
  > "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice
  > ... Scope: all binary and Koblitz curves, one target, setup charged."

  Decomposition must be algebraic in torsor coordinates, which escapes the premise "group operations and
  membership tests".
- **SO-QSP** (LEAD-ICB-quasi-subfield-polynomials):
  > "Euler-Petit Theorem 1: every linearized QSP has beta >= 3/4 ..." (no Scope clause in the YAML)

  Torsor-period sets are not linearised, which escapes the premise "linearized".

**First discriminating step.** Use a toy rung with explicit LMFDB curves: n = 11 or 13 at g = 2, or n = 17 at
g = 3. Build the torsor base. Compare per-attempt cost at matched |F| against a random subspace and a size-matched
null, in D ≤ 5 closure work and WDSat conflicts (H-CERTBIN protocol). Dispositions:
- **The census clause.** EV-BINSTD-2d41c3 had already found the 24 g = 5 hits (outcome B, 2026-10-01). From that
  point on, "closes the Couveignes-Lercier route at g <= 6" could not fire. I did not decide that clause.
  - What this candidate adds is the **g = 6 enumeration**: 617 classes, previously blocked by IMP-H1.
  - It also adds **one class upgraded to an explicit Jacobian** with J(F_2) ≅ Z/131, which EV-BINSTD-2d41c3 had
    left open ("Does NOT upgrade ... to 'is a Jacobian'").
  - Together these let the toy-rung and n = 131 steps start from a concrete J.
- **Per-attempt cost within [0.5, 2] of the subspace arm →** **open_next_step**: price n = 131 on the J above.
  best_measured: the ratio.
- **Cost above 2× →** **closed_obstructed (measured)**, reason: membership cost.
- **No bounded-degree membership in torsor coordinates →** **closed_obstructed (cost_model)**.

**Tier and gain.** Tier I. **Predicted gain in the matched gap: 0.**
- H5 (prediction): the SO-FROB orbit cap holds for any Frobenius-stable base. So the most it buys is
  log2(131) = 7.03 bits on relations, matched by rho's sqrt(2n).
- H6 (prediction): per-attempt decomposition probability at matched |F| equals the birthday value, as for every
  Frobenius-stable base measured at n = 11..23. So the per-attempt cost ratio is ≥ 1.

**Costs.**
- Implementation: 2-5 days (Cantor arithmetic over F_{2^n}, torsor construction, base builder).
- Compute: minutes at toy size.
- Self-kill risk: high, but the close it gives is cheap and decisive.

**Match phrasings.**
1. "abelian variety over F_2 with a rational point of order 131: genus-6 hyperelliptic Jacobian with exactly 131
   points for Couveignes-Lercier periods"
2. "a small curve over F_2 whose Jacobian has 131 points gives a Frobenius-stable model of the 131-bit field"
3. "Frobenius-stable factor base gain is exactly n on relations and never more; stable subspaces empty at prime n"

Atlas hits: LEAD-ICB-nonlinear-frob-stable-bases (all three), LEAD-ICB-ecc2k130-jacobian-carrier and
LEAD-ICB-frobenius-orbit-factor-base.

## 4. Killed candidates, with reasons

| # | idea | why killed |
|:--|:--|:--|
| K1 | Berkovich/tropical skeleton of E over Q_p as a decomposition aid | Good reduction for every lift: the skeleton is a point (BPR, recalled). Tate-curve structure appears only on degenerations, which is SO-XEDNI territory (alpha = 3). |
| K2 | Second Witt coordinate of the elliptic Teichmüller lift as an implicit-membership factor base | Torsion lifts on any lift E'/Z_p in O(log N) (P~ = P' - N^{-1}[N]P'), so membership is cheap. But torsion lifts are homomorphic, so a mod-p^2 decomposition is implied by the mod-p one: the second-digit constraint is linear in the digits (tangent space) and adds nothing. The digit is a degree-about-p function of x, so the algebraic system has degree about p. SO-PADIC and SO-TABLE apply. |
| K3 | Serre-Tate deformation over Z/p^2 carrying k | Ext^1(Z/N, F_p) = 0: the extension splits canonically (Wall P). |
| K4 | Smart's attack on the p-part of E(F_{p^k}) | Sylow subgroups are coprime, with no map from the N-part (SO-TORS). |
| K5 | Canonical lift of Koblitz curves (CM by Z[τ] over Z_2) | r is odd, so the torsion lifts with zero formal defect. SO-PADIC and SO-ENDO. |
| K6 | Kedlaya / Lauder-Wan / Harvey point counting as a decomposition decision oracle | Over F_p the cost is poly(p) or about p^{1/2}. It decides existence, not the tuple. Over descended F_2 systems it is exponential in the variable count. |
| K7 | Harvey average-polynomial-time remainder trees for B3 batching | Needs many moduli. Prime IC has one modulus, and the Montgomery trick already shares inversions. B3 cannot cross the SO-TABLE exponent wall. |
| K8 | Gross-Koblitz / Stickelberger biases of character-constant bases | Named in SO-ALGFB's forecloses; conservation fixes the mean yield. |
| K9 | Weil/Deligne/Katz bounds on decomposition counts of interval bases (to close coincidence-harvest escapes) | Main term B^2/p is about 1 at B about p^{1/2}; the error is about sqrt(p) log^2 p. The bound is vacuous in the IC regime (derivation). |
| K10 | Corvaja-Zannier / Garcia-Voloch bounds on points of C_R with both coordinates in a multiplicative subgroup (for B2's subgroup base, beta_work 0.647) | These are upper bounds, about \|G\|^{2/3}, above the expected yield \|G\|^2/p for \|G\| < p^{3/4}. They do not bind and give no algorithm (recalled). |
| K11 | BKK / mixed-volume census at special j | Newton polytopes are p-independent integers, so this is constant tier. It is already in the ledger (IDEA-20260805-1f4a11, H-SEMAEV-002, IDEA-20260811-97e244). |
| K12 | p-adic (Denef-Vercauteren/Tuitman) carrier search for LEAD-ICB-ecc2k130-jacobian-carrier | Derivation: a genus-(n-1) carrier must satisfy #C(F_{2^k}) = #E^twist(F_{2^k}) for all k < n, because A's Frobenius traces are -t_k(E) for n ∤ k. That is a curve with elliptic-curve point counts at 130 levels. Heuristic expected count < 1 at n = 11 (prediction, about 2^{-30} among hyperelliptic genus-10 curves). Symmetric Z/n-cover carriers are GHS in disguise (magic-number bound). The toy rungs n = 11, 13 are predicted empty unless they show the Weil-restriction structure seen at n = 7. |
| K13 | Tate-curve (nodal) deformation over F_p((t)) specialised at t = 1 | Specialisation is not continuous for the t-adic topology. |
| K14 | Function-field (F_2[z]) Coppersmith for binary decomposition | Covered by the lattice scout's C3 (function-field corner lemma). Not duplicated here. |
| K15 | (out of field, B6) closing LEAD-RHO-non-automorphism-equivalence by an Ω(log h) canonicaliser bound | **The lead's discriminator is mis-specified.** Its class gain is sqrt(h), so an Ω(log h) per-step cost leaves a net gain of about sqrt(h)/log h > 1. A closure needs Ω(sqrt h). By-product (derivation): any rational H-invariant f on G has deg f ≥ N/(2μ_H), with μ_H = min over λ ∈ H\{±1} of min{a^2+b^2 : a ≡ λb mod N}. (Use f∘[a] - f∘[b] ≢ 0, since equal degrees would force λ = ±1, together with N ≤ 2d(a^2+b^2).) Heuristically μ_H ≈ N/(πh), so d ≳ πh/2. Strassen's degree bound then gives ≥ log2 h multiplications. This pre-decides the lead's "search for a non-constant H-invariant at h ~ N^{1/3}" for *algebraic* invariants of degree < N/(2μ_H). It cannot close the lead, and only bit-level invariants remain to search. |
| K16 | Zeta-defect Z (IDEA-20261016-09fd08) as a transfer | Not decided by C2. Z is defined by a sum over N points, so the Weil machinery has no low-degree handle. The carry reduction (C2) is derivation only. |

## 5. Fields searched with no candidate

- **B2 (Semaev solving degree).**
  - Tropical/BKK root counts are p-independent (K11).
  - Sparse/fewnomial point bounds for subgroup bases do not bind (K10).
  - The Groebner degree ≥ deg(membership polynomial) bound is the known KR-IC-5931ee content.
- **B3 (prime IC constants).** Remainder-tree and average-polynomial-time methods need many moduli (K7). p-adic
  arithmetic has no constant to offer the F_p pipeline.
- **B4 (SAT/XOR, writability).** The 2-adic/Lucas digit-sum bound on descended degree is the known product-space
  fact (KR-IC-73db3f, KR-IC-f5c584). There is no tropical lever on conflict counts.
- **B6 (generic/rho).** p-adic/canonical-lift H-invariants reduce to rational invariants, which K15 bounds. Step
  primitives are not in this field.
- **Berkovich/tropical structure of E/Q_p**: K1.
- **Formal groups, canonical lifts and Witt digits**: K2-K5.
- **Point counting as an oracle**: K6, K12.
- **Gauss/Jacobi sums and Gross-Koblitz**: K8.
- **Equidistribution of decomposition counts**: K9.

## 6. Citations

| source | used for | provenance |
|:--|:--|:--|
| Lauter-Stange, SAC 2008, LNCS 5381 (2009) 309-327, arXiv:0803.0728 v2 | C1 (load-bearing): Thms 1, 6, 7, 8, 10, eqs (3), (4), (6), Problem 2 | retrieved (arXiv page and PDF text, this session) |
| Ahmadi-Shparlinski, "Exponential sums over points of elliptic curves", arXiv:1302.4210, Lemma 1, restating Kohel-Shparlinski ANTS 2000 Cor. 1 | C2 (form of the twisted-sum bound) | retrieved (PDF text, this session) |
| Kohel-Shparlinski, ANTS-IV, LNCS 1838 (2000) 395-404 | C2 | retrieved (bibliographic, via search plus the citation above); full text not opened (host refused the connection) |
| Weil bound; Grothendieck-Ogg-Shafarevich; Deligne, Weil II | C2 (the constant 2) | recalled; the constant is my derivation, and the measured max is 1.99995 |
| Dupuy-Kedlaya-Roe-Vincent, arXiv:2003.05380 | C5 (completeness, Jacobian caveat) | retrieved (PDF text, this session) |
| LMFDB `av_fq_isog` | C5 | queried by me this session |
| Kedlaya 2008 (root-unitary search); Honda-Tate; Couveignes-Lercier FFA 2009 | C5 | recalled |
| Einsiedler-Kapranov-Lind 2006; Maclagan-Sturmfels 2015 | C3 | recalled |
| Baker-Payne-Rabinoff, Algebraic Geometry 3 (2016) | Wall T, K1 | recalled |
| Adams-Loustaunau 1994; Howgrave-Graham 1997; Ryan (cuso), EUROCRYPT 2025 | C4 | recalled |
| Strassen degree bound | K15 | recalled |

## 7. Artifacts (all produced this session)

Directory: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/padic-tropical-r2/`

| file | content |
|:--|:--|
| `miller_eds_r2.py` -> `miller_eds_r2.out`, `miller_eds_r2.json` | C1 identity, K2, partial-sum spectrum against nulls, N \| p-1 controls |
| `ls_eq4_check_r2.py` -> `ls_eq4_check_r2.out` | LS eq. (4) exponent check (n^2 holds; the extracted n^2-1 does not) |
| `weil_bound_r2.py` -> `weil_job0..7.out` | C2 full sums, K1 verification and refill, NAF cross-check, controls |
| `smart_ratio_r2.py` -> `smart_job0..5.out` | C2 Smart-ratio arm (ratio test and strong linear form), same six curves as `miller_eds_r2` |
| `tropical_r2.py` -> `tropical_r2.out` | C3 lift ensemble; C4 corner coefficients and pivot valuations |
| `koblitz_g6_r2.py` -> `koblitz_g6_r2.out` | C5 genus-6 recount to F_{2^12} |
| `lmfdb_census_r2.json` | C5 LMFDB query results (transcribed from tool output) |
| `match-log-r2.txt` | all 15 phrasings through `lead_atlas.py --match` and `build_frontier_map.py --match` |
| `dl_ls_r2/`, `dl_as_r2/`, `dl_dkrv_r2/` | fetched PDFs and their extracted text, read only as data |

## 8. What I reproduced from the round-1 file, and what I did not

| round-1 claim | status in this session |
|:--|:--|
| U·φ(R)/φ(R-P) constant (6 curves) | **reproduced** with independent code on 6 different curve draws, plus 3 special-form primes |
| K2 exact, C = φ(P)^{-2N} | **reproduced**: D = φ(P)^{-2} on 6/6 curves |
| LS eq. (4) as φ(P)^{n^2-1}W(n) | **contradicted** as stated: n^2 holds (section 3, C1) |
| sibling `miller_u_spectrum_v2.out` (not round-1's own either) | not used; replaced by C2's theorem, full sums and the Smart-ratio arm |
| corrected Coppersmith margin -0.6086 (CORR-20261024-b2a799) | not verified: no CORRECTION.md in `analysis/smallroot-reach/`; I use CLOSURE.md's -0.0481 |
| valuation lemma (round-1 C2) | re-derived; **toy check produced** here (it was not run in round 1) |
| per-block LP ceilings 0.50/0.75/0.25/0.333 | not rerun; superseded by the general corner-weight statement in C4 |
| LMFDB census 24 / 617, explicit genus-6 curve | **reproduced** (my SQL; recount extended from k ≤ 6 to k ≤ 12) |
| genus-5 canonical curve recount | not reproduced; not used |
| min-dim table | **reproduced** from LMFDB SQL |
