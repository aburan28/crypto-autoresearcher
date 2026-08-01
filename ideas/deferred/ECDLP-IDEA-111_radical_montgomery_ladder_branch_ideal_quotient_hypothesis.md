# ECDLP-IDEA-111 — Radical Montgomery-ladder branch-ideal quotient

## Status and claim labels

- Class: conservative algebraic source compression, theorem-deferred.
- Risk band: medium-high.
- Top lane: `-`.
- Cohort: `20260717-f`.
- State: `deferred_lossless_quotient_theorem_required`.
- Approval: `unapproved`.
- Evidence scale: no implementation or run; any later reduced-bit experiment is `toy` evidence.
- Cost claims: `heuristic` and `model-bound` until losslessness, quotient rank, output, and solve complexity are proved and measured.
- Novelty: `novelty-unverified`; no qualifying lossless branch quotient has been established.
- Breakthrough claim: **none**; a correct ladder encoding, radical ideal, or recovered toy scalar would not alone beat Pollard rho or BSGS.

## Falsifiable hypothesis

Encode a length-\(t\) Montgomery-ladder inverse problem for \(R=[s]P\) as a radical branch ideal with Boolean selectors \(z_i(z_i-1)=0\), exact addition/doubling equations, and all exceptional denominators saturated. The hypothesis is that the union of the \(2^t\) translated ladder branches has a **lossless, target-uniform quotient** whose normal-form rank grows as \(2^{\kappa t}\) for a proved \(\kappa<1/2\), while retaining enough information to enumerate complete factor-base decompositions and perform blind descent. The claim is false if the saturated branch components are generically disjoint and any lossless quotient has rank \(2^{(1-o(1))t}\), or if compression loses a branch, introduces spurious points, or defers exponential work to witness reconstruction.

## Mechanism-new operation

The proposed new operation is a **lossless radical-union quotient**: quotient the saturated Boolean ladder ideal by common translation/denominator structure and prove that the quotient simultaneously represents every branch with sub-square-root rank. It seeks shared algebra across mutually translated branch components, not a faster Gröbner/SAT solver for the same exponential ideal.

The strict duplicate/control boundary is: coordinate changes, window sizes, solver substitutions, preprocessing parameters, dense resultants, explicit branch/large-prime tables, guessed branch selectors, post-hoc pruning, and relation-only certificates are duplicates or controls unless a theorem proves that the new quotient is radical, lossless, target-uniform, and has sub-rho construction plus witness-recovery cost. A DAG that merely stores common prefixes or an ideal that omits denominator/exceptional branches is not the new operation.

## Assumptions

- \(E/\mathbb F_p\) contains a prime-order subgroup \(G=\langle P\rangle\) of order \(N\), and a complete Montgomery-compatible or projective formula set is fixed.
- Ladder length \(t=\lceil\log_2N\rceil\), bit order, exceptional cases, saturation elements, monomial order, quotient map, and factor-base predicate are committed before seeing \(Q\).
- The ideal represents the exact union of all scalar branches over the stated field, including zero denominators and points at infinity through explicit case components.
- Quotient compression is uniform in the target point and does not store curve-specific scalar tables as uncharged advice.
- Normal-form construction, coefficient growth, extension fields, basis output, witness reconstruction, verification, and failed branches are charged.
- Factor-base relation rows and target descents must be complete equalities in \(E(\mathbb F_p)\), independently verified.
- No experiment is authorized until the lossless quotient theorem and a symbolic size bound pass independent review.

## Semantic fingerprint

`Montgomery_ladder_inverse | Boolean_branch_radical_ideal | denominator_saturation | translated_component_union | lossless_common_structure_quotient | sub_sqrt_normal_form_rank | complete_factor_base_witness | blind_masked_descent | theorem_first_gate`

The semantic novelty is exactly the lossless rank-reducing quotient. Re-encoding the same branch union, swapping solvers, or compressing only its syntax is a duplicate of existing preimage-DAG/branch-barrier work.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H650`, the algebraic ladder/preimage representation closest to a branch-ideal formulation.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1408-PREIMAGE-DAG`, the positive correctness control for sharing explicit preimage computation in a DAG.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless-DAG negative showing that shared syntax need not reduce complete edge/output cost.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H666`, which asks whether exact factor membership has a bounded public polynomial/rational lift in a small number of scalar coordinates; it is a compact-membership control, not evidence about branch-component separation.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H668`, which asks whether the P1426 rank-`4B` kernel has an explicit Riemann–Roch coefficient factorization and transposed evaluation; it is the closest recorded rank-factorization control, not a ladder-quotient result.

## Closest primary literature

