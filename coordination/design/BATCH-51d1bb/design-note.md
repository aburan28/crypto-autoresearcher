# Finite lumpability diagnostic

This design converts the corrected `IDEA-20260905-b1f9f0` into `H-CRYPTO-acdb49` and the approved prospective `EXP-CRYPTO-5e8beb`. The uncertainty remains substantive: whether any of the fixed restricted-private kernels gives the specified coordinate features a reproducible finite defect advantage over the matched partitions. A complete control-passing panel can answer **no**. No result has been observed.

The five bodies become effective through exact Coordinator archival, validation and publication. The implementation handoff authorizes zero runs. A separately reviewed and genuinely bound scientific launch is still required.

## Frozen panel and criterion

C11 and C17 each have four residue features x mod q, q=2,3,4,5, with 32 deterministically seeded partitions preserving each exact ordered cell-size vector. Identity and constant features add two controls per prime. C15 supplies mod3/mod5 cosets, identity and constant. Thus there are `2*(4*33+2)+4=272` main partitions. All states are visible cycle coordinates; none is a claimed cheaply obtainable function of an unknown ECDLP scalar.

Each partition has four restricted fresh-private kernels, a fully public uniform-translation kernel, and a hidden fresh-uniform kernel. Horizons are 0,1,2,3. The transcript is the initial feature followed by every public label and subsequent feature. Every initial state is compared with the simulator starting from that **same initial feature**.

For each of the 32 restricted comparison panels, the coordinate defect must be at least 1/8 below the exact mean of its 32 null defects and strictly smaller than at least 24 null defects. A q/kernel pair qualifies only if both prime sizes qualify. All 16 pairs are preregistered and reported. At least one paired qualifier supports this finite prediction; zero rejects it when controls are valid. No seed, kernel or horizon is added after results, and no p-value or population significance is claimed.

The four main boundaries are distinct. Identity/constant and C15 cosets are exactly lumpable. Hidden uniform translations force zero defect for every partition. A nonzero deterministic public translation has defect one on every nontrivial lossy prime-order partition. But public uniform translations' **joint averaged** defect is a separating-translation fraction, not that binary maximum. Restricted-private comparisons use the actual joint defect, not a sum of separately maximized conditional defects or a forced-zero boundary.

## Prospective approximation derivation

Write J_x(l,b)=nu(l)K_l(x,b). For a current feature c, let r_c be its least state. Conditional on any positive-probability allowed history ending in c, the real hidden state has some distribution pi supported in that fiber. Fresh state-independent labels and fresh private draws make the next observation law exactly sum_x pi(x)J_x. The simulator uses J_(r_c). Convexity of the finite L1 norm gives TV(sum pi J_x,J_(r_c)) <= sum pi TV(J_x,J_(r_c)) <= delta.

Couple the two next observations while their complete observed histories agree. Their conditional disagreement probability is at most delta. Starting with the same initial feature, an iterative coupling and union bound give a probability of any transcript disagreement at most min(1,t*delta), hence the same bound on full joint transcript TV. This quantifies over every initial state and every reachable history under the frozen laws. An adaptive observation, persistent private seed, or hidden-state-dependent label law changes the premise.

This is the design's own prospective derivation, awaiting independent review and implementation verification. The parent-read Theorem1/equation2.1 of arxiv0710.1986 supports the exact common-cell-mass criterion only. No approximation theorem, compact representation result or independent proof is attributed to that source.

The producer uses exact full-history dynamic programming. The independent checker reconstructs the laws and enumerates latent label/translation paths and simulator paths without importing producer kernel, TV or dynamic-programming helpers. Each distribution must have nonnegative reduced rational masses summing to one. Full transcript tables and maximum witnesses are checked; final-time marginals alone are insufficient. The reference artifact contains separately labeled real and simulator reference distributions.

## The assumption trap

The separate trap uses C11, identity feature, every initial state, and horizon two. Draw one uniform hidden A and reuse it at both steps. For fixed x the actual pair is `(x+A,x+2A)`, so there are eleven equally weighted traces. Fresh uniform increments give 121 equally weighted traces. The preregistered full-TV target is therefore 10/11. Both final states are uniform because multiplication by two is invertible modulo eleven, so final-marginal TV is zero.

