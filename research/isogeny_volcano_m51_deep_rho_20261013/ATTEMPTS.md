# Four-level m=51 rho attempt ledger

This additive ledger preserves completed, non-triggered, and failed audit paths.
No outcome-driven scientific rerun or backfill was performed.

| attempt | scope | outcome | effect on evidence |
|---|---|---|---|
| Scientific execution | Exact frozen 20,480-solve schedule at `/tmp/m51-deep-rho-run-1a3bdfb1` | completed in 608.035806 s; run sealed | supplies the native endpoint measurement record |
| Primary analysis | Frozen analyzer on the original sealed path | completed; status `aa_alert_labels_withheld` | preserves numerical diagnostics but releases no inferential/equivalence label |
| Conditional setup-robustness lane | Prespecified 2,176-solve follow-up | not triggered because the A/A gate failed | no robustness observation exists; zero solves is the protocol-defined outcome |
| Deterministic archive | Normalize and compress the already sealed tree | completed; archive SHA-256 `d8d334f8...19059e` | preserves the exact scientific tree; adds no measurement |
| Relocated analyzer replay | Run the frozen analyzer on the archive extracted at a different absolute path | stopped at `RNG cross-language execution differs: 0` | packaging/replay limitation only; scientific record unchanged |
| Independent statistical recomputation | Recompute reported statistics from sealed records | exact agreement, zero discrepancies | corroborates the numerical analysis; does not override the failed gate |
| Live-tree cache audit | Inspect an unmanifested post-seal `__pycache__` entry | exact cache moved to recoverable quarantine; manifests pass again | documents and removes post-seal live-tree contamination; archive was unaffected |

The next scientifically admissible measurement is a fresh, separately frozen
replication with its own A/A gate and no reuse of outcome-selected seeds or
endpoints. It must be reported as a new run. Reanalyzing or increasing this
run's sample after seeing the gate result would not repair its predeclared
inference.
