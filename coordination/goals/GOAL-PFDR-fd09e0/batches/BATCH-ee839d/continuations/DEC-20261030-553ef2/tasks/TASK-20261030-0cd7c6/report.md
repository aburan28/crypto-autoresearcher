# Blind review: exact formal layers; finite transfer remains conditional

TASK-20261030-0cd7c6 · 2026-10-30 · owned joint: `independent-primary-joint-algebra-and-quantifiers`

**Scoped verdict: inconclusive for applicability to an actual joint cell or growing family.** I independently prove a formal joint-module layer identity and a sufficient finite good-specialization lemma. I also give explicit controls rejecting generic-unit, row-count, support-only and principal-ceiling shortcuts. No producer result was read, so this is not an acceptance or rejection of the producer's unseen derivation. The complete manual argument is in [blind-derivation.md](blind-derivation.md).

For (K=\mathbb Q(c)\), (I=(F_1,F_2,F_3)\subset K[x]\), formal modulus (N\), fixed finite support (M\), and (T_s=I^s\cap K^M\), I derive

\[
E_{\rm formal}(\mu,M)=\sum_{s=1}^{\mu}\dim_KT_s,
\qquad q_{\rm formal}=\mu|M|-E_{\rm formal}.
\]

The proof collects coefficients of the independent polynomial variable (N\) in ((N,I)^\mu\). It needs no regular-sequence assumption on the three (F_i\). The spaces (T_s\) already include mixed products, dependencies, and support cancellations. Their dimensions are not the number of products or a sum of three principal dimensions. No dimensions were numerically or symbolically computed by software.

For integer specialization (N=p\), the unconditional replacement is the exact filtered-module identity

\[
E_p=\sum_{i=0}^{\mu-1}\dim_{\mathbb F_p}
 \overline{((p,I_p)^\mu:p^i)\cap\mathbb Z_{(p)}^M}.
\]

Equality with the generic sum is proved under explicit sufficient conditions: (p\)-saturation of every (I_p^s\), exact base change of each finite-support intersection, and preservation of its rank. For every fixed ((\mu,M)\), a finite certificate can establish these conditions by monic ideal bases with two-way membership/reduction identities, normal-form matrices, and unit maximal-rank minors. Clearing their finitely many denominators produces a nonzero polynomial (\Delta_{\mu,M}(c)\). The guarantee applies when (p\nmid\Delta_{\mu,M}(c_0)\).

This proves the quantifiers (\forall(\mu,M)\ \exists\text{finite certificate}\ \forall\text{good specializations}\). It does not prove one certificate or one exceptional-prime bound for every growing multiplicity, support, prime, or coefficient family. No actual target certificate, (\Delta\), ideal basis or kernel matrix was supplied or constructed here. A single fixed-base membership witness does extend soundly to products of every (k\); that narrower result does not establish completeness of the larger ideal-power intersections.

The nonunit control breaks the unjustified transfer exactly: in (\mathbb Q(c)[N,x]\), (x=c^{-1}(cx)\in(N,cx)\). At (c(p)=p,N=p,x=1\), the original generators vanish modulo (p\), but (x\) does not. The good-specialization predicate rejects it. Separately, matrix ([c]\) has no denominators yet drops rank modulo (p\) for this family. Thus denominator units and rank/pivot survival are separate requirements. Duplicate relations do not change the ideal. The permitted historical F101 corruption and signed-lift examples remain exact counterexamples to support-to-root and x-zero-to-signed-relation transfers; no finite trial was rerun.

The height interface is equally conditional. Clearing an integer identity proves divisibility, but row multipliers can increase the real determinant even if they are (p\)-units. Modular inverse representatives can be as large as the modulus power. Large trailing coefficients do not necessarily change a triangular determinant, so the required charge is the actual integer lift, basis index and input bit size, not an invented universal penalty. For a coefficient polynomial (P\), the elementary bound ( |P(c_0,n)|\le\|P\|_1 H^{\deg_cP}\max(1,|n|)^{\deg_NP}\) exposes the missing growth terms. Fixed fixture heights do not settle (H=p^{O(1)}\), or changing base multiplicity.

