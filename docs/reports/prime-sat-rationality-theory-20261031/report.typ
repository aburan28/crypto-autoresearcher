#set page(paper: "a4", margin: 17mm, numbering: "1")
#set text(size: 9pt)
= Rationality encodings: independent review
*DEC-20261031-430815 · TASK-20261031-6c3fc9*

#image("diagram.svg", width: 100%)

Seven conditional rationality-encoding claims passed independent mathematical source review. The accepted components are common-root localization, slack and guard projection, nilpotent-square rationality, witness-fiber counts, quadratic circuit counts, and the mathematical integration contract. This decision preserves one concrete correction to ancillary sign wording.

Assumptions: prime p greater than 3, nonsingular short Weierstrass curve, split norm or split monic U as required, field-valued witnesses, normalized A/B projection, and every chart stratum including B=0. Actual engine integration was outside the reviewer’s source set.

For split monic U of degree k, rationality is equivalent to existence of C of degree less than k with (C²-f)\^k=0 modulo U. This retains repeated branch roots, which an exact square congruence can incorrectly reject. U=1 is the separate empty case. The fiber has 2\^q p\^(k-r) choices, where r counts distinct roots and q counts those with nonzero square ordinates.

The nilpotent circuit adds respectively 0, 3, 9, 15, 21, 36 field variables and the same numbers of equations for k=0..5. The conditional linear-B guard adds ten variables and twelve quadratic equations; the slack version adds nine variables and eight equations. These symbolic block counts exclude norm, membership, field ranges, bit arithmetic and certificate work.

F1 — additive correction. On E/F5: y²=x³+1, take h=X(y-1), A=-X, B=X and U=X\^5, with target O. At P=(0,1), y-1 has order three, so h has order four; at -P it has order one. The divisor is therefore 4P+(-P), although both auxiliary guard roots beta=±1 are valid. Replace the universal “same balanced signed multiset” wording by “same normalized chart and uniquely recovered signed divisor.” Balance holds only for zero residual excess; otherwise the residual ratio selects the sign. The frozen proof and PDF remain unchanged; this report and decision are the additive correction. The example is a required future software regression, not an executed test here.

The reviewer also exhibits failures when splitting is dropped, extension-field witnesses are allowed, zero-B charts are removed, or only U is projected. Quadratic generator degree alone gives no degree-of-regularity bound. The accepted complete-integration claim is a contract, not verified bridge software.

Custody: fifteen frozen sources and twenty-five snapshot hashes reconcile. Review TASK-20261031-048643 is a separate source-audit session with producer proofs as deliberate inputs; no blind rederivation is claimed. The native gate checks declared plan/attestation consistency, not mathematical truth or authenticated serving model. Effective model, effort and capacity remain unverified under the prospective amendment. No test suite, solver instance, benchmark or remote job was run in this review.

Next implement the corrected guard, slack and nilpotent predicates with complete signed recovery and the F1 regression. Then compare complete projected signed model sets in certified SAT, including prefix-coverage certificates and all reconstruction/checking work. The unchanged partial-matrix and two-bit backdoor configurations are not being scaled.


Exact sources and gate receipt: report-inputs.json. Diagram shows claim dependencies; no timing measurements were collected.
