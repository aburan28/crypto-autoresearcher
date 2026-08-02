# Proof search for assumption A17 — method, locations checked, outcome

**Task**: `TASK-20260802-15971b` (executor) · **Batch**: `BATCH-002` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-02 · **Repo commit at start**: `7f8a78d47bd35298cd140838381872d65bb2c0f1`
· **Branch**: `claude/goal-target-hqc-launch-vndegi` · **Tree at start**: see §0.4

---

## 0. What this document is

`docs/inventor-protocol.md` §4: *"'we screened N mechanisms and all were
rejected' … is a fatigue report. It is a statement about the search, not about
the problem."* The conclusion in §6 below — that neither primary source proves,
weakens, or acknowledges A17 — is worth exactly as much as the search recorded
here. This file therefore records the **complete location inventory of both
documents**, the **exact commands**, and a **per-location verdict**, including
the locations where nothing was found.

It contains **no security claim about HQC in either direction**, no experiment
design, no hypothesis, and no measurement of HQC. Claim-tier ceiling: **toy**
(`RQ-HQC-001.scope.claim_tier_ceiling`). Certificate: `kind: none` — nothing
here claims a solve or a relation.

### 0.1 Inference

| field | value |
|---|---|
| `requested_policy` | `executor-implementation` |
| `resolved_model_id` | `claude-opus-5` |
| `fallback_used` | **true** — no policy alias in `orchestration/model-policies.yaml` resolves under this Claude Code harness; `.claude/agents/` frontmatter supports only Claude models, so all subagents run `model: inherit` |
| `model_verified` | false — `python3 -m orchestration.adapter doctor --probe` was not run; the adapter is not the runtime here |
| `independent_session` | true |
| `reasoning_effort` | null |

### 0.2 Sources re-acquired and hash-verified before use

Per the handoff, both primary sources were re-acquired from the URLs recorded in
`…/BATCH-001/tasks/TASK-20260802-6344ed/source_access_log.yaml`, and the
recorded sha256 was verified **before** any claim below was based on them.

| key | URL | bytes | sha256 | matches recorded? |
|---|---|---|---|---|
| **SPEC** | `https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf` | 876 126 | `174186cb5fdc0108aad914391360c222f52ea533bfb406146fac124b3a25406d` | **yes, exact** |
| **RMRS** | `https://arxiv.org/pdf/2005.10741` | 525 223 | `cbb7dbd670f27cdcf602438018df52745c0af495050aedb3b83a0b00986f5446` | **yes, exact** |

Fetched `2026-08-02T22:46:25Z`–`22:46:28Z`, `curl -sS -L --max-time 180`, HTTP
200 both. No bot protection was encountered and none was circumvented; no
author was contacted; no paywall was involved (both are author-published /
preprint). Neither PDF is committed (third-party PDF policy, unchanged from
BATCH-001). Downloads live only in the session scratchpad.

Because both hashes are byte-identical to BATCH-001's, **this search is over
exactly the same two documents the transcription was made from.** A negative
here cannot be explained by a different revision of either source.

### 0.3 Tooling

- PyMuPDF 1.28.0 (MuPDF 1.29.0), Python 3.11 — `page.get_text("text")` over all
  51 SPEC pages and all 14 RMRS pages, dumped to `spec.txt` / `rmrs.txt` with
  page markers, then indexed into a page→text map.
- Document outline read via `doc.get_toc()` for both, to enumerate every
  section and confirm there is no section the linear scan skipped.
- Regex sweeps with `re.finditer(..., re.I)` reporting **per-page hit counts**,
  so an absent term is recorded as an absence over the whole document rather
  than as a failure to look.
- Exact/high-precision arithmetic (`fractions.Fraction`, `decimal` at 300–400
  digits) for the numeric checks in §7.

**Limitation, stated up front.** This search is over the **text layer**. Linear
extraction mangles displayed mathematics, and BATCH-001 image-verified the
formulas for that reason. A *proof of A17* would be prose plus displayed
mathematics; prose survives text extraction intact, and the structural markers a
proof would carry (`Proof`, `Lemma`, `Remark`, `Appendix`, section headings)
are all plain text and are enumerated exhaustively in §3 and §4. I did **not**
render any page as an image in this task. What that limitation could hide: a
proof typeset entirely as displayed mathematics with no prose and no `Proof`
marker. I regard that as implausible but it is not excluded, and it is the one
route a reviewer could take to overturn §6.

