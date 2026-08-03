---
id: KN-LIT-7650
type: literature
title: "Module Lattice Security (Part I): Unconditional Verification of Weber's Conjecture for k <= 12"
authors:
  - "Ming-Xing Luo"
year: 2026
venue: "arXiv preprint arXiv:2604.15858 [cs.CR, quant-ph]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2604.15858"
  url: "https://arxiv.org/abs/2604.15858"
tags: [principal-ideal-problem, cyclotomic, class-group, class-number, ideal-lattice, lattice, iwasawa, grh, number-theory, pqc, extraordinary-claim]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Reports the **first unconditional verification of Weber's conjecture (1886) for
`k ≤ 12`** — i.e. that the class number of the real cyclotomic field of conductor
`2^{k+1}` is `1` — where existing verifications for `k ≥ 9` were **conditional on GRH**.
The stated method combines the **Fukuda–Komatsu computational sieve**, the inductive
structure of the **cyclotomic `Z_2`-tower**, and **Herbrand's theorem**.

The framing given is cryptographic: Weber's conjecture is said to govern the
solvability of the **Principal Ideal Problem**, the **freeness of modules over rings of
integers**, and the tightness of **worst-case-to-average-case reductions** in Ring-LWE
and Module-LWE.

## Key claims (as reported)
- Unconditional (GRH-free) verification of Weber's conjecture for `k ≤ 12`.
- Method: Fukuda–Komatsu sieve + `Z_2`-tower induction + Herbrand's theorem.
- The stated bearing on PIP solvability, module freeness, and RLWE/MLWE reduction
  tightness is the **author's framing**, relayed here, not an independently checked
  implication.

## Relevance to this program
Two distinct reasons, and the second is a caution that should travel with any citation
of this entry.

**1. The mathematics is squarely in the program's blind spot.** Class numbers of real
cyclotomic fields, `Z_p`-towers, and Herbrand's theorem are the Iwasawa-theoretic
machinery underneath every "the class group is trivial, so ideals are principal, so
PIP is easy" argument in ideal-lattice cryptography. The corpus is thin on the
*unconditional-vs-GRH* distinction, which is exactly the kind of hidden assumption the
red-team role exists to surface: a security argument that silently inherits GRH is
conditional whether or not it says so. See [[KN-LIT-7649]] and [[KN-TECH-081]] for the
PIP thread this feeds.

**2. Provenance caution — this is Part I of a series whose Part IV makes an
extraordinary claim.** [[KN-LIT-1743]] is Part IV by the same single author, and it
claims a **probabilistic polynomial-time quantum attack breaking ML-KEM, Falcon, HAWK,
NTRU-HPS and NTRU-HRSS at all standardized parameter sets**. As of this entry, **no
corroboration of that claim from any independent source appears in this corpus**, and
none was sought or found during the 2026-08-01 sweep. A claim of that magnitude with no
third-party confirmation is a lead, not a fact.

The consequence for how this entry is used: **Part I's number-theoretic content and
Part IV's cryptanalytic conclusion must be cited separately and never transitively.**
A verification of Weber's conjecture for `k ≤ 12` is a checkable, bounded, plausible
computational result; it does not lend credibility to the series' downstream break
claims, and this entry does not extend any to them. If the PIP thread ever becomes
load-bearing for a program conclusion, both papers require an independent read before
either is relied on.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the arXiv API abstract for 2604.15858,
retrieved 2026-08-01 (hence `confidence: reported`). arXiv metadata: submitted
2026-04-17, categories cs.CR and quant-ph, single author, v2. Preprint — not
peer-reviewed, no DOI or venue as of this entry.

NOT verified here: the verification of Weber's conjecture for `k ≤ 12`; its
unconditionality; the prior state of the art (that `k ≥ 9` required GRH); the method;
and every stated cryptographic implication. **The Part IV break claim referenced above
is neither endorsed nor refuted here** — it is recorded as uncorroborated within this
corpus, which is a statement about this corpus, not about the paper.
