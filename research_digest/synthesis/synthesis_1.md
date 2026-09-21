# Synthesis 1 — Batches 001–032 (~1,600 papers)

## 1. Topic map (approximate shares)

This slice is overwhelmingly **flagship-venue theoretical cryptography, 2016–2021**,
with a single hardware/side-channel-heavy batch at the front.

- **Provable security & protocols (MPC, ZK/SNARKs, FHE/FE/iO, foundations): ~40–45%.**
  The dominant mass. Nearly every batch from 002 onward is built around MPC round
  complexity, garbled circuits, zero-knowledge proof systems (SNARKs/NIZKs/IOPs),
  functional encryption, obfuscation, and impossibility/separation results.
- **Lattices & post-quantum (incl. isogenies): ~20–25%.** LWE/RLWE/Module-LWE
  constructions and cryptanalysis, NIST PQC candidate attacks (WalnutDSA, GeMSS,
  LUOV, ROLLO, LEDAcrypt, Picnic), plus a steady isogeny thread (SIDH/CSIDH/
  SQISign/CSI-FiSh) from 2017 onward.
- **Symmetric cryptanalysis & design: ~12–15%.** Keccak/SHA-1, AES distinguishers,
  CAESAR AE, cube/division-property attacks, tweakable ciphers, stream ciphers
  (Grain/Trivium, A5/1, GEA-1/2).
- **Side-channel / fault / implementation security: ~8–10%.** Concentrated in batch
  001 (CHES 2004–2006: DPA, masking, WDDL/MDPL, FPGA factoring machines) and in
  CHES-2017 subclusters (batches 006–007); thereafter masking theory and leakage
  resilience appear as a persistent minority inside theory batches.
- **ECC / ECDLP proper: ~3–5% — strikingly sparse.** Direct ECDLP/ECC papers are
  rare: scalar-multiplication SCA, Koblitz/Kummer arithmetic, ECDSA signing, a few
  discrete-log records (768-bit p-field DL, RSA-240/795-bit DL, TNFS vs pairing
  curves), generic-group/preprocessing lower bounds, and quantum resource estimates
  for Shor on ECDLP. The corpus's nearest-DLP content is mostly **isogeny-based
  crypto and finite-field DL records**, not ECDLP algorithms.

## 2. Notable papers

- **10401289** — SHAttered: first full SHA-1 collision (Stevens et al., CWI/Google) — landmark practical hash break.
- **10210143** — 768-bit prime-field discrete log record (NFS) — key calibration point for pairing/FSA key sizes.
- **10210146** — Kilobit trapdoored-SNFS prime-field DL computation — exposes trapdoored-prime risk.
- **12171079** — RSA-240 factoring + 795-bit DLP records — the 2019 state-of-the-art records.
- **10529194** — Complete RSA-1024 break in Libgcrypt via sliding-window leakage — famous Flush+Reload-style key recovery.
- **Batch 006** — Ouroboros: first provably secure proof-of-stake blockchain (Kiayias et al.) — foundational PoS paper.
- **Batch 006** — Bellare et al., ratcheted encryption — formal basis for Signal-style messaging.
- **Batch 010** — Ouroboros Praos — second-generation PoS consensus.
- **Batch 017** — zk-STARK: scalable zero knowledge with no trusted setup (Ben-Sasson et al.) — seminal transparent ZK.
- **Batch 017** — Gohr, neural cryptanalysis of Speck32/64 — launched the deep-learning-distinguisher subfield.
- **Batch 017** — Zhandry, compressed-oracle technique — now-standard QROM tool.
- **Batch 015** — Leurent–Peyrin, chosen-prefix collisions for SHA-1 — SHA-1's practical death blow.
- **Batch 015** — Aurora (transparent SNARG) and **Batch 021** — Marlin; **Batch 024** — Spartan; **Batch 032** — Halo Infinite — the canonical modern SNARK lineage.
- **11272266** — CSIDH (Castryck et al.) — seminal commutative isogeny group action.
- **Batch 024 (12171224)** — Castryck–Decru style genus-theory break of DDH for CSIDH group actions — major isogeny cryptanalysis result.
- **Batch 020** — De Feo et al., VDFs from isogenies; Beullens et al., CSI-FiSh with record 154-digit class-group computation.
- **Batch 026 (12491357)** — SQISign: 204-byte post-quantum signatures — compactness record.
- **10822110** — Corrigan-Gibbs & Kogan: discrete-log with preprocessing lower bounds/attacks — canonical generic-group result.
- **Batch 029** — GEA-1/GEA-2 GPRS break (intentional 40-bit backdoor) — high-profile applied cryptanalysis.
- **Batch 031** — MuSig2 — two-round Schnorr multi-signatures, deployed-relevant.
- **Batch 021** — OptORAMa — optimal ORAM, resolving a long-open complexity question.

## 3. Era / venue patterns

- **Batch 001 is a time capsule**: CHES 2004–2006 side-channel/hardware era — Ruhr
  Bochum (HGI), TU Graz (IAIK), UCL Louvain, K.U. Leuven COSIC, Cambridge.
- **Batches 002–032 march chronologically through 2016–2021 flagship proceedings**:
  Eurocrypt/Crypto/Asiacrypt 2016 (002–003) → Eurocrypt 2017 (004) → Crypto/
  Eurocrypt/CHES/Asiacrypt 2017 (005–007) → Asiacrypt 2017/PKC 2018/Eurocrypt 2018
  (008–010) → Crypto/TCC 2018 (011–013) → PKC/Eurocrypt/Crypto/TCC 2019 (014–019)
  → Asiacrypt 2019/Eurocrypt 2020 (020–021) → Crypto/PKC/TCC/Asiacrypt 2020
  (022–027) → Eurocrypt/Crypto 2021 (028–032).
- Topic drift: side-channel hardware work fades after 2017; ZK/SNARKs grow from a
  minority to a co-dominant theme; isogeny crypto appears in 2017, peaks 2019–2021;
  blockchain/consensus emerges 2017–2019; QROM/quantum-proof techniques become
  routine from 2019. Recurring groups: UT-Austin, Aarhus, CWI, CWI/Google, ENS/
  INRIA Paris, KU Leuven, MSR/Stanford/Michigan ZK cluster.

## 4. Anomalies

- **Corrupted/garbled extracts**: 010.pdf, 029.pdf (batch 001); 10031269.pdf (002);
  116940179.pdf (017); 11891120.pdf (018, hex-encoded).
- **Non-papers**: LNCS front-matter/editorial pages (11535218, 11593447, 11745853,
  11818175, 11935230); Springer LLNCS LaTeX class instructions (12105473, 12550135);
  1-page invited-talk abstracts (batch 008 ×2, 121109003, 127110258, 05.pdf in 001);
  1-page no-text files (10210179, 10401132, 12105233); ML fairness paper misfiled
  (11239269, batch 013); stray diagram fragment (12491342); malformed math fragment
  (10993372).
- **Out-of-pattern odd files**: 11.pdf (batch 012, ~2006 pairing smartcard paper),
  119.pdf (batch 019, older IT-2PC paper), 13.pdf (batch 032, ~2006 Joye–Paillier) —
  short non-ePrint filenames among LNCS-ID files.
- **No true duplicates flagged**; a few near-sequential works by overlapping authors
  (topology-hiding computation in 005; updatable encryption in 025) are distinct.
- **Corpus-level observation**: despite a stated ECC/ECDLP focus, this slice is
  ~95% general theory crypto; ECDLP-specific content is a thin minority.
