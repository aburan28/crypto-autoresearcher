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