This trap violates freshness and is explicitly tagged bound-inapplicable. It is not a falsifier of the correctly scoped coupling statement. It tests whether the measurement machinery preserves joint history and notices the missing premise. The fresh identity control remains an exact zero-defect, exact-simulator case.

## Counts and artifacts

There are 134 partitions at each prime and four at C15. Summing initial states gives `134*11+134*17+4*15=3,812`. Six kernels produce 22,872 initial-state/kernel combinations, and four horizons give **91,488 main full-transcript checks**. The eleven trap starts bring the total to **91,499**. There is one planned scientific run, not 91,499 independent trials.

Across the partitions there are 7,271 unordered same-fiber pairs: 1,936 at C11, 5,185 at C17 and 150 at C15. Six kernels give 43,626 joint pair-TV checks. The eight coordinate/null ensembles yield 32 restricted comparisons and 1,024 null-score entries. These are hand-derived protocol counts, not executed outputs; parent checks them before archival.

All kernel tables, full real/simulator/reference transcript distributions, rational TV certificates, score rows, control summaries, source bindings, costs and partial-run receipts have exact filenames in the specification. `table_bits` uses the integer bit length of B-1, giving zero for B=1; descriptor metadata and actual serialized bytes are charged separately. A bound of one is flagged as vacuous. Missing or incomplete tables cannot be hidden by a pass summary.

Construction, hash-based partition generation, rejected shuffle draws, feature/kernel/state access, arithmetic operand bit lengths, transcript enumeration, checking, serialization and retained storage are charged. Full-state tables are permitted for this finite audit but do not establish a compact quotient or an ECDLP speedup. The complete cryptanalytic frontier remains unassessed.

## Readiness and remaining gates

| Item | Disposition |
| --- | --- |
| Source scope | Corrected successor retained; earlier source unchanged. Exact-lumping literature separated from own approximation derivation. |
| Complete finite parameters | Groups, features, laws, seeds, representatives, order, horizons, initial states and counts fixed. |
| Controls | Identity/constant, composite cosets, public rigidity, hidden uniform, exact matched sizes, independent tables and freshness/joint-history trap. |
| Decidable outcome | Valid positive and valid negative finite-conjecture outcomes separate from invalid/incomplete evidence. |
| Artifact and cost completeness | Full joint distributions and certificates, source/launch bindings, measured arithmetic/resources and all construction/data costs. |
| Scientific budget | One fixed run/panel, one worker and8GiB remain binding; only time/CPU estimates are advisory nulls. No favorable retry or expanded panel. |
| Runtime and durable artifacts | Actual launch.json/receipt.json names, exclusive supervisor output creation,3600-second machine checkpoint and bounded LUMP1 hash-checked partial-result transport. |
| Implementation | Ten exact files, zero runs, independent reference and source-only runtime preflight. |
| Scientific launch | Requires implementation snapshot, independent review, actual backend/resource preflight, separate handoff and genuine run/claim/launch binding. |
| Official state | Hypothesis specified, prospective specification approved after archival; no supported result, goal closure or knowledge promotion. |

The parent found no dedicated lumpability development in this repository's `formal/` tree. The missing formalization binding is this experiment's rational conditional kernels and observed-history semantics to an exact Lean conditional-mixture and finite-history coupling statement. No claim is made that Mathlib lacks probability, TV or coupling libraries. Revisit the precise binding after representation freeze and independent review; no formal proof is claimed now.

The ten implementation files are fixtures.py, kernels.py, transcripts.py, reference.py, certificates.py, driver.py, runtime_preflight.py, README.md, implementation-manifest.yaml and implementation-report.yaml under this experiment's implementation directory. Their handoff is `TASK-20260907-6bd7c0`, archived by `TASK-20260907-c0a81d`.

Source excerpts, hashes, repository discovery and library searches were supplied by the parent control plane. This Coordinator performed no commands, tests, fixture evaluation, experiments or independent source readback. Failed KB retrieval is a retrieval limit. Nearby spectral r-adding and history-refinement studies remain separate. The broader portfolio is not declared designed or complete by this task.
