# ECDLP-IDEA-008 — Partial pairing-return cycle

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; even a correct pairing value or one returned power is only an auxiliary-input observation, and a full self-bilinear map would cross a known hardness boundary rather than constitute an unexplained speedup.

## Falsifiable hypothesis

For a prime-order subgroup \(G=\langle P\rangle\) of order \(N\), an explicit auxiliary pairing environment supplies two scalar-compatible lifts and a **partial, efficiently recognizable return map** from a pairing target back to \(G\). On a cycle-level subset of reciprocal density \(N^{\Delta+o(1)}\), it realizes
\[
  \mathcal R([a]P,[b]P)=[ab]P
\]
with a complete pairing-and-return certificate, without computing \(a\), \(b\), or a target-group discrete logarithm. Iterating \(O(\log N)\) certified returns on \(Q=[x]P\) produces \([x^D]P\) for a public divisor \(D\mid N-1\), \(D=N^{\alpha+o(1)}\), after which Cheon-style auxiliary-input tables recover \(x\) in total exponent below \(1/2\). The density \(\Delta\) is defined for the **whole successful cycle**, so multiplying hidden per-stage probabilities cannot be omitted. This hypothesis is `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

## Mechanism-new operation

The proposed operation is not merely a pairing, an isogeny, or the abstract partial scalar-power correspondence already represented by `ECDLP-IDEA-003`. It is a concrete outward-and-back cycle:
\[
 G\times G\xrightarrow{\text{scalar-compatible lifts and bilinear pairing}}G_T
 \xrightarrow{\text{partial certified return}}G.
\]
Its essential novelty test is whether the partial return map can be recognized and evaluated on enough pairing outputs without solving a DLP or becoming a full self-bilinear map. Solver substitutions, parameter changes, a table of successful returns, post-hoc selection, or a relation-only pairing certificate are duplicates/controls.

## Assumptions

1. \(G\subset E(\mathbb F_p)\) has public prime order \(N\asymp p\), and the auxiliary torsion, extension degree, cofactors, pairing, and scalar-compatible lifts are constructed from public target-independent data.
2. The two lifts land in pairing-nondegenerate directions and preserve the same hidden scalars; distortion-like data, if used, is fully constructed and charged.
3. The partial return algorithm has a public membership/acceptance test and outputs a certificate proving the returned point has the pairing-product scalar; no target-field DLP, source-group DLP, or oracle branch label is used.
4. \(D\mid N-1\), \(D=N^{\alpha+o(1)}\), and every squaring/multiplication needed to reach \([x^D]P\) is counted in the cycle-level time and reciprocal-density exponents.
5. Pairing extension-field arithmetic, auxiliary-variety construction, calibration samples, failed return attempts, Cheon table generation, sorting/collisions, verification, and memory are charged.
6. Any precomputation is independent of \(Q\); a precomputed explicit table of \(N^{1-o(1)}\) pairing values or returns is disallowed.
7. Results on supersingular or oracle-instrumented positive controls remain `toy` and cannot be extrapolated to ordinary prime-field curves.

## Semantic fingerprint

`prime-field ECDLP -> two scalar-compatible pairing lifts -> bilinear target value encoding scalar product -> recognizable partial return to source subgroup -> certified scalar-power cycle -> Cheon auxiliary-input recovery`

The indispensable operation is the **non-DLP partial return**. If the implementation instead assumes \([x^D]P\), uses an injected return table, evaluates only the pairing, or implements a generic partial scalar-power black box, it is a control or duplicate rather than this idea.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — total-cost baseline requiring the whole acquisition and recovery path to beat rho.
2. `ledger/H-ISO-001.yaml` — closest auxiliary-map/isogeny hypothesis; same-field neighbor maps cannot supply the missing multiplicative scalar operation by themselves.
3. `ledger/EV-ISO-001.yaml` — measured evidence that small isogenies did not alter relation yield or degree regularity.
4. `ledger/H-REP-001.yaml` — closest representation-change negative; moving into a pairing target is insufficient without the certified return.
5. `ledger/SYNTHESIS-20260716.md` — governing boundary against promoting correctness, isolated relations, or uncharged preprocessing.

## Closest primary literature

- Jung Hee Cheon and Dong Hoon Lee, [A Note on Self-Bilinear Maps](https://eprint.iacr.org/2002/117), show that a bilinear map together with an injective homomorphism back to the source makes Diffie–Hellman easy and rule out a full self-bilinear map under standard hardness assumptions. This is the principal obstruction, not supporting evidence.
- Dan Boneh and Alice Silverberg, [Applications of Multilinear Forms to Cryptography](https://eprint.iacr.org/2002/080.pdf), analyze the severe geometric barriers to the higher multilinearity that an iterated cycle would resemble.
- Alfred Menezes, Tatsuaki Okamoto, and Scott Vanstone, [Reducing elliptic curve logarithms to logarithms in a finite field](https://doi.org/10.1109/18.259647), is the primary pairing-transfer boundary; any favorable embedding-degree finite-field attack must be charged as MOV rather than credited to this mechanism.
- Jung Hee Cheon, [Security Analysis of the Strong Diffie-Hellman Problem](https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf), gives the auxiliary-input recovery tradeoff once \([x^D]P\) is actually available; it does not construct that input.
- Victor Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison. No cited primary work establishes a useful partial pairing return on ordinary prime-field curves, so novelty is `novelty-unverified`.

## Complete factor-base-to-target-descent path

1. Freeze \((E,P,N)\), a public auxiliary pairing environment, two scalar-compatible lifts, a return-domain predicate, and a divisor \(D\mid N-1\) with \(D=N^{\alpha+o(1)}\).
2. Construct and validate the pairing, lift nondegeneracy, return predicate, and return certificates on target-independent calibration inputs; publish every failed branch and all extension-field costs.
3. Starting from \(Q=[x]P\), use a fixed addition/squaring circuit for exponent \(D\). At each gate, form the prescribed pairing target, attempt the partial return, and accept only a certificate that verifies the source point encodes the product scalar.
4. Restart or use only a preregistered public randomization strategy when a gate is outside the return domain; measure the reciprocal probability and cost of completing the entire circuit as \(N^{\Delta+o(1)}\), not one gate in isolation.
5. On success obtain a verified auxiliary point \(Q_D=[x^D]P\). Build the two Cheon replacement tables for the \(D\)-part and the \((N-1)/D\)-part; these tables replace an ordinary factor base and require no relation matrix.
6. Match the Cheon table entries to recover candidates for \(x\), remove any subgroup or root ambiguity exactly as specified by the algorithm, and accept only the candidate satisfying \([x]P=Q\).
7. Report acquisition, calibration, tables, ambiguity resolution, verification, and memory separately; a pairing relation or \(Q_D\) alone is not target descent.

## Full rho/BSGS cost model

Let auxiliary construction have exponent \(c\), a complete fixed return-circuit attempt (all pairings, lifts, predicates, certificates, and \(O(\log N)\) gates) cost \(N^{r+o(1)}\), and its success probability be \(N^{-\Delta+o(1)}\). Let calibration use \(N^{\gamma+o(1)}\) samples at per-sample exponent \(r_0\); if calibration solves a matrix of dimension \(N^\gamma\), charge \(N^{\omega_{\rm cal}\gamma+o(1)}\), otherwise its linear-algebra exponent is explicitly zero. Let return state use \(N^{s+o(1)}\) bits, including extension-field coordinates and certificate encodings.

- Generic rho: \(T_{\rho}=N^{1/2+o(1)}\), \(M_{\rho}=N^{o(1)}\).
- BSGS: \(T_{\rm BSGS}=N^{1/2+o(1)}\), \(M_{\rm BSGS}=N^{1/2+o(1)}\).
- Pairing/lift/return setup: \(T_{\rm pre}=N^{c+o(1)}\).
- Calibration: \(T_{\rm cal}=N^{\max(\gamma+r_0,\omega_{\rm cal}\gamma)+o(1)}\), with \(\omega_{\rm cal}\gamma=0\) when no calibration matrix exists.
- Successful scalar-power acquisition: \(T_{\rm acquire}=N^{r+\Delta+o(1)}\).
- Cheon replacement-table recovery for \(D=N^\alpha\): \(T_{\rm Cheon}=N^{\max(\alpha/2,(1-\alpha)/2)+o(1)}\) and the same exponent bounds its table memory in the straightforward model.
- Relation collection and relation linear algebra are absent: \(T_{\rm rel}=T_{\rm LA}=N^{0+o(1)}\); this zero must not hide calibration algebra or the Cheon table collision/sort work.
- Final ambiguity resolution and scalar verification have exponent \(v\), ordinarily \(v=0\), but measured extension-field conversion costs are charged if larger.

The end-to-end time and memory exponents are
\[
 \lambda=\max\{c,\gamma+r_0,\omega_{\rm cal}\gamma,r+\Delta,\alpha/2,(1-\alpha)/2,v\},
\]
\[
 \mu=\max\{s,\gamma,\alpha/2,(1-\alpha)/2\}.
\]
The apparent optimum \(\alpha=1/2\) gives a Cheon term \(1/4\), but it is irrelevant unless the pairing-return acquisition terms are also below \(1/2\). Any extension-field DLP route is costed separately as MOV and cannot be attributed to this cycle.

## Likely fatal obstruction

A total efficient return would be a self-bilinear map, precisely the setting Cheon–Lee identify as collapsing Diffie–Hellman; Boneh–Silverberg give further reasons geometric multilinearity is unavailable. Ordinary prime-field curves generally lack a distortion map taking the rational \(N\)-torsion line to an independent pairing direction. A partial return predicate may simply recognize a subset whose branch labels encode a target-group DLP, and repeated use may multiply sparse per-gate probabilities until \(\Delta\ge1/2\). If it succeeds on a pairing-friendly curve with small embedding degree, MOV may already be the actual attack. Thus the most likely outcome is impossibility, DLP-equivalence, or a density/setup cost restoring rho.

## Proof track

1. Construct the two scalar-compatible lifts and prove pairing nondegeneracy without secret endomorphism data or a favorable MOV shortcut.
2. Define a public partial return domain and prove correctness, soundness, and non-DLP evaluation of its certified return map.
3. Prove a lower bound on the whole-circuit success density after every iterative gate and randomization, not merely on isolated returns.
4. Combine that density with Cheon's exact divisor/ambiguity conditions to exhibit measured parameters with \(\lambda<1/2-\varepsilon\) and no full self-bilinear extension.

## Disproof track

1. Test whether return-domain membership or branch recovery is computationally equivalent to a target-field/source-group discrete logarithm on exhaustive toy instances.
2. Measure isolated-gate and full-cycle densities versus circuit depth; falsify if the full-cycle exponent grows to \(1/2\) or if successes come only from injected return data.
3. Attempt to extend the partial map algebraically; either an extension contradicts the assumed hardness boundary or failure localizes the density/branch obstruction.
4. Compare against direct MOV, rho, BSGS, and assumed-auxiliary-input Cheon controls with every setup and memory term included.

## Positive and negative controls

- Positive control: a tiny supersingular pairing example with an explicit, fully labeled oracle return; it validates circuit and certificate plumbing only and is barred from promotion.
- Positive control: inject a correct \([x^D]P\) directly into Cheon recovery to verify divisor conditions, table matching, ambiguity handling, and final scalar checking.
- Negative control: an ordinary prime-field curve with no known distortion map must not silently synthesize a second pairing direction or accept degenerate pairing values.
- Negative control: shuffle pairing outputs, alter one return certificate, or replace a returned point by a random source point; all must be rejected.
- Boundary control: compare direct MOV cost on the same pairing environment and label any smaller-extension-field DLP as the actual mechanism.
- Leakage control: permute/blind targets and forbid post-hoc return-domain selection, precomputed successful-output tables, and target-dependent auxiliary construction.

## Quantitative promotion and falsification gates

Promotion requires zero false return certificates; nondegenerate pairing checks on every accepted gate; at least 100 independent successful full cycles on each of the three largest frozen toy sizes; a 95% upper confidence bound \(r+\Delta\le0.45\); a public \(D\) with \(0.4\le\alpha\le0.6\); measured \(\lambda\le0.45\) with a 95% upper confidence bound below \(0.50\); measured \(\mu\le0.45\); and direct MOV, rho, and BSGS controls no faster under the same accounting. The outcome remains `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

