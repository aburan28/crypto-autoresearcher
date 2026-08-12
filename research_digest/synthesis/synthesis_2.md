# Synthesis 2 — Batches 033–064 (~1,600 papers)

## 1. Topic map

The slice splits into two starkly different eras. Batches 033–053 and 055 are modern (2021–2024, plus a cluster of 2026-dated preprints); batches 056–064 drop back to the 2001–2004 classic era. Batch 054 is a mixed bridge containing the slice's only dense ECDLP core.

Approximate shares across the slice:

- **Theory/foundations: MPC, ZK/SNARKs, provable security — ~45%.** Dominant in every modern batch. MPC alone is ~10 papers per batch in 037–050 (round complexity, garbling, fluid/YOSO MPC, VOLE, secret sharing). Proof systems (IOPs, folding schemes, compressed sigma protocols, Fiat-Shamir analyses, polynomial commitments) are nearly as large.
- **Post-quantum cryptography — ~25%.** Lattices (LWE/NTRU/FHE/signatures, cryptanalysis and estimators), isogenies (a complete arc from SIDH constructions through the 2022 break to countermeasures and constructive reuse), code-based and multivariate schemes. Peak in 034–039, 044–053, 055.
- **Quantum cryptography (unclonable, certified deletion, verification of QC) — ~4%.** Concentrated in 033, 037, 040, 049.
- **Symmetric cryptanalysis and design — ~15%.** A persistent thread in nearly every batch: AES/ChaCha/Trivium/LowMC attacks, division property/cube/MITM methods, NESSIE-era stream ciphers in 057–064, ZK-friendly hashes in 047–048.
- **ECC/ECDLP, pairings, curve arithmetic — ~8%.** Thin in the modern era (isolated items: OMDL/blind Schnorr, El Housni–Guillevic 2-chains, SwiftEC, ECFFT); dense in batch 054 (index calculus, Weil descent, GHS classifications) and the 2001–2004 blocks 056–062 (point counting, GHS, Tate pairing, invalid-curve and special-point SCA).
- **Side-channel / implementations — ~5%.** Concentrated in batch 064 (CHES 2004: DPA/CPA, masking, ECC on smartcards), plus clusters in 055, 059, 061.

## 2. Notable papers

- **14004409.pdf** — Castryck–Decru key-recovery attack on SIDH/SIKE — breaks NIST round-4 candidate SIKEp434 in minutes; the defining cryptanalytic event of the slice.
- **Batch 045 (Eurocrypt 2023)** — Robert's polynomial-time SIDH attack and Maino–Martindale key-recovery — the theoretical core of the SIDH break.
- **Batch 039 (Crypto 2022)** — Beullens, "Breaking Rainbow Takes a Weekend on a Laptop" — practical kill of a NIST PQC finalist.
- **Batch 039** — Nova: Recursive Zero-Knowledge Arguments from Folding Schemes — foundational folding/IVC work.
- **Batch 045** — HyperPlonk — Plonk with linear-time prover over large fields.
- **Batch 051** — Protostar — generic folding scheme for special-sound protocols.
- **Batch 054** — Kleinjung et al., 768-bit prime-field discrete log (NFS-DL record, 2017) — key DLP cost-modeling landmark.
- **130900207** — 521-bit TNFS discrete-log record in Fp6 — finite-field DL record relevant to pairing parameter sizing.
- **Batch 054** — Gaudry–Thomé–Thériault–Diem / Diem index calculus and Joux–Vitse Weil descent papers — the ECDLP cryptanalysis core of the slice.
- **21390212** — Boneh–Franklin, Identity-Based Encryption from the Weil Pairing — seminal pairing-based crypto paper.
- **21390200** — Boneh–Shparlinski on the bit security of ECDH — directly relevant to ECDLP hardness analysis.
- **21390189** — Gallant–Lambert–Vanstone endomorphism point multiplication — classic fast ECC arithmetic (and later SCA target).
- **22480516** — BLS short signatures — seminal pairing-based signature scheme.
- **22480554** — Rivest–Shamir–Tauman ring signatures — foundational anonymity primitive.
- **Batch 060** — Boneh–Gentry–Lynn–Shacham aggregate signatures; Shamir–Tromer TWIRL factoring hardware; von Ahn et al. CAPTCHA.
- **Batch 061** — Krawczyk's SIGMA (basis of IKE); Oechslin's rainbow tables; Barkan–Biham–Keller instant GSM/A5 break.
- **Batch 042** — Hawk lattice signature (137910165); invalidation of the De Feo–Jao–Plût SIDH identification soundness proof (137910237).
- **Batch 040** — Bellare et al. FROST/BLS threshold-signature security hierarchy.
- **Batch 033** — Dory (Lee, transparent polynomial commitments); Devadas et al. iO from LWE; Peikert et al. lattice commitments.
- **Batch 064** — EAX mode (Bellare–Rogaway–Wagner); Brier–Clavier–Olivier Correlation Power Analysis; Gura et al. ECC-vs-RSA on 8-bit CPUs.

## 3. Era/venue patterns

Modern era is almost entirely IACR flagship proceedings, identifiable by sequential LNCS/chapter IDs: TCC 2021 (033), ASIACRYPT 2021 (034–035), EUROCRYPT 2022 (036–037), CRYPTO 2022 + TCC 2022 (038–040), ASIACRYPT/PKC 2022 (042–043), EUROCRYPT 2023 (044–046), CRYPTO 2023 (047–051), ASIACRYPT 2023 (052). Batches 053–056 mix in 2026-dated ePrint preprints. The classic era covers Crypto/Eurocrypt/Asiacrypt 2001–2003, FSE 2003–2004, PKC 2003, CHES 2004 (056–064).

Topic shift is monotonic: classic-era batches center on pairings/ID-based crypto, RSA/OAEP, NESSIE-era symmetric cryptanalysis, and first-generation side-channel work; modern batches are dominated by MPC/ZK and post-quantum, with ECC reduced to isogeny machinery and generic DL-group assumptions. Institutionally, KU Leuven's isogeny group anchors the SIDH-break cluster (045, 046, 052); ENS/MIT/ETH groups recur in the 2002–2003 protocol work.

## 4. Anomalies

- **Unusable extracts:** 130420251 (math-symbol garbage), 135070040 and 14438223 (no text), 22480087 and 22480274 (0 pages), plus ~15 font-remapped/garbled extracts concentrated in 2002–2004 batches (057–064); batch 063 has 13 files that are LNCS series cover pages only.
- **Non-papers/off-topic:** fairness survey (14004458), ML-systems literature review (2026-1043), blockchain-economics paper (2026-999), biometric "gummy fingers" note (25010573), opinion piece (25010566), ancient-padlocks item (28940325), 1-page position essay (18.pdf).
- **Odd filenames:** bare numeric names (134.pdf, 14.pdf, 24.pdf, 26.pdf, 15.pdf, 18.pdf, 19.pdf, 29.pdf, 308.pdf), several being era outliers.
- **Metadata quirks:** "No Author Given" (130900241), no visible authors (14369056); future 2026 dates in 054–056; NUL-byte and MacRoman encoding issues in several chunk files (processing notes, not content anomalies).
- **Duplicates:** none confirmed; 14004255–57 form a two-part series, 2026-979/2026-984 are overlapping-but-distinct works.
