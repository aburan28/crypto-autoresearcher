# Cascade cost note — what `[35, Theorem 1]` and `[35, Proposition 8.5]` cost

**Task:** `TASK-20260805-c89efb` (REC-2) · **Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-002`
**Role:** executor · **Repairs recorded defect:** `GD-1` (`ledger/goals/GOAL-SSIQ-001/goal.yaml`)
**Date (UTC):** 2026-08-05 · **Repo commit at time of work:** `ab8e3ad8f93b84f197aef647746a36ef0d7cd359` (clean tree)

## 0. Scope and what this note is not

This is an **observation record**. It states what the sources say the reductions
cost, with locators, and states explicitly where a cost is not assigned. It does
**not** assess whether the cascade threatens, helps, or changes any condition
derived in `BATCH-001`; that judgement belongs to the Red Team
(`TASK-20260805-538c72`) and the Coordinator.

Nothing in this note asserts, implies, or supports the existence or nearness of a
p^{1/4} algorithm. **0.25 is a target of `GOAL-SSIQ-001`, not a claim.**

No hypothesis is minted here, no ledger record is edited, no record status is
changed, and no compute beyond fetching and text extraction was performed.

---

## 1. Identification of `[35]`, from the frozen source's own reference list

`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, line 328, verbatim:

> [35] Aurel Page and Benjamin Wesolowski. "The Supersingular Endomorphism Ring
> and One Endomorphism Problems are Equivalent". In: EUROCRYPT 2024, Part VI.
> Vol. 14656. LNCS. Springer, 2024, pp. 388–417. doi: 10.1007/978-3-031-58751-1_14.

The frozen reference entry names **the EUROCRYPT 2024 proceedings version**, by
volume, page range (388–417) and DOI. It names **no** ePrint or arXiv identifier.
The identifiers `iacr:2023/1399` and `arXiv:2309.10432` used below come from this
repository's own corpus entry `knowledge/literature/KN-LIT-131.md`, **not** from
the frozen text; they are labelled as such wherever used.

## 2. Where the frozen source uses `[35]`

`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, line 21, verbatim:

> As an immediate corollary, applying the computational reductions [35, Theorem 1]
> and [35, Proposition 8.5], we deduce the following consequences.

Line 23, verbatim:

> **Corollary 1.2.** Assuming Heuristic 1, there is a Las Vegas algorithm of
> expected complexity p^{1/3+o(1)} for the supersingular endomorphism ring problem
> (given E supersingular, find a basis of End(E) — see Problem 2.3) and for the
> supersingular isogeny problem (given E and E′ supersingular, find an isogeny
> E → E′ — see Problem 2.4).

The theorem those reductions are applied to is line 19, verbatim:

> **Theorem 1.1.** Assuming Heuristic 1, there is a Las Vegas algorithm which,
> given a supersingular elliptic curve E/F_{p^2}, finds a non-scalar endomorphism
> α ∈ End(E) \ Z in expected time and memory p^{1/3+o(1)}.

The three problems, from the frozen text (lines 119, 123, 125): Problem 2.2
(**OneEnd**), Problem 2.3 (**EndRing**), Problem 2.4 (**Isogeny**). Frozen line 117
states Theorem 1.1 is about Problem 2.2; frozen line 121 states Corollary 1.2 is
about Problems 2.3 and 2.4. So the cascade the goal's target rides on is:

```
Isogeny  --[35, Proposition 8.5]-->  EndRing  --[35, "Theorem 1"]-->  OneEnd
                                                                        |
                                             frozen Theorem 1.1 (Heuristic 1):
                                                        p^{1/3+o(1)} time & memory
