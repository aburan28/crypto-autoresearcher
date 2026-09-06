---
id: KN-TECH-d64293
type: technique
title: Neural feature extraction as a classical mask generator - Fourier/Goldreich-Levin decision-rule readout, first-layer Top-k projection, and the composed-objective discipline that must rank the candidates
tags: [differential-neural, neural-distinguisher, differential-linear, fourier-analysis, goldreich-levin, mask-search, candidate-generation, sparsity-regularization, objective-mismatch, proxy-reward, sat-linear-trail, arx, speck, siphash, chacha, interpretability, methodology, symmetric-cryptanalysis, symmetric, cross-domain]
confidence: reported
complexity: >-
  Candidate generation is one training run plus a heavy-Fourier search; ranking is
  the expensive half and is a separate solver cost per candidate (one
  minimum-weight linear-trail search each). The technique makes no complexity
  claim of its own: it converts a learned model into a candidate SET, and the
  quality of the result is decided entirely by the objective used to rank that
  set.
applicability: >-
  Any search where a cheap learned or heuristic scorer proposes an INTERMEDIATE
  object that must then be composed with further stages before its value is known
  - differential-linear intermediate masks being the worked case, but equally
  learned move ordering in an algebraic search, learned pivot or presentation
  selection, and any RL reward defined on a local surrogate rather than on
  downstream yield.
source_refs: [KN-LIT-824baa, KN-LIT-4449, KN-LIT-1717, KN-LIT-3694, KN-TECH-065, KN-TECH-056, KN-TECH-080]
added: "2026-09-04"
superseded_by: null
---

## Epistemic status

The mechanics below are transcribed from [[KN-LIT-824baa]] and are `reported`:
nothing here has been reproduced by this program. The **discipline** in the last
two sections is this program's abstraction, adopted on its own merits and
consistent with `docs/inventor-protocol.md` (null-object controls before belief,
the lossy-projection test) and [[KN-TECH-080]] (method ceiling, nearby-object
control). Treat the pipeline as a candidate generator to be audited, not as a
method known to work.

## The pipeline

Three stages, and the third is the one that is usually skipped.

### 1. Train a difference-only distinguisher

Feed the network `φ_diff(C_0, C_1) = C_0 ⊕ C_1` rather than the ciphertext pair.
This is a deliberate loss of information — the pair determines the difference and
not conversely — and it is what buys the interpretation: for a mask `Γ`,

    ⟨Γ, C_0 ⊕ C_1⟩ = ⟨Γ, C_0⟩ ⊕ ⟨Γ, C_1⟩,

so every parity feature over the input **is** a classical equal-mask
differential-linear feature. A full-pair distinguisher is strictly stronger as a
classifier and strictly worse as an interface: its features can be
unequal-mask "variant-DL" relations with no classical equal-mask reading.

### 2. Read masks out, two independent ways

