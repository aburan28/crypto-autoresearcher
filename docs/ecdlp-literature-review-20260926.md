# ECDLP literature review and publication plan — 2026-09-26

Scope: the four workspace repositories (`crypto`, `cryptanalysis`,
`crypto-autoresearcher`, `cairn`), read for results on (a) Pollard rho speed on
GPUs and (b) index calculus on elliptic curves. Every internal result was
checked against a literature sweep of 122 papers. ePrint and arXiv were
reachable this time; the August documents recorded HTTP 403. That sweep's
bibliography is now in the corpus: 92 new or superseding `KN-LIT` entries,
plus a claim-level known-results map (`knowledge/frontiers/ecdlp/`, 48 rows).

**Limits, stated first.** Deep, source-level adjudication was started for
eight candidates but did not finish: the review agents hit a usage limit. The
verdicts below come from the sweep (abstracts, plus full text where marked)
and targeted checks. Each is labelled with how it was reached, and every
"plausibly new" still needs the human check named in its row. No result here
moves an ECDLP exponent, and none is claimed to.

## 1. What the program has, by topic

### 1a. Pollard rho on GPUs: a real, timely engineering result

Everything below is in `cryptanalysis` and `crypto`. `crypto-autoresearcher`
has no GPU rho work; its rho lane is specified but has never run.

| Result | Numbers (as recorded) | Where |
|---|---|---|
| ECC2K-130 walk on 1× RTX PRO 6000 Blackwell | 22.100934 B scheduled updates/s (median of 5); DP34 collection 21.55 B/s; ≈20.1 SM-cycles/update | `cryptanalysis/docs/papers/ecc2k130-blackwell/` (ePrint-ready draft) |
| Campaign-compatible σ-walk | 17.45–17.63 B/s per GPU; 8-GPU fleet 138.9 B/s; ≈2^55.3 of the expected 2^60.9 iterations done, no collision | `cryptanalysis/ecc2k130/runner/` |
| Enabling fact | NVIDIA's `clmad` 64×64 carry-less multiply-add (PTX ISA 9.3, sm_80+). **Verified in NVIDIA's PTX documentation, 2026-09-26.** NVIDIA's own 2026-07-15 announcement benchmarks only GHASH and sum-check, with nothing on ECC or ECDLP | PTX ISA §9.7.1.5 |
| Per-GPU survey | RTX PRO 6000 14.5–15.1, B200 8.84 (19.40 with the table walk), L40S 8.70, H100 7.54, A100 4.63, T4 0.54 B/s | `crypto/ecc2k130/`, `cryptanalysis/paper/` |
| FPGA | AWS F2 VU47P: 8.249 G steps/s measured on the device (power not measured) | `crypto/hdl/ecc2k130/aws/` |
| Walk constant | σ-walk c = 1.08–1.10 (small n), extrapolated to 2^60.91–60.92 iterations; confirms Bailey et al. | `crypto/ecc2k130/WALK-CONSTANT.md` |
| Laptop demo | 81-bit Koblitz ECDLP (m = 83) solved on an M4 Pro GPU in 114 s | `cryptanalysis/ecc2k130/small/` |

**Literature position.** This is established by the sweep, from full text for
2009/541, 2010/077 and 2016/382.

- Prior GPU state of the art for this problem is Bernstein et al. 2010,
  "ECC2K-130 on NVIDIA GPUs": more than 63M it/s on a GTX 295. That is about
  1,180 SM-cycles per iteration then, against about 20 now (derived).
- No academic GPU Pollard-rho paper appears on ePrint or arXiv after 2019.
  GPU collision-search engineering now lives in community kangaroo solvers
  (JeanLucPons Kangaroo; RCKangaroo) and in EC-arithmetic frameworks (gECC,
  2025).
- The largest binary record is 117.35 bits (Bernstein et al. 2016/382, FPGA),
  not Wenger–Wolfger, whose paper solved sect113r1.
- No completed ECC2K-130 solution has been published.

→ Rows `KR-RHO-*` in the map; entries `KN-LIT-c75942`, `-448a0c`, `-63a5c5`,
`-2c4f3d`, `-a4b3d8`, `-74dfa6`.