```

## 3. What was obtained, and a numbering discrepancy that must be recorded

Three renderings of `[35]` were obtained (full access log with URLs, HTTP status,
timestamps and SHA-256: `source_access_log.yaml`):

| rendering | provenance | SHA-256 (prefix) | pages | numbering of the two cited results |
|---|---|---|---|---|
| **EUROCRYPT 2024 proceedings chapter** (the version `[35]` names) | `link.springer.com/content/pdf/10.1007/978-3-031-58751-1_14.pdf`, 200 OK, full 30-page chapter, pp. 388–417 | `55c054a8…` | 30 | **Proposition 8.5** = "Isogeny reduces to EndRing"; **Theorem 8.6** = "EndRing reduces to Isogeny"; **Theorem 1.1** = the equivalence; **Theorem 7.2** = the precise EndRing→OneEnd reduction |
| author full version, HAL v2 (produced 2024-05-26, cites the EUROCRYPT pages) | `inria.hal.science/hal-04209824/document`, 200 OK | `97d80b8e…` | 54 (incl. HAL cover) | Proposition **8.4** = "Isogeny reduces to EndRing"; Theorem **8.5** = "EndRing reduces to Isogeny"; Theorem 1.1; Theorem 7.2 |
| preprint, arXiv:2309.10432v2 (16 Oct 2023; corpus-supplied identifier) | `arxiv.org/pdf/2309.10432`, 200 OK | `afa0ad19…` | 53 | same as HAL v2 |

**IACR ePrint 2023/1399 was NOT obtained.** Both attempts on
`https://eprint.iacr.org/2023/1399.pdf` returned **HTTP 403** with a Cloudflare
"Just a moment…" managed-challenge HTML body (origin-side bot challenge; the agent
proxy reported no relay failure). This is an **infrastructure outcome**, not a
mathematical finding. Recorded as unobtained.

### 3.1 `Proposition 8.5` — matched exactly

The citation `[35, Proposition 8.5]` matches the **proceedings** version exactly,
in number *and* in direction. In the author full version the same statement is
numbered Proposition **8.4**. This corroborates that `[35]` resolves to the
proceedings chapter, as its reference entry says.

### 3.2 `Theorem 1` — no literal match in any obtained rendering

**No obtained rendering of `[35]` contains a result numbered "Theorem 1".** The
proceedings numbers its main theorem **Theorem 1.1** (p. 389) and has, in order,
Theorem 1.1, Theorem 1.3, Theorem 4.2, Theorem 7.2, Theorems 8.1/8.2/8.6/8.8; a
literal string "Theorem 1" occurs in the proceedings only inside a citation to a
*different* paper (`[DKL+20, Theorem 1]`, p. 389).

Two candidate readings are recorded, and **this task does not resolve between
them**:

- **(a)** `[35, Theorem 1]` is shorthand for `[35, Theorem 1.1]`. Supporting fact:
  Theorem 1.1 is the equivalence EndRing ≡ OneEnd, which is the direction
  Corollary 1.2 needs, and its companion citation `Proposition 8.5` resolves to
  the same document under the same numbering scheme.
- **(b)** the intended target is `[33, Theorem 1]`. Supporting fact: reference
  `[33]` (Herlédan Le Merdy–Wesolowski, TCC 2025 — frozen line 326) **does**
  contain a literal "**Theorem 1**", stating that Isogeny, EndRing, MaxOrder,
  MaxOrder_Q, HomModule, OneEnd and MOER "are all equivalent under probabilistic
  polynomial time reductions", and frozen line 127 describes `[33]` as
  "a larger network of unconditional equivalencies". `[33]` was obtained (HAL
  hal-04954150, SHA-256 `6d8d0c83…`); see §6.

Both readings are costed below, because under either reading the reduction the
cascade needs is the EndRing→OneEnd (resp. Isogeny→OneEnd) direction.

---

## 4. `[35, Proposition 8.5]` — Isogeny reduces to EndRing

### 4.1 What it does

Proceedings chapter, **p. 413**, § 8.3, verbatim (independently reproduced by
three extractors — poppler `pdftotext`, `pdfminer.six`, PyMuPDF; see
`extractor_unblock_log.md`):

> **Proposition 8.5 (Isogeny reduces to EndRing).** Assuming the generalised
> Riemann hypothesis, the problem Isogeny_λ reduces to EndRing in probabilistic
> polynomial time (with respect to the length of the instance), for some function
> λ(log p) = O(log p).

Its complete proof, same page, verbatim:

> *Proof.* Isogeny immediately reduces to ℓ-IsogenyPath. It is already known that
> the ℓ-isogeny path problem (with paths of length O(log p)) is equivalent to
> EndRing [Wes22b], so Isogeny_λ reduces to EndRing. □

