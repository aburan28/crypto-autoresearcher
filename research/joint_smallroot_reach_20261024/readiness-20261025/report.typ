#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt, font: "DejaVu Sans")
#set par(leading: 0.55em)
#set heading(numbering: none)
#heading(level: 1, "Weighted reach, conditional cost, and solver readiness")
#image("weighted-reach.svg", width: 100%)
#text(size: 8pt, "Derived from finite-audit.json, one deterministic construction per t; no sampling uncertainty. Gray region uses an unvalidated yield/cost model and rho as a separate reference.")
#text("This is an additive accounting and software-readiness report. No new joint-system scientific trial, root recovery, random-target measurement, or IC speedup is reported. The original audit and independent review remain unchanged.")


#heading(level: 2, "Inputs and observations")
#text("- Archived finite input: ../artifacts/finite-audit.json, published before this   continuation; three joint union-support candidates at multiplicities 1, 2, 3.   Their algebraic fixture has a=2, b=3, xQ=5 and six integer unknowns. No subgroup   identity or random target distribution was specified; none is inferred.")


#text("- External implementation: keeganryan/cuso (https://github.com/keeganryan/cuso),   commit fb2747d2105a8e48499bf10a3a717cf80c14d079, package version 0.4.0,   LGPL-3.0-or-later. Its README links Ryan's   eprint 2024/1577 (https://eprint.iacr.org/2024/1577). No source is vendored.")


#text("- Software readiness observed: SageMath 10.9, CPython 3.12.15, igraph 1.0.0,   fpylll 0.6.4. The documented examples/symbolic/rsa_affine_padding.py completed   and printed delta*=1/3. Its complete stdout/stderr is retained in   cuso-univariate-readiness.log. This is one documented univariate calibration,   not a joint-system result. No time or peak-RSS measurement was captured.")


#text("- External source inspection: src/cuso/symbolic/optimal.py calls   J.groebner_basis(); symbolic/asymptotic.py constructs the ideal and calls   the optimal-shift routine. The implementation therefore has a Gröbner   preprocessing cost. It cannot yet substantiate a claim that this route   bypasses Gröbner costs. This differs from claiming that all shift approaches   require a particular finite-field solving degree.")


#text("- The README's span guarantee does not guarantee efficient lattice reduction,   enough independent relations, or root recovery. The symbolic return value   is explicitly heuristic, within its specified construction and assumptions.")


#heading(level: 2, "Derived weighted accounting")
#text("Write leaf bounds as X=p^beta and internal-node bounds as Y=p^gamma. There are four leaves and two non-root internal nodes. For the archived triangular families, let sL and sI be the respective coordinate exponent sums, N the row count, and K=tN-q. Their determinant-level sufficient region is")


#text("4*sL*beta + 2*sI*gamma < K.")


#text("This region omits the LLL and evaluation-norm losses. A sufficient first-vector bound includes the factor sqrt(N)*2^((N-1)/4) multiplying det(L)^(1/N). For finite p the corresponding right-hand-side budget is reduced by N*log_p(sqrt(N)*2^((N-1)/4)). Even satisfying this stronger condition does not supply enough independent integer polynomials for extraction.")