### 0.4 Prohibitions — positive confirmation

| item | value |
|---|---|
| experiment designed (protocol / parameters / trial counts / seeds / success criterion / measurement plan) | **false** |
| decoding trial or numerical simulation of HQC run | **false** |
| writes outside `…/tasks/TASK-20260802-15971b/` | **false** |
| `knowledge/`, `ledger/`, or the sibling task's directory touched | **false** |
| state-mutating git command run | **false** (`git rev-parse HEAD`, `git status --porcelain`, `git branch --show-current` only) |
| bot protection circumvented / author contacted | **false** |
| security claim about HQC made in either direction | **false** |
| third-party PDF committed | **false** |

`git status --porcelain` at start reported no modifications to tracked files
(clean tree at `7f8a78d4`); the only tree change this task makes is the three
new files in its own task directory.

---

## 1. What would have counted as a find

Declared **before** searching, so that a weaker find cannot be retro-fitted into
"acknowledgment".

| tier | what it would be | verdict |
|---|---|---|
| **T1 — proves** | a proof, lemma, proposition, or cited external theorem establishing that the `n_e` inner-decoder failure events are independent (or that their joint law is dominated by the independent one) under the *true* HQC error distribution | **not found in either source** |
| **T2 — weakens** | a statement replacing independence by a weaker sufficient condition (negative association, negative orthant dependence, a martingale/Chernoff argument, a union bound over blocks) that is then established | **not found in either source** |
| **T3 — acknowledges** | prose naming the step: "we assume the block failures are independent", "we model the outer channel as memoryless", or any hedge attached to the passage from `p_i` to the concatenated DFR | **not found in either source** (nearest misses in §5) |
| **T4 — evidence** | a simulation, figure, or table addressing the *joint* behaviour of two or more inner blocks | **not found in either source** |

---

## 2. The object searched for, in one line

Theorem 6.1 (SPEC p.38–39) / Theorem 4.3 (RMRS p.12) assert

```
DFR  <=   sum_{l = delta_e+1}^{n_e}  C(n_e, l) * p_i^l * (1 - p_i)^{n_e - l}
```

The summand is the binomial pmf. The only route by which the number of failed
inner blocks has a binomial law is that the `n_e` inner-decoder outcomes are
independent and identically distributed. That is A17. The formal statement and
its distinguishable readings are in `a17_characterization.md` §2.

---

## 3. SPEC — complete location inventory

51 pages. Outline read via `get_toc()`; every listed section is accounted for
below. Sections with no possible bearing on A17 are listed anyway, marked
`n/a`, so that "not searched" is never confused with "searched, nothing there".

