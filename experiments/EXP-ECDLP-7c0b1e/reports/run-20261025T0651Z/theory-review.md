# Same-session mathematical and decoder-interface check

25 October 2026. This is a read-only review by a collaborating agent within the same session. It is **not an independent-session scientific review**, a formal proof-assistant certificate, a priority search, or a scientific status transition. No experiment, EC arithmetic trial or private-target-label read was performed. No frozen source or run artifact was changed.

## Scope and outcome

The written derivation in `theory/character-kernel-bound.md` was checked against its stated assumptions and the actual candidate-construction call boundaries in the frozen `src/decoder.cpp`. The algebra in `theory/pin-obstruction.md` was also checked for the specified local tensor model. No substantive mathematical or interface blocker was found. The explicit bounds are conservative, and their narrow scope matters.

The review did not independently retrieve or audit the historical proofs of the cited external algebraic-geometric theorems. It checked the application of their standard stated forms: degree and étaleness of multiplication maps, smooth projective normalization, tame Riemann--Hurwitz, and Hasse--Weil. This review does not independently establish novelty of the application.

Reviewed-byte SHA-256 digests:

| Object | SHA-256 |
|---|---|
| `character-kernel-bound.md`, after the clarification below | `8a9c4a876f8578c84ce1fdf41d8ea93cd93604d8f836629e1584e014ca778421` |
| `pin-obstruction.md` | `6b6eb799035b3dacc9f2dda27de4f34920702fb7f60309ad4265f3e7acce4ebe` |
| frozen `decoder.cpp` | `7ffb572cac3dea4251b1e3c8b3d6e61c7959e789043f1b7e1105b173ad6d118a` |

## Character bound and constants

For every nontrivial exponent pair `(a,c)` modulo five, the claimed rational function has a geometric valuation not divisible by five. When `c=0`, the pole at O suffices. For doubling and `c!=0`, a nonzero two-torsion point has nonzero finite x under the stated `B!=0` assumption. For doubling followed by translation, the four distinct geometric poles cannot all lie in the at-most-three-point zero/pole support of x. Pullback by `[h]` preserves a witness valuation because `p` does not divide h and the multiplication map is étale. Geometric witnesses need not be rational; the argument correctly avoids that extra assumption.

The at-most-15-point support pulls back to at most `15h^2` geometric points. A valuation coprime to five forces degree five and geometric connectedness of the Kummer extension. Ramification is tame and full at each valuation not divisible by five. Thus `g=1+2m <= 1+30h^2` follows from the genus-one Riemann--Hurwitz formula. This also covers the five twists geometrically.

Over the removed rational base set of size d, each degree-five cover has at most `5d` rational points. Fourier inversion across the five twists cancels the common base term. Hasse--Weil consequently gives

`|S_j| <= 2g sqrt(p)+5d <= (60h^2+2)sqrt(p)+75h^2`.

The bound uses loose constants but the displayed constant is sufficient. Equal-sized rational fibres of `[h]:E(Fp)->H` justify normalization by N, and conditioning on the good event adds the stated factor `1/q_b`. At most fifteen bad points on H give `epsilon_b<=15/r`. No primality shortcut replaces this homomorphism argument.

## Fourier and entropy steps

The joint distribution has twenty-four nontrivial Fourier coefficients, each at most eta in magnitude. Inversion gives the `24 eta/25` joint-cell bound and the `4 eta/5` marginal-cell bounds. Expanding the product of the two marginals gives `(32 eta+16 eta^2)/25` for the difference from the product distribution.

Parseval gives `chi_square(p||Uniform_25)<=24 eta^2`. The inequality `ln t<=t-1` then yields relative entropy at most `24 eta^2/ln 2` bits. Decomposing relative entropy against uniform product proves both the mutual-information bound and the conditional-entropy-deficit bound. These steps need no lower bound on individual cells. The stated conditioned-kernel row and Dobrushin bounds are conservative consequences when `eta<1/4`.