#block(breakable: false)[#text(size: 8pt)[#table(columns: (auto, auto, 2fr, auto, 1fr), inset: 4pt, [#text("t")],
[#text("N")],
[#text("weighted inequality before losses")],
[#text("dense entries")],
[#text("upper ceiling on 3beta+2gamma in this region")],
[#text("1")],
[#text("31")],
[#text("44beta+38gamma < 3")],
[#text("961")],
[#text("9/44")],
[#text("2")],
[#text("382")],
[#text("1140beta+938gamma < 98")],
[#text("145924")],
[#text("49/190")],
[#text("3")],
[#text("2591")],
[#text("12048beta+9620gamma < 1280")],
[#text("6713281")],
[#text("80/251")])]]
#text("The last column is exact rational algebra on archived statistics, not a new shift search. For beta,gamma >= 0, set A=4sL, B=2sI. Then 3beta+2gamma <= max(3/A,2/B)*(A*beta+B*gamma); for these three rows the maximum is 3/A. Thus the displayed ceilings are 3K/A. The graph plots these sufficient regions. A point outside a region lacks this certificate; it is not proved unrecoverable. Dense entries measure structural storage growth, not bytes, peak memory, reduction time, or an algorithmic lower bound.")


#heading(level: 2, "Conditional cost model and measurable goal")
#text("The following is a model, with unvalidated assumptions: window restrictions behave as independent uniform field-coordinate restrictions; the four-leaf system produces expected usable decompositions proportional to lambda=p^(4beta+2gamma-3); the extractor succeeds with bounded nonzero probability conditional on a solution; duplicates, sign ambiguities and rank do not introduce exponent losses; the subgroup has order Theta(p); and sparse linear algebra costs p^(2beta+o(1)). For lambda <= 1, collecting p^beta usable relations using attempts costing p^(tau+o(1)) gives the optimistic exponent")


#text("C(beta,gamma,tau)=max(3-3beta-2gamma+tau, 2beta).")


#text("Here tau is an attack-cost exponent. It is NOT the symbolic shift-tuning tuple also named tau by cuso. Preprocessing and failure probabilities must be charged separately if this formula does not already include them. The formula is not a measured complete-cost estimate.")


#text("For a frozen IC baseline of exponent cB, necessary model conditions for a strict improvement are beta<cB/2 and 3beta+2gamma>3+tau-cB. The current matched IC baseline cB has not been reproduced in this study. Do not silently set it equal to rho.")


#text("For the separate rho reference cB=1/2, the conditions become beta<1/4 and 3beta+2gamma>5/2+tau. Consequently gamma must exceed 7/8+tau/2 near the limiting beta=1/4; with gamma<=1 and tau>=0 one also needs beta>(1/2+tau)/3 and tau<1/4. These are conditional requirements, not an algorithm. The three finite certificate regions above have no overlap with that modeled sub-rho region, even before charging losses or extraction cost. This says nothing universal about improved shifts, other representations, higher multiplicity, or the security of any curve.")


#text("The performance goal remains a matched, independently replayed complete IC comparison: verified discrete logs and relation certificates; cold setup, shift construction, Gröbner preprocessing, reduction, extraction, misses, duplicates, rank, linear algebra and final verification charged; time and peak memory recorded at multiple sizes; identical curves, subgroups, target seeds, resources and success requirements in both arms. Report the speed ratio with uncertainty and failures, plus the separate rho reference. A determinant threshold or a planted-root success alone does not satisfy this goal.")


#heading(level: 2, "Admission and publication observations")
#text("The full repository was materialized. The backlog command reported GOAL-PFDR-fd09e0 approved_unrun=0 cap=none. Two open lanes were found, BATCH-286bd3 and BATCH-8d6d84, both on the existing sibling research branch. The goal's max_concurrent is 2. No lane was stolen, closed, or newly admitted. The existing batch's ready-task query refused an unresolved archive.commit_sha binding for TASK-20261017-56402f. This is not a result about small roots and was not repaired by changing its archived records.")


#text("The configured Coordinator resolves to an unverified Anthropic model. Its credential is absent. Probes of OpenAI, OpenRouter and ZAI likewise report missing credentials; the configured local service refuses its connection. Doctor exit code zero is not a verified backend: its warning text is retained. The installed Codex CLI reports authenticated ChatGPT access, so the API failures do not establish that all inference is unavailable. However, this session has no receipt-bound independent Coordinator thread: no existing SQLite state database was found in the exposed Codex directories. No fallback, policy downgrade, model-verification assertion, or scientific dispatch occurred. The next design requires a lawful lane and a verified runtime under the repo's design-experiment rules, followed by a runnable frozen joint-system contract.")


#text("Full-ledger validation exits 1 with 106 errors outside all 61 changed paths at input head d157d6015eb9f6b83feabe6b5fa65c281933cffa. Its complete output is retained. This is not a clean global validation; no baseline entries were added or suppressed. Branch-scoped merge hygiene passes. The study does not repair unrelated ledger history.")


#text("The user explicitly authorized merge. The two observed CI defects have been repaired and the artifact workflow passes on the merged-main head. Other applicable hosted workflows remain queued/pending at this snapshot. The active ruleset requires progress-fidelity, but does not list every applicable check. Auto-merge is therefore left disabled while those checks are pending; enabling it could merge before the other checks finish. This is a check gate, not a renewed permission request. No failed or pending check was bypassed.")


#heading(level: 2, "Remaining gap and next check")
#text("The external goal is not achieved. The scoped reach/cost accounting is reviewable; an optimized weighted joint construction and a verified complete IC improvement remain absent. This is an implementation/admission and evidence gap, not a mathematical impossibility claim or a closure of the lead. Repository goals, hypotheses and the lead retain their existing scientific statuses.")


#text("Next: in a lawful lane with a receipt-bound Coordinator, freeze an adapter to the pinned cuso source, affine windows, coefficient-height/denominator conditions, weighted bounds and exact shift domain. Use the already successful univariate calibration plus single-S3 and nearby-object controls. Predeclare the joint workload and collect construction size/time/RSS before root recovery; publish the inputs and pass native admission before execution. Require independent normalization and extraction checks before selecting a random-target panel. The old 0.8408 versus 8/9 margin remains unreconciled, not a target already shown to be within reach.")


#text("Graph sources checked: the original reach-cost.svg and review-20261024/accounting.svg report their frozen accounting, so they are preserved. This report adds weighted-reach.svg and its drawing script. No canonical curve/isogeny relationship or scientific status changed.")


