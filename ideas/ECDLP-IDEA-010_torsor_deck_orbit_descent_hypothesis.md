# ECDLP-IDEA-010 — Torsor deck-orbit descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cover lift, deck orbit, projected relation, or correct toy descent is not a breakthrough without a branch-complete end-to-end exponent below rho.

## Falsifiable hypothesis

For a prime-order subgroup \(\langle P\rangle\subset E(\mathbb F_p)\), \(|P|=N\asymp p\), there is a public family of covers or torsors
\[
  \pi:X\longrightarrow E
\]
with deck group \(\Gamma\) and degree \(d=N^{\alpha+o(1)}\), together with a target-independent canonicalization of selected fiber orbits. A relation reducer on \(X\) represents a lift of a random \(R=[a]P\) by a small number of precomputed deck-orbit atoms, and a certified norm/pushforward maps that relation to \(E\). The orbit quotient increases usable relation and target-descent density enough that construction, fiber solving, branch handling, relation collection, linear algebra, descent, and memory together have exponent below \(1/2\). The hypothesis is `toy`, `heuristic`, `model-bound`, and `novelty-unverified`; fixed-degree covers count only if the new orbit operation changes an exponent rather than a constant.

## Mechanism-new operation

The proposed operation is **multivalued lifting followed by deck-orbit canonicalization and certified pushforward descent**. Unlike `ECDLP-IDEA-002`, it does not assume a homomorphic conorm into a split Jacobian; it exploits the non-homomorphic fiber/orbit structure and must solve the hidden branch-consistency problem explicitly. Unlike a coordinate change or same-field isogeny, the accepted relation is first constructed among orbit atoms upstairs and then normed/pushed down. A fixed cover with only a constant-factor yield gain, an explicit table of favorable branches, solver substitution, dense resultant elimination, post-hoc branch selection, or a relation-only pushforward certificate is a duplicate/control.

## Assumptions

1. \(E/\mathbb F_p\), \(P\), and prime \(N=\operatorname{ord}(P)\asymp p\) are public; equations for \(X\), \(\pi\), \(\Gamma\), ramification, fields of definition, and exceptional fibers are explicit.
2. Cover/torsor construction is independent of \(Q\); degree \(d=N^{\alpha+o(1)}\), genus, equation size, and every extension-field representation are charged.
3. Fiber solving and orbit canonicalization use no hidden scalar, source DLP, target-derived selector, or precomputed explicit table of favorable branches.
4. Each accepted upstairs divisor/relation includes a complete certificate, and norm/pushforward yields a nontrivial verified relation in \(\langle P\rangle\), not an identity that cancels all deck information.
5. The replacement base consists of \(B=N^{\beta+o(1)}\) target-independent deck-orbit atoms; base construction, duplicates, stabilizers, ramified orbits, coefficient growth, and projected rank are measured.
6. Relation and target-descent densities are measured separately, including every branch tried or discarded; growing-degree exhaustive enumeration is not hidden in a polynomial-time label.
7. Any toy fit remains `heuristic` and `model-bound`, and a valid lift/pushforward does not by itself support a cryptographic claim.

## Semantic fingerprint

`prime-field ECDLP -> public cover/torsor fibers -> canonical deck-orbit atoms -> upstairs supported divisor/relation -> certified norm or pushforward to E -> base logarithms -> separate target fiber-orbit descent`

The indispensable operation is **target-compatible branch/orbit compression with a nontrivial pushforward relation**. Removing it must collapse the proposal to an ordinary factor base, fixed cover, generic divisor-class index calculus, or resultants control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — closest end-to-end relation/decomposition cost negative; orbit yield must improve its exponent after branch costs.
2. `ledger/H-FB-001.yaml` — closest factor-base hypothesis; deck-orbit atoms must be more than a structured relabeling.
3. `ledger/EV-FB-001.yaml` — closest evidence that simple base structure did not change yield or solving.
4. `ledger/H-REP-001.yaml` — closest representation-change negative; lifting to \(X\) alone is not mechanism-new.
5. `ledger/SYNTHESIS-20260716.md` — governing requirement for controls, target descent, full cost, and scoped conclusions.

## Closest primary literature

