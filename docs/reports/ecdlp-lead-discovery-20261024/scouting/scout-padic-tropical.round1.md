# Scout dossier: p-adic and tropical geometry (final lead-discovery round)

Scout field: Berkovich/tropical structure of E over Q_p, formal groups and canonical lifts, Kedlaya/Harvey-style
p-adic cohomology and point counts, p-adic valuations of Semaev systems, tropical root counting, Newton-polygon
methods for decomposition. Written 2026-10-24. Everything in this file is a proposal or a toy computation by one
agent. Nothing here changes any record. Repositories were not edited. All artifacts are under
`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/padic-tropical/`.

Labels used below: **produced** means I computed it in this session, and the script and output are listed.
**prediction** means an expected value that has not been measured. Citation provenance is `retrieved` (I read the
source or its abstract page with WebSearch/WebFetch in this session) or `recalled` (from memory, not checked).

## 0. Verdict on the field, in one paragraph

Two short arguments close almost the whole field for prime-field ECDLP, so it cannot produce an exponent-moving
prime-field candidate.

- **Wall P (coprimality).** Every p-adic object attached to E/F_p lives in a pro-p group or a Z_p-module.
  Examples: the formal group, Witt and Teichmuller digits, Serre-Tate deformations, and the p-part of E(F_{p^k}).
  The subgroup G has prime order N != p, so every homomorphism from G into such an object is trivial. Any
  non-homomorphic read-out is a hash. This is SO-PADIC.
- **Wall T (trivial valuation).** F_p has only the trivial valuation. Every lift of E/F_p to Q_p has good
  reduction, so its Berkovich skeleton is a point (Baker-Payne-Rabinoff; recalled). A lifted Semaev system has unit
  coefficients wherever its residue coefficients are nonzero. Section 3, C2, proves that its tropical branch
  structure on the factor-base locus is a single cell.

What the field can still supply:

1. Cheap proofs that close open leads. C1 does this for B7, using an EDS normalisation from the Lauter-Stange
   literature that I found while searching p-adic sigma functions. C2 does it for a proposed p-adic tropical
   decoder. C3 is a second, independent p-adic proof of the small-root ceiling that the lattice scout also derives.
2. One instrument result on the Koblitz side (C4). A point-count census built on Kedlaya's root-unitary search,
   queried through the LMFDB and independently recounted, gives an explicit hyperelliptic Jacobian over F_2 with
   exactly 131 rational points.

I make no prime-field claim of an exponent gain, and none is predicted.

## 1. Inputs read

- ATLAS.md: all eight families and the open-steps table, read fully.
- KRMAP.md: all generic-rho and index-calculus rows.
- object-frame-ideation.md, sections 1-3 (and 4-6).
- idea-generator.md: "Search heuristics" and "Obstructions as generative material".
- target-result-profile.md.
- LEADERBOARD Table B and the phase shares; the FRONTIER outline.
- Lead YAMLs, read in full for every SO code quoted below.
- Ledger records read individually by path:
  - IDEA-20260814-c3af09, IDEA-20261017-e3a6f1 (grep).
  - H-FROB-ff99bf, H-BINSTD-944a66, EV-FROB-a85eaf, EV-BINSTD-2d41c3.
  - analysis/smallroot-reach/{CLOSURE,CORRECTION}.md and tools/smallroot_reach.py (header).
- Dedup: ledger index grep for tropical / Newton polygon / Berkovich / Kedlaya / Harvey / Dwork / Lauder /
  Gross-Koblitz / Stickelberger / Serre-Tate / BKK / mixed volume / Kronecker / Lauter / Stange.
- `lead_atlas.py --match` and `build_frontier_map.py --match` on every phrasing. The log is in
  `padic-tropical/match-log.txt`.
- The sibling scout file `scout-lattice-smallroot.md`. It already contains the "corner ceiling" (see C3).

## 2. Field walls, written out

**Wall P.** Let A be a pro-p group or a Z_p-module: the formal group E-hat(pZ_p), the kernel of E(Z/p^k) -> E(F_p),
W(F_p), or a Serre-Tate deformation space. G = <P> has order N with gcd(N, p) = 1, so Hom(G, A) = 0. Every
extension 0 -> A -> * -> G -> 0 splits uniquely, because Ext^1(Z/N, A) = 0. A homomorphic read-out of k from any
p-adic object is therefore zero. A non-homomorphic one (digits of a chosen lift) is a function of the encoding.
This is exactly SO-PADIC. The quoted obstruction.statement of LEAD-TRF-padic-canonical-section is:

> "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal
> logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any
> non-homomorphic section recovers d only at the random 1/p rate. ... Scope: non-anomalous prime-field curves, all
> lifts of E."

The same argument covers Koblitz curves, since r is odd and coprime to 2. It covers canonical lifts computed by
Satoh's algorithm as well, because those still give the torsion section.

**Wall T.** Let F_p be the residue field and lift a Semaev system S_{m+1}(x; x_R) to Z_p. A nonzero residue
coefficient is a unit in every lift. A zero residue coefficient has a lift-dependent valuation >= 1. A factor-base
x-coordinate is a unit in every lift unless x == 0 (mod p). Proof that this gives a single tropical cell: C2.

## 3. Candidates

### C1 (prime field, B7). The Miller primitive U is the Lauter-Stange perfectly periodic EDS ratio, so k-recovery from U is EDS Association

