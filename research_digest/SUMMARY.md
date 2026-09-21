# Research Corpus Summary — /Volumes/Volume/research

*Compiled 2026-07-22 from first-page text extraction of all PDFs, digested by 127 batch workers and 4 synthesis workers. Per-paper one-line summaries: `batches/batch_001.md` … `batch_127.md`. Raw extracts: `manifest.jsonl`. Detailed area syntheses: `synthesis/synthesis_1..4.md`.*

## Scope

- **6,345 research PDFs** catalogued (bank/visa statements excluded — 31 personal financial documents were skipped and not summarized).
- 6,328 (99.7%) yielded usable title/abstract text; 17 were unreadable (14 scanned without text layer, 3 stream errors).
- **`/Volumes/Volume/research2` does not exist** on this machine — nothing to summarize there.
- Naming schemes mix IACR ePrint IDs (`2026-950.pdf`), LNCS/volume-style numeric IDs, Springer ISBNs (`3-540-*.pdf`), and legacy short names (`001.pdf`, `ww2.pdf`).

## What the corpus is

A ~25-year cryptography library (roughly 2000–2026), dominated by IACR flagship proceedings (CRYPTO / EUROCRYPT / ASIACRYPT / TCC / PKC / CHES / FSE) plus classic preprints. Approximate topic mix across the corpus:

| Area | Share | Notes |
|---|---|---|
| Provable security & protocols (MPC, ZK/SNARKs, FE/iO, signatures) | ~35–40% | Largest block; SNARK lineage Aurora→Marlin→Spartan→Halo, GGPR QSPs, Groth16, Bulletproofs precursor |
| Symmetric cryptanalysis & AE | ~20% | Wang-style MD5/SHA-1 breaks, SHA-3 competition, CAESAR, Keccak, AES related-key/biclique |
| Post-quantum (lattices, isogenies, code-based) | ~15–20% | FHE lineage, Ring-LWE, GGH13 multilinear maps → iO boom and bust, SIKE break cluster |
| Side-channel & hardware implementation | ~10% | CHES 2004–2006 time capsule early on: DPA, template attacks, masking/WDDL, FPGA clusters |
| Pairings / IBE / ABE | ~7% | Boneh–Franklin IBE, BLS signatures, Groth–Sahai NIZKs, Dual System Encryption |
| **ECC / ECDLP proper** | **~3–5%** | Thin but high-impact — see below |

## ECDLP / discrete-log highlights (most relevant to this repo)

- **Index calculus & Weil descent**: GHS-lineage papers, Smith's genus-3 isogeny DLP transfer (batch 054 is the densest ECDLP cluster).
- **Small-characteristic DLP earthquake (2012–2014)**: quasi-polynomial Barbulescu–Gaudry–Joux–Thomé; Granger–Kleinjung–Zumbrägel break of the '128-bit' supersingular curve; Joux–Lercier FFS; TNFS development.
- **Records**: 768-bit finite-field DL (Kleinjung et al.), RSA-240 + 795-bit DL, RSA-768 factorization, Certicom **ECC2K-130** GPU/Cell/FPGA break, 113-bit Koblitz curve FPGA cluster (appears twice: `ww2.pdf` = `ww_2014_368.pdf`, a duplicate).
- **Curve arithmetic**: Bernstein Curve25519/Ed25519, Edwards & twisted-Edwards coordinates, GLV endomorphism, double-base chains, Boneh–Shparlinski ECDH bit security.
- **Isogeny-based**: CSIDH (+ genus-theory DDH break of CSIDH group actions) and the 2022 Castryck–Decru **SIDH/SIKE break** with the Robert/Maino–Martindale follow-up cluster.

## Landmark papers elsewhere in the corpus

- **SHAttered** — first SHA-1 collision; Wang–Yu MD5/SHA-0/SHA-1 breaks; Stevens et al. rogue-CA MD5 certificates.
- **zk-STARK** (no trusted setup); Nova and Protostar folding schemes.
- **Beullens — "Breaking Rainbow Takes a Weekend on a Laptop."**
- Garg–Gentry–Halevi multilinear maps → iO wave, ended by total breaks of CLT/GGH maps (Cheon et al., Hu–Jia).
- Ouroboros / Ouroboros Praos (PoS foundations), MuSig2, GEA-1/GEA-2 backdoor break, HKDF (Krawczyk), differential privacy (Dwork et al.), Boneh–Goh–Nissim 2-DNF HE.

## Corpus quality notes

- ~60 anomalous files overall: LNCS front-matter/cover pages, LaTeX class docs, 1-page invited-talk abstracts, a CV, a white paper, slide decks, a few off-topic ML/fairness papers.
- Font-encoding (CID) garbling affects a subset of 2002–2006 PDFs; a handful of extracts are unusable.
- Confirmed duplicate pair: `ww2.pdf` / `ww_2014_368.pdf`; a few other near-duplicates flagged in batch files.
- Some `2026-*.pdf` ePrints are future-dated preprints.

## How to navigate

1. Start from the four area syntheses in `synthesis/`.
2. Drill into any batch of 50 papers via `batches/batch_NNN.md` (one line per paper).
3. `manifest.jsonl` has the raw first-page text for grep-style search (e.g., `grep -i "pollard" manifest.jsonl`).