| SPEC location | pages | bearing | verdict |
|---|---|---|---|
| 1 Introduction | 6 | n/a | — |
| 2.1 Notations | 7 | n/a | — |
| 2.2 Coding theory (incl. Def 2.2.5, `∆ = ⌊(d−1)/2⌋`) | 7–9 | defines ∆ used by A20 | no independence statement about blocks |
| 2.3 Security assumptions | 9–11 | contains 2 `independen*` hits (p.9) | **both about the DSD problem's error model** (*"random errors are often taken as independent Bernoulli variables acting independently on vector coordinates"*) and one on p.10 about circulant submatrices. Neither concerns decoder blocks. |
| 2.4 Security definitions | 11–13 | n/a | — |
| 3.1 XOF and Hash | 13 | n/a | — |
| 3.2 Vector sampling | 13–14 | source of A1/A22 | no block statement |
| 3.3 Vector multiplication | 14–17 | n/a | — |
| **3.4 Concatenated Reed-Muller and Reed-Solomon codes** | **17–22** | **the construction A17 is about** | 3.4.1 defines the concatenation and says *"We perform maximum likelihood decoding on the internal code. Doing that, we obtain a vector of F_q^{n_e} that is then decoded using an algebraic decoder for the Reed-Solomon code."* **No statement about the joint law of the `n_e` inner outcomes.** 3.4.2 gives RS parameters, generator polynomials, Berlekamp syndrome decoding (source of A18). 3.4.3 gives duplicated-RM Hadamard decoding (source of A12). |
| 3.5 HQC-PKE (incl. *Correctness*) | 22–26 | source of A20 | states the `ω(·) ≤ ∆` condition; no block statement |
| 3.6 HQC-KEM | 26–29 | n/a | — |
| 4 Parameters and Sizes (Tables 4, 5) | 29–30 | supplies `n_e, δ_e, d_i` | no prose |
| 5 Performance Analysis | 30–31 | n/a | — |
| **6.1 opening paragraph** | **32** | **the section map** | verbatim: *"We analyze the distribution of the error vector e′ … in Section 6.1.1 and the Decoding Failure Rate (DFR) of the internal Reed-Muller code in Section 6.1.2. **The resulting DFR of the scheme is studied in Section 6.1.3.**"* The word *"resulting"* is the **entire logical connective** offered for the inner→scheme step. Nearest miss #2 (§5). |
| **6.1.1 Analysis of the error vector distribution** | **32–34** | source of A5, A6, A7 | 3 `independen*` hits on p.32 and 6 on p.33: all are about (i) the coordinates of `e′` (A5) or (ii) the input vectors `x, y, r₁, r₂, e` (A1–A4). **None is about inner-decoder blocks.** Props 6.1.1, 6.1.2 proved. Simulations (Tables 9, 10; Fig. 3) are about the **global** weight of `e′`. |
| **6.1.2 DFR of the internal code** | **35–38** | Props 6.1.3, 6.1.4 | both **proved**, both about **one** inner block. Zero `independen*` hits on pp.35–38. Table 11 is a single-block simulation. |
| **6.1.3 Decoding failure rate analysis** | **38–39** | **the site of A17** | **Two sentences of prose, one theorem statement, and one simulation paragraph. NO PROOF.** Full prose: *"Using the lower bound p_i on the decoding probability of the Reed-Muller codes given in Section 6.1.2, one can deduce the DFR of the concatenated code used in HQC."* then Theorem 6.1, then *"Simulation results."* Zero `independen*` hits. Zero `Proof` tokens (§4). |
| 6.2 Security proof, 6.2.1 IND-CPA | 40–43 | n/a to A17 | 1 `independen*` hit p.40 and 2 p.43, all about `cPKE` being independent of the challenge bit `b` |
| **6.2.2 IND-CCA2 (Def 6.2.1, Eqs 9/11/12, Thm 6.3)** | **43–44** | the δ join (A20, A21) | δ enters `Adv^{IND-CCA2}` as the additive term `(q_RO + q_D)·δ`. No block statement. |
| 6.2.3 Non-uniform sampling (Prop 6.2.1, Lemma 6.4, Table 12) | 44–45 | A22 | multiplies δ by at most `(τ^{ω_r}_max)³`; no block statement |
| 6.3 Known attacks | 45–47 | n/a | 1 `independen*` hit, unrelated |
| 7 Advantages and Limitations | 47 | checked for a self-assessment of the DFR model | nothing about block independence |
| References | 47–51 | see §4.3 | — |

**SPEC contains no appendix.** `/Appendix/` → **0 hits over all 51 pages**.

---

## 4. SPEC — structural-marker sweep

The point of this sweep: a proof of A17, if present, would carry a structural
marker. Every marker in the document is enumerated and each one is resolved.

```
/Theorem 6\.1\b/   -> p.38 x1 (statement lead-in), p.39 x2
/Proof/            -> p.33 x1, p.35 x1, p.36 x1, p.40 x1     [4 total, whole document]
/Lemma/            -> p.44 x1, p.45 x2                       [Lemma 6.4 only, about the sampler]
/Remark/           -> 0 hits, whole document
/Appendix/         -> 0 hits, whole document
/footnote/         -> 0 hits, whole document
```

Resolving all four `Proof` tokens in the specification:

| page | proves | about A17? |
|---|---|---|
| 33 | Proposition 6.1.1 (per-coordinate law of `x·r`) | no |
| 35 | Proposition 6.1.3 (simple inner-code bound) | no — one block |
| 36 | Proposition 6.1.4 (improved inner-code bound) | no — one block |
| 40 | Theorem 6.2 (IND-CPA) | no |

