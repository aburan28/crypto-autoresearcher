# HQC analytic decoding-failure-rate model — verbatim transcription

**Task**: `TASK-20260802-6344ed` (executor) · **Batch**: `BATCH-001` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-02 · **Repo commit at start**: `47a684f24a51771cad8336509d28ec025755501b` (clean tree)

---

## 0. What this document is, and what it is not

This is a **transcription**. It states what the primary sources say, in their
own words and symbols, and numbers the assumptions so later records can cite
them by identifier.

It contains **no assessment of HQC's security in either direction**, no
hypothesis, no experiment, no re-derivation, and no judgement about whether any
assumption below is correct, tight, or sufficient. Sections 6 and 7 record
**hedges the primary text makes about itself** and **anomalies visible in the
published text**; both are reported as observations of the source, not as
findings about HQC.

Nothing here was written from memory. No `UNVERIFIED-FROM-MEMORY` section
exists because none was needed: both primary sources were obtained. See
`source_access_log.yaml` for routes, timestamps, and hashes.

---

## 1. Sources transcribed

| Key | Document | Obtained from | sha256 | Level |
|---|---|---|---|---|
| **SPEC** | *Hamming Quasi-Cyclic (HQC)*, specification dated 22/08/2025, 51 pp. | `https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf` | `174186cb5fdc0108aad914391360c222f52ea533bfb406146fac124b3a25406d` (876 126 B) | full text read |
| **RMRS** | Aragon, Gaborit, Zémor, *HQC-RMRS, an instantiation of the HQC encryption framework with a more efficient auxiliary error-correcting code*, arXiv:2005.10741 (submitted 21 May 2020), 14 pp. | `https://arxiv.org/pdf/2005.10741` | `cbb7dbd670f27cdcf602438018df52745c0af495050aedb3b83a0b00986f5446` (525 223 B) | full text read |

