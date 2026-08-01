# ECDLP-IDEA-109 — Serre–Tate torsion-section jet coordinate

## Status and claim labels

- Class: representation-changing, preserved rejection merged with the prime-to-\(p\) torsion no-go.
- Risk band: high.
- Top lane: `-`.
- Cohort: `20260717-f`.
- State: `rejected_merged_prime_to_p_torsion_no_go`.
- Approval: `unapproved`.
- Evidence scale: no run; any future reduced-field preflight is `toy` evidence only.
- Cost claims: `heuristic` and `model-bound` until an explicit arithmetic circuit and end-to-end source audit exist.
- Novelty: `novelty-unverified`; the proposed jet quotient has not been shown to exist.
- Breakthrough claim: **none**; a valid lift, relation, or descent witness would establish correctness only, not an advantage over Pollard rho or BSGS.

## Falsifiable hypothesis

Let \(E/\mathbb F_p\) be ordinary, let \(G=\langle P\rangle\subset E(\mathbb F_p)\) have prime order \(N\ne p\), and let \(Q=[x]P\). The hypothesis is that a canonical Serre–Tate deformation of \((E,P,Q)\), together with the unique prime-to-\(p\) lifts of its \(N\)-torsion sections, admits a finite jet quotient \(J\) computable from public curve and point data such that

\[
J([a]R)=aJ(R)\pmod N
\]

on a density \(N^{-\delta}\) of source points, and a precommitted public jet-atom decoder \(D_J\) maps \(J(R)\) to every exact signed factor-base tuple for \(R\) without scalar labels or source enumeration. The setup, atom decoding, output size, relation collection, linear algebra, and blind target descent all have measured time and memory exponents below \(1/2\). The hypothesis is false if every canonical jet invariant is unchanged under prime-to-\(p\) torsion translation, factors only through the reduction of the base curve, requires reconstructing an \(N\)-division object of degree or size \(N^{1/2-o(1)}\), or leaves \(D_J\) equivalent to the original source search.

## Mechanism-new operation

The proposed new operation is **torsion-section jet linearization**: lift a point as an étale \(N\)-torsion section through a one-parameter Serre–Tate deformation, apply the Gauss–Manin connection and theta/rigid-function jets, and quotient the resulting jet module so scalar multiplication becomes visible as multiplication by the scalar. This is not another same-field isogeny, volcano walk, solver substitution, parameter sweep, dense resultant, explicit large-prime table, post-hoc selector, or relation-only certificate.

For the factor-base route, the same operation includes the target-independent decoder \(D_J\); scalar covariance without exact atom-to-point inversion is only a direct-coordinate diagnostic and does not instantiate the claimed relation/descent pipeline.

The strict duplicate/control boundary is: a lift that merely preserves the group law, a different choice of Serre–Tate parameter, a prime-to-\(p\) division polynomial, or a same-field isogeny is a duplicate/control unless it produces an explicitly defined nonzero \(J\) with the displayed scalar covariance and sub-rho end-to-end cost. The characteristic-\(p\) anomalous-curve logarithm is only a positive control; importing it to \(N\ne p\) without a new torsion-sensitive jet is the already recorded no-go.

## Assumptions

- \(E/\mathbb F_p\) is ordinary and is presented with enough public data to construct its canonical formal deformation without knowing \(x\).
- \(G\) has prime order \(N\ne p\), so the relevant \(N\)-torsion is finite étale over the deformation ring.
- The factor base is fixed before seeing \(Q\), and all selectors and parameters are committed before relation collection.
- The conjectural quotient \(J\) is invariant under coordinate changes but not annihilated by étale torsion translation.
- All extension-field degree, \(p\)-adic precision, division-polynomial degree, root isolation, ambiguity, and verification work is charged.
- Relation rows are accepted only after exact verification in \(E(\mathbb F_p)\); no jet equality alone is a relation certificate.
- The cost comparison is for one generic prime-order instance, not for amortized fixed-curve advice hidden outside the ledger.

## Semantic fingerprint

`ordinary_curve | canonical_Serre-Tate_deformation | prime-to-p_torsion_section_lift | Gauss-Manin_theta_jet | torsion-sensitive_scalar_covariance | public_jet_atom_decoder | target-independent_factor_base | exact_EC_relation_verification | blind_masked_descent | full_rho_BSGS_accounting`

