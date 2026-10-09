# Public noncentral-endomorphism sampler: zero-run synthesis

**Date:** 2026-10-09  
**Goal:** `GOAL-SSI-2fa82a`  
**Question:** `RQ-SSI-1946c9`  
**Batch:** `BATCH-12e6aa`  
**Report task:** `TASK-20261009-a0cb98`

## Result at a glance

**[Independently verified]** The round evaluated four proposed public
noncentral-endomorphism sampler families against five independently owned
joints. No family survived all five. F1 and F2 retain scoped accepted-output
typing facts but break J3, J4, and J5; F3 remains inconclusive at J3 but
breaks J4 and J5; F4 remains inconclusive at J3 and J5 but breaks J4. The
round therefore reports zero surviving sampler families, zero PKE candidates,
and zero KEM or key-exchange candidates. This is the copied, non-voted
composition in [S7].

**[Derived]** “No surviving family” means only that none of the four frozen
packets passed every joint. It is not a proof that public noncentral samplers
do not exist, not an EndRing hardness result, and not a family-level
impossibility theorem.

**[Unmeasured]** No scientific, implementation, formalizer, experiment,
benchmark, or parameter-selection run was performed. Consequently this report
contains no quantitative performance graph. The explanatory flow diagram is
available as editable [Mermaid source](sampler-flow.mmd) and as a rendered
[vector SVG](sampler-flow.svg).

## Evidence labels and decision loop

**[Derived]** This report uses four labels throughout:

- **[Proposed]** identifies a candidate mechanism, interface, or future gate.
- **[Derived]** identifies a consequence recomputed from the frozen contract
  or independently verified premises.
- **[Independently verified]** identifies a conclusion owned by a frozen
  independent review or the final composition.
- **[Unmeasured]** identifies a cost, probability, scaling, or performance
  quantity for which this zero-run round supplied no measurement.

**[Independently verified]** The user-directed research loop is explicit:

> **propose → independently evaluate → retain / repair / retire → ideate-next**

**[Derived]** In this round, “retain” preserves the accepted-output algebra and
the exact probability/cost identities that passed their owning joints;
“repair” was considered under one reserved correction and skipped under the
frozen admission rule; “retire” removes F1–F4 from the surviving set for this
round without asserting universal impossibility; and “ideate-next” points to a
new interface addressing adaptive OneEnd coverage. The complete flow and its
status labels appear in Figure 1.

![Figure 1. Candidate families feed independent J1–J5 gates, composition, the
retain/repair/retire decision, and the next ideation loop.](sampler-flow.svg){width=95%}

## Frozen question and scope

**[Proposed]** For public parameters
\(\Pi_\lambda=(p_\lambda,\mathbb F_{p_\lambda^2},E_{0,\lambda},
\ell,L_\lambda,\mathrm{Canon},A_{\mathrm{eval}})\), the challenge endpoint
\(E\) is sampled by the campaign-defined exact nonbacktracking
\(\ell\)-isogeny walk from \(E_{0,\lambda}\). Only canonical endpoint bytes
are released. The walk, kernels, maps, orientation, ideals, tags, torsion
labels, and endomorphism-ring witnesses are erased. The sampler receives only
\(\Pi_\lambda\), \(E\), and independent coins [S1, S2].

**[Proposed]** The target interface is

\[
  \mathrm{Samp}(\Pi_\lambda,E;\rho)\longrightarrow
  \mathtt{FAIL}\ \text{or}\ D_\alpha,
\]

where an accepted descriptor is canonically serialized, efficiently
evaluable, and publicly verifies as a non-scalar self-map
\(\alpha:E\to E\). It must provide one polynomial \(q\) and negligible
\(\nu\) such that

\[
 \Pr_{E\leftarrow D_{ER}}
 \left[\Pr_\rho[\mathrm{Verify}(E,D_\alpha)=1]
 \geq 1/q(\lambda)\right]\geq 1-\nu(\lambda).
\]