`Isogeny_λ` is defined on p. 413: the Isogeny problem where the returned φ must
satisfy `log(deg φ) ≤ λ(log p)`. `[Wes22b]` is Wesolowski, FOCS 2021, "The
supersingular isogeny path and endomorphism ring problems are equivalent"
(= `[45]` of the frozen source).

### 4.2 What it multiplies the complexity by

- **Assigned cost class:** a factor **polynomial in the instance length**, i.e.
  **(log p)^{O(1)}**, on a *probabilistic* (expected-time) reduction.
- **Assigned parameter:** λ(log p) = O(log p).
- **Degree of that polynomial: NOT ASSIGNED.** The statement gives no exponent, no
  constant, and no count of EndRing oracle calls.
- **Step "Isogeny immediately reduces to ℓ-IsogenyPath": the source assigns no
  cost to this step.** It is asserted in one clause with no cost attached.
- **Step "ℓ-IsogenyPath ≡ EndRing": the source assigns no cost to this step.** It
  is delegated entirely to `[Wes22b]`; `[35]` restates only the path length
  O(log p), not the reduction's running time, degree, or oracle-call count.
- **Conditionality assigned:** the statement begins "Assuming the generalised
  Riemann hypothesis". GRH is a dependency **of this reduction as stated**.

### 4.3 Recorded observation about the conditionality list

The frozen source's Corollary 1.2 (line 23) is stated as "Assuming Heuristic 1"
and mentions no other assumption; `[35, Proposition 8.5]`, which line 21 says is
applied to obtain it, is stated "Assuming the generalised Riemann hypothesis".
Both facts are recorded here with locators. `docs/claims-and-verification.md`
("Claim records for conditional results") states that a heuristic- or
GRH-conditional reduction adds its dependency to the list; applying that rule to
`GOAL-SSIQ-001`'s records is a Coordinator action, not this task's.

---

## 5. `[35, Theorem 1]` (read as Theorem 1.1 / stated precisely as Theorem 7.2) — EndRing reduces to OneEnd

### 5.1 What it does

Proceedings chapter, **p. 389**, § 1.1, verbatim:

> **Theorem 1.1.** The EndRing and OneEnd problems are equivalent, under
> probabilistic polynomial time reductions.
>
> Formal definitions are provided in Sect. 2, and the proof is the object of
> Sect. 7. The reduction from OneEnd to EndRing is obvious, and the other
> direction is stated more precisely in Theorem 7.2. **This reduction transforms
> one instance of EndRing into polynomially many instances of OneEnd.**

The precise form, proceedings **p. 409**, verbatim:

> **Theorem 7.2 (EndRing reduces to OneEnd).** Algorithm 3 is a reduction from
> EndRing to OneEnd_λ of expected polynomial time in log(p) and λ(log p).

`OneEnd_λ` is defined on p. 395: the OneEnd problem where the returned α must
satisfy `log(deg α) ≤ λ(log p)`.

### 5.2 What it multiplies the complexity by

- **Assigned cost class:** **expected polynomial time in log(p) and λ(log p)**,
  i.e. a factor `(log p · λ(log p))^{O(1)}`.
- **Assigned oracle cost:** "**polynomially many** instances of OneEnd" (p. 389).
  This is the multiplier that acts on the p^{1/3+o(1)} OneEnd solver.
- **Degree of those polynomials: NOT ASSIGNED.** Neither p. 389 nor Theorem 7.2
  names an exponent or a constant for "polynomially many" / "polynomial time".

**Sub-factors the proof does assign** (proceedings pp. 409–410, Theorem 7.2's
proof — recorded because they are the only explicit exponents anywhere in the
cascade):

| quantity | assigned value | locator |
|---|---|---|
| first loop, walk-length parameter | `k_1 = O(log p)` | p. 410 |
| first loop, expected iterations | `O(1)` (full-rank probability ≥ 1/16) | p. 410 |
| index after first loop | `[End(E) : R_1] ≤ 2^{3k_1λ(log p)+2}/p = 2^{O(log(p)·λ(log p))}`, Eq. (1) | p. 410 |
| second loop, per-iteration success probability | **`Ω((log N)^{-12})`** — i.e. expected `O((log N)^{12})` iterations per success | p. 410 |
| second loop, number of successes needed | "polynomially bounded in log([End(E) : R])", "hence in **poly(log p, λ(log p))**" — **degree NOT ASSIGNED** | p. 410 |
| oracle parameter inside the loop | `k_2 = 12 · log(4100000 · (log N)^{12} N^2 √p + 13)` (Algorithm 3, Step 13; Lemma 7.1) | pp. 408–409 |

