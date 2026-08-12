# Batch 001 (50 papers)
- Overwhelmingly a CHES 2004–2006 era batch on side-channel analysis: power/EM attacks (DPA, template, stochastic, higher-order) and hardware countermeasures (masking, dual-rail logic, WDDL, MDPL).
- Recurring institutions: Ruhr University Bochum (HGI), TU Graz (IAIK), UCL Crypto Group Louvain, K.U. Leuven COSIC, Cambridge Computer Lab.
- A hardware-implementation sub-thread covers AES S-boxes, modular arithmetic, ECC/Koblitz scalar multiplication, pairing hardware, and factoring machines (SHARK, COPACOBANA, ECM-on-FPGA).
- Elliptic-curve specific items are relatively few: 001 (SCA on ECC scalar mult), 007 (Koblitz), 008 (HECC), 059 (double-base chains), 030 (Tate pairing).
- Six later papers (079, 099, 10031111–10031132, 2013–2016, likely IACR ePrint) shift to protocols: MPC, broadcast encryption, OT, PAKE, tamper resilience.
- Anomalies: 010.pdf and 029.pdf are corrupted/garbled extractions; 05.pdf is a 1-page presentation abstract, not a full paper.

# Batch 002 (50 papers)
- This batch is a coherent slice of mainstream provable-security cryptography from roughly 2016 (Eurocrypt/Crypto/Asiacrypt-era): PKE/IBE/ABE, signatures, garbled circuits, MPC, NIZKs, and tight reductions dominate.
- Strong symmetric-crypto presence: Keccak cryptanalysis, CAESAR authenticated-encryption attacks (ELmD, SCREAM), the MiMC and Sparx cipher designs, Simpira permutations, and tweakable blockciphers.
- Notable side-channel/fault cluster: key-rank estimation, statistical fault attacks on AE modes, masked/shuffled implementation attacks, leakage-resilient PRFs, and low-latency SCA-protected ciphers (PRINCE/Midori).
- Post-quantum/lattice cluster: LPN solving, MQDSS signatures, tightly-secure lattice signatures/IBE, dynamic group signatures, FHE bootstrapping (sub-0.1s), and ideal-lattice hardness in all rings.
- Almost no elliptic-curve/ECDLP content; closest is the tower number field sieve paper (discrete log in F_p^n, relevant to pairing key sizes) — anomalous relative to the corpus's stated ECC focus.
- One anomaly: 10031269.pdf's extracted text is garbled font-glyph encoding (undecodable); no duplicates observed in this batch.

# Batch 003 (50 papers)
- Dominated by 2016-era IACR ePrint papers (Crypto/Asiacrypt/TCC/Eurocrypt style), covering provable-security constructions, cryptanalysis, and post-quantum candidates.
- Direct ECC/ECDLP relevance: bit security of elliptic-curve Diffie–Hellman (101740346), extended Tower NFS threatening pairing key sizes (101740373), supersingular isogeny security analysis (10031307), and Ideal-SVP on structured lattices (10210116).
- Heavy presence of functional/attribute-based encryption, structure-preserving signatures, non-malleable/leakage-resilient codes, MPC round/complexity results, and obfuscation-based primitives (several UT-Austin/Aarhus groups recur).
- Notable cryptanalysis results: key recovery on QC-MDPC, zeroizing attacks on iO over CLT13, LP attack on binary-matrix LWE, improved k-list/SVP sieving.
- No duplicates, garbage, or non-paper content found; all 50 extracts are legitimate research paper first pages.

# Batch 004 (50 papers)
- This batch appears to be drawn from the EUROCRYPT 2017 proceedings (LNCS volume 10210): nearly all 50 files are full research papers from that venue/era.
- Dominant themes: secure multiparty computation (cut-and-choose, round complexity, UC models), indistinguishability obfuscation and functional encryption, and lattice-based cryptography (attacks and constructions).
- Notable for this corpus's ECDLP focus: 10210143 (768-bit prime-field discrete log record via NFS) and 10210146 (kilobit trapdoored-SNFS prime field DL computation); one elliptic-curve arithmetic paper (10210211, Kohel's twisted µ4-normal form over binary fields) and one SIDH/isogeny paper (10210251).
- Symmetric/side-channel cluster present: masking schemes (10210168, 10210174), cube attack on Keccak (10210176), 5-round AES property (10210215).
- Anomaly: 10210179.pdf is a 1-page file with no extractable text — content unknown.

# Batch 005 (50 papers)
- Dominantly 2017-era CRYPTO/EUROCRYPT/TCC-style papers (IDs resemble IACR ePrint 2017/3xx–4xx); heavy focus on theoretical constructions: functional encryption, obfuscation, secure computation, and lattice-based cryptography.
- Strong symmetric-crypto subcluster: impossible-differential and cube cryptanalysis, Keccak/SHA-1 collisions, tweakable blockcipher and AE modes.
- Notable landmark paper: 10401289 — the first full SHA-1 collision (SHAttered, Stevens et al., CWI/Google).
- Notable applied paper: 10401105 — Lindell's fast two-party ECDSA signing, the only elliptic-curve-adjacent work in this batch; ECDLP/pairings/side-channel content otherwise absent.
- One anomaly: 10401132 has no extractable text (1 page).
- Anomalous duo of related papers: 10210328 and 10401284 are sequential works on topology-hiding computation by overlapping authors (not duplicates).

# Batch 006 (50 papers)
- Batch splits cleanly into two venue-era clusters: ~25 theory papers (looks like CRYPTO 2017 proceedings) on MPC, indistinguishability obfuscation, commitments, zero-knowledge, CDS, and lattice techniques; followed by ~25 CHES-style 2017 papers on masking, side-channel attacks, fault injection, and implementation security.
- Notable papers: Ouroboros (first provably secure proof-of-stake blockchain), a UC treatment of Bitcoin, Groth–Maller minimal signatures of knowledge / SE-SNARKs, and Bellare et al.'s ratcheted encryption formalization underlying Signal-style messaging.
- Lattice/post-quantum theme recurs in both halves: Gaussian sampling, LWE-based lossy trapdoor functions, side-channel attacks on QcBits and masked lattice encryption, McBits revisited.
- Side-channel cluster emphasizes masking theory and practice (Boolean↔arithmetic conversion, threshold sharing uniformity, very-high-order masking) plus physical attacks: X-ray fault injection, EM attacks on dual-rail FPGA logic, secure-boot compromise via FPGA SoCs, lidar spoofing.
- No duplicates, non-paper files, or anomalous extracts detected; all 50 entries are research-paper first pages with clear title/abstract text.

# Batch 007 (50 papers)
- Two coherent venue clusters: files 10529xxx are CHES 2017 papers (side-channel attacks/defenses, lightweight and efficient implementations), and files 10624xxx are ASIACRYPT 2017 papers (~30p LNCS format, provable security, cryptanalysis, post-quantum).
- Dominant themes: side-channel analysis and countermeasures (blind SCA, horizontal attacks on ECC, masking, leakage assessment, CNN profiling), lightweight symmetric crypto (PRESENT, GIFT, Gimli, SKINNY, bit-serial hardware), and post-quantum crypto (NTRU, isogenies, LWE/RLWE, MQ signatures, code-based Niederreiter).
- ECC-relevant highlights: systematic horizontal attacks on ECC scalar multiplication (10529167), Kummer-line scalar multiplication over prime fields (106240107), isogeny-based attacks and signatures (106240108, 106240124), and qDSA signatures on Montgomery/Kummer arithmetic (106240214).
- Notable results: complete break of RSA-1024 in Libgcrypt via left-to-right sliding-window leakage (10529194); CacheZoom cache attacks on SGX enclaves (10529203); Grover+Simon quantum attack on the FX construction (106240174).
- No anomalies: all 50 extracts are genuine research-paper first pages; no duplicates, slides, or non-paper content detected.

# Batch 008 (50 papers)
- This batch is drawn from two major conference proceedings: ASIACRYPT 2017 (files 10624xxxx, LNCS vol. 10624) and PKC 2018 (files 10770/10777xxxx), i.e. late-2017 era cryptography.
- Dominant themes: zero-knowledge proofs/SNARKs and secure computation (garbled circuits, MPC, OT), lattice-based and post-quantum cryptography (LWE/SIS/LWR constructions, Rényi divergence, quantum Fiat-Shamir), and obfuscation/multilinear maps.
- Symmetric cryptography is a solid minority thread: AES yoyo distinguishers, Even-Mansour attacks, OCB3 integrity, beyond-birthday MACs, iterated random functions.
- Only two papers touch elliptic curves directly: a faster SIDH isogeny algorithm (Costello–Hisil) and quantum resource estimates for Shor's ECDLP algorithm (Roetteler et al.) — both notable for the corpus's ECC focus.
- Anomalies: two 1-page invited-talk abstracts (Wang on combinatorics in IT-crypto; Moody on the NIST PQC competition) rather than full papers. No duplicates, no non-paper content; the chunk file itself contained 4 stray NUL bytes (cleaned copy used).

# Batch 009 (50 papers)
- This batch is drawn almost entirely from the PKC 2018 and EUROCRYPT 2018 conference proceedings (file IDs 10770xxx and 10822xxx), i.e., top-tier 2017–2018 cryptography.
- Dominant topics: zero-knowledge proofs/arguments (Hamming-weight ZK, subversion-ZK SNARKs, DVNIZK, ZK round complexity), secure computation (OT extension, two-round MPC, covert 2PC, message complexity), and lattice/post-quantum cryptography (LWE equivalence to eDCP, tuple sieving, parallel basis reduction, rounded Gaussian sampling, lattice group signatures, MQ signatures SOFIA).
- Notable ECDLP-relevant paper: 10822110.pdf (Corrigan-Gibbs & Kogan) proves tight generic lower bounds for discrete-log with preprocessing and gives new preprocessing attacks; 10822135.pdf (Micciancio & Walter) formalizes bit security.
- Other highlights: practical cryptanalysis of WalnutDSA (10770207), bootstrapped blockchain consensus without trusted setup (10770257), PKE resistant to parameter subversion from elliptic-curve groups (10770208).
- No non-paper files, garbage extracts, or obvious duplicates found; all 50 entries are genuine research papers.

# Batch 010 (50 papers)
- This batch is a coherent run of what appear to be EUROCRYPT 2018 papers (sequential IDs 10822186–10822378, 18–40 pages each); all 50 are legitimate research papers, no garbage, statements, or slides.
- Dominant themes: secure computation/MPC round complexity (concurrent black-box MPC, garbled RAM, OT-from-MPC, topology-hiding), zero-knowledge/proof systems (SNARGs, SWI, SZK transformations, proofs of sequential work), and random-oracle-model foundations (QROM Fiat-Shamir, correlation intractability, global random oracles).
- Strong secondary threads: symmetric cryptanalysis (boomerang connectivity table, cube attacks, GCM forgeries, CTR missing-difference), lattice cryptography (GLP masking, SVP sieving, RLWE/PLWE reductions, Gaussian sampling), and blockchain consensus (Ouroboros Praos, rational-protocol-design Bitcoin).
- Only one paper touches elliptic curves directly (10822193, supersingular isogeny graphs / endomorphism rings) — ECDLP/ECC content is nearly absent; this batch is mostly theory cryptography.
- Notable named results: OPAQUE asymmetric PAKE, Ouroboros Praos PoS blockchain, Overdrive SPDZ improvements, and the refutation of the Lin–Tessaro iO candidate (10822365).
- Anomalies: none — every file parsed as a valid crypto paper with coherent title/abstract; no duplicates detected.

# Batch 011 (50 papers)
- This batch is overwhelmingly a single-venue slice: nearly all 50 papers are CRYPTO 2018 contributions (recent IACR ePrint numbers, uniform 25–32 page lengths, Springer-style formatting).
- Dominant themes: secure multiparty computation (MPC, OT extension, garbled circuits/RAM, SPDZ variants — ~12 papers) and symmetric cryptanalysis (Grain/Trivium stream ciphers, AES, cube/correlation attacks, MAC forgeries — ~10 papers).
- Secondary themes: lattices/post-quantum (NIZKs from lattices, threshold FHE, extreme-pruning lower bounds, BKW tradeoffs, Mersenne PKE, GGH13 obfuscation attacks), zero-knowledge proofs/SNARKs, and searchable encryption.
- Only tangentially ECDLP-relevant for this corpus: the Algebraic Group Model paper (10993298), the optimal distributed discrete-log protocol (10993301), CDH trapdoor functions (10993227), and non-uniform generic-group bounds (10993327).
- Anomalies: none of the files are non-papers; source chunk contained one stray NUL byte (extraction artifact, cleaned before reading); 10993314 has no visible authors in the extract.

# Batch 012 (50 papers)
- Dominated by theory-of-cryptography papers from the ~2018 CRYPTO/TCC era (numbered ePrint-style files 10993xxx and 11239xxx): secure computation (MPC round complexity, incomplete networks, leakage resilience), obfuscation/functional encryption, and impossibility/black-box separation results.
- Recurring themes: tight security reductions (signatures, NIKE, LRW2), indistinguishability obfuscation and FE (constructions, quantum attacks, Turing-machine variants), ORAM/OPRAM bounds, and quantum-safe primitives (QFHE, pseudorandom quantum states, collapsing hash functions).
- Notable papers: Ball et al. on worst-case Proofs of Work; Pellet-Mary's quantum attack on GGH13-based obfuscators; Boneh et al. "Crypto Dark Matter" PRF candidates; Dodis et al. breaking Facebook's attachment franking.
- Very little elliptic-curve/ECDLP content in this batch despite the corpus focus; the one ECC-adjacent paper is an older smartcard pairing implementation (11.pdf).
- Anomalies: 10993372.pdf is a 1-page malformed math fragment (not a paper); 11.pdf has an odd short filename and is a ~2006 pairing-on-smartcards paper, out of place among 2018 theory papers.

# Batch 013 (50 papers)
- All 50 files are IACR ePrint first pages (IDs ~11239195–11272197, i.e. 2018-era), dominated by TCC 2018 and ASIACRYPT 2018 conference papers on theoretical cryptography.
- Heavy emphasis on MPC round-complexity and security notions (two-round MPC, adaptively secure MPC, black-box constructions) and on foundations/impossibility results (unique signatures, enhanced trapdoor permutations, black-box separations).
- Strong lattice/post-quantum thread: LWE-based traitor tracing, OT, IPFE, GPV-IBE in QROM, quantum lattice enumeration, plus cryptanalysis of NIST PQC candidates (Walnut, DRS).
- Multilinear maps and obfuscation appear repeatedly: CLT13/GGH15 zeroizing-attack-resistant constructions and GGH13 statistical-leak analysis.
- Symmetric/side-channel cluster: masking instantiations, noisy-leakage proofs, Feistel/tweakable ciphers, DS-MITM automation, invariant attacks on Midori-64/MANTIS, hidden-shift quantum attacks.
- Anomalies: 11239269.pdf is an ML fairness paper (algorithmic classification), not cryptography; 11272173.pdf (Costello, Kummer surfaces) is the only isogeny/elliptic-curve paper despite the corpus being mostly ECC.

# Batch 014 (50 papers)
- Dominated by ~2018-era IACR conference papers (CRYPTO/EUROCRYPT/ASIACRYPT ePrint style, 30p LNCS format throughout).
- Strong cluster of pairing-based/attribute-based and tightly-secure primitives: ABS, IPE, ID-KEM, QA-NIZK, tight IBE, ring signatures, functional encryption.
- Large post-quantum cluster: lattices (LWE/RLWR, BKZ, BLISS side-channel), isogenies (CSIDH, ordinary-isogeny key exchange), and cryptanalysis of NIST PQC submissions (RankSign, DAGS, WalnutDSA).
- Notable papers: CSIDH (11272266); Galbraith–Massimo–Paterson on malicious DH/EC parameter validation (114420140); SIFA fault attacks on masked AES (11272244).
- Symmetric crypto and implementation security well represented: MORUS and Keccak/KMAC cryptanalysis, white-box attacks, probing-security tooling, quantum k-xor algorithms.
- No anomalies: all 50 files are genuine research-paper first pages; no duplicates, slides, or non-paper content.

# Batch 015 (50 papers)
- All 50 files are genuine cryptography research papers, circa 2019; filename blocks 114420xxx and 114760xxx correspond to Springer LNCS volumes for PKC 2019 and Eurocrypt 2019 respectively.
- Dominant themes: advanced encryption/functional primitives (IBE/HIBE, ABE/ABS, PRE, IBBE, functional encryption, registration-based encryption) and NIZK/zero-knowledge proof systems (several LWE-based or CDH-based NIZK constructions, Aurora SNARG, QA-NIZK).
- Strong post-quantum presence: lattice-based RIBE, KEMs in the QROM, decryption-failure attacks on NIST candidates, masked binomial sampling, NTRU key generation, isogeny signatures (SeaSign), Picnic multi-target attacks.
- Notable papers: Aurora (transparent SNARG for R1CS), Leurent–Peyrin chosen-prefix collisions for full SHA-1, Zhandry's quantum lightning, Wesolowski's VDF, De Feo–Galbraith SeaSign.
- Side-channel/subversion topics appear (masking at arbitrary orders, kleptographic/cliptographic signatures with offline watchdog), but no ECDLP or elliptic-curve-specific cryptanalysis in this batch.
- No anomalies: no non-paper files, no obvious duplicates; all extracts are first pages with title/abstract intact, though all are truncated mid-text at ~1500 chars.

# Batch 016 (50 papers)
- This batch is a coherent run of EUROCRYPT 2019 proceedings papers (uniform ~28–32 page lengths, sequential file IDs), dominated by theoretical cryptography rather than elliptic-curve/ECDLP work.
- Heavy clusters: lattice/post-quantum cryptography (G6K sieving, ideal-lattice SVP, gadget toolkit, LPN hardness, lattice group signatures, rank-metric Durandal, PQ misuse attacks) and secure computation (MPC, PSI, HSS, NIZKs, ORAM, differential privacy).
- Blockchain topics recur: private proof-of-stake, consensus via herding, state channels, Mimblewimble formalization, blockchain-hybrid secure computation.
- Notable pair: 114760253 builds iO from constant-degree expanding polynomials over R, while 114760350 (Barak et al.) breaks exactly those candidates with sum-of-squares/SDP attacks — a live build-then-break storyline.
- Only one elliptic-curve-relevant paper: 114760273 (quantum circuits for CSIDH isogeny evaluation, Bernstein–Lange–Martindale–Panny); a few others use DH-type assumptions (CDH/DDH/k-Lin).
- No anomalies: all 50 entries are genuine research-paper first pages; no duplicates or non-paper files detected.

