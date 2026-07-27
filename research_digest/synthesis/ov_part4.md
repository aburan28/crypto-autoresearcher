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
