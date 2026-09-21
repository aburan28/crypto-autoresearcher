# Coordinator plan — 2026-07-17 experiment batch

Source of hypotheses: `research_directions_20260717.md` (Research Director submission, 12 candidates).
Role split per AGENTS.md: Coordinator (me) freezes protocols, dispatches handoffs, owns state
transitions; Executor sub-agents implement, run, and return evidence. Decisions (DEC records)
are recorded by me after evidence review — never by executors.

## Stage 1 — Dispatch (parallel, 12 Executors)

| Candidate | Experiment | Ledger family | Core measurement |
|---|---|---|---|
| A1 | EXP-JET-001 | JET | tangent-screen σ, C_lin, C_nonlin vs serial-S3 harvester |
| A2 | EXP-INC-001 | INC | output-sensitive incidence reporting vs exact enumeration |
| A3 | EXP-STR-001 | STR | AP-support hit rate, displacement rank α, structured solve |
| B1 | EXP-NET-001 | NET | Somos collision enrichment vs birthday, k-recovery vs BSGS |
| B2 | EXP-BKK-001 | BKK | Newton polytopes/MV vs Bézout, sparse vs dense solve |
| B3 | EXP-EQJ-001 | EQJ | isotypic block ranks/multiplicities of relation operator |
| C1 | EXP-TRA-001 | TRA | coarse-grained spectral localization factor L(S,C) |
| C2 | EXP-TTN-001 | TTN | TTN bond-rank growth vs dense-resultant exponent 1.979 |
| C3 | EXP-NCP-001 | NCP | NC-GB word relations vs commutative quotient |
| D1 | EXP-JETB-001 | JETB | jet-augmented generic model: simulation check vs measured σ |
| D2 | EXP-BKKMV-001 | BKKMV | exact MV growth-law certificate m=3..5(+7 attempt) |
| D3 | EXP-INCB-001 | INCB | EC chord richness profile vs random-line control |

Common rules frozen into every handoff:
- seeds 20260717..20260722 (or the subset named in the candidate section); deviations recorded as limitations
- positive + negative controls exactly as named in each candidate section
- budgets: wall_clock ≤ 2400 s/agent, single sage invocation > 600 s = infrastructure timeout (NOT evidence, AGENTS rule 5), reduce load and record deviation
- artifacts: specification.yaml, .sage implementation, runs/RUN-*/{manifest.yaml,raw.json,stderr.txt}, analysis.md, ledger RQ/H/EV YAML records
- executors do NOT git-commit (coordinator commits after review) and do NOT touch files outside their own EXP dir + their 3 ledger records
- every result states its tested parameters, evidence scope, and transfer or
  extrapolation assumptions; honest negative = success (rule 8)

## Stage 2 — Review & decide (Coordinator)

For each returned EV record: verify validity_status, controls, and gate arithmetic; then write
DEC-20260717-NNN with decision (supported/weakened/rejected_scoped/inconclusive/failed_infrastructure),
evidence refs, and scope statement. Write SYNTHESIS-20260717.md. Commit.