- Serge Lang, [Algebraic groups over finite fields](https://wstein.org/papers/bib/Lang-Algebraic_Groups_Over_Finite_Fields.pdf), gives the finite-field torsor/Lang-map structural boundary; existence or triviality does not provide a cheap scalar-compatible branch selector.
- Yan Bo Tian, [A cryptanalytic application of Weil descent](https://arxiv.org/abs/2012.07173), is the nearest concrete cover-transfer attack, for elliptic curves over cubic extensions and special cover geometry rather than generic prime-field fibers.
- Claus Diem, [On the discrete logarithm problem in elliptic curves](https://www.math.uni-leipzig.de/~diem/preprints/small-degree-exact.pdf), provides the plane-curve/factor-base index-calculus setting whose decomposition and linear-algebra costs remain relevant upstairs.
- Pierrick Gaudry, [Index calculus for abelian varieties and the elliptic curve discrete logarithm problem](https://doi.org/10.1016/j.jsc.2008.08.005), gives the general relation framework for divisor-class groups and covers.
- Victor Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline. No cited source establishes the required target-compatible deck-orbit branch compression on generic prime-field curves, so novelty is `novelty-unverified`.

## Complete factor-base-to-target-descent path

1. Freeze \((E,P,N)\), construct \(X\), \(\pi\), \(\Gamma\), and publish the degree/genus/ramification/field data plus a deterministic orbit-canonicalization rule.
2. Enumerate or sample \(B=N^{\beta+o(1)}\) canonical orbit atoms \(A_i\) on \(X\), compute their certified norms/pushforwards \(F_i\in\langle P\rangle\), and deduplicate trivial, ramified, or stabilizer-collapsed images.
3. For uniform \(a\), set \(R=[a]P\), solve the fiber \(\pi^{-1}(R)\) according to the preregistered branch policy, and seek a verified upstairs divisor/function relation between a selected fiber orbit and the \(A_i\).
4. Norm/push forward the certificate to obtain a nontrivial relation \(R+\sum_i e_iF_i=O\) (or a fully specified nonzero multiple thereof), and count every failed fiber, branch, cancellation, and dependent row.
5. Collect enough independent projected rows to solve \(\log_P(F_i)\), charging coefficient arithmetic and the measured sparse or dense linear-algebra backend.
6. After the base-log state is frozen, sample independent \(t\), solve fibers over \(Q+[t]P\), and run the identical orbit reducer and pushforward path with no target-specific branch learning.
7. Recover \(x\) from a verified projected target relation and accept only if \([x]P=Q\); preserve the upstairs and downstairs certificates together.

## Full rho/BSGS cost model

Let cover degree be \(d=N^{\alpha+o(1)}\), replacement-base size \(B=N^{\beta+o(1)}\), and cover/torsor construction (including equations, genus, deck action, and fields) cost \(N^{c+o(1)}\). Let one chosen-branch fiber solve plus upstairs reducer attempt cost \(N^{u+o(1)}\), and let explicit branch/orbit handling contribute \(N^{b+o(1)}\); exhaustive handling has \(b\ge\alpha\). Let relation and target reciprocal success densities be \(N^{\delta+o(1)}\) and \(N^{\delta_t+o(1)}\), pushforward/certificate verification cost \(N^{v+o(1)}\), base-atom construction per element cost \(N^{u_0+o(1)}\), and stored state use \(N^{s+o(1)}\) bits, including cover equations, fields, branches, and coefficients.

- Generic rho: \(T_{\rho}=N^{1/2+o(1)}\), \(M_{\rho}=N^{o(1)}\).
- BSGS: \(T_{\rm BSGS}=N^{1/2+o(1)}\), \(M_{\rm BSGS}=N^{1/2+o(1)}\).
- Cover and replacement-base preprocessing: \(T_{\rm pre}=N^{\max(c,\beta+u_0,\alpha)+o(1)}\); the \(\alpha\) term charges materializing degree-size equations/data when applicable.
- Relation collection: \(T_{\rm rel}=N^{\beta+b+u+\delta+o(1)}\).
- Linear algebra: \(T_{\rm LA}=N^{2\beta+o(1)}\), \(M_{\rm LA}=N^{\beta+o(1)}\) under a verified sparse Wiedemann model; projected dense rows instead incur \(N^{3\beta+o(1)}\).
- Target descent: \(T_{\rm desc}=N^{b+u+\delta_t+o(1)}\).
- Accepted-certificate verification contributes \(N^{\beta+v+o(1)}\), plus \(N^{v+o(1)}\) for final descent verification.

The optimistic sparse end-to-end exponent is
\[
 \lambda=\max\{c,\beta+u_0,\alpha,\beta+b+u+\delta,2\beta,\beta+v,b+u+\delta_t,v\},
\]
with \(2\beta\) replaced by \(3\beta\) for dense projected matrices. The memory exponent is
\[
 \mu=\max\{s,\beta,\alpha\ \text{if all branches/cover data are stored}\}.
\]
A fixed-degree cover has \(\alpha=b=0\) and can change only constants unless it provably changes \(\delta\), \(\delta_t\), or \(\beta\). A growing degree can change density but must pay \(\alpha\) and branch cost \(b\); neither is free preprocessing.

## Likely fatal obstruction

For fixed \(d\), a fiber supplies only a constant number of branches, so orbit compression normally gives at most a constant-factor yield change and cannot improve an exponent. For growing \(d=N^\alpha\), constructing, solving, or enumerating the fiber generally costs at least \(N^\alpha\), canceling the gain. A branch selector compatible with the hidden scalar may itself encode the ECDLP or be target-dependent. Lang's theorem can trivialize torsors as a structural existence statement over finite fields, but it does not supply the required cheap canonical branch or preserve a useful scalar relation. Finally, norm/pushforward may average the deck orbit to zero, a known multiple, or the same ordinary factor-base relation, while upstairs divisor elimination becomes a dense-resultant computation with rho-or-worse cost.

## Proof track

1. Construct \((X,\pi,\Gamma)\), prove the canonicalization rule is target-independent, and bound degree, genus, ramification, equation size, and fiber-solving complexity.
2. Prove that accepted upstairs relations push forward to nontrivial source-group relations and that orbit identification preserves enough independent rows.
3. Prove a relation and separate target-descent density advantage that survives all branch/stabilizer/cancellation costs and is unavailable to an equal-size source factor base.
4. Derive parameters \((\alpha,\beta,c,u_0,b,u,\delta,\delta_t,v,s)\) with measured applicable \(\lambda<1/2-\varepsilon\) and no hidden branch oracle or dense elimination.

## Disproof track

1. Exhaustively enumerate toy fibers, deck orbits, stabilizers, ramification, and pushforwards; classify every cancellation and duplicate projected row.
2. Compare canonical selection, exhaustive branch enumeration, random branch choice, and an explicitly oracle-labeled favorable branch to isolate the price of branch consistency.
3. Fit yield and cost against \(d\), \(B\), genus, and \(N\); falsify if fixed degree changes only constants or growing degree contributes \(b\ge\alpha\) that cancels the density gain.
4. Ablate the cover while retaining projected points \(F_i\); statistically equivalent relation/descent behavior identifies an ordinary factor-base or representation duplicate.

## Positive and negative controls

- Positive structural control: a tiny explicitly split cover with enumerated deck group and known fiber branches must round-trip through lift, orbit canonicalization, divisor verification, and pushforward.
- Positive instrumentation control: an oracle-labeled favorable branch validates the downstream reducer but is excluded from every promotion fit.
- Negative control: fixed-degree random covers and equal-size random source-curve bases must establish the constant-factor baseline.
- Negative control: permute deck labels, alter one ramification multiplicity, or replace a fiber point by a point over the wrong base coordinate; the verifier must reject.
- Cancellation control: relations whose deck-orbit norm/pushforward is zero or a tautological known multiple are recorded but never counted as usable rows.
- Leakage control: blind and permute targets; forbid post-hoc branch selection, target-trained covers, and explicit large tables of successful fibers.

## Quantitative promotion and falsification gates

Promotion requires zero false upstairs or pushforward certificates; at least 200 independent usable projected relations and 100 independent target descents on each of the three largest frozen toy sizes; projected rank at least \(0.95B\); branch-policy success reported over all attempts; a preregistered fit with point estimate \(\lambda\le0.45\) and 95% upper confidence bound below \(0.50\); measured \(\mu\le0.45\); and at least a 20% exponent-level, not merely constant-factor, improvement over cover-ablated and equal-size source-base controls. The state remains `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

Falsify or demote if any certificate is unsound; fixed degree yields only a constant factor; growing degree forces \(\alpha\ge0.50\) or \(b+u+\delta_t\ge0.50\); the selected branch requires \(x\), target-derived learning, or an explicit large table; more than 10% of accepted upstairs relations push forward trivially without the preregistered correction; projected rank falls below \(0.95B\); dense elimination/linear algebra reaches exponent \(0.50\); or the cover-ablation control is statistically equivalent within 10%.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-010/contract.yaml` — frozen cover families, degree/genus ladder, branch policy, orbit base, seeds, controls, and gates.
- `ideas/artifacts/ECDLP-IDEA-010/deck_orbit_preflight.sage` — fiber enumeration, deck action, canonicalization, upstairs relation, norm/pushforward, and verifier.
- `ideas/artifacts/ECDLP-IDEA-010/runs/<run_id>/manifest.json` — immutable code/environment/curve/cover/seed binding.
- `ideas/artifacts/ECDLP-IDEA-010/runs/<run_id>/fibers.jsonl` — every fiber, branch, orbit, stabilizer, relation, pushforward, cancellation, and rejection.
- `ideas/artifacts/ECDLP-IDEA-010/runs/<run_id>/costs.tsv` — construction, branch, density, rank, linear algebra, descent, verification, and peak memory.
- `ideas/artifacts/ECDLP-IDEA-010/analysis.md` — fixed-versus-growing-degree fits, controls, obstruction audit, and scoped decision.

## Interpretation boundary

A solvable fiber, canonical deck orbit, valid upstairs divisor, nontrivial pushforward relation, or recovered toy scalar is not a breakthrough. Fixed-degree branch multiplicity is presumed a constant-factor control, and growing degree must pay its construction and branch costs. Only an independently verified full relation-to-target-descent exponent below rho could justify escalation; all present claims are `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

## Exactly one next executable action

1. Draft and structurally validate the bounded split-cover versus random-cover fiber-enumeration contract at `ideas/artifacts/ECDLP-IDEA-010/contract.yaml`, fixing canonical, exhaustive, random, and oracle-labeled branch policies before execution.
