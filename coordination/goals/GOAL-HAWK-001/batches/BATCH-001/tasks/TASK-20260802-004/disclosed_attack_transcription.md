# Claim-structure transcription — SRC-4, the disclosed attack

Task TASK-20260802-004, GOAL-HAWK-001 / BATCH-001, 2026-08-02.

**Source of record.** Zygimantas Straznickas and Stephen A. Weis, *HAWK-n Key
Recovery Reduces to SVP in Dimension n/2 + 1*, Anthropic technical report, 2026.
Held in this corpus since 2026-07-28 as `KN-LIT-7592`.

Obtained `2026-08-02` from `https://anthropic.com/document/hawk_key_recovery.pdf`.
PDF `sha256:056faead316ea9a8eb01000cb9c548e79e21ad09a0684c3d52bbc1093183ac89`
(748154 bytes); pdfminer.six extraction
`sha256:a5bd24e6e907aeef8d50d1bde97893ca34c72acba051913657d21f17b2c348ca`
(78015 chars).

---

## The batch's principal finding: this attack has no heuristics

`GOAL-HAWK-001.next_action` instructs that the primary sources be filed "with the
**four heuristics** transcribed verbatim and numbered", and the goal's `objective`
asks to "restate it as a **numbered-heuristic conditional theorem**".

**Neither is possible for this attack, because it is unconditional.**

A regex census over the full 78015-character extraction:

| Token | Occurrences |
|---|---|
| `Heuristic` | **0** |
| `Conjecture` | **0** |
| `Assumption` | 1 — and *not* an assumption of the reduction; see below |
| `Theorem` | 28 |
| `Lemma` | 60 |
| `Proposition` | 19 |
| `unconditional` | 4 |

The abstract states it directly:

> "We give an **unconditional, deterministic** polynomial-time reduction from
> HAWK-n key recovery over Kn = Q(ζ2ℓ) to poly(n) calls to an exact Shortest
> Vector Problem (SVP) oracle in dimension n/2 + 1, where n = 2ℓ−1 is the ring
> degree."

**The "four heuristics" belong to a different paper** — eprint 2026/1318,
*Cryptanalysis of HAWK: a Guessing Game* (Nelson–Limbrey–Ling–Mendelsohn), whose
abstract says its algorithm assumes "four number-theoretic heuristics" and whose
full text could **not** be obtained (`source_access_log.yaml`, SRC-2).

So the goal record conflates **three distinct works** into one target:

| | Basis | Status |
|---|---|---|
| **SRC-4** Straznickas–Weis | **Unconditional**, deterministic | Full text obtained |
| **SRC-1** van Gent–Pulles | Heuristic 1 (2016 estimates) + unnumbered §5 argument | Full text obtained |
| **SRC-2** Nelson et al. 2026/1318 | Four number-theoretic heuristics, one publicly conceded insufficient | **Abstract only** |

`RQ-HAWK-001` asks "under exactly which numbered heuristics does it succeed or
fail?". For the disclosed attack the answer is **none**, and that answer is not a
technicality — it is the difference between an attack that needs validating and
one that needs only checking.

---

## The single `Assumption` is not an assumption of the reduction

It appears in the **cost-comparison table**, and it is HAWK's own model:

> "**Assumption**), as used for [HAWK25, Table 8]: an unusually short vector of
> length ν in a rank-d lattice of volume V is found by progressive BKZ at the
> smallest β with (cid:112)β/d ν ≤ δ 2β−d−1 V 1/d, δβ = (cid:0) β 2πe β
> (cid:1)1/(2(β−1)), a condition that depends only on d and the gap ln ν −
> 1 d ln V"

`[EXTRACTION-DAMAGED]` — the inequality is not reliably rendered; `(cid:112)` is an
extracted `√` glyph and the exponents are flattened.

The important point is structural, not formulaic: the authors adopt **HAWK's own
Table 8 success condition** in order to price the *comparison baseline* on the
spec's terms. It conditions the **cost table**, not the reduction. The reduction
itself stands without it.

---

## The claim chain — verbatim

> "The integer solutions of the two conditions form the lattice Λ(τ) B , of rank n
> (Lemma 4.3). A Z-basis of it is computed from Q in polynomial time (§4.1). Vτ is
> a shortest vector of Λ(τ) B . Lengths are measured by Q(τ)(Y) := TrF (det Y),
> which is the trace from the degree-n/4 field F fixed by c and τ, §3.2.
> det Vτ = 1 since det B = 1, and so its squared length is the minimum TrF (1) =
> n/4, regardless of the [...]"

