# Stopping-law / joint Q·S·P·C control (QM-STOPPING)

Task `TASK-20260730-043` · batch `BATCH-018` · idea `IDEA-20260729-001`  
Convention `CSIDH-COLLIMATION-FC0-R2` · control count: one · curve/isogeny/circuit compute: none

Decision/evidence binding: `DEC-20260730-015` / `EV-SSI-017`.  
Pinned code pin: `CollimationSieve@6f9188e4eb5611bcfdf29a3e1ec3cd69a29a50e9`.  
Pinned Peikert PDF (author-host archive, SHA-256):
`d4785e2863eebe97eb3a2909e02d669d138b2080c6e96e42c70d8d4fd2e89675`
(extracted facts from BATCH-011 `TASK-20260730-009`; not re-fetched here).

## 1. Control pass rule

The control **passes** only if a single source-compatible probability space and
global attempt timeline instantiate all of the following. Partial local
schedules, estimated/typical per-run formulas, and finite ideal-choice panel
horizons do not satisfy the rule.

### 1.1 Stopping time τ

A stopping time \(\tau\) must be defined so that, almost surely, the procedure
terminates after a finite number of top-level sieve / recovery invocations,
and the index set \(\{1,\ldots,\tau\}\) covers every costed transition of:

- recursive discards (failed keep / discard-and-rerun);
- failed regularization and repeated punctured-regularization attempts;
- fresh-sieve recovery runs after postprocessing failure;
- residual-tail entry (classical enumeration / terminal branch);
- any declared stopping-policy breach typed as \(F_{\mathrm{stop}}\) in
  BATCH-013 `recovery_spec.md`.

The terminal σ-algebra must be Verify-relative in the sense of
`recovery_spec.md`: success is only `Verify(x,k') = true`; report-only
completion, unverified candidates, and exhausted residual search are failure
exits under \(F\), not success. A local machine horizon that ends in
`retry_horizon_exhausted` without a Verify predicate is **not** an
instantiation of \(\tau\).

Candidate schema (type only; **not** source-instantiated):

\[
\tau=\inf\{k\geq 1:\text{after invocation }k\text{ the procedure enters
terminal success, terminal residual-tail closure, or named }F\text{-exit}\}.
\]

### 1.2 Joint finite-expectation obligations

On that same space, the following expectations must be proved finite
(not estimated from typical per-run models):

\[
\mathbb{E}\sum_{k\leq\tau} Q_k,\qquad
\mathbb{E}\sum_{k\leq\tau} S_k,\qquad
\mathbb{E}\sum_{k\leq\tau} P_k,\qquad
\mathbb{E}\Bigl[\sum_{k\leq\tau} C_k + H\Bigr],
\]

where \(Q_k\) are oracle/query charges, \(S_k\) sieve/T-gate or equivalent
non-oracle sieve charges, \(P_k\) postprocessing charges, \(C_k\) classical
recovery/attempt charges on invocation \(k\), and \(H\) is terminal residual /
verification classical work after the last quantum invocation. Identity of
paper quantities such as \(\widetilde Q_{\mathrm{total}}\) with
\(\mathbb{E}\sum_{k\leq\tau} Q_k\) must be explicit.

### 1.3 Scope of this control versus BATCH-011

BATCH-011 `stopping_liveness_control.md` required (1)–(4): stopping law,
joint additive expectations, global memory liveness schedule, and common
operational \(F\). **This control addresses only the stopping-law /
joint-expectation half (QM-STOPPING / O1).** It does **not** clear
`QM-MEMORY-MAP` or `QM-ERROR`. Those remain open pending real FC0 lifetime
and `Verify(x,k')` implementation (DEC-20260730-015 / EV-SSI-017 /
RT-20260730-041). A residual-gap checklist alone is not a stopping law.

## 2. What ttm-v2 panel supplies — and does not

Sources: BATCH-016 `tape_machine_spec_v2.md` and
`panel_audit_results.yaml` (TASK-20260730-031 / TASK-20260730-033).

### Supplies (retained, finite ideal-choice only)

- A **bounded one-retry horizon** at the designated `internal_S2` site:
  initial attempt plus at most one same-level retry; no `retry(2)`.
- **Ideal-choice** collecting semantics on a typed tape / recursive history
  machine for the preregistered panel rows.
- Exhaustive compositional enumeration observations under that machine,
  labeled `finite_ideal_choice_ttm_v2_observation_only`.

### Does **not** supply

- A model of concrete **HashDRBG** randomness or reachability under the
  pinned sieve’s RNG.
