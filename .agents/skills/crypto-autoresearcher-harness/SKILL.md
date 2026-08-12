---
name: crypto-autoresearcher-harness
description: >-
  Run, resume, or inspect a Crypto Autoresearcher ECDLP research campaign from
  OpenCode. Use when the user asks to run the harness, continue a GOAL-*,
  check research status, or start a bounded research workflow.
compatibility: Requires a checkout of the Crypto Autoresearcher repository.
---

# Crypto Autoresearcher Harness (OpenCode adapter)

This repository-native adapter delegates to the canonical portable skill at
`plugins/crypto-autoresearcher-harness/skills/crypto-autoresearcher-harness/SKILL.md`.

Before taking any action, locate the Git worktree root and read that canonical
skill in full. Its protocol, including the read-only preflight and the
Coordinator/dispatch/archival gates, is authoritative. Do not copy or weaken
those rules here.

OpenCode discovers this adapter automatically through `.agents/skills/`. It is
intentionally a skill rather than an OpenCode V2 in-process plugin: this front
door only needs portable instructions, and the V2 plugin API is beta. The
repository's generated `.opencode/agent/` bindings remain the authority for
role permissions.
