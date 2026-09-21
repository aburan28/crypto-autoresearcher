# Rate / parameter regime extraction — the priority deliverable

**Task:** TASK-20260803-292b99 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`

---

## 0. Scope firewall

This program asserts **nothing** about Classic McEliece's security in either
direction. Several sources quoted here make statements about Classic McEliece
parameters; those statements are theirs, quoted because a headline without its
regime is not a usable transcription. **No comparison between any regime below
and Classic McEliece's actual rate is performed in this document**, because
Classic McEliece's rate has not been transcribed from its own specification —
that is `TASK-20260803-f3aece`'s deliverable, and doing the arithmetic here
against second-hand parameters is exactly the shortcut the batch forbids.

---

## 1. PRIMARY — `iacr:2026/1232`: THE PAPER'S ABSTRACT STATES **NO** RATE CONDITION

### 1.1 The finding, stated plainly

**In the text obtained (abstract + authors' revision note, sources A01 and A11),
`iacr:2026/1232` states:**

| Dimension of scope | What the obtained text states |
|---|---|
| **Code family** | binary Goppa codes; and, generally, Goppa codes over a field of **even characteristic** |
| **Field condition** | **even characteristic** (stated explicitly) |
| **Rate condition** | **NONE STATED** |
| **Genus condition** | **NONE STATED** |
| **Degree condition** | **NONE STATED** (a Goppa-polynomial degree `r = 9` appears, but only as a demonstrated CFS instance, not as a restriction) |
| **Extension-degree (m) condition** | **NONE STATED** (an `m = 16` appears, again only as a demonstrated CFS instance) |

**This is a statement about the ABSTRACT, not about the paper.** The body was
not obtained (`source_access_log.yaml`: A02, A03, A04, A29 all 403,
`cf-mitigated: challenge`). **Whether the body imposes a rate condition is
UNKNOWN.** "The abstract states no rate condition" and "the paper claims no rate
restriction" are different sentences and this document asserts only the first.

Given that every other examined result in this line carries a rate or family
restriction (§2, §3, §4 below), the absence of one in a 250-word abstract is
**weak evidence about the body and is not treated as evidence at all here.**

### 1.2 The passages where the scope IS stated, VERBATIM

Sentence 1 — the code family:

> We provide a new way of performing an algebraic attack on the McEliece
> cryptosystem based on binary Goppa codes.

Sentence 2 — the generalisation, and the only stated restriction of any kind:

> It also applies in general to the case where the field over which the Goppa
> code is defined is of even characteristic.

Sentence on the distinguisher byproduct, repeating the same field condition:

> A byproduct of our approach is a new distinguisher for Goppa codes in even
> characteristic which is as the syzygy distinguisher of [R25] subexponential in
> the security parameter of the scheme.

**These three sentences are the entire scope statement available.** They give a
family and a characteristic. They give no rate.

### 1.3 The passage where the paper does NOT state a rate condition, quoted in full

The task requires that if the paper states no restriction, the passage where it
does not be quoted. Since the entire obtained text is short, it is quoted
entire, so the absence is verifiable rather than asserted. This is the complete
abstract as published (A01, cross-checked at A11):

> We provide a new way of performing an algebraic attack on the McEliece
> cryptosystem based on binary Goppa codes. It also applies in general to the
> case where the field over which the Goppa code is defined is of even
> characteristic. It is based on a new algebraic modeling for finding as in
> [CMT23,M25,BLT26] matrices of rank $2$ in the code of quadratic relations
> related to the Goppa code that is attacked. Such matrices are then used to
> recover the secret algebraic structure of the code, from which an equivalent
> secret key can be efficiently derived, leading to a full key-recovery attack.
> A byproduct of our approach is a new distinguisher for Goppa codes in even
> characteristic which is as the syzygy distinguisher of [R25] subexponential in
> the security parameter of the scheme. We demonstrate the effectiveness of our
> attack on McEliece TII challenges, some of which having been studied in
> [BLT26], and aimed at having $83$,$89$,$119$,$166$, $210$ and even $248$ bit
> security respectively and CFS keys with parameters $r=9$ and $m=16$,
> corresponding to a security of $74.9$ bits according to [LS12]. This CFS key
> was not attacked in practice in [BLT26] and took us 14 hours of computation
> and 24GB of RAM. We make the conjecture that this attack has a complexity
> which is of the same nature as the distinguisher, namely subexponential in the
> security parameter.

**No occurrence of "rate", "high rate", "R =", "k/n", or any inequality on code
parameters appears anywhere in it.** Verified by inspection of the extracted
character stream, not by recollection.

The keyword list on the ePrint record is likewise family-only, VERBATIM:
`McEliece scheme, Algebraic cryptanalysis, Binary Goppa codes`.

### 1.4 The parameter instances the abstract DOES name

These are **demonstrated instances**, not a regime. Transcribed with their own
qualifiers:

- **McEliece TII challenges** "aimed at having $83$,$89$,$119$,$166$, $210$ and
  even $248$ bit security respectively". These are the **challenges' design
  targets**, in the abstract's own words "aimed at having", not measured attack
  costs, and the abstract does **not** say which of them were solved.
- **CFS keys with parameters $r=9$ and $m=16$**, "corresponding to a security of
  $74.9$ bits according to [LS12]", which "took us 14 hours of computation and
  24GB of RAM". `r` is the Goppa-polynomial degree and `m` the extension degree
  in the usual convention; the abstract does not define them, and **no `n` and
  no rate is given for this instance**.

**CFS operates in a high-rate regime** — that is stated in the *other* paper,
`arXiv:2304.14757`, VERBATIM: *"we could hope to break the CFS scheme [CFS01]
which operates precisely in the high rate regime"*. Whether that bears on
`iacr:2026/1232`'s regime is **not** determinable from the abstract and is not
inferred here.

Neither the TII challenges nor CFS keys are Classic McEliece parameter sets.
**The abstract names no Classic McEliece parameter set anywhere.**

### 1.5 The one scope statement the authors make about Classic McEliece

Transcribed because it is scope text and the task requires scope text.
**Attributed to the authors. Not adopted, not contradicted, not verified.**
From the ePrint `Note:` field (A01), VERBATIM:

> Note that the last paragraph in the introduction called « The impact on the
> McEliece scheme » leaves no doubt that this attack does not break Classic
> McEliece parameters.

The same note records that the authors **removed** the sentence "This breaks the
scheme." in the 2026-06-12 revision and replaced it with a full-key-recovery
formulation. See `attack_transcription.md` §1.3 for the note in full.

**The introduction paragraph the note refers to was NOT read.** It is in the
body. This program records that the authors characterise their own paragraph
this way, and records that it has not verified the characterisation. Under the
BATCH-001 opening's §7 symmetry rule, treating this note as a licence to dismiss
the paper would be the same error as treating the title as a licence to alarm.

---

## 2. `iacr:2024/1193` — *The syzygy distinguisher* (KN-LIT-71d1a0): regime IS stated, in the **dual** rate

Full text obtained (B01, sha256 `b69f8256…d68c0`; **version caveat in
`attack_transcription.md` §2**). This is the paper the primary target anchors its
subexponentiality to.

### 2.1 The paper's headline scope claim, VERBATIM

> Moreover it does not suffer from the strong regime limitations of the previous
> distinguishers or structure recovery algorithms: in particular, it applies to
> the codes used in the Classic McEliece candidate for postquantum cryptography
> standardization.

That is a **regime claim about a distinguisher**, and RQ-MCE-e65b3c's
"distinguisher is not break" constraint is stated here explicitly: **this paper
distinguishes; it does not claim key recovery.**

### 2.2 The parameter the regime is stated in — **dual rate**, not primal rate

Theorem 3, VERBATIM: *"Asymptotically, q-ary alternant (including Goppa) codes of
**dual rate R** can be distinguished from random codes […]"*.

The paper is explicit about the conversion, VERBATIM:

> Fix a base field cardinality q, for instance q = 2, and a (dual) rate R. In [4]
> it is suggested to take a primal code of rate between 0.7 and 0.8, so passing to
> the dual gives 0.2 ≤ R ≤ 0.3. However here we allow any R.

**"However here we allow any R"** is the paper's own statement that its
asymptotic theorem carries no rate restriction. **[NO EXTRACTION DAMAGE] — this
sentence is clean prose.**

**Trap flagged, not resolved:** `R` in this paper is the **dual** rate. Any later
comparison against a primal rate `k/n` must convert. Reading `R < 0.277` as a
primal-rate threshold would be a category error. This document performs no such
comparison.

### 2.3 Where a rate condition DOES appear: the null-model conditions of Heuristic 1

Remark 2, VERBATIM:

> **Remark 2.** Consider this Heuristic in the asymptotic regime. Setting R = k/n,
> we can take d = dGV(q, n, k) ≈ H_q^{-1}(1 − R)n and d⊥ = dGV(q, n, n − k) ≈
> H_q^{-1}(R)n the corresponding Gilbert-Varshamov distances, where H_q is the
> q-ary entropy function. Then the condition in 1. translates as
> H_q^{-1}(1 − R) > R(1 − R), and the condition in 2. translates as
> H_q^{-1}(R) > R², both of which are satisfied when R is small enough. In
> particular for q = 2, we find that 1. is satisfied for R < 0.277 and 2. is
> satisfied for R < 0.141.

**Extraction quality:** the prose and the two numeric thresholds `0.277` and
`0.141` are **clean** — they appear as plain inline digits, not as flattened
superscripts, and are not marked damaged. The symbolic conditions
`H_q^{-1}(1 − R) > R(1 − R)` and `H_q^{-1}(R) > R²` are **mildly reconstructed**
(the extraction renders `H −1 q` with the inverse and the subscript split across
tokens) and are marked **[EXTRACTION-DAMAGED — symbolic form only; the numeric
thresholds are clean]**.

**What these thresholds are and are not, stated carefully because it is the
easiest thing in this whole document to get wrong:**

- They are conditions under which **Heuristic 1's prediction for RANDOM codes**
  is expected to hold. They describe the **null model / control**, not the
  alternant or Goppa codes being detected.
- Remark 2 sets `R = k/n` for the code Heuristic 1 is applied to. Elsewhere the
  distinguisher is applied to **shortened dual** codes `C_s`, and the proof of
  Theorem 3 states VERBATIM: *"Moreover the shortened code C_s has rate
  k_s/n_s = (k_{r*}+r)/(n−k+k_{r*}+r) = o(1), so by Remark 2 both conditions in
  Heuristic 1 are satisfied."*
- **So in the asymptotic theorem the rate that must be small is the rate of the
  SHORTENED code, which the paper shows is `o(1)` by construction — not the rate
  of the McEliece code.** That is precisely why the paper can also write "here we
  allow any R".
- **This program does not adjudicate that reading.** It is stated as the paper's
  own chain of statements, quoted, and left to the Validator.

### 2.4 Finite-parameter scope, VERBATIM

> However this is only an asymptotic result: for concrete, finite parameters,
> such as those proposed in the Classic McEliece specification, a naive
> implementation of our distinguisher still falls beyond the best attacks by a
> non-negligible factor.

And on its Example 2 table, VERBATIM: *"These complexities improve those from
[7], although they remain practically unreacheable and well beyond security
levels."* (Source's spelling.) The κ values in that table are
**[EXTRACTION-DAMAGED]** and are **not** transcribed anywhere in this task's
deliverables — see `attack_transcription.md` §2.4.

The paper also reports, VERBATIM, that its Heuristic-1-based complexity estimate's
precondition **fails for two of the five parameter triples it tabulates**: *"We
see this condition is satisfied for the parameter sets (3488, 12, 64),
(6960, 13, 119), (8192, 13, 128), but for (4608, 13, 96) and (6688, 13, 128) it
is not."*

---

## 3. `arXiv:2304.14757` (KN-LIT-4c8135): regime is a **high-rate condition PLUS a small field PLUS an explicit Goppa exclusion**

Full text obtained (C02, sha256 `ebbd94ac…c564b8`).

### 3.1 The restriction as the paper's own Table 1 states it, VERBATIM

```
paper                 restriction
[SS92, CGG`14]        m “ 1
[COT14]               m “ 2 + Wild Goppa code
this paper            q “ 2 or q “ 3, m arbitrary + high rate condition (6)
                      (does not apply in the particular case of Goppa codes)
```

(`“` is this extraction's rendering of `=`.)

### 3.2 The prose restatement, VERBATIM

> […] show that we can actually attack McEliece-alternant for any extension degree
> m provided that the rate of the alternant code is sufficiently large (6) and the
> field size sufficiently low q “ 2 or q “ 3.

### 3.3 THE GOPPA EXCLUSION — the single most load-bearing sentence in this paper for GOAL-MCE-001

VERBATIM:

> Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code.

Clean extraction, plain prose, no damage. The paper's Table 1 repeats it as a
parenthetical restriction. Section 3.2's heading is, VERBATIM, *"What is wrong
with Goppa codes?"*, and it states VERBATIM: *"Goppa codes behave differently
from random alternant codes and provide counterexamples to Heuristic 18."*

The abstract likewise confines the positive answer, VERBATIM: *"We give for the
first time a positive answer for this problem **when the code is a generic
alternant code** and when the code field size $q$ is small : $q \in \{2,3\}$"*.

### 3.4 High-rate condition (6) itself — **[EXTRACTION-DAMAGED], NOT TRANSCRIBED**

Raw pdfminer output at the location of equation (6), unedited:

```
                                                                        (6)
n ´ 1 ą
´
pr ´ 1q
p2e ` 1qr ´ 2
where e
ˆ
              ˙
       ˆ
def
“ maxti P N | r ě qi ` 1u “
                                    logqpr ´ 1q
`
`
rm ` 1
2
        ˘˘
m
2
qe ´ 1
q ´ 1
,
                ˙
```

**[EXTRACTION-DAMAGED].** The two-column ligature-heavy typesetting has
interleaved the left-hand side, the binomial `(rm+1 choose 2)`, the factor
`m/2`, the bracketed `(2e+1)r − 2(q^e − 1)/(q−1)`, and the factor `(r−1)` beyond
reliable reordering. **This inequality is NOT reconstructed and carries no claim
in any deliverable of this task.** A reviewer wanting condition (6) must read the
rendered PDF at sha256 `ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`.

What IS clean and transcribable: `e := max{ i ∈ ℕ | r ≥ q^i + 1 } = ⌊log_q(r−1)⌋`
(prose-level definition, appears twice in the extraction consistently), and the
qualitative statement that (6) is a **lower bound on n − 1**, i.e. a
**large-n-relative-to-rm** condition, which is what "high rate" means here.
**The qualitative reading is labelled as such and is not a substitute for the
formula.**

The paper's own restatement of when the attack applies is also clean, VERBATIM:
*"we have at the end a way to break a McEliece scheme based on binary or ternary
alternant codes as soon as (A_r(x,y)^⊥)^{*2} is not the full code F_q^{n−1}."*
(with the star-product markup **[EXTRACTION-DAMAGED]**).

Also clean and relevant to why the rate matters, VERBATIM: *"This would allow to
break the McEliece scheme **as soon as the code rate is large enough** and would
break all instances of the CFS signature scheme."*

### 3.5 A proof-of-concept location the paper gives, VERBATIM

> A proof-of-concept implementation in MAGMA of the whole attack can be found at
> https://github.com/roccomora/HighRateAlternant.

Recorded as a lead. **Not fetched** — outside this task's mandate, and no run is
authorized.

---

## 4. `iacr:2025/531` (KN-LIT-7ee1a9): the regime exists in the body and was NOT obtained

Abstract only (D03). The abstract's own statements about rate, VERBATIM:

> Whereas the distinguisher of [FGO+11] is only able to distinguish Goppa codes
> or alternant codes of **rate very close to 1**, in [CMT23a] a much more powerful
> (and more general) distinguisher was proposed.

> Computing $\mathrm{HF}(2)$ still gives a polynomial time distinguisher for
> alternant or Goppa codes and is apparently able to distinguish Goppa or
> alternant codes in a **much broader regime of rates** as the one of [FGO+11].

> The value of $\mathrm{HF}(2)$ corresponding to random linear codes is known and
> this yields **a precise description of the new regime of rates** that can be
> distinguished by this new method.

**The precise description is announced in the abstract and given in the body.
The body was not obtained.** The regime for this paper is therefore
**NOT TRANSCRIBED**, and the fact that it exists is not a substitute for having
it. Note also the paper's own hedge on the broader regime: *"is **apparently**
able to distinguish"*.

This is again a **distinguisher**, not a key recovery.

---

## 5. Summary table — what regime each source claims

| Source | Obtained | Code family | Field condition | Rate / parameter condition | Damage |
|---|---|---|---|---|---|
| `iacr:2026/1232` **PRIMARY** | abstract only | Goppa codes (binary; and Goppa over even characteristic) | **even characteristic** | **NONE STATED IN THE ABSTRACT.** Body unread; existence of a body-level condition **UNKNOWN** | none — nothing damaged, the values are simply absent |
| `iacr:2024/1193` | full text | alternant, including Goppa; distinguisher on the **dual** | any q; worked for q = 2 | Theorem 3 states **"here we allow any R"** (R = dual rate). Heuristic 1's random-code null model needs R small; for q = 2 the paper gives **R < 0.277** (part 1) and **R < 0.141** (part 2), applied to the **shortened** code whose rate the proof argues is o(1) | eq. (92), Heuristic 1 formulas, Example 2 table, κ row — all **[EXTRACTION-DAMAGED]**; the 0.277 / 0.141 thresholds are **clean** |
| `arXiv:2304.14757` | full text | **generic alternant codes; explicitly NOT Goppa codes** | **q ∈ {2, 3}** | **high rate condition (6)**, m arbitrary | condition (6) **[EXTRACTION-DAMAGED]**, not reconstructed; the Goppa exclusion sentence is **clean** |
| `iacr:2025/531` | abstract only | alternant or Goppa | q ≥ r for the closed formula (per abstract) | "much broader regime of rates" than rate-close-to-1; **precise description NOT OBTAINED** | n/a |

---

## 6. The distance to Classic McEliece: NOT COMPUTED, and why

GOAL-MCE-001's first completion criterion asks for the distance between the 2026
regime and Classic McEliece's parameters "stated quantitatively, or its
unavailability recorded with routes tried". **It is unavailable, and here is
exactly why, with no part of it hidden:**

1. **The primary target states no rate regime in the text obtained**, and its
   body — where a regime would live if there is one — is blocked. There is no
   left-hand side to the comparison.
2. **Classic McEliece's rate has not been transcribed from its own
   specification** by this task; that is `TASK-20260803-f3aece`'s deliverable.
   The `(n, m, t)` triples that appear in `iacr:2024/1193`'s Example 2 are a
   **third party's** reproduction and must not be used as the parameter source
   (see `attack_transcription.md` §2.4). There is no verified right-hand side
   either.
3. Computing a distance from a missing left-hand side and a second-hand
   right-hand side would produce a number with the appearance of a measurement
   and the content of a guess. That is the failure GOAL-HQC-001 BATCH-001
   committed at 50.7 bits, and it is refused here.

**What IS available for a later comparison, once both sides exist:** the
`arXiv:2304.14757` regime is stated as a family exclusion (**not Goppa**) plus a
field condition (**q ∈ {2,3}**) plus condition (6) — and the family exclusion
alone is a sharper and cheaper discriminator than any rate arithmetic. The
`iacr:2024/1193` regime is stated in the **dual** rate and its asymptotic theorem
explicitly declines a rate restriction. **These two facts are transcription, not
analysis, and the analysis belongs to a later batch.**
