# Verbatim heuristic transcription — SRC-1 (van Gent & Pulles 2025)

Task TASK-20260802-004, GOAL-HAWK-001 / BATCH-001, 2026-08-02.

**Source of record.** Daniël M. H. van Gent and Ludo N. Pulles, *HAWK: Having
Automorphisms Weakens Key*, IACR Communications in Cryptology, Vol. 2, No. 2,
12 pages, DOI `10.62056/a3qjp2w9p`. Also IACR ePrint 2025/928. Centrum Wiskunde &
Informatica, Cryptology Group, Amsterdam.

Obtained `2026-08-02` from `https://cic.iacr.org/p/2/2/20/pdf`.
PDF `sha256:56107a8a72a662b2475a70ffc2a02a4b5303a2ae4855af01627c9ef3b40baf50`
(554496 bytes); pdfminer.six extraction
`sha256:94ff38cf6737e7d3319305851d0ccb5b248b74cc930a1e72028e4a1fd713d035`
(39268 chars).

---

## Finding that changes the batch: the count is one, not four

`GOAL-HAWK-001.next_action` instructs that the primary sources be filed "with the
**four heuristics** transcribed verbatim and numbered."

**Those four heuristics are not in this paper.** They belong to eprint 2026/1318
(*Cryptanalysis of HAWK: a Guessing Game*, Nelson–Limbrey–Ling–Mendelsohn), whose
abstract states the algorithm assumes "four number-theoretic heuristics" — and
whose full text **could not be obtained** (see `source_access_log.yaml`).

This paper contains **exactly one numbered heuristic**, `Heuristic 1`, plus an
unnumbered group-theoretic heuristic argument in §5. A regex census over the
full extraction found: `Heuristic 1` (numbered, ×1), `Theorem 1`, `Proposition 2`,
`Lemma 1`–`Lemma 3`, and zero occurrences of `Conjecture`.

The goal's next_action therefore **conflates two sources**. That is a defect in the
goal record, recorded here rather than silently worked around; it is carried into
the BATCH-001 evidence record and the goal checkpoint.

---

## Transcription caveat, stated before the transcriptions

The text below is a **pdfminer.six extraction of a two-column PDF containing
LaTeX-set mathematics**. Extraction mangles mathematical layout: superscripts and
subscripts are flattened, some glyphs appear as `(cid:NN)`, square-root and
fraction structure is lost, and display equations are re-flowed. Prose transcribes
faithfully; **formulas do not**.

Every formula below is therefore marked `[EXTRACTION-DAMAGED]` where the rendering
is not trustworthy. **No formula in this file may be relied on for a mathematical
argument without checking it against the typeset PDF.** This is the first named
duty of the validator task TASK-20260802-006.

---

## Heuristic 1 — verbatim, with damage marked

Preceding sentence, giving the definition the statement depends on:

> "[...] let δβ = GH(β)1/(β−1) be the root Hermite factor, and note δβ ≈
> (β/(2πe)) [EXTRACTION-DAMAGED: exponent lost]"

The statement:

> **Heuristic 1.** Suppose Λ ⊆ R2
> n is a nonzero rank-k lattice with λ1(Λ) ≤ √2. If β ∈ Z≥2 satisfies
>
> p2β/k ≤ δ2β−k−1
> β    (2)
>
> then BKZ-β will recover a shortest vector of Λ. In particular, this condition
> holds asymptotically for β = k/2 + 1.

`[EXTRACTION-DAMAGED]` — Equation (2) is **not** reliably rendered. The leading `p`
is an artifact of an extracted `√` glyph, and the subscript/superscript placement
on `δ` has been flattened. The intended statement is a root-Hermite-factor
condition of the shape `√(2β/k) ≤ δ_β^(2β−k−1)`, but **this reconstruction is an
inference by this task, not a transcription**, and it must be confirmed against
the typeset PDF.

Justification as given (prose, transcribes cleanly):

> **Justification.** Because Λ can be identified with a sublattice of Zn, by
> [Duc24, Lemma 2], its volume is at least 1. Note that the projection of a
> shortest vector of Λ onto the terminal block of a BKZ-β tour has an expected
> norm of λ1(Λ) · pβ/k ≤ p2β/k. Moreover, if the terminal block during a BKZ-β
> tour would be a random block, its first minimum would be δ2β−k+1. Thus, if
> Eq. (2) holds, then the [ADPS16] success condition [...] holds.

Methodological basis, §4 opening:

> "In this section, we analyze the hardness of recovering a shortest vector from a
> lattice Λ appearing in Proposition 2. Specifically, we determine the minimal
> block size β such that BKZ-β finds a shortest vector in Λ, using standard
> heuristics in lattice reduction.
>
> We use the methodology based on the "2016 estimates" which were phrased for
> lattices related to Learning with Errors [ADPS16], and verified experimentally
> [AGVW17, DDGR20, PV21]."

---

## The unnumbered group-theoretic heuristic, §5 — verbatim