**Why RMRS is here.** SPEC §6.1.1 opens: *"We provide a precise analysis of the
error distribution approximation following [4]."* SPEC reference **[4]** is
exactly the RMRS paper (SPEC p.48: *"Nicolas Aragon, Philippe Gaborit, and
Gilles Zémor. HQC-RMRS, an instantiation of the HQC encryption framework with
a more efficient auxiliary error-correcting code.
https://arxiv.org/abs/2005.10741."*). RMRS is therefore **the derivation source
SPEC's DFR model points at**, identified from the specification itself rather
than from memory or from a search guess.

Neither PDF is committed to this repository (handoff constraint on third-party
copyrighted PDFs). The hashes above let a reviewer re-acquire and check
byte-identity.

### 1.1 Extraction method and how formulas were verified

Text was extracted with PyMuPDF 1.28.0 (`page.get_text("text")`), Python
3.11.15. Linear text extraction mangles displayed mathematics. Therefore
**every displayed formula reproduced in §3–§5 below was additionally verified
by rendering the source page to an image and reading the rendered page**, not
by trusting the text layer. Full pages 32, 33, 35, 36, 37, 38, 39 were rendered
at 2.2× scale; pages 18 and 29 were rendered as 2.6×-scale clips of the region
holding the tables in question.

Per-formula status is marked inline:

- `[IMAGE-VERIFIED]` — the rendering below was checked against the rendered
  page image and matches it.
- `[EXTRACTION-DAMAGED]` — the text layer produced something that could not be
  reconciled with the page image, or the rendering here may be lossy. **A
  formula so marked carries no claim and must be re-read from the PDF before
  any use.**

Pages rendered and read as images: SPEC pp. 18, 29, 32, 33, 35, 36, 37, 38, 39.
RMRS formulas were **not** image-verified; RMRS material appears below only as
prose quotation and as cross-reference, and any RMRS formula is marked
accordingly.

---

## 2. The objects the model is about (SPEC, definitional context)

Quoted so the symbols in §3–§5 have their source meanings.

**Codes.** SPEC §3.4.1: *"For the external code, we use a Reed-Solomon code of
dimension 32 over F256. For the internal code, we use the Reed-Muller code
[128, 8, 64] that we duplicate 3 or 5 times (i.e. duplicating each bit to
obtain codes of parameters [384, 8, 192] and [640, 8, 320]). We perform maximum
likelihood decoding on the internal code. Doing that, we obtain a vector of
F_q^{n_e} that is then decoded using an algebraic decoder for the Reed-Solomon
code."*

**Shortened RS codes** (SPEC §3.4.2, `[IMAGE-VERIFIED]` p.18): RS-S1[46 = 255 −
209, 16 = 225 − 209, 31]; RS-S2[56 = 255 − 199, 24 = 223 − 199, 33]; RS-S3[90 =
255 − 165, 32 = 197 − 165, 49]. Table 3 gives (n, k, δ) = (46, 16, 15),
(56, 24, 16), (90, 32, 29) for RS-S1/S2/S3. *(See anomaly X6.)*

**Error vector.** SPEC §6.1: *"We analyze the distribution of the error vector
**e′** = **x** · **r**₂ − **r**₁ · **y** + **e** in Section 6.1.1"*.

**Decoding condition.** SPEC §3.5, *Correctness*: *"The correctness of HQC
relies on the decoding capability of the code C. Specifically, C correctly
decodes v − u · y whenever: ω(s · r₂ − u · y + e) ≤ ∆ ; ω((x + h · y) · r₂ −
(r₁ + h · r₂) · y + e) ≤ ∆ ; ω(x · r₂ − r₁ · y + e) ≤ ∆"*.

**∆.** SPEC Definition 2.2.5 context: *"A code of length n and dimension k with
minimum distance d is capable of decoding arbitrary patterns of up to ∆ =
⌊(d−1)/2⌋ errors and is denoted as an [n, k, d] code."*

**Parameter sets.** SPEC Table 5 `[IMAGE-VERIFIED]` p.29 — reproduced exactly:

| Instance | Security | n₁ | n₂ | n | k | ω | ω_r = ω_e | DFR |
|---|---|---|---|---|---|---|---|---|
| HQC-1 | NIST-1 | 46 | 384 | 17 669 | 128 | 66 | 75 | < 2⁻¹²⁸ |
| HQC-3 | NIST-3 | 56 | 640 | 35 851 | 192 | 100 | 114 | < 2⁻¹⁹² |
| HQC-5 | NIST-5 | 90 | 640 | 57 637 | 256 | 131 | 149 | < 2⁻²⁵⁶ |

SPEC §4.1 prose: *"n₁ denote the length of the external Reed-Solomon code and
n₂ denote the length of the internal Reed-Muller code so that the length of the
concatenated code C is n₁n₂, its dimension is k and its decoding failure rate
(DFR) is adjusted for each security level. The parameter n denotes the length
of the ambient space namely the smallest primitive prime greater than n₁n₂. The
parameters ω, ω_r and ω_e denote the weight of the vectors (x, y), (r₁, r₂) and
e respectively."*

---

## 3. Stage 1 — the error-vector distribution (SPEC §6.1.1)

### 3.1 The framing paragraph (verbatim, SPEC p.32) `[IMAGE-VERIFIED]`

> "We provide a precise analysis of the error distribution approximation
> following [4]. We first compute exactly the probability distribution of each
> fixed coordinate e′_k of the error vector
> e′ = x · r₂ − r₁ · y + e = (e′₀, . . . e′_{n−1}).
> We obtain that every coordinate e′_k is Bernoulli distributed with parameter
> p∗ = P[e′_k = 1] given by Proposition 6.1.2.
>
> To compute decoding error probabilities, we will then need the probability
> distribution of the weight of the error vector e′ restricted to given sets of
> coordinates that correspond to codeword supports. We will make the
> simplifying assumption that the coordinates e′_k of e′ are independent
> variables, which will let us work with the binomial distribution of parameter
> p∗ for the weight distributions of e′. In other words we modelize the error
> vector as a binary symmetric channel with parameters p∗. This working
> assumption is justified by remarking that, in the high weight regime relevant
> to us, since the component vectors x, y, e have fixed weights, the
> probability that a given coordinate e′_k takes the value 1 conditioned on
> abnormally many others equalling 1 can realistically only be ≤ p∗. We support
> this modeling of the otherwise intractable weight distribution of e′ by
> extensive simulations. These simulations back up our assumption that our
> computations of decoding error probabilities and DFRs can only be upper
> bounds on their real values.
>
> The vectors x, y, r₁, r₂, e have been taken uniformly random and
> independently chosen among vectors of weight ω, ω_r and ω_e."

### 3.2 Proposition 6.1.1 (SPEC p.32) `[IMAGE-VERIFIED]`

> "**Proposition 6.1.1.** *Let x = (x₀, . . . x_{n−1}) be a random vector chosen
> uniformly among all binary vectors of weight ω and let r = (r₀, . . . ,
> r_{n−1}) be a random vector chosen uniformly among all vectors of weight ω_r
> and independently of x. Then, denoting z = x · r, we have that for every k ∈
> {0, . . . n − 1}, the k-th coordinate z_k of z is Bernoulli distributed with
> parameter p̃ = P(z_k = 1) equal to:*"

```
              1                    ⌈
p̃  =  ───────────────────   ·      Σ        C_ℓ
       C(n,ω) · C(n,ω_r)      1 ⩽ ℓ ⩽ min(ω,ω_r)
                                   ℓ odd
```

> "*where C_ℓ = C(n, ℓ) · C(n−ℓ, ω−ℓ) · C(n−ω, ω_r−ℓ).*"

`C(a,b)` denotes the binomial coefficient written in the source as a stacked
`(a choose b)`.

### 3.3 Equation (1) — distribution of t = x·r₂ − r₁·y (SPEC p.33) `[IMAGE-VERIFIED]`

Preceded verbatim by: *"By independence of (x, r₂) with (y, r₁), the k-th
coordinates of x · r₂ and of r₁ · y are independent, and they are Bernoulli
distributed with parameter p̃ by Proposition 6.1.1. Therefore their modulo 2 sum
t = x · r₂ − r₁ · y is Bernoulli distributed with:"*

```
Pr[t_k = 1] = 2 p̃ (1 − p̃)
Pr[t_k = 0] = (1 − p̃)² + p̃²                                      (1)
```

### 3.4 Proposition 6.1.2 and Equation (2) (SPEC p.33) `[IMAGE-VERIFIED]`

> "**Proposition 6.1.2.** *Let x, y, r₁, r₂, e be independent random vectors
> with uniform distributions among vectors of fixed weight w for x, y, among
> vectors of weight ω_r for r₁, r₂, and among vectors of weight ω_e for e. Let
> e′ = x · r₂ − r₁ · y + e = (e′₀, . . . , e′_{n−1}). Then for any k = 0 . . . n
> − 1, the coordinate e′_k has distribution:*"

```
Pr[e′_k = 1] = 2p̃(1 − p̃)(1 − ω_e/n) + ((1 − p̃)² + p̃²)(ω_e/n)
Pr[e′_k = 0] = ((1 − p̃)² + p̃²)(1 − ω_e/n) + 2p̃(1 − p̃)(ω_e/n)      (2)
```

### 3.5 Equation (3) — the binomial weight model (SPEC p.33) `[IMAGE-VERIFIED]`

> "Proposition 6.1.2 gives us the probability that a coordinate of the error
> vector e′ is 1. In our simulations, which occur in the regime ω = α√n with
> constant α, we make the simplifying assumption that the coordinates of e′ are
> independent, meaning that the weight of e′ follows a binomial distribution of
> parameter p⋆, where p⋆ is defined as in Eq. (2): p⋆ = 2p̃(1 − p̃)(1 − ω_e/n) +
> ((1 − p̃)² + p̃²)(ω_e/n). This approximation will give us, for 0 ≤ d ≤ min(2 ×
> ω × ω_r + ω_e, n),"

```
Pr[ω(e′) = d] = C(n, d) · (p⋆)^d · (1 − p⋆)^(n−d)                  (3)
```

### 3.6 The simulation evidence SPEC offers for stage 1 (SPEC p.34, verbatim)

> "These simulations show that error vectors are more likely to have a weight
> close to the mean than predicted by the binomial distribution, and that on
> the contrary the error is less likely to be of large weight than if it were
> binomially distributed. This is illustrated on the parameter set corresponding
> to HQC-1. For cryptographic purposes we are mainly interested by very small
> DFR and large weight occurrences which are more likely to induce decoding
> errors. These tables show that the probability of obtaining a large weight is
> close but smaller for the error weight distribution of e′ rather than for the
> binomial approximation. This supports our modelization and the fact that
> computing the decoding failure probability with this binomial approximation
> permits to obtain an upper bound on the real DFR. This will be confirmed
> hereafter by simulations with real weight parameters (but smaller lengths).
> … We computed vectors of length n and then truncated the last l = n − n₁n₂
> bits before measuring the Hamming weight of the vectors."

SPEC Table 9: parameter set HQC-1, ω = 66, ω_e = ω_r = 75, n = 17 669,
n₁n₂ = 17 664, p⋆ = 0.3398. (Caption: *"Table 9: Probability p∗ for HQC-1
parameter set"* — see anomaly X8.)

SPEC Table 10 — *"Simulated probabilities of large weight vectors for HQC-1 for
the error vector distribution and the binomial approximation"*:

| | 0.1% | 0.01% | 0.001% | 0.0001% |
|---|---|---|---|---|
| Error vectors | 6 169 | 6 203 | 6 232 | 6 257 |
| Binomial approximation | 6 197 | 6 237 | 6 272 | 6 301 |

---

## 4. Stage 2 — DFR of the internal (Reed-Muller) code (SPEC §6.1.2)

Lead-in, verbatim (SPEC p.35): *"It is only possible to obtain an exact
decoding probability formula for the Reed-Solomon codes as for Reed-Muller
codes we consider a maximum-likelihood decoding for which there is no exact
formula. We provide in the following proposition a lower bound on the decoding
probability in that case."*

### 4.1 Proposition 6.1.3 — simple upper bound (SPEC p.35) `[IMAGE-VERIFIED]`

> "**Proposition 6.1.3** (Simple Upper Bound for the DFR of the internal code)**.**
> *Let p be the transition probability of the binary symmetric channel. Then
> the DFR of a duplicated Reed-Muller code of dimension 8 and minimal distance
> d_i can be upper bounded by:*"

```
              d_i
p_i = 255  ·   Σ    C(d_i, j) · p^j · (1 − p)^(d_i − j)
             j=d_i/2
```

**Proof, verbatim (SPEC pp. 35–36)** `[IMAGE-VERIFIED]`:

> "For any linear code C of length n, when transmitting a codeword c, the
> probability that the channel makes the received word y at least as close to a
> word c′ = c + x as c (for x a non-zero word of C and ω(x) the weight of x)
> is:"

```
   Σ        C(ω(x), j) · p^j · (1 − p)^(n − j)
j ⩾ ω(x)/2
```

> "By the union bound applied on the different non-zero codewords x of C, we
> obtain that the probability of a decryption failure can thus be upper bounded
> by:"

```
     Σ            Σ        C(ω(x), j) · p^j · (1 − p)^(n − j)
x∈C, x≠0     j ⩾ ω(x)/2
```

> "There are 255 non-zero words in a [128,8,64] Reed-Muller code, 254 of weight
> 64 and one of weight 128. The contribution of the weight 128 vector is
> smaller than the weight 64 vectors, hence by applying the previous bound to
> duplicated Reed-Muller codes we obtain the result."

*(The exponent in the proposition statement is `(1 − p)^(d_i − j)`; the
exponent in the general expression inside its own proof is `(1 − p)^(n − j)`.
Both renderings are image-verified. Recorded as anomaly X1; no claim is made
here about which is intended.)*

### 4.2 Proposition 6.1.4 — improved upper bound (SPEC p.36) `[IMAGE-VERIFIED]`

Lead-in, verbatim: *"**Better upper bound for the DFR of the internal code.**
The previous simple bound pessimistically assumes that decoding fails when more
than one codeword minimizes the distance to the received vector. The following
bound improves the previous one by taking into account the fact that decoding
can still succeed with probability 1/2 when exactly two codewords minimize the
distance to the received vector."*

> "**Proposition 6.1.4** (Improved Upper Bound for the DFR of the internal
> code)**.** *Let p be the transition probability of the binary symmetric
> channel. Then the DFR of a Reed-Muller code of dimension 8 and minimal
> distance d_i can be upper bounded by:*"

```
          n
p_i  =    Σ     𝔄_ω · p^ω · (1 − p)^(n − ω)
       ω=d_i/2
```

> "*where*"

```
𝔄_ω = min [ C(n, ω) ,

            ½ · 255 · C(d_i, d_i/2) · C(d_i, ω − d_i/2)

                        d_i
            +  255  ·    Σ     C(d_i, j) · C(d_i, ω − j)
                      j=d_i/2+1

                            d_i/2
            +  ½ · C(255,2) ·  Σ    C(d_i/2, j)³ · C(d_i/2, ω − d_i + j)  ]
                             j=0
```

**Proof, verbatim (SPEC pp. 36–38)** `[IMAGE-VERIFIED]`:

> "Let E be the decoding error event. Let e be the error vector.
> • Let A be the event where the closest non-zero codeword c to the error is
>   such that d(e, c) = d(e, 0) = ω(e).
> • Let B be the event where the closest non-zero codeword c to the error
>   vector is such that d(e, c) < ω(e).
> • Let A′ ⊂ A be the event where the closest non-zero codeword c to the error
>   vector is such that d(e, c) = ω(e) and such a vector is unique, meaning that
>   for every c′ ∈ C, c′ ≠ c, c′ ≠ 0, we have d(e, c′) > ω(e).
> • Finally, let A″ be the event that is the complement of A′ in A, meaning the
>   event where the closest non-zero codeword c to the error is at distance |e|
>   from e, and there exists at least one codeword c′, c′ ≠ c, c′ ≠ 0, such that
>   d(e, c′) = d(e, c) = ω(e).
>
> The probability space is partitioned as Ω = A ∪ B ∪ C = A′ ∪ A″ ∪ B ∪ C,
> where C is the complement of A ∪ B. When C occurs, the decoder always decodes
> correctly, i.e. P(E|C) = 0. We therefore write:
> P(E) = P(E|A′)P(A′) + P(E|A″)P(A″) + P(E|B)P(B)
>
> When the event A′ occurs, the decoder chooses at random between the two
> closest codewords and is correct with probability 1/2, i.e. P(E|A′) = 1/2. We
> have P(E|B) = 1 and writing P(E|A″) ⩽ 1, we have:"

```
P(E_ω) ⩽ ½ P(A′_ω) + P(A″_ω) + P(B_ω)
       = ½ (P(A′_ω) + P(A″_ω)) + ½ P(A″_ω) + P(B_ω)
P(E_w) ⩽ ½ P(A_ω) + ½ P(A″_ω) + P(B_ω)                             (4)
```

> "where for X = A, A′, A″, E, the event X_ω signifies the intersection of the
> event X with the event "ω(e) = ω". Now we have the straightforward union
> bounds:"

```
                d_i
P(B_ω) ⩽ 255  ·  Σ     C(d_i, j) · C(d_i, weight − j) · p^ω · (1 − p)^(n − ω)   (5)
              j=d_i/2+1
```

**The literal token `weight` above is what the published PDF renders.** It is
image-verified on SPEC p.37 and is **not** an extraction artefact; the
corresponding slot in the Proposition 6.1.4 statement reads `ω − j`. Recorded
as anomaly X2. This rendering carries no claim.

> "with n = 2d_i the length of the inner code, and where we use the convention
> that a binomial coefficient C(ℓ, k) = 0 whenever k < 0 or k > ℓ."

```
P(A_ω) ⩽ 255 · C(d_i, d_i/2) · C(d_i, ω − d_i/2) · p^ω · (1 − p)^(n − ω)        (6)
```

> "and it remains to find an upper bound on P(A″). We have: P(A″) ⩽ Σ_{c,c′}
> P(A_{c,c′}) where the sum is over pairs of distinct non-zero codewords and
> where: A_{c,c′} = {d(e, c) = d(e, c′) = ω(e)}
>
> This event is equivalent to the error meeting the supports of c and c′ on
> exactly half their coordinates. All codewords except the all-one vector have
> weight d_i, and any two codewords of weight d_i either have non-intersecting
> supports or intersect in exactly d/2 positions. P(A_{c,c′}) is largest when c
> and c′ have weight d and non-zero intersection. In this case we have:"

```
            d_i/2
P(A^ω_{c,c′}) = Σ    C(d_i/2, j)³ · C(d_i/2, ω − d_i + j) · p^ω · (1 − p)^(n − ω)
             j=0
```

> "Hence,"

```
                                            d_i/2
P(A″_ω) ⩽ Σ P(A_{c,c′}) ⩽ C(255, 2) ·        Σ    C(d_i/2, j)³ · C(d_i/2, ω − d_i + j)
          c,c′                              j=0
                                            · p^ω · (1 − p)^(n − ω)             (7)
```

> "Plugging 6, 5 and 7 into 4 we obtain the result."

### 4.3 SPEC's own statement of what the bound is worth (verbatim, p.38)

> "The previous formula permits to obtain a lower bound on the decoding
> probability. When the error rate gets smaller, the bound becomes closer to
> the real value of the decoding probability. For cryptographic parameters the
> approximation is less precise, which means that the DFR obtained will be
> conservative compared to what happens in practice."

### 4.4 SPEC Table 11 (image-verified, p.38)

Prose above it, verbatim: *"We performed simulations to compare the real
decryption failure rate with the theoretical one from proposition 6.1.3 for
[512, 8, 256] and [640, 8, 320] duplicated Reed-Muller codes using p⋆ values
from actual parameters."* *(See anomaly X4: the codes named in the prose and
the codes listed in the table differ.)*