# Batch 017 (50 papers)
- Dominated by Eurocrypt 2019 (files 114760xxx) and Crypto 2019 (files 116940xxx) papers: MPC, zero-knowledge, secret sharing, leakage resilience, watermarking, and quantum/post-quantum cryptanalysis.
- Notable papers: zk-STARK ("Scalable Zero Knowledge with no Trusted Setup"), Libra, Gohr's deep-learning attack on Speck32/64, Zhandry's compressed-oracle QROM technique, and the Jaques–Schanck quantum claw-finding cost analysis of SIKE/SIDH.
- Corpus-relevant items (ECC/ECDLP-adjacent): Two-Party ECDSA from Hash Proof Systems; fixed-vs-random generator distinction in group-based assumptions (DL/CDH/DDH preprocessing bounds); quantum cryptanalysis of SIKE.
- Little elliptic-curve or ECDLP material overall; this batch skews toward general theoretical cryptography and symmetric/quantum cryptanalysis.
- Anomalies: two files (11535218, 11593447) are LNCS proceedings front-matter/editorial-board pages, not research papers; one file (116940179) is garbled hex/glyph-encoded extraction, unreadable.
- No obvious duplicates found.

# Batch 018 (50 papers)
- Almost entirely theoretical cryptography, circa CRYPTO/TCC 2019 era: zero knowledge, secure computation, encryption (ABE, FE, FHE), proof systems, and non-malleability dominate.
- Recurring threads: lattice/LWE-based constructions (NIZK, ABE, ZK arguments), quantum security in the QROM (O2H theorem, SNARGs, delegated quantum computation), and storage-proofs (Filecoin replication, proofs of space-time).
- Notable applied results: devastating practical cryptanalysis of OCB2 (ISO-standardized AE mode), Bellare–Ng–Tackmann's AEAD-nonce-privacy revision, and asymmetric message franking for Signal-like messaging.
- No elliptic-curve or ECDLP papers appear in this batch; only tangential number theory (modular inversion hidden number problem).
- Three anomalies: two Springer LNCS volume front-matter pages (11745853, 11818175) and one hex-encoded unreadable extract (11891120).

# Batch 019 (50 papers)
- Almost entirely a theory-of-cryptography proceedings batch: the ID clusters (11891146–11891254, 119210105–119210166) look like TCC 2019-style papers, dominated by MPC, FHE/lattice, and zero-knowledge/PIR topics.
- Lattice/post-quantum crypto is the single largest theme: MP-LWE variants, Ring-LWE reductions, approximate trapdoors, hash-and-sign signatures, QROM KEM reductions, tensor isomorphism group actions, pseudorandom quantum states.
- MPC cluster is deep: preprocessing via FSS, MPC over Z/p^k Z, UC security with stateless tokens, topology-hiding computation, solitary-output full security, PEZ protocols.
- Only one paper is directly elliptic-curve related (119210106, isogeny graphs over RSA moduli / class groups); no ECDLP, side-channel, or pairing-implementation papers — pairings appear only as ABE/SPS/QA-NIZK tools.
- Notable heavyweight papers: Gentry–Halevi compressible FHE/PIR (11891159), Coron–Notarnicola CLT13 cryptanalysis (119210133), Coron–Pereira first CLT13 multipartite key-exchange implementation (119210130).
- Anomalies: `119.pdf` (Jakoby–Liśkiewicz) breaks the numeric ID pattern and is an older-era information-theoretic 2PC paper; no duplicates or non-paper files found.

# Batch 020 (50 papers)
- Dominated by ASIACRYPT 2019 proceedings-style papers (long 26–32 page LNCS formats, single-affiliation author blocks), with a few from EUROCRYPT/CRYPTO 2019 era.
- Strong symmetric-key cryptanalysis and side-channel/leakage cluster: MILP division property, AES exchange attack, A5/1 GSM break, S-box anomaly analysis, duplex/sponge leakage resilience, ISO 17825 TVLA critique, location-based SCA.
- Heavy post-quantum coverage: isogeny crypto (CSIDH/CSI-FiSh, SIDH/SIKE key compression, isogeny VDFs, AKE, Edwards isogenies), lattice crypto (Order-LWE, module-LLL, quantum sieving), LAC attack, code-based signatures and ZK.
- MPC/advanced-protocol cluster: fair/robust MPC round complexity, broadcast message complexity, MCFE/inner-product FE, UC frameworks and commitments, private set union, card-based crypto formal verification.
- Notable papers: De Feo et al. VDFs from isogenies and pairings; Beullens et al. CSI-FiSh with record 154-digit class group; Bardeh–Rønjom first 6-round AES distinguisher; Zhang's rainbow-table-free A5/1 attack.
- No anomalies: all 50 are genuine research-paper first pages; no duplicates detected.

# Batch 021 (50 papers)
- The batch is dominated by what appears to be EUROCRYPT 2020 proceedings (the contiguous 12105xxx series): symmetric cryptanalysis, lattice/post-quantum crypto, ZK proofs/SNARKs, MPC, and secret sharing.
- Notable papers: Marlin (universal/updatable zkSNARKs), OptORAMa (optimal ORAM), Transparent SNARKs from DARK compilers (Supersonic), blind Schnorr signatures in the AGM, and Grover-oracle cost estimates for AES/LowMC relevant to NIST PQC security categories.
- ECC/ECDLP-specific work is sparse: double-base chains for EC scalar multiplication, SPA-resistant genus-2 HECC scalar multiplication, low-weight DLP/subset-sum algorithms, and memory-tightness/scalability analyses of (Hashed) ElGamal over elliptic curves.
- Several side-channel/fault papers: masking with PRGs, fault template attacks, hedged Fiat-Shamir under faults, Gram-Schmidt norm leakage key recovery against Falcon/DLP.
- Anomalies: 11935230.pdf is LNCS series front matter (editorial board page, not a research paper); 12105233.pdf has no extracted text.

# Batch 022 (50 papers)
- Dominated by recent top-venue conference papers (Eurocrypt/CRYPTO-era, ~2020, Springer LNCS style): heavy on post-quantum cryptography, especially isogeny-based (CSIDH appears four times: quantum analysis, c-sieve cost, endomorphism-ring reduction, Lossy CSI-FiSh).
- Strong zero-knowledge / proof-systems cluster: Fractal (transparent recursive SNARKs), SPARKs, statistical Zaps/ZAPRs, sequential-OR signatures, NIZKs in pairing-free groups.
- Substantial lattice/FHE/iO theory block: entropic LWE hardness, candidate iO from split-FHE, sparsifiable-input piO, tight lattice security, lattice FE impossibility, constrained/watermarked PRFs.
- ECC-relevant papers: CSIDH/CSI-FiSh isogeny work, pairing-friendly curves vs Special TNFS (Guillevic), ECM cofactorization speedups, iMessage signcryption analysis, Noise framework fACCE proofs.
- Applied/side-channel presence: Friet fault-detecting AE, Tornado masking compiler, slide attacks, quantum hash collision attacks, NIST PQC KEM oracle-cloning attacks.
- Anomalies: 12105473.pdf is Springer LLNCS LaTeX class instructions, not a research paper; 121059011.pdf is an invited-lecture essay (Silverberg) rather than a technical result.

# Batch 023 (50 papers)
- Dominated by what appear to be ~2020-era conference proceedings (PKC/CRYPTO style): two contiguous ID blocks (12110xxx, 12171xxx) of full papers, mostly 26-31 pages.
- Heavy lattice/post-quantum presence: LWE/RLWE constructions, lattice reduction algorithms (CVPP slicer, enumeration, ModuleSVP, Ideal-SVP), isogeny-based SIKE/CSIDH cryptanalysis and threshold schemes.
- Strong proof-theory and ZK contingent: NIZK extensions, inner-product arguments, compressed Sigma-protocols, SNARGs, witness encryption, memory-tight reductions, indifferentiability.
- DLP/factorization relevance for this corpus: 12171078 (DLP in pairing-relevant fields) and 12171079 (RSA-240 + 795-bit DLP records) are the most directly ECDLP-adjacent.
- Anomalies: 121109003 is a 1-page invited-talk abstract (Ishai, "How Low Can We Go?"), not a full paper; 12171069 is an anonymized submission ("No Institute Given", authors not shown).

# Batch 024 (50 papers)
- This batch appears to be a large contiguous slice of CRYPTO 2020 papers (uniform ~30-page Springer LNCS format, consecutive submission IDs 12171119–12171355).
- Dominant topics: secure multiparty computation (MPC with identifiable abort, FaF-security, synchronous/async fallback, covert security, reverse firewalls), zero-knowledge (NIZK, ZAPs, Spartan zkSNARK, lattice product proofs, Fiat–Shamir analyses), and theoretical foundations (functional encryption, FE amplification, hinting PRGs, incompressible encodings).
- Notable for ECC/isogeny relevance: 12171224 breaks DDH for class group actions (CSIDH) using genus theory — an important result against isogeny-based cryptography.
- Side-channel/leakage papers are well represented (leakage-resilient key exchange, random probing, timing attack on FO transformation/FrodoKEM, leakage-resistance modes guide).
- Post-quantum cryptanalysis appears: LUOV signature attack, algebraic lattice reduction over cyclotomics, measure-and-reprogram for QROM Fiat–Shamir, lattice blind signatures.
- No anomalies: all 50 entries are genuine research papers; no duplicates or non-paper content found.

# Batch 025 (50 papers)
- Two coherent conference runs: files 12171357–12171410 are CRYPTO 2020 (LNCS 12170) papers; files 12491112–12491251 are ASIACRYPT 2020 (LNCS 12491) papers. All ~2020-era full research papers.
- Dominant themes: secure multi-party computation (edaBits, GMW branching, matrix multiplication, RSA modulus generation, round complexity, synchronous/asynchronous MPC), NIST post-quantum cryptanalysis (LEDAcrypt, HQC, Classic McEliece side-channel, quantum sieve costs), and lattice-based constructions (NIZK, IPE, e-cash, KDM-CCA2, M-LWE hardness).
- Strong symmetric-crypto cluster: cryptanalysis of Spook, MiMC, tweakable Even-Mansour, key-alternating ciphers, impossible differentials, division property/monomial prediction, ARX differential models, quantum collision attacks on AES-like hashing.
- Isogeny-based crypto appears twice (B-SIDH, SiGamal) — both later affected by the 2022 SIDH breaks, though the extracts predate that.
- Password-authenticated key exchange shows up twice (UC relaxed PAKE, fuzzy asymmetric PAKE); updatable encryption also twice (Jiang; Boneh et al.) — related but distinct papers, not duplicates.
- No anomalies: every entry is a genuine research paper with title, authors, and abstract; no duplicates, slides, or garbage files detected.

# Batch 026 (50 papers)
- This batch is a nearly contiguous run of ASIACRYPT 2020 proceedings papers (LNCS-style, ~30p each), spanning post-quantum crypto, MPC, ZK proofs, symmetric cryptanalysis, and side-channel masking; the tail (12550xxx) shifts to TCC-style theory papers.
- Strong isogeny-based cluster: CSIDH/group actions (12491283), radical isogenies (12491308), SQISign signatures (12491357), isogeny OPRFs (12491375), and isogeny ring signatures (12491294) — directly relevant to ECDLP-adjacent isogeny research.
- Heavy MPC/secret-sharing presence: threshold multi-key FHE, Galois-ring LSSS, CAFEs, round compression, distributed ZK proofs, and arithmetic secret sharing complexity.
- Side-channel/masking cluster: SILVER verification tool, cryptanalysis of masked ciphers via linear cryptanalysis, and packed-multiplication amortized masking.
- Anomaly: 12491342.pdf (1p) is a stray diagram fragment about a "punctured matrix" XOR scheme — not a paper first page.
- Notable results: SQISign's 204-byte post-quantum signatures, first full-permutation distinguisher on Gimli, and improved algebraic attacks breaking ROLLO NIST candidates' claimed security.

# Batch 027 (50 papers)
- The entire batch is drawn from a single venue and era: TCC 2020 proceedings (LNCS volume 12550, filenames 12550xxx), i.e., modern theory-of-cryptography work — no toy curves or ECDLP experiments.
- Dominant themes: succinct arguments / zero knowledge (SNARKs, IOPs, NIZKs, witness hiding, deterministic-prover ZK), secure multiparty computation (round-optimal MPC, fairness, asynchronous BA), and quantum-era cryptography (classical verification of quantum computation, certified deletion, quantum traitor tracing).
- Secondary themes: blockchains and consensus (ledger combiners, blockchain from non-idealized hashes, secret-keeping blockchains), secret sharing lower/upper bounds, ORAM lower bounds, and foundational/primitive results (extractable OWFs, non-committing encryption, function inversion tradeoffs).
- Discrete-log/DDH appears as a hardness assumption in several constructions (e.g., reusable two-round MPC from DDH, range-trapdoor functions from power-DDH, algebraic group model analyses of decisional assumptions), but no paper is specifically about elliptic-curve cryptography or ECDLP.
- Anomaly: 12550135.pdf is not a research paper — it is the Springer LLNCS LaTeX class instruction document.
- Notable high-impact results: round-optimal (4-round) MPC from minimal assumptions (12550195), first symmetric-key CP-ABE for circuits from LWE (12550137), and the accumulation-scheme foundations for recursive proof composition later used in Halo-style systems (12550115).

# Batch 028 (50 papers)
- This batch is dominated by Eurocrypt/TCC-style 2021-era theory cryptography: MPC round complexity and scaling, zero-knowledge/batch verification, and lattice/FHE constructions.
- A notable isogeny/post-quantum cluster: UC-secure CSIDH OT, hidden-shift attacks on SIDH, twin-smooth-integer sieving for B-SIDH/SQISign, and isogeny-based Delay Encryption.
- Only two elliptic-curve-adjacent implementation papers: Koblitz-curve window-τNAF precomputation (126960004) and the Hidden Number Problem / ECDSA key-recovery paper (126960172).
- Several high-impact cryptanalysis results: ROS problem breaks blind/threshold signatures (126960077), passive key-recovery attacks on CKKS (126960098), and the LUOV nested subset differential attack (126960034).
- Quantum-crypto theory appears repeatedly: post-quantum MPC, quantum software leasing, ROM-vs-QROM separations, and a refutation of the quantum-lightning hardness assumption.
- No anomalies: all 50 files are genuine research-paper first pages; no duplicates, slides, or garbage detected.

# Batch 029 (50 papers)
- Dominated by ~2020–2021 top-venue papers (file numbering and cited venues strongly suggest EUROCRYPT 2021 LNCS vol. 12696 and nearby proceedings); mostly EU/US/IL theory cryptography.
- Big theme: secure computation — MPC (actively secure, covert, NISC, mrNISC, unbounded MPC, constant-overhead binary-field MPC), garbled circuits, function secret sharing, VOLE-PSI, silent OT/Paillier HSS.
- Strong cryptanalysis cluster: FF3 FPE attacks, GEA-1/GEA-2 GPRS break (likely intentional 40-bit backdoor), UOV/Rainbow parameter-breaking attacks, AES key-schedule structure, MITM preimage search, neural distinguisher analysis.
- Side-channel/leakage cluster: masking verification in F2, dummy shuffling in white-box, random probing expansion, Shamir leakage-resilience.
- Post-quantum and lattice cluster: GPU lattice sieving record (dim 180), Ring-LWE ideal SVP, LWE-based iO/mrNISC/MPC, SIDH arithmetic, QROM KEM tightness, lattice VOPRF, quantum proofs (compressed oracle, classical proofs of quantum knowledge).
- No anomalies: all 50 files appear to be genuine research-paper first pages; no duplicates, no non-paper content detected.

# Batch 030 (50 papers)
- Nearly all 50 items are circa-2021 conference papers (LNCS-style preprints, likely PKC/CRYPTO/EUROCRYPT 2021 era) spanning lattice crypto, zero-knowledge, MPC/PSI, signatures, and post-quantum cryptography.
- Lattice/PQC themes dominate: BKZ/uSVP attack cost estimation, slide-reduction convergence, lattice multi-signatures, lattice ZK proofs, I-PLWE hardness, LPN worst-case reductions, and MinRank multivariate schemes.
- ECC/isogeny-adjacent highlights: compact ZK proofs for threshold ECDSA, DH-OPRF blinding weaknesses, SIKE hardware cryptanalysis cost model, and pairing-free SIDH key compression.
- Notable single-author theory results: Niehues' optimally tight VRFs, Zhandry's white-box traitor tracing, Ambrona's generic pair-encoding negation, Nuida's PRG-failure taxonomy.
- Anomaly: 127110258.pdf is a 1-page invited-talk abstract (Ducas, Lattices and Factoring), not a full paper; no non-paper artifacts or duplicates found.

# Batch 031 (50 papers)
- This batch is dominated by theoretical cryptography, apparently a single conference proceedings block (file IDs 12826044–12826226, ~30p each, style matches CRYPTO 2021): MPC, zero-knowledge, lattices, and quantum cryptography.
- Heavy quantum/post-quantum theme: concurrent quantum ZK, post-quantum constant-round ZK, quantum copy-protection, quantum secure computation, QROM security of HMAC, quantum collision attacks on SHA-2, impossibility of quantum VBB obfuscation.
- Strong MPC/secret-sharing cluster: arithmetic secret sharing over Z/p^lZ, broadcast-optimal two-round MPC, ATLAS honest-majority MPC, non-commutative-ring MPC, garbled circuits beating half-gates, black-box round complexity results.
- Notable applied/results papers: MuSig2 two-round Schnorr multi-signatures, KHAPE aPAKE, FIDO2 provable security analysis, linear cryptanalysis of FF3-1/FEA, cryptanalysis of full LowMC, key recovery on all HFE variants (GeMSS), improved MITM on ternary LWE keys.
- Anomaly: despite the corpus being described as mostly ECC/ECDLP/side-channel material, this batch contains essentially no elliptic-curve or ECDLP papers; closest DL-related items are MuSig2, k-out-of-n DL proofs, and DualRing ring signatures. No non-paper artifacts found.

# Batch 032 (50 papers)
- This batch is almost entirely the CRYPTO 2021 proceedings (Springer LNCS ~12825–12828 numbering), so the era is uniform: 2021 flagship-venue theory crypto.
- Dominant themes: secure multiparty computation (YOSO, Fluid MPC, Silver VOLE/OT, GMW-style compilers, unconditional MPC), zero-knowledge/SNARKs (Halo Infinite, state-restoration soundness, batch arguments, compressed Σ-protocols), and secret sharing / extractors / leakage resilience.
- A solid minority covers lattice/post-quantum crypto (LWE ring signatures, FE for Turing machines, compressed Σ-protocols on lattices, faster LLL) and symmetric cryptanalysis (superbox alignment, differential-linear, SPN t-wise independence).
- Notable papers: "Halo Infinite" (PCD without SNARK recursion), "Silver" (silent OT/VOLE from LDPC decoding), "Counterexamples to New Circular Security Assumptions Underlying iO", and the SIDH torsion-point attack paper — the only ECC/isogeny-adjacent work in the batch.
- Anomalies: `13.pdf` is an out-of-sequence older paper (Joye–Paillier prime generation on portable devices, ~2006, 15 pages); `12826339.pdf` is an anonymous submission; `12826431.pdf` shows no authors in the extract. No duplicates or non-paper content found.