- **Bottleneck.** B7, non-homomorphic transfers when the pairing is trivial:
  - LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined).
  - LEAD-EXO-miller-pairing-cocycle (open_next_step). Its next step is: "Verify ... K2 (U(kP)=c*r_k*C^(k/N),
    r_k=psi_{k-1}/psi_k) exactly on toy prime-order curves with gcd(N,p-1)=1, then measure whether k can be
    recovered from U(kP) in fewer than sqrt(N) group operations once r_k is charged."
- **External ingredient.** Lauter and Stange, "The elliptic curve discrete logarithm problem and equivalent hard
  problems for elliptic divisibility sequences", SAC 2008, LNCS 5381 pp. 309-327, arXiv:0803.0728. Provenance:
  retrieved; full text read from arXiv. The parts used:
  - Problem 2 (EDS Association): determine W_{E,P}(k) from P and Q = [k]P.
  - Theorem 6, eqs (3)-(4): phi(P) = (W(q-1)/W(q-1+ord P))^{1/ord(P)^2}, and phi([n]P) = phi(P)^{n^2-1} W(n) is a
    perfectly periodic EDS equivalent to W.
  - Theorem 8: phi(Q) is computable from Q in O((log q)^3) without k.
  - Theorem 10 and eq (6): W(k+1)/W(k) = phi(P)^{2k+1} phi([k+1]P)/phi([k]P). k is then one F_q^* discrete log
    away, but only if the non-perfectly-periodic terms W(k) are known.
  - Remark 1: the coset problem when gcd(m, q-1) = 1.
  - Theorem 1: EDS Association, EDS Residue and width-3 EDS DL are each solvable in sub-exponential time iff ECDLP is.

  The program holds it as KN-LIT-247. No KR row exists, and neither Miller lead cites it.