**Decision level — heavy-Fourier extraction.** Take the sign representation
`g(x) = (−1)^{f(x)}` of the trained Boolean rule and run the Goldreich–Levin
heavy-coefficient search: buckets `(k, S)` with `S ⊆ {1..k}`, estimated weight

    w_g(k,S) = E_z E_{y,y'} [ g(y‖z) g(y'‖z) χ_S(y) χ_S(y') ],

split every bucket whose weight exceeds `τ²/2`, then keep the surviving supports
with `|ĝ(S)| > τ`. Each retained `S` is an output mask. Report the
**reconstruction similarity** — agreement between the sparse rule and the network
on *fresh uniform* inputs, not on training data — because a support set that
explains 82% of the rule is a different object from one that explains 98%.

**Representation level — first-layer Top-k projection.** Strip the residual
tower and reorganize the first convolution to run along the difference **bit**
dimension, so the layer is `W ∈ R^{N_f × d}` with one coefficient per bit
(`Conv1DFully` in [[KN-LIT-824baa]]). Project each row to a weight-`k` mask by
`Γ_j = TopK(|W_j|)`. Several channels may project to the same mask; the
multiplicity is itself a signal.

The two readouts answer different questions and neither substitutes for the
other. The first-layer set is what the model *can see*; the Fourier set is what
survives to *decide*. In [[KN-LIT-824baa]] a mask known to be useful reached the
first-layer set in 9 of 30 runs and the decision set in 0 of 30 — so reporting
only one of the two would have told the opposite story.

### 3. Rank the candidates by the COMPOSED objective, not by the training loss

This is the step whose omission the source paper is named after. A fixed-round
distinguisher trained on a middle component `E_m` optimizes for the local
correlation `r`. A long-round differential-linear distinguisher is worth
`p · r · q²`, where `q` comes from a linear approximation over rounds the network
never saw. Ranking by `r` and ranking by `r q²` gave **different orders**, and the
locally best candidate lost to the classical one by a factor `2^13`.

So: generate with the network, then score every candidate with the real
objective — one minimum-weight linear-trail search (SAT/MILP) per candidate — and
rank on that. The candidate set is cheap and large; the ranking is expensive and
is the actual product.

## Sparsity guidance, and its exact ceiling

Adding a first-layer sparsity regularizer
`L = L_cls + λ_sp(e)·b_sp(e)·L_sp(W)` — a soft-activity ratio annealed toward a
target `max_hw/d`, with L1, asymmetric over/under penalties and a boost factor —
biases the representation toward low-Hamming-weight masks and measurably enlarges
the candidate pool (34.4 → 44.4 of 77 strong weight-2 masks; a specific useful
mask 1/30 → 9/30 at the first layer).

**It cannot rank.** The source paper's own Table 7 contains two Hamming-weight-2
masks whose 5-round trail correlations differ by `2^9`. Any prior defined on
weight alone is blind to that gap by construction. Sparsity guidance is therefore
a *recall* intervention, not a *precision* one — expect it to widen the pool, and
do not expect it to move the decision rule. It also costs stability: seed-to-seed
accuracy variance rose roughly twentyfold in the reported experiment.

## The generalization: proxy scoring of intermediate objects

Strip the cryptanalysis and the pattern is a scoring-objective defect that has
nothing to do with neural networks:

> When a search proposes an **intermediate** object and scores it by a locally
> measurable proxy, the selection is only as good as the proxy's rank correlation
> with the composed downstream objective. If that correlation is near zero the
> search is wasting its budget; if it is **negative** the search is actively
> steering away from the good candidates, and it will do so more confidently the
> better it is trained.

The diagnostic is one number and it is cheap: on a sample where both are
computable, measure the rank correlation between the proxy and the composed
objective *before* trusting any ranking the search produces. The remedies, in
increasing cost:

1. **Re-rank.** Keep the proxy as a generator, discard its ordering, and score the
   whole candidate set with the composed objective. Always available; costs one
   downstream evaluation per candidate.
2. **Structural prior.** Bias generation toward a family known to compose well.
   Sparsity is the weak version of this — it is a prior on the object's *size*
   when what is needed is a prior on its *position*.
3. **Surrogate of the downstream term.** Precompute or approximate the composed
   factor and fold it into the training objective. This is the open half; see
   [[KN-OPEN-7f0d85]].

**Where this program is already exposed.** `harness/rl_isogeny` scores candidate
Semaev presentations by null-relative Macaulay excess — a local surrogate — and
not by downstream solve yield. That is the same shape, and it inherits the same
obligation: measure the rank correlation between reward and yield at a scale
where both are computable, before the reward is trusted to rank.

## Controls this technique requires before any of its output is believed

Under `docs/inventor-protocol.md` and [[KN-TECH-080]]:

- **Budget-matched classical baseline (the lossy-projection test).** Spend the
  network's data budget on directly measuring the candidate space instead. In the
  reported SipHash setting the exhaustive weight-≤4 evaluation was *already
  feasible* — 679,120 masks — and recovered a superset of what the network found.
  A neural generator only earns its cost where the classical enumeration does not
  fit, so state the crossover point rather than assuming it.
- **Null-object control on near-deterministic features.** A parity with
  correlation indistinguishable from 1 over a multi-round component is a
  candidate *structurally forced* relation, not a finding. Re-measure it under a
  fresh key schedule, a shorter round count, and an unrelated input difference
  before recording it.
- **Untrained-model control.** Report what Top-k projection of a randomly
  initialized first layer recovers. Recovery rates are meaningless without it.
- **Decomposition sensitivity.** The boundary between `E_1`, `E_m`, `E_2` is a
  free parameter — the same 18-round Speck128/128 distinguisher is analyzed as
  `5+8+5` and as `5+9+4` in the literature — so a "DL score" is not well defined
  until the decomposition is either fixed and declared, or optimized as part of
  the measure. Any ranking that is boundary-sensitive is not admissible as a
  portfolio measure.
- **Budget outcomes are not bounds.** A minimum-weight trail search that times
  out gives no `q`; recording it as a weak `q` is an `AGENTS.md` rule 3
  violation.

## Reference points usable as implementation-fidelity gates

All `reported` from [[KN-LIT-824baa]] and its cited sources; reproduce them
before extending anything.

| setting | object | value |
| --- | --- | --- |
| Speck32/64, 9 rd | DL `(0xa840,0x0010) → (0x0205,0x0204)` | corr `2^-7.3` |
| Speck32/64, 5 rd | DL `(0x1000,0x5000) → (0x0205,0x0204)` | corr `2^-1` |
| SipHash-2-4 final., 4 rd | mask `{61,29}` under `Δ=(0x40000,0x80040000,0,0)` | corr `2^-6.03` |
| SipHash-2-4 final., 4 rd | strongest weight-≤4 mask `{25}` | corr `2^-4.86` |
| Speck128/128, 18 rd | `5+8+5`, mask `{77,5}` | `p=2^-30`, `r=2^-5.81`, `q=2^-10` |
| ChaCha, 2.5 rd middle | single-bit mask `{0}` | corr `2^-8.3` |