I re-read Ryan's pinned full-primary sections: §2.5/Heuristic 1 (PDF p.6), §3.2 and §4.1–4.2, §6.1–6.6 (pp.19–24), and Appendix C/C.1 (pp.48–52). Its §6.1 requires denominators coprime to the known modulus multiple. Lemma 7 assumes the shared modular root, suitability/statistic representation, Heuristics 1 and 2, proportional coefficient specialization, a strict exponent margin and the stated joint (k,p\) growth condition. Its polynomial-time statement excludes final root recovery. Finite interpolation and degree checks do not prove Heuristic 2. None of these hypotheses is discharged merely by the formal identity above.

The source comparison used pinned cuso `fb2747d2105a8e48499bf10a3a717cf80c14d079` and byte-matching native files from published `4f27d0cd0a50b94d4f990a593321cf2951015ce9`. Cuso's same-modulus ideal and modulus normalization match the interface being derived; its final-row denominator list is narrower than a complete membership, saturation and kernel-rank certificate. Native `model.hpp` freezes rational integer coefficients and centers, rather than the full (c(p)\) family. Reading the implementation establishes neither executed parity nor full-cell certificate correctness. The exact upstream S3 and S4/S5 source copies explicitly scope their convex ceilings to principal ideals; this review does not extend them to the joint ideal.

The minimal next artifact is a finite proof-of-certificate pack: exact row identities and integer lifts; monic ideal bases with generator/reduction identities for every required power; normal-form kernel matrices and unit minors; both-direction row/module span and suitability witnesses; and actual determinant/index/height charges. Section 9 of the derivation specifies a checker design only. No checker implementation, scientific cell, bound search, root recovery, resource sampling, container, advice, seal or native invocation was performed.

All 24 original scientific cells remain unrun. The old Q4 terminal no-retry restriction and historical failed independence plans remain unwaived. No runtime qualification, numerical reach, principal-to-joint closure, extraction, IC cost or advantage, status promotion, or future checker PASS is asserted. The existing named problem is `problems/joint-smallroot-reach-baseline-and-oracle-unverified.md`; only the four assigned files were written, leaving shared updates and mathematical composition to the Coordinator.

Provenance: fresh independent native selection `gpt-6.1-sol`, `review-adversarial`, `xhigh`, canonical agent `/root/joint_blind_validation_0cd7c6`, task session `joint-blind-validation-20261030`, owner `validator-joint-blind-0cd7c6`. This records the parent-supplied actual managed invocation selection, not an independently probed API catalog or serving-model certificate. `model_verified=false`; no fallback or degradation was used. Input primary hashes and source-blob comparisons were checked directly; other control-plane publication/claim custody is the root's supplied authorization, not mathematical evidence.

Retrieval limits: the tool catalog exposed no `search_knowledge`/`get_context` MCP. I used only scoped reads/searches of permitted planning files, named historical inputs, full-primary text and pinned code. All current protected producer, snapshot and sibling paths remained unread permanently. Some initial tool output was truncated; relevant mathematical passages were re-read in narrower calls, and `sources_read` records partial sections without claiming every file was read in full. A native source-tree filename inventory was broader than needed and included older check filenames; no contents of those check files were read and no protected current-round artifact was exposed. Later source reads used exact file paths.

The review-evidence skill's claim/provenance boundaries and research-visuals guidance were read. The original handoff gives only four text outputs and assigns final visual composition to the Coordinator. No separate visual/PDF, Git mutation, fetch/merge, claim/state change, archive, problem-record edit or session-receipt file was created by this reviewer. This is an explicit division of work, not a completed composition or review gate.

The machine-readable attestation is [review-attestation.yaml](review-attestation.yaml); actual metadata/source checks and limits are in [checks.json](checks.json). I consent to the root's **normal reporting-only release of these four frozen files after their byte counts and hashes are verified**. This consent grants no mathematical acceptance, status transition, unblinding, or new execution authority.

Citation provenance: the pinned primary text, cuso/native code and exact upstream copies are `retrieved`, verified by `/root/joint_blind_validation_0cd7c6` through the reads and content bindings recorded here. Named historical reports/records are `internal` and used only within their stated scopes. The algebraic lemmas are `manual derivation`, with no novelty or machine-proof claim. Own-output UTF-8, control-character, JSON/YAML parse and attestation-field checks completed; these are document checks, not the round's independence/composition checker.