**[Derived]** This quantifier order separates bad-curve mass from coin
failure on a fixed curve. Retrying with fresh coins must keep the same
challenge \(E\); resampling \(E\) would change the experiment. The byte-level
law includes `FAIL`, rejects, retries, aborts, descriptor size, validation,
runtime, and memory [S1, S3].

**[Independently verified]** \(D_{ER}\) is a campaign-defined endpoint law on
canonical bytes with path multiplicity retained. The inspected sources do not
identify it exactly with a uniform or standard EndRing input law, and no
applicable bridge to such a law was supplied [S2, S3].

## Four proposed families

### F1 — relative Frobenius and the conjugate curve

**[Proposed]** Find a separable \(\phi:E\to E^{(p)}\), then compose it with
relative Frobenius \(F_{E^{(p)},p}:E^{(p)}\to E\). A deterministic public core
exists on the locus where canonicalization supplies an isomorphism
\(c:E^{(p)}\to E\), using \(\phi=c^{-1}\) [S1, S4].

**[Independently verified]** Conditional on a valid separable \(\phi\), the
composition is a typed self-map of degree \(p\deg\phi\) and inseparable degree
\(p\); the nonsquare inseparable degree excludes scalars. A raw coordinatewise
\(p\)-power map from \(E\) instead targets \(E^{(p)}\) and is not an
endomorphism of \(E\) unless the return leg is present [S2, S4, S5].

**[Unmeasured]** No general public `FindConjugate`, high-\(D_{ER}\)-mass bound,
complete polynomial time/memory bound, or non-singleton honest-support result
was established. The exact public core has publicly enumerable singleton
support [S3, S7].

### F2 — exceptional automorphism transport

**[Proposed]** Use a public nontrivial automorphism directly at \(j=0\) or
\(1728\), or transport one to a general curve as
\(\widehat\phi\circ u\circ\phi:E\to E\) [S1, S4].

**[Independently verified]** Accepted direct exceptional automorphisms are
degree-one maps distinct from \(\pm1\). For an accepted transported path, the
quadratic identity has nonzero discriminant and rejects the identity-middle
immediate backtrack. These are accepted-output facts only [S4, S5].

**[Unmeasured]** The two exceptional geometric classes do not supply a
probability bound under \(D_{ER}\). No general public
`FindExceptionalPath`, complete polynomial cost, or hidden-support result was
established; the direct route again has singleton public support [S2, S3,
S7].

### F3 — short nonbacktracking cycles

**[Proposed]** Enumerate bounded odd nonbacktracking \(\ell\)-isogeny words,
normalize every step, require exact canonical closure at \(E\), and return the
lexicographically first accepted descriptor [S1, S4].

**[Independently verified]** Every accepted odd closed word gives a typed
self-map of degree \(\ell^d\), which is nonsquare for odd \(d\); immediate
dual backtracks are excluded and would be scalar controls. The deterministic
per-curve success law is exact [S3, S4].

**[Unmeasured]** `F3-ODD-CYCLE-MASS` and `F3-PUBLIC-LINE-ENUM` remain unproved,
so neither high-mass success nor complete polynomial bit cost is established.
The lexicographically first returned byte string is a publicly enumerable
singleton whenever construction is polynomial [S3, S7].

### F4 — bounded map or interpolation search

**[Proposed]** Sample a fixed bounded raw string, parse it as a canonical
rational-map descriptor or deterministic interpolation transcript, compile
to one explicit map, globally verify the curve equation and source/target,
and reject scalars [S1, S4].

**[Independently verified]** Every accepted descriptor is a globally verified
non-scalar \(E\to E\) map. The raw domain, acceptance multiplicities,
same-curve retry law, and one-call symbolic polynomial cost are exact under
the frozen evaluator contract [S3, S4].

**[Unmeasured]** `F4-BOUNDED-DESCRIPTOR-DENSITY` is unproved. No positive
support-entropy lower bound and no theorem excluding a different polynomial
support enumerator was established. Thus J3 and J5 remain inconclusive, not
positive [S3, S7].

## Accepted-output typing is not construction or success