# Batch 033 (50 papers)
- All 50 files are consecutive ePrint-style extracts (1304201xx–1304202xx) from a single theory-crypto proceedings volume, almost certainly TCC 2021: foundations, MPC, zero knowledge, commitments, and quantum cryptography.
- Dominant themes: secure multi-party computation (round complexity, adaptivity, communication efficiency — ~12 papers), zero-knowledge/proof systems (SNARGs, ZAPs, sigma-protocols, PoK), and quantum/post-quantum crypto (software leasing, resettable ZK, quantum FHE, key-length extension).
- Notable papers: Dory (transparent inner-product/polynomial commitments, Lee); Chiesa–Yogev tight bounds for Micali's SNARGs; Devadas et al. iO from LWE + succinct sampling; Peikert et al. lattice vector/functional commitments.
- Recurring author clusters: Kamath–Klein–Pietrzak (two papers on adaptive security/garbling), Badertscher (three papers), Hirt–Liu-Zhang–Maurer (adaptive MPC).
- Anomaly for this corpus: zero ECC/ECDLP/side-channel/pairing-attack content — the batch is pure theoretical cryptography despite the corpus focus on elliptic-curve research.
- No duplicates, no non-paper items; all 50 extracts are legitimate research paper first pages.

# Batch 034 (50 papers)
- Dominated by ~2021-era IACR ePrint-style papers (filenames suggest TCC/ASIACRYPT 2021 submissions): broad theory crypto rather than the corpus's ECDLP core.
- Heavy representation of zero-knowledge/SNARK foundations (Lunar, inner pairing products, compressed Σ-protocols, Gentry-Wichs tightness, Sub-ZK) and MPC/secret-sharing (non-interactive MPC via blockchains, PSM, HSS, regenerating codes, garbling).
- Strong lattice/post-quantum cluster: NTRU fatigue analysis, dual LWE attacks on CRYSTALS, quantum sieving, QR-UOV, LWR-based hybrid encryption, QROM KEM reduction tightness.
- Symmetric cryptanalysis cluster: division property, integral distinguishers, Trivium cube attack, Rasta/Dasta algebraic attacks, AES-like rebound attacks, DBL hash modes, SCM AE mode.
- Most ECC-relevant items: OMDL in the generic group model (blind Schnorr/MuSig2), threshold ECDSA via class groups, and a unified treatment of elliptic-curve special-point side-channel attacks.
- Anomaly: 130420251.pdf (1p) is garbage — a fragment of math symbols with no readable paper content.

# Batch 035 (50 papers)
- Batch is a coherent run of ~2021-era conference papers (sequential 130900xxx IDs; LNCS-style formatting, Asiacrypt-like mix), spanning symmetric cryptanalysis, FHE, MPC, and quantum cryptography.
- Dominant themes: symmetric-key cryptanalysis (linear/cube/fault/quantum attacks on Simon, Simeck, LowMC, LightMAC, OCB), homomorphic encryption (BGV/BFV, CKKS transciphering, TFHE), and provable-security foundations (QROM, AGM-in-UC, tight reductions).
- Post-quantum content is strong: NTRU hardness reductions, fault-injection and key-mismatch attacks on NIST PQC Round 3 KEMs, lattice group signatures, isogeny-based MPC and OPRF cryptanalysis.
- Closest to ECDLP/finite-field DL: a record 521-bit TNFS discrete-log computation in Fp6 (130900207); little elliptic-curve-specific material in this batch.
- Notable anomalies: 130900241 lists "No Author Given"; extracts contain NUL-byte artifacts (rendered "/x00") in author lists of 130900235 and 130900337. No duplicates or non-paper items found.

# Batch 036 (50 papers)
- Batch drawn from two consecutive arXiv submission clusters (~2021–2022); content is overwhelmingly PKC/EUROCRYPT-2022-era public-key theory papers.
- Dominant themes: post-quantum cryptography (lattices, isogenies, code-based), zero-knowledge/SNARK constructions, and MPC protocols.
- Strong isogeny thread: Séta encryption, HealS/SHealS, radical isogenies on Montgomery curves, OSIDH attack, torsion-point reductions, and Wesolowski's orientation/endomorphism-ring reductions.
- Lattice-based constructions are pervasive: tight signatures, blind signatures, IPFE, leakage-resilient IBE/ABE, gadget sampling, lockable obfuscation, OLE, and updatable encryption.
- Several SNARK/proof-system papers (Szepieniec, Lipmaa, ECLIPSE, DCR range proofs) plus MPC works (reusable two-round MPC, FaB-DPSS, SPDZ triples, bottleneck complexity).
- No anomalies: all 50 extracts are genuine research-paper first pages; no duplicates, slides, or non-paper content found.

# Batch 037 (50 papers)
- All 50 files are genuine research papers; consecutive IDs (132760xxx) and uniform style indicate one proceedings volume — Springer LNCS 13276, i.e., EUROCRYPT 2022 (part I).
- Dominant themes: zero-knowledge proofs/SNARKs (IOPs, Bulletproofs, elastic SNARKs, SNARGs), secure computation (MPC, garbled circuits/RAM, coin toss, PVSS), and post-quantum crypto (lattices, isogenies, NIST PQC KEM analysis).
- Strong quantum-security thread: quantum attacks/algorithms (filtering for SIS/LWE, Even-Mansour, watermarking PRFs, non-malleable commitments, blind verification of quantum sampling).
- Symmetric cryptanalysis highlights: first correlation attack on full SNOW-V/Vi, DFA breaking DEFAULT's security claim, refined GEA-1/GEA-2 attacks, committing AE (Bellare–Hoang).
- ECC relevance is thin: only 132760128 (SNARK-friendly 2-chains of pairing-friendly curves, El Housni–Guillevic) is directly elliptic-curve/pairing work; several others use DL-group assumptions generically.
- Anomaly: the source chunk contained one NUL byte (unreadable as strict UTF-8); a cleaned copy chunk_037_clean.txt was used for extraction. No duplicates or non-paper items.

# Batch 038 (50 papers)
- Dominated by ~2022-era Eurocrypt/Crypto-style proceedings papers (mostly 30p): secure multiparty computation and round/communication optimality, zero-knowledge, obfuscation, and functional/attribute-based encryption.
- Strong symmetric-cryptanalysis cluster: improved attacks on ChaCha, GIFT-64, AES-like hashing (rebound/Super-Inbound), sponge preimage tightness, and MITM modeling; plus white-box and side-channel work.
- Post-quantum cluster: trilinear-form signatures, lattice isomorphism problem, GeMSS/Rainbow rank attacks, partial key exposure on BIKE/Rainbow/NTRU, and LWE-based ZK.
- ECDLP-adjacent highlights: Groth–Shoup on ECDSA with additive key derivation and presignatures (GGM analysis), and Zhandry's generic-group model comparison (Shoup vs Maurer).
- Anomalies: 135070040.pdf has no extracted text; 134.pdf is an older (mid-2000s) GESS/SFE paper, an era outlier in the batch.

