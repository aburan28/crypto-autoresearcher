#set page(paper:"a4",margin:16mm,footer:context [#text(size:8pt)[EXP-ECDLP-5184f7 • proposed design • no new attack results] #h(1fr) #counter(page).display()])
#set text(font:"DejaVu Sans",size:9.5pt)
#set par(leading:.5em)
= Are Solinas primes more resistant to ECDLP?
Controlled study design • 2026-10-11 UTC • related EXP-ECDLP-4c6a09

*Measure three distinct effects: which curves are generated, attack work at matched subgroup size, and arithmetic speed.* No new trial was run. This is a design report; solver/oracle/timing integration remains subsequent implementation work.

== Main sample: 36 paired prime blocks
12 sparse primes each at 24, 28 and 32 bits, drawn without replacement from the deduplicated verified catalog p = 2ᵇ − 2ᵃ + s·2ᶜ + t, 1 ≤ c < a ≤ b−2, s,t ∈ {−1,+1}. This specified sparse ensemble does not represent every Solinas family.

#table(columns:(.5fr,1.3fr,2fr),inset:5pt,
 [Arm],[Prime-selection rule],[What it tests],
 [S],[Specified sparse catalog],[Prime family of interest],
 [R],[Same bits; within 1% of S],[Total sparse-versus-random contrast],
 [C],[R rules + same p mod 12],[Effect beyond this congruence control])
Random controls use uniform odd-integer rejection sampling with exact primality checks, excluding the sparse catalog and historical anchors. No next-prime sampling and no outcome-dependent replacement. Freeze all 108 main moduli before curve counts or attack timings.

#image("comparison-design.svg",width:100%)

== Separate historical case studies
Six exact earlier primes, each with R/C controls, add 18 moduli. Their sizes are 18, 21, 32, 36, 56 and 72 bits. The four smaller cases receive the toy attack stage; 56-/72-bit cases are structural audits only. They are reported individually, never pooled with the 36 main blocks.

#pagebreak()
= Attack measurements and controls
Audit the first 32 uniform nonsingular coefficient models per modulus without security screening: full curve order/factorization, largest prime subgroup ell, cofactor, trace, twist and weak-curve flags. This retains potential differences in curve-generation outcomes.

For conditional attacks, prepare 512 models per eligible modulus. Fixed screen: ordinary, N≠p, j outside {0,1728}, largest prime ell of 16–26 bits appearing once, and no embedding degree ≤20. This removes obvious confounders and is not a comprehensive security certificate.

Match S/R and S/C subgroup orders within ratio 1.10, before attacks. Use at most eight common S groups per block. Retain short/empty blocks. Every G must satisfy G≠O and ell·G=O; retain full EC1 identities and all selection records.

== Primary metric
Pollard rho, 16-adding walk, Brent cycle detection; four uniform synthetic targets per group and four walk seeds per target. Verify every scalar independently. At most 13,824 main rho attempts. Count search group operations W and measure *U = min(W/√ell,20)*. The exact integer cap is ceil(20√ell); setup, preparation and verification have separate counters, with end-to-end cost as a secondary outcome.

The √ell normalization comes from birthday collisions: after about √ell sampled group states, collisions become likely. Increasing ell alone therefore increases raw generic attack work. It need not indicate an effect of the field-prime shape.

BSGS uses the same targets with M=min(4096,ceil√ell) stored points. Retain actual bytes and complete target coverage. At most 3,456 main BSGS attempts. All arms first use the same generic arithmetic implementation.

#table(columns:(1.2fr,2.3fr),inset:4pt,
 [Control],[Interpretation or required behavior],
 [Sham family tags],[Exact same-group counts and answers],
 [Isomorphic curve],[Transported hashing reproduces the walk; native hashing checks encoding effects],
 [Opaque group + 32-adding walk],[All main groups; distinguish coordinate/walk artifacts],
 [BSGS + easy subgroups],[Independent correct solver and instrument sensitivity],
 [Generic/sparse reducers],[Same operands; exact agreement; timing separate],
 [Truth, replay, isolated timing],[No exposed scalar truth; deterministic counters; pinned single worker])

== Decision rule fixed in advance
Compute curve means including capped attempts; paired log ratios; equal block weights. Bootstrap whole prime blocks within size strata, 10,000 replicates, for 99% confidence intervals. Repeated targets/seeds are not independent primes. Higher measured rho cost requires the overall S/R lower bound >1.20, direction agreement in at least two sizes, and passing controls. Practical similarity requires the entire interval within [1/1.20,1.20]; otherwise inconclusive. Over 5% censoring limits claims to the declared capped work. Achieved statistical power is not asserted.

