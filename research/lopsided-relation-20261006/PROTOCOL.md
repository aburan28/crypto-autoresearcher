# Protocol: Lopsided batch decomposition for relation collection (toy, exactness-first)

Date: 2026-10-06. Branch: `cursor/lopsided-relation-mapping-1024`.
Assumption (user instruction): arXiv:2610.06783 Theorems 1/5 and Corollary 26
hold as stated. This task does NOT re-verify that paper and does NOT claim a
measured speedup for index calculus. It builds the integration: the
reduction shape from relation search to lopsided wanted-pairs form, with a
clean oracle seam, verified to preserve the relation set exactly.

## Why this is relevant to index calculus (the point)

Point decomposition is 3SUM-shaped: $R = P + Q$ is $P + Q + (-R) = 0$, a
3-term relation. The paper's chain is: 3SUM / Exact Triangle $\to$ lopsided
All-Edges Sparse Triangle (= offline Set Disjointness) $\to$ wanted entries
of a thin matrix product. Our MITM table-lookup join *is* an offline
set-intersection workload: many query values (target encodings) against a
stored key set (table tails / factor-base values). The paper solves exactly
this workload shape in subquadratic time when the instance is lopsided
(small middle part). So the relevance path is direct: batched decomposition
$\to$ lopsided wanted-pairs instances $\to$ thin-product oracle.

## What this task builds

1. `batch_lopsided.py`: synthetic 3SUM-shaped relation search
   ($R_t = f_i + f_j$ over $\mathbb{Z}_M$) solved three ways with BIT-IDENTICAL
   relation sets (verified by assertion, "no discrepancies" gate):
   - baseline: per-target hash lookup (our practical analogue of per-target
     $S_3$ + table probe);
   - lopsided+hash: factor base chunked into middle-pieces of size $D$,
     wanted pairs $(t,b)$ resolved per chunk (the paper's reduction shape,
     oracle seam = `count_chunk`);
   - lopsided+scan: same shape with per-query linear scan (the paper's
     "inner products one by one" baseline analogue).
   The oracle seam `count_chunk` is where the assumed thin-product oracle
   plugs in later; today it is exact hash/scan, so equality holds by
   construction AND is machine-checked.
2. `strassen_kernel.py`: exact 7-vs-8 multiplication check of Strassen's
   identity, the mechanism class (encode -> fewer products -> decode) the
   paper's Schonhage/Coppersmith construction belongs to. (A hand-transcribed
   Schonhage 10-product kernel FAILED its own randomized check and was
   deleted rather than hand-repaired; its correct transcription is deferred
   to the paper source / Lean formalization.)
3. `regime_table.py`: analytic regime check of our IC arities against the
   paper's preconditions ($D \le N^{\varepsilon}$, $|W|$ density) — read as a
   deployment map (which $(m, N)$ cells are oracle-eligible), not a verdict.
4. `run_all.py` $\to$ `results.json`; `ANALYSIS.md` interprets.

## Falsification / controls

- Relation-set equality across all three solvers on every instance
  (planted + random targets); any mismatch fails the run.
- Schonhage kernel: 200 randomized trials + zero/outer-only/inner-only/
  big-int controls.
- Dense-$W$ control in the op model (full product must win there).
- Success = exact agreement + measured overheads + regime map. A claimed IC
  speedup from this task alone = failure (out of scope: oracle not yet
  implemented, units incomparable — word-RAM mult-adds vs $S_3$ solves).

## Budgets and scope

- Wall clock < 60 s, memory trivial, stdlib only, deterministic seeds.
- No ledger writes, no goal state changes, no changes to
  `src/crypto_autoresearcher/index_calculus/`.
- Write scope: `research/lopsided-relation-20261006/` only.
- Operation counts are the metric, never wall time.

## Artifacts

`PROTOCOL.md`, `batch_lopsided.py`, `schonhage_kernel.py`,
`regime_table.py`, `run_all.py`, `results.json`, `ANALYSIS.md`.