| Security level | p⋆ | Reed-Muller code | DFR from 6.1.4 | Observed DFR |
|---|---|---|---|---|
| NIST-1 | 0.3398 | [384, 8, 192] | −10.79 | −10.96 |
| NIST-3 | 0.3618 | [640, 8, 320] | −14.14 | −14.39 |
| NIST-5 | 0.3725 | [640, 8, 320] | −11.30 | −11.48 |

Caption, verbatim: *"Table 11: Comparison between the observed Decryption
Failure Rate and the formula from proposition 6.1.3. Results are presented as
log₂(DFR)."* *(Header says 6.1.4, caption says 6.1.3 — anomaly X3.)*

---

## 5. Stage 3 — DFR of the concatenated code (SPEC §6.1.3)

Lead-in, verbatim (SPEC p.38): *"Using the lower bound p_i on the decoding
probability of the Reed-Muller codes given in Section 6.1.2, one can deduce the
DFR of the concatenated code used in HQC."*

### 5.1 Theorem 6.1 (SPEC pp. 38–39) `[IMAGE-VERIFIED]`

> "**Theorem 6.1** (DFR of the concatenated code)**.** *The DFR of the
> concatenated code using a Reed-Solomon code [n_e, k_e, d_e]_{F₂₅₆} as the
> external code and a Reed-Muller code as the internal code can be upper
> bounded by:*"

