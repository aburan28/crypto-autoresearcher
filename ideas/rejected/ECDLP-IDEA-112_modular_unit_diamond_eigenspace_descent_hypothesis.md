# ECDLP-IDEA-112 — Modular-unit diamond-eigenspace descent

## Status and claim labels

- Class: representation-changing level-structure channel, preserved rejection.
- Risk band: high.
- Top lane: `-`.
- Cohort: `20260717-f`.
- State: `rejected_level_degree_no_go`.
- Approval: `unapproved`.
- Evidence scale: no run; any later small-level calculation is `toy` evidence only.
- Cost claims: `heuristic` and `model-bound` until modular-model degree, unit representation, evaluation, output, and descent are fully charged.
- Novelty: `novelty-unverified`; a sub-rho evaluable diamond-eigenbasis separating all scalars has not been shown.
- Breakthrough claim: **none**; correct modular-unit identities or exact toy scalar recovery do not establish a generic ECDLP improvement.

## Falsifiable hypothesis

View \((E,P)\) and \((E,Q)=(E,[x]P)\) as points on a level-\(N\) modular curve, with diamond operators \(\langle a\rangle:(E,P)\mapsto(E,[a]P)\). The hypothesis is that a public family of modular-unit eigensections \(u_\chi\) can be represented and evaluated at these two level structures in total degree/output \(N^{d+o(1)}\), \(d<1/2\), and that ratios

\[
u_\chi(E,Q)/u_\chi(E,P)=\chi(x)
\]

for \(N^{s}\) precommitted characters feed a target-independent public atomizer \(D_U\) that returns every exact signed factor-base tuple, thereby determining complete source decompositions and the blind target scalar with full time and memory exponents below \(1/2\). The hypothesis is false if separating the diamond orbit forces modular-curve gonality, divisor degree, coefficient size, extension degree, number of characters, or evaluation/output at least \(N^{1/2-o(1)}\), or if \(D_U\) is equivalent to enumerating the original source relation.

## Mechanism-new operation

The proposed new operation is **diamond-eigenspace evaluation on full level structure**: diagonalize the action of \((\mathbb Z/N\mathbb Z)^\times\) on an explicitly evaluable modular-unit space and turn eigenvalue ratios into scalar characters. The claimed obstruction removal is an eigenbasis whose representation and evaluation avoid constructing the full level-\(N\) orbit.

For the factor-base route, the operation also includes the exact scalar-blind atomizer \(D_U\), frozen before target queries. Character values without that point-source inverse remain relation-only diagnostics.

The strict duplicate/control boundary is: bounded automorphisms of a fixed elliptic curve, CM endomorphisms, same-field isogenies, alternate modular parameters, solver substitutions, explicit large-prime/level tables, post-hoc character selection, dense modular resultants, and relation-only eigenvalue certificates are duplicates or controls unless a new operation constructs and evaluates enough level-\(N\) diamond eigensections below rho cost. Smooth-order character recovery on a toy level is a control, not evidence for generic prime \(N\).

## Assumptions

- \(G=\langle P\rangle\subset E(\mathbb F_p)\) has prime order \(N\), and \(Q=[x]P\) with \(x\ne0\).
- A model of the relevant level-\(N\) modular curve/stack, cusps, field of definition, modular units, diamond action, and evaluation convention is fixed before seeing \(Q\).
- The eigensections are computable from public data without enumerating the \(N\)-torsion basis, importing target-specific advice, or assuming a free level-structure oracle.
- All modular equation degrees, root-of-unity extensions, coefficient heights, precision, character reconstruction, zeros/poles, ambiguity, and output are charged.
- The factor base and characters are target-independent and precommitted; exact EC verification is required for every accepted relation and target descent.
- Any smoothness assumption on \(N-1\) is explicit and cannot stand in for a generic prime-order benchmark.
- Single-target and amortized fixed-level claims are kept separate.

## Semantic fingerprint

`prime_level_modular_curve | marked_N_torsion_point | diamond_operator_orbit | modular_unit_eigensection | scalar_character_ratio | exact_eigensignature_source_atomizer | sub_sqrt_level_representation | target_independent_factor_base | blind_masked_descent | gonality_degree_accounting`

