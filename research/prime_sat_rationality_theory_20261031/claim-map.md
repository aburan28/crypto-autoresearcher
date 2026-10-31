# Rationality encodings: exact claims submitted for review

This is an unreviewed claim map, not a decision. All source bytes are bound in source-package.json. Original scratch-relative references are resolved through the prospective source-inputs.json source/destination mapping; canonical copied bytes are the review inputs. The prospective review plan has seven joints. No software suite, solver, scientific trial or benchmark was run to assemble this package.

Common assumptions: prime p>3; nonsingular y²=f(x)=x³+ax+b; all witnesses in F_p, not an algebraic closure; exact normalized chart/norm identities; monic modulus; separate verified splitting and interval constraints; target subtraction and signed multiplicities retained. Every claim below depends on its own detailed hypotheses in the frozen source.

| Joint | Submitted statement | Source within coordination/prime_sat_rationality_theory_20261031/sources |
|---|---|---|
| common_root_localization | Conditional on split norm, square-or-zero f on the common-root support suffices and is necessary for rational zero-divisor support; removing a rational target does not remove a nonsquare pair. | signed-recovery/proof.md |
| slack_projection | beta²=F+c*u encodes c!=0 OR F square-or-zero; valid fibers have p or2p points according to the exact c,F cases. | conditional-square/proof.md |
| guard_projection | The five guard equations implement the same predicate with one or two valid auxiliary points and imply Boolean e. | conditional-square/proof.md |
| nilpotent_square | For split monic degree-k U, exists degree<k C with (C²-f)^k=0modU iff every root has square-or-zero f; U=1 is empty. Exact square congruence fails at repeated branch roots. | nilpotent-square/proof.md |
| fiber_count | With r distinct roots and q nonzero-square values, C has2^q*p^(k-r) witnesses; fixed division intermediates add no fibers. | nilpotent-square/proof.md; implementation-draft/CIRCUIT-LAYOUT.draft.md |
| quadratic_circuit | Coefficient identities LR=P+UQ and the specified reductions give k0..5 added-variable/equation counts0,3,9,15,21,36, all degree<=2. | implementation-draft/CIRCUIT-LAYOUT.draft.md |
| complete_integration_boundary | Keep nonconstant-linear, nonzero-constant and zero-B strata; preserve signed output and project normalized A/B coefficients rather than U alone. | conditional-square/proof.md; implementation-draft/SOURCE-API.draft.md; implementation-draft/sat-integration-audit.json |

All seven verdicts are pending. The counts are field-level symbolic counts, excluding chart/norm/interval generators, bit ranges, carries and certificate costs. Quadratic generators do not establish degree of regularity. No novelty claim, universal chart-descent proof, witness-search bound or performance claim is submitted.

The existing fixed-software chart decision is background, not proof of these new encodings. The fresh reviewer is asked to inspect the supplied proofs and produce independent reasoning/counterexamples; this is explicitly a source audit, not blind rederivation. Exact source and runtime limitations must remain in the attestation.
