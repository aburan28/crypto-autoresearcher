---
id: KN-TECH-079
type: technique
title: Structural meet-in-the-middle cryptanalysis - Demirci-Selcuk tables, bicliques, and differential meet-in-the-middle
tags: [meet-in-the-middle, demirci-selcuk, biclique, differential-mitm, truncated-differential, precomputation-table, time-memory-data, key-recovery, aes, automated-search, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "Demirci-Selcuk: an offline table of size 2^t indexed by a delta-set's ordered output sequence, matched online against partially decrypted data - the attack is a time-memory-data trade whose three axes must be reported together. Biclique key recovery on a full cipher typically improves on exhaustive search by a small constant-factor exponent, not by an order"
applicability: SPNs with slow enough diffusion that a middle property is computable from few state bytes; the family where memory, not time, is usually the binding cost and therefore where full-cost accounting decides whether a claim stands
source_refs: [KN-TECH-035, KN-TECH-062, KN-TECH-063, KN-TECH-066, KN-TECH-076, KN-LIT-2109, KN-LIT-3723, KN-LIT-5934, KN-LIT-3730, KN-LIT-2639, KN-LIT-4884, KN-LIT-4887, KN-LIT-2701, KN-LIT-2703, KN-LIT-5058, KN-LIT-1471, KN-LIT-2402, KN-LIT-1002]
added: 2026-07-31
superseded_by: null
---

## Method

The differential family's third mode, after statistical distinguishing
(`KN-TECH-062`) and freedom-degree construction (`KN-TECH-066`): **precompute
one half, match the other**.

### Demirci–Selçuk meet-in-the-middle

The property exploited is a *structural* one. Take a **δ-set** — a set of
plaintexts differing in exactly one active byte, taking all its values — and
consider the ordered sequence of some output byte after several rounds. For an
AES-like cipher this sequence is determined by a small number of intermediate
state bytes, so the set of achievable sequences is far smaller than the set of
all sequences.

- **Offline**: enumerate the possible parameter values and build a table of the
  resulting sequences.
- **Online**: guess the outer subkey bytes, build the δ-set, partially decrypt,
  and look the observed sequence up. A miss eliminates the guess.

The attack is a genuine **time-memory-data trade**, and its memory term is
usually the dominant one — which is why this family is where `KN-TECH-035`'s
full-cost rules matter most. Refinements reduce the table by shifting work from
memory to online guessing; the difference-enumeration technique and its
successors are the standard tools (`KN-LIT-2109`, `KN-LIT-3723`), and modern
configurations are found by constraint solvers rather than by hand
(`KN-LIT-5934`, `KN-LIT-3730`, `KN-LIT-2639`) — the same delegation as in
`KN-TECH-076`, with the same model-correctness obligations. The technique
transfers to Feistel constructions (`KN-LIT-4884`) and combines with truncated
differentials (`KN-LIT-4887`).

### Bicliques

A biclique is a small structure covering a few rounds in which every key in a
group maps every state in one set to every state in another. Used to extend a
meet-in-the-middle attack by a few rounds, it produced key-recovery results on
**full** AES (`KN-LIT-2701`) and on full IDEA (`KN-LIT-5058`), and preimage
attacks on the SHA-2 and Skein families (`KN-LIT-2703`).

**These results must be quoted with their margin.** Biclique key recovery on
full AES improves on exhaustive search by a small exponent — it is a genuine
break of the "exhaustive search is best" claim and it is *not* a practical
threat, requiring effort astronomically beyond reach. Reporting it as "AES is
broken" is exactly the overclaim `AGENTS.md` forbids; reporting it as "no
result exists" is the symmetric failure — premature closure — that
`KN-TECH-056` treats as an equal error.

### Differential meet-in-the-middle

The recent hybridisation: use a differential to constrain the state and a
meet-in-the-middle structure to recover the key, so the differential supplies
the filter and the table supplies the search. It sits alongside the
algebraic-MITM variants used against low-complexity designs (`KN-LIT-2402`) and
the MITM preimage line on AES-based hashing (`KN-LIT-1471`, `KN-TECH-066`).

## Program usage

- **The corpus's clearest symmetric example of memory being the real cost.**
  `KN-TECH-035` (full-cost accounting), `KN-TECH-044` (charging memory in
  lattice sieving) and `KN-TECH-050` (memory-charged isogeny path-finding) all
  make the same argument on the asymmetric side; DS-MITM makes it on the
  symmetric side, and the three together are the program's case that a
  time-only exponent is an incomplete claim wherever a table appears.
- **The biclique episode is a two-sided calibration.** It is simultaneously the
  right way to state a small advantage honestly and the standing example of how
  such a statement gets misread downstream. Both readings matter to this
  program: `sota_delta` honesty in one direction, refusal to declare a target
  saturated in the other.
- **Table construction is a structure-for-samples trade**, the same shape as the
  rebound attack's inbound phase (`KN-TECH-066`) and as factor-base design in
  index calculus — where `KN-FIND-007` established that geometry redistributes
  yield rather than creating it. The corresponding question here is whether the
  table genuinely shrinks the search or merely relocates it into memory that
  nobody is charging for.

## Applicability limits

- **Diffusion decides feasibility.** The attack needs the middle property to
  depend on few state bytes; a design with faster diffusion admits no compact
  table.
- **Memory is frequently infeasible even when time is not.** A claim in this
  family that reports time alone has not reported its cost.
- **Bicliques give small exponents.** The improvement over exhaustive search is
  typically a fraction of a bit to a few bits; it is a structural statement, not
  an operational one.
- **Automated configuration inherits `KN-TECH-076`'s hazards** — an incorrect
  model yields a confidently optimal, wrong attack configuration.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The δ-set construction, the
offline-table/online-match structure, the time-memory-data trade and the biclique
mechanism are standard published results, written from established knowledge and
not re-derived here. Demirci–Selçuk's originating paper and
Bogdanov–Khovratovich–Rechberger's biclique paper are named in prose or cited
only through this corpus's title-level records; no identifier was minted for a
paper this corpus does not hold. **The characterisation of the full-AES biclique
advantage as a small exponent improvement over exhaustive search is stated from
established public knowledge; no figure from `KN-LIT-2701` was read**, and this
entry deliberately quotes none. All cited `KN-LIT` records are title-level per
the family note. The framing of this entry as the symmetric-side case for
memory-charged costing, and the comparisons to `KN-FIND-007`, `KN-TECH-044` and
`KN-TECH-050`, are this program's own reasoning.