```
  n_e
   Σ     C(n_e, l) · p_i^l · (1 − p_i)^(n_e − l)
l=δ_e+1
```

> "*where d_e = 2δ_e + 1 and p_i is defined as in proposition 6.1.3.*"

### 5.2 The simulation SPEC reports for stage 3 (verbatim, p.39)

> "In Figure 4, we tested the DFR of the concatenated codes against both
> symmetric binary channels and HQC vectors, and compared the results with the
> theoretical value obtained using Proposition 6.1.3 and Theorem 6.1."

Figure 4 caption, verbatim: *"Comparison between the DFR from Theorem 6.1
(Theoretical) and the actual DFR of concatenated codes against approximation by
a binary symmetric channel (Binomial) and against HQC error vectors (HQC).
Parameters simulated are derived from those of HQC for NIST-1 security level:
ω = 66, ω_r = ω_e = 75, a [384, 8, 192] duplicated Reed-Muller code for
internal code and a [NRS, 16] Reed-Solomon code for external code."*

Figure 4 axes as rendered: x-axis `NRS` from 32 to 36; y-axis `DFR` from −22 to
−2; three series `Theoretical`, `Binomial`, `HQC`. **Figure 4 is a plot; no
numeric series is transcribed here, because reading values off a rendered plot
would be an estimate and not a transcription.**

