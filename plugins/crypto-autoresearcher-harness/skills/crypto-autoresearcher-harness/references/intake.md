# Ideas and experiment design

Bind the user's actual question and scope. Read AGENTS.md, the Idea Generator
and Coordinator contracts, docs/inventor-protocol.md, the target-result profile,
and templates/research-records.md. Retrieve the knowledge base and primary
sources before novelty claims; mark citation provenance and unresolved novelty.

Use the existing stage procedures under .claude/skills/propose-ideas/SKILL.md
and .claude/skills/design-experiment/SKILL.md as repository documents on any
runtime. Host-specific invocation syntax is not required. Current AGENTS.md
takes precedence over legacy wording such as sequential ID allocation.

Proposals need mechanisms, assumptions, predictions, controls, falsification,
cost accounting, and a checked frontier comparison. Proof-oriented work needs
the proof_search_map audits. Allocate/check IDs with tools/allocate_id.py.
Designs need explicit parameters, deterministic seeds, controls, metrics,
budgets, stopping rules and exact artifacts before approval.

Route work through declared handoffs and Coordinator archival using the shared
lifecycle. Freeze designs with approved_by: null until a committed Coordinator
decision approves them. Ideas/design mode ends after the requested artifacts
are archived and published; clearly report what remains unapproved and unrun.
When the user requested execution too, return to the lifecycle's approval step
and continue rather than ending at the design checkpoint.
