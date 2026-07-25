---
name: pursue-crux
description: >-
  Decompose a blocked or open research goal into sub-problems, identify the CRUX
  (the sub-problem whose resolution decides the goal), and pursue it as a
  first-class target -- including when the crux turns out to be a known problem
  in another field. Use whenever a goal is blocked, a direction is exhausted, or
  a barrier/no-go result has been proved. Never treat "the crux is a known hard
  problem" as a stopping point.
---

# Pursue the crux

A goal is rarely blocked as a whole; it is blocked at a specific point. This
skill finds that point, makes it a research target in its own right, and keeps
the reduction chain auditable.

## Procedure

1. **State the goal quantitatively.** What measurable claim would satisfy it?
   (e.g. "total cost o(sqrt N)"). If it cannot be stated as a measurable claim,
   fix that first -- an unmeasurable goal cannot be decomposed.

2. **Localize.** Derive which single quantity the goal depends on, holding the
   rest fixed (a localization/reduction theorem). Prove the reduction if you
   can; otherwise state it as a hypothesis with its assumptions explicit.

3. **Enumerate sub-problems** that could move that quantity. For each, record:
   the exact claim, what a positive vs negative resolution would mean, and cost.
   File them as `IDEA-*` proposals so they are tracked, not lost.

4. **Identify the crux**: the sub-problem whose resolution decides the goal
   (positive => goal achieved; negative => goal provably unreachable by this
   route). Prefer cruxes that are *decidable* over ones that are merely open.

5. **Close the cheap ones first.** Prove or refute the tractable sub-problems --
   each one either advances the goal or narrows the crux. Record every negative
   result: a closed route is real progress and prevents rediscovery.

6. **When the crux is a known problem in another field** (fine-grained
   complexity, additive combinatorics, coding theory, ...):
   - **Pursue it anyway.** Import that field's best known upper AND lower bounds.
   - **Calibrate**: does the state of the art reach the region your goal needs?
     If it lands exactly on the boundary, say so -- that is informative, and it
     is a real check your reduction could have failed.
   - **Check instance structure**: your instance is usually NOT worst-case. Ask
     explicitly whether you control the instance, and whether that freedom helps
     or is self-defeating. Prove which.
   - **Cite precisely** and record novelty as `unverified` unless you have done
     a genuine survey (a couple of searches is not a survey).

7. **Record the chain.** Goal -> localization -> sub-problems -> crux -> status,
   with IDs, so any reader can audit which link is load-bearing and which links
   are proved vs conjectured.

## Rules

- A barrier/no-go result is a *waypoint*, not a terminus: it converts "unknown"
  into "blocked exactly here", which is the input to the next decomposition.
- Never relabel a reduction, equivalence, or negative result as achieving the
  goal. State plainly which link is still open.
- Never fabricate a resolution to the crux. If the crux is a famous open
  problem, that is a finding about the goal's difficulty -- report it as such,
  with the reduction that establishes it.
- Prefer decompositions where some sub-problem is decidable with the tools and
  environment actually available; record the rest as blocked, with what would
  unblock them.