So the only explicit exponent that the source attaches anywhere in this reduction
is **12**, in the per-iteration success probability `Ω((log N)^{-12})` (with
`log N = O(log p · λ(log p))` via Eq. (1)). The *number of iterations of the outer
bookkeeping*, and therefore the total OneEnd-oracle-call count, carries **no
assigned degree**.

### 5.3 The `λ` gap, recorded

Theorem 7.2 reduces EndRing to **OneEnd_λ**, and its cost is stated as a function
of `λ(log p)`. The frozen source's Problem 2.2 (line 119) is the **unbounded**
OneEnd problem, and its Theorem 1.1 (line 19) states no bound on `deg α`.

**Neither source states the value of λ at which Corollary 1.2 applies Theorem 7.2.**
The frozen source assigns no λ to its own OneEnd solver, and `[35]` assigns no λ
to Corollary 1.2's use of its theorem.

*Derived here, NOT stated in either source, recorded so a checker can verify or
refute it:* the endomorphism returned by the frozen source's Algorithm 3 (line 206)
is `α = ω̂ ∘ ϕ ∘ φ ∘ ω`, with `deg ω = 2^n` and `n = O(log p)` (frozen line 193),
`deg ϕ = p` (Frobenius, frozen line 205), and `deg φ ≤ X^2` where
`X = B^{1/2}(p/2)^{1/6} = p^{1/6+o(1)}` (frozen lines 167, 214), giving
`deg α ≤ 2^{2n} · p · p^{1/3+o(1)} = p^{O(1)}`, hence `log deg α = O(log p)`. This
is a derivation by this task, labelled as such; it is not a source statement and
carries no authority beyond its own arithmetic.

---

## 6. `[33]` — obtained, recorded, not the object of this task

Frozen line 127 states the equivalence of the three problems "culminat[es] in a
larger network of unconditional equivalencies in [33]", and reading (b) of §3.2
points at it. `[33]` was obtained (HAL hal-04954150 v3, produced 2025-12-01,
34 pages, SHA-256 `6d8d0c83…`). Two verbatim statements, recorded without
assessment:

> **Theorem 1.** The problems Isogeny, EndRing, MaxOrder, MaxOrder_Q, HomModule,
> OneEnd and MOER, are all equivalent under probabilistic polynomial time
> reductions. Reductions involving MaxOrder_Q require oracle access to Q.

> **Theorem 2.** For any pair of problems (P, Q) chosen from the problems MOER,
> EndRing, Isogeny, OneEnd, MaxOrder, MaxOrder_Q, HomModule, and ℓ-IsogenyPath
> there exists a probablistic polynomial time worst-case to average-case reduction
> from P to Q. All reductions hold unconditionally, with the two following
> exceptions which require the generalized Riemann hypothesis: – if
> P = ℓ-IsogenyPath, or – if Q ∈ {MaxOrder, MaxOrder_Q} and p ≡ 1 mod 8. …

Cost assigned by these statements: **probabilistic polynomial time**, degree **NOT
ASSIGNED**, oracle-call count **NOT ASSIGNED**. `[33]` is not cited by the frozen
Corollary 1.2 and its per-arrow costs were not audited by this task.

---

## 7. Cost table — the deliverable in one place

Every entry is a statement *of the source*, at the locator given. "NOT ASSIGNED"
means the source states no such quantity; it does not mean the quantity is large,
small, zero, or unimportant.

