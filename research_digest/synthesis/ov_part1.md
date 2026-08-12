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