- A **global history-uniform** stopping law over top-level discards,
  recovery runs, and residual entry.
- A **Verify-relative** \(\tau\) or any `Verify(x,k')` predicate.
- Joint finiteness of \(\sum Q,\sum S,\sum P,\sum C+H\) for an end-to-end
  FC0-R2 attack.
- QUERY_MEMORY clearance, or equivalence with BATCH-014 pair/zero-progress
  definitions (`definitions_differ_not_equated`).

Inflating the one-retry panel into a global stopping law would be a
fabrication under the executor contract; this control refuses that inflation.

## 3. Source facts used for the pass/fail check

### 3.1 Peikert PDF (BATCH-011 extraction; page numbers one-indexed physical)

- p.12 Eq. (3.3): per-sieve query model
  \(Q=(r/(1-\delta))^d\log L_0\) under a random discard-fraction model —
  not a joint law of top-level retries/recovery.
- p.15 §3.4.1: failed regularization discards and re-runs the sieve;
  success probability is an empirical least-frequency ratio, not a uniform
  conditional success lower bound.
- pp.15–16 §§3.4.2 / 3.4.4: repeated punctured measurements; expected
  recovered information reported; number/dependence of fresh-sieve recovery
  runs undefined.
- p.18 Fig. 1: \(\widetilde Q_{\mathrm{total}}\) framed with expected
  information and typical per-run query assumptions — not identified with
  \(\mathbb{E}\sum_{k\leq\tau} Q_k\).
- p.20 Eq. (4.1): non-oracle sieve T-gate estimate on typical phase-vector
  length — does not jointly charge all top-level retries, postprocessing,
  recovery, and classical tail under one \(\tau\).

### 3.2 CollimationSieve@6f9188e4

Prior process extraction (BATCH-012 / BATCH-017 gate) establishes
report-only sieve completion: no end-to-end recovered-key `Verify`, no
implemented FC0 W/R/B/M_tail lifetimes, and no global attempt kernel that
would define \(\tau\). BATCH-017 lifetime/error gates document those gaps;
they do not instantiate a stopping law (RT-20260730-041 CONFIRM).

### 3.3 BATCH-013 recovery_spec (type obligations only)

Defines \(F\) via Verify-relative success, \(F_{\mathrm{stop}}\) for
stopping-policy breach, and stage schedule for recovery/tail. These are
**specification obligations**, not source instantiations. They sharpen what
\(\tau\) must cover; they do not prove finite joint expectations.

## 4. Instantiation attempt and blockers

| Obligation | Status | Note |
|---|---|---|
| Source-compatible \(\tau\) covering discards/retries/recovery/residual | **not_instantiated** | Schema exists; transition kernel, independence, uniform success bound absent |
| Verify-relative terminal σ-algebra | **not_instantiated** | `Verify(x,k')` absent in pinned code; recovery_spec only |
| \(\mathbb{E}\sum Q_k < \infty\) under \(\tau\) | **not_instantiated** | \(\widetilde Q_{\mathrm{total}}\) ≠ required random sum |
| \(\mathbb{E}\sum S_k < \infty\) under \(\tau\) | **not_instantiated** | Eq. (4.1) typical/essential estimate only |
| \(\mathbb{E}\sum P_k < \infty\) under \(\tau\) | **not_instantiated** | Postprocessing transitions uncosted jointly |
| \(\mathbb{E}[\sum C_k+H] < \infty\) under \(\tau\) | **not_instantiated** | Classical recovery/tail/Verify uninstantiated |
| ttm-v2 one-retry horizon as global \(\tau\) | **rejected_as_insufficient** | Local panel horizon ≠ end-to-end law |

C2 heavy-tail mutation from BATCH-011
(\(\Pr[\tau=n]=1/(n(n+1))\), \(\mathbb{E}[\tau]=\infty\)) remains
**NOT REJECTED** by the cited per-run facts: no iid retry law or uniform
conditional success lower bound appears in the pinned Peikert extraction or
the report-only sieve pin. Therefore joint additive expectations are not
established.

## 5. Control result

**FAIL.**

- Joint Q/S/P/C(+H) ledger incomplete.
- QM-STOPPING remains **open**.
- Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.
- QM-MEMORY-MAP and QM-ERROR remain **open** (not addressed for clearance
  by this control; BATCH-017 gate ≠ clearance).
- No numeric security, NIST-level, breakthrough, curve-compute, BATCH-014
  equivalence, or goal-completion claim.
- Zero compute; `maximum_runs: 1`.