**Blocking issue found in this review, verified by diffing the two repos.**
The frozen `goal22` build behind the 22.1 B/s manuscript implements the **v1**
fruitless-cycle rule, `eccTagFruitless`, which refuses 2-cycles and pairwise
4-cycles only. `crypto/ecc2k130/WALK-CONSTANT.md` shows that v1 lets the
τ-relation 4-cycles (τ²+τ+2 = 0) and six-step pairwise cycles through. By
that note's accounting they trap about half the trails at DP32, and the v1
table walk cost **4.85–6.26× the σ-walk per solve**. Rule v2 (in `crypto`
HEAD) is projected at 0.81–0.86× but has never been measured on a GPU.

So the manuscript's "≈1% of DP34 trails enter six-step cycles" understates
the problem. Its 22.1 B/s is a throughput of steps, not of useful work, until
v2 is measured. The paper must:

1. port rule v2 and re-measure;
2. add a collision-quality run on the scaled curves (m = 41/83);
3. or re-scope its claim to the σ-walk (17.6 B/s), which is campaign-compatible.

### 1b. Index calculus: careful negatives, a few plausibly new pieces

Every internal IC line in all three repos is negative at cryptographic size.
That matches the literature; see `KR-IC-*` "Survey consensus" and
"Characteristic-2 summation algorithms stay far slower than rho". Several
internal "discoveries" were known:

| Internal result | Verdict | Basis |
|---|---|---|
| Frobenius-invariant factor bases on Koblitz curves (IDEA-20260915-8fe0ef) | **Known**: GGMP 2020/1315 | abstract; program's own DEC-20260916-3c0cf5 |
| "First fall degree 3" of S_3 Weil descents (`crypto` FFD notes, KN-FIND-006) | **Known mechanism**: Kosters–Yeo trace morphism (FFD 2 in their convention); HKY 2015 | KY abstract §4; July novelty screen |
| Symmetrised coordinates for decomposition | **Known**: FGHR 2014, FHJRV 2014 | the `crypto` note retracts it itself |
| "Choose V to keep V^(2) small" (`cryptanalysis` pdp-degree-heuristics) | **Objective known**: HPST 2013 chooses V for small V^(i); V = span{1,z,…} is the standard FPPR/Petit–Quisquater choice. Uniqueness follows from Bachoc–Serra–Zémor 2017 (a Vosper analogue: small dim S² ⇒ geometric-progression basis). Possibly new: the *linearization-excess* rule predicting solving degree (MAE 0.06, 656 bases) | abstracts; BSZ abstract |
| Batch prime-field "IC" (`ic prime`) | **Known**: Kuhn–Struik multi-target rho; the repo says so itself | abstract |
| Isogeny-transfer lane (8 evidence records) | **Known**: Tate / JMV 2005 | EV-IT-511f3d |
| Trace as one XOR clause in WDSat (≈2× relations/CPU-s) | **Partly known**: the trace constraint is KY's morphism; XOR reasoning is Trimoska et al. CP 2020. The clause-level measurement may be new but is encoding-dependent (`crypto` finds no gain in its own encoding) | abstracts |

Candidates that survived the sweep, pending the named check:

