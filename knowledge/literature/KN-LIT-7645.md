---
id: KN-LIT-7645
type: literature
title: "Computing class groups and gonalities of algebraic curves over finite fields"
authors:
  - "Maarten Derickx"
  - "Kenji Terao"
year: 2026
venue: "arXiv preprint arXiv:2602.17417 [math.NT, math.AG]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2602.17417"
  url: "https://arxiv.org/abs/2602.17417"
tags: [class-group, jacobian, function-field, finite-field, hyperelliptic, riemann-roch, gonality, index-calculus, dlp, number-theory, implementation, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Practical algorithms for computing the **divisor class group** and the **gonality** of
a curve over a finite field, reported to achieve **several orders of magnitude speedup**
over existing methods for sufficiently large genus or residue field.

The stated mechanism is a **precomputation step using power-series expansions**, which
makes computing large numbers of **Riemann–Roch spaces** efficient in an amortized
sense.

## Key claims (as reported)
- Practical divisor-class-group and gonality algorithms for curves over `F_q`.
- "Several orders of magnitude" speedup over existing methods — **conditioned on
  sufficiently large genus or residue field**. The abstract gives no threshold, no
  timings, no baseline system, and no asymptotic statement.
- The gain is **amortized**: the claim is about computing *many* Riemann–Roch spaces,
  not one.

## Relevance to this program
The divisor class group of a curve over `F_q` is its **Jacobian**, and the DLP in that
group is the higher-genus generalization of the ECDLP the program tracks under
`jacobian`/`hyperelliptic`. Class-group computation for function fields is also the
native habitat of **index calculus on curves**: the standard subexponential attacks in
genus `g ≥ 3` are class-group computations with a factor base of small-degree places,
and Riemann–Roch space computation is a real inner-loop cost there.

So this is a **cost-model input to curve index calculus**, in the same category as
[[KN-LIT-7642]] for the isogeny side: an engineering speedup in a routine the attacks
already call. What it is **not**:

- Not an asymptotic improvement. The abstract claims practical speedup at large
  parameters, not a better exponent, and this entry must not be cited as moving one.
- Not a break. The paper is stated as computational number theory, and neither
  cryptography nor a DLP attack is mentioned in the abstract. The bearing on index
  calculus is **this program's inference**, not the authors' claim, and is flagged as
  such.
- **Does not bear on the prime-field ECDLP.** Genus-1 curves over prime fields have no
  subexponential class-group route; that is the whole point of the ECDLP's standing.

Gonality is recorded because it is the invariant governing which curves admit low-degree
maps to `P^1` — the structural quantity behind Weil-descent and cover-attack
feasibility (`weil-descent` thread) — but no descent consequence is claimed here.

## Not verified here
Full paper not read. Claims relayed from the arXiv API abstract for 2602.17417,
retrieved 2026-08-01 (hence `confidence: reported`). arXiv metadata: submitted
2026-02-19, categories math.NT and math.AG, two authors. Preprint — not peer-reviewed,
no DOI or venue as of this entry.

NOT verified here: the algorithms; the "several orders of magnitude" figure or the
genus/field-size regime it holds in; the amortization argument; whether an
implementation is public; and every part of the index-calculus connection drawn above,
which is inference from the subject matter and appears nowhere in the source.