### 5.3 How the DFR enters the IND-CCA2 statement (SPEC §6.2.2, verbatim)

Transcribed because `GOAL-HQC-001` is framed on "the DFR model that carries
IND-CCA"; this is the exact textual join.

> "**Definition 6.2.1** (δ-correct PKE [22])**.** A PKE = (PKE.Keygen,
> PKE.Encrypt, PKE.Decrypt) is δ-correct if:
> E[ max_{m∈M} Pr[PKE.Decrypt(dk_PKE, c_PKE) ≠ m | c_PKE ←
> PKE.Encrypt(ek_PKE, m)] ] ≤ δ.   (9)
> where the expectation is taken over (ek_PKE, dk_PKE) ← PKE.Keygen(param)."

> "In HQC-PKE the failure to decrypt a ciphertext c_PKE occurs if and only if
> ω (x · r₂ − r₁ · y + e) > ∆.
> Note that the aforementioned equation does not depend on the message m.
> Therefore, the probability in Equation 9 simplifies to
> Pr[PKE.Decrypt(dk_PKE, c_PKE) ≠ m | c_PKE ← PKE.Encrypt(ek_PKE, m)] ≤ δ. (11)
> This probability is equivalent to the probability that is analyzed in section
> 6.1 namely: Pr[ ω (x · r₂ − r₁ · y + e) > ∆ | … ] ≤ δ.   (12)"

*(Equation 12's conditioning block lists the `XOF.Init` / `SampleFixedWeightVect$`
sampling calls for y, x, r₂, e, r₁; reproduced in the source as a bracketed
list. Not re-typeset here.)*

> "**Theorem 6.3.** If HQC-PKE is δ correct, for any IND-CCA2 adversary A
> against the HQC-KEM scheme issuing at most q_RO queries to G and q_D queries
> to the HQC-KEM.Decaps oracle, there exists adversaries B₁ and B₂ such that:"

```
Adv^{IND-CCA2}_{HQC-KEM}(A) ⩽  1/(2^{|k|} · 2^{|salt|})  +  3 q_RO / 2^{|k|}
                             +  (q_RO + q_D) · δ
                             +  2 · ( Adv_{2-DQCSD-P}(B₁) + Adv_{3-DQCSD-PT}(B₂) )   (13)
```

`[EXTRACTION-DAMAGED]` — Equation (13) was transcribed from the **text layer
only**; SPEC p.44 was not rendered and read as an image. The term structure and
the four summands are legible in the text layer, but the exact typesetting of
the first two denominators is not image-confirmed. **This rendering carries no
claim** and must be re-read from the PDF before use.

SPEC §6.2.3 then states that when the deployed sampler
`SampleFixedWeightVect` (biased) replaces `SampleFixedWeightVect$` (uniform),
*"The third term (q_RO + q_D) · δ is related to the δ-correctness of the scheme
… Using Lemma 6.4, the above probability increases by at most (τ^{ω_r}_max)³"*,
with τ values in SPEC Table 12 (e.g. NIST-1: τ^{ω_r}_max = 1.00015).

---

## 6. NUMBERED ASSUMPTIONS

These are the assumptions the transcribed model rests on. Each carries the
source text that establishes it. **A-numbers are stable identifiers for later
records to cite.** Where an assumption is *implicit in a formula rather than
stated in prose*, that is said explicitly and is an observation about the text,
not a criticism of it.

