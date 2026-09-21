---
id: KN-LIT-7583
type: literature
title: An analysis of a weakened version of PRISM
authors:
  - "Jolijn Cottaar"
  - "Steven D. Galbraith"
  - "Luciano Maino"
  - "Monika Trimoska"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/906 (revision of 2026-07-27)'
identifiers:
  eprint: iacr:2026/906
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/906
tags: [isogeny, supersingular, endomorphism-ring, signature, cryptanalysis, primality-testing, miller-rabin, qrom, assumption-failure, parameter-selection, post-quantum]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Investigates how the choice of **primality test** affects the security of PRISM (PKC25), a
hash-and-sign signature whose security rests on the hardness of computing
large-prime-degree isogenies from a curve of unknown endomorphism ring. PRISM obtains the
isogeny degree by hashing messages onto large odd integers that pass a primality test —
so the test is load-bearing, and a probabilistic test admits composite degrees.

## Key claims (as reported)
- When a **weak primality test** is used, the assumption underlying PRISM's standard-model
  security proof **does not hold**.
- Extending the analysis to the assumption used in the (quantum) random oracle model, the
  authors argue that the **Miller–Rabin test suffices** in that setting.
- They estimate the **minimal number of Miller–Rabin iterations** required for PRISM to
  reach its target security level, framed as minimising signing cost.

## Relevance to this program
This is the more instructive half of the PRISM pair (`KN-LIT-7582` is the scheme). Its
value to this program is almost entirely methodological, and it is worth stating plainly
because the failure mode it exhibits is one the program is itself exposed to.

The security assumption was stated over *prime*-degree isogenies. The implementation
supplies degrees via a probabilistic primality test. The gap between "prime" and "passes a
probabilistic primality test" is small in probability and total in logic: the standard-
model assumption is simply false for the object the scheme actually constructs. The attack
surface is not in the isogeny mathematics at all — it is in the mismatch between the
idealised object a theorem quantifies over and the concrete object a program produces.

That is the same class of error the program's own rules target: `AGENTS.md` requires every
conclusion to be scoped to the tested curves, parameters, solver, and budget, and
`docs/claims-and-verification.md` requires a solve/relation claim to carry a certificate
that the run wrapper re-verifies independently. The reason for independent re-verification
is exactly this — that "the solver reported a relation" and "a relation exists" are
different propositions, and the gap between them is where results go wrong. PRISM's
primality test is the outside-world instance of the same distinction.

Also notable: the standard-model assumption breaks while the QROM assumption survives with
Miller–Rabin. A security argument's *model* determines which implementation shortcuts are
fatal, so "which model is this proved in" is a load-bearing question, not bookkeeping.

- `KN-TECH-028` (endomorphism rings, Deuring, KLPT, SQIsign) is the technique entry in
  scope. Nothing there is superseded.
- `KN-OPEN-013` is the open problem the assumption belongs to. Unmoved: this is an attack
  on a scheme's instantiation, not on the isogeny problem.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-05-08, revised 2026-07-27. **This paper entered the gather window by revision, not by
first release.** Not peer-reviewed or formally published as of this entry; no DOI on the
ePrint page. Category: ATTACKS.

NOT verified here: what "weak primality test" means precisely and whether any deployed
PRISM instantiation used one; the argument that the standard-model assumption fails (its
strength — whether a concrete forgery or an assumption-level obstruction — is not stated
in the abstract); the QROM argument that Miller–Rabin suffices; the iteration-count
estimate and the security level it targets; and whether the PRISM authors' 2026-07-27
revision (`KN-LIT-7582`) addresses this analysis. **The methodological reading above is
this program's own, not a claim made by the paper.**