- Montgomery gives the x-coordinate ladder and its differential-addition structure: [P. L. Montgomery, *Speeding the Pollard and elliptic curve methods of factorization*](https://www.ams.org/journals/mcom/1987-48-177/S0025-5718-1987-0866113-7/).
- Shoup proves generic-group lower bounds that anchor the \(N^{1/2}\) comparison when the representation yields no exploitable non-generic operation: [V. Shoup, *Lower bounds for discrete logarithms and related problems*](https://doi.org/10.1007/3-540-69053-0_18).
- Lauter and Stange study elliptic divisibility sequences and scalar-multiplication algebra relevant to compact recurrence encodings: [K. Lauter and K. Stange, *The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences*](https://arxiv.org/abs/0803.0728).

None proves a sub-square-root lossless quotient of the full saturated ladder branch union. The proposed operation is therefore `novelty-unverified`.

## Complete factor-base-to-target-descent path

- **Frozen specification:** hash \((E,P,N)\), complete ladder formulas, bit length, Boolean ideal, all saturation/case components, monomial order, quotient construction, witness decoder, and a target-independent factor-base predicate. Fix \(F=\{F_1,\dots,F_B\}\) with \(B=N^\beta\).
- **Quotient construction:** build the target-uniform symbolic quotient once, prove a bijection between its decoded points and the full saturated branch union, publish the basis/rank and all coefficient/output sizes, and forbid target-specific pruning.
- **Known-source relations:** sample known \(s\), set \(R=[s]P\), specialize only the public target coordinates in the frozen quotient, and decode a complete equality \(R=\sum_i e_iF_i\). Verify it exactly on the curve; only then record \(s=\sum_i e_i\log_P(F_i)\pmod N\). A recovered ladder bit string with no factor-base equality is diagnostic, not a relation path.
- **Matrix and factor logs:** collect at least \(B+\sigma\) independently generated exact rows, retain all rejected/spurious quotient outputs, publish the matrix, demonstrate rank \(B\) over \(\mathbb F_N\), solve for factor logarithms, and independently check every \([\log_P(F_i)]P=F_i\).
- **Blind target:** a separate process samples hidden \(t\), supplies \(R_t=Q+[t]P\), and prevents \(t\) and \(Q\) from affecting the quotient, basis, branch ordering, or factor base.
- **Complete descent:** specialize the unchanged quotient at \(R_t\), enumerate and charge all normal forms and decoded witnesses, accept only a complete verified \(R_t=\sum_i d_iF_i\), and compute \(\hat x=\sum_i d_i\log_P(F_i)-t\pmod N\).
- **Final verification:** reveal \(t\), check \([\hat x]P=Q\), and preserve every missing, spurious, ambiguous, or timed-out branch. Direct scalar recovery from a decoded branch, if it occurs, is charged as the same full witness output rather than credited as a free shortcut.

## Full rho/BSGS cost model

Let \(B=N^\beta\) and \(t=\lceil\log_2N\rceil\). Define \(N^a,N^{a_m}\) as ideal/formula setup; \(N^g,N^{g_m}\) as construction of the lossless quotient; \(N^d\) as its materialized normal-form rank/output basis; \(N^f,N^{f_m}\) as factor-base construction; \(N^q,N^{q_m}\) as per-target specialization and solve work; \(N^o\) as complete witness output; \(N^u\) as ambiguity/spurious-branch resolution; \(N^v,N^{v_m}\) as exact verification; \(N^\delta,N^{\delta_t}\) as reciprocal source-relation and blind-descent densities; and \(N^\ell,N^{\ell_m}\) as matrix rank/linear-algebra time and memory. Coefficient bit growth and saturation components belong to \(g,d,q,o\), not an uncharged constant.

The complete time and peak-memory exponents are

\[
\lambda=\max\{a,g+d,f,\beta+\delta+q+o+u+v,\ell,\delta_t+q+o+u+v\},
\]

\[
\mu=\max\{a_m,g_m+d,f_m,q_m,\ell_m,\beta+o,o+u,v_m\}.
\]

The hypothesized theorem must give \(g+d<1/2\); a compact input with exponential normal-form or witness output does not qualify. Without special matrix structure, \(\ell\ge2\beta\) and \(\ell_m\ge\beta\). Pollard rho has expected time exponent \(1/2\) and negligible serial memory, with parallel collision tables charged. BSGS has time and memory exponents \(1/2\). All symbolic preprocessing must be rerun or explicitly amortized under a declared multi-target model; the single-target claim may not hide it as fixed-curve advice.

## Likely fatal obstruction

For a generic point, the two inverse ladder transitions are distinct translations and their saturated components share little beyond the syntactic recurrence. Repeating them produces generically disjoint components whose coordinate ring dimension and number of witnesses double at each bit. Radicalization and saturation remove multiplicity and invalid denominators but do not identify distinct scalar branches. A quotient that merges them is therefore likely lossy; a quotient that keeps enough idempotents to decode every branch retains rank \(2^{(1-o(1))t}\). Any apparent compression is expected to move the exponential cost into coefficient degree, specialization, or witness enumeration.

## Proof track

- Specify the complete saturated branch ideal and prove radicality plus exact coverage of all ladder paths, including exceptional components.
- Construct an explicit quotient and decoder, prove a bijection on geometric points for every generic target, and bound construction, normal-form rank, coefficient growth, and output by \(N^{\kappa+o(1)}\) with \(\kappa<1/2\).
- Prove that specialization is target-uniform and that complete factor-base witnesses are recovered without enumerating discarded idempotents.
- Only after those theorems, instantiate rank, density, linear algebra, blind descent, verification, and memory terms in \((\lambda,\mu)\).

## Disproof track

- Prove a Chinese-remainder/idempotent lower bound showing that the saturated generic branch components are disjoint and every lossless quotient has dimension at least \(2^{t-o(t)}\).
- Show on symbolic small \(t\) that quotient-rank ratios approach branch count after saturation, distinguishing real algebraic sharing from common-subexpression compression.
- Construct exceptional-denominator and point-at-infinity cases to test losslessness; one missing or spurious decoded branch rejects the quotient.
- Audit witness reconstruction separately from ideal construction so delayed enumeration cannot masquerade as compression.

## Positive and negative controls

- **Positive implementation control:** a synthetic branch system with deliberately identical components and a known low-rank quotient; the theorem checker and decoder must certify it.
- **Positive correctness control:** imported `ECFG-P1408-PREIMAGE-DAG`, used only to check complete branch generation and witness verification.
- **Negative structural control:** independent generic affine translations whose radical component union has a known direct-product coordinate ring.
- **Negative completeness control:** exceptional denominators, the point at infinity, and both bit values at every toy ladder depth.
- **Duplicate control:** alternate solvers, monomial orders, window sizes, prefix DAGs, dense resultants, or guessed selector pruning without a lossless-rank theorem.

## Quantitative promotion and falsification gates

This candidate remains deferred and `unapproved` until an independent proof verifies radicality, exact coverage, lossless decoding, target uniformity, and quotient construction plus rank exponent strictly below \(1/2\). Only then may a preregistered `toy` preflight use at least 20 fresh curves at each of 14, 16, 18, and 20 subgroup bits, exhaustive scalar/branch truth through 18 bits, and at the two largest sizes at least 1,000 exact relations and 100 blind masked descents per size. Promotion further requires zero missing/spurious branches, zero invalid relations/scalars, rank at least \(0.80B\) before solve and exactly \(B\) at solve, and bootstrap 95% upper confidence bounds \(\lambda\le0.45\) and \(\mu\le0.45\).

The candidate is falsified if a generic-component lower bound gives quotient rank \(N^{1/2-o(1)}\) or larger, if one branch is lost or invented, if witness output reconstructs an exponential table, if target-specific pruning is needed, or if preregistered complete scaling gives a 95% lower confidence bound \(\lambda\ge0.50\) or \(\mu\ge0.50\). No empirical solver run can override a failed losslessness theorem.

## Artifact plan

The theorem gate, if undertaken, belongs at `ideas/artifacts/ECDLP-IDEA-111/lossless_branch_quotient_gate.md`; a future frozen ideal/quotient schema belongs at `ideas/artifacts/ECDLP-IDEA-111/branch_ideal_spec.yaml`; and only post-approval independent rank, completeness, controls, and descent results belong at `ideas/artifacts/ECDLP-IDEA-111/analysis.md`. These are planned paths only: do not create directories, configs, or result artifacts while the candidate is deferred.

## Interpretation boundary

This is a theorem-deferred, novelty-unverified representation proposal, not an authorized experiment. Compact source code, a smaller Gröbner basis, a valid radical ideal, a solved toy ladder, or correct relations do not prove a lower asymptotic exponent. Heuristic and model-bound estimates remain diagnostics. Promotion requires a lossless quotient theorem and full source/output/rank/linear-algebra/blind-descent/memory accounting below rho/BSGS; otherwise the recorded DAG edge barrier controls.

## Exactly one next executable action

1. Draft the lossless-quotient theorem statement and generic-component dimension lower-bound test at `ideas/artifacts/ECDLP-IDEA-111/lossless_branch_quotient_gate.md`, but do not create that artifact or run a solver until independent review authorizes the theorem gate.