| # | Assumption | Where it comes from |
|---|---|---|
| **A1** | x, y, r₁, r₂, e are **uniformly random and independently chosen** among binary vectors of fixed weight ω (x, y), ω_r (r₁, r₂), ω_e (e). | SPEC §6.1.1, verbatim: *"The vectors x, y, r₁, r₂, e have been taken uniformly random and independently chosen among vectors of weight ω, ω_r and ω_e."* Also Prop 6.1.2's hypothesis. |
| **A2** | Within Prop 6.1.1, **x and r are independent**, giving the exact per-coordinate Bernoulli parameter p̃. | Prop 6.1.1 hypothesis: *"…chosen uniformly among all vectors of weight ω_r and independently of x."* |
| **A3** | **(x, r₂) is independent of (y, r₁)**, so the k-th coordinates of x·r₂ and r₁·y are independent, giving Eq. (1). | SPEC p.33 verbatim: *"By independence of (x, r₂) with (y, r₁), the k-th coordinates of x · r₂ and of r₁ · y are independent…"* |
| **A4** | **e is independent of t = x·r₂ − r₁·y**, giving Eq. (2). | SPEC p.33 verbatim: *"Finally, by adding modulo 2 coordinate-wise the two independent vectors e and t, we obtain the distribution of the coordinates of the error vector e′."* |
| **A5** | **THE COORDINATES OF e′ ARE INDEPENDENT** — the load-bearing simplifying assumption. Consequence: the weight of e′ (and of e′ restricted to a codeword support) is **binomial** with parameter p⋆, i.e. e′ is modelled as a **binary symmetric channel** with crossover p⋆. | SPEC §6.1.1, verbatim: *"We will make the simplifying assumption that the coordinates e′_k of e′ are independent variables, which will let us work with the binomial distribution of parameter p∗ for the weight distributions of e′. In other words we modelize the error vector as a binary symmetric channel with parameters p∗."* Restated at Eq. (3). |
| **A6** | The **direction** claimed for A5's error: conditioning on abnormally many coordinates equal to 1 can *"realistically only"* lower a coordinate's probability below p∗, so the binomial model is claimed to yield **upper bounds** on DFR. | SPEC §6.1.1, verbatim: *"…the probability that a given coordinate e′_k takes the value 1 conditioned on abnormally many others equalling 1 can realistically only be ≤ p∗."* and *"…our computations of decoding error probabilities and DFRs can only be upper bounds on their real values."* Stated as supported by simulation, not proved. |
| **A7** | A5 is applied **in the regime ω = α√n with constant α**. | SPEC p.33, verbatim: *"In our simulations, which occur in the regime ω = α√n with constant α, we make the simplifying assumption…"* |
| **A8** | The internal-code bound takes **p (the BSC transition probability) equal to p⋆** computed at the scheme's parameters. | Props 6.1.3/6.1.4 are stated for *"p … the transition probability of the binary symmetric channel"*; Table 11 supplies p⋆ per level and Table 9 gives p⋆ = 0.3398 for HQC-1. |
| **A9** | **Union bound over the 255 non-zero RM codewords** (Prop 6.1.3). | SPEC p.36, verbatim: *"By the union bound applied on the different non-zero codewords x of C…"* |
| **A10** | The **all-one codeword (weight 128) is dropped**, on the stated ground that its contribution is smaller than that of the weight-64 codewords, and the weight-64 count 254 is rounded up to 255. | SPEC p.36, verbatim: *"There are 255 non-zero words in a [128,8,64] Reed-Muller code, 254 of weight 64 and one of weight 128. The contribution of the weight 128 vector is smaller than the weight 64 vectors…"* |
| **A11** | The bound derived for the **[128,8,64] RM code is transferred to its 3× and 5× duplications** by substituting the duplicated minimum distance d_i and length n = 2d_i. | SPEC p.36, verbatim: *"…hence by applying the previous bound to duplicated Reed-Muller codes we obtain the result."* and p.37: *"with n = 2d_i the length of the inner code"*. |
| **A12** | The decoder used on the internal code is **maximum-likelihood**, for which *"there is no exact formula"*; hence a bound rather than an exact DFR. | SPEC §6.1.2 lead-in, verbatim. Decoder realisation in SPEC §3.4.3 (Hadamard transform / "Green machine", peak selection with the stated tie rule). |
| **A13** | **Tie-breaking model in Prop 6.1.4**: P(E \| A′) = 1/2 (decoder picks at random between the two closest codewords), P(E \| B) = 1, P(E \| A″) ⩽ 1, P(E \| C) = 0. | SPEC p.37, verbatim. |
| **A14** | **Worst-case pair choice** for P(A_{c,c′}): the bound uses the configuration claimed to maximise it (two weight-d_i codewords with non-zero intersection, intersecting in d/2 positions). | SPEC p.38, verbatim: *"P(A_{c,c′}) is largest when c and c′ have weight d and non-zero intersection."* |
| **A15** | **Union bound over ordered/unordered pairs** of distinct non-zero codewords for P(A″), with the count taken as C(255, 2). | SPEC p.38, Eq. (7). |
| **A16** | **Cap by C(n, ω)**: 𝔄_ω is the minimum of the union-bound expression and the total number of weight-ω vectors — a probability-capping step. | SPEC p.36, the `min[ … ]` in Prop 6.1.4. |
| **A17** | **THE n_e INNER-DECODER OUTCOMES ARE INDEPENDENT AND IDENTICALLY DISTRIBUTED WITH FAILURE PROBABILITY p_i.** This is what makes Theorem 6.1's expression a binomial tail. **It is implicit in the formula; neither SPEC §6.1.3 nor RMRS Theorem 4.3 states it in prose.** Recorded as an observation about the text. | Theorem 6.1's summand `C(n_e, l) p_i^l (1 − p_i)^{n_e − l}` is the binomial pmf; SPEC's surrounding prose is only *"Using the lower bound p_i … one can deduce the DFR of the concatenated code used in HQC."* |
| **A18** | **The outer RS decoder fails exactly when more than δ_e of the n_e symbols are wrong**, with d_e = 2δ_e + 1 — i.e. bounded-distance decoding of the shortened RS code, and one failed inner block counted as exactly one symbol error. | Theorem 6.1's summation lower limit `l = δ_e + 1` and its *"where d_e = 2δ_e + 1"*. |
| **A19** | Theorem 6.1 uses **p_i "as defined in proposition 6.1.3"** (the simple bound), per the theorem's own text — although §6.1.3's lead-in points to §6.1.2 and Table 11's header names 6.1.4. | SPEC p.39, verbatim: *"where d_e = 2δ_e + 1 and p_i is defined as in proposition 6.1.3."* See anomaly X3. |
| **A20** | For the IND-CCA2 join: **decryption failure occurs if and only if ω(e′) > ∆**, and ∆ = ⌊(d−1)/2⌋ for the concatenated code C. | SPEC §6.2.2 verbatim (*"occurs if and only if"*), §3.5 *Correctness*, and Definition 2.2.5's ∆. |
| **A21** | The **δ used in Theorem 6.3 is the DFR analysed in §6.1**, and the IND-CCA2 advantage acquires the term **(q_RO + q_D) · δ**. | SPEC §6.2.2 verbatim: *"This probability is equivalent to the probability that is analyzed in section 6.1"*; Theorem 6.3's third summand. |
| **A22** | The §6.1 analysis and the §6.2.1–6.2.2 proofs assume the **uniform** fixed-weight sampler `SampleFixedWeightVect$`; the biased deployed sampler `SampleFixedWeightVect` is handled separately in §6.2.3 by multiplying by at most (τ^{ω_r}_max)³. | SPEC §6.2 verbatim: *"we assume in Sections 6.2.1 and 6.2.2 that the vectors r₁, r₂ and e are generated using SampleFixedWeightVect$ instead of SampleFixedWeightVect"*; §6.2.3 and Table 12. |
| **A23** | Computations are performed in F₂ⁿ with n the smallest primitive prime greater than n₁n₂, and the **ℓ = n − n₁n₂ trailing bits are truncated**; the stage-1 simulation likewise truncates before measuring weight. | SPEC §3.5 verbatim and SPEC p.34 verbatim: *"We computed vectors of length n and then truncated the last l = n − n₁n₂ bits before measuring the Hamming weight of the vectors."* |

