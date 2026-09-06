---
id: KN-OPEN-02200b
type: open_problem
title: >-
  Is H-TOP true at m >= 5 - is the top form of the digit-substituted summation
  polynomial S_{m+1} the single monomial prod_k x_k^{2^{m-1}} with coefficient
  exactly 1, free of the curve parameters and the target?
tags: [semaev, summation-polynomial, top-form, leading-coefficient, resultant, digit-presentation, generator-degree, symbolic-obligation, open, ecdlp]
confidence: established
status: open
source_refs: [EV-PFDR-1394a4, DEC-20260904-1e27a2, H-PFDR-4148b8, EXP-PFDR-5726af, KN-FIND-0618ab]
added: 2026-09-04
superseded_by: null
---

## Statement

**H-TOP.** For the base-2 digit presentation, the top-degree part of the
summation polynomial `S_{m+1}(x_1, …, x_m, x_R)` in the `m` unknowns is the
single monomial `prod_k x_k^{2^(m-1)}` with coefficient an integer constant
(namely 1), independent of the curve parameters `(a, b)` and of the target
`x_R`.

H-TOP is **load-bearing**. It is what fixes the generator degree
`delta = m * 2^(m-1)` (`KN-FIND-0618ab`), and through that it fixes the
first-fall closed form of `H-PFDR-4148b8`, the zero-row finding that voided the
`m >= 3` cells of the one conditional cost table this program has built, and the
degree floor `d_ff >= delta + 1` at every arity.

## What is settled

| `m` | status | basis |
| --- | --- | --- |
| 2 | **holds** | by hand; degree 4, top form `16 a_{1,0} a_{1,1} a_{2,0} a_{2,1}` after substitution, reproduced term by term by an independent reviewer |
| 3 | **holds** | `RUN-PFDR-5726af-htop`: `Res_T(S_3(x1,x2,T), S_3(x3,x_R,T))` over `Z[a,b,x_R]` has total degree 12 in `(x1,x2,x3)`, per-variable `[4,4,4]`, 125 monomials, degree-12 part the single monomial `x1^4 x2^4 x3^4` with coefficient exactly 1, free of `a`, `b`, `x_R`. Independently reproduced by a different extraction route (TASK-20260904-ed0e8f) and by a third implementation (TASK-20260904-642cf5), the latter adding a negative leg the run did not record: `S_4` vanishes 8/8 on planted zero-sum 4-tuples and is nonzero 8/8 at random `x_R` |
| 4 | **holds** (established by review, not by the run) | `deg_{(x1..x4)} S_5 = 32` and the coefficient of `x_1^8 x_2^8 x_3^8 x_4^8` is 1, in six random `(a, b, x_R)`, with `x_R` symbolic, and with `a, b` symbolic — no free symbols in the leading coefficient. The package's own stage-0 note had declared `m = 4` **not attempted** |
| ≥ 5 | **OPEN** | — |

## Why it is not already closed by the general argument

The argument offered in the record — "the resultant recursion multiplies leading
coefficients" — is a **generic** statement, and the degenerate specialisations a
reviewer actually hit are exactly where genericity fails: `c_1 = c_2` and
`x_3 = x_4` kill the leading `T`-coefficient. A proof therefore needs the
**non-vanishing of both leading `T`-coefficients** through the recursion, and
that is not established. Being generic is not the same as being true at the
specialisation the construction uses.

A second reason the claim is not free: the archived list `[4, 4, 4, 12]` that
`HEUR-001`'s `random_model_justification` cites as a per-variable profile of
`S_4` is **not one** — it is a generator-degree list, decisive because the entry
becomes `[5, 5, 5, 12]` when `|FB| = 5`, and a per-variable profile cannot track
the factor base. So `m = 3` rests on the symbolic run alone, and `m >= 5` has no
archival support at all.

## Resolution criteria

- **POSITIVE.** Extend the symbolic check to `S_6` at `m = 5` by the same
  one-variable specialisation used at `m = 4` — the reviewer estimates seconds
  of `sympy` and it settles the next case outright — and then supply the
  recursion argument with the non-vanishing of both leading `T`-coefficients
  discharged, which is what would close `m >= 5` in general rather than one case
  at a time. Predicted values at `m = 5`: total degree `m*2^(m-1) = 80` in the
  five unknowns, per-variable degree `2^(m-1) = 16`, top form the single
  monomial `prod_k x_k^16` with coefficient 1.
- **NEGATIVE.** Any `m` at which the degree-`m*2^(m-1)` part of `S_{m+1}` is not
  a single monomial, or has a coefficient depending on `(a, b)` or `x_R`, or has
  a coefficient that vanishes modulo some prime of interest. Such an instance
  would be a counterexample certificate and would immediately re-open the
  `m >= 3` cells of the conditional cost table, the first-fall closed form at
  that arity, and the degree floor.
- Either outcome is decisive and cheap. This is the smallest open object in the
  degree column.

## Scope

- The claim is about the top form only, not about the whole polynomial, and not
  about any cost, solving degree or attack. Nothing about the ECDLP follows from
  either resolution by itself.
- `KN-TECH-002` gives the classical per-variable law `2^(n-2)` for `S_n`, which
  is consistent with H-TOP and is the reason `m*2^(m-1)` is the expected total
  degree; what H-TOP adds beyond that law is the **single-monomial** structure
  and the **constant, non-vanishing** leading coefficient, and those are what the
  downstream results actually use.
- A CAS resultant over `Z[a, b, x_R]` is exact and has no termination heuristic,
  so a `sympy` computation is an acceptable instrument here; the contract that
  produced the `m = 3` result names the construction, not a CAS. Sage is absent
  from the current execution host, and that is an infrastructure fact, never
  evidence about this question.