The obstruction-removing claim is specifically that a nonzero finite jet quotient detects translation by étale \(N\)-torsion and its public decoder returns exact sources. If either operation is absent, the record semantically collapses to the existing prime-to-\(p\) lift, same-field-isogeny, or source-search negatives.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ISO-SP-001`, where Frobenius/distorted Weil self-pairings recover a cyclic torsion action on theorem-covered ascending-volcano instances; it is a torsion-orientation control, not a same-field-isogeny or Serre–Tate result.
2. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-003`, where evaluating a divided orientation on all division lifts recovers orientation data only by exposing the complete lift family; the proposed jet must avoid that output.
3. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-004`, where a primitive pairing on one projected lift certifies an orientation branch; certification is not a public scalar coordinate.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H651`, an addition-compatible automorphism-quotient proposal that can merge output nodes only while retaining compact orientation data; the shared issue is whether quotienting discards the scalar orientation.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H653`, where an automorphism-closed factor base replaces a point orbit by one logarithm variable but still needs oriented source recovery; this is the closest recorded orbit/orientation obstruction, not a torsion-lift theorem.

## Closest primary literature

- Katz develops Serre–Tate local moduli and canonical coordinates for ordinary abelian varieties: [N. Katz, *Serre–Tate local moduli*](https://link.springer.com/chapter/10.1007/BFb0090648).
- Smart's anomalous-curve attack is the exceptional \(p\)-torsion positive control, not evidence for prime-to-\(p\) torsion: [N. P. Smart, *The discrete logarithm problem on elliptic curves of trace one*](https://doi.org/10.1007/s001459900052).
- Serre and Tate's good-reduction theorem supplies essential background on abelian varieties and reduction, while Katz is the direct deformation reference: [J.-P. Serre and J. Tate, *Good reduction of abelian varieties*](https://doi.org/10.2307/1970722).

No cited source establishes the claimed scalar-covariant prime-to-\(p\) jet. Accordingly the novelty and feasibility claims remain `novelty-unverified`.

## Complete factor-base-to-target-descent path

- **Commitment and source definition:** hash the curve, \(P\), \(N\), deformation convention, jet order, precision rule, selector, and a target-independent factor-base predicate. Freeze \(F=\{F_1,\ldots,F_B\}\subset G\) with \(B=N^\beta\); do not choose \(F\) after seeing \(Q\).
- **Canonical lift:** construct the Serre–Tate deformation and the unique étale \(N\)-torsion sections above every source point used by the generator. Record extension degree, precision, branch data, and the complete cost of obtaining the jet representation.
- **Source-to-relation conversion:** sample a known scalar \(s\), compute \(R=[s]P\), and use the conjectural \(J\)-coordinate to return a complete tuple \((e_1,\ldots,e_B)\) satisfying \(R=\sum_i e_iF_i\). Reject partial, ambiguous, or jet-only matches. Verify the equality exactly on the curve and store the row \(s=\sum_i e_i\log_P(F_i)\pmod N\).
- **Rank and factor logarithms:** continue until at least \(B+\sigma\) exact rows have been accepted, publish row-generation and factor logs, compute rank over \(\mathbb F_N\), and solve only if the audited rank is \(B\). Independently recompute every recovered \(\log_P(F_i)\) by checking \([\log_P(F_i)]P=F_i\).
- **Blind masked target:** an independent process chooses unrevealed \(t\), supplies \(R_t=Q+[t]P\), and withholds \(t\) from setup, factor-base construction, relation selection, and descent.
- **Complete descent:** apply the same precommitted lift and jet decomposer to \(R_t\), charge all retries and ambiguity resolution, and accept only an exact decomposition \(R_t=\sum_i d_iF_i\). Compute \(\hat x=\sum_i d_i\log_P(F_i)-t\pmod N\).
- **Final verification:** release \(t\), verify \([\hat x]P=Q\), and retain failures and timeouts. A valid relation, full-rank matrix, or correct toy descent is not by itself a cryptanalytic improvement.

## Full rho/BSGS cost model

Let \(B=N^\beta\). Write \(N^a,N^{a_m}\) for canonical-deformation setup time and memory; \(N^j,N^{j_m}\) for torsion-section/jet construction; \(N^f,N^{f_m}\) for factor-base construction; \(N^q,N^{q_m}\) for one complete jet query; \(N^o\) for the materialized output per successful decomposition; \(N^u\) for target ambiguity resolution; \(N^v,N^{v_m}\) for exact verification; \(N^\delta\) and \(N^{\delta_t}\) for reciprocal relation and blind-descent success densities; and \(N^\ell,N^{\ell_m}\) for rank plus linear-algebra time and memory. All exponents are measured from fresh instances, and hidden extension degree and precision are included in \(j,q,o\).

The complete expected time and peak-memory exponents are

\[
\lambda=\max\{a,j,f,\beta+\delta+q+o+v,\ell,\delta_t+q+o+u+v\},
\]

\[
\mu=\max\{a_m,j_m,f_m,q_m,\ell_m,\beta+o,o+u,v_m\}.
\]

Absent proved structure, dense linear algebra gives at least \(\ell\ge 2\beta\) time and \(\ell_m\ge\beta\) memory; sparse claims must include iteration count, rank failures, and preconditioner setup. Pollard rho is the generic baseline at time exponent \(1/2\) with negligible serial memory (or explicitly charged parallel distinguished points). BSGS has time exponent \(1/2\) and memory exponent \(1/2\). A result is competitive only if both the complete \(\lambda\) and the applicable memory claim \(\mu\) beat the appropriate baseline without advice, omitted output, or postselection.

## Likely fatal obstruction

For \(N\ne p\), the \(N\)-torsion is étale and its sections lift uniquely; infinitesimal deformation therefore sees no nontrivial tangent direction along torsion translation. Gauss–Manin and Serre–Tate jets describe deformation of the abelian variety, while translation by a prime-to-\(p\) torsion section is locally constant. The expected outcome is that every coordinate-invariant finite jet either annihilates the torsion displacement or reconstructs a global level-\(N\) object whose degree, precision, or output is already \(N^{1/2-o(1)}\) or worse. That is the recorded obstruction, so this candidate is preserved as a merged rejection.

## Proof track

- Define the deformation ring, lifted sections, connection, theta trivialization, and quotient \(J\) functorially, with a proof that public inputs determine them.
- Prove that \(J\) is nonzero on the prime-to-\(p\) torsion subgroup and satisfies scalar covariance without using \(x\), an \(N\)-division table, or target-dependent advice.
- Give an exact algorithm from \(J(R)\) to complete factor-base decompositions, including density, ambiguity, output size, and independent EC verification.
- Prove rank and descent bounds and then instantiate every exponent in \((\lambda,\mu)\) on blind fresh curves.

## Disproof track

- Prove, via étaleness or translation invariance, that every finite functorial deformation jet factors through the base curve and is constant on the lifted \(N\)-torsion orbit.
- Alternatively show that separating the orbit forces level-\(N\) degree, extension degree, precision, or output \(N^{1/2-o(1)}\).
- On toy ordinary curves, exhaustively compare all torsion translates under every precommitted candidate jet; one unexplained collision in a claimed injective quotient falsifies that quotient.
- Audit any apparent speedup for hidden division-polynomial enumeration, known-log factor bases, or target-dependent parameter choice.

## Positive and negative controls

- **Positive control:** anomalous curves with subgroup order \(p\), where the Smart/Satoh-style lift exposes a characteristic-\(p\) logarithmic channel and exact recovered scalars must verify.
- **Positive implementation control:** a deliberately supplied toy additive coordinate on a cyclic group, which must drive the same relation, rank, masked-descent, and verification pipeline.
- **Negative control:** generic ordinary curves with prime subgroup \(N\ne p\), with torsion translates randomized under the same jet order and precision.
- **Negative duplicate control:** same-field isogenies, alternate Serre–Tate parameters, and higher division-polynomial orders with no proved torsion-sensitive quotient; these must not be promoted as new mechanisms.
- **Leakage control:** random relabeling of scalar indices and a factor base whose point logs are not known to the decomposition process.

## Quantitative promotion and falsification gates

The preserved rejection can be reopened only after a formal nonzero scalar-covariant \(J\) theorem passes independent review. A later executable preflight must use at least 20 fresh ordinary curves at each of 14, 16, 18, and 20 subgroup bits; exhaustive truth is required through 18 bits, followed at the two largest sizes by at least 1,000 exact accepted relations and 100 blind masked descents per size. It must have zero incorrect relations and zero incorrect final scalars, audited rank at least \(0.80B\) before completion and exactly \(B\) at solve time, and bootstrap 95% upper confidence bounds \(\lambda\le 0.45\) and \(\mu\le 0.45\), with every setup and failed attempt charged.

The hypothesis is falsified for this mechanism if étaleness proves \(J=0\), if the quotient requires target-dependent advice, if any claimed exact relation or scalar fails independent verification, if median complete relation/descent output grows as \(N^{1/2-o(1)}\), or if a preregistered fit gives a 95% lower confidence bound \(\lambda\ge 0.50\) or \(\mu\ge 0.50\). The present structural no-go already fixes the state as rejected unless a new theorem removes it.

## Artifact plan

If and only if the proof gate is reopened, place the immutable theorem/no-go note at `ideas/artifacts/ECDLP-IDEA-109/serre_tate_jet_no_go.md`, the frozen model and hashes at `ideas/artifacts/ECDLP-IDEA-109/formal_model.yaml`, and independently reproduced cost/rank/descent results at `ideas/artifacts/ECDLP-IDEA-109/analysis.md`. Do not create empty directories or treat a planned path as evidence.

## Interpretation boundary

This record is a `novelty-unverified`, theorem-level proposal merged into a known prime-to-\(p\) torsion obstruction. A canonical lift, a correct jet computation, or exact factor-base relations demonstrate only scoped correctness. Toy success, heuristic scaling, model-bound estimates, anomalous-curve behavior, and same-field transport do not imply a generic ECDLP improvement. Only blind end-to-end performance including setup, source density, output, rank, linear algebra, descent, verification, and memory may be compared with rho/BSGS.

## Exactly one next executable action

1. Write and independently check the étale-translation lemma for finite Serre–Tate/Gauss–Manin jets at `ideas/artifacts/ECDLP-IDEA-109/serre_tate_jet_no_go.md`, without starting an experiment or creating the artifact directory unless the lemma identifies a nonzero quotient.
