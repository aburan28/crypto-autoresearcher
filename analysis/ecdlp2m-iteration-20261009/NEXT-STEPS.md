# GOAL-ECDLP2M-001: ranked next steps after the 2026-10-09 iteration

This is a pointer document for the Coordinator. It approves nothing and
changes nothing. Every item names the skill that would act on it and the gate
that holds it. The goal's own gate still applies: no new batch until the
TASK-20261005-34c6e8 repair, the lane reconciliation and the C5 re-rank are
done (DEC-20261005-040d37, -fe9f9f, -ef42c6). The approval cap of 3 approved,
never-run contracts per goal also applies.

## What the iteration established empirically

1. **The cost of a failed decomposition attempt is the binding constraint, and
   only bounded-degree algebraic refutation could pay it**
   (`ctrial-harvest/`, `m3-closure-pilot/`).
   - Relation collection beats rho only if an UNSAT attempt costs
     2^(alpha*l) with alpha < m/2 - 1.
   - Every SAT or enumeration method measured has alpha of about m. WDSat
     matches exhaustive search: the UNSAT slope is 2.9985 bits per l.
   - At m=3 and m=4 the measured families extrapolate 50 to 150 bits above every
     budget line at ECC2K-130.
   - At m=3 the degree-4 mutant closure refutes every UNSAT chained-S_3 instance
     run (n = 9, 11, 15), with a cross-checked instrument. The degree stays
     flat at 4. This is consistent with Assumption 1 at m=3, and the mechanism
     follows the sparse support of the system: the support-matched null is
     refuted and the dense null is not.
2. **Gaudry n=4 on the c2pnb curves wins on time and loses once memory is
   charged** (`c1-gaudry-n4-c2pnb/`).
   - It is time-only sub-rho on all five rows.
   - It is dominated under the program's time x memory convention on every
     row inside the per-trial cost band.
   - It wins mesh area-time only at 304w1 and 368w1, and only for
     c_trial <= 2^27.
3. **The CERTBIN k=2 collision excess is an instrument artifact**
   (`certbin-k2-collision-audit/`). A pointer is on the bus as
   MSG-20261009-11c45d.
4. **Three widely cited closures are cited beyond the scope they tested**
   (closure audit, this session).
   - KN-FIND-aa2efc: no large primes, time only, a single target.
   - KR-IC-1fcdbc: two abstract-read sources, cited in 105 files.
   - KR-IC-5ea2f8: the GHS-prime-degree row, extended to composite degree.

   Two "nulls" never tested the quantity that matters:
   - GP versus random V was matched on dim(V*V).
   - The Nagao coset comparison was an implementation timing.

## Ranked next steps

| # | step | why now | route | gate |
|---|---|---|---|---|
| 1 | Measure whether the closure degree stays at 4 as m grows. Run W_D on chained S_3 for t = m in {4, 5}, n ladder to the memory wall, several curves, polynomial and random V, both nulls at every n, M4RI >= 20240729 plus an independent eliminator, enumeration ground truth | This is the only mechanism that can satisfy alpha < m/2 - 1. An exponent gain needs m >= 5, and Assumption 1 at m >= 4 is the unmeasured premise under the only memory-charged sub-vOW binary row (sect571, EV-SEMBIN-4125ec). The pilot at m=3 is cheap and clean | `/propose-ideas` on the SEMBIN or DREG question (owner: GOAL-SEMBIN-5078bc or GOAL-DREG-001, which are not slot-gated here), then `/design-experiment` | Approval capacity of the owning goal. Fixing M4RI needs github.com allowed in this environment's network policy |
| 2 | Turn the m=3 pilot into a contract-grade replication: the same ladder as `m3-closure-pilot/`, completed with the nulls at n >= 11, the random-V cells, and n = 13/17 at full sample size | It converts the exploratory reading into evidence and settles the dense-versus-support null contrast across n | Same route as #1. It can be Stage 0 of the same contract | Same as #1 |
| 3 | Re-scope the over-extended citations: KN-FIND-aa2efc (large-prime rows; EXP-BINSTD-e066d8 Stage 0 is approved but unimplemented), KR-IC-1fcdbc (read `inputs/GG-2014-806` in full), KR-IC-5ea2f8 (composite degree; EXP-BINSTD-ee23dc Stage 0), and KR-IC-46d822 (14/9 is the single-large-prime exponent, not double; the Joux–Vitse constant is n!*2^(3n(n-1))) | Zero compute. These rows are cited as dominating most binary readings | `/curate-knowledge` for the KR-IC rows; implementation of e066d8/ee23dc Stage 0 belongs to the design lane | Not slot-gated for knowledge rows |
| 4 | Make a Coordinator correction of EV-CERTBIN-691499 and DEC-20261004-d70aac, and check the predecessor EV-CERTBIN-db7f15, which uses the same instrument family | A documented artifact currently backs a weaken | Coordinator correction record (additive) | IMP-ECDLP2M-STRANDED reconciliation, if the records are involved |
| 5 | Implement the S_4-versus-chained-S_3 live path of EXP-BINSTD-6f3434 (its Stage 1 runner is a placeholder that always returns O-IMPEDIMENT) and the m=4 S_5 ANF export blocked in b94ec8 | Nothing has ever measured an m >= 4 SAT cell, and the direct-versus-chained presentation question stays open | Design-lane amendment of the approved contract | Goal gate (BINSTD) |
| 6 | C1 toy ladder: E over F_(2^4) lifted to F_(2^(4k)), k in {5,7,9,11,13}, about 2*10^4 decompositions, to pin c_trial, D and the memory per worker | It decides the one mesh area-time cell (304/368). Under the program's own metric C1 is already dominated | Input to the U-HOLDH-V2 revision (standing order rank 2) | Goal gate |
| 7 | Harness fix: `tools/newest_experiments.py` `off_main_runs` sees only fetched remote refs. In a clone that fetched only main, it reported "ready" for two contracts already executed on unmerged `cursor/*` branches | It prevents duplicate runs of stranded work | Normal code change and PR | None |

## Out of scope or closed by this iteration (with revisit conditions)

- **m=3 or m=4 relation collection by SAT or enumeration on ECC2K-130.**
  Measured costs are 50 to 150 bits over budget.
  Revisit if: a solver shows UNSAT cost growing by less than m/2 - 1 bits per
  unit l at m >= 3.
- **Rho-constant polishing (C5).** It is worth at most 0.5 bit.
  Revisit if: an m=4 row comes within 1 bit of its budget.
- **Couveignes–Lercier route at 131 (C6).** The size cap and the source are
  unverified, and this is NOT a closure (inventor-protocol section 4).
  Revisit when: the primary source has been read.