---

## 7. WHERE THE PRIMARY TEXT HEDGES (verbatim)

Recorded because the handoff asks for *"every place the primary text itself
hedges"*. These are the sources' own words about their own model.

- **H1** (SPEC §6.1.1) — *"We will make the **simplifying assumption** that the
  coordinates e′_k of e′ are independent variables"*.
- **H2** (SPEC §6.1.1) — *"This **working assumption** is justified by remarking
  that … the probability that a given coordinate e′_k takes the value 1
  conditioned on abnormally many others equalling 1 can **realistically only**
  be ≤ p∗."*
- **H3** (SPEC §6.1.1) — *"We support this modeling of the **otherwise
  intractable** weight distribution of e′ by extensive simulations. These
  simulations **back up our assumption** that our computations of decoding
  error probabilities and DFRs **can only be upper bounds** on their real
  values."*
- **H4** (SPEC §6.1.2) — *"for Reed-Muller codes we consider a
  maximum-likelihood decoding for which **there is no exact formula**."*
- **H5** (SPEC §6.1.2) — *"The previous simple bound **pessimistically assumes**
  that decoding fails when more than one codeword minimizes the distance to the
  received vector."*
- **H6** (SPEC p.38) — *"When the error rate gets smaller, the bound becomes
  closer to the real value of the decoding probability. **For cryptographic
  parameters the approximation is less precise**, which means that the DFR
  obtained will be conservative compared to what happens in practice."*
- **H7** (SPEC p.34) — *"These tables show that the probability of obtaining a
  large weight is **close but smaller** for the error weight distribution of e′
  rather than for the binomial approximation."*
- **H8** (RMRS Remark 4.2, verbatim) — *"Propositions 4.2.1 and 4.2.2 have been
  derived with a binary symmetric channel model for the distribution of the HQC
  error vector restricted to the support of a (duplicated) Reed-Muller code.
  Figure 4 compares the actual weight distribution of the error vector to the
  binomial distribution when restricted to this relatively small number of
  bits. We observe that they are virtually identical, meaning that **a small
  proportion of HQC bits do behave as i.i.d Bernoulli variables**."*
- **H9** (RMRS Remark 4.1, verbatim) — *"Propositions 4.2.1 and 4.2.2 give
  upper bounds on the Decryption Failure Rate for the internal code. **The
  smaller the DFR, the closer the bounds become to the real value.**"*
- **H10** (RMRS §4.3, verbatim) — *"For Reed-Muller codes, rather than
  considering the upper bound approximation we effectively decoded the code,
  which means than in practice the upper bound that we use for our theoretical
  DFR, is greater than what is obtained in the simulations."*
- **H11** (RMRS §5 Conclusion, verbatim) — *"In Section 3 we presented a better
  analysis of the error weight distribution for HQC, which leads to a better
  DFR estimation."*

### 7.1 What RMRS (SPEC ref [4]) adds that SPEC does not carry

Recorded as observations, since the handoff asks for the model's derivation
source.

1. **RMRS §3's justification paragraph is nearly identical to SPEC §6.1.1** —
   the same *"simplifying assumption … independent variables"* sentence appears
   in both, with SPEC adding the phrase *"In other words we modelize the error
   vector as a binary symmetric channel with parameters p∗"*, which RMRS's
   corresponding paragraph does not contain.