| # | step | source + locator | what it does | multiplies complexity by | conditional on |
|---|---|---|---|---|---|
| S1 | Isogeny → ℓ-IsogenyPath | `[35]` proceedings p. 413, in the proof of Prop. 8.5 | asserts the reduction in one clause | **the source assigns no cost to this step** | (inside GRH-conditional Prop. 8.5) |
| S2 | ℓ-IsogenyPath ≡ EndRing | `[35]` proceedings p. 413, delegated to `[Wes22b]` (= frozen `[45]`) | delegated, not restated | **the source assigns no cost to this step** (only "paths of length O(log p)" is restated) | GRH |
| S1+S2 | **`[35, Proposition 8.5]`**: Isogeny_λ → EndRing | `[35]` proceedings p. 413 | lets an EndRing solver answer Isogeny | **probabilistic polynomial time in the instance length**, i.e. `(log p)^{O(1)}`, with `λ(log p) = O(log p)`; **degree NOT ASSIGNED; EndRing oracle-call count NOT ASSIGNED** | **GRH** |
| S3 | **`[35, Theorem 1]`** read as Theorem 1.1, precisely Theorem 7.2: EndRing → OneEnd_λ | `[35]` proceedings pp. 389, 409–410 | Algorithm 3: builds End(E) from repeated OneEnd calls with saturation and index bookkeeping | **expected polynomial time in log(p) and λ(log p)**; "**polynomially many** instances of OneEnd"; **degree NOT ASSIGNED**. Only explicit exponent in the whole cascade: per-iteration success `Ω((log N)^{-12})`, `log N = O(log p·λ(log p))` | probabilistic (Las Vegas) only; no GRH, no heuristic stated |
| S3′ | alternative reading `[33, Theorem 1]`: Isogeny ≡ OneEnd directly | `[33]` HAL v3, Theorem 1 | unconditional equivalence network | **probabilistic polynomial time**; **degree NOT ASSIGNED**; oracle-call count **NOT ASSIGNED** | unconditional (per that statement) |
| S4 | the frozen source's own application of S1–S3 in Corollary 1.2 | `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` lines 21, 23 | states the same p^{1/3+o(1)} for EndRing and Isogeny as for OneEnd | **the source assigns no cost to this step** — line 21 says only "applying the computational reductions … we deduce"; no multiplier, no cofactor, no exponent is stated, and GRH is not restated | Heuristic 1 (as stated in Cor. 1.2) |
| — | λ at which S3 is applied | — | — | **the source assigns no cost to this step**: neither source states the λ of the frozen OneEnd solver (see §5.3) | — |

### 7.1 The one exponent question GD-1 asks, answered as a source reading

`GD-1` asks whether a reduction costs `p^{ε}` for some `ε > 0`. **As stated by the
sources**, neither reduction is assigned a cost of the form `p^{ε}`: both are
assigned costs polynomial in the *instance length* `log p` (S1+S2, S3), which is
`(log p)^{O(1)}` and is smaller than `p^{ε}` for every fixed `ε > 0`. **The degree
of that polynomial is not assigned anywhere in `[35]`, in `[33]`, or in the frozen
source.** GD-1's other prediction is therefore confirmed exactly: *no exponent is
assigned to those reductions anywhere*, and the frozen source states no multiplier
at all when it applies them (row S4).

Whether an unassigned-degree `(log p)^{O(1)}` factor, a GRH dependency appearing in
S1+S2 but not in Corollary 1.2's statement, and an unstated λ are consequential for
any condition derived in `BATCH-001` **is deliberately not assessed here**.

---

## 8. Provenance and reproducibility of every quotation above

- Frozen-source quotations cite line numbers in
  `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` at repo commit
  `ab8e3ad8f93b84f197aef647746a36ef0d7cd359`.
- `[35]` quotations are from the EUROCRYPT 2024 proceedings PDF, SHA-256
  `55c054a8b4e75041fc2aef62438ac1bd5071f34fec7dea298bafecd6a62280ff`, 30 pages,
  printed pages 388–417 (PDF page *n* = printed page *n*+387).
- Every § 4 and § 5 statement quoted above was extracted **independently by three
  different extractors** (poppler `pdftotext -layout` 24.02.0, `pdfminer.six`
  20260107, PyMuPDF 1.28.0/MuPDF 1.29.0) and the three agree on the wording; see
  `extractor_unblock_log.md` § 5 for the cross-check and for a flattening hazard
  that affects superscripts.
- The PDFs themselves are **not** committed (the task declares exactly four
  artifacts). They are re-obtainable from the URLs in `source_access_log.yaml`
  and verifiable against the SHA-256 values recorded there.
- **Unobtained:** IACR ePrint 2023/1399 (HTTP 403, Cloudflare challenge, twice).
  Recorded as unobtained; no statement in this note is sourced from it, and no
  theorem statement anywhere in this note was reconstructed from memory.
