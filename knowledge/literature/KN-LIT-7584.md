---
id: KN-LIT-7584
type: literature
title: Efficient Ternary Computation of Optimal Ate Pairing on BLS27 Curves
authors:
  - "Walid Haddaji"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1522'
identifiers:
  eprint: iacr:2026/1522
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1522
tags: [pairing, elliptic-curve, bls-curves, embedding-degree, number-field-sieve, extnfs, finite-field-dlp, parameter-selection, implementation, cost-model]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Gives a ternary variant of the Miller loop for optimal Ate pairings on BLS curves with
embedding degree `k = 27`, exploiting the degree-3 extension tower of `F_{p^27}` that
binary approaches leave unused, and generates two new parameter seeds chosen against
exTNFS and SexTNFS security levels.

## Key claims (as reported)
- Restricting the seed representation to sparse ternary digits streamlines point
  operations and eliminates costly inversions in the Miller loop.
- Two new seeds are generated, one tailored to exTNFS and one to SexTNFS security levels;
  their sparse ternary representations are claimed to serve the Miller loop and to permit
  full exploitation of cyclotomic cubing in `F_{p^27}` during the hard part of the final
  exponentiation.
- The exTNFS seed yields a **22% improvement** in overall optimal Ate pairing cost versus
  the state-of-the-art binary approach of Fouotsa et al. (2020).
- The proposed SexTNFS seed is claimed to ensure a higher security level against the most
  advanced NFS variants.
- Framing: `k = 27` is motivated as relevant for the 256-bit security level *specifically
  because of* recent advances in NFS and its variants (exTNFS, SexTNFS).

## Relevance to this program
Recorded for the parameter-selection story, not the implementation result. The
implementation content — ternary Miller loops, cyclotomic cubing — is outside the
program's scope and no ECDLP conclusion depends on it.

What is in scope is the *mechanism* the abstract takes for granted: pairing-friendly
curve parameters are chosen as a function of the best known attack on the discrete
logarithm in the embedding field `F_{p^k}`, and every improvement to NFS/exTNFS/SexTNFS
propagates directly into larger required `p` or different `k`. This is a live, worked
example of an exponent-level result in a *finite-field* DLP algorithm forcing concrete
parameter migration — the outcome that the program's target result profile
(`docs/target-result-profile.md`) describes for the elliptic-curve case, observed here in
the one setting where index calculus actually works.

The instructive contrast is the one the corpus exists to hold steady: index calculus
gives subexponential DLP in `F_{p^k}` and is why pairing parameters keep moving, while the
elliptic-curve group over a prime field has resisted every point-decomposition approach
(`KN-TECH-002`, `KN-TECH-003`, `KN-OPEN-001`). The two live side by side in the same
protocol. Nothing in this paper suggests any transfer from the former to the latter, and
this entry should not be read as evidence of one.

**Does not bear on the ECDLP.** No result here touches the elliptic-curve discrete
logarithm; the NFS variants referenced attack the finite-field DLP in the embedding field.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-07-24, approved 2026-07-27. Not peer-reviewed or formally published as of this entry;
no DOI on the ePrint page. Category: PUBLICKEY.

NOT verified here: the 22% figure, its cost metric (field multiplications, cycles, or
otherwise), and the platform and parameters behind it; the attribution and content of the
Fouotsa et al. (2020) baseline; the two new seeds and the security estimates assigned to
them; the claim that the SexTNFS seed "ensures a higher level of security", which is a
parameter-selection claim resting on an unstated NFS cost estimate and is **not** verified
here; and whether the claimed 256-bit security level survives current exTNFS/SexTNFS
estimates. **No pairing parameter set should be selected or re-costed on the basis of this
entry.** The abstract as rendered on the ePrint listing contains an unexpanded LaTeX macro
(`\Fpk{27}`), read here as `F_{p^27}`.
