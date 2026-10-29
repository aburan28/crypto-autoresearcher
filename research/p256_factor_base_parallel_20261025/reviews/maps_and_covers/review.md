# Local adversarial check of F5, F7 and the Cartier joint

TASK-20261025-9b6553 · 25 October 2026 · PASS within the stated mathematical and implementation scope, with procedural deviations. No new mathematical defect was found in the assigned joints. This local result supplies no canonical scientific-review attestation, model-verification attestation, publication approval or state transition.

## Observation

The independent Sage 10.6 check used public P-256 constants, a fresh implementation, exact algebra, proof.all(True), a single CPU and 2 GiB, with container network disabled. Producer JSON was used only as comparison data after blind-derivation.md was saved. Producer Python was read afterwards and was never imported. Both producer manifests were hash-checked with no disagreement. Executed code, raw stdout/stderr, source hashes, exact command, exit status and completion marker are retained in this directory. No statistical sample, runtime benchmark or attack-cost measurement was conducted.

- p and r are proven prime. The published G is nonzero and [r]G=O. The exact Hasse radius floor(sqrt(4p)) is 680564733762648764426319935326885249024; the interval has the sole positive multiple r. This independently certifies #E(Fp)=r and t=89188191154553853111372247798585809583.
- The five supplied prime-factor witnesses for -Delta were independently proven prime and multiplied exactly to -Delta. Every exponent is one and Delta≡1 mod4. Thus Delta is fundamental, f_pi=1 and f_E=1 by order inclusion, for the source and its Fp-isogenous endpoints.
- Division polynomials were freshly factored at ell=3,5,11. Direct symmetric Vélu formulas reconstructed one degree-three, one degree-five and two degree-eleven maps. All four match the producer's serialized maps and endpoints, satisfy exact landing identities, and pass dual landing and both coordinate compositions in both directions. Six source fixtures (including infinity and r-1) exercise transport/recovery for each map.
- All twelve degree-five factors of psi11 were considered. Exactly two pass the independent subgroup-closure and landing checks; the other ten are rejected. The negative control is substantive: equal factor degree alone does not identify an isogeny kernel.
- The quartic and sextic smoothness conditions, genus3/genus2 and cover degrees follow directly from the equations. Fresh fibre checks include split and nonsplit supports over Fp2 and Frobenius stability. Infinity is represented with its actual multiplicity or the two infinities, respectively.
- A fresh PARI/SEA computation reproduces the complementary elliptic trace t_B=167631093631314538742209370567683050917 and order 115792089210356248762697446949407573529918512321658999656791421938299414803035. This is below r and coprime to r. The birational map from v²=s⁴−3s²+b*s to B:Y²=X³−3X²+b² was independently checked as an exact rational identity.
- The new differential calculation independently gives p|A. All five necessary Prym order candidates p²+k*p+1 (k=-2,-1,0,1,2) have gcd1 with the actual r. Five small-field point-count controls include p≡1 mod4 counterexamples; singular b=2 companions are explicitly rejected.

## Comparison and findings

| Joint | Exact producer statement | Finding | Severity |
|---|---|---|---|
| F5 conductor | report.md:16, f_pi=f_E=1 from fundamental Delta | Independently certified by complete prime-factor verification | none |
| F5 kernels and maps | report.md:39–51, rational stable kernels and dual transport | All four maps and both dual compositions checked; ten false factors rejected | none |
| F7 cover and norm | report.md:17–39 and :51–55, smooth covers and pi_*pi^*=[2] | Geometric proof and fresh fibre checks agree; arbitrary-class implementation remains absent | none |
| F7 genus-two factor | report.md:57–65, quotient B and one rational r-factor | Fresh SEA count and exact quotient map agree | none |
| New Cartier joint | analysis/cartier-proposal/derivation.md:13–79 | Differential characters, direct Cartier formula, corrected Frobenius congruence and five gcd tests agree | none |
| Custody | Normal committed-and-pushed-input precondition | Unmet under the authorized local exception; this packet cannot discharge the canonical scientific gate | procedural, blocking promotion |
| Blindness | Derive before producer results | An equation lookup in F7 obligations.md also exposed the narrative seven-fixture count and “A unknown” before the blind file; exact exposure is recorded there | procedural, limited blindness |

