# Generator report: lane L4 (GENERIC), TASK-20260930-5c3258

Idea-generator, 2026-10-01. This report covers the three proposals as they are on disk (filed and committed by the dispatcher at d798d2b42; this report does not change them). No runs were made, no ids were minted, and nothing outside the write scope was written.

## Inference

- requested_policy: research-deep
- fallback_used: true
- reason: The card allows fallback (`fallback_allowed: true`). The first two launches of this lane on the session model ended before any file was written:
  - the first was stopped by a spend limit;
  - the second was stopped by a content-safeguards classifier false positive on a discrete-logarithm text.

  So this lane ran on the card's permitted fallback model (claude-opus-5-5, as the runtime reports it; not probe-verified). A session limit interrupted that run once more, after the three records were written. The run was then resumed to write this report.
- Each record carries the same `inference` block (`fallback_used: true`, `model_verified: false`, `bedrock_used: false`).

## Identifiers

| id | used | question filed under |
| --- | --- | --- |
| IDEA-20260930-750de2 | yes | RQ-LHW-1877bb |
| IDEA-20260930-79abd9 | yes | RQ-LHW-1877bb (related: RQ-ECDLP-78dbc5) |
| IDEA-20260930-79c17d | yes | RQ-GRUMPY-964876 |

Unused ids: none.

No proposal was filed under RQ-ECDLP-78dbc5. That lane already holds nine proposals and five hypotheses (selection rules, the Borel, basin and hub ceilings, batch-grown and reselected tables, small-root preprocessing). This session found no candidate that was clearly distinct from those and could survive the required random-relabelling null and decay test. That is a statement about this search only. It is **not** a closure of the lane, and its honest status is `unverified`.

## Records read for overlap

- **Questions:** RQ-LHW-1877bb, RQ-GRUMPY-964876 and RQ-ECDLP-78dbc5, read verbatim via `context/L4-GENERIC.md`.
- **LHW lane, read in full:** IDEA-20260906-ab08cb, IDEA-20260906-3493fe, IDEA-20260906-7d5c16, IDEA-20260906-c37df9 and H-LHW-8e8cff.
- **GRUMPY lane:**
  - IDEA-20260906-7bd805, read in full.
  - IDEA-20260906-c9ac0d, IDEA-20260906-d5defc and IDEA-20260906-a7270e: claim and mechanism heads only.
  - Statements of H-GRUMPY-1ead49, H-GRUMPY-94a295, H-GRUMPY-c09652 and H-GRUMPY-f7f335.
- **Batch lane:**
  - IDEA-20260923-c2a85f, lines 1–140.
  - Grep screen over the other eight RQ-ECDLP-78dbc5 proposals for rainbow, multiple tables, negation, restart, seed compression and bits per entry.
- **Corpus and form:**
  - Literature notes KN-LIT-4794, KN-LIT-7291, KN-LIT-fbe4e0, KN-LIT-3060, KN-LIT-013, KN-LIT-2177 and KN-LIT-4893.
  - KN-FIND-ffe1df (lines 1–60 and 139–258, which contain Theorem C).
  - The 24 generic-rho frontier rows.
  - The form exemplar IDEA-20260926-89886c.
  - `agents/idea-generator.md`, and `docs/inventor-protocol.md` sections 2–5.

## Searches

The crypto-kb index was empty, so all corpus searching used Grep over `ledger/` and `knowledge/`:

- the three question ids, which matched 145 files and listed every proposal and hypothesis in the lane;
- Mersenne, fold-vector and residue-guess patterns, with no match on the low-weight class;
- LHW and low-Hamming patterns;
- Esser, NestedRho and low-weight patterns in `knowledge/`;
- lower-bound, Shoup and 1.154 patterns in the GRUMPY records, with no match;
- grumpy with 1.18, which matched only KN-LIT-fbe4e0. That note cites `docs/BENCHMARKS.md`, which is absent from this checkout.

**Retrieved and read with WebFetch:**
- Landing pages and abstracts of IACR ePrint 2019/931 (Esser–May), 2026/1720 (Kalam–Karmakar–Sarkar), 2019/804 (Delaplace–Esser–May) and 2015/605 (Galbraith–Wang–Zhang).
- The arXiv:2411.07418 abstract and HTML introduction, which quote Gelfond 1968 and Erdős–Mauduit–Sárközy 1986.

**Not retrieved:**
- PDF bodies of ePrint 2019/931 (fetched twice, including the iacr.org archive copy), 2012/294 and 2026/1720 (its summary was unreliable and was not used). Their compressed streams could not be extracted, and local PDF reading needs pdftoppm, which is not installed.
- The ANTS X page (HTTP 503) and Wagner's `fixedsum.pdf` (could not be rendered).
- The Springer chapter (redirects to an authentication page).
- Dinur 2020, Gopalakrishnan–Thériault–Yao 2007 and Mauduit–Sárközy 1997 were seen only as search-result snippets, and the records mark them `recalled`.

**Web searches run:**
- low-weight DLP polynomial memory after Esser–May;
- golden-collision time-space lower bound;
- Gopalakrishnan–Thériault–Yao partial key;
- fixed digit sum in residue classes;
- optimal average-case generic DLP constant (grumpy).

## One-line summaries