The candidate is mechanism-new only if the diamond-eigenbasis is separating and sub-rho evaluable and its signature has an exact public source inverse. Merely restating scalar multiplication as a diamond action, computing a high-degree modular relation, or leaving atomization to source search is a level-structure/isogeny control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-015`, where a public `GL_2(Z/16Z)` basis-transition and canonical-generator certificate reconciles branch labels; it is an explicit level-orientation control, not a general modular-unit evaluator.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H651`, an addition-compatible automorphism quotient that merges pair/four outputs only while preserving orientation information; the proposed diamond eigenspace must likewise pay for orbit separation.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H652`, where orientation-segmented orbit directories make orientation implicit in witness ranges; it is an orbit-directory control, not a torsion-level coordinate theorem.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H653`, where an automorphism-closed factor base compresses point orbits into logarithm variables but retains oriented-source obligations; this is the closest recorded quotient/orientation barrier.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1412-NO-END-TO-END-PROMOTION`, the no-promotion boundary for a valid representation lacking complete costed descent.

## Closest primary literature

- Kubert and Lang develop modular units and their divisors on modular curves: [D. Kubert and S. Lang, *Modular Units*](https://doi.org/10.1007/978-1-4757-1741-9).
- Streng gives explicit generators for the modular-unit group on `Gamma_1(N)`, directly neighboring the proposed unit space but not supplying a sub-rho evaluator: [M. Streng, *Generators of the group of modular units for Gamma1(N) over the rationals*](https://arxiv.org/abs/1503.08127).
- Abramovich proves linear lower bounds for the gonality of congruence modular curves, supplying a structural degree warning at growing level: [D. Abramovich, *A linear lower bound on the gonality of modular curves*](https://arxiv.org/abs/alg-geom/9609012).

These primary sources do not furnish the claimed sub-rho diamond-eigenbasis/evaluator. The novelty and scaling claims remain `novelty-unverified`.

## Complete factor-base-to-target-descent path

- **Freeze level data:** hash \((E,P,N)\), the modular model, unit divisors, eigenbasis algorithm, field/precision rules, character set, selector, and a target-independent factor-base predicate. Construct \(F=\{F_1,\dots,F_B\}\subset G\), \(B=N^\beta\).
- **Build and audit eigensections:** construct the claimed \(u_\chi\), prove their diamond transformation law, publish degrees, coefficient heights, fields, zeros/poles, representation size, and complete setup cost. No target-conditioned unit or character may be added.
- **Known-source relations:** sample known \(s\), compute \(R=[s]P\), evaluate the frozen eigensections at \((E,R)\), and use their ratios to return a complete factor-base equality \(R=\sum_i e_iF_i\). Verify it exactly in \(E(\mathbb F_p)\), then store \(s=\sum_i e_i\log_P(F_i)\pmod N\). A character value without a complete equality is only a diagnostic.
- **Rank and factor logarithms:** collect at least \(B+\sigma\) verified relations, retain poles/collisions/failures, publish the matrix, independently confirm rank \(B\) over \(\mathbb F_N\), solve factor logs, and check \([\log_P(F_i)]P=F_i\) for every factor.
- **Blind masked target:** an independent process samples hidden \(t\), supplies \(R_t=Q+[t]P\), and withholds \(t\) from level setup, factor base, unit construction, character selection, and descent.
- **Complete descent:** evaluate the same eigensections at \((E,R_t)\), account for roots of unity, zeros, poles, character collisions, and retries, return a complete exact \(R_t=\sum_i d_iF_i\), and compute \(\hat x=\sum_i d_i\log_P(F_i)-t\pmod N\).
- **Final verification:** reveal \(t\), verify \([\hat x]P=Q\), and preserve all failures. If character ratios directly determine \(x\), their construction, number, discrete-log-in-roots-of-unity work, and output replace rather than evade the costed descent terms.

## Full rho/BSGS cost model

Let \(B=N^\beta\), use \(N^s\) eigensections/characters, and let their maximum materialized degree/representation size be \(N^d\). Define \(N^a,N^{a_m}\) as modular-model setup; \(N^g,N^{g_m}\) as eigenspace construction; \(N^f,N^{f_m}\) as factor-base construction; \(N^q,N^{q_m}\) as evaluation work per unit/character; \(N^o\) as complete relation/eigenvalue output; \(N^u\) as character/zero/pole ambiguity resolution; \(N^v,N^{v_m}\) as exact verification; \(N^\delta,N^{\delta_t}\) as reciprocal relation and blind-descent densities; and \(N^\ell,N^{\ell_m}\) as rank/linear-algebra time and memory. Field degree and coefficient height are included in \(d,g,q,o\).

The full expected exponents are

\[
\lambda=\max\{a,g+s+d,f,\beta+\delta+s+q+d+o+v,\ell,\delta_t+s+q+d+o+u+v\},
\]

\[
\mu=\max\{a_m,g_m+s+d,f_m,q_m,\ell_m,\beta+o,s+d+o+u,v_m\}.
\]

Compression may replace \(s+d\) only with a proved compressed size and charged evaluator; it cannot be deleted. Dense linear algebra gives \(\ell\ge2\beta\), \(\ell_m\ge\beta\) absent special structure. Pollard rho has expected time exponent \(1/2\) and negligible serial memory, with parallel collision costs explicit. BSGS has time exponent \(1/2\) and memory exponent \(1/2\). Amortized construction over many targets must state the crossover and does not establish a single-instance result.

## Likely fatal obstruction

The diamond action is large precisely because full level-\(N\) structure is large. Modular units that separate its orbit require divisors, fields, or coefficient data whose degree grows with the modular curve; gonality lower bounds make a bounded-degree separating coordinate implausible. A full set of eigencharacters also lives over large root-of-unity fields, and evaluating their ratios may require constructing the marked \(N\)-torsion level structure or outputting essentially the orbit. Thus the scalar has been relocated into a level object of linear or worse degree, not compressed, and total representation/evaluation cost is expected to exceed the rho boundary.

## Proof track

- Construct an explicit target-independent modular-unit space stable under diamond operators and prove its eigenbasis separates every \((E,[x]P)\) in the benchmark family.
- Bound model degree, unit divisors, coefficient heights, field extensions, basis size, evaluation, and root-of-unity reconstruction by \(N^{d+o(1)}\) with all combined exponents below \(1/2\).
- Prove conversion from ratios to complete factor-base witnesses, source density, full matrix rank, and blind target descent without level tables or advice.
- Instantiate and independently reproduce every term in \((\lambda,\mu)\) on fresh curves.

## Disproof track

- Apply gonality/divisor-degree or representation-dimension bounds to show that any rational function family separating a diamond orbit has total degree/output \(N^{1-o(1)}\) or at least \(N^{1/2-o(1)}\).
- Show that constructing/evaluating \(u_\chi(E,P)\) requires a full \(N\)-torsion basis, modular polynomial, or root-of-unity extension of prohibitive degree.
- Exhaustively evaluate small-level units and measure distinctness, poles, character count, coefficient height, and actual separation against random functions with equal output size.
- Audit apparent direct recovery for a hidden discrete logarithm in \(\mu_N\) or a precomputed diamond table.

## Positive and negative controls

- **Positive implementation control:** a toy cyclic action with supplied low-degree eigenfunctions and smooth character group; ratios must recover the planted translation exactly.
- **Positive algebra control:** a small modular level where diamond action and modular-unit transformation laws can be exhaustively verified, with no performance claim.
- **Negative control:** generic ordinary curves at comparable small subgroup sizes, using target-independent units and randomly permuted marked torsion points.
- **Negative degree control:** random rational functions matched for divisor degree/output, to test whether separation is merely paid for by representation size.
- **Duplicate control:** same-field isogenies, CM automorphisms, alternative modular parameters, dense resultants, explicit level tables, and post-hoc character subsets.

## Quantitative promotion and falsification gates

This preserved rejection can be reopened only by an independently reviewed theorem giving a separating, target-independent eigenbasis with complete construction/evaluation exponent below \(1/2\) despite level degree and field costs. A later preregistered `toy` preflight must use at least 20 fresh curves at each of 14, 16, 18, and 20 subgroup bits, exhaustive scalar/unit truth through 18 bits, and at the two largest sizes at least 1,000 verified source relations and 100 blind masked descents per size. It must yield zero invalid relations/scalars, audited rank at least \(0.80B\) before solve and exactly \(B\) at solve, and bootstrap 95% upper confidence bounds \(\lambda\le0.45\) and \(\mu\le0.45\), including all level setup, coefficients, extensions, poles, output, and failed evaluations.

The candidate is falsified if a degree/gonality theorem forces separating data \(N^{1/2-o(1)}\) or larger, if evaluation needs a full level table or target-conditioned units, if any accepted relation/scalar fails exact verification, if root-of-unity recovery merely relocates a DLP, or if preregistered scaling gives a 95% lower confidence bound \(\lambda\ge0.50\) or \(\mu\ge0.50\). Existing level-degree evidence fixes the present state as rejected.

## Artifact plan

If a genuinely new theorem reopens the record, preserve the no-go/theorem analysis at `ideas/artifacts/ECDLP-IDEA-112/level_degree_no_go.md`, freeze the modular model, unit divisors, characters, and hashes at `ideas/artifacts/ECDLP-IDEA-112/diamond_unit_model.yaml`, and place independent degree, control, rank, and blind-descent results at `ideas/artifacts/ECDLP-IDEA-112/analysis.md`. Planned paths must not be created or cited as completed evidence.

## Interpretation boundary

Restating \([x]P\) as a diamond action is exact mathematics but not scalar extraction. Modular-unit identities, correct transformation laws, valid relations, a full-rank toy matrix, or successful small-level descent show only correctness. Toy, heuristic, model-bound, and novelty-unverified claims remain explicitly bounded. No breakthrough can be claimed without a generic, blind, complete source-to-descent implementation whose setup, degree, output, linear algebra, verification, and memory beat rho/BSGS.

## Exactly one next executable action

1. Write an independent degree/gonality lower-bound note for separating diamond-eigenunit families at `ideas/artifacts/ECDLP-IDEA-112/level_degree_no_go.md`, without computing level tables or creating the artifact directory unless the bound leaves a sub-rho construction regime open.