| # | Candidate | Status | Check before publishing |
|---|---|---|---|
| I1 | **Nagao ePrint 2015/984 Lemma 4 is false over F_2**, with two small counterexamples (KN-FIND-936151) | plausibly new; the 2015/984 PDF was fetched and the lemma is as described in the finding | confirm no later version corrects it (ePrint version history); check HKY 2015 and the Galbraith–Gaudry survey for a remark |
| I2 | **Semaev 2015 audited with memory charged**: crossovers at n = 460/520 against coherent vOW, t = m optimal, trace-parity bias of low-degree V, per-curve table with only K/B-571 below rho (EV-SEMBIN-4125ec, KN-FIND-9643e7, EV-SEMBIN-0c8bf4) | plausibly new framing; conditional on Semaev's Assumption 1 | Courtois 2016/003 and the 2015 ellipticnews thread; replicate EXP-SEMBIN-992e73 first |
| I3 | **Binary IC below n ≈ 300 fails because the descended ANF will not fit in the rho budget** (+6.3 to +40.8 bits; ECC2K-130 free oracle 2^68.58 vs rho 2^60.81) (EV-ICPERF-784b25, KN-FIND-aa2efc) | plausibly new as a quantitative statement | state the dense-ANF and linear-algebra-cap assumptions up front; compare Shantz–Teske and GG 2014 |
| I4 | **Quasi-subfield bound β > 1/2 for n' ∤ n** (KN-FIND-617d78) | plausibly new; answers HKPYY 2020 §5 as quoted by the finding | Euler–Petit journal version (FFA 2021); later QSP work |
| I5 | **Galois group (Z/2)^{m−2} of Semaev polynomials, factorization dichotomy** (manuscript `papers/semaev-conservation-specialization`) | likely partly folklore | Kosters–Yeo full text (arXiv 1503.08001), FGHR §3; a function-field expert for Lemmas 2.3/3.2 |
| I6 | **ecGFp5 symmetrised-decomposition estimate ≈2^121** vs a 128-bit target (research/gfp5_deployed_curves_20260920.md) | **no published cryptanalysis of ecGFp5 exists** (sweep). FGHR 2014 estimates ~2^130 for twisted Edwards over F_{q^5}, q ≈ 2^64, so the in-house number is not implausible, but it is **unmeasured** | measure the symmetrised ideal degree (KN-OPEN-9b4a2b); check Iijima–Momose–Chao's degree-5 GHS classification; deployed curve, so contact the designer before publishing |
| I7 | **WDSat's gain is its static branching order, not XOR-GE**: 135× more conflicts under random relabelling (EV-ICPERF-390707) | plausibly new ablation | Trimoska thesis and CP 2020 for order ablations |

## 2. Publication shortlist (ranked)

1. **Paper: "ECC2K-130 on Blackwell: binary-field Pollard rho with native
   carry-less multiplication"** (ePrint, then TCHES, or SAC/Indocrypt/Africacrypt).
   - The draft exists in `cryptanalysis/docs/papers/ecc2k130-blackwell/`.
   - The novelty is timely: first ECDLP use of `clmad`, and about 60× per
     SM-clock over the last academic GPU number.
   - It must first fix the v1/v2 cycle-rule issue (§1a) and add:
     - GTX 295 (2012/002) and Cell (2010/077) related work, plus
       Wenger–Wolfger, 2016/382, BLS 2011 and BKL 2010;
     - the per-GPU survey;
     - a public artifact deposit.
   - A completed ECC2K-130 solve (≈180 days at the fleet rate; the repo
     prices it at about $56k spot) would be a headline result on its own, and
     no one has published one.
2. **Blog post: "What ECC2K-130 costs in 2026."**
   - 2009: <2,700 PS3-years, or 63M it/s per GTX 295.
   - 2026: about 3.1 GPU-years on one RTX PRO 6000 at 22 B/s, or about 42k
     GPU-hours at the campaign σ-walk rate.
   - It is supportable now once the stale numbers in `docs/performance-gains.html`
     and `hdl/ecc2k130/README.md` are fixed. It must not quote the table-walk
     rate as useful work.
3. **Short paper or blog: "Index calculus on binary curves at real sizes — why
   it still loses to rho"** (I3 + I2 + the PDP slope data in
   `cryptanalysis/experiments/pdp-scaling`). It is a negative-results paper,
   framed against Galbraith–Gaudry 2016, Shantz–Teske and GG 2014.
4. **Short note: "The fake first fall degree does not bound the true one"**
   (I1). It is cheap, precise and checkable.
5. **Note: quasi-subfield bound** (I4), after the FFA 2021 check.
6. **ecGFp5 security margin** (I6). This is the most consequential lead,
   because it concerns a deployed ZK curve. It is not publishable until the
   symmetrised ideal degree is measured, and it follows a responsible-disclosure
   path.
7. **Blog: "Stage metrics lie: relabelling, skipped phases and the
   restart-limit bug."** 15.6% of steps were discarded by a bad `maxIters`;
   the triple-decomposition oracle cut the walked count while costing 4.6×
   more overall. These are method lessons from all three repos.

Not recommended: the BKK "speedup", H-PSEUDO "tight complexity", the GGM
closures, the MONO identities, conservation as a standalone result, and the
negation-map grid (EXP-RHO-60da4f, which lost to plain rho).