- **IDEA-20260930-750de2** — mechanism. On the low-weight DLP in a prime-order group, any congruence filter carried over from subset sum must guess x mod M, at a cost of G_M (the number of residues hit). The guess-and-kangaroo family with M = 2^k ± 1 is proved no better than min(kangaroo, brute force) at leading exponent for k ≥ 1.124w. The concentration ratio D_M is the one measured quantity that could reverse this. Novelty: unverified. Cost: implementation low, compute low (Stage 1 is minutes of integer work with no group operations). Priority: high.
- **IDEA-20260930-79abd9** — measurement. The low-weight DLP with preprocessing, charged in (P, S, T, epsilon, U).
  - Split-advice tables give S·T = |W|·m^{O(1)}; Bernstein–Lange interval tables give S·T² = c·2^m.
  - For alpha < 0.110 this leaves an exponent gap to the adapted floor S·T² ≥ epsilon·|W|; the balanced-point crossover is at alpha ≈ 0.174.
  - The walk-region law S·T² ~ |W + J_T| reduces escape to one quantity: the sumset deficit rho, measured against a random-set null.
  - Novelty: unverified. Cost: implementation medium, compute low. Priority: low.
- **IDEA-20260930-79c17d** — mechanism.
  - Every (even adaptive) three-class schedule has mean ≥ (2/√3)√l − O(1) = 1.1547√l.
  - Negation-map floors are 0.8165 when only cross-sequence matches are checked, and 0.7454 (best class balance) or 0.7559 (equal rates) when within-sequence matches are also checked and s = 2.
  - The constant therefore splits as floor + imbalance loss + overlap loss, measured on H-GRUMPY-1ead49's counter. Fixed thresholds decide whether overlap is forced and how the sqrt 2 negation factor depends on the matching convention.
  - Novelty: unverified. Cost: implementation low, compute low. Priority: medium.

## Recommended first test

Stage 1 of IDEA-20260930-750de2. It computes exact residue-class sizes |W_sigma|, G_M, D_M and C_M/B on eight cells (m ≤ 32), for every odd M ≤ 4095 and for every 2^k ± 1 modulus and its divisors. It runs alongside a random-set null, an interval null, a planted clustered positive control and a decay ladder.

It is the cheapest valid discriminator:
- It needs no group operations or curve instrument, and takes minutes of integer DP and enumeration.
- Its thresholds are fixed in advance: E1 if R ≥ 0.5 at every cell; E2 if R ≤ 0.25 at two or more cells and R falls as m grows.
- It falsifies the counting step of Theorem 3 directly.
- Its negative outcome closes the congruence-filter route at the section-4 standard, and its positive outcome would be a polylog-memory route below kangaroo.

## Honest accounting (docs/inventor-protocol.md §5)

**Objects:**
- 750de2: the residue rho_M of known partial exponents, plus the guessed residue of x. It is a partial action on the known side and branching (b = G_M) on the unknown side.
- 79abd9: the walk region R_T = W + D0 + J_T, a partial-action object priced by |R_T|.
- 79c17d: the pair-count envelope P_n = sum over i<j of n_i·n_j against the solved set C_n.

**Depth of verified structure (derivation level, toy tier; nothing has been run):**
- 750de2: Lemmas 1–2 and Theorem 3 are elementary. P-FOLD-2, H1 and H1' are open.
- 79abd9: the frontier rows are formula-level. The region law (H1) and the floor adaptation P-CGK-W are unproved.
- 79c17d: Theorems F and F± are elementary and unconditional within model M3(B). M3–M5 are empirical.

**dominated_by:**
- 750de2: the family is dominated by kangaroo for alpha above about 0.11, by brute force below that, and by the single-level half-split law and Esser–May (reported) wherever those are cheaper. As an obstruction: n/a.
- 79abd9: n/a (no algorithm claimed). Any walk-advice table is predicted to be dominated by min(split row, interval row).
- 79c17d: n/a (it is a lower bound).

All rows were checked against the generic-rho map; the KR rows are listed in each record's `prior_art.rows_checked`.

**sota_delta:** zero on time, memory and data in all three records. Model and constant deltas:
- 750de2: the transfer price G_M, plus a dominance theorem for Mersenne and Fermat folds.
- 79abd9: the preprocessing frontier for W(m, w), the thresholds 0.110 and 0.174, and the measured quantity rho.
- 79c17d: a proven lower end 1.1547 for the RQ's constant, three negation floors, and a two-term certified decomposition.

**Closures:**
- 750de2 proposes a section-4 closure of congruence filtering with a guessed residue for the low-weight class, conditional on its Stage 1 returning E1.
- Theorem 3 already closes, rigorously, the guess-and-kangaroo family for moduli 2^k ± 1 with k ≥ 1.124w, at leading exponent.
- No other closure is claimed. The batch lane's lack of a new candidate is a search outcome, not a closure.

**Open directions:**
- Approximate (non-exact) group-side filters, which Theorem C covers only in the exact case.
- Nested and representation-based advice for the low-weight class.
- Conjecture C1 of IDEA-20260906-ab08cb.
- A proof of P-CGK-W.
- Arithmetic k-giant schedules (k ≥ 4) measured against their floors f_k.
- For RQ-ECDLP-78dbc5, any candidate that changes the walk region rather than the constant (79abd9's lens applied to full-group tables).
