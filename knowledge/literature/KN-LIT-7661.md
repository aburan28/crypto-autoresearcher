---
id: KN-LIT-7661
type: literature
title: "Time vs Success Probability Tradeoff for SVP and BDD with Implications to LWE and SIS"
authors:
  - "Divesh Aggarwal"
  - "Haoxiang Jin"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1364"
identifiers:
  eprint: "iacr:2026/1364"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1364"
tags: [lattice, svp, bdd, lwe, sis, slide-reduction, worst-case-to-average-case, reduction-tightness, cost-model, concrete-security, complexity, conjecture]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A systematic characterization of the **time versus success-probability tradeoff** for
SVP and BDD, aimed at the known looseness of worst-case-to-average-case reductions.

The stated problem: classic GapSVP/BDD → LWE reductions are **notoriously lossy** —
even assuming *exponential* hardness of the worst-case lattice problems, they yield only
**subexponential** lower bounds on LWE. Aggarwal–Leong–Veliche (TCC'24) reframed
hardness in terms of the **maximum success probability achievable by any PPT
algorithm** and got nearly tight reductions, but only in the polynomial-time regime.

This work extends the question to **time-rich adversaries**. It presents new
**blockwise guessing algorithms** for SVP and BDD using small-dimension SVP and CVP
oracles, and — by exploiting consecutive-product properties of **Slide Reduction** —
obtains the tightest known lower bounds on success probability as a function of time.
The authors then **conjecture** that no algorithm beats this tradeoff.

## Key claims (as reported)
- New blockwise guessing algorithms for SVP and BDD from small-dimension oracles.
- Tightest known success-probability-versus-time lower bounds, via Slide Reduction's
  consecutive-product structure.
- **A conjecture** that the tradeoff is optimal — explicitly labelled as such. The
  implications for LWE and SIS concrete security are downstream of that conjecture, not
  of a theorem.

## Relevance to this program
Slots into an area the corpus already covers well: [[KN-TECH-040]] holds the
core-SVP costing and cost-model zoo, [[KN-TECH-041]] the basis profiles and BKZ
simulation, [[KN-TECH-021]] the worst-case-to-average-case reductions this paper is
about. **This entry adds a 2026 increment to `KN-TECH-021`'s subject, not a new area** —
a keyword audit on 2026-08-01 initially suggested a gap (`lattice cost model` matched 0
files) but that was an artifact of vocabulary, not of coverage.

Why this paper specifically:

- **Reduction looseness is the central honesty problem in lattice security claims**, and
  it is the exact analogue of what `AGENTS.md` rule 4 and `KN-TECH-035` enforce on the
  cost side: a proof that a problem is hard *asymptotically* under a lossy reduction is
  not a statement about a deployed parameter set. This paper makes the loss quantitative
  rather than folkloric.
- **The success-probability axis is usually dropped.** Cost claims in this program are
  required to state time, memory, and the model; success probability is a fourth axis
  that lattice estimates routinely fix at a convenient constant. A paper whose whole
  subject is the time-vs-probability frontier is a useful corrective.
- **The conclusion rests on a conjecture, and the paper says so.** That is the correct
  form for this kind of result, and it matches the target-result profile's requirement
  (`docs/target-result-profile.md`) that results be stated **conditionally on explicit
  numbered heuristics**. Worth citing as an example of the form, not only the content.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1364,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, two authors, report number, year 2026.

NOT verified here: the blockwise guessing algorithms; the lower bounds or their
tightness; the Slide Reduction consecutive-product argument; the attributions to
Aggarwal–Leong–Veliche (TCC'24); and every downstream LWE/SIS implication, all of which
are **conditional on the paper's own optimality conjecture**. No concrete parameter set
is assessed here, and **no lattice-scheme security level in this program's ledger
changes**.