> **5 Group-theoretic Heuristics**
>
> Our results are strong in that they impose no conditions on the automorphism,
> besides being nontrivial, but they 'only' halve the security parameter of HAWK.
> As [JWL+23] shows, under the stronger assumption that an attacker has access to
> an oracle giving automorphisms of a lattice, SVP can be (probabilistically)
> solved in polynomial time. If instead of having an oracle, the attacker
> generates a single uniformly random automorphism, then we can, as we will argue,
> heuristically break HAWK with high probability.
>
> Suppose σ is uniformly sampled from O(rot(Q)), and let g ∈ Sn be the
> corresponding permutation on the shortest vectors of rot(Q) ∼= Zn modulo sign,
> i.e., on the coordinates [...]

**This is the load-bearing claim of the paper for cryptanalytic purposes and it is
not numbered.** It is the difference between "halves the security parameter"
(the proven-modulo-Heuristic-1 result) and "heuristically break HAWK with high
probability" (the §5 argument). Any downstream citation must say which of the two
it is relying on.

---

## The results Heuristic 1 is consumed by — verbatim

> **Proposition 2.** There exists a polynomial-time algorithm that, given a
> Hermitian form Q of R2 n and σ ∈ O(rot(Q)) \ Gn,Q, computes a nonzero sublattice
> Λ of rot(Q) of rank at most n/2 such that λ1(Λ) ≤ √2.

> **Theorem 1.** Given a Hermitian form Q of the module lattice R2 U ∈ GLn(Z) \
> Gn,Q of Q, then, using standard lattice reduction heuristics, one can solve
> smLIP for Q by running BKZ-β with β = n/4 + 1 on some sublattice Λ constructed
> in polynomial time from U and that has rank at most n/2.

`[EXTRACTION-DAMAGED]` — the Theorem 1 statement is visibly missing a clause: "Given
a Hermitian form Q of the module lattice R2 U ∈ GLn(Z) \ Gn,Q of Q" is not
grammatical, and a phrase such as "and a nontrivial automorphism" has been dropped
by the two-column extraction. **The theorem's hypothesis is therefore NOT reliably
transcribed here.**

Assembly, §6 Conclusion (prose, clean):

> **Theorem 1** now easily follows from combining **Proposition 2** and
> **Heuristic 1**. Namely, given a Hermitian form Q of R2 n and a nontrivial
> Z-automorphism σ, Proposition 2 computes in polynomial time a basis for a
> lattice Λ of rank at most n/2, such that recovering a shortest vector of Λ
> allows solving smLIP for Q. Then, Heuristic 1 shows, heuristically, that BKZ-β
> recovers a shortest vector of Λ when β = rk(Λ)/2 + 1 ≤ n/4 + 1.
>
> Based on the results of Section 5, it is reasonable to suspect that Λ is of much
> lower rank in the average case. Indeed, sampling σ uniformly at random likely
> gives a lattice of rank at most log(n), for which directly solving SVP only
> takes polynomial time in n.

---

## Dependency structure, as this task reads it

**This is a reading, not a transcription**, and is flagged as such:

```
nontrivial Z-automorphism σ  (INPUT — assumed available, not produced)
        │
        ▼
Proposition 2  — PROVEN, polynomial time → sublattice Λ, rank ≤ n/2, λ1(Λ) ≤ √2
        │
        ▼
Heuristic 1    — HEURISTIC (2016 estimates) → BKZ-β recovers λ1(Λ) at β = k/2+1
        │
        ▼
Theorem 1      — smLIP for Q solved at β = n/4+1   ⇒ "halves the security bits"
        │
        ▼
§5 unnumbered  — HEURISTIC, group-theoretic → random σ gives rank ≤ log(n)
                 ⇒ "heuristically break HAWK with high probability"
```

Two observations the goal will need, both **this task's inference and not the
authors' claims**:

1. **The automorphism is an input, not an output.** The paper's own abstract frames
   the result conditionally: the reduction applies "**if** an adversary knows a
   nontrivial automorphism". Nothing transcribed here produces one. The abstract
   further relays that the HAWK team amended omSVP after Luo et al. (Asiacrypt
   2024) and that this work gives "confidence in the soundness of this updated
   definition, assuming smLIP is hard, since there are plausibly no more trivial
   automorphisms" — i.e. **the paper is at least partly reassuring about HAWK**,
   which is the opposite of how a title-level reading suggests.
2. **The two claim levels must not be merged.** "Halves the security parameter"
   rests on Heuristic 1 alone; "break with high probability" additionally rests on
   the unnumbered §5 argument.

---

## What was NOT obtained

- **The four heuristics of eprint 2026/1318** — the actual object
  `GOAL-HAWK-001.next_action` asks for. PDF blocked; see `source_access_log.yaml`.
- **The 30/06 update to 2026/1318** conceding that Heuristic 4 is insufficient.
  The ePrint HTML abstract truncates mid-sentence inside it, as already recorded
  in `KN-LIT-7670`.
- **eprint 2026/890** beyond its abstract (held as `KN-LIT-7648`).
- **The HAWK Round-3 specification.** Not attempted this task; `RQ-HAWK-001`
  records that csrc.nist.gov is unreachable under this harness's network policy.
