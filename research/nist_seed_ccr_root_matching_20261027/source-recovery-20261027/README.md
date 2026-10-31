# Recovered Atkin interface: exact cohort observations

2026-10-27. T-5518. ATKIN-NATIVE-GETALL-01 and -02. Observations only; no formal historical-selector decision or status promotion.

The complete second run passes its formal export check. All666 native-body observations match the first run byte for byte:598 cohort GETALL calls and68 controls in each run. Every one of299 rational parameters succeeds at both26-bit and30-bit MSW arithmetic widths; all21 curves are represented. There are no cohort zero divisions. The historical selector remains unidentified.

The fixed cohort contains11 reconstructed omissions and10 publications across six streams. Every model is y^2=x^3-3x+b over Fp; exact p,b,n,UID,seed and ordinal are in the sealed rows.json. Cohort SHA256:93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545. Reconstructed omission does not establish historical visitation or rejection.

| RNG timestamp | Field bits | Omitted | Published | Successful parameters | Branch checks |
|---|---:|---:|---:|---:|---:|
|863711343|239|5|3|123|189|
|863966734|192|2|3|70|98|
|871002724|521|0|1|14|22|
|871696354|256|1|1|28|43|
|872952608|384|0|1|10|16|
|891607927|224|3|1|54|65|

Counts are per width and per run. All parameters succeed. 315 fixed curve/level cells include299 rational parameters at15 type-II levels53 through293. Cells without a rational parameter are not failed curves.

## Source and reconstructed dependencies

The author-hosted March5,1993 note contains actual GETPAA and GETALL bodies. The exact extraction compiled unchanged. The original ZL arithmetic, BLVNOC, GETJQN, CHARLA and coefficient tables were not recovered. The replacement arithmetic uses normalized most-significant-word-first limbs; the source library format is not established. New FLINT code enumerates all rational neighbor j values in sorted order. New corrected CCR/Newton code checks the division-polynomial remainder, cyclicity and Velu quotient coherence. This is source-body execution with reconstructed dependencies and modern tables, not an original1997 program run.

GETPAA uses ordinary alpha partials and Euler j partials. With E4=-A/3, E6=-B/2 and r=E6/E4, GETALL forms alpha_prime=r*(j*Psi_j)/Psi_alpha. At a candidate neighbor jq, rq=alpha_prime*Psi_alpha(alpha,jq)/(ell*jq*Psi_j(alpha,jq)), E4q=rq^2*jq/(jq-1728), and E6q=rq*E4q. It returns Aq=-3*ell^4*E4q and Bq=-2*ell^6*E6q and obtains the kernel sum from second derivative ratios. No extraction of a cube root of j occurs in this interface. For the cohort A=-3, E4=1. This does not settle other historical field-dependent paths.

## Independent replay and controls

PARI/GP independently recomputed301 source cases and437 candidate branches:299/433 on the cohort and2/4 on regular controls. It matched derivative normalization, reconstructed kernels, division-polynomial remainders and cyclicity. All299 accepted cohort kernels also matched Frobenius traces derived from the recorded orders, which the native routine and reconstructed validator did not receive. The replay applies to both runs because their entire observation streams are byte identical. Public archives were verified; the repeat archive was decompressed, relocated and independently replayed.

Each run includes60 derivative controls (all15 tables in two fields and two widths, five derivative outputs each), four regular GETALL controls, two known derivative-exception GETALL controls and two after-cohort fixture repeats. The regular field/model is p1009,A990,B660,j34,ell53. The exceptional model is p1009,A199,B469,j24,ell53,alpha98; its zero division is retained. Multiword roundtrips cover both limb widths through521-bit values.

## Aggregate-count obstruction

Omitted863711343/36 and publishedP-239v2 both have18 source parameters,26 candidate branch checks and zero divisions in the same field. A predicate of this aggregate tuple alone cannot separate them. OmittedP-224 ordinal777 has10 parameters and14 checks, compared with the publication at14 parameters and15 checks; a budget monotone solely in these two totals cannot reject the former while retaining the latter. These statements do not concern actual historical time, per-level profiles or an arbitrary combined rule.

## Source search and retained failures

The February5,1997 LiDIA1.3 announcement still lists prime-field point counting as work in progress; it does not identify the later tested LiDIA body as part of that release. The author-linked UVW/Dist-V2.1.tgz is a2024 Magma package. The ja93.pdf preprint is the February21,1995 version of the same Morain article. Neither is a recovered1997 point counter. Bounded mirror probes and missing-library searches are retained in SOURCE-ACCESS.json, RELEASE-ACCESS.json and SOURCE-SEARCH.json. Failed access is not evidence of nonexistence.

A source-build link failed before native calls because the compiler driver did not find the SDK libc++ stub; the successful link adds its explicit directory and changes no Fortran. The first GP audit logged a malformed comment but continued to the final marker; the audit remained FAIL. The second audit changes only that comment and passes. The first formal export checker found686 encoding/identity findings: controls were represented as full Cartesian arms and observer IDs/commit fields did not match that schema. Its data and failed export remain unchanged. The prospectively frozen repeat treats333 embedded-input cases at each of two widths, repeats the entire run, and passes the formal check with zero findings.

Native process elapsed times were53.8456 and54.5844seconds on a shared desktop, diagnostic only. No timing comparison or historical resource estimate is made. All attempted native calls completed; no timeout or censored native row was converted into a mathematical rejection.

## Custody, graph scope and next test

Original author source/email/PDF, the linked2024 distribution and the native binary stay private because redistribution permission has not been established. URLs/hashes and the new adapters are public. The modern LiDIA coefficient tables carry their COPYING notice. Both canonical store uploads were refused by HeadObject403; the exact archives are retained in Git under the existing PR exception. No remote store custody or merge readiness is asserted.

The existing CCR kernel-recovery diagram and modular-coordinate guard diagrams were checked and remain unchanged: this source-body reconstruction adds execution provenance and no new isogeny, CM-order result or official scientific decision. workflow.svg and counts.svg document this round. The next source gap is the original validator/table/caller combination; any recovered mechanism must be tested on the same11 omissions and10 publications before being proposed as the historical selector.

Sources: [Atkin March5,1993](https://www.lix.polytechnique.fr/~morain/AtkinEmails/19930305.txt); [Atkin March3,1993](https://www.lix.polytechnique.fr/~morain/AtkinEmails/19930303.txt); [LiDIA1.3 announcement](https://math.albany.edu/g/Math/Comp/cas/LiDIA-feb97); [Morain author preprint](https://www.lix.polytechnique.fr/~morain/Articles/ja93.pdf). All were retrieved; source hashes are retained.

Evidence: BUNDLE-FIRST.json, BUNDLE-REPEAT.json, CROSS-REPEAT.json, EXPORT-CHECK.json, INDEPENDENT-AUDIT-02.json and both archive-replay.stdout receipts. Existing PR:https://github.com/isogeny-labs/crypto-autoresearcher/pull/2602.
