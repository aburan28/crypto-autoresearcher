# E/F_{p^5} at p = 2^64 − 2^32 + 1: the deployed small-n regime (2026-09-20)

Galbraith's ECC 2015 verdict — summation-polynomial index calculus is dead for E(F_{2^n}),
prime n > 160 — has held for eleven years and this program is closing that regime as
theorems (SATIC, DREG, SEMBIN, FFD_SEMAEV_MEASUREMENT1). The complement of the verdict is
where the same machinery works: small prime n. The ZK ecosystem then deployed n = 5.

This note opens `RQ-GFPN-c01af8` and five proposals under it, plus two proposals that
close the last untested threads from the same slide deck. Nothing here is a result.

## The two curves

| | EcGFp5 (Pornin 2022) | EcMasFp5 (Polygon Hermez 2025) |
|---|---|---|
| field | F_p[z]/(z^5 − 3), p = 2^64 − 2^32 + 1 | same |
| equation | y² = x(x² + 2x + 263z), double-odd | y² = x³ + 3x + 8z⁴ |
| order | 2n, n 319-bit prime | 320-bit prime, cofactor 1 |
| rational 2-torsion | yes, (0,0) | none |
| twist security (self-reported) | not stated | 101.93 bits |
| security argument | Gaudry ≥ 2^142, JV "above 128" | "inherits 142 bits from the field" |

## The arithmetic the design note did and the arithmetic it did not do

Design note (raw descended system, n = 5, m = 5): systems ≈ p^{2−2/5} = 2^102.4; ideal
degree D ≈ 2^{k(k−1)} = 2^20; per-system floor D² = 2^40 ⇒ total ≥ 2^142; nominal
FGLM 5·D³ ≈ 2^62 ⇒ 2^165.

Symmetrization the curves' own structure provides (FGHR 2014, FHJRV 2014):

| arm | group | \|G\| | D | D² floor → total | 5·D³ nominal → total |
|---|---|---|---|---|---|
| raw | 1 | 1 | 2^20 | 2^40 → **2^142** | 2^62 → 2^165 |
| S_5 (EcMasFp5) | S_5 | 120 ≈ 2^6.9 | 2^13.1 | 2^26 → **2^129** | 2^42 → 2^144 |
| (Z/2)^4 ⋊ S_5 (EcGFp5) | 2-torsion + S_5 | 1920 ≈ 2^10.9 | 2^9.1 | 2^18 → **2^121** | 2^30 → 2^132 |

Read: the advertised 128 is inside the band for EcGFp5 and at the edge for EcMasFp5. The
prime-order curve is the *stronger* of the two against this attack, which is the opposite
of what "cofactor 1 is safer" intuition says. Everything above is a prediction; D_sym ≥
D_raw/|G| because orbits are not free, and FGLM's real exponent on these systems is what
`IDEA-20260920-a639a1` measures. D does not depend on p, so it is measured at toy p and
carried to p = 2^64 by counting systems — that heuristic (HEUR-GFPN-DFLAT) is the one
thing the ladder must establish first.

Two things the design notes do not discuss at all:

- **Oracle-assisted static DH** (Joux–Vitse): ~p ≈ 2^64 queries plus one 4-point
  decomposition, ~2^85–2^93 work. Far below 128 in both dimensions
  (`IDEA-20260920-73dc35`).
- **Cover attacks at n = 5.** The note cites Diem's "prime n ≥ 11 is safe". n = 5 is not
  covered; Gorla–Massierer note some F_{q^5} curves transfer to a genus-5 Picard group at
  Õ(q^{4/3}) ≈ 2^85. Deterministic per-curve check owed (`IDEA-20260920-10547b`).

And one thing arithmetic closes without an experiment: the Joux–Vitse (n−1)-point variant
for *full* DLP needs ≥ p²·4! ≈ 2^132.6 attempts at p = 2^64 (`IDEA-20260920-9e672a`).

## What is opened