Falsify or demote if any certificate is unsound; no independent pairing direction exists; the return uses either source/target DLP or target-derived advice; whole-cycle \(r+\Delta\ge0.50\); the useful domain is only an explicit large table; setup/calibration reaches exponent \(0.50\); direct MOV explains the speed; or the operation extends to a full self-bilinear map under assumptions that are supposed to preserve DH hardness.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-008/contract.yaml` — frozen curve families, auxiliary environment, return predicate, divisor \(D\), circuit, seeds, and gates.
- `ideas/artifacts/ECDLP-IDEA-008/partial_return_preflight.sage` — pairing/lift construction, oracle-labeled control, partial-return interface, and certificate verifier.
- `ideas/artifacts/ECDLP-IDEA-008/cheon_recovery.py` — standalone auxiliary-input recovery with table and ambiguity accounting.
- `ideas/artifacts/ECDLP-IDEA-008/runs/<run_id>/cycle_attempts.jsonl` — all gate outcomes, restarts, pairing values, certificate hashes, and rejection reasons.
- `ideas/artifacts/ECDLP-IDEA-008/runs/<run_id>/costs.tsv` — setup, calibration, full-cycle density, Cheon time, verification, and peak memory.
- `ideas/artifacts/ECDLP-IDEA-008/analysis.md` — Cheon–Lee/Boneh–Silverberg boundary audit, fitted exponents, controls, and scoped decision.

## Interpretation boundary

A valid pairing, a certified return on one toy input, a returned \([x^2]P\), an injected \([x^D]P\), or a correct Cheon recovery is not a breakthrough. A full return would implicate a known hardness collapse, while a partial return must beat its own whole-cycle density and construction costs. No claim may exceed `toy`, `heuristic`, `model-bound`, and `novelty-unverified` without independent end-to-end evidence.

## Exactly one next executable action

1. Draft and structurally validate the bounded ordinary-versus-oracle partial-return contract at `ideas/artifacts/ECDLP-IDEA-008/contract.yaml`, including full-cycle rather than per-gate density and direct MOV controls; do not execute it yet.