**There is no fifth proof.** Theorem 6.1 — the only result in the specification
that uses A17 — is stated without proof, and the pages surrounding it (38, 39)
contain no `Proof`, `Lemma`, `Remark`, `Appendix`, or footnote marker.

### 4.1 Keyword sweep, SPEC (whole document, case-insensitive)

| pattern | total | pages |
|---|---|---|
| `independen` | 16 | 9×2, 10, 32×3, 33×6, 40, 43×2, 45 |
| `i.i.d` | **0** | — |
| `iid` (word) | **0** | — |
| `identically` | **0** | — |
| `correlat` | **0** | — |
| `binomial` | 13 | 32, 33, 34×8, 35, 37, 39 |
| `concatenat` | 15 | 3, 5, 11, 17×5, 22, 29, 38×3, 39×2 |
| `assum` | 11 | 5, 9, 32×3, 33, 36, 40×3, 50 |
| `simplif` | 3 | 32, 33, 43 |
| `modeliz` | 3 | 3, 32, 34 |
| `bounded distance` | **0** | — |
| `plug` | 1 | 38 (*"Plugging 6, 5 and 7 into 4"* — inside the Prop 6.1.4 proof) |
| `symbol` | 1 | 17 |
| `union bound` | 2 | 36, 37 |

**Every one of the 16 `independen` hits was read in ±260 characters of context
and classified.** None concerns the joint law of inner-decoder outcomes. The
words `i.i.d.`, `iid`, `identically`, and `correlat*` **do not occur anywhere in
the 51-page specification**.

The single `binomial` hit on p.39 is in the caption of Figure 4 (the series
label *"Binomial"* for a BSC-simulated DFR curve); it is a plot label, not a
statement about block independence, and §5.4 explains why the figure does not
constitute T4 evidence.

---

## 5. SPEC — the three nearest misses, and why each falls short

Recorded because the honest form of a negative is to state what the source
*does* say at the site, not merely that it does not say the thing sought.

**Nearest miss #1 — RMRS p.9 (carried here because SPEC has no counterpart).**
See §6.2. SPEC has **no** sentence at all describing the inner→outer transfer;
the RMRS sentence is the only prose in either document that names the operation.

**Nearest miss #2 — SPEC p.32, §6.1 opening:** *"The **resulting** DFR of the
scheme is studied in Section 6.1.3."* This is a section map, not a claim. The
adjective *"resulting"* asserts that a scheme DFR follows from the inner DFR; it
does not say by what step, and it attaches no hedge. Under the T1–T4 ladder it
is below T3, because it does not name the assumption it is exercising.

**Nearest miss #3 — SPEC p.38, §6.1.3 lead-in:** *"Using the lower bound `p_i`
on the decoding probability of the Reed-Muller codes given in Section 6.1.2, one
can deduce the DFR of the concatenated code used in HQC."* This is the closest
thing in the specification to a derivation sentence for Theorem 6.1. It names
the input (`p_i`), asserts that a deduction exists (*"one can deduce"*), and
supplies neither the deduction nor the property of the `n_e` outcomes that the
deduction requires. Below T3 for the same reason.

**§5.4 — Figure 4 is not T4 evidence.** SPEC Fig. 4 (p.39) plots three DFR
series against `NRS ∈ [32, 36]`: `Theoretical` (Theorem 6.1), `Binomial` (a
concatenated-code DFR simulated against a **binary symmetric channel**), and
`HQC` (simulated against real HQC error vectors). The `Binomial` series is
generated *under* A5/A17 rather than testing them; the `HQC` series is the only
one that could bear on A17. However: (i) the figure supplies no numeric series
and BATCH-001 correctly declined to read values off a rendered plot; (ii) it is
at `NRS = 32…36` and `k_e = 16` with a `[384,8,192]` inner code, whereas the
deployed sets are `n_e ∈ {46, 56, 90}`; and (iii) a DFR curve is a **first
moment** of `S = Σ_j F_j` past a threshold, at DFR ≈ 2⁻²² to 2⁻², whereas A17's
load-bearing content is a `(δ_e+1)`-way joint moment at DFR ≈ 2⁻¹³³ to 2⁻²⁶¹
(`a17_sensitivity.yaml`, derivation step 2). A curve at that depth cannot
discriminate the hypotheses; it is consistent with a wide family of joint laws.
**Recorded as: a figure exists at the right conceptual place, and it does not
constrain the quantity A17 is load-bearing for.** No claim is made here about
what the figure shows, since no value was read from it.