| id | class | what | priority |
|---|---|---|---|
| RQ-GFPN-c01af8 | question | deployed F_{p^5} curves: symmetrization-aware cost, SDHP, covers | — |
| IDEA-20260920-a639a1 | measurement | D and per-PDP cost per symmetrization arm; band at p = 2^64 | high |
| IDEA-20260920-73dc35 | cost-model | oracle-assisted SDHP (queries, work) per curve | high |
| IDEA-20260920-10547b | audit | odd-char GHS cover genus, named curves + isogeny class | medium |
| IDEA-20260920-63a902 | audit | SafeCurves-style certificate audit of both curves | medium |
| IDEA-20260920-9e672a | cost-model | JV (n−1) full-DLP variant closed by arithmetic | low |
| IDEA-20260920-0490f5 | theory | degree-2 quotient descent lemma (closes "larger group actions") | low |
| IDEA-20260920-18dc28 | measurement | WDSat + torsion + coset-typed combined arm (Trimoska's future work) | low |

`research/THM_QUOTIENT_DESCENT1.md` carries the proof for 0490f5.

## What is NOT opened, and why

- Distinct coset factor bases, torsion-quotient coordinates, Sarkar–Singh: opened 2026-09-18
  (`IDEA-20260918-c05e71 / -7a11c2 / -5a9a51`).
- Linear-invariance pruning of representation search: already in
  `THM_FALLDEG_INVARIANTS1 §3.1` (Caminata–Gorla).
- BSGS / grumpy-giants constants: `RQ-GRUMPY-964876`.
- Frobenius on subfield curves, ECC2K-130 index calculus: `RQ-FROB-7d8dd4`, `RQ-QSP-f9bbdb`.
- Finite-field-DLP analogy (double cover, Frobenius as low-degree rational function): the
  obstruction on the slide (Aut(E) finite, div(x^q − x) trivial) has not been circumvented by
  anyone since; the transfer-map classification (Kummer ⇒ pairings, formal group ⇒
  anomalous, covers ⇒ GHS) is already the program's no-go gate. Not reopened.
- Trace-zero variety (Gorla–Massierer): requires a subfield curve; neither named curve is
  one (b ∉ F_p by construction). N/A.

## Sources to freeze before any number is quoted

- Pornin, EcGFp5, ePrint 2022/274 (security section §2).
- Polygon Hermez, "Elliptic Curves over Goldilocks", hackmd.io/@Wimet/S1R3RAY5yx (EcMasFp5).
- Joux–Vitse, ePrint 2010/157 / J. Cryptology 2013 (n = 5 relations, SDHP, F4 variant).
- FHJRV, EUROCRYPT 2014 (hal-00935050 — already retrieved under
  `research/equation-schemes-20260905/retrieved-pages/`; unread by this note).
- FGHR, J. Cryptology 2014 ((Z/2)^{m−1} ⋊ S_m).
- Gaudry, J. Symb. Comput. 2009 (n-point decomposition, double large primes).
- Diem, J. Ramanujan Math. Soc. 2003 (odd-char GHS); Galbraith–Hess–Smart, EUROCRYPT 2002.
- Gorla–Massierer, arXiv 1403.0126 (the n = 5 genus-5 remark).
- Kohel, INDOCRYPT 2012 (may already contain the descent lemma).

## Execution order

1. Freeze sources; `63a902` audit so every later cell runs on certified parameters.
2. `a639a1` n = 4 reproduction cell, then the three-prime n = 5 ladder, arms (i)–(iii).
3. `73dc35` rides the same ladder (4-variable system) and reports the SDHP pair.
4. `10547b` cover-genus instrument, validated on a constructed vulnerable toy, then the
   named curves and a bounded isogeny walk.
5. `9e672a`, `0490f5`, `18dc28` as budget allows; each is bookkeeping.

## Required registry edit

`GFPN` must be added to `ecc_areas` in `orchestration/research-priority.yaml` (patch in
`orchestration/research-priority.GFPN.patch`), or `tools/validate_ledger.py` will not
classify the new question as ECC.