- **Derivation.** Set r_k = W(k-1)/W(k), as in K2.
  1. By LS eq (4), r_k = [phi((k-1)P)/phi(kP)] * phi(P)^{2k-1}.
  2. U is a function of the point R = kP. Its quoted form c*r_k*C^{k/N} must therefore be invariant under
     k -> k+N, which forces C = phi(P)^{-2N}.
  3. Hence **U(R) = c' * phi(R-P)/phi(R)**. Every k-dependence in K2 cancels.
  4. U is the perfectly periodic EDS ratio, computable from R (Miller's loop, or LS Theorem 8), and it carries no
     information beyond R.
  5. The only route from U-type quantities to k is eq (6) or Theorem 10. That route needs the
     non-perfectly-periodic W(k), which is Problem 2.
  6. **The direction, stated exactly.**
     - Computing r_k (equivalently W(k), W(k+1)) from kP in time T gives ECDLP in time T plus one F_p^*
       discrete log, which costs L_p(1/3) (LS Theorem 10, when phi(P) generates F_p^*).
     - Conversely, given k, W(k) costs O(log k) (Shipsey's Theorem 7, as cited by LS).
     - So the K2 route is ECDLP restated plus a sub-exponential F_p^* DLP. LS Theorem 1 records this as a
       sub-exponential equivalence. It is a reduction, not an unconditional hardness proof.
     - Hence any "cheap closed form for r_k without k" would itself be a sub-exponential ECDLP algorithm.

  **The other two records bundled in LEAD-TRF-miller-cocycle-nonhom-transfer:**
  - IDEA-20261009-c8433d. Its own claim is that the generalized-Jacobian class "is trivial on l-parts with l not
    dividing p^k - 1, and costs a DLP in F_{p^k}^* otherwise". That is the Tate pairing, so with gcd(N, p-1) = 1 it
    is SO-PAIR/MOV and is decided.
  - IDEA-20261016-09fd08 (the zeta-defect Z). It is the additive twin of U. Its own K2 reads
    "Z(dP)=d*Z(P)+g_d(P), g_d=(2y_P/d)f_d'(x_P)/f_d(x_P)", with Z computable from the point by its K1.
    - Derivation (mine, not run): from (P, kP), knowing g_k(P) gives k*Z(P) = Z(kP) - g_k(P) in F_p. That gives k
      mod p, and so k for N ~ p up to O(1) candidates, whenever Z(P) != 0.
    - Conversely, k gives g_k in O(log k) via jets.
    - So computing the carry g_k from kP is polynomial-time equivalent to ECDLP. Z carries no extractable
      k-information beyond ECDLP itself.
    - This rests on 09fd08's K2, which that record marks unreviewed.
- **Produced verification.** Script `padic-tropical/miller_vs_lauterstange.py`; output
  `padic-tropical/miller_vs_lauterstange.out`.
  - Setup: six random prime-order curves with gcd(N, p-1) = 1 and p in {10007, 10009, 20011, 30011, 40009, 50021}.
    The Miller function f_{N,P} is normalised as in e3a6f1 and U = f^{N^{-1} mod (p-1)}. phi is computed from the
    division-polynomial EDS by LS (3)-(4).
  - Result: U(kP) * phi(kP)/phi((k-1)P) took **exactly one value per curve** over every evaluable k. That is
    10,142 / 9,792 / 20,010 / 30,210 / 40,312 / 49,682 values of k. Pole hits of the Miller chain were skipped.
- **Representation and operation pair; class.**
  - Representation: Q -> U(Q) in F_p^*, a function of the coordinates through a Miller function (R2/R3, a
    function-field object).
  - Operation set: translation by P, through the line-function cocycle.
  - Class: **coordinate-dependent**. U(R+P)/U(R) needs R itself. The identity shows U is a fixed function of the
    point and not of k.
- **SO codes touched, and the premise each candidate idea escaped before this closure.**
  - **SO-NET**, LEAD-EXO-elliptic-net-eds: "Somos identities hold for every k, so net relations encode the group law
    on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); ... the charged
    k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting". The Miller idea escaped the
    premise "net relations", because U is a one-point map into F_p^* and not a relation. C1 shows that the map is
    itself an EDS normalisation, so the net lead's vocabulary applies after all.
  - **SO-PAIR**, LEAD-TRF-second-torsion-direction: "Balasubramanian-Koblitz: for N || #E(F_p), N != p,
    E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1 ... Scope: ordinary and supersingular curves
    over F_p, prime N." U needs no second torsion direction, so it escaped that premise. Nothing is gained.
  - **SO-GEN**, LEAD-EXO-augmented-oracle-ggm: "Each named oracle is GGM-simulable ... Scope: oracles, not
    resources". U reads coordinates, so it escaped. The closure goes through LS Theorem 1, not through GGM.
- **First discriminating step, with outcomes mapped to dispositions.** A reviewed derivation note, plus a rerun of
  the toy script on one more curve family (j = 0 and j = 1728 with gcd(N, p-1) = 1). The dispositions follow what
  each lead pre-registered.
  - **LEAD-EXO-miller-pairing-cocycle.** Its discriminator says: "If K2 holds and r_k needs k, the primitive
    collapses into the closed elliptic-net lead and this lead closes as obstructed". K2 holds as an LS identity,
    verified 6/6 in toy runs, and r_k needs k (ECDLP restated, step 6). So the lead goes to **closed_obstructed
    (kind: proof, with LS 2008 as the literature anchor)**, collapsing into LEAD-EXO-elliptic-net-eds. It should
    cite KN-LIT-247 and gain a KR row.
  - **LEAD-TRF-miller-cocycle-nonhom-transfer.** Its pre-registered discriminator is equidistribution of log U. That
    measurement belongs to a sibling scout: `scout/miller_u_spectrum_v2.out` is not mine; it reads max|S| about
    2.01-2.02 sqrt(p) on theorem cells and a peak on the N | p-1 control. I do not claim it. C1 adds that the U
    component and the c8433d component are decided, and that the 09fd08 component is ECDLP restated (derivation).
    With the sibling's spectrum, the lead's components are decided → **closed_obstructed(proof)**. Without it →
    **open_next_step** with only the equidistribution check left. best_measured: the 6/6 toy identity.
  - The identity fails on some curve family → **open_next_step** for that family. best_measured: the 6/6 toy
    agreement above.
- **Tier: X. Predicted gain: 0.**
  - H1: the closure rests on a reduction, LS Theorem 10 plus Theorem 1: a cheap r_k would give ECDLP for the
    price of one F_p^* DLP. Only the identification U = c'*phi(R-P)/phi(R) is empirical, and it is verified on 6/6
    toy curves.
  - H2 (prediction): the residual "structure in k" question that H1 of e3a6f1 raises equals the character-sum
    whiteness of an EDS ratio, which is bounded at about 2 sqrt(p) by Weil-type estimates (recalled). Predicted
    correlation with characters of Z/N: at the 1/sqrt(p) noise level.
- **Costs.** Implementation 2 hours (done at toy size). Compute: minutes. Self-kill risk: low.
- **Match phrasings.**
  1. "Miller primitive U is the Lauter-Stange perfectly periodic EDS ratio phi(R-P)/phi(R)"
  2. "recovering the scalar from the Miller function value is as hard as computing the divisibility-sequence term"
  3. "Somos/EDS relations encode the group law on one k-fibre; EDS Association sub-exponentially equivalent to ECDLP"

### C2 (prime field, B1). Valuation-triviality lemma: every p-adic tropical or Newton-polygon decoder on an F_p Semaev system collapses to the unpruned baseline

- **Bottleneck.** B1 (a non-enumerative oracle).
  - The p-adic tropical decoder IDEA-20260814-c3af09 is mapped to LEAD-ICP-coppersmith-smallroot-semaev in
    coverage.tsv. It claims tropical initial-form branches prune the Semaev solve.
  - Scope: p-adic lifts only. The digit lead's "valuation-semigroup presentations" are monomial-valuation and
    Groebner-semigroup objects. C2 does not touch them.
- **External ingredient.** The fundamental theorem of tropical geometry and Kapranov's theorem: tropical cells and
  initial forms over a valued field (recalled). Also Baker-Payne-Rabinoff 2016: a good-reduction curve has a
  point-skeleton (recalled).
- **Lemma.** Let f in F_p[x_1..x_m] be any reduced Semaev decomposition polynomial. Let f~ in Z_p[x] be any lift
  and v the p-adic valuation.
  1. Let A_0 be the support of f. For a in A_0 the coefficient is a unit, so v(c~_a) = 0. Off A_0, v(c~_a) >= 1,
     and this value depends on the lift.
  2. Any F_p-point x of the factor-base locus with all x_i nonzero mod p lifts to a point of valuation vector
     w = 0.
  3. At w = 0, trop(f~)(0) = min_a v(c~_a) = 0, and in_0(f~) = sum over A_0 of c_a x^a = f. The initial form is
     the reduction itself.
  4. The branch that holds every unit-coordinate root is therefore exactly "solve f over F_p, then Hensel-lift".
     That is the proposal's own baseline embedding ("all valuation branches tied").
  5. A cell with w != 0 needs some coordinate of nonzero valuation. That means x_i == 0 (mod p), at most two
     factor-base points, or x_i = infinity, which is the point O.
  6. Any other variation comes from the lift-dependent valuations off A_0. The proposal's own lift-ensemble
     falsifier calls that an encoding artifact.
- **Representation and operation pair; class.** Representation: a Z_p-lift of the coordinates and of the system
  (R1). Operation set: initial forms, substitution and Hensel refinement. Class: **coordinate-dependent**. The lemma
  shows the coordinate-dependence is constant on the factor-base locus.
- **SO codes touched.**
  - **SO-PADIC**: statement quoted in section 2. Premise escaped: "section ... of reduction". The decoder lifts the
    polynomial system, not points. The lemma closes it from the valuation side.
  - LEAD-EXO-padic-jet-canonical-lift, same family: "... every additive order-l image is zero ... the computable
    Teichmuller-style contrast reads as chance ... IDEA-436 D1 valuation profile collapses to the +/- fibre
    indicator (KN-FIND-1ba0fe). Scope: ordinary prime-field curves, toy primes 10-14 bits".
  - **SO-ALGFB**, LEAD-ICP-algebraic-membership-factor-base: "A target-independent algebraic locus of degree d
    yields O(d) usable points ... Scope: prime-order E/F_p, any base of size B." The decoder escapes the premise
    "target-independent locus" because it works on the target fibre. That does not save it.
- **First discriminating step (zero compute, about 1 hour).** Review the lemma. Optionally run the e3a6f1 toy panel
  at 12-16 bits with the branch-order-erased arm only.
  - **Prediction:** median visited-branch ratio = 1 - O(2/B) (>= 0.99 at B >= 256). The coefficient of variation
    across lifts is 0 for lifts that keep A_0's coefficients fixed. The ratio moves only when lift noise is placed
    off A_0.
  - Lemma survives review → c3af09 is falsified on its own gates (ratio <= 0.70 is impossible) and the p-adic
    Newton-polygon sub-family is **closed_obstructed(proof)** under LEAD-ICP-coppersmith-smallroot-semaev /
    SO-PADIC.
  - A counterexample, meaning a lift with unit-coordinate roots outside w = 0 → the lemma is wrong and c3af09
    stays proposed.
- **Tier: X (closure). Predicted gain: 0.** H3: the lemma is a proof, so there is no heuristic. The predicted branch
  ratio of at least 0.99 is a prediction for the optional toy panel.
- **Costs.** Implementation 0 to 2 hours. Compute: seconds. Self-kill risk: very low. Value is modest, since it
  closes one proposal and one sub-family.
- **Match phrasings.**
  1. "p-adic tropical initial-form decoder is trivial on F_p Semaev systems"
  2. "Newton polygons over Q_p of a lifted decomposition polynomial carry no information beyond the mod-p system"
  3. "valuation profile collapses: every unit-coordinate root lies in the single cell w = 0 whose initial form is
     the reduction (lift-dependent valuations are encoding artifacts)"

### C3 (prime field, B1). [MERGE with scout-lattice-smallroot C1/C2] A p-adic strong-Grobner proof of the small-root ceiling, with per-block LP numbers

- **Status.** The sibling lattice scout independently derives the same leading-monomial ("corner") ceiling. It has
  a sharper, order-averaged bound, vol < 1/D. Read this candidate as an independent proof route and a cross-check,
  not as a separate lead.
- **Bottleneck.** B1. LEAD-ICP-coppersmith-smallroot-semaev, with the corrected margin −0.6086 at (4,2)
  (CORRECTION.md, CORR-20261024-b2a799). CORRECTION.md itself says: "Nothing here shows the optimal-shift question is
  formally closed: Jochemsz–May extended is one strategy."
- **External ingredients.**
  - Aono, Agrawal, Satoh, Watanabe, "On the optimality of lattices for the Coppersmith technique", ACISP 2012 / AAECC
    29 (2017) 169-195. Provenance: retrieved (abstract and summary). It proves the standard univariate lattice is
    optimal, and the Boneh-Durfee equation case.
  - Chinburg, Hemenway, Heninger, Scherr, "Cryptographic applications of capacity theory: on the optimality of
    Coppersmith's method for univariate polynomials", arXiv:1605.08065. Provenance: retrieved (abstract); the
    ASIACRYPT 2016 venue is recalled. It uses capacity theory of adelic subsets of curves (archimedean x p-adic) to
    rule out all Coppersmith-type auxiliary polynomials, of any degree, beyond N^{1/d}.
  - Ryan, "Solving Multivariate Coppersmith Problems with Known Moduli", EUROCRYPT 2025, LNCS 15606 pp. 355-384,
    ePrint 2024/1577, tool cuso. Provenance: retrieved. It gives provably optimal shift sets via Grobner bases.
- **Lemma (rigorous).** Let f be monic mod p^t in a monomial order <, after multiplying by lc^{-1} mod p^t.
  1. {p^{t-k} f^k : 0 <= k <= t} is a strong Grobner basis of (p,f)^t over Z.
     - The S-polynomial of p^{t-k}f^k and p^{t-j}f^j (j > k) is p^{t-k}f^k (x^{(j-k)a0} - f^{j-k}), which reduces to 0.
     - The G-polynomial is p^{t-j}f^j itself.
  2. So every g in (p,f)^t with in(g) = x^a has lc(g) in p^{t-k(a)}Z, where k(a) = max{k : a - k*a0 in N^n}.
  3. A Howgrave-Graham-useful g needs |lc(g)| X^a <= ||g(Xx)|| < p^t, hence w.a < k(a), where X_i = p^{w_i}.
  4. Pick < as the w-weight order. Then a0 is the max-weight monomial of f. If w.a0 >= 1, then w.a >= k w.a0 >= k(a)
     for all a, so **no useful polynomial exists in any (p,f)^t-lattice, at any t, with any shift set**.
  5. Ceiling: an ideal-based lattice can succeed only if every monomial of f is < p on the box.

  Calibration: it reproduces Coppersmith's 1/d exactly (univariate, tight; AASW). For Boneh-Durfee xy + Ax + 1 it
  gives delta < 1/2, which is the BD-conjectured bound (recalled), and no lattice is known beyond 0.292. For the full
  box it gives eps < 1/d >= JM-HG 2/(d(n+1)).
- **Produced numbers.** Script `padic-tropical/ceiling_lp.py`; output `ceiling_lp.out`. It solves the single-order LP
  max sum(beta) subject to a.beta < 1 over the true supports, at a random curve mod 1000003:

  | block | supports | single-order ceiling (eps units) | corrected JM-HG achieved |
  |:--|:--|:--|:--|
  | S_3, root block, 2 unknowns | 9 | 0.5000 | — |
  | S_3, inner block, 3 unknowns | 13 | 0.7500 | 0.2803 |
  | S_4, root / (3,0) | 125 | 0.2500 | — |
  | S_4, inner, 4 unknowns | 439 | 0.3333 | 0.1034 |

  Scope of the produced numbers: blocks with l <= 3 leaves (S_3 and S_4) only. The S_5 run (l = 4) was not
  computed; the run was terminated.
  - Within that scope, every IC demand is above the worst-block ceiling.
    - For trees whose root block is S_3 or S_4 and w >= 1: demand is 1 - (m-2)/(2(m-1)(w+1)) > 3/4, above the
      root-block ceilings 1/2 and 1/4.
    - For w = 0 with m = 2 or 3: demand is 1 and 3/4, against 1/2 and 1/4.
    - Inside the program's block-composition model, these cells are closed for every ideal-based shift strategy.
  - Cells with blocks of l >= 4 leaves (including w = 0 with m >= 4) are not covered by my numbers. They rest on the
    lattice scout's general order-averaged corner bound, vol < 1/D (`scout-lattice-smallroot.md`), which is theirs.
- **Scope gap, stated.**
  - The rigorous statement is per equation. For a joint multi-block ideal (p, f_1, ..., f_{w+1})^t the coprime-order
    version is vacuous at (4,2): the leading monomials are forced to x1^2x2^2, x3^2x4^2, u1^2u2^2.
  - So joint lattices remain open. That is cuso's job: compute the joint reach at t <= 4.
  - Non-lattice auxiliary polynomials need a multivariate CHHS capacity argument (Chinburg's capacity theory on
    varieties, recalled). That would be a real research extension.
- **Pair; class.** Representation: the integer lift of x in [0, p) (R1), with the archimedean box. Operation set:
  multiplication by shift monomials and by (p, f)^t. Class: **coordinate-dependent** (integer representatives).
- **SO codes touched.**
  - **SO-TABLE**, LEAD-ICP-generic-table-decomposition: "Any decomposition oracle that enumerates or table-looks-up
    factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N ... Scope: any generic
    (enumeration/table) decomposition over F_p." Premise escaped: "enumerates or table-looks-up". The lattice reads
    integer sizes.
  - **SO-ALGFB**: quoted above. Premise escaped: "algebraic locus". Interval membership is an archimedean inequality,
    which is KN-OPEN-020's lattice-describable cell.
  - **SO-GEN**, LEAD-RHO-generic-sqrt-lower-bound: "any generic algorithm needs Omega(sqrt r) group operations ...
    Scope: all generic algorithms, any field, any r." Premise escaped: "generic".
  - The lemma closes the escape inside ideal-based lattices.
- **First step and dispositions.**
  1. Merge with the lattice scout's C1/C2.
  2. Run cuso on (a) S_3 at t <= 4, which is calibration: cuso's certified reach must be <= 0.75, otherwise the
     lemma is wrong, and (b) the joint (4,2) ideal.
  - Joint reach < 8/9 with no upward trend in t → LEAD-ICP-coppersmith-smallroot-semaev **closed_obstructed(theorem
    for single blocks + measured joint, scope: ideal-based lattices)**.
  - Joint reach >= 8/9 → **open_next_step**: planted recovery H-PFDR-621852. best_measured: the cuso reach.
- **Tier: X. Predicted gain: 0.**
  - H4 (prediction): the joint (4,2) reach is <= the max per-block ceiling, 0.75. Composing blocks cannot beat its
    best block, because each extra equation brings its own forced corner of weight >= 1.
  - H5 (prediction): cuso's provably optimal S_3 reach lies in [0.28, 0.75].
- **Costs.** Implementation: hours (cuso install plus a script). Compute: hours. Self-kill risk: it is a duplicate,
  and that is by design.
- **Match phrasings.**
  1. "strong Groebner basis over Z of (p,f)^t: leading-coefficient ceiling for Coppersmith small roots"
  2. "no lattice built from the modulus and the summation polynomial can find roots once any monomial exceeds p on
     the box"
  3. "lattice-describable factor base: Jochemsz-May reach below demand for every shift strategy (strategy-independent
     closure, ideal-based lattices)"