**[Independently verified]** J2 holds for all four families only under the
quantifier “for every accepted non-`FAIL` descriptor.” It establishes the
root type \(E\to E\), field and composition compatibility, canonical syntax
handling, and a public non-scalarity certificate [S4, S5].

**[Derived]** That statement has the logical form

\[
  \mathrm{Accept}(E,D)\Longrightarrow
  \llbracket D\rrbracket\in\mathrm{End}(E)\setminus\mathbb Z.
\]

It does **not** imply that an accepted descriptor exists for a general
endpoint, that it can be constructed publicly from the bare curve, that the
acceptance probability is inverse-polynomial on \(1-\nu\) of \(D_{ER}\), or
that retries, total cost, support, and scaling meet the sampler contract.

**[Unmeasured]** Evaluation through the frozen evaluator is specified, but no
concrete operation count, runtime, memory measurement, implementation result,
or parameter scaling was produced [S4, S5].

## Independent joint matrix

**[Independently verified]** The following matrix reproduces the final
composition exactly; the Coordinator copied owner verdicts without voting
[S7].

| Candidate | J1 | J2 | J3 | J4 | J5 |
|---|---|---|---|---|---|
| F1-relative-frobenius | holds | holds | breaks | breaks | breaks |
| F2-exceptional-automorphism-transport | holds | holds | breaks | breaks | breaks |
| F3-short-cycle | holds | holds | inconclusive | breaks | breaks |
| F4-bounded-map-search | holds | holds | inconclusive | breaks | inconclusive |

**[Independently verified]** Joint meanings are:

- **J1 — distribution and sources:** `holds` means the exact campaign law,
  bare-input declaration, representation boundary, and non-equivalence to a
  standard law are stated honestly. It does not prove useful-locus mass [S3].
- **J2 — type and non-scalarity:** `holds` is restricted to accepted outputs;
  it does not prove construction, existence, density, or scaling [S4, S5].
- **J3 — success and cost:** F1/F2 break because their submitted general
  routes and required success/cost parameters are absent; F3/F4 are
  inconclusive because named mass/density or cost obligations remain open
  [S6].
- **J4 — hard-problem implication:** `breaks` for the frozen interface across
  all families because the Page–Wesolowski adaptive oracle is not instantiated
  by a high-mass promise under one fixed distribution [S6, S7].
- **J5 — support and auxiliary data:** F1/F2/F3 break on publicly enumerable
  singleton returned support; F4 is inconclusive. Leaked path, orientation,
  ideal, tag, torsion, or ring data would change the bare-curve problem [S6].

## Distributional bounded OneEnd versus the required adaptive oracle

**[Independently verified]** An accepted descriptor is a bounded OneEnd answer
for that same curve. If a family actually satisfied J3, then for a good
\(E\sim D_{ER}\), capped same-curve repetition with
\(N=\lceil q(\lambda)\kappa\ln2\rceil\) would fail with probability at most
\(2^{-\kappa}\). Across \(D_{ER}\), total failure would be at most
\(\nu(\lambda)+2^{-\kappa}\) [S6, S7].

| Property | Frozen sampler promise | Oracle needed by the cited PW reduction |
|---|---|---|
| Input coverage | Good set has mass at least \(1-\nu\) under one fixed \(D_{ER}\) | Every adaptively queried curve, or a proved bridge for every internal query law |
| Walk law | Fixed start, fixed length, nonbacktracking \(\ell\)-walk | Source-generated 2-isogeny walks from the arbitrary EndRing input, with fixed and adaptive lengths |
| Failure | Capped wrapper can return `FAIL`; unbounded retry may not terminate on bad curves | Each oracle call supplies a valid bounded non-scalar endomorphism |
| Cost condition | Expected polynomial only conditional on a good curve; capped cost includes residual failure | Uniform conditional expected bound through every adaptive transcript |
| Result | Distributional bounded OneEnd on the stated scope | Enough coverage to instantiate `EndRing <= bounded OneEnd` |

**[Independently verified]** The cited Page–Wesolowski direction is
\(\mathrm{EndRing}\leq\mathrm{bounded\ OneEnd}\): a bounded OneEnd oracle is
used to solve EndRing. The reverse observation that an EndRing basis yields a
non-scalar element is separate and must not be confused with that theorem
[S2, S6].