2. **RMRS Remark 4.1 tabulates BOTH bounds against the observed DFR; SPEC
   Table 11 tabulates one.** RMRS Table 4 (verbatim values): security 128,
   p⋆ = 0.3196, [256, 8, 128], DFR from 4.2.1 = −7.84, from 4.2.2 = −8.03,
   observed = −8.72; security 192, p⋆ = 0.3535, [512, 8, 256], −11.81, −12.12,
   −12.22; security 256, p⋆ = 0.3728, [768, 8, 384], −13.90, −14.20, −14.25.
   These are **different codes and different p⋆ values from SPEC Table 11** —
   they are the 2020 RMRS-paper parameters, not the 2025 SPEC parameters.
3. **RMRS Remark 4.2 is the only place either source states the scope of the
   i.i.d. claim explicitly** (*"a small proportion of HQC bits do behave as
   i.i.d Bernoulli variables"*). SPEC has no equivalent remark.
4. **RMRS Theorem 4.3 is SPEC Theorem 6.1** with the same expression and the
   same closing clause (*"Where d_e = 2δ_e + 1 and p_i is defined as in
   Proposition 4.2.1"*). RMRS gives **no proof** of Theorem 4.3, and no prose
   statement of A17.

---

## 8. ANOMALIES VISIBLE IN THE PUBLISHED TEXT

Reported as **observations of the source documents**, image-verified where
marked. **None of these is a claim about HQC, about the model's correctness, or
about anyone's competence**; they are recorded so that a later re-derivation
does not silently pick one reading and call it "the model".

| # | Observation | Verification |
|---|---|---|
| **X1** | Prop 6.1.3's statement has exponent `(1 − p)^(d_i − j)`; the general union-bound expression inside its own proof has `(1 − p)^(n − j)` with n the code length. | SPEC pp.35, 36, both image-verified. |
| **X2** | SPEC Eq. (5) renders `C(d_i, weight − j)` — the literal English word `weight` appears inside a binomial coefficient in the published PDF. The corresponding slot in Prop 6.1.4's statement is `C(d_i, ω − j)`. | SPEC p.37, image-verified. **Not** an extraction artefact. |
| **X3** | SPEC §6.1.3 lead-in says p_i is *"given in Section 6.1.2"*; Theorem 6.1 says *"p_i is defined as in proposition 6.1.3"*; Table 11's column header says *"DFR from 6.1.4"* while its caption says *"the formula from proposition 6.1.3"*. Three cross-references, not all the same. | SPEC pp.38, 39, image-verified. |
| **X4** | SPEC p.38 prose names *"[512, 8, 256] and [640, 8, 320] duplicated Reed-Muller codes"*; SPEC Table 11 directly beneath lists **[384, 8, 192]** and [640, 8, 320]. | SPEC p.38, image-verified. |
| **X5** | Prop 6.1.3 says *"a **duplicated** Reed-Muller code of dimension 8 and minimal distance d_i"*; Prop 6.1.4 says *"a Reed-Muller code of dimension 8 and minimal distance d_i"* (no "duplicated"). | SPEC pp.35, 36, image-verified. |
| **X6** | SPEC §3.4.1 says *"For the external code, we use a Reed-Solomon code of dimension 32 over F256"*, while §3.4.2 and Table 5 use shortened RS codes of dimension **16, 24 or 32** by security level. Separately, RS-S3 is written `[90, 32, 49]` while Table 3 gives δ = 29 for RS-3/RS-S3. | SPEC pp.17, 18 (p.18 image-verified), p.29 image-verified. |
| **X7** | SPEC p.38 proof text switches between `d_i` and an unsubscripted `d` (*"intersect in exactly d/2 positions"*, *"when c and c′ have weight d"*). | SPEC p.38, image-verified. |
| **X8** | Both `p∗` and `p⋆` glyphs are used for the same quantity: §6.1.1 defines `p∗ = P[e′_k = 1]`, Eq. (3) and Tables 9/11 use `p⋆`. Table 9's caption says `p∗` while its column header says `p⋆`. | SPEC pp.32–34, pp.32/33 image-verified. |
| **X9** | SPEC §6.2.2 states the failure event as `ω(x·r₂ − r₁·y + e) > ∆` **"if and only if"**, with ∆ = ⌊(d−1)/2⌋ a bounded-distance quantity, whereas §6.1 computes the failure probability of the **two-stage RM-then-RS decoder** described in §3.4.1 (ML decoding of the inner code, algebraic decoding of the outer). The two are stated in different terms in the same document. | SPEC §3.5, §6.1.3, §6.2.2; text layer plus image-verified §6.1.3. **Recorded as a textual observation only.** |
| **X10** | SPEC §6.3 *Known attacks* discusses ISD, DOOM, and structural/polynomial-factorisation attacks. It does **not** discuss decryption-failure attacks, and Guo–Johansson's *A New Decryption Failure Attack Against HQC* (ASIACRYPT 2020) is **not** in SPEC's reference list. SPEC ref [20] is a different Guo-et-al. paper (the 2022 TCHES rejection-sampling timing attack). | SPEC pp.45–46, pp.48–51, text layer. |

---

## 9. Completeness statement

- The DFR model **was obtained and is transcribed** (§3–§5), with numbered
  assumptions (§6), the source's own hedges (§7), and published-text anomalies
  (§8).
- Every displayed formula in §3, §4, §5.1 is `[IMAGE-VERIFIED]`.
- Exactly one rendering is marked `[EXTRACTION-DAMAGED]`: **SPEC Eq. (13)** in
  §5.3. It carries no claim.
- Figure 3 and Figure 4 are plots; no numeric series is transcribed from them,
  because that would be estimation, not transcription.
- No part of this document was reconstructed from memory.