### C4 (Koblitz, B5). Abelian periods for F_{2^131}: the census impediment is lifted and an explicit hyperelliptic Jacobian over F_2 with exactly 131 points exists

- **Bottleneck.** B5, LEAD-ICB-nonlinear-frob-stable-bases.
  - Its next step includes: "finish the dimension-5/6 Weil-polynomial census over F_2 for 131 | #A (H-FROB-ff99bf hit
    an impediment at dims 5-6; H-BINSTD-944a66 has preliminary support)".
  - It discriminates: "A census with no dimension-5/6 abelian variety having 131 | #A closes the Couveignes-Lercier
    route at g <= 6."
  - H-FROB-ff99bf states what a hit means: "a concrete Weil polynomial, hence a Honda-Tate isogeny class of abelian
    varieties over F_2 with a rational point of order 131 -- the exact object the Couveignes-Lercier factor-base
    construction needs ... A hit does NOT by itself give a factor base: the degree half (an explicit group with
    one-coordinate-enough translation formulae, and a degree bound on the descended system against GGMP example
    5.1's ~280x solve-cost penalty) remains open".
- **External ingredients.**
  - Dupuy, Kedlaya, Roe, Vincent, "Isogeny classes of abelian varieties over finite fields in the LMFDB",
    arXiv:2003.05380, in Arithmetic Geometry, Number Theory, and Computation, pp. 375-448. Provenance: retrieved.
    Their completeness statement: for each (g, q) present, every isogeny class is included.
  - The tables rest on Kedlaya's root-unitary search ("Search techniques for root-unitary polynomials", 2008;
    recalled).
  - Honda-Tate theory (recalled). Couveignes-Lercier, elliptic periods, FFA 2009 (recalled).
