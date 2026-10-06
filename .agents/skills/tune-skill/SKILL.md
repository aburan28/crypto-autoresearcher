---
name: tune-skill
description: "Propose a reward-guided textual revision to another skill's instructions (and its dispatched agent contract, if any), using that skill's own downstream ledger records as the reward signal. Standalone prototype: reads ledger/experiments state but writes no ledger record and holds no Coordinator authority \u2014 every diff is a normal code change a human approves before it is applied. Use when asked to tune, improve, or \"RL\" a skill's prompt against its track record, e.g. `/tune-skill propose-ideas`."
---

# tune-skill

Read `.claude/skills/tune-skill/SKILL.md` from this checkout and follow it. Resolve references and assets relative to that canonical directory. Preserve its authority and execution boundaries; this adapter adds no runtime role.