#pagebreak()
= Why subgroup size must be controlled
*Measured context only:* the preceding number-field experiment held base primes fixed. It did not compare Solinas with random primes. The two rational models below were previously selected for rank gains, so they are diagnostics rather than the new primary sample.

#image("historical-subgroup-confounding.svg",width:100%)
Six exact subgroup identities are listed on the next page. No uncertainty bars are shown because these are exact orders of six recorded groups, rather than estimates from the proposed sampling scheme. Source: internal immutable RUN-ECDLP-6d910b / RUN-ECDLP-9e6cc1 records and copied curve-identities.csv.

== How to interpret possible outcomes
#table(columns:(1.3fr,2fr),inset:5pt,
 [Observation],[Supported conclusion],
 [Larger ell in the unconditional S audit],[Different curve-generation outcomes under this recipe],
 [Same normalized calls; different seconds],[Arithmetic or implementation-speed effect],
 [More coordinate-walk calls; no oracle effect],[Representation or walk effect],
 [Higher normalized rho cost across controls],[Higher cost for that declared attack in this sample],
 [Interval entirely within the practical margin],[Practical similarity within the tested scope],
 [Wide interval or failed controls],[Inconclusive; preserve failures and unmatched samples])

== What would establish stronger resistance?
Two cyclic prime-order groups of the same order are abstractly isomorphic. A generic attacker behind an opaque interface cannot read the binary shape of the field prime. A higher rho benchmark constant alone therefore does not establish intrinsic generic hardness.

A broader claim would need a validated structure-dependent shortcut that works on comparable random-prime curves and is avoided by the specified sparse-prime curves, with independent reproduction and review. Retain the cheaper applicable generic control. Toy results do not establish deployed-curve or asymptotic security.

#pagebreak()
= Identities, provenance and execution boundary
== Exact identities for the historical chart
#text(size:7.4pt)[A=-3, B=3, p=262079, k=6\
N=261372; ell=947; h=276; G=(237963, 249012)\
urn:ec-record:1:sha256:8344f218e66391b3a2c10bf4d3f538d257cd9b958603aa387e6fa9b017669b6c]

#text(size:7.4pt)[A=-3, B=3, p=2097023, k=7\
N=2097833; ell=2097833; h=1; G=(1, 1)\
urn:ec-record:1:sha256:7f5aebdfe3ce06dc6fb333edcf906eec91e660ae5e5a5f74411435f6f96635d1]

#text(size:7.4pt)[A=-3, B=3, p=68719472639, k=12\
N=68719579720; ell=5385547; h=12760; G=(39306801954, 30775010499)\
urn:ec-record:1:sha256:55d93546292c07c17b3387818426a571b1590bb818b7744fc040c477068d85b3]

#text(size:7.4pt)[A=7, B=1, p=262079, k=6\
N=262235; ell=293; h=895; G=(173214, 38192)\
urn:ec-record:1:sha256:aecb5e3fd7115bdbfd214d14535a7fa414643bc3c2c9b3681d66d49a5ae7cac7]

#text(size:7.4pt)[A=7, B=1, p=2097023, k=7\
N=2095324; ell=6803; h=308; G=(1165070, 837767)\
urn:ec-record:1:sha256:2f53a922e551928386c48f1afe98a9e2e9924dd67a49ef874908bcdc580b15ef]

#text(size:7.4pt)[A=7, B=1, p=68719472639, k=12\
N=68719359128; ell=26109179; h=2632; G=(12970623466, 67126316800)\
urn:ec-record:1:sha256:c3394223ab666ffa15217079258f3a281d9cacf2964ede7b08388d87b18b6985]

== Reproduction and scope
The adjacent protocol.md is the detailed source-linked protocol. plan.json is the initial machine-readable plan; measurement-boundary.json authoritatively clarifies the common normalized horizon. No samples or scientific observations changed. design-provenance.json hashes internal evidence and lists the exact six anchor moduli. controls.csv is a compact control inventory.

build_design_report.py renders both editable SVG figures and this PDF from the plan and the six copied historical identities. It does not run primality catalogs, point counting, or ECDLP trials. Future preparation must materialize the catalog, matching, EC1 records and all source/seed traces; identities for unsampled groups are not invented here.

Resource protection: at most two preparation workers, one isolated timing worker, 4 GiB address-space limit per worker, 8 GiB headroom and a 600-second process watchdog. Fixed samples and operation caps define stops; there is no campaign wall-clock/batch ceiling. Infrastructure failures are not mathematical evidence.

The proposed identifier is not an officially registered or approved executable experiment. No independent scientific review, hypothesis promotion or canonical frontier update occurred in this design session. Earlier immutable results and reports remain unchanged.