## 3. Mechanism to stop re-deriving the literature

**Diagnosis** (`docs/novelty-screen-20260729.md`, and an audit this session):

- 94% of `KN-LIT` entries are bulk stubs, 25% of them title-only.
- The canonical papers the program kept re-deriving were exactly the stubs:
  GGMP was KN-LIT-796 and HKY was KN-LIT-475.
- Nothing forced an idea to compare itself with the literature before being
  written.

**Changes in this commit** (all additive; no immutable record's substance
changed):

- **92 curated `KN-LIT` entries** with verified identifiers, each saying what
  was read. Among them:
  - about 45 canonical rho papers (negation map, Frobenius, kangaroo,
    multi-target, precomputation, GPU/FPGA records, community GPU solvers);
  - about 45 IC papers (Diem II, HPST, Shantz–Teske, APS, Yokoyama et al.,
    Hodges–Petit–Schlather, the SAT paper, recent Gröbner work).

  27 stubs now carry `superseded_by`. KN-LIT-010, which had Shantz–Teske's
  title under HPST's authors, is superseded by a correct entry. Two bulk
  duplicates point at their curated twins.
- **Known-results map**: `knowledge/frontiers/ecdlp/{generic-rho,index-calculus}/KR-*.yaml`,
  48 rows. Each row is a claim with its sources, its status (proven /
  heuristic / disputed / …), `forecloses` phrases, and the internal records
  that touched it, including the re-derivations. Schema and rules are in the
  directory README.
- **`tools/build_frontier_map.py`**: renders the map, `--check`s it in CI and
  `make check-ledger`, and `--match "<idea text>"` does a quick prior-art
  lookup.
- **Gate**: `prior_art` block on ideas, validated by `tools/validate_ledger.py`.
  - It is required from **IDEA-20261001-*** on, and optional before then, so
    no existing record changes state. The cutover is `PRIOR_ART_CUTOVER`.
  - `novelty_status: known` must cite a grounded `same`/`special_case` match.
- **Ideation wiring**:
  - `/propose-ideas` pastes the rendered map into the handoff and re-checks
    each returned idea with `--match`;
  - `/deep-research` starts from the map;
  - the idea-generator contract requires the block;
  - the schema is in `templates/research-records.md`.
- **Plumbing fixes**:
  - `allocate_id.py` now sees and mints `KN-*` and `KR-*` ids. Before this,
    `--check KN-LIT-001` reported an existing id as free.
  - `curate-knowledge` no longer says to grep for the next free number.
  - `build_knowledge_index.py --help` no longer writes `INDEX.md`.

**Not done (next):**

- stage the map into the `kb` retrieval index;
- restart the weekly literature gather, proposing `KR-*` rows;
- backfill identifiers for about 4,157 LNCS-named stubs from their filenames;
- give subagents the `mcp__crypto-kb__*` tools.

## 4. Cross-repo fixes spotted (not made here)

- `cryptanalysis/paper/ecdlp.tex`:
  - the numbers are stale: the campaign rate (14.1 → 17.6 B/s) and a
    "22.3 B/s floor" the repo's own 22.10 B/s result undercuts;
  - the hyperelliptic slopes (−1/6, −1/4) do not follow from the stated
    q^{2−2/g} cost; they are the relation-search regime;
  - the Bailey et al. author list is wrong;
  - the GPU, Cell and FPGA ECC2K-130 papers and the summation-polynomial
    core are missing from the bibliography.
- `cryptanalysis/suite/docs/ECDLP_ATTACK_MATRIX.md` and
  `crypto/research/notes/index-calculus/RESEARCH_FFD_MEASUREMENT.md`
  misattribute "Notes on summation polynomials" and HKY CRYPTO 2015
  (Galbraith and Huang–Kiltz–Petit are named instead of Kosters–Yeo and
  Huang–Kosters–Yeo).
- `crypto/docs/performance-gains.html` still headlines a retracted "IC beats
  rho (0.77×)".

## Provenance

- Repo surveys and the literature sweep ran 2026-09-26.
- The bibliography (122 entries, identifiers seen on fetched pages) is the
  source of every new `KN-LIT` entry.
- Claims marked "abstract" were relayed, not re-derived.
