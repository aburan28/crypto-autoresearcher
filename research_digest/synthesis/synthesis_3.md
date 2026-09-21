# Synthesis 3 — Batches 065–096 (~1,600 papers, ca. 2004–2012)

## 1. Topic map

My slice covers ASIACRYPT 2004 through EUROCRYPT/TCC 2012, almost entirely Springer LNCS
proceedings blocks identifiable from the file-number runs. Approximate shares:

- **Provable security / theory of crypto (MPC, UC, ZK/NIZK, commitments, definitional
  work, black-box separations)** — ~30–35%. The single largest area; whole TCC blocks
  (066, 069, 072, 073, 077, 078, 082, 086) are dominated by it, plus leakage-resilience
  sub-clusters from 2008 on (083, 085, 087, 090–092, 095).
- **Symmetric cryptanalysis and design** — ~30%. Three eras visible: XSL/XL algebraic
  analysis of AES (065); the Wang-style MD4/MD5/SHA-0/SHA-1 collision wave (067, 068,
  071, 072, 075); then the SHA-3-competition years — rebound/biclique attacks on
  candidates, Grøstl, JH, BLAKE, Keccak, Skein (083, 085, 087, 089, 092, 094) — plus
  eSTREAM stream-cipher breaks (071, 075, 079).
- **Side-channel / hardware implementation (CHES blocks)** — ~12%. DPA/EM/fault attacks,
  masking countermeasures, PUFs/TRNGs, lightweight ciphers, AES/ECC/pairing hardware
  (076, 079, 080, 084, 085, 088, 093).
- **Lattices / PQC / FHE** — ~10%, growing steeply from 2009: NTRU attacks and fixes,
  LWE/Ring-LWE FHE, BKZ analyses, lattice signatures and trapdoors (069, 070, 081, 084,
  085, 087, 090, 091, 093, 094, 096).
- **Pairings / IBE / ABE / functional encryption** — ~8% (066, 070–074, 077, 081–083,
  089–091, 096).
- **ECC / ECDLP** — thin, ~5%. Mostly implementation (Edwards/Twisted Edwards arithmetic,
  GLV, pairing hardware) plus a handful of genuine ECDLP-relevant results (tori/FFS/NFS
  index calculus, Pollard-rho speedups, isogeny DLP transfer, binary-field index
  calculus). Several batches explicitly note ECDLP absence.
- **Other**: multivariate cryptanalysis (HFE/MFE/UOV/SFLASH), RSA/factoring
  (Coppersmith-type attacks, factoring records), game-theory protocols, differential
  privacy outlier.

## 2. Notable papers

- **Batch 066** — Boneh–Goh–Nissim, "Evaluating 2-DNF Formulas on Ciphertexts" —
  foundational partially homomorphic encryption.
- **Batch 067** — Wang–Yu, "How to Break MD5" — the landmark practical MD5 collision.
- **Batch 067** — Nguyen–Stehlé, L² floating-point LLL algorithm.
- **Batch 068** — Wang–Yu–Yin, collisions for full SHA-0 (2^39) and full SHA-1 (2^69).
- **Batch 069** — Bernstein, Curve25519 speed-record ECDH.
- **Batch 069** — Dwork–McSherry–Nissim–Smith, "Calibrating Noise to Sensitivity" —
  foundational differential privacy.
- **Batch 070** — Nguyen–Regev, parallelepiped attack breaking GGH/NTRUSign.
- **Batch 070** — Cheon, Strong Diffie–Hellman problem analysis.
- **Batch 070** — Joux–Lercier, function field sieve for finite-field DLP.
- **Batch 074/083** — Stevens–Lenstra–de Weger et al., chosen-prefix MD5 collisions →
  rogue X.509/CA certificates.
- **Batch 076** — Aoki et al., first kilobit SNFS factorization (2^1039−1).
- **Batch 076** — Bernstein–Lange, Edwards-curve complete addition formulas; PRESENT
  lightweight cipher introduced.
- **Batch 078** — Groth–Sahai, efficient NIZKs for bilinear groups.
- **Batch 078** — Smith, explicit-isogeny transfer of genus-3 hyperelliptic Jacobian DLP
  (~18.6% of curves) — a genuine ECDLP-hardness result.
- **Batch 084** — Biryukov–Khovratovich–Nikolić, related-key attack on full AES-256;
  Waters, Dual System Encryption.
- **Batch 087** — Kleinjung et al., RSA-768 factorization record; Hayashi et al., 676-bit
  DLP in GF(3^6n).
- **Batch 088** — Krawczyk, HKDF; Dunkelman–Keller–Shamir, practical break of full KASUMI.
- **Batch 090** — Boneh–Sahai–Waters, "Functional Encryption: Definitions and Challenges".
- **Batch 093** — Brakerski–Vaikuntanathan, Ring-LWE fully homomorphic encryption;
  Bernstein et al., Ed25519 high-speed signatures.
- **Batch 094** — Bogdanov–Khovratovich–Rechberger, biclique cryptanalysis of full AES;
  Chen–Nguyen, "BKZ 2.0" security estimates.
- **Batch 095** — Joux–Vitse cover-and-decomposition index calculus (151-bit Fp6) and
  Faugère–Perret–Petit–Renault binary-field ECDLP index calculus — the slice's most
  direct modern ECDLP results.

## 3. Era/venue patterns

- **Venues**: near-exclusively IACR LNCS proceedings — ASIACRYPT 2004, TCC 2005–2012,
  PKC 2005–2010, EUROCRYPT 2005–2012, CRYPTO 2006–2011, FSE 2005–2008, CHES 2007–2011.
  File-number runs map cleanly to LNCS volume numbers, giving tidy conference blocks.
- **Institutions/groups**: Bochum (Paar), KU Leuven/COSIC (Preneel, Verbauwhede), IAIK
  Graz dominate the CHES hardware/SCA blocks; ENS Paris/UCL, UCSD, IBM, EPFL recur in
  theory blocks. Frequent authors: Bernstein, Lange, Groth, Waters, Stehlé, Rechberger.
- **Topic drift**: 2004–2007 = symmetric cryptanalysis after Wang + UC/MPC theory;
  2008–2009 = SHA-3 competition, leakage resilience, pairing-based constructions;
  2010–2012 = lattices/FHE/functional encryption surge, biclique era, record
  factorization/DLP computations. ECC remains marginal throughout — implementation- and
  attack-oriented, rarely ECDLP-hardness-focused.

## 4. Anomalies

- **Extraction failures are the dominant anomaly**: dozens of files are CID/hex
  font-garbled or mojibake (e.g., 33290211, 3378_425, 38760080, 40470185, 49650108,
  51570297, 59120206, 62230405, 66320133, 72370136); some batches lose 4–16 of 50
  files (067 is worst with ~16 garbled).
- **Non-papers**: Korean government IT-policy talk (33290425), industry/position talks
  (40040048, 40040362), Regev's "Lattice-based Cryptography" survey (071), numerous
  1–2-page invited-talk abstracts (Peikert 54440072, Menezes 72370009, Joux 72370001,
  Ishai, Camenisch, Tor 68410481), Krawczyk's 2023 AWS slide deck (667slides.pdf) — an
  era-intruding outlier.
- **Fragments**: 60560053 (chart-axis fragments only), 70730563 (figure labels only).
- **Odd filenames**: short IDs like 34.pdf, 407.pdf, 440, 459.pdf, 530.pdf, 546.pdf,
  659.pdf, 679.pdf — mostly real papers despite the names.
- No systematic duplicates flagged; two PRINTcipher papers in 092 are distinct works.