---

## 6. RMRS (arXiv:2005.10741) — complete location inventory

14 pages, two sections of relevance. Outline read via `get_toc()`.

| RMRS location | pages | verdict |
|---|---|---|
| 1 Introduction | 1–2 | 1 `independen*` hit, about the HQC framework's security reduction being independent of the auxiliary decoder. Not A17. |
| 2 Preliminaries | 2–3 | n/a |
| 3 Analysis of the error vector distribution | 3–4 | contains the A5 sentence, **verbatim identical to SPEC's** except that SPEC adds *"In other words we modelize the error vector as a binary symmetric channel with parameters p∗"*. |
| 3.1 Distribution of the product of two vectors (Prop 3.1.1) | 4–5 | proved; per-coordinate |
| 3.2 Analysis of `e′` (Prop 3.2.1) | 5 | proved; per-coordinate. 8 `independen*` hits on p.5, **all** about `x·r₂`, `r₁·y`, `e` being mutually independent (A1–A4) or about the coordinates of `e′` (A5). |
| **3.3 Supporting elements for our modelization** | **6–8** | **the entire evidence base RMRS offers for A5.** Figures 2, 3 and Tables 1, 2, 3 compare the **global** weight distribution of `e′` (lengths `n₁n₂` = 23 746 and 20 480) against the binomial. **Nothing here examines two or more decoder blocks jointly.** |
| 4.1 Construction | 8–9 | defines the concatenation and the Hadamard inner decoder. **No statement about the joint law of inner outcomes.** |
| **4.2 Decryption failure rate analysis** | **9–12** | Props 4.2.1, 4.2.2 both **proved**, both single-block. Remarks 4.1, 4.2 both **precede** Theorem 4.3 and are both about the **internal** code. **Theorem 4.3 is stated with NO PROOF and NO citation.** |
| 4.3 Simulation results | 12–13 | Figure 5: concatenated-code DFR vs `NRS ∈ [54, 64]`, two series (`Binomial`, `HQC-RMRS`). Same three limitations as SPEC Fig. 4 (§5.4). |
| 4.4 Proposed parameters | 13 | table only |
| 5 Conclusion | 13 | *"In Section 4 we propose using a concatenation … and we provide an upper bound on the DFR in this setting."* No hedge attached to the concatenation step. |
| References | 14 | **exactly two entries** — see §6.3 |

**RMRS contains no appendix.** `/Appendix/` → **0 hits over all 14 pages**.

### 6.1 RMRS — structural-marker sweep

```
/Theorem 4\.3/  -> p.12 x1   (the statement; nothing follows it but section 4.3)
/Proof/         -> p.4 x1, p.5 x1, p.9 x1, p.10 x1     [4 total, whole document]
/Lemma/         -> 0 hits, whole document
/Remark/        -> p.12 x2   (Remarks 4.1 and 4.2, both BEFORE Theorem 4.3)
/Appendix/      -> 0 hits, whole document
```

Resolving all four `Proof` tokens: Prop 3.1.1 (p.4), Prop 3.2.1 (p.5), Prop
4.2.1 (p.9), Prop 4.2.2 (p.10). **There is no fifth.** Theorem 4.3 has no proof.

### 6.2 RMRS — the nearest miss, and it is the closest either source comes

**RMRS p.9, §4.2 opening, verbatim:**

> "We first provide two bounds on the maximum likelihood decoding error
> probability of the duplicated Reed-Muller code: a first simple union bound and
> a second more accurate one. **These bounds can then be plugged into the
> decoding error probability for the bounded distance decoder of the
> Reed-Solomon code.**"

This is the **only sentence in either document** that describes the operation
A17 licenses. It is a T3-adjacent near miss and it still falls short, for a
reason worth stating precisely: *"plugged into the decoding error probability
for the bounded distance decoder"* **presupposes** that such a decoding error
probability is a function of the single number `p_i`. It is a function of `p_i`
alone exactly when the block failures are i.i.d.; otherwise it is a function of
the whole joint law. The sentence therefore **exercises** A17 without naming it,
which is the third of the three categories the handoff asks to be kept apart:
not proved, not asserted, **silently assumed**.