**[Independently verified]** The earliest missing bridge is an upgrade to a
total bounded OneEnd oracle for every adaptive query, or a complete bridge to
all Page–Wesolowski internal query laws with reciprocal-success, termination,
degree, representation, canonical-transport, and total-cost bounds. No such
bridge is present. Therefore the frozen sampler-to-EndRing composition breaks;
this is not an EndRing separation or hardness theorem [S6, S7].

## Correction decision

**[Independently verified]** The reserved correction decision is reproduced
exactly from [S7]:

```yaml
reserved_task_id: TASK-20261009-1f7c04
user_authorization_received: true
queued: false
disposition: skipped_by_frozen_admission_rule
reason: >-
  No one missing source or typing repair can change a family disposition.
  F1 and F2 need a new public constructor plus mass/cost/support and oracle-
  coverage results. F3 needs independent mass/cost, support, and coverage
  repairs. F4 needs density, support, and coverage results. Changing D_ER or
  adding a path, orientation, ideal, tag, torsion data, or complete ring is
  forbidden by the frozen rule.
```

**[Derived]** No correction packet was admitted, so the initial matrix is the
final matrix. The retained results are the scoped typed facts and exact laws;
all four candidates are retired from this round’s survivor set.

## PKE, KEM, and key-exchange gates

**[Derived]** A public noncentral sampler would be only an upstream ingredient.
The following gates remain distinct and none may be skipped:

| Gate | Required evidence | Status after this round |
|---|---|---|
| Public sampler | One F1–F4-style family survives J1–J5, including construction, high-mass success, cost, and support | **Not established:** zero surviving families |
| Hard-problem bridge | Total adaptive bounded OneEnd coverage, or a complete bridge to every PW internal query law | **Not established:** J4 breaks |
| Public-key binding and correctness | A complete scheme syntax with key generation, encryption/encapsulation or exchange, decryption/decapsulation or agreement, and message/key recovery correctness | **Not proposed or evaluated** |
| Security game | Exact PKE/KEM/key-exchange adversary model and game, oracle access, assumptions, and a correctly directed reduction | **Not proposed or evaluated** |
| Concrete realization | Parameters, implementation, side conditions, validation, performance, and end-to-end costs | **Unmeasured:** zero implementation, parameter, experiment, and benchmark runs |

**[Independently verified]** The composition establishes no secure PKE, no
IND-CPA or IND-CCA result, no KEM, no authenticated or unauthenticated key
exchange, no public-key binding, no message recovery construction, and no
concrete parameters [S7].

## Retain, retire, and ideate-next

**[Derived]** Retain:

- the exact \(D_{ER}\) and byte-law discipline;
- J2’s accepted-output type/non-scalarity invariants;
- F3/F4’s exact per-curve counting and retry identities at their stated scope;
- the proof that a distributional promise does not automatically instantiate
  an adaptive always-answer oracle.

**[Derived]** Retire from this round’s survivor set: F1, F2, F3, and F4 as
submitted. F1/F2 need more than a single source or typing repair; F3/F4 remain
scientifically open at named joints but still fail the all-joint admission
rule. This retirement does not assert nonexistence.

**[Proposed]** Ideate-next under `ENDRING-ADAPTIVE-ONEEND-COVERAGE`: propose
materially distinct interfaces that either give a uniformly polynomial public
non-scalar-endomorphism sampler on every supersingular oracle input, or prove a
complete bridge from a declared sampler law to every adaptive
Page–Wesolowski internal query law. Each proposal must preserve exact success,
total-cost, and honest-support accounting and must independently evaluate
construction, typing, per-query success, adaptive termination, cost, support
enumeration, and reduction quantifiers [S7].

**[Proposed]** The next ideation step is not an automatic launch and does not
authorize a PKE/KEM/key-exchange or security claim. Hidden orientation, ideal,
path, tag, torsion basis, or complete-ring data; challenge-curve resampling;
and universal-impossibility inference remain excluded [S7].

