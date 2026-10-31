# CM controls and complete y-coordinate matching

2026-10-27. T-5518. ATKIN-Y-MATCH-01. Observations and an explicitly derived corollary; no historical-selector decision or official hypothesis transition.

Two independent implementations agree on all415 cases each (830 implementation calls):411 cohort kernels and four control calls. There are29,401 positive-half scalar-coordinate computations per implementation, with both signs compared at each index (58,802 signed scalar comparisons). The extra export counter named scalar_candidates_tested counts positive-half indices, not the two signed variants.

The cohort consists of228 kernels on11 reconstructed omissions and183 kernels on10 publications, across six RNG streams. All411 have nonzeroS1 and exactly one coincident signed y-only/full-point match. No first-y match gives a wrong trace residue on the cohort. Reconstructed omissions do not establish historical visitation or rejection events.

| Field bits | Stream | Omitted curves | Published curves | Kernels | Ambiguous kernels |
|---:|---|---:|---:|---:|---:|
|239|863711343|5|3|160|0|
|192|863966734|2|3|96|0|
|521|871002724|0|1|23|0|
|256|871696354|1|1|43|0|
|384|872952608|0|1|12|0|
|224|891607927|3|1|77|0|

## A source-described failure mode with working CM controls

Atkin’s author-hosted March5,1993 note, final-calculations discussion, describes sequential matching against signed y-coordinates and warns that another x-coordinate could share a matching y. This study reconstructs that full cyclic-kernel search in new GP code. The independent verifier uses division polynomials with formal derivative jets to recover y([k]P)/y from x([k]P), rather than repeat affine addition. All complete match sets and full Frobenius trace relations agree. Neither implementation is original eigenvalue code.

The ordinary CM control is E/F103:y^2=x^3+1, order84, j=0, with its two stable7-kernels. On the split kernel, y-only matches are{1,2,4} and the full match is1. On the irreducible cubic kernel, y-only matches are{3,5,6}, the full match is5, and the sequential signed search encounters6 first. Scalar6 implies trace1 modulo7, while the correct trace20 is6 modulo7. Thus the detector exposes an actual erroneous early stop in the reconstructed search on this constructed control. No original-program defect is asserted. The regular E/F101:y^2=x^3+x+1, order105, with kernel X^3+70X^2+47X+10, has the single match1 andS1=31; its after-cohort A/A matches exactly.

The local complete-manifest LMFDB av_fq index supplies isogeny classes1.103.au (q103, stored Weil polynomial1-20T+103T^2, p-rank1) and1.101.d (q101,1+3T+101T^2,p-rank1). Source:postgresql://devmirror.lmfdb.xyz:5432/lmfdb/public.av_fq_isog; extraction ended2026-10-19T16:45:49.243703+00:00. These are class labels, not individual-model identities. The small models are independently counted by the auditor; no catalog crosswalk to a cryptographic curve is made.

## Why nonzeroS1 excludes this ambiguity

The elementary argument is in lemma.md. A false complete y-function match gives a nontrivial scalar a preserving y on the nonidentity subgroup. Every orbit has at most3 points because a fixed y determines a cubic in x. Order2 is impossible: a=-1 reverses y on every nonidentity odd-order point. Thus a has order3 and ell=1 modulo3. Each orbit contains the three roots of a depressed cubic, whose x-sum is zero. Summing over the subgroup gives2S1=0, henceS1=0 in odd characteristic. Therefore nonzeroS1 certifies uniqueness; zeroS1 is only necessary for ambiguity, not sufficient. The statement concerns the full valid cyclic kernel, not a single evaluated point or an improper factor.

## Executed scope and separately derived canonical scope

The411 inputs are distinct accepted kernels:299 from the previous Atkin-interface reconstruction at15 type-II levels53 through293, and112 from corrected CCR at3,5,7,11,13,17,19. This is22 represented levels, not native execution of every possible level or kernel. All21 full curve identities remain fixed. Models are y^2=x^3-3x+b overFp; exact p,b,n,seed,ordinal andUID are in rows.json. Cohort SHA256:93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545.

A separate post-start symbolic deduction uses Atkin’s March3,1993 formula and the earlier sealed canonical derivative guards. For a canonical parameter F, S1=(ell*gcd(12,ell-1)/2)*(E6/E4)*(j*Phi_j)/(F*Phi_F). All factors are nonzero on the886 rational canonical parameters: E4=1,E6=-b/2, nonzeroj/F, and the independently verified derivative Bezout identities. The integer normalizer is nonzero in these large fields. Whenever this formula supplies a valid cyclic kernel, itsS1 is nonzero and complete-y matching is unique. These886 matches were not newly executed. Together with the299 directly tested type-II parameters, this gives a conditional uniqueness statement on the1185 parameters of the available61-level equation set. The112 low-level CCR kernel calls are not added again to that parameter count. SOURCE-COROLLARY.json binds the exact prior proof and archive hashes. This deduction does not change the frozen415-case experiment.

## Completeness, attempts and custody

The GP process completed415 calls in135.0882seconds; the independent verifier completed415 in245.1762seconds, with65MB/155MB maximumRSS as recorded. Times are shared-desktop diagnostics, not a performance comparison. Every planned case completed. GP’s stack-size warning is retained and no other native error occurred. Formal export checking passes for all830 rows. The two CM controls detect four false match scalars in total and one wrong first trace; ordinary A/A passes.

Before native execution, five schema findings in the first metadata draft were corrected to describe the two actual implementation arms. A late publication-helper review found that symlinked Python source would resolve into the sealed directory; evidence-replay.tar.zst corrects only that replay helper, while the first archive remains unchanged. Public CSV line endings are normalized toLF; the sealed CRLF raw CSV and exact row-equivalence binding are retained. No scientific input or observation was changed by either packaging correction.

Both attempted canonical object-store uploads were refused by HeadObject403; exact archive bytes remain in Git under the existing PR exception. The original Atkin correspondence is not redistributed; URLs and hashes are public. The directory index exposes the same five already recovered notes. Bounded searches did not recover original ZL/CHARLA/caller source. Full text of Dewaghe’s later1998 paper was not acquired:AMS403, CiteSeer429 and an unreachable mirror are retained, and no algorithmic conclusion relies on that inaccessible text.

## Historical limits and next source target

This rules out the specified complete-kernel y-only ambiguity on the frozen411-kernel domain and gives the stated conditional extension. It does not identify the original selector, prove that the original program visited any omitted position, authenticate period coefficient tables, or cover other partial/faulty fingerprints. The original validator/caller remains the discriminating source target; any different endomorphism-related or transfer criterion must still account for all11 omissions while retaining all10 publications.

The earlier CCR root-matching, modular-coordinate and recovered-interface diagrams were checked and remain unchanged. This round adds an eigenvalue-matching stage observation and a point-orbit diagram, not a new isogeny-volcano edge or scientific status promotion.

Sources (retrieved):[Atkin March5,1993](https://www.lix.polytechnique.fr/~morain/AtkinEmails/19930305.txt);[Atkin March3,1993](https://www.lix.polytechnique.fr/~morain/AtkinEmails/19930303.txt). Local sources:LMFDB-query.stdout;SOURCE.json;CASE-BINDINGS.json;SOURCE-COROLLARY.json;AUDIT.json;EXPORT-CHECK.json;BUNDLE-REPLAY.json;replay receipts.
