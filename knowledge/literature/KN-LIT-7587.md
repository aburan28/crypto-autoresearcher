---
id: KN-LIT-7587
type: literature
title: The Polynomial-Time Low-Degree Conjecture is False
authors:
  - "Songtao Mao"
year: 2026
venue: 'arXiv preprint arXiv:2607.20318 [cs.CC]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.20318'
  url: https://arxiv.org/abs/2607.20318
tags: [complexity, lower-bound, low-degree-method, average-case-hardness, hardness-evidence, counterexample, barrier, methodology, reed-muller, distinguisher]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Disproves the polynomial-time low-degree conjecture in its standard binary formulation, by
constructing a family of permutation-invariant planted distributions that are exactly
low-degree-indistinguishable from `G(n, 1/2)` up to degree `D_n = Θ((log n)^{r-1})`, yet
are strongly distinguished in polynomial time by a deterministic rank test after
independent noise.

## Key claims (as reported)
- For every fixed integer `r >= 3`: a permutation-invariant distribution `P_n` on simple
  graphs with null `Q_n = G(n, 1/2)`, such that **every** marginal of `P_n` on at most
  `D_n = Θ((log n)^{r-1})` edges is uniform — so the low-degree advantage is *zero*
  through degree `D_n`.
- Nevertheless, after every edge is independently resampled at a fixed positive rate, a
  deterministic **rank test** strongly distinguishes the result from `Q_n` in polynomial
  time.
- Construction: a subspace of a Reed–Muller code whose nonzero polynomials have small
  absolute bias; points whose evaluation vectors have no short linear dependencies; a
  random alternating bilinear form evaluated on pairs of those vectors.
- Consequence as stated: low-degree indistinguishability, a uniform null, permutation
  invariance, and independent resampling **do not together imply polynomial-time
  hardness**; a valid general conjecture must add a further condition.
- Prior work produced counterexamples to *variants* of the conjecture or to versions for
  higher time complexity; the standard binary polynomial-time formulation had remained
  open.

## Relevance to this program
This does not touch the ECDLP. It is recorded because it is a **failure of a
hardness-evidence methodology**, and this program runs on hardness-evidence methodologies.

The low-degree method is one of the standard instruments for arguing that a problem is
hard when no unconditional lower bound is available: one shows that low-degree
polynomials cannot distinguish planted from null, and treats that as evidence no efficient
algorithm can. This paper exhibits a case where the evidence is maximally strong — the
low-degree advantage is *exactly zero* through the relevant degree, not merely bounded —
and the conclusion is nonetheless false, with the distinguisher being a rank test, an
object that is polynomial-time but simply not a low-degree polynomial.

The transferable lesson is about the shape of the error, and it applies directly to how
this program should report its own barriers. The program's central negative results are of
the form "technique family X, measured by indicator Y, does not beat `sqrt(p)`" — for
instance Gröbner solving degree as the indicator for summation-polynomial systems
(`KN-TECH-004`, `KN-TECH-011`, `KN-OPEN-002`). Every such statement is a claim about the
indicator, and this paper is a clean, recent demonstration that a well-motivated indicator
with a rich supporting literature can be *decisively* wrong about the thing it proxies
for. It argues for exactly the scoping `AGENTS.md` rule 4 already requires: a barrier is
scoped to the technique family and the measurement, and never promoted to a statement
that no efficient algorithm exists.

Note also the mechanism: the counterexample's distinguisher is an *algebraic-rank* test.
The failure is not that the planted structure was subtle but that it lived in a place the
low-degree lens is blind to by construction. Barriers stated relative to a measurement can
be evaded by algorithms that do not factor through that measurement, which is a general
caution and not a specific prediction about the ECDLP.

No existing entry is superseded. This is new methodological context, not a correction to
any recorded result.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-27 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-22, primary category cs.CC (cross-listed cs.DS), 17 pages per the author comment.
Preprint — not peer-reviewed, no DOI or venue as of this entry.

NOT verified here: the construction and its correctness; the claim that every marginal on
`<= D_n` edges is uniform; the rank test and its polynomial-time analysis; the precise
statement of the "standard binary polynomial-time formulation" being disproved and whether
the community accepts that formulation as *the* low-degree conjecture; the characterisation
of prior counterexamples as addressing only variants; and whether the result has been
independently confirmed. **A single-author preprint disproving a widely-used conjecture
one week after posting carries real risk of being withdrawn or corrected — this entry
should be re-checked before it is relied on.** The application to this program's barrier
reporting is this program's own reading; the paper makes no claim about the ECDLP.
