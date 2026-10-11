---
title: "Subgroup-preserving Jacobian transfers: advantage and public recoverability"
record_kind: literature_assessment
confidence: reported
added: "2026-09-30"
scientific_runs: 0
research_state_transition: false
knowledge_refs:
  - KN-LIT-7261
  - KN-LIT-b4a89c
  - KN-LIT-54c462
  - KN-LIT-171
---

# Subgroup-preserving Jacobian transfers

User goal: assess whether a subgroup-preserving Jacobian transfer offers a real computational advantage, and independently assess whether that advantage can remain hidden from the public curve.

This is a literature synthesis and goal intake, not an approved execution contract, canonical GOAL record, new internal finding, or validated trapdoor construction. Existing knowledge records are reused rather than duplicated. No benchmark, transfer implementation, independent review, or research-state promotion was performed.

## Current assessment

| Claim | Evidence status | Boundary |
| --- | --- | --- |
| Transfers can preserve a prime-order subgroup | Elementary group-theoretic criterion below | Requires an actual efficiently evaluable homomorphism |
| Some Jacobian transfers improve DLP complexity | Reported external result: KN-LIT-b4a89c | Certain curves over cubic extension fields |
| A practical binary-field descended computation exists | Reported external computation: KN-LIT-54c462 | GLS curve over F_(2^(5*31)); not ECC2K-130 |
| A useful transfer can remain hidden | Proposed architecture: KN-LIT-7261 | Not a general secrecy theorem |
| ECC2K-130 has such an advantage | Unestablished by the consulted evidence | No candidate transfer or measured total cost supplied |

## Subgroup preservation

For G = <P> of prime order r and a homomorphism phi from G into J_C(k), phi(P) != 0 implies phi restricted to G is injective. Then Q = [x]P implies phi(Q) = [x]phi(P), preserving the scalar logarithm modulo r.

A geometric correspondence must induce the required map on rational points and be evaluable with accounted cost. An abstract isogeny class, shared group-order factor, or sparse system alone is insufficient. For an isogeny, degree coprime to r is a sufficient kernel condition. Maps to higher-dimensional Jacobians require their own subgroup check.

## Computational advantage

A useful transfer must beat the strongest applicable public baseline in total time and memory. Account separately for construction, map evaluation, preprocessing, relation collection, linear algebra, individual logarithms, failures, and verification. Report both one-target and amortized costs; never amortize preprocessing without stating the number of targets.

Tian reports approximately O-tilde(q) complexity for some prime-order elliptic-curve groups over F_(q^3), transferred through Weil restriction to genus-3 Jacobians. Generic rho on a group of order approximately q^3 has square-root complexity approximately q^(3/2). This is an asymptotic comparison, not a matched hardware benchmark. Source: KN-LIT-b4a89c; https://arxiv.org/abs/2012.07173.

Chi-Dominguez, Rodriguez-Henriquez, and Smith report a prime-subgroup GLS/GHS computation over F_(2^(5*31)) in approximately 1,035 CPU-days using Magma. It is an executable literature example, not a measured speed ratio against this program's GPU rho. Source: KN-LIT-54c462; https://arxiv.org/abs/2106.09967. KN-LIT-867 is superseded and should not be used as the current entry.

## Independent assessment of secrecy

Distinguish hiding a particular map from hiding every useful alternative transfer. The public-only observer need not recover the original secret correspondence to erase the advantage.

Teske proposes a secret descent-friendly curve over F_(2^161), a genus-7/8 Jacobian DLP, and a public isogenous curve. This supports the architecture's published precedent, not an unconditional theorem that all useful paths are unrecoverable. Source: KN-LIT-7261; https://eprint.iacr.org/2003/058.

Jao-Miller-Venkatesan report GRH-conditional random reducibility among curves with nearly the same endomorphism rings. Inference: this constrains claims that merely moving within such a family produces an isolated easy curve. It neither reconstructs an arbitrary secret map nor excludes all trapdoors, and the endomorphism-ring restriction must travel with every citation. Source: KN-LIT-171; https://arxiv.org/abs/math/0411378.

Finite unsuccessful searches cannot certify secrecy. No outsider reconstruction timing or lower bound was obtained here.

## Applicability to ECC2K-130

The target field F_(2^131) has prime extension degree; its only proper subfield is F_2. The composite-degree and cubic-extension examples above do not directly transfer. This blocks their direct reuse, not every conceivable correspondence.

The challenge curve's Koblitz/Frobenius structure is public and cannot by itself count as secret auxiliary information. A mere field-basis change supplies neither a new subgroup transfer nor demonstrated easier decomposition.

Field degree alone does not identify a curve. Any later comparison must use the repository's exact curve UID and separate correspondence/factor-base identities. Koblitz analogues at n=31 can support preliminary checks; m=83 is the higher-fidelity checkpoint. Neither establishes a result at m=131.

## Evidence needed before stronger claims

- A defined source subgroup, destination Jacobian, rational map, and subgroup-preservation argument.
- A total-cost comparison against the strongest applicable public baseline, including preprocessing and failed work.
- An independent assessment of public recoverability, covering alternative useful transfers and stating its finite scope.
- Reproducible artifacts and separate independent review before promotion to an internal finding.

Compactness, sparsity, descent possibility, and failure to discover a map are not substitutes for these requirements.

## Provenance and limits

The four existing KN records were fetched and read on 2026-09-30 UTC. The primary abstract pages were retrieved in the preceding conversation; full-text proofs and reported computations were not independently reproduced in this session. External claims remain reported. This note makes no global impossibility or secrecy claim.

No formal goal was closed. The next reviewable work is source-level verification of the published scope and cost assumptions; an ECC2K-130 candidate remains an explicit missing input.
