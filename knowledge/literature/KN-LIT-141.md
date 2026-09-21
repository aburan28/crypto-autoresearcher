---
id: KN-LIT-141
type: literature
title: 'MQ Challenge: Hardness Evaluation of Solving Multivariate Quadratic Problems'
authors: [Yasuda Takanori, Dahan Xavier, Huang Yun-Ju, Takagi Tsuyoshi, Sakurai Kouichi]
year: 2015
venue: 'Cryptology ePrint Archive, Paper 2015/275'
identifiers:
  eprint: iacr:2015/275
  doi: null
  url: https://eprint.iacr.org/2015/275
tags: [mq, multivariate-quadratic, challenge, benchmark, records, calibration, parameter-selection, hardness-evaluation, post-quantum, verifiability, solving]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Constructs the **Fukuoka MQ Challenge**: a public set of multivariate quadratic
problem instances designed to be hard, intended both to guide parameter selection
for multivariate public-key cryptosystems and to stimulate research into MQ
solving. The paper investigates how hardness depends on the parameter set — number
of variables, polynomial degree, number of equations, base field size — in order
to construct instances that are genuinely difficult rather than accidentally easy.

## Key claims (as reported)
- The MQ problem underpins the security of candidate post-quantum cryptosystems.
- Hardness depends on several parameters jointly: most importantly the number of
  variables and the degree, but also the number of equations and the size of the
  base field.
- The relation among those parameters is investigated in order to construct hard
  instances, which are then published as a challenge.
- The challenge is intended to help determine appropriate parameters for
  multivariate public-key cryptosystems.

## Relevance to this program
The calibration anchor for the MQ solver family, completing the pattern the
corpus already applies to ECDLP (`KN-TECH-036`, public record computations) and
to lattices (`KN-TECH-049`, the SVP and LWE challenges). Before this entry the
program could compare its crossbred solver path only against its own
measurements.

The connection is direct and checkable: `KN-LIT-139` reports that Joux solved all
the Fukuoka **Type I** challenges, including 148 quadratic equations in 74
variables in under a day. That gives a publicly stated instance size and wall
clock against which the program's own solver cost model can be sanity-checked —
the same instrument `KN-TECH-049` describes, applied to the solver rather than to
the cryptosystem.

The paper's framing also reinforces a discipline the program states elsewhere:
hardness is a function of a **parameter tuple**, not of one variable. An MQ
instance count quoted without its field size and equation count is not a
difficulty statement, exactly as a lattice "dimension `d` record" is meaningless
without its challenge family.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2015/275, DBLP `journals/iacr/YasudaDHTS15`, a NIST post-quantum workshop paper
and presentation, an ACM Communications in Computer Algebra record, and the
challenge site `mqchallenge.org`); direct fetches returned HTTP 403 under this
session's egress policy. No DOI was confirmed.

NOT verified here: the challenge's instance types and their exact parameters, the
hardness analysis relating the parameters, the current state of the challenge
leaderboard, and whether the Type I instances referenced via `KN-LIT-139` remain
the relevant comparison a decade later. **The challenge's current state was not
retrieved and this entry is not maintained automatically** — the same caveat
`KN-TECH-049` records for the lattice challenge halls of fame.