The earlier F7 statement that Prym r-multiplicity was unresolved (report.md:47 and result.json) describes its retained evidence. The additional Cartier proof locally resolves that mathematical question without identifying A. The historical producer files were left unchanged.

## Inference

The norm identity pi_*pi^*=[2] proves injection on the odd order-r source subgroup and recovery by [2^-1 mod r]pi_*. The derived Cartier/Weil constraints and gcd checks imply valuation_r(#J_C(Fp))=1. Thus the injected subgroup is the whole rational r-primary subgroup of the quartic Jacobian. The genus-two factorization independently gives the analogous result there. Geometric r-torsion over an algebraic closure is much larger and is outside that statement.

F5's stable cyclic kernels are finite etale because ell!=p. A rational isogeny does not require nonzero rational kernel points, and etale kernels of degree>1 are geometrically disconnected. The connected Prym P=ker(norm)^0 is a positive-dimensional abelian variety and a separate object. No kernel-connectedness inference was used.

The new proof has two independent mathematical presentations in cartier-proof-note.md: the eigenspace argument and the explicit formula dx/u³=f(x)^((p-3)/4)dx/u^p, whose numerator degree is too low to contribute to Cartier. The corrected Achter–Howe §2.5 congruence over Fp is applicable. At p=5,b=1, the Prym Cartier matrix [[2,1],[1,0]] is invertible and chi_P=T⁴−2T³−T²−10T+25; this defeats a characteristic-independent extension.

Map transport preserves the logarithm scalar. It supplies no automatic improvement in unknown-scalar recovery. Destination relation generation, independent rank modulo r, target attachment, individual logarithm and complete costs remain unknown. Curve maps and divisor fibres do not implement arbitrary-class plane-quartic arithmetic. A full-Jacobian complexity result for another subgroup or field regime cannot fill those obligations.

## Limitations and next check

The model binding and reviewer-policy fidelity were not probed, so no model_verified claim is made. This is a child native session sharing the local workspace; it is not an adapter-verified independent scientific-review session. The custody exception is the authority for continued local work. Local HEAD is 2c8c71cfff6f7f63297fbe4de4608cd94d857184; the exception names the sealed payload base c35b9da6a65e019eaa517fc1a5f7774428ff35db. No assertion equating those revisions is made. The raw package and its exception retain their own custody claims.

Independence covers source implementation and algebraic reconstruction; Sage and PARI are shared library dependencies with the producer. The B count is a fresh computation with the same point-counting backend, not a different point-count algorithm or a portable primality/SEA transcript certificate. We did not calculate the exact P-256 A, implement full quartic/Jacobian arithmetic, audit every library, verify a destination solver or measure costs. These are coverage limits, with no negative inference about other constructions.

The next checkable implementation obligation is arbitrary-class arithmetic and norm on this exact quartic, followed by a solver that handles the injected rational r-component and both transported inputs, with independently checked relation rank and scalar verification. Existing producer obligations.md files track that gap. Shared problem/index and canonical graph edits belong to the parent; this task owns only this review directory.

Provenance: producer files are internal and compared after the blind record; public constants were read from baseline/parameters.py and independently hard-coded. The primary source is Achter–Howe arXiv:1710.10726v5 §§2.2–2.5, retrieved local PDF/text and read after the blind record. Exact source hashes and verified_by are recorded in sources.json. No knowledge-search tool was available. No novelty, performance, breakthrough or official scientific-state claim is made. The diagram and report.pdf describe this local scope; existing F5/F7 canonical figures were inspected and left unchanged because this task has no shared-graph write authority.
