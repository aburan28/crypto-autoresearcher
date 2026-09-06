---
id: KN-OPEN-7f0d85
type: open_problem
title: Can a learned cryptanalytic feature search be made long-round-aware - is there a trainable surrogate for the downstream linear-extension term, or is re-ranking the ceiling?
tags: [differential-neural, differential-linear, mask-search, objective-mismatch, proxy-reward, surrogate-objective, reward-design, sat-linear-trail, sparsity-regularization, arx, speck, siphash, chacha, reinforcement-learning, methodology, open, symmetric-cryptanalysis, cross-domain]
confidence: reported
status: open
source_refs: [KN-LIT-824baa, KN-TECH-d64293, KN-TECH-065, KN-TECH-056, KN-TECH-080, KN-LIT-4449, KN-LIT-1717]
added: "2026-09-04"
superseded_by: null
---

## The gap, stated precisely

A fixed-round difference-only differential-neural distinguisher trained on a
middle component `E_m` minimizes a binary classification loss under a fixed data
distribution. Its features are therefore ordered by the **local** correlation
`|r|`. A long-round differential-linear distinguisher built from that middle is
worth

    p · r · q²,

where `q` is the correlation of a linear approximation over rounds the network
never saw and cannot see. Nothing in the training objective refers to `q`.

[[KN-LIT-824baa]] establishes that this is not a theoretical worry. On the
18-round Speck128/128 `5+8+5` distinguisher, every recurrently extracted neural
mask had a *stronger* middle correlation than the classically selected `{77,5}`
(up to `2^-0.01` against `2^-5.81`) and a *weaker* composed correlation, the best
losing by `2^13.16`. Sparsity guidance raised the classical mask's first-layer
recovery from 1/30 runs to 9/30 but left decision-level recovery at 0/30.

**The generator is not obviously the problem; the ranking is.** That is the
distinction the open questions below are organized around, and it is also what
makes the problem tractable — re-ranking is always available, so the question is
whether anything cheaper or stronger exists.

## Open questions

**Q1 — Is the candidate set already sufficient?** Nobody has scored the *whole*
neural candidate set by the composed objective. [[KN-LIT-824baa]] computes `q`
for six masks: five recurrent Fourier terms and the classical reference. The
first-layer projection exposes `44.37 ± 3.16` of the 77 strong weight-2 masks per
sparsity-guided model. Does that set contain a mask with `|r q²| > 2^-25.81` —
i.e. does pure re-ranking of an existing generator already beat the classically
searched mask? This is roughly 77 solver calls and it decides whether the defect
is generative or merely ordinal. **If re-ranking suffices, Q2–Q4 are optional
optimizations.**

**Q2 — Is `|r|` uninformative about `|q|`, or anti-informative?** Measure the rank
correlation between the middle correlation and the minimum-weight forward trail
correlation across a declared candidate space. Zero correlation means the neural
preference wastes budget; negative correlation means it *steers away* from good
candidates and will do so more confidently the better it is trained. The two
diagnoses call for different repairs and the measurement separating them is one
scatter plot.

**Q3 — Is there a cheap structural prior that ranks where sparsity cannot?**
Hamming weight demonstrably cannot: the source paper's Table 7 contains two
weight-2 masks whose trail correlations differ by `2^9`. A prior on mask
*position* rather than *size* might. One concrete, untested candidate from
[[KN-LIT-824baa]]'s Table 6: the masks the network prefers appear to be
(left-word bit `b`, right-word bit `b`) pairs, while the classically useful
`{77,5}` is offset by 8 = Speck128's rotation constant `α`. Whether the
`α`-offset family systematically admits lower-weight forward trails is
enumerable and unverified.

**Q4 — Is there a trainable surrogate for `q`?** The obstruction is that `q`
comes from a discrete minimum-weight trail search — not differentiable, and one
solver call per candidate. Possible routes, none tested: precompute `q` on a
sampled mask set and fit a cheap predictor used as a training-time re-weighting;
substitute a differentiable relaxation of linear-trail weight; or abandon
end-to-end training and use the network purely as a proposal distribution inside
a classical search loop. A negative result here — that no surrogate beats
re-ranking at equal cost — is a complete and useful answer.

**Q5 — Where is the crossover at which a neural generator earns its cost?** In
the SipHash setting the *exhaustive* weight-≤4 enumeration was feasible (679,120
masks) and contained everything the network found. A generator only pays for
itself where enumeration does not fit. State the state size, Hamming weight, and
data budget at which a budget-matched classical search (exhaustive, random, or
greedy) stops winning. Without this the whole approach has no established regime.

**Q6 — Does the `5+8+5` result survive the boundary being moved?** Gong et al.
re-decompose the same 18-round distinguisher as `5+9+4`, under which the neural
boundary carries the singleton `{5}` instead of `{77,5}`. If the mismatch
weakens or vanishes under a different split, then it is partly an artifact of
where the boundary was drawn — and any DL score used as a portfolio measure over,
say, a rotation-constant space must optimize the decomposition rather than fix
it.

## Why this is on the program's list at all

The cipher-specific version is adjacent to this program's symmetric goals
(`GOAL-SIMSPK-001` most directly). The **general** version is not adjacent to
anything — it is a defect this program can commit in its own tooling, and
arguably already has: `harness/rl_isogeny` scores candidate Semaev presentations
by null-relative Macaulay excess, a local surrogate, and not by downstream solve
yield. Q2's diagnostic transfers verbatim to that reward. Any future learned or
heuristic ranker over intermediate objects inherits the same obligation, which is
recorded as a required control in [[KN-TECH-d64293]].

## What would close this

Q1 and Q2 together close the *diagnostic* half and are cheap enough to be a
single bounded experiment. Q5 establishes whether there is a regime worth
optimizing at all, and should probably run before Q3 and Q4 rather than after —
a generator with no established regime is not worth a surrogate. Q4's honest
best outcome may well be "re-ranking is the ceiling", which is a result and
should be recorded as one rather than treated as a failure to find a method.

None of the above is answered here. Nothing in [[KN-LIT-824baa]] has been
reproduced by this program; every number quoted in this entry is `reported`.