# Batch 039 (50 papers)
- This batch is remarkably homogeneous: all 50 files appear to be papers from a single top-tier conference proceedings (uniform ~30-page extended-paper format, Springer-style abstracts), consistent with CRYPTO 2022; the corpus skews heavily to theory/foundations and post-quantum crypto rather than ECC/ECDLP.
- Dominant themes: post-quantum/lattice-based primitives (SNARKs, ZK proofs, blind/multi-signatures, OT), secure computation (MPC, garbling, ORAM, oblivious retrieval), and symmetric cryptanalysis (differential/linear theory, ARX, sponge and Merkle-Damgård time-space tradeoffs).
- Notable high-impact papers: "Breaking Rainbow Takes a Weekend on a Laptop" (Beullens' practical key recovery killing a NIST PQC finalist) and "Nova: Recursive Zero-Knowledge Arguments from Folding Schemes" (foundational folding-scheme IVC work).
- One elliptic-curve-relevant item: 135070137 accelerates the Delfs–Galbraith algorithm for the general supersingular isogeny problem (isogeny-based crypto); otherwise ECC/ECDLP content is minimal in this batch.
- Anomalies: none serious — all 50 are genuine research papers; the only oddity is a stray "?" character artifact in the author block of 135070245 (Signal Double Ratchet analysis).
- No duplicates detected in this batch.

# Batch 040 (50 papers)
- Dominated by theory cryptography circa 2022: ~25 CRYPTO 2022 papers (135070xxx IDs) followed by ~25 TCC 2022 papers (137470xxx IDs); nearly all are full proceedings papers, no junk items.
- MPC is the single biggest theme (~10 papers): dishonest-majority packed secret sharing, fluid MPC, two-round/round-optimal MPC, randomized encodings, minimal-trust full security, broadcast via packed VSS.
- Second cluster is proof systems: succinct arguments, IOPs, lattice-based sublinear ZK for R1CS, Fiat-Shamir tightness, quantum rewinding, vector commitments over rings, compressed Sigma-protocols.
- Notable applied items: FROST/BLS threshold-signature security hierarchy (Bellare et al.), insider security analysis of MLS, Falcon-style shorter lattice signatures, CSIDH group-action PAKE, proof-of-useful-work blockchain (Ofelimos).
- Quantum cryptography is prominent (~6 papers): unclonable encryption, semi-quantum tokenized signatures, classical verification of quantum computation, PRS/PRFS generators, collusion-resistant copy-protection.
- Essentially no elliptic-curve/ECDLP content; closest items are CSIDH group actions, pairing-free vector-commitment impossibility, and generic-group (Uber/PGG) formalizations.

# Batch 041 (50 papers)
- All 50 entries are genuine research papers, apparently from a 2022-era theory-crypto conference batch (CRYPTO/TCC/ASIACRYPT-style); no non-paper content or duplicates found.
- First block (137470xxx, 35 papers): foundations of cryptography — secure computation complexity (sublinear MPC, SNIR/SNIS decidability, OT complexity), zero-knowledge and proof systems (IOPs, SNARGs, NIZKs), and lower bounds (VRFs, RBE, CGKA, PPAD).
- Second block (137910xxx, 15 papers): symmetric-key cryptanalysis and design (Salsa/ChaCha, SKINNYe-64-256, 3kf9 MAC, deck functions, truncated permutation) plus applied/protocol papers (TLS 1.3 key schedule, puncturable key wrapping).
- Elliptic-curve-relevant highlights: ECFFT Part II (scalable transparent proofs over all large fields via elliptic curves), SwiftEC (faster indifferentiable hashing to elliptic curves), and improved Coppersmith bounds for the EC Hidden Number Problem in ECDH side-channel settings.
- Post-quantum / quantum themes recur: isogeny-based trapdoor claw-free functions, classically verifiable NIZK for QMA, post-quantum insecurity from LWE, quantum analysis of memory-hard functions.
- Processing note: the chunk file was not UTF-8 (MacRoman-encoded); a decoded copy was used for reading. Not a content anomaly.

# Batch 042 (50 papers)
- Entire batch appears to be ASIACRYPT 2022 proceedings papers (uniform LNCS style, ~30 pages each, sequential numbering; an "asiacrypt22" contact email appears in 137910237).
- Dominant themes: zero-knowledge proofs/NIZKs and SNARKs, functional encryption, lattice/post-quantum cryptography (NTRU, LWE, Hawk, SPHINCS+, FO transform), and symmetric cryptanalysis (LowMC, differential-neural, rectangle/linear attacks, OMAC bounds).
- Also represented: secure messaging (ratcheting, AEAD key identification), distributed consensus/blockchain networking (Byzantine agreement, SMR, flooding), searchable/sum-preserving encryption, and isogeny crypto (SIDH proofs, group-action CDH≡DLog).
- Notable: 137910237 shows the De Feo–Jao–Plût SIDH identification scheme's soundness proof is invalid; 137910165 introduces the Hawk lattice signature; 137910083's Mimblewimble fix was deployed in Litecoin MWEB.
- Anomalies: none in content — all 50 files are genuine research papers, no duplicates. (Source chunk file contained 2 stray NUL bytes; a cleaned UTF-8 copy was used.)

# Batch 043 (50 papers)
- Uniform batch of ~2022-era conference papers (Springer LNCS first-page style, mostly ASIACRYPT 2022 and PKC 2022 vintage); all 50 are legitimate research papers, no duplicates or non-paper items.
- Heavy on public-key proof/signature primitives: zero-knowledge arguments, ring/blind/group signatures, vector and functional commitments.
- Strong isogeny-crypto cluster: new isogeny representation/pSIDH (Leroux), radical isogeny "racewalking", CSIDH-based OT/MPC, group-action KEM/NIKE in the QROM.
- FHE and MPC themes recur: NTRU/LWE FHE (FINAL), TFHE bootstrapping, hybrid HE (Elisabeth), YOSO-model encryption, PSI, secret leader election, topology-hiding computation.
- Symmetric cryptanalysis and side-channel work present: MILP boomerang on AES-192, SAT-based 6-round SHA-3 collisions, cube attacks on Trivium, division property for MiMC family, masked fixed-weight sampling.
- Anomalous/notable: "Certifying Giant Nonprimes" (13940083) applies crypto certificates to GIMPS/PrimeGrid prime searches — an unusual application paper; nothing else anomalous.

# Batch 044 (50 papers)
- Almost all papers are 2022–2023 era, LNCS-style conference papers (consistent with PKC/CRYPTO/EUROCRYPT proceedings volumes), spanning post-quantum crypto, ABE/FE, NIZKs, and MPC.
- Strong lattice/post-quantum theme: NTRU efficiency, Kyber anonymity, Mitaka probing attack, LIP hull attacks, SCALLOP isogeny group action, FFI hardness, puncturable PRFs.
- Several applied-crypto attack papers: two independent MEGA key-recovery works (13940136 Heninger/Ryan, 14004044 Albrecht et al.), Chaghri and RIPEMD-160 cryptanalysis, sponge MitM preimage attacks.
- Zero-knowledge and advanced primitives are well represented: polynomial commitments (Dew, private PCS), subverted RSA group NIZKs, fine-grained verifier NIZK, laconic function evaluation, delegation of committed programs.
- Anomaly: `14.pdf` has a non-standard numeric filename and is an older (~2006-era) CEA-LETI side-channel power-analysis paper, out of step with the rest of the batch.
- No duplicates detected; all 50 entries are genuine research-paper first pages.

# Batch 045 (50 papers)
- This batch is strikingly homogeneous: nearly all 50 files are EUROCRYPT 2023 papers (LNCS format, ~29-33 pages), spanning foundations, MPC, signatures, lattices, and symmetric cryptanalysis.
- Isogeny-based crypto is a major theme, dominated by the 2022 SIDH break: Robert's polynomial-time attack, the Maino-Martindale key-recovery attack, SQISign speedups via the Deuring correspondence, and the M-SIDH/MD-SIDH countermeasure proposal.
- Other notable papers: HyperPlonk (Plonk with linear-time prover), SNARGs from DDH, Chopsticks two-round multi-signatures, optimal single-server PIR, and the Batch Bootstrapping I/II series on FHE.
- Several papers address privacy/obliviousness lower bounds (DP data structures, batch PIR, differential obliviousness composition) and quantum-world feasibility/separation results (commitments, OT, Valiant's conjecture).
- Anomalies: none of the files are non-research content; 14004206.pdf (71p) is an unusually long automated-cryptanalysis paper; 14004255/14004256/14004257 form a related two-part series (not duplicates).

# Batch 046 (50 papers)
- The batch is essentially a contiguous run of Eurocrypt 2023 proceedings papers (LNCS-style numbering 14004xxx/14085xxxx), spanning MPC, garbled circuits/RAM, ZK/SNARKs, lattices, isogenies, and symmetric cryptanalysis.
- Most notable paper: the Castryck–Decru key-recovery attack on SIDH/SIKE (14004409.pdf), breaking the NIST round-4 candidate SIKEp434 in minutes; related isogeny works include CSIDH fault attacks (14004332.pdf) and trusted supersingular curve generation (14004354.pdf).
- Strong MPC cluster: garbled RAM (NanoGRAM), actively secure 2PC half-gates, reusable NISC, MrNISC, COT/DPF tree optimizations, arithmetic garbling, and constant-overhead VOLE.
- Symmetric/SCA cluster: truncated boomerang attacks on AES-based ciphers, SHA-3 collision attacks, quantum linear key recovery via QFT, low-noise masking with Mersenne-prime ciphers, and a revisit of Prouff–Rivain masking proofs.
- Anomaly: 14004458.pdf (Rothblum, "Indistinguishable Predictions and Multi-Group Fair Learning") is an algorithmic-fairness survey, not a cryptography paper per se.
- No duplicates or non-paper files found; all 50 extracts are genuine research papers.

# Batch 047 (50 papers)
- Entire batch appears to be CRYPTO 2023 proceedings papers (Springer-style first pages, ~21–35p each), spanning the full modern cryptography spectrum rather than the corpus's nominal elliptic-curve focus.
- Post-quantum themes dominate: lattice cryptography (tight AKE, compact gadgets, LWR hardness barriers, fast lattice reduction, timed crypto), code-based cryptanalysis (Durandal, BIKE), isogeny blind signatures (CSI-Otter), and an attack on the ATFE signature scheme.
- Strong cluster of threshold/distributed signatures and MPC: Sparkle, Snowblind, two-party deterministic Schnorr, Fluid MPC, round-optimal black-box MPC, class-group threshold encryption, Bingo VSS/DKG.
- Symmetric crypto well represented: practical related-key attack on GOST, Griffin ZK-friendly hash, indifferentiability corrections for sum-of-permutations, Squared-Ratio multi-user method, backdoor-avoidance criteria for SPNs, Gaston permutation.
- Elliptic-curve-specific content is thin: only pairing-friendly curve cycles (140850167), the CSIDH class-group action (140850136), and class-group encryption (140850104) touch EC machinery.
- Notable "proof repair" theme: several papers fix flaws in prior security proofs (Dilithium Fiat-Shamir-with-aborts, XMSS/SPHINCS+, sum of permutations). Anomalies: source chunk contained 3 NUL bytes (cleaned for reading); no duplicates or non-paper items found.

# Batch 048 (50 papers)
- Batch is a coherent slice of CRYPTO 2023 proceedings (Springer LNCS vol. 14085, filenames 1408502xx–1408504xx): all 50 files are genuine research papers, no anomalies, no duplicates.
- Dominant themes: lattice/post-quantum cryptography (LWE/RLWE/MLWE, FHE ring packing, LaBRADOR, Orbweaver, lattice succinct arguments, ISIS cryptanalysis) and secure multi-party computation (HSS from sparse LPN, weighted MPC, network-agnostic MPC/DKG, round-optimal coin tossing, OT conversions).
- Second cluster: zero-knowledge / succinct arguments (Brakedown, projection codes for RAM programs, universal arguments, impossibility of algebraic NIZK in pairing-free groups, Fiat-Shamir-with-aborts analysis).
- Smaller but notable threads: symmetric cryptanalysis (Rubato key recovery, differential MITM on SKINNY/AES-256, ChaCha PNB attack, SPN t-wise independence) and quantum-era primitives (certified deletion, EPR-pair secure computation, tests of quantumness certifying qubits).
- Notable papers: practical Schnorr threshold signatures "Olaf" (FROST + Pedersen DKG without AGM), HMAC dual-PRF analysis, Falcon/Mitaka small-q security reductions, Anemoi ZK-friendly permutations.

# Batch 049 (50 papers)
- Dominated by theory/foundations work, apparently from a single proceedings-style ePrint cluster (likely CRYPTO 2023): NIZK, SNARGs, proofs of knowledge, and complexity-based foundations (OWFs, Kolmogorov complexity).
- Heavy MPC coverage: solitary-output MPC, proactive secret sharing, network-agnostic/statistical MPC, YOSO/mobile adversaries, topology-hiding computation, DORAM, Byzantine agreement.
- Strong quantum-crypto cluster: publicly-verifiable/certified deletion (three papers), quantum PKE, unclonable/copy-protection, pseudorandom states with proof of destruction.
- Lattice/post-quantum applied work: anonymous credentials, proof-of-knowledge from Hint-MLWE, DualMS multi-signature, chainable functional commitments, VOLE-in-the-head signatures.
- Very little elliptic-curve content: only the CSIDH/class-group self-pairings paper (140850419) and the ECDSA provable-security limits paper (14369093).
- Anomaly: 14369056 has no visible authors; no duplicates or non-paper files found.

# Batch 050 (50 papers)
- Batch consists of recent IACR-conference-style papers (Crypto/Eurocrypt 2023 era, Springer LNCS front pages), dominated by theory-of-cryptography topics: MPC, consensus/Byzantine agreement, zkSNARKs, and idealized-model analyses (GGM/AGM).
- Strong MPC cluster: broadcast-optimal 4-round MPC, DORAM, YOSO, friends-and-foes security, rational MPC, delayed-party MPC over star networks.
- zkSNARK/proof-system cluster: simulation-extractable SNARK compilation (two related papers, 14369117 and 14369136), distributed-prover interactive proofs, LVD-SNARGs, Schwartz-Zippel mod N for Bulletproofs.
- Post-quantum/lattice/code-based threads: LWE NIKE multi-user security, Ideal-SVP worst-to-average reductions, dual attacks in coding theory, rank decoding/LRPC, lattice Bulletproofs commitments.
- Symmetric-key and QROM results: key-alternating cipher bounds, beyond-birthday MAC forgeries, quantum-secure compressing PRFs, IND-1-CCA KEMs, tight AKE in QROM.
- Anomalies: none — all 50 files are genuine research-paper first pages; extracted text has character-encoding mojibake (ORCID/accents mangled) but is readable. No elliptic-curve/ECDLP-specific papers in this chunk.

# Batch 051 (50 papers)
- This batch is an essentially contiguous run of CRYPTO 2023 (Springer LNCS chapter IDs 14438xxx) papers; venue/era is uniform, ~2023.
- Dominant topics: zero-knowledge proofs / SNARKs / accumulation (Protostar, FRI Fiat-Shamir, Punic, ZK-FEDB), MPC and secret-sharing machinery (ramp hyper-invertible matrices, RMFE, NI-VSS, universal circuits), and post-quantum cryptography (lattice signatures/NTRU, isogeny-based FESTA/CSIDH/pSIDH, code-based LESS/SDitH).
- Strong symmetric-cryptanalysis cluster: ASCON exact security, differential-linear attacks on LEA/Speck, cube attacks, Elisabeth-4 break, MitM on Feistel hashes, HDL attacks.
- Notable papers: Protostar (generic folding for special-sound protocols), Cryptographic Smooth Neighbors (record twin-smooth parameters for SQISign), FESTA (PKE built constructively from the SIDH attacks), Hermes (disproves Bost's conjecture that forward security and I/O efficiency in SSE are incompatible).
- Anomalies: 14438223.pdf has no extracted text (empty extract). No duplicates detected; all 49 remaining items are genuine research-paper first pages.

# Batch 052 (50 papers)
- The batch is a coherent slice of recent conference papers: files 14438240–14438394 appear to be ASIACRYPT 2023 proceedings (LNCS style), and 14602003–14602039 continue in the same format, likely another 2023 LNCS volume.
- Heavy concentration on lattice-based/post-quantum cryptography: LWE attacks and security analysis, FHE bootstrapping, threshold FHE, quantum circuits for AES, and quantum lattice enumeration.
- A notable isogeny cluster: polynomial-time attack on M-SIDH/FESTA (Castryck–Vercauteren), new SIDH countermeasures (binSIDH/terSIDH), CSIDH proof systems, and genus-2 superspecial isogeny cryptanalysis.
- Strong zero-knowledge/proof-systems thread: NIZK frameworks, weak ZK via Goldreich-Levin, MPC-in-the-Head improvements, ZKVM memory consistency, functional proofs.
- Anomaly: none — all 50 entries are legitimate research papers; no duplicates, slides, or garbage found. ECC-specific work is sparse (mainly the Edwards448/E448 point-operation paper and isogeny papers).

# Batch 053 (50 papers)
- Two distinct strata: 44 recent (ePrint-style, ~2023–2024) papers on post-quantum/lattice cryptography, zero-knowledge proofs, signatures, and MPC, plus 6 older mid-2000s works on side-channel attacks, RFID, and zero-knowledge databases.
- Heavy concentration of lattice/post-quantum topics: LWE hardness/estimation, code-based signatures (ReSolveD, R-SDP), lattice MVC, Peregrine/HFERP cryptanalysis, isogeny group actions (SCALLOP-HD).
- Strong ZK/proof-systems cluster: lookup arguments (cq+/Locq), compressed sigma protocols, simulation-extractable KZG/HyperPlonk, vector commitments with range proofs.
- Notable cryptanalysis/backdoor papers: Micali-Schnorr PRG backdoor analysis, Peregrine break, HFERP attack, parallel-ROS attack on isogeny/lattice blind signatures.
- Anomalies: 15.pdf extract begins mid-paper (title not visible); 18.pdf is a 1-page position essay, not a full research paper; no obvious duplicates.

# Batch 054 (50 papers)
- Strong core theme: ECDLP/curve-DLP cryptanalysis — index calculus (Gaudry–Thomé–Thériault–Diem; Diem; Laine–Lauter), Weil descent and Gröbner-basis methods (Joux–Vitse, Petit–Quisquater, Huang–Kosters–Yeo, Nagao), and GHS-attack classifications (Momose–Chao group).
- A second large cluster of 2025–2026 ePrint-style papers (2026-1000 through 2026-1018) covering MPC/VSS/PVSS, post-quantum constructions (UPKE from FESTA, POKÉ weak keys, PQ e-voting, symmetric ABE), quantum cryptanalysis, and blockchain/messaging protocols.
- Classics present: Canetti–Goldreich–Halevi random-oracle critique, Bellare on negligible functions, Renner–Wolf on information reconciliation/privacy amplification, and the Koblitz–Koblitz–Menezes ECC history paper.
- Includes the 768-bit prime-field discrete logarithm computation (Kleinjung et al., 2017), a landmark NFS-DL record relevant to DLP cost modeling.
- Anomalies: 19.pdf is a garbage one-line extract; 1997-015.pdf and 2005-277.pdf are slash/glyph-encoded (font-remapped) text, only partially readable; 2026-1017.pdf extract is a graphical-abstract/highlights page; several 2026 papers carry future (2026) dates.

# Batch 055 (50 papers)
- All 50 files are recent research papers (filenames carry 2026 ePrint-style numbers, many dated May 2026); no legacy ECDLP-era material in this batch.
- Dominant theme is post-quantum cryptography: lattice schemes (CKKS/BFV bootstrapping, ML-DSA/ML-KEM, threshold FHE, discrete Gaussian sampling, lattice estimators), isogeny-based crypto (SQIsign, pushforward attacks, Coppersmith bounds for isogeny HNP), and code-based crypto (Gabidulin EGMC break, QC-MDPC decoding).
- Strong symmetric-cryptanalysis cluster: AES related-differential and 7-round key-independent distinguishers, low-round Feistel plaintext recovery (classical + quantum), a Rijndael-256 SoK, and a Vistrutah FPGA evaluation.
- Side-channel and implementation security is prominent: single-trace attack on LESS, profiling-device-free SASCA on ML-KEM, masked Gaussian sampling, and an ML-DSA reduction-placement audit that found a wolfSSL defect.
- Notable breaks: 2026-972 breaks all 16 EGMC parameter sets (128-bit set reduced to ~35 bits); 2026-1030 gives practical attacks on an isogeny threshold signature scheme; 2026-1019 breaks two PAUKS keyword-search schemes.
- Anomalies: 2026-1043 is an ML-for-autonomous-systems literature review, not a cryptography paper; 2026-979 and 2026-984 are closely related (quantum rejection sampling for lattice Gaussian sampling and dual attacks) by different author teams — overlapping contributions, not duplicates.

# Batch 056 (50 papers)
- Mixed batch: 9 recent (2026-era) preprints followed by a large block of classic ~2001-era papers (Asiacrypt/Crypto/Eurocrypt, with OCR artifacts like "±" for "ffi") on MPC, RSA/OAEP, signatures, and protocols.
- Dominant classic themes: secure multi-party computation (UC commitments, minimal complete primitives, constant-round MPC, robust MPC, secret reconstruction, asynchronous broadcast), RSA padding analysis (Manger's OAEP attack, Shoup's OAEP reconsideration, Fujisaki-Okamoto-Pointcheval-Stern RSA-OAEP proof), and signature schemes (forward-secure, on-line/off-line, shuffle proofs, NSS cryptanalysis).
- Notable landmark papers: Boneh-Franklin's Identity-Based Encryption from the Weil Pairing (21390212), Boneh-Shparlinski on ECDH bit security (21390200), and Gallant-Lambert-Vanstone endomorphism point multiplication (21390189) — the last two directly relevant to ECDLP/ECC.
- Two braid-group cryptography papers (21390469, 21390485) and two server-aided/hidden-number lattice papers (22480021, 22480036) form small clusters; 22480067 (Lenstra's AES-matching key sizes) is a well-known standards discussion.
- Anomalies: 22480087.pdf has no extractable text (0 pages); 2026-999 is a blockchain-economics (portfolio theory) paper, not cryptography per se; 2026-994 is an AI-verification position paper with a crypto accountability layer.

# Batch 057 (50 papers)
- Dominated by early-2000s symmetric cryptanalysis: reduced-round attacks on Camellia, MISTY1, RC6, Skipjack, XTEA/TEA, SC2000, Serpent, and the SOBER/MUGI/Scream stream ciphers (NESSIE/FSE-2002 era).
- Strong cluster of pairing-based and curve papers: BLS short signatures (22480516), Galbraith on supersingular curves (22480497), Gaudry–Gürel point counting (22480482), Weil-pairing credentials (22480535).
- Notable foundational papers: Rivest–Shamir–Tauman ring signatures (22480554), Bellare et al. key-privacy (22480568), Knudsen–Wagner integral cryptanalysis (23650114), Patarin's generic Feistel attacks (22480224).
- Several threshold-crypto and zero-knowledge protocol papers from ENS/MIT groups (Fouque–Stern, Lysyanskaya–Peikert, Fouque–Pointcheval, Courtois MinRank).
- Anomalies: 22480274 has no extractable text (0 pages); 23650232 and 22480107 are severely garbled; 22480241's extract starts mid-paper (no abstract).

# Batch 058 (50 papers)
- Dominated by 2002-era conference papers: the 2442xxxx series is Crypto 2002, the 2501xxxx series appears to be Asiacrypt 2002; a classic early-2000s provable-security vintage.
- Recurring themes: block/stream cipher design and cryptanalysis (AES algebraic structure, tweakable block ciphers, RC4 shuffles, SNOW/Scream, Boolean functions), and the limits of provable security (proof flaws in ESIGN/ECDSA, RO-vs-CT separation, generic-group-model weaknesses).
- ECC/pairing content relevant to the corpus: supersingular abelian varieties (Rubin–Silverberg), fast Tate pairing algorithms (Barreto et al.), zeta functions of hyperelliptic curves in char 2, XTR/LUC bit security via the hidden number problem, and Wagner's generalized birthday attack including EC blind signatures.
- Strong RSA/factoring cluster: Bernstein's factorization circuit analysis, unbalanced RSA with small CRT exponent, RSA padding (PSS, OAEP variants), TLS-RSA security.
- Anomaly: 24.pdf is garbled mojibake (broken font/encoding), not a readable research paper; no summary possible.

# Batch 059 (49 papers)
- Dominated by two 2002–2003 conference proceedings: ASIACRYPT 2002 (2501xxxx files) and PKC 2003 (2567xxxx files); overwhelmingly public-key cryptography, signatures, and provable security.
- Strong block-cipher cryptanalysis cluster: Rijndael/AES dual ciphers and algebraic (XSL) attacks, differential-linear enhancements, boomerang attacks on SHACAL.
- Notable ECC relevance: side-channel/fault attacks on scalar multiplication (Goubin refined DPA, Izu–Takagi exceptional procedure attack, invalid-curve key-validation attacks), Montgomery arithmetic over GF(2^k), char-2 point counting, and Vaudenay's ECDSA curve-certification bypass.
- Pairing-based/ID-based crypto is prominent (Gentry–Silverberg HIBE, Cha–Cheon, Boldyreva GDH threshold/blind signatures, Zhang–Kim blind/ring signatures).
- Anomalies: 25010566 is an opinion/position paper (Crypto-Integrity), and 25010573 is a 2-page biometric fingerprint-spoofing note (gummy fingers) — off-topic for a crypto-theory corpus.
- Classic results present: Dodis VRFs, Groth's verifiable shuffle, Golle et al. exit-poll mixing, Courtois–Pieprzyk XSL, Klimov–Mityagin–Shamir break of neural key exchange.

# Batch 060 (50 papers)
- Batch is almost entirely Eurocrypt/Crypto 2003-era proceedings papers: dominant themes are zero-knowledge/concurrent ZK, secure two-party and multi-party computation, and provable-security foundations (UC model, group signatures, PAKE).
- Strong cryptanalysis cluster: RSA side-channel/partial-key-exposure attacks (Kühn, Fouque et al., Blömer–May, Shamir–Tromer TWIRL), HFE/Quartz multivariate attacks (Courtois et al., Faugère–Joux), block/stream cipher cryptanalysis (EMD mode, shrinking generator, LILI-128/Toyocrypt, related-key theory).
- Elliptic-curve content is a minority but notable: Lercier–Lubicz quasi-quadratic point counting, Hess's GHS attack generalization, Ciet–Lange–Sica–Quisquater fast-endomorphism arithmetic; pairing-based work includes Boneh–Gentry–Lynn–Shacham aggregate signatures and Canetti–Halevi–Katz forward-secure PKE.
- Well-known landmark papers present: CAPTCHA (von Ahn et al.), TWIRL factoring hardware, aggregate signatures from bilinear maps, foundations of group signatures (Bellare–Micciancio–Warinschi).
- Anomaly: 26.pdf is garbled misencoded text (apparent CJK-encoded PDF extraction failure mentioning RSA); no usable content. No duplicates detected.

# Batch 061 (50 papers)
- This batch is almost entirely IACR conference papers from ~2003: the 2729xxxxx files match CRYPTO 2003 (LNCS 2729) and the 2887xxxxx files match FSE 2003 (LNCS 2887).
- Dominant themes: symmetric cryptanalysis (stream ciphers, block ciphers, MACs, NESSIE/AES candidates), provable security theory (UC framework, plaintext awareness, RCCA, zero-knowledge), and key-exchange protocols (SIGMA/IKE, group key exchange, braid groups).
- Notable papers: Katz–Yung scalable group key exchange, Krawczyk's SIGMA (basis of IKE), Barkan–Biham–Keller's instant GSM/A5 ciphertext-only break, Oechslin's rainbow tables, Rubin–Silverberg torus-based cryptography (CEILIDH), Cheon–Jun's polynomial-time break of braid Diffie–Hellman.
- Side-channel content is present but minority: Private Circuits (Ishai–Sahai–Wagner), unified ECC formulae attacks (Stebila–Thériault, file "28.pdf"), DES internal-collision power attack, and a hex-encoded Akkar–Goubin high-order DPA paper.
- Elliptic-curve/ECDLP material is thin here: only ECPP-based primality proving, torus-based crypto, and the ECC side-channel paper touch curve mathematics.
- Anomalies: 6 of 50 files are unusable extracts — 5 with garbled/custom-font-encoded text (28870038, 28870078, 28870093, 28870162, 28870263) and 1 with no text at all (28870107); 28870200 is hex-encoded but fully decodable.

# Batch 062 (50 papers)
- Era/venues: almost entirely 2002–2003 academic cryptography — a large FSE 2003 block (stream ciphers Turing/Rabbit/Helix, block-cipher cryptanalysis), plus ASIACRYPT/PKC/CHES-style papers; filenames look like proceeding article IDs.
- Dominant topics: symmetric cipher design & cryptanalysis (MQ/algebraic attacks, HAVAL collisions, Khazad, traceable ciphers), RSA & factoring (generalized Wiener attack, NFS polynomial selection, RSA-1024/TWIRL estimates, tight reductions, ESIGN security), and ECC/hyperelliptic work (Koblitz scalar multiplication, Picard-curve arithmetic, Tate pairing, index calculus for small genus, AGM point counting).
- Protocol cluster: group signatures (three papers), broadcast encryption / trace-and-revoke / key predistribution (four papers), authenticated key establishment, oblivious transfer, and zero-knowledge arguments.
- Notable papers: Al-Riyami–Paterson "Certificateless Public Key Cryptography" (seminal CL-PKC paper); Coron–Naccache showing Boneh et al.'s k-element aggregate extraction assumption is just CDH; Lenstra et al.'s RSA-1024 factoring estimates.
- Anomalies: 3 extracts are undecodable font-encoding garbage (28870366, 29470042, 29470129); 2 more required hex-glyph decoding but were recovered (28870277 = Wallén, 28870324 = Rabbit); one off-topic item (ancient Chinese padlocks, 28940325); one odd filename ("29.pdf").

# Batch 063 (50 papers)
- Dominated by early-2000s public-key cryptography papers (mostly LNCS-style, 13–19 pages): Diffie–Hellman hardness variants, pairings/ID-based schemes, signcryption, PKI certificate revocation, and mix-nets/voting.
- A strong stream-cipher cryptanalysis cluster: algebraic attacks (summation generators, SOBER, fast algebraic attacks, S-boxes, E0/Bluetooth), correlation attacks, and Boolean function theory (bent, resilient, rotation-symmetric).
- Elliptic-curve content is thin: only King's GF(2^n) point compression and Akishita–Takagi's isogeny countermeasure analysis against ZVP/Goubin side-channel attacks, plus one hardware DPA countermeasure paper (asynchronous circuits).
- Thirteen files are Springer LNCS proceedings volumes whose extract is only the series cover page (no paper title); two have identifiable titles (LNCS 149 Cryptography 1982 workshop, LNCS 209 EUROCRYPT'84).
- Four files (29470229, 29470246, 29470303, 30170094) are garbled/mojibake extracts that cannot be summarized.

# Batch 064 (50 papers)
- Batch is almost entirely two 2004 conference proceedings: FSE 2004 (LNCS 3017, filenames 3017xxxx = page numbers) covering stream/block ciphers, modes of operation, and related-key analysis; and CHES 2004 (LNCS 3156, filenames 3156xxxx) covering side-channel attacks/countermeasures and cryptographic hardware.
- Dominant themes: power analysis (DPA/CPA/second-order, masking countermeasures), ECC hardware implementations (GF(p)/GF(2^m) arithmetic, smartcard coprocessors), stream-cipher design and cryptanalysis (HC-256, RC4/RC4A, SOBER-128).
- Notable papers: HC-256 (Wu); EAX authenticated-encryption mode (Bellare–Rogaway–Wagner); Correlation Power Analysis (Brier–Clavier–Olivier); ECC vs RSA on 8-bit CPUs (Gura et al., Sun Labs); fault analysis of stream ciphers (Hoch–Shamir).
- Anomalies: 4 extracts (30170261, 30170409, 30170454, 31560176) are unreadable due to broken font encoding (glyph codes like /D6/CT); source chunk contained stray NUL bytes (a cleaned UTF-8 copy was used); 30170483 is only a 1-page extended abstract; the two Maximov papers (30170483, 308.pdf) overlap in topic but are distinct works.

# Batch 065 (50 papers)
- Dominated by ASIACRYPT 2004 (LNCS 3329, the `3329xxxx` files) and TCC 2005 (LNCS 3378, the `3378_xxx` files) proceedings — era ~2004–2005, mostly symmetric crypto, provable security, and protocol theory.
- Notable cluster of algebraic-cryptanalysis papers: XSL analysis (Cid–Leurent), XL bounds (Diem), and XL-vs-Gröbner comparison (Ars–Faugère et al.), collectively deflating XSL/XL claims against AES.
- Strong hash-function mini-theme: three papers on UOWHF domain extenders and higher-order UOWHFs (Sarkar; Hong–Preneel–Lee), plus timestamping security (Buldas–Saarepera).
- Little elliptic-curve content: one curve-based hardware coprocessor paper (Sakiyama et al.) and one pairing-based group signature (Nguyen–Safavi-Naini); ECDLP itself is absent.
- Anomalies: three files (33290211, 33290445, 3378_151) are garbled mojibake extracts with unidentifiable titles; 33290425 is a Korean government IT-policy talk, not research; 32 and 33290076 are 1-page position/talk abstracts.

# Batch 066 (50 papers)
- Two coherent conference blocks: `3378_*` files are TCC 2005 (LNCS 3378) theory papers — steganography, simulation-based/UC security (incl. quantum QKD), secure computation, privacy; `3386*` files are PKC 2005 (LNCS 3386) papers — RSA analysis, threshold RSA, password-based key exchange, multivariate cryptanalysis, identity-/certificateless-based encryption.
- Notable papers: Boneh–Goh–Nissim "Evaluating 2-DNF Formulas on Ciphertexts" (foundational partially-homomorphic encryption); Cramer–Damgård–Ishai share conversion; Renner–König UC privacy amplification against quantum adversaries; Bleichenbacher's pseudoprime attack on GNU Crypto SRP.
- Nice pair: 33860246.pdf proposes the Tractable Rational Map signature scheme and 33860261.pdf (Joux et al.) cryptanalyzes it — same venue, proposal and break.
- Anomalies: 4 of 50 files unusable — 3378_425.pdf has no extracted text (0p), and 3378_170.pdf, 3378_494.pdf, 3378_530.pdf are garbled font-mapped extractions; titles unrecoverable from the text.
- Little elliptic-curve/ECDLP content in this batch; pairing-based work appears only in the identity-based papers at the end of the PKC block.

# Batch 067 (50 papers)
- Dominated by 2005-era Springer LNCS proceedings: the 34940xxx filenames match EUROCRYPT 2005 (LNCS 3494) and the 35570xxx filenames match FSE 2005 (LNCS 3557); a few stray files (34.pdf, 35.pdf, 348.pdf, 33860420.pdf) are CHES/CT-RSA-era papers.
- Two strong thematic clusters: symmetric cryptanalysis (Wang et al. MD4/MD5 breaks, SHA-0/SHA-1 collisions, RC4 biases, second-preimage attacks, T-functions, stream-cipher designs) and theoretical/public-key crypto (commitments, oblivious transfer, UC security, HIBE, traitor tracing, VRFs, biometric authentication).
- ECC-adjacent content is present but secondary: bilinear-map constructions (VRF, HIBE, traitor tracing) and two hardware ECC papers (8051 co-design, FPGA Koblitz-curve multiplication); lattice/Coppersmith work (L² algorithm, Blömer-May toolkit, RSA partial key exposure) rounds it out.
- 16 of 50 files are garbled extractions (hex-glyph CID-encoded text or mojibake with no recoverable title/abstract); 34940235.pdf and 35570124.pdf also begin with readable title/author fragments but the body is garbled.
- Notable landmark papers: Wang-Yu "How to Break MD5", Boneh-Boyen-Goh constant-ciphertext HIBE, Bernstein's Poly1305-AES, Kelsey-Schneier second preimages, Nguyen-Stehlé L² algorithm.

# Batch 068 (50 papers)
- Mid-2000s Springer-style conference papers (c. 2005, FSE/SAC/CRYPTO era); split roughly evenly between symmetric cryptanalysis and provable-security protocol work.
- Landmark hash-function cryptanalysis: Wang–Yu–Yin's collisions for full SHA-0 (2^39) and full SHA-1 (2^69), plus attacks on MD2, and stream ciphers (RC4, VMPC, RC4A, Mugi, bit-search generator).
- Side-channel/fault theme: AES S-box masking, DPA-vs-S-box transparency order, fault analysis of RC4, padding oracles with secret random IVs.
- Protocol theme: MPC without authentication, constant-round MPC, NIZK characterizations, secret sharing, broadcast encryption (Boneh–Gentry–Waters), HMQV, HB+ RFID authentication.
- ECDLP relevance is thin: one paper on index calculus for the DLP on algebraic tori (Granger–Vercauteren), plus a CDH-based signature and HMQV in the discrete-log setting.
- Anomalies: 35570282.pdf and 35570324.pdf are garbled font/CID-mapped extractions; 35570357.pdf has no extracted text; 368.pdf is raw hex-CID garbage (4 extraction failures total).

# Batch 069 (50 papers)
- Dominated by two LNCS proceedings volumes: 3876xxxx files are TCC 2006 papers (zero-knowledge, MPC, commitments, randomness, complexity), 3958xxxx files are PKC 2006 papers (signatures, encryption, cryptanalysis, DLP).
- Notable papers: Bernstein's Curve25519 speed-record ECDH; Dwork–McSherry–Nissim–Smith "Calibrating Noise to Sensitivity" (foundational differential privacy); Mantin's practical RC4/WEP attack; Bleichenbacher–May small CRT-exponent RSA attack; Commeine–Semaev Number Field Sieve DLP algorithm.
- Strong zero-knowledge theme: concurrent ZK without assumptions, NIZK from homomorphic encryption, ZK with restricted random oracles, plus MPC/dispute-control and VSS results.
- Cryptanalysis of discrete-log-based systems appears repeatedly: NFS for DLP in F_p, attack on a proof of knowledge of discrete log, error correction in the exponent.
- Anomalies: 7 files have broken extraction — 38760080 (ASCII-code-per-character encoding, partially decodable), 38760286 / 38760486 / 38760565 (garbled CID-font garbage), 39580015 / 39580192 (math-symbol-only fragments), 39580243 (no text extracted).

# Batch 070 (50 papers)
- Dominated by mid-2000s conference cryptography: the 4004xxxx files look like Eurocrypt 2006 proceedings and the 3958xxxx files like PKC 2006, mostly Springer LNCS format.
- Strong recurring themes: secure protocol design without random oracles (signatures, IBE, group signatures, aggregate signatures), key-exchange security (KEA, SAS, password-based group KE, twist-augmented), and secure two-party computation / oblivious transfer foundations.
- Notable heavy hitters: Cheon's Strong Diffie-Hellman analysis, Nguyen-Regev's parallelepiped attack on GGH/NTRUSign, Groth-Ostrovsky-Sahai perfect NIZK, Gentry's standard-model IBE, Joux-Lercier function field sieve, Bellare-Rogaway triple encryption.
- Several lattice / number-theoretic cryptanalysis papers (NTRU symplectic lattices, FFS medium prime case, polynomial equivalence, braid groups).
- Anomalies: 40040511.pdf is font-encoded garbage (unreadable glyph codes); 40040048.pdf is explicitly not a refereed research paper (industry talk note); 40040362.pdf is a position essay rather than a technical result.

# Batch 071 (50 papers)
- Dominated by mid-2000s symmetric cryptanalysis: eSTREAM stream-cipher breaks (Achterbahn, Grain, DECIM, SNOW 2.0, Py, WG/LEX, MOSQUITO, HBB) and Wang-style hash collision work (MD4/MD5/SHA-1/SHA-256/HAVAL/Tiger), apparently FSE 2006-era papers.
- A second block of CRYPTO 2006-era theory papers: NIZK/zaps (Groth-Ostrovsky-Sahai), signatures of knowledge, blind signatures, randomized hashing (Halevi-Krawczyk), non-malleable encryption, anonymous HIBE (Boyen-Waters), fuzzy extractors.
- Number-theoretic highlights: Joux-Lercier-Smart-Vercauteren on NFS for medium-prime finite fields, and "Inverting HFE is Quasipolynomial" (Granboulan-Joux-Stern) — the only DLP-relevant items in a batch otherwise light on elliptic-curve/ECDLP content.
- Regev's "Lattice-based Cryptography" is a survey, not a research paper.
- Anomalies: three files are extraction garbage (40470185.pdf token soup; 40470296.pdf mojibake, likely misencoded CJK text; 40470313.pdf hex-font garbage), and 407.pdf has an anomalous short filename.
- File ordering suggests conference-proceedings sequences (4047xxxx ≈ FSE 2006, 4117xxxx ≈ CRYPTO 2006).

# Batch 072 (50 papers)
- Dominated by mid-2000s CRYPTO/Eurocrypt/TCC-era theory cryptography: secure MPC, Byzantine agreement, secret sharing, UC security, and voting protocols form a large first cluster.
- A second strong cluster is symmetric cryptanalysis and hash-function research in the wake of the Wang et al. MD5/SHA-0/SHA-1 breaks: SHA-1 characteristics, SHA-0 collisions, HMAC/NMAC proofs and attacks, hash combiners, domain-extension transforms.
- RSA/factoring foundations (RSA vs factoring equivalence, Coppersmith attacks, OAEP, plaintext awareness, Paillier impossibility) and identity-/pairing-based constructions (HIBE, broadcast encryption, NIZK group signatures) also feature.
- Only two elliptic/hyperelliptic-curve papers: 2-adic CM method for genus 2 curves, and double-base scalar multiplication on Koblitz/supersingular curves.
- Three anomalous extracts with unreadable mojibake/broken encoding (41170422.pdf, 420.pdf, 42840317.pdf); the remaining 47 are genuine research papers, no obvious duplicates.

# Batch 073 (50 papers)
- Batch consists almost entirely of TCC 2007 (filenames 43920xxx) and PKC 2007 (44500xxx) proceedings papers — 2007-era provable-security cryptography.
- Dominant themes: signature variants (blind, ring, group, designated confirmer, threshold, fair exchange), program obfuscation (3 papers), secret sharing, and secure computation protocols.
- Notable papers: Hohenberger–Rothblum–shelat–Vaikuntanathan on obfuscating re-encryption; Shacham–Waters ring signatures without random oracles; Boyen–Waters constant-size group signatures; Boneh–Waters queries on encrypted data.
- Strong cryptanalysis cluster: attacks on NTRU, the PJH lattice system, braid/Thompson-group key exchange, MFE and HFE multivariate schemes.
- Five files are extraction failures (mojibake/CID-encoded garbage): 43920118, 43920174, 43920311, 43920478, and 440 (the last also has an anomalous short filename).
- No elliptic-curve/ECDLP content; pairing-based constructions appear (group/ring signatures, ABE, PKIE).

# Batch 074 (50 papers)
- Batch is dominated by ~2007-era conference papers (PKC, EUROCRYPT, FSE eSTREAM years), with three main clusters: secure two-/multi-party computation and zero-knowledge, symmetric cryptanalysis of hash functions and stream ciphers (MD5, FORK-256, Panama, eSTREAM candidates), and pairing/signature-based public-key cryptography.
- Notable papers: Stevens–Lenstra–de Weger chosen-prefix MD5 collisions with rogue X.509 certificates; Lindell–Pinkas cut-and-choose malicious 2PC; Ong–Vadhan "Zero Knowledge and Soundness are Symmetric"; Enge–Gaudry L(1/3+ε) DLP algorithm for low-degree curves; Granger et al. generalization of the Ate pairing to hyperelliptic curves.
- Only a handful of ECDLP/ECC-specific items (batch ECDSA verification on Koblitz curves, Ate pairing, Jacobian DLP); most of the batch is protocols and symmetric cryptanalysis rather than curve cryptanalysis.
- Anomalies: 45150034.pdf and 459.pdf are undecodable garbage extracts (broken font/glyph encoding); 45930071.pdf is hex-encoded but decodes to a Naya-Plasencia paper on Achterbahn.

# Batch 075 (50 papers)
- Dominant themes: symmetric-key cryptanalysis (slide attacks, weak keys, related-key rectangle attacks on AES/IDEA/Blowfish/GOST) and hash-function cryptanalysis of the MD4/MD5/SHA-1 family following Wang et al.'s 2004–05 breakthroughs.
- Strong showing of eSTREAM-era stream cipher work (QUAD, Pomaranch, Trivium, IV-setup security) and provable-security/MAC theory (PMAC bounds, randomized preprocessing, hash combiners).
- Second half shifts to public-key and protocol theory: lattice attacks on NTRU and small-exponent RSA (Coppersmith-type), MPC/UC protocols, oblivious transfer, PIR, bounded-quantum-storage QKD, and the NIST SP 800-90 Dual-EC-style RNG analysis by Brown & Gjøsteen.
- Era appears to be ~2006–2007 (FSE/CRYPTO/EUROCRYPT vintage), judging by cited works; mostly IACR-conference-style papers, not elliptic-curve/ECDLP focused.
- Notable papers: Practical Cryptanalysis of SFLASH (Dubois–Fouque–Shamir–Stern), Full Key-Recovery on HMAC/NMAC-MD4, and Information Security Economics (Anderson & Moore) — the latter a non-technical outlier.
- Anomaly: 46220130.pdf extracted as garbled mojibake (likely CJK-encoded PDF); content unidentifiable.

# Batch 076 (50 papers)
- Dominated by CHES/ASIACRYPT/EUROCRYPT-era (ca. 2007) papers: heavy concentration on side-channel attacks (DPA, EM, fault) and DPA-resistant logic styles (MDPL, masking, dual-rail), plus FPGA/hardware implementations of AES, ECC, pairings, modular exponentiation, and NFS sieving.
- Strong hash-function theme: Merkle-Damgård variants and preservation results (Lucks wide-pipe, ROX, Hirose, Yasuda), hardware-oriented MAME, and MAC constructions (Alpha-MAC attack, Pelican/MT-MAC analysis).
- Notable results: first SNFS kilobit factorization (2^1039-1, Aoki et al.), Bernstein–Lange Edwards-curve formulas, PRESENT ultra-lightweight cipher, Groth's NIZK shuffle and group signatures without random oracles, FPGA Pollard-rho attack on binary ECDLP.
- Four files are corrupted/unextractable (mojibake or hex-encoded font streams): 46220605.pdf, 47270014.pdf, 47270121.pdf, 47270227.pdf.

# Batch 077 (50 papers)
- Dominated by theory-of-cryptography papers (2007–2008 era, TCC/ASIACRYPT/PKC-style LNCS proceedings): secure MPC, zero-knowledge, and definitional work on encryption security notions.
- Strong cluster of encryption-signature theory: non-malleability, plaintext awareness, CCA2 variants, designated-verifier/proxy/certificateless schemes, plus lattice- and multivariate-based constructions.
- Cryptanalysis cluster: attacks on Tiger, GRINDAHL, Edon80, ℓ-IC (SFLASH-style), known-key AES/Feistel distinguishers, and DLP with low-Hamming-weight exponents.
- Elliptic-curve relevance is modest but present: Galbraith–Verheul on the vector decomposition problem on pairing-friendly curves, Longa–Miri composite EC operations, Boyen's compact EC encryption, Montgomery-multiplication hardware.
- Anomalies: one non-research invited talk (Cryptographic Test Correction, 49390088.pdf) that is light/anecdotal in tone; no duplicates or garbage files detected.

# Batch 078 (50 papers)
- Dominated by ~2008-era theory-of-cryptography papers (TCC/Eurocrypt style): secure computation (MPC, covert adversaries), zero-knowledge, commitments, and game theory–cryptography connections.
- A second cluster covers symmetric/primitive cryptanalysis and design: KeeLoq attack, HMAC/NMAC-MD4/MD5 key recovery, LPS expander hash collisions, sponge indifferentiability, permutation-based hashing bounds.
- ECDLP-relevant highlight: 49650162 (Smith) uses explicit isogenies to move genus-3 hyperelliptic Jacobian DLP instances to easier non-hyperelliptic Jacobians (~18.6% of curves).
- Other notable papers: Groth–Sahai efficient NIZKs for bilinear groups (49650412), Cash–Kiltz–Shoup twin Diffie-Hellman (49650126), Katz–Sahai–Waters predicate encryption (49650145).
- Anomalies: two files (49650108, 49650268) are hex/garbled extraction failures, not readable research text.
- Game-theoretic protocols (mediators, rational secret sharing, correlated equilibria) form a conspicuous sub-batch of ~5 papers.

# Batch 079 (50 papers)
- Strongly symmetric-crypto / FSE-2008-era batch: hash function cryptanalysis dominates (SHA-0, step-reduced SHA-256, MD4 preimage, HAVAL, GOST, LASH, Snefru, LAKE, SWIFFT), plus stream-cipher attacks (RC4, KeeLoq, Salsa20/ChaCha/Rumba, Trivium, self-shrinking generator, FCSR entropy).
- Second large cluster: side-channel/fault attacks and countermeasures and hardware implementation (second-order SCA protection, AES collision/power attacks, RSA-CRT fault countermeasures, ECC on FPGA/GPU, TRNGs, PUF fuzzy extractors) — largely CHES 2008 vintage, many Ruhr-University Bochum authors.
- Small theory cluster at the front: tamper-proof-hardware UC commitments (Moran–Segev; Chandran–Goyal–Sahai), point-function obfuscation (Canetti–Dakdouk), isolated proofs of knowledge (Damgård–Nielsen–Wichs).
- Only one pairing/identity-based paper (512.pdf, Barreto et al. IB signcryption); essentially no ECDLP content in this batch.
- Anomalies: 49650468.pdf extracted as hex-escaped text (title decodable); 50860338.pdf and 51540196.pdf are PDF glyph-encoded (unreadable); 50860388.pdf has no extractable text.

# Batch 080 (50 papers)
- Two clear sub-batches: a ~2008 CHES-style cluster (filenames 515402xx–515404xx) on side-channel/fault attacks and compact crypto hardware, and a Crypto-2008 cluster (515700xx) on theory — MPC, hash-function provable security, and public-key primitives.
- Heavy representation from Bochum, K.U. Leuven/COSIC, and IAIK Graz groups; recurring authors include Preneel, Paar, Rechberger, Verbauwhede, Ostrovsky, Vaikuntanathan.
- Notable papers: Bernstein–Lange–Farashahi "Binary Edwards Curves" (complete addition formulas in characteristic 2); the KeeLoq DPA break (Eisenbarth et al.); Biham–Carmeli–Shamir "Bug Attacks"; Coron–Patarin–Seurin ROM/ideal-cipher equivalence; Peikert–Vaikuntanathan lattice NISZK.
- ECC-specific content is sparse in this batch: only Binary Edwards Curves, the EC Diffie–Hellman hardcore-bits paper, and the GF(2^m) bit-serial multiplier; most content is symmetric crypto, side channels, and generic MPC/theory.
- Anomalies: two 1-page invited-talk abstracts (51540441.pdf Intel platform security; 53500055.pdf Yao complexity-crypto talk), one file with garbled glyph extraction (51570297.pdf), and one unusually short filename (530.pdf).

# Batch 081 (50 papers)
- Dominated by ~2008-era Springer LNCS papers (ASIACRYPT/PKC/EUROCRYPT style, 14–20 pages) spanning public-key encryption, IBE, signatures, cryptanalysis, and secure computation.
- Strong cryptanalysis cluster: preimage attacks on HAVAL, slide attacks on Grindahl/RadioGatún, impossible-differential attack on MISTY1, attacks on LEX, Sosemanuk/SNOW 2.0, TCHo, and the HB# RFID protocol.
- DLP/factoring cluster of direct ECDLP interest: two Pollard-rho speedups (prime fields and F_{p^m} via normal bases, with pairing-security implications), generic-group lower bounds (Rupp et al.), plus lattice factoring/RSA key-exposure work (May, Herrmann, Aono).
- Notable papers: Shacham–Waters "Compact Proofs of Retrievability", Hisil et al. "Twisted Edwards Curves Revisited" (fast ECC arithmetic), Moran–Naor–Segev optimally fair coin toss (resolving Cleve's Ω(1/r) bound tightness).
- Recurring themes: CCA-secure PKE with minimal overhead (Hanaoka–Kurosawa; Abe–Kiltz–Okamoto twice), IBE variants (Boneh–Hamburg, Chow escrow removal, Libert–Vergnaud accountable authority), anonymous credentials/revocation (Camenisch et al.).
- Anomalies: 53500394.pdf and 54430429.pdf are garbled/mis-encoded extractions and could not be summarized; no obvious duplicates detected.

# Batch 082 (50 papers)
- Batch is two LNCS proceedings runs: TCC 2009 (LNCS 5444, 34 papers, 54440019–54440593) and EUROCRYPT 2009 (LNCS 5479, 15 papers, 54790001–54790261), plus one older standalone key-agreement paper (546.pdf).
- TCC 2009 block is dominated by secure-computation theory: complete fairness, rational secret sharing, MPC without honest majority, UC security, adaptive security, oblivious transfer, zero-knowledge, garbled circuits.
- EUROCRYPT 2009 block mixes symmetric cryptanalysis (full-MD5 preimage, HMAC/NMAC-MD5, MDC-2) with public-key results (selective opening, generic RSA vs factoring, broadcast encryption, order-preserving encryption, NICE break).
- Notable papers: Sasaki–Aoki first preimage attack on full MD5; Aggarwal–Maurer "Breaking RSA Generically is Equivalent to Factoring"; Gentry–Halevi HIBE with polynomially many levels; Nielsen–Orlandi LEGO garbled circuits.
- Anomalies: 54440162.pdf extraction was font-garbled (decoded as "Authenticated Adversarial Routing", Amir–Bunn–Ostrovsky); 54440072.pdf is only a 1-page invited-talk abstract (Peikert lattice survey); 546.pdf has a non-standard filename.
- Essentially no elliptic-curve/ECDLP content in this batch despite the corpus theme; it is almost entirely theory-of-cryptography and symmetric/public-key cryptanalysis.

# Batch 083 (50 papers)
- Strongly clustered around 2008–2009 IACR conference work (Eurocrypt/Crypto/FSE 2009 era, Springer LNCS-style front pages), dominated by symmetric cryptanalysis and provable-security theory.
- Heavy SHA-3-competition-era hash cryptanalysis: attacks or proofs for MD6, RadioGatún, LAKE, EnRUPT, Whirlpool, Grøstl, Tiger, SHA-0/1/2, plus the famous MD5 rogue-CA chosen-prefix collision paper.
- A notable leakage-resilience/side-channel cluster: Goldwasser's invited-talk abstract, the Standaert–Malkin–Yung unified framework, Pietrzak's leakage-resilient mode, Naor–Segev, and Alwen–Dodis–Wichs.
- Elliptic-curve content is implementation-oriented rather than ECDLP-theoretic: ECM on GPUs (Bernstein et al.), GLV endomorphisms (Galbraith–Lin–Scott), double-base chains (Doche–Kohel–Sica), genus-2 curve generation (Satoh).
- Notable anomalies: 54790369.pdf is a 2-page invited-talk abstract, not a full paper; no duplicates or non-paper items found.

# Batch 084 (50 papers)
- Two clean venue clusters: files 56770xxx are CRYPTO 2009 papers (foundations, ZK, symmetric cryptanalysis, lattices, pairings-related PKC); files 57470xxx are CHES 2009 papers (implementations, side-channel attacks/defenses, pairing and ECC hardware).
- Side-channel work dominates the CHES half: EM/template attacks on HMAC, algebraic SCA on AES, attacks on RSA-CRT and RSA prime generation, plus masking/shuffling/RSL countermeasures.
- Notable papers: Biryukov–Khovratovich–Nikolić related-key attack on full AES-256; Waters' Dual System Encryption; Barak–Mahmoody optimal O(n²) attack on random-oracle key exchange; Bernstein's batch binary Edwards speed records; practical forgery of ISO/IEC 9796-2/EMV signatures (Coron et al.).
- Elliptic-curve/pairing content is implementation-focused: hashing into curves (Icart), BN-curve Fp arithmetic and ASIPs, Tate pairing in characteristic 3, ECC coprocessor with SCA countermeasures.
- Anomalies: 57470031 has hex-escaped text extraction (decodable title); 56770459 is a 1-page position essay; 57470063 a 1-page keynote abstract; 57470220 a 5-page invited-talk extended abstract.

# Batch 085 (50 papers)
- Dominated by ~2009 conference proceedings: CHES 2009 (57470xxx: hardware security, PUFs, Trojans, side-channel/fault attacks), Asiacrypt 2009 (5912xxx: hash cryptanalysis, MPC, lattices), TCC 2010 (5978xxx: parallel repetition).
- Heavy SHA-3 competition cryptanalysis cluster: rebound attacks on Lane and Whirlpool, plus Skein, CubeHash, MD6, and MD5 combiners.
- Only two elliptic-curve-relevant items: double-base scalar multiplication (57470302) and cache-timing attacks on OpenSSL ECC (59120664); the batch skews to symmetric and protocol crypto.
- Notable theory results: hedged PKE against bad randomness (Bellare et al.), practical garbled-circuit 2PC (Pinkas et al.), lattice Fiat-Shamir signatures (Lyubashevsky).
- Anomalies: 59120206.pdf is font-encoded garbage (unreadable); 59120614.pdf is hex-escaped text but decodable (Stehlé et al., ideal-lattice PKE).

# Batch 086 (50 papers)
- Dominated by two 2010 conference proceedings: TCC 2010 (the 59780xxx block) and PKC 2010 (the 60560xxx block), plus two older outliers (5_21.pdf, 605.pdf, ~2005 era).
- Heavy theory-of-cryptography focus: secure computation / fairness / covert security, UC assumptions, zero-knowledge (concurrent, non-malleable, Σ-protocols), obfuscation, leakage resilience, and foundational assumptions (DDH, LWE, subset sum).
- The PKC block adds applied topics: pairing/ECC implementation (high-degree twists, Hessian curves, cyclotomic squaring, Groth–Sahai fixes), attribute-based and proxy re-encryption, network coding signatures, and a full break of the PKC'2009 Algebraic Surface Cryptosystem.
- Two files are one-page invited-talk abstracts (Ishai on MPC applications; Camenisch on privacy-enhancing crypto), not full papers.
- Anomaly: 60560053.pdf contains only chart-axis fragments ("Jochemsz–May / Our approach"), not a readable paper — likely a figure page from a small-RSA-exponent attack paper.

# Batch 087 (50 papers)
- Dominated by circa-2010 top-tier conference papers (Crypto/Eurocrypt/PKC/TCC/FSE era) spanning both symmetric and public-key cryptography.
- A large cluster of SHA-3 competition cryptanalysis: JH, BLAKE, Grøstl, ECHO, BMW, Luffa, ESSENCE, Lesamnta, Tiger, plus AES implementation records.
- Strong leakage-resilience / side-channel group: Dodis–Pietrzak, Goldwasser–Rothblum, Juma–Vahlis, Brakerski–Goldwasser.
- Lattice/FHE cluster: Peikert's Gaussian sampler, Gentry's worst-case FHE basis, Boyen's lattice signatures, Agrawal–Boneh–Boyen HIBE.
- Notable record-setting cryptanalytic results: RSA-768 factorization (Kleinjung et al.) and 676-bit DLP in GF(3^6n) (Hayashi et al.), plus the DECT cipher break.
- ECDLP-relevant: Galbraith–Ruprai kangaroo acceleration in short intervals; hashing into ordinary elliptic curves (Brier et al.). No anomalies; all 50 are genuine research papers.

# Batch 088 (50 papers)
- Two clean conference blocks: files 6223xxxxx are CRYPTO 2010 (LNCS 6223) papers; files 6225xxxxx are CHES 2010 (LNCS 6225) papers — an all-2010 theory-then-hardware batch.
- CRYPTO half is heavy on secure computation: verifiable/delegated computation (Gennaro-Gentry-Parno; Chung-Kalai-Vadhan), ORAM, NMZK, coin tossing, UC zero-one law, plus symmetric results (KASUMI sandwich attack, generalized Feistel, HKDF, RKA-secure PRFs).
- CHES half mixes side-channel/fault attacks (random delays, I-cache, collision attacks, Flash bumping, FSA, RSA exponent-randomization fault attack), lightweight crypto (Quark, PRINTcipher, ARMADILLO, GOST in 651 GE), PUFs/TRNGs, and several SHA-3 Round-2 hardware benchmarking papers.
- ECC-relevant entries: co-Z addition formulæ/ladders (Goundar-Joye-Miyaji), Longa-Gebotys x86-64 speed records, and an RNS FPGA scalar-multiplication coprocessor.
- Notable single papers: Dunkelman-Keller-Shamir practical related-key break of full KASUMI; Krawczyk's HKDF; Rivain-Prouff provable higher-order AES masking.
- Anomalies: 62230405.pdf and 62250225.pdf are unreadable font-encoding garbage ("/CD/D2..." mojibake), not summarizable.

# Batch 089 (50 papers)
- Dominated by Asiacrypt/Eurocrypt/PKC 2010-era papers (IACR ePrint numbering), spanning symmetric cryptanalysis, provable-security protocol design, and lattice/pairing-based constructions.
- Heavy cluster of SHA-3 candidate cryptanalysis (Skein, Hamsi, ECHO, Grøstl), plus classical attacks on Tiger/MD4/SHA-2, AES-192/256, SOSEMANUK, and Grain/KATAN.
- Strong presence of zero-knowledge and proof-system papers (Groth ×2, polynomial commitments, SGGM, random-oracle programmability) and leakage-resilience work.
- ECDLP-relevant items: Granger's Static-DHP index-calculus on ECs over extension fields, Bernstein–Lange–Schwabe Pollard rho negation-map speedup, and Avanzi–Heuberger char-3 scalar multiplication.
- Anomalies: 6477379.pdf and 6477561.pdf have garbled/obfuscated text layers (hex-encoded titles and undecodable content respectively); 65710296.pdf is a 1-page talk abstract, not a full paper.

# Batch 090 (50 papers)
- Dominated by theoretical crypto / provable-security papers, apparently from 2011-era ePrint proceedings: one block on signatures, multivariate cryptanalysis and impossibility results, a large TCC-style block on hardness amplification, leakage resilience, black-box separations, and secure computation, and a Eurocrypt-style block on lattices, pairings, and side channels.
- Major themes: leakage-resilient encryption/signatures (5 papers), black-box impossibility/separation results (6+ papers), secure two-party computation and coin tossing (6 papers), and differential/zero-knowledge privacy definitions (3 papers).
- Notable papers: Boneh-Sahai-Waters "Functional Encryption: Definitions and Challenges"; Stehlé-Steinfeld making NTRU provably secure under ideal-lattice assumptions; Aranha et al.'s sub-2M-cycle pairing implementation on BN curves.
- Little ECC/ECDLP content; the only elliptic-curve work is pairing implementation (66320047). Post-quantum cryptanalysis cluster (HFE, IP1S, skew polynomials, UOV) appears early in the batch.
- Anomalies: two 1-page invited-talk abstracts (65970536, 66320001), one 5-page survey talk (66320002), and an unusually short filename (659.pdf).

# Batch 091 (50 papers)
- Dominant theme: theoretical cryptography circa 2010–2011 (mostly EUROCRYPT/TCC-era work), with heavy coverage of leakage-resilient crypto, homomorphic encryption/lattices, and secure multi-party computation.
- Strong lattice/FHE cluster: Gentry–Halevi FHE implementation, FHE over the integers, bonsai trees, lattice (H)IBE, BGN-type LWE cryptosystem, extreme-pruning lattice enumeration.
- Symmetric/crypto-analysis cluster: practical related-key attacks on AES-256, automatic related-key search, RC4/WPA statistical attacks, algebraic attack on compact-key McEliece variants, Stam's conjecture proof.
- Notable impact papers: Boneh–Freeman homomorphic signatures for polynomials, Lewko et al. fully secure functional encryption, Freeman's composite-to-prime-order pairing conversion, Ristenpart et al. indifferentiability limitations.
- Anomaly: 66320133.pdf extract is unreadable hex-encoded garbage (no recoverable title). One item (66320296) is a 2-page position essay, not a research paper. No obvious duplicates.
- Very little elliptic-curve/ECDLP content directly; pairings appear mainly as bilinear-group assumptions for ABE/VRF/signatures.

# Batch 092 (50 papers)
- Dominated by ~2011-era conference papers (EUROCRYPT/FSE/LNCS-style extracts): heavy symmetric cryptanalysis (SHA-3 candidates ECHO, BLAKE, Keccak, Luffa, SHAvite-3, Hamsi; block ciphers PRINTcipher, GOST, PRESENT; stream ciphers Grain-128, RC4, Hummingbird-1, knapsack generator).
- A strong public-key cluster opens the batch: KDM-secure encryption (Malkin/Teranishi/Yung; Applebaum), Lewko–Waters HIBE/ABE works, threshold/revocation schemes (Wee), deniable encryption (Dürmuth–Freeman).
- Later papers shift to secure computation and delegation: verifiable computation, memory delegation, web-model MPC, BGW multiplication, IPS compiler, 1/p-secure MPC.
- Notable leakage/side-channel cluster at the end: leakage-resilient ZK, key evolution under space-bounded leakage, MIA evaluation, generic side-channel distinguishers.
- Notable individual papers: Isobe's first single-key attack on full GOST; Dinur–Shamir dynamic cube attacks on Grain-128; EasyCrypt computer-aided proofs.
- Anomalies: 667slides.pdf is a slide deck (Krawczyk AWS Crypto 2023 talk), not a research paper; 679.pdf is an unusually short filename but a real paper. No obvious duplicates (two PRINTcipher papers are distinct works).

# Batch 093 (50 papers)
- Two clear venue blocks: a Crypto 2011 (6841xxxx) theory cluster — post-quantum crypto, FHE, leakage resilience, deniable/OPE encryption — and a CHES 2011 (6917xxxx) hardware cluster — side-channel attacks/countermeasures, PUFs, lightweight ciphers, pairing/ECC implementations.
- Notable theory papers: Brakerski-Vaikuntanathan Ring-LWE FHE, Coron et al. integer FHE with shorter keys, Hanrot-Pujol-Stehlé BKZ dynamical-systems analysis, Bernstein-Lange-Peters ball-collision decoding, Abe et al. optimal structure-preserving signatures.
- Notable applied papers: Bernstein et al. Ed25519 high-speed signatures; Fan-Gierlichs-Vercauteren combined fault+side-channel ECC attack; Oswald-Paar DESFire key recovery; lightweight designs spongent, LED, Piccolo.
- Anomalies: 68410481 is a Tor invited-talk abstract (2p), and 69170274 is a 1-page EMC standardization presentation abstract — neither is a full research paper.
- ECC-relevant content is mostly implementation- and attack-oriented (Ed25519, binary-field scalar multiplication, fault/SCA on ECC, pairing hardware), not ECDLP-hardness results.

# Batch 094 (50 papers)
- Dominated by ASIACRYPT 2011–era papers (the 7073xxxx/7194xxxx ID runs): a strong theory-heavy mix of provable-security constructions (functional encryption, lossy/deniable encryption, UC commitments, zero-knowledge) and cryptanalysis.
- Notable landmark results: Bogdanov–Khovratovich–Rechberger biclique cryptanalysis of full AES; Chen–Nguyen "BKZ 2.0" lattice security estimates; Agrawal–Freeman–Vaikuntanathan LWE functional encryption; Gaudry–Kohel–Smith genus-2 point counting with real multiplication.
- A substantial SHA-3-competition and hash cryptanalysis cluster (SHA-3 FPGA benchmarking, JH rebound, SHA-256 higher-order differential collisions, SHA-2 characteristic search, ARMADILLO2).
- Side-channel/leakage-resilience and physical-security themes recur (related-key/tampering, leakage-resilience limits, inner-product extractor, tamper-resilient hardware tokens, TLS tag-size attack).
- Only one ECC-adjacent paper: genus-2 curve point counting; the batch is otherwise symmetric-crypto, lattices, and protocol theory rather than ECDLP.
- Anomaly: 70730563.pdf is a 1-page fragment containing only figure labels (Pri-Expo/Bit-Expo variants), not an extractable paper.

# Batch 095 (50 papers)
- Dominated by two 2012 IACR proceedings: file IDs 7194xxxx are TCC 2012 papers (foundations: zero knowledge, leakage resilience, PRFs, black-box separations); 7237xxxx are EUROCRYPT 2012 papers (symmetric cryptanalysis, pairings, block-cipher provable security).
- Strong leakage-resilience cluster: leakage-tolerant UC protocols, parallel repetition for leakage, leakage-resilient circuits, IBE with continual auxiliary leakage.
- Directly ECDLP-relevant: Joux–Vitse cover-and-decomposition index calculus over Fp6 (real 151-bit computation) and Faugère–Perret–Petit–Renault binary-field ECDLP index calculus via Gröbner bases.
- Notable symmetric-crypto results: biclique attack on full IDEA, Slidex attack/tight Even–Mansour bounds, key-alternating ciphers, LPMAC generic attacks.
- Anomalies: 72370136.pdf is a garbled/character-encoded extract (undecipherable); 72370009.pdf is a 1-page invited-talk abstract (Menezes, "Another Look at Provable Security"); 72370001.pdf is an invited-talk tutorial abstract (Joux).

# Batch 096 (50 papers)
- Batch is dominated by ~2011–2012 public-key cryptography papers (PKC/Eurocrypt-era style): FHE over the integers (DGHV compression, bootstrapping, approximate-GCD cryptanalysis) and lattice-based crypto (LWE/Ring-LWE, trapdoors, PRFs, signatures) form the largest cluster.
- A second major theme is signature security reductions: tight proofs, optimal loss factors (FDH, Schnorr, Waters signatures), and RSA-based space-efficient schemes.
- Key exchange is well represented: PAKE via OT, single-round UC PAKE, CK+-secure AKE from factoring/codes/lattices, plus private set operations (PSI, set union, policy-enhanced PSI).
- Definitional/foundational results recur: selective-opening security separations, circular/KDM security, related-key-attack resilience, leakage resilience.
- Notably absent: elliptic-curve crypto and ECDLP papers — anomalous for this corpus; only one side-channel paper (Moradi, collision attacks).
- Anomaly: 72930354.pdf extracted as hex-escaped text ("NTRUCCA: How to Strengthen NTRUEncrypt to Chosen-Ciphertext Security..."); content otherwise decodable. No duplicates or non-paper files found.

# Batch 097 (50 papers)
- Dominated by CRYPTO 2012 (LNCS 7417) and PKC 2012 (LNCS 7293) proceedings papers — foundational/symmetric crypto, MPC, functional/attribute-based encryption, leakage and tamper resilience.
- Notable ECDLP item: experimental run of Cheon's algorithm solving DLP-with-auxiliary-input on a 160-bit Barreto–Naehrig curve (1314 core days) — the only elliptic-curve attack paper in this batch.
- Other standouts: Lenstra et al.'s "Public Keys" real-world RSA/ECDSA key sanity check, the SPDZ paper (MPC from somewhat homomorphic encryption), TinyOT-style practical 2PC, and the GCM proof flaw repair by Iwata et al.
- Anomalies: two 1-page invited-talk abstracts (Zittrain, Brickell), one file with no extracted text (74170437), and one garbage extraction of stray digits (74170602).
- Themes cluster tightly: hash/compression-function theory, UC/composable secure computation, differential privacy, and ABE/functional encryption — little applied or side-channel-empirical work beyond theory of leakage resilience.

# Batch 098 (50 papers)
- Dominated by ~2012-era CRYPTO/CHES-style proceedings: roughly two thematic blocks — theoretical/foundational crypto plus a very large side-channel/hardware-security cluster (DPA, masking, PUFs, fault attacks).
- A second block covers symmetric cryptanalysis (GOST, TEA/XTEA, Camellia, Grøstl rebound/preimage attacks) and lightweight-cipher implementation studies.
- Notable papers: Mahmoody–Pass on black-box vs non-black-box commitments; Gentry–Halevi–Smart homomorphic AES evaluation; Brakerski FHE without modulus switching; Skorobogatov & Woods FPGA backdoor discovery.
- Direct ECDLP/elliptic-curve content is thin here: only a pairing-bit-hardness result (74170827), an FPGA GF(2^m) scalar multiplier (74280493), and a CPA-protected DF-ECC processor (74280547).
- Anomalies: one empty extract (74280120), one page of plot-axis garbage (74280231), one IACR copyright form (74280338), and a talk abstract on banking security (74280318).

# Batch 099 (50 papers)
- Dominated by 2012-era symmetric cryptanalysis: hash-function attacks (Keccak/SHA-3 finalists, SHA-2, RIPEMD-128, Whirlpool, ARMADILLO2), biclique/rebound techniques, and ARX differential analysis; mostly FSE 2012 and ASIACRYPT 2012 papers.
- Strong block-cipher/modes thread: ciphertext stealing, McOE online AE, GCM weak keys, iterated Even-Mansour bounds, LED, PRINCE, ZUC, Salsa20, HMAC related-key attacks.
- Second cluster of public-key theory: pairings (structure-preserving and dual form signatures, ηT pairing DLP record over GF(3^97)), lattices (NTRUSign cryptanalysis, Gaussian sampling), LPN-based schemes, leakage/RKA security.
- Most ECDLP-relevant items: Petit–Quisquater on Weil-descent polynomial systems for binary-curve ECDLP (subexponential heuristics), Hayashi et al. breaking ηT-pairing fields via FFS, and Bos–Kleinjung ECM factorization records.
- Anomalies: 76580001 (Boneh pairings) and 76580002 (Zong lattices) are 1-page invited-talk abstracts, not full papers. No duplicates or non-paper files found.

# Batch 100 (50 papers)
- Dominated by ~2012–2013 conference papers (ASIACRYPT 2012, PKC/TCC 2013 vintage) on provable-security public-key cryptography: signatures, encryption notions, and UC-secure protocols.
- Recurring themes: functional/attribute-based encryption (Waters, Hohenberger–Waters, Boyen, Okamoto–Takashima, Barbosa–Farshim), homomorphic encryption limits and packing (Brakerski, Gentry, Katz), and zero-knowledge variants (concurrent, public-coin, malleable NIZKs).
- A smaller but notable cluster of side-channel / leakage papers: shuffling analysis (Veyrat-Charvillon et al.), inner-product masking (Balasch et al.), CRT-RSA combined attack (Barbu et al.), RSA key recovery from noisy bits.
- Only one elliptic-curve-specific paper: Longa–Sica's four-dimensional GLV-GLS scalar multiplication.
- Anomalies: three items are short invited-talk abstracts/essays rather than full papers (77780050 Waters, 77780250 Lindell, 77850120 Gentry); no obvious duplicates.

# Batch 101 (50 papers)
- Dominated by TCC 2013 (77850xxx) and EUROCRYPT 2013 (78810xxx) proceedings papers; ~2012–2013 theoretical cryptography.
- Heavy focus on secure computation / MPC foundations: fairness, reactive functionalities, UC synchrony, OT extension, correlated randomness, constant-overhead MPC, ORAM.
- Strong black-box separation / impossibility thread: Fiat-Shamir, Fischlin's paradigm, random oracles, NIZK, circular security, RDM security, UOWHF lower bounds.
- Notable high-impact papers: Garg–Gentry–Halevi candidate multilinear maps from ideal lattices; Joux's faster medium-prime index calculus (1175/1425-bit DLP records); Bos–Costello–Hisil–Lauter genus-2 speed records; Stevens' improved SHA-1 collisions.
- Side-channel / leakage cluster: masking security proof, key-rank estimation, leakage-resilient crypto from minimal assumptions.
- Anomalies: four very short items (1–2 pages): a talk abstract (77850354), a survey talk abstract (77850597), an errata notice (77850719, responding to 77850557), and a 2-page Keccak/SHA-3 summary (78810311).

# Batch 102 (50 papers)
- This batch is almost entirely Crypto 2013 proceedings papers (LNCS vols. 8042/8043), spanning symmetric cryptanalysis, secure computation, lattices, and quantum security — essentially no elliptic-curve/ECDLP content.
- Dominant themes: secure two-party/multi-party computation with cut-and-choose optimizations (MiniLEGO, Lindell, Huang-Katz-Evans, Mohassel-Riva), and the 2013 multilinear-map wave (CLT integer multilinear maps, ABE for circuits, full-domain hash, identity-based aggregate signatures).
- Notable landmark papers: Gennaro-Gentry-Parno-Raykova "Quadratic Span Programs and Succinct NIZKs" (foundational for SNARKs/zkSNARKs), Ben-Sasson et al. "SNARKs for C" (first practical zk-SNARK implementation), and Ducas et al. "Lattice Signatures and Bimodal Gaussians" (BLISS).
- Symmetric side: improved meet-in-the-middle attacks on AES (Derbez-Fouque-Jean, Canteaut et al. sieve-in-the-middle), differential/linear links (Blondeau-Nyberg), and real-time Bluetooth E0 cryptanalysis.
- Quantum security is a recurring thread: Boneh-Zhandry appear twice (quantum-secure MACs; quantum-secure signatures/CCA), plus Unruh's everlasting MPC and Dupuis-Fawzi-Wehner's noisy-storage results.
- Anomaly: 78810606.pdf extracted as hex character-code garbage (font-encoding failure) — title/content unrecoverable from the extract.

# Batch 103 (50 papers)
- Batch splits cleanly into two venue runs: Crypto 2013 papers (files 80420xxx, theory: MPC, FHE, obfuscation, assumptions) and CHES 2013 papers (files 80860xxx, applied: side-channel attacks, masking, PUFs, hardware Trojans, embedded implementations).
- Notable theory results: Gentry–Sahai–Waters LWE-based FHE (approximate eigenvector method), Bellare–Hoang–Keelveedhi UCE random-oracle instantiation, and the Krawczyk–Paterson–Wee systematic TLS security analysis.
- Notable applied results: Göloğlu et al.'s Function Field Sieve DLP records in F_2^1971 and F_2^3164, Oliveira et al.'s lambda-coordinates speed records for binary ECC, and Bernstein–Chou–Schwabe's McBits constant-time code-based crypto.
- Side-channel/fault-attack cluster is strong: 384-bit ECDSA nonce-leak attack via Bleichenbacher HNP, fault attacks on MICKEY 2.0 and Tate pairing final exponentiation, SRAM PUF cloning via remanence decay, and dopant-level hardware Trojans.
- Anomaly: 80860135.pdf extracted as raw glyph codes ("/C7/D2...") — content not readable as text.
- Source chunk contained one embedded NUL byte (cleaned before processing); era is uniformly 2013, no duplicates detected.

# Batch 104 (50 papers)
- Dominated by 2013-era LNCS-style papers (Asiacrypt/FSE/TCC venues): secure multiparty computation, UC security, commitments, and zero-knowledge are the single largest cluster.
- Strong secondary clusters in hash-function cryptanalysis (HMAC/Whirlpool, RIPEMD-160, HAS-160, diamond structures) and block-cipher cryptanalysis (Feistel, Even-Mansour, LED-128, LBlock/TWINE).
- Side-channel and leakage work is well represented: masking schemes, leakage-detection statistics, tamper resilience, leakage-resilient PKE, and practical SPA on binary Huff curves.
- Notable high-impact items: Boneh–Waters constrained PRFs, Jutla–Roy quasi-adaptive NIZK, Bernstein–Lange "non-uniform cracks in the concrete", and the Taiwan smart-card RSA factoring study.
- ECC/ECDLP-adjacent material is thin: only binary Huff curve implementation/SPA and the 4-dimensional GLV via Weil restriction (genus-2 / elliptic curves over Fp2).
- Anomaly: 82700101.pdf is a 1-page invited-talk abstract (Danezis), not a full research paper.

# Batch 105 (50 papers)
- Dominated by theory-of-cryptography conference papers circa 2013–2014: the filename blocks map to Crypto 2013 (8271xxxx), TCC 2014 (8349xxxx), and PKC 2014 (8383xxxx) proceedings.
- Heavy focus on secure computation and its foundations: MPC round complexity, fairness, UC security, hardware tokens, black-box separations, and zero-knowledge variants.
- A strong obfuscation cluster (point/function/extractability/evasive/VBB obfuscation) reflecting the post-GGH13 multilinear-maps boom, plus non-malleable codes and tamper/leakage resilience.
- Only two elliptic-curve/DLP-relevant papers: Smith's Q-curve fast endomorphisms (GLV/GLS acceleration) and the GF(2^809) FFS discrete-log record; the batch is otherwise symmetric/lattice/foundations heavy.
- Anomalies: three 1-page invited-talk abstracts (Knudsen on block cipher history, Micali on mechanism design, Impagliazzo on general vs. specific assumptions) — no full papers.
- No obvious duplicates; no non-paper junk files detected.

# Batch 106 (50 papers)
- Two clear venue clusters: files 83830xxx are PKC 2014-era public-key papers (leakage resilience, CCA security, lattices/LWE/LPN, ABE, signatures, obfuscation); files 8424xxxx are FSE 2014-era symmetric papers (block-cipher and hash cryptanalysis, RC4/WEP attacks, MACs, masking).
- Heavy symmetric cryptanalysis coverage: Keccak/SHA-3 (3 papers), PRINCE (2 papers), LED, WIDEA, GOST/Camellia, Skein, plus generic results on Matsui's Algorithm 2, near-collisions, and known-key security.
- ECC relevance is thin: one paper (83830154) does concrete Pollard-rho cost estimates for NIST P-256, a BN curve, and genus-2 analogues — the only discrete-log work in the batch.
- Notable lattice/PQ thread: Gauss-sieve SVP record, LWE proxy re-encryption, lattice VLR group signatures, LPN CCA encryption, RKA-KDM schemes from DDH/LWE/QR/DCR.
- Anomalies: none — all 50 extracts are genuine research papers; no duplicates, no non-paper content. Two PRINCE papers (84240065, 84240085) overlap topically but are independent analyses.

# Batch 107 (50 papers)
- Era/venues: almost entirely FSE 2013 (84240xxx series) and EUROCRYPT 2014 (84410xxx series) conference papers, plus a few likely CRYPTO-era 2014 items (85400xxx).
- Two strong thematic clusters: (1) symmetric cryptanalysis and design — stream ciphers (Trivium, Grain v1, Hummingbird-2, GMR-2), lightweight block ciphers (KLEIN, LED, Zorro), AES meet-in-the-middle and biclique attacks, and authenticated-encryption design/theory (ALE, Minematsu's AE mode, Namprempre–Rogaway–Shrimpton composition); (2) theory of cryptography — obfuscation (Barak et al., Hohenberger–Sahai–Waters), garbled RAM/circuits, functional and attribute-based encryption, non-malleable codes, UC commitments.
- Notable for ECDLP relevance: Barbulescu–Gaudry–Joux–Thomé quasi-polynomial DLP in small-characteristic fields; Faugère–Huot–Joux–Renault–Vitse on symmetrized summation polynomials for EC index calculus; Costello–Hisil–Smith fast constant-time ECDH on the x-line.
- Side-channel/leakage cluster: Coron higher-order masking of S-box tables, Duc–Dziembowski–Faust unifying probing and noisy leakage, Durvaux–Standaert–Veyrat-Charvillon on certifying chip leakage.
- Anomaly: 84410115.pdf is a garbage/hex-escaped extraction (likely a CJK-encoded PDF whose text layer failed) — title and content unreadable.
- No duplicates detected among the 50 files.

# Batch 108 (50 papers)
- Dominant cluster: symmetric-key cryptography from FSE 2015 (LNCS 8540) — lightweight block/stream cipher design and cryptanalysis (Sprout, KATAN, PRINCE, Simon/Speck, MISTY1, LED-64), plus MDS matrix and S-box constructions.
- Heavy CAESAR-era authenticated-encryption presence: new schemes (p-OMD, APE, CLOC, COBRA, POE/POET) and attacks on candidates (FIDES, ICEPOLE), plus refined security bounds (GCM, keyed sponges, tweakable blockciphers).
- Second venue cluster: CRYPTO 2014 (LNCS 8616) — lattices/FHE (Gentry-Szydlo, key-homomorphic PRFs, faster bootstrapping), MPC/garbled circuits (FleXOR, dishonest-majority binary MPC), indistinguishability obfuscation (Boneh-Zhandry), and quantum one-time memories.
- Notable applied work: RC4/WPA-TKIP plaintext recovery and RC4 bias analyses, and algorithm-substitution (mass surveillance) security modeling.
- Anomalies: none — all 50 extracts are valid research-paper first pages; no duplicates, slides, or non-paper content found.

# Batch 109 (50 papers)
- Strongly homogeneous batch: essentially all papers are CRYPTO 2014 proceedings (LNCS-style, ~18p) spanning MPC, obfuscation, pairings, lattices, and symmetric crypto; two CHES 2014 papers close the batch.
- Heavy concentration on secure computation (MPC round complexity, identifiable abort, cut-and-choose, garbled circuits, NIMPC) and on obfuscation/multilinear maps (iO feasibility and impossibility, witness encryption, broadcast encryption).
- ECC/ECDLP-relevant highlights: Granger–Kleinjung–Zumbrägel break '128-bit' supersingular binary curves via quasi-polynomial DLP; Ben-Sasson et al. scalable zk-SNARKs via cycles of elliptic curves; Abe–Groth–Ohkubo–Tibouchi structure-preserving signatures from Type II pairings.
- Notable side-channel papers: Genkin–Shamir–Tromer acoustic RSA key extraction, and Benger et al. Flush+Reload lattice attack on OpenSSL ECDSA over secp256k1.
- No anomalies: every file is a genuine research paper extract; no duplicates, slides, or non-paper content detected.

# Batch 110 (50 papers)
- Overwhelmingly CHES 2014 (8731xxxx) and ASIACRYPT 2014 (8873xxxx) papers: hardware crypto, side-channel attacks/countermeasures, and provable security work from the 2014 era.
- Dominant theme is side-channel analysis: static-power leakage, higher-order DPA models, EM sensors, masking conversions, gate-level masking, template attacks, and physical attacks on laptops and PUFs.
- Strong representation of efficient implementations: GPU-accelerated NFS cofactorization, Curve41417 ECDH on ARM, genus-2 Jacobian coordinates, Ring-LWE and BLISS lattice crypto on reconfigurable hardware, pairings/ECC for embedded systems.
- Notable papers: Genkin–Pipman–Tromer "Get Your Hands Off My Laptop" physical key-extraction; Bernstein–Chuengsatiansup–Lange Curve41417; Boneh–Corrigan-Gibbs bivariate polynomials mod composites; Jean–Nikolić–Peyrin TWEAKEY framework.
- Anomaly: 87310144.pdf is unextractable garbage (font-encoded character codes, no readable text) — likely a Chinese-language paper with broken extraction.

# Batch 111 (50 papers)
- This batch is dominated by conference proceedings papers, apparently ASIACRYPT 2014 (88730xxx files) and TCC 2015 (9014xxx files), covering a broad sweep of theoretical and applied cryptography.
- ECC/ECDLP-relevant highlights: Joux–Pierrot on small-characteristic finite-field DLP precomputation, Doche on double-base chains for scalar multiplication, and Aranha et al. on GLV/GLS decomposition side-channel attacks against ECDSA with single-bit nonce bias.
- Strong side-channel cluster: soft analytical attacks, higher-order optimal distinguishers, higher-order threshold implementations, and SCA of GF(2^128) multiplication in AES-GCM.
- Large theory contingent: obfuscation (iO, diO, AIPO, UCEs), black-box separations, zero-knowledge variants, secure computation (MPC, ORAM, fairness, topology-hiding, dual execution), and SNARKs via square span programs.
- Symmetric crypto also well represented: Feistel/Even-Mansour/impossible-differential cryptanalysis, sponge AE modes (NORX et al.), RC4 bias exploitation, Catena password scrambling.
- Anomaly: 88730361.pdf is a 1-page abstract of a legal-policy talk on information-security law in Asia, not a technical research paper.

# Batch 112 (50 papers)
- Dominated by theoretical cryptography from the 2014–2015 era, consistent with ePrint preprints for TCC 2015 / PKC 2015 / EUROCRYPT 2015 (file numbers 9014xxxx–9020xxxx).
- Two large thematic clusters: non-malleable codes and tamper/leakage resilience (90140377–90140534, 90200135), and obfuscation-based results (iO, diO, probabilistic obfuscation, multilinear maps) spanning 90150377–90150669.
- Also strong coverage of secure computation (adaptive/UC MPC, verifiable computation, oblivious polynomial evaluation), functional encryption, tight security reductions, and selective-opening security of PKE.
- Elliptic-curve/pairing content is sparse: only structure-preserving signatures from Type II pairings (90200154) and BGV bootstrapping mentioning elliptic-curve groups (90200107) touch EC-adjacent topics.
- Most relevant to ECDLP: 90200136 (rigorous analysis of Pollard Kangaroo/Rho and Gaudry-Schost random-walk DLP attacks) — the only paper directly about the discrete logarithm problem.
- No anomalies: all 50 extracts are legitimate research-paper first pages; no duplicates, slides, or non-paper content detected.

# Batch 113 (50 papers)
- Dominated by 2015-era public-key cryptography: provable-security constructions for signatures, encryption, key exchange, NIZK, and commitments (mostly PKC/EUROCRYPT/CRYPTO-style papers).
- Heavy post-quantum theme: lattice-based group signatures, trapdoor sampling, LPN encryption, code-based cryptanalysis (BBCRS, binary linear code decoding), and a quantum-money cryptanalysis.
- FHE and garbled-circuit efficiency cluster: FHEW (sub-second bootstrapping), HElib bootstrapping, half-gates garbling, privacy-free garbled circuits, AGCD-based FHE.
- Strong symmetric-cryptanalysis contingent: cube attacks on Keccak, invariant subspace attacks, division property, Even-Mansour related-key analysis, FX-construction tradeoffs, Sbox equivalence.
- DLP-relevant items: improved NFS for GF(p^n) (with a 595-bit GF(p^2) record), Multiple NFS with Conjugation, and a tight generic lower bound for the multiple discrete logarithm problem.
- No anomalies: all 50 files are legitimate research papers; no duplicates, no non-paper content.

# Batch 114 (50 papers)
- Coherent 2015-era batch: mostly Eurocrypt/CRYPTO 2015 papers (file IDs 9056xxxx and 9216xxxx) spanning theory, symmetric cryptanalysis, lattice crypto, and side channels.
- Heavy theory/core-crypto presence: UC frameworks, obfuscation, multilinear maps (both a new construction and its cryptanalysis), ABE/predicate encryption, function secret sharing, FSS/CDS communication complexity.
- Strong side-channel/masking cluster (4 papers): concrete masking security proofs, leakage-resilient circuits, verified higher-order masking, inner-product masking.
- Lattice crypto is prominent: LWE/LWR algorithms, LSH sieving for SVP, weak Ring-LWE instances, lattice AKE, predicate encryption from LWE.
- Notable named results: SPHINCS stateless hash-based signatures, the Bitcoin Backbone protocol, Cheon et al.'s total break of the CLT multilinear map, free-start collisions on 76-step SHA-1, first attack on full MISTY1, Decaf point compression.
- No anomalies: all 50 extracts are genuine research papers; no duplicates detected; only 92160145 lacks visible author names.

# Batch 115 (50 papers)
- Dominated by CRYPTO 2015 proceedings papers (the 921602xx file range), spanning LWE/lattice algorithms, functional encryption and iO, MPC round complexity, and zero-knowledge.
- Strong symmetric-crypto cluster: Even-Mansour analyses, S-box reverse engineering (Skipjack), PRESENT/SIMON/Sprout cryptanalysis, keyed-sponge PRF bounds, online AE definitions.
- ECDLP-relevant paper: 92160209 (last fall degree, HFE, and Weil descent attacks on ECDLP in characteristic 2, casting doubt on first-fall-degree heuristics).
- Side-channel/masking cluster near the end: probing-security decomposition (92160288), masking consolidation (92160324), plus two CHES 2015 papers (92930001, 92930021) on profiling attacks and dimensionality reduction.
- Notable breaks: total break of CLT13 multilinear maps via zeroizing attacks (92160310), key recovery on ASASA (92160238), full Sprout attack (92160328).
- No anomalies: all 50 files are genuine research papers; no duplicates or non-paper content found.

# Batch 116 (50 papers)
- Two coherent venue blocks: 929300xx ≈ CHES 2015 (hardware/side-channel focus) and 945201xx ≈ ASIACRYPT 2015 (theory/cryptanalysis focus).
- Dominant themes: side-channel attacks and countermeasures (DPA, EM emanations, masking, higher-order attacks, leakage assessment), plus FPGA/hardware acceleration of homomorphic encryption (YASHE/LTV/ring-LWE).
- Notable papers: Genkin et al.'s cheap EM key-extraction from PCs ("pita bread" attack), Becker's real-world cloning of commercial XOR Arbiter PUFs, and the Tower Number Field Sieve (Barbulescu–Gaudry–Kleinjung), a landmark DL result affecting pairing security.
- ECDLP-relevant theory appears in the second half: multiple-DLP with auxiliary inputs, NFS-DL individual logarithms, TNFS, and pairing-based structure-preserving signatures.
- No anomalies: all 50 extracts are genuine research-paper first pages; no duplicates detected.

# Batch 117 (50 papers)
- Batch is dominated by 2015-era conference papers (mostly ASIACRYPT/TCC-style, ~25-page LNCS format) covering symmetric cryptography, provable security, and secure computation — almost no elliptic-curve/ECDLP content despite the corpus theme.
- Strong clusters: symmetric designs/cryptanalysis (Sprout, Midori, ASASA, AEZ/Marble, HMAC, Even–Mansour, hash known-key attacks), secure computation/MPC (UC black-box, OT-based SPDZ, ORAM, garbling, cut-and-choose), and advanced public-key primitives (IBE, ABE, functional encryption, obfuscation).
- Notable non-technical items: three anomalous short extracts (94520356, 94520357, 94520358) which are 1–2 page keynote/essay abstracts, not full papers — including Rogaway's "The Moral Character of Cryptographic Work".
- Side-channel/leakage theme present (key enumeration, power-analysis metric ILA, AES under leakage, memory-hard tradeoffs).
- Obfuscation lower bounds cluster at the end (95620001, 95620016, 95620046), with 95620016 explicitly building on 95620001 (Pass–Shelat) but not a duplicate.
- Anomalies found: 3 (short keynote/essay abstracts); no duplicates detected.

# Batch 118 (50 papers)
- Dominated by TCC 2016-A (9562xxxx, 42 papers) and PKC 2016 (9614xxxx, 8 papers) era work, ~2015–2016, mostly theoretical/foundational cryptography.
- Recurring themes: indistinguishability obfuscation (constructions, applications, and impossibility results), functional/predicate encryption, ORAM and oblivious parallel RAM, NIZK/PCP/sigma-protocol techniques, and non-malleable codes.
- Notable ECDLP/EC-relevant items: algebraic index-calculus attempts on prime-field ECDLP (96140156) and degenerate curve attacks extending invalid-curve attacks to Edwards curves (96140158); several pairing-based IBE/ABE papers.
- Other standouts: Onion ORAM (constant bandwidth blowup), VRFs from standard assumptions, ARMed SPHINCS (embedded hash-based signatures), LPN-based authentication.
- No duplicates, no non-paper anomalies; all 50 extracts are recognizable research papers.

# Batch 119 (50 papers)
- Mid-2010s IACR-style crypto papers (9614xxxx/9665xxxx ePrint numbering), heavy on public-key primitives: signature variants (sanitizable, aggregate, attribute-based, functional, hash-based XMSS-T), KDM/circular-security and leakage-resilient PKE, MPC, and functional encryption.
- Strong cryptanalysis thread: breaks of GGH and CLT15 multilinear maps, generalized Coppersmith attacks on RSA variants, NFS discrete-log polynomial selection in non-prime fields, hash-combiner attacks, weak Ring-LWE instances, PMAC analysis, and practical attacks (OpenSSL RNG, s2n "Lucky Microseconds" timing, Streebog/Kuznyechik S-box reverse engineering).
- Notable papers: Bootle et al.'s logarithmic-communication discrete-log ZK argument (inner-product technique, precursor to Bulletproofs); Hu–Jia GGH map break; Cheon et al. CLT15 break; Albrecht–Paterson s2n timing attack.
- Only mild elliptic-curve/pairing presence (SXDH-based schemes, bilinear-map ABS); no ECDLP-focused papers in this batch.
- Anomaly: 96140171.pdf is a 1-page file with no extractable text. No obvious duplicates.

# Batch 120 (50 papers)
- Batch splits cleanly into two halves: ~36 Eurocrypt/Crypto-era 2015–2016 research papers (numeric IDs), followed by 10 LNCS conference proceedings front-covers (Springer ISBN files, ASIACRYPT/PKC/CRYPTO 2018–2022).
- Dominant themes: secure multi-party computation and its round/interaction complexity, obfuscation (diO, iO, post-zeroizing, graded encodings), and lattice cryptography (basis reduction, BKZ, LWE IBE, ring signatures, ideal lattices).
- Notable papers: the Stevens–Karpman–Peyrin freestart collision for full SHA-1, Groth's 3-group-element pairing SNARK, Cramer–Ducas–Peikert–Regev on short generators of principal ideals, and Renes–Costello–Batina complete addition formulas for prime-order Weierstrass curves.
- Several 1–2 page items are position/talk abstracts rather than full papers (Preneel, Collberg, Bhargavan, Prouff).
- Anomaly: 96650356.pdf is unreadable mojibake (encoding garbage); no title or content recoverable.

# Batch 121 (50 papers)
- This batch is anomalous: 48 of 50 files are Springer LNCS proceedings volumes whose extract shows only the front-matter/editorial-board page, not an individual research paper.
- Volumes span CRYPTO, EUROCRYPT, ASIACRYPT, and PKC from roughly 2007 to 2026 (LNCS 4450 through 16554), a nearly complete IACR flagship-conference run.
- Several older volumes (2007–2012 era) show only the LNCS series number and generic editorial board; the specific conference is not visible in the extract and is marked with (?).
- Only two files are actual research papers: Naito–Yasuda on keyed-sponge PRF bounds, and Abed et al. on the RIV robust authenticated-encryption construction.
- Nothing here covers ECC/ECDLP directly; the batch is essentially bibliographic metadata for whole conference proceedings.
- One likely future-dated anomaly: 978-3-032-26740-5.pdf is labeled PKC 2026 (May 25–28, 2026).

# Batch 122 (50 papers)
- Batch is two coherent conference blocks: files 9783xxxx are FSE 2016 papers (symmetric cryptanalysis, block/stream ciphers, MAC modes), and 9813xxxx are CHES 2016 papers (side-channel attacks, masking, hardware implementations).
- Dominant themes: automatic cryptanalysis tooling (SAT/MILP/key-bridging/division property) applied to NSA lightweight ciphers Simon and Speck, and masking countermeasures with d+1 shares and leakage detection.
- Notable papers: CacheBleed (Yarom–Genkin–Heninger) breaking OpenSSL "constant-time" RSA; DCA attack (Bos et al.) defeating commercial white-box AES; Flush+Gauss+Reload, the first cache attack on lattice-based BLISS signatures.
- ECC content is thin: only FourQ-on-FPGA and a Koblitz-curve software implementation touch elliptic curves; both are implementation speed records rather than ECDLP theory.
- Anomaly: one applied password-cracking systems paper (WPA2 FPGA cluster) and one hardware-security paper on SAT attacks against logic locking sit slightly outside pure crypto; no duplicates or non-paper content found.

# Batch 123 (50 papers)
- Entire batch is CRYPTO 2016 (LNCS vols. 9813–9815, parts I–III): 50 full research papers, no duplicates or anomalies.
- Heavy symmetric-crypto focus: authenticated-encryption modes (SCT, EWCDM, XGCM), tweakable ciphers (XPX, SKINNY/MANTIS), and cryptanalysis (MISTY1 2^70 attack, FLIP, AES-like SPNs, division property).
- Strong theory/MPC cluster: obfuscation combiners and impossibility results, PPAD/Nash hardness, protocol transformations, network-hiding and OT-based MPC.
- ECDLP-relevant highlights: exTNFS lowers medium-prime NFS complexity (pairing key-size impact), efficient constant-time SIDH implementation, µKummer genus-2 hyperelliptic crypto on microcontrollers.
- Hardware/embedded security presence: Antikernel OS, vatiCAN automotive authentication, DRAM PUFs, parametric Trojans, ParTI combined side-channel/fault countermeasures.
- Notable cryptanalysis: subfield lattice attack on overstretched NTRU, practical break of Algebraic Eraser, polynomial-time break of GGH15 multilinear maps, quantum Simon's-algorithm attacks on symmetric schemes.

# Batch 124 (50 papers)
- Entire batch is theoretical cryptography, mostly TCC 2016-era conference papers (filenames 9815xxxx/9816xxxx and 9985xxxx); all 50 are genuine research papers with clear abstracts.
- Dominant themes: circular/KDM security separations from LWE, indistinguishability obfuscation (attacks on GGH13, FE-to-iO equivalences, proof-of-human-work from iO), and FHE variants (quantum FHE, multi-key multi-hop FHE, spooky encryption).
- Strong zero-knowledge / proof-systems cluster: IOPs (Ben-Sasson–Chiesa–Spooner, foundational for later STARKs), O-SNARKs, 3-message ZK, SZK vs randomized encodings, proofs of small secrets for (Ring-)LWE.
- Notable MPC/protocol papers: TWORAM (2-round ORAM), 3-round concurrent non-malleable commitments, constant-round MPC from BMR+SHE, fair coin-tossing, adaptive garbled circuits (two independent papers).
- Anomaly: despite the corpus being described as ECC/ECDLP-heavy, this batch contains essentially no elliptic-curve or ECDLP content; only one bilinear-pairing paper (Type-I to Type-III conversion) touches curves at all.

# Batch 125 (50 papers)
- Batch splits into two clear eras: a 2002–2004 block of applied cryptography (Boneh–Boyen IBE/signatures, signcryption, forward-secure signatures, stream-cipher cryptanalysis, braid-group attacks) and a ~2016 TCC-style block of theory papers (garbled RAM, MPC with identifiable abort, obfuscation, differential privacy, pseudoentropy).
- The first 15 files (99850xxx) form a coherent theory cluster: constant-round RAM-model 2PC, adaptive garbled RAM, secret-key functional encryption implying iO, and concentrated/computational differential privacy.
- ECDLP-relevant items: FGHR13 (symmetries in index calculus for ECDLP) and anon.pdf (breaking the Certicom ECC2K-130 challenge with parallel Pollard rho) — plus Koblitz's textbook on number theory and cryptography.
- Six files (AFproc, CameraDPV, CompressedPairings, DFSproc, ProcEC04, and one section of EUROCRYPT-adjacent material) have garbled/broken text extraction and cannot be summarized.
- Six files are LNCS proceedings front-matter/editorial-board pages (b104116, b105124, b11817, b72231, b75033, b94617) and one (authors.pdf) is a conference author index — none are research papers.
- Non-paper anomalies: PQShield 2022 white paper on post-quantum cryptography (industry white paper, not a research paper) and a 2-page AES/Rijndael extended abstract.

# Batch 126 (50 papers)
- Dominant flavor: Eurocrypt/Crypto 2002–2004-era LNCS papers on provable security — PSS, hybrid encryption/KEM, key-insulated and proxy signatures, zero-knowledge, identity-based schemes.
- Strong ECDLP cluster: the Certicom ECC2K-130 breaking effort appears four times (Cell CPUs, NVIDIA GPUs, FPGAs, overall status), plus FPGA ECDL records and a complexity bound on Semaev's index calculus.
- Notable classics: Vaudenay's CBC padding-oracle attack, Bellare–Kohno hash balance, Boneh–Boyen–Shacham short group signatures, Canetti–Halevi–Katz IBE→CCA, Coron on Coppersmith's method.
- Anomalies: 8 files are garbled font-encoding garbage (biham-chen-sha0, cl04, clean, desbcr04, dps, ec-final, eurocrypt.final, plus partial junk); 4 are LNCS/proceedings front matter; 1 is IACR COI policy; 1 is textbook slides.
- One duplicate pair: eprint_2012_002.pdf and full_gpu_indocrypt.pdf are both "ECC2K-130 on NVIDIA GPUs".

# Batch 127 (45 papers)
- Chunk contains 45 files, not the expected 50; heavily dominated by early-2000s Crypto/Eurocrypt-era papers (IBE, MPC, hash/MAC design, cryptanalysis) with a later ECDLP cluster (Semaev, ECC2K-130 GPU, GHS Weil descent, quasi-subfield polynomials, 113-bit Koblitz FPGA record).
- Notable papers: Boneh–Boyen IBE without random oracles, Cramer–Shoup universal hash proofs, Horwitz–Lynn HIBE, Black–Rogaway PMAC, Gentry–Szydlo NTRU signature cryptanalysis, Bernstein et al. ECC2K-130 on GPUs.
- 10 extracts are font-encoding garbage with no recoverable text (hybrid, linear-des, lncs, multicollisions, opsmtfinal, revised-Katz-Ostrovsky, rsaagg, sign, sv, vde); titles inferable only from filenames in a few cases.
- Non-research items: kent.pdf (PKI position essay), main.pdf and preface.pdf (Crypto 2000/2001 proceedings front matter), resume.pdf (Christophe Petit's CV), quasi-subfield...pdf (repository cover page only).
- ww_2014_368.pdf is an exact duplicate of ww2.pdf. oopsla-21.pdf is a PL/program-analysis paper (OOPSLA), an outlier in this crypto corpus.
