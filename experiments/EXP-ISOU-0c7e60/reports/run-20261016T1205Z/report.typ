#set page(paper: "us-letter", margin: (x: 0.52in, y: 0.46in))
#set text(font: "Libertinus Serif", size: 9.4pt)
#set par(leading: 0.58em)
#set heading(numbering: none)
#text(size: 18pt, weight: "bold", fill: rgb("#17364a"))[Native compact isogeny verification]
#parbreak()
#text(size: 12pt)[Degree $2^44497 - 1$ · secp256k1 · 16 October 2026 UTC]

This is an observation report. Independent postrun evidence review and any admission remain separate. One candidate and one fresh native verifier completed; no mathematical retry or substitution occurred.

#text(size: 8.4pt)[Goal GOAL-ISOU-f30a07 · H-ISOU-ffa8b0 · EXP-ISOU-0c7e60 \
Producer TASK-20261016-6db186 · report TASK-20261016-6239ad · approval DEC-20261016-4c28d0]

#image("flow.svg", width: 100%)

The constructor reports *CONSTRUCTED* and the independent native verifier reports *VERIFIED_COMPACT*, degree_bits=44497, on the exact registered source. Both native resource receipts report PASS, exit 0 and zero unavailable memory samples. Two native operations were requested and completed; none failed, timed out or remained unstarted.

The unreduced expression is $[a] + [b] phi$, where $phi(x,y) = (beta x,y)$ and its geometric degree is $a^2 - a b + b^2$. The certificate stores a 13,395-digit degree and two 6,698-character coefficients in 63,615 bytes. This is the compact known-endomorphism category; the expanded-map challenge score remains unassigned.

#text(weight: "bold", fill: rgb("#17364a"))[Recorded phase costs]
#table(
 columns: (1.6fr, 1fr, 1fr, 1.1fr, 1.2fr),
 inset: 4pt, stroke: 0.5pt + rgb("#b7c6cd"),
 [Operation], [Worker s], [OS real s], [CPU s (a)], [Worker RSS MiB (b)],
 [Construction], [83.029], [83.06], [58.66], [5.15625],
 [Verification], [351.050], [351.04], [241.28], [5.09375],
)
#text(size: 8.4pt)[(a) Derived user+system: 57.73+0.93=58.66 s and 237.36+3.92=241.28 s. \
(b) Derived from sampled 5,406,720 and 5,341,184 bytes divided by 1,048,576.]

The distinct supervisor timers are 83.051 and 351.076 seconds. OS maximum-RSS fields are 5,996,544 and 5,521,408 bytes, with a different public-command accounting scope. Original clock values remain preserved. Nested intervals are not summed. The two disjoint public-command OS receipts sum to 434.10 s real and 299.94 s CPU; setup, build, publication, report work and other trials are excluded and their CPU was unmeasured here.

Construction and verification used 1,800/3,600-second watchdogs and an 8 GiB sampled worker cap, 25 ms sampling and 100 ms unusable-sampling grace. This is not an OS hard memory limit. The diagram shows different phases of one instance; sample size is one per operation, with no measured spread or paired speed comparison.

First constructor invocation and OS worker start: *12:05:37 UTC*. Both adapters terminal: *12:12:51 UTC*. Host: Apple M4 Pro, 14 logical CPUs, 48 GiB, Darwin arm64, macOS 26.6, shared; initial load averages 41.70/46.42/48.93.

#pagebreak()
#text(size: 16pt, weight: "bold", fill: rgb("#17364a"))[Checks, immutable custody and boundaries]

The native verifier reports passing exponent primality; 44,495 Lucas–Lehmer transitions, terminal zero and matching recurrence digest; Cornacchia; exact integer and evaluated identity supplement; unreduced norm; separability; beta/lambda pairing; subgroup invertibility; eight public point images and both dual compositions. The source is the exact SEC2 model $y^2=x^3+7$:
#text(size: 8pt)[icv1-fp256-t432420386565659656852420866390673177327-76dadd18]

The producer uses BigUint, Mersenne folding and Jacobian evaluation. The verifier uses independent Int/general modular Lucas–Lehmer, independent Cornacchia and fixed-limb affine point replay. Prescribed public cases are fixed. SEC2 field/subgroup primality is TRUSTED_STANDARD, without self-contained p/n primality certificates.

Existing clean installed-byte-equivalent controls were reused from the frozen 94-pass native suite, including composite/rejection, norm/alias/point/dual mutations, real missing/zero-RSS child controls and fresh-path refusal. Those controls were not extra scientific trials in this instance. No build occurred for this experiment.

#text(weight: "bold", fill: rgb("#17364a"))[Exact provenance]
#parbreak()
Source aburan28/crypto, clean build e82d80feaf82d3730576ccd9137911b336f9dab8. The native executable remained unchanged. Harness execution commit: 4b2ebf2956eda0c038252aa461173c7c16428418. Actual served model/effort are unexposed and remain null.

#text(size: 8.1pt)[Binary SHA256: \
b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b \
Certificate SHA256 (63,615 bytes): \
85b5db3665a52a8fd04554964c03a6ed208bbb7ad1749770f5fa9d528b77f5d1 \
Raw archive SHA256 (96,856 bytes): \
9abc49de038066691ff20d2c83a46a5b260ca116ac69739f9c2d43e4b13c354d \
Lucas–Lehmer states SHA256: \
71bcb12e23c41e4a4fbd3d14498c96d9fbdcce3c778d48dd1c90506f2844fb35]

The frozen thin shell adapter invoked the installed executable directly under /usr/bin/time -l: compact-cm construct --exponent 44497 --timeout 1800, then compact-cm verify --input EXACT_CERT --timeout 3600, each with its declared fresh output. Full absolute argv and plan/queue/adapter/standards hashes are in report.md and the original run records. Python handled metadata, hashes and report work only.

Run companions were published first at 13410eae9e, then raw archive/observation at f1d5bbb476, then the completed nonexpired epoch-1 producer release 8ea5cb8658 with 14 artifact hashes. All 47 raw-file hashes and the fresh verifier's exact sealed certificate input were checked as metadata with zero mismatches. The archive retains the complete certificate/native trees, OS logs, collector and an explicitly labelled wrapper-prefix snapshot.

#text(weight: "bold", fill: rgb("#17364a"))[Publication and housekeeping receipts]
#parbreak()
The initial goal-claim push refused a remote auto-update before any mathematical work. The existing epoch was retained; the own-branch file diff was empty; a normal merge/push completed before launch. Two JavaScript metadata-preparation requests failed parsing before any tool command or file write. The corrected metadata collector passed syntax and executed once.

The wrapped Conductor release freed T3264 and exited. A redundant explicit release refused the already-stale epoch; no reclaim followed. Its /bin/sh checkpoint was unsupported after release. These are publication/housekeeping events and changed no native result or frozen artifact.

The initial Typst render rejected literal asterisk footnote labels. Letter labels repair the source; report.md retains the full failed input and compiler log.

The declared 22-path terminal snapshot follows this report, then independent review TASK-20261016-4bad89. Canonical frontiers/graphs and the season catalogue remain unchanged by this observational delivery. Worldwide comparison and expanded-map scoring remain separate.

#text(size: 8.2pt)[Sources: GIMPS candidate selection, https://www.mersenne.org/primes/; trusted SEC2 domain, https://www.secg.org/sec2-v2.pdf. Raw runs: experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e and RUN-ISOU-384b62. Archive: m44497/execution/TASK-20261016-6db186/native-evidence.tar.gz under this goal.]