The phrase `bounded distance` occurs **once in RMRS and zero times in SPEC** —
so the specification does not even carry this much.

### 6.3 RMRS — reference-list check (could the proof be cited elsewhere?)

RMRS has **exactly two references**:

- `[1]` Aguilar-Melchor, Blazy, Deneuville, Gaborit, Zémor, *Efficient encryption
  from random quasi-cyclic codes*, IEEE Trans. IT 64(5):3927–3943, 2018.
  Back-references printed by the bibliography: pages **2, 3, 4, 6, 7, 8, 14**.
- `[2]` MacWilliams & Sloane, *The theory of error-correcting codes*, 1977.
  Back-reference: page **9** only — and the p.9 citation is *"can be decoded
  using a fast Hadamard transform (see chapter 14 of [2])"*, i.e. it supports
  the **inner decoding algorithm**, not the concatenation step.

**Neither reference is cited on pages 10, 11 or 12** — the pages carrying the
Prop 4.2.2 proof and Theorem 4.3. So Theorem 4.3 is supported by no proof and by
no citation, in a paper with a two-item bibliography where that is checkable
exhaustively.

**SPEC side.** SPEC §6.1.1 opens *"following [4]"*, and `[4]` is RMRS (recorded
in BATCH-001 from SPEC's own reference list). SPEC §3.4 opens *"instantiated
using concatenated Reed-Muller and Reed-Solomon codes as described in [4]"*.
So SPEC's Theorem 6.1 points at RMRS's Theorem 4.3, and RMRS's Theorem 4.3
points at nothing. **The citation chain for A17 terminates without a proof.**
This is the named obstruction the closure standard asks for: it is not that a
proof was not located, it is that the chain is two links long and both links are
exhausted.

### 6.4 Keyword sweep, RMRS (whole document, case-insensitive)

| pattern | total | pages |
|---|---|---|
| `independen` | 12 | 1, 4×3, 5×8 |
| `i.i.d` | **1** | **12** — see §6.5 |
| `iid` (word) | **0** | — |
| `identically` | **0** | — |
| `correlat` | **0** | — |
| `binomial` | 22 | 4, 5, 6×8, 7×5, 8×2, 12, 13×3, 14 |
| `assum` | 5 | 4×3, 5, 10 |
| `bounded distance` | **1** | 9 (§6.2) |
| `plug` | 2 | 9 (§6.2), 12 (*"Plugging 9, 8 and 10 into 7"*, inside the Prop 4.2.2 proof) |
| `union bound` | 3 | 9, 10, 11 — all inside Props 4.2.1/4.2.2, all over **RM codewords within one block** |
| `block` | 2 | 6 (*"blocksize of the double circulant code"*), 9 (*"every block of three bits"* — bit-duplication) |

The word `block` **never** denotes a concatenation block in RMRS. Neither
document has a name for the object A17 is about.

### 6.5 The single `i.i.d.` in either source — and why it is not A17

**RMRS Remark 4.2, p.12, verbatim:**

> "Propositions 4.2.1 and 4.2.2 have been derived with a binary symmetric channel
> model for the distribution of the HQC error vector **restricted to the support
> of a (duplicated) Reed-Muller code**. Figure 4 compares the actual weight
> distribution of the error vector to the binomial distribution when restricted
> to this relatively small number of bits. We observe that they are virtually
> identical, meaning that **a small proportion of HQC bits do behave as i.i.d
> Bernoulli variables**."

This is the one place either document writes `i.i.d.`, and BATCH-001 was right
to record it (H8). It is **evidence for A5 restricted to one block** — i.e. it
supports the marginal input to Props 4.2.1/4.2.2 — and it is stated for a
**support length of 256** (Fig. 4 caption: parameter set II, *"the support length
is 256"*), a **single** RM block.

It is not evidence for A17, and the remark's own wording is what rules it out:
*"a **small proportion** of HQC bits"*. A17 needs the **joint** law across all
`n_e` blocks, i.e. **all** `n₁n₂` used bits at once — 17 664 to 57 600 bits, not
256. The remark is scoped, correctly, to the regime where it was checked, and
that scope excludes A17's use. Recorded as **T3 for A5, not for A17**.

---

## 7. Zero-cost arithmetic checks run alongside the search

Run because `docs/inventor-protocol.md` §8 audit 1 (exact baseline reproduction)
applies to any claim about how a bound moves, and because the sensitivity
derivation needs the published chain reproduced first. Exact rationals /
400-digit decimals; **no decoding trial, no simulation, no randomness**.

**7.1 Baseline reproduction.** Evaluating the transcribed Prop 6.1.1 → Eq. (2) →
Prop 6.1.3/6.1.4 → Theorem 6.1 chain at the SPEC Table 5 parameters:

| set | `p⋆` computed | SPEC Tables 9/11 | `log₂ p_i` (6.1.4) | SPEC Table 11 | `log₂` Theorem 6.1 |
|---|---|---|---|---|---|
| HQC-1 | 0.33978837 | 0.3398 | −10.7950 | −10.79 | **−132.892** |
| HQC-3 | 0.36180358 | 0.3618 | −14.1374 | −14.14 | **−193.861** |
| HQC-5 | 0.37248858 | 0.3725 | −11.3240 | −11.30 | **−260.597** |

Reproduces the specification's published digits, independently of the BATCH-001
red team's control C8.

**7.2 A 0.03–0.09-bit discrepancy against the red-team recomputation, explained.**
`TASK-20260802-73a352` §3 reported Theorem 6.1 at 2⁻¹³²·⁸⁶ / 2⁻¹⁹³·⁸⁸ /
2⁻²⁶⁰·⁵¹; I get −132.892 / −193.861 / −260.597. Re-running the chain with
SPEC's **published four-digit** `p⋆` (0.3398 / 0.3618 / 0.3725) instead of the
exact recomputed `p⋆` yields **−132.856 / −193.878 / −260.512**, matching the
red team to the digits it printed. **The two computations agree; the difference
is entirely the rounding of `p⋆` at the fourth decimal.** Recorded because it
also quantifies something useful: a fourth-digit rounding of `p⋆` moves the
stage-3 bound by up to **0.085 bits**, so any statement about the bound at
sub-0.1-bit resolution must say which `p⋆` it used.

**7.3 Deep-tail check** (needed by derivation step 2 in `a17_sensitivity.yaml`):
the `l = δ_e + 1` term's share of the full Theorem 6.1 tail is **0.999006**
(HQC-1), **0.999880** (HQC-3), **0.999245** (HQC-5).

**7.4 Null-object measurements** (used by `a17_characterization.md` §5):
`log₂(255/254) = 0.005669` bits (A10); the `min[C(n,ω), …]` cap of Prop 6.1.4
(A16) is active in 219/289 (HQC-1) and 354/481 (HQC-3, HQC-5) summands and moves
`p_i` by **0.3744** / **0.2898** bits.

**7.5 Published-dispersion extraction** (used by derivation step 7): implied
variance ratios `γ = Var(ω(ẽ)) / (N p⋆(1−p⋆))` from the published quantile
tables under a Gaussian interpolation — SPEC Table 10: 0.735, 0.736, 0.733,
0.725 at the 10⁻³…10⁻⁶ tails; RMRS Table 2: 0.631, 0.619, 0.613, 0.614; RMRS
Table 3: 0.676, 0.673, 0.674, 0.685. Stable across four tail depths in all three
tables. **Derived from published summary statistics, not measured here**; the
Gaussian interpolation is an approximation and is labelled as such wherever used.

---

## 8. Outcome per source

| source | proves A17 (T1) | weakens it (T2) | acknowledges it (T3) | joint evidence (T4) |
|---|---|---|---|---|
| **SPEC** (51 pp., all sections enumerated §3, all 4 `Proof` tokens resolved §4, 0 appendices, 0 remarks, 0 footnotes) | **no** | **no** | **no** — nearest is *"one can deduce"* (p.38) and *"the resulting DFR"* (p.32) | **no** — Fig. 4 does not constrain the load-bearing quantity (§5.4) |
| **RMRS** (14 pp., all sections enumerated §6, all 4 `Proof` tokens resolved §6.1, 0 appendices, 2-item bibliography exhausted §6.3) | **no** | **no** | **no** — nearest is *"plugged into the decoding error probability for the bounded distance decoder"* (p.9, §6.2), which exercises the assumption without naming it | **no** — Remark 4.2's `i.i.d.` is single-block and self-scoped to *"a small proportion of HQC bits"* (§6.5) |

**The negative is a searched negative, and the obstruction is named:** SPEC's
Theorem 6.1 cites RMRS; RMRS's Theorem 4.3 cites nothing and proves nothing; the
citation chain is two links long and exhausted; the words `i.i.d.`,
`identically` and `correlat*` are absent from the specification entirely; and
neither document possesses a *word* for a concatenation block.

**Bounds on this negative, stated plainly.** It covers exactly these two
documents at these two hashes. It does not cover: the HQC reference/optimised
implementation and its comments; the NIST submission-package archives and the
PQC-conference presentation archives linked from `pqc-hqc.org/resources.html`
(BATCH-001 attempt 3 recorded them as linked and not downloaded); earlier HQC
specification revisions; `[1]` Aguilar-Melchor et al. 2018, which carries the
predecessor BCH⊗repetition DFR analysis and is **not in this program's corpus**;
or the wider concatenated-coding literature, where a general theorem about
concatenated-code error probability under a memoryless inner channel would be
unsurprising to exist. Any of those could contain a T1/T2/T3 item. **What is
established is that the two documents this program identified as the model's
primary carriers do not contain one.**

---

## 9. Incidental observations (recorded, not acted on)

`AGENTS.md` rule 8 — unexpected observations are recorded, not discarded. None
of these is in this task's scope and none is acted on here.

**9.1 — `[80, 32, 49]` in RMRS.** RMRS Figure 6 (p.14) proposes
`HQC-RMRS-128` with an external Reed-Solomon code `[80, 32, 49]`. That code is
MDS (`80 − 32 + 1 = 49`), so the value 49 is correct **there**. This is relevant
context for the sibling correction `CORR-20260802-3ae664` (RS-S3 `49 → 59`): the
digit 49 is a real published RS minimum distance in the RMRS lineage for a
*different* code, which makes it a more attractive misread than a random digit.
It does not weaken the correction — `90 − 32 + 1 = 59` and `2·29 + 1 = 59` both
stand, and I confirmed both here. **Disposition belongs to `TASK-20260802-63b16a`
and to the Coordinator; nothing is written to that task's scope from here.**

**9.2 — SPEC Eq. (13) text layer.** For the A17 load-bearing trace (duty 4) I
read SPEC p.44's **text layer** to confirm how δ enters `Adv^{IND-CCA2}`. The
four summands and their structure agree with BATCH-001's transcription. **I did
not render p.44 as an image, and I do NOT claim to discharge the
`[EXTRACTION-DAMAGED]` marker** — image verification and the `D-6` citation fix
are `TASK-20260802-63b16a`'s scope. Recorded only so that the trace in
`a17_characterization.md` §4 names its basis.

**9.3 — X9 is visible from the A17 site.** The event `ω(x·r₂ − r₁·y + e) > ∆`
that SPEC §6.2.2 declares equivalent to decryption failure *"if and only if"*
is **not** the event `S > δ_e` that Theorem 6.1 bounds, and the two are related
by neither containment direction in general. This is BATCH-001's X9 and the red
team's second-ranked lead. It is treated in `a17_characterization.md` §6 as a
**competing target**, not resolved here.

---

## 10. Reproducibility

Everything above re-runs from: the two URLs and hashes in §0.2; PyMuPDF 1.28.0
text extraction; the regex list in §4.1/§6.4; and the arithmetic in §7, which
uses only `math.comb`, `fractions.Fraction` and `decimal` at 400 digits over the
formulas transcribed in
`…/BATCH-001/tasks/TASK-20260802-6344ed/dfr_model_transcription.md` §3–§5 with
the `d = n − k + 1` correction to RS-S3 (`δ_e = 29` at HQC-5) already applied by
`BATCH-002-OPENING.md` §3. **No seed, no randomness, no sampling and no simulation is involved anywhere in
this task.** The identity check in `a17_sensitivity.yaml` derivation step 1
(Jordan's inclusion–exclusion, verified to 10⁻¹⁵ on an 8-variable exchangeable
mixture with the three fixed mixing values `Q ∈ {0.1, 0.4, 0.9}`) is a
**deterministic** evaluation of two closed forms of the same combinatorial
identity; it involves no HQC object and draws nothing at random.