## Run and measurement accounting

**[Independently verified]** The frozen reviews and final composition report
the following exact counts [S3, S4, S6, S7]:

| Run class | Count | Evidence label |
|---|---:|---|
| Scientific runs | 0 | independently verified |
| Implementation runs | 0 | independently verified |
| Formalizer runs | 0 | independently verified |
| Experiment runs | 0 | independently verified |
| Benchmark runs | 0 | independently verified |
| Parameter-selection runs | 0 | independently verified |

**[Unmeasured]** There are no measured runtimes, operation counts, memory
figures, success frequencies, uncertainty intervals, concrete security
parameters, or end-to-end comparisons. A quantitative graph would therefore
have no data to plot and is intentionally omitted. Source inspection,
symbolic derivation, hashing, parsing, static validation, and document
rendering are administrative operations, not scientific runs.

## Limitations

**[Derived]** This report is a synthesis of the frozen methodology, source
ledger, four independent review records, the J2 companion assessment, and the
final composition. It does not re-open producer packets or primary-source
bytes and does not extend any frozen reviewer’s authority.

**[Independently verified]** The results do not establish an EndRing solver,
EndRing hardness, complete-ring reconstruction, novelty, a deployable
primitive, a parameter set, or impossibility of public noncentral samplers.
J6 documentation review occurs only after these report/visual artifacts exist
and is not claimed here [S7].

## Source index

**[Derived]** All scientific claims above are traceable to these frozen
repository artifacts. Hashes are the frozen values recorded by the review or
composition; `[S1]` is the unchanged methodology hash recorded by J4.

| ID | Frozen repository source | Role | SHA-256 |
|---|---|---|---|
| S1 | [methodology.md](methodology.md) | Frozen question, families, controls, and zero-run boundary | `0c2cbca1fd2e78b2d4bbfe138d63e92fe6643070f3d5401ff1a308d392e88998` |
| S2 | [source-ledger.yaml](../../../coordination/design/TASK-20261009-1c8974/tasks/TASK-20261009-daf6ab/source-ledger.yaml) | Primary-source provenance and transfer limits | `d7a7e0063115037ac77302a8e748d899fea6e6ec0732660efeddfc56f6336fa9` |
| S3 | [J1 review](../../../coordination/design/TASK-20261009-1c8974/reviews/TASK-20261009-8182ff/review.yaml) | Exact distribution, bare input, and source boundary | `9d0807b0b05b0598001fbbb80533e0eba548f5fb7028f99ab2663a12a10b4c2e` |
| S4 | [J2 review](../../../coordination/design/TASK-20261009-1c8974/reviews/TASK-20261009-b3e555/review.yaml) | Accepted-output typing, serialization, and non-scalarity | `3f11486bf45d2b77f3f03850cad64a097b1fb894d5c4c95997d38ed8e6bac111` |
| S5 | [J2 transfer companion](../../../coordination/design/TASK-20261009-1c8974/reviews/TASK-20261009-b3e555/transfer-assessment.json) | Construction/existence/preservation/cost separation; draft companion, not a ledger record or certificate | `d87296a557b2147cbd0285d06bb2ecee9a5fcb5691eb37483896ebc9cbfc3d0c` |
| S6 | [J3/J5 review](../../../coordination/design/TASK-20261009-1c8974/reviews/TASK-20261009-38456a/review.yaml) and [J4 review](../../../coordination/design/TASK-20261009-1c8974/reviews/TASK-20261009-8a1dc4/review.yaml) | Success/cost/support and hard-problem implication | `e9b9478b7a26cee0512e81194f2a0efa55871c6486447d1a00cfc8ad657fcd4c`; `9f99aa52b39d29aca1328e1dbec9b9840a5a1a4487878cdf9845ddca38663924` |
| S7 | [final-composition.yaml](../../../coordination/design/TASK-20261009-1c8974/composition/TASK-20261009-44fe0f/final-composition.yaml) | Exact matrix, correction decision, outcomes, and next action | `a16c3cc8d6302723b839eeaa310a308939870933cae53f0d00f7a90da78f7533` |