> "[...] Proposition 4.5), so **Ducas's block reduction** [Duc23; BN24] finds all
> its shortest vectors with SVP calls in **dimension n/2 + 1** (Theorem 5.1,
> Appendix E). Recovering the key from Vτ is then **the descent of van Gent and
> Pulles** [GP25]: their kernel sublattice {x ∈ R2 τ x} is isometric to a scaled
> Zn (Proposition D.2), and one further run of Ducas's algorithm on it returns an
> equivalent key. Combined, this is our main result (**Theorem 6.1**): HAWK key
> recovery reduces deterministically to poly(n) calls to exact SVP in dimension
> n/2 + 1. We implement the attack [...]"

> "(Lemma D.1), so the descent of van Gent and Pulles [GP25, Props. 1–2] applies: a
> short vector of the kernel sublattice MY recovers an equivalent key. Appendix D
> sharpens the analysis to an **unconditional bound**: the parity test Y ≡ I
> (mod 2) selects the two candidates Y = ±Vτ , for which the kernel is n Zn
> (Proposition D.2), so one further run of Ducas's algorithm [Duc23] exactl[y ...]"

---

## How it relates to SRC-1 — the authors state this themselves

This is the sentence that settles the relationship between the two obtained
sources:

> "[...] of unity as shortest vectors — and this exactness is what admits the
> provable solver of [Duc23] (Remark D.3) and so **upgrades the endgame from the
> heuristic pricing of [GP25, Thm. 1] to the unconditional accounting of
> Theorem 6.1**."

So SRC-4 **does not merely cite** SRC-1's descent — it **removes SRC-1's heuristic
step**. van Gent–Pulles's Theorem 1 rests on their Heuristic 1 (a 2016-estimates
BKZ success condition, transcribed in `heuristics_transcription.md`); Straznickas–
Weis replace that step by proving the relevant lattice is *exactly* near-hypercubic,
which admits Ducas's **provable** block reduction instead of a heuristically-priced
BKZ.

**What is new here, stated precisely.** `KN-LIT-7592` already records that the
reduction is "unconditional and deterministic, with no numbered heuristics" (its
line 73) and already cites the `[GP25]` descent (line 43). What it does **not**
record — a grep for `upgrade|discharg|heuristic.*pricing` over that entry returns
zero — is the **relationship between the two papers**: that SRC-4 does not merely
*use* SRC-1's descent but *removes SRC-1's heuristic step*. That relationship is
BATCH-001's structural contribution, and it is visible only with both full texts in
hand.

## The cost claim — verbatim, with its baseline

> "a factor of two in the oracle dimension: βkey/n → 1 under the model of
> [HAWK25, §5.1] while ours is n/2 + 1. With the provable sieve of [ADRS15] as the
> oracle this gives time **2(n/2+1)+o(n) unconditionally**."

> "**Table 1.** Cost of one SVP-oracle call. β is the oracle dimension: βkey
> [HAWK25, Table 7] for the spec, n/2 + 1 for the attack. ∗Core-SVP is our
> conversion 20.292β (exponent [...])"

Three things to carry with any citation of this:

1. The exponent `2^{(n/2+1)+o(n)}` is **unconditional but oracle-relative** — it is
   the cost of the *provable* [ADRS15] sieve, not of a practical solver. A
   Core-SVP `2^{0.292β}` conversion is given separately and is a **heuristic**
   pricing, by the authors' own labelling.
2. The comparison baseline is **HAWK's own spec model** (`[HAWK25, §5.1]`,
   Tables 7 and 8) — i.e. matched-baseline discipline is satisfied on the spec's
   terms, which is what `RQ-HAWK-001.constraints` requires.
3. "Roughly halves HAWK's effective key strength" is a statement about the
   **oracle dimension**, `β_key/n → 1` versus `n/2 + 1`. It is not a claim that
   HAWK is broken at deployed parameters, and this file does not make one.

---

## What this task did NOT establish

- **Nothing is verified.** No step of the reduction was checked, no lemma
  re-derived, no implementation run. The paper reports an implementation; this
  task did not execute it.
- **No HAWK parameter set is assessed.** `RQ-HAWK-001`'s claim-tier ceiling
  (toy-tier until a certified instance at the scheme's own parameter scale exists)
  is untouched, and no certificate has been produced or checked.
- **SRC-2's four heuristics remain unread** — the actual object the goal's
  next_action names. That obligation survives BATCH-001 intact.
- **The HAWK Round-3 specification remains unread**, so `[HAWK25]` table
  references above are relayed from SRC-4, not checked against the spec.
