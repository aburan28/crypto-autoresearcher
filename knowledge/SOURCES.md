# Source Index

Every external source this program has consumed, and how reachable it
still is. Generated from the repository by `tools/build_source_index.py` —
do not hand-edit facts here; correct the underlying record and regenerate.
Machine-readable twin: `knowledge/sources.json`.

`knowledge/INDEX.md` lists what the corpus *believes*. This lists what it
*read*. The distinction that matters in every table below is whether the
bytes are in the repository: a hash this tool can recompute is a receipt,
a hash it cannot is an assertion by the session that recorded it.

## Summary

| Class | Count |
|---|---|
| Frozen source packages (`SRC-*`) | 7 |
| — of those with the artifact committed | 6 |
| Per-URL retrieval attempts | 1 |
| — succeeded | 0 |
| — failed or blocked | 1 |
| Source artifacts under `inputs/` | 9 |
| — hash recomputed and matching | 7 |
| — hash MISMATCH | 0 |
| — present but carrying no `.sha256` | 1 |
| — sought and never retrieved | 1 |
| Seed bibliography entries | 10 |
| Literature entries (`KN-LIT-*`) | 7859 |
| — with a resolvable external identifier | 2249 |
| — with no identifier recorded | 5610 |

Primary identifier kinds — one per entry, chosen in eprint > arXiv > DOI > ISBN > URL order, so an entry carrying both an ePrint number and a URL counts once, under ePrint: arxiv 1324, doi 149, eprint 742, url 34. Every identifier an entry carries is kept in `sources.json`.

`citation_verified` distribution: `False` 21, `True` 10, `body_read_from_user_provided_text` 1, `full_text` 4, `full_text_supplied` 2, `metadata` 1, `partial` 5, `read` 7486, `secondary_only` 1, `transcription_of_full_text_at_recorded_sha256` 2, `web` 326.

## 1. Frozen source packages

`SRC-*` records under `inputs/`. `Artifact in repo` is the field that
decides whether a later session can re-read what was read here.

| Record | Title | Author | Year | Package | Artifact in repo | Basis | URL | sha256 |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  | `inputs/SAFECURVES-20260825` | yes | package_contents |  |  |
| SRC-BENNETT-WEAKNESS-2023 | The Optimal Choice of Hypothesis Is the Weakest, Not the Shortest | Michael Timothy Bennett | 2023 | `inputs/BENNETT-WEAKNESS-2023` | yes | declared |  |  |
| SRC-DCP-SIMON-2026 | A Polynomial-Time Quantum Algorithm for the Dihedral Coset Problem [Preliminary Draft] | Daniel R. Simon | 2026 | `inputs/DCP-SIMON-2026` | yes | package_contents |  |  |
| SRC-OAI-TEN-PROOFS-2026 | Ten Advances in Mathematics and Theoretical Computer Science | OpenAI | 2026 | `inputs/OAI-TEN-PROOFS-2026` | **no** | declared | https://cdn.openai.com/pdf/ten-proofs-oai.pdf | 64b900d5fae6fe22 |
| SRC-P13-PANNY-POC | Proof-of-concept implementation of the Wesolowski 2026 p^{1/3+o(1)} attack on OneEnd | Lorenz Panny |  | `inputs/P13-PANNY-POC` | yes | frozen_path | https://yx7.cc/files/p-one-third.py | 4f43780404a7ab5d |
| SRC-P13-WESOLOWSKI-2026 | The supersingular isogeny problem in time and memory p^{1/3+o(1)} | Benjamin Wesolowski | 2026 | `inputs/P13-WESOLOWSKI-2026` | yes | package_contents |  |  |
| SRC-SATIC-TRIMOSKA-2019 | A SAT-Based Approach for Index Calculus on Binary Elliptic Curves |  | 2019 | `inputs/SATIC-TRIMOSKA-2019` | yes | package_contents |  |  |

Declared reproducibility limitations:

- **SRC-OAI-TEN-PROOFS-2026** — The PDF is not committed, so the sha256 above cannot be recomputed from this repository and no later session can re-read the source these summaries were taken from. This record is an assertion about a read that happened, not a checkable receipt for it -- the contrast is SRC-P13-WESOLOWSKI-2026, whose full text is frozen at inputs/P13-WESOLOWSKI-2026/paper_fulltext.md.

## 2. Per-URL retrieval attempts

From `provenance.json` packages. Failed attempts are kept: a blocked
fetch records that the source was sought and why it is missing, which is
not the same as never having looked.

| Source id | URL | Status | HTTP | Retrieved at | Vendored path |
|---|---|---|---|---|---|
| dent-galbraith-hidden.pdf |  | failed |  |  | `inputs/ECTD-TESKE-20260731/sources/dent-galbraith-hidden.pdf` |

## 3. Source artifacts under `inputs/`

The only rows in this document whose integrity this tool checks itself,
and only where a `.sha256` sidecar states an expected value:

- `match` / `MISMATCH` — sidecar present, hash recomputed here.
- `present_unhashed` — the file is in the repository but nothing declares
  what it should hash to, so this index vouches for its presence only.
- `never_retrieved` — a `.FAIL` marker with no file. The source was sought
  and not obtained; the row stays so the attempt is not mistaken for an
  absence of interest.

`fetch marker` flags a sibling `.FAIL` file. Beside a *present* file it
records that some fetch failed, and says nothing about the file that is here.

| Path | Bytes | Verdict | Declared sha256 | Fetch marker |
|---|---|---|---|---|
| `inputs/BENNETT-WEAKNESS-2023/arxiv-2301.12987v4.pdf` | 211063 | match | b664a4074578629b |  |
| `inputs/ECTD-TESKE-20260731/sources/defeo-1711.04062.pdf` | 901036 | match | ca0e70abad06f732 |  |
| `inputs/ECTD-TESKE-20260731/sources/dent-galbraith-hidden.pdf` |  | **never_retrieved** |  | yes |
| `inputs/ECTD-TESKE-20260731/sources/fght-2016-961.pdf` | 618309 | **present_unhashed** |  | yes |
| `inputs/ECTD-TESKE-20260731/sources/galbraith-iso.pdf` | 258454 | match | 77362b01d48d9391 |  |
| `inputs/ECTD-TESKE-20260731/sources/jk-2020-1436.pdf` | 242478 | match | 65a8ecff9a6a3b27 | yes |
| `inputs/ECTD-TESKE-20260731/sources/jmv-0811.0647.pdf` | 294859 | match | 118c6096f6287f4b |  |
| `inputs/ECTD-TESKE-20260731/sources/kutas-2019-1290.pdf` | 430504 | match | a7f94571aa03ce34 | yes |
| `inputs/ECTD-TESKE-20260731/sources/teske-2003-058.pdf` | 287387 | match | 8d889ae0b1b03f77 | yes |

## 4. Seed bibliography

`inputs/bibliography.json` — the hand-curated list the corpus started from.

| id | Title | Authors | Year | Venue | URL |
|---|---|---|---|---|---|
| `amadori_pintore_sala_2017_prime_field` | On the discrete logarithm problem for prime-field elliptic curves | Alessandro Amadori; Federico Pintore; Massimiliano Sala | 2017 | Cryptology ePrint Archive, Paper 2017/609 | https://eprint.iacr.org/2017/609 |
| `faugere_huot_joux_renault_vitse_2014_symmetrized` | Symmetrized summation polynomials: Using small order torsion points to speed up elliptic curve index calculus | Jean-Charles Faugere; Louise Huot; Antoine Joux; Guillaume Renault; Vanessa Vitse | 2014 | EUROCRYPT 2014 | https://researchportal.ip-paris.fr/en/publications/symmetrized-summation-polynomials-using-small-order-torsion-point/ |
| `faugere_perret_petit_renault_2012_binary_complexity` | Improving the Complexity of Index Calculus Algorithms in Elliptic Curves over Binary Fields | Jean-Charles Faugere; Ludovic Perret; Christophe Petit; Guenael Renault | 2012 | EUROCRYPT 2012 | https://www.iacr.org/cryptodb/data/paper.php?pubkey=24270 |
| `gaudry_2009_abelian_varieties` | Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem | Pierrick Gaudry | 2009 | Journal of Symbolic Computation | https://doi.org/10.1016/j.jsc.2008.08.005 |
| `karabina_2015_point_decomposition_binary` | Point Decomposition Problem in Binary Elliptic Curves | Koray Karabina | 2015 | arXiv:1504.02347 | https://arxiv.org/abs/1504.02347 |
| `kousidis_wiemers_2015_first_fall_degree` | On the First Fall Degree of Summation Polynomials | Stavros Kousidis; Andreas Wiemers | 2015 | Cryptology ePrint Archive, Paper 2015/1121 | https://eprint.iacr.org/2015/1121 |
| `mcguire_mueller_2017_grobner_free` | A New Index Calculus Algorithm for the Elliptic Curve Discrete Logarithm Problem and Summation Polynomial Evaluation | Gary McGuire; Daniela Mueller | 2017 | Cryptology ePrint Archive, Paper 2017/1262 | https://eprint.iacr.org/2017/1262 |
| `semaev_2004_summation_polynomials` | Summation polynomials and the discrete logarithm problem on elliptic curves | Igor Semaev | 2004 | Cryptology ePrint Archive, Paper 2004/031 | https://eprint.iacr.org/2004/031 |
| `shantz_teske_2013_experimental_study` | Solving the Elliptic Curve Discrete Logarithm Problem Using Semaev Polynomials, Weil Descent and Grobner Basis Methods -- an Experimental Study | Michael Shantz; Edlyn Teske | 2013 | Cryptology ePrint Archive, Paper 2013/596 | https://eprint.iacr.org/2013/596 |
| `trimoska_ionica_dequen_2020_sat_pdp` | A SAT-Based Approach for Index Calculus on Binary Elliptic Curves | Monika Trimoska; Sorina Ionica; Gilles Dequen | 2020 | AFRICACRYPT 2020 / PMC open access | https://pmc.ncbi.nlm.nih.gov/articles/PMC7334981/ |

## 5. Literature citations with a resolvable identifier

2249 of 7859 `KN-LIT-*` entries carry an
eprint, arXiv, DOI, ISBN or URL identifier.

| ID | Title | Year | Identifier | Verified |
|---|---|---|---|---|
| KN-LIT-001 | Summation polynomials and the discrete logarithm problem on elliptic curves | 2004 | `eprint:2004/031` | web |
| KN-LIT-002 | Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem | 2009 | `eprint:2004/073` | web |
| KN-LIT-003 | On the discrete logarithm problem in elliptic curves | 2011 | `doi:10.1112/s0010437x10005075` | web |
| KN-LIT-004 | Using symmetries in the index calculus for elliptic curves discrete logarithm | 2014 | `doi:10.1007/s00145-013-9158-5` | web |
| KN-LIT-005 | On polynomial systems arising from a Weil descent | 2012 | `eprint:2012/146` | web |
| KN-LIT-006 | Recent progress on the elliptic curve discrete logarithm problem | 2016 | `eprint:2015/1022` | web |
| KN-LIT-007 | Constructive and destructive facets of Weil descent on elliptic curves | 2002 | `doi:10.1007/s00145-001-0011-x` | false |
| KN-LIT-008 | Monte Carlo methods for index computation (mod p) | 1978 | `doi:10.2307/2006496` | web |
| KN-LIT-009 | New algorithm for the discrete logarithm problem on elliptic curves | 2015 | `eprint:2015/310` | web |
| KN-LIT-010 | Solving the elliptic curve discrete logarithm problem using Semaev polynomials, Weil descent and Groebner basis methods - an experimental study | 2013 | `eprint:2013/596` | web |
| KN-LIT-011 | Lower Bounds for Discrete Logarithms and Related Problems | 1997 | `doi:10.1007/3-540-69053-0_18` | web |
| KN-LIT-012 | Parallel Collision Search with Cryptanalytic Applications | 1999 | `doi:10.1007/pl00003816` | web |
| KN-LIT-013 | The Discrete-Logarithm Problem with Preprocessing | 2018 | `eprint:2017/1113` | web |
| KN-LIT-0138f3 | Message-recovery horizontal correlation attack on Classic McEliece | 2025 | `eprint:2023/546` | web |
| KN-LIT-014 | The number of roots of a system of equations (Bernstein / BKK bound) | 1975 | `doi:10.1007/bf01075595` | web |
| KN-LIT-015 | A polyhedral method for solving sparse polynomial systems | 1995 | `doi:10.1090/s0025-5718-1995-1297471-4` | web |
| KN-LIT-016 | Solving sparse linear equations over finite fields | 1986 | `doi:10.1109/tit.1986.1057137` | web |
| KN-LIT-017 | Solving homogeneous linear equations over GF(2) via block Wiedemann algorithm | 1994 | `doi:10.1090/s0025-5718-1994-1192970-7` | web |
| KN-LIT-018 | The Tate pairing via elliptic nets | 2007 | `eprint:2006/392` | web |
| KN-LIT-019 | On the number of incidences between points and planes in three dimensions | 2018 | `arxiv:1407.0426` | web |
| KN-LIT-01b5dc | The complexity of information set decoding | 1990 | `doi:10.1109/18.57202` | web |
| KN-LIT-01f731 | A new sieving-style information-set decoding algorithm | 2023 | `eprint:2023/247` | web |
| KN-LIT-020 | The Xedni Calculus and the Elliptic Curve Discrete Logarithm Problem | 2000 | `doi:10.1023/a:1008319518035` | web |
| KN-LIT-021 | Analysis of the Xedni Calculus Attack | 2000 | `doi:10.1023/a:1008312401197` | web |
| KN-LIT-022 | Elliptic Curve Discrete Logarithm Problem over Small Degree Extension Fields | 2013 | `eprint:2010/157` | web |
| KN-LIT-023 | Improving the Complexity of Index Calculus Algorithms in Elliptic Curves over Binary Fields | 2012 | `doi:10.1007/978-3-642-29011-4_4` | web |
| KN-LIT-024 | On the First Fall Degree of Summation Polynomials | 2019 | `eprint:2015/1121` | web |
| KN-LIT-025 | Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields | 2016 | `doi:10.1007/978-3-662-49387-8_1` | web |
| KN-LIT-0258c8 | Decoding one out of many | 2011 | `eprint:2011/367` | web |
| KN-LIT-026 | An Algorithm for Finding the Basis Elements of the Residue Class Ring of a Zero-Dimensional Polynomial Ideal (Buchberger's thesis) | 1965 | `doi:10.1016/j.jsc.2005.09.007` | web |
| KN-LIT-027 | A new efficient algorithm for computing Grobner bases (F4) | 1999 | `doi:10.1016/s0022-4049(99)00005-5` | web |
| KN-LIT-028 | A new efficient algorithm for computing Grobner bases without reduction to zero (F5) | 2002 | `doi:10.1145/780506.780516` | web |
| KN-LIT-029 | On the complexity of Grobner basis computation of semi-regular overdetermined algebraic equations | 2004 | `url:magali.bardet.free.fr/publis/ltx43bf.pdf` | web |
| KN-LIT-030 | Linear Representations of Finite Groups | 1977 | `doi:10.1007/978-1-4684-9458-7` | web |
| KN-LIT-031 | Grobner bases of ideals invariant under a commutative group - the non-modular case | 2013 | `doi:10.1145/2465506.2465944` | web |
| KN-LIT-032 | Tensor-Train Decomposition | 2011 | `doi:10.1137/090752286` | web |
| KN-LIT-033 | Simulating Quantum Computation by Contracting Tensor Networks | 2008 | `arxiv:quant-ph/0511069` | web |
| KN-LIT-034 | Fast counting with tensor networks | 2019 | `arxiv:1805.00475` | web |
| KN-LIT-035 | The diamond lemma for ring theory | 1978 | `doi:10.1016/0001-8708(78)90010-5` | web |
| KN-LIT-036 | An introduction to commutative and noncommutative Grobner bases | 1994 | `doi:10.1016/0304-3975(94)90283-6` | web |
| KN-LIT-037 | Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities | 1997 | `doi:10.1007/s001459900030` | web |
| KN-LIT-038 | A Sum-Product Estimate in Finite Fields, and Applications | 2004 | `arxiv:math/0301343` | web |
| KN-LIT-039 | Chebotarev and his Density Theorem | 1996 | `doi:10.1007/bf03027290` | web |
| KN-LIT-040 | Hamiltonian Systems and Transformation in Hilbert Space | 1931 | `doi:10.1073/pnas.17.5.315` | web |
| KN-LIT-041 | Faster Point Multiplication on Elliptic Curves with Efficient Endomorphisms (GLV) | 2001 | `doi:10.1007/3-540-44647-8_11` | web |
| KN-LIT-042 | Faster Attacks on Elliptic Curve Cryptosystems | 1998 | `doi:10.1007/3-540-48892-8_15` | web |
| KN-LIT-043 | Hardness of Computing the Most Significant Bits of Secret Keys in Diffie-Hellman and Related Schemes (Hidden Number Problem) | 1996 | `doi:10.1007/3-540-68697-5_11` | web |
| KN-LIT-044 | The Insecurity of (EC)DSA with Partially Known Nonces (Nguyen-Shparlinski) | 2003 | `doi:10.1023/a:1025436905711` | web |
| KN-LIT-045 | Lattice Attacks on Digital Signature Schemes | 2001 | `doi:10.1023/a:1011214926272` | web |
| KN-LIT-046 | Factoring polynomials with rational coefficients (the LLL algorithm) | 1982 | `doi:10.1007/bf01457454` | web |
| KN-LIT-047 | Lattice basis reduction - Improved practical algorithms and solving subset sum problems (BKZ) | 1994 | `doi:10.1007/bf01581144` | web |
| KN-LIT-0471e7 | Introduction to Topics in Computational Number Theory Inspired by Peter L. Montgomery | 2017 | `url:www.cambridge.org/9781107109353` | read |
| KN-LIT-048 | New directions in nearest neighbor searching with applications to lattice sieving (BDGL) | 2016 | `eprint:2015/1128` | web |
| KN-LIT-049 | Generating Hard Instances of Lattice Problems (the SIS problem) | 1996 | `doi:10.1145/237814.237838` | web |
| KN-LIT-050 | On Lattices, Learning with Errors, Random Linear Codes, and Cryptography (the LWE problem) | 2009 | `doi:10.1145/1568318.1568324` | web |
| KN-LIT-051 | A Decade of Lattice Cryptography | 2016 | `eprint:2015/939` | web |
| KN-LIT-052 | NTRU - A Ring-Based Public Key Cryptosystem | 1998 | `doi:10.1007/bfb0054868` | web |
| KN-LIT-053 | On Ideal Lattices and Learning with Errors over Rings (Ring-LWE) | 2013 | `eprint:2012/230` | web |
| KN-LIT-054 | Worst-case to average-case reductions for module lattices (Module-LWE/SIS) | 2015 | `eprint:2012/090` | web |
| KN-LIT-055 | CRYSTALS-Kyber - A CCA-Secure Module-Lattice-Based KEM (ML-KEM / FIPS 203) | 2018 | `eprint:2017/634` | web |
| KN-LIT-056 | CRYSTALS-Dilithium - A Lattice-Based Digital Signature Scheme (ML-DSA / FIPS 204) | 2018 | `eprint:2017/633` | web |
| KN-LIT-057 | Falcon - Fast-Fourier Lattice-based Compact Signatures over NTRU (FN-DSA / FIPS 206 draft) | 2020 | `url:falcon-sign.info` | web |
| KN-LIT-058 | Trapdoors for Hard Lattices and New Cryptographic Constructions (GPV) | 2008 | `eprint:2007/432` | web |
| KN-LIT-059 | Fiat-Shamir with Aborts - Applications to Lattice and Factoring-Based Signatures | 2009 | `doi:10.1007/978-3-642-10366-7_35` | web |
| KN-LIT-060 | Fully Homomorphic Encryption Using Ideal Lattices | 2009 | `doi:10.1145/1536414.1536440` | web |
| KN-LIT-061 | On the concrete hardness of Learning with Errors (the LWE estimator) | 2015 | `eprint:2015/046` | web |
| KN-LIT-062 | Towards quantum-resistant cryptosystems from supersingular elliptic curve isogenies (SIDH) | 2014 | `eprint:2011/506` | web |
| KN-LIT-063 | Cryptographic Hash Functions from Expander Graphs (CGL) | 2009 | `eprint:2006/021` | web |
| KN-LIT-064 | SIKE - Supersingular Isogeny Key Encapsulation (NIST PQC submission, broken 2022) | 2022 | `url:csrc.nist.gov/csrc/media/projects/post-quantum-cryptography/documents/round-4/submissions/sike-spec.pdf` | web |
| KN-LIT-065 | An efficient key recovery attack on SIDH | 2023 | `eprint:2022/975` | web |
| KN-LIT-066 | A Direct Key Recovery Attack on SIDH (arbitrary starting curve) | 2023 | `eprint:2023/640` | web |
| KN-LIT-067 | Breaking SIDH in Polynomial Time | 2023 | `eprint:2022/1038` | web |
| KN-LIT-068 | The number of curves of genus two with elliptic differentials (Kani's theorem) | 1997 | `doi:10.1515/crll.1997.485.93` | web |
| KN-LIT-069 | CSIDH - An Efficient Post-Quantum Commutative Group Action | 2018 | `eprint:2018/383` | web |
| KN-LIT-06af57 | High-performance implementations of Classic McEliece KEM on GPUs | 2025 | `doi:10.1109/iscas56072.2025.11043393` | web |
| KN-LIT-070 | Hard Homogeneous Spaces / Public-Key Cryptosystem Based on Isogenies (Couveignes; Rostovtsev-Stolbunov) | 2006 | `eprint:2006/291` | web |
| KN-LIT-071 | Constructing elliptic curve isogenies in quantum subexponential time (Childs-Jao-Soukharev) | 2014 | `arxiv:1012.4019` | web |
| KN-LIT-072 | SQIsign - Compact Post-Quantum Signatures from Quaternions and Isogenies | 2020 | `eprint:2020/1240` | web |
| KN-LIT-072f64 | Reducing the number of qubits in quantum information set decoding | 2024 | `eprint:2024/907` | web |
| KN-LIT-073 | On the quaternion ell-isogeny path problem (KLPT) | 2014 | `eprint:2014/505` | web |
| KN-LIT-074 | The supersingular isogeny path and endomorphism ring problems are equivalent | 2021 | `eprint:2021/919` | web |
| KN-LIT-075 | Die Typen der Multiplikatorenringe elliptischer Funktionenkorper (the Deuring correspondence) | 1941 | `doi:10.1007/bf02940746` | web |
| KN-LIT-076 | On the Security of Supersingular Isogeny Cryptosystems (GPST adaptive attack) | 2016 | `eprint:2016/859` | web |
| KN-LIT-077 | Faster Algorithms for Isogeny Problems Using Torsion Point Images | 2017 | `eprint:2017/571` | web |
| KN-LIT-078 | Computing isogenies between supersingular elliptic curves over F_p (Delfs-Galbraith) | 2016 | `arxiv:1310.7789` | web |
| KN-LIT-079 | A Quantum Algorithm for Computing Isogenies between Supersingular Elliptic Curves | 2014 | `doi:10.1007/978-3-319-13039-2_25` | web |
| KN-LIT-080 | Thorns in Polynomial Convolution | 2026 | `eprint:2026/1022` | full_text |
| KN-LIT-081 | On Reduction Probability Models in Lattice Sieving | 2026 | `eprint:2026/1465` | full_text |
| KN-LIT-082 | An improved algorithm for computing logarithms over GF(p) and its cryptographic significance | 1978 | `doi:10.1109/tit.1978.1055817` | read |
| KN-LIT-082ca9 | The giant footprint is the smallest: low-footprint decryption of Classic McEliece | 2025 | `doi:10.1109/csp66295.2025.00011` | web |
| KN-LIT-083 | Class number, a theory of factorization, and genera | 1971 | `doi:10.1090/pspum/020/0316385` | web |
| KN-LIT-084 | Reducing elliptic curve logarithms to logarithms in a finite field | 1993 | `doi:10.1109/18.259647` | web |
| KN-LIT-085 | A remark concerning m-divisibility and the discrete logarithm in the divisor class group of curves | 1994 | `doi:10.1090/s0025-5718-1994-1218343-6` | web |
| KN-LIT-086 | The Improbability That an Elliptic Curve Has Subexponential Discrete Log Problem under the Menezes-Okamoto-Vanstone Algorithm | 1998 | `doi:10.1007/s001459900040` | web |
| KN-LIT-087 | Evaluation of discrete logarithms in a group of p-torsion points of an elliptic curve in characteristic p | 1998 | `doi:10.1090/s0025-5718-98-00887-4` | web |
| KN-LIT-088 | Fermat quotients and the polynomial time discrete log algorithm for anomalous elliptic curves | 1998 | `url:www.lanfanshu.com/paper/61e50034d7071fa839f637c2` | web |
| KN-LIT-089 | The Discrete Logarithm Problem on Elliptic Curves of Trace One | 1999 | `doi:10.1007/s001459900052` | web |
| KN-LIT-090 | The GHS Attack in odd Characteristic | 2003 | `url:www.math.uni-leipzig.de/~diem/preprints/english.html` | web |
| KN-LIT-091 | A Key Recovery Attack on Discrete Log-based Schemes Using a Prime Order Subgroup | 1997 | `doi:10.1007/bfb0052240` | web |
| KN-LIT-092 | Differential Fault Attacks on Elliptic Curve Cryptosystems | 2000 | `doi:10.1007/3-540-44598-6_8` | web |
| KN-LIT-093 | Curve25519 - new Diffie-Hellman speed records | 2006 | `doi:10.1007/11745853_14` | read |
| KN-LIT-094 | The Full Cost of Cryptanalytic Attacks | 2004 | `doi:10.1007/s00145-003-0213-5` | read |
| KN-LIT-095 | Solving a 112-bit Prime Elliptic Curve Discrete Logarithm Problem on Game Consoles using Sloppy Reduction | 2012 | `doi:10.1504/ijact.2012.045590` | read |
| KN-LIT-096 | Breaking ECC2K-130 | 2009 | `eprint:2009/541` | read |
| KN-LIT-097 | Faster elliptic-curve discrete logarithms on FPGAs | 2016 | `eprint:2016/382` | read |
| KN-LIT-098 | Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer | 1997 | `doi:10.1137/s0097539795293172` | read |
| KN-LIT-099 | Quantum Resource Estimates for Computing Elliptic Curve Discrete Logarithms | 2017 | `eprint:2017/598` | read |
| KN-LIT-0f43ad | Finding the permutation between equivalent linear codes: The support splitting algorithm | 2000 | `doi:10.1109/18.850662` | web |
| KN-LIT-100 | Lattice Reduction by Random Sampling and Birthday Methods | 2003 | `doi:10.1007/3-540-36494-3_14` | read |
| KN-LIT-1000 | Local Inversion of maps: Black box Cryptanalysis | 2022 | `arxiv:2207.03247` | read |
| KN-LIT-1001 | Mazur’s isogeny theorem | 2022 | `arxiv:2209.03153` | read |
| KN-LIT-1002 | Meet-in-the-Middle | 2022 | `eprint:2022/171` | read |
| KN-LIT-1003 | Michal Kepkowski*, Lucjan Hanzlik, Ian Wood, and Mohamed Ali Kaafar arXiv:2205.08071v1 [cs.CR] 17 May 2022 How Not to Handle Keys: Timing Attacks on FIDO | 2022 | `arxiv:2205.08071` | read |
| KN-LIT-1004 | Mind the TWEAKEY Schedule: Cryptanalysis on SKINNYe-64-256 | 2022 | `eprint:2022/789` | read |
| KN-LIT-1005 | New Time-Memory Trade-Offs for Subset Sum | 2022 | `eprint:2022/1329` | read |
| KN-LIT-1006 | ON A COUPLED KADOMTSEV–PETVIASHVILI SYSTEM ASSOCIATED WITH AN ELLIPTIC CURVE | 2022 | `arxiv:2202.07588` | read |
| KN-LIT-1007 | On Concurrent Multi-Party Quantum Computation | 2022 | `arxiv:2207.05861` | read |
| KN-LIT-1008 | On elliptic curves with p-isogenies over quadratic fields | 2022 | `arxiv:2203.03533` | read |
| KN-LIT-1009 | ON Fp -ROOTS OF THE HILBERT CLASS POLYNOMIAL MODULO p | 2022 | `arxiv:2202.04317` | read |
| KN-LIT-101 | BKZ 2.0: Better Lattice Security Estimates | 2011 | `doi:10.1007/978-3-642-25385-0_1` | read |
| KN-LIT-1010 | ON THE ACYCLICITY OF REDUCTIONS OF ELLIPTIC CURVES MODULO PRIMES IN ARITHMETIC PROGRESSIONS | 2022 | `arxiv:2206.00872` | read |
| KN-LIT-1011 | ON THE ALGEBRA OF ELLIPTIC CURVES | 2022 | `arxiv:2209.05065` | read |
| KN-LIT-1012 | ON THE CORANK OF THE FINE SELMER GROUP OF AN ELLIPTIC CURVE OVER A Zp -EXTENSION | 2022 | `arxiv:2208.13247` | read |
| KN-LIT-1013 | ON THE DECISIONAL DIFFIE–HELLMAN PROBLEM FOR CLASS GROUP ACTIONS ON ORIENTED ELLIPTIC CURVES | 2022 | `arxiv:2210.01160` | read |
| KN-LIT-1014 | On the differential spectrum of a class of APN power functions over odd characteristic finite fields and their c-differential properties | 2022 | `arxiv:2210.10390` | read |
| KN-LIT-1015 | On the Hardness of the Finite Field Isomorphism Problem | 2022 | `eprint:2022/998` | read |
| KN-LIT-1016 | ON THE MODULARITY OF ELLIPTIC CURVES OVER THE CYCLOTOMIC Zp -EXTENSION OF SOME REAL QUADRATIC FIELDS | 2022 | `arxiv:2205.09790` | read |
| KN-LIT-1017 | ON THE PRIME SELMER RANKS OF CYCLIC PRIME TWIST FAMILIES OF ELLIPTIC CURVES OVER GLOBAL FUNCTION FIELDS | 2022 | `arxiv:2211.11486` | read |
| KN-LIT-1018 | ON THE VANISHING OF TWISTED L-FUNCTIONS OF ELLIPTIC CURVES OVER RATIONAL FUNCTION FIELDS | 2022 | `arxiv:2207.00197` | read |
| KN-LIT-1019 | Optimal Single-Server Private Information Retrieval | 2022 | `eprint:2022/609` | read |
| KN-LIT-102 | Lattice Enumeration Using Extreme Pruning | 2010 | `doi:10.1007/978-3-642-13190-5_13` | read |
| KN-LIT-1020 | ORDINARY ISOGENY GRAPHS OVER Fp : THE INVERSE VOLCANO PROBLEM | 2022 | `arxiv:2210.01086` | read |
| KN-LIT-1021 | ORIENTATIONS AND CYCLES IN SUPERSINGULAR ISOGENY GRAPHS | 2022 | `eprint:2022/562` | read |
| KN-LIT-1022 | ORIENTEERING WITH ONE ENDOMORPHISM | 2022 | `arxiv:2201.11079` | read |
| KN-LIT-1023 | Pairing-Friendly Elliptic Curves: Revisited | 2022 | `arxiv:2212.01855` | read |
| KN-LIT-1024 | POLYNOMIAL BOUNDS ON TORSION FROM A FIXED GEOMETRIC ISOGENY CLASS OF ELLIPTIC CURVES | 2022 | `arxiv:2210.10177` | read |
| KN-LIT-1025 | POLYNOMIALS REALIZING IMAGES OF GALOIS REPRESENTATIONS OF AN ELLIPTIC CURVE | 2022 | `arxiv:2209.13477` | read |
| KN-LIT-1026 | Probabilistic Hash-and-Sign with Retry in the Quantum Random Oracle Model? | 2022 | `eprint:2022/135` | read |
| KN-LIT-1027 | Protecting the most significant bits in scalar multiplication algorithms | 2022 | `eprint:2022/1254` | read |
| KN-LIT-1028 | p∞ –SELMER RANKS OF CM ABELIAN VARIETIES | 2022 | `arxiv:2208.14563` | read |
| KN-LIT-1029 | Quantum Analysis of | 2022 | `eprint:2022/683` | read |
| KN-LIT-103 | Sieve algorithms for the shortest vector problem are practical | 2008 | `doi:10.1515/jmc.2008.009` | read |
| KN-LIT-1030 | Quantum Impossible Differential Attacks: | 2022 | `eprint:2022/754` | read |
| KN-LIT-1031 | RADICAL ISOGENIES AND MODULAR CURVES | 2022 | `eprint:2022/1446` | read |
| KN-LIT-1032 | REMARKS ON HILBERT’S TENTH PROBLEM AND THE IWASAWA THEORY OF ELLIPTIC CURVES | 2022 | `arxiv:2206.06296` | read |
| KN-LIT-1033 | RESIDUAL SUPERSINGULAR IWASAWA THEORY OVER QUADRATIC IMAGINARY FIELDS | 2022 | `arxiv:2206.03679` | read |
| KN-LIT-1034 | Revisiting Related-Key Boomerang attacks on AES using computer-aided tool | 2022 | `eprint:2022/725` | read |
| KN-LIT-1035 | Rocca: An Efficient AES-based Encryption Scheme for Beyond 5G | 2022 | `eprint:2022/116` | read |
| KN-LIT-1036 | Semi-Quantum Tokenized Signatures | 2022 | `eprint:2022/228` | read |
| KN-LIT-1037 | Solving Small Exponential ECDLP in EC-based Additively Homomorphic Encryption and Applications | 2022 | `eprint:2022/1573` | read |
| KN-LIT-1038 | Speeding-Up Parallel Computation of Large Smooth-Degree Isogeny using Precedence-Constrained Scheduling | 2022 | `eprint:2022/1103` | read |
| KN-LIT-1039 | STARK-HEEGNER POINTS AND DIAGONAL CLASSES | 2022 | `arxiv:2207.01310` | read |
| KN-LIT-104 | Faster exponential time algorithms for the shortest vector problem | 2010 | `doi:10.1137/1.9781611973075.119` | read |
| KN-LIT-1040 | Strongly Anonymous Ratcheted Key Exchange | 2022 | `eprint:2022/118` | read |
| KN-LIT-1041 | Structural Evaluation of AES-like Ciphers against Mixture Differential Cryptanalysis | 2022 | `eprint:2022/1199` | read |
| KN-LIT-1042 | STUDYING HILBERT’S 10th PROBLEM VIA EXPLICIT ELLIPTIC CURVES | 2022 | `arxiv:2207.07021` | read |
| KN-LIT-1043 | Synthesizing Quantum Circuits of AES with | 2022 | `eprint:2022/620` | read |
| KN-LIT-1044 | TAMAGAWA NUMBERS OF ELLIPTIC CURVES WITH TORSION POINTS | 2022 | `arxiv:2202.06235` | read |
| KN-LIT-1045 | THE 3-ISOGENY SELMER GROUPS OF THE ELLIPTIC CURVES y 2 = x3 + n2 | 2022 | `arxiv:2211.06062` | read |
| KN-LIT-1046 | THE DISTRIBUTION OF l∞ -SELMER GROUPS IN DEGREE l TWIST | 2022 | `arxiv:2207.05674` | read |
| KN-LIT-1047 | The Generalized Montgomery Coordinate: A New Computational Tool for Isogeny-based Cryptography | 2022 | `eprint:2022/150` | read |
| KN-LIT-1048 | The Hardness of LPN over Any Integer Ring and Field for PCG Applications Hanlin Liu ID | 2022 | `eprint:2022/712` | read |
| KN-LIT-1049 | THE LOCAL-GLOBAL PRINCIPLE FOR DIVISIBILITY IN CM | 2022 | `arxiv:2201.11839` | read |
| KN-LIT-105 | Shortest Vector from Lattice Sieving: a Few Dimensions for Free | 2017 | `eprint:2017/999` | read |
| KN-LIT-1050 | THE MORDELL-WEIL LATTICE OF AN INOSE SURFACE ARISING FROM ISOGENOUS ELLIPTIC CURVES | 2022 | `arxiv:2209.02463` | read |
| KN-LIT-1051 | THE OSTROWSKI QUOTIENT OF AN ELLIPTIC CURVE | 2022 | `arxiv:2202.04922` | read |
| KN-LIT-1052 | THE p-ADIC LIMITS OF CLASS NUMBERS IN Zp -TOWERS | 2022 | `arxiv:2210.06182` | read |
| KN-LIT-1053 | Triangulating Rebound Attack on AES-like Hashing | 2022 | `eprint:2022/731` | read |
| KN-LIT-1054 | Truncated Boomerang Attacks and Application to AES-based Ciphers | 2022 | `eprint:2022/701` | read |
| KN-LIT-1055 | WATKINS’ CONJECTURE FOR ELLIPTIC CURVES OVER FUNCTION FIELDS | 2022 | `arxiv:2203.10932` | read |
| KN-LIT-1056 | Yet Another Algebraic Cryptanalysis of Small Scale Variants of AES | 2022 | `eprint:2022/695` | read |
| KN-LIT-1057 | 1 / 62 2025:18 Quantum Money from Abelian Group Actions | 2023 | `arxiv:2307.12120` | read |
| KN-LIT-1058 | 2-ADIC GALOIS IMAGES OF NON-CM ISOGENY-TORSION GRAPHS DEFINED OVER Q | 2023 | `arxiv:2302.06094` | read |
| KN-LIT-1059 | A New Linear Distinguisher for Four-Round AES | 2023 | `eprint:2023/398` | read |
| KN-LIT-106 | The General Sieve Kernel and New Records in Lattice Reduction | 2019 | `eprint:2019/089` | read |
| KN-LIT-1060 | A note on “a multi-instance cancelable fingerprint biometric based secure session key agreement protocol employing elliptic curve | 2023 | `eprint:2023/993` | read |
| KN-LIT-1061 | A Note on “A Secure Anonymous D2D Mutual Authentication and Key Agreement Protocol for IoT” | 2023 | `eprint:2023/726` | read |
| KN-LIT-1062 | A note on “authenticated key agreement protocols for dew-assisted IoT systems” | 2023 | `eprint:2023/1497` | read |
| KN-LIT-1063 | A Post-Quantum Round-Optimal Oblivious PRF from Isogenies | 2023 | `eprint:2023/225` | read |
| KN-LIT-1064 | A question about points on an elliptic curve with prime denominator | 2023 | `arxiv:2307.09406` | read |
| KN-LIT-1065 | A REMARK ON THE CHARACTERISTIC ELEMENTS OF ANTICYCLOTOMIC SELMER GROUPS OF ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION AT SUPERSINGULAR PRIMES | 2023 | `arxiv:2307.12053` | read |
| KN-LIT-1066 | A Systematic Study of Data Augmentation for Protected AES Implementations | 2023 | `eprint:2023/1179` | read |
| KN-LIT-1067 | A Tightly Secure Identity-based Signature Scheme from Isogenies | 2023 | `eprint:2023/426` | read |
| KN-LIT-1068 | ABSOLUTE ZETA FUNCTIONS ARISING FROM CEILING AND FLOOR PUISEUX POLYNOMIALS | 2023 | `arxiv:2308.03232` | read |
| KN-LIT-1069 | ALGEBRAIC RELATIONS OVER FINITE FIELDS THAT PRESERVE THE ENDOMORPHISM RINGS OF CM j-INVARIANTS | 2023 | `arxiv:2308.10976` | read |
| KN-LIT-107 | Post-quantum key exchange - a new hope | 2016 | `eprint:2015/1092` | read |
| KN-LIT-1070 | All You Need Is Fault: Zero-Value Attacks on AES and a New λ-Detection M&M | 2023 | `eprint:2023/1129` | read |
| KN-LIT-1071 | AN ANALOGUE OF A CONJECTURE OF RASMUSSEN AND TAMAGAWA FOR ABELIAN VARIETIES OVER FUNCTION FIELDS | 2023 | `arxiv:2310.11100` | read |
| KN-LIT-1072 | An Elementary Formal Proof of the Group Law on Weierstrass Elliptic Curves in any Characteristic | 2023 | `arxiv:2302.10640` | read |
| KN-LIT-1073 | ANTICYCLOTOMIC IWASAWA THEORY OF ABELIAN VARIETIES OF GL2 -TYPE | 2023 | `arxiv:2310.06813` | read |
| KN-LIT-1074 | BIPARTITE EULER SYSTEMS FOR CERTAIN GALOIS REPRESENTATIONS | 2023 | `arxiv:2302.05181` | read |
| KN-LIT-1075 | BRAID GROUPS, ELLIPTIC CURVES, AND RESOLVING THE QUARTIC | 2023 | `arxiv:2309.12999` | read |
| KN-LIT-1076 | BRAUER RELATIONS, ISOGENIES AND PARITIES OF RANKS | 2023 | `arxiv:2311.02137` | read |
| KN-LIT-1077 | Breaking Parallel ROS: Implication for Isogeny and Lattice-based Blind Signatures | 2023 | `eprint:2023/1603` | read |
| KN-LIT-1078 | Capybara and Tsubaki: Verifiable Random Functions from Group Actions and Isogenies | 2023 | `eprint:2023/182` | read |
| KN-LIT-1079 | CDLS: Proving Knowledge of Committed Discrete Logarithms with Soundness | 2023 | `eprint:2023/1595` | read |
| KN-LIT-108 | Revisiting the Expected Cost of Solving uSVP and Applications to LWE | 2017 | `eprint:2017/815` | read |
| KN-LIT-1080 | Classical and Quantum Meet-in-the-Middle Nostradamus Attacks on AES-like Hashing | 2023 | `eprint:2023/772` | read |
| KN-LIT-1081 | Composable Long-Term Security with Rewinding Robin Berger1 , Brandon Broadnax2 , Michael Klooß3? , Jeremias Mechler1 | 2023 | `eprint:2023/363` | read |
| KN-LIT-1082 | Compressed M-SIDH: An Instance of Compressed SIDH-like Schemes with Isogenies of Highly Composite Degrees | 2023 | `eprint:2023/136` | read |
| KN-LIT-1083 | Computation of Hilbert class polynomials and modular polynomials from supersingular elliptic curves | 2023 | `arxiv:2301.08531` | read |
| KN-LIT-1084 | Computing Isogenies of Power-Smooth Degrees | 2023 | `eprint:2023/508` | read |
| KN-LIT-1085 | COMPUTING QUADRATIC POINTS ON MODULAR CURVES X0 (N ) | 2023 | `arxiv:2303.12566` | read |
| KN-LIT-1086 | Computing supersingular endomorphism rings using inseparable endomorphisms | 2023 | `arxiv:2306.03051` | read |
| KN-LIT-1087 | COMPUTING THE CHARLAP-COLEY-ROBBINS | 2023 | `arxiv:2302.05217` | read |
| KN-LIT-1088 | Concrete Quantum Cryptanalysis of Binary Elliptic Curves via Addition Chain | 2023 | `eprint:2023/553` | read |
| KN-LIT-1089 | Contemporary Mathematics Computing the endomorphism ring of an elliptic curve over a number field | 2023 | `arxiv:2301.11169` | read |
| KN-LIT-109 | Faster Dual Lattice Attacks for Solving LWE with Applications to CRYSTALS | 2021 | `doi:10.1007/978-3-030-92068-5_2` | web |
| KN-LIT-1090 | COTORSION OF ANTI-CYCLOTOMIC SELMER GROUPS ON AVERAGE | 2023 | `arxiv:2305.10571` | read |
| KN-LIT-1091 | CryptAttackTester: high-assurance attack analysis | 2023 | `eprint:2023/940` | read |
| KN-LIT-1092 | CSI-Otter: Isogeny-based (Partially) Blind Signatures from the Class Group Action with a Twist | 2023 | `eprint:2023/1239` | read |
| KN-LIT-1093 | CURVES WITH FEW BAD PRIMES OVER CYCLOTOMIC Zl -EXTENSIONS | 2023 | `arxiv:2302.02514` | read |
| KN-LIT-1094 | CYCLICITY AND EXPONENT OF ELLIPTIC CURVES MODULO p IN ARITHMETIC PROGRESSIONS | 2023 | `arxiv:2307.05594` | read |
| KN-LIT-1095 | DEEP HOLE LATTICES AND ISOGENIES OF ELLIPTIC CURVES | 2023 | `arxiv:2310.14091` | read |
| KN-LIT-1096 | DENSITY OF SELMER RANKS IN FAMILIES OF EVEN GALOIS | 2023 | `arxiv:2301.09760` | read |
| KN-LIT-1097 | DERIVED p-ADIC HEIGHTS AND THE LEADING COEFFICIENT OF THE BERTOLINI–DARMON–PRASANNA p-ADIC L-FUNCTION | 2023 | `arxiv:2308.10474` | read |
| KN-LIT-1098 | DIAGONAL HYPERSURFACES AND ELLIPTIC CURVES OVER | 2023 | `arxiv:2307.11982` | read |
| KN-LIT-1099 | DIOPHANTINE STABILITY FOR ELLIPTIC CURVES ON AVERAGE | 2023 | `arxiv:2304.09742` | read |
| KN-LIT-110 | Report on the Security of LWE: Improved Dual Lattice Attack | 2022 | `doi:10.5281/zenodo.6412487` | read |
| KN-LIT-1100 | DIVISIBILITY OF ORDERS OF REDUCTIONS OF ELLIPTIC CURVES | 2023 | `arxiv:2301.00711` | read |
| KN-LIT-1101 | Divisibility sequences related to abelian varieties isogenous to a power of an elliptic curve | 2023 | `arxiv:2309.09699` | read |
| KN-LIT-1102 | Dynamics of Endomorphisms for Projective Bundles on Elliptic Curves | 2023 | `arxiv:2310.03313` | read |
| KN-LIT-1103 | Effective Pairings in Isogeny-based Cryptography | 2023 | `eprint:2023/858` | read |
| KN-LIT-1104 | Efficient Computation of (3n , 3n )-Isogenies | 2023 | `eprint:2023/376` | read |
| KN-LIT-1105 | Exploring Multi-Task Learning in the Context of Masked AES Implementations | 2023 | `eprint:2023/006` | read |
| KN-LIT-1106 | FAMILIES OF ISOGENOUS ELLIPTIC CURVES ORDERED BY HEIGHT | 2023 | `arxiv:2308.11122` | read |
| KN-LIT-1107 | Fast and Frobenius: Rational Isogeny Evaluation over Finite Fields | 2023 | `arxiv:2306.16072` | read |
| KN-LIT-1108 | FINDING ORIENTATIONS OF SUPERSINGULAR ELLIPTIC | 2023 | `arxiv:2308.11539` | read |
| KN-LIT-1109 | FROBENIUS SIGN SEPARATION FOR ABELIAN VARIETIES | 2023 | `arxiv:2310.10568` | read |
| KN-LIT-111 | Does the Dual-Sieve Attack on Learning with Errors even Work? | 2023 | `eprint:2023/302` | read |
| KN-LIT-1110 | GEOMETRIC ENDOMORPHISMS OF THE HESSE MODULI SPACE OF ELLIPTIC CURVES | 2023 | `arxiv:2309.00113` | read |
| KN-LIT-1111 | GROWTH OF TORSION GROUPS OF ELLIPTIC CURVES OVER NUMBER FIELDS WITHOUT RATIONALLY DEFINED CM | 2023 | `arxiv:2308.01683` | read |
| KN-LIT-1112 | HILBERT’S TENTH PROBLEM IN ANTICYCLOTOMIC TOWERS OF NUMBER FIELDS | 2023 | `arxiv:2302.04157` | read |
| KN-LIT-1113 | HYPERELLIPTIC CURVES MAPPING TO ABELIAN VARIETIES AND APPLICATIONS TO BEILINSON’S CONJECTURE FOR ZERO-CYCLES | 2023 | `arxiv:2309.06361` | read |
| KN-LIT-1114 | Hyperelliptic genus 3 curves with involutions and a Prym map | 2023 | `arxiv:2308.07038` | read |
| KN-LIT-1115 | Hypergeometry and the AGM over Finite Fields | 2023 | `arxiv:2302.10387` | read |
| KN-LIT-1116 | IDEAL CLASS GROUPS OF DIVISION FIELDS OF ELLIPTIC | 2023 | `arxiv:2304.05035` | read |
| KN-LIT-1117 | Improved algorithms for finding fixed-degree isogenies between supersingular elliptic curves Benjamin Benčina1 | 2023 | `eprint:2023/1618` | read |
| KN-LIT-1118 | Improved Quantum Circuits for AES: Reducing the Depth and the Number of Qubits | 2023 | `eprint:2023/1417` | read |
| KN-LIT-1119 | IRREDUCIBILITY CRITERIA FOR THE PREIMAGES OF A TRANSVERSE VARIETY UNDER ENDOMORPHISMS OF PRODUCTS OF ELLIPTIC CURVES | 2023 | `arxiv:2310.20665` | read |
| KN-LIT-112 | A subfield lattice attack on overstretched NTRU assumptions: Cryptanalysis of some FHE and Graded Encoding Schemes | 2016 | `eprint:2016/127` | read |
| KN-LIT-1120 | IS-CUBE: An isogeny-based compact KEM using a boxed SIDH diagram | 2023 | `eprint:2023/1506` | read |
| KN-LIT-1121 | Iterative constructions of irreducible polynomials from isogenies | 2023 | `arxiv:2302.09674` | read |
| KN-LIT-1122 | Iwasawa theory and mock plectic points | 2023 | `arxiv:2311.03100` | read |
| KN-LIT-1123 | Lightweight Public Key Encryption in Post-Quantum Computing Era | 2023 | `arxiv:2311.14845` | read |
| KN-LIT-1124 | LOCALLY IMPRIMITIVE POINTS ON ELLIPTIC CURVES | 2023 | `arxiv:2304.03964` | read |
| KN-LIT-1125 | Low Memory Attacks on Small Key CSIDH Jesús-Javier Chi-Domínguez1 | 2023 | `eprint:2023/507` | read |
| KN-LIT-1126 | MAHLER MEASURE OF A NONRECIPROCAL FAMILY OF ELLIPTIC CURVES | 2023 | `arxiv:2301.05390` | read |
| KN-LIT-1127 | MAZUR’S MAIN CONJECTURE AT EISENSTEIN PRIMES | 2023 | `arxiv:2303.04373` | read |
| KN-LIT-1128 | Minimizing CNOT-count in quantum circuit of the extended Shor’s algorithm for ECDLP | 2023 | `arxiv:2305.11410` | read |
| KN-LIT-1129 | Modular algorithms for Gross–Stark units and Stark–Heegner points arXiv:2301.08977v1 [math.NT] 21 Jan 2023 Håvard Damm-Johnsen | 2023 | `arxiv:2301.08977` | read |
| KN-LIT-113 | Revisiting Lattice Attacks on Overstretched NTRU Parameters | 2017 | `doi:10.1007/978-3-319-56620-7_1` | web |
| KN-LIT-1130 | Mordell-Weil groups as Galois modules | 2023 | `arxiv:2306.13365` | read |
| KN-LIT-1131 | MULTIPLICATION POLYNOMIALS FOR ELLIPTIC CURVES OVER FINITE LOCAL RINGS | 2023 | `arxiv:2302.03650` | read |
| KN-LIT-1132 | NEIGHBORHOOD OF VERTICES IN THE ISOGENY GRAPH OF PRINCIPALLY POLARIZED SUPERSPECIAL ABELIAN SURFACES | 2023 | `arxiv:2309.14963` | read |
| KN-LIT-1133 | New record in the number of qubits for a quantum implementation of AES | 2023 | `eprint:2023/018` | read |
| KN-LIT-1134 | New Space-Efficient Quantum Algorithm for Binary Elliptic Curves using the Optimized Division Algorithm | 2023 | `arxiv:2303.06570` | read |
| KN-LIT-1135 | NON-VANISHING OF CENTRAL L-VALUES OF THE GROSS FAMILY OF ELLIPTIC CURVES | 2023 | `arxiv:2305.08689` | read |
| KN-LIT-1136 | NON-VANISHING OF KOLYVAGIN SYSTEMS AND IWASAWA THEORY | 2023 | `arxiv:2312.09301` | read |
| KN-LIT-1137 | Not Just Regular Decoding: Asymptotics and Improvements of Regular Syndrome Decoding Attacks | 2023 | `eprint:2023/1568` | read |
| KN-LIT-1138 | On CM Elliptic Curves and the Cyclotomic λ-Invariants of | 2023 | `arxiv:2302.09594` | read |
| KN-LIT-1139 | On correlation distribution of Niho-type decimation d = 3(pm − 1) + | 2023 | `arxiv:2309.06715` | read |
| KN-LIT-114 | NTRU Fatigue: How Stretched is Overstretched? | 2021 | `eprint:2021/999` | read |
| KN-LIT-1140 | ON DARMON’S PROGRAM | 2023 | `arxiv:2308.07062` | read |
| KN-LIT-1141 | On fine Mordell-Weil groups over Zp-extensions of an imaginary arXiv:2308.04096v3 [math.NT] 21 Sep 2024 quadratic field | 2023 | `arxiv:2308.04096` | read |
| KN-LIT-1142 | On Galois self-orthogonal algebraic geometry codes | 2023 | `arxiv:2309.01051` | read |
| KN-LIT-1143 | ON ORDINARY ISOGENY GRAPHS WITH LEVEL STRUCTURES | 2023 | `arxiv:2306.10981` | read |
| KN-LIT-1144 | ON POSSIBILITIES OF 3-ADIC GALOIS IMAGES ASSOCIATED TO ISOGENY-TORSION GRAPHS arXiv:2307.04074v2 [math.NT] 7 Aug 2025 RAKVI | 2023 | `arxiv:2307.04074` | read |
| KN-LIT-1145 | ON r-ISOGENIES OVER Q(ζr ) | 2023 | `arxiv:2307.14131` | read |
| KN-LIT-1146 | ON THE KERNELS OF THE PRO-p OUTER GALOIS REPRESENTATIONS ASSOCIATED TO ONCE-PUNCTURED CM ELLIPTIC CURVES | 2023 | `arxiv:2312.04196` | read |
| KN-LIT-1147 | ON THE SIGNED SELMER GROUPS FOR MOTIVES AT NON-ORDINARY PRIMES IN Z2p -EXTENSIONS | 2023 | `arxiv:2309.02016` | read |
| KN-LIT-1148 | ON THE ZETA FUNCTIONS OF SUPERSINGULAR | 2023 | `arxiv:2307.01001` | read |
| KN-LIT-1149 | ON TOWERS OF ISOGENY GRAPHS WITH FULL LEVEL STRUCTURES | 2023 | `arxiv:2309.00524` | read |
| KN-LIT-115 | Recovering Short Generators of Principal Ideals in Cyclotomic Rings | 2016 | `eprint:2015/313` | read |
| KN-LIT-1150 | Optimizing AES Threshold Implementation under the Glitch-Extended Probing Model | 2023 | `eprint:2023/1856` | read |
| KN-LIT-1151 | Oriented Supersingular Elliptic Curves and Eichler Orders of Prime Level | 2023 | `arxiv:2312.08844` | read |
| KN-LIT-1152 | p-ADIC HYPERGEOMETRIC FUNCTIONS AND THE TRACE OF FROBENIUS OF ELLIPTIC CURVES | 2023 | `arxiv:2311.03259` | read |
| KN-LIT-1153 | p-adic Waldspurger Formula for Non-split Primes and Converse of Gross–Zagier and Kolyvagin Theorem | 2023 | `arxiv:2304.09806` | read |
| KN-LIT-1154 | Partial Sums Meet FFT: Improved Attack on 6-Round | 2023 | `eprint:2023/1659` | read |
| KN-LIT-1155 | PERFECT POWERS IN ELLIPTIC DIVISIBILITY SEQUENCES | 2023 | `arxiv:2312.08997` | read |
| KN-LIT-1156 | Quantum Circuit Designs of Point Doubling Operation for Binary Elliptic Curves | 2023 | `eprint:2023/1140` | read |
| KN-LIT-1157 | RATIONAL TORSION POINTS ON ABELIAN SURFACES WITH QUATERNIONIC MULTIPLICATION | 2023 | `arxiv:2308.15193` | read |
| KN-LIT-1158 | Reading between the rational sections: Global structures of 4d N = 2 KK theories | 2023 | `arxiv:2308.10225` | read |
| KN-LIT-1159 | Ready to SQI? Safety first! Towards a constant-time implementation of isogeny-based signature SQIsign | 2023 | `eprint:2023/807` | read |
| KN-LIT-116 | Short Stickelberger Class Relations and application to Ideal-SVP | 2017 | `eprint:2016/885` | read |
| KN-LIT-1160 | REDUCED MINIMAL MODELS AND TORSION | 2023 | `arxiv:2301.09488` | read |
| KN-LIT-1161 | REDUCTION AND ISOGENIES OF ELLIPTIC CURVES | 2023 | `arxiv:2310.15914` | read |
| KN-LIT-1162 | REFINEMENTS ON VERTICAL SATO-TATE | 2023 | `arxiv:2310.08791` | read |
| KN-LIT-1163 | REMARKS ON GREENBERG’S CONJECTURE FOR GALOIS REPRESENTATIONS ASSOCIATED TO ELLIPTIC CURVES | 2023 | `arxiv:2308.06673` | read |
| KN-LIT-1164 | Revocable Cryptography from Learning with Errors | 2023 | `eprint:2023/325` | read |
| KN-LIT-1165 | RINGS WHERE A NON-NILPOTENT SUM OF UNITS IS A UNIT | 2023 | `arxiv:2307.11036` | read |
| KN-LIT-1166 | SATO–TATE TYPE DISTRIBUTIONS FOR MATRIX POINTS ON ELLIPTIC | 2023 | `arxiv:2308.02683` | read |
| KN-LIT-1167 | SCALLOP-HD: group action from 2-dimensional isogenies | 2023 | `eprint:2023/1488` | read |
| KN-LIT-1168 | Searching for ELFs in the Cryptographic Forest | 2023 | `eprint:2023/140` | read |
| KN-LIT-1169 | Security Impact Analysis of Degree of Field Extension in Lattice Attacks on Ring-LWE Problem 1st Yuri Lucas Direbieski 2nd Hiroki Tanioka | 2023 | `arxiv:2305.15772` | read |
| KN-LIT-117 | Efficient quantum algorithms for computing class groups and solving the principal ideal problem in arbitrary degree number fields | 2016 | `doi:10.1137/1.9781611974331.ch64` | read |
| KN-LIT-1170 | Simple Two-Round OT in the Explicit Isogeny Model | 2023 | `eprint:2023/269` | read |
| KN-LIT-1171 | Spectral theory of isogeny graphs | 2023 | `arxiv:2308.13913` | read |
| KN-LIT-1172 | Splitting of almost ordinary abelian surfaces in families and the S-integrality conjectures | 2023 | `arxiv:2304.07715` | read |
| KN-LIT-1173 | THE ANTICYCLOTOMIC MAIN CONJECTURES FOR ELLIPTIC CURVES | 2023 | `arxiv:2306.17784` | read |
| KN-LIT-1174 | The c-differential properties of a class of power functions | 2023 | `arxiv:2311.00982` | read |
| KN-LIT-1175 | THE COUNTING FUNCTION FOR ELKIES PRIMES | 2023 | `arxiv:2311.17231` | read |
| KN-LIT-1176 | THE FIELD OF MODULI OF PLANE CURVES | 2023 | `arxiv:2303.01454` | read |
| KN-LIT-1177 | The International Journal Of Engineering And Science (IJES) \|\| Volume \|\| 4 \|\| Issue \|\| 4 \|\| Pages \|\| PP.45-50 \|\| 2015 \|\| ISSN (e): 2319 – 1813 ISSN (p): 2319 – 1805 | 2023 | `arxiv:2311.11392` | read |
| KN-LIT-1178 | THE PROBABILITY OF NON-ISOMORPHIC GROUP STRUCTURES OF | 2023 | `arxiv:2301.09176` | read |
| KN-LIT-1179 | The supersingular endomorphism ring problem given one endomorphism | 2023 | `arxiv:2309.11912` | read |
| KN-LIT-118 | LWE with Side Information: Attacks and Concrete Security Estimation | 2020 | `eprint:2020/292` | read |
| KN-LIT-1180 | TORSION AND TWISTS OF ABELIAN VARIETIES | 2023 | `arxiv:2310.11086` | read |
| KN-LIT-1181 | TORSION PRIMES FOR ELLIPTIC CURVES OVER DEGREE | 2023 | `arxiv:2304.14284` | read |
| KN-LIT-1182 | TOWARDS STRONG UNIFORMITY FOR ISOGENIES OF PRIME DEGREE | 2023 | `arxiv:2302.08350` | read |
| KN-LIT-1183 | Two Remarks on Torsion-Point Attacks in Isogeny-Based Cryptography | 2023 | `eprint:2023/1229` | read |
| KN-LIT-1184 | UNIFORM BOUNDS FOR THE NUMBER OF RATIONAL POINTS OF BOUNDED HEIGHT ON CERTAIN ELLIPTIC CURVES | 2023 | `arxiv:2312.03655` | read |
| KN-LIT-1185 | Unique-Path Identity Based Encryption With Applications to Strongly Secure Messaging | 2023 | `eprint:2023/248` | read |
| KN-LIT-1186 | USING THE CHARLAP-COLEY-ROBBINS POLYNOMIALS FOR COMPUTING ISOGENIES FRANÇOIS MORAIN | 2023 | `arxiv:2303.00346` | read |
| KN-LIT-1187 | A COMPREHENSIVE ANALYSIS OF REGEV’S QUANTUM ALGORITHM | 2024 | `eprint:2024/1758` | read |
| KN-LIT-1188 | A Concrete Analysis of Wagner’s k-List Algorithm over Zp | 2024 | `eprint:2024/282` | read |
| KN-LIT-1189 | A GRAPH-THEORETIC APPROACH TO COMPUTING SELMER | 2024 | `arxiv:2410.22714` | read |
| KN-LIT-119 | On the impact of decryption failures on the security of LWE/LWR based schemes | 2019 | `eprint:2018/1089` | read |
| KN-LIT-1190 | A HEURISTIC APPROACH TO THE IWASAWA THEORY OF ELLIPTIC CURVES | 2024 | `arxiv:2409.15056` | read |
| KN-LIT-1191 | A new family of binary sequences with a low correlation via elliptic curves | 2024 | `arxiv:2407.18570` | read |
| KN-LIT-1192 | A NOTE ON THE GROWTH OF SHA IN DIHEDRAL EXTENSIONS | 2024 | `arxiv:2411.15663` | read |
| KN-LIT-1193 | A Note on “ Provably Secure and Lightweight Authentication Key Agreement Scheme for Smart Meters” | 2024 | `eprint:2024/1158` | read |
| KN-LIT-1194 | A note on “a novel authentication protocol for IoT-enabled devices” | 2024 | `eprint:2024/1191` | read |
| KN-LIT-1195 | AGM AQUARIUMS AND ELLIPTIC CURVES OVER ARBITRARY FINITE FIELDS | 2024 | `arxiv:2410.17969` | read |
| KN-LIT-1196 | Alternative Key Schedules for the AES | 2024 | `eprint:2024/315` | read |
| KN-LIT-1197 | AN ANALOGUE OF KIDA’S FORMULA FOR ELLIPTIC CURVES WITH ADDITIVE REDUCTION | 2024 | `arxiv:2402.02024` | read |
| KN-LIT-1198 | AN ARITHMETIC INTERSECTION FOR SQUARES OF ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2024 | `arxiv:2412.08738` | read |
| KN-LIT-1199 | An efficient collision attack on Castryck-Decru-Smith’s hash function | 2024 | `eprint:2024/1776` | read |
| KN-LIT-120 | Explicit hard instances of the shortest vector problem | 2008 | `eprint:2008/333` | read |
| KN-LIT-1200 | AN ELEMENTARY APPROACH TO THE GROUP LAW ON ELLIPTIC CURVES | 2024 | `arxiv:2401.02346` | read |
| KN-LIT-1201 | Approximation and bounding techniques for the Fisher-Rao distances between parametric statistical models | 2024 | `arxiv:2403.10089` | read |
| KN-LIT-1202 | BASE CHANGE AND IWASAWA MAIN CONJECTURES FOR GL2 | 2024 | `arxiv:2405.00270` | read |
| KN-LIT-1203 | BEHAVIORS OF THE TATE–SHAFAREVICH GROUP OF ELLIPTIC | 2024 | `arxiv:2411.12316` | read |
| KN-LIT-1204 | BISON: Blind Identification with Stateless scOped pseudoNyms | 2024 | `arxiv:2406.01518` | read |
| KN-LIT-1205 | Bitsliced Jasmin Implementation of the Mayo Signature Scheme | 2024 | `eprint:2024/1893` | read |
| KN-LIT-1206 | Bounds on Heights of 2-isogeny | 2024 | `arxiv:2409.00505` | read |
| KN-LIT-1207 | Breaking the IEEE Encryption Standard – XCB-AES in Two Queries | 2024 | `eprint:2024/1554` | read |
| KN-LIT-1208 | Bundle-extension inverse problems over elliptic curves | 2024 | `arxiv:2407.07344` | read |
| KN-LIT-1209 | Chosen-Prefix Collisions on AES-like Hashing | 2024 | `eprint:2024/1888` | read |
| KN-LIT-121 | Creating Cryptographic Challenges Using Multi-Party Computation: The LWE Challenge | 2016 | `eprint:2017/606` | read |
| KN-LIT-1210 | CLIMBING AND DESCENDING TALL ISOGENY VOLCANOS | 2024 | `eprint:2024/924` | read |
| KN-LIT-1211 | COINCIDENCES OF DIVISION FIELDS OF AN ELLIPTIC CURVE DEFINED OVER A NUMBER FIELD | 2024 | `arxiv:2407.14370` | read |
| KN-LIT-1212 | COMPUTING 2-ISOGENIES BETWEEN KUMMER LINES | 2024 | `eprint:2024/037` | read |
| KN-LIT-1213 | COMPUTING ISOGENIES AT SINGULAR POINTS OF THE MODULAR POLYNOMIAL | 2024 | `arxiv:2402.02038` | read |
| KN-LIT-1214 | CONNECTING KANI’S LEMMA AND PATH-FINDING IN THE BRUHAT-TITS TREE TO COMPUTE SUPERSINGULAR | 2024 | `arxiv:2402.05059` | read |
| KN-LIT-1215 | COUNTING ELLIPTIC CURVES WITH A CYCLIC m-ISOGENY OVER Q | 2024 | `arxiv:2401.06815` | read |
| KN-LIT-1216 | d-ELLIPTIC LOCI AND THE TORELLI MAP | 2024 | `arxiv:2404.10826` | read |
| KN-LIT-1217 | DEGREES OF ISOGENIES OVER PRIME DEGREE NUMBER FIELDS OF NON-CM ELLIPTIC CURVES WITH RATIONAL j-INVARIANT | 2024 | `arxiv:2411.03062` | read |
| KN-LIT-1218 | DESCENT FOR PROJECTIVE TWISTS OF MODULAR CURVES FRANCISZEK KNYSZEWSKI | 2024 | `arxiv:2402.17636` | read |
| KN-LIT-1219 | DISTRIBUTION OF CYCLES IN SUPERSINGULAR l-ISOGENY GRAPHS | 2024 | `eprint:2024/509` | read |
| KN-LIT-122 | Estimating quantum speedups for lattice sieves | 2020 | `eprint:2019/1161` | read |
| KN-LIT-1220 | Diving Deep into the Preimage Security of AES-like Hashing | 2024 | `eprint:2024/300` | read |
| KN-LIT-1221 | DL-SITM: Deep Learning-Based See-in-the-Middle Attack on AES Tomáš | 2024 | `eprint:2024/1389` | read |
| KN-LIT-1222 | ECPM Cryptanalysis Resource Estimation Dedy Septono Catur Putranto1,2[0000−0002−1246−7877] , Rini Wisnu Wardhani3[0000−0003−0565−6458] | 2024 | `eprint:2024/1767` | read |
| KN-LIT-1223 | EFFICIENT (3, 3)-ISOGENIES ON FAST KUMMER SURFACES | 2024 | `eprint:2024/144` | read |
| KN-LIT-1224 | Efficient theta-based algorithms for computing (l, l)-isogenies on Kummer surfaces for arbitrary odd l | 2024 | `eprint:2024/1519` | read |
| KN-LIT-1225 | Elliptic curves and the residue-counts of x2 + bx + c/x modulo p | 2024 | `arxiv:2407.15432` | read |
| KN-LIT-1226 | Elliptic Curves in Continuous-Variable Quantum Systems | 2024 | `arxiv:2401.11579` | read |
| KN-LIT-1227 | ELLIPTIC CURVES OF CONDUCTOR 2m p, QUADRATIC TWISTS, AND WATKINS’ CONJECTURE | 2024 | `arxiv:2411.08321` | read |
| KN-LIT-1228 | ELLIPTIC CURVES OVER HASSE PAIRS | 2024 | `arxiv:2406.03399` | read |
| KN-LIT-1229 | Endomorphism Rings of Supersingular Elliptic | 2024 | `arxiv:2409.11025` | read |
| KN-LIT-123 | Lattice Attacks on NTRU and LWE: A History of Refinements | 2021 | `eprint:2021/799` | read |
| KN-LIT-1230 | ENTANGLEMENT OF ELLIPTIC CURVES UPON BASE EXTENSION | 2024 | `arxiv:2403.03073` | read |
| KN-LIT-1231 | Erebor and Durian: Full Anonymous Ring Signatures from Quaternions and Isogenies | 2024 | `eprint:2024/1185` | read |
| KN-LIT-1232 | EUCLEAK Side-Channel Attack on the YubiKey 5 Series (Revealing and Breaking Infineon ECDSA Implementation on the Way) | 2024 | `eprint:2024/1380` | read |
| KN-LIT-1233 | EXCEPTIONAL ZEROS FOR HEEGNER POINTS AND p-CONVERSE TO | 2024 | `arxiv:2409.01360` | read |
| KN-LIT-1234 | EXPONENTIAL SUMS OVER SINGULAR BINARY QUARTIC FORMS AND APPLICATIONS | 2024 | `arxiv:2404.00541` | read |
| KN-LIT-1235 | Extending class group action attacks via sesquilinear pairings | 2024 | `arxiv:2406.10440` | read |
| KN-LIT-1236 | FAST COMPUTATION OF 2-ISOGENIES IN DIMENSION 4 AND CRYPTOGRAPHIC APPLICATIONS | 2024 | `arxiv:2407.15492` | read |
| KN-LIT-1237 | Faster algorithms for isogeny computations over extensions of finite fields | 2024 | `eprint:2024/1852` | read |
| KN-LIT-1238 | Finding Practical Parameters for Isogeny-based Cryptography | 2024 | `eprint:2024/1150` | read |
| KN-LIT-1239 | General Practical Cryptanalysis of the Sum of | 2024 | `eprint:2024/2033` | read |
| KN-LIT-124 | On the Cost of Computing Isogenies Between Supersingular Elliptic Curves | 2018 | `eprint:2018/313` | web |
| KN-LIT-1240 | GENERALIZED TWISTED EDWARDS CURVES OVER FINITE | 2024 | `arxiv:2412.06199` | read |
| KN-LIT-1241 | Global Galois Symbols on E × E | 2024 | `arxiv:2407.20468` | read |
| KN-LIT-1242 | HEAVENLY ELLIPTIC CURVES OVER QUADRATIC FIELDS | 2024 | `arxiv:2410.18389` | read |
| KN-LIT-1243 | Heegner point constructions and fundamental units in cubic fields | 2024 | `arxiv:2407.12834` | read |
| KN-LIT-1244 | HILBERT’S 10th PROBLEM VIA MORDELL CURVES | 2024 | `arxiv:2412.04253` | read |
| KN-LIT-1245 | HILBERT’S TENTH PROBLEM FOR FAMILIES OF Zp -EXTENSIONS OF IMAGINARY QUADRATIC FIELDS | 2024 | `arxiv:2406.01443` | read |
| KN-LIT-1246 | Hilbert’s tenth problem via additive combinatorics | 2024 | `arxiv:2412.01768` | read |
| KN-LIT-1247 | HYPERTRANSCENDENCE AND q-DIFFERENCE EQUATIONS OVER ELLIPTIC FUNCTION FIELDS | 2024 | `arxiv:2409.10092` | read |
| KN-LIT-1248 | Ideal-to-isogeny algorithm using 2-dimensional | 2024 | `eprint:2024/778` | read |
| KN-LIT-1249 | IMAGINARY QUADRATIC FIELDS F WITH X0 (15)(F ) FINITE | 2024 | `arxiv:2405.09337` | read |
| KN-LIT-125 | Improved Classical Cryptanalysis of SIKE in Practice | 2020 | `eprint:2019/298` | web |
| KN-LIT-1250 | Improved Boomerang Attacks on 6-Round AES | 2024 | `eprint:2024/977` | read |
| KN-LIT-1251 | Isogeny problems with level structure | 2024 | `eprint:2024/459` | read |
| KN-LIT-1252 | ISOGENY RELATIONS IN PRODUCTS OF FAMILIES OF ELLIPTIC CURVES | 2024 | `arxiv:2409.01408` | read |
| KN-LIT-1253 | ISOTRIVIAL ELLIPTIC SURFACES IN POSITIVE CHARACTERISTIC | 2024 | `arxiv:2405.11602` | read |
| KN-LIT-1254 | Key Collisions on AES and Its Applications | 2024 | `eprint:2024/1508` | read |
| KN-LIT-1255 | Key Policy Attribute-Based Encryption Leveraging Isogeny-Based Cryptography | 2024 | `eprint:2024/1392` | read |
| KN-LIT-1256 | Key Recovery Attack on the Partial Vandermonde Knapsack Problem | 2024 | `eprint:2024/366` | read |
| KN-LIT-1257 | KLaPoTi: An asymptotically efficient isogeny group action from 2-dimensional isogenies | 2024 | `eprint:2024/1844` | read |
| KN-LIT-1258 | Lattice-based Fault Attacks against ECMQV | 2024 | `eprint:2024/882` | read |
| KN-LIT-1259 | LeOPaRd: Towards Practical Post-Quantum Oblivious PRFs via 2HashDH Paradigm | 2024 | `eprint:2024/1615` | read |
| KN-LIT-126 | Quantum Cryptanalysis in the RAM Model: Claw-Finding Attacks on SIKE | 2019 | `eprint:2019/103` | web |
| KN-LIT-1260 | LIT-SiGamal: An efficient isogeny-based PKE based on a LIT diagram | 2024 | `eprint:2024/521` | read |
| KN-LIT-1261 | MACHINE LEARNING APPROACHES TO THE SHAFAREVICH-TATE GROUP OF ELLIPTIC CURVES | 2024 | `arxiv:2412.18576` | read |
| KN-LIT-1262 | MINIMAL SUBGROUPS OF GL2 (ZS ) | 2024 | `arxiv:2402.11049` | read |
| KN-LIT-1263 | MINIMAL TORSION CURVES IN GEOMETRIC ISOGENY CLASSES | 2024 | `arxiv:2407.14322` | read |
| KN-LIT-1264 | ModSRAM: Algorithm-Hardware Co-Design for Large Number | 2024 | `arxiv:2402.14152` | read |
| KN-LIT-1265 | NEW ISOGENIES OF ELLIPTIC CURVES OVER NUMBER FIELDS | 2024 | `arxiv:2405.05507` | read |
| KN-LIT-1266 | NON-COMMUTATIVE IWASAWA THEORY OF ABELIAN VARIETIES OVER GLOBAL FUNCTION FIELDS | 2024 | `arxiv:2405.20963` | read |
| KN-LIT-1267 | ODD AND EVEN ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2024 | `arxiv:2406.07240` | read |
| KN-LIT-1268 | ON A CONJECTURE OF MAZUR PREDICTING THE GROWTH OF MORDELL–WEIL RANKS IN Zp -EXTENSIONS | 2024 | `arxiv:2401.07792` | read |
| KN-LIT-1269 | ON DIHEDRAL GROUP ACTIONS ON RIEMANN SURFACES | 2024 | `arxiv:2409.07294` | read |
| KN-LIT-127 | He Gives C-Sieves on the CSIDH | 2020 | `eprint:2019/725` | web |
| KN-LIT-1270 | ON p-ADIC L-FUNCTIONS OF ELLIPTIC CURVES AND THE IDEAL CLASS GROUPS OF THE DIVISION FIELDS | 2024 | `arxiv:2405.19142` | read |
| KN-LIT-1271 | On pseudo-nullity of fine Mordell-Weil group | 2024 | `arxiv:2409.03546` | read |
| KN-LIT-1272 | ON THE ANTICYCLOTOMIC IWASAWA THEORY OF NEWFORMS AT EISENSTEIN PRIMES OF SEMISTABLE REDUCTION | 2024 | `arxiv:2402.12781` | read |
| KN-LIT-1273 | ON THE COHOMOLOGY OF PLUS/MINUS SELMER GROUPS OF SUPERSINGULAR ELLIPTIC CURVES IN WEAKLY RAMIFIED BASE FIELDS | 2024 | `arxiv:2407.08430` | read |
| KN-LIT-1274 | On the Feasibility of Sliced Garbling | 2024 | `eprint:2024/389` | read |
| KN-LIT-1275 | ON THE IWASAWA INVARIANTS OF MAZUR–TATE ELEMENTS OF ELLIPTIC CURVES AT ADDITIVE PRIMES | 2024 | `arxiv:2412.16629` | read |
| KN-LIT-1276 | ON THE KODAIRA TYPES OF ELLIPTIC CURVES WITH POTENTIALLY | 2024 | `arxiv:2406.01985` | read |
| KN-LIT-1277 | On the rough order assumption in imaginary quadratic number fields | 2024 | `eprint:2024/1520` | read |
| KN-LIT-1278 | ON THE STRUCTURE OF THE BLOCH–KATO SELMER GROUPS OF MODULAR FORMS OVER ANTICYCLOTOMIC Zp -TOWERS | 2024 | `arxiv:2409.11966` | read |
| KN-LIT-1279 | On the Untapped Potential of the Quantum FLT-based Inversion | 2024 | `eprint:2024/228` | read |
| KN-LIT-128 | Quantum Security Analysis of CSIDH | 2020 | `eprint:2018/537` | web |
| KN-LIT-1280 | On Wagner’s k-Tree Algorithm Over Integers | 2024 | `eprint:2024/1612` | read |
| KN-LIT-1281 | On l-th roots and division by l | 2024 | `arxiv:2403.06619` | read |
| KN-LIT-1282 | ORDINARY ISOGENY GRAPHS WITH LEVEL STRUCTURE | 2024 | `arxiv:2411.02732` | read |
| KN-LIT-1283 | p-CONVERSE THEOREMS FOR ELLIPTIC CURVES OF POTENTIALLY GOOD ORDINARY REDUCTION AT EISENSTEIN PRIMES | 2024 | `arxiv:2410.23241` | read |
| KN-LIT-1284 | Practical Investigation on the Distinguishability of Longa’s Atomic Patterns | 2024 | `arxiv:2409.11868` | read |
| KN-LIT-1285 | Practical Non-interactive Multi-signatures, and a Multi-to-Aggregate Signatures Compiler | 2024 | `eprint:2024/1081` | read |
| KN-LIT-1286 | PRIME ISOGENOUS DISCRIMINANT IDEAL TWINS | 2024 | `arxiv:2402.19183` | read |
| KN-LIT-1287 | PRINCIPAL POLARIZATIONS ON PRODUCTS OF ABELIAN VARIETIES OVER FINITE FIELDS | 2024 | `arxiv:2404.00652` | read |
| KN-LIT-1288 | Quantitative upper bounds related to an isogeny criterion for elliptic curves | 2024 | `arxiv:2404.12466` | read |
| KN-LIT-1289 | Quantum Circuits of AES with a Low-depth | 2024 | `eprint:2024/381` | read |
| KN-LIT-129 | The SQALE of CSIDH: Sublinear Velu Quantum-resistant isogeny Action with Low Exponents | 2022 | `eprint:2020/1520` | web |
| KN-LIT-1290 | R-STELLAR: A Resilient Synthesizable Signature Attenuation SCA Protection on AES-256 with built-in Attack-on-Countermeasure Detection | 2024 | `eprint:2024/1309` | read |
| KN-LIT-1291 | Radical √ N élu Isogeny Formulae | 2024 | `eprint:2024/878` | read |
| KN-LIT-1292 | RANK DISTRIBUTION IN CUBIC TWIST FAMILIES OF ELLIPTIC CURVES | 2024 | `arxiv:2403.18034` | read |
| KN-LIT-1293 | RANK GROWTH OF ABELIAN VARIETIES OVER CERTAIN FINITE GALOIS EXTENSIONS | 2024 | `arxiv:2410.16867` | read |
| KN-LIT-1294 | Reality Check on Side-Channels: Lessons learnt from breaking AES on ARM Cortex-A72 processor with Out-of-Order Execution | 2024 | `eprint:2024/1381` | read |
| KN-LIT-1295 | Reducing Overdefined Systems of Polynomial Equations Derived from Small Scale Variants of the AES via Data Mining Methods | 2024 | `eprint:2024/809` | read |
| KN-LIT-1296 | REFINED CONJECTURES ON FITTING IDEALS OF SELMER GROUPS OVER Z2p -EXTENSIONS CÉDRIC DION | 2024 | `arxiv:2405.15076` | read |
| KN-LIT-1297 | Revisiting Differential-Linear Attacks via a Boomerang Perspective With Application to AES, Ascon, CLEFIA, SKINNY, PRESENT, KNOT, TWINE, WARP, LBlock, Simeck, and | 2024 | `eprint:2024/255` | read |
| KN-LIT-1298 | SHADOW LINE DISTRIBUTIONS | 2024 | `arxiv:2409.00891` | read |
| KN-LIT-1299 | SIGNITC: Supersingular Isogeny Graph | 2024 | `eprint:2024/1225` | read |
| KN-LIT-130 | Orientations and the Supersingular Endomorphism Ring Problem | 2022 | `eprint:2021/1583` | web |
| KN-LIT-1300 | SOLUTION OF CERTAIN DIOPHANTINE EQUATIONS IN GAUSSIAN INTEGERS | 2024 | `arxiv:2409.20416` | read |
| KN-LIT-1301 | Solving AES-SAT Using Side-Channel Hints: A Practical Assessment | 2024 | `eprint:2024/2079` | read |
| KN-LIT-1302 | Solving McEliece-1409 in One Day — Cryptanalysis with the | 2024 | `eprint:2024/393` | read |
| KN-LIT-1303 | SQIAsignHD: SQIsignHD Adaptor Signature | 2024 | `arxiv:2404.09026` | read |
| KN-LIT-1304 | SQIPrime: A dimension 2 variant of SQISignHD with non-smooth challenge isogenies | 2024 | `eprint:2024/773` | read |
| KN-LIT-1305 | SQIsign2D-East: A New Signature Scheme Using 2-dimensional Isogenies | 2024 | `eprint:2024/771` | read |
| KN-LIT-1306 | STATISTICS FOR 3-ISOGENY INDUCED SELMER GROUPS OF ELLIPTIC CURVES | 2024 | `arxiv:2406.03066` | read |
| KN-LIT-1307 | SUPERSINGULAR ELLIPTIC CURVES, QUATERNION ALGEBRAS AND APPLICATIONS TO CRYPTOGRAPHY | 2024 | `arxiv:2410.06123` | read |
| KN-LIT-1308 | TAMAGAWA NUMBER CONJECTURE FOR CM MODULAR FORMS AND RANKIN–SELBERG CONVOLUTIONS | 2024 | `arxiv:2407.11891` | read |
| KN-LIT-1309 | TAMAGAWA NUMBERS OF ELLIPTIC CURVES WITH AN l-ISOGENY | 2024 | `arxiv:2408.03419` | read |
| KN-LIT-131 | The Supersingular Endomorphism Ring and One Endomorphism Problems are Equivalent | 2024 | `eprint:2023/1399` | web |
| KN-LIT-1310 | THE ASYMPTOTIC DISTRIBUTION OF ELKIES PRIMES FOR REDUCTIONS OF ABELIAN VARIETIES IS GAUSSIAN | 2024 | `arxiv:2411.18171` | read |
| KN-LIT-1311 | The generalized method of solving ECDLP using quantum annealing Łukasz Dzierzkowski1[0000−0002−9204−4558] | 2024 | `arxiv:2410.08725` | read |
| KN-LIT-1312 | THE GROWTH OF TATE–SHAFAREVICH GROUPS OF p-SUPERSINGULAR ELLIPTIC CURVES OVER ANTICYCLOTOMIC Zp -EXTENSIONS AT INERT PRIMES | 2024 | `arxiv:2409.02202` | read |
| KN-LIT-1313 | The Hessian of elliptic curves | 2024 | `arxiv:2407.17042` | read |
| KN-LIT-1314 | THE MAXIMAL ABELIAN EXTENSION CONTAINED IN A DIVISION FIELD OF AN ELLIPTIC CURVE OVER Q WITH COMPLEX MULTIPLICATION | 2024 | `arxiv:2408.16164` | read |
| KN-LIT-1315 | The Supersingular l-Isogeny Path and Endomorphism Ring Problems: Tighter Unconditional Reductions | 2024 | `eprint:2024/1569` | read |
| KN-LIT-1316 | TORSION OF RATIONAL ELLIPTIC CURVES OVER THE CYCLOTOMIC EXTENSIONS OF Q arXiv:2406.15606v6 [math.NT] 3 Aug 2025 ÖMER AVCI | 2024 | `arxiv:2406.15606` | read |
| KN-LIT-1317 | TOWARDS A CLASSIFICATION OF p2 -DISCRIMINANT IDEAL TWINS OVER NUMBER FIELDS ALYSON DEINES, ASIMINA S. HAMAKIOTES, ANDREEA IORGA, CHANGNINGPHAABI NAMOIJAM | 2024 | `arxiv:2403.01287` | read |
| KN-LIT-1318 | Undecidability of infinite algebraic extensions of Fp(t) | 2024 | `arxiv:2409.01492` | read |
| KN-LIT-1319 | UNIFORM POLYNOMIAL BOUNDS ON TORSION FROM RATIONAL | 2024 | `arxiv:2409.08214` | read |
| KN-LIT-132 | Improved algorithms for finding fixed-degree isogenies between supersingular elliptic curves | 2024 | `eprint:2023/1618` | web |
| KN-LIT-1320 | USING FRICKE MODULAR POLYNOMIALS TO COMPUTE ISOGENIES FRANÇOIS MORAIN | 2024 | `arxiv:2402.09027` | read |
| KN-LIT-1321 | WiP: Towards a Secure SECP256K1 for Crypto Wallets: Hardware Architecture and Implementation | 2024 | `arxiv:2411.03910` | read |
| KN-LIT-1321dc | Decoupling support enumeration and value discovery in non-binary ISD | 2025 | `eprint:2025/1523` | web |
| KN-LIT-1322 | ZETA ELEMENTS FOR ELLIPTIC CURVES AND APPLICATIONS | 2024 | `arxiv:2409.01350` | read |
| KN-LIT-1323 | Zeta-functions of Curves over Finite Fields | 2024 | `arxiv:2405.05711` | read |
| KN-LIT-1324 | 100% of elliptic curves with a marked point have positive rank | 2025 | `arxiv:2504.01965` | read |
| KN-LIT-1325 | A Compact Post-quantum Strong Designated Verifier Signature Scheme from Isogenies | 2025 | `eprint:2025/1335` | read |
| KN-LIT-1326 | A COMPARISON PROBLEM FOR ABELIAN SURFACES AND DESCENT FOR SYMPLECTIC ORBITAL INTEGRALS | 2025 | `arxiv:2505.19285` | read |
| KN-LIT-1327 | A High-Performance Curve25519 and Curve448 Unified Elliptic Curve Cryptography Accelerator | 2025 | `arxiv:2504.04731` | read |
| KN-LIT-1328 | A Little LESS Secure Side-Channel Attacks Exploiting Randomness Leakage | 2025 | `eprint:2025/913` | read |
| KN-LIT-1329 | A LOCAL SIGN DECOMPOSITION FOR SYMPLECTIC SELF-DUAL GALOIS REPRESENTATIONS OF RANK TWO | 2025 | `arxiv:2508.17776` | read |
| KN-LIT-133 | SQIsignHD: New Dimensions in Cryptography | 2024 | `eprint:2023/436` | web |
| KN-LIT-1330 | A new approach in constructing isogenies of elliptic curves in characteristic three | 2025 | `arxiv:2509.00427` | read |
| KN-LIT-1331 | A New Method for Solving Discrete Logarithm Based on Index Calculus | 2025 | `eprint:2025/015` | read |
| KN-LIT-1332 | A Note on the Post-Quantum Security of Identity-Based Encryption on Isogenous Pairing Groups | 2025 | `eprint:2025/1439` | read |
| KN-LIT-1333 | A note on “a fully dynamic multi-secret sharing scheme with redundant authorization” | 2025 | `eprint:2025/2329` | read |
| KN-LIT-1334 | A Note on “CABC: A Cross-Domain Authentication Method Combining Blockchain with Certificateless Signature for IIoT” | 2025 | `eprint:2025/834` | read |
| KN-LIT-1335 | A Note on “Designing Anonymous Signature-Based Identity Authentication Scheme for Ocean Multilevel Transmission” | 2025 | `eprint:2025/1914` | read |
| KN-LIT-1336 | A p-CONVERSE THEOREM FOR REAL QUADRATIC FIELDS | 2025 | `arxiv:2504.21799` | read |
| KN-LIT-1337 | A Robust Variant of ChaCha20-Poly1305 | 2025 | `eprint:2025/222` | read |
| KN-LIT-1338 | ABELIAN THREEFOLDS WITH IMAGINARY MULTIPLICATION | 2025 | `arxiv:2504.03860` | read |
| KN-LIT-1339 | Accelerating Elliptic Curve Point Additions on Versal AI Engine for Multi-scalar Multiplication | 2025 | `arxiv:2502.11660` | read |
| KN-LIT-134 | Bootstrap Methods: Another Look at the Jackknife | 1979 | `doi:10.1214/aos/1176344552` | web |
| KN-LIT-1340 | ADDITIVE RIGIDITY FOR x-COORDINATES OF RATIONAL POINTS ON ELLIPTIC CURVES | 2025 | `arxiv:2510.03828` | read |
| KN-LIT-1341 | ALMOST PRIME ORDERS OF ELLIPTIC CURVES OVER PRIME POWER FIELDS | 2025 | `arxiv:2504.18732` | read |
| KN-LIT-1342 | AN ANALOGUE OF KIDA’S FORMULA FOR MAZUR–TATE ELEMENTS | 2025 | `arxiv:2511.21979` | read |
| KN-LIT-1343 | AN ASYMPTOTIC FORMULA FOR TATE-SHAFAREVICH GROUPS OF CM ELLIPTIC CURVES AT SUPERSINGULAR PRIMES KATHARINA MÜLLER | 2025 | `arxiv:2504.05734` | read |
| KN-LIT-1344 | AN ATIYAH-BOTT FORMULA FOR THE LEFSCHETZ NUMBER OF A SINGULAR FOLIATION | 2025 | `arxiv:2501.05812` | read |
| KN-LIT-1345 | AN EFFICIENT VALIDATED ASYNCHRONOUS BYZANTINE | 2025 | `eprint:2026/1106` | read |
| KN-LIT-1346 | Analyzing the capabilities of HLS and RTL tools in the design of an FPGA Montgomery Multiplier | 2025 | `arxiv:2509.08067` | read |
| KN-LIT-1347 | ATKIN AND SWINNERTON-DYER CONGRUENCES FOR MEROMORPHIC | 2025 | `arxiv:2511.05718` | read |
| KN-LIT-1348 | Attacks on PRISM-id via Torsion over Small Extension Fields | 2025 | `eprint:2025/1602` | read |
| KN-LIT-1349 | AVERAGE RANK OF ELLIPTIC CURVES OVER FUNCTION FIELDS | 2025 | `arxiv:2510.25630` | read |
| KN-LIT-135 | Power-Law Distributions in Empirical Data | 2009 | `url:aaronclauset.github.io/powerlaws` | web |
| KN-LIT-1350 | Better Bounds for Finding Fixed-Degree Isogenies via Coppersmith’s Method | 2025 | `eprint:2025/1812` | read |
| KN-LIT-1351 | Brace for impact: ECDLP challenges for quantum cryptanalysis | 2025 | `arxiv:2508.14011` | read |
| KN-LIT-1352 | Breaking ECDSA with Two Affinely Related Nonces | 2025 | `eprint:2025/705` | read |
| KN-LIT-1353 | Circuit-Succinct Algebraic Batch Arguments from Projective Functional Commitments? | 2025 | `eprint:2025/1943` | read |
| KN-LIT-1354 | CLASS GROUPS AND SELMER GROUPS IN SPECIAL FAMILIES | 2025 | `arxiv:2504.15428` | read |
| KN-LIT-1355 | Cluster Computing (2025)28:691 https://doi.org/10.1007/s10586-025-05493-9 (0123456789().,-volV)(0123456789() | 2025 | `arxiv:2509.10581` | read |
| KN-LIT-1356 | Commitment Schemes Based on Module-LIP | 2025 | `eprint:2025/431` | read |
| KN-LIT-1357 | Compact, Efficient and CCA-Secure Updatable Encryption from Isogenies | 2025 | `eprint:2025/1853` | read |
| KN-LIT-1358 | COMPLEX TORI CONSTRUCTED FROM CAYLEY–DICKSON ALGEBRAS | 2025 | `arxiv:2504.12660` | read |
| KN-LIT-1359 | Complexity of Post-Quantum Cryptography in | 2025 | `arxiv:2504.13537` | read |
| KN-LIT-1359cc | Classic McEliece on the ARM Cortex-M4 | 2021 | `eprint:2021/492` | web |
| KN-LIT-136 | Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing | 1995 | `doi:10.1111/j.2517-6161.1995.tb02031.x` | web |
| KN-LIT-1360 | Computing Isomorphisms between Products of Supersingular Elliptic Curves | 2025 | `arxiv:2503.21535` | read |
| KN-LIT-1361 | COMPUTING THE MOD-3 GALOIS IMAGE OF A PRINCIPALLY POLARIZED ABELIAN SURFACE OVER THE RATIONALS | 2025 | `arxiv:2502.02044` | read |
| KN-LIT-1362 | CONGRUENCE CONDITIONS FOR THE MOD λ VALUES OF THE FOURIER COEFFICIENTS OF CLASSICAL EIGENFORMS | 2025 | `arxiv:2506.08865` | read |
| KN-LIT-1363 | Congruences modulo 23 to y 2 = x3 − 23 are trivial Elie Studnia | 2025 | `arxiv:2507.20801` | read |
| KN-LIT-1364 | CONTINUOUS INVERSE AMBIGUOUS FUNCTIONS ON LIE GROUPS | 2025 | `arxiv:2510.09958` | read |
| KN-LIT-1365 | COUNTING 5-ISOGENIES OF ELLIPTIC CURVES OVER Q | 2025 | `arxiv:2504.07750` | read |
| KN-LIT-1366 | Cryptanalysis of Isogeny-Based Quantum Money with Rational Points | 2025 | `eprint:2025/201` | read |
| KN-LIT-1367 | Cryptomania v.s. Minicrypt in a Quantum World | 2025 | `eprint:2025/639` | read |
| KN-LIT-1368 | Cycles and Cuts in Supersingular L-Isogeny Graphs | 2025 | `eprint:2025/155` | read |
| KN-LIT-1369 | Decompose and conquer: ZVP attacks on GLV curves | 2025 | `eprint:2025/076` | read |
| KN-LIT-137 | Training Compute-Optimal Large Language Models | 2022 | `url:arxiv.org/abs/2203.15556` | web |
| KN-LIT-1370 | Delta operation at height | 2025 | `arxiv:2512.12714` | read |
| KN-LIT-1371 | Derivative-Free Richelot Isogenies via Subresultants: | 2025 | `eprint:2025/2145` | read |
| KN-LIT-1372 | DETERMINING MONOGENITY OF PURE CUBIC NUMBER | 2025 | `arxiv:2505.06213` | read |
| KN-LIT-1373 | Diamond iO: Indistinguishability Obfuscation at Near Functional-Encryption Cost via Matrix Products | 2025 | `eprint:2025/236` | read |
| KN-LIT-1374 | Dimensional eROSion: Improving the ROS Attack with Decomposition in Higher Bases | 2025 | `eprint:2025/306` | read |
| KN-LIT-1375 | Distinguishing Full-Round AES-256 in a Ciphertext-Only Setting via Hybrid Statistical Learning | 2025 | `eprint:2025/862` | read |
| KN-LIT-1376 | DISTRIBUTION QUESTIONS FOR ISOGENY GRAPHS OVER FINITE FIELDS | 2025 | `arxiv:2512.14469` | read |
| KN-LIT-1377 | DIVISIBILITY OF THE COEFFICIENTS OF MODULAR POLYNOMIALS | 2025 | `arxiv:2509.06423` | read |
| KN-LIT-1378 | DIVISION POLYNOMIALS FOR ARBITRARY ISOGENIES | 2025 | `eprint:2025/521` | read |
| KN-LIT-1379 | DOUBLE-ORIENTATIONS ON SUPERSINGULAR ISOGENY GRAPHS | 2025 | `arxiv:2510.15820` | read |
| KN-LIT-138 | Efficient Algorithms for Solving Overdefined Systems of Multivariate Polynomial Equations | 2000 | `doi:10.1007/3-540-45539-6_27` | web |
| KN-LIT-1380 | ECDSA Cracking Methods | 2025 | `eprint:2025/654` | read |
| KN-LIT-1381 | ECTester: Reverse-engineering side-channel countermeasures of ECC implementations | 2025 | `eprint:2025/1293` | read |
| KN-LIT-1382 | Efficient Algorithms for Isogeny Computation on Hyperelliptic Curves: Their Applications in Post-Quantum Cryptography | 2025 | `arxiv:2504.04559` | read |
| KN-LIT-1383 | Efficient Privacy-Preserving Blueprints for Threshold Comparison | 2025 | `eprint:2025/2253` | read |
| KN-LIT-1384 | Eisenstein cocycles for imaginary quadratic fields | 2025 | `arxiv:2504.19125` | read |
| KN-LIT-1385 | Elliptic Curve Modulation (ECM) for Extremely | 2025 | `arxiv:2505.14153` | read |
| KN-LIT-1386 | Engel p-adic Isogeny-based Cryptography over Laurent Series: Foundations, Security, and an ESP32 Implementation | 2025 | `arxiv:2511.20533` | read |
| KN-LIT-1387 | Enhanced Algorithms for the Representation of integers by Binary Quadratic forms: Reduction to Subset Sum | 2025 | `arxiv:2502.11402` | read |
| KN-LIT-1388 | EQUIVALENCE OF CONJECTURES ON HEAVENLY ELLIPTIC CURVES | 2025 | `arxiv:2505.17474` | read |
| KN-LIT-1389 | EXISTENCE OF SIMPLE NON-CYCLIC ABELIAN VARIETIES OVER | 2025 | `arxiv:2507.06916` | read |
| KN-LIT-139 | A crossbred algorithm for solving Boolean polynomial systems | 2017 | `eprint:2017/372` | web |
| KN-LIT-1390 | Experimentally studying path-finding problem between conjugates in supersingular isogeny graphs: Optimizing primes and powers to speed-up cycle finding Madhurima Mukhopadhyay | 2025 | `eprint:2025/189` | read |
| KN-LIT-1391 | EXPLICIT CONSTRUCTIONS OF CYCLIC N -ISOGENIES | 2025 | `arxiv:2512.21088` | read |
| KN-LIT-1392 | EXPLICIT SURJECTIVITY OF GALOIS REPRESENTATIONS OF PRODUCTS OF ELLIPTIC CURVES OVER FUNCTION FIELDS | 2025 | `arxiv:2510.20910` | read |
| KN-LIT-1393 | Fast Plaintext-Ciphertext Matrix Multiplication from Additively Homomorphic Encryption | 2025 | `arxiv:2504.14497` | read |
| KN-LIT-1394 | G ECC: A GPU- BASED HIGH - THROUGHPUT FRAMEWORK FOR E LLIPTIC C URVE C RYPTOGRAPHY | 2025 | `arxiv:2501.03245` | read |
| KN-LIT-1395 | Generic-compatible distinguishers for linear regression based attacks | 2025 | `eprint:2025/1875` | read |
| KN-LIT-1396 | GROSS LATTICES OF SUPERSINGULAR ELLIPTIC CURVES | 2025 | `arxiv:2503.03478` | read |
| KN-LIT-1397 | HasteBoots: Proving TFHE Programmable Bootstrapping in Seconds | 2025 | `eprint:2025/261` | read |
| KN-LIT-1398 | How (not) to Build Identity-Based Encryption from Isogenies | 2025 | `eprint:2025/1726` | read |
| KN-LIT-1399 | Hydrangea: Optimistic Two-Round Partial Synchrony with Improved Fault Resilience | 2025 | `eprint:2025/1112` | read |
| KN-LIT-13a01d | A distinguisher for high rate McEliece cryptosystems | 2010 | `eprint:2010/331` | web |
| KN-LIT-140 | On the Complexity of Solving Quadratic Boolean Systems | 2013 | `url:arxiv.org/abs/1112.6263` | web |
| KN-LIT-1400 | Improved algorithms for ascending isogeny | 2025 | `eprint:2025/1243` | read |
| KN-LIT-1401 | IMPROVED BOUNDS FOR SERRE’S OPEN IMAGE THEOREM | 2025 | `arxiv:2501.00202` | read |
| KN-LIT-1402 | Improved Subfield Curve Search For Specific Field Characteristics | 2025 | `eprint:2025/226` | read |
| KN-LIT-1403 | Improving the Masked Division for the FALCON Signature | 2025 | `eprint:2025/628` | read |
| KN-LIT-1404 | INERTIAL TYPES OF ELLIPTIC CURVES OVER Qp2 | 2025 | `arxiv:2512.05023` | read |
| KN-LIT-1405 | INFINITELY MANY ELLIPTIC CURVES OVER Q(i) WITH RANK 2 AND j-INVARIANT 1728 | 2025 | `arxiv:2506.17605` | read |
| KN-LIT-1406 | INFINITELY MANY PRIMES OF BASIC REDUCTION FOR SOME ABELIAN FOURFOLDS | 2025 | `arxiv:2511.05322` | read |
| KN-LIT-1407 | INFINITELY MANY SUPERSINGULAR PRIMES FOR SOME MUMFORD’S | 2025 | `arxiv:2511.06654` | read |
| KN-LIT-1408 | INKE: Isogeny-Based PKE Using Intermediate Curves | 2025 | `eprint:2025/1458` | read |
| KN-LIT-1409 | Insecurity of One Ring Signature Scheme with Batch Verification for Applications in VANETs | 2025 | `eprint:2025/999` | read |
| KN-LIT-141 | MQ Challenge: Hardness Evaluation of Solving Multivariate Quadratic Problems | 2015 | `eprint:2015/275` | web |
| KN-LIT-1410 | ISOGENIES OF CM ELLIPTIC CURVES | 2025 | `arxiv:2503.05685` | read |
| KN-LIT-1411 | ISOGENY GRAPHS OF ABELIAN VARIETIES AND SINGULAR IDEALS IN ORDERS | 2025 | `arxiv:2508.03570` | read |
| KN-LIT-1412 | ISOGENY GRAPHS WITH LEVEL STRUCTURES ARISING FROM THE VERSCHIEBUNG MAP | 2025 | `arxiv:2501.03846` | read |
| KN-LIT-1413 | Issuer Hiding for BBS-Based Anonymous Credentials | 2025 | `eprint:2025/2080` | read |
| KN-LIT-1414 | ITEP-TH-37/25 Dispersionless version of multi-component Pfaff-Toda hierarchy | 2025 | `arxiv:2512.22357` | read |
| KN-LIT-1415 | Key Recovery Attacks on ZIP Ciphers: | 2025 | `eprint:2025/2291` | read |
| KN-LIT-1416 | Let us walk on the 3-isogeny graph: efficient | 2025 | `eprint:2025/691` | read |
| KN-LIT-1417 | Linear Complementary Pairs of Algebraic Geometry Codes via Kummer Extensions | 2025 | `arxiv:2506.23081` | read |
| KN-LIT-1418 | LOCAL-GLOBAL PRINCIPLE FOR 11-ISOGENIES OF ELLIPTIC CURVES IS TRUE OVER QUADRATIC FIELDS | 2025 | `arxiv:2501.17602` | read |
| KN-LIT-1419 | Low latency FPGA implementation of twisted Edward curve cryptography hardware accelerator over prime field | 2025 | `arxiv:2504.21342` | read |
| KN-LIT-141bac | A public-key cryptosystem based on algebraic coding theory | 1978 | `url:ipnpr.jpl.nasa.gov/progress_report2/42-44/44n.pdf` | false |
| KN-LIT-142 | A Note on Negligible Functions | 1997 | `eprint:1997/004` | read |
| KN-LIT-1420 | MAZUR’S GROWTH NUMBER CONJECTURE IN THE RANK ONE CASE | 2025 | `arxiv:2504.10761` | read |
| KN-LIT-1421 | Memory Optimizations of Wagner’s Algorithm with Applications to Equihash | 2025 | `eprint:2025/2141` | read |
| KN-LIT-1422 | MODULAR FORMS OF CM TYPE MOD l | 2025 | `arxiv:2505.16529` | read |
| KN-LIT-1423 | Murmurations for elliptic curves ordered by height | 2025 | `arxiv:2504.12295` | read |
| KN-LIT-1424 | New Exchanged Boomerang Distinguishers for 5-Round AES | 2025 | `eprint:2025/248` | read |
| KN-LIT-1425 | New Techniques for Analyzing Differentials with Application to AES | 2025 | `eprint:2025/1326` | read |
| KN-LIT-1426 | Non Reed-Solomon Type MDS Codes from Elliptic Curves | 2025 | `arxiv:2509.04247` | read |
| KN-LIT-1427 | NUMBER OF K-RATIONAL POINTS WITH GIVEN j-INVARIANT ON MODULAR CURVES | 2025 | `arxiv:2512.24817` | read |
| KN-LIT-1428 | ON ANTICYCLOTOMIC SELMER GROUPS OF ELLIPTIC CURVES | 2025 | `arxiv:2504.01696` | read |
| KN-LIT-1429 | ON CERTAIN ROOT NUMBER 1 CASES OF THE CUBE SUM PROBLEM | 2025 | `arxiv:2508.05361` | read |
| KN-LIT-143 | The Random Oracle Methodology, Revisited | 1998 | `eprint:1998/011` | read |
| KN-LIT-1430 | ON PRIMES REPRESENTED BY aX 2 + bY | 2025 | `arxiv:2503.05396` | read |
| KN-LIT-1431 | On randomness complexity of 1-private protocols | 2025 | `eprint:2025/1121` | read |
| KN-LIT-1432 | On the Complexity of Effective Theories arXiv:2512.11029v1 [hep-th] 11 Dec 2025 – Seiberg-Witten theory | 2025 | `arxiv:2512.11029` | read |
| KN-LIT-1433 | On the Fiat–Shamir Security of Succinct Arguments from Functional Commitments | 2025 | `eprint:2025/902` | read |
| KN-LIT-1434 | ON THE GROWTH OF TATE–SHAFAREVICH GROUPS OF p-SUPERSINGULAR ABELIAN VARIETIES OF GL2 -TYPE OVER Zp -EXTENSIONS OF NUMBER FIELDS | 2025 | `arxiv:2510.11511` | read |
| KN-LIT-1435 | ON THE HASSE PRINCIPLE FOR DIVISIBILITY IN ELLIPTIC CURVES | 2025 | `arxiv:2511.02078` | read |
| KN-LIT-1436 | On the local-to-global principle for zero-cycles on self products of elliptic curves with CM | 2025 | `arxiv:2509.13641` | read |
| KN-LIT-1437 | On the Regularity of the Generalized Birthday Problem | 2025 | `eprint:2025/1351` | read |
| KN-LIT-1438 | On the Termination of the HotStuff Protocol Within the Universally Composable Framework | 2025 | `eprint:2025/1560` | read |
| KN-LIT-1439 | ON THE TORSION GROWTH IN QUADRATIC NUMBER FIELDS FOR ELLIPTIC CURVES DEFINED OVER THE RATIONALS | 2025 | `arxiv:2504.03286` | read |
| KN-LIT-144 | Corrigendum to Everett W. Howe: Isogeny classes of abelian varieties with no principal polarizations, pp. 203–216 in: Moduli of Abelian Varieties (C. Faber, G. van der Geer, F. Oort, eds.) | 2000 | `arxiv:0002232` | read |
| KN-LIT-1440 | On the UC-(In)Security of PAKE Protocols Without the Random Oracle Model | 2025 | `eprint:2025/998` | read |
| KN-LIT-1441 | One for All, All for One: Universal semi-agnostic quantum circuit for solving (Standard) Abelian Hidden Subgroup Problems | 2025 | `eprint:2025/869` | read |
| KN-LIT-1442 | One More Motivation to Use Evaluation Tools This Time for Hardware Multiplicative Masking of AES | 2025 | `eprint:2025/733` | read |
| KN-LIT-1443 | One-Shot Secure Aggregation: A Hybrid Cryptographic Protocol for Private Federated Learning in IoT | 2025 | `arxiv:2511.23252` | read |
| KN-LIT-1444 | Optimal Representation for Right-to-Left | 2025 | `arxiv:2508.07310` | read |
| KN-LIT-1445 | Optimizing AES-GCM on ARM Cortex-M4: A | 2025 | `eprint:2025/512` | read |
| KN-LIT-1446 | Orient Express: Using Frobenius to Express | 2025 | `eprint:2025/1047` | read |
| KN-LIT-1447 | PaCo: Bootstrapping for CKKS via Partial CoeffToSlot | 2025 | `eprint:2025/886` | read |
| KN-LIT-1448 | PASCAL’S MATRIX, POINT COUNTING ON ELLIPTIC CURVES AND PROLATE SPHEROIDAL FUNCTIONS | 2025 | `arxiv:2508.08494` | read |
| KN-LIT-1449 | PEGASIS: Practical Effective Class Group Action using 4-Dimensional Isogenies | 2025 | `eprint:2025/401` | read |
| KN-LIT-145 | The Splitting of Primes in Division Fields of Elliptic Curves W.Duke and Á. Tóth Dedicated to the memory of Petr C̃ižek | 2001 | `arxiv:0103151` | read |
| KN-LIT-1450 | Permutation-Based Hashing With Stronger (Second) | 2025 | `eprint:2025/963` | read |
| KN-LIT-1451 | POSITIVE DENSITY OF PRIMES OF ORDINARY REDUCTION FOR ABELIAN VARIETIES OF SIMPLE SIGNATURE | 2025 | `arxiv:2508.11174` | read |
| KN-LIT-1452 | Practical Key Collision on AES and Kiasu-BC | 2025 | `eprint:2025/462` | read |
| KN-LIT-1453 | Prepared for submission to JHEP | 2025 | `arxiv:2504.13011` | read |
| KN-LIT-1454 | PRIME ORDER TORSION ON ELLIPTIC CURVES OVER NUMBER FIELDS | 2025 | `arxiv:2505.14109` | read |
| KN-LIT-1455 | Privacy-Preserving Edge Computing from Pairing-Based Inner Product Functional Encryption | 2025 | `arxiv:2504.02068` | read |
| KN-LIT-1456 | Pure and Applied Mathematics Quarterly | 2025 | `arxiv:2508.11835` | read |
| KN-LIT-1457 | Qlapoti: Simple and Efficient | 2025 | `eprint:2025/1604` | read |
| KN-LIT-1458 | QUADRATIC SPACES AND SELMER GROUPS OF ABELIAN VARIETIES WITH MULTIPLICATION | 2025 | `arxiv:2504.21272` | read |
| KN-LIT-1459 | Quantum circuit for implementing AES S-box with low costs | 2025 | `eprint:2025/454` | read |
| KN-LIT-146 | COMPUTING THE CARDINALITY OF CM ELLIPTIC | 2002 | `arxiv:0210173` | read |
| KN-LIT-1460 | Quantum resource estimates for computing binary elliptic curve discrete logarithms | 2025 | `arxiv:2503.02984` | read |
| KN-LIT-1461 | Recursion Enabled: Improved Cryptanalysis of the Permuted Kernel Problem | 2025 | `eprint:2025/2073` | read |
| KN-LIT-1462 | Refined Humbert Invariants in Supersingular Isogeny Degree Analysis | 2025 | `eprint:2025/1605` | read |
| KN-LIT-1463 | Resource analysis of Shor’s elliptic curve algorithm with an improved quantum adder on a two-dimensional lattice | 2025 | `arxiv:2510.23212` | read |
| KN-LIT-1464 | S ELMER -I NSPIRED E LLIPTIC C URVE G ENERATION | 2025 | `arxiv:2510.02383` | read |
| KN-LIT-1465 | Scrutinizing the Security of AES-based Hashing and One-way Functions | 2025 | `eprint:2025/792` | read |
| KN-LIT-1466 | Security and Privacy Management of IoT Using Quantum Computing | 2025 | `arxiv:2511.03538` | read |
| KN-LIT-1467 | SELBERG ORTHOGONALITY FOR HALF-INTEGRAL WEIGHT | 2025 | `arxiv:2508.07734` | read |
| KN-LIT-1468 | SELMER GROUPS OF FAMILIES OF ELLIPTIC CURVES WITH AN l-ISOGENY | 2025 | `arxiv:2508.21406` | read |
| KN-LIT-1469 | SELMER STABILITY FOR ELLIPTIC CURVES IN GALOIS l-EXTENSIONS | 2025 | `arxiv:2504.15945` | read |
| KN-LIT-147 | REAL MULTIPLICATION AND NONCOMMUTATIVE GEOMETRY arXiv:math/0202109v1 [math.AG] 12 Feb 2002 (ein Alterstraum) | 2002 | `arxiv:0202109` | read |
| KN-LIT-1470 | Side-channel safe conditional moves and swaps | 2025 | `eprint:2025/935` | read |
| KN-LIT-1471 | Simplified Meet-in-the-middle Preimage Attacks on AES-based Hashing Mathieu Degré | 2025 | `eprint:2025/2213` | read |
| KN-LIT-1472 | SINGLE-VALUED PERIODS OF MEROMORPHIC MODULAR FORMS AND A MOTIVIC INTERPRETATION OF THE GROSS-ZAGIER CONJECTURE | 2025 | `arxiv:2508.04844` | read |
| KN-LIT-1473 | SMALL TAMAGAWA NUMBERS OF ELLIPTIC CURVES WITH ISOGENIES OR TORSION | 2025 | `arxiv:2505.20479` | read |
| KN-LIT-1474 | SoK: Deep Learning-based Physical Side-channel Analysis | 2025 | `eprint:2025/1309` | read |
| KN-LIT-1475 | SOME REDUCIBLE AND IRREDUCIBLE BRILL–NOETHER LOCI | 2025 | `arxiv:2503.16255` | read |
| KN-LIT-1476 | SPECIAL ENDOMORPHISMS OF QM ABELIAN SURFACES | 2025 | `arxiv:2509.22837` | read |
| KN-LIT-1477 | Spectral Curves with Complex Multiplication in Hermitian Matrix Models | 2025 | `arxiv:2509.16997` | read |
| KN-LIT-1478 | SPORADIC POINTS ON X0 (N ) | 2025 | `arxiv:2511.09015` | read |
| KN-LIT-1479 | SQIsign2D2 : New SQIsign2D Variant by Leveraging Power Smooth Isogenies in Dimension One | 2025 | `eprint:2025/920` | read |
| KN-LIT-148 | The rational function analogue of a question of Schur and exceptionality of permutation representations | 2002 | `arxiv:0201069` | read |
| KN-LIT-1480 | SQIsign2DPush: Faster Signature Scheme Using 2-Dimensional Isogenies | 2025 | `eprint:2025/897` | read |
| KN-LIT-1481 | STABILITY OF TORSION SUBGROUPS OF ELLIPTIC CURVES OVER NON-GALOIS EXTENSIONS OF ODD PRIME DEGREE | 2025 | `arxiv:2510.18194` | read |
| KN-LIT-1482 | Superglue: Fast formulae for (2,2)-gluing isogenies | 2025 | `eprint:2025/736` | read |
| KN-LIT-1483 | Supersingular primes and Bogomolov property | 2025 | `arxiv:2504.13498` | read |
| KN-LIT-1484 | SUPERSPECIAL PRIMES FOR QM ABELIAN SURFACES OVER REAL NUMBER FIELDS | 2025 | `arxiv:2511.07814` | read |
| KN-LIT-1485 | The computational refined Humbert invariant problem is equivalent to the computational isogeny problem | 2025 | `eprint:2025/1295` | read |
| KN-LIT-1486 | The density of elliptic curves over Qp with a rational 3-torsion point or a rational 3-isogeny | 2025 | `arxiv:2502.08583` | read |
| KN-LIT-1487 | The Nonlinear Filter Model of Stream Cipher Redivivus | 2025 | `eprint:2025/160` | read |
| KN-LIT-1488 | THE PARTITION FUNCTION AND ELLIPTIC CURVES | 2025 | `arxiv:2508.09608` | read |
| KN-LIT-1489 | THE POSSIBLE ADELIC INDICES FOR ELLIPTIC CURVES ADMITTING A RATIONAL CYCLIC ISOGENY | 2025 | `arxiv:2512.00652` | read |
| KN-LIT-149 | A formula for the central value of certain | 2003 | `arxiv:0309023` | read |
| KN-LIT-1490 | THE QUANTUM INTEGRABLE HIERARCHY FOR THE GROMOV-WITTEN THEORY OF ELLIPTIC CURVES | 2025 | `arxiv:2512.04621` | read |
| KN-LIT-1491 | The Rényi Smoothing Parameter and Its Applications in Lattice-Based Cryptography | 2025 | `eprint:2025/986` | read |
| KN-LIT-1492 | THE SEA ALGORITHM FOR ENDOMORPHISMS OF SUPERSINGULAR | 2025 | `arxiv:2501.16321` | read |
| KN-LIT-1493 | THE SPINE OF A SUPERSINGULAR l-ISOGENY GRAPH | 2025 | `arxiv:2502.03613` | read |
| KN-LIT-1494 | Threshold Public-Key Encryption: | 2025 | `eprint:2025/1665` | read |
| KN-LIT-1495 | TORSION OF Q-CURVES OVER NUMBER FIELDS OF SMALL ODD | 2025 | `arxiv:2506.00753` | read |
| KN-LIT-1496 | TORSION OF RATIONAL ELLIPTIC CURVES OVER THE Zp -EXTENSIONS OF QUADRATIC FIELDS | 2025 | `arxiv:2505.04149` | read |
| KN-LIT-1497 | TWISTS ARISING FROM TORSION POINTS arXiv:2510.08486v1 [math.NT] 9 Oct 2025 LUKAS NOVAK | 2025 | `arxiv:2510.08486` | read |
| KN-LIT-1498 | UNBOUNDED AVERAGE SELMER RANKS OF ELLIPTIC CURVES IN TORSION FAMILIES | 2025 | `arxiv:2512.16120` | read |
| KN-LIT-1499 | Unconditional foundations for supersingular isogeny-based cryptography | 2025 | `arxiv:2502.17010` | read |
| KN-LIT-150 | A Framework for Password-Based Authenticated Key Exchange? | 2003 | `eprint:2003/032` | read |
| KN-LIT-1500 | UNIFORM BOUNDS ON THE LEVEL OF CYCLOTOMIC DIVISION FIELDS OF ELLIPTIC CURVES | 2025 | `arxiv:2511.23381` | read |
| KN-LIT-1501 | UNIFORM IRREDUCIBILITY OF GALOIS ACTION ON THE l-PRIMARY PART OF ABELIAN 3-FOLDS OF PICARD TYPE | 2025 | `arxiv:2511.04609` | read |
| KN-LIT-1502 | Universally Composable On-Chain Quadratic Voting for Liquid Democracy | 2025 | `eprint:2025/803` | read |
| KN-LIT-1503 | UNVEILING ARITHMETIC STATISTICS OF CONGRUENT NUMBER | 2025 | `arxiv:2509.03129` | read |
| KN-LIT-1504 | UPKE and UKEM Schemes from Supersingular Isogenies | 2025 | `eprint:2025/1010` | read |
| KN-LIT-1505 | Validation of Quantum Elliptic Curve Point Addition Circuits | 2025 | `arxiv:2506.03318` | read |
| KN-LIT-1506 | WaterSQI and PRISMO: Quaternion Signatures for Supersingular Isogeny Group Actions | 2025 | `eprint:2025/1737` | read |
| KN-LIT-1507 | ZETA FUNCTIONS OF ABSTRACT ISOGENY GRAPHS AND MODULAR CURVES | 2025 | `arxiv:2509.15214` | read |
| KN-LIT-1508 | −3-SELMER GROUPS, IDEAL CLASS GROUPS AND LARGE 3-SELMER RANKS | 2025 | `arxiv:2502.01069` | read |
| KN-LIT-1509 | 2nd Student Conference of Informatics & Telecommunications | 2026 | `arxiv:2605.17116` | read |
| KN-LIT-151 | ANTICYCLOTOMIC IWASAWA THEORY OF CM ELLIPTIC CURVES | 2003 | `arxiv:0302319` | read |
| KN-LIT-1510 | A Blockchain-Based Pre-Verification Access Control Scheme with Vector Commitments and Bulletproofs | 2026 | `eprint:2026/1003` | read |
| KN-LIT-1511 | A Certified Framework for Deterministic Navigation in Higher-Genus p-Isogeny Graphs | 2026 | `eprint:2026/007` | read |
| KN-LIT-1512 | A Comparative Evaluation of End-to-End-Encrypted Key | 2026 | `eprint:2026/1108` | read |
| KN-LIT-1513 | A COMPLETE CHARACTERIZATION OF HERON TRIANGLES | 2026 | `arxiv:2605.22458` | read |
| KN-LIT-1514 | A Complexity-Theoretic Approach to Proofs of Space | 2026 | `eprint:2026/1470` | read |
| KN-LIT-1515 | A computational approach to Drinfeld modules | 2026 | `arxiv:2601.02162` | read |
| KN-LIT-1516 | A Constant-Time Implementation Methodology for Activation Functions on Microcontrollers | 2026 | `arxiv:2605.22441` | read |
| KN-LIT-1517 | A CORRELATED REFINEMENT OF THE DOUBLE DOUBLE | 2026 | `arxiv:2606.11154` | read |
| KN-LIT-1518 | A correlation duet: Correlation attacks on correlation generators | 2026 | `eprint:2026/1126` | read |
| KN-LIT-1519 | A Cryptographic Framework for Proof of Personhood | 2026 | `eprint:2026/333` | read |
| KN-LIT-152 | Curves of genus 2 with (N,N) decomposable Jacobians | 2003 | `arxiv:0312285` | read |
| KN-LIT-1520 | A FORMAL ANALYSIS OF FLEX AND FLEX2 | 2026 | `eprint:2026/983` | read |
| KN-LIT-1521 | A Formal Basis for Quantum Cryptographic Exposure Measurement under HNDL Threat | 2026 | `arxiv:2605.22569` | read |
| KN-LIT-1522 | A General Randomness Reuse Framework for First-Order Secure Masking and Applications on AES Design Using Randomness Solely for Input Encoding | 2026 | `eprint:2026/026` | read |
| KN-LIT-1523 | A Guess and Determine Attack on the Elliptic Curve Discrete | 2026 | `arxiv:2607.09814` | read |
| KN-LIT-1524 | A High-Speed Hardware Accelerator for QR-UOV Signature Scheme | 2026 | `eprint:2026/1458` | read |
| KN-LIT-1525 | A LOCAL HILBERT–PÓLYA REALISATION FOR ELLIPTIC CURVE L-FUNCTIONS | 2026 | `arxiv:2605.17645` | read |
| KN-LIT-1526 | A New Construction Method for More Efficient Quadratic One-Time Noisy | 2026 | `eprint:2026/1033` | read |
| KN-LIT-1527 | A New Insight into Constructing Cryptographic Boolean Functions via Walsh Spectral Analysis | 2026 | `eprint:2026/985` | read |
| KN-LIT-1528 | A NOTE ON BREMNER’S CONJECTURE AND UNIFORMITY | 2026 | `arxiv:2604.04850` | read |
| KN-LIT-1529 | A note on Zilber-Pink in Y (1)n | 2026 | `arxiv:2605.00766` | read |
| KN-LIT-153 | Hecke eigenvalues of Siegel modular forms (mod p) and of algebraic modular forms | 2003 | `arxiv:0309006` | read |
| KN-LIT-1530 | A p-ADIC COHOMOLOGICAL APPROACH TO CONGRUENCES OF MEROMORPHIC MODULAR FORMS | 2026 | `arxiv:2601.12157` | read |
| KN-LIT-1531 | A Post-Quantum Accountable Sanitizable Signature Scheme Based on Unbalanced Oil and Vinegar | 2026 | `eprint:2026/827` | read |
| KN-LIT-1532 | A Practical Key-Recovery Attack on GRAFHEN | 2026 | `eprint:2026/1460` | read |
| KN-LIT-1533 | A PROOF OF THE 4, 7 CASES OF SYLVESTER’S CONJECTURE ON CUBE SUMS | 2026 | `arxiv:2605.25917` | read |
| KN-LIT-1534 | A THEORY OF GENERALIZED LAMÉ CURVES | 2026 | `arxiv:2604.21880` | read |
| KN-LIT-1535 | A VPN-as-a-Service Tailored Enabler for Computing-constrained Environments | 2026 | `arxiv:2606.11729` | read |
| KN-LIT-1536 | ABELIAN SURFACES IN HESSE FORM AND EXPLICIT ISOGENY FORMULAS | 2026 | `eprint:2026/039` | read |
| KN-LIT-1537 | Acoustic Interference: A New Paradigm Weaponizing Acoustic Latent Semantic for Universal Jailbreak against Large Audio Language Models | 2026 | `arxiv:2605.18168` | read |
| KN-LIT-1538 | ALGEBRA OF THE INFRARED WITH CURVE–VALUED POTENTIAL | 2026 | `arxiv:2607.04039` | read |
| KN-LIT-1539 | Algebraic Attack on | 2026 | `eprint:2026/241` | read |
| KN-LIT-154 | HOMOMORPHISMS OF HYPERELLIPTIC JACOBIANS YU. G. ZARHIN | 2003 | `arxiv:0301173` | read |
| KN-LIT-1540 | ALGEBRAIC MODELINGS OF THE SUPERSINGULAR ISOGENY PROBLEM | 2026 | `arxiv:2607.05160` | read |
| KN-LIT-1541 | ALGORITHMS FOR HYPERELLIPTIC MUMFORD CURVES: | 2026 | `arxiv:2607.02160` | read |
| KN-LIT-1542 | An Application-Layer Multi-Modal Covert-Channel Reference Monitor for LLM Agent Egress | 2026 | `arxiv:2605.20734` | read |
| KN-LIT-1543 | An Elliptic Curve Governing Hopf Linking in an A4-Symmetric Tensegrity | 2026 | `arxiv:2604.18116` | read |
| KN-LIT-1544 | An Evidence-driven Protocol for Trustworthy CI Pipelines | 2026 | `arxiv:2605.21089` | read |
| KN-LIT-1545 | AN INFINITE FAMILY OF PRIMITIVE HERON TRIANGLES WITH TWO SIDES AS PERFECT SQUARES | 2026 | `arxiv:2601.17317` | read |
| KN-LIT-1546 | ANALYTIC RANK-ONE ELLIPTIC CURVES OVER FUNCTION FIELDS AND THEIR RANK OVER CERTAIN RING CLASS FIELDS | 2026 | `arxiv:2603.29686` | read |
| KN-LIT-1547 | ANSA-IBKEM: Practical Quantum-Safe Identity-Based Key Encapsulation via Annular | 2026 | `eprint:2026/1449` | read |
| KN-LIT-1548 | ANTICYCLOTOMIC IWASAWA MAIN CONJECTURES FOR MODULAR FORMS | 2026 | `arxiv:2603.22483` | read |
| KN-LIT-1549 | ARITHMETIC EXCEPTIONALITY OF LATTÈS MAPS | 2026 | `arxiv:2603.25014` | read |
| KN-LIT-155 | Multi-trapdoor Commitments and their Applications to Proofs of Knowledge Secure under Concurrent Man-in-the-middle Attacks? | 2003 | `eprint:2003/214` | read |
| KN-LIT-1550 | Ark: Offchain Transaction Batching in Bitcoin | 2026 | `arxiv:2605.20952` | read |
| KN-LIT-1551 | ARTIN TWISTS OF DRINFELD MODULES AND GOSS L-SERIES | 2026 | `arxiv:2602.04211` | read |
| KN-LIT-1552 | Asking Back: Interaction-Layer | 2026 | `arxiv:2605.16462` | read |
| KN-LIT-1553 | Assessing Geometric Security of AES Neural Realizations: Linear-Time Key Recovery via Neural Leakage | 2026 | `eprint:2026/734` | read |
| KN-LIT-1554 | Asymptotically Optimal Distance-Tail Bounds for Large-Field RAA Codes | 2026 | `eprint:2026/1075` | read |
| KN-LIT-1555 | Asynchronous Lagrange-Based | 2026 | `eprint:2026/973` | read |
| KN-LIT-1556 | Atkin polynomials for families of abelian varieties with real multiplication | 2026 | `arxiv:2601.16944` | read |
| KN-LIT-1557 | Auditing Apple’s DifferentialPrivacy.framework: Implementation Bugs | 2026 | `arxiv:2605.21378` | read |
| KN-LIT-1558 | Auditing Privacy in Multi-Tenant RAG under Account Collusion | 2026 | `arxiv:2605.19847` | read |
| KN-LIT-1559 | AuditPay: Anonymous Payments with Controlled Oversight | 2026 | `eprint:2026/1118` | read |
| KN-LIT-156 | Non-constant Curves of Genus 2 with Infinite Pro-Galois Covers | 2003 | `arxiv:0312414` | read |
| KN-LIT-1560 | Author's version, accepted for the workshop “Test Methods and Reliability of Circuits and Systems” (TuZ-2026) Horizontal SCA Attacks on Binary kP Algorithms using Chevallier-Mames Atomic Blocks | 2026 | `arxiv:2604.22429` | read |
| KN-LIT-1561 | Author’s version; presented at the 4th Workshop on Nano Security (at the Design, Automation and Test in Europe Conference 2026) Preventing Distinguishability between | 2026 | `arxiv:2604.26536` | read |
| KN-LIT-1562 | AUTOMORPHISMS OF FINITE FIELDS FROM ISOGENY CYCLES | 2026 | `arxiv:2603.19428` | read |
| KN-LIT-1563 | Autonomous LLM-Orchestrated Side-Channel | 2026 | `eprint:2026/1085` | read |
| KN-LIT-1564 | AWARE: A Non-Interactive Anonymous Whistleblowing System against Recipient Corruption | 2026 | `eprint:2026/1046` | read |
| KN-LIT-1565 | Babel: Jailbreaking Safety Attention via Obfuscation | 2026 | `arxiv:2605.17971` | read |
| KN-LIT-1566 | Balanced and Adaptively Secure Asynchronous | 2026 | `eprint:2026/998` | read |
| KN-LIT-1567 | Batched Attribute-Based Encryption from Bilinear Pairings | 2026 | `eprint:2026/1454` | read |
| KN-LIT-1568 | Be Kind, Rewrite: Benign Projections via | 2026 | `arxiv:2605.19147` | read |
| KN-LIT-1569 | Better Usability: Leakage-Resistant AEADs from Single-length key Blockciphers (Full Version) | 2026 | `eprint:2026/824` | read |
| KN-LIT-157 | ON THE ARAKELOV THEORY OF ELLIPTIC CURVES | 2003 | `arxiv:0312359` | read |
| KN-LIT-1570 | Beyond Content: A Comprehensive Speech Toxicity Dataset and Detection Framework Incorporating Paralinguistic Cues | 2026 | `arxiv:2605.15984` | read |
| KN-LIT-1571 | Beyond Controlled Noise: Achieving Symmetric FHE through Dynamic Position Shifting | 2026 | `arxiv:2605.15774` | read |
| KN-LIT-1572 | Beyond the Anonymous Inbox: Secure Whistleblowing for All | 2026 | `eprint:2026/950` | read |
| KN-LIT-1573 | BIDO: A B IOMETRIC I DENTITY O NLINE AUTHENTICATION | 2026 | `arxiv:2605.16908` | read |
| KN-LIT-1574 | BIGNESS OF CANONICAL QUADRATIC POINTS ON CURVES OF GENUS | 2026 | `arxiv:2605.11888` | read |
| KN-LIT-1575 | Binary quadratic forms and elliptic curves with analytic rank one | 2026 | `arxiv:2607.18728` | read |
| KN-LIT-1576 | BOGOMOLOV PROPERTY FOR MODULAR GALOIS REPRESENTATIONS WITH NONTRIVIAL NEBENTYPUS | 2026 | `arxiv:2603.13523` | read |
| KN-LIT-1577 | Breaking ACDGV MinRank Gabidulin encryption schemes over matrix codes | 2026 | `eprint:2026/972` | read |
| KN-LIT-1578 | Bridging the Cybersecurity Gap Between Web2 and Web3 An Incident-Based Analysis of Organizational and Application-Level Security Failures | 2026 | `arxiv:2605.18484` | read |
| KN-LIT-1579 | BSD INVARIANTS AND MURMURATIONS OF ELLIPTIC CURVES | 2026 | `arxiv:2603.04604` | read |
| KN-LIT-158 | PRIMES IN THE DENOMINATORS OF IGUSA CLASS POLYNOMIALS | 2003 | `arxiv:0301240` | read |
| KN-LIT-1580 | Building Europe’s Quantum Shield: The Strategic view for a Continent-Wide | 2026 | `arxiv:2605.22332` | read |
| KN-LIT-1581 | BumbleBee: Best-of-Both-Worlds MVBA with Optimal | 2026 | `eprint:2026/989` | read |
| KN-LIT-1582 | Bypassing the Random-Probing Model in Masking Security Proofs | 2026 | `eprint:2026/288` | read |
| KN-LIT-1583 | Can Cross-Layer Design Bridge Security and Efficiency? A Robust Authentication Framework for Healthcare Information Exchange Systems Khalid M. Ezzat | 2026 | `arxiv:2604.26339` | read |
| KN-LIT-1584 | Can We Tolerate Small Side-Channel Leakages: The Role of Registers in Glitch-Stopping Circuits | 2026 | `eprint:2026/1011` | read |
| KN-LIT-1585 | Chain Reactions: How Nonce Collisions in ECDSA Compromise Polygon MEV Searchers | 2026 | `arxiv:2605.21498` | read |
| KN-LIT-15853c | Key-recovery side-channel attack on the Berlekamp-Massey decoding algorithm in the Classic McEliece KEM | 2025 | `eprint:2025/2043` | web |
| KN-LIT-1586 | CHASING RABBITS THROUGH HYPERCUBES: BETTER ALGORITHMS FOR HIGHER DIMENSIONAL 2-ISOGENY COMPUTATIONS AND MAX DUPARC | 2026 | `eprint:2026/114` | read |
| KN-LIT-1587 | Choose Wisely and Privately: Proactive Client Selection for Fair and Efficient Federated Learning | 2026 | `arxiv:2605.20975` | read |
| KN-LIT-1588 | Ciphertext-Updatable Attribute-Based and Predicate Encryption from Lattices | 2026 | `eprint:2026/1045` | read |
| KN-LIT-1589 | CLASSIFICATION OF THE RANK OF A CERTAIN FAMILY OF ELLIPTIC CURVES | 2026 | `arxiv:2607.16335` | read |
| KN-LIT-159 | PRYM VARIETIES AND FOURFOLD COVERS | 2003 | `arxiv:0303155` | read |
| KN-LIT-1590 | Coincident Poisson structures on principal-bundle moduli spaces | 2026 | `arxiv:2607.17433` | read |
| KN-LIT-1591 | COLLISION OF ORBITS ON AN ELLIPTIC SURFACE | 2026 | `arxiv:2602.10383` | read |
| KN-LIT-1592 | Collusion-Resistant Asymmetric Anamorphic Encryption: Framework, Generic Construction, and Concrete Instantiations | 2026 | `eprint:2026/1028` | read |
| KN-LIT-1593 | Comments on “Server-Aided Public Key Authenticated Searchable | 2026 | `eprint:2026/1015` | read |
| KN-LIT-1594 | Communication and Storage-Friendly | 2026 | `eprint:2026/054` | read |
| KN-LIT-1595 | Compact Quaternion Algorithms for SQIsign | 2026 | `eprint:2026/1031` | read |
| KN-LIT-1596 | Compile-time Security Analysis and Optimization of Sensitive | 2026 | `arxiv:2605.16561` | read |
| KN-LIT-1597 | COMPLETING THE CLASSIFICATION OF TORSION SUBGROUPS FOR RATIONAL ELLIPTIC CURVES OVER SEXTIC FIELDS | 2026 | `arxiv:2602.14718` | read |
| KN-LIT-1598 | COMPUTER VISION AND CONVERSE THEOREMS | 2026 | `arxiv:2604.15155` | read |
| KN-LIT-1599 | Computing Asymptotic Bounds for the Automated Coppersmith Method via Linear Programming | 2026 | `eprint:2026/1027` | read |
| KN-LIT-160 | SIEGEL MODULAR FORMS (MOD p) AND ALGEBRAIC MODULAR FORMS | 2003 | `arxiv:0306224` | read |
| KN-LIT-1600 | CoNAN: A Structure-Aware Framework for Lattice Cryptanalysis | 2026 | `eprint:2026/1041` | read |
| KN-LIT-1601 | Concave is the New Linear: The Impossibility of Anti-Plutocratic DAO Governance | 2026 | `arxiv:2605.18990` | read |
| KN-LIT-1602 | CONGRUENCES FOR TRACES OF SINGULAR MODULI AND HURWITZ - KRONECKER CLASS NUMBERS | 2026 | `arxiv:2602.19544` | read |
| KN-LIT-1603 | Constant-Online PVSS from CCA2-Secure Threshold Encryption: A Generic Framework | 2026 | `eprint:2026/1009` | read |
| KN-LIT-1604 | Constant-Size Issuer Hiding for BBS Credentials via Randomizable Keys | 2026 | `eprint:2026/369` | read |
| KN-LIT-1605 | CONSTRUCTING GENUS 2 CURVES WITH GIVEN REFINED | 2026 | `arxiv:2602.14319` | read |
| KN-LIT-1606 | Counting and recovering the quadratic relations of a vectorial function | 2026 | `eprint:2026/652` | read |
| KN-LIT-1607 | Cryptanalysis of the Subfield Bilinear Collision Problem | 2026 | `eprint:2026/916` | read |
| KN-LIT-1608 | Cryptographic Collateralized Loan without Smart Contracts | 2026 | `eprint:2026/1123` | read |
| KN-LIT-1609 | Current trends in AI-Aided Cryptography | 2026 | `eprint:2026/1006` | read |
| KN-LIT-161 | Special points on products of modular curves. Bas Edixhoven | 2003 | `arxiv:0302138` | read |
| KN-LIT-1610 | CURVES OF GENUS TWO WITH MAPS OF EVERY DEGREE TO A FIXED ELLIPTIC CURVE | 2026 | `arxiv:2601.19050` | read |
| KN-LIT-1611 | DARTIC: Decentralized Anonymous Reputation at Scale for Trustworthy Crowdsourcing arXiv:2605.18146v2 [cs.CR] 19 May 2026 Mouhamed Amine Bouchiha, Member, IEEE, Mourad Rabah, Ronan Champagnat, Abdelazi | 2026 | `arxiv:2605.18146` | read |
| KN-LIT-1612 | DDYF: Differential Dolev-Yao Fuzzing of Cryptographic Protocols | 2026 | `eprint:2026/991` | read |
| KN-LIT-1613 | Decentralized autonomous organization and blockchain-based incentivization framework for community-based facilities management | 2026 | `arxiv:2605.18773` | read |
| KN-LIT-1614 | Decision-Aware Quadratic ReLU Replacement for HE-Friendly Inference | 2026 | `arxiv:2605.22237` | read |
| KN-LIT-1615 | DEDEKIND ZETA FUNCTIONS OF NON-GALOIS TORSION FIELDS OF ELLIPTIC CURVES | 2026 | `arxiv:2604.08776` | read |
| KN-LIT-1616 | DeepProve: Verifiable End-to-End | 2026 | `eprint:2026/1112` | read |
| KN-LIT-1617 | Defining reduction types of curves via minimal regular and minimal normal crossings models Jakab Schrettner | 2026 | `arxiv:2607.16159` | read |
| KN-LIT-1618 | DELIGNE–LUSZTIG VARIETIES WHOSE CANONICAL DIVISORS HAVE NEGATIVITY | 2026 | `arxiv:2605.02522` | read |
| KN-LIT-1619 | Detecting Verbatim LLM Copy-Paste in Homework | 2026 | `arxiv:2605.16336` | read |
| KN-LIT-162 | THE p-PART OF TATE-SHAFAREVICH GROUPS OF ELLIPTIC CURVES | 2003 | `arxiv:0303143` | read |
| KN-LIT-1620 | DIOPHANTINE RANK STABILITY AND NON-VANISHING OF L-FUNCTIONS | 2026 | `arxiv:2606.31646` | read |
| KN-LIT-1621 | Distance-Preserving Digests: A Primitive for BFT Consensus | 2026 | `arxiv:2605.15329` | read |
| KN-LIT-1622 | DISTORTION MAPS FOR ELLIPTIC CURVES OVER FINITE FIELDS arXiv:2601.09904v1 [math.NT] 14 Jan 2026 NIKITA ANDRUSOV, SEVAG BÜYÜKSIMKEŞYAN, DIMITRIOS NOULAS, FABIEN PAZUKI | 2026 | `arxiv:2601.09904` | read |
| KN-LIT-1623 | Distributed Simon’s Algorithm with Less | 2026 | `eprint:2026/1001` | read |
| KN-LIT-1624 | DISTRIBUTION OF SELMER RANKS IN PRIME CYCLIC EXTENSIONS | 2026 | `arxiv:2607.01126` | read |
| KN-LIT-1625 | Distributions of Iwasawa λ-invariants of Zp -towers over supersingular isogeny graphs | 2026 | `arxiv:2605.23184` | read |
| KN-LIT-1626 | DIVISIBILITY BIASES IN THE ORDERS OF ELLIPTIC CURVE REDUCTIONS | 2026 | `arxiv:2606.25067` | read |
| KN-LIT-1627 | Doubly Aggregatable Signatures | 2026 | `eprint:2026/1042` | read |
| KN-LIT-1628 | Dr. Petar Radanliev | 2026 | `arxiv:2605.19755` | read |
| KN-LIT-1629 | Dynamic Elliptical Graph Factor Models via Riemannian Optimization with Geodesic Temporal Regularization | 2026 | `arxiv:2605.18316` | read |
| KN-LIT-163 | A CRT ALGORITHM FOR CONSTRUCTING GENUS 2 CURVES OVER FINITE FIELDS | 2004 | `arxiv:0405305` | read |
| KN-LIT-1630 | ECCFROG522PP: An Enhanced 522 bit Weierstrass | 2026 | `arxiv:2604.21261` | read |
| KN-LIT-1631 | Efficient and Parallel Implementation of Isogeny-based Deterministic Group Actions | 2026 | `eprint:2026/627` | read |
| KN-LIT-1632 | Eidolon: A Post-Quantum Signature Scheme Based on k-Colorability in the Age of Graph Neural Networks | 2026 | `eprint:2026/173` | read |
| KN-LIT-1633 | ELLIPTIC CURVES WITH RANK ONE AND NONTRIVIAL 2-PART OF TATE SHAFAREVICH GROUPS OVER THE Z2 -EXTENSION OF Q | 2026 | `arxiv:2603.14234` | read |
| KN-LIT-1634 | ELLIPTIC CURVES, FOURIER RATIO, AND SAMPLING COMPLEXITY | 2026 | `arxiv:2607.08051` | read |
| KN-LIT-1635 | Endomorphisms via splittings | 2026 | `eprint:2026/215` | read |
| KN-LIT-1636 | EXACT CLASSIFICATION OF ELLIPTIC CURVES y 2 = x3 − pqx WITH | 2026 | `arxiv:2607.14033` | read |
| KN-LIT-1637 | Exact Hidden Paths in Noisy High Dimensional Path Spaces | 2026 | `arxiv:2605.22477` | read |
| KN-LIT-1638 | Exact output statistics of Icart’s encoding in the exceptional j = 0 case | 2026 | `arxiv:2606.07390` | read |
| KN-LIT-1639 | EXCEPTIONAL RATIONAL FUNCTIONS OF DEGREE 5 OVER FINITE FIELDS: CLASSIFICATION BY MONODROMY | 2026 | `arxiv:2607.05075` | read |
| KN-LIT-164 | A double large prime variation for small genus hyperelliptic index calculus | 2004 | `eprint:2004/153` | read |
| KN-LIT-1640 | EXCEPTIONAL SETS FOR CERTAIN 2 F1 HYPERGEOMETRIC FUNCTIONS | 2026 | `arxiv:2607.16331` | read |
| KN-LIT-1641 | EXISTENCE AND NON-EXISTENCE OF RATIONAL ELLIPTIC CURVES WITH PRESCRIBED TORSION SUBGROUPS OVER QUADRATIC FIELDS | 2026 | `arxiv:2602.07723` | read |
| KN-LIT-1642 | Expander properties of superspecial isogeny digraphs with level structure | 2026 | `eprint:2026/500` | read |
| KN-LIT-1643 | Explicit cost analysis of Toom-4 multiplication for incomplete NTT in lattice-based cryptography | 2026 | `eprint:2026/971` | read |
| KN-LIT-1644 | EXPLICIT p-ADIC HODGE THEORY FOR ELLIPTIC CURVES AND NON-SPLIT | 2026 | `arxiv:2603.04021` | read |
| KN-LIT-1645 | Exploiting Strong Key Bridges: Full-Fledged | 2026 | `eprint:2026/1110` | read |
| KN-LIT-1646 | Fast Difficulty Adjustment in Proof-of-Work Consensus | 2026 | `eprint:2026/1116` | read |
| KN-LIT-1647 | Fast Isogeny Evaluation on Binary Curves | 2026 | `eprint:2026/704` | read |
| KN-LIT-1648 | Faster CoeffToSlot and SlotToCoeff for Sparsely Packed Ciphertexts with Application to CKKS Bootstrapping | 2026 | `eprint:2026/1023` | read |
| KN-LIT-1649 | Faster Isogeny Group Action for Post-Quantum NIKE | 2026 | `eprint:2026/896` | read |
| KN-LIT-165 | ANTICYCLOTOMIC IWASAWA THEORY OF CM ELLIPTIC CURVES II | 2004 | `arxiv:0401124` | read |
| KN-LIT-1650 | Faster NTRU-based Bootstrapping with | 2026 | `eprint:2026/1447` | read |
| KN-LIT-1651 | Faster Polynomial Evaluations for SIMD FHEs and Application to BGV in HElib | 2026 | `eprint:2026/1089` | read |
| KN-LIT-1652 | Faster Pseudorandom Correlation Generators via Walsh-Hadamard Transform | 2026 | `eprint:2026/196` | read |
| KN-LIT-1653 | Fault Injection Attacks Against zkSTARKs | 2026 | `eprint:2026/835` | read |
| KN-LIT-1654 | FedEDAuth - Federated Embedding Distribution Authentication for Counterfeit IC Detection | 2026 | `arxiv:2605.15885` | read |
| KN-LIT-1655 | Fifty Shades of Darknet | 2026 | `arxiv:2605.19437` | read |
| KN-LIT-1656 | Finding Missing Input Validation in TEEs via LLM-Assisted | 2026 | `arxiv:2605.22058` | read |
| KN-LIT-1657 | Finding Random Collisions for Random Degree-2 Functions | 2026 | `eprint:2026/1044` | read |
| KN-LIT-1658 | FINDING THE COMPLEMENT OF AN ELLIPTIC CURVE | 2026 | `arxiv:2606.02429` | read |
| KN-LIT-1659 | Finite-Field Arithmetic in CKKS | 2026 | `eprint:2026/1102` | read |
| KN-LIT-166 | BOUNDS FOR TORSION ON ABELIAN VARIETIES WITH INTEGRAL MODULI PETE L. CLARK | 2004 | `arxiv:0407264` | read |
| KN-LIT-1660 | Finiteness for Étale Fundamental Groups of Néron Models | 2026 | `arxiv:2607.00232` | read |
| KN-LIT-1661 | Frequency-Domain Regularized Adversarial Alignment for Transferable Attacks against Closed-Source MLLMs | 2026 | `arxiv:2605.21541` | read |
| KN-LIT-1662 | FROM ORIENTATIONS TO l-ADIC PERIOD VECTORS | 2026 | `arxiv:2603.29789` | read |
| KN-LIT-1663 | Frontdoors, Not Backdoors: Accountable Anonymity for National | 2026 | `eprint:2026/389` | read |
| KN-LIT-1664 | Functional Bootstrapping for a Single LWE Ciphertext with Õ(1) Polynomial Multiplications | 2026 | `eprint:2026/975` | read |
| KN-LIT-1665 | GALOIS REPRESENTATION OF THE PRODUCT OF TWO DRINFELD MODULES OF GENERIC CHARACTERISTIC | 2026 | `arxiv:2603.27710` | read |
| KN-LIT-1666 | GENERALIZED FERMAT EQUATION OVER CYCLOTOMIC Zl -EXTENSIONS OF TOTALLY REAL FIELDS | 2026 | `arxiv:2605.20860` | read |
| KN-LIT-1667 | GENERALIZED FRUIT DIOPHANTINE EQUATION AND SUPER | 2026 | `arxiv:2602.01001` | read |
| KN-LIT-1668 | Generalized Howe curves of genus 4, 5, and 6 with completely decomposable Jacobians | 2026 | `arxiv:2604.18074` | read |
| KN-LIT-1669 | Genus one correspondence between tropical and algebraic curves | 2026 | `arxiv:2607.06426` | read |
| KN-LIT-167 | Common Divisors of Elliptic Divisibility Sequences over Function Fields | 2004 | `arxiv:0402016` | read |
| KN-LIT-1670 | GEOMETRIC CONSTRUCTION OF MODULAR POLYNOMIALS WITH LEVEL STRUCTURES | 2026 | `arxiv:2601.17338` | read |
| KN-LIT-1671 | Geometric Critical Point Screening: Clustering-Free Cryptanalytic Extraction of Neural Network Models | 2026 | `eprint:2026/1025` | read |
| KN-LIT-1672 | Geometry-of-numbers methods over global fields II: Coregular representations | 2026 | `arxiv:2604.16978` | read |
| KN-LIT-1673 | Graph Structure of Chebyshev Permutation Polynomials over Binary and Ternary Adic Rings | 2026 | `arxiv:2605.21819` | read |
| KN-LIT-1674 | Graphical Abstract Quantum and Post-Quantum Blockchain: A Systematic Survey | 2026 | `eprint:2026/1017` | read |
| KN-LIT-1675 | GROSS-ZAGIER FORMULA FOR THE 4, 7 CASES OF SYLVESTER’S CONJECTURE | 2026 | `arxiv:2607.01744` | read |
| KN-LIT-1676 | Guess-and-Determine Rebound Revisited: Full Quantum Collision Attack on AES-256 in DM Hash Mode | 2026 | `eprint:2026/1050` | read |
| KN-LIT-1677 | Heartbeat-Bound Hierarchical Credentials: Cryptographic Revocation for AI Agent Swarms | 2026 | `arxiv:2605.20704` | read |
| KN-LIT-1678 | HEIGHT MODULI OF ELLIPTIC SURFACES: MOTIVIC | 2026 | `arxiv:2601.15543` | read |
| KN-LIT-1679 | HENSEL MINIMALITY, p-ADIC EXPONENTIATION AND TATE UNIFORMIZATION | 2026 | `arxiv:2602.16433` | read |
| KN-LIT-168 | COMPLEX MULTIPLICATION TESTS FOR ELLIPTIC CURVES | 2004 | `arxiv:0409501` | read |
| KN-LIT-1680 | HIGHER FITTING IDEALS AND THE STRUCTURE OF ANTICYCLOTOMIC SHAFAREVICH–TATE GROUPS | 2026 | `arxiv:2603.12357` | read |
| KN-LIT-1681 | Highlights Image Encryption via DataIdentified Discrete Chaotic Maps | 2026 | `arxiv:2605.21118` | read |
| KN-LIT-1682 | Hodge Loci and Complex Multiplication via Generalized Symmetries in Calabi-Yau sigma models | 2026 | `arxiv:2605.30418` | read |
| KN-LIT-1683 | How to Authenticate a Non-Deterministic Computation | 2026 | `eprint:2026/741` | read |
| KN-LIT-1684 | HRA-Secure Lattice-based Proxy Re-Encryption without Noise Flooding | 2026 | `eprint:2026/1113` | read |
| KN-LIT-1685 | IACR Transactions on Cryptographic Hardware and Embedded Systems | 2026 | `eprint:2026/1462` | read |
| KN-LIT-1686 | IACR Transactions on Symmetric Cryptology | 2026 | `eprint:2026/176` | read |
| KN-LIT-1687 | Identity-Based Encryption from Isogenies | 2026 | `eprint:2026/1457` | read |
| KN-LIT-1688 | Identity-Based Revocable and Linkable Ring Signature | 2026 | `eprint:2026/1111` | read |
| KN-LIT-1689 | Impact of Post-Quantum Signatures on InnoDB | 2026 | `eprint:2026/987` | read |
| KN-LIT-169 | COMPUTING MODULAR POLYNOMIALS | 2004 | `arxiv:0408051` | read |
| KN-LIT-1690 | Improved Dual Attack and Trapdoor Sampling via Quantum Rejection Sampling | 2026 | `eprint:2026/979` | read |
| KN-LIT-1691 | Improving Skipping Fault Correction | 2026 | `eprint:2026/1448` | read |
| KN-LIT-1692 | INCIDENCE OBSTRUCTIONS FOR POWER PRODUCTS IN ELLIPTIC DIVISIBILITY SEQUENCES arXiv:2605.25797v1 [math.NT] 25 May 2026 DONGYEON KYM | 2026 | `arxiv:2605.25797` | read |
| KN-LIT-1693 | Information-Theoretic Optimistic Verifiable Secret Sharing | 2026 | `eprint:2026/1000` | read |
| KN-LIT-1694 | INSEPARABLE ENDOMORPHISMS AND RANK-2 SUBLATTICES OF THE GROSS LATTICE | 2026 | `arxiv:2602.05284` | read |
| KN-LIT-1695 | Internal Post-Quantum Discovery as a Governance Capability: Evidence-Based Cryptographic | 2026 | `arxiv:2605.16549` | read |
| KN-LIT-1696 | INTRINSIC SUBGROUPS AND THE l-ADIC GALOIS IMAGE | 2026 | `arxiv:2606.01571` | read |
| KN-LIT-1697 | INTRODUCTION TO DIEUDONNÉ MODULES AND SUPERSINGULAR ABELIAN VARIETIES REVISITED | 2026 | `arxiv:2603.11506` | read |
| KN-LIT-1698 | IOP Publishing Journal vv (yyyy) aaaaaa | 2026 | `arxiv:2604.12985` | read |
| KN-LIT-1699 | Is PSI Really Faster Than PSU? Achieving Efficient PSU with Invertible Bloom Filters | 2026 | `eprint:2026/376` | read |
| KN-LIT-170 | DIOPHANTINE DEFINABILITY OF INFINITE DISCRETE | 2004 | `arxiv:0408271` | read |
| KN-LIT-1700 | ITEP-TH-14/26 Integrable hierarchies with zero dispersion and elliptic curves | 2026 | `arxiv:2606.01354` | read |
| KN-LIT-1701 | IWASAWA INVARIANTS OF SHARP/FLAT 2-ADIC L-FUNCTIONS FOR QUADRATIC TWISTS OF ELLIPTIC CURVES | 2026 | `arxiv:2607.05305` | read |
| KN-LIT-1702 | IWASAWA MAIN CONJECTURE FOR ORDINARY SEMISTABLE ELLIPTIC CURVES OVER GLOBAL FUNCTION FIELDS | 2026 | `arxiv:2603.11615` | read |
| KN-LIT-1703 | IWASAWA THEORY FOR K3 SURFACES OVER FINITE FIELDS | 2026 | `arxiv:2606.25737` | read |
| KN-LIT-1704 | Jevil: A Catastrophic-Failure-by-Design | 2026 | `eprint:2026/1103` | read |
| KN-LIT-1705 | Jindo: Practical Lattice-Based Polynomial Commitments for Client-Side Proving | 2026 | `eprint:2026/044` | read |
| KN-LIT-1706 | JOINT SATO-TATE LAWS FOR TRANSFORMATIONS OF HECKE EIGENVALUES: THE VERTICAL CASE | 2026 | `arxiv:2604.24753` | read |
| KN-LIT-1707 | Kardashev scale Quantum Computing for Bitcoin Mining | 2026 | `arxiv:2603.25519` | read |
| KN-LIT-1708 | KAT-Seeded Fuzzing of Stateful Hash-Based Signature Verification in liboqs | 2026 | `eprint:2026/1107` | read |
| KN-LIT-1709 | Key Encapsulation Mechanism-Based Integrated Encryption Scheme (KEM-IES) | 2026 | `arxiv:2605.10175` | read |
| KN-LIT-171 | Do All Elliptic Curves of the Same Order Have the Same Difficulty of Discrete Log? | 2004 | `arxiv:0411378` | read |
| KN-LIT-1710 | Key-Independent Secret-Key Distinguisher for 7-Round AES based on the Joint Generalized Zero-Difference Property | 2026 | `eprint:2026/980` | read |
| KN-LIT-1711 | KODAIRA-NERON STATISTICS FOR RATIONAL ELLIPTIC | 2026 | `arxiv:2605.14226` | read |
| KN-LIT-1712 | Labeled Multi-Key Batched IBE | 2026 | `eprint:2026/1452` | read |
| KN-LIT-1713 | Lang-Trotter phenomena and unlikely intersections | 2026 | `arxiv:2605.00759` | read |
| KN-LIT-1714 | Latent Geometry as a Structural Monitor: Eigenspace Alignment for Anomaly Detection in Anonymity Networks | 2026 | `arxiv:2605.20391` | read |
| KN-LIT-1715 | Lightweight Hardware Accelerator for the UOV Signature Scheme with Oil Space Blinding | 2026 | `eprint:2026/1451` | read |
| KN-LIT-1716 | Linear self-equivalence of the known families of APN functions: a unified point of view | 2026 | `eprint:2026/1012` | read |
| KN-LIT-1717 | Local Constraints Behind Fourier Analysis of Neural Distinguishers for SPECK32/64 | 2026 | `eprint:2026/1136` | read |
| KN-LIT-1718 | LOCAL MONODROMY OF UNIT ROOT F-ISOCRYSTALS FROM SHIMURA VARIETIES | 2026 | `arxiv:2607.10054` | read |
| KN-LIT-1719 | LOCAL TRANSITIVITY AND ENTANGLEMENT OBSTRUCTIONS FOR PRIMITIVE POINTS | 2026 | `arxiv:2601.17559` | read |
| KN-LIT-172 | Elliptic curves and Hilbert’s tenth problem for algebraic function fields over real and p-adic fields | 2004 | `arxiv:0409103` | read |
| KN-LIT-1720 | Locally Conformally Kähler Manifolds of Algebraic Codimension One | 2026 | `arxiv:2606.27754` | read |
| KN-LIT-1721 | Locally recoverable codes from elliptic surfaces with availability and hierarchical locality | 2026 | `arxiv:2605.28460` | read |
| KN-LIT-1722 | Locally Repairable Codes with Availability via Elliptic Function Fields | 2026 | `arxiv:2605.06182` | read |
| KN-LIT-1723 | LoTRS: Practical Post-Quantum Structured Threshold Ring Signatures from Lattices | 2026 | `eprint:2026/974` | read |
| KN-LIT-1724 | Low-Depth Bootstrapping for Matrix-Native FHE | 2026 | `eprint:2026/811` | read |
| KN-LIT-1725 | LymphNode: A Plug-and-Play Access Control Method for Deep Neural Networks | 2026 | `arxiv:2605.16227` | read |
| KN-LIT-1726 | Lynx: Symmetric Primitive for Shorter and Faster VOLE-in-the-Head Signatures | 2026 | `eprint:2026/1099` | read |
| KN-LIT-1727 | MAGIQ: A Post-Quantum Multi-Agentic AI Governance System with Provable Security | 2026 | `arxiv:2605.06933` | read |
| KN-LIT-1728 | Maskaglia: A New, Efficient Approach to Masked Discrete | 2026 | `eprint:2026/988` | read |
| KN-LIT-1729 | MDSS-STAR: Private Heavy-Hitters through Multi-Dealer Secret Sharing | 2026 | `eprint:2026/747` | read |
| KN-LIT-173 | Elliptic Curves x3 + y 3 = k of High Rank | 2004 | `arxiv:0403116` | read |
| KN-LIT-1730 | Measurement Study of Post-Quantum Readiness of Internet: 2026 | 2026 | `arxiv:2606.16473` | read |
| KN-LIT-1731 | Microbenchmarking Cloud Cryptographic Workloads for Privacy-Preserving Healthcare IoT | 2026 | `arxiv:2605.24063` | read |
| KN-LIT-1732 | MINIMAL DEGREE OF AN ISOGENY BETWEEN A SUPERSINGULAR ELLIPTIC | 2026 | `arxiv:2607.14624` | read |
| KN-LIT-1733 | MINIMAL TRIVIALIZING ISOGENIES FOR Gm -GERBES OVER ABELIAN | 2026 | `arxiv:2605.30530` | read |
| KN-LIT-1734 | Minimizing Mempool Dependency in PoW Mining on Blockchain: A Paradigm Shift with Compressed Block Representation for | 2026 | `eprint:2026/141` | read |
| KN-LIT-1735 | MIPSBLEED: Uncovering Microarchitectural Timing Leaks in Pervasive Embedded Processors | 2026 | `arxiv:2606.16372` | read |
| KN-LIT-1736 | Miraidon: MinRank Identification | 2026 | `eprint:2026/997` | read |
| KN-LIT-1737 | MOCK MODULARITY OF LOG GROMOV–WITTEN INVARIANTS: THE MIRROR TO P2 arXiv:2602.08153v1 [math.AG] 8 Feb 2026 HÜLYA ARGÜZ | 2026 | `arxiv:2602.08153` | read |
| KN-LIT-1738 | Modern Portfolio Theory in the Crypto-Wilderness Ivan Vynyavskyy # | 2026 | `eprint:2026/999` | read |
| KN-LIT-1739 | MODULAR CURVES AND BAD REDUCTION | 2026 | `arxiv:2604.09536` | read |
| KN-LIT-174 | Endomorphism Rings and Isogenies Classes for Drinfeld A-Modules of Rank 2 over Finite Fields | 2004 | `arxiv:0412367` | read |
| KN-LIT-1740 | MODULAR ELLIPTIC CURVES AND HYPERBOLIC UNIFORMIZATION | 2026 | `arxiv:2607.03830` | read |
| KN-LIT-1741 | Modular invariance of characters of quasi-lisse vertex algebras | 2026 | `arxiv:2605.29921` | read |
| KN-LIT-1742 | Module Lattice Security (Part III): Structured CVP Distance on the Log-Unit Lattice | 2026 | `arxiv:2605.17404` | read |
| KN-LIT-1743 | Module Lattice Security (Part IV): Probabilistic Polynomial Quantum Attack on Module-LWE over 2-Power Cyclotomics | 2026 | `arxiv:2605.17412` | read |
| KN-LIT-1744 | Module Learning With Errors and Structured | 2026 | `eprint:2026/155` | read |
| KN-LIT-1745 | MODULI OF HIGGS BUNDLES OVER THE TWO PUNCTURED | 2026 | `arxiv:2602.15179` | read |
| KN-LIT-1746 | MODULI OF PARABOLIC BUNDLES ON AN ELLIPTIC CURVE | 2026 | `arxiv:2605.25087` | read |
| KN-LIT-1747 | MODULI SPACE OF GENUS ONE CURVES ON QUARTIC AND QUINTIC DEL | 2026 | `arxiv:2606.00876` | read |
| KN-LIT-1748 | MONSKY MATRIX AND 2-SELMER RANK | 2026 | `arxiv:2604.26183` | read |
| KN-LIT-1749 | MORDELL CURVES WITH ORDINATES IN ARITHMETIC PROGRESSION | 2026 | `arxiv:2607.06998` | read |
| KN-LIT-175 | Entropic Security and the Encryption of High Entropy Messages? | 2004 | `eprint:2004/219` | read |
| KN-LIT-1750 | More from Less: Composable General Multi-Party Computation with Global Public Verifiability from a Single Enclave Only Saskia Bayreuther , Robin Berger , Felix Dörre , Eva Hetzel , Yufan Jiang | 2026 | `eprint:2026/1005` | read |
| KN-LIT-1751 | Multi-key Fully Homomorphic Encryption with Non-Interactive Setup in the Plain Model | 2026 | `eprint:2026/322` | read |
| KN-LIT-1752 | Multi-target hyperbolic sieves and elliptic trace obstructions | 2026 | `arxiv:2606.13018` | read |
| KN-LIT-1753 | MultiBallot: Verifiable and privacy-preserving E-Collecting in the Swiss setting | 2026 | `arxiv:2605.19312` | read |
| KN-LIT-1754 | MULTILINEAR POLYNOMIALS VIA TREE-BASED CIRCUIT AND THE SUMCHECK PROTOCOL | 2026 | `eprint:2026/1469` | read |
| KN-LIT-1755 | MURMURATIONS OF ELLIPTIC CURVES OVER FUNCTION FIELDS | 2026 | `arxiv:2603.13802` | read |
| KN-LIT-1756 | MURMURATIONS, MESTRE–NAGAO SUMS, AND CONVOLUTIONAL NEURAL NETWORKS FOR ELLIPTIC CURVES arXiv:2603.17681v1 [math.NT] 18 Mar 2026 JOANNA BIERI, EDGAR COSTA, ALYSON DEINES, KYU-HWAN LEE, DAVID LOWRY-DUDA | 2026 | `arxiv:2603.17681` | read |
| KN-LIT-1757 | n-ARY ELLIPTIC GROUPS, RINGS, AND PRIMES IN ARITHMETIC PROGRESSIONS | 2026 | `arxiv:2605.16974` | read |
| KN-LIT-1758 | New Constructions of Functional Adaptor Signatures: | 2026 | `eprint:2026/1124` | read |
| KN-LIT-1759 | New Quantum Circuits for ECDLP: Breaking Prime Elliptic Curve Cryptography | 2026 | `eprint:2026/106` | read |
| KN-LIT-176 | EXPLICIT DESCENT VIA 4-ISOGENY ON AN ELLIPTIC CURVE | 2004 | `arxiv:0411215` | read |
| KN-LIT-1760 | New X -Secure T -Private Information Retrieval Schemes via Rational Curves and Hermitian Curves | 2026 | `arxiv:2601.07676` | read |
| KN-LIT-1761 | NON-VANISHING FOR QUARTIC HECKE L-FUNCTIONS AND RANKS OF ELLIPTIC CURVES | 2026 | `arxiv:2604.01316` | read |
| KN-LIT-1762 | NON-VANISHING OF THE p-ADIC CONSTANT FOR MOCK MODULAR FORMS ASSOCIATED TO A NEWFORM WITH REAL FOURIER COEFFICIENTS | 2026 | `arxiv:2604.20520` | read |
| KN-LIT-1763 | NONCOMPACT IWASAWA FACTORIZATION AND TRANSLATIONALLY EQUIVARIANT HYPERBOLIC AFFINE SPHERES | 2026 | `arxiv:2607.07285` | read |
| KN-LIT-1764 | NONTRIVIAL TORSION IN THE TATE–SHAFAREVICH GROUP OF | 2026 | `arxiv:2602.19861` | read |
| KN-LIT-1765 | Oblivious Garbling and its Applications | 2026 | `eprint:2026/1132` | read |
| KN-LIT-1766 | Oblivious Single Access Machines are Concretely Efficient Sage Pia UConn | 2026 | `eprint:2026/451` | read |
| KN-LIT-1767 | Obscura: Privacy-Preserving Protocol for the Algorand Blockchain Using LSAG Ring Signatures | 2026 | `arxiv:2605.02077` | read |
| KN-LIT-1768 | ON A CONJECTURE OF DEINES | 2026 | `arxiv:2604.07295` | read |
| KN-LIT-1769 | On discrepancy estimates for pseudorandom vectors constructed by the elliptic curve congruential generator 1,2 | 2026 | `arxiv:2605.20627` | read |
| KN-LIT-177 | GENERALISED EULER CHARACTERISTICS OF SELMER GROUPS | 2004 | `arxiv:0404431` | read |
| KN-LIT-1770 | ON GALOIS EMBEDDING PROBLEMS ARISING FROM 3-TORSION OF ELLIPTIC CURVES | 2026 | `arxiv:2605.13590` | read |
| KN-LIT-1771 | ON GRADED LIE ALGEBRAS ASSOCIATED TO ONCE-PUNCTURED ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2026 | `arxiv:2602.00615` | read |
| KN-LIT-1772 | On Iwasawa theory of abelian varieties over Z2p-extension with | 2026 | `arxiv:2604.05739` | read |
| KN-LIT-1773 | ON PERIODS OF ELLIPTIC CURVES | 2026 | `arxiv:2606.02254` | read |
| KN-LIT-1774 | On Publicly Verifiable Tokens in Group Signatures with Message-Dependent Opening | 2026 | `eprint:2026/1037` | read |
| KN-LIT-1775 | On QC and GQC algebraic geometry codes | 2026 | `arxiv:2602.05097` | read |
| KN-LIT-1776 | On the Absolute Geometry of Spec Z and the Fargues-Fontaine curve | 2026 | `arxiv:2606.06604` | read |
| KN-LIT-1777 | On the coefficients of the Taylor expansion of L-functions of elliptic curves | 2026 | `arxiv:2605.09251` | read |
| KN-LIT-1778 | On the conversion of module representations for higher dimensional supersingular isogenies | 2026 | `eprint:2026/276` | read |
| KN-LIT-1779 | ON THE DENSITY OF COPRIME REDUCTIONS OF ELLIPTIC CURVES | 2026 | `arxiv:2603.24915` | read |
| KN-LIT-178 | Images of isogeny classes on modular elliptic curves | 2004 | `arxiv:0407336` | read |
| KN-LIT-1780 | ON THE FINITE TRANSCENDENCE OF FROBENIUS TRACES FOR ABELIAN VARIETIES OVER Q | 2026 | `arxiv:2605.17674` | read |
| KN-LIT-1781 | On the Formal Verification of Authenticated Encryption of the MQTT Protocol | 2026 | `eprint:2026/1020` | read |
| KN-LIT-1782 | On the Geometric Limits of Transformer Defenses against Obfuscation Attacks: Latent Embedding Collapse & Performance–Robustness Gap | 2026 | `arxiv:2605.19159` | read |
| KN-LIT-1783 | ON THE IDENTIFICATION OF ELLIPTIC CURVES THAT ADMIT INFINITELY MANY TWISTS SATISFYING THE BIRCH–SWINNERTON-DYER CONJECTURE | 2026 | `arxiv:2601.16044` | read |
| KN-LIT-1784 | ON THE INFINITUDE OF ELLIPTIC CURVES OVER A NUMBER FIELD WITH PRESCRIBED SMALL RANK arXiv:2602.10865v1 [math.NT] 11 Feb 2026 DAVID ZYWINA | 2026 | `arxiv:2602.10865` | read |
| KN-LIT-1785 | On the Maximal Length of MDS Elliptic Codes | 2026 | `arxiv:2605.29439` | read |
| KN-LIT-1786 | ON THE MH (G)-PROPERTY FOR SELMER GROUPS AT SUPERSINGULAR REDUCTION | 2026 | `arxiv:2601.08612` | read |
| KN-LIT-1787 | ON THE NUMBER OF FROBENIUS PERIODIC VECTOR BUNDLES ON ELLIPTIC CURVES | 2026 | `arxiv:2607.04340` | read |
| KN-LIT-1788 | ON THE RAMANUJAN VECTOR FIELD MODULO P | 2026 | `arxiv:2602.20109` | read |
| KN-LIT-1789 | On the Secrecy of the Encapsulation Coin in ML-KEM | 2026 | `eprint:2026/1117` | read |
| KN-LIT-179 | Iwasawa Theory of Elliptic Curves at Supersingular Primes over Zp-extensions of Number Fields | 2004 | `arxiv:0411496` | read |
| KN-LIT-1790 | On the Security of Public Key Authenticated Encryption with Keyword Search with Sender-independent Search Complexity | 2026 | `eprint:2026/1019` | read |
| KN-LIT-1791 | ON THE VISIBILITY CATEGORY OF THE SHAFAREVICH–TATE GROUP | 2026 | `arxiv:2601.21519` | read |
| KN-LIT-1792 | ON Up -CONGRUENCES FOR MEROMORPHIC MODULAR FORMS VIA SUPERSINGULARITY | 2026 | `arxiv:2606.14020` | read |
| KN-LIT-1793 | On weak keys of POKÉ | 2026 | `eprint:2026/1002` | read |
| KN-LIT-1794 | Onion-Routed Multi-Circuit Key Establishment for Quantum-Resilient Sessions | 2026 | `arxiv:2605.21349` | read |
| KN-LIT-1795 | Operationalising Post-Quantum TLS: Automated | 2026 | `arxiv:2605.17955` | read |
| KN-LIT-1796 | Optimal Distributed Monotone-Policy Encryption for DNFs and More from Lattices | 2026 | `eprint:2026/1464` | read |
| KN-LIT-1797 | Optimized Point Addition Circuits for Elliptic | 2026 | `eprint:2026/1128` | read |
| KN-LIT-1798 | Optimizing Polynomial Multiplication and | 2026 | `eprint:2026/1450` | read |
| KN-LIT-1799 | ORDINARY ABELIAN VARIETIES: ISOGENY GRAPHS AND POLARIZATIONS | 2026 | `arxiv:2601.20979` | read |
| KN-LIT-17d46b | Asymptotic analysis of probabilistic algorithms for finding short codewords | 1992 | `doi:10.1007/978-3-7091-2786-5_15` | web |
| KN-LIT-180 | Lucas sequences whose 8th term is a square | 2004 | `arxiv:0408371` | read |
| KN-LIT-1800 | p-ADIC ELLIPTIC POLYLOGARITHMS AND CUBIC CHABAUTY | 2026 | `arxiv:2604.20662` | read |
| KN-LIT-1801 | p-ADIC L-FUNCTIONS FOR ELLIPTIC CURVES OVER GLOBAL | 2026 | `arxiv:2603.10576` | read |
| KN-LIT-1802 | p-ADIC PROPERTIES OF TRANSLATED DIVISION | 2026 | `arxiv:2607.11261` | read |
| KN-LIT-1803 | Packed Pre-Constructed PVSS for Randomness Generation and E-Voting | 2026 | `eprint:2026/1119` | read |
| KN-LIT-1804 | PATTERNS ON ELLIPTIC CURVES BEYOND BREMNER’S CONJECTURE | 2026 | `arxiv:2605.14962` | read |
| KN-LIT-1805 | PERFECT POWERS IN THE PRODUCT OF DENOMINATORS OF ELLIPTIC CURVES | 2026 | `arxiv:2606.00466` | read |
| KN-LIT-1806 | Performance Analysis of Quantum-Secure Digital | 2026 | `arxiv:2601.17785` | read |
| KN-LIT-1807 | PIKE: Faster Isogeny-Based Public Key Encryption with Pairing-Assisted Decryption | 2026 | `eprint:2026/473` | read |
| KN-LIT-1808 | Plectic Heegner classes | 2026 | `arxiv:2603.28327` | read |
| KN-LIT-1809 | PQKryvos: Post-Quantum Secure E-Voting With Flexible Ballot | 2026 | `eprint:2026/1004` | read |
| KN-LIT-181 | MODULAR PARAMETRIZATIONS OF NEUMANN–SETZER ELLIPTIC CURVES | 2004 | `arxiv:0404333` | read |
| KN-LIT-1810 | Practical Amortized Bootstrapping for NTRU-Based FHE | 2026 | `eprint:2026/068` | read |
| KN-LIT-1811 | Privacy Coins Under Viewing Key Compromise | 2026 | `eprint:2026/872` | read |
| KN-LIT-1812 | Privacy is Fungibility: Why Endogenous Tokens Are Not Money | 2026 | `arxiv:2605.15934` | read |
| KN-LIT-1813 | Privacy-Preserving Distributed Optimization Under Time | 2026 | `arxiv:2605.20944` | read |
| KN-LIT-1814 | Private Information Retrieval: A Tutorial and Survey | 2026 | `eprint:2026/1135` | read |
| KN-LIT-1815 | Profiling-Device-Free SASCA Framework for ML-KEM | 2026 | `eprint:2026/981` | read |
| KN-LIT-1816 | Prompts Don’t Protect: Architectural Enforcement via MCP Proxy for LLM Tool Access Control | 2026 | `arxiv:2605.18414` | read |
| KN-LIT-1817 | PRYM-BRILL-NOETHER THEORY FOR GENERAL COVERS | 2026 | `arxiv:2607.01173` | read |
| KN-LIT-1818 | Pseudo-Oil Subspaces and the Geometry of Underdetermined MQ Problems | 2026 | `eprint:2026/1122` | read |
| KN-LIT-1819 | Pseudonym Scheme Based on Hybrid Certificates for Security Credential Management System in Vehicular Communications | 2026 | `arxiv:2606.14008` | read |
| KN-LIT-182 | ON ELEMENTARY EQUIVALENCE, ISOMORPHISM AND ISOGENY OF ARITHMETIC FUNCTION FIELDS | 2004 | `arxiv:0406133` | read |
| KN-LIT-1820 | pSquare-hash: A Family of Tweakable Hash Functions for Physically Secure PQ Signatures | 2026 | `eprint:2026/1129` | read |
| KN-LIT-1821 | Public Key Encryption Secure Against Quantum Leakage | 2026 | `eprint:2026/1131` | read |
| KN-LIT-1822 | Public-Decay Homomorphic State Space Models for Private | 2026 | `arxiv:2605.16647` | read |
| KN-LIT-1823 | Pushforward Problems and Applications to Isogeny-based Cryptography | 2026 | `eprint:2026/1030` | read |
| KN-LIT-1824 | Pushing Collision Attacks on SHA-2 to 39 Steps | 2026 | `eprint:2026/1120` | read |
| KN-LIT-1825 | Pushing the boundaries of group-based aggregation with zero-evading generators of low additive complexity | 2026 | `eprint:2026/1148` | read |
| KN-LIT-1826 | QT-PUF: Quantum Tunneling Leakage Based PUF for Implantable IoMT Devices | 2026 | `arxiv:2605.22113` | read |
| KN-LIT-1827 | Quantum algorithm for Discrete Gaussian Sampling | 2026 | `eprint:2026/984` | read |
| KN-LIT-1828 | Quantum Circuit Implementation and Grover’s Search on the Lightweight Block Cipher KLEIN Family Indranil Mukherjee , Ranit Dutta , Bhupendra Singh | 2026 | `eprint:2026/1007` | read |
| KN-LIT-1829 | Quantum Circuit Optimization with LLMs under a Structured Guideline | 2026 | `eprint:2026/1446` | read |
| KN-LIT-182bfb | Asymptotics and improvements of sieving for codes | 2024 | `eprint:2023/1577` | web |
| KN-LIT-183 | ON THE CORRESPONDECE BETWEEN SUPERSINGULAR | 2004 | `arxiv:0404538` | read |
| KN-LIT-1830 | Quantum Futures Interactive: A Live Demonstration of Post-Quantum Blockchain Security, Infrastructure | 2026 | `arxiv:2605.15991` | read |
| KN-LIT-1831 | Quantum Horizon An evaluation of quantum computing as a threat to Bitcoin and Ethereum arXiv:2606.14484v1 [quant-ph] 12 Jun 2026 Iosif M. Gershteyn ̳ & Jacob A. Alber | 2026 | `arxiv:2606.14484` | read |
| KN-LIT-1832 | Quantum Meets Statistical-Physical Secrecy: A Novel Hybrid Key Distribution Architecture | 2026 | `arxiv:2605.15247` | read |
| KN-LIT-1833 | Quantum-Safe Cryptography: A Migration Framework for Legacy Systems Toward NIST PQC Standards with the Crypto-Agility Readiness Score | 2026 | `eprint:2026/1467` | read |
| KN-LIT-1834 | quantum-safe: Bridging the Post-Quantum Production Gap with a Hybrid-by-Default Python Cryptography Library | 2026 | `arxiv:2605.17061` | read |
| KN-LIT-1835 | QuantumScouter: Reinforcement Learning-Based Optimization of Variational Quantum Circuits for Differential Cryptanalysis | 2026 | `eprint:2026/1456` | read |
| KN-LIT-1836 | R EFUSAL E VALUATION IN C ODING LLM S AND C ODE AGENTS : A S YSTEMATIC R EVIEW OF T HIRTEEN M ALICIOUS -C ODE | 2026 | `arxiv:2605.20351` | read |
| KN-LIT-1837 | RANK OF ELLIPTIC CURVES AND CLASS GROUPS OF REAL QUADRATIC FIELDS | 2026 | `arxiv:2601.15988` | read |
| KN-LIT-1838 | RANK-TWO DRINFELD MODULE OVER ELLIPTIC CURVES | 2026 | `arxiv:2606.26851` | read |
| KN-LIT-1839 | RANKS OF ELLIPTIC CURVES TWISTED BY QUADRATIC FORMS | 2026 | `arxiv:2607.13000` | read |
| KN-LIT-184 | Optimized quantum implementation of elliptic curve arithmetic over binary fields Phillip Kaye and Christof Zalka | 2004 | `arxiv:0407095` | read |
| KN-LIT-1840 | Rational 2-Cycles for x3 + bx + a and the Elliptic Family | 2026 | `arxiv:2606.15109` | read |
| KN-LIT-1841 | RATIONAL POINTS ON MODULAR CURVES VIA MAPS TO ELLIPTIC CURVES WITH RANK ZERO | 2026 | `arxiv:2601.17202` | read |
| KN-LIT-1842 | RATIONAL POINTS ON MODULAR CURVES: PARAMETERIZATION AND GEOMETRIC EXPLANATIONS | 2026 | `arxiv:2602.20964` | read |
| KN-LIT-1843 | Reassessing the Security of LPN-C and its HHE-Oriented Variants | 2026 | `eprint:2026/1130` | read |
| KN-LIT-1844 | RECOVERING KODAIRA TYPES FROM l-TORSION ON ELLIPTIC CURVES | 2026 | `arxiv:2607.02678` | read |
| KN-LIT-1845 | Reducing the Number of Qubits in Quantum Discrete Logarithms on Elliptic Curves | 2026 | `eprint:2026/280` | read |
| KN-LIT-1846 | REDUCTION TYPES OF GENUS 2 CURVES | 2026 | `arxiv:2607.07558` | read |
| KN-LIT-1847 | REGULATOR CONSTANTS AND COHOMOLOGY | 2026 | `arxiv:2603.01310` | read |
| KN-LIT-1848 | Related-Differential Distinguishers on up to 7 Rounds of AES | 2026 | `eprint:2026/1039` | read |
| KN-LIT-1849 | REMARKS ON A THEOREM OF SILVERMAN | 2026 | `arxiv:2607.09002` | read |
| KN-LIT-185 | Shimura curves for level-3 subgroups of the (2, 3, 7) triangle group arXiv:math/0409020v2 [math.NT] 25 Dec 2006 and some other examples | 2004 | `arxiv:0409020` | read |
| KN-LIT-1850 | Resettable Non-Interactive Zero-Knowledge: Attacks and Defenses | 2026 | `eprint:2026/1036` | read |
| KN-LIT-1851 | RESONANCE OF RANK-TWO VECTOR BUNDLES OVER ELLIPTIC CURVES arXiv:2604.23291v1 [math.AG] 25 Apr 2026 CĂLIN SPIRIDON | 2026 | `arxiv:2604.23291` | read |
| KN-LIT-1852 | Rethinking Side-Channel Analysis: Automated Discovery and Analysis of Side-Channel Leakage with LLM-Assisted Agents | 2026 | `arxiv:2605.17406` | read |
| KN-LIT-1853 | Revisiting DKLs Threshold ECDSA: | 2026 | `eprint:2026/976` | read |
| KN-LIT-1854 | Round-Based Approximation of (Higher-Order) | 2026 | `eprint:2026/358` | read |
| KN-LIT-1855 | Round-Optimal Subversion-Resilient UC PAKE from Malleable Trapdoor Smooth Projective Hash Functions | 2026 | `eprint:2026/1047` | read |
| KN-LIT-1856 | Scalable High-Throughput FPGA Architecture for SMAC Message | 2026 | `eprint:2026/1466` | read |
| KN-LIT-1857 | Scaling Intelligence: Verifiable | 2026 | `eprint:2026/1038` | read |
| KN-LIT-1858 | Scaling of Memory and Bandwidth Requirements of Post-Quantum Signatures with Message Size Falko Strenzke[0009−0006−6574−2904] | 2026 | `eprint:2026/617` | read |
| KN-LIT-1859 | SCARA: A S EMANTICS -C ONSTRAINED AUTONOMOUS R EMEDIATION AGENT FOR O PAQUE I NDUSTRIAL S OFTWARE | 2026 | `arxiv:2605.19668` | read |
| KN-LIT-186 | SUPERSINGULAR PRIMES FOR POINTS ON X0 (p)/wp | 2004 | `arxiv:0408065` | read |
| KN-LIT-1860 | Schnorr-like Proofs of Knowledge for Hidden Oil | 2026 | `eprint:2026/1021` | read |
| KN-LIT-1861 | SECANT RANK AND SYZYGIES OF PROJECTIONS OF ELLIPTIC | 2026 | `arxiv:2604.02046` | read |
| KN-LIT-1862 | SECONDARY TERMS FOR FIRST MOMENTS OF SELMER GROUPS OF TWISTS OF ELLIPTIC CURVES OVER GLOBAL FUNCTION FIELDS | 2026 | `arxiv:2606.14274` | read |
| KN-LIT-1863 | Secure and Parallel Determinant Computation for Large-Scale Matrices in Edge Environments | 2026 | `arxiv:2605.22039` | read |
| KN-LIT-1864 | Securing Cryptography in the Age of Quantum Computing and AI: Threats | 2026 | `arxiv:2603.06969` | read |
| KN-LIT-1865 | Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities: | 2026 | `eprint:2026/625` | read |
| KN-LIT-1866 | Security Amplification via Robust Indistinguishability Combiners | 2026 | `eprint:2026/1121` | read |
| KN-LIT-1867 | Security Analysis of Bitcoin’s V2 Transport Protocol: Exploiting Design Implications for | 2026 | `arxiv:2605.19715` | read |
| KN-LIT-1868 | Security of the Fischlin Transform in Quantum Random Oracle Model | 2026 | `eprint:2026/311` | read |
| KN-LIT-1869 | Semantics-Based Verification of an Implemented Shor Oracle for ECDLP in Qrisp | 2026 | `arxiv:2605.01008` | read |
| KN-LIT-187 | THE PERIOD-INDEX PROBLEM IN WC-GROUPS I: ELLIPTIC CURVES | 2004 | `arxiv:0406131` | read |
| KN-LIT-1870 | Sequence-Level Security for Active Weighted Signature Reconfiguration | 2026 | `eprint:2026/1013` | read |
| KN-LIT-1871 | Shor’s algorithm is possible with as few as 10,000 reconfigurable atomic qubits | 2026 | `arxiv:2603.28627` | read |
| KN-LIT-1872 | Side-Channel Attacks Revisited — an Optimization Problem Perspective: | 2026 | `eprint:2026/1468` | read |
| KN-LIT-1873 | Signal and Ready to MINGLE: In-Band Gossip for Key Transparency Split-View Detection in E2EE Messengers | 2026 | `eprint:2026/1010` | read |
| KN-LIT-1874 | Single-Trace Power Analysis of LESS Key Generation Süleyman Emir Akın1[0009−0002−7684−4763] | 2026 | `eprint:2026/990` | read |
| KN-LIT-1875 | Sleep Reveals the Nonce: Breaking ECDSA using Sleep-Based Power Side-Channel Vulnerability | 2026 | `arxiv:2602.01491` | read |
| KN-LIT-1876 | SOBRE LOS TEOREMAS DE SHAFAREVICH Y SIEGEL arXiv:2601.04284v2 [math.NT] 11 Jan 2026 HÉCTOR PASTÉN | 2026 | `arxiv:2601.04284` | read |
| KN-LIT-1877 | SoK: Cryptographic Erasure on Public Ledgers | 2026 | `eprint:2026/1109` | read |
| KN-LIT-1878 | SoK: Offline Finding Protocols for Lightweight Location Tracking | 2026 | `eprint:2026/488` | read |
| KN-LIT-1879 | SoK: PIOP-based SNARKs for General Computation | 2026 | `eprint:2026/1133` | read |
| KN-LIT-188 | Trace of Frobenius endomorphism of an elliptic curve with complex multiplication1 | 2004 | `arxiv:0401289` | read |
| KN-LIT-1880 | SoK: Private LLM Inference using Approximate Homomorphic Encryption | 2026 | `eprint:2026/935` | read |
| KN-LIT-1881 | SoK: Rijndael-256 | 2026 | `eprint:2026/1035` | read |
| KN-LIT-1882 | Space-Efficient Quantum Algorithm for Elliptic Curve Discrete Logarithms with Resource Estimation | 2026 | `arxiv:2604.02311` | read |
| KN-LIT-1883 | Sparse Hermite Interpolation Method for Discrete-CKKS Functional Bootstrapping | 2026 | `eprint:2026/1026` | read |
| KN-LIT-1884 | SPECIAL L-VALUES OF CERTAIN CM WEIGHT THREE HECKE EIGENFORMS | 2026 | `arxiv:2601.07030` | read |
| KN-LIT-1885 | Spectral Theory of Isogeny Graphs and Quantum Sampling of Secure Supersingular Elliptic Curves | 2026 | `arxiv:2602.02263` | read |
| KN-LIT-1886 | SPIDER: Two Server Functionality for the Cost of Zero | 2026 | `eprint:2026/1134` | read |
| KN-LIT-1887 | Splittings and Endomorphism Rings | 2026 | `eprint:2026/1198` | read |
| KN-LIT-1888 | SPRINT: New Isogeny Proofs of Knowledge and Isogeny-Based Signatures | 2026 | `eprint:2026/364` | read |
| KN-LIT-1889 | Structural Analysis of Cryptographic Sequences using Stringology-Based Fingerprinting | 2026 | `arxiv:2605.19123` | read |
| KN-LIT-189 | 2000]11F30, 11G05, 17B67 | 2005 | `arxiv:0512623` | read |
| KN-LIT-1890 | Study of Post Quantum status of Widely Used Protocols | 2026 | `arxiv:2603.28728` | read |
| KN-LIT-1891 | Subvarieties in Bogomolov-Guan precursors | 2026 | `arxiv:2606.08599` | read |
| KN-LIT-1892 | Super-intelligence Survival Guide: Verification via Proof-Carrying Output | 2026 | `eprint:2026/994` | read |
| KN-LIT-1893 | Supersingular elliptic curves and twisting endomorphisms | 2026 | `arxiv:2606.31687` | read |
| KN-LIT-1894 | Suppressing Hidden Extension-Field Linearity in Rank-Metric Cryptography via Structural Incompatibility | 2026 | `eprint:2026/992` | read |
| KN-LIT-1895 | Survey of isogeny-based signature schemes resistant to Castryck–Decru attack | 2026 | `eprint:2026/446` | read |
| KN-LIT-1896 | SwiftSNNI: Optimized Scheduling for Secure Neural Network Inference (SNNI) on Multi-Core Systems | 2026 | `eprint:2026/503` | read |
| KN-LIT-1897 | Symmetric Attribute-Based Encryption from Minimal Hardness Assumptions | 2026 | `eprint:2026/1018` | read |
| KN-LIT-1898 | T IME G UARD: Channel-wise Pool Training for Backdoor Defense in Time Series Forecasting | 2026 | `arxiv:2605.22365` | read |
| KN-LIT-1899 | Taking Cryptography Out of the Data Path via Near-Memory | 2026 | `arxiv:2605.20047` | read |
| KN-LIT-190 | A modular description of the K(2)-local sphere at the prime | 2005 | `arxiv:0507184` | read |
| KN-LIT-1900 | TALUS: Threshold ML-DSA with One-Round Online Signing via Boundary Clearance and Carry Elimination | 2026 | `arxiv:2603.22109` | read |
| KN-LIT-1901 | THE 2-PART OF THE BLOCH-KATO CONJECTURE, AND | 2026 | `arxiv:2605.11100` | read |
| KN-LIT-1902 | The ABC of Symmetric Primitives over Integer Rings: Milk Before Meat (Extended Version) | 2026 | `eprint:2026/1104` | read |
| KN-LIT-1903 | The Algebraic Isogeny Model: A General Model with | 2026 | `eprint:2026/032` | read |
| KN-LIT-1904 | THE CLASSIFICATION | 2026 | `arxiv:2601.21756` | read |
| KN-LIT-1905 | The conjecture of Colmez and reciprocity laws for modular forms | 2026 | `arxiv:2603.28536` | read |
| KN-LIT-1906 | The Double Well Done Doubly-Well | 2026 | `arxiv:2606.05282` | read |
| KN-LIT-1907 | The Fact of the MATTER: Efficient Hardware Accelerators for Wide-Block Memory Encryption | 2026 | `eprint:2026/1115` | read |
| KN-LIT-1908 | THE IMAGE OF THE ADELIC GALOIS REPRESENTATION OF AN ELLIPTIC CURVE WITH COMPLEX MULTIPLICATION | 2026 | `arxiv:2603.08545` | read |
| KN-LIT-1909 | The Impossibility of Post-Quantum Public Indifferentiability for Merkle-Damgård | 2026 | `eprint:2026/128` | read |
| KN-LIT-191 | ANALYTIC PROBLEMS FOR ELLIPTIC CURVES | 2005 | `arxiv:0510197` | read |
| KN-LIT-1910 | The Landscape of Reusable Garbling | 2026 | `eprint:2026/492` | read |
| KN-LIT-1911 | The Lang-Trotter conjecture on average for genus-2 curves with S3 reduced automorphism group | 2026 | `arxiv:2604.00822` | read |
| KN-LIT-1912 | The m = n + 1 Boundary of EME: A Splicing Distinguisher for the Unrefreshed | 2026 | `eprint:2026/1461` | read |
| KN-LIT-1913 | The MDS or NMDS for Modified GRS codes with | 2026 | `arxiv:2606.25662` | read |
| KN-LIT-1914 | THE NULLITY OF A FAMILY OF PROPER BIHARMONIC MAPS VIA ELLIPTIC CURVES | 2026 | `arxiv:2607.16014` | read |
| KN-LIT-1915 | The Privacy Subsidy: Kyle’s λ under Noise-Perturbed Order-Flow Observation | 2026 | `arxiv:2605.15746` | read |
| KN-LIT-1916 | THE SIZE OF 2-SELMER GROUPS FOR THE π3 -CONGRUENT NUMBER PROBLEM | 2026 | `arxiv:2602.08912` | read |
| KN-LIT-1917 | THE SMALLEST INVARIANT FACTOR OF ELLIPTIC CURVES, AND COINCIDENCES | 2026 | `arxiv:2604.21601` | read |
| KN-LIT-1918 | The solvability of the inverse volcano problem over non-prime finite fields | 2026 | `arxiv:2604.11330` | read |
| KN-LIT-1919 | The SQInstructor: a guide to SQIsign and the Deuring Correspondence with level structures | 2026 | `arxiv:2603.09899` | read |
| KN-LIT-192 | BUILDINGS, ELLIPTIC CURVES, AND THE K(2)-LOCAL SPHERE | 2005 | `arxiv:0510026` | read |
| KN-LIT-1920 | THE STACKY BATYREV–MANIN CONJECTURE AND MODULAR CURVES | 2026 | `arxiv:2602.19771` | read |
| KN-LIT-1921 | THE WIRTINGER-TYPE INTEGRAL FOR A GENUS TWO CURVE | 2026 | `arxiv:2603.00577` | read |
| KN-LIT-1922 | This is an author's extended version of the article accepted for LATS 2025; the final publication is available at https://ieeexplore.ieee.org/document/10963958 | 2026 | `arxiv:2603.19811` | read |
| KN-LIT-1923 | THREE BRILLHART–LEHMER–SELFRIDGE PRIMALITY PROOFS FOR WAGSTAFF NUMBERS | 2026 | `arxiv:2605.18555` | read |
| KN-LIT-1924 | THREE-PERIODIC HELICES ON ELLIPTIC CURVES AND THEIR ASSOCIATED REGULAR ALGEBRAS | 2026 | `arxiv:2604.21900` | read |
| KN-LIT-1925 | Threshold Signatures in the Head | 2026 | `eprint:2026/1125` | read |
| KN-LIT-1926 | ThriftyMPC: Reducing the Cost of Large-Scale MPC in the Cloud | 2026 | `eprint:2026/977` | read |
| KN-LIT-1927 | TOKYO 11TH INTERNATIONAL INNOVATIVE STUDIES & CONTEMPORARY SCIENTIFIC RESEARCH CONGRESS | 2026 | `arxiv:2605.16912` | read |
| KN-LIT-1928 | Topology-Hiding Computation From Key Agreement in Diameter-Two Graphs | 2026 | `eprint:2026/996` | read |
| KN-LIT-1929 | TORSION GROUPS OF ELLIPTIC CURVES THAT APPEAR INFINITELY OFTEN OVER SEPTIC FIELDS | 2026 | `arxiv:2602.03513` | read |
| KN-LIT-193 | CONSTRUCTING ELLIPTIC CURVES IN ALMOST POLYNOMIAL TIME | 2005 | `arxiv:0511729` | read |
| KN-LIT-1930 | TORSION GROUPS OF RATIONAL ELLIPTIC CURVES OVER Zp -EXTENSIONS OF QUADRATIC FIELDS: THE p ≤ 5 CASE | 2026 | `arxiv:2607.13514` | read |
| KN-LIT-1931 | Torsion of rational elliptic curves over Zp-extensions of quadratic fields for p ≥ 5, with a slope analysis for p=3 | 2026 | `arxiv:2607.17303` | read |
| KN-LIT-1932 | TORSION-STABILIZED MODULAR CURVES OF LEVEL p | 2026 | `arxiv:2607.08564` | read |
| KN-LIT-1933 | Towards a Unified Memory-Less Framework for TCitH Jesús-Javier Chi-Domı́nguez1 , Décio | 2026 | `eprint:2026/1029` | read |
| KN-LIT-1934 | Towards Post-Quantum Secure Pharmacovigilance with ML-KEM and ML-DSA | 2026 | `arxiv:2606.09412` | read |
| KN-LIT-1935 | Transformers Learn the Mestre-Nagao Heuristic | 2026 | `arxiv:2606.15036` | read |
| KN-LIT-1936 | Triple-Hoisted Baby-Step Giant-Step Linear Transformation over | 2026 | `arxiv:2605.17222` | read |
| KN-LIT-1937 | Tripling on Hessian curves via isogeny decomposition | 2026 | `eprint:2026/334` | read |
| KN-LIT-1938 | TriSweep: A Four-Drone Swarm Framework for Electromagnetic Side-Channel Analysis | 2026 | `arxiv:2605.22709` | read |
| KN-LIT-1939 | Trout++: Robust Asynchronous Two-Round ECDSA for Arbitrary Thresholds | 2026 | `eprint:2026/1455` | read |
| KN-LIT-194 | EVIL PRIMES AND SUPERSPECIAL MODULI | 2005 | `arxiv:0512472` | read |
| KN-LIT-1940 | TWIST CLASS REDUNDANCY DRIVES THE PREDICTION OF TRACES OF FROBENIUS OF ELLIPTIC CURVES | 2026 | `arxiv:2605.14288` | read |
| KN-LIT-1941 | TWO INFINITE FAMILIES OF ELLIPTIC CURVES WITH MORDELL-WEIL RANK | 2026 | `arxiv:2601.08570` | read |
| KN-LIT-1942 | uGen: An Agentic Framework for Generating | 2026 | `arxiv:2605.15503` | read |
| KN-LIT-1943 | Ultra Kolyvagin systems and higher Fitting ideals of Iwasawa Selmer groups | 2026 | `arxiv:2605.26917` | read |
| KN-LIT-1944 | Unified FPGA Design of Kyber and Dilithium with Provable Fault Tolerance | 2026 | `eprint:2026/1008` | read |
| KN-LIT-1945 | UNIFORM SUM-PRODUCT PHENOMENON FOR ALGEBRAIC | 2026 | `arxiv:2603.06483` | read |
| KN-LIT-1946 | UNLIKELY INTERSECTIONS WITH CM ABELIAN VARIETIES IN A | 2026 | `arxiv:2601.05919` | read |
| KN-LIT-1947 | Updatable Public-Key Encryption from FESTA | 2026 | `eprint:2026/1014` | read |
| KN-LIT-1948 | UPPER BOUNDS FOR MOMENTS OF ANALYTIC RANKS OF ELLIPTIC CURVES OVER NUMBER FIELDS | 2026 | `arxiv:2607.15998` | read |
| KN-LIT-1949 | V ROOM: Accelerating (Almost All) Number-Theoretic Cryptography Using Vectorization and the Residue Number System | 2026 | `eprint:2026/393` | read |
| KN-LIT-195 | FINDING LARGE SELMER RANK VIA AN ARITHMETIC THEORY OF LOCAL CONSTANTS | 2005 | `arxiv:0512085` | read |
| KN-LIT-1950 | Vela and Carina: Fast Pairing-Based Multilinear Polynomial Commitments from Reciprocal Polynomials | 2026 | `eprint:2026/1438` | read |
| KN-LIT-1951 | Verifiable Bootstrapping from Lattice-based Folding | 2026 | `eprint:2026/1127` | read |
| KN-LIT-1952 | Verifiable Provenance and Watermarking for Generative AI: An Evidentiary Framework for International Operational Law and Domestic Courts | 2026 | `arxiv:2605.21002` | read |
| KN-LIT-1953 | Verifying Consensus Protocols from LLM-assisted TLA+: A Case Study of Byzantine Reliable Broadcast | 2026 | `eprint:2026/978` | read |
| KN-LIT-1954 | Verifying Provenance of Digital Media: Security Analysis of C2PA and its Implementation | 2026 | `eprint:2026/804` | read |
| KN-LIT-1955 | VERTEX OPERATOR ALGEBRA BUNDLES ON MODULAR CURVES AND THEIR ASSOCIATED MODULAR FORMS | 2026 | `arxiv:2601.10686` | read |
| KN-LIT-1956 | VISIBLE 2-TORSION IN THE TATE-SHAFAREVICH GROUP OF AN ELLIPTIC CURVE | 2026 | `arxiv:2605.31488` | read |
| KN-LIT-1957 | Vistrutah on FPGA: High-Throughput Pipelined Architecture and Comparison with Wider AES Variant | 2026 | `eprint:2026/1034` | read |
| KN-LIT-1958 | WEBER MODULAR CURVES AND MODULAR ISOGENIES | 2026 | `arxiv:2603.29802` | read |
| KN-LIT-1959 | WEIGHTED AVERAGES OF p-ADIC HYPERGEOMETRIC FUNCTIONS AND TRACES OF FROBENIUS OF ELLIPTIC CURVES | 2026 | `arxiv:2603.01148` | read |
| KN-LIT-196 | GALOIS GROUPS VIA ATKIN-LEHNER TWISTS PETE L. CLARK | 2005 | `arxiv:0506490` | read |
| KN-LIT-1960 | Weighted Distributions of Complex Multiplication | 2026 | `arxiv:2605.07626` | read |
| KN-LIT-1961 | When Removing Reductions Goes Wrong: Auditing Reduction Placement in Production ML-DSA Implementations | 2026 | `eprint:2026/1032` | read |
| KN-LIT-1962 | X3DH with Deniable Authentication without Trusted Third Parties | 2026 | `eprint:2026/522` | read |
| KN-LIT-1963 | Zero-shot deep-unfolding decoder for QC-MDPC McEliece cryptosystems | 2026 | `eprint:2026/982` | read |
| KN-LIT-1964 | ZK-Flex: A Flexible and Scalable Framework for Accelerating | 2026 | `arxiv:2606.03046` | read |
| KN-LIT-1965 | “BREAKMEIFYOUCAN!”: Exploiting Keyspace Reduction and Relay | 2026 | `eprint:2026/100` | read |
| KN-LIT-19691d | Mckeycutter: a high-throughput key generator of Classic McEliece on hardware | 2023 | `doi:10.1109/dac56929.2023.10247918` | web |
| KN-LIT-197 | Index Calculus in Class Groups of Plane Curves of Small Degree Claus Diem | 2005 | `eprint:2005/119` | read |
| KN-LIT-198 | Isogenies of elliptic curves and the Morava stabilizer group | 2005 | `arxiv:0508079` | read |
| KN-LIT-199 | ON THE EMBEDDING PROBLEM FOR 2+ S4 REPRESENTATIONS | 2005 | `arxiv:0507381` | read |
| KN-LIT-19cf36 | On insecurity of cryptosystems based on generalized Reed-Solomon codes | 1992 | `doi:10.1515/dma.1992.2.4.439` | web |
| KN-LIT-1b6203 | Factoring into coprimes in essentially linear time | 2004 | `url:cr.yp.to/papers.html#dcba` | read |
| KN-LIT-1c9474 | HQC-RMRS, an instantiation of the HQC encryption framework with a more efficient auxiliary error-correcting code | 2020 | `arxiv:2005.10741` | read |
| KN-LIT-1d7668 | Classic McEliece key generation on RAM constrained devices | 2022 | `eprint:2022/1613` | web |
| KN-LIT-1d8337 | Masking large keys in hardware: a masked implementation of McEliece | 2015 | `eprint:2015/924` | web |
| KN-LIT-1f10ac | A summary of McEliece-type cryptosystems and their security | 2007 | `eprint:2006/162` | web |
| KN-LIT-200 | Ordinary elliptic curves of high rank over Fp (x) with constant j-invariant II | 2005 | `arxiv:0509600` | read |
| KN-LIT-201 | Scholten forms and elliptic/hyperelliptic curves with weak Weil restrictions | 2005 | `eprint:2005/277` | read |
| KN-LIT-202 | ALGEBRAIC THETA FUNCTIONS AND THE p-ADIC INTERPOLATION OF EISENSTEIN-KRONECKER NUMBERS | 2006 | `arxiv:0610163` | read |
| KN-LIT-203 | Anneaux d’endomorphismes et classe d’isogénies de modules de | 2006 | `arxiv:0606416` | read |
| KN-LIT-204 | Big symplectic or orthogonal monodromy modulo l Chris Hall | 2006 | `arxiv:0608718` | read |
| KN-LIT-205 | CONTROL THEOREMS FOR ELLIPTIC CURVES OVER FUNCTION FIELDS | 2006 | `arxiv:0604249` | read |
| KN-LIT-206 | DETECTING COMPLEX MULTIPLICATION JEFFREY D. ACHTER | 2006 | `arxiv:0602115` | read |
| KN-LIT-207 | Efficiently Computable Endomorphisms for Hyperelliptic Curves | 2006 | `arxiv:0603505` | read |
| KN-LIT-208 | Explicit models of genus 2 curves with split CM | 2006 | `arxiv:0612666` | read |
| KN-LIT-209 | Fast algorithms for computing isogenies between elliptic curves | 2006 | `arxiv:0609020` | read |
| KN-LIT-210 | hep-th/0607132 arXiv:hep-th/0607132v3 17 Sep 2006 On the Existence of Non-Supersymmetric Black Hole Attractors for | 2006 | `arxiv:0607132` | read |
| KN-LIT-211 | Invariants de classes : exemples de non-annulation en dimension supérieure | 2006 | `arxiv:0603185` | read |
| KN-LIT-212 | ON THE BIRCH–SWINNERTON-DYER QUOTIENTS MODULO SQUARES | 2006 | `arxiv:0610290` | read |
| KN-LIT-213 | PARITY OF RANKS FOR ELLIPTIC CURVES WITH A CYCLIC ISOGENY | 2006 | `arxiv:0604149` | read |
| KN-LIT-21383c | Quantum Computation and Lattice Problems (Regev 2004) | 2004 | `arxiv:cs/0304005` | web |
| KN-LIT-214 | POWER RESIDUES OF FOURIER COEFFICIENTS OF ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2006 | `arxiv:0604034` | read |
| KN-LIT-215 | RATIONAL POINTS ON ELLIPTIC CURVES | 2006 | `arxiv:0606003` | read |
| KN-LIT-216 | SCALING GROUP FLOW AND LEFSCHETZ TRACE FORMULA FOR LAMINATED SPACES WITH p−ADIC TRANSVERSAL | 2006 | `arxiv:0603576` | read |
| KN-LIT-217 | Average twin prime conjecture for elliptic curves | 2007 | `arxiv:0709.1461` | read |
| KN-LIT-218 | COMBINATORIAL ASPECTS OF ELLIPTIC CURVES II: RELATIONSHIP BETWEEN ELLIPTIC CURVES AND CHIP-FIRING GAMES ON GRAPHS | 2007 | `arxiv:0710.0574` | read |
| KN-LIT-219 | CONSTRUCTING ELLIPTIC CURVES OF PRIME ORDER | 2007 | `arxiv:0712.2022` | read |
| KN-LIT-220 | DESCENT ON ELLIPTIC CURVES AND HILBERT’S TENTH PROBLEM | 2007 | `arxiv:0707.1485` | read |
| KN-LIT-221 | Distribution of Farey Fractions in | 2007 | `arxiv:0705.3861` | read |
| KN-LIT-222 | Elliptic curves related to cyclic cubic extensions | 2007 | `arxiv:0711.0083` | read |
| KN-LIT-223 | GALOIS THEORY OF ITERATED ENDOMORPHISMS | 2007 | `arxiv:0706.2384` | read |
| KN-LIT-224 | GROWTH OF SELMER RANK IN NONABELIAN EXTENSIONS OF NUMBER FIELDS | 2007 | `arxiv:0703363` | read |
| KN-LIT-224f2c | Quantum circuit design for the Lee-Brickell based information set decoding | 2024 | `doi:10.1007/978-3-031-61489-7_2` | web |
| KN-LIT-225 | ISOGENIES OF SUPERSINGULAR ELLIPTIC CURVES OVER FINITE | 2007 | `arxiv:0712.2052` | read |
| KN-LIT-226 | ON UNIFORM LOWER BOUND OF THE GALOIS IMAGES ASSOCIATED TO ELLIPTIC CURVES | 2007 | `arxiv:0703686` | read |
| KN-LIT-227 | Pure Anderson Motives over Finite Fields | 2007 | `arxiv:0709.2815` | read |
| KN-LIT-228 | RELATIONS AMONG MODULAR POINTS ON ELLIPTIC CURVES | 2007 | `arxiv:0706.0566` | read |
| KN-LIT-229 | SELMER GROUPS FOR ELLIPTIC CURVES IN Zdl -EXTENSIONS OF FUNCTION FIELDS OF CHARACTERISTIC p | 2007 | `arxiv:0707.1143` | read |
| KN-LIT-230 | Singularities of n-fold integrals of the Ising arXiv:0706.3367v1 [math-ph] 22 Jun 2007 the theory of ellipti | 2007 | `arxiv:0706.3367` | read |
| KN-LIT-231 | A NOTE ON LARSEN’S CONJECTURE AND RANKS OF ELLIPTIC CURVES | 2008 | `arxiv:0803.1122` | read |
| KN-LIT-232 | A REFINED VERSION OF THE LANG-TROTTER CONJECTURE | 2008 | `arxiv:0801.3946` | read |
| KN-LIT-233 | A visible factor for analytic rank one Amod Agashe | 2008 | `arxiv:0810.5177` | read |
| KN-LIT-234 | ALMOST PRIME VALUES OF THE ORDER OF ELLIPTIC CURVES OVER FINITE FIELDS | 2008 | `arxiv:0812.2860` | read |
| KN-LIT-235 | ELLIPTIC CURVE CRYPTOGRAPHY: THE SERPENTINE COURSE OF A PARADIGM SHIFT | 2008 | `eprint:2008/390` | read |
| KN-LIT-237 | Expander graphs based on GRH with an application to elliptic curve cryptography | 2008 | `arxiv:0811.0647` | read |
| KN-LIT-238 | Fields Institute Communications | 2008 | `arxiv:0808.1129` | read |
| KN-LIT-239 | Large Selmer groups over number fields | 2008 | `arxiv:0805.1231` | read |
| KN-LIT-23ad7f | RISC-V based Vectorization of Classic McEliece Key Generation | 2026 | `eprint:2026/523` | web |
| KN-LIT-23bab0 | Hardware design and implementation of Classic McEliece post-quantum cryptosystem based on FPGA | 2022 | `doi:10.1109/hpec55821.2022.9926295` | web |
| KN-LIT-240 | More Discriminants with the Brezing-Weng Method | 2008 | `arxiv:0803.3894` | read |
| KN-LIT-241 | ON ELKIES SUBGROUPS OF l-TORSION POINTS IN ELLIPTIC CURVES DEFINED OVER A FINITE FIELD par | 2008 | `arxiv:0809.2774` | read |
| KN-LIT-242 | ON THE VANISHING OF SELMER GROUPS FOR ELLIPTIC CURVES OVER RING CLASS FIELDS | 2008 | `arxiv:0806.4267` | read |
| KN-LIT-243 | p-ADIC EISENSTEIN-KRONECKER SERIES FOR CM | 2008 | `arxiv:0807.4007` | read |
| KN-LIT-2435 | AMERICAN MATHEMATICAL SOCIETY |  | `doi:10.1090/proc/13605` | read |
| KN-LIT-244 | René Schoof | 2008 | `arxiv:0801.3840` | read |
| KN-LIT-245 | Square-free discriminants of Frobenius rings | 2008 | `arxiv:0805.0775` | read |
| KN-LIT-246 | Squareness in the special L-value or Squareness in the special L-value and special L-values of twists | 2008 | `arxiv:0810.5179` | read |
| KN-LIT-247 | The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences | 2008 | `arxiv:0803.0728` | read |
| KN-LIT-248 | Visibility and the Birch and Swinnerton-Dyer conjecture for analytic rank one Amod Agashe | 2008 | `arxiv:0810.2487` | read |
| KN-LIT-249 | A REFINEMENT OF KOBLITZ’S CONJECTURE | 2009 | `arxiv:0909.5280` | read |
| KN-LIT-250 | Computing modular correspondences for abelian varieties | 2009 | `arxiv:0910.4668` | read |
| KN-LIT-251 | COMPUTING THE ENDOMORPHISM RING OF AN ORDINARY ELLIPTIC CURVE OVER A FINITE FIELD | 2009 | `arxiv:0902.4670` | read |
| KN-LIT-252 | Critères d’irréductibilité pour les représentations des courbes elliptiques | 2009 | `arxiv:0908.1084` | read |
| KN-LIT-253 | de Bordeaux 00 (XXXX), 000–000 arXiv:0901.0120v3 [math.NT] 8 Sep 2009 On a theorem of Mestre and Schoof par John E. CREMONA et Andrew V. SUTHERLAND | 2009 | `arxiv:0901.0120` | read |
| KN-LIT-254 | ELEMENTARY 3-DESCENT WITH A 3-ISOGENY | 2009 | `arxiv:0903.4963` | read |
| KN-LIT-255 | Encrypted Messages from the Heights of Cryptomania | 2009 | `eprint:2009/616` | read |
| KN-LIT-256 | EXPLICIT CM-THEORY FOR LEVEL 2-STRUCTURES ON ABELIAN SURFACES | 2009 | `arxiv:0910.1848` | read |
| KN-LIT-257 | Fonctions L en géométrie rigide I : F -modules convergents ou surconvergents et conjecture de Dwork | 2009 | `arxiv:0910.4437` | read |
| KN-LIT-258 | Isogenies of Elliptic Curves: A Computational Approach Daniel Shumow | 2009 | `arxiv:0910.5370` | read |
| KN-LIT-259 | KUMMER SURFACES ASSOCIATED WITH SEIBERG-WITTEN CURVES | 2009 | `arxiv:0912.4774` | read |
| KN-LIT-260 | Linearization Framework for Collision Attacks: | 2009 | `eprint:2009/382` | read |
| KN-LIT-261 | ON FIELDS OF DEFINITION OF TORSION POINTS OF ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2009 | `arxiv:0909.1661` | read |
| KN-LIT-262 | ON RIGID ANALYTIC UNIFORMIZATIONS OF JACOBIANS OF SHIMURA CURVES | 2009 | `arxiv:0910.3391` | read |
| KN-LIT-263 | ON THE DISTRIBUTION OF THE NUMBER OF POINTS ON ALGEBRAIC CURVES IN EXTENSIONS OF FINITE FIELDS | 2009 | `arxiv:0907.3664` | read |
| KN-LIT-264 | On the Necessary and Sufficient Assumptions for UC Computation | 2009 | `eprint:2009/247` | read |
| KN-LIT-265 | On-line Non-transferable Signatures Revisited? | 2009 | `eprint:2009/406` | read |
| KN-LIT-266 | ONE CLASS OF WILD BUT BRICK-TAME MATRIX PROBLEMS | 2009 | `arxiv:0903.4374` | read |
| KN-LIT-267 | PRIMITIVE INTEGRAL SOLUTIONS TO x2 + y 3 = z | 2009 | `arxiv:0911.2932` | read |
| KN-LIT-268 | Runge’s Method and Modular Curves Yuri Bilu, Pierre Parent (Université de Bordeaux I) | 2009 | `arxiv:0907.3306` | read |
| KN-LIT-269 | THE ARITHMETIC OF GENUS TWO CURVES WITH (4,4)-SPLIT JACOBIANS | 2009 | `arxiv:0902.3480` | read |
| KN-LIT-270 | The Certicom Challenges ECC2-X | 2009 | `eprint:2009/466` | read |
| KN-LIT-271 | TORSION POINTS ON ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2009 | `arxiv:0907.2499` | read |
| KN-LIT-272 | USING INDICES OF POINTS ON AN ELLIPTIC CURVE TO CONSTRUCT A | 2009 | `arxiv:0901.4168` | read |
| KN-LIT-273 | A Family of Implementation-Friendly BN Elliptic Curves | 2010 | `eprint:2010/429` | read |
| KN-LIT-274 | A Subexponential Algorithm for Evaluating | 2010 | `arxiv:1002.4228` | read |
| KN-LIT-275 | A variant of the F4 algorithm | 2010 | `eprint:2010/158` | read |
| KN-LIT-276 | ACCELERATING THE CM METHOD | 2010 | `arxiv:1009.1082` | read |
| KN-LIT-277 | AKASHI SERIES OF SELMER GROUPS | 2010 | `arxiv:1005.0394` | read |
| KN-LIT-278 | Belyi Lattès maps | 2010 | `arxiv:1011.5644` | read |
| KN-LIT-279 | BORNE UNIFORME POUR LES HOMOTHÉTIES DANS L’IMAGE | 2010 | `arxiv:1007.4725` | read |
| KN-LIT-2791 | Breaking elliptic curve cryptosystems using reconfigurable hardware |  | `doi:10.1109/fpl.2010.34` | read |
| KN-LIT-27f923 | An optimized quantum implementation of ISD on scalable quantum resources | 2021 | `eprint:2021/1608` | web |
| KN-LIT-280 | Class number formulas via 2-isogenies of elliptic curves | 2010 | `arxiv:1008.4766` | read |
| KN-LIT-281 | Computing Isogenies Between Abelian Varieties | 2010 | `arxiv:1001.2016` | read |
| KN-LIT-282 | Constructing elliptic curve isogenies in quantum subexponential time | 2010 | `arxiv:1012.4019` | read |
| KN-LIT-283 | Cryptographic Extraction and Key Derivation: The HKDF Scheme | 2010 | `eprint:2010/264` | read |
| KN-LIT-284 | de Bordeaux 00 (XXXX), 000–000 A local-global principle for rational isogenies of prime degree par Andrew V. Sutherland | 2010 | `arxiv:1006.1782` | read |
| KN-LIT-285 | Fast algorithms for computing isogenies between ordinary elliptic curves in small characteristic | 2010 | `arxiv:1002.2597` | read |
| KN-LIT-286 | Fast Arithmetics in Artin-Schreier Towers over Finite Fields arXiv:1002.2594v1 [cs.SC] 12 Feb 2010 Luca De Feo | 2010 | `arxiv:1002.2594` | read |
| KN-LIT-287 | Fast Exhaustive Search for Polynomial Systems in F2 | 2010 | `eprint:2010/313` | read |
| KN-LIT-288 | GAUSSIAN HYPERGEOMETRIC EVALUATIONS OF TRACES OF FROBENIUS FOR ELLIPTIC CURVES | 2010 | `arxiv:1003.4421` | read |
| KN-LIT-288b99 | Statistical decoding of codes over Fq | 2011 | `doi:10.1007/978-3-642-25405-5_14` | web |
| KN-LIT-289 | IGUSA CLASS POLYNOMIALS, EMBEDDINGS OF QUARTIC CM | 2010 | `arxiv:1006.0208` | read |
| KN-LIT-28adfb | A further improvement of the work factor in an attempt at breaking McEliece's cryptosystem | 1994 | `url:hal.inria.fr/inria-00074443` | false |
| KN-LIT-290 | Interactive Locking, Zero-Knowledge PCPs, and Unconditional Cryptography? | 2010 | `eprint:2010/089` | read |
| KN-LIT-291 | MUSINGS ON Q(1/4): ARITHMETIC SPIN STRUCTURES ON ELLIPTIC CURVES | 2010 | `arxiv:1005.3008` | read |
| KN-LIT-292 | NILPOTENT OPERATORS AND WEIGHTED PROJECTIVE LINES | 2010 | `arxiv:1002.3797` | read |
| KN-LIT-293 | ON ELLIPTIC CURVES WITH AN ISOGENY OF DEGREE | 2010 | `arxiv:1007.4617` | read |
| KN-LIT-294 | On group structures realized by elliptic curves over arbitrary finite fields | 2010 | `arxiv:1003.3004` | read |
| KN-LIT-295 | ON THE NUMBER OF MORDELL-WEIL GENERATORS FOR CUBIC SURFACES | 2010 | `arxiv:1012.1838` | read |
| KN-LIT-296 | ON THE PRE-IMAGE OF A POINT UNDER AN ISOGENY AND SIEGEL’S THEOREM | 2010 | `arxiv:1009.0807` | read |
| KN-LIT-297 | Parity conjectures for elliptic curves over global fields of positive characteristic | 2010 | `arxiv:1011.2991` | read |
| KN-LIT-298 | PRIME POWER TERMS IN ELLIPTIC DIVISIBILITY SEQUENCES | 2010 | `arxiv:1002.4202` | read |
| KN-LIT-299 | Strong Weil curves over Fq (T ) with small conductor | 2010 | `arxiv:1002.2260` | read |
| KN-LIT-2c8264 | A Subexponential-Time Quantum Algorithm for the Dihedral Hidden Subgroup Problem (Kuperberg 2005) | 2005 | `arxiv:quant-ph/0302112` | web |
| KN-LIT-2d85cd | Low-Reiter: Niederreiter encryption scheme for embedded microcontrollers | 2010 | `doi:10.1007/978-3-642-12929-2_13` | web |
| KN-LIT-2d9edb | An algebraic attack against McEliece-like cryptosystems based on BCH codes | 2023 | `eprint:2022/1715` | web |
| KN-LIT-300 | The Ising model: from elliptic curves to modular | 2010 | `arxiv:1007.0535` | read |
| KN-LIT-301 | A GROSS-ZAGIER FORMULA FOR QUATERNION ALGEBRAS OVER TOTALLY | 2011 | `arxiv:1112.2009` | read |
| KN-LIT-302 | A LOW-MEMORY ALGORITHM FOR FINDING SHORT PRODUCT REPRESENTATIONS IN FINITE GROUPS | 2011 | `arxiv:1101.0564` | read |
| KN-LIT-303 | A New Approach to Practical Active-Secure Two-Party Computation? | 2011 | `eprint:2011/091` | read |
| KN-LIT-304 | A NEW AUTOMORPHISM OF X0 (108) | 2011 | `arxiv:1108.5595` | read |
| KN-LIT-305 | Adaptive Pseudo-Free Groups and Applications | 2011 | `eprint:2011/053` | read |
| KN-LIT-3054 | Computing Hasse–Witt matrices of hyperelliptic curves in |  | `doi:10.1090/conm/663/13352` | read |
| KN-LIT-306 | AN ALGEBRAIC SATO-TATE GROUP AND SATO-TATE CONJECTURE | 2011 | `arxiv:1109.4449` | read |
| KN-LIT-307 | AVERAGE FROBENIUS DISTRIBUTION FOR THE DEGREE TWO PRIMES OF A NUMBER FIELD | 2011 | `arxiv:1109.4007` | read |
| KN-LIT-308 | Caractère d’isogénie et critères d’irréductibilité Agnès David Laboratoire de mathématiques de Versailles Université de Versailles Saint-Quentin-en-Yvelines | 2011 | `arxiv:1103.3892` | read |
| KN-LIT-309 | Computing endomorphism rings of elliptic curves under the GRH arXiv:1101.4323v2 [math.NT] 14 Feb 2011 Gaetan Bisson | 2011 | `arxiv:1101.4323` | read |
| KN-LIT-310 | CUBIC SURFACES WITH SPECIAL PERIODS | 2011 | `arxiv:1104.1782` | read |
| KN-LIT-311 | ELLIPTIC CURVES WITH BOUNDED RANKS IN FUNCTION FIELD TOWERS | 2011 | `arxiv:1105.6083` | read |
| KN-LIT-312 | Four-Dimensional Gallant-Lambert-Vanstone Scalar Multiplication | 2011 | `arxiv:1106.5149` | read |
| KN-LIT-313 | HEURISTICS ON PAIRING-FRIENDLY ELLIPTIC CURVES | 2011 | `arxiv:1107.0307` | read |
| KN-LIT-314 | Higher K-Groups of Smooth Projective Curves Over Finite Fields 1 Qingzhong Ji 2 Hourong Qin | 2011 | `arxiv:1112.5920` | read |
| KN-LIT-315 | IDEALS OF DEGREE ONE CONTRIBUTE MOST OF THE HEIGHT | 2011 | `arxiv:1106.1385` | read |
| KN-LIT-316 | IDENTIFYING SUPERSINGULAR ELLIPTIC CURVES | 2011 | `arxiv:1107.1140` | read |
| KN-LIT-317 | Improved Algorithm for the Isogeny Problem for Ordinary Elliptic Curves | 2011 | `arxiv:1105.6331` | read |
| KN-LIT-318 | International Journal of Computer Science & Information Technology (IJCSIT) | 2011 | `arxiv:1107.3631` | read |
| KN-LIT-319 | MATHEMATICS OF COMPUTATION | 2011 | `arxiv:1110.3602` | read |
| KN-LIT-320 | ON CONGRUENT PRIMES AND CLASS NUMBERS OF IMAGINARY | 2011 | `arxiv:1110.5959` | read |
| KN-LIT-321 | ON JACQUET-LANGLANDS ISOGENY OVER FUNCTION FIELDS | 2011 | `arxiv:1103.5830` | read |
| KN-LIT-322 | On local-global divisibility by p2 in elliptic curves | 2011 | `arxiv:1103.4963` | read |
| KN-LIT-323 | On local-global divisibility by pn in elliptic curves | 2011 | `arxiv:1104.4762` | read |
| KN-LIT-324 | On the correct use of the negation map in the Pollard rho method | 2011 | `eprint:2011/003` | read |
| KN-LIT-325 | On the Distribution of | 2011 | `arxiv:1112.3390` | read |
| KN-LIT-326 | On the Distribution of the Subset Sum Pseudorandom Number Generator on Elliptic Curves | 2011 | `arxiv:1102.1053` | read |
| KN-LIT-327 | ON THE GENERALISED TATE CONJECTURE FOR PRODUCTS OF ELLIPTIC CURVES OVER FINITE FIELDS | 2011 | `arxiv:1101.1730` | read |
| KN-LIT-328 | On the number of elliptic curves with prescribed isogeny or torsion group over number fields of prime degree | 2011 | `arxiv:1109.6278` | read |
| KN-LIT-328239 | Inverting Cryptographic Hash Functions via Cube-and-Conquer | 2022 | `arxiv:2212.02405` | read |
| KN-LIT-329 | ON THE PULLBACK OF AN ARITHMETIC THETA FUNCTION | 2011 | `arxiv:1106.4732` | read |
| KN-LIT-32fb9b | Efficient decryption architecture for Classic McEliece | 2023 | `doi:10.1109/isqed57927.2023.10129325` | web |
| KN-LIT-330 | OPTIMALITY OF THE WIDTH-w NON-ADJACENT FORM: | 2011 | `arxiv:1110.0966` | read |
| KN-LIT-331 | p-JETS OF p-ISOGENIES | 2011 | `arxiv:1104.0119` | read |
| KN-LIT-332 | Quantum to classical randomness extractors ? | 2011 | `arxiv:1111.2026` | read |
| KN-LIT-333 | Radical Characterizations of Elliptic Curves | 2011 | `arxiv:1109.2440` | read |
| KN-LIT-334 | RATIONAL POINTS ON ELLIPTIC CURVES y 2 = x3 + a3 IN Fp WHERE p ≡ 1 (mod 6) IS PRIME | 2011 | `arxiv:1106.5218` | read |
| KN-LIT-335 | SECOND ISOGENY DESCENTS AND THE BIRCH AND SWINNERTON-DYER CONJECTURAL FORMULA | 2011 | `arxiv:1105.4018` | read |
| KN-LIT-336 | SMALL HEIGHT AND INFINITE NONABELIAN EXTENSIONS | 2011 | `arxiv:1109.5859` | read |
| KN-LIT-337 | The class group pairing and p-descent on elliptic curves | 2011 | `arxiv:1110.4232` | read |
| KN-LIT-338 | The probability that the number of points on the Jacobian of a genus 2 curve is prime | 2011 | `arxiv:1101.4792` | read |
| KN-LIT-339 | TRACES OF HECKE OPERATORS IN LEVEL 1 AND GAUSSIAN HYPERGEOMETRIC FUNCTIONS | 2011 | `arxiv:1109.3362` | read |
| KN-LIT-33d2bd | Cryptanalysis of the Niederreiter public key scheme based on GRS subcodes | 2010 | `doi:10.1007/978-3-642-12929-2_5` | web |
| KN-LIT-340 | VAN GEEMEN–SARTI INVOLUTIONS AND ELLIPTIC FIBRATIONS ON K3 | 2011 | `arxiv:1110.6380` | read |
| KN-LIT-341 | Verifiable Delegation of Computation over Large Datasets? | 2011 | `eprint:2011/132` | read |
| KN-LIT-342 | A HEIGHT INEQUALITY FOR RATIONAL POINTS ON ELLIPTIC CURVES IMPLIED BY THE ABC-CONJECTURE | 2012 | `arxiv:1210.6543` | read |
| KN-LIT-343 | Algebraic points on Shimura curves of Γ0(p)-type | 2012 | `arxiv:1202.4841` | read |
| KN-LIT-344 | AVERAGE FROBENIUS DISTRIBUTION FOR ELLIPTIC CURVES DEFINED OVER FINITE GALOIS EXTENSIONS OF THE RATIONALS (APPEARED IN MATHEMATICAL PROCEEDINGS OF THE CAMBRIDGE PHILOSOPHICAL SOCIETY ) | 2012 | `arxiv:1210.4603` | read |
| KN-LIT-345 | CHARACTER SUMS DETERMINED BY LOW DEGREE ISOGENIES OF ELLIPTIC CURVES | 2012 | `arxiv:1210.2743` | read |
| KN-LIT-346 | CLASS NUMBERS VIA 3-ISOGENIES AND ELLIPTIC SURFACES | 2012 | `arxiv:1203.3560` | read |
| KN-LIT-347 | Classe d’isogénie de variétés abéliennes pleinement de type GSp | 2012 | `arxiv:1211.4387` | read |
| KN-LIT-348 | Computing endomorphism rings of abelian varieties of dimension two | 2012 | `arxiv:1209.1189` | read |
| KN-LIT-349 | Critère d’irréductibilité pour les courbes elliptiques semi-stables sur un corps de nombres Agnès David Laboratoire de mathématiques de Versailles | 2012 | `arxiv:1202.1649` | read |
| KN-LIT-350 | DERIVED P-ADIC HEIGHTS AND P-ADIC L-FUNCTIONS | 2012 | `arxiv:1202.6343` | read |
| KN-LIT-352 | DISTRIBUTION OF SQUAREFREE VALUES OF SEQUENCES ASSOCIATED WITH ELLIPTIC CURVES | 2012 | `arxiv:1210.3433` | read |
| KN-LIT-353 | ELLIPTIC CURVES WITH p-SELMER GROWTH FOR ALL p | 2012 | `arxiv:1204.1166` | read |
| KN-LIT-354 | ELLIPTIC CURVES, MODULAR FORMS, AND SUMS OF HURWITZ CLASS NUMBERS (APPEARED IN JOURNAL OF NUMBER THEORY ) | 2012 | `arxiv:1208.4769` | read |
| KN-LIT-355 | Galois groups of co-abelian ball quotient covers | 2012 | `arxiv:1201.0094` | read |
| KN-LIT-356 | GENERALIZATION OF DEURING REDUCTION THEOREM | 2012 | `arxiv:1209.5207` | read |
| KN-LIT-357 | GROUP STRUCTURES OF ELLIPTIC CURVES OVER FINITE FIELDS | 2012 | `arxiv:1210.3880` | read |
| KN-LIT-358 | HYPERGEOMETRIC FUNCTIONS OVER Fq AND TRACES OF FROBENIUS FOR ELLIPTIC CURVES | 2012 | `arxiv:1208.0508` | read |
| KN-LIT-359 | INTEGRAL TATE MODULES AND SPLITTING OF PRIMES IN TORSION FIELDS OF ELLIPTIC CURVES | 2012 | `arxiv:1201.2124` | read |
| KN-LIT-360 | ISOGENY VOLCANOES | 2012 | `arxiv:1208.5370` | read |
| KN-LIT-361 | LOCAL INVARIANTS OF ISOGENOUS ELLIPTIC CURVES | 2012 | `arxiv:1208.5519` | read |
| KN-LIT-362 | ON RANKS OF JACOBIAN VARIETIES IN PRIME DEGREE EXTENSIONS | 2012 | `arxiv:1209.0933` | read |
| KN-LIT-363 | ON THE AVERAGE EXPONENT OF ELLIPTIC CURVES MODULO p | 2012 | `arxiv:1203.4382` | read |
| KN-LIT-364 | ON THE DISTRIBUTION OF 2-SELMER RANKS WITHIN QUADRATIC TWIST FAMILIES OF ELLIPTIC CURVES WITH PARTIAL RATIONAL TWO-TORSION | 2012 | `arxiv:1203.1030` | read |
| KN-LIT-365 | ON THE ELLIPTIC CURVES y 2 = x(x ± p)(x ± q) OVER IMAGINARY QUADRATIC NUMBER FIELDS OF CLASS NUMBER ONE | 2012 | `arxiv:1207.0287` | read |
| KN-LIT-366 | ON THE EVALUATION OF MODULAR POLYNOMIALS ANDREW V. SUTHERLAND | 2012 | `arxiv:1202.3985` | read |
| KN-LIT-3663ee | Equivalent Goppa codes and trapdoors to McEliece's public key cryptosystem | 1991 | `doi:10.1007/3-540-46416-6_46` | web |
| KN-LIT-3664 | Elligator: Elliptic-curve points indistinguishable from uniform random strings |  | `doi:10.1145/2508859.2516734` | read |
| KN-LIT-367 | ON THE HOMOTOPY OF Q(3) AND Q(5) | 2012 | `arxiv:1211.0076` | read |
| KN-LIT-368 | ON THE MERTENS CONJECTURE FOR ELLIPTIC CURVES OVER FINITE FIELDS | 2012 | `arxiv:1209.6087` | read |
| KN-LIT-369 | On the Surjectivity of Galois Representations Associated to Elliptic Curves over Number Fields | 2012 | `arxiv:1204.0046` | read |
| KN-LIT-370 | ONE HALF LOG DISCRIMINANT AND DIVISION POLYNOMIALS | 2012 | `arxiv:1207.5387` | read |
| KN-LIT-371 | Quasi-modular forms attached to elliptic curves: Hecke operators | 2012 | `arxiv:1205.2408` | read |
| KN-LIT-372 | SECOND p-DESCENTS ON ELLIPTIC CURVES | 2012 | `arxiv:1209.3085` | read |
| KN-LIT-373 | Secure Identity-Based Encryption in the Quantum Random Oracle Model? | 2012 | `eprint:2012/076` | read |
| KN-LIT-374 | SELMER RANKS OF QUADRATIC TWISTS OF ELLIPTIC CURVES WITH PARTIAL RATIONAL TWO-TORSION | 2012 | `arxiv:1201.5408` | read |
| KN-LIT-375 | Signature Schemes Secure against Hard-to-Invert Leakage | 2012 | `eprint:2012/045` | read |
| KN-LIT-37562e | Improving the efficiency of quantum circuits for information set decoding | 2023 | `doi:10.1145/3607256` | web |
| KN-LIT-376 | THE p-PARITY CONJECTURE FOR ELLIPTIC CURVES WITH A p-ISOGENY arXiv:1207.0431v3 [math.NT] 8 Apr 2014 KĘSTUTIS ČESNAVIČIUS | 2012 | `arxiv:1207.0431` | read |
| KN-LIT-377 | The power operation structure on Morava E-theory of height 2 at the prime | 2012 | `arxiv:1210.3730` | read |
| KN-LIT-378 | THE TRACE OF FROBENIUS OF ELLIPTIC CURVES AND THE p-ADIC GAMMA FUNCTION | 2012 | `arxiv:1205.5001` | read |
| KN-LIT-379 | USING SYMMETRIES IN THE INDEX CALCULUS FOR ELLIPTIC | 2012 | `eprint:2012/199` | read |
| KN-LIT-380 | A DEURING CRITERION FOR ABELIAN VARIETIES | 2013 | `arxiv:1311.5454` | read |
| KN-LIT-380ab7 | Full key-recovery cubic-time template attack on Classic McEliece decapsulation | 2025 | `eprint:2024/1694` | web |
| KN-LIT-381 | A local-global principle for isogenies of prime degree over number fields arXiv:1303.3809v2 [math.NT] 13 Jan 2014 Samuele Anni | 2013 | `arxiv:1303.3809` | read |
| KN-LIT-382 | A quantum circuit to find discrete logarithms on ordinary binary elliptic curves in depth O(log2 n) | 2013 | `arxiv:1306.1161` | read |
| KN-LIT-3822a6 | The Optimal Choice of Hypothesis Is the Weakest, Not the Shortest | 2023 | `arxiv:2301.12987v4` | full_text |
| KN-LIT-383 | A UNIFORM VERSION OF A FINITENESS CONJECTURE FOR CM ELLIPTIC CURVES | 2013 | `arxiv:1305.5241` | read |
| KN-LIT-384 | Authenticating Computation on Groups: New | 2013 | `eprint:2013/801` | read |
| KN-LIT-385 | Automatic Security Evaluation and (Related-key) Differential Characteristic Search: Application to SIMON, PRESENT, LBlock | 2013 | `eprint:2013/676` | read |
| KN-LIT-386 | Classification of Elliptic/Hyperelliptic Curves with Weak Coverings against the GHS Attack under an Isogeny Condition | 2013 | `eprint:2013/487` | read |
| KN-LIT-387 | COMPUTING ISOGENIES BETWEEN SUPERSINGULAR ELLIPTIC CURVES OVER Fp | 2013 | `arxiv:1310.7789` | read |
| KN-LIT-388 | CONSTRUCTING SUPERSINGULAR ELLIPTIC CURVES WITH A GIVEN | 2013 | `arxiv:1301.6875` | read |
| KN-LIT-389 | CRITERIA FOR IRREDUCIBILITY OF MOD p REPRESENTATIONS OF FREY CURVES | 2013 | `arxiv:1309.4748` | read |
| KN-LIT-38b647 | Reduction from sparse LPN to LPN, Dual Attack 3.0 | 2024 | `eprint:2023/1852` | web |
| KN-LIT-390 | Easy scalar decompositions for efficient scalar multiplication on elliptic curves and genus 2 Jacobians | 2013 | `arxiv:1310.5250` | read |
| KN-LIT-391 | ENDOMORPHISM ALGEBRAS OF FACTORS OF CERTAIN HYPERGEOMETRIC JACOBIANS | 2013 | `arxiv:1304.6202` | read |
| KN-LIT-392 | EXPLICIT POINTS ON THE LEGENDRE CURVE II | 2013 | `arxiv:1307.4251` | read |
| KN-LIT-393 | Families of fast elliptic curves from Q-curves | 2013 | `arxiv:1305.5400` | read |
| KN-LIT-394 | Formal groups and invariant differentials of elliptic curves | 2013 | `arxiv:1303.6706` | read |
| KN-LIT-395 | From Weak to Strong Zero-Knowledge and Applications? | 2013 | `eprint:2013/260` | read |
| KN-LIT-396 | GALOIS ACTION ON Q̄-ISOGENY CLASSES OF ABELIAN L-SURFACES WITH QUATERNIONIC MULTIPLICATION | 2013 | `arxiv:1304.6207` | read |
| KN-LIT-397 | In memory of Andrei Zelevinsky | 2013 | `arxiv:1310.2581` | read |
| KN-LIT-398 | International Journal of Computer Science and Business Informatics IJCSBI.ORG | 2013 | `arxiv:1309.0245` | read |
| KN-LIT-399 | Modularity and integral points on moduli schemes | 2013 | `arxiv:1310.7263` | read |
| KN-LIT-3c87b9 | RACE: a Rapid ARM Cryptographic Engine for code-based Classic McEliece PQC scheme | 2025 | `eprint:2025/2310` | web |
| KN-LIT-3c9f21 | A distinguisher for high rate McEliece cryptosystems | 2010 | `eprint:2010/331` | web |
| KN-LIT-3f2ee6 | Verifying Classic McEliece: examining the role of formal methods in post-quantum cryptography standardisation | 2022 | `eprint:2023/010` | web |
| KN-LIT-400 | On the class numbers of the fields of the pn-torsion points of certain elliptic curves over Q | 2013 | `arxiv:1307.7691` | read |
| KN-LIT-401 | ON THE ESSENTIAL DIMENSION OF COHERENT SHEAVES | 2013 | `arxiv:1306.6432` | read |
| KN-LIT-402 | ON THE FREY-MAZUR CONJECTURE OVER LOW GENUS CURVES | 2013 | `arxiv:1309.6568` | read |
| KN-LIT-403 | On the Product of Small Elkies Primes | 2013 | `arxiv:1301.0035` | read |
| KN-LIT-404 | Parallelizable Rate-1 Authenticated Encryption from Pseudorandom Functions Kazuhiko Minematsu | 2013 | `eprint:2013/628` | read |
| KN-LIT-405 | QUADRATIC TWISTS OF ELLIPTIC CURVES | 2013 | `arxiv:1312.3884` | read |
| KN-LIT-406 | Ranks of GL2 Iwasawa modules of elliptic curves | 2013 | `arxiv:1303.0710` | read |
| KN-LIT-407 | SELMER GROUPS AS FLAT COHOMOLOGY GROUPS arXiv:1301.4724v4 [math.NT] 10 Jul 2015 KĘSTUTIS ČESNAVIČIUS | 2013 | `arxiv:1301.4724` | read |
| KN-LIT-408 | SEQUENCES OF IRREDUCIBLE POLYNOMIALS OVER ODD PRIME FIELDS VIA ELLIPTIC CURVE ENDOMORPHISMS | 2013 | `arxiv:1308.6723` | read |
| KN-LIT-409 | Singular values of multiple eta-quotients for ramified primes | 2013 | `arxiv:1301.5521` | read |
| KN-LIT-410 | TETRAHEDRAL ELLIPTIC CURVES AND THE LOCAL-GLOBAL PRINCIPLE FOR ISOGENIES | 2013 | `arxiv:1306.6818` | read |
| KN-LIT-411 | THE DISTRIBUTION OF 2-SELMER RANKS OF QUADRATIC TWISTS OF ELLIPTIC CURVES WITH PARTIAL TWO-TORSION | 2013 | `arxiv:1307.7030` | read |
| KN-LIT-412 | The prime divisors of the number of points on abelian varieties | 2013 | `arxiv:1310.1007` | read |
| KN-LIT-413 | UPR-1250-T Chiral Four-Dimensional F-Theory Compactifications | 2013 | `arxiv:1306.3987` | read |
| KN-LIT-414 | A CONVERSE TO A THEOREM OF GROSS, ZAGIER, AND KOLYVAGIN | 2014 | `arxiv:1405.7294` | read |
| KN-LIT-415 | A NOTE ON SUPERSINGULAR ABELIAN VARIETIES | 2014 | `arxiv:1412.7107` | read |
| KN-LIT-416 | A TABLE OF ELLIPTIC CURVES OVER THE CUBIC FIELD OF DISCRIMINANT −23 | 2014 | `arxiv:1409.7911` | read |
| KN-LIT-417 | Algebraic functional equations and completely faithful Selmer groups | 2014 | `arxiv:1405.6180` | read |
| KN-LIT-418 | AN OPTIMAL REPRESENTATION FOR THE TRACE ZERO SUBGROUP | 2014 | `arxiv:1405.2733` | read |
| KN-LIT-419 | CRITERIA FOR p-ORDINARITY OF FAMILIES OF ELLIPTIC CURVES OVER INFINITELY MANY NUMBER FIELDS | 2014 | `arxiv:1404.3278` | read |
| KN-LIT-41f867 | On the McEliece public-key cryptosystem | 1988 | `doi:10.1007/springerreference_351` | web |
| KN-LIT-420 | Determination of elliptic curves by their adjoint p-adic L-functions | 2014 | `arxiv:1406.2676` | read |
| KN-LIT-421 | FINDING ELLIPTIC CURVES WITH A SUBGROUP OF PRESCRIBED SIZE | 2014 | `arxiv:1403.7887` | read |
| KN-LIT-422 | FROBENIUS DISTRIBUTION FOR PAIRS OF ELLIPTIC CURVES AND EXCEPTIONAL ISOGENIES FRANÇOIS CHARLES | 2014 | `arxiv:1411.2914` | read |
| KN-LIT-423 | Generation of class fields by using the Weber function | 2014 | `arxiv:1408.5650` | read |
| KN-LIT-424 | GENUS-2 CURVES AND JACOBIANS WITH A GIVEN NUMBER OF POINTS | 2014 | `arxiv:1403.6911` | read |
| KN-LIT-425 | HEEGNER POINTS ON CARTAN NON-SPLIT CURVES | 2014 | `arxiv:1403.7801` | read |
| KN-LIT-426 | HYPERELLIPTIC MODULAR CURVES X0 (n) AND ISOGENIES OF ELLIPTIC CURVES OVER QUADRATIC FIELDS | 2014 | `arxiv:1406.0655` | read |
| KN-LIT-427 | Indivisibility of Heegner points in the multiplicative case | 2014 | `arxiv:1407.1099` | read |
| KN-LIT-428 | Isogeny graphs with maximal real multiplication | 2014 | `arxiv:1407.6672` | read |
| KN-LIT-429 | On an analogue of the conjecture of Birch and Swinnerton-Dyer for Abelian schemes over higher dimensional bases over finite fields Timo Keller | 2014 | `arxiv:1410.5294` | read |
| KN-LIT-430 | On completely faithful Selmer groups of elliptic curves and Hida arXiv:1408.2599v3 [math.NT] 9 Jan 2015 deformations | 2014 | `arxiv:1408.2599` | read |
| KN-LIT-431 | ON FACTORIZATIONS OF MAPS BETWEEN CURVES | 2014 | `arxiv:1405.4753` | read |
| KN-LIT-432 | ON INVARIANTS OF ELLIPTIC CURVES ON AVERAGE | 2014 | `arxiv:1404.5700` | read |
| KN-LIT-433 | ON SERRE’S UNIFORMITY CONJECTURE FOR SEMISTABLE ELLIPTIC CURVES OVER TOTALLY REAL FIELDS | 2014 | `arxiv:1408.1279` | read |
| KN-LIT-434 | p-TORSION MONODROMY REPRESENTATIONS OF ELLIPTIC CURVES OVER GEOMETRIC FUNCTION FIELDS | 2014 | `arxiv:1403.7168` | read |
| KN-LIT-435 | SELMER GROUPS AND ANTICYCLOTOMIC Zp -EXTENSIONS | 2014 | `arxiv:1411.4685` | read |
| KN-LIT-436 | SOME REMARKS ON K-LATTICES AND THE ADELIC HEISENBERG GROUP FOR CM CURVES | 2014 | `arxiv:1407.3351` | read |
| KN-LIT-437 | SQUAREFREE PARTS OF POLYNOMIAL VALUES | 2014 | `arxiv:1407.4890` | read |
| KN-LIT-438 | STRONG MINIMALITY AND THE j-FUNCTION | 2014 | `arxiv:1402.4588` | read |
| KN-LIT-4388b3 | Hybrid decoding – classical-quantum trade-offs for information set decoding | 2022 | `eprint:2022/964` | web |
| KN-LIT-439 | Summation polynomial algorithms for elliptic curves in characteristic two | 2014 | `eprint:2014/806` | read |
| KN-LIT-440 | THE DISTRIBUTION OF THE TAMAGAWA RATIO IN THE FAMILY OF ELLIPTIC CURVES WITH A TWO-TORSION POINT | 2014 | `arxiv:1406.6745` | read |
| KN-LIT-441 | THE FREQUENCY OF ELLIPTIC CURVE GROUPS OVER PRIME | 2014 | `arxiv:1405.6923` | read |
| KN-LIT-442 | THE INVERSE GALOIS PROBLEM FOR ORTHOGONAL GROUPS | 2014 | `arxiv:1409.1151` | read |
| KN-LIT-443 | The Q-curve Construction for Endomorphism-Accelerated Elliptic Curves arXiv:1409.4526v2 [cs.CR] 24 Mar 2015 Benjamin Smith | 2014 | `arxiv:1409.4526` | read |
| KN-LIT-444 | The quartic Fermat equation in Hilbert class fields of imaginary quadratic fields | 2014 | `arxiv:1410.3008` | read |
| KN-LIT-445 | The structure of Selmer groups of elliptic curves and modular symbols | 2014 | `arxiv:1407.2465` | read |
| KN-LIT-4451 | Improving deep learning-based neural distinguisher with multiple ciphertext pairs for speck and Simon |  | `doi:10.1038/s41598-025-98251-1` | read |
| KN-LIT-446 | Time-Memory Trade-offs for Index Calculus in Genus | 2014 | `eprint:2014/346` | read |
| KN-LIT-447 | TORSION POINTS ON CM ELLIPTIC CURVES OVER REAL NUMBER FIELDS | 2014 | `arxiv:1411.2742` | read |
| KN-LIT-448 | Two-sources Randomness Extractors for Elliptic Curves | 2014 | `arxiv:1404.2226` | read |
| KN-LIT-449 | A classification of elliptic curves with respect to the GHS attack in odd characteristic | 2015 | `eprint:2015/805` | read |
| KN-LIT-450 | ABELIAN SURFACES GOOD AWAY FROM | 2015 | `arxiv:1504.03047` | read |
| KN-LIT-451 | AN ALGORITHM FOR CONSTRUCTING CERTAIN DIFFERENTIAL OPERATORS IN POSITIVE CHARACTERISTIC | 2015 | `arxiv:1503.01419` | read |
| KN-LIT-452 | Automata and the susceptibility of the square lattice Ising model modulo powers of primes | 2015 | `arxiv:1507.02872` | read |
| KN-LIT-453 | BEZOUT-TYPE THEOREMS FOR DIFFERENTIAL FIELDS | 2015 | `arxiv:1501.03121` | read |
| KN-LIT-454 | BOUNDS FOR THE LANG-TROTTER CONJECTURES | 2015 | `arxiv:1508.07682` | read |
| KN-LIT-4548 | IOSR Journal of Computer Engineering (IOSR-JCE) e-ISSN: 2278-0661,p-ISSN: 2278-8727, Volume 18 |  | `doi:10.9790/0661-1802040111` | read |
| KN-LIT-455 | Class groups and Selmer groups Journal of Number Theory, (56), 1996, 79 - 114 | 2015 | `arxiv:1507.08324` | read |
| KN-LIT-4558 | J. Math. Cryptol. 2020; 14:460ś485 Research Article |  | `doi:10.1515/jmc-2019-0029` | read |
| KN-LIT-456 | Complexity of ECDLP under the First Fall Degree Assumption (Draft) | 2015 | `eprint:2015/984` | read |
| KN-LIT-457 | Comprehensive Efficient Implementations of ECC on C54xx Family of Low-cost Digital Signal Processors | 2015 | `arxiv:1502.01872` | read |
| KN-LIT-4573 | Keccak |  | `doi:10.6028/nist.ir.7896` | read |
| KN-LIT-458 | Computing all elliptic curves over an arbitrary number field with prescribed primes of bad reduction | 2015 | `arxiv:1511.05108` | read |
| KN-LIT-459 | COMPUTING IMAGES OF GALOIS REPRESENTATIONS ATTACHED TO ELLIPTIC CURVES | 2015 | `arxiv:1504.07618` | read |
| KN-LIT-460 | Constraining Pseudorandom Functions Privately | 2015 | `eprint:2015/116` | read |
| KN-LIT-461 | Distribution of elliptic twins over fixed finite fields: Numerical results David Leon Gil | 2015 | `arxiv:1506.07269` | read |
| KN-LIT-462 | Edwards Curves and Gaussian Hypergeometric Series | 2015 | `arxiv:1501.03526` | read |
| KN-LIT-463 | ELLIPTIC CURVES, RANDOM MATRICES AND ORBITAL INTEGRALS | 2015 | `arxiv:1510.07068` | read |
| KN-LIT-464 | ENDOMORPHISM RINGS OF REDUCTIONS OF ELLIPTIC | 2015 | `arxiv:1509.07095` | read |
| KN-LIT-465 | FIELDS OF DEFINITION OF ELLIPTIC k-CURVES AND THE REALIZABILITY OF ALL GENUS 2 SATO–TATE GROUPS OVER A NUMBER FIELD | 2015 | `arxiv:1511.02322` | read |
| KN-LIT-466 | FINE SELMER GROUPS, HEEGNER POINTS AND ANTICYCLOTOMIC Zp -EXTENSIONS | 2015 | `arxiv:1503.06463` | read |
| KN-LIT-467 | FUNCTIONAL GRAPHS OF RATIONAL MAPS INDUCED BY ENDOMORPHISMS OF ORDINARY ELLIPTIC CURVES OVER FINITE FIELDS | 2015 | `arxiv:1509.05365` | read |
| KN-LIT-468 | GALOIS REPRESENTATIONS ATTACHED TO ABELIAN VARIETIES OF CM TYPE by Davide Lombardo | 2015 | `arxiv:1506.04734` | read |
| KN-LIT-469 | GENERALIZED HEEGNER CYCLES AT EISENSTEIN PRIMES AND THE KATZ p-ADIC L-FUNCTION | 2015 | `arxiv:1512.05032` | read |
| KN-LIT-470 | HORIZONTAL ISOGENY GRAPHS OF ORDINARY ABELIAN | 2015 | `arxiv:1506.00522` | read |
| KN-LIT-471 | INDEPENDENCE OF THE ZEROS OF ELLIPTIC CURVE L-FUNCTIONS OVER FUNCTION FIELDS | 2015 | `arxiv:1502.05294` | read |
| KN-LIT-472 | INTEGRAL IWASAWA THEORY OF GALOIS REPRESENTATIONS FOR NON-ORDINARY PRIMES | 2015 | `arxiv:1511.06986` | read |
| KN-LIT-473 | ISOGENIES OF NON-CM ELLIPTIC CURVES WITH RATIONAL j-INVARIANTS OVER NUMBER FIELDS | 2015 | `arxiv:1506.03127` | read |
| KN-LIT-474 | ISOGENOUS DECOMPOSITION OF THE JACOBIAN OF GENERALIZED FERMAT CURVES | 2015 | `arxiv:1507.02903` | read |
| KN-LIT-475 | Last fall degree, HFE, and Weil descent attacks on ECDLP ? | 2015 | `eprint:2015/573` | read |
| KN-LIT-476 | MODULAR ELLIPTIC CURVES OVER REAL ABELIAN FIELDS AND THE GENERALIZED FERMAT EQUATION x2l + y 2m = z p | 2015 | `arxiv:1506.02860` | read |
| KN-LIT-477 | On Generalized First Fall Degree Assumptions | 2015 | `eprint:2015/358` | read |
| KN-LIT-478 | ON HEEGNER POINTS FOR PRIMES OF ADDITIVE REDUCTION RAMIFYING IN THE BASE FIELD | 2015 | `arxiv:1505.08059` | read |
| KN-LIT-479 | ON SIGN CHANGES OF CUSP FORMS AND THE HALTING OF AN ALGORITHM TO CONSTRUCT A SUPERSINGULAR ELLIPTIC CURVE WITH A GIVEN ENDOMORPHISM RING | 2015 | `arxiv:1511.02082` | read |
| KN-LIT-47b29b | Progressive sieving-style information-set decoding algorithm | 2026 | `eprint:2026/633` | web |
| KN-LIT-480 | On the Bousfield-Kan spectral sequence for Qp2qp3q arXiv:1507.02650v1 [math.AT] 9 Jul 2015 Donald M. Larson ̊ | 2015 | `arxiv:1507.02650` | read |
| KN-LIT-481 | ON THE CONSTRUCTION OF IRREDUCIBLE POLYNOMIALS OVER FINITE FIELDS VIA ODD PRIME DEGREE ENDOMORPHISMS OF ELLIPTIC CURVES | 2015 | `arxiv:1511.00929` | read |
| KN-LIT-482 | ON THE GREATEST PRIME FACTOR OF SOME DIVISIBILITY SEQUENCES | 2015 | `arxiv:1505.06500` | read |
| KN-LIT-483 | On Twists of A Family of Elliptic Curves and Their L−Function | 2015 | `arxiv:1511.07581` | read |
| KN-LIT-484 | PLUS/MINUS HEEGNER POINTS AND IWASAWA THEORY OF ELLIPTIC CURVES AT SUPERSINGULAR PRIMES | 2015 | `arxiv:1503.07812` | read |
| KN-LIT-485 | Poisson distribution of a prime counting function corresponding to elliptic curves | 2015 | `arxiv:1503.01018` | read |
| KN-LIT-4850 | Maps between curves and arithmetic obstructions |  | `doi:10.1090/conm/722/14532` | read |
| KN-LIT-486 | PRIME NUMBER RACES FOR ELLIPTIC CURVES OVER FUNCTION FIELDS | 2015 | `arxiv:1502.05295` | read |
| KN-LIT-487 | QUICKLY CONSTRUCTING CURVES OF GENUS 4 WITH MANY POINTS | 2015 | `arxiv:1506.04478` | read |
| KN-LIT-488 | SEQUENCES OF IRREDUCIBLE POLYNOMIALS OVER ODD | 2015 | `arxiv:1501.01269` | read |
| KN-LIT-489 | SOME ARITHMETIC PROPERTIES ON NONSTANDARD RATIONALS | 2015 | `arxiv:1509.06474` | read |
| KN-LIT-490 | THE CM CLASS NUMBER ONE PROBLEM FOR CURVES OF GENUS | 2015 | `arxiv:1511.04869` | read |
| KN-LIT-491 | A BOUND ON THE PRIMES OF BAD REDUCTION FOR CM CURVES OF GENUS | 2016 | `arxiv:1609.05826` | read |
| KN-LIT-492 | ABELIAN n-DIVISION FIELDS OF ELLIPTIC CURVES AND BRAUER GROUPS OF PRODUCT KUMMER & ABELIAN SURFACES | 2016 | `arxiv:1606.09240` | read |
| KN-LIT-493 | Arithmetic of split Kummer surfaces: Montgomery endomorphism of Edwards products | 2016 | `arxiv:1601.03680` | read |
| KN-LIT-4932 | MinimaLT: Minimal-latency Networking Through Better Security |  | `doi:10.1145/2508859.2516737` | read |
| KN-LIT-494 | Balloon Hashing: A Memory-Hard Function | 2016 | `eprint:2016/027` | read |
| KN-LIT-495 | CANONICAL HEIGHTS ON GENUS TWO JACOBIANS | 2016 | `arxiv:1603.00640` | read |
| KN-LIT-495e7f | Structural cryptanalysis of McEliece schemes with compact keys | 2016 | `eprint:2014/210` | web |
| KN-LIT-496 | Composite Genus One Belyi Maps | 2016 | `arxiv:1610.08075` | read |
| KN-LIT-497 | Contemporary Mathematics The geometry of efficient arithmetic on elliptic curves | 2016 | `arxiv:1601.03665` | read |
| KN-LIT-498 | CYCLIC ÉTALE COVERINGS OF GENERIC CURVES AND ORDINARINESS OF DORMANT OPERS | 2016 | `arxiv:1602.07061` | read |
| KN-LIT-499 | Efficient Secure Multiparty Computation with Identifiable Abort | 2016 | `eprint:2016/187` | read |
| KN-LIT-49a052 | An attack on a modified Niederreiter encryption scheme | 2006 | `doi:10.1007/11745853_2` | web |
| KN-LIT-4a6dd5 | Classic McEliece implementation with low memory footprint | 2020 | `eprint:2021/138` | web |
| KN-LIT-4acef4 | One Discrete Gaussian Sample in 2^{n/2+o(n)} Time | 2026 | `eprint:2026/1599` | read |
| KN-LIT-4c1133 | Compact HQC with new (un)balance | 2026 | `eprint:2026/461` | web |
| KN-LIT-4c8135 | Polynomial time key-recovery attack on high rate random alternant codes | 2024 | `arxiv:2304.14757` | web |
| KN-LIT-4fa25d | Classic McEliece: conservative code-based cryptography: what plaintext confirmation means | 2022 | `url:classic.mceliece.org/mceliece-pc-20221023.pdf` | web |
| KN-LIT-500 | ELLIPTIC CURVES IN ISOGENY CLASSES | 2016 | `arxiv:1611.05258` | read |
| KN-LIT-501 | ELLIPTIC GAUSS SUMS AND SCHOOF’S ALGORITHM | 2016 | `arxiv:1601.03227` | read |
| KN-LIT-502 | EXTENSIONS OF CM ELLIPTIC CURVES AND ORBIT COUNTING ON THE PROJECTIVE LINE | 2016 | `arxiv:1608.01390` | read |
| KN-LIT-503 | FAST COMPUTATION OF ISOMORPHISMS BETWEEN FINITE FIELDS USING ELLIPTIC CURVES | 2016 | `arxiv:1604.03072` | read |
| KN-LIT-504 | GOVERNING FIELDS AND STATISTICS FOR 4-SELMER | 2016 | `arxiv:1607.07860` | read |
| KN-LIT-505 | GROWTH OF TORSION GROUPS OF ELLIPTIC CURVES UPON BASE CHANGE | 2016 | `arxiv:1609.02515` | read |
| KN-LIT-506 | GROWTH OF TORSION OF ELLIPTIC CURVES WITH ODD-ORDER TORSION OVER QUADRATIC | 2016 | `arxiv:1604.01153` | read |
| KN-LIT-507 | HEEGNER POINTS AT EISENSTEIN PRIMES AND TWISTS OF ELLIPTIC CURVES | 2016 | `arxiv:1609.06687` | read |
| KN-LIT-508 | INDIVISIBILITY OF CLASS NUMBERS OF IMAGINARY | 2016 | `arxiv:1612.04443` | read |
| KN-LIT-509 | ISOGENY GRAPHS OF ORDINARY ABELIAN VARIETIES | 2016 | `arxiv:1609.09793` | read |
| KN-LIT-510 | MODULAR INVARIANTS AND ISOGENIES | 2016 | `arxiv:1611.01094` | read |
| KN-LIT-511 | ON BHARGAVA’S HEURISTICS FOR GL2 (Fp )-NUMBER FIELDS AND THE NUMBER OF ELLIPTIC CURVES OF BOUNDED CONDUCTOR | 2016 | `arxiv:1610.09467` | read |
| KN-LIT-512 | On p-adic Differential Equations with Separation of Variables arXiv:1602.00244v2 [cs.SC] 3 May 2016 | 2016 | `arxiv:1602.00244` | read |
| KN-LIT-513 | ON PRYM VARIETIES FOR THE COVERINGS OF SOME SINGULAR PLANE CURVES | 2016 | `arxiv:1609.03981` | read |
| KN-LIT-514 | ON THE BIRCH AND SWINNERTON-DYER CONJECTURE FOR CM ELLIPTIC CURVES OVER Q | 2016 | `arxiv:1605.01481` | read |
| KN-LIT-515 | ON THE GAPS BETWEEN NON-ZERO FOURIER COEFFICIENTS OF CUSP FORMS OF HIGHER WEIGHT | 2016 | `arxiv:1602.05745` | read |
| KN-LIT-516 | On the local-global divisibility of torsion points on elliptic curves and GL2-type varieties | 2016 | `arxiv:1609.00410` | read |
| KN-LIT-517 | On the plus and the minus Selmer groups for elliptic curves at supersingular primes | 2016 | `arxiv:1607.03612` | read |
| KN-LIT-518 | ON THE RANKS OF ELLIPTIC CURVES WITH ISOGENIES | 2016 | `arxiv:1611.01329` | read |
| KN-LIT-519 | On the Representation of Primes by Binary Quadratic Forms, and Elliptic Curves | 2016 | `arxiv:1604.06586` | read |
| KN-LIT-520 | PREDICTING THE ELLIPTIC CURVE CONGRUENTIAL GENERATOR LÁSZLÓ MÉRAI | 2016 | `arxiv:1609.03305` | read |
| KN-LIT-521 | Ranks of the Rational Points of Abelian Varieties over Ramified Fields, and Iwasawa Theory for Primes with Non-Ordinary Reduction | 2016 | `arxiv:1608.03315` | read |
| KN-LIT-522 | REDUCTIONS OF POINTS ON ALGEBRAIC GROUPS | 2016 | `arxiv:1612.02847` | read |
| KN-LIT-523 | REMARKS ON AUTOMORPHY OF RESIDUALLY DIHEDRAL REPRESENTATIONS | 2016 | `arxiv:1607.04750` | read |
| KN-LIT-524 | Root numbers and parity of local Iwasawa invariants | 2016 | `arxiv:1608.08078` | read |
| KN-LIT-525 | SHADOW LINES IN THE ARITHMETIC OF ELLIPTIC CURVES | 2016 | `arxiv:1610.08729` | read |
| KN-LIT-526 | Spins of prime ideals and the negative Pell equation x2 − 2py 2 = −1 | 2016 | `arxiv:1611.10337` | read |
| KN-LIT-527 | Submitted exclusively to the London Mathematical Society doi:10.1112/0000/000000 arXiv:1603.00711v2 [math.AG] 24 May 2016 Explicit isogenies in quadratic time in any characteristic | 2016 | `arxiv:1603.00711` | read |
| KN-LIT-528 | Targeted Homomorphic Attribute-Based Encryption? | 2016 | `eprint:2016/691` | read |
| KN-LIT-529 | THE 1-EIGENSPACE FOR MATRICES IN GL2 (Zl ) | 2016 | `arxiv:1612.02845` | read |
| KN-LIT-52ce4c | Quantum Algorithms for Lattice Problems (Chen 2024) — main LWE claim RETRACTED | 2024 | `eprint:2024/555` | web |
| KN-LIT-530 | The average size of the 3-isogeny Selmer groups of elliptic curves y 2 = x3 + k | 2016 | `arxiv:1610.05759` | read |
| KN-LIT-531 | The Brauer group of the moduli stack of elliptic curves | 2016 | `arxiv:1608.00851` | read |
| KN-LIT-532 | THE MANIN–STEVENS CONSTANT IN THE SEMISTABLE CASE arXiv:1604.02165v2 [math.NT] 14 Oct 2018 KĘSTUTIS ČESNAVIČIUS | 2016 | `arxiv:1604.02165` | read |
| KN-LIT-533 | TORSION POINTS AND GALOIS REPRESENTATIONS ON CM ELLIPTIC CURVES | 2016 | `arxiv:1612.03229` | read |
| KN-LIT-534 | A Survey on Hardware Implementations of Elliptic Curve Cryptosystems | 2017 | `arxiv:1710.08336` | read |
| KN-LIT-535 | A UNIVERSAL TORELLI THEOREM FOR ELLIPTIC SURFACES | 2017 | `arxiv:1706.00564` | read |
| KN-LIT-536 | A VARIANT OF A THEOREM BY AILON-RUDNICK FOR ELLIPTIC CURVES | 2017 | `arxiv:1703.01343` | read |
| KN-LIT-537 | ABELIAN VARIETIES ISOGENOUS TO A POWER OF AN ELLIPTIC CURVE OVER A GALOIS EXTENSION arXiv:1706.04963v2 [math.AG] 24 Jan 2018 ISABEL VOGT | 2017 | `arxiv:1706.04963` | read |
| KN-LIT-538 | Access Control Encryption for General Policies from Standard Assumptions | 2017 | `eprint:2017/467` | read |
| KN-LIT-539 | ANALOGUES OF IWASAWA’S μ = 0 CONJECTURE AND THE WEAK LEOPOLDT CONJECTURE FOR A NON-CYCLOTOMIC Z2 -EXTENSION | 2017 | `arxiv:1711.01697` | read |
| KN-LIT-540 | APPLICATIONS OF THE SQUARE SIEVE TO A CONJECTURE | 2017 | `arxiv:1710.02125` | read |
| KN-LIT-541 | BOUNDS OF THE RANK OF THE MORDELL–WEIL GROUP OF JACOBIANS OF HYPERELLIPTIC CURVES | 2017 | `arxiv:1708.07896` | read |
| KN-LIT-542 | CARTAN IMAGES AND l-TORSION POINTS OF ELLIPTIC CURVES WITH RATIONAL j-INVARIANT arXiv:1702.00121v4 [math.NT] 26 Nov 2017 ORON Y. PROPP | 2017 | `arxiv:1702.00121` | read |
| KN-LIT-543 | Chapter 1 arXiv:1701.01927v2 [math.NT] 19 Apr 2017 Isogenies for point counting on genus two hyperelliptic curves | 2017 | `arxiv:1701.01927` | read |
| KN-LIT-544 | CHARACTER SUMS FOR ELLIPTIC CURVE DENSITIES | 2017 | `arxiv:1703.04154` | read |
| KN-LIT-545 | COMPOSITE IMAGES OF GALOIS FOR ELLIPTIC CURVES OVER Q & | 2017 | `arxiv:1707.04646` | read |
| KN-LIT-546 | Computation of a 768-bit prime field discrete logarithm Thorsten Kleinjung12 | 2017 | `eprint:2017/067` | read |
| KN-LIT-547 | COMPUTING THE CASSELS-TATE PAIRING ON 3-ISOGENY SELMER GROUPS VIA CUBIC NORM EQUATIONS | 2017 | `arxiv:1711.02432` | read |
| KN-LIT-548 | CONSTRUCTING PERMUTATION RATIONAL FUNCTIONS FROM ISOGENIES | 2017 | `arxiv:1707.06134` | read |
| KN-LIT-549 | Counterexamples to the local-global divisibility over elliptic curves | 2017 | `arxiv:1705.01880` | read |
| KN-LIT-550 | Decomposability and Mordell-Weil ranks of Jacobians using Picard numbers Soohyun Park | 2017 | `arxiv:1712.04905` | read |
| KN-LIT-551 | Elliptic curves maximal over extensions of finite base fields | 2017 | `arxiv:1709.01352` | read |
| KN-LIT-552 | ELLIPTIC CURVES OF FIBONACCI PRIME ORDER OVER Fp | 2017 | `arxiv:1710.05687` | read |
| KN-LIT-553 | EXCEPTIONAL SPLITTING OF REDUCTIONS OF ABELIAN SURFACES | 2017 | `arxiv:1706.08154` | read |
| KN-LIT-554 | EXCEPTIONAL ZERO FORMULAE FOR ANTICYCLOTOMIC p-ADIC L-FUNCTIONS OF ELLIPTIC CURVES IN THE RAMIFIED CASE | 2017 | `arxiv:1707.06019` | read |
| KN-LIT-555 | Explicit Bound for the Prime Ideal Theorem in Residue Classes | 2017 | `arxiv:1709.09914` | read |
| KN-LIT-556 | FINE SELMER GROUPS AND ISOGENY INVARIANCE | 2017 | `arxiv:1704.04893` | read |
| KN-LIT-557 | HORIZONTAL VARIATION OF TATE–SHAFAREVICH GROUPS | 2017 | `arxiv:1712.02148` | read |
| KN-LIT-558 | International Journal of Computer Science and Information Security (IJCSIS) | 2017 | `arxiv:1707.04892` | read |
| KN-LIT-559 | LOCAL-GLOBAL QUESTIONS FOR DIVISIBILITY IN COMMUTATIVE ALGEBRAIC GROUPS | 2017 | `arxiv:1706.03726` | read |
| KN-LIT-55e037 | Optimizing key recovery in Classic McEliece: advanced error correction for noisy side-channel measurements | 2025 | `eprint:2025/802` | web |
| KN-LIT-560 | Luca De Feo | 2017 | `arxiv:1711.04062` | read |
| KN-LIT-561 | Multi-Collision Resistant Hash Functions and their Applications | 2017 | `eprint:2017/489` | read |
| KN-LIT-562 | ON A LOCAL INVARIANT OF ELLIPTIC CURVES WITH A p-ISOGENY | 2017 | `arxiv:1703.02148` | read |
| KN-LIT-563 | ON ELLIPTIC CURVES OF PRIME POWER CONDUCTOR OVER IMAGINARY QUADRATIC FIELDS WITH CLASS NUMBER ONE | 2017 | `arxiv:1711.02170` | read |
| KN-LIT-564 | ON FREE RESOLUTIONS OF IWASAWA MODULES | 2017 | `arxiv:1707.01485` | read |
| KN-LIT-565 | ON THE ELLIPTIC CURVE ENDOMORPHISM GENERATOR LÁSZLÓ MÉRAI | 2017 | `arxiv:1706.08710` | read |
| KN-LIT-566 | ON THE JOINT DISTRIBUTION OF Selφ (E/Q) AND Selφ̂ (E ′ /Q) IN QUADRATIC TWIST FAMILIES | 2017 | `arxiv:1702.02687` | read |
| KN-LIT-567 | ON THE MAIN CONJECTURE OF IWASAWA THEORY FOR CERTAIN NON-CYCLOTOMIC Zp -EXTENSIONS | 2017 | `arxiv:1711.07554` | read |
| KN-LIT-5677ae | Security analysis of the Classic McEliece, HQC and BIKE schemes in low memory | 2023 | `eprint:2023/428` | web |
| KN-LIT-568 | On the vanishing of almost all primary components of the Shafarevich-Tate group of elliptic curves over the rationals François Destrempes | 2017 | `arxiv:1703.02215` | read |
| KN-LIT-569 | PURSUING POLYNOMIAL BOUNDS ON TORSION | 2017 | `arxiv:1705.10401` | read |
| KN-LIT-570 | Ranks of rational points of the Jacobian varieties of hyperelliptic curves | 2017 | `arxiv:1702.07837` | read |
| KN-LIT-571 | SELMER GROUPS AND ANTICYCLOTOMIC Zp -EXTENSIONS II | 2017 | `arxiv:1709.06455` | read |
| KN-LIT-572 | SERRE’S UNIFORMITY CONJECTURE FOR ELLIPTIC CURVES WITH RATIONAL CYCLIC ISOGENIES | 2017 | `arxiv:1702.01985` | read |
| KN-LIT-573 | Shifted Poisson geometry and meromorphic matrix algebras over an elliptic curve | 2017 | `arxiv:1712.01659` | read |
| KN-LIT-574 | Super-Isolated Elliptic Curves and Abelian Surfaces in Cryptography | 2017 | `arxiv:1705.02316` | read |
| KN-LIT-575 | Symmetry, Integrability and Geometry: Methods and Applications | 2017 | `arxiv:1711.05842` | read |
| KN-LIT-576 | THE GENERALIZED FERMAT EQUATION WITH EXPONENTS 2, 3, n | 2017 | `arxiv:1703.05058` | read |
| KN-LIT-577 | The Square Sieve and a Lang-Trotter Question for Generic Abelian Varieties | 2017 | `arxiv:1702.03017` | read |
| KN-LIT-578 | THREE-ISOGENY SELMER GROUPS AND RANKS OF ABELIAN VARIETIES IN QUADRATIC TWIST FAMILIES OVER A NUMBER FIELD | 2017 | `arxiv:1709.09790` | read |
| KN-LIT-579 | TORSION POINTS ON ELLIPTIC CURVES OVER NUMBER FIELDS OF SMALL DEGREE | 2017 | `arxiv:1707.00364` | read |
| KN-LIT-580 | Universal Finite Subgroup of the Tate Curve | 2017 | `arxiv:1708.08637` | read |
| KN-LIT-581 | Watermarking Cryptographic Functionalities from Standard Lattice Assumptions | 2017 | `eprint:2017/380` | read |
| KN-LIT-582 | A First-Order SCA Resistant AES without Fresh Randomness | 2018 | `eprint:2018/172` | read |
| KN-LIT-5823 | PQConnect: Automated Post-Quantum End-to-End Tunnels |  | `doi:10.14722/ndss.2025.241879` | read |
| KN-LIT-582d77 | Finding Preimages in Full MD5 Faster Than Exhaustive Search | 2009 | `doi:10.1007/978-3-642-01001-9_8` | metadata |
| KN-LIT-583 | A LOCAL-GLOBAL PRINCIPLE FOR ISOGENIES OF COMPOSITE DEGREE | 2018 | `arxiv:1801.05355` | read |
| KN-LIT-584 | A New Algorithm for Double Scalar Multiplication over Koblitz Curves | 2018 | `arxiv:1801.08589` | read |
| KN-LIT-585 | A note on the security of CSIDH | 2018 | `arxiv:1806.03656` | read |
| KN-LIT-586 | A Systematic Study of the Impact of Graphical Models on Inference-based Attacks on AES | 2018 | `eprint:2018/671` | read |
| KN-LIT-587 | Adaptively Secure Distributed PRFs from LWE? | 2018 | `eprint:2018/927` | read |
| KN-LIT-588 | AN UNEXPECTED TRACE RELATION OF CM POINTS | 2018 | `arxiv:1806.11337` | read |
| KN-LIT-589 | ANTICYCLOTOMIC p-ADIC L-FUNCTIONS FOR ELLIPTIC CURVES AT SOME ADDITIVE REDUCTION PRIMES | 2018 | `arxiv:1801.01619` | read |
| KN-LIT-590 | Cache-Attacks on the ARM TrustZone implementations of AES-256 and AES-256-GCM via GPU-based analysis | 2018 | `eprint:2018/621` | read |
| KN-LIT-591 | CODIMENSION TWO CYCLES IN IWASAWA THEORY AND ELLIPTIC CURVES WITH SUPERSINGULAR REDUCTION | 2018 | `arxiv:1806.07214` | read |
| KN-LIT-592 | Computing the endomorphism ring of an ordinary abelian surface over a finite field | 2018 | `arxiv:1810.12270` | read |
| KN-LIT-593 | CONSTRUCTING PICARD CURVES WITH COMPLEX MULTIPLICATION USING THE CHINESE REMAINDER THEOREM | 2018 | `arxiv:1803.00514` | read |
| KN-LIT-594 | Curves, Jacobians, and Cryptography | 2018 | `arxiv:1807.05270` | read |
| KN-LIT-595 | CYCLES IN THE SUPERSINGULAR l-ISOGENY GRAPH AND CORRESPONDING ENDOMORPHISMS | 2018 | `arxiv:1804.04063` | read |
| KN-LIT-596 | Efficient Construction of a Substitution Box Based on a Mordell Elliptic Curve Over a Finite Field | 2018 | `arxiv:1809.11057` | read |
| KN-LIT-597 | Elliptic surfaces over P1 and large class groups of number fields | 2018 | `arxiv:1811.08166` | read |
| KN-LIT-598 | ENDOMORPHISM ALGEBRAS OF GEOMETRICALLY SPLIT ABELIAN SURFACES OVER Q | 2018 | `arxiv:1807.10010` | read |
| KN-LIT-599 | EVALUATION OF GAUSSIAN HYPERGEOMETRIC SERIES USING HUFF’S MODELS OF ELLIPTIC CURVES | 2018 | `arxiv:1805.08475` | read |
| KN-LIT-5f3698 | Sloppy Alice attacks! Adaptive chosen ciphertext attacks on the McEliece public-key cryptosystem | 2002 | `doi:10.1007/978-1-4757-3585-7_7` | web |
| KN-LIT-5f8f0a | Code-based cryptography | 2009 | `doi:10.1007/978-3-540-88702-7_4` | web |
| KN-LIT-5ff88f | Polynomial time key-recovery attack on high rate random alternant codes (boundary completed: the Goppa exclusion is phase-scoped, present-tense, unproved, and conjectured by its authors to fall) | 2024 | `arxiv:2304.14757v3` | transcription_of_full_text_at_recorded_sha256 |
| KN-LIT-600 | Fiat-Shamir and Correlation Intractability from Strong KDM-Secure Encryption? | 2018 | `eprint:2018/131` | read |
| KN-LIT-601 | First-Order Masking with Only Two Random Bits | 2018 | `eprint:2018/1007` | read |
| KN-LIT-602 | GALOIS REPRESENTATIONS ATTACHED TO ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION ÁLVARO LOZANO-ROBLEDO | 2018 | `arxiv:1809.02584` | read |
| KN-LIT-603 | GENERATING FUNCTIONS FOR POWER MOMENTS OF ELLIPTIC CURVES OVER Fp | 2018 | `arxiv:1807.00749` | read |
| KN-LIT-604 | Growth of the analytic rank of modular elliptic curves over quintic extensions | 2018 | `arxiv:1802.07290` | read |
| KN-LIT-605 | Hard Isogeny Problems over RSA Moduli and Groups with Infeasible Inversion | 2018 | `arxiv:1810.00022` | read |
| KN-LIT-606 | How Does Strict Parallelism Affect Security? A Case Study on the Side-Channel Attacks against GPU-based Bitsliced AES Implementation | 2018 | `eprint:2018/1080` | read |
| KN-LIT-607 | Improved Key Recovery Attacks on Reduced-Round | 2018 | `eprint:2018/527` | read |
| KN-LIT-608 | Isolated Curves and the MOV Attack Travis Scholl | 2018 | `eprint:2018/307` | read |
| KN-LIT-609 | Kolyvagin’s result on the vanishing of X(E/K)[p∞] and its consequences for anticyclotomic Iwasawa theory | 2018 | `arxiv:1808.09544` | read |
| KN-LIT-610 | La constante de Manin et le degré modulaire d’une courbe elliptique | 2018 | `arxiv:1805.01622` | read |
| KN-LIT-611 | LIE INVARIANT FROBENIUS LIFTS ON LINEAR ALGEBRAIC GROUPS | 2018 | `arxiv:1808.01289` | read |
| KN-LIT-612 | MOD-2 DIHEDRAL GALOIS REPRESENTATIONS OF PRIME CONDUCTOR | 2018 | `arxiv:1806.04653` | read |
| KN-LIT-613 | Multi-Theorem Preprocessing NIZKs from Lattices | 2018 | `eprint:2018/272` | read |
| KN-LIT-614 | MULTIPARTY NON-INTERACTIVE KEY EXCHANGE AND MORE FROM ISOGENIES ON ELLIPTIC CURVES arXiv:1807.03038v3 [cs.CR] 31 Aug 2018 | 2018 | `arxiv:1807.03038` | read |
| KN-LIT-615 | No singular modulus is a unit | 2018 | `arxiv:1805.07167` | read |
| KN-LIT-616 | No-signaling Linear PCPs | 2018 | `eprint:2018/649` | read |
| KN-LIT-617 | NON-DIVISIBLE CYCLES ON PRODUCTS OF VERY GENERAL ABELIAN VARIETIES | 2018 | `arxiv:1806.09195` | read |
| KN-LIT-618 | NON-VANISHING THEOREMS FOR CENTRAL L-VALUES OF SOME ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2018 | `arxiv:1811.07595` | read |
| KN-LIT-619 | ON A CONJECTURE OF BUIUM AND POONEN | 2018 | `arxiv:1803.04946` | read |
| KN-LIT-620 | ON ASYMPTOTIC FERMAT OVER THE Z2 -EXTENSION OF Q | 2018 | `arxiv:1804.02849` | read |
| KN-LIT-621 | ON CONJECTURAL RANK PARITIES OF QUARTIC AND SEXTIC TWISTS OF ELLIPTIC CURVES | 2018 | `arxiv:1809.04244` | read |
| KN-LIT-622 | On Division Polynomial PIT and Supersingularity | 2018 | `arxiv:1801.02664` | read |
| KN-LIT-623 | ON SUPERSPECIAL ABELIAN SURFACES AND TYPE NUMBERS OF TOTALLY DEFINITE QUATERNION ALGEBRAS | 2018 | `arxiv:1809.04316` | read |
| KN-LIT-624 | ON THE DEGREE OF THE p-TORSION FIELD OF ELLIPTIC CURVES | 2018 | `arxiv:1804.07627` | read |
| KN-LIT-625 | On the existence of superspecial nonhyperelliptic curves of genus 4 arXiv:1804.09063v2 [math.AG] 23 Jun 2019 Momonari Kudo | 2018 | `arxiv:1804.09063` | read |
| KN-LIT-626 | ON THE NON-VANISHING OF p-ADIC HEIGHTS ON CM ABELIAN | 2018 | `arxiv:1803.09268` | read |
| KN-LIT-627 | ON THE STRUCTURE OF SIGNED SELMER GROUPS arXiv:1807.07607v2 [math.NT] 25 Apr 2019 GAUTIER PONSINET | 2018 | `arxiv:1807.07607` | read |
| KN-LIT-628 | ON THE Λ-COTORSION SUBGROUP OF THE SELMER GROUP | 2018 | `arxiv:1812.00207` | read |
| KN-LIT-629 | Order-LWE and the Hardness of Ring-LWE with Entropic Secrets? | 2018 | `eprint:2018/494` | read |
| KN-LIT-630 | p-ADIC GROSS–ZAGIER FORMULA AT CRITICAL SLOPE AND A CONJECTURE OF PERRIN-RIOU | 2018 | `arxiv:1811.08216` | read |
| KN-LIT-631 | pr -SELMER COMPANION MODULAR FORMS | 2018 | `arxiv:1806.04944` | read |
| KN-LIT-632 | Pre- and post-quantum Diffie–Hellman from groups, actions, and isogenies | 2018 | `arxiv:1809.04803` | read |
| KN-LIT-633 | PROJECTIVE GEOMETRIES ARISING FROM ELEKES-SZABÓ PROBLEMS | 2018 | `arxiv:1806.03422` | read |
| KN-LIT-634 | Quantum FHE (Almost) As Secure As Classical? | 2018 | `eprint:2018/338` | read |
| KN-LIT-635 | Quasi-Optimal SNARGs via Linear Multi-Prover Interactive Proofs | 2018 | `eprint:2018/133` | read |
| KN-LIT-636 | Ramanujan graphs in cryptography | 2018 | `arxiv:1806.05709` | read |
| KN-LIT-6361 | Sato-Tate groups of some weight 3 motives |  | `doi:10.1090/conm/663/13350` | read |
| KN-LIT-6362 | Sato-Tate groups of y 2 = x8 + c and y 2 = x7 − cx |  | `doi:10.1090/conm/663/13351` | read |
| KN-LIT-6363 | Sato–Tate groups of abelian threefolds: |  | `doi:10.1090/conm/770/15432` | read |
| KN-LIT-637 | Ramification in Division Fields and Sporadic Points on Modular Curves | 2018 | `arxiv:1810.04809` | read |
| KN-LIT-638 | RANKS OF ELLIPTIC CURVES OVER Z2p -EXTENSIONS | 2018 | `arxiv:1809.10127` | read |
| KN-LIT-63884a | Key-recovery fault injection attack on the Classic McEliece KEM | 2022 | `eprint:2022/1529` | web |
| KN-LIT-639 | Round Optimal Black-Box “Commit-and-Prove” | 2018 | `eprint:2018/921` | read |
| KN-LIT-640 | Semisimple pointed isogeny graphs for abelian varieties | 2018 | `arxiv:1803.05194` | read |
| KN-LIT-641 | Simulations of Optical Emissions for Attacking | 2018 | `eprint:2018/291` | read |
| KN-LIT-642 | SINGULAR UNITS AND ISOGENIES BETWEEN CM ELLIPTIC CURVES | 2018 | `arxiv:1810.13214` | read |
| KN-LIT-643 | Solving ECDLP via List Decoding | 2018 | `eprint:2018/795` | read |
| KN-LIT-644 | Sub-logarithmic Distributed Oblivious RAM with Small Block Size? | 2018 | `arxiv:1802.05145` | read |
| KN-LIT-644dfd | Hybrid-grained GPU implementations for the Classic McEliece | 2025 | `doi:10.1109/ispa67752.2025.00164` | web |
| KN-LIT-645 | Succinct Garbling Schemes from Functional Encryption through a Local Simulation Paradigm? | 2018 | `eprint:2018/759` | read |
| KN-LIT-646 | The average number of subgroups of elliptic curves over finite fields | 2018 | `arxiv:1811.10149` | read |
| KN-LIT-647 | The Riemann-Roch strategy Complex lift of the Scaling Site | 2018 | `arxiv:1805.10501` | read |
| KN-LIT-648 | The second moment of the number of integral points on elliptic curves is bounded | 2018 | `arxiv:1807.03761` | read |
| KN-LIT-649 | Towards Bidirectional Ratcheted Key Exchange? | 2018 | `eprint:2018/296` | read |
| KN-LIT-650 | Truncated Differential Properties of the Diagonal Set of Inputs for 5-round AES (Extended Version) | 2018 | `eprint:2018/182` | read |
| KN-LIT-651 | Two-Message Statistically Sender-Private OT from LWE ? | 2018 | `eprint:2018/530` | read |
| KN-LIT-652 | Watermarking PRFs from Lattices: Stronger Security via Extractable PRFs | 2018 | `eprint:2018/986` | read |
| KN-LIT-653 | ZCZ – Achieving n-bit SPRP Security with a Minimal Number of Tweakable-block-cipher Calls | 2018 | `eprint:2018/819` | read |
| KN-LIT-654 | “S-Box” Implementation of AES is NOT side channel resistant | 2018 | `eprint:2018/1002` | read |
| KN-LIT-655 | A GROSS-KOHNEN-ZAGIER THEOREM FOR NON-SPLIT CARTAN CURVES | 2019 | `arxiv:1905.05048` | read |
| KN-LIT-656 | A Key-Independent Distinguisher for 6-round AES in an Adaptive Setting | 2019 | `eprint:2019/945` | read |
| KN-LIT-6565a8 | Complete and improved FPGA implementation of Classic McEliece | 2022 | `eprint:2022/412` | web |
| KN-LIT-657 | A new ECDLP-based PoW model | 2019 | `arxiv:1911.11287` | read |
| KN-LIT-658 | A PROOF OF PERRIN-RIOU’S HEEGNER POINT MAIN CONJECTURE | 2019 | `arxiv:1908.09512` | read |
| KN-LIT-659 | A VIEW ON ELLIPTIC INTEGRALS FROM PRIMITIVE FORMS | 2019 | `arxiv:1909.02715` | read |
| KN-LIT-660 | Adventures in Supersingularland Sarah Arpin, Catalina Camacho-Navarro, Kristin Lauter | 2019 | `arxiv:1909.07779` | read |
| KN-LIT-661 | An Energy-Efficient Reconfigurable DTLS Cryptographic Engine for Securing Internet-of-Things Applications | 2019 | `arxiv:1907.04455` | read |
| KN-LIT-662 | CHES 2018 side channel contest CTF – Solution of the AES Challenges | 2019 | `eprint:2019/094` | read |
| KN-LIT-663 | COINCIDENCES OF DIVISION FIELDS | 2019 | `arxiv:1912.05618` | read |
| KN-LIT-664 | Collusion Resistant Trace-and-Revoke for Arbitrary Identities from Standard Assumptions | 2019 | `eprint:2019/984` | read |
| KN-LIT-665 | Constructing Cycles in Isogeny Graphs of Supersingular Elliptic Curves | 2019 | `arxiv:1912.03073` | read |
| KN-LIT-666 | COUNTING ELLIPTIC CURVES WITH AN ISOGENY OF DEGREE THREE | 2019 | `arxiv:1906.07877` | read |
| KN-LIT-667 | COUNTING THE NUMBER OF THE TWISTS OF CERTAIN POLARIZED ABELIAN VARIETIES | 2019 | `arxiv:1911.08758` | read |
| KN-LIT-668 | Dissecting the CHES 2018 AES Challenge | 2019 | `eprint:2019/783` | read |
| KN-LIT-669 | Ease of Side-Channel Attacks on AES-192/256 by Targeting Extreme Keys | 2019 | `eprint:2019/340` | read |
| KN-LIT-670 | ELEMENTS OF GIVEN ORDER IN TATE-SHAFAREVICH GROUPS OF ABELIAN VARIETIES IN QUADRATIC TWIST FAMILIES | 2019 | `arxiv:1904.00116` | read |
| KN-LIT-671 | ENDOMORPHISM RINGS OF SUPERSINGULAR ELLIPTIC CURVES | 2019 | `arxiv:1907.12185` | read |
| KN-LIT-672 | EXCEPTIONAL JUMPS OF PICARD RANKS OF REDUCTIONS OF K3 SURFACES OVER NUMBER FIELDS | 2019 | `arxiv:1909.07473` | read |
| KN-LIT-673 | Extended Truncated-differential Distinguishers on Round-reduced AES | 2019 | `eprint:2019/622` | read |
| KN-LIT-674 | Flexible Authenticated and Confidential Channel Establishment (fACCE): Analyzing the Noise Protocol Framework? | 2019 | `eprint:2019/436` | read |
| KN-LIT-675 | Genus 2 Supersingular Isogeny Oblivious Transfer arXiv:1907.00475v4 [cs.CR] 27 Jul 2019 Ramsès Fernàndez-València[0000−0002−8959−636X] | 2019 | `arxiv:1907.00475` | read |
| KN-LIT-676 | GLOBAL METHODS FOR THE SYMPLECTIC TYPE OF CONGRUENCES BETWEEN ELLIPTIC CURVES | 2019 | `arxiv:1910.12290` | read |
| KN-LIT-677 | HASH FUNCTIONS FROM SUPERSPECIAL GENUS-2 CURVES USING RICHELOT ISOGENIES | 2019 | `arxiv:1903.06451` | read |
| KN-LIT-678 | Hessian matrices, automorphisms of p-groups, and torsion points of elliptic curves | 2019 | `arxiv:1912.09860` | read |
| KN-LIT-678a43 | Solving the supersingular isogeny problem in time p^{2/5+o(1)} using bivariate multipoint evaluation | 2026 | `eprint:2026/1575` | read |
| KN-LIT-679 | Implementing Grover oracles for quantum key search on AES and LowMC | 2019 | `eprint:2019/1146` | read |
| KN-LIT-680 | Improved Meet-in-the-Middle Preimage Attacks against AES Hashing Modes | 2019 | `eprint:2019/607` | read |
| KN-LIT-681 | INT-AMPLIFIED ENDOMORPHISMS ON NORMAL | 2019 | `arxiv:1902.06071` | read |
| KN-LIT-682 | Integrality of Seshadri constants and irreducibility of principal polarizations on products of two isogenous elliptic curves | 2019 | `arxiv:1911.10843` | read |
| KN-LIT-683 | Integrality properties in the Moduli Space of Elliptic Curves: Isogeny Case | 2019 | `arxiv:1908.11088` | read |
| KN-LIT-684 | Leveraging Linear Decryption: Rate-1 Fully-Homomorphic Encryption and Time-Lock Puzzles? | 2019 | `eprint:2019/720` | read |
| KN-LIT-6847 | Structure-Preserving Cryptography |  | `doi:10.1007/s00145-014-9196-7` | read |
| KN-LIT-685 | Mixture Integral Attacks on Reduced-Round AES with a Known/Secret S-Box | 2019 | `eprint:2019/772` | read |
| KN-LIT-686 | Modularity of GL2(Fp)-representations over CM fields | 2019 | `arxiv:1910.12986` | read |
| KN-LIT-687 | MORDELL-WEIL RANKS AND TATE-SHAFAREVICH GROUPS OF ELLIPTIC CURVES WITH MIXED-REDUCTION TYPE OVER CYCLOTOMIC EXTENSIONS | 2019 | `arxiv:1911.10643` | read |
| KN-LIT-688 | MÖBIUS FORMULAS FOR DENSITIES OF SETS OF PRIME IDEALS | 2019 | `arxiv:1907.02914` | read |
| KN-LIT-689 | NEIGHBORHOOD OF THE SUPERSINGULAR ELLIPTIC | 2019 | `arxiv:1905.00244` | read |
| KN-LIT-690 | NON-VANISHING THEOREMS FOR CENTRAL L-VALUES OF SOME ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION II | 2019 | `arxiv:1904.05756` | read |
| KN-LIT-691 | ON DERIVATIVES OF KATO’S EULER SYSTEM FOR ELLIPTIC CURVES | 2019 | `arxiv:1910.07404` | read |
| KN-LIT-692 | ON ISOGENIES AMONG CERTAIN ABELIAN SURFACES | 2019 | `arxiv:1901.09846` | read |
| KN-LIT-693 | On the algebraic functional equation of the eigenspaces of mixed signed Selmer groups of elliptic curves with good reduction at primes above p | 2019 | `arxiv:1912.09023` | read |
| KN-LIT-6938cf | Symphony of speeds: harmonizing Classic McEliece cryptography with GPU innovation | 2025 | `eprint:2025/748` | web |
| KN-LIT-694 | On the Euler characteristics of signed Selmer groups | 2019 | `arxiv:1905.11038` | read |
| KN-LIT-695 | On the growth of Mordell-Weil ranks in p-adic Lie extensions | 2019 | `arxiv:1902.01068` | read |
| KN-LIT-696 | ON THE PROPERTIES OF NORTHCOTT AND NARKIEWICZ FOR ELLIPTIC CURVES | 2019 | `arxiv:1911.08752` | read |
| KN-LIT-697 | Optimizations of Side-Channel Attack on AES MixColumns Using Chosen Input | 2019 | `eprint:2019/343` | read |
| KN-LIT-698 | Poisson structures on loop spaces of CP n and an r-matrix associated with the universal elliptic curve | 2019 | `arxiv:1901.07082` | read |
| KN-LIT-699 | Practical Attacks on Reduced-Round AES | 2019 | `eprint:2019/770` | read |
| KN-LIT-6a786b | The use of information sets in decoding cyclic codes | 1962 | `doi:10.1109/tit.1962.1057777` | web |
| KN-LIT-6ad1af | Classic McEliece hardware implementation with enhanced side-channel and fault resistance | 2024 | `eprint:2024/1828` | web |
| KN-LIT-6b1fc8 | Understanding the new distinguisher of alternant codes at degree 2 | 2025 | `eprint:2025/531` | web |
| KN-LIT-6bdee9 | Side-channel attacks on the McEliece and Niederreiter public-key cryptosystems | 2011 | `eprint:2010/479` | web |
| KN-LIT-6c6f5e | Verified non-recursive calculation of Beneš networks applied to Classic McEliece | 2026 | `eprint:2026/107` | web |
| KN-LIT-6da230 | Classic McEliece: conservative code-based cryptography: guide for security reviewers | 2022 | `url:classic.mceliece.org/mceliece-security-20221023.pdf` | read |
| KN-LIT-6dcb5b | Verified fast formulas for control bits for permutation networks | 2020 | `url:cr.yp.to/papers.html#controlbits` | false |
| KN-LIT-6e1eb5 | A side-channel attack against Classic McEliece when loading the Goppa polynomial | 2023 | `doi:10.1007/978-3-031-37679-5_5` | web |
| KN-LIT-700 | PRIME TORSION IN THE BRAUER GROUP OF AN ELLIPTIC CURVE | 2019 | `arxiv:1909.05317` | read |
| KN-LIT-701 | PRIMITIVE DIVISORS OF ELLIPTIC DIVISIBILITY SEQUENCES OVER FUNCTION FIELDS WITH CONSTANT j-INVARIANT | 2019 | `arxiv:1904.12393` | read |
| KN-LIT-702 | Primitive divisors of sequences associated to elliptic curves | 2019 | `arxiv:1906.00632` | read |
| KN-LIT-70266b | Statistical decoding revisited | 2006 | `doi:10.1007/11780656_24` | web |
| KN-LIT-703 | Quantum Algorithms for the Approximate | 2019 | `eprint:2019/101` | read |
| KN-LIT-704 | Quantum Security Analysis of AES | 2019 | `eprint:2019/272` | read |
| KN-LIT-705 | RATIONAL POINTS ON CUBIC, QUARTIC AND SEXTIC CURVES OVER FINITE FIELDS arXiv:1912.11441v2 [math.NT] 30 Jan 2020 JOSÉ ALVES OLIVEIRA | 2019 | `arxiv:1912.11441` | read |
| KN-LIT-706 | Reducing the Cost of Implementing AES as a Quantum Circuit | 2019 | `eprint:2019/854` | read |
| KN-LIT-707 | RESIDUAL SUPERSINGULAR IWASAWA THEORY AND SIGNED IWASAWA INVARIANTS | 2019 | `arxiv:1911.10649` | read |
| KN-LIT-708 | SOME PROPERTIES OF THE DISTRIBUTION OF THE NUMBERS OF POINTS ON ELLIPTIC CURVES OVER A FINITE PRIME FIELD | 2019 | `arxiv:1901.00604` | read |
| KN-LIT-709 | Speeding Up Elliptic Curve Multiplication with Mixed-base Representation for Applications to SIDH Ciphers | 2019 | `arxiv:1905.06492` | read |
| KN-LIT-710 | Spin Me Right Round Rotational Symmetry for FPGA-specific AES | 2019 | `eprint:2019/349` | read |
| KN-LIT-711 | TATE-SHAFAREVICH GROUPS OF CONSTANT ELLIPTIC CURVES AND ISOGENY VOLCANOS | 2019 | `arxiv:1904.00501` | read |
| KN-LIT-712 | THE MANIN CONSTANT AND THE MODULAR DEGREE | 2019 | `arxiv:1911.09446` | read |
| KN-LIT-713 | The smooth locus in infinite-level Rapoport-Zink spaces | 2019 | `arxiv:1903.04588` | read |
| KN-LIT-714 | TORSION OF ELLIPTIC CURVES WITH RATIONAL j-INVARIANT DEFINED OVER NUMBER FIELDS OF PRIME DEGREE | 2019 | `arxiv:1912.04037` | read |
| KN-LIT-715 | TORSION POINTS AND ISOGENIES ON CM ELLIPTIC CURVES | 2019 | `arxiv:1906.07121` | read |
| KN-LIT-716 | TORSION POINTS OF ORDER 2g + 1 ON ODD DEGREE HYPERELLIPTIC CURVES OF GENUS g | 2019 | `arxiv:1902.02743` | read |
| KN-LIT-717 | TOTALLY INVARIANT DIVISORS OF INT-AMPLIFIED ENDOMORPHISMS OF NORMAL PROJECTIVE VARIETIES | 2019 | `arxiv:1905.05362` | read |
| KN-LIT-718 | TOWARDS HILBERT’S TENTH PROBLEM FOR RINGS OF INTEGERS | 2019 | `arxiv:1909.01434` | read |
| KN-LIT-719 | TPM-FAIL: TPM meets Timing and Lattice Attacks | 2019 | `arxiv:1911.05673` | read |
| KN-LIT-71d1a0 | The syzygy distinguisher | 2025 | `eprint:2024/1193` | web |
| KN-LIT-71fb0b | Weak keys in McEliece public-key cryptosystem | 2001 | `doi:10.1109/18.915687` | web |
| KN-LIT-720 | TRIANGULATIONS OF NON-ARCHIMEDEAN CURVES | 2019 | `arxiv:1911.04407` | read |
| KN-LIT-721 | UNIFORM BOUNDS ON THE IMAGE OF THE ARBOREAL GALOIS REPRESENTATIONS ATTACHED TO NON-CM ELLIPTIC CURVES | 2019 | `arxiv:1909.07468` | read |
| KN-LIT-722 | UNLIKELY INTERSECTIONS WITH ISOGENY ORBITS IN A PRODUCT OF ELLIPTIC SCHEMES | 2019 | `arxiv:1902.01323` | read |
| KN-LIT-723 | Variants of the AES Key Schedule for Better Truncated Differential Bounds | 2019 | `eprint:2019/095` | read |
| KN-LIT-724 | Weak-Key Distinguishers for AES | 2019 | `eprint:2019/852` | read |
| KN-LIT-725 | A CLASSIFICATION OF ISOGENY-TORSION GRAPHS OF Q-ISOGENY CLASSES OF ELLIPTIC CURVES | 2020 | `arxiv:2001.05616` | read |
| KN-LIT-726 | A GROUP THEORETIC PERSPECTIVE ON ENTANGLEMENTS OF DIVISION FIELDS | 2020 | `arxiv:2008.09886` | read |
| KN-LIT-7261 | An Elliptic Curve Trapdoor System | 2003 | `eprint:2003/058` | true |
| KN-LIT-727 | Akashi series and Euler characteristics of signed Selmer groups of elliptic curves with semistable reduction at primes above p | 2020 | `arxiv:2001.09304` | read |
| KN-LIT-728 | Algebraic blinding and cryptographic trilinear maps | 2020 | `arxiv:2002.07923` | read |
| KN-LIT-729 | Alternative Tower Field Construction for Quantum Implementation of the AES S-box | 2020 | `eprint:2020/941` | read |
| KN-LIT-730 | AN AUTHENTICATED KEY SCHEME OVER ELLIPTIC CURVES FOR TOPOLOGICAL NETWORKS | 2020 | `arxiv:2006.02147` | read |
| KN-LIT-731 | ANALOGUES OF ALLADI’S FORMULA OVER GLOBAL FUNCTION FIELDS | 2020 | `arxiv:2010.11069` | read |
| KN-LIT-732 | ANALYTIC RANKS OF ELLIPTIC CURVES OVER NUMBER FIELDS | 2020 | `arxiv:2005.07909` | read |
| KN-LIT-733 | Automatic Search of Meet-in-the-Middle Preimage Attacks on AES-like Hashing Zhenzhen Bao2(B) , Xiaoyang Dong3(B) , Jian Guo2(B) | 2020 | `eprint:2020/467` | read |
| KN-LIT-734 | BOUNDS FOR 2-SELMER RANKS IN TERMS OF SEMINARROW CLASS GROUPS | 2020 | `arxiv:2005.00194` | read |
| KN-LIT-735 | CALABI-YAU THREEFOLDS WITH PICARD NUMBER THREE | 2020 | `arxiv:2011.12876` | read |
| KN-LIT-736 | CLASSICAL IWASAWA THEORY AND INFINITE DESCENT ON A FAMILY OF ABELIAN VARIETIES | 2020 | `arxiv:2008.10310` | read |
| KN-LIT-737 | COMPUTING ENDOMORPHISM RINGS OF SUPERSINGULAR | 2020 | `arxiv:2004.11495` | read |
| KN-LIT-738 | CONJECTURE A AND μ-INVARIANT FOR SELMER GROUPS OF SUPERSINGULAR ELLIPTIC CURVES | 2020 | `arxiv:2006.14134` | read |
| KN-LIT-739 | CONSTRUCTING CONGRUENT NUMBER ELLIPTIC CURVES | 2020 | `arxiv:2006.08113` | read |
| KN-LIT-740 | CONSTRUCTION OF HECKE CHARACTERS FOR THREE-DIMENSIONAL CM | 2020 | `arxiv:2009.12761` | read |
| KN-LIT-741 | COUNTING ELLIPTIC CURVES WITH A RATIONAL N -ISOGENY FOR SMALL N | 2020 | `arxiv:2009.05223` | read |
| KN-LIT-7414 | University of Birmingham Quasi-subfield polynomials and the elliptic curve discrete logarithm problem |  | `doi:10.1515/jmc-2015-0049` | read |
| KN-LIT-742 | Cover attacks for elliptic curves with prime order | 2020 | `arxiv:2012.07173` | read |
| KN-LIT-743 | CYCLIC REDUCTION DENSITIES FOR ELLIPTIC CURVES | 2020 | `arxiv:2001.00028` | read |
| KN-LIT-744 | Deep Learning Side-Channel Analysis on Large-Scale Traces A Case Study on a Polymorphic AES | 2020 | `eprint:2020/881` | read |
| KN-LIT-745 | Degree bounds for projective division fields associated to elliptic modules with a trivial endomorphism ring | 2020 | `arxiv:2002.08411` | read |
| KN-LIT-746 | Differential Power Analysis Attacks on Different Implementations of AES with the ChipWhisperer Nano | 2020 | `eprint:2020/1008` | read |
| KN-LIT-747 | DISTRIBUTION OF NON-WIEFERICH PRIMES IN CERTAIN ALGEBRAIC | 2020 | `arxiv:2002.11941` | read |
| KN-LIT-748 | Divided We Stand, United We Fall: Security Analysis of Some SCA+SIFA Countermeasures Against SCA-Enhanced Fault Template Attacks? | 2020 | `eprint:2020/892` | read |
| KN-LIT-749 | EFFECTIVE SATO–TATE CONJECTURE FOR ABELIAN VARIETIES AND APPLICATIONS | 2020 | `arxiv:2002.08807` | read |
| KN-LIT-750 | Efficient ECM factorization in parallel with the Lyness map | 2020 | `arxiv:2002.03811` | read |
| KN-LIT-751 | Efficient Montgomery-like formulas for general | 2020 | `eprint:2020/526` | read |
| KN-LIT-752 | ELLIPTIC (p, q)-DIFFERENCE MODULES | 2020 | `arxiv:2007.09508` | read |
| KN-LIT-753 | ELLIPTIC CURVES OVER Fp AND DETERMINANTS OF LEGENDRE MATRICES | 2020 | `arxiv:2012.05746` | read |
| KN-LIT-754 | ELLIPTIC CURVES WITH NON-ABELIAN ENTANGLEMENTS | 2020 | `arxiv:2008.09087` | read |
| KN-LIT-755 | Enhanced Flush+Reload Attack on AES? | 2020 | `eprint:2020/907` | read |
| KN-LIT-756 | ENTANGLEMENT IN THE FAMILY OF DIVISION FIELDS OF ELLIPTIC CURVES WITH COMPLEX MULTIPLICATION | 2020 | `arxiv:2006.00883` | read |
| KN-LIT-7564 | The supersingular isogeny problem in time and memory p^{1/3+o(1)} | 2026 | `eprint:2026/1486` | web |
| KN-LIT-7565 | Multilevel Amortized Gaussian Elimination in Information-Set Decoding: Applications to HQC and PCG | 2026 | `eprint:2026/1498` | web |
| KN-LIT-7566 | Provable Recovery of RSA Private Exponents below N^{11/42-epsilon} | 2026 | `eprint:2026/1478` | web |
| KN-LIT-7567 | On the Impossibility of Round-Optimal Pairing-Free Blind Signatures in the ROM | 2026 | `eprint:2026/090` | web |
| KN-LIT-7568 | Hybrid hash function based on the DLP and SIS problems | 2026 | `eprint:2026/1459` | web |
| KN-LIT-7569 | Beyond Binary: crosscorrelation of Cubic, Quartic and Quintic Character Sequences | 2026 | `eprint:2026/829` | web |
| KN-LIT-757 | EQUIDISTRIBUTION OF αpθ WITH A CHEBOTAREV CONDITION AND APPLICATIONS TO EXTREMAL PRIMES | 2020 | `arxiv:2012.12534` | read |
| KN-LIT-7570 | On k-way split multiplication algorithms | 2026 | `eprint:2026/1494` | web |
| KN-LIT-7571 | Post-Quantum Anonymous Signatures from the Lattice Isomorphism Group Action | 2026 | `eprint:2026/436` | web |
| KN-LIT-7572 | Border Bases and Border Basis Schemes | 2026 | `arxiv:2607.18948` | web |
| KN-LIT-7573 | Generic ordinarity for abelian coverings of the projective line | 2026 | `arxiv:2607.21033` | web |
| KN-LIT-7574 | Quantum Cryptanalysis on IBM Quantum Hardware: Extending Even-Mansour Period Recovery from N=4 to N=10 | 2026 | `arxiv:2607.18340` | web |
| KN-LIT-7575 | DSA Nonce Vulnerabilities: An Interactive Analysis | 2026 | `arxiv:2607.17107` | web |
| KN-LIT-758 | EULER CHARACTERISTICS AND THEIR CONGRUENCES FOR MULTI-SIGNED SELMER GROUPS | 2020 | `arxiv:2011.05387` | read |
| KN-LIT-7580 | Complex-Multiplication Terminals for Supersingular Isogeny Path-Finding | 2026 | `eprint:2026/1516` | web |
| KN-LIT-7581 | Quantum Lazy Sampling and Path Recording for Any Group | 2026 | `eprint:2026/1510` | web |
| KN-LIT-7582 | PRISM with a pinch of salt: Simple, Efficient and Strongly Unforgeable Signatures from Isogenies | 2026 | `eprint:2026/443` | web |
| KN-LIT-7583 | An analysis of a weakened version of PRISM | 2026 | `eprint:2026/906` | web |
| KN-LIT-7584 | Efficient Ternary Computation of Optimal Ate Pairing on BLS27 Curves | 2026 | `eprint:2026/1522` | web |
| KN-LIT-7585 | ZKPoSP: Post-Quantum Zero-Knowledge Proofs for Hierarchical Deterministic Wallets | 2026 | `eprint:2026/1508` | web |
| KN-LIT-7586 | The McEliece Cryptosystem After Nearly Five Decades: A Survey of Security, Cryptanalysis, and Future Directions | 2026 | `eprint:2026/1512` | web |
| KN-LIT-7587 | The Polynomial-Time Low-Degree Conjecture is False | 2026 | `arxiv:2607.20318` | web |
| KN-LIT-7588 | CryptanalysisBench: Can LLMs do Cryptanalysis? | 2026 | `arxiv:2607.18538` | web |
| KN-LIT-7589 | Lower bounds on the strength of the determinant | 2026 | `arxiv:2607.21015` | web |
| KN-LIT-759 | Explicit description of isogeny and isomorphism classes of Drinfeld modules over finite field | 2020 | `arxiv:2009.02533` | read |
| KN-LIT-7590 | Degenerating Discriminants | 2026 | `arxiv:2607.17966` | web |
| KN-LIT-7591 | Lower bounds for the CNOT-complexity of linear reversible operators | 2026 | `arxiv:2607.22248` | web |
| KN-LIT-7592 | HAWK-n Key Recovery Reduces to SVP in Dimension n/2 + 1 | 2026 | `url:anthropic.com/document/hawk_key_recovery.pdf` | read |
| KN-LIT-7593 | Cryptanalysis of 7-Round AES via the Algebraic Structure of its S-box | 2026 | `url:anthropic.com/document/aes_mobius_bridge.pdf` | web |
| KN-LIT-7594 | Discovering cryptographic weaknesses with Claude | 2026 | `url:www.anthropic.com/research/discovering-cryptographic-weaknesses` | web |
| KN-LIT-7595 | Mythos Preview's Chain of Thought in Discovering the AES Möbius Bridge | 2026 | `url:anthropic.com/document/aes_mobius_bridge_cot.pdf` | web |
| KN-LIT-7596 | Advanced cryptography from lattice isomorphism — new constructions of IBE and FHE | 2026 | `eprint:2026/465` | web |
| KN-LIT-7597 | Decision trees, Frobenius traces, and Weierstrass coefficients of elliptic curves | 2026 | `arxiv:2607.24251` | web |
| KN-LIT-7598 | A lower bound for the distance between CM points on Shimura curves | 2026 | `arxiv:2607.23270` | web |
| KN-LIT-7599 | Engineered Complete Intersections: Algorithmic Aspects | 2026 | `arxiv:2607.23622` | web |
| KN-LIT-760 | EXPLICIT TWO-COVER DESCENT FOR GENUS 2 CURVES | 2020 | `arxiv:2009.10313` | read |
| KN-LIT-7600 | A Resource Estimation Model for the Hardware-Software Co-Design of Distributed Quantum Architectures | 2026 | `arxiv:2607.22998` | web |
| KN-LIT-7601 | Cryptanalytic Properties of Mealy Machines | 2026 | `eprint:2026/1193` | web |
| KN-LIT-7602 | Classic Full Plaintext Recovery Attacks on Low Round Generalized Feistel Networks | 2026 | `eprint:2026/1519` | web |
| KN-LIT-7604 | Notes on summation polynomials | 2015 | `arxiv:1503.08001` | web |
| KN-LIT-7605 | On the last fall degree of Weil descent polynomial systems |  | `arxiv:2103.07282` | web |
| KN-LIT-7606 | The Structured Generic-Group Model | 2026 | `eprint:2026/384` | web |
| KN-LIT-7607 | Last fall degree, HFE, and Weil descent attacks on ECDLP | 2015 | `eprint:2015/573` | web |
| KN-LIT-761 | EXPLICIT UNIFORM BOUNDS FOR BRAUER GROUPS OF SINGULAR K3 SURFACES | 2020 | `arxiv:2006.14907` | read |
| KN-LIT-7612 | Security Analysis on UOV Families with Odd Characteristics: Using Symmetric Algebra | 2026 | `eprint:2025/1137` | web |
| KN-LIT-7613 | Explicit height bounds on modular polynomials for the elliptic j-invariant, cube root of j, and Weber modular function f | 2026 | `arxiv:2607.22214` | web |
| KN-LIT-7614 | Extremal Chowla sets and their linear analogues: A human-AI mathematical investigation using Co-Scientist | 2026 | `arxiv:2607.24847` | web |
| KN-LIT-7615 | Certified in Theory, Broken in Practice: Assumption Gaps in Cryptographic Model Certification | 2026 | `arxiv:2607.21839` | web |
| KN-LIT-7616 | Can PCE solve the factorisation problem via optimisation? | 2026 | `arxiv:2607.23727` | web |
| KN-LIT-7617 | Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber | 2025 | `eprint:2022/1750` | read |
| KN-LIT-7618 | CRYSTALS-Kyber: Algorithm Specifications And Supporting Documentation (Round 3) | 2021 | `url:pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf` | read |
| KN-LIT-7619 | FAEST reference implementation (faest-ref) | 2026 | `url:github.com/faest-sign/faest-ref` | true |
| KN-LIT-762 | Far Field EM Side-Channel Attack on AES Using Deep Learning | 2020 | `eprint:2020/1096` | read |
| KN-LIT-7620 | NIST IR 8610: Status Report on the Second Round of the Additional Digital Signature Schemes for the NIST Post-Quantum Cryptography Standardization Process | 2026 | `doi:10.6028/nist.ir.8610` | true |
| KN-LIT-7621 | The Arithmetic of Elliptic Curves (2nd ed.) | 2009 | `doi:10.1007/978-0-387-09494-6` | web |
| KN-LIT-7622 | Heegner points and derivatives of L-series | 1986 | `doi:10.1007/bf01388809` | web |
| KN-LIT-7623 | Formal complex multiplication in local fields | 1965 | `doi:10.2307/1970622` | web |
| KN-LIT-7624 | Endomorphisms of abelian varieties over finite fields | 1966 | `doi:10.1007/bf01404549` | web |
| KN-LIT-7625 | Isogeny classes of abelian varieties over finite fields | 1968 | `doi:10.2969/jmsj/02010083` | web |
| KN-LIT-7626 | Abelian varieties over finite fields | 1969 | `doi:10.24033/asens.1183` | web |
| KN-LIT-7627 | Néron Models | 1990 | `doi:10.1007/978-3-642-51438-8` | web |
| KN-LIT-7628 | Abelian varieties | 1970 | `url:stacks.math.columbia.edu/bibliography/avar` | web |
| KN-LIT-7629 | A First Course in Modular Forms | 2005 | `doi:10.1007/978-0-387-27226-9` | web |
| KN-LIT-763 | FAST COMPUTATION OF ELLIPTIC CURVE ISOGENIES IN CHARACTERISTIC TWO | 2020 | `arxiv:2003.06367` | read |
| KN-LIT-7630 | Constructing Isogenies Between Elliptic Curves Over Finite Fields | 1999 | `doi:10.1112/s1461157000000097` | true |
| KN-LIT-7631 | Expander graphs based on GRH with an application to elliptic curve cryptography (redirect) | 2009 | `arxiv:0811.0647` | read |
| KN-LIT-7632 | Mathematics of Isogeny Based Cryptography | 2017 | `arxiv:1711.04062` | true |
| KN-LIT-7633 | Hidden Pairings and Trapdoor DDH Groups | 2006 | `doi:10.1007/11792086_31` | false |
| KN-LIT-7634 | Trapdoor DDH Groups from Pairings and Isogenies | 2020 | `eprint:2019/1290` | true |
| KN-LIT-7635 | A Kilobit Hidden SNFS Discrete Logarithm Computation | 2017 | `eprint:2016/961` | true |
| KN-LIT-7636 | Removable Weak Keys for Discrete Logarithm Based Cryptography | 2020 | `eprint:2020/1436` | true |
| KN-LIT-7637 | Ten Advances in Mathematics and Theoretical Computer Science | 2026 | `url:cdn.openai.com/pdf/ten-proofs-oai.pdf` | read |
| KN-LIT-7638 | Publicly Verifiable Zero-Knowledge and Post-Quantum Signatures From VOLE-in-the-Head | 2023 | `eprint:2023/996` | true |
| KN-LIT-7639 | Character sums over AG codes | 2024 | `eprint:eccc tr24-069` | read |
| KN-LIT-764 | FASTER COMPUTATION OF ISOGENIES OF LARGE PRIME DEGREE | 2020 | `arxiv:2003.10118` | read |
| KN-LIT-7640 | Ten Advances in Mathematics and Theoretical Computer Science | 2026 | `url:cdn.openai.com/pdf/ten-proofs-oai.pdf` | read |
| KN-LIT-7641 | The principal ideal problem for endomorphism rings of superspecial abelian varieties | 2026 | `eprint:2026/454` | web |
| KN-LIT-7642 | Efficient quaternion algorithms for the Deuring correspondence, and application to the evaluation of modular polynomials | 2026 | `eprint:2026/185` | web |
| KN-LIT-7643 | High-Order Galois Automorphisms for TNFS Linear Algebra | 2026 | `eprint:2026/560` | web |
| KN-LIT-7644 | The discrete logarithm problem in cokernels of O_K-matrices | 2026 | `arxiv:2607.03594` | web |
| KN-LIT-7645 | Computing class groups and gonalities of algebraic curves over finite fields | 2026 | `arxiv:2602.17417` | web |
| KN-LIT-7646 | Decomposition of the Ate Pairing and its Relation to Generalized Pairing Inversion | 2026 | `eprint:2026/1049` | web |
| KN-LIT-7647 | SoliloQuat: Throwing Caution to the Wind | 2026 | `eprint:2026/859` | web |
| KN-LIT-7648 | Cryptanalysis of Definite and Indefinite Lattice Isomorphism Problems With Applications to DEFI | 2026 | `eprint:2026/890` | web |
| KN-LIT-7649 | Principal ideal problem and ideal shortest vector over rational primes in power-of-two cyclotomic fields | 2026 | `arxiv:2601.07511` | web |
| KN-LIT-765 | Finding Elliptic Curves With Many Integral Points arXiv:2012.06233v1 [math.NT] 11 Dec 2020 Benjamin Jones | 2020 | `arxiv:2012.06233` | read |
| KN-LIT-7650 | Module Lattice Security (Part I): Unconditional Verification of Weber's Conjecture for k <= 12 | 2026 | `arxiv:2604.15858` | web |
| KN-LIT-7651 | Cryptanalysis of Hecke-KE: A Linear-Algebra Attack via Hecke Eigenbasis Decomposition | 2026 | `eprint:2026/770` | web |
| KN-LIT-7652 | Linear Code Equivalence via Plücker Coordinates | 2026 | `eprint:2026/495` | web |
| KN-LIT-7653 | Learning the Word Problem: Geodesic Lengths and Cryptographic Applications | 2026 | `arxiv:2607.26241` | web |
| KN-LIT-7654 | On the higher algebraic K-groups of arithmetically equivalent number fields | 2026 | `arxiv:2607.26685` | web |
| KN-LIT-7655 | Radical 3-isogenies for the ideal class group actions on (2, epsilon)-structures | 2026 | `eprint:2026/576` | web |
| KN-LIT-7656 | Forensic categories: a framework for SQIsign-like primitives | 2026 | `eprint:2026/1171` | web |
| KN-LIT-7657 | Resource Estimation of the Distributed Quantum Algorithm for the Elliptic Curve Logarithm Problem | 2026 | `eprint:2026/1244` | web |
| KN-LIT-7658 | The Cokernel Pairing | 2026 | `eprint:2026/001` | web |
| KN-LIT-7659 | Coppersmith's Method for Solving Modular Inversion Hidden Number Problem via Determinant-Based Elimination | 2026 | `eprint:2026/423` | web |
| KN-LIT-766 | Fine-Grained Cryptography: A New Frontier? | 2020 | `eprint:2020/442` | read |
| KN-LIT-7660 | On the Security of Constraint-Friendly Map-to-Curve Relations | 2026 | `eprint:2026/590` | web |
| KN-LIT-7661 | Time vs Success Probability Tradeoff for SVP and BDD with Implications to LWE and SIS | 2026 | `eprint:2026/1364` | web |
| KN-LIT-7662 | Refined Approx-SVP Rank Reduction Conditions and Adaptive Lattice Reduction for MSIS Security Estimation | 2026 | `eprint:2026/607` | web |
| KN-LIT-7663 | On the Concrete Hardness Gap Between MLWE and LWE | 2026 | `eprint:2026/279` | web |
| KN-LIT-7664 | Unified Dual Attack Analyses: Covariance-Based Score Distribution Prediction for LWE | 2026 | `eprint:2026/1048` | web |
| KN-LIT-7665 | What Happens When integrating Modulus Switching and Lossy Source Coding: A New Dual Attack Variant on LWE | 2026 | `eprint:2026/1400` | web |
| KN-LIT-7666 | An Improved Hybrid Dual Attack on LWE with Sparse Secrets and its Application to FHE | 2026 | `eprint:2026/1060` | web |
| KN-LIT-7667 | Careful with the Ring: Enhanced Hybrid Decoding Attacks against Module/Ring-LWE | 2026 | `eprint:2026/366` | web |
| KN-LIT-7668 | Sharper and Closed-Form Attacks on SIS When Modulus Is Small | 2026 | `eprint:2026/1349` | web |
| KN-LIT-7669 | Solving SIS in any norm via Gaussian sampling | 2026 | `eprint:2026/225` | web |
| KN-LIT-767 | Fixslicing AES-like Ciphers New bitsliced AES speed records on ARM-Cortex M and RISC-V | 2020 | `eprint:2020/1123` | read |
| KN-LIT-7670 | Cryptanalysis of HAWK: a Guessing Game | 2026 | `eprint:2026/1318` | web |
| KN-LIT-7671 | Exploiting the complexity of Lattice Isomorphism Problem via Irreducible Decomposition | 2026 | `eprint:2026/1139` | web |
| KN-LIT-7672 | Revisiting the Concrete Security of Falcon-type Signatures | 2026 | `eprint:2026/096` | web |
| KN-LIT-7674 | Cryptanalysis of HAWK: a Guessing Game (with 30/06 correction) | 2026 | `eprint:2026/1318` | body_read_from_user_provided_text |
| KN-LIT-7675 | Revisiting the Security of Approximate FHE with Noise-Flooding Countermeasures | 2025 | `eprint:2024/424` | web |
| KN-LIT-768 | From the Hardness of Detecting Superpositions to Cryptography: Quantum Public Key Encryption and Commitments | 2020 | `arxiv:2009.07450` | read |
| KN-LIT-769 | Hardness of LWE on General Entropic Distributions? | 2020 | `eprint:2020/119` | read |
| KN-LIT-76ba49 | Evaluation of Gaussian elimination using HLS for fast public key generation in the Classic McEliece | 2025 | `url:ww.bncss.org/index.php/bncss/article/view/186` | false |
| KN-LIT-770 | Hashing to elliptic curves of j “ 0 and Mordell–Weil groups | 2020 | `arxiv:2005.08336` | read |
| KN-LIT-771 | Improved quantum circuits for elliptic curve discrete logarithms | 2020 | `arxiv:2001.09580` | read |
| KN-LIT-772 | Improved torsion-point attacks on | 2020 | `arxiv:2005.14681` | read |
| KN-LIT-773 | Improving Speed and Security in Updatable Encryption Schemes | 2020 | `eprint:2020/222` | read |
| KN-LIT-774 | INFINITESIMAL AUTOMORPHISMS OF ALGEBRAIC VARIETIES AND VECTOR FIELDS ON ELLIPTIC SURFACES | 2020 | `arxiv:2004.07227` | read |
| KN-LIT-775 | Integrality of twisted L-values of elliptic curves | 2020 | `arxiv:2004.05492` | read |
| KN-LIT-776 | IRREDUCIBILITY OF MOD p GALOIS REPRESENTATIONS OF ELLIPTIC CURVES WITH MULTIPLICATIVE REDUCTION OVER NUMBER FIELDS | 2020 | `arxiv:2004.07611` | read |
| KN-LIT-777 | Isogenies of elliptic curves over function fields | 2020 | `arxiv:2005.02920` | read |
| KN-LIT-778 | ISOGENY GRAPHS OF SUPERSPECIAL ABELIAN VARIETIES AND BRANDT MATRICES | 2020 | `arxiv:2005.09031` | read |
| KN-LIT-779 | IWASAWA THEORY FOR QUADRATIC HILBERT MODULAR FORMS | 2020 | `arxiv:2006.14491` | read |
| KN-LIT-780 | Karatsuba-based square-root Vélu’s formulas applied to two isogeny-based protocols | 2020 | `eprint:2020/1109` | read |
| KN-LIT-781 | LINEAR INDEPENDENCE IN LINEAR SYSTEMS ON ELLIPTIC CURVES | 2020 | `arxiv:2005.05473` | read |
| KN-LIT-782 | MINIMAL MODELS OF RATIONAL ELLIPTIC CURVES WITH NON-TRIVIAL TORSION | 2020 | `arxiv:2001.01016` | read |
| KN-LIT-783 | Mitigating TLS compromise with ECDHE and SRP | 2020 | `arxiv:2005.13864` | read |
| KN-LIT-784 | MixColumns Coefficient Property and Security of the AES with A Secret S-Box | 2020 | `eprint:2020/546` | read |
| KN-LIT-785 | Modified Cache Template Attack on AES | 2020 | `eprint:2020/1560` | read |
| KN-LIT-786 | MULTIPLICATIVE AND LINEAR DEPENDENCE IN FINITE | 2020 | `arxiv:2008.00389` | read |
| KN-LIT-787 | MULTIPLICITIES IN SELMER GROUPS AND ROOT NUMBERS FOR ARTIN TWISTS | 2020 | `arxiv:2007.12996` | read |
| KN-LIT-788 | New (k, l, m)-verifiable multi-secret sharing schemes based on XTR public key system | 2020 | `arxiv:2011.08648` | read |
| KN-LIT-789 | New Representations of the AES Key Schedule | 2020 | `eprint:2020/1253` | read |
| KN-LIT-790 | NIZK from LPN and Trapdoor Hash via Correlation Intractability for Approximable Relations ? | 2020 | `eprint:2020/258` | read |
| KN-LIT-791 | nordita 2020-007 | 2020 | `arxiv:2009.14513` | read |
| KN-LIT-792 | ON 2-SELMER GROUPS AND QUADRATIC TWISTS OF ELLIPTIC CURVES | 2020 | `arxiv:2001.02263` | read |
| KN-LIT-793 | ON BLOCH–KATO SELMER GROUPS AND IWASAWA THEORY OF p-ADIC GALOIS REPRESENTATIONS | 2020 | `arxiv:2010.10251` | read |
| KN-LIT-794 | ON CLASS NUMBERS, TORSION SUBGROUPS, AND QUADRATIC TWISTS OF ELLIPTIC CURVES | 2020 | `arxiv:2007.08756` | read |
| KN-LIT-795 | ON ELEMENTS OF LARGE ORDER OF ELLIPTIC | 2020 | `arxiv:2008.00433` | read |
| KN-LIT-796 | On Index Calculus Algorithms for Subfield Curves | 2020 | `eprint:2020/1315` | read |
| KN-LIT-7965a1 | An algorithmic reduction theory for binary codes: LLL and more | 2022 | `eprint:2020/869` | web |
| KN-LIT-797 | On some p-adic Galois representations and form class groups | 2020 | `arxiv:2009.13837` | read |
| KN-LIT-798 | On the algebraic functional equation for the mixed signed Selmer group over multiple Zp-extensions | 2020 | `arxiv:2004.10592` | read |
| KN-LIT-799 | ON THE ANTICYCLOTOMIC IWASAWA THEORY OF RATIONAL ELLIPTIC | 2020 | `arxiv:2008.02571` | read |
| KN-LIT-7baf07 | Quasipolynomial Cryptanalysis of the McEliece Cryptosystem (or: PIR Meets McEliece) | 2026 | `eprint:2026/1630` | web |
| KN-LIT-7c2620 | Careful with the Ring: Enhanced Hybrid Decoding Attacks against Module/Ring-LWE | 2026 | `eprint:2026/366` | web |
| KN-LIT-7c4620 | A heuristic subexponential attack on the McEliece cryptosystem | 2026 | `eprint:2026/1232` | web |
| KN-LIT-7c6f53 | Cryptanalysis of the original McEliece cryptosystem | 1998 | `doi:10.1007/3-540-49649-1_16` | web |
| KN-LIT-7d2077 | Classic McEliece: conservative code-based cryptography: guide for implementors | 2022 | `url:classic.mceliece.org/mceliece-impl-20221023.pdf` | web |
| KN-LIT-7d6c98 | Profiled side-channel attack on cryptosystems based on the binary syndrome decoding problem | 2022 | `eprint:2022/125` | web |
| KN-LIT-7ee1a9 | Understanding the new distinguisher of alternant codes at degree 2 | 2025 | `eprint:2025/531` | web |
| KN-LIT-7f3c21 | Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications (RFC 9106) | 2021 | `doi:10.17487/rfc9106` | true |
| KN-LIT-800 | On the distribution of orders of Frobenius action on `-torsion of abelian surfaces | 2020 | `arxiv:2001.03546` | read |
| KN-LIT-801 | On the division fields of an elliptic curve and an effective bound to the hypotheses of the local-global divisibility | 2020 | `arxiv:2001.03429` | read |
| KN-LIT-802 | On the Role of Hash-based Signatures in Quantum-Safe Internet of Things: Current Solutions and Future Directions | 2020 | `arxiv:2004.10435` | read |
| KN-LIT-80202e | Quantum information set decoding algorithms | 2017 | `arxiv:1703.00263` | web |
| KN-LIT-803 | ON TOTALLY SPLIT PRIMES IN HIGH-DEGREE TORSION FIELDS OF ELLIPTIC CURVES arXiv:2009.13119v2 [math.NT] 1 Oct 2021 JORI MERIKOSKI | 2020 | `arxiv:2009.13119` | read |
| KN-LIT-804 | On two problems about isogenies of elliptic curves over finite fields | 2020 | `arxiv:2001.00126` | read |
| KN-LIT-805 | Order-Fairness for Byzantine Consensus | 2020 | `eprint:2020/269` | read |
| KN-LIT-806 | p-ADIC DISTRIBUTION OF CM POINTS AND HECKE ORBITS | 2020 | `arxiv:2002.03232` | read |
| KN-LIT-807 | PERFECT SQUARES REPRESENTING THE NUMBER OF RATIONAL POINTS ON ELLIPTIC CURVES OVER FINITE FIELD EXTENSIONS | 2020 | `arxiv:2003.09951` | read |
| KN-LIT-808 | Pholkos – Efficient Large-state Tweakable Block Ciphers from the AES Round Function | 2020 | `eprint:2020/275` | read |
| KN-LIT-809 | Primitive divisors of sequences associated to elliptic curves with complex multiplication | 2020 | `arxiv:2010.10175` | read |
| KN-LIT-810 | Q-CURVES OVER ODD DEGREE NUMBER FIELDS | 2020 | `arxiv:2004.10054` | read |
| KN-LIT-811 | QUADRATIC TWISTS OF ELLIPTIC CURVES AND CLASS NUMBERS | 2020 | `arxiv:2006.01063` | read |
| KN-LIT-812 | Quantum Collision Attacks on AES-like Hashing with Low Quantum Random Access Memories | 2020 | `eprint:2020/1030` | read |
| KN-LIT-813 | Radical Isogenies | 2020 | `eprint:2020/1108` | read |
| KN-LIT-813e69 | Decoding complexity bound for linear block codes | 1989 | `url:www.mathnet.ru/eng/ppi665` | false |
| KN-LIT-814 | RESIDUAL GALOIS REPRESENTATIONS OF ELLIPTIC CURVES WITH IMAGE CONTAINED IN THE NORMALISER OF A NON-SPLIT CARTAN | 2020 | `arxiv:2002.02714` | read |
| KN-LIT-815 | RIGIDITY IN ELLIPTIC CURVE LOCAL-GLOBAL PRINCIPLES | 2020 | `arxiv:2005.05881` | read |
| KN-LIT-816 | SIMULTANEOUS SUPERSINGULAR REDUCTIONS OF CM ELLIPTIC CURVES | 2020 | `arxiv:2005.01537` | read |
| KN-LIT-817 | SPANNING THE ISOGENY CLASS OF A POWER OF AN ELLIPTIC CURVE | 2020 | `arxiv:2004.08315` | read |
| KN-LIT-818 | SUPERSINGULAR MAIN CONJECTURES, SYLVESTER’S CONJECTURE AND GOLDFELD’S CONJECTURE | 2020 | `arxiv:2002.04767` | read |
| KN-LIT-819 | TAMAGAWA NUMBER DIVISIBILITY OF CENTRAL L-VALUES OF TWISTS OF THE FERMAT ELLIPTIC CURVE | 2020 | `arxiv:2003.02772` | read |
| KN-LIT-820 | TAMELY RAMIFIED COVERS OF THE PROJECTIVE LINE WITH | 2020 | `arxiv:2007.12299` | read |
| KN-LIT-821 | Tandem Deep Learning Side-Channel Attack Against FPGA Implementation of AES | 2020 | `eprint:2020/373` | read |
| KN-LIT-822 | The absolute discriminant of the endomorphism ring of most reductions of a non-CM elliptic curve is close to maximal | 2020 | `arxiv:2003.01253` | read |
| KN-LIT-823 | THE STRUCTURE OF THE GROUP OF RATIONAL POINTS OF AN ABELIAN VARIETY OVER A FINITE FIELD | 2020 | `arxiv:2006.00637` | read |
| KN-LIT-824 | THE θ-CONGRUENT NUMBERS ELLIPTIC CURVES VIA A FERMAT-TYPE THEOREM | 2020 | `arxiv:2012.13451` | read |
| KN-LIT-825 | TORSION POINTS OF DRINFELD MODULES OVER LARGE ALGEBRAIC EXTENSIONS OF FINITELY GENERATED FUNCTION FIELDS | 2020 | `arxiv:2007.13949` | read |
| KN-LIT-826 | TORSION POINTS ON ISOGENOUS ABELIAN VARIETIES | 2020 | `arxiv:2011.05815` | read |
| KN-LIT-827 | Towards Post-Quantum Key-Updatable Public-Key Encryption via Supersingular Isogenies | 2020 | `eprint:2020/1593` | read |
| KN-LIT-828 | TWISTED μ4 -NORMAL FORM FOR ELLIPTIC CURVES DAVID KOHEL | 2020 | `arxiv:2012.10799` | read |
| KN-LIT-8285cb | Information-set decoding with hints | 2021 | `eprint:2021/279` | web |
| KN-LIT-829 | WHAT Ell SEES THAT K DOESN’T (WHEN p > 3) | 2020 | `arxiv:2006.16093` | read |
| KN-LIT-830 | Zero-Knowledge IOPs with | 2020 | `eprint:2020/152` | read |
| KN-LIT-831 | θ-Congruent Numbers, Tiling Numbers and the Selmer Rank of Related | 2020 | `arxiv:2010.09238` | read |
| KN-LIT-832 | Λ-SUBMODULES OF FINITE INDEX OF ANTICYCLOTOMIC | 2020 | `arxiv:2003.10301` | read |
| KN-LIT-833 | `-adic images of Galois for elliptic curves over Q | 2021 | `arxiv:2160.11141` | read |
| KN-LIT-834 | A computational proof of the existence of the Dual Isogeny | 2021 | `arxiv:2104.09213` | read |
| KN-LIT-835 | A Family of Independent Variable Eddington Factor Methods with Efficient Preconditioned Iterative Solvers | 2021 | `arxiv:2111.12255` | read |
| KN-LIT-836 | A New Isogeny Representation and Applications to Cryptography | 2021 | `eprint:2021/1600` | read |
| KN-LIT-837 | A PARAMETRIZED SET OF EXPLICIT ELEMENTS OF X(E/Q)[3] | 2021 | `arxiv:2102.11737` | read |
| KN-LIT-838 | A Semi-Permanent Stuck-At Fault Analysis on AES | 2021 | `eprint:2021/1124` | read |
| KN-LIT-839 | An Isogeny-Based ID Protocol Using Structured Public Keys | 2021 | `eprint:2021/1301` | read |
| KN-LIT-83a367 | AXI hardware accelerator for McEliece on FPGA embedded systems | 2024 | `doi:10.1109/tdsc.2024.3445181` | web |
| KN-LIT-840 | ANTICYCLOTOMIC μ-INVARIANTS OF RESIDUALLY | 2021 | `arxiv:2103.02092` | read |
| KN-LIT-841 | ASYMPTOTIC GROWTH OF MORDELL–WEIL RANKS OF ELLIPTIC CURVES IN NONCOMMUTATIVE TOWERS | 2021 | `arxiv:2109.07457` | read |
| KN-LIT-842 | Automatic Classical and Quantum Rebound Attacks on AES-like Hashing by Exploiting Related-key Differentials | 2021 | `eprint:2021/111` | read |
| KN-LIT-843 | Biases in Moments of Dirichlet Coefficients of Elliptic Curve Families Yan (Roger) Weng | 2021 | `arxiv:2102.02702` | read |
| KN-LIT-844 | Biases in Moments of the Dirichlet Coefficients in One- and Two-Parameter Families of Elliptic Curves | 2021 | `arxiv:2103.03942` | read |
| KN-LIT-845 | Big prime factors in orders of elliptic curves over finite fields | 2021 | `arxiv:2112.07046` | read |
| KN-LIT-846 | Collisions in Supersingular Isogeny Graphs and the SIDH-based Identification Protocol | 2021 | `eprint:2021/1051` | read |
| KN-LIT-847 | Commitment Schemes from Supersingular Elliptic | 2021 | `eprint:2021/1031` | read |
| KN-LIT-848 | Complete Analysis of Implementing Isogeny-based Cryptography using Huff Form of Elliptic Curves | 2021 | `eprint:2021/085` | read |
| KN-LIT-849 | Complete Practical Side-Channel-Assisted Reverse Engineering of AES-Like Ciphers | 2021 | `eprint:2021/1252` | read |
| KN-LIT-84b674 | Classic McEliece: conservative code-based cryptography: cryptosystem specification | 2022 | `url:classic.mceliece.org/mceliece-spec-20221023.pdf` | web |
| KN-LIT-850 | CONGRUENCES BETWEEN RAMANUJAN’S TAU FUNCTION | 2021 | `arxiv:2103.06154` | read |
| KN-LIT-851 | CONSTANT TAMAGAWA NUMBERS OF SPECIAL ELLIPTIC CURVES | 2021 | `arxiv:2106.00340` | read |
| KN-LIT-852 | Constructing Cubic Curves with Involutions | 2021 | `arxiv:2106.08154` | read |
| KN-LIT-853 | Counting rational points on elliptic curves with a rational 2-torsion point | 2021 | `arxiv:2105.04032` | read |
| KN-LIT-854 | Cuts and Isogenies | 2021 | `arxiv:2102.02769` | read |
| KN-LIT-855 | DeCSIDH: Delegating isogeny computations in the CSIDH setting | 2021 | `eprint:2021/700` | read |
| KN-LIT-856 | DEDUCING INFORMATION ABOUT CURVES OVER FINITE FIELDS FROM THEIR WEIL POLYNOMIALS | 2021 | `arxiv:2110.04221` | read |
| KN-LIT-857 | Deep Learning-based Side-channel Analysis against AES Inner Rounds | 2021 | `eprint:2021/981` | read |
| KN-LIT-858 | Delegating Supersingular Isogenies over Fp2 with Cryptographic Applications | 2021 | `eprint:2021/506` | read |
| KN-LIT-859 | DENSITY OF PERIODIC POINTS FOR LATTÈS MAPS OVER FINITE FIELDS arXiv:2103.00074v1 [math.NT] 26 Feb 2021 ZOË BELL, JASMINE CAMERO, KARINA CHO, TREVOR HYDE, CHIEH-MI LU | 2021 | `arxiv:2103.00074` | read |
| KN-LIT-860 | DIOPHANTINE TRIPLES AND K3 SURFACES | 2021 | `arxiv:2101.11705` | read |
| KN-LIT-861 | Efficient FPGA-based ECDSA Verification Engine for Permissioned Blockchains | 2021 | `arxiv:2112.02229` | read |
| KN-LIT-862 | ELEMENTS OF PRIME ORDER IN TATE–SHAFAREVICH GROUPS OF ABELIAN VARIETIES OVER Q | 2021 | `arxiv:2106.14096` | read |
| KN-LIT-863 | Elliptic Curve Fast Fourier Transform (ECFFT) Part I: Fast Polynomial Algorithms over all Finite Fields | 2021 | `arxiv:2107.08473` | read |
| KN-LIT-864 | Environmentally Friendly Composable Multi-Party Computation in the Plain Model from Standard (Timed) Assumptions | 2021 | `eprint:2021/843` | read |
| KN-LIT-865 | Explicit connections between supersingular isogeny graphs and Bruhat–Tits trees Laia Amorós,1 Annamaria Iezzi,2,3 Kristin Lauter,4 | 2021 | `eprint:2021/372` | read |
| KN-LIT-866 | EXPLICIT ISOGENIES OF PRIME DEGREE OVER QUADRATIC FIELDS | 2021 | `arxiv:2101.02673` | read |
| KN-LIT-867 | Extending the GLS endomorphism to speed up GHS Weil descent using Magma Jesús-Javier Chi-Domı́nguezb,a,, Francisco Rodrı́guez-Henrı́quezb,a,1, Benjamin Smithc,2 | 2021 | `arxiv:2106.09967` | read |
| KN-LIT-868 | FACTORIZATION OF MEASURES AND APPLICATIONS TO THE WEAK | 2021 | `arxiv:2108.06034` | read |
| KN-LIT-869 | Faster Key Generation of Supersingular Isogeny Diffie-Hellman | 2021 | `eprint:2021/1320` | read |
| KN-LIT-86e77b | Cofactor-torsion attacks on hinted scalar multiplications in SNARK circuits | 2026 | `eprint:2026/1776` | read |
| KN-LIT-870 | Filtered deformations of elliptic algebras | 2021 | `arxiv:2107.13540` | read |
| KN-LIT-871 | Fully projective radical isogenies in constant-time | 2021 | `eprint:2021/259` | read |
| KN-LIT-872 | Fundamenta Informaticae 184(2) : 107–139 (2021) | 2021 | `arxiv:2111.04533` | read |
| KN-LIT-873 | GENERALIZED BIRCH LEMMA AND THE 2-PART OF THE BIRCH AND SWINNERTON-DYER CONJECTURE FOR CERTAIN ELLIPTIC CURVES | 2021 | `arxiv:2102.11808` | read |
| KN-LIT-874 | Group Authentication and Key Establishment Scheme arXiv:2109.15037v2 [cs.CR] 4 May 2024 Sueda Guzey, Graduate Student Member, IEEE, Gunes Karabulut Kurt, Senior Member, IEEE | 2021 | `arxiv:2109.15037` | read |
| KN-LIT-875 | Group Signatures and More from Isogenies and Lattices: | 2021 | `eprint:2021/1366` | read |
| KN-LIT-876 | Higher-degree supersingular group actions | 2021 | `arxiv:2107.08832` | read |
| KN-LIT-877 | INFINITE FAMILIES OF ISOGENY-TORSION GRAPHS | 2021 | `arxiv:2104.01128` | read |
| KN-LIT-878 | Internet Computer Consensus Jan Camenisch, Manu Drijvers, Timo Hanke | 2021 | `eprint:2021/632` | read |
| KN-LIT-879 | ISOGENIES OF CERTAIN K3 SURFACES OF RANK | 2021 | `arxiv:2109.03189` | read |
| KN-LIT-87e00e | Collisions for Hash Functions MD4, MD5, HAVAL-128 and RIPEMD | 2004 | `eprint:2004/199` | read |
| KN-LIT-880 | Isogeny-based Group Signatures and | 2021 | `eprint:2021/1368` | read |
| KN-LIT-881 | IWASAWA INVARIANTS FOR ELLIPTIC CURVES OVER | 2021 | `arxiv:2103.16005` | read |
| KN-LIT-882 | KOLYVAGIN CLASSES VERSUS NON-CRISTALLINE DIAGONAL CLASSES | 2021 | `arxiv:2103.11492` | read |
| KN-LIT-883 | KUMMER QUARTIC SURFACES, STRICT | 2021 | `arxiv:2101.10501` | read |
| KN-LIT-884 | L-FUNCTIONS OF ELLIPTIC CURVES MODULO INTEGERS arXiv:2110.12156v3 [math.NT] 30 Nov 2022 FÉLIX BARIL BOUDREAU | 2021 | `arxiv:2110.12156` | read |
| KN-LIT-885 | Large Tate–Shafarevich orders from good abc triples | 2021 | `arxiv:2111.07794` | read |
| KN-LIT-886 | Lattice-based weak curve fault attack on ECDSA | 2021 | `eprint:2021/129` | read |
| KN-LIT-886c90 | A timing attack against the secret permutation in the McEliece PKC | 2010 | `doi:10.1007/978-3-642-12929-2_8` | web |
| KN-LIT-887 | LOCAL DATA OF RATIONAL ELLIPTIC CURVES WITH NON-TRIVIAL TORSION | 2021 | `arxiv:2104.10337` | read |
| KN-LIT-888 | Mathematical Assoc. of America | 2021 | `arxiv:2110.12226` | read |
| KN-LIT-889 | Meet-in-the-Middle Attacks Revisited: | 2021 | `eprint:2021/427` | read |
| KN-LIT-890 | MOMENTS OF GAUSSIAN HYPERGEOMETRIC FUNCTIONS OVER FINITE FIELDS | 2021 | `arxiv:2111.08393` | read |
| KN-LIT-891 | Multiradical isogenies | 2021 | `eprint:2021/1133` | read |
| KN-LIT-892 | New families of quantum stabilizer codes from Hermitian self-orthogonal algebraic geometry codes | 2021 | `arxiv:2110.00769` | read |
| KN-LIT-893 | New First-Order Secure AES Performance Records | 2021 | `eprint:2021/037` | read |
| KN-LIT-894 | NOTES ON SOLUTIONS OF KZ EQUATIONS | 2021 | `arxiv:2103.01725` | read |
| KN-LIT-895 | NUMBER OF KUMMER STRUCTURES AND MODULI SPACES OF GENERALIZED KUMMER SURFACES | 2021 | `arxiv:2106.05541` | read |
| KN-LIT-896 | ON AHLFORS CURRENTS | 2021 | `arxiv:2101.11973` | read |
| KN-LIT-897 | On Algebraic Embedding for Unstructured Lattices | 2021 | `eprint:2021/053` | read |
| KN-LIT-898 | On order of vanishing of characteristic elements | 2021 | `arxiv:2109.03985` | read |
| KN-LIT-899 | On parameterizations of cyclic N -isogenies and strict K-curves lying above rational points of Y0+(N ) | 2021 | `arxiv:2110.13908` | read |
| KN-LIT-89d5df | Compact GF(2) systemizer and optimized constant-time hardware sorters for Key Generation in Classic McEliece | 2022 | `eprint:2022/1277` | web |
| KN-LIT-8d884f | Efficient ASIC architecture for low latency Classic McEliece decoding | 2024 | `doi:10.46586/tches.v2024.i2.403-425` | web |
| KN-LIT-900 | ON SELMER GROUPS IN THE SUPERSINGULAR REDUCTION CASE | 2021 | `arxiv:2103.06147` | read |
| KN-LIT-901 | ON THE AVERAGE OF p-SELMER RANK IN QUADRATIC TWIST FAMILIES OF ELLIPTIC CURVES OVER FUNCTION FIELD | 2021 | `arxiv:2102.00549` | read |
| KN-LIT-902 | ON THE BIRCH–SWINNERTON-DYER CONJECTURE FOR MODULAR | 2021 | `arxiv:2110.13102` | read |
| KN-LIT-903 | On the Isogeny Problem with Torsion Point Information | 2021 | `eprint:2021/153` | read |
| KN-LIT-904 | On the security of ECDSA with additive key derivation and presignatures | 2021 | `eprint:2021/1330` | read |
| KN-LIT-905 | ON THE SELMER GROUP AND RANK OF A FAMILY OF | 2021 | `arxiv:2111.03723` | read |
| KN-LIT-906 | One-way functions and malleability oracles: Hidden shift attacks on isogeny-based protocols | 2021 | `eprint:2021/282` | read |
| KN-LIT-907 | Online-Extractability in the Quantum Random-Oracle Model? | 2021 | `eprint:2021/280` | read |
| KN-LIT-908 | Plectic p-adic invariants | 2021 | `arxiv:2104.12566` | read |
| KN-LIT-909 | Post-quantum Resettably-Sound Zero Knowledge? | 2021 | `eprint:2021/349` | read |
| KN-LIT-910 | PRIMITIVE DIVISORS OF SEQUENCES ASSOCIATED TO ELLIPTIC CURVES OVER FUNCTION FIELDS | 2021 | `arxiv:2103.06787` | read |
| KN-LIT-911 | privateDH: An Enhanced Diffie-Hellman Key-Exchange Protocol using RSA and AES Algorithms | 2021 | `eprint:2021/647` | read |
| KN-LIT-912 | Probability Distributions for Elliptic Curves in the CGL Hash Function | 2021 | `arxiv:2108.06457` | read |
| KN-LIT-913 | Proof of Assets in the Diem Blockchain | 2021 | `eprint:2021/598` | read |
| KN-LIT-914 | PURELY ARITHMETIC PDE’S OVER A p-ADIC FIELD I: | 2021 | `arxiv:2103.16627` | read |
| KN-LIT-915 | Quadratic Fields Admitting Elliptic Curves with | 2021 | `arxiv:2103.09814` | read |
| KN-LIT-916 | QUADRATIC POINTS ON BIELLIPTIC MODULAR CURVES | 2021 | `arxiv:2112.03226` | read |
| KN-LIT-917 | RANK GROWTH OF ELLIPTIC CURVES OVER N -TH ROOT EXTENSIONS | 2021 | `arxiv:2112.12864` | read |
| KN-LIT-918 | REPRESENTATIONS ATTACHED TO ELLIPTIC CURVES WITH A NON-TRIVIAL ODD TORSION POINT | 2021 | `arxiv:2106.15722` | read |
| KN-LIT-919 | Resistance of Isogeny-Based Cryptographic | 2021 | `eprint:2021/850` | read |
| KN-LIT-920 | Revisiting Homomorphic Encryption Schemes for Finite Fields ? | 2021 | `eprint:2021/204` | read |
| KN-LIT-921 | Richelot Isogenies, Pairings on Squared Kummer | 2021 | `eprint:2021/1617` | read |
| KN-LIT-922 | Round-Efficient Byzantine Agreement and Multi-Party Computation with Asynchronous Fallback | 2021 | `eprint:2021/1141` | read |
| KN-LIT-923 | SANDPILE GROUPS OF SUPERSINGULAR ISOGENY GRAPHS | 2021 | `arxiv:2111.10389` | read |
| KN-LIT-924 | Secure Linear Aggregation Using Decentralized | 2021 | `arxiv:2111.10753` | read |
| KN-LIT-925 | SHealS and HealS: isogeny-based PKEs from a key validation method for SIDH | 2021 | `eprint:2021/1596` | read |
| KN-LIT-926 | SHORT-INTERVAL SECTOR PROBLEMS FOR CM ELLIPTIC CURVES | 2021 | `arxiv:2105.11093` | read |
| KN-LIT-927 | Side Channel Analysis against the ANSSI’s protected AES implementation on ARM | 2021 | `eprint:2021/592` | read |
| KN-LIT-928 | SPORADIC POINTS OF ODD DEGREE ON X1 (N ) COMING FROM Q-CURVES | 2021 | `arxiv:2107.10909` | read |
| KN-LIT-929 | Sumcheck Arguments and their Applications ? | 2021 | `eprint:2021/333` | read |
| KN-LIT-930 | Superposition Meet-in-the-Middle Attacks: Updates on Fundamental Security of AES-like Hashing | 2021 | `eprint:2021/575` | read |
| KN-LIT-931 | Supersingular Isogeny-Based Ring Signature? | 2021 | `eprint:2021/1318` | read |
| KN-LIT-932 | SYMBOL LENGTH IN BRAUER GROUPS OF ELLIPTIC CURVES | 2021 | `arxiv:2107.10886` | read |
| KN-LIT-933 | TAMAGAWA NUMBERS OF ELLIPTIC CURVES WITH PRESCRIBED TORSION | 2021 | `arxiv:2102.04834` | read |
| KN-LIT-934 | The Case for SIKE A Decade of the Supersingular Isogeny Problem | 2021 | `eprint:2021/543` | read |
| KN-LIT-935 | THE FAILURE OF GALOIS DESCENT FOR p-SELMER GROUPS OF ELLIPTIC CURVES arXiv:2106.02486v2 [math.NT] 1 May 2024 ROSS PATERSON | 2021 | `arxiv:2106.02486` | read |
| KN-LIT-936 | The Impact of Hardware Specifications on Reaching Quantum Advantage in the Fault Tolerant Regime | 2021 | `arxiv:2108.12371` | read |
| KN-LIT-937 | The Lang-Trotter Conjecture for the elliptic curve y 2 = x3 + Dx | 2021 | `arxiv:2108.06292` | read |
| KN-LIT-938 | TORSION FOR CM ELLIPTIC CURVES DEFINED OVER NUMBER FIELDS OF DEGREE 2p | 2021 | `arxiv:2110.07819` | read |
| KN-LIT-939 | TORSION GROUPS OF MORDELL CURVES OVER NUMBER FIELDS OF HIGHER DEGREE | 2021 | `arxiv:2105.04954` | read |
| KN-LIT-93ad69 | Perturbation of Hankel moment singular values and supersingular endomorphism rings via CVP | 2026 | `eprint:2026/1586` | read |
| KN-LIT-940 | TYPICALLY BOUNDING TORSION ON ELLIPTIC CURVES ISOGENOUS TO RATIONAL j-INVARIANT | 2021 | `arxiv:2112.11566` | read |
| KN-LIT-941 | VARIATION OF CANONICAL HEIGHT FOR FATOU POINTS ON P1 | 2021 | `arxiv:2107.05982` | read |
| KN-LIT-942 | Verifiable Isogeny Walks: Towards an Isogeny-based Postquantum VDF | 2021 | `eprint:2021/1289` | read |
| KN-LIT-943 | l-ADIC IMAGES OF GALOIS FOR ELLIPTIC CURVES OVER Q | 2021 | `arxiv:2106.11141` | read |
| KN-LIT-944 | 2-ADIC GALOIS IMAGES OF ISOGENY-TORSION GRAPHS OVER Q WITH CM | 2022 | `arxiv:2208.11649` | read |
| KN-LIT-945 | A JACOBI SYMBOL CRITERION INVOLVING k-FIBONACCI | 2022 | `arxiv:2203.11755` | read |
| KN-LIT-946 | A NEW ASPECT OF CHEBYSHEV’S BIAS FOR ELLIPTIC CURVES OVER FUNCTION FIELDS | 2022 | `arxiv:2206.05445` | read |
| KN-LIT-947 | A Note on Reimplementing the Castryck-Decru Attack and Lessons Learned for SageMath | 2022 | `eprint:2022/1283` | read |
| KN-LIT-948 | Abelian Varieties with p-rank Zero | 2022 | `arxiv:2203.08401` | read |
| KN-LIT-949 | ADDING LEVEL STRUCTURE TO SUPERSINGULAR ELLIPTIC CURVE | 2022 | `arxiv:2203.03531` | read |
| KN-LIT-950 | ALGEBRAIC INDEPENDENCE AND DIFFERENCE EQUATIONS OVER ELLIPTIC FUNCTION FIELDS | 2022 | `arxiv:2207.13377` | read |
| KN-LIT-951 | An attack on SIDH with arbitrary starting curve (draft) | 2022 | `eprint:2022/1026` | read |
| KN-LIT-952 | Another Round of Breaking and Making Quantum Money: How to Not Build It from Lattices, and More | 2022 | `arxiv:2211.11994` | read |
| KN-LIT-95256d | Attacks Against the IND-CPA^D Security of Exact FHE Schemes | 2024 | `eprint:2024/127` | web |
| KN-LIT-953 | ASYMPTOTIC FERMAT FOR SIGNATURE (4, 2, p) OVER NUMBER FIELDS | 2022 | `arxiv:2209.09153` | read |
| KN-LIT-954 | ASYMPTOTIC FORMULA FOR TATE–SHAFAREVICH GROUPS OF p-SUPERSINGULAR ELLIPTIC CURVES OVER ANTICYCLOTOMIC EXTENSIONS | 2022 | `arxiv:2203.14164` | read |
| KN-LIT-955 | Attaining GOD Beyond Honest Majority With Friends and Foes | 2022 | `eprint:2022/120` | read |
| KN-LIT-956 | Beyond the Csiszár-Korner Bound: Best-Possible Wiretap Coding via Obfuscation | 2022 | `eprint:2022/343` | read |
| KN-LIT-957 | BILINEAR FORMS WITH TRACE FUNCTIONS OVER | 2022 | `arxiv:2211.14702` | read |
| KN-LIT-958 | Breaking a fully Balanced ASIC Coprocessor Implementing Complete Addition Formulas on Weierstrass Elliptic Curves | 2022 | `arxiv:2201.01158` | read |
| KN-LIT-959 | BULGARIAN ACADEMY OF SCIENCES CYBERNETICS AND INFORMATION TECHNOLOGIES  Volume 21, No 2 Sofia  2021 | 2022 | `arxiv:2208.01635` | read |
| KN-LIT-960 | CLASS GROUP STATISTICS FOR TORSION FIELDS GENERATED BY ELLIPTIC CURVES | 2022 | `arxiv:2204.09757` | read |
| KN-LIT-961 | Computing 2a-isogenies in Legendre Form | 2022 | `eprint:2022/870` | read |
| KN-LIT-962 | COMPUTING ISOGENIES BETWEEN FINITE DRINFELD MODULES BENJAMIN WESOLOWSKI | 2022 | `eprint:2022/438` | read |
| KN-LIT-963 | COUNTING ELLIPTIC CURVES OVER THE RATIONALS WITH A 7-ISOGENY | 2022 | `arxiv:2212.11354` | read |
| KN-LIT-964 | COUNTING POINTS ON ABELIAN SURFACES OVER FINITE FIELDS WITH ELKIES’S METHOD | 2022 | `arxiv:2203.02009` | read |
| KN-LIT-965 | COVERING FAMILIES OF THE ASYMMETRIC QUANTUM RABI MODEL: η-SHIFTED NON-COMMUTATIVE HARMONIC OSCILLATORS | 2022 | `arxiv:2209.14665` | read |
| KN-LIT-966 | CYCLIC ISOGENIES OF ELLIPTIC CURVES OVER FIXED | 2022 | `arxiv:2206.08891` | read |
| KN-LIT-967 | Derived Zeta Functions for Curves over Finite Fields | 2022 | `arxiv:2203.11488` | read |
| KN-LIT-968 | DYNAMICS ON P1 : PREPERIODIC POINTS AND PAIRWISE STABILITY | 2022 | `arxiv:2212.13215` | read |
| KN-LIT-969 | Efficient NIZKs and Signatures from Commit-and-Open Protocols in the QROM? | 2022 | `eprint:2022/270` | read |
| KN-LIT-970 | Efficient Proofs of Knowledge for Threshold Relations | 2022 | `eprint:2022/746` | read |
| KN-LIT-970963 | Dimension Reduction for SVP in HAWK: A Trace-Zero Approach | 2026 | `eprint:2026/1560` | read |
| KN-LIT-971 | ELLIPTIC ANALOGUE OF IRREGULAR PRIME NUMBERS FOR THE pn -DIVISION FIELDS OF THE CURVES y 2 = x3 − (s4 + t2 )x | 2022 | `arxiv:2205.08946` | read |
| KN-LIT-972 | Elliptic Loops | 2022 | `arxiv:2204.08019` | read |
| KN-LIT-973 | Endomorphism Rings of Supersingular Elliptic Curves over Fp and Binary Quadratic Forms | 2022 | `arxiv:2203.02097` | read |
| KN-LIT-974 | EXPLICIT BOUNDS ON THE COEFFICIENTS OF MODULAR POLYNOMIALS FOR THE ELLIPTIC j-INVARIANT | 2022 | `arxiv:2211.06019` | read |
| KN-LIT-975 | EXPLICIT CLASSIFICATION OF ISOGENY GRAPHS OF RATIONAL ELLIPTIC CURVES | 2022 | `arxiv:2208.05603` | read |
| KN-LIT-976 | EXPLICIT ISOGENIES OF PRIME DEGREE OVER NUMBER FIELDS | 2022 | `arxiv:2203.06009` | read |
| KN-LIT-977 | EXPLICIT SATO-TATE TYPE DISTRIBUTION FOR A FAMILY OF K3 SURFACES | 2022 | `arxiv:2207.01597` | read |
| KN-LIT-978 | Extending Lenstra’s Primality Test to CM | 2022 | `arxiv:2212.04463` | read |
| KN-LIT-979 | Failing to hash into supersingular isogeny graphs | 2022 | `eprint:2022/518` | read |
| KN-LIT-980 | FAMILIES OF φ-CONGRUENCE SUBGROUPS OF THE MODULAR GROUP | 2022 | `arxiv:2206.12442` | read |
| KN-LIT-981 | FILTRATIONS OF THE CHOW GROUP OF ZERO-CYCLES ON | 2022 | `arxiv:2210.14372` | read |
| KN-LIT-982 | FPGA Acceleration of Multi-Scalar Multiplication: CycloneMSM Kaveh Aasaraai, Don Beaver, Emanuele Cesena, Rahul Maganti | 2022 | `eprint:2022/1396` | read |
| KN-LIT-983 | Full Quantum Equivalence of | 2022 | `eprint:2022/113` | read |
| KN-LIT-984 | Further Cryptanalysis of a Type of RSA Variants | 2022 | `eprint:2022/611` | read |
| KN-LIT-98438d | FrodoKEM: A CCA-Secure Learning With Errors Key Encapsulation Mechanism | 2025 | `eprint:2025/1861` | read |
| KN-LIT-985 | Generalising Fault Attacks to Genus Two Isogeny Cryptosystems | 2022 | `eprint:2022/196` | read |
| KN-LIT-986 | GENERALIZED CLASS POLYNOMIALS | 2022 | `arxiv:2207.08915` | read |
| KN-LIT-987 | GENERATORS FOR THE ELLIPTIC CURVE arXiv:2206.05740v2 [math.NT] 6 Jul 2022 E(p,q) : y 2 = x3 − p2 x + q | 2022 | `arxiv:2206.05740` | read |
| KN-LIT-988 | GROWTH OF TORSION GROUPS OF ELLIPTIC CURVES UPON BASE CHANGE FROM NUMBER FIELDS | 2022 | `arxiv:2210.16977` | read |
| KN-LIT-989 | Guaranteed Output in O( n) Rounds for Round-Robin Sampling Protocols? | 2022 | `eprint:2022/257` | read |
| KN-LIT-990 | Horizontal racewalking using radical isogenies | 2022 | `eprint:2022/1259` | read |
| KN-LIT-991 | Hyperexponential solutions of elliptic difference equations | 2022 | `arxiv:2205.00041` | read |
| KN-LIT-992 | Hyperspherical Trigonometry and Corresponding Elliptic Functions | 2022 | `arxiv:2211.13983` | read |
| KN-LIT-993 | IDEAL CLASS GROUPS OF NUMBER FIELDS AND BLOCH-KATO’S TATE-SHAFAREVICH GROUPS FOR SYMMETRIC POWERS OF ELLIPTIC CURVES | 2022 | `arxiv:2204.07759` | read |
| KN-LIT-994 | IDEAL CLASS GROUPS OF NUMBER FIELDS ASSOCIATED TO MODULAR GALOIS REPRESENTATIONS | 2022 | `arxiv:2205.05238` | read |
| KN-LIT-995 | Improved Straight-Line Extraction in the Random Oracle Model With Applications to Signature Aggregation | 2022 | `eprint:2022/393` | read |
| KN-LIT-996 | ISOGENIES OVER QUADRATIC FIELDS OF ELLIPTIC CURVES WITH RATIONAL j-INVARIANT | 2022 | `arxiv:2203.10672` | read |
| KN-LIT-997 | ISOGENY GRAPHS ON SUPERSPECIAL ABELIAN VARIETIES: | 2022 | `arxiv:2201.04293` | read |
| KN-LIT-998 | Key Structures: Improved Related-Key Boomerang Attack against the Full AES-256 | 2022 | `eprint:2022/845` | read |
| KN-LIT-999 | Local inversion of maps: A new attack on | 2022 | `arxiv:2202.06584` | read |
| KN-LIT-a24b73 | Triple Cryptanalysis of Isogeny-Based VRFs from Asiacrypt 2025 | 2026 | `eprint:2026/1623` | read |
| KN-LIT-a409fc | New approaches to reduced complexity decoding | 1991 | `doi:10.1016/0166-218x(91)90107-8` | web |
| KN-LIT-a4d70e | The syzygy distinguisher | 2025 | `eprint:2024/1193` | web |
| KN-LIT-a58ca4 | How to lose some weight - a practical template syndrome decoding attack | 2025 | `eprint:2024/621` | web |
| KN-LIT-a740ab | Optimized implementation of encapsulation and decapsulation of Classic McEliece on ARMv8 | 2022 | `eprint:2022/1706` | web |
| KN-LIT-a85246 | Multi-instance security degradation of code-based KEMs | 2026 | `eprint:2026/517` | web |
| KN-LIT-aa3372 | A complete quantum circuit to solve the information set decoding problem | 2021 | `doi:10.1109/qce52317.2021.00056` | web |
| KN-LIT-ace115 | Acceleration of Classic McEliece post-quantum cryptosystem with cache processing | 2023 | `doi:10.1109/mm.2023.3304425` | web |
| KN-LIT-ae8a1e | A modular analysis of the Fujisaki-Okamoto transformation | 2017 | `eprint:2017/604` | web |
| KN-LIT-b03de7 | Non-binary information set decoding and an attack on BCH-McEliece: A tale of two approaches to code-based cryptanalysis | 2025 | `url:backend.orbit.dtu.dk/ws/portalfiles/portal/429438711/phd_thesis_fe.pdf` | false |
| KN-LIT-b175dc | Acceleration of McEliece cryptosystem with instruction set extension for RISC-V | 2025 | `doi:10.1109/csr64739.2025.11130090` | web |
| KN-LIT-b2191d | Decoding linear codes with high error rate and its impact for LPN security | 2018 | `eprint:2017/1139` | web |
| KN-LIT-b2df4f | Multiparallel MMT: faster ISD algorithm solving high-dimensional syndrome decoding problem | 2023 | `doi:10.1587/transfun.2022cip0023` | web |
| KN-LIT-b46f62 | Implementation of Classic McEliece key generation based on Goppa binary code | 2022 | `doi:10.1109/icsict55466.2022.9963372` | web |
| KN-LIT-b5686a | McBits revisited | 2017 | `doi:10.1007/978-3-319-66787-4_11` | web |
| KN-LIT-b66899 | Statistical decoding | 2017 | `arxiv:1701.07416` | web |
| KN-LIT-b777d1 | Algebraic approach for code equivalence | 2018 | `doi:10.70675/4409179fzb277z4e80z8334z16f39e22980c` | web |
| KN-LIT-b8093a | Solving the Shortest Vector Problem in 2^{0.6039n} Time via Mid-point Hessian | 2026 | `eprint:2026/1597` | read |
| KN-LIT-b8a8be | Memory-efficient quantum information set decoding algorithm | 2023 | `doi:10.1007/978-3-031-35486-1_20` | web |
| KN-LIT-b9d3e0 | How to backdoor (Classic) McEliece and how to guard against backdoors | 2022 | `eprint:2022/362` | web |
| KN-LIT-b9e1a8 | Hamming Quasi-Cyclic (HQC) | 2025 | `url:pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf` | read |
| KN-LIT-bb53c1 | A non asymptotic analysis of information set decoding | 2013 | `eprint:2013/162` | web |
| KN-LIT-bbd0e9 | A probabilistic algorithm for computing minimum weights of large error-correcting codes | 1988 | `doi:10.1109/18.21270` | web |
| KN-LIT-bfef5d | Leveraging HLS to design a versatile & high-performance Classic McEliece accelerator | 2024 | `doi:10.1145/3698395` | web |
| KN-LIT-c0a19f | Modeling bit flipping decoding based on nonorthogonal check sums with application to iterative decoding attack of McEliece cryptosystem | 2007 | `doi:10.1109/tit.2006.887515` | web |
| KN-LIT-c2c4d0 | Reaction attacks against several public-key cryptosystems | 1999 | `url:cypherpunks.ca/~iang/pubs/paper-reaction-attacks.pdf` | false |
| KN-LIT-c41d8b | Polynomial time key-recovery attack on high rate random alternant codes (boundary corrected: generic alternant only, Goppa codes explicitly excluded) | 2024 | `arxiv:2304.14757` | transcription_of_full_text_at_recorded_sha256 |
| KN-LIT-c4974d | Analysis of backdoored (Classic) McEliece in a multi-user setting | 2024 | `doi:10.1007/978-981-95-0172-4_1` | web |
| KN-LIT-caabe2 | Two decoding algorithms for linear codes | 1989 | `url:www.mathnet.ru/eng/ppi635` | false |
| KN-LIT-cd29fd | Quantum sieving for code-based cryptanalysis and its limitations for ISD | 2025 | `eprint:2024/1358` | web |
| KN-LIT-cd9880 | McEliece cryptosystem implementation: theory and practice | 2008 | `doi:10.1007/978-3-540-88403-3_4` | web |
| KN-LIT-ced593 | On the complexity of some cryptographic problems based on the general decoding problem | 2002 | `doi:10.1109/isit.1998.709047` | web |
| KN-LIT-d15818 | FPGA-based Niederreiter cryptosystem using binary Goppa codes | 2018 | `eprint:2017/1180` | web |
| KN-LIT-d3ec68 | Preimage Attacks on 3-Pass HAVAL and Step-Reduced MD5 | 2008 | `eprint:2008/183` | read |
| KN-LIT-d4f467 | Embedded Elliptic Curves and Embedded Families for SNARK-Friendly Elliptic Curves | 2024 | `eprint:2024/1737` | read |
| KN-LIT-d5b1a7 | Fast hardware architecture with efficient matrix computations for the key generation of Classic McEliece | 2025 | `doi:10.1109/tcsi.2025.3528119` | web |
| KN-LIT-d5baac | Post-quantum WireGuard | 2021 | `eprint:2020/379` | web |
| KN-LIT-d6d510 | An attack on the CFS scheme and on TII McEliece challenges | 2026 | `eprint:2026/430` | web |
| KN-LIT-d78021 | AI for code-based cryptography | 2025 | `eprint:2025/440` | web |
| KN-LIT-d82a53 | A note on the Goppa code distinguishing problem | 2025 | `eprint:2025/1661` | web |
| KN-LIT-d962e5 | A safety-critical, RISC-V SoC integrated and ASIC-ready Classic McEliece accelerator | 2024 | `doi:10.1007/978-3-031-55673-9_20` | web |
| KN-LIT-dd47da | Optimizing BJMM with nearest neighbors: full decoding in 2^{2n/21} and McEliece security | 2017 | `url:web.archive.org/web/20201127050037/https://www.cits.ruhr-uni-bochum.de/imperia/md/content/may/paper/bjmm+.pdf` | false |
| KN-LIT-de5373 | Security analysis for BIKE, Classic McEliece and HQC against the quantum ISD algorithms | 2022 | `eprint:2022/1771` | web |
| KN-LIT-e204ab | A Polynomial-Time Quantum Algorithm for the Dihedral Coset Problem (Simon 2026, preliminary draft) | 2026 | `eprint:2026/1591` | read |
| KN-LIT-e37d4c | A note on the Goppa code distinguishing problem | 2025 | `eprint:2025/1661` | web |
| KN-LIT-e3fe13 | An IND-CCA2 attack against the 1st- and 2nd-round versions of NTS-KEM | 2020 | `doi:10.1007/978-3-030-69255-1_11` | web |
| KN-LIT-e4a472 | The tangent space attack | 2025 | `eprint:2025/763` | web |
| KN-LIT-e530e8 | Side channels in the McEliece PKC | 2008 | `doi:10.1007/978-3-540-88403-3_15` | web |
| KN-LIT-e800e6 | A key-recovery side-channel attack on Classic McEliece implementations | 2022 | `eprint:2022/514` | web |
| KN-LIT-e8eaf8 | A designer's guide to KEMs | 2003 | `eprint:2002/174` | web |
| KN-LIT-eb2b9b | NIST IR 8545: Status Report on the Fourth Round of the NIST Post-Quantum Cryptography Standardization Process | 2025 | `doi:10.6028/nist.ir.8545` | web |
| KN-LIT-ef4327 | Concrete time/memory trade-offs in generalised Stern's ISD algorithm | 2023 | `eprint:2023/1940` | web |
| KN-LIT-f1073f | On breaking McEliece keys using brute force | 2025 | `eprint:2025/632` | web |
| KN-LIT-f1eb40 | Algebraic key-recovery side-channel attack on Classic McEliece | 2025 | `doi:10.1007/978-3-032-10536-3_20` | web |
| KN-LIT-f28b46 | Revisiting nearest-neighbor-based information set decoding | 2022 | `eprint:2022/1328` | web |
| KN-LIT-f390dc | A new algorithm for finding minimum-weight words in a linear code: application to McEliece's cryptosystem and to narrow-sense BCH codes of length 511 | 1998 | `doi:10.1109/18.651067` | web |
| KN-LIT-f50ab3 | Leaky McEliece: secret key recovery from highly erroneous side-channel information | 2025 | `eprint:2023/1536` | web |
| KN-LIT-f51628 | Sieving method for SDP with the zero window: an improvement in low memory environments | 2024 | `doi:10.1007/978-981-97-7737-2_9` | web |
| KN-LIT-f6de4b | Bombieri–Weil bound (additive / Artin–Schreier case) — attempted verification of hypothesis (H1') | 1966 | `url:encyclopediaofmath.org/wiki/bombieri-weil_bound` | secondary_only |
| KN-LIT-f7d7dd | Improved quantum information set decoding | 2018 | `arxiv:1808.00714v1` | web |
| KN-LIT-fa9bc8 | Analysis of information set decoding for a sub-linear error weight | 2016 | `doi:10.1007/978-3-319-29360-8_10` | web |
| KN-LIT-fab214 | Punctured syndrome decoding problem: Efficient side-channel attacks against Classic McEliece | 2023 | `eprint:2023/308` | web |
| KN-LIT-fb3102 | A statistical decoding algorithm for general linear block codes | 2001 | `doi:10.1007/3-540-45325-3_1` | web |
| KN-LIT-fb9047 | A method for finding codewords of small weight | 1989 | `doi:10.1007/bfb0019850` | web |
| KN-LIT-fbc2c8 | Breaking Goppa-based McEliece with hints | 2022 | `eprint:2022/525` | web |
| KN-LIT-fd29f0 | Security-analysis of a class of cryptosystems based on linear error-correcting codes | 1994 | `doi:10.6100/ir426904` | false |

## 6. Literature citations with no recorded identifier

5610 entries name a source this index cannot resolve to a
retrievable location. They are listed, not dropped and not backfilled by
guesswork (AGENTS.md rule 5): closing a row means finding the identifier
and editing the entry, after which this table shrinks on its own.

| ID | Title | Year | Venue | Verified |
|---|---|---|---|---|
| KN-LIT-0cbb26 | Montgomery Multiplication on the Cell | 2012 | preprint (EPFL) | read |
| KN-LIT-10be29 | An observation on the security of McEliece's public-key cryptosystem | 1988 | Eurocrypt | false |
| KN-LIT-17708c | On minimum distance decoding of linear codes | 1991 | Fifth joint Soviet-Swedish international workshop on information theory | false |
| KN-LIT-180ad5 | Side-Channel and Fault-Injection Attacks on Kyber and Dilithium: Survey and New Results | 2022 | IACR ePrint 2022/737 (IEEE Trans. Computers venue unconfirmed from ePrint record) | partial |
| KN-LIT-1966 | (Almost) Optimal Constructions of UOWHFs from 1-to-1, Regular One-way Functions and Beyond |  |  | read |
| KN-LIT-1967 | (Batch) Fully Homomorphic Encryption over Integers for Non-Binary Message Spaces |  |  | read |
| KN-LIT-1968 | (CM) Torsion on Elliptic Curves over Number Fields |  |  | read |
| KN-LIT-1969 | (Compact) Adaptively Secure FE for Attribute-Weighted Sums from k-Lin |  |  | read |
| KN-LIT-1970 | (Efficient) Universally Composable Oblivious |  |  | read |
| KN-LIT-1971 | (Hierarchical) Identity-Based Encryption from Affine Message Authentication |  |  | read |
| KN-LIT-1972 | (Nearly) round-optimal black-box constructions of commitments secure against selective opening attacks |  |  | read |
| KN-LIT-1973 | (Nondeterministic) Hardness vs. Non-Malleability |  |  | read |
| KN-LIT-1974 | (One) failure is not an option Bootstrapping the search for failures in lattice-based encryption schemes |  |  | read |
| KN-LIT-1975 | (Password) Authenticated Key Establishment: From 2-Party To Group |  |  | read |
| KN-LIT-1976 | (Pseudo) Preimage Attack on Round-Reduced |  |  | read |
| KN-LIT-1977 | (Pseudo) Random Quantum States with Binary Phase? |  |  | read |
| KN-LIT-1978 | (R)CCA Secure Updatable Encryption with Integrity Protection |  |  | read |
| KN-LIT-1979 | (Verifiable) Delay Functions from Lucas Sequences |  |  | read |
| KN-LIT-1980 | 0-RTT Key Exchange with Full Forward Secrecy |  |  | read |
| KN-LIT-1981 | 1-out-of-n Signatures from a Variety of Keys |  |  | read |
| KN-LIT-1982 | 10-Round Feistel is Indifferentiable from an Ideal Cipher? |  | Journal of Cryptology | read |
| KN-LIT-1983 | 18/10/2022 1/19 1. Supersingular Isogeny Diffie-Hellman (SIDH) An efficient key recovery attack on |  |  | read |
| KN-LIT-1984 | 2-ADIC POINT COUNTING ON K3 SURFACES |  |  | read |
| KN-LIT-1985 | 256 bit Standardized Crypto for 650 GE – GOST Revisited? |  |  | read |
| KN-LIT-1986 | 3-Message Zero Knowledge |  |  | read |
| KN-LIT-1987 | 3-Move Undeniable Signature Scheme |  |  | read |
| KN-LIT-1988 | 3-Party Secure Computation for RAMs: |  |  | read |
| KN-LIT-1989 | 3kf9: Enhancing 3GPP-MAC beyond the Birthday Bound |  |  | read |
| KN-LIT-1990 | 4-Round Luby-Rackoff Construction is a qPRP |  |  | read |
| KN-LIT-1991 | 4-Round Resettably-Sound Zero Knowledge |  |  | read |
| KN-LIT-1992 | [Page 1] arXiv:math/9903208v1 [math.NT] 18 Mar 1999 On Tate-Shafarevich Groups of some Elliptic Curves |  |  | read |
| KN-LIT-1993 | `-Invertible Cycles for Multivariate Quadratic (MQ) Public Key Cryptography |  |  | read |
| KN-LIT-1994 | A (Second) Preimage Attack on the GOST Hash Function |  |  | read |
| KN-LIT-1995 | A 270 Attack on the Full MISTY1 |  |  | read |
| KN-LIT-1996 | A 2n/2 -Time Algorithm for n-SVP and √ |  |  | read |
| KN-LIT-1997 | A Bit-Vector Differential Model for the Modular Addition by a Constant |  |  | read |
| KN-LIT-1998 | A Black-Box Approach to Post-Quantum Zero-Knowledge in Constant Rounds |  |  | read |
| KN-LIT-1999 | A Black-Box Construction of Fully-Simulatable, Round-Optimal Oblivious Transfer from Strongly Uniform Key Agreement |  |  | read |
| KN-LIT-1eb70d | Application de la méthode de décodage itérative d'Omura à la cryptanalyse du système de McEliece | 1993 |  | false |
| KN-LIT-2000 | A Block-Cipher Mode of Operation for Parallelizable Message Authentication |  |  | read |
| KN-LIT-2001 | A Chosen Ciphertext Attack on RSA Optimal Asymmetric Encryption Padding (OAEP) as Standardized in PKCS #1 v2.0 |  |  | read |
| KN-LIT-2002 | A Classification of Computational Assumptions in the Algebraic Group Model |  |  | read |
| KN-LIT-2003 | A Closer Look at Anonymity and Robustness in Encryption Schemes |  |  | read |
| KN-LIT-2004 | A Closer Look at PKI: Security and Efficiency |  |  | read |
| KN-LIT-2005 | A Coding-Theoretic Approach to Recovering Noisy RSA Keys |  |  | read |
| KN-LIT-2006 | A Collision-Attack on AES |  |  | read |
| KN-LIT-2007 | A Combinatorial Approach to Quantum Random Functions |  |  | read |
| KN-LIT-2008 | A Comparison and a Combination of SST and AGM Algorithms for Counting Points of Elliptic |  |  | read |
| KN-LIT-2009 | A Complete and Explicit Security Reduction Algorithm for RSA-based Cryptosystems |  |  | read |
| KN-LIT-2010 | A Complete Characterization of |  |  | read |
| KN-LIT-2011 | A complete set of addition laws for incomplete Edwards curves |  |  | read |
| KN-LIT-2012 | A Comprehensive Evaluation of Mutual |  |  | read |
| KN-LIT-2013 | A Compressed Σ-Protocol Theory for Lattices |  |  | read |
| KN-LIT-2014 | A Concrete Security Analysis for 3GPP-MAC |  |  | read |
| KN-LIT-2015 | A Concrete Treatment of Fiat-Shamir Signatures in the Quantum Random-Oracle Model |  |  | read |
| KN-LIT-2016 | A Cookbook for Black-Box Separations and a Recipe for UOWHFs |  |  | read |
| KN-LIT-2017 | A Correct, Private and Efficient Mix Network |  |  | read |
| KN-LIT-2018 | A Correlation Attack on Full SNOW-V and SNOW-Vi |  |  | read |
| KN-LIT-2019 | A Counterexample to the Chain Rule for Conditional HILL Entropy? And what Deniable Encryption has to do with it |  |  | read |
| KN-LIT-2020 | A Critical Analysis of ISO 17825 (‘Testing methods for the mitigation of non-invasive attack classes against cryptographic modules’) |  |  | read |
| KN-LIT-2021 | A Cryptanalysis of PRINTcipher: The Invariant Subspace Attack |  |  | read |
| KN-LIT-2022 | A Dedicated Sieving Hardware |  |  | read |
| KN-LIT-2023 | A Deeper Look at Machine Learning-Based Cryptanalysis |  |  | read |
| KN-LIT-2024 | A Design Flow and Evaluation Framework for |  |  | read |
| KN-LIT-2025 | A Design for a Physical RNG with Robust Entropy Estimators |  |  | read |
| KN-LIT-2026 | A Design Methodology for a DPA-Resistant Cryptographic LSI with RSL Techniques |  |  | read |
| KN-LIT-2027 | A Design Methodology for Stealthy Parametric |  |  | read |
| KN-LIT-2028 | A Detailed Analysis of Fiat-Shamir with Aborts |  |  | read |
| KN-LIT-2029 | A DETERMINISTIC ALGORITHM FOR FINDING r-POWER DIVISORS |  |  | read |
| KN-LIT-2030 | A Dichotomy for Local Small-Bias Generators |  |  | read |
| KN-LIT-2031 | A Differential Fault Attack against Early Rounds of (Triple-)DES |  |  | read |
| KN-LIT-2032 | A Differential Fault Attack on MICKEY 2.0 |  |  | read |
| KN-LIT-2033 | A Digital Signature Scheme based on CV P∞ ? |  |  | read |
| KN-LIT-2034 | A Direct Anonymous Attestation Scheme for Embedded Devices |  |  | read |
| KN-LIT-2035 | A discretization attack |  |  | read |
| KN-LIT-2036 | A Distributed Online Certificate Status Protocol with a Single Public Key |  |  | read |
| KN-LIT-2037 | A Domain Extender for the Ideal Cipher |  |  | read |
| KN-LIT-2038 | A Double-Piped Mode of Operation for MACs, PRFs and PROs: Security beyond the Birthday Barrier |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2039 | A Failure-Friendly Design Principle for Hash Functions |  |  | read |
| KN-LIT-2040 | A Fast and Key-Efficient Reduction of ChosenCiphertext to Known-Plaintext Security? |  |  | read |
| KN-LIT-2041 | A Fast and Simple Partially Oblivious PRF, with |  |  | read |
| KN-LIT-2042 | A First Approach to Provide Anonymity in Attribute Certificates? |  |  | read |
| KN-LIT-2043 | A First-Order DPA Attack Against AES in Counter Mode with Unknown Initial Counter |  |  | read |
| KN-LIT-2044 | A Formal Study of Power Variability Issues and Side-Channel Attacks for Nanoscale Devices Mathieu Renauld, François-Xavier Standaert |  |  | read |
| KN-LIT-2045 | A Formal Treatment of Backdoored Pseudorandom Generators |  |  | read |
| KN-LIT-2046 | A Formal Treatment of Multi-key Channels |  |  | read |
| KN-LIT-2047 | A Formal Treatment of Onion Routing |  |  | read |
| KN-LIT-2048 | A formula for disaster: a unified approach to elliptic curve special-point-based attacks |  |  | read |
| KN-LIT-2049 | A Formula for The Selmer Group of a Rational Three-Isogeny Matt DeLong |  |  | read |
| KN-LIT-2050 | A Forward-Secure Public-Key Encryption Scheme |  |  | read |
| KN-LIT-2051 | A Framework and Compact Constructions for Non-monotonic Attribute-Based Encryption Shota Yamada?1 |  |  | read |
| KN-LIT-2052 | A Framework for Achieving KDM-CCA Secure Public-Key Encryption |  |  | read |
| KN-LIT-2053 | A Framework for Automated Independent-Biclique Cryptanalysis |  |  | read |
| KN-LIT-2054 | A Framework for Efficient and Composable Oblivious Transfer |  |  | read |
| KN-LIT-2055 | A Framework for Identity-Based Encryption with Almost Tight Security |  |  | read |
| KN-LIT-2056 | A Framework for Practical Anonymous Credentials from Lattices |  |  | read |
| KN-LIT-2057 | A Framework for Practical Universally Composable Zero-Knowledge Protocols? |  |  | read |
| KN-LIT-2058 | A Framework for Statistically Sender Private OT with Optimal Rate |  |  | read |
| KN-LIT-2059 | A Framework for Universally Composable Non-Committing Blind Signatures |  |  | read |
| KN-LIT-2060 | A Full Characterization of Completeness for Two-party Randomized Function Evaluation |  |  | read |
| KN-LIT-2061 | A General Polynomial Selection Method and New Asymptotic Complexities for the Tower Number Field Sieve Algorithm |  |  | read |
| KN-LIT-2062 | A generalization of DDH with applications to |  |  | read |
| KN-LIT-2063 | A Generalized Birthday Problem |  |  | read |
| KN-LIT-2064 | A Generalized Method of Differential Fault Attack Against AES Cryptosystem |  |  | read |
| KN-LIT-2065 | A Generalized Wiener Attack on RSA |  |  | read |
| KN-LIT-2066 | A Generic Approach to Invariant Subspace Attacks: Cryptanalysis of Robin, iSCREAM and Zorro |  |  | read |
| KN-LIT-2067 | A Generic Construction of an Anonymous Reputation System and Instantiations from Lattices |  |  | read |
| KN-LIT-2068 | A Generic Construction of Tightly Secure Password-based Authenticated Key Exchange |  |  | read |
| KN-LIT-2069 | A Generic Scheme Based on Trapdoor One-Way Permutations with Signatures as Short as Possible |  |  | read |
| KN-LIT-2070 | A Generic Transform from Multi-Round Interactive Proof to NIZK |  |  | read |
| KN-LIT-2071 | A Geometric Approach to Homomorphic Secret Sharing |  |  | read |
| KN-LIT-2072 | A Geometric Approach to Linear Cryptanalysis |  |  | read |
| KN-LIT-2073 | A Graduate Course in Applied Cryptography |  |  | read |
| KN-LIT-2074 | A Greater GIFT: Strengthening GIFT against Statistical Cryptanalysis |  |  | read |
| KN-LIT-2075 | A Group Signature Scheme from Lattice Assumptions |  |  | read |
| KN-LIT-2076 | A Hardcore Lemma for Computational Indistinguishability: Security Amplification for Arbitrarily Weak PRGs with Optimal Stretch |  |  | read |
| KN-LIT-2077 | A heuristic for finding compatible differential paths with application to HAS-160 |  |  | read |
| KN-LIT-2078 | A heuristic quasi-polynomial algorithm for discrete logarithm in finite fields of small characteristic |  |  | read |
| KN-LIT-2079 | A Heuristic Subexponential |  |  | read |
| KN-LIT-2080 | A HEURISTIC SUBEXPONENTIAL ALGORITHM TO FIND PATHS IN MARKOFF GRAPHS OVER FINITE FIELDS JOSEPH H. SILVERMAN |  |  | read |
| KN-LIT-2081 | A high speed coprocessor for elliptic curve scalar multiplications over Fp |  |  | read |
| KN-LIT-2082 | A High Throughput/Gate AES Hardware |  |  | read |
| KN-LIT-2083 | A Holistic Approach Towards Side-Channel Secure Fixed-Weight Polynomial Sampling |  |  | read |
| KN-LIT-2084 | A hybrid lattice-reduction and meet-in-the-middle attack against NTRU |  |  | read |
| KN-LIT-2085 | A Key Recovery Attack on MDPC with CCA Security Using Decoding Errors |  |  | read |
| KN-LIT-2086 | A Key-Recovery Attack against Mitaka in the t-Probing Model |  |  | read |
| KN-LIT-2087 | A Key-recovery Attack on 855-round Trivium |  |  | read |
| KN-LIT-2088 | A key-recovery timing attack on post-quantum primitives using the Fujisaki-Okamoto transformation and its application on FrodoKEM |  |  | read |
| KN-LIT-2089 | A kilobit hidden SNFS discrete logarithm computation |  |  | read |
| KN-LIT-2090 | A kilobit special number field sieve factorization |  |  | read |
| KN-LIT-2091 | A larger Class of Cryptographic Boolean Functions via a Study of the Maiorana-McFarland Construction Claude Carlet |  |  | read |
| KN-LIT-2092 | A Lattice Based Public Key Cryptosystem Using Polynomial Representations |  |  | read |
| KN-LIT-2093 | A Leakage-Resilient Mode of Operation Krzysztof Pietrzak |  |  | read |
| KN-LIT-2094 | A Lightweight Concurrent Fault Detection Scheme for the AES S-boxes Using Normal Basis |  |  | read |
| KN-LIT-2095 | A Lightweight Identification Protocol Based on Lattices |  |  | read |
| KN-LIT-2096 | A Linear Lower Bound on the Communication Complexity of Single-Server Private Information Retrieval? |  |  | read |
| KN-LIT-2097 | A Linked-List Approach to Cryptographically Secure Elections Using Instant Runoff Voting |  |  | read |
| KN-LIT-2098 | A Little Honesty Goes a Long Way: The Two-Tier |  |  | read |
| KN-LIT-2099 | A Logarithmic Lower Bound for Oblivious RAM (for all parameters)? |  |  | read |
| KN-LIT-2100 | A Low-Cost ECC Coprocessor for Smartcards |  |  | read |
| KN-LIT-2101 | A low-resource quantum factoring algorithm |  |  | read |
| KN-LIT-2102 | A Lower Bound for One-Round Oblivious RAM |  |  | read |
| KN-LIT-2103 | A Lower Bound for Proving Hardness of Learning with Rounding with Polynomial Modulus? |  |  | read |
| KN-LIT-2104 | A Lower Bound on the Length of Signatures Based on Group Actions and Generic Isogenies |  |  | read |
| KN-LIT-2105 | A MAC forgery attack on SOBER-128 |  |  | read |
| KN-LIT-2106 | A MAC Mode for Lightweight Block Ciphers |  |  | read |
| KN-LIT-2107 | A Map of Witness Maps: |  |  | read |
| KN-LIT-2108 | A masked ring-LWE implementation |  |  | read |
| KN-LIT-2109 | A Meet-in-the-Middle Attack on 8-Round AES |  |  | read |
| KN-LIT-2110 | A Message Authentication Code Based on Unimodular Matrix Groups |  |  | read |
| KN-LIT-2111 | A Method for Making Password-Based Key Exchange Resilient to Server Compromise? |  |  | read |
| KN-LIT-2112 | A Methodology for Differential-Linear |  |  | read |
| KN-LIT-2113 | A Mix-Net From Any CCA2 Secure Cryptosystem |  |  | read |
| KN-LIT-2114 | A Model for Structure Attacks, with |  |  | read |
| KN-LIT-2115 | A Modular Approach to the Incompressibility of Block-Cipher-Based AEADs |  |  | read |
| KN-LIT-2116 | A Modular Approach to the Security Analysis of Two-Permutation Constructions Yu Long Chen imec-COSIC, KU Leuven, Belgium |  |  | read |
| KN-LIT-2117 | A Modular Framework for Building Variable-Input-Length Tweakable Ciphers |  |  | read |
| KN-LIT-2118 | A Modular Security Analysis of the TLS Handshake Protocol |  |  | read |
| KN-LIT-2119 | A Modular Treatment of Blind Signatures from Identification Schemes |  |  | read |
| KN-LIT-2120 | A Modular Treatment of Cryptographic APIs: The Symmetric-Key Case |  |  | read |
| KN-LIT-2121 | A More Cautious Approach to Security Against Mass Surveillance |  |  | read |
| KN-LIT-2122 | A More Complete Analysis of the Signal Double Ratchet Algorithm? |  |  | read |
| KN-LIT-2123 | A Near-Practical Attack against B mode of HBB |  |  | read |
| KN-LIT-2124 | A New Algebraic Approach to the Regular |  |  | read |
| KN-LIT-2125 | A New Algorithm for the Unbalanced Meet-in-the-Middle Problem |  |  | read |
| KN-LIT-2126 | A New and Improved Paradigm for Hybrid Encryption Secure Against Chosen-Ciphertext Attack |  |  | read |
| KN-LIT-2127 | A new approach based on quadratic forms to attack the McEliece cryptosystem ‹ |  |  | read |
| KN-LIT-2128 | A New Approach to Black-Box Concurrent Secure Computation |  |  | read |
| KN-LIT-2129 | A New Approach to Efficient Non-Malleable Zero-Knowledge? |  |  | read |
| KN-LIT-2130 | A New Approach to Round-Optimal Secure Multiparty Computation |  |  | read |
| KN-LIT-2131 | A New Attack Against Khazad Frédéric Muller |  |  | read |
| KN-LIT-2132 | A New Attack on 6-Round IDEA |  |  | read |
| KN-LIT-2133 | A New Attack on the LEX Stream Cipher |  |  | read |
| KN-LIT-2134 | A New Attack with Side Channel Leakage during Exponent Recoding Computations |  |  | read |
| KN-LIT-2135 | A New Baby-Step Giant-Step Algorithm and Some Applications to Cryptanalysis |  |  | read |
| KN-LIT-2136 | A New Bit-Serial Architecture for Field |  |  | read |
| KN-LIT-2137 | A New Class of Collision Attacks and its Application to DES |  |  | read |
| KN-LIT-2138 | A New Class of Weak Keys for Blowfish |  |  | read |
| KN-LIT-2139 | A New Classification of 4-bit Optimal S-boxes and its |  |  | read |
| KN-LIT-2140 | A new criterion for avoiding the propagation of linear relations through an Sbox? |  |  | read |
| KN-LIT-2141 | A New Decryption Failure Attack against HQC |  |  | read |
| KN-LIT-2142 | A New Dedicated 256-bit Hash Function: FORK-256 |  |  | read |
| KN-LIT-2143 | A New Distinguisher for Clock Controlled Stream Ciphers |  |  | read |
| KN-LIT-2144 | A New Distribution-Sensitive Secure |  |  | read |
| KN-LIT-2145 | A New Formulation of the Linear Equivalence |  |  | read |
| KN-LIT-2146 | A New Framework for Constraint-Based Probabilistic Template Side Channel Attacks |  |  | read |
| KN-LIT-2147 | A New Framework For More Efficient Round-Optimal Lattice-Based (Partially) Blind Signature via Trapdoor Sampling |  |  | read |
| KN-LIT-2148 | A New Framework for Quantum Oblivious Transfer |  |  | read |
| KN-LIT-2149 | A New Keystream Generator MUGI Dai Watanabe1 , Soichi Furuya1 , Hirotaka Yoshida1 |  |  | read |
| KN-LIT-2150 | A new lattice construction for partial key exposure attack for RSA |  |  | read |
| KN-LIT-2151 | A new MAC Construction Alred and a Specific Instance Alpha-MAC |  |  | read |
| KN-LIT-2152 | A New Mode of Operation for |  |  | read |
| KN-LIT-2153 | A New Model for Error-Tolerant Side-Channel Cube Attacks |  |  | read |
| KN-LIT-2154 | A New Paradigm for Public-Key Functional Encryption for Degree-2 Polynomials Romain Gay? |  |  | read |
| KN-LIT-2155 | A New Paradigm of Hybrid Encryption Scheme |  |  | read |
| KN-LIT-2156 | A New Public-Key Cryptosystem via Mersenne Numbers |  |  | read |
| KN-LIT-2157 | A New Randomness Extraction Paradigm for Hybrid Encryption |  |  | read |
| KN-LIT-2158 | A New Related Message Attack on RSA |  |  | read |
| KN-LIT-2159 | A New Security Notion for PKC in the Standard Model: Weaker, Simpler, and Still Realizing Secure Channels |  |  | read |
| KN-LIT-2160 | A New Side-Channel Attack on RSA Prime Generation |  |  | read |
| KN-LIT-2161 | A New Simple Technique to Bootstrap Various |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2162 | A New Structural-Differential Property of 5-Round AES |  |  | read |
| KN-LIT-2163 | A New Variant of PMAC: Beyond the Birthday Bound |  |  | read |
| KN-LIT-2164 | A New Variant of Unbalanced Oil and Vinegar Using Quotient Ring: QR-UOV |  |  | read |
| KN-LIT-2165 | A Non-Interactive Shuffle with Pairing Based Verifiability? |  |  | read |
| KN-LIT-2166 | A non-PCP Approach to Succinct Quantum-Safe Zero-Knowledge ? |  |  | read |
| KN-LIT-2167 | A Nonuniform Algorithm for the Hidden Number Problem in Subgroups |  |  | read |
| KN-LIT-2168 | A Note on Non-Interactive Zero-Knowledge from CDH |  |  | read |
| KN-LIT-2169 | A Note on Perfect Correctness by Derandomization? |  |  | read |
| KN-LIT-2170 | A Note on the Communication Complexity of Multiparty Computation in the Correlated |  |  | read |
| KN-LIT-2171 | A Note on the Post-Quantum Security of (Ring) Signatures |  |  | read |
| KN-LIT-2172 | A Novel CCA Attack using Decryption Errors against LAC |  |  | read |
| KN-LIT-2173 | A Novel Completeness Test for Leakage Models and its Application to Side Channel Attacks and Responsibly Engineered Simulators |  |  | read |
| KN-LIT-2174 | A One-Pass Mode of Operation for Deterministic Message Authentication— Security beyond the Birthday Barrier |  |  | read |
| KN-LIT-2175 | A one-time single-bit fault leaks all previous NTRU-HRSS session keys to a chosen-ciphertext attack |  |  | read |
| KN-LIT-2176 | A Parallel Repetition Theorem for Leakage Resilience |  |  | read |
| KN-LIT-2177 | A Parameterized Splitting System and its Application to the Discrete Logarithm Problem with Low Hamming Weight Product Exponents |  |  | read |
| KN-LIT-2178 | A PCP Theorem for Interactive Proofs and Applications |  |  | read |
| KN-LIT-2179 | A Physical Approach for Stochastic Modeling of TERO-based TRNG |  |  | read |
| KN-LIT-2180 | A point compression method for elliptic curves defined over GF (2n ) |  |  | read |
| KN-LIT-2181 | A Polynomial Time Algorithm for the Braid Diffie-Hellman Conjugacy Problem |  |  | read |
| KN-LIT-2182 | A polynomial time attack on instances of M-SIDH and FESTA |  |  | read |
| KN-LIT-2183 | A Polynomial Time Attack on RSA with Private CRT-Exponents Smaller Than N 0.073 |  |  | read |
| KN-LIT-2184 | A Polynomial-Time Algorithm for Solving the Hidden Subset Sum Problem |  |  | read |
| KN-LIT-2185 | A Polynomial-Time Attack on the BBCRS Scheme |  |  | read |
| KN-LIT-2186 | A Polynomial-Time Key-Recovery Attack on MQQ Cryptosystems |  |  | read |
| KN-LIT-2187 | A practical attack on a braid group based cryptographic protocol |  |  | read |
| KN-LIT-2188 | A Practical Attack on KeeLoq |  |  | read |
| KN-LIT-2189 | A Practical Attack on Some Braid Group Based Cryptographic Primitives |  |  | read |
| KN-LIT-2190 | A Practical Attack on the Fixed RC4 in the WEP Mode |  |  | read |
| KN-LIT-2191 | A Practical Cryptanalysis of the Algebraic Eraser |  |  | read |
| KN-LIT-2192 | A Practical Cryptanalysis of WalnutDSATM Daniel Hart1 , DoHoon Kim1 , Giacomo Micheli1 , Guillermo Pascual Perez1 |  |  | read |
| KN-LIT-2193 | A Practical Key Recovery Attack on Basic TCHo ? |  |  | read |
| KN-LIT-2194 | A Practical Public Key Cryptosystem from Paillier and Rabin Schemes |  |  | read |
| KN-LIT-2195 | A Practical-Time Related-Key Attack on the |  |  | read |
| KN-LIT-2196 | A Practice-Oriented Treatment of Pseudorandom Number Generators |  |  | read |
| KN-LIT-2197 | A preliminary version of this paper appears in Proceedings of the 13th Annual Conference on Computer and Communications Security, ACM, 2006. This is the full version |  |  | read |
| KN-LIT-2198 | A preliminary version of this paper appears in the proceedings of Eurocrypt 2016. This is the full version |  |  | read |
| KN-LIT-2199 | A preliminary version of this paper appears in the proceedings of the USENIX Security Symposium 2013. This is the full version. On the Security of RC4 in TLS and WPA |  |  | read |
| KN-LIT-2200 | A Profitable Sub-Prime Loan: Obtaining the Advantages of Composite Order in Prime-Order Bilinear Groups |  |  | read |
| KN-LIT-2201 | A Proposal for an ISO Standard for Public Key Encryption (version 2.0) |  |  | read |
| KN-LIT-2202 | A proposition for Correlation Power Analysis enhancement |  |  | read |
| KN-LIT-2203 | A Provable-Security Analysis of Intel’s Secure Key RNG |  |  | read |
| KN-LIT-2204 | A Provable-Security Treatment of the Key-Wrap Problem |  |  | read |
| KN-LIT-2205 | A Provably Secure Group Signature Scheme from Code-Based Assumptions Martianus Frederic Ezerman, Hyung Tae Lee, San Ling |  |  | read |
| KN-LIT-2206 | A Public Key Encryption Scheme Based on the Polynomial Reconstruction Problem |  |  | read |
| KN-LIT-2207 | A public key encryption scheme secure against |  |  | read |
| KN-LIT-2208 | A public key encryption scheme secure against key dependent |  |  | read |
| KN-LIT-2209 | A Punctured Programming Approach to Adaptively Secure Functional Encryption |  |  | read |
| KN-LIT-2210 | A Quantum Cipher with Near Optimal Key-Recycling |  |  | read |
| KN-LIT-2211 | A Quantum-Proof Non-Malleable Extractor With Application to Privacy Amplification against Active Quantum Adversaries |  |  | read |
| KN-LIT-2212 | A Rate-Optimizing Compiler for Non-malleable |  |  | read |
| KN-LIT-2213 | A Rational Protocol Treatment of 51% |  |  | read |
| KN-LIT-2214 | A Realizable Special Hardware Sieving Device for Factoring 1024-bit |  |  | read |
| KN-LIT-2215 | A Refined Hardness Estimation of LWE in Two-step Mode |  |  | read |
| KN-LIT-2216 | A Refined Power-Analysis Attack on Elliptic Curve Cryptosystems Louis Goubin |  |  | read |
| KN-LIT-2217 | A Scalable Password-based Group Key Exchange Protocol in the Standard Model |  |  | read |
| KN-LIT-2218 | A Secret-Sharing Based MPC Protocol for Boolean Circuits with Good Amortized Complexity |  |  | read |
| KN-LIT-2219 | A SECURE PUBLIC-KEY SIGNATURE SYSTEM WITH EXTREMELY FAST VERIFICATION |  |  | read |
| KN-LIT-2220 | A Secure Signature Scheme from Bilinear Maps |  |  | read |
| KN-LIT-2221 | A Security Analysis of the NIST SP 800-90 Elliptic Curve Random Number Generator |  |  | read |
| KN-LIT-2222 | A Sender Verifiable Mix-Net and a New Proof of a Shuffle |  |  | read |
| KN-LIT-2223 | A short-list of pairing-friendly curves resistant to Special TNFS at the 128-bit security level |  |  | read |
| KN-LIT-2224 | A Shuffle Argument Secure in the Generic Model |  |  | read |
| KN-LIT-2225 | A Side-Channel Analysis Resistant Description of the AES S-box ? |  |  | read |
| KN-LIT-2226 | A Side-Channel Assisted Cryptanalytic Attack Against QcBits |  |  | read |
| KN-LIT-2227 | A Signature Scheme as Secure as the Diffie-Hellman Problem |  |  | read |
| KN-LIT-2228 | A simple and compact algorithm for SIDH with arbitrary degree isogenies |  |  | read |
| KN-LIT-2229 | A Simple and Efficient Framework of Proof Systems for NP |  |  | read |
| KN-LIT-2230 | A Simple BGN-type Cryptosystem from LWE |  |  | read |
| KN-LIT-2231 | A Simple Construction of iO for Turing Machines? |  |  | read |
| KN-LIT-2232 | A Simple Obfuscation Scheme for Pattern-Matching with Wildcards |  |  | read |
| KN-LIT-2233 | A Simple Public-Key Cryptosystem with a |  |  | read |
| KN-LIT-2234 | A Simple Threshold Authenticated Key Exchange from Short Secrets |  |  | read |
| KN-LIT-2235 | A Simple Variant of the Merkle-Damgård Scheme with a Permutation |  |  | read |
| KN-LIT-2236 | A Simpler and More Efficient Reduction of DLog to CDH for Abelian Group Actions |  |  | read |
| KN-LIT-2237 | A Simpler Construction of CCA2-Secure Public-Key Encryption Under General Assumptions |  |  | read |
| KN-LIT-2238 | A Simpler Variant of Universally Composable Security for Standard Multiparty Computation? |  |  | read |
| KN-LIT-2239 | A Simplified Representation of AES |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2240 | A Single-Key Attack on the Full GOST Block Cipher |  |  | read |
| KN-LIT-2241 | A Statistical Model for Higher Order DPA on Masked Devices |  |  | read |
| KN-LIT-2242 | A Statistically-Hiding Integer Commitment Scheme based on Groups with Hidden Order |  |  | read |
| KN-LIT-2243 | A Stochastic Model for Differential Side Channel Cryptanalysis |  |  | read |
| KN-LIT-2244 | A Strategy for Finding Roots of Multivariate Polynomials with New Applications in Attacking RSA Variants |  |  | read |
| KN-LIT-2245 | A Study of Pair Encodings: Predicate Encryption in Prime Order Groups |  |  | read |
| KN-LIT-2246 | A Study of the MD5 Attacks: Insights and Improvements |  |  | read |
| KN-LIT-2247 | A Subversion-Resistant SNARK |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2248 | A Survey of Single-Database PIR: Techniques and Applications |  |  | read |
| KN-LIT-2249 | A Synthetic Indifferentiability Analysis of Interleaved Double-Key Even-Mansour Ciphers |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2250 | A Systematic Approach and Analysis of Key Mismatch Attacks on Lattice-Based NIST |  |  | read |
| KN-LIT-2251 | A Systematic Approach to the Side-Channel Analysis of ECC Implementations with Worst-Case Horizontal Attacks |  |  | read |
| KN-LIT-2252 | A Tale of Two Shares: Why Two-Share Threshold Implementation Seems Worthwhile—and Why it is Not |  |  | read |
| KN-LIT-2253 | A Tamper and Leakage Resilient von Neumann Architecture |  |  | read |
| KN-LIT-2254 | A Theoretical Treatment of Related-Key Attacks: |  |  | read |
| KN-LIT-2255 | A Theory of Composition for Differential Obliviousness |  |  | read |
| KN-LIT-2256 | A Third is All You Need: Extended Partial Key Exposure Attack on CRT-RSA with Additive Exponent Blinding |  |  | read |
| KN-LIT-2257 | A Thorough Treatment of Highly-Efficient NTRU Instantiations Julien Duman[0000−0002−5195−1290]1 , Kathrin Hövelmanns[0000−0002−5478−0140]2 |  |  | read |
| KN-LIT-2258 | A Threshold Pseudorandom Function |  |  | read |
| KN-LIT-2259 | A Tight Computational Indistinguishability Bound of Product Distributions |  |  | read |
| KN-LIT-2260 | A Tight High-Order Entropic Quantum |  |  | read |
| KN-LIT-2261 | A Tool Kit for Finding Small Roots of Bivariate Polynomials over the Integers |  |  | read |
| KN-LIT-2262 | A Toolbox for Barriers on Interactive Oracle Proofs |  |  | read |
| KN-LIT-2263 | A Toolbox for Cryptanalysis: Linear and Affine Equivalence Algorithms? |  |  | read |
| KN-LIT-2264 | A Toolkit for Ring-LWE Cryptography |  |  | read |
| KN-LIT-2265 | A Traceable Block Cipher |  |  | read |
| KN-LIT-2266 | A Transform for NIZK Almost as Efficient and General as the Fiat-Shamir Transform Without Programmable Random Oracles |  |  | read |
| KN-LIT-2267 | A Tutorial on High Performance Computing applied to Cryptanalysis |  |  | read |
| KN-LIT-2268 | A Tweakable Enciphering Mode |  |  | read |
| KN-LIT-2269 | A Twist on the Naor-Yung Paradigm and Its Application to E cient CCA-Secure Encryption from Hard Search Problems |  |  | read |
| KN-LIT-2270 | A Unified and Composable Take on Ratcheting |  |  | read |
| KN-LIT-2271 | A Unified Approach to MPC with Preprocessing using OT |  |  | read |
| KN-LIT-2272 | A Unified Framework for Non-Universal SNARKs Helger Lipmaa |  |  | read |
| KN-LIT-2273 | A Unified Framework for the Analysis of Side-Channel Key Recovery Attacks |  |  | read |
| KN-LIT-2274 | A Unified Framework for Trapdoor-Permutation-Based Sequential Aggregate Signatures |  |  | read |
| KN-LIT-2275 | A Unified Metric for Quantifying Information Leakage of Cryptographic Devices under Power Analysis Attacks |  |  | read |
| KN-LIT-2276 | A Uniform Min-Max Theorem with Applications in Cryptography |  |  | read |
| KN-LIT-2277 | A Universally Composable Framework for the Privacy of Email Ecosystems |  |  | read |
| KN-LIT-2278 | A Universally Composable PAKE with Zero Communication Cost (And Why It Shouldn’t Be Considered UC-Secure) |  |  | read |
| KN-LIT-2279 | A Unified Approach to Related-Key Attacks |  |  | read |
| KN-LIT-2280 | A Variant of the Cramer-Shoup Cryptosystem for Groups of Unknown Order |  |  | read |
| KN-LIT-2281 | A Verifiable Random Function |  |  | read |
| KN-LIT-2282 | A Verifiable Secret Shuffle of Homomorphic Encryptions |  |  | read |
| KN-LIT-2283 | A Very Compact Hardware Implementation of the MISTY1 Block Cipher |  |  | read |
| KN-LIT-2284 | A Very Compact S-box for AES |  |  | read |
| KN-LIT-2285 | A Very High Speed True Random Number Generator with Entropy Assessment |  |  | read |
| KN-LIT-2286 | A Weakness in Some Oblivious Transfer and Zero-Knowledge Protocols |  |  | read |
| KN-LIT-2287 | A Weakness of the Linear Part of Stream Cipher MUGI |  |  | read |
| KN-LIT-2288 | A Zero-Dimensional Gröbner Basis for AES-128 |  |  | read |
| KN-LIT-2289 | A Zero-One Law for Cryptographic Complexity with respect to Computational UC Security? |  |  | read |
| KN-LIT-2290 | ABE for Circuits with Constant-Size Secret Keys and Adaptive Security |  |  | read |
| KN-LIT-2291 | ABE for DFA from k-Lin |  |  | read |
| KN-LIT-2292 | ABE for DFA from LWE against Bounded Collusions, Revisited Hoeteck Wee |  |  | read |
| KN-LIT-2293 | ABE with Tag Made Easy |  |  | read |
| KN-LIT-2294 | ABELIAN VARIETIES OVER Q AND MODULAR FORMS |  |  | read |
| KN-LIT-2295 | Abelian Varieties with Few Isogenies and Cryptography |  |  | read |
| KN-LIT-2296 | able Decentralized Multi-Client Functional Encryption for Inner Product Phan |  |  | read |
| KN-LIT-2297 | ably-Extractable |  |  | read |
| KN-LIT-2298 | Abstraction in Cryptography |  |  | read |
| KN-LIT-2299 | Accelerating AES with Vector Permute Instructions |  |  | read |
| KN-LIT-2300 | Accelerating HE Operations from Key Decomposition Technique |  |  | read |
| KN-LIT-2301 | Accelerating Homomorphic Evaluation on Reconfigurable Hardware |  |  | read |
| KN-LIT-2302 | Accelerating LTV Based Homomorphic Encryption in Reconfigurable Hardware |  |  | read |
| KN-LIT-2303 | Accelerating the Delfs–Galbraith algorithm with fast subfield root detection |  |  | read |
| KN-LIT-2304 | Accelerating the Whirlpool Hash Function using |  |  | read |
| KN-LIT-2305 | Access Control Encryption for Equality, Comparison, and More |  |  | read |
| KN-LIT-2306 | Accumulating Composites and Improved Group Signing |  |  | read |
| KN-LIT-2307 | Accumulators in (and Beyond) Generic Groups: Non-Trivial Batch Verification Requires Interaction |  |  | read |
| KN-LIT-2308 | Achievable CCA2 Relaxation for Homomorphic Encryption |  |  | read |
| KN-LIT-2309 | Achieving Constant Round Leakage-Resilient Zero-Knowledge? |  |  | read |
| KN-LIT-2310 | Achieving Leakage Resilience Through Dual System Encryption |  |  | read |
| KN-LIT-2311 | Achieving privacy in verifiable computation with multiple servers – without FHE and without pre-processing? |  |  | read |
| KN-LIT-2312 | Achieving the limits of the noisy-storage model using entanglement sampling Frédéric |  |  | read |
| KN-LIT-2313 | Actively Secure Arithmetic Computation and VOLE with Constant Computational Overhead |  |  | read |
| KN-LIT-2314 | Actively Secure Half-Gates with Minimum Overhead under Duplex Networks Hongrui Cui1[0000−0002−6203−413X] , Xiao Wang2[0000−0002−5991−7417] |  |  | read |
| KN-LIT-2315 | Actively Secure OT Extension with Optimal Overhead |  |  | read |
| KN-LIT-2316 | Actively Secure Private Function Evaluation |  |  | read |
| KN-LIT-2317 | Actively Secure Two-Party Evaluation of any Quantum Operation Frédéric Dupuis1? |  |  | read |
| KN-LIT-2318 | Acyclicity Programming for Sigma-Protocols |  |  | read |
| KN-LIT-2319 | Ad Hoc PSM Protocols: Secure Computation Without Coordination |  |  | read |
| KN-LIT-2320 | Adapting Density Attacks to Low-Weight Knapsacks |  |  | read |
| KN-LIT-2321 | Adapting the Weaknesses of the Random Oracle Model to the Generic Group Model |  |  | read |
| KN-LIT-2322 | Adaptive and Concurrent Secure Computation from New Adaptive, Non-Malleable Commitments |  |  | read |
| KN-LIT-2323 | Adaptive Distributional Security for Garbling Schemes with O(\|x\|) Online Complexity Estuardo Alpı́rez Bock1[0000−0002−8410−5488] |  |  | read |
| KN-LIT-2324 | Adaptive Extractors and their Application to Leakage Resilient Secret Sharing |  |  | read |
| KN-LIT-2325 | Adaptive Garbled RAM from Laconic Oblivious Transfer |  |  | read |
| KN-LIT-2326 | Adaptive Multiparty NIKE |  |  | read |
| KN-LIT-2327 | Adaptive Oblivious Transfer and Generalization |  |  | read |
| KN-LIT-2328 | Adaptive Oblivious Transfer with Access Control from Lattice Assumptions |  |  | read |
| KN-LIT-2329 | Adaptive One-way Functions and Applications |  |  | read |
| KN-LIT-2330 | Adaptive partitioning |  |  | read |
| KN-LIT-2331 | Adaptive Security in the Threshold Setting: From Cryptosystems to Signature Schemes |  |  | read |
| KN-LIT-2332 | Adaptive Security of Multi-Party Protocols, Revisited |  |  | read |
| KN-LIT-2333 | Adaptive Security via Deletion in Attribute-Based Encryption: Solutions from Search Assumptions in Bilinear Groups |  |  | read |
| KN-LIT-2334 | Adaptive Security with Quasi-Optimal Rate |  |  | read |
| KN-LIT-2335 | Adaptive Simulation Security for Inner Product Functional Encryption |  |  | read |
| KN-LIT-2336 | Adaptive Succinct Garbled RAM or: How To Delegate Your Database? |  |  | read |
| KN-LIT-2337 | Adaptive Trapdoor Functions and Chosen-Ciphertext Security |  |  | read |
| KN-LIT-2338 | Adaptive Versus Non-Adaptive Strategies in the Quantum Setting with Applications |  |  | read |
| KN-LIT-2339 | Adaptive versus Static Multi-oracle Algorithms, and Quantum Security of a Split-key PRF |  |  | read |
| KN-LIT-2340 | Adaptive Witness Encryption and Asymmetric Password-based Cryptography |  |  | read |
| KN-LIT-2341 | Adaptive Zero-Knowledge Proofs and Adaptively Secure Oblivious Transfer |  |  | read |
| KN-LIT-2342 | Adaptively Secure ABE for DFA from k-Lin and More |  |  | read |
| KN-LIT-2343 | Adaptively Secure and Succinct Functional Encryption: Improving Security and Efficiency, Simultaneously |  |  | read |
| KN-LIT-2344 | Adaptively Secure Broadcast |  |  | read |
| KN-LIT-2345 | Adaptively Secure Computation for RAM Programs |  |  | read |
| KN-LIT-2346 | Adaptively Secure Constrained Pseudorandom Functions in the Standard Model |  |  | read |
| KN-LIT-2347 | Adaptively Secure Garbled Circuits from One-Way Functions Brett Hemenway1 , Zahra Jafargholi2 , Rafail Ostrovsky3,? |  |  | read |
| KN-LIT-2348 | Adaptively Secure Garbling Schemes for Parallel Computations |  |  | read |
| KN-LIT-2349 | Adaptively Secure Garbling with Applications to |  |  | read |
| KN-LIT-2350 | Adaptively Secure Garbling with Near Optimal Online Complexity? |  |  | read |
| KN-LIT-2351 | Adaptively Secure Identity-Based Encryption from Lattices with Asymptotically Shorter |  |  | read |
| KN-LIT-2352 | Adaptively Secure Inner Product Encryption from LWE |  |  | read |
| KN-LIT-2353 | Adaptively Secure MPC with Sublinear Communication Complexity |  |  | read |
| KN-LIT-2354 | Adaptively Secure Multi-Party Computation from LWE (via Equivocal FHE)? |  |  | read |
| KN-LIT-2355 | Adaptively Secure Multi-Party Computation with Dishonest Majority |  |  | read |
| KN-LIT-2356 | Adaptively Secure Proxy Re-encryption |  |  | read |
| KN-LIT-2357 | Adaptively Secure Puncturable Pseudorandom Functions in the Standard Model |  |  | read |
| KN-LIT-2358 | Adaptively Secure, Universally Composable, Multiparty Computation in Constant Rounds |  |  | read |
| KN-LIT-2359 | Adaptively Simulation-Secure Attribute-Hiding Predicate Encryption |  |  | read |
| KN-LIT-236 | Elliptic Curves | 2008 |  | read |
| KN-LIT-2360 | Adaptively Single-key Secure Constrained PRFs for NC1 |  |  | read |
| KN-LIT-2361 | Additive Randomized Encodings and Their Applications |  |  | read |
| KN-LIT-2362 | Additive-Homomorphic Functional Commitments and Applications to Homomorphic Signatures |  |  | read |
| KN-LIT-2363 | Additively Homomorphic Encryption with d-Operand Multiplications |  |  | read |
| KN-LIT-2364 | Additively Homomorphic IBE from Higher Residuosity |  |  | read |
| KN-LIT-2365 | Additively Homomorphic UC Commitments with Optimal Amortized Overhead Ignacio Cascudo, Ivan Damgård, Bernardo David, Irene Giacomelli |  |  | read |
| KN-LIT-2366 | Advanced Lattice Sieving on GPUs, with Tensor Cores |  |  | read |
| KN-LIT-2367 | Advanced Meet-in-the-Middle Preimage Attacks: First Results on Full Tiger, and |  |  | read |
| KN-LIT-2368 | Adversary-dependent Lossy Trapdoor Function from Hardness of Factoring Semi-smooth RSA |  |  | read |
| KN-LIT-2369 | AES and the Wide Trail Design Strategy |  |  | read |
| KN-LIT-2370 | AES Encryption Implementation and Analysis on Commodity Graphics Processing Units |  |  | read |
| KN-LIT-2371 | AES on FPGA from the fastest to the smallest |  |  | read |
| KN-LIT-2372 | After-the-Fact Leakage in Public-Key Encryption |  |  | read |
| KN-LIT-2373 | Aggregatable Distributed Key Generation Kobi Gurkan ? , Philipp Jovanovic ?? , Mary Maller ? ? ? , Sarah Meiklejohn |  |  | read |
| KN-LIT-2374 | Aggregate and Verifiably Encrypted Signatures from Bilinear Maps |  |  | read |
| KN-LIT-2375 | Aggregate Cash Systems: A Cryptographic Investigation of Mimblewimble |  |  | read |
| KN-LIT-2376 | Agile Cryptography: A Universally Composable Approach |  |  | read |
| KN-LIT-2377 | ALBATROSS: publicly AttestabLe BATched Randomness based On Secret Sharing |  |  | read |
| KN-LIT-2378 | ALE: AES-Based Lightweight Authenticated Encryption Andrey Bogdanov1 , Florian Mendel2 , Francesco Regazzoni3,4 |  |  | read |
| KN-LIT-2379 | alg-geom/9712027 |  |  | read |
| KN-LIT-2380 | Algebraic (Trapdoor) One-Way Functions and their Applications |  |  | read |
| KN-LIT-2381 | Algebraic Adversaries in the Universal |  |  | read |
| KN-LIT-2382 | Algebraic and Slide Attacks on KeeLoq |  |  | read |
| KN-LIT-2383 | Algebraic Attack against Variants of McEliece with Goppa Polynomial of a Special Form |  |  | read |
| KN-LIT-2384 | Algebraic Attacks and Decomposition of Boolean Functions |  |  | read |
| KN-LIT-2385 | Algebraic Attacks on Combiners with Memory |  |  | read |
| KN-LIT-2386 | Algebraic Attacks on Rasta and Dasta Using Low-Degree Equations |  |  | read |
| KN-LIT-2387 | Algebraic Attacks on Round-Reduced Rain and Full AIM-III Kaiyi Zhang1[0000−0002−2294−3523] , Qingju Wang2[0000−0003−4565−8394] |  |  | read |
| KN-LIT-2388 | Algebraic Attacks on SOBER-t32 and SOBER-t16 without stuttering |  |  | read |
| KN-LIT-2389 | Algebraic Attacks on Stream Ciphers with Linear Feedback |  |  | read |
| KN-LIT-2390 | Algebraic Attacks on Summation Generators Dong Hoon Lee, Jaeheon Kim, Jin Hong |  |  | read |
| KN-LIT-2391 | Algebraic Attacks over GF (2k ), Application to |  |  | read |
| KN-LIT-2392 | Algebraic Cryptanalysis of 58-round |  |  | read |
| KN-LIT-2393 | Algebraic Cryptanalysis of a Quantum Money Scheme The Noise-Free Case |  |  | read |
| KN-LIT-2394 | Algebraic cryptanalysis of hidden field equation (HFE) cryptosystems using Gröbner bases |  |  | read |
| KN-LIT-2395 | Algebraic Cryptanalysis of McEliece Variants with Compact Keys |  |  | read |
| KN-LIT-2396 | Algebraic Cryptanalysis of STARK-Friendly Designs: Application to MARVELlous and MiMC |  |  | read |
| KN-LIT-2397 | Algebraic Cryptanalysis of the PKC’2009 Algebraic Surface Cryptosystem |  |  | read |
| KN-LIT-2398 | Algebraic Decomposition for Probing Security |  |  | read |
| KN-LIT-2399 | Algebraic Distinguishers: From Discrete Logarithms to Decisional Uber Assumptions |  |  | read |
| KN-LIT-2400 | Algebraic Group Model with Oblivious Sampling |  |  | read |
| KN-LIT-2401 | Algebraic Immunity of S-boxes and Augmented Functions |  |  | read |
| KN-LIT-2402 | Algebraic Meet-in-the-Middle Attack on LowMC |  |  | read |
| KN-LIT-2403 | Algebraic partitioning: |  |  | read |
| KN-LIT-2404 | Algebraic Reductions of Knowledge |  |  | read |
| KN-LIT-2405 | Algebraic Side-Channel Analysis in the Presence of Errors |  |  | read |
| KN-LIT-2406 | Algebraic Side-Channel Attacks Beyond the Hamming Weight Leakage Model |  |  | read |
| KN-LIT-2407 | Algebraic Side-Channel Attacks on the AES: |  |  | read |
| KN-LIT-2408 | Algebraic Techniques for Short(er) Exact Lattice-Based Zero-Knowledge Proofs |  |  | read |
| KN-LIT-2409 | Algebraic Techniques in Differential Cryptanalysis |  |  | read |
| KN-LIT-2410 | Algebraic XOR-RKA-Secure Pseudorandom Functions from Post-Zeroizing Multilinear Maps |  |  | read |
| KN-LIT-2411 | Algebraically Structured LWE, Revisited |  |  | read |
| KN-LIT-2412 | Algorithmic Number Theory MSRI Publications |  |  | read |
| KN-LIT-2413 | Algorithmic Number Theory Symposium XVII, Groningen, July 6-10, 2026 |  |  | read |
| KN-LIT-2414 | Algorithmic Number Theory Symposium XVII, Groningen, July 6-10, 2026 EFFICIENT QUATERNION ALGORITHMS FOR THE DEURING |  |  | read |
| KN-LIT-2415 | Algorithmic Number Theory Symposium XVII, Groningen, July 6-10, 2026 LARGE SMOOTH TWINS FROM SHORT LATTICE VECTORS |  |  | read |
| KN-LIT-2416 | ALGORITHMS FOR p-ADIC HEIGHTS ON HYPERELLIPTIC CURVES OF ARBITRARY REDUCTION |  |  | read |
| KN-LIT-2417 | Algorithms in HElib |  |  | read |
| KN-LIT-2418 | Alibi: A Flaw in Cuckoo-Hashing based |  |  | read |
| KN-LIT-2419 | Alien vs. Quine, The Vanishing Circuit |  |  | read |
| KN-LIT-2420 | All Complete Functionalities are Reversible |  |  | read |
| KN-LIT-2421 | All-But-Many Encryption A New Framework for Fully-Equipped UC Commitments |  |  | read |
| KN-LIT-2422 | All-But-Many Lossy Trapdoor Functions |  |  | read |
| KN-LIT-2423 | All-But-Many Lossy Trapdoor Functions and Selective Opening Chosen-Ciphertext Security from LWE |  |  | read |
| KN-LIT-2424 | All-But-Many Lossy Trapdoor Functions from Lattices and Applications |  |  | read |
| KN-LIT-2425 | Almost Optimal Bounds for Direct Product |  |  | read |
| KN-LIT-2426 | Almost Optimum Secret Sharing Schemes Secure against Cheating for Arbitrary Secret Distribution |  |  | read |
| KN-LIT-2427 | Almost Optimum t-Cheater Identifiable |  |  | read |
| KN-LIT-2428 | Almost Tight Multi-User Security under Adaptive Corruptions & Leakages in the Standard Model |  |  | read |
| KN-LIT-2429 | Almost Tight Multi-User Security under Adaptive Corruptions from LWE in the Standard Model |  |  | read |
| KN-LIT-2430 | Almost Tight Security in Lattices with |  |  | read |
| KN-LIT-2431 | Almost Tightly-Secure Re-Randomizable and Replayable CCA-secure Public Key Encryption |  |  | read |
| KN-LIT-2432 | Almost uniform density of power residues and the provable security of ESIGN |  |  | read |
| KN-LIT-2433 | Almost-everywhere Secure Computation |  |  | read |
| KN-LIT-2434 | Alzette: a 64-bit ARX-box |  |  | read |
| KN-LIT-2436 | Amortization with Fewer Equations for Proving Knowledge of Small Secrets |  |  | read |
| KN-LIT-2437 | Amortized bootstrapping revisited: Simpler, asymptotically-faster, implemented |  |  | read |
| KN-LIT-2438 | Amortized Complexity of Zero-Knowledge |  |  | read |
| KN-LIT-2439 | Amortized Functional Bootstrapping in less than 7ms, with Õ(1) polynomial multiplications |  |  | read |
| KN-LIT-2440 | Amortized NISC over Z2k from RMFE |  |  | read |
| KN-LIT-2441 | Amortizing Garbled Circuits |  |  | read |
| KN-LIT-2442 | Amortizing Randomness Complexity in Private Circuits |  |  | read |
| KN-LIT-2443 | Amortizing Rate-1 OT and Applications to PIR and PSI |  |  | read |
| KN-LIT-2444 | Amplification of Chosen-Ciphertext Security |  |  | read |
| KN-LIT-2445 | Amplified Boomerang Attack Against Reduced-Round SHACAL |  |  | read |
| KN-LIT-2446 | Amplifying Collision Resistance: A Complexity-Theoretic Treatment Ran Canetti1 |  |  | read |
| KN-LIT-2447 | Amplifying Privacy in Privacy Amplification |  |  | read |
| KN-LIT-2448 | Amplifying the Security of Functional Encryption, Unconditionally |  |  | read |
| KN-LIT-2449 | An Accumulator Based on Bilinear Maps and Efficient Revocation for Anonymous Credentials |  |  | read |
| KN-LIT-2450 | An Algebraic Approach to Maliciously Secure Private Set Intersection |  |  | read |
| KN-LIT-2451 | An Algebraic Attack on Ciphers with Low-Degree Round Functions: Application to Full MiMC Maria Eichlseder1( ) |  |  | read |
| KN-LIT-2452 | An Algebraic Attack on Rank Metric Code-Based Cryptosystems |  |  | read |
| KN-LIT-2453 | An Algebraic Formulation of the Division Property: Revisiting Degree Evaluations, Cube |  |  | read |
| KN-LIT-2454 | An Algebraic Framework for Diffie-Hellman Assumptions |  |  | read |
| KN-LIT-2455 | An Algebraic Framework for Pseudorandom Functions and Applications to Related-Key Security |  |  | read |
| KN-LIT-2456 | An Algebraic Framework for Silent Preprocessing with Trustless Setup and Active Security |  |  | read |
| KN-LIT-2457 | An Algebraic Framework for Universal and Updatable SNARKs |  |  | read |
| KN-LIT-2458 | An algorithm for efficient detection of (N, N )-splittings and its application to the isogeny problem in dimension |  |  | read |
| KN-LIT-2459 | An Algorithm to Solve the Discrete Logarithm Problem with the Number Field Sieve |  |  | read |
| KN-LIT-2460 | An Alternative Approach for SIDH Arithmetic |  |  | read |
| KN-LIT-2461 | An Alternative Approach to Non-black-box Simulation in Fully Concurrent Setting |  |  | read |
| KN-LIT-2462 | An Analysis of NIST SP 800-90A |  |  | read |
| KN-LIT-2463 | An Analysis of OpenSSL’s Random Number Generator |  |  | read |
| KN-LIT-2464 | An Analysis of the Algebraic Group Model? |  |  | read |
| KN-LIT-2465 | An analysis of the vector decomposition problem |  |  | read |
| KN-LIT-2466 | An Analysis of the XSL Algorithm |  |  | read |
| KN-LIT-2467 | An Analysis of XSL Applied to BES |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2468 | An Analytical Model for Time-Driven Cache Attacks |  |  | read |
| KN-LIT-2469 | An Asymptotically Optimal Method for Converting Bit Encryption to Multi-Bit Encryption |  |  | read |
| KN-LIT-2470 | An Efficiency-Preserving Transformation from Honest-Verifier Statistical Zero-Knowledge to Statistical Zero-Knowledge |  |  | read |
| KN-LIT-2471 | An Efficient and Generic Construction for Signal’s Handshake (X3DH): |  |  | read |
| KN-LIT-2472 | An Efficient and Parallel Gaussian Sampler for Lattices |  |  | read |
| KN-LIT-2473 | An Efficient CDH-based Signature Scheme |  |  | read |
| KN-LIT-2474 | An Efficient Countermeasure against Correlation Power-Analysis Attacks with Randomized Montgomery Operations for DF-ECC Processor |  |  | read |
| KN-LIT-2475 | An Efficient Method for Random Delay Generation in Embedded Software |  |  | read |
| KN-LIT-2476 | An Efficient Parallel Repetition Theorem |  |  | read |
| KN-LIT-2477 | An Efficient Protocol for Secure Two-Party Computation in the Presence of Malicious Adversaries |  |  | read |
| KN-LIT-2478 | An Efficient Public Key Trace and Revoke Scheme Secure against Adaptive Chosen Ciphertext Attack |  |  | read |
| KN-LIT-2479 | An Efficient Quantum Collision Search Algorithm and Implications on Symmetric Cryptography |  |  | read |
| KN-LIT-2480 | An Efficient Scheme for Proving a Shuffle |  |  | read |
| KN-LIT-2481 | An Efficient Signature Scheme from Bilinear |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2482 | An Efficient Strong Asymmetric PAKE Compiler Instantiable from Group Actions |  |  | read |
| KN-LIT-2483 | An Efficient Transform from Sigma Protocols to NIZK with a CRS and Non-Programmable |  |  | read |
| KN-LIT-2484 | An Enciphering Scheme Based on a Card Shuffle |  |  | read |
| KN-LIT-2485 | An Equivalence between Zero Knowledge and Commitments |  |  | read |
| KN-LIT-2486 | An Existential Unforgeable Signature Scheme based on Multivariate Quadratic Equations |  |  | read |
| KN-LIT-2487 | An Experimentally Veri ed Attack on Full |  |  | read |
| KN-LIT-2488 | An Exploration of Mechanisms for Dynamic |  |  | read |
| KN-LIT-2489 | An extended abstract of this paper appears in Advances in Cryptology — EUROCRYPT ’08, Lecture Notes in Computer Science Vol. 4965, N. Smart ed., Springer-Verlag, 2008. This is the full version |  | Advances in Cryptology | read |
| KN-LIT-2490 | An Extension of Kedlaya’s Point-Counting Algorithm to Superelliptic Curves |  |  | read |
| KN-LIT-2491 | An Efficient Two-Party Public Key Cryptosystem Secure against Adaptive |  |  | read |
| KN-LIT-2492 | An Identity Escrow Scheme with Appointed Verifiers |  |  | read |
| KN-LIT-2493 | An Identity-Based Signature from Gap Diffie-Hellman Groups |  |  | read |
| KN-LIT-2494 | An Improved Affine Equivalence Algorithm for Random Permutations |  |  | read |
| KN-LIT-2495 | An Improved Algebraic Attack on Hamsi-256 |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2496 | An Improved BKW Algorithm for LWE with Applications to Cryptography and Lattices |  |  | read |
| KN-LIT-2497 | An Improved Impossible Differential Attack on MISTY1 |  |  | read |
| KN-LIT-2498 | An Improved RNS Variant of the BFV Homomorphic Encryption Scheme |  |  | read |
| KN-LIT-2499 | An Improved Security Bound for HCTR |  |  | read |
| KN-LIT-2500 | An Incremental PoSW for General Weight Distributions |  |  | read |
| KN-LIT-2501 | An Introduction to the Theory of Elliptic Curves |  |  | read |
| KN-LIT-2502 | An L(1/3 + ε) Algorithm for the Discrete Logarithm Problem for Low Degree Curves |  |  | read |
| KN-LIT-2503 | An LLL Algorithm for Module Lattices |  |  | read |
| KN-LIT-2504 | An Ode to ANTS (by William Shakespeare) Shall I compare thee to another conference? |  |  | read |
| KN-LIT-2505 | An Optimal Distributed Discrete Log Protocol with Applications to Homomorphic Secret Sharing |  |  | read |
| KN-LIT-2506 | An Optimized Hardware Architecture for the Montgomery Multiplication Algorithm |  |  | read |
| KN-LIT-2507 | An RSA Family of Trap-door Permutations with |  |  | read |
| KN-LIT-2508 | An Uninstantiable Random-Oracle-Model Scheme for a Hybrid-Encryption Problem |  |  | read |
| KN-LIT-2509 | An Upper Bound on the Number of m-Resilient Boolean Functions |  |  | read |
| KN-LIT-2510 | Analysing the HPKE Standard |  |  | read |
| KN-LIT-2511 | Analysis and Improvement of the Generic Higher-Order Masking Scheme of FSE 2012 |  |  | read |
| KN-LIT-2512 | Analysis and Improvement of the Random Delay Countermeasure of CHES 2009 |  |  | read |
| KN-LIT-2513 | Analysis and Improvements of NTRU Encryption Paddings |  |  | read |
| KN-LIT-2514 | Analysis of Bernstein’s Factorization Circuit |  |  | read |
| KN-LIT-2515 | Analysis of Differential Attacks in ARX Constructions Gaëtan Leurent |  |  | read |
| KN-LIT-2516 | Analysis of Impossible, Integral and Zero-Correlation Attacks on Type-II Generalized Feistel Networks using the Matrix Method |  |  | read |
| KN-LIT-2517 | Analysis of Involutional Ciphers: Khazad and Anubis? |  |  | read |
| KN-LIT-2518 | Analysis of Multivariate Encryption Schemes: Application to Dob |  |  | read |
| KN-LIT-2519 | Analysis of Neural Cryptography |  |  | read |
| KN-LIT-2520 | Analysis of One Popular Group Signature Scheme |  |  | read |
| KN-LIT-2521 | Analysis of QUAD Bo-Yin Yang1 , Owen Chia-Hsin Chen2 |  |  | read |
| KN-LIT-2522 | Analysis of Random Oracle Instantiation Scenarios for OAEP and other Practical Schemes |  |  | read |
| KN-LIT-2523 | Analysis of reduced-SHAvite-3-256 v2 |  |  | read |
| KN-LIT-2524 | Analysis of RIPEMD-160: New Collision |  |  | read |
| KN-LIT-2525 | Analysis of RMAC |  |  | read |
| KN-LIT-2526 | Analysis of SHA-512/224 and SHA-512/256 |  |  | read |
| KN-LIT-2527 | Analysis of Step-Reduced SHA-256? Florian Mendel?? , Norbert Pramstaller |  |  | read |
| KN-LIT-2528 | Analysis of the Blockchain Protocol in Asynchronous Networks |  |  | read |
| KN-LIT-2529 | Analysis of the Kupyna-256 Hash Function |  |  | read |
| KN-LIT-2530 | Analysis of the Non-linear Part of Mugi |  |  | read |
| KN-LIT-2531 | Analysis of the security of the PSSI problem and cryptanalysis of the Durandal signature scheme |  |  | read |
| KN-LIT-2532 | Analyzing Blockwise Lattice Algorithms using Dynamical Systems 1 |  |  | read |
| KN-LIT-2533 | Analyzing Multi-Key Security Degradation |  |  | read |
| KN-LIT-2534 | Analyzing the complexity of reference post-quantum software |  |  | read |
| KN-LIT-2535 | Analyzing the complexity of reference post-quantum software: the case of lattice-based KEMs |  |  | read |
| KN-LIT-2536 | Anamorphic Encryption: Private Communication against a Dictator |  |  | read |
| KN-LIT-2537 | Anamorphic Signatures: Secrecy From a Dictator Who Only Permits Authentication! |  |  | read |
| KN-LIT-2538 | Andrew V. Sutherland |  |  | read |
| KN-LIT-2539 | Annihilation Attacks for Multilinear Maps: Cryptanalysis of Indistinguishability Obfuscation over GGH13 |  |  | read |
| KN-LIT-2540 | Anomalies and Vector Space Search: Tools for S-Box Analysis |  |  | read |
| KN-LIT-2541 | Anonymity of NIST PQC Round-3 KEMs |  |  | read |
| KN-LIT-2542 | Anonymous AE |  |  | read |
| KN-LIT-2543 | Anonymous Broadcast Encryption: Adaptive Security and Efficient Constructions in the Standard Model |  |  | read |
| KN-LIT-2544 | Anonymous Counting Tokens |  |  | read |
| KN-LIT-2545 | Anonymous Credentials on a Standard Java Card |  |  | read |
| KN-LIT-2546 | Anonymous Credentials on Java Card |  |  | read |
| KN-LIT-2547 | Anonymous Hierarchical Identity-Based Encryption (Without Random Oracles) |  |  | read |
| KN-LIT-2548 | Anonymous IBE, Leakage Resilience and Circular Security from New Assumptions? |  |  | read |
| KN-LIT-2549 | Anonymous Identification in Ad Hoc Groups |  |  | read |
| KN-LIT-2550 | Anonymous Permutation Routing |  |  | read |
| KN-LIT-2551 | Anonymous Quantum Communication |  |  | read |
| KN-LIT-2552 | Anonymous Signature Schemes |  |  | read |
| KN-LIT-2553 | Anonymous Signatures Made Easy |  |  | read |
| KN-LIT-2554 | Anonymous Tokens with Private Metadata Bit |  |  | read |
| KN-LIT-2555 | Anonymous Traitor Tracing: How to Embed Arbitrary Information in a Key |  |  | read |
| KN-LIT-2556 | Anonymous Transferable E-Cash |  |  | read |
| KN-LIT-2557 | Anonymous Whistleblowing over Authenticated Channels |  |  | read |
| KN-LIT-2558 | Anonymous, Robust Post-Quantum Public Key Encryption |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2559 | Another Look at Complementation Properties Charles Bouillaguet1 , Orr Dunkelman1,2 |  |  | read |
| KN-LIT-2560 | Another Look at Provable Security |  |  | read |
| KN-LIT-2561 | Another Round of Breaking and Making |  |  | read |
| KN-LIT-2562 | Another Step Towards Realizing Random Oracles: Non-Malleable Point Obfuscation |  |  | read |
| KN-LIT-2563 | Another Tradeoff Attack on Sprout-like Stream Ciphers? |  |  | read |
| KN-LIT-2564 | Another view of the division property? |  |  | read |
| KN-LIT-2565 | Antrag: Annular NTRU Trapdoor Generation Making Mitaka As Secure As Falcon |  |  | read |
| KN-LIT-2566 | APE: Authenticated Permutation-Based |  |  | read |
| KN-LIT-2567 | Applying MILP Method to Searching Integral Distinguishers Based on Division Property for 6 Lightweight Block Ciphers |  |  | read |
| KN-LIT-2568 | Approx-SVP in Ideal Lattices with Pre-processing |  |  | read |
| KN-LIT-2569 | Approximate Divisor Multiples – Factoring with Only a Third of the Secret CRT-Exponents |  |  | read |
| KN-LIT-2570 | Approximate Quantum Error-Correcting |  |  | read |
| KN-LIT-2571 | Approximate Trapdoors for Lattices and Smaller Hash-and-Sign Signatures |  |  | read |
| KN-LIT-2572 | Arithmetic Operators for Pairing-Based Cryptography |  |  | read |
| KN-LIT-2573 | Arithmetic Sketching Dan Boneh1 , Elette Boyle2 , Henry Corrigan-Gibbs3 |  |  | read |
| KN-LIT-2574 | Arithmetic Software Libraries |  |  | read |
| KN-LIT-2575 | ARMADILLO: a Multi-Purpose Cryptographic Primitive Dedicated to Hardware |  |  | read |
| KN-LIT-2576 | ARMed SPHINCS Computing a 41 KB signature in 16 KB of RAM 1 |  |  | read |
| KN-LIT-2577 | Arya: Nearly Linear-Time Zero-Knowledge Proofs for Correct Program Execution ? |  |  | read |
| KN-LIT-2578 | ASCA, SASCA and DPA with Enumeration: Which One Beats the Other and When? |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2579 | Aspects of Hyperelliptic Curves over Large Prime |  |  | read |
| KN-LIT-2580 | Assessment of Hiding the Higher-Order |  |  | read |
| KN-LIT-2581 | Astrolabous: A Universally Composable Time-Lock Encryption Scheme |  |  | read |
| KN-LIT-2582 | Asymmetric Group Key Agreement |  |  | read |
| KN-LIT-2583 | Asymmetric Group Message Franking: Definitions & Constructions |  |  | read |
| KN-LIT-2584 | Asymmetric Message Franking: Content Moderation for Metadata-Private |  |  | read |
| KN-LIT-2585 | Asymmetric PAKE with low computation and communication |  |  | read |
| KN-LIT-2586 | Asymptotic complexities of discrete logarithm algorithms in pairing-relevant finite fields |  |  | read |
| KN-LIT-2587 | Asymptotically Compact Adaptively Secure |  |  | read |
| KN-LIT-2588 | Asymptotically Efficient Lattice-Based Digital Signatures? |  |  | read |
| KN-LIT-2589 | Asymptotically faster quantum algorithms to solve multivariate quadratic equations |  |  | read |
| KN-LIT-2590 | Asymptotically Free Broadcast in Constant Expected Time via Packed VSS |  |  | read |
| KN-LIT-2591 | Asymptotically Good Ideal Linear Secret Sharing with Strong Multiplication over Any Fixed Finite Field |  |  | read |
| KN-LIT-2592 | Asymptotically Good Multiplicative LSSS over Galois Rings and Applications to MPC over Z/pk Z |  |  | read |
| KN-LIT-2593 | Asymptotically Optimal Communication for Torus-Based Cryptography |  |  | read |
| KN-LIT-2594 | Asymptotically Quasi-Optimal Cryptography |  |  | read |
| KN-LIT-2595 | Asymptotically Tight Bounds for Composing ORAM with PIR |  |  | read |
| KN-LIT-2596 | Asymptotically-Good Arithmetic Secret Sharing over Z/p Z with Strong Multiplication and Its Applications to E cient MPC |  |  | read |
| KN-LIT-2597 | Asymptotics for the standard block size in primal lattice attacks: |  |  | read |
| KN-LIT-2598 | Asymptotics of hybrid primal lattice attacks |  |  | read |
| KN-LIT-2599 | Asynchronous Byzantine Agreement with Subquadratic Communication |  |  | read |
| KN-LIT-2600 | Asynchronous Proactive Cryptosystems |  |  | read |
| KN-LIT-2601 | Asynchronous Secure Communication Tolerating Mixed Adversaries |  |  | read |
| KN-LIT-2602 | Asynchronous Secure Multiparty Computation in Constant Time |  |  | read |
| KN-LIT-2603 | Ate Pairing on Hyperelliptic Curves |  |  | read |
| KN-LIT-2604 | Atomic Secure Multi-Party Multiplication with Low Communication |  |  | read |
| KN-LIT-2605 | Attack and Improvement of a Secure S-box Calculation Based on the Fourier Transform |  |  | read |
| KN-LIT-2606 | Attack on Broadcast RC4 Revisited |  |  | read |
| KN-LIT-2607 | Attacking and defending the McEliece cryptosystem |  |  | read |
| KN-LIT-2608 | Attacking DSA Under a Repeated Bits Assumption |  |  | read |
| KN-LIT-2609 | Attacking Power Generators Using Unravelled Linearization: When Do We Output Too Much? |  |  | read |
| KN-LIT-2610 | Attacking RSA–CRT Signatures with |  |  | read |
| KN-LIT-2611 | Attacking State-of-the-Art Software Countermeasures—A Case Study for AES |  |  | read |
| KN-LIT-2612 | Attacking the Knudsen-Preneel Compression Functions |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2613 | Attacks and Countermeasures for White-box Designs? |  |  | read |
| KN-LIT-2614 | Attacks and Security Proofs of EAX-Prime |  |  | read |
| KN-LIT-2615 | Attribute Based Encryption (and more) for Nondeterministic Finite Automata from LWE |  |  | read |
| KN-LIT-2616 | Attribute Based Encryption for Deterministic Finite Automata from DLIN |  |  | read |
| KN-LIT-2617 | Attribute-Based Encryption for Circuits from Multilinear Maps |  |  | read |
| KN-LIT-2618 | Attribute-Based Encryption with Fast Decryption |  |  | read |
| KN-LIT-2619 | Attribute-Based Functional Encryption on Lattices |  |  | read |
| KN-LIT-2620 | Attribute-Based Multi-Input FE (and more) for Attribute-Weighted Sums |  |  | read |
| KN-LIT-2621 | Attribute-Based Signatures for Circuits from Bilinear Map |  |  | read |
| KN-LIT-2622 | Attribute-based Signatures for Unbounded Circuits in the ROM and Efficient Instantiations from Lattices |  |  | read |
| KN-LIT-2623 | Attribute-Based Signatures for Unbounded Languages from Standard Assumptions |  |  | read |
| KN-LIT-2624 | Augmented Random Oracles |  |  | read |
| KN-LIT-2625 | Aurora: Transparent Succinct Arguments for R1CS |  |  | read |
| KN-LIT-2626 | Authenticated and Misuse-Resistant Encryption of Key-Dependent Data |  |  | read |
| KN-LIT-2627 | Authenticated Encryption in the Face of |  |  | read |
| KN-LIT-2628 | Authenticated Encryption with Key Identification |  |  | read |
| KN-LIT-2629 | Authenticated Encryption with Variable Stretch |  |  | read |
| KN-LIT-2630 | Authenticated Garbling from Simple Correlations |  |  | read |
| KN-LIT-2631 | Authenticated Key Exchange and Key Encapsulation in the Standard Model |  |  | read |
| KN-LIT-2632 | Authenticated Key Exchange and Signatures with Tight Security in the Standard Model |  |  | read |
| KN-LIT-2633 | Authenticated Key Exchange from Ideal Lattices Jiang Zhang1 , Zhenfeng Zhang1, , Jintai Ding2,3 |  |  | read |
| KN-LIT-2634 | Authenticating Pervasive Devices with Human Protocols |  |  | read |
| KN-LIT-2635 | Authentication in the Bounded Storage Model |  |  | read |
| KN-LIT-2636 | Autocorrelation Coefficients and Correlation Immunity of Boolean Functions |  |  | read |
| KN-LIT-2637 | Automated Analysis of Cryptographic |  |  | read |
| KN-LIT-2638 | Automated Design of Cryptographic Devices Resistant to Multiple Side-Channel Attacks |  |  | read |
| KN-LIT-2639 | Automated Meet-in-the-Middle Attack Goes to Feistel |  |  | read |
| KN-LIT-2640 | Automated Security Proofs with Sequences of Games |  |  | read |
| KN-LIT-2641 | Automated Unbounded Analysis of Cryptographic Constructions in the Generic Group Model |  |  | read |
| KN-LIT-2642 | Automatic Search for Key-Bridging Technique: |  |  | read |
| KN-LIT-2643 | Automatic Search for Related-Key Differential Characteristics in Byte-Oriented Block Ciphers: Application |  |  | read |
| KN-LIT-2644 | Automatic Search for the Best Trails in ARX: Application to Block Cipher Speck |  |  | read |
| KN-LIT-2645 | Automatic Search of Attacks on round-reduced AES and Applications |  |  | read |
| KN-LIT-2646 | Automatic Search of Bit-Based Division Property for ARX Ciphers and Word-Based Division Property |  |  | read |
| KN-LIT-2647 | Automatic Verification of Differential Characteristics: Application to Reduced Gimli |  |  | read |
| KN-LIT-2648 | B-SIDH: supersingular isogeny Diffie-Hellman using twisted torsion |  |  | read |
| KN-LIT-2649 | Back to Massey: Impressively fast, scalable and tight security evaluation tools |  |  | read |
| KN-LIT-2650 | Backdoors in Pseudorandom Number Generators: Possibility and Impossibility Results |  |  | read |
| KN-LIT-2651 | Bad directions in cryptographic hash functions |  |  | read |
| KN-LIT-2652 | Balanced Non-Adjacent Forms |  |  | read |
| KN-LIT-2653 | Bandwidth-efficient threshold |  |  | read |
| KN-LIT-2654 | Banquet: Short and Fast Signatures from AES |  |  | read |
| KN-LIT-2655 | Barriers for Succinct Arguments in the Random Oracle Model |  |  | read |
| KN-LIT-2656 | Basing PRFs on Constant-Query Weak PRFs: Minimizing Assumptions for Efficient Symmetric Cryptography? |  |  | read |
| KN-LIT-2657 | Basing Weak Public-Key Cryptography on Strong One-Way Functions |  |  | read |
| KN-LIT-2658 | Batch Arguments for NP and More from Standard Bilinear Group Assumptions |  |  | read |
| KN-LIT-2659 | Batch binary Edwards |  |  | read |
| KN-LIT-2660 | Batch Bootstrapping I: A New Framework for SIMD Bootstrapping in Polynomial Modulus |  |  | read |
| KN-LIT-2661 | Batch Bootstrapping II: Bootstrapping in Polynomial Modulus Only Requires Õ(1) FHE Multiplications in Amortization |  |  | read |
| KN-LIT-2662 | Batch Fully Homomorphic Encryption over the Integers? |  |  | read |
| KN-LIT-2663 | Batch NFS |  |  | read |
| KN-LIT-2664 | Batch Verification and Proofs of Proximity with Polylog Overhead |  |  | read |
| KN-LIT-2665 | Batch Verification for Statistical Zero Knowledge Proofs? |  |  | read |
| KN-LIT-2666 | Batch Verification of Short Signatures |  |  | read |
| KN-LIT-2667 | Batch-OT with Optimal Rate |  |  | read |
| KN-LIT-2668 | Batching Base Oblivious Transfers? |  |  | read |
| KN-LIT-2669 | Batching Schnorr Identification Scheme with Applications to Privacy-Preserving |  |  | read |
| KN-LIT-2670 | Batching Techniques for Accumulators with Applications to IOPs and Stateless Blockchains |  |  | read |
| KN-LIT-2671 | BDD-based Cryptanalysis of Keystream Generators |  |  | read |
| KN-LIT-2672 | Be Adaptive, Avoid Overcommitting |  |  | read |
| KN-LIT-2673 | BeepBeep: Embedded Real-Time Encryption |  |  | read |
| KN-LIT-2674 | Behind the Scene of Side Channel Attacks |  |  | read |
| KN-LIT-2675 | Best of Both Worlds Revisiting the Spymasters Double Agent Problem |  |  | read |
| KN-LIT-2676 | Best Possible Information-Theoretic MPC |  |  | read |
| KN-LIT-2677 | BETA: Biometric-Enabled Threshold Authentication Shashank Agrawal1 , Saikrishna Badrinarayanan2 , Payman Mohassel3 |  |  | read |
| KN-LIT-2678 | Better Algorithms for LWE and LWR |  |  | read |
| KN-LIT-2679 | Better Bootstrapping in Fully Homomorphic Encryption |  |  | read |
| KN-LIT-2680 | Better Concrete Security for Half-Gates Garbling (in the Multi-Instance Setting) |  |  | read |
| KN-LIT-2681 | Better Security-Efficiency Trade-Offs in Permutation-Based Two-Party Computation |  |  | read |
| KN-LIT-2682 | Better Steady than Speedy: Full break of SPEEDY-7-192 |  |  | read |
| KN-LIT-2683 | Better than Advertised Security for Non-Interactive Threshold Signatures Mihir Bellare1[0000000287655573] |  |  | read |
| KN-LIT-2684 | Better Two-Round Adaptive Multi-Party Computation? |  |  | read |
| KN-LIT-2685 | Better Zero-Knowledge Proofs for Lattice Encryption and Their Application to Group Signatures? |  |  | read |
| KN-LIT-2686 | Between a Rock and a Hard Place: Interpolating |  |  | read |
| KN-LIT-2687 | Beyond 2c/2 Security in Sponge-Based Authenticated Encryption Modes |  |  | read |
| KN-LIT-2688 | Beyond Birthday Bound Secure Fresh Rekeying: Application to Authenticated Encryption |  |  | read |
| KN-LIT-2689 | Beyond Birthday Bound Secure MAC in Faulty Nonce Model |  |  | read |
| KN-LIT-2690 | Beyond Hellman’s Time-Memory Trade-Offs with Applications to Proofs of Space |  |  | read |
| KN-LIT-2691 | Beyond MPC-in-the-Head: Black-Box Constructions of Short Zero-Knowledge Proofs |  |  | read |
| KN-LIT-2692 | Beyond quadratic speedups in quantum attacks on symmetric schemes |  |  | read |
| KN-LIT-2693 | Beyond Security and Efficiency: On-Demand Ratcheting with Security Awareness |  |  | read |
| KN-LIT-2694 | Beyond Software Watermarking: Traitor-Tracing for Pseudorandom Functions |  |  | read |
| KN-LIT-2695 | Beyond the Limitation of Prime-Order Bilinear |  |  | read |
| KN-LIT-2696 | Beyond Uber: Instantiating Generic Groups via PGGs |  |  | read |
| KN-LIT-2697 | Beyond Uniformity: Better Security/Efficiency Tradeoffs for Compression Functions |  |  | read |
| KN-LIT-2698 | Beyond-birthday-bound Security Based on Tweakable Block Cipher |  |  | read |
| KN-LIT-2699 | Beyond-Birthday-Bound Security for Tweakable Even-Mansour Ciphers with Linear Tweak and Key Mixing |  |  | read |
| KN-LIT-2700 | Bicameral and Auditably Private Signatures |  |  | read |
| KN-LIT-2701 | Biclique Cryptanalysis of the Full AES |  |  | read |
| KN-LIT-2702 | Bicliques for permutations: |  |  | read |
| KN-LIT-2703 | Bicliques for Preimages: Attacks on Skein-512 and the SHA-2 family ? |  |  | read |
| KN-LIT-2704 | BIELLIPTIC SHIMURA CURVES X0D (N ) WITH NONTRIVIAL LEVEL |  |  | read |
| KN-LIT-2705 | Bifurcated Signatures: Folding the Accountability vs. Anonymity Dilemma into a Single Private Signing Scheme |  |  | read |
| KN-LIT-2706 | Big-Key Symmetric Encryption: Resisting Key Exfiltration |  |  | read |
| KN-LIT-2707 | Bilinear Entropy Expansion from the Decisional |  |  | read |
| KN-LIT-2708 | Binary AMD Circuits from Secure Multiparty Computation |  |  | read |
| KN-LIT-2709 | Binary Edwards Curves |  |  | read |
| KN-LIT-2710 | Bingo: Adaptivity and Asynchrony in Verifiable |  |  | read |
| KN-LIT-2711 | Bipartite Modular Multiplication |  |  | read |
| KN-LIT-2712 | Bit Security as Computational Cost for Winning Games with High Probability |  |  | read |
| KN-LIT-2713 | Bit-Based Division Property and Application to Simon Family |  |  | read |
| KN-LIT-2714 | Bit-Pattern Based Integral Attack |  |  | read |
| KN-LIT-2715 | Bit-Sliding: A Generic Technique for Bit-Serial Implementations of SPN-based Primitives |  |  | read |
| KN-LIT-2716 | Bitcoin as a Transaction Ledger: A Composable Treatment? |  |  | read |
| KN-LIT-2717 | Bitline PUF: Building Native Challenge-Response PUF Capability into Any SRAM |  |  | read |
| KN-LIT-2718 | BiTR: Built-in Tamper Resilience |  |  | read |
| KN-LIT-2719 | Bits Security of the Elliptic Curve Diffie–Hellman Secret Keys |  |  | read |
| KN-LIT-2720 | Bivariate Polynomials Modulo Composites and their Applications |  |  | read |
| KN-LIT-2721 | BKW Meets Fourier New Algorithms for LPN with Sparse Parities |  |  | read |
| KN-LIT-2722 | Black-Box Analysis of the Block-Cipher-Based Hash-Function Constructions from PGV |  |  | read |
| KN-LIT-2723 | Black-Box Circular-Secure Encryption Beyond Affine Functions |  |  | read |
| KN-LIT-2724 | Black-Box Composition Does Not Imply |  |  | read |
| KN-LIT-2725 | Black-Box Construction of a Non-Malleable Encryption Scheme from Any Semantically Secure One |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2726 | Black-box Constructions of Composable Protocols without Set-Up |  |  | read |
| KN-LIT-2727 | Black-Box Constructions of Two-Party Protocols from One-Way Functions |  |  | read |
| KN-LIT-2728 | Black-Box Extension Fields and the Inexistence of Field-Homomorphic One-Way Permutations |  |  | read |
| KN-LIT-2729 | Black-Box Impossibilities of Obtaining 2-Round Weak ZK and Strong WI from Polynomial Hardness |  |  | read |
| KN-LIT-2730 | Black-Box Non-Interactive Non-Malleable Commitments |  |  | read |
| KN-LIT-2731 | Black-Box Parallel Garbled RAM |  |  | read |
| KN-LIT-2732 | Black-Box Reusable NISC with Random Oracles |  |  | read |
| KN-LIT-2733 | Black-Box Secret Sharing from Primitive Sets in Algebraic Number Fields |  |  | read |
| KN-LIT-2734 | Black-Box Separations for Differentially Private Protocols |  |  | read |
| KN-LIT-2735 | Black-Box Separations for Non-Interactive Commitments in a Quantum World |  |  | read |
| KN-LIT-2736 | Black-Box Separations for One-More (Static) CDH and Its Generalization? |  |  | read |
| KN-LIT-2737 | Black-box use of One-way Functions is Useless for Optimal Fair Coin-Tossing |  |  | read |
| KN-LIT-2738 | Black-Hole Radiation Decoding is Quantum Cryptography |  |  | read |
| KN-LIT-2739 | Blackbox Secret Sharing Revisited: A Coding-Theoretic Approach with Application to Expansionless Near-Threshold Schemes |  |  | read |
| KN-LIT-2740 | Blind and Anonymous Identity-Based Encryption and Authorised Private Searches on Public Key Encrypted Data |  |  | read |
| KN-LIT-2741 | Blind Identity-Based Encryption and Simulatable Oblivious Transfer |  |  | read |
| KN-LIT-2742 | Blind Schnorr Signatures and Signed ElGamal Encryption in the Algebraic Group Model |  |  | read |
| KN-LIT-2743 | Blind Source Separation from Single Measurements using Singular Spectrum Analysis |  |  | read |
| KN-LIT-2744 | Block Cipher Invariants as Eigenvectors of Correlation Matrices? |  |  | read |
| KN-LIT-2745 | Block Ciphers and Systems of Quadratic Equations? |  |  | read |
| KN-LIT-2746 | Block Ciphers Implementations Provably Secure Against Second Order Side Channel Analysis |  |  | read |
| KN-LIT-2747 | Block Ciphers that are Easier to Mask: How Far Can we Go? |  |  | read |
| KN-LIT-2748 | Block Ciphers – Focus On The Linear Layer (feat. PRIDE)? Martin R. Albrecht1?? , Benedikt Driessen2? ? ? , Elif Bilge Kavun3 |  |  | read |
| KN-LIT-2749 | Block ciphers – past and present Lars Ramkilde Knudsen |  |  | read |
| KN-LIT-2750 | Block-Cipher-Based Tree Hashing |  |  | read |
| KN-LIT-2751 | Blockchains Enable Non-Interactive MPC |  |  | read |
| KN-LIT-2752 | Blockchains from Non-Idealized Hash Functions 1 ?2,3 |  |  | read |
| KN-LIT-2753 | Blockcipher Based Hashing Revisited Martijn Stam |  |  | read |
| KN-LIT-2754 | Blockcipher-based Authenticated Encryption: How Small Can We Go? |  |  | read |
| KN-LIT-2755 | Blockcipher-based MACs: Beyond the Birthday Bound without Message Length Yusuke Naito |  |  | read |
| KN-LIT-2756 | Blockwise Rank Decoding Problem and LRPC Codes: Cryptosystems with Smaller Sizes |  |  | read |
| KN-LIT-2757 | Blockwise-Adaptive Attackers Revisiting the (in)security of some provably secure Encryption Modes: CBC, GEM, IACBC |  |  | read |
| KN-LIT-2758 | Bloom Filter Encryption and Applications to Efficient Forward-Secret 0-RTT Key Exchange |  |  | read |
| KN-LIT-2759 | BLOOM: Bimodal Lattice One-Out-of-Many Proofs and Applications |  |  | read |
| KN-LIT-2760 | Boneh et al.’s k-Element Aggregate Extraction |  |  | read |
| KN-LIT-2761 | Bonsai Trees, or How to Delegate a Lattice Basis |  |  | read |
| KN-LIT-2762 | Boolean Searchable Symmetric Encryption with Worst-Case |  |  | read |
| KN-LIT-2763 | Boomerang Attacks on BLAKE-32 |  |  | read |
| KN-LIT-2764 | Boomerang Connectivity Table: A New Cryptanalysis Tool |  |  | read |
| KN-LIT-2765 | Boosting Authenticated Encryption Robustness With Minimal Modifications |  |  | read |
| KN-LIT-2766 | Boosting Merkle-Damgård Hashing for Message Authentication |  |  | read |
| KN-LIT-2767 | Boosting OMD for Almost Free Authentication of Associated Data |  |  | read |
| KN-LIT-2768 | Boosting the Security of Blind Signature Schemes |  |  | read |
| KN-LIT-2769 | Boosting Verifiable Computation on Encrypted Data |  |  | read |
| KN-LIT-2770 | Bootstrapping BGV Ciphertexts with a Wider Choice of p and q |  |  | read |
| KN-LIT-2771 | Bootstrapping for HElib |  |  | read |
| KN-LIT-2772 | Bootstrapping fully homomorphic encryption over the integers in less than one second |  |  | read |
| KN-LIT-2773 | Bootstrapping Obfuscators via Fast Pseudorandom Functions |  |  | read |
| KN-LIT-2774 | Bootstrapping the Blockchain, with Applications |  |  | read |
| KN-LIT-2775 | Bounded CCA2-Secure |  |  | read |
| KN-LIT-2776 | Bounded Collusion ABE for TMs from IBE |  |  | read |
| KN-LIT-2777 | Bounded Functional Encryption for Turing Machines: Adaptive Security from General Assumptions |  |  | read |
| KN-LIT-2778 | Bounded Indistinguishability and the Complexity of Recovering Secrets? |  |  | read |
| KN-LIT-2779 | Bounded Key-Dependent Message Security |  |  | read |
| KN-LIT-2780 | Bounded Tamper Resilience: How to go beyond the Algebraic Barrier |  |  | read |
| KN-LIT-2781 | Bounded-Collusion Attribute-Based Encryption from Minimal Assumptions |  |  | read |
| KN-LIT-2782 | Bounded-Collusion IBE from Key Homomorphism |  |  | read |
| KN-LIT-2783 | Bounded-Collusion Identity-Based Encryption from Semantically-Secure Public-Key Encryption: Generic Constructions with Short Ciphertexts |  |  | read |
| KN-LIT-2784 | Bounds in Shallows and in Miseries? |  |  | read |
| KN-LIT-2785 | Brakedown: Linear-time and field-agnostic SNARKs for R1CS |  |  | read |
| KN-LIT-2786 | Branching Heuristics in Differential Collision Search with Applications to SHA-512 |  |  | read |
| KN-LIT-2787 | Break-glass Encryption |  |  | read |
| KN-LIT-2788 | Breaking a Cryptographic Protocol with Pseudoprimes |  |  | read |
| KN-LIT-2789 | Breaking and Repairing GCM Security Proofs |  |  | read |
| KN-LIT-2790 | Breaking Ciphers with COPACOBANA A Cost-Optimized Parallel Code Breaker |  |  | read |
| KN-LIT-2792 | Breaking Grain-128 with Dynamic Cube Attacks |  |  | read |
| KN-LIT-2793 | Breaking Mifare DESFire MF3ICD40: Power Analysis and Templates in the Real World? |  |  | read |
| KN-LIT-2794 | Breaking pairing-based cryptosystems using ηT pairing over GF (397 ) Takuya Hayashi1 |  |  | read |
| KN-LIT-2795 | Breaking post-quantum cryptography with arithmetic geometry Andrew Sutherland |  |  | read |
| KN-LIT-2796 | Breaking Rainbow Takes a Weekend on a Laptop |  |  | read |
| KN-LIT-2797 | Breaking RSA Generically is Equivalent to Factoring |  |  | read |
| KN-LIT-2798 | Breaking Symmetric Cryptosystems using Quantum Period Finding |  |  | read |
| KN-LIT-2799 | Breaking the Circuit Size Barrier for Secure Computation Under DDH |  |  | read |
| KN-LIT-2800 | Breaking the Circuit Size Barrier for Secure Computation under Quasi-Polynomial LPN |  |  | read |
| KN-LIT-2801 | Breaking the decisional Diffie-Hellman problem for class group actions using genus theory |  |  | read |
| KN-LIT-2802 | Breaking The FF3 Format-Preserving Encryption Standard Over Small Domains |  |  | read |
| KN-LIT-2803 | Breaking the Sub-Exponential Barrier in Obfustopia |  |  | read |
| KN-LIT-2804 | Breaking ‘128-bit Secure’ Supersingular Binary Curves? |  |  | read |
| KN-LIT-2805 | Breakthrough silicon scanning discovers backdoor in military chip |  |  | read |
| KN-LIT-2806 | Bridging Broadcast Encryption and Group Key Agreement Qianhong Wu1,2 , Bo Qin1,3 , Lei Zhang4 |  |  | read |
| KN-LIT-2807 | Bridging Game Theory and Cryptography: |  |  | read |
| KN-LIT-2808 | Bringing Order to Chaos: The Case of Collision-Resistant Chameleon-Hashes |  |  | read |
| KN-LIT-2809 | Broadcast Amplification |  |  | read |
| KN-LIT-2810 | Broadcast and Trace with N ε Ciphertext Size from Standard Assumptions |  |  | read |
| KN-LIT-2811 | Broadcast Encryption with Size N 1/3 and More from k-Lin |  |  | read |
| KN-LIT-2812 | Broadcast, Trace and Revoke with Optimal Parameters from Polynomial Hardness |  |  | read |
| KN-LIT-2813 | Broadcast-Optimal Two Round MPC with an Honest Majority |  |  | read |
| KN-LIT-2814 | Broadcast-Optimal Two-Round MPC? |  |  | read |
| KN-LIT-2815 | Bug Attacks |  |  | read |
| KN-LIT-2816 | Building an Efficient Lattice Gadget Toolkit: |  |  | read |
| KN-LIT-2817 | Building Better Signcryption Schemes with Tag-KEMs |  |  | read |
| KN-LIT-2818 | Building Lossy Trapdoor Functions from Lossy Encryption |  |  | read |
| KN-LIT-2819 | Building Quantum-One-Way Functions from Block Ciphers: Davies-Meyer and Merkle-Damgård Constructions |  |  | read |
| KN-LIT-2820 | But Why Does it Work? A Rational Protocol Design Treatment of Bitcoin |  |  | read |
| KN-LIT-2821 | Cache Attacks Enable Bulk Key Recovery on the Cloud |  |  | read |
| KN-LIT-2822 | Cache-Collision Timing Attacks Against AES |  |  | read |
| KN-LIT-2823 | Cache-timing attacks on AES |  |  | read |
| KN-LIT-2824 | Cache-Timing Template Attacks |  |  | read |
| KN-LIT-2825 | CacheBleed: A Timing Attack on OpenSSL Constant Time RSA |  |  | read |
| KN-LIT-2826 | CacheZoom: How SGX Amplifies The Power of Cache Attacks |  |  | read |
| KN-LIT-2827 | CAIRN 2: An FPGA Implementation of the Sieving Step in the Number Field Sieve Method |  |  | read |
| KN-LIT-2828 | Calamari and Falafl: Logarithmic (Linkable) Ring Signatures from Isogenies and Lattices |  |  | read |
| KN-LIT-2829 | Can a Public Blockchain Keep a Secret? |  |  | read |
| KN-LIT-2830 | Can Optimally-Fair Coin Tossing be Based on One-Way Functions? |  |  | read |
| KN-LIT-2831 | Can we avoid tests for zero in fast elliptic-curve arithmetic? |  |  | read |
| KN-LIT-2832 | Candidate iO From Homomorphic Encryption Schemes |  |  | read |
| KN-LIT-2833 | Candidate Multilinear Maps from Ideal Lattices |  |  | read |
| KN-LIT-2834 | Candidate Obfuscation via Oblivious LWE Sampling |  |  | read |
| KN-LIT-2835 | Candidate Trapdoor Claw-Free Functions from Group Actions with Applications to Quantum Protocols |  |  | read |
| KN-LIT-2836 | Candidate Witness Encryption from Lattice Techniques |  |  | read |
| KN-LIT-2837 | Capacity and Data Complexity in Multidimensional Linear Attack |  |  | read |
| KN-LIT-2838 | CAPTCHA: Using Hard AI Problems For Security |  |  | read |
| KN-LIT-2839 | Card-based Cryptographic Protocols Using a Minimal Number of Cards |  |  | read |
| KN-LIT-2840 | Card-based Cryptography Meets Formal Verification |  |  | read |
| KN-LIT-2841 | Careful with Composition: Limitations of the Indifferentiability Framework |  |  | read |
| KN-LIT-2842 | CASE: A New Frontier in Public-Key Authenticated Encryption |  |  | read |
| KN-LIT-2843 | Catalic: Delegated PSI Cardinality with Applications to Contact Tracing |  |  | read |
| KN-LIT-2844 | Categorization of Faulty Nonce Misuse Resistant Message Authentication |  |  | read |
| KN-LIT-2845 | Caveat Implementor! |  |  | read |
| KN-LIT-2846 | CBE from CL-PKE: A Generic Construction and Efficient Schemes |  |  | read |
| KN-LIT-2847 | CCA Proxy Re-Encryption without Bilinear Maps in the Standard Model |  |  | read |
| KN-LIT-2848 | CCA Updatable Encryption Against Malicious Re-Encryption Attacks |  |  | read |
| KN-LIT-2849 | CCA-1 Secure Updatable Encryption with Adaptive Security |  |  | read |
| KN-LIT-2850 | CCA-Secure (Puncturable) KEMs from Encryption With Non-Negligible Decryption Errors |  |  | read |
| KN-LIT-2851 | CCA-Secure Inner-Product Functional Encryption from Projective Hash Functions |  |  | read |
| KN-LIT-2852 | CCA-Secure Keyed-Fully Homomorphic Encryption |  |  | read |
| KN-LIT-2853 | CCA-Secure Proxy Re-Encryption without Pairings? |  |  | read |
| KN-LIT-2854 | CDs Have Fingerprints Too |  |  | read |
| KN-LIT-2855 | Central endomorphisms of groups and radical rings* |  |  | read |
| KN-LIT-2856 | Ceremonies for End-to-End Verifiable Elections |  |  | read |
| KN-LIT-2857 | Certicom ECC Challenge |  |  | read |
| KN-LIT-2858 | Certificate-Based Encryption and the Certificate Revocation Problem |  |  | read |
| KN-LIT-2859 | Certificateless Encryption Schemes Strongly Secure in the Standard Model |  |  | read |
| KN-LIT-2860 | Certificateless Public Key Cryptography |  |  | read |
| KN-LIT-2861 | Certified Everlasting Zero-Knowledge Proof for QMA |  |  | read |
| KN-LIT-2862 | Certifying Giant Nonprimes 1 2 |  |  | read |
| KN-LIT-2863 | Certifying RSA |  |  | read |
| KN-LIT-2864 | Certifying Trapdoor Permutations, Revisited ? |  |  | read |
| KN-LIT-2865 | ChaCha, a variant of Salsa20 |  |  | read |
| KN-LIT-2866 | Chain Reductions for Multi-Signatures and the HBMS Scheme |  |  | read |
| KN-LIT-2867 | Chainable Functional |  |  | read |
| KN-LIT-2868 | Challenges for Trusted Computing |  |  | read |
| KN-LIT-2869 | Chameleon-Hashes with Ephemeral Trapdoors |  |  | read |
| KN-LIT-2870 | Changing of the Guards: a simple and efficient method for achieving uniformity in threshold sharing |  |  | read |
| KN-LIT-2871 | Channels of Small Log-Ratio Leakage and Characterization of Two-Party Differentially Private Computation |  |  | read |
| KN-LIT-2872 | Characterisation and Estimation of the Key Rank Distribution in the Context of Side Channel Evaluations |  |  | read |
| KN-LIT-2873 | Characterization of Secure Multiparty Computation Without Broadcast |  |  | read |
| KN-LIT-2874 | Characterizing Collision and Second-Preimage Resistance in Linicrypt? |  |  | read |
| KN-LIT-2875 | Characterizing Deterministic-Prover Zero Knowledge |  | Journal of Cryptology | read |
| KN-LIT-2876 | Characterizing Ideal Weighted Threshold Secret Sharing |  |  | read |
| KN-LIT-2877 | Characterizing the Cryptographic Properties of Reactive 2-Party Functionalities |  |  | read |
| KN-LIT-2878 | Chernoff-type Direct Product Theorems |  |  | read |
| KN-LIT-2879 | CHIP and CRISP: Protecting All Parties Against Compromise through Identity-Binding PAKEs |  |  | read |
| KN-LIT-2880 | Chopsticks: Fork-Free Two-Round Multi-Signatures from Non-Interactive Assumptions |  |  | read |
| KN-LIT-2881 | Chosen Ciphertext Secure Keyed-Homomorphic |  |  | read |
| KN-LIT-2882 | Chosen Ciphertext Security from Injective Trapdoor Functions? |  |  | read |
| KN-LIT-2883 | Chosen Ciphertext Security via Point Obfuscation |  |  | read |
| KN-LIT-2884 | Chosen Ciphertext Security via UCE |  |  | read |
| KN-LIT-2885 | Chosen-Ciphertext Attacks against MOSQUITO |  |  | read |
| KN-LIT-2886 | Chosen-Ciphertext Secure Dual-Receiver Encryption in the Standard Model Based on Post-Quantum Assumptions |  |  | read |
| KN-LIT-2887 | Chosen-Ciphertext Secure Fully Homomorphic Encryption? |  |  | read |
| KN-LIT-2888 | Chosen-Ciphertext Secure Key-Encapsulation Based on Gap Hashed Diffie-Hellman |  |  | read |
| KN-LIT-2889 | Chosen-Ciphertext Security from Identity-Based Encryption |  |  | read |
| KN-LIT-2890 | Chosen-Ciphertext Security from Subset Sum |  |  | read |
| KN-LIT-2891 | Chosen-Ciphertext Security from Tag-Based Encryption |  |  | read |
| KN-LIT-2892 | Chosen-Ciphertext Security of Multiple Encryption |  |  | read |
| KN-LIT-2893 | Chosen-Ciphertext Security via Correlated Products |  |  | read |
| KN-LIT-2894 | Chosen-prefix Collisions for MD5 and Colliding X.509 Certificates for Different Identities |  |  | read |
| KN-LIT-2895 | CHRISTOPHE PETIT Mail address: 16c Devonport Road, W12 8NY, London, UK |  |  | read |
| KN-LIT-2896 | cient Pairing-Based Shu e Argument 1 |  |  | read |
| KN-LIT-2897 | cient Public Key Encryption Based on Ideal |  |  | read |
| KN-LIT-2898 | cient State Recovery Attack on X-FCSR-256 |  |  | read |
| KN-LIT-2899 | cient structural attack on NIST submission DAGS |  |  | read |
| KN-LIT-2900 | Ciminion: Symmetric Encryption Based on Toffoli-Gates over Large Finite Fields |  |  | read |
| KN-LIT-2901 | Cipher DAGs (extended abstract) |  |  | read |
| KN-LIT-2902 | Ciphers Secure Against Related-Key Attacks |  |  | read |
| KN-LIT-2903 | Ciphertext Expansion in Limited-Leakage |  |  | read |
| KN-LIT-2904 | Ciphertext-Policy Attribute-Based Encryption: |  |  | read |
| KN-LIT-2905 | Circuit Compilers with O(1/ log(n)) Leakage Rate |  |  | read |
| KN-LIT-2906 | Circuit-ABE from LWE: Unbounded Attributes and Semi-Adaptive Security |  |  | read |
| KN-LIT-2907 | Circuit-Private Multi-Key FHE |  |  | read |
| KN-LIT-2908 | CIRCUITS FOR INTEGER FACTORIZATION: A PROPOSAL |  |  | read |
| KN-LIT-2909 | Circular and KDM Security for Identity-Based Encryption |  |  | read |
| KN-LIT-2910 | Circular and Leakage Resilient |  |  | read |
| KN-LIT-2911 | Circular Security Is Complete for KDM Security |  |  | read |
| KN-LIT-2912 | Circular Security Separations for Arbitrary Length Cycles from LWE |  |  | read |
| KN-LIT-2913 | Circular-Secure Encryption from Decision Diffie-Hellman |  |  | read |
| KN-LIT-2914 | Classical and Quantum Full Plaintext Recovery for Low-Round Feistel-Type Designs |  |  | read |
| KN-LIT-2915 | Classical Cryptographic Protocols in a Quantum World |  |  | read |
| KN-LIT-2916 | Classical Proofs for the Quantum Collapsing Property of Classical Hash Functions Serge Fehr |  |  | read |
| KN-LIT-2917 | Classical proofs of quantum knowledge |  |  | read |
| KN-LIT-2918 | Classical Verification of Quantum Computations with Efficient Verifier |  |  | read |
| KN-LIT-2919 | Classical vs Quantum Random Oracles |  |  | read |
| KN-LIT-2920 | Classically Verifiable NIZK for QMA with Preprocessing |  |  | read |
| KN-LIT-2921 | Client-Server Concurrent Zero Knowledge with |  |  | read |
| KN-LIT-2922 | CLIMBING AND DESCENDING TALL VOLCANOS |  |  | read |
| KN-LIT-2923 | Cliptography: Clipping the Power of Kleptographic Attacks |  |  | read |
| KN-LIT-2924 | CLOC: Authenticated Encryption for Short Input |  |  | read |
| KN-LIT-2925 | Cloning Games: A General Framework for Unclonable Primitives |  |  | read |
| KN-LIT-2926 | Cluster Computing in Zero Knowledge |  |  | read |
| KN-LIT-2927 | Clustering Effect in Simon and Simeck |  |  | read |
| KN-LIT-2928 | CM ELLIPTIC CURVES: VOLCANOES, REALITY AND APPLICATIONS PETE L. CLARK Contents |  |  | read |
| KN-LIT-2929 | Co-Z Addition Formulæ and Binary Ladders on Elliptic Curves |  |  | read |
| KN-LIT-2930 | COA-Secure Obfuscation and Applications Ran Canetti1 , Suvradip Chakraborty2 , Dakshita Khurana3 |  |  | read |
| KN-LIT-2931 | COBRA: A Parallelizable Authenticated Online Cipher without Block Cipher Inverse |  |  | read |
| KN-LIT-2932 | Coded-BKW with Sieving |  |  | read |
| KN-LIT-2933 | Coded-BKW: Solving LWE Using Lattice Codes |  |  | read |
| KN-LIT-2934 | Coefficient Grouping for Complex Affine Layers |  |  | read |
| KN-LIT-2935 | Coefficient Grouping: Breaking Chaghri and More |  |  | read |
| KN-LIT-2936 | Cofactorization on Graphics Processing Units |  |  | read |
| KN-LIT-2937 | Collapse-binding quantum commitments without random oracles |  |  | read |
| KN-LIT-2938 | Collision Attack on 5 Rounds of Grøstl |  |  | read |
| KN-LIT-2939 | Collision Attacks against CAESAR Candidates Forgery and Key-Recovery against AEZ and Marble |  |  | read |
| KN-LIT-2940 | Collision Attacks against the Knudsen-Preneel Compression Functions |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2941 | Collision Attacks on AES-based MAC: Alpha-MAC |  |  | read |
| KN-LIT-2942 | Collision Attacks on Round-Reduced SHA-3 |  |  | read |
| KN-LIT-2943 | Collision Attacks on the Reduced Dual-Stream Hash Function RIPEMD-128 |  |  | read |
| KN-LIT-2944 | Collision Attacks on Up to 5 Rounds of SHA-3 Using Generalized Internal Differentials |  |  | read |
| KN-LIT-2945 | Collision of random walks and a refined analysis of attacks on the discrete logarithm problem |  |  | read |
| KN-LIT-2946 | Collision Resistant Hashing for Paranoids: Dealing with Multiple Collisions |  |  | read |
| KN-LIT-2947 | Collision Resistant Hashing from Sub-exponential Learning Parity with Noise |  |  | read |
| KN-LIT-2948 | Collision Search for Elliptic Curve Discrete Logarithm over GF(2m ) with FPGA |  |  | read |
| KN-LIT-2949 | Collision-based Power Analysis of Modular |  |  | read |
| KN-LIT-2950 | Collision-Resistance from Multi-Collision-Resistance |  |  | read |
| KN-LIT-2951 | Collision-resistant No More: Hash-and-sign Paradigm Revisited Ilya Mironov |  |  | read |
| KN-LIT-2952 | Collisions and Near-Collisions for Reduced-Round Tiger |  |  | read |
| KN-LIT-2953 | Collisions and Semi-Free-Start Collisions for Round-Reduced RIPEMD-160 |  |  | read |
| KN-LIT-2954 | Collisions are not Incidental: A Compression Function Exploiting Discrete Geometry |  |  | read |
| KN-LIT-2955 | Collisions for Step-Reduced SHA-256 |  |  | read |
| KN-LIT-2956 | Collisions for the LPS expander graph hash function |  |  | read |
| KN-LIT-2957 | Collisions of SHA-0 and Reduced SHA-1? |  |  | read |
| KN-LIT-2958 | Collisions on SHA-0 in one hour |  |  | read |
| KN-LIT-2959 | Colluding Attacks to a Payment Protocol and Two Signature Exchange Schemes |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-2960 | Collusion Resistant Broadcast and Trace from Positional Witness Encryption |  |  | read |
| KN-LIT-2961 | Collusion Resistant Copy-Protection for Watermarkable Functionalities |  |  | read |
| KN-LIT-2962 | Collusion Resistant Watermarkable PRFs from Standard Assumptions |  |  | read |
| KN-LIT-2963 | Collusion Resistant Watermarking Schemes for Cryptographic Functionalities |  |  | read |
| KN-LIT-2964 | Collusion-Free Multiparty Computation in the Mediated Model |  |  | read |
| KN-LIT-2965 | Collusion-Free Protocols in the Mediated Model |  |  | read |
| KN-LIT-2966 | Collusion-Resistant Functional Encryption for RAMs |  |  | read |
| KN-LIT-2967 | Comb to Pipeline: Fast Software Encryption Revisited |  |  | read |
| KN-LIT-2968 | Combinatorially Homomorphic Encryption |  |  | read |
| KN-LIT-2969 | Combinatorics in Information-Theoretic Cryptography (invited talk)? |  |  | read |
| KN-LIT-2970 | Combined Attack on CRT-RSA |  |  | read |
| KN-LIT-2971 | Combined Fault and Leakage Resilience: Composability |  |  | read |
| KN-LIT-2972 | Combiners for Backdoored Random Oracles |  |  | read |
| KN-LIT-2973 | Combiners for Functional Encryption, Unconditionally |  |  | read |
| KN-LIT-2974 | Commitments and Efficient Zero-Knowledge Proofs from Learning Parity with Noise? |  |  | read |
| KN-LIT-2975 | Committed MPC |  |  | read |
| KN-LIT-2976 | Communication Complexity in Algebraic Two-Party Protocols |  |  | read |
| KN-LIT-2977 | Communication Complexity of Conditional Disclosure of Secrets and Attribute-Based Encryption |  |  | read |
| KN-LIT-2978 | Communication Efficient Secure Linear Algebra |  |  | read |
| KN-LIT-2979 | Communication Locality in Secure Multi-Party Computation How to Run Sublinear Algorithms in a Distributed Setting |  |  | read |
| KN-LIT-2980 | Communication Lower Bounds for Statistically Secure MPC, with or without Preprocessing |  |  | read |
| KN-LIT-2981 | Communication Lower Bounds of Key-Agreement Protocols via Density Increment Arguments |  |  | read |
| KN-LIT-2982 | Communication-Efficient Non-Interactive Proofs of Knowledge with Online Extractors |  |  | read |
| KN-LIT-2983 | Communication-Efficient Unconditional MPC with Guaranteed Output Delivery |  |  | read |
| KN-LIT-2984 | Commuting Signatures and Verifiable Encryption |  |  | read |
| KN-LIT-2985 | Compact Adaptively Secure ABE for NC1 from k-Lin |  |  | read |
| KN-LIT-2986 | Compact Adaptively Secure ABE from k-Lin: |  |  | read |
| KN-LIT-2987 | Compact and Tightly Selective-Opening Secure Public-key Encryption Schemes |  |  | read |
| KN-LIT-2988 | Compact CCA-Secure Encryption for Messages of Arbitrary Length |  |  | read |
| KN-LIT-2989 | Compact FE for Unbounded Attribute-Weighted Sums for Logspace from SXDH |  |  | read |
| KN-LIT-2990 | Compact Group Signatures Without Random Oracles |  |  | read |
| KN-LIT-2991 | Compact Lattice Gadget and Its Applications to Hash-and-Sign Signatures |  |  | read |
| KN-LIT-2992 | Compact Multi-Signatures for Smaller Blockchains |  |  | read |
| KN-LIT-2993 | Compact Proofs of Retrievability |  |  | read |
| KN-LIT-2994 | Compact Ring Signatures from Learning With Errors Rohit Chatterjee1 , Sanjam Garg2,3 , Mohammad Hajiabadi4 , Dakshita Khurana5 |  |  | read |
| KN-LIT-2995 | Compact Ring-LWE Cryptoprocessor Sujoy Sinha Roy1 , Frederik Vercauteren1 , Nele Mentens1 |  |  | read |
| KN-LIT-2996 | Compact Selective Opening Security From LWE |  |  | read |
| KN-LIT-2997 | Compact Structure-preserving Signatures with Almost Tight Security |  |  | read |
| KN-LIT-2998 | Compact VSS and Efficient Homomorphic UC Commitments |  |  | read |
| KN-LIT-2999 | Compact Zero-Knowledge Proofs for Threshold ECDSA with Trustless Setup |  |  | read |
| KN-LIT-3000 | Compact Zero-Knowledge Proofs of Small Hamming Weight |  |  | read |
| KN-LIT-3001 | Compact, Efficient and UC-Secure Isogeny-Based Oblivious Transfer |  |  | read |
| KN-LIT-3002 | Compactly Hiding Linear Spans Tightly Secure Constant-Size Simulation-Sound |  |  | read |
| KN-LIT-3003 | Compactness of Hashing Modes and Efficiency beyond Merkle Tree |  |  | read |
| KN-LIT-3004 | Compactness vs Collusion Resistance in Functional Encryption? |  |  | read |
| KN-LIT-3005 | Comparing Elliptic Curve Cryptography and RSA on 8-bit CPUs |  |  | read |
| KN-LIT-3006 | Comparing proofs of security for lattice-based encryption |  |  | read |
| KN-LIT-3007 | Comparing the difficulty of factorization and discrete logarithm: a 240-digit experiment? |  |  | read |
| KN-LIT-3008 | Comparing Two Notions of Simulatability |  |  | read |
| KN-LIT-3009 | Comparison between XL and Gröbner Basis Algorithms |  |  | read |
| KN-LIT-3010 | Comparison of 256-bit stream ciphers at the beginning of 2006 |  |  | read |
| KN-LIT-3011 | Comparison of Bit and Word Level Algorithms for Evaluating Unstructured Functions over Finite Rings |  |  | read |
| KN-LIT-3012 | Compiler Assisted Masking |  |  | read |
| KN-LIT-3013 | Complete addition formulas for prime order elliptic curves |  |  | read |
| KN-LIT-3014 | Complete Characterization of Broadcast and Pseudo-Signatures from Correlations |  |  | read |
| KN-LIT-3015 | Complete Characterization of Fairness in Secure Two-Party Computation of Boolean Functions? |  |  | read |
| KN-LIT-3016 | Completely Non-Malleable Encryption Revisited |  |  | read |
| KN-LIT-3017 | Completeness for Symmetric Two-Party Functionalities - Revisited? |  |  | read |
| KN-LIT-3018 | Completeness Theorems for Adaptively Secure Broadcast |  |  | read |
| KN-LIT-3019 | Completeness Theorems with Constructive Proofs for Finite Deterministic 2-Party Functions |  |  | read |
| KN-LIT-3020 | Complexity of Multi-party Computation Problems: The Case of 2-Party Symmetric Secure Function Evaluation? |  |  | read |
| KN-LIT-3021 | Composability and On-Line Deniability of Authentication |  |  | read |
| KN-LIT-3022 | Composable & Modular Anonymous Credentials: |  |  | read |
| KN-LIT-3023 | Composable Adaptive Secure Protocols without Setup under Polytime Assumptions |  |  | read |
| KN-LIT-3024 | Composable and Finite Computational Security of Quantum Message Transmission |  |  | read |
| KN-LIT-3025 | Composable Security in the Tamper-Proof Hardware Model under Minimal Complexity |  |  | read |
| KN-LIT-3026 | Composing Quantum Protocols in a Classical Environment |  |  | read |
| KN-LIT-3027 | Composition Does Not Imply Adaptive Security |  |  | read |
| KN-LIT-3028 | Composition Implies Adaptive Security in Minicrypt Krzysztof Pietrzak ? |  |  | read |
| KN-LIT-3029 | Composition of Zero-Knowledge Proofs with Efficient Provers? |  |  | read |
| KN-LIT-3030 | Composition with Knowledge Assumptions |  |  | read |
| KN-LIT-3031 | Compressed Σ-Protocol Theory and Practical Application to Plug & Play Secure Algorithmics |  |  | read |
| KN-LIT-3032 | Compressed Σ-Protocols for Bilinear Group |  |  | read |
| KN-LIT-3033 | Compressible FHE with Applications to PIR |  |  | read |
| KN-LIT-3034 | Compressing Proofs of k-Out-Of-n Partial Knowledge |  |  | read |
| KN-LIT-3035 | Compression and Information Leakage of Plaintext |  |  | read |
| KN-LIT-3036 | Compression from Collisions, or why CRHF Combiners have a Long Output Krzysztof Pietrzak |  |  | read |
| KN-LIT-3037 | COMPUTATION OF CLASSICAL AND v-ADIC L-SERIES OF t-MOTIVES XAVIER CARUSO |  |  | read |
| KN-LIT-3038 | Computation of discrete logarithms over finite fields E. Thomé |  |  | read |
| KN-LIT-3039 | Computational Extractors and Pseudorandomness |  |  | read |
| KN-LIT-3040 | Computational Hardness of Optimal Fair Computation: Beyond Minicrypt |  |  | read |
| KN-LIT-3041 | Computational Indistinguishability Amplification: Tight Product Theorems for System Composition? |  |  | read |
| KN-LIT-3042 | Computational integrity with a public random string from quasi-linear PCPs |  |  | read |
| KN-LIT-3043 | Computational Robust (Fuzzy) Extractors for CRS-dependent Sources with Minimal Min-entropy |  |  | read |
| KN-LIT-3044 | Computational Soundness of Coinductive Symbolic Security under Active Attacks |  |  | read |
| KN-LIT-3045 | Computational soundness, co-induction, and encryption cycles |  |  | read |
| KN-LIT-3046 | Computational Verifiable Secret Sharing Revisited? |  |  | read |
| KN-LIT-3047 | Computational Wiretap Coding from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-3048 | Computationally binding quantum commitments |  |  | read |
| KN-LIT-3049 | Computationally Volume-Hiding Structured Encryption |  |  | read |
| KN-LIT-3050 | Computer-aided cryptography: status and perspectives |  |  | read |
| KN-LIT-3051 | Computer-Aided Security Proofs for the Working Cryptographer |  |  | read |
| KN-LIT-3052 | COMPUTING EULER FACTORS OF GENUS 2 CURVES AT ODD PRIMES OF ALMOST GOOD REDUCTION |  |  | read |
| KN-LIT-3053 | Computing generator in cyclotomic integer rings |  |  | read |
| KN-LIT-3055 | Computing Individual Discrete Logarithms Faster in GF(pn ) with the NFS-DL Algorithm ? |  |  | read |
| KN-LIT-3056 | COMPUTING MODULAR POLYNOMIALS BY DEFORMATION |  |  | read |
| KN-LIT-3057 | Computing modular polynomials with the Chinese Remainder Theorem |  |  | read |
| KN-LIT-3058 | Computing newforms using supersingular isogeny graphs |  |  | read |
| KN-LIT-3059 | Computing on Authenticated Data: New Privacy Definitions and Constructions |  |  | read |
| KN-LIT-3060 | Computing small discrete logarithms faster |  |  | read |
| KN-LIT-3061 | Computing supersingular isogenies on Kummer surfaces |  |  | read |
| KN-LIT-3062 | Computing the algebraic immunity efficiently |  |  | read |
| KN-LIT-3063 | Computing the endomorphism ring of an ordinary elliptic curve |  |  | read |
| KN-LIT-3064 | Computing the image of Galois representations attached to elliptic curves |  |  | read |
| KN-LIT-3065 | Computing the RSA Secret Key is Deterministic |  |  | read |
| KN-LIT-3066 | COMPUTING ZETA FUNCTIONS AND L-FUNCTIONS OF CURVES CMI-HIMR SUMMER SCHOOL IN COMPUTATIONAL NUMBER THEORY (2019) |  |  | read |
| KN-LIT-3067 | Computing Zeta Functions of |  |  | read |
| KN-LIT-3068 | COMPUTING ZETA FUNCTIONS OF ALGEBRAIC CURVES |  |  | read |
| KN-LIT-3069 | Concealment and its Applications to Authenticated Encryption |  |  | read |
| KN-LIT-3070 | Concise Mercurial Vector Commitments and Independent Zero-Knowledge Sets with Short Proofs |  |  | read |
| KN-LIT-3071 | Concise Multi-Challenge CCA-Secure Encryption and Signatures with Almost Tight Security |  |  | read |
| KN-LIT-3072 | Concrete Analysis of Quantum Lattice Enumeration Shi Bai1[0000−0002−0746−3054] |  |  | read |
| KN-LIT-3073 | Concrete quantum cryptanalysis of binary elliptic curves |  |  | read |
| KN-LIT-3074 | Concurrent Asynchronous Byzantine Agreement |  |  | read |
| KN-LIT-3075 | Concurrent Error Detection Schemes for Involution Ciphers |  |  | read |
| KN-LIT-3076 | Concurrent Non-Malleable Commitments (and More) in 3 Rounds |  |  | read |
| KN-LIT-3077 | Concurrent Non-malleable Commitments from Any One-way Function |  |  | read |
| KN-LIT-3078 | Concurrent Non-Malleable Zero Knowledge Proofs ? ?? |  |  | read |
| KN-LIT-3079 | Concurrent Non-Malleable Zero Knowledge with Adaptive Inputs |  |  | read |
| KN-LIT-3080 | Concurrent Secure Computation via Non-Black Box Simulation |  |  | read |
| KN-LIT-3081 | Concurrent Secure Computation with Optimal Query Complexity |  |  | read |
| KN-LIT-3082 | Concurrent Signatures |  |  | read |
| KN-LIT-3083 | Concurrent Statistical Zero-Knowledge Arguments for NP from One Way Functions |  |  | read |
| KN-LIT-3084 | Concurrent Zero Knowledge in the Bounded Player Model |  |  | read |
| KN-LIT-3085 | Concurrent Zero Knowledge without Complexity Assumptions? |  |  | read |
| KN-LIT-3086 | Concurrently Composable Security With Shielded Super-polynomial Simulators |  |  | read |
| KN-LIT-3087 | Concurrently Secure Computation in Constant Rounds |  |  | read |
| KN-LIT-3088 | Concurrently Secure Identification Schemes Based on the Worst-Case Hardness of Lattice Problems |  |  | read |
| KN-LIT-3089 | Concurrently-Secure Blind Signatures without Random Oracles or Setup Assumptions? |  |  | read |
| KN-LIT-3090 | Conditional Computational Entropy, or Toward Separating Pseudoentropy from Compressibility |  |  | read |
| KN-LIT-3091 | Conditional Cube Attack on Reduced-Round Keccak Sponge Function |  |  | read |
| KN-LIT-3092 | Conditional Differential Cryptanalysis of NLFSR-based Cryptosystems |  |  | read |
| KN-LIT-3093 | Conditional Disclosure of Secrets via Non-Linear Reconstruction |  |  | read |
| KN-LIT-3094 | Conditional Oblivious Cast ? |  |  | read |
| KN-LIT-3095 | Confidential Signatures and Deterministic Signcryption |  |  | read |
| KN-LIT-3096 | Confidentiality and Integrity: A Constructive Perspective |  |  | read |
| KN-LIT-3097 | Consensus through Herding |  |  | read |
| KN-LIT-3098 | Consolidating Inner Product Masking Josep Balasch1 , Sebastian Faust2,3 , Benedikt Gierlichs1 |  |  | read |
| KN-LIT-3099 | Consolidating Masking Schemes Oscar Reparaz, Begül Bilgin |  |  | read |
| KN-LIT-3100 | Constant Ciphertext-Rate Non-Committing Encryption from Standard Assumptions |  |  | read |
| KN-LIT-3101 | Constant Input Attribute Based (and Predicate) Encryption from Evasive and Tensor LWE |  |  | read |
| KN-LIT-3102 | Constant Round Adaptively Secure Protocols in the Tamper-Proof Hardware Model |  |  | read |
| KN-LIT-3103 | Constant Round Authenticated Group Key Agreement via Distributed Computation ? |  |  | read |
| KN-LIT-3104 | Constant Size Ciphertexts in Threshold Attribute-Based Encryption |  |  | read |
| KN-LIT-3105 | Constant-Overhead Secure Computation of Boolean Circuits using Preprocessing |  |  | read |
| KN-LIT-3106 | Constant-Overhead Unconditionally Secure Multiparty Computation over Binary Fields |  |  | read |
| KN-LIT-3107 | Constant-Rate Oblivious Transfer from Noisy Channels |  |  | read |
| KN-LIT-3108 | Constant-Round Asynchronous |  |  | read |
| KN-LIT-3109 | Constant-Round Authenticated Group Key Exchange for Dynamic Groups ? |  |  | read |
| KN-LIT-3110 | Constant-Round Black-Box Construction of Composable Multi-Party Computation Protocol |  |  | read |
| KN-LIT-3111 | Constant-round Blind Classical Verification of Quantum Sampling |  |  | read |
| KN-LIT-3112 | Constant-Round Concurrent Non-Malleable |  |  | read |
| KN-LIT-3113 | Constant-Round Concurrent Zero Knowledge in the Bounded Player Model |  |  | read |
| KN-LIT-3114 | Constant-Round Concurrent Zero-knowledge from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-3115 | Constant-round Leakage-resilient Zero-knowledge from Collision Resistance |  |  | read |
| KN-LIT-3116 | Constant-Round Maliciously Secure Two-Party Computation in the RAM Model ? ?? |  |  | read |
| KN-LIT-3117 | Constant-Round MPC with Fairness and Guarantee of Output Delivery |  |  | read |
| KN-LIT-3118 | Constant-Round Multi-Party Private Set Union Using Reversed Laurent Series |  |  | read |
| KN-LIT-3119 | Constant-Round Multiparty Computation Using a Black-Box Pseudorandom Generator |  |  | read |
| KN-LIT-3120 | Constant-Round Non-Malleable Commitments from Sub-Exponential One-Way Functions |  |  | read |
| KN-LIT-3121 | Constant-Round Private Function Evaluation with Linear Complexity |  |  | read |
| KN-LIT-3122 | Constant-Size Commitments to Polynomials and Their Applications? |  |  | read |
| KN-LIT-3123 | Constant-size Group Signatures from Lattices |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3124 | Constant-Size Structure-Preserving Signatures |  |  | read |
| KN-LIT-3125 | Constrained PRFs for NC1 in |  |  | read |
| KN-LIT-3126 | Constrained Pseudorandom Functions and Their Applications ? |  |  | read |
| KN-LIT-3127 | Constrained Pseudorandom Functions for Unconstrained Inputs |  |  | read |
| KN-LIT-3128 | Constrained Pseudorandom Functions for Unconstrained Inputs Revisited: Achieving |  |  | read |
| KN-LIT-3129 | Constrained Pseudorandom Functions from Homomorphic Secret Sharing |  |  | read |
| KN-LIT-3130 | Constraining and Watermarking PRFs from Milder Assumptions |  |  | read |
| KN-LIT-3131 | Constraint-Hiding Constrained PRFs for NC1 from LWE |  |  | read |
| KN-LIT-3132 | Constructing and Deconstructing Intentional Weaknesses in Symmetric Ciphers |  |  | read |
| KN-LIT-3133 | Constructing and Understanding Chosen Ciphertext Security via Puncturable Key Encapsulation Mechanisms |  |  | read |
| KN-LIT-3134 | Constructing Committed Signatures From Strong-RSA Assumption In The Standard |  |  | read |
| KN-LIT-3135 | Constructing Confidential Channels from Authenticated Channels—Public-Key Encryption Revisited |  |  | read |
| KN-LIT-3136 | Constructing Cryptographic Hash Functions from Fixed-Key Blockciphers |  |  | read |
| KN-LIT-3137 | Constructing Ideal Secret Sharing Schemes based on Chinese Remainder Theorem? |  |  | read |
| KN-LIT-3138 | Constructing Locally Leakage-resilient Linear Secret-sharing Schemes |  |  | read |
| KN-LIT-3139 | Constructing Rate-1 MACs from Related-Key |  |  | read |
| KN-LIT-3140 | Constructing S-boxes for lightweight cryptography with Feistel structure |  |  | read |
| KN-LIT-3141 | Constructing Verifiable Random Functions with Large Input Spaces |  |  | read |
| KN-LIT-3142 | Construction and Analysis of Boolean Functions of 2t + 1 Variables with Maximum Algebraic Immunity ? |  |  | read |
| KN-LIT-3143 | Construction of a Non-Malleable Encryption Scheme from Any Semantically Secure One |  |  | read |
| KN-LIT-3144 | Construction of Differential Characteristics in ARX Designs |  |  | read |
| KN-LIT-3145 | Construction of Universal Designated-Verifier Signatures and Identity-Based Signatures from Standard Signatures |  |  | read |
| KN-LIT-3146 | Constructive Post-Quantum Reductions |  |  | read |
| KN-LIT-3147 | Contemporary Mathematics |  | Contemporary Mathematics | read |
| KN-LIT-3148 | Contemporary Mathematics Analysis and optimization of elliptic-curve single-scalar multiplication |  | Contemporary Mathematics | read |
| KN-LIT-3149 | Contention in Cryptoland: Obfuscation, Leakage and UCE |  |  | read |
| KN-LIT-3150 | Context Discovery and Commitment Attacks |  |  | read |
| KN-LIT-3151 | Continuous Group Key Agreement with Active Security |  |  | read |
| KN-LIT-3152 | Continuous Non-malleable Codes 2 1 |  |  | read |
| KN-LIT-3153 | Continuous Non-Malleable Codes in the 8-Split-State Model ? |  |  | read |
| KN-LIT-3154 | Continuous Non-Malleable Key Derivation and Its Application to Related-Key Security |  |  | read |
| KN-LIT-3155 | Continuous Verifiable Delay Functions |  |  | read |
| KN-LIT-3156 | Continuously Non-Malleable Codes against Bounded-Depth Tampering |  |  | read |
| KN-LIT-3157 | ConTra Corona: Contact Tracing against the Coronavirus by Bridging the Centralized–Decentralized Divide for Stronger Privacy |  |  | read |
| KN-LIT-3158 | Controlling Access to an Oblivious Database using Stateful Anonymous Credentials |  |  | read |
| KN-LIT-3159 | Converse Results to the Wiener Attack on RSA |  |  | read |
| KN-LIT-3160 | Conversion from Arithmetic to Boolean Masking with Logarithmic Complexity |  |  | read |
| KN-LIT-3161 | Conversions among Several Classes of Predicate Encryption and Applications to ABE with Various Compactness Tradeoffs |  |  | read |
| KN-LIT-3162 | Converting Cryptographic Schemes from Symmetric to Asymmetric Bilinear Groups |  |  | read |
| KN-LIT-3163 | Converting Meet-in-the-Middle Preimage Attack into Pseudo Collision Attack: |  |  | read |
| KN-LIT-3164 | Converting Pairing-Based Cryptosystems from Composite-Order Groups to Prime-Order Groups |  |  | read |
| KN-LIT-3165 | Convexity of division property transitions: |  |  | read |
| KN-LIT-3166 | Convolutional Neural Networks with Data Augmentation against Jitter-Based Countermeasures – Profiling Attacks without Pre-Processing |  |  | read |
| KN-LIT-3167 | Coordinate Blinding over Large Prime Fields |  |  | read |
| KN-LIT-3168 | Correcting Errors in RSA Private Keys |  |  | read |
| KN-LIT-3169 | Correcting Subverted Random Oracles |  |  | read |
| KN-LIT-3170 | Correlated Extra-Reductions Defeat |  |  | read |
| KN-LIT-3171 | Correlated Product Security From Any One-Way Function |  |  | read |
| KN-LIT-3172 | Correlated Pseudorandomness from Expand-Accumulate Codes |  |  | read |
| KN-LIT-3173 | Correlated Pseudorandomness from the |  |  | read |
| KN-LIT-3174 | Correlated-Input Secure Hash Functions |  |  | read |
| KN-LIT-3175 | Correlated-Source Extractors and Cryptography with Correlated-Random Tapes? |  |  | read |
| KN-LIT-3176 | Correlation attacks using a new class of weak feedback polynomials |  |  | read |
| KN-LIT-3177 | Correlation Cube Attack Revisited |  |  | read |
| KN-LIT-3178 | Correlation Cube Attacks: From Weak-Key Distinguisher to Key Recovery? |  |  | read |
| KN-LIT-3179 | Correlation Intractability and SNARGs from Sub-exponential DDH Arka Rai Choudhuri1[0000−0003−0452−3426] |  |  | read |
| KN-LIT-3180 | Correlation of Quadratic Boolean Functions: Cryptanalysis of All Versions of Full MORUS |  |  | read |
| KN-LIT-3181 | Correlation Power Analysis with a Leakage Model |  |  | read |
| KN-LIT-3182 | Correlation-Enhanced Power Analysis Collision Attack |  |  | read |
| KN-LIT-3183 | Cost analysis of hash collisions: Will quantum computers make SHARCS obsolete? |  |  | read |
| KN-LIT-3184 | Count Me In! Extendability for Threshold Ring Signatures Diego F. Aranha1 , Mathias Hall-Andersen1 , Anca Nitulescu3 |  |  | read |
| KN-LIT-3185 | Counter-cryptanalysis Marc Stevens |  |  | read |
| KN-LIT-3186 | Counter-in-Tweak: Authenticated Encryption Modes for Tweakable Block Ciphers |  |  | read |
| KN-LIT-3187 | Counterexamples to Hardness Amplification Beyond Negligible |  |  | read |
| KN-LIT-3188 | Counterexamples to New Circular Security Assumptions Underlying iO |  |  | read |
| KN-LIT-3189 | Counting Keys in Parallel After a Side Channel Attack |  |  | read |
| KN-LIT-3190 | Counting Points on Elliptic Curves over Finite Fields of Small Characteristic in Quasi Quadratic Time |  |  | read |
| KN-LIT-3191 | Counting Points on Genus 2 Curves with Real Multiplication |  |  | read |
| KN-LIT-3192 | Counting points on modular curves |  |  | read |
| KN-LIT-3193 | COUNTING POINTS ON SMOOTH PLANE QUARTICS |  |  | read |
| KN-LIT-3194 | Counting Unpredictable Bits: A Simple PRG from One-way Functions |  |  | read |
| KN-LIT-3195 | Counting Vampires: From Univariate Sumcheck to Updatable ZK-SNARK |  |  | read |
| KN-LIT-3196 | Coupling of Random Systems |  |  | read |
| KN-LIT-3197 | Cover and Decomposition Index Calculus on Elliptic Curves made practical |  |  | read |
| KN-LIT-3198 | Covert Learning: How to Learn with an Untrusted Intermediary? |  |  | read |
| KN-LIT-3199 | Covert Security with Public Verifiability: |  |  | read |
| KN-LIT-3200 | CP-ABE for Circuits (and more) in the Symmetric Key Setting |  |  | read |
| KN-LIT-3201 | CPA-to-CCA Transformation for KDM Security |  |  | read |
| KN-LIT-3202 | CRAFT: Composable Randomness Beacons and |  |  | read |
| KN-LIT-3203 | Cramer-Damgård Signatures Revisited: Efficient Flat-Tree Signatures Based on Factoring |  |  | read |
| KN-LIT-3204 | Credential Authenticated Identification and Key Exchange |  |  | read |
| KN-LIT-3205 | Credibility in Private Set Membership Sanjam Garg1,2 , Mohammad Hajiabadi3 , Abhishek Jain4 , Zhengzhong Jin5 |  |  | read |
| KN-LIT-3206 | Critical Points of Toroidal Belyı̆ Maps |  |  | read |
| KN-LIT-3207 | Crowd Verifiable Zero-Knowledge and End-to-end Verifiable Multiparty Computation |  |  | read |
| KN-LIT-3208 | Crowd-Blending Privacy |  |  | read |
| KN-LIT-3209 | Cryptanalyses of Branching Program Obfuscations over GGH13 Multilinear Map from the NTRU Problem |  |  | read |
| KN-LIT-3210 | Cryptanalyses of Candidate Branching Program Obfuscators |  |  | read |
| KN-LIT-3211 | Cryptanalyses on a Merkle-Damgård Based MAC — Almost Universal Forgery and Distinguishing-H Attacks |  |  | read |
| KN-LIT-3212 | Cryptanalysis of |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3213 | Cryptanalysis of 2R− schemes |  |  | read |
| KN-LIT-3214 | Cryptanalysis of 3-pass HAVAL? |  |  | read |
| KN-LIT-3215 | Cryptanalysis of a Message Authentication Code |  |  | read |
| KN-LIT-3216 | Cryptanalysis of a Public-key Encryption Scheme Based on the Polynomial Reconstruction Problem Jean-Sébastien Coron |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3217 | Cryptanalysis of a Theorem: Decomposing the Only Known Solution to the Big APN Problem Léo Perrin1( ) |  |  | read |
| KN-LIT-3218 | Cryptanalysis of Achterbahn |  |  | read |
| KN-LIT-3219 | Cryptanalysis of Achterbahn-128/80 María Naya-Plasencia? |  |  | read |
| KN-LIT-3220 | Cryptanalysis of an Efficient Proof of Knowledge of Discrete Logarithm |  |  | read |
| KN-LIT-3221 | Cryptanalysis of an oblivious |  |  | read |
| KN-LIT-3222 | Cryptanalysis of ARMADILLO2 |  |  | read |
| KN-LIT-3223 | Cryptanalysis of Block Ciphers with Overdefined Systems of Equations |  |  | read |
| KN-LIT-3224 | Cryptanalysis of C2 |  |  | read |
| KN-LIT-3225 | Cryptanalysis of Candidate Obfuscators for Affine Determinant Programs |  |  | read |
| KN-LIT-3226 | Cryptanalysis of CLT13 Multilinear Maps with Independent Slots |  |  | read |
| KN-LIT-3227 | Cryptanalysis of Cryptosystems Based on Non-commutative Skew Polynomials |  |  | read |
| KN-LIT-3228 | Cryptanalysis of ESSENCE |  |  | read |
| KN-LIT-3229 | Cryptanalysis of FIDES |  |  | read |
| KN-LIT-3230 | Cryptanalysis of FORK-256 |  |  | read |
| KN-LIT-3231 | Cryptanalysis of Full LowMC and LowMC-M with Algebraic Techniques |  |  | read |
| KN-LIT-3232 | Cryptanalysis of Full RIPEMD-128 |  |  | read |
| KN-LIT-3233 | Cryptanalysis of Full Sprout |  |  | read |
| KN-LIT-3234 | Cryptanalysis of G RINDAHL Thomas Peyrin |  |  | read |
| KN-LIT-3235 | Cryptanalysis of GGH Map |  |  | read |
| KN-LIT-3236 | Cryptanalysis of GGH15 Multilinear Maps Jean-Sébastien |  |  | read |
| KN-LIT-3237 | Cryptanalysis of Group-based Key Agreement Protocols Using Subgroup Distance Functions |  |  | read |
| KN-LIT-3238 | Cryptanalysis of GSM Encryption in 2G/3G Networks without Rainbow Tables |  |  | read |
| KN-LIT-3239 | Cryptanalysis of HFE with Internal Perturbation |  |  | read |
| KN-LIT-3240 | Cryptanalysis of HFEv and internal perturbation of HFE |  |  | read |
| KN-LIT-3241 | Cryptanalysis of HMAC/NMAC-Whirlpool |  |  | read |
| KN-LIT-3242 | Cryptanalysis of JAMBU |  |  | read |
| KN-LIT-3243 | Cryptanalysis of KLEIN |  |  | read |
| KN-LIT-3244 | Cryptanalysis of LEDAcrypt |  |  | read |
| KN-LIT-3245 | Cryptanalysis of Masked Ciphers: A not so Random Idea |  |  | read |
| KN-LIT-3246 | Cryptanalysis of MDC-2? |  |  | read |
| KN-LIT-3247 | Cryptanalysis of MinRank |  |  | read |
| KN-LIT-3248 | Cryptanalysis of Multivariate and Odd-Characteristic HFE Variants |  |  | read |
| KN-LIT-3249 | Cryptanalysis of OCB2: Attacks on Authenticity and Confidentiality |  |  | read |
| KN-LIT-3250 | Cryptanalysis of PRESENT-like Ciphers with Secret S-boxes |  |  | read |
| KN-LIT-3251 | Cryptanalysis of RadioGatún |  |  | read |
| KN-LIT-3252 | Cryptanalysis of Reduced NORX |  |  | read |
| KN-LIT-3253 | Cryptanalysis of Round-Reduced LED |  |  | read |
| KN-LIT-3254 | Cryptanalysis of RSA Signatures with Fixed-Pattern Padding |  |  | read |
| KN-LIT-3255 | Cryptanalysis of SAFER++? |  |  | read |
| KN-LIT-3256 | Cryptanalysis of SFLASH |  |  | read |
| KN-LIT-3257 | Cryptanalysis of SFLASH with Slightly Modified Parameters |  |  | read |
| KN-LIT-3258 | Cryptanalysis of Sober-t32 |  |  | read |
| KN-LIT-3259 | Cryptanalysis of Sosemanuk and SNOW 2.0 Using Linear Masks |  |  | read |
| KN-LIT-3260 | Cryptanalysis of stream ciphers with linear masking |  |  | read |
| KN-LIT-3261 | Cryptanalysis of Symmetric Primitives over Rings and a Key Recovery Attack on Rubato |  |  | read |
| KN-LIT-3262 | Cryptanalysis of the |  |  | read |
| KN-LIT-3263 | Cryptanalysis of the DECT Standard Cipher |  |  | read |
| KN-LIT-3264 | Cryptanalysis of the EMD Mode of Operation |  |  | read |
| KN-LIT-3265 | Cryptanalysis of the FLIP Family of Stream Ciphers |  |  | read |
| KN-LIT-3266 | Cryptanalysis of the Full Spritz Stream Cipher |  |  | read |
| KN-LIT-3267 | Cryptanalysis of the GPRS Encryption |  |  | read |
| KN-LIT-3268 | Cryptanalysis of the ISDB Scrambling Algorithm (MULTI2) |  |  | read |
| KN-LIT-3269 | Cryptanalysis of the Knapsack Generator |  |  | read |
| KN-LIT-3270 | Cryptanalysis of the LAKE Hash Family |  |  | read |
| KN-LIT-3271 | Cryptanalysis of The Lifted Unbalanced Oil Vinegar Signature Scheme |  |  | read |
| KN-LIT-3272 | Cryptanalysis of the Modified Version of the Hash Function Proposed at PKC’98 |  |  | read |
| KN-LIT-3273 | Cryptanalysis of the Multilinear Map over the Integers |  |  | read |
| KN-LIT-3274 | Cryptanalysis of the New CLT Multilinear Map over the Integers |  |  | read |
| KN-LIT-3275 | Cryptanalysis of the NTRU Signature Scheme (NSS) from Eurocrypt 2001 |  |  | read |
| KN-LIT-3276 | Cryptanalysis of the Paeng-Jung-Ha Cryptosystem from PKC 2003 |  |  | read |
| KN-LIT-3277 | Cryptanalysis of the Peregrine |  |  | read |
| KN-LIT-3278 | Cryptanalysis of the Public-Key Encryption Based on Braid Groups |  |  | read |
| KN-LIT-3279 | Cryptanalysis of the Revised NTRU Signature Scheme |  |  | read |
| KN-LIT-3280 | Cryptanalysis of the RSA Subgroup Assumption from TCC 2005 |  |  | read |
| KN-LIT-3281 | Cryptanalysis of the Sidelnikov cryptosystem |  |  | read |
| KN-LIT-3282 | Cryptanalysis of the Square Cryptosystems |  |  | read |
| KN-LIT-3283 | Cryptanalysis of the Tiger Hash Function? |  |  | read |
| KN-LIT-3284 | Cryptanalysis of the Tractable Rational Map Cryptosystem |  |  | read |
| KN-LIT-3285 | Cryptanalysis of Unbalanced RSA with Small CRT-Exponent |  |  | read |
| KN-LIT-3286 | Cryptanalysis of WIDEA |  |  | read |
| KN-LIT-3287 | Cryptanalysis on HMAC/NMAC-MD5 and MD5-MAC? |  |  | read |
| KN-LIT-3288 | Cryptanalysis Results on Spook Bringing Full-round Shadow-512 to the |  |  | read |
| KN-LIT-3289 | Cryptanalysis via algebraic spans |  |  | read |
| KN-LIT-3290 | Cryptanalytic Applications of the Polynomial Method for Solving Multivariate Equation Systems over GF(2) |  |  | read |
| KN-LIT-3291 | Cryptanalytic Extraction of Neural Network Models |  |  | read |
| KN-LIT-3292 | Cryptanalytic Time-Memory-Data Tradeoffs for FX-Constructions with Applications to PRINCE and PRIDE Itai Dinur |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3293 | CryptAttackTester: formalizing attack analyses |  |  | read |
| KN-LIT-3294 | Crypto Engineering: Some History and Some Case Studies |  |  | read |
| KN-LIT-3295 | Crypto-Integrity |  |  | read |
| KN-LIT-3296 | Cryptographic Agents: Towards a Unified Theory of Computing on Encrypted Data |  |  | read |
| KN-LIT-3297 | Cryptographic Agility and its Relation to Circular Encryption |  |  | read |
| KN-LIT-3298 | Cryptographic Analysis of the Bluetooth Secure Connection Protocol Suite |  |  | read |
| KN-LIT-3299 | Cryptographic applications of capacity theory: On the optimality of Coppersmith’s method for univariate polynomials |  |  | read |
| KN-LIT-3300 | Cryptographic competitions |  |  | read |
| KN-LIT-3301 | Cryptographic Complexity of Multi-party Computation Problems: Classifications and Separations |  |  | read |
| KN-LIT-3302 | Cryptographic Group Actions and Applications |  |  | read |
| KN-LIT-3303 | Cryptographic Hardness of Random Local Functions – Survey |  |  | read |
| KN-LIT-3304 | Cryptographic Hash-Function Basics: Definitions, Implications, and Separations for Preimage Resistance, Second-Preimage Resistance, and Collision Resistance |  |  | read |
| KN-LIT-3305 | CRYPTOGRAPHIC IMPLICATIONS OF HESS’ GENERALIZED GHS ATTACK |  |  | read |
| KN-LIT-3306 | Cryptographic Primitives with Hinting Property |  |  | read |
| KN-LIT-3307 | Cryptographic Protocols for Electronic Voting |  |  | read |
| KN-LIT-3308 | Cryptographic Pseudorandom Generators Can |  |  | read |
| KN-LIT-3309 | Cryptographic Reverse Firewall via Malleable Smooth Projective Hash Functions |  |  | read |
| KN-LIT-3310 | Cryptographic Reverse Firewalls 1,? |  |  | read |
| KN-LIT-3311 | Cryptographic Schemes Based on the ASASA Structure: Black-box, White-box, and Public-key |  |  | read |
| KN-LIT-3312 | Cryptographic Sensing |  |  | read |
| KN-LIT-3313 | Cryptographic Shallots: A Formal Treatment of Repliable Onion Encryption |  |  | read |
| KN-LIT-3314 | Cryptographic Smooth Neighbors |  |  | read |
| KN-LIT-3315 | Cryptographic Test Correction |  |  | read |
| KN-LIT-3316 | Cryptographically Significant Boolean functions: Construction and Analysis in terms of Algebraic Immunity |  |  | read |
| KN-LIT-3317 | Cryptography and Game Theory: Designing Protocols for Exchanging Information? |  |  | read |
| KN-LIT-3318 | Cryptography between Wonderland and Underland |  |  | read |
| KN-LIT-3319 | Cryptography from Compression Functions: The UCE Bridge to the ROM |  |  | read |
| KN-LIT-3320 | Cryptography from One-Way Communication: On Completeness of Finite Channels |  |  | read |
| KN-LIT-3321 | Cryptography from Planted Graphs: Security with Logarithmic-Size Messages Damiano Abram1[0009−0004−3916−7550] , Amos Beimel2[0000−0002−6572−4195] |  |  | read |
| KN-LIT-3322 | Cryptography from Pseudorandom Quantum States |  |  | read |
| KN-LIT-3323 | Cryptography in an Unbounded Computational Model |  |  | read |
| KN-LIT-3324 | Cryptography in NaCl |  |  | read |
| KN-LIT-3325 | Cryptography in Subgroups of Zn |  |  | read |
| KN-LIT-3326 | Cryptography in the Multi-string Model |  |  | read |
| KN-LIT-3327 | Cryptography in Theory and Practice: The Case of Encryption in IPsec |  |  | read |
| KN-LIT-3328 | Cryptography Secure Against |  |  | read |
| KN-LIT-3329 | Cryptography Using Captcha Puzzles |  |  | read |
| KN-LIT-3330 | Cryptography with Auxiliary Input and Trapdoor from Constant-Noise LPN |  |  | read |
| KN-LIT-3331 | Cryptography with Certified Deletion |  |  | read |
| KN-LIT-3332 | Cryptography with Constant Input Locality? |  |  | read |
| KN-LIT-3333 | Cryptography with One-Way Communication |  |  | read |
| KN-LIT-3334 | Cryptography with Streaming Algorithms |  |  | read |
| KN-LIT-3335 | Cryptography with Tamperable and Leaky Memory |  |  | read |
| KN-LIT-3336 | Cryptography with Updates |  |  | read |
| KN-LIT-3337 | Cryptography with Weights: MPC |  |  | read |
| KN-LIT-3338 | Cryptography Without (Hardly Any) Secrets ? |  |  | read |
| KN-LIT-3339 | CSI-FiSh: Efficient Isogeny based Signatures through Class Group Computations |  |  | read |
| KN-LIT-3340 | CSIDH: An Efficient |  |  | read |
| KN-LIT-3341 | CTIDH: faster constant-time |  |  | read |
| KN-LIT-3342 | Cube Attacks and Cube-attack-like Cryptanalysis on the Round-reduced Keccak Sponge Function |  |  | read |
| KN-LIT-3343 | Cube Attacks on Non-Blackbox Polynomials Based on Division Property |  |  | read |
| KN-LIT-3344 | Cube Attacks on Tweakable Black Box Polynomials |  |  | read |
| KN-LIT-3345 | Cube Testers and Key Recovery Attacks |  |  | read |
| KN-LIT-3346 | Cuckoo Commitments: Registration-Based Encryption and Key-Value Map Commitments for Large Spaces |  |  | read |
| KN-LIT-3347 | Cuckoo Hashing in Cryptography: Optimal Parameters, Robustness and Applications Kevin Yeo |  |  | read |
| KN-LIT-3348 | Curious case of Rowhammer: Flipping Secret Exponent Bits using Timing Analysis |  |  | read |
| KN-LIT-3349 | Curve41417: Karatsuba revisited |  |  | read |
| KN-LIT-3350 | Cutting-Edge Cryptography Through the Lens of Secret Sharing |  |  | read |
| KN-LIT-3351 | Cycle counts for authenticated encryption |  |  | read |
| KN-LIT-3352 | Cycle Slicer: An Algorithm for Building Permutations on Special Domains |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3353 | DAG-Σ: A DAG-based Sigma Protocol for Relations in CNF |  |  | read |
| KN-LIT-3354 | Data Is a Stream: Security of Stream-Based Channels |  |  | read |
| KN-LIT-3355 | Data-Independent Memory Hard Functions: |  |  | read |
| KN-LIT-3356 | David and Goliath Commitments: UC Computation for Asymmetric Parties Using Tamper-Proof Hardware |  |  | read |
| KN-LIT-3357 | DDH-like Assumptions Based on Extension Rings |  |  | read |
| KN-LIT-3358 | Decaf: Eliminating cofactors through point compression |  |  | read |
| KN-LIT-3359 | Decentralized Anonymous Micropayments? |  |  | read |
| KN-LIT-3360 | Decentralized Attribute-Based Signatures |  |  | read |
| KN-LIT-3361 | Decentralized Multi-Authority ABE for DNFs from LWE |  |  | read |
| KN-LIT-3362 | Decentralized Multi-Authority Attribute-Based Inner-Product FE: Large Universe and Unbounded |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3363 | Decentralized Multi-Client |  |  | read |
| KN-LIT-3364 | Decentralizing Attribute-Based Encryption |  |  | read |
| KN-LIT-3365 | Decentralizing Inner-Product Functional Encryption |  |  | read |
| KN-LIT-3366 | Decisional second-preimage resistance: When does SPR imply PRE? |  |  | read |
| KN-LIT-3367 | Decoding Random Binary Linear Codes in 2n/20 : How 1 + 1 = 0 Improves Information Set Decoding |  |  | read |
| KN-LIT-3368 | Decoding Random Linear Codes in Õ(20.054n ) |  |  | read |
| KN-LIT-3369 | Decryption Failure Attacks on IND-CCA Secure Lattice-Based Schemes Jan-Pieter D’Anvers1 |  |  | read |
| KN-LIT-3370 | DEFAULT: Cipher Level Resistance Against Differential Fault Attack |  |  | read |
| KN-LIT-3371 | Defeating Countermeasures Based on Randomized BSD Representations |  |  | read |
| KN-LIT-3372 | Degenerate Curve Attacks Extending Invalid Curve Attacks to |  |  | read |
| KN-LIT-3373 | Degradation and Amplification of Computational Hardness |  |  | read |
| KN-LIT-3374 | Degree Evaluation of NFSR-Based Cryptosystems? |  |  | read |
| KN-LIT-3375 | Degree of Composition of Highly Nonlinear |  |  | read |
| KN-LIT-3376 | Degree-D Reverse Multiplication-Friendly Embeddings: Constructions and Applications |  |  | read |
| KN-LIT-3377 | Delay Encryption |  |  | read |
| KN-LIT-3378 | Delayed-Key Message Authentication for Streams |  |  | read |
| KN-LIT-3379 | Delegatable Functional Signatures |  |  | read |
| KN-LIT-3380 | Delegating Quantum Computation in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-3381 | Delegating RAM Computations with Adaptive Soundness and Privacy? |  |  | read |
| KN-LIT-3382 | Deniable Fully Homomorphic Encryption from Learning With Errors |  |  | read |
| KN-LIT-3383 | Deniable Functional Encryption |  |  | read |
| KN-LIT-3384 | Deniable Ring Authentication? |  |  | read |
| KN-LIT-3385 | Depth-Robust Graphs and Their Cumulative Memory Complexity |  |  | read |
| KN-LIT-3386 | Derandomization in Cryptography |  |  | read |
| KN-LIT-3387 | Design and analysis of a distributed ECDSA signing service |  |  | read |
| KN-LIT-3388 | Design and Analysis of Practical Public-Key Encryption Schemes Secure against Adaptive Chosen Ciphertext Attack |  |  | read |
| KN-LIT-3389 | Design in Type-I, Run in Type-III: Fast and Scalable Bilinear-Type Conversion using Integer Programming |  |  | read |
| KN-LIT-3390 | Design of Testable Random Bit Generators |  |  | read |
| KN-LIT-3391 | Design Principles for HFEv- based Multivariate |  |  | read |
| KN-LIT-3392 | Design Strategies for ARX with Provable Bounds: |  |  | read |
| KN-LIT-3393 | Designated Con rmer Signatures Revisited? |  |  | read |
| KN-LIT-3394 | Designated Verifier/Prover and Preprocessing NIZKs from Diffie-Hellman Assumptions |  |  | read |
| KN-LIT-3395 | Designated-verifier pseudorandom generators, and their applications |  |  | read |
| KN-LIT-3396 | Designing an ASIP for Cryptographic Pairings over Barreto-Naehrig Curves ? |  |  | read |
| KN-LIT-3397 | Designing Proof of Human-work Puzzles for Cryptocurrency and Beyond |  |  | read |
| KN-LIT-3398 | Destroying Fault Invariant with Randomization -A Countermeasure for AES against Differential Fault Attacks |  |  | read |
| KN-LIT-3399 | Detect, Pack and Batch: Perfectly-Secure MPC with Linear |  |  | read |
| KN-LIT-3400 | Detecting Dangerous Queries: A New Approach for Chosen Ciphertext Security |  |  | read |
| KN-LIT-3401 | Detecting flawed masking schemes with leakage detection tests |  |  | read |
| KN-LIT-3402 | Determining the Core Primitive for Optimally Secure Ratcheting? |  |  | read |
| KN-LIT-3403 | Deterministic and Efficiently Searchable Encryption |  |  | read |
| KN-LIT-3404 | Deterministic Polynomial Time Equivalence between Factoring and Key-Recovery Attack on Takagi’s RSA |  |  | read |
| KN-LIT-3405 | Deterring Certificate Subversion: Efficient Double-Authentication-Preventing Signatures |  |  | read |
| KN-LIT-3406 | Developing a Hardware Evaluation Method for SHA-3 Candidates |  |  | read |
| KN-LIT-340675 | Differential Fault Attack on ML-DSA using Coefficients Computable from Public Information | 2026 | IACR ePrint 2026/1344 | partial |
| KN-LIT-3407 | Dew: A Transparent Constant-sized Polynomial Commitment Scheme |  |  | read |
| KN-LIT-3408 | Déjà Q All Over Again: Tighter and Broader Reductions of q-Type Assumptions |  |  | read |
| KN-LIT-3409 | Déjà Q: Encore! Un Petit IBE |  |  | read |
| KN-LIT-3410 | Déjà Q: Using Dual Systems to Revisit q-Type Assumptions |  |  | read |
| KN-LIT-3411 | Differential addition chains |  |  | read |
| KN-LIT-3412 | Differential Analysis of the LED Block Cipher |  |  | read |
| KN-LIT-3413 | Differential and invertibility properties of BLAKE |  |  | read |
| KN-LIT-3414 | Differential and Linear Cryptanalysis of a Reduced-Round SC2000 |  |  | read |
| KN-LIT-3415 | Differential Behavioral Analysis |  |  | read |
| KN-LIT-3416 | Differential Computation Analysis: Hiding your White-Box Designs is Not Enough |  |  | read |
| KN-LIT-3417 | Differential Cryptanalysis in the Fixed-Key Model |  |  | read |
| KN-LIT-3418 | Differential Cryptanalysis of |  |  | read |
| KN-LIT-3419 | Differential Cryptanalysis of Round-Reduced PRINTcipher: Computing Roots of Permutations |  |  | read |
| KN-LIT-3420 | Differential Cryptanalysis of the Stream Ciphers |  |  | read |
| KN-LIT-3421 | Differential Fault Analysis of Trivium |  |  | read |
| KN-LIT-3422 | Differential Fault Analysis on DES Middle Rounds |  |  | read |
| KN-LIT-3423 | Differential Meet-In-The-Middle Cryptanalysis |  |  | read |
| KN-LIT-3424 | Differential Privacy with Imperfect Randomness |  |  | read |
| KN-LIT-3425 | Differential propagation analysis of Keccak |  |  | read |
| KN-LIT-3426 | Differential-Linear Approximation |  |  | read |
| KN-LIT-3427 | Differential-Linear Attacks against the Stream Cipher Phelix? |  |  | read |
| KN-LIT-3428 | Differential-Linear Cryptanalysis from an Algebraic Perspective? |  |  | read |
| KN-LIT-3429 | Differential-Linear Cryptanalysis of ICEPOLE |  |  | read |
| KN-LIT-3430 | Differential-Linear Cryptanalysis of Serpent? |  |  | read |
| KN-LIT-3431 | Differential-Linear Cryptanalysis Revisited |  |  | read |
| KN-LIT-3432 | Digital Signatures Based on the Hardness of Ideal Lattice Problems in all Rings |  |  | read |
| KN-LIT-3433 | Digital Signatures from Strong RSA without Prime Generation |  |  | read |
| KN-LIT-3434 | Digital Signatures with Memory-Tight Security in the Multi-Challenge Setting |  |  | read |
| KN-LIT-3435 | Dining Cryptographers Revisited |  |  | read |
| KN-LIT-3436 | Direct Construction of Recursive MDS Diffusion Layers using Shortened BCH Codes |  |  | read |
| KN-LIT-3437 | Direct Product Hardness Amplification |  |  | read |
| KN-LIT-3438 | Disappearing Cryptography in the Bounded Storage Model |  |  | read |
| KN-LIT-3439 | Discrete Gaussian Leftover Hash Lemma over Infinite Domains |  |  | read |
| KN-LIT-3440 | Discrete logarithm in GF(2809 ) with FFS Razvan Barbulescu, Cyril Bouvier, Jérémie Detrey, Pierrick Gaudry |  |  | read |
| KN-LIT-3441 | Discrete-Log-Based Signatures May Not Be Equivalent to Discrete Log |  |  | read |
| KN-LIT-3442 | Discretization Error Reduction for High Precision Torus Fully Homomorphic Encryption |  |  | read |
| KN-LIT-3443 | Dishonest Majority Multi-Party Computation for Binary Circuits |  |  | read |
| KN-LIT-3444 | Disjunctions for Hash Proof Systems: |  |  | read |
| KN-LIT-3445 | Disorientation faults in |  |  | read |
| KN-LIT-3446 | Dissection-BKW Andre Esser1 , Felix Heuer1 , Robert Kübler1 |  |  | read |
| KN-LIT-3447 | Distinguisher and Related-Key Attack on the Full AES-256 |  |  | read |
| KN-LIT-3448 | Distinguisher-Dependent Simulation in |  |  | read |
| KN-LIT-3449 | Distinguishing attacks on SOBER-t16 and t32 |  |  | read |
| KN-LIT-3450 | Distributed (Correlation) Samplers: How to Remove a Trusted Dealer in One Round? |  |  | read |
| KN-LIT-3451 | Distributed Broadcast Encryption from Bilinear Groups |  |  | read |
| KN-LIT-3452 | Distributed Differential Privacy via Shuffling Albert Cheu1(B) |  |  | read |
| KN-LIT-3453 | Distributed Merkle’s Puzzles |  |  | read |
| KN-LIT-3454 | Distributed Oblivious RAM for Secure Two-Party Computation? |  |  | read |
| KN-LIT-3455 | Distributed Public-Key Cryptography from Weak Secrets |  |  | read |
| KN-LIT-3456 | Distributed-Prover Interactive Proofs |  |  | read |
| KN-LIT-3457 | Distributional Collision Resistance Beyond One-Way Functions |  |  | read |
| KN-LIT-3458 | Divisible E-Cash from Constrained Pseudo-Random Functions |  |  | read |
| KN-LIT-3459 | DLCT: A New Tool for Differential-Linear Cryptanalysis |  |  | read |
| KN-LIT-3460 | Does Fiat-Shamir Require a Cryptographic Hash Function? |  |  | read |
| KN-LIT-3461 | Does My Device Leak Information? An a priori Statistical Power Analysis of Leakage Detection Tests |  |  | read |
| KN-LIT-3462 | Does Privacy Require True Randomness? |  |  | read |
| KN-LIT-3463 | Domain Extension for Enhanced Target |  |  | read |
| KN-LIT-3464 | Domain Extension for MACs Beyond the Birthday Barrier |  |  | read |
| KN-LIT-3465 | DORAM revisited: Maliciously secure RAM-MPC with logarithmic overhead |  |  | read |
| KN-LIT-3466 | Dory: Efficient, Transparent arguments for |  |  | read |
| KN-LIT-3467 | Double-Base Chains for Scalar Multiplications on Elliptic Curves |  |  | read |
| KN-LIT-3468 | Double-Base Number System for Multi-Scalar Multiplications |  |  | read |
| KN-LIT-3469 | Double-base scalar multiplication revisited |  |  | read |
| KN-LIT-3470 | Double-Block-Length Hash Function for Minimum Memory Size |  |  | read |
| KN-LIT-3471 | DPA Attacks and S-Boxes |  |  | read |
| KN-LIT-3472 | DPA Leakage Models for CMOS Logic Circuits |  |  | read |
| KN-LIT-3473 | DPA on n-bit sized Boolean and Arithmetic |  |  | read |
| KN-LIT-3474 | DPA, Bitslicing and Masking at 1 GHz |  |  | read |
| KN-LIT-3475 | DPA-Resistance Without Routing Constraints? |  |  | read |
| KN-LIT-3476 | Dual EC: A Standardized Back Door |  |  | read |
| KN-LIT-3477 | Dual Form Signatures: An Approach for Proving Security from Static Assumptions |  |  | read |
| KN-LIT-3478 | Dual Isogenies and Their Application to Public-key Compression for Isogeny-based Cryptography |  |  | read |
| KN-LIT-3479 | Dual Projective Hashing and its Applications |  |  | read |
| KN-LIT-3480 | Dual System Encryption Framework in Prime-Order Groups via Computational Pair Encodings |  |  | read |
| KN-LIT-3481 | Dual System Encryption via Doubly Selective Security: Framework, Fully Secure Functional Encryption for Regular Languages, and More Nuttapong Attrapadung |  |  | read |
| KN-LIT-3482 | Dual System Encryption via Predicate Encodings |  |  | read |
| KN-LIT-3483 | Dual System Encryption: Realizing Fully Secure IBE and HIBE under Simple Assumptions |  |  | read |
| KN-LIT-3484 | Dual System Framework in Multilinear Settings and Applications to Fully Secure (Compact) ABE for Unbounded-Size Circuits |  |  | read |
| KN-LIT-3485 | Dual-Rail Random Switching Logic: A Countermeasure to Reduce Side Channel Leakage? |  |  | read |
| KN-LIT-3486 | Dual-System Simulation-Soundness with |  |  | read |
| KN-LIT-3487 | DualMS: Efficient Lattice-Based Two-Round Multi-Signature with Trapdoor-Free Simulation |  |  | read |
| KN-LIT-3488 | DualRing : Generic Construction of Ring Signatures with Efficient Instantiations Tsz Hon Yuen1[0000−0002−0629−6792] |  |  | read |
| KN-LIT-3489 | Dummy Shuffling against Algebraic Attacks in White-box Implementations? |  |  | read |
| KN-LIT-3490 | Durandal: a rank metric based signature scheme |  |  | read |
| KN-LIT-3491 | Dynamic Accumulators and Application to Efficient Revocation of Anonymous Credentials |  |  | read |
| KN-LIT-3492 | Dynamic Ad Hoc Clock Synchronization |  |  | read |
| KN-LIT-3493 | Dynamic Collusion Bounded Functional Encryption from Identity-Based Encryption |  |  | read |
| KN-LIT-3494 | Dynamic Collusion Functional Encryption and Multi-Authority Attribute-Based Encryption |  |  | read |
| KN-LIT-3495 | Dynamic Credentials and Ciphertext Delegation for Attribute-Based Encryption |  |  | read |
| KN-LIT-3496 | Dynamic Decentralized Functional Encryption |  |  | read |
| KN-LIT-3497 | Dynamic Group Diffie-Hellman Key Exchange under Standard Assumptions |  |  | read |
| KN-LIT-3498 | Dynamic Local Searchable Symmetric Encryption |  |  | read |
| KN-LIT-3499 | Dynamic Proofs of Retrievability via Oblivious RAM? |  |  | read |
| KN-LIT-3500 | Dynamic Threshold Public-Key Encryption |  |  | read |
| KN-LIT-3501 | Early Propagation and Imbalanced Routing, How to Diminish in FPGAs |  |  | read |
| KN-LIT-3502 | Easing Coppersmith Methods using Analytic Combinatorics: Applications to Public-Key |  |  | read |
| KN-LIT-3503 | ECC2K-130 on NVIDIA GPUs Daniel J. Bernstein1 , Hsieh-Chung Chen2 , Chen-Mou Cheng3 , Tanja Lange4 |  |  | read |
| KN-LIT-3504 | ECLIPSE: Enhanced Compiling method for Pedersen-committed zkSNARK Engines? |  |  | read |
| KN-LIT-3505 | ECM at Work |  |  | read |
| KN-LIT-3506 | ECM on Graphics Cards Daniel J. Bernstein1 , Tien-Ren Chen2 , Chen-Mou Cheng3 |  |  | read |
| KN-LIT-3507 | ECM USING EDWARDS CURVES |  |  | read |
| KN-LIT-3508 | EdDSA for more curves |  |  | read |
| KN-LIT-3509 | Effective and Efficient Masking with Low Noise using Small-Mersenne-Prime Ciphers Loı̈c Masure1[0000−0003−2978−4067] , Pierrick Méaux2[0000−0001−5733−4341] |  |  | read |
| KN-LIT-351 | Design Methods for Cryptanalysis | 2012 |  | read |
| KN-LIT-3510 | Efficiency Limitations for Σ-Protocols for Group Homomorphisms ? |  |  | read |
| KN-LIT-3511 | Efficiency Preserving Transformations for Concurrent Non-Malleable Zero Knowledge |  |  | read |
| KN-LIT-3512 | Efficiency Tradeoffs for Malicious Two-Party Computation |  |  | read |
| KN-LIT-3513 | Efficient (3, 3)-isogenies between fast Kummer surfaces |  |  | read |
| KN-LIT-3514 | Efficient Adaptively Secure Zero-knowledge from Garbled Circuits |  |  | read |
| KN-LIT-3515 | Efficient Adaptively-Secure IB-KEMs and VRFs via Near-Collision Resistance? |  |  | read |
| KN-LIT-3516 | Efficient Algorithms for |  |  | read |
| KN-LIT-3517 | Efficient algorithms for supersingular isogeny Diffie-Hellman |  |  | read |
| KN-LIT-3518 | Efficient and Non-Malleable Proofs of Plaintext |  |  | read |
| KN-LIT-3519 | Efficient and Optimally Secure Key-Length Extension for Block Ciphers via Randomized Cascading |  |  | read |
| KN-LIT-3520 | Efficient and Provable White-Box Primitives |  |  | read |
| KN-LIT-3521 | Efficient and Provably Secure Methods for Switching from Arithmetic to Boolean Masking Blandine Debraize |  |  | read |
| KN-LIT-3522 | Efficient and Provably Secure Trapdoor-free Group Signature Schemes from Bilinear Pairings |  |  | read |
| KN-LIT-3523 | Efficient and Provably-Secure Identity-Based Signatures and |  |  | read |
| KN-LIT-3524 | Efficient and Round-Optimal Oblivious Transfer and Commitment with Adaptive Security? |  |  | read |
| KN-LIT-3525 | Efficient and Secure Elliptic Curve Point Multiplication using Double-Base Chains |  |  | read |
| KN-LIT-3526 | Efficient and Universally Composable Single Secret Leader Election from Pairings |  |  | read |
| KN-LIT-3527 | Efficient Arithmetic on Hessian Curves |  |  | read |
| KN-LIT-3528 | Efficient Attribute-Based Signatures for Unbounded Arithmetic Branching Programs |  |  | read |
| KN-LIT-3529 | Efficient Authentication from Hard Learning Problems Eike Kiltz1? , Krzysztof Pietrzak2?? |  |  | read |
| KN-LIT-3530 | Efficient Batch Zero-Knowledge Arguments for Low Degree Polynomials? |  |  | read |
| KN-LIT-3531 | Efficient Binary Conversion for Paillier Encrypted Values |  |  | read |
| KN-LIT-3532 | Efficient Boolean Search over Encrypted Data with Reduced Leakage |  |  | read |
| KN-LIT-3533 | Efficient Bootstrapping for Approximate Homomorphic Encryption with Non-Sparse Keys |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3534 | Efficient Byzantine Agreement with Faulty Minority? |  |  | read |
| KN-LIT-3535 | Efficient Chosen Ciphertext Secure Public Key Encryption under the Computational Diffie-Hellman Assumption |  |  | read |
| KN-LIT-3536 | Efficient Chosen-Ciphertext Security via Extractable Hash Proofs |  |  | read |
| KN-LIT-3537 | Efficient Circuit-based PSI with Linear Communication |  |  | read |
| KN-LIT-3538 | Efficient Collision Attack Frameworks for RIPEMD-160 |  |  | read |
| KN-LIT-3539 | Efficient Collision Search Attacks on SHA-0 |  |  | read |
| KN-LIT-3540 | Efficient Collision-Resistant Hashing from Worst-Case Assumptions on Cyclic Lattices |  |  | read |
| KN-LIT-3541 | Efficient Completely Context-Hiding Quotable and Linearly Homomorphic Signatures |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3542 | Efficient compression of SIDH public keys |  |  | read |
| KN-LIT-3543 | Efficient Computation Modulo a Shared Secret with Application to the Generation of Shared Safe-Prime Products |  |  | read |
| KN-LIT-3544 | Efficient Computation of Algebraic Immunity for |  |  | read |
| KN-LIT-3545 | Efficient Constant-Round MPC with |  |  | read |
| KN-LIT-3546 | Efficient Constructions of Composable |  |  | read |
| KN-LIT-3547 | Efficient Countermeasures against RPA, DPA, and SPA |  |  | read |
| KN-LIT-3548 | Efficient Covert Two-Party Computation |  |  | read |
| KN-LIT-3549 | Efficient Cryptosystems From 2k -th Power Residue Symbols? |  |  | read |
| KN-LIT-3550 | Efficient Delegation of Zero-Knowledge Proofs of Knowledge in a Pairing-Friendly Setting |  |  | read |
| KN-LIT-3551 | Efficient Design Strategies Based on the AES Round Function |  |  | read |
| KN-LIT-3552 | Efficient Designated Confirmer Signatures |  |  | read |
| KN-LIT-3553 | Efficient Designated-Verifier Non-Interactive Zero-Knowledge Proofs of Knowledge |  |  | read |
| KN-LIT-3554 | Efficient Detection of High Probability Statistical Properties of Cryptosystems via Surrogate Differentiation |  |  | read |
| KN-LIT-3555 | Efficient Dissection of Composite Problems, with |  |  | read |
| KN-LIT-3556 | Efficient Explicit Constructions of Multipartite Secret Sharing Schemes |  |  | read |
| KN-LIT-3557 | Efficient Extension of Standard Schnorr/RSA Signatures into Universal Designated-Verifier Signatures |  |  | read |
| KN-LIT-3558 | Efficient FHEW Bootstrapping with Small |  |  | read |
| KN-LIT-3559 | Efficient Fully Secure Computation via Distributed Zero-Knowledge Proofs |  |  | read |
| KN-LIT-3560 | Efficient Fully Structure-Preserving Signatures for Large Messages |  |  | read |
| KN-LIT-3561 | Efficient Fuzzy Extraction of PUF-Induced Secrets: |  |  | read |
| KN-LIT-3562 | Efficient Fuzzy Search on Encrypted Data |  |  | read |
| KN-LIT-3563 | Efficient General-Adversary Multi-Party Computation |  |  | read |
| KN-LIT-3564 | Efficient Generic Forward-Secure Signatures With An Unbounded Number Of Time Periods |  |  | read |
| KN-LIT-3565 | Efficient Group Signatures without Trapdoors? |  |  | read |
| KN-LIT-3566 | Efficient hardware for the Tate pairing calculation in characteristic three |  |  | read |
| KN-LIT-3567 | Efficient Hashing using the AES Instruction Set |  |  | read |
| KN-LIT-3568 | Efficient Helper Data Key Extractor on FPGAs |  |  | read |
| KN-LIT-3569 | Efficient High-Speed WPA2 Brute Force Attacks using |  |  | read |
| KN-LIT-3570 | Efficient Homomorphic Comparison Methods with Optimal Complexity |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3571 | Efficient Hybrid Exact/Relaxed Lattice Proofs |  |  | read |
| KN-LIT-3572 | Efficient IBE with Tight Reduction to Standard Assumption in the Multi-challenge Setting |  |  | read |
| KN-LIT-3573 | Efficient Identity-Based Encryption over NTRU Lattices |  |  | read |
| KN-LIT-3574 | Efficient Implementations of MQPKS on Constrained Devices |  |  | read |
| KN-LIT-3575 | Efficient Indifferentiable Hashing into Ordinary Elliptic Curves |  |  | read |
| KN-LIT-3576 | Efficient Information-Theoretic Secure Multiparty Computation over Z/pk Z via Galois Rings |  |  | read |
| KN-LIT-3577 | Efficient Instantiations of Tweakable Blockciphers and |  |  | read |
| KN-LIT-3578 | Efficient Invisible and Unlinkable Sanitizable Signatures |  |  | read |
| KN-LIT-3579 | Efficient k-out-of-n Oblivious Transfer Schemes with Adaptive and Non-Adaptive Queries |  |  | read |
| KN-LIT-3580 | Efficient KDM-CCA Secure Public-Key Encryption for Polynomial Functions |  |  | read |
| KN-LIT-3581 | Efficient Key Recovery for all HFE Signature Variants |  |  | read |
| KN-LIT-3582 | Efficient KZG-based Univariate Sum-check and Lookup Argument |  |  | read |
| KN-LIT-3583 | Efficient Lattice (H)IBE in the Standard Model? |  |  | read |
| KN-LIT-3584 | Efficient Lattice-Based Blind Signatures via Gaussian One-Time Signatures |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3585 | Efficient Lattice-Based Inner-Product Functional Encryption |  |  | read |
| KN-LIT-3586 | Efficient Lattice-Based Zero-Knowledge Arguments with Standard Soundness: Construction and Applications |  |  | read |
| KN-LIT-3587 | Efficient Linear Array for Multiplication in GF (2m ) Using a Normal Basis for Elliptic Curve Cryptography |  |  | read |
| KN-LIT-3588 | Efficient Maliciously Secure Multiparty Computation for RAM |  |  | read |
| KN-LIT-3589 | Efficient Multi-Party Computation with Dispute Control? |  |  | read |
| KN-LIT-3590 | Efficient Multi-Party Computation: from Passive to Active Security via Secure SIMD Circuits |  |  | read |
| KN-LIT-3591 | Efficient Multi-Receiver Identity-Based |  |  | read |
| KN-LIT-3592 | Efficient Multiparty Protocols via Log-Depth Threshold Formulae |  |  | read |
| KN-LIT-3593 | Efficient Network Coding Signatures in the Standard Model |  |  | read |
| KN-LIT-3594 | Efficient NIZKs for Algebraic Sets |  |  | read |
| KN-LIT-3595 | Efficient NIZKs from LWE via Polynomial Reconstruction and “MPC in the Head” |  |  | read |
| KN-LIT-3596 | Efficient Non-interactive Proof Systems for Bilinear Groups? |  |  | read |
| KN-LIT-3597 | Efficient Non-Interactive Secure Computation |  |  | read |
| KN-LIT-3598 | Efficient Non-Interactive Zero-Knowledge Proofs in Cross-Domains without Trusted Setup |  |  | read |
| KN-LIT-3599 | Efficient Non-Malleable Codes and Key-Derivation for Poly-Size Tampering Circuits |  |  | read |
| KN-LIT-3600 | Efficient Noninteractive Certification of RSA Moduli and Beyond |  |  | read |
| KN-LIT-3601 | Efficient Oblivious Pseudorandom Function with Applications to Adaptive OT and Secure Computation of Set Intersection |  |  | read |
| KN-LIT-3602 | Efficient Oblivious Transfer in the Bounded-Storage Model |  |  | read |
| KN-LIT-3603 | Efficient One-time Proxy Signatures |  |  | read |
| KN-LIT-3604 | Efficient Pairings and ECC for Embedded Systems |  |  | read |
| KN-LIT-3605 | Efficient Password Authenticated Key Exchange via Oblivious Transfer |  |  | read |
| KN-LIT-3606 | Efficient Perfectly Secure Computation with Optimal Resilience |  |  | read |
| KN-LIT-3607 | Efficient Polynomial Operations in the Shared-Coefficients Setting |  |  | read |
| KN-LIT-3608 | Efficient Power and Timing Side Channels for Physical Unclonable Functions |  |  | read |
| KN-LIT-3609 | Efficient Private Matching and Set Intersection |  |  | read |
| KN-LIT-3610 | Efficient Proofs Of Knowledge of Discrete Logarithms and Representations in Groups with Hidden Order |  |  | read |
| KN-LIT-3611 | Efficient Protocols for Set Membership and Range Proofs |  |  | read |
| KN-LIT-3612 | Efficient Pseudorandom |  |  | read |
| KN-LIT-3613 | Efficient Pseudorandom Correlation Generators: |  |  | read |
| KN-LIT-3614 | Efficient Pseudorandom Functions via On-the-Fly Adaptation |  |  | read |
| KN-LIT-3615 | Efficient Pseudorandom Generators Based on the DDH Assumption |  |  | read |
| KN-LIT-3616 | Efficient Public-Key Cryptography in the Presence of Key Leakage |  |  | read |
| KN-LIT-3617 | Efficient Public-Key Cryptography with Bounded |  |  | read |
| KN-LIT-3618 | Efficient Range Proofs with Transparent Setup from Bounded Integer Commitments |  |  | read |
| KN-LIT-3619 | Efficient Range-Trapdoor Functions and Applications: Rate-1 OT and More |  |  | read |
| KN-LIT-3620 | Efficient Ratcheting: Almost-Optimal Guarantees for Secure Messaging |  |  | read |
| KN-LIT-3621 | Efficient Redactable Signature and Application to Anonymous Credentials Olivier Sanders |  |  | read |
| KN-LIT-3622 | Efficient Ring Signatures in the Standard Model |  |  | read |
| KN-LIT-3623 | Efficient Ring Signatures Without Random Oracles |  |  | read |
| KN-LIT-3624 | Efficient Ring-LWE Encryption on 8-bit |  |  | read |
| KN-LIT-3625 | Efficient Round Optimal Blind Signatures |  |  | read |
| KN-LIT-3626 | Efficient Scalable Constant-Round MPC via Garbled Circuits |  |  | read |
| KN-LIT-3627 | Efficient Schemes for Committing Authenticated Encryption |  |  | read |
| KN-LIT-3628 | Efficient Searchable Symmetric Encryption for Join Queries |  |  | read |
| KN-LIT-3629 | Efficient Secure Linear Algebra in the Presence of Covert or Computationally Unbounded Adversaries |  |  | read |
| KN-LIT-3630 | Efficient Secure Storage with Version Control and Key Rotation |  |  | read |
| KN-LIT-3631 | Efficient Selective-ID Secure Identity-Based Encryption Without Random Oracles |  |  | read |
| KN-LIT-3632 | Efficient Sequential Aggregate Signed Data |  |  | read |
| KN-LIT-3633 | Efficient Signcryption with Key Privacy from Gap Diffie-Hellman Groups Benoı̂t Libert ? |  |  | read |
| KN-LIT-3634 | Efficient simulation of random states and random unitaries |  |  | read |
| KN-LIT-3635 | Efficient Simultaneous Broadcast |  |  | read |
| KN-LIT-3636 | Efficient String-Commitment from Weak Bit-Commitment |  |  | read |
| KN-LIT-3637 | Efficient Techniques for High-Speed Elliptic Curve Cryptography |  |  | read |
| KN-LIT-3638 | Efficient Threshold RSA Signatures with |  |  | read |
| KN-LIT-3639 | Efficient Two Party and Multi Party Computation against Covert Adversaries |  |  | read |
| KN-LIT-3640 | Efficient Two-Party Secure Computation on Committed Inputs |  |  | read |
| KN-LIT-3641 | Efficient UC Commitment Extension with Homomorphism for Free (and Applications) Ignacio Cascudo1 , Ivan Damgård2 , Bernardo David3 , Nico Döttling4 |  |  | read |
| KN-LIT-3642 | Efficient UC-Secure Authenticated Key-Exchange for Algebraic Languages |  |  | read |
| KN-LIT-3643 | Efficient Universal Padding Techniques for Multiplicative Trapdoor One-way Permutation |  |  | read |
| KN-LIT-3644 | Efficient Unlinkable Sanitizable Signatures from Signatures with Re-Randomizable Keys Nils Fleischhacker, Johannes Krupp, Giulio Malavolta, Jonas Schneider |  |  | read |
| KN-LIT-3645 | Efficient Updatable Public-Key Encryption from Lattices |  |  | read |
| KN-LIT-3646 | Efficient verifiable delay functions? |  |  | read |
| KN-LIT-3647 | Efficient Verifiable Partially-Decryptable Commitments from Lattices and Applications |  |  | read |
| KN-LIT-3648 | Efficient Zero-Knowledge Arguments for Arithmetic Circuits in the Discrete Log Setting? |  |  | read |
| KN-LIT-3649 | Efficient Zero-Knowledge Arguments from Two-Tiered |  |  | read |
| KN-LIT-3650 | Efficient Zero-Knowledge Arguments in Discrete Logarithm Setting: Sublogarithmic Proof or Sublinear Verifier |  |  | read |
| KN-LIT-3651 | Efficient Zero-knowledge Authentication Based on a Linear Algebra Problem MinRank |  |  | read |
| KN-LIT-3652 | Efficient Zero-Knowledge Proof of Algebraic and Non-Algebraic Statements with Applications to Privacy Preserving Credentials |  |  | read |
| KN-LIT-3653 | Efficient Zero-Knowledge Proofs of Non-Algebraic Statements with Sublinear Amortized Cost |  |  | read |
| KN-LIT-3654 | Efficient, Adaptively Secure, and Composable Oblivious Transfer with a Single, Global CRS Seung Geol Choi1? , Jonathan Katz2?? |  |  | read |
| KN-LIT-3655 | Efficient, Oblivious Data Structures for MPC |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3656 | Efficient, Robust and Constant-Round Distributed RSA Key Generation |  |  | read |
| KN-LIT-3657 | Efficient, Verifiable Shuffle Decryption and Its Requirement of Unlinkability Jun Furukawa |  |  | read |
| KN-LIT-3658 | Efficiently Masking Binomial Sampling at Arbitrary Orders for Lattice-Based Crypto |  |  | read |
| KN-LIT-3659 | Efficiently Shuffling in Public |  |  | read |
| KN-LIT-3660 | Efficiently Testable Circuits Without Conductivity |  |  | read |
| KN-LIT-3661 | EKE Meets Tight Security in the Universally Composable Framework |  |  | read |
| KN-LIT-3662 | Eliminating Random Permutation Oracles in the Even-Mansour Cipher |  |  | read |
| KN-LIT-3663 | ElimLin Algorithm Revisited |  |  | read |
| KN-LIT-3665 | Elliptic and Hyperelliptic Curves: a Practical Security Analysis |  |  | read |
| KN-LIT-3666 | Elliptic curve cryptography in a post-quantum world: the mathematics of isogeny-based cryptography |  |  | read |
| KN-LIT-3667 | Elliptic Curve Scalar Multiplication Combining Yao’s |  |  | read |
| KN-LIT-3668 | Elliptic curves and number-thcorelic algorithms - H.W. Lenstra, Jr - version 19860716 |  |  | read |
| KN-LIT-3669 | EM Attack Is Non-Invasive? |  |  | read |
| KN-LIT-3670 | Embedded Evaluation of Randomness in Oscillator Based Elementary TRNG |  |  | read |
| KN-LIT-3671 | Embedding the UC Model into the IITM Model |  |  | read |
| KN-LIT-3672 | Encoding Functions with Constant Online Rate or How to Compress Garbled Circuits Keys? |  |  | read |
| KN-LIT-3673 | Encoding-Free ElGamal Encryption Without Random Oracles |  |  | read |
| KN-LIT-3674 | EnCounter: On Breaking the Nonce Barrier in Differential Fault Analysis with a Case-Study on PAEQ |  |  | read |
| KN-LIT-3675 | Encrypt or Decrypt? To Make a Single-Key Beyond Birthday Secure Nonce-Based MAC |  |  | read |
| KN-LIT-3676 | Encrypted Davies-Meyer and Its Dual: Towards Optimal Security Using Mirror Theory |  |  | read |
| KN-LIT-3677 | Encryption and Applications |  |  | read |
| KN-LIT-3678 | Encryption Switching Protocols |  |  | read |
| KN-LIT-3679 | Encryption Switching Protocols Revisited: Switching modulo p |  |  | read |
| KN-LIT-3680 | Encryption to the Future A Paradigm for Sending Secret Messages to Future (Anonymous) Committees Matteo Campanelli1 |  |  | read |
| KN-LIT-3681 | End-to-end Design of a PUF-based Privacy Preserving Authentication Protocol |  |  | read |
| KN-LIT-3682 | End-to-End Secure Messaging with Traceability Only for Illegal Content |  |  | read |
| KN-LIT-3683 | End-to-End Verifiable Elections in the Standard Model? |  |  | read |
| KN-LIT-3684 | Endemic Oblivious Transfer via Random |  |  | read |
| KN-LIT-3685 | Endomorphisms for Faster Elliptic Curve Cryptography on a Large Class of Curves |  |  | read |
| KN-LIT-3686 | Energy-Efficient Software Implementation of Long Integer Modular Arithmetic? |  |  | read |
| KN-LIT-3687 | Engineering Code Obfuscation |  |  | read |
| KN-LIT-3688 | Engineering Privacy-Friendly Computations |  |  | read |
| KN-LIT-3689 | Enhan ing Collision Atta ks |  |  | read |
| KN-LIT-3690 | Enhanced Lattice-Based Signatures on Reconfigurable Hardware |  |  | read |
| KN-LIT-3691 | Enhanced Security Notions for Dedicated-Key Hash Functions: Definitions and Relationships |  |  | read |
| KN-LIT-3692 | Enhancements Are Blackbox Non-Trivial: Impossibility of Enhanced Trapdoor Permutations from Standard Trapdoor Permutations |  |  | read |
| KN-LIT-3693 | Enhancing Differential-Linear Cryptanalysis? |  |  | read |
| KN-LIT-3694 | Enhancing Differential-Neural Cryptanalysis |  |  | read |
| KN-LIT-3695 | Entropy Evaluation for Oscillator-based True |  |  | read |
| KN-LIT-3696 | Entropy of the Internal State of an FCSR in Galois Representation Andrea Röck |  |  | read |
| KN-LIT-3697 | ENUMERATING AND COUNTING SMOOTH INTEGERS |  |  | read |
| KN-LIT-3698 | EpiGRAM: Practical Garbled RAM |  |  | read |
| KN-LIT-3699 | Equational Security Proofs of Oblivious Transfer Protocols? |  |  | read |
| KN-LIT-3700 | Equipping Public-Key Cryptographic Primitives with Watermarking (or: A Hole Is to Watermark) |  |  | read |
| KN-LIT-3701 | Equivalence between Semantic Security and Indistinguishability against Chosen Ciphertext Attacks |  |  | read |
| KN-LIT-3702 | Equivalence of Uniform Key Agreement and Composition Insecurity★ |  |  | read |
| KN-LIT-3703 | Equivalences and Black-Box Separations of Matrix Diffie-Hellman Problems |  |  | read |
| KN-LIT-3704 | Equivalent Key Recovery Attacks against HMAC and NMAC with Whirlpool Reduced to 7 Rounds |  |  | read |
| KN-LIT-3705 | Equivocal Blind Signatures and Adaptive UC-Security |  |  | read |
| KN-LIT-3706 | Error Correction and Ciphertext Quantization in Lattice Cryptography |  |  | read |
| KN-LIT-3707 | Error Correction in The Bounded Storage Model |  |  | read |
| KN-LIT-3708 | Errors in Computational Complexity Proofs for Protocols |  |  | read |
| KN-LIT-3709 | Essential Algebraic Structure Within the AES |  |  | read |
| KN-LIT-3710 | Essentially Optimal |  |  | read |
| KN-LIT-3711 | EvalRound Algorithm in CKKS Bootstrapping Kim |  |  | read |
| KN-LIT-3712 | Evaluating 2-DNF Formulas on Ciphertexts |  |  | read |
| KN-LIT-3713 | Evaluation and Improvement of Generic-Emulating DPA Attacks Weijia Wang1 , Yu Yu1 , Junrong Liu1,2 , Zheng Guo1,2 |  |  | read |
| KN-LIT-3714 | Evaluation of Security Level of Cryptography: The Elliptic Curve Discrete Logarithm Problem (ECDLP) |  |  | read |
| KN-LIT-3715 | Evaluation of the Masked Logic Style MDPL on a Prototype Chip |  |  | read |
| KN-LIT-3716 | Everlasting Multi-Party Computation |  |  | read |
| KN-LIT-3717 | Everybody’s a Target: Scalability in Public-Key Encryption |  |  | read |
| KN-LIT-3718 | EWCDM: An Efficient, Beyond-Birthday Secure, Nonce-Misuse Resistant MAC |  |  | read |
| KN-LIT-3719 | Exact Lattice Sampling from Non-Gaussian Distributions |  |  | read |
| KN-LIT-3720 | Exact Security Analysis of ASCON |  |  | read |
| KN-LIT-3721 | Exceptional Procedure Attack on Elliptic Curve Cryptosystems |  |  | read |
| KN-LIT-3722 | Exclusive Exponent Blinding May Not Suffice to Prevent Timing Attacks on RSA |  |  | read |
| KN-LIT-3723 | Exhausting Demirci-Selçuk Meet-in-the-Middle Attacks against Reduced-Round AES |  |  | read |
| KN-LIT-3724 | Expand-Convolute Codes for Pseudorandom Correlation Generators from LPN |  |  | read |
| KN-LIT-3725 | Expected-Time Cryptography: |  |  | read |
| KN-LIT-3726 | Experimenting with Faults, Lattices and the DSA |  |  | read |
| KN-LIT-3727 | EXPLICIT DESCENT IN THE PICARD GROUP OF A CYCLIC COVER OF THE PROJECTIVE LINE |  |  | read |
| KN-LIT-3728 | EXPLICIT NON-GORENSTEIN R = T VIA RANK BOUNDS II: COMPUTATION |  |  | read |
| KN-LIT-3729 | Explicit Non-malleable Codes against Bit-wise Tampering and Permutations |  |  | read |
| KN-LIT-3730 | Exploiting Non-Full Key Additions: Full-Fledged Automatic Demirci-Selçuk Meet-in-the-Middle Cryptanalysis of SKINNY |  |  | read |
| KN-LIT-3731 | Exploiting the Power of GPUs for Asymmetric Cryptography |  |  | read |
| KN-LIT-3732 | Exploiting the Symmetry of Zn : Randomization and the Automorphism Problem |  |  | read |
| KN-LIT-3733 | Exploring Constructions of Compact NIZKs from Various Assumptions |  |  | read |
| KN-LIT-3734 | Exploring Crypto Dark Matter: |  |  | read |
| KN-LIT-3735 | Exploring Decryption Failures of BIKE: New Class of Weak Keys and Key Recovery Attacks |  |  | read |
| KN-LIT-3736 | Exploring SAT for Cryptanalysis: (Quantum) Collision Attacks against 6-Round |  |  | read |
| KN-LIT-3737 | Exploring the Boundaries of Topology-Hiding Computation |  |  | read |
| KN-LIT-3738 | Exploring the Limits of Common Coins Using Frontier Analysis of Protocols |  |  | read |
| KN-LIT-3739 | Expressive Key-Policy Attribute-Based Encryption with Constant-Size Ciphertexts |  |  | read |
| KN-LIT-3740 | Extendable Threshold Ring Signatures with Enhanced Anonymity |  |  | read |
| KN-LIT-3741 | Extended Nested Dual System Groups, Revisited |  |  | read |
| KN-LIT-3742 | Extended Tower Number Field Sieve with Application to Finite Fields of Arbitrary Composite Extension Degree |  |  | read |
| KN-LIT-3743 | Extended Tower Number Field Sieve: A New Complexity for the Medium Prime Case? |  |  | read |
| KN-LIT-3744 | Extended-DDH and Lossy Trapdoor Functions |  |  | read |
| KN-LIT-3745 | Extending Oblivious Transfer with Low Communication via Key-Homomorphic PRFs |  |  | read |
| KN-LIT-3746 | Extending Oblivious Transfers Efficiently |  |  | read |
| KN-LIT-3747 | Extending Scalar Multiplication |  |  | read |
| KN-LIT-3748 | Extending the GHS Weil Descent Attack |  |  | read |
| KN-LIT-3749 | Extending the Salsa20 nonce |  |  | read |
| KN-LIT-3750 | eXternal Benchmarking eXtension for the SUPERCOP crypto benchmarking framework |  |  | read |
| KN-LIT-3751 | Extracting Group Signatures from Traitor Tracing Schemes |  |  | read |
| KN-LIT-3752 | Extracting Randomness from Extractor-Dependent Sources |  |  | read |
| KN-LIT-3753 | Extractors Against Side-Channel Attacks: Weak or Strong? |  |  | read |
| KN-LIT-3754 | Extreme Enumeration on GPU and in Clouds - How Many Dollars You Need to Break SVP Challenges - 1 |  |  | read |
| KN-LIT-3755 | Eye for an Eye: E cient Concurrent Zero-Knowledge in the Timing Model |  |  | read |
| KN-LIT-3756 | Efficient Adaptively-Secure Byzantine Agreement for Long Messages |  |  | read |
| KN-LIT-3757 | Efficient Leakage-Resilient MACs without Idealized Assumptions |  |  | read |
| KN-LIT-3758 | Efficient Attribute-Based Signatures for Non-Monotone Predicates in the Standard Model |  |  | read |
| KN-LIT-3759 | Efficient Circuit-Size Independent Public Key Encryption with KDM Security |  |  | read |
| KN-LIT-3760 | Efficient Construction of (Distributed) Verifiable Random Functions |  |  | read |
| KN-LIT-3761 | Efficient Laconic Cryptography from Learning With Errors Nico Döttling1 , Dimitris Kolonelos2,3 , Russell W. F. Lai4 , Chuanwei Lin1 |  |  | read |
| KN-LIT-3762 | Efficient Reconstruction of RC4 Keys from Internal States |  |  | read |
| KN-LIT-3763 | Efficient Secure Two-Party Computation Using Symmetric Cut-and-Choose |  |  | read |
| KN-LIT-3764 | Factoring estimates for a 1024-bit |  |  | read |
| KN-LIT-3765 | Factoring Large Numbers with the TWIRL Device |  |  | read |
| KN-LIT-3766 | FACTORING POLYNOMIALS OVER FUNCTION FIELDS |  |  | read |
| KN-LIT-3767 | Factoring pq 2 with Quadratic Forms: Nice Cryptanalyses |  |  | read |
| KN-LIT-3768 | Factoring Products of Braids via Garside Normal Form |  |  | read |
| KN-LIT-3769 | Factoring RSA keys from certified smart cards: |  |  | read |
| KN-LIT-3770 | Factorization of a 768-bit RSA modulus |  |  | read |
| KN-LIT-3771 | Failing gracefully: Decryption failures and the Fujisaki-Okamoto transform |  |  | read |
| KN-LIT-3772 | Failures in NIST’s ECC standards |  |  | read |
| KN-LIT-3773 | Fair and Comprehensive Methodology for Comparing Hardware Performance of Fourteen Round Two SHA-3 Candidates using FPGAs? |  |  | read |
| KN-LIT-3774 | Fair and Efficient Secure Multiparty Computation with Reputation Systems? |  |  | read |
| KN-LIT-3775 | Fair and Robust Multi-Party Computation using a Global Transaction Ledger |  |  | read |
| KN-LIT-3776 | Fair-Zero Knowledge |  |  | read |
| KN-LIT-3777 | Fairness Versus Guaranteed Output Delivery in Secure Multiparty Computation? |  |  | read |
| KN-LIT-3778 | Fairness with an Honest Minority and a Rational Majority? |  |  | read |
| KN-LIT-3779 | Families of Fast Elliptic Curves from Q-curves Benjamin Smith |  |  | read |
| KN-LIT-3780 | Families of SNARK-friendly 2-chains of elliptic curves |  |  | read |
| KN-LIT-3781 | Fast Algebraic Attacks on Stream Ciphers with Linear Feedback |  |  | read |
| KN-LIT-3782 | Fast Algorithms for the Free Riders Problem in Broadcast Encryption |  |  | read |
| KN-LIT-3783 | Fast and Secure CBC-Type MAC Algorithms |  |  | read |
| KN-LIT-3784 | Fast and Simple Point Operations on Edwards448 and E448 |  |  | read |
| KN-LIT-3785 | Fast Arithmetic on Jacobians of Picard Curves |  |  | read |
| KN-LIT-3786 | Fast Batch Verification of Multiple Signatures |  |  | read |
| KN-LIT-3787 | Fast Batched DPSS and its Applications Vipul Goyal1,2 , Abhiram Kothapalli1 , Elisaweta Masserova1 , Bryan Parno1 , and Yifan Song1 |  |  | read |
| KN-LIT-3788 | Fast Blind Rotation for Bootstrapping FHEs |  |  | read |
| KN-LIT-3789 | Fast change of level and applications to isogenies |  |  | read |
| KN-LIT-3790 | Fast Computation of Large Distributions and Its Cryptographic Applications |  |  | read |
| KN-LIT-3791 | Fast constant-time |  |  | read |
| KN-LIT-3792 | Fast Correlation Attack Revisited Cryptanalysis on Full Grain-128a, Grain-128, and Grain-v1 |  |  | read |
| KN-LIT-3793 | Fast Correlation Attacks over Extension Fields, Large-unit Linear Approximation and Cryptanalysis of SNOW 2.0 |  |  | read |
| KN-LIT-3794 | Fast Correlation Attacks: an Algorithmic Point of View |  |  | read |
| KN-LIT-3795 | Fast Correlation Attacks: Methods and Countermeasures |  |  | read |
| KN-LIT-3796 | Fast Cryptographic Primitives and Circular-Secure Encryption Based on Hard Learning Problems |  |  | read |
| KN-LIT-3797 | Fast Cryptography in Genus |  |  | read |
| KN-LIT-3798 | Fast Distributed RSA Key Generation for |  |  | read |
| KN-LIT-3799 | Fast Encryption and Authentication in a Single Cryptographic Primitive |  |  | read |
| KN-LIT-3800 | Fast Evaluation of Polynomials over Binary |  |  | read |
| KN-LIT-3801 | Fast Generation of Prime Numbers on Portable Devices: An Update |  |  | read |
| KN-LIT-3802 | Fast Homomorphic |  |  | read |
| KN-LIT-3803 | Fast Large-Scale |  |  | read |
| KN-LIT-3804 | Fast Lattice Basis Reduction Suitable for |  |  | read |
| KN-LIT-3805 | Fast Leakage Assessment |  |  | read |
| KN-LIT-3806 | Fast Message Franking: From Invisible Salamanders to Encryptment |  |  | read |
| KN-LIT-3807 | Fast Multi-computations with Integer Similarity Strategy ? |  |  | read |
| KN-LIT-3808 | Fast Multi-Precision Multiplication for Public-Key Cryptography on Embedded Microprocessors |  |  | read |
| KN-LIT-3809 | Fast Near Collision Attack on the Grain v1 Stream Cipher |  |  | read |
| KN-LIT-3810 | Fast Practical Lattice Reduction through Iterated Compression [0000−0001−5846−2046] |  |  | read |
| KN-LIT-3811 | Fast Pseudorandom Functions Based on Expander Graphs? |  |  | read |
| KN-LIT-3812 | Fast Reduction of Algebraic Lattices over Cyclotomic fields |  |  | read |
| KN-LIT-3813 | Fast Secure Two-Party ECDSA Signing |  |  | read |
| KN-LIT-3814 | Fast Software AES Encryption |  |  | read |
| KN-LIT-3815 | FAST SQUARE-FREE DECOMPOSITION OF INTEGERS USING CLASS GROUPS ERIK MULDER |  |  | read |
| KN-LIT-3816 | Fast verification of masking schemes in characteristic two |  |  | read |
| KN-LIT-3817 | Fast, Compact, and Expressive Attribute-Based Encryption |  |  | read |
| KN-LIT-3818 | FAST: Secure and High Performance |  |  | read |
| KN-LIT-3819 | Faster 2-regular information-set decoding |  |  | read |
| KN-LIT-3820 | Faster addition and doubling on elliptic curves |  |  | read |
| KN-LIT-3821 | Faster Algorithms for Approximate Common Divisors: Breaking Fully-Homomorphic-Encryption Challenges over the Integers |  |  | read |
| KN-LIT-3822 | Faster Algorithms for Solving LPN |  |  | read |
| KN-LIT-3823 | Faster Amortized FHEW Bootstrapping Using Ring Automorphisms Gabrielle De Micheli1[0000−0002−2617−6878] , Duhyeong Kim2[0000−0002−4766−3456] |  |  | read |
| KN-LIT-3824 | Faster and Lower Memory Scalar Multiplication on Supersingular Curves in Characteristic Three |  |  | read |
| KN-LIT-3825 | Faster and Shorter |  |  | read |
| KN-LIT-3826 | Faster and Timing-Attack Resistant AES-GCM |  |  | read |
| KN-LIT-3827 | Faster batch forgery identification |  |  | read |
| KN-LIT-3828 | Faster Binary-Field Multiplication and Faster Binary-Field MACs |  |  | read |
| KN-LIT-3829 | Faster Bootstrapping with Polynomial Error |  |  | read |
| KN-LIT-3830 | Faster cofactorization with ECM using mixed representations |  |  | read |
| KN-LIT-3831 | Faster Compact Diffie–Hellman: Endomorphisms on the x-line |  |  | read |
| KN-LIT-3832 | Faster discrete logarithms on |  |  | read |
| KN-LIT-3833 | Faster ECC over F2521 −1 |  |  | read |
| KN-LIT-3834 | Faster elliptic-curve discrete logarithms on |  |  | read |
| KN-LIT-3835 | Faster Enumeration-based Lattice Reduction: Root Hermite Factor k1/(2k) in Time kk/8 + o(k) |  |  | read |
| KN-LIT-3836 | Faster Evaluation of SBoxes via Common Shares |  |  | read |
| KN-LIT-3837 | Faster Explicit Formulas for Computing Pairings over Ordinary Curves Diego F. Aranha1? , Koray Karabina2? |  |  | read |
| KN-LIT-3838 | Faster Fp -arithmetic for Cryptographic Pairings on Barreto-Naehrig Curves |  |  | read |
| KN-LIT-3839 | Faster Fully Homomorphic Encryption |  |  | read |
| KN-LIT-3840 | Faster Fully Homomorphic Encryption: Bootstrapping in less than 0.1 Seconds |  |  | read |
| KN-LIT-3841 | Faster Gaussian Lattice Sampling using Lazy Floating-Point Arithmetic |  |  | read |
| KN-LIT-3842 | Faster Gaussian Sampling for Trapdoor Lattices with Arbitrary Modulus? |  |  | read |
| KN-LIT-3843 | Faster Homomorphic Function Evaluation using Non-Integral Base Encoding |  |  | read |
| KN-LIT-3844 | Faster Homomorphic Linear Transformations in HElib? |  |  | read |
| KN-LIT-3845 | Faster index calculus for the medium prime case |  |  | read |
| KN-LIT-3846 | Faster packed homomorphic operations and efficient circuit bootstrapping for TFHE |  |  | read |
| KN-LIT-3847 | Faster Pairing Computations on Curves with High-Degree Twists |  |  | read |
| KN-LIT-3848 | Faster Point Multiplication on Elliptic Curves with Efficient Endomorphisms |  |  | read |
| KN-LIT-3849 | Faster Scalar Multiplication on Koblitz Curves combining Point Halving with the Frobenius Endomorphism |  |  | read |
| KN-LIT-3850 | Faster Secure Two-Party Computation in the Single-Execution Setting |  |  | read |
| KN-LIT-3851 | Faster Sounder Succinct Arguments and IOPs |  |  | read |
| KN-LIT-3852 | FASTER SQUARE ROOTS IN ANNOYING FINITE FIELDS |  |  | read |
| KN-LIT-3853 | Faster Squaring in the Cyclotomic Subgroup of Sixth Degree Extensions |  |  | read |
| KN-LIT-3854 | Fault Analysis of Stream Ciphers |  |  | read |
| KN-LIT-3855 | Fault Attacks on RSA Signatures with Partially Unknown Messages |  |  | read |
| KN-LIT-3856 | Fault Injection and a Timing Channel on an Analysis Technique |  |  | read |
| KN-LIT-3857 | Fault Sensitivity Analysis Yang Li1 , Kazuo Sakiyama1 , Shigeto Gomisawa1 , Toshinori Fukunaga2 |  |  | read |
| KN-LIT-3858 | Fault Template Attacks on Block Ciphers |  |  | read |
| KN-LIT-3859 | Fault-Injection Attacks against NIST’s |  |  | read |
| KN-LIT-3860 | Fault-Tolerant Aggregate Signatures |  |  | read |
| KN-LIT-3861 | FE and iO for Turing Machines from Minimal Assumptions |  |  | read |
| KN-LIT-3862 | FE for Inner Products and Its Application to Decentralized ABE |  |  | read |
| KN-LIT-3863 | Feasibility and Completeness of |  |  | read |
| KN-LIT-3864 | Feasibility and Infeasibility of Adaptively Secure Fully Homomorphic Encryption |  |  | read |
| KN-LIT-3865 | Feasibility and Infeasibility of Secure Computation with Malicious PUFs |  |  | read |
| KN-LIT-3866 | Feistel Networks made Public, and Applications |  |  | read |
| KN-LIT-3867 | FESTA : Fast Encryption from Supersingular Torsion Attacks |  |  | read |
| KN-LIT-3868 | FHE Circuit Privacy Almost For Free |  |  | read |
| KN-LIT-3869 | FHE Over the Integers: Decomposed and Batched in the Post-Quantum Regime |  |  | read |
| KN-LIT-3870 | FHE-Based Bootstrapping of Designated-Prover NIZK |  |  | read |
| KN-LIT-3871 | FHEW: Bootstrapping Homomorphic Encryption in less than a second‹ |  |  | read |
| KN-LIT-3872 | Fiat-Shamir for Repeated Squaring with |  |  | read |
| KN-LIT-3873 | Fiat-Shamir Security of FRI and Related SNARKs |  |  | read |
| KN-LIT-3874 | Fiat-Shamir Transformation of Multi-Round Interactive Proofs |  |  | read |
| KN-LIT-3875 | Fiat-Shamir With Aborts: |  |  | read |
| KN-LIT-3876 | Fiat–Shamir Bulletproofs are Non-Malleable (in the Algebraic Group Model) Chaya Ganesh1[0000−0002−2909−9177] , Claudio Orlandi2[0000−0003−4992−0249] |  |  | read |
| KN-LIT-3877 | Fides: Lightweight Authenticated Cipher with Side-Channel Resistance for Constrained Hardware Begül |  |  | read |
| KN-LIT-3878 | Field Instruction Multiple Data |  |  | read |
| KN-LIT-3879 | FINAL: Faster FHE instantiated with NTRU and LWE |  |  | read |
| KN-LIT-3880 | Financially Backed Covert Security |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3881 | Finding Collisions in a Quantum World: Quantum Black-Box Separation of Collision-Resistance and One-Wayness |  |  | read |
| KN-LIT-3882 | Finding Collisions in the Full SHA-1 |  |  | read |
| KN-LIT-3883 | Finding Collisions on a Public Road, or Do Secure Hash Functions Need Secret Coins? |  |  | read |
| KN-LIT-3884 | Finding Hash Collisions with Quantum Computers by Using Differential Trails with Smaller Probability than Birthday Bound |  |  | read |
| KN-LIT-3885 | FINDING INTEGRAL POINTS ON ELLIPTIC CURVES OVER IMAGINARY |  |  | read |
| KN-LIT-3886 | Finding many Collisions via Reusable Quantum Walks Application to Lattice Sieving |  |  | read |
| KN-LIT-3887 | Finding Pessiland |  |  | read |
| KN-LIT-3888 | Finding Preimages in Full MD5 Faster than Exhaustive Search |  |  | read |
| KN-LIT-3889 | Finding Preimages of Tiger Up to 23 Steps |  |  | read |
| KN-LIT-3890 | Finding Second Preimages of Short Messages for Hamsi-256 |  |  | read |
| KN-LIT-3891 | Finding SHA-1 Characteristics: |  |  | read |
| KN-LIT-3892 | Finding SHA-2 Characteristics: Searching Through a Minefield of Contradictions |  |  | read |
| KN-LIT-3893 | Finding short integer solutions when the modulus is small |  |  | read |
| KN-LIT-3894 | Finding Small Roots of Bivariate Integer |  |  | read |
| KN-LIT-3895 | Finding the AES Bits in the Haystack: |  |  | read |
| KN-LIT-3896 | Finding the Impossible: Automated Search for Full Impossible-Differential, Zero-Correlation, and Integral Attacks |  |  | read |
| KN-LIT-3897 | Fine-Grained Cryptography Revisited |  |  | read |
| KN-LIT-3898 | Fine-grained Cryptography? |  |  | read |
| KN-LIT-3899 | Fine-Grained Non-Interactive Key-Exchange: |  |  | read |
| KN-LIT-3900 | Fine-Grained Proxy Re-Encryption: Definitions & Constructions from LWE |  |  | read |
| KN-LIT-3901 | Fine-grained Secure Attribute-based Encryption |  |  | read |
| KN-LIT-3902 | Fine-Grained Secure Computation |  |  | read |
| KN-LIT-3903 | Fine-grained Verifier NIZK and Its Applications |  |  | read |
| KN-LIT-3904 | Fine-Tuning Groth-Sahai Proofs |  |  | read |
| KN-LIT-3905 | Fine-tuning the ISO/IEC Standard LightMAC |  |  | read |
| KN-LIT-3906 | First-Order Side-Channel Attacks on the Permutation Tables Countermeasure |  |  | read |
| KN-LIT-3907 | Fixing and Mechanizing the Security Proof of Fiat-Shamir with Aborts and Dilithium |  |  | read |
| KN-LIT-3908 | Fixing Cracks in the Concrete: Random Oracles with Auxiliary Input, Revisited |  |  | read |
| KN-LIT-3909 | Flash Memory ‘Bumping’ Attacks |  |  | read |
| KN-LIT-3910 | Flashproofs: Efficient Zero-Knowledge Arguments of Range and Polynomial Evaluation with Transparent Setup |  |  | read |
| KN-LIT-3911 | Flaws in Applying Proof Methodologies to Signature Schemes |  |  | read |
| KN-LIT-3912 | Flexible and Efficient Verifiable Computation on Encrypted Data |  |  | read |
| KN-LIT-3913 | FleXOR: Flexible garbling for XOR gates that beats free-XOR |  |  | read |
| KN-LIT-3914 | Floating-Point LLL Revisited |  |  | read |
| KN-LIT-3915 | Fluid MPC: Secure Multiparty Computation with Dynamic Participants Arka Rai Choudhuri1[0000−0003−0452−3426] |  |  | read |
| KN-LIT-3916 | Flush, Gauss, and Reload – A Cache Attack on the BLISS Lattice-Based Signature Scheme |  |  | read |
| KN-LIT-3917 | FO derandomization sometimes damages security |  |  | read |
| KN-LIT-3918 | FOAM: Searching for Hardware-Optimal SPN Structures and Components with a Fair Comparison |  |  | read |
| KN-LIT-3919 | Forgery and Partial Key-Recovery Attacks on |  |  | read |
| KN-LIT-3920 | Forgery Attacks on Several Beyond-Birthday-Bound Secure MACs |  |  | read |
| KN-LIT-3921 | Forging Attacks on two Authenticated |  |  | read |
| KN-LIT-3922 | Fork-Resilient Continuous Group Key Agreement |  |  | read |
| KN-LIT-3923 | Forkcipher: a New Primitive for Authenticated |  |  | read |
| KN-LIT-3924 | Formal Abstractions for Attested Execution Secure Processors |  |  | read |
| KN-LIT-3925 | Formal Verification of Masked Hardware Implementations in the Presence of Glitches Roderick Bloem, Hannes Gross, Rinat Iusupov |  |  | read |
| KN-LIT-3926 | Formal Verification of Saber’s Public-Key |  |  | read |
| KN-LIT-3927 | Formalizing Delayed Adaptive Corruptions and the Security of Flooding Networks |  |  | read |
| KN-LIT-3928 | Formalizing Hash-then-Sign Signatures |  |  | read |
| KN-LIT-3929 | Forward Secret Encrypted RAM: |  |  | read |
| KN-LIT-3930 | Forward-Secure Encryption with Fast Forwarding |  |  | read |
| KN-LIT-3931 | Forward-Secure Signatures with Optimal Signing and Verifying |  |  | read |
| KN-LIT-3932 | Foundations of Group Signatures: Formal |  |  | read |
| KN-LIT-3933 | Foundations of Non-Malleable Hash and One-Way Functions |  |  | read |
| KN-LIT-3934 | Founding Cryptography on Oblivious Transfer – Efficiently |  |  | read |
| KN-LIT-3935 | Founding Cryptography on Tamper-Proof |  |  | read |
| KN-LIT-3936 | Founding Secure Computation on Blockchains |  |  | read |
| KN-LIT-3937 | Four-Dimensional GLV via the Weil Restriction |  |  | read |
| KN-LIT-3938 | Four-Round Black-Box Non-Malleable Schemes from One-Way Permutations |  |  | read |
| KN-LIT-3939 | Four-Round Concurrent Non-Malleable Commitments from One-Way Functions |  |  | read |
| KN-LIT-3940 | FourQ on embedded devices with strong countermeasures against side-channel attacks |  |  | read |
| KN-LIT-3941 | FourQ on FPGA: New Hardware Speed Records for Elliptic Curve Cryptography over Large Prime Characteristic Fields |  |  | read |
| KN-LIT-3942 | FPGA Design of Self-Certified Signature Verification on Koblitz Curves? |  |  | read |
| KN-LIT-3943 | FPGA Implementation of Pairings using |  |  | read |
| KN-LIT-3944 | FPGA Implementation of Point Multiplication on Koblitz Curves Using Kleinian Integers |  |  | read |
| KN-LIT-3945 | FPGA implementations of SPRING And their |  |  | read |
| KN-LIT-3946 | FPGA-based Key Generator for the Niederreiter Cryptosystem using Binary Goppa Codes |  |  | read |
| KN-LIT-3947 | FPGA-based True Random Number Generation using Circuit Metastability with Adaptive Feedback Control |  |  | read |
| KN-LIT-3948 | Fractal: Post-Quantum and Transparent Recursive Proofs from Holography |  |  | read |
| KN-LIT-3949 | Franchised Quantum Money |  |  | read |
| KN-LIT-3950 | Freestart collision for full |  |  | read |
| KN-LIT-3951 | Friet: an Authenticated Encryption Scheme with Built-in Fault Detection |  |  | read |
| KN-LIT-3952 | From 5-pass MQ-based identi cation to MQ-based signatures |  |  | read |
| KN-LIT-3953 | From Collisions to |  |  | read |
| KN-LIT-3954 | From Cryptomania to Obfustopia through Secret-Key Functional Encryption |  |  | read |
| KN-LIT-3955 | From Farfalle to Megafono via Ciminion: The PRF Hydra for MPC Applications |  |  | read |
| KN-LIT-3956 | From FE Combiners to Secure MPC and Back |  |  | read |
| KN-LIT-3957 | From Fixed-Length to Arbitrary-Length RSA Encoding Schemes Revisited |  |  | read |
| KN-LIT-3958 | From Identification to Signatures via the Fiat-Shamir Transform: Minimizing Assumptions for Security and Forward-Security |  |  | read |
| KN-LIT-3959 | From Identification to Signatures, Tightly: |  |  | read |
| KN-LIT-3960 | From Improved Leakage Detection to the Detection of Points of Interests in Leakage Traces |  |  | read |
| KN-LIT-3961 | From Laconic Zero-Knowledge to Public-Key Cryptography |  |  | read |
| KN-LIT-3962 | From Minicrypt to Obfustopia via Private-Key Functional Encryption |  |  | read |
| KN-LIT-3963 | From Non-Adaptive to Adaptive Pseudorandom Functions |  |  | read |
| KN-LIT-3964 | From Obfuscation to the Security of Fiat-Shamir for Proofs |  |  | read |
| KN-LIT-3965 | From Passive to Covert Security at Low Cost |  |  | read |
| KN-LIT-3966 | From Polynomial IOP and Commitments to Non-malleable zkSNARKs Antonio Faonio1[0000−0002−7152−6478] , Dario Fiore2[0000−0001−7274−6600] |  |  | read |
| KN-LIT-3967 | From Private Simultaneous Messages to Zero-Information Arthur-Merlin Protocols and Back? |  |  | read |
| KN-LIT-3968 | From Selective to Adaptive Security in Functional Encryption |  |  | read |
| KN-LIT-3969 | From Selective to Full Security: Semi-Generic Transformations in the Standard Model |  |  | read |
| KN-LIT-3970 | From Single-Input to Multi-Client Inner-Product Functional Encryption |  |  | read |
| KN-LIT-3971 | From Weak to Strong Watermarking |  |  | read |
| KN-LIT-3972 | FSBday: Implementing Wagner’s generalized birthday attack against the SHA-3 round-1 candidate FSB |  |  | read |
| KN-LIT-3973 | Full Domain Hash from (Leveled) Multilinear |  |  | read |
| KN-LIT-3974 | Full Indifferentiable Security of the Xor of Two or More Random Permutations Using the χ2 Method |  |  | read |
| KN-LIT-3975 | Full Key-Recovery Attacks on HMAC/NMAC-MD4 and |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3976 | Full-Domain Subgroup Hiding and Constant-Size Group Signatures |  |  | read |
| KN-LIT-3977 | Full-Hiding (Unbounded) Multi-Input Inner Product Functional Encryption from the k-Linear Assumption |  |  | read |
| KN-LIT-3978 | Full-State Keyed Duplex With Built-In Multi-User Support |  |  | read |
| KN-LIT-3979 | Fully Adaptive |  |  | read |
| KN-LIT-3980 | Fully Adaptive Schnorr Threshold Signatures |  |  | read |
| KN-LIT-3981 | Fully Anonymous Group Signatures without Random Oracles |  |  | read |
| KN-LIT-3982 | Fully Deniable Interactive Encryption 1 2 |  |  | read |
| KN-LIT-3983 | Fully Distributed Threshold RSA under Standard Assumptions |  |  | read |
| KN-LIT-3984 | Fully Dynamic Attribute-Based Signatures for Circuits from Codes |  |  | read |
| KN-LIT-3985 | Fully Homomophic Encryption over the Integers Revisited |  |  | read |
| KN-LIT-3986 | Fully Homomorphic Encryption from Ring-LWE and Security for Key Dependent Messages |  |  | read |
| KN-LIT-3987 | Fully Homomorphic Encryption from the Finite |  |  | read |
| KN-LIT-3988 | Fully Homomorphic Encryption over the Integers |  |  | read |
| KN-LIT-3989 | Fully Homomorphic Encryption over the Integers with Shorter Public Keys Jean-Sébastien |  |  | read |
| KN-LIT-3990 | Fully Homomorphic Encryption with Polylog Overhead |  |  | read |
| KN-LIT-3991 | Fully Homomorphic Encryption with Relatively |  |  | read |
| KN-LIT-3992 | Fully Homomorphic Encryption without Modulus Switching from Classical GapSVP |  |  | read |
| KN-LIT-3993 | Fully Homomorphic Message Authenticators |  |  | read |
| KN-LIT-3994 | Fully Homomorphic NIZK and NIWI Proofs |  |  | read |
| KN-LIT-3995 | Fully Key-Homomorphic Encryption, Arithmetic Circuit ABE and Compact Garbled Circuits? |  |  | read |
| KN-LIT-3996 | Fully Leakage-Resilient Codes |  |  | read |
| KN-LIT-3997 | Fully Leakage-Resilient Signatures |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-3998 | Fully Secure Accountable-Authority Identity-Based Encryption |  |  | read |
| KN-LIT-3999 | Fully Secure Attribute-Based Encryption for t-CNF from LWE |  |  | read |
| KN-LIT-39d9ed | Isogenies and the Discrete Logarithm Problem in Genus Three | 2007 | 11th Workshop on Elliptic Curve Cryptography (ECC 2007), Dublin, 6 September 2007 (talk slides) | read |
| KN-LIT-4000 | Fully Secure Functional Encryption for Inner Products, from Standard Assumptions |  |  | read |
| KN-LIT-4001 | Fully Secure Functional Encryption with General Relations from the Decisional Linear Assumption |  |  | read |
| KN-LIT-4002 | Fully Secure Functional Encryption without Obfuscation |  |  | read |
| KN-LIT-4003 | Fully Secure Functional Encryption: |  |  | read |
| KN-LIT-4004 | Fully Secure Unbounded Inner-Product and Attribute-Based Encryption |  |  | read |
| KN-LIT-4005 | Fully Structure-Preserving Signatures and Shrinking Commitments |  |  | read |
| KN-LIT-4006 | Fully Succinct Batch Arguments for NP from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-4007 | Fully, (Almost) Tightly Secure IBE and Dual System Groups |  |  | read |
| KN-LIT-4008 | Fully-Secure MPC with Minimal Trust |  |  | read |
| KN-LIT-4009 | Fully-succinct Publicly Verifiable Delegation from Constant-Size Assumptions |  |  | read |
| KN-LIT-4010 | Fuming Acid and Cryptanalysis: Handy Tools for |  |  | read |
| KN-LIT-4011 | Function Private Predicate Encryption for Low Min-Entropy Predicates |  |  | read |
| KN-LIT-4012 | Function Secret Sharing? |  |  | read |
| KN-LIT-4013 | Function-Hiding Inner Product Encryption |  |  | read |
| KN-LIT-4014 | Function-Private Functional Encryption in the Private-Key Setting |  |  | read |
| KN-LIT-4015 | Function-Private Identity-Based Encryption: Hiding the Function in Functional Encryption |  |  | read |
| KN-LIT-4016 | Function-Private Subspace-Membership |  |  | read |
| KN-LIT-4017 | Functional Commitments for All Functions, with Transparent Setup and from SIS |  |  | read |
| KN-LIT-4018 | Functional Encryption against Probabilistic Queries: Definition, Construction and Applications |  |  | read |
| KN-LIT-4019 | Functional Encryption for Attribute-Weighted Sums from k-Lin |  |  | read |
| KN-LIT-4020 | Functional Encryption for Inner Product Predicates from Learning with Errors |  |  | read |
| KN-LIT-4021 | Functional Encryption for Inner Product with Full Function Privacy |  |  | read |
| KN-LIT-4022 | Functional Encryption for Inner Product: Achieving Constant-Size Ciphertexts with Adaptive Security or Support for Negation |  |  | read |
| KN-LIT-4023 | Functional Encryption for Quadratic Functions from k-Lin, Revisited Hoeteck Wee |  |  | read |
| KN-LIT-4024 | Functional Encryption for Randomized Functionalities in the Private-Key Setting from Minimal Assumptions |  |  | read |
| KN-LIT-4025 | Functional Encryption for Regular Languages |  |  | read |
| KN-LIT-4026 | Functional Encryption for Threshold Functions (or Fuzzy IBE) from Lattices |  |  | read |
| KN-LIT-4027 | Functional Encryption for Turing Machines |  |  | read |
| KN-LIT-4028 | Functional Encryption for Turing Machines with Dynamic Bounded Collusion from LWE |  |  | read |
| KN-LIT-4029 | Functional Encryption from (Small) Hardware Tokens |  |  | read |
| KN-LIT-4030 | Functional Encryption with Bounded Collusions via Multi-Party Computation |  |  | read |
| KN-LIT-4031 | Functional Encryption with Secure Key Leasing |  |  | read |
| KN-LIT-4032 | Functional Encryption: |  |  | read |
| KN-LIT-4033 | Functional Encryption: Definitions and Challenges |  |  | read |
| KN-LIT-4034 | Functional Encryption: Deterministic to Randomized Functions from Simple Assumptions |  |  | read |
| KN-LIT-4035 | Functional Encryption: New Perspectives and Lower Bounds |  |  | read |
| KN-LIT-4036 | Functional Graph Revisited: Updates on (Second) Preimage Attacks on Hash Combiners |  |  | read |
| KN-LIT-4037 | Functional Re-encryption and Collusion-Resistant Obfuscation |  |  | read |
| KN-LIT-4038 | Functional Signatures and Pseudorandom Functions |  |  | read |
| KN-LIT-4039 | Further Hidden Markov Model Cryptanalysis |  |  | read |
| KN-LIT-4040 | Further Observations on Optimistic Fair Exchange Protocols in the Multi-user Setting |  |  | read |
| KN-LIT-4041 | Further Observations on the Structure of the AES Algorithm |  |  | read |
| KN-LIT-4042 | Further Simplifications in Proactive RSA Signatures |  |  | read |
| KN-LIT-4043 | Fuzzy Asymmetric Password-Authenticated Key Exchange |  |  | read |
| KN-LIT-4044 | Fuzzy Extractors: How to Generate Strong Keys from Biometrics and Other Noisy Data |  |  | read |
| KN-LIT-4045 | Fuzzy Password-Authenticated Key Exchange |  |  | read |
| KN-LIT-4046 | G+G: A Fiat-Shamir Lattice Signature Based on Convolved Gaussians |  |  | read |
| KN-LIT-4047 | Game Theoretic Notions of Fairness in Multi-Party Coin Toss? |  |  | read |
| KN-LIT-4048 | Game-Theoretic Fairness Meets Multi-Party Protocols: The Case of Leader Election |  |  | read |
| KN-LIT-4049 | Games and the Impossibility of Realizable Ideal Functionality |  |  | read |
| KN-LIT-4050 | Garbled Circuits Checking Garbled Circuits: |  |  | read |
| KN-LIT-4051 | Garbled Circuits for Leakage-Resilience: Hardware Implementation and Evaluation of One-Time Programs? Kimmo Järvinen1 |  |  | read |
| KN-LIT-4052 | Garbled Circuits With Sublinear Evaluator |  |  | read |
| KN-LIT-4053 | Garbled RAM Revisited |  |  | read |
| KN-LIT-4054 | Garbling XOR Gates “For Free” in the Standard Model |  |  | read |
| KN-LIT-4055 | Garbling, Stacked and Staggered Faster k-out-of-n Garbled Function Evaluation |  |  | read |
| KN-LIT-4056 | Gate Evaluation Secret Sharing And Secure One-Round Two-Party Computation |  |  | read |
| KN-LIT-4057 | Gate-Level Masking Under a Path-Based Leakage Metric |  |  | read |
| KN-LIT-4058 | Gaussian Sampling over the Integers: Efficient, Generic, Constant-Time |  |  | read |
| KN-LIT-4059 | GCM Security Bounds Reconsidered |  |  | read |
| KN-LIT-4060 | GCM, GHASH and Weak Keys |  |  | read |
| KN-LIT-4061 | Gemini: Elastic SNARKs for Diverse Environments |  |  | read |
| KN-LIT-4062 | General Ad Hoc Encryption from Exponent Inversion IBE |  |  | read |
| KN-LIT-4063 | General Hardness Amplification of Predicates and Puzzles ? |  |  | read |
| KN-LIT-4064 | General Impossibility of Group Homomorphic |  |  | read |
| KN-LIT-4065 | General Linear Group Action on Tensors: A Candidate for Post-Quantum Cryptography? |  |  | read |
| KN-LIT-4066 | General Properties of Quantum Bit Commitments |  |  | read |
| KN-LIT-4067 | General Properties of Quantum Zero-Knowledge Proofs |  |  | read |
| KN-LIT-4068 | General Statistically Secure Computation with Bounded-Resettable Hardware Tokens |  |  | read |
| KN-LIT-4069 | Generalized Channels from Limited Blockchain |  |  | read |
| KN-LIT-4070 | Generalized Environmental Security From Number Theoretic Assumptions |  |  | read |
| KN-LIT-4071 | Generalized Fuzzy Password-Authenticated Key Exchange from Error Correcting Codes |  |  | read |
| KN-LIT-4072 | Generalized Identity Based and Broadcast Encryption Schemes |  |  | read |
| KN-LIT-4073 | Generalized Polynomial Decomposition for S-boxes with Application to Side-Channel Countermeasures |  |  | read |
| KN-LIT-4074 | Generalized Powering Functions and their Application to Digital Signatures |  |  | read |
| KN-LIT-4075 | Generalized Proofs of Knowledge with Fully Dynamic Setup |  |  | read |
| KN-LIT-4076 | Generalized Pseudorandom Secret Sharing and Efficient Straggler-Resilient Secure Computation |  |  | read |
| KN-LIT-4077 | Generalized Special-Sound Interactive Proofs and their Knowledge Soundness |  |  | read |
| KN-LIT-4078 | Generating Genus two Hyperelliptic Curves over Large Characteristic Finite Fields |  |  | read |
| KN-LIT-4079 | Generating Provable Primes Efficiently on Embedded Devices |  |  | read |
| KN-LIT-4080 | Generic and Practical Resettable Zero-Knowledge in the Bare Public-Key Model? |  |  | read |
| KN-LIT-4081 | Generic Attack on Duplex-Based AEAD Modes using Random Function Statistics |  |  | read |
| KN-LIT-4082 | Generic Attacks against Beyond-Birthday-Bound MACs |  |  | read |
| KN-LIT-4083 | Generic Attacks on Feistel Schemes |  |  | read |
| KN-LIT-4084 | Generic Attacks on Unbalanced Feistel Schemes with Contracting Functions |  |  | read |
| KN-LIT-4085 | Generic Authenticated Key Exchange in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-4086 | Generic Compiler for Publicly Verifiable Covert Multi-Party Computation |  |  | read |
| KN-LIT-4087 | Generic Compilers for Authenticated Key Exchange? |  |  | read |
| KN-LIT-4088 | Generic Constructions for Chosen-Ciphertext Secure Attribute Based Encryption |  |  | read |
| KN-LIT-4089 | Generic Constructions of Robustly Reusable Fuzzy Extractor |  |  | read |
| KN-LIT-4090 | Generic Framework for Key-Guessing Improvements |  |  | read |
| KN-LIT-4091 | Generic Hardness of the Multiple |  |  | read |
| KN-LIT-4092 | Generic Homomorphic Undeniable Signatures |  |  | read |
| KN-LIT-4093 | Generic Key Recovery Attack on Feistel Scheme |  |  | read |
| KN-LIT-4094 | Generic Lower Bounds for Root Extraction and Signature Schemes in General Groups |  |  | read |
| KN-LIT-4095 | Generic Models for Group Actions Julien Duman , Dominik Hartmann , Eike Kiltz |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4096 | Generic Negation of Pair Encodings |  |  | read |
| KN-LIT-4097 | Generic On-line/Off-line Threshold Signatures |  |  | read |
| KN-LIT-4098 | Generic Related-key Attacks for HMAC |  |  | read |
| KN-LIT-4099 | Generic Security of NMAC and HMAC with Input Whitening |  |  | read |
| KN-LIT-4100 | Generic Security of the SAFE API and Its Applications |  |  | read |
| KN-LIT-4101 | Generic Side-Channel Countermeasures for Reconfigurable Devices? |  |  | read |
| KN-LIT-4102 | Generic Side-Channel Distinguishers: Improvements and Limitations |  |  | read |
| KN-LIT-4103 | Generic Transformations of Predicate Encodings: Constructions and Applications |  |  | read |
| KN-LIT-4104 | Generic Universal Forgery Attack on Iterative Hash-based MACs |  |  | read |
| KN-LIT-4105 | Generic-Group Delay Functions Require Hidden-Order Groups |  |  | read |
| KN-LIT-4106 | Generic-Group Lower Bounds via Reductions Between Geometric-Search Problems: |  |  | read |
| KN-LIT-4107 | Generically Speeding-Up Repeated Squaring is Equivalent to Factoring: Sharp Thresholds for All Generic-Ring Delay Functions |  |  | read |
| KN-LIT-4108 | Gentry-Wichs Is Tight: A Falsifiable Non-Adaptively Sound SNARG |  |  | read |
| KN-LIT-4109 | Genus 2 Curves with Split Jacobians |  |  | read |
| KN-LIT-4110 | Get Your Hands Off My Laptop: Physical Side-Channel Key-Extraction Attacks on PCs |  |  | read |
| KN-LIT-4111 | GGH15 Beyond Permutation Branching Programs: Proofs, Attacks, and Candidates |  |  | read |
| KN-LIT-4112 | GGHLite: More Efficient Multilinear Maps from Ideal Lattices |  |  | read |
| KN-LIT-4113 | GIFT: A Small Present Towards Reaching the Limit of Lightweight Encryption |  |  | read |
| KN-LIT-4114 | Gimli: a cross-platform permutation |  |  | read |
| KN-LIT-4115 | Giving an Adversary Guarantees (Or: How to Model Designated Verifier Signatures in a Composable Framework) |  |  | read |
| KN-LIT-4116 | Gladius: LWR based efficient hybrid public key encryption with distributed decryption |  |  | read |
| KN-LIT-4117 | GLUE: Generalizing Unbounded Attribute-Based Encryption for Flexible |  |  | read |
| KN-LIT-4118 | GLV/GLS Decomposition, Power Analysis, and Attacks on ECDSA Signatures With Single-Bit Nonce Bias |  |  | read |
| KN-LIT-4119 | GNUC: A New Universal Composability Framework |  |  | read |
| KN-LIT-4120 | Going Beyond Dual Execution: MPC for Functions with Efficient Verification |  |  | read |
| KN-LIT-4121 | Good is Not Good Enough |  |  | read |
| KN-LIT-4122 | Gossiping for Communication-Efficient Broadcast |  |  | read |
| KN-LIT-4123 | GQ and Schnorr Identification Schemes: Proofs of Security against Impersonation under |  |  | read |
| KN-LIT-4124 | Graded Encoding Schemes from Obfuscation |  |  | read |
| KN-LIT-4125 | Graph Design for Secure Multiparty Computation over Non-Abelian Groups |  |  | read |
| KN-LIT-4126 | Graph-Decomposition-Based Frameworks for Subset-Cover Broadcast Encryption and Efficient Instantiations |  |  | read |
| KN-LIT-4127 | Graph-Induced Multilinear Maps from Lattices |  |  | read |
| KN-LIT-4128 | Graph-Theoretic Algorithms for the Alternating |  |  | read |
| KN-LIT-4129 | Graph-Theoretic Algorithms for the “Isomorphism of Polynomials” Problem |  |  | read |
| KN-LIT-4130 | Groth–Sahai proofs revisited |  |  | read |
| KN-LIT-4131 | Group Action Key Encapsulation and Non-Interactive Key Exchange in the QROM Julien Duman , Dominik Hartmann , Eike Kiltz |  |  | read |
| KN-LIT-4132 | Group Diffie-Hellman Key Exchange Secure Against Dictionary Attacks |  |  | read |
| KN-LIT-4133 | Group Encryption |  |  | read |
| KN-LIT-4134 | Group Encryption: Full Dynamicity, Message |  |  | read |
| KN-LIT-4135 | Group Encryption: Non-Interactive Realization in the Standard Model |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4136 | Group Signatures from Lattices: Simpler, Tighter, Shorter, Ring-based |  |  | read |
| KN-LIT-4137 | Group Signatures with Almost-for-free Revocation |  |  | read |
| KN-LIT-4138 | Group Signatures with Selective Linkability |  |  | read |
| KN-LIT-4139 | Group Signatures with User-Controlled and Sequential Linkability |  |  | read |
| KN-LIT-4140 | Group Signatures without NIZK: From Lattices in the Standard Model |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4141 | Group to Group Commitments Do Not Shrink |  |  | read |
| KN-LIT-4142 | Group-Based Secure Computation: Optimizing Rounds, Communication, and Computation |  |  | read |
| KN-LIT-4143 | Grover Meets Simon – Quantumly Attacking the FX-construction |  |  | read |
| KN-LIT-4144 | Grover vs. McEliece |  |  | read |
| KN-LIT-4145 | Guaranteed Output Delivery Comes Free in Honest Majority MPC |  |  | read |
| KN-LIT-4146 | GUC-Secure Commitments via Random Oracles: |  |  | read |
| KN-LIT-4147 | Guess-and-determine Algebraic Attack on the Self-Shrinking Generator? |  |  | read |
| KN-LIT-4148 | Half-Tree: Halving the Cost of Tree Expansion |  |  | read |
| KN-LIT-4149 | Halo Infinite: Proof-Carrying Data from Additive Polynomial Commitments |  |  | read |
| KN-LIT-4150 | Handling Adaptive Compromise for Practical Encryption Schemes |  |  | read |
| KN-LIT-4151 | Handling Expected Polynomial-Time Strategies in Simulation-Based Security Proofs |  |  | read |
| KN-LIT-4152 | Hard-Core Predicates for a Diffie-Hellman Problem over Finite Fields |  |  | read |
| KN-LIT-4153 | Hardening Signature Schemes via Derive-then-Derandomize: Stronger Security Proofs for EdDSA |  |  | read |
| KN-LIT-4154 | Hardness amplification of weakly verifiable puzzles |  |  | read |
| KN-LIT-4155 | Hardness of Computing Individual Bits for One-way Functions on Elliptic Curves |  |  | read |
| KN-LIT-4156 | Hardness of k-LWE and Applications in Traitor Tracing |  |  | read |
| KN-LIT-4157 | Hardness of Non-Interactive Differential Privacy from One-Way Functions |  |  | read |
| KN-LIT-4158 | Hardness of SIS and LWE with Small Parameters |  |  | read |
| KN-LIT-4159 | Hardness Preserving Constructions of Pseudorandom Functions |  |  | read |
| KN-LIT-4160 | Hardness Preserving Reductions via Cuckoo Hashing |  |  | read |
| KN-LIT-4161 | Hardware Acceleration of the Tate Pairing in Characteristic Three ? |  |  | read |
| KN-LIT-4162 | Hardware Accelerator for the Tate Pairing in Characteristic Three Based on Karatsuba-Ofman Multipliers |  |  | read |
| KN-LIT-4163 | Hardware/Software Co-design for Hyperelliptic Curve Cryptography (HECC) on the 8051 μP |  |  | read |
| KN-LIT-4164 | Hardware/Software Co-Design of Elliptic Curve Cryptography on an 8051 Microcontroller Manuel Koschuch, Joachim Lechner, Andreas Weitzer, Johann Großschädl |  |  | read |
| KN-LIT-4165 | Hash Function Balance and its Impact on Birthday Attacks |  |  | read |
| KN-LIT-4166 | Hash Functions and RFID Tags: |  |  | read |
| KN-LIT-4167 | Hash Functions and the (Amplified) Boomerang Attack |  |  | read |
| KN-LIT-4168 | Hash Functions Based on Three Permutations: A Generic Security Analysis |  |  | read |
| KN-LIT-4169 | Hash Functions from Sigma Protocols and Improvements to VSH |  |  | read |
| KN-LIT-4170 | Hash Proof Systems over Lattices Revisited |  |  | read |
| KN-LIT-4171 | Hash-Function based PRFs: AMAC and its Multi-User Security |  |  | read |
| KN-LIT-4172 | Hashing Garbled Circuits for Free |  |  | read |
| KN-LIT-4173 | Hashing solutions instead of generating problems: On the interactive certification of RSA moduli? |  |  | read |
| KN-LIT-4174 | Hawk: Module LIP makes Lattice Signatures Fast, Compact and Simple |  |  | read |
| KN-LIT-4175 | HBS: A Single-Key Mode of Operation for Deterministic Authenticated Encryption |  |  | read |
| KN-LIT-4176 | Hedged Nonce-Based Public-Key Encryption: |  |  | read |
| KN-LIT-4177 | Hedged Public-Key Encryption: |  |  | read |
| KN-LIT-4178 | Hedging Public-Key Encryption in the Real World |  |  | read |
| KN-LIT-4179 | Hello, Thank you very much for looking at my book, Elementary Number Theory and Elliptic Curves. This book is slated for publication in Springer-Verlag’s Undergraduate |  |  | read |
| KN-LIT-4180 | Herding Hash Functions and the Nostradamus Attack |  |  | read |
| KN-LIT-4181 | HERMES: Efficient Ring Packing using MLWE |  |  | read |
| KN-LIT-4182 | Hermes: I/O-Efficient Forward-Secure Searchable Symmetric Encryption |  |  | read |
| KN-LIT-4183 | Heuristic Tool for Linear Cryptanalysis with Applications to CAESAR Candidates |  |  | read |
| KN-LIT-4184 | Heuristics for the arithmetic of elliptic curves |  |  | read |
| KN-LIT-4185 | HIBE with Short Public Parameters Without Random Oracle |  |  | read |
| KN-LIT-4186 | Hidden Cosets and Applications to Unclonable Cryptography |  |  | read |
| KN-LIT-4187 | Hidden Number Problem with the Trace and Bit Security of XTR and LUC |  |  | read |
| KN-LIT-4188 | Hidden Shift Quantum Cryptanalysis and Implications |  |  | read |
| KN-LIT-4189 | Hidden Stabilizers, the Isogeny To Endomorphism Ring Problem and the Cryptanalysis of pSIDH |  |  | read |
| KN-LIT-4190 | Hiding in Plain Sight: Memory-tight Proofs via Randomness Programming |  |  | read |
| KN-LIT-4191 | Hiding Secrecy Leakage in Leaky Helper Data |  |  | read |
| KN-LIT-4192 | Hiding the Input-Size in Secure Two-Party Computation? |  |  | read |
| KN-LIT-4193 | Hierarchical ID-Based Cryptography |  |  | read |
| KN-LIT-4194 | Hierarchical Identity Based Encryption with Constant Size Ciphertext? |  |  | read |
| KN-LIT-4195 | Hierarchical Identity Based Encryption with Polynomially Many Levels |  |  | read |
| KN-LIT-4196 | Hierarchical Identity-Based Encryption with Tight Multi-Challenge Security |  |  | read |
| KN-LIT-4197 | Hierarchical Integrated Signature and Encryption (or: Key Separation vs. Key Reuse: Enjoy the Best of Both Worlds) |  |  | read |
| KN-LIT-4198 | High Order Linearization Equation (HOLE) Attack on Multivariate Public Key Cryptosystems |  |  | read |
| KN-LIT-4199 | High Speed Cryptoprocessor for ηT Pairing on 128-bit Secure Supersingular Elliptic Curves over Characteristic Two Fields |  |  | read |
| KN-LIT-4200 | High-order Attacks against the Exponent Splitting Protection |  |  | read |
| KN-LIT-4201 | High-Order Conversion From Boolean to Arithmetic Masking Jean-Sébastien Coron |  |  | read |
| KN-LIT-4202 | High-performance Concurrent Error Detection Scheme for AES Hardware |  |  | read |
| KN-LIT-4203 | High-Performance Scalar Multiplication using 8-Dimensional GLV/GLS Decomposition |  |  | read |
| KN-LIT-4204 | High-Precision Bootstrapping for Approximate |  |  | read |
| KN-LIT-4205 | High-Precision Bootstrapping of RNS-CKKS |  |  | read |
| KN-LIT-4206 | High-speed high-security signatures |  |  | read |
| KN-LIT-4207 | High-speed key encapsulation from NTRU |  |  | read |
| KN-LIT-4208 | High-Throughput Secure Three-Party Computation for Malicious Adversaries and an Honest Majority |  |  | read |
| KN-LIT-4209 | Higher Order Differential Attack on Step-Reduced Variants of Luffa v1 |  |  | read |
| KN-LIT-4210 | Higher Order Masking of Look-up Tables Jean-Sébastien Coron |  |  | read |
| KN-LIT-4211 | Higher Order Universal One-Way Hash Functions from the Subset Sum Assumption |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4212 | Higher Order Universal One-Way Hash Functions? |  |  | read |
| KN-LIT-4213 | Higher-Order Differential Meet-in-The-Middle Preimage Attacks on SHA-1 and BLAKE |  |  | read |
| KN-LIT-4214 | Higher-order differential properties of Keccak and Luffa ? |  |  | read |
| KN-LIT-4215 | Higher-Order Glitches Free Implementation of the AES using Secure Multi-Party Computation Protocols |  |  | read |
| KN-LIT-4216 | Higher-Order Masking Schemes for S-Boxes |  |  | read |
| KN-LIT-4217 | Higher-Order Side Channel Security and Mask Refreshing |  |  | read |
| KN-LIT-4218 | Higher-Order Threshold Implementations |  |  | read |
| KN-LIT-4219 | Highly Efficient Key |  |  | read |
| KN-LIT-4220 | Highly Efficient OT-Based Multiplication Protocols |  |  | read |
| KN-LIT-4221 | Highly Efficient GF (28 ) Inversion Circuit Based on Redundant GF Arithmetic and Its Application to AES Design |  |  | read |
| KN-LIT-4222 | Highly Regular Right-to-Left Algorithms for Scalar Multiplication |  |  | read |
| KN-LIT-4223 | Highly-Efficient Universally-Composable Commitments based on the DDH Assumption |  |  | read |
| KN-LIT-4224 | Highly-Scalable Searchable Symmetric |  |  | read |
| KN-LIT-4225 | HIGHT: A New Block Cipher Suitable for Low-Resource Device ? |  |  | read |
| KN-LIT-4226 | HMQV: A High-Performance Secure Diffie-Hellman Protocol |  |  | read |
| KN-LIT-4227 | Holographic SNARGs for P and Batch-NP from (Polynomially Hard) Learning with Errors |  |  | read |
| KN-LIT-4228 | Homomorphic Authenticated Encryption Secure Against Chosen-Ciphertext Attack |  |  | read |
| KN-LIT-4229 | Homomorphic Encryption for Arithmetic of Approximate Numbers |  |  | read |
| KN-LIT-4230 | Homomorphic Encryption for Finite Automata |  |  | read |
| KN-LIT-4231 | Homomorphic Encryption from Learning with Errors: Conceptually-Simpler, Asymptotically-Faster, Attribute-Based |  |  | read |
| KN-LIT-4232 | Homomorphic Encryption: from Private-Key to Public-Key |  |  | read |
| KN-LIT-4233 | Homomorphic Evaluation of the AES Circuit |  |  | read |
| KN-LIT-4234 | Homomorphic evaluation requires depth |  |  | read |
| KN-LIT-4235 | Homomorphic Lower Digits Removal and Improved FHE Bootstrapping |  |  | read |
| KN-LIT-4236 | Homomorphic Network Coding Signatures in the Standard Model |  |  | read |
| KN-LIT-4237 | Homomorphic polynomial evaluation using Galois |  |  | read |
| KN-LIT-4238 | Homomorphic Secret Sharing for Low Degree Polynomials |  |  | read |
| KN-LIT-4239 | Homomorphic Secret Sharing from Lattices Without FHE |  |  | read |
| KN-LIT-4240 | Homomorphic Signatures for Polynomial Functions |  |  | read |
| KN-LIT-4241 | Homomorphic Signatures with Efficient Verification for Polynomial Functions |  |  | read |
| KN-LIT-4242 | Homomorphic SIM2 D Operations: Single Instruction Much More Data |  |  | read |
| KN-LIT-4243 | Homomorphic Time-Lock Puzzles and Applications |  |  | read |
| KN-LIT-4244 | Honey Encryption: Security Beyond the Brute-Force Bound |  |  | read |
| KN-LIT-4245 | Horizontal Side-Channel Attacks and Countermeasures on the ISW Masking Scheme |  |  | read |
| KN-LIT-4246 | Horst Meets Fluid -SPN: Griffin for Zero-Knowledge Applications ? |  |  | read |
| KN-LIT-4247 | Hosting Services on an Untrusted Cloud |  |  | read |
| KN-LIT-4248 | How Far Can We Go Beyond Linear Cryptanalysis? |  |  | read |
| KN-LIT-4249 | How Far Can We Go on the x64 Processors? |  |  | read |
| KN-LIT-4250 | How Far Should Theory be from Practice? – Evaluation of a Countermeasure |  |  | read |
| KN-LIT-4251 | How Fast Can Higher-Order Masking Be in Software? |  |  | read |
| KN-LIT-4252 | How Low Can We Go? |  |  | read |
| KN-LIT-4253 | How Many Oblivious Transfers are Needed for Secure Multiparty Computation?? |  |  | read |
| KN-LIT-4254 | How not to Prove Yourself: Pitfalls of the Fiat-Shamir Heuristic and Applications to Helios |  |  | read |
| KN-LIT-4255 | How Risky is the Random-Oracle Model? |  |  | read |
| KN-LIT-4256 | How Secure is AES under Leakage |  |  | read |
| KN-LIT-4257 | How Should We Solve Search Problems Privately? |  |  | read |
| KN-LIT-4258 | How to achieve a McEliece-based Digital Signature Scheme |  |  | read |
| KN-LIT-4259 | How to Achieve Perfect Simulation and A Complete Problem for Non-interactive Perfect Zero-Knowledge |  |  | read |
| KN-LIT-4260 | How to Avoid Obfuscation Using Witness PRFs |  |  | read |
| KN-LIT-4261 | How to Break MD5 and Other Hash Functions |  |  | read |
| KN-LIT-4262 | How to Break Secure |  |  | read |
| KN-LIT-4263 | How to Build a Trapdoor Function from an Encryption Scheme |  |  | read |
| KN-LIT-4264 | How to Build Fully Secure Tweakable Blockciphers from Classical Blockciphers |  |  | read |
| KN-LIT-4265 | How to Build Optimally Secure PRFs Using Block Ciphers |  |  | read |
| KN-LIT-4266 | How to Build Pseudorandom Functions From Public Random Permutations |  |  | read |
| KN-LIT-4267 | How to Certify the Leakage of a Chip? |  |  | read |
| KN-LIT-4268 | How to Compile Polynomial IOP into Simulation-Extractable SNARKs: A Modular Approach |  |  | read |
| KN-LIT-4269 | How to Compress Encrypted Data |  |  | read |
| KN-LIT-4270 | How to Compress Rabin Ciphertexts and Signatures (and More) |  |  | read |
| KN-LIT-4271 | How to Compute under AC 0 Leakage without Secure Hardware |  |  | read |
| KN-LIT-4272 | How to Construct an Ideal Cipher from a Small Set of Public Permutations |  |  | read |
| KN-LIT-4273 | How to Delegate and Verify in Public: Verifiable Computation from Attribute-based Encryption |  |  | read |
| KN-LIT-4274 | How to Disembed a Program? |  |  | read |
| KN-LIT-4275 | How to Eat Your Entropy and Have it Too — Optimal Recovery Strategies for Compromised RNGs |  |  | read |
| KN-LIT-4276 | How to Efficiently Evaluate RAM Programs with Malicious Security |  |  | read |
| KN-LIT-4277 | How to Enhance the Security of the 3GPP |  |  | read |
| KN-LIT-4278 | How to Estimate the Success Rate of Higher-Order Side-Channel Attacks Victor Lomné1 |  |  | read |
| KN-LIT-4279 | How to Extract Useful Randomness from Unreliable Sources |  |  | read |
| KN-LIT-4280 | How to Fake Auxiliary Input |  |  | read |
| KN-LIT-4281 | HOW TO FIND SMALL FACTORS OF INTEGERS |  |  | read |
| KN-LIT-4282 | HOW TO FIND SMOOTH PARTS OF INTEGERS |  |  | read |
| KN-LIT-4283 | How to Fool an Unbounded Adversary with a Short Key |  |  | read |
| KN-LIT-4284 | How to Generalize RSA Cryptanalyses |  |  | read |
| KN-LIT-4285 | How to Hash into Elliptic Curves |  |  | read |
| KN-LIT-4286 | How to Hide Circuits in MPC An Efficient Framework for Private Function Evaluation |  |  | read |
| KN-LIT-4287 | How to Improve Rebound Attacks Marı́a Naya-Plasencia |  |  | read |
| KN-LIT-4288 | How to Leak a Secret |  |  | read |
| KN-LIT-4289 | How to leverage hardness of constant-degree expanding polynomials over R to build iO ? |  |  | read |
| KN-LIT-4290 | How to manipulate curve standards: a white paper for the black hat |  |  | read |
| KN-LIT-4291 | How to Maximize Software Performance of Symmetric Primitives on Pentium III and 4 Processors |  |  | read |
| KN-LIT-4292 | How to Maximize the Potential of FPGA Resources for Modular Exponentiation |  |  | read |
| KN-LIT-4293 | How to Meet Ternary LWE Keys |  |  | read |
| KN-LIT-4294 | How to Obfuscate MPC Inputs |  |  | read |
| KN-LIT-4295 | How to Obfuscate Programs Directly |  |  | read |
| KN-LIT-4296 | How to Obtain Fully Structure-Preserving (Automorphic) Signatures from Structure-Preserving Ones |  |  | read |
| KN-LIT-4297 | How to prove knowledge of small secrets |  |  | read |
| KN-LIT-4298 | How to Record Quantum Queries, and Applications to Quantum Indifferentiability |  |  | read |
| KN-LIT-4299 | How to Recover a Secret with O(n) Additions? |  |  | read |
| KN-LIT-4300 | How to Run Turing Machines on Encrypted Data |  |  | read |
| KN-LIT-4301 | How to Sample a Discrete Gaussian (and more) from a Random Oracle |  |  | read |
| KN-LIT-4302 | How to Securely Compute with Noisy Leakage in Quasilinear Complexity |  |  | read |
| KN-LIT-4303 | How To Securely Outsource Cryptographic Computations |  |  | read |
| KN-LIT-4304 | How to Securely Release Unverified Plaintext in Authenticated Encryption |  |  | read |
| KN-LIT-4305 | How to Sequentialize Independent Parallel Attacks? Biased Distributions Have a Phase Transition |  |  | read |
| KN-LIT-4306 | How To Shuffle in Public |  |  | read |
| KN-LIT-4307 | How to strengthen pseudo-random generators by using compression? |  |  | read |
| KN-LIT-4308 | HOW TO STRETCH RANDOM FUNCTIONS: THE SECURITY OF PROTECTED COUNTER SUMS |  | Journal of Cryptology | read |
| KN-LIT-4309 | How to Thwart Birthday Attacks against MACs via Small Randomness |  |  | read |
| KN-LIT-4310 | How to Use (Plain) Witness Encryption: |  |  | read |
| KN-LIT-4311 | How to Use Bitcoin to Design Fair Protocols |  |  | read |
| KN-LIT-4312 | How to Use Metaheuristics for Design of Symmetric-Key Primitives |  |  | read |
| KN-LIT-4313 | How to Watermark Cryptographic Functions |  |  | read |
| KN-LIT-4314 | Hull Attacks on the Lattice Isomorphism Problem |  |  | read |
| KN-LIT-4315 | Hunting and Gathering – Verifiable Random Functions from Standard Assumptions with Short Proofs |  |  | read |
| KN-LIT-4316 | Hybrid Consensus: Efficient Consensus in the Permissionless Model |  |  | read |
| KN-LIT-4317 | Hybrid Encryption in a Multi-User Setting, Revisited? |  |  | read |
| KN-LIT-4318 | Hyper-Encryption against Space-Bounded Adversaries from On-Line Strong Extractors |  |  | read |
| KN-LIT-4319 | Hypercubic Lattice Reduction and Analysis of |  |  | read |
| KN-LIT-4320 | HYPERGEOMETRIC L-FUNCTIONS IN AVERAGE |  |  | read |
| KN-LIT-4321 | HyperPlonk: Plonk with Linear-Time Prover and High-Degree Custom Gates |  |  | read |
| KN-LIT-4322 | i-Hop Homomorphic Encryption and Rerandomizable Yao Circuits |  |  | read |
| KN-LIT-4323 | IBE with Incompressible Master Secret and Small Identity Secrets |  |  | read |
| KN-LIT-4324 | ICEBERG : an Involutional Cipher Efficient for Block Encryption in Reconfigurable Hardware. Francois-Xavier Standaert, Gilles Piret, Gael Rouvroy |  |  | read |
| KN-LIT-4325 | ICEPOLE: High-speed |  |  | read |
| KN-LIT-4326 | ID-Based Blind Signature and Ring Signature from Pairings |  |  | read |
| KN-LIT-4327 | Ideal-SVP is Hard for Small-Norm Uniform Prime Ideals |  |  | read |
| KN-LIT-4328 | Idealizing Identity-Based Encryption |  |  | read |
| KN-LIT-4329 | Identification Protocols and Signature Schemes Based on Supersingular Isogeny Problems |  |  | read |
| KN-LIT-4330 | Identifying Cheaters Without an Honest Majority |  |  | read |
| KN-LIT-4331 | Identity-Based Aggregate and Multi-Signature Schemes based on RSA |  |  | read |
| KN-LIT-4332 | Identity-Based Aggregate Signatures |  |  | read |
| KN-LIT-4333 | Identity-Based Broadcast Encryption with |  |  | read |
| KN-LIT-4334 | Identity-based Broadcast Encryption with Efficient Revocation |  |  | read |
| KN-LIT-4335 | Identity-Based Cryptosystems and Quadratic Residuosity |  |  | read |
| KN-LIT-4336 | Identity-Based Encryption for Fair Anonymity Applications: Defining, Implementing, and |  |  | read |
| KN-LIT-4337 | Identity-based Encryption from Codes with Rank Metric |  |  | read |
| KN-LIT-4338 | Identity-Based Encryption from the Diffie-Hellman Assumption? |  |  | read |
| KN-LIT-4339 | Identity-Based Encryption from the Weil Pairing |  |  | read |
| KN-LIT-4340 | Identity-Based Encryption Resilient to Continual Auxiliary Leakage |  |  | read |
| KN-LIT-4341 | Identity-Based Encryption Secure |  |  | read |
| KN-LIT-4342 | Identity-Based Encryption Secure Against Selective Opening Attack |  |  | read |
| KN-LIT-4343 | Identity-based Encryption Tightly Secure under Chosen-ciphertext Attacks |  |  | read |
| KN-LIT-4344 | Identity-based encryption with (almost) tight security in the multi-instance, multi-ciphertext setting |  |  | read |
| KN-LIT-4345 | Identity-based Hierarchical Key-insulated Encryption without Random Oracles |  |  | read |
| KN-LIT-4346 | Identity-Based Hierarchical Strongly |  |  | read |
| KN-LIT-4347 | Identity-Based Lossy Trapdoor Functions: |  |  | read |
| KN-LIT-4348 | Identity-Based Matchmaking Encryption from Standard Assumptions |  |  | read |
| KN-LIT-4349 | Identity-Based Threshold Decryption |  |  | read |
| KN-LIT-4350 | Identity-Based Traitor Tracing Michel Abdalla1 , Alexander W. Dent2 , John Malone-Lee3 |  |  | read |
| KN-LIT-4351 | Immunizing Backdoored PRGs |  |  | read |
| KN-LIT-4352 | Immunizing Encryption Schemes from Decryption Errors |  |  | read |
| KN-LIT-4353 | Implementing a Feasible Attack against ECC2K-130 Certicom Challenge |  |  | read |
| KN-LIT-4354 | Implementing BP-Obfuscation Using Graph-Induced Encoding |  |  | read |
| KN-LIT-4355 | Implementing Candidate Graded Encoding Schemes from Ideal Lattices |  |  | read |
| KN-LIT-4356 | Implementing Cryptographic Pairings on Smartcards |  |  | read |
| KN-LIT-4357 | Implementing Gentry’s Fully-Homomorphic Encryption Scheme |  |  | read |
| KN-LIT-4358 | Implementing Resettable UC-functionalities with Untrusted Tamper-proof Hardware-Tokens |  |  | read |
| KN-LIT-4359 | Implementing the Elliptic |  |  | read |
| KN-LIT-4360 | Implicit Factoring: On Polynomial Time Factoring Given Only an Implicit Hint |  |  | read |
| KN-LIT-4361 | Implicit White-Box Implementations: White-Boxing ARX Ciphers |  |  | read |
| KN-LIT-4362 | Implicit Zero-Knowledge Arguments and Applications to the Malicious Setting |  |  | read |
| KN-LIT-4363 | Impossibility and Feasibility Results for Zero Knowledge with Public Keys? |  |  | read |
| KN-LIT-4364 | Impossibility of Black-Box Simulation Against Leakage Attacks |  |  | read |
| KN-LIT-4365 | Impossibility of Blind Signatures From One-Way Permutations |  |  | read |
| KN-LIT-4366 | Impossibility of Indifferentiable Iterated Blockciphers from 3 or Less Primitive Calls |  |  | read |
| KN-LIT-4367 | Impossibility of Order-Revealing Encryption in Idealized Models |  |  | read |
| KN-LIT-4368 | Impossibility of Quantum Virtual Black-Box Obfuscation of Classical Circuits |  |  | read |
| KN-LIT-4369 | Impossibility of Simulation Secure Functional Encryption Even with Random Oracles |  |  | read |
| KN-LIT-4370 | Impossibility of VBB Obfuscation with Ideal Constant-Degree Graded Encodings |  |  | read |
| KN-LIT-4371 | Impossibility on Tamper-Resilient Cryptography with Uniqueness Properties |  |  | read |
| KN-LIT-4372 | Impossibility Results for Lattice-Based Functional Encryption Schemes Akın Ünal? Work done while the author was working at |  |  | read |
| KN-LIT-4373 | Impossibility Results for Static Input Secure Computation |  |  | read |
| KN-LIT-4374 | Impossible Differential Cryptanalysis of |  |  | read |
| KN-LIT-4375 | Impossible Differential Cryptanalysis of CLEFIA Yukiyasu Tsunoo1 , Etsuko Tsujihara2 , Maki Shigeri3 , Teruo Saito3 |  |  | read |
| KN-LIT-4376 | Impossible Fault Analysis of RC4 and Differential Fault Analysis of RC4 |  |  | read |
| KN-LIT-4377 | Improved (Almost) Tightly-Secure Simulation-Sound QA-NIZK with Applications |  |  | read |
| KN-LIT-4378 | Improved (Almost) Tightly-Secure Structure-Preserving Signatures |  |  | read |
| KN-LIT-4379 | Improved (Hierarchical) Inner-Product Encryption from Lattices |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4380 | Improved Algorithms for Efficient Arithmetic on Elliptic Curves Using Fast Endomorphisms |  |  | read |
| KN-LIT-4381 | Improved All-Subkeys Recovery Attacks on |  |  | read |
| KN-LIT-4382 | Improved Analysis of Kannan’s Shortest Lattice |  |  | read |
| KN-LIT-4383 | Improved Attacks on Full GOST |  |  | read |
| KN-LIT-4384 | Improved Blind Side-Channel Analysis by Exploitation of Joint Distributions of Leakages |  |  | read |
| KN-LIT-4385 | Improved Bounds on Security Reductions for Discrete Log Based Signatures |  |  | read |
| KN-LIT-4386 | Improved Classical and Quantum Algorithms for Subset-Sum |  |  | read |
| KN-LIT-4387 | Improved Collision Search for SHA-0 |  |  | read |
| KN-LIT-4388 | Improved Computational Extractors and their Applications |  |  | read |
| KN-LIT-4389 | Improved Conditional Cube Attacks on Keccak Keyed Modes with MILP Method? |  |  | read |
| KN-LIT-4390 | Improved Construction of Nonlinear Resilient S-Boxes |  |  | read |
| KN-LIT-4391 | Improved Constructions of Anonymous |  |  | read |
| KN-LIT-4392 | Improved Cryptanalysis of HFERP |  |  | read |
| KN-LIT-4393 | Improved Cryptanalysis of MISTY1 |  |  | read |
| KN-LIT-4394 | Improved Cryptanalysis of Reduced RIPEMD-160 |  |  | read |
| KN-LIT-4395 | Improved Cryptanalysis of Skein Jean-Philippe Aumasson1, , Çağdaş Çalık2 , Willi Meier1, , Onur Özen3 |  |  | read |
| KN-LIT-4396 | Improved Cryptanalysis of the DECT Standard Cipher |  |  | read |
| KN-LIT-4397 | Improved cryptanalysis of UOV and Rainbow |  |  | read |
| KN-LIT-4398 | Improved Delegation of Computation using Fully Homomorphic Encryption? |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4399 | Improved Differential Attacks for ECHO and Grøstl |  |  | read |
| KN-LIT-4400 | Improved Differential-Linear Attacks with Applications to ARX Ciphers |  |  | read |
| KN-LIT-4401 | Improved Differential-Linear Cryptanalysis of 7-round Chaskey with Partitioning Gaëtan Leurent |  |  | read |
| KN-LIT-4402 | Improved Discrete Gaussian and |  |  | read |
| KN-LIT-4403 | Improved Division Property Based Cube Attacks |  |  | read |
| KN-LIT-4404 | Improved Dual System ABE in Prime-Order Groups via Predicate Encodings |  |  | read |
| KN-LIT-4405 | Improved Fully Adaptive Decentralized MA-ABE for NC1 from MDDH |  |  | read |
| KN-LIT-4406 | Improved generic algorithms for 3-collisions |  |  | read |
| KN-LIT-4407 | Improved Generic Attacks Against Hash-based MACs and HAIFA? |  |  | read |
| KN-LIT-4408 | Improved Generic Attacks on Unbalanced Feistel Schemes with Expanding Functions |  |  | read |
| KN-LIT-4409 | Improved Higher-Order Differential Attacks on MISTY1 |  |  | read |
| KN-LIT-4410 | Improved Higher-Order Side-Channel Attacks with FPGA Experiments Eric Peeters, François-Xavier Standaert |  |  | read |
| KN-LIT-4411 | Improved Identity-Based Signcryption |  |  | read |
| KN-LIT-4412 | Improved indifferentiability security analysis of chopMD Hash Function |  |  | read |
| KN-LIT-4413 | Improved Key Recovery Attacks on Reduced-Round AES in the Single-Key Setting |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4414 | Improved Linear Approximations to ARX |  |  | read |
| KN-LIT-4415 | Improved Linear Distinguishers for SNOW 2.0 |  |  | read |
| KN-LIT-4416 | Improved Linear Hull Attack on Round-Reduced Simon with Dynamic Key-guessing Techniques |  |  | read |
| KN-LIT-4417 | Improved Linear Sieving Techniques with Applications to Step-Reduced LED-64 |  |  | read |
| KN-LIT-4418 | Improved Masking for Tweakable Blockciphers with Applications to Authenticated Encryption |  |  | read |
| KN-LIT-4419 | Improved Multi-User Security Using the Squared-Ratio Method 1 |  |  | read |
| KN-LIT-4420 | Improved Non-Committing Encryption with Applications to Adaptively Secure Protocols |  |  | read |
| KN-LIT-4421 | Improved On-line/Off-line Signature Schemes |  |  | read |
| KN-LIT-4422 | Improved On-Line/Off-Line Threshold Signatures |  |  | read |
| KN-LIT-4423 | Improved OR-Composition of Sigma-Protocols |  |  | read |
| KN-LIT-4424 | Improved OT Extension for Transferring Short Secrets |  |  | read |
| KN-LIT-4425 | Improved Power Analysis Attacks on Falcon |  |  | read |
| KN-LIT-4426 | Improved Private Set Intersection against Malicious Adversaries |  |  | read |
| KN-LIT-4427 | Improved Private Set Intersection for Sets with Small Entries |  |  | read |
| KN-LIT-4428 | Improved Programmable Bootstrapping with |  |  | read |
| KN-LIT-4429 | Improved Progressive BKZ Algorithms and their Precise Cost Estimation by Sharp Simulator |  |  | read |
| KN-LIT-4430 | Improved Rebound Attack on the Finalist Grøstl |  |  | read |
| KN-LIT-4431 | Improved Security Analysis for Nonce-based Enhanced Hash-then-Mask MACs |  |  | read |
| KN-LIT-4432 | Improved Security Evaluation Techniques for Imperfect |  |  | read |
| KN-LIT-4433 | Improved Security for Linearly Homomorphic Signatures: A Generic Framework |  |  | read |
| KN-LIT-4434 | Improved Security for OCB3 |  |  | read |
| KN-LIT-4435 | Improved security proofs in lattice-based cryptography: using the Rényi divergence rather than the statistical distance |  |  | read |
| KN-LIT-4436 | Improved Setup Assumptions for 3-Round Resettable Zero Knowledge |  |  | read |
| KN-LIT-4437 | Improved Short Lattice Signatures in the Standard Model |  |  | read |
| KN-LIT-4438 | Improved Side-Channel Analysis of Finite-Field Multiplication Sonia Belaı̈d1 , Jean-Sébastien |  |  | read |
| KN-LIT-4439 | Improved Single-Key Attacks on 8-round AES-192 and AES-256 |  |  | read |
| KN-LIT-4440 | Improved Single-Key Attacks on 9-Round AES-192/256 |  |  | read |
| KN-LIT-4441 | Improved Single-Round Secure Multiplication Using Regenerating Codes |  |  | read |
| KN-LIT-4442 | Improved Slender-set Linear Cryptanalysis |  |  | read |
| KN-LIT-4443 | Improved Slide Attacks |  |  | read |
| KN-LIT-4444 | Improved Structure Preserving Signatures under Standard Bilinear Assumptions |  |  | read |
| KN-LIT-4445 | Improved Test Pattern Generation for Hardware Trojan Detection using |  |  | read |
| KN-LIT-4446 | Improved Upper Bounds of Differential and Linear Characteristic Probability for Camellia |  |  | read |
| KN-LIT-4447 | Improved Zero-knowledge Proofs of Knowledge for the ISIS Problem, and Applications |  |  | read |
| KN-LIT-4448 | Improvements of Algebraic Attacks for solving the Rank Decoding and MinRank problems |  |  | read |
| KN-LIT-4449 | Improving Attacks on Round-Reduced |  |  | read |
| KN-LIT-4450 | Improving Bounds on Elliptic Curve Hidden Number Problem for ECDH Key Exchange |  |  | read |
| KN-LIT-4452 | Improving Fast Algebraic Attacks |  |  | read |
| KN-LIT-4453 | Improving Key-Recovery in Linear Attacks: Application to 28-round PRESENT |  |  | read |
| KN-LIT-4454 | Improving Local Collisions: New Attacks on Reduced SHA-256 |  |  | read |
| KN-LIT-4455 | Improving Modular Inversion in RNS using the Plus-Minus Method |  |  | read |
| KN-LIT-4456 | Improving NFS for the discrete logarithm problem in non-prime finite fields |  |  | read |
| KN-LIT-4457 | Improving Revocation for Group Signature with Redactable Signature Olivier Sanders |  |  | read |
| KN-LIT-4458 | Improving Support-Minors rank attacks: |  |  | read |
| KN-LIT-4459 | Improving the Boneh-Franklin Traitor Tracing Scheme |  |  | read |
| KN-LIT-4460 | Improving the Generalized Feistel |  |  | read |
| KN-LIT-4461 | Improving the Polynomial time Precomputation of Frobenius Representation Discrete Logarithm Algorithms Simplified Setting for Small Characteristic Finite Fields |  |  | read |
| KN-LIT-4462 | Improving the Security of MACs via Randomized Message Preprocessing |  |  | read |
| KN-LIT-4463 | Improving the Security of Quantum Protocols via Commit-and-Open Ivan Damgård1 |  |  | read |
| KN-LIT-4464 | In How Many Ways Can You Write Rijndael? |  |  | read |
| KN-LIT-4465 | Incompressible Encodings |  |  | read |
| KN-LIT-4466 | Incremental Deterministic Public-Key Encryption |  |  | read |
| KN-LIT-4467 | Incremental Multiset Hash Functions and Their Application to Memory Integrity Checking Dwaine Clarke? , Srinivas Devadas, Marten van Dijk?? |  |  | read |
| KN-LIT-4468 | Incremental Program Obfuscation |  |  | read |
| KN-LIT-4469 | Incremental Proofs of Sequential Work |  |  | read |
| KN-LIT-4470 | Incrementally Aggregatable Vector Commitments and Applications to Verifiable Decentralized Storage? |  |  | read |
| KN-LIT-4471 | Incrementally Verifiable Computation or Proofs of Knowledge Imply Time/Space Efficiency |  |  | read |
| KN-LIT-4472 | IND-CCA secure Cryptography based on a variant of the LPN Problem |  |  | read |
| KN-LIT-4473 | IND-CCA-secure Key Encapsulation Mechanism in the Quantum Random Oracle Model, Revisited |  |  | read |
| KN-LIT-4474 | Index Calculus Attack for Hyperelliptic Curves of Small Genus |  |  | read |
| KN-LIT-4475 | Indifferentiability for Public Key Cryptosystems |  |  | read |
| KN-LIT-4476 | Indifferentiability of 8-Round Feistel Networks |  |  | read |
| KN-LIT-4477 | Indifferentiability of Confusion-Diffusion Networks |  |  | read |
| KN-LIT-4478 | Indifferentiability of Iterated Even-Mansour Ciphers with Non-Idealized Key-Schedules: |  |  | read |
| KN-LIT-4479 | Indifferentiability of Permutation-Based |  |  | read |
| KN-LIT-4480 | Indifferentiability of Truncated Random Permutations |  |  | read |
| KN-LIT-4481 | Indifferentiable Authenticated Encryption |  |  | read |
| KN-LIT-4482 | Indifferentiable Security Analysis of Popular Hash Functions with Prefix-free Padding |  |  | read |
| KN-LIT-4483 | Indistinguishability Obfus ation Without Multilinear Maps: New Paradigms via Low Degree Weak |  |  | read |
| KN-LIT-4484 | Indistinguishability Obfuscation and UCEs: The Case of Computationally Unpredictable Sources |  |  | read |
| KN-LIT-4485 | Indistinguishability Obfuscation for Turing Machines: Constant Overhead and Amortization |  |  | read |
| KN-LIT-4486 | Indistinguishability Obfuscation from |  |  | read |
| KN-LIT-4487 | Indistinguishability Obfuscation from Compact Functional Encryption |  |  | read |
| KN-LIT-4488 | Indistinguishability Obfuscation from Constant-Degree Graded Encoding Schemes |  |  | read |
| KN-LIT-4489 | Indistinguishability Obfuscation from LPN over Fp , DLIN, and |  |  | read |
| KN-LIT-4490 | Indistinguishability Obfuscation from Semantically-Secure Multilinear Encodings |  |  | read |
| KN-LIT-4491 | Indistinguishability Obfuscation from Simple-to-State Hard Problems: |  |  | read |
| KN-LIT-4492 | Indistinguishability Obfuscation from SXDH on 5-Linear Maps and Locality-5 PRGs |  |  | read |
| KN-LIT-4493 | Indistinguishability Obfuscation versus Multi-Bit Point Obfuscation with Auxiliary Input |  |  | read |
| KN-LIT-4494 | Indistinguishability Obfuscation Without Maps: Attacks and Fixes for Noisy Linear FE |  |  | read |
| KN-LIT-4495 | Indistinguishability Obfuscation Without Multilinear Maps: New methods for Bootstrapping and Instantiation |  |  | read |
| KN-LIT-4496 | Indistinguishability Obfuscation: from Approximate to Exact? |  |  | read |
| KN-LIT-4497 | Indistinguishable Proofs of Work or Knowledge |  |  | read |
| KN-LIT-4498 | Individual Cryptography |  |  | read |
| KN-LIT-4499 | Individual Simulations |  |  | read |
| KN-LIT-4500 | Inferring Sequences Produced by Nonlinear |  |  | read |
| KN-LIT-4501 | Information Theoretic and Security Analysis of a 65-nanometer DDSLL AES S-box Mathieu Renauld? , Dina Kamel |  |  | read |
| KN-LIT-4502 | Information Theoretic Evaluation of Side-Channel Resistant Logic Styles |  |  | read |
| KN-LIT-4503 | Information-Combining Differential Fault Attacks on DEFAULT |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4504 | Information-Theoretic 2-Round MPC without Round Collapsing: Adaptive Security, and More |  |  | read |
| KN-LIT-4505 | Information-Theoretic Broadcast with Dishonest Majority for Long Messages |  |  | read |
| KN-LIT-4506 | Information-Theoretic Conditions for Two-Party Secure Function Evaluation Claude Crépeau1 ? , George Savvides1 ? |  |  | read |
| KN-LIT-4507 | Information-theoretic Indistinguishability via the Chi-squared Method |  |  | read |
| KN-LIT-4508 | Information-theoretic Local Non-malleable |  |  | read |
| KN-LIT-4509 | Information-Theoretic Secret-Key Agreement: The Asymptotically Tight Relation Between the Secret-Key Rate and the Channel Quality Ratio |  |  | read |
| KN-LIT-4510 | Information-Theoretic Security Without an Honest Majority |  |  | read |
| KN-LIT-4511 | Information-Theoretically Secure MPC against Mixed Dynamic Adversaries |  |  | read |
| KN-LIT-4512 | Injective Trapdoor Functions via Derandomization: How Strong is Rudich’s Black-Box Barrier? |  |  | read |
| KN-LIT-4513 | Inner Product Masking Revisited |  |  | read |
| KN-LIT-4514 | Inner-Product Functional |  |  | read |
| KN-LIT-4515 | Inoculating Multivariate Schemes Against Differential Attacks |  |  | read |
| KN-LIT-4516 | Instance-Dependent Verifiable Random |  |  | read |
| KN-LIT-4517 | Instant Ciphertext-Only Cryptanalysis of GSM |  |  | read |
| KN-LIT-4518 | Instantaneous Decentralized Poker |  |  | read |
| KN-LIT-4519 | Instantiability of Classical Random-Oracle-Model Encryption Transforms |  |  | read |
| KN-LIT-4520 | Instantiability of RSA-OAEP under Chosen-Plaintext Attack |  |  | read |
| KN-LIT-4521 | Instantiating Random Oracles via UCEs |  |  | read |
| KN-LIT-4522 | Instantiating the Whitened |  |  | read |
| KN-LIT-4523 | Instruction Set Extensions for Ef£cient AES Implementation on 32-bit Processors |  |  | read |
| KN-LIT-4524 | Instruction Set Extensions for Fast Arithmetic |  |  | read |
| KN-LIT-4525 | Insuperability of the Standard Versus Ideal Model Gap for Tweakable Blockcipher Security |  |  | read |
| KN-LIT-4526 | Integral and Multidimensional Linear Distinguishers with Correlation Zero |  |  | read |
| KN-LIT-4527 | Integral Cryptanalysis on Full MISTY1 |  |  | read |
| KN-LIT-4528 | Integral Matrix Gram Root and Lattice Gaussian Sampling without Floats |  |  | read |
| KN-LIT-4529 | Integrals Go Statistical: Cryptanalysis of Full Skipjack Variants |  |  | read |
| KN-LIT-4530 | Intel’s New AES Instructions for Enhanced |  |  | read |
| KN-LIT-4531 | Interactive and Noninteractive Zero Knowledge are Equivalent in the Help Model? |  |  | read |
| KN-LIT-4532 | Interactive Coding for Interactive Proofs |  |  | read |
| KN-LIT-4533 | Interactive Non-Malleable Codes Nils Fleischhacker1? , Vipul Goyal2?? , Abhishek Jain3? ? ? |  |  | read |
| KN-LIT-4534 | Interactive Oracle Proofs? |  |  | read |
| KN-LIT-4535 | Interactive Zero-Knowledge with Restricted Random Oracles |  |  | read |
| KN-LIT-4536 | Interactively Secure Groups from Obfuscation |  |  | read |
| KN-LIT-4537 | Internal Differential Boomerangs: Practical Analysis of the Round-Reduced Keccak-f Permutation |  |  | read |
| KN-LIT-4538 | Introduction |  |  | read |
| KN-LIT-4539 | Introduction Theorem (Hasse) For an elliptic curve E over a finite field |  |  | read |
| KN-LIT-4540 | Intrusion-Resilience via the Bounded-Storage Model |  |  | read |
| KN-LIT-4541 | Inverted Edwards coordinates |  |  | read |
| KN-LIT-4542 | Invertible Quadratic |  |  | read |
| KN-LIT-4543 | Inverting HFE is Quasipolynomial |  |  | read |
| KN-LIT-4544 | Inverting HFE Systems is Quasi-polynomial for All Fields |  |  | read |
| KN-LIT-4545 | Inverting the nal exponentiation of Tate pairings on ordinary elliptic curves using faults |  |  | read |
| KN-LIT-4546 | Investigating Fundamental Security Requirements on Whirlpool: |  |  | read |
| KN-LIT-4547 | Investigating SRAM PUFs |  |  | read |
| KN-LIT-4549 | Is Information-Theoretic Topology-Hiding Computation Possible? |  |  | read |
| KN-LIT-4550 | Is the security of quantum cryptography guaranteed by the laws of physics? |  |  | read |
| KN-LIT-4551 | Is there an Oblivious RAM Lower Bound for Online Reads? |  |  | read |
| KN-LIT-4552 | Isogenies and the Discrete Logarithm Problem in Jacobians of Genus 3 Hyperelliptic Curves |  |  | read |
| KN-LIT-4553 | Isogenies in genus 2 for cryptographic applications Benjamin Smith with Wouter Castryck, Craig Costello, Thomas Decru, Enric Florit |  |  | read |
| KN-LIT-4554 | Isogeny graphs, computational problems, and applications to cryptography |  |  | read |
| KN-LIT-4555 | Isogeny interpolation for elliptic curves, and applications Wouter Castryck, Thomas Decru, Luciano Maino, Chloe Martindale |  |  | read |
| KN-LIT-4556 | Isogeny-based key compression without pairings |  |  | read |
| KN-LIT-4557 | It wasn’t me! Repudiability and Claimability of Ring Signatures |  |  | read |
| KN-LIT-4559 | J. Ramanujan Math. Soc. 20, No.1 (2005) 1–32 Optimized Baby Step-Giant Step Methods |  |  | read |
| KN-LIT-4560 | Jack L.H.Crawford Queen Mary Univ. of London |  |  | read |
| KN-LIT-4561 | Jacobian Coordinates on Genus 2 Curves |  |  | read |
| KN-LIT-4562 | Jammin’ on the deck |  |  | read |
| KN-LIT-4563 | JIMU: Faster LEGO-based Secure Computation using Additive Homomorphic Hashes |  |  | read |
| KN-LIT-4564 | Just How Fair is an Unreactive World? |  |  | read |
| KN-LIT-4565 | Just how hard are rotations of Zn ? |  |  | read |
| KN-LIT-4566 | k-Round Multiparty Computation from k-Round Oblivious Transfer via Garbled Interactive Circuits |  |  | read |
| KN-LIT-4567 | k-Times Anonymous Authentication |  |  | read |
| KN-LIT-4568 | k-times Anonymous Authentication with a Constant Proving Cost |  |  | read |
| KN-LIT-4569 | KATAN & KTANTAN — A Family of Small and Efficient Hardware-Oriented Block Ciphers |  |  | read |
| KN-LIT-4570 | KDM Security for the Fujisaki-Okamoto Transformations in the QROM |  |  | read |
| KN-LIT-4571 | KDM-CCA Security from RKA Secure Authenticated Encryption ? |  |  | read |
| KN-LIT-4572 | KDM-Security via Homomorphic Smooth Projective Hashing |  |  | read |
| KN-LIT-4574 | KEM Combiners? |  |  | read |
| KN-LIT-4575 | Key Dependent Message Security and Receiver Selective Opening Security for Identity-Based Encryption |  |  | read |
| KN-LIT-4576 | Key Derivation Without Entropy Waste |  |  | read |
| KN-LIT-4577 | Key Difference Invariant Bias in Block Ciphers Andrey Bogdanov1? , Christina Boura1? , Vincent Rijmen2? , Meiqin Wang3? |  |  | read |
| KN-LIT-4578 | Key Encapsulation Mechanism with Explicit Rejection in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-4579 | Key Encapsulation Mechanism with Tight Enhanced Security in the Multi-User Setting: |  |  | read |
| KN-LIT-4580 | Key Encapsulation Mechanisms from |  |  | read |
| KN-LIT-4581 | Key Exchange Using Passwords and Long Keys? |  |  | read |
| KN-LIT-4582 | Key Guessing Strategies for |  |  | read |
| KN-LIT-4583 | Key Recovery Attack against 2.5-round π-Cipher |  |  | read |
| KN-LIT-4584 | Key Recovery Attacks of Practical Complexity on AES-256 Variants With Up To 10 Rounds |  |  | read |
| KN-LIT-4585 | Key Recovery Attacks on 3-round |  |  | read |
| KN-LIT-4586 | Key Recovery from Gram–Schmidt Norm |  |  | read |
| KN-LIT-4587 | Key Recovery on Hidden Monomial Multivariate Schemes |  |  | read |
| KN-LIT-4588 | Key Rotation for Authenticated Encryption |  |  | read |
| KN-LIT-4589 | Key-alternating Ciphers and Key-length Extension: |  |  | read |
| KN-LIT-4590 | Key-Alternating Ciphers in a Provable Setting: Encryption Using a Small Number of Public Permutations? |  |  | read |
| KN-LIT-4591 | Key-Dependent Message Security: |  |  | read |
| KN-LIT-4592 | Key-Evolution Schemes Resilient to Space-Bounded Leakage? |  |  | read |
| KN-LIT-4593 | Key-Homomorphic |  |  | read |
| KN-LIT-4594 | Key-Homomorphic Pseudorandom Functions from LWE with Small Modulus |  |  | read |
| KN-LIT-4595 | Key-Insulated Public Key Cryptosystems |  |  | read |
| KN-LIT-4596 | Key-Privacy in Public-Key Encryption |  |  | read |
| KN-LIT-4597 | Key-Recovery Attack on the ASASA Cryptosystem With Expanding S-Boxes |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4598 | Key-Recovery Attacks on ASASA |  |  | read |
| KN-LIT-4599 | Key-Recovery Attacks on Universal Hash Function based MAC Algorithms? |  |  | read |
| KN-LIT-4600 | Key-Reduced Variants of 3kf9 with Beyond-Birthday-Bound Security |  |  | read |
| KN-LIT-4601 | Key-schedule Security for the TLS 1.3 |  |  | read |
| KN-LIT-4602 | Key-Versatile Signatures and Applications: |  |  | read |
| KN-LIT-4603 | Keyword Search and Oblivious Pseudorandom Functions |  |  | read |
| KN-LIT-4604 | KFC - The Krazy Feistel Cipher |  |  | read |
| KN-LIT-4605 | KHAPE: Asymmetric PAKE from Key-Hiding Key Exchange |  |  | read |
| KN-LIT-4606 | Knowledge Encryption and Its Applications to Simulatable Protocols With Low Round-Complexity |  |  | read |
| KN-LIT-4607 | Knowledge-Binding Commitments with Applications in Time-Stamping |  |  | read |
| KN-LIT-4608 | Known-IV Attacks on |  |  | read |
| KN-LIT-4609 | Known-key Distinguisher on Full PRESENT |  |  | read |
| KN-LIT-4610 | Known-Key Distinguishers for Some Block Ciphers? |  |  | read |
| KN-LIT-4611 | Known-Key Distinguishers on 11-Round Feistel and Collision Attacks on Its Hashing Modes |  |  | read |
| KN-LIT-4612 | Known–Plaintext–Only Attack on RSA–CRT with Montgomery Multiplication |  |  | read |
| KN-LIT-4613 | Kummer for Genus One over Prime Order Fields |  |  | read |
| KN-LIT-4614 | Kummer strikes back: new DH speed records |  |  | read |
| KN-LIT-4615 | Kurosawa-Desmedt Meets Tight Security |  |  | read |
| KN-LIT-4616 | KVaC: Key-Value Commitments for Blockchains and Beyond |  |  | read |
| KN-LIT-4617 | KyberSlash: Exploiting secret-dependent division timings in Kyber implementations |  |  | read |
| KN-LIT-4618 | LaBRADOR: Compact Proofs for R1CS from Module-SIS |  |  | read |
| KN-LIT-4619 | Laconic Branching Programs from the Diffie-Hellman Assumption |  |  | read |
| KN-LIT-4620 | Laconic Function Evaluation for Turing Machines |  |  | read |
| KN-LIT-4621 | Laconic Oblivious Transfer and its Applications Chongwon Cho1 , Nico Döttling2?,?? , Sanjam Garg2?? , Divya Gupta3??,? ? ? |  |  | read |
| KN-LIT-4622 | Laconic Private Set Intersection and Applications |  |  | read |
| KN-LIT-4623 | Lambda coordinates for binary elliptic curves |  |  | read |
| KN-LIT-4624 | Language Modeling and Encryption on Packet Switched Networks? |  |  | read |
| KN-LIT-4625 | Languages with Efficient Zero-Knowledge PCPs are in SZK |  |  | read |
| KN-LIT-4626 | Lapin: An Efficient |  |  | read |
| KN-LIT-4627 | Large Message Homomorphic Secret Sharing from DCR and Applications |  |  | read |
| KN-LIT-4628 | Large Modulus Ring-LWE ≥ Module-LWE |  |  | read |
| KN-LIT-4629 | Large Superfluous Keys in Multivariate Quadratic Asymmetric Systems |  |  | read |
| KN-LIT-4630 | Large-Precision Homomorphic Sign Evaluation using FHEW/TFHE Bootstrapping |  |  | read |
| KN-LIT-4631 | Lars Knudsen1 ? and David Wagner2 |  |  | read |
| KN-LIT-4632 | Latin Dances Reloaded: Improved Cryptanalysis against Salsa and ChaCha, and the proposal of Forró |  |  | read |
| KN-LIT-4633 | Lattice Basis Delegation in Fixed Dimension and Shorter-Ciphertext Hierarchical IBE |  |  | read |
| KN-LIT-4634 | Lattice Enumeration for Tower NFS: a 521-bit Discrete Logarithm Computation |  |  | read |
| KN-LIT-4635 | Lattice Mixing and Vanishing Trapdoors A Framework for Fully Secure Short Signatures and more Xavier Boyen |  |  | read |
| KN-LIT-4636 | Lattice Reduction Algorithms: Theory and Practice Phong Q. Nguyen |  |  | read |
| KN-LIT-4637 | Lattice Reduction for Modules, or How to Reduce ModuleSVP to ModuleSVP |  |  | read |
| KN-LIT-4638 | Lattice Reduction with Approximate Enumeration Oracles |  |  | read |
| KN-LIT-4639 | Lattice sieving via quantum random walks |  |  | read |
| KN-LIT-4640 | Lattice Signature with Efficient Protocols, Application to Anonymous Credentials |  |  | read |
| KN-LIT-4641 | Lattice Signatures and Bimodal Gaussians |  |  | read |
| KN-LIT-4642 | Lattice Signatures Without Trapdoors |  |  | read |
| KN-LIT-4643 | Lattice Trapdoors and IBE from Middle-Product LWE |  |  | read |
| KN-LIT-4644 | Lattice-based Authenticated Key Exchange with Tight Security? |  |  | read |
| KN-LIT-4645 | Lattice-Based Blind Signatures, Revisited |  |  | read |
| KN-LIT-4646 | Lattice-based Cryptography |  |  | read |
| KN-LIT-4647 | Lattice-Based E-Cash, Revisited |  |  | read |
| KN-LIT-4648 | Lattice-Based Fully Dynamic Multi-Key FHE with Short Ciphertexts |  |  | read |
| KN-LIT-4649 | Lattice-Based Functional Commitments: |  |  | read |
| KN-LIT-4650 | Lattice-Based Group Encryption with Full |  |  | read |
| KN-LIT-4651 | Lattice-based Group Signature Scheme with Verifier-local Revocation |  |  | read |
| KN-LIT-4652 | Lattice-Based Group Signatures with Logarithmic Signature Size |  |  | read |
| KN-LIT-4653 | Lattice-Based Identification Schemes Secure Under Active Attacks ? |  |  | read |
| KN-LIT-4654 | Lattice-based Revocable (Hierarchical) IBE with Decryption Key Exposure Resistance |  |  | read |
| KN-LIT-4655 | Lattice-based Signatures with Tight Adaptive Corruptions and More |  |  | read |
| KN-LIT-4656 | Lattice-Based SNARGs and Their Application to More Efficient Obfuscation |  |  | read |
| KN-LIT-4657 | Lattice-Based SNARKs: Publicly Verifiable |  |  | read |
| KN-LIT-4658 | Lattice-Based Succinct Arguments for NP with Polylogarithmic-Time Verification |  |  | read |
| KN-LIT-4659 | Lattice-based Succinct Arguments from Vanishing Polynomials |  |  | read |
| KN-LIT-4660 | Lattice-Based Threshold-Changeability for Standard Shamir Secret-Sharing Schemes |  |  | read |
| KN-LIT-4661 | Lattice-Based Timed Cryptography |  |  | read |
| KN-LIT-4662 | Lattice-Based Zero-Knowledge Arguments for Integer Relations |  |  | read |
| KN-LIT-4663 | Lattice-Based Zero-Knowledge Proofs and Applications: |  |  | read |
| KN-LIT-4664 | Lattice-Based Zero-Knowledge Proofs: New Techniques for Shorter and Faster Constructions and Applications |  |  | read |
| KN-LIT-4665 | Lattices and Factoring (Invited Talk) Léo |  |  | read |
| KN-LIT-4666 | Layout Graphs, Random Walks and the t-wise Independence of SPN Block Ciphers |  |  | read |
| KN-LIT-4667 | Lazy Modulus Switching for the BKW Algorithm on LWE |  |  | read |
| KN-LIT-4668 | Le Mans: Dynamic and Fluid MPC for Dishonest Majority |  |  | read |
| KN-LIT-4669 | Leak Resistant Arithmetic |  |  | read |
| KN-LIT-4670 | Leakage Assessment Methodology – a clear roadmap for side-channel evaluations |  |  | read |
| KN-LIT-4671 | Leakage Certification Revisited: Bounding Model Errors in Side-Channel |  |  | read |
| KN-LIT-4672 | Leakage Resilience of the Duplex Construction |  |  | read |
| KN-LIT-4673 | Leakage Resilient ElGamal Encryption |  |  | read |
| KN-LIT-4674 | Leakage Resilient Fully Homomorphic Encryption |  |  | read |
| KN-LIT-4675 | Leakage Resilient One-Way Functions: The Auxiliary-Input Setting |  |  | read |
| KN-LIT-4676 | Leakage Resilient Secret Sharing and Applications? |  |  | read |
| KN-LIT-4677 | Leakage Resilient Value Comparison With Application to Message Authentication |  |  | read |
| KN-LIT-4678 | Leakage-Flexible CCA-secure Public-Key Encryption: Simple Construction and Free of Pairing |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4679 | Leakage-resilience of the Shamir Secret-sharing Scheme against Physical-bit Leakages |  |  | read |
| KN-LIT-4680 | Leakage-Resilient Authenticated Key Establishment Protocols |  |  | read |
| KN-LIT-4681 | Leakage-Resilient Chosen-Ciphertext Secure Public-Key Encryption from Hash Proof System and One-Time Lossy Filter |  |  | read |
| KN-LIT-4682 | Leakage-Resilient Circuits Revisited – Optimal Number of Computing Components without Leak-free Hardware |  |  | read |
| KN-LIT-4683 | Leakage-Resilient Circuits without Computational Assumptions |  |  | read |
| KN-LIT-4684 | Leakage-Resilient Cryptography from |  |  | read |
| KN-LIT-4685 | Leakage-Resilient Cryptography from Minimal Assumptions |  |  | read |
| KN-LIT-4686 | Leakage-Resilient Cryptography From the Inner-Product Extractor |  |  | read |
| KN-LIT-4687 | Leakage-Resilient IBE/ABE with Optimal Leakage Rates from Lattices |  |  | read |
| KN-LIT-4688 | Leakage-resilient Identity-based Encryption in Bounded Retrieval Model with Nearly Optimal Leakage-Ratio |  |  | read |
| KN-LIT-4689 | Leakage-Resilient Key Exchange and Two-Seed Extractors |  |  | read |
| KN-LIT-4690 | Leakage-resilient Linear Secret-sharing against arbitrary Bounded-size Leakage Family? |  |  | read |
| KN-LIT-4691 | Leakage-Resilient Non-Malleable Codes ? |  |  | read |
| KN-LIT-4692 | Leakage-Resilient Pseudorandom Functions and Side-Channel Attacks on Feistel Networks |  |  | read |
| KN-LIT-4693 | Leakage-Resilient Public-Key Cryptography in the Bounded-Retrieval Model |  |  | read |
| KN-LIT-4694 | Leakage-Resilient Public-Key Encryption from Obfuscation |  |  | read |
| KN-LIT-4695 | Leakage-Resilient Signatures |  |  | read |
| KN-LIT-4696 | Leakage-Resilient Signatures with Graceful Degradation |  |  | read |
| KN-LIT-4697 | Leakage-Resilient Symmetric Cryptography Under Empirically Verifiable Assumptions |  |  | read |
| KN-LIT-4698 | Leakage-Resilient Symmetric Encryption via Re-keying |  |  | read |
| KN-LIT-4699 | Leakage-Resilient Zero Knowledge |  |  | read |
| KN-LIT-4700 | Leakage-Tolerant Computation with Input-Independent Preprocessing |  |  | read |
| KN-LIT-4701 | Leakage-Tolerant Interactive Protocols? |  |  | read |
| KN-LIT-4702 | Leaked-State-Forgery Attack Against The Authenticated Encryption Algorithm ALE |  |  | read |
| KN-LIT-4703 | Learning a Parallelepiped: Cryptanalysis of GGH and NTRU Signatures |  |  | read |
| KN-LIT-4704 | Learning a Zonotope and More: Cryptanalysis of NTRUSign Countermeasures |  |  | read |
| KN-LIT-4705 | Learning Strikes Again: the Case of the DRS Signature Scheme |  |  | read |
| KN-LIT-4706 | Learning With Errors and Extrapolated Dihedral Cosets |  |  | read |
| KN-LIT-4707 | Learning With Physical Rounding for Linear and Quadratic Leakage Functions Clément |  |  | read |
| KN-LIT-4708 | Learning with Rounding, Revisited |  |  | read |
| KN-LIT-4709 | Ledger Combiners for Fast Settlement |  |  | read |
| KN-LIT-4710 | Leftover Hash Lemma, Revisited |  |  | read |
| KN-LIT-4711 | LEGO for Two-Party Secure Computation |  |  | read |
| KN-LIT-4712 | Length Based Attack and Braid Groups: Cryptanalysis of Anshel-Anshel-Goldfeld Key Exchange Protocol |  |  | read |
| KN-LIT-4713 | Less is More Dimensionality |  |  | read |
| KN-LIT-4714 | Let a Non-Barking Watchdog Bite: Cliptographic Signatures with an Offline Watchdog Sherman S. M. Chow1 , Alexander Russell2 , Qiang Tang3 |  |  | read |
| KN-LIT-4715 | Let Attackers Program Ideal Models: Modularity and Composability for Adaptive Compromise |  |  | read |
| KN-LIT-4716 | Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation Tiacheng Xie? , Jiaheng Zhang , Yupeng Zhang?? |  |  | read |
| KN-LIT-4717 | Lifting and Elliptic Curve Discrete Logarithms |  |  | read |
| KN-LIT-4718 | Lifting Standard Model Reductions to Common Setup Assumptions |  |  | read |
| KN-LIT-4719 | Light-Weight Instruction Set Extensions for Bit-Sliced Cryptography |  |  | read |
| KN-LIT-4720 | Lightweight Authenticated Encryption Mode Suitable for Threshold Implementation |  |  | read |
| KN-LIT-4721 | Lightweight Coprocessor for Koblitz Curves: 283-bit ECC Including Scalar Conversion with only 4300 Gates |  |  | read |
| KN-LIT-4722 | Lightweight Cryptography for the Cloud: Exploit the Power of Bitslice Implementation |  |  | read |
| KN-LIT-4723 | Lightweight MDS Generalized Circulant Matrices |  |  | read |
| KN-LIT-4724 | Lightweight MDS Involution Matrices |  |  | read |
| KN-LIT-4725 | Lightweight Multiplication in GF (2n ) with Applications to MDS Matrices |  |  | read |
| KN-LIT-4726 | Lightweight Privacy Preserving Authentication for RFID Using a Stream Cipher |  |  | read |
| KN-LIT-4727 | Lightweight, Maliciously Secure Verifiable Function Secret Sharing |  |  | read |
| KN-LIT-4728 | Limitations of the Meta-Reduction Technique: The Case of Schnorr Signatures |  | Journal of Cryptology | read |
| KN-LIT-4729 | Limitations on Transformations from Composite-Order to Prime-Order Groups: The Case of Round-Optimal Blind Signatures |  |  | read |
| KN-LIT-4730 | Limited-birthday Distinguishers for Hash Functions |  |  | read |
| KN-LIT-4731 | Limits in the Provable Security of ECDSA Signatures |  |  | read |
| KN-LIT-4732 | Limits of Breach-Resistant and Snapshot-Oblivious RAMs? |  |  | read |
| KN-LIT-4733 | Limits of Constructive Security Proofs |  |  | read |
| KN-LIT-4734 | Limits of Extractability Assumptions with Distributional Auxiliary Input |  |  | read |
| KN-LIT-4735 | Limits of Polynomial Packings for Zpk and Fpk |  |  | read |
| KN-LIT-4736 | Limits of Practical Sublinear Secure Computation |  |  | read |
| KN-LIT-4737 | Limits of provable security for homomorphic encryption |  |  | read |
| KN-LIT-4738 | Limits on Low-Degree Pseudorandom Generators (Or: Sum-of-Squares Meets Program Obfuscation) |  |  | read |
| KN-LIT-4739 | Limits on the Adaptive Security of Yao’s Garbling |  |  | read |
| KN-LIT-4740 | Limits on the Efficiency of (Ring) LWE based Non-Interactive Key Exchange Siyao Guo1? , Pritish Kamath2?? |  |  | read |
| KN-LIT-4741 | Limits on the Power of Cryptographic Cheap Talk? |  |  | read |
| KN-LIT-4742 | Limits on the Power of Garbling Techniques for Public-Key Encryption |  |  | read |
| KN-LIT-4743 | Limits on the Power of Zero-Knowledge Proofs in Cryptographic Constructions |  |  | read |
| KN-LIT-4744 | Limits on the Usefulness of Random Oracles |  |  | read |
| KN-LIT-4745 | Linear Algebra with Sub-linear Zero-Knowledge Arguments |  |  | read |
| KN-LIT-4746 | Linear Approximations of Addition Modulo 2n -1 ? |  |  | read |
| KN-LIT-4747 | Linear Cryptanalysis of Bluetooth Stream Cipher |  |  | read |
| KN-LIT-4748 | Linear Cryptanalysis of DES with Asymmetries |  |  | read |
| KN-LIT-4749 | Linear Cryptanalysis of FF3-1 and FEA |  |  | read |
| KN-LIT-4750 | Linear Equivalence of Block Ciphers with Partial Non-Linear Layers: Application to LowMC |  |  | read |
| KN-LIT-4751 | Linear Integer Secret Sharing and Distributed Exponentiation |  |  | read |
| KN-LIT-4752 | Linear Recurring Sequences for the UOV Key Generation |  |  | read |
| KN-LIT-4753 | Linear Secret Sharing Schemes from Error |  |  | read |
| KN-LIT-4754 | Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak |  |  | read |
| KN-LIT-4755 | Linear VSS and Distributed Commitments Based on Secret Sharing and Pairwise Checks |  |  | read |
| KN-LIT-4756 | Linear-map Vector Commitments and their |  |  | read |
| KN-LIT-4757 | Linear-Size Constant-Query IOPs for Delegating Computation |  |  | read |
| KN-LIT-4758 | Linear-Time Arguments with Sublinear Verification from Tensor Codes |  |  | read |
| KN-LIT-4759 | Linear-Time Zero-Knowledge Proofs for Arithmetic Circuit Satisfiability |  |  | read |
| KN-LIT-4760 | Linearly Homomorphic Signatures over Binary Fields and New Tools for Lattice-Based Signatures |  |  | read |
| KN-LIT-4761 | Linearly Homomorphic Structure-Preserving |  |  | read |
| KN-LIT-4762 | Linearly-Homomorphic Signatures and Scalable Mix-Nets |  |  | read |
| KN-LIT-4763 | Linicrypt: A Model for Practical Cryptography? |  |  | read |
| KN-LIT-4764 | Links among Impossible Differential, Integral and Zero Correlation Linear Cryptanalysis |  |  | read |
| KN-LIT-4765 | Links Between Truncated Differential and Multidimensional Linear Properties of Block |  |  | read |
| KN-LIT-4766 | List Oblivious Transfer and Applications to Round-Optimal Black-Box |  |  | read |
| KN-LIT-4767 | Local Non-Malleable Codes in the Bounded Retrieval Model |  |  | read |
| KN-LIT-4768 | Locality-Preserving Oblivious RAM Gilad Asharov1? |  |  | read |
| KN-LIT-4769 | Locally Computable UOWHF with Linear Shrinkage |  |  | read |
| KN-LIT-4770 | Locally Decodable and Updatable |  |  | read |
| KN-LIT-4771 | Locally Verifiable Distributed SNARGs |  |  | read |
| KN-LIT-4772 | Locally Verifiable Signature and Key Aggregation |  |  | read |
| KN-LIT-4773 | Location, location, location: Revisiting modeling and exploitation for location-based side channel leakages |  |  | read |
| KN-LIT-4774 | Lockable Obfuscation from Circularly Insecure |  |  | read |
| KN-LIT-4775 | Log-S-unit Lattices Using Explicit Stickelberger |  |  | read |
| KN-LIT-4776 | Logarithmic-Size (Linkable) |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4777 | Long Modular Multiplication for Cryptographic Applications1 |  |  | read |
| KN-LIT-4778 | Long-term Security and Universal Composability |  |  | read |
| KN-LIT-4779 | Looking beyond XTR |  |  | read |
| KN-LIT-4780 | Lookup Arguments: Improvements, Extensions and Applications to Zero-Knowledge Decision Trees |  |  | read |
| KN-LIT-4781 | Lossiness and Entropic Hardness for Ring-LWE |  |  | read |
| KN-LIT-4782 | Lossy Algebraic Filters With Short Tags |  |  | read |
| KN-LIT-4783 | Lossy Codes and a New Variant of the Learning-With-Errors Problem |  |  | read |
| KN-LIT-4784 | Lossy CSI-FiSh: Efficient Signature Scheme with Tight Reduction to Decisional CSIDH-512 |  |  | read |
| KN-LIT-4785 | Lossy Encryption: Constructions from General |  |  | read |
| KN-LIT-4786 | Lossy Functions Do Not Amplify Well |  |  | read |
| KN-LIT-4787 | Low Communication Complexity Protocols |  |  | read |
| KN-LIT-4788 | Low Cost Constant Round MPC |  |  | read |
| KN-LIT-4789 | Low Error Efficient Computational Extractors in the CRS Model |  |  | read |
| KN-LIT-4790 | Low Memory Attacks against Two-Round Even-Mansour using the 3-XOR Problem |  |  | read |
| KN-LIT-4791 | Low Noise LPN: KDM Secure Public Key |  |  | read |
| KN-LIT-4792 | Low Overhead Broadcast Encryption from Multilinear Maps |  |  | read |
| KN-LIT-4793 | Low Probability Differentials and the Cryptanalysis of Full-Round CLEFIA-128 |  |  | read |
| KN-LIT-4794 | Low Weight Discrete Logarithm and Subset Sum in 20.65n with Polynomial Memory |  |  | read |
| KN-LIT-4795 | Low-Communication Multiparty Triple Generation for SPDZ from Ring-LPN? |  |  | read |
| KN-LIT-4796 | Low-communication parallel quantum multi-target preimage search |  |  | read |
| KN-LIT-4797 | Low-Complexity Weak Pseudorandom Functions in AC0[MOD2] 1 |  |  | read |
| KN-LIT-4798 | Low-Latency Encryption – Is “Lightweight = Light + Wait”?? |  |  | read |
| KN-LIT-4799 | Low-Overhead Implementation of a Soft Decision Helper Data Algorithm for SRAM PUFs |  |  | read |
| KN-LIT-4800 | Low-Power Elliptic Curve Cryptography Using Scaled Modular Arithmetic |  |  | read |
| KN-LIT-4801 | Lower and Upper Bounds for Deniable |  |  | read |
| KN-LIT-4802 | Lower Bound Framework for Differentially |  |  | read |
| KN-LIT-4803 | Lower Bound on SNARGs in the Random Oracle Model |  |  | read |
| KN-LIT-4804 | Lower Bounds for (Batch) PIR with Private Preprocessing |  |  | read |
| KN-LIT-4805 | Lower Bounds for Differentially Private RAMs |  |  | read |
| KN-LIT-4806 | Lower Bounds for Encrypted Multi-Maps and Searchable Encrypti in the Leakage Cell Probe Model |  |  | read |
| KN-LIT-4807 | Lower Bounds for Leakage-Resilient Secret Sharing |  |  | read |
| KN-LIT-4808 | Lower Bounds for Multi-Server Oblivious RAMs |  |  | read |
| KN-LIT-4809 | Lower Bounds for Non-Interactive Zero-Knowledge |  |  | read |
| KN-LIT-4810 | Lower Bounds for the Number of Decryption Updates in Registration-Based Encryption |  |  | read |
| KN-LIT-4811 | Lower Bounds in the Hardware Token Model |  |  | read |
| KN-LIT-4812 | Lower Bounds on Anonymous Whistleblowing |  |  | read |
| KN-LIT-4813 | Lower Bounds on Assumptions behind |  |  | read |
| KN-LIT-4814 | Lower Bounds on Assumptions Behind Registration-Based Encryption |  |  | read |
| KN-LIT-4815 | Lower Bounds on Implementing Robust and Resilient Mediators |  |  | read |
| KN-LIT-4816 | Lower Bounds on Lattice Enumeration with Extreme Pruning |  |  | read |
| KN-LIT-4817 | Lower bounds on lattice sieving and information set decoding |  |  | read |
| KN-LIT-4818 | Lower Bounds on Obfuscation from All-or-Nothing Encryption Primitives |  |  | read |
| KN-LIT-4819 | Lower Bounds on the Degree of Block Ciphers |  |  | read |
| KN-LIT-4820 | LP Solutions of Vectorial Integer Subset Sums – Cryptanalysis of Galbraith’s Binary Matrix LWE |  |  | read |
| KN-LIT-4821 | LPN Decoded |  |  | read |
| KN-LIT-4822 | LS-Designs: Bitslice Encryption for Efficient Masked Software Implementations |  |  | read |
| KN-LIT-4823 | Luby-Rackoff Backwards with More Users and More Security |  |  | read |
| KN-LIT-4824 | Luby-Rackoff Ciphers from Weak Round Functions? |  |  | read |
| KN-LIT-4825 | Lucky Microseconds: A Timing Attack on Amazon’s s2n Implementation of TLS |  |  | read |
| KN-LIT-4826 | Lunar: a Toolbox for More Efficient |  |  | read |
| KN-LIT-4827 | LWE with Side Information: |  |  | read |
| KN-LIT-4828 | LWE Without Modular Reduction and |  |  | read |
| KN-LIT-4829 | M-SIDH and MD-SIDH: countering SIDH attacks by masking information |  |  | read |
| KN-LIT-4830 | Machine-Checked Security for XMSS |  |  | read |
| KN-LIT-4831 | MacORAMa: Optimal Oblivious RAM with Integrity |  |  | read |
| KN-LIT-4832 | Mac’n’Cheese: Zero-Knowledge Proofs for Boolean and Arithmetic Circuits with Nested Disjunctions |  |  | read |
| KN-LIT-4833 | Magic Adversaries Versus Individual Reduction: Science Wins Either Way ? |  |  | read |
| KN-LIT-4834 | Making a Faster Cryptanalytic Time-Memory Trade-Off |  |  | read |
| KN-LIT-4835 | Making Masking Security Proofs Concrete Or How to Evaluate the Security of any Leaking Device |  |  | read |
| KN-LIT-4836 | Making NTRU as Secure as Worst-Case Problems over Ideal Lattices |  |  | read |
| KN-LIT-4837 | Making Password Authenticated Key Exchange suitable for resource-constrained industrial control devices |  |  | read |
| KN-LIT-4838 | Making Private Function Evaluation Safer |  |  | read |
| KN-LIT-4839 | Making Public Key Functional Encryption |  |  | read |
| KN-LIT-4840 | Making RSA–PSS Provably Secure Against Non-Random Faults Gilles Barthe1 , François Dupressoir1 , Pierre-Alain Fouque2 , Benjamin Grégoire4 |  |  | read |
| KN-LIT-4841 | Making Sigma-protocols Non-interactive without Random Oracles |  |  | read |
| KN-LIT-4842 | Making the Best of a Leaky Situation: Zero-Knowledge PCPs from Leakage-Resilient Circuits |  |  | read |
| KN-LIT-4843 | Maliciously Secure Massively Parallel Computation for All-but-One Corruptions |  |  | read |
| KN-LIT-4844 | Maliciously Secure Matrix Multiplication with Applications to Private Deep Learning? |  |  | read |
| KN-LIT-4845 | Maliciously Secure Oblivious Linear Function Evaluation with Constant Overhead |  |  | read |
| KN-LIT-4846 | Maliciously-Secure MrNISC in the Plain Model |  |  | read |
| KN-LIT-4847 | Malleable Proof Systems and Applications |  |  | read |
| KN-LIT-4848 | MAME: A Compression Function with Reduced |  |  | read |
| KN-LIT-4849 | Man-in-the-Middle Secure Authentication Schemes from LPN and Weak PRFs |  |  | read |
| KN-LIT-4851 | Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS |  |  | read |
| KN-LIT-4852 | Masked Dual-Rail Pre-Charge Logic: DPA-Resistance without Routing Constraints ? |  |  | read |
| KN-LIT-4853 | Masked Triples Amortizing Multiplication Triples across Conditionals |  |  | read |
| KN-LIT-4854 | Masking AES with d + |  |  | read |
| KN-LIT-4855 | Masking against Side-Channel Attacks: a Formal Security Proof |  |  | read |
| KN-LIT-4856 | Masking and Dual-rail Logic Don’t Add Up |  |  | read |
| KN-LIT-4857 | Masking at Gate Level in the Presence of Glitches |  |  | read |
| KN-LIT-4858 | Masking Based Domain Extenders for UOWHFs: Bounds and Constructions Palash Sarkar |  |  | read |
| KN-LIT-4859 | Masking Proofs are Tight and How to Exploit it in Security Evaluations |  |  | read |
| KN-LIT-4860 | Masking Tables—An Underestimated Security Risk |  |  | read |
| KN-LIT-4861 | Masking the GLP Lattice-Based Signature Scheme at Any Order Gilles Barthe1 , Sonia Belaı̈d2 , Thomas Espitau3 , Pierre-Alain Fouque4 |  |  | read |
| KN-LIT-4862 | Masking vs. Multiparty Computation: How Large is the Gap for AES? |  |  | read |
| KN-LIT-4863 | Masks will Fall Off Higher-Order Optimal Distinguishers |  |  | read |
| KN-LIT-4864 | Master-Key KDM-Secure ABE via Predicate Encoding |  |  | read |
| KN-LIT-4865 | Master-Key KDM-Secure IBE from Pairings |  |  | read |
| KN-LIT-4866 | Match Box Meet-in-the-Middle Attack against KATAN |  |  | read |
| KN-LIT-4867 | Match Me if You Can: Matchmaking Encryption and its Applications |  |  | read |
| KN-LIT-4868 | Math 4527 (Number Theory 2) Lecture #12 of 38 ∼ February 17, 2021 |  |  | read |
| KN-LIT-4869 | Math 7370. Topics in Number Theory: Elliptic Curves and Arithmetic Geometry |  |  | read |
| KN-LIT-4870 | Mathematics and Cryptography: A Marriage of Convenience? |  |  | read |
| KN-LIT-4871 | Matrix PRFs: Constructions, Attacks, and Applications to Obfuscation |  |  | read |
| KN-LIT-4872 | McBits Revisited Tung Chou |  |  | read |
| KN-LIT-4873 | McBits: fast constant-time code-based cryptography |  |  | read |
| KN-LIT-4874 | McEliece and Niederreiter Cryptosystems That Resist Quantum Fourier Sampling Attacks |  |  | read |
| KN-LIT-4875 | McEliece needs a Break – Solving McEliece-1284 and Quasi-Cyclic-2918 with Modern ISD |  |  | read |
| KN-LIT-4876 | McOE: A Family of Almost Foolproof On-Line Authenticated Encryption Schemes |  |  | read |
| KN-LIT-4877 | McTiny: Fast High-Confidence Post-Quantum Key Erasure for Tiny Network Servers |  |  | read |
| KN-LIT-4878 | MD4 is Not One-Way |  |  | read |
| KN-LIT-4879 | MD5 is Weaker than Weak: Attacks on Concatenated Combiners |  |  | read |
| KN-LIT-4880 | Measure-Rewind-Measure: Tighter Quantum Random Oracle Model Proofs for One-Way to |  |  | read |
| KN-LIT-4881 | Measuring, simulating and exploiting the head concavity phenomenon in BKZ |  |  | read |
| KN-LIT-4882 | Meet-in-the-Middle and Impossible Differential Fault Analysis on AES |  |  | read |
| KN-LIT-4883 | Meet-in-the-Middle Attacks and Structural Analysis of Round-Reduced PRINCE |  |  | read |
| KN-LIT-4884 | Meet-in-the-Middle Attacks on Generic Feistel Constructions |  |  | read |
| KN-LIT-4885 | Meet-in-the-Middle Preimage Attacks |  |  | read |
| KN-LIT-4886 | Meet-in-the-Middle Preimage Attacks on AES |  |  | read |
| KN-LIT-4887 | Meet-in-the-Middle Technique for Truncated Differential |  |  | read |
| KN-LIT-4888 | Memento: How to Reconstruct your Secrets from a Single Password in a Hostile Environment |  |  | read |
| KN-LIT-4889 | Memory Checking for Parallel RAMs |  |  | read |
| KN-LIT-4890 | Memory Leakage-Resilient Encryption based on Physically Unclonable Functions |  |  | read |
| KN-LIT-4891 | Memory Lower Bounds of Reductions Revisited |  |  | read |
| KN-LIT-4892 | Memory-Demanding Password Scrambling |  |  | read |
| KN-LIT-4893 | Memory-Efficient Attacks on Small LWE Keys |  |  | read |
| KN-LIT-4894 | Memory-Hard Functions from Cryptographic Primitives |  |  | read |
| KN-LIT-4895 | Memory-Tight Multi-Challenge Security of Public-Key Encryption |  |  | read |
| KN-LIT-4896 | Memory-Tight Reductions |  |  | read |
| KN-LIT-4897 | Memory-Tight Reductions for Practical Key Encapsulation Mechanisms |  |  | read |
| KN-LIT-4898 | Mercurial Commitments with Applications to Zero-Knowledge Sets |  |  | read |
| KN-LIT-4899 | Mercurial Commitments: Minimal Assumptions and Efficient Constructions |  |  | read |
| KN-LIT-4900 | Merkle Puzzles Are Optimal — An O(n2 )-Query Attack on any Key Exchange from a Random Oracle |  |  | read |
| KN-LIT-4901 | Merkle Puzzles in a Quantum World Gilles Brassard1 , Peter Høyer2 , Kassem Kalach1 |  |  | read |
| KN-LIT-4902 | Merkle Tree Traversal in Log Space and Time |  |  | read |
| KN-LIT-4903 | Merkle-Damgård Revisited : how to Construct a Hash Function |  |  | read |
| KN-LIT-4904 | Mersenne Factorization Factory |  |  | read |
| KN-LIT-4905 | Mesh Signatures How to Leak a Secret with Unwitting and Unwilling Participants |  |  | read |
| KN-LIT-4906 | Message Authentication Codes from Unpredictable Block Ciphers |  |  | read |
| KN-LIT-4907 | Message Authentication, Revisited |  |  | read |
| KN-LIT-4908 | Message Franking via Committing Authenticated Encryption |  |  | read |
| KN-LIT-4909 | Message Freedom in MD4 and MD5 Collisions: Application to APOP |  |  | read |
| KN-LIT-4910 | Message Transmission with Reverse Firewalls— Secure Communication on Corrupted Machines |  |  | read |
| KN-LIT-4911 | Message-Locked Encryption and Secure Deduplication |  |  | read |
| KN-LIT-4912 | Message-recovery Laser Fault Injection Attack on the Classic McEliece Cryptosystem |  |  | read |
| KN-LIT-4913 | Methods for studying integral points on elliptic curves |  |  | read |
| KN-LIT-4914 | MHz2k: MPC from HE over Z2k with |  |  | read |
| KN-LIT-4915 | MicroEliece: McEliece for Embedded Devices |  |  | read |
| KN-LIT-4916 | Middle-Product Learning With Errors |  |  | read |
| KN-LIT-4917 | Middle-Product Learning with Rounding |  |  | read |
| KN-LIT-4918 | Midori: A Block Cipher for Low Energy Subhadeep Banik1 , Andrey Bogdanov1 , Takanori Isobe2 , Kyoji Shibutani2 |  |  | read |
| KN-LIT-4919 | MILP-aided Method of Searching Division |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4920 | MILP-Based Automatic Search Algorithms for Differential and Linear Trails for Speck |  |  | read |
| KN-LIT-4921 | MiMC: Efficient Encryption and Cryptographic Hashing with Minimal Multiplicative Complexity |  |  | read |
| KN-LIT-4922 | Mind the Composition: Birthday Bound Attacks on EWCDMD and SoKAC21 |  |  | read |
| KN-LIT-4923 | Mind the Gap: Modular Machine-checked |  |  | read |
| KN-LIT-4924 | Mind the Middle Layer: The HADES Design Strategy Revisited ? |  |  | read |
| KN-LIT-4925 | Mind the Propagation of States New Automatic Search Tool for Impossible Differentials and Impossible Polytopic Transitions |  |  | read |
| KN-LIT-4926 | Miniature CCA2 PK Encryption : Tight Security Without Redundancy |  |  | read |
| KN-LIT-4927 | Minicrypt Primitives with Algebraic Structure and Applications |  |  | read |
| KN-LIT-4928 | MiniLEGO: Efficient Secure Two-Party Computation From General Assumptions |  |  | read |
| KN-LIT-4929 | Minimal Complete Primitives for Secure Multi-Party Computation |  |  | read |
| KN-LIT-4930 | Minimalism in Cryptography: The Even-Mansour Scheme Revisited |  |  | read |
| KN-LIT-4931 | Minimalism of Software Implementation - Extensive Performance Analysis of Symmetric Primitives on the RL78 Microcontroller Mitsuru Matsui and Yumiko Murakami |  |  | read |
| KN-LIT-4933 | Minimizing the Two-Round Even-Mansour Cipher Shan Chen? , Rodolphe Lampe?? , Jooyoung Lee? ? ? |  |  | read |
| KN-LIT-4934 | Minimizing the Two-Round Tweakable |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4935 | Misuse Attacks on Post-Quantum Cryptosystems |  |  | read |
| KN-LIT-4936 | Mitaka: A Simpler, Parallelizable, Maskable Variant of Falcon |  |  | read |
| KN-LIT-4937 | Mitigating Dictionary Attacks on Password-Protected Local Storage |  |  | read |
| KN-LIT-4938 | Mitigating Multi-Target Attacks in Hash-based Signatures |  |  | read |
| KN-LIT-4939 | Mode-Level vs. Implementation-Level Physical |  |  | read |
| KN-LIT-4940 | Modeling for Three-Subset Division Property without Unknown Subset Improved Cube Attacks against Trivium and Grain-128AEAD |  |  | read |
| KN-LIT-4941 | Modeling Key Compromise Impersonation Attacks on Group Key Exchange Protocols |  |  | read |
| KN-LIT-4942 | Modeling Random Oracles under Unpredictable Queries |  |  | read |
| KN-LIT-4943 | MODULAR CURVES OVER NUMBER FIELDS AND ECM |  |  | read |
| KN-LIT-4944 | Modular Design of Role-Symmetric Authenticated Key Exchange Protocols |  |  | read |
| KN-LIT-4945 | Modular Hardware Architecture for Somewhat |  |  | read |
| KN-LIT-4946 | Modular Security Specifications Framework |  |  | read |
| KN-LIT-4947 | MODULES OVER ORDERS |  |  | read |
| KN-LIT-4948 | Modulus Fault Attacks Against RSA-CRT Signatures |  |  | read |
| KN-LIT-4949 | MoniPoly—An Expressive q-SDH-Based Anonymous Attribute-Based Credential System |  |  | read |
| KN-LIT-4950 | Montgomery curves and the Montgomery ladder |  |  | read |
| KN-LIT-4951 | MonZ2k a: Fast Maliciously Secure Two Party Computation on Z2k |  |  | read |
| KN-LIT-4952 | More Constructions of Lossy and |  |  | read |
| KN-LIT-4953 | More Efficient (Almost) Tightly Secure Structure-Preserving Signatures |  |  | read |
| KN-LIT-4954 | More Efficient Algorithms for the NTRU Key Generation using the Field Norm |  |  | read |
| KN-LIT-4955 | More Efficient Constant-Round Multi-Party Computation from BMR and SHE |  |  | read |
| KN-LIT-4956 | More Efficient Digital Signatures with Tight Multi-User Security? |  |  | read |
| KN-LIT-4957 | More Efficient Dishonest Majority Secure Computation over Z2k via Galois Rings |  |  | read |
| KN-LIT-4958 | More Efficient Oblivious Transfer Extensions with Security for Malicious Adversaries? |  |  | read |
| KN-LIT-4959 | More Efficient Public-Key Cryptography with |  |  | read |
| KN-LIT-4960 | More Insight on Deep Learning-aided Cryptanalysis |  |  | read |
| KN-LIT-4961 | More is Less: Perfectly Secure Oblivious Algorithms in the Multi-Server Setting? |  |  | read |
| KN-LIT-4962 | More Powerful and Reliable Second-level |  |  | read |
| KN-LIT-4963 | MOTIF: (Almost) Free Branching in GMW via Vector-Scalar Multiplication |  |  | read |
| KN-LIT-4964 | Moving a Step of ChaCha in Syncopated Rhythm |  |  | read |
| KN-LIT-4965 | MozZ2k arella: Efficient Vector-OLE and Zero-Knowledge Proofs Over Z2k Carsten Baum[0000−0001−7905−0198] , Lennart Braun[0000−0001−9164−305X] |  |  | read |
| KN-LIT-4966 | MPC vs. SFE: Perfect Security in a Unified Corruption Model ? |  |  | read |
| KN-LIT-4967 | MPC-Friendly Symmetric Cryptography from Alternating Moduli: |  |  | read |
| KN-LIT-4968 | MPSign: A Signature from |  |  | read |
| KN-LIT-4969 | Mr NISC: Multiparty Reusable Non-Interactive Secure Computation |  |  | read |
| KN-LIT-4970 | Multi-Authority ABE for Non-Monotonic Access Structures |  |  | read |
| KN-LIT-4971 | Multi-Authority ABE from Lattices without Random Oracles |  |  | read |
| KN-LIT-4972 | Multi-Authority Attribute Based Encryption |  |  | read |
| KN-LIT-4973 | Multi-Bit Cryptosystems Based on Lattice Problems |  |  | read |
| KN-LIT-4974 | Multi-ciphertext security degradation for lattices |  |  | read |
| KN-LIT-4975 | Multi-Client Functional Encryption for Linear Functions in the Standard Model from LWE |  |  | read |
| KN-LIT-4976 | Multi-Client Functional Encryption for Separable Functions Michele Ciampi1 |  |  | read |
| KN-LIT-4977 | Multi-Client Functional Encryption with Fine-Grained Access Control |  |  | read |
| KN-LIT-4978 | Multi-Client Inner Product Encryption: Function-Hiding Instantiations Without Random Oracles |  |  | read |
| KN-LIT-4979 | Multi-Client Non-Interactive Verifiable Computation Seung Geol Choi1? |  |  | read |
| KN-LIT-4980 | Multi-Client Oblivious RAM with Poly-Logarithmic Communication |  |  | read |
| KN-LIT-4981 | Multi-Client Verifiable Computation with Stronger Security Guarantees |  |  | read |
| KN-LIT-4982 | Multi-Designated Receiver Signed Public Key Encryption |  |  | read |
| KN-LIT-4983 | Multi-Hop Fine-Grained Proxy Re-Encryption |  |  | read |
| KN-LIT-4984 | Multi-Identity and Multi-Key Leveled FHE from Learning with Errors |  |  | read |
| KN-LIT-4985 | Multi-Input Attribute Based Encryption and Predicate Encryption |  |  | read |
| KN-LIT-4986 | Multi-Input Functional Encryption for Inner Products: Function-Hiding Realizations and |  |  | read |
| KN-LIT-4987 | Multi-Input Functional Encryption for Unbounded Arity Functions |  |  | read |
| KN-LIT-4988 | Multi-Input Functional Encryption in the Private-Key Setting: Stronger Security from Weaker Assumptions |  |  | read |
| KN-LIT-4989 | Multi-Input Functional Encryption with Unbounded-Message Security |  |  | read |
| KN-LIT-4990 | Multi-Input Functional Encryption? |  |  | read |
| KN-LIT-4991 | Multi-Input Inner-Product |  |  | read |
| KN-LIT-4992 | Multi-Input Quadratic Functional Encryption from Pairings |  |  | read |
| KN-LIT-4993 | Multi-Input Quadratic Functional Encryption: |  |  | read |
| KN-LIT-4994 | Multi-Instance Secure Public-Key Encryption |  |  | read |
| KN-LIT-4995 | Multi-Instance Security and its Application to Password-Based Cryptography |  |  | read |
| KN-LIT-4996 | Multi-key and Multi-input Predicate Encryption from Learning with Errors Danilo Francati1[0000−0002−4639−0636] , Daniele Friolo2[0000−0003−0836−1735] |  |  | read |
| KN-LIT-4997 | Multi-Key FHE from LWE, Revisited |  |  | read |
| KN-LIT-4998 | Multi-key Fully-Homomorphic Encryption in the Plain Model |  |  | read |
| KN-LIT-4999 | Multi-Key Homomophic Encryption from TFHE |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-4dadec | Module-Lattice-Based Digital Signature Standard (FIPS 204) | 2024 | NIST Federal Information Processing Standards Publication | partial |
| KN-LIT-4f3b80 | A Single-Trace Side-Channel Attack on ML-DSA: Practical Full-Key Recovery from a Single Faulty Signature | 2024 | IACR ePrint 2024/238 | partial |
| KN-LIT-5000 | Multi-Key Homomorphic Authenticators |  |  | read |
| KN-LIT-5001 | Multi-Key Homomorphic Signatures Unforgeable under Insider Corruption? |  |  | read |
| KN-LIT-5002 | Multi-Key Searchable Encryption, Revisited |  |  | read |
| KN-LIT-5003 | Multi-Key Security: The Even-Mansour Construction Revisited |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5004 | Multi-Linear Secret-Sharing Schemes |  |  | read |
| KN-LIT-5005 | Multi-Location Leakage Resilient Cryptography |  |  | read |
| KN-LIT-5006 | Multi-Party Computation of Polynomials and Branching Programs without Simultaneous Interaction |  |  | read |
| KN-LIT-5007 | Multi-Party Functional Encryption |  |  | read |
| KN-LIT-5008 | Multi-Party Homomorphic Secret Sharing and Sublinear MPC from Sparse LPN |  |  | read |
| KN-LIT-5009 | Multi-Party Indirect Indexing and Applications |  |  | read |
| KN-LIT-5010 | Multi-Party Key Exchange for Unbounded Parties from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-5011 | Multi-party Stand-alone and Setup-free Verifiably Committed Signatures |  |  | read |
| KN-LIT-5012 | Multi-Party Virtual State Channels Stefan Dziembowski1 , Lisa Eckey2 , Sebastian Faust2 |  |  | read |
| KN-LIT-5013 | Multi-Property Preserving Combiners for Hash Functions |  |  | read |
| KN-LIT-5014 | Multi-property-preserving Domain Extension Using Polynomial-based Modes of Operation |  |  | read |
| KN-LIT-5015 | Multi-property-preserving Hash Domain Extension and the EMD Transform |  |  | read |
| KN-LIT-5016 | Multi-Prover Commitments Against Non-Signaling Attacks |  |  | read |
| KN-LIT-5017 | Multi-Query Computationally-Private Information Retrieval with Constant Communication Rate |  |  | read |
| KN-LIT-5018 | Multi-Signatures for Ad-hoc and Privacy-Preserving Group Signing |  |  | read |
| KN-LIT-5019 | Multi-Target Attacks on the Picnic Signature |  |  | read |
| KN-LIT-5020 | Multi-target DPA attacks: Pushing DPA beyond the limits of a desktop computer |  |  | read |
| KN-LIT-5021 | Multi-theorem Designated-Verifier NIZK for QMA |  |  | read |
| KN-LIT-5022 | Multi-user collisions: Applications to Discrete Logarithm, Even-Mansour and PRINCE |  |  | read |
| KN-LIT-5023 | Multi-user Schnorr security, revisited |  |  | read |
| KN-LIT-5024 | Multi-User Security of the Sum of Truncated |  |  | read |
| KN-LIT-5025 | Multi-Valued Byzantine Broadcast: the t < n Case |  |  | read |
| KN-LIT-5026 | Multi-Variate High-Order Attacks of Shuffled Tables Recomputation |  |  | read |
| KN-LIT-5027 | Multidimensional Extension of Matsui’s |  |  | read |
| KN-LIT-5028 | Multilinear and Aggregate Pseudorandom Functions: |  |  | read |
| KN-LIT-5029 | Multilinear Maps from Obfuscation |  |  | read |
| KN-LIT-5030 | Multilinear Schwartz-Zippel mod N and Lattice-Based Succinct Arguments |  |  | read |
| KN-LIT-5031 | Multimodal Private Signatures Khoa Nguyen[0000−0001−8555−638X] , Fuchun Guo[0000−0001−6939−7710] |  |  | read |
| KN-LIT-5032 | Multiparty Computation for Dishonest Majority: from Passive to Active Security at Low Cost |  |  | read |
| KN-LIT-5033 | Multiparty Computation from Somewhat Homomorphic Encryption |  |  | read |
| KN-LIT-5034 | Multiparty Computation with Low |  |  | read |
| KN-LIT-5035 | Multiparty Generation of an RSA Modulus Megan Chen, Ran Cohen, Jack Doerner, Yashvanth Kondi |  |  | read |
| KN-LIT-5036 | Multiparty Key Exchange, Efficient Traitor Tracing, and More from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-5037 | Multiparty Reusable Non-Interactive Secure Computation from LWE |  |  | read |
| KN-LIT-5038 | Multiple differential cryptanalysis of round-reduced PRINCE ? |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5039 | Multiple Differential Cryptanalysis: Theory and Practice |  |  | read |
| KN-LIT-5040 | Multiple Discrete Logarithm Problems with Auxiliary Inputs |  |  | read |
| KN-LIT-5041 | Multiple Linear Cryptanalysis of a Reduced Round RC6 |  |  | read |
| KN-LIT-5042 | Multiple-Differential Side-Channel Collision Attacks on AES |  |  | read |
| KN-LIT-5043 | Multiplicative Differentials |  |  | read |
| KN-LIT-5044 | Multipurpose Identity-Based Signcryption A Swiss Army Knife for Identity-Based Cryptography Xavier Boyen |  |  | read |
| KN-LIT-5045 | Multitarget Decryption Failure Attacks |  |  | read |
| KN-LIT-5046 | Multivariate Public Key Cryptosystem from Sidon Spaces |  |  | read |
| KN-LIT-5047 | Murmurations of Arithmetic L-functions |  |  | read |
| KN-LIT-5048 | MuSig-L: Lattice-Based Multi-Signature With Single-Round Online Phase |  |  | read |
| KN-LIT-5049 | MuSig2: Simple Two-Round Schnorr Multi-Signatures |  |  | read |
| KN-LIT-5050 | Must the Communication Graph of MPC Protocols be an Expander? |  |  | read |
| KN-LIT-5051 | Must you know the code of f to securely compute f ? |  |  | read |
| KN-LIT-5052 | Mutual Information Analysis: How, When and Why? |  |  | read |
| KN-LIT-5053 | Mutual Information Analysis A Generic Side-Channel Distinguisher |  |  | read |
| KN-LIT-5054 | Mutually Independent Commitments Moses Liskov1 , Anna Lysyanskaya1 , Silvio Micali1 |  |  | read |
| KN-LIT-5055 | NanoCMOS-Molecular Realization of Rijndael |  |  | read |
| KN-LIT-5056 | Naor-Reingold Goes Public: The Complexity of Known-key Security |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5057 | Narrow T-functions |  |  | read |
| KN-LIT-5058 | Narrow-Bicliques: Cryptanalysis of Full IDEA |  |  | read |
| KN-LIT-5059 | Naturally Rehearsing Passwords |  |  | read |
| KN-LIT-5060 | Neal Koblitz |  |  | read |
| KN-LIT-5061 | Near Collision Attack on the Grain v1 Stream Cipher |  |  | read |
| KN-LIT-5062 | Near-Linear Unconditionally-Secure Multiparty Computation with a Dishonest Minority |  |  | read |
| KN-LIT-5063 | Near-Optimal Private Information Retrieval with Preprocessing |  |  | read |
| KN-LIT-5064 | Nearly One-Sided Tests and the Goldreich-Levin Predicate |  |  | read |
| KN-LIT-5065 | Nearly Optimal Property Preserving Hashing |  |  | read |
| KN-LIT-5066 | Nearly Optimal Robust Secret Sharing against Rushing Adversaries |  |  | read |
| KN-LIT-5067 | Nearly Optimal Verifiable Data Streaming Johannes Krupp1 , Dominique Schröder1 , Mark Simkin1 , Dario Fiore2 |  |  | read |
| KN-LIT-5068 | NEON crypto |  |  | read |
| KN-LIT-5069 | Network Agnostic MPC with Statistical Security |  |  | read |
| KN-LIT-5070 | Network Oblivious Transfer |  |  | read |
| KN-LIT-5071 | Network-Agnostic Multi-Party Computation Revisited |  |  | read |
| KN-LIT-5072 | Network-Agnostic Security Comes (Almost) for Free in DKG and MPC |  |  | read |
| KN-LIT-5073 | Network-Hiding Communication and Applications to Multi-Party Protocols |  |  | read |
| KN-LIT-5074 | NEV: Faster and Smaller NTRU Encryption using Vector Decoding |  |  | read |
| KN-LIT-5075 | Never trust a bunny? |  |  | read |
| KN-LIT-5076 | New (and Old) Proof Systems for Lattice Problems |  |  | read |
| KN-LIT-5077 | New AES software speed records |  |  | read |
| KN-LIT-5078 | New algorithms for the Deuring correspondence |  |  | read |
| KN-LIT-5079 | New and Improved Key-Homomorphic Pseudorandom Functions |  |  | read |
| KN-LIT-5080 | New Applications of T-functions in |  |  | read |
| KN-LIT-5081 | New Approach for Selectively Convertible Undeniable Signature Schemes |  |  | read |
| KN-LIT-5082 | New Approaches for Quantum Copy-Protection |  |  | read |
| KN-LIT-5083 | New Approaches to Password Authenticated Key Exchange based on RSA |  |  | read |
| KN-LIT-5084 | New Approaches to Traitor Tracing with Embedded Identities |  |  | read |
| KN-LIT-5085 | New Attacks against Reduced-Round Versions of IDEA |  |  | read |
| KN-LIT-5086 | New attacks against standardized MACs |  |  | read |
| KN-LIT-5087 | New Attacks on Feistel |  |  | read |
| KN-LIT-5088 | New attacks on Keccak-224 and Keccak-256 |  |  | read |
| KN-LIT-5089 | New Attacks on LowMC instances with a Single Plaintext/Ciphertext pair |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5090 | New Attacks on RSA with Small Secret CRT-Exponents |  |  | read |
| KN-LIT-5091 | New Attacks on the Concatenation and XOR |  |  | read |
| KN-LIT-5092 | New Birthday Attacks on Some MACs Based on Block Ciphers |  |  | read |
| KN-LIT-5093 | New Bounds for Keyed Sponges with Extendable Output: Independence between |  |  | read |
| KN-LIT-5094 | New Bounds on the Local Leakage Resilience of Shamir’s Secret Sharing Scheme |  |  | read |
| KN-LIT-5095 | New Chosen-Ciphertext Attacks on NTRU |  |  | read |
| KN-LIT-5096 | New Circular Security Counterexamples from Decision Linear and Learning with Errors |  |  | read |
| KN-LIT-5097 | New Code-Based Privacy-Preserving Cryptographic Constructions |  |  | read |
| KN-LIT-5098 | New Collision Attacks on Round-Reduced Keccak |  |  | read |
| KN-LIT-5099 | New collision attacks on SHA-1 based on optimal joint local-collision analysis Marc Stevens |  |  | read |
| KN-LIT-5100 | New Complexity Trade-Offs for the (Multiple) |  |  | read |
| KN-LIT-5101 | New Composite Operations and Precomputation Scheme for Elliptic Curve Cryptosystems over Prime Fields |  |  | read |
| KN-LIT-5102 | New Constructions and Applications of Trapdoor DDH Groups |  |  | read |
| KN-LIT-5103 | New Constructions of Hinting PRGs, OWFs with Encryption, and more |  |  | read |
| KN-LIT-5104 | New Constructions of Identity-Based and Key-Dependent Message Secure Encryption Schemes ? |  |  | read |
| KN-LIT-5105 | New Constructions of Reusable |  |  | read |
| KN-LIT-5106 | New Constructions of Statistical NIZKs: |  |  | read |
| KN-LIT-5107 | New Cryptanalytic Results on IDEA Eli Biham1 |  |  | read |
| KN-LIT-5108 | New Cryptographic Primitives Based on Multiword T-functions |  |  | read |
| KN-LIT-5109 | New Definitions and Separations for Circular Security |  |  | read |
| KN-LIT-5110 | New Design Techniques for Efficient Arithmetization-Oriented Hash Functions: Anemoi Permutations and Jive Compression Mode |  |  | read |
| KN-LIT-5111 | New Developments in Leakage-Resilient Cryptography |  |  | read |
| KN-LIT-5112 | New Distinguishing Attack on MAC using Secret-Prefix Method |  |  | read |
| KN-LIT-5113 | New Features of Latin Dances: Analysis of Salsa, ChaCha, and |  |  | read |
| KN-LIT-5114 | New Generic Attacks Against Hash-based MACs |  |  | read |
| KN-LIT-5115 | New Guess-and-Determine Attack on the Self-Shrinking Generator ? |  |  | read |
| KN-LIT-5116 | New High Entropy Element for FPGA based True Random Number Generators |  |  | read |
| KN-LIT-5117 | New Impossible Differential Search Tool from |  |  | read |
| KN-LIT-5118 | New Insight into the Isomorphism of Polynomial |  |  | read |
| KN-LIT-5119 | New Insights on AES-Like SPN Ciphers |  |  | read |
| KN-LIT-5120 | New Instantiations of the CRYPTO 2017 Masking Schemes |  |  | read |
| KN-LIT-5121 | New Key Recovery Attacks on Minimal Two-Round Even-Mansour Ciphers |  |  | read |
| KN-LIT-5122 | New Key-Recovery Attacks on HMAC/NMAC-MD4 and |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5123 | New Lattice Two-Stage Sampling Technique and its Applications to Functional Encryption |  |  | read |
| KN-LIT-5124 | New Lightweight DES Variants |  |  | read |
| KN-LIT-5125 | New Links Between Differential and Linear Cryptanalysis |  |  | read |
| KN-LIT-5126 | New Message Difference for MD4 |  |  | read |
| KN-LIT-5127 | New MILP Modeling: Improved Conditional Cube Attacks on Keccak-based Constructions |  |  | read |
| KN-LIT-5128 | New Monotones and Lower Bounds in Unconditional Two-Party Computation |  |  | read |
| KN-LIT-5129 | New Multilinear Maps over the Integers |  |  | read |
| KN-LIT-5130 | New Negative Results on Differing-Inputs Obfuscation |  |  | read |
| KN-LIT-5131 | New Observations on Impossible |  |  | read |
| KN-LIT-5132 | New Online/Offline Signature Schemes Without Random Oracles |  |  | read |
| KN-LIT-5133 | New Parallel Domain Extenders for UOWHF |  |  | read |
| KN-LIT-5134 | New Partial Key Exposure Attacks on RSA |  |  | read |
| KN-LIT-5135 | New Preimage Attacks Against Reduced SHA-1 |  |  | read |
| KN-LIT-5136 | New Proof Methods for Attribute-Based Encryption: Achieving Full Security through Selective Techniques |  |  | read |
| KN-LIT-5137 | New proof systems and an OPRF from CSIDH |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5138 | New Proofs for NMAC and HMAC: Security without Collision-Resistance |  |  | read |
| KN-LIT-5139 | New Public Key Cryptosystem using Finite Non Abelian Groups |  |  | read |
| KN-LIT-5140 | New rank records for elliptic curves with rational torsion |  |  | read |
| KN-LIT-5141 | New Realizations of Somewhere Statistically |  |  | read |
| KN-LIT-5142 | New Results on Boomerang and Rectangle Attacks? |  |  | read |
| KN-LIT-5143 | New results on Gimli: full-permutation |  |  | read |
| KN-LIT-5144 | New Results on Instruction Cache Attacks |  |  | read |
| KN-LIT-5145 | New Results on Modular Inversion Hidden Number |  |  | read |
| KN-LIT-5146 | New Results on the Hardness of Diffie-Hellman Bits |  |  | read |
| KN-LIT-5147 | New security notions and feasibility results for authentication of quantum data |  |  | read |
| KN-LIT-5148 | New Security Proofs for the 3GPP |  |  | read |
| KN-LIT-5149 | New Security Results on Encrypted Key Exchange |  |  | read |
| KN-LIT-5150 | New SIDH Countermeasures for a More Efficient Key Exchange |  |  | read |
| KN-LIT-5151 | New Slide Attacks on Almost Self-Similar Ciphers |  |  | read |
| KN-LIT-5152 | New Techniques for Cryptanalysis of Hash Functions and Improved Attacks on Snefru |  |  | read |
| KN-LIT-5153 | New Techniques for Efficient Trapdoor Functions and Applications |  |  | read |
| KN-LIT-5154 | New Techniques for Obfuscating Conjunctions |  |  | read |
| KN-LIT-5155 | New Techniques for SPHFs and E cient One-Round PAKE Protocols |  |  | read |
| KN-LIT-5156 | New Techniques for Traitor Tracing: Size N 1/3 and More from Pairings |  |  | read |
| KN-LIT-5157 | New Techniques for Zero-Knowledge: Leveraging Inefficient Provers |  |  | read |
| KN-LIT-5158 | New Techniques in Replica Encodings with Client Setup |  |  | read |
| KN-LIT-5159 | New Ways to Garble Arithmetic Circuits |  |  | read |
| KN-LIT-5160 | NIZK from SNARG |  |  | read |
| KN-LIT-5161 | NIZKs with an Untrusted CRS: Security in the Face of Parameter Subversion |  |  | read |
| KN-LIT-5162 | No Time to Hash: On Super-Efficient Entropy Accumulation |  |  | read |
| KN-LIT-5163 | Noisy Leakage Revisited |  |  | read |
| KN-LIT-5164 | Non-Adaptive Universal One-Way Hash Functions from Arbitrary One-Way Functions |  |  | read |
| KN-LIT-5165 | Non-committing encryption from Φ-hiding |  |  | read |
| KN-LIT-5166 | Non-Committing Encryption with Constant Ciphertext Expansion from Standard Assumptions |  |  | read |
| KN-LIT-5167 | Non-Committing Encryption with Quasi-Optimal Ciphertext-Rate Based on the DDH Problem |  |  | read |
| KN-LIT-5168 | Non-cryptographic Primitive for Pseudorandom Permutation |  |  | read |
| KN-LIT-5169 | Non-Full Sbox Linearization: Applications to Collision Attacks on Round-Reduced Keccak |  |  | read |
| KN-LIT-5170 | Non-Full-Active Super-Sbox Analysis: |  |  | read |
| KN-LIT-5171 | Non-Interactive and Re-Usable |  |  | read |
| KN-LIT-5172 | Non-Interactive Anonymous Router with Quasi-Linear Router Computation |  |  | read |
| KN-LIT-5173 | Non-Interactive Anonymous Router? |  |  | read |
| KN-LIT-5174 | Non-Interactive Batch Arguments for NP from Standard Assumptions |  |  | read |
| KN-LIT-5175 | Non-Interactive Blind Signatures for Random Messages |  |  | read |
| KN-LIT-5176 | Non-Interactive CCA-Secure Threshold Cryptosystems with Adaptive Security: |  |  | read |
| KN-LIT-5177 | Non-Interactive CCA2-Secure Threshold Cryptosystems: Achieving Adaptive Security in the Standard Model Without Pairings |  |  | read |
| KN-LIT-5178 | Non-interactive classical verification of quantum computation |  |  | read |
| KN-LIT-5179 | Non-Interactive Commitment from Non-Transitive Group Actions Flamini |  |  | read |
| KN-LIT-5180 | Non-Interactive Composition of Sigma-Protocols via Share-then-Hash |  |  | read |
| KN-LIT-5181 | Non-interactive Distributed-Verifier Proofs and Proving Relations among Commitments |  |  | read |
| KN-LIT-5182 | Non-interactive Distributional Indistinguishability (NIDI) and Non-Malleable Commitments |  |  | read |
| KN-LIT-5183 | Non-Interactive Key Exchange |  |  | read |
| KN-LIT-5184 | Non-Interactive Keyed-Verification Anonymous Credentials |  |  | read |
| KN-LIT-5185 | Non-interactive Mimblewimble transactions, revisited |  |  | read |
| KN-LIT-5186 | Non-Interactive Multiparty Computation |  |  | read |
| KN-LIT-5187 | Non-Interactive Non-Malleability from Quantum Supremacy |  |  | read |
| KN-LIT-5188 | Non-Interactive Proofs for Integer Multiplication |  |  | read |
| KN-LIT-5189 | Non-Interactive Publicly-Verifiable Delegation of Committed Programs |  |  | read |
| KN-LIT-5190 | Non-Interactive Secure 2PC in the Offline/Online and Batch Settings |  |  | read |
| KN-LIT-5191 | Non-Interactive Secure Computation of Inner-Product from LPN and LWE |  |  | read |
| KN-LIT-5192 | Non-Interactive Secure Multiparty Computation for Symmetric Functions, Revisited: |  |  | read |
| KN-LIT-5193 | Non-Interactive Secure Multiparty Computation? |  |  | read |
| KN-LIT-5194 | Non-Interactive Timestamping in the Bounded Storage Model |  |  | read |
| KN-LIT-5195 | Non-interactive Universal Arguments |  |  | read |
| KN-LIT-5196 | Non-Interactive Verifiable Computing: Outsourcing Computation to Untrusted Workers |  |  | read |
| KN-LIT-5197 | Non-interactive Zaps and New Techniques for NIZK |  |  | read |
| KN-LIT-5198 | Non-Interactive Zero Knowledge from Sub-exponential DDH |  |  | read |
| KN-LIT-5199 | Non-Interactive Zero-Knowledge Arguments for QMA, with preprocessing |  |  | read |
| KN-LIT-5200 | Non-Interactive Zero-Knowledge from Homomorphic Encryption |  |  | read |
| KN-LIT-5201 | Non-Interactive Zero-Knowledge from Non-Interactive Batch Arguments |  |  | read |
| KN-LIT-5202 | Non-Interactive Zero-Knowledge Functional Proofs |  |  | read |
| KN-LIT-5203 | Non-Interactive Zero-Knowledge in Pairing-Free Groups from Weaker Assumptions |  |  | read |
| KN-LIT-5204 | Non-Interactive Zero-Knowledge Proofs for Composite Statements |  |  | read |
| KN-LIT-5205 | Non-interactive zero-knowledge proofs in the quantum random oracle model |  |  | read |
| KN-LIT-5206 | Non-Interactive Zero-Knowledge Proofs to Multiple Verifiers |  |  | read |
| KN-LIT-5207 | Non-Interactive Zero-Knowledge Proofs with Fine-Grained Security |  |  | read |
| KN-LIT-5208 | Non-Malleability against Polynomial Tampering |  |  | read |
| KN-LIT-5209 | Non-Malleability from Malleability: Simulation-Sound Quasi-Adaptive NIZK Proofs and CCA2-Secure Encryption from Homomorphic Signatures |  |  | read |
| KN-LIT-5210 | Non-Malleability vs. CCA-Security: The Case of Commitments |  |  | read |
| KN-LIT-5211 | Non-Malleable Codes for Bounded Parallel-Time Tampering |  |  | read |
| KN-LIT-5212 | Non-Malleable Codes for Partial Functions with Manipulation Detection |  |  | read |
| KN-LIT-5213 | Non-Malleable Codes from Two-Source Extractors? |  |  | read |
| KN-LIT-5214 | Non-Malleable Codes, Extractors and Secret Sharing for Interleaved Tampering and Composition of Tampering |  |  | read |
| KN-LIT-5215 | Non-Malleable Coding Against Bit-wise and Split-State Tampering? |  |  | read |
| KN-LIT-5216 | Non-malleable Commitments Against Quantum Attacks |  |  | read |
| KN-LIT-5217 | Non-Malleable Condensers for Arbitrary Min-Entropy, and Almost Optimal Protocols for Privacy Amplification |  |  | read |
| KN-LIT-5218 | Non-Malleable Encryption: Simpler, Shorter, Stronger |  |  | read |
| KN-LIT-5219 | Non-Malleable Functions and Their Applications ? |  |  | read |
| KN-LIT-5220 | Non-Malleable Obfuscation |  |  | read |
| KN-LIT-5221 | Non-Malleable Secret Sharing against Bounded Joint-Tampering Attacks in the Plain Model |  |  | read |
| KN-LIT-5222 | Non-Malleable Secret Sharing for General Access Structures |  |  | read |
| KN-LIT-5223 | Non-Malleable Secret Sharing in the Computational Setting: Adaptive Tampering |  |  | read |
| KN-LIT-5224 | Non-Malleable Statistically Hiding Commitment from Any One-Way Function |  |  | read |
| KN-LIT-5225 | Non-Malleable Time-Lock Puzzles and Applications |  |  | read |
| KN-LIT-5226 | Non-Malleable Vector Commitments via Local Equivocability |  |  | read |
| KN-LIT-5227 | Non-randomness of S-unit lattices |  |  | read |
| KN-LIT-5228 | Non-Trivial Black-Box Combiners for Collision-Resistant Hash-Functions don’t Exist |  |  | read |
| KN-LIT-5229 | Non-Uniform Bounds in the Random-Permutation, Ideal-Cipher, and Generic-Group Models |  |  | read |
| KN-LIT-5230 | Non-uniform cracks in the concrete: the power of free precomputation |  |  | read |
| KN-LIT-5231 | Non-uniformity and Quantum Advice in the Quantum Random Oracle Model |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5232 | Non-Uniformly Sound Certificates with Applications to Concurrent Zero-Knowledge |  |  | read |
| KN-LIT-5233 | Non-Wafer-Scale Sieving Hardware for the NFS: Another Attempt to Cope with 1024-bit |  |  | read |
| KN-LIT-5234 | Non-Zero Inner Product Encryption Schemes from Various Assumptions: LWE, DDH and DCR |  |  | read |
| KN-LIT-5235 | Nonce-Based Cryptography: Retaining Security when Randomness Fails |  |  | read |
| KN-LIT-5236 | Nonce-Based Symmetric Encryption |  |  | read |
| KN-LIT-5237 | Nonces are Noticed: AEAD Revisited |  |  | read |
| KN-LIT-5238 | Noninteractive Statistical Zero-Knowledge Proofs for Lattice Problems |  |  | read |
| KN-LIT-5239 | Noninteractive Zero Knowledge for NP from (Plain) Learning With Errors |  |  | read |
| KN-LIT-5240 | Nonlinear Equivalence of Stream Ciphers |  |  | read |
| KN-LIT-5241 | Nonlinear Invariant Attack Practical Attack on Full SCREAM, iSCREAM, and Midori64 |  |  | read |
| KN-LIT-5242 | Nonmalleable Digital Lockers and Robust Fuzzy Extractors in the Plain Model |  |  | read |
| KN-LIT-5243 | Nostradamus goes Quantum |  |  | read |
| KN-LIT-5244 | Notions of Black-Box Reductions, Revisited |  |  | read |
| KN-LIT-5245 | Nova: Recursive Zero-Knowledge Arguments from Folding Schemes |  |  | read |
| KN-LIT-5246 | NTRU Fatigue: How Stretched is Overstretched ? Léo Ducas & Wessel van Woerden |  |  | read |
| KN-LIT-5247 | NTRU Prime: reducing attack surface at low cost |  |  | read |
| KN-LIT-5248 | NTRUCCA: How to Strengthen NTRUEncrypt to Chosen-Ciphertext Security in the Standard Model |  |  | read |
| KN-LIT-5249 | Number Theory (part 7): Elliptic Curves |  |  | read |
| KN-LIT-5250 | Numerical Method for Comparison on Homomorphically Encrypted Numbers |  |  | read |
| KN-LIT-5251 | OAEP 3-Round |  |  | read |
| KN-LIT-5252 | OAEP is Secure Under Key-Dependent Messages |  |  | read |
| KN-LIT-5253 | OAEP Reconsidered |  |  | read |
| KN-LIT-5254 | Obfuscated Fuzzy Hamming Distance and Conjunctions from Subset Product Problems |  |  | read |
| KN-LIT-5255 | Obfuscating Circuits via Composite-Order Graded Encoding |  |  | read |
| KN-LIT-5256 | Obfuscating Conjunctions |  |  | read |
| KN-LIT-5257 | Obfuscating Point Functions with Multibit Output ? |  |  | read |
| KN-LIT-5258 | Obfuscating Simple Functionalities from Knowledge assumptions |  |  | read |
| KN-LIT-5259 | Obfuscation Combiners |  |  | read |
| KN-LIT-5260 | Obfuscation for Cryptographic Purposes |  |  | read |
| KN-LIT-5261 | Obfuscation for Evasive Functions Boaz Barak1 , Nir Bitansky2 ? , Ran Canetti2,3 ?? |  |  | read |
| KN-LIT-5262 | Obfuscation of Hyperplane Membership |  |  | read |
| KN-LIT-5263 | Obfuscation of Probabilistic Circuits and Applications |  |  | read |
| KN-LIT-5264 | Obfuscation-based Non-black-box Simulation and Four Message Concurrent Zero Knowledge for NP |  |  | read |
| KN-LIT-5265 | Obfustopia Built on Secret-Key Functional Encryption |  |  | read |
| KN-LIT-5266 | Oblivious Accumulators |  |  | read |
| KN-LIT-5267 | Oblivious Hashing Revisited, and Applications to |  |  | read |
| KN-LIT-5268 | Oblivious Key-Value Stores and Amplification for Private Set Intersection |  |  | read |
| KN-LIT-5269 | Oblivious Message Retrieval |  |  | read |
| KN-LIT-5270 | Oblivious Network RAM and Leveraging Parallelism to Achieve Obliviousness |  |  | read |
| KN-LIT-5271 | Oblivious Parallel RAM and Applications |  |  | read |
| KN-LIT-5272 | Oblivious Parallel RAM: |  |  | read |
| KN-LIT-5273 | Oblivious Polynomial Evaluation and Oblivious Neural Learning |  |  | read |
| KN-LIT-5274 | Oblivious Polynomial Evaluation and Secure Set-Intersection from Algebraic PRFs |  |  | read |
| KN-LIT-5275 | Oblivious Pseudorandom Functions from Isogenies |  |  | read |
| KN-LIT-5276 | Oblivious RAM Revisited |  |  | read |
| KN-LIT-5277 | Oblivious RAM with O((log N )3 ) Worst-Case Cost |  |  | read |
| KN-LIT-5278 | Oblivious RAM with Worst-Case Logarithmic Overhead |  |  | read |
| KN-LIT-5279 | Oblivious Transfer from Any Non-Trivial Elastic Noisy Channel via Secret Key Agreement |  |  | read |
| KN-LIT-5280 | Oblivious Transfer from Trapdoor Permutations in Minimal Rounds Arka Rai Choudhuri1[0000−0003−0452−3426] |  |  | read |
| KN-LIT-5281 | Oblivious Transfer from Weak Noisy Channels Jürg Wullschleger |  |  | read |
| KN-LIT-5282 | Oblivious Transfer from Zero-Knowledge Proofs |  |  | read |
| KN-LIT-5283 | Oblivious Transfer in Incomplete Networks |  |  | read |
| KN-LIT-5284 | Oblivious Transfer in the Bounded Storage Model |  |  | read |
| KN-LIT-5285 | Oblivious Transfer is in MiniQCrypt |  |  | read |
| KN-LIT-5286 | Oblivious Transfer is Symmetric |  |  | read |
| KN-LIT-5287 | Oblivious Transfer with Constant Computational Overhead |  |  | read |
| KN-LIT-5288 | Oblivious Transfer with Hidden Access Control Policies |  |  | read |
| KN-LIT-5289 | Oblivious-Transfer Amplification Jürg Wullschleger |  |  | read |
| KN-LIT-5290 | Oblivious-Transfer Complexity of Noisy Coin-Toss via Secure Zero Communication Reductions |  |  | read |
| KN-LIT-5291 | Observations on COMET |  |  | read |
| KN-LIT-5292 | Observations on the SIMON block cipher family |  |  | read |
| KN-LIT-5293 | Ofelimos: Combinatorial Optimization via Proof-of-Useful-Work |  |  | read |
| KN-LIT-5294 | Off-Line/On-Line Signatures: Theoretical |  |  | read |
| KN-LIT-5295 | OMAC: One-Key CBC MAC |  |  | read |
| KN-LIT-5296 | On 2-Round Secure Multiparty Computation |  |  | read |
| KN-LIT-5297 | On a Generalization of Substitution-Permutation Networks: The HADES Design Strategy |  |  | read |
| KN-LIT-5298 | On Actively-Secure Elementary MPC Reductions |  |  | read |
| KN-LIT-5299 | On Average-Case Hardness in TFNP from One-Way Functions? |  |  | read |
| KN-LIT-5300 | On Basing Private Information Retrieval on NP-Hardness |  |  | read |
| KN-LIT-5301 | On Basing Search SIVP on NP-Hardness |  |  | read |
| KN-LIT-5302 | On Basing Size-Verifiable One-Way Functions on NP-Hardness |  |  | read |
| KN-LIT-5303 | On Best-Possible Obfuscation |  |  | read |
| KN-LIT-5304 | ON BINARY QUARTICS AND THE CASSELS-TATE PAIRING |  |  | read |
| KN-LIT-5305 | On Black-Box Complexity of Universally Composable Security in the CRS model |  |  | read |
| KN-LIT-5306 | On Black-Box Constructions of Predicate Encryption from Trapdoor Permutations |  |  | read |
| KN-LIT-5307 | On Black-Box Constructions of Time and Space |  |  | read |
| KN-LIT-5308 | On Black-Box Extensions of Non-Interactive |  |  | read |
| KN-LIT-5309 | On Black-Box Knowledge-Sound |  |  | read |
| KN-LIT-5310 | On Black-Box Reductions between Predicate Encryption Schemes |  |  | read |
| KN-LIT-5311 | On Black-Box Separations among Injective One-Way Functions |  |  | read |
| KN-LIT-5312 | On Black-Box Verifiable Outsourcing Amit Agarwal1[0000−0002−7642−1341] , Navid Alamati2[0000−0001−8621−7486] |  |  | read |
| KN-LIT-5313 | On Bounded Distance Decoding with Predicate: Breaking the “Lattice Barrier” for the Hidden Number Problem |  |  | read |
| KN-LIT-5314 | On Bounded Distance Decoding, Unique Shortest Vectors, and the Minimum Distance Problem |  |  | read |
| KN-LIT-5315 | On Building Fine-Grained One-Way Functions from Strong Average-Case Hardness |  |  | read |
| KN-LIT-5316 | On Cipher-Dependent Related-Key Attacks in the Ideal-Cipher Model |  |  | read |
| KN-LIT-5317 | On Class Group Computations Using the Number Field Sieve |  |  | read |
| KN-LIT-5318 | On Codes and Learning with Errors over Function Fields |  |  | read |
| KN-LIT-5319 | On Communication Models and Best-Achievable Security in Two-Round MPC |  |  | read |
| KN-LIT-5320 | On Communication-Efficient Asynchronous MPC with Adaptive Security |  |  | read |
| KN-LIT-5321 | On Complete Primitives for Fairness |  |  | read |
| KN-LIT-5322 | On Composable Security for Digital Signatures |  |  | read |
| KN-LIT-5323 | On Computational Shortcuts for Information-Theoretic PIR |  |  | read |
| KN-LIT-5324 | On Computing Nearest Neighbors with Applications to Decoding of Binary Linear Codes |  |  | read |
| KN-LIT-5325 | On Concurrently Secure Computation in the Multiple Ideal Query Model |  |  | read |
| KN-LIT-5326 | On Constant-Round Concurrent Zero-Knowledge |  |  | read |
| KN-LIT-5327 | On Constructing Certificateless Cryptosystems from Identity Based Encryption |  |  | read |
| KN-LIT-5328 | On Constructing Locally Computable Extractors and Cryptosystems in the Bounded Storage Model? |  |  | read |
| KN-LIT-5329 | On Constructing One-Way Permutations from Indistinguishability Obfuscation? |  |  | read |
| KN-LIT-5330 | On Continual Leakage of Discrete Log Representations |  |  | read |
| KN-LIT-5331 | On Cryptographic Assumptions and Challenges |  |  | read |
| KN-LIT-5332 | On Cut-and-Choose Oblivious Transfer and Its Variants |  |  | read |
| KN-LIT-5333 | On definitions of selective opening security |  |  | read |
| KN-LIT-5334 | On Deniability in Quantum Key Exchange |  |  | read |
| KN-LIT-5335 | On Deniability in the Common Reference String and Random Oracle Model |  |  | read |
| KN-LIT-5336 | On Diamond Structures and Trojan Message Attacks |  |  | read |
| KN-LIT-5337 | On Diophantine Complexity and Statistical |  |  | read |
| KN-LIT-5338 | On dual lattice attacks against small-secret LWE |  |  | read |
| KN-LIT-5339 | On Efficient Message Authentication Via Block Cipher Design Techniques |  |  | read |
| KN-LIT-5340 | On Efficient Zero-Knowledge PCPs |  |  | read |
| KN-LIT-5341 | On ELFs, Deterministic Encryption, and Correlated-Input Security |  |  | read |
| KN-LIT-5342 | On Error Correction in the Exponent Chris Peikert |  |  | read |
| KN-LIT-5343 | On Expected Constant-Round Protocols for Byzantine Agreement |  |  | read |
| KN-LIT-5344 | On expected polynomial runtime in cryptography |  |  | read |
| KN-LIT-5345 | On Extractability Obfuscation |  |  | read |
| KN-LIT-5346 | On Feistel Ciphers using Optimal Diffusion Mappings across Multiple Rounds |  |  | read |
| KN-LIT-5347 | On Feistel Structures Using a Diffusion Switching Mechanism |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5348 | On Finding Quantum Multi-collisions |  |  | read |
| KN-LIT-5349 | On Fully Secure MPC with Solitary Output Shai Halevi1 , Yuval Ishai2 , Eyal Kushilevitz2 |  |  | read |
| KN-LIT-5350 | On Gaussian sampling, smoothing parameter and application to signatures |  |  | read |
| KN-LIT-5351 | On Generic Constructions of Circularly-Secure, Leakage-Resilient Public-Key Encryption Schemes |  |  | read |
| KN-LIT-5352 | On Hardness Amplification of One-Way Functions |  |  | read |
| KN-LIT-5353 | On Homomorphic Encryption and Chosen-Ciphertext Security |  |  | read |
| KN-LIT-5354 | On Homomorphic Secret Sharing from Polynomial-Modulus LWE |  |  | read |
| KN-LIT-5355 | On Ideal Lattices and Learning with Errors Over Rings |  |  | read |
| KN-LIT-5356 | On IND-qCCA security in the ROM and its applications CPA security is sufficient for TLS 1.3 |  |  | read |
| KN-LIT-5357 | On Information-Theoretic Secure Multiparty Computation with Local Repairability |  |  | read |
| KN-LIT-5358 | On Instantiating the Algebraic Group Model from Falsifiable Assumptions |  |  | read |
| KN-LIT-5359 | On Instantiating Unleveled Fully-Homomorphic Signatures from Falsifiable Assumptions |  |  | read |
| KN-LIT-5360 | On Invertible Sampling and Adaptive Security Yuval Ishai1,? , Abishek Kumarasubramanian2 |  |  | read |
| KN-LIT-5361 | On Kilian’s Randomization of Multilinear Map Encodings |  |  | read |
| KN-LIT-5362 | On Lightweight Stream Ciphers with Shorter Internal States |  |  | read |
| KN-LIT-5363 | On Linear Communication Complexity for (Maximally) Fluid MPC |  |  | read |
| KN-LIT-5364 | On Minimal Assumptions for Sender-Deniable Public |  |  | read |
| KN-LIT-5365 | On Module Unique-SVP and NTRU |  |  | read |
| KN-LIT-5366 | On Montgomery-Like Representations for Elliptic Curves over GF (2k ) |  |  | read |
| KN-LIT-5367 | On Multiparty Garbling of Arithmetic Circuits |  |  | read |
| KN-LIT-5368 | On Non-uniform Security for Black-box Non-Interactive CCA Commitments |  |  | read |
| KN-LIT-5369 | On Obfuscation with Random Oracles |  |  | read |
| KN-LIT-5370 | On One-way Functions and Sparse Languages |  |  | read |
| KN-LIT-5371 | On Optimal Tightness for Key Exchange with Full Forward Secrecy via Key Confirmation |  |  | read |
| KN-LIT-5372 | On Pairing-Free Blind Signature Schemes in the Algebraic Group Model |  |  | read |
| KN-LIT-5373 | On Perfect Correctness in (Lockable) Obfuscation |  |  | read |
| KN-LIT-5374 | On Perfect Linear Approximations and Differentials over Two-Round SPNs |  |  | read |
| KN-LIT-5375 | On plateaued functions and their constructions |  |  | read |
| KN-LIT-5376 | On Polynomial Functions Modulo pe and Faster Bootstrapping for Homomorphic Encryption |  |  | read |
| KN-LIT-5377 | ON POWERFUL INTEGERS EXPRESSIBLE AS SUMS OF TWO COPRIME FOURTH POWERS |  |  | read |
| KN-LIT-5378 | On Privacy Models for RFID |  |  | read |
| KN-LIT-5379 | On Provably Secure Time-Stamping Schemes |  |  | read |
| KN-LIT-5380 | On Proving Equivalence Class Signatures Secure from Non-interactive Assumptions |  |  | read |
| KN-LIT-5381 | On Pseudorandom Encodings |  |  | read |
| KN-LIT-5382 | On Public Key Encryption from Noisy Codewords? |  |  | read |
| KN-LIT-5383 | On Publicly-Accountable Zero-Knowledge and Small Shuffle Arguments |  |  | read |
| KN-LIT-5384 | On QA-NIZK in the BPK Model |  |  | read |
| KN-LIT-5385 | On Quantum Advantage in Information Theoretic Single-Server PIR |  |  | read |
| KN-LIT-5386 | On Quantum Secure Compressing Pseudorandom Functions Ritam Bhaumik1[0000−0002−2883−4870] , Benoı̂t Cogliati2[0000−0001−6445−2514] |  |  | read |
| KN-LIT-5387 | On Randomizing Hash Functions to Strengthen the Security of Digital Signatures |  |  | read |
| KN-LIT-5388 | On Rejection Sampling in Lyubashevsky’s Signature Scheme |  |  | read |
| KN-LIT-5389 | On Related-Secret Pseudorandomness |  |  | read |
| KN-LIT-5390 | On Removing Graded Encodings from Functional Encryption |  |  | read |
| KN-LIT-5391 | On Reverse-Engineering S-Boxes with Hidden Design Criteria or Structure |  |  | read |
| KN-LIT-5392 | On Robust Combiners for Oblivious Transfer and Other Primitives |  |  | read |
| KN-LIT-5393 | On Robust Combiners for Private Information |  |  | read |
| KN-LIT-5394 | On Round Optimal Statistical Zero Knowledge Arguments |  |  | read |
| KN-LIT-5395 | On Round-Optimal Zero Knowledge in the Bare Public-Key Model |  |  | read |
| KN-LIT-5396 | On Second-Order Differential Power Analysis? |  |  | read |
| KN-LIT-5397 | On Secret Sharing, Randomness, and Random-less Reductions for Secret Sharing Divesh Aggarwal1[0000−0002−3841−0262] , Eldon Chung1[0000−0002−0048−4610] |  |  | read |
| KN-LIT-5398 | On Secure Computation of Solitary Output |  |  | read |
| KN-LIT-5399 | On Secure Multi-Party Computation in Black-Box Groups |  |  | read |
| KN-LIT-5400 | On Seed-Incompressible Functions |  |  | read |
| KN-LIT-5401 | On Selective-Opening Security of Deterministic Primitives |  |  | read |
| KN-LIT-5402 | On Signatures of Knowledge |  |  | read |
| KN-LIT-5403 | ON SMOOTH PLANE MODELS FOR MODULAR CURVES OF SHIMURA TYPE |  |  | read |
| KN-LIT-5404 | On Statistically Secure Obfuscation with Approximate Correctness |  |  | read |
| KN-LIT-5405 | On Strong Simulation and Composable Point Obfuscation |  |  | read |
| KN-LIT-5406 | On Structure-Preserving Cryptography and Lattices |  |  | read |
| KN-LIT-5407 | On Succinct Non-Interactive Arguments in Relativized Worlds |  |  | read |
| KN-LIT-5408 | On Symmetric Encryption and Point Obfuscation |  |  | read |
| KN-LIT-5409 | On Symmetric Encryption with Distinguishable Decryption Failures |  |  | read |
| KN-LIT-5410 | On Tamper-Resistance from a Theoretical Viewpoint The Power of Seals? |  |  | read |
| KN-LIT-5411 | On the (Im)plausibility of Public-Key Quantum Money from Collision-Resistant Hash Functions |  |  | read |
| KN-LIT-5412 | On the (Im)Possibility of Arthur-Merlin Witness Hiding Protocols |  |  | read |
| KN-LIT-5413 | On the (Im)Possibility of Key Dependent Encryption? |  |  | read |
| KN-LIT-5414 | On the (Im)possibility of Obfuscating Programs |  |  | read |
| KN-LIT-5415 | On the (Im)possibility of Projecting Property in Prime-Order Setting |  |  | read |
| KN-LIT-5416 | On The (In)security Of Fischlin’s Paradigm |  |  | read |
| KN-LIT-5417 | On the (in)security of ROS |  |  | read |
| KN-LIT-5418 | On the (In)security of SNARKs in the Presence of Oracles |  |  | read |
| KN-LIT-5419 | On the (In)Security of the Diffie-Hellman Oblivious PRF with Multiplicative Blinding |  |  | read |
| KN-LIT-5420 | On the (Ir)Replaceability of Global Setups, or How (Not) to Use a Global Ledger |  |  | read |
| KN-LIT-5421 | On the Achievability of Simulation-Based |  |  | read |
| KN-LIT-5422 | On the Adaptive Security of MACs and PRFs? |  |  | read |
| KN-LIT-5423 | On the Additive Differential Probability of Exclusive-Or |  |  | read |
| KN-LIT-5424 | On the Amortized Complexity of Zero-knowledge Protocols |  |  | read |
| KN-LIT-5425 | On the Analysis of Cryptographic Assumptions in the Generic Ring Model? |  |  | read |
| KN-LIT-5426 | On the behaviors of affine equivalent Sboxes |  |  | read |
| KN-LIT-5427 | On the Bit Security of Cryptographic Primitives? |  |  | read |
| KN-LIT-5428 | On the Bit Security of Elliptic Curve Diffie–Hellman |  |  | read |
| KN-LIT-5429 | On the Bit Security of NTRUEncrypt |  |  | read |
| KN-LIT-5430 | On the Black-Box Complexity of Optimally-Fair Coin Tossing |  |  | read |
| KN-LIT-5431 | On the Bottleneck Complexity of MPC with Correlated Randomness? |  |  | read |
| KN-LIT-5432 | On the Bounded Sum-of-digits Discrete |  |  | read |
| KN-LIT-5433 | On the CCA Compatibility of Public-Key Infrastructure |  |  | read |
| KN-LIT-5434 | On the Circular Security of Bit-Encryption |  |  | read |
| KN-LIT-5435 | On the Complexity of Additively Homomorphic UC Commitments Tore Kasper Frederiksen, Thomas P. Jakobsen |  |  | read |
| KN-LIT-5436 | On the Complexity of Arithmetic Secret Sharing |  |  | read |
| KN-LIT-5437 | On the Complexity of Collision Resistant Hash Functions: New and Old Black-Box Separations |  |  | read |
| KN-LIT-5438 | On the Complexity of Compressing Obfuscation Gilad Asharov1? , Naomi Ephraim2?? |  |  | read |
| KN-LIT-5439 | On the Complexity of Fair Coin Flipping |  |  | read |
| KN-LIT-5440 | On the Complexity of Non-Adaptively Increasing the Stretch of Pseudorandom Generators |  |  | read |
| KN-LIT-5441 | On the Complexity of Parallel Hardness Amplification for One-Way Functions |  |  | read |
| KN-LIT-5442 | On the Complexity of Scrypt and Proofs of Space in the Parallel Random Oracle Model Joël |  |  | read |
| KN-LIT-5443 | On the Complexity of UC Commitments? |  |  | read |
| KN-LIT-5444 | On the Composition of Public-Coin Zero-Knowledge Protocols |  |  | read |
| KN-LIT-5445 | On the Composition of Two-Prover |  |  | read |
| KN-LIT-5446 | On the Compressed-Oracle Technique, and Post-Quantum Security of Proofs of Sequential Work ? |  |  | read |
| KN-LIT-5447 | On the computation and evaluation of modular polynomials |  |  | read |
| KN-LIT-5448 | On the Computational Overhead of MPC with Dishonest Majority |  |  | read |
| KN-LIT-5449 | On the Concrete Security of Goldreich’s Pseudorandom Generator |  |  | read |
| KN-LIT-5450 | On the Concrete Security of TLS 1.3 PSK Mode? |  |  | read |
| KN-LIT-5451 | On the Concurrent Composition of Quantum Zero-Knowledge |  |  | read |
| KN-LIT-5452 | On the Connection between Leakage Tolerance and Adaptive Security |  |  | read |
| KN-LIT-5453 | On the Construction of Lightweight Circulant Involutory MDS Matrices |  |  | read |
| KN-LIT-5454 | On the Correlation Intractability of Obfuscated Pseudorandom Functions |  |  | read |
| KN-LIT-5455 | On the Cost of Post-Compromise Security in Concurrent Continuous Group-Key Agreement |  |  | read |
| KN-LIT-5456 | On the Cryptographic Complexity of the Worst Functions? |  |  | read |
| KN-LIT-5457 | On the Depth of Oblivious Parallel RAM? |  |  | read |
| KN-LIT-5458 | On the Design of Hardware Building Blocks for Modern Lattice-Based Encryption Schemes Norman Göttert, Thomas Feller, Michael Schneider |  |  | read |
| KN-LIT-5459 | On the Discrete Logarithm Problem on Algebraic Tori ? |  |  | read |
| KN-LIT-5460 | On The Distribution of Linear Biases: Three Instructive Examples? |  |  | read |
| KN-LIT-5461 | On the Effectiveness of the Remanence Decay Side-Channel to Clone Memory-based PUFs |  |  | read |
| KN-LIT-5462 | On the Efficiency of Bit Commitment Reductions |  |  | read |
| KN-LIT-5463 | On the Efficiency of Classical and Quantum Oblivious Transfer Reductions |  |  | read |
| KN-LIT-5464 | On the Enumeration of Double-Base Chains with Applications to Elliptic Curve Cryptography |  |  | read |
| KN-LIT-5465 | On the Equivalence of RSA and Factoring regarding Generic Ring Algorithms |  |  | read |
| KN-LIT-5466 | On the Exact Round Complexity of Secure Three-Party Computation |  |  | read |
| KN-LIT-5467 | On the Exact Security of Schnorr-Type Signatures in the Random Oracle Model |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5468 | On the Existence of Three Round Zero-Knowledge Proofs |  |  | read |
| KN-LIT-5469 | On the Feasibility of Consistent Computations |  |  | read |
| KN-LIT-5470 | On the Feasibility of Extending Oblivious Transfer |  |  | read |
| KN-LIT-5471 | On the Feasibility of Unclonable Encryption, and More |  |  | read |
| KN-LIT-5472 | On the Field-Based Division Property: |  |  | read |
| KN-LIT-5473 | On the Function Field Sieve and the Impact of Higher Splitting Probabilities |  |  | read |
| KN-LIT-5474 | On the Generalized Linear Equivalence of Functions over Finite Fields |  |  | read |
| KN-LIT-5475 | On the Generic and Efficient Constructions of Secure Designated Confirmer Signatures |  |  | read |
| KN-LIT-5476 | On the Generic Construction of Identity-Based Signatures with Additional Properties |  |  | read |
| KN-LIT-5477 | On the Generic Insecurity of the Full Domain Hash |  |  | read |
| KN-LIT-5478 | On the Gold Standard for Security of Universal Steganography |  |  | read |
| KN-LIT-5479 | On the Hardness of Information-Theoretic Multiparty Computation? |  |  | read |
| KN-LIT-5480 | On the Hardness of Learning with Rounding over Small Modulus ? |  |  | read |
| KN-LIT-5481 | On the Hardness of Proving CCA-Security of Signed ElGamal 1 |  |  | read |
| KN-LIT-5482 | On the Hardness of the Computational |  |  | read |
| KN-LIT-5483 | On the hardness of the NTRU problem |  |  | read |
| KN-LIT-5484 | On the higher order nonlinearities of algebraic immune functions Claude Carlet |  |  | read |
| KN-LIT-5485 | On the ideal shortest vector problem over random rational primes |  |  | read |
| KN-LIT-5486 | On the Impact of Known-Key Attacks on Hash Functions |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5487 | On the Implausibility of Differing-Inputs Obfuscation and Extractable Witness Encryption with Auxiliary Input |  |  | read |
| KN-LIT-5488 | On the Implementation of a Fast Prime Generation Algorithm |  |  | read |
| KN-LIT-5489 | On the Implementation of Unified Arithmetic on Binary Huff Curves |  |  | read |
| KN-LIT-5490 | On the Impossibilities of Basing One-Way Permutations on Central Cryptographic Primitives |  |  | read |
| KN-LIT-5491 | On the Impossibility of |  |  | read |
| KN-LIT-5492 | On the Impossibility of Algebraic NIZK |  |  | read |
| KN-LIT-5493 | On the Impossibility of Algebraic Vector |  |  | read |
| KN-LIT-5494 | On the Impossibility of Basing Public-Coin One-Way Permutations on Trapdoor Permutations |  |  | read |
| KN-LIT-5495 | On the Impossibility of Constructing Efficient |  |  | read |
| KN-LIT-5496 | On the Impossibility of Efficiently Combining Collision Resistant Hash Functions |  |  | read |
| KN-LIT-5497 | On the Impossibility of Highly-Efficient Blockcipher-Based Hash Functions |  |  | read |
| KN-LIT-5498 | On the Impossibility of Instantiating PSS in the Standard Model |  |  | read |
| KN-LIT-5499 | On the Impossibility of Key Agreements from Quantum Random Oracles |  |  | read |
| KN-LIT-5500 | On the Impossibility of Purely Algebraic Signatures |  |  | read |
| KN-LIT-5501 | On the Impossibility of Structure-Preserving Deterministic Primitives |  |  | read |
| KN-LIT-5502 | On the Impossibility of Three-Move Blind Signature Schemes |  |  | read |
| KN-LIT-5503 | On the Impossibility of Tight Cryptographic Reductions |  |  | read |
| KN-LIT-5504 | On the Impossibility of Virtual Black-Box Obfuscation in Idealized Models |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5505 | On the Indifferentiability of Key-Alternating Ciphers |  |  | read |
| KN-LIT-5506 | On the Indifferentiability of the Sponge Construction |  |  | read |
| KN-LIT-5507 | On the Insecurity of a Server-Aided RSA Protocol |  |  | read |
| KN-LIT-5508 | On The Insider Security of MLS |  |  | read |
| KN-LIT-5509 | On the Instantiability of Hash-and-Sign RSA Signatures |  |  | read |
| KN-LIT-5510 | On the Integer Polynomial Learning with Errors Problem |  |  | read |
| KN-LIT-5511 | On the Joint Security of Encryption and Signature, Revisited |  |  | read |
| KN-LIT-5512 | On the Key Dependent Message Security of the Fujisaki-Okamoto Constructions |  |  | read |
| KN-LIT-5513 | On the Lattice Isomorphism Problem, Quadratic Forms, Remarkable Lattices, and Cryptography |  |  | read |
| KN-LIT-5514 | On the Limitations of the Spread of an IBE-to-PKE Transformation |  |  | read |
| KN-LIT-5515 | On the Limitations of Universally Composable |  |  | read |
| KN-LIT-5516 | On the Local Leakage Resilience of Linear Secret Sharing Schemes |  |  | read |
| KN-LIT-5517 | On the looseness of FO derandomization |  |  | read |
| KN-LIT-5518 | On the Lossiness of the Rabin Trapdoor Function |  |  | read |
| KN-LIT-5519 | On the Memory-Tightness of Hashed ElGamal |  |  | read |
| KN-LIT-5520 | On the Message Complexity of Secure Multiparty Computation |  |  | read |
| KN-LIT-5521 | On the Minimum Number of Multiplications Necessary for Universal Hash Functions |  |  | read |
| KN-LIT-5522 | On the Multi-User Security of LWE-based NIKE |  |  | read |
| KN-LIT-5523 | On the Multi-User Security of Short Schnorr Signatures with Preprocessing |  |  | read |
| KN-LIT-5524 | On the Multiplicative Complexity of Boolean |  |  | read |
| KN-LIT-5525 | On the Non-Existence of Short Vectors in Random Module Lattices |  |  | read |
| KN-LIT-5526 | On the non-tightness of measurement-based reductions for key encapsulation mechanism in the quantum random oracle model ? |  |  | read |
| KN-LIT-5527 | On the Optimal Parameter Choice for Elliptic Curve Cryptosystems Using Isogeny |  |  | read |
| KN-LIT-5528 | On the Optimal Succinctness and Efficiency of Functional Encryption and Attribute-Based Encryption |  |  | read |
| KN-LIT-5529 | On the Optimality of Linear, Differential and Sequential Distinguishers |  |  | read |
| KN-LIT-5530 | On the Optimization of Side-Channel Attacks by Advanced Stochastic Methods |  |  | read |
| KN-LIT-5531 | On the Plausibility of Fully Homomorphic Encryption for RAMs |  |  | read |
| KN-LIT-5532 | On the Portability of Generalized Schnorr Proofs |  |  | read |
| KN-LIT-5533 | On the Possibility of a |  |  | read |
| KN-LIT-5534 | On the Possibility of Basing Cryptography on EXP 6= BPP |  |  | read |
| KN-LIT-5535 | On the Power of Amortization in Secret Sharing: |  |  | read |
| KN-LIT-5536 | On the Power of an Honest Majority in Three-Party Computation Without Broadcast |  |  | read |
| KN-LIT-5537 | On the Power of Bitsli e Implementation on Intel Core2 Pro essor |  |  | read |
| KN-LIT-5538 | On the Power of Correlated Randomness in Secure Computation |  |  | read |
| KN-LIT-5539 | On the Power of Expansion: More Efficient Constructions in the Random Probing Model |  |  | read |
| KN-LIT-5540 | On the Power of Fault Sensitivity Analysis and Collision |  |  | read |
| KN-LIT-5541 | On the Power of Hierarchical Identity-Based Encryption |  |  | read |
| KN-LIT-5542 | On the Power of Multiple Anonymous Messages: Frequency Estimation and Selection in the Shuffle Model of Differential Privacy |  |  | read |
| KN-LIT-5543 | On the Power of Power Analysis in the Real World: A Complete |  |  | read |
| KN-LIT-5544 | On the Power of Secure Two-Party Computation |  | Journal of Cryptology | read |
| KN-LIT-5545 | On the Power of the Randomized Iterate |  |  | read |
| KN-LIT-5546 | On the Practical Exploitability of Dual EC in TLS Implementations |  |  | read |
| KN-LIT-5547 | On the Practical Security of Inner Product |  |  | read |
| KN-LIT-5548 | On the Price of Concurrency in Group Ratcheting Protocols? |  |  | read |
| KN-LIT-5549 | On the Provable Security of an Efficient RSA-Based Pseudorandom Generator |  |  | read |
| KN-LIT-5550 | On the Provable Security of the Iterated Even-Mansour Cipher against Related-Key and Chosen-Key Attacks |  |  | read |
| KN-LIT-5551 | On the Public Indifferentiability and Correlation Intractability of the 6-Round Feistel Construction |  |  | read |
| KN-LIT-5552 | On the Quantum Complexity of the Continuous Hidden Subgroup Problem ? |  |  | read |
| KN-LIT-5553 | On the Regularity of Lossy RSA |  |  | read |
| KN-LIT-5554 | On the Relation Between the Ideal Cipher and the Random Oracle Models |  |  | read |
| KN-LIT-5555 | On the Relationship between Statistical |  |  | read |
| KN-LIT-5556 | On the Ring-LWE and Polynomial-LWE Problems |  |  | read |
| KN-LIT-5557 | On the Round Complexity of Black-Box Secure MPC |  |  | read |
| KN-LIT-5558 | On the Round Complexity of Fully Secure Solitary MPC with Honest Majority |  |  | read |
| KN-LIT-5559 | On the Round Complexity of OT Extension |  |  | read |
| KN-LIT-5560 | On The Round Complexity of Secure Quantum Computation |  |  | read |
| KN-LIT-5561 | On the Round Complexity of the Shuffle Model |  |  | read |
| KN-LIT-5562 | On the Salsa20 Core Function |  |  | read |
| KN-LIT-5563 | On the Security Loss in Cryptographic Reductions? |  |  | read |
| KN-LIT-5564 | On the Security Loss of Unique Signatures |  |  | read |
| KN-LIT-5565 | On the Security of a Bidirectional Proxy Re-Encryption Scheme from PKC 2010 |  |  | read |
| KN-LIT-5566 | On the Security of CAMELLIA against the Square Attack |  |  | read |
| KN-LIT-5567 | On the Security of Classic Protocols for Unique |  |  | read |
| KN-LIT-5568 | On the Security of Cryptosystems with Quadratic Decryption: The Nicest Cryptanalysis |  |  | read |
| KN-LIT-5569 | On the Security of Dynamic Group Signatures: Preventing Signature Hijacking Yusuke Sakai1? , Jacob C. N. Schuldt2?? , Keita Emura3? ? ? |  |  | read |
| KN-LIT-5570 | On the Security of Hash Functions Employing Blockcipher Postprocessing |  |  | read |
| KN-LIT-5571 | On the Security of Homomorphic Encryption on Approximate Numbers? |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5572 | On the Security of IV Dependent Stream Ciphers |  |  | read |
| KN-LIT-5573 | On the Security of Joint Signature and Encryption |  |  | read |
| KN-LIT-5574 | On the Security of Keyed Hashing Based on Public Permutations |  |  | read |
| KN-LIT-5575 | On the Security of MOR Public Key Cryptosystem In-Sok Lee1? , Woo-Hwan Kim1? |  |  | read |
| KN-LIT-5576 | On the Security of Multiple Encryption or CCA-security+CCA-security=CCA-security? |  |  | read |
| KN-LIT-5577 | On the Security of OAEP |  |  | read |
| KN-LIT-5578 | On the Security of One-Witness Blind Signature Schemes |  |  | read |
| KN-LIT-5579 | On the security of OSIDH |  |  | read |
| KN-LIT-5580 | On the Security of Padding-Based Encryption Schemes – or – Why we cannot prove OAEP secure in the Standard |  |  | read |
| KN-LIT-5581 | On the Security of Randomized CBC–MAC Beyond the Birthday Paradox Limit A New Construction |  |  | read |
| KN-LIT-5582 | On the Security of RDSA |  |  | read |
| KN-LIT-5583 | On the Security of Rijndael-like Structures against |  |  | read |
| KN-LIT-5584 | On the Security of RSA Encryption in TLS |  |  | read |
| KN-LIT-5585 | On the Security of Supersingular Isogeny Cryptosystems |  |  | read |
| KN-LIT-5586 | On the Security of Tandem-DM |  |  | read |
| KN-LIT-5587 | On the Security of the Pre-Shared Key Ciphersuites of TLS |  |  | read |
| KN-LIT-5588 | On the Security of the TLS Protocol: A Systematic Analysis |  |  | read |
| KN-LIT-5589 | On the Security of the “Free-XOR” Technique? |  |  | read |
| KN-LIT-5590 | On the Security of Time-Lock Puzzles and Timed Commitments |  |  | read |
| KN-LIT-5591 | On the Security of TLS-DHE in the Standard Model |  |  | read |
| KN-LIT-5592 | On the Selective Opening Security of Practical Public-Key Encryption Schemes |  |  | read |
| KN-LIT-5593 | On the Semantic Security of Functional Encryption Schemes |  |  | read |
| KN-LIT-5594 | On the Shortness of Vectors to be found by the Ideal-SVP Quantum Algorithm |  |  | read |
| KN-LIT-5595 | On the Simplicity of Converting Leakages from Multivariate to Univariate – Case Study of a Glitch-Resistant Masking Scheme |  |  | read |
| KN-LIT-5596 | On the Size of Pairing-based Non-interactive Arguments |  |  | read |
| KN-LIT-5597 | On the Static Diffie-Hellman Problem on Elliptic Curves over Extension Fields |  |  | read |
| KN-LIT-5598 | On the Statistical Leak of the |  |  | read |
| KN-LIT-5599 | On the Streaming Indistinguishability of a |  |  | read |
| KN-LIT-55b31e | Knapsack-type cryptosystems and algebraic coding theory | 1986 | Problems of Control and Information Theory | false |
| KN-LIT-5600 | On the Structure of Unconditional UC Hybrid Protocols |  |  | read |
| KN-LIT-5601 | On the Success Probability of Solving Unique SVP via BKZ |  |  | read |
| KN-LIT-5602 | On the Unpredictability of Bits of the Elliptic Curve Diffie–Hellman Scheme |  |  | read |
| KN-LIT-5603 | On the Untapped Potential of Encoding Predicates by Arithmetic Circuits and Their Applications Shuichi Katsumata ? |  |  | read |
| KN-LIT-5604 | On the vanishing of twisted L-functions of elliptic curves over function fields |  |  | read |
| KN-LIT-5605 | On the Worst-Case Inefficiency of CGKA Alexander Bienstock1 , Yevgeniy Dodis1? , Sanjam Garg2?? , Garrison Grogan3 |  |  | read |
| KN-LIT-5606 | On the Wrong Key Randomisation and Key Equivalence Hypotheses in Matsui’s |  |  | read |
| KN-LIT-5607 | On Tight Quantum Security of HMAC and NMAC in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-5608 | On Tight Security Proofs for Schnorr Signatures |  |  | read |
| KN-LIT-5609 | On Tightly Secure Non-Interactive Key Exchange |  |  | read |
| KN-LIT-5610 | On Tightly Secure Primitives in the Multi-Instance Setting |  |  | read |
| KN-LIT-5611 | On Time-Lock Cryptographic Assumptions in Abelian Hidden-Order Groups? |  |  | read |
| KN-LIT-5612 | On Time-Space Lower Bounds for Finding Short Collisions in Sponge Hash Functions |  |  | read |
| KN-LIT-5613 | On Time-Space Tradeoffs for Bounded-Length |  |  | read |
| KN-LIT-5614 | On Unconditionally Secure Robust Distributed Key Distribution Centers |  |  | read |
| KN-LIT-5615 | On Valiant’s Conjecture Impossibility of Incrementally Verifiable Computation from Random Oracles |  |  | read |
| KN-LIT-5616 | On Virtual Grey Box Obfuscation for General Circuits Nir Bitansky1 ? |  |  | read |
| KN-LIT-5617 | On Weak Keys and Forgery Attacks against Polynomial-based MAC Schemes? |  |  | read |
| KN-LIT-5618 | On-Line Ciphers and the Hash-CBC Construction |  |  | read |
| KN-LIT-5619 | One-Hot Conversion: Towards Faster Table-based A2B Conversion |  |  | read |
| KN-LIT-5620 | One-Message Secure Reductions: On the Cost of Converting Correlations |  |  | read |
| KN-LIT-5621 | One-Message Zero Knowledge and Non-Malleable Commitments |  |  | read |
| KN-LIT-5622 | One-out-of-Many Proofs: |  |  | read |
| KN-LIT-5623 | One-out-of-Many Unclonable Cryptography: |  |  | read |
| KN-LIT-5624 | One-Pass HMQV and Asymmetric Key-Wrapping |  |  | read |
| KN-LIT-5625 | One-Round Key Exchange with Strong Security: |  |  | read |
| KN-LIT-5626 | One-Shot Fiat-Shamir-based NIZK Arguments of Composite Residuosity and Logarithmic-Size Ring Signatures in the Standard Model |  |  | read |
| KN-LIT-5627 | One-Shot Verifiable Encryption from Lattices |  |  | read |
| KN-LIT-5628 | One-Time Computable Self-Erasing Functions? |  |  | read |
| KN-LIT-5629 | One-Time Programs |  |  | read |
| KN-LIT-5630 | One-Time Programs from Commodity Hardware |  |  | read |
| KN-LIT-5631 | One-time Verifier-based Encrypted Key Exchange |  |  | read |
| KN-LIT-5632 | One-way Functions and the Hardness of (Probabilistic) Time-Bounded Kolmogorov Complexity w.r.t. Samplable Distributions |  |  | read |
| KN-LIT-5633 | One-Way Functions Imply Secure Computation in a Quantum World |  |  | read |
| KN-LIT-5634 | One-Way Permutations, Interactive Hashing and Statistically Hiding Commitments |  |  | read |
| KN-LIT-5635 | Onion ORAM: A Constant Bandwidth Blowup |  |  | read |
| KN-LIT-5636 | Online Authenticated-Encryption and its Nonce-Reuse Misuse-Resistance |  |  | read |
| KN-LIT-5637 | Online/Offline Attribute-Based Encryption |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5638 | Online/Offline OR Composition of Sigma Protocols |  |  | read |
| KN-LIT-5639 | OPAQUE: An Asymmetric PAKE Protocol Secure Against Pre-Computation Attacks |  |  | read |
| KN-LIT-5640 | OPEN IMAGE COMPUTATIONS FOR ELLIPTIC CURVES OVER NUMBER FIELDS |  |  | read |
| KN-LIT-5641 | OpenSSLNTRU: Faster post-quantum TLS key exchange |  |  | read |
| KN-LIT-5642 | Optically Enhanced Position-Locked |  |  | read |
| KN-LIT-5643 | Optimal Algebraic Manipulation Detection Codes in the Constant-Error Model |  |  | read |
| KN-LIT-5644 | Optimal Amplification of Noisy Leakages? |  |  | read |
| KN-LIT-5645 | Optimal Bounded-Collusion Secure Functional Encryption |  |  | read |
| KN-LIT-5646 | Optimal Broadcast Encryption and CP-ABE from Evasive Lattice Assumptions |  |  | read |
| KN-LIT-5647 | Optimal Broadcast Encryption from LWE and Pairings in the Standard Model |  |  | read |
| KN-LIT-5648 | Optimal Broadcast Encryption from Pairings and LWE |  |  | read |
| KN-LIT-5649 | Optimal Channel Security Against Fine-Grained State Compromise: The Safety of Messaging |  |  | read |
| KN-LIT-5650 | Optimal Collision Security in Double Block Length Hashing with Single Length Key |  |  | read |
| KN-LIT-5651 | Optimal Computational Split-state Non-malleable Codes |  |  | read |
| KN-LIT-5652 | Optimal Forgeries Against Polynomial-Based MACs and GCM |  |  | read |
| KN-LIT-5653 | Optimal Key Ranking Procedures in a Statistical Cryptanalysis |  |  | read |
| KN-LIT-5654 | Optimal Linear Multiparty Conditional Disclosure of Secrets Protocols? |  |  | read |
| KN-LIT-5655 | Optimal Merging in Quantum k-xor and k-sum Algorithms |  |  | read |
| KN-LIT-5656 | Optimal Randomness Extraction from a Diffie-Hellman Element |  |  | read |
| KN-LIT-5657 | Optimal Reductions between Oblivious Transfers using Interactive Hashing |  |  | read |
| KN-LIT-5658 | Optimal Reductions of Some Decisional Problems to the Rank Problem |  |  | read |
| KN-LIT-5659 | Optimal Security for Keyed Hash Functions: Avoiding Time-Space Tradeoffs for Finding Collisions |  |  | read |
| KN-LIT-5660 | Optimal Security Proofs for Full Domain Hash, Revisited |  |  | read |
| KN-LIT-5661 | Optimal Security Proofs for PSS and other |  |  | read |
| KN-LIT-5662 | Optimal Security Proofs for Signatures from Identification Schemes |  |  | read |
| KN-LIT-5663 | Optimal Security Reductions for Unique Signatures: |  |  | read |
| KN-LIT-5664 | Optimal Structure-Preserving Signatures in Asymmetric Bilinear Groups |  |  | read |
| KN-LIT-5665 | Optimal Tightness for Chain-Based Unique Signatures |  |  | read |
| KN-LIT-5666 | Optimal Verification of Operations on Dynamic Sets |  |  | read |
| KN-LIT-5667 | Optimal-Rate Non-Committing Encryption? |  |  | read |
| KN-LIT-5668 | Optimally Secure Block Ciphers from Ideal Primitives |  |  | read |
| KN-LIT-5669 | Optimally Secure Tweakable Blockciphers |  |  | read |
| KN-LIT-5670 | Optimising Linear Key Recovery Attacks with Affine Walsh Transform Pruning |  |  | read |
| KN-LIT-5671 | Optimistic Asynchronous Atomic Broadcast |  |  | read |
| KN-LIT-5672 | Optimistic Fair Exchange in a Multi-User Setting |  |  | read |
| KN-LIT-5673 | Optimistic Mixing for Exit-Polls Philippe Golle1 , Sheng Zhong2 , Dan Boneh1 |  |  | read |
| KN-LIT-5674 | Optimization failures in SHA-3 software |  |  | read |
| KN-LIT-5675 | Optimization of LPN Solving Algorithms |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5676 | Optimized Interpolation Attacks on LowMC |  |  | read |
| KN-LIT-5677 | Optimized Method for Computing Odd-Degree Isogenies on Edwards Curves |  |  | read |
| KN-LIT-5678 | Optimizing Authenticated Garbling for Faster Secure Two-Party Computation |  |  | read |
| KN-LIT-5679 | Optimizing double-base elliptic-curve single-scalar multiplication |  |  | read |
| KN-LIT-5680 | Optimizing Rectangle Attacks: A Unified and Generic Framework for Key Recovery |  |  | read |
| KN-LIT-5681 | Optimizing Robustness while Generating Shared Secret Safe Primes |  |  | read |
| KN-LIT-5682 | Optimizing S-box Implementations for Several Criteria using SAT Solvers |  |  | read |
| KN-LIT-5683 | OptORAMa: Optimal Oblivious RAM Gilad Asharov1 , Ilan Komargodski2 , Wei-Kai Lin3 |  |  | read |
| KN-LIT-5684 | Orbweaver: Succinct Linear Functional Commitments from Lattices |  |  | read |
| KN-LIT-5685 | Order-C Secure Multiparty Computation for Highly Repetitive Circuits |  |  | read |
| KN-LIT-5686 | Order-Preserving Encryption Secure Beyond One-Wayness |  |  | read |
| KN-LIT-5687 | Order-Preserving Symmetric Encryption |  |  | read |
| KN-LIT-5688 | Ordering elliptic curves by their conductors |  |  | read |
| KN-LIT-5689 | Orientations and the supersingular endomorphism ring problem Benjamin Wesolowski[0000−0003−1249−6077] |  |  | read |
| KN-LIT-5690 | Orion: Zero Knowledge Proof with Linear Prover Time |  |  | read |
| KN-LIT-5691 | OT-Combiners via Secure Computation |  |  | read |
| KN-LIT-5692 | Our Data, Ourselves: Privacy via Distributed Noise Generation |  |  | read |
| KN-LIT-5693 | Ouroboros Praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain |  |  | read |
| KN-LIT-5694 | Ouroboros: A Provably Secure Proof-of-Stake Blockchain Protocol |  |  | read |
| KN-LIT-5695 | Out of Oddity – New Cryptanalytic Techniques against Symmetric Primitives Optimized for Integrity Proof Systems |  |  | read |
| KN-LIT-5696 | Output Compression, MPC, and iO for Turing Machines |  |  | read |
| KN-LIT-5697 | Output-Compressing Randomized Encodings and Applications |  |  | read |
| KN-LIT-5698 | Outsider-Anonymous Broadcast Encryption with Sublinear Ciphertexts |  |  | read |
| KN-LIT-5699 | Overcoming Impossibility Results in Composable Security using Interval-Wise Guarantees |  |  | read |
| KN-LIT-5700 | Overcoming Weak Expectations |  |  | read |
| KN-LIT-5701 | Overdrive: Making SPDZ Great Again |  |  | read |
| KN-LIT-5702 | Overloading the Nonce: Rugged PRPs |  |  | read |
| KN-LIT-5703 | Overtaking VEST |  |  | read |
| KN-LIT-5704 | P-signatures and Noninteractive Anonymous Credentials |  |  | read |
| KN-LIT-5705 | PAC Privacy: Automatic Privacy Measurement and Control of Data Processing |  |  | read |
| KN-LIT-5706 | Packed Ciphertexts in LWE-based Homomorphic Encryption |  |  | read |
| KN-LIT-5707 | Packed Multiplication: How to Amortize the Cost of Side-channel Masking? |  |  | read |
| KN-LIT-5708 | Packing Messages and Optimizing Bootstrapping in GSW-FHE |  |  | read |
| KN-LIT-5709 | Padding Oracle Attacks on CBC-mode Encryption with |  |  | read |
| KN-LIT-5710 | Pairing-based Cryptography: |  |  | read |
| KN-LIT-5711 | PAKEs: New Framework, New Techniques and More Efficient Lattice-Based Constructions in the Standard Model |  |  | read |
| KN-LIT-5712 | Parallel and Concurrent Security of the |  |  | read |
| KN-LIT-5713 | Parallel Coin-Tossing and Constant-Round Secure Two-Party Computation |  |  | read |
| KN-LIT-5714 | Parallel Gauss Sieve Algorithm: Solving the SVP Challenge over a 128-Dimensional Ideal Lattice |  |  | read |
| KN-LIT-5715 | Parallel Hashing via List Recoverability |  |  | read |
| KN-LIT-5716 | Parallel Implementations of Masking |  |  | read |
| KN-LIT-5717 | Parallel Key-Insulated Public Key Encryption Without Random Oracles |  |  | read |
| KN-LIT-5718 | Parallel Multi-Party Computation from Linear Multi-Secret Sharing Schemes ? |  |  | read |
| KN-LIT-5719 | Parallel Repetition for Leakage Resilience Amplification Revisited |  |  | read |
| KN-LIT-5720 | Parallel Repetition of (k1 , . . . , kμ )-Special-Sound Multi-Round Interactive Proofs |  |  | read |
| KN-LIT-5721 | Parallel Repetition Theorems for Interactive Arguments? |  |  | read |
| KN-LIT-5722 | Parallelizable and |  |  | read |
| KN-LIT-5723 | Parallelizable Delegation from LWE |  |  | read |
| KN-LIT-5724 | Parallelizing Explicit Formula for Arithmetic in the Jacobian of Hyperelliptic Curves |  |  | read |
| KN-LIT-5725 | Parameter-Hiding Order-Revealing Encryption without Pairings Cong Peng1[0000−0002−9958−3255] , Rongmao Chen2B[0000−0002−5113−387X] |  |  | read |
| KN-LIT-5726 | ParTI – Towards Combined Hardware Countermeasures against Side-Channel and Fault-Injection Attacks |  |  | read |
| KN-LIT-5727 | Partial Fairness in Secure Two-Party Computation |  |  | read |
| KN-LIT-5728 | Partial Key Exposure |  |  | read |
| KN-LIT-5729 | Partial Key Exposure Attack on Short Secret Exponent CRT-RSA |  |  | read |
| KN-LIT-5730 | Partial Key Exposure Attacks on BIKE |  |  | read |
| KN-LIT-5731 | Partial-Collision Attack on the Round-Reduced Compression Function of Skein-256 |  |  | read |
| KN-LIT-5732 | Partitioning via Non-Linear Polynomial Functions: More Compact IBEs from |  |  | read |
| KN-LIT-5733 | Password Hashing and Preprocessing |  |  | read |
| KN-LIT-5734 | Password Interception in a SSL/TLS Channel |  |  | read |
| KN-LIT-5735 | Password-Authenticated |  |  | read |
| KN-LIT-5736 | Password-Authenticated Session-Key Generation on the Internet in the Plain Model |  |  | read |
| KN-LIT-5737 | Password-Authenticated TLS via OPAQUE and Post-Handshake Authentication |  |  | read |
| KN-LIT-5738 | Password-based Authenticated Key Exchange David Pointcheval |  |  | read |
| KN-LIT-5739 | Password-Based Authenticated Key Exchange in the Three-Party Setting |  |  | read |
| KN-LIT-5740 | Password-based Group Key Exchange in a Constant Number of Rounds |  |  | read |
| KN-LIT-5741 | Patchable Indistinguishability Obfuscation: iO for Evolving Software? |  |  | read |
| KN-LIT-5742 | Path Swapping Method to Improve DPA resistance of Quasi Delay Insensitive Asynchronous circuits |  |  | read |
| KN-LIT-5743 | Pattern Matching in Encrypted Stream from Inner Product Encryption |  |  | read |
| KN-LIT-5744 | Pattern Matching on Encrypted Streams |  |  | read |
| KN-LIT-5745 | Perfect Algebraic Immune Functions ? |  |  | read |
| KN-LIT-5746 | Perfect Block Ciphers With Small Blocks |  |  | read |
| KN-LIT-5747 | Perfect Hiding and Perfect Binding Universally Composable Commitment Schemes with Constant Expansion Factor |  |  | read |
| KN-LIT-5748 | Perfect MPC Over Layered Graphs 1 2 |  |  | read |
| KN-LIT-5749 | Perfect Non-Interactive Zero Knowledge for NP |  |  | read |
| KN-LIT-5750 | Perfect Structure on the Edge of Chaos Trapdoor Permutations from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-5751 | Perfectly Secure Message Transmission Revisited |  |  | read |
| KN-LIT-5752 | Perfectly Secure Multiparty Computation and the Computational Overhead of Cryptography |  |  | read |
| KN-LIT-5753 | Perfectly Secure Oblivious Parallel RAM? |  |  | read |
| KN-LIT-5754 | Perfectly Secure Oblivious RAM with Sublinear Bandwidth Overhead |  |  | read |
| KN-LIT-5755 | Perfectly Secure Oblivious RAM Without Random Oracles |  |  | read |
| KN-LIT-5756 | Perfectly Secure Password Protocols in the Bounded Retrieval Model |  |  | read |
| KN-LIT-5757 | Perfectly-Secure MPC with Linear Communication Complexity? |  |  | read |
| KN-LIT-5758 | Performance Analysis and Parallel Implementation of Dedicated Hash Functions |  |  | read |
| KN-LIT-5759 | Performance Analysis of the SHA-3 Candidates on Exotic Multi-Core Architectures |  |  | read |
| KN-LIT-5760 | Permissionless Clock Synchronization with Public Setup |  |  | read |
| KN-LIT-5761 | Permuted Puzzles and Cryptographic Hardness |  |  | read |
| KN-LIT-5762 | Perturbating RSA Public Keys: an Improved Attack |  |  | read |
| KN-LIT-5763 | Physical Layer Group Key Agreement for Automotive Controller Area Networks |  |  | read |
| KN-LIT-5764 | Physical Zero-Knowledge Proofs of Physical Properties |  |  | read |
| KN-LIT-5765 | Physically Uncloneable Functions in the Universal Composition Framework |  |  | read |
| KN-LIT-5766 | PI-Cut-Choo and Friends: Compact Blind Signatures via Parallel Instance Cut-and-Choose and More |  |  | read |
| KN-LIT-5767 | Piccolo: An Ultra-Lightweight Blockcipher Kyoji Shibutani, Takanori Isobe, Harunaga Hiwatari, Atsushi Mitsuda |  |  | read |
| KN-LIT-5768 | Pinpointing the Side-Channel Leakage of Masked AES Hardware Implementations ? |  |  | read |
| KN-LIT-5769 | Pipelineable On-Line Encryption |  |  | read |
| KN-LIT-5770 | Pipelined Computation of Scalar Multiplication in Elliptic Curve Cryptosystems |  |  | read |
| KN-LIT-5771 | Pirate Evolution: How to make the most of your traitor keys |  |  | read |
| KN-LIT-5772 | Pitfalls and Shortcomings for Decompositions and Alignment |  |  | read |
| KN-LIT-5773 | Plain versus Randomized Cascading-Based Key-Length Extension for Block Ciphers Peter Gaži |  |  | read |
| KN-LIT-5774 | Plaintext Recovery Attacks Against WPA/TKIP? |  |  | read |
| KN-LIT-5775 | Plaintext-Dependent Decryption: A Formal Security Treatment of SSH-CTR |  |  | read |
| KN-LIT-5776 | Point Obfuscation and 3-round Zero-Knowledge? |  |  | read |
| KN-LIT-5777 | Point-Function Obfuscation: |  |  | read |
| KN-LIT-5778 | PointProofs, Revisited |  |  | read |
| KN-LIT-5779 | Policy-Based Signatures |  |  | read |
| KN-LIT-5780 | Policy-Compliant |  |  | read |
| KN-LIT-5781 | POLKA: Towards Leakage-Resistant PostQuantum CCA-Secure Public Key Encryption Clément |  |  | read |
| KN-LIT-5782 | Polling with Physical Envelopes: A Rigorous Analysis of a Human-Centric Protocol |  |  | read |
| KN-LIT-5783 | Polly Cracker, revisited, revisited Gottfried Herold? |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5784 | Polly Cracker, Revisited? |  |  | read |
| KN-LIT-5785 | Poly Onions: Achieving Anonymity in the Presence of Churn |  |  | read |
| KN-LIT-5786 | Poly-Many Hardcore Bits for Any One-Way Function and a Framework for Differing-Inputs Obfuscation |  |  | read |
| KN-LIT-5787 | Polylogarithmic Private Approximations and Efficient Matching |  |  | read |
| KN-LIT-5788 | Polynomial Equivalence Problems: Algorithmic and Theoretical Aspects |  |  | read |
| KN-LIT-5789 | Polynomial IOPs for Linear Algebra Relations |  |  | read |
| KN-LIT-5790 | Polynomial IOPs for Memory Consistency |  |  | read |
| KN-LIT-5791 | Polynomial Spaces: A New Framework for |  |  | read |
| KN-LIT-5792 | Polynomial Time Attack on Wild McEliece Over Quadratic Extensions |  |  | read |
| KN-LIT-5793 | Polynomial-Time Cryptanalysis of the Subspace Flooding Assumption for Post-Quantum iO |  |  | read |
| KN-LIT-5794 | Polytopic Cryptanalysis |  |  | read |
| KN-LIT-5795 | Populating the Zoo of Rugged Pseudorandom Permutations |  |  | read |
| KN-LIT-5796 | Position Based Cryptography? |  |  | read |
| KN-LIT-5797 | Position-Based Quantum Cryptography: |  |  | read |
| KN-LIT-5798 | Positive Results and Techniques for Obfuscation |  |  | read |
| KN-LIT-5799 | Possibility and Impossibility Results for |  |  | read |
| KN-LIT-5800 | Post-Quantum Anonymity of Kyber |  |  | read |
| KN-LIT-5801 | Post-Quantum Anonymous One-Sided Authenticated Key Exchange without Random Oracles |  |  | read |
| KN-LIT-5802 | Post-quantum Asynchronous Deniable Key Exchange and the Signal Handshake |  |  | read |
| KN-LIT-5803 | Post-quantum cryptography – dealing with the fallout of physics success |  |  | read |
| KN-LIT-5804 | Post-Quantum Insecurity from LWE |  |  | read |
| KN-LIT-5805 | Post-Quantum Multi-Party Computation |  |  | read |
| KN-LIT-5806 | Post-quantum RSA |  |  | read |
| KN-LIT-5807 | Post-Quantum Security of Fiat-Shamir |  |  | read |
| KN-LIT-5808 | Post-Quantum Security of Key Encapsulation Mechanism against CCA Attacks with a Single Decapsulation Query? |  |  | read |
| KN-LIT-5809 | Post-quantum Security of Plain OAEP Transform |  |  | read |
| KN-LIT-5810 | Post-Quantum Security of the Even-Mansour Cipher |  |  | read |
| KN-LIT-5811 | Post-Quantum Security of the Fujisaki-Okamoto and OAEP Transforms |  |  | read |
| KN-LIT-5812 | Post-Quantum Simulatable Extraction with Minimal Assumptions: Black-Box and Constant-Round |  |  | read |
| KN-LIT-5813 | Post-Quantum Verification of Fujisaki-Okamoto |  |  | read |
| KN-LIT-5814 | Post-Zeroizing Obfuscation: new mathematical tools, and the case of evasive circuits |  |  | read |
| KN-LIT-5815 | Potential Weaknesses of the Commutator Key Agreement Protocol based on Braid Groups |  |  | read |
| KN-LIT-5816 | PoW-Based Distributed Cryptography with no Trusted Setup? |  |  | read |
| KN-LIT-5817 | Power Analysis of an FPGA Implementation of Rijndael: Is Pipelining a DPA Countermeasure? |  |  | read |
| KN-LIT-5818 | Power and EM Attacks on Passive 13.56 MHz RFID Devices |  |  | read |
| KN-LIT-5819 | Power and Fault Analysis Resistance in Hardware through Dynamic Reconfiguration |  |  | read |
| KN-LIT-5820 | Power Attack on Small RSA Public Exponent Pierre-alain Fouque1 , Sébastien Kunz-Jacques1,2 , Gwenaëlle Martinet2 |  |  | read |
| KN-LIT-5821 | PPAD is as Hard as LWE and Iterated Squaring Nir Bitansky1 , Arka Rai Choudhuri2 , Justin Holmgren3 , Chethan Kamath1 |  |  | read |
| KN-LIT-5822 | PPAD-Hardness and Delegation with Unambiguous Proofs |  |  | read |
| KN-LIT-5824 | Practical Adaptive Oblivious Transfer from Simple Assumptions |  |  | read |
| KN-LIT-5825 | Practical and Employable Protocols for UC-Secure Circuit Evaluation over Zn ? |  |  | read |
| KN-LIT-5826 | Practical and Tightly-Secure Digital Signatures and Authenticated Key Exchange |  |  | read |
| KN-LIT-5827 | Practical attacks against the Walnut digital signature scheme |  |  | read |
| KN-LIT-5828 | Practical Bootstrapping in Quasilinear Time |  |  | read |
| KN-LIT-5829 | Practical Chosen Ciphertext Secure Encryption from Factoring |  |  | read |
| KN-LIT-5830 | Practical Collisions for EnRUPT |  |  | read |
| KN-LIT-5831 | Practical Construction and Analysis of Pseudo-randomness Primitives |  |  | read |
| KN-LIT-5832 | Practical Covert Authentication |  |  | read |
| KN-LIT-5833 | Practical Cryptanalysis of a Public-Key Encryption Scheme Based on |  |  | read |
| KN-LIT-5834 | Practical Cryptanalysis of ARMADILLO2 |  |  | read |
| KN-LIT-5835 | Practical Cryptanalysis of iso/iec 9796-2 and emv Signatures |  |  | read |
| KN-LIT-5836 | Practical Cryptanalysis of SFLASH |  |  | read |
| KN-LIT-5837 | Practical Cryptanalysis of the Identification Scheme Based on the Isomorphism of |  |  | read |
| KN-LIT-5838 | Practical Cryptanalysis of the Open Smart Grid Protocol |  |  | read |
| KN-LIT-5839 | Practical Electromagnetic Template Attack on HMAC |  |  | read |
| KN-LIT-5840 | Practical Exact Proofs from Lattices: New Techniques to Exploit Fully-Splitting Rings? |  |  | read |
| KN-LIT-5841 | Practical Free-Start Collision Attacks on 76-step |  |  | read |
| KN-LIT-5842 | Practical Fully Secure Unrestricted Inner Product Functional Encryption modulo p |  |  | read |
| KN-LIT-5843 | Practical Functional Encryption for Quadratic Functions with Applications to |  |  | read |
| KN-LIT-5844 | Practical Homomorphic MACs for Arithmetic Circuits |  |  | read |
| KN-LIT-5845 | Practical Identity-Based Encryption without Random Oracles |  |  | read |
| KN-LIT-5846 | Practical Key Recovery for Discrete-Logarithm Based Authentication Schemes from Random Nonce Bits |  |  | read |
| KN-LIT-5847 | Practical Key-recovery For All Possible Parameters of SFLASH |  |  | read |
| KN-LIT-5848 | Practical Large-scale Distributed Key Generation |  |  | read |
| KN-LIT-5849 | Practical Lattice-Based Cryptography: A Signature Scheme for Embedded Systems |  |  | read |
| KN-LIT-5850 | Practical Leakage-Resilient Symmetric Cryptography |  |  | read |
| KN-LIT-5851 | Practical Multilinear Maps over the Integers |  |  | read |
| KN-LIT-5852 | Practical Near-Collisions and Collisions on Round-Reduced ECHO-256 Compression Function |  |  | read |
| KN-LIT-5853 | Practical Non-interactive Publicly Verifiable Secret Sharing with Thousands of Parties |  |  | read |
| KN-LIT-5854 | Practical Post-Quantum Signature Schemes from Isomorphism Problems of Trilinear Forms |  |  | read |
| KN-LIT-5855 | Practical Product Proofs for Lattice Commitments? |  |  | read |
| KN-LIT-5856 | Practical Provably Secure Flooding for Blockchains |  |  | read |
| KN-LIT-5857 | Practical Round-Optimal Blind Signatures in the ROM from Standard Assumptions |  |  | read |
| KN-LIT-5858 | Practical Round-Optimal Blind Signatures in the Standard Model |  |  | read |
| KN-LIT-5859 | Practical Schnorr Threshold Signatures Without the Algebraic Group Model |  |  | read |
| KN-LIT-5860 | Practical Security Analysis of PUF-based Two-Player Protocols |  |  | read |
| KN-LIT-5861 | Practical Settlement Bounds for Longest-Chain Consensus |  |  | read |
| KN-LIT-5862 | Practical Signatures From Standard Assumptions Florian Böhl1 |  |  | read |
| KN-LIT-5863 | Practical Statistically-Sound Proofs of Exponentiation in any Group? Charlotte Hoffmann[0000−0003−2027−5549]1 , Pavel Hubáček[0000−0002−6850−6222]2 |  |  | read |
| KN-LIT-5864 | Practical Sublinear Proofs for R1CS from Lattices? |  |  | read |
| KN-LIT-5865 | Practical Symmetric On-line Encryption |  |  | read |
| KN-LIT-5866 | Practical Two-Party Computation based on the Conditional Gate |  |  | read |
| KN-LIT-5867 | Practical Verifiable Encryption and Decryption of Discrete Logarithms |  |  | read |
| KN-LIT-5868 | Practical, Predictable Lattice Basis Reduction ? |  |  | read |
| KN-LIT-5869 | Practical-Time Related-Key Attack on GOST with Secret S-boxes |  |  | read |
| KN-LIT-5870 | Practically Efficient Private Set Intersection From Trusted Hardware with Side-Channels |  |  | read |
| KN-LIT-5871 | Pre-Computation Scheme of Window τ NAF for Koblitz Curves Revisited |  |  | read |
| KN-LIT-5872 | Precise Concurrent Zero Knowledge |  |  | read |
| KN-LIT-5873 | precisely synchronized with the cryptographic computation. For example, wireless devices and smartcards often have no internal clock generator, or devices using PLLs will not have any external clock s |  |  | read |
| KN-LIT-5874 | Predicate Aggregate Signatures and Applications |  |  | read |
| KN-LIT-5875 | Predicate Encryption for Circuits from LWE |  |  | read |
| KN-LIT-5876 | Predicate Encryption for Multi-Dimensional Range Queries from Lattices |  |  | read |
| KN-LIT-5877 | Predicate Encryption from Bilinear Maps and One-Sided Probabilistic Rank |  |  | read |
| KN-LIT-5878 | Predicate Encryption Supporting Disjunctions |  |  | read |
| KN-LIT-5879 | Predictable Arguments of Knowledge |  |  | read |
| KN-LIT-5880 | Predicting Lattice Reduction |  |  | read |
| KN-LIT-5881 | Predicting performance for post-quantum encrypted-file systems |  |  | read |
| KN-LIT-5882 | Predictive Models for Min-Entropy Estimation |  |  | read |
| KN-LIT-5883 | Preimage and Collision Attacks on MD2 |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-5884 | Preimage Attacks on 3, 4, and 5-pass HAVAL |  |  | read |
| KN-LIT-5885 | Preimage Attacks on Reduced Tiger and SHA-2 |  |  | read |
| KN-LIT-5886 | Preimages for Reduced SHA-0 and SHA-1 |  |  | read |
| KN-LIT-5887 | PRESENT Runs Fast: |  |  | read |
| KN-LIT-5888 | PRESENT: An Ultra-Lightweight Block Cipher A. Bogdanov1, L.R. Knudsen2 , G. Leander1 , C. Paar1, A. Poschmann1 |  |  | read |
| KN-LIT-5889 | Preventing CLT Attacks on Obfuscation with Linear Overhead |  |  | read |
| KN-LIT-5890 | Preventing Pollution Attacks in Multi-Source Network Coding Shweta Agrawal 1? , Dan Boneh 2?? |  |  | read |
| KN-LIT-5891 | PRF-ODH: Relations, Instantiations, and Impossibility Results |  |  | read |
| KN-LIT-5892 | Primality Proving via One Round in ECPP and One Iteration in AKS |  |  | read |
| KN-LIT-5893 | Primary-Secondary-Resolver Membership Proof Systems |  |  | read |
| KN-LIT-5894 | PRINCE – A Low-latency Block Cipher for Pervasive Computing Applications ? |  |  | read |
| KN-LIT-5895 | PRINTcipher: A Block Cipher for IC-Printing |  |  | read |
| KN-LIT-5896 | Privacy Amplification in the Isolated Qubits Model Yi-Kai Liu |  |  | read |
| KN-LIT-5897 | Privacy with Imperfect Randomness |  |  | read |
| KN-LIT-5898 | Privacy-Enhancing Auctions Using Rational Cryptography |  |  | read |
| KN-LIT-5899 | Privacy-Enhancing Cryptography: From Theory |  |  | read |
| KN-LIT-5900 | Privacy-Free Garbled Circuits for Formulas: Size Zero and Information-Theoretic |  |  | read |
| KN-LIT-5901 | Privacy-Free Garbled Circuits with Applications To Efficient Zero-Knowledge? |  |  | read |
| KN-LIT-5902 | Privacy-Preserving |  |  | read |
| KN-LIT-5903 | Privacy-Preserving Authenticated Key Exchange in the Standard Model |  |  | read |
| KN-LIT-5904 | Privacy-Preserving Blueprints |  |  | read |
| KN-LIT-5905 | Privacy-Preserving Graph Algorithms in the Semi-Honest Model |  |  | read |
| KN-LIT-5906 | Privacy-Preserving Pattern Matching on Encrypted Data |  |  | read |
| KN-LIT-5907 | Private Aggregation from Fewer Anonymous Messages |  |  | read |
| KN-LIT-5908 | Private Anonymous Data Access |  |  | read |
| KN-LIT-5909 | Private Circuits II: Keeping Secrets in Tamperable Circuits |  |  | read |
| KN-LIT-5910 | Private Circuits with Quasilinear Randomness |  |  | read |
| KN-LIT-5911 | Private Circuits: A Modular Approach |  |  | read |
| KN-LIT-5912 | Private Circuits: Securing Hardware against Probing Attacks |  |  | read |
| KN-LIT-5913 | Private Coins versus Public Coins in Zero-Knowledge Proof Systems |  |  | read |
| KN-LIT-5914 | Private Multiplication over Finite Fields Sonia Belaïd1 , Fabrice Benhamouda2 , Alain Passelègue3 |  |  | read |
| KN-LIT-5915 | Private Mutual Authentication and Conditional Oblivious Transfer |  |  | read |
| KN-LIT-5916 | Private Polynomial Commitments and Applications to MPC |  |  | read |
| KN-LIT-5917 | Private Puncturable PRFs From Standard Lattice Assumptions |  |  | read |
| KN-LIT-5918 | Private Searching On Streaming Data? |  |  | read |
| KN-LIT-5919 | Private Set Intersection in the Internet Setting From Lightweight Oblivious PRF |  |  | read |
| KN-LIT-5920 | Private Set Operations from Multi-Query Reverse Private Membership Test |  |  | read |
| KN-LIT-5921 | Private Set Operations from Oblivious Switching? |  |  | read |
| KN-LIT-5922 | Privately Constraining and Programming PRFs, the LWE Way |  |  | read |
| KN-LIT-5923 | Privately Puncturing PRFs from Lattices: |  |  | read |
| KN-LIT-5924 | Probabilistic Slide Cryptanalysis and Its |  |  | read |
| KN-LIT-5925 | Probabilistic Termination and Composability of Cryptographic Protocols |  |  | read |
| KN-LIT-5926 | Probabilistically Checkable Proofs of Proximity with Zero-Knowledge |  |  | read |
| KN-LIT-5927 | Producing Collisions for Panama, Instantaneously |  |  | read |
| KN-LIT-5928 | Program Obfuscation with Leaky Hardware |  |  | read |
| KN-LIT-5929 | Programmable and Parallel ECC Coprocessor Architecture: Tradeoffs between Area, Speed and Security |  |  | read |
| KN-LIT-5930 | Programmable Distributed Point Functions |  |  | read |
| KN-LIT-5931 | Programmable Hash Functions and Their Applications |  |  | read |
| KN-LIT-5932 | Programmable Hash Functions from Lattices: Short Signatures and IBEs with Small Key Sizes |  |  | read |
| KN-LIT-5933 | Programmable Hash Functions go Private: |  |  | read |
| KN-LIT-5934 | Programming the Demirci-Selçuk Meet-in-the-Middle Attack with Constraints |  |  | read |
| KN-LIT-5935 | Progression-Free Sets and Sublinear Pairing-Based Non-Interactive Zero-Knowledge Arguments |  |  | read |
| KN-LIT-5936 | Projective Arithmetic Functional Encryption and Indistinguishability Obfuscation From Degree-5 Multilinear Maps? |  |  | read |
| KN-LIT-5937 | Projective Coordinates Leak |  |  | read |
| KN-LIT-5938 | Promise Zero Knowledge and its Applications to Round Optimal MPC |  |  | read |
| KN-LIT-5939 | Promise Σ-protocol: How to Construct Efficient Threshold ECDSA from Encryptions Based on Class Groups |  |  | read |
| KN-LIT-5940 | Proof of history: what is it good for? Victor Shoup |  |  | read |
| KN-LIT-5941 | Proof of Mirror Theory for a Wide Range of ξmax |  |  | read |
| KN-LIT-5942 | Proof of Space from Stacked Expanders |  |  | read |
| KN-LIT-5943 | Proof-Carrying Data From Arithmetized Random Oracles |  |  | read |
| KN-LIT-5944 | Proof-Carrying Data without Succinct Arguments ? |  |  | read |
| KN-LIT-5945 | Proof-of-Stake Protocols for Privacy-Aware Blockchains |  |  | read |
| KN-LIT-5946 | Proofs for Inner Pairing Products and Applications Benedikt Bünz1 |  |  | read |
| KN-LIT-5947 | Proofs of Replicated Storage Without Timing Assumptions? |  |  | read |
| KN-LIT-5948 | Proofs of Space |  |  | read |
| KN-LIT-5949 | Proofs of Storage from Homomorphic Identification Protocols |  |  | read |
| KN-LIT-5950 | Proofs of Work From Worst-Case Assumptions |  |  | read |
| KN-LIT-5951 | Property Preserving Symmetric Encryption |  |  | read |
| KN-LIT-5952 | Property Preserving Symmetric Encryption Revisited |  |  | read |
| KN-LIT-5953 | Property-Preserving Hash Functions for Hamming Distance from Standard Assumptions |  |  | read |
| KN-LIT-5954 | PrORAM Fast O(log n) Authenticated Shares ZK ORAM |  |  | read |
| KN-LIT-5955 | Protecting AES with Shamir’s Secret Sharing Scheme |  |  | read |
| KN-LIT-5956 | Protecting against Multidimensional Linear and Truncated Differential Cryptanalysis by Decorrelation |  |  | read |
| KN-LIT-5957 | Protecting Circuits from Leakage: the Computationally-Bounded and Noisy Cases Sebastian Faust1 ? |  |  | read |
| KN-LIT-5958 | Protecting Cryptographic Keys Against Continual Leakage |  |  | read |
| KN-LIT-5959 | Protecting Obfuscation Against Algebraic Attacks |  |  | read |
| KN-LIT-5960 | Protecting Transport Layer Security from Legacy Vulnerabilities |  |  | read |
| KN-LIT-5961 | Protocols for Multiparty Coin Toss With Dishonest Majority |  |  | read |
| KN-LIT-5962 | Protostar: Generic Efficient Accumulation/Folding for Special-sound Protocols |  |  | read |
| KN-LIT-5963 | Prototype IC with WDDL and Differential Routing – |  |  | read |
| KN-LIT-5964 | Prouff & Rivain’s Formal Security Proof of Masking, Revisited Tight Bounds in the Noisy Leakage Model |  |  | read |
| KN-LIT-5965 | Provable Security Evaluation of Structures against Impossible Differential and Zero Correlation Linear Cryptanalysis |  |  | read |
| KN-LIT-5966 | Provable Security of (Tweakable) Block Ciphers Based on Substitution-Permutation Networks |  |  | read |
| KN-LIT-5967 | Provable Security of KASUMI and 3GPP |  |  | read |
| KN-LIT-5968 | Provable Security of the Knudsen-Preneel Compression Functions |  |  | read |
| KN-LIT-5969 | Provable Time-Memory Trade-Offs: Symmetric Cryptography Against Memory-Bounded Adversaries |  |  | read |
| KN-LIT-5970 | Provably Authenticated Group Diffie-Hellman Key Exchange – The Dynamic Case |  |  | read |
| KN-LIT-5971 | Provably Robust Sponge-Based PRNGs and KDFs |  |  | read |
| KN-LIT-5972 | Provably Secure Fair Blind Signatures with Tight Revocation |  |  | read |
| KN-LIT-5973 | Provably Secure Higher-Order Masking of AES |  |  | read |
| KN-LIT-5974 | Provably Secure MACs From Differentially-uniform Permutations and AES-based Implementations |  |  | read |
| KN-LIT-5975 | Provably Secure NTRU Instances over Prime Cyclotomic Rings ? |  |  | read |
| KN-LIT-5976 | Provably Secure Reflection Ciphers |  |  | read |
| KN-LIT-5977 | Provably Secure S-Box Implementation Based on Fourier Transform |  |  | read |
| KN-LIT-5978 | Provably Secure Steganography |  |  | read |
| KN-LIT-5979 | Provably Secure Steganography with Imperfect Sampling |  |  | read |
| KN-LIT-5980 | Provably Secure Threshold Password-Authenticated Key Exchange? |  |  | read |
| KN-LIT-5981 | Provably Weak Instances of Ring-LWE |  |  | read |
| KN-LIT-5982 | Provably Weak Instances of Ring-LWE Revisited |  |  | read |
| KN-LIT-5983 | Proving Resistance against Invariant Attacks: How to Choose the Round Constants |  |  | read |
| KN-LIT-5984 | Proving the TLS Handshake Secure (as it is) |  |  | read |
| KN-LIT-5985 | Proving tight security for Rabin–Williams signatures |  |  | read |
| KN-LIT-5986 | Proxy Re-encryption from Lattices |  |  | read |
| KN-LIT-5987 | Proxy Signatures Secure Against Proxy Key Exposure |  |  | read |
| KN-LIT-5988 | Pseudo-cryptanalysis of the Original Blue |  |  | read |
| KN-LIT-5989 | Pseudoentropy: Lower-bounds for Chain rules and Transformations |  |  | read |
| KN-LIT-5990 | Pseudorandom (Function-Like) Quantum State Generators: |  |  | read |
| KN-LIT-5991 | Pseudorandom Correlation Functions from |  |  | read |
| KN-LIT-5992 | Pseudorandom Functions and Lattices |  |  | read |
| KN-LIT-5993 | Pseudorandom Functions in Almost Constant Depth from Low-Noise LPN |  |  | read |
| KN-LIT-5994 | Pseudorandom Generators from Regular One-way Functions: New Constructions with Improved Parameters |  |  | read |
| KN-LIT-5995 | Pseudorandom Knapsacks and the Sample Complexity of LWE Search-to-Decision Reductions? |  |  | read |
| KN-LIT-5996 | Pseudorandom permutation families over abelian groups |  |  | read |
| KN-LIT-5997 | Pseudorandom Quantum States |  |  | read |
| KN-LIT-5998 | Pseudorandomness from Braid Groups |  |  | read |
| KN-LIT-5999 | Pseudorandomness of Decoding, Revisited: Adapting OHCP to Code-Based Cryptography |  |  | read |
| KN-LIT-6000 | Pseudorandomness with Proof of Destruction and Applications |  |  | read |
| KN-LIT-6001 | PSI from PaXoS: |  |  | read |
| KN-LIT-6002 | PSS is Secure against Random Fault Attacks |  |  | read |
| KN-LIT-6003 | Public Key Authentication with one (on-line) Single Addition |  |  | read |
| KN-LIT-6004 | Public Key Compression and Modulus Switching for Fully Homomorphic Encryption over the Integers |  |  | read |
| KN-LIT-6005 | Public Key Encryption Against Related Key Attacks |  |  | read |
| KN-LIT-6006 | Public Key Encryption with Flexible Pattern Matching |  |  | read |
| KN-LIT-6007 | Public Key Encryption with Secure Key Leasing |  |  | read |
| KN-LIT-6008 | Public Key Perturbation of Randomized RSA Implementations |  |  | read |
| KN-LIT-6009 | Public Keys Arjen K. Lenstra1 , James P. Hughes2 , Maxime Augier1 , Joppe W. Bos1 |  |  | read |
| KN-LIT-6010 | Public Randomness Extraction with |  |  | read |
| KN-LIT-6011 | Public Verifiability in the Covert Model (Almost) for Free |  |  | read |
| KN-LIT-6012 | Public Verification of Private Effort? |  |  | read |
| KN-LIT-6013 | Public-Coin 3-Round Zero-Knowledge from Learning with Errors and Keyless Multi-Collision-Resistant Hash |  |  | read |
| KN-LIT-6014 | Public-Coin Concurrent Zero-Knowledge in the Global Hash Model? |  |  | read |
| KN-LIT-6015 | Public-Coin Differing-Inputs Obfuscation and Its Applications |  |  | read |
| KN-LIT-6016 | Public-Coin Statistical Zero-Knowledge Batch Verification against Malicious Verifiers? |  |  | read |
| KN-LIT-6017 | Public-Coin Zero-Knowledge Arguments with |  |  | read |
| KN-LIT-6018 | Public-Key Cryptographic Primitives Provably as Secure as Subset Sum |  |  | read |
| KN-LIT-6019 | Public-Key Cryptography from New Multivariate Quadratic Assumptions |  |  | read |
| KN-LIT-6020 | Public-Key Cryptography in the Fine-Grained Setting |  |  | read |
| KN-LIT-6021 | Public-Key Cryptosystems Resilient to Key Leakage ? |  |  | read |
| KN-LIT-6022 | Public-Key Encryption from Homogeneous CLWE Andrej Bogdanov ? , Miguel Cueto Noval ?? |  |  | read |
| KN-LIT-6023 | Public-Key Encryption in the Bounded-Retrieval Model |  |  | read |
| KN-LIT-6024 | Public-Key Encryption Indistinguishable Under Plaintext-Checkable Attacks |  |  | read |
| KN-LIT-6025 | Public-Key Encryption Resistant to Parameter Subversion and its Realization from Efficiently-Embeddable Groups |  |  | read |
| KN-LIT-6026 | Public-Key Encryption Schemes with Auxiliary Inputs |  |  | read |
| KN-LIT-6027 | Public-key Encryption with Keyword Search in Multi-user, Multi-challenge Setting under Adaptive Corruptions |  |  | read |
| KN-LIT-6028 | Public-Key Encryption with Quantum Keys Khashayar Barooti1 , Alex B. Grilo2 , Loïs Huguenin-Dumittan1 |  |  | read |
| KN-LIT-6029 | Public-Key Encryption, Local Pseudorandom Generators, and the Low-Degree Method |  |  | read |
| KN-LIT-6030 | Public-Key Function-Private Hidden Vector Encryption (and More) |  |  | read |
| KN-LIT-6031 | Public-Key Generation with Verifiable Randomness |  |  | read |
| KN-LIT-6032 | Public-Key Identification Schemes Based on Multivariate Cubic Polynomials |  |  | read |
| KN-LIT-6033 | Public-Key Identification Schemes Based on Multivariate Quadratic Polynomials |  |  | read |
| KN-LIT-6034 | Public-Key Locally-Decodable Codes |  |  | read |
| KN-LIT-6035 | Public-Key Puncturable Encryption: Modular and Compact Constructions |  |  | read |
| KN-LIT-6036 | Public-Key Steganography |  |  | read |
| KN-LIT-6037 | Public-Key Steganography with Active Attacks |  |  | read |
| KN-LIT-6038 | Public-Key Watermarking Schemes for Pseudorandom Functions |  |  | read |
| KN-LIT-6039 | Public-Seed Pseudorandom Permutations |  |  | read |
| KN-LIT-6040 | Publicly Verifiable Deletion from Minimal Assumptions |  |  | read |
| KN-LIT-6041 | Publicly Verifiable Proofs from Blockchains |  |  | read |
| KN-LIT-6042 | Publicly Verifiable Zero Knowledge from (Collapsing) Blockchains |  |  | read |
| KN-LIT-6043 | Publicly Verifiable Zero-Knowledge and |  |  | read |
| KN-LIT-6044 | Publicly-Verifiable Deletion via Target-Collapsing Functions |  |  | read |
| KN-LIT-6045 | PUFKY: A Fully Functional PUF-based Cryptographic Key Generator |  |  | read |
| KN-LIT-6046 | PUFs: Myth, Fact or Busted? A Security Evaluation of Physically Unclonable Functions (PUFs) |  |  | read |
| KN-LIT-6047 | Puncturable Key Wrapping and Its Applications |  | Journal of Cryptology | read |
| KN-LIT-6048 | Puncturable Pseudorandom Sets and Private Information Retrieval with Near-Optimal Online Bandwidth and Time? |  |  | read |
| KN-LIT-6049 | Purely Rational Secret Sharing |  |  | read |
| KN-LIT-6050 | Pushing the Limits of High-Speed GF (2m ) Elliptic Curve Scalar Multiplication on FPGAs |  |  | read |
| KN-LIT-6051 | Pushing the Limits of SHA-3 Hardware Implementations to Fit on RFID |  |  | read |
| KN-LIT-6052 | Pushing the Limits of Valiant's Universal Circuits: Simpler, Tighter and More Compact 1 1,2,3 |  |  | read |
| KN-LIT-6053 | Pushing the Limits: A Very |  |  | read |
| KN-LIT-6054 | QA-NIZK Arguments in Asymmetric Groups: |  |  | read |
| KN-LIT-6055 | QCB: Efficient Quantum-secure Authenticated Encryption Ritam Bhaumik1 , Xavier Bonnetain2 , André Chailloux1 , Gaëtan Leurent1 |  |  | read |
| KN-LIT-6056 | QcBits: Constant-Time Small-Key Code-Based Cryptography |  |  | read |
| KN-LIT-6057 | QCCA-Secure Generic Key Encapsulation Mechanism with Tighter Security in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-6058 | QCCA-Secure Generic Transformations in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-6059 | qDSA: Small and Secure Digital Signatures with Curve-based Diffie–Hellman Key Pairs |  |  | read |
| KN-LIT-6060 | QFactory: classically-instructed remote secret qubits preparation |  |  | read |
| KN-LIT-6061 | QUAD: a Practical Stream Cipher with Provable Security |  |  | read |
| KN-LIT-6062 | Quadratic Chabauty for elliptic curves over number fields |  |  | read |
| KN-LIT-6063 | Quadratic Multiparty Randomized Encodings |  |  | read |
| KN-LIT-6064 | Quadratic Secret Sharing and Conditional Disclosure of Secrets? |  |  | read |
| KN-LIT-6065 | Quadratic Span Programs and Succinct NIZKs without PCPs Rosario Gennaro? , Craig Gentry?? |  |  | read |
| KN-LIT-6066 | Quadratic Time, Linear Space Algorithms for |  |  | read |
| KN-LIT-6067 | Quantifying risks in cryptographic selection processes |  |  | read |
| KN-LIT-6068 | Quantifying the Security Cost of Migrating Protocols to Practice |  |  | read |
| KN-LIT-6069 | Quantitative Fault Injection Analysis |  |  | read |
| KN-LIT-6070 | Quantum Algorithms for the k-xor Problem |  |  | read |
| KN-LIT-6071 | Quantum algorithms for the subset-sum problem |  |  | read |
| KN-LIT-6072 | Quantum Algorithms for Variants of Average-Case Lattice Problems via Filtering |  |  | read |
| KN-LIT-6073 | Quantum Anonymous Transmissions |  |  | read |
| KN-LIT-6074 | Quantum attacks against Blue Midnight Wish, ECHO, Fugue, Grøstl, Hamsi, JH, Keccak, Shabal |  |  | read |
| KN-LIT-6075 | Quantum Attacks against Indistinguishablility Obfuscators Proved Secure in the Weak |  |  | read |
| KN-LIT-6076 | Quantum Attacks on Hash Constructions with Low Quantum Random Access Memory |  |  | read |
| KN-LIT-6077 | Quantum Attacks without Superposition Queries: the Offline Simon’s Algorithm |  |  | read |
| KN-LIT-6078 | Quantum Authentication and Encryption with Key Recycling Or: How to Re-use a One-Time Pad Even if P = NP — Safely & Feasibly |  |  | read |
| KN-LIT-6079 | Quantum CCA-Secure PKE, Revisited |  |  | read |
| KN-LIT-6080 | Quantum Circuit Implementations of AES with Fewer Qubits |  |  | read |
| KN-LIT-6081 | Quantum circuits for the CSIDH: optimizing quantum evaluation of isogenies |  |  | read |
| KN-LIT-6082 | Quantum Collision Attacks on |  |  | read |
| KN-LIT-6083 | Quantum Commitments and Signatures without One-Way Functions |  |  | read |
| KN-LIT-6084 | Quantum Computationally Predicate-Binding Commitments with Application in Quantum Zero-Knowledge Arguments for NP? |  |  | read |
| KN-LIT-6085 | Quantum cryptanalysis in the RAM model: Claw- nding attacks on SIKE |  |  | read |
| KN-LIT-6086 | Quantum encryption with certified deletion |  |  | read |
| KN-LIT-6087 | Quantum Encryption with Certified Deletion, Revisited: |  |  | read |
| KN-LIT-6088 | Quantum Fully Homomorphic Encryption With Verification |  |  | read |
| KN-LIT-6089 | Quantum homomorphic encryption for circuits of low T-gate complexity |  |  | read |
| KN-LIT-6090 | Quantum homomorphic encryption for polynomial-sized circuits |  |  | read |
| KN-LIT-6091 | Quantum Indistinguishability of Random Sponges |  |  | read |
| KN-LIT-6092 | Quantum Key-length Extension |  |  | read |
| KN-LIT-6093 | Quantum Lattice Enumeration and Tweaking Discrete Pruning |  |  | read |
| KN-LIT-6094 | Quantum Lightning Never Strikes the Same State Twice |  |  | read |
| KN-LIT-6095 | Quantum Linear Key-recovery Attacks Using the QFT André Schrottenloher[0000−0002−1329−8630] |  |  | read |
| KN-LIT-6096 | Quantum Linearization Attacks |  |  | read |
| KN-LIT-6097 | Quantum Multicollision-Finding Algorithm |  |  | read |
| KN-LIT-6098 | Quantum non-malleability and authentication |  |  | read |
| KN-LIT-6099 | Quantum one-time programs |  |  | read |
| KN-LIT-6100 | Quantum position verification in the random oracle model |  |  | read |
| KN-LIT-6101 | Quantum Proofs of Knowledge |  |  | read |
| KN-LIT-6102 | Quantum Random Oracle Model with Auxiliary Input |  |  | read |
| KN-LIT-6103 | Quantum Rewinding for Many-Round Protocols |  |  | read |
| KN-LIT-6104 | Quantum Security of NMAC and Related Constructions — PRF domain extension against quantum attacks |  |  | read |
| KN-LIT-6105 | Quantum security proofs using semi-classical oracles |  |  | read |
| KN-LIT-6106 | Quantum Speed-Up for Multidimensional (Zero Correlation) Linear Distinguishers |  |  | read |
| KN-LIT-6107 | Quantum-access-secure message authentication via blind-unforgeability |  |  | read |
| KN-LIT-6108 | Quantum-Secure Coin-Flipping and Applications |  |  | read |
| KN-LIT-6109 | Quantum-Secure Symmetric-Key Cryptography Based on Hidden Shifts |  |  | read |
| KN-LIT-6110 | Quark: a lightweight hash |  |  | read |
| KN-LIT-6111 | Quasi-Adaptive NIZK for Linear Subspaces Revisited |  |  | read |
| KN-LIT-6112 | Quasi-Linear Size Zero Knowledge from Linear-Algebraic PCPs |  |  | read |
| KN-LIT-6113 | QuasiModo: Efficient Certificate Validation and Revocation? |  |  | read |
| KN-LIT-6114 | Quisquis: A New Design for Anonymous Cryptocurrencies 1 |  |  | read |
| KN-LIT-6115 | R3PO: Reach-Restricted Reactive Program |  |  | read |
| KN-LIT-6116 | Radical Isogenies on Montgomery Curves |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6117 | Rai-Choo! Evolving Blind Signatures to the Next Level |  |  | read |
| KN-LIT-6118 | Ramp hyper-invertible matrices and their applications to MPC protocols |  |  | read |
| KN-LIT-6119 | Random Oracle Combiners: Breaking the Concatenation Barrier for Collision-Resistance |  |  | read |
| KN-LIT-6120 | Random Oracle Reducibility |  |  | read |
| KN-LIT-6121 | Random Oracles and Auxiliary Input |  |  | read |
| KN-LIT-6122 | Random Oracles and Non-Uniformity |  |  | read |
| KN-LIT-6123 | Random Oracles in a Quantum World Dan Boneh1 , Özgür Dagdelen2 , Marc Fischlin2 |  |  | read |
| KN-LIT-6124 | Random Oracles With(out) Programmability |  |  | read |
| KN-LIT-6125 | Random Probing Expansion: Quasi Linear Gadgets & Dynamic Compilers |  |  | read |
| KN-LIT-6126 | Random Probing Security: Verification |  |  | read |
| KN-LIT-6127 | Random Sampling for Short Lattice Vectors on Graphics Cards |  |  | read |
| KN-LIT-6128 | Random Sampling Revisited: Lattice Enumeration with Discrete Pruning |  |  | read |
| KN-LIT-6129 | Random Selection with an Adversarial Majority? |  |  | read |
| KN-LIT-6130 | Random Self-reducibility of Ideal-SVP via Arakelov Random Walks |  |  | read |
| KN-LIT-6131 | Random Subgroups of Braid Groups: An Approach to Cryptanalysis of a Braid Group based Cryptographic Protocol |  |  | read |
| KN-LIT-6132 | Random-Index Oblivious RAM |  |  | read |
| KN-LIT-6133 | Random-Index PIR and Applications |  |  | read |
| KN-LIT-6134 | Random-Oracle Uninstantiability from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-6135 | Randomizable Proofs and Delegatable Anonymous Credentials Mira Belenkiy1 , Jan Camenisch2 , Melissa Chase3 , Markulf Kohlweiss4 |  |  | read |
| KN-LIT-6136 | Randomized Half-Ideal Cipher on Groups with applications to UC (a)PAKE |  |  | read |
| KN-LIT-6137 | Randomness Complexity of |  |  | read |
| KN-LIT-6138 | Randomness Extraction via δ-Biased Masking in the Presence of a Quantum Attacker |  |  | read |
| KN-LIT-6139 | Randomness-Dependent Message Security |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6140 | Range Extension for Weak PRFs; The Good, the Bad, and the Ugly |  |  | read |
| KN-LIT-6141 | Rank of an elliptic curve and 3-rank of a quadratic field via the Burgess bounds |  |  | read |
| KN-LIT-6142 | Rankin’s Constant and Blockwise Lattice Reduction |  |  | read |
| KN-LIT-6143 | Rasta: A cipher with low ANDdepth and few ANDs per bit |  |  | read |
| KN-LIT-6144 | Ratcheted Encryption and Key Exchange: The Security of Messaging |  |  | read |
| KN-LIT-6145 | Rate-1 Fully Local Somewhere Extractable Hashing from DDH |  |  | read |
| KN-LIT-6146 | Rate-1 Incompressible Encryption from Standard Assumptions |  |  | read |
| KN-LIT-6147 | Rate-1 Key-Dependent Message Security via Reusable Homomorphic Extractor against Correlated-Source Attacks |  |  | read |
| KN-LIT-6148 | Rate-1 Quantum Fully Homomorphic Encryption |  |  | read |
| KN-LIT-6149 | Rate-1 Trapdoor Functions from the Diffie-Hellman Problem |  |  | read |
| KN-LIT-6150 | Rate-1, Linear Time and Additively Homomorphic UC Commitments |  |  | read |
| KN-LIT-6151 | Rate-Limited Secure Function Evaluation: Definitions and Constructions |  |  | read |
| KN-LIT-6152 | Rational isogenies from irrational endomorphisms |  |  | read |
| KN-LIT-6153 | Rational Modular Encoding in the DCR Setting: |  |  | read |
| KN-LIT-6154 | RATIONAL POINTS ON HYPERELLIPTIC ATKIN-LEHNER QUOTIENTS OF MODULAR CURVES AND THEIR COVERINGS |  |  | read |
| KN-LIT-6155 | Rational Sumchecks? |  |  | read |
| KN-LIT-6156 | Rationality in the Full-Information Model |  |  | read |
| KN-LIT-6157 | Re-encryption, functional re-encryption, and multi-hop re-encryption: A framework for achieving obfuscation-based security and instantiations from lattices |  |  | read |
| KN-LIT-6158 | Read-Proof Hardware from Protective Coatings Pim Tuyls, Geert-Jan Schrijen, Boris Škorić |  |  | read |
| KN-LIT-6159 | Real Time Cryptanalysis of Bluetooth Encryption with Condition Masking |  |  | read |
| KN-LIT-6160 | Realistic Failures in Secure Multi-Party Computation? |  |  | read |
| KN-LIT-6161 | Realizing Chosen Ciphertext Security |  |  | read |
| KN-LIT-6162 | Realizing Hash-and-Sign Signatures under Standard Assumptions |  |  | read |
| KN-LIT-6163 | Really fast syndrome-based hashing |  |  | read |
| KN-LIT-6164 | Rebound Attack on JH42 |  |  | read |
| KN-LIT-6165 | Rebound Attack on Reduced-Round Versions of JH |  |  | read |
| KN-LIT-6166 | Rebound Attack on the Full Lane Compression Function ? |  |  | read |
| KN-LIT-6167 | Rebound Distinguishers: Results on the Full |  |  | read |
| KN-LIT-6168 | Receipt-Free Universally-Verifiable Voting With Everlasting Privacy |  |  | read |
| KN-LIT-6169 | Receiver-Anonymity in Rerandomizable RCCA-Secure Cryptosystems Resolved |  |  | read |
| KN-LIT-6170 | Recent Advances and Existing Research |  |  | read |
| KN-LIT-6171 | Reconciling d + 1 Masking in Hardware and Software |  |  | read |
| KN-LIT-6172 | Reconfigurable Cryptography: A flexible approach to long-term security |  |  | read |
| KN-LIT-6173 | Reconsidering Generic Composition |  |  | read |
| KN-LIT-6174 | Reconstructing RSA Private Keys from Random Key Bits |  |  | read |
| KN-LIT-6175 | Recovering NTRU Secret Key From Inversion Oracles |  |  | read |
| KN-LIT-6176 | Recovering RSA Secret Keys from Noisy Key Bits with Erasures and Errors |  |  | read |
| KN-LIT-6177 | Recovering Secret Keys from Weak Side Channel Traces of Differing Lengths |  |  | read |
| KN-LIT-6178 | Recovering the tight security proof of SPHINCS+ |  |  | read |
| KN-LIT-6179 | Rectangle Attacks on 49-Round SHACAL-1? |  |  | read |
| KN-LIT-6180 | Recursive Diffusion Layers for |  |  | read |
| KN-LIT-6181 | Recursive Proof Composition from Accumulation Schemes |  |  | read |
| KN-LIT-6182 | Recyclable PUFs: |  |  | read |
| KN-LIT-6183 | Redeeming Reset Indifferentiability and Applications to Post-Quantum Security |  |  | read |
| KN-LIT-6184 | Reduce-by-Feedback: |  |  | read |
| KN-LIT-6185 | Reducing Complexity Assumptions for Statistically-Hiding Commitment Iftach Haitner1? , Omer Horvitz2?? , Jonathan Katz2? ? ? |  |  | read |
| KN-LIT-6186 | Reducing Depth in Constrained PRFs: From Bit-Fixing to NC1 ? |  |  | read |
| KN-LIT-6187 | Reducing the Key Size of McEliece Cryptosystem from Automorphism-induced Goppa Codes via Permutations |  |  | read |
| KN-LIT-6188 | Reducing the Number of Non-linear Multiplications in Masking Schemes |  |  | read |
| KN-LIT-6189 | Reducing Trust in the PKG in Identity Based Cryptosystems |  |  | read |
| KN-LIT-6190 | Reductions from module lattices to free module |  |  | read |
| KN-LIT-6191 | Refined Cryptanalysis of the GPRS Ciphers GEA-1 and GEA-2 |  |  | read |
| KN-LIT-6192 | Refinements of the k-tree Algorithm for the Generalized Birthday Problem |  |  | read |
| KN-LIT-6193 | Reflection Cryptanalysis of PRINCE-like Ciphers Hadi Soleimany1 , Céline Blondeau1 , Xiaoli Yu2,3 , Wenling Wu2 |  |  | read |
| KN-LIT-6194 | Registered (Inner-Product) Functional Encryption Danilo Francati1[0000−0002−4639−0636] , Daniele Friolo2[0000−0003−0836−1735] |  |  | read |
| KN-LIT-6195 | Registered ABE via Predicate Encodings |  |  | read |
| KN-LIT-6196 | Registered Attribute-Based Encryption |  |  | read |
| KN-LIT-6197 | Registered Attribute-Based Signature |  |  | read |
| KN-LIT-6198 | Registration-Based Encryption from Standard Assumptions Sanjam Garg? , Mohammad Hajiabadi?? , Mohammad Mahmoody? ? ? |  |  | read |
| KN-LIT-6199 | Registration-Based Encryption: Removing Private-Key Generator from IBE |  |  | read |
| KN-LIT-6200 | Regularity of Lossy RSA on Subdomains and its Applications Mark Lewko1 |  |  | read |
| KN-LIT-6201 | Related Randomness Attacks for Public Key Encryption |  |  | read |
| KN-LIT-6202 | Related Randomness Security for Public Key Encryption, Revisited |  |  | read |
| KN-LIT-6203 | Related-key Attacks Against Full Hummingbird-2 |  |  | read |
| KN-LIT-6204 | Related-key Cryptanalysis of the Full AES-192 and AES-256 |  |  | read |
| KN-LIT-6205 | Related-Key Forgeries for Prøst-OTR |  |  | read |
| KN-LIT-6206 | Related-Key Rectangle Attacks on Reduced |  |  | read |
| KN-LIT-6207 | Related-Key Security for Pseudorandom |  |  | read |
| KN-LIT-6208 | Relational Hash: Probabilistic Hash for Verifying Relations, Secure against Forgery and More |  |  | read |
| KN-LIT-6209 | Relations between Constrained and Bounded Chosen Ciphertext Security for Key Encapsulation Mechanisms |  |  | read |
| KN-LIT-6210 | Relationships between quantum IND-CPA notions 1 |  |  | read |
| KN-LIT-6211 | Relatively-Sound NIZKs and Password-Based Key-Exchange ? |  |  | read |
| KN-LIT-6212 | Relativistic (or 2-prover 1-round) zero-knowledge protocol for NP secure against quantum adversaries |  |  | read |
| KN-LIT-6213 | Relaxing Chosen-Ciphertext Security |  |  | read |
| KN-LIT-6214 | Relaxing Environmental Security: Monitored |  |  | read |
| KN-LIT-6215 | Relaxing Full-Codebook Security: A Refined Analysis of Key-Length Extension Schemes |  |  | read |
| KN-LIT-6216 | Removing Erasures with Explainable Hash Proof Systems |  |  | read |
| KN-LIT-6217 | Removing Escrow from Identity-Based Encryption |  |  | read |
| KN-LIT-6218 | Replacing a Random Oracle: Full Domain Hash From Indistinguishability Obfuscation |  |  | read |
| KN-LIT-6219 | Report on evaluation of KpqC Round-2 candidates |  |  | read |
| KN-LIT-6220 | Reproducible Circularly-Secure Bit Encryption: Applications and Realizations |  |  | read |
| KN-LIT-6221 | Research Status of the ECDLP |  |  | read |
| KN-LIT-6222 | Reset Indifferentiability and its Consequences |  |  | read |
| KN-LIT-6223 | Resettable Cryptography in Constant Rounds – the Case of Zero Knowledge |  |  | read |
| KN-LIT-6224 | Resettable Statistical Zero Knowledge |  |  | read |
| KN-LIT-6225 | Resettable Zero-Knowledge in the Weak Public-Key Model |  |  | read |
| KN-LIT-6226 | Resettably Secure Computation |  |  | read |
| KN-LIT-6227 | Resettably Sound Zero-Knowledge Arguments from OWFs - the (semi) Black-Box way |  |  | read |
| KN-LIT-6228 | Resistance Against Iterated Attacks by Decorrelation Revisited |  |  | read |
| KN-LIT-6229 | Resistance of Randomized Projective Coordinates Against Power Analysis |  |  | read |
| KN-LIT-6230 | Resistance of S-boxes against Algebraic Attacks |  |  | read |
| KN-LIT-6231 | Resisting Randomness Subversion: Fast |  |  | read |
| KN-LIT-6232 | ReSolveD: Shorter Signatures from Regular Syndrome Decoding and VOLE-in-the-Head |  |  | read |
| KN-LIT-6233 | Resource Fairness and Composability of Cryptographic Protocols |  |  | read |
| KN-LIT-6234 | Resource-Restricted Cryptography: Revisiting MPC Bounds in the Proof-of-Work Era 1 |  |  | read |
| KN-LIT-6235 | Resource-Restricted Indifferentiability |  |  | read |
| KN-LIT-6236 | Responsive Round Complexity and Concurrent Zero-Knowledge |  |  | read |
| KN-LIT-6237 | Results on Rotation Symmetric Bent and Correlation Immune Boolean Functions |  |  | read |
| KN-LIT-6238 | Resynchronization Attacks on WG and LEX ? |  |  | read |
| KN-LIT-6239 | Return of GGH15: Provable Security Against Zeroizing Attacks? |  |  | read |
| KN-LIT-6240 | Reusable Designated-Verifier NIZKs for all NP from CDH |  |  | read |
| KN-LIT-6241 | Reusable Fuzzy Extractors for Low-Entropy Distributions Ran Canetti1,2 , Benjamin Fuller1,3 , Omer Paneth1 |  |  | read |
| KN-LIT-6242 | Reusable Non-Interactive Secure Computation |  |  | read |
| KN-LIT-6243 | Reusable Secure Computation in the Plain Model |  |  | read |
| KN-LIT-6244 | Reusable Two-Round MPC from DDH |  |  | read |
| KN-LIT-6245 | Reusable Two-Round MPC from LPN |  |  | read |
| KN-LIT-6246 | Reusing Tamper-Proof Hardware in UC-Secure Protocols |  |  | read |
| KN-LIT-6247 | Revamped Differential-Linear Cryptanalysis on Reduced Round ChaCha |  |  | read |
| KN-LIT-6248 | Reverse Cycle Walking and Its Applications |  |  | read |
| KN-LIT-6249 | Reverse Firewalls for Actively Secure MPCs |  |  | read |
| KN-LIT-6250 | Reverse Firewalls for Adaptively Secure MPC without Setup |  |  | read |
| KN-LIT-6251 | Reverse Firewalls for Oblivious Transfer |  |  | read |
| KN-LIT-6252 | Reverse-engineering of the cryptanalytic attack used in the Flame super-malware |  |  | read |
| KN-LIT-6253 | Reverse-Engineering the S-Box of Streebog |  |  | read |
| KN-LIT-6254 | Reversible Proofs of Sequential Work |  |  | read |
| KN-LIT-6255 | Revisiting AES-GCM-SIV: Multi-user Security |  |  | read |
| KN-LIT-6256 | Revisiting BBS Signatures |  |  | read |
| KN-LIT-6257 | Revisiting cycles of pairing-friendly elliptic curves |  |  | read |
| KN-LIT-6258 | Revisiting Fairness in MPC: Polynomial Number of Parties and General Adversarial Structures |  |  | read |
| KN-LIT-6259 | Revisiting Higher-Order Differential-Linear Attacks from an Algebraic Perspective ? |  |  | read |
| KN-LIT-6260 | Revisiting Lower and Upper Bounds for Selective Decommitments |  |  | read |
| KN-LIT-6261 | Revisiting Non-Malleable Secret Sharing |  |  | read |
| KN-LIT-6262 | Revisiting Post-Quantum Fiat-Shamir |  |  | read |
| KN-LIT-6263 | Revisiting Proxy Re-Encryption: Forward |  |  | read |
| KN-LIT-6264 | Revisiting Security Estimation for LWE with Hints from a Geometric Perspective Dana Dachman-Soled1 |  |  | read |
| KN-LIT-6265 | Revisiting the Constant-sum Winternitz One-time Signature with Applications to SPHINCS+ and XMSS |  |  | read |
| KN-LIT-6266 | Revisiting the Cryptographic Hardness of Finding a Nash Equilibrium |  |  | read |
| KN-LIT-6267 | Revisiting the Efficiency of Malicious Two-Party Computation |  |  | read |
| KN-LIT-6268 | Revisiting the Gentry-Szydlo Algorithm |  |  | read |
| KN-LIT-6269 | Revisiting the IDEA Philosophy |  |  | read |
| KN-LIT-6270 | Revisiting the Indifferentiability of the Sum of Permutations |  |  | read |
| KN-LIT-6271 | Revisiting the Security of DbHtS MACs: Beyond-Birthday-Bound in the Multi-User Setting |  |  | read |
| KN-LIT-6272 | Revo able quantum timed-release en ryption |  |  | read |
| KN-LIT-6273 | Revocable Group Signature Schemes with Constant Costs for Signing and Verifying |  |  | read |
| KN-LIT-6274 | Revocable Identity-Based Encryption Revisited: |  |  | read |
| KN-LIT-6275 | Revocation for Delegatable Anonymous Credentials |  |  | read |
| KN-LIT-6276 | Rewriting Variables: the Complexity of Fast Algebraic Attacks on Stream Ciphers |  |  | read |
| KN-LIT-6277 | RFID and its Vulnerability to Faults |  |  | read |
| KN-LIT-6278 | RFID Noisy Reader How to Prevent from Eavesdropping on the Communication? |  |  | read |
| KN-LIT-6279 | Richer Efficiency/Security Trade-offs in 2PC |  |  | read |
| KN-LIT-6280 | Riding on Asymmetry: Efficient ABE for Branching Programs |  |  | read |
| KN-LIT-6281 | Right-Invariance: A Property for Probabilistic Analysis of Cryptography based on Infinite Groups |  |  | read |
| KN-LIT-6282 | Rigorous Bounds on Cryptanalytic Time/Memory Tradeoffs |  |  | read |
| KN-LIT-6283 | Rigorous Foundations for Dual Attacks in Coding Theory |  |  | read |
| KN-LIT-6284 | Ring Signatures: Logarithmic-Size, No Setup — from Standard Assumptions |  |  | read |
| KN-LIT-6285 | Ring Signatures: Stronger Definitions, and Constructions without Random Oracles |  |  | read |
| KN-LIT-6286 | Ring-based Identity Based Encryption |  |  | read |
| KN-LIT-6287 | Ring-LWE in Polynomial Rings |  |  | read |
| KN-LIT-6288 | Ring/Module Learning with Errors under Linear |  |  | read |
| KN-LIT-6289 | Risky Traitor Tracing and New Differential Privacy Negative Results |  |  | read |
| KN-LIT-6290 | RIV for Robust Authenticated Encryption Farzaneh Abed1 , Christian Forler2 |  |  | read |
| KN-LIT-6291 | RKA Security beyond the Linear Barrier: IBE, Encryption and Signatures |  |  | read |
| KN-LIT-6292 | Robust Decentralized Multi-Client Functional Encryption: Motivation, Definition, and Inner-Product Constructions |  |  | read |
| KN-LIT-6293 | Robust Encryption, Revisited |  |  | read |
| KN-LIT-6294 | Robust Multiparty Computation with Linear Communication Complexity |  |  | read |
| KN-LIT-6295 | Robust Non-Interactive Multiparty Computation Against Constant-Size Collusion |  |  | read |
| KN-LIT-6296 | Robust Profiling for DPA-Style Attacks |  |  | read |
| KN-LIT-6297 | Robust Property-Preserving Hash Functions for Hamming Distance and More |  |  | read |
| KN-LIT-6298 | Robust Publicly Verifiable Covert Security: |  |  | read |
| KN-LIT-6299 | Robust Transforming Combiners from Indistinguishability Obfuscation to Functional Encryption |  |  | read |
| KN-LIT-6300 | Robuster Combiners for Oblivious Transfer |  |  | read |
| KN-LIT-6301 | Robustly Reusable Fuzzy Extractor from Standard Assumptions |  |  | read |
| KN-LIT-6302 | Robustness for Free in Unconditional Multi-Party Computation |  |  | read |
| KN-LIT-6303 | Rogue-Instance Security for Batch Knowledge Proofs ? |  |  | read |
| KN-LIT-6304 | Rotatable Zero Knowledge Sets: Post Compromise Secure Auditable Dictionaries with application to Key Transparency |  |  | read |
| KN-LIT-6305 | Rotation Key Reduction for Client-Server Systems of Deep Neural Network on Fully Homomorphic Encryption |  |  | read |
| KN-LIT-6306 | Rotational Cryptanalysis From a Differential-linear Perspective Practical Distinguishers for Round-reduced FRIET, Xoodoo, and Alzette |  |  | read |
| KN-LIT-6307 | Rotational Cryptanalysis of ARX |  |  | read |
| KN-LIT-6308 | Rotational Cryptanalysis of ARX Revisited Dmitry Khovratovich1 , Ivica Nikolić2 , Josef Pieprzyk3 |  |  | read |
| KN-LIT-6309 | Rotational cryptanalysis of round-reduced Keccak |  |  | read |
| KN-LIT-6310 | Rotational Differential-Linear Distinguishers of ARX Ciphers with Arbitrary Output Linear Masks |  |  | read |
| KN-LIT-6311 | Rotational Rebound Attacks on Reduced Skein |  |  | read |
| KN-LIT-6312 | Rotations and Translations of Number Field |  |  | read |
| KN-LIT-6313 | Round Efficient Secure Multiparty Quantum Computation with Identifiable Abort |  |  | read |
| KN-LIT-6314 | Round Optimal Blind Signatures |  |  | read |
| KN-LIT-6315 | Round Optimal Secure Multiparty Computation from Minimal Assumptions Arka Rai Choudhuri1[0000−0003−0452−3426] |  |  | read |
| KN-LIT-6316 | Round-Efficient Black-Box Construction of Composable Multi-Party Computation |  |  | read |
| KN-LIT-6317 | Round-Efficient Concurrently Composable Secure Computation via a Robust Extraction Lemma |  |  | read |
| KN-LIT-6318 | Round-Optimal and |  |  | read |
| KN-LIT-6319 | Round-Optimal and Efficient Verifiable Secret Sharing |  |  | read |
| KN-LIT-6320 | Round-optimal Black-box Commit-and-prove with Succinct Communication |  |  | read |
| KN-LIT-6321 | Round-Optimal Black-Box MPC in the Plain Model |  |  | read |
| KN-LIT-6322 | Round-Optimal Black-Box Protocol Compilers |  |  | read |
| KN-LIT-6323 | Round-Optimal Black-Box Secure Computation from Two-Round Malicious OT |  |  | read |
| KN-LIT-6324 | Round-Optimal Black-Box Two-Party Computation |  |  | read |
| KN-LIT-6325 | Round-Optimal Blind Signatures in the Plain Model from Classical and Quantum Standard Assumptions |  |  | read |
| KN-LIT-6326 | Round-Optimal Byzantine Agreement |  |  | read |
| KN-LIT-6327 | Round-Optimal Composable Blind Signatures in the Common Reference String Model |  |  | read |
| KN-LIT-6328 | Round-Optimal Contributory Conference Key Agreement |  |  | read |
| KN-LIT-6329 | Round-Optimal Fully Black-Box Zero-Knowledge Arguments from One-Way Permutations |  |  | read |
| KN-LIT-6330 | Round-optimal Honest-majority MPC in Minicrypt and with Everlasting Security |  |  | read |
| KN-LIT-6331 | Round-Optimal Multi-Party |  |  | read |
| KN-LIT-6332 | Round-Optimal Oblivious Transfer and MPC from Computational CSIDH |  |  | read |
| KN-LIT-6333 | Round-Optimal Password-Based Authenticated Key Exchange |  |  | read |
| KN-LIT-6334 | Round-Optimal Password-Protected Secret Sharing and T-PAKE in the Password-Only Model |  |  | read |
| KN-LIT-6335 | Round-Optimal Privacy-Preserving Protocols with Smooth Projective Hash Functions |  |  | read |
| KN-LIT-6336 | Round-Optimal Secure Multi-Party Computation |  |  | read |
| KN-LIT-6337 | Round-Optimal Secure Multiparty Computation with Honest Majority |  |  | read |
| KN-LIT-6338 | Round-optimal Verifiable Oblivious Pseudorandom Functions from Ideal Lattices |  |  | read |
| KN-LIT-6339 | Round-Robin is Optimal: Lower Bounds for Group Action Based Protocols |  |  | read |
| KN-LIT-6340 | Rounded Gaussians Fast and Secure Constant-Time Sampling for Lattice-Based Crypto |  |  | read |
| KN-LIT-6341 | Rounding and Chaining LLL: Finding Faster Small Roots of Univariate Polynomial Congruences |  |  | read |
| KN-LIT-6342 | Rounding in the Rings |  |  | read |
| KN-LIT-6343 | RSA Key Extraction via Low-Bandwidth Acoustic Cryptanalysis? |  |  | read |
| KN-LIT-6344 | RSA meets DPA: Recovering RSA Secret Keys from Noisy Analog Data |  |  | read |
| KN-LIT-6345 | RSA signatures and Rabin–Williams signatures: the state of the art |  |  | read |
| KN-LIT-6346 | RSA with Balanced Short Exponents and Its Application to Entity Authentication |  |  | read |
| KN-LIT-6347 | RSA with CRT: A new cost-effective solution to thwart fault attacks David Vigilant |  |  | read |
| KN-LIT-6348 | RSA–OAEP is Secure under the RSA Assumption |  |  | read |
| KN-LIT-6349 | Rubato: Noisy Ciphers for Approximate Homomorphic Encryption |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6350 | Run-time Accessible DRAM PUFs in Commodity Devices |  |  | read |
| KN-LIT-6351 | Safe curves for elliptic-curve cryptography |  |  | read |
| KN-LIT-6352 | Safely Exporting Keys from Secure Channels: On the Security of EAP-TLS and TLS Key Exporters |  |  | read |
| KN-LIT-6353 | Safety in Numbers: On the Need for Robust Diffie-Hellman Parameter Validation |  |  | read |
| KN-LIT-6354 | Salvaging Indifferentiability in a Multi-stage Setting |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6355 | Salvaging Merkle-Damgård for Practical Applications |  |  | read |
| KN-LIT-6356 | Salvaging Weak Security Bounds for Blockcipher-Based Constructions |  |  | read |
| KN-LIT-6357 | Sampling in a Quantum Population, and Applications |  |  | read |
| KN-LIT-6358 | Sanitization of FHE Ciphertexts |  |  | read |
| KN-LIT-6359 | SAS-Based Authenticated Key Agreement |  |  | read |
| KN-LIT-6360 | SAS-Based Group Authentication and Key Agreement Protocols |  |  | read |
| KN-LIT-6364 | Saturation Attacks on Reduced Round Skipjack |  |  | read |
| KN-LIT-6365 | SCA-LDPC: A Code-Based Framework for Key-Recovery Side-Channel Attacks on Post-Quantum Encryption Schemes Qian Guo[0000−0003−0930−3174]1 , Denis Nabokov[0009−0001−0740−5954]1 |  |  | read |
| KN-LIT-6366 | Scalable and Transparent Proofs over All Large Fields, via Elliptic Curves (ECFFT Part II) Eli Ben-Sasson1[0000−0002−0708−0483] , Dan Carmon1[0000−0001−9952−5947] |  |  | read |
| KN-LIT-6367 | Scalable and Unconditionally Secure Multiparty Computation |  |  | read |
| KN-LIT-6368 | Scalable Ciphertext Compression Techniques for |  |  | read |
| KN-LIT-6369 | Scalable Group Signatures with Revocation |  |  | read |
| KN-LIT-6370 | Scalable Multi-party Private Set Union from Multi-Query Secret-Shared Private Membership Test |  |  | read |
| KN-LIT-6371 | Scalable Multi-Party Private Set-Intersection |  |  | read |
| KN-LIT-6372 | Scalable Multiparty Computation with |  |  | read |
| KN-LIT-6373 | Scalable Protocols for Authenticated Group Key Exchange |  |  | read |
| KN-LIT-6374 | Scalable Pseudorandom Quantum States? |  |  | read |
| KN-LIT-6375 | Scalable Secure Multiparty Computation |  |  | read |
| KN-LIT-6376 | Scalable Zero Knowledge via Cycles of Elliptic Curves |  |  | read |
| KN-LIT-6377 | Scalable Zero Knowledge with no Trusted Setup |  |  | read |
| KN-LIT-6378 | Scale-Invariant Fully Homomorphic Encryption over the Integers |  |  | read |
| KN-LIT-6379 | SCALES MPC with Small Clients and Larger Ephemeral Servers |  |  | read |
| KN-LIT-6380 | SCALLOP: scaling the CSI-FiSh Luca De Feo1[0000−0002−9321−0773] , Tako Boris Fouotsa2[0000−0003−1821−8406] |  |  | read |
| KN-LIT-6381 | SCARE of Secret Ciphers with SPN Structures |  |  | read |
| KN-LIT-6382 | Schrödinger’s Pirate: How To Trace a Quantum Decoder |  |  | read |
| KN-LIT-6383 | Scream: a software-efficient stream cipher |  |  | read |
| KN-LIT-6384 | Scrutinizing and Improving Impossible Differential Attacks: |  |  | read |
| KN-LIT-6385 | Scrypt is Maximally Memory-Hard |  |  | read |
| KN-LIT-6386 | SDitH in the QROM Carlos Aguilar-Melchor1 �, Andreas Hülsing2? �, David Joseph1 � |  |  | read |
| KN-LIT-6387 | Se ond Preimage Atta ks on Dithered Hash |  |  | read |
| KN-LIT-6388 | Search for Related-key Differential Characteristics in DES-like ciphers |  |  | read |
| KN-LIT-6389 | Searchable Encryption Revisited: Consistency |  |  | read |
| KN-LIT-6390 | Searchable Encryption with Optimal Locality: Achieving Sublogarithmic Read Efficiency |  |  | read |
| KN-LIT-6391 | SEARCHING FOR DIFFERENTIAL ADDITION CHAINS |  |  | read |
| KN-LIT-6392 | Searching for Differential Paths in MD4 ? |  |  | read |
| KN-LIT-6393 | SeaSign: Compact isogeny signatures from class group actions |  |  | read |
| KN-LIT-6394 | Second Preimage Attack on 3-Pass HAVAL and Partial Key-Recovery Attacks on HMAC/NMAC-3-Pass HAVAL |  |  | read |
| KN-LIT-6395 | Second Preimages on n-bit Hash Functions for Much Less than 2n Work |  |  | read |
| KN-LIT-6396 | Second-Order Differential Collisions for Reduced SHA-256 |  |  | read |
| KN-LIT-6397 | Secret Can Be Public: Low-Memory AEAD Mode for High-Order Masking |  |  | read |
| KN-LIT-6398 | Secret Exponent Attacks on RSA-type Schemes with Moduli N = pr q |  |  | read |
| KN-LIT-6399 | Secret External Encodings Do not Prevent |  |  | read |
| KN-LIT-6400 | Secret Handshakes from CA-Oblivious Encryption |  |  | read |
| KN-LIT-6401 | Secret Keys from Channel Noise |  |  | read |
| KN-LIT-6402 | Secret Sharing and Non-Shannon Information Inequalities? |  |  | read |
| KN-LIT-6403 | Secret Sharing and Statistical Zero Knowledge |  |  | read |
| KN-LIT-6404 | Secret Sharing Schemes for Very Dense Graphs |  |  | read |
| KN-LIT-6405 | Secret-Sharing for NP |  |  | read |
| KN-LIT-6406 | Secret-Sharing Schemes for General and Uniform Access Structures |  |  | read |
| KN-LIT-6407 | SECTIONS ON CERTAIN j = 0 ELLIPTIC SURFACES |  |  | read |
| KN-LIT-6408 | Secure and Efficient Asynchronous Broadcast Protocols |  |  | read |
| KN-LIT-6409 | Secure and Efficient Software Masking on Superscalar Pipelined Processors |  |  | read |
| KN-LIT-6410 | Secure Arithmetic Computation with Constant Computational Overhead |  |  | read |
| KN-LIT-6411 | Secure Arithmetic Computation with No Honest Majority? |  |  | read |
| KN-LIT-6412 | Secure Blind Decryption |  |  | read |
| KN-LIT-6413 | Secure Certification of Mixed Quantum States with Application to Two-Party Randomness Generation |  |  | read |
| KN-LIT-6414 | Secure Channels based on Authenticated |  |  | read |
| KN-LIT-6415 | Secure Communication in Multicast Graphs |  |  | read |
| KN-LIT-6416 | Secure Communications over Insecure Channels Based on Short Authenticated Strings |  |  | read |
| KN-LIT-6417 | Secure Computability of Functions in the IT setting with |  |  | read |
| KN-LIT-6418 | Secure Computation Against Adaptive Auxiliary Information |  |  | read |
| KN-LIT-6419 | Secure Computation and Its Diverse Applications Yuval Ishai |  |  | read |
| KN-LIT-6420 | Secure Computation based on Leaky Correlations: High Resilience Setting |  |  | read |
| KN-LIT-6421 | Secure Computation for Big Data |  |  | read |
| KN-LIT-6422 | Secure Computation from Elastic Noisy Channels |  |  | read |
| KN-LIT-6423 | Secure Computation from Leaky Correlated Randomness |  |  | read |
| KN-LIT-6424 | Secure Computation From Millionaire |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6425 | Secure Computation from One-Way Noisy Communication, or: |  |  | read |
| KN-LIT-6426 | Secure Computation from Random Error Correcting Codes |  |  | read |
| KN-LIT-6427 | Secure Computation on the Web: Computing without Simultaneous Interaction |  |  | read |
| KN-LIT-6428 | Secure Computation using Leaky Correlations (Asymptotically Optimal Constructions)? |  |  | read |
| KN-LIT-6429 | Secure Computation with |  |  | read |
| KN-LIT-6430 | Secure Computation with Partial Message Loss |  |  | read |
| KN-LIT-6431 | Secure Computation with Shared EPR Pairs (Or: How to Teleport in Zero-Knowledge) |  |  | read |
| KN-LIT-6432 | Secure Computation Without Authentication |  |  | read |
| KN-LIT-6433 | Secure Conversion Between Boolean and Arithmetic Masking of Any Order |  |  | read |
| KN-LIT-6434 | Secure Data Management in Trusted Computing |  |  | read |
| KN-LIT-6435 | Secure Database Commitments and Universal Arguments of Quasi Knowledge |  |  | read |
| KN-LIT-6436 | Secure Distributed Linear Algebra in a Constant Number of Rounds |  |  | read |
| KN-LIT-6437 | Secure Efficient History-Hiding Append-Only Signatures in the Standard Model |  |  | read |
| KN-LIT-6438 | Secure Human Identification Protocols |  |  | read |
| KN-LIT-6439 | Secure Hybrid Encryption from Weakened Key Encapsulation |  |  | read |
| KN-LIT-6440 | Secure Identity Based Encryption Without Random Oracles |  |  | read |
| KN-LIT-6441 | Secure Lightweight Entity Authentication with Strong PUFs: Mission Impossible? |  |  | read |
| KN-LIT-6442 | Secure Linear Algebra Using Linearly Recurrent Sequences |  |  | read |
| KN-LIT-6443 | Secure Massively Parallel Computation for Dishonest Majority |  |  | read |
| KN-LIT-6444 | Secure Message Authentication against Related-Key Attack |  |  | read |
| KN-LIT-6445 | Secure MPC: Laziness Leads to GOD |  |  | read |
| KN-LIT-6446 | Secure Multi-Party Computation with Identifiable Abort |  |  | read |
| KN-LIT-6447 | Secure Multi-party Quantum Computation with a Dishonest Majority |  |  | read |
| KN-LIT-6448 | Secure Multiparty Computation from Threshold Encryption based on Class Groups |  |  | read |
| KN-LIT-6449 | Secure Multiparty Computation with Free Branching |  |  | read |
| KN-LIT-6450 | Secure Multiparty Computation with Minimal Interaction |  |  | read |
| KN-LIT-6451 | Secure Multiparty Computation with Sublinear Preprocessing |  |  | read |
| KN-LIT-6452 | Secure Network Coding Over the Integers? |  |  | read |
| KN-LIT-6453 | Secure Non-Interactive Reducibility is Decidable |  |  | read |
| KN-LIT-6454 | Secure Non-Interactive Reduction and Spectral Analysis of Correlations 1 2? |  |  | read |
| KN-LIT-6455 | Secure Non-interactive Simulation: Feasibility & Rate |  |  | read |
| KN-LIT-6456 | Secure Obfuscation for Encrypted Signatures |  |  | read |
| KN-LIT-6457 | Secure Obfuscation in a Weak Multilinear Map Model? Sanjam Garg?? , Eric Miles? ? ? , Pratyay Mukherjee?? , Amit Sahai??? |  |  | read |
| KN-LIT-6458 | Secure Physical Computation using Disposable Circuits |  |  | read |
| KN-LIT-6459 | Secure Protocol Transformations |  |  | read |
| KN-LIT-6460 | Secure Protocols with Asymmetric Trust |  |  | read |
| KN-LIT-6461 | Secure Quantum Computation with Classical Communication |  |  | read |
| KN-LIT-6462 | Secure Quantum Extraction Protocols |  |  | read |
| KN-LIT-6463 | Secure Remote Authentication Using Biometric Data |  |  | read |
| KN-LIT-6464 | Secure Sampling with Sublinear Communication Seung Geol Choi1 , Dana Dachman-Soled2 |  |  | read |
| KN-LIT-6465 | Secure Signatures and Chosen Ciphertext Security in a Quantum Computing World |  |  | read |
| KN-LIT-6466 | Secure Sketch for Biometric Templates |  |  | read |
| KN-LIT-6467 | Secure Software Leasing |  |  | read |
| KN-LIT-6468 | Secure Software Leasing from Standard Assumptions |  |  | read |
| KN-LIT-6469 | Secure Software Leasing Without Assumptions |  |  | read |
| KN-LIT-6470 | Secure Two-Party Computation is Practical |  |  | read |
| KN-LIT-6471 | Secure Two-Party Computation via Cut-and-Choose Oblivious Transfer |  |  | read |
| KN-LIT-6472 | Secure Two-Party Computation with Low Communication |  |  | read |
| KN-LIT-6473 | Secure Two-Party Computation with Reusable Bit-Commitments, via a Cut-and-Choose with Forge-and-Lose Technique |  |  | read |
| KN-LIT-6474 | Secure Two-Party Quantum Evaluation of Unitaries Against Specious Adversaries |  |  | read |
| KN-LIT-6475 | Secure Wire Shuffling in the Probing Model |  |  | read |
| KN-LIT-6476 | Securely Obfuscating Re-Encryption Susan Hohenberger1,2 , Guy N. Rothblum3? |  |  | read |
| KN-LIT-6477 | Securing Approximate Homomorphic Encryption using Differential Privacy? |  |  | read |
| KN-LIT-6478 | Securing Circuits Against Constant-Rate Tampering |  |  | read |
| KN-LIT-6479 | Securing Circuits and Protocols Against 1/ poly(k) Tampering Rate |  |  | read |
| KN-LIT-6480 | Securing Computation Against Continuous Leakage |  |  | read |
| KN-LIT-6481 | Securing Cryptography Implementations in Embedded Systems |  |  | read |
| KN-LIT-6482 | Securing RSA-KEM via the AES |  |  | read |
| KN-LIT-6483 | Securing Threshold Cryptosystems against Chosen Ciphertext Attack |  |  | read |
| KN-LIT-6484 | Security Against Covert Adversaries: Efficient Protocols for Realistic Adversaries? |  |  | read |
| KN-LIT-6485 | Security Amplification for Interactive Cryptographic Primitives |  |  | read |
| KN-LIT-6486 | Security Amplification for the Cascade of Arbitrarily Weak PRPs: Tight Bounds via the Interactive Hardcore Lemma |  |  | read |
| KN-LIT-6487 | Security Analysis and Improvements for the IETF MLS Standard for Group Messaging |  |  | read |
| KN-LIT-6488 | Security Analysis of a 2/3-rate Double Length Compression Function in The Black-Box Model |  |  | read |
| KN-LIT-6489 | Security Analysis of Constructions Combining FIL Random Oracles |  |  | read |
| KN-LIT-6490 | Security Analysis of CPace |  |  | read |
| KN-LIT-6491 | Security Analysis of IKE’s Signature-based Key-Exchange Protocol ? |  |  | read |
| KN-LIT-6492 | Security Analysis of KEA Authenticated Key Exchange Protocol |  |  | read |
| KN-LIT-6493 | Security Analysis of Key-Alternating Feistel Ciphers |  |  | read |
| KN-LIT-6494 | Security Analysis of NIST CTR-DRBG |  |  | read |
| KN-LIT-6495 | Security Analysis of PRINCE |  |  | read |
| KN-LIT-6496 | Security Analysis of Quantum Lightning |  |  | read |
| KN-LIT-6497 | Security Analysis of RSA-BSSA |  |  | read |
| KN-LIT-6498 | Security analysis of SPAKE2+ |  |  | read |
| KN-LIT-6499 | Security Analysis of the Mode of JH Hash Function |  |  | read |
| KN-LIT-6500 | Security Analysis of the MOR Cryptosystem |  |  | read |
| KN-LIT-6501 | Security Analysis of the Strong Diffie-Hellman Problem |  |  | read |
| KN-LIT-6502 | Security Analysis of the WhatsApp End-to-End |  |  | read |
| KN-LIT-6503 | Security Bounds for the Design of Code-based Cryptosystems |  |  | read |
| KN-LIT-6504 | Security Evaluation Against Electromagnetic Analysis at Design Time |  |  | read |
| KN-LIT-6505 | Security Evaluations Beyond Computing Power How to Analyze Side-Channel Attacks you Cannot Mount? |  |  | read |
| KN-LIT-6506 | Security Flaws Induced by CBC Padding |  |  | read |
| KN-LIT-6507 | Security in the Presence of Key Reuse: |  |  | read |
| KN-LIT-6508 | Security Limitations of Classical-Client Delegated Quantum Computing |  |  | read |
| KN-LIT-6509 | Security Limits for Compromising Emanations |  |  | read |
| KN-LIT-6510 | Security Notions and Generic Constructions for Client Puzzles |  |  | read |
| KN-LIT-6511 | Security Notions for Unconditionally Secure Signature Schemes |  |  | read |
| KN-LIT-6512 | Security of Blind Signatures Revisited |  | Journal of Cryptology | read |
| KN-LIT-6513 | Security of Blind Signatures Under Aborts |  |  | read |
| KN-LIT-6514 | Security of Digital Signature Schemes in Weakened Random Oracle Models |  |  | read |
| KN-LIT-6515 | Security of Encryption Schemes in Weakened Random Oracle Models |  |  | read |
| KN-LIT-6516 | Security of Full-State Keyed Sponge and Duplex: Applications to Authenticated Encryption |  |  | read |
| KN-LIT-6517 | Security of Hedged Fiat–Shamir Signatures under Fault Attacks |  |  | read |
| KN-LIT-6518 | Security of Keyed Sponge Constructions Using a Modular Proof Approach |  |  | read |
| KN-LIT-6519 | Security of Reduced Version of the Block Cipher Camellia against Truncated and Impossible Differential Cryptanalysis |  |  | read |
| KN-LIT-6520 | Security of Sanitizable Signatures Revisited Christina Brzuska, Marc Fischlin, Tobias Freudenreich, Anja Lehmann |  |  | read |
| KN-LIT-6521 | Security of Symmetric Encryption against Mass Surveillance |  |  | read |
| KN-LIT-6522 | Security of the AES with a Secret S-box |  |  | read |
| KN-LIT-6523 | Security of the Blockchain against Long Delay Attack |  |  | read |
| KN-LIT-6524 | Security of the Fiat-Shamir Transformation in the Quantum Random-Oracle Model |  |  | read |
| KN-LIT-6525 | Security of Truncated Permutation Without Initial Value |  |  | read |
| KN-LIT-6526 | Security Proof for Partial-Domain Hash |  |  | read |
| KN-LIT-6527 | Security Proofs for Identity-Based Identification and Signature Schemes |  |  | read |
| KN-LIT-6528 | Security Proofs for Key-Alternating Ciphers with Non-Independent Round Permutations |  |  | read |
| KN-LIT-6529 | Security Reductions for White-Box Key-Storage in Mobile Payments |  |  | read |
| KN-LIT-6530 | Security under Message-Derived Keys: Signcryption in iMessage |  |  | read |
| KN-LIT-6531 | Security with Functional Re-Encryption from CPA |  |  | read |
| KN-LIT-6532 | Security-Amplifying Combiners for Collision-Resistant Hash Functions |  |  | read |
| KN-LIT-6533 | Security-Mediated Certificateless Cryptography |  |  | read |
| KN-LIT-6534 | Security-Preserving Distributed Samplers: How to Generate any CRS in One Round without Random Oracles |  |  | read |
| KN-LIT-6535 | Security/Efficiency Tradeoffs for Permutation-Based Hashing |  |  | read |
| KN-LIT-6536 | Seedless Fruit is the Sweetest: |  |  | read |
| KN-LIT-6537 | Selecting Time Samples for Multivariate DPA Attacks |  |  | read |
| KN-LIT-6538 | Selective Opening Security from Simulatable Data Encapsulation |  |  | read |
| KN-LIT-6539 | Selective Opening Security in the |  |  | read |
| KN-LIT-6540 | Self-bilinear Map on Unknown Order Groups from Indistinguishability Obfuscation and Its Applications? |  |  | read |
| KN-LIT-6541 | Self-Blindable Credential Certificates from the Weil Pairing |  |  | read |
| KN-LIT-6542 | Self-Generated-Certificate Public Key Encryption Without Pairing |  |  | read |
| KN-LIT-6543 | Self-Referencing: A Scalable Side-Channel Approach for Hardware Trojan Detection |  |  | read |
| KN-LIT-6544 | Self-Updatable Encryption: Time Constrained Access Control with |  |  | read |
| KN-LIT-6545 | Semantic Security and Indistinguishability in the Quantum World |  |  | read |
| KN-LIT-6546 | Semantic Security for the Wiretap Channel |  |  | read |
| KN-LIT-6547 | Semantically Secure Order-Revealing Encryption: Multi-Input |  |  | read |
| KN-LIT-6548 | Semi-Adaptive Security and Bundling |  |  | read |
| KN-LIT-6549 | Semi-Homomorphic Encryption and Multiparty Computation |  |  | read |
| KN-LIT-6550 | Semi-Honest to Malicious Oblivious Transfer |  |  | read |
| KN-LIT-6551 | Semi-Quantum Copy-Protection and More |  |  | read |
| KN-LIT-6552 | Sender-Anamorphic Encryption Reformulated: |  |  | read |
| KN-LIT-6553 | Sender-binding Key Encapsulation |  |  | read |
| KN-LIT-6554 | Separate Your Domains: |  |  | read |
| KN-LIT-6555 | Separating Adaptive Streaming from Oblivious Streaming using the Bounded Storage Model |  |  | read |
| KN-LIT-6556 | Separating Computational and Statistical Differential Privacy in the Client-Server Model |  |  | read |
| KN-LIT-6557 | Separating IND-CPA and Circular Security for Unbounded Length Key Cycles |  |  | read |
| KN-LIT-6558 | Separating Random Oracle Proofs from Complexity Theoretic Proofs: The Non-committing Encryption Case |  |  | read |
| KN-LIT-6559 | Separating Semantic and Circular Security for Symmetric-Key Bit Encryption from the Learning with Errors Assumption |  |  | read |
| KN-LIT-6560 | Separating Short Structure-Preserving Signatures from Non-Interactive Assumptions |  |  | read |
| KN-LIT-6561 | Separating Sources for |  |  | read |
| KN-LIT-6562 | Separations in Circular Security for Arbitrary Length Key Cycles |  |  | read |
| KN-LIT-6563 | Sequences of Games: A Tool for Taming Complexity in Security Proofs Victor Shoup |  |  | read |
| KN-LIT-6564 | Sequential Aggregate Signatures and Multisignatures Without Random Oracles Steve Lu?1 , Rafail Ostrovsky??2 , Amit Sahai? ? ?3 |  |  | read |
| KN-LIT-6565 | Sequential Aggregate Signatures with Lazy Verification from Trapdoor Permutations |  |  | read |
| KN-LIT-6566 | Sequential Aggregate Signatures with Short Public Keys: Design, Analysis and Implementation Studies |  |  | read |
| KN-LIT-6567 | Server-Aided Verification: Theory and Practice |  |  | read |
| KN-LIT-6568 | Sesquilinear pairings on elliptic curves (+ isogenies) Katherine E. Stange (+ Joseph Macula) |  |  | read |
| KN-LIT-6569 | Session Resumption Protocols and Efficient Forward Security for TLS 1.3 0-RTT |  |  | read |
| KN-LIT-6570 | Session-Key Generation using Human Passwords Only |  |  | read |
| KN-LIT-6571 | Seven-Property-Preserving Iterated Hashing: ROX |  |  | read |
| KN-LIT-6572 | Séta: Supersingular Encryption from Torsion Attacks |  |  | read |
| KN-LIT-6573 | SHA-3 interoperability |  |  | read |
| KN-LIT-6574 | Share conversion, pseudorandom secret-sharing and applications to secure distributed computing |  |  | read |
| KN-LIT-6575 | Sharper Bounds in Lattice-Based Cryptography using the Rényi Divergence |  |  | read |
| KN-LIT-6576 | Short and Stateless Signatures from the RSA Assumption |  |  | read |
| KN-LIT-6577 | Short Chosen-Prefix Collisions for MD5 and the Creation of a Rogue CA Certificate |  |  | read |
| KN-LIT-6578 | Short Code-based One-out-of-Many Proofs and Applications |  |  | read |
| KN-LIT-6579 | Short Concurrent Covert Authenticated Key Exchange (Short cAKE) |  |  | read |
| KN-LIT-6580 | Short Digital Signatures and ID-KEMs via Truncation Collision Resistance |  |  | read |
| KN-LIT-6581 | Short Discrete Log Proofs for |  |  | read |
| KN-LIT-6582 | Short Exponent Diffie-Hellman Problems |  |  | read |
| KN-LIT-6583 | Short generators without quantum computers: the case of multiquadratics |  |  | read |
| KN-LIT-6584 | Short Group Signatures |  |  | read |
| KN-LIT-6585 | Short Group Signatures via Structure-Preserving Signatures: Standard Model Security from Simple Assumptions |  |  | read |
| KN-LIT-6586 | Short Leakage Resilient and Non-malleable |  |  | read |
| KN-LIT-6587 | Short Memory Scalar Multiplication on Koblitz Curves |  |  | read |
| KN-LIT-6588 | Short Non-interactive Zero-Knowledge Proofs |  |  | read |
| KN-LIT-6589 | Short Pairing-based Non-interactive Zero-Knowledge Arguments |  |  | read |
| KN-LIT-6590 | Short Pairing-Free Blind Signatures with Exponential Security |  |  | read |
| KN-LIT-6591 | Short Signatures from Regular Syndrome Decoding in the Head |  |  | read |
| KN-LIT-6592 | Short signatures from the Weil pairing |  |  | read |
| KN-LIT-6593 | Short Signatures From Weaker Assumptions |  |  | read |
| KN-LIT-6594 | Short Signatures in the Random Oracle Model |  |  | read |
| KN-LIT-6595 | Short Signatures With Short Public Keys From Homomorphic Trapdoor Functions |  |  | read |
| KN-LIT-6596 | Short Signatures Without Random Oracles |  |  | read |
| KN-LIT-6597 | Short Variable Length Domain Extenders With Beyond Birthday Bound Security |  |  | read |
| KN-LIT-6598 | Short, Invertible Elements in Partially Splitting |  |  | read |
| KN-LIT-6599 | Short-lived zero-knowledge proofs and signatures |  |  | read |
| KN-LIT-65ecae | On syndrome decoding of linear codes | 1986 | Proceedings of the 9th All-Union Symposium on Redundancy in Information Systems | false |
| KN-LIT-6600 | Short-output universal hash functions and |  |  | read |
| KN-LIT-6601 | Shorter Hash-and-Sign Lattice-Based Signatures Thomas Espitau[0000−0002−7655−9594]1 , Mehdi Tibouchi[0000−0002−2736−2963]1 |  |  | read |
| KN-LIT-6602 | Shorter Lattice-Based Group Signatures via |  |  | read |
| KN-LIT-6603 | Shorter Lattice-Based Zero-Knowledge Proofs via One-Time Commitments |  |  | read |
| KN-LIT-6604 | Shorter Non-Interactive Zero-Knowledge Arguments and ZAPs for Algebraic Languages |  |  | read |
| KN-LIT-6605 | Shorter Pairing-based Arguments under Standard Assumptions |  |  | read |
| KN-LIT-6606 | Shorter QA-NIZK and SPS with Tighter Security Masayuki Abe1 , Charanjit S. Jutla2 , Miyako Ohkubo3 , Jiaxin Pan4 |  |  | read |
| KN-LIT-6607 | Shorter Quadratic QA-NIZK Proofs |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6608 | Shorter Quasi-Adaptive NIZK Proofs for Linear Subspaces |  |  | read |
| KN-LIT-6609 | Shorter Ring Signatures from Standard Assumptions Alonso González1 |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6610 | Shuffling Against Side-Channel Attacks: a Comprehensive Study with Cautionary Note Nicolas Veyrat-Charvillon, Marcel Medwed |  |  | read |
| KN-LIT-6611 | SiBIR: Signer-Base Intrusion-Resilient Signatures |  |  | read |
| KN-LIT-6612 | Side Channel Attack to Actual Cryptanalysis: Breaking CRT-RSA with Low Weight Decryption Exponents |  |  | read |
| KN-LIT-6613 | Side Channel Cryptanalysis of a Higher Order Masking Scheme |  |  | read |
| KN-LIT-6614 | Side Channel Information Set Decoding using Iterative Chunking Plaintext Recovery from the “Classic McEliece” Hardware Reference Implementation |  |  | read |
| KN-LIT-6615 | Side-Channel Analysis of Multiplications in GF(2128 ) Application to AES-GCM |  |  | read |
| KN-LIT-6616 | Side-channel Analysis of Six SHA-3 Candidates |  |  | read |
| KN-LIT-6617 | Side-Channel Analysis Protection and Low-Latency in Action – case study of PRINCE and Midori |  |  | read |
| KN-LIT-6618 | Side-Channel Attack Against RSA Key |  |  | read |
| KN-LIT-6619 | Side-Channel Attacks in ECC: A General Technique for Varying the Parametrization of the Elliptic Curve |  |  | read |
| KN-LIT-6620 | Side-Channel Attacks on Textbook RSA and ElGamal Encryption Ulrich Kühn |  |  | read |
| KN-LIT-6621 | Side-Channel Leakage through Static Power – Should We Care about in Practice? – Amir Moradi |  |  | read |
| KN-LIT-6622 | Side-channel Masking with Pseudo-Random Generator |  |  | read |
| KN-LIT-6623 | SIDH Proof of Knowledge |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6624 | Sieve-in-the-Middle: Improved MITM Attacks |  |  | read |
| KN-LIT-6625 | Sieving for shortest vectors in lattices using angular locality-sensitive hashing |  |  | read |
| KN-LIT-6626 | Sieving for twin smooth integers with solutions to the Prouhet-Tarry-Escott problem |  |  | read |
| KN-LIT-6627 | Sieving Using Bucket Sort? |  |  | read |
| KN-LIT-6628 | SiGamal: A supersingular isogeny-based PKE and its application to a PRF |  |  | read |
| KN-LIT-6629 | Sigma protocols for MQ, PKP and SIS, and fishy signature schemes |  |  | read |
| KN-LIT-6630 | Sigma Protocols from |  |  | read |
| KN-LIT-6631 | SIGMA: the ‘SIGn-and-MAc’ Approach to Authenticated Diffie-Hellman and its Use in the IKE Protocols |  |  | read |
| KN-LIT-6632 | Signature Schemes with Bounded Leakage Resilience |  |  | read |
| KN-LIT-6633 | Signature Schemes with Efficient Protocols and Dynamic Group Signatures from Lattice Assumptions |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6634 | Signatures from Sequential-OR Proofs |  |  | read |
| KN-LIT-6635 | Signatures of Correct Computation |  |  | read |
| KN-LIT-6636 | Signatures Resilient to Continual Leakage on Memory and Computation |  |  | read |
| KN-LIT-6637 | Signatures with Flexible Public Key: Introducing Equivalence Classes for Public Keys |  |  | read |
| KN-LIT-6638 | Signed Binary Representations Revisited Katsuyuki Okeya1 , Katja Schmidt-Samoa2 |  |  | read |
| KN-LIT-6639 | Signing a Linear Subspace: Signature Schemes for Network Coding |  |  | read |
| KN-LIT-6640 | SILVER – Statistical Independence and Leakage Verification |  |  | read |
| KN-LIT-6641 | Silver: Silent VOLE and Oblivious Transfer from Hardness of Decoding Structured LDPC Codes |  |  | read |
| KN-LIT-6642 | Simpira v2: A Family of Efficient Permutations Using the AES Round Function |  |  | read |
| KN-LIT-6643 | Simple Adaptive Oblivious Transfer Without Random Oracle |  |  | read |
| KN-LIT-6644 | Simple and Efficient Batch Verification Techniques for Verifiable Delay Functions |  |  | read |
| KN-LIT-6645 | Simple and Efficient Perfectly-Secure Asynchronous MPC ? |  |  | read |
| KN-LIT-6646 | Simple and Efficient Public-Key Encryption from Computational Diffie-Hellman in the Standard Model |  |  | read |
| KN-LIT-6647 | Simple And Efficient Shuffling With Provable |  |  | read |
| KN-LIT-6648 | Simple and Efficient Two-Server ORAM |  |  | read |
| KN-LIT-6649 | Simple and Generic Constructions of Succinct Functional Encryption |  |  | read |
| KN-LIT-6650 | Simple and More Efficient PRFs with Tight Security from LWE and Matrix-DDH? |  |  | read |
| KN-LIT-6651 | Simple and Tight Bounds for Information |  |  | read |
| KN-LIT-6652 | Simple Chosen-Ciphertext Security from Low-Noise LPN |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6653 | Simple Constructions from (Almost) Regular One-Way Functions |  |  | read |
| KN-LIT-6654 | Simple Functional Encryption Schemes for Inner Products |  |  | read |
| KN-LIT-6655 | Simple Key Enumeration (and Rank Estimation) using Histograms: an Integrated Approach |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6656 | Simple Lattice Trapdoor Sampling from a Broad Class of Distributions |  |  | read |
| KN-LIT-6657 | Simple Photonic Emission Analysis of AES Photonic side channel analysis for the rest of us Alexander Schlösser,1 , Dmitry Nedospasov,2 , Juliane Krämer2 |  |  | read |
| KN-LIT-6658 | Simple Power Analysis of Unified Code for ECC Double and Add |  |  | read |
| KN-LIT-6659 | Simple Power Analysis on AES Key Expansion Revisited |  |  | read |
| KN-LIT-6660 | Simple Proofs of Sequential Work |  |  | read |
| KN-LIT-6661 | Simple Proofs of Space-Time and Rational Proofs of Storage |  |  | read |
| KN-LIT-6662 | Simple Refreshing in the Noisy Leakage Model |  |  | read |
| KN-LIT-6663 | Simple Schemes in the Bounded Storage Model |  |  | read |
| KN-LIT-6664 | Simple Tests of Quantumness Also Certify Qubits |  |  | read |
| KN-LIT-6665 | Simple Threshold (Fully Homomorphic) Encryption From LWE With Polynomial Modulus |  |  | read |
| KN-LIT-6666 | Simple, Black-Box Constructions of Adaptively Secure Protocols? |  |  | read |
| KN-LIT-6667 | Simple, Fast, Efficient, and Tightly-Secure Non-Malleable Non-Interactive Timed Commitments? |  |  | read |
| KN-LIT-6668 | Simpler and More Efficient Rank Estimation for |  |  | read |
| KN-LIT-6669 | Simpler Efficient Group Signatures from Lattices? |  |  | read |
| KN-LIT-6670 | Simpler Statistically Sender Private Oblivious Transfer from Ideals of Cyclotomic Integers ? |  |  | read |
| KN-LIT-6671 | Simplex Consensus: A Simple and Fast Consensus Protocol |  |  | read |
| KN-LIT-6672 | Simplified MITM Modeling for Permutations: New (Quantum) Attacks |  |  | read |
| KN-LIT-6673 | Simplified Threshold RSA with Adaptive and Proactive Security |  |  | read |
| KN-LIT-6674 | Simplifying Design and Analysis of Complex Predicate Encryption Schemes |  |  | read |
| KN-LIT-6675 | Simplifying Game-Based Definitions |  |  | read |
| KN-LIT-6676 | Simulatable Adaptive Oblivious Transfer |  |  | read |
| KN-LIT-6677 | Simulatable Channels: Extended Security that is |  |  | read |
| KN-LIT-6678 | Simulatable Commitments and Efficient Concurrent Zero-Knowledge |  |  | read |
| KN-LIT-6679 | Simulatable Leakage: Analysis, Pitfalls, and new Constructions |  |  | read |
| KN-LIT-6680 | Simulatable VRFs with Applications to Multi-Theorem NIZK |  |  | read |
| KN-LIT-6681 | Simulating Auxiliary Inputs, Revisited ? |  |  | read |
| KN-LIT-6682 | Simulation in Quasi-polynomial Time, and its Application to Protocol Composition |  |  | read |
| KN-LIT-6683 | Simulation without the Artificial Abort: |  |  | read |
| KN-LIT-6684 | Simulation-Based Concurrent Non-Malleable Commitments and Decommitments |  |  | read |
| KN-LIT-6685 | Simulation-based Selective Opening CCA Security for PKE from Key Encapsulation Mechanisms |  |  | read |
| KN-LIT-6686 | Simulation-Extractable KZG Polynomial |  |  | read |
| KN-LIT-6687 | Simulation-Sound Arguments for LWE and Applications to KDM-CCA2 Security |  |  | read |
| KN-LIT-6688 | Simulation-Sound NIZK Proofs for a Practical |  |  | read |
| KN-LIT-6689 | Simultaneous Amplification: The Case of Non-Interactive Zero-Knowledge |  |  | read |
| KN-LIT-6690 | Simultaneous Hardcore Bits and Cryptography Against Memory Attacks |  |  | read |
| KN-LIT-6691 | Simultaneous Secrecy and Reliability Amplification for a General Channel Model |  |  | read |
| KN-LIT-6692 | Simultaneously Resettable Arguments of Knowledge |  |  | read |
| KN-LIT-6693 | Sine Series Approximation of the Mod Function for Bootstrapping of Approximate HE |  |  | read |
| KN-LIT-6694 | Single Base Modular Multiplication for Efficient Hardware RNS Implementations of ECC |  |  | read |
| KN-LIT-6695 | Single-Server Private Information Retrieval with Sublinear Amortized Time |  |  | read |
| KN-LIT-6696 | Single-shot security for one-time memories in the isolated qubits model Yi-Kai Liu |  |  | read |
| KN-LIT-6697 | Single-to-Multi-Theorem Transformations for Non-Interactive Statistical Zero-Knowledge |  |  | read |
| KN-LIT-6698 | Single-Trace Side-Channel Attacks on Masked Lattice-Based Encryption |  |  | read |
| KN-LIT-6699 | SipHash: a fast short-input PRF |  |  | read |
| KN-LIT-6700 | Sleuth: Automated Verification of Software Power Analysis Countermeasures |  |  | read |
| KN-LIT-6701 | Slide Attacks on a Class of Hash Functions |  |  | read |
| KN-LIT-6702 | Slide Reduction, Revisited—Filling the Gaps in SVP Approximation |  |  | read |
| KN-LIT-6703 | Sliding right into disaster: Left-to-right sliding windows leak |  |  | read |
| KN-LIT-6704 | Small CRT-Exponent RSA Revisited |  |  | read |
| KN-LIT-6705 | Small Public Keys and Fast Verification for Multivariate Quadratic Public Key Systems |  |  | read |
| KN-LIT-6706 | Small Scale Variants of the AES |  |  | read |
| KN-LIT-6707 | Smaller decoding exponents: ball-collision decoding |  |  | read |
| KN-LIT-6708 | Smaller Keys for Code-based Cryptography: QC-MDPC McEliece Implementations on Embedded Devices |  |  | read |
| KN-LIT-6709 | SMASH - A Cryptographic Hash Function |  |  | read |
| KN-LIT-6710 | Smashing SQUASH-0 |  |  | read |
| KN-LIT-6711 | Smashing WEP in A Passive Attack |  |  | read |
| KN-LIT-6712 | SMILE: Set Membership from Ideal Lattices with Applications to Ring Signatures and Confidential Transactions |  |  | read |
| KN-LIT-6713 | Smooth NIZK Arguments |  |  | read |
| KN-LIT-6714 | Smooth Projective Hashing and Password-Based Authenticated Key Exchange from Lattices |  |  | read |
| KN-LIT-6715 | Smooth Projective Hashing and Two-Message |  |  | read |
| KN-LIT-6716 | Smooth Projective Hashing for Conditionally Extractable Commitments |  |  | read |
| KN-LIT-6717 | Smoothing Out Binary Linear Codes and Worst-case Sub-exponential Hardness for LPN |  |  | read |
| KN-LIT-6718 | SNACKs: Leveraging Proofs of Sequential Work for Blockchain Light Clients |  |  | read |
| KN-LIT-6719 | Snapshot-Oblivious RAMs: Sub-Logarithmic Efficiency for Short Transcripts |  |  | read |
| KN-LIT-6720 | SNARGs and PPAD Hardness from the Decisional Diffie-Hellman Assumption |  |  | read |
| KN-LIT-6721 | SNARGs for Monotone Policy Batch NP |  |  | read |
| KN-LIT-6722 | SNARGs for P from |  |  | read |
| KN-LIT-6723 | SNARKs for C : Verifying Program Executions |  |  | read |
| KN-LIT-6724 | Snarky Ceremonies |  |  | read |
| KN-LIT-6725 | Snarky Signatures: Minimal Signatures of Knowledge from Simulation-Extractable SNARKs |  |  | read |
| KN-LIT-6726 | Snowblind: A Threshold |  |  | read |
| KN-LIT-6727 | SoC it to EM: electromagnetic side-channel attacks on a complex system-on-chip |  |  | read |
| KN-LIT-6728 | SOFIA: MQ-based signatures in the QROM 2 3 and Joost Rijneveld and |  |  | read |
| KN-LIT-6729 | Soft Analytical Side-Channel Attacks |  |  | read |
| KN-LIT-6730 | Soft Decision Error Correction for Compact Memory-Based PUFs using a Single Enrollment |  |  | read |
| KN-LIT-6731 | SoftSpokenOT: Quieter OT Extension From Small-Field Silent VOLE in the Minicrypt Model |  |  | read |
| KN-LIT-6732 | Software implementation of binary elliptic curves: impact of the carry-less multiplier on scalar multiplication Jonathan Taverne1? , Armando Faz-Hernández2 , Diego F. Aranha3?? |  |  | read |
| KN-LIT-6733 | Software implementation of Koblitz curves over quadratic fields |  |  | read |
| KN-LIT-6734 | SoK: Learning With Errors, Circular Security, and Fully Homomorphic Encryption |  |  | read |
| KN-LIT-6735 | Solving a 676-bit Discrete Logarithm Problem in GF(36n ) Takuya Hayashi1 |  |  | read |
| KN-LIT-6736 | Solving a Discrete Logarithm Problem with Auxiliary Input on a 160-bit |  |  | read |
| KN-LIT-6737 | Solving Linear Equations Modulo Divisors: On Factoring Given Any Bits |  |  | read |
| KN-LIT-6738 | Solving Linear Equations Modulo Unknown Divisors: Revisited |  |  | read |
| KN-LIT-6739 | Solving LPN Using Covering Codes |  |  | read |
| KN-LIT-6740 | SOLVING NORM EQUATIONS IN GLOBAL FUNCTION FIELDS |  |  | read |
| KN-LIT-6741 | Solving Quadratic Equations with XL on Parallel Architectures |  |  | read |
| KN-LIT-6742 | Solving Random Subset Sum Problem by lp -norm SVP Oracle ? |  |  | read |
| KN-LIT-6743 | Solving Systems of Modular Equations in One Variable: How Many RSA-Encrypted Messages Does Eve Need to Know? |  |  | read |
| KN-LIT-6744 | Solving the Hidden Number Problem for CSIDH and CSURF via Automated Coppersmith |  |  | read |
| KN-LIT-6745 | Solving Underdetermined Systems of Multivariate Quadratic Equations revisited |  |  | read |
| KN-LIT-6746 | Some Easy Instances of Ideal-SVP and Implications on the Partial Vandermonde Knapsack Problem |  |  | read |
| KN-LIT-6747 | Some Mathematical Mysteries in Lattices |  |  | read |
| KN-LIT-6748 | Some Perspectives on Complexity-Based Cryptography |  |  | read |
| KN-LIT-6749 | Some Plausible Constructions of Double-Block-Length Hash Functions |  |  | read |
| KN-LIT-6750 | Some Recent Progress in Lattice-Based Cryptography |  |  | read |
| KN-LIT-6751 | Some RSA-based Encryption Schemes with Tight Security Reduction |  |  | read |
| KN-LIT-6752 | Some thoughts on security after ten years of qmail 1.0 |  |  | read |
| KN-LIT-6753 | Sometimes-Recurse Shuffle |  |  | read |
| KN-LIT-6754 | Somewhat Non-Committing Encryption and Efficient Adaptively Secure Oblivious Transfer? |  |  | read |
| KN-LIT-6755 | Somewhere Statistical Soundness, Post-Quantum Security, and SNARGs |  |  | read |
| KN-LIT-6756 | Soundness in the Public-Key Model |  |  | read |
| KN-LIT-6757 | SPA-resistant Scalar Multiplication on Hyperellipitc Curve Cryptosystems Combining |  |  | read |
| KN-LIT-6758 | Space Efficient Signature Schemes from the RSA Assumption |  |  | read |
| KN-LIT-6759 | SPARKs: Succinct Parallelizable Arguments of Knowledge |  |  | read |
| KN-LIT-6760 | Spartan and Bulletproofs are simulation-extractable (for free!) |  |  | read |
| KN-LIT-6761 | Spartan: Efficient and general-purpose zkSNARKs without trusted setup |  |  | read |
| KN-LIT-6762 | Speak Much, Remember Little: Cryptography in the Bounded Storage Model, Revisited? |  |  | read |
| KN-LIT-6763 | Specific versus General Assumptions in Cryptography |  |  | read |
| KN-LIT-6764 | Speed-Stacking: Fast Sublinear Zero-Knowledge Proofs for Disjunctions |  |  | read |
| KN-LIT-6765 | Speed-ups and time–memory trade-offs for tuple lattice sieving |  |  | read |
| KN-LIT-6766 | Speeding up point multiplication on hyperelliptic curves with efficiently-computable endomorphisms |  |  | read |
| KN-LIT-6767 | Speeding Up the Pollard Rho Method on Prime Fields |  |  | read |
| KN-LIT-6768 | Speeding up XTR |  |  | read |
| KN-LIT-6769 | SPHF-Friendly Non-Interactive Commitments |  |  | read |
| KN-LIT-6770 | SPHINCS: practical stateless hash-based signatures |  |  | read |
| KN-LIT-6771 | Sponge-based pseudo-random number generators |  |  | read |
| KN-LIT-6772 | spongent: A Lightweight Hash Function |  |  | read |
| KN-LIT-6773 | Sponges Resist Leakage: The Case of Authenticated Encryption |  |  | read |
| KN-LIT-6774 | Spooky Encryption and its Applications |  |  | read |
| KN-LIT-6775 | Spooky Interaction and its Discontents: Compilers for Succinct Two-Message Argument Systems |  |  | read |
| KN-LIT-6776 | SpOT-Light: Lightweight Private Set Intersection from Sparse OT Extension |  |  | read |
| KN-LIT-6777 | Spreading Alerts Quietly and the Subgroup Escape Problem |  |  | read |
| KN-LIT-6778 | SPRING: Fast Pseudorandom Functions from Rounded Ring Products |  |  | read |
| KN-LIT-6779 | SQISign: Compact Post-Quantum |  |  | read |
| KN-LIT-6780 | Square Span Programs with Applications to Succinct NIZK Arguments |  |  | read |
| KN-LIT-6781 | SQUASH - A New MAC With Provable Security Properties for Highly Constrained |  |  | read |
| KN-LIT-6782 | SSE and SSD: Page-Efficient Searchable Symmetric Encryption |  |  | read |
| KN-LIT-6783 | SSE Implementation of Multivariate PKCs on Modern x86 |  |  | read |
| KN-LIT-6784 | Stacked Garbling for Disjunctive Zero-Knowledge Proofs |  |  | read |
| KN-LIT-6785 | Stacked Garbling Garbled Circuit Proportional to Longest Execution Path |  |  | read |
| KN-LIT-6786 | Stacking Sigmas: A Framework to Compose Σ-Protocols for Disjunctions |  |  | read |
| KN-LIT-6787 | Stam’s collision resistance conjecture |  |  | read |
| KN-LIT-6788 | Standard Security Does Not Imply Indistinguishability Under Selective Opening |  |  | read |
| KN-LIT-6789 | Standard Security Does Not Imply Security Against Selective-Opening |  |  | read |
| KN-LIT-6790 | Starfish on Strike |  |  | read |
| KN-LIT-6791 | State Machine Replication under Changing |  |  | read |
| KN-LIT-6792 | State Separation for Code-Based Game-Playing Proofs Chris Brzuska1 , Antoine Delignat-Lavaud2 , Cédric Fournet2 |  |  | read |
| KN-LIT-6793 | Static-Memory-Hard Functions, and Modeling the Cost of Space vs. Time |  |  | read |
| KN-LIT-6794 | Statistical Concurrent Non-Malleable Zero Knowledge |  |  | read |
| KN-LIT-6795 | Statistical Concurrent Non-malleable Zero-knowledge from One-way Functions |  |  | read |
| KN-LIT-6796 | Statistical Decoding 2.0: Reducing Decoding to LPN |  |  | read |
| KN-LIT-6797 | Statistical Fault Attacks on Nonce-Based |  |  | read |
| KN-LIT-6798 | Statistical Ineffective Fault Attacks on |  |  | read |
| KN-LIT-6799 | Statistical Security in Two-Party Computation Revisited |  |  | read |
| KN-LIT-6800 | Statistical Tools Flavor Side-Channel |  |  | read |
| KN-LIT-6801 | Statistical Witness Indistinguishability (and more) in Two Messages |  |  | read |
| KN-LIT-6802 | Statistical ZAP Arguments |  |  | read |
| KN-LIT-6803 | Statistical ZAPR Arguments from Bilinear Maps |  |  | read |
| KN-LIT-6804 | Statistical Zaps and New Oblivious Transfer Protocols |  |  | read |
| KN-LIT-6805 | Statistical ZAPs from Group-Based Assumptions |  |  | read |
| KN-LIT-6806 | Statistical zero-knowledge proofs with efficient provers: lattice problems and more |  |  | read |
| KN-LIT-6807 | Statistical Zeroizing Attack: Cryptanalysis of Candidates of BP Obfuscation over GGH15 |  |  | read |
| KN-LIT-6808 | Statistically Sender-Private OT From LPN and Derandomization |  |  | read |
| KN-LIT-6809 | Stealing Keys from PCs using a Radio: Cheap Electromagnetic Attacks on Windowed Exponentiation |  |  | read |
| KN-LIT-6810 | Stealthy Dopant-Level Hardware Trojans ? |  |  | read |
| KN-LIT-6811 | Steel: Composable Hardware-based |  |  | read |
| KN-LIT-6812 | Steganography-Free Zero-Knowledge |  |  | read |
| KN-LIT-6813 | Stream ciphers: A Practical Solution for Efficient Homomorphic-Ciphertext Compression? |  |  | read |
| KN-LIT-6814 | Stream Ciphers: Dead or Alive? |  |  | read |
| KN-LIT-6815 | Streaming Authenticated Data Structures |  |  | read |
| KN-LIT-6816 | Streaming Functional Encryption |  |  | read |
| KN-LIT-6817 | Strengthening Digital Signatures via Randomized Hashing |  |  | read |
| KN-LIT-6818 | Strengthening the Known-Key Security Notion for Block Ciphers |  |  | read |
| KN-LIT-6819 | Strengthening Zero-Knowledge Protocols Using Signatures |  |  | read |
| KN-LIT-6820 | Stretching Groth-Sahai: NIZK Proofs of Partial Satisfiability |  |  | read |
| KN-LIT-6821 | Strong 8-bit Sboxes with Efficient Masking in Hardware Erik Boss1 , Vincent Grosso1 , Tim Güneysu2 , Gregor Leander1 |  |  | read |
| KN-LIT-6822 | Strong and Tight Security Guarantees against Integral Distinguishers |  |  | read |
| KN-LIT-6823 | Strong Asymmetric PAKE based on Trapdoor CKEM |  |  | read |
| KN-LIT-6824 | Strong Authentication for RFID Systems Using the AES Algorithm |  |  | read |
| KN-LIT-6825 | Strong Conditional Oblivious Transfer and Computing on Intervals |  |  | read |
| KN-LIT-6826 | Strong Hardness of Privacy from Weak Traitor Tracing? |  |  | read |
| KN-LIT-6827 | Strong Key-Insulated Signature Schemes |  |  | read |
| KN-LIT-6828 | Strong Security from Probabilistic Signature Schemes |  |  | read |
| KN-LIT-6829 | Stronger Leakage-Resilient and Non-Malleable Secret |  |  | read |
| KN-LIT-6830 | Stronger Lower Bounds for Online ORAM? |  |  | read |
| KN-LIT-6831 | Stronger Security and Constructions of Multi-Designated Verifier Signatures ? Ivan Damgård1 , Helene Haagh12 |  |  | read |
| KN-LIT-6832 | Stronger security bounds for permutations |  |  | read |
| KN-LIT-6833 | Stronger security bounds for Wegman-Carter-Shoup authenticators |  |  | read |
| KN-LIT-6834 | Stronger Security for Reusable Garbled Circuits |  |  | read |
| KN-LIT-6835 | Strongly Multiplicative and 3-Multiplicative Linear Secret Sharing Schemes |  |  | read |
| KN-LIT-6836 | Strongly Secure Authenticated Key Exchange from Factoring, Codes, and Lattices |  |  | read |
| KN-LIT-6837 | Strongly Secure Authenticated Key Exchange from Supersingular Isogenies |  |  | read |
| KN-LIT-6838 | Strongly Unforgeable Signatures Based on Computational Diffie-Hellman |  |  | read |
| KN-LIT-6839 | Strongly-Optimal Structure Preserving Signatures from Type II Pairings: |  |  | read |
| KN-LIT-6840 | Structural Evaluation by Generalized Integral Property |  |  | read |
| KN-LIT-6841 | Structural Evaluation of AES and Chosen-Key Distinguisher of 9-round AES-128 |  |  | read |
| KN-LIT-6842 | Structural Lattice Reduction: Generalized Worst-Case to Average-Case Reductions and Homomorphic Cryptosystems |  |  | read |
| KN-LIT-6843 | Structure vs. Hardness through the Obfuscation Lens ? |  |  | read |
| KN-LIT-6844 | Structure-Preserving and Re-randomizable |  |  | read |
| KN-LIT-6845 | Structure-Preserving Chosen-Ciphertext Security With Shorter Verifiable Ciphertexts |  |  | read |
| KN-LIT-6846 | Structure-Preserving Compilers from New Notions of Obfuscations |  |  | read |
| KN-LIT-6848 | Structure-Preserving Signatures and Commitments to Group Elements |  |  | read |
| KN-LIT-6849 | Structure-Preserving Signatures from Standard Assumptions, Revisited |  |  | read |
| KN-LIT-6850 | Structure-Preserving Signatures from Type II Pairings |  |  | read |
| KN-LIT-6851 | Structure-Preserving Signatures on Equivalence |  |  | read |
| KN-LIT-6852 | Structure-Preserving Signatures on Equivalence Classes From Standard Assumptions |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6853 | Structure-Preserving Smooth Projective Hashing |  |  | read |
| KN-LIT-6854 | Structured Encryption and Dynamic Leakage Suppression |  |  | read |
| KN-LIT-6855 | Structured Encryption and Leakage Suppression |  |  | read |
| KN-LIT-6856 | Sub-Linear Lattice-Based Zero-Knowledge Arguments for Arithmetic Circuits? |  |  | read |
| KN-LIT-6857 | Sub-linear Zero-Knowledge Argument for Correctness of a Shuffle |  |  | read |
| KN-LIT-6858 | Sub-Linear, Secure Comparison With Two Non-Colluding Parties |  |  | read |
| KN-LIT-6859 | Sublinear GMW-Style Compiler for MPC with Preprocessing |  |  | read |
| KN-LIT-6860 | Sublinear Secure Computation from New Assumptions |  |  | read |
| KN-LIT-6861 | Sublinear Zero-Knowledge Arguments for RAM Programs |  |  | read |
| KN-LIT-6862 | Sublinear-Communication Secure Multiparty Computation does not require FHE |  |  | read |
| KN-LIT-6863 | Sublinear-Round Byzantine Agreement under Corrupt Majority |  |  | read |
| KN-LIT-6864 | Submission number 132 to Asiacrypt 2016: DO NOT DISTRIBUTE! |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-6865 | Subquadratic SNARGs in the Random Oracle Model |  |  | read |
| KN-LIT-6866 | Subset-Restricted Random Walks for Pollard rho Method on Fpm ? |  |  | read |
| KN-LIT-6867 | Subspace LWE |  |  | read |
| KN-LIT-6868 | Substitution-permutation networks |  |  | read |
| KN-LIT-6869 | Subtractive Sets over Cyclotomic Rings Limits of Schnorr-like Arguments over Lattices |  |  | read |
| KN-LIT-6870 | Subvector Commitments with Application to Succinct Arguments |  |  | read |
| KN-LIT-6871 | Subversion-Resilient Public Key Encryption with Practical Watchdogs |  |  | read |
| KN-LIT-6872 | Subversion-zero-knowledge SNARKs |  |  | read |
| KN-LIT-6873 | Subvert KEM to Break DEM: Practical Algorithm-Substitution Attacks on Public-Key Encryption |  |  | read |
| KN-LIT-6874 | Success through confidence: Evaluating the effectiveness of a side-channel attack |  |  | read |
| KN-LIT-6875 | Successfully Attacking Masked AES Hardware Implementations |  |  | read |
| KN-LIT-6876 | Succinct and Adaptively Secure ABE for Arithmetic Branching Programs from k-Lin |  |  | read |
| KN-LIT-6877 | Succinct Arguments for RAM Programs via Projection Codes |  |  | read |
| KN-LIT-6878 | Succinct Arguments from Multi-Prover Interactive Proofs and their Efficiency Benefits |  |  | read |
| KN-LIT-6879 | Succinct Arguments in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-6880 | Succinct Classical Verification of Quantum Computation |  |  | read |
| KN-LIT-6881 | Succinct Diophantine-Satisfiability Arguments |  |  | read |
| KN-LIT-6882 | Succinct Functional Commitment for a Large Class of Arithmetic Circuits |  |  | read |
| KN-LIT-6883 | Succinct Interactive Oracle Proofs: Applications and Limitations |  |  | read |
| KN-LIT-6884 | Succinct LWE Sampling, Random Polynomials, and Obfuscation |  |  | read |
| KN-LIT-6885 | Succinct Malleable NIZKs and an Application to Compact Shuffles |  |  | read |
| KN-LIT-6886 | Succinct Non-Interactive Arguments via Linear Interactive Proofs? |  |  | read |
| KN-LIT-6887 | Succinct Non-Interactive Secure Computation |  |  | read |
| KN-LIT-6888 | Succinct Non-Interactive Zero Knowledge Arguments from Span Programs and Linear |  |  | read |
| KN-LIT-6889 | Succinct Spooky Free Compilers Are Not Black Box Sound |  |  | read |
| KN-LIT-6890 | Succinct Vector, Polynomial, and Functional Commitments from Lattices |  |  | read |
| KN-LIT-6891 | Succinct Verification of Compressed Sigma Protocols in the Updatable SRS setting |  |  | read |
| KN-LIT-6892 | Sufficient Conditions for Collision-Resistant Hashing |  |  | read |
| KN-LIT-6893 | Sufficient Conditions for Intractability over Black-Box Groups: Generic Lower Bounds for |  |  | read |
| KN-LIT-6894 | Sum-of-Squares Meets Program Obfuscation, Revisited |  |  | read |
| KN-LIT-6895 | Super Elliptic Curves |  |  | read |
| KN-LIT-6896 | Super-Linear Time-Memory Trade-Offs for Symmetric Encryption |  |  | read |
| KN-LIT-6897 | Super-Sbox Cryptanalysis: Improved Attacks for AES-like Permutations |  |  | read |
| KN-LIT-6898 | SuperPack: Dishonest Majority MPC with Constant Online Communication |  |  | read |
| KN-LIT-6899 | Superscalar Coprocessor for High-speed Curve-based Cryptography ? |  |  | read |
| KN-LIT-6900 | Supersingular Abelian Varieties in Cryptology |  |  | read |
| KN-LIT-6901 | Supersingular Curves in Cryptography |  |  | read |
| KN-LIT-6902 | Supersingular Curves You Can Trust |  |  | read |
| KN-LIT-6903 | Supersingular isogeny graphs and endomorphism rings: reductions and solutions? |  |  | read |
| KN-LIT-6904 | Supersingular Isogeny Graphs in Cryptography Kristin Lauter |  |  | read |
| KN-LIT-6905 | Supersingular reduction of elliptic curves introductory lecture at VaNTAGe series 10 26 October 2021 |  |  | read |
| KN-LIT-6906 | Sustained Space Complexity |  |  | read |
| KN-LIT-6907 | SWIFFT: A Modest Proposal for FFT Hashing? |  |  | read |
| KN-LIT-6908 | SwiftEC: Shallue–van de Woestijne |  |  | read |
| KN-LIT-6909 | Switching Blindings with a View Towards IDEA |  |  | read |
| KN-LIT-6910 | Switching Lemma for Bilinear Tests and Constant-size NIZK Proofs for Linear Subspaces |  |  | read |
| KN-LIT-6911 | Symbolic Encryption with Pseudorandom Keys? |  |  | read |
| KN-LIT-6912 | Symmetric Key Cryptography on Modern Graphics Hardware |  |  | read |
| KN-LIT-6913 | Symmetric Key Exchange with Full Forward |  |  | read |
| KN-LIT-6914 | Symmetric Primitives with Structured Secrets |  |  | read |
| KN-LIT-6915 | Symmetric Subgroup Membership Problems |  |  | read |
| KN-LIT-6916 | Symmetrically and Asymmetrically Hard Cryptography |  |  | read |
| KN-LIT-6917 | Symmetrized Summation Polynomials: Using Small Order Torsion Points to Speed up Elliptic Curve Index Calculus |  |  | read |
| KN-LIT-6918 | Symplectic Lattice Reduction and NTRU |  |  | read |
| KN-LIT-6919 | Synchronizable Fair Exchange |  |  | read |
| KN-LIT-6920 | Synchronized Aggregate Signatures from the RSA Assumption |  |  | read |
| KN-LIT-6921 | Synchronous Consensus with Optimal Asynchronous Fallback Guarantees |  |  | read |
| KN-LIT-6922 | Synchronous, with a Chance of Partition Tolerance |  |  | read |
| KN-LIT-6923 | Syndrome Decoding Estimator |  |  | read |
| KN-LIT-6924 | Syndrome Decoding in the Head: Shorter Signatures from Zero-Knowledge Proofs |  |  | read |
| KN-LIT-6925 | Tag Size Does Matter: Attacks and Proofs for the TLS Record Protocol |  |  | read |
| KN-LIT-6926 | Tagged Chameleon Hash from Lattices and Application to Redactable Blockchain |  |  | read |
| KN-LIT-6927 | Tagged One-Time Signatures: |  |  | read |
| KN-LIT-6928 | Tamper and Leakage Resilience in the Split-State Model |  |  | read |
| KN-LIT-6929 | Tamper Detection and Continuous Non-Malleable Codes |  |  | read |
| KN-LIT-6930 | Tamper Resilient Circuits: The Adversary at the Gates |  |  | read |
| KN-LIT-6931 | tardigrade: An Atomic Broadcast Protocol for Arbitrary Network Conditions |  |  | read |
| KN-LIT-6932 | TARDIS: A Foundation of Time-Lock Puzzles in UC Carsten Baum1 ? , Bernardo David2 ?? , Rafael Dowsley3 ? ? ? |  |  | read |
| KN-LIT-6933 | Targeted Lossy Functions and Applications Anonymous Submission |  |  | read |
| KN-LIT-6934 | Tate pairing implementation for hyperelliptic curves y 2 = xp − x + d |  |  | read |
| KN-LIT-6935 | Taylor Expansion of Maximum Likelihood Attacks for |  |  | read |
| KN-LIT-6935a1 | The Four Faces of Lifting for the Elliptic Curve Discrete Logarithm Problem | 2007 | 11th Workshop on Elliptic Curve Cryptography (ECC 2007), Shannon Institute, Dublin, 5-7 September 2007 (invited talk slides) | read |
| KN-LIT-6936 | TEC-Tree: A Low-Cost, Parallelizable Tree for |  |  | read |
| KN-LIT-6937 | Template Attacks in Principal Subspaces |  |  | read |
| KN-LIT-6938 | Templates as Master Keys |  |  | read |
| KN-LIT-6939 | Templates vs. Stochastic Methods –A Performance Analysis for Side Channel Cryptanalysis |  |  | read |
| KN-LIT-6940 | The 128-bit Blockcipher CLEFIA |  |  | read |
| KN-LIT-6941 | The 2-adic CM method for genus 2 curves with application to cryptography |  |  | read |
| KN-LIT-6942 | The Abe-Okamoto Partially Blind Signature Scheme Revisited |  |  | read |
| KN-LIT-6943 | The Additive Differential Probability of ARX |  |  | read |
| KN-LIT-6944 | The AGM-X0 (N ) Heegner point lifting |  |  | read |
| KN-LIT-6945 | The Algebraic Group Model and its Applications |  |  | read |
| KN-LIT-6946 | The ANF of the Composition of Addition and Multiplication mod 2n with a Boolean Function |  |  | read |
| KN-LIT-6947 | The Arithmetic Codex: |  |  | read |
| KN-LIT-6948 | The Billion-Mulmod-Per-Second PC |  |  | read |
| KN-LIT-6949 | The Bitcoin Backbone Protocol with Chains of Variable Difficulty? |  |  | read |
| KN-LIT-6950 | The Bitcoin Backbone Protocol: Analysis and Applications? |  |  | read |
| KN-LIT-6951 | The Broadcast Message Complexity of Secure Multiparty Computation |  |  | read |
| KN-LIT-6952 | The Carry Leakage on the Randomized Exponent Countermeasure |  |  | read |
| KN-LIT-6953 | The Complexity of |  |  | read |
| KN-LIT-6954 | The Conditional Correlation Attack: A Practical Attack on Bluetooth Encryption |  |  | read |
| KN-LIT-6955 | The Construction of Ambiguous Optimistic Fair Exchange from Designated Confirmer Signature without Random Oracles? |  |  | read |
| KN-LIT-6956 | The Cost of Adaptivity in Security Games on Graphs |  |  | read |
| KN-LIT-6957 | The Cost to Break SIKE: |  |  | read |
| KN-LIT-6958 | The Cramer-Shoup Encryption Scheme is Plaintext Aware in the Standard Model |  |  | read |
| KN-LIT-6959 | The Cramer-Shoup Strong-RSA |  |  | read |
| KN-LIT-6960 | The cryptoint library |  |  | read |
| KN-LIT-6961 | The Curious Case of Non-Interactive Commitments — On the Power of Black-Box vs. Non-Black-Box Use of Primitives |  |  | read |
| KN-LIT-6962 | The Curse of Small Domains: New Attacks on Format-Preserving Encryption |  |  | read |
| KN-LIT-6963 | The Degree of Regularity of HFE Systems |  |  | read |
| KN-LIT-6964 | The Direction of Updatable Encryption |  |  | read |
| KN-LIT-6965 | The Direction of Updatable Encryption does not |  |  | read |
| KN-LIT-6966 | The discrete logarithm problem on elliptic curves defined over Q |  |  | read |
| KN-LIT-6967 | The Distinction Between Fixed and Random Generators in Group-Based Assumptions? |  |  | read |
| KN-LIT-6968 | The Double Ratchet: Security Notions, Proofs, and Modularization for the Signal Protocol |  |  | read |
| KN-LIT-6969 | The EAX Mode of Operation |  |  | read |
| KN-LIT-6970 | The Elliptic Curve Discrete Logarithm Problem |  |  | read |
| KN-LIT-6971 | The error rate of algorithm analyses |  |  | read |
| KN-LIT-6972 | The Exact PRF Security of Truncation: Tight Bounds for Keyed Sponges and Truncated CBC |  |  | read |
| KN-LIT-6973 | The Exact PRF-Security of NMAC and HMAC |  |  | read |
| KN-LIT-6974 | The Exact Price for Unconditionally Secure Asymmetric Cryptography |  |  | read |
| KN-LIT-6975 | The Exact Round Complexity of Secure Computation? |  |  | read |
| KN-LIT-6976 | The Exchange Attack: How to Distinguish Six Rounds of AES with 288.2 chosen plaintexts |  |  | read |
| KN-LIT-6977 | The Fiat–Shamir Transformation in a Quantum World |  |  | read |
| KN-LIT-6978 | The first collision for full |  |  | read |
| KN-LIT-6979 | The First Thorough Side-Channel Hardware Trojan |  |  | read |
| KN-LIT-6980 | The Frequency Injection Attack on Ring-Oscillator-Based True Random Number Generators |  |  | read |
| KN-LIT-6981 | The Function Field Sieve in the Medium Prime Case |  |  | read |
| KN-LIT-6982 | The Future of Cryptography Bart Preneel |  |  | read |
| KN-LIT-6983 | The Gap Is Sensitive to Size of Preimages: Collapsing Property Doesn’t Go Beyond Quantum Collision-Resistance for Preimages Bounded Hash Functions |  |  | read |
| KN-LIT-6984 | The General Sieve Kernel and |  |  | read |
| KN-LIT-6985 | The Generalized Randomized Iterate and its Application to New Efficient Constructions of UOWHFs from Regular One-Way Functions |  |  | read |
| KN-LIT-6986 | The GGM Function Family is a Weakly One-Way Family of Functions |  |  | read |
| KN-LIT-6987 | The GHS Attack Revisited F. Hess |  |  | read |
| KN-LIT-6988 | The Glitch PUF: A New Delay-PUF Architecture Exploiting Glitch Shapes |  |  | read |
| KN-LIT-6989 | The Grindahl hash functions |  |  | read |
| KN-LIT-6990 | The Group of Signed Quadratic Residues and Applications |  |  | read |
| KN-LIT-6991 | The Hardness of Hensel Lifting: The Case of RSA and Discrete Logarithm |  |  | read |
| KN-LIT-6992 | The Hash Function Family LAKE |  |  | read |
| KN-LIT-6993 | The Hidden Number Problem with Small Unknown Multipliers: Cryptanalyzing MEGA in |  |  | read |
| KN-LIT-6994 | The Hierarchy of Key Evolving Signatures and a Characterization of Proxy Signatures |  |  | read |
| KN-LIT-6995 | The Ideal-Cipher Model, Revisited: An Uninstantiable Blockcipher-Based Hash Function |  |  | read |
| KN-LIT-6996 | The Impact of Carries on the Complexity of Collision Attacks on SHA-1 ? Florian Mendel?? , Norbert Pramstaller |  |  | read |
| KN-LIT-6997 | The Impact of Decryption Failures on the |  |  | read |
| KN-LIT-6998 | The Impossibility of Obfuscation with Auxiliary Input or a Universal Simulator |  |  | read |
| KN-LIT-6999 | The Indifferentiability of the Duplex and its Practical Applications |  |  | read |
| KN-LIT-7000 | The Insecurity of Esign in Practical Implementations |  |  | read |
| KN-LIT-7001 | The IPS Compiler: Optimizations, Variants and Concrete Efficiency? |  |  | read |
| KN-LIT-7002 | The Iterated Random Function Problem |  |  | read |
| KN-LIT-7003 | The Iterated Random Permutation Problem with Applications to Cascade Encryption |  |  | read |
| KN-LIT-7004 | The Joy of Cryptography |  |  | read |
| KN-LIT-7005 | The Kernel Matrix Diffie-Hellman Assumption? |  |  | read |
| KN-LIT-7006 | The Key-Dependent Attack on Block Ciphers? |  |  | read |
| KN-LIT-7007 | The Knowledge Tightness of Parallel Zero-Knowledge |  |  | read |
| KN-LIT-7008 | The Knowledge-of-Exponent Assumptions and 3-Round Zero-Knowledge Protocols |  |  | read |
| KN-LIT-7009 | The Layered Games Framework for Specifications and Analysis of Security Protocols |  |  | read |
| KN-LIT-7010 | The Leakage-Resilience Limit of a Computational Problem is Equal to its Unpredictability Entropy |  |  | read |
| KN-LIT-7011 | The LED Block Cipher |  |  | read |
| KN-LIT-7012 | The Locality of Searchable Symmetric Encryption |  |  | read |
| KN-LIT-7013 | The Magic of ELFs Mark Zhandry? |  |  | read |
| KN-LIT-7014 | The MALICIOUS Framework: Embedding Backdoors into Tweakable Block Ciphers |  |  | read |
| KN-LIT-7015 | The Measure-and-Reprogram Technique 2.0: |  |  | read |
| KN-LIT-7016 | The Memory-Tightness of Authenticated Encryption |  |  | read |
| KN-LIT-7017 | The Minimum Number of Cards in Practical Card-based Protocols? |  |  | read |
| KN-LIT-7018 | The Missing Difference Problem, and its Applications to Counter Mode Encryption |  |  | read |
| KN-LIT-7019 | The MMap Strikes Back: Obfuscation and New Multilinear Maps Immune to CLT13 Zeroizing Attacks? |  |  | read |
| KN-LIT-7020 | The Modular Inversion Hidden Number Problem |  |  | read |
| KN-LIT-7021 | The Moral Character of Cryptographic Work |  |  | read |
| KN-LIT-7022 | The More The Merrier: Reducing the Cost of Large Scale MPC |  |  | read |
| KN-LIT-7023 | The Mother of All Leakages: How to Simulate Noisy Leakages via Bounded Leakage (Almost) for Free |  |  | read |
| KN-LIT-7024 | The Multi-User Security of Authenticated Encryption: AES-GCM in TLS 1.3 |  |  | read |
| KN-LIT-7025 | The Multi-User Security of Double Encryption |  |  | read |
| KN-LIT-7026 | The Multiple Number Field Sieve with |  |  | read |
| KN-LIT-7027 | THE MULTIPLE-LATTICE NUMBER FIELD SIEVE |  |  | read |
| KN-LIT-7028 | The Nested Subset Differential Attack |  |  | read |
| KN-LIT-7029 | The Number Field Sieve in the Medium Prime Case |  |  | read |
| KN-LIT-7030 | The One-More Discrete Logarithm Assumption in the Generic Group Model |  |  | read |
| KN-LIT-7031 | The Order of Encryption and Authentication for Protecting Communications (Or: How Secure is SSL?)? |  |  | read |
| KN-LIT-7032 | The Outer Limits of RFID Security |  |  | read |
| KN-LIT-7033 | The Parallel Reversible Pebbling Game: Analyzing the Post-Quantum Security of iMHFs |  |  | read |
| KN-LIT-7034 | The PHOTON Family of Lightweight Hash Functions |  |  | read |
| KN-LIT-7035 | The Poly1305-AES message-authentication code |  |  | read |
| KN-LIT-7036 | The Power of Identification Schemes |  |  | read |
| KN-LIT-7037 | The Power of Negations in Cryptography? |  |  | read |
| KN-LIT-7038 | The Power of Proofs-of-Possession: Securing Multiparty Signatures against Rogue-Key Attacks |  |  | read |
| KN-LIT-7039 | The Power of Undirected Rewindings for Adaptive Security |  |  | read |
| KN-LIT-7040 | The Pre-Shared Key Modes of HPKE |  |  | read |
| KN-LIT-7041 | The preimage security of double-block-length compression functions |  |  | read |
| KN-LIT-7042 | The Price of Active Security in Cryptographic Protocols |  |  | read |
| KN-LIT-7043 | The Price of Verifiability: Lower Bounds for Verifiable Random Functions |  |  | read |
| KN-LIT-7044 | The Provable Security of Graph-Based |  |  | read |
| KN-LIT-7045 | The Pseudorandom Oracle Model and Ideal Obfuscation |  |  | read |
| KN-LIT-7046 | The Query-Complexity of Preprocessing Attacks |  |  | read |
| KN-LIT-7047 | The Random Oracle Model and the Ideal Cipher Model are Equivalent |  |  | read |
| KN-LIT-7048 | The Randomized Iterate, Revisited - Almost Linear Seed Length PRGs from A Broader Class of One-way Functions |  |  | read |
| KN-LIT-7049 | The randomized slicer for CVPP: sharper, faster, smaller, batchier |  |  | read |
| KN-LIT-7050 | The Rebound Attack: Cryptanalysis of Reduced Whirlpool and Grøstl |  |  | read |
| KN-LIT-7051 | The Related-Key Analysis of Feistel Constructions |  |  | read |
| KN-LIT-7052 | The Related-Key Security of Iterated Even–Mansour Ciphers |  |  | read |
| KN-LIT-7053 | The Relationship Between Idealized Models Under Computationally Bounded Adversaries ? |  |  | read |
| KN-LIT-7054 | The Relationship between Password-Authenticated Key Exchange and Other Cryptographic Primitives |  |  | read |
| KN-LIT-7055 | THE RELATIVE CLASS NUMBER ONE PROBLEM FOR |  |  | read |
| KN-LIT-7056 | The Resiliency of MPC with Low Interaction: The Benefit of Making Errors |  |  | read |
| KN-LIT-7057 | The Retracing Boomerang Attack |  |  | read |
| KN-LIT-7058 | The Return of the SDitH Carlos Aguilar-Melchor1 , Nicolas Gama1 , James Howe1  |  |  | read |
| KN-LIT-7059 | The Rise of Paillier: Homomorphic Secret |  |  | read |
| KN-LIT-7060 | The Round Complexity of Verifiable Secret Sharing Revisited |  |  | read |
| KN-LIT-7061 | The Round Complexity of Verifiable Secret Sharing: The Statistical Case |  |  | read |
| KN-LIT-7062 | The Round Functions of RIJNDAEL Generate the Alternating Group |  |  | read |
| KN-LIT-7063 | The Salsa20 family of stream ciphers |  |  | read |
| KN-LIT-7064 | The Sampling Twice Technique for the RSA-based Cryptosystems with Anonymity |  |  | read |
| KN-LIT-7065 | The security impact of a new cryptographic library |  |  | read |
| KN-LIT-7066 | The security of all bits using list decoding |  |  | read |
| KN-LIT-7067 | The Security of DSA and ECDSA Bypassing the Standard Elliptic Curve Certification Scheme |  |  | read |
| KN-LIT-7068 | The Security of Lazy Users in Out-of-Band Authentication |  |  | read |
| KN-LIT-7069 | The Security of Many-Round Luby-Rackoff |  |  | read |
| KN-LIT-7070 | The Security of the FDH Variant of Chaum’s Undeniable Signature Scheme |  |  | read |
| KN-LIT-7071 | The Security of Triple Encryption and a Framework for Code-Based Game-Playing Proofs |  |  | read |
| KN-LIT-7072 | The Semi-Generic Group Model and Applications to Pairing-Based Cryptography? |  |  | read |
| KN-LIT-7073 | The ship has sailed: the NIST Post-Quantum Cryptography ”competition” |  |  | read |
| KN-LIT-7074 | The Simeck Family of Lightweight Block Ciphers |  |  | read |
| KN-LIT-7075 | The SKINNY Family of Block |  |  | read |
| KN-LIT-7076 | The Software Performance of Authenticated-Encryption Modes |  |  | read |
| KN-LIT-7077 | The SPHINCS+ Signature Framework |  |  | read |
| KN-LIT-7078 | The Spirit of Beaver against Physical Attacks Oscar Reparaz1,2 ( ), Lauren De Meyer1 , Begül Bilgin1 , Victor Arribas1 |  |  | read |
| KN-LIT-7079 | The Sum Can Be Weaker Than Each Part |  |  | read |
| KN-LIT-7080 | The Summation-Truncation Hybrid: Reusing Discarded Bits for Free |  |  | read |
| KN-LIT-7081 | The t-wise Independence of Substitution-Permutation Networks |  |  | read |
| KN-LIT-7082 | The TinyTable protocol for 2-Party Secure Computation, or: Gate-scrambling Revisited |  |  | read |
| KN-LIT-7083 | The Torsion-Limit for Algebraic Function Fields and Its Application to Arithmetic Secret Sharing |  |  | read |
| KN-LIT-7084 | The Tower Number Field Sieve |  |  | read |
| KN-LIT-7085 | The Twin Diffie-Hellman Problem and Applications |  |  | read |
| KN-LIT-7086 | The Twist-AUgmented Technique for Key Exchange |  |  | read |
| KN-LIT-7087 | The Universal Composable |  |  | read |
| KN-LIT-7088 | The Usefulness of Sparsifiable Inputs: How to Avoid Subexponential iO |  |  | read |
| KN-LIT-7089 | The Wonderful World of Global Random Oracles Jan Camenisch1 , Manu Drijvers1,2 , Tommaso Gagliardoni1 |  |  | read |
| KN-LIT-7090 | The World is Not Enough: Another Look on Second-Order DPA François-Xavier |  |  | read |
| KN-LIT-7091 | The XL-Algorithm and a Conjecture from Commutative Algebra |  |  | read |
| KN-LIT-7092 | The “Backend Duplication” Method A Leakage-Proof Place-and-Route Strategy for ASICs |  |  | read |
| KN-LIT-7093 | Theory and Practice of a Leakage Resilient Masking Scheme |  |  | read |
| KN-LIT-7094 | There is Wisdom in Harnessing the Strengths of your Enemy: Customized Encoding to Thwart Side-Channel Attacks |  |  | read |
| KN-LIT-7095 | Think openly, build securely White paper: Quantum Computing Threat: An Overview of Post-Quantum |  |  | read |
| KN-LIT-7096 | Thinking Outside the Superbox |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7097 | Three Halves Make a Whole? Beating the Half-Gates Lower Bound for Garbled Circuits? |  |  | read |
| KN-LIT-7098 | Three Third Generation Attacks on the Format |  |  | read |
| KN-LIT-7099 | Three-Party ORAM for Secure Computation |  |  | read |
| KN-LIT-7100 | Three-Round Secure Multiparty Computation from Black-Box Two-Round Oblivious Transfer |  |  | read |
| KN-LIT-7101 | Three’s Compromised Too: Circular Insecurity for Any Cycle Length from (Ring-)LWE |  |  | read |
| KN-LIT-7102 | Threshold and Multi-Signature Schemes from Linear Hash Functions |  |  | read |
| KN-LIT-7103 | Threshold and Proactive Pseudo-Random Permutations |  |  | read |
| KN-LIT-7104 | Threshold and Revocation Cryptosystems via Extractable Hash Proofs |  |  | read |
| KN-LIT-7105 | Threshold Cryptosystems Based on Factoring |  |  | read |
| KN-LIT-7106 | Threshold Cryptosystems From Threshold Fully Homomorphic Encryption |  |  | read |
| KN-LIT-7107 | Threshold Cryptosystems Secure against Chosen-Ciphertext Attacks |  |  | read |
| KN-LIT-7108 | Threshold Decryption and Zero-Knowledge Proofs for Lattice-Based Cryptosystems |  |  | read |
| KN-LIT-7109 | Threshold Garbled Circuits and Ad Hoc Secure Computation |  |  | read |
| KN-LIT-7110 | Threshold Implementations of all |  |  | read |
| KN-LIT-7111 | Threshold Linear Secret Sharing to the Rescue of MPC-in-the-Head |  |  | read |
| KN-LIT-7112 | Threshold Linearly Homomorphic Encryption on Z/2k Z |  |  | read |
| KN-LIT-7113 | Threshold Password-Authenticated Key Exchange |  |  | read |
| KN-LIT-7114 | Threshold Private Set Intersection with Better Communication Complexity |  |  | read |
| KN-LIT-7115 | Threshold Ring Signatures and Applications to Ad-hoc Groups |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7116 | Threshold Ring Signatures: |  |  | read |
| KN-LIT-7117 | Threshold RSA for Dynamic and Ad-Hoc Groups |  |  | read |
| KN-LIT-7118 | Threshold Schemes from Isogeny Assumptions |  |  | read |
| KN-LIT-7119 | Threshold Schnorr with Stateless Deterministic Signing from Standard Assumptions |  |  | read |
| KN-LIT-7120 | Threshold Signatures with Private Accountability |  |  | read |
| KN-LIT-7121 | Threshold Signatures, Multisignatures and Blind Signatures Based on the Gap-Diffie-Hellman-Group Signature Scheme |  |  | read |
| KN-LIT-7122 | Threshold Structure-Preserving Signatures Elizabeth Crites1 , Markulf Kohlweiss1,2 , Bart Preneel3 |  |  | read |
| KN-LIT-7123 | Threshold Structure-Preserving Signatures: Strong and Adaptive |  |  | read |
| KN-LIT-7124 | Throughput vs. Area Trade-offs in High-Speed Architectures of Five Round |  |  | read |
| KN-LIT-7125 | Tight adaptive reprogramming in the QROM |  |  | read |
| KN-LIT-7126 | Tight Bounds for |  |  | read |
| KN-LIT-7127 | Tight Bounds on the Randomness Complexity of Secure Multiparty Computation |  |  | read |
| KN-LIT-7128 | Tight Leakage-Resilient CCA-Security from Quasi-Adaptive Hash Proof System |  |  | read |
| KN-LIT-7129 | Tight Preimage Resistance of the Sponge Construction |  |  | read |
| KN-LIT-7130 | Tight Private Circuits: Achieving Probing Security with the Least Refreshing |  |  | read |
| KN-LIT-7131 | Tight Proofs for Signature Schemes without Random Oracles |  |  | read |
| KN-LIT-7132 | Tight Proofs of Space and Replication |  |  | read |
| KN-LIT-7133 | Tight Security Bounds for Double-block Hash-then-Sum MACs |  |  | read |
| KN-LIT-7134 | Tight Security Bounds for Key-Alternating Ciphers |  |  | read |
| KN-LIT-7135 | Tight Security Bounds for Micali’s SNARGs |  |  | read |
| KN-LIT-7136 | Tight Security for Key-Alternating Ciphers with Correlated Sub-Keys |  |  | read |
| KN-LIT-7137 | Tight State-Restoration Soundness in the Algebraic Group Model |  |  | read |
| KN-LIT-7138 | Tight Time-Memory Trade-offs for Symmetric Encryption |  |  | read |
| KN-LIT-7139 | Tight Time-Space Lower Bounds for Finding |  |  | read |
| KN-LIT-7140 | Tight Tradeoffs in Searchable Symmetric Encryption |  |  | read |
| KN-LIT-7141 | Tighter proofs of CCA security in the quantum random oracle model |  |  | read |
| KN-LIT-7142 | Tighter QCCA-Secure Key Encapsulation Mechanism with Explicit Rejection in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-7143 | Tighter Reductions for Forward-Secure Signature Schemes |  |  | read |
| KN-LIT-7144 | Tighter Security for Generic Authenticated Key Exchange in the QROM |  |  | read |
| KN-LIT-7145 | Tighter Security for Schnorr Identification and Signatures: A High-Moment Forking Lemma for Σ-Protocols |  |  | read |
| KN-LIT-7146 | Tighter Security Proofs for GPV-IBE in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-7147 | Tighter, faster, simpler side-channel security evaluations beyond computing power |  |  | read |
| KN-LIT-7148 | Tightly Secure CCA-Secure Encryption without Pairings |  |  | read |
| KN-LIT-7149 | Tightly secure hierarchical identity-based encryption |  |  | read |
| KN-LIT-7150 | Tightly Secure IBE under Constant-size Master Public Key |  |  | read |
| KN-LIT-7151 | Tightly Secure Inner Product Functional Encryption: Multi-Input and Function-Hiding Constructions Junichi Tomida |  |  | read |
| KN-LIT-7152 | Tightly Secure Signatures and Public-Key Encryption |  |  | read |
| KN-LIT-7153 | Tightly SIM-SO-CCA Secure Public Key Encryption from Standard Assumptions |  |  | read |
| KN-LIT-7154 | Tightly-Secure Authenticated Key Exchange |  |  | read |
| KN-LIT-7155 | Tightly-Secure Authenticated Key Exchange, Revisited |  |  | read |
| KN-LIT-7156 | Tightly-Secure Key-Encapsulation Mechanism in the Quantum Random Oracle Model |  |  | read |
| KN-LIT-7157 | Tightly-Secure Signatures |  |  | read |
| KN-LIT-7158 | Tightly-Secure Signatures from Chameleon Hash Functions |  |  | read |
| KN-LIT-7159 | Tightly-Secure Signatures from Five-Move Identification Protocols |  |  | read |
| KN-LIT-7160 | Time space tradeoffs for attacks against one-way functions and PRGs |  |  | read |
| KN-LIT-7161 | Time- and Space-Efficient Arguments from Groups of Unknown Order |  |  | read |
| KN-LIT-7162 | Time-Area Optimized |  |  | read |
| KN-LIT-7163 | Time-Lock Puzzles in the Random Oracle Model |  |  | read |
| KN-LIT-7164 | Time-Memory Trade-Off Attacks on |  |  | read |
| KN-LIT-7165 | Time-memory Trade-offs for Near-collisions Gaëtan Leurent |  |  | read |
| KN-LIT-7166 | Time-Memory Tradeoff Attacks on the MTP Proof-of-Work Scheme? |  |  | read |
| KN-LIT-7167 | Time-Memory tradeoffs for large-weight syndrome decoding in ternary codes |  |  | read |
| KN-LIT-7168 | Time-Optimal Interactive Proofs for Circuit Evaluation |  |  | read |
| KN-LIT-7169 | Time-Space Tradeoffs and Short Collisions in Merkle-Damgård Hash Functions |  |  | read |
| KN-LIT-7170 | Time-Space Tradeoffs for Sponge Hashing: Attacks and Limitations for Short Collisions |  |  | read |
| KN-LIT-7171 | TNT: How to Tweak a Block Cipher |  |  | read |
| KN-LIT-7172 | To be incorporated into author’s High-speed cryptography book |  |  | read |
| KN-LIT-7173 | To Hash or Not to Hash Again? (In)differentiability |  |  | read |
| KN-LIT-7174 | To Infinity and Beyond: Combined Attack on ECC using Points of Low Order |  |  | read |
| KN-LIT-7175 | To Label, or Not To Label (in Generic Groups) |  |  | read |
| KN-LIT-7176 | Too Many Hints – When LLL Breaks LWE |  |  | read |
| KN-LIT-7177 | Tools for Simulating Features of Composite Order Bilinear Groups in the Prime Order Setting |  |  | read |
| KN-LIT-7178 | Topology-Hiding Computation |  |  | read |
| KN-LIT-7179 | Topology-Hiding Computation Beyond Logarithmic Diameter |  |  | read |
| KN-LIT-7180 | Topology-Hiding Computation Beyond Semi-Honest Adversaries |  |  | read |
| KN-LIT-7181 | Topology-Hiding Computation on All Graphs |  |  | read |
| KN-LIT-7182 | Tornado: Automatic Generation of Probing-Secure Masked Bitsliced Implementations |  |  | read |
| KN-LIT-7183 | TORSION SUBGROUPS OF ELLIPTIC CURVES OVER |  |  | read |
| KN-LIT-7184 | Torsion subgroups of elliptic curves over number fields Andrew V. Sutherland |  |  | read |
| KN-LIT-7185 | Torsion subgroups of elliptic curves over quadratic fields and a conjecture of Granville |  |  | read |
| KN-LIT-7186 | Torsion subgroups of rational elliptic curves over the compositum of all cubic fields |  |  | read |
| KN-LIT-7187 | Torus-Based Cryptography |  |  | read |
| KN-LIT-7188 | Total Break of the `-IC Signature Scheme |  |  | read |
| KN-LIT-7189 | Toward a Fully Secure Authenticated Encryption Scheme From a Pseudorandom Permutation |  |  | read |
| KN-LIT-7190 | Toward a rigorous variation of Coppersmith’s algorithm on three variables |  |  | read |
| KN-LIT-7191 | Toward Basing Fully Homomorphic Encryption on Worst-Case Hardness |  |  | read |
| KN-LIT-7192 | Toward Fine-Grained Blackbox Separations |  |  | read |
| KN-LIT-7193 | Toward Hierarchical Identity-Based Encryption |  |  | read |
| KN-LIT-7194 | Toward Practical Lattice-based Proof of Knowledge from Hint-MLWE Duhyeong Kim1[0000−0002−4766−3456] , Dongwon Lee2[0000−0002−2156−197X] |  |  | read |
| KN-LIT-7195 | Toward RSA-OAEP without Random Oracles |  |  | read |
| KN-LIT-7196 | Towards a Classification of Non-interactive Computational Assumptions in Cyclic Groups |  |  | read |
| KN-LIT-7197 | Towards a Game Theoretic View of Secure Computation |  |  | read |
| KN-LIT-7198 | Towards a Separation of Semantic and CCA Security for Public Key Encryption |  |  | read |
| KN-LIT-7199 | Towards a Simpler Lattice Gadget Toolkit |  |  | read |
| KN-LIT-7200 | Towards a Theory of Extractable Functions |  |  | read |
| KN-LIT-7201 | Towards a Unified Approach to Black-Box Constructions of Zero-Knowledge Proofs? |  |  | read |
| KN-LIT-7202 | Towards a unifying view of block cipher cryptanalysis |  |  | read |
| KN-LIT-7203 | Towards Accountability in CRS Generation |  |  | read |
| KN-LIT-7204 | Towards Black-Box Accountable Authority IBE with Short Ciphertexts and Private Keys |  |  | read |
| KN-LIT-7205 | Towards Breaking the Exponential Barrier for General Secret Sharing |  |  | read |
| KN-LIT-7206 | Towards Case-Optimized Hybrid Homomorphic Encryption Featuring the Elisabeth Stream Cipher |  |  | read |
| KN-LIT-7207 | Towards Characterizing Securely Computable Two-Party Randomized Functions |  |  | read |
| KN-LIT-7208 | Towards Classical Hardness of Module-LWE: The Linear Rank Case |  |  | read |
| KN-LIT-7209 | Towards Closing The Security Gap of Tweak-aNd-Tweak (TNT) |  |  | read |
| KN-LIT-7210 | Towards compressed permutation oracles |  |  | read |
| KN-LIT-7211 | Towards Easy Leakage Certification |  |  | read |
| KN-LIT-7212 | Towards Efficiency-Preserving Round Compression in MPC Do fewer rounds mean more computation? |  |  | read |
| KN-LIT-7213 | Towards Efficient Second-Order Power Analysis |  |  | read |
| KN-LIT-7214 | Towards faster polynomial-time lattice reduction |  |  | read |
| KN-LIT-7215 | Towards Green Cryptography: a Comparison of Lightweight Ciphers from the Energy Viewpoint Stéphanie Kerckhof, François Durvaux, Cédric Hocquet |  |  | read |
| KN-LIT-7216 | Towards KEM Unification |  |  | read |
| KN-LIT-7217 | Towards Micro-Architectural Leakage Simulators: Reverse Engineering |  |  | read |
| KN-LIT-7218 | Towards Non-Black-Box Lower Bounds in Cryptography ? |  |  | read |
| KN-LIT-7219 | Towards Non-Black-Box Separations of |  |  | read |
| KN-LIT-7220 | Towards Non-Interactive Witness Hiding |  |  | read |
| KN-LIT-7221 | Towards Non-Interactive Zero-Knowledge for NP from LWE |  |  | read |
| KN-LIT-7222 | Towards practical key exchange from ordinary isogeny graphs |  |  | read |
| KN-LIT-7223 | Towards Practical Multi-key TFHE: Parallelizable, Key-Compatible, Quasi-linear Complexity Hyesun Kwak |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7224 | Towards Practical Topology-Hiding Computation |  |  | read |
| KN-LIT-7225 | Towards Practical Whitebox Cryptography: |  |  | read |
| KN-LIT-7226 | Towards Privacy for Social Networks: A Zero-Knowledge Based Definition of Privacy |  |  | read |
| KN-LIT-7227 | Towards Robust Computation on Encrypted Data |  |  | read |
| KN-LIT-7228 | Towards Security Limits in Side-Channel Attacks (With an Application to Block Ciphers) |  |  | read |
| KN-LIT-7229 | Towards Sound Fresh Re-Keying with Hard (Physical) |  |  | read |
| KN-LIT-7230 | Towards Stream Ciphers for Efficient FHE with Low-Noise Ciphertexts |  |  | read |
| KN-LIT-7231 | Towards Super-Exponential Side-Channel Security with Efficient Leakage-Resilient PRFs |  |  | read |
| KN-LIT-7232 | Towards Tight Adaptive Security of Non-Interactive Key Exchange |  |  | read |
| KN-LIT-7233 | Towards Tight Random Probing Security Gaëtan |  |  | read |
| KN-LIT-7234 | Towards Tight Security Bounds for OMAC, XCBC and TMAC |  |  | read |
| KN-LIT-7235 | Towards Tight Security of Cascaded LRW2 |  |  | read |
| KN-LIT-7236 | Towards Tightly Secure Lattice Short Signature and Id-Based Encryption |  |  | read |
| KN-LIT-7237 | Towards Topology-Hiding Computation from Oblivious Transfer |  |  | read |
| KN-LIT-7238 | Towards Understanding the Known-Key Security of Block Ciphers |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7239 | Traceable Group Encryption |  |  | read |
| KN-LIT-7240 | Traceable PRFs: Full Collusion Resistance and Active Security |  |  | read |
| KN-LIT-7241 | Traceable Ring Signature |  |  | read |
| KN-LIT-7242 | Traceable Secret Sharing and Applications |  |  | read |
| KN-LIT-7243 | Traceable Signatures |  |  | read |
| KN-LIT-7244 | Tracing a Linear Subspace: Application to Linearly-Homomorphic Group Signatures |  |  | read |
| KN-LIT-7245 | Tracing Quantum State Distinguishers via Backtracking |  |  | read |
| KN-LIT-7246 | Tractable Rational Map Signature |  |  | read |
| KN-LIT-7247 | Tradeoff Cryptanalysis of Memory-Hard Functions |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7248 | Trading One-Wayness against Chosen-Ciphertext Security in Factoring-Based Encryption |  |  | read |
| KN-LIT-7249 | Trading Plaintext-Awareness for Simulatability to Achieve Chosen Ciphertext Security |  |  | read |
| KN-LIT-7250 | Traitor Tracing with Constant Transmission Rate |  |  | read |
| KN-LIT-7251 | Traitor Tracing with N 1/3 -size Ciphertexts and O(1)-size Keys from k-Lin |  |  | read |
| KN-LIT-7252 | Traitor-Tracing from LWE Made Simple and Attribute-Based |  |  | read |
| KN-LIT-7253 | Transciphering Framework for Approximate |  |  | read |
| KN-LIT-7254 | Transferable E-cash: A Cleaner Model and the First Practical Instantiation |  |  | read |
| KN-LIT-7255 | Transient-Steady Effect Attack on Block Ciphers |  |  | read |
| KN-LIT-7256 | Transitive Signatures based on Factoring and RSA |  |  | read |
| KN-LIT-7257 | Transparent Batchable Time-lock Puzzles and |  |  | read |
| KN-LIT-7258 | Transparent SNARKs from DARK Compilers |  |  | read |
| KN-LIT-7259 | Trapdoor Functions from the Computational Diffie-Hellman Assumption? |  |  | read |
| KN-LIT-7260 | Trapdoor Hash Functions and Their Applications 1 2 |  |  | read |
| KN-LIT-7262 | Trapdoors for Lattices: Simpler, Tighter, Faster, Smaller |  |  | read |
| KN-LIT-7263 | Treading the Impossible: A Tour of Set-Up Assumptions for Obtaining Universally |  |  | read |
| KN-LIT-7264 | TreePIR: Sublinear-Time and Polylog-Bandwidth Private Information Retrieval from DDH |  |  | read |
| KN-LIT-7265 | Tri-State Circuits A Circuit Model that Captures RAM |  |  | read |
| KN-LIT-7266 | Triangular modular curves of low genus |  |  | read |
| KN-LIT-7267 | TRIANGULAR MODULAR CURVES OF SMALL GENUS |  |  | read |
| KN-LIT-7268 | Trick or Tweak: On the (In)security of OTR’s Tweaks |  |  | read |
| KN-LIT-7269 | Triply Adaptive UC NIZK |  |  | read |
| KN-LIT-7270 | TriviA: A Fast and Secure Authenticated Encryption Scheme |  |  | read |
| KN-LIT-7271 | Trojan Side-Channels: Lightweight Hardware Trojans through Side-Channel Engineering Lang Lin , Markus Kasper , Tim Güneysu |  |  | read |
| KN-LIT-7272 | Trojan-Resilience without Cryptography |  |  | read |
| KN-LIT-7273 | Truly Efficient String Oblivious Transfer Using Resettable Tamper-Proof Tokens |  |  | read |
| KN-LIT-7274 | TTS: High-Speed Signatures on a Low-Cost Smart Card |  |  | read |
| KN-LIT-7275 | Turing: a Fast Stream Cipher |  |  | read |
| KN-LIT-7276 | Tweakable Block Ciphers |  |  | read |
| KN-LIT-7277 | Tweakable Block Ciphers Secure Beyond the Birthday Bound in the Ideal Cipher Model |  |  | read |
| KN-LIT-7278 | Tweakable Blockciphers with Beyond Birthday-Bound Security |  |  | read |
| KN-LIT-7279 | Tweaking Even-Mansour Ciphers |  |  | read |
| KN-LIT-7280 | Tweaking the Asymmetry of Asymmetric-Key Cryptography on Lattices: KEMs and Signatures of Smaller Sizes |  |  | read |
| KN-LIT-7281 | Tweaks and Keys for Block Ciphers: the TWEAKEY Framework |  |  | read |
| KN-LIT-7282 | TweetNaCl: A crypto library in 100 tweets |  |  | read |
| KN-LIT-7283 | Twin Column Parity Mixers and Gaston |  |  | read |
| KN-LIT-7284 | Twisted Edwards Curves |  |  | read |
| KN-LIT-7285 | Twisted Edwards Curves Revisited |  |  | read |
| KN-LIT-7286 | Twisted Hessian curves |  |  | read |
| KN-LIT-7287 | Twisted Polynomials and Forgery Attacks on GCM? |  |  | read |
| KN-LIT-7288 | Twisted-PHS: Using the Product Formula to Solve Approx-SVP in Ideal Lattices |  |  | read |
| KN-LIT-7289 | TWISTS OF THE BURKHARDT QUARTIC THREEFOLD |  |  | read |
| KN-LIT-7290 | Two attacks on rank metric code-based schemes: |  |  | read |
| KN-LIT-7291 | TWO GRUMPY GIANTS AND A BABY |  |  | read |
| KN-LIT-7292 | Two Halves Make a Whole Reducing Data Transfer in Garbled Circuits using Half Gates |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7293 | Two Is A Crowd? A Black-Box Separation Of |  |  | read |
| KN-LIT-7294 | Two Linear Distinguishing Attacks on VMPC and RC4A and Weakness of RC4 Family of Stream Ciphers |  |  | read |
| KN-LIT-7295 | Two New Techniques of Side-Channel Cryptanalysis |  |  | read |
| KN-LIT-7296 | Two Power Analysis Attacks against One-Mask Methods |  |  | read |
| KN-LIT-7297 | Two Provers in Isolation |  |  | read |
| KN-LIT-7298 | Two-Message Witness Indistinguishability and Secure Computation in the |  |  | read |
| KN-LIT-7299 | Two-Message, Oblivious Evaluation of Cryptographic Functionalities |  |  | read |
| KN-LIT-7300 | Two-output Secure Computation With Malicious Adversaries |  |  | read |
| KN-LIT-7301 | Two-Party Adaptor Signatures |  |  | read |
| KN-LIT-7302 | Two-Party Computing with Encrypted Data |  |  | read |
| KN-LIT-7303 | Two-Party ECDSA from Hash |  |  | read |
| KN-LIT-7304 | Two-Party Generation of DSA Signatures |  |  | read |
| KN-LIT-7305 | Two-Pass Authenticated Key Exchange with |  |  | read |
| KN-LIT-7306 | Two-Round Adaptively Secure MPC from |  |  | read |
| KN-LIT-7307 | Two-Round Adaptively Secure MPC from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-7308 | Two-Round Adaptively Secure Multiparty Computation from Standard Assumptions |  |  | read |
| KN-LIT-7309 | Two-Round Concurrent 2PC from Sub-Exponential LWE |  |  | read |
| KN-LIT-7310 | Two-Round Maliciously Secure Computation with Super-Polynomial Simulation |  |  | read |
| KN-LIT-7311 | Two-Round Man-in-the-Middle Security from LPN |  |  | read |
| KN-LIT-7312 | Two-Round MPC without Round Collapsing Revisited – Towards Efficient Malicious Protocols |  |  | read |
| KN-LIT-7313 | Two-Round MPC: Information-Theoretic and Black-Box |  |  | read |
| KN-LIT-7314 | Two-Round Multiparty Secure Computation from Minimal Assumptions? |  |  | read |
| KN-LIT-7315 | Two-Round Multiparty Secure Computation Minimizing Public Key Operations ? |  |  | read |
| KN-LIT-7316 | Two-round n-out-of-n and Multi-Signatures and Trapdoor Commitment from Lattices |  |  | read |
| KN-LIT-7317 | Two-Round Oblivious Linear Evaluation from Learning with Errors |  |  | read |
| KN-LIT-7318 | Two-Round Oblivious Transfer from CDH or LPN |  |  | read |
| KN-LIT-7319 | Two-Round PAKE from Approximate SPH and Instantiations from Lattices |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7320 | Two-round Secure MPC from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-7321 | Two-Round Stateless Deterministic |  |  | read |
| KN-LIT-7322 | Two-Round Trip Schnorr Multi-Signatures via Delinearized Witnesses |  |  | read |
| KN-LIT-7323 | Two-server Distributed ORAM with Sublinear |  |  | read |
| KN-LIT-7324 | Two-Server Password-Authenticated Secret Sharing UC-Secure Against Transient Corruptions |  |  | read |
| KN-LIT-7325 | Two-Sided Malicious Security for Private Intersection-Sum with Cardinality |  |  | read |
| KN-LIT-7326 | Two-Tier Signatures, Strongly Unforgeable Signatures, and Fiat-Shamir without Random Oracles |  |  | read |
| KN-LIT-7327 | TWORAM: Efficient Oblivious RAM in Two Rounds with Applications to Searchable Encryption |  |  | read |
| KN-LIT-7328 | Type 2 Structure-Preserving Signature Schemes Revisited |  |  | read |
| KN-LIT-7329 | Type-II Optimal Polynomial Bases |  |  | read |
| KN-LIT-7330 | UC Commitments for Modular Protocol Design and |  |  | read |
| KN-LIT-7331 | UC-Secure Multiparty Computation from One-Way Functions using Stateless Tokens |  |  | read |
| KN-LIT-7332 | Ultra High Performance ECC over NIST Primes on Commercial FPGAs |  |  | read |
| KN-LIT-7333 | UNAF: A Special Set of Additive Differences with Application to the Differential Analysis of ARX |  |  | read |
| KN-LIT-7334 | Unaligned Rebound Attack: Application to Keccak |  |  | read |
| KN-LIT-7335 | Unbelievable Security Matching AES security using public key systems |  |  | read |
| KN-LIT-7336 | Unbiased Random Sequences from Quasigroup String Transformations |  |  | read |
| KN-LIT-7337 | Unbounded ABE via Bilinear Entropy Expansion, Revisited |  |  | read |
| KN-LIT-7338 | Unbounded Dynamic Predicate Compositions in ABE from Standard Assumptions |  |  | read |
| KN-LIT-7339 | Unbounded Dynamic Predicate Compositions in Attribute-Based Encryption |  |  | read |
| KN-LIT-7340 | Unbounded HIBE and Attribute-Based Encryption |  |  | read |
| KN-LIT-7341 | Unbounded HIBE with Tight Security |  |  | read |
| KN-LIT-7342 | Unbounded Inner Product Functional Encryption from Bilinear Maps |  |  | read |
| KN-LIT-7343 | Unbounded Multi-Party Computation from Learning with Errors |  |  | read |
| KN-LIT-7344 | Unbounded Quadratic Functional Encryption and More from Pairings |  |  | read |
| KN-LIT-7345 | Unclonable Encryption, Revisited |  |  | read |
| KN-LIT-7346 | Unclonable Polymers and |  |  | read |
| KN-LIT-7347 | Unconditional and Composable Security Using a Single Stateful Tamper-Proof Hardware Token |  |  | read |
| KN-LIT-7348 | Unconditional Authenticity and Privacy from an Arbitrarily Weak Secret |  |  | read |
| KN-LIT-7349 | Unconditional Byzantine Agreement and Multi-Party Computation Secure Against Dishonest Minorities from Scratch |  |  | read |
| KN-LIT-7350 | Unconditional Characterizations of Non-Interactive Zero-Knowledge |  |  | read |
| KN-LIT-7351 | Unconditionally Secure and Universally Composable Commitments from Physical Assumptions |  |  | read |
| KN-LIT-7352 | Unconditionally Secure Anonymous Encryption and Group Authentication? |  |  | read |
| KN-LIT-7353 | Unconditionally Secure Computation Against Low-Complexity Leakage |  |  | read |
| KN-LIT-7354 | Unconditionally Secure Computation with Reduced Interaction |  |  | read |
| KN-LIT-7355 | Unconditionally Secure Multiparty Computation for Symmetric Functions with Low Bottleneck Complexity |  |  | read |
| KN-LIT-7356 | Unconditionally Secure NIZK in the Fine-Grained Setting |  |  | read |
| KN-LIT-7357 | Unconditionally-Secure Robust Secret Sharing with Compact Shares |  |  | read |
| KN-LIT-7358 | Uncovering Algebraic Structures in the MPC Landscape |  |  | read |
| KN-LIT-7359 | Undeniable Signatures Based on Characters: How to Sign with One Bit |  |  | read |
| KN-LIT-7360 | Understanding and Constructing AKE via Double-key Key Encapsulation Mechanism |  |  | read |
| KN-LIT-7361 | Understanding binary-Goppa decoding |  |  | read |
| KN-LIT-7362 | Understanding brute force |  |  | read |
| KN-LIT-7363 | Unforgeable Quantum Encryption |  |  | read |
| KN-LIT-7364 | Unidirectional Chosen-Ciphertext Secure Proxy Re-Encryption |  |  | read |
| KN-LIT-7365 | Unidirectional Updatable Encryption and Proxy Re-encryption from DDH |  |  | read |
| KN-LIT-7366 | Unified and Optimized Linear Collision Attacks and Their Application in a Non-Profiled Setting |  |  | read |
| KN-LIT-7367 | Unified Point Addition Formulæ and Side-Channel Attacks |  |  | read |
| KN-LIT-7368 | Unified, Minimal and Selectively Randomizable Structure-Preserving Signatures |  |  | read |
| KN-LIT-7369 | Unifying Classical and Quantum Key Distillation Matthias Christandl1 , Artur Ekert1,2 , Michal Horodecki3 , Pawel Horodecki4 |  |  | read |
| KN-LIT-7370 | Unifying computational entropies via Kullback–Leibler divergence |  |  | read |
| KN-LIT-7371 | Unifying Freedom and Separation for Tight Probing-Secure Composition |  |  | read |
| KN-LIT-7372 | Unifying Leakage Models on a Rényi Day |  |  | read |
| KN-LIT-7373 | Unifying Leakage Models: from Probing Attacks to Noisy Leakage |  |  | read |
| KN-LIT-7374 | Unifying Presampling via Concentration Bounds |  |  | read |
| KN-LIT-7375 | Unique Signatures and Verifiable Random Functions from the DH-DDH Separation |  |  | read |
| KN-LIT-7376 | Uniqueness Enhancement of PUF Responses Based on the Locations of Random Outputting |  |  | read |
| KN-LIT-7377 | Uniqueness is a Different Story: Impossibility of Verifiable Random Functions from Trapdoor Permutations |  |  | read |
| KN-LIT-7378 | Universal Amplification of KDM Security: From 1-Key Circular to Multi-Key KDM |  |  | read |
| KN-LIT-7379 | Universal Composition with Joint State |  |  | read |
| KN-LIT-7380 | Universal Composition with Responsive Environments |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7381 | Universal Constructions and Robust Combiners for Indistinguishability Obfuscation and Witness Encryption |  |  | read |
| KN-LIT-7382 | Universal Designated Verifier Signature Proof (or How to Efficiently Prove Knowledge of a Signature) |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7383 | Universal Designated-Verifier Signatures |  |  | read |
| KN-LIT-7384 | Universal Forgery and Key Recovery Attacks on ELmD Authenticated Encryption Algorithm |  |  | read |
| KN-LIT-7385 | Universal Hash Proofs and a Paradigm for Adaptive Chosen |  |  | read |
| KN-LIT-7386 | Universal Hash Proofs and a Paradigm for Adaptive Chosen Ciphertext Secure Public-Key Encryption |  |  | read |
| KN-LIT-7387 | Universal One-Way |  |  | read |
| KN-LIT-7388 | Universal Padding Schemes for RSA |  |  | read |
| KN-LIT-7389 | Universal Proxy Re-Encryption |  |  | read |
| KN-LIT-7390 | Universal Reductions: Reductions Relative to Stateful Oracles |  |  | read |
| KN-LIT-7391 | Universal Ring Signatures in the Standard Model |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7392 | Universal Samplers with Fast Verification |  |  | read |
| KN-LIT-7393 | Universally Anonymizable Public-Key Encryption |  |  | read |
| KN-LIT-7394 | Universally Composable |  |  | read |
| KN-LIT-7395 | Universally Composable Adaptive Oblivious Transfer |  |  | read |
| KN-LIT-7396 | Universally Composable Auditable Surveillance Valerie Fetzer1,4[0009−0001−8157−9768] , Michael Klooß2 ?[0000−0003−3466−0675] |  |  | read |
| KN-LIT-7397 | Universally Composable Authentication and Key-Exchange with Global PKI |  |  | read |
| KN-LIT-7398 | Universally Composable Commitments |  |  | read |
| KN-LIT-7399 | Universally Composable Efficient Multiparty Computation from Threshold Homomorphic Encryption |  |  | read |
| KN-LIT-7400 | Universally Composable Multi-Party Computation with an Unreliable Common Reference String |  |  | read |
| KN-LIT-7401 | Universally Composable Multiparty Computation with Partially Isolated Parties |  |  | read |
| KN-LIT-7402 | Universally Composable Password-Based Key Exchange |  |  | read |
| KN-LIT-7403 | Universally Composable Privacy Amplification Against Quantum Adversaries |  |  | read |
| KN-LIT-7404 | Universally Composable Relaxed |  |  | read |
| KN-LIT-7405 | Universally Composable Secure Computation with (Malicious) Physically Uncloneable Functions |  |  | read |
| KN-LIT-7406 | Universally Composable Secure Computation with Corrupted Tokens |  |  | read |
| KN-LIT-7407 | Universally Composable Security with Global Setup |  |  | read |
| KN-LIT-7408 | Universally Composable Subversion-Resilient Cryptography |  |  | read |
| KN-LIT-7409 | Universally Composable Symbolic Analysis for Two-Party Protocols based on Homomorphic Encryption |  |  | read |
| KN-LIT-7410 | Universally Composable Symbolic Analysis of |  |  | read |
| KN-LIT-7411 | Universally Composable Σ-protocols in the Global Random-Oracle Model |  |  | read |
| KN-LIT-7412 | Universally Convertible Directed Signatures |  |  | read |
| KN-LIT-7413 | Universally-Composable Two-Party Computation in Two Rounds |  |  | read |
| KN-LIT-7415 | Unified View for Notions of Bit Security |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7416 | Unknown-Input Attacks in the Parallel Setting: Improving the Security of the CHES 2012 Leakage-Resilient PRF |  |  | read |
| KN-LIT-7417 | Unlinkability of Sanitizable Signatures |  |  | read |
| KN-LIT-7418 | Unprovable Security of Perfect NIZK and Non-interactive Non-malleable Commitments |  |  | read |
| KN-LIT-7419 | Untagging Tor: A Formal Treatment of Onion Encryption |  |  | read |
| KN-LIT-7420 | Untraceable Fair Network Payment Protocols with Off-line TTP |  |  | read |
| KN-LIT-7421 | Updatable and Universal Common Reference Strings with Applications to zk-SNARKs |  |  | read |
| KN-LIT-7422 | Updatable Encryption with Post-Compromise Security |  |  | read |
| KN-LIT-7423 | Updatable Policy-Compliant Signatures Christian Badertscher1 , Monosij Maitra2,3 |  |  | read |
| KN-LIT-7424 | Updatable Public Key Encryption in the Standard Model |  |  | read |
| KN-LIT-7425 | Updatable Signatures and Message |  |  | read |
| KN-LIT-7426 | Updatable Zero-Knowledge Databases |  |  | read |
| KN-LIT-7427 | Updatable, Aggregatable, Succinct Mercurial Vector Commitment from Lattice Hongxiao Wang1[0009−0005−2983−7239] , Siu-Ming Yiu1( )[0000−0002−3975−8500] |  |  | read |
| KN-LIT-7428 | Updateable Inner Product Argument with |  |  | read |
| KN-LIT-7429 | Upgrading to Functional Encryption |  |  | read |
| KN-LIT-7430 | Upper and Lower Bounds for Continuous Non-Malleable Codes |  |  | read |
| KN-LIT-7431 | Upper Bounds on Algebraic Immunity of Boolean Power Functions |  |  | read |
| KN-LIT-7432 | Upper Bounds on the Communication Complexity of Optimally Resilient Cryptographic Multiparty Computation |  |  | read |
| KN-LIT-7433 | Upslices, Downslices, and Secret-Sharing with Complexity of 1.5n |  |  | read |
| KN-LIT-7434 | Usable assembly language for GPUs: a success story Daniel J. Bernstein , Hsieh-Chung Chen , Chen-Mou Cheng , Tanja Lange |  |  | read |
| KN-LIT-7435 | Using an RSA Accelerator for Modular Inversion |  |  | read |
| KN-LIT-7436 | Using Bleichenbacher’s Solution to the Hidden |  |  | read |
| KN-LIT-7437 | Using Equivalence Classes to Accelerate Solving the Discrete Logarithm Problem in a Short Interval |  |  | read |
| KN-LIT-7438 | Using Indistinguishability Obfuscation via UCEs |  |  | read |
| KN-LIT-7439 | Using Subspace-Based Template Attacks |  |  | read |
| KN-LIT-7440 | Valiant’s Universal Circuits Revisited: an |  |  | read |
| KN-LIT-7441 | Validation of Elliptic Curve Public Keys Adrian Antipa1 , Daniel Brown1 , Alfred Menezes2 |  |  | read |
| KN-LIT-7442 | Variants of Waters’ Dual System Primitives |  |  | read |
| KN-LIT-7443 | Vector and Functional Commitments from Lattices |  |  | read |
| KN-LIT-7444 | Vector Commitments and their Applications |  |  | read |
| KN-LIT-7445 | Vector Commitments over Rings and Compressed Σ-Protocols |  |  | read |
| KN-LIT-7446 | Vector Commitments With Proofs of Smallness: |  |  | read |
| KN-LIT-7447 | Vectorial functions for symmetric cryptography: immersion and insights |  |  | read |
| KN-LIT-7448 | Verifiable Capacity-bound Functions: A New Primitive from Kolmogorov Complexity (Revisiting space-based security in the adaptive setting) |  |  | read |
| KN-LIT-7449 | Verifiable Delay Functions from Supersingular Isogenies and Pairings |  |  | read |
| KN-LIT-7450 | Verifiable Elections That Scale for Free |  |  | read |
| KN-LIT-7451 | Verifiable Functional Encryption Saikrishna Badrinarayanan? , Vipul Goyal ?? |  |  | read |
| KN-LIT-7452 | Verifiable Homomorphic Oblivious Transfer and Private Equality Test |  |  | read |
| KN-LIT-7453 | Verifiable Inner Product Encryption Scheme? |  | IACR Cryptology ePrint Archive | read |
| KN-LIT-7454 | Verifiable Oblivious Storage |  |  | read |
| KN-LIT-7455 | Verifiable Predicate Encryption and |  |  | read |
| KN-LIT-7456 | Verifiable Private Information Retrieval |  |  | read |
| KN-LIT-7457 | Verifiable Random Functions from Identity-based Key Encapsulation? |  |  | read |
| KN-LIT-7458 | Verifiable Random Functions from Standard Assumptions |  |  | read |
| KN-LIT-7459 | Verifiable Random Functions from Weaker Assumptions |  |  | read |
| KN-LIT-7460 | Verifiable Random Functions with Optimal Tightness? |  |  | read |
| KN-LIT-7461 | Verifiable Registration-Based Encryption |  |  | read |
| KN-LIT-7462 | Verifiable Relation Sharing and Multi-Verifier Zero-Knowledge in Two Rounds: Trading NIZKs with Honest Majority |  |  | read |
| KN-LIT-7463 | Verifiable Rotation of Homomorphic Encryptions |  |  | read |
| KN-LIT-7464 | Verifiable Set Operations over Outsourced Databases? |  |  | read |
| KN-LIT-7465 | Verifiable Shuffle of Large Size Ciphertexts |  |  | read |
| KN-LIT-7466 | Verifiable side-channel security of cryptographic implementations: constant-time MEE-CBC |  |  | read |
| KN-LIT-7467 | Verifiably Encrypted Signatures with Short Keys based on the Decisional Linear Problem and Obfuscation for Encrypted VES |  |  | read |
| KN-LIT-7468 | Verifiably Secure Devices |  |  | read |
| KN-LIT-7469 | Verified Proofs of Higher-Order Masking Gilles Barthe1 , Sonia Belaı̈d2 , François Dupressoir1 , Pierre-Alain Fouque3 |  |  | read |
| KN-LIT-7470 | Verifier-Local Revocation Group Signature Schemes with Backward Unlinkability from Bilinear Maps |  |  | read |
| KN-LIT-7471 | Verifier-on-a-Leash: new schemes for verifiable delegated quantum computation, with quasilinear resources |  |  | read |
| KN-LIT-7472 | Very High Order Masking: Efficient |  |  | read |
| KN-LIT-7473 | Very-efficient simulatable flipping of many coins into a well? |  |  | read |
| KN-LIT-7474 | Virtual Black-Box Obfuscation for All Circuits via Generic Graded Encoding |  |  | read |
| KN-LIT-7475 | Virtual Grey-Boxes Beyond Obfuscation: A Statistical Security Notion for Cryptographic Agents |  |  | read |
| KN-LIT-7476 | Visualizing area-time tradeoffs for |  |  | read |
| KN-LIT-7477 | Visualizing size-security tradeoffs for lattice-based encryption |  |  | read |
| KN-LIT-7478 | VMPC One-Way Function and Stream Cipher |  |  | read |
| KN-LIT-7479 | VOLE-PSI: Fast OPRF and Circuit-PSI from Vector-OLE |  |  | read |
| KN-LIT-7480 | VSH, an Efficient and Provable Collision-Resistant Hash Function |  |  | read |
| KN-LIT-7481 | VSS from Distributed ZK Proofs and Applications |  |  | read |
| KN-LIT-7482 | Vulnerability of Nonlinear Filter Generators Based on Linear Finite State Machines |  |  | read |
| KN-LIT-7483 | Watermarking PRFs against Quantum Adversaries |  |  | read |
| KN-LIT-7484 | Watermarking PRFs under Standard Assumptions: Public Marking and Security with Extraction Queries |  |  | read |
| KN-LIT-7485 | Watermarking Public-Key |  |  | read |
| KN-LIT-7486 | Waters Signatures with Optimal Security Reduction |  |  | read |
| KN-LIT-7487 | Wave: A New Family of Trapdoor One-Way Preimage Sampleable Functions Based on Codes? |  |  | read |
| KN-LIT-7488 | We Are on the Same Side. Alternative Sieving Strategies for the Number Field Sieve Charles Bouillaguet1[0000−0001−9416−6244] |  |  | read |
| KN-LIT-7489 | Weak instances of class group action based cryptography via self-pairings |  |  | read |
| KN-LIT-7490 | Weak instances of ECDLP With a focus on finite local rings |  |  | read |
| KN-LIT-7491 | Weak Key Authenticity and the Computational Completeness of Formal Encryption |  |  | read |
| KN-LIT-7492 | Weak Verifiable Random Functions Zvika Brakerski1 , Shafi Goldwasser1,2,? |  |  | read |
| KN-LIT-7493 | Weak Zero-Knowledge via the Goldreich-Levin Theorem |  |  | read |
| KN-LIT-7494 | Weakening Assumptions for Publicly-Verifiable Deletion |  |  | read |
| KN-LIT-7495 | Weakly Extractable One-Way Functions |  |  | read |
| KN-LIT-7496 | Weakly Secure Equivalence-Class Signatures from Standard Assumptions |  |  | read |
| KN-LIT-7497 | Weakly-Private Secret Sharing Schemes? |  |  | read |
| KN-LIT-7498 | Weighted Oblivious RAM, with Applications to Searchable Symmetric Encryption |  |  | read |
| KN-LIT-7499 | Weil Descent of Elliptic Curves over Finite Fields of Characteristic Three Seigo Arita |  |  | read |
| KN-LIT-7500 | Welcome to the isogeny party! |  |  | read |
| KN-LIT-7501 | What Information is Leaked under Concurrent Composition? |  |  | read |
| KN-LIT-7502 | WHAT IS. . . AN ELLIPTIC CURVE? |  |  | read |
| KN-LIT-7503 | What output size resists collisions in a xor of independent expansions? |  |  | read |
| KN-LIT-7504 | When are Fuzzy Extractors Possible? |  |  | read |
| KN-LIT-7505 | When e-th Roots Become Easier Than Factoring |  |  | read |
| KN-LIT-7506 | When Failure Analysis Meets Side-Channel Attacks |  |  | read |
| KN-LIT-7507 | When Homomorphism Becomes a Liability |  |  | read |
| KN-LIT-7508 | When Messages are Keys: Is HMAC a dual-PRF? Matilda Backendal1[0000−0002−8677−8301] , Mihir Bellare2[0000−0002−8765−5573] |  |  | read |
| KN-LIT-7509 | Which eSTREAM ciphers have been broken? |  |  | read |
| KN-LIT-7510 | Which Languages Have 4-Round Fully Black-Box Zero-Knowledge Arguments from One-Way Functions? |  |  | read |
| KN-LIT-7511 | Which Languages Have 4-Round Zero-Knowledge Proofs? |  |  | read |
| KN-LIT-7512 | Which phase-3 eSTREAM ciphers provide the best software speeds? |  |  | read |
| KN-LIT-7513 | White-Box Cryptography in the Gray Box |  |  | read |
| KN-LIT-7514 | Who watches the watchmen? : Utilizing Performance Monitors for Compromising keys of RSA on Intel Platforms |  |  | read |
| KN-LIT-7515 | Why Provable Security Matters? Jacques Stern |  |  | read |
| KN-LIT-7516 | Why Proving HIBE Systems Secure is Difficult |  |  | read |
| KN-LIT-7517 | Why “Fiat-Shamir for Proofs” Lacks a Proof? Nir Bitansky1?? |  |  | read |
| KN-LIT-7518 | Wild McEliece |  |  | read |
| KN-LIT-7519 | Wild McEliece Incognito |  |  | read |
| KN-LIT-7520 | Witness Authenticating NIZKs and Applications |  |  | read |
| KN-LIT-7521 | Witness Encryption and Null-IO from Evasive LWE |  |  | read |
| KN-LIT-7522 | Witness Encryption for Succinct Functional Commitments and Applications |  |  | read |
| KN-LIT-7523 | Witness Encryption from Instance Independent Assumptions |  |  | read |
| KN-LIT-7524 | Witness Indistinguishability for any |  |  | read |
| KN-LIT-7525 | Witness Maps and Applications |  |  | read |
| KN-LIT-7526 | Witness-Succinct Universally-Composable SNARKs |  |  | read |
| KN-LIT-7527 | Worst-Case Hardness for LPN and Cryptographic Hashing via Code Smoothing |  |  | read |
| KN-LIT-7528 | Worst-Case Subexponential Attacks on PRGs of Constant Degree or Constant Locality Akın Ünal[0000−0002−8929−0221] |  |  | read |
| KN-LIT-7529 | XLS is not a Strong Pseudorandom Permutation |  |  | read |
| KN-LIT-7530 | XOCB: Beyond-Birthday-Bound Secure Authenticated Encryption Mode with Rate-One Computation |  |  | read |
| KN-LIT-7531 | XPX: Generalized Tweakable Even-Mansour with Improved Security Guarantees |  |  | read |
| KN-LIT-7532 | XTR Implementation on Reconfigurable Hardware |  |  | read |
| KN-LIT-7533 | Yes, There is an Oblivious RAM Lower Bound! |  |  | read |
| KN-LIT-7534 | YOSO: You Only Speak Once Secure MPC with Stateless Ephemeral Roles |  |  | read |
| KN-LIT-7535 | Your Rails Cannot Hide From Localized EM: How Dual-Rail Logic Fails on FPGAs |  |  | read |
| KN-LIT-7536 | Your Reputation’s Safe with Me: Framing-Free Distributed Zero-Knowledge Proofs |  |  | read |
| KN-LIT-7537 | Yoyo Tricks with AES |  |  | read |
| KN-LIT-7538 | ZAPs and Non-Interactive Witness Indistinguishability from Indistinguishability Obfuscation |  |  | read |
| KN-LIT-7539 | Zero Correlation Linear Cryptanalysis with Reduced Data Complexity |  |  | read |
| KN-LIT-7540 | Zero Knowledge and Soundness are Symmetric? |  |  | read |
| KN-LIT-7541 | Zero Knowledge in the Random Oracle Model, Revisited Hoeteck Wee? |  |  | read |
| KN-LIT-7542 | Zero Knowledge Protocols and Signatures from the Restricted Syndrome Decoding Problem Marco Baldi1[0000−0002−8754−5526] , Sebastian Bitzer2[0000−0002−5928−359X] |  |  | read |
| KN-LIT-7543 | Zero-Communication Reductions 1 |  |  | read |
| KN-LIT-7544 | Zero-Knowledge Accumulators and Set Algebra |  |  | read |
| KN-LIT-7545 | Zero-knowledge Argument for Polynomial Evaluation with Application to Blacklists |  |  | read |
| KN-LIT-7546 | Zero-Knowledge Arguments for Lattice-Based |  |  | read |
| KN-LIT-7547 | Zero-Knowledge Arguments for Lattice-Based Accumulators: Logarithmic-Size Ring Signatures and Group Signatures without Trapdoors |  |  | read |
| KN-LIT-7548 | Zero-Knowledge Arguments for Matrix-Vector |  |  | read |
| KN-LIT-7549 | Zero-Knowledge Arguments for Subverted RSA Groups |  |  | read |
| KN-LIT-7550 | Zero-Knowledge Elementary Databases with More Expressive Queries |  |  | read |
| KN-LIT-7551 | Zero-Knowledge Functional |  |  | read |
| KN-LIT-7552 | Zero-Knowledge Proofs on Secret-Shared Data via Fully Linear PCPs Dan Boneh1 , Elette Boyle2 , Henry Corrigan-Gibbs1 |  |  | read |
| KN-LIT-7553 | Zero-Knowledge Protocols for the Subset Sum Problem from MPC-in-the-Head with Rejection |  |  | read |
| KN-LIT-7554 | Zero-Knowledge Sets with short proofs? |  |  | read |
| KN-LIT-7555 | Zeroizing Attacks on Indistinguishability Obfuscation over CLT13 |  |  | read |
| KN-LIT-7556 | Zeroizing Without Low-Level Zeroes: New |  |  | read |
| KN-LIT-7557 | ZMAC: A Fast Tweakable Block Cipher Mode for Highly Secure Message Authentication |  |  | read |
| KN-LIT-7558 | Zombies and Ghosts: Optimal Byzantine Agreement in the Presence of Omission Faults |  |  | read |
| KN-LIT-7559 | μKummer: efficient hyperelliptic signatures and key exchange on microcontrollers |  |  | read |
| KN-LIT-7560 | “HILA5 Pindakaas”: On the CCA security of lattice-based encryption with error correction |  |  | read |
| KN-LIT-7561 | “Ooh Aah... Just a Little Bit” : A small amount of side channel can go a long way |  |  | read |
| KN-LIT-7562 | “Provable” Security Against Differential and Linear Cryptanalysis |  |  | read |
| KN-LIT-7563 | The supersingular isogeny problem in time and memory p^{1/3+o(1)} | 2026 | preprint; full text frozen in-repo at inputs/P13-WESOLOWSKI-2026/paper_fulltext.md (SRC-P13-WESOLOWSKI-2026) | full_text |
| KN-LIT-7603 | Linear Descent for Rank-2 and Rank-4 Module-LIP |  | Anonymous submission (unrefereed; venue and date not stated in the text) | full_text_supplied |
| KN-LIT-7f6a8b | Introduction to the higher dimensional setting / Isogeny Computations in Higher Dimensions (ECC 2024 autumn school and workshop) | 2024 | ECC 2024 autumn school (29 October 2024) and ECC 2024 workshop (30 October 2024), Inria / IMB, Bordeaux (lecture slides and handout) | read |
| KN-LIT-80f208 | Explicit bounds for generic decoding algorithms for code-based cryptography | 2009 | WCC | false |
| KN-LIT-8ce0b5 | Rank Bounds for NTT Twiddle-Factor Fault Attacks on ML-DSA (Lean 4 Machine-Checked) | 2026 | IACR ePrint 2026/1188 | partial |
| KN-LIT-91b680 | A Survey of Chosen-Prefix Collision Attacks | 2021 | chapter in Computational Cryptography, CUP (revised form) | read |
| KN-LIT-93e8d7 | Error-correcting coding for digital communication | 1981 | book | false |
| KN-LIT-a45b7b | Index Calculus in Class Groups of Plane Curves of Small Degree | 2007 | 11th Workshop on Elliptic Curve Cryptography (ECC 2007), Dublin (talk slides) | read |
| KN-LIT-a4d0f1 | Elliptic and hyperelliptic curves with weak coverings against Weil descent attack | 2007 | 11th Workshop on Elliptic Curve Cryptography (ECC 2007), Dublin (talk slides) | read |
| KN-LIT-b875db | Solving the Shortest Vector Problem in 2^{0.7314n+o(n)} Time via Discrete Gaussian Sampling on Superlattices | 2026 | Preprint (unrefereed; no venue, ePrint number, or DOI stated in the supplied text) | full_text_supplied |
| KN-LIT-b9bba7 | Practical key recovery attacks on two McEliece variants | 2010 | SCC | false |
| KN-LIT-be0bfd | The Matrix Reloaded: Multiplication Strategies in FrodoKEM | 2021 | Proceedings of the 20th International Conference on Cryptology and Network Security (CANS 2021) | read |
| KN-LIT-d1a453 | Recognizing the structure of permuted reducible codes | 2007 | WCC | false |
| KN-LIT-f37d84 | Definite Orthogonal Modular Forms: Computations, Excursions, and Discoveries | 2026 | ANTS-XV proceedings (preprint form in downloads) | read |
| KN-LIT-fb9929 | Low-Latency Elliptic Curve Scalar Multiplication |  | manuscript (author's page, draft) | read |
| KN-LIT-fd27c2 | Analysis and Optimization of Cryptographically Generated Addresses |  | manuscript (EPFL/ENAC preprint) | read |

## 7. Identifiers claimed by more than one entry

A curation signal, not an error: one entry may supersede the other, or the
corpus may hold a true duplicate. Resolving it is a `/curate-knowledge` job.

| Identifier | Entries |
|---|---|
| `arxiv:0811.0647` | KN-LIT-237, KN-LIT-7631 |
| `arxiv:1012.4019` | KN-LIT-071, KN-LIT-282 |
| `arxiv:1310.7789` | KN-LIT-078, KN-LIT-387 |
| `arxiv:1711.04062` | KN-LIT-560, KN-LIT-7632 |
| `arxiv:2304.14757` | KN-LIT-4c8135, KN-LIT-c41d8b |
| `eprint:2010/331` | KN-LIT-13a01d, KN-LIT-3c9f21 |
| `eprint:2015/573` | KN-LIT-475, KN-LIT-7607 |
| `eprint:2023/1618` | KN-LIT-1117, KN-LIT-132 |
| `eprint:2024/1193` | KN-LIT-71d1a0, KN-LIT-a4d70e |
| `eprint:2025/1661` | KN-LIT-d82a53, KN-LIT-e37d4c |
| `eprint:2025/531` | KN-LIT-6b1fc8, KN-LIT-7ee1a9 |
| `eprint:2026/1318` | KN-LIT-7670, KN-LIT-7674 |
| `eprint:2026/366` | KN-LIT-7667, KN-LIT-7c2620 |
| `url:cdn.openai.com/pdf/ten-proofs-oai.pdf` | KN-LIT-7637, KN-LIT-7640 |
