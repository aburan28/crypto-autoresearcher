# Synthesis 4 — Batches 097–127 (~1,545 papers)

## 1. Topic map

Approximate shares across the slice (31 batches × ~50 papers):

- **Theory of cryptography / secure computation (~30%)** — the single largest block. MPC and 2PC (SPDZ, TinyOT, MiniLEGO, cut-and-choose, garbled circuits/RAM, ORAM), zero-knowledge and proof systems (NIZK, QSPs, SNARKs, IOPs), UC frameworks, black-box separations, and the 2013–2016 obfuscation/multilinear-maps boom plus its cryptanalysis.
- **Symmetric cryptography (~25%)** — SHA-3-competition hash cryptanalysis (Keccak, Grøstl, Skein), biclique/rebound/MITM attacks on AES and lightweight ciphers (LED, PRINCE, KLEIN, Simon/Speck, Sprout, MISTY1), RC4 biases, CAESAR-era authenticated encryption (CLOC, POET, NORX, AEZ), and Even–Mansour/Feistel theory.
- **Side-channel & hardware security (~15%)** — CHES-driven: DPA/EM/acoustic/cache attacks, masking theory and verification, PUFs, fault attacks, hardware Trojans, white-box crypto. Peaks in batches 098, 103, 110, 116, 122.
- **Lattices / post-quantum (~12%)** — LWE FHE (GSW), BLISS, FHEW, sieving, Ring-LWE weaknesses, NTRU attacks, code-based crypto (McBits), SPHINCS/XMSS.
- **Provable public-key security & pairings-based schemes (~10%)** — signatures, IBE/ABE/functional encryption, structure-preserving signatures, constrained PRFs, KEM/DEM-era classics in the 2002–2004 throwback batches.
- **ECDLP / elliptic curves (~3–5%)** — thin but high-impact: Cheon's algorithm experiments, Weil-descent/index-calculus heuristics, Pollard rho/kangaroo analyses, GLV/GLS and FourQ/Curve41417 implementations, and the ECC2K-130 breaking effort. Finite-field DLP (FFS, NFS-DL, (ex)TNFS, quasi-polynomial small-characteristic DLP) is the stronger "discrete log" thread and mostly targets pairing security rather than ECDLP per se.

## 2. Notable papers

- **78810355-ish (batch 101)** — Garg–Gentry–Halevi, candidate multilinear maps from ideal lattices — launched the iO era.
- **batch 101** — Joux, faster medium-prime index calculus — 1175/1425-bit DLP records.
- **batch 102** — Gennaro–Gentry–Parno–Raykova, Quadratic Span Programs — foundation of zk-SNARKs.
- **batch 102** — Ben-Sasson et al., SNARKs for C — first practical zk-SNARK implementation.
- **batch 102** — Ducas et al., BLISS — landmark lattice signature scheme.
- **batch 103** — Gentry–Sahai–Waters, FHE from LWE (approximate eigenvector method).
- **batch 103** — Bernstein–Chou–Schwabe, McBits — constant-time code-based crypto.
- **batch 107** — Barbulescu–Gaudry–Joux–Thomé, quasi-polynomial DLP in small characteristic — collapsed small-char pairing security.
- **batch 109** — Granger–Kleinjung–Zumbrägel, break of '128-bit' supersingular binary curves.
- **batch 109** — Genkin–Shamir–Tromer, acoustic RSA key extraction.
- **batch 116** — Barbulescu–Gaudry–Kleinjung, Tower Number Field Sieve — revised pairing key sizes.
- **batch 116** — Genkin et al., "pita bread" EM key extraction from PCs.
- **batch 114** — Bernstein et al., SPHINCS; Garay et al., Bitcoin Backbone; Cheon et al., total break of CLT multilinear maps.
- **batch 119** — Bootle et al., inner-product discrete-log ZK argument — precursor to Bulletproofs.
- **batch 120** — Stevens–Karpman–Peyrin, freestart collision for full SHA-1; Groth's 3-group-element pairing SNARK; Renes–Costello–Batina complete addition formulas.
- **batch 122** — Yarom–Genkin–Heninger, CacheBleed; Bos et al., DCA white-box AES break.
- **batches 125–127** — Bernstein et al., breaking Certicom ECC2K-130 (Cell/GPU/FPGA papers).
- **batch 126** — Vaudenay, CBC padding-oracle attack; Boneh–Boyen–Shacham short group signatures.
- **batch 127** — Boneh–Boyen IBE without random oracles; Cramer–Shoup universal hash proofs; Gentry–Szydlo NTRU signature cryptanalysis.
- **batch 097** — Lenstra et al., "Public Keys" — real-world RSA/ECDSA key sanity check; experimental Cheon attack on a 160-bit BN curve (1314 core days).

## 3. Era / venue patterns

The slice is overwhelmingly IACR-flagship proceedings, 2012–2016: CRYPTO/EUROCRYPT/ASIACRYPT, TCC, PKC, FSE, and CHES, identifiable from LNCS-style file numbering. Batches 097–120 march chronologically through 2012→2016; 121 is a bibliographic anomaly; 122–124 resume 2016; 125–127 jump back to 2000–2004 classics plus the ECC2K-130 effort. Recurring institutions/authors: Gentry, Sahai, Waters, Boneh, Bernstein, Joux, Kleinjung, Standaert, Tromer. Topic drift is clear: the 2013 multilinear-maps/iO construction boom turns into a 2015–2016 cryptanalysis wave (zeroizing attacks on CLT/GGH); symmetric work tracks the SHA-3 and CAESAR competitions; small-characteristic DLP collapses mid-slice; quantum-secure symmetric analysis (Boneh–Zhandry, Simon's algorithm) emerges by 2016.

## 4. Anomalies

- **Batch 121**: 48/50 files are LNCS proceedings front-matter/editorial-board pages, not papers (including a future-dated "PKC 2026").
- **Batches 125–127**: ~25 files are garbled font-encoding extractions; 6+ are proceedings front matter; non-papers include Christophe Petit's CV, a PQShield 2022 white paper, an IACR COI policy, a PKI essay, and an OOPSLA program-analysis paper.
- **Duplicates**: eprint_2012_002.pdf = full_gpu_indocrypt.pdf (ECC2K-130 on GPUs); ww_2014_368.pdf = ww2.pdf.
- **Scattered**: ~15 one-page invited-talk abstracts across batches 097–120; several unreadable extracts (74170437, 78810606, 80860135, 84410115, 87310144, 96650356, 96140171); batch 127 has 45 files, not 50.