- **Produced results.** Queries on the LMFDB `av_fq_isog` table, which I ran, plus my own recounts.
  1. q = 2, isogeny classes with 131 | #A(F_2), by dimension g = 1..6: 0, 0, 0, 0, **24**, **617**. The class totals
     5, 35, 215, 1645, 14325, 164937 match LMFDB completeness.
     - The g = 5 list (24 classes; 21 with #A(F_2) = 131 and 3 with 262; 11 classes contain Jacobians) **reproduces**
       EV-BINSTD-2d41c3 (the program's own result, 2026-10-01, preliminary). It is not new.
     - The **g = 6 count is new to the program**. EV-BINSTD-2d41c3 records g = 6 as failed_infrastructure (IMP-H1,
       a projected ~1,400 h). Per LMFDB, not recounted by me: 617 classes, 497 simple, 173 containing Jacobians,
       8 containing hyperelliptic Jacobians, and 375 with #A(F_2) = 131 exactly.
     - Existence needs no LMFDB completeness. Completeness matters only for the "these are all" reading.
  2. Certificate for g = 5, independent of the LMFDB curve data (`verify_g5.py`, `verify_irred_hyp.py`).
     - All 24 polynomials pass the symmetry check, the |alpha| = sqrt(2) check and L(1) == 0 mod 131.
     - All 24 are irreducible over Q (sympy).
     - For q = p prime, a non-real Weil number gives a commutative End^0 with e = 1. So each irreducible polynomial is
       the Frobenius polynomial of a simple 5-dimensional abelian variety with #A(F_2) = P(1), by Honda-Tate.
  3. **An explicit Jacobian, which upgrades EV-BINSTD-2d41c3's "does NOT upgrade ... to 'is a Jacobian'".**
     - The curve: the hyperelliptic genus-6 curve y^2 + (x^7 + x + 1) y = x^6 + x^3 + x^2 over F_2 (LMFDB class
       6.2.b_b_ab_b_d_l).
     - Smoothness: gcd(h, f'^2 + h'^2 f) = 1 over F_2, with deg h = g+1 = 7 and h irreducible.
     - My brute-force counts give #C(F_{2^k}) = 4, 6, 4, 26, 44, 102 for k = 1..6.
     - The reconstructed L-polynomial is [1,1,1,-1,1,3,11,6,4,-8,16,32,64]. It is irreducible, has the Weil property
       and satisfies **#J(F_2) = L(1) = 131**. J(F_2) is cyclic of order 131, and the curve is ordinary (2-rank 6).
     - A genus-5 canonical curve (three quadrics in P^4, class 5.2.b_d_e_i_k) also recounts to #J(F_2) = 131 by brute
       force over F_{2^1..2^5}. Smoothness of that model was not checked independently.
  4. A minimal-dimension table for toy ladders (`min_dim_census_q2.json`), for primes n <= 293: the least g with
     n | #A(F_2).
     - g = 2 at n = 11, 13, 19.
     - g = 3 at n = 17, 23, 29, 31, 37, 41, 71.
     - g = 5 at n = 107, 127, 131, 151-199 and 163, which is K-163's degree.
     - For each n, explicit Jacobians exist at the minimal g in most cases.
- **Mechanism (the degree half; not yet built).**
  1. J is the genus-6 Jacobian with J(F_2) = <T>, T of order 131.
  2. The Lang map L(R) = Frob(R) - R has fibre L^{-1}(T), a torsor under Z/131. Its points R satisfy
     Frob^i(R) = R + iT, and they are defined over F_{2^131}.
  3. Coordinates of R (Mumford u-coefficients) generate F_{2^131}, and Frobenius acts on the fibre as translation by T.
  4. Candidate factor bases are subsets of F_{2^131} built from low-degree functions on J evaluated along the fibre.
     They are Frobenius-stable and non-linear: an "abelian-period" base in the Couveignes-Lercier sense.
- **Pair; class.** Representation: torsor coordinates on a genus-6 Jacobian over F_2 (R3). Operation set: Frobenius,
  acting as translation by T on the fibre. Class: **partial-action**, since only Frobenius translation (orbit) is
  claimed.
- **SO codes touched.**
  - **SO-FROB**, LEAD-ICB-frobenius-orbit-factor-base: "... the stable subspaces form an arithmetic lattice fixed by the
    factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more ... At prime n
    with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty ... Rho gets the matching sqrt(2n) from the
    same automorphisms, so the matched gap is unchanged. ... Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy
    to n = 61 measured; ECC2K-130 by structure." Premise escaped: "sigma-stable subspaces". The abelian-period base is
    non-linear. The cap "exactly n ... never more" on orbit counting still applies by the same orbit argument.
  - **SO-TABLE (binary)**, LEAD-ICB-generic-table-oracle: "Every oracle built from group operations and membership
    tests makes IC a generic-group algorithm with advice ... Scope: all binary and Koblitz curves, one target, setup
    charged." Premise escaped: "group operations and membership tests". The decomposition must be algebraic in torsor
    coordinates.
  - **SO-QSP**, LEAD-ICB-quasi-subfield-polynomials: "every linearized QSP has beta >= 3/4 ...". Premise escaped:
    "linearized". Torsor-period sets are not linearised.
- **First discriminating step, on the toy ladder from item 4.**
  - n = 11 or 13 at g = 2, or n = 17 at g = 3, using explicit Jacobians from the LMFDB.
  - Build the Lang torsor and an abelian-period base F of matched size. Run H-CERTBIN's matched-|F| per-attempt
    comparison (D <= 5 closure work, WDSat conflicts) against a random subspace and a size-matched null.
  - Per-attempt cost within [0.5, 2] of the subspace arm → **open_next_step**. Price n = 131 on the genus-6 J above.
    best_measured: the ratio.
  - Cost above 2x → **closed_obstructed(measured)**: Couveignes-Lercier route at g <= 6 for n = 131, reason: membership
    cost.
  - Torsor coordinates do not give a membership test of bounded degree → **closed_obstructed(cost_model)**.
- **Tier: I. Predicted incremental exponent gain: 0.**
  - H6 (prediction): the SO-FROB orbit cap holds for any Frobenius-stable base, so the most it can buy is log2(131) =
    7.03 bits, the same as the orbit union already measured. Rho gets sqrt(2n), so the matched gap is unchanged.
  - Predicted constant: the per-attempt decomposition probability at matched |F| equals the birthday value. That is
    true of every Frobenius-stable base measured at n = 11..23.
  - So the predicted per-attempt cost ratio is >= 1. Any gain would have to come from a lower membership degree, and
    beat GGMP's ~280x penalty.
- **Costs.**
  - Implementation: 2-5 days (Cantor arithmetic over F_{2^n}, Lang-torsor construction, base builder).
  - Compute: minutes at toy size. A g = 6 recount for completeness would take hours if wanted.
  - Self-kill risk: high. It is likely to close as membership cost, but it is a cheap and decisive close.
- **Match phrasings.**
  1. "abelian variety over F_2 with a rational point of order 131: Couveignes-Lercier abelian periods for F_{2^131}"
  2. "a genus-6 curve over F_2 whose Jacobian has exactly 131 points gives a Frobenius-stable model of the 131-bit
     field"
  3. "non-subspace Frobenius-stable factor base: orbit gain exactly n and never more; the stable structure is paid back
     in membership cost"

## 4. Killed candidates, with reasons

| # | idea | why killed |
|:--|:--|:--|
| K1 | Berkovich/tropical skeleton of E over Q_p as a decomposition aid | Every lift of E/F_p has good reduction, so the skeleton is a point (BPR, recalled). Tate-curve structure appears only on degenerations, which is SO-XEDNI's function-field territory: alpha = 3. |
| K2 | Tropical decoder for Semaev (IDEA-20260814-c3af09) as an algorithm | Turned into C2: it is the unpruned baseline. |
| K3 | Elliptic Teichmuller lift (second Witt coordinate) as a factor base or digit | The second coordinate has degree about p in x (Finotti, recalled). Its density-1/p base is empty, and reading the digit is chance (KN-FIND-e8cfdc). Covered by SO-PADIC. |
| K4 | Serre-Tate deformation over Z/p^2 carrying the log | Ext^1(Z/N, F_p) = 0, so the extension splits canonically and carries nothing (Wall P). |
| K5 | Smart's attack on the p-part of E(F_{p^k}) when a_p^k == 1 (mod p) | Sylow subgroups are coprime, with no map from the N-part. k = ord_p(a_p) is about p anyway. |
| K6 | Canonical lift of Koblitz curves (CM curve j = -3375, D = -7, defined over Q) | Torsion lifts with zero formal defect; r is odd. SO-PADIC/SO-ENDO. N-torsion fields have degree about N. |
| K7 | Lauder-Wan / Dwork / Kedlaya point counting as a decomposition decision oracle | Over F_p the cost is poly(p) > sqrt(p). Over descended F_2 systems it is exponential in the ml variables, which is no better than enumeration. |
| K8 | Harvey average-polynomial-time remainder trees for B3 batching | Needs many moduli. Prime IC has one modulus, and the Montgomery trick is already optimal. B3 cannot cross the S*T^2 exponent wall in any case. |
| K9 | Gross-Koblitz / Stickelberger biases of character-constant bases | SO-ALGFB conservation: mean yield depends only on B, and character-constant sets are named in its forecloses list. |
| K10 | Deligne/Katz equidistribution to bound decomposition-count variance (closing coincidence-harvest escapes) | A size-B algebraic base has conductor of order B, so Weil-Deligne bounds are vacuous at B ~ p^{1/m}. Interval bases are not trace functions. |
| K11 | Function-field (F_2[t], t-adic degree) Coppersmith for binary decomposition | The asymptotic reach LP is the same as the archimedean one. In char 2, S_3 = e2^2 + e3 + b reduces to the F_2-linear plus bilinear u = v x1 system, which is the known descended/product-space formulation (KR-IC-73db3f, KR-IC-f5c584). |
| K12 | Implicit-membership bases defined by point counts of auxiliary curves (#C_{x(P)} == 0 mod 2^k) | Membership needs a test per element, so it is enumerative. SO-TABLE applies. |
| K13 | CM-cycle bases {j : an l-isogeny cycle of length k exists} via modular polynomials | An F_p-rational cycle needs l^k >~ |D| ~ p, so the set has size at least p and is not small. |
| K14 | Deformation to a nodal (Tate) curve over F_p((t)) and specialisation t -> 1 | Specialisation is not continuous for the t-adic topology. No relation to E_{t=1}(F_p). |
| K15 | Small-coefficient curves (secp256k1, b = 7) with small x and small preselected targets: char-0 forcing | Only when X^6 < p, where relations must hold over Q and are rare. IC needs X ~ p^{1/4}, outside that regime. |
| K16 | BKK/mixed-volume (tropical root count) census of special-j degeneration, as an exponent lever | Newton polytopes are p-independent, so root-count changes at special j are p-independent integers (constant tier). Already priced in the ledger: IDEA-20260805-1f4a11, H-SEMAEV-002, IDEA-20260811-97e244 (BKK Newton saturation at m <= 5), and +4% Ir measured at j = 0. |
| K17 | p-adic carrier search (Denef-Vercauteren/Tuitman) for ECC2K-130 Jacobian carriers at n = 131 | The instrument works: genus about 130 over F_2 in poly(g). But the expected carrier count is < 1 for every g' >= 130 under the DiPippo-Howe isogeny-class count against about 2^{3g'} curves (heuristic; loose arithmetic, not a bound). Symmetric (Z/131-cover) carriers need at least 130 branch points by the Frobenius-twisted branch-orbit argument, which is the GHS magic-number fact restated. |
| K18 | Polynomial-calculus degree lower bound (Impagliazzo-Pudlak-Sgall) for the digit presentation | Proof complexity is not my field, and a sibling `scout/pcdeg/` directory exists, so I did not pursue it. |

## 5. Fields searched with no candidate

- Berkovich skeleta and faithful tropicalisation (Helminck, BPR): good reduction. K1.
- Formal groups, canonical lifts, Teichmuller/Witt digits, Serre-Tate: Wall P. K3-K6.
- Kedlaya/Harvey/Lauder-Wan/Tuitman point counting as an oracle: K7, K8.
- Gauss/Jacobi sums, Gross-Koblitz, Stickelberger: K9.
- Deligne/Katz equidistribution of yield: K10.
- t-adic function-field small roots for binary fields: K11.
- p-adic Newton polygons and tropical root counts of F_p Semaev systems: C2 makes them trivial.
- BKK/GKZ special-j: K16.

## 6. Citations

| source | used for | provenance |
|:--|:--|:--|
| Lauter-Stange, SAC 2008, LNCS 5381 pp. 309-327; arXiv:0803.0728 | C1, load-bearing | retrieved (full text) |
| Aono-Agrawal-Satoh-Watanabe, ACISP 2012; AAECC 29 (2017) 169-195 | C3 | retrieved (abstract/summary) |
| Chinburg-Hemenway-Heninger-Scherr, arXiv:1605.08065 | C3 | retrieved (abstract); venue ASIACRYPT 2016 recalled |
| Ryan, EUROCRYPT 2025, LNCS 15606 pp. 355-384; ePrint 2024/1577 | C3 | retrieved (abstract) |
| Dupuy-Kedlaya-Roe-Vincent, arXiv:2003.05380 | C4, load-bearing | retrieved |
| LMFDB av_fq_isog queries | C4 | retrieved (run by me), recounts produced |
| Honda-Tate; Tate (1966), Honda (1968) | C4 | recalled |
| Couveignes-Lercier, "Elliptic periods for finite fields", FFA 15 (2009) | C4 | recalled |
| Kedlaya, "Search techniques for root-unitary polynomials" (2008) | C4 | recalled |
| Baker-Payne-Rabinoff, Algebraic Geometry 3 (2016) | Wall T | recalled |
| Finotti, elliptic Teichmuller lift degrees | K3 | recalled |
| Shipsey, PhD thesis (2000) | C1 context | recalled, cited by Lauter-Stange |
| Jochemsz-May, ASIACRYPT 2006; Howgrave-Graham 1997; Boneh-Durfee 1999 | C3 | recalled |

## 7. Artifacts

All in `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/padic-tropical/`:

- `miller_vs_lauterstange.py` / `.out` (C1)
- `ceiling_lp.py` / `.out` (C3; S_3 and S_4 rows only, the S_5 row was not computed because the run was terminated)
- `verify_g5.py`, `verify_irred_hyp.py`, `smooth_check.txt`, `min_dim_census_q2.json` (C4)
- `dl_lauterstange/ls.pdf`, `ls.txt` (source copy, untrusted download, read as data only)
- `match-log.txt`