The exceptional-symbol correction is also valid. Since the good-event indicator is a function of the full input/output feature pair, its chain-rule identity holds. Its uncertainty is at most `h2(epsilon)`, and the remaining rare conditional entropies are bounded by `log2(7)`. This gives the explicit `h2(epsilon)+epsilon log2(7)` allowance. It is correct to retain an `O(log p/p)` allowance for the full alphabet rather than asserting the conditioned `O(1/p)` result without correction. A rare deterministic O-input row prevents an inference about the full worst-row contraction from average bulk information.

One minor wording issue was found and addressed in the unfrozen mathematical note: before writing Fourier moments as `zeta^(a U+c V)`, define the mathematical labels by `chi(x)=zeta^U`. An arbitrary identification of the five roots with integers is not automatically a group-compatible exponent labeling. The implementation's sorted root labels are an arbitrary permutation; entropy, cellwise closeness to uniform, and the resulting distributional statements survive that permutation. The reviewed original note had SHA-256 `4624ea6946abde9ee36b497822d1ba69b3a6d0d87773e158de391fbac87a0841`; the clarified paragraph was read and its updated digest appears above. No frozen implementation, protocol or numerical result needed a correction.

## Signature ceiling and actual code

The counting lemma `Pr(success|W)<=min(1,B d^m/r)` is valid for a uniform scalar independent of W. Conditioning on the public preprocessing and all independent coins makes each signature's candidate list fixed. There are at most `d^m` signatures and at most B successful scalars per list. Post-hoc full-point checks select among those guesses and do not increase the candidate set.

The relevant frozen source call boundaries were checked:

- `public_targets` assigns a per-fixture ordinal from file order, without deriving it from Q. The protocol must still supply the stated target-independent order, as it does for the intended ideal population model.
- `train` derives feature training and heldout seeds from public fixture and feature data. It takes no Q argument. Operation counters do not influence its candidate-selection outputs.
- `make_views` derives its seed from public fixture/feature data and the target ordinal. The sampled R points do not depend on Q. Q enters each shifted target and hence its terminal feature label.
- `search` receives the start and terminal labels. In exact-prefix mode it additionally receives R points and an advance closure that uses only doubling, public P and the feature function. Its exact guessed-prefix coordinates do not add access to Q.
- `emit_target` finishes the candidate list before checking `[candidate]P==Q`. The loop checks every candidate and does not feed a successful or failed comparison back into search.
- Public target validation has the same accepted boolean outcome for all canonical valid subgroup targets; its arithmetic/counter details are not search inputs.

Thus the stated interface lemma applies to both prefix modes at the intended valid-target population. Logging shifted coordinates or arithmetic costs does not invalidate it because those logged values are not fed to the search. This is a source-level dependency check, not OS isolation or a formal noninterference proof.

The hypotheses remain essential: the probability statement uses an ideal uniform-target population independent of public W. It does not claim exact uniformity or independence of one fixed seeded PRNG cohort after its generation inputs are conditioned on. The bound is per chosen configuration; pooled configurations require their combined observations and candidate budget. With `d<=8,m=4,B<=8`, the stated `32768/r` upper bound is vacuous at the tested subgroup sizes. Any growing-parameter extrapolation describes this abstract interface, since the present finite implementation also has explicit input-size guards.

## Local tensor note and limits

The two isolated-pin argument over a field correctly forces a common basis to be monomial. Such a basis preserves mixed parity of the AND support. The explicit rational AND-only escape has determinant -2 and therefore does not contradict the characteristic-two claim.

For the characteristic-two invariant B, the first-leg slice pairing is alternating. Mixing those slices scales it by the determinant, while each of the remaining leg actions scales the pairing by its determinant through `S^T J S=det(S)J`. The invariant proof works over any nonzero commutative characteristic-two ring with identity. Invertible matrices have unit determinants, so `B(AND)=1` cannot become the zero invariant of a parity-pure tensor. The stated restriction to a fixed isolated three-leg tensor is necessary. Larger blocks, different representations, noninvertible reductions with new semantics and sums of parity signatures are not excluded.

Neither note supplies a general ECDLP lower bound, an exact coarse Markov law, a posterior guarantee, a sample-complexity lower bound, or a novel solver. The unary character estimate does not bound the independent-pair entropy statistic without a separate argument. These limitations are already stated in the reviewed note and should remain attached when summarizing it.
